"""Image preview widget with thumbnail display."""

from textual.app import ComposeResult
from textual.widgets import Static, Label, Button
from textual.containers import Vertical, Horizontal, Container
from textual.reactive import reactive
from textual.message import Message
from textual import on
from pathlib import Path
from typing import Optional, Callable
import asyncio


class ImagePreview(Container):
    """
    Widget to preview images before uploading.

    Features:
    - Thumbnail display
    - Image metadata (size, dimensions, format)
    - Send/Cancel buttons
    - Drag to reposition
    - ESC to close

    Usage:
        preview = ImagePreview(image_path)
        preview.set_send_callback(on_send)
        await app.mount(preview)
    """

    DEFAULT_CSS = """
    ImagePreview {
        width: 100%;
        height: auto;
        background: $surface;
        border: thick $primary;
        padding: 1;
    }

    ImagePreview > Vertical {
        width: 100%;
        height: auto;
    }

    ImagePreview .preview-header {
        width: 100%;
        height: 3;
        background: $boost;
        padding: 1;
        text-align: center;
    }

    ImagePreview .preview-content {
        width: 100%;
        height: auto;
        padding: 1;
    }

    ImagePreview .preview-thumbnail {
        width: 100%;
        height: 20;
        background: $panel;
        border: solid $primary;
        text-align: center;
        content-align: center middle;
    }

    ImagePreview .preview-metadata {
        width: 100%;
        height: auto;
        padding: 1;
        text-align: center;
    }

    ImagePreview .preview-buttons {
        width: 100%;
        height: 3;
        align: center middle;
    }

    ImagePreview Button {
        margin: 0 1;
    }
    """

    image_path: reactive[Optional[Path]] = reactive(None)

    def __init__(self, image_path: Optional[Path] = None, **kwargs):
        """
        Initialize image preview.

        Args:
            image_path: Path to image to preview
        """
        super().__init__(**kwargs)
        self.image_path = image_path
        self.send_callback: Optional[Callable] = None
        self.cancel_callback: Optional[Callable] = None

    def compose(self) -> ComposeResult:
        """Create child widgets."""
        with Vertical():
            yield Label("Image Preview", classes="preview-header")

            with Vertical(classes="preview-content"):
                # Thumbnail (ASCII art representation)
                yield Static(
                    self._generate_thumbnail_display(),
                    id="thumbnail",
                    classes="preview-thumbnail"
                )

                # Metadata
                yield Static(
                    self._generate_metadata(),
                    id="metadata",
                    classes="preview-metadata"
                )

            # Buttons
            with Horizontal(classes="preview-buttons"):
                yield Button("Send", variant="primary", id="send-btn")
                yield Button("Cancel", variant="error", id="cancel-btn")

    def _generate_thumbnail_display(self) -> str:
        """Generate ASCII art thumbnail representation."""
        if not self.image_path or not self.image_path.exists():
            return "[No Image]"

        try:
            from PIL import Image

            with Image.open(self.image_path) as img:
                # Create small ASCII art
                width, height = 40, 15
                img_resized = img.resize((width, height))
                img_gray = img_resized.convert('L')

                # ASCII gradient
                chars = " .:-=+*#%@"

                lines = []
                for y in range(height):
                    line = ""
                    for x in range(width):
                        pixel = img_gray.getpixel((x, y))
                        char_index = int(pixel / 255 * (len(chars) - 1))
                        line += chars[char_index]
                    lines.append(line)

                return "\n".join(lines)

        except Exception as e:
            return f"[Preview Error: {e}]"

    def _generate_metadata(self) -> str:
        """Generate metadata display."""
        if not self.image_path or not self.image_path.exists():
            return "No metadata available"

        try:
            from PIL import Image

            with Image.open(self.image_path) as img:
                size_kb = self.image_path.stat().st_size / 1024

                return (
                    f"File: {self.image_path.name}\n"
                    f"Format: {img.format}\n"
                    f"Size: {img.width}x{img.height}\n"
                    f"File Size: {size_kb:.1f} KB"
                )

        except Exception as e:
            return f"Metadata error: {e}"

    def set_send_callback(self, callback: Callable) -> None:
        """Set callback for send button."""
        self.send_callback = callback

    def set_cancel_callback(self, callback: Callable) -> None:
        """Set callback for cancel button."""
        self.cancel_callback = callback

    @on(Button.Pressed, "#send-btn")
    async def on_send_pressed(self, event: Button.Pressed) -> None:
        """Handle send button press."""
        if self.send_callback and self.image_path:
            await self.send_callback(self.image_path)
        await self.remove()

    @on(Button.Pressed, "#cancel-btn")
    async def on_cancel_pressed(self, event: Button.Pressed) -> None:
        """Handle cancel button press."""
        if self.cancel_callback:
            await self.cancel_callback()
        await self.remove()

    def watch_image_path(self, new_path: Optional[Path]) -> None:
        """React to image path changes."""
        if self.is_mounted:
            # Update thumbnail
            thumbnail = self.query_one("#thumbnail", Static)
            thumbnail.update(self._generate_thumbnail_display())

            # Update metadata
            metadata = self.query_one("#metadata", Static)
            metadata.update(self._generate_metadata())


class CompactImagePreview(Static):
    """
    Compact inline image preview for chat.

    Features:
    - Small thumbnail
    - Inline display
    - Click to expand

    Usage:
        preview = CompactImagePreview(image_path)
        container.mount(preview)
    """

    DEFAULT_CSS = """
    CompactImagePreview {
        width: auto;
        height: 5;
        background: $panel;
        border: solid $primary;
        padding: 1;
        margin: 0 1;
    }

    CompactImagePreview:hover {
        border: solid $accent;
        background: $boost;
    }
    """

    def __init__(self, image_path: Path, **kwargs):
        """
        Initialize compact preview.

        Args:
            image_path: Path to image
        """
        super().__init__(**kwargs)
        self.image_path = image_path
        self.update(self._generate_compact_display())

    def _generate_compact_display(self) -> str:
        """Generate compact display."""
        if not self.image_path.exists():
            return "[Image Not Found]"

        try:
            from PIL import Image

            with Image.open(self.image_path) as img:
                size_kb = self.image_path.stat().st_size / 1024
                return (
                    f"📷 {self.image_path.name}\n"
                    f"   {img.width}x{img.height} • {size_kb:.1f} KB"
                )

        except Exception:
            return f"📷 {self.image_path.name}"

    async def on_click(self, event) -> None:
        """Handle click to expand."""
        # Post message to parent to show full preview
        self.post_message(self.ImageClicked(self, self.image_path))

    class ImageClicked(Message):
        """Message when image is clicked."""

        def __init__(self, sender, image_path: Path):
            super().__init__()
            self.sender = sender
            self.image_path = image_path
