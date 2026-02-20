"""Image gallery widget for multiple images."""

from textual.app import ComposeResult
from textual.widgets import Static, Label, Button, ListView, ListItem
from textual.containers import Vertical, Horizontal, Container, ScrollableContainer
from textual.reactive import reactive
from textual import on
from pathlib import Path
from typing import List, Optional, Callable
import asyncio


class ImageGalleryItem(ListItem):
    """Single item in image gallery."""

    DEFAULT_CSS = """
    ImageGalleryItem {
        width: 100%;
        height: 6;
        background: $panel;
        border: solid $primary;
        padding: 1;
        margin: 0 0 1 0;
    }

    ImageGalleryItem:hover {
        background: $boost;
        border: solid $accent;
    }

    ImageGalleryItem.-selected {
        background: $primary;
        border: thick $accent;
    }
    """

    def __init__(self, image_path: Path, index: int, **kwargs):
        """
        Initialize gallery item.

        Args:
            image_path: Path to image
            index: Item index
        """
        super().__init__(**kwargs)
        self.image_path = image_path
        self.index = index

    def compose(self) -> ComposeResult:
        """Create child widgets."""
        with Horizontal():
            # Thumbnail representation
            yield Static(
                self._generate_thumbnail(),
                classes="gallery-thumbnail"
            )

            # Info
            with Vertical():
                yield Label(f"📷 {self.image_path.name}")
                yield Label(self._get_image_info(), classes="gallery-info")

    def _generate_thumbnail(self) -> str:
        """Generate small thumbnail."""
        if not self.image_path.exists():
            return "[?]"

        try:
            from PIL import Image

            with Image.open(self.image_path) as img:
                # Tiny ASCII art (8x4)
                width, height = 8, 4
                img_resized = img.resize((width, height))
                img_gray = img_resized.convert('L')

                chars = " .:#@"
                lines = []
                for y in range(height):
                    line = ""
                    for x in range(width):
                        pixel = img_gray.getpixel((x, y))
                        char_index = int(pixel / 255 * (len(chars) - 1))
                        line += chars[char_index]
                    lines.append(line)

                return "\n".join(lines)

        except Exception:
            return "[!]"

    def _get_image_info(self) -> str:
        """Get image info."""
        if not self.image_path.exists():
            return "File not found"

        try:
            from PIL import Image

            with Image.open(self.image_path) as img:
                size_kb = self.image_path.stat().st_size / 1024
                return f"{img.width}x{img.height} • {size_kb:.1f} KB"

        except Exception:
            return "Error reading file"


class ImageGallery(Container):
    """
    Image gallery widget for multiple images.

    Features:
    - List view of all images
    - Selection support
    - Batch operations
    - Progress indicators
    - Remove images
    - Upload all

    Usage:
        gallery = ImageGallery()
        await gallery.add_image(path1)
        await gallery.add_image(path2)
        gallery.set_upload_callback(on_upload)
    """

    DEFAULT_CSS = """
    ImageGallery {
        width: 100%;
        height: 100%;
        background: $surface;
        border: thick $primary;
        padding: 1;
    }

    ImageGallery .gallery-header {
        width: 100%;
        height: 3;
        background: $boost;
        padding: 1;
    }

    ImageGallery .gallery-content {
        width: 100%;
        height: 1fr;
        overflow-y: auto;
    }

    ImageGallery .gallery-footer {
        width: 100%;
        height: 3;
        background: $panel;
        padding: 1;
    }

    ImageGallery .gallery-buttons {
        width: 100%;
        height: 3;
        align: center middle;
    }

    ImageGallery Button {
        margin: 0 1;
    }

    ImageGallery .gallery-progress {
        width: 100%;
        height: 1;
        text-align: center;
        color: $accent;
    }
    """

    images: reactive[List[Path]] = reactive(list, layout=True)
    selected_index: reactive[int] = reactive(0)

    def __init__(self, **kwargs):
        """Initialize image gallery."""
        super().__init__(**kwargs)
        self.images = []
        self.upload_callback: Optional[Callable] = None
        self.remove_callback: Optional[Callable] = None

    def compose(self) -> ComposeResult:
        """Create child widgets."""
        with Vertical():
            # Header
            with Horizontal(classes="gallery-header"):
                yield Label(f"Image Gallery ({len(self.images)} images)", id="gallery-title")

            # Content (scrollable list)
            with ScrollableContainer(classes="gallery-content"):
                yield ListView(id="image-list")

            # Progress
            yield Label("", id="gallery-progress", classes="gallery-progress")

            # Footer buttons
            with Horizontal(classes="gallery-buttons"):
                yield Button("Upload All", variant="primary", id="upload-all-btn")
                yield Button("Remove Selected", variant="error", id="remove-btn")
                yield Button("Clear All", id="clear-btn")
                yield Button("Close", id="close-btn")

    async def add_image(self, image_path: Path) -> None:
        """
        Add image to gallery.

        Args:
            image_path: Path to image
        """
        if image_path not in self.images:
            self.images.append(image_path)
            await self._refresh_list()

    async def add_images(self, image_paths: List[Path]) -> None:
        """
        Add multiple images to gallery.

        Args:
            image_paths: List of image paths
        """
        for path in image_paths:
            if path not in self.images:
                self.images.append(path)

        await self._refresh_list()

    async def remove_image(self, index: int) -> None:
        """
        Remove image by index.

        Args:
            index: Image index
        """
        if 0 <= index < len(self.images):
            removed = self.images.pop(index)

            if self.remove_callback:
                await self.remove_callback(removed)

            await self._refresh_list()

    async def clear_all(self) -> None:
        """Clear all images."""
        self.images.clear()
        await self._refresh_list()

    async def _refresh_list(self) -> None:
        """Refresh the image list display."""
        if not self.is_mounted:
            return

        # Update title
        title = self.query_one("#gallery-title", Label)
        title.update(f"Image Gallery ({len(self.images)} images)")

        # Update list
        image_list = self.query_one("#image-list", ListView)
        await image_list.clear()

        for index, image_path in enumerate(self.images):
            item = ImageGalleryItem(image_path, index)
            await image_list.append(item)

    def set_upload_callback(self, callback: Callable) -> None:
        """Set callback for upload action."""
        self.upload_callback = callback

    def set_remove_callback(self, callback: Callable) -> None:
        """Set callback for remove action."""
        self.remove_callback = callback

    async def _update_progress(self, current: int, total: int) -> None:
        """Update progress display."""
        if not self.is_mounted:
            return

        progress = self.query_one("#gallery-progress", Label)

        if current < total:
            percentage = int((current / total) * 100)
            progress.update(f"Uploading: {current}/{total} ({percentage}%)")
        else:
            progress.update("Upload complete!")
            await asyncio.sleep(2)
            progress.update("")

    @on(Button.Pressed, "#upload-all-btn")
    async def on_upload_all_pressed(self, event: Button.Pressed) -> None:
        """Handle upload all button."""
        if not self.images or not self.upload_callback:
            return

        # Upload each image with progress
        for index, image_path in enumerate(self.images):
            await self._update_progress(index, len(self.images))
            await self.upload_callback(image_path)

        await self._update_progress(len(self.images), len(self.images))

    @on(Button.Pressed, "#remove-btn")
    async def on_remove_pressed(self, event: Button.Pressed) -> None:
        """Handle remove selected button."""
        image_list = self.query_one("#image-list", ListView)

        if image_list.index is not None:
            await self.remove_image(image_list.index)

    @on(Button.Pressed, "#clear-btn")
    async def on_clear_pressed(self, event: Button.Pressed) -> None:
        """Handle clear all button."""
        await self.clear_all()

    @on(Button.Pressed, "#close-btn")
    async def on_close_pressed(self, event: Button.Pressed) -> None:
        """Handle close button."""
        await self.remove()

    @on(ListView.Selected)
    async def on_list_item_selected(self, event: ListView.Selected) -> None:
        """Handle list item selection."""
        if event.item and hasattr(event.item, 'index'):
            self.selected_index = event.item.index


class UploadProgressIndicator(Static):
    """
    Progress indicator for image uploads.

    Features:
    - Progress bar
    - Current/Total display
    - File name
    - Cancel button

    Usage:
        progress = UploadProgressIndicator()
        await progress.update_progress(5, 10, "image.png")
    """

    DEFAULT_CSS = """
    UploadProgressIndicator {
        width: 100%;
        height: 5;
        background: $panel;
        border: solid $primary;
        padding: 1;
        margin: 1 0;
    }

    UploadProgressIndicator .progress-bar {
        width: 100%;
        height: 1;
        background: $surface;
        border: solid $primary;
    }

    UploadProgressIndicator .progress-fill {
        height: 1;
        background: $accent;
    }

    UploadProgressIndicator .progress-text {
        width: 100%;
        text-align: center;
        color: $text;
    }
    """

    current: reactive[int] = reactive(0)
    total: reactive[int] = reactive(1)
    filename: reactive[str] = reactive("")

    def __init__(self, **kwargs):
        """Initialize progress indicator."""
        super().__init__(**kwargs)

    def compose(self) -> ComposeResult:
        """Create child widgets."""
        with Vertical():
            yield Label(self.filename, classes="progress-text")
            yield Static(self._render_progress_bar(), id="progress-bar")
            yield Label(
                f"{self.current}/{self.total} ({self._get_percentage()}%)",
                id="progress-label",
                classes="progress-text"
            )

    def _render_progress_bar(self) -> str:
        """Render progress bar."""
        width = 40
        filled = int((self.current / max(self.total, 1)) * width)
        return f"[{'=' * filled}{' ' * (width - filled)}]"

    def _get_percentage(self) -> int:
        """Get percentage."""
        if self.total == 0:
            return 0
        return int((self.current / self.total) * 100)

    async def update_progress(self, current: int, total: int, filename: str = "") -> None:
        """
        Update progress.

        Args:
            current: Current progress
            total: Total items
            filename: Current filename
        """
        self.current = current
        self.total = total
        self.filename = filename

        if self.is_mounted:
            # Update progress bar
            bar = self.query_one("#progress-bar", Static)
            bar.update(self._render_progress_bar())

            # Update label
            label = self.query_one("#progress-label", Label)
            label.update(f"{current}/{total} ({self._get_percentage()}%)")
