# ResizableSessionGrid Drag-to-Resize Implementation

## Overview

The `ResizableSessionGrid` now supports interactive drag-to-resize functionality for session panes. Users can click and drag the splitter dividers between panes to dynamically adjust their sizes.

## Implementation Summary

### File Modified
- `/Users/wallonwalusayi/claude-multi-terminal/claude_multi_terminal/widgets/resizable_grid.py`

### Key Components

#### 1. Splitter Widget (Enhanced)
The `Splitter` widget now tracks mouse drag operations properly:

**Mouse Event Handling:**
- `on_mouse_down()`: Captures mouse and tracks drag start position
- `on_mouse_move()`: Calculates incremental delta from last position
- `on_mouse_up()`: Releases mouse capture and ends drag

**Key Features:**
- Uses `event.screen_x` and `event.screen_y` for absolute screen coordinates
- Tracks both initial drag position and last position for smooth incremental updates
- Posts `SplitterDragged` messages with delta values
- Visual feedback with "dragging" CSS class (gold highlight)

```python
def on_mouse_move(self, event: events.MouseMove) -> None:
    """Handle drag movement."""
    if self.is_dragging:
        # Calculate incremental delta from last position for smooth dragging
        if self.orientation == "vertical":
            delta = event.screen_x - self.last_x
            self.last_x = event.screen_x
        else:
            delta = event.screen_y - self.last_y
            self.last_y = event.screen_y

        # Only notify if there's actual movement
        if delta != 0:
            self.post_message(SplitterDragged(splitter=self, delta=delta))
        event.stop()
```

#### 2. SplitterDragged Message (Updated)
Changed from `offset` to `delta` to support incremental updates:

```python
class SplitterDragged(events.Message):
    """Message sent when a splitter is dragged."""

    def __init__(self, splitter: Splitter, delta: int):
        super().__init__()
        self.splitter = splitter
        self.delta = delta  # Incremental change from last position
```

#### 3. ResizableSessionGrid (Implemented)

**Main Handler:**
```python
def on_splitter_dragged(self, message: SplitterDragged) -> None:
    """Handle splitter drag events to resize panes."""
    splitter = message.splitter
    orientation = splitter.orientation
    parent = splitter.parent

    if orientation == "vertical":
        self._resize_vertical_panes(splitter, parent, message.delta)
    else:
        self._resize_horizontal_panes(splitter, parent, message.delta)
```

**Vertical Resize Algorithm:**
```python
def _resize_vertical_panes(self, splitter: Splitter, parent: Widget, delta_x: int):
    """Resize left/right panes."""

    # 1. Find adjacent panes (left and right of splitter)
    # 2. Get current rendered sizes
    # 3. Apply incremental delta
    # 4. Enforce minimum sizes (30 characters)
    # 5. Convert to fractional units using integer scale (1000)
    # 6. Apply new styles

    left_pane.styles.width = f"{left_fr}fr"
    right_pane.styles.width = f"{right_fr}fr"
```

**Horizontal Resize Algorithm:**
```python
def _resize_horizontal_panes(self, splitter: Splitter, parent: Widget, delta_y: int):
    """Resize top/bottom panes."""

    # Same algorithm as vertical but for height
    # Minimum height: 10 lines

    top_pane.styles.height = f"{top_fr}fr"
    bottom_pane.styles.height = f"{bottom_fr}fr"
```

## How It Works

### 1. User Interaction Flow
```
User clicks splitter → on_mouse_down() captures mouse
User drags mouse → on_mouse_move() calculates delta and posts message
Grid receives message → on_splitter_dragged() dispatches to resize method
Resize method calculates new sizes → applies fractional units
Textual re-layouts → panes resize visually
User releases mouse → on_mouse_up() ends drag
```

### 2. Incremental Delta Tracking
Instead of calculating delta from drag start (which would cause jumps), we track the last mouse position and calculate incremental deltas:

```
Drag start: x=100
Move 1: x=105 → delta=5 → resize by 5
Move 2: x=108 → delta=3 → resize by 3
Move 3: x=107 → delta=-1 → resize by -1 (reverse)
```

This provides smooth, continuous resizing that follows the cursor precisely.

### 3. Fractional Unit Conversion
Textual's flex layout uses fractional units (fr) for proportional sizing. We convert absolute pixel/character sizes to fractional units:

```python
# Get current sizes
left_width = 80, right_width = 120
total_width = 200

# Apply delta
delta_x = 10
new_left_width = 90, new_right_width = 110

# Convert to fractional units (scale=1000 for precision)
left_fr = int(90 * 1000 / 200) = 450
right_fr = int(110 * 1000 / 200) = 550

# Apply as "450fr" and "550fr"
```

This maintains proportional sizing while allowing precise control.

### 4. Minimum Size Enforcement
Each pane has minimum dimensions to ensure usability:
- **Width**: 30 characters minimum
- **Height**: 10 lines minimum

When a drag would violate these limits, the resize is clamped:

```python
if new_left_width < min_width:
    new_left_width = min_width
    new_right_width = total_width - new_left_width
elif new_right_width < min_width:
    new_right_width = min_width
    new_left_width = total_width - new_right_width
```

### 5. Visual Feedback
The splitter provides immediate visual feedback during dragging:

```css
Splitter {
    background: rgb(66,66,66);  /* Default: dark gray */
}

Splitter:hover {
    background: rgb(255,183,77);  /* Hover: orange */
}

Splitter.dragging {
    background: rgb(255,213,128);  /* Dragging: lighter gold */
}
```

## Supported Layouts

### 2 Panes (Side-by-Side)
```
┌─────────────┃─────────────┐
│   Left      ┃    Right    │
│   Pane      ┃    Pane     │
└─────────────┃─────────────┘
```
- 1 vertical splitter
- Resizable horizontally

### 3 Panes (2 Top, 1 Bottom)
```
┌──────┃──────┐
│ Top  ┃ Top  │
│ Left ┃Right │
╞══════════════╡
│   Bottom     │
└──────────────┘
```
- 1 vertical splitter (top row)
- 1 horizontal splitter (between rows)

### 4 Panes (2x2 Grid)
```
┌──────┃──────┐
│ Top  ┃ Top  │
│ Left ┃Right │
╞══════╪══════╡
│Bottom┃Bottom│
│ Left ┃Right │
└──────┃──────┘
```
- 2 vertical splitters (one per row)
- 1 horizontal splitter (between rows)

### 5+ Panes (Dynamic Rows)
```
┌──────┃──────┐
│ Row1 ┃ Row1 │
│ Left ┃Right │
╞══════╪══════╡
│ Row2 ┃ Row2 │
│ Left ┃Right │
╞══════╪══════╡
│ Row3 ┃ Row3 │
│ Left ┃Right │
└──────┃──────┘
```
- Multiple horizontal splitters between rows
- Vertical splitters within each row

## Technical Details

### Mouse Coordinate Systems
- `event.x`, `event.y`: Relative to widget
- `event.screen_x`, `event.screen_y`: Absolute screen coordinates
- We use screen coordinates for accurate cross-widget tracking

### Why Incremental Deltas?
Using incremental deltas (change from last position) instead of absolute offsets (change from start) prevents:
- Jumps when mouse moves quickly
- Synchronization issues between mouse and layout
- Accumulation of errors from repeated calculations

### Fractional Unit Precision
We use a scale factor of 1000 to preserve precision while using integer fractional units:
- `500fr` and `500fr` = 50/50 split
- `333fr` and `667fr` = 33/67 split
- `750fr` and `250fr` = 75/25 split

This allows smooth resizing without floating-point rounding errors.

### Performance Considerations
- Resize events are throttled by mouse move rate (typically 60-120 Hz)
- Only panes with actual size changes trigger re-layout
- Textual's virtual DOM efficiently updates only changed regions
- Incremental deltas minimize computational overhead

## Testing

A test application is provided at `/Users/wallonwalusayi/claude-multi-terminal/test_resizable_grid.py`:

```bash
# Activate virtual environment
source venv/bin/activate

# Run test application
python test_resizable_grid.py

# Use keyboard shortcuts:
# - 1: Switch to 1-pane layout
# - 2: Switch to 2-pane layout
# - 3: Switch to 3-pane layout
# - 4: Switch to 4-pane layout
# - q: Quit
```

The test app displays real-time size information in each pane and allows testing of all resize scenarios.

## Usage in Application

The resize functionality is automatically available in `ResizableSessionGrid`. Users can:

1. **Hover over divider**: Splitter changes to orange
2. **Click and drag**: Splitter becomes gold, panes resize in real-time
3. **Release mouse**: Final layout is applied

No configuration or additional code is required - the feature is fully integrated.

## Future Enhancements

Possible improvements for future versions:

1. **Persistent Layouts**: Save and restore custom pane sizes
2. **Snap Points**: Snap to common splits (25%, 50%, 75%)
3. **Double-Click Reset**: Double-click splitter to reset to equal sizes
4. **Keyboard Resize**: Use keyboard shortcuts to resize panes
5. **Layout Presets**: Quick access to predefined layouts
6. **Resize Animations**: Smooth animated transitions between sizes

## Summary

The drag-to-resize functionality is now fully implemented and provides:

- Smooth, responsive resizing with visual feedback
- Minimum size constraints for usability
- Support for all layout configurations (2-4+ panes)
- Efficient incremental updates with no performance impact
- Intuitive interaction model matching standard GUI conventions

The implementation leverages Textual's event system, CSS styling, and flexible layout engine to provide a professional, native-feeling resize experience in the terminal.
