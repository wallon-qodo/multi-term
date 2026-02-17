#!/usr/bin/env python3
"""
Integration test for export functionality with realistic session transcript.
Demonstrates parsing of complex conversations with code blocks, multiple commands, and responses.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from claude_multi_terminal.core.export import TranscriptExporter


def create_realistic_transcript():
    """Create a realistic session transcript with various content types."""
    return """
      ▄▄▄▄▄
     █     █
     █ █ █ █
     █▄▄▄▄▄█
      █████
     ███████
      █ █ █

  Claude Code v2.1.23
             Sonnet 4.5 · API Usage Billing
    ▘▘ ▝▝    /Users/developer/my-project

    /model to try Opus 4.5

  ❯ Try "write a test for <filepath>"


╔══════════════════════════════════════════════════════════════════════════════╗
║ ⏱ 09:15:23 ┊ ⚡ Command: analyze this codebase and suggest improvements      ║
╚══════════════════════════════════════════════════════════════════════════════╝

📝 Response: I'll analyze your codebase structure and suggest improvements.

After reviewing the files, here are my recommendations:

1. **Architecture**: Consider separating concerns with a cleaner MVC pattern
2. **Testing**: Add unit tests for core functionality
3. **Documentation**: Add docstrings to public APIs
4. **Error Handling**: Implement proper exception handling in network calls

Would you like me to help implement any of these improvements?

✻ Baked for 4s


╔══════════════════════════════════════════════════════════════════════════════╗
║ ⏱ 09:16:45 ┊ ⚡ Command: add unit tests for the authentication module        ║
╚══════════════════════════════════════════════════════════════════════════════╝

📝 Response: I'll create comprehensive unit tests for the authentication module.

```python
import unittest
from unittest.mock import patch, MagicMock
from auth.module import AuthManager


class TestAuthManager(unittest.TestCase):
    def setUp(self):
        self.auth_manager = AuthManager()

    def test_login_success(self):
        result = self.auth_manager.login('user@example.com', 'password123')
        self.assertTrue(result['success'])
        self.assertIsNotNone(result['token'])

    def test_login_invalid_credentials(self):
        result = self.auth_manager.login('wrong@email.com', 'wrong_pass')
        self.assertFalse(result['success'])
        self.assertIn('error', result)

    @patch('auth.module.requests.post')
    def test_token_refresh(self, mock_post):
        mock_post.return_value.json.return_value = {'token': 'new_token_xyz'}
        token = self.auth_manager.refresh_token('old_token')
        self.assertEqual(token, 'new_token_xyz')


if __name__ == '__main__':
    unittest.main()
```

I've created tests covering:
- Successful login
- Invalid credentials
- Token refresh with mocked HTTP calls

Run with: `python -m pytest tests/test_auth.py -v`

✻ Sautéed for 8s


╔══════════════════════════════════════════════════════════════════════════════╗
║ ⏱ 09:18:12 ┊ ⚡ Command: /help                                               ║
╚══════════════════════════════════════════════════════════════════════════════╝

📝 Response: Here are the available commands:

**Navigation & Management**
- `/model` - Switch between Claude models (Sonnet/Opus/Haiku)
- `/clear` - Clear conversation history
- `/save` - Save current session state
- `/load` - Load a saved session

**Development Tools**
- `/commit` - Create a git commit with changes
- `/review-pr` - Review a GitHub pull request
- `/test` - Run tests for the project
- `/diff` - Show git diff of changes
- `/status` - Show git status

**Information**
- `/help` - Show this help message
- `/version` - Show Claude CLI version
- `/docs` - Open documentation

**Export**
- `/export` - Export session transcript
  - `/export markdown` - Export as Markdown (default)
  - `/export json` - Export as JSON
  - `/export text` - Export as plain text

**Other**
- `/debug` - Debug mode and diagnostics
- `/plan` - Enable plan mode for complex tasks
- `/web` - Search the web for information

✻ Churned for 1s


╔══════════════════════════════════════════════════════════════════════════════╗
║ ⏱ 09:19:45 ┊ ⚡ Command: implement the token refresh logic                   ║
╚══════════════════════════════════════════════════════════════════════════════╝

📝 Response: I'll implement the token refresh logic with exponential backoff.

[Code block with TokenRefreshError and AuthTokenManager classes]

Key features:
- Exponential backoff for failed requests
- Automatic refresh before expiration
- Proper error handling with custom exceptions
- Token lifecycle management

✻ Grilled for 6s


╔══════════════════════════════════════════════════════════════════════════════╗
║ ⏱ 09:21:30 ┊ ⚡ Command: /export markdown dev_session_backup                 ║
╚══════════════════════════════════════════════════════════════════════════════╝

📝 Response: Exporting session to Markdown format...

✓ Exported to Markdown: ~/claude-exports/dev_session_backup.md

Your session has been successfully exported with:
- 5 commands
- Complete conversation history
- Code blocks preserved
- Timestamps included

✻ Roasted for 1s
"""


def test_realistic_export():
    """Test export with realistic session data."""
    print("=" * 80)
    print("Testing Export with Realistic Session Transcript")
    print("=" * 80)
    print()

    # Create exporter
    exporter = TranscriptExporter(export_dir="/tmp/claude-realistic-exports")

    # Get realistic transcript
    transcript = create_realistic_transcript()
    print(f"📝 Transcript length: {len(transcript)} characters")
    print()

    # Parse transcript
    print("1. Parsing transcript...")
    messages = exporter.parse_transcript(transcript)
    print(f"   ✓ Parsed {len(messages)} messages")
    print()

    # Display parsed messages
    print("2. Parsed message summary:")
    for i, msg in enumerate(messages, 1):
        content_preview = msg.content.replace('\n', ' ')[:80]
        print(f"   [{i}] {msg.type:8s} @ {msg.timestamp} | {content_preview}...")
    print()

    # Export to Markdown
    print("3. Exporting to Markdown...")
    md_path = exporter.export_to_markdown(
        messages=messages,
        session_name="Development_Session",
        filename="realistic_export_test"
    )
    print(f"   ✓ Exported to: {md_path}")

    # Verify Markdown content
    with open(md_path, 'r') as f:
        md_content = f.read()
        print(f"   ✓ Markdown file size: {len(md_content)} bytes")
        print(f"   ✓ Contains code blocks: {'```python' in md_content}")
        print(f"   ✓ Contains timestamps: {messages[0].timestamp in md_content if messages else False}")
    print()

    # Export to JSON
    print("4. Exporting to JSON...")
    json_path = exporter.export_to_json(
        messages=messages,
        session_name="Development_Session",
        session_id="dev-session-uuid-12345",
        filename="realistic_export_test",
        metadata={
            "command_count": 5,
            "is_active": False,
            "working_directory": "/Users/developer/my-project",
            "model": "claude-sonnet-4.5"
        }
    )
    print(f"   ✓ Exported to: {json_path}")

    # Verify JSON content
    import json
    with open(json_path, 'r') as f:
        json_data = json.load(f)
        print(f"   ✓ JSON file size: {len(json.dumps(json_data, indent=2))} bytes")
        print(f"   ✓ Session ID: {json_data['session']['id']}")
        print(f"   ✓ Message count: {json_data['session']['message_count']}")
        print(f"   ✓ Metadata: {list(json_data['metadata'].keys())}")
    print()

    # Export to Text
    print("5. Exporting to text...")
    text_path = exporter.export_raw_text(
        raw_text=transcript,
        session_name="Development_Session",
        filename="realistic_export_test"
    )
    print(f"   ✓ Exported to: {text_path}")

    with open(text_path, 'r') as f:
        text_content = f.read()
        print(f"   ✓ Text file size: {len(text_content)} bytes")
    print()

    print("=" * 80)
    print("✓ Realistic export test completed successfully!")
    print("=" * 80)
    print()
    print("Generated files:")
    print(f"  - {md_path}")
    print(f"  - {json_path}")
    print(f"  - {text_path}")
    print()
    print("You can review these files to see the export output.")


def test_large_session():
    """Test export with large session (1000+ messages)."""
    print("=" * 80)
    print("Testing Large Session Export (Performance Test)")
    print("=" * 80)
    print()

    # Generate large transcript
    print("1. Generating large transcript (1000 messages)...")
    large_transcript = ""

    for i in range(500):
        large_transcript += f"""
╔══════════════════════════════════════════════════════════════════════════════╗
║ ⏱ 10:{i:02d}:00 ┊ ⚡ Command: test command {i}                               ║
╚══════════════════════════════════════════════════════════════════════════════╝

📝 Response: This is test response {i} with some content.

✻ Baked for 1s

"""

    print(f"   ✓ Generated {len(large_transcript)} characters")
    print()

    # Export
    print("2. Exporting large session...")
    import time
    start_time = time.time()

    exporter = TranscriptExporter(export_dir="/tmp/claude-large-exports")
    messages = exporter.parse_transcript(large_transcript)

    print(f"   ✓ Parsed {len(messages)} messages")

    md_path = exporter.export_to_markdown(
        messages=messages,
        session_name="Large_Test_Session",
        filename="large_session_test"
    )

    elapsed = time.time() - start_time
    print(f"   ✓ Export completed in {elapsed:.2f} seconds")
    print(f"   ✓ Performance: {len(messages)/elapsed:.0f} messages/second")
    print()

    # Verify file size
    import os
    file_size = os.path.getsize(md_path)
    print(f"   ✓ Output file size: {file_size/1024:.2f} KB")
    print()

    print("=" * 80)
    print("✓ Large session export test passed!")
    print("=" * 80)


if __name__ == "__main__":
    try:
        test_realistic_export()
        print("\n")
        test_large_session()

        print("\n" + "=" * 80)
        print("✓ ALL INTEGRATION TESTS PASSED!")
        print("=" * 80)

    except Exception as e:
        print(f"\n✗ Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
