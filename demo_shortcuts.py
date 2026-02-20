#!/usr/bin/env python3
"""
Standalone demo of shortcut reference system.
Does not require textual or other dependencies.
"""

import sys
import os

# Add parent to path without importing the main package
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import only the specific module
from claude_multi_terminal.help.shortcut_reference import (
    ShortcutReference,
    ShortcutCategory,
    print_quick_ref,
)


def main():
    print("╔" + "═" * 78 + "╗")
    print("║" + " " * 20 + "Claude Multi-Terminal - Shortcuts Demo" + " " * 19 + "║")
    print("╚" + "═" * 78 + "╝")
    print()

    # Create reference
    ref = ShortcutReference()
    print(f"📚 Loaded {len(ref.shortcuts)} keyboard shortcuts\n")

    # Demo 1: Quick Reference Card
    print("┌" + "─" * 78 + "┐")
    print("│" + " " * 25 + "QUICK REFERENCE CARD" + " " * 33 + "│")
    print("└" + "─" * 78 + "┘")
    print()
    print_quick_ref()
    print()

    # Demo 2: Search functionality
    print("┌" + "─" * 78 + "┐")
    print("│" + " " * 28 + "SEARCH EXAMPLES" + " " * 35 + "│")
    print("└" + "─" * 78 + "┘")
    print()

    searches = [
        ("split", "Find split-related commands"),
        ("ctrl+b", "All Ctrl+B commands"),
        ("workspace", "Workspace operations"),
        ("copy", "Copy mode commands"),
    ]

    for query, description in searches:
        results = ref.search_shortcuts(query)
        print(f"🔍 Search: '{query}' - {description}")
        print(f"   Found {len(results)} matches:")
        for i, result in enumerate(results[:4], 1):  # Show top 4
            print(f"   {i}. {result.key:20} → {result.action:35} [{result.mode}]")
        print()

    # Demo 3: Mode-specific shortcuts
    print("┌" + "─" * 78 + "┐")
    print("│" + " " * 25 + "SHORTCUTS BY MODE" + " " * 36 + "│")
    print("└" + "─" * 78 + "┘")
    print()

    for mode in ["NORMAL", "COMMAND", "COPY", "INSERT"]:
        shortcuts = ref.get_mode_shortcuts(mode)
        print(f"📍 {mode} Mode: {len(shortcuts)} shortcuts")

        # Show a few examples
        for shortcut in shortcuts[:3]:
            print(f"   • {shortcut.key:15} - {shortcut.action}")
        if len(shortcuts) > 3:
            print(f"   ... and {len(shortcuts) - 3} more")
        print()

    # Demo 4: Category breakdown
    print("┌" + "─" * 78 + "┐")
    print("│" + " " * 24 + "SHORTCUTS BY CATEGORY" + " " * 33 + "│")
    print("└" + "─" * 78 + "┘")
    print()

    for category in ShortcutCategory:
        shortcuts = ref.get_category_shortcuts(category)
        if shortcuts:
            print(f"📂 {category.value:25} {len(shortcuts):2} shortcuts")

    print()

    # Demo 5: Most frequent shortcuts
    print("┌" + "─" * 78 + "┐")
    print("│" + " " * 22 + "TOP 10 MOST USED SHORTCUTS" + " " * 30 + "│")
    print("└" + "─" * 78 + "┘")
    print()

    frequent = ref.get_frequent_shortcuts(10)
    for i, shortcut in enumerate(frequent, 1):
        mode_emoji = {
            "NORMAL": "🟦",
            "COMMAND": "🟧",
            "COPY": "🟨",
            "INSERT": "🟩",
        }.get(shortcut.mode, "⬜")

        print(f"{i:2}. {mode_emoji} {shortcut.key:15} → {shortcut.action:30} [{shortcut.mode}]")

    print()

    # Demo 6: Export capabilities
    print("┌" + "─" * 78 + "┐")
    print("│" + " " * 26 + "EXPORT FORMATS" + " " * 38 + "│")
    print("└" + "─" * 78 + "┘")
    print()

    print("📄 Available export formats:")
    print("   • Markdown (.md)  - Full cheat sheet with tables")
    print("   • HTML (.html)    - Interactive searchable reference")
    print("   • JSON (.json)    - Machine-readable data")
    print()

    # Show markdown sample
    print("📝 Markdown sample (first 500 chars):")
    print("─" * 80)
    md_content = ref.generate_cheat_sheet()
    print(md_content[:500] + "...")
    print("─" * 80)
    print()

    # Summary
    print("╔" + "═" * 78 + "╗")
    print("║" + " " * 33 + "SUMMARY" + " " * 39 + "║")
    print("╚" + "═" * 78 + "╝")
    print()
    print(f"✅ Total Shortcuts:      {len(ref.shortcuts)}")
    print(f"✅ Modes:                4 (NORMAL, COMMAND, COPY, INSERT)")
    print(f"✅ Categories:           {len(ShortcutCategory)}")
    print(f"✅ Frequent Shortcuts:   {len([s for s in ref.shortcuts if s.frequency == 'frequent'])}")
    print(f"✅ Export Formats:       3 (Markdown, HTML, JSON)")
    print()
    print("💡 Use ShortcutReference class to generate documentation programmatically!")
    print("💡 Call export_to_markdown(), export_to_html(), or export_to_json()")
    print()


if __name__ == "__main__":
    main()
