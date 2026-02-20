"""
Theme selector dialog for choosing and previewing themes.
"""

from textual.app import ComposeResult
from textual.containers import Container, Vertical, Horizontal
from textual.widgets import Static, Button, Label
from textual.reactive import reactive
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from ..themes import ThemeManager
from ..animations import AnimationHelper, OVERLAY_SHOW, OVERLAY_HIDE


class ThemeSelector(Container):
    """
    Theme selection dialog.

    Allows users to browse, preview, and select themes.
    """

    DEFAULT_CSS = """
    ThemeSelector {
        dock: top;
        height: 100%;
        width: 100%;
        background: rgba(0, 0, 0, 0.8);
        layer: theme_selector;
        align: center middle;
    }

    ThemeSelector > Vertical {
        width: 90;
        height: auto;
        max-height: 80%;
        background: $surface;
        border: thick $primary;
        padding: 2 4;
    }

    ThemeSelector #theme-list {
        height: 1fr;
        overflow-y: auto;
        border: solid $border;
        padding: 1;
    }

    ThemeSelector .theme-item {
        padding: 1 2;
        margin: 0 0 1 0;
        background: $panel;
        border: solid $border;
    }

    ThemeSelector .theme-item:hover {
        border: solid $primary;
        background: $primary 20%;
    }

    ThemeSelector .theme-item.-selected {
        border: thick $accent;
        background: $accent 30%;
    }

    ThemeSelector #theme-preview {
        height: 20;
        border: solid $border;
        padding: 1;
        margin-top: 1;
    }

    ThemeSelector .button-row {
        dock: bottom;
        height: auto;
        width: 100%;
        padding-top: 1;
        align: center middle;
    }

    ThemeSelector Button {
        margin: 0 1;
    }

    ThemeSelector.hidden {
        display: none;
    }
    """

    show_selector: reactive[bool] = reactive(True)
    selected_theme: reactive[str] = reactive("")

    def __init__(self, theme_manager: ThemeManager):
        """
        Initialize theme selector.

        Args:
            theme_manager: ThemeManager instance
        """
        super().__init__()
        self.theme_manager = theme_manager
        self.selected_theme = theme_manager.get_current_theme().name

    def compose(self) -> ComposeResult:
        """Compose the theme selector dialog."""
        with Vertical():
            yield Static(
                "[bold cyan]Theme Selector[/bold cyan]",
                id="title"
            )
            yield Static("", id="theme-list")
            yield Static("", id="theme-preview")

            with Horizontal(classes="button-row"):
                yield Button("Apply", id="apply-button", variant="primary")
                yield Button("Cancel", id="cancel-button")

    def on_mount(self) -> None:
        """Initialize the selector when mounted."""
        self.refresh_theme_list()
        self.refresh_preview()

    def refresh_theme_list(self) -> None:
        """Refresh the theme list display."""
        themes = self.theme_manager.list_themes()

        # Create table
        table = Table(show_header=True, expand=True)
        table.add_column("Theme", style="bold", no_wrap=True)
        table.add_column("Description")
        table.add_column("Author", style="dim")
        table.add_column("", justify="center", no_wrap=True)

        current_theme = self.theme_manager.get_current_theme().name

        for name, theme in sorted(themes.items(), key=lambda x: x[1].display_name):
            # Active indicator
            active = "✓" if name == current_theme else ""

            # Selected indicator
            selected_style = "bold cyan" if name == self.selected_theme else ""

            table.add_row(
                Text(theme.display_name, style=selected_style),
                Text(theme.description, style=selected_style),
                Text(theme.author, style=selected_style),
                Text(active, style="bold green"),
            )

        # Update theme list
        theme_list = self.query_one("#theme-list", Static)
        theme_list.update(table)

    def refresh_preview(self) -> None:
        """Refresh the theme preview."""
        theme = self.theme_manager.get_theme(self.selected_theme)
        if not theme:
            return

        # Create preview panel showing theme colors
        colors = theme.colors

        preview_text = f"""[bold]{theme.display_name}[/bold] - {theme.description}

[dim]Backgrounds:[/dim]
Primary: [on {colors.bg_primary}]        [/]
Secondary: [on {colors.bg_secondary}]        [/]
Tertiary: [on {colors.bg_tertiary}]        [/]

[dim]Accents:[/dim]
[{colors.accent_primary}]● Primary[/]  [{colors.accent_success}]● Success[/]  [{colors.accent_warning}]● Warning[/]  [{colors.accent_error}]● Error[/]

[dim]Text:[/dim]
[{colors.text_primary}]Primary text[/]  [{colors.text_secondary}]Secondary text[/]  [{colors.text_dim}]Dim text[/]
"""

        panel = Panel(
            preview_text,
            title=f"Preview: {theme.display_name}",
            border_style=colors.border_focus,
        )

        preview = self.query_one("#theme-preview", Static)
        preview.update(panel)

    async def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses."""
        if event.button.id == "apply-button":
            # Apply the selected theme
            if self.theme_manager.set_theme(self.selected_theme):
                # Notify app to reload theme
                self.post_message(self.ThemeChanged(self.selected_theme))
                self.add_class("hidden")
        elif event.button.id == "cancel-button":
            # Cancel without applying
            self.selected_theme = self.theme_manager.get_current_theme().name
            self.add_class("hidden")

    async def on_key(self, event) -> None:
        """Handle keyboard input."""
        if event.key == "escape":
            # Cancel on Escape
            self.selected_theme = self.theme_manager.get_current_theme().name
            self.add_class("hidden")
            event.stop()
        elif event.key == "up":
            # Navigate up
            self._select_previous_theme()
            event.stop()
        elif event.key == "down":
            # Navigate down
            self._select_next_theme()
            event.stop()
        elif event.key == "enter":
            # Apply on Enter
            if self.theme_manager.set_theme(self.selected_theme):
                self.post_message(self.ThemeChanged(self.selected_theme))
                self.add_class("hidden")
            event.stop()

    def _select_next_theme(self) -> None:
        """Select the next theme in the list."""
        themes = list(self.theme_manager.list_themes().keys())
        try:
            current_index = themes.index(self.selected_theme)
            next_index = (current_index + 1) % len(themes)
            self.selected_theme = themes[next_index]
            self.refresh_theme_list()
            self.refresh_preview()
        except ValueError:
            pass

    def _select_previous_theme(self) -> None:
        """Select the previous theme in the list."""
        themes = list(self.theme_manager.list_themes().keys())
        try:
            current_index = themes.index(self.selected_theme)
            previous_index = (current_index - 1) % len(themes)
            self.selected_theme = themes[previous_index]
            self.refresh_theme_list()
            self.refresh_preview()
        except ValueError:
            pass

    def show(self) -> None:
        """Show the theme selector with animation."""
        self.remove_class("hidden")
        self.refresh_theme_list()
        self.refresh_preview()

        # Animate entrance
        container = self.query_one(Vertical)
        AnimationHelper.slide_in_from_top(container, duration=OVERLAY_SHOW["duration"])

    def hide(self) -> None:
        """Hide the theme selector with animation."""
        container = self.query_one(Vertical)

        # Animate exit, then hide
        def on_complete():
            self.add_class("hidden")

        AnimationHelper.slide_out_to_top(container, duration=OVERLAY_HIDE["duration"], callback=on_complete)

    # Custom message for theme changes
    class ThemeChanged:
        """Message sent when theme is changed."""

        def __init__(self, theme_name: str):
            self.theme_name = theme_name
