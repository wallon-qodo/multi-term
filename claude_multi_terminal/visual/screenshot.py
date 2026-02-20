"""Screenshot capture functionality with selection tool."""

import asyncio
import tempfile
from pathlib import Path
from enum import Enum
from typing import Optional, Tuple, Callable
from dataclasses import dataclass


class ScreenshotMode(Enum):
    """Screenshot capture modes."""
    FULLSCREEN = "fullscreen"
    SELECTION = "selection"
    WINDOW = "window"


@dataclass
class ScreenshotRegion:
    """Represents a screenshot region."""
    x: int
    y: int
    width: int
    height: int


class ScreenshotCapture:
    """
    Screenshot capture with multiple modes.

    Features:
    - Full screen capture
    - Selection tool (area capture)
    - Window-specific capture
    - Preview before sending
    - Auto-upload to conversation

    Usage:
        capture = ScreenshotCapture()
        await capture.capture_fullscreen()
        await capture.capture_selection()
    """

    def __init__(self):
        """Initialize screenshot capture."""
        self.temp_dir = Path(tempfile.gettempdir()) / "claude_screenshots"
        self.temp_dir.mkdir(parents=True, exist_ok=True)
        self.last_screenshot: Optional[Path] = None
        self.preview_callback: Optional[Callable] = None

    def set_preview_callback(self, callback: Callable) -> None:
        """Set callback for screenshot preview."""
        self.preview_callback = callback

    async def capture_fullscreen(self) -> Optional[Path]:
        """
        Capture full screen screenshot.

        Returns:
            Path to screenshot file, or None if capture failed
        """
        try:
            import platform

            # Generate unique filename
            timestamp = asyncio.get_event_loop().time()
            filename = self.temp_dir / f"screenshot_{int(timestamp)}.png"

            system = platform.system()

            if system == "Darwin":  # macOS
                # Use screencapture command
                process = await asyncio.create_subprocess_exec(
                    "screencapture", "-x", str(filename),
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE
                )
                await process.communicate()

            elif system == "Linux":
                # Try multiple screenshot tools
                tools = [
                    ["import", "-window", "root", str(filename)],  # ImageMagick
                    ["gnome-screenshot", "-f", str(filename)],      # GNOME
                    ["scrot", str(filename)],                        # scrot
                ]

                for tool in tools:
                    try:
                        process = await asyncio.create_subprocess_exec(
                            *tool,
                            stdout=asyncio.subprocess.PIPE,
                            stderr=asyncio.subprocess.PIPE
                        )
                        returncode = (await process.communicate())[0]
                        if returncode == 0 and filename.exists():
                            break
                    except FileNotFoundError:
                        continue

            elif system == "Windows":
                # Use PIL/Pillow for Windows
                from PIL import ImageGrab
                img = ImageGrab.grab()
                img.save(filename)

            else:
                return None

            if filename.exists():
                self.last_screenshot = filename

                # Show preview if callback set
                if self.preview_callback:
                    await self.preview_callback(filename)

                return filename

            return None

        except Exception as e:
            print(f"Screenshot capture failed: {e}")
            return None

    async def capture_selection(self) -> Optional[Path]:
        """
        Capture screenshot with selection tool.

        Returns:
            Path to screenshot file, or None if capture failed
        """
        try:
            import platform

            timestamp = asyncio.get_event_loop().time()
            filename = self.temp_dir / f"screenshot_{int(timestamp)}.png"

            system = platform.system()

            if system == "Darwin":  # macOS
                # Interactive selection with screencapture
                process = await asyncio.create_subprocess_exec(
                    "screencapture", "-i", "-x", str(filename),
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE
                )
                await process.communicate()

            elif system == "Linux":
                # Try selection tools
                tools = [
                    ["import", str(filename)],                       # ImageMagick (interactive)
                    ["gnome-screenshot", "-a", "-f", str(filename)], # GNOME area
                    ["scrot", "-s", str(filename)],                  # scrot select
                ]

                for tool in tools:
                    try:
                        process = await asyncio.create_subprocess_exec(
                            *tool,
                            stdout=asyncio.subprocess.PIPE,
                            stderr=asyncio.subprocess.PIPE
                        )
                        await process.communicate()
                        if filename.exists():
                            break
                    except FileNotFoundError:
                        continue

            elif system == "Windows":
                # Use snippingtool or fallback to PIL
                try:
                    process = await asyncio.create_subprocess_exec(
                        "snippingtool", "/clip",
                        stdout=asyncio.subprocess.PIPE,
                        stderr=asyncio.subprocess.PIPE
                    )
                    await process.communicate()

                    # Get from clipboard
                    from PIL import ImageGrab
                    img = ImageGrab.grabclipboard()
                    if img:
                        img.save(filename)
                except Exception:
                    # Fallback to full screen
                    return await self.capture_fullscreen()

            else:
                return None

            if filename.exists():
                self.last_screenshot = filename

                # Show preview if callback set
                if self.preview_callback:
                    await self.preview_callback(filename)

                return filename

            return None

        except Exception as e:
            print(f"Selection capture failed: {e}")
            return None

    async def capture_window(self) -> Optional[Path]:
        """
        Capture specific window.

        Returns:
            Path to screenshot file, or None if capture failed
        """
        try:
            import platform

            timestamp = asyncio.get_event_loop().time()
            filename = self.temp_dir / f"screenshot_{int(timestamp)}.png"

            system = platform.system()

            if system == "Darwin":  # macOS
                # Interactive window selection
                process = await asyncio.create_subprocess_exec(
                    "screencapture", "-w", "-x", str(filename),
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE
                )
                await process.communicate()

            elif system == "Linux":
                # Window selection
                tools = [
                    ["import", "-window", "root", str(filename)],
                    ["gnome-screenshot", "-w", "-f", str(filename)],
                ]

                for tool in tools:
                    try:
                        process = await asyncio.create_subprocess_exec(
                            *tool,
                            stdout=asyncio.subprocess.PIPE,
                            stderr=asyncio.subprocess.PIPE
                        )
                        await process.communicate()
                        if filename.exists():
                            break
                    except FileNotFoundError:
                        continue

            else:
                # Fallback to fullscreen
                return await self.capture_fullscreen()

            if filename.exists():
                self.last_screenshot = filename

                # Show preview if callback set
                if self.preview_callback:
                    await self.preview_callback(filename)

                return filename

            return None

        except Exception as e:
            print(f"Window capture failed: {e}")
            return None

    async def capture_region(self, region: ScreenshotRegion) -> Optional[Path]:
        """
        Capture specific region.

        Args:
            region: Region to capture

        Returns:
            Path to screenshot file, or None if capture failed
        """
        try:
            import platform

            timestamp = asyncio.get_event_loop().time()
            filename = self.temp_dir / f"screenshot_{int(timestamp)}.png"

            system = platform.system()

            if system == "Darwin":  # macOS
                # Region capture: -R x,y,w,h
                region_str = f"{region.x},{region.y},{region.width},{region.height}"
                process = await asyncio.create_subprocess_exec(
                    "screencapture", "-R", region_str, "-x", str(filename),
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE
                )
                await process.communicate()

            elif system == "Linux":
                # Use ImageMagick with geometry
                geometry = f"{region.width}x{region.height}+{region.x}+{region.y}"
                process = await asyncio.create_subprocess_exec(
                    "import", "-window", "root", "-crop", geometry, str(filename),
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE
                )
                await process.communicate()

            elif system == "Windows":
                from PIL import ImageGrab
                bbox = (region.x, region.y,
                       region.x + region.width, region.y + region.height)
                img = ImageGrab.grab(bbox)
                img.save(filename)

            else:
                return None

            if filename.exists():
                self.last_screenshot = filename
                return filename

            return None

        except Exception as e:
            print(f"Region capture failed: {e}")
            return None

    def cleanup_old_screenshots(self, max_age_seconds: int = 3600) -> None:
        """
        Clean up old screenshot files.

        Args:
            max_age_seconds: Maximum age in seconds (default: 1 hour)
        """
        import time

        if not self.temp_dir.exists():
            return

        current_time = time.time()

        for file in self.temp_dir.glob("screenshot_*.png"):
            try:
                file_age = current_time - file.stat().st_mtime
                if file_age > max_age_seconds:
                    file.unlink()
            except Exception:
                pass

    def get_last_screenshot(self) -> Optional[Path]:
        """Get path to last captured screenshot."""
        return self.last_screenshot
