# Enterprise Design - Quick Reference Card

## Color Palette Quick Reference

### Copy-Paste RGB Values

```python
# Backgrounds
BG_MAIN       = "rgb(15,15,22)"
BG_PANE       = "rgb(20,20,28)"
BG_ELEVATED   = "rgb(25,25,35)"
BG_INPUT      = "rgb(30,30,40)"
BG_HEADER     = "rgb(40,40,55)"

# Accents
BLUE          = "rgb(100,150,255)"
LIGHT_BLUE    = "rgb(150,200,255)"
GREEN         = "rgb(100,255,150)"
ORANGE        = "rgb(255,180,50)"
RED           = "rgb(255,100,100)"
CYAN          = "rgb(100,200,255)"

# Text
TEXT_MAIN     = "rgb(220,220,240)"
TEXT_DIM      = "rgb(120,120,150)"
TEXT_BRIGHT   = "rgb(240,245,255)"

# Borders
BORDER_DEFAULT = "rgb(70,70,90)"
BORDER_FOCUS   = "rgb(100,150,255)"
```

## Box Drawing Quick Reference

### Copy-Paste Characters

```
Single Line:        Double Line:        Rounded:            Heavy:
┌─┬─┐              ╔═╦═╗              ╭─┬─╮              ┏━┳━┓
├─┼─┤              ╠═╬═╣              ├─┼─┤              ┣━╋━┫
└─┴─┘              ╚═╩═╝              ╰─┴─╯              ┗━┻━┛

Separators:         Dashed:
│ ┊ ┃ ┆            ┄ ┅ ┆ ┇
```

## Icon Quick Reference

### Copy-Paste Icons

```
Status:
● ○ ⚡ 💤 ✓ ❌ ⚠ 💡

Actions:
⌨ 🖱 📋 💾 ✏ 📡 🕐 📊 🔖 📝

Borders:
┃ ┊ ═ ─ ━ ┄
```

## Component Templates

### Command Separator
```python
separator = Text()
separator.append("\n\n")
separator.append("╔" + "═" * 78 + "╗\n", style="bold rgb(100,180,255)")
separator.append("║ ", style="bold rgb(100,180,255)")
separator.append("⏱ 14:30:45 ", style="dim cyan")
separator.append("┊ ", style="dim white")
separator.append("⚡ Command: ", style="bold rgb(150,220,255)")
separator.append(command, style="bold rgb(255,220,100)")
separator.append(" ║\n", style="bold rgb(100,180,255)")
separator.append("╚" + "═" * 78 + "╝\n", style="bold rgb(100,180,255)")
```

### Completion Marker
```python
end_marker = Text()
end_marker.append("\n")
end_marker.append("╭" + "─" * 78 + "╮\n", style="dim rgb(100,255,150)")
end_marker.append("│ ", style="dim rgb(100,255,150)")
end_marker.append("✓ ", style="bold bright_green")
end_marker.append("Response complete", style="dim rgb(150,255,150)")
end_marker.append(" │\n", style="dim rgb(100,255,150)")
end_marker.append("╰" + "─" * 78 + "╯\n", style="dim rgb(100,255,150)")
```

### Session Header
```python
header = Text()
header.append("● ", style="bold bright_green")  # or "○" for inactive
header.append("┃ ", style="dim white")
header.append(session_name, style="bold white")
header.append("  ┊  ", style="dim white")
header.append(f"📊 {count} cmd", style="dim cyan")
header.append("  ┊  ", style="dim white")
header.append(f"ID: {session_id[:6]}", style="dim rgb(150,150,180)")
```

### Status Bar Line
```python
status = Text()
status.append("┃ ", style="dim rgb(100,150,255)")
status.append("Ready", style="bold bright_green")
status.append(" ┃", style="dim rgb(100,150,255)")
status.append("  CPU: ", style="dim white")
status.append("45%", style="bold bright_green")
status.append("  ┊  MEM: ", style="dim white")
status.append("62%", style="bold bright_green")
```

## CSS Templates

### Pane Border Focus
```css
SessionPane {
    border: heavy rgb(70,70,90);
    background: rgb(20,20,28);
}

SessionPane:focus-within {
    border: heavy rgb(100,150,255);
    background: rgb(22,22,30);
}
```

### Gradient Header
```css
.session-header {
    background: linear-gradient(90deg, rgb(40,40,55) 0%, rgb(50,50,65) 100%);
    color: rgb(200,220,255);
    border-bottom: solid rgb(80,80,100);
}

:focus-within .session-header {
    background: linear-gradient(90deg, rgb(50,70,120) 0%, rgb(60,90,150) 100%);
    color: rgb(240,245,255);
    border-bottom: solid rgb(100,150,255);
}
```

### Input Field
```css
.command-input {
    background: rgb(30,30,40);
    border-top: heavy rgb(80,80,100);
    padding: 0 2;
}

:focus-within .command-input {
    background: rgb(35,35,50);
    border-top: heavy rgb(100,150,255);
}
```

## Notification Templates

### Information
```python
self.notify(
    "✓ Operation successful",
    severity="information"
)
```

### Warning
```python
self.notify(
    "⚠ Warning message",
    severity="warning"
)
```

### Error
```python
self.notify(
    "❌ Error occurred",
    severity="error"
)
```

## Color Thresholds

### Metric Colors
```python
def get_metric_color(value: float) -> str:
    if value < 50:
        return "bright_green"
    elif value < 80:
        return "bright_yellow"
    else:
        return "bright_red"
```

### Session Count Badge
```python
def get_badge_color(count: int) -> str:
    return "bright_green" if count <= 4 else "bright_yellow"
```

## Spacing Guidelines

```
Screen Padding:      1-2 cells
Component Padding:   1-2 cells
Grid Gutter:         1 cell
Input Padding:       0-2 horizontal
Header Height:       3 rows
Status Bar Height:   3 rows
```

## Typography Hierarchy

```
Level 1 (Title):     Bold rgb(150,200,255) + Icons
Level 2 (Header):    Bold rgb(200,220,255)
Level 3 (Label):     Bold white
Body:                rgb(220,220,240)
Caption:             dim white / dim cyan
```

## Focus Indicator Pattern

```
Unfocused:
- Border: rgb(70,70,90) heavy
- Header: gray gradient
- Status: ○ (hollow dot)

Focused:
- Border: rgb(100,150,255) heavy
- Header: blue gradient
- Status: ● (solid dot)
```

## Activity State Pattern

```
Active (processing):
- Dot: ● bright_green
- Border: blue when focused
- Counter: visible

Idle (waiting):
- Dot: ○ dim white
- Border: gray when unfocused
- Counter: visible
```

## Separator Usage

```
Between elements:    ┊ (light)
Between sections:    ┃ (heavy)
Subtle division:     ┄ (dashed)
Standard border:     │ (single)
```

## Animation Timing

```
Fast transitions:    0.1s (focus states)
Medium transitions:  0.3s (mode changes)
No animation:        0s (text output, scrolling)
```

## Z-Index Hierarchy

```
Background:          0
Panes:               1
Dialogs:             10
Notifications:       20
```

## Responsive Breakpoints

```
1 session:   1x1 (fullscreen)
2 sessions:  2x1 (side-by-side)
3 sessions:  2x2 (one empty)
4 sessions:  2x2 (full grid)
5-6 sessions: 2x3 (scrollable)
```

## Common Patterns

### Status Badge
```
"● 2 Active"  - Green dot + count
"○ 0 Active"  - Gray dot + count
```

### Timestamp
```
"⏱ 14:30:45"  - Clock icon + time
"🕐 14:30"     - Simple clock + time
```

### Metric Display
```
"CPU: 45%"    - Green if <50
"CPU: 75%"    - Yellow if 50-80
"CPU: 95%"    - Red if >80
```

### Command Display
```
"⚡ Command: help"     - Lightning + command
"📝 Response:"         - Note + response
"✓ Response complete" - Check + completion
```

## File Organization

```
theme.py           - Color constants
app.py             - Main CSS
session_pane.py    - Component styles
header_bar.py      - Header rendering
status_bar.py      - Status rendering
rename_dialog.py   - Dialog styles
```

## Testing Checklist

- [ ] Colors render correctly
- [ ] Box drawing displays properly
- [ ] Icons appear (not boxes/squares)
- [ ] Borders align perfectly
- [ ] Focus states change color
- [ ] Metrics update in real-time
- [ ] Notifications styled correctly
- [ ] Dialog renders centered
- [ ] Grid layout adapts
- [ ] Text is readable

## Terminal Requirements

- True color support (24-bit)
- Unicode/UTF-8 encoding
- Modern monospace font
- Minimum 80x24 characters
- COLORTERM=truecolor

## Quick Fixes

### Colors wrong?
```bash
export COLORTERM=truecolor
```

### Box drawing broken?
```bash
export LANG=en_US.UTF-8
```

### Icons show as boxes?
Install a modern font (Fira Code, JetBrains Mono)

## Performance Tips

- Batch Rich Text operations
- Cache metric calculations
- Debounce rapid updates
- Lazy render off-screen content
- Minimize layout recalculations

---

**Remember**: Every visual element should serve a purpose. Form follows function in enterprise design.
