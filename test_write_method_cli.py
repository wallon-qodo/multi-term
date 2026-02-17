#!/usr/bin/env python3
"""Non-interactive test for SelectableRichLog.write() method signature."""

import sys
from textual.widgets import RichLog
from claude_multi_terminal.widgets.selectable_richlog import SelectableRichLog
from rich.text import Text


def test_write_signature():
    """Test that SelectableRichLog.write() matches RichLog.write() signature."""

    print("Testing SelectableRichLog.write() method signature...")
    print("="*60)

    # Create instances
    rich_log = RichLog()
    selectable_log = SelectableRichLog()

    # Get method signatures
    import inspect

    parent_sig = inspect.signature(RichLog.write)
    child_sig = inspect.signature(SelectableRichLog.write)

    print(f"\nParent RichLog.write signature:")
    print(f"  {parent_sig}")

    print(f"\nChild SelectableRichLog.write signature:")
    print(f"  {child_sig}")

    # Compare parameters
    parent_params = list(parent_sig.parameters.keys())
    child_params = list(child_sig.parameters.keys())

    print(f"\nParent parameters: {parent_params}")
    print(f"Child parameters:  {child_params}")

    # Check if signatures match
    if parent_params == child_params:
        print("\n✓ PASS: Method signatures match!")
        print("="*60)
        return True
    else:
        print("\n✗ FAIL: Method signatures do not match!")
        print(f"  Missing in child: {set(parent_params) - set(child_params)}")
        print(f"  Extra in child: {set(child_params) - set(parent_params)}")
        print("="*60)
        return False


def test_write_calls():
    """Test various write() call patterns."""

    print("\nTesting write() call patterns...")
    print("="*60)

    log = SelectableRichLog()

    tests_passed = 0
    tests_failed = 0

    try:
        # Test 1: Simple write
        log.write("Test 1")
        tests_passed += 1
        print("✓ Test 1: Simple write")
    except Exception as e:
        tests_failed += 1
        print(f"✗ Test 1 failed: {e}")

    try:
        # Test 2: Positional unpacking (mimics DeferredRender)
        args = ("Test 2", None, False, True, None)
        log.write(*args)
        tests_passed += 1
        print("✓ Test 2: Positional unpacking (5 args)")
    except Exception as e:
        tests_failed += 1
        print(f"✗ Test 2 failed: {e}")

    try:
        # Test 3: All keyword args
        log.write(
            content="Test 3",
            width=None,
            expand=False,
            shrink=True,
            scroll_end=None,
            animate=False
        )
        tests_passed += 1
        print("✓ Test 3: All keyword arguments")
    except Exception as e:
        tests_failed += 1
        print(f"✗ Test 3 failed: {e}")

    try:
        # Test 4: Mixed positional and keyword
        log.write("Test 4", width=50, animate=True)
        tests_passed += 1
        print("✓ Test 4: Mixed positional and keyword")
    except Exception as e:
        tests_failed += 1
        print(f"✗ Test 4 failed: {e}")

    print(f"\nTests passed: {tests_passed}/{tests_passed + tests_failed}")
    print("="*60)

    return tests_failed == 0


if __name__ == "__main__":
    sig_match = test_write_signature()
    calls_work = test_write_calls()

    if sig_match and calls_work:
        print("\n✓✓✓ ALL TESTS PASSED ✓✓✓")
        print("\nThe SelectableRichLog.write() method signature is correct.")
        print("The method can accept both positional and keyword arguments.")
        print("The TypeError has been successfully fixed!")
        sys.exit(0)
    else:
        print("\n✗✗✗ SOME TESTS FAILED ✗✗✗")
        sys.exit(1)
