#!/usr/bin/env python3
"""Test app with output logging."""

import asyncio
from claude_multi_terminal.app import ClaudeMultiTerminalApp

LOG = open("/tmp/app_output.log", "w")

def log(msg):
    LOG.write(f"{msg}\n")
    LOG.flush()
    print(f"[LOG] {msg}")

async def test():
    log("Creating app...")
    app = ClaudeMultiTerminalApp()

    log("Starting app...")
    async with app.run_test() as pilot:
        log("App started, waiting 5 seconds for initialization...")
        await asyncio.sleep(5)

        # Get the sessions
        from claude_multi_terminal.widgets.session_pane import SessionPane
        panes = list(app.query(SessionPane))
        log(f"Found {len(panes)} panes")

        if panes:
            pane = panes[0]
            log(f"Checking first pane: {pane.session_id[:8]}")

            # Check RichLog
            from textual.widgets import RichLog
            rich_log = pane.query_one(f"#output-{pane.session_id}", RichLog)
            log(f"RichLog has {len(rich_log.lines)} lines initially")

            # Wait and check again
            log("Waiting 10 more seconds for Claude to send welcome message...")
            await asyncio.sleep(10)

            log(f"RichLog now has {len(rich_log.lines)} lines")

            if len(rich_log.lines) > 0:
                log("✓ OUTPUT IS APPEARING IN RICHLOG!")
                log("First 5 lines:")
                for i, line in enumerate(list(rich_log.lines)[:5]):
                    line_text = "".join(segment.text for segment in line)
                    log(f"  Line {i}: {repr(line_text[:60])}")
            else:
                log("✗ NO OUTPUT IN RICHLOG")
                log("This means the callback chain is broken")

        log("Test complete")

if __name__ == "__main__":
    print("Starting app test with logging...")
    print("Check /tmp/app_output.log for details")
    asyncio.run(test())
    print("\nTest complete. Check /tmp/app_output.log")
