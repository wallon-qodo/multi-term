# Context Menu Design for SelectableRichLog

## Visual Design

The context menu follows the Homebrew theme with amber accents and warm charcoal backgrounds.

### Menu Appearance

```
┌────────────────────────────────┐
│ Copy              Ctrl+C       │  ← Active item (amber on hover)
│ Select All        Ctrl+A       │  ← Active item
│ Clear Selection   Esc          │  ← Disabled (dimmed) when no selection
└────────────────────────────────┘
```

### Color Scheme

**Menu Container:**
- Background: `rgb(32,32,32)` - Secondary background color
- Border: `solid rgb(255,183,77)` - Amber border (primary accent)
- Layer: `overlay` - Appears above all content

**Menu Items (Active):**
- Background: `rgb(32,32,32)` - Matches container
- Text: `rgb(224,224,224)` - Primary text color (off-white)
- Hover Background: `rgb(255,183,77)` - Amber highlight
- Hover Text: `rgb(24,24,24)` - Dark text for contrast

**Menu Items (Disabled):**
- Background: `rgb(32,32,32)` - Matches container
- Text: `rgb(117,117,117)` - Dimmed text color
- No hover effect

### Typography

- Font: Monospace (terminal default)
- Padding: 0 horizontal, 2 vertical (inside each item)
- Alignment: Left-aligned label, right-aligned shortcut

## Interaction Flow

### Opening the Menu

1. User right-clicks (button 3) anywhere in the SelectableRichLog widget
2. Context menu appears at cursor position
3. Menu items are enabled/disabled based on current selection state

### Menu Item States

**Copy:**
- Enabled: When text is selected (selection_start ≠ selection_end)
- Disabled: When no text is selected
- Action: Copies selected text to clipboard via `app.clip_manager`

**Select All:**
- Always enabled
- Action: Selects all text from first line, column 0 to last line, end

**Clear Selection:**
- Enabled: When text is selected
- Disabled: When no text is selected
- Action: Clears current selection

### Dismissing the Menu

The menu can be dismissed by:
1. Clicking outside the menu (any left-click on the RichLog)
2. Pressing Escape key
3. Selecting a menu item (auto-dismiss after action)
4. Right-clicking again (new menu replaces old)

## Keyboard Shortcuts

The context menu displays keyboard shortcuts for each action:

| Action          | Shortcut | Function                                    |
|-----------------|----------|---------------------------------------------|
| Copy            | Ctrl+C   | Copy selected text to clipboard             |
| Select All      | Ctrl+A   | Select all text in the output               |
| Clear Selection | Esc      | Clear current selection or dismiss menu     |

Note: On macOS, shortcuts also work with Cmd key (Cmd+C, Cmd+A)

## Technical Implementation

### Components

1. **MenuItem** (dataclass)
   - `label`: Display text
   - `callback`: Function to execute
   - `enabled`: Whether item is clickable
   - `shortcut`: Keyboard shortcut display

2. **ContextMenu** (Container widget)
   - Positions at x, y coordinates
   - Renders menu items as Labels
   - Handles click events
   - Auto-dismisses on outside click or Escape

3. **SelectableRichLog** (enhanced)
   - Detects right-click (button 3) in `on_mouse_down()`
   - Creates and shows ContextMenu
   - Manages menu lifecycle

### Position Calculation

The menu automatically adjusts position to stay within screen bounds:

```python
# Prevent menu from going off right edge
if menu_x + menu_width > screen_width:
    menu_x = max(0, screen_width - menu_width)

# Prevent menu from going off bottom edge
if menu_y + menu_height > screen_height:
    menu_y = max(0, screen_height - menu_height)
```

## Unicode Characters Used

The menu uses standard ASCII and Unicode box-drawing characters:

- Border: Textual's `solid` border style (single-line box drawing)
- Separator (if needed): `─` (U+2500 - Box Drawings Light Horizontal)

## Accessibility

- **Color Contrast:** High contrast between text and backgrounds
- **Disabled States:** Clearly indicated with dimmed text color
- **Keyboard Navigation:** All actions available via keyboard shortcuts
- **Focus Management:** Menu can be dismissed with Escape

## Example Usage

```python
# In your application with SelectableRichLog
from claude_multi_terminal.widgets.selectable_richlog import SelectableRichLog

class MyApp(App):
    def __init__(self):
        super().__init__()
        # Required: clipboard manager for copy functionality
        self.clip_manager = ClipboardManager()

    def compose(self):
        yield SelectableRichLog()
```

The context menu will automatically appear on right-click!

## Future Enhancements

Possible future additions to the context menu:

- **Paste** - Paste from clipboard (when in input mode)
- **Copy All** - Copy entire output without selecting
- **Find** - Search for text in output
- **Export** - Save output to file
- **Clear Output** - Clear all text in log
- **Line Numbers** - Toggle line number display

## Design Rationale

### Why These Colors?

- **Amber border**: Matches the Homebrew theme's primary accent, creating visual consistency
- **Dark background**: Maintains the terminal aesthetic and reduces eye strain
- **High contrast text**: Ensures readability against dark background
- **Amber hover**: Provides clear visual feedback without being jarring

### Why This Layout?

- **Compact size**: Menu doesn't obstruct too much of the terminal
- **Shortcut alignment**: Right-aligned shortcuts are easy to scan
- **No icons**: Keeps the design clean and terminal-appropriate
- **Simple structure**: Easy to understand at a glance

### Why These Menu Items?

- **Copy**: Most common clipboard operation
- **Select All**: Quick way to select entire output
- **Clear Selection**: Explicit way to deselect (in addition to Escape)
- All three are fundamental text operations

## Homebrew Theme Integration

This implementation fully integrates with the existing Homebrew theme:

```python
# From claude_multi_terminal/theme.py
BG_SECONDARY = "rgb(32,32,32)"      # Menu background
ACCENT_PRIMARY = "rgb(255,183,77)"  # Border and hover
TEXT_PRIMARY = "rgb(224,224,224)"   # Active text
TEXT_DIM = "rgb(117,117,117)"       # Disabled text
BORDER_DEFAULT = "rgb(66,66,66)"    # Separator color
```

All colors are sourced from the established theme, ensuring visual harmony.
