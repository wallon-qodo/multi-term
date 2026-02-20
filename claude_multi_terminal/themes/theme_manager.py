"""
Theme manager for loading, switching, and persisting themes.
"""

import json
from pathlib import Path
from typing import Dict, Optional
from .theme_base import Theme
from .builtin_themes import BUILTIN_THEMES, DEFAULT_THEME


class ThemeManager:
    """
    Manages theme loading, switching, and persistence.

    Handles built-in themes and custom user themes.
    """

    def __init__(self, config_dir: Optional[Path] = None):
        """
        Initialize theme manager.

        Args:
            config_dir: Configuration directory for theme storage
        """
        self.config_dir = config_dir or (Path.home() / ".claude")
        self.themes_dir = self.config_dir / "themes"
        self.config_file = self.config_dir / "theme_config.json"

        # Ensure directories exist
        self.themes_dir.mkdir(parents=True, exist_ok=True)

        # Current active theme
        self._current_theme: Theme = DEFAULT_THEME

        # Load saved theme preference
        self._load_theme_config()

    def _load_theme_config(self) -> None:
        """Load theme configuration from disk."""
        try:
            if self.config_file.exists():
                with open(self.config_file, "r") as f:
                    config = json.load(f)
                    theme_name = config.get("current_theme", "openclaw")
                    self._current_theme = self.get_theme(theme_name) or DEFAULT_THEME
        except Exception:
            # If loading fails, use default theme
            self._current_theme = DEFAULT_THEME

    def _save_theme_config(self) -> None:
        """Save theme configuration to disk."""
        try:
            config = {
                "current_theme": self._current_theme.name,
                "version": "1.0",
            }
            with open(self.config_file, "w") as f:
                json.dump(config, f, indent=2)
        except Exception:
            # Silently fail on save errors
            pass

    def get_theme(self, name: str) -> Optional[Theme]:
        """
        Get a theme by name.

        Args:
            name: Theme name (e.g., "nord", "dracula")

        Returns:
            Theme if found, None otherwise
        """
        # Check built-in themes first
        if name in BUILTIN_THEMES:
            return BUILTIN_THEMES[name]

        # Check custom themes
        custom_theme_file = self.themes_dir / f"{name}.json"
        if custom_theme_file.exists():
            try:
                with open(custom_theme_file, "r") as f:
                    data = json.load(f)
                    return Theme.from_dict(data)
            except Exception:
                return None

        return None

    def set_theme(self, name: str) -> bool:
        """
        Set the active theme.

        Args:
            name: Theme name to activate

        Returns:
            bool: True if theme was set successfully
        """
        theme = self.get_theme(name)
        if theme:
            self._current_theme = theme
            self._save_theme_config()
            return True
        return False

    def get_current_theme(self) -> Theme:
        """
        Get the currently active theme.

        Returns:
            Theme: Current active theme
        """
        return self._current_theme

    def list_themes(self) -> Dict[str, Theme]:
        """
        List all available themes (built-in + custom).

        Returns:
            Dict mapping theme names to Theme objects
        """
        themes = dict(BUILTIN_THEMES)

        # Add custom themes
        if self.themes_dir.exists():
            for theme_file in self.themes_dir.glob("*.json"):
                try:
                    with open(theme_file, "r") as f:
                        data = json.load(f)
                        theme = Theme.from_dict(data)
                        themes[theme.name] = theme
                except Exception:
                    # Skip invalid theme files
                    continue

        return themes

    def save_custom_theme(self, theme: Theme) -> bool:
        """
        Save a custom theme to disk.

        Args:
            theme: Theme to save

        Returns:
            bool: True if saved successfully
        """
        try:
            theme_file = self.themes_dir / f"{theme.name}.json"
            with open(theme_file, "w") as f:
                json.dump(theme.to_dict(), f, indent=2)
            return True
        except Exception:
            return False

    def delete_custom_theme(self, name: str) -> bool:
        """
        Delete a custom theme.

        Args:
            name: Theme name to delete

        Returns:
            bool: True if deleted successfully
        """
        # Prevent deletion of built-in themes
        if name in BUILTIN_THEMES:
            return False

        try:
            theme_file = self.themes_dir / f"{name}.json"
            if theme_file.exists():
                theme_file.unlink()
                return True
            return False
        except Exception:
            return False

    def generate_css(self, theme: Optional[Theme] = None) -> str:
        """
        Generate CSS variables for a theme.

        Args:
            theme: Theme to generate CSS for (uses current if None)

        Returns:
            str: CSS variable definitions
        """
        if theme is None:
            theme = self._current_theme

        colors = theme.colors
        css = f"""
/* Theme: {theme.display_name} */
Screen {{
    background: {colors.bg_primary};
    color: {colors.text_primary};
}}

/* Headers and panels */
HeaderBar {{
    background: {colors.bg_header};
    color: {colors.text_primary};
}}

StatusBar {{
    background: {colors.bg_header};
    color: {colors.text_primary};
}}

/* Session panes */
SessionPane {{
    background: {colors.bg_secondary};
    border: solid {colors.border_default};
}}

SessionPane:focus {{
    border: solid {colors.border_focus};
}}

/* Input fields */
Input {{
    background: {colors.bg_input};
    color: {colors.text_primary};
    border: solid {colors.border_default};
}}

Input:focus {{
    border: solid {colors.border_focus};
}}

/* Buttons and widgets */
Button {{
    background: {colors.bg_tertiary};
    color: {colors.text_primary};
    border: solid {colors.border_default};
}}

Button:hover {{
    border: solid {colors.border_hover};
}}

Button:focus {{
    border: solid {colors.border_focus};
    background: {colors.accent_primary};
    color: {colors.text_bright};
}}

/* Status indicators */
.status-active {{
    color: {colors.status_active};
}}

.status-inactive {{
    color: {colors.status_inactive};
}}

.status-processing {{
    color: {colors.status_processing};
}}

.status-error {{
    color: {colors.status_error};
}}

/* Toasts and notifications */
Toast {{
    background: {colors.bg_tertiary};
    border: solid {colors.accent_info};
    color: {colors.text_primary};
}}

Toast.-information {{
    background: rgba({self._rgb_to_rgba(colors.accent_info)}, 0.2);
    border: solid {colors.accent_info};
}}

Toast.-warning {{
    background: rgba({self._rgb_to_rgba(colors.accent_warning)}, 0.2);
    border: solid {colors.accent_warning};
    color: {colors.accent_warning};
}}

Toast.-error {{
    background: rgba({self._rgb_to_rgba(colors.accent_error)}, 0.2);
    border: solid {colors.accent_error};
    color: {colors.accent_error};
}}

/* Selection */
.selected {{
    background: {colors.selection_bg};
    color: {colors.selection_text};
}}

/* Scrollbars */
ScrollBar {{
    background: {colors.bg_secondary};
}}

ScrollBar Thumb {{
    background: {colors.border_default};
}}

ScrollBar Thumb:hover {{
    background: {colors.border_hover};
}}

/* Tabs */
TabBar {{
    background: {colors.bg_header};
}}

Tab {{
    background: {colors.bg_secondary};
    color: {colors.text_secondary};
    border: solid {colors.border_subtle};
}}

Tab:hover {{
    background: {colors.bg_tertiary};
}}

Tab.-active {{
    background: {colors.accent_primary};
    color: {colors.text_bright};
    border: solid {colors.accent_primary};
}}

/* Workspace indicators */
.workspace-active {{
    background: {colors.accent_primary};
    color: {colors.text_bright};
}}

.workspace-inactive {{
    background: {colors.bg_tertiary};
    color: {colors.text_dim};
}}
"""
        return css

    def _rgb_to_rgba(self, rgb_str: str) -> str:
        """
        Convert rgb(r,g,b) to r,g,b for rgba usage.

        Args:
            rgb_str: RGB color string like "rgb(255,100,50)"

        Returns:
            str: "r,g,b" for use in rgba()
        """
        # Extract numbers from rgb(...) string
        import re
        match = re.search(r'rgb\((\d+),\s*(\d+),\s*(\d+)\)', rgb_str)
        if match:
            return f"{match.group(1)},{match.group(2)},{match.group(3)}"
        return "0,0,0"
