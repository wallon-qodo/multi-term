"""Window manager for floating windows with z-index ordering."""

from textual.containers import Container
from textual.widget import Widget
from textual.geometry import Offset, Size
from typing import List
from .floating_window import FloatingWindow


class WindowManager(Container):
    """Manages floating windows with z-index ordering."""

    DEFAULT_CSS = """
    WindowManager {
        width: 100%;
        height: 100%;
        background: rgb(18, 18, 18);
        overflow: hidden;
        layout: vertical;
    }
    """

    def __init__(self, **kwargs):
        """Initialize the window manager.

        Args:
            **kwargs: Additional keyword arguments.
        """
        super().__init__(**kwargs)
        self.windows: List[FloatingWindow] = []
        self.active_window: FloatingWindow | None = None
        self.next_z_index = 1000

    async def add_window(
        self,
        title: str,
        content: Widget,
        x: int = 5,
        y: int = 5,
        width: int = 80,
        height: int = 25
    ) -> FloatingWindow:
        """Add a new floating window.

        Args:
            title: Window title.
            content: Widget to display in the window.
            x: Initial x position.
            y: Initial y position.
            width: Initial width.
            height: Initial height.

        Returns:
            The created FloatingWindow.
        """
        window = FloatingWindow(title, content)
        window.styles.offset = (x, y)
        window.styles.width = width
        window.styles.height = height

        self.windows.append(window)
        await self.mount(window)

        # Set initial z-index
        self._bring_to_front(window)

        return window

    def on_floating_window_window_focused(
        self, message: FloatingWindow.WindowFocused
    ) -> None:
        """Handle window focus events.

        Args:
            message: The window focused message.
        """
        self._bring_to_front(message.window)
        message.stop()

    async def on_floating_window_window_closed(
        self, message: FloatingWindow.WindowClosed
    ) -> None:
        """Handle window close events.

        Args:
            message: The window closed message.
        """
        await self.remove_window(message.window)
        message.stop()

    def _bring_to_front(self, window: FloatingWindow) -> None:
        """Bring a window to the front.

        Args:
            window: The window to bring to front.
        """
        # Deactivate previous active window
        if self.active_window and self.active_window != window:
            self.active_window.is_active = False

        # Activate new window
        window.is_active = True
        self.active_window = window

        # Set z-index using layers
        window.styles.layer = str(self.next_z_index)
        self.next_z_index += 1

    async def remove_window(self, window: FloatingWindow) -> None:
        """Remove a window.

        Args:
            window: The window to remove.
        """
        if window in self.windows:
            self.windows.remove(window)
            await window.remove()

            # Focus next window
            if self.windows:
                self._bring_to_front(self.windows[-1])
            else:
                self.active_window = None

    async def tile_windows(self) -> None:
        """Arrange windows in a tiled layout."""
        if not self.windows:
            return

        count = len(self.windows)
        cols = int(count ** 0.5)
        if cols * cols < count:
            cols += 1
        rows = (count + cols - 1) // cols

        # Get available space
        container_width = self.size.width
        container_height = self.size.height

        # Calculate window dimensions with some padding
        padding = 2
        window_width = (container_width // cols) - padding
        window_height = (container_height // rows) - padding

        for i, window in enumerate(self.windows):
            col = i % cols
            row = i // cols

            x = col * (window_width + padding)
            y = row * (window_height + padding)

            window.styles.offset = (x, y)
            window.styles.width = window_width
            window.styles.height = window_height

    async def cascade_windows(self) -> None:
        """Arrange windows in a cascading layout."""
        if not self.windows:
            return

        offset_x = 5
        offset_y = 3
        base_width = 80
        base_height = 25

        for i, window in enumerate(self.windows):
            x = offset_x + (i * 3)
            y = offset_y + (i * 2)

            window.styles.offset = (x, y)
            window.styles.width = base_width
            window.styles.height = base_height

    def get_window_count(self) -> int:
        """Get the number of windows.

        Returns:
            The number of windows.
        """
        return len(self.windows)

    def get_active_window(self) -> FloatingWindow | None:
        """Get the currently active window.

        Returns:
            The active window, or None if no window is active.
        """
        return self.active_window

    async def close_all_windows(self) -> None:
        """Close all windows."""
        # Create a copy of the list since we'll be modifying it
        windows_to_close = list(self.windows)
        for window in windows_to_close:
            await self.remove_window(window)
