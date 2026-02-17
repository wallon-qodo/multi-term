# Mode Display - Key Code Samples

## 1. Mode Configuration (modes.py)

```python
"""Mode definitions and color mappings for the application."""

from ..types import AppMode
from dataclasses import dataclass


@dataclass
class ModeConfig:
    """Configuration for a specific mode including colors and icons."""
    color: str
    icon: str
    description: str
    hints: list[str]


# Mode color and icon mappings
MODE_CONFIGS = {
    AppMode.NORMAL: ModeConfig(
        color="rgb(100,180,240)",  # Blue
        icon="⌘",
        description="Normal",
        hints=["i:Insert", "v:Copy", "Ctrl+B:Command"]
    ),
    AppMode.INSERT: ModeConfig(
        color="rgb(120,200,120)",  # Green
        icon="✎",
        description="Insert",
        hints=["ESC:Normal", "Type to input"]
    ),
    AppMode.COPY: ModeConfig(
        color="rgb(255,180,70)",   # Yellow
        icon="📋",
        description="Copy",
        hints=["ESC:Normal", "y:Yank", "Arrow:Navigate"]
    ),
    AppMode.COMMAND: ModeConfig(
        color="rgb(255,77,77)",    # Coral
        icon="⚡",
        description="Command",
        hints=["ESC:Cancel", "Enter key binding"]
    ),
}


def get_mode_config(mode: AppMode) -> ModeConfig:
    """Get the configuration for a given mode."""
    return MODE_CONFIGS.get(mode, MODE_CONFIGS[AppMode.NORMAL])
```

## 2. StatusBar Updates (status_bar.py)

### Imports
```python
from textual.widgets import Static
from textual.reactive import reactive
from rich.text import Text
import psutil
import platform

from ..types import AppMode
from ..core.modes import get_mode_config
```

### Class Definition with Reactive Properties
```python
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
```

### Reactive Watcher
```python
    def watch_current_mode(self, mode: AppMode) -> None:
        """Update styling when mode changes."""
        # Remove all mode classes
        for m in AppMode:
            self.set_class(False, f"-mode-{m.value}")
        # Add current mode class
        self.set_class(True, f"-mode-{mode.value}")
```

### Render Method (Key Parts)
```python
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

        # Broadcast mode indicator (if active)
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

        # Line 2: Keybindings (unchanged from original)
        # ... keybinding display code ...

        return text
```

## 3. App Integration (app.py)

### Mode Transition Methods
```python
    # Modal System - Mode Transition Methods
    def enter_normal_mode(self) -> None:
        """Enter NORMAL mode - window management and navigation."""
        self.mode = AppMode.NORMAL
        self.command_prefix_active = False
        status_bar = self.query_one(StatusBar)
        status_bar.current_mode = AppMode.NORMAL
        self.notify("Mode: NORMAL", severity="information", timeout=1)

    def enter_insert_mode(self) -> None:
        """Enter INSERT mode - all keys forwarded to active session."""
        self.mode = AppMode.INSERT
        self.command_prefix_active = False
        status_bar = self.query_one(StatusBar)
        status_bar.current_mode = AppMode.INSERT
        self.notify("Mode: INSERT", severity="information", timeout=1)

    def enter_copy_mode(self) -> None:
        """Enter COPY mode - scrollback navigation and text selection."""
        self.mode = AppMode.COPY
        self.command_prefix_active = False
        status_bar = self.query_one(StatusBar)
        status_bar.current_mode = AppMode.COPY
        self.notify("Mode: COPY (scrollback navigation)", severity="information", timeout=2)

    def enter_command_mode(self) -> None:
        """Enter COMMAND mode - prefix key mode (Ctrl+B then action)."""
        self.mode = AppMode.COMMAND
        self.command_prefix_active = True
        status_bar = self.query_one(StatusBar)
        status_bar.current_mode = AppMode.COMMAND
        self.notify("Mode: COMMAND (awaiting command)", severity="information", timeout=2)
```

### Initialization in on_mount
```python
    async def on_mount(self) -> None:
        """Initialize the application with default sessions or restore workspace."""
        # ... session initialization code ...

        # Initialize status bar with current mode
        status_bar = self.query_one(StatusBar)
        status_bar.current_mode = self.mode

        # ... rest of initialization ...
```

## 4. Test Application (test_mode_display.py)

```python
#!/usr/bin/env python3
"""Test the mode display in the StatusBar."""

from textual.app import App, ComposeResult
from claude_multi_terminal.widgets.status_bar import StatusBar
from claude_multi_terminal.types import AppMode
import asyncio


class TestModeApp(App):
    """Test app to cycle through modes."""

    def compose(self) -> ComposeResult:
        """Create the layout."""
        yield StatusBar()

    async def on_mount(self) -> None:
        """Cycle through modes for testing."""
        status_bar = self.query_one(StatusBar)

        modes = [
            (AppMode.NORMAL, "Normal mode - window management"),
            (AppMode.INSERT, "Insert mode - typing"),
            (AppMode.COPY, "Copy mode - text selection"),
            (AppMode.COMMAND, "Command mode - prefix key"),
        ]

        for mode, description in modes:
            status_bar.current_mode = mode
            self.notify(description, timeout=3)
            await asyncio.sleep(3)

        # Test broadcast mode with different modes
        status_bar.broadcast_mode = True
        self.notify("Broadcast mode enabled", timeout=2)
        await asyncio.sleep(2)

        for mode, _ in modes:
            status_bar.current_mode = mode
            await asyncio.sleep(2)

        self.exit()


if __name__ == "__main__":
    app = TestModeApp()
    app.run()
```

## 5. Usage Examples

### Setting Mode Programmatically
```python
# Get status bar reference
status_bar = self.query_one(StatusBar)

# Change to INSERT mode
status_bar.current_mode = AppMode.INSERT

# Change to COPY mode
status_bar.current_mode = AppMode.COPY

# Enable broadcast mode
status_bar.broadcast_mode = True
```

### Getting Mode Configuration
```python
from claude_multi_terminal.core.modes import get_mode_config
from claude_multi_terminal.types import AppMode

# Get config for a specific mode
config = get_mode_config(AppMode.INSERT)
print(f"Color: {config.color}")
print(f"Icon: {config.icon}")
print(f"Description: {config.description}")
print(f"Hints: {config.hints}")

# Output:
# Color: rgb(120,200,120)
# Icon: ✎
# Description: Insert
# Hints: ['ESC:Normal', 'Type to input']
```

### Iterating Through All Modes
```python
from claude_multi_terminal.types import AppMode
from claude_multi_terminal.core.modes import get_mode_config

for mode in AppMode:
    config = get_mode_config(mode)
    print(f"{mode.value}: {config.color} {config.icon} {config.description}")

# Output:
# normal: rgb(100,180,240) ⌘ Normal
# insert: rgb(120,200,120) ✎ Insert
# copy: rgb(255,180,70) 📋 Copy
# command: rgb(255,77,77) ⚡ Command
```

## 6. CSS Customization

To customize mode colors, edit the CSS in StatusBar.DEFAULT_CSS:

```python
DEFAULT_CSS = """
StatusBar.-mode-normal {
    border-top: heavy rgb(100,180,240);  # Blue
}

StatusBar.-mode-insert {
    border-top: heavy rgb(120,200,120);  # Green
}

StatusBar.-mode-copy {
    border-top: heavy rgb(255,180,70);   # Yellow
}

StatusBar.-mode-command {
    border-top: heavy rgb(255,77,77);    # Coral
}
"""
```

## 7. Adding a New Mode

To add a new mode:

1. Add to AppMode enum in `types.py`:
```python
class AppMode(Enum):
    NORMAL = "normal"
    INSERT = "insert"
    COPY = "copy"
    COMMAND = "command"
    SEARCH = "search"  # New mode
```

2. Add configuration in `modes.py`:
```python
MODE_CONFIGS = {
    # ... existing modes ...
    AppMode.SEARCH: ModeConfig(
        color="rgb(220,150,220)",  # Magenta
        icon="🔍",
        description="Search",
        hints=["ESC:Normal", "/:Search", "n:Next"]
    ),
}
```

3. Add CSS class in `status_bar.py`:
```python
StatusBar.-mode-search {
    border-top: heavy rgb(220,150,220);
}
```

4. Add transition method in `app.py`:
```python
def enter_search_mode(self) -> None:
    """Enter SEARCH mode - find text in output."""
    self.mode = AppMode.SEARCH
    status_bar = self.query_one(StatusBar)
    status_bar.current_mode = AppMode.SEARCH
    self.notify("Mode: SEARCH", severity="information", timeout=1)
```

## Key Concepts

### Reactive Properties
Textual's reactive system automatically triggers updates when properties change:
```python
current_mode = reactive(AppMode.NORMAL)  # Reactive property

def watch_current_mode(self, mode: AppMode) -> None:
    # This is called automatically when current_mode changes
    pass
```

### CSS Class Management
The `set_class()` method toggles CSS classes on widgets:
```python
self.set_class(True, "-mode-insert")   # Add class
self.set_class(False, "-mode-insert")  # Remove class
```

### Rich Text Styling
Use Rich's Text object for colored output:
```python
text = Text()
text.append("Hello", style="bold rgb(255,77,77)")
text.append(" World", style="rgb(100,180,240)")
```
