#!/usr/bin/env python3
"""Test Claude with --dangerously-skip-permissions flag."""

import ptyprocess
import os
import time
import select
import re

def strip_ansi(text):
    return re.sub(r'\x1b\[[0-9;?]*[a-zA-Z]|\x1b\([0-9;?]*[a-zA-Z]', '', text)

print("=" * 70)
print("TESTING CLAUDE WITH --dangerously-skip-permissions FLAG")
print("=" * 70)

env = os.environ.copy()
env['TERM'] = 'xterm-256color'

# Spawn with the flag
process = ptyprocess.PtyProcess.spawn(
    ['/opt/homebrew/bin/claude', '--dangerously-skip-permissions'],
    cwd=os.path.expanduser("~"),
    env=env,
    dimensions=(24, 80)
)

print(f"\n✓ Spawned Claude with skip-permissions flag")
fd = process.fd

# Read initial output
print("\n1. Reading initial output (3 seconds)...")
time.sleep(3)
initial_data = bytearray()
for i in range(30):
    ready, _, _ = select.select([fd], [], [], 0.1)
    if not ready:
        break
    data = os.read(fd, 4096)
    initial_data.extend(data)
    print(f"   📥 Read {len(data)} bytes")

print(f"\n   Total: {len(initial_data)} bytes")

if initial_data:
    plain = strip_ansi(initial_data.decode('utf-8', errors='replace'))
    print("\n   Initial output:")
    print("   " + "-"*60)
    print(plain[:500])

    if "trust this folder" in plain.lower():
        print("\n   ✗ Still showing security prompt")
    else:
        print("\n   ✓ No security prompt! Continuing...")

# Send a command
print("\n2. Sending command: 'hello'...")
os.write(fd, b'hello\n')
print("   ✓ Command sent")

# Wait for response
print("\n3. Waiting for Claude response (8 seconds)...")
response_data = bytearray()
for i in range(80):
    ready, _, _ = select.select([fd], [], [], 0.1)
    if ready:
        data = os.read(fd, 4096)
        response_data.extend(data)
        if len(response_data) <= len(data):  # First chunk
            print(f"   📥 Read {len(data)} bytes")
        elif i % 10 == 0:  # Print progress every second
            print(f"   📥 Total so far: {len(response_data)} bytes")

if response_data:
    print(f"\n✓✓✓ GOT RESPONSE! ({len(response_data)} bytes)")
    plain = strip_ansi(response_data.decode('utf-8', errors='replace'))
    print("\n   Response:")
    print("   " + "="*60)
    print(plain[:800])
    print("\n   ✓✓✓ CLAUDE IS RESPONDING TO COMMANDS!")
else:
    print("\n✗ No response to command")

# Try another command
if response_data:
    print("\n4. Testing another command: 'pwd'...")
    os.write(fd, b'pwd\n')

    time.sleep(3)
    cmd2_data = bytearray()
    for i in range(30):
        ready, _, _ = select.select([fd], [], [], 0.1)
        if ready:
            data = os.read(fd, 4096)
            cmd2_data.extend(data)

    if cmd2_data:
        print(f"   ✓ Second command also worked! ({len(cmd2_data)} bytes)")

print(f"\nProcess alive: {process.isalive()}")
process.terminate(force=True)

print("\n" + "="*70)
if response_data:
    print("SUCCESS: Claude CLI is working with --dangerously-skip-permissions!")
    print("="*70)
else:
    print("FAILED: Still not responding")
    print("="*70)
