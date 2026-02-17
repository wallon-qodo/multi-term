#!/usr/bin/env python3
"""Test script for context menu functionality in SelectableRichLog."""

from textual.app import App, ComposeResult
from textual.containers import Vertical
from textual.widgets import Header, Footer
from claude_multi_terminal.widgets.selectable_richlog import SelectableRichLog


class TestApp(App):
    """Test application for context menu."""

    CSS = """
    Screen {
        background: rgb(24,24,24);
    }

    SelectableRichLog {
        width: 100%;
        height: 100%;
    }
    """

    BINDINGS = [
        ("q", "quit", "Quit"),
    ]

    def __init__(self):
        super().__init__()
        self.clip_manager = MockClipboardManager()

    def compose(self) -> ComposeResult:
        """Create the UI layout."""
        yield Header()
        yield SelectableRichLog()
        yield Footer()

    def on_mount(self) -> None:
        """Populate the log with sample text."""
        log = self.query_one(SelectableRichLog)
        log.write("Welcome to the Context Menu Test!")
        log.write("")
        log.write("Try the following:")
        log.write("1. Right-click anywhere to open the context menu")
        log.write("2. Use 'Copy' to copy selected text (if any)")
        log.write("3. Use 'Select All' to select all text (Ctrl+A)")
        log.write("4. Use 'Clear Selection' to clear selection (Esc)")
        log.write("")
        log.write("You can also:")
        log.write("- Left-click and drag to select text")
        log.write("- Double-click to select a word")
        log.write("- Triple-click to select a line")
        log.write("- Press Ctrl+C to copy selected text")
        log.write("- Press Esc to dismiss the menu or clear selection")
        log.write("")
        log.write("Sample text for testing:")
        log.write("The quick brown fox jumps over the lazy dog.")
        log.write("Lorem ipsum dolor sit amet, consectetur adipiscing elit.")
        log.write("Textual is a great TUI framework for Python!")


class MockClipboardManager:
    """Mock clipboard manager for testing."""

    def __init__(self):
        self.buffer = ""

    def copy_to_system(self, text: str) -> bool:
        """Simulate copying to clipboard."""
        self.buffer = text
        return True


if __name__ == "__main__":
    app = TestApp()
    app.run()
