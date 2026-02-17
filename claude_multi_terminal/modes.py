"""
Modal System Types for Claude Multi-Terminal - TUIOS-Style Modal Interaction.

This module implements a Vim-inspired modal interaction system that provides distinct
operational modes for terminal management. The modal system enables efficient keyboard-driven
workflows by separating different types of user actions into isolated contexts.

TUIOS Modal Philosophy:
----------------------
Text User Interface Operating System (TUIOS) design principles applied:
- Clear visual feedback for current mode state
- Predictable mode transitions with explicit entry/exit conditions
- Modal state isolation prevents accidental actions
- Keyboard-first design optimized for power users

Modal Hierarchy:
---------------
NORMAL → Default state, navigation and commands
   ↓
INSERT → Text input and terminal interaction
   ↓
COPY   → Selection and clipboard operations
   ↓
COMMAND → System commands and configuration

Each mode has distinct visual styling, keybindings, and behavioral contexts.

Architecture:
------------
- AppMode: Enum defining available operational modes
- ModeConfig: Configuration dataclass for mode metadata
- ModeHandler: Protocol defining mode-specific behavior handlers
- ModeTransition: Validation logic for legal mode transitions
- ModeState: Tracks current mode and transition history

Author: Claude Code Team
License: MIT
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Protocol, Optional, Callable, Any
from datetime import datetime

from .theme import theme, icons


class AppMode(Enum):
    """
    Application operational modes for TUIOS-style modal interaction.

    Each mode represents a distinct operational context with specific keybindings,
    visual feedback, and behavioral characteristics optimized for particular tasks.

    Attributes:
        NORMAL: Default navigation and command mode
        INSERT: Text input and terminal interaction mode
        COPY: Selection and clipboard operations mode
        COMMAND: System commands and configuration mode
    """

    NORMAL = auto()    # Navigation, pane management, focus control
    INSERT = auto()    # Terminal input, text editing
    COPY = auto()      # Text selection, clipboard operations
    COMMAND = auto()   # System commands, configuration, keybindings

    def __str__(self) -> str:
        """Return human-readable mode name."""
        return self.name

    def __repr__(self) -> str:
        """Return detailed mode representation."""
        return f"AppMode.{self.name}"


@dataclass(frozen=True)
class ModeConfig:
    """
    Configuration metadata for an application mode.

    Defines the visual appearance, behavior characteristics, and metadata
    for a specific operational mode. Immutable to ensure mode consistency.

    Attributes:
        mode: The AppMode this configuration applies to
        display_name: Human-readable name shown in UI
        color: RGB color string for status bar and visual indicators
        icon: Unicode character representing the mode
        description: Detailed explanation of mode purpose
        entry_conditions: Requirements that must be met to enter this mode
        exit_keys: Default keybindings to exit this mode
        cursor_style: Terminal cursor appearance in this mode
    """

    mode: AppMode
    display_name: str
    color: str  # RGB color string compatible with Textual
    icon: str  # Unicode icon from theme.icons
    description: str
    entry_conditions: str = ""
    exit_keys: list[str] = field(default_factory=lambda: ["escape"])
    cursor_style: str = "block"  # block, underline, bar

    def __post_init__(self) -> None:
        """Validate mode configuration consistency."""
        if not self.display_name:
            raise ValueError(f"Mode {self.mode} must have display_name")
        if not self.color:
            raise ValueError(f"Mode {self.mode} must have color")
        if not self.icon:
            raise ValueError(f"Mode {self.mode} must have icon")


# Mode Configuration Registry
# Maps each AppMode to its visual and behavioral configuration
MODE_CONFIGS: dict[AppMode, ModeConfig] = {
    AppMode.NORMAL: ModeConfig(
        mode=AppMode.NORMAL,
        display_name="NORMAL",
        color=theme.ANSI_BLUE,  # Blue for navigation/command mode
        icon=icons.KEYBOARD,
        description=(
            "Default navigation and command mode. Navigate between panes, "
            "manage layout, execute commands. Press 'i' to enter INSERT mode, "
            "'c' for COPY mode, ':' for COMMAND mode."
        ),
        entry_conditions="Application start or ESC from any mode",
        exit_keys=["i", "c", "colon"],  # Enter other modes
        cursor_style="block",
    ),

    AppMode.INSERT: ModeConfig(
        mode=AppMode.INSERT,
        display_name="INSERT",
        color=theme.ANSI_GREEN,  # Green for active input
        icon=icons.EDIT,
        description=(
            "Terminal input and text editing mode. Interact directly with "
            "terminal sessions, type commands, edit text. Press ESC to "
            "return to NORMAL mode."
        ),
        entry_conditions="Press 'i' in NORMAL mode or focus terminal pane",
        exit_keys=["escape"],
        cursor_style="bar",  # Vertical bar for insertion point
    ),

    AppMode.COPY: ModeConfig(
        mode=AppMode.COPY,
        display_name="COPY",
        color=theme.ACCENT_WARNING,  # Yellow/orange for selection
        icon=icons.CLIPBOARD,
        description=(
            "Visual selection and clipboard operations mode. Select text, "
            "copy to clipboard, manipulate selections. Use hjkl or arrows "
            "to extend selection. Press 'y' to yank (copy), ESC to exit."
        ),
        entry_conditions="Press 'c' in NORMAL mode or 'v' for visual select",
        exit_keys=["escape", "y"],  # y = yank (copy) and exit
        cursor_style="underline",  # Underline for selection cursor
    ),

    AppMode.COMMAND: ModeConfig(
        mode=AppMode.COMMAND,
        display_name="COMMAND",
        color=theme.ACCENT_PRIMARY,  # Coral red for system commands
        icon=icons.COMMAND,
        description=(
            "System command and configuration mode. Execute system commands, "
            "adjust settings, manage sessions, configure keybindings. "
            "Type command and press Enter, or ESC to cancel."
        ),
        entry_conditions="Press ':' in NORMAL mode",
        exit_keys=["escape", "enter"],  # Enter executes, ESC cancels
        cursor_style="block",
    ),
}


class ModeHandler(Protocol):
    """
    Protocol defining the interface for mode-specific behavior handlers.

    Each mode can have a handler that implements custom behavior for
    key events, focus changes, and lifecycle events. Handlers enable
    mode-specific logic without coupling the mode system to application details.

    Methods:
        on_enter: Called when mode is activated
        on_exit: Called when mode is deactivated
        on_key: Handle key press in this mode
        on_focus_change: Handle focus change while in this mode
        can_transition_to: Validate if transition to another mode is allowed
    """

    def on_enter(self, previous_mode: Optional[AppMode]) -> None:
        """
        Called when entering this mode.

        Args:
            previous_mode: The mode we're transitioning from, or None if app start
        """
        ...

    def on_exit(self, next_mode: AppMode) -> bool:
        """
        Called when exiting this mode.

        Args:
            next_mode: The mode we're transitioning to

        Returns:
            True to allow transition, False to block it
        """
        ...

    def on_key(self, key: str) -> bool:
        """
        Handle key press in this mode.

        Args:
            key: The key that was pressed

        Returns:
            True if key was handled, False to propagate to default handlers
        """
        ...

    def on_focus_change(self, has_focus: bool) -> None:
        """
        Handle focus change while in this mode.

        Args:
            has_focus: True if gained focus, False if lost focus
        """
        ...

    def can_transition_to(self, target_mode: AppMode) -> tuple[bool, str]:
        """
        Validate if transition to target mode is allowed.

        Args:
            target_mode: The mode to transition to

        Returns:
            Tuple of (allowed, reason). If not allowed, reason explains why.
        """
        ...


@dataclass
class ModeTransition:
    """
    Represents a mode transition with timestamp and validation.

    Tracks historical mode changes for debugging, analytics, and
    implementing features like "previous mode" navigation.

    Attributes:
        from_mode: Starting mode (None if app initialization)
        to_mode: Target mode
        timestamp: When transition occurred
        trigger: What caused the transition (key, command, etc)
        allowed: Whether transition was permitted
        reason: Explanation if transition was blocked
    """

    from_mode: Optional[AppMode]
    to_mode: AppMode
    timestamp: datetime = field(default_factory=datetime.now)
    trigger: str = "unknown"
    allowed: bool = True
    reason: str = ""

    def __str__(self) -> str:
        """Return human-readable transition description."""
        from_str = self.from_mode.name if self.from_mode else "START"
        status = "✓" if self.allowed else "✗"
        return f"[{status}] {from_str} → {self.to_mode.name} ({self.trigger})"


class ModeState:
    """
    Tracks current mode state and manages mode transitions.

    Central state management for the modal system. Handles transition
    validation, mode history, and coordination with mode handlers.

    Attributes:
        current_mode: Currently active mode
        previous_mode: Most recent previous mode for quick toggle
        handlers: Registry of mode-specific behavior handlers
        history: Chronological list of mode transitions
        max_history: Maximum transitions to retain in history
    """

    def __init__(
        self,
        initial_mode: AppMode = AppMode.NORMAL,
        max_history: int = 100
    ) -> None:
        """
        Initialize mode state tracking.

        Args:
            initial_mode: Starting mode (default: NORMAL)
            max_history: Maximum transition history entries to retain
        """
        self.current_mode = initial_mode
        self.previous_mode: Optional[AppMode] = None
        self.handlers: dict[AppMode, ModeHandler] = {}
        self.history: list[ModeTransition] = []
        self.max_history = max_history

        # Record initial state
        self.history.append(
            ModeTransition(
                from_mode=None,
                to_mode=initial_mode,
                trigger="initialization",
                allowed=True
            )
        )

    def register_handler(self, mode: AppMode, handler: ModeHandler) -> None:
        """
        Register a behavior handler for a specific mode.

        Args:
            mode: The mode to handle
            handler: Handler implementation
        """
        self.handlers[mode] = handler

    def unregister_handler(self, mode: AppMode) -> None:
        """
        Remove behavior handler for a mode.

        Args:
            mode: The mode to stop handling
        """
        self.handlers.pop(mode, None)

    def can_transition_to(self, target_mode: AppMode) -> tuple[bool, str]:
        """
        Check if transition to target mode is allowed.

        Consults current mode's handler if available, otherwise allows
        all transitions (permissive by default).

        Args:
            target_mode: Mode to transition to

        Returns:
            Tuple of (allowed, reason)
        """
        if target_mode == self.current_mode:
            return False, f"Already in {target_mode.name} mode"

        current_handler = self.handlers.get(self.current_mode)
        if current_handler:
            return current_handler.can_transition_to(target_mode)

        # Default: allow all transitions
        return True, ""

    def transition_to(
        self,
        target_mode: AppMode,
        trigger: str = "manual"
    ) -> bool:
        """
        Attempt to transition to target mode.

        Validates transition, calls lifecycle handlers, updates state,
        and records transition in history.

        Args:
            target_mode: Mode to transition to
            trigger: What caused this transition (for logging)

        Returns:
            True if transition succeeded, False if blocked
        """
        # Validate transition
        allowed, reason = self.can_transition_to(target_mode)

        if not allowed:
            # Record blocked transition
            self.history.append(
                ModeTransition(
                    from_mode=self.current_mode,
                    to_mode=target_mode,
                    trigger=trigger,
                    allowed=False,
                    reason=reason
                )
            )
            self._trim_history()
            return False

        # Call current mode's exit handler
        current_handler = self.handlers.get(self.current_mode)
        if current_handler:
            if not current_handler.on_exit(target_mode):
                # Handler blocked transition
                self.history.append(
                    ModeTransition(
                        from_mode=self.current_mode,
                        to_mode=target_mode,
                        trigger=trigger,
                        allowed=False,
                        reason="Blocked by exit handler"
                    )
                )
                self._trim_history()
                return False

        # Execute transition
        old_mode = self.current_mode
        self.previous_mode = old_mode
        self.current_mode = target_mode

        # Call new mode's enter handler
        target_handler = self.handlers.get(target_mode)
        if target_handler:
            target_handler.on_enter(old_mode)

        # Record successful transition
        self.history.append(
            ModeTransition(
                from_mode=old_mode,
                to_mode=target_mode,
                trigger=trigger,
                allowed=True
            )
        )
        self._trim_history()

        return True

    def toggle_previous(self) -> bool:
        """
        Toggle between current and previous mode.

        Convenience method for quickly switching between two modes.
        Common use case: toggle between NORMAL and INSERT.

        Returns:
            True if toggled, False if no previous mode
        """
        if not self.previous_mode:
            return False

        return self.transition_to(self.previous_mode, trigger="toggle")

    def get_config(self, mode: Optional[AppMode] = None) -> ModeConfig:
        """
        Get configuration for a mode.

        Args:
            mode: Mode to get config for (default: current mode)

        Returns:
            ModeConfig for the specified mode
        """
        target = mode or self.current_mode
        return MODE_CONFIGS[target]

    def get_recent_transitions(self, count: int = 10) -> list[ModeTransition]:
        """
        Get most recent mode transitions.

        Args:
            count: Number of transitions to return

        Returns:
            List of recent transitions, newest first
        """
        return list(reversed(self.history[-count:]))

    def _trim_history(self) -> None:
        """Trim history to max_history length."""
        if len(self.history) > self.max_history:
            self.history = self.history[-self.max_history:]


# Utility functions for mode management

def get_mode_color(mode: AppMode) -> str:
    """
    Get status bar color for a mode.

    Args:
        mode: Mode to get color for

    Returns:
        RGB color string
    """
    return MODE_CONFIGS[mode].color


def get_mode_icon(mode: AppMode) -> str:
    """
    Get icon for a mode.

    Args:
        mode: Mode to get icon for

    Returns:
        Unicode icon character
    """
    return MODE_CONFIGS[mode].icon


def get_mode_description(mode: AppMode) -> str:
    """
    Get detailed description of a mode.

    Args:
        mode: Mode to get description for

    Returns:
        Human-readable mode description
    """
    return MODE_CONFIGS[mode].description


def is_input_mode(mode: AppMode) -> bool:
    """
    Check if mode allows direct text input.

    Args:
        mode: Mode to check

    Returns:
        True if mode accepts text input (INSERT, COMMAND)
    """
    return mode in (AppMode.INSERT, AppMode.COMMAND)


def is_navigation_mode(mode: AppMode) -> bool:
    """
    Check if mode is for navigation/commands.

    Args:
        mode: Mode to check

    Returns:
        True if mode is for navigation (NORMAL, COPY)
    """
    return mode in (AppMode.NORMAL, AppMode.COPY)


# Default mode transition rules
# Maps (from_mode, key) -> to_mode for standard transitions
DEFAULT_MODE_TRANSITIONS: dict[tuple[AppMode, str], AppMode] = {
    # From NORMAL
    (AppMode.NORMAL, "i"): AppMode.INSERT,
    (AppMode.NORMAL, "c"): AppMode.COPY,
    (AppMode.NORMAL, "v"): AppMode.COPY,  # Vim-style visual mode
    (AppMode.NORMAL, "colon"): AppMode.COMMAND,
    (AppMode.NORMAL, ":"): AppMode.COMMAND,

    # From INSERT
    (AppMode.INSERT, "escape"): AppMode.NORMAL,

    # From COPY
    (AppMode.COPY, "escape"): AppMode.NORMAL,
    (AppMode.COPY, "y"): AppMode.NORMAL,  # Yank and exit

    # From COMMAND
    (AppMode.COMMAND, "escape"): AppMode.NORMAL,
    (AppMode.COMMAND, "enter"): AppMode.NORMAL,
}


def get_mode_transition(from_mode: AppMode, key: str) -> Optional[AppMode]:
    """
    Get target mode for a key press in current mode.

    Args:
        from_mode: Current mode
        key: Key that was pressed

    Returns:
        Target mode if transition defined, None otherwise
    """
    return DEFAULT_MODE_TRANSITIONS.get((from_mode, key))


# Export all public symbols
__all__ = [
    # Core types
    "AppMode",
    "ModeConfig",
    "ModeHandler",
    "ModeTransition",
    "ModeState",

    # Configuration
    "MODE_CONFIGS",
    "DEFAULT_MODE_TRANSITIONS",

    # Utility functions
    "get_mode_color",
    "get_mode_icon",
    "get_mode_description",
    "is_input_mode",
    "is_navigation_mode",
    "get_mode_transition",
]
