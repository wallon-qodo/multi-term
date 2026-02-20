#!/usr/bin/env python3
"""Test script for workspace persistence functionality."""

import time
import tempfile
from pathlib import Path

from claude_multi_terminal.persistence.storage import SessionStorage
from claude_multi_terminal.persistence.session_state import WorkspaceData, SessionState


def test_workspace_persistence():
    """Test saving and loading workspaces."""
    print("Testing workspace persistence...")

    # Create temporary storage directory
    with tempfile.TemporaryDirectory() as tmpdir:
        storage_dir = Path(tmpdir)
        storage = SessionStorage(storage_dir)

        # Create test sessions
        session1 = SessionState(
            session_id="test_session_1",
            name="Dev Session",
            working_directory="/tmp/dev",
            created_at=time.time(),
            modified_at=time.time(),
            command_count=5,
            last_command="ls -la",
            output_snapshot=["line 1", "line 2", "line 3"]
        )

        session2 = SessionState(
            session_id="test_session_2",
            name="Test Session",
            working_directory="/tmp/test",
            created_at=time.time(),
            modified_at=time.time(),
            command_count=3,
            last_command="pytest",
            output_snapshot=["test line 1", "test line 2"]
        )

        # Create test workspaces
        workspace1 = WorkspaceData(
            workspace_id="ws_001",
            name="Development",
            sessions=[session1],
            created_at=time.time(),
            modified_at=time.time(),
            description="Development workspace",
            tags=["dev", "coding"]
        )

        workspace2 = WorkspaceData(
            workspace_id="ws_002",
            name="Testing",
            sessions=[session2],
            created_at=time.time(),
            modified_at=time.time(),
            description="Testing workspace",
            tags=["test", "qa"]
        )

        workspaces = {
            1: workspace1,
            2: workspace2
        }

        # Test save
        print("✓ Testing save_workspaces...")
        result = storage.save_workspaces(workspaces)
        assert result is True, "Failed to save workspaces"
        print("  ✓ Workspaces saved successfully")

        # Verify file exists
        assert storage.workspaces_file.exists(), "Workspaces file not created"
        print("  ✓ Workspaces file created")

        # Verify backup was created
        backup_file = storage.workspaces_file.with_suffix('.bak')
        # First save won't have backup, so save again
        storage.save_workspaces(workspaces)
        assert backup_file.exists(), "Backup file not created"
        print("  ✓ Backup file created on subsequent save")

        # Test load
        print("\n✓ Testing load_workspaces...")
        loaded_workspaces = storage.load_workspaces()
        assert loaded_workspaces is not None, "Failed to load workspaces"
        print("  ✓ Workspaces loaded successfully")

        # Verify loaded data
        assert len(loaded_workspaces) == 2, f"Expected 2 workspaces, got {len(loaded_workspaces)}"
        print("  ✓ Correct number of workspaces loaded")

        assert 1 in loaded_workspaces, "Workspace 1 not found"
        assert 2 in loaded_workspaces, "Workspace 2 not found"
        print("  ✓ All workspace IDs present")

        # Verify workspace 1 data
        ws1 = loaded_workspaces[1]
        assert ws1.workspace_id == "ws_001", f"Expected ws_001, got {ws1.workspace_id}"
        assert ws1.name == "Development", f"Expected 'Development', got {ws1.name}"
        assert len(ws1.sessions) == 1, f"Expected 1 session, got {len(ws1.sessions)}"
        assert ws1.description == "Development workspace"
        assert "dev" in ws1.tags and "coding" in ws1.tags
        print("  ✓ Workspace 1 data verified")

        # Verify session data
        loaded_session1 = ws1.sessions[0]
        assert loaded_session1.session_id == "test_session_1"
        assert loaded_session1.name == "Dev Session"
        assert loaded_session1.working_directory == "/tmp/dev"
        assert loaded_session1.command_count == 5
        assert loaded_session1.last_command == "ls -la"
        assert len(loaded_session1.output_snapshot) == 3
        print("  ✓ Session data verified")

        # Verify workspace 2 data
        ws2 = loaded_workspaces[2]
        assert ws2.workspace_id == "ws_002"
        assert ws2.name == "Testing"
        assert len(ws2.sessions) == 1
        print("  ✓ Workspace 2 data verified")

        # Test error handling - corrupted file
        print("\n✓ Testing error handling...")
        with open(storage.workspaces_file, 'w') as f:
            f.write("invalid json {{{")

        # Should recover from backup
        recovered_workspaces = storage.load_workspaces()
        assert recovered_workspaces is not None, "Failed to recover from backup"
        assert len(recovered_workspaces) == 2, "Backup recovery incomplete"
        print("  ✓ Successfully recovered from corrupted file using backup")

        # Test load non-existent file
        storage2 = SessionStorage(Path(tmpdir) / "nonexistent")
        result = storage2.load_workspaces()
        assert result is None, "Expected None for non-existent file"
        print("  ✓ Correctly handles non-existent workspaces file")

    print("\n✅ All workspace persistence tests passed!")


if __name__ == "__main__":
    test_workspace_persistence()
