"""Comprehensive tests for workspace system data model.

Test Coverage:
    - Workspace creation and validation
    - LayoutMode enum
    - WorkspaceManager lifecycle operations
    - Session management across workspaces
    - Focus handling
    - Edge cases and error conditions
"""

import time
import pytest
from claude_multi_terminal.workspaces import (
    Workspace,
    LayoutMode,
    WorkspaceManager
)


class TestLayoutMode:
    """Tests for LayoutMode enum."""

    def test_layout_mode_values(self):
        """Verify all layout modes have correct string values."""
        assert LayoutMode.TILED.value == "tiled"
        assert LayoutMode.FLOATING.value == "floating"
        assert LayoutMode.MONOCLE.value == "monocle"

    def test_layout_mode_comparison(self):
        """Verify enum comparison works correctly."""
        assert LayoutMode.TILED == LayoutMode.TILED
        assert LayoutMode.TILED != LayoutMode.FLOATING


class TestWorkspace:
    """Tests for Workspace dataclass."""

    def test_workspace_creation_default(self):
        """Test creating workspace with default values."""
        ws = Workspace(id=1, name="Test Workspace")

        assert ws.id == 1
        assert ws.name == "Test Workspace"
        assert ws.session_ids == []
        assert ws.focused_session_id is None
        assert ws.layout_mode == LayoutMode.TILED
        assert isinstance(ws.created_at, float)
        assert isinstance(ws.modified_at, float)

    def test_workspace_creation_custom(self):
        """Test creating workspace with custom values."""
        custom_time = time.time()
        session_ids = ["session-1", "session-2"]

        ws = Workspace(
            id=5,
            name="Custom",
            session_ids=session_ids,
            focused_session_id="session-1",
            layout_mode=LayoutMode.FLOATING,
            created_at=custom_time,
            modified_at=custom_time
        )

        assert ws.id == 5
        assert ws.name == "Custom"
        assert ws.session_ids == session_ids
        assert ws.focused_session_id == "session-1"
        assert ws.layout_mode == LayoutMode.FLOATING
        assert ws.created_at == custom_time

    def test_workspace_id_validation(self):
        """Test workspace ID must be between 1 and 9."""
        # Valid IDs
        for i in range(1, 10):
            ws = Workspace(id=i, name=f"Workspace {i}")
            assert ws.id == i

        # Invalid IDs
        with pytest.raises(ValueError):
            Workspace(id=0, name="Invalid")

        with pytest.raises(ValueError):
            Workspace(id=10, name="Invalid")

        with pytest.raises(ValueError):
            Workspace(id=-1, name="Invalid")

    def test_add_session(self):
        """Test adding sessions to workspace."""
        ws = Workspace(id=1, name="Test")
        initial_modified = ws.modified_at

        time.sleep(0.01)  # Ensure timestamp changes
        ws.add_session("session-1")

        assert "session-1" in ws.session_ids
        assert ws.modified_at > initial_modified

    def test_add_duplicate_session(self):
        """Test adding duplicate session doesn't create duplicates."""
        ws = Workspace(id=1, name="Test")
        ws.add_session("session-1")
        ws.add_session("session-1")

        assert ws.session_ids.count("session-1") == 1

    def test_remove_session(self):
        """Test removing sessions from workspace."""
        ws = Workspace(id=1, name="Test")
        ws.add_session("session-1")
        ws.add_session("session-2")
        initial_modified = ws.modified_at

        time.sleep(0.01)
        result = ws.remove_session("session-1")

        assert result is True
        assert "session-1" not in ws.session_ids
        assert "session-2" in ws.session_ids
        assert ws.modified_at > initial_modified

    def test_remove_nonexistent_session(self):
        """Test removing session that doesn't exist."""
        ws = Workspace(id=1, name="Test")
        result = ws.remove_session("nonexistent")

        assert result is False

    def test_remove_focused_session(self):
        """Test removing focused session clears focus properly."""
        ws = Workspace(id=1, name="Test")
        ws.add_session("session-1")
        ws.add_session("session-2")
        ws.set_focus("session-1")

        ws.remove_session("session-1")

        # Should focus next available session
        assert ws.focused_session_id == "session-2"

    def test_remove_last_session_clears_focus(self):
        """Test removing last session clears focus to None."""
        ws = Workspace(id=1, name="Test")
        ws.add_session("session-1")
        ws.set_focus("session-1")

        ws.remove_session("session-1")

        assert ws.focused_session_id is None

    def test_set_focus(self):
        """Test setting focus to a session."""
        ws = Workspace(id=1, name="Test")
        ws.add_session("session-1")
        ws.add_session("session-2")

        result = ws.set_focus("session-2")

        assert result is True
        assert ws.focused_session_id == "session-2"

    def test_set_focus_invalid_session(self):
        """Test setting focus to session not in workspace fails."""
        ws = Workspace(id=1, name="Test")
        ws.add_session("session-1")

        result = ws.set_focus("nonexistent")

        assert result is False
        assert ws.focused_session_id is None

    def test_clear_focus(self):
        """Test clearing focus by passing None."""
        ws = Workspace(id=1, name="Test")
        ws.add_session("session-1")
        ws.set_focus("session-1")

        result = ws.set_focus(None)

        assert result is True
        assert ws.focused_session_id is None

    def test_set_layout_mode(self):
        """Test changing layout mode."""
        ws = Workspace(id=1, name="Test")
        initial_modified = ws.modified_at

        time.sleep(0.01)
        ws.set_layout_mode(LayoutMode.MONOCLE)

        assert ws.layout_mode == LayoutMode.MONOCLE
        assert ws.modified_at > initial_modified

    def test_is_empty(self):
        """Test checking if workspace is empty."""
        ws = Workspace(id=1, name="Test")

        assert ws.is_empty() is True

        ws.add_session("session-1")
        assert ws.is_empty() is False

        ws.remove_session("session-1")
        assert ws.is_empty() is True

    def test_update_modified_time(self):
        """Test manual modification timestamp update."""
        ws = Workspace(id=1, name="Test")
        initial_modified = ws.modified_at

        time.sleep(0.01)
        ws.update_modified_time()

        assert ws.modified_at > initial_modified


class TestWorkspaceManager:
    """Tests for WorkspaceManager class."""

    def test_manager_initialization(self):
        """Test manager creates 9 default workspaces."""
        manager = WorkspaceManager()

        assert len(manager.workspaces) == 9
        assert manager.active_workspace_id == 1

        for i in range(1, 10):
            ws = manager.get_workspace(i)
            assert ws is not None
            assert ws.id == i
            assert ws.name == f"Workspace {i}"
            assert ws.is_empty()

    def test_create_workspace(self):
        """Test creating/recreating a workspace."""
        manager = WorkspaceManager()

        ws = manager.create_workspace(5, "Custom Workspace")

        assert ws.id == 5
        assert ws.name == "Custom Workspace"
        assert manager.get_workspace(5) == ws

    def test_create_workspace_invalid_id(self):
        """Test creating workspace with invalid ID raises error."""
        manager = WorkspaceManager()

        with pytest.raises(ValueError):
            manager.create_workspace(0, "Invalid")

        with pytest.raises(ValueError):
            manager.create_workspace(10, "Invalid")

    def test_get_workspace(self):
        """Test retrieving workspace by ID."""
        manager = WorkspaceManager()

        ws = manager.get_workspace(3)
        assert ws is not None
        assert ws.id == 3

        ws_none = manager.get_workspace(99)
        assert ws_none is None

    def test_get_active_workspace(self):
        """Test retrieving currently active workspace."""
        manager = WorkspaceManager()

        active = manager.get_active_workspace()
        assert active.id == 1

        manager.switch_to_workspace(5)
        active = manager.get_active_workspace()
        assert active.id == 5

    def test_switch_to_workspace(self):
        """Test switching between workspaces."""
        manager = WorkspaceManager()

        result = manager.switch_to_workspace(7)
        assert result is True
        assert manager.active_workspace_id == 7

        result = manager.switch_to_workspace(99)
        assert result is False
        assert manager.active_workspace_id == 7  # Unchanged

    def test_rename_workspace(self):
        """Test renaming an existing workspace."""
        manager = WorkspaceManager()

        result = manager.rename_workspace(3, "My Custom Name")
        assert result is True

        ws = manager.get_workspace(3)
        assert ws.name == "My Custom Name"

    def test_rename_nonexistent_workspace(self):
        """Test renaming nonexistent workspace fails."""
        manager = WorkspaceManager()

        result = manager.rename_workspace(99, "Invalid")
        assert result is False

    def test_add_session_to_workspace(self):
        """Test adding session to workspace."""
        manager = WorkspaceManager()

        result = manager.add_session_to_workspace(2, "session-1")
        assert result is True

        ws = manager.get_workspace(2)
        assert "session-1" in ws.session_ids

    def test_add_session_auto_focus(self):
        """Test adding first session to empty workspace auto-focuses it."""
        manager = WorkspaceManager()

        manager.add_session_to_workspace(4, "session-1")
        ws = manager.get_workspace(4)

        assert ws.focused_session_id == "session-1"

    def test_add_session_to_nonexistent_workspace(self):
        """Test adding session to nonexistent workspace fails."""
        manager = WorkspaceManager()

        result = manager.add_session_to_workspace(99, "session-1")
        assert result is False

    def test_remove_session_from_workspace(self):
        """Test removing session from workspace."""
        manager = WorkspaceManager()
        manager.add_session_to_workspace(3, "session-1")
        manager.add_session_to_workspace(3, "session-2")

        result = manager.remove_session_from_workspace(3, "session-1")
        assert result is True

        ws = manager.get_workspace(3)
        assert "session-1" not in ws.session_ids
        assert "session-2" in ws.session_ids

    def test_remove_session_nonexistent(self):
        """Test removing nonexistent session."""
        manager = WorkspaceManager()

        result = manager.remove_session_from_workspace(3, "nonexistent")
        assert result is False

    def test_move_session(self):
        """Test moving session between workspaces."""
        manager = WorkspaceManager()
        manager.add_session_to_workspace(1, "session-1")

        result = manager.move_session("session-1", 1, 5)
        assert result is True

        ws1 = manager.get_workspace(1)
        ws5 = manager.get_workspace(5)

        assert "session-1" not in ws1.session_ids
        assert "session-1" in ws5.session_ids

    def test_move_session_auto_focus_destination(self):
        """Test moving session to empty workspace auto-focuses it."""
        manager = WorkspaceManager()
        manager.add_session_to_workspace(1, "session-1")

        manager.move_session("session-1", 1, 5)
        ws5 = manager.get_workspace(5)

        assert ws5.focused_session_id == "session-1"

    def test_move_session_invalid_workspace(self):
        """Test moving session with invalid workspace IDs fails."""
        manager = WorkspaceManager()
        manager.add_session_to_workspace(1, "session-1")

        result = manager.move_session("session-1", 1, 99)
        assert result is False

        result = manager.move_session("session-1", 99, 1)
        assert result is False

    def test_move_nonexistent_session(self):
        """Test moving session that doesn't exist in source."""
        manager = WorkspaceManager()

        result = manager.move_session("nonexistent", 1, 2)
        assert result is False

    def test_get_session_workspace(self):
        """Test finding which workspace contains a session."""
        manager = WorkspaceManager()
        manager.add_session_to_workspace(3, "session-1")
        manager.add_session_to_workspace(7, "session-2")

        ws_id = manager.get_session_workspace("session-1")
        assert ws_id == 3

        ws_id = manager.get_session_workspace("session-2")
        assert ws_id == 7

        ws_id = manager.get_session_workspace("nonexistent")
        assert ws_id is None

    def test_list_workspaces(self):
        """Test listing all workspaces."""
        manager = WorkspaceManager()

        workspaces = manager.list_workspaces()

        assert len(workspaces) == 9
        assert all(isinstance(ws, Workspace) for ws in workspaces)
        assert [ws.id for ws in workspaces] == list(range(1, 10))

    def test_get_workspace_session_count(self):
        """Test getting session count for workspace."""
        manager = WorkspaceManager()
        manager.add_session_to_workspace(2, "session-1")
        manager.add_session_to_workspace(2, "session-2")
        manager.add_session_to_workspace(2, "session-3")

        count = manager.get_workspace_session_count(2)
        assert count == 3

        count = manager.get_workspace_session_count(5)
        assert count == 0

        count = manager.get_workspace_session_count(99)
        assert count == 0

    def test_clear_workspace(self):
        """Test clearing all sessions from workspace."""
        manager = WorkspaceManager()
        manager.add_session_to_workspace(4, "session-1")
        manager.add_session_to_workspace(4, "session-2")

        result = manager.clear_workspace(4)
        assert result is True

        ws = manager.get_workspace(4)
        assert ws.is_empty()
        assert ws.focused_session_id is None

    def test_clear_nonexistent_workspace(self):
        """Test clearing nonexistent workspace fails."""
        manager = WorkspaceManager()

        result = manager.clear_workspace(99)
        assert result is False

    def test_set_workspace_layout(self):
        """Test changing workspace layout mode."""
        manager = WorkspaceManager()

        result = manager.set_workspace_layout(6, LayoutMode.FLOATING)
        assert result is True

        ws = manager.get_workspace(6)
        assert ws.layout_mode == LayoutMode.FLOATING

    def test_set_layout_nonexistent_workspace(self):
        """Test setting layout on nonexistent workspace fails."""
        manager = WorkspaceManager()

        result = manager.set_workspace_layout(99, LayoutMode.MONOCLE)
        assert result is False


class TestWorkspaceIntegration:
    """Integration tests for complex workspace scenarios."""

    def test_multiple_workspaces_with_sessions(self):
        """Test managing multiple workspaces with different sessions."""
        manager = WorkspaceManager()

        # Setup workspace 1
        manager.rename_workspace(1, "Development")
        manager.add_session_to_workspace(1, "dev-session-1")
        manager.add_session_to_workspace(1, "dev-session-2")
        manager.set_workspace_layout(1, LayoutMode.TILED)

        # Setup workspace 2
        manager.rename_workspace(2, "Testing")
        manager.add_session_to_workspace(2, "test-session-1")
        manager.set_workspace_layout(2, LayoutMode.MONOCLE)

        # Setup workspace 3
        manager.rename_workspace(3, "Research")
        manager.add_session_to_workspace(3, "research-session-1")
        manager.add_session_to_workspace(3, "research-session-2")
        manager.add_session_to_workspace(3, "research-session-3")
        manager.set_workspace_layout(3, LayoutMode.FLOATING)

        # Verify isolation
        ws1 = manager.get_workspace(1)
        ws2 = manager.get_workspace(2)
        ws3 = manager.get_workspace(3)

        assert len(ws1.session_ids) == 2
        assert len(ws2.session_ids) == 1
        assert len(ws3.session_ids) == 3

        assert ws1.layout_mode == LayoutMode.TILED
        assert ws2.layout_mode == LayoutMode.MONOCLE
        assert ws3.layout_mode == LayoutMode.FLOATING

    def test_session_lifecycle_across_workspaces(self):
        """Test complete session lifecycle: create, move, remove."""
        manager = WorkspaceManager()

        # Create session in workspace 1
        manager.add_session_to_workspace(1, "session-abc")
        assert manager.get_session_workspace("session-abc") == 1

        # Move to workspace 5
        manager.move_session("session-abc", 1, 5)
        assert manager.get_session_workspace("session-abc") == 5
        assert manager.get_workspace_session_count(1) == 0
        assert manager.get_workspace_session_count(5) == 1

        # Move to workspace 9
        manager.move_session("session-abc", 5, 9)
        assert manager.get_session_workspace("session-abc") == 9

        # Remove from workspace 9
        manager.remove_session_from_workspace(9, "session-abc")
        assert manager.get_session_workspace("session-abc") is None
        assert manager.get_workspace_session_count(9) == 0

    def test_focus_management_complex(self):
        """Test focus handling with multiple operations."""
        manager = WorkspaceManager()

        # Add sessions
        manager.add_session_to_workspace(1, "session-1")
        manager.add_session_to_workspace(1, "session-2")
        manager.add_session_to_workspace(1, "session-3")

        ws = manager.get_workspace(1)

        # First session should be auto-focused
        assert ws.focused_session_id == "session-1"

        # Change focus
        ws.set_focus("session-2")
        assert ws.focused_session_id == "session-2"

        # Remove focused session
        ws.remove_session("session-2")
        # Should focus next available (session-3)
        assert ws.focused_session_id == "session-3"

        # Remove all sessions one by one
        ws.remove_session("session-1")
        assert ws.focused_session_id == "session-3"

        ws.remove_session("session-3")
        assert ws.focused_session_id is None

    def test_workspace_switch_preserves_state(self):
        """Test switching workspaces preserves individual workspace state."""
        manager = WorkspaceManager()

        # Setup different workspaces
        manager.add_session_to_workspace(1, "ws1-session")
        manager.add_session_to_workspace(2, "ws2-session")
        manager.get_workspace(1).set_focus("ws1-session")
        manager.get_workspace(2).set_focus("ws2-session")

        # Switch between workspaces
        manager.switch_to_workspace(1)
        assert manager.get_active_workspace().focused_session_id == "ws1-session"

        manager.switch_to_workspace(2)
        assert manager.get_active_workspace().focused_session_id == "ws2-session"

        manager.switch_to_workspace(1)
        assert manager.get_active_workspace().focused_session_id == "ws1-session"
