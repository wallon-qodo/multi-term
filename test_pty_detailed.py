#!/usr/bin/env python3
"""Detailed PTY test to diagnose connection issues."""

import ptyprocess
import time
import os
import sys
import select

print("=" * 70)
print("DETAILED PTY CONNECTION TEST")
print("=" * 70)

# Set up environment
env = os.environ.copy()
env['TERM'] = 'xterm-256color'
env['COLORTERM'] = 'truecolor'

claude_path = '/opt/homebrew/bin/claude'

# Check Claude exists
if not os.path.exists(claude_path):
    print(f"ERROR: Claude CLI not found at {claude_path}")
    sys.exit(1)

print(f"\n1. Claude CLI found at: {claude_path}")

# Spawn Claude with PTY
print("\n2. Spawning Claude CLI with PTY...")
try:
    process = ptyprocess.PtyProcess.spawn(
        [claude_path],
        cwd=os.path.expanduser("~"),
        env=env,
        dimensions=(24, 80)
    )
    print(f"   ✓ Process spawned (PID: {process.pid})")
    print(f"   ✓ Process alive: {process.isalive()}")
except Exception as e:
    print(f"   ✗ Failed to spawn: {e}")
    sys.exit(1)

# Test 1: Can we read initial output?
print("\n3. Testing READ capability (waiting 3 seconds for welcome message)...")
start = time.time()
total_bytes = 0
chunks = []

while time.time() - start < 3:
    try:
        # Use select to check if data is available
        ready, _, _ = select.select([process.fd], [], [], 0.1)
        if ready:
            data = process.read(1024)
            chunk = data.decode('utf-8', errors='replace')
            chunks.append(chunk)
            total_bytes += len(data)
            print(f"   📥 Read {len(data)} bytes")
    except Exception as e:
        print(f"   ⚠️  Read error: {e}")
        break

print(f"\n   Result: Read {total_bytes} total bytes in {len(chunks)} chunks")

if total_bytes > 0:
    print("   ✓ READ WORKS - Claude is sending data")
    print(f"\n   First 200 chars of output:")
    print("   " + "-" * 60)
    combined = "".join(chunks)
    print(repr(combined[:200]))
else:
    print("   ✗ READ FAILED - No data received from Claude")
    print("   This suggests:")
    print("   - Claude might not be starting properly")
    print("   - PTY might not be connected")
    print("   - Claude might be waiting for something")

# Test 2: Can we write to the PTY?
print("\n4. Testing WRITE capability...")
try:
    test_cmd = "echo TEST_MESSAGE\n"
    process.write(test_cmd.encode('utf-8'))
    print(f"   ✓ WRITE WORKS - Sent: {repr(test_cmd)}")
except Exception as e:
    print(f"   ✗ WRITE FAILED: {e}")

# Test 3: Does Claude respond to our write?
print("\n5. Testing RESPONSE to written command (waiting 5 seconds)...")
time.sleep(0.5)  # Give it a moment to process
start = time.time()
response_bytes = 0
response_chunks = []

while time.time() - start < 5:
    try:
        ready, _, _ = select.select([process.fd], [], [], 0.1)
        if ready:
            data = process.read(1024)
            chunk = data.decode('utf-8', errors='replace')
            response_chunks.append(chunk)
            response_bytes += len(data)
            print(f"   📥 Read {len(data)} bytes")
    except Exception as e:
        break

print(f"\n   Result: Read {response_bytes} total bytes in response")

if response_bytes > 0:
    print("   ✓ RESPONSE RECEIVED - Claude is responding to commands")
    print(f"\n   Response preview (first 300 chars):")
    print("   " + "-" * 60)
    combined_response = "".join(response_chunks)
    print(repr(combined_response[:300]))
else:
    print("   ✗ NO RESPONSE - Claude did not respond to our command")
    print("   This suggests:")
    print("   - Command was not properly sent")
    print("   - Claude is waiting for more input")
    print("   - There's a buffering/timing issue")

# Final status
print("\n" + "=" * 70)
print("SUMMARY:")
print("=" * 70)

if process.isalive():
    print("✓ Process is still alive")
else:
    print("✗ Process died")

print(f"✓ Initial read: {total_bytes} bytes" if total_bytes > 0 else "✗ Initial read: FAILED")
print(f"✓ Response read: {response_bytes} bytes" if response_bytes > 0 else "✗ Response read: FAILED")

# Cleanup
print("\n6. Cleaning up...")
if process.isalive():
    process.terminate(force=True)
    print("   ✓ Process terminated")

print("\n" + "=" * 70)
print("TEST COMPLETE")
print("=" * 70)
