"""Help overlay system displaying contextual keyboard shortcuts and commands."""

from dataclasses import dataclass
from enum import Enum
from typing import Optional
from textual.screen import ModalScreen
from textual.widgets import Static, Label
from textual.containers import Vertical, ScrollableContainer
from textual.app import ComposeResult
from textual.binding import Binding
from rich.table import Table
from rich.text import Text

from ..types import AppMode
from ..theme import theme, boxes


class HelpCategory(Enum):
    """Categories for organizing help entries."""

    GENERAL = "general"
    MODAL = "modal"
    WORKSPACE = "workspace"
    LAYOUT = "layout"
    SESSION = "session"
    COPY_MODE = "copy_mode"
    ADVANCED = "advanced"


@dataclass
class HelpEntry:
    """Single help entry for a keyboard shortcut or command."""

    key: str
    description: str
    category: HelpCategory
    mode: Optional[AppMode] = None
    example: Optional[str] = None


class HelpOverlay(ModalScreen[None]):
    """
    Full-screen help overlay displaying keyboard shortcuts and commands.

    Features:
    - Mode-aware filtering (shows relevant shortcuts for current mode)
    - Category-based organization
    - Scrollable content with keyboard navigation
    - TUIOS minimalist design with HomebrewTheme coral-red palette
    """

    BINDINGS = [
        Binding("escape,question_mark", "dismiss", "Close", priority=True),
        Binding("j,down", "scroll_down", "Scroll Down", show=False),
        Binding("k,up", "scroll_up", "Scroll Up", show=False),
        Binding("tab", "next_category", "Next Category", show=False),
        Binding("shift+tab", "prev_category", "Prev Category", show=False),
    ]

    DEFAULT_CSS = """
    HelpOverlay {
        align: center middle;
        background: rgba(0, 0, 0, 0.7);
    }

    HelpOverlay > Vertical {
        background: rgb(24,24,24);
        border: heavy rgb(255,77,77);
        width: 85%;
        max-width: 110;
        height: 85%;
        max-height: 40;
        padding: 0;
    }

    HelpOverlay #help-header {
        background: rgb(26,26,26);
        color: rgb(255,77,77);
        text-style: bold;
        padding: 1 2;
        border-bottom: solid rgb(255,77,77);
        height: auto;
        content-align: center middle;
    }

    HelpOverlay #help-subheader {
        background: rgb(28,28,28);
        color: rgb(180,180,180);
        padding: 0 2;
        height: auto;
        border-bottom: solid rgb(60,60,60);
    }

    HelpOverlay #help-content {
        height: 1fr;
        padding: 1 2;
        overflow-y: auto;
    }

    HelpOverlay #help-footer {
        background: rgb(26,26,26);
        color: rgb(120,120,120);
        padding: 0 2;
        height: auto;
        border-top: solid rgb(60,60,60);
        text-align: center;
    }

    HelpOverlay Static {
        color: rgb(240,240,240);
    }
    """

    def __init__(self, current_mode: AppMode = AppMode.NORMAL):
        """
        Initialize help overlay.

        Args:
            current_mode: Current application mode for filtering help entries
        """
        super().__init__()
        self.current_mode = current_mode
        self.current_category: Optional[HelpCategory] = None
        self.help_entries = self._build_help_entries()
        self.scroll_position = 0

    def compose(self) -> ComposeResult:
        """Compose the help overlay layout."""
        yield Vertical(
            Label(self._get_header_text(), id="help-header"),
            Label(self._get_subheader_text(), id="help-subheader"),
            ScrollableContainer(
                Static(id="help-content"),
                id="help-scroll"
            ),
            Label(
                "[Use j/k or ↑↓ to scroll, Tab for categories, ? or Esc to close]",
                id="help-footer"
            ),
        )

    def on_mount(self) -> None:
        """Render help content when mounted."""
        self._render_help_content()

    def _get_header_text(self) -> str:
        """Get the header text with application title."""
        return f"{boxes.DOUBLE_HORIZONTAL * 2} HELP - Claude Multi-Terminal {boxes.DOUBLE_HORIZONTAL * 2}"

    def _get_subheader_text(self) -> str:
        """Get the subheader text with current mode."""
        mode_name = self.current_mode.value.upper()
        category_text = ""
        if self.current_category:
            category_text = f" | Category: {self.current_category.value.replace('_', ' ').title()}"
        return f"Current Mode: {mode_name}{category_text}"

    def _build_help_entries(self) -> list[HelpEntry]:
        """
        Build comprehensive list of all keyboard shortcuts and commands.

        Returns:
            List of all help entries organized by category and mode
        """
        entries = []

        # GENERAL COMMANDS (Available in NORMAL mode)
        entries.extend([
            HelpEntry("i", "Enter INSERT mode (terminal input)", HelpCategory.GENERAL, AppMode.NORMAL),
            HelpEntry("v", "Enter COPY mode (scrollback navigation)", HelpCategory.GENERAL, AppMode.NORMAL),
            HelpEntry("Ctrl+B", "Enter COMMAND mode (window management)", HelpCategory.GENERAL, AppMode.NORMAL),
            HelpEntry("q", "Quit application", HelpCategory.GENERAL, AppMode.NORMAL),
            HelpEntry("?", "Show this help overlay", HelpCategory.GENERAL, AppMode.NORMAL),
            HelpEntry("Ctrl+Q", "Force quit application", HelpCategory.GENERAL, AppMode.NORMAL),
        ])

        # MODAL KEYBINDINGS
        entries.extend([
            HelpEntry("Esc", "Return to NORMAL mode from any mode", HelpCategory.MODAL, mode=None),
            HelpEntry("i", "INSERT mode: All keys forwarded to terminal", HelpCategory.MODAL, AppMode.INSERT,
                     "Type commands directly in terminal"),
            HelpEntry("v", "COPY mode: Navigate scrollback buffer", HelpCategory.MODAL, AppMode.COPY,
                     "View and copy terminal history"),
            HelpEntry("Ctrl+B", "COMMAND mode: Prefix for layout operations", HelpCategory.MODAL, AppMode.COMMAND,
                     "Press Ctrl+B then another key"),
        ])

        # WORKSPACE MANAGEMENT (1-9 keys)
        entries.extend([
            HelpEntry("1-9", "Switch to workspace N (1 through 9)", HelpCategory.WORKSPACE, AppMode.NORMAL,
                     "Press number key to switch"),
            HelpEntry("Shift+1-9", "Move active session to workspace N", HelpCategory.WORKSPACE, AppMode.NORMAL,
                     "Hold Shift + number key"),
            HelpEntry("F10", "Open workspace manager (full interface)", HelpCategory.WORKSPACE, AppMode.NORMAL),
            HelpEntry("Ctrl+S", "Save all workspace sessions", HelpCategory.WORKSPACE, AppMode.NORMAL),
            HelpEntry("Ctrl+L", "Load saved workspace sessions", HelpCategory.WORKSPACE, AppMode.NORMAL),
        ])

        # SESSION MANAGEMENT
        entries.extend([
            HelpEntry("Ctrl+N", "Create new session in active workspace", HelpCategory.SESSION, AppMode.NORMAL),
            HelpEntry("Ctrl+W", "Close active session", HelpCategory.SESSION, AppMode.NORMAL),
            HelpEntry("x", "Close active session (alternative)", HelpCategory.SESSION, AppMode.NORMAL),
            HelpEntry("Ctrl+R", "Rename active session", HelpCategory.SESSION, AppMode.NORMAL),
            HelpEntry("r", "Rename active session (alternative)", HelpCategory.SESSION, AppMode.NORMAL),
            HelpEntry("Ctrl+Shift+T", "Reopen last closed session", HelpCategory.SESSION, AppMode.NORMAL),
            HelpEntry("Ctrl+H", "Open session history browser", HelpCategory.SESSION, AppMode.NORMAL),
            HelpEntry("F9", "Open session history browser (alternative)", HelpCategory.SESSION, AppMode.NORMAL),
        ])

        # NAVIGATION
        entries.extend([
            HelpEntry("h", "Navigate to left pane", HelpCategory.LAYOUT, AppMode.NORMAL),
            HelpEntry("j", "Navigate to pane below", HelpCategory.LAYOUT, AppMode.NORMAL),
            HelpEntry("k", "Navigate to pane above", HelpCategory.LAYOUT, AppMode.NORMAL),
            HelpEntry("l", "Navigate to right pane", HelpCategory.LAYOUT, AppMode.NORMAL),
            HelpEntry("n", "Next pane (cycle forward)", HelpCategory.LAYOUT, AppMode.NORMAL),
            HelpEntry("p", "Previous pane (cycle backward)", HelpCategory.LAYOUT, AppMode.NORMAL),
            HelpEntry("Tab", "Next pane (alternative)", HelpCategory.LAYOUT, AppMode.NORMAL),
            HelpEntry("Shift+Tab", "Previous pane (alternative)", HelpCategory.LAYOUT, AppMode.NORMAL),
        ])

        # BSP LAYOUT OPERATIONS (Ctrl+B prefix)
        entries.extend([
            HelpEntry("Ctrl+B h", "Split current pane horizontally", HelpCategory.LAYOUT, AppMode.COMMAND,
                     "Creates new pane beside current"),
            HelpEntry("Ctrl+B v", "Split current pane vertically", HelpCategory.LAYOUT, AppMode.COMMAND,
                     "Creates new pane below current"),
            HelpEntry("Ctrl+B r", "Rotate split orientation", HelpCategory.LAYOUT, AppMode.COMMAND,
                     "Toggle horizontal/vertical split"),
            HelpEntry("Ctrl+B =", "Equalize all split sizes", HelpCategory.LAYOUT, AppMode.COMMAND,
                     "Reset all panes to equal size"),
            HelpEntry("Ctrl+B [", "Increase left/top pane size", HelpCategory.LAYOUT, AppMode.COMMAND),
            HelpEntry("Ctrl+B ]", "Increase right/bottom pane size", HelpCategory.LAYOUT, AppMode.COMMAND),
            HelpEntry("Ctrl+B l", "Switch to BSP layout mode", HelpCategory.LAYOUT, AppMode.COMMAND),
            HelpEntry("Ctrl+B s", "Switch to Stack layout mode", HelpCategory.LAYOUT, AppMode.COMMAND),
            HelpEntry("Ctrl+B t", "Switch to Tab layout mode", HelpCategory.LAYOUT, AppMode.COMMAND),
            HelpEntry("Ctrl+B n", "Next session in layout", HelpCategory.LAYOUT, AppMode.COMMAND),
            HelpEntry("Ctrl+B p", "Previous session in layout", HelpCategory.LAYOUT, AppMode.COMMAND),
            HelpEntry("Ctrl+B ?", "Show help overlay", HelpCategory.LAYOUT, AppMode.COMMAND),
        ])

        # COPY MODE OPERATIONS
        entries.extend([
            HelpEntry("j / ↓", "Move cursor down", HelpCategory.COPY_MODE, AppMode.COPY),
            HelpEntry("k / ↑", "Move cursor up", HelpCategory.COPY_MODE, AppMode.COPY),
            HelpEntry("h / ←", "Move cursor left", HelpCategory.COPY_MODE, AppMode.COPY),
            HelpEntry("l / →", "Move cursor right", HelpCategory.COPY_MODE, AppMode.COPY),
            HelpEntry("w", "Move forward one word", HelpCategory.COPY_MODE, AppMode.COPY),
            HelpEntry("b", "Move backward one word", HelpCategory.COPY_MODE, AppMode.COPY),
            HelpEntry("0", "Move to start of line", HelpCategory.COPY_MODE, AppMode.COPY),
            HelpEntry("$", "Move to end of line", HelpCategory.COPY_MODE, AppMode.COPY),
            HelpEntry("g", "Go to top of buffer", HelpCategory.COPY_MODE, AppMode.COPY),
            HelpEntry("G", "Go to bottom of buffer", HelpCategory.COPY_MODE, AppMode.COPY),
            HelpEntry("/", "Search forward in buffer", HelpCategory.COPY_MODE, AppMode.COPY),
            HelpEntry("?", "Search backward in buffer", HelpCategory.COPY_MODE, AppMode.COPY),
            HelpEntry("n", "Next search match", HelpCategory.COPY_MODE, AppMode.COPY),
            HelpEntry("N", "Previous search match", HelpCategory.COPY_MODE, AppMode.COPY),
            HelpEntry("v", "Start visual selection", HelpCategory.COPY_MODE, AppMode.COPY),
            HelpEntry("y", "Yank (copy) selection to clipboard", HelpCategory.COPY_MODE, AppMode.COPY),
            HelpEntry("Esc", "Exit COPY mode, return to NORMAL", HelpCategory.COPY_MODE, AppMode.COPY),
        ])

        # ADVANCED FEATURES
        entries.extend([
            HelpEntry("Ctrl+B", "Toggle broadcast mode", HelpCategory.ADVANCED, AppMode.NORMAL,
                     "Send input to all sessions"),
            HelpEntry("Ctrl+F", "Toggle focus mode", HelpCategory.ADVANCED, AppMode.NORMAL,
                     "Maximize active pane"),
            HelpEntry("F11", "Toggle focus mode (alternative)", HelpCategory.ADVANCED, AppMode.NORMAL),
            HelpEntry("Ctrl+Shift+F", "Toggle search panel", HelpCategory.ADVANCED, AppMode.NORMAL,
                     "Search within session output"),
            HelpEntry("Ctrl+C", "Copy visible output", HelpCategory.ADVANCED, AppMode.NORMAL,
                     "Copy all visible terminal text"),
            HelpEntry("F2", "Toggle mouse mode", HelpCategory.ADVANCED, AppMode.NORMAL,
                     "Enable/disable mouse interaction"),
        ])

        return entries

    def filter_by_mode(self, mode: AppMode) -> list[HelpEntry]:
        """
        Filter help entries by application mode.

        Args:
            mode: Application mode to filter by

        Returns:
            List of help entries relevant to the specified mode
        """
        return [
            entry for entry in self.help_entries
            if entry.mode is None or entry.mode == mode
        ]

    def filter_by_category(self, category: HelpCategory) -> list[HelpEntry]:
        """
        Filter help entries by category.

        Args:
            category: Category to filter by

        Returns:
            List of help entries in the specified category
        """
        return [
            entry for entry in self.help_entries
            if entry.category == category
        ]

    def _render_help_content(self) -> None:
        """Render the help content as a formatted table."""
        # Determine which entries to show
        if self.current_category:
            entries = self.filter_by_category(self.current_category)
        else:
            entries = self.filter_by_mode(self.current_mode)

        # Create Rich renderable content
        content_text = Text()

        # Group entries by category
        categories = {}
        for entry in entries:
            if entry.category not in categories:
                categories[entry.category] = []
            categories[entry.category].append(entry)

        # Render each category
        for idx, (category, cat_entries) in enumerate(categories.items()):
            if idx > 0:
                content_text.append("\n")

            # Category header
            category_title = category.value.replace('_', ' ').upper()
            content_text.append(f"\n{category_title}\n", style=f"bold {theme.ACCENT_PRIMARY}")
            content_text.append(boxes.SINGLE_HORIZONTAL * 60 + "\n", style=theme.ACCENT_PRIMARY)

            # Entries in this category
            for entry in cat_entries:
                # Key (bold white)
                key_width = 20
                key_text = entry.key.ljust(key_width)
                content_text.append(key_text, style=f"bold {theme.TEXT_BRIGHT}")

                # Description (normal gray)
                content_text.append(entry.description + "\n", style=theme.TEXT_SECONDARY)

                # Optional example (dimmed)
                if entry.example:
                    content_text.append(" " * key_width, style="")
                    content_text.append(f"  → {entry.example}\n", style=theme.TEXT_DIM)

        # If no entries found
        if not categories:
            content_text.append(
                f"\nNo help entries found for {self.current_mode.value.upper()} mode.\n",
                style=theme.TEXT_DIM
            )
            content_text.append(
                "Press ? or Esc to close, or Tab to browse categories.\n",
                style=theme.TEXT_DIM
            )

        # Update the content widget
        content_widget = self.query_one("#help-content", Static)
        content_widget.update(content_text)

    def action_scroll_down(self) -> None:
        """Scroll help content down."""
        container = self.query_one("#help-scroll", ScrollableContainer)
        container.scroll_down()

    def action_scroll_up(self) -> None:
        """Scroll help content up."""
        container = self.query_one("#help-scroll", ScrollableContainer)
        container.scroll_up()

    def action_next_category(self) -> None:
        """Cycle to next help category."""
        categories = list(HelpCategory)
        if self.current_category is None:
            self.current_category = categories[0]
        else:
            current_idx = categories.index(self.current_category)
            next_idx = (current_idx + 1) % len(categories)
            self.current_category = categories[next_idx]

        # Update display
        self.query_one("#help-subheader", Label).update(self._get_subheader_text())
        self._render_help_content()

    def action_prev_category(self) -> None:
        """Cycle to previous help category."""
        categories = list(HelpCategory)
        if self.current_category is None:
            self.current_category = categories[-1]
        else:
            current_idx = categories.index(self.current_category)
            prev_idx = (current_idx - 1) % len(categories)
            self.current_category = categories[prev_idx]

        # Update display
        self.query_one("#help-subheader", Label).update(self._get_subheader_text())
        self._render_help_content()

    def action_dismiss(self) -> None:
        """Close the help overlay."""
        self.dismiss()
