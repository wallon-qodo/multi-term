"""Footer hints widget displaying contextual keyboard shortcuts."""

from textual.widgets import Static
from textual.reactive import reactive
from rich.text import Text
from typing import List, Tuple

from ..types import AppMode


class FooterHints(Static):
    """
    Display contextual keyboard hints at the bottom of the screen.

    Shows 3-7 most relevant shortcuts for the current mode in a compact,
    non-intrusive format. Updates automatically when mode changes.

    Design follows TUIOS minimalist principles with HomebrewTheme coral-red accents.
    """

    DEFAULT_CSS = """
    FooterHints {
        dock: bottom;
        background: rgb(24,24,24);
        color: rgb(180,180,180);
        height: 1;
        padding: 0 2;
        border-top: solid rgb(42,42,42);
    }

    FooterHints.-mode-normal {
        border-top: solid rgb(100,180,240);
    }

    FooterHints.-mode-insert {
        border-top: solid rgb(120,200,120);
    }

    FooterHints.-mode-copy {
        border-top: solid rgb(255,180,70);
    }

    FooterHints.-mode-command {
        border-top: solid rgb(255,77,77);
    }
    """

    current_mode = reactive(AppMode.NORMAL)

    def watch_current_mode(self, mode: AppMode) -> None:
        """Update styling when mode changes."""
        # Remove all mode classes
        for m in AppMode:
            self.set_class(False, f"-mode-{m.value}")
        # Add current mode class
        self.set_class(True, f"-mode-{mode.value}")
        # Refresh content
        self.refresh()

    def render(self) -> Text:
        """Render contextual hints for current mode."""
        hints = self.get_hints_for_mode(self.current_mode)
        return self._format_hints(hints)

    def get_hints_for_mode(self, mode: AppMode) -> List[Tuple[str, str, str]]:
        """
        Get contextual hints for the specified mode.

        Args:
            mode: Application mode to get hints for

        Returns:
            List of (key, action, color) tuples for display
        """
        if mode == AppMode.NORMAL:
            return [
                ("?", "Help", "rgb(255,77,77)"),
                ("i", "Insert", "rgb(120,200,120)"),
                ("v", "Copy", "rgb(255,180,70)"),
                ("^B", "Command", "rgb(255,77,77)"),
                ("n", "New", "rgb(100,180,240)"),
                ("x", "Close", "rgb(255,77,77)"),
                ("h/j/k/l", "Navigate", "rgb(100,180,240)"),
                ("q", "Quit", "rgb(255,77,77)"),
            ]

        elif mode == AppMode.INSERT:
            return [
                ("Esc", "Normal", "rgb(100,180,240)"),
                ("Type", "Terminal input", "rgb(120,200,120)"),
                ("Enter", "Submit", "rgb(120,200,120)"),
            ]

        elif mode == AppMode.COPY:
            return [
                ("Esc", "Normal", "rgb(100,180,240)"),
                ("j/k", "Scroll", "rgb(255,180,70)"),
                ("/", "Search", "rgb(255,180,70)"),
                ("v", "Visual", "rgb(255,180,70)"),
                ("y", "Yank", "rgb(120,200,120)"),
                ("g/G", "Top/Bottom", "rgb(255,180,70)"),
            ]

        elif mode == AppMode.COMMAND:
            return [
                ("Esc", "Cancel", "rgb(100,180,240)"),
                ("h/v", "Split", "rgb(255,77,77)"),
                ("l/s/t", "Layout", "rgb(255,77,77)"),
                ("n/p", "Next/Prev", "rgb(100,180,240)"),
                ("?", "Help", "rgb(255,77,77)"),
            ]

        # Fallback
        return [
            ("?", "Help", "rgb(255,77,77)"),
            ("Esc", "Normal", "rgb(100,180,240)"),
        ]

    def _format_hints(self, hints: List[Tuple[str, str, str]]) -> Text:
        """
        Format hints as rich text with separators.

        Args:
            hints: List of (key, action, color) tuples

        Returns:
            Formatted Rich Text object
        """
        text = Text()

        # Mode indicator
        mode_icons = {
            AppMode.NORMAL: "●",
            AppMode.INSERT: "▸",
            AppMode.COPY: "◆",
            AppMode.COMMAND: "⬢",
        }

        mode_colors = {
            AppMode.NORMAL: "rgb(100,180,240)",
            AppMode.INSERT: "rgb(120,200,120)",
            AppMode.COPY: "rgb(255,180,70)",
            AppMode.COMMAND: "rgb(255,77,77)",
        }

        icon = mode_icons.get(self.current_mode, "●")
        color = mode_colors.get(self.current_mode, "rgb(180,180,180)")

        text.append(icon, style=f"bold {color}")
        text.append(" ", style="")

        # Render hints
        for i, (key, action, hint_color) in enumerate(hints):
            if i > 0:
                text.append(" │ ", style="rgb(60,60,60)")

            text.append(key, style=f"bold {hint_color}")
            text.append(":", style="rgb(120,120,120)")
            text.append(action, style="rgb(180,180,180)")

        return text

    def get_contextual_tip(self, context: str) -> str:
        """
        Get a contextual tip message for specific situations.

        Args:
            context: Context identifier (e.g., "empty_workspace", "single_pane")

        Returns:
            Tip message string or empty string if no tip for context
        """
        tips = {
            "empty_workspace": "Press 'n' to create a new session",
            "single_pane": "Press Ctrl+B then h/v to split",
            "multiple_panes": "Press h/j/k/l to navigate between panes",
            "first_launch": "Welcome! Press ? for help",
            "broadcast_active": "Broadcast mode: Input sent to all sessions",
            "focus_mode": "Press F11 or Ctrl+F to exit focus mode",
        }

        return tips.get(context, "")
