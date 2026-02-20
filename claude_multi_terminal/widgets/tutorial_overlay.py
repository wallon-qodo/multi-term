"""
Tutorial overlay widget.

Displays the interactive tutorial as an overlay on top of the main UI.
"""

from textual.app import ComposeResult
from textual.containers import Container, Vertical
from textual.widgets import Static
from textual.reactive import reactive
from rich.panel import Panel
from rich.console import Group
from rich.markdown import Markdown

from ..tutorial import Tutorial
from ..animations import AnimationHelper, OVERLAY_SHOW


class TutorialOverlay(Container):
    """
    Tutorial overlay widget.

    Displays tutorial steps as a modal overlay with backdrop.
    """

    DEFAULT_CSS = """
    TutorialOverlay {
        dock: top;
        height: 100%;
        width: 100%;
        background: rgba(0, 0, 0, 0.7);
        layer: tutorial;
        align: center middle;
    }

    TutorialOverlay > Vertical {
        width: 80;
        height: auto;
        background: rgb(28,28,28);
        border: thick cyan;
        padding: 2 4;
    }

    TutorialOverlay Static {
        width: 100%;
        height: auto;
    }

    TutorialOverlay.hidden {
        display: none;
    }
    """

    show_overlay: reactive[bool] = reactive(True)

    def __init__(self, tutorial: Tutorial):
        """
        Initialize the tutorial overlay.

        Args:
            tutorial: The tutorial instance to display
        """
        super().__init__()
        self.tutorial = tutorial
        self.add_class("hidden")

    def compose(self) -> ComposeResult:
        """Compose the tutorial overlay."""
        with Vertical():
            yield Static(id="tutorial-content")

    def on_mount(self) -> None:
        """Initialize the overlay when mounted."""
        self.refresh_content()

        # Animate entrance if tutorial is active
        if self.tutorial.active:
            container = self.query_one(Vertical)
            AnimationHelper.slide_in_from_bottom(container, duration=OVERLAY_SHOW["duration"])

    def refresh_content(self) -> None:
        """Refresh the tutorial content."""
        if not self.tutorial.active:
            self.add_class("hidden")
            return

        self.remove_class("hidden")

        step = self.tutorial.get_current_step()
        if not step:
            self.add_class("hidden")
            return

        # Build content
        content_parts = []

        # Description
        content_parts.append(Markdown(step.description))

        # Instruction box
        content_parts.append("\n")
        instruction_panel = Panel(
            Markdown(step.instruction),
            title="📋 What to do",
            border_style="yellow",
            padding=(0, 1),
        )
        content_parts.append(instruction_panel)

        # Hint (if any)
        if step.hint:
            content_parts.append("\n")
            content_parts.append(f"[dim italic]💡 {step.hint}[/dim italic]")

        # Progress and skip option
        content_parts.append("\n")
        content_parts.append(
            f"[dim]{self.tutorial.get_progress()} • "
            f"Press Ctrl+Shift+Q to skip tutorial[/dim]"
        )

        # Create panel
        panel = Panel(
            Group(*content_parts),
            title=f"[bold cyan]Tutorial: {step.title}[/bold cyan]",
            border_style="cyan",
            padding=(1, 2),
        )

        # Update content
        content_widget = self.query_one("#tutorial-content", Static)
        content_widget.update(panel)

    def handle_key(self, key: str) -> bool:
        """
        Handle a key press during tutorial.

        Args:
            key: The key pressed

        Returns:
            bool: True if tutorial handled the key
        """
        handled = self.tutorial.handle_key(key)
        if handled:
            self.refresh_content()
        return handled

    def handle_mode_change(self, new_mode: str) -> bool:
        """
        Handle a mode change during tutorial.

        Args:
            new_mode: The new mode

        Returns:
            bool: True if tutorial handled the mode change
        """
        handled = self.tutorial.handle_mode_change(new_mode)
        if handled:
            self.refresh_content()
        return handled

    def handle_action(self, action: str) -> bool:
        """
        Handle an action during tutorial.

        Args:
            action: The action performed

        Returns:
            bool: True if tutorial handled the action
        """
        handled = self.tutorial.handle_action(action)
        if handled:
            self.refresh_content()
        return handled

    def skip_tutorial(self) -> None:
        """Skip the tutorial."""
        self.tutorial.skip()
        self.add_class("hidden")
