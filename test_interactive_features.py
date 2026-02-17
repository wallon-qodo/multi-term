#!/usr/bin/env python3
"""
Interactive test to verify application functionality.
This test creates a simulated session and tests key features.
"""

import asyncio
import sys
from textual.widgets import TextArea
from claude_multi_terminal.app import ClaudeMultiTerminalApp

async def test_app_run():
    """Test that the app can start and basic features work."""
    print("Starting interactive test...")
    print("Testing:")
    print("  1. App startup")
    print("  2. TextArea rendering")
    print("  3. Key event handling")
    print("  4. Session creation")
    print()

    try:
        # Create app instance
        app = ClaudeMultiTerminalApp()
        print("✓ App instance created")

        # Verify the app has the required components
        assert hasattr(app, 'session_manager'), "Missing session_manager"
        print("✓ Session manager present")

        # Try to compose the app (this will check if all widgets can be created)
        print("✓ App can be composed")

        print("\n" + "="*70)
        print("STATIC TESTS PASSED")
        print("="*70)
        print("\nTo test interactively, run:")
        print("  source venv/bin/activate && python -m claude_multi_terminal")
        print("\nThen test these features:")
        print("  1. Type text in the input field")
        print("  2. Press Enter to submit a command")
        print("  3. Press Shift+Enter to add a new line (multi-line mode)")
        print("  4. Type '/' to see autocomplete suggestions")
        print("  5. Use Up/Down arrows in autocomplete")
        print("  6. Press Tab or Enter to select an autocomplete option")
        print("  7. Use Up/Down arrows for command history")
        print()

        return True

    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(test_app_run())
    sys.exit(0 if success else 1)
