#!/usr/bin/env python3
"""Test if Claude CLI works directly."""

import ptyprocess
import time
import os

print("Testing Claude CLI connection...")
print("=" * 60)

# Set up environment
env = os.environ.copy()
env['TERM'] = 'xterm-256color'
env['COLORTERM'] = 'truecolor'

print("\n1. Spawning Claude CLI process...")
try:
    process = ptyprocess.PtyProcess.spawn(
        ['/opt/homebrew/bin/claude'],
        cwd=os.path.expanduser("~"),
        env=env,
        dimensions=(24, 80)
    )
    print("   ✓ Process spawned successfully")
except Exception as e:
    print(f"   ✗ Failed to spawn: {e}")
    exit(1)

print("\n2. Waiting for initial output (10 seconds)...")
print("   (Claude CLI takes time to initialize)")

all_output = []
start_time = time.time()

# Read for 10 seconds
while time.time() - start_time < 10:
    try:
        if process.isalive():
            data = process.read(1024)
            output = data.decode('utf-8', errors='replace')
            all_output.append(output)
            print(f"   Received {len(output)} bytes")
    except:
        pass
    time.sleep(0.1)

print(f"\n3. Total output received: {sum(len(o) for o in all_output)} bytes")

if all_output:
    print("\n4. First 500 characters of output:")
    print("-" * 60)
    combined = "".join(all_output)
    print(repr(combined[:500]))
    print("-" * 60)

    print("\n✓ Claude CLI is working and sending output!")
    print("\nThis means the PTY connection works.")
    print("If you're not seeing output in the app, the issue is with")
    print("how the app is displaying it, not with Claude itself.")
else:
    print("\n✗ No output received from Claude CLI")
    print("\nThis suggests:")
    print("- Claude CLI might not be starting correctly")
    print("- Or it's taking longer than 10 seconds to initialize")
    print("- Or there's an environment issue")

# Clean up
if process.isalive():
    process.terminate(force=True)

print("\nTest complete.")
