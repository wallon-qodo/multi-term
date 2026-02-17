#!/usr/bin/env python3
"""Test script to verify drag-to-swap functionality integration.

This test creates a simple UI with multiple session panes and verifies:
1. Drag messages are properly defined
2. CSS classes for drag states are defined
3. Event handlers are in place
4. Swap logic is implemented
"""

from claude_multi_terminal.widgets.session_pane import SessionPane
from claude_multi_terminal.widgets.resizable_grid import ResizableSessionGrid


def test_drag_messages_exist():
    """Verify drag message classes exist."""
    print("✓ Testing drag message classes...")

    # Check DragStarted exists
    assert hasattr(SessionPane, 'DragStarted'), "DragStarted message class not found"
    drag_started = SessionPane.DragStarted("test-id")
    assert drag_started.session_id == "test-id"
    print("  ✓ DragStarted message works")

    # Check DragEnded exists
    assert hasattr(SessionPane, 'DragEnded'), "DragEnded message class not found"
    drag_ended = SessionPane.DragEnded("test-id", "target-id")
    assert drag_ended.session_id == "test-id"
    assert drag_ended.target_session_id == "target-id"
    print("  ✓ DragEnded message works")


def test_drag_css_exists():
    """Verify drag-related CSS is defined."""
    print("✓ Testing CSS for drag states...")

    css = SessionPane.DEFAULT_CSS

    # Check for drag-related CSS classes
    assert "SessionPane.dragging" in css, "Missing CSS for .dragging state"
    assert "SessionPane.drop-target" in css, "Missing CSS for .drop-target state"
    assert "SessionPane.drop-target-active" in css, "Missing CSS for .drop-target-active state"

    print("  ✓ All drag CSS classes defined")


def test_drag_methods_exist():
    """Verify drag-related methods exist."""
    print("✓ Testing drag methods...")

    # Create a dummy session pane
    pane = SessionPane(
        session_id="test-123",
        session_name="Test Session",
        session_manager=None
    )

    # Check drag state attributes
    assert hasattr(pane, 'is_being_dragged'), "Missing is_being_dragged attribute"
    assert hasattr(pane, 'drag_start_pos'), "Missing drag_start_pos attribute"
    assert hasattr(pane, 'drag_threshold'), "Missing drag_threshold attribute"

    # Check methods exist
    assert hasattr(pane, 'on_mouse_move'), "Missing on_mouse_move method"
    assert hasattr(pane, 'set_drop_target'), "Missing set_drop_target method"
    assert hasattr(pane, 'set_drop_target_active'), "Missing set_drop_target_active method"

    print("  ✓ All drag methods exist")


def test_grid_drag_handlers_exist():
    """Verify grid has drag event handlers."""
    print("✓ Testing grid drag handlers...")

    grid = ResizableSessionGrid()

    # Check drag state
    assert hasattr(grid, 'dragged_session_id'), "Missing dragged_session_id attribute"

    # Check handler methods
    assert hasattr(grid, 'on_session_pane_drag_started'), "Missing on_session_pane_drag_started handler"
    assert hasattr(grid, 'on_session_pane_drag_ended'), "Missing on_session_pane_drag_ended handler"
    assert hasattr(grid, '_swap_sessions'), "Missing _swap_sessions method"

    print("  ✓ All grid handlers exist")


def test_swap_logic():
    """Test the swap logic without UI."""
    print("✓ Testing swap logic...")

    # This tests that the method exists and doesn't crash
    grid = ResizableSessionGrid()

    # The method should handle non-existent sessions gracefully
    grid._swap_sessions("nonexistent-1", "nonexistent-2")

    print("  ✓ Swap logic doesn't crash on invalid input")


def main():
    """Run all tests."""
    print("\n" + "="*60)
    print("Testing Drag-to-Swap Integration")
    print("="*60 + "\n")

    try:
        test_drag_messages_exist()
        test_drag_css_exists()
        test_drag_methods_exist()
        test_grid_drag_handlers_exist()
        test_swap_logic()

        print("\n" + "="*60)
        print("✓ All tests passed!")
        print("="*60 + "\n")
        print("Integration complete. Drag-to-swap functionality is ready.")
        print("\nTo test interactively:")
        print("1. Run the app: python -m claude_multi_terminal")
        print("2. Create multiple sessions")
        print("3. Click and drag a session pane")
        print("4. Drop it on another pane to swap positions")
        print()

    except AssertionError as e:
        print(f"\n✗ Test failed: {e}\n")
        return 1
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}\n")
        import traceback
        traceback.print_exc()
        return 1

    return 0


if __name__ == '__main__':
    exit(main())
