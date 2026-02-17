"""Type definitions for the multi-terminal application."""

from enum import Enum


class AppMode(Enum):
    """Application mode enum for modal key handling."""

    NORMAL = "normal"      # Default mode: window management, navigation
    INSERT = "insert"      # Insert mode: all keys forwarded to active session
    COPY = "copy"         # Copy mode: scrollback navigation, text selection
    COMMAND = "command"    # Command mode: prefix key mode (Ctrl+B then action)
