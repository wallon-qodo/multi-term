#!/usr/bin/env python3
"""
Final verification that the context menu is working.
"""

import asyncio
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from claude_multi_terminal.app import ClaudeMultiTerminalApp
from claude_multi_terminal.widgets.selectable_richlog import SelectableRichLog


async def test_final():
    """Final test."""
    app = ClaudeMultiTerminalApp()

    async with app.run_test() as pilot:
        await pilot.pause(0.5)

        print("\n" + "="*80)
        print("FINAL CONTEXT MENU VERIFICATION")
        print("="*80)

        # Find SelectableRichLog
        richlog_widgets = list(app.query(SelectableRichLog))
        richlog = richlog_widgets[0]

        # Add content
        richlog.write("Test output line 1")
        richlog.write("Test output line 2")

        await pilot.pause(0.2)

        # Show context menu
        richlog._show_context_menu(20, 10)
        await pilot.pause(0.3)

        if richlog.context_menu:
            menu = richlog.context_menu

            print(f"\n✓ Context menu created")
            print(f"  - Mounted: {menu.is_mounted}")
            print(f"  - Menu size: {menu.size}")
            print(f"  - Menu items: {len(menu.menu_items)}")

            # Check labels
            from textual.widgets import Label
            labels = list(menu.query(Label))

            print(f"\n✓ Menu has {len(labels)} label widgets:")
            for i, label in enumerate(labels):
                content = label.content[:30] if len(label.content) > 30 else label.content
                classes = ', '.join(label.classes)
                print(f"  {i+1}. '{content}' ({classes})")

            # Export and check
            svg = app.export_screenshot()

            # Check for menu items in SVG (accounting for HTML entities)
            menu_checks = [
                ("Copy", "Copy" in svg),
                ("Select", "Select" in svg),
                ("Clear", "Clear" in svg),
                ("Export", "Export" in svg),
                ("Ctrl+C", "Ctrl+C" in svg or "Ctrl&#43;C" in svg),
                ("Ctrl+A", "Ctrl+A" in svg or "Ctrl&#43;A" in svg),
            ]

            print(f"\n✓ SVG Content Verification:")
            all_found = True
            for item, found in menu_checks:
                status = "✓" if found else "✗"
                print(f"  {status} {item}: {'Found' if found else 'NOT FOUND'}")
                if not found:
                    all_found = False

            print("\n" + "="*80)
            if all_found:
                print("SUCCESS: Context menu is working correctly!")
                print("All menu items are visible and rendering properly.")
            else:
                print("PARTIAL SUCCESS: Menu is rendering but some items may be missing.")

            print("="*80)

        else:
            print("\n✗ FAILED: Context menu was not created!")

        await pilot.pause(1)


if __name__ == "__main__":
    asyncio.run(test_final())
