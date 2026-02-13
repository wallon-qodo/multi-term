"""Individual tab widget for session switching."""

import time
from textual.widgets import Static
from textual.reactive import reactive
from textual import events
from textual.message import Message
from rich.text import Text


class Tab(Static):
    """
    Individual tab representing a session.

    Features:
    - Click to activate session
    - Close button (×)
    - Visual feedback for active/inactive state
    - Hover effects
    """

    DEFAULT_CSS = """
    Tab {
        width: auto;
        height: 3;
        min-width: 15;
        max-width: 30;
        padding: 0 2;
        background: rgb(28,28,28);
        color: rgb(180,180,180);
        border-right: solid rgb(42,42,42);
        content-align: center middle;
    }

    Tab:hover {
        background: rgb(38,38,38);
        color: rgb(240,240,240);
    }

    Tab.active {
        background: rgb(32,32,32);
        color: rgb(255,100,100);
        border-bottom: solid rgb(255,77,77);
    }

    Tab.active:hover {
        background: rgb(40,40,40);
    }

    Tab .close-button {
        color: rgb(180,180,180);
    }

    Tab .close-button:hover {
        color: rgb(255,77,77);
        background: rgba(255,77,77,0.2);
    }
    """

    is_active = reactive(False)

    class Clicked(Message):
        """Posted when tab is clicked to activate."""

        def __init__(self, tab: "Tab", session_id: str) -> None:
            super().__init__()
            self.tab = tab
            self.session_id = session_id

    class CloseRequested(Message):
        """Posted when close button is clicked."""

        def __init__(self, tab: "Tab", session_id: str) -> None:
            super().__init__()
            self.tab = tab
            self.session_id = session_id

    class RenameRequested(Message):
        """Posted when tab is double-clicked or rename is requested from context menu."""

        def __init__(self, tab: "Tab", session_id: str) -> None:
            super().__init__()
            self.tab = tab
            self.session_id = session_id

    class ContextMenuRequested(Message):
        """Posted when tab is right-clicked."""

        def __init__(self, tab: "Tab", session_id: str, screen_x: int, screen_y: int) -> None:
            super().__init__()
            self.tab = tab
            self.session_id = session_id
            self.screen_x = screen_x
            self.screen_y = screen_y

    def __init__(
        self,
        session_id: str,
        session_name: str,
        is_active: bool = False,
        custom_color: tuple[str, str] = None,
        **kwargs
    ):
        """
        Initialize tab.

        Args:
            session_id: UUID of the session
            session_name: Display name for the tab
            is_active: Whether this tab is currently active
            custom_color: Optional (color_name, color_rgb) tuple for custom color
        """
        super().__init__(**kwargs)
        self.session_id = session_id
        self.session_name = session_name
        self.custom_color = custom_color  # Set this BEFORE is_active
        self.can_focus = False  # Tabs don't receive focus

        # Double-click detection
        self._last_click_time = 0
        self._double_click_threshold = 0.5  # 500ms

        # Set is_active last (triggers watch_is_active which needs custom_color)
        self.is_active = is_active
        if is_active:
            self.add_class("active")

    def on_mount(self) -> None:
        """Apply custom color when mounted."""
        self._apply_custom_color()

    def set_custom_color(self, color: tuple[str, str] = None) -> None:
        """
        Set custom color for this tab.

        Args:
            color: (color_name, color_rgb) tuple, or None to reset to default
        """
        self.custom_color = color
        self._apply_custom_color()

    def _apply_custom_color(self) -> None:
        """Apply custom color styling if set."""
        # Safety check: custom_color might not exist during initialization
        if not hasattr(self, 'custom_color'):
            return

        if self.custom_color:
            color_name, color_rgb = self.custom_color
            # Apply custom color to tab
            if self.is_active:
                self.styles.color = color_rgb
                self.styles.border_bottom = ("solid", color_rgb)
            else:
                # For inactive tabs, use a dimmer version
                self.styles.color = color_rgb
        else:
            # Reset to default colors
            if self.is_active:
                self.styles.color = "rgb(255,100,100)"
                self.styles.border_bottom = ("solid", "rgb(255,77,77)")
            else:
                self.styles.color = "rgb(180,180,180)"

    def render(self) -> Text:
        """Render the tab with name and close button."""
        text = Text()

        # Session name (truncate if too long)
        display_name = self.session_name
        if len(display_name) > 20:
            display_name = display_name[:17] + "..."

        text.append(display_name, style="")
        text.append("  ", style="")
        text.append("×", style="dim")  # Close button

        return text

    def watch_is_active(self, is_active: bool) -> None:
        """Update visual state when active status changes."""
        if is_active:
            self.add_class("active")
        else:
            self.remove_class("active")
        # Reapply custom color with new active state
        self._apply_custom_color()

    def on_mouse_down(self, event: events.MouseDown) -> None:
        """Handle click events."""
        # Right-click - show context menu
        if event.button == 3:
            # Calculate screen coordinates for context menu
            screen_x = event.screen_x
            screen_y = event.screen_y
            self.post_message(self.ContextMenuRequested(self, self.session_id, screen_x, screen_y))
            event.stop()
            return

        # Only handle left clicks from here
        if event.button != 1:
            return

        # Check if click was on close button (last 3 characters)
        # This is approximate - checking if click is in right portion of tab
        if event.x >= (self.size.width - 3):
            # Close button clicked
            self.post_message(self.CloseRequested(self, self.session_id))
            event.stop()
        else:
            # Tab body clicked - check for double-click
            current_time = time.time()
            time_since_last_click = current_time - self._last_click_time

            if time_since_last_click < self._double_click_threshold:
                # Double-click detected - request rename
                self.post_message(self.RenameRequested(self, self.session_id))
                self._last_click_time = 0  # Reset to prevent triple-click
                event.stop()
            else:
                # Single click - activate session
                self._last_click_time = current_time
                self.post_message(self.Clicked(self, self.session_id))
                event.stop()
