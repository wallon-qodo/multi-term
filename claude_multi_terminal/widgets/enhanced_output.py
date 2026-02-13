"""Enhanced output widget with automatic code block detection and extraction."""

from textual.containers import VerticalScroll, Container
from textual.widgets import Static
from textual.app import ComposeResult
from rich.text import Text
from .code_block import CodeBlock, CodeBlockParser
from .selectable_richlog import SelectableRichLog
import re
from typing import Optional


class EnhancedOutputPane(VerticalScroll):
    """
    Enhanced output pane that automatically detects and replaces code blocks
    with interactive CodeBlock widgets.

    Features:
    - Automatic code block detection in markdown
    - Interactive copy/save buttons for code blocks
    - Syntax highlighting
    - Seamless integration with RichLog output
    - Beautiful Homebrew theme styling
    """

    DEFAULT_CSS = """
    EnhancedOutputPane {
        background: rgb(24,24,24);
        color: rgb(240,240,240);
        border: none;
        padding: 1 2;
        scrollbar-gutter: stable;
    }

    EnhancedOutputPane .text-content {
        width: 100%;
        height: auto;
        background: transparent;
        color: rgb(240,240,240);
        padding: 0;
    }
    """

    def __init__(self, **kwargs):
        """Initialize enhanced output pane."""
        super().__init__(**kwargs)
        self._content_widgets = []
        self._accumulated_text = ""
        self._last_widget_id = 0

    def clear_content(self) -> None:
        """Clear all content from the pane."""
        # Remove all child widgets
        for widget in list(self.query("*")):
            widget.remove()
        self._content_widgets.clear()
        self._accumulated_text = ""
        self._last_widget_id = 0

    async def write_output(self, text: str | Text) -> None:
        """
        Write output to the pane, automatically detecting and extracting code blocks.

        Args:
            text: Text or Rich Text to write
        """
        # Convert Rich Text to plain string for parsing
        if isinstance(text, Text):
            plain_text = text.plain
        else:
            plain_text = str(text)

        # Accumulate text to handle streaming output
        self._accumulated_text += plain_text

        # Check if we have complete code blocks (ending with ```)
        if "```" in self._accumulated_text:
            # Try to parse and render code blocks
            await self._render_accumulated_content()

    async def _render_accumulated_content(self) -> None:
        """
        Parse accumulated text and render it with code block widgets.
        """
        text = self._accumulated_text

        # Check if we have complete code blocks
        # Count backticks to see if we have complete blocks
        backtick_count = text.count("```")

        # We need pairs of ``` to have complete code blocks
        if backtick_count < 2:
            # Not enough code blocks yet, wait for more
            return

        # Check if the last code block is complete
        # Find the last occurrence of ```
        last_backtick_pos = text.rfind("```")
        # Check if there's a newline or end of string after it
        is_complete = (
            last_backtick_pos == len(text) - 3 or  # At the end
            (last_backtick_pos + 3 < len(text) and text[last_backtick_pos + 3] in ['\n', ' '])
        )

        if not is_complete and backtick_count % 2 != 0:
            # Incomplete code block, wait for more
            return

        # Clear existing widgets
        for widget in list(self.query("*")):
            widget.remove()
        self._content_widgets.clear()

        # Parse code blocks
        blocks = CodeBlockParser.extract_code_blocks(text)

        if not blocks:
            # No code blocks found, render as plain text
            await self._render_plain_text(text)
            return

        # Split text into segments: text, code, text, code, etc.
        segments = []
        last_end = 0

        for language, code, start_pos, end_pos in blocks:
            # Add text before code block
            if start_pos > last_end:
                before_text = text[last_end:start_pos]
                if before_text.strip():
                    segments.append(("text", before_text))

            # Add code block
            segments.append(("code", language, code))
            last_end = end_pos

        # Add remaining text after last code block
        if last_end < len(text):
            after_text = text[last_end:]
            if after_text.strip():
                segments.append(("text", after_text))

        # Render segments
        for segment in segments:
            if segment[0] == "text":
                # Render as plain text
                text_widget = Static(
                    Text.from_ansi(segment[1]),
                    classes="text-content"
                )
                await self.mount(text_widget)
                self._content_widgets.append(text_widget)

            elif segment[0] == "code":
                # Render as interactive code block
                language = segment[1]
                code = segment[2]
                code_widget = CodeBlock(code=code, language=language)
                await self.mount(code_widget)
                self._content_widgets.append(code_widget)

        # Scroll to bottom
        self.scroll_end(animate=False)

    async def _render_plain_text(self, text: str) -> None:
        """
        Render plain text without code blocks.

        Args:
            text: Plain text to render
        """
        # Convert ANSI codes to Rich Text
        rich_text = Text.from_ansi(text)
        text_widget = Static(rich_text, classes="text-content")
        await self.mount(text_widget)
        self._content_widgets.append(text_widget)

        # Scroll to bottom
        self.scroll_end(animate=False)

    def get_plain_text(self) -> str:
        """
        Get all text content as plain string.

        Returns:
            Plain text content
        """
        return self._accumulated_text


class CodeBlockIndicator(Container):
    """
    Inline indicator that shows when a code block is being streamed.

    Features:
    - Appears while code block is being received
    - Shows language and line count
    - Animated pulse effect
    - Disappears when code block is complete
    """

    DEFAULT_CSS = """
    CodeBlockIndicator {
        width: 100%;
        height: 3;
        background: rgb(32,32,32);
        border: solid rgb(100,180,255);
        padding: 1 2;
        margin: 1 0;
    }

    CodeBlockIndicator .indicator-text {
        width: 100%;
        height: 1;
        background: transparent;
        color: rgb(129,212,250);
        content-align: left middle;
    }
    """

    def __init__(self, language: str = "text", **kwargs):
        """
        Initialize code block indicator.

        Args:
            language: Programming language being streamed
        """
        super().__init__(**kwargs)
        self.language = language

    def compose(self) -> ComposeResult:
        """Compose the indicator layout."""
        indicator_text = Text()
        indicator_text.append("⚡ ", style="bold rgb(100,180,255)")
        indicator_text.append(f"Receiving code block", style="rgb(129,212,250)")
        if self.language and self.language != "text":
            indicator_text.append(f" ({self.language})", style="dim rgb(129,212,250)")
        indicator_text.append("...", style="dim rgb(129,212,250)")
        yield Static(indicator_text, classes="indicator-text")
