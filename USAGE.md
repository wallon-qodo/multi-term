# Claude Multi-Terminal - Usage Guide

## Quick Start

### Running the Application

```bash
cd claude-multi-terminal
source venv/bin/activate
claude-multi
```

Or use Python directly:

```bash
python -m claude_multi_terminal
```

## Features Overview

### 1. Multiple Sessions

The app starts with **2 Claude Code CLI sessions** by default in a split-pane layout.

- **1 session**: Full screen
- **2 sessions**: Side-by-side (2x1 grid)
- **3-4 sessions**: 2x2 grid
- **5-6 sessions**: 2 columns with dynamic rows

### 2. Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| **Ctrl+N** | Create new session |
| **Ctrl+W** | Close current session |
| **Ctrl+S** | Save all sessions to disk |
| **Ctrl+L** | Load sessions from saved state |
| **Ctrl+R** | Rename current session |
| **Ctrl+B** | Toggle broadcast mode (send to all sessions) |
| **Ctrl+C** | Copy output from current session |
| **Tab** | Focus next pane |
| **Shift+Tab** | Focus previous pane |
| **Ctrl+Q** | Quit application |

### 3. Broadcast Mode

When broadcast mode is **ON** (Ctrl+B):
- Commands typed in ANY input field are sent to ALL sessions simultaneously
- Status bar shows **[BROADCAST MODE]** in yellow/warning color
- Great for running the same command across multiple sessions

Press Ctrl+B again to turn it off.

### 4. Session Persistence

**Saving:**
```
Press Ctrl+S to save current sessions
```

This saves to: `~/.claude_multi_terminal/workspace_state.json`

**Loading:**
```
Press Ctrl+L to restore saved sessions
```

The saved state includes:
- Session names
- Working directories
- Session metadata

**Note:** Output history is NOT saved (to keep file size manageable).

### 5. Session Naming

**Rename a session:**
1. Focus the session you want to rename (Tab/Shift+Tab)
2. Press **Ctrl+R**
3. Enter new name in the dialog
4. Press Enter or click OK

Default names: "Session 1", "Session 2", etc.

### 6. Copy/Paste and Text Selection

**Copy ALL output from a session:**
1. Focus the session (Tab/Shift+Tab)
2. Press **Ctrl+C**
3. All output is copied to system clipboard (macOS: pbcopy)

The copied text is plain text without ANSI color codes.

**Select specific text:**
- **Hold Shift + Click and Drag** to select text (works in most terminals)
- **Shift + Double-click** to select a word
- Then use your terminal's copy shortcut (Cmd+C on macOS, Ctrl+Shift+C on Linux)

**Note:** Press **F2** in the app for a quick reminder about text selection methods.

For detailed text selection instructions, see [TEXT_SELECTION.md](TEXT_SELECTION.md).

## Workflow Examples

### Example 1: Compare Responses

```
1. Start app (2 sessions by default)
2. Tab to first session
3. Ask Claude a question
4. Tab to second session
5. Ask the same question with different context
6. Compare responses side-by-side
```

### Example 2: Multi-Project Work

```
1. Ctrl+N to create new sessions (up to 6)
2. Ctrl+R to name them: "Frontend", "Backend", "Docs", "Tests"
3. Each session works in different directory
4. Ctrl+S to save your workspace
5. Ctrl+L to restore later
```

### Example 3: Broadcast Commands

```
1. Have 4 sessions open
2. Ctrl+B to enable broadcast mode
3. Type: "git status"
4. All 4 sessions execute the command
5. Check git status across multiple repos at once
```

## Troubleshooting

### App doesn't start

**Error: "Claude CLI not found"**

Solution:
```bash
# Set custom Claude path
export CLAUDE_PATH=/path/to/your/claude
claude-multi
```

### Clipboard not working

**macOS:** Should work out of the box with `pbcopy`/`pbpaste`

**Linux:** Requires `xclip` or `xsel`:
```bash
# Ubuntu/Debian
sudo apt-get install xclip

# Fedora
sudo dnf install xclip
```

### Sessions not loading

Check saved state file:
```bash
cat ~/.claude_multi_terminal/workspace_state.json
```

If corrupted, a backup is automatically created with `.bak` extension.

### Terminal too small

Minimum terminal size: **80x24**

If your terminal is smaller, you'll see a warning. Resize your terminal window.

## Advanced Configuration

### Custom Claude Path

Set environment variable before running:
```bash
export CLAUDE_PATH=/custom/path/to/claude
claude-multi
```

### Change Storage Directory

Edit `claude_multi_terminal/config.py`:
```python
STORAGE_DIR = Path.home() / ".my_custom_dir"
```

### Adjust Default Settings

In `config.py`:
```python
DEFAULT_SESSION_COUNT = 2   # Starting sessions
MAX_SESSIONS = 6            # Maximum allowed
PTY_ROWS = 24              # Terminal height
PTY_COLS = 80              # Terminal width
```

## Tips & Best Practices

1. **Use broadcast mode carefully** - Commands are sent to ALL sessions, including destructive ones like `rm`

2. **Name your sessions** - Easier to identify which is which in a 2x2 grid

3. **Save frequently** - Ctrl+S is quick and preserves your workspace setup

4. **Close idle sessions** - Ctrl+W to free up resources when you're done

5. **Copy before exiting** - Session output is lost on exit unless you copy it (Ctrl+C)

## Limitations

### Current Version (0.1.0)

- Maximum 6 sessions (configurable in code)
- No session tabs (only split panes)
- No session output search/filter
- No command history per session
- Output history not persisted on save
- Paste functionality is internal only (copies between sessions)

### Planned Features (Future)

- Session tabs + splits hybrid layout
- Resizable split ratios
- Command history with search
- Log export to files
- Custom color themes
- Session templates
- Remote session sharing

## Need Help?

Check the project repository or raise an issue if you encounter problems.

Happy multi-tasking with Claude! 🦀
