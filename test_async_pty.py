#!/usr/bin/env python3
"""Test PTY with async read loop like the real app."""

import asyncio
import sys
import os

# Add project to path
sys.path.insert(0, '/Users/wallonwalusayi/claude-multi-terminal')

from claude_multi_terminal.core.session_manager import SessionManager

# Log file for debugging
LOG_FILE = open("/tmp/async_pty_test.log", "w")

def log(msg):
    LOG_FILE.write(f"{msg}\n")
    LOG_FILE.flush()
    print(msg)

async def main():
    log("=" * 70)
    log("ASYNC PTY TEST (Like Real App)")
    log("=" * 70)

    # Create session manager
    log("\n1. Creating SessionManager...")
    manager = SessionManager()

    # Create a session
    log("\n2. Creating session...")
    session_id = manager.create_session(name="Test Session")
    session = manager.sessions[session_id]

    log(f"   ✓ Session created: {session_id}")
    log(f"   ✓ PTY process alive: {session.pty_handler.process.isalive()}")

    # Track output
    output_count = 0
    output_chunks = []

    def output_callback(data: str):
        nonlocal output_count
        output_count += 1
        output_chunks.append(data)
        log(f"\n📥 Callback #{output_count}: Received {len(data)} bytes")
        log(f"   First 100 chars: {repr(data[:100])}")

    # Start reading
    log("\n3. Starting async read loop...")
    await session.pty_handler.start_reading(output_callback)
    log("   ✓ Read loop started")

    # Wait for initial output
    log("\n4. Waiting 3 seconds for welcome message...")
    await asyncio.sleep(3)

    log(f"\n   Result: Received {output_count} callbacks, {sum(len(c) for c in output_chunks)} total bytes")

    if output_count > 0:
        log("   ✓ INITIAL OUTPUT RECEIVED")
    else:
        log("   ✗ NO INITIAL OUTPUT - Read loop not working!")
        await session.pty_handler.terminate()
        return

    # Send a command
    log("\n5. Sending command: 'hello'")
    await session.pty_handler.write("hello\n")
    log("   ✓ Command sent")

    # Reset counter to track response
    response_start = output_count

    # Wait for response
    log("\n6. Waiting 8 seconds for Claude response...")
    await asyncio.sleep(8)

    response_count = output_count - response_start
    log(f"\n   Result: Received {response_count} new callbacks after sending command")

    if response_count > 0:
        log("   ✓ RESPONSE RECEIVED - Command worked!")
        log("\n   Response preview:")
        log("   " + "-" * 60)
        response_text = "".join(output_chunks[response_start:])
        log(repr(response_text[:300]))
    else:
        log("   ✗ NO RESPONSE - Command did not trigger output")

    # Terminate
    log("\n7. Terminating session...")
    await manager.terminate_session(session_id)
    log("   ✓ Session terminated")

    # Summary
    log("\n" + "=" * 70)
    log("SUMMARY:")
    log("=" * 70)
    log(f"Total callbacks: {output_count}")
    log(f"Total bytes: {sum(len(c) for c in output_chunks)}")
    log(f"Initial output: {'✓ YES' if response_start > 0 else '✗ NO'}")
    log(f"Command response: {'✓ YES' if response_count > 0 else '✗ NO'}")
    log("=" * 70)

    LOG_FILE.close()

if __name__ == "__main__":
    asyncio.run(main())
