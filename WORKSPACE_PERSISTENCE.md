# Workspace Persistence Documentation

## Overview

The workspace persistence system allows saving and loading multiple workspace configurations, each containing a complete snapshot of sessions with their metadata, working directories, and command history.

## Architecture

### Components

1. **WorkspaceData** (`session_state.py`)
   - Dataclass representing a saved workspace
   - Contains workspace metadata and list of SessionState objects
   - Provides serialization methods: `to_dict()` and `from_dict()`

2. **SessionStorage** (`storage.py`)
   - File-based persistence layer
   - Methods: `save_workspaces()` and `load_workspaces()`
   - Storage location: `~/.multi-term/workspaces.json`
   - Atomic writes with backup creation

3. **ClaudeMultiTerminalApp** (`app.py`)
   - Integrates workspace persistence with app lifecycle
   - Loads workspaces on startup
   - Auto-saves on workspace switch (if AUTO_SAVE enabled)
   - Saves all workspaces on exit (if SAVE_ON_EXIT enabled)

### Data Structures

#### WorkspaceData
```python
@dataclass
class WorkspaceData:
    workspace_id: str           # Unique identifier
    name: str                   # Display name
    sessions: List[SessionState]  # List of session states
    created_at: float           # Unix timestamp
    modified_at: float          # Unix timestamp
    description: Optional[str]  # Optional description
    tags: List[str]            # Optional tags
```

#### Storage Format
Workspaces are stored as a JSON dictionary mapping workspace IDs to workspace data:
```json
{
  "1": {
    "workspace_id": "ws_abc123",
    "name": "Development",
    "sessions": [...],
    "created_at": 1234567890.0,
    "modified_at": 1234567890.0,
    "description": "Dev environment",
    "tags": ["dev", "coding"]
  },
  "2": {
    "workspace_id": "ws_xyz789",
    "name": "Testing",
    "sessions": [...],
    ...
  }
}
```

## Usage

### Saving Workspaces

Workspaces are saved automatically in three scenarios:

1. **On Workspace Switch** (if AUTO_SAVE enabled)
   - Current workspace saved before loading new one
   - Triggered by `action_manage_workspaces()`

2. **On Exit** (if SAVE_ON_EXIT enabled)
   - All workspaces persisted to disk
   - Triggered by `on_unmount()`

3. **Manual Save**
   - Call `storage.save_workspaces(workspaces)`

### Loading Workspaces

Workspaces are loaded automatically:

1. **On Startup**
   - `on_mount()` loads saved workspaces
   - Populates `app.workspaces` dictionary

2. **Manual Load**
   - Call `storage.load_workspaces()`
   - Returns `Dict[int, WorkspaceData]` or None

### Error Handling

The system handles errors gracefully:

1. **Corrupted Files**
   - Attempts to load from `.bak` backup
   - Archives corrupted file for debugging
   - Returns None if unrecoverable

2. **Missing Files**
   - Returns None (no error thrown)
   - App continues with empty workspaces

3. **Invalid Workspace Data**
   - Skips invalid entries
   - Continues loading valid workspaces
   - Logs warnings for debugging

## Implementation Details

### Atomic Writes

All writes use atomic operations to prevent corruption:

1. Write to temporary file (`.tmp`)
2. Flush and sync to disk
3. Atomic rename to target file
4. Create backup of previous version (`.bak`)

### Backup Strategy

- Backup created before each save
- Backup file: `workspaces.bak`
- Used for recovery on load failure
- Overwritten on each save (only one backup level)

### Auto-Save Integration

The `_save_current_workspace()` method:

1. Captures all session states from grid panes
2. Creates/updates WorkspaceData object
3. Stores in `app.workspaces` dictionary
4. Persists entire dictionary to disk

Auto-save is triggered by:
- `_restore_workspace_state()` - before switching workspaces
- `action_manage_workspaces()` - before opening workspace manager
- `on_unmount()` - on app exit

## Configuration

Workspace persistence respects these Config settings:

- `AUTO_SAVE`: Enable automatic saving on workspace switch
- `SAVE_ON_EXIT`: Enable saving all workspaces on exit

## File Locations

```
~/.multi-term/
├── workspace_state.json    # Current workspace state
├── workspaces.json         # All saved workspaces
├── workspaces.bak          # Backup of workspaces.json
├── workspaces.tmp          # Temporary file (transient)
└── history/                # Session history directory
```

## API Reference

### SessionStorage Methods

#### `save_workspaces(workspaces: Dict[int, WorkspaceData]) -> bool`
Save all workspaces to disk.

**Parameters:**
- `workspaces`: Dictionary mapping workspace IDs to WorkspaceData objects

**Returns:**
- `True` if save successful, `False` otherwise

**Example:**
```python
storage = SessionStorage()
workspaces = {
    1: WorkspaceData(...),
    2: WorkspaceData(...)
}
success = storage.save_workspaces(workspaces)
```

#### `load_workspaces() -> Optional[Dict[int, WorkspaceData]]`
Load all workspaces from disk.

**Returns:**
- Dictionary of workspaces if loaded successfully
- `None` if file doesn't exist or is unrecoverable

**Example:**
```python
storage = SessionStorage()
workspaces = storage.load_workspaces()
if workspaces:
    print(f"Loaded {len(workspaces)} workspace(s)")
```

### WorkspaceData Methods

#### `to_dict() -> dict`
Convert workspace data to dictionary for JSON serialization.

**Returns:**
- Dictionary representation suitable for JSON storage

#### `from_dict(data: dict) -> WorkspaceData` (classmethod)
Reconstruct workspace data from dictionary.

**Parameters:**
- `data`: Dictionary representation of workspace data

**Returns:**
- WorkspaceData object

**Raises:**
- `KeyError`: If required fields are missing
- `TypeError`: If field types are incorrect

## Testing

Run the test suite:
```bash
cd /Users/wallonwalusayi/claude-multi-terminal
source venv/bin/activate
python test_workspace_persistence.py
```

Tests cover:
- Save and load operations
- Backup creation and recovery
- Corrupted file handling
- Non-existent file handling
- Data integrity verification

## Future Enhancements

Potential improvements:

1. **Workspace Import/Export**
   - Export workspace to standalone file
   - Import workspace from file
   - Share workspaces between users

2. **Workspace Templates**
   - Pre-configured workspace templates
   - Quick workspace creation from templates

3. **Workspace Tagging**
   - Better workspace organization
   - Filter/search by tags

4. **Workspace History**
   - Track workspace changes over time
   - Rollback to previous versions

5. **Workspace Metadata**
   - Last accessed timestamp
   - Usage statistics
   - Custom metadata fields

## Troubleshooting

### Workspaces not saving
- Check `Config.AUTO_SAVE` is True
- Verify write permissions for `~/.multi-term/`
- Check logs for errors

### Workspaces not loading
- Check if `workspaces.json` exists
- Try loading from backup: `workspaces.bak`
- Check file format with `cat ~/.multi-term/workspaces.json | jq .`

### Corrupted workspace file
- System automatically tries backup recovery
- Check for archived corrupted files: `corrupted_*_workspaces.json`
- Manual recovery: rename `.bak` to `.json`

## Performance Considerations

- Workspace file size grows with number of workspaces and sessions
- Each workspace contains full session snapshots (50 lines of output)
- Atomic writes ensure data integrity but require 2x disk space temporarily
- Load time scales linearly with number of workspaces

Recommended limits:
- Max workspaces: 50-100
- Max sessions per workspace: 10-20
- Total file size: < 10 MB

## Security

- Workspace files stored in user's home directory
- File permissions: 0644 (user read/write, group/others read)
- No sensitive data stored (passwords, tokens, etc.)
- Output snapshots limited to 50 lines per session
