#!/usr/bin/env python3
"""Test script for the automatic archiving system.

This script comprehensively tests:
1. Session archiving (compress and move to archive)
2. Session restoration (decompress and retrieve)
3. Archive index operations
4. Archive search functionality
5. Background archiving
6. Space savings calculations
"""

import sys
import time
import json
import tempfile
from pathlib import Path
from datetime import datetime, timedelta

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from claude_multi_terminal.archiver import SessionArchiver, ArchiveEntry, ArchiveIndex
from claude_multi_terminal.persistence.storage import SessionStorage
from claude_multi_terminal.persistence.session_state import SessionState


def print_header(title: str):
    """Print a formatted section header."""
    print(f"\n{'=' * 70}")
    print(f"  {title}")
    print('=' * 70)


def print_success(message: str):
    """Print a success message."""
    print(f"✓ {message}")


def print_error(message: str):
    """Print an error message."""
    print(f"✗ {message}")


def create_test_session(session_id: str, name: str, age_days: int) -> SessionState:
    """Create a test session with specified age.

    Args:
        session_id: Unique session ID
        name: Session name
        age_days: How many days old the session should be

    Returns:
        SessionState object
    """
    timestamp = time.time() - (age_days * 24 * 60 * 60)
    return SessionState(
        session_id=session_id,
        name=name,
        working_directory=f"/home/user/project_{name.lower()}",
        created_at=timestamp,
        modified_at=timestamp,
        command_count=10,
        last_command=f"echo 'test {name}'"
    )


def test_archive_index():
    """Test archive index functionality."""
    print_header("TEST 1: Archive Index")

    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)
        index_file = tmp_path / "test_index.json"

        # Create index
        index = ArchiveIndex(index_file)
        print_success("Created archive index")

        # Add entries
        entry1 = ArchiveEntry(
            session_id="session1",
            name="Test Session 1",
            archived_at=time.time(),
            original_timestamp=time.time() - 86400,
            archive_path="2024/01/123456_session1.json.gz",
            size_bytes=1024,
            original_size_bytes=10240,
            working_directory="/home/user/project1"
        )

        entry2 = ArchiveEntry(
            session_id="session2",
            name="Test Session 2",
            archived_at=time.time(),
            original_timestamp=time.time() - 172800,
            archive_path="2024/01/123457_session2.json.gz",
            size_bytes=2048,
            original_size_bytes=20480,
            working_directory="/home/user/project2",
            last_command="ls -la"
        )

        index.add_entry(entry1)
        index.add_entry(entry2)
        print_success(f"Added 2 entries to index")

        # Test retrieval
        retrieved = index.get_entry("session1")
        assert retrieved is not None
        assert retrieved.name == "Test Session 1"
        print_success("Retrieved entry by session_id")

        # Test search
        results = index.search(name="Session 1")
        assert len(results) == 1
        assert results[0].session_id == "session1"
        print_success("Searched by name")

        results = index.search(working_dir="project2")
        assert len(results) == 1
        assert results[0].session_id == "session2"
        print_success("Searched by working directory")

        # Test stats
        stats = index.get_stats()
        assert stats['total_sessions'] == 2
        assert stats['total_size_mb'] == round(3072 / (1024 * 1024), 2)
        assert stats['space_saved_mb'] == round(27648 / (1024 * 1024), 2)
        print_success(f"Stats calculated: {stats['total_sessions']} sessions, "
                     f"{stats['space_saved_mb']:.2f} MB saved")

        # Test persistence
        index2 = ArchiveIndex(index_file)
        assert len(index2.entries) == 2
        print_success("Index persisted and reloaded")


def test_session_archiving():
    """Test session archiving and restoration."""
    print_header("TEST 2: Session Archiving & Restoration")

    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)
        storage_dir = tmp_path / "storage"
        storage_dir.mkdir()
        history_dir = storage_dir / "history"
        history_dir.mkdir()

        # Create archiver
        archiver = SessionArchiver(storage_dir=storage_dir, archive_days=30)
        print_success("Created archiver")

        # Create test session
        session = create_test_session("test123", "TestSession", age_days=35)

        # Save session to history (simulate)
        history_file = history_dir / f"{int(session.modified_at)}_test123.json"
        with open(history_file, 'w') as f:
            json.dump({
                'session_id': session.session_id,
                'name': session.name,
                'working_directory': session.working_directory,
                'created_at': session.created_at,
                'modified_at': session.modified_at,
                'command_count': session.command_count,
                'last_command': session.last_command
            }, f)

        original_size = history_file.stat().st_size
        print_success(f"Created test session file ({original_size} bytes)")

        # Archive the session
        result = archiver.archive_session(session, history_file)
        assert result is True
        assert not history_file.exists()
        print_success("Session archived successfully")

        # Check index
        entry = archiver.index.get_entry("test123")
        assert entry is not None
        assert entry.name == "TestSession"
        compression_ratio = (1 - entry.size_bytes / entry.original_size_bytes) * 100
        print_success(f"Index updated: {compression_ratio:.1f}% compression")

        # Restore the session
        restored = archiver.restore_session("test123")
        assert restored is not None
        assert restored.session_id == "test123"
        assert restored.name == "TestSession"
        assert restored.working_directory == session.working_directory
        print_success("Session restored successfully")


def test_auto_archiving():
    """Test automatic archiving of old sessions."""
    print_header("TEST 3: Automatic Archiving")

    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)
        storage_dir = tmp_path / "storage"
        storage_dir.mkdir()
        history_dir = storage_dir / "history"
        history_dir.mkdir()

        # Create archiver with 7-day threshold
        archiver = SessionArchiver(storage_dir=storage_dir, archive_days=7)
        print_success("Created archiver (7-day threshold)")

        # Create mix of old and new sessions
        sessions = [
            create_test_session("old1", "OldSession1", age_days=10),
            create_test_session("old2", "OldSession2", age_days=15),
            create_test_session("new1", "NewSession1", age_days=3),
            create_test_session("new2", "NewSession2", age_days=5),
        ]

        # Save sessions to history
        for session in sessions:
            history_file = history_dir / f"{int(session.modified_at)}_{session.session_id}.json"
            with open(history_file, 'w') as f:
                json.dump({
                    'session_id': session.session_id,
                    'name': session.name,
                    'working_directory': session.working_directory,
                    'created_at': session.created_at,
                    'modified_at': session.modified_at,
                    'command_count': session.command_count,
                    'last_command': session.last_command
                }, f)

        print_success("Created 4 test sessions (2 old, 2 new)")

        # Run auto-archiving
        result = archiver.auto_archive_old_sessions()
        print_success(f"Auto-archiving complete:")
        print(f"  - Archived: {result['archived_count']} sessions")
        print(f"  - Failed: {result['failed_count']}")
        print(f"  - Space saved: {result['space_saved_mb']:.2f} MB")

        # Verify results
        assert result['archived_count'] == 2  # Should archive 2 old sessions
        assert result['failed_count'] == 0

        # Check that old sessions are archived
        assert archiver.index.get_entry("old1") is not None
        assert archiver.index.get_entry("old2") is not None
        print_success("Old sessions archived")

        # Check that new sessions remain in history
        new1_file = list(history_dir.glob("*_new1.json"))
        new2_file = list(history_dir.glob("*_new2.json"))
        assert len(new1_file) == 1
        assert len(new2_file) == 1
        print_success("New sessions remain in history")


def test_storage_integration():
    """Test integration with SessionStorage."""
    print_header("TEST 4: Storage Integration")

    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)

        # Create storage with archiving enabled
        storage = SessionStorage(
            storage_dir=tmp_path,
            lazy_loading=False,
            enable_auto_archive=True
        )
        print_success("Created SessionStorage with archiving enabled")

        # Get archiver
        archiver = storage.get_archiver()
        assert archiver is not None
        print_success("Retrieved archiver from storage")

        # Create old sessions in history
        for i in range(5):
            session = create_test_session(f"session{i}", f"Session{i}", age_days=40)
            history_file = storage.history_dir / f"{int(session.modified_at)}_session{i}.json"
            with open(history_file, 'w') as f:
                json.dump({
                    'session_id': session.session_id,
                    'name': session.name,
                    'working_directory': session.working_directory,
                    'created_at': session.created_at,
                    'modified_at': session.modified_at,
                    'command_count': session.command_count,
                    'last_command': session.last_command
                }, f)

        print_success("Created 5 old test sessions")

        # Trigger manual archiving
        result = storage.archive_old_sessions(days=30)
        print_success(f"Manual archiving via storage:")
        print(f"  - Archived: {result['archived_count']} sessions")
        print(f"  - Space saved: {result['space_saved_mb']:.2f} MB")

        assert result['archived_count'] == 5

        # Get stats
        stats = archiver.get_archive_stats()
        print_success(f"Archive stats: {stats['total_sessions']} sessions")


def test_archive_search():
    """Test archive search functionality."""
    print_header("TEST 5: Archive Search")

    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)
        storage_dir = tmp_path / "storage"
        storage_dir.mkdir()

        archiver = SessionArchiver(storage_dir=storage_dir)
        print_success("Created archiver")

        # Add various test entries to index
        base_time = time.time()
        entries = [
            ArchiveEntry(
                session_id=f"session{i}",
                name=f"BuildSession{i}" if i % 2 == 0 else f"TestSession{i}",
                archived_at=base_time - (i * 86400),
                original_timestamp=base_time - ((i + 30) * 86400),
                archive_path=f"2024/01/{int(base_time - (i * 86400))}_session{i}.json.gz",
                size_bytes=1024 * (i + 1),
                original_size_bytes=10240 * (i + 1),
                working_directory=f"/home/user/{'builds' if i % 2 == 0 else 'tests'}/project{i}"
            )
            for i in range(10)
        ]

        for entry in entries:
            archiver.index.add_entry(entry)

        print_success("Added 10 test entries to index")

        # Search by name
        results = archiver.index.search(name="Build")
        assert len(results) == 5
        print_success(f"Search by name: found {len(results)} 'Build' sessions")

        # Search by directory
        results = archiver.index.search(working_dir="tests")
        assert len(results) == 5
        print_success(f"Search by directory: found {len(results)} 'tests' sessions")

        # Search by date range (using > 5 days to get exactly 5 results)
        cutoff = base_time - (4.5 * 86400)  # 4.5 days to get sessions 0-4
        results = archiver.index.search(after_date=cutoff)
        assert len(results) == 5
        print_success(f"Search by date: found {len(results)} recent sessions")

        # Combined search
        results = archiver.index.search(name="Test", working_dir="tests", limit=3)
        assert len(results) == 3
        print_success(f"Combined search with limit: found {len(results)} sessions")


def run_all_tests():
    """Run all archiving system tests."""
    print("\n" + "=" * 70)
    print("  AUTOMATIC ARCHIVING SYSTEM - COMPREHENSIVE TEST SUITE")
    print("=" * 70)

    tests = [
        ("Archive Index", test_archive_index),
        ("Session Archiving & Restoration", test_session_archiving),
        ("Automatic Archiving", test_auto_archiving),
        ("Storage Integration", test_storage_integration),
        ("Archive Search", test_archive_search),
    ]

    passed = 0
    failed = 0

    for test_name, test_func in tests:
        try:
            test_func()
            passed += 1
        except AssertionError as e:
            failed += 1
            print_error(f"{test_name} FAILED: {e}")
        except Exception as e:
            failed += 1
            print_error(f"{test_name} ERROR: {e}")
            import traceback
            traceback.print_exc()

    # Print summary
    print_header("TEST SUMMARY")
    print(f"Total Tests: {passed + failed}")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")

    if failed == 0:
        print_success("\nAll tests passed! ✨")
        return 0
    else:
        print_error(f"\n{failed} test(s) failed")
        return 1


if __name__ == "__main__":
    sys.exit(run_all_tests())
