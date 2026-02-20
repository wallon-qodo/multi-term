# Workspace System API Quick Reference

## Import

```python
from claude_multi_terminal.workspaces import (
    Workspace,
    LayoutMode,
    WorkspaceManager
)
```

## Layout Modes

```python
LayoutMode.TILED      # Grid layout
LayoutMode.FLOATING   # Free-form windows
LayoutMode.MONOCLE    # Fullscreen single pane
```

## Initialize Manager

```python
manager = WorkspaceManager()
# Creates 9 workspaces (1-9), workspace 1 is active
```

## Common Operations

### Switch Workspace
```python
manager.switch_to_workspace(3)
active = manager.get_active_workspace()
```

### Rename Workspace
```python
manager.rename_workspace(1, "Development")
manager.rename_workspace(2, "Testing")
```

### Add Session
```python
# Add to workspace
manager.add_session_to_workspace(1, "session-uuid-123")

# First session auto-focuses
ws = manager.get_workspace(1)
print(ws.focused_session_id)  # "session-uuid-123"
```

### Move Session
```python
# Move between workspaces
manager.move_session("session-123", from_ws=1, to_ws=5)
```

### Remove Session
```python
manager.remove_session_from_workspace(1, "session-123")
```

### Find Session
```python
ws_id = manager.get_session_workspace("session-123")
print(f"Session in workspace {ws_id}")
```

### Change Layout
```python
manager.set_workspace_layout(1, LayoutMode.TILED)
manager.set_workspace_layout(2, LayoutMode.FLOATING)
manager.set_workspace_layout(3, LayoutMode.MONOCLE)
```

### List All Workspaces
```python
for ws in manager.list_workspaces():
    print(f"[{ws.id}] {ws.name}: {len(ws.session_ids)} sessions")
```

### Check Session Count
```python
count = manager.get_workspace_session_count(2)
print(f"{count} sessions")
```

### Clear Workspace
```python
manager.clear_workspace(5)  # Remove all sessions
```

## Workspace Object Methods

```python
ws = manager.get_workspace(1)

# Check if empty
if ws.is_empty():
    print("No sessions")

# Add session
ws.add_session("session-456")

# Remove session
ws.remove_session("session-456")

# Set focus
ws.set_focus("session-789")
ws.set_focus(None)  # Clear focus

# Change layout
ws.set_layout_mode(LayoutMode.FLOATING)

# Get properties
print(ws.name)
print(ws.session_ids)
print(ws.focused_session_id)
print(ws.layout_mode)
print(ws.created_at)
print(ws.modified_at)
```

## Return Values

All modification methods return `bool`:
- `True` = success
- `False` = failure (workspace not found, session not found, etc.)

```python
if manager.rename_workspace(5, "Research"):
    print("Renamed successfully")
else:
    print("Workspace not found")
```

## Auto-Behaviors

### 1. Auto-Focus First Session
```python
ws.add_session("first-session")
# ws.focused_session_id == "first-session"
```

### 2. Auto-Shift Focus on Remove
```python
ws.add_session("s1")
ws.add_session("s2")
ws.set_focus("s1")
ws.remove_session("s1")
# ws.focused_session_id == "s2" (auto-shifted)
```

### 3. Auto-Update Timestamps
```python
ws.add_session("s1")     # Updates modified_at
ws.set_focus("s1")       # Updates modified_at
ws.set_layout_mode(...)  # Updates modified_at
```

## Complete Example

```python
from claude_multi_terminal.workspaces import WorkspaceManager, LayoutMode

# Initialize
manager = WorkspaceManager()

# Setup Development workspace
manager.rename_workspace(1, "Development")
manager.add_session_to_workspace(1, "dev-1")
manager.add_session_to_workspace(1, "dev-2")
manager.set_workspace_layout(1, LayoutMode.TILED)

# Setup Testing workspace
manager.rename_workspace(2, "Testing")
manager.add_session_to_workspace(2, "test-1")
manager.set_workspace_layout(2, LayoutMode.MONOCLE)

# Switch between workspaces
manager.switch_to_workspace(1)
print(f"Active: {manager.get_active_workspace().name}")

manager.switch_to_workspace(2)
print(f"Active: {manager.get_active_workspace().name}")

# Move session
manager.move_session("dev-1", from_ws=1, to_ws=5)

# List all workspaces
for ws in manager.list_workspaces():
    count = len(ws.session_ids)
    if count > 0:
        print(f"[{ws.id}] {ws.name}: {count} sessions")
```

## Validation

### Valid Workspace IDs
Only 1-9 are valid:
```python
Workspace(id=1, name="Valid")   # ✓ OK
Workspace(id=9, name="Valid")   # ✓ OK
Workspace(id=0, name="Invalid") # ✗ ValueError
Workspace(id=10, name="Invalid") # ✗ ValueError
```

### Duplicate Prevention
```python
ws.add_session("session-1")
ws.add_session("session-1")  # Ignored
ws.add_session("session-1")  # Ignored
# Only one "session-1" in session_ids
```

## Testing

```bash
# Run tests
cd /Users/wallonwalusayi/claude-multi-terminal
python3 test_workspace_standalone.py
```

## Documentation

- **Full API**: `WORKSPACE_SYSTEM_DOCUMENTATION.md`
- **Summary**: `WORKSPACE_SYSTEM_SUMMARY.md`
- **This Guide**: `WORKSPACE_API_QUICK_REF.md`

---

**Module**: `claude_multi_terminal.workspaces`
**Version**: 1.0.0
**Status**: Production-ready
