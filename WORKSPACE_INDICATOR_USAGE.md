# Workspace Indicator Usage Guide

The HeaderBar widget now includes visual workspace indicators showing workspaces 1-9 with session counts and active workspace highlighting.

## Features

### Visual Design
- **Active workspace**: Coral red background (rgb(255,77,77)) with white text
- **Inactive with sessions**: Gray text (rgb(180,180,180)) with dim borders
- **Empty workspaces**: Very dim gray (rgb(80,80,80))
- **Session counts**: Shown as [1•2] for workspace 1 with 2 sessions

### Display Format
```
[1•2] [2] [3] [4•1] [5] [6] [7] [8] [9]
```
- Active workspace (e.g., 1): `[1•2]` with coral background
- Workspace with sessions (e.g., 4): `[4•1]` in gray
- Empty workspaces: `[2]` in dim gray

## API Usage

### Setting Active Workspace

```python
# Get header bar reference
header = self.query_one(HeaderBar)

# Switch to workspace 3
header.set_active_workspace(3)
```

### Updating Session Counts

```python
# Update single workspace
header.update_workspace_sessions(workspace_id=1, count=2)
header.update_workspace_sessions(workspace_id=4, count=1)

# Update all workspaces at once
session_counts = {
    1: 2,  # Workspace 1 has 2 sessions
    4: 1,  # Workspace 4 has 1 session
    # Other workspaces will default to 0
}
header.update_all_workspace_sessions(session_counts)
```

### Using Reactive Properties

The workspace indicators automatically update when reactive properties change:

```python
# These will automatically trigger re-render
header.active_workspace = 2
header.workspace_sessions = {1: 3, 2: 1, 5: 2}
```

## Integration Example

```python
async def switch_workspace(self, workspace_id: int) -> None:
    """Switch to a different workspace."""
    # Update internal state
    self.current_workspace = workspace_id

    # Update header display
    header = self.query_one(HeaderBar)
    header.set_active_workspace(workspace_id)

    # Load workspace sessions
    sessions = self.load_workspace_sessions(workspace_id)

    # Update session count
    header.update_workspace_sessions(workspace_id, len(sessions))
    header.session_count = len(sessions)  # Update total active
```

## Keybindings Suggestion

To integrate with keyboard shortcuts (e.g., Alt+1 through Alt+9):

```python
BINDINGS = [
    Binding("alt+1", "switch_workspace(1)", "Workspace 1"),
    Binding("alt+2", "switch_workspace(2)", "Workspace 2"),
    Binding("alt+3", "switch_workspace(3)", "Workspace 3"),
    Binding("alt+4", "switch_workspace(4)", "Workspace 4"),
    Binding("alt+5", "switch_workspace(5)", "Workspace 5"),
    Binding("alt+6", "switch_workspace(6)", "Workspace 6"),
    Binding("alt+7", "switch_workspace(7)", "Workspace 7"),
    Binding("alt+8", "switch_workspace(8)", "Workspace 8"),
    Binding("alt+9", "switch_workspace(9)", "Workspace 9"),
]
```

## Color Reference (HomebrewTheme)

- **Active workspace background**: `rgb(255,77,77)` (Coral red)
- **Active workspace text**: `rgb(255,255,255)` (White)
- **Inactive with sessions text**: `rgb(180,180,180)` (Light gray)
- **Inactive with sessions border**: `rgb(120,120,120)` (Dim gray)
- **Empty workspace text**: `rgb(120,120,120)` (Dim gray)
- **Empty workspace border**: `rgb(80,80,80)` (Very dim gray)

## Example Output

```
╔═══ ⚡ CLAUDE MULTI-TERMINAL ┃ [1•2] [2] [3] [4•1] [5] [6] [7] [8] [9] ┃ ● 3 Active ═══╗     ┃ 🕐 02:30 PM PST
```

Where:
- Workspace 1 is active with 2 sessions (coral background)
- Workspace 4 has 1 session (gray)
- Workspaces 2, 3, 5-9 are empty (very dim)
- Total of 3 active sessions across all workspaces
