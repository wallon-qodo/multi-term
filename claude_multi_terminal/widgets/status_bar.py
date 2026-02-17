"""Status bar widget showing keybindings and current mode."""

from textual.widgets import Static
from textual.reactive import reactive
from rich.text import Text
import psutil
import platform
from datetime import datetime
from enum import Enum

from ..types import AppMode
from ..core.modes import get_mode_config

# Streaming state enum (will be imported from stream_monitor once available)
class StreamState(Enum):
    """Streaming state for status display."""
    IDLE = "idle"
    CONNECTING = "connecting"
    STREAMING = "streaming"
    COMPLETE = "complete"
    ERROR = "error"


class StatusBar(Static):
    """Bottom status bar showing current state and key bindings."""

    DEFAULT_CSS = """
    StatusBar {
        dock: bottom;
        background: rgb(26,26,26);
        color: rgb(240,240,240);
        height: 3;
        padding: 0 2;
        border-top: heavy rgb(42,42,42);
    }

    StatusBar.-broadcast {
        background: rgb(50,20,20);
        border-top: heavy rgb(255,77,77);
    }

    StatusBar.-mode-normal {
        border-top: heavy rgb(100,180,240);
    }

    StatusBar.-mode-insert {
        border-top: heavy rgb(120,200,120);
    }

    StatusBar.-mode-copy {
        border-top: heavy rgb(255,180,70);
    }

    StatusBar.-mode-command {
        border-top: heavy rgb(255,77,77);
    }
    """

    broadcast_mode = reactive(False)
    current_mode = reactive(AppMode.NORMAL)

    # Streaming state reactive properties
    stream_state = reactive(StreamState.IDLE)
    streaming_speed = reactive(0.0)  # tokens/sec
    streaming_tokens = reactive(0)  # current stream token count

    # Token tracking reactive properties
    session_tokens = reactive(0)  # total tokens this session
    session_cost = reactive(0.0)  # total cost in USD

    # Model information
    model_name = reactive("claude-sonnet-4.5")

    # Internal state for animations
    _spinner_frame = 0
    _spinner_chars = "⠋⠙⠹⠸⠼⠴⠦⠧⠇⠏"
    _last_complete_time = None

    def watch_broadcast_mode(self, is_broadcasting: bool) -> None:
        """Update styling when broadcast mode changes."""
        self.set_class(is_broadcasting, "-broadcast")

    def watch_current_mode(self, mode: AppMode) -> None:
        """Update styling when mode changes."""
        # Remove all mode classes
        for m in AppMode:
            self.set_class(False, f"-mode-{m.value}")
        # Add current mode class
        self.set_class(True, f"-mode-{mode.value}")

    def watch_stream_state(self, new_state: StreamState) -> None:
        """React to streaming state changes."""
        if new_state == StreamState.COMPLETE:
            self._last_complete_time = datetime.now()
            # Schedule a refresh in 2 seconds to fade out the indicator
            self.set_timer(2.0, self.refresh)
        elif new_state == StreamState.STREAMING:
            # Start spinner animation at 10fps
            self.set_interval(0.1, self._update_spinner)
        self.refresh()

    def _update_spinner(self) -> None:
        """Update spinner animation frame."""
        if self.stream_state == StreamState.STREAMING:
            self._spinner_frame = (self._spinner_frame + 1) % len(self._spinner_chars)
            self.refresh()

    def update_streaming_state(self, state: StreamState, speed: float = 0.0, tokens: int = 0) -> None:
        """Update streaming indicator.

        Args:
            state: Current streaming state
            speed: Streaming speed in tokens/sec
            tokens: Number of tokens streamed so far
        """
        self.stream_state = state
        self.streaming_speed = speed
        self.streaming_tokens = tokens

    def update_token_usage(self, tokens: int, cost: float) -> None:
        """Update token usage display.

        Args:
            tokens: Total tokens used this session
            cost: Total cost in USD
        """
        self.session_tokens = tokens
        self.session_cost = cost

    def update_model(self, model_name: str) -> None:
        """Update model name display.

        Args:
            model_name: Full model name (e.g., "claude-sonnet-4-5")
        """
        self.model_name = model_name

    def _get_short_model_name(self) -> str:
        """Convert full model name to short display name."""
        name_map = {
            "claude-opus-4-6": "Opus 4.6",
            "claude-opus-4.6": "Opus 4.6",
            "claude-sonnet-4-5": "Sonnet 4.5",
            "claude-sonnet-4.5": "Sonnet 4.5",
            "claude-haiku-4-5": "Haiku 4.5",
            "claude-haiku-4.5": "Haiku 4.5",
        }
        return name_map.get(self.model_name, self.model_name)

    def _format_token_count(self, tokens: int) -> str:
        """Format token count with K suffix for thousands."""
        if tokens >= 1000:
            return f"{tokens / 1000:.1f}K"
        return str(tokens)

    def _get_cost_color(self, cost: float) -> str:
        """Get color for cost display based on amount."""
        if cost < 0.10:
            return "rgb(120,200,120)"  # Green
        elif cost < 1.00:
            return "rgb(255,180,70)"   # Yellow
        else:
            return "rgb(255,77,77)"     # Red

    def render(self) -> Text:
        """Render status bar content with system metrics."""
        text = Text()

        # Get current mode configuration
        mode_config = get_mode_config(self.current_mode)

        # Line 1: Mode indicator on the left
        text.append("┃", style=f"bold {mode_config.color}")
        text.append(f" {mode_config.icon} {mode_config.description.upper()} ",
                   style=f"bold {mode_config.color}")
        text.append("┃", style=f"bold {mode_config.color}")

        # Streaming indicator (show when active or recently completed)
        show_streaming = False
        if self.stream_state != StreamState.IDLE:
            if self.stream_state != StreamState.COMPLETE:
                show_streaming = True
            elif self._last_complete_time:
                # Show for 2 seconds after completion
                elapsed = (datetime.now() - self._last_complete_time).total_seconds()
                show_streaming = elapsed < 2.0

        if show_streaming:
            text.append("  ", style="rgb(120,120,120)")
            spinner = self._spinner_chars[self._spinner_frame]
            text.append(spinner, style="bold rgb(100,180,240)")
            text.append(f" {self.streaming_tokens} tok", style="rgb(180,180,180)")
            if self.streaming_speed > 0:
                text.append(f" ({self.streaming_speed:.0f} tok/s)", style="rgb(120,120,120)")

        # Model name
        text.append("  ", style="rgb(120,120,120)")
        text.append("┊", style="rgb(60,60,60)")
        text.append("  ", style="rgb(120,120,120)")
        text.append(self._get_short_model_name(), style="bold rgb(255,77,77)")

        # Token usage
        text.append("  ┊  ", style="rgb(60,60,60)")
        tokens_formatted = self._format_token_count(self.session_tokens)
        cost_color = self._get_cost_color(self.session_cost)
        text.append(f"{tokens_formatted} tok", style="rgb(180,180,180)")
        text.append(f" (${self.session_cost:.2f})", style=f"bold {cost_color}")

        # Mode hints (contextual help)
        if mode_config.hints:
            text.append("  ", style="rgb(120,120,120)")
            for i, hint in enumerate(mode_config.hints):
                if i > 0:
                    text.append(" ┊ ", style="rgb(60,60,60)")
                text.append(hint, style="rgb(180,180,180)")

        # Broadcast mode indicator (overrides mode hints if active)
        if self.broadcast_mode:
            text.append("  ", style="rgb(120,120,120)")
            text.append("┃", style="bold rgb(255,77,77)")
            text.append(" 📡 BROADCAST ", style="bold rgb(255,100,100) on rgb(50,20,20)")
            text.append(" ┃", style="bold rgb(255,77,77)")

        # Current time
        current_time = datetime.now().strftime("%H:%M")
        text.append("  ┊  ", style="rgb(60,60,60)")
        text.append(current_time, style="rgb(100,180,240)")

        # System metrics with OpenClaw colors (right side)
        try:
            cpu = psutil.cpu_percent(interval=0)
            mem = psutil.virtual_memory().percent

            text.append("  ", style="rgb(120,120,120)")
            text.append("┊", style="rgb(60,60,60)")
            text.append("  CPU: ", style="rgb(180,180,180)")
            cpu_color = "rgb(120,200,120)" if cpu < 50 else "rgb(255,180,70)" if cpu < 80 else "rgb(255,77,77)"
            text.append(f"{cpu:.0f}%", style=f"bold {cpu_color}")

            text.append("  ┊  MEM: ", style="rgb(180,180,180)")
            mem_color = "rgb(120,200,120)" if mem < 60 else "rgb(255,180,70)" if mem < 80 else "rgb(255,77,77)"
            text.append(f"{mem:.0f}%", style=f"bold {mem_color}")

            text.append(f"  ┊  {platform.system()}", style="rgb(100,180,240)")
        except:
            pass

        text.append("\n")

        # Line 2: Mode-specific keybindings
        if self.current_mode == AppMode.NORMAL:
            bindings = [
                ("i", "Insert", "rgb(120,200,120)"),
                ("v", "Copy", "rgb(255,180,70)"),
                ("^B", "Command", "rgb(255,77,77)"),
                ("n", "New", "rgb(100,180,240)"),
                ("x", "Close", "rgb(255,77,77)"),
                ("h/j/k/l", "Navigate", "rgb(100,180,240)"),
                ("r", "Rename", "rgb(255,180,70)"),
                ("q", "Quit", "rgb(255,77,77)"),
            ]
        elif self.current_mode == AppMode.INSERT:
            bindings = [
                ("ESC", "Normal", "rgb(100,180,240)"),
                ("Type", "Input to session", "rgb(120,200,120)"),
                ("Enter", "Submit", "rgb(120,200,120)"),
                ("Shift+Enter", "Newline", "rgb(180,180,180)"),
            ]
        elif self.current_mode == AppMode.COPY:
            bindings = [
                ("ESC", "Normal", "rgb(100,180,240)"),
                ("j/k", "Scroll", "rgb(255,180,70)"),
                ("d/u", "Half Page", "rgb(255,180,70)"),
                ("f/b", "Full Page", "rgb(255,180,70)"),
                ("g/G", "Top/Bottom", "rgb(255,180,70)"),
                ("y", "Yank", "rgb(120,200,120)"),
            ]
        elif self.current_mode == AppMode.COMMAND:
            bindings = [
                ("ESC", "Cancel", "rgb(100,180,240)"),
                ("c", "New", "rgb(100,180,240)"),
                ("x", "Close", "rgb(255,77,77)"),
                ("n/p", "Next/Prev", "rgb(100,180,240)"),
                ("[", "Copy mode", "rgb(255,180,70)"),
                ("r", "Rename", "rgb(255,180,70)"),
            ]
        else:
            # Fallback to default bindings
            bindings = [
                ("^N", "New", "rgb(100,180,240)"),
                ("^W", "Close", "rgb(255,77,77)"),
                ("^S", "Save", "rgb(120,200,120)"),
                ("^R", "Rename", "rgb(255,180,70)"),
                ("^B", "Broadcast", "rgb(255,77,77)"),
                ("^C", "Copy", "rgb(220,150,220)"),
                ("Tab", "Next", "rgb(100,180,240)"),
                ("^Q", "Quit", "rgb(255,77,77)"),
            ]

        for i, (key, action, color) in enumerate(bindings):
            if i > 0:
                text.append(" ┊ ", style="rgb(60,60,60)")
            text.append(key, style=f"bold {color}")
            text.append(f":{action}", style="rgb(180,180,180)")

        return text
