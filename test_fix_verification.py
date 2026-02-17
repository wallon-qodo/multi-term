#!/usr/bin/env python3
"""
Verify the fix was applied.
"""

import asyncio
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

# Force reload of the module
if 'claude_multi_terminal.widgets.selectable_richlog' in sys.modules:
    del sys.modules['claude_multi_terminal.widgets.selectable_richlog']

from claude_multi_terminal.app import ClaudeMultiTerminalApp
from claude_multi_terminal.widgets.selectable_richlog import SelectableRichLog, ContextMenu


async def test_fix():
    """Test the fix."""
    app = ClaudeMultiTerminalApp()

    async with app.run_test() as pilot:
        # Wait for app to fully load
        await pilot.pause(0.5)

        print("\n" + "="*80)
        print("Verifying Context Menu Fix")
        print("="*80)

        # Check the CSS
        print("\nContextMenu CSS:")
        print(ContextMenu.DEFAULT_CSS)

        # Find SelectableRichLog
        richlog_widgets = list(app.query(SelectableRichLog))

        if not richlog_widgets:
            print("ERROR: No SelectableRichLog widgets found!")
            return

        richlog = richlog_widgets[0]

        # Add content
        richlog.write("Test line 1")
        richlog.write("Test line 2")

        await pilot.pause(0.2)

        # Show context menu
        print("\nCreating context menu...")
        richlog._show_context_menu(20, 10)

        await pilot.pause(0.3)

        if richlog.context_menu:
            menu = richlog.context_menu

            print(f"\nMenu properties:")
            print(f"  Size: {menu.size}")
            print(f"  Region: {menu.region}")
            print(f"  Width style: {menu.styles.width}")

            # Check labels
            from textual.widgets import Label
            labels = list(menu.query(Label))

            print(f"\nLabels ({len(labels)} total):")
            for i, label in enumerate(labels):
                print(f"  Label {i+1}:")
                print(f"    Content: '{label.content}'")
                print(f"    Size: {label.size}")
                print(f"    Width style: {label.styles.width}")

            # Export
            print("\n" + "-"*80)
            svg = app.export_screenshot()
            path = "/Users/wallonwalusayi/claude-multi-terminal/fix_verification.svg"
            with open(path, "w") as f:
                f.write(svg)
            print(f"Screenshot saved: {path}")

            if "Copy" in svg and "Select All" in svg:
                print("✓✓✓ SUCCESS! Menu text IS visible in SVG!")
            else:
                print("✗✗✗ FAILED! Menu text still NOT visible!")

        await pilot.pause(1)


if __name__ == "__main__":
    asyncio.run(test_fix())
