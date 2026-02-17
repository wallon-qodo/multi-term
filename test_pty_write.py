#!/usr/bin/env python3
"""Test if writing to Claude PTY works."""

import ptyprocess
import time
import os

print("Testing PTY write to Claude CLI...")

# Set up environment
env = os.environ.copy()
env['TERM'] = 'xterm-256color'
env['COLORTERM'] = 'truecolor'

# Spawn Claude
print("\n1. Spawning Claude CLI...")
process = ptyprocess.PtyProcess.spawn(
    ['/opt/homebrew/bin/claude'],
    cwd=os.path.expanduser("~"),
    env=env,
    dimensions=(24, 80)
)

print("2. Waiting for welcome message (5 seconds)...")
initial_output = []
start = time.time()
while time.time() - start < 5:
    try:
        data = process.read(1024)
        output = data.decode('utf-8', errors='replace')
        initial_output.append(output)
    except:
        pass
    time.sleep(0.1)

print(f"3. Received {sum(len(o) for o in initial_output)} bytes of welcome message")

# Send a command
print("\n4. Sending command: 'hello'")
process.write(b'hello\n')
print("   Command sent!")

# Wait for response
print("\n5. Waiting for response (10 seconds)...")
response_output = []
start = time.time()
while time.time() - start < 10:
    try:
        data = process.read(1024)
        output = data.decode('utf-8', errors='replace')
        response_output.append(output)
        print(f"   Received {len(output)} bytes")
    except:
        pass
    time.sleep(0.1)

print(f"\n6. Total response: {sum(len(o) for o in response_output)} bytes")

if response_output:
    print("\n✓ Claude RESPONDED to the command!")
    print("\nFirst 300 chars of response:")
    print("-" * 60)
    combined = "".join(response_output)
    print(repr(combined[:300]))
else:
    print("\n✗ NO RESPONSE from Claude after sending 'hello'")
    print("\nThis suggests Claude CLI might be:")
    print("- Waiting for some initialization")
    print("- Not ready to accept input yet")
    print("- Expecting a different input format")

# Clean up
if process.isalive():
    process.terminate(force=True)

print("\nTest complete.")
