# Search Feature - Quick Start Guide

## What is it?
Find text across all your Claude CLI sessions instantly. Perfect for finding errors, tracking variables, or reviewing past conversations.

## How to use it

### 1. Open Search
**Two ways:**
- Press `Ctrl+F` anywhere
- Type `/search` in any session

### 2. Search
- Type your search term in the search box
- Results appear instantly as you type
- All matches highlighted in yellow

### 3. Navigate Results
- Press `Enter` or `F3` for next match
- Press `Shift+Enter` or `Shift+F3` for previous match
- Click Next/Previous buttons
- Current match shown in brighter yellow

### 4. Close Search
- Press `Escape`
- Click the Close button
- All highlights automatically cleared

## Tips & Tricks

### Quick Navigation
- Use `F3` for rapid navigation between matches
- Sessions auto-scroll to show matches
- 5 lines of context shown around each match

### Match Info
The search panel shows:
- Total number of matches
- Current match position (e.g., "Match 3 of 15")
- Matches per session (e.g., "Session 1: 8, Session 2: 7")

### Best Practices
1. **Be specific**: More specific terms = fewer, better results
2. **Case doesn't matter**: "error", "Error", "ERROR" all match
3. **Use /search**: Quick way to open search from command line
4. **Clear when done**: Press Escape to clear highlights

## Examples

### Find all errors
```
1. Press Ctrl+F
2. Type: error
3. Navigate with Enter
```

### Track a variable
```
1. Press Ctrl+F
2. Type: username
3. Review all mentions across sessions
```

### Find command output
```
1. Press Ctrl+F
2. Type: success
3. See which commands succeeded
```

## Visual Guide

```
┌────────────────────────────────────────────┐
│  Session 1                    Session 2    │
│  > npm install                > git status │
│  Installing packages...       On branch... │
│  ✓ success (highlighted)      All clear    │
│                                             │
│  > npm test                   > npm build  │
│  Running tests...             Building...  │
│  error: test failed           ✓ success    │
│  (highlighted)                (highlighted)│
└────────────────────────────────────────────┘
┌────────────────────────────────────────────┐
│ 🔍 Global Search                           │
│ ┌──────────────────────────────────────┐   │
│ │ success                              │   │
│ └──────────────────────────────────────┘   │
│ [⬆ Prev] [⬇ Next] [✕ Close]               │
│ Match 2 of 3 | Session1: 1, Session2: 2   │
└────────────────────────────────────────────┘
```

## Keyboard Shortcuts Reference

| Shortcut | Action |
|----------|--------|
| `Ctrl+F` | Open search panel |
| `Enter` | Jump to next match |
| `Shift+Enter` | Jump to previous match |
| `F3` | Jump to next match (alternative) |
| `Shift+F3` | Jump to previous match (alternative) |
| `Escape` | Close search and clear highlights |

## Common Questions

### Q: Can I search with regex?
A: Not yet, but it's planned for v2. Current search is literal text only.

### Q: Is search case-sensitive?
A: No, search is case-insensitive by default. "error" matches "Error", "ERROR", etc.

### Q: How far back does search go?
A: Search covers the entire session history (up to 10,000 lines per session).

### Q: Can I search just one session?
A: Search always covers all sessions, but results show per-session counts.

### Q: Does search affect performance?
A: No, search is optimized to complete in under 500ms even for large histories.

### Q: Can I export search results?
A: Not yet, but you can use the copy feature to copy matching lines.

## Troubleshooting

### Search not finding matches
- Check spelling
- Try partial words (e.g., "err" instead of "error")
- Verify text is in session output (not in input only)

### Highlights not showing
- Ensure search panel is open
- Try closing and reopening search (Esc, then Ctrl+F)
- Check that matches exist in visible area

### Navigation not working
- Verify there are matches (check match count)
- Try clicking Next/Prev buttons instead of keyboard
- Close and reopen search panel

## Need Help?
- See full documentation: `docs/SEARCH_FEATURE.md`
- Report issues: GitHub issues
- Keyboard shortcuts: Press `?` in app (if available)
