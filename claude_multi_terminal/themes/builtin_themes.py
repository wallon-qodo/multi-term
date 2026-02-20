"""
Built-in themes for Claude Multi-Terminal.

Includes 6 professionally designed color schemes:
- OpenClaw (default)
- Nord
- Dracula
- Gruvbox
- Solarized Dark
- Monokai
- Tokyo Night
"""

from .theme_base import Theme, ThemeColors


# OpenClaw Theme (Default - current theme)
OPENCLAW_THEME = Theme(
    name="openclaw",
    display_name="OpenClaw",
    description="Professional coral-accented dark theme (default)",
    author="Claude Multi-Terminal",
    colors=ThemeColors(
        # Backgrounds
        bg_primary="rgb(24,24,24)",
        bg_secondary="rgb(28,28,28)",
        bg_tertiary="rgb(32,32,32)",
        bg_input="rgb(30,30,30)",
        bg_header="rgb(26,26,26)",
        # Accents
        accent_primary="rgb(255,77,77)",
        accent_secondary="rgb(255,100,100)",
        accent_success="rgb(120,200,120)",
        accent_warning="rgb(255,180,70)",
        accent_error="rgb(255,77,77)",
        accent_info="rgb(100,180,240)",
        # Text
        text_primary="rgb(240,240,240)",
        text_secondary="rgb(180,180,180)",
        text_dim="rgb(120,120,120)",
        text_bright="rgb(255,255,255)",
        text_accent="rgb(255,77,77)",
        # Borders
        border_default="rgb(60,60,60)",
        border_focus="rgb(255,77,77)",
        border_subtle="rgb(42,42,42)",
        border_hover="rgb(90,90,90)",
        # Selection
        selection_bg="rgba(255,77,77,0.25)",
        selection_text="rgb(255,255,255)",
        # Status
        status_active="rgb(120,200,120)",
        status_inactive="rgb(120,120,120)",
        status_processing="rgb(255,180,70)",
        status_error="rgb(255,77,77)",
        # ANSI
        ansi_black="rgb(32,32,32)",
        ansi_red="rgb(255,77,77)",
        ansi_green="rgb(120,200,120)",
        ansi_yellow="rgb(255,200,100)",
        ansi_blue="rgb(100,180,240)",
        ansi_magenta="rgb(220,150,220)",
        ansi_cyan="rgb(120,220,230)",
        ansi_white="rgb(240,240,240)",
        ansi_bright_black="rgb(120,120,120)",
        ansi_bright_red="rgb(255,120,120)",
        ansi_bright_green="rgb(150,220,150)",
        ansi_bright_yellow="rgb(255,230,120)",
        ansi_bright_blue="rgb(140,200,255)",
        ansi_bright_magenta="rgb(240,180,240)",
        ansi_bright_cyan="rgb(160,240,245)",
        ansi_bright_white="rgb(255,255,255)",
    ),
)


# Nord Theme
NORD_THEME = Theme(
    name="nord",
    display_name="Nord",
    description="Arctic, north-bluish color palette",
    author="Arctic Ice Studio",
    colors=ThemeColors(
        # Backgrounds
        bg_primary="rgb(46,52,64)",        # nord0
        bg_secondary="rgb(59,66,82)",      # nord1
        bg_tertiary="rgb(67,76,94)",       # nord2
        bg_input="rgb(76,86,106)",         # nord3
        bg_header="rgb(46,52,64)",         # nord0
        # Accents
        accent_primary="rgb(136,192,208)",  # nord8 (frost)
        accent_secondary="rgb(143,188,187)", # nord7
        accent_success="rgb(163,190,140)",  # nord14 (aurora green)
        accent_warning="rgb(235,203,139)",  # nord13 (aurora yellow)
        accent_error="rgb(191,97,106)",     # nord11 (aurora red)
        accent_info="rgb(129,161,193)",     # nord9
        # Text
        text_primary="rgb(236,239,244)",    # nord6
        text_secondary="rgb(229,233,240)",  # nord5
        text_dim="rgb(216,222,233)",        # nord4
        text_bright="rgb(236,239,244)",     # nord6
        text_accent="rgb(136,192,208)",     # nord8
        # Borders
        border_default="rgb(76,86,106)",    # nord3
        border_focus="rgb(136,192,208)",    # nord8
        border_subtle="rgb(67,76,94)",      # nord2
        border_hover="rgb(94,129,172)",     # nord10
        # Selection
        selection_bg="rgba(136,192,208,0.3)",
        selection_text="rgb(236,239,244)",
        # Status
        status_active="rgb(163,190,140)",   # nord14
        status_inactive="rgb(76,86,106)",   # nord3
        status_processing="rgb(235,203,139)", # nord13
        status_error="rgb(191,97,106)",     # nord11
        # ANSI
        ansi_black="rgb(59,66,82)",         # nord1
        ansi_red="rgb(191,97,106)",         # nord11
        ansi_green="rgb(163,190,140)",      # nord14
        ansi_yellow="rgb(235,203,139)",     # nord13
        ansi_blue="rgb(129,161,193)",       # nord9
        ansi_magenta="rgb(180,142,173)",    # nord15
        ansi_cyan="rgb(136,192,208)",       # nord8
        ansi_white="rgb(229,233,240)",      # nord5
        ansi_bright_black="rgb(76,86,106)", # nord3
        ansi_bright_red="rgb(191,97,106)",
        ansi_bright_green="rgb(163,190,140)",
        ansi_bright_yellow="rgb(235,203,139)",
        ansi_bright_blue="rgb(129,161,193)",
        ansi_bright_magenta="rgb(180,142,173)",
        ansi_bright_cyan="rgb(143,188,187)",
        ansi_bright_white="rgb(236,239,244)", # nord6
    ),
)


# Dracula Theme
DRACULA_THEME = Theme(
    name="dracula",
    display_name="Dracula",
    description="Dark theme with vibrant purples and pinks",
    author="Dracula Theme",
    colors=ThemeColors(
        # Backgrounds
        bg_primary="rgb(40,42,54)",
        bg_secondary="rgb(44,46,58)",
        bg_tertiary="rgb(48,50,62)",
        bg_input="rgb(68,71,90)",
        bg_header="rgb(40,42,54)",
        # Accents
        accent_primary="rgb(189,147,249)",  # purple
        accent_secondary="rgb(255,121,198)", # pink
        accent_success="rgb(80,250,123)",   # green
        accent_warning="rgb(255,184,108)",  # orange
        accent_error="rgb(255,85,85)",      # red
        accent_info="rgb(139,233,253)",     # cyan
        # Text
        text_primary="rgb(248,248,242)",
        text_secondary="rgb(98,114,164)",
        text_dim="rgb(68,71,90)",
        text_bright="rgb(255,255,255)",
        text_accent="rgb(189,147,249)",
        # Borders
        border_default="rgb(68,71,90)",
        border_focus="rgb(189,147,249)",
        border_subtle="rgb(48,50,62)",
        border_hover="rgb(98,114,164)",
        # Selection
        selection_bg="rgba(189,147,249,0.3)",
        selection_text="rgb(248,248,242)",
        # Status
        status_active="rgb(80,250,123)",
        status_inactive="rgb(68,71,90)",
        status_processing="rgb(255,184,108)",
        status_error="rgb(255,85,85)",
        # ANSI
        ansi_black="rgb(33,34,44)",
        ansi_red="rgb(255,85,85)",
        ansi_green="rgb(80,250,123)",
        ansi_yellow="rgb(241,250,140)",
        ansi_blue="rgb(98,114,164)",
        ansi_magenta="rgb(255,121,198)",
        ansi_cyan="rgb(139,233,253)",
        ansi_white="rgb(248,248,242)",
        ansi_bright_black="rgb(68,71,90)",
        ansi_bright_red="rgb(255,110,103)",
        ansi_bright_green="rgb(90,247,142)",
        ansi_bright_yellow="rgb(244,249,157)",
        ansi_bright_blue="rgb(130,170,255)",
        ansi_bright_magenta="rgb(255,146,208)",
        ansi_bright_cyan="rgb(154,237,254)",
        ansi_bright_white="rgb(255,255,255)",
    ),
)


# Gruvbox Theme
GRUVBOX_THEME = Theme(
    name="gruvbox",
    display_name="Gruvbox",
    description="Retro groove with warm, earthy colors",
    author="Pavel Pertsev",
    colors=ThemeColors(
        # Backgrounds
        bg_primary="rgb(40,40,40)",         # bg0_h
        bg_secondary="rgb(50,48,47)",       # bg0
        bg_tertiary="rgb(60,56,54)",        # bg1
        bg_input="rgb(80,73,69)",           # bg2
        bg_header="rgb(40,40,40)",
        # Accents
        accent_primary="rgb(251,184,108)",  # orange
        accent_secondary="rgb(254,128,25)", # bright orange
        accent_success="rgb(184,187,38)",   # green
        accent_warning="rgb(250,189,47)",   # yellow
        accent_error="rgb(251,73,52)",      # red
        accent_info="rgb(131,165,152)",     # aqua
        # Text
        text_primary="rgb(235,219,178)",    # fg0
        text_secondary="rgb(213,196,161)",  # fg1
        text_dim="rgb(168,153,132)",        # fg3
        text_bright="rgb(251,241,199)",     # fg0_h
        text_accent="rgb(251,184,108)",
        # Borders
        border_default="rgb(80,73,69)",
        border_focus="rgb(251,184,108)",
        border_subtle="rgb(60,56,54)",
        border_hover="rgb(102,92,84)",
        # Selection
        selection_bg="rgba(251,184,108,0.3)",
        selection_text="rgb(235,219,178)",
        # Status
        status_active="rgb(184,187,38)",
        status_inactive="rgb(102,92,84)",
        status_processing="rgb(250,189,47)",
        status_error="rgb(251,73,52)",
        # ANSI
        ansi_black="rgb(40,40,40)",
        ansi_red="rgb(204,36,29)",
        ansi_green="rgb(152,151,26)",
        ansi_yellow="rgb(215,153,33)",
        ansi_blue="rgb(69,133,136)",
        ansi_magenta="rgb(177,98,134)",
        ansi_cyan="rgb(104,157,106)",
        ansi_white="rgb(168,153,132)",
        ansi_bright_black="rgb(146,131,116)",
        ansi_bright_red="rgb(251,73,52)",
        ansi_bright_green="rgb(184,187,38)",
        ansi_bright_yellow="rgb(250,189,47)",
        ansi_bright_blue="rgb(131,165,152)",
        ansi_bright_magenta="rgb(211,134,155)",
        ansi_bright_cyan="rgb(142,192,124)",
        ansi_bright_white="rgb(235,219,178)",
    ),
)


# Solarized Dark Theme
SOLARIZED_THEME = Theme(
    name="solarized",
    display_name="Solarized Dark",
    description="Precision colors for terminals, carefully designed",
    author="Ethan Schoonover",
    colors=ThemeColors(
        # Backgrounds
        bg_primary="rgb(0,43,54)",          # base03
        bg_secondary="rgb(7,54,66)",        # base02
        bg_tertiary="rgb(88,110,117)",      # base01
        bg_input="rgb(7,54,66)",
        bg_header="rgb(0,43,54)",
        # Accents
        accent_primary="rgb(38,139,210)",   # blue
        accent_secondary="rgb(42,161,152)", # cyan
        accent_success="rgb(133,153,0)",    # green
        accent_warning="rgb(181,137,0)",    # yellow
        accent_error="rgb(220,50,47)",      # red
        accent_info="rgb(38,139,210)",      # blue
        # Text
        text_primary="rgb(131,148,150)",    # base0
        text_secondary="rgb(147,161,161)",  # base1
        text_dim="rgb(88,110,117)",         # base01
        text_bright="rgb(253,246,227)",     # base3
        text_accent="rgb(38,139,210)",
        # Borders
        border_default="rgb(7,54,66)",
        border_focus="rgb(38,139,210)",
        border_subtle="rgb(0,43,54)",
        border_hover="rgb(88,110,117)",
        # Selection
        selection_bg="rgba(38,139,210,0.3)",
        selection_text="rgb(253,246,227)",
        # Status
        status_active="rgb(133,153,0)",
        status_inactive="rgb(88,110,117)",
        status_processing="rgb(181,137,0)",
        status_error="rgb(220,50,47)",
        # ANSI
        ansi_black="rgb(7,54,66)",
        ansi_red="rgb(220,50,47)",
        ansi_green="rgb(133,153,0)",
        ansi_yellow="rgb(181,137,0)",
        ansi_blue="rgb(38,139,210)",
        ansi_magenta="rgb(211,54,130)",
        ansi_cyan="rgb(42,161,152)",
        ansi_white="rgb(238,232,213)",
        ansi_bright_black="rgb(0,43,54)",
        ansi_bright_red="rgb(203,75,22)",
        ansi_bright_green="rgb(88,110,117)",
        ansi_bright_yellow="rgb(101,123,131)",
        ansi_bright_blue="rgb(131,148,150)",
        ansi_bright_magenta="rgb(108,113,196)",
        ansi_bright_cyan="rgb(147,161,161)",
        ansi_bright_white="rgb(253,246,227)",
    ),
)


# Monokai Theme
MONOKAI_THEME = Theme(
    name="monokai",
    display_name="Monokai",
    description="Sublime Text's iconic color scheme",
    author="Wimer Hazenberg",
    colors=ThemeColors(
        # Backgrounds
        bg_primary="rgb(39,40,34)",
        bg_secondary="rgb(45,46,40)",
        bg_tertiary="rgb(52,53,47)",
        bg_input="rgb(73,72,62)",
        bg_header="rgb(39,40,34)",
        # Accents
        accent_primary="rgb(249,38,114)",   # pink
        accent_secondary="rgb(174,129,255)", # purple
        accent_success="rgb(166,226,46)",   # green
        accent_warning="rgb(253,151,31)",   # orange
        accent_error="rgb(249,38,114)",     # pink
        accent_info="rgb(102,217,239)",     # cyan
        # Text
        text_primary="rgb(248,248,242)",    # foreground
        text_secondary="rgb(117,113,94)",   # comment
        text_dim="rgb(85,81,70)",
        text_bright="rgb(255,255,255)",
        text_accent="rgb(249,38,114)",
        # Borders
        border_default="rgb(73,72,62)",
        border_focus="rgb(249,38,114)",
        border_subtle="rgb(52,53,47)",
        border_hover="rgb(117,113,94)",
        # Selection
        selection_bg="rgba(249,38,114,0.3)",
        selection_text="rgb(248,248,242)",
        # Status
        status_active="rgb(166,226,46)",
        status_inactive="rgb(73,72,62)",
        status_processing="rgb(253,151,31)",
        status_error="rgb(249,38,114)",
        # ANSI
        ansi_black="rgb(39,40,34)",
        ansi_red="rgb(249,38,114)",
        ansi_green="rgb(166,226,46)",
        ansi_yellow="rgb(230,219,116)",
        ansi_blue="rgb(102,217,239)",
        ansi_magenta="rgb(174,129,255)",
        ansi_cyan="rgb(161,239,228)",
        ansi_white="rgb(248,248,242)",
        ansi_bright_black="rgb(117,113,94)",
        ansi_bright_red="rgb(255,89,149)",
        ansi_bright_green="rgb(180,235,80)",
        ansi_bright_yellow="rgb(255,243,155)",
        ansi_bright_blue="rgb(137,231,250)",
        ansi_bright_magenta="rgb(198,160,255)",
        ansi_bright_cyan="rgb(185,250,240)",
        ansi_bright_white="rgb(255,255,255)",
    ),
)


# Tokyo Night Theme
TOKYO_NIGHT_THEME = Theme(
    name="tokyo-night",
    display_name="Tokyo Night",
    description="Clean, dark theme inspired by Tokyo's night lights",
    author="Enkia",
    colors=ThemeColors(
        # Backgrounds
        bg_primary="rgb(26,27,38)",         # bg
        bg_secondary="rgb(30,31,44)",       # bg_dark
        bg_tertiary="rgb(36,40,59)",        # bg_highlight
        bg_input="rgb(41,46,66)",           # bg_popup
        bg_header="rgb(26,27,38)",
        # Accents
        accent_primary="rgb(122,162,247)",  # blue
        accent_secondary="rgb(125,207,255)", # cyan
        accent_success="rgb(158,206,106)",  # green
        accent_warning="rgb(255,158,100)",  # orange
        accent_error="rgb(247,118,142)",    # red
        accent_info="rgb(122,162,247)",     # blue
        # Text
        text_primary="rgb(192,202,245)",    # fg
        text_secondary="rgb(169,177,214)",  # fg_dark
        text_dim="rgb(86,95,137)",          # comment
        text_bright="rgb(200,211,245)",     # fg_bright
        text_accent="rgb(122,162,247)",
        # Borders
        border_default="rgb(41,46,66)",
        border_focus="rgb(122,162,247)",
        border_subtle="rgb(36,40,59)",
        border_hover="rgb(73,81,111)",
        # Selection
        selection_bg="rgba(122,162,247,0.3)",
        selection_text="rgb(192,202,245)",
        # Status
        status_active="rgb(158,206,106)",
        status_inactive="rgb(73,81,111)",
        status_processing="rgb(255,158,100)",
        status_error="rgb(247,118,142)",
        # ANSI
        ansi_black="rgb(21,24,33)",
        ansi_red="rgb(247,118,142)",
        ansi_green="rgb(158,206,106)",
        ansi_yellow="rgb(224,175,104)",
        ansi_blue="rgb(122,162,247)",
        ansi_magenta="rgb(187,154,247)",
        ansi_cyan="rgb(125,207,255)",
        ansi_white="rgb(192,202,245)",
        ansi_bright_black="rgb(86,95,137)",
        ansi_bright_red="rgb(255,135,162)",
        ansi_bright_green="rgb(177,224,130)",
        ansi_bright_yellow="rgb(255,199,119)",
        ansi_bright_blue="rgb(140,180,255)",
        ansi_bright_magenta="rgb(210,180,255)",
        ansi_bright_cyan="rgb(150,220,255)",
        ansi_bright_white="rgb(200,211,245)",
    ),
)


# Dictionary of all built-in themes
BUILTIN_THEMES = {
    "openclaw": OPENCLAW_THEME,
    "nord": NORD_THEME,
    "dracula": DRACULA_THEME,
    "gruvbox": GRUVBOX_THEME,
    "solarized": SOLARIZED_THEME,
    "monokai": MONOKAI_THEME,
    "tokyo-night": TOKYO_NIGHT_THEME,
}


# Default theme
DEFAULT_THEME = OPENCLAW_THEME
