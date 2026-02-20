"""
Application configuration constants and settings.

This module provides centralized configuration management for Claude Multi-Terminal,
including path detection, storage management, and application constants.
"""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional
import os
import shutil


@dataclass
class Config:
    """
    Configuration manager for Claude Multi-Terminal.

    Provides centralized access to all application settings, paths, and constants.
    Automatically detects Claude CLI location and manages storage directories.

    Attributes:
        CLAUDE_PATH: Path to the Claude CLI executable
        DEFAULT_SESSION_COUNT: Default number of sessions on startup
        MAX_SESSIONS: Maximum number of concurrent sessions allowed
        AUTO_SAVE: Enable automatic session saving
        SAVE_ON_EXIT: Save sessions when exiting
        STORAGE_DIR: Directory for session data and history

    Example:
        config = Config()
        config.ensure_storage_dir()
        print(f"Claude CLI: {config.CLAUDE_PATH}")
    """

    # Claude CLI configuration
    CLAUDE_PATH: str = field(default="")

    # Session configuration
    DEFAULT_SESSION_COUNT: int = 2
    MAX_SESSIONS: int = 9

    # Persistence configuration
    AUTO_SAVE: bool = True
    SAVE_ON_EXIT: bool = True
    STORAGE_DIR: Path = field(default_factory=lambda: Path.home() / ".multi-term")

    # PTY configuration
    PTY_ROWS: int = 24
    PTY_COLS: int = 80
    PTY_ENCODING: str = "utf-8"

    # Terminal configuration
    TERM_TYPE: str = "xterm-256color"
    COLORTERM: str = "truecolor"

    # Performance tuning
    PTY_READ_INTERVAL: float = 0.01  # 100 Hz polling rate
    UI_UPDATE_INTERVAL: float = 0.016  # ~60 FPS UI refresh

    # Theme configuration
    THEME_NAME: str = "openclaw"  # Default theme

    @staticmethod
    def get_config_dir() -> Path:
        """
        Get the configuration directory.

        Returns:
            Path: Configuration directory path (~/.claude)
        """
        return Path.home() / ".claude"

    @staticmethod
    def detect_claude_path() -> str:
        """
        Detect the Claude CLI executable path.

        Searches in the following order:
        1. CLAUDE_PATH environment variable
        2. Common installation paths (Homebrew, system)
        3. PATH environment variable

        Returns:
            str: Path to Claude CLI executable, or "claude" as fallback

        Example:
            path = Config.detect_claude_path()
            if shutil.which(path):
                print(f"Found Claude at: {path}")
        """
        # Check environment variable first
        if env_path := os.environ.get("CLAUDE_PATH"):
            if os.path.exists(env_path) and os.access(env_path, os.X_OK):
                return env_path

        # Check common installation locations
        common_paths = [
            "/opt/homebrew/bin/claude",  # Homebrew (Apple Silicon)
            "/usr/local/bin/claude",     # Homebrew (Intel) or manual install
            "/usr/bin/claude",            # System install
            Path.home() / ".local" / "bin" / "claude",  # User install
        ]

        for path in common_paths:
            path_str = str(path)
            if os.path.exists(path_str) and os.access(path_str, os.X_OK):
                return path_str

        # Check if 'claude' is in PATH
        if claude_in_path := shutil.which("claude"):
            return claude_in_path

        # Fallback to "claude" and hope it's in PATH
        return "claude"

    def ensure_storage_dir(self) -> Path:
        """
        Ensure the storage directory exists and is writable.

        Creates the storage directory and all necessary subdirectories if they
        don't exist. Validates write permissions.

        Returns:
            Path: The storage directory path

        Raises:
            PermissionError: If directory cannot be created or is not writable
            OSError: If directory creation fails for other reasons

        Example:
            config = Config()
            storage = config.ensure_storage_dir()
            session_file = storage / "session_1.json"
        """
        try:
            # Create main storage directory
            self.STORAGE_DIR.mkdir(parents=True, exist_ok=True)

            # Create subdirectories
            (self.STORAGE_DIR / "sessions").mkdir(exist_ok=True)
            (self.STORAGE_DIR / "history").mkdir(exist_ok=True)
            (self.STORAGE_DIR / "exports").mkdir(exist_ok=True)

            # Validate write permissions
            test_file = self.STORAGE_DIR / ".write_test"
            try:
                test_file.touch()
                test_file.unlink()
            except OSError as e:
                raise PermissionError(
                    f"Storage directory {self.STORAGE_DIR} is not writable"
                ) from e

            return self.STORAGE_DIR

        except OSError as e:
            raise OSError(
                f"Failed to create storage directory {self.STORAGE_DIR}: {e}"
            ) from e

    def validate(self) -> tuple[bool, list[str]]:
        """
        Validate the current configuration.

        Checks all configuration values for validity and returns any issues found.

        Returns:
            tuple[bool, list[str]]: (is_valid, list_of_issues)

        Example:
            config = Config()
            is_valid, issues = config.validate()
            if not is_valid:
                for issue in issues:
                    print(f"Config issue: {issue}")
        """
        issues = []

        # Validate Claude path
        if not shutil.which(self.CLAUDE_PATH):
            issues.append(f"Claude CLI not found at {self.CLAUDE_PATH}")

        # Validate session counts
        if self.DEFAULT_SESSION_COUNT < 1:
            issues.append("DEFAULT_SESSION_COUNT must be at least 1")
        if self.DEFAULT_SESSION_COUNT > self.MAX_SESSIONS:
            issues.append(
                f"DEFAULT_SESSION_COUNT ({self.DEFAULT_SESSION_COUNT}) "
                f"exceeds MAX_SESSIONS ({self.MAX_SESSIONS})"
            )
        if self.MAX_SESSIONS > 9:
            issues.append("MAX_SESSIONS cannot exceed 9 (UI limitation)")

        # Validate storage directory
        if not self.STORAGE_DIR.is_absolute():
            issues.append("STORAGE_DIR must be an absolute path")

        # Validate performance settings
        if self.PTY_READ_INTERVAL <= 0:
            issues.append("PTY_READ_INTERVAL must be positive")
        if self.UI_UPDATE_INTERVAL <= 0:
            issues.append("UI_UPDATE_INTERVAL must be positive")

        return len(issues) == 0, issues

    def get_session_file(self, session_id: str) -> Path:
        """
        Get the file path for a specific session.

        Args:
            session_id: Unique session identifier

        Returns:
            Path: Full path to session file

        Example:
            config = Config()
            session_file = config.get_session_file("session_1")
        """
        return self.STORAGE_DIR / "sessions" / f"{session_id}.json"

    def get_history_file(self, session_id: str) -> Path:
        """
        Get the history file path for a specific session.

        Args:
            session_id: Unique session identifier

        Returns:
            Path: Full path to history file

        Example:
            config = Config()
            history_file = config.get_history_file("session_1")
        """
        return self.STORAGE_DIR / "history" / f"{session_id}.txt"

    def __post_init__(self) -> None:
        """Post-initialization validation and setup."""
        # Initialize CLAUDE_PATH if not set
        if not self.CLAUDE_PATH:
            self.CLAUDE_PATH = self.detect_claude_path()

        # Ensure STORAGE_DIR is a Path object
        if isinstance(self.STORAGE_DIR, str):
            self.STORAGE_DIR = Path(self.STORAGE_DIR)

        # Expand user paths
        self.STORAGE_DIR = self.STORAGE_DIR.expanduser().resolve()


# Default configuration instance
# This can be imported and used directly: from .config import config
config = Config()
