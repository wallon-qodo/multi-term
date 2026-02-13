"""Session History Browser widget for viewing and restoring past sessions."""

from textual.app import ComposeResult
from textual.screen import ModalScreen
from textual.widgets import Static, Button, Input, ListView, ListItem, Label
from textual.containers import Container, Vertical, Horizontal
from textual.binding import Binding
from typing import List, Optional, Callable
from datetime import datetime

from ..persistence.session_state import SessionState


class SessionHistoryItem(ListItem):
    """Individual session history item in the list."""

    def __init__(self, session: SessionState, **kwargs):
        """
        Initialize history item.

        Args:
            session: SessionState to display
        """
        super().__init__(**kwargs)
        self.session = session

    def compose(self) -> ComposeResult:
        """Compose the history item layout."""
        # Format timestamp
        timestamp = datetime.fromtimestamp(self.session.modified_at or self.session.created_at)
        time_str = timestamp.strftime("%Y-%m-%d %H:%M:%S")

        # Build display text
        with Vertical(classes="history-item-content"):
            yield Static(f"📋 {self.session.name}", classes="session-name")
            yield Static(f"📁 {self.session.working_directory}", classes="session-dir")
            yield Static(f"🕐 {time_str} | ⚡ {self.session.command_count} commands", classes="session-meta")
            if self.session.last_command:
                yield Static(f"💬 Last: {self.session.last_command[:60]}", classes="session-last-cmd")


class SessionHistoryBrowser(ModalScreen):
    """
    Modal screen for browsing session history.

    Features:
    - List of all saved sessions
    - Search/filter by name
    - Restore session to reopen
    - Delete session from history
    - Preview session details
    """

    DEFAULT_CSS = """
    SessionHistoryBrowser {
        align: center middle;
    }

    SessionHistoryBrowser > Container {
        width: 90;
        height: 35;
        background: rgb(32,32,32);
        border: thick rgb(100,180,240);
    }

    SessionHistoryBrowser .header {
        height: 3;
        background: rgb(40,40,40);
        color: rgb(100,180,240);
        content-align: center middle;
        text-style: bold;
    }

    SessionHistoryBrowser .search-box {
        height: 3;
        padding: 0 1;
        background: rgb(30,30,30);
    }

    SessionHistoryBrowser Input {
        width: 1fr;
        background: rgb(26,26,26);
        border: solid rgb(42,42,42);
    }

    SessionHistoryBrowser Input:focus {
        border: solid rgb(100,180,240);
    }

    SessionHistoryBrowser ListView {
        height: 1fr;
        background: rgb(32,32,32);
        padding: 1;
    }

    SessionHistoryBrowser ListItem {
        height: auto;
        padding: 1;
        background: rgb(30,30,30);
        border: solid rgb(42,42,42);
        margin: 0 0 1 0;
    }

    SessionHistoryBrowser ListItem:hover {
        background: rgb(45,45,45);
    }

    SessionHistoryBrowser ListItem.-selected {
        background: rgb(40,40,40);
        border: solid rgb(100,180,240);
    }

    SessionHistoryBrowser .history-item-content {
        height: auto;
    }

    SessionHistoryBrowser .session-name {
        color: rgb(255,100,100);
        text-style: bold;
    }

    SessionHistoryBrowser .session-dir {
        color: rgb(180,180,180);
        text-style: italic;
    }

    SessionHistoryBrowser .session-meta {
        color: rgb(156,156,156);
    }

    SessionHistoryBrowser .session-last-cmd {
        color: rgb(169,169,169);
        text-style: dim;
    }

    SessionHistoryBrowser .button-bar {
        height: 3;
        padding: 0 1;
        background: rgb(30,30,30);
        align: center middle;
    }

    SessionHistoryBrowser Button {
        margin: 0 1;
        min-width: 12;
    }

    SessionHistoryBrowser .restore-button {
        background: rgb(76,175,80);
        color: rgb(255,255,255);
    }

    SessionHistoryBrowser .restore-button:hover {
        background: rgb(56,142,60);
    }

    SessionHistoryBrowser .delete-button {
        background: rgb(255,77,77);
        color: rgb(255,255,255);
    }

    SessionHistoryBrowser .delete-button:hover {
        background: rgb(198,40,40);
    }

    SessionHistoryBrowser .cancel-button {
        background: rgb(80,80,80);
        color: rgb(240,240,240);
    }

    SessionHistoryBrowser .cancel-button:hover {
        background: rgb(100,100,100);
    }

    SessionHistoryBrowser .empty-state {
        height: 1fr;
        content-align: center middle;
        color: rgb(156,156,156);
        text-style: italic;
    }
    """

    BINDINGS = [
        Binding("escape", "cancel", "Cancel"),
        Binding("enter", "restore", "Restore"),
        Binding("delete", "delete", "Delete"),
    ]

    def __init__(
        self,
        sessions: List[SessionState],
        on_restore: Optional[Callable[[SessionState], None]] = None,
        on_delete: Optional[Callable[[str], None]] = None,
        **kwargs
    ):
        """
        Initialize session history browser.

        Args:
            sessions: List of SessionState objects to display
            on_restore: Callback when session is restored
            on_delete: Callback when session is deleted
        """
        super().__init__(**kwargs)
        self.all_sessions = sessions
        self.filtered_sessions = sessions.copy()
        self.on_restore_callback = on_restore
        self.on_delete_callback = on_delete
        self.selected_session: Optional[SessionState] = None

    def compose(self) -> ComposeResult:
        """Compose the history browser layout."""
        with Container():
            yield Static("📚 Session History", classes="header")

            with Horizontal(classes="search-box"):
                yield Input(
                    placeholder="Search sessions by name or directory...",
                    id="search-input"
                )

            if self.filtered_sessions:
                list_view = ListView(id="session-list")
                list_view.can_focus = True
                yield list_view
            else:
                yield Static(
                    "No session history found.\nClosed sessions are automatically saved here.",
                    classes="empty-state"
                )

            with Horizontal(classes="button-bar"):
                yield Button("Restore", variant="success", classes="restore-button", id="restore-btn")
                yield Button("Delete", variant="error", classes="delete-button", id="delete-btn")
                yield Button("Cancel", classes="cancel-button", id="cancel-btn")

    async def on_mount(self) -> None:
        """Populate the list when mounted."""
        if self.filtered_sessions:
            await self._populate_list()

            # Focus the list view
            list_view = self.query_one("#session-list", ListView)
            list_view.focus()

    async def _populate_list(self) -> None:
        """Populate the list view with session items."""
        list_view = self.query_one("#session-list", ListView)
        await list_view.clear()

        for session in self.filtered_sessions:
            item = SessionHistoryItem(session)
            await list_view.append(item)

    async def on_input_changed(self, event: Input.Changed) -> None:
        """Handle search input changes."""
        if event.input.id != "search-input":
            return

        search_term = event.value.lower().strip()

        if not search_term:
            # Show all sessions
            self.filtered_sessions = self.all_sessions.copy()
        else:
            # Filter sessions
            self.filtered_sessions = [
                session for session in self.all_sessions
                if (search_term in session.name.lower() or
                    search_term in session.working_directory.lower())
            ]

        # Repopulate list
        await self._populate_list()

    async def on_list_view_selected(self, event: ListView.Selected) -> None:
        """Handle list item selection."""
        if isinstance(event.item, SessionHistoryItem):
            self.selected_session = event.item.session

    async def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button clicks."""
        button_id = event.button.id

        if button_id == "restore-btn":
            await self.action_restore()
        elif button_id == "delete-btn":
            await self.action_delete()
        elif button_id == "cancel-btn":
            await self.action_cancel()

    async def action_restore(self) -> None:
        """Restore the selected session."""
        if not self.selected_session:
            # Try to get first selected item from list
            try:
                list_view = self.query_one("#session-list", ListView)
                if list_view.index is not None:
                    item = list_view.children[list_view.index]
                    if isinstance(item, SessionHistoryItem):
                        self.selected_session = item.session
            except Exception:
                pass

        if self.selected_session and self.on_restore_callback:
            self.on_restore_callback(self.selected_session)
            self.dismiss()
        else:
            # No session selected
            pass

    async def action_delete(self) -> None:
        """Delete the selected session."""
        if not self.selected_session:
            # Try to get first selected item from list
            try:
                list_view = self.query_one("#session-list", ListView)
                if list_view.index is not None:
                    item = list_view.children[list_view.index]
                    if isinstance(item, SessionHistoryItem):
                        self.selected_session = item.session
            except Exception:
                pass

        if self.selected_session:
            # Remove from lists
            session_id = self.selected_session.session_id
            self.all_sessions = [s for s in self.all_sessions if s.session_id != session_id]
            self.filtered_sessions = [s for s in self.filtered_sessions if s.session_id != session_id]

            # Call delete callback
            if self.on_delete_callback:
                self.on_delete_callback(session_id)

            # Repopulate list
            await self._populate_list()

            # Clear selection
            self.selected_session = None

    async def action_cancel(self) -> None:
        """Cancel and close the browser."""
        self.dismiss()
