# Drag-to-Swap Flow Diagram

## Event Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                         USER ACTION                             │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
                    ┌──────────────────┐
                    │  Mouse Down      │
                    │  (Left Button)   │
                    └──────────────────┘
                              │
                              ▼
                    ┌──────────────────┐
                    │  SessionPane:    │
                    │  - Store start   │
                    │    position      │
                    │  - Capture mouse │
                    └──────────────────┘
                              │
                              ▼
                    ┌──────────────────┐
                    │  Mouse Move      │
                    └──────────────────┘
                              │
                              ▼
                    ┌──────────────────┐
                    │  Distance > 5px? │
                    └──────────────────┘
                         │         │
                    NO   │         │  YES
                         │         │
                         │         ▼
                         │    ┌──────────────────────┐
                         │    │  Start Drag:         │
                         │    │  - Add .dragging     │
                         │    │  - Post DragStarted  │
                         │    └──────────────────────┘
                         │              │
                         │              ▼
                         │    ┌──────────────────────┐
                         │    │  ResizableGrid:      │
                         │    │  - Store dragged ID  │
                         │    │  - Highlight targets │
                         │    └──────────────────────┘
                         │              │
                         │              ▼
                         │    ┌──────────────────────┐
                         │    │  Mouse Move (cont)   │
                         │    │  - Update highlights │
                         │    └──────────────────────┘
                         │              │
                         └──────────────┼──────────────┐
                                        ▼              │
                              ┌──────────────────┐    │
                              │  Mouse Up        │    │
                              └──────────────────┘    │
                                        │              │
                         ┌──────────────┴──────────────┤
                         │                             │
                    Dragging?                      Not Dragging
                         │                             │
                    YES  │                             ▼
                         ▼                        (No Action)
              ┌──────────────────────┐
              │  SessionPane:        │
              │  - Find target       │
              │  - Post DragEnded    │
              │  - Remove .dragging  │
              │  - Release mouse     │
              └──────────────────────┘
                         │
                         ▼
              ┌──────────────────────┐
              │  ResizableGrid:      │
              │  - Clear highlights  │
              │  - Check target      │
              └──────────────────────┘
                         │
          ┌──────────────┴──────────────┐
          │                             │
    Valid Target?                  No Target
          │                             │
     YES  │                             ▼
          ▼                        (No Action)
   ┌──────────────────┐
   │  _swap_sessions: │
   │  - Find indices  │
   │  - Swap in list  │
   │  - Rebuild layout│
   │  - Show notify   │
   └──────────────────┘
          │
          ▼
   ┌──────────────────┐
   │   Layout Updated │
   │   Panes Swapped  │
   └──────────────────┘
```

## State Transitions

```
┌────────────┐
│   NORMAL   │  ← Initial state, no drag
└────────────┘
       │
       │ Mouse down + move > 5px
       ▼
┌────────────┐
│  DRAGGING  │  ← Pane semi-transparent, red border
└────────────┘
       │
       │ Mouse up
       ▼
┌────────────┐
│   NORMAL   │  ← Returns to normal state
└────────────┘
```

## Drop Target States

```
Other Panes (not being dragged):

┌────────────┐
│   NORMAL   │
└────────────┘
       │
       │ Drag started
       ▼
┌────────────┐
│DROP TARGET │  ← Highlighted as valid target
└────────────┘
       │
       │ Mouse over this pane
       ▼
┌────────────┐
│DROP ACTIVE │  ← Actively hovered, thicker border
└────────────┘
       │
       │ Mouse moves away or drag ends
       ▼
┌────────────┐
│   NORMAL   │  ← Back to normal
└────────────┘
```

## Message Flow

```
SessionPane                ResizableGrid
    │                          │
    │──── DragStarted ─────────▶│
    │        (session_id)       │
    │                           │
    │                      ┌────┴─────┐
    │                      │ Highlight│
    │                      │  targets │
    │                      └────┬─────┘
    │                           │
    │◀─── set_drop_target ──────┤
    │        (true)              │
    │                           │
    │   ... user drags ...      │
    │                           │
    │──── DragEnded ────────────▶│
    │  (session_id, target_id)  │
    │                           │
    │                      ┌────┴─────┐
    │                      │  Swap    │
    │                      │  panes   │
    │                      └────┬─────┘
    │                           │
    │◀─── set_drop_target ──────┤
    │        (false)             │
    │                           │
```

## CSS Class Application

```
Timeline of CSS classes during drag-and-drop:

t=0: User clicks pane A
  Pane A: [normal state]
  Pane B: [normal state]
  Pane C: [normal state]

t=1: Mouse moves 6px
  Pane A: .dragging              ← Being dragged
  Pane B: .drop-target           ← Can drop here
  Pane C: .drop-target           ← Can drop here

t=2: Mouse over Pane B
  Pane A: .dragging
  Pane B: .drop-target .drop-target-active  ← Active target
  Pane C: .drop-target

t=3: Mouse over Pane C
  Pane A: .dragging
  Pane B: .drop-target           ← No longer active
  Pane C: .drop-target .drop-target-active  ← Now active

t=4: Mouse released over Pane C
  Pane A: [normal state]         ← Drag ended
  Pane B: [normal state]         ← Highlights cleared
  Pane C: [normal state]         ← Highlights cleared

t=5: Layout rebuilt, A and C swapped positions
  [Position swap complete]
```

## Code Locations

### SessionPane (`session_pane.py`)
- **Lines 211-228**: Message class definitions
- **Lines 234-247**: CSS drag styles
- **Lines 463-466**: Drag state initialization
- **Lines 715-770**: Mouse event handlers

### ResizableGrid (`resizable_grid.py`)
- **Line 177**: Drag state variable
- **Lines 547-618**: Drag event handlers and swap logic

## Integration Points

1. **Textual Event System**
   - Uses built-in mouse events (MouseDown, MouseMove, MouseUp)
   - Posts custom messages (DragStarted, DragEnded)
   - Parent widget subscribes to child messages

2. **CSS Styling**
   - Uses Textual's reactive CSS system
   - Classes applied/removed dynamically
   - Smooth transitions via CSS

3. **Layout System**
   - Integrates with existing ResizableSessionGrid
   - Works with current layout algorithms
   - No modifications to BSP tree needed for swaps

## Performance Considerations

- **Mouse tracking**: Only active during drag (capture_mouse)
- **Layout rebuild**: Only on successful swap
- **Visual updates**: CSS-based, hardware accelerated
- **Message passing**: Minimal overhead, stops propagation

## Error Handling

1. **Invalid drop target**: Silently ignored, no swap occurs
2. **Same pane drop**: Filtered by check `target_widget != self`
3. **No target found**: `target_id = None`, swap skipped
4. **Grid not mounted**: Try/except blocks prevent crashes
5. **Mouse capture release**: Protected by try/except
