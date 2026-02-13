"""
Integration module for code block detection and extraction in SelectableRichLog.

This provides a seamless way to add interactive code blocks to the terminal output
without major architectural changes.
"""

from rich.text import Text
from .code_block import CodeBlockParser
from typing import Callable, Optional
import re


class CodeBlockHighlighter:
    """
    Post-processor that adds visual indicators for code blocks in terminal output.

    Since we're using RichLog which doesn't support embedded widgets, we instead:
    1. Detect code blocks in output
    2. Add visual indicators (borders, metadata)
    3. Store code block data for copy/save operations
    4. Add clickable regions via context menu
    """

    def __init__(self):
        """Initialize the highlighter."""
        self.code_blocks = []  # Store extracted code blocks
        self.block_counter = 0

    def process_output(self, text: str) -> Text:
        """
        Process output text and enhance code blocks with visual indicators.

        Args:
            text: Plain text or ANSI text

        Returns:
            Rich Text with enhanced code blocks
        """
        # Extract code blocks
        blocks = CodeBlockParser.extract_code_blocks(text)

        if not blocks:
            # No code blocks, return as-is
            return Text.from_ansi(text)

        # Clear previous blocks
        self.code_blocks = []
        self.block_counter = 0

        # Build enhanced output
        result = Text()
        last_end = 0

        for language, code, start_pos, end_pos in blocks:
            # Add text before code block
            if start_pos > last_end:
                before_text = text[last_end:start_pos]
                result.append_text(Text.from_ansi(before_text))

            # Add enhanced code block
            enhanced_block = self._create_enhanced_block(language, code)
            result.append_text(enhanced_block)

            # Store block data
            self.code_blocks.append({
                'id': self.block_counter,
                'language': language,
                'code': code,
                'line_count': len(code.split('\n')),
                'char_count': len(code)
            })
            self.block_counter += 1

            last_end = end_pos

        # Add remaining text
        if last_end < len(text):
            after_text = text[last_end:]
            result.append_text(Text.from_ansi(after_text))

        return result

    def _create_enhanced_block(self, language: str, code: str) -> Text:
        """
        Create a beautifully formatted code block with visual indicators.

        Args:
            language: Programming language
            code: Source code

        Returns:
            Rich Text with formatted code block
        """
        block = Text()
        line_count = len(code.split('\n'))
        char_count = len(code)

        # Top border with metadata
        block.append("\n\n", style="")
        block.append("╭─", style="bold rgb(100,180,255)")
        block.append(" CODE BLOCK ", style="bold rgb(129,212,250)")
        block.append(f"#{self.block_counter} ", style="dim rgb(100,180,255)")
        block.append("─", style="rgb(100,180,255)")
        block.append("┤ ", style="rgb(100,180,255)")

        # Language badge
        if language and language != "text":
            block.append(f" {language.upper()} ", style="bold black on rgb(129,212,250)")
        else:
            block.append(" TEXT ", style="bold black on rgb(150,150,150)")

        block.append(" ├", style="rgb(100,180,255)")
        block.append("─" * 10, style="rgb(100,180,255)")
        block.append("╮\n", style="bold rgb(100,180,255)")

        # Metadata line
        block.append("│ ", style="rgb(100,180,255)")
        block.append(f"📊 {line_count} lines", style="dim cyan")
        block.append(" · ", style="dim white")
        block.append(f"{char_count} chars", style="dim cyan")

        # Pad to right edge (approximate)
        padding = max(0, 70 - len(f"📊 {line_count} lines · {char_count} chars") - 30)
        block.append(" " * padding, style="")

        # Action hints
        block.append("Right-click to copy/save ", style="dim rgb(150,150,150)")
        block.append("│\n", style="rgb(100,180,255)")

        # Separator
        block.append("├", style="rgb(100,180,255)")
        block.append("─" * 78, style="rgb(100,180,255)")
        block.append("┤\n", style="rgb(100,180,255)")

        # Code content with line numbers
        lines = code.split('\n')
        max_line_num_width = len(str(len(lines)))

        for i, line in enumerate(lines, 1):
            # Line number
            line_num = str(i).rjust(max_line_num_width)
            block.append("│ ", style="rgb(100,180,255)")
            block.append(f"{line_num} ", style="dim rgb(100,150,200)")
            block.append("│ ", style="dim white")

            # Code line (preserve any ANSI formatting)
            block.append(line, style="rgb(240,240,240)")
            block.append("\n", style="")

        # Bottom border
        block.append("╰", style="bold rgb(100,180,255)")
        block.append("─" * 78, style="rgb(100,180,255)")
        block.append("╯\n", style="bold rgb(100,180,255)")

        # Action hint
        block.append("  ", style="")
        block.append("💡 ", style="")
        block.append(f"Use right-click menu to copy/save code block #{self.block_counter}", style="dim rgb(150,150,150)")
        block.append("\n\n", style="")

        return block

    def get_block(self, block_id: int) -> Optional[dict]:
        """
        Get code block data by ID.

        Args:
            block_id: Block identifier

        Returns:
            Dictionary with block data or None
        """
        for block in self.code_blocks:
            if block['id'] == block_id:
                return block
        return None

    def get_all_blocks(self) -> list[dict]:
        """
        Get all code blocks.

        Returns:
            List of code block dictionaries
        """
        return self.code_blocks.copy()

    def has_code_blocks(self) -> bool:
        """
        Check if any code blocks have been detected.

        Returns:
            True if code blocks exist
        """
        return len(self.code_blocks) > 0


class CodeBlockContextMenu:
    """
    Context menu handler for code block operations.

    Adds "Copy Code Block" and "Save Code Block" options to the right-click menu
    when clicking within a code block region.
    """

    def __init__(self, highlighter: CodeBlockHighlighter, clipboard_manager):
        """
        Initialize context menu handler.

        Args:
            highlighter: CodeBlockHighlighter instance
            clipboard_manager: Clipboard manager for copy operations
        """
        self.highlighter = highlighter
        self.clipboard_manager = clipboard_manager

    def get_menu_items(self, line_idx: int, col_idx: int, lines: list) -> list:
        """
        Get additional menu items for code blocks at the given position.

        Args:
            line_idx: Line index in output
            col_idx: Column index in line
            lines: All output lines

        Returns:
            List of menu items to add to context menu
        """
        # Check if cursor is within a code block
        block_id = self._find_block_at_position(line_idx, lines)

        if block_id is None:
            return []

        # Get block data
        block = self.highlighter.get_block(block_id)
        if not block:
            return []

        # Return code block specific menu items
        from .selectable_richlog import MenuItem

        return [
            MenuItem(
                label="---",  # Separator
                callback=lambda: None
            ),
            MenuItem(
                label=f"📋 Copy Code Block #{block_id}",
                callback=lambda: self._copy_block(block),
                enabled=True,
                shortcut=""
            ),
            MenuItem(
                label=f"💾 Save Code Block #{block_id}",
                callback=lambda: self._save_block(block),
                enabled=True,
                shortcut=""
            ),
        ]

    def _find_block_at_position(self, line_idx: int, lines: list) -> Optional[int]:
        """
        Find code block ID at the given line position.

        Args:
            line_idx: Line index
            lines: All output lines

        Returns:
            Block ID or None
        """
        # Look for code block markers in nearby lines
        # Check current line and a few lines above
        for offset in range(0, min(50, line_idx + 1)):
            check_idx = line_idx - offset
            if check_idx < 0 or check_idx >= len(lines):
                continue

            line = lines[check_idx]
            line_text = "".join(seg.text for seg in line._segments) if hasattr(line, '_segments') else ""

            # Check for code block header with ID
            match = re.search(r'CODE BLOCK #(\d+)', line_text)
            if match:
                block_id = int(match.group(1))
                # Make sure we're still within this block (not past the bottom border)
                # Look ahead for bottom border
                for ahead in range(check_idx, min(len(lines), line_idx + 1)):
                    ahead_text = "".join(seg.text for seg in lines[ahead]._segments) if hasattr(lines[ahead], '_segments') else ""
                    if ahead == line_idx:
                        # Current position
                        return block_id
                    if "╰" in ahead_text and "─" * 10 in ahead_text:
                        # Found bottom border, check if current line is before it
                        if line_idx <= ahead:
                            return block_id
                        break

        return None

    def _copy_block(self, block: dict) -> None:
        """
        Copy code block to clipboard.

        Args:
            block: Block dictionary
        """
        success = self.clipboard_manager.copy_to_system(block['code'])

        # Notify user
        if hasattr(self.clipboard_manager, 'app'):
            app = self.clipboard_manager.app
        else:
            # Try to get app from somewhere
            app = None

        if app:
            if success:
                app.notify(
                    f"✓ Copied code block #{block['id']} ({block['line_count']} lines)",
                    severity="information",
                    timeout=2
                )
            else:
                app.notify(
                    "✓ Copied to internal buffer",
                    severity="warning",
                    timeout=2
                )

    def _save_block(self, block: dict) -> None:
        """
        Save code block to file (show dialog).

        Args:
            block: Block dictionary
        """
        # This would show the save dialog
        # For now, just notify
        if hasattr(self.clipboard_manager, 'app'):
            app = self.clipboard_manager.app
            if app:
                app.notify(
                    f"💾 Save dialog not yet implemented for block #{block['id']}",
                    severity="information",
                    timeout=2
                )
