"""Status bar widget showing keybindings and current mode."""

from textual.widgets import Static
from textual.reactive import reactive
from rich.text import Text
import psutil
import platform

from ..types import AppMode
from ..core.modes import get_mode_config


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
