"""Platform-specific clipboard operations."""

import subprocess
import os


class ClipboardManager:
    """
    Platform-specific clipboard operations.

    macOS: Uses pbcopy/pbpaste
    Linux: Uses xclip or xsel
    """

    def __init__(self):
        """Initialize clipboard manager."""
        self.platform = os.uname().sysname.lower()

    def copy_to_system(self, text: str) -> bool:
        """
        Copy text to system clipboard.

        Args:
            text: Text to copy

        Returns:
            True if successful, False otherwise
        """
        try:
            if self.platform == "darwin":
                # macOS
                process = subprocess.Popen(
                    ['pbcopy'],
                    stdin=subprocess.PIPE
                )
                process.communicate(text.encode('utf-8'))
                return process.returncode == 0
            elif self.platform == "linux":
                # Try xclip first, fall back to xsel
                try:
                    process = subprocess.Popen(
                        ['xclip', '-selection', 'clipboard'],
                        stdin=subprocess.PIPE
                    )
                    process.communicate(text.encode('utf-8'))
                    return process.returncode == 0
                except FileNotFoundError:
                    process = subprocess.Popen(
                        ['xsel', '--clipboard', '--input'],
                        stdin=subprocess.PIPE
                    )
                    process.communicate(text.encode('utf-8'))
                    return process.returncode == 0
            else:
                return False
        except Exception:
            return False

    def paste_from_system(self) -> str:
        """
        Get text from system clipboard.

        Returns:
            Clipboard text or empty string on failure
        """
        try:
            if self.platform == "darwin":
                result = subprocess.run(
                    ['pbpaste'],
                    capture_output=True,
                    text=True
                )
                return result.stdout if result.returncode == 0 else ""
            elif self.platform == "linux":
                try:
                    result = subprocess.run(
                        ['xclip', '-selection', 'clipboard', '-o'],
                        capture_output=True,
                        text=True
                    )
                    return result.stdout if result.returncode == 0 else ""
                except FileNotFoundError:
                    result = subprocess.run(
                        ['xsel', '--clipboard', '--output'],
                        capture_output=True,
                        text=True
                    )
                    return result.stdout if result.returncode == 0 else ""
            else:
                return ""
        except Exception:
            return ""

    def get_from_system(self) -> str:
        """
        Get text from system clipboard (alias for paste_from_system).

        Returns:
            Clipboard text or empty string on failure
        """
        return self.paste_from_system()
