"""
Entry point for Claude Multi-Terminal application.

This module provides the main entry point when running the package via:
    python -m claude_multi_terminal

It handles application initialization, environment validation, and graceful
error handling for startup failures.
"""

import sys
import os
import argparse
import shutil
from pathlib import Path

from .config import Config

__version__ = "0.1.0"


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


def parse_arguments() -> argparse.Namespace:
    """
    Parse command-line arguments.

    Returns:
        argparse.Namespace: Parsed arguments
    """
    parser = argparse.ArgumentParser(
        prog="multi-term",
        description="Multi-session terminal UI for Claude with vim-style window management",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  multi-term                    # Normal launch
  multi-term --tutorial        # First-time interactive tutorial
  multi-term --version         # Show version
  multi-term --check           # Validate environment

For more information: https://github.com/wallon-qodo/multi-term
        """,
    )

    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {__version__}",
    )

    parser.add_argument(
        "--tutorial",
        action="store_true",
        help="Launch first-time interactive tutorial (2 minutes)",
    )

    parser.add_argument(
        "--check",
        action="store_true",
        help="Validate environment and exit (useful for CI/CD)",
    )

    parser.add_argument(
        "--no-mouse",
        action="store_true",
        help="Disable mouse support (enables terminal text selection)",
    )

    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug mode with verbose logging",
    )

    return parser.parse_args()


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
        # Parse command-line arguments
        args = parse_arguments()

        # Validate environment
        is_valid, error_msg = validate_environment()
        if not is_valid:
            print(f"Error: {error_msg}", file=sys.stderr)
            sys.exit(1)

        # Handle --check flag
        if args.check:
            print("✓ Environment validation passed")
            print(f"✓ Claude CLI: {Config.detect_claude_path()}")
            print(f"✓ Config directory: {Config.get_config_dir()}")
            print(f"✓ Sessions directory: {Config().storage_dir}")
            sys.exit(0)

        # Initialize configuration
        try:
            config = Config()
            config.ensure_storage_dir()
        except Exception as e:
            print(f"Configuration error: {e}", file=sys.stderr)
            sys.exit(2)

        # Import app here to avoid module loading warning
        from .app import ClaudeMultiTerminalApp

        # Create app
        app = ClaudeMultiTerminalApp()

        # Set tutorial mode if requested
        if args.tutorial:
            app.tutorial_mode = True

        # Set debug mode if requested
        if args.debug:
            # TODO: Enable debug logging
            pass

        try:
            # Run with mouse support (can be disabled with --no-mouse)
            app.run(mouse=not args.no_mouse)
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
