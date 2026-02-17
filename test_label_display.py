#!/usr/bin/env python3
"""
Test to diagnose why Label content is not displaying.
"""

import asyncio
from textual.app import App, ComposeResult
from textual.widgets import Label
from textual.containers import Container


class TestApp(App):
    """Test app to check label rendering."""

    CSS = """
    Screen {
        background: rgb(24,24,24);
    }

    .test-label {
        width: 100%;
        height: 1;
        padding: 0 2;
        background: rgb(32,32,32);
        color: rgb(224,224,224);
    }

    .menu-item {
        width: 100%;
        height: 1;
        padding: 0 2;
        background: rgb(32,32,32);
        color: rgb(224,224,224);
        content-align: left middle;
    }
    """

    def compose(self) -> ComposeResult:
        """Create labels."""
        yield Label("Test Label 1", classes="test-label")
        yield Label("Test Label 2 with more text", classes="test-label")
        yield Label("Copy                     Ctrl+C", classes="menu-item")
        yield Label("Select All               Ctrl+A", classes="menu-item")


async def test_labels():
    """Run the test app."""
    app = TestApp()

    async with app.run_test() as pilot:
        await pilot.pause(1)

        # Check labels
        labels = list(app.query(Label))
        print(f"\nFound {len(labels)} labels")

        for i, label in enumerate(labels):
            print(f"\nLabel {i+1}:")
            print(f"  Classes: {list(label.classes)}")
            print(f"  str(label): {str(label)}")

            # Check internal state
            if hasattr(label, '_content'):
                print(f"  _content: {label._content}")

            # Try to get the actual displayed text
            try:
                region = label.region
                size = label.size
                print(f"  Region: {region}")
                print(f"  Size: {size}")
            except Exception as e:
                print(f"  Could not get region/size: {e}")

        await pilot.pause(2)


if __name__ == "__main__":
    asyncio.run(test_labels())
