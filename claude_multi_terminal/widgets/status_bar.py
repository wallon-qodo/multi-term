"""Status bar widget showing keybindings and current mode."""

from textual.widgets import Static
from textual.reactive import reactive
from rich.text import Text
import psutil
import platform


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
    """

    broadcast_mode = reactive(False)

    def watch_broadcast_mode(self, is_broadcasting: bool) -> None:
        """Update styling when broadcast mode changes."""
        self.set_class(is_broadcasting, "-broadcast")

    def render(self) -> Text:
        """Render status bar content with system metrics."""
        text = Text()

        # Line 1: Mode indicator with OpenClaw colors
        if self.broadcast_mode:
            text.append("┃", style="bold rgb(255,77,77)")
            text.append(" 📡 BROADCAST MODE ACTIVE ", style="bold rgb(255,100,100) on rgb(50,20,20)")
            text.append(" ┃", style="bold rgb(255,77,77)")
            text.append(" Commands sent to ALL sessions ", style="italic rgb(255,100,100)")
        else:
            text.append("┃", style="rgb(120,120,120)")
            text.append(" Ready ", style="bold rgb(120,200,120)")
            text.append("┃", style="rgb(120,120,120)")

            # System metrics with OpenClaw colors
            try:
                cpu = psutil.cpu_percent(interval=0)
                mem = psutil.virtual_memory().percent

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

        # Line 2: Keybindings with OpenClaw styling
        bindings = [
            ("^N", "New", "rgb(100,180,240)"),
            ("^W", "Close", "rgb(255,77,77)"),
            ("^S", "Save", "rgb(120,200,120)"),
            ("^R", "Rename", "rgb(255,180,70)"),
            ("^B", "Broadcast", "rgb(255,77,77)"),
            ("^C", "Copy", "rgb(220,150,220)"),
            ("F2", "Mouse", "rgb(120,220,230)"),
            ("Tab", "Next", "rgb(100,180,240)"),
            ("^Q", "Quit", "rgb(255,77,77)"),
        ]

        for i, (key, action, color) in enumerate(bindings):
            if i > 0:
                text.append(" ┊ ", style="rgb(60,60,60)")
            text.append(key, style=f"bold {color}")
            text.append(f":{action}", style="rgb(180,180,180)")

        return text
