"""RichLog widget with mouse text selection support."""

from textual.widgets import RichLog, Static, Label
from textual import events
from textual.reactive import reactive
from textual.geometry import Region, Offset
from textual.containers import Container, Vertical
from textual.app import ComposeResult
from textual.binding import Binding
from rich.text import Text
from typing import Optional, Tuple, Callable
from dataclasses import dataclass


@dataclass
class MenuItem:
    """Represents a menu item in the context menu."""
    label: str
    callback: Callable
    enabled: bool = True
    shortcut: str = ""


class ContextMenu(Container):
    """
    Context menu widget that appears at cursor position.

    Features:
    - Shows at specified x, y coordinates
    - Lists menu items with callbacks
    - Handles enabled/disabled states
    - Dismisses on outside click or Escape
    - Styled with Homebrew theme colors
    """

    DEFAULT_CSS = """
    ContextMenu {
        layer: overlay;
        width: auto;
        height: auto;
        background: rgb(32,32,32);
        border: solid rgb(255,77,77);
        padding: 0;
        offset: 0 0;
        layout: vertical;
    }

    ContextMenu .menu-item {
        width: auto;
        height: 1;
        padding: 0 2;
        background: rgb(32,32,32);
        color: rgb(240,240,240);
        content-align: left middle;
    }

    ContextMenu .menu-item:hover {
        background: rgb(255,77,77);
        color: rgb(24,24,24);
    }

    ContextMenu .menu-item-disabled {
        width: auto;
        height: 1;
        padding: 0 2;
        background: rgb(32,32,32);
        color: rgb(120,120,120);
        content-align: left middle;
    }

    ContextMenu .menu-separator {
        width: auto;
        height: 1;
        background: rgb(32,32,32);
        color: rgb(60,60,60);
    }
    """

    BINDINGS = [
        Binding("escape", "dismiss", "Dismiss menu", show=False),
    ]

    def __init__(
        self,
        items: list[MenuItem],
        x: int,
        y: int,
        **kwargs
    ):
        """
        Initialize context menu.

        Args:
            items: List of menu items to display
            x: X coordinate for menu position
            y: Y coordinate for menu position
        """
        super().__init__(**kwargs)
        self.menu_items = items
        self.menu_x = x
        self.menu_y = y

    def compose(self) -> ComposeResult:
        """Compose the menu layout."""
        from textual.widgets import Label

        # Yield each label directly (ContextMenu is already a Container)
        for item in self.menu_items:
            if item.label == "---":
                # Separator
                label = Label("─" * 30, classes="menu-separator")
            elif item.enabled:
                # Active menu item
                display_text = item.label
                if item.shortcut:
                    # Pad shortcut to align right
                    padding = max(0, 30 - len(item.label) - len(item.shortcut))
                    display_text = f"{item.label}{' ' * padding}{item.shortcut}"
                label = Label(display_text, classes="menu-item")
                label.menu_item = item  # Store reference for click handling
            else:
                # Disabled menu item
                display_text = item.label
                if item.shortcut:
                    padding = max(0, 30 - len(item.label) - len(item.shortcut))
                    display_text = f"{item.label}{' ' * padding}{item.shortcut}"
                label = Label(display_text, classes="menu-item-disabled")
                label.menu_item = None

            yield label

    def on_mount(self) -> None:
        """Position the menu when mounted."""
        # Set position relative to parent
        self.styles.offset = (self.menu_x, self.menu_y)

        # Ensure menu stays within screen bounds
        screen_width = self.screen.size.width
        screen_height = self.screen.size.height

        # Calculate menu dimensions (approximate)
        menu_width = 32  # Approximate width with border
        menu_height = len(self.menu_items) + 2  # Items + border

        # Adjust position if menu would go off screen
        if self.menu_x + menu_width > screen_width:
            self.menu_x = max(0, screen_width - menu_width)
        if self.menu_y + menu_height > screen_height:
            self.menu_y = max(0, screen_height - menu_height)

        self.styles.offset = (self.menu_x, self.menu_y)

    def on_mouse_down(self, event: events.MouseDown) -> None:
        """Handle menu item clicks."""
        # Get the widget under the mouse
        widget, _ = self.screen.get_widget_at(event.screen_x, event.screen_y)

        # Check if it's a label with a menu item
        if hasattr(widget, 'menu_item') and widget.menu_item:
            # Execute callback
            widget.menu_item.callback()
            # Dismiss menu
            self.remove()

        # Stop event propagation
        event.stop()

    def action_dismiss(self) -> None:
        """Dismiss the menu."""
        self.remove()

    def on_click(self, event: events.Click) -> None:
        """Prevent clicks from propagating through menu."""
        event.stop()


class SelectableRichLog(RichLog):
    """
    Enhanced RichLog widget with mouse text selection capabilities.

    Features:
    - Click and drag to select text
    - Double-click to select word
    - Triple-click to select line
    - Ctrl+C to copy selected text
    - Visual highlight for selected text
    """

    DEFAULT_CSS = """
    SelectableRichLog {
        background: rgb(24,24,24);
        color: rgb(240,240,240);
        border: none;
        padding: 1 2;
    }

    SelectableRichLog:focus {
        border: none;
    }

    SelectableRichLog .auto-scroll-indicator {
        dock: top;
        width: 13;
        height: 1;
        background: rgb(40,40,40);
        color: rgb(240,240,240);
        border: solid rgb(80,80,80);
        padding: 0 1;
        layer: overlay;
        align: right top;
    }

    SelectableRichLog .auto-scroll-indicator.enabled {
        background: rgb(40,60,40);
        color: rgb(100,255,100);
        border: solid rgb(80,160,80);
    }

    SelectableRichLog .auto-scroll-indicator.disabled {
        background: rgb(60,40,40);
        color: rgb(255,100,100);
        border: solid rgb(160,80,80);
    }
    """

    # Reactive properties
    selection_active = reactive(False)
    auto_scroll_enabled = reactive(True)

    def __init__(self, **kwargs):
        """Initialize selectable RichLog."""
        super().__init__(**kwargs)
        self.selection_start: Optional[Tuple[int, int]] = None  # (line, column)
        self.selection_end: Optional[Tuple[int, int]] = None
        self.is_selecting = False
        self.last_click_time = 0
        self.click_count = 0
        self.can_focus = True
        self.context_menu: Optional[ContextMenu] = None

        # Auto-scroll state
        self._user_scrolled_up = False
        self._last_scroll_y = 0
        self._last_max_scroll_y = 0

        # Search highlighting
        self.search_highlights: list[Tuple[int, int, int]] = []  # [(line_idx, col_idx, length)]
        self.current_match: Optional[Tuple[int, int, int]] = None  # (line_idx, col_idx, length)

    def on_mouse_down(self, event: events.MouseDown) -> None:
        """Start text selection on left click, show context menu on right click."""
        # Dismiss any existing context menu on any click
        if self.context_menu:
            self.context_menu.remove()
            self.context_menu = None

        if event.button == 1:  # Left click
            import time
            current_time = time.time()

            # Detect double/triple click
            if current_time - self.last_click_time < 0.5:
                self.click_count += 1
            else:
                self.click_count = 1

            self.last_click_time = current_time

            # Get text position from mouse coordinates
            pos = self._get_text_position(event)

            if self.click_count == 1:
                # Single click - start selection
                self.selection_start = pos
                self.selection_end = pos
                self.is_selecting = True
                self.selection_active = True
                self.capture_mouse()

            elif self.click_count == 2:
                # Double click - select word
                self._select_word(pos)

            elif self.click_count >= 3:
                # Triple click - select line
                self._select_line(pos)
                self.click_count = 0

            event.stop()

        elif event.button == 3:  # Right click
            # Show context menu
            self._show_context_menu(event.x, event.y)
            event.stop()

    def on_mouse_move(self, event: events.MouseMove) -> None:
        """Update selection end position while dragging."""
        if self.is_selecting:
            self.selection_end = self._get_text_position(event)
            self.refresh()
            event.stop()

    def on_descendant_blur(self, event: events.DescendantBlur) -> None:
        """Handle when a descendant loses focus."""
        # Dismiss context menu when clicking outside
        if self.context_menu and event.widget == self.context_menu:
            self.context_menu.remove()
            self.context_menu = None

    def on_mouse_up(self, event: events.MouseUp) -> None:
        """Finalize selection."""
        if self.is_selecting:
            self.is_selecting = False
            self.release_mouse()

            # If no text selected (just a click), clear selection
            if self.selection_start == self.selection_end:
                self._clear_selection()

            event.stop()

    def on_key(self, event: events.Key) -> None:
        """Handle keyboard shortcuts."""
        # Ctrl+C / Cmd+C - copy selection
        if event.key == "ctrl+c" or event.key == "cmd+c":
            if self.selection_active and self.selection_start and self.selection_end:
                self._copy_selection()
                event.stop()
                event.prevent_default()

        # Ctrl+A / Cmd+A - select all
        elif event.key == "ctrl+a" or event.key == "cmd+a":
            self._select_all()
            event.stop()
            event.prevent_default()

        # Ctrl+Shift+A - toggle auto-scroll
        elif event.key == "ctrl+shift+a":
            self._toggle_auto_scroll()
            event.stop()
            event.prevent_default()

        # Escape - clear selection or dismiss context menu
        elif event.key == "escape":
            if self.context_menu:
                self.context_menu.remove()
                self.context_menu = None
            else:
                self._clear_selection()
            event.stop()

    def _get_text_position(self, event: events.MouseEvent) -> Tuple[int, int]:
        """
        Convert mouse coordinates to text position (line, column).

        Args:
            event: Mouse event with x, y coordinates

        Returns:
            Tuple of (line_index, column_index)
        """
        # Calculate line number from scroll offset + mouse Y
        # Adjust for padding
        line_idx = int(self.scroll_y + event.y - 1)

        # Bounds check
        line_idx = max(0, min(line_idx, len(self.lines) - 1))

        # Find column in line based on X coordinate
        col_idx = 0
        if line_idx < len(self.lines):
            # Adjust for padding
            col_idx = max(0, int(event.x - 2))

        return (line_idx, col_idx)

    def _select_word(self, pos: Tuple[int, int]) -> None:
        """
        Select the word at the given position.

        Args:
            pos: (line, column) position
        """
        line_idx, col_idx = pos

        if line_idx >= len(self.lines):
            return

        line = self.lines[line_idx]
        text = "".join(seg.text for seg in line._segments)

        if not text or col_idx >= len(text):
            return

        # Find word boundaries
        import re

        # Find start of word
        start = col_idx
        while start > 0 and re.match(r'\w', text[start - 1]):
            start -= 1

        # Find end of word
        end = col_idx
        while end < len(text) and re.match(r'\w', text[end]):
            end += 1

        self.selection_start = (line_idx, start)
        self.selection_end = (line_idx, end)
        self.selection_active = True
        self.refresh()

    def _select_line(self, pos: Tuple[int, int]) -> None:
        """
        Select the entire line at the given position.

        Args:
            pos: (line, column) position
        """
        line_idx, _ = pos

        if line_idx >= len(self.lines):
            return

        line = self.lines[line_idx]
        text = "".join(seg.text for seg in line._segments)

        self.selection_start = (line_idx, 0)
        self.selection_end = (line_idx, len(text))
        self.selection_active = True
        self.refresh()

    def _clear_selection(self) -> None:
        """Clear the current selection."""
        self.selection_start = None
        self.selection_end = None
        self.selection_active = False
        self.refresh()

    def _select_all(self) -> None:
        """Select all text in the output."""
        if not self.lines:
            return

        # Select from start of first line to end of last line
        self.selection_start = (0, 0)

        last_line_idx = len(self.lines) - 1
        if last_line_idx >= 0:
            last_line = self.lines[last_line_idx]
            last_line_text = "".join(seg.text for seg in last_line._segments)
            self.selection_end = (last_line_idx, len(last_line_text))
        else:
            self.selection_end = (0, 0)

        self.selection_active = True
        self.refresh()

    def _show_context_menu(self, x: int, y: int) -> None:
        """
        Show context menu at the specified position.

        Args:
            x: X coordinate for menu position
            y: Y coordinate for menu position
        """
        # Check if there's selected text
        has_selection = (
            self.selection_active and
            self.selection_start and
            self.selection_end and
            self.selection_start != self.selection_end
        )

        # Check if there's any output
        has_output = len(self.lines) > 0

        # Create menu items
        menu_items = [
            MenuItem(
                label="Copy",
                callback=self._copy_selection,
                enabled=has_selection,
                shortcut="Ctrl+C"
            ),
            MenuItem(
                label="Select All",
                callback=self._select_all,
                enabled=True,
                shortcut="Ctrl+A"
            ),
            MenuItem(
                label="Clear Selection",
                callback=self._clear_selection,
                enabled=has_selection,
                shortcut="Esc"
            ),
            MenuItem(
                label="---",  # Separator
                callback=lambda: None,
                enabled=False
            ),
            MenuItem(
                label="Copy All Output",
                callback=self._show_copy_all_submenu,
                enabled=has_output
            ),
            MenuItem(
                label="Export Session...",
                callback=self._show_export_options,
                enabled=True
            ),
        ]

        # Remove any existing context menu
        if self.context_menu:
            self.context_menu.remove()

        # Create and mount new context menu
        self.context_menu = ContextMenu(items=menu_items, x=x, y=y)
        self.screen.mount(self.context_menu)

    def _show_export_options(self) -> None:
        """Show export format submenu."""
        # Find the parent SessionPane to call export
        from .session_pane import SessionPane

        session_pane = None
        for ancestor in self.ancestors:
            if isinstance(ancestor, SessionPane):
                session_pane = ancestor
                break

        if not session_pane:
            if hasattr(self.app, 'notify'):
                self.app.notify(
                    "Could not find session to export",
                    severity="error"
                )
            return

        # Dismiss context menu
        if self.context_menu:
            self.context_menu.remove()
            self.context_menu = None

        # Show export format submenu
        export_menu_items = [
            MenuItem(
                label="Export as Markdown",
                callback=lambda: self.app.call_later(session_pane.export_session, "markdown"),
                enabled=True
            ),
            MenuItem(
                label="Export as JSON",
                callback=lambda: self.app.call_later(session_pane.export_session, "json"),
                enabled=True
            ),
            MenuItem(
                label="Export as Text",
                callback=lambda: self.app.call_later(session_pane.export_session, "text"),
                enabled=True
            ),
        ]

        # Show submenu at same position as original menu
        self.context_menu = ContextMenu(items=export_menu_items, x=20, y=10)
        self.screen.mount(self.context_menu)

    def _show_copy_all_submenu(self) -> None:
        """Show copy all output submenu with timestamp options."""
        # Dismiss current menu
        if self.context_menu:
            self.context_menu.remove()
            self.context_menu = None

        # Create submenu with timestamp options
        copy_all_items = [
            MenuItem(
                label="Copy All (Plain Text)",
                callback=lambda: self._copy_all_output(include_timestamps=False),
                enabled=True
            ),
            MenuItem(
                label="Copy All (with Timestamps)",
                callback=lambda: self._copy_all_output(include_timestamps=True),
                enabled=True
            ),
        ]

        # Show submenu at same position
        self.context_menu = ContextMenu(items=copy_all_items, x=20, y=10)
        self.screen.mount(self.context_menu)

    def _copy_all_output(self, include_timestamps: bool = False) -> None:
        """
        Copy all output from the session to clipboard.

        Args:
            include_timestamps: Whether to include timestamps in the output
        """
        try:
            # Extract all text from lines
            all_text = self._get_all_output_text(include_timestamps)

            if not all_text:
                if hasattr(self.app, 'notify'):
                    self.app.notify(
                        "No output to copy",
                        severity="warning",
                        timeout=2
                    )
                return

            # Copy to clipboard
            if hasattr(self.app, 'clip_manager'):
                success = self.app.clip_manager.copy_to_system(all_text)

                if success:
                    # Calculate statistics
                    line_count = len(self.lines)
                    char_count = len(all_text)

                    # Format message based on size
                    if char_count > 1_000_000:
                        size_msg = f"{char_count / 1_000_000:.1f}M"
                    elif char_count > 1_000:
                        size_msg = f"{char_count / 1_000:.1f}K"
                    else:
                        size_msg = str(char_count)

                    timestamp_msg = " (with timestamps)" if include_timestamps else ""

                    self.app.notify(
                        f"Copied {line_count} lines ({size_msg} chars){timestamp_msg}",
                        severity="information",
                        timeout=3
                    )
                else:
                    # Fallback to internal buffer
                    self.app.clip_manager_buffer = all_text
                    self.app.notify(
                        "Copied to internal buffer",
                        severity="warning",
                        timeout=2
                    )
        except Exception as e:
            if hasattr(self.app, 'notify'):
                self.app.notify(
                    f"Failed to copy output: {str(e)}",
                    severity="error",
                    timeout=3
                )

    def _get_all_output_text(self, include_timestamps: bool = False) -> str:
        """
        Extract all text from the output log.

        Args:
            include_timestamps: Whether to include timestamps (if available)

        Returns:
            All output text as a plain string
        """
        if not self.lines:
            return ""

        lines = []
        for line in self.lines:
            # Extract text from segments
            line_text = "".join(seg.text for seg in line._segments)

            # For now, we don't parse timestamps as they're embedded in the text
            # In a future enhancement, we could strip them when include_timestamps=False
            lines.append(line_text)

        return "\n".join(lines)

    def _copy_selection(self) -> None:
        """Copy selected text to clipboard."""
        selected_text = self.get_selected_text()

        if not selected_text:
            return

        # Get clipboard manager from app
        if hasattr(self.app, 'clip_manager'):
            success = self.app.clip_manager.copy_to_system(selected_text)

            if success:
                self.app.notify(
                    f"📋 Copied {len(selected_text)} characters",
                    severity="information",
                    timeout=2
                )
            else:
                # Fallback to internal buffer
                self.app.clip_manager_buffer = selected_text
                self.app.notify(
                    "📋 Copied to internal buffer",
                    severity="warning",
                    timeout=2
                )

    def get_selected_text(self) -> str:
        """
        Extract plain text from current selection.

        Returns:
            Selected text as plain string, or empty string if no selection
        """
        if not (self.selection_start and self.selection_end):
            return ""

        start_line, start_col = self.selection_start
        end_line, end_col = self.selection_end

        # Ensure start < end
        if (start_line, start_col) > (end_line, end_col):
            start_line, start_col, end_line, end_col = \
                end_line, end_col, start_line, start_col

        # Bounds check
        if start_line >= len(self.lines):
            return ""

        # Extract text
        lines = []
        for line_idx in range(start_line, end_line + 1):
            if line_idx < len(self.lines):
                line = self.lines[line_idx]
                text = "".join(seg.text for seg in line._segments)

                if line_idx == start_line == end_line:
                    # Selection within single line
                    lines.append(text[start_col:end_col])
                elif line_idx == start_line:
                    # First line of multi-line selection
                    lines.append(text[start_col:])
                elif line_idx == end_line:
                    # Last line of multi-line selection
                    lines.append(text[:end_col])
                else:
                    # Middle line - take all
                    lines.append(text)

        return "\n".join(lines)

    def render_line(self, y: int) -> Text:
        """
        Override render_line to add selection and search highlighting.

        Args:
            y: Line number to render

        Returns:
            Rich Text object with highlighting applied
        """
        # Get the base rendered line from parent
        line = super().render_line(y)

        # Apply search highlighting first (so selection can override it)
        if self.search_highlights:
            line = self._apply_search_highlights(line, y)

        # Apply selection highlighting if this line is in selection
        if self.selection_active and self.selection_start and self.selection_end:
            line = self._apply_selection_highlight(line, y)

        return line

    def _apply_selection_highlight(self, line, line_idx: int):
        """
        Apply selection highlighting to a line.

        Args:
            line: Strip object from RichLog rendering
            line_idx: Index of this line

        Returns:
            Strip object with selection highlighting applied
        """
        if not (self.selection_start and self.selection_end):
            return line

        start_line, start_col = self.selection_start
        end_line, end_col = self.selection_end

        # Ensure start < end
        if (start_line, start_col) > (end_line, end_col):
            start_line, start_col, end_line, end_col = \
                end_line, end_col, start_line, start_col

        # Check if this line is in selection range
        if not (start_line <= line_idx <= end_line):
            return line

        # Import needed classes
        from rich.segment import Segment
        from rich.style import Style
        from textual.strip import Strip

        # Get plain text from Strip segments
        plain_text = "".join(seg.text for seg in line._segments) if hasattr(line, '_segments') else ""

        if not plain_text:
            return line

        # Determine selection range for this line
        if line_idx == start_line == end_line:
            # Selection within single line
            col_start, col_end = start_col, end_col
        elif line_idx == start_line:
            # First line of multi-line selection
            col_start, col_end = start_col, len(plain_text)
        elif line_idx == end_line:
            # Last line of multi-line selection
            col_start, col_end = 0, end_col
        else:
            # Middle line - highlight all
            col_start, col_end = 0, len(plain_text)

        # Bounds check
        col_start = max(0, min(col_start, len(plain_text)))
        col_end = max(col_start, min(col_end, len(plain_text)))

        # If no selection in this line, return as-is
        if col_start >= col_end:
            return line

        # Build new segments with selection highlighting
        new_segments = []
        current_pos = 0

        # Selection highlight style
        from rich.color import Color
        highlight_style = Style(bgcolor=Color.parse("rgb(60,50,30)"))

        for segment in line._segments:
            seg_text = segment.text
            seg_len = len(seg_text)
            seg_end = current_pos + seg_len

            # Check if this segment overlaps with selection
            if current_pos >= col_end or seg_end <= col_start:
                # No overlap - keep segment as-is
                new_segments.append(segment)
            else:
                # Has overlap - need to split segment
                overlap_start = max(0, col_start - current_pos)
                overlap_end = min(seg_len, col_end - current_pos)

                # Before selection
                if overlap_start > 0:
                    new_segments.append(Segment(seg_text[:overlap_start], segment.style))

                # Selected part
                selected_text = seg_text[overlap_start:overlap_end]
                # Merge highlight with existing style
                if segment.style:
                    merged_style = segment.style + highlight_style
                else:
                    merged_style = highlight_style
                new_segments.append(Segment(selected_text, merged_style))

                # After selection
                if overlap_end < seg_len:
                    new_segments.append(Segment(seg_text[overlap_end:], segment.style))

            current_pos = seg_end

        # Return new Strip with highlighted segments
        return Strip(new_segments, len(line))

    def set_search_highlights(self, highlights: list[Tuple[int, int, int]]) -> None:
        """
        Set search highlights for the output.

        Args:
            highlights: List of (line_idx, col_idx, length) tuples
        """
        self.search_highlights = highlights
        self.refresh()

    def clear_search_highlights(self) -> None:
        """Clear all search highlights."""
        self.search_highlights = []
        self.refresh()

    def set_current_match(self, line_idx: int, col_idx: int, length: int) -> None:
        """
        Set the current match highlight (distinct from other matches).

        Args:
            line_idx: Line index of current match
            col_idx: Column index of current match
            length: Length of match text
        """
        self.current_match = (line_idx, col_idx, length)
        self.refresh()

    def clear_current_match(self) -> None:
        """Clear the current match highlight."""
        self.current_match = None
        self.refresh()

    def _apply_search_highlights(self, line, line_idx: int):
        """
        Apply search highlighting to a line.

        Args:
            line: Strip object from RichLog rendering
            line_idx: Index of this line

        Returns:
            Strip object with search highlighting applied
        """
        # Import needed classes
        from rich.segment import Segment
        from rich.style import Style
        from rich.color import Color
        from textual.strip import Strip

        # Get plain text from Strip segments
        plain_text = "".join(seg.text for seg in line._segments) if hasattr(line, '_segments') else ""

        if not plain_text:
            return line

        # Find all highlights for this line
        line_highlights = []
        for h_line_idx, h_col_idx, h_length in self.search_highlights:
            if h_line_idx == line_idx:
                line_highlights.append((h_col_idx, h_length))

        # Check for current match on this line
        current_match_range = None
        if self.current_match and self.current_match[0] == line_idx:
            current_match_range = (self.current_match[1], self.current_match[2])

        if not line_highlights and not current_match_range:
            return line

        # Define highlight styles
        # Regular match: yellow/amber background (matching theme)
        match_style = Style(bgcolor=Color.parse("rgb(80,60,20)"))
        # Current match: brighter amber background
        current_match_style = Style(bgcolor=Color.parse("rgb(120,90,30)"))

        # Build new segments with highlights
        new_segments = []
        current_pos = 0

        for segment in line._segments:
            seg_text = segment.text
            seg_len = len(seg_text)
            seg_end = current_pos + seg_len

            # Check which highlights overlap with this segment
            overlaps = []

            # Check regular highlights
            for col_idx, length in line_highlights:
                col_end = col_idx + length
                if col_idx < seg_end and col_end > current_pos:
                    overlaps.append((col_idx, col_end, False))  # False = not current

            # Check current match
            if current_match_range:
                col_idx, length = current_match_range
                col_end = col_idx + length
                if col_idx < seg_end and col_end > current_pos:
                    overlaps.append((col_idx, col_end, True))  # True = is current

            if not overlaps:
                # No highlights in this segment
                new_segments.append(segment)
            else:
                # Has highlights - need to split segment
                seg_start_pos = current_pos
                text_parts = []  # [(start, end, is_current)]

                # Sort overlaps by start position
                overlaps.sort()

                # Build ranges
                last_pos = 0
                for h_start, h_end, is_current in overlaps:
                    # Calculate relative positions in segment
                    rel_start = max(0, h_start - seg_start_pos)
                    rel_end = min(seg_len, h_end - seg_start_pos)

                    # Add non-highlighted part before highlight
                    if rel_start > last_pos:
                        text_parts.append((last_pos, rel_start, None))

                    # Add highlighted part
                    if rel_end > rel_start:
                        text_parts.append((rel_start, rel_end, is_current))

                    last_pos = rel_end

                # Add remaining non-highlighted part
                if last_pos < seg_len:
                    text_parts.append((last_pos, seg_len, None))

                # Create segments
                for part_start, part_end, is_current in text_parts:
                    part_text = seg_text[part_start:part_end]

                    if is_current is None:
                        # Not highlighted
                        new_segments.append(Segment(part_text, segment.style))
                    elif is_current:
                        # Current match
                        merged_style = segment.style + current_match_style if segment.style else current_match_style
                        new_segments.append(Segment(part_text, merged_style))
                    else:
                        # Regular match
                        merged_style = segment.style + match_style if segment.style else match_style
                        new_segments.append(Segment(part_text, merged_style))

            current_pos = seg_end

        # Return new Strip with highlighted segments
        return Strip(new_segments, len(line))

    def _toggle_auto_scroll(self) -> None:
        """Toggle auto-scroll on/off."""
        self.auto_scroll_enabled = not self.auto_scroll_enabled

        # If re-enabling and we're not already at bottom, scroll to bottom
        if self.auto_scroll_enabled:
            self.scroll_end(animate=False)

        # Show notification
        status = "enabled" if self.auto_scroll_enabled else "disabled"
        icon = "▼" if self.auto_scroll_enabled else "▬"
        if hasattr(self.app, 'notify'):
            self.app.notify(
                f"{icon} Auto-scroll {status}",
                severity="information",
                timeout=2
            )

    def _is_at_bottom(self) -> bool:
        """Check if scrolled to bottom (within 2 lines tolerance)."""
        if not hasattr(self, 'max_scroll_y') or not hasattr(self, 'scroll_y'):
            return True

        # Account for floating point imprecision and partial line visibility
        return self.scroll_y >= (self.max_scroll_y - 2)

    def on_mouse_scroll_down(self, event: events.MouseScrollDown) -> None:
        """Detect manual scroll down - re-enable auto-scroll if at bottom."""
        # Perform the scroll action
        self.scroll_relative(y=event.y, animate=False)

        # If user scrolled to bottom, re-enable auto-scroll
        if self._user_scrolled_up and self._is_at_bottom():
            self._user_scrolled_up = False
            if not self.auto_scroll_enabled:
                self.auto_scroll_enabled = True
                if hasattr(self.app, 'notify'):
                    self.app.notify(
                        "▼ Auto-scroll re-enabled",
                        severity="information",
                        timeout=1.5
                    )

    def on_mouse_scroll_up(self, event: events.MouseScrollUp) -> None:
        """Detect manual scroll up - disable auto-scroll."""
        # Perform the scroll action
        self.scroll_relative(y=-event.y, animate=False)

        # If user scrolls up, mark as manual scroll and disable auto-scroll
        if not self._is_at_bottom():
            self._user_scrolled_up = True
            if self.auto_scroll_enabled:
                self.auto_scroll_enabled = False
                if hasattr(self.app, 'notify'):
                    self.app.notify(
                        "▬ Auto-scroll paused (scroll to bottom to resume)",
                        severity="information",
                        timeout=2
                    )

    def write(self, content, width=None, expand=False, shrink=True, scroll_end=None, animate=False):
        """Override write to implement auto-scroll behavior."""
        super().write(content, width=width, expand=expand, shrink=shrink, scroll_end=scroll_end, animate=animate)

        # Auto-scroll if enabled and user hasn't manually scrolled up
        if self.auto_scroll_enabled and not self._user_scrolled_up:
            self.scroll_end(animate=False)

        return self
