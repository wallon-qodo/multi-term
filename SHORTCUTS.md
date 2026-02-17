# Claude Multi-Terminal - Keyboard Shortcuts

*TUIOS-Inspired Multi-Terminal Interface with Modal Keyboard Control*

---

## Quick Reference

| Key | Action | Mode | Category |
|-----|--------|------|----------|
| `i` | Enter INSERT mode | NORMAL | Navigation |
| `v` | Enter COPY mode | NORMAL | Copy Mode |
| `Ctrl+B` | COMMAND mode prefix | NORMAL | Navigation |
| `Esc` | Return to NORMAL mode | ANY | Navigation |
| `Tab` | Next pane | NORMAL | Navigation |
| `Shift+Tab` | Previous pane | NORMAL | Navigation |
| `h/j/k/l` | Navigate panes (vim) | NORMAL | Navigation |
| `1-9` | Switch workspace | NORMAL | Workspace Operations |
| `Ctrl+N` | New session | NORMAL | Session Management |
| `Ctrl+B h` | Split horizontal | COMMAND | Layout Operations |
| `Ctrl+B v` | Split vertical | COMMAND | Layout Operations |
| `j/k` | Move down/up | COPY | Copy Mode |
| `w` | Next word | COPY | Copy Mode |
| `b` | Previous word | COPY | Copy Mode |
| `v` | Visual select | COPY | Copy Mode |

---

## Detailed Guide

### NORMAL Mode

*Default mode for window management and navigation*

**Navigation:**
- **`i`** - Enter INSERT mode - Switch to INSERT mode for terminal input
- **`v`** - Enter COPY mode - Enter COPY mode for scrollback navigation and selection
- **`Ctrl+B`** - COMMAND mode prefix - Enter COMMAND mode for advanced operations (2-key sequence)
- **`Esc`** - Return to NORMAL mode - Exit current mode and return to NORMAL
- **`h/j/k/l`** - Navigate panes (vim) - Move focus between panes using vim-style keys
- **`Tab`** - Next pane - Move focus to next pane
- **`Shift+Tab`** - Previous pane - Move focus to previous pane
- **`n`** - Next pane - Move to next pane (alternative)
- **`p`** - Previous pane - Move to previous pane (alternative)

**Session Management:**
- **`Ctrl+N`** - New session - Create new terminal session
- **`x`** - Close session - Close current session
- **`Ctrl+W`** - Close session - Close current session (alternative)
- **`r`** - Rename session - Rename current session
- **`Ctrl+R`** - Rename session - Rename current session (alternative)
- **`Ctrl+Shift+T`** - Reopen last session - Reopen last closed session
- **`Ctrl+B`** - Toggle broadcast - Toggle broadcast mode (send to all sessions)

**Workspace Operations:**
- **`1-9`** - Switch workspace - Switch to workspace 1-9
- **`Shift+1-9`** - Move session to workspace - Move focused session to workspace 1-9
- **`Ctrl+S`** - Save workspace - Save current workspace state
- **`Ctrl+L`** - Load workspace - Load saved workspace
- **`F10`** - Workspace manager - Open workspace management interface

**System:**
- **`q`** - Quit application - Exit the application
- **`Ctrl+Q`** - Quit application - Exit the application (alternative)
- **`Ctrl+H`** - History browser - Browse session history
- **`F9`** - History browser - Browse session history (alternative)

**Visual & Display:**
- **`Ctrl+F`** - Focus mode - Toggle focus mode (maximize current pane)
- **`F11`** - Focus mode - Toggle focus mode (alternative)
- **`F2`** - Toggle mouse - Toggle mouse support (disable for text selection)

**Search:**
- **`Ctrl+Shift+F`** - Search - Open search panel

**Copy Mode:**
- **`Ctrl+C`** - Copy output - Copy terminal output


### COMMAND Mode

*Advanced layout operations (Ctrl+B prefix required)*

**Layout Operations:**
- **`Ctrl+B h`** - Split horizontal - Split pane horizontally (top/bottom)
- **`Ctrl+B v`** - Split vertical - Split pane vertically (left/right)
- **`Ctrl+B r`** - Rotate split - Rotate split direction
- **`Ctrl+B =`** - Equalize splits - Equalize all split ratios to 50/50
- **`Ctrl+B [`** - Increase left/top - Increase left/top pane size by 5%
- **`Ctrl+B ]`** - Increase right/bottom - Increase right/bottom pane size by 5%
- **`Ctrl+B l`** - BSP layout - Switch to BSP (tiling) layout mode
- **`Ctrl+B s`** - STACK layout - Switch to STACK (monocle) layout mode
- **`Ctrl+B t`** - TAB layout - Switch to TAB (floating) layout mode

**Navigation:**
- **`Ctrl+B n`** - Next session - Next session in STACK/TAB mode
- **`Ctrl+B p`** - Previous session - Previous session in STACK/TAB mode

**System:**
- **`Ctrl+B ?`** - Show help - Display help overlay with all shortcuts


### COPY Mode

*Scrollback navigation and text selection*

**Copy Mode:**
- **`j/k`** - Move down/up - Move cursor down/up by one line
- **`h/l`** - Move left/right - Move cursor left/right by one character
- **`w`** - Next word - Move forward by word
- **`b`** - Previous word - Move backward by word
- **`0`** - Start of line - Jump to start of line
- **`$`** - End of line - Jump to end of line
- **`g`** - Top of buffer - Jump to top of scrollback buffer
- **`G`** - Bottom of buffer - Jump to bottom of scrollback buffer
- **`v`** - Visual select - Start visual selection mode
- **`y`** - Yank (copy) - Copy selection to clipboard and exit COPY mode

**Search:**
- **`/`** - Search forward - Search forward in scrollback
- **`?`** - Search backward - Search backward in scrollback
- **`n`** - Next match - Jump to next search match
- **`N`** - Previous match - Jump to previous search match

**Navigation:**
- **`Esc`** - Exit COPY mode - Return to NORMAL mode


### INSERT Mode

*Direct terminal input mode*

**Navigation:**
- **`Esc`** - Return to NORMAL - Exit INSERT mode and return to NORMAL

**Session Management:**
- **`(any key)`** - Pass to terminal - All other keys pass through to terminal


---

## Tips

- **Modal Design**: Based on vim/tmux principles - distinct modes for different tasks
- **Ctrl+B Prefix**: Command mode uses 2-key sequences (press Ctrl+B, then command key)
- **ESC Key**: Always returns to NORMAL mode from any mode
- **Vim Keys**: h/j/k/l navigation supported throughout
- **Text Selection**: F2 toggles mouse support (disable for terminal text selection)

*Generated by Claude Multi-Terminal Shortcut Reference System*
