#!/usr/bin/env python3
"""Quick test to verify output is being written to RichLog."""

import asyncio
from claude_multi_terminal.app import ClaudeMultiTerminalApp

async def main():
    app = ClaudeMultiTerminalApp()

    async with app.run_test() as pilot:
        # Wait for initialization
        print("Waiting for app to initialize...")
        await asyncio.sleep(4)

        # Check session panes
        from claude_multi_terminal.widgets.session_pane import SessionPane
        from textual.widgets import RichLog

        panes = app.query(SessionPane).results()
        print(f"\nFound {len(panes)} session panes")

        for i, pane in enumerate(panes):
            print(f"\n=== Pane {i+1} (Session {pane.session_id[:8]}...) ===")
            print(f"  Mounted: {pane.is_mounted}")

            # Get RichLog
            try:
                rich_log = pane.query_one(f"#output-{pane.session_id}", RichLog)
                line_count = len(rich_log.lines)
                print(f"  RichLog lines: {line_count}")

                if line_count > 0:
                    print(f"  First line: {rich_log.lines[0].plain[:60]}")
                    if line_count > 1:
                        print(f"  Last line: {rich_log.lines[-1].plain[:60]}")
                else:
                    print("  ERROR: No lines in RichLog!")

            except Exception as e:
                print(f"  ERROR getting RichLog: {e}")

if __name__ == "__main__":
    asyncio.run(main())
