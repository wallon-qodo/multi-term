# Text Selection and Copying Guide

## Methods to Copy Text from Claude Multi-Terminal

### Method 1: Ctrl+C (Recommended)
The easiest way to copy output from the currently focused session.

**Steps:**
1. Click on the session pane you want to copy from (or use Tab to switch to it)
2. Press **Ctrl+C**
3. All output from that session is copied to your system clipboard
4. Paste anywhere with Cmd+V (Mac) or Ctrl+V (Linux/Windows)

**Pros:** Works instantly, copies all output, no mouse needed
**Cons:** Copies entire output, can't select specific text

### Method 2: F2 Toggle (For Mouse Selection)
Temporarily disable app mouse control to enable native terminal text selection.

**Steps:**
1. Press **F2** to disable mouse capture
2. You'll see notification: "Mouse mode: OFF - You can now click and drag to select text"
3. Click and drag to select text in any pane (like a normal terminal)
4. Copy with Cmd+C (Mac) or Ctrl+Shift+C (Linux) or right-click → Copy
5. Press **F2** again when done to re-enable app mouse control

**Pros:** Select specific text, works like normal terminal
**Cons:** Temporarily disables app mouse features, requires toggling

### Method 3: Shift+Click (May Work)
Some terminals support Shift+Click for selection even when app has mouse capture.

**Steps:**
1. Hold **Shift** and click+drag to select text
2. Copy with Cmd+C or right-click menu

**Pros:** No need to toggle mouse mode
**Cons:** Not supported by all terminals

### Method 4: Tmux/Screen Selection (Advanced)
If running the app inside tmux or screen:

**Tmux:**
- Enter copy mode: `Ctrl+B [` (or your tmux prefix + `[`)
- Navigate with arrow keys
- Start selection: `Space`
- Copy: `Enter`

**Screen:**
- Enter copy mode: `Ctrl+A Esc`
- Navigate and select
- Copy: `Enter`

## Quick Reference

| Action | Keyboard Shortcut |
|--------|------------------|
| Copy all output from focused pane | **Ctrl+C** |
| Toggle mouse mode for text selection | **F2** |
| Switch between panes | **Tab** / **Shift+Tab** |
| Quit app | **Ctrl+Q** |

## Troubleshooting

### "Ctrl+C doesn't copy"
- Make sure you've clicked on a session pane first (it should have a double border)
- Wait for the notification confirming the copy
- Check if your terminal supports clipboard access

### "Can't select text with mouse"
1. Try pressing **F2** first to disable mouse capture
2. If that doesn't work, try holding **Shift** while clicking
3. As a fallback, use **Ctrl+C** to copy all output

### "F2 doesn't work"
- Some terminals may not support dynamic mouse mode toggling
- Use **Ctrl+C** to copy all output instead
- Or use Shift+Click if your terminal supports it

### "Copied text includes ANSI codes"
- The Ctrl+C method automatically strips ANSI color codes
- If you see escape sequences like `\x1b[38;2;255`, you may have copied raw output
- Use the Ctrl+C method instead of manual selection

## Terminal Compatibility

**Best support:** iTerm2, Terminal.app (Mac), Konsole, GNOME Terminal
**Partial support:** Windows Terminal, Alacritty
**Limited support:** Basic xterm

## Examples

### Copy a specific Claude response:
1. Press **F2** (disable mouse)
2. Select the response text with mouse
3. Copy with Cmd+C
4. Press **F2** (re-enable mouse)

### Copy entire conversation:
1. Click on the session pane
2. Press **Ctrl+C**
3. Paste into a file or document

### Copy from multiple sessions:
1. Tab to Session 1
2. Ctrl+C to copy
3. Paste into a document
4. Tab to Session 2
5. Ctrl+C to copy
6. Paste below the first session's output

---

**Pro Tip:** If you frequently need to copy output, consider running the app in tmux/screen for better text selection control, or use the `--output-file` feature if available in future versions.
