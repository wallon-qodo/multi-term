"""Context menu widget for tab right-click actions."""

from textual.widgets import Static
from textual.containers import Vertical
from textual.message import Message
from textual import events
from typing import List, Tuple


class ContextMenuItem(Static):
    """Individual menu item in the context menu."""

    def __init__(self, label: str, action: str, **kwargs):
        """
        Initialize menu item.

        Args:
            label: Display text for the menu item
            action: Action identifier (e.g., "rename", "close")
        """
        super().__init__(label, **kwargs)
        self.action = action
        self.can_focus = False

    def on_mouse_down(self, event: events.MouseDown) -> None:
        """Handle click on menu item."""
        if event.button == 1:
            # Post message to parent context menu
            if self.parent and hasattr(self.parent, 'post_item_selected'):
                self.parent.post_item_selected(self.action)
            event.stop()


class ContextMenu(Vertical):
    """
    Context menu for tab actions.

    Features:
    - Appears at cursor position on right-click
    - Menu items: Rename, Close, etc.
    - Click outside to dismiss
    - Styled to match Homebrew theme
    """

    DEFAULT_CSS = """
    ContextMenu {
        width: 20;
        height: auto;
        background: rgb(40,40,40);
        border: solid rgb(100,180,240);
        padding: 0;
        layer: overlay;
    }

    ContextMenu > ContextMenuItem {
        width: 100%;
        height: 1;
        padding: 0 1;
        background: rgb(40,40,40);
        color: rgb(240,240,240);
    }

    ContextMenu > ContextMenuItem:hover {
        background: rgb(100,180,240);
        color: rgb(255,255,255);
        text-style: bold;
    }
    """

    class ItemSelected(Message):
        """Posted when a menu item is clicked."""

        def __init__(self, action: str, session_id: str) -> None:
            super().__init__()
            self.action = action
            self.session_id = session_id

    def __init__(
        self,
        items: List[Tuple[str, str]],
        session_id: str,
        x: int,
        y: int,
        **kwargs
    ):
        """
        Initialize context menu.

        Args:
            items: List of (label, action) tuples
            session_id: Session ID this menu is for
            x: X coordinate to display menu
            y: Y coordinate to display menu
        """
        super().__init__(**kwargs)
        self.menu_items = items
        self.session_id = session_id
        self.menu_x = x
        self.menu_y = y

    def compose(self):
        """Compose menu items."""
        for label, action in self.menu_items:
            yield ContextMenuItem(label, action)

    def on_mount(self) -> None:
        """Position the menu when mounted."""
        # Set absolute position
        self.styles.offset = (self.menu_x, self.menu_y)

    def post_item_selected(self, action: str) -> None:
        """Post ItemSelected message and remove self."""
        self.post_message(self.ItemSelected(action, self.session_id))
        self.remove()
