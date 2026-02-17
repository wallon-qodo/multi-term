"""Floating window widget with drag and resize capabilities."""

from textual.containers import Container, Vertical, Horizontal
from textual.widgets import Static, Label
from textual.reactive import reactive
from textual import events
from textual.geometry import Offset, Size
from textual.message import Message
from textual.widget import Widget


class FloatingWindow(Container):
    """A draggable, resizable floating window."""

    DEFAULT_CSS = """
    FloatingWindow {
        background: rgb(26, 26, 26);
        border: solid rgb(42, 42, 42);
        width: auto;
        height: auto;
        min-width: 40;
        min-height: 15;
        layer: windows;
        offset: 0 0;
    }

    FloatingWindow.active {
        border: solid rgb(255, 77, 77);
    }

    FloatingWindow .window-titlebar {
        background: rgb(32, 32, 32);
        color: rgb(240, 240, 240);
        height: 3;
        width: 100%;
        padding: 0 1;
        border-bottom: solid rgb(42, 42, 42);
    }

    FloatingWindow.active .window-titlebar {
        background: rgb(40, 40, 40);
        border-bottom: solid rgb(255, 77, 77);
    }

    FloatingWindow .window-titlebar:hover {
        background: rgb(45, 45, 45);
    }

    FloatingWindow .window-title {
        width: 1fr;
        height: 100%;
        content-align: left middle;
        color: rgb(240, 240, 240);
    }

    FloatingWindow .window-close {
        width: auto;
        height: 100%;
        content-align: center middle;
        color: rgb(255, 77, 77);
        padding: 0 1;
    }

    FloatingWindow .window-close:hover {
        background: rgb(255, 77, 77);
        color: rgb(240, 240, 240);
    }

    FloatingWindow .window-content {
        width: 100%;
        height: 1fr;
        background: rgb(26, 26, 26);
        overflow: auto;
    }

    FloatingWindow .window-resize-handle {
        dock: bottom;
        width: 100%;
        height: 1;
        background: rgb(26, 26, 26);
        content-align: right middle;
        color: rgb(255, 77, 77);
    }
    """

    class WindowMoved(Message):
        """Message sent when window is moved."""

        def __init__(self, window: "FloatingWindow", offset: Offset):
            super().__init__()
            self.window = window
            self.offset = offset

    class WindowResized(Message):
        """Message sent when window is resized."""

        def __init__(self, window: "FloatingWindow", size: Size):
            super().__init__()
            self.window = window
            self.size = size

    class WindowFocused(Message):
        """Message sent when window is focused."""

        def __init__(self, window: "FloatingWindow"):
            super().__init__()
            self.window = window

    class WindowClosed(Message):
        """Message sent when window close button is clicked."""

        def __init__(self, window: "FloatingWindow"):
            super().__init__()
            self.window = window

    is_active = reactive(False)

    def __init__(self, title: str, content: Widget, **kwargs):
        """Initialize the floating window.

        Args:
            title: Window title text.
            content: Widget to display in the content area.
            **kwargs: Additional keyword arguments.
        """
        super().__init__(**kwargs)
        self.window_title = title
        self.window_content = content
        self.is_dragging = False
        self.is_resizing = False
        self.drag_start = Offset(0, 0)
        self.resize_start = Offset(0, 0)
        self.initial_offset = Offset(0, 0)
        self.initial_size = Size(0, 0)

    def compose(self):
        """Compose the window layout."""
        with Vertical():
            # Title bar with close button
            with Horizontal(classes="window-titlebar"):
                yield Label(self.window_title, classes="window-title")
                yield Label("✕", classes="window-close", id="close-btn")

            # Content area
            with Container(classes="window-content"):
                yield self.window_content

            # Resize handle (bottom-right corner)
            yield Static("◣", classes="window-resize-handle", id="resize-handle")

    def on_mouse_down(self, event: events.MouseDown) -> None:
        """Handle mouse down events for dragging and resizing.

        Args:
            event: The mouse down event.
        """
        # Get the widget that was clicked
        widget_at_pos = self.get_widget_at(event.x, event.y)[0] if self.get_widget_at(event.x, event.y) else None

        # Check if clicking close button
        if widget_at_pos and hasattr(widget_at_pos, 'id') and widget_at_pos.id == "close-btn":
            self.post_message(self.WindowClosed(self))
            event.stop()
            return

        # Check if clicking resize handle
        if widget_at_pos and hasattr(widget_at_pos, 'id') and widget_at_pos.id == "resize-handle":
            self.is_resizing = True
            self.resize_start = Offset(event.screen_x, event.screen_y)
            self.initial_size = self.size
            self.capture_mouse()
            event.stop()
            return

        # Check if clicking titlebar (for dragging)
        if widget_at_pos and "window-titlebar" in widget_at_pos.classes:
            self.is_dragging = True
            self.drag_start = Offset(event.screen_x, event.screen_y)
            self.initial_offset = self.offset
            self.capture_mouse()
            event.stop()
            return

        # Focus window on any click
        self.post_message(self.WindowFocused(self))

    def on_mouse_move(self, event: events.MouseMove) -> None:
        """Handle mouse move events for dragging and resizing.

        Args:
            event: The mouse move event.
        """
        if self.is_dragging:
            delta_x = event.screen_x - self.drag_start.x
            delta_y = event.screen_y - self.drag_start.y
            new_offset = Offset(
                max(0, self.initial_offset.x + delta_x),
                max(0, self.initial_offset.y + delta_y)
            )
            self.styles.offset = (new_offset.x, new_offset.y)
            self.post_message(self.WindowMoved(self, new_offset))
            event.stop()

        elif self.is_resizing:
            delta_x = event.screen_x - self.resize_start.x
            delta_y = event.screen_y - self.resize_start.y
            new_width = max(40, self.initial_size.width + delta_x)
            new_height = max(15, self.initial_size.height + delta_y)
            self.styles.width = new_width
            self.styles.height = new_height
            self.post_message(self.WindowResized(self, Size(new_width, new_height)))
            event.stop()

    def on_mouse_up(self, event: events.MouseUp) -> None:
        """Handle mouse up events to stop dragging/resizing.

        Args:
            event: The mouse up event.
        """
        if self.is_dragging or self.is_resizing:
            self.is_dragging = False
            self.is_resizing = False
            self.release_mouse()
            event.stop()

    def watch_is_active(self, active: bool) -> None:
        """React to active state changes.

        Args:
            active: Whether the window is now active.
        """
        self.set_class(active, "active")
