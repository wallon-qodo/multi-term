#!/usr/bin/env python3
"""Test the complete app with the fix."""

import asyncio
import sys
import os

sys.path.insert(0, '/Users/wallonwalusayi/claude-multi-terminal')

from claude_multi_terminal.core.session_manager import SessionManager

async def main():
    print("=" * 70)
    print("FINAL INTEGRATION TEST - Complete App with Fix")
    print("=" * 70)

    manager = SessionManager()

    # Create session (should use --dangerously-skip-permissions now)
    print("\n1. Creating session with SessionManager...")
    session_id = manager.create_session(name="Test Session")
    session = manager.sessions[session_id]

    print(f"   ✓ Session created: {session_id[:8]}...")
    print(f"   ✓ PTY alive: {session.pty_handler.process.isalive()}")
    print(f"   ✓ Command: {' '.join(session.pty_handler.command)}")

    # Verify flag is present
    if '--dangerously-skip-permissions' in session.pty_handler.command:
        print("   ✓ Using --dangerously-skip-permissions flag")
    else:
        print("   ✗ WARNING: Flag not found in command!")

    # Set up output tracking
    output_chunks = []

    def callback(data: str):
        output_chunks.append(data)
        if len(output_chunks) <= 5 or len(output_chunks) % 5 == 0:
            print(f"   📥 Output chunk #{len(output_chunks)}: {len(data)} bytes")

    # Start reading
    print("\n2. Starting async read loop...")
    await session.pty_handler.start_reading(callback)

    # Wait for initialization
    print("\n3. Waiting 3 seconds for initialization...")
    await asyncio.sleep(3)

    print(f"   Received {len(output_chunks)} chunks, {sum(len(c) for c in output_chunks)} bytes total")

    if len(output_chunks) > 0:
        print("   ✓ Initial output received")
        # Check if prompt is present
        combined = "".join(output_chunks)
        if "trust this folder" in combined.lower():
            print("   ✗ ERROR: Security prompt still present!")
        else:
            print("   ✓ No security prompt - ready for commands")
    else:
        print("   ✗ No initial output - something is wrong")
        await manager.terminate_session(session_id)
        return

    # Test command
    print("\n4. Sending test command: 'echo Testing 123'...")
    chunks_before = len(output_chunks)
    await session.pty_handler.write("echo Testing 123\n")

    print("   Waiting 5 seconds for response...")
    await asyncio.sleep(5)

    chunks_after = len(output_chunks)
    new_chunks = chunks_after - chunks_before

    if new_chunks > 0:
        print(f"   ✓✓✓ COMMAND WORKED! Got {new_chunks} new chunks")
        response = "".join(output_chunks[chunks_before:])
        print(f"   Response preview: {repr(response[:200])}")
    else:
        print("   ✗ No response to command")

    # Test another command
    if new_chunks > 0:
        print("\n5. Sending second command: 'pwd'...")
        chunks_before2 = len(output_chunks)
        await session.pty_handler.write("pwd\n")

        await asyncio.sleep(3)

        chunks_after2 = len(output_chunks)
        new_chunks2 = chunks_after2 - chunks_before2

        if new_chunks2 > 0:
            print(f"   ✓ Second command also worked! Got {new_chunks2} new chunks")
        else:
            print("   ✗ Second command failed")

    # Summary
    print("\n" + "=" * 70)
    print("FINAL SUMMARY:")
    print("=" * 70)
    print(f"✓ Session created with skip-permissions flag")
    print(f"✓ PTY process alive: {session.pty_handler.process.isalive()}")
    print(f"✓ Total output chunks: {len(output_chunks)}")
    print(f"✓ Total bytes: {sum(len(c) for c in output_chunks)}")

    if new_chunks > 0:
        print("✓✓✓ COMMANDS WORKING - Fix is successful!")
    else:
        print("✗ Commands not working - more debugging needed")

    await manager.terminate_session(session_id)
    print("\n✓ Test complete")

if __name__ == "__main__":
    asyncio.run(main())
