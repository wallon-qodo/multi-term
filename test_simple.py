#!/usr/bin/env python3
"""Simple test to verify output display."""

import asyncio
from claude_multi_terminal.app import ClaudeMultiTerminalApp

async def test():
    app = ClaudeMultiTerminalApp()

    async with app.run_test() as pilot:
        # Wait for sessions to initialize
        await asyncio.sleep(3)

        # Get the first session pane
        from claude_multi_terminal.widgets.session_pane import SessionPane
        panes = app.query(SessionPane)

        if panes:
            pane = panes.first()
            print(f"Found pane: {pane.session_id}")

            # Get the RichLog to check its contents
            from textual.widgets import RichLog
            rich_log = pane.query_one(f"#output-{pane.session_id}", RichLog)
            print(f"RichLog has {len(rich_log.lines)} lines")

            # Print first few lines
            for i, line in enumerate(list(rich_log.lines)[:5]):
                print(f"Line {i}: {line.plain[:80]}")

            # Try sending a command
            input_widget = pane.query_one(f"#input-{pane.session_id}")
            input_widget.value = "echo test"
            await pilot.press("enter")

            # Wait for response
            await asyncio.sleep(2)

            # Check output again
            print(f"\nAfter command, RichLog has {len(rich_log.lines)} lines")
            for i, line in enumerate(list(rich_log.lines)[-5:]):
                print(f"Line {i}: {line.plain[:80]}")

if __name__ == "__main__":
    asyncio.run(test())
