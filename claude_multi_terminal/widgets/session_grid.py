"""Grid layout manager for multiple session panes."""

from textual.containers import Grid
from textual.reactive import reactive
from typing import TYPE_CHECKING

from .session_pane import SessionPane

if TYPE_CHECKING:
    from ..core.session_manager import SessionManager


class SessionGrid(Grid):
    """
    Container managing layout of multiple SessionPane widgets.

    Supports dynamic grid layouts:
    - 1 session: 1x1 (full screen)
    - 2 sessions: 2x1 (side-by-side)
    - 3 sessions: 2x2 (one empty cell)
    - 4 sessions: 2x2 (full grid)
    - 5+ sessions: Dynamic rows
    """

    pane_count = reactive(0)

    def __init__(self, *args, **kwargs):
        """Initialize session grid."""
        super().__init__(*args, **kwargs)
        self.panes = []

    def watch_pane_count(self, count: int) -> None:
        """Update grid layout when pane count changes."""
        if count == 0:
            self.styles.grid_size_columns = 1
            self.styles.grid_size_rows = 1
        elif count == 1:
            self.styles.grid_size_columns = 1
            self.styles.grid_size_rows = 1
        elif count == 2:
            self.styles.grid_size_columns = 2
            self.styles.grid_size_rows = 1
        elif count <= 4:
            self.styles.grid_size_columns = 2
            self.styles.grid_size_rows = 2
        else:
            # More than 4: use 2 columns, scale rows
            self.styles.grid_size_columns = 2
            self.styles.grid_size_rows = (count + 1) // 2

        # Use fractional units for even distribution
        self.styles.grid_gutter = 1

    async def add_session(self, session_id: str, session_manager: "SessionManager") -> None:
        """
        Add a new session pane to the grid.

        Args:
            session_id: UUID of the session
            session_manager: Reference to SessionManager
        """
        session_info = session_manager.sessions.get(session_id)

        if not session_info:
            return

        pane = SessionPane(
            session_id=session_id,
            session_name=session_info.name,
            session_manager=session_manager
        )

        await self.mount(pane)
        self.panes.append(pane)
        self.pane_count = len(self.panes)

    async def remove_session(self, session_id: str) -> None:
        """
        Remove a session pane from the grid.

        Args:
            session_id: UUID of the session to remove
        """
        for pane in self.panes:
            if pane.session_id == session_id:
                await pane.remove()
                self.panes.remove(pane)
                self.pane_count = len(self.panes)
                break

    async def clear(self) -> None:
        """Remove all session panes."""
        for pane in list(self.panes):
            await pane.remove()
        self.panes.clear()
        self.pane_count = 0
