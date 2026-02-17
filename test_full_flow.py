#!/usr/bin/env python3
"""Test the full flow with UI."""

import asyncio
import sys
from textual.app import App, ComposeResult
from textual.widgets import RichLog, Input, Static
from textual.containers import Vertical
from claude_multi_terminal.core.session_manager import SessionManager

# Log to file since textual captures stdout
DEBUG_LOG = open("/tmp/debug_flow.log", "w")
def debug_log(msg):
    DEBUG_LOG.write(f"{msg}\n")
    DEBUG_LOG.flush()

class TestApp(App):
    """Minimal test app to debug output display."""

    def __init__(self):
        super().__init__()
        self.session_manager = SessionManager()
        self.output_count = 0

    def compose(self) -> ComposeResult:
        yield Static("Test App - Watch for output below:", id="header")
        yield RichLog(id="output", highlight=True, markup=True)
        yield Input(placeholder="Type something...", id="input")

    async def on_mount(self) -> None:
        """Start a Claude session."""
        debug_log("[DEBUG] Creating session...")
        session_id = self.session_manager.create_session(name="Test")

        session = self.session_manager.sessions[session_id]
        debug_log(f"[DEBUG] Session created: {session_id}")
        debug_log(f"[DEBUG] PTY alive: {session.pty_handler.process.isalive()}")

        # Start reading with callback
        await session.pty_handler.start_reading(self._handle_output)
        debug_log("[DEBUG] Started reading PTY output")

    def _handle_output(self, output: str) -> None:
        """Handle output from PTY."""
        self.output_count += 1
        debug_log(f"[DEBUG] Received output #{self.output_count}: {repr(output[:100])}")

        # Use call_from_thread to safely update UI
        self.call_from_thread(self._update_ui, output)

    def _update_ui(self, output: str) -> None:
        """Update UI on main thread."""
        debug_log(f"[DEBUG] _update_ui called with {len(output)} chars")
        try:
            log = self.query_one("#output", RichLog)
            debug_log(f"[DEBUG] Got RichLog widget: {log}")
            log.write(output)
            debug_log(f"[DEBUG] Wrote to RichLog successfully")
        except Exception as e:
            import traceback
            debug_log(f"[DEBUG ERROR] Failed to write to RichLog: {e}")
            debug_log(f"[DEBUG ERROR] Traceback: {traceback.format_exc()}")

    async def on_input_submitted(self, event: Input.Submitted) -> None:
        """Send input to Claude."""
        cmd = event.value
        debug_log(f"[DEBUG] Sending command: {repr(cmd)}")

        # Get the session
        for session in self.session_manager.sessions.values():
            await session.pty_handler.write(cmd + "\n")
            debug_log("[DEBUG] Command sent to PTY")

        event.input.value = ""

if __name__ == "__main__":
    debug_log("=" * 60)
    debug_log("Starting test app...")
    debug_log("Expected: You should see Claude's startup output in the UI")
    debug_log("Then type a command like 'hello' and press Enter")
    debug_log("=" * 60)
    app = TestApp()
    app.run()
