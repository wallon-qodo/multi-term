# Automatic Session Archiving System

## Overview

The automatic archiving system helps manage storage by automatically compressing and archiving old sessions. This keeps the active history directory lean while preserving all historical data in compressed archives.

## Features

- **Automatic archiving** - Sessions older than 30 days (configurable) are automatically archived
- **Gzip compression** - Typically achieves 5-10x space reduction
- **Background operation** - Archiving runs in background, non-blocking
- **Easy restoration** - Restore archived sessions with simple API
- **Fast search** - Index-based search without decompressing archives
- **Organized storage** - Archives organized by year/month for easy management

## Architecture

```
~/.multi-term/
├── history/                          # Active session history (recent)
│   └── {timestamp}_{id}.json
├── archive/                          # Archived sessions (compressed)
│   ├── 2024/
│   │   ├── 01/
│   │   │   └── {timestamp}_{id}.json.gz
│   │   └── 02/
│   │       └── {timestamp}_{id}.json.gz
│   └── 2025/
│       └── ...
└── archive_index.json               # Fast lookup index
```

## Usage

### Automatic Archiving (Recommended)

Archiving is enabled by default and runs automatically in the background:

```python
from claude_multi_terminal.persistence.storage import SessionStorage

# Archiving is enabled by default
storage = SessionStorage()

# Background archiving runs every 24 hours automatically
# No manual intervention needed!
```

### Manual Archiving

Trigger manual archiving when needed:

```python
# Archive sessions older than 30 days (default)
result = storage.archive_old_sessions()
print(f"Archived {result['archived_count']} sessions")
print(f"Saved {result['space_saved_mb']:.2f} MB")

# Archive sessions older than custom threshold
result = storage.archive_old_sessions(days=7)
```

### Accessing the Archiver

Get direct access to the archiver for advanced operations:

```python
archiver = storage.get_archiver()

# Get archive statistics
stats = archiver.get_archive_stats()
print(f"Total archived: {stats['total_sessions']} sessions")
print(f"Total size: {stats['total_size_mb']:.2f} MB")
print(f"Space saved: {stats['space_saved_mb']:.2f} MB")
```

### Restoring Archived Sessions

```python
archiver = storage.get_archiver()

# Restore by session ID
session = archiver.restore_session("session_abc123")
if session:
    print(f"Restored: {session.name}")
    print(f"Working dir: {session.working_directory}")
    print(f"Last command: {session.last_command}")
```

### Searching Archives

```python
archiver = storage.get_archiver()

# Search by name
results = archiver.index.search(name="build")
for entry in results:
    print(f"{entry.name}: {entry.working_directory}")

# Search by working directory
results = archiver.index.search(working_dir="/home/user/project")

# Search by date range
import time
last_week = time.time() - (7 * 24 * 60 * 60)
results = archiver.index.search(after_date=last_week)

# Combined search with limit
results = archiver.index.search(
    name="test",
    working_dir="/home/user",
    after_date=last_week,
    limit=10
)
```

## Using the Archive Browser Widget

The archive browser provides a visual interface for managing archives:

```python
from claude_multi_terminal.widgets.archive_browser import ArchiveBrowser

def on_restore(session):
    """Called when user restores a session."""
    print(f"Restored: {session.name}")
    # Add session back to active sessions

# Create browser
archiver = storage.get_archiver()
browser = ArchiveBrowser(
    archiver=archiver,
    on_restore=on_restore
)

# Mount in your app
await self.mount(browser)
```

Browser features:
- Search by name or directory
- View compression statistics
- One-click restore
- Keyboard shortcuts (`r` to restore, `/` to search, `esc` to close)

## Configuration

### Changing Archive Threshold

```python
from claude_multi_terminal.archiver import SessionArchiver

# Create archiver with custom threshold
archiver = SessionArchiver(
    storage_dir=storage_dir,
    archive_days=14  # Archive after 14 days instead of 30
)
```

### Changing Background Interval

```python
# Start background archiving with custom interval
archiver.start_background_archiving(interval_hours=6)  # Run every 6 hours

# Stop background archiving
archiver.stop_background_archiving()
```

### Disabling Auto-Archiving

```python
# Disable automatic archiving
storage = SessionStorage(enable_auto_archive=False)

# Or stop background archiving on existing storage
archiver = storage.get_archiver()
if archiver:
    archiver.stop_background_archiving()
```

## Performance Benefits

### Space Savings

Typical compression ratios:
- **Session files**: 85-90% reduction (10x smaller)
- **Large sessions**: 90-95% reduction (15-20x smaller)
- **Overall**: ~5-10x space savings on average

Example:
```
Before archiving: 1,000 sessions × 50 KB = 50 MB
After archiving:  1,000 sessions × 5 KB = 5 MB
Space saved: 45 MB (90%)
```

### Performance Improvements

- **Faster startup**: Active history contains only recent sessions
- **Faster searches**: Index-based lookups without decompression
- **Lower memory**: Fewer active sessions to load
- **Better organization**: Year/month structure for easy browsing

## Archive Index Format

The index provides fast lookups without decompressing archives:

```json
{
  "session_abc123": {
    "session_id": "session_abc123",
    "name": "Build Session",
    "archived_at": 1707000000.0,
    "original_timestamp": 1704000000.0,
    "archive_path": "2024/01/1704000000_session_abc123.json.gz",
    "size_bytes": 5120,
    "original_size_bytes": 51200,
    "working_directory": "/home/user/project",
    "last_command": "make build"
  }
}
```

## API Reference

### SessionArchiver

**Constructor:**
```python
SessionArchiver(storage_dir=None, archive_days=30)
```

**Methods:**

- `archive_session(session_state, history_file)` - Archive a single session
- `restore_session(session_id)` - Restore archived session
- `auto_archive_old_sessions(progress_callback=None)` - Archive all old sessions
- `start_background_archiving(interval_hours=24)` - Start background worker
- `stop_background_archiving()` - Stop background worker
- `get_archive_stats()` - Get statistics

### ArchiveIndex

**Methods:**

- `add_entry(entry)` - Add archive entry to index
- `remove_entry(session_id)` - Remove entry from index
- `get_entry(session_id)` - Get entry by ID
- `search(name, working_dir, after_date, before_date, limit)` - Search archives
- `get_stats()` - Get index statistics

### SessionStorage Integration

**Methods:**

- `get_archiver()` - Get archiver instance
- `archive_old_sessions(days=None)` - Manually trigger archiving

## Troubleshooting

### Archives Not Being Created

Check if archiving is enabled:
```python
archiver = storage.get_archiver()
if archiver:
    print("Archiving enabled")
else:
    print("Archiving disabled")
```

Verify background worker is running:
```python
if archiver._background_thread and archiver._background_thread.is_alive():
    print("Background archiving is running")
else:
    print("Background archiving is not running")
```

### Slow Archive Searches

The index should make searches fast. If searches are slow:
1. Check index file exists: `~/.multi-term/archive_index.json`
2. Rebuild index if corrupted (delete file, restart app)
3. Reduce search result limit

### Disk Space Not Freed

After archiving, old history files should be deleted. If not:
1. Check logs for archiving errors
2. Verify file permissions on history directory
3. Manually trigger archiving and check results

### Restoring Sessions Fails

If restoration fails:
1. Verify archive file exists at the path in index
2. Check file is valid gzip: `gzip -t <file>`
3. Check file permissions
4. Try re-archiving the session

## Best Practices

1. **Keep default threshold** - 30 days balances history access and storage
2. **Monitor space savings** - Check stats periodically: `archiver.get_archive_stats()`
3. **Use background archiving** - Let it run automatically, don't micromanage
4. **Search before restore** - Use index search to find sessions efficiently
5. **Backup archives** - Archives are compressed but not encrypted; back up important data

## Examples

### Complete Archiving Workflow

```python
from claude_multi_terminal.persistence.storage import SessionStorage

# Initialize with archiving enabled (default)
storage = SessionStorage()

# Get archiver for manual operations
archiver = storage.get_archiver()

# Check current state
stats = archiver.get_archive_stats()
print(f"Currently archived: {stats['total_sessions']} sessions")
print(f"Space saved: {stats['space_saved_mb']:.2f} MB")

# Manually archive old sessions (optional, happens automatically)
result = storage.archive_old_sessions(days=30)
print(f"Archived: {result['archived_count']} sessions")
print(f"Failed: {result['failed_count']}")
print(f"Saved: {result['space_saved_mb']:.2f} MB")

# Search archives
recent_builds = archiver.index.search(name="build", limit=10)
for entry in recent_builds:
    print(f"- {entry.name}: {entry.working_directory}")

# Restore a specific session
session = archiver.restore_session("session_abc123")
if session:
    print(f"Restored: {session.name}")
    # Use the restored session...
```

## Implementation Details

### Compression

- Uses Python's `gzip` module with default compression (level 9)
- Text-based JSON compresses very well (~85-90%)
- Decompression is fast enough for interactive use

### Background Threading

- Runs in daemon thread (won't block app exit)
- Configurable interval (default: 24 hours)
- Graceful shutdown with timeout
- Thread-safe operations with locks

### File Organization

Archives organized by date for:
- Easier manual browsing
- Better filesystem performance
- Natural chronological grouping
- Simpler backup strategies

### Error Handling

- Corrupted archives: Logged but don't stop processing
- Failed archiving: Original file preserved
- Index corruption: Falls back to rebuilding
- Missing archives: Gracefully handled on restore

## Testing

Run the comprehensive test suite:

```bash
python3 test_archiving_system.py
```

Tests cover:
- Archive index operations
- Session archiving and restoration
- Automatic archiving
- Storage integration
- Archive search functionality

## Future Enhancements

Potential improvements:
- Archive encryption for sensitive data
- Configurable compression levels
- Archive export/import
- Archive cloud sync
- Archive analytics and visualization
- Automatic archive cleanup (delete very old archives)
