#!/usr/bin/env python3
"""Diagnostic script to identify Terminal.app rendering issues."""

import sys
import time
import os

def test_1_basic_output():
    """Test 1: Basic print output"""
    print("\n" + "="*60)
    print("TEST 1: Basic Print Output")
    print("="*60)
    print("✓ If you can see this, basic output works")
    print("✓ Colors: \033[31mRED\033[0m \033[32mGREEN\033[0m \033[34mBLUE\033[0m")
    time.sleep(2)

def test_2_ansi_codes():
    """Test 2: ANSI escape codes"""
    print("\n" + "="*60)
    print("TEST 2: ANSI Escape Codes")
    print("="*60)
    # Clear screen
    print("\033[2J\033[H", end="")
    print("✓ Screen should have cleared")
    print("✓ Cursor at top-left")
    time.sleep(2)

def test_3_alternate_screen():
    """Test 3: Alternate screen buffer"""
    print("\n" + "="*60)
    print("TEST 3: Alternate Screen Buffer")
    print("="*60)
    print("About to switch to alternate screen in 2 seconds...")
    time.sleep(2)

    # Switch to alternate screen
    print("\033[?1049h", end="")
    sys.stdout.flush()
    print("\033[2J\033[H", end="")
    sys.stdout.flush()

    print("✓ YOU ARE NOW IN ALTERNATE SCREEN BUFFER")
    print("✓ If you see this, alternate screen works!")
    print("✓ This should NOT scroll your previous output")
    print("\nReturning to normal screen in 3 seconds...")
    time.sleep(3)

    # Return to normal screen
    print("\033[?1049l", end="")
    sys.stdout.flush()
    print("✓ Returned to normal screen")
    time.sleep(1)

def test_4_textual_init():
    """Test 4: Textual initialization"""
    print("\n" + "="*60)
    print("TEST 4: Textual Framework Initialization")
    print("="*60)

    try:
        from textual.app import App
        from textual.widgets import Static
        print("✓ Textual imports successful")

        class DiagnosticApp(App):
            """Minimal Textual app for testing"""

            DEFAULT_CSS = """
            Screen {
                background: rgb(26, 26, 26);
            }

            Static {
                width: 100%;
                height: 100%;
                content-align: center middle;
                color: rgb(255, 77, 77);
                background: rgb(26, 26, 26);
            }
            """

            def compose(self):
                yield Static("✓ TEXTUAL APP IS RUNNING!\n\nIf you see this, Textual works!\n\nPress Ctrl+C or 'q' to exit")

            def on_key(self, event):
                if event.key == "q":
                    self.exit()

        print("✓ App class created")
        print("\nStarting Textual app in 2 seconds...")
        print("(Press 'q' or Ctrl+C to exit)")
        time.sleep(2)

        app = DiagnosticApp()
        app.run()

        print("\n✓ Textual app exited successfully")

    except Exception as e:
        print(f"✗ ERROR: {e}")
        import traceback
        traceback.print_exc()

def test_5_full_app():
    """Test 5: Full ClaudeMultiTerminal app"""
    print("\n" + "="*60)
    print("TEST 5: Full Application")
    print("="*60)

    try:
        print("Importing ClaudeMultiTerminalApp...")
        from claude_multi_terminal.app import ClaudeMultiTerminalApp
        print("✓ Import successful")

        print("\nCreating app instance...")
        app = ClaudeMultiTerminalApp()
        print("✓ App created")

        print("\nStarting full app in 2 seconds...")
        print("(Press Ctrl+C to exit)")
        time.sleep(2)

        app.run()

        print("\n✓ Full app exited successfully")

    except Exception as e:
        print(f"✗ ERROR: {e}")
        import traceback
        traceback.print_exc()

def main():
    print("\n" + "="*60)
    print("TERMINAL DIAGNOSTIC SUITE")
    print("="*60)
    print(f"Terminal: {os.environ.get('TERM', 'unknown')}")
    print(f"TERM_PROGRAM: {os.environ.get('TERM_PROGRAM', 'unknown')}")
    print(f"Python: {sys.version}")

    try:
        test_1_basic_output()
        test_2_ansi_codes()
        test_3_alternate_screen()
        test_4_textual_init()
        test_5_full_app()

        print("\n" + "="*60)
        print("ALL TESTS COMPLETE")
        print("="*60)

    except KeyboardInterrupt:
        print("\n\n✓ Interrupted by user")
    except Exception as e:
        print(f"\n\n✗ UNEXPECTED ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
