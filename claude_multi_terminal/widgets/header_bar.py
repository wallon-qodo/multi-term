"""Header bar widget with app title and status."""

from textual.widgets import Static
from textual.reactive import reactive
from rich.text import Text
import datetime
from zoneinfo import ZoneInfo
import time


class HeaderBar(Static):
    """Top header bar showing app title and session count."""

    DEFAULT_CSS = """
    HeaderBar {
        dock: top;
        background: rgb(26,26,26);
        color: rgb(240,240,240);
        height: 3;
        padding: 0 2;
        border-bottom: heavy rgb(42,42,42);
    }
    """

    session_count = reactive(0)
    active_workspace = reactive(1)  # Default to workspace 1
    workspace_sessions = reactive({i: 0 for i in range(1, 10)})  # Session count per workspace

    def render(self) -> Text:
        """Render header content with OpenClaw styling."""
        text = Text()

        # Left side: App branding with Coral Red accent
        text.append("╔═══", style="bold rgb(255,77,77)")
        text.append(" ⚡ ", style="bold rgb(255,100,100)")
        text.append("CLAUDE MULTI-TERMINAL", style="bold rgb(255,77,77)")
        text.append(" ", style="")

        # Workspace indicators section
        text.append("┃", style="rgb(120,120,120)")
        text.append(" ", style="")

        for i in range(1, 10):
            # Workspace number with styling
            if i == self.active_workspace:
                # Active workspace: coral background
                text.append("[", style="bold rgb(255,77,77)")
                text.append(str(i), style="bold rgb(255,255,255) on rgb(255,77,77)")

                # Show session count if any
                session_count = self.workspace_sessions.get(i, 0)
                if session_count > 0:
                    text.append("•", style="bold rgb(255,255,255) on rgb(255,77,77)")
                    text.append(str(session_count), style="bold rgb(255,255,255) on rgb(255,77,77)")

                text.append("]", style="bold rgb(255,77,77)")
            else:
                # Inactive workspace: dim border
                session_count = self.workspace_sessions.get(i, 0)
                if session_count > 0:
                    # Has sessions: show with count
                    text.append("[", style="dim rgb(120,120,120)")
                    text.append(str(i), style="rgb(180,180,180)")
                    text.append("•", style="dim rgb(120,120,120)")
                    text.append(str(session_count), style="rgb(180,180,180)")
                    text.append("]", style="dim rgb(120,120,120)")
                else:
                    # Empty workspace: very dim
                    text.append("[", style="dim rgb(80,80,80)")
                    text.append(str(i), style="dim rgb(120,120,120)")
                    text.append("]", style="dim rgb(80,80,80)")

            # Spacing between workspace indicators
            text.append(" ", style="")

        # Session badge with OpenClaw colors (total active sessions)
        if self.session_count > 0:
            badge_color = "rgb(120,200,120)" if self.session_count <= 4 else "rgb(255,180,70)"
            text.append("┃", style="rgb(120,120,120)")
            text.append(" ", style="")
            text.append(f"●", style=f"bold {badge_color}")
            text.append(f" {self.session_count} Active", style="bold rgb(240,240,240)")
            text.append(" ", style="")

        text.append("═══╗", style="bold rgb(255,77,77)")

        # Right side: System info with amber accents
        # Get user's local timezone
        try:
            # Get local timezone name
            if time.daylight:
                # DST is in effect
                tz_offset = -time.altzone
                tz_name = time.tzname[1]
            else:
                # Standard time
                tz_offset = -time.timezone
                tz_name = time.tzname[0]

            # Get current time in local timezone
            local_tz = datetime.datetime.now().astimezone().tzinfo
            now = datetime.datetime.now(tz=local_tz)

            # Format: 2:26 PM PST (12-hour format with timezone)
            time_str = now.strftime("%I:%M %p")

            # Get timezone abbreviation (PST, EST, CST, MST, etc.)
            tz_abbr = now.strftime("%Z")

            # If timezone abbreviation is empty or too long, use tz_name
            if not tz_abbr or len(tz_abbr) > 5:
                tz_abbr = tz_name

        except Exception:
            # Fallback to simple format if timezone detection fails
            now = datetime.datetime.now()
            time_str = now.strftime("%I:%M %p")
            tz_abbr = "Local"

        text.append("  " * 20)  # Spacer
        text.append("┃ ", style="rgb(120,120,120)")
        text.append("🕐 ", style="")
        text.append(time_str, style="bold rgb(100,180,240)")
        text.append(f" {tz_abbr}", style="dim rgb(150,150,180)")

        return text

    def set_active_workspace(self, workspace_id: int) -> None:
        """Set the active workspace (1-9).

        Args:
            workspace_id: Workspace number (1-9)
        """
        if 1 <= workspace_id <= 9:
            self.active_workspace = workspace_id

    def update_workspace_sessions(self, workspace_id: int, count: int) -> None:
        """Update session count for a specific workspace.

        Args:
            workspace_id: Workspace number (1-9)
            count: Number of sessions in the workspace
        """
        if 1 <= workspace_id <= 9:
            sessions = dict(self.workspace_sessions)  # Create mutable copy
            sessions[workspace_id] = count
            self.workspace_sessions = sessions  # Trigger reactive update

    def update_all_workspace_sessions(self, session_counts: dict) -> None:
        """Update session counts for all workspaces.

        Args:
            session_counts: Dict mapping workspace_id (1-9) to session count
        """
        sessions = {i: 0 for i in range(1, 10)}  # Initialize all to 0
        for workspace_id, count in session_counts.items():
            if 1 <= workspace_id <= 9:
                sessions[workspace_id] = count
        self.workspace_sessions = sessions
