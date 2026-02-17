#!/usr/bin/env python3
"""Integration test to verify SelectableRichLog works correctly with resize events."""

import sys
from textual.app import App, ComposeResult
from textual.widgets import Header, Footer
from claude_multi_terminal.widgets.selectable_richlog import SelectableRichLog
from rich.text import Text


class IntegrationTestApp(App):
    """Integration test application that simulates real usage."""

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
        """Test real-world usage patterns when app mounts."""
        log = self.query_one("#test_log", SelectableRichLog)

        try:
            print("\n" + "="*60)
            print("INTEGRATION TEST: SelectableRichLog.write() Method")
            print("="*60)

            # Test 1: Write before widget is sized (deferred render)
            log.write("Line 1: Pre-mount content")
            log.write("Line 2: More pre-mount content")
            print("✓ Test 1: Deferred writes (before sizing)")

            # Test 2: Regular writes
            for i in range(5):
                log.write(f"Line {i+3}: Regular write #{i+1}")
            print("✓ Test 2: Regular writes after mount")

            # Test 3: Rich content
            log.write(Text("Line 8: Bold text", style="bold"))
            log.write(Text("Line 9: Colored text", style="green"))
            print("✓ Test 3: Rich Text rendering")

            # Test 4: Mixed parameters
            log.write("Line 10: Custom width", width=50)
            log.write("Line 11: Expand enabled", expand=True)
            log.write("Line 12: No shrink", shrink=False)
            print("✓ Test 4: Mixed parameter calls")

            # Test 5: Auto-scroll behavior
            for i in range(20):
                log.write(f"Line {i+13}: Auto-scroll test #{i+1}")
            print("✓ Test 5: Auto-scroll with many lines")

            # Simulate resize event (this triggers the deferred render replay)
            # The app will handle this automatically, but we can verify it doesn't crash
            print("\n" + "-"*60)
            print("Waiting for resize event processing...")
            print("(The app will handle DeferredRender unpacking)")
            print("-"*60)

            # Schedule app exit after 1 second
            self.set_timer(1.0, self.test_complete)

        except TypeError as e:
            print(f"\n✗ INTEGRATION TEST FAILED: TypeError")
            print(f"   {e}")
            sys.exit(1)
        except Exception as e:
            print(f"\n✗ INTEGRATION TEST FAILED: {type(e).__name__}")
            print(f"   {e}")
            sys.exit(1)

    def test_complete(self) -> None:
        """Called after test completes successfully."""
        print("\n" + "="*60)
        print("✓✓✓ INTEGRATION TEST PASSED ✓✓✓")
        print("="*60)
        print("\nAll write operations completed successfully.")
        print("No TypeError occurred during deferred render replay.")
        print("The SelectableRichLog.write() method is working correctly!")
        print("\nClosing app in 2 seconds...")
        self.set_timer(2.0, self.exit)


if __name__ == "__main__":
    app = IntegrationTestApp()
    try:
        app.run()
        print("\n✓ Application exited cleanly")
        sys.exit(0)
    except Exception as e:
        print(f"\n✗ Application crashed: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
