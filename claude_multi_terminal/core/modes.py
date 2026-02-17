"""Mode definitions and color mappings for the application."""

from ..types import AppMode
from dataclasses import dataclass


@dataclass
class ModeConfig:
    """Configuration for a specific mode including colors and icons."""

    color: str
    icon: str
    description: str
    hints: list[str]  # Contextual hints to show in status bar


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
