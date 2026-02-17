#!/usr/bin/env python3
"""Test the mode display in the StatusBar."""

from textual.app import App, ComposeResult
from claude_multi_terminal.widgets.status_bar import StatusBar
from claude_multi_terminal.types import AppMode
import asyncio


class TestModeApp(App):
    """Test app to cycle through modes."""

    def compose(self) -> ComposeResult:
        """Create the layout."""
        yield StatusBar()

    async def on_mount(self) -> None:
        """Cycle through modes for testing."""
        status_bar = self.query_one(StatusBar)

        modes = [
            (AppMode.NORMAL, "Normal mode - window management"),
            (AppMode.INSERT, "Insert mode - typing"),
            (AppMode.COPY, "Copy mode - text selection"),
            (AppMode.COMMAND, "Command mode - prefix key"),
        ]

        for mode, description in modes:
            status_bar.current_mode = mode
            self.notify(description, timeout=3)
            await asyncio.sleep(3)

        # Test broadcast mode with different modes
        status_bar.broadcast_mode = True
        self.notify("Broadcast mode enabled", timeout=2)
        await asyncio.sleep(2)

        for mode, _ in modes:
            status_bar.current_mode = mode
            await asyncio.sleep(2)

        self.exit()


if __name__ == "__main__":
    app = TestModeApp()
    app.run()
