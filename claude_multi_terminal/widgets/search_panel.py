"""Global search panel for finding text across all sessions."""

from textual.widgets import Input, Button, Label, Static
from textual.containers import Horizontal, Vertical
from textual.app import ComposeResult
from textual.reactive import reactive
from textual.binding import Binding
from rich.text import Text
from typing import Optional, List, Tuple
import re


class SearchResult:
    """Represents a single search match."""

    def __init__(
        self,
        session_id: str,
        session_name: str,
        line_idx: int,
        col_idx: int,
        match_text: str,
        context_before: str = "",
        context_after: str = ""
    ):
        """
        Initialize search result.

        Args:
            session_id: ID of the session containing the match
            session_name: Display name of the session
            line_idx: Line index where match was found
            col_idx: Column index where match starts
            match_text: The matched text
            context_before: Text before the match (for preview)
            context_after: Text after the match (for preview)
        """
        self.session_id = session_id
        self.session_name = session_name
        self.line_idx = line_idx
        self.col_idx = col_idx
        self.match_text = match_text
        self.context_before = context_before
        self.context_after = context_after


class SearchPanel(Vertical):
    """
    Global search panel widget.

    Features:
    - Search input with real-time updates
    - Match count per session
    - Next/Previous navigation
    - Jump to match in session
    - Case-insensitive search by default
    - Regex support toggle
    """

    DEFAULT_CSS = """
    SearchPanel {
        height: auto;
        width: 100%;
        background: rgb(30,30,30);
        border-top: heavy rgb(255,77,77);
        padding: 1 2;
        dock: bottom;
        display: none;
        layer: overlay;
    }

    SearchPanel.visible {
        display: block;
    }

    SearchPanel .search-header {
        height: auto;
        width: 100%;
        padding: 0 0 1 0;
    }

    SearchPanel .search-title {
        color: rgb(255,100,100);
        text-style: bold;
        padding: 0 1 0 0;
    }

    SearchPanel .search-input-row {
        height: auto;
        width: 100%;
        padding: 0 0 1 0;
    }

    SearchPanel Input {
        width: 1fr;
        background: rgb(40,40,40);
        border: solid rgb(255,77,77);
        margin: 0 1 0 0;
    }

    SearchPanel Input:focus {
        border: solid rgb(255,100,100);
        background: rgb(44,44,44);
    }

    SearchPanel Button {
        min-width: 10;
        margin: 0 1;
        height: 3;
    }

    SearchPanel Button.nav-btn {
        min-width: 8;
        background: rgb(42,42,42);
        border: solid rgb(100,100,100);
        color: rgb(240,240,240);
    }

    SearchPanel Button.nav-btn:hover {
        background: rgb(60,60,60);
        border: solid rgb(120,120,120);
    }

    SearchPanel Button.nav-btn:disabled {
        background: rgb(30,30,30);
        border: solid rgb(60,60,60);
        color: rgb(120,120,120);
    }

    SearchPanel Button.close-btn {
        min-width: 8;
        background: rgb(60,60,80);
        border: solid rgb(80,80,100);
        color: rgb(200,200,220);
    }

    SearchPanel Button.close-btn:hover {
        background: rgb(80,80,100);
    }

    SearchPanel .search-info {
        height: auto;
        width: 100%;
        color: rgb(180,180,180);
        padding: 0 0 0 0;
    }

    SearchPanel .search-results {
        height: auto;
        width: 100%;
        color: rgb(180,180,180);
        padding: 1 0 0 0;
        text-style: dim;
    }
    """

    BINDINGS = [
        Binding("escape", "close", "Close search", show=False),
        Binding("enter", "search_next", "Next match", show=False),
        Binding("shift+enter", "search_prev", "Previous match", show=False),
        Binding("f3", "search_next", "Next match", show=False),
        Binding("shift+f3", "search_prev", "Previous match", show=False),
    ]

    # Reactive properties
    search_query = reactive("")
    case_sensitive = reactive(False)
    use_regex = reactive(False)
    current_match = reactive(0)
    total_matches = reactive(0)

    def __init__(self, **kwargs):
        """Initialize search panel."""
        super().__init__(**kwargs)
        self.results: List[SearchResult] = []
        self.is_visible = False

    def compose(self) -> ComposeResult:
        """Compose the search panel layout."""
        with Horizontal(classes="search-header"):
            yield Label("🔍 Global Search", classes="search-title")
            yield Static(
                "Search across all sessions | ESC to close",
                classes="search-info"
            )

        with Horizontal(classes="search-input-row"):
            yield Input(
                placeholder="Enter search term... (Ctrl+F to focus)",
                id="search-input"
            )
            yield Button("⬆ Prev", id="prev-btn", classes="nav-btn")
            yield Button("⬇ Next", id="next-btn", classes="nav-btn")
            yield Button("✕ Close", id="close-btn", classes="close-btn")

        yield Static(
            "No matches found",
            id="search-results",
            classes="search-results"
        )

    async def on_mount(self) -> None:
        """Initialize the search panel when mounted."""
        # Update button states
        self._update_button_states()

    def show(self) -> None:
        """Show the search panel and focus input."""
        self.add_class("visible")
        self.is_visible = True
        self.display = True

        # Focus the input field
        input_widget = self.query_one("#search-input", Input)
        input_widget.focus()

    def hide(self) -> None:
        """Hide the search panel."""
        self.remove_class("visible")
        self.is_visible = False
        self.display = False

        # Clear highlights in all sessions
        self._clear_all_highlights()

    def action_close(self) -> None:
        """Close the search panel."""
        self.hide()

    async def on_input_changed(self, event: Input.Changed) -> None:
        """Handle search input changes."""
        if event.input.id != "search-input":
            return

        self.search_query = event.value
        await self._perform_search()

    async def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses."""
        if event.button.id == "close-btn":
            self.hide()
        elif event.button.id == "next-btn":
            await self.action_search_next()
        elif event.button.id == "prev-btn":
            await self.action_search_prev()

    async def action_search_next(self) -> None:
        """Navigate to next match."""
        if not self.results:
            return

        self.current_match = (self.current_match + 1) % len(self.results)
        await self._jump_to_match(self.current_match)

    async def action_search_prev(self) -> None:
        """Navigate to previous match."""
        if not self.results:
            return

        self.current_match = (self.current_match - 1) % len(self.results)
        await self._jump_to_match(self.current_match)

    async def _perform_search(self) -> None:
        """
        Perform search across all sessions.

        Finds all matches and updates UI with results.
        """
        query = self.search_query.strip()

        # Clear previous results
        self.results = []
        self.current_match = 0
        self.total_matches = 0

        if not query:
            self._update_results_display()
            self._clear_all_highlights()
            return

        # Get all session panes from the app
        try:
            from .session_pane import SessionPane

            session_panes = self.app.query(SessionPane)

            # Search each session
            for pane in session_panes:
                matches = await self._search_session(pane, query)
                self.results.extend(matches)

            self.total_matches = len(self.results)

            # Update UI
            self._update_results_display()
            self._update_button_states()

            # Highlight all matches
            await self._highlight_all_matches()

            # Jump to first match if any
            if self.results:
                self.current_match = 0
                await self._jump_to_match(0)

        except Exception as e:
            # Handle errors gracefully
            self.app.notify(f"Search error: {e}", severity="error")

    async def _search_session(
        self,
        pane,
        query: str
    ) -> List[SearchResult]:
        """
        Search a single session for matches.

        Args:
            pane: SessionPane to search
            query: Search query string

        Returns:
            List of SearchResult objects
        """
        matches = []

        try:
            from .selectable_richlog import SelectableRichLog

            # Get the output widget
            output = pane.query_one(f"#output-{pane.session_id}", SelectableRichLog)

            # Prepare search pattern
            if self.use_regex:
                try:
                    pattern = re.compile(
                        query,
                        0 if self.case_sensitive else re.IGNORECASE
                    )
                except re.error:
                    # Invalid regex, treat as literal
                    pattern = re.compile(
                        re.escape(query),
                        0 if self.case_sensitive else re.IGNORECASE
                    )
            else:
                # Literal search
                pattern = re.compile(
                    re.escape(query),
                    0 if self.case_sensitive else re.IGNORECASE
                )

            # Search each line
            for line_idx, line in enumerate(output.lines):
                # Extract plain text from line
                line_text = "".join(seg.text for seg in line._segments)

                # Find all matches in this line
                for match in pattern.finditer(line_text):
                    col_idx = match.start()
                    match_text = match.group()

                    # Get context (30 chars before/after)
                    context_start = max(0, col_idx - 30)
                    context_end = min(len(line_text), col_idx + len(match_text) + 30)

                    context_before = line_text[context_start:col_idx]
                    context_after = line_text[col_idx + len(match_text):context_end]

                    result = SearchResult(
                        session_id=pane.session_id,
                        session_name=pane.session_name,
                        line_idx=line_idx,
                        col_idx=col_idx,
                        match_text=match_text,
                        context_before=context_before,
                        context_after=context_after
                    )
                    matches.append(result)

        except Exception as e:
            # Session might not be ready, skip silently
            pass

        return matches

    async def _jump_to_match(self, match_idx: int) -> None:
        """
        Jump to the specified match.

        Args:
            match_idx: Index of match to jump to
        """
        if not self.results or match_idx >= len(self.results):
            return

        result = self.results[match_idx]

        # Find the session pane
        from .session_pane import SessionPane

        session_panes = self.app.query(SessionPane)
        target_pane = None

        for pane in session_panes:
            if pane.session_id == result.session_id:
                target_pane = pane
                break

        if not target_pane:
            return

        # Get the output widget
        from .selectable_richlog import SelectableRichLog

        output = target_pane.query_one(
            f"#output-{result.session_id}",
            SelectableRichLog
        )

        # Scroll to the line
        # Calculate the target scroll position
        target_scroll = max(0, result.line_idx - 5)  # Show match with 5 lines context
        output.scroll_to(y=target_scroll, animate=False)

        # Update current match highlight
        await self._highlight_current_match(result)

        # Update results display
        self._update_results_display()

    async def _highlight_all_matches(self) -> None:
        """Highlight all search matches across all sessions."""
        from .session_pane import SessionPane
        from .selectable_richlog import SelectableRichLog

        session_panes = self.app.query(SessionPane)

        for pane in session_panes:
            output = pane.query_one(
                f"#output-{pane.session_id}",
                SelectableRichLog
            )

            # Get matches for this session
            session_matches = [
                (r.line_idx, r.col_idx, len(r.match_text))
                for r in self.results
                if r.session_id == pane.session_id
            ]

            # Set search highlights
            output.set_search_highlights(session_matches)

    async def _highlight_current_match(self, result: SearchResult) -> None:
        """
        Highlight the current match with a different color.

        Args:
            result: The current search result to highlight
        """
        from .session_pane import SessionPane
        from .selectable_richlog import SelectableRichLog

        session_panes = self.app.query(SessionPane)

        for pane in session_panes:
            output = pane.query_one(
                f"#output-{pane.session_id}",
                SelectableRichLog
            )

            if pane.session_id == result.session_id:
                # Set current match highlight
                output.set_current_match(
                    result.line_idx,
                    result.col_idx,
                    len(result.match_text)
                )
            else:
                # Clear current match in other sessions
                output.clear_current_match()

    def _clear_all_highlights(self) -> None:
        """Clear search highlights from all sessions."""
        try:
            from .session_pane import SessionPane
            from .selectable_richlog import SelectableRichLog

            session_panes = self.app.query(SessionPane)

            for pane in session_panes:
                output = pane.query_one(
                    f"#output-{pane.session_id}",
                    SelectableRichLog
                )
                output.clear_search_highlights()
                output.clear_current_match()

        except Exception:
            # Ignore errors during cleanup
            pass

    def _update_results_display(self) -> None:
        """Update the results display text."""
        try:
            results_widget = self.query_one("#search-results", Static)

            if not self.search_query.strip():
                results_widget.update("Enter a search term to begin")
            elif not self.results:
                results_widget.update(
                    Text(
                        f"No matches found for '{self.search_query}'",
                        style="dim yellow"
                    )
                )
            else:
                # Group results by session
                session_counts = {}
                for result in self.results:
                    key = (result.session_id, result.session_name)
                    session_counts[key] = session_counts.get(key, 0) + 1

                # Build display text
                display_text = Text()
                display_text.append(
                    f"Match {self.current_match + 1} of {self.total_matches}",
                    style="bold rgb(255,100,100)"
                )
                display_text.append(" | ", style="dim white")

                # Add per-session counts
                session_parts = []
                for (session_id, session_name), count in session_counts.items():
                    session_parts.append(f"{session_name[:20]}: {count}")

                display_text.append(", ".join(session_parts), style="dim cyan")

                results_widget.update(display_text)

        except Exception:
            # Widget might not be ready
            pass

    def _update_button_states(self) -> None:
        """Update navigation button enabled/disabled states."""
        try:
            prev_btn = self.query_one("#prev-btn", Button)
            next_btn = self.query_one("#next-btn", Button)

            has_results = len(self.results) > 0

            prev_btn.disabled = not has_results
            next_btn.disabled = not has_results

        except Exception:
            # Buttons might not be ready yet
            pass

    def watch_total_matches(self, count: int) -> None:
        """React to total matches changes."""
        self._update_button_states()
