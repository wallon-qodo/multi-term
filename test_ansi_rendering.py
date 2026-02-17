#!/usr/bin/env python3
"""Test ANSI rendering with Text.from_ansi()."""

import sys
import os
import asyncio

sys.path.insert(0, '/Users/wallonwalusayi/claude-multi-terminal')

from claude_multi_terminal.core.session_manager import SessionManager
from rich.text import Text
import re

def filter_ansi(text: str) -> str:
    """Filter problematic ANSI sequences."""
    text = re.sub(r'\x1b\[\?2026[hl]', '', text)
    text = re.sub(r'\x1b\[\?1004[hl]', '', text)
    text = re.sub(r'\x1b\[\?25[hl]', '', text)
    text = re.sub(r'\x1b\[\?2004[hl]', '', text)
    return text

async def main():
    print("=" * 70)
    print("TESTING ANSI RENDERING WITH Text.from_ansi()")
    print("=" * 70)

    manager = SessionManager()
    session_id = manager.create_session(name="Test")
    session = manager.sessions[session_id]

    output_chunks = []

    def callback(data: str):
        output_chunks.append(data)
        if len(output_chunks) <= 3:
            print(f"\n📥 Chunk #{len(output_chunks)}: {len(data)} bytes")

    await session.pty_handler.start_reading(callback)
    print("\n✓ Started reading")

    print("\n⏳ Waiting 3 seconds for initial output...")
    await asyncio.sleep(3)

    print(f"\n📊 Received {len(output_chunks)} chunks")

    if len(output_chunks) > 0:
        # Test filtering
        print("\n" + "=" * 70)
        print("TESTING ANSI FILTERING")
        print("=" * 70)

        raw = "".join(output_chunks[:2])  # First 2 chunks
        print(f"\nRaw output length: {len(raw)} bytes")
        print(f"Contains \\x1b[?2026h: {'Yes' if '\\x1b[?2026' in repr(raw) else 'No'}")

        filtered = filter_ansi(raw)
        print(f"\nFiltered output length: {len(filtered)} bytes")
        print(f"Removed: {len(raw) - len(filtered)} bytes")

        # Test Text.from_ansi()
        print("\n" + "=" * 70)
        print("TESTING Text.from_ansi() CONVERSION")
        print("=" * 70)

        try:
            rich_text = Text.from_ansi(filtered)
            print(f"✓ Converted to Rich Text")
            print(f"  Plain text length: {len(rich_text.plain)}")
            print(f"  Number of segments: {len(rich_text._spans)}")

            # Show what it looks like
            print(f"\n  Preview (first 200 chars):")
            print("  " + "-" * 60)
            print(f"  {rich_text.plain[:200]}")

        except Exception as e:
            print(f"✗ Conversion failed: {e}")

    # Test command
    print("\n" + "=" * 70)
    print("TESTING COMMAND RESPONSE")
    print("=" * 70)

    chunks_before = len(output_chunks)
    print("\n📤 Sending: 'echo Test 123'")
    await session.pty_handler.write("echo Test 123\n")

    await asyncio.sleep(3)

    new_chunks = len(output_chunks) - chunks_before
    if new_chunks > 0:
        print(f"✓ Got {new_chunks} response chunks")

        response = "".join(output_chunks[chunks_before:])
        filtered_response = filter_ansi(response)
        rich_response = Text.from_ansi(filtered_response)

        print(f"\n  Response preview:")
        print("  " + "-" * 60)
        print(f"  {rich_response.plain[:300]}")
    else:
        print("✗ No response")

    await manager.terminate_session(session_id)
    print("\n✓ Test complete")

if __name__ == "__main__":
    asyncio.run(main())
