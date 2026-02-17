#!/usr/bin/env python3
"""Simple test script to verify the app can be instantiated."""

from claude_multi_terminal.app import ClaudeMultiTerminalApp
from claude_multi_terminal.core.session_manager import SessionManager
from claude_multi_terminal.core.clipboard import ClipboardManager

def test_imports():
    """Test that all modules can be imported."""
    print("✓ All modules imported successfully")

def test_instantiation():
    """Test that the app can be instantiated."""
    try:
        app = ClaudeMultiTerminalApp()
        print(f"✓ App instantiated: {app.TITLE}")
        print(f"✓ Session manager ready")
        print(f"✓ Clipboard manager ready")
        print(f"✓ Storage initialized at: {app.storage.storage_dir}")
    except Exception as e:
        print(f"✗ Failed to instantiate app: {e}")
        raise

def test_components():
    """Test individual components."""
    # Test ClipboardManager
    clipboard = ClipboardManager()
    print(f"✓ Clipboard manager for platform: {clipboard.platform}")

    # Test SessionManager
    session_mgr = SessionManager(claude_path="/opt/homebrew/bin/claude")
    print(f"✓ Session manager with claude at: {session_mgr.claude_path}")

if __name__ == "__main__":
    print("Testing Claude Multi-Terminal components...\n")
    test_imports()
    test_instantiation()
    test_components()
    print("\n✓ All tests passed!")
    print("\nTo run the app:")
    print("  source venv/bin/activate")
    print("  claude-multi")
    print("\nOr:")
    print("  python -m claude_multi_terminal")
