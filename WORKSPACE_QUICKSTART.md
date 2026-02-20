# Workspace Persistence Quick Start

## What Is It?

Workspace persistence allows you to save and load complete workspace configurations, including all sessions with their metadata, working directories, and command history.

## How to Use

### Automatic Operation

Workspace persistence works automatically with no manual intervention required:

1. **On Startup**: Loads previously saved workspaces
2. **On Workspace Switch**: Auto-saves current workspace (if AUTO_SAVE enabled)
3. **On Exit**: Saves all workspaces (if SAVE_ON_EXIT enabled)

### Configuration

Edit `config.py` to control behavior:
```python
AUTO_SAVE = True      # Auto-save on workspace switch
SAVE_ON_EXIT = True   # Save all workspaces on exit
```

### Storage Location

All workspaces are saved to:
```
~/.multi-term/workspaces.json
```

Backup file:
```
~/.multi-term/workspaces.bak
```

## What Gets Saved

Each workspace contains:
- Workspace ID and name
- All sessions with:
  - Session name
  - Working directory
  - Command count
  - Last command
  - Output snapshot (last 50 lines)
  - Conversation file path
- Creation and modification timestamps
- Optional description and tags

## Programmatic Usage

### Save Workspaces

```python
from claude_multi_terminal.persistence.storage import SessionStorage
from claude_multi_terminal.persistence.session_state import WorkspaceData

storage = SessionStorage()
workspaces = {
    1: WorkspaceData(...),
    2: WorkspaceData(...)
}
success = storage.save_workspaces(workspaces)
```

### Load Workspaces

```python
storage = SessionStorage()
workspaces = storage.load_workspaces()

if workspaces:
    for ws_id, workspace in workspaces.items():
        print(f"Workspace {ws_id}: {workspace.name}")
        print(f"  Sessions: {len(workspace.sessions)}")
```

## Error Recovery

If workspace file is corrupted:
1. System automatically tries backup recovery
2. Corrupted file is archived for manual inspection
3. App continues with empty workspaces

## Testing

Run the test suite:
```bash
cd /Users/wallonwalusayi/claude-multi-terminal
source venv/bin/activate
python test_workspace_persistence.py
```

## Troubleshooting

### Workspaces not saving
- Check Config.AUTO_SAVE is True
- Verify write permissions: `ls -la ~/.multi-term/`
- Check disk space: `df -h ~`

### Workspaces not loading
- Check if file exists: `ls -la ~/.multi-term/workspaces.json`
- Try loading backup: `cp ~/.multi-term/workspaces.bak ~/.multi-term/workspaces.json`
- Validate JSON: `cat ~/.multi-term/workspaces.json | jq .`

### Reset workspaces
```bash
rm ~/.multi-term/workspaces.json
rm ~/.multi-term/workspaces.bak
```

## More Information

For detailed documentation, see:
- `WORKSPACE_PERSISTENCE.md` - Full feature documentation
- `IMPLEMENTATION_SUMMARY.md` - Implementation details
