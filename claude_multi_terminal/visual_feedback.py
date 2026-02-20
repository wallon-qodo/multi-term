"""
Visual feedback system for user actions.

Provides clear, immediate feedback for all user interactions through
icons, colors, progress indicators, and animations.
"""

from typing import Optional, Callable
from textual.app import App
from textual.widgets import Widget, Static, Label
from textual.containers import Container, Horizontal
from rich.text import Text
from dataclasses import dataclass
from enum import Enum


class FeedbackType(Enum):
    """Types of visual feedback."""

    SUCCESS = "success"
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"
    PROCESSING = "processing"


@dataclass
class FeedbackStyle:
    """Visual style for feedback."""

    icon: str
    color: str
    severity: str


# Feedback styles mapping
FEEDBACK_STYLES = {
    FeedbackType.SUCCESS: FeedbackStyle(
        icon="✓",
        color="green",
        severity="information"
    ),
    FeedbackType.ERROR: FeedbackStyle(
        icon="✗",
        color="red",
        severity="error"
    ),
    FeedbackType.WARNING: FeedbackStyle(
        icon="⚠",
        color="yellow",
        severity="warning"
    ),
    FeedbackType.INFO: FeedbackStyle(
        icon="ℹ",
        color="blue",
        severity="information"
    ),
    FeedbackType.PROCESSING: FeedbackStyle(
        icon="⟳",
        color="cyan",
        severity="information"
    ),
}


class VisualFeedback:
    """
    Visual feedback manager.

    Coordinates visual feedback across the application.
    """

    def __init__(self, app: App):
        """
        Initialize visual feedback manager.

        Args:
            app: Application instance
        """
        self.app = app

    def show_action_feedback(
        self,
        action: str,
        feedback_type: FeedbackType = FeedbackType.SUCCESS,
        details: Optional[str] = None,
        duration: float = 2.0,
    ) -> None:
        """
        Show visual feedback for an action.

        Args:
            action: Action description (e.g., "Workspace switched")
            feedback_type: Type of feedback
            details: Optional additional details
            duration: Display duration in seconds
        """
        style = FEEDBACK_STYLES[feedback_type]

        # Build message
        message = f"{style.icon} {action}"
        if details:
            message += f": {details}"

        # Show toast notification
        self.app.notify(
            message,
            severity=style.severity,
            timeout=duration
        )

    def show_success(self, action: str, details: Optional[str] = None) -> None:
        """
        Show success feedback.

        Args:
            action: Action description
            details: Optional details
        """
        self.show_action_feedback(action, FeedbackType.SUCCESS, details)

    def show_error(self, action: str, details: Optional[str] = None, duration: float = 4.0) -> None:
        """
        Show error feedback.

        Args:
            action: Action description
            details: Optional error details
            duration: Display duration (longer for errors)
        """
        self.show_action_feedback(action, FeedbackType.ERROR, details, duration)

    def show_warning(self, action: str, details: Optional[str] = None) -> None:
        """
        Show warning feedback.

        Args:
            action: Action description
            details: Optional warning details
        """
        self.show_action_feedback(action, FeedbackType.WARNING, details)

    def show_info(self, action: str, details: Optional[str] = None) -> None:
        """
        Show info feedback.

        Args:
            action: Action description
            details: Optional info details
        """
        self.show_action_feedback(action, FeedbackType.INFO, details)

    def show_processing(self, action: str, details: Optional[str] = None) -> None:
        """
        Show processing feedback.

        Args:
            action: Action description
            details: Optional processing details
        """
        self.show_action_feedback(action, FeedbackType.PROCESSING, details, duration=1.5)


class ActionIndicator:
    """
    Action indicator for showing progress/status.

    Provides visual indicators for ongoing actions.
    """

    # Spinner frames for processing animations
    SPINNER_FRAMES = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]

    def __init__(self, app: App):
        """
        Initialize action indicator.

        Args:
            app: Application instance
        """
        self.app = app
        self.current_frame = 0

    def get_next_spinner_frame(self) -> str:
        """
        Get next spinner animation frame.

        Returns:
            str: Next spinner character
        """
        frame = self.SPINNER_FRAMES[self.current_frame]
        self.current_frame = (self.current_frame + 1) % len(self.SPINNER_FRAMES)
        return frame

    def show_progress(self, action: str, percentage: Optional[int] = None) -> None:
        """
        Show progress for a long-running action.

        Args:
            action: Action description
            percentage: Optional percentage (0-100)
        """
        spinner = self.get_next_spinner_frame()

        if percentage is not None:
            message = f"{spinner} {action} ({percentage}%)"
        else:
            message = f"{spinner} {action}..."

        # Update status bar or show notification
        try:
            from .widgets.status_bar import StatusBar
            status_bar = self.app.query_one(StatusBar)
            # Could update status bar with progress message
        except:
            pass


class FeedbackIcons:
    """
    Icon library for visual feedback.

    Provides consistent icons across the application.
    """

    # Mode icons
    MODE_NORMAL = "⌘"
    MODE_INSERT = "✏️"
    MODE_VISUAL = "📋"
    MODE_FOCUS = "🎯"

    # Action icons
    SESSION_NEW = "➕"
    SESSION_CLOSE = "✖"
    SESSION_SAVE = "💾"
    SESSION_LOAD = "📂"

    # Status icons
    STATUS_ACTIVE = "●"
    STATUS_INACTIVE = "○"
    STATUS_PROCESSING = "⟳"
    STATUS_SUCCESS = "✓"
    STATUS_ERROR = "✗"
    STATUS_WARNING = "⚠"
    STATUS_INFO = "ℹ"

    # Workspace icons
    WORKSPACE_ACTIVE = "◆"
    WORKSPACE_INACTIVE = "◇"

    # Feature icons
    THEME = "🎨"
    HELP = "❓"
    BROADCAST = "📡"
    SEARCH = "🔍"
    HISTORY = "📜"
    SETTINGS = "⚙"

    # Notification icons
    BELL = "🔔"
    ALERT = "⚠️"
    CHECK = "✅"
    CROSS = "❌"

    @staticmethod
    def mode_icon(mode: str) -> str:
        """
        Get icon for mode.

        Args:
            mode: Mode name

        Returns:
            str: Mode icon
        """
        icons = {
            "normal": FeedbackIcons.MODE_NORMAL,
            "insert": FeedbackIcons.MODE_INSERT,
            "visual": FeedbackIcons.MODE_VISUAL,
            "copy": FeedbackIcons.MODE_VISUAL,
            "focus": FeedbackIcons.MODE_FOCUS,
        }
        return icons.get(mode.lower(), FeedbackIcons.MODE_NORMAL)

    @staticmethod
    def status_icon(status: str) -> str:
        """
        Get icon for status.

        Args:
            status: Status name

        Returns:
            str: Status icon
        """
        icons = {
            "active": FeedbackIcons.STATUS_ACTIVE,
            "inactive": FeedbackIcons.STATUS_INACTIVE,
            "processing": FeedbackIcons.STATUS_PROCESSING,
            "success": FeedbackIcons.STATUS_SUCCESS,
            "error": FeedbackIcons.STATUS_ERROR,
            "warning": FeedbackIcons.STATUS_WARNING,
            "info": FeedbackIcons.STATUS_INFO,
        }
        return icons.get(status.lower(), FeedbackIcons.STATUS_INFO)


class FeedbackMessages:
    """
    Predefined feedback messages for common actions.

    Provides consistent messaging across the application.
    """

    # Session actions
    SESSION_CREATED = "Session created"
    SESSION_CLOSED = "Session closed"
    SESSION_SAVED = "Session saved"
    SESSION_LOADED = "Session loaded"
    SESSION_RENAMED = "Session renamed"

    # Workspace actions
    WORKSPACE_SWITCHED = "Workspace switched"
    WORKSPACE_SAVED = "Workspace saved"
    WORKSPACE_LOADED = "Workspace loaded"

    # Mode transitions
    MODE_CHANGED = "Mode changed"
    FOCUS_ENABLED = "Focus mode enabled"
    FOCUS_DISABLED = "Focus mode disabled"

    # Clipboard actions
    TEXT_COPIED = "Text copied to clipboard"
    COPY_FAILED = "Failed to copy text"

    # Theme actions
    THEME_CHANGED = "Theme changed"
    THEME_SAVED = "Theme saved"

    # Error messages
    NO_SESSION = "No active session"
    INVALID_INPUT = "Invalid input"
    OPERATION_FAILED = "Operation failed"
    NOT_FOUND = "Not found"

    @staticmethod
    def session_action(action: str, session_name: Optional[str] = None) -> str:
        """
        Format session action message.

        Args:
            action: Action performed
            session_name: Optional session name

        Returns:
            str: Formatted message
        """
        if session_name:
            return f"{action}: {session_name}"
        return action

    @staticmethod
    def workspace_action(action: str, workspace_num: int) -> str:
        """
        Format workspace action message.

        Args:
            action: Action performed
            workspace_num: Workspace number

        Returns:
            str: Formatted message
        """
        return f"{action} to workspace {workspace_num}"

    @staticmethod
    def mode_action(old_mode: str, new_mode: str) -> str:
        """
        Format mode transition message.

        Args:
            old_mode: Previous mode
            new_mode: New mode

        Returns:
            str: Formatted message
        """
        return f"Mode: {old_mode.upper()} → {new_mode.upper()}"


# Convenience instance for easy access
feedback_icons = FeedbackIcons()
feedback_messages = FeedbackMessages()
