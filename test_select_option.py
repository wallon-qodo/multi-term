#!/usr/bin/env python3
"""Test selecting option 1 to bypass security prompt."""

import ptyprocess
import os
import time
import select
import re

def strip_ansi(text):
    return re.sub(r'\x1b\[[0-9;?]*[a-zA-Z]|\x1b\([0-9;?]*[a-zA-Z]', '', text)

print("=" * 70)
print("TESTING SELECTING OPTION 1")
print("=" * 70)

env = os.environ.copy()
env['TERM'] = 'xterm-256color'

process = ptyprocess.PtyProcess.spawn(
    ['/opt/homebrew/bin/claude'],
    cwd=os.path.expanduser("~"),
    env=env,
    dimensions=(24, 80)
)

print(f"\n✓ Spawned Claude")
fd = process.fd

# Read and wait for full prompt
print("\n1. Waiting for security prompt (2 seconds)...")
time.sleep(2)
initial_data = bytearray()
while True:
    ready, _, _ = select.select([fd], [], [], 0.1)
    if not ready:
        break
    data = os.read(fd, 4096)
    initial_data.extend(data)

print(f"   📥 Read {len(initial_data)} bytes")
print(f"\n   Prompt:")
print("   " + "-"*60)
print(strip_ansi(initial_data.decode('utf-8', errors='replace'))[:400])

# Try different ways to confirm
test_inputs = [
    ("Just Enter", b'\n'),
    ("Enter then Enter", b'\n\n'),
    ("1 then Enter", b'1\n'),
    ("Down arrow then Enter", b'\x1b[B\n'),
]

for label, input_bytes in test_inputs:
    print(f"\n{'='*70}")
    print(f"TESTING: {label}")
    print("="*70)

    # Respawn fresh Claude
    if process.isalive():
        process.terminate(force=True)
    time.sleep(0.5)

    process = ptyprocess.PtyProcess.spawn(
        ['/opt/homebrew/bin/claude'],
        cwd=os.path.expanduser("~"),
        env=env,
        dimensions=(24, 80)
    )
    fd = process.fd

    # Wait for prompt
    time.sleep(1.5)
    # Clear buffer
    while True:
        ready, _, _ = select.select([fd], [], [], 0.05)
        if not ready:
            break
        os.read(fd, 4096)

    # Send input
    print(f"   Sending: {repr(input_bytes)}")
    os.write(fd, input_bytes)

    # Wait and check if we got past the prompt
    time.sleep(2)
    response = bytearray()
    for i in range(30):
        ready, _, _ = select.select([fd], [], [], 0.1)
        if ready:
            data = os.read(fd, 4096)
            response.extend(data)

    if response:
        plain = strip_ansi(response.decode('utf-8', errors='replace'))
        print(f"\n   Response ({len(response)} bytes):")
        print("   " + "-"*60)
        print(plain[:300])

        # Check if prompt is gone
        if "trust this folder" not in plain.lower() and "yes" not in plain.lower() and len(response) > 100:
            print(f"\n   ✓✓✓ PROMPT BYPASSED! Now trying command...")

            # Try sending a command
            os.write(fd, b'hello\n')
            time.sleep(3)

            cmd_response = bytearray()
            for i in range(30):
                ready, _, _ = select.select([fd], [], [], 0.1)
                if ready:
                    data = os.read(fd, 4096)
                    cmd_response.extend(data)
                    print(f"      📥 Got response: {len(data)} bytes")

            if cmd_response:
                print(f"\n   ✓✓✓ COMMAND WORKED! Got {len(cmd_response)} bytes")
                print("   " + "="*60)
                print(strip_ansi(cmd_response.decode('utf-8', errors='replace'))[:400])
                break  # Success!
        else:
            print("   ✗ Still showing prompt")
    else:
        print("   ✗ No response")

# Cleanup
if process.isalive():
    process.terminate(force=True)

print("\n" + "="*70)
print("TEST COMPLETE")
print("="*70)
