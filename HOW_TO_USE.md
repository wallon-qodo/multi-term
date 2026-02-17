# Claude Multi-Terminal - Quick Start Guide

## How to Launch the App

Run this command in Terminal.app:

```bash
cd /Users/wallonwalusayi/claude-multi-terminal
source venv/bin/activate
python LAUNCH.py
```

Press Enter when prompted, and the app will take over your terminal window.

## What You'll See

A split-screen interface with 2 Claude CLI sessions side-by-side:
- Each pane has a **session name** at the top (Session 1, Session 2)
- A large **output area** in the middle showing Claude's responses
- An **input box** at the bottom where you type commands
- A **status bar** at the bottom showing keyboard shortcuts

## How to Use

### Basic Usage
1. **Type a command** in the input box at the bottom of any pane
2. **Press Enter** to send the command
3. **Wait 2-3 seconds** for Claude to respond (first response is slower)
4. Claude's response will appear in the output area above

### Keyboard Shortcuts

- **Tab** - Switch between panes (left/right)
- **Ctrl+N** - Create a new session (up to 6 total)
- **Ctrl+W** - Close the currently focused session
- **Ctrl+R** - Rename the current session
- **Ctrl+S** - Save all sessions (persists between restarts)
- **Ctrl+L** - Load saved sessions
- **Ctrl+B** - Toggle broadcast mode (send commands to ALL sessions at once)
- **Ctrl+C** - Copy output from the focused session
- **F2** - Toggle mouse mode (for selecting text)
- **Ctrl+Q** - Quit the app

### Tips

1. **Each session is independent** - You can have different conversations in each pane
2. **Use broadcast mode** (Ctrl+B) to send the same command to all sessions at once
3. **Text selection**: Press F2 or hold Shift while clicking to select text
4. **Sessions persist**: Use Ctrl+S to save your sessions and Ctrl+L to restore them later
5. **Multiple tasks**: Have one agent working on code while another does research

## Example Workflow

1. Start the app with 2 sessions
2. In Session 1: Ask Claude to "help me debug this Python function"
3. In Session 2: Ask Claude to "write tests for my API"
4. Both agents work independently in parallel
5. Press Tab to switch between them
6. Use Ctrl+C to copy output from either session

## Troubleshooting

**If the app doesn't start:**
- Make sure you're in the correct directory: `/Users/wallonwalusayi/claude-multi-terminal`
- Make sure venv is activated: `source venv/bin/activate`
- Run: `python LAUNCH.py`

**If commands don't work:**
- Wait a few seconds - Claude CLI takes time to initialize
- Check that your cursor is in the input box (Tab to switch panes)
- Try typing something simple like "hello" first

**If output doesn't appear:**
- The fix is already in place (using `call_later` instead of `call_from_thread`)
- Output should now appear correctly in all sessions

## Enjoy!

You now have a powerful multi-terminal interface for running multiple Claude Code sessions simultaneously!
