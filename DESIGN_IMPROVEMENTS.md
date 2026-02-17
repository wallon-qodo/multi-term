# Claude Multi-Terminal UI Improvements
## Design Documentation & Implementation Guide

---

## Executive Summary

This document outlines comprehensive UI/UX improvements to transform the Claude Multi-Terminal application into a modern, professional terminal tool with enhanced usability and visual appeal. The improvements focus on three key areas:

1. **Resizable Panes** - Dynamic layout control via mouse drag
2. **Mouse Text Selection** - Native text selection and clipboard integration
3. **Homebrew Terminal Color Scheme** - Modern, professional color palette

---

## 1. Resizable Panes Implementation

### Current State
- **File**: `/Users/wallonwalusayi/claude-multi-terminal/claude_multi_terminal/widgets/session_grid.py`
- **Layout**: Fixed Grid with automatic column/row calculations
- **Limitation**: No user control over pane sizes

### Design Vision

```
┌─────────────────────────────────────────────────────────┐
│  ● Session 1          │  ● Session 2                    │
│                       │                                  │
│  Drag this edge ───>  ┃  <─── to resize                 │
│                       │                                  │
├───────────────────────┼──────────────────────────────────┤
│  ● Session 3          │  ● Session 4                    │
│                       ┃                                  │
│  Drag vertically ─────┃  for height control             │
│                       │                                  │
└─────────────────────────────────────────────────────────┘

Visual Feedback:
- Divider changes color on hover (dim → bright)
- Cursor changes to resize indicator (↔ or ↕)
- Smooth resize with live preview
- Minimum pane size enforcement (30 cols / 10 rows)
```

### Technical Architecture

#### Option A: Container-Based (Recommended)
**Using Textual's Container system with dynamic sizing**

```python
from textual.containers import Container, Horizontal, Vertical
from textual.widget import Widget
from textual import events

class ResizablePane(Container):
    """Container with resizable borders."""

    DEFAULT_CSS = """
    ResizablePane {
        height: auto;
        width: auto;
        min-width: 30;
        min-height: 10;
    }

    ResizablePane .resize-handle-vertical {
        width: 1;
        height: 1fr;
        background: $border;
        &:hover {
            background: $accent;
            cursor: ew-resize;
        }
    }

    ResizablePane .resize-handle-horizontal {
        width: 1fr;
        height: 1;
        background: $border;
        &:hover {
            background: $accent;
            cursor: ns-resize;
        }
    }
    """

    def __init__(self, content: Widget, **kwargs):
        super().__init__(**kwargs)
        self.content = content
        self.is_resizing = False
        self.resize_start_pos = None
        self.resize_start_size = None

    def compose(self):
        yield self.content
        yield Static(classes="resize-handle-vertical")

    def on_mouse_down(self, event: events.MouseDown):
        # Check if click is on resize handle
        if self._is_on_handle(event):
            self.is_resizing = True
            self.resize_start_pos = (event.x, event.y)
            self.resize_start_size = (self.size.width, self.size.height)
            self.capture_mouse()

    def on_mouse_move(self, event: events.MouseMove):
        if self.is_resizing:
            delta_x = event.x - self.resize_start_pos[0]
            delta_y = event.y - self.resize_start_pos[1]

            new_width = max(30, self.resize_start_size[0] + delta_x)
            new_height = max(10, self.resize_start_size[1] + delta_y)

            self.styles.width = new_width
            self.styles.height = new_height

            self.refresh(layout=True)

    def on_mouse_up(self, event: events.MouseUp):
        if self.is_resizing:
            self.is_resizing = False
            self.release_mouse()
```

#### Option B: Custom Splitter Widget
**Following pattern of professional terminal apps like tmux**

```python
class Splitter(Widget):
    """Interactive divider between panes."""

    DEFAULT_CSS = """
    Splitter {
        width: 1;
        background: $border;
    }

    Splitter:hover {
        background: $accent;
    }

    Splitter.vertical {
        width: 1;
        height: 1fr;
    }

    Splitter.horizontal {
        width: 1fr;
        height: 1;
    }
    """

    def __init__(self, orientation: str = "vertical", **kwargs):
        super().__init__(**kwargs)
        self.orientation = orientation
        self.is_dragging = False

    def render(self) -> str:
        if self.orientation == "vertical":
            return "┃" * self.size.height
        else:
            return "━" * self.size.width
```

### Implementation Strategy

**Phase 1: Replace Grid with Container Layout**
```python
# New: ResizableSessionGrid
class ResizableSessionGrid(Container):
    """Container managing resizable session panes."""

    def compose(self):
        # For 2 panes: Horizontal([Pane1, Splitter, Pane2])
        # For 4 panes: Vertical([
        #     Horizontal([Pane1, Splitter, Pane2]),
        #     Splitter(orientation="horizontal"),
        #     Horizontal([Pane3, Splitter, Pane4])
        # ])

        yield Horizontal(
            ResizablePane(SessionPane(...), id="pane-1"),
            Splitter(orientation="vertical"),
            ResizablePane(SessionPane(...), id="pane-2"),
        )
```

**Phase 2: Add Mouse Event Handlers**
- Capture mouse down on splitter
- Track mouse move while dragging
- Recalculate pane sizes dynamically
- Persist sizes to user preferences

**Phase 3: Visual Polish**
- Add hover effects
- Change cursor on splitter hover
- Animate resize transitions (subtle)
- Show size hints during drag

### User Experience Flow

1. **Hover** → Divider highlights (rgb(70,70,90) → rgb(100,150,255))
2. **Click & Hold** → Cursor changes to resize indicator
3. **Drag** → Live preview with dimension tooltip
4. **Release** → Lock new size, persist preference
5. **Double-Click Divider** → Reset to equal distribution

### Persistence Strategy

```python
# ~/.config/claude-multi-terminal/layout.json
{
    "layout": {
        "pane_1": {"width": "45%", "height": "50%"},
        "pane_2": {"width": "55%", "height": "50%"},
        "pane_3": {"width": "45%", "height": "50%"},
        "pane_4": {"width": "55%", "height": "50%"}
    }
}
```

---

## 2. Mouse Text Selection & Copy/Paste

### Current State
- **File**: `/Users/wallonwalusayi/claude-multi-terminal/claude_multi_terminal/widgets/session_pane.py`
- **Widget**: `RichLog` for terminal output
- **Limitation**: No native text selection, only keyboard copy (Ctrl+C)

### Design Vision

```
┌────────────────────────────────────────────┐
│ ● Session 1                                │
│                                            │
│ ╔═══════════════════════════════╗         │
│ ║ ⏱ 12:34:56 ┊ ⚡ Command: test ║         │
│ ╚═══════════════════════════════╝         │
│                                            │
│ 📝 Response:                               │
│ ┌─────────────────────────────┐           │
│ │ Selected text appears      │  ← Click   │
│ │ with highlight background  │    & Drag  │
│ └─────────────────────────────┘           │
│                                            │
│ Right-click menu:                          │
│ ┌─────────────┐                           │
│ │ 📋 Copy     │                           │
│ │ 📄 Copy All │                           │
│ │ 🗑 Clear    │                           │
│ └─────────────┘                           │
└────────────────────────────────────────────┘

Selection Behavior:
- Click & drag to select text
- Double-click to select word
- Triple-click to select line
- Shift+click to extend selection
- Selection persists until clicked away
```

### Technical Architecture

#### Approach 1: Enhanced RichLog Widget
**Extend Textual's RichLog with selection capabilities**

```python
class SelectableRichLog(RichLog):
    """RichLog with mouse text selection support."""

    DEFAULT_CSS = """
    SelectableRichLog {
        /* Standard RichLog styling */
    }

    SelectableRichLog .selected-text {
        background: rgba(100, 150, 255, 0.3);
        color: inherit;
    }
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.selection_start = None
        self.selection_end = None
        self.is_selecting = False

    def on_mouse_down(self, event: events.MouseDown):
        """Start text selection."""
        if event.button == 1:  # Left click
            self.selection_start = self._get_text_position(event)
            self.is_selecting = True
            self.capture_mouse()

    def on_mouse_move(self, event: events.MouseMove):
        """Update selection end position."""
        if self.is_selecting:
            self.selection_end = self._get_text_position(event)
            self._highlight_selection()
            self.refresh()

    def on_mouse_up(self, event: events.MouseUp):
        """Finalize selection."""
        if self.is_selecting:
            self.is_selecting = False
            self.release_mouse()

            # Copy to clipboard if Ctrl held
            if event.ctrl:
                self._copy_selection()

    def _get_text_position(self, event: events.MouseEvent) -> tuple:
        """Convert mouse coordinates to text position (line, column)."""
        # Calculate line number from scroll offset + mouse Y
        line_idx = self.scroll_y + event.y

        # Find column in line based on X coordinate
        if line_idx < len(self.lines):
            line = self.lines[line_idx]
            col_idx = self._x_to_column(line, event.x)
            return (line_idx, col_idx)

        return (0, 0)

    def _highlight_selection(self):
        """Apply highlight styling to selected text."""
        if not (self.selection_start and self.selection_end):
            return

        start_line, start_col = self.selection_start
        end_line, end_col = self.selection_end

        # Ensure start < end
        if (start_line, start_col) > (end_line, end_col):
            start_line, start_col, end_line, end_col = \
                end_line, end_col, start_line, start_col

        # Apply selection styling
        for line_idx in range(start_line, end_line + 1):
            if line_idx < len(self.lines):
                line = self.lines[line_idx]

                # Determine column range for this line
                if line_idx == start_line == end_line:
                    col_start, col_end = start_col, end_col
                elif line_idx == start_line:
                    col_start, col_end = start_col, len(line)
                elif line_idx == end_line:
                    col_start, col_end = 0, end_col
                else:
                    col_start, col_end = 0, len(line)

                # Apply highlight (implementation depends on Rich internals)
                self._apply_highlight(line_idx, col_start, col_end)

    def _copy_selection(self):
        """Copy selected text to clipboard."""
        selected_text = self._get_selected_text()
        if selected_text:
            self.app.clipboard_manager.copy_to_system(selected_text)
            self.app.notify("📋 Copied to clipboard", severity="information")

    def _get_selected_text(self) -> str:
        """Extract plain text from selection."""
        if not (self.selection_start and self.selection_end):
            return ""

        start_line, start_col = self.selection_start
        end_line, end_col = self.selection_end

        # Ensure start < end
        if (start_line, start_col) > (end_line, end_col):
            start_line, start_col, end_line, end_col = \
                end_line, end_col, start_line, start_col

        # Extract text
        lines = []
        for line_idx in range(start_line, end_line + 1):
            if line_idx < len(self.lines):
                line = self.lines[line_idx]
                text = "".join(seg.text for seg in line._segments)

                if line_idx == start_line == end_line:
                    lines.append(text[start_col:end_col])
                elif line_idx == start_line:
                    lines.append(text[start_col:])
                elif line_idx == end_line:
                    lines.append(text[:end_col])
                else:
                    lines.append(text)

        return "\n".join(lines)
```

#### Approach 2: Text Selection Overlay
**Non-invasive overlay widget for selection visualization**

```python
class SelectionOverlay(Widget):
    """Transparent overlay for text selection."""

    def __init__(self, target_widget: RichLog, **kwargs):
        super().__init__(**kwargs)
        self.target = target_widget
        self.selection = None

    def render(self) -> RenderableType:
        """Render selection highlight boxes."""
        if not self.selection:
            return ""

        # Draw highlight rectangles over selected areas
        # This approach allows selection without modifying RichLog
        ...
```

### Implementation Strategy

**Phase 1: Enable Mouse Capture**
```python
# In SessionPane.compose()
def compose(self) -> ComposeResult:
    # Replace RichLog with SelectableRichLog
    yield SelectableRichLog(
        classes="terminal-output",
        id=f"output-{self.session_id}",
        highlight=True,
        markup=True,
        auto_scroll=True,
        max_lines=10000,
        wrap=True,
        # NEW: Enable mouse capture
        can_focus=True,
        mouse_capture=True
    )
```

**Phase 2: Add Context Menu**
```python
class OutputContextMenu(OptionList):
    """Right-click context menu for output area."""

    def compose(self):
        yield Option("📋 Copy Selection", id="copy")
        yield Option("📄 Copy All", id="copy-all")
        yield Option("🔍 Search", id="search")
        yield Option("🗑 Clear Output", id="clear")
```

**Phase 3: Clipboard Integration**
```python
# Enhanced clipboard manager
class ClipboardManager:
    def copy_to_system(self, text: str) -> bool:
        """Copy text to system clipboard with fallbacks."""
        # Try pbcopy (macOS)
        try:
            subprocess.run(['pbcopy'], input=text.encode(), check=True)
            return True
        except:
            pass

        # Try xclip (Linux)
        try:
            subprocess.run(['xclip', '-selection', 'clipboard'],
                         input=text.encode(), check=True)
            return True
        except:
            pass

        # Try clip (Windows)
        try:
            subprocess.run(['clip'], input=text.encode(), check=True)
            return True
        except:
            pass

        # Fallback: OSC 52 escape sequence (terminal clipboard)
        try:
            import base64
            encoded = base64.b64encode(text.encode()).decode()
            print(f"\033]52;c;{encoded}\a", end="", flush=True)
            return True
        except:
            return False
```

### User Experience Flow

1. **Click & Drag** → Selection highlight appears in real-time
2. **Release** → Selection persists with subtle highlight
3. **Ctrl+C / Cmd+C** → Copy selected text to clipboard + notification
4. **Right-Click** → Show context menu
5. **Click elsewhere** → Clear selection

### Accessibility Considerations
- Keyboard-only selection (Shift + Arrow keys)
- Screen reader support for selection announcements
- High contrast selection colors for visibility
- Configurable selection color in theme

---

## 3. Homebrew Terminal Color Scheme

### Current State
- **File**: `/Users/wallonwalusayi/claude-multi-terminal/claude_multi_terminal/theme.py`
- **Style**: Custom RGB colors (dark blue-gray theme)
- **Goal**: Modern, professional homebrew-inspired palette

### Design Philosophy

**Homebrew Terminal Characteristics:**
- Warm, muted tones (not pure black/white)
- Subtle gradients for depth
- Amber/gold accents for highlights
- High contrast for readability
- "Retro-modern" aesthetic

### New Color Palette

```python
@dataclass
class HomebrewTheme:
    """Professional homebrew-inspired color palette."""

    # Background Colors (Warm Charcoal)
    BG_PRIMARY = "rgb(24,24,24)"        # Main background (true black avoided)
    BG_SECONDARY = "rgb(32,32,32)"      # Secondary panels
    BG_TERTIARY = "rgb(40,40,40)"       # Elevated elements
    BG_INPUT = "rgb(36,36,36)"          # Input fields
    BG_HEADER = "rgb(28,28,28)"         # Headers (slightly lighter)

    # Accent Colors (Amber & Copper)
    ACCENT_PRIMARY = "rgb(255,183,77)"    # Primary accent (amber gold)
    ACCENT_SECONDARY = "rgb(255,213,128)" # Light amber
    ACCENT_SUCCESS = "rgb(174,213,129)"   # Muted green
    ACCENT_WARNING = "rgb(255,167,38)"    # Orange
    ACCENT_ERROR = "rgb(239,83,80)"       # Muted red
    ACCENT_INFO = "rgb(100,181,246)"      # Steel blue

    # Text Colors (Warm Grays)
    TEXT_PRIMARY = "rgb(224,224,224)"     # Main text (off-white)
    TEXT_SECONDARY = "rgb(189,189,189)"   # Secondary text
    TEXT_DIM = "rgb(117,117,117)"         # Dimmed text
    TEXT_BRIGHT = "rgb(255,255,255)"      # Pure white (sparingly)
    TEXT_AMBER = "rgb(255,193,7)"         # Accent text

    # Border Colors (Subtle Separation)
    BORDER_DEFAULT = "rgb(66,66,66)"      # Default borders
    BORDER_FOCUS = "rgb(255,183,77)"      # Focused borders (amber)
    BORDER_SUBTLE = "rgb(48,48,48)"       # Subtle dividers

    # Terminal ANSI Colors (Homebrew-adjusted)
    ANSI_BLACK = "rgb(40,40,40)"
    ANSI_RED = "rgb(239,83,80)"
    ANSI_GREEN = "rgb(174,213,129)"
    ANSI_YELLOW = "rgb(255,213,128)"
    ANSI_BLUE = "rgb(100,181,246)"
    ANSI_MAGENTA = "rgb(206,147,216)"
    ANSI_CYAN = "rgb(128,222,234)"
    ANSI_WHITE = "rgb(224,224,224)"

    # Bright variants
    ANSI_BRIGHT_BLACK = "rgb(117,117,117)"
    ANSI_BRIGHT_RED = "rgb(244,143,177)"
    ANSI_BRIGHT_GREEN = "rgb(200,230,201)"
    ANSI_BRIGHT_YELLOW = "rgb(255,241,118)"
    ANSI_BRIGHT_BLUE = "rgb(144,202,249)"
    ANSI_BRIGHT_MAGENTA = "rgb(225,190,231)"
    ANSI_BRIGHT_CYAN = "rgb(178,235,242)"
    ANSI_BRIGHT_WHITE = "rgb(255,255,255)"

    # Status Colors (Semantic)
    STATUS_ACTIVE = "rgb(174,213,129)"    # Green
    STATUS_INACTIVE = "rgb(117,117,117)"  # Dim gray
    STATUS_PROCESSING = "rgb(255,213,128)" # Amber
    STATUS_ERROR = "rgb(239,83,80)"       # Red

    # Semantic UI Colors
    SUCCESS = "rgb(174,213,129)"
    WARNING = "rgb(255,213,128)"
    ERROR = "rgb(239,83,80)"
    INFO = "rgb(100,181,246)"
```

### Visual Mockup

```
╔═══════════════════════════════════════════════════════════════╗
║  ● Claude Multi-Terminal    |  2 Sessions  |  📡 Broadcast  ║  ← rgb(28,28,28)
╠═══════════════════════════════════════════════════════════════╣
║                                                               ║
║  ┌───────────────────────────┬───────────────────────────┐   ║
║  │ ● Session 1              │ ● Session 2              │   ║  ← Border: rgb(66,66,66)
║  │                           │                           │   ║     Focus: rgb(255,183,77)
║  │ ╔═════════════════════╗   │ ╔═════════════════════╗   │   ║
║  │ ║ ⚡ test command     ║   │ ║ ⚡ another cmd      ║   ║  ← Amber accent
║  │ ╚═════════════════════╝   │ ╚═════════════════════╝   │   ║
║  │                           │                           │   ║
║  │ Response output...        │ Output here...            │   ║  ← rgb(224,224,224)
║  │                           │                           │   ║
║  │ ┌─────────────────────┐   │ ┌─────────────────────┐   │   ║
║  │ │ ⌨ Enter command... │   │ │ ⌨ Enter command... │   ║  ← rgb(36,36,36)
║  │ └─────────────────────┘   │ └─────────────────────┘   │   ║
║  └───────────────────────────┴───────────────────────────┘   ║
║                                                               ║
╠═══════════════════════════════════════════════════════════════╣
║  Ctrl+N: New | Ctrl+W: Close | Ctrl+C: Copy | F2: Mouse    ║  ← rgb(28,28,28)
╚═══════════════════════════════════════════════════════════════╝
```

### Implementation Changes

**1. Update theme.py**
```python
# Complete theme replacement
from dataclasses import dataclass

@dataclass
class HomebrewTheme:
    # ... (colors from above)
    pass

# Global instance
theme = HomebrewTheme()
```

**2. Update SessionPane CSS**
```python
# In session_pane.py
SessionPane {
    border: heavy $border-default;  # rgb(66,66,66)
    background: $bg-secondary;      # rgb(32,32,32)
}

SessionPane:focus-within {
    border: heavy $accent-primary;  # rgb(255,183,77)
    background: $bg-tertiary;       # rgb(40,40,40)
}

SessionPane .session-header {
    background: $bg-header;         # rgb(28,28,28)
    color: $text-amber;             # rgb(255,193,7)
    border-bottom: solid $border-subtle;
}

SessionPane .terminal-output {
    background: $bg-primary;        # rgb(24,24,24)
    color: $text-primary;           # rgb(224,224,224)
}

SessionPane .command-input {
    background: $bg-input;          # rgb(36,36,36)
    border-top: heavy $border-default;
}
```

**3. Update App CSS**
```python
# In app.py
Screen {
    background: $bg-primary;  # rgb(24,24,24)
}

Toast.-information {
    background: rgba(100,181,246,0.2);  # Blue info
    border: solid $accent-info;
    color: $text-primary;
}

Toast.-warning {
    background: rgba(255,183,77,0.2);   # Amber warning
    border: solid $accent-warning;
    color: $text-amber;
}

Toast.-error {
    background: rgba(239,83,80,0.2);    # Red error
    border: solid $accent-error;
    color: $error;
}
```

### Design Rationale

**Why Homebrew Colors?**
1. **Professional & Modern**: Used by thousands of developers daily
2. **Terminal-Native**: Designed specifically for terminal aesthetics
3. **High Contrast**: Excellent readability in both dark environments
4. **Familiar**: Reduces cognitive load for terminal users
5. **Warm Tones**: More comfortable for extended viewing

**Color Psychology:**
- **Amber/Gold**: Attention, warmth, professionalism
- **Warm Grays**: Sophistication, neutrality
- **Muted Pastels**: Reduce eye strain vs. bright neon
- **Charcoal Black**: Modern, clean, less harsh than pure black

---

## Implementation Roadmap

### Phase 1: Foundation (Week 1)
- [ ] Update theme.py with HomebrewTheme
- [ ] Apply new colors throughout app CSS
- [ ] Update all widgets to use theme variables
- [ ] Visual regression testing

### Phase 2: Mouse Selection (Week 2)
- [ ] Implement SelectableRichLog widget
- [ ] Add mouse event handlers
- [ ] Integrate with clipboard manager
- [ ] Add context menu
- [ ] Test cross-platform clipboard

### Phase 3: Resizable Panes (Week 3)
- [ ] Replace Grid with Container layout
- [ ] Implement Splitter widget
- [ ] Add mouse drag handlers
- [ ] Add visual feedback
- [ ] Implement persistence

### Phase 4: Polish & Testing (Week 4)
- [ ] Smooth animations
- [ ] Edge case handling
- [ ] Performance optimization
- [ ] Documentation
- [ ] User testing

---

## Technical Considerations

### Performance
- **Resize Operations**: Debounce layout recalculations (max 60 FPS)
- **Text Selection**: Use efficient line-based indexing
- **Color Updates**: Leverage Textual's reactive CSS system

### Cross-Platform
- **macOS**: pbcopy for clipboard
- **Linux**: xclip/xsel for clipboard
- **Windows**: clip.exe for clipboard
- **Fallback**: OSC 52 escape sequences

### Accessibility
- Keyboard alternatives for all mouse operations
- High contrast mode support
- Screen reader compatibility
- Configurable color themes

### Backward Compatibility
- Keep existing keyboard shortcuts
- Maintain current configuration format
- Graceful degradation for old terminals

---

## Testing Strategy

### Unit Tests
```python
# test_resizable_panes.py
def test_splitter_drag():
    """Test splitter responds to drag events."""

def test_minimum_pane_size():
    """Test panes don't shrink below minimum."""

def test_layout_persistence():
    """Test layout saves and restores."""

# test_text_selection.py
def test_selection_basic():
    """Test click-drag text selection."""

def test_selection_copy():
    """Test copying selected text to clipboard."""

def test_selection_clear():
    """Test selection clears on click."""

# test_theme.py
def test_color_contrast():
    """Test colors meet WCAG contrast ratios."""

def test_theme_consistency():
    """Test all widgets use theme colors."""
```

### Integration Tests
```python
# test_ui_integration.py
def test_resize_and_select():
    """Test resize doesn't break text selection."""

def test_theme_and_selection():
    """Test selection visible in new theme."""
```

### Manual Testing Checklist
- [ ] Resize panes in all directions
- [ ] Select text in each pane
- [ ] Copy/paste across applications
- [ ] Test with 1, 2, 3, 4 sessions
- [ ] Test on different terminal sizes
- [ ] Test with different terminal emulators
- [ ] Verify colors on different displays

---

## User Documentation Updates

### New Keybindings
```
F2              - Toggle mouse mode (app control ↔ text selection)
Ctrl+C / Cmd+C  - Copy selected text or output
```

### New Mouse Interactions
```
Click & Drag    - Select text in output area
Right-Click     - Show context menu
Drag Divider    - Resize panes
Double-Click    - Select word / Reset pane size
```

### Configuration
```toml
# ~/.config/claude-multi-terminal/config.toml

[theme]
name = "homebrew"  # or "classic", "custom"

[layout]
persist_sizes = true
min_pane_width = 30
min_pane_height = 10

[mouse]
enable_selection = true
enable_resize = true
```

---

## Success Metrics

### Usability
- [ ] 90% of users find resizing intuitive
- [ ] Text selection works on first attempt
- [ ] Colors improve readability scores

### Performance
- [ ] Resize operations < 16ms (60 FPS)
- [ ] No lag during text selection
- [ ] Smooth animations on all platforms

### Adoption
- [ ] 80% of users prefer new color scheme
- [ ] 70% of users utilize resize feature
- [ ] Positive feedback on text selection

---

## Appendix: Unicode Reference

### Box Drawing Characters (U+2500–U+257F)
```
┌─┬─┐   ╔═╦═╗   ╭─┬─╮   ┏━┳━┓
│ │ │   ║ ║ ║   │ │ │   ┃ ┃ ┃
├─┼─┤   ╠═╬═╣   ├─┼─┤   ┣━╋━┫
│ │ │   ║ ║ ║   │ │ │   ┃ ┃ ┃
└─┴─┘   ╚═╩═╝   ╰─┴─╯   ┗━┻━┛
```

### Block Elements (U+2580–U+259F)
```
▀ ▁ ▂ ▃ ▄ ▅ ▆ ▇ █ ▉ ▊ ▋ ▌ ▍ ▎ ▏
▐ ░ ▒ ▓ ▔ ▕ ▖ ▗ ▘ ▙ ▚ ▛ ▜ ▝ ▞ ▟
```

### Geometric Shapes (U+25A0–U+25FF)
```
■ □ ▢ ▣ ▤ ▥ ▦ ▧ ▨ ▩ ▪ ▫ ▬ ▭ ▮ ▯
● ○ ◉ ◎ ◐ ◑ ◒ ◓ ◔ ◕ ◖ ◗ ◘ ◙ ◚ ◛
► ▻ ◄ ◅ ▲ △ ▼ ▽ ◆ ◇ ◈ ◊ ○ ◌ ◍ ◎
```

### Arrows & Indicators
```
← ↑ → ↓ ↔ ↕ ↖ ↗ ↘ ↙ ↚ ↛ ↜ ↝ ↞ ↟
⇐ ⇑ ⇒ ⇓ ⇔ ⇕ ⇖ ⇗ ⇘ ⇙ ⇚ ⇛ ⇜ ⇝ ⇞ ⇟
⟵ ⟶ ⟷ ⟸ ⟹ ⟺ ⟻ ⟼ ⟽ ⟾ ⟿
```

---

## Contact & Feedback

For questions or suggestions regarding these improvements:
- Open an issue on GitHub
- Email: support@claude-multi-terminal.dev
- Slack: #claude-multi-terminal

**Last Updated**: 2026-01-29
**Author**: Claude Sonnet 4.5 (TUI Design Architect)
**Version**: 1.0
