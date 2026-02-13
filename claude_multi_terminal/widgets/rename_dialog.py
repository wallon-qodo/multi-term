"""Modal dialog for renaming sessions."""

from textual.screen import ModalScreen
from textual.widgets import Input, Button, Label
from textual.containers import Vertical, Horizontal
from textual.app import ComposeResult


class RenameDialog(ModalScreen[str]):
    """Modal dialog for renaming a session."""

    DEFAULT_CSS = """
    RenameDialog {
        align: center middle;
    }

    RenameDialog > Vertical {
        background: rgb(30,30,45);
        border: heavy rgb(100,150,255);
        width: 60;
        height: auto;
        padding: 2 3;
    }

    RenameDialog Label {
        padding: 0 0 1 0;
        color: rgb(200,220,255);
        text-style: bold;
    }

    RenameDialog Input {
        margin: 0 0 2 0;
        background: rgb(20,20,30);
        border: solid rgb(80,100,150);
    }

    RenameDialog Input:focus {
        border: solid rgb(120,170,255);
        background: rgb(25,25,35);
    }

    RenameDialog Horizontal {
        height: auto;
        align: center middle;
        padding-top: 1;
    }

    RenameDialog Button {
        margin: 0 1;
        min-width: 12;
    }

    RenameDialog Button#ok-btn {
        background: rgb(50,120,200);
        color: white;
        border: solid rgb(80,150,230);
    }

    RenameDialog Button#ok-btn:hover {
        background: rgb(70,140,220);
    }

    RenameDialog Button#cancel-btn {
        background: rgb(60,60,80);
        color: rgb(200,200,220);
        border: solid rgb(80,80,100);
    }

    RenameDialog Button#cancel-btn:hover {
        background: rgb(80,80,100);
    }
    """

    def __init__(self, current_name: str):
        """
        Initialize rename dialog.

        Args:
            current_name: Current session name
        """
        super().__init__()
        self.current_name = current_name

    def compose(self) -> ComposeResult:
        """Compose the dialog layout."""
        yield Vertical(
            Label("✏ Rename Session"),
            Label("Enter a new name for this session:", markup=False),
            Input(value=self.current_name, id="name-input"),
            Horizontal(
                Button("✓ Confirm", variant="primary", id="ok-btn"),
                Button("✗ Cancel", id="cancel-btn"),
            )
        )

    async def on_mount(self) -> None:
        """Focus the input when mounted."""
        self.query_one("#name-input", Input).focus()

    async def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button clicks."""
        if event.button.id == "ok-btn":
            input_value = self.query_one("#name-input", Input).value
            self.dismiss(input_value if input_value.strip() else None)
        else:
            self.dismiss(None)

    async def on_input_submitted(self, event: Input.Submitted) -> None:
        """Handle Enter key in input field."""
        input_value = event.value
        self.dismiss(input_value if input_value.strip() else None)
