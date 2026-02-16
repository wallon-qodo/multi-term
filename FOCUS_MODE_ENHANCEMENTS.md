# Focus Mode Enhancements

## Overview

Added two convenient ways to focus/maximize a session to full screen, in addition to the existing F11 key.

## Changes Made

### 1. Ctrl+F Keybinding

**Before:**
- `Ctrl+F` was used for global search
- `F11` was the only way to toggle focus mode

**After:**
- `Ctrl+F` now toggles focus mode (more intuitive shortcut)
- `Ctrl+Shift+F` is now used for global search
- `F11` still works for focus mode (backward compatible)

### 2. Right-Click Context Menu

Added right-click context menu to session panes with the following options:

- **🔍 Focus** - Maximize the clicked session to full screen
- **✏ Rename** - Rename the session
- **✗ Close** - Close the session

## Implementation Details

### Files Modified

**1. `claude_multi_terminal/app.py`**

- Updated keybindings:
  ```python
  Binding("ctrl+f", "toggle_focus", "Focus Mode", priority=True),
  Binding("ctrl+shift+f", "toggle_search", "Search", priority=True),
  ```

- Added session pane context menu handler:
  ```python
  async def on_session_pane_context_menu_requested(self, message) -> None:
      """Handle session pane right-click - show context menu."""
  ```

- Added focus helper method:
  ```python
  async def _focus_session_by_id(self, session_id: str) -> None:
      """Focus/maximize a specific session."""
  ```

- Updated context menu item handler to support "focus" action

**2. `claude_multi_terminal/widgets/session_pane.py`**

- Added `ContextMenuRequested` message class:
  ```python
  class ContextMenuRequested(Message):
      """Posted when session pane is right-clicked."""
  ```

- Added mouse event handler:
  ```python
  def on_mouse_down(self, event: events.MouseDown) -> None:
      """Handle mouse clicks - detect right-click for context menu."""
  ```

## Usage

### Method 1: Ctrl+F (Recommended)

1. Focus on the session you want to maximize (click on it)
2. Press `Ctrl+F`
3. Press `Ctrl+F` again (or `F11`) to exit focus mode

### Method 2: Right-Click Menu

1. Right-click anywhere in a session pane
2. Select "🔍 Focus" from the context menu
3. The session is immediately maximized
4. Press `Ctrl+F` or `F11` to exit focus mode

### Method 3: F11 (Original)

1. Focus on the session you want to maximize
2. Press `F11`
3. Press `F11` again to exit focus mode

## Benefits

1. **More Intuitive**: `Ctrl+F` is a more natural shortcut for "Focus" than `F11`
2. **Discoverable**: Right-click menu makes the feature discoverable without memorizing keys
3. **Flexible**: Can focus any session directly via right-click, not just the currently focused one
4. **Backward Compatible**: `F11` still works for users who prefer it

## Search Functionality

Global search has been moved to `Ctrl+Shift+F` (still available, just different key combo).

## UX Flow

**Entering Focus Mode:**
```
Right-click session → Click "🔍 Focus" → Session maximized
OR
Click session → Press Ctrl+F → Session maximized
OR
Click session → Press F11 → Session maximized
```

**Exiting Focus Mode:**
```
Press Ctrl+F → Return to grid view
OR
Press F11 → Return to grid view
```

## Technical Notes

### Context Menu System

Uses the existing `ContextMenu` widget system that was originally built for tab right-click menus. The session pane context menu includes:

- Focus option (new)
- Rename option (reuses existing functionality)
- Close option (reuses existing functionality)

### Focus Logic

The `_focus_session_by_id()` helper method:
1. Finds the target session pane by ID
2. Sets global focus mode flag
3. Calls grid's `set_focus_mode()` to hide other sessions
4. Shows notification with exit instructions

### Message Flow

```
User right-clicks session pane
  ↓
SessionPane.on_mouse_down() detects right-click
  ↓
Posts SessionPane.ContextMenuRequested message
  ↓
App.on_session_pane_context_menu_requested() handles it
  ↓
Creates and displays ContextMenu widget
  ↓
User clicks "Focus" menu item
  ↓
ContextMenu posts ItemSelected message
  ↓
App.on_context_menu_item_selected() handles it
  ↓
Calls _focus_session_by_id() to maximize session
```

## Testing

### Manual Test Steps

1. **Test Ctrl+F:**
   - Start application
   - Press `Ctrl+F` → Session should maximize
   - Press `Ctrl+F` again → Should return to grid

2. **Test Right-Click:**
   - Right-click on any session pane
   - Context menu should appear with "🔍 Focus" option
   - Click "Focus" → Session should maximize
   - Press `Ctrl+F` or `F11` → Should return to grid

3. **Test Search (Ctrl+Shift+F):**
   - Press `Ctrl+Shift+F` → Global search panel should appear
   - Press `Escape` → Search should close

4. **Test F11 (Backward Compatibility):**
   - Press `F11` → Session should maximize
   - Press `F11` again → Should return to grid

### Expected Behavior

✅ Ctrl+F toggles focus mode for currently focused session
✅ Right-click menu shows focus option
✅ Right-click focus works on any session (not just focused one)
✅ Context menu disappears after selecting an option
✅ Notification shows session name and exit instructions
✅ F11 still works (backward compatible)
✅ Ctrl+Shift+F opens global search

## Future Enhancements

Possible improvements:

1. **Double-click to focus**: Double-clicking session header could toggle focus
2. **Keyboard navigation**: Arrow keys to switch between sessions in grid view
3. **Zoom animation**: Smooth transition animation when entering/exiting focus mode
4. **Focus history**: Quick switch between last focused sessions (Alt+Tab style)
5. **Multi-focus**: Split view with 2-3 focused sessions side by side

---

**Status**: ✓ Complete and Tested
**Date**: 2026-02-16
**Impact**: Major UX improvement - more intuitive and discoverable focus mode
