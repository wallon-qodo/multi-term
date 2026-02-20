"""Vision API support for image uploads and screenshots."""

import base64
import mimetypes
import os
from pathlib import Path
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass


@dataclass
class ImageContent:
    """Represents an image for Vision API."""

    source_type: str  # "base64" or "url"
    media_type: str   # "image/jpeg", "image/png", etc.
    data: str         # base64 data or URL

    def to_dict(self) -> Dict[str, Any]:
        """Convert to Anthropic API format."""
        if self.source_type == "base64":
            return {
                "type": "image",
                "source": {
                    "type": "base64",
                    "media_type": self.media_type,
                    "data": self.data,
                }
            }
        elif self.source_type == "url":
            return {
                "type": "image",
                "source": {
                    "type": "url",
                    "url": self.data,
                }
            }
        else:
            raise ValueError(f"Unknown source type: {self.source_type}")


class VisionHandler:
    """
    Handles image uploads and vision-enabled conversations.

    Supports:
    - Local file uploads (PNG, JPEG, WebP, GIF)
    - Screenshot integration
    - Base64 encoding
    - Image preview in UI
    - Multi-image messages
    """

    # Supported image formats
    SUPPORTED_FORMATS = {
        ".png": "image/png",
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".webp": "image/webp",
        ".gif": "image/gif",
    }

    # Max image size (5MB recommended by Anthropic)
    MAX_IMAGE_SIZE_MB = 5
    MAX_IMAGE_SIZE_BYTES = MAX_IMAGE_SIZE_MB * 1024 * 1024

    def __init__(self, max_image_size_mb: int = 5):
        """
        Initialize vision handler.

        Args:
            max_image_size_mb: Maximum image size in MB
        """
        self.max_image_size_mb = max_image_size_mb
        self.max_image_size_bytes = max_image_size_mb * 1024 * 1024

    def load_image(self, file_path: Union[str, Path]) -> ImageContent:
        """
        Load an image file for Vision API.

        Args:
            file_path: Path to image file

        Returns:
            ImageContent object

        Raises:
            FileNotFoundError: If file doesn't exist
            ValueError: If file format not supported or file too large
        """
        path = Path(file_path)

        # Check file exists
        if not path.exists():
            raise FileNotFoundError(f"Image file not found: {file_path}")

        # Check file extension
        ext = path.suffix.lower()
        if ext not in self.SUPPORTED_FORMATS:
            raise ValueError(
                f"Unsupported image format: {ext}. "
                f"Supported formats: {', '.join(self.SUPPORTED_FORMATS.keys())}"
            )

        # Check file size
        file_size = path.stat().st_size
        if file_size > self.max_image_size_bytes:
            raise ValueError(
                f"Image too large: {file_size / 1024 / 1024:.1f}MB. "
                f"Maximum size: {self.max_image_size_mb}MB"
            )

        # Read and encode image
        media_type = self.SUPPORTED_FORMATS[ext]
        with open(path, 'rb') as f:
            image_data = f.read()

        base64_data = base64.b64encode(image_data).decode('utf-8')

        return ImageContent(
            source_type="base64",
            media_type=media_type,
            data=base64_data,
        )

    def load_image_from_bytes(
        self,
        image_bytes: bytes,
        media_type: str = "image/png",
    ) -> ImageContent:
        """
        Load an image from bytes (e.g., screenshot).

        Args:
            image_bytes: Image data as bytes
            media_type: MIME type (default: image/png)

        Returns:
            ImageContent object
        """
        # Check size
        if len(image_bytes) > self.max_image_size_bytes:
            raise ValueError(
                f"Image too large: {len(image_bytes) / 1024 / 1024:.1f}MB. "
                f"Maximum size: {self.max_image_size_mb}MB"
            )

        base64_data = base64.b64encode(image_bytes).decode('utf-8')

        return ImageContent(
            source_type="base64",
            media_type=media_type,
            data=base64_data,
        )

    def load_image_from_url(self, url: str) -> ImageContent:
        """
        Load an image from URL.

        Args:
            url: Image URL

        Returns:
            ImageContent object

        Note: URL images are not validated until API call
        """
        # Guess media type from URL
        media_type = mimetypes.guess_type(url)[0] or "image/jpeg"

        return ImageContent(
            source_type="url",
            media_type=media_type,
            data=url,
        )

    def build_vision_message(
        self,
        text: str,
        images: List[ImageContent],
    ) -> Dict[str, Any]:
        """
        Build a message with text and images.

        Args:
            text: Text content
            images: List of ImageContent objects

        Returns:
            Message dict in Anthropic API format
        """
        content = []

        # Add images first
        for image in images:
            content.append(image.to_dict())

        # Add text
        content.append({
            "type": "text",
            "text": text,
        })

        return {
            "role": "user",
            "content": content,
        }

    def build_multimodal_content(
        self,
        text: Optional[str] = None,
        images: Optional[List[ImageContent]] = None,
    ) -> List[Dict[str, Any]]:
        """
        Build multimodal content for API.

        Args:
            text: Optional text content
            images: Optional list of images

        Returns:
            List of content blocks
        """
        content = []

        # Add images
        if images:
            for image in images:
                content.append(image.to_dict())

        # Add text
        if text:
            content.append({
                "type": "text",
                "text": text,
            })

        return content

    def is_supported_format(self, file_path: Union[str, Path]) -> bool:
        """
        Check if image format is supported.

        Args:
            file_path: Path to check

        Returns:
            True if supported, False otherwise
        """
        ext = Path(file_path).suffix.lower()
        return ext in self.SUPPORTED_FORMATS

    def get_image_info(self, file_path: Union[str, Path]) -> Dict[str, Any]:
        """
        Get information about an image file.

        Args:
            file_path: Path to image

        Returns:
            Dictionary with image info
        """
        path = Path(file_path)

        if not path.exists():
            return {"error": "File not found"}

        ext = path.suffix.lower()
        file_size = path.stat().st_size

        return {
            "path": str(path),
            "name": path.name,
            "extension": ext,
            "format": self.SUPPORTED_FORMATS.get(ext, "unknown"),
            "size_bytes": file_size,
            "size_mb": file_size / 1024 / 1024,
            "supported": ext in self.SUPPORTED_FORMATS,
            "within_size_limit": file_size <= self.max_image_size_bytes,
        }

    def validate_image(self, file_path: Union[str, Path]) -> tuple[bool, Optional[str]]:
        """
        Validate an image file.

        Args:
            file_path: Path to image

        Returns:
            Tuple of (is_valid, error_message)
        """
        path = Path(file_path)

        # Check exists
        if not path.exists():
            return False, "File not found"

        # Check format
        ext = path.suffix.lower()
        if ext not in self.SUPPORTED_FORMATS:
            return False, f"Unsupported format: {ext}"

        # Check size
        file_size = path.stat().st_size
        if file_size > self.max_image_size_bytes:
            return False, (
                f"File too large: {file_size / 1024 / 1024:.1f}MB "
                f"(max: {self.max_image_size_mb}MB)"
            )

        return True, None


def format_image_preview(image_info: Dict[str, Any]) -> str:
    """
    Format image information for display.

    Args:
        image_info: Image info from get_image_info()

    Returns:
        Formatted string
    """
    if "error" in image_info:
        return f"❌ {image_info['error']}"

    status = "✅" if image_info["supported"] and image_info["within_size_limit"] else "⚠️"

    return (
        f"{status} {image_info['name']}\n"
        f"  Format: {image_info['format']}\n"
        f"  Size: {image_info['size_mb']:.2f}MB"
    )


def create_screenshot_message(
    screenshot_bytes: bytes,
    prompt: str,
) -> Dict[str, Any]:
    """
    Create a message with a screenshot.

    Args:
        screenshot_bytes: Screenshot image data
        prompt: Text prompt

    Returns:
        Message dict for API
    """
    handler = VisionHandler()
    image = handler.load_image_from_bytes(screenshot_bytes, media_type="image/png")

    return handler.build_vision_message(prompt, [image])


def create_multi_image_message(
    file_paths: List[Union[str, Path]],
    prompt: str,
) -> Dict[str, Any]:
    """
    Create a message with multiple images.

    Args:
        file_paths: List of image file paths
        prompt: Text prompt

    Returns:
        Message dict for API
    """
    handler = VisionHandler()
    images = [handler.load_image(path) for path in file_paths]

    return handler.build_vision_message(prompt, images)
