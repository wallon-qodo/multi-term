#!/usr/bin/env python3
"""Test when Claude is actually ready for input."""

import asyncio
import sys
import os

sys.path.insert(0, '/Users/wallonwalusayi/claude-multi-terminal')

from claude_multi_terminal.core.session_manager import SessionManager

async def main():
    print("=" * 70)
    print("TESTING WHEN CLAUDE IS READY FOR INPUT")
    print("=" * 70)

    manager = SessionManager()
    session_id = manager.create_session(name="Test")
    session = manager.sessions[session_id]

    output_chunks = []

    def callback(data: str):
        output_chunks.append(data)
        # Print each chunk as we get it to see what's happening
        print(f"\n📥 [{len(output_chunks)}] Got {len(data)} bytes")
        # Show readable parts
        readable = ''.join(c if c.isprintable() or c in '\n\r' else '.' for c in data)
        print(f"   {readable[:150]}")

    await session.pty_handler.start_reading(callback)
    print("\n✓ Started reading")

    # Wait longer for Claude to fully initialize
    print("\n⏳ Waiting 5 seconds for Claude to fully initialize...")
    await asyncio.sleep(5)

    print(f"\n📊 Received {len(output_chunks)} chunks so far")

    # Now try different commands with waits between each
    test_commands = [
        ("ls", 3),
        ("pwd", 3),
        ("echo 'test'", 3),
        ("help", 3),
    ]

    for cmd, wait_time in test_commands:
        chunks_before = len(output_chunks)

        print(f"\n{'='*60}")
        print(f"📤 Sending: {repr(cmd)}")
        await session.pty_handler.write(cmd + "\n")

        print(f"⏳ Waiting {wait_time} seconds for response...")
        await asyncio.sleep(wait_time)

        chunks_after = len(output_chunks)
        new_chunks = chunks_after - chunks_before

        if new_chunks > 0:
            print(f"✓ Got {new_chunks} new chunks - COMMAND WORKED!")
            # Show response
            response = "".join(output_chunks[chunks_before:])
            print(f"\n   Response ({len(response)} bytes):")
            print("   " + "-" * 50)
            print(repr(response[:400]))
            break  # Found a working command!
        else:
            print(f"✗ No response to '{cmd}'")

    # If we get here and no commands worked, check if Claude is even alive
    print(f"\n{'='*60}")
    print("FINAL STATUS:")
    print(f"Process alive: {session.pty_handler.process.isalive()}")
    print(f"Total chunks: {len(output_chunks)}")
    print(f"Total bytes: {sum(len(c) for c in output_chunks)}")

    await manager.terminate_session(session_id)
    print("\n✓ Test complete")

if __name__ == "__main__":
    asyncio.run(main())
