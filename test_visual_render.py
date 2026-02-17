#!/usr/bin/env python3
"""
Test to see what's actually rendered visually.
"""

import asyncio
from textual.app import App, ComposeResult
from textual.widgets import Label, Static
from textual.containers import Container


class TestApp(App):
    """Test app to check label rendering."""

    CSS = """
    Screen {
        background: rgb(24,24,24);
    }

    Container {
        border: solid green;
        width: 40;
        height: auto;
        background: rgb(32,32,32);
    }

    .menu-item {
        width: 100%;
        height: 1;
        padding: 0 2;
        background: rgb(32,32,32);
        color: rgb(224,224,224);
        content-align: left middle;
    }

    .menu-item-disabled {
        width: 100%;
        height: 1;
        padding: 0 2;
        background: rgb(32,32,32);
        color: rgb(117,117,117);
        content-align: left middle;
    }

    .menu-separator {
        width: 100%;
        height: 1;
        background: rgb(32,32,32);
        color: rgb(66,66,66);
    }
    """

    def compose(self) -> ComposeResult:
        """Create a container with labels."""
        container = Container()
        container._add_children(
            Label("Copy                     Ctrl+C", classes="menu-item-disabled"),
            Label("Select All               Ctrl+A", classes="menu-item"),
            Label("Clear Selection           Esc", classes="menu-item-disabled"),
            Label("─" * 30, classes="menu-separator"),
            Label("Copy All Output", classes="menu-item"),
            Label("Export Session...", classes="menu-item"),
        )
        yield container


async def test_render():
    """Run the test app and capture output."""
    app = TestApp()

    async with app.run_test() as pilot:
        await pilot.pause(0.5)

        # Try to get a text representation
        print("\nAttempting to get screen text representation:")
        print("="*60)

        try:
            # Get the actual screen content
            from textual.pilot import Pilot
            if hasattr(pilot, '_app'):
                screen = pilot._app.screen
                print(f"Screen size: {screen.size}")

                # Try to render the screen
                from textual.renderables.screen import Screen as ScreenRenderable
                from rich.console import Console
                from io import StringIO

                # Create a console
                string_io = StringIO()
                console = Console(
                    file=string_io,
                    width=screen.size.width,
                    height=screen.size.height,
                    legacy_windows=False,
                    force_terminal=True
                )

                # Try to print screen content
                # (This may not work perfectly but let's see)
                print("\nScreen rendering attempt:")
                print("-"*60)

        except Exception as e:
            print(f"Error: {e}")
            import traceback
            traceback.print_exc()

        # Check label content directly
        labels = list(app.query(Label))
        print(f"\n\nFound {len(labels)} labels:")
        print("="*60)

        for i, label in enumerate(labels):
            print(f"\nLabel {i+1}:")

            # Check all possible attributes
            attrs_to_check = ['_content', 'renderable', '_text', '_rich_text', 'content']
            for attr in attrs_to_check:
                if hasattr(label, attr):
                    val = getattr(label, attr)
                    print(f"  {attr}: {val} (type: {type(val).__name__})")

            # Check CSS
            print(f"  display: {label.styles.display}")
            print(f"  visibility: {label.styles.visibility}")

        await pilot.pause(1)

        # Take a "screenshot"
        print("\n\nAttempting to export screen as SVG:")
        print("="*60)
        try:
            svg = pilot.app.export_screenshot()
            # Save it
            with open("/Users/wallonwalusayi/claude-multi-terminal/test_screenshot.svg", "w") as f:
                f.write(svg)
            print("Saved to test_screenshot.svg")
        except Exception as e:
            print(f"Could not export: {e}")

        await pilot.pause(1)


if __name__ == "__main__":
    asyncio.run(test_render())
