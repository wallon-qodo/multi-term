#!/usr/bin/env python3
"""Direct test script for the persistence module (bypasses package __init__)."""

import sys
import time
import tempfile
import shutil
import importlib.util
from pathlib import Path

# Get the paths to the persistence modules
base_dir = Path(__file__).parent
session_state_path = base_dir / 'claude_multi_terminal' / 'persistence' / 'session_state.py'
storage_path = base_dir / 'claude_multi_terminal' / 'persistence' / 'storage.py'

# Load session_state module
spec = importlib.util.spec_from_file_location("session_state", session_state_path)
session_state = importlib.util.module_from_spec(spec)
spec.loader.exec_module(session_state)

# Load storage module (manually set session_state in its namespace)
spec = importlib.util.spec_from_file_location("storage", storage_path)
storage_module = importlib.util.module_from_spec(spec)

# Inject session_state classes into storage module's namespace to resolve relative imports
sys.modules['claude_multi_terminal.persistence.session_state'] = session_state
storage_module.__dict__['WorkspaceState'] = session_state.WorkspaceState
storage_module.__dict__['SessionState'] = session_state.SessionState

spec.loader.exec_module(storage_module)

# Extract classes
SessionState = session_state.SessionState
WorkspaceState = session_state.WorkspaceState
SessionStorage = storage_module.SessionStorage


def main():
    """Run all tests."""
    print('Testing Persistence Module')
    print('=' * 50)

    # Test SessionState
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
    print(f'✓ SessionState created: {session.name}')
    print(f'  - ID: {session.session_id}')
    print(f'  - Commands: {session.command_count}')
    print(f'  - Output snapshot: {len(session.output_snapshot)} lines')

    # Test WorkspaceState
    print('\n2. Testing WorkspaceState...')
    workspace = WorkspaceState()
    workspace.sessions.append(session)
    workspace.active_session_id = session.session_id
    print(f'✓ WorkspaceState created')
    print(f'  - Sessions: {len(workspace.sessions)}')
    print(f'  - Active: {workspace.active_session_id}')

    # Test JSON serialization
    print('\n3. Testing JSON serialization...')
    json_str = workspace.to_json()
    print(f'✓ Serialized to JSON ({len(json_str)} bytes)')

    # Test JSON deserialization
    print('\n4. Testing JSON deserialization...')
    restored = WorkspaceState.from_json(json_str)
    print(f'✓ Deserialized: {restored.sessions[0].name}')

    # Test SessionStorage
    print('\n5. Testing SessionStorage...')
    temp_dir = Path(tempfile.mkdtemp())

    try:
        storage = SessionStorage(storage_dir=temp_dir)
        print(f'✓ Storage initialized at {temp_dir}')

        # Save state
        print('\n6. Testing save_state()...')
        storage.save_state(workspace)
        print('✓ Workspace saved')

        # Load state
        print('\n7. Testing load_state()...')
        loaded = storage.load_state()
        print(f'✓ Loaded {len(loaded.sessions)} session(s)')

        # Save to history
        print('\n8. Testing save_session_to_history()...')
        storage.save_session_to_history(session)
        print('✓ Saved to history')

        # Load history
        print('\n9. Testing load_session_history()...')
        history = storage.load_session_history(limit=10)
        print(f'✓ Loaded {len(history)} from history')

        # Storage stats
        print('\n10. Testing get_storage_stats()...')
        stats = storage.get_storage_stats()
        print(f'✓ Stats: {stats["total_sessions"]} sessions, {stats["storage_size_mb"]} MB')

        # Delete
        print('\n11. Testing delete_session_from_history()...')
        storage.delete_session_from_history(session.session_id)
        print('✓ Deleted from history')

        # Clear old
        print('\n12. Testing clear_old_history()...')
        deleted = storage.clear_old_history(days=30)
        print(f'✓ Cleared {deleted} old sessions')

    finally:
        shutil.rmtree(temp_dir)
        print(f'\n✓ Cleaned up temp directory')

    print('\n' + '=' * 50)
    print('✅ All persistence module tests passed!')


if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print(f'\n❌ Error: {e}')
        import traceback
        traceback.print_exc()
        sys.exit(1)
