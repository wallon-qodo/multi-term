#!/usr/bin/env python3
"""
Test to see what content is actually in the Label widgets.
"""

import asyncio
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from claude_multi_terminal.app import ClaudeMultiTerminalApp
from claude_multi_terminal.widgets.selectable_richlog import MenuItem, ContextMenu


async def test_label_content():
    """Test what content is in labels."""
    app = ClaudeMultiTerminalApp()

    async with app.run_test() as pilot:
        # Wait for app to fully load
        await pilot.pause(0.3)

        print("\n" + "="*80)
        print("Testing Label Content")
        print("="*80)

        # Create menu items
        menu_items = [
            MenuItem(
                label="Copy",
                callback=lambda: None,
                enabled=False,
                shortcut="Ctrl+C"
            ),
            MenuItem(
                label="Select All",
                callback=lambda: None,
                enabled=True,
                shortcut="Ctrl+A"
            ),
        ]

        # Create context menu
        context_menu = ContextMenu(items=menu_items, x=10, y=5)

        # Mount it
        await app.screen.mount(context_menu)
        await pilot.pause(0.2)

        # Get the label children
        from textual.widgets import Label
        labels = list(context_menu.query(Label))

        print(f"\nFound {len(labels)} Label widgets:\n")

        for i, label in enumerate(labels):
            print(f"Label {i+1}:")
            print(f"  Type: {type(label)}")
            print(f"  Classes: {list(label.classes)}")

            # Try different ways to get the text
            print(f"  str(label): {str(label)}")
            print(f"  repr(label): {repr(label)}")

            # Check attributes
            if hasattr(label, 'renderable'):
                print(f"  label.renderable: {label.renderable}")
                print(f"  type(label.renderable): {type(label.renderable)}")

            if hasattr(label, '_text'):
                print(f"  label._text: {label._text}")

            if hasattr(label, 'update'):
                print(f"  Has update method: Yes")

            # Try to render it
            try:
                from io import StringIO
                from rich.console import Console
                console = Console(file=StringIO(), width=50, legacy_windows=False)
                console.print(label.renderable if hasattr(label, 'renderable') else label)
                output = console.file.getvalue()
                print(f"  Rendered output: '{output.strip()}'")
            except Exception as e:
                print(f"  Could not render: {e}")

            print()

        # Now test creating a label directly
        print("="*80)
        print("Testing direct Label creation:")
        print("="*80)

        from textual.widgets import Label

        test_label1 = Label("Hello World")
        test_label2 = Label("Test with shortcut      Ctrl+C")

        print(f"\nDirect Label 1: {test_label1}")
        print(f"  renderable: {test_label1.renderable if hasattr(test_label1, 'renderable') else 'N/A'}")

        print(f"\nDirect Label 2: {test_label2}")
        print(f"  renderable: {test_label2.renderable if hasattr(test_label2, 'renderable') else 'N/A'}")

        await pilot.pause(1)


if __name__ == "__main__":
    asyncio.run(test_label_content())
