# Text Selection in Claude Multi-Terminal

## The Problem

TUI (Terminal User Interface) apps like Claude Multi-Terminal capture mouse and keyboard input, which prevents normal text selection. However, there are several ways to select and copy text!

## Solutions (in order of recommendation)

### 1. Use Shift+Click (Easiest)

Most modern terminals allow text selection even in TUI mode by holding Shift:

**macOS Terminal / iTerm2:**
- **Hold Shift + Click and Drag** to select text
- **Shift + Double-click** to select a word
- **Cmd+C** to copy (normal macOS copy)

**Linux (GNOME Terminal, Konsole, etc.):**
- **Hold Shift + Click and Drag** to select text
- **Ctrl+Shift+C** to copy

**Windows Terminal:**
- **Hold Shift + Click and Drag** to select text
- **Ctrl+Shift+C** to copy

### 2. Use Built-in Copy (Ctrl+C)

The app has a built-in copy function:

1. **Focus the pane** you want to copy from (Tab/Shift+Tab)
2. **Press Ctrl+C** - copies ALL output from that pane
3. **Press Cmd+V** (macOS) or **Ctrl+V** (Linux/Windows) to paste

**Note:** This copies the entire output, not just selected text.

### 3. Terminal's Copy Mode

Many terminals have a "copy mode":

**tmux users:**
- Press **Prefix + [** to enter copy mode
- Use arrow keys to navigate
- Press **Space** to start selection
- Press **Enter** to copy

**iTerm2:**
- **Cmd+Shift+C** enters copy mode
- Use arrow keys and select text

### 4. Use F2 Toggle (Limited)

Press **F2** in the app to get a reminder about text selection. While the app can't fully disable mouse capture, the notification reminds you of the Shift+Click method.

## Recommendations by Terminal

| Terminal | Best Method | Notes |
|----------|-------------|-------|
| **iTerm2 (macOS)** | Shift+Click and drag | Works perfectly |
| **Terminal.app (macOS)** | Shift+Click and drag | Built-in support |
| **GNOME Terminal** | Shift+Click and drag | Standard behavior |
| **Windows Terminal** | Shift+Click and drag | Modern terminals support this |
| **Alacritty** | Shift+Click and drag | Configure in alacritty.yml |
| **tmux** | Use copy-mode | Prefix+[ |

## Copy All Output Quick Reference

Want to copy everything from a session?

1. **Tab** to focus the session
2. **Ctrl+C** - copies all output to clipboard
3. Done! Paste anywhere with Cmd+V/Ctrl+V

## Still Having Issues?

If Shift+Click doesn't work in your terminal:

1. Check your terminal's preferences for mouse reporting settings
2. Try a different terminal emulator (iTerm2 is excellent on macOS)
3. Use the built-in Ctrl+C to copy all output
4. Use your terminal's copy-mode if available

## Configuration Examples

### Alacritty (add to ~/.config/alacritty/alacritty.yml)

```yaml
mouse:
  # Allow text selection with Shift key
  mouse_bindings:
    - { mouse: Left, mods: Shift, action: Copy }
```

### iTerm2

1. Preferences → Profiles → Terminal
2. Ensure "Report mouse events" is checked
3. Shift+Click will still work for selection

## Pro Tip

If you need to copy specific parts of output frequently, consider:
1. Running Claude with output redirection: `claude > output.log`
2. Using **Ctrl+S** to save sessions, which stores session metadata
3. Using the built-in **Ctrl+C** and pasting into a text editor, then selecting what you need
