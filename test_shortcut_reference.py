#!/usr/bin/env python3
"""
Test script to demonstrate ShortcutReference capabilities.

This script shows all export formats and search functionality.
"""

from pathlib import Path
from claude_multi_terminal.help.shortcut_reference import (
    ShortcutReference,
    ShortcutCategory,
    generate_all_docs,
    print_quick_ref,
)


def main():
    """Run comprehensive tests of shortcut reference system."""
    print("=" * 80)
    print("Claude Multi-Terminal - Shortcut Reference System Test")
    print("=" * 80)
    print()

    # Initialize reference
    ref = ShortcutReference()
    print(f"✓ Loaded {len(ref.shortcuts)} keyboard shortcuts")
    print()

    # Test 1: Quick Reference (console output)
    print("TEST 1: Quick Reference Card (80x24 terminal format)")
    print("-" * 80)
    print_quick_ref()
    print()
    print()

    # Test 2: Mode-specific shortcuts
    print("TEST 2: Mode-Specific Shortcuts")
    print("-" * 80)
    for mode in ["NORMAL", "COMMAND", "COPY", "INSERT"]:
        shortcuts = ref.get_mode_shortcuts(mode)
        print(f"{mode} Mode: {len(shortcuts)} shortcuts")
    print()

    # Test 3: Search functionality
    print("TEST 3: Search Functionality")
    print("-" * 80)
    queries = ["split", "ctrl+b", "copy", "vim"]
    for query in queries:
        results = ref.search_shortcuts(query)
        print(f"Search '{query}': {len(results)} results")
        if results:
            for shortcut in results[:3]:  # Show top 3
                print(f"  - {shortcut.key}: {shortcut.action} ({shortcut.mode})")
    print()

    # Test 4: Category filtering
    print("TEST 4: Category Filtering")
    print("-" * 80)
    for category in ShortcutCategory:
        shortcuts = ref.get_category_shortcuts(category)
        print(f"{category.value}: {len(shortcuts)} shortcuts")
    print()

    # Test 5: Frequent shortcuts
    print("TEST 5: Most Frequently Used Shortcuts")
    print("-" * 80)
    frequent = ref.get_frequent_shortcuts(10)
    for i, shortcut in enumerate(frequent, 1):
        print(f"{i:2}. {shortcut.key:15} - {shortcut.action} ({shortcut.mode})")
    print()

    # Test 6: Export all formats
    print("TEST 6: Export Documentation")
    print("-" * 80)
    output_dir = Path.home() / ".multi-term"
    output_dir.mkdir(parents=True, exist_ok=True)

    # Markdown
    md_path = ref.export_to_markdown()
    print(f"✓ Markdown exported: {md_path}")
    print(f"  Size: {md_path.stat().st_size:,} bytes")

    # HTML
    html_path = ref.export_to_html()
    print(f"✓ HTML exported: {html_path}")
    print(f"  Size: {html_path.stat().st_size:,} bytes")

    # JSON
    json_path = ref.export_to_json()
    print(f"✓ JSON exported: {json_path}")
    print(f"  Size: {json_path.stat().st_size:,} bytes")
    print()

    # Test 7: Generate all docs at once
    print("TEST 7: Batch Export")
    print("-" * 80)
    all_docs = generate_all_docs()
    for format_name, filepath in all_docs.items():
        print(f"✓ {format_name.upper():10} -> {filepath}")
    print()

    # Summary
    print("=" * 80)
    print("All tests completed successfully!")
    print()
    print("Generated files:")
    print(f"  - Markdown: {md_path}")
    print(f"  - HTML:     {html_path}")
    print(f"  - JSON:     {json_path}")
    print()
    print("Open the HTML file in a browser to see searchable documentation!")
    print("=" * 80)


if __name__ == "__main__":
    main()
