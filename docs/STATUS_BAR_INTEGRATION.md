# Status Bar Integration Guide

## Overview
The status bar has been updated to display streaming state, token usage, and model information in Phase 4 of the TUIOS-inspired multi-terminal TUI app.

## Status Bar Layout

```
[NORMAL] ⠋ 127 tok (45 tok/s) | Sonnet 4.5 | 1.2K tok ($0.05) | 14:32 | CPU: 45% | MEM: 60% | Darwin
```

### Line 1 Components (Left to Right)
1. **Mode Indicator**: `[NORMAL]`, `[INSERT]`, `[COPY]`, `[COMMAND]`
2. **Streaming Indicator**: `⠋ 127 tok (45 tok/s)` (when active)
3. **Model Name**: `Sonnet 4.5` (shortened from full model name)
4. **Token Usage**: `1.2K tok ($0.05)` (color-coded by cost)
5. **Current Time**: `14:32`
6. **System Metrics**: CPU, MEM, Platform

### Line 2: Mode-specific keybindings (unchanged)

## Integration Points

### From App.py or Session Manager

```python
# Get reference to status bar
status_bar = self.query_one(StatusBar)

# Update streaming state (typically called from StreamMonitor)
status_bar.update_streaming_state(
    state=StreamState.STREAMING,
    speed=45.5,  # tokens per second
    tokens=127   # current stream token count
)

# Update token usage (typically called after request completion)
status_bar.update_token_usage(
    tokens=1234,  # total session tokens
    cost=0.05     # total session cost in USD
)

# Update model name (typically on session start or model change)
status_bar.update_model("claude-sonnet-4-5")
```

### Reactive Properties

The status bar uses Textual reactive properties that automatically trigger UI updates:

```python
# Streaming state
stream_state = reactive(StreamState.IDLE)
streaming_speed = reactive(0.0)
streaming_tokens = reactive(0)

# Token tracking
session_tokens = reactive(0)
session_cost = reactive(0.0)

# Model info
model_name = reactive("claude-sonnet-4.5")
```

### StreamState Enum

```python
class StreamState(Enum):
    IDLE = "idle"           # No active streaming
    CONNECTING = "connecting"  # Establishing connection
    STREAMING = "streaming"    # Active streaming
    COMPLETE = "complete"      # Just completed (shows for 2s)
    ERROR = "error"            # Error occurred
```

## Visual Behavior

### Streaming Indicator
- **Visibility**: Shows when `stream_state != IDLE`
- **Animation**: Braille spinner at 10fps when `STREAMING`
- **Fade**: Remains visible for 2 seconds after `COMPLETE`
- **Format**: `⠋ 127 tok (45 tok/s)`
- **Color**: Blue spinner, gray text

### Model Name
- **Shortened Names**:
  - `claude-opus-4-6` → `Opus 4.6`
  - `claude-sonnet-4-5` → `Sonnet 4.5`
  - `claude-haiku-4-5` → `Haiku 4.5`
- **Color**: Coral red `rgb(255,77,77)`
- **Future**: Tooltip on hover with full model name

### Token Usage
- **Format**: `1.2K tok ($0.05)`
- **Color Coding**:
  - Green `rgb(120,200,120)`: < $0.10
  - Yellow `rgb(255,180,70)`: $0.10 - $1.00
  - Red `rgb(255,77,77)`: > $1.00
- **Number Formatting**:
  - < 1000: Show exact count
  - ≥ 1000: Format as `1.2K`, `15.6K`, etc.

## Example Integration Workflow

### 1. Session Start
```python
# Initialize status bar with model
status_bar.update_model("claude-sonnet-4-5")
status_bar.update_token_usage(0, 0.0)
```

### 2. Request Initiated
```python
# Start streaming indicator
status_bar.update_streaming_state(
    state=StreamState.CONNECTING,
    speed=0.0,
    tokens=0
)
```

### 3. During Streaming
```python
# Update real-time (every 100ms)
status_bar.update_streaming_state(
    state=StreamState.STREAMING,
    speed=current_speed,
    tokens=tokens_so_far
)
```

### 4. Request Complete
```python
# Mark as complete (fades after 2s)
status_bar.update_streaming_state(
    state=StreamState.COMPLETE,
    speed=final_speed,
    tokens=total_tokens
)

# Update session totals
status_bar.update_token_usage(
    tokens=session_total_tokens,
    cost=session_total_cost
)
```

## Performance Notes

- **Update Frequency**: Streaming updates at 10fps (100ms)
- **Refresh Overhead**: < 10ms per update
- **Spinner Animation**: Managed via `set_interval` timer
- **Auto-fade**: Uses `set_timer` for delayed state transitions

## Future Enhancements (Not in Phase 4)

1. **Click Interactions**:
   - Click model name to show full model details
   - Click token usage to show detailed breakdown
   - Click streaming indicator to show request history

2. **Advanced Metrics**:
   - Average response time
   - Cache hit rate
   - Request success rate

3. **Session Management**:
   - Show active session name
   - Multi-session token totals
   - Session switching indicator

## File Changes Summary

### `/claude_multi_terminal/widgets/status_bar.py`

**Lines 1-21**: Added imports and StreamState enum
- Added `datetime`, `Enum` imports
- Added StreamState enum definition (temporary until Agent 1 creates stream_monitor)

**Lines 62-77**: Added reactive properties
- `stream_state`, `streaming_speed`, `streaming_tokens`
- `session_tokens`, `session_cost`
- `model_name`
- Internal animation state

**Lines 91-163**: Added methods
- `watch_stream_state()`: React to streaming state changes
- `_update_spinner()`: Animate spinner at 10fps
- `update_streaming_state()`: Public API for streaming updates
- `update_token_usage()`: Public API for token updates
- `update_model()`: Public API for model updates
- `_get_short_model_name()`: Model name formatting
- `_format_token_count()`: Token count formatting with K suffix
- `_get_cost_color()`: Cost-based color selection

**Lines 178-227**: Updated render method
- Added streaming indicator with animation (lines 178-194)
- Added model name display (lines 196-200)
- Added token usage with color coding (lines 202-207)
- Added current time display (lines 224-227)

## Testing Checklist

- [ ] Streaming indicator appears when state != IDLE
- [ ] Spinner animates smoothly at 10fps
- [ ] Streaming indicator fades after 2 seconds on COMPLETE
- [ ] Token counts format correctly (1.2K for thousands)
- [ ] Cost colors update correctly (green/yellow/red)
- [ ] Model names shorten correctly (Opus 4.6, Sonnet 4.5, etc.)
- [ ] Time updates every minute
- [ ] No layout breakage with long model names
- [ ] Status bar remains at 3 lines height
- [ ] Colors match HomebrewTheme (coral red, blue, green, yellow)

## Dependencies

**Requires from Agent 1 (StreamMonitor)**:
- `StreamState` enum
- `StreamMonitor` class with state tracking
- Integration with Claude API streaming

**Requires from Agent 2 (TokenTracker)**:
- `TokenTracker` class with usage tracking
- `MODEL_PRICING` for cost calculations
- Token counting for streaming responses

**Note**: Current implementation includes a temporary `StreamState` enum in `status_bar.py` that will be replaced with the import from `stream_monitor` once Agent 1 completes their work.
