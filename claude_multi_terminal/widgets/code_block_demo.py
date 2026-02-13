"""
Demonstration of code block extraction integration.

This module shows how to integrate code block detection into the session pane.
"""

from rich.text import Text
from .code_block import CodeBlockParser
import re


class CodeBlockDetector:
    """
    Helper class to detect and track code blocks in streaming output.

    Features:
    - Detects when code blocks start/end
    - Buffers incomplete code blocks
    - Emits complete code blocks for widget creation
    """

    def __init__(self):
        """Initialize the detector."""
        self.buffer = ""
        self.in_code_block = False
        self.code_block_lang = None
        self.code_block_content = []
        self.complete_blocks = []

    def process_chunk(self, text: str) -> tuple[str, list[tuple[str, str]]]:
        """
        Process a chunk of text and extract complete code blocks.

        Args:
            text: Chunk of text to process

        Returns:
            Tuple of (text_to_display, list of (language, code) for complete blocks)
        """
        self.buffer += text
        complete_blocks = []

        # Check for code block markers
        lines = self.buffer.split('\n')
        output_lines = []
        i = 0

        while i < len(lines):
            line = lines[i]

            # Check for code block start
            if line.strip().startswith('```'):
                if not self.in_code_block:
                    # Starting a new code block
                    self.in_code_block = True
                    # Extract language
                    lang_match = re.match(r'```(\w+)', line.strip())
                    self.code_block_lang = lang_match.group(1) if lang_match else "text"
                    self.code_block_content = []
                    # Don't add this line to output
                else:
                    # Ending code block
                    self.in_code_block = False
                    # Emit complete code block
                    code = '\n'.join(self.code_block_content)
                    complete_blocks.append((self.code_block_lang or "text", code))
                    # Reset
                    self.code_block_lang = None
                    self.code_block_content = []
                    # Don't add this line to output
            elif self.in_code_block:
                # Inside code block - accumulate
                self.code_block_content.append(line)
            else:
                # Regular text
                output_lines.append(line)

            i += 1

        # Update buffer with remaining incomplete content
        if self.in_code_block:
            # Still in a code block, keep the buffer
            self.buffer = '```' + (self.code_block_lang or '') + '\n' + '\n'.join(self.code_block_content)
        else:
            # No active code block, clear buffer
            self.buffer = ""

        text_to_display = '\n'.join(output_lines)
        return text_to_display, complete_blocks


def extract_code_blocks_from_text(text: str) -> dict:
    """
    Extract all code blocks from text and return structured data.

    Args:
        text: Text containing code blocks

    Returns:
        Dictionary with:
        - 'has_code_blocks': bool
        - 'blocks': list of {'language': str, 'code': str, 'start': int, 'end': int}
        - 'text_only': str (text with code blocks removed)
    """
    blocks = CodeBlockParser.extract_code_blocks(text)

    result = {
        'has_code_blocks': len(blocks) > 0,
        'blocks': [],
        'text_only': text
    }

    if not blocks:
        return result

    # Build structured block data
    for language, code, start_pos, end_pos in blocks:
        result['blocks'].append({
            'language': language,
            'code': code,
            'start': start_pos,
            'end': end_pos,
            'line_count': len(code.split('\n')),
            'char_count': len(code)
        })

    # Remove code blocks from text
    text_only = text
    for _, _, start_pos, end_pos in reversed(blocks):  # Reverse to maintain positions
        text_only = text_only[:start_pos] + text_only[end_pos:]

    result['text_only'] = text_only

    return result


def create_code_block_summary(language: str, code: str) -> Text:
    """
    Create a beautiful summary text for a code block.

    Args:
        language: Programming language
        code: Code content

    Returns:
        Rich Text summary
    """
    line_count = len(code.split('\n'))
    char_count = len(code)

    summary = Text()
    summary.append("\n┌─", style="rgb(100,180,255)")
    summary.append(" Code Block ", style="bold rgb(129,212,250)")
    summary.append("─┐\n", style="rgb(100,180,255)")

    summary.append("│ ", style="rgb(100,180,255)")
    summary.append("Language: ", style="dim white")
    summary.append(language or "text", style="bold cyan")
    summary.append("\n", style="")

    summary.append("│ ", style="rgb(100,180,255)")
    summary.append(f"Lines: {line_count}", style="dim white")
    summary.append(" · ", style="dim white")
    summary.append(f"Chars: {char_count}", style="dim white")
    summary.append("\n", style="")

    summary.append("└─", style="rgb(100,180,255)")
    summary.append(" Hover to copy/save ", style="dim rgb(129,212,250)")
    summary.append("─┘\n\n", style="rgb(100,180,255)")

    return summary


# Example usage in session_pane.py:
"""
# In SessionPane._update_output():

# Process the output to extract code blocks
from .code_block_demo import extract_code_blocks_from_text, create_code_block_summary

result = extract_code_blocks_from_text(filtered_output)

if result['has_code_blocks']:
    # Write text without code blocks
    if result['text_only'].strip():
        rich_text = Text.from_ansi(result['text_only'])
        output_widget.write(rich_text)

    # Add code block summaries (widgets would be better, but this shows the concept)
    for block in result['blocks']:
        summary = create_code_block_summary(block['language'], block['code'])
        output_widget.write(summary)

        # In a full implementation, you would mount a CodeBlock widget here
        # code_widget = CodeBlock(code=block['code'], language=block['language'])
        # await self.mount(code_widget)
else:
    # No code blocks, write normally
    rich_text = Text.from_ansi(filtered_output)
    output_widget.write(rich_text)
"""
