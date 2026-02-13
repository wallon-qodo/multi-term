"""Color picker dialog for tab customization."""

from textual.screen import ModalScreen
from textual.widgets import Static, Button
from textual.containers import Vertical, Horizontal, Grid
from textual.app import ComposeResult
from typing import Optional


class ColorOption(Static):
    """Individual color option in the picker."""

    def __init__(self, color_name: str, color_rgb: str, **kwargs):
        """
        Initialize color option.

        Args:
            color_name: Display name (e.g., "Red", "Blue")
            color_rgb: RGB value (e.g., "rgb(255,0,0)")
        """
        super().__init__("●", **kwargs)
        self.color_name = color_name
        self.color_rgb = color_rgb
        self.can_focus = False

    def on_mount(self) -> None:
        """Apply color when mounted."""
        self.styles.color = self.color_rgb


class ColorPickerDialog(ModalScreen[Optional[tuple[str, str]]]):
    """
    Modal dialog for selecting tab colors.

    Features:
    - Preset color palette
    - Visual color preview
    - Quick selection
    - Default/reset option
    """

    DEFAULT_CSS = """
    ColorPickerDialog {
        align: center middle;
    }

    ColorPickerDialog > Vertical {
        background: rgb(32,32,32);
        border: thick rgb(100,180,240);
        width: 50;
        height: auto;
        padding: 2 3;
    }

    ColorPickerDialog .title {
        text-align: center;
        color: rgb(100,180,240);
        text-style: bold;
        padding: 0 0 1 0;
    }

    ColorPickerDialog .subtitle {
        text-align: center;
        color: rgb(180,180,180);
        padding: 0 0 2 0;
    }

    ColorPickerDialog Grid {
        grid-size: 4;
        grid-gutter: 1;
        height: auto;
        padding: 1 0;
    }

    ColorPickerDialog .color-item {
        width: 100%;
        height: 3;
        content-align: center middle;
        background: rgb(40,40,40);
        border: solid rgb(60,60,60);
        text-style: bold;
    }

    ColorPickerDialog .color-item:hover {
        background: rgb(50,50,50);
        border: solid rgb(100,180,240);
    }

    ColorPickerDialog Horizontal {
        height: auto;
        align: center middle;
        padding-top: 2;
    }

    ColorPickerDialog Button {
        margin: 0 1;
        min-width: 12;
    }

    ColorPickerDialog .default-btn {
        background: rgb(80,80,80);
        color: rgb(240,240,240);
    }

    ColorPickerDialog .default-btn:hover {
        background: rgb(100,100,100);
    }

    ColorPickerDialog .cancel-btn {
        background: rgb(60,60,80);
        color: rgb(200,200,220);
    }

    ColorPickerDialog .cancel-btn:hover {
        background: rgb(80,80,100);
    }
    """

    # Preset color palette
    COLORS = [
        ("Red", "rgb(255,77,77)"),
        ("Orange", "rgb(255,167,38)"),
        ("Yellow", "rgb(255,213,79)"),
        ("Green", "rgb(102,187,106)"),
        ("Teal", "rgb(38,198,218)"),
        ("Blue", "rgb(100,180,240)"),
        ("Purple", "rgb(186,104,200)"),
        ("Pink", "rgb(244,143,177)"),
        ("Cyan", "rgb(77,208,225)"),
        ("Lime", "rgb(205,220,57)"),
        ("Indigo", "rgb(121,134,203)"),
        ("Brown", "rgb(161,136,127)"),
    ]

    def __init__(self, current_color: Optional[tuple[str, str]] = None, **kwargs):
        """
        Initialize color picker.

        Args:
            current_color: Current (name, rgb) tuple if any
        """
        super().__init__(**kwargs)
        self.current_color = current_color
        self.selected_color: Optional[tuple[str, str]] = None

    def compose(self) -> ComposeResult:
        """Compose the color picker layout."""
        with Vertical():
            yield Static("🎨 Choose Tab Color", classes="title")
            yield Static("Click a color to apply it", classes="subtitle")

            with Grid():
                for color_name, color_rgb in self.COLORS:
                    color_option = ColorOption(color_name, color_rgb, classes="color-item")
                    # Store color info as data attributes
                    color_option.color_name = color_name
                    color_option.color_rgb = color_rgb
                    yield color_option

            with Horizontal():
                yield Button("⭕ Default", classes="default-btn", id="default-btn")
                yield Button("✗ Cancel", classes="cancel-btn", id="cancel-btn")

    def on_mount(self) -> None:
        """Highlight current color if any."""
        if self.current_color:
            current_rgb = self.current_color[1]
            for widget in self.query(".color-item"):
                if hasattr(widget, 'color_rgb') and widget.color_rgb == current_rgb:
                    widget.styles.border = ("heavy", "rgb(255,255,255)")

    def on_static_click(self, event) -> None:
        """Handle color option clicks."""
        if isinstance(event.widget, ColorOption):
            # Color selected
            self.selected_color = (event.widget.color_name, event.widget.color_rgb)
            self.dismiss(self.selected_color)

    async def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button clicks."""
        if event.button.id == "default-btn":
            # Reset to default (no custom color)
            self.dismiss(None)
        elif event.button.id == "cancel-btn":
            # Cancel - return False to indicate no change
            self.dismiss(False)
