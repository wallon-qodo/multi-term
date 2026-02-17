#!/usr/bin/env python3
"""Quick test to verify PTY communication works."""

import asyncio
import time
from claude_multi_terminal.core.pty_handler import PTYHandler

async def test_pty():
    """Test basic PTY read/write."""
    print("Testing PTY communication...")

    output_received = []

    def callback(data):
        output_received.append(data)
        print(f"Received: {repr(data)}")

    # Test with a simple echo command
    handler = PTYHandler(
        command=["python3", "-c", "import sys; sys.stdout.write('HELLO\\n'); sys.stdout.flush(); input()"],
        cwd="/tmp",
        env={"TERM": "xterm-256color"}
    )

    handler.spawn()
    await handler.start_reading(callback)

    # Wait for initial output
    await asyncio.sleep(0.5)

    print(f"\nReceived {len(output_received)} chunks")

    # Send a command
    await handler.write("test input\n")
    await asyncio.sleep(0.5)

    await handler.terminate()

    if output_received:
        print("✓ PTY communication working!")
    else:
        print("✗ No output received from PTY")

if __name__ == "__main__":
    asyncio.run(test_pty())
