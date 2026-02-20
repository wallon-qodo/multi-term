"""Archive browser widget for viewing and restoring archived sessions.

This widget provides a user-friendly interface for browsing archived sessions,
searching through archives, and restoring sessions when needed.

Features:
    - Browse archived sessions
    - Search by name, directory, date range
    - View archive statistics
    - Restore sessions with one click
    - Display compression savings
"""

from textual.app import ComposeResult
from textual.widgets import Static, Label, Button, Input, DataTable
from textual.containers import Container, Vertical, Horizontal
from textual.binding import Binding
from datetime import datetime
from typing import Optional

from ..archiver import SessionArchiver, ArchiveEntry


class ArchiveBrowser(Container):
    """Widget for browsing and restoring archived sessions.

    This widget displays a searchable list of archived sessions with
    metadata and provides controls for restoration.

    Bindings:
        r: Restore selected session
        /: Focus search input
        escape: Close browser
    """

    BINDINGS = [
        Binding("r", "restore_selected", "Restore", show=True),
        Binding("/", "focus_search", "Search", show=True),
        Binding("escape", "close", "Close", show=True),
    ]

    DEFAULT_CSS = """
    ArchiveBrowser {
        width: 100%;
        height: 100%;
        background: $surface;
        border: thick $primary;
        padding: 1;
    }

    ArchiveBrowser Vertical {
        width: 100%;
        height: 100%;
    }

    ArchiveBrowser .header {
        width: 100%;
        height: auto;
        background: $primary;
        color: $text;
        padding: 0 1;
        margin-bottom: 1;
    }

    ArchiveBrowser .search-bar {
        width: 100%;
        height: auto;
        margin-bottom: 1;
    }

    ArchiveBrowser DataTable {
        width: 100%;
        height: 1fr;
        margin-bottom: 1;
    }

    ArchiveBrowser .stats {
        width: 100%;
        height: auto;
        background: $panel;
        padding: 0 1;
    }

    ArchiveBrowser .controls {
        width: 100%;
        height: auto;
        margin-top: 1;
    }
    """

    def __init__(
        self,
        archiver: SessionArchiver,
        on_restore: Optional[callable] = None,
        **kwargs
    ):
        """Initialize archive browser.

        Args:
            archiver: SessionArchiver instance
            on_restore: Callback when session is restored, receives SessionState
            **kwargs: Additional container kwargs
        """
        super().__init__(**kwargs)
        self.archiver = archiver
        self.on_restore = on_restore
        self.selected_session_id: Optional[str] = None

    def compose(self) -> ComposeResult:
        """Create child widgets."""
        with Vertical():
            # Header
            with Horizontal(classes="header"):
                yield Label("📦 Archive Browser", id="header-label")

            # Search bar
            with Horizontal(classes="search-bar"):
                yield Input(
                    placeholder="Search by name or directory...",
                    id="search-input"
                )
                yield Button("Search", id="search-btn", variant="primary")
                yield Button("Clear", id="clear-btn", variant="default")

            # Data table
            yield DataTable(id="archive-table", zebra_stripes=True)

            # Statistics
            yield Label("", id="stats-label", classes="stats")

            # Controls
            with Horizontal(classes="controls"):
                yield Button("Restore", id="restore-btn", variant="success")
                yield Button("Refresh", id="refresh-btn", variant="default")
                yield Button("Close", id="close-btn", variant="default")

    def on_mount(self) -> None:
        """Set up the widget after mounting."""
        # Configure table
        table = self.query_one("#archive-table", DataTable)
        table.cursor_type = "row"

        # Add columns
        table.add_columns(
            "Name",
            "Directory",
            "Archived",
            "Size",
            "Saved",
            "ID"
        )

        # Load initial data
        self._load_archives()
        self._update_stats()

    def _load_archives(self, search_term: Optional[str] = None) -> None:
        """Load and display archived sessions.

        Args:
            search_term: Optional search filter
        """
        table = self.query_one("#archive-table", DataTable)
        table.clear()

        # Search archives
        if search_term:
            entries = self.archiver.index.search(
                name=search_term,
                working_dir=search_term,
                limit=100
            )
        else:
            entries = list(self.archiver.index.entries.values())
            entries.sort(key=lambda e: e.archived_at, reverse=True)
            entries = entries[:100]  # Limit to most recent 100

        # Add rows
        for entry in entries:
            archived_date = datetime.fromtimestamp(entry.archived_at)
            archived_str = archived_date.strftime("%Y-%m-%d %H:%M")

            size_mb = entry.size_bytes / (1024 * 1024)
            saved_mb = (entry.original_size_bytes - entry.size_bytes) / (1024 * 1024)
            compression_pct = (1 - entry.size_bytes / entry.original_size_bytes) * 100

            table.add_row(
                entry.name,
                entry.working_directory[:40],  # Truncate long paths
                archived_str,
                f"{size_mb:.2f} MB",
                f"{saved_mb:.2f} MB ({compression_pct:.0f}%)",
                entry.session_id[:8],  # Show short ID
                key=entry.session_id
            )

    def _update_stats(self) -> None:
        """Update statistics label."""
        stats = self.archiver.get_archive_stats()
        stats_label = self.query_one("#stats-label", Label)

        stats_text = (
            f"📊 Total: {stats['total_sessions']} sessions | "
            f"Size: {stats['total_size_mb']:.2f} MB | "
            f"Saved: {stats['space_saved_mb']:.2f} MB | "
            f"Threshold: {stats['archive_days_threshold']} days"
        )
        stats_label.update(stats_text)

    def on_data_table_row_selected(self, event: DataTable.RowSelected) -> None:
        """Handle row selection.

        Args:
            event: Row selected event
        """
        self.selected_session_id = event.row_key.value

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses.

        Args:
            event: Button pressed event
        """
        button_id = event.button.id

        if button_id == "search-btn":
            search_input = self.query_one("#search-input", Input)
            self._load_archives(search_input.value if search_input.value else None)

        elif button_id == "clear-btn":
            search_input = self.query_one("#search-input", Input)
            search_input.value = ""
            self._load_archives()

        elif button_id == "restore-btn":
            self.action_restore_selected()

        elif button_id == "refresh-btn":
            self._load_archives()
            self._update_stats()

        elif button_id == "close-btn":
            self.action_close()

    def action_restore_selected(self) -> None:
        """Restore the selected session."""
        if not self.selected_session_id:
            # Show notification (would need app context)
            return

        # Restore session
        session = self.archiver.restore_session(self.selected_session_id)
        if session and self.on_restore:
            self.on_restore(session)

    def action_focus_search(self) -> None:
        """Focus the search input."""
        search_input = self.query_one("#search-input", Input)
        search_input.focus()

    def action_close(self) -> None:
        """Close the browser."""
        self.remove()


class ArchiveStatsWidget(Static):
    """Compact widget showing archive statistics.

    This widget provides a quick overview of archive status,
    suitable for display in status bars or headers.
    """

    def __init__(self, archiver: SessionArchiver, **kwargs):
        """Initialize stats widget.

        Args:
            archiver: SessionArchiver instance
            **kwargs: Additional static kwargs
        """
        super().__init__(**kwargs)
        self.archiver = archiver

    def on_mount(self) -> None:
        """Update stats on mount."""
        self.update_stats()

    def update_stats(self) -> None:
        """Update the displayed statistics."""
        stats = self.archiver.get_archive_stats()

        if stats['total_sessions'] == 0:
            self.update("📦 Archive: Empty")
        else:
            self.update(
                f"📦 Archive: {stats['total_sessions']} sessions "
                f"({stats['total_size_mb']:.1f} MB, saved {stats['space_saved_mb']:.1f} MB)"
            )
