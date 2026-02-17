"""
Comprehensive Test Suite for Phase 5 Help System & Discoverability
Tests help overlay, shortcut reference, footer hints, and documentation.

Test Coverage:
1. HelpCategory Tests - Enum values and category management
2. HelpEntry Tests - Entry creation and validation
3. HelpOverlay Tests - Overlay display, filtering, navigation
4. ShortcutReference Tests - Reference generation and exports
5. FooterHints Tests - Mode-aware footer hints
6. App Integration Tests - Help system integration with app
7. Documentation Tests - Completeness and validation

Target: ~47 tests, 100% code coverage, <1s execution time
"""

import pytest
from enum import Enum
from typing import Optional, List
from pathlib import Path
import tempfile
import os


# =============================================================================
# Mock Classes (until actual implementation is available)
# =============================================================================

class AppMode(Enum):
    """Mock AppMode enum for testing."""
    NORMAL = 1
    INSERT = 2
    COPY = 3
    COMMAND = 4


class HelpCategory(Enum):
    """Categories for organizing help entries."""
    NAVIGATION = "navigation"
    EDITING = "editing"
    LAYOUT = "layout"
    WORKSPACE = "workspace"
    CLIPBOARD = "clipboard"
    COMMAND = "command"
    SYSTEM = "system"


class HelpEntry:
    """Represents a single help entry with keybinding and description."""

    def __init__(
        self,
        key: str,
        action: str,
        category: HelpCategory,
        mode: Optional[AppMode] = None,
        example: Optional[str] = None,
        description: Optional[str] = None
    ):
        """
        Initialize help entry.

        Args:
            key: Keybinding (e.g., "Ctrl+B h")
            action: Short action description
            category: Help category
            mode: Specific mode (None = all modes)
            example: Usage example
            description: Detailed description
        """
        if not key:
            raise ValueError("Key cannot be empty")
        if not action:
            raise ValueError("Action cannot be empty")

        self.key = key
        self.action = action
        self.category = category
        self.mode = mode
        self.example = example
        self.description = description

    def __eq__(self, other) -> bool:
        """Compare help entries."""
        if not isinstance(other, HelpEntry):
            return False
        return (
            self.key == other.key and
            self.action == other.action and
            self.category == other.category and
            self.mode == other.mode
        )

    def __repr__(self) -> str:
        """String representation."""
        mode_str = f", mode={self.mode.name}" if self.mode else ""
        return f"HelpEntry(key='{self.key}', action='{self.action}'{mode_str})"


class HelpOverlay:
    """Help overlay widget for displaying keyboard shortcuts."""

    def __init__(self):
        """Initialize help overlay."""
        self.visible = False
        self.current_mode_filter: Optional[AppMode] = None
        self.current_category_filter: Optional[HelpCategory] = None
        self.entries: List[HelpEntry] = []
        self.scroll_position = 0
        self._load_default_entries()

    def _load_default_entries(self):
        """Load default help entries for all phases."""
        # Phase 1: Modal System
        self.entries.extend([
            HelpEntry("i", "Enter INSERT mode", HelpCategory.EDITING, AppMode.NORMAL),
            HelpEntry("v", "Enter COPY mode", HelpCategory.CLIPBOARD, AppMode.NORMAL),
            HelpEntry(":", "Enter COMMAND mode", HelpCategory.COMMAND, AppMode.NORMAL),
            HelpEntry("Esc", "Return to NORMAL mode", HelpCategory.NAVIGATION, AppMode.INSERT),
            HelpEntry("Esc", "Return to NORMAL mode", HelpCategory.NAVIGATION, AppMode.COPY),
            HelpEntry("Esc", "Cancel command", HelpCategory.COMMAND, AppMode.COMMAND),
        ])

        # Phase 2: Workspace Management
        self.entries.extend([
            HelpEntry("Ctrl+B 1-9", "Switch workspace", HelpCategory.WORKSPACE, AppMode.NORMAL),
            HelpEntry("Ctrl+B Shift+1-9", "Move pane to workspace", HelpCategory.WORKSPACE, AppMode.NORMAL),
            HelpEntry("Ctrl+B n", "New workspace", HelpCategory.WORKSPACE, AppMode.NORMAL),
            HelpEntry("Ctrl+B x", "Close workspace", HelpCategory.WORKSPACE, AppMode.NORMAL),
        ])

        # Phase 3: BSP Layout
        self.entries.extend([
            HelpEntry("Ctrl+B h", "Split horizontal", HelpCategory.LAYOUT, AppMode.COMMAND),
            HelpEntry("Ctrl+B v", "Split vertical", HelpCategory.LAYOUT, AppMode.COMMAND),
            HelpEntry("Ctrl+B r", "Rotate layout", HelpCategory.LAYOUT, AppMode.COMMAND),
            HelpEntry("Ctrl+B =", "Balance layout", HelpCategory.LAYOUT, AppMode.COMMAND),
            HelpEntry("Ctrl+B [", "Decrease ratio", HelpCategory.LAYOUT, AppMode.COMMAND),
            HelpEntry("Ctrl+B ]", "Increase ratio", HelpCategory.LAYOUT, AppMode.COMMAND),
            HelpEntry("h/j/k/l", "Navigate panes", HelpCategory.NAVIGATION, AppMode.NORMAL),
        ])

        # Phase 4: Streaming
        self.entries.extend([
            HelpEntry("Ctrl+B p", "Pause/resume stream", HelpCategory.SYSTEM, AppMode.NORMAL),
        ])

        # Phase 5: Help System
        self.entries.extend([
            HelpEntry("?", "Toggle help overlay", HelpCategory.SYSTEM, AppMode.NORMAL),
            HelpEntry("Tab", "Next category", HelpCategory.NAVIGATION),
            HelpEntry("j/k", "Scroll help", HelpCategory.NAVIGATION),
        ])

        # COPY mode navigation
        self.entries.extend([
            HelpEntry("j/k", "Move cursor down/up", HelpCategory.NAVIGATION, AppMode.COPY),
            HelpEntry("h/l", "Move cursor left/right", HelpCategory.NAVIGATION, AppMode.COPY),
            HelpEntry("w/b", "Word forward/backward", HelpCategory.NAVIGATION, AppMode.COPY),
            HelpEntry("0/$", "Line start/end", HelpCategory.NAVIGATION, AppMode.COPY),
            HelpEntry("g/G", "Top/bottom", HelpCategory.NAVIGATION, AppMode.COPY),
            HelpEntry("/", "Search forward", HelpCategory.NAVIGATION, AppMode.COPY),
            HelpEntry("?", "Search backward", HelpCategory.NAVIGATION, AppMode.COPY),
            HelpEntry("n/N", "Next/previous match", HelpCategory.NAVIGATION, AppMode.COPY),
            HelpEntry("y", "Yank (copy) selection", HelpCategory.CLIPBOARD, AppMode.COPY),
        ])

        # Additional commands
        self.entries.extend([
            HelpEntry("q", "Quit application", HelpCategory.SYSTEM, AppMode.NORMAL),
            HelpEntry("Ctrl+B r", "Rename pane", HelpCategory.EDITING, AppMode.NORMAL),
        ])

    def show(self):
        """Show the help overlay."""
        self.visible = True

    def hide(self):
        """Hide the help overlay."""
        self.visible = False

    def toggle(self):
        """Toggle help overlay visibility."""
        self.visible = not self.visible

    def filter_by_mode(self, mode: Optional[AppMode] = None) -> List[HelpEntry]:
        """
        Filter entries by mode.

        Args:
            mode: Mode to filter by (None = all modes)

        Returns:
            List of filtered entries
        """
        if mode is None:
            return self.entries
        return [e for e in self.entries if e.mode == mode or e.mode is None]

    def filter_by_category(self, category: Optional[HelpCategory] = None) -> List[HelpEntry]:
        """
        Filter entries by category.

        Args:
            category: Category to filter by (None = all categories)

        Returns:
            List of filtered entries
        """
        if category is None:
            return self.entries
        return [e for e in self.entries if e.category == category]

    def filter(
        self,
        mode: Optional[AppMode] = None,
        category: Optional[HelpCategory] = None
    ) -> List[HelpEntry]:
        """
        Filter entries by mode and/or category.

        Args:
            mode: Mode to filter by
            category: Category to filter by

        Returns:
            List of filtered entries
        """
        results = self.entries
        if mode:
            results = [e for e in results if e.mode == mode or e.mode is None]
        if category:
            results = [e for e in results if e.category == category]
        return results

    def render_table(self, entries: Optional[List[HelpEntry]] = None) -> str:
        """
        Render entries as a formatted table.

        Args:
            entries: Entries to render (None = all)

        Returns:
            Formatted table string
        """
        if entries is None:
            entries = self.entries

        if not entries:
            return "No help entries found."

        # Calculate column widths
        max_key = max(len(e.key) for e in entries)
        max_action = max(len(e.action) for e in entries)

        # Build table
        lines = []
        lines.append(f"{'Key':<{max_key}} | {'Action':<{max_action}} | Category")
        lines.append("-" * (max_key + max_action + 25))

        for entry in entries:
            category_name = entry.category.value
            lines.append(
                f"{entry.key:<{max_key}} | {entry.action:<{max_action}} | {category_name}"
            )

        return "\n".join(lines)

    def scroll_down(self):
        """Scroll help content down."""
        self.scroll_position += 1

    def scroll_up(self):
        """Scroll help content up."""
        self.scroll_position = max(0, self.scroll_position - 1)

    def next_category(self):
        """Switch to next category."""
        categories = list(HelpCategory)
        if self.current_category_filter is None:
            self.current_category_filter = categories[0]
        else:
            idx = categories.index(self.current_category_filter)
            self.current_category_filter = categories[(idx + 1) % len(categories)]


class ShortcutReference:
    """Generates reference documentation for keyboard shortcuts."""

    def __init__(self, entries: List[HelpEntry]):
        """
        Initialize shortcut reference.

        Args:
            entries: List of help entries
        """
        self.entries = entries

    def generate_markdown_cheatsheet(self) -> str:
        """
        Generate complete markdown cheat sheet.

        Returns:
            Markdown-formatted cheat sheet
        """
        lines = ["# Keyboard Shortcuts Cheat Sheet\n"]

        # Group by mode
        for mode in [None] + list(AppMode):
            mode_entries = [e for e in self.entries if e.mode == mode]
            if not mode_entries:
                continue

            mode_name = mode.name if mode else "Global"
            lines.append(f"\n## {mode_name} Mode\n")

            # Group by category
            for category in HelpCategory:
                cat_entries = [e for e in mode_entries if e.category == category]
                if not cat_entries:
                    continue

                lines.append(f"\n### {category.value.title()}\n")
                for entry in cat_entries:
                    lines.append(f"- **{entry.key}**: {entry.action}")
                    if entry.example:
                        lines.append(f"  - Example: {entry.example}")

        return "\n".join(lines)

    def generate_quick_reference(self, mode: Optional[AppMode] = None) -> str:
        """
        Generate quick reference for a specific mode.

        Args:
            mode: Mode to generate reference for (None = all)

        Returns:
            Quick reference string
        """
        entries = self.entries if mode is None else [
            e for e in self.entries if e.mode == mode or e.mode is None
        ]

        lines = []
        mode_name = mode.name if mode else "All Modes"
        lines.append(f"=== Quick Reference: {mode_name} ===\n")

        for entry in entries:
            lines.append(f"{entry.key:20} {entry.action}")

        return "\n".join(lines)

    def export_to_markdown(self, filepath: str):
        """
        Export cheat sheet to markdown file.

        Args:
            filepath: Output file path
        """
        content = self.generate_markdown_cheatsheet()
        with open(filepath, 'w') as f:
            f.write(content)

    def search_by_key(self, key: str) -> List[HelpEntry]:
        """
        Search entries by key pattern.

        Args:
            key: Key pattern to search for

        Returns:
            Matching entries
        """
        key_lower = key.lower()
        return [e for e in self.entries if key_lower in e.key.lower()]

    def search_by_action(self, action: str) -> List[HelpEntry]:
        """
        Search entries by action text.

        Args:
            action: Action text to search for

        Returns:
            Matching entries
        """
        action_lower = action.lower()
        return [e for e in self.entries if action_lower in e.action.lower()]

    def get_mode_shortcuts(self, mode: AppMode) -> List[HelpEntry]:
        """
        Get all shortcuts for a specific mode.

        Args:
            mode: Mode to get shortcuts for

        Returns:
            List of shortcuts
        """
        return [e for e in self.entries if e.mode == mode or e.mode is None]


class FooterHints:
    """Footer hints widget showing contextual keyboard shortcuts."""

    def __init__(self):
        """Initialize footer hints."""
        self.visible = True
        self.current_mode = AppMode.NORMAL
        self.hints = {
            AppMode.NORMAL: [
                "i:INSERT", "v:COPY", "?:Help", "q:Quit"
            ],
            AppMode.INSERT: [
                "Esc:NORMAL"
            ],
            AppMode.COPY: [
                "y:Yank", "Esc:Exit", "?:Search"
            ],
            AppMode.COMMAND: [
                "Enter:Execute", "Esc:Cancel"
            ]
        }

    def get_hints(self, mode: Optional[AppMode] = None) -> List[str]:
        """
        Get hints for a mode.

        Args:
            mode: Mode to get hints for (None = current mode)

        Returns:
            List of hint strings
        """
        target_mode = mode or self.current_mode
        return self.hints.get(target_mode, [])

    def set_mode(self, mode: AppMode):
        """
        Update current mode.

        Args:
            mode: New mode
        """
        self.current_mode = mode

    def show(self):
        """Show footer hints."""
        self.visible = True

    def hide(self):
        """Hide footer hints."""
        self.visible = False


# =============================================================================
# Test Class 1: HelpCategory Tests (~3 tests)
# =============================================================================

class TestHelpCategory:
    """Test HelpCategory enum."""

    def test_category_values(self):
        """Test that all expected categories exist."""
        expected_categories = {
            "NAVIGATION", "EDITING", "LAYOUT", "WORKSPACE",
            "CLIPBOARD", "COMMAND", "SYSTEM"
        }
        actual_categories = {cat.name for cat in HelpCategory}
        assert actual_categories == expected_categories, \
            f"Expected {expected_categories}, got {actual_categories}"

    def test_category_count(self):
        """Test that we have exactly 7 categories."""
        assert len(HelpCategory) == 7, \
            f"Expected 7 categories, got {len(HelpCategory)}"

    def test_category_names(self):
        """Test category value names."""
        assert HelpCategory.NAVIGATION.value == "navigation"
        assert HelpCategory.EDITING.value == "editing"
        assert HelpCategory.LAYOUT.value == "layout"
        assert HelpCategory.WORKSPACE.value == "workspace"
        assert HelpCategory.CLIPBOARD.value == "clipboard"
        assert HelpCategory.COMMAND.value == "command"
        assert HelpCategory.SYSTEM.value == "system"


# =============================================================================
# Test Class 2: HelpEntry Tests (~5 tests)
# =============================================================================

class TestHelpEntry:
    """Test HelpEntry class."""

    def test_entry_creation_all_fields(self):
        """Test creating entry with all fields."""
        entry = HelpEntry(
            key="Ctrl+B h",
            action="Split horizontal",
            category=HelpCategory.LAYOUT,
            mode=AppMode.COMMAND,
            example="Ctrl+B h to split current pane horizontally",
            description="Splits the current pane into two horizontal sections"
        )

        assert entry.key == "Ctrl+B h"
        assert entry.action == "Split horizontal"
        assert entry.category == HelpCategory.LAYOUT
        assert entry.mode == AppMode.COMMAND
        assert entry.example == "Ctrl+B h to split current pane horizontally"
        assert entry.description == "Splits the current pane into two horizontal sections"

    def test_entry_creation_minimal(self):
        """Test creating entry with required fields only."""
        entry = HelpEntry(
            key="i",
            action="Enter INSERT mode",
            category=HelpCategory.EDITING
        )

        assert entry.key == "i"
        assert entry.action == "Enter INSERT mode"
        assert entry.category == HelpCategory.EDITING
        assert entry.mode is None
        assert entry.example is None
        assert entry.description is None

    def test_entry_validation_empty_key(self):
        """Test that empty key raises ValueError."""
        with pytest.raises(ValueError, match="Key cannot be empty"):
            HelpEntry(
                key="",
                action="Test action",
                category=HelpCategory.NAVIGATION
            )

    def test_entry_validation_empty_action(self):
        """Test that empty action raises ValueError."""
        with pytest.raises(ValueError, match="Action cannot be empty"):
            HelpEntry(
                key="x",
                action="",
                category=HelpCategory.NAVIGATION
            )

    def test_entry_comparison(self):
        """Test entry equality comparison."""
        entry1 = HelpEntry("x", "Close", HelpCategory.SYSTEM, AppMode.NORMAL)
        entry2 = HelpEntry("x", "Close", HelpCategory.SYSTEM, AppMode.NORMAL)
        entry3 = HelpEntry("y", "Yank", HelpCategory.CLIPBOARD, AppMode.COPY)

        assert entry1 == entry2
        assert entry1 != entry3
        assert entry1 != "not an entry"


# =============================================================================
# Test Class 3: HelpOverlay Tests (~12 tests)
# =============================================================================

class TestHelpOverlay:
    """Test HelpOverlay widget."""

    def test_overlay_initialization(self):
        """Test overlay initializes correctly."""
        overlay = HelpOverlay()

        assert not overlay.visible
        assert overlay.current_mode_filter is None
        assert overlay.current_category_filter is None
        assert len(overlay.entries) > 0
        assert overlay.scroll_position == 0

    def test_filter_by_normal_mode(self):
        """Test filtering entries by NORMAL mode."""
        overlay = HelpOverlay()
        normal_entries = overlay.filter_by_mode(AppMode.NORMAL)

        assert len(normal_entries) > 0
        for entry in normal_entries:
            assert entry.mode == AppMode.NORMAL or entry.mode is None

    def test_filter_by_insert_mode(self):
        """Test filtering entries by INSERT mode."""
        overlay = HelpOverlay()
        insert_entries = overlay.filter_by_mode(AppMode.INSERT)

        assert len(insert_entries) > 0
        # Should include at least "Esc" to return to NORMAL
        esc_entries = [e for e in insert_entries if "Esc" in e.key]
        assert len(esc_entries) > 0

    def test_filter_by_copy_mode(self):
        """Test filtering entries by COPY mode."""
        overlay = HelpOverlay()
        copy_entries = overlay.filter_by_mode(AppMode.COPY)

        assert len(copy_entries) > 0
        # Should include navigation keys
        nav_keys = ["j/k", "h/l", "w/b", "0/$", "g/G"]
        found_keys = [e.key for e in copy_entries if e.key in nav_keys]
        assert len(found_keys) > 0

    def test_filter_by_command_mode(self):
        """Test filtering entries by COMMAND mode."""
        overlay = HelpOverlay()
        command_entries = overlay.filter_by_mode(AppMode.COMMAND)

        assert len(command_entries) > 0
        # Should include layout commands
        layout_entries = [e for e in command_entries if e.category == HelpCategory.LAYOUT]
        assert len(layout_entries) > 0

    def test_filter_by_category(self):
        """Test filtering entries by category."""
        overlay = HelpOverlay()
        nav_entries = overlay.filter_by_category(HelpCategory.NAVIGATION)

        assert len(nav_entries) > 0
        for entry in nav_entries:
            assert entry.category == HelpCategory.NAVIGATION

    def test_filter_combined(self):
        """Test filtering by both mode and category."""
        overlay = HelpOverlay()
        results = overlay.filter(
            mode=AppMode.COPY,
            category=HelpCategory.NAVIGATION
        )

        assert len(results) > 0
        for entry in results:
            assert entry.mode == AppMode.COPY or entry.mode is None
            assert entry.category == HelpCategory.NAVIGATION

    def test_render_help_table(self):
        """Test rendering help entries as table."""
        overlay = HelpOverlay()
        table = overlay.render_table(overlay.entries[:5])

        assert "Key" in table
        assert "Action" in table
        assert "Category" in table
        assert "-" in table  # Header separator

    def test_navigation_scroll_down(self):
        """Test scrolling down in help."""
        overlay = HelpOverlay()
        assert overlay.scroll_position == 0

        overlay.scroll_down()
        assert overlay.scroll_position == 1

        overlay.scroll_down()
        assert overlay.scroll_position == 2

    def test_navigation_scroll_up(self):
        """Test scrolling up in help."""
        overlay = HelpOverlay()
        overlay.scroll_position = 5

        overlay.scroll_up()
        assert overlay.scroll_position == 4

        overlay.scroll_up()
        assert overlay.scroll_position == 3

        # Should not go below 0
        overlay.scroll_position = 0
        overlay.scroll_up()
        assert overlay.scroll_position == 0

    def test_toggle_visibility(self):
        """Test toggling help overlay visibility."""
        overlay = HelpOverlay()
        assert not overlay.visible

        overlay.toggle()
        assert overlay.visible

        overlay.toggle()
        assert not overlay.visible

    def test_category_navigation(self):
        """Test navigating between categories."""
        overlay = HelpOverlay()
        assert overlay.current_category_filter is None

        overlay.next_category()
        assert overlay.current_category_filter == HelpCategory.NAVIGATION

        overlay.next_category()
        assert overlay.current_category_filter == HelpCategory.EDITING

        # Should wrap around
        for _ in range(10):
            overlay.next_category()
        assert overlay.current_category_filter in HelpCategory

    def test_all_phase_keybindings_present(self):
        """Test that keybindings from all phases are documented."""
        overlay = HelpOverlay()
        all_keys = [e.key for e in overlay.entries]

        # Phase 1: Modal System
        assert any("i" == k for k in all_keys), "Missing 'i' for INSERT mode"
        assert any("v" == k for k in all_keys), "Missing 'v' for COPY mode"
        assert any(":" == k for k in all_keys), "Missing ':' for COMMAND mode"

        # Phase 2: Workspace Management
        assert any("Ctrl+B 1-9" in k for k in all_keys), "Missing workspace switch"
        assert any("Ctrl+B n" in k for k in all_keys), "Missing new workspace"

        # Phase 3: BSP Layout
        assert any("Ctrl+B h" in k for k in all_keys), "Missing horizontal split"
        assert any("Ctrl+B v" in k for k in all_keys), "Missing vertical split"
        assert any("h/j/k/l" in k for k in all_keys), "Missing pane navigation"

        # Phase 4: Streaming
        assert any("Ctrl+B p" in k for k in all_keys), "Missing pause/resume"

        # Phase 5: Help System
        assert any("?" in k for k in all_keys), "Missing help toggle"


# =============================================================================
# Test Class 4: ShortcutReference Tests (~8 tests)
# =============================================================================

class TestShortcutReference:
    """Test ShortcutReference class."""

    def test_reference_initialization(self):
        """Test reference initializes with entries."""
        overlay = HelpOverlay()
        reference = ShortcutReference(overlay.entries)

        assert len(reference.entries) > 0
        assert reference.entries == overlay.entries

    def test_generate_markdown_cheatsheet(self):
        """Test generating markdown cheat sheet."""
        entries = [
            HelpEntry("i", "Insert mode", HelpCategory.EDITING, AppMode.NORMAL),
            HelpEntry("v", "Copy mode", HelpCategory.CLIPBOARD, AppMode.NORMAL),
        ]
        reference = ShortcutReference(entries)
        markdown = reference.generate_markdown_cheatsheet()

        assert "# Keyboard Shortcuts Cheat Sheet" in markdown
        assert "NORMAL Mode" in markdown
        assert "**i**" in markdown
        assert "**v**" in markdown

    def test_generate_quick_reference(self):
        """Test generating quick reference."""
        entries = [
            HelpEntry("i", "Insert mode", HelpCategory.EDITING, AppMode.NORMAL),
            HelpEntry("v", "Copy mode", HelpCategory.CLIPBOARD, AppMode.NORMAL),
        ]
        reference = ShortcutReference(entries)
        quick_ref = reference.generate_quick_reference(AppMode.NORMAL)

        assert "Quick Reference" in quick_ref
        assert "NORMAL" in quick_ref
        assert "i" in quick_ref
        assert "v" in quick_ref

    def test_export_to_markdown_file(self):
        """Test exporting cheat sheet to file."""
        entries = [
            HelpEntry("i", "Insert mode", HelpCategory.EDITING, AppMode.NORMAL),
        ]
        reference = ShortcutReference(entries)

        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.md') as f:
            temp_path = f.name

        try:
            reference.export_to_markdown(temp_path)
            assert os.path.exists(temp_path)

            with open(temp_path, 'r') as f:
                content = f.read()

            assert "# Keyboard Shortcuts Cheat Sheet" in content
            assert "**i**" in content
        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)

    def test_search_by_key(self):
        """Test searching entries by key."""
        entries = [
            HelpEntry("Ctrl+B h", "Split horizontal", HelpCategory.LAYOUT),
            HelpEntry("Ctrl+B v", "Split vertical", HelpCategory.LAYOUT),
            HelpEntry("i", "Insert mode", HelpCategory.EDITING),
        ]
        reference = ShortcutReference(entries)

        results = reference.search_by_key("Ctrl+B")
        assert len(results) == 2
        assert all("Ctrl+B" in r.key for r in results)

        results = reference.search_by_key("h")
        assert len(results) >= 1

    def test_search_by_action(self):
        """Test searching entries by action text."""
        entries = [
            HelpEntry("Ctrl+B h", "Split horizontal", HelpCategory.LAYOUT),
            HelpEntry("Ctrl+B v", "Split vertical", HelpCategory.LAYOUT),
            HelpEntry("i", "Insert mode", HelpCategory.EDITING),
        ]
        reference = ShortcutReference(entries)

        results = reference.search_by_action("split")
        assert len(results) == 2
        assert all("split" in r.action.lower() for r in results)

        results = reference.search_by_action("mode")
        assert len(results) >= 1

    def test_get_mode_shortcuts(self):
        """Test getting shortcuts for specific mode."""
        entries = [
            HelpEntry("i", "Insert mode", HelpCategory.EDITING, AppMode.NORMAL),
            HelpEntry("Esc", "Exit mode", HelpCategory.NAVIGATION, AppMode.INSERT),
            HelpEntry("?", "Help", HelpCategory.SYSTEM, None),
        ]
        reference = ShortcutReference(entries)

        normal_shortcuts = reference.get_mode_shortcuts(AppMode.NORMAL)
        assert len(normal_shortcuts) == 2  # 'i' and '?' (global)

        insert_shortcuts = reference.get_mode_shortcuts(AppMode.INSERT)
        assert len(insert_shortcuts) == 2  # 'Esc' and '?' (global)

    def test_markdown_format_validation(self):
        """Test that markdown output has valid format."""
        overlay = HelpOverlay()
        reference = ShortcutReference(overlay.entries)
        markdown = reference.generate_markdown_cheatsheet()

        # Should have proper markdown headers
        assert markdown.count("# ") >= 1  # Main header
        assert markdown.count("## ") >= 1  # Mode headers
        assert markdown.count("### ") >= 1  # Category headers

        # Should have bold formatting for keys
        assert "**" in markdown


# =============================================================================
# Test Class 5: FooterHints Tests (~6 tests)
# =============================================================================

class TestFooterHints:
    """Test FooterHints widget."""

    def test_footer_initialization(self):
        """Test footer hints initializes correctly."""
        footer = FooterHints()

        assert footer.visible
        assert footer.current_mode == AppMode.NORMAL
        assert len(footer.hints) == 4  # One for each mode

    def test_get_hints_normal_mode(self):
        """Test getting hints for NORMAL mode."""
        footer = FooterHints()
        hints = footer.get_hints(AppMode.NORMAL)

        assert len(hints) > 0
        assert any("INSERT" in h for h in hints)
        assert any("COPY" in h for h in hints)
        assert any("Help" in h for h in hints)

    def test_get_hints_insert_mode(self):
        """Test getting hints for INSERT mode."""
        footer = FooterHints()
        hints = footer.get_hints(AppMode.INSERT)

        assert len(hints) > 0
        assert any("NORMAL" in h for h in hints)

    def test_get_hints_copy_mode(self):
        """Test getting hints for COPY mode."""
        footer = FooterHints()
        hints = footer.get_hints(AppMode.COPY)

        assert len(hints) > 0
        assert any("Yank" in h or "y:" in h for h in hints)

    def test_get_hints_command_mode(self):
        """Test getting hints for COMMAND mode."""
        footer = FooterHints()
        hints = footer.get_hints(AppMode.COMMAND)

        assert len(hints) > 0
        assert any("Execute" in h or "Enter" in h for h in hints)
        assert any("Cancel" in h or "Esc" in h for h in hints)

    def test_mode_change_updates(self):
        """Test that mode changes update current mode."""
        footer = FooterHints()
        assert footer.current_mode == AppMode.NORMAL

        footer.set_mode(AppMode.INSERT)
        assert footer.current_mode == AppMode.INSERT

        footer.set_mode(AppMode.COPY)
        assert footer.current_mode == AppMode.COPY

        # get_hints with no args should use current mode
        hints = footer.get_hints()
        copy_hints = footer.get_hints(AppMode.COPY)
        assert hints == copy_hints


# =============================================================================
# Test Class 6: App Integration Tests (~8 tests)
# =============================================================================

class TestAppIntegration:
    """Test help system integration with app."""

    def test_help_overlay_creation(self):
        """Test that help overlay can be created."""
        overlay = HelpOverlay()
        assert overlay is not None
        assert len(overlay.entries) > 0

    def test_show_help_action(self):
        """Test triggering show help action."""
        overlay = HelpOverlay()
        assert not overlay.visible

        # Simulate pressing '?'
        overlay.show()
        assert overlay.visible

    def test_help_overlay_push_pop(self):
        """Test help overlay can be shown and hidden."""
        overlay = HelpOverlay()

        overlay.show()
        assert overlay.visible

        overlay.hide()
        assert not overlay.visible

    def test_help_overlay_mode_awareness(self):
        """Test help overlay shows mode-specific help."""
        overlay = HelpOverlay()

        # NORMAL mode shortcuts
        normal_entries = overlay.filter_by_mode(AppMode.NORMAL)
        assert len(normal_entries) > 0

        # COPY mode shortcuts
        copy_entries = overlay.filter_by_mode(AppMode.COPY)
        assert len(copy_entries) > 0

        # Should be different
        normal_keys = {e.key for e in normal_entries}
        copy_keys = {e.key for e in copy_entries}
        assert normal_keys != copy_keys

    def test_footer_hints_visibility(self):
        """Test footer hints visibility control."""
        footer = FooterHints()
        assert footer.visible

        footer.hide()
        assert not footer.visible

        footer.show()
        assert footer.visible

    def test_footer_hints_updates(self):
        """Test footer hints update with mode changes."""
        footer = FooterHints()

        normal_hints = footer.get_hints(AppMode.NORMAL)
        insert_hints = footer.get_hints(AppMode.INSERT)

        # Hints should be different for different modes
        assert normal_hints != insert_hints

    def test_contextual_tips_empty_workspace(self):
        """Test contextual tip for empty workspace."""
        # This would show "Press 'n' to create new terminal"
        overlay = HelpOverlay()
        new_terminal_entries = [
            e for e in overlay.entries
            if "workspace" in e.action.lower() or "new" in e.action.lower()
        ]
        assert len(new_terminal_entries) > 0

    def test_contextual_tips_single_pane(self):
        """Test contextual tip for single pane."""
        # This would show "Press Ctrl+B h/v to split"
        overlay = HelpOverlay()
        split_entries = [
            e for e in overlay.entries
            if "split" in e.action.lower()
        ]
        assert len(split_entries) > 0


# =============================================================================
# Test Class 7: Documentation Tests (~5 tests)
# =============================================================================

class TestDocumentation:
    """Test documentation completeness and validation."""

    def test_all_phases_keybindings_documented(self):
        """Test that keybindings from all phases 1-4 are documented."""
        overlay = HelpOverlay()
        all_actions = [e.action.lower() for e in overlay.entries]

        # Phase 1: Modal System
        assert any("insert" in a for a in all_actions)
        assert any("copy" in a for a in all_actions)
        assert any("command" in a for a in all_actions)

        # Phase 2: Workspace Management
        assert any("workspace" in a for a in all_actions)

        # Phase 3: BSP Layout
        assert any("split" in a for a in all_actions)
        assert any("navigate" in a or "pane" in a for a in all_actions)

        # Phase 4: Streaming
        assert any("pause" in a or "stream" in a for a in all_actions)

    def test_markdown_export_completeness(self):
        """Test markdown export includes all entries."""
        overlay = HelpOverlay()
        reference = ShortcutReference(overlay.entries)
        markdown = reference.generate_markdown_cheatsheet()

        # Check that all modes are represented
        assert "NORMAL" in markdown
        assert "INSERT" in markdown
        assert "COPY" in markdown
        assert "COMMAND" in markdown

        # Check that all categories are represented
        for category in HelpCategory:
            assert category.value.title() in markdown

    def test_quick_reference_completeness(self):
        """Test quick reference includes essential shortcuts."""
        overlay = HelpOverlay()
        reference = ShortcutReference(overlay.entries)

        for mode in AppMode:
            quick_ref = reference.generate_quick_reference(mode)
            assert mode.name in quick_ref
            assert len(quick_ref) > 0

    def test_search_functionality_accuracy(self):
        """Test that search returns accurate results."""
        overlay = HelpOverlay()
        reference = ShortcutReference(overlay.entries)

        # Search by key
        ctrl_b_results = reference.search_by_key("Ctrl+B")
        assert len(ctrl_b_results) > 0
        assert all("Ctrl+B" in r.key for r in ctrl_b_results)

        # Search by action
        split_results = reference.search_by_action("split")
        assert len(split_results) > 0
        assert all("split" in r.action.lower() for r in split_results)

    def test_keybinding_coverage_validation(self):
        """Test that all essential keybindings are covered."""
        overlay = HelpOverlay()
        all_keys = [e.key for e in overlay.entries]

        # Essential navigation
        assert any("h/j/k/l" in k or "hjkl" in k for k in all_keys)

        # Essential actions
        essential_keys = ["i", "v", ":", "Esc", "?", "q"]
        for key in essential_keys:
            assert any(key == k or key in k for k in all_keys), \
                f"Essential key '{key}' not documented"


# =============================================================================
# Main Test Runner
# =============================================================================

def run_all_tests():
    """Run all tests and generate report."""
    print("=" * 70)
    print("Phase 5 Help System - Comprehensive Test Suite")
    print("=" * 70)

    # Run pytest with detailed output
    exit_code = pytest.main([
        __file__,
        "-v",
        "--tb=short",
        "--color=yes",
        "-ra"
    ])

    return exit_code


if __name__ == "__main__":
    exit_code = run_all_tests()
    exit(exit_code)
