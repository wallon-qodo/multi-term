# Multi-Line Input & Command History - Visual Demo

## Quick Visual Guide

This document provides a visual walkthrough of the multi-line input and command history feature.

## 1. Single-Line Mode (Default)

```
┌─────────────────────────────────────────────────────────────────────┐
│ ● Session | ID: abc123                                              │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│ [Terminal Output Area]                                              │
│                                                                     │
├─────────────────────────────────────────────────────────────────────┤
│ Single-line | Enter: Submit | Shift+Enter: Multi-line mode | ↑↓: H │
│ write a function to calculate fibonacci_                           │
└─────────────────────────────────────────────────────────────────────┘

Actions:
• Press ENTER → Submits command "write a function to calculate fibonacci"
• Press ↑     → Shows previous command from history
• Press ↓     → Shows next command (or restores current draft)
• Type "/"    → Shows slash command autocomplete
```

## 2. Multi-Line Mode

```
┌─────────────────────────────────────────────────────────────────────┐
│ ● Session | ID: abc123                                              │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│ [Terminal Output Area]                                              │
│                                                                     │
├─────────────────────────────────────────────────────────────────────┤
│ Multi-line | Ctrl+Enter: Submit | Shift+Enter: New line | Esc: ... │
│ write a Python function that:                                       │
│ 1. Calculates fibonacci numbers                                     │
│ 2. Uses memoization for efficiency                                  │
│ 3. Includes type hints and docstrings_                              │
└─────────────────────────────────────────────────────────────────────┘

Actions:
• Press ENTER       → Adds new line (does NOT submit)
• Press CTRL+ENTER  → Submits entire multi-line command
• Press ESC         → Exits multi-line mode, returns to single-line
• Press SHIFT+ENTER → Adds new line (same as Enter in this mode)
```

## 3. History Navigation

### Scenario: Navigate through 3 previous commands

```
History Stack (newest first):
[3] /model switch to opus
[2] write unit tests for auth.py
[1] explain how async/await works

Current: [empty]
```

### Step-by-Step Navigation

**Initial State:**
```
│ Single-line | Enter: Submit | Shift+Enter: Multi-line mode | ↑↓: H │
│ _                                                                   │
```

**Press ↑ (once):**
```
│ Single-line | Enter: Submit | Shift+Enter: Multi-line mode | ↑↓: H │
│ /model switch to opus_                                             │
```
*Shows most recent command [3]*

**Press ↑ (twice):**
```
│ Single-line | Enter: Submit | Shift+Enter: Multi-line mode | ↑↓: H │
│ write unit tests for auth.py_                                      │
```
*Shows previous command [2]*

**Press ↑ (three times):**
```
│ Single-line | Enter: Submit | Shift+Enter: Multi-line mode | ↑↓: H │
│ explain how async/await works_                                     │
```
*Shows oldest command [1]*

**Press ↓ (once):**
```
│ Single-line | Enter: Submit | Shift+Enter: Multi-line mode | ↑↓: H │
│ write unit tests for auth.py_                                      │
```
*Back to command [2]*

**Press ↓ (twice):**
```
│ Single-line | Enter: Submit | Shift+Enter: Multi-line mode | ↑↓: H │
│ /model switch to opus_                                             │
```
*Back to command [3]*

**Press ↓ (three times):**
```
│ Single-line | Enter: Submit | Shift+Enter: Multi-line mode | ↑↓: H │
│ _                                                                   │
```
*Restores original draft (empty in this case)*

## 4. Draft Preservation

### Scenario: Typing a command, then checking history

**Start typing:**
```
│ Single-line | Enter: Submit | Shift+Enter: Multi-line mode | ↑↓: H │
│ create a REST API endpoint for_                                    │
```
*Draft: "create a REST API endpoint for"*

**Press ↑ to check history:**
```
│ Single-line | Enter: Submit | Shift+Enter: Multi-line mode | ↑↓: H │
│ /model switch to opus_                                             │
```
*Draft saved automatically*

**Press ↓ to restore:**
```
│ Single-line | Enter: Submit | Shift+Enter: Multi-line mode | ↑↓: H │
│ create a REST API endpoint for_                                    │
```
*Draft restored - can continue typing*

## 5. Mode Switching Flow

### From Single-Line to Multi-Line and Back

```
┌─────────────────────────────────────────────────────────────────┐
│                      SINGLE-LINE MODE                           │
│  • Type: "explain decorators"                                   │
│  • Press: SHIFT+ENTER                                           │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                      MULTI-LINE MODE                            │
│  • Current text: "explain decorators"                           │
│  • Press ENTER: Adds "\n" (new line)                            │
│  • Continue typing: "with practical examples"                   │
│  • Press CTRL+ENTER: Submits entire command                     │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                      COMMAND SUBMITTED                          │
│  • Input cleared                                                │
│  • Mode: Back to SINGLE-LINE                                    │
│  • Command added to history                                     │
└─────────────────────────────────────────────────────────────────┘
```

## 6. Autocomplete Integration

### Slash Commands Work in Both Modes

**Single-Line Mode with Autocomplete:**
```
┌─────────────────────────────────────────────────────────────────┐
│ ╭─ Slash Commands ─╮                                            │
│ │ /model  Switch Claude model (Sonnet/Opus/Haiku)              │
│ │ /help   Show help and available commands                     │
│ │ /commit Create a git commit with changes                     │
│ └─────────────────────────────────────────────────────────────┘ │
├─────────────────────────────────────────────────────────────────┤
│ Single-line | Enter: Submit | Shift+Enter: Multi-line mode | ↑↓ │
│ /m_                                                              │
└─────────────────────────────────────────────────────────────────┘

• Type "/"  → Dropdown appears
• Type "/m" → Filters to commands starting with /m
• Press ↑↓  → Navigate autocomplete (NOT history when visible)
• Press TAB or ENTER → Select highlighted command
• Press ESC → Close dropdown
```

## 7. Command Output Display

### Single-Line Command Output:
```
╔══════════════════════════════════════════════════════════════════╗
║ ⏱ 14:32:10 ┊ ⚡ Command: explain decorators                      ║
╚══════════════════════════════════════════════════════════════════╝

📝 Response: [Claude's response here]
```

### Multi-Line Command Output:
```
╔══════════════════════════════════════════════════════════════════╗
║ ⏱ 14:35:22 ┊ ⚡ Command: write a Python function that: [...]    ║
╚══════════════════════════════════════════════════════════════════╝

📝 Response: [Claude's response here]
```
*Note: Multi-line commands show first line + "[...]" to save space*

## 8. Keyboard Shortcuts Reference Card

```
┌────────────────────────────────────────────────────────────────────┐
│                    KEYBOARD SHORTCUTS                              │
├────────────────────────────────────────────────────────────────────┤
│                                                                    │
│  SINGLE-LINE MODE:                                                 │
│    Enter          → Submit command                                 │
│    Shift+Enter    → Switch to multi-line mode                      │
│    ↑ (Up Arrow)   → Previous command in history                    │
│    ↓ (Down Arrow) → Next command in history (or restore draft)     │
│    /              → Show slash command autocomplete                │
│                                                                    │
│  MULTI-LINE MODE:                                                  │
│    Ctrl+Enter     → Submit command                                 │
│    Enter          → Add new line                                   │
│    Shift+Enter    → Add new line (same as Enter)                   │
│    Esc            → Exit multi-line mode                           │
│                                                                    │
│  AUTOCOMPLETE (WHEN VISIBLE):                                      │
│    ↑ / ↓          → Navigate options                               │
│    Enter / Tab    → Select highlighted option                      │
│    Esc            → Close dropdown                                 │
│                                                                    │
│  HISTORY:                                                          │
│    • Stores last 100 commands per session                          │
│    • Avoids consecutive duplicates                                 │
│    • Preserves current draft when navigating                       │
│    • Only active in single-line mode                               │
│                                                                    │
└────────────────────────────────────────────────────────────────────┘
```

## 9. Common Workflows

### Workflow 1: Quick Single-Line Commands
```
1. Type: "what is the weather"
2. Press: Enter
3. Result: Command submitted immediately
```

### Workflow 2: Complex Multi-Line Prompt
```
1. Press: Shift+Enter (enter multi-line mode)
2. Type:  "Write a FastAPI endpoint that:
           - Handles user authentication
           - Returns JWT tokens
           - Includes error handling"
3. Press: Ctrl+Enter
4. Result: Entire prompt submitted to Claude
```

### Workflow 3: Reusing Previous Commands
```
1. Press: ↑ (show last command)
2. Press: ↑ (show previous command)
3. Press: Enter (submit that command)
4. Result: Historical command re-executed
```

### Workflow 4: Modifying Historical Command
```
1. Press: ↑ (show last command: "write tests for api.py")
2. Edit:  Change to "write tests for auth.py"
3. Press: Enter
4. Result: Modified command submitted and added to history
```

## 10. Visual State Diagram

```
                     ┌─────────────────┐
                     │   APPLICATION   │
                     │     START       │
                     └────────┬────────┘
                              │
                              ▼
                     ┌─────────────────┐
                     │  SINGLE-LINE    │◄────────┐
                     │     MODE        │         │
                     └────────┬────────┘         │
                              │                   │
                 Shift+Enter  │  Enter           │
                              │  submits         │
                              ▼                   │
                     ┌─────────────────┐         │
                     │  MULTI-LINE     │         │
                     │     MODE        │         │
                     └────────┬────────┘         │
                              │                   │
                Ctrl+Enter    │  Esc             │
                submits       │  exits           │
                              ▼                   │
                     ┌─────────────────┐         │
                     │   COMMAND       │─────────┘
                     │   SUBMITTED     │
                     └─────────────────┘
                              │
                              ├─→ Add to history
                              ├─→ Clear input
                              └─→ Return to single-line mode
```

## 11. Error Handling

### Empty Command Submission
```
User Action: Press Enter with empty input
Result: Nothing happens (no error, no submission)
```

### History Navigation with No History
```
User Action: Press ↑ when history is empty
Result: Nothing happens (input unchanged)
```

### Autocomplete with No Matches
```
User Action: Type "/xyz" (no matching commands)
Result: Dropdown automatically closes
```

## 12. Tips and Tricks

### Tip 1: Quick Multi-Line Toggle
Instead of typing a long prompt in single-line mode, press `Shift+Enter` first to switch to multi-line, then type comfortably.

### Tip 2: History Search Shortcut
Use `↑` repeatedly to find a specific command, or keep `↓` pressed to skip through quickly.

### Tip 3: Draft Safety
Start typing a complex command, then press `↑` to check history. Your draft is automatically saved and can be restored with `↓`.

### Tip 4: Autocomplete + Multi-Line
Type "/" to get autocomplete, select a slash command, press `Shift+Enter` to add multi-line arguments.

### Tip 5: Command Editing
Press `↑` to recall a command, edit it, then submit. The new version is added to history.

---

## Quick Start Example

**Try this sequence to learn the feature:**

1. Type: `hello world`
2. Press: `Enter` (submits)
3. Type: `second command`
4. Press: `Enter` (submits)
5. Press: `↑` (shows "second command")
6. Press: `↑` (shows "hello world")
7. Press: `↓` (shows "second command")
8. Press: `↓` (empty/draft)
9. Press: `Shift+Enter` (multi-line mode)
10. Type: `line 1`
11. Press: `Enter` (adds newline)
12. Type: `line 2`
13. Press: `Ctrl+Enter` (submits)
14. Press: `↑` (shows full multi-line command)

**Congratulations! You've mastered multi-line input and command history!**

---

*For detailed technical documentation, see `MULTILINE_HISTORY_IMPLEMENTATION.md`*
*For integration instructions, see `INTEGRATION_GUIDE.md`*
