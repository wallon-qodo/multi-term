# Mode Display Feature

## Overview

The StatusBar widget now displays the current application mode with color coding, icons, and contextual hints. This provides visual feedback about which mode the application is in and what actions are available.

## Features

### 1. Mode Indicator Display
- **Left-aligned mode indicator** with icon and name
- **Color-coded border** that changes based on mode
- **Reactive updates** - changes instantly when mode switches

### 2. Mode Color Coding

| Mode | Color | RGB | Icon | Description |
|------|-------|-----|------|-------------|
| NORMAL | Blue | `rgb(100,180,240)` | ⌘ | Window management and navigation |
| INSERT | Green | `rgb(120,200,120)` | ✎ | Input forwarded to active session |
| COPY | Yellow | `rgb(255,180,70)` | 📋 | Scrollback navigation and text selection |
| COMMAND | Coral | `rgb(255,77,77)` | ⚡ | Prefix key command mode |

### 3. Contextual Hints

Each mode displays helpful keyboard shortcuts:

- **NORMAL**: `i:Insert ┊ v:Copy ┊ Ctrl+B:Command`
- **INSERT**: `ESC:Normal ┊ Type to input`
- **COPY**: `ESC:Normal ┊ y:Yank ┊ Arrow:Navigate`
- **COMMAND**: `ESC:Cancel ┊ Enter key binding`

### 4. Visual Design

The status bar uses the OpenClaw theme with:
- Colored borders matching the current mode
- Icon + uppercase mode name (e.g., "⌘ NORMAL")
- Separator-divided hints in gray
- System metrics on the right side
- Broadcast mode indicator when active

## Implementation

### Files Modified

1. **`/claude_multi_terminal/core/modes.py`** (NEW)
   - Mode configuration with colors, icons, descriptions
   - Helper function `get_mode_config()`

2. **`/claude_multi_terminal/widgets/status_bar.py`**
   - Added `current_mode` reactive property
   - Added `watch_current_mode()` to update CSS classes
   - Updated `render()` to display mode indicator and hints
   - Added CSS classes for each mode's border color

3. **`/claude_multi_terminal/app.py`**
   - Updated mode transition methods to set `status_bar.current_mode`
   - Added initialization in `on_mount()`

### Code Structure

```python
# Mode configuration (modes.py)
@dataclass
class ModeConfig:
    color: str
    icon: str
    description: str
    hints: list[str]

MODE_CONFIGS = {
    AppMode.NORMAL: ModeConfig(...),
    AppMode.INSERT: ModeConfig(...),
    AppMode.COPY: ModeConfig(...),
    AppMode.COMMAND: ModeConfig(...),
}

# StatusBar widget
class StatusBar(Static):
    current_mode = reactive(AppMode.NORMAL)

    def watch_current_mode(self, mode: AppMode) -> None:
        """Update CSS classes when mode changes."""
        # Remove all mode classes
        for m in AppMode:
            self.set_class(False, f"-mode-{m.value}")
        # Add current mode class
        self.set_class(True, f"-mode-{mode.value}")
```

### Reactive Updates

The StatusBar uses Textual's reactive properties:
- Changes to `current_mode` trigger `watch_current_mode()`
- CSS classes update automatically
- Border color changes based on CSS class
- Widget re-renders with new mode info

## Usage

### Setting the Mode

From the application:
```python
status_bar = self.query_one(StatusBar)
status_bar.current_mode = AppMode.INSERT
```

### Mode Transitions

The app includes methods for each mode:
```python
def enter_normal_mode(self) -> None:
    self.mode = AppMode.NORMAL
    status_bar = self.query_one(StatusBar)
    status_bar.current_mode = AppMode.NORMAL
```

## Testing

### Manual Testing

Run the test script:
```bash
cd /Users/wallonwalusayi/claude-multi-terminal
python test_mode_display.py
```

This will cycle through all modes, showing:
- Mode indicator changes
- Border color changes
- Contextual hints updates
- Broadcast mode interaction

### Integration Testing

Start the main application:
```bash
python -m claude_multi_terminal
```

Then test mode transitions:
- Press `i` for INSERT mode (green border)
- Press `ESC` for NORMAL mode (blue border)
- Press `v` for COPY mode (yellow border)
- Press `Ctrl+B` for COMMAND mode (coral border)

## Visual Layout

```
┌─────────────────────────────────────────────────────────────┐
│ ┃ ⌘ NORMAL ┃  i:Insert ┊ v:Copy ┊ Ctrl+B:Command  ┊  ...  │ ← Line 1: Mode + Hints + Metrics
│ ^N:New ┊ ^W:Close ┊ ^S:Save ┊ ^R:Rename ┊ ^B:Broadcast ... │ ← Line 2: Key bindings
└─────────────────────────────────────────────────────────────┘
  └─ Border color matches mode (blue for NORMAL)
```

## Broadcast Mode Interaction

When broadcast mode is active:
- Mode indicator still shows current mode
- Additional broadcast indicator appears: `┃ 📡 BROADCAST ┃`
- Broadcast indicator uses coral red background
- Mode hints are still visible before broadcast indicator

## CSS Classes

The StatusBar applies mode-specific CSS classes:
- `-mode-normal` → blue border
- `-mode-insert` → green border
- `-mode-copy` → yellow border
- `-mode-command` → coral border

These classes are mutually exclusive and update reactively.

## Future Enhancements

Possible improvements:
1. Mode-specific keybinding display (show only relevant bindings)
2. Animation on mode transitions
3. Mode history/breadcrumbs
4. Custom mode colors via configuration
5. Sound effects on mode change (optional)
6. Mode-specific status messages
