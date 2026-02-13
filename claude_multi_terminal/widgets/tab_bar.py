"""Tab bar widget for session management."""

from textual.containers import Horizontal, Container
from textual.widgets import Static
from textual.reactive import reactive
from textual.app import ComposeResult
from typing import Optional, List
from rich.text import Text

from .tab_item import Tab


class TabBar(Container):
    """
    Tab bar displaying all open sessions.

    Features:
    - Horizontal layout of tabs
    - Automatic overflow handling
    - Active tab highlighting
    - Tab switching on click
    - Close buttons on tabs
    """

    DEFAULT_CSS = """
    TabBar {
        height: 3;
        width: 1fr;
        background: rgb(26,26,26);
        border-bottom: solid rgb(42,42,42);
        layout: horizontal;
        padding: 0;
    }

    TabBar Horizontal {
        height: 3;
        width: auto;
        scrollbar-size: 0 0;
        overflow-x: auto;
        overflow-y: hidden;
    }

    TabBar .tab-container {
        height: 3;
        width: auto;
    }

    TabBar .overflow-indicator {
        width: 5;
        height: 3;
        background: rgb(32,32,32);
        color: rgb(255,77,77);
        content-align: center middle;
        display: none;
    }

    TabBar .overflow-indicator.visible {
        display: block;
    }
    """

    tab_count = reactive(0)

    def __init__(self, *args, **kwargs):
        """Initialize tab bar."""
        super().__init__(*args, **kwargs)
        self.tabs: List[Tab] = []
        self.active_session_id: Optional[str] = None

    def compose(self) -> ComposeResult:
        """Compose the tab bar layout."""
        with Horizontal(classes="tab-container"):
            # Tabs will be dynamically added here
            pass
        yield Static("»", classes="overflow-indicator")

    async def add_tab(self, session_id: str, session_name: str, is_active: bool = False, custom_color: tuple[str, str] = None) -> None:
        """
        Add a new tab to the bar.

        Args:
            session_id: UUID of the session
            session_name: Display name for the tab
            is_active: Whether this tab should be active
            custom_color: Optional (color_name, color_rgb) tuple for custom color
        """
        # Create new tab
        tab = Tab(
            session_id=session_id,
            session_name=session_name,
            is_active=is_active,
            custom_color=custom_color
        )

        # Add to tabs list
        self.tabs.append(tab)
        self.tab_count = len(self.tabs)

        # Mount to container
        container = self.query_one(".tab-container", Horizontal)
        await container.mount(tab)

        # Update active session
        if is_active:
            self.active_session_id = session_id
            # Deactivate other tabs
            for other_tab in self.tabs:
                if other_tab.session_id != session_id:
                    other_tab.is_active = False

        # Check for overflow
        await self._update_overflow_indicator()

    async def remove_tab(self, session_id: str) -> None:
        """
        Remove a tab from the bar.

        Args:
            session_id: UUID of the session to remove
        """
        # Find and remove tab
        tab_to_remove = None
        for tab in self.tabs:
            if tab.session_id == session_id:
                tab_to_remove = tab
                break

        if tab_to_remove:
            self.tabs.remove(tab_to_remove)
            self.tab_count = len(self.tabs)
            await tab_to_remove.remove()

            # If removed tab was active, activate another
            if self.active_session_id == session_id:
                self.active_session_id = None
                if self.tabs:
                    # Activate the first tab
                    await self.set_active_tab(self.tabs[0].session_id)

        # Check for overflow
        await self._update_overflow_indicator()

    async def set_active_tab(self, session_id: str) -> None:
        """
        Set which tab is active.

        Args:
            session_id: UUID of the session to activate
        """
        self.active_session_id = session_id

        # Update visual state of all tabs
        for tab in self.tabs:
            tab.is_active = (tab.session_id == session_id)

    async def update_tab_name(self, session_id: str, new_name: str) -> None:
        """
        Update the display name of a tab.

        Args:
            session_id: UUID of the session
            new_name: New name to display
        """
        for tab in self.tabs:
            if tab.session_id == session_id:
                tab.session_name = new_name
                tab.refresh()
                break

    async def update_tab_color(self, session_id: str, color: tuple[str, str] = None) -> None:
        """
        Update the color of a tab.

        Args:
            session_id: UUID of the session
            color: (color_name, color_rgb) tuple, or None to reset to default
        """
        for tab in self.tabs:
            if tab.session_id == session_id:
                tab.set_custom_color(color)
                tab.refresh()
                break

    def get_tab(self, session_id: str) -> Optional[Tab]:
        """
        Get tab by session ID.

        Args:
            session_id: UUID of the session

        Returns:
            Tab widget if found, None otherwise
        """
        for tab in self.tabs:
            if tab.session_id == session_id:
                return tab
        return None

    async def _update_overflow_indicator(self) -> None:
        """Update visibility of overflow indicator."""
        try:
            indicator = self.query_one(".overflow-indicator", Static)
            container = self.query_one(".tab-container", Horizontal)

            # Check if tabs overflow container width
            # This is approximate - in a real implementation we'd measure actual widths
            if len(self.tabs) > 6:  # Heuristic: ~6 tabs fit on average screen
                indicator.add_class("visible")
            else:
                indicator.remove_class("visible")
        except Exception:
            # Widgets might not be mounted yet
            pass

    async def clear_tabs(self) -> None:
        """Remove all tabs."""
        for tab in self.tabs:
            await tab.remove()
        self.tabs.clear()
        self.tab_count = 0
        self.active_session_id = None

    def on_tab_clicked(self, message: Tab.Clicked) -> None:
        """
        Handle tab click events.

        Args:
            message: Clicked message from Tab
        """
        # Let the event bubble up to the app
        pass

    def on_tab_close_requested(self, message: Tab.CloseRequested) -> None:
        """
        Handle tab close button clicks.

        Args:
            message: CloseRequested message from Tab
        """
        # Let the event bubble up to the app
        pass
