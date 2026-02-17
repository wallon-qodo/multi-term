#!/usr/bin/env python3
"""Test sending Enter to bypass security prompt."""

import ptyprocess
import os
import time
import select

print("=" * 70)
print("TESTING WITH ENTER TO BYPASS SECURITY PROMPT")
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

# Read initial prompt
print("\n1. Reading security prompt...")
time.sleep(1)
ready, _, _ = select.select([fd], [], [], 0.1)
if ready:
    data = os.read(fd, 4096)
    print(f"   📥 Read {len(data)} bytes")

# SEND ENTER TO CONFIRM
print("\n2. Sending Enter to confirm trust...")
os.write(fd, b'\n')
print("   ✓ Sent Enter key")

# Wait for Claude to initialize after confirmation
print("\n3. Waiting 2 seconds for Claude to initialize...")
time.sleep(2)

# Read any output after Enter
print("\n4. Reading post-confirmation output...")
all_data = bytearray()
for i in range(20):
    ready, _, _ = select.select([fd], [], [], 0.1)
    if ready:
        data = os.read(fd, 4096)
        all_data.extend(data)
        print(f"   📥 Read {len(data)} bytes")

if all_data:
    output = all_data.decode('utf-8', errors='replace')
    print(f"\n   Post-confirmation output ({len(all_data)} bytes):")
    print("   " + "="*60)
    # Show plain text without ANSI
    import re
    plain = re.sub(r'\x1b\[[0-9;?]*[a-zA-Z]|\x1b\([0-9;?]*[a-zA-Z]', '', output)
    print(plain[:500])

# NOW try sending a command
print("\n5. Sending command: 'hello'...")
os.write(fd, b'hello\n')
print("   ✓ Command sent")

# Wait for response
print("\n6. Waiting for response...")
response_data = bytearray()
for i in range(100):  # 10 seconds
    ready, _, _ = select.select([fd], [], [], 0.1)
    if ready:
        data = os.read(fd, 4096)
        response_data.extend(data)
        print(f"   📥 Read {len(data)} bytes (total: {len(response_data)})")

if response_data:
    print(f"\n✓✓✓ GOT RESPONSE! ({len(response_data)} bytes)")
    response = response_data.decode('utf-8', errors='replace')
    print("\n   Response preview:")
    print("   " + "="*60)
    import re
    plain = re.sub(r'\x1b\[[0-9;?]*[a-zA-Z]|\x1b\([0-9;?]*[a-zA-Z]', '', response)
    print(plain[:500])
else:
    print("\n✗ Still no response")

print(f"\nProcess alive: {process.isalive()}")
process.terminate(force=True)
print("\n✓ Test complete")
