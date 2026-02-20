"""
Theme system for Claude Multi-Terminal.

Provides customizable color schemes and visual styles.
"""

from .theme_base import Theme, ThemeColors
from .theme_manager import ThemeManager
from .builtin_themes import BUILTIN_THEMES

__all__ = ["Theme", "ThemeColors", "ThemeManager", "BUILTIN_THEMES"]
