"""Tests for File Watcher integration."""

import pytest
import time
from pathlib import Path
from claude_multi_terminal.integrations.file_watcher import FileWatcher, FileChange


@pytest.fixture
def watch_dir(tmp_path):
    """Create a temporary directory for watching."""
    watch_path = tmp_path / "watch_test"
    watch_path.mkdir()
    return watch_path


@pytest.fixture
def watcher(watch_dir):
    """Create a FileWatcher instance."""
    watcher = FileWatcher(watch_path=watch_dir, poll_interval=0.1)
    yield watcher
    watcher.stop()


def test_file_watcher_init(watch_dir):
    """Test FileWatcher initialization."""
    watcher = FileWatcher(watch_path=watch_dir)
    assert watcher.watch_path == watch_dir
    assert not watcher._running


def test_file_watcher_start_stop(watcher):
    """Test starting and stopping watcher."""
    watcher.start()
    assert watcher._running

    time.sleep(0.2)

    watcher.stop()
    assert not watcher._running


def test_detect_new_file(watcher, watch_dir):
    """Test detecting new file creation."""
    changes = []

    def on_change(change):
        changes.append(change)

    watcher.add_listener(on_change)
    watcher.start()

    # Wait for initial scan
    time.sleep(0.3)

    # Create a new file
    new_file = watch_dir / "test.txt"
    new_file.write_text("Test content")

    # Wait for detection
    time.sleep(0.3)

    watcher.stop()

    # Check changes
    assert len(changes) > 0
    assert any(c.change_type == "created" and c.path == new_file for c in changes)


def test_detect_modified_file(watcher, watch_dir):
    """Test detecting file modification."""
    # Create initial file
    test_file = watch_dir / "test.txt"
    test_file.write_text("Initial content")

    changes = []

    def on_change(change):
        changes.append(change)

    watcher.add_listener(on_change)
    watcher.start()

    # Wait for initial scan
    time.sleep(0.3)
    changes.clear()

    # Modify file
    time.sleep(0.1)  # Ensure mtime changes
    test_file.write_text("Modified content")

    # Wait for detection
    time.sleep(0.3)

    watcher.stop()

    # Check changes
    assert any(c.change_type == "modified" and c.path == test_file for c in changes)


def test_detect_deleted_file(watcher, watch_dir):
    """Test detecting file deletion."""
    # Create initial file
    test_file = watch_dir / "test.txt"
    test_file.write_text("Test content")

    changes = []

    def on_change(change):
        changes.append(change)

    watcher.add_listener(on_change)
    watcher.start()

    # Wait for initial scan
    time.sleep(0.3)
    changes.clear()

    # Delete file
    test_file.unlink()

    # Wait for detection
    time.sleep(0.3)

    watcher.stop()

    # Check changes
    assert any(c.change_type == "deleted" and c.path == test_file for c in changes)


def test_ignore_patterns(watch_dir):
    """Test ignoring files based on patterns."""
    watcher = FileWatcher(watch_path=watch_dir, poll_interval=0.1)

    # Create files that should be ignored
    pyc_file = watch_dir / "test.pyc"
    pyc_file.write_text("bytecode")

    log_file = watch_dir / "test.log"
    log_file.write_text("logs")

    # Create file that should not be ignored
    py_file = watch_dir / "test.py"
    py_file.write_text("code")

    assert watcher._should_ignore(pyc_file)
    assert watcher._should_ignore(log_file)
    assert not watcher._should_ignore(py_file)


def test_get_changes(watcher, watch_dir):
    """Test getting pending changes."""
    watcher.start()
    time.sleep(0.2)

    # Create a file
    new_file = watch_dir / "test.txt"
    new_file.write_text("Test")

    time.sleep(0.2)

    changes = watcher.get_changes()
    assert len(changes) > 0

    # Queue should be cleared
    changes2 = watcher.get_changes()
    assert len(changes2) == 0

    watcher.stop()


def test_get_history(watcher, watch_dir):
    """Test getting change history."""
    watcher.start()
    time.sleep(0.2)

    # Create multiple files
    for i in range(3):
        new_file = watch_dir / f"test_{i}.txt"
        new_file.write_text(f"Content {i}")
        time.sleep(0.2)

    watcher.stop()

    history = watcher.get_history()
    assert len(history) >= 3

    # Test count parameter
    recent = watcher.get_history(count=2)
    assert len(recent) == 2


def test_get_statistics(watcher, watch_dir):
    """Test getting watcher statistics."""
    watcher.start()
    time.sleep(0.2)

    # Create and modify files
    test_file = watch_dir / "test.txt"
    test_file.write_text("Test")
    time.sleep(0.2)

    test_file.write_text("Modified")
    time.sleep(0.2)

    watcher.stop()

    stats = watcher.get_statistics()
    assert "watched_files" in stats
    assert "total_changes" in stats
    assert "change_types" in stats
    assert stats["running"] is False


def test_suggest_files(watcher, watch_dir):
    """Test file suggestion."""
    # Create test files
    (watch_dir / "module1.py").write_text("code")
    (watch_dir / "module2.py").write_text("code")
    (watch_dir / "test_module.py").write_text("test")

    watcher.start()
    time.sleep(0.3)
    watcher.stop()

    # Test suggestions
    suggestions = watcher.suggest_files("module")
    assert len(suggestions) > 0
    assert all("module" in str(p).lower() for p in suggestions)

    # Test limit
    suggestions = watcher.suggest_files("module", limit=2)
    assert len(suggestions) <= 2


def test_get_active_files(watcher, watch_dir):
    """Test getting recently active files."""
    watcher.start()
    time.sleep(0.2)

    # Create files
    file1 = watch_dir / "file1.txt"
    file1.write_text("content1")
    time.sleep(0.2)

    file2 = watch_dir / "file2.txt"
    file2.write_text("content2")
    time.sleep(0.2)

    watcher.stop()

    active = watcher.get_active_files(since_minutes=1)
    assert len(active) >= 2
    assert file1 in active
    assert file2 in active


def test_context_manager(watch_dir):
    """Test using FileWatcher as context manager."""
    with FileWatcher(watch_path=watch_dir, poll_interval=0.1) as watcher:
        assert watcher._running
        time.sleep(0.2)

    # Should be stopped after exiting context
    assert not watcher._running


def test_multiple_listeners(watcher, watch_dir):
    """Test multiple event listeners."""
    changes1 = []
    changes2 = []

    def listener1(change):
        changes1.append(change)

    def listener2(change):
        changes2.append(change)

    watcher.add_listener(listener1)
    watcher.add_listener(listener2)
    watcher.start()

    time.sleep(0.2)

    # Create a file
    new_file = watch_dir / "test.txt"
    new_file.write_text("Test")

    time.sleep(0.2)
    watcher.stop()

    # Both listeners should receive the change
    assert len(changes1) > 0
    assert len(changes2) > 0
    assert len(changes1) == len(changes2)


def test_remove_listener(watcher, watch_dir):
    """Test removing event listener."""
    changes = []

    def listener(change):
        changes.append(change)

    watcher.add_listener(listener)
    watcher.start()
    time.sleep(0.2)

    # Create file
    (watch_dir / "test1.txt").write_text("Test")
    time.sleep(0.2)

    count1 = len(changes)

    # Remove listener
    watcher.remove_listener(listener)

    # Create another file
    (watch_dir / "test2.txt").write_text("Test")
    time.sleep(0.2)

    watcher.stop()

    # Count should not have increased
    assert len(changes) == count1
