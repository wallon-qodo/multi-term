"""
Keyboard Shortcut Reference Generator and Cheat Sheet System.

This module provides comprehensive documentation generation for all keyboard shortcuts,
creating multiple output formats (Markdown, HTML, plain text) for different use cases.
Implements search functionality and mode-specific filtering.

Author: Claude Code Team
License: MIT
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Optional
import json
import re


class ShortcutCategory(Enum):
    """Categories for organizing keyboard shortcuts."""
    NAVIGATION = "Navigation"
    SESSION_MGMT = "Session Management"
    WORKSPACE = "Workspace Operations"
    LAYOUT = "Layout Operations"
    COPY_MODE = "Copy Mode"
    SEARCH = "Search"
    SYSTEM = "System"
    VISUAL = "Visual & Display"


@dataclass
class ShortcutEntry:
    """Represents a single keyboard shortcut."""
    key: str
    action: str
    mode: str
    category: ShortcutCategory
    description: str = ""
    frequency: str = "common"  # common, frequent, rare

    def matches_query(self, query: str) -> bool:
        """Check if this entry matches a search query."""
        query_lower = query.lower()
        return (
            query_lower in self.key.lower() or
            query_lower in self.action.lower() or
            query_lower in self.description.lower() or
            query_lower in self.mode.lower()
        )


class ShortcutReference:
    """
    Generates comprehensive keyboard shortcut documentation.

    Provides multiple export formats (Markdown, HTML) and search capabilities
    for discovering keyboard shortcuts across all modes and categories.
    """

    def __init__(self):
        """Initialize the shortcut reference with all defined shortcuts."""
        self.shortcuts: list[ShortcutEntry] = []
        self._load_shortcuts()

    def _load_shortcuts(self) -> None:
        """Load all keyboard shortcuts from the application."""
        # NORMAL Mode - Window Management & Navigation
        normal_shortcuts = [
            ShortcutEntry("i", "Enter INSERT mode", "NORMAL", ShortcutCategory.NAVIGATION,
                         "Switch to INSERT mode for terminal input", "frequent"),
            ShortcutEntry("v", "Enter COPY mode", "NORMAL", ShortcutCategory.COPY_MODE,
                         "Enter COPY mode for scrollback navigation and selection", "frequent"),
            ShortcutEntry("Ctrl+B", "COMMAND mode prefix", "NORMAL", ShortcutCategory.NAVIGATION,
                         "Enter COMMAND mode for advanced operations (2-key sequence)", "frequent"),
            ShortcutEntry("Esc", "Return to NORMAL mode", "ANY", ShortcutCategory.NAVIGATION,
                         "Exit current mode and return to NORMAL", "frequent"),

            # Workspace switching
            ShortcutEntry("1-9", "Switch workspace", "NORMAL", ShortcutCategory.WORKSPACE,
                         "Switch to workspace 1-9", "frequent"),
            ShortcutEntry("Shift+1-9", "Move session to workspace", "NORMAL", ShortcutCategory.WORKSPACE,
                         "Move focused session to workspace 1-9", "common"),

            # Pane navigation
            ShortcutEntry("h/j/k/l", "Navigate panes (vim)", "NORMAL", ShortcutCategory.NAVIGATION,
                         "Move focus between panes using vim-style keys", "frequent"),
            ShortcutEntry("Tab", "Next pane", "NORMAL", ShortcutCategory.NAVIGATION,
                         "Move focus to next pane", "frequent"),
            ShortcutEntry("Shift+Tab", "Previous pane", "NORMAL", ShortcutCategory.NAVIGATION,
                         "Move focus to previous pane", "frequent"),
            ShortcutEntry("n", "Next pane", "NORMAL", ShortcutCategory.NAVIGATION,
                         "Move to next pane (alternative)", "common"),
            ShortcutEntry("p", "Previous pane", "NORMAL", ShortcutCategory.NAVIGATION,
                         "Move to previous pane (alternative)", "common"),

            # Session management
            ShortcutEntry("Ctrl+N", "New session", "NORMAL", ShortcutCategory.SESSION_MGMT,
                         "Create new terminal session", "frequent"),
            ShortcutEntry("x", "Close session", "NORMAL", ShortcutCategory.SESSION_MGMT,
                         "Close current session", "common"),
            ShortcutEntry("Ctrl+W", "Close session", "NORMAL", ShortcutCategory.SESSION_MGMT,
                         "Close current session (alternative)", "common"),
            ShortcutEntry("r", "Rename session", "NORMAL", ShortcutCategory.SESSION_MGMT,
                         "Rename current session", "common"),
            ShortcutEntry("Ctrl+R", "Rename session", "NORMAL", ShortcutCategory.SESSION_MGMT,
                         "Rename current session (alternative)", "common"),
            ShortcutEntry("Ctrl+Shift+T", "Reopen last session", "NORMAL", ShortcutCategory.SESSION_MGMT,
                         "Reopen last closed session", "rare"),

            # System
            ShortcutEntry("q", "Quit application", "NORMAL", ShortcutCategory.SYSTEM,
                         "Exit the application", "common"),
            ShortcutEntry("Ctrl+Q", "Quit application", "NORMAL", ShortcutCategory.SYSTEM,
                         "Exit the application (alternative)", "common"),
            ShortcutEntry("Ctrl+S", "Save workspace", "NORMAL", ShortcutCategory.WORKSPACE,
                         "Save current workspace state", "common"),
            ShortcutEntry("Ctrl+L", "Load workspace", "NORMAL", ShortcutCategory.WORKSPACE,
                         "Load saved workspace", "rare"),
            ShortcutEntry("F10", "Workspace manager", "NORMAL", ShortcutCategory.WORKSPACE,
                         "Open workspace management interface", "common"),
            ShortcutEntry("Ctrl+H", "History browser", "NORMAL", ShortcutCategory.SYSTEM,
                         "Browse session history", "common"),
            ShortcutEntry("F9", "History browser", "NORMAL", ShortcutCategory.SYSTEM,
                         "Browse session history (alternative)", "common"),

            # Visual
            ShortcutEntry("Ctrl+F", "Focus mode", "NORMAL", ShortcutCategory.VISUAL,
                         "Toggle focus mode (maximize current pane)", "common"),
            ShortcutEntry("F11", "Focus mode", "NORMAL", ShortcutCategory.VISUAL,
                         "Toggle focus mode (alternative)", "common"),
            ShortcutEntry("F2", "Toggle mouse", "NORMAL", ShortcutCategory.VISUAL,
                         "Toggle mouse support (disable for text selection)", "rare"),
            ShortcutEntry("Ctrl+B", "Toggle broadcast", "NORMAL", ShortcutCategory.SESSION_MGMT,
                         "Toggle broadcast mode (send to all sessions)", "rare"),

            # Search
            ShortcutEntry("Ctrl+Shift+F", "Search", "NORMAL", ShortcutCategory.SEARCH,
                         "Open search panel", "common"),
            ShortcutEntry("Ctrl+C", "Copy output", "NORMAL", ShortcutCategory.COPY_MODE,
                         "Copy terminal output", "common"),
        ]

        # COMMAND Mode (Ctrl+B prefix)
        command_shortcuts = [
            # Layout operations
            ShortcutEntry("Ctrl+B h", "Split horizontal", "COMMAND", ShortcutCategory.LAYOUT,
                         "Split pane horizontally (top/bottom)", "frequent"),
            ShortcutEntry("Ctrl+B v", "Split vertical", "COMMAND", ShortcutCategory.LAYOUT,
                         "Split pane vertically (left/right)", "frequent"),
            ShortcutEntry("Ctrl+B r", "Rotate split", "COMMAND", ShortcutCategory.LAYOUT,
                         "Rotate split direction", "common"),
            ShortcutEntry("Ctrl+B =", "Equalize splits", "COMMAND", ShortcutCategory.LAYOUT,
                         "Equalize all split ratios to 50/50", "common"),
            ShortcutEntry("Ctrl+B [", "Increase left/top", "COMMAND", ShortcutCategory.LAYOUT,
                         "Increase left/top pane size by 5%", "common"),
            ShortcutEntry("Ctrl+B ]", "Increase right/bottom", "COMMAND", ShortcutCategory.LAYOUT,
                         "Increase right/bottom pane size by 5%", "common"),

            # Layout modes
            ShortcutEntry("Ctrl+B l", "BSP layout", "COMMAND", ShortcutCategory.LAYOUT,
                         "Switch to BSP (tiling) layout mode", "common"),
            ShortcutEntry("Ctrl+B s", "STACK layout", "COMMAND", ShortcutCategory.LAYOUT,
                         "Switch to STACK (monocle) layout mode", "common"),
            ShortcutEntry("Ctrl+B t", "TAB layout", "COMMAND", ShortcutCategory.LAYOUT,
                         "Switch to TAB (floating) layout mode", "common"),
            ShortcutEntry("Ctrl+B n", "Next session", "COMMAND", ShortcutCategory.NAVIGATION,
                         "Next session in STACK/TAB mode", "common"),
            ShortcutEntry("Ctrl+B p", "Previous session", "COMMAND", ShortcutCategory.NAVIGATION,
                         "Previous session in STACK/TAB mode", "common"),

            # Help
            ShortcutEntry("Ctrl+B ?", "Show help", "COMMAND", ShortcutCategory.SYSTEM,
                         "Display help overlay with all shortcuts", "common"),
        ]

        # COPY Mode - Scrollback Navigation
        copy_shortcuts = [
            # Movement
            ShortcutEntry("j/k", "Move down/up", "COPY", ShortcutCategory.COPY_MODE,
                         "Move cursor down/up by one line", "frequent"),
            ShortcutEntry("h/l", "Move left/right", "COPY", ShortcutCategory.COPY_MODE,
                         "Move cursor left/right by one character", "frequent"),
            ShortcutEntry("w", "Next word", "COPY", ShortcutCategory.COPY_MODE,
                         "Move forward by word", "frequent"),
            ShortcutEntry("b", "Previous word", "COPY", ShortcutCategory.COPY_MODE,
                         "Move backward by word", "frequent"),
            ShortcutEntry("0", "Start of line", "COPY", ShortcutCategory.COPY_MODE,
                         "Jump to start of line", "frequent"),
            ShortcutEntry("$", "End of line", "COPY", ShortcutCategory.COPY_MODE,
                         "Jump to end of line", "frequent"),
            ShortcutEntry("g", "Top of buffer", "COPY", ShortcutCategory.COPY_MODE,
                         "Jump to top of scrollback buffer", "common"),
            ShortcutEntry("G", "Bottom of buffer", "COPY", ShortcutCategory.COPY_MODE,
                         "Jump to bottom of scrollback buffer", "common"),

            # Search
            ShortcutEntry("/", "Search forward", "COPY", ShortcutCategory.SEARCH,
                         "Search forward in scrollback", "common"),
            ShortcutEntry("?", "Search backward", "COPY", ShortcutCategory.SEARCH,
                         "Search backward in scrollback", "common"),
            ShortcutEntry("n", "Next match", "COPY", ShortcutCategory.SEARCH,
                         "Jump to next search match", "common"),
            ShortcutEntry("N", "Previous match", "COPY", ShortcutCategory.SEARCH,
                         "Jump to previous search match", "common"),

            # Selection
            ShortcutEntry("v", "Visual select", "COPY", ShortcutCategory.COPY_MODE,
                         "Start visual selection mode", "frequent"),
            ShortcutEntry("y", "Yank (copy)", "COPY", ShortcutCategory.COPY_MODE,
                         "Copy selection to clipboard and exit COPY mode", "frequent"),
            ShortcutEntry("Esc", "Exit COPY mode", "COPY", ShortcutCategory.NAVIGATION,
                         "Return to NORMAL mode", "frequent"),
        ]

        # INSERT Mode
        insert_shortcuts = [
            ShortcutEntry("Esc", "Return to NORMAL", "INSERT", ShortcutCategory.NAVIGATION,
                         "Exit INSERT mode and return to NORMAL", "frequent"),
            ShortcutEntry("(any key)", "Pass to terminal", "INSERT", ShortcutCategory.SESSION_MGMT,
                         "All other keys pass through to terminal", "frequent"),
        ]

        self.shortcuts = normal_shortcuts + command_shortcuts + copy_shortcuts + insert_shortcuts

    def generate_cheat_sheet(self) -> str:
        """
        Generate comprehensive Markdown cheat sheet.

        Returns:
            Formatted Markdown document with all shortcuts organized by mode and category.
        """
        md = ["# Claude Multi-Terminal - Keyboard Shortcuts\n"]
        md.append("*TUIOS-Inspired Multi-Terminal Interface with Modal Keyboard Control*\n")
        md.append("---\n\n")

        # Quick reference table
        md.append("## Quick Reference\n\n")
        md.append("| Key | Action | Mode | Category |\n")
        md.append("|-----|--------|------|----------|\n")

        # Show most frequent shortcuts
        frequent = [s for s in self.shortcuts if s.frequency == "frequent"]
        for shortcut in frequent[:15]:  # Top 15 most used
            md.append(f"| `{shortcut.key}` | {shortcut.action} | {shortcut.mode} | {shortcut.category.value} |\n")

        md.append("\n---\n\n")

        # Detailed guide by mode
        md.append("## Detailed Guide\n\n")

        modes = ["NORMAL", "COMMAND", "COPY", "INSERT"]

        for mode in modes:
            mode_shortcuts = [s for s in self.shortcuts if s.mode == mode or s.mode == "ANY"]
            if not mode_shortcuts:
                continue

            md.append(f"### {mode} Mode\n\n")

            if mode == "NORMAL":
                md.append("*Default mode for window management and navigation*\n\n")
            elif mode == "COMMAND":
                md.append("*Advanced layout operations (Ctrl+B prefix required)*\n\n")
            elif mode == "COPY":
                md.append("*Scrollback navigation and text selection*\n\n")
            elif mode == "INSERT":
                md.append("*Direct terminal input mode*\n\n")

            # Group by category
            categories = {}
            for shortcut in mode_shortcuts:
                cat = shortcut.category.value
                if cat not in categories:
                    categories[cat] = []
                categories[cat].append(shortcut)

            for category, shortcuts in sorted(categories.items()):
                md.append(f"**{category}:**\n")
                for shortcut in shortcuts:
                    desc = f" - {shortcut.description}" if shortcut.description else ""
                    md.append(f"- **`{shortcut.key}`** - {shortcut.action}{desc}\n")
                md.append("\n")

            md.append("\n")

        # Footer
        md.append("---\n\n")
        md.append("## Tips\n\n")
        md.append("- **Modal Design**: Based on vim/tmux principles - distinct modes for different tasks\n")
        md.append("- **Ctrl+B Prefix**: Command mode uses 2-key sequences (press Ctrl+B, then command key)\n")
        md.append("- **ESC Key**: Always returns to NORMAL mode from any mode\n")
        md.append("- **Vim Keys**: h/j/k/l navigation supported throughout\n")
        md.append("- **Text Selection**: F2 toggles mouse support (disable for terminal text selection)\n")
        md.append("\n")
        md.append("*Generated by Claude Multi-Terminal Shortcut Reference System*\n")

        return "".join(md)

    def generate_quick_ref(self) -> str:
        """
        Generate compact quick reference fitting in 80x24 terminal.

        Returns:
            Compact text format with most essential shortcuts.
        """
        lines = []
        lines.append("┌─────────────────────────────────────────────────────────────────────────────┐")
        lines.append("│         CLAUDE MULTI-TERMINAL - KEYBOARD SHORTCUTS QUICK REFERENCE          │")
        lines.append("├─────────────────────────────────────────────────────────────────────────────┤")
        lines.append("│ MODES: i=INSERT  v=COPY  Ctrl+B=COMMAND  Esc=NORMAL                        │")
        lines.append("├─────────────────────────────────────────────────────────────────────────────┤")
        lines.append("│ NAVIGATION                   │ SESSION MANAGEMENT                           │")
        lines.append("│ Tab/Shift+Tab  Next/Prev     │ Ctrl+N         New session                   │")
        lines.append("│ h/j/k/l        Vim movement  │ x / Ctrl+W     Close session                 │")
        lines.append("│ 1-9            Switch space  │ r / Ctrl+R     Rename session                │")
        lines.append("│ Shift+1-9      Move to space │ Ctrl+S         Save workspace                │")
        lines.append("├─────────────────────────────────────────────────────────────────────────────┤")
        lines.append("│ LAYOUT (Ctrl+B prefix)       │ COPY MODE (v to enter)                       │")
        lines.append("│ Ctrl+B h       Split horiz   │ j/k            Down/Up                       │")
        lines.append("│ Ctrl+B v       Split vert    │ w/b            Next/Prev word                │")
        lines.append("│ Ctrl+B r       Rotate split  │ 0/$            Start/End line                │")
        lines.append("│ Ctrl+B =       Equalize      │ g/G            Top/Bottom buffer             │")
        lines.append("│ Ctrl+B [/]     Adjust split  │ v              Start selection               │")
        lines.append("│ Ctrl+B l/s/t   Layout mode   │ y              Yank (copy) & exit            │")
        lines.append("│ Ctrl+B ?       Help overlay  │ /  ?           Search fwd/back               │")
        lines.append("├─────────────────────────────────────────────────────────────────────────────┤")
        lines.append("│ SYSTEM                       │ VISUAL                                       │")
        lines.append("│ q / Ctrl+Q     Quit          │ Ctrl+F / F11   Focus mode                    │")
        lines.append("│ F10            Workspace mgr │ F2             Toggle mouse                  │")
        lines.append("│ Ctrl+H / F9    History       │ Ctrl+Shift+F   Search                        │")
        lines.append("└─────────────────────────────────────────────────────────────────────────────┘")

        return "\n".join(lines)

    def export_to_markdown(self, filepath: Optional[Path] = None) -> Path:
        """
        Export cheat sheet to Markdown file.

        Args:
            filepath: Output file path (default: ~/.multi-term/shortcuts.md)

        Returns:
            Path to exported file
        """
        if filepath is None:
            filepath = Path.home() / ".multi-term" / "SHORTCUTS.md"

        filepath.parent.mkdir(parents=True, exist_ok=True)

        content = self.generate_cheat_sheet()
        filepath.write_text(content, encoding="utf-8")

        return filepath

    def export_to_html(self, filepath: Optional[Path] = None) -> Path:
        """
        Generate standalone HTML reference with embedded CSS.

        Args:
            filepath: Output file path (default: ~/.multi-term/shortcuts.html)

        Returns:
            Path to exported file
        """
        if filepath is None:
            filepath = Path.home() / ".multi-term" / "SHORTCUTS.html"

        filepath.parent.mkdir(parents=True, exist_ok=True)

        html = self._generate_html()
        filepath.write_text(html, encoding="utf-8")

        return filepath

    def _generate_html(self) -> str:
        """Generate HTML content with embedded CSS."""
        # Homebrew theme colors
        css = """
        <style>
            * { margin: 0; padding: 0; box-sizing: border-box; }
            body {
                font-family: 'SF Mono', 'Monaco', 'Consolas', monospace;
                background: #181818;
                color: #f0f0f0;
                padding: 2rem;
                line-height: 1.6;
            }
            .container { max-width: 1200px; margin: 0 auto; }
            h1 {
                color: #64b4f0;
                border-bottom: 2px solid #64b4f0;
                padding-bottom: 0.5rem;
                margin-bottom: 1rem;
            }
            h2 {
                color: #ffb446;
                margin-top: 2rem;
                margin-bottom: 1rem;
                border-left: 4px solid #ffb446;
                padding-left: 0.5rem;
            }
            h3 {
                color: #9ac896;
                margin-top: 1.5rem;
                margin-bottom: 0.5rem;
            }
            table {
                width: 100%;
                border-collapse: collapse;
                margin: 1rem 0;
                background: #1c1c1c;
            }
            th {
                background: #2a2a2a;
                color: #64b4f0;
                padding: 0.75rem;
                text-align: left;
                border: 1px solid #3a3a3a;
            }
            td {
                padding: 0.5rem;
                border: 1px solid #2a2a2a;
            }
            tr:hover { background: #242424; }
            code, .key {
                background: #2a2a2a;
                padding: 0.2rem 0.4rem;
                border-radius: 3px;
                color: #ff9d76;
                font-family: 'SF Mono', monospace;
            }
            .mode-normal { color: #64b4f0; }
            .mode-command { color: #ff9d76; }
            .mode-copy { color: #ffb446; }
            .mode-insert { color: #9ac896; }
            .category {
                display: inline-block;
                padding: 0.2rem 0.5rem;
                border-radius: 3px;
                font-size: 0.85em;
                background: #2a2a2a;
                color: #aaa;
            }
            .search-box {
                margin: 1rem 0;
                padding: 0.75rem;
                background: #1c1c1c;
                border: 1px solid #3a3a3a;
                border-radius: 4px;
            }
            #search {
                width: 100%;
                padding: 0.5rem;
                background: #242424;
                border: 1px solid #3a3a3a;
                color: #f0f0f0;
                font-family: inherit;
                border-radius: 3px;
            }
            .tips {
                background: #1c1c1c;
                border-left: 4px solid #9ac896;
                padding: 1rem;
                margin: 2rem 0;
            }
            .tips ul { margin-left: 1.5rem; }
            .tips li { margin: 0.5rem 0; }
            @media print {
                body { background: white; color: black; }
                table { page-break-inside: avoid; }
            }
        </style>
        """

        # Generate HTML body
        html_parts = [
            "<!DOCTYPE html>",
            "<html lang='en'>",
            "<head>",
            "<meta charset='UTF-8'>",
            "<meta name='viewport' content='width=device-width, initial-scale=1.0'>",
            "<title>Claude Multi-Terminal - Keyboard Shortcuts</title>",
            css,
            "</head>",
            "<body>",
            "<div class='container'>",
            "<h1>Claude Multi-Terminal - Keyboard Shortcuts</h1>",
            "<p><em>TUIOS-Inspired Multi-Terminal Interface with Modal Keyboard Control</em></p>",

            # Search box
            "<div class='search-box'>",
            "<input type='text' id='search' placeholder='Search shortcuts... (e.g., split, ctrl+b, copy)'>",
            "</div>",

            # Quick reference table
            "<h2>Quick Reference</h2>",
            "<table id='shortcuts-table'>",
            "<thead><tr>",
            "<th>Key</th><th>Action</th><th>Mode</th><th>Category</th>",
            "</tr></thead>",
            "<tbody>",
        ]

        # Add all shortcuts to table
        for shortcut in sorted(self.shortcuts, key=lambda s: (s.mode, s.category.value, s.key)):
            mode_class = f"mode-{shortcut.mode.lower()}"
            html_parts.extend([
                "<tr>",
                f"<td><code>{self._escape_html(shortcut.key)}</code></td>",
                f"<td>{self._escape_html(shortcut.action)}</td>",
                f"<td class='{mode_class}'>{shortcut.mode}</td>",
                f"<td><span class='category'>{shortcut.category.value}</span></td>",
                "</tr>",
            ])

        html_parts.extend([
            "</tbody>",
            "</table>",

            # Detailed sections
            "<h2>Detailed Guide</h2>",
        ])

        # Add detailed mode sections
        for mode in ["NORMAL", "COMMAND", "COPY", "INSERT"]:
            mode_shortcuts = [s for s in self.shortcuts if s.mode == mode or s.mode == "ANY"]
            if not mode_shortcuts:
                continue

            html_parts.append(f"<h3>{mode} Mode</h3>")

            # Group by category
            categories = {}
            for shortcut in mode_shortcuts:
                cat = shortcut.category.value
                if cat not in categories:
                    categories[cat] = []
                categories[cat].append(shortcut)

            for category, shortcuts in sorted(categories.items()):
                html_parts.append(f"<h4>{category}</h4>")
                html_parts.append("<ul>")
                for shortcut in shortcuts:
                    desc = f" - {self._escape_html(shortcut.description)}" if shortcut.description else ""
                    html_parts.append(
                        f"<li><code>{self._escape_html(shortcut.key)}</code> - "
                        f"{self._escape_html(shortcut.action)}{desc}</li>"
                    )
                html_parts.append("</ul>")

        # Tips section
        html_parts.extend([
            "<div class='tips'>",
            "<h3>Tips & Tricks</h3>",
            "<ul>",
            "<li><strong>Modal Design:</strong> Based on vim/tmux principles - distinct modes for different tasks</li>",
            "<li><strong>Ctrl+B Prefix:</strong> Command mode uses 2-key sequences (press Ctrl+B, then command key)</li>",
            "<li><strong>ESC Key:</strong> Always returns to NORMAL mode from any mode</li>",
            "<li><strong>Vim Keys:</strong> h/j/k/l navigation supported throughout</li>",
            "<li><strong>Text Selection:</strong> F2 toggles mouse support (disable for terminal text selection)</li>",
            "</ul>",
            "</div>",

            "</div>",  # container

            # JavaScript for search
            "<script>",
            "const searchInput = document.getElementById('search');",
            "const table = document.getElementById('shortcuts-table');",
            "const rows = table.getElementsByTagName('tbody')[0].getElementsByTagName('tr');",
            "",
            "searchInput.addEventListener('input', function() {",
            "  const query = this.value.toLowerCase();",
            "  for (let row of rows) {",
            "    const text = row.textContent.toLowerCase();",
            "    row.style.display = text.includes(query) ? '' : 'none';",
            "  }",
            "});",
            "</script>",

            "</body>",
            "</html>",
        ])

        return "\n".join(html_parts)

    def _escape_html(self, text: str) -> str:
        """Escape HTML special characters."""
        return (text
                .replace("&", "&amp;")
                .replace("<", "&lt;")
                .replace(">", "&gt;")
                .replace('"', "&quot;")
                .replace("'", "&#39;"))

    def get_mode_shortcuts(self, mode: str) -> list[ShortcutEntry]:
        """
        Get all shortcuts for a specific mode.

        Args:
            mode: Mode name (NORMAL, INSERT, COPY, COMMAND, ANY)

        Returns:
            List of shortcuts for the specified mode
        """
        mode_upper = mode.upper()
        return [s for s in self.shortcuts if s.mode == mode_upper or s.mode == "ANY"]

    def search_shortcuts(self, query: str) -> list[ShortcutEntry]:
        """
        Search shortcuts by keyword.

        Searches across key, action, description, and mode fields.
        Uses fuzzy matching for better discoverability.

        Args:
            query: Search query string

        Returns:
            List of matching shortcuts, sorted by relevance
        """
        if not query:
            return self.shortcuts

        results = []
        query_lower = query.lower()

        for shortcut in self.shortcuts:
            if shortcut.matches_query(query):
                # Calculate relevance score
                score = 0
                if query_lower in shortcut.key.lower():
                    score += 10
                if query_lower in shortcut.action.lower():
                    score += 5
                if query_lower in shortcut.mode.lower():
                    score += 3

                results.append((score, shortcut))

        # Sort by score (highest first)
        results.sort(key=lambda x: x[0], reverse=True)

        return [shortcut for score, shortcut in results]

    def get_category_shortcuts(self, category: ShortcutCategory) -> list[ShortcutEntry]:
        """
        Get all shortcuts for a specific category.

        Args:
            category: ShortcutCategory enum value

        Returns:
            List of shortcuts in the specified category
        """
        return [s for s in self.shortcuts if s.category == category]

    def get_frequent_shortcuts(self, limit: int = 10) -> list[ShortcutEntry]:
        """
        Get most frequently used shortcuts.

        Args:
            limit: Maximum number of shortcuts to return

        Returns:
            List of most frequent shortcuts
        """
        frequent = [s for s in self.shortcuts if s.frequency == "frequent"]
        return frequent[:limit]

    def export_to_json(self, filepath: Optional[Path] = None) -> Path:
        """
        Export shortcuts to JSON format for programmatic use.

        Args:
            filepath: Output file path (default: ~/.multi-term/shortcuts.json)

        Returns:
            Path to exported file
        """
        if filepath is None:
            filepath = Path.home() / ".multi-term" / "shortcuts.json"

        filepath.parent.mkdir(parents=True, exist_ok=True)

        data = {
            "version": "1.0.0",
            "shortcuts": [
                {
                    "key": s.key,
                    "action": s.action,
                    "mode": s.mode,
                    "category": s.category.value,
                    "description": s.description,
                    "frequency": s.frequency,
                }
                for s in self.shortcuts
            ]
        }

        filepath.write_text(json.dumps(data, indent=2), encoding="utf-8")

        return filepath


# Convenience functions

def generate_all_docs(output_dir: Optional[Path] = None) -> dict[str, Path]:
    """
    Generate all documentation formats.

    Args:
        output_dir: Output directory (default: ~/.multi-term/)

    Returns:
        Dictionary mapping format name to output file path
    """
    if output_dir is None:
        output_dir = Path.home() / ".multi-term"

    output_dir.mkdir(parents=True, exist_ok=True)

    ref = ShortcutReference()

    return {
        "markdown": ref.export_to_markdown(output_dir / "SHORTCUTS.md"),
        "html": ref.export_to_html(output_dir / "SHORTCUTS.html"),
        "json": ref.export_to_json(output_dir / "shortcuts.json"),
    }


def print_quick_ref() -> None:
    """Print quick reference to console."""
    ref = ShortcutReference()
    print(ref.generate_quick_ref())


# Export public API
__all__ = [
    "ShortcutCategory",
    "ShortcutEntry",
    "ShortcutReference",
    "generate_all_docs",
    "print_quick_ref",
]
