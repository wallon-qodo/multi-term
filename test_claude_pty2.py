#!/usr/bin/env python3
"""Test if Claude CLI works with PTY - explicit PATH."""

import asyncio
import os
from claude_multi_terminal.core.pty_handler import PTYHandler

async def test_claude_pty():
    """Test Claude CLI via PTY with explicit PATH."""
    print("Testing Claude CLI via PTY with explicit PATH...")
    print("=" * 60)

    output_received = []

    def callback(data):
        output_received.append(data)
        print(f"[OUTPUT] {repr(data[:200])}")

    # Get current environment and ensure PATH is there
    env = os.environ.copy()
    print(f"PATH in env: {env.get('PATH', 'NOT SET')[:100]}")

    # Test with Claude CLI
    handler = PTYHandler(
        command=["/opt/homebrew/bin/claude"],
        cwd="/tmp",
        env=env
    )

    print("Spawning Claude CLI...")
    handler.spawn()

    print("Starting output reading...")
    await handler.start_reading(callback)

    # Wait for initial output
    print("Waiting for initial output...")
    await asyncio.sleep(3)

    print(f"\n[INFO] Received {len(output_received)} chunks")

    # Send a test command
    if len(output_received) == 0 or "No such file" in output_received[0]:
        print("✗ Claude didn't start properly")
    else:
        print("✓ Claude started!")
        print("Sending test command...")
        await handler.write("what is 2+2?\n")
        await asyncio.sleep(5)
        print(f"Total chunks: {len(output_received)}")

    await handler.terminate()

if __name__ == "__main__":
    asyncio.run(test_claude_pty())
