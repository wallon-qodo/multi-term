"""Interactive code block widget with copy/save functionality."""

from textual.widgets import Static, Button
from textual.containers import Container, Horizontal, Vertical
from textual.reactive import reactive
from textual.app import ComposeResult
from textual import events
from rich.syntax import Syntax
from rich.text import Text
import re
from typing import Optional, Callable


class CodeBlockActions(Container):
    """
    Action buttons overlay for code blocks.

    Features:
    - Hover-triggered appearance
    - Copy and Save buttons
    - Beautiful Homebrew-themed styling
    - Smooth fade-in animation
    """

    DEFAULT_CSS = """
    CodeBlockActions {
        layer: overlay;
        height: 3;
        width: 100%;
        dock: top;
        background: rgba(40,40,40,0.95);
        border-bottom: solid rgb(255,77,77);
        padding: 0 2;
        offset: 0 0;
        display: none;
    }

    CodeBlockActions.visible {
        display: block;
    }

    CodeBlockActions .action-header {
        height: 1;
        width: 1fr;
        background: transparent;
        color: rgb(255,100,100);
        padding: 0;
        content-align: left middle;
    }

    CodeBlockActions .action-buttons {
        height: 1;
        width: auto;
        background: transparent;
        padding: 0;
        layout: horizontal;
    }

    CodeBlockActions Button {
        height: 1;
        min-width: 10;
        background: rgb(42,42,42);
        color: rgb(240,240,240);
        border: solid rgb(100,100,100);
        margin-right: 1;
        padding: 0 1;
    }

    CodeBlockActions Button:hover {
        background: rgb(255,77,77);
        color: rgb(24,24,24);
        border: solid rgb(255,100,100);
    }

    CodeBlockActions Button:focus {
        background: rgb(255,77,77);
        color: rgb(24,24,24);
        border: solid rgb(255,100,100);
    }

    CodeBlockActions .copy-btn {
        color: rgb(129,212,250);
    }

    CodeBlockActions .save-btn {
        color: rgb(165,214,167);
    }
    """

    def __init__(
        self,
        language: str,
        on_copy: Callable,
        on_save: Callable,
        **kwargs
    ):
        """
        Initialize code block actions.

        Args:
            language: Programming language for syntax highlighting
            on_copy: Callback when copy button is clicked
            on_save: Callback when save button is clicked
        """
        super().__init__(**kwargs)
        self.language = language
        self.on_copy_callback = on_copy
        self.on_save_callback = on_save

    def compose(self) -> ComposeResult:
        """Compose the action bar layout."""
        with Vertical():
            # Header with language info
            header_text = Text()
            header_text.append("╭─ ", style="rgb(255,77,77)")
            header_text.append(f"Code: {self.language or 'text'}", style="bold rgb(255,100,100)")
            header_text.append(" ─╮", style="rgb(255,77,77)")
            yield Static(header_text, classes="action-header")

            # Action buttons
            with Horizontal(classes="action-buttons"):
                yield Button("📋 Copy", id="copy-btn", classes="copy-btn")
                yield Button("💾 Save", id="save-btn", classes="save-btn")

    async def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses."""
        if event.button.id == "copy-btn":
            await self.on_copy_callback()
        elif event.button.id == "save-btn":
            await self.on_save_callback()
        event.stop()


class CodeBlock(Container):
    """
    Interactive code block widget with syntax highlighting and actions.

    Features:
    - Syntax highlighting for multiple languages
    - Hover-activated copy/save buttons
    - Beautiful Homebrew theme styling
    - Line numbers
    - Language badge
    """

    DEFAULT_CSS = """
    CodeBlock {
        width: 100%;
        height: auto;
        background: rgb(26,26,26);
        border: solid rgb(60,60,60);
        padding: 0;
        margin: 1 0;
    }

    CodeBlock:hover {
        border: solid rgb(255,77,77);
        background: rgb(32,32,32);
    }

    CodeBlock .code-content {
        width: 100%;
        height: auto;
        background: rgb(26,26,26);
        padding: 1 2;
        scrollbar-gutter: stable;
        overflow-y: auto;
        max-height: 40;
    }

    CodeBlock:hover .code-content {
        background: rgb(32,32,32);
    }

    CodeBlock .code-footer {
        height: 1;
        width: 100%;
        background: rgb(24,24,24);
        border-top: solid rgb(42,42,42);
        color: rgb(150,150,150);
        padding: 0 2;
        content-align: left middle;
    }

    CodeBlock:hover .code-footer {
        background: rgb(26,26,26);
        border-top: solid rgb(255,77,77);
        color: rgb(200,200,200);
    }
    """

    # Reactive properties
    is_hovering = reactive(False)

    def __init__(
        self,
        code: str,
        language: str = "",
        **kwargs
    ):
        """
        Initialize code block.

        Args:
            code: Source code content
            language: Programming language for syntax highlighting
        """
        super().__init__(**kwargs)
        self.code = code
        self.language = language or "text"
        self.line_count = len(code.split('\n'))
        self.char_count = len(code)

    def compose(self) -> ComposeResult:
        """Compose the code block layout."""
        # Action bar (initially hidden, shown on hover)
        yield CodeBlockActions(
            language=self.language,
            on_copy=self._handle_copy,
            on_save=self._handle_save,
            id=f"actions-{id(self)}"
        )

        # Code content with syntax highlighting
        try:
            # Use Rich Syntax for beautiful highlighting
            syntax = Syntax(
                self.code,
                self.language,
                theme="monokai",
                line_numbers=True,
                word_wrap=False,
                indent_guides=True,
                background_color="rgb(26,26,26)"
            )
            yield Static(syntax, classes="code-content", id=f"content-{id(self)}")
        except Exception:
            # Fallback to plain text if syntax highlighting fails
            yield Static(self.code, classes="code-content", id=f"content-{id(self)}")

        # Footer with metadata
        footer_text = Text()
        footer_text.append("┊ ", style="dim white")
        footer_text.append(f"{self.line_count} lines", style="dim cyan")
        footer_text.append(" · ", style="dim white")
        footer_text.append(f"{self.char_count} chars", style="dim cyan")
        footer_text.append(" · ", style="dim white")
        footer_text.append(f"Language: {self.language}", style="dim white")
        yield Static(footer_text, classes="code-footer")

    def on_enter(self, event: events.Enter) -> None:
        """Show action buttons on mouse enter."""
        self.is_hovering = True
        self._show_actions()
        event.stop()

    def on_leave(self, event: events.Leave) -> None:
        """Hide action buttons on mouse leave."""
        self.is_hovering = False
        self._hide_actions()
        event.stop()

    def _show_actions(self) -> None:
        """Show the action buttons overlay."""
        try:
            actions = self.query_one(f"#actions-{id(self)}", CodeBlockActions)
            actions.add_class("visible")
        except Exception:
            pass

    def _hide_actions(self) -> None:
        """Hide the action buttons overlay."""
        try:
            actions = self.query_one(f"#actions-{id(self)}", CodeBlockActions)
            actions.remove_class("visible")
        except Exception:
            pass

    async def _handle_copy(self) -> None:
        """Handle copy button click."""
        # Get clipboard manager from app
        if hasattr(self.app, 'clip_manager'):
            success = self.app.clip_manager.copy_to_system(self.code)

            if success:
                self.app.notify(
                    f"✓ Copied {self.line_count} lines to clipboard",
                    severity="information",
                    timeout=2
                )
            else:
                # Fallback to internal buffer
                self.app.clip_manager_buffer = self.code
                self.app.notify(
                    "✓ Copied to internal buffer",
                    severity="warning",
                    timeout=2
                )

    async def _handle_save(self) -> None:
        """Handle save button click - prompts for filename."""
        from .save_file_dialog import SaveFileDialog

        # Suggest filename based on language
        suggested_name = self._suggest_filename()

        # Show save dialog
        filename = await self.app.push_screen_wait(
            SaveFileDialog(
                suggested_name=suggested_name,
                code_content=self.code
            )
        )

        if filename:
            self.app.notify(
                f"✓ Saved to: {filename}",
                severity="information",
                timeout=3
            )

    def _suggest_filename(self) -> str:
        """
        Suggest a filename based on the language.

        Returns:
            Suggested filename with extension
        """
        # Map common languages to file extensions
        extension_map = {
            "python": ".py",
            "javascript": ".js",
            "typescript": ".ts",
            "java": ".java",
            "cpp": ".cpp",
            "c": ".c",
            "rust": ".rs",
            "go": ".go",
            "ruby": ".rb",
            "php": ".php",
            "swift": ".swift",
            "kotlin": ".kt",
            "scala": ".scala",
            "bash": ".sh",
            "shell": ".sh",
            "sql": ".sql",
            "html": ".html",
            "css": ".css",
            "json": ".json",
            "yaml": ".yaml",
            "markdown": ".md",
            "text": ".txt",
        }

        ext = extension_map.get(self.language.lower(), ".txt")
        return f"code_snippet{ext}"


class CodeBlockParser:
    """
    Parser for detecting and extracting code blocks from markdown text.

    Features:
    - Detects fenced code blocks (```language...```)
    - Extracts language and code content
    - Handles multiple code blocks in text
    """

    # Regex for fenced code blocks
    CODE_BLOCK_PATTERN = re.compile(
        r'```([a-zA-Z0-9_+-]*)\n(.*?)```',
        re.DOTALL | re.MULTILINE
    )

    @classmethod
    def extract_code_blocks(cls, text: str) -> list[tuple[str, str, int, int]]:
        """
        Extract all code blocks from text.

        Args:
            text: Markdown text containing code blocks

        Returns:
            List of tuples: (language, code, start_pos, end_pos)
        """
        blocks = []
        for match in cls.CODE_BLOCK_PATTERN.finditer(text):
            language = match.group(1) or "text"
            code = match.group(2).rstrip('\n')
            start_pos = match.start()
            end_pos = match.end()
            blocks.append((language, code, start_pos, end_pos))
        return blocks

    @classmethod
    def has_code_blocks(cls, text: str) -> bool:
        """
        Check if text contains any code blocks.

        Args:
            text: Text to check

        Returns:
            True if code blocks found
        """
        return bool(cls.CODE_BLOCK_PATTERN.search(text))

    @classmethod
    def replace_code_blocks_with_widgets(cls, text: str) -> tuple[str, list[tuple[int, str, str]]]:
        """
        Replace code blocks in text with placeholder markers.

        Args:
            text: Original text with code blocks

        Returns:
            Tuple of (modified_text, list of (position, language, code))
        """
        blocks = cls.extract_code_blocks(text)

        if not blocks:
            return text, []

        # Replace each code block with a unique marker
        modified_text = text
        offset = 0
        widget_data = []

        for i, (language, code, start_pos, end_pos) in enumerate(blocks):
            # Create a marker that will be replaced with widget
            marker = f"\n\n[CODE_BLOCK_{i}]\n\n"

            # Calculate adjusted positions accounting for previous replacements
            adjusted_start = start_pos - offset
            adjusted_end = end_pos - offset

            # Replace the code block
            modified_text = (
                modified_text[:adjusted_start] +
                marker +
                modified_text[adjusted_end:]
            )

            # Update offset for next replacement
            offset += (end_pos - start_pos) - len(marker)

            # Store widget data
            widget_data.append((i, language, code))

        return modified_text, widget_data
