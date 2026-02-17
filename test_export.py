#!/usr/bin/env python3
"""Test script for transcript export functionality."""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from claude_multi_terminal.core.export import TranscriptExporter, ConversationMessage, sanitize_filename
from datetime import datetime


def test_transcript_parser():
    """Test parsing of transcript text."""
    sample_transcript = """
      ▄▄▄▄▄
     █     █
     █ █ █ █
     █▄▄▄▄▄█
      █████
     ███████
      █ █ █

  Claude Code v2.1.23
             Sonnet 4.5 · API Usage Billing
    ▘▘ ▝▝    /Users/test/project


╔══════════════════════════════════════════════════════════════════════════════╗
║ ⏱ 14:23:45 ┊ ⚡ Command: write a hello world program                        ║
╚══════════════════════════════════════════════════════════════════════════════╝

📝 Response: Here's a simple hello world program:

```python
print("Hello, World!")
```

This program uses Python's built-in print function.

✻ Baked for 2s


╔══════════════════════════════════════════════════════════════════════════════╗
║ ⏱ 14:24:10 ┊ ⚡ Command: /help                                               ║
╚══════════════════════════════════════════════════════════════════════════════╝

📝 Response: Available commands:
- /model - Switch model
- /help - Show help
- /export - Export transcript

✻ Sautéed for 1s
"""

    exporter = TranscriptExporter()
    messages = exporter.parse_transcript(sample_transcript)

    print(f"✓ Parsed {len(messages)} messages")
    for i, msg in enumerate(messages):
        print(f"  [{i+1}] {msg.type} @ {msg.timestamp}: {msg.content[:50]}...")

    assert len(messages) > 0, "Should parse at least one message"
    print("✓ Parser test passed")


def test_markdown_export():
    """Test Markdown export."""
    messages = [
        ConversationMessage(
            timestamp="14:23:45",
            type="command",
            content="write a hello world program"
        ),
        ConversationMessage(
            timestamp="14:23:45",
            type="response",
            content="Here's a simple hello world program:\n\n```python\nprint('Hello, World!')\n```"
        ),
    ]

    exporter = TranscriptExporter(export_dir="/tmp/claude-test-exports")
    filepath = exporter.export_to_markdown(
        messages=messages,
        session_name="test_session",
        filename="test_export"
    )

    print(f"✓ Exported to: {filepath}")

    # Verify file exists and has content
    with open(filepath, 'r') as f:
        content = f.read()
        assert "# Claude Multi-Terminal Session" in content
        assert "write a hello world program" in content
        assert "```bash" in content or "```python" in content
        print(f"✓ Markdown file contains expected content ({len(content)} bytes)")

    print("✓ Markdown export test passed")


def test_json_export():
    """Test JSON export."""
    messages = [
        ConversationMessage(
            timestamp="14:23:45",
            type="command",
            content="write a hello world program"
        ),
        ConversationMessage(
            timestamp="14:23:45",
            type="response",
            content="Here's a simple hello world program"
        ),
    ]

    exporter = TranscriptExporter(export_dir="/tmp/claude-test-exports")
    filepath = exporter.export_to_json(
        messages=messages,
        session_name="test_session",
        session_id="test-uuid-1234",
        filename="test_export",
        metadata={"command_count": 1, "is_active": False}
    )

    print(f"✓ Exported to: {filepath}")

    # Verify file exists and is valid JSON
    import json
    with open(filepath, 'r') as f:
        data = json.load(f)
        assert "session" in data
        assert "messages" in data
        assert data["session"]["id"] == "test-uuid-1234"
        assert len(data["messages"]) == 2
        print(f"✓ JSON file is valid and contains {len(data['messages'])} messages")

    print("✓ JSON export test passed")


def test_filename_sanitization():
    """Test filename sanitization."""
    test_cases = [
        ("normal_name", "normal_name"),
        ("name with spaces", "name with spaces"),
        ("name/with/slashes", "name_with_slashes"),
        ("name:with:colons", "name_with_colons"),
        ("name<>with|invalid*chars", "name__with_invalid_chars"),
        ("..leading.dots", "leading.dots"),
        ("trailing.dots..", "trailing.dots"),
        ("a" * 250, "a" * 200),  # Long name truncation
    ]

    for input_name, expected_pattern in test_cases:
        result = sanitize_filename(input_name)
        print(f"  '{input_name[:30]}...' -> '{result[:30]}...'")
        assert len(result) <= 200, f"Filename too long: {len(result)}"
        assert not any(c in result for c in '<>:"/\\|?*'), f"Invalid chars in: {result}"

    print("✓ Filename sanitization test passed")


def main():
    """Run all tests."""
    print("=" * 80)
    print("Testing Claude Multi-Terminal Export Functionality")
    print("=" * 80)
    print()

    try:
        print("1. Testing transcript parser...")
        test_transcript_parser()
        print()

        print("2. Testing Markdown export...")
        test_markdown_export()
        print()

        print("3. Testing JSON export...")
        test_json_export()
        print()

        print("4. Testing filename sanitization...")
        test_filename_sanitization()
        print()

        print("=" * 80)
        print("✓ All tests passed!")
        print("=" * 80)

    except Exception as e:
        print(f"\n✗ Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
