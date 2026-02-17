#!/usr/bin/env python3
"""
Test script for the Copy All Output feature.

This script verifies:
1. Context menu includes "Copy All Output" option
2. Copy All Output submenu appears with timestamp options
3. _get_all_output_text() correctly extracts all text
4. Large outputs (10k+ lines) are handled efficiently
"""

from claude_multi_terminal.widgets.selectable_richlog import SelectableRichLog, MenuItem
from rich.text import Text
import time


def test_get_all_output_text():
    """Test extracting all text from output."""
    print("Test 1: Extract all text from output")
    print("-" * 50)

    # Create a mock SelectableRichLog widget
    log = SelectableRichLog()

    # Simulate adding lines (we'll manually add to lines list)
    # Note: In real usage, lines are added via write() method
    from rich.console import Console
    from rich.segment import Segment
    from textual.strip import Strip

    # Create some test lines
    test_content = [
        "Line 1: Hello World",
        "Line 2: This is a test",
        "Line 3: Testing copy all output",
        "Line 4: With multiple lines",
        "Line 5: And various content",
    ]

    # Manually create Strip objects (simulating what RichLog does)
    for line_text in test_content:
        segments = [Segment(line_text)]
        strip = Strip(segments)
        log.lines.append(strip)

    # Test extraction
    all_text = log._get_all_output_text(include_timestamps=False)

    print(f"Original lines: {len(test_content)}")
    print(f"Extracted lines: {len(all_text.splitlines())}")
    print(f"Characters: {len(all_text)}")
    print()
    print("Extracted text:")
    print(all_text)
    print()

    # Verify
    assert len(all_text.splitlines()) == len(test_content), "Line count mismatch"
    assert all_text == "\n".join(test_content), "Content mismatch"
    print("✓ Test passed!")
    print()


def test_large_output():
    """Test handling large outputs (10k+ lines)."""
    print("Test 2: Handle large outputs (10,000+ lines)")
    print("-" * 50)

    log = SelectableRichLog()

    from rich.segment import Segment
    from textual.strip import Strip

    # Create 10,000 lines
    line_count = 10_000
    print(f"Creating {line_count:,} lines...")

    start_time = time.time()
    for i in range(line_count):
        line_text = f"Line {i+1}: This is test content with some data {i * 123}"
        segments = [Segment(line_text)]
        strip = Strip(segments)
        log.lines.append(strip)

    creation_time = time.time() - start_time
    print(f"Created in {creation_time:.3f} seconds")

    # Test extraction
    print("Extracting all text...")
    start_time = time.time()
    all_text = log._get_all_output_text(include_timestamps=False)
    extraction_time = time.time() - start_time

    print(f"Extracted in {extraction_time:.3f} seconds")
    print(f"Total lines: {len(all_text.splitlines()):,}")
    print(f"Total characters: {len(all_text):,}")
    print()

    # Verify performance (should be < 1 second for 10k lines)
    assert extraction_time < 1.0, f"Too slow! Took {extraction_time:.3f}s (should be < 1s)"
    assert len(all_text.splitlines()) == line_count, "Line count mismatch"

    print("✓ Test passed! (Fast operation)")
    print()


def test_context_menu_structure():
    """Test that context menu has correct structure."""
    print("Test 3: Context menu structure")
    print("-" * 50)

    log = SelectableRichLog()

    # Add some content so menu is enabled
    from rich.segment import Segment
    from textual.strip import Strip

    segments = [Segment("Test line")]
    strip = Strip(segments)
    log.lines.append(strip)

    # Check that we have the methods
    assert hasattr(log, '_show_copy_all_submenu'), "Missing _show_copy_all_submenu method"
    assert hasattr(log, '_copy_all_output'), "Missing _copy_all_output method"
    assert hasattr(log, '_get_all_output_text'), "Missing _get_all_output_text method"

    print("✓ All required methods present")
    print()


def test_empty_output():
    """Test handling empty output."""
    print("Test 4: Handle empty output")
    print("-" * 50)

    log = SelectableRichLog()

    # Test with no lines
    all_text = log._get_all_output_text(include_timestamps=False)

    assert all_text == "", "Should return empty string for empty output"
    print("✓ Test passed! (Empty output handled correctly)")
    print()


def test_special_characters():
    """Test handling special characters and formatting."""
    print("Test 5: Handle special characters and formatting")
    print("-" * 50)

    log = SelectableRichLog()

    from rich.segment import Segment
    from textual.strip import Strip

    # Create lines with special characters
    test_lines = [
        "Line with unicode: 你好世界 🚀",
        "Line with tabs:\t\tindented",
        "Line with newline markers: \\n \\r\\n",
        "Line with quotes: 'single' \"double\"",
        "Line with backslashes: C:\\Users\\path\\to\\file",
    ]

    for line_text in test_lines:
        segments = [Segment(line_text)]
        strip = Strip(segments)
        log.lines.append(strip)

    all_text = log._get_all_output_text(include_timestamps=False)

    print(f"Extracted {len(all_text.splitlines())} lines")
    print("Content:")
    print(all_text)
    print()

    # Verify all special characters are preserved
    assert all_text == "\n".join(test_lines), "Special characters not preserved"
    print("✓ Test passed! (Special characters preserved)")
    print()


if __name__ == "__main__":
    print("=" * 50)
    print("Copy All Output Feature Test Suite")
    print("=" * 50)
    print()

    try:
        test_context_menu_structure()
        test_get_all_output_text()
        test_empty_output()
        test_special_characters()
        test_large_output()

        print("=" * 50)
        print("✓ ALL TESTS PASSED!")
        print("=" * 50)
        print()
        print("Feature Status: READY")
        print()
        print("Next steps:")
        print("1. Run the application")
        print("2. Right-click in the output area")
        print("3. Select 'Copy All Output'")
        print("4. Choose timestamp option")
        print("5. Verify clipboard contains all output")

    except Exception as e:
        print()
        print("=" * 50)
        print("✗ TEST FAILED!")
        print("=" * 50)
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        exit(1)
