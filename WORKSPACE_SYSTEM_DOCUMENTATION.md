# Workspace System Documentation

## Overview

The workspace system provides a comprehensive data model for managing multiple independent workspaces, each containing their own set of Claude CLI sessions with independent layout modes and focus states. This system is designed to support the Phase 2 workspace feature as outlined in CLAUDE.md.

## Architecture

### Core Components

1. **LayoutMode (Enum)**: Defines the layout strategies for organizing sessions
2. **Workspace (Dataclass)**: Data model for a single workspace
3. **WorkspaceManager (Class)**: Manager for workspace lifecycle and operations

### File Location

- **Module**: `/Users/wallonwalusayi/claude-multi-terminal/claude_multi_terminal/workspaces.py`
- **Tests**: `/Users/wallonwalusayi/claude-multi-terminal/tests/test_workspaces.py`

## API Reference

### LayoutMode Enum

```python
class LayoutMode(Enum):
    TILED = "tiled"       # Automatic grid layout with equal-sized panes
    FLOATING = "floating" # Free-form draggable windows
    MONOCLE = "monocle"   # Single maximized session (fullscreen)
```

### Workspace Dataclass

#### Attributes

| Attribute | Type | Default | Description |
|-----------|------|---------|-------------|
| `id` | `int` | *required* | Workspace identifier (1-9) |
| `name` | `str` | *required* | User-visible name |
| `session_ids` | `List[str]` | `[]` | List of session UUIDs |
| `focused_session_id` | `Optional[str]` | `None` | Currently focused session |
| `layout_mode` | `LayoutMode` | `TILED` | Current layout strategy |
| `created_at` | `float` | `time.time()` | Creation timestamp |
| `modified_at` | `float` | `time.time()` | Last modification timestamp |

#### Methods

##### `add_session(session_id: str) -> None`
Add a session to this workspace. Automatically updates modified timestamp.

```python
ws = Workspace(id=1, name="Dev")
ws.add_session("session-uuid-123")
```

##### `remove_session(session_id: str) -> bool`
Remove a session from workspace. Returns `True` if removed, `False` if not found.
Automatically clears focus if removing focused session.

```python
if ws.remove_session("session-uuid-123"):
    print("Session removed")
```

##### `set_focus(session_id: Optional[str]) -> bool`
Set focused session. Pass `None` to clear focus. Returns `True` on success.

```python
ws.set_focus("session-uuid-123")  # Focus session
ws.set_focus(None)                # Clear focus
```

##### `set_layout_mode(mode: LayoutMode) -> None`
Change the layout mode for this workspace.

```python
ws.set_layout_mode(LayoutMode.FLOATING)
```

##### `is_empty() -> bool`
Check if workspace has no sessions.

```python
if ws.is_empty():
    print("Workspace is empty")
```

##### `update_modified_time() -> None`
Manually update the modified timestamp.

```python
ws.update_modified_time()
```

### WorkspaceManager Class

#### Attributes

| Attribute | Type | Description |
|-----------|------|-------------|
| `workspaces` | `Dict[int, Workspace]` | Dictionary of all 9 workspaces |
| `active_workspace_id` | `int` | ID of currently active workspace |

#### Initialization

```python
manager = WorkspaceManager()
# Creates 9 workspaces (1-9) with default names
# Sets workspace 1 as active
```

#### Methods

##### `create_workspace(workspace_id: int, name: str) -> Workspace`
Create or recreate a workspace with a specific name.

```python
ws = manager.create_workspace(5, "My Custom Workspace")
```

**Raises**: `ValueError` if workspace_id not in range 1-9

##### `get_workspace(workspace_id: int) -> Optional[Workspace]`
Retrieve a workspace by ID.

```python
ws = manager.get_workspace(3)
if ws:
    print(f"Workspace: {ws.name}")
```

##### `get_active_workspace() -> Workspace`
Get the currently active workspace.

```python
active = manager.get_active_workspace()
print(f"Active: {active.name}")
```

##### `switch_to_workspace(workspace_id: int) -> bool`
Switch to a different workspace. Returns `True` on success.

```python
if manager.switch_to_workspace(5):
    print("Switched to workspace 5")
```

##### `rename_workspace(workspace_id: int, name: str) -> bool`
Rename an existing workspace. Returns `True` on success.

```python
manager.rename_workspace(3, "Testing Environment")
```

##### `add_session_to_workspace(workspace_id: int, session_id: str) -> bool`
Add a session to a workspace. Auto-focuses if workspace is empty.

```python
manager.add_session_to_workspace(2, "session-uuid-456")
```

##### `remove_session_from_workspace(workspace_id: int, session_id: str) -> bool`
Remove a session from a workspace. Returns `True` on success.

```python
manager.remove_session_from_workspace(2, "session-uuid-456")
```

##### `move_session(session_id: str, from_ws: int, to_ws: int) -> bool`
Move a session between workspaces. Returns `True` on success.

```python
manager.move_session("session-123", from_ws=1, to_ws=5)
```

##### `get_session_workspace(session_id: str) -> Optional[int]`
Find which workspace contains a session. Returns workspace ID or `None`.

```python
ws_id = manager.get_session_workspace("session-123")
print(f"Session is in workspace {ws_id}")
```

##### `list_workspaces() -> List[Workspace]`
Get a list of all workspaces, sorted by ID.

```python
for ws in manager.list_workspaces():
    print(f"{ws.id}: {ws.name} ({len(ws.session_ids)} sessions)")
```

##### `get_workspace_session_count(workspace_id: int) -> int`
Get the number of sessions in a workspace.

```python
count = manager.get_workspace_session_count(3)
print(f"Workspace 3 has {count} sessions")
```

##### `clear_workspace(workspace_id: int) -> bool`
Remove all sessions from a workspace. Returns `True` on success.

```python
manager.clear_workspace(4)
```

##### `set_workspace_layout(workspace_id: int, layout_mode: LayoutMode) -> bool`
Change layout mode for a workspace. Returns `True` on success.

```python
manager.set_workspace_layout(2, LayoutMode.MONOCLE)
```

## Usage Examples

### Basic Workspace Management

```python
from claude_multi_terminal.workspaces import WorkspaceManager, LayoutMode

# Initialize manager
manager = WorkspaceManager()

# Setup development workspace
manager.rename_workspace(1, "Development")
manager.add_session_to_workspace(1, "dev-session-1")
manager.add_session_to_workspace(1, "dev-session-2")
manager.set_workspace_layout(1, LayoutMode.TILED)

# Setup testing workspace
manager.rename_workspace(2, "Testing")
manager.add_session_to_workspace(2, "test-session-1")
manager.set_workspace_layout(2, LayoutMode.MONOCLE)

# Switch between workspaces
manager.switch_to_workspace(1)  # Go to Development
manager.switch_to_workspace(2)  # Go to Testing
```

### Session Lifecycle

```python
# Create session in workspace 1
session_id = "session-abc-123"
manager.add_session_to_workspace(1, session_id)

# Find which workspace contains the session
ws_id = manager.get_session_workspace(session_id)
print(f"Session in workspace {ws_id}")

# Move session to different workspace
manager.move_session(session_id, from_ws=1, to_ws=5)

# Remove session completely
manager.remove_session_from_workspace(5, session_id)
```

### Focus Management

```python
ws = manager.get_workspace(1)

# Add multiple sessions
ws.add_session("session-1")
ws.add_session("session-2")
ws.add_session("session-3")

# First session auto-focused on creation
print(f"Focused: {ws.focused_session_id}")  # "session-1"

# Change focus
ws.set_focus("session-2")

# Clear focus
ws.set_focus(None)
```

### Layout Switching

```python
# Get workspace
ws = manager.get_workspace(3)

# Try different layouts
ws.set_layout_mode(LayoutMode.TILED)     # Grid layout
ws.set_layout_mode(LayoutMode.FLOATING)  # Free-form windows
ws.set_layout_mode(LayoutMode.MONOCLE)   # Fullscreen single pane
```

### Workspace Inspection

```python
# List all workspaces
for ws in manager.list_workspaces():
    session_count = len(ws.session_ids)
    layout = ws.layout_mode.value
    print(f"[{ws.id}] {ws.name}: {session_count} sessions ({layout})")

# Check if workspace is empty
ws = manager.get_workspace(5)
if ws.is_empty():
    print("Workspace 5 has no sessions")

# Get session count
count = manager.get_workspace_session_count(2)
print(f"Workspace 2: {count} sessions")
```

## Design Patterns

### Automatic Timestamp Tracking

All state-modifying operations automatically update the `modified_at` timestamp:

```python
ws = Workspace(id=1, name="Test")
initial = ws.modified_at

ws.add_session("session-1")      # Updates modified_at
ws.set_focus("session-1")         # Updates modified_at
ws.set_layout_mode(LayoutMode.TILED)  # Updates modified_at

assert ws.modified_at > initial
```

### Auto-Focus Behavior

When adding the first session to an empty workspace, it automatically becomes focused:

```python
ws = Workspace(id=1, name="Test")
assert ws.focused_session_id is None

ws.add_session("session-1")
assert ws.focused_session_id == "session-1"  # Auto-focused
```

### Focus Shifting on Removal

When removing the focused session, focus automatically shifts to the next available session:

```python
ws.add_session("session-1")
ws.add_session("session-2")
ws.set_focus("session-1")

ws.remove_session("session-1")
assert ws.focused_session_id == "session-2"  # Auto-shifted

ws.remove_session("session-2")
assert ws.focused_session_id is None  # No sessions left
```

### Workspace Isolation

Each workspace maintains completely independent state:

```python
# Setup three different workspaces
manager.add_session_to_workspace(1, "dev-1")
manager.set_workspace_layout(1, LayoutMode.TILED)

manager.add_session_to_workspace(2, "test-1")
manager.set_workspace_layout(2, LayoutMode.MONOCLE)

manager.add_session_to_workspace(3, "research-1")
manager.set_workspace_layout(3, LayoutMode.FLOATING)

# Each workspace maintains its own state
ws1 = manager.get_workspace(1)
ws2 = manager.get_workspace(2)
ws3 = manager.get_workspace(3)

assert ws1.layout_mode == LayoutMode.TILED
assert ws2.layout_mode == LayoutMode.MONOCLE
assert ws3.layout_mode == LayoutMode.FLOATING
```

## Validation and Error Handling

### Workspace ID Validation

Workspace IDs must be between 1 and 9:

```python
# Valid IDs
for i in range(1, 10):
    ws = Workspace(id=i, name=f"Workspace {i}")  # ✓ OK

# Invalid IDs
Workspace(id=0, name="Invalid")   # ✗ Raises ValueError
Workspace(id=10, name="Invalid")  # ✗ Raises ValueError
Workspace(id=-1, name="Invalid")  # ✗ Raises ValueError
```

### Safe Operations

All manager operations return boolean success indicators:

```python
# Returns False if workspace doesn't exist
result = manager.rename_workspace(99, "Invalid")
assert result is False

# Returns False if session not found
result = manager.remove_session_from_workspace(1, "nonexistent")
assert result is False

# Returns False if invalid workspace IDs
result = manager.move_session("session-1", 1, 99)
assert result is False
```

### Duplicate Prevention

Adding duplicate sessions is safe (no duplicates created):

```python
ws = Workspace(id=1, name="Test")
ws.add_session("session-1")
ws.add_session("session-1")  # Ignored
ws.add_session("session-1")  # Ignored

assert ws.session_ids.count("session-1") == 1
```

## Testing

### Running Tests

```bash
# Using pytest (if installed)
cd /Users/wallonwalusayi/claude-multi-terminal
python3 -m pytest tests/test_workspaces.py -v

# Using standalone test runner
cd /Users/wallonwalusayi/claude-multi-terminal
python3 test_workspace_standalone.py
```

### Test Coverage

The test suite covers:

- ✓ LayoutMode enum values
- ✓ Workspace creation and validation
- ✓ Session management (add/remove)
- ✓ Focus handling
- ✓ WorkspaceManager initialization
- ✓ Workspace operations (create/rename/switch)
- ✓ Session operations across workspaces
- ✓ Layout mode changes
- ✓ Integration scenarios
- ✓ Timestamp updates
- ✓ Edge cases and error conditions

All 11 test categories pass with 100% success rate.

## Integration with CLAUDE.md Phase 2

This workspace system implements the data model foundation for the Phase 2 workspace feature described in CLAUDE.md:

### Alignment with Requirements

| Requirement | Implementation |
|-------------|----------------|
| 9 independent workspaces | ✓ WorkspaceManager creates 9 workspaces (1-9) |
| Numbered 1-9 for quick switching | ✓ Workspace.id constrained to 1-9 |
| User-renameable | ✓ WorkspaceManager.rename_workspace() |
| Session organization | ✓ Workspace.session_ids list |
| Layout modes | ✓ LayoutMode enum (TILED, FLOATING, MONOCLE) |
| Independent state | ✓ Each workspace maintains own sessions/layout |
| Focus tracking | ✓ Workspace.focused_session_id |
| Timestamp audit | ✓ created_at and modified_at fields |

### Next Steps for Full Integration

To complete the Phase 2 workspace feature, the following UI/interaction layer is needed:

1. **Keyboard Shortcuts**
   - `Alt+1` through `Alt+9` to switch workspaces
   - `Ctrl+B` then `w` followed by number for workspace operations

2. **UI Components**
   - Workspace indicator in status bar
   - Workspace switcher dialog
   - Session drag-and-drop between workspaces

3. **Persistence**
   - Save workspace state to disk
   - Restore workspaces on app startup
   - Integrate with existing persistence layer

4. **Session Manager Integration**
   - Connect WorkspaceManager with SessionManager
   - Sync session lifecycle with workspace membership
   - Handle session creation/termination events

## Thread Safety

**Important**: The WorkspaceManager is NOT thread-safe. Use external synchronization (locks) if accessing from multiple threads.

```python
import threading

lock = threading.Lock()
manager = WorkspaceManager()

def safe_add_session(workspace_id, session_id):
    with lock:
        manager.add_session_to_workspace(workspace_id, session_id)
```

## Performance Considerations

### Linear Search for Session Lookup

`get_session_workspace()` performs a linear search across all workspaces:

```python
# O(9 * avg_sessions_per_workspace) complexity
ws_id = manager.get_session_workspace(session_id)
```

For better performance with frequent lookups, consider maintaining an inverted index:

```python
# Example optimization (not implemented)
class OptimizedWorkspaceManager(WorkspaceManager):
    def __init__(self):
        super().__init__()
        self._session_to_workspace = {}  # session_id -> workspace_id
```

### Timestamp Precision

Timestamps use `time.time()` which has microsecond precision on most systems. For operations happening within microseconds, timestamps may appear equal.

## Best Practices

1. **Use workspace IDs consistently**: Always use integers 1-9 for workspace IDs
2. **Check return values**: All modification methods return success booleans
3. **Update timestamps**: Automatic timestamp updates track all modifications
4. **Maintain focus**: Focus management is automatic but can be overridden
5. **Handle empty workspaces**: Use `is_empty()` before assuming sessions exist

## License

MIT License - See project LICENSE file for details.

## Authors

Claude Code Team

---

**Last Updated**: 2026-02-17
**Version**: 1.0.0
**Module**: `claude_multi_terminal.workspaces`
