#!/usr/bin/env python3
"""Test the fixed app with RichLog and proper refresh."""

import asyncio
from textual.app import App, ComposeResult
from textual.widgets import RichLog, Input, Static
from textual.containers import Vertical
from claude_multi_terminal.core.session_manager import SessionManager

class TestFixedApp(App):
    """Test app to verify the fixes."""

    def compose(self) -> ComposeResult:
        yield Static("Fixed App - Testing RichLog with refresh", id="header")
        yield RichLog(
            id="output",
            highlight=True,
            markup=True,
            auto_scroll=True
        )
        yield Input(placeholder="Type command and press Enter...", id="input")

    async def on_mount(self) -> None:
        """Start a Claude session."""
        self.session_manager = SessionManager()
        self.output_count = 0

        # Create session
        session_id = self.session_manager.create_session(name="Test")
        self.session = self.session_manager.sessions[session_id]

        # Start reading with callback
        await self.session.pty_handler.start_reading(self._handle_output)

        log = self.query_one("#output", RichLog)
        log.write("✓ Session started. Type 'hello' and press Enter to test.")

    def _handle_output(self, output: str) -> None:
        """Handle output from PTY."""
        self.output_count += 1

        # Use call_later to safely update UI
        self.call_later(self._update_ui, output)

    def _update_ui(self, output: str) -> None:
        """Update UI on main thread."""
        try:
            log = self.query_one("#output", RichLog)
            log.write(output)
            log.scroll_end(animate=False)
            log.refresh()  # Force refresh to ensure display updates
        except Exception as e:
            pass

    async def on_input_submitted(self, event: Input.Submitted) -> None:
        """Send input to Claude."""
        cmd = event.value
        if cmd.strip():
            await self.session.pty_handler.write(cmd + "\n")
        event.input.value = ""

if __name__ == "__main__":
    app = TestFixedApp()
    app.run()
