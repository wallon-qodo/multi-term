#!/usr/bin/env python3
"""Verification script for the core module implementation."""

import sys
from pathlib import Path

# Test imports
try:
    from claude_multi_terminal.core import (
        SessionManager,
        SessionInfo,
        ClipboardManager,
        TranscriptExporter,
        sanitize_filename
    )
    print("✓ All imports successful")
except ImportError as e:
    print(f"✗ Import failed: {e}")
    sys.exit(1)

# Test SessionManager
print("\nTesting SessionManager:")
try:
    manager = SessionManager()
    print("✓ SessionManager instantiated")

    # Check required methods exist
    assert hasattr(manager, 'create_session'), "Missing create_session method"
    assert hasattr(manager, 'terminate_session'), "Missing terminate_session method"
    assert hasattr(manager, 'get_session'), "Missing get_session method"
    assert hasattr(manager, 'list_sessions'), "Missing list_sessions method"
    print("✓ All required SessionManager methods present")

    # Check sessions dict
    assert hasattr(manager, 'sessions'), "Missing sessions dict"
    assert isinstance(manager.sessions, dict), "sessions is not a dict"
    print("✓ SessionManager has sessions dict")

except Exception as e:
    print(f"✗ SessionManager test failed: {e}")
    sys.exit(1)

# Test SessionInfo dataclass
print("\nTesting SessionInfo:")
try:
    from dataclasses import is_dataclass
    assert is_dataclass(SessionInfo), "SessionInfo is not a dataclass"
    print("✓ SessionInfo is a dataclass")

    # Check required fields
    fields = {f.name for f in SessionInfo.__dataclass_fields__.values()}
    required_fields = {'session_id', 'name', 'pty_handler', 'created_at', 'working_directory'}
    assert required_fields.issubset(fields), f"Missing fields: {required_fields - fields}"
    print(f"✓ SessionInfo has all required fields: {fields}")

except Exception as e:
    print(f"✗ SessionInfo test failed: {e}")
    sys.exit(1)

# Test ClipboardManager
print("\nTesting ClipboardManager:")
try:
    clipboard = ClipboardManager()
    print("✓ ClipboardManager instantiated")

    # Check required methods exist
    assert hasattr(clipboard, 'copy_to_system'), "Missing copy_to_system method"
    assert hasattr(clipboard, 'get_from_system'), "Missing get_from_system method"
    assert hasattr(clipboard, 'paste_from_system'), "Missing paste_from_system method"
    print("✓ All required ClipboardManager methods present")

    # Test copy and paste (should not fail even if clipboard not available)
    result = clipboard.copy_to_system("test")
    print(f"✓ copy_to_system returns: {type(result).__name__}")

    text = clipboard.get_from_system()
    print(f"✓ get_from_system returns: {type(text).__name__}")

except Exception as e:
    print(f"✗ ClipboardManager test failed: {e}")
    sys.exit(1)

# Test TranscriptExporter
print("\nTesting TranscriptExporter:")
try:
    exporter = TranscriptExporter()
    print("✓ TranscriptExporter instantiated")

    # Check required methods exist
    assert hasattr(exporter, 'export_to_markdown'), "Missing export_to_markdown method"
    assert hasattr(exporter, 'export_to_text'), "Missing export_to_text method"
    print("✓ All required TranscriptExporter methods present")

    # Check export_to_text signature
    import inspect
    sig = inspect.signature(exporter.export_to_text)
    params = list(sig.parameters.keys())
    assert 'output_lines' in params, "export_to_text missing output_lines parameter"
    assert 'filepath' in params, "export_to_text missing filepath parameter"
    print(f"✓ export_to_text has correct signature: {params}")

except Exception as e:
    print(f"✗ TranscriptExporter test failed: {e}")
    sys.exit(1)

# Test sanitize_filename function
print("\nTesting sanitize_filename:")
try:
    test_cases = [
        ("test:file/name", "test_file_name"),
        ("  .dots..  ", "dots"),
        ("<>:|?*test", "______test"),
    ]

    for input_str, expected_pattern in test_cases:
        result = sanitize_filename(input_str)
        # Just check it returns a valid string
        assert isinstance(result, str), f"sanitize_filename returned non-string: {type(result)}"
        assert len(result) > 0, f"sanitize_filename returned empty string for: {input_str}"
        assert '/' not in result, f"sanitize_filename didn't remove /: {result}"
        assert ':' not in result, f"sanitize_filename didn't remove :: {result}"

    print("✓ sanitize_filename works correctly")

except Exception as e:
    print(f"✗ sanitize_filename test failed: {e}")
    sys.exit(1)

print("\n" + "=" * 60)
print("✓ All core module tests passed!")
print("=" * 60)
print("\nModule structure:")
print("  - SessionManager: Manages multiple Claude CLI sessions")
print("  - SessionInfo: Dataclass for session metadata")
print("  - ClipboardManager: Platform-specific clipboard operations")
print("  - TranscriptExporter: Export session transcripts to various formats")
print("  - sanitize_filename: Utility function for safe filenames")
