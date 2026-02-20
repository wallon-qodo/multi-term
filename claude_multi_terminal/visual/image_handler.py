"""Image handling for clipboard paste and drag-drop."""

import asyncio
import base64
import tempfile
from pathlib import Path
from enum import Enum
from typing import Optional, List, Callable, Dict, Any
from dataclasses import dataclass
import io


class ImageFormat(Enum):
    """Supported image formats."""
    PNG = "png"
    JPEG = "jpeg"
    JPG = "jpg"
    GIF = "gif"
    WEBP = "webp"
    BMP = "bmp"


@dataclass
class ImageInfo:
    """Information about an image."""
    path: Path
    format: ImageFormat
    width: int
    height: int
    size_bytes: int
    thumbnail: Optional[bytes] = None


class ImageHandler:
    """
    Handle image paste, drag-drop, and conversion.

    Features:
    - Clipboard paste detection
    - Drag & drop support
    - Format conversion
    - Thumbnail generation
    - Multiple image support
    - Progress indicators

    Usage:
        handler = ImageHandler()
        image = await handler.paste_from_clipboard()
        images = await handler.handle_drop(file_paths)
    """

    def __init__(self, max_size_mb: int = 10):
        """
        Initialize image handler.

        Args:
            max_size_mb: Maximum image size in MB
        """
        self.temp_dir = Path(tempfile.gettempdir()) / "claude_images"
        self.temp_dir.mkdir(parents=True, exist_ok=True)
        self.max_size_bytes = max_size_mb * 1024 * 1024
        self.upload_callback: Optional[Callable] = None
        self.progress_callback: Optional[Callable] = None

    def set_upload_callback(self, callback: Callable) -> None:
        """Set callback for image upload."""
        self.upload_callback = callback

    def set_progress_callback(self, callback: Callable) -> None:
        """Set callback for upload progress."""
        self.progress_callback = callback

    async def paste_from_clipboard(self) -> Optional[ImageInfo]:
        """
        Paste image from clipboard.

        Returns:
            ImageInfo if image found, None otherwise
        """
        try:
            import platform

            system = platform.system()

            if system == "Darwin":  # macOS
                # Use pngpaste or osascript
                return await self._paste_macos()

            elif system == "Linux":
                # Use xclip or wl-paste
                return await self._paste_linux()

            elif system == "Windows":
                # Use PIL ImageGrab
                return await self._paste_windows()

            return None

        except Exception as e:
            print(f"Clipboard paste failed: {e}")
            return None

    async def _paste_macos(self) -> Optional[ImageInfo]:
        """Paste image on macOS."""
        try:
            timestamp = asyncio.get_event_loop().time()
            filename = self.temp_dir / f"paste_{int(timestamp)}.png"

            # Try pngpaste first (brew install pngpaste)
            try:
                process = await asyncio.create_subprocess_exec(
                    "pngpaste", str(filename),
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE
                )
                await process.communicate()

                if filename.exists():
                    return await self._get_image_info(filename)

            except FileNotFoundError:
                pass

            # Fallback to osascript
            script = '''
                set theImage to the clipboard as «class PNGf»
                set theFile to POSIX file "{}"
                set theFileRef to open for access theFile with write permission
                write theImage to theFileRef
                close access theFileRef
            '''.format(filename)

            process = await asyncio.create_subprocess_exec(
                "osascript", "-e", script,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            await process.communicate()

            if filename.exists():
                return await self._get_image_info(filename)

            return None

        except Exception as e:
            print(f"macOS clipboard paste failed: {e}")
            return None

    async def _paste_linux(self) -> Optional[ImageInfo]:
        """Paste image on Linux."""
        try:
            timestamp = asyncio.get_event_loop().time()
            filename = self.temp_dir / f"paste_{int(timestamp)}.png"

            # Try xclip (X11)
            try:
                process = await asyncio.create_subprocess_exec(
                    "xclip", "-selection", "clipboard", "-t", "image/png", "-o",
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE
                )
                stdout, _ = await process.communicate()

                if stdout:
                    filename.write_bytes(stdout)
                    return await self._get_image_info(filename)

            except FileNotFoundError:
                pass

            # Try wl-paste (Wayland)
            try:
                process = await asyncio.create_subprocess_exec(
                    "wl-paste", "-t", "image/png",
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE
                )
                stdout, _ = await process.communicate()

                if stdout:
                    filename.write_bytes(stdout)
                    return await self._get_image_info(filename)

            except FileNotFoundError:
                pass

            return None

        except Exception as e:
            print(f"Linux clipboard paste failed: {e}")
            return None

    async def _paste_windows(self) -> Optional[ImageInfo]:
        """Paste image on Windows."""
        try:
            from PIL import ImageGrab

            img = ImageGrab.grabclipboard()

            if img is None:
                return None

            timestamp = asyncio.get_event_loop().time()
            filename = self.temp_dir / f"paste_{int(timestamp)}.png"

            img.save(filename)
            return await self._get_image_info(filename)

        except Exception as e:
            print(f"Windows clipboard paste failed: {e}")
            return None

    async def handle_drop(self, file_paths: List[str]) -> List[ImageInfo]:
        """
        Handle drag-and-drop of image files.

        Args:
            file_paths: List of dropped file paths

        Returns:
            List of ImageInfo objects for valid images
        """
        images = []

        for file_path in file_paths:
            try:
                path = Path(file_path)

                if not path.exists():
                    continue

                # Check if it's an image
                if not self._is_image_file(path):
                    continue

                # Check size
                if path.stat().st_size > self.max_size_bytes:
                    print(f"Image too large: {path.name}")
                    continue

                # Get image info
                info = await self._get_image_info(path)
                if info:
                    images.append(info)

                    # Report progress
                    if self.progress_callback:
                        await self.progress_callback(len(images), len(file_paths))

            except Exception as e:
                print(f"Failed to process {file_path}: {e}")

        return images

    def _is_image_file(self, path: Path) -> bool:
        """Check if file is a supported image."""
        image_extensions = {
            '.png', '.jpg', '.jpeg', '.gif', '.webp', '.bmp'
        }
        return path.suffix.lower() in image_extensions

    async def _get_image_info(self, path: Path) -> Optional[ImageInfo]:
        """Get information about an image."""
        try:
            from PIL import Image

            with Image.open(path) as img:
                # Get format
                format_str = img.format.lower() if img.format else 'png'
                try:
                    image_format = ImageFormat(format_str)
                except ValueError:
                    image_format = ImageFormat.PNG

                # Generate thumbnail
                thumbnail = await self._generate_thumbnail(img)

                return ImageInfo(
                    path=path,
                    format=image_format,
                    width=img.width,
                    height=img.height,
                    size_bytes=path.stat().st_size,
                    thumbnail=thumbnail
                )

        except Exception as e:
            print(f"Failed to get image info: {e}")
            return None

    async def _generate_thumbnail(self, image, max_size: int = 128) -> bytes:
        """Generate thumbnail for image."""
        try:
            from PIL import Image

            # Create thumbnail
            thumb = image.copy()
            thumb.thumbnail((max_size, max_size), Image.Resampling.LANCZOS)

            # Convert to bytes
            buffer = io.BytesIO()
            thumb.save(buffer, format='PNG')
            return buffer.getvalue()

        except Exception:
            return b''

    async def convert_format(self, image_path: Path,
                           target_format: ImageFormat) -> Optional[Path]:
        """
        Convert image to different format.

        Args:
            image_path: Path to source image
            target_format: Target format

        Returns:
            Path to converted image, or None on failure
        """
        try:
            from PIL import Image

            with Image.open(image_path) as img:
                # Generate output filename
                output_path = image_path.with_suffix(f'.{target_format.value}')

                # Convert
                if target_format == ImageFormat.JPEG or target_format == ImageFormat.JPG:
                    # Convert RGBA to RGB for JPEG
                    if img.mode == 'RGBA':
                        rgb_img = Image.new('RGB', img.size, (255, 255, 255))
                        rgb_img.paste(img, mask=img.split()[3])
                        rgb_img.save(output_path, 'JPEG')
                    else:
                        img.save(output_path, 'JPEG')
                else:
                    img.save(output_path, target_format.value.upper())

                return output_path

        except Exception as e:
            print(f"Format conversion failed: {e}")
            return None

    async def optimize_image(self, image_path: Path,
                           max_dimension: int = 2048,
                           quality: int = 85) -> Optional[Path]:
        """
        Optimize image for upload.

        Args:
            image_path: Path to image
            max_dimension: Maximum width/height
            quality: JPEG quality (1-100)

        Returns:
            Path to optimized image
        """
        try:
            from PIL import Image

            with Image.open(image_path) as img:
                # Resize if needed
                if img.width > max_dimension or img.height > max_dimension:
                    ratio = min(max_dimension / img.width, max_dimension / img.height)
                    new_size = (int(img.width * ratio), int(img.height * ratio))
                    img = img.resize(new_size, Image.Resampling.LANCZOS)

                # Save optimized
                output_path = image_path.with_stem(f"{image_path.stem}_optimized")
                img.save(output_path, optimize=True, quality=quality)

                return output_path

        except Exception as e:
            print(f"Image optimization failed: {e}")
            return None

    def get_image_base64(self, image_path: Path) -> Optional[str]:
        """
        Get base64-encoded image data.

        Args:
            image_path: Path to image

        Returns:
            Base64-encoded string
        """
        try:
            with open(image_path, 'rb') as f:
                image_data = f.read()
                return base64.b64encode(image_data).decode('utf-8')
        except Exception as e:
            print(f"Failed to encode image: {e}")
            return None

    def cleanup_old_images(self, max_age_seconds: int = 3600) -> None:
        """
        Clean up old temporary images.

        Args:
            max_age_seconds: Maximum age in seconds
        """
        import time

        if not self.temp_dir.exists():
            return

        current_time = time.time()

        for file in self.temp_dir.glob("paste_*.*"):
            try:
                file_age = current_time - file.stat().st_mtime
                if file_age > max_age_seconds:
                    file.unlink()
            except Exception:
                pass
