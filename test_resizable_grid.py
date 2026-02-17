#!/usr/bin/env python3
"""
Test script for ResizableSessionGrid with drag-to-resize functionality.

This creates a simple test app with multiple session panes to verify that
the drag-to-resize functionality works correctly.
"""

from textual.app import App, ComposeResult
from textual.widgets import Static, Footer
from textual.containers import Container
from claude_multi_terminal.widgets.resizable_grid import (
    ResizableSessionGrid,
    Splitter,
    ResizablePane,
)


class TestPane(Static):
    """Simple test pane that displays its size."""

    def __init__(self, pane_name: str, **kwargs):
        super().__init__(**kwargs)
        self.pane_name = pane_name
        self.border_title = pane_name

    def on_mount(self) -> None:
        """Set up the pane."""
        self.update(f"[bold cyan]{self.pane_name}[/]\n\nDrag the dividers to resize!\n\nSize: updating...")
        self.set_interval(0.5, self._update_size)

    def _update_size(self) -> None:
        """Update the size display."""
        size = self.size
        self.update(
            f"[bold cyan]{self.pane_name}[/]\n\n"
            f"Drag the dividers to resize!\n\n"
            f"Size: [bold yellow]{size.width} x {size.height}[/]"
        )


class TestResizableApp(App):
    """Test application for resizable grid."""

    CSS = """
    TestPane {
        border: heavy rgb(66,66,66);
        background: rgb(32,32,32);
        padding: 2;
        height: 1fr;
        width: 1fr;
    }

    TestPane:focus {
        border: heavy rgb(255,183,77);
    }

    Screen {
        background: rgb(24,24,24);
    }
    """

    BINDINGS = [
        ("q", "quit", "Quit"),
        ("1", "layout_1", "1 Pane"),
        ("2", "layout_2", "2 Panes"),
        ("3", "layout_3", "3 Panes"),
        ("4", "layout_4", "4 Panes"),
    ]

    def compose(self) -> ComposeResult:
        """Compose the test UI."""
        yield Container(id="main-container")
        yield Footer()

    async def on_mount(self) -> None:
        """Set up initial layout."""
        await self.action_layout_2()

    async def action_layout_1(self) -> None:
        """Switch to 1-pane layout."""
        container = self.query_one("#main-container", Container)
        await container.query("*").remove()

        pane = ResizablePane(TestPane("Pane 1"))
        await container.mount(pane)

    async def action_layout_2(self) -> None:
        """Switch to 2-pane side-by-side layout."""
        from textual.containers import Horizontal

        container = self.query_one("#main-container", Container)
        await container.query("*").remove()

        left = ResizablePane(TestPane("Left Pane"))
        left.styles.width = "1fr"
        right = ResizablePane(TestPane("Right Pane"))
        right.styles.width = "1fr"

        splitter = Splitter(orientation="vertical")

        layout = Horizontal(left, splitter, right)
        await container.mount(layout)

    async def action_layout_3(self) -> None:
        """Switch to 3-pane layout (2 top, 1 bottom)."""
        from textual.containers import Horizontal, Vertical

        container = self.query_one("#main-container", Container)
        await container.query("*").remove()

        top_left = ResizablePane(TestPane("Top Left"))
        top_left.styles.width = "1fr"
        top_right = ResizablePane(TestPane("Top Right"))
        top_right.styles.width = "1fr"

        v_splitter = Splitter(orientation="vertical")

        top_row = Horizontal(top_left, v_splitter, top_right)
        top_row.styles.height = "1fr"

        h_splitter = Splitter(orientation="horizontal")

        bottom = ResizablePane(TestPane("Bottom Pane"))
        bottom.styles.height = "1fr"

        layout = Vertical(top_row, h_splitter, bottom)
        await container.mount(layout)

    async def action_layout_4(self) -> None:
        """Switch to 4-pane 2x2 grid layout."""
        from textual.containers import Horizontal, Vertical

        container = self.query_one("#main-container", Container)
        await container.query("*").remove()

        # Top row
        top_left = ResizablePane(TestPane("Top Left"))
        top_left.styles.width = "1fr"
        top_right = ResizablePane(TestPane("Top Right"))
        top_right.styles.width = "1fr"

        v_splitter_top = Splitter(orientation="vertical")

        top_row = Horizontal(top_left, v_splitter_top, top_right)
        top_row.styles.height = "1fr"

        h_splitter = Splitter(orientation="horizontal")

        # Bottom row
        bottom_left = ResizablePane(TestPane("Bottom Left"))
        bottom_left.styles.width = "1fr"
        bottom_right = ResizablePane(TestPane("Bottom Right"))
        bottom_right.styles.width = "1fr"

        v_splitter_bottom = Splitter(orientation="vertical")

        bottom_row = Horizontal(bottom_left, v_splitter_bottom, bottom_right)
        bottom_row.styles.height = "1fr"

        layout = Vertical(top_row, h_splitter, bottom_row)
        await container.mount(layout)


if __name__ == "__main__":
    app = TestResizableApp()
    app.run()
