# Modal System Quick Reference

## Import and Basic Usage

```python
from claude_multi_terminal.modes import (
    AppMode,           # Enum of 4 modes
    ModeState,         # State management
    MODE_CONFIGS,      # Configuration registry
    get_mode_color,    # Utility functions
    get_mode_icon,
)

# Initialize
state = ModeState()  # Starts in NORMAL mode

# Transition
state.transition_to(AppMode.INSERT, trigger="user_key_i")

# Toggle back
state.toggle_previous()

# Check current mode
if state.current_mode == AppMode.INSERT:
    # Handle insert mode
    pass
```

---

## The Four Modes

| Mode | Key | Icon | Color | Cursor | Use Case |
|------|-----|------|-------|--------|----------|
| **NORMAL** | - | ⌨ | Blue | Block | Navigate, manage panes |
| **INSERT** | `i` | ✏ | Green | Bar | Type in terminal |
| **COPY** | `c` | 📋 | Yellow | Underline | Select text, copy |
| **COMMAND** | `:` | ⚡ | Coral | Block | Run system commands |

---

## Key Transitions

### From NORMAL Mode
- Press **i** → INSERT mode (start typing)
- Press **c** → COPY mode (start selecting)
- Press **v** → COPY mode (visual select)
- Press **:** → COMMAND mode (run command)

### Return to NORMAL
- From INSERT: Press **ESC**
- From COPY: Press **ESC** or **y** (yank)
- From COMMAND: Press **ESC** or **ENTER**

---

## Common Patterns

### Mode-Aware Event Handling

```python
def on_key(self, event: events.Key) -> None:
    mode = self.mode_state.current_mode

    if mode == AppMode.NORMAL:
        # Handle navigation keys
        if event.key == "h":
            self.focus_left()
        elif event.key == "i":
            self.mode_state.transition_to(AppMode.INSERT)

    elif mode == AppMode.INSERT:
        # Pass keys to terminal
        if event.key == "escape":
            self.mode_state.transition_to(AppMode.NORMAL)
        else:
            self.terminal.send_key(event.key)

    elif mode == AppMode.COPY:
        # Handle selection
        if event.key == "y":
            self.copy_selection()
            self.mode_state.transition_to(AppMode.NORMAL)
```

### Status Bar Update

```python
def update_status_bar(self):
    config = self.mode_state.get_config()
    self.status_bar.mode_label.update(
        f"{config.icon} {config.display_name}"
    )
    self.status_bar.styles.background = config.color
```

### Custom Mode Handler

```python
class InsertModeHandler:
    def on_enter(self, previous_mode):
        self.terminal.set_cursor_style("bar")
        self.terminal.focus()

    def on_exit(self, next_mode):
        self.terminal.set_cursor_style("block")
        return True  # Allow transition

    def on_key(self, key):
        return False  # Don't consume, pass to terminal

    def on_focus_change(self, has_focus):
        if not has_focus:
            self.mode_state.transition_to(AppMode.NORMAL)

    def can_transition_to(self, target_mode):
        return True, ""  # Allow all transitions

state.register_handler(AppMode.INSERT, InsertModeHandler())
```

---

## Configuration Access

```python
# Get mode configuration
config = MODE_CONFIGS[AppMode.NORMAL]
print(config.display_name)    # "NORMAL"
print(config.color)           # "rgb(100,180,240)"
print(config.icon)            # "⌨"
print(config.cursor_style)    # "block"
print(config.description)     # Full description text

# Or use current mode
current_config = state.get_config()
```

---

## Utility Functions

```python
# Get mode styling
color = get_mode_color(AppMode.INSERT)      # "rgb(120,200,120)"
icon = get_mode_icon(AppMode.COPY)          # "📋"
desc = get_mode_description(AppMode.COMMAND)

# Mode classification
is_input_mode(AppMode.INSERT)        # True
is_input_mode(AppMode.NORMAL)        # False
is_navigation_mode(AppMode.COPY)     # True
is_navigation_mode(AppMode.COMMAND)  # False

# Transition lookup
next_mode = get_mode_transition(AppMode.NORMAL, "i")
# Returns: AppMode.INSERT
```

---

## History and Debugging

```python
# View recent transitions
for trans in state.get_recent_transitions(count=5):
    print(trans)
# Output:
# [✓] NORMAL → INSERT (user_key_i)
# [✗] INSERT → INSERT (blocked: Already in INSERT mode)
# [✓] INSERT → NORMAL (user_key_escape)

# Check specific transition
last_transition = state.history[-1]
print(f"Allowed: {last_transition.allowed}")
print(f"Trigger: {last_transition.trigger}")
print(f"Time: {last_transition.timestamp}")
```

---

## Error Handling

```python
# Transition validation
allowed, reason = state.can_transition_to(AppMode.COPY)
if not allowed:
    print(f"Cannot transition: {reason}")
    return

# Safe transition
if state.transition_to(AppMode.INSERT, trigger="my_action"):
    print("Transition successful")
else:
    print("Transition blocked")
    # Check history for reason
    last = state.history[-1]
    print(f"Reason: {last.reason}")
```

---

## Type Annotations

```python
from typing import Optional
from claude_multi_terminal.modes import AppMode, ModeState, ModeConfig

def handle_mode_change(
    state: ModeState,
    new_mode: AppMode
) -> bool:
    """Transition to new mode with validation."""
    return state.transition_to(new_mode)

def get_mode_styling(mode: AppMode) -> dict[str, str]:
    """Get styling info for a mode."""
    config = MODE_CONFIGS[mode]
    return {
        "color": config.color,
        "icon": config.icon,
        "cursor": config.cursor_style,
    }
```

---

## Testing

```python
# Test mode transitions
state = ModeState()
assert state.current_mode == AppMode.NORMAL

state.transition_to(AppMode.INSERT)
assert state.current_mode == AppMode.INSERT
assert state.previous_mode == AppMode.NORMAL

state.toggle_previous()
assert state.current_mode == AppMode.NORMAL

# Test invalid transition
result = state.transition_to(AppMode.NORMAL)
assert result is False  # Already in NORMAL
```

---

## Best Practices

### 1. Always use the state machine
```python
# ✅ Good
state.transition_to(AppMode.INSERT)

# ❌ Bad
state.current_mode = AppMode.INSERT  # No validation, no history
```

### 2. Use type hints
```python
# ✅ Good
def handle_mode(mode: AppMode) -> None:
    pass

# ❌ Bad
def handle_mode(mode):  # Type unclear
    pass
```

### 3. Check transition validity
```python
# ✅ Good
if state.transition_to(target_mode):
    update_ui()

# ❌ Bad
state.transition_to(target_mode)
update_ui()  # May not have transitioned
```

### 4. Use configuration registry
```python
# ✅ Good
config = MODE_CONFIGS[mode]

# ❌ Bad
if mode == AppMode.NORMAL:
    color = "rgb(100,180,240)"  # Duplicated
```

---

## Integration Checklist

When integrating modes into your app:

- [ ] Import `ModeState` and initialize in app
- [ ] Register mode handlers for custom behavior
- [ ] Update status bar to show current mode
- [ ] Route key events through mode system
- [ ] Apply visual styling based on mode
- [ ] Handle mode transitions on focus changes
- [ ] Add mode indicator to UI
- [ ] Test all transition paths
- [ ] Document mode-specific keybindings
- [ ] Add help overlay for mode keys

---

## Common Issues

### Mode not changing
```python
# Check if transition succeeded
if not state.transition_to(target_mode):
    # Check why it failed
    print(state.history[-1].reason)
```

### Handler not called
```python
# Ensure handler is registered
if mode not in state.handlers:
    state.register_handler(mode, MyHandler())
```

### Wrong mode color
```python
# Use configuration, don't hardcode
config = state.get_config()
self.styles.background = config.color  # ✅
# Not: self.styles.background = "blue"  # ❌
```

---

## File Locations

- **Types**: `/Users/wallonwalusayi/claude-multi-terminal/claude_multi_terminal/modes.py`
- **Documentation**: `/Users/wallonwalusayi/claude-multi-terminal/MODAL_SYSTEM_PHASE1.md`
- **This Reference**: `/Users/wallonwalusayi/claude-multi-terminal/MODAL_SYSTEM_QUICK_REFERENCE.md`

---

**Version**: 1.0.0
**Status**: Production Ready
**Python**: 3.10+
