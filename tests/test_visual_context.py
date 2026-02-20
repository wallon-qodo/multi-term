"""Tests for Phase 5: Visual Context & Images."""

import pytest
import asyncio
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch, AsyncMock
from PIL import Image

from claude_multi_terminal.visual import (
    ScreenshotCapture,
    ScreenshotMode,
    ImageHandler,
    ImageFormat,
    OCRProcessor,
    OCREngine,
)


class TestScreenshotCapture:
    """Test screenshot capture functionality."""

    @pytest.fixture
    def capture(self):
        """Create screenshot capture instance."""
        return ScreenshotCapture()

    @pytest.fixture
    def temp_image(self):
        """Create temporary test image."""
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as f:
            img = Image.new('RGB', (100, 100), color='red')
            img.save(f.name)
            yield Path(f.name)
            Path(f.name).unlink(missing_ok=True)

    def test_initialization(self, capture):
        """Test capture initialization."""
        assert capture.temp_dir.exists()
        assert capture.last_screenshot is None

    def test_set_preview_callback(self, capture):
        """Test setting preview callback."""
        callback = Mock()
        capture.set_preview_callback(callback)
        assert capture.preview_callback == callback

    @pytest.mark.asyncio
    async def test_cleanup_old_screenshots(self, capture):
        """Test cleanup of old screenshots."""
        # Create old screenshot
        old_file = capture.temp_dir / "screenshot_1000.png"
        old_file.touch()

        # Wait a moment
        await asyncio.sleep(0.1)

        # Cleanup with 0 seconds max age
        capture.cleanup_old_screenshots(max_age_seconds=0)

        # File should be deleted
        assert not old_file.exists()

    def test_get_last_screenshot(self, capture, temp_image):
        """Test getting last screenshot."""
        capture.last_screenshot = temp_image
        assert capture.get_last_screenshot() == temp_image


class TestImageHandler:
    """Test image handling functionality."""

    @pytest.fixture
    def handler(self):
        """Create image handler instance."""
        return ImageHandler()

    @pytest.fixture
    def test_image(self):
        """Create test image."""
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as f:
            img = Image.new('RGB', (200, 200), color='blue')
            img.save(f.name)
            yield Path(f.name)
            Path(f.name).unlink(missing_ok=True)

    def test_initialization(self, handler):
        """Test handler initialization."""
        assert handler.temp_dir.exists()
        assert handler.max_size_bytes == 10 * 1024 * 1024

    def test_set_callbacks(self, handler):
        """Test setting callbacks."""
        upload_cb = Mock()
        progress_cb = Mock()

        handler.set_upload_callback(upload_cb)
        handler.set_progress_callback(progress_cb)

        assert handler.upload_callback == upload_cb
        assert handler.progress_callback == progress_cb

    def test_is_image_file(self, handler):
        """Test image file detection."""
        assert handler._is_image_file(Path("test.png"))
        assert handler._is_image_file(Path("test.jpg"))
        assert handler._is_image_file(Path("test.jpeg"))
        assert handler._is_image_file(Path("test.gif"))
        assert not handler._is_image_file(Path("test.txt"))
        assert not handler._is_image_file(Path("test.py"))

    @pytest.mark.asyncio
    async def test_get_image_info(self, handler, test_image):
        """Test getting image information."""
        info = await handler._get_image_info(test_image)

        assert info is not None
        assert info.path == test_image
        assert info.width == 200
        assert info.height == 200
        assert info.size_bytes > 0
        assert info.thumbnail is not None

    @pytest.mark.asyncio
    async def test_handle_drop_single(self, handler, test_image):
        """Test handling single dropped image."""
        images = await handler.handle_drop([str(test_image)])

        assert len(images) == 1
        assert images[0].path == test_image

    @pytest.mark.asyncio
    async def test_handle_drop_multiple(self, handler):
        """Test handling multiple dropped images."""
        # Create multiple test images
        images_to_drop = []
        for i in range(3):
            with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as f:
                img = Image.new('RGB', (100, 100), color='red')
                img.save(f.name)
                images_to_drop.append(f.name)

        try:
            images = await handler.handle_drop(images_to_drop)
            assert len(images) == 3

        finally:
            for img_path in images_to_drop:
                Path(img_path).unlink(missing_ok=True)

    @pytest.mark.asyncio
    async def test_handle_drop_non_image(self, handler):
        """Test handling non-image files."""
        with tempfile.NamedTemporaryFile(suffix='.txt', delete=False) as f:
            f.write(b"not an image")
            txt_path = f.name

        try:
            images = await handler.handle_drop([txt_path])
            assert len(images) == 0

        finally:
            Path(txt_path).unlink(missing_ok=True)

    @pytest.mark.asyncio
    async def test_convert_format(self, handler, test_image):
        """Test image format conversion."""
        converted = await handler.convert_format(test_image, ImageFormat.JPEG)

        assert converted is not None
        assert converted.exists()
        assert converted.suffix == '.jpeg'

        # Cleanup
        converted.unlink()

    @pytest.mark.asyncio
    async def test_optimize_image(self, handler):
        """Test image optimization."""
        # Create large test image
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as f:
            img = Image.new('RGB', (3000, 3000), color='green')
            img.save(f.name)
            large_image = Path(f.name)

        try:
            optimized = await handler.optimize_image(large_image, max_dimension=1024)

            assert optimized is not None
            assert optimized.exists()

            # Check size was reduced
            with Image.open(optimized) as opt_img:
                assert opt_img.width <= 1024
                assert opt_img.height <= 1024

            # Cleanup
            optimized.unlink()

        finally:
            large_image.unlink(missing_ok=True)

    def test_get_image_base64(self, handler, test_image):
        """Test base64 encoding."""
        b64 = handler.get_image_base64(test_image)

        assert b64 is not None
        assert isinstance(b64, str)
        assert len(b64) > 0

    @pytest.mark.asyncio
    async def test_cleanup_old_images(self, handler):
        """Test cleanup of old images."""
        # Create old image
        old_file = handler.temp_dir / "paste_1000.png"
        old_file.touch()

        # Wait
        await asyncio.sleep(0.1)

        # Cleanup
        handler.cleanup_old_images(max_age_seconds=0)

        # Should be deleted
        assert not old_file.exists()


class TestOCRProcessor:
    """Test OCR functionality."""

    @pytest.fixture
    def processor(self):
        """Create OCR processor."""
        return OCRProcessor()

    @pytest.fixture
    def text_image(self):
        """Create image with text."""
        from PIL import ImageDraw, ImageFont

        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as f:
            img = Image.new('RGB', (400, 100), color='white')
            draw = ImageDraw.Draw(img)

            # Draw text
            try:
                font = ImageFont.truetype("Arial.ttf", 36)
            except:
                font = ImageFont.load_default()

            draw.text((10, 30), "Hello World", fill='black', font=font)
            img.save(f.name)

            yield Path(f.name)
            Path(f.name).unlink(missing_ok=True)

    def test_initialization(self, processor):
        """Test processor initialization."""
        assert isinstance(processor.available_engines, list)

    def test_get_available_engines(self, processor):
        """Test getting available engines."""
        engines = processor.get_available_engines()
        assert isinstance(engines, list)

    @pytest.mark.asyncio
    async def test_preprocess_for_ocr(self, processor, text_image):
        """Test image preprocessing."""
        preprocessed = await processor.preprocess_for_ocr(text_image)

        if preprocessed:
            assert preprocessed.exists()
            preprocessed.unlink()

    def test_search_text(self, processor):
        """Test text search in OCR results."""
        from claude_multi_terminal.visual.ocr import OCRResult

        result = OCRResult(
            text="Hello World Test",
            confidence=0.95,
            bounding_boxes=[(0, 0, 100, 20)],
            language='eng',
            engine=OCREngine.TESSERACT
        )

        matches = processor.search_text(result, "Hello")
        assert len(matches) > 0


class TestImageWidgets:
    """Test image preview and gallery widgets."""

    @pytest.mark.asyncio
    async def test_image_preview_initialization(self):
        """Test ImagePreview widget initialization."""
        from claude_multi_terminal.widgets import ImagePreview

        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as f:
            img = Image.new('RGB', (100, 100), color='red')
            img.save(f.name)
            test_path = Path(f.name)

        try:
            preview = ImagePreview(test_path)
            assert preview.image_path == test_path

        finally:
            test_path.unlink(missing_ok=True)

    @pytest.mark.asyncio
    async def test_compact_image_preview(self):
        """Test CompactImagePreview widget."""
        from claude_multi_terminal.widgets.image_preview import CompactImagePreview

        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as f:
            img = Image.new('RGB', (100, 100), color='blue')
            img.save(f.name)
            test_path = Path(f.name)

        try:
            preview = CompactImagePreview(test_path)
            assert preview.image_path == test_path

        finally:
            test_path.unlink(missing_ok=True)

    @pytest.mark.asyncio
    async def test_image_gallery_initialization(self):
        """Test ImageGallery widget initialization."""
        from claude_multi_terminal.widgets import ImageGallery

        gallery = ImageGallery()
        assert gallery.images == []

    @pytest.mark.asyncio
    async def test_image_gallery_add_image(self):
        """Test adding images to gallery."""
        from claude_multi_terminal.widgets import ImageGallery

        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as f:
            img = Image.new('RGB', (100, 100), color='green')
            img.save(f.name)
            test_path = Path(f.name)

        try:
            gallery = ImageGallery()
            await gallery.add_image(test_path)
            assert len(gallery.images) == 1
            assert test_path in gallery.images

        finally:
            test_path.unlink(missing_ok=True)


@pytest.mark.integration
class TestVisualContextIntegration:
    """Integration tests for visual context system."""

    @pytest.mark.asyncio
    async def test_full_screenshot_workflow(self):
        """Test complete screenshot capture workflow."""
        capture = ScreenshotCapture()
        handler = ImageHandler()

        # Set up callbacks
        preview_called = False
        uploaded = []

        async def on_preview(path):
            nonlocal preview_called
            preview_called = True

        async def on_upload(path):
            uploaded.append(path)

        capture.set_preview_callback(on_preview)
        handler.set_upload_callback(on_upload)

        # Test would capture screenshot here in real scenario
        # For test, we create a mock screenshot
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as f:
            img = Image.new('RGB', (100, 100), color='white')
            img.save(f.name)
            mock_screenshot = Path(f.name)

        try:
            # Simulate upload
            info = await handler._get_image_info(mock_screenshot)
            assert info is not None
            assert info.width == 100
            assert info.height == 100

        finally:
            mock_screenshot.unlink(missing_ok=True)

    @pytest.mark.asyncio
    async def test_drag_drop_workflow(self):
        """Test drag-and-drop workflow."""
        handler = ImageHandler()
        gallery = None  # Would be ImageGallery widget

        # Create test images
        test_images = []
        for i in range(3):
            with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as f:
                img = Image.new('RGB', (100, 100), color='red')
                img.save(f.name)
                test_images.append(f.name)

        try:
            # Handle drop
            images = await handler.handle_drop(test_images)
            assert len(images) == 3

            # All images should have valid info
            for img_info in images:
                assert img_info.width == 100
                assert img_info.height == 100
                assert img_info.thumbnail is not None

        finally:
            for img_path in test_images:
                Path(img_path).unlink(missing_ok=True)


def test_visual_module_imports():
    """Test that all visual modules can be imported."""
    from claude_multi_terminal.visual import (
        ScreenshotCapture,
        ScreenshotMode,
        ImageHandler,
        ImageFormat,
        OCRProcessor,
        OCREngine,
    )

    assert ScreenshotCapture is not None
    assert ScreenshotMode is not None
    assert ImageHandler is not None
    assert ImageFormat is not None
    assert OCRProcessor is not None
    assert OCREngine is not None


def test_widget_imports():
    """Test that image widgets can be imported."""
    from claude_multi_terminal.widgets import (
        ImagePreview,
        CompactImagePreview,
        ImageGallery,
        ImageGalleryItem,
        UploadProgressIndicator,
    )

    assert ImagePreview is not None
    assert CompactImagePreview is not None
    assert ImageGallery is not None
    assert ImageGalleryItem is not None
    assert UploadProgressIndicator is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
