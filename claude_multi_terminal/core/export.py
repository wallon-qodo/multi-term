"""Session transcript export functionality."""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional, Any
from dataclasses import dataclass, asdict
import re


@dataclass
class ConversationMessage:
    """Represents a single message in the conversation."""
    timestamp: str
    type: str  # 'command' or 'response'
    content: str
    metadata: Optional[Dict[str, Any]] = None


class TranscriptExporter:
    """
    Handles exporting session transcripts to various formats.

    Supports:
    - Markdown format (human-readable with timestamps)
    - JSON format (structured data for programmatic access)
    """

    DEFAULT_EXPORT_DIR = os.path.expanduser("~/claude-exports/")

    def __init__(self, export_dir: Optional[str] = None):
        """
        Initialize the transcript exporter.

        Args:
            export_dir: Directory to save exports (defaults to ~/claude-exports/)
        """
        self.export_dir = Path(export_dir or self.DEFAULT_EXPORT_DIR)
        self._ensure_export_dir()

    def _ensure_export_dir(self) -> None:
        """Create export directory if it doesn't exist."""
        self.export_dir.mkdir(parents=True, exist_ok=True)

    def parse_transcript(self, raw_text: str) -> List[ConversationMessage]:
        """
        Parse raw transcript text into structured messages.

        Identifies commands and responses based on visual separators and markers
        that Claude Multi-Terminal uses.

        Args:
            raw_text: Raw text from SelectableRichLog

        Returns:
            List of ConversationMessage objects
        """
        messages = []
        lines = raw_text.split('\n')

        i = 0
        while i < len(lines):
            line = lines[i]

            # Look for command separator (╔═══...╗ pattern)
            if line.startswith('╔') and '═' in line:
                # Next line contains timestamp and command
                if i + 1 < len(lines):
                    header_line = lines[i + 1]
                    # Extract timestamp and command
                    # Format: "║ ⏱ HH:MM:SS ┊ ⚡ Command: <command> ║"
                    timestamp_match = re.search(r'⏱\s*(\d{2}:\d{2}:\d{2})', header_line)
                    command_match = re.search(r'⚡ Command:\s*(.+?)(?:\s+║|$)', header_line)

                    if timestamp_match and command_match:
                        timestamp = timestamp_match.group(1)
                        command = command_match.group(1).strip()

                        messages.append(ConversationMessage(
                            timestamp=timestamp,
                            type='command',
                            content=command,
                            metadata={'separator': 'box'}
                        ))

                # Skip to end of separator box (╚═══...╝)
                i += 1
                while i < len(lines) and not lines[i].startswith('╚'):
                    i += 1
                i += 1  # Skip the closing line

                # Now collect response until next command or end
                response_lines = []
                response_start_idx = i

                # Skip empty lines after separator
                while i < len(lines) and not lines[i].strip():
                    i += 1

                # Look for "📝 Response:" marker
                if i < len(lines) and '📝 Response:' in lines[i]:
                    i += 1  # Skip the response marker line

                # Collect response lines until next command separator
                while i < len(lines):
                    if lines[i].startswith('╔') and '═' in lines[i]:
                        # Found next command
                        break

                    # Check for completion marker (✻ Baked/Sautéed/etc)
                    if lines[i].strip().startswith('✻'):
                        # Include completion marker in response
                        response_lines.append(lines[i])
                        i += 1
                        break

                    response_lines.append(lines[i])
                    i += 1

                # Add response message if we collected any content
                if response_lines:
                    response_content = '\n'.join(response_lines).strip()
                    if response_content:
                        # Use same timestamp as command
                        messages.append(ConversationMessage(
                            timestamp=timestamp if timestamp_match else '',
                            type='response',
                            content=response_content
                        ))
            else:
                i += 1

        return messages

    def export_to_markdown(
        self,
        messages: List[ConversationMessage],
        session_name: str,
        filename: Optional[str] = None
    ) -> str:
        """
        Export conversation to Markdown format.

        Args:
            messages: List of conversation messages
            session_name: Name of the session
            filename: Optional custom filename (without extension)

        Returns:
            Path to the exported file
        """
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"session_{session_name}_{timestamp}.md"
        elif not filename.endswith('.md'):
            filename += '.md'

        filepath = self.export_dir / filename

        # Generate Markdown content
        md_lines = [
            f"# Claude Multi-Terminal Session: {session_name}",
            "",
            f"**Exported:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "",
            f"**Total Messages:** {len(messages)}",
            "",
            "---",
            ""
        ]

        for msg in messages:
            if msg.type == 'command':
                md_lines.extend([
                    f"## Command [{msg.timestamp}]",
                    "",
                    "```bash",
                    msg.content,
                    "```",
                    ""
                ])
            elif msg.type == 'response':
                md_lines.extend([
                    f"### Response [{msg.timestamp}]",
                    "",
                    msg.content,
                    "",
                    "---",
                    ""
                ])

        # Write to file
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write('\n'.join(md_lines))

        return str(filepath)

    def export_to_json(
        self,
        messages: List[ConversationMessage],
        session_name: str,
        session_id: str,
        filename: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Export conversation to JSON format.

        Args:
            messages: List of conversation messages
            session_name: Name of the session
            session_id: Session UUID
            filename: Optional custom filename (without extension)
            metadata: Optional additional metadata to include

        Returns:
            Path to the exported file
        """
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"session_{session_name}_{timestamp}.json"
        elif not filename.endswith('.json'):
            filename += '.json'

        filepath = self.export_dir / filename

        # Build JSON structure
        export_data = {
            "session": {
                "id": session_id,
                "name": session_name,
                "exported_at": datetime.now().isoformat(),
                "message_count": len(messages)
            },
            "messages": [asdict(msg) for msg in messages],
            "metadata": metadata or {}
        }

        # Write to file with pretty formatting
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, indent=2, ensure_ascii=False)

        return str(filepath)

    def export_raw_text(
        self,
        raw_text: str,
        session_name: str,
        filename: Optional[str] = None
    ) -> str:
        """
        Export raw transcript text (plain text format).

        Args:
            raw_text: Raw text from SelectableRichLog
            session_name: Name of the session
            filename: Optional custom filename (without extension)

        Returns:
            Path to the exported file
        """
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"session_{session_name}_{timestamp}.txt"
        elif not filename.endswith('.txt'):
            filename += '.txt'

        filepath = self.export_dir / filename

        # Add header to raw text
        header = (
            f"Claude Multi-Terminal Session: {session_name}\n"
            f"Exported: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
            f"{'=' * 80}\n\n"
        )

        # Write to file
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(header + raw_text)

        return str(filepath)

    def export_to_text(
        self,
        output_lines: List[str],
        filepath: Path,
    ) -> bool:
        """
        Export output lines to text file.

        Args:
            output_lines: List of output lines to export
            filepath: Path object for the output file

        Returns:
            True if successful, False otherwise
        """
        try:
            # Join lines and write to file
            content = '\n'.join(output_lines)

            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)

            return True
        except Exception as e:
            print(f"Error exporting to text: {e}")
            return False


def sanitize_filename(name: str) -> str:
    """
    Sanitize a string to be used as a filename.

    Args:
        name: Raw string to sanitize

    Returns:
        Sanitized filename-safe string
    """
    # Remove or replace invalid filename characters
    name = re.sub(r'[<>:"/\\|?*]', '_', name)
    # Remove leading/trailing spaces and dots
    name = name.strip('. ')
    # Limit length
    if len(name) > 200:
        name = name[:200]
    return name or 'unnamed'
