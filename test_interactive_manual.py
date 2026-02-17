#!/usr/bin/env python3
"""
Interactive test - run the actual app and test right-click manually.
This script will:
1. Launch the app
2. Add some test content to the terminal
3. Wait for user to right-click and test the menu
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from claude_multi_terminal.app import ClaudeMultiTerminalApp


def main():
    """Run the app interactively."""
    print("="*80)
    print("INTERACTIVE CONTEXT MENU TEST")
    print("="*80)
    print()
    print("This will launch the Claude Multi-Terminal application.")
    print()
    print("TO TEST THE CONTEXT MENU:")
    print("1. Wait for the app to load")
    print("2. The terminal will have some test output")
    print("3. RIGHT-CLICK on the terminal output area")
    print("4. You should see a context menu with 6 items:")
    print("   - Copy (Ctrl+C) - disabled/gray")
    print("   - Select All (Ctrl+A) - enabled/white")
    print("   - Clear Selection (Esc) - disabled/gray")
    print("   - ────────── (separator)")
    print("   - Copy All Output - enabled/white")
    print("   - Export Session... - enabled/white")
    print()
    print("5. Try clicking on 'Select All' - it should select all text")
    print("6. Right-click again - now 'Copy' and 'Clear Selection' should be enabled")
    print("7. Press Ctrl+Q to quit when done")
    print()
    print("="*80)
    print()

    app = ClaudeMultiTerminalApp()

    try:
        # Run the app
        app.run()
    except KeyboardInterrupt:
        print("\nInterrupted by user")
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
