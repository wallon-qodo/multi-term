"""Loading indicator widget for lazy-loaded sessions.

This module provides visual feedback during lazy loading operations, including
spinner animations, progress bars, and status messages. Ensures smooth UX
during background loading.

Classes:
    LoadingIndicator: Animated loading widget for lazy operations
    LoadingOverlay: Full-screen overlay for major loading operations
"""

from textual.widget import Widget
from textual.widgets import Static, Label
from textual.containers import Container, Vertical, Horizontal
from textual.reactive import reactive
from rich.text import Text
from rich.spinner import Spinner
import time
from typing import Optional


class LoadingIndicator(Widget):
    """Animated loading indicator for lazy loading operations.

    Shows a spinner and status message during background loading. Automatically
    updates to show progress and completion status.

    Features:
        - Animated spinner using braille patterns
        - Status message updates
        - Progress percentage (optional)
        - Automatic removal on completion

    Example:
        >>> indicator = LoadingIndicator("Loading workspace...")
        >>> await container.mount(indicator)
        >>> indicator.update_status("Loaded 50%")
        >>> indicator.complete("Workspace loaded!")
    """

    DEFAULT_CLASS = "loading-indicator"

    CSS = """
    LoadingIndicator {
        height: auto;
        width: auto;
        background: rgba(40, 40, 40, 0.95);
        border: solid rgb(100, 180, 240);
        padding: 1 2;
        margin: 1;
    }

    LoadingIndicator .spinner {
        color: rgb(100, 180, 240);
        text-style: bold;
    }

    LoadingIndicator .status {
        color: rgb(200, 200, 200);
        padding-left: 1;
    }

    LoadingIndicator.complete {
        border: solid rgb(120, 220, 120);
    }

    LoadingIndicator.complete .spinner {
        color: rgb(120, 220, 120);
    }
    """

    # Braille spinner frames for smooth animation
    SPINNER_FRAMES = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]

    def __init__(
        self,
        message: str = "Loading...",
        show_progress: bool = False,
        *args,
        **kwargs
    ):
        """Initialize loading indicator.

        Args:
            message: Status message to display
            show_progress: Whether to show progress percentage
        """
        super().__init__(*args, **kwargs)
        self.message = message
        self.show_progress = show_progress
        self.progress = 0
        self.frame_index = 0
        self.is_complete = False
        self.start_time = time.time()

    def compose(self):
        """Compose the loading indicator."""
        with Horizontal():
            yield Static("", classes="spinner")
            yield Static(self.message, classes="status")

    def on_mount(self):
        """Start animation when mounted."""
        self.set_interval(0.1, self._update_spinner)

    def _update_spinner(self):
        """Update spinner animation frame."""
        if self.is_complete:
            return

        spinner = self.query_one(".spinner", Static)
        status = self.query_one(".status", Static)

        # Update spinner frame
        self.frame_index = (self.frame_index + 1) % len(self.SPINNER_FRAMES)
        spinner_char = self.SPINNER_FRAMES[self.frame_index]

        # Update text with optional progress
        if self.show_progress and self.progress > 0:
            status_text = f"{self.message} ({self.progress}%)"
        else:
            status_text = self.message

        spinner.update(spinner_char)
        status.update(status_text)

    def update_status(self, message: str, progress: Optional[int] = None):
        """Update status message and progress.

        Args:
            message: New status message
            progress: Progress percentage (0-100)
        """
        self.message = message
        if progress is not None:
            self.progress = max(0, min(100, progress))

    def complete(self, message: str = "Complete!"):
        """Mark loading as complete.

        Args:
            message: Completion message
        """
        self.is_complete = True
        self.add_class("complete")

        spinner = self.query_one(".spinner", Static)
        status = self.query_one(".status", Static)

        elapsed = time.time() - self.start_time
        status_text = f"{message} ({elapsed:.1f}s)"

        spinner.update("✓")
        status.update(status_text)

    def error(self, message: str = "Error loading"):
        """Mark loading as failed.

        Args:
            message: Error message
        """
        self.is_complete = True
        self.remove_class("complete")
        self.styles.border = ("solid", "rgb(255, 77, 77)")

        spinner = self.query_one(".spinner", Static)
        status = self.query_one(".status", Static)

        spinner.update("✗")
        status.update(message)
        spinner.styles.color = "rgb(255, 77, 77)"


class LoadingOverlay(Container):
    """Full-screen loading overlay for major operations.

    Displays a centered loading indicator that blocks interaction during
    critical loading operations. Useful for workspace switches or initial
    application load.

    Example:
        >>> overlay = LoadingOverlay("Switching workspace...")
        >>> await app.mount(overlay)
        >>> # ... perform loading ...
        >>> overlay.complete()
        >>> await overlay.remove()
    """

    DEFAULT_CLASS = "loading-overlay"

    CSS = """
    LoadingOverlay {
        width: 100%;
        height: 100%;
        background: rgba(0, 0, 0, 0.85);
        align: center middle;
        layer: overlay;
    }

    LoadingOverlay Vertical {
        width: auto;
        height: auto;
        background: rgb(32, 32, 32);
        border: solid rgb(100, 180, 240);
        padding: 2 4;
    }

    LoadingOverlay Label {
        text-align: center;
        color: rgb(240, 240, 240);
        text-style: bold;
        margin: 1;
    }
    """

    def __init__(
        self,
        message: str = "Loading...",
        show_progress: bool = False,
        *args,
        **kwargs
    ):
        """Initialize loading overlay.

        Args:
            message: Loading message
            show_progress: Whether to show progress
        """
        super().__init__(*args, **kwargs)
        self.message = message
        self.show_progress = show_progress
        self.indicator = None

    def compose(self):
        """Compose the loading overlay."""
        with Vertical():
            yield Label("🔄 Loading")
            self.indicator = LoadingIndicator(
                message=self.message,
                show_progress=self.show_progress
            )
            yield self.indicator

    def update_status(self, message: str, progress: Optional[int] = None):
        """Update loading status.

        Args:
            message: New status message
            progress: Progress percentage
        """
        if self.indicator:
            self.indicator.update_status(message, progress)

    def complete(self, message: str = "Complete!"):
        """Mark loading as complete.

        Args:
            message: Completion message
        """
        if self.indicator:
            self.indicator.complete(message)

    def error(self, message: str = "Error loading"):
        """Mark loading as failed.

        Args:
            message: Error message
        """
        if self.indicator:
            self.indicator.error(message)


class MinimalLoadingIndicator(Static):
    """Minimal inline loading indicator.

    Lightweight loading indicator that can be embedded inline in other widgets.
    Uses a simple spinner without borders or backgrounds.

    Example:
        >>> indicator = MinimalLoadingIndicator()
        >>> await widget.mount(indicator)
        >>> indicator.stop("Done!")
    """

    # Compact spinner frames
    SPINNER_FRAMES = ["◐", "◓", "◑", "◒"]

    def __init__(self, message: str = "Loading...", *args, **kwargs):
        """Initialize minimal indicator.

        Args:
            message: Loading message
        """
        super().__init__("", *args, **kwargs)
        self.message = message
        self.frame_index = 0
        self.is_running = True
        self.interval = None

    def on_mount(self):
        """Start animation."""
        self.interval = self.set_interval(0.15, self._update)
        self._update()

    def _update(self):
        """Update spinner frame."""
        if not self.is_running:
            return

        self.frame_index = (self.frame_index + 1) % len(self.SPINNER_FRAMES)
        spinner_char = self.SPINNER_FRAMES[self.frame_index]

        text = Text()
        text.append(spinner_char, style="bold cyan")
        text.append(f" {self.message}", style="dim")

        self.update(text)

    def stop(self, message: str = ""):
        """Stop animation and show final message.

        Args:
            message: Final message to display
        """
        self.is_running = False
        if self.interval:
            self.interval.stop()

        text = Text()
        text.append("✓", style="bold green")
        if message:
            text.append(f" {message}", style="")

        self.update(text)

    def update_message(self, message: str):
        """Update loading message.

        Args:
            message: New message
        """
        self.message = message
