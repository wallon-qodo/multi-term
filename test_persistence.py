#!/usr/bin/env python3
"""Test script for the persistence module."""

import sys
import time
import tempfile
import shutil
from pathlib import Path

# Add project to path
sys.path.insert(0, str(Path(__file__).parent))

# Import persistence module components
from claude_multi_terminal.persistence.session_state import SessionState, WorkspaceState
from claude_multi_terminal.persistence.storage import SessionStorage


def test_session_state():
    """Test SessionState dataclass."""
    print('\n1. Testing SessionState...')

    session = SessionState(
        session_id='test-123',
        name='Test Session',
        working_directory='/tmp',
        created_at=time.time(),
        modified_at=time.time(),
        command_count=5,
        last_command='ls -la'
    )

    assert session.session_id == 'test-123'
    assert session.name == 'Test Session'
    assert session.command_count == 5
    assert isinstance(session.output_snapshot, list)
    assert len(session.output_snapshot) == 0

    print(f'✓ SessionState created: {session.name}')
    print(f'  - ID: {session.session_id}')
    print(f'  - Working dir: {session.working_directory}')
    print(f'  - Commands: {session.command_count}')
    print(f'  - Output snapshot: {len(session.output_snapshot)} lines')

    return session


def test_workspace_state(session):
    """Test WorkspaceState dataclass."""
    print('\n2. Testing WorkspaceState...')

    workspace = WorkspaceState()
    workspace.sessions.append(session)
    workspace.active_session_id = session.session_id

    assert len(workspace.sessions) == 1
    assert workspace.active_session_id == session.session_id
    assert workspace.version == "1.0"

    print(f'✓ WorkspaceState created')
    print(f'  - Sessions: {len(workspace.sessions)}')
    print(f'  - Active: {workspace.active_session_id}')
    print(f'  - Version: {workspace.version}')

    return workspace


def test_json_serialization(workspace):
    """Test JSON serialization and deserialization."""
    print('\n3. Testing JSON serialization...')

    json_str = workspace.to_json()
    assert isinstance(json_str, str)
    assert len(json_str) > 0
    assert 'test-123' in json_str

    print(f'✓ Serialized to JSON ({len(json_str)} bytes)')

    print('\n4. Testing JSON deserialization...')

    restored = WorkspaceState.from_json(json_str)
    assert len(restored.sessions) == 1
    assert restored.sessions[0].session_id == 'test-123'
    assert restored.sessions[0].name == 'Test Session'
    assert restored.active_session_id == 'test-123'

    print(f'✓ Deserialized from JSON')
    print(f'  - Sessions: {len(restored.sessions)}')
    print(f'  - Session name: {restored.sessions[0].name}')
    print(f'  - Session ID: {restored.sessions[0].session_id}')


def test_storage(workspace, session):
    """Test SessionStorage functionality."""
    print('\n5. Testing SessionStorage...')

    temp_dir = Path(tempfile.mkdtemp())

    try:
        storage = SessionStorage(storage_dir=temp_dir)
        assert storage.storage_dir == temp_dir
        assert storage.state_file.exists() is False  # Not created yet
        assert storage.history_dir.exists() is True  # Created during init

        print(f'✓ SessionStorage initialized')
        print(f'  - Storage dir: {temp_dir}')
        print(f'  - State file: {storage.state_file.name}')
        print(f'  - History dir: {storage.history_dir.name}')

        # Test save state
        print('\n6. Testing save_state()...')
        result = storage.save_state(workspace)
        assert result is True
        assert storage.state_file.exists() is True
        print('✓ Workspace saved successfully')

        # Test load state
        print('\n7. Testing load_state()...')
        loaded = storage.load_state()
        assert loaded is not None
        assert len(loaded.sessions) == 1
        assert loaded.sessions[0].name == 'Test Session'
        print(f'✓ Workspace loaded successfully')
        print(f'  - Sessions: {len(loaded.sessions)}')
        print(f'  - First session: {loaded.sessions[0].name}')

        # Test save to history
        print('\n8. Testing save_session_to_history()...')
        result = storage.save_session_to_history(session)
        assert result is True
        print('✓ Session saved to history')

        # Test load history
        print('\n9. Testing load_session_history()...')
        history = storage.load_session_history(limit=10)
        assert len(history) == 1
        assert history[0].session_id == 'test-123'
        print(f'✓ Loaded {len(history)} session(s) from history')
        if history:
            print(f'  - First: {history[0].name}')

        # Test storage stats
        print('\n10. Testing get_storage_stats()...')
        stats = storage.get_storage_stats()
        assert stats['total_sessions'] == 1
        assert stats['storage_size_mb'] > 0
        print(f'✓ Storage stats retrieved')
        print(f'  - Total sessions: {stats["total_sessions"]}')
        print(f'  - Size: {stats["storage_size_mb"]} MB')

        # Test delete
        print('\n11. Testing delete_session_from_history()...')
        result = storage.delete_session_from_history(session.session_id)
        assert result is True

        # Verify deletion
        history = storage.load_session_history(limit=10)
        assert len(history) == 0
        print('✓ Session deleted from history')

        # Test clear old history
        print('\n12. Testing clear_old_history()...')
        deleted = storage.clear_old_history(days=30)
        assert deleted == 0  # Nothing old enough to delete
        print(f'✓ Cleared {deleted} old session(s)')

    finally:
        shutil.rmtree(temp_dir)
        print(f'\n✓ Cleaned up temp directory')


def main():
    """Run all tests."""
    print('Testing Persistence Module')
    print('=' * 50)

    try:
        session = test_session_state()
        workspace = test_workspace_state(session)
        test_json_serialization(workspace)
        test_storage(workspace, session)

        print('\n' + '=' * 50)
        print('✅ All persistence module tests passed!')
        return 0

    except AssertionError as e:
        print(f'\n❌ Test failed: {e}')
        return 1
    except Exception as e:
        print(f'\n❌ Unexpected error: {e}')
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())
