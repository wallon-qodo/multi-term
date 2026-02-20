#!/usr/bin/env python3
"""Standalone test for workspace system."""

import sys
import os
import time

# Add the directory containing workspaces.py to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'claude_multi_terminal'))

# Import the module directly without going through __init__.py
import importlib.util
spec = importlib.util.spec_from_file_location(
    "workspaces",
    "/Users/wallonwalusayi/claude-multi-terminal/claude_multi_terminal/workspaces.py"
)
workspaces = importlib.util.module_from_spec(spec)
spec.loader.exec_module(workspaces)

Workspace = workspaces.Workspace
LayoutMode = workspaces.LayoutMode
WorkspaceManager = workspaces.WorkspaceManager


def test_layout_mode():
    """Test LayoutMode enum."""
    print("Testing LayoutMode enum...")
    assert LayoutMode.TILED.value == "tiled"
    assert LayoutMode.FLOATING.value == "floating"
    assert LayoutMode.MONOCLE.value == "monocle"
    print("  ✓ LayoutMode values correct")


def test_workspace_creation():
    """Test Workspace creation."""
    print("\nTesting Workspace creation...")

    # Default values
    ws = Workspace(id=1, name="Test Workspace")
    assert ws.id == 1
    assert ws.name == "Test Workspace"
    assert ws.session_ids == []
    assert ws.focused_session_id is None
    assert ws.layout_mode == LayoutMode.TILED
    assert isinstance(ws.created_at, float)
    assert isinstance(ws.modified_at, float)
    print("  ✓ Default workspace creation works")

    # Custom values
    custom_time = time.time()
    ws2 = Workspace(
        id=5,
        name="Custom",
        session_ids=["s1", "s2"],
        focused_session_id="s1",
        layout_mode=LayoutMode.FLOATING,
        created_at=custom_time,
        modified_at=custom_time
    )
    assert ws2.id == 5
    assert ws2.session_ids == ["s1", "s2"]
    print("  ✓ Custom workspace creation works")


def test_workspace_validation():
    """Test Workspace ID validation."""
    print("\nTesting Workspace ID validation...")

    # Valid IDs
    for i in range(1, 10):
        ws = Workspace(id=i, name=f"WS{i}")
        assert ws.id == i
    print("  ✓ Valid IDs (1-9) accepted")

    # Invalid IDs
    for invalid_id in [0, 10, -1]:
        try:
            Workspace(id=invalid_id, name="Invalid")
            assert False, f"Should have raised ValueError for id={invalid_id}"
        except ValueError:
            pass
    print("  ✓ Invalid IDs rejected")


def test_workspace_session_management():
    """Test adding/removing sessions."""
    print("\nTesting session management...")

    ws = Workspace(id=1, name="Test")

    # Add sessions
    ws.add_session("session-1")
    ws.add_session("session-2")
    assert len(ws.session_ids) == 2
    assert "session-1" in ws.session_ids
    print("  ✓ Adding sessions works")

    # Duplicate handling
    ws.add_session("session-1")
    assert ws.session_ids.count("session-1") == 1
    print("  ✓ Duplicate sessions prevented")

    # Remove session
    result = ws.remove_session("session-1")
    assert result is True
    assert "session-1" not in ws.session_ids
    assert len(ws.session_ids) == 1
    print("  ✓ Removing sessions works")

    # Remove nonexistent
    result = ws.remove_session("nonexistent")
    assert result is False
    print("  ✓ Removing nonexistent session returns False")


def test_workspace_focus():
    """Test focus management."""
    print("\nTesting focus management...")

    ws = Workspace(id=1, name="Test")
    ws.add_session("session-1")
    ws.add_session("session-2")

    # Set focus
    result = ws.set_focus("session-2")
    assert result is True
    assert ws.focused_session_id == "session-2"
    print("  ✓ Setting focus works")

    # Invalid focus
    result = ws.set_focus("nonexistent")
    assert result is False
    print("  ✓ Invalid focus rejected")

    # Clear focus
    result = ws.set_focus(None)
    assert result is True
    assert ws.focused_session_id is None
    print("  ✓ Clearing focus works")

    # Remove focused session
    ws.set_focus("session-1")
    ws.remove_session("session-1")
    assert ws.focused_session_id == "session-2"  # Should auto-focus next
    print("  ✓ Focus shifts when removing focused session")


def test_workspace_manager_init():
    """Test WorkspaceManager initialization."""
    print("\nTesting WorkspaceManager initialization...")

    manager = WorkspaceManager()
    assert len(manager.workspaces) == 9
    assert manager.active_workspace_id == 1

    for i in range(1, 10):
        ws = manager.get_workspace(i)
        assert ws is not None
        assert ws.id == i
        assert ws.name == f"Workspace {i}"
        assert ws.is_empty()

    print("  ✓ All 9 workspaces initialized")


def test_workspace_manager_operations():
    """Test WorkspaceManager operations."""
    print("\nTesting WorkspaceManager operations...")

    manager = WorkspaceManager()

    # Create/rename
    ws = manager.create_workspace(5, "Custom")
    assert ws.name == "Custom"
    print("  ✓ Workspace creation works")

    result = manager.rename_workspace(3, "Renamed")
    assert result is True
    assert manager.get_workspace(3).name == "Renamed"
    print("  ✓ Workspace renaming works")

    # Switch workspace
    result = manager.switch_to_workspace(7)
    assert result is True
    assert manager.active_workspace_id == 7
    print("  ✓ Workspace switching works")

    # Add sessions
    result = manager.add_session_to_workspace(2, "session-1")
    assert result is True
    assert "session-1" in manager.get_workspace(2).session_ids
    print("  ✓ Adding sessions to workspace works")

    # Auto-focus first session
    ws2 = manager.get_workspace(2)
    assert ws2.focused_session_id == "session-1"
    print("  ✓ First session auto-focused")


def test_workspace_manager_session_operations():
    """Test session operations across workspaces."""
    print("\nTesting session operations across workspaces...")

    manager = WorkspaceManager()

    # Add sessions to different workspaces
    manager.add_session_to_workspace(1, "session-1")
    manager.add_session_to_workspace(2, "session-2")
    manager.add_session_to_workspace(3, "session-3")

    # Find session workspace
    ws_id = manager.get_session_workspace("session-2")
    assert ws_id == 2
    print("  ✓ Finding session workspace works")

    # Move session
    result = manager.move_session("session-1", 1, 5)
    assert result is True
    assert manager.get_session_workspace("session-1") == 5
    assert manager.get_workspace_session_count(1) == 0
    assert manager.get_workspace_session_count(5) == 1
    print("  ✓ Moving sessions between workspaces works")

    # Remove session
    result = manager.remove_session_from_workspace(2, "session-2")
    assert result is True
    assert manager.get_session_workspace("session-2") is None
    print("  ✓ Removing sessions works")

    # Clear workspace
    manager.add_session_to_workspace(4, "s1")
    manager.add_session_to_workspace(4, "s2")
    result = manager.clear_workspace(4)
    assert result is True
    assert manager.get_workspace(4).is_empty()
    print("  ✓ Clearing workspace works")


def test_workspace_layout():
    """Test layout mode operations."""
    print("\nTesting layout mode operations...")

    ws = Workspace(id=1, name="Test")
    ws.set_layout_mode(LayoutMode.MONOCLE)
    assert ws.layout_mode == LayoutMode.MONOCLE
    print("  ✓ Workspace layout setting works")

    manager = WorkspaceManager()
    result = manager.set_workspace_layout(6, LayoutMode.FLOATING)
    assert result is True
    assert manager.get_workspace(6).layout_mode == LayoutMode.FLOATING
    print("  ✓ Manager layout setting works")


def test_integration_scenario():
    """Test complete integration scenario."""
    print("\nTesting integration scenario...")

    manager = WorkspaceManager()

    # Setup workspace 1 - Development
    manager.rename_workspace(1, "Development")
    manager.add_session_to_workspace(1, "dev-1")
    manager.add_session_to_workspace(1, "dev-2")
    manager.set_workspace_layout(1, LayoutMode.TILED)

    # Setup workspace 2 - Testing
    manager.rename_workspace(2, "Testing")
    manager.add_session_to_workspace(2, "test-1")
    manager.set_workspace_layout(2, LayoutMode.MONOCLE)

    # Setup workspace 3 - Research
    manager.rename_workspace(3, "Research")
    manager.add_session_to_workspace(3, "research-1")
    manager.add_session_to_workspace(3, "research-2")
    manager.set_workspace_layout(3, LayoutMode.FLOATING)

    # Verify isolation
    ws1 = manager.get_workspace(1)
    ws2 = manager.get_workspace(2)
    ws3 = manager.get_workspace(3)

    assert len(ws1.session_ids) == 2
    assert len(ws2.session_ids) == 1
    assert len(ws3.session_ids) == 2

    assert ws1.layout_mode == LayoutMode.TILED
    assert ws2.layout_mode == LayoutMode.MONOCLE
    assert ws3.layout_mode == LayoutMode.FLOATING

    print("  ✓ Multiple workspaces maintain independent state")

    # Test workspace switching preserves state
    manager.switch_to_workspace(1)
    assert manager.get_active_workspace().name == "Development"

    manager.switch_to_workspace(2)
    assert manager.get_active_workspace().name == "Testing"

    manager.switch_to_workspace(3)
    assert manager.get_active_workspace().name == "Research"

    print("  ✓ Workspace switching preserves state")


def test_timestamp_updates():
    """Test that timestamps update correctly."""
    print("\nTesting timestamp updates...")

    ws = Workspace(id=1, name="Test")
    initial_modified = ws.modified_at

    time.sleep(0.01)
    ws.add_session("session-1")
    assert ws.modified_at > initial_modified
    print("  ✓ Adding session updates timestamp")

    modified_after_add = ws.modified_at
    time.sleep(0.01)
    ws.set_focus("session-1")
    assert ws.modified_at > modified_after_add
    print("  ✓ Setting focus updates timestamp")

    modified_after_focus = ws.modified_at
    time.sleep(0.01)
    ws.set_layout_mode(LayoutMode.FLOATING)
    assert ws.modified_at > modified_after_focus
    print("  ✓ Changing layout updates timestamp")


def run_all_tests():
    """Run all tests."""
    print("=" * 70)
    print("WORKSPACE SYSTEM TEST SUITE")
    print("=" * 70)

    tests = [
        test_layout_mode,
        test_workspace_creation,
        test_workspace_validation,
        test_workspace_session_management,
        test_workspace_focus,
        test_workspace_manager_init,
        test_workspace_manager_operations,
        test_workspace_manager_session_operations,
        test_workspace_layout,
        test_integration_scenario,
        test_timestamp_updates,
    ]

    passed = 0
    failed = 0

    for test in tests:
        try:
            test()
            passed += 1
        except AssertionError as e:
            failed += 1
            print(f"\n  ✗ FAILED: {e}")
        except Exception as e:
            failed += 1
            print(f"\n  ✗ ERROR: {e}")

    print("\n" + "=" * 70)
    print(f"RESULTS: {passed} passed, {failed} failed")
    print("=" * 70)

    return failed == 0


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
