#!/usr/bin/env python3
"""Test the complete input -> output flow in the app."""

import asyncio
import sys
import os

sys.path.insert(0, '/Users/wallonwalusayi/claude-multi-terminal')

from claude_multi_terminal.core.session_manager import SessionManager
from rich.text import Text
import re

# Simulate the filter function
def filter_ansi(text: str) -> str:
    text = re.sub(r'\x1b\[\?2026[hl]', '', text)
    text = re.sub(r'\x1b\[\?1004[hl]', '', text)
    text = re.sub(r'\x1b\[\?25[hl]', '', text)
    text = re.sub(r'\x1b\[\?2004[hl]', '', text)
    return text

async def main():
    print("=" * 70)
    print("TESTING COMPLETE INPUT -> OUTPUT FLOW")
    print("=" * 70)

    manager = SessionManager()
    session_id = manager.create_session(name="Flow Test")
    session = manager.sessions[session_id]

    output_chunks = []
    filtered_chunks = []

    def callback(data: str):
        output_chunks.append(data)
        filtered = filter_ansi(data)
        filtered_chunks.append(filtered)

        print(f"\n📥 Callback #{len(output_chunks)}:")
        print(f"   Raw: {len(data)} bytes")
        print(f"   Filtered: {len(filtered)} bytes")
        print(f"   Empty after filter: {not filtered.strip()}")
        if filtered.strip():
            print(f"   Preview: {repr(filtered[:80])}")

    await session.pty_handler.start_reading(callback)
    print("\n✓ Started reading PTY")

    print("\n1. Waiting 3 seconds for initialization...")
    await asyncio.sleep(3)

    print(f"\n   📊 Initial output: {len(output_chunks)} chunks")

    # Now send a command
    print("\n2. Sending command: 'hello'")
    print("   Writing to PTY...")

    await session.pty_handler.write("hello\n")
    print("   ✓ Write complete")

    # Track what happens
    chunks_before = len(output_chunks)
    print(f"\n3. Waiting 5 seconds for response...")
    print(f"   (Currently have {chunks_before} chunks)")

    await asyncio.sleep(5)

    chunks_after = len(output_chunks)
    new_chunks = chunks_after - chunks_before

    print(f"\n4. Results:")
    print(f"   New chunks received: {new_chunks}")

    if new_chunks > 0:
        print("   ✓ Got response chunks!")

        # Analyze what we got
        for i in range(chunks_before, chunks_after):
            chunk_num = i - chunks_before + 1
            raw = output_chunks[i]
            filtered = filtered_chunks[i]

            print(f"\n   Response chunk {chunk_num}:")
            print(f"     Raw size: {len(raw)} bytes")
            print(f"     Filtered size: {len(filtered)} bytes")
            print(f"     Is empty: {not filtered.strip()}")

            if filtered.strip():
                print(f"     Content: {repr(filtered[:100])}")

                # Try Text.from_ansi conversion
                try:
                    rich_text = Text.from_ansi(filtered)
                    print(f"     Plain text: {repr(rich_text.plain[:100])}")
                except Exception as e:
                    print(f"     Conversion error: {e}")
    else:
        print("   ✗ NO response chunks!")
        print("\n   Possible issues:")
        print("   1. Command not sent to Claude")
        print("   2. Claude not responding")
        print("   3. PTY read loop stopped")

        # Check PTY status
        print(f"\n   PTY Status:")
        print(f"   - Process alive: {session.pty_handler.process.isalive()}")
        print(f"   - Read loop running: {session.pty_handler._running}")

    # Try another command
    if new_chunks == 0:
        print("\n5. Trying simpler command: 'pwd'")
        chunks_before2 = len(output_chunks)
        await session.pty_handler.write("pwd\n")

        await asyncio.sleep(3)

        new_chunks2 = len(output_chunks) - chunks_before2
        print(f"   New chunks: {new_chunks2}")

    await manager.terminate_session(session_id)

    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print(f"Total chunks: {len(output_chunks)}")
    print(f"Response to 'hello': {'✓ YES' if new_chunks > 0 else '✗ NO'}")

    if new_chunks > 0:
        # Check if any filtered chunks were empty
        empty_count = sum(1 for fc in filtered_chunks[chunks_before:chunks_after] if not fc.strip())
        print(f"Empty chunks after filter: {empty_count}/{new_chunks}")

        if empty_count == new_chunks:
            print("\n⚠️  PROBLEM: All response chunks became empty after filtering!")
            print("   This means the filter is too aggressive.")

if __name__ == "__main__":
    asyncio.run(main())
