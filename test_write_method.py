#!/usr/bin/env python3
"""Test script to validate SelectableRichLog.write() method signature."""

import sys
from textual.app import App, ComposeResult
from textual.widgets import Header, Footer
from claude_multi_terminal.widgets.selectable_richlog import SelectableRichLog
from rich.text import Text


class TestApp(App):
    """Test application for SelectableRichLog.write() method."""

    CSS = """
    Screen {
        background: rgb(24,24,24);
    }
    """

    def compose(self) -> ComposeResult:
        """Compose the test UI."""
        yield Header()
        yield SelectableRichLog(id="test_log")
        yield Footer()

    def on_mount(self) -> None:
        """Test various write() call patterns when app mounts."""
        log = self.query_one("#test_log", SelectableRichLog)

        try:
            # Test 1: Simple write with just content
            log.write("Test 1: Simple content")
            print("✓ Test 1 passed: Simple write with content only")

            # Test 2: Write with all parameters (mimics RichLog unpacking)
            log.write(
                "Test 2: Full parameters",
                width=None,
                expand=False,
                shrink=True,
                scroll_end=None
            )
            print("✓ Test 2 passed: Write with all keyword parameters")

            # Test 3: Write with Rich Text object
            rich_text = Text("Test 3: Rich Text", style="bold green")
            log.write(rich_text)
            print("✓ Test 3 passed: Write with Rich Text object")

            # Test 4: Write with custom width
            log.write("Test 4: Custom width", width=50)
            print("✓ Test 4 passed: Write with custom width")

            # Test 5: Write with expand=True
            log.write("Test 5: Expand enabled", expand=True)
            print("✓ Test 5 passed: Write with expand=True")

            # Test 6: Write with scroll_end override
            log.write("Test 6: Scroll end override", scroll_end=False)
            print("✓ Test 6 passed: Write with scroll_end=False")

            # Test 7: Multiple writes in sequence
            for i in range(5):
                log.write(f"Test 7.{i}: Multiple writes")
            print("✓ Test 7 passed: Multiple sequential writes")

            # Test 8: Write with all parameters explicitly set
            log.write(
                "Test 8: All explicit parameters",
                width=80,
                expand=True,
                shrink=False,
                scroll_end=True
            )
            print("✓ Test 8 passed: Write with all explicit parameters")

            print("\n" + "="*60)
            print("✓ All tests passed successfully!")
            print("="*60)
            print("\nThe write() method signature is correct and working.")
            print("You can close this app with Ctrl+C")

        except TypeError as e:
            print(f"\n✗ TypeError detected: {e}")
            print("\nThis indicates the write() method signature is incorrect.")
            sys.exit(1)
        except Exception as e:
            print(f"\n✗ Unexpected error: {type(e).__name__}: {e}")
            sys.exit(1)


if __name__ == "__main__":
    app = TestApp()
    app.run()
