"""OpenClaw-inspired professional terminal color theme and design constants."""

from dataclasses import dataclass


@dataclass
class HomebrewTheme:
    """Professional OpenClaw-inspired color palette for modern terminal applications."""

    # Background Colors (Dark Charcoal)
    BG_PRIMARY = "rgb(24,24,24)"        # Main background
    BG_SECONDARY = "rgb(28,28,28)"      # Secondary panels
    BG_TERTIARY = "rgb(32,32,32)"       # Elevated elements
    BG_INPUT = "rgb(30,30,30)"          # Input fields
    BG_HEADER = "rgb(26,26,26)"         # Headers

    # Accent Colors (Coral Red)
    ACCENT_PRIMARY = "rgb(255,77,77)"     # Primary accent (coral red)
    ACCENT_SECONDARY = "rgb(255,100,100)" # Light coral
    ACCENT_SUCCESS = "rgb(120,200,120)"   # Muted green
    ACCENT_WARNING = "rgb(255,180,70)"    # Orange
    ACCENT_ERROR = "rgb(255,77,77)"       # Coral red (same as primary)
    ACCENT_INFO = "rgb(100,180,240)"      # Steel blue

    # Text Colors (Clean Grays)
    TEXT_PRIMARY = "rgb(240,240,240)"     # Main text (bright off-white)
    TEXT_SECONDARY = "rgb(180,180,180)"   # Secondary text
    TEXT_DIM = "rgb(120,120,120)"         # Dimmed text
    TEXT_BRIGHT = "rgb(255,255,255)"      # Pure white
    TEXT_AMBER = "rgb(255,77,77)"         # Accent text (coral red)

    # Border Colors (Subtle Separation)
    BORDER_DEFAULT = "rgb(60,60,60)"      # Default borders
    BORDER_FOCUS = "rgb(255,77,77)"       # Focused borders (coral red)
    BORDER_SUBTLE = "rgb(42,42,42)"       # Subtle dividers
    BORDER_HOVER = "rgb(90,90,90)"        # Hover state

    # Terminal ANSI Colors (OpenClaw-adjusted)
    ANSI_BLACK = "rgb(32,32,32)"
    ANSI_RED = "rgb(255,77,77)"
    ANSI_GREEN = "rgb(120,200,120)"
    ANSI_YELLOW = "rgb(255,200,100)"
    ANSI_BLUE = "rgb(100,180,240)"
    ANSI_MAGENTA = "rgb(220,150,220)"
    ANSI_CYAN = "rgb(120,220,230)"
    ANSI_WHITE = "rgb(240,240,240)"

    # Bright variants
    ANSI_BRIGHT_BLACK = "rgb(120,120,120)"
    ANSI_BRIGHT_RED = "rgb(255,120,120)"
    ANSI_BRIGHT_GREEN = "rgb(150,220,150)"
    ANSI_BRIGHT_YELLOW = "rgb(255,230,120)"
    ANSI_BRIGHT_BLUE = "rgb(140,200,255)"
    ANSI_BRIGHT_MAGENTA = "rgb(240,180,240)"
    ANSI_BRIGHT_CYAN = "rgb(160,240,245)"
    ANSI_BRIGHT_WHITE = "rgb(255,255,255)"

    # Status Colors (Semantic)
    STATUS_ACTIVE = "rgb(120,200,120)"    # Green
    STATUS_INACTIVE = "rgb(120,120,120)"  # Dim gray
    STATUS_PROCESSING = "rgb(255,180,70)" # Orange
    STATUS_ERROR = "rgb(255,77,77)"       # Coral red

    # Semantic UI Colors
    SUCCESS = "rgb(120,200,120)"
    WARNING = "rgb(255,180,70)"
    ERROR = "rgb(255,77,77)"
    INFO = "rgb(100,180,240)"

    # Selection Colors
    SELECTION_BG = "rgba(255,77,77,0.25)"   # Coral red with transparency
    SELECTION_TEXT = "rgb(255,255,255)"     # White for contrast


@dataclass
class BoxDrawing:
    """Unicode box drawing characters for professional layouts."""

    # Single line boxes
    SINGLE_TOP_LEFT = "┌"
    SINGLE_TOP_RIGHT = "┐"
    SINGLE_BOTTOM_LEFT = "└"
    SINGLE_BOTTOM_RIGHT = "┘"
    SINGLE_HORIZONTAL = "─"
    SINGLE_VERTICAL = "│"
    SINGLE_T_DOWN = "┬"
    SINGLE_T_UP = "┴"
    SINGLE_T_RIGHT = "├"
    SINGLE_T_LEFT = "┤"
    SINGLE_CROSS = "┼"

    # Double line boxes
    DOUBLE_TOP_LEFT = "╔"
    DOUBLE_TOP_RIGHT = "╗"
    DOUBLE_BOTTOM_LEFT = "╚"
    DOUBLE_BOTTOM_RIGHT = "╝"
    DOUBLE_HORIZONTAL = "═"
    DOUBLE_VERTICAL = "║"

    # Rounded boxes
    ROUND_TOP_LEFT = "╭"
    ROUND_TOP_RIGHT = "╮"
    ROUND_BOTTOM_LEFT = "╰"
    ROUND_BOTTOM_RIGHT = "╯"

    # Heavy lines
    HEAVY_HORIZONTAL = "━"
    HEAVY_VERTICAL = "┃"

    # Dashed lines
    DASH_HORIZONTAL = "┄"
    DASH_VERTICAL = "┆"

    # Separators
    SEPARATOR_LIGHT = "┊"
    SEPARATOR_HEAVY = "┃"


@dataclass
class Icons:
    """Unicode icons for enhanced visual communication."""

    # Status
    ONLINE = "●"
    OFFLINE = "○"
    ACTIVE = "⚡"
    IDLE = "💤"

    # Actions
    COMMAND = "⚡"
    RESPONSE = "📝"
    CLIPBOARD = "📋"
    BROADCAST = "📡"
    TIME = "🕐"
    SUCCESS = "✓"
    ERROR = "❌"
    WARNING = "⚠"
    INFO = "💡"

    # UI Elements
    KEYBOARD = "⌨"
    MOUSE = "🖱"
    SAVE = "💾"
    EDIT = "✏"
    BOOKMARK = "🔖"
    METRICS = "📊"
    BELL = "🔔"


# Global instances
theme = HomebrewTheme()
boxes = BoxDrawing()
icons = Icons()

# Alias for backward compatibility
EnterpriseTheme = HomebrewTheme
