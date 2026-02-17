#!/usr/bin/env python3
"""Test if read() is blocking and preventing interaction."""

import ptyprocess
import os
import time
import select
import sys

print("=" * 70)
print("TESTING IF READ IS BLOCKING")
print("=" * 70)

env = os.environ.copy()
env['TERM'] = 'xterm-256color'

process = ptyprocess.PtyProcess.spawn(
    ['/opt/homebrew/bin/claude'],
    cwd=os.path.expanduser("~"),
    env=env,
    dimensions=(24, 80)
)

print(f"\n✓ Spawned Claude (PID: {process.pid})")

# Read initial output with SELECT to avoid blocking
print("\n1. Reading initial output (non-blocking with select)...")
fd = process.fd
total_read = 0
chunks = 0

for i in range(30):  # Try for 3 seconds
    ready, _, _ = select.select([fd], [], [], 0.1)
    if ready:
        try:
            data = os.read(fd, 1024)
            total_read += len(data)
            chunks += 1
            print(f"   📥 Read {len(data)} bytes (chunk {chunks})")
        except Exception as e:
            print(f"   ⚠️  Read error: {e}")
            break

print(f"\n✓ Read {total_read} bytes in {chunks} chunks")

# Now send a command
print("\n2. Sending command: 'hello'...")
os.write(fd, b'hello\n')
print("   ✓ Command sent")

# Try to read response (non-blocking)
print("\n3. Reading response (non-blocking with select)...")
response_read = 0
response_chunks = 0

for i in range(100):  # Try for 10 seconds
    ready, _, _ = select.select([fd], [], [], 0.1)
    if ready:
        try:
            data = os.read(fd, 1024)
            if data:
                response_read += len(data)
                response_chunks += 1
                print(f"   📥 Read {len(data)} bytes (response chunk {response_chunks})")
                # Show first bit
                if response_chunks == 1:
                    print(f"      First 100 chars: {repr(data[:100])}")
        except Exception as e:
            print(f"   ⚠️  Read error: {e}")
            break

print(f"\n📊 Response: {response_read} bytes in {response_chunks} chunks")

if response_chunks > 0:
    print("✓ GOT RESPONSE - Non-blocking reads work!")
else:
    print("✗ NO RESPONSE - Even with non-blocking reads")

# Check if still alive
print(f"\nProcess alive: {process.isalive()}")

# Cleanup
process.terminate(force=True)
print("\n✓ Test complete")
