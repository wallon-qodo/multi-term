#!/usr/bin/env python3
"""Test the real app initialization and command execution."""

import asyncio
import time
from claude_multi_terminal.app import ClaudeMultiTerminalApp

DEBUG_LOG = open("/tmp/test_real_app.log", "w")
def log(msg):
    DEBUG_LOG.write(f"{msg}\n")
    DEBUG_LOG.flush()

async def test_app():
    """Test the app by initializing it and sending a test command."""
    log("[DEBUG] Creating app...")
    app = ClaudeMultiTerminalApp()

    log("[DEBUG] Starting app in async context...")

    # We'll use app.run_test() which allows us to control the app programmatically
    async with app.run_test() as pilot:
        log("[DEBUG] App is running in test mode")

        # Wait for initialization
        await asyncio.sleep(2)
        log("[DEBUG] Waited 2 seconds for initialization")

        # Check if sessions were created
        session_count = len(app.session_manager.sessions)
        log(f"[DEBUG] Session count: {session_count}")

        # Try to find a session pane
        try:
            from claude_multi_terminal.widgets.session_pane import SessionPane
            panes = app.query(SessionPane)
            log(f"[DEBUG] Found {len(panes)} SessionPane widgets")

            if panes:
                pane = panes.first()
                log(f"[DEBUG] First pane: {pane.session_id}, mounted={pane.is_mounted}")

                # Try to send a command
                input_widget = pane.query_one(f"#input-{pane.session_id}")
                log(f"[DEBUG] Found input widget: {input_widget}")

                # Simulate typing and submitting a command
                log("[DEBUG] Setting input value...")
                input_widget.value = "echo 'test command'"

                log("[DEBUG] Submitting input...")
                # Trigger submission
                await pilot.press("enter")

                log("[DEBUG] Waiting for output...")
                await asyncio.sleep(3)

                log("[DEBUG] Test complete")
        except Exception as e:
            import traceback
            log(f"[DEBUG ERROR] Exception: {e}")
            log(f"{traceback.format_exc()}")

    log("[DEBUG] App test finished")

if __name__ == "__main__":
    log("[DEBUG] Starting test...")
    asyncio.run(test_app())
    log("[DEBUG] Test script complete")
