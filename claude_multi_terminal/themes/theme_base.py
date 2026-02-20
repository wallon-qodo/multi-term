"""
Base theme classes and color definitions.
"""

from dataclasses import dataclass
from typing import Dict, Any


@dataclass
class ThemeColors:
    """Color palette for a theme."""

    # Backgrounds
    bg_primary: str          # Main background
    bg_secondary: str        # Secondary panels
    bg_tertiary: str         # Elevated elements
    bg_input: str            # Input fields
    bg_header: str           # Headers

    # Accents
    accent_primary: str      # Primary accent
    accent_secondary: str    # Secondary accent
    accent_success: str      # Success/positive
    accent_warning: str      # Warning/caution
    accent_error: str        # Error/negative
    accent_info: str         # Information

    # Text
    text_primary: str        # Main text
    text_secondary: str      # Secondary text
    text_dim: str            # Dimmed text
    text_bright: str         # Bright/emphasized text
    text_accent: str         # Accent colored text

    # Borders
    border_default: str      # Default borders
    border_focus: str        # Focused borders
    border_subtle: str       # Subtle dividers
    border_hover: str        # Hover state

    # Selection
    selection_bg: str        # Selection background
    selection_text: str      # Selection text

    # Status
    status_active: str       # Active/online
    status_inactive: str     # Inactive/offline
    status_processing: str   # Processing/loading
    status_error: str        # Error status

    # ANSI Colors (for terminal output)
    ansi_black: str
    ansi_red: str
    ansi_green: str
    ansi_yellow: str
    ansi_blue: str
    ansi_magenta: str
    ansi_cyan: str
    ansi_white: str
    ansi_bright_black: str
    ansi_bright_red: str
    ansi_bright_green: str
    ansi_bright_yellow: str
    ansi_bright_blue: str
    ansi_bright_magenta: str
    ansi_bright_cyan: str
    ansi_bright_white: str

    def to_dict(self) -> Dict[str, str]:
        """Convert to dictionary for serialization."""
        return {
            # Backgrounds
            "bg_primary": self.bg_primary,
            "bg_secondary": self.bg_secondary,
            "bg_tertiary": self.bg_tertiary,
            "bg_input": self.bg_input,
            "bg_header": self.bg_header,
            # Accents
            "accent_primary": self.accent_primary,
            "accent_secondary": self.accent_secondary,
            "accent_success": self.accent_success,
            "accent_warning": self.accent_warning,
            "accent_error": self.accent_error,
            "accent_info": self.accent_info,
            # Text
            "text_primary": self.text_primary,
            "text_secondary": self.text_secondary,
            "text_dim": self.text_dim,
            "text_bright": self.text_bright,
            "text_accent": self.text_accent,
            # Borders
            "border_default": self.border_default,
            "border_focus": self.border_focus,
            "border_subtle": self.border_subtle,
            "border_hover": self.border_hover,
            # Selection
            "selection_bg": self.selection_bg,
            "selection_text": self.selection_text,
            # Status
            "status_active": self.status_active,
            "status_inactive": self.status_inactive,
            "status_processing": self.status_processing,
            "status_error": self.status_error,
            # ANSI
            "ansi_black": self.ansi_black,
            "ansi_red": self.ansi_red,
            "ansi_green": self.ansi_green,
            "ansi_yellow": self.ansi_yellow,
            "ansi_blue": self.ansi_blue,
            "ansi_magenta": self.ansi_magenta,
            "ansi_cyan": self.ansi_cyan,
            "ansi_white": self.ansi_white,
            "ansi_bright_black": self.ansi_bright_black,
            "ansi_bright_red": self.ansi_bright_red,
            "ansi_bright_green": self.ansi_bright_green,
            "ansi_bright_yellow": self.ansi_bright_yellow,
            "ansi_bright_blue": self.ansi_bright_blue,
            "ansi_bright_magenta": self.ansi_bright_magenta,
            "ansi_bright_cyan": self.ansi_bright_cyan,
            "ansi_bright_white": self.ansi_bright_white,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, str]) -> "ThemeColors":
        """Create from dictionary."""
        return cls(**data)


@dataclass
class Theme:
    """Complete theme definition."""

    name: str                # Theme name
    display_name: str        # Display name for UI
    description: str         # Theme description
    author: str              # Theme author
    colors: ThemeColors      # Color palette
    dark_mode: bool = True   # Whether theme is dark

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "name": self.name,
            "display_name": self.display_name,
            "description": self.description,
            "author": self.author,
            "dark_mode": self.dark_mode,
            "colors": self.colors.to_dict(),
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Theme":
        """Create from dictionary."""
        colors = ThemeColors.from_dict(data["colors"])
        return cls(
            name=data["name"],
            display_name=data["display_name"],
            description=data["description"],
            author=data["author"],
            dark_mode=data.get("dark_mode", True),
            colors=colors,
        )
