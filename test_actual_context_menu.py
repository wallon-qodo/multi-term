#!/usr/bin/env python3
"""
Test the actual context menu in the real app.
"""

import asyncio
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from claude_multi_terminal.app import ClaudeMultiTerminalApp
from claude_multi_terminal.widgets.selectable_richlog import SelectableRichLog


async def test_real_context_menu():
    """Test the context menu in the real app."""
    app = ClaudeMultiTerminalApp()

    async with app.run_test() as pilot:
        # Wait for app to fully load
        await pilot.pause(0.5)

        print("\n" + "="*80)
        print("Testing Real Context Menu")
        print("="*80)

        # Find SelectableRichLog widgets
        richlog_widgets = list(app.query(SelectableRichLog))
        print(f"\nFound {len(richlog_widgets)} SelectableRichLog widgets")

        if not richlog_widgets:
            print("ERROR: No SelectableRichLog widgets found!")
            return

        richlog = richlog_widgets[0]

        # Add some content
        richlog.write("Test output line 1")
        richlog.write("Test output line 2")
        richlog.write("Test output line 3")

        await pilot.pause(0.2)

        print("\nAdded test content to RichLog")

        # Trigger the context menu by calling the internal method
        print("\nTriggering context menu at position (20, 10)...")
        richlog._show_context_menu(20, 10)

        await pilot.pause(0.3)

        # Check if context menu was created
        print(f"\nContext menu created: {richlog.context_menu is not None}")

        if richlog.context_menu:
            menu = richlog.context_menu

            print(f"Context menu mounted: {menu.is_mounted}")
            print(f"Menu items count: {len(menu.menu_items)}")
            print(f"Menu position: x={menu.menu_x}, y={menu.menu_y}")

            # Get labels from menu
            from textual.widgets import Label
            labels = list(menu.query(Label))

            print(f"\nMenu has {len(labels)} label children:")

            for i, label in enumerate(labels):
                classes = list(label.classes)
                content = getattr(label, 'content', 'NO CONTENT ATTR')
                display = label.styles.display
                visibility = label.styles.visibility

                print(f"\n  Label {i+1}:")
                print(f"    Content: '{content}'")
                print(f"    Classes: {classes}")
                print(f"    Display: {display}")
                print(f"    Visibility: {visibility}")

            # Try to export screenshot
            print("\n" + "-"*80)
            print("Exporting screenshot...")
            try:
                svg = app.export_screenshot()
                path = "/Users/wallonwalusayi/claude-multi-terminal/context_menu_screenshot.svg"
                with open(path, "w") as f:
                    f.write(svg)
                print(f"Screenshot saved to: {path}")

                # Search for menu text in SVG
                if "Copy" in svg and "Select All" in svg:
                    print("✓ Menu text found in SVG!")
                else:
                    print("✗ Menu text NOT found in SVG!")

            except Exception as e:
                print(f"Could not export screenshot: {e}")

        else:
            print("\nERROR: Context menu was not created!")

        await pilot.pause(1)


if __name__ == "__main__":
    asyncio.run(test_real_context_menu())
