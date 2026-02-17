#!/usr/bin/env python3
"""Test if Claude CLI works with PTY."""

import asyncio
import time
from claude_multi_terminal.core.pty_handler import PTYHandler

async def test_claude_pty():
    """Test Claude CLI via PTY."""
    print("Testing Claude CLI via PTY...")
    print("=" * 60)

    output_received = []

    def callback(data):
        output_received.append(data)
        print(f"[OUTPUT] {repr(data)}")

    # Test with Claude CLI
    handler = PTYHandler(
        command=["/opt/homebrew/bin/claude"],
        cwd="/tmp",
        env={
            "TERM": "xterm-256color",
            "COLORTERM": "truecolor"
        }
    )

    print("Spawning Claude CLI...")
    handler.spawn()

    print("Starting output reading...")
    await handler.start_reading(callback)

    # Wait for initial output
    print("Waiting for initial output...")
    await asyncio.sleep(2)

    print(f"\n[INFO] Received {len(output_received)} chunks so far")
    print("=" * 60)

    # Send a test command
    print("Sending test command: 'hello'")
    await handler.write("hello\n")

    # Wait for response
    print("Waiting for response...")
    await asyncio.sleep(5)

    print(f"\n[INFO] Total received {len(output_received)} chunks")
    print("=" * 60)

    if output_received:
        print("✓ Output received from Claude!")
        print("\nFirst few chunks:")
        for i, chunk in enumerate(output_received[:5]):
            print(f"  [{i}] {repr(chunk[:100])}")
    else:
        print("✗ No output received from Claude")

    await handler.terminate()

if __name__ == "__main__":
    asyncio.run(test_claude_pty())
