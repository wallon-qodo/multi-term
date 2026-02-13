"""Dialog for saving code blocks to files."""

from textual.screen import ModalScreen
from textual.widgets import Static, Input, Button
from textual.containers import Container, Vertical, Horizontal
from textual.app import ComposeResult
from rich.text import Text
import os
from pathlib import Path


class SaveFileDialog(ModalScreen[str]):
    """
    Modal dialog for saving code to a file.

    Features:
    - Filename input with suggestions
    - Working directory display
    - Cancel/Save buttons
    - Beautiful Homebrew theme styling
    - Input validation
    """

    DEFAULT_CSS = """
    SaveFileDialog {
        align: center middle;
    }

    SaveFileDialog > Container {
        width: 70;
        height: auto;
        background: rgb(32,32,32);
        border: heavy rgb(255,77,77);
        padding: 0;
    }

    SaveFileDialog .dialog-header {
        height: 3;
        width: 100%;
        background: rgb(40,40,40);
        border-bottom: solid rgb(255,77,77);
        color: rgb(255,100,100);
        padding: 1 2;
        content-align: left middle;
    }

    SaveFileDialog .dialog-content {
        width: 100%;
        height: auto;
        background: rgb(32,32,32);
        padding: 2;
    }

    SaveFileDialog .field-label {
        height: 1;
        width: 100%;
        color: rgb(200,200,200);
        padding: 0 0 0 0;
        margin: 1 0 0 0;
    }

    SaveFileDialog Input {
        width: 100%;
        background: rgb(40,40,40);
        border: solid rgb(100,100,100);
        color: rgb(240,240,240);
        margin: 0 0 1 0;
    }

    SaveFileDialog Input:focus {
        border: solid rgb(255,77,77);
        background: rgb(42,42,42);
    }

    SaveFileDialog .info-text {
        height: auto;
        width: 100%;
        color: rgb(150,150,150);
        padding: 0;
        margin: 0 0 1 0;
    }

    SaveFileDialog .dialog-buttons {
        height: 3;
        width: 100%;
        background: rgb(32,32,32);
        border-top: solid rgb(60,60,60);
        padding: 0 2;
        layout: horizontal;
        align: right middle;
    }

    SaveFileDialog Button {
        height: 1;
        min-width: 12;
        margin-left: 1;
        padding: 0 2;
    }

    SaveFileDialog .cancel-btn {
        background: rgb(42,42,42);
        color: rgb(200,200,200);
        border: solid rgb(100,100,100);
    }

    SaveFileDialog .cancel-btn:hover {
        background: rgb(60,60,60);
        border: solid rgb(150,150,150);
    }

    SaveFileDialog .save-btn {
        background: rgb(76,175,80);
        color: rgb(255,255,255);
        border: solid rgb(129,199,132);
    }

    SaveFileDialog .save-btn:hover {
        background: rgb(102,187,106);
        border: solid rgb(165,214,167);
    }

    SaveFileDialog .save-btn:focus {
        background: rgb(102,187,106);
        border: solid rgb(165,214,167);
    }

    SaveFileDialog .error-message {
        height: auto;
        width: 100%;
        background: rgba(239,83,80,0.2);
        border: solid rgb(255,77,77);
        color: rgb(244,143,177);
        padding: 1 2;
        margin: 1 0;
        display: none;
    }

    SaveFileDialog .error-message.visible {
        display: block;
    }
    """

    def __init__(
        self,
        suggested_name: str = "code.txt",
        code_content: str = "",
        **kwargs
    ):
        """
        Initialize save file dialog.

        Args:
            suggested_name: Suggested filename
            code_content: Code content to save
        """
        super().__init__(**kwargs)
        self.suggested_name = suggested_name
        self.code_content = code_content
        self.working_dir = os.getcwd()

    def compose(self) -> ComposeResult:
        """Compose the dialog layout."""
        with Container():
            # Header
            header_text = Text()
            header_text.append("💾 ", style="")
            header_text.append("Save Code to File", style="bold rgb(255,100,100)")
            yield Static(header_text, classes="dialog-header")

            # Content
            with Vertical(classes="dialog-content"):
                # Working directory info
                info_text = Text()
                info_text.append("📁 Working Directory:\n", style="dim rgb(150,150,150)")
                info_text.append(self.working_dir, style="dim cyan")
                yield Static(info_text, classes="info-text")

                # Filename input
                yield Static("Filename:", classes="field-label")
                yield Input(
                    value=self.suggested_name,
                    placeholder="Enter filename...",
                    id="filename-input"
                )

                # Error message (hidden by default)
                yield Static(
                    "⚠ Error: File already exists or invalid filename",
                    classes="error-message",
                    id="error-message"
                )

            # Buttons
            with Horizontal(classes="dialog-buttons"):
                yield Button("Cancel", id="cancel-btn", classes="cancel-btn")
                yield Button("Save", id="save-btn", classes="save-btn")

    async def on_mount(self) -> None:
        """Focus the input field when dialog opens."""
        input_widget = self.query_one("#filename-input", Input)
        input_widget.focus()
        # Select the filename without extension for easy editing
        if "." in self.suggested_name:
            base_name = self.suggested_name.rsplit(".", 1)[0]
            input_widget.cursor_position = len(base_name)

    async def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses."""
        if event.button.id == "cancel-btn":
            self.dismiss(None)
        elif event.button.id == "save-btn":
            await self._handle_save()
        event.stop()

    async def on_input_submitted(self, event: Input.Submitted) -> None:
        """Handle Enter key in input field."""
        await self._handle_save()
        event.stop()

    async def _handle_save(self) -> None:
        """Validate and save the file."""
        input_widget = self.query_one("#filename-input", Input)
        filename = input_widget.value.strip()

        # Validate filename
        if not filename:
            self._show_error("Please enter a filename")
            return

        # Check for invalid characters
        if any(char in filename for char in ['/', '\\', '\0', '<', '>', ':', '"', '|', '?', '*']):
            self._show_error("Filename contains invalid characters")
            return

        # Build full path
        full_path = os.path.join(self.working_dir, filename)

        # Check if file exists (warn but allow overwrite)
        if os.path.exists(full_path):
            # In a real implementation, you might want to show a confirmation dialog
            # For now, we'll just allow overwrite
            pass

        # Write the file
        try:
            Path(full_path).write_text(self.code_content, encoding='utf-8')
            self.dismiss(full_path)
        except Exception as e:
            self._show_error(f"Failed to save: {str(e)}")

    def _show_error(self, message: str) -> None:
        """
        Show an error message in the dialog.

        Args:
            message: Error message to display
        """
        error_widget = self.query_one("#error-message", Static)
        error_widget.update(f"⚠ Error: {message}")
        error_widget.add_class("visible")

        # Hide error after 3 seconds
        if hasattr(self, 'app') and self.app:
            self.app.set_timer(3.0, lambda: error_widget.remove_class("visible"))

    def on_key(self, event) -> None:
        """Handle Escape key to close dialog."""
        if event.key == "escape":
            self.dismiss(None)
            event.stop()
