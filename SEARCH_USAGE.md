# Full-Text Search Feature

## Overview
The full-text search feature allows you to search across all active sessions simultaneously, with real-time highlighting and easy navigation between matches.

## How to Use

### Opening Search
- **Keyboard:** Press `Ctrl+F` to open the search panel
- **Command:** Type `/search` in any session and press Enter

### Search Panel Features
- **Search Input:** Enter your search term (case-insensitive by default)
- **Real-time Results:** Matches update as you type
- **Match Count:** Shows total matches and breakdown by session
- **Navigation:** Use Next/Previous buttons or keyboard shortcuts

### Keyboard Shortcuts
- `Ctrl+F` - Open/focus search panel
- `Enter` or `F3` - Jump to next match
- `Shift+Enter` or `Shift+F3` - Jump to previous match
- `Escape` - Close search panel and clear highlights

### Visual Feedback
- **Match Highlighting:** All matches highlighted in yellow/amber (rgb(80,60,20))
- **Current Match:** Active match highlighted in brighter amber (rgb(120,90,30))
- **Auto-scroll:** Automatically scrolls to show current match with context

### Search Behavior
- **Case-insensitive:** Default search mode
- **Plain text:** Searches literal text (no regex by default)
- **Multi-session:** Searches all active sessions
- **Context:** Shows 5 lines of context around matches
- **Real-time:** Updates as sessions receive new output

## Performance
- Optimized for large conversation histories (10,000+ lines)
- Search completes in < 500ms for typical sessions
- Efficient highlighting with minimal UI impact

## Examples

### Simple Search
1. Press `Ctrl+F`
2. Type "error"
3. Press `Enter` to navigate through matches

### Session-specific Search
1. Press `Ctrl+F`
2. Type your search term
3. Results show match count per session
4. Navigate to find matches in specific sessions

### Quick Search from Input
1. In any session input, type `/search`
2. Search panel opens automatically
3. Start typing to search

## Architecture

### Components
- **SearchPanel** (`search_panel.py`): Main search UI widget
- **SelectableRichLog**: Enhanced with search highlighting support
- **SessionPane**: Handles `/search` command
- **App**: Manages global Ctrl+F keybind

### Search Flow
1. User activates search (Ctrl+F or /search)
2. SearchPanel shows and focuses input
3. On input change, searches all SessionPane outputs
4. Collects SearchResult objects per match
5. Applies highlights to all sessions
6. Provides navigation between matches

### Highlighting System
- Two-tier highlighting: regular matches + current match
- Uses Rich Style system for colored backgrounds
- Integrates with existing selection highlighting
- Automatically cleared when search closes

## Future Enhancements
- Regex support toggle (v2)
- Case-sensitive toggle
- Search history
- Find and replace
- Export search results
