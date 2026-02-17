#!/usr/bin/env python3
"""
Test to diagnose width calculation issue.
"""

import asyncio
from textual.app import App, ComposeResult
from textual.widgets import Label
from textual.containers import Container


class TestApp(App):
    """Test app to check width calculation."""

    CSS = """
    Screen {
        background: rgb(24,24,24);
    }

    #menu1 {
        layer: overlay;
        width: auto;
        height: auto;
        background: rgb(32,32,32);
        border: solid rgb(255,183,77);
        padding: 0;
        layout: vertical;
    }

    #menu1 .menu-item {
        width: 100%;
        height: 1;
        padding: 0 2;
        background: rgb(32,32,32);
        color: rgb(224,224,224);
    }

    #menu2 {
        layer: overlay;
        width: 40;
        height: auto;
        background: rgb(32,32,32);
        border: solid rgb(255,183,77);
        padding: 0;
        layout: vertical;
    }

    #menu2 .menu-item {
        width: 100%;
        height: 1;
        padding: 0 2;
        background: rgb(32,32,32);
        color: rgb(224,224,224);
    }

    #menu3 {
        layer: overlay;
        width: auto;
        height: auto;
        background: rgb(32,32,32);
        border: solid rgb(255,183,77);
        padding: 0;
        layout: vertical;
    }

    #menu3 .menu-item {
        width: auto;
        height: 1;
        padding: 0 2;
        background: rgb(32,32,32);
        color: rgb(224,224,224);
    }
    """

    def compose(self) -> ComposeResult:
        """Create three test menus with different width strategies."""
        # Menu 1: Container auto width, items 100% width
        menu1 = Container(id="menu1")
        menu1._add_children(
            Label("Copy                    Ctrl+C", classes="menu-item"),
            Label("Select All              Ctrl+A", classes="menu-item"),
        )
        menu1.styles.offset = (0, 0)
        yield menu1

        # Menu 2: Container fixed width, items 100% width
        menu2 = Container(id="menu2")
        menu2._add_children(
            Label("Copy                    Ctrl+C", classes="menu-item"),
            Label("Select All              Ctrl+A", classes="menu-item"),
        )
        menu2.styles.offset = (0, 3)
        yield menu2

        # Menu 3: Container auto width, items auto width
        menu3 = Container(id="menu3")
        menu3._add_children(
            Label("Copy                    Ctrl+C", classes="menu-item"),
            Label("Select All              Ctrl+A", classes="menu-item"),
        )
        menu3.styles.offset = (0, 6)
        yield menu3


async def test_width():
    """Run the test app."""
    app = TestApp()

    async with app.run_test() as pilot:
        await pilot.pause(0.5)

        print("\n" + "="*80)
        print("Testing Width Calculation Strategies")
        print("="*80)

        # Check each menu
        for menu_id in ["menu1", "menu2", "menu3"]:
            menu = app.query_one(f"#{menu_id}")
            labels = list(menu.query(Label))

            print(f"\n{menu_id.upper()}:")
            print(f"  Container size: {menu.size}")
            print(f"  Container region: {menu.region}")
            print(f"  Container width style: {menu.styles.width}")

            for i, label in enumerate(labels):
                print(f"  Label {i+1}:")
                print(f"    Content: '{label.content}'")
                print(f"    Size: {label.size}")
                print(f"    Width style: {label.styles.width}")

        # Export screenshot
        try:
            svg = app.export_screenshot()
            with open("/Users/wallonwalusayi/claude-multi-terminal/width_test.svg", "w") as f:
                f.write(svg)
            print("\nScreenshot saved to width_test.svg")

            # Check if text appears in SVG
            if "Copy" in svg and "Select All" in svg:
                print("✓ Menu text IS visible in SVG!")
            else:
                print("✗ Menu text NOT visible in SVG!")
        except Exception as e:
            print(f"Could not export: {e}")

        await pilot.pause(1)


if __name__ == "__main__":
    asyncio.run(test_width())
