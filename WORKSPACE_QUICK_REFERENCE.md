# Workspace Indicators - Quick Reference

## Visual Display

```
╔═══ ⚡ CLAUDE MULTI-TERMINAL ┃ [1•2] [2] [3] [4•1] [5] [6] [7] [8] [9] ┃ ● 3 Active ═══╗
                                  ^^^^      ^^^^
                                  Active    Inactive w/ sessions
```

## Color Codes

| State | Appearance | Meaning |
|-------|-----------|---------|
| **[1•2]** (coral background) | Active workspace | Currently viewing workspace 1 with 2 sessions |
| [4•1] (gray) | Has sessions | Workspace 4 has 1 session (not active) |
| [2] (dim gray) | Empty | Workspace 2 has no sessions |

## API Methods

```python
# Get header reference
header = self.query_one(HeaderBar)

# Switch active workspace
header.set_active_workspace(3)

# Update single workspace session count
header.update_workspace_sessions(workspace_id=1, count=2)

# Update all workspaces at once
header.update_all_workspace_sessions({1: 2, 4: 1, 7: 3})
```

## Reactive Properties

```python
# Direct property access (also triggers update)
header.active_workspace = 2
header.workspace_sessions = {1: 3, 2: 1, 5: 2}
```

## Integration Pattern

```python
async def switch_workspace(self, workspace_id: int) -> None:
    """Standard pattern for workspace switching."""
    # 1. Update internal state
    self.current_workspace = workspace_id

    # 2. Update header display
    header = self.query_one(HeaderBar)
    header.set_active_workspace(workspace_id)

    # 3. Load workspace sessions
    sessions = self.load_workspace_sessions(workspace_id)

    # 4. Update session count
    header.update_workspace_sessions(workspace_id, len(sessions))
    header.session_count = sum(len(s) for s in self.all_workspaces.values())
```

## Suggested Keybindings

```python
# Workspace switching
Binding("alt+1", "switch_workspace(1)", "Workspace 1"),
Binding("alt+2", "switch_workspace(2)", "Workspace 2"),
# ... through alt+9

# Move session to workspace
Binding("ctrl+shift+1", "move_to_workspace(1)", "Move to WS 1"),
Binding("ctrl+shift+2", "move_to_workspace(2)", "Move to WS 2"),
# ... through ctrl+shift+9
```

## Files

- **Implementation**: `/Users/wallonwalusayi/claude-multi-terminal/claude_multi_terminal/widgets/header_bar.py`
- **Usage Guide**: `WORKSPACE_INDICATOR_USAGE.md`
- **Visual Reference**: `WORKSPACE_INDICATOR_VISUAL.txt`
- **Integration Example**: `WORKSPACE_INTEGRATION_EXAMPLE.py`
- **Summary**: `WORKSPACE_INDICATOR_SUMMARY.md`
- **Quick Reference**: `WORKSPACE_QUICK_REFERENCE.md` (this file)

## Colors Reference

```python
# From theme.py (HomebrewTheme)
ACCENT_PRIMARY = "rgb(255,77,77)"     # Coral red (active workspace)
TEXT_PRIMARY = "rgb(240,240,240)"     # White (active text)
TEXT_SECONDARY = "rgb(180,180,180)"   # Light gray (inactive with sessions)
TEXT_DIM = "rgb(120,120,120)"         # Dim gray (empty workspace)
BORDER_SUBTLE = "rgb(42,42,42)"       # Separator borders
```

## Testing

```python
# Test in Python REPL or app
from claude_multi_terminal.widgets.header_bar import HeaderBar

# Create header
header = HeaderBar()

# Test active workspace
header.set_active_workspace(3)
assert header.active_workspace == 3

# Test session counts
header.update_workspace_sessions(1, 2)
header.update_workspace_sessions(3, 1)
assert header.workspace_sessions[1] == 2
assert header.workspace_sessions[3] == 1

# Test bulk update
header.update_all_workspace_sessions({1: 2, 4: 1, 7: 3})
assert header.workspace_sessions[1] == 2
assert header.workspace_sessions[4] == 1
assert header.workspace_sessions[7] == 3
```

## Common Patterns

### Pattern 1: Initialize on startup
```python
async def on_mount(self) -> None:
    header = self.query_one(HeaderBar)
    header.set_active_workspace(1)
    header.update_workspace_sessions(1, len(self.initial_sessions))
```

### Pattern 2: Update on session create
```python
async def action_new_session(self) -> None:
    # Create session...
    header = self.query_one(HeaderBar)
    current_count = header.workspace_sessions[self.current_workspace]
    header.update_workspace_sessions(self.current_workspace, current_count + 1)
    header.session_count += 1
```

### Pattern 3: Update on session close
```python
async def action_close_session(self) -> None:
    # Close session...
    header = self.query_one(HeaderBar)
    current_count = header.workspace_sessions[self.current_workspace]
    header.update_workspace_sessions(self.current_workspace, current_count - 1)
    header.session_count -= 1
```

### Pattern 4: Update on workspace switch
```python
async def action_switch_workspace(self, workspace_id: int) -> None:
    header = self.query_one(HeaderBar)
    header.set_active_workspace(workspace_id)
    # Load sessions...
    session_count = len(loaded_sessions)
    header.update_workspace_sessions(workspace_id, session_count)
```

## Troubleshooting

**Indicators not showing**: Check that HeaderBar is composed in the app and mounted.

**Colors not matching**: Verify HomebrewTheme colors haven't changed in theme.py.

**Reactive updates not working**: Ensure you're modifying the reactive properties, not internal state.

**Session counts wrong**: Make sure to call `update_workspace_sessions()` whenever sessions change.

## Next Steps

1. Add keyboard shortcuts (Alt+1-9) to app.py
2. Implement workspace state management
3. Add workspace persistence (save/load)
4. Add click handlers for workspace indicators
5. Add tooltips showing workspace names
6. Add context menu for workspace operations
