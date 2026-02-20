"""
Visual polish and refinements for professional appearance.

Applies rounded corners, shadows, spacing, and other visual enhancements.
"""

from typing import Dict, Any


class PolishStyles:
    """
    Polished CSS styles for professional appearance.

    Provides rounded corners, shadows, refined spacing, and visual hierarchy.
    """

    # Rounded corner radii (in cells)
    RADIUS_SMALL = 1
    RADIUS_MEDIUM = 2
    RADIUS_LARGE = 3

    # Shadow definitions (offset-x offset-y blur color)
    SHADOW_SUBTLE = "0 1 2 rgba(0, 0, 0, 0.1)"
    SHADOW_MEDIUM = "0 2 4 rgba(0, 0, 0, 0.15)"
    SHADOW_STRONG = "0 4 8 rgba(0, 0, 0, 0.25)"

    # Spacing system (consistent padding/margin)
    SPACE_NONE = 0
    SPACE_TINY = 1
    SPACE_SMALL = 2
    SPACE_MEDIUM = 3
    SPACE_LARGE = 4
    SPACE_XLARGE = 6

    @staticmethod
    def generate_polished_css(theme_colors: Dict[str, str]) -> str:
        """
        Generate polished CSS with professional refinements.

        Args:
            theme_colors: Theme color palette

        Returns:
            str: Polished CSS styles
        """
        return f"""
/* ===== GLOBAL POLISH ===== */

Screen {{
    background: {theme_colors.get('bg_primary', 'rgb(24,24,24)')};
    color: {theme_colors.get('text_primary', 'rgb(240,240,240)')};
    padding: 1;
}}

/* ===== ROUNDED CORNERS & SHADOWS ===== */

/* Header with subtle gradient and shadow */
HeaderBar {{
    background: {theme_colors.get('bg_header', 'rgb(26,26,26)')};
    color: {theme_colors.get('text_primary', 'rgb(240,240,240)')};
    border: solid {theme_colors.get('border_subtle', 'rgb(42,42,42)')};
    border-bottom: heavy {theme_colors.get('border_default', 'rgb(60,60,60)')};
    padding: 1 2;
    height: auto;
    box-shadow: {PolishStyles.SHADOW_MEDIUM};
}}

/* Status bar with subtle elevation */
StatusBar {{
    background: {theme_colors.get('bg_header', 'rgb(26,26,26)')};
    color: {theme_colors.get('text_secondary', 'rgb(180,180,180)')};
    border: solid {theme_colors.get('border_subtle', 'rgb(42,42,42)')};
    border-top: heavy {theme_colors.get('border_default', 'rgb(60,60,60)')};
    padding: 1 2;
    height: auto;
    box-shadow: {PolishStyles.SHADOW_MEDIUM};
}}

/* Session panes with rounded corners */
SessionPane {{
    background: {theme_colors.get('bg_secondary', 'rgb(28,28,28)')};
    border: solid {theme_colors.get('border_default', 'rgb(60,60,60)')};
    border-radius: {PolishStyles.RADIUS_MEDIUM};
    padding: 1;
    margin: 0 1;
    box-shadow: {PolishStyles.SHADOW_SUBTLE};
}}

SessionPane:focus {{
    border: thick {theme_colors.get('border_focus', 'rgb(255,77,77)')};
    box-shadow: {PolishStyles.SHADOW_MEDIUM};
    background: {theme_colors.get('bg_tertiary', 'rgb(32,32,32)')};
}}

SessionPane:hover {{
    border: solid {theme_colors.get('border_hover', 'rgb(90,90,90)')};
}}

/* ===== INPUT FIELDS ===== */

Input {{
    background: {theme_colors.get('bg_input', 'rgb(30,30,30)')};
    color: {theme_colors.get('text_primary', 'rgb(240,240,240)')};
    border: solid {theme_colors.get('border_default', 'rgb(60,60,60)')};
    border-radius: {PolishStyles.RADIUS_MEDIUM};
    padding: 1 2;
    box-shadow: inset {PolishStyles.SHADOW_SUBTLE};
}}

Input:focus {{
    border: thick {theme_colors.get('border_focus', 'rgb(255,77,77)')};
    background: {theme_colors.get('bg_primary', 'rgb(24,24,24)')};
    box-shadow: {PolishStyles.SHADOW_MEDIUM};
}}

/* ===== BUTTONS ===== */

Button {{
    background: {theme_colors.get('bg_tertiary', 'rgb(32,32,32)')};
    color: {theme_colors.get('text_primary', 'rgb(240,240,240)')};
    border: solid {theme_colors.get('border_default', 'rgb(60,60,60)')};
    border-radius: {PolishStyles.RADIUS_MEDIUM};
    padding: 1 3;
    margin: 0 1;
    box-shadow: {PolishStyles.SHADOW_SUBTLE};
}}

Button:hover {{
    border: solid {theme_colors.get('border_hover', 'rgb(90,90,90)')};
    background: {theme_colors.get('bg_input', 'rgb(30,30,30)')};
    box-shadow: {PolishStyles.SHADOW_MEDIUM};
}}

Button:focus {{
    border: thick {theme_colors.get('border_focus', 'rgb(255,77,77)')};
    background: {theme_colors.get('accent_primary', 'rgb(255,77,77)')};
    color: {theme_colors.get('text_bright', 'rgb(255,255,255)')};
    box-shadow: {PolishStyles.SHADOW_STRONG};
}}

Button.-primary {{
    background: {theme_colors.get('accent_primary', 'rgb(255,77,77)')};
    color: {theme_colors.get('text_bright', 'rgb(255,255,255)')};
    border: solid {theme_colors.get('accent_primary', 'rgb(255,77,77)')};
}}

Button.-primary:hover {{
    background: {theme_colors.get('accent_secondary', 'rgb(255,100,100)')};
}}

/* ===== TOASTS & NOTIFICATIONS ===== */

Toast {{
    background: {theme_colors.get('bg_tertiary', 'rgb(32,32,32)')};
    border: solid {theme_colors.get('accent_info', 'rgb(100,180,240)')};
    color: {theme_colors.get('text_primary', 'rgb(240,240,240)')};
    border-radius: {PolishStyles.RADIUS_MEDIUM};
    padding: 1 2;
    box-shadow: {PolishStyles.SHADOW_STRONG};
}}

Toast.-information {{
    background: rgba({PolishStyles._rgb_to_rgba(theme_colors.get('accent_info', 'rgb(100,180,240)'))}, 0.2);
    border: thick {theme_colors.get('accent_info', 'rgb(100,180,240)')};
}}

Toast.-success {{
    background: rgba({PolishStyles._rgb_to_rgba(theme_colors.get('accent_success', 'rgb(120,200,120)'))}, 0.2);
    border: thick {theme_colors.get('accent_success', 'rgb(120,200,120)')};
    color: {theme_colors.get('accent_success', 'rgb(120,200,120)')};
}}

Toast.-warning {{
    background: rgba({PolishStyles._rgb_to_rgba(theme_colors.get('accent_warning', 'rgb(255,180,70)'))}, 0.2);
    border: thick {theme_colors.get('accent_warning', 'rgb(255,180,70)')};
    color: {theme_colors.get('accent_warning', 'rgb(255,180,70)')};
}}

Toast.-error {{
    background: rgba({PolishStyles._rgb_to_rgba(theme_colors.get('accent_error', 'rgb(255,77,77)'))}, 0.2);
    border: thick {theme_colors.get('accent_error', 'rgb(255,77,77)')};
    color: {theme_colors.get('accent_error', 'rgb(255,77,77)')};
}}

/* ===== SCROLLBARS ===== */

ScrollBar {{
    background: {theme_colors.get('bg_secondary', 'rgb(28,28,28)')};
    border-radius: {PolishStyles.RADIUS_SMALL};
}}

ScrollBar Thumb {{
    background: {theme_colors.get('border_default', 'rgb(60,60,60)')};
    border-radius: {PolishStyles.RADIUS_SMALL};
}}

ScrollBar Thumb:hover {{
    background: {theme_colors.get('border_hover', 'rgb(90,90,90)')};
}}

/* ===== TABS ===== */

TabBar {{
    background: {theme_colors.get('bg_header', 'rgb(26,26,26)')};
    padding: 1 2;
    border-bottom: solid {theme_colors.get('border_default', 'rgb(60,60,60)')};
}}

Tab {{
    background: {theme_colors.get('bg_secondary', 'rgb(28,28,28)')};
    color: {theme_colors.get('text_secondary', 'rgb(180,180,180)')};
    border: solid {theme_colors.get('border_subtle', 'rgb(42,42,42)')};
    border-radius: {PolishStyles.RADIUS_MEDIUM} {PolishStyles.RADIUS_MEDIUM} 0 0;
    padding: 1 3;
    margin: 0 1 0 0;
}}

Tab:hover {{
    background: {theme_colors.get('bg_tertiary', 'rgb(32,32,32)')};
    border: solid {theme_colors.get('border_hover', 'rgb(90,90,90)')};
}}

Tab.-active {{
    background: {theme_colors.get('accent_primary', 'rgb(255,77,77)')};
    color: {theme_colors.get('text_bright', 'rgb(255,255,255)')};
    border: solid {theme_colors.get('accent_primary', 'rgb(255,77,77)')};
    box-shadow: {PolishStyles.SHADOW_MEDIUM};
}}

/* ===== WORKSPACE INDICATORS ===== */

.workspace-indicator {{
    border-radius: {PolishStyles.RADIUS_SMALL};
    padding: 0 2;
    margin: 0 1;
}}

.workspace-active {{
    background: {theme_colors.get('accent_primary', 'rgb(255,77,77)')};
    color: {theme_colors.get('text_bright', 'rgb(255,255,255)')};
    border: solid {theme_colors.get('accent_primary', 'rgb(255,77,77)')};
    box-shadow: {PolishStyles.SHADOW_MEDIUM};
}}

.workspace-inactive {{
    background: {theme_colors.get('bg_tertiary', 'rgb(32,32,32)')};
    color: {theme_colors.get('text_dim', 'rgb(120,120,120)')};
    border: solid {theme_colors.get('border_subtle', 'rgb(42,42,42)')};
}}

.workspace-inactive:hover {{
    background: {theme_colors.get('bg_input', 'rgb(30,30,30)')};
    color: {theme_colors.get('text_secondary', 'rgb(180,180,180)')};
}}

/* ===== PANELS & CONTAINERS ===== */

Container {{
    border-radius: {PolishStyles.RADIUS_MEDIUM};
}}

Vertical {{
    padding: {PolishStyles.SPACE_MEDIUM};
}}

Horizontal {{
    padding: {PolishStyles.SPACE_SMALL} {PolishStyles.SPACE_MEDIUM};
}}

/* ===== FOOTER HINTS ===== */

FooterHints {{
    background: {theme_colors.get('bg_header', 'rgb(26,26,26)')};
    color: {theme_colors.get('text_dim', 'rgb(120,120,120)')};
    padding: 1 2;
    border-top: solid {theme_colors.get('border_subtle', 'rgb(42,42,42)')};
}}

/* ===== DIALOGS & OVERLAYS ===== */

Dialog {{
    background: {theme_colors.get('bg_secondary', 'rgb(28,28,28)')};
    border: thick {theme_colors.get('border_focus', 'rgb(255,77,77)')};
    border-radius: {PolishStyles.RADIUS_LARGE};
    padding: {PolishStyles.SPACE_LARGE};
    box-shadow: {PolishStyles.SHADOW_STRONG};
}}

/* ===== SELECTION & HIGHLIGHTING ===== */

.selected {{
    background: {theme_colors.get('selection_bg', 'rgba(255,77,77,0.25)')};
    color: {theme_colors.get('selection_text', 'rgb(255,255,255)')};
    border-radius: {PolishStyles.RADIUS_SMALL};
}}

/* ===== STATUS INDICATORS ===== */

.status-indicator {{
    border-radius: 50%;
    padding: 0 1;
    margin: 0 1;
}}

.status-active {{
    color: {theme_colors.get('status_active', 'rgb(120,200,120)')};
}}

.status-inactive {{
    color: {theme_colors.get('status_inactive', 'rgb(120,120,120)')};
}}

.status-processing {{
    color: {theme_colors.get('status_processing', 'rgb(255,180,70)')};
}}

.status-error {{
    color: {theme_colors.get('status_error', 'rgb(255,77,77)')};
}}
"""

    @staticmethod
    def _rgb_to_rgba(rgb_str: str) -> str:
        """
        Convert rgb(r,g,b) to r,g,b for rgba usage.

        Args:
            rgb_str: RGB color string

        Returns:
            str: "r,g,b" for rgba
        """
        import re
        match = re.search(r'rgb\((\d+),\s*(\d+),\s*(\d+)\)', rgb_str)
        if match:
            return f"{match.group(1)},{match.group(2)},{match.group(3)}"
        return "0,0,0"


class TypographyRefinements:
    """
    Typography refinements for better readability.
    """

    @staticmethod
    def apply_typography() -> str:
        """
        Generate typography CSS.

        Returns:
            str: Typography styles
        """
        return """
/* ===== TYPOGRAPHY ===== */

* {{
    text-style: none;
}}

.heading {{
    text-style: bold;
}}

.subheading {{
    text-style: bold;
}}

.emphasis {{
    text-style: bold;
}}

.dimmed {{
    text-style: dim;
}}

.highlighted {{
    text-style: bold underline;
}}

.code {{
    text-style: italic;
}}
"""


class SpatialHierarchy:
    """
    Spatial hierarchy for visual organization.
    """

    @staticmethod
    def apply_hierarchy() -> str:
        """
        Generate spatial hierarchy CSS.

        Returns:
            str: Hierarchy styles
        """
        return """
/* ===== SPATIAL HIERARCHY ===== */

/* Primary elements (highest importance) */
.primary {{
    padding: 2;
    margin: 1;
}}

/* Secondary elements */
.secondary {{
    padding: 1;
    margin: 1;
}}

/* Tertiary elements (least emphasis) */
.tertiary {{
    padding: 1;
    margin: 0;
}}

/* Grouped elements */
.group {{
    padding: 2;
    margin: 1;
    border-radius: 2;
}}

/* Card-like containers */
.card {{
    padding: 3;
    margin: 2;
    border-radius: 2;
    box-shadow: 0 2 4 rgba(0, 0, 0, 0.15);
}}
"""
