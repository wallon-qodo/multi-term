#!/usr/bin/env python3
"""
Debug script to test context menu rendering in SelectableRichLog.
This will launch the app and programmatically test the context menu.
"""

import asyncio
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from claude_multi_terminal.app import ClaudeMultiTerminalApp
from claude_multi_terminal.widgets.selectable_richlog import MenuItem, ContextMenu
from textual.pilot import Pilot


async def test_context_menu():
    """Test context menu rendering."""
    app = ClaudeMultiTerminalApp()

    async with app.run_test() as pilot:
        # Wait for app to fully load
        await pilot.pause(0.5)

        print("\n" + "="*80)
        print("PHASE 1: Testing Context Menu Rendering")
        print("="*80)

        # Find a SelectableRichLog widget
        from claude_multi_terminal.widgets.selectable_richlog import SelectableRichLog
        richlog_widgets = list(app.query(SelectableRichLog))

        print(f"\nFound {len(richlog_widgets)} SelectableRichLog widgets")

        if not richlog_widgets:
            print("ERROR: No SelectableRichLog widgets found!")
            return

        richlog = richlog_widgets[0]

        # Add some test content so the menu has output
        richlog.write("Test line 1")
        richlog.write("Test line 2")
        richlog.write("Test line 3")

        await pilot.pause(0.2)

        print("\n" + "-"*80)
        print("PHASE 2: Creating Context Menu Manually")
        print("-"*80)

        # Create menu items manually (same as in _show_context_menu)
        menu_items = [
            MenuItem(
                label="Copy",
                callback=lambda: print("Copy clicked"),
                enabled=False,  # No selection
                shortcut="Ctrl+C"
            ),
            MenuItem(
                label="Select All",
                callback=lambda: print("Select All clicked"),
                enabled=True,
                shortcut="Ctrl+A"
            ),
            MenuItem(
                label="Clear Selection",
                callback=lambda: print("Clear Selection clicked"),
                enabled=False,  # No selection
                shortcut="Esc"
            ),
            MenuItem(
                label="---",  # Separator
                callback=lambda: None,
                enabled=False
            ),
            MenuItem(
                label="Copy All Output",
                callback=lambda: print("Copy All Output clicked"),
                enabled=True  # Has output
            ),
            MenuItem(
                label="Export Session...",
                callback=lambda: print("Export Session clicked"),
                enabled=True
            ),
        ]

        print(f"\nCreated {len(menu_items)} menu items:")
        for i, item in enumerate(menu_items):
            print(f"  {i+1}. {item.label:20} enabled={item.enabled:5} shortcut={item.shortcut}")

        # Create context menu
        context_menu = ContextMenu(items=menu_items, x=10, y=5)

        print("\n" + "-"*80)
        print("PHASE 3: Mounting Context Menu")
        print("-"*80)

        # Mount the menu
        await app.screen.mount(context_menu)
        await pilot.pause(0.3)

        print("\nContext menu mounted")
        print(f"  Menu position: x={context_menu.menu_x}, y={context_menu.menu_y}")
        print(f"  Menu items count: {len(context_menu.menu_items)}")

        # Check what children the menu has
        print("\n" + "-"*80)
        print("PHASE 4: Inspecting Menu Composition")
        print("-"*80)

        children = list(context_menu.children)
        print(f"\nContext menu has {len(children)} children:")

        for i, child in enumerate(children):
            from textual.widgets import Label
            if isinstance(child, Label):
                # Get the label's content
                label_text = str(child.renderable) if hasattr(child, 'renderable') else str(child)
                classes = list(child.classes)
                has_menu_item = hasattr(child, 'menu_item')
                menu_item_val = child.menu_item if has_menu_item else None

                print(f"  Child {i+1}:")
                print(f"    Type: Label")
                print(f"    Content: '{label_text}'")
                print(f"    Classes: {classes}")
                print(f"    Has menu_item attr: {has_menu_item}")
                print(f"    menu_item value: {menu_item_val}")
            else:
                print(f"  Child {i+1}:")
                print(f"    Type: {type(child).__name__}")

        # Inspect the compose method directly
        print("\n" + "-"*80)
        print("PHASE 5: Testing compose() Method Directly")
        print("-"*80)

        # Create a new menu to test compose
        test_menu = ContextMenu(items=menu_items, x=20, y=10)
        composed_widgets = list(test_menu.compose())

        print(f"\ncompose() returned {len(composed_widgets)} widgets:")
        for i, widget in enumerate(composed_widgets):
            from textual.widgets import Label
            if isinstance(widget, Label):
                label_text = str(widget.renderable) if hasattr(widget, 'renderable') else str(widget)
                classes = list(widget.classes)
                print(f"  Widget {i+1}:")
                print(f"    Type: Label")
                print(f"    Content: '{label_text}'")
                print(f"    Classes: {classes}")

        # Try to capture the visual state
        print("\n" + "-"*80)
        print("PHASE 6: Checking Menu Visibility")
        print("-"*80)

        print(f"\nContext menu properties:")
        print(f"  Is mounted: {context_menu.is_mounted}")
        print(f"  Display: {context_menu.styles.display}")
        print(f"  Visibility: {context_menu.styles.visibility}")
        print(f"  Width: {context_menu.styles.width}")
        print(f"  Height: {context_menu.styles.height}")
        print(f"  Layer: {context_menu.styles.layer}")

        # Try to get size
        size = context_menu.size
        print(f"  Actual size: {size.width}x{size.height}")

        # Check if menu is visible on screen
        print(f"\nMenu region: {context_menu.region}")
        print(f"Screen size: {app.screen.size}")

        # Wait for user to see the result
        await pilot.pause(2)

        print("\n" + "="*80)
        print("CONCLUSION")
        print("="*80)

        if len(children) == 0:
            print("\nPROBLEM FOUND: Menu has NO children!")
            print("The compose() method may not be yielding widgets correctly.")
        elif len(children) != len(menu_items):
            print(f"\nPROBLEM FOUND: Menu has {len(children)} children but should have {len(menu_items)}!")
        else:
            print(f"\nMenu structure looks correct ({len(children)} children for {len(menu_items)} items)")
            print("The issue may be with CSS styling or visibility.")

        print("\n" + "="*80)


if __name__ == "__main__":
    asyncio.run(test_context_menu())
