"""Individual terminal pane displaying a Claude CLI session."""

from textual.widgets import Static, Input, OptionList, TextArea
from textual.widgets.option_list import Option
from textual.containers import Vertical, Horizontal
from textual.reactive import reactive
from textual import events, on
from textual.app import ComposeResult
from textual.geometry import Offset
from textual.message import Message
from rich.text import Text
import re
import math
from typing import TYPE_CHECKING, List, Deque
from collections import deque

from .selectable_richlog import SelectableRichLog
from ..core.export import TranscriptExporter, sanitize_filename

if TYPE_CHECKING:
    from ..core.session_manager import SessionManager


# Braille Animation Generators (from CodePen)
DOT_BITS = [[0x01, 0x08], [0x02, 0x10], [0x04, 0x20], [0x40, 0x80]]


def seeded_random(seed: int):
    """Seeded random number generator for consistent animations."""
    s = seed
    def _rand():
        nonlocal s
        s = (s * 1664525 + 1013904223) & 0xffffffff
        return s / 0xffffffff
    return _rand


def gen_pendulum(width: int = 10, max_spread: float = 1.0) -> List[str]:
    """Generate pendulum wave animation frames using braille characters."""
    total_frames = 120
    pixel_cols = width * 2
    frames = []

    for t in range(total_frames):
        codes = [0x2800] * width
        progress = t / total_frames
        spread = math.sin(math.pi * progress) * max_spread
        base_phase = progress * math.pi * 8

        for pc in range(pixel_cols):
            swing = math.sin(base_phase + pc * spread)
            center = (1 - swing) * 1.5

            for row in range(4):
                if abs(row - center) < 0.7:
                    codes[pc // 2] |= DOT_BITS[row][pc % 2]

        frames.append(''.join(chr(c) for c in codes))

    return frames


def gen_compress(width: int = 10) -> List[str]:
    """Generate compress/squeeze animation frames using braille characters."""
    total_frames = 100
    pixel_cols = width * 2
    total_dots = pixel_cols * 4
    frames = []

    rand = seeded_random(42)
    importance = [rand() for _ in range(total_dots)]

    for t in range(total_frames):
        codes = [0x2800] * width
        progress = t / total_frames
        sieve_threshold = max(0.1, 1 - progress * 1.2)
        squeeze = min(1, progress / 0.85)
        active_width = max(1, pixel_cols * (1 - squeeze * 0.95))

        for pc in range(pixel_cols):
            mapped_pc = (pc / pixel_cols) * active_width
            if mapped_pc >= active_width:
                continue

            target_pc = round(mapped_pc)
            if target_pc >= pixel_cols:
                continue

            char_idx = target_pc // 2
            dc = target_pc % 2

            for row in range(4):
                if importance[pc * 4 + row] < sieve_threshold:
                    codes[char_idx] |= DOT_BITS[row][dc]

        frames.append(''.join(chr(c) for c in codes))

    return frames


def gen_sort(width: int = 10) -> List[str]:
    """Generate sorting visualization animation frames using braille characters."""
    pixel_cols = width * 2
    total_frames = 100
    frames = []

    rand = seeded_random(19)
    shuffled = [rand() * 3 for _ in range(pixel_cols)]
    target = [(i / (pixel_cols - 1)) * 3 for i in range(pixel_cols)]

    for t in range(total_frames):
        codes = [0x2800] * width
        progress = t / total_frames
        cursor = progress * pixel_cols * 1.2

        for pc in range(pixel_cols):
            char_idx = pc // 2
            dc = pc % 2
            d = pc - cursor

            if d < -3:
                center = target[pc]
            elif d < 2:
                blend = 1 - (d + 3) / 5
                ease = blend * blend * (3 - 2 * blend)
                center = shuffled[pc] + (target[pc] - shuffled[pc]) * ease

                if abs(d) < 0.8:
                    for r in range(4):
                        codes[char_idx] |= DOT_BITS[r][dc]
                    continue
            else:
                center = (shuffled[pc] +
                         math.sin(progress * math.pi * 16 + pc * 2.7) * 0.6 +
                         math.sin(progress * math.pi * 9 + pc * 1.3) * 0.4)

            center = max(0, min(3, center))

            for r in range(4):
                if abs(r - center) < 0.7:
                    codes[char_idx] |= DOT_BITS[r][dc]

        frames.append(''.join(chr(c) for c in codes))

    return frames


class CommandTextArea(TextArea):
    """
    Custom TextArea that emits a Submitted message on Enter key (without Shift).
    Pressing Shift+Enter adds a newline (multi-line mode).
    Note: The Enter key handling allows bubbling so parent (SessionPane) can
    intercept for autocomplete handling.
    """

    class Submitted(Message):
        """Message sent when Enter is pressed without Shift."""

        def __init__(self, text_area: "CommandTextArea", text: str) -> None:
            super().__init__()
            self.text_area = text_area
            self.text = text

    async def _on_key(self, event: events.Key) -> None:
        """Override key handler to intercept Enter key."""
        # Check for plain Enter key (not Shift+Enter)
        if event.key == "enter":
            # Plain Enter - emit submitted message
            # But DON'T stop the event - let it bubble to parent for autocomplete handling
            text = self.text
            self.post_message(self.Submitted(self, text))
            # Prevent TextArea's default newline behavior
            event.prevent_default()
            # Let event bubble up to SessionPane for autocomplete handling
            return
        elif event.key == "shift+enter":
            # Shift+Enter - add newline (let default behavior happen)
            # Just call parent to handle normally
            await super()._on_key(event)
            return
        elif event.key == "escape":
            # Don't handle escape - let it bubble to parent for autocomplete
            # Just prevent default TextArea behavior
            event.prevent_default()
            return

        # Let parent class handle all other keys
        await super()._on_key(event)


class SessionPane(Vertical):
    """
    Individual terminal pane displaying a Claude CLI session.

    Composition:
    - Session name header (with focus indicator)
    - SelectableRichLog for terminal output (handles ANSI codes)
    - Input field for commands
    """

    DEFAULT_CSS = """
    SessionPane {
        border: heavy rgb(60,60,60);
        height: 1fr;
        width: 1fr;
        background: rgb(32,32,32);
    }

    SessionPane:focus-within {
        border: heavy rgb(255,77,77);
        background: rgb(40,40,40);
    }

    SessionPane.focused-mode {
        border: double rgb(100,180,240);
        background: rgb(40,40,40);
    }

    SessionPane.focused-mode .session-header {
        background: rgb(45,45,50);
        color: rgb(100,180,240);
        border-bottom: solid rgb(100,180,240);
    }

    SessionPane .session-header {
        background: rgb(26,26,26);
        color: rgb(255,77,77);
        padding: 0 2;
        height: 3;
        border-bottom: solid rgb(42,42,42);
    }

    SessionPane:focus-within .session-header {
        background: rgb(40,40,40);
        color: rgb(255,100,100);
        border-bottom: solid rgb(255,77,77);
    }

    SessionPane .terminal-output {
        height: 1fr;
        scrollbar-gutter: stable;
        background: rgb(24,24,24);
        color: rgb(240,240,240);
        border: none;
        padding: 1 2;
    }

    SessionPane .processing-inline {
        height: 1;
        width: auto;
        background: transparent;
        color: rgb(240,240,240);
        padding: 0 0 0 1;
        display: none;
        dock: none;
    }

    SessionPane .processing-inline.visible {
        display: block;
    }

    SessionPane .command-input {
        dock: bottom;
        background: rgb(30,30,30);
        border-top: heavy rgb(60,60,60);
        border-bottom: none;
        border-left: none;
        border-right: none;
        padding: 0 2;
    }

    SessionPane:focus-within .command-input {
        background: rgb(40,40,40);
        border-top: heavy rgb(255,77,77);
    }

    SessionPane .input-container {
        dock: bottom;
        height: auto;
        background: rgb(30,30,30);
        border-top: heavy rgb(60,60,60);
    }

    SessionPane:focus-within .input-container {
        background: rgb(40,40,40);
        border-top: heavy rgb(255,77,77);
    }

    SessionPane .multi-line-input {
        height: auto;
        max-height: 10;
        background: rgb(30,30,30);
        padding: 1 2;
        border: none;
    }

    SessionPane:focus-within .multi-line-input {
        background: rgb(40,40,40);
    }

    SessionPane .mode-indicator {
        height: 1;
        background: rgb(32,32,32);
        color: rgb(180,180,180);
        padding: 0 2;
        text-align: right;
    }

    SessionPane .mode-indicator.multiline {
        color: rgb(255,77,77);
    }

    /* Slash Command Autocomplete Dropdown */
    SessionPane .autocomplete-dropdown {
        display: none;
        layer: overlay;
        offset: 0 -1;
        width: 50;
        max-height: 12;
        background: rgb(40,40,40);
        border: heavy rgb(255,77,77);
        border-bottom: none;
        padding: 0;
    }

    SessionPane .autocomplete-dropdown.visible {
        display: block;
    }

    SessionPane .autocomplete-dropdown > OptionList {
        background: rgb(40,40,40);
        color: rgb(240,240,240);
        height: auto;
        max-height: 12;
        border: none;
        padding: 0 1;
    }

    SessionPane .autocomplete-dropdown > OptionList > .option-list--option {
        background: rgb(40,40,40);
        color: rgb(180,180,180);
        padding: 0 1;
    }

    SessionPane .autocomplete-dropdown > OptionList > .option-list--option-highlighted {
        background: rgb(255,77,77);
        color: rgb(24,24,24);
    }

    SessionPane .autocomplete-dropdown > OptionList:focus > .option-list--option-highlighted {
        background: rgb(255,77,77);
        color: rgb(24,24,24);
    }

    /* Autocomplete header */
    SessionPane .autocomplete-header {
        background: rgb(42,42,42);
        color: rgb(255,100,100);
        padding: 0 1;
        height: 1;
        text-align: left;
    }
    """

    session_name = reactive("Unnamed Session")
    is_active = reactive(False)
    command_count = reactive(0)

    def __init__(
        self,
        session_id: str,
        session_name: str,
        session_manager: "SessionManager",
        *args,
        **kwargs
    ):
        """
        Initialize session pane.

        Args:
            session_id: UUID of the session
            session_name: Display name
            session_manager: Reference to SessionManager
        """
        super().__init__(*args, **kwargs)
        self.session_id = session_id
        self.session_name = session_name
        self.session_manager = session_manager
        self.can_focus = True
        self._update_count = 0  # Debug counter
        self._last_output_time = None  # Track when we last got output
        self._last_command = None  # Track last command sent
        self._response_timer = None  # Timer for response completion
        import time
        self._start_time = time.time()

        # Metrics tracking
        self._processing_start_time = 0  # When current command started
        self._token_count = 0  # Tokens received so far
        self._thinking_time = 0  # Processing time

        # Debug logging
        self._debug_log = open(f"/tmp/session_{session_id[:8]}.log", "w")

        # Slash command autocomplete
        self._autocomplete_visible = False
        self._slash_commands = [
            ("/model", "Switch Claude model (Sonnet/Opus/Haiku)"),
            ("/help", "Show help and available commands"),
            ("/logout", "Logout from Claude CLI"),
            ("/commit", "Create a git commit with changes"),
            ("/review-pr", "Review a GitHub pull request"),
            ("/test", "Run tests for the project"),
            ("/debug", "Debug mode and diagnostics"),
            ("/clear", "Clear the conversation history"),
            ("/save", "Save current session state"),
            ("/load", "Load a saved session"),
            ("/plan", "Enable plan mode for complex tasks"),
            ("/web", "Search the web for information"),
            ("/diff", "Show git diff of changes"),
            ("/status", "Show git status"),
            ("/branch", "Git branch operations"),
            ("/config", "Configure Claude CLI settings"),
            ("/version", "Show Claude CLI version"),
            ("/docs", "Open documentation"),
            ("/feedback", "Send feedback to Anthropic"),
            ("/privacy", "Privacy and data handling info"),
            ("/export", "Export session transcript (markdown|json)"),
            ("/search", "Search across all sessions (Ctrl+F)"),
        ]

        # Export functionality
        self._exporter = TranscriptExporter()

        # Multi-line input and command history
        self._multiline_mode = False  # Start in single-line mode
        self._command_history: Deque[str] = deque(maxlen=100)  # Store last 100 commands
        self._history_index = -1  # Current position in history (-1 = no history navigation)
        self._current_draft = ""  # Store current input when navigating history

        # Real-time status tracking for user feedback
        self._current_status = "Initializing"
        self._status_history: Deque[str] = deque(maxlen=10)  # Keep last 10 status updates

    def _log(self, msg: str):
        """Write to debug log."""
        import time
        self._debug_log.write(f"[{time.time():.2f}] {msg}\n")
        self._debug_log.flush()

    def _extract_status_from_output(self, output: str) -> str:
        """
        Extract meaningful status information from Claude's output.

        Looks for action phrases and file references to show what Claude is doing.

        Args:
            output: Raw output from Claude

        Returns:
            Status string or empty string if nothing meaningful found
        """
        # Common patterns that indicate what Claude is doing
        patterns = [
            # Tool usage patterns (most specific first)
            (r"<invoke name=\"(\w+)\"", lambda m: f"Using {m.group(1)}"),
            (r"<invoke name=\"(\w+)\"", lambda m: f"Using {m.group(1)}"),

            # File operations with paths
            (r"Reading [`'\"]?([^`'\":\n]+\.[\w]+)", lambda m: f"Reading {m.group(1).split('/')[-1]}"),
            (r"Writing [`'\"]?([^`'\":\n]+\.[\w]+)", lambda m: f"Writing {m.group(1).split('/')[-1]}"),
            (r"Editing [`'\"]?([^`'\":\n]+\.[\w]+)", lambda m: f"Editing {m.group(1).split('/')[-1]}"),
            (r"Modifying [`'\"]?([^`'\":\n]+\.[\w]+)", lambda m: f"Modifying {m.group(1).split('/')[-1]}"),

            # Search and find operations
            (r"Searching for [`'\"]?([^`'\":\n]{3,30})[`'\"]?", lambda m: f"Searching: {m.group(1)}"),
            (r"Looking for [`'\"]?([^`'\":\n]{3,30})[`'\"]?", lambda m: f"Finding: {m.group(1)}"),
            (r"Finding [`'\"]?([^`'\":\n]{3,30})[`'\"]?", lambda m: f"Finding: {m.group(1)}"),

            # Execution operations
            (r"Running command [`'\"]?([^`'\":\n]+)[`'\"]?", lambda m: f"Running: {m.group(1)}"),
            (r"Executing [`'\"]?([^`'\":\n]+)[`'\"]?", lambda m: f"Running: {m.group(1)}"),
            (r"Testing [`'\"]?([^`'\":\n]+)[`'\"]?", lambda m: f"Testing: {m.group(1)}"),

            # Analysis operations
            (r"Analyzing ([^`'\":\n]{3,30})", lambda m: f"Analyzing: {m.group(1)}"),
            (r"Checking ([^`'\":\n]{3,30})", lambda m: f"Checking: {m.group(1)}"),
            (r"Verifying ([^`'\":\n]{3,30})", lambda m: f"Verifying: {m.group(1)}"),

            # Build/Install operations
            (r"Installing ([^`'\":\n]+)", lambda m: f"Installing: {m.group(1)}"),
            (r"Building ([^`'\":\n]+)", lambda m: f"Building: {m.group(1)}"),
            (r"Compiling ([^`'\":\n]+)", lambda m: f"Compiling: {m.group(1)}"),

            # Action phrases (Claude's typical responses)
            (r"Let me (\w+(?:\s+\w+){0,4})", lambda m: m.group(1).capitalize()),
            (r"I'll (\w+(?:\s+\w+){0,4})", lambda m: m.group(1).capitalize()),
            (r"I'm going to (\w+(?:\s+\w+){0,4})", lambda m: m.group(1).capitalize()),
            (r"First,? I(?:'ll| will) (\w+(?:\s+\w+){0,4})", lambda m: f"→ {m.group(1)}"),
            (r"Now (?:let me |I'll |I will )?(\w+(?:\s+\w+){0,4})", lambda m: m.group(1).capitalize()),

            # Generic -ing patterns
            (r"(?:^|\n)(?:##?\s+)?(\w+ing)(?:\s+[a-z])", lambda m: m.group(1)),
        ]

        for pattern, formatter in patterns:
            match = re.search(pattern, output, re.IGNORECASE)
            if match:
                try:
                    status = formatter(match)
                    # Clean up the status
                    status = status.strip()
                    if len(status) > 40:
                        status = status[:37] + "..."
                    return status
                except:
                    continue

        return ""

    def compose(self) -> ComposeResult:
        """Build the pane UI components."""
        yield Static(
            self._render_header(),
            classes="session-header",
            id=f"header-{self.session_id}"
        )
        # Use SelectableRichLog for terminal output with ANSI support
        yield SelectableRichLog(
            classes="terminal-output",
            id=f"output-{self.session_id}",
            highlight=True,
            markup=True,
            auto_scroll=True,
            max_lines=10000,  # Keep up to 10k lines in history
            wrap=True  # Wrap long lines
        )
        # Inline processing indicator (hidden by default)
        yield Static(
            "",
            classes="processing-inline",
            id=f"processing-inline-{self.session_id}"
        )
        # Slash command autocomplete dropdown (positioned above input)
        with Vertical(classes="autocomplete-dropdown", id=f"autocomplete-{self.session_id}"):
            yield Static(
                "╭─ Slash Commands ─╮",
                classes="autocomplete-header",
                id=f"autocomplete-header-{self.session_id}"
            )
            yield OptionList(id=f"autocomplete-list-{self.session_id}")

        # Input container with mode indicator
        with Vertical(classes="input-container", id=f"input-container-{self.session_id}"):
            yield Static(
                "Single-line | Enter: Submit | Shift+Enter: Multi-line mode",
                classes="mode-indicator",
                id=f"mode-indicator-{self.session_id}"
            )
            yield CommandTextArea(
                text="",
                classes="multi-line-input",
                id=f"input-{self.session_id}",
                soft_wrap=True,
                show_line_numbers=False,
                tab_behavior="indent"
            )

    def _render_header(self) -> Text:
        """Render rich header with status indicators."""
        text = Text()

        # Connection status indicator
        status_icon = "●" if self.is_active else "○"
        status_color = "bright_green" if self.is_active else "dim white"

        # Left side: Status + Name
        text.append(f"{status_icon} ", style=f"bold {status_color}")
        text.append("┃ ", style="dim white")
        text.append(self.session_name, style="bold white")

        # Right side: Metrics
        if self.command_count > 0:
            text.append("  ", style="")
            text.append("┊", style="dim white")
            text.append(f"  📊 {self.command_count} cmd", style="dim cyan")

        # Session ID badge (last 6 chars)
        text.append("  ", style="")
        text.append("┊", style="dim white")
        text.append(f"  ID: {self.session_id[:6]}", style="dim rgb(150,150,180)")

        return text

    async def on_mount(self) -> None:
        """Initialize the session when pane is mounted."""
        # Add Claude Code-style startup greeting
        output_widget = self.query_one(f"#output-{self.session_id}", SelectableRichLog)

        import os
        cwd = os.getcwd()

        startup_msg = Text()
        startup_msg.append("\n")

        # ASCII art logo (Claude robot character)
        startup_msg.append("      ▄▄▄▄▄\n", style="rgb(188,116,96)")
        startup_msg.append("     █     █\n", style="rgb(188,116,96)")
        startup_msg.append("     █ █ █ █\n", style="rgb(24,24,24) on rgb(188,116,96)")
        startup_msg.append("     █▄▄▄▄▄█\n", style="rgb(188,116,96)")
        startup_msg.append("      █████\n", style="rgb(188,116,96)")
        startup_msg.append("     ███████\n", style="rgb(188,116,96)")
        startup_msg.append("      █ █ █\n\n", style="rgb(188,116,96)")

        # Header
        startup_msg.append("  ", style="")
        startup_msg.append("Claude Code ", style="bold rgb(255,77,77)")
        startup_msg.append("v2.1.23\n", style="dim white")

        startup_msg.append("             ", style="")
        startup_msg.append("Sonnet 4.5", style="bright_white")
        startup_msg.append(" · ", style="dim white")
        startup_msg.append("API Usage Billing\n", style="dim white")

        startup_msg.append("    ▘▘ ▝▝    ", style="bold rgb(255,150,100)")
        startup_msg.append(f"{cwd}\n", style="dim cyan")

        startup_msg.append("\n\n")

        # Auth message (if ANTHROPIC_API_KEY is set)
        if os.environ.get('ANTHROPIC_API_KEY'):
            startup_msg.append("   ", style="")
            startup_msg.append("Auth conflict: ", style="bold yellow")
            startup_msg.append("Using ANTHROPIC_API_KEY instead of Anthropic Console key. Either\n", style="dim white")
            startup_msg.append("    unset ANTHROPIC_API_KEY, or run ", style="dim white")
            startup_msg.append("`claude /logout`", style="dim cyan")
            startup_msg.append(".\n", style="dim white")

        startup_msg.append("    ", style="")
        startup_msg.append("/model", style="dim cyan")
        startup_msg.append(" to try ", style="dim white")
        startup_msg.append("Opus 4.5\n", style="bright_white")

        startup_msg.append("\n\n")

        # Prompt suggestion
        startup_msg.append("  ❯ ", style="bold bright_green")
        startup_msg.append("Try ", style="dim white")
        startup_msg.append('"write a test for <filepath>"', style="dim cyan")
        startup_msg.append("\n\n", style="")

        output_widget.write(startup_msg)
        self._log("Wrote startup message to SelectableRichLog")

        # Get PTY handler from session manager
        session = self.session_manager.sessions.get(self.session_id)
        if session:
            # Start reading PTY output
            await session.pty_handler.start_reading(
                callback=self._handle_output
            )

        # Focus the input field
        input_widget = self.query_one(f"#input-{self.session_id}", CommandTextArea)
        input_widget.focus()

    def _handle_output(self, output: str) -> None:
        """
        Callback for PTY output.

        Args:
            output: Raw terminal output (may contain ANSI codes)
        """
        self._log(f"_handle_output called: {len(output)} bytes")

        # Skip if widget not mounted yet or no app reference
        if not self.is_mounted or not hasattr(self, 'app') or self.app is None:
            self._log("Skipping: widget not mounted or no app")
            return

        # The PTY callback is invoked on the main asyncio thread (not a separate thread),
        # so we can directly update the UI. We use call_later to defer to next event loop tick.
        try:
            self.app.call_later(self._update_output, output)
            self._log("Scheduled _update_output via call_later")
        except Exception as e:
            # Silently ignore errors - widget might be unmounting
            self._log(f"ERROR in _handle_output: {e}")
            pass

    def _filter_ansi(self, text: str) -> str:
        """
        Filter out problematic ANSI sequences that don't render well in Textual.

        In pipe mode, Claude outputs clean text with minimal ANSI codes,
        so we only need to filter a few problematic sequences.

        Args:
            text: Raw output with ANSI codes

        Returns:
            Filtered text with problematic codes removed
        """
        # Remove bracketed paste mode sequences (if any)
        text = re.sub(r'\x1b\[\?2026[hl]', '', text)
        text = re.sub(r'\x1b\[\?2004[hl]', '', text)

        # Remove mouse tracking sequences (if any)
        text = re.sub(r'\x1b\[\?1004[hl]', '', text)

        # Remove cursor visibility changes (rare in pipe mode)
        text = re.sub(r'\x1b\[\?25[hl]', '', text)

        # Remove screen manipulation codes (shouldn't appear in pipe mode, but be safe)
        text = re.sub(r'\x1b\[2J', '', text)  # Clear entire screen
        text = re.sub(r'\x1b\[3J', '', text)  # Clear scrollback
        text = re.sub(r'\x1b\[H', '', text)   # Move cursor to home

        # Remove OSC sequences (terminal title, etc)
        text = re.sub(r'\x1b\]0;[^\x07]*\x07', '', text)

        return text

    def _update_output(self, output: str) -> None:
        """
        Update the output widget with new output (called on main thread).

        Args:
            output: Raw terminal output (may contain ANSI codes)
        """
        try:
            self._log(f"_update_output called: {len(output)} bytes")

            # Get the SelectableRichLog widget
            output_widget = self.query_one(f"#output-{self.session_id}", SelectableRichLog)

            # Update counter for debugging
            self._update_count += 1

            # Track last output time for response completion detection
            import time
            self._last_output_time = time.time()

            # Check for completion signal
            if "\x00COMMAND_COMPLETE\x00" in output:
                self._log("Received command complete signal")
                # Add completion message immediately
                self._add_completion_message()
                return

            # Filter problematic ANSI sequences
            filtered_output = self._filter_ansi(output)
            self._log(f"After filter: {len(filtered_output)} bytes, empty={not filtered_output.strip()}")

            # Skip empty output after filtering
            if not filtered_output.strip():
                self._log("Skipping empty output")
                return

            # Update token count (rough estimate: 4 chars per token)
            self._token_count += len(filtered_output) // 4

            # Extract status information from output for real-time feedback
            status = self._extract_status_from_output(filtered_output)
            if status and status != self._current_status:
                self._current_status = status
                self._status_history.append(status)
                self._log(f"Status update: {status}")

            # Clear processing indicator on first real output
            if hasattr(self, '_has_processing_indicator') and self._has_processing_indicator:
                # Hide the inline processing indicator
                processing_widget = self.query_one(f"#processing-inline-{self.session_id}", Static)
                processing_widget.remove_class("visible")
                processing_widget.display = False
                self._has_processing_indicator = False

                # Add newline to move response text to next line
                output_widget.write(Text("\n"))
                self._log("Cleared processing indicator and added newline")

            # Convert ANSI codes to Rich Text for proper rendering
            # This handles colors, styles, and formatting from Claude's output
            rich_text = Text.from_ansi(filtered_output)
            self._log(f"Converted to Rich Text: {len(rich_text.plain)} plain chars")

            # Check if this contains Claude's completion text (✻ Completed/Finished/etc)
            completion_patterns = ["✻ Completed", "✻ Finished", "✻ Done", "✻ Processed"]
            has_completion = any(pattern in filtered_output for pattern in completion_patterns)

            # Write the Rich Text to SelectableRichLog
            output_widget.write(rich_text)
            self._log(f"Written to SelectableRichLog, total lines: {len(output_widget.lines)}")

            # Force the widget to update its virtual display
            output_widget.refresh(layout=True)
            self._log("Refreshed with layout=True")

            # Scroll to end is now handled by SelectableRichLog.write() override
            # which respects auto_scroll_enabled state
            self._log(f"Current scroll_y={output_widget.scroll_y}")

            # Additional refresh after scrolling
            output_widget.refresh()

            # Update session name to show activity
            self.session_name = f"Session [{self._update_count} updates]"
            self._log(f"Update complete, count: {self._update_count}")

            # Don't schedule timer anymore - we use COMMAND_COMPLETE signal instead

        except Exception as e:
            # Widget might not be ready yet or might be removed
            self._log(f"ERROR in _update_output: {e}")
            pass

    def _animate_processing(self) -> None:
        """Animate the processing indicator with braille animations, plus real-time metrics."""
        try:
            # Stop if processing is done
            if not hasattr(self, '_has_processing_indicator') or not self._has_processing_indicator:
                return

            processing_widget = self.query_one(f"#processing-inline-{self.session_id}", Static)

            # Increment frame
            self._animation_frame += 1

            # Switch animation type every 60 frames (12 seconds at 0.2s per frame)
            if self._animation_frame % 60 == 0:
                self._current_animation_idx = (self._current_animation_idx + 1) % len(self._animation_types)

            # Get current animation
            current_anim_type = self._animation_types[self._current_animation_idx]
            current_anim_name = self._animation_names[self._current_animation_idx]
            current_anim_color = self._animation_colors[self._current_animation_idx]
            animation_frames = self._animations[current_anim_type]

            # Get current frame from the animation
            frame_idx = self._animation_frame % len(animation_frames)
            braille_frame = animation_frames[frame_idx]

            # Calculate real-time metrics
            import time
            elapsed = time.time() - self._processing_start_time

            # Format elapsed time
            if elapsed < 60:
                time_str = f"{int(elapsed)}s"
            else:
                mins = int(elapsed / 60)
                secs = int(elapsed % 60)
                time_str = f"{mins}m {secs}s"

            # Format token count
            if self._token_count < 1000:
                token_str = f"{self._token_count}"
            else:
                token_k = self._token_count / 1000
                token_str = f"{token_k:.1f}k"

            # Calculate tokens per second for streaming feedback
            if elapsed > 0:
                tps = self._token_count / elapsed
                tps_str = f"{tps:.1f}/s"
            else:
                tps_str = "0/s"

            # Add streaming indicator with animated cursor
            cursor_frames = ["▌", "▐", "▌", " "]
            cursor = cursor_frames[self._animation_frame % len(cursor_frames)]

            # Get current status or fall back to animation name
            display_status = self._current_status if hasattr(self, '_current_status') else current_anim_name

            # Update the processing widget with animation + metrics
            animation_text = Text()
            animation_text.append(braille_frame, style=current_anim_color)  # Braille animation
            animation_text.append(" ", style="")
            animation_text.append(display_status, style="bold yellow")  # Real-time status
            animation_text.append(f" {cursor}", style="bold bright_cyan")  # Streaming cursor

            # Add metrics (not animated, just updated)
            animation_text.append(" (", style="dim white")
            animation_text.append(time_str, style="dim cyan")
            animation_text.append(" · ", style="dim white")
            animation_text.append("↓ ", style="dim white")
            animation_text.append(f"{token_str}", style="dim cyan")
            animation_text.append(" @ ", style="dim white")
            animation_text.append(tps_str, style="dim green")
            animation_text.append(")", style="dim white")

            processing_widget.update(animation_text)
            processing_widget.refresh()

            # Schedule next frame (every 0.2s for smoother animation)
            if hasattr(self, 'app') and self.app:
                self.app.set_timer(0.2, self._animate_processing)

        except Exception as e:
            self._log(f"Error in animation: {e}")

    def _show_autocomplete(self, filter_text: str = "") -> None:
        """
        Show the autocomplete dropdown with filtered commands.

        Args:
            filter_text: Text to filter commands (e.g., "/m" shows commands starting with "/m")
        """
        try:
            dropdown = self.query_one(f"#autocomplete-{self.session_id}", Vertical)
            option_list = self.query_one(f"#autocomplete-list-{self.session_id}", OptionList)

            # Filter commands based on input
            filter_text = filter_text.lower()
            filtered_commands = [
                (cmd, desc) for cmd, desc in self._slash_commands
                if cmd.lower().startswith(filter_text)
            ]

            # If no matches, hide dropdown
            if not filtered_commands:
                self._hide_autocomplete()
                return

            # Clear existing options
            option_list.clear_options()

            # Add filtered options with rich formatting
            for cmd, desc in filtered_commands:
                option_text = Text()
                option_text.append(cmd, style="bold rgb(255,100,100)")
                option_text.append("  ", style="")
                option_text.append(desc, style="dim rgb(180,180,180)")
                option_list.add_option(Option(option_text, id=cmd))

            # Show dropdown and mark as visible
            dropdown.add_class("visible")
            dropdown.display = True
            self._autocomplete_visible = True

            # Highlight first option
            if len(option_list._options) > 0:
                option_list.highlighted = 0

        except Exception as e:
            self._log(f"Error showing autocomplete: {e}")

    def _hide_autocomplete(self) -> None:
        """Hide the autocomplete dropdown."""
        try:
            dropdown = self.query_one(f"#autocomplete-{self.session_id}", Vertical)
            dropdown.remove_class("visible")
            dropdown.display = False
            self._autocomplete_visible = False
        except Exception as e:
            self._log(f"Error hiding autocomplete: {e}")

    def _get_selected_command(self) -> str:
        """
        Get the currently selected command from autocomplete.

        Returns:
            The selected command text (e.g., "/model")
        """
        try:
            option_list = self.query_one(f"#autocomplete-list-{self.session_id}", OptionList)
            if option_list.highlighted is not None:
                option = option_list.get_option_at_index(option_list.highlighted)
                return option.id or ""
        except Exception:
            pass
        return ""

    @on(TextArea.Changed)
    def on_input_changed(self, event: TextArea.Changed) -> None:
        """
        Handle input field changes to show/hide autocomplete.

        Args:
            event: TextArea changed event
        """
        # Only handle events from this session's input
        if event.text_area.id != f"input-{self.session_id}":
            return

        value = event.text_area.text

        # Show autocomplete when "/" is typed
        if value.startswith("/") and not value.startswith("//"):
            self._show_autocomplete(value)
        else:
            self._hide_autocomplete()

    @on(CommandTextArea.Submitted)
    async def on_command_submitted(self, event: CommandTextArea.Submitted) -> None:
        """
        Handle command submission from CommandTextArea.

        Args:
            event: Submitted event from CommandTextArea
        """
        # Only handle events from this session's input
        if event.text_area.id != f"input-{self.session_id}":
            return

        # If autocomplete is visible, don't submit - let autocomplete handle it
        if self._autocomplete_visible:
            # The Enter key should select from autocomplete, not submit
            selected = self._get_selected_command()
            if selected:
                # Fill input with selected command and add a space
                event.text_area.text = selected + " "
                # Move cursor to end
                event.text_area.move_cursor((0, len(event.text_area.text)))
                self._hide_autocomplete()
            return

        command = event.text
        await self._submit_command(command, event.text_area)

    async def on_key(self, event: events.Key) -> None:
        """
        Handle key events for autocomplete navigation and command cancellation.

        Args:
            event: Key event
        """
        input_widget = self.query_one(f"#input-{self.session_id}", CommandTextArea)

        # Handle Ctrl+C for cancelling running command (when not in input)
        if event.key == "ctrl+c" and not input_widget.has_focus:
            # Cancel the currently running command
            if hasattr(self, '_has_processing_indicator') and self._has_processing_indicator:
                await self._cancel_current_command()
                event.prevent_default()
                event.stop()
                return

        # Only handle autocomplete keys when autocomplete is visible and input is focused
        if not self._autocomplete_visible:
            return

        if not input_widget.has_focus:
            return

        option_list = self.query_one(f"#autocomplete-list-{self.session_id}", OptionList)

        if event.key == "up":
            # Navigate up in autocomplete list
            if option_list.highlighted is not None and option_list.highlighted > 0:
                option_list.highlighted -= 1
            event.prevent_default()
            event.stop()

        elif event.key == "down":
            # Navigate down in autocomplete list
            if option_list.highlighted is not None:
                max_index = len(option_list._options) - 1
                if option_list.highlighted < max_index:
                    option_list.highlighted += 1
            event.prevent_default()
            event.stop()

        elif event.key in ("enter", "tab"):
            # Select the highlighted command
            selected = self._get_selected_command()
            if selected:
                # Fill input with selected command and add a space
                input_widget.text = selected + " "
                # Move cursor to end
                input_widget.move_cursor((0, len(input_widget.text)))
                self._hide_autocomplete()
                event.prevent_default()
                event.stop()

        elif event.key == "escape":
            # Hide autocomplete on Escape
            self._hide_autocomplete()
            event.prevent_default()
            event.stop()

    @on(OptionList.OptionSelected)
    def on_option_selected(self, event: OptionList.OptionSelected) -> None:
        """
        Handle option selection from autocomplete dropdown.

        Args:
            event: Option selected event
        """
        # Only handle events from this session's autocomplete
        if event.option_list.id != f"autocomplete-list-{self.session_id}":
            return

        # Fill input with selected command
        input_widget = self.query_one(f"#input-{self.session_id}", CommandTextArea)
        if event.option.id:
            input_widget.text = event.option.id + " "
            input_widget.move_cursor((0, len(input_widget.text)))
            self._hide_autocomplete()
            input_widget.focus()

        event.stop()

    async def _cancel_current_command(self) -> None:
        """Cancel the currently executing command."""
        self._log("Cancelling current command")

        # Get session and cancel command
        session = self.session_manager.sessions.get(self.session_id)
        if session:
            await session.pty_handler.cancel_current_command()

        # Hide processing indicator
        if hasattr(self, '_has_processing_indicator') and self._has_processing_indicator:
            processing_widget = self.query_one(f"#processing-inline-{self.session_id}", Static)
            processing_widget.remove_class("visible")
            processing_widget.display = False
            self._has_processing_indicator = False

        # Add cancellation message to output
        output_widget = self.query_one(f"#output-{self.session_id}", SelectableRichLog)
        cancel_msg = Text()
        cancel_msg.append("\n⚠️  ", style="bold yellow")
        cancel_msg.append("Command cancelled by user (Ctrl+C)", style="dim yellow")
        cancel_msg.append("\n\n", style="")
        output_widget.write(cancel_msg)
        # Scroll handled by write() override
        output_widget.refresh()

        # Mark as inactive
        self.is_active = False

    def _add_completion_message(self) -> None:
        """Add completion message after response is complete."""
        import time
        import random

        self._log("Adding completion message")
        try:
            # Hide processing indicator
            if hasattr(self, '_has_processing_indicator') and self._has_processing_indicator:
                processing_widget = self.query_one(f"#processing-inline-{self.session_id}", Static)
                processing_widget.remove_class("visible")
                processing_widget.display = False
                self._has_processing_indicator = False

            output_widget = self.query_one(f"#output-{self.session_id}", SelectableRichLog)

            # Check if Claude already provided a completion message
            recent_text = "\n".join([str(line) for line in output_widget.lines[-5:]])
            has_claude_completion = "✻" in recent_text or "Completed" in recent_text or "Finished" in recent_text or "Done" in recent_text or "Processed" in recent_text

            if not has_claude_completion:
                # Calculate elapsed time
                elapsed = time.time() - self._processing_start_time if hasattr(self, '_processing_start_time') else 0

                # Format elapsed time
                if elapsed < 60:
                    time_str = f"{int(elapsed)}s"
                else:
                    mins = int(elapsed / 60)
                    secs = int(elapsed % 60)
                    time_str = f"{mins}m {secs}s"

                # Choose a random completion verb
                completion_verbs = ["Completed", "Finished", "Done", "Processed"]
                verb = random.choice(completion_verbs)

                end_marker = Text()
                end_marker.append("\n", style="")
                end_marker.append("✻ ", style="bold bright_cyan")
                end_marker.append(f"{verb} in {time_str}", style="dim white")

                # Add status summary if we tracked any steps
                if hasattr(self, '_status_history') and len(self._status_history) > 1:
                    end_marker.append(" • ", style="dim white")
                    end_marker.append(f"{len(self._status_history)} steps", style="dim cyan")

                end_marker.append("\n\n", style="")
                output_widget.write(end_marker)
                # Scroll handled by write() override
                output_widget.refresh()

            self._last_command = None  # Clear so we don't add multiple markers
            self.is_active = False  # Mark as inactive

        except Exception as e:
            self._log(f"Error adding completion message: {e}")

    async def _submit_command(self, command: str, input_widget: CommandTextArea) -> None:
        """
        Handle user command submission.

        Args:
            command: The command text to submit
            input_widget: The CommandTextArea widget to clear after submission
        """
        self._log(f"_submit_command: command='{command}'")

        # Check if app is in broadcast mode - let app handle it
        if hasattr(self.app, 'broadcast_mode') and self.app.broadcast_mode:
            self._log("In broadcast mode, letting app handle it")
            return

        if not command.strip():
            self._log("Empty command, skipping")
            return

        # Handle /search command locally (don't send to Claude)
        if command.strip() == '/search':
            # Clear input field
            input_widget.text = ""

            # Trigger search panel
            if hasattr(self.app, 'action_toggle_search'):
                await self.app.action_toggle_search()
            else:
                self.app.notify("Search not available", severity="warning")

            return

        # Handle /export command locally (don't send to Claude)
        if command.strip().startswith('/export'):
            parts = command.strip().split(maxsplit=2)
            format_type = "markdown"  # default
            filename = None

            if len(parts) >= 2:
                format_type = parts[1].lower()
            if len(parts) >= 3:
                filename = parts[2]

            # Clear input field
            input_widget.text = ""

            # Execute export
            await self.export_session(format_type=format_type, filename=filename)

            return

        # Update metrics
        self.command_count += 1
        self.is_active = True

        # Add visual separator before sending command
        output_widget = self.query_one(f"#output-{self.session_id}", SelectableRichLog)

        # Create enterprise-grade visual separator with command echo
        import datetime
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        separator = Text()
        separator.append("\n\n", style="")
        separator.append("╔" + "═" * 78 + "╗\n", style="bold rgb(100,180,255)")
        separator.append("║ ", style="bold rgb(100,180,255)")
        separator.append(f"⏱ {timestamp} ", style="dim cyan")
        separator.append("┊ ", style="dim white")
        separator.append("⚡ Command: ", style="bold rgb(150,220,255)")
        separator.append(command, style="bold rgb(255,220,100)")
        # Pad to fill the box
        padding = 78 - len(f"⏱ {timestamp} ┊ ⚡ Command: {command}") - 2
        if padding > 0:
            separator.append(" " * padding, style="")
        separator.append(" ║\n", style="bold rgb(100,180,255)")
        separator.append("╚" + "═" * 78 + "╝\n", style="bold rgb(100,180,255)")
        separator.append("\n📝 Response: ", style="bold rgb(150,255,150)")  # NO newline after colon!

        output_widget.write(separator)
        # Scroll handled by write() override
        output_widget.refresh()
        self._log("Added visual separator")

        # Show and animate inline processing indicator
        processing_widget = self.query_one(f"#processing-inline-{self.session_id}", Static)
        processing_widget.display = True
        processing_widget.add_class("visible")

        # Initialize animation state and reset metrics
        self._processing_start_time = __import__('time').time()
        self._token_count = 0  # Reset token count for new command
        self._thinking_time = 0  # Reset thinking time
        self._has_processing_indicator = True
        self._animation_frame = 0

        # Generate braille animation frames
        self._animations = {
            'pendulum': gen_pendulum(10, 1.0),
            'compress': gen_compress(10),
            'sort': gen_sort(10)
        }
        self._animation_names = ['Pendulum', 'Compress', 'Sort']
        self._animation_types = ['pendulum', 'compress', 'sort']
        self._animation_colors = ['rgb(250,204,21)', 'rgb(248,113,113)', 'rgb(96,165,250)']  # Yellow, Red, Blue
        self._current_animation_idx = 0

        # Initialize status for this command
        self._current_status = "Sending to Claude..."
        self._status_history.clear()
        self._status_history.append(self._current_status)

        # Start with initial frame with metrics
        initial_text = Text()
        initial_text.append(self._animations['pendulum'][0], style=self._animation_colors[0])
        initial_text.append(" ", style="")
        initial_text.append(self._current_status, style="bold yellow")
        initial_text.append(" ▌", style="bold bright_cyan")  # Streaming cursor
        initial_text.append(" (0s · ↓ 0 @ 0/s)", style="dim white")
        processing_widget.update(initial_text)

        # Start animation (every 0.2s for smooth streaming)
        if hasattr(self, 'app') and self.app:
            self.app.set_timer(0.2, self._animate_processing)

        # Store command for tracking
        self._last_command = command

        # Get session and write to PTY
        session = self.session_manager.sessions.get(self.session_id)

        if session:
            self._log(f"Writing to PTY: '{command}\\n'")
            # Add newline for command submission
            await session.pty_handler.write(command + "\n")
            self._log("Write complete")
        else:
            self._log("ERROR: No session found!")
            # Show error in output
            error_text = Text()
            error_text.append("❌ ERROR: ", style="bold red")
            error_text.append("No session found!", style="red")
            output_widget.write(error_text)

        # Clear input field
        input_widget.text = ""

    def watch_session_name(self, new_name: str) -> None:
        """React to session name changes."""
        if not self.is_mounted:
            return
        try:
            header = self.query_one(f"#header-{self.session_id}", Static)
            header.update(self._render_header())
        except Exception:
            # Widget not ready yet
            pass

    def watch_is_active(self, is_active: bool) -> None:
        """React to activity state changes."""
        if not self.is_mounted:
            return
        try:
            header = self.query_one(f"#header-{self.session_id}", Static)
            header.update(self._render_header())
        except Exception:
            pass

    def watch_command_count(self, count: int) -> None:
        """React to command count changes."""
        if not self.is_mounted:
            return
        try:
            header = self.query_one(f"#header-{self.session_id}", Static)
            header.update(self._render_header())
        except Exception:
            pass

    def get_output_text(self) -> str:
        """
        Extract plain text from terminal output for copying.

        Returns:
            Plain text content without ANSI codes
        """
        try:
            rich_log = self.query_one(f"#output-{self.session_id}", SelectableRichLog)
            # SelectableRichLog stores lines, extract plain text from each
            lines = []
            for line in rich_log.lines:
                # Each line is a Strip object containing Segment objects
                # Extract text from each segment
                line_text = "".join(segment.text for segment in line._segments)
                lines.append(line_text)
            return "\n".join(lines)
        except Exception:
            # Fallback: return empty string if extraction fails
            return ""

    async def export_session(self, format_type: str = "markdown", filename: str = None) -> None:
        """
        Export session transcript to file.

        Args:
            format_type: Export format ('markdown', 'json', or 'text')
            filename: Optional custom filename (without extension)
        """
        try:
            # Get raw transcript text
            raw_text = self.get_output_text()

            if not raw_text.strip():
                if hasattr(self.app, 'notify'):
                    self.app.notify(
                        "No conversation to export",
                        severity="warning"
                    )
                return

            # Sanitize session name for filename
            safe_name = sanitize_filename(self.session_name)

            # Parse and export based on format
            if format_type.lower() == "markdown":
                messages = self._exporter.parse_transcript(raw_text)
                filepath = self._exporter.export_to_markdown(
                    messages=messages,
                    session_name=safe_name,
                    filename=filename
                )
                if hasattr(self.app, 'notify'):
                    self.app.notify(
                        f"✓ Exported to Markdown: {filepath}",
                        severity="information",
                        timeout=6
                    )

            elif format_type.lower() == "json":
                messages = self._exporter.parse_transcript(raw_text)
                filepath = self._exporter.export_to_json(
                    messages=messages,
                    session_name=safe_name,
                    session_id=self.session_id,
                    filename=filename,
                    metadata={
                        "command_count": self.command_count,
                        "is_active": self.is_active
                    }
                )
                if hasattr(self.app, 'notify'):
                    self.app.notify(
                        f"✓ Exported to JSON: {filepath}",
                        severity="information",
                        timeout=6
                    )

            elif format_type.lower() == "text":
                filepath = self._exporter.export_raw_text(
                    raw_text=raw_text,
                    session_name=safe_name,
                    filename=filename
                )
                if hasattr(self.app, 'notify'):
                    self.app.notify(
                        f"✓ Exported to text: {filepath}",
                        severity="information",
                        timeout=6
                    )

            else:
                if hasattr(self.app, 'notify'):
                    self.app.notify(
                        f"Unknown export format: {format_type}. Use 'markdown', 'json', or 'text'",
                        severity="error"
                    )

        except Exception as e:
            if hasattr(self.app, 'notify'):
                self.app.notify(
                    f"Export failed: {str(e)}",
                    severity="error"
                )
