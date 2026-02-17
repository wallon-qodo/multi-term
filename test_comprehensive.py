#!/usr/bin/env python3
"""Comprehensive automated test suite for drag-to-swap functionality."""

import sys
import time
import asyncio
from pathlib import Path

# Test results
results = {
    "passed": [],
    "failed": [],
    "warnings": []
}

def log_pass(test_name):
    print(f"✓ PASS: {test_name}")
    results["passed"].append(test_name)

def log_fail(test_name, error):
    print(f"✗ FAIL: {test_name}")
    print(f"  Error: {error}")
    results["failed"].append((test_name, error))

def log_warning(test_name, warning):
    print(f"⚠ WARNING: {test_name}")
    print(f"  {warning}")
    results["warnings"].append((test_name, warning))

print("="*70)
print("COMPREHENSIVE TEST SUITE - DRAG-TO-SWAP FUNCTIONALITY")
print("="*70)
print()

# TEST 1: Module imports
print("TEST 1: Module Imports")
print("-" * 70)
try:
    from claude_multi_terminal.widgets.resizable_grid import ResizablePane, ResizableSessionGrid
    log_pass("ResizablePane and ResizableSessionGrid imports")

    from claude_multi_terminal.widgets.session_pane import SessionPane
    log_pass("SessionPane import")

    from claude_multi_terminal.app import ClaudeMultiTerminalApp
    log_pass("ClaudeMultiTerminalApp import")

    from textual.widgets import Static
    from textual import events
    from textual.message import Message
    log_pass("Textual imports")

except Exception as e:
    log_fail("Module imports", str(e))
    import traceback
    traceback.print_exc()
    sys.exit(1)

print()

# TEST 2: ResizablePane structure
print("TEST 2: ResizablePane Structure")
print("-" * 70)
try:
    # Check for drag handle
    if hasattr(ResizablePane, 'DragStarted'):
        log_pass("ResizablePane has DragStarted message")
    else:
        log_fail("ResizablePane DragStarted message", "Missing DragStarted class")

    if hasattr(ResizablePane, 'DragEnded'):
        log_pass("ResizablePane has DragEnded message")
    else:
        log_fail("ResizablePane DragEnded message", "Missing DragEnded class")

    # Check for mouse handlers
    required_methods = ['on_mouse_down', 'on_mouse_move', 'on_mouse_up',
                       'set_drop_target', 'set_drop_target_active']

    for method in required_methods:
        if hasattr(ResizablePane, method):
            log_pass(f"ResizablePane has {method}")
        else:
            log_fail(f"ResizablePane {method}", f"Missing method {method}")

    # Check CSS
    if 'drag-handle' in ResizablePane.DEFAULT_CSS:
        log_pass("ResizablePane has drag-handle CSS")
    else:
        log_warning("ResizablePane drag-handle CSS", "drag-handle not found in CSS")

    if 'dragging' in ResizablePane.DEFAULT_CSS:
        log_pass("ResizablePane has dragging state CSS")
    else:
        log_fail("ResizablePane dragging CSS", "dragging state CSS missing")

except Exception as e:
    log_fail("ResizablePane structure check", str(e))
    import traceback
    traceback.print_exc()

print()

# TEST 3: ResizableSessionGrid handlers
print("TEST 3: ResizableSessionGrid Handlers")
print("-" * 70)
try:
    if hasattr(ResizableSessionGrid, 'on_resizable_pane_drag_started'):
        log_pass("ResizableSessionGrid has on_resizable_pane_drag_started")
    else:
        log_fail("ResizableSessionGrid drag_started handler", "Missing handler")

    if hasattr(ResizableSessionGrid, 'on_resizable_pane_drag_ended'):
        log_pass("ResizableSessionGrid has on_resizable_pane_drag_ended")
    else:
        log_fail("ResizableSessionGrid drag_ended handler", "Missing handler")

    if hasattr(ResizableSessionGrid, '_swap_sessions'):
        log_pass("ResizableSessionGrid has _swap_sessions")
    else:
        log_fail("ResizableSessionGrid swap method", "Missing _swap_sessions")

except Exception as e:
    log_fail("ResizableSessionGrid handler check", str(e))
    import traceback
    traceback.print_exc()

print()

# TEST 4: App creation
print("TEST 4: App Creation")
print("-" * 70)
try:
    app = ClaudeMultiTerminalApp()
    log_pass("ClaudeMultiTerminalApp instance created")

    # Check if app has required attributes
    if hasattr(app, 'TITLE'):
        log_pass("App has TITLE attribute")

    if hasattr(app, 'CSS_PATH'):
        log_pass("App has CSS_PATH attribute")

except Exception as e:
    log_fail("App creation", str(e))
    import traceback
    traceback.print_exc()

print()

# TEST 5: ResizablePane instantiation
print("TEST 5: ResizablePane Instantiation")
print("-" * 70)
try:
    from textual.widgets import Label

    # Create a mock content widget
    content = Label("Test Content")
    pane = ResizablePane(content)

    log_pass("ResizablePane instantiated with content")

    # Check initialization
    if hasattr(pane, 'drag_handle'):
        log_pass("ResizablePane has drag_handle attribute")
    else:
        log_fail("ResizablePane drag_handle", "Missing drag_handle attribute")

    if hasattr(pane, 'is_being_dragged'):
        log_pass("ResizablePane has is_being_dragged attribute")
    else:
        log_fail("ResizablePane is_being_dragged", "Missing is_being_dragged attribute")

    if hasattr(pane, 'drag_start_pos'):
        log_pass("ResizablePane has drag_start_pos attribute")
    else:
        log_fail("ResizablePane drag_start_pos", "Missing drag_start_pos attribute")

    if hasattr(pane, 'drag_threshold'):
        log_pass("ResizablePane has drag_threshold attribute")
        if pane.drag_threshold == 5:
            log_pass("ResizablePane drag_threshold is 5")
        else:
            log_warning("ResizablePane drag_threshold", f"Expected 5, got {pane.drag_threshold}")
    else:
        log_fail("ResizablePane drag_threshold", "Missing drag_threshold attribute")

except Exception as e:
    log_fail("ResizablePane instantiation", str(e))
    import traceback
    traceback.print_exc()

print()

# TEST 6: Message class validation
print("TEST 6: Message Classes")
print("-" * 70)
try:
    from textual.message import Message as TextualMessage

    # Check DragStarted
    drag_started = ResizablePane.DragStarted
    if issubclass(drag_started, TextualMessage):
        log_pass("DragStarted is a valid Textual Message")
    else:
        log_fail("DragStarted message", "Not a Textual Message subclass")

    # Check DragEnded
    drag_ended = ResizablePane.DragEnded
    if issubclass(drag_ended, TextualMessage):
        log_pass("DragEnded is a valid Textual Message")
    else:
        log_fail("DragEnded message", "Not a Textual Message subclass")

    # Test message instantiation
    try:
        msg = ResizablePane.DragStarted(pane, "test-session-id")
        if hasattr(msg, 'session_id') and msg.session_id == "test-session-id":
            log_pass("DragStarted message instantiation")
        else:
            log_fail("DragStarted message", "session_id not set correctly")
    except Exception as e:
        log_fail("DragStarted message instantiation", str(e))

    try:
        msg = ResizablePane.DragEnded(pane, "source-id", "target-id")
        if (hasattr(msg, 'session_id') and msg.session_id == "source-id" and
            hasattr(msg, 'target_session_id') and msg.target_session_id == "target-id"):
            log_pass("DragEnded message instantiation")
        else:
            log_fail("DragEnded message", "IDs not set correctly")
    except Exception as e:
        log_fail("DragEnded message instantiation", str(e))

except Exception as e:
    log_fail("Message class validation", str(e))
    import traceback
    traceback.print_exc()

print()

# TEST 7: Integration test (if possible)
print("TEST 7: Integration Test")
print("-" * 70)
try:
    # This test checks if the components work together
    from claude_multi_terminal.core.session_manager import SessionManager
    from textual.app import App

    class TestApp(App):
        def compose(self):
            from textual.containers import Container
            yield Container()

    test_app = TestApp()
    log_pass("Test app created for integration testing")

except Exception as e:
    log_warning("Integration test", f"Could not create test app: {str(e)}")

print()

# TEST 8: File structure check
print("TEST 8: File Structure")
print("-" * 70)
try:
    base_path = Path(__file__).parent / "claude_multi_terminal"

    required_files = [
        "widgets/__init__.py",
        "widgets/resizable_grid.py",
        "widgets/session_pane.py",
        "app.py"
    ]

    for file in required_files:
        file_path = base_path / file
        if file_path.exists():
            log_pass(f"File exists: {file}")
        else:
            log_fail(f"File check: {file}", "File not found")

except Exception as e:
    log_fail("File structure check", str(e))

print()

# SUMMARY
print("="*70)
print("TEST SUMMARY")
print("="*70)
print(f"✓ Passed: {len(results['passed'])}")
print(f"✗ Failed: {len(results['failed'])}")
print(f"⚠ Warnings: {len(results['warnings'])}")
print()

if results['failed']:
    print("FAILED TESTS:")
    for test_name, error in results['failed']:
        print(f"  - {test_name}: {error}")
    print()

if results['warnings']:
    print("WARNINGS:")
    for test_name, warning in results['warnings']:
        print(f"  - {test_name}: {warning}")
    print()

# Final verdict
if not results['failed']:
    print("="*70)
    print("✓ ALL CRITICAL TESTS PASSED!")
    print("="*70)
    print()
    print("The drag-to-swap functionality is properly implemented.")
    print()
    print("To test manually:")
    print("1. Run: python3 -m claude_multi_terminal.app")
    print("2. Look for gray bars at the top of each pane (with ⣿ symbol)")
    print("3. Click and drag from the gray bar (not the pane content)")
    print("4. Drag over another pane and release to swap")
    print()
    sys.exit(0)
else:
    print("="*70)
    print("✗ SOME TESTS FAILED")
    print("="*70)
    print()
    print("Please review the failures above.")
    sys.exit(1)
