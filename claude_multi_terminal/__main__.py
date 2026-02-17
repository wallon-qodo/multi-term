"""
Entry point for Claude Multi-Terminal application.

This module provides the main entry point when running the package via:
    python -m claude_multi_terminal

It handles application initialization, environment validation, and graceful
error handling for startup failures.
"""

import sys
import os
import shutil
from pathlib import Path

from .config import Config


def validate_environment() -> tuple[bool, str]:
    """
    Validate that the environment is properly configured.

    Returns:
        tuple[bool, str]: (is_valid, error_message)
    """
    # Check for Claude CLI
    claude_path = Config.detect_claude_path()
    if not claude_path:
        return False, (
            "Claude CLI not found. Please install Claude Code or set CLAUDE_PATH.\n"
            "Installation: https://claude.ai/download\n"
            "Or set environment variable: export CLAUDE_PATH=/path/to/claude"
        )

    # Validate Claude CLI is executable
    if not os.access(claude_path, os.X_OK):
        return False, f"Claude CLI at {claude_path} is not executable"

    return True, ""


def main() -> None:
    """
    Main entry point for the Claude Multi-Terminal application.

    Validates the environment, initializes configuration, and launches the TUI.
    Handles all startup errors gracefully with informative error messages.

    Exit codes:
        0: Normal exit
        1: Environment validation failed
        2: Configuration error
        3: Fatal runtime error
    """
    try:
        # Validate environment
        is_valid, error_msg = validate_environment()
        if not is_valid:
            print(f"Error: {error_msg}", file=sys.stderr)
            sys.exit(1)

        # Initialize configuration
        try:
            config = Config()
            config.ensure_storage_dir()
        except Exception as e:
            print(f"Configuration error: {e}", file=sys.stderr)
            sys.exit(2)

        # Import app here to avoid module loading warning
        from .app import ClaudeMultiTerminalApp

        # Create and run app
        app = ClaudeMultiTerminalApp()

        try:
            # Run with mouse support enabled by default
            # Users can disable in settings if they need text selection
            app.run(mouse=True)
        except KeyboardInterrupt:
            print("\nShutting down gracefully...")
        except Exception as e:
            print(f"Fatal runtime error: {e}", file=sys.stderr)
            import traceback
            traceback.print_exc()
            sys.exit(3)

    except Exception as e:
        # Catch-all for unexpected errors during initialization
        print(f"Unexpected error during startup: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(3)


if __name__ == "__main__":
    main()
