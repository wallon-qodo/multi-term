#!/usr/bin/env python3
"""Test typing a command and seeing the response."""

import asyncio
from claude_multi_terminal.app import ClaudeMultiTerminalApp
from textual.widgets import RichLog

LOG = open("/tmp/command_test.log", "w")

def log(msg):
    LOG.write(f"{msg}\n")
    LOG.flush()

async def test():
    log("Starting app...")
    app = ClaudeMultiTerminalApp()

    async with app.run_test() as pilot:
        log("Waiting 3 seconds for initialization...")
        await asyncio.sleep(3)

        # Get first pane
        from claude_multi_terminal.widgets.session_pane import SessionPane
        panes = list(app.query(SessionPane))
        pane = panes[0]

        rich_log = pane.query_one(f"#output-{pane.session_id}", RichLog)

        log(f"Initial line count: {len(rich_log.lines)}")
        log("Initial content (first 3 lines):")
        for i, line in enumerate(list(rich_log.lines)[:3]):
            line_text = "".join(segment.text for segment in line)
            log(f"  {i}: {repr(line_text[:80])}")

        # Type a command
        log("\nTyping command: 'hello'")
        input_widget = pane.query_one(f"#input-{pane.session_id}")
        input_widget.value = "hello"
        await pilot.press("enter")
        log("Command submitted")

        # Wait for response
        log("Waiting 8 seconds for response...")
        await asyncio.sleep(8)

        log(f"\nAfter command line count: {len(rich_log.lines)}")
        log("Last 5 lines:")
        for i, line in enumerate(list(rich_log.lines)[-5:]):
            line_text = "".join(segment.text for segment in line)
            log(f"  {i}: {repr(line_text[:80])}")

        log("\nTest complete")

if __name__ == "__main__":
    asyncio.run(test())
    print("Check /tmp/command_test.log for results")
