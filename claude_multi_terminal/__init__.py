"""
Claude Multi-Terminal - Multi-pane terminal UI for Claude Code CLI.

A sophisticated terminal multiplexer designed specifically for the Claude Code CLI,
providing multiple concurrent sessions in a resizable grid layout with advanced
features like session persistence, drag-and-drop reordering, and intelligent focus
management.

Key Features:
    - Multiple concurrent Claude sessions in a single window
    - Resizable grid layout with drag-to-resize functionality
    - Session persistence and restoration
    - Focus mode for distraction-free coding
    - Advanced keyboard navigation and shortcuts
    - Real-time session status indicators
    - Conversation history and search

Usage:
    python -m claude_multi_terminal

    Or after installation:
    multi-term

Author: Claude Code Team
License: MIT
"""

from .app import ClaudeMultiTerminalApp

__version__ = "0.1.0"
__all__ = ["ClaudeMultiTerminalApp"]
