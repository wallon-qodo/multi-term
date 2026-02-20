# Stream Monitor API Reference

## Module: `claude_multi_terminal.streaming.stream_monitor`

### Classes

---

## `StreamState` (Enum)

Stream lifecycle states.

**Values:**
- `IDLE = "idle"` - No activity
- `THINKING = "thinking"` - Model thinking before stream starts
- `STREAMING = "streaming"` - Actively receiving tokens
- `COMPLETE = "complete"` - Stream finished successfully
- `ERROR = "error"` - Stream failed

---

## `StreamingSession` (Dataclass)

Container for streaming session data.

**Attributes:**
- `session_id: UUID` - Unique identifier for this stream
- `state: StreamState` - Current state of the stream
- `start_time: float` - When streaming started (Unix timestamp)
- `end_time: Optional[float]` - When streaming ended (None if active)
- `tokens_received: int` - Total tokens received so far
- `current_speed: float` - Current streaming speed (tokens/sec)
- `buffer: List[str]` - Recent output chunks for display
- `error_message: Optional[str]` - Error details if state is ERROR

**Methods:**

### `duration() -> float`
Get duration of stream in seconds.

**Returns:** Duration from start_time to end_time (or current time if active)

### `is_active() -> bool`
Check if stream is currently active.

**Returns:** True if state is THINKING or STREAMING

---

## `StreamMonitor`

Monitor and track streaming response sessions. Thread-safe.

**Class Constants:**
- `SPINNER_FRAMES: List[str]` - 10 Braille spinner characters
- `BUFFER_SIZE: int = 50` - Maximum buffer entries per session
- `SPEED_WINDOW: float = 2.0` - Speed calculation window (seconds)

**Properties:**

### `active_streams: Dict[UUID, StreamingSession]`
Get all active streaming sessions (read-only copy).

### `total_tokens_received: int`
Get total tokens received across all sessions.

### `total_streams_completed: int`
Get total number of completed streams.

**Methods:**

### `__init__()`
Initialize stream monitor.

---

### `start_stream(session_id: Optional[UUID] = None, thinking: bool = False) -> UUID`

Start a new streaming session.

**Args:**
- `session_id` - Optional UUID to use (generates new if None)
- `thinking` - If True, start in THINKING state

**Returns:** Session ID for this stream

**Example:**
```python
# Start in streaming state
session_id = monitor.start_stream()

# Start in thinking state
session_id = monitor.start_stream(thinking=True)
```

---

### `update_stream(session_id: UUID, token_count: int = 1, content: Optional[str] = None) -> bool`

Update stream with new tokens/content.

**Args:**
- `session_id` - ID of stream to update
- `token_count` - Number of new tokens received (default: 1)
- `content` - Optional content chunk to add to buffer

**Returns:** True if successful, False if session not found

**Side Effects:**
- Transitions from THINKING → STREAMING on first token
- Updates token count and total statistics
- Recalculates current speed
- Adds content to buffer (if provided)

**Example:**
```python
# Simple token update
monitor.update_stream(session_id, token_count=10)

# With content
monitor.update_stream(session_id, token_count=5, content="Hello world")
```

---

### `end_stream(session_id: UUID, success: bool = True, error_message: Optional[str] = None) -> bool`

Mark stream as complete or failed.

**Args:**
- `session_id` - ID of stream to end
- `success` - True if completed successfully (default: True)
- `error_message` - Error details if success=False

**Returns:** True if successful, False if session not found

**Side Effects:**
- Sets end_time to current timestamp
- Updates state to COMPLETE or ERROR
- Increments total_streams_completed (if success=True)
- Cleans up speed tracking data

**Example:**
```python
# Success
monitor.end_stream(session_id, success=True)

# Error
monitor.end_stream(session_id, success=False, error_message="Network timeout")
```

---

### `get_stream_state(session_id: UUID) -> Optional[StreamingSession]`

Get current state of a stream.

**Args:**
- `session_id` - ID of stream to query

**Returns:** StreamingSession object or None if not found

**Example:**
```python
session = monitor.get_stream_state(session_id)
if session:
    print(f"State: {session.state}")
    print(f"Tokens: {session.tokens_received}")
    print(f"Speed: {session.current_speed} tok/s")
```

---

### `get_active_streams() -> List[StreamingSession]`

Get all currently active streams.

**Returns:** List of StreamingSession objects with state THINKING or STREAMING

**Example:**
```python
active = monitor.get_active_streams()
print(f"Active streams: {len(active)}")
for session in active:
    print(f"  {session.session_id}: {session.tokens_received} tokens")
```

---

### `calculate_speed(session_id: UUID) -> float`

Calculate current streaming speed.

**Args:**
- `session_id` - ID of stream to calculate speed for

**Returns:** Speed in tokens/second, or 0.0 if unavailable

**Algorithm:**
- Uses 2-second rolling window
- Sums tokens in window
- Divides by time span
- Returns 0 if insufficient data

**Example:**
```python
speed = monitor.calculate_speed(session_id)
print(f"Current speed: {speed:.1f} tok/s")
```

---

### `remove_stream(session_id: UUID) -> bool`

Remove a stream from active tracking.

**Args:**
- `session_id` - ID of stream to remove

**Returns:** True if removed, False if not found

**Side Effects:**
- Removes from active_streams dict
- Cleans up speed tracking data

---

### `clear_completed() -> int`

Remove all completed/error streams.

**Returns:** Number of streams removed

**Example:**
```python
cleared = monitor.clear_completed()
print(f"Cleared {cleared} completed streams")
```

---

### `get_spinner_frame() -> str`

Get current spinner animation frame.

**Returns:** Single character spinner frame

**Side Effects:**
- Updates internal spinner index (~10 FPS)
- Thread-safe with lock

**Example:**
```python
frame = monitor.get_spinner_frame()
print(f"Spinner: {frame}")  # e.g., "⠋"
```

---

### `format_stream_indicator(session_id: UUID, include_speed: bool = True) -> Optional[str]`

Format visual indicator for a stream.

**Args:**
- `session_id` - ID of stream to format
- `include_speed` - Whether to include speed information (default: True)

**Returns:** Formatted indicator string or None if session not found

**Format by state:**
- THINKING: `"⠋ Thinking..."`
- STREAMING (with speed): `"⠋ 127 tok (45 tok/s)"`
- STREAMING (no speed): `"⠋ 127 tok"`
- COMPLETE: `"✓ 500 tok (52 tok/s avg)"`
- ERROR: `"✗ Network timeout"`

**Example:**
```python
indicator = monitor.format_stream_indicator(session_id)
print(indicator)  # "⠹ 127 tok (45 tok/s)"

# Without speed
indicator = monitor.format_stream_indicator(session_id, include_speed=False)
print(indicator)  # "⠹ 127 tok"
```

---

### `get_stats() -> Dict[str, any]`

Get overall streaming statistics.

**Returns:** Dictionary with statistics:
- `total_tokens_received: int` - Total tokens across all streams
- `total_streams_completed: int` - Number of completed streams
- `active_streams: int` - Number of currently active streams
- `active_sessions: List[str]` - Session IDs as strings

**Example:**
```python
stats = monitor.get_stats()
print(f"Total tokens: {stats['total_tokens_received']}")
print(f"Completed: {stats['total_streams_completed']}")
print(f"Active: {stats['active_streams']}")
```

---

## Helper Functions

### `get_spinner_frame(frame_index: int = 0) -> str`

Get a specific spinner frame by index.

**Args:**
- `frame_index` - Index of frame to get (0-9, cycles)

**Returns:** Single character spinner frame

**Example:**
```python
from claude_multi_terminal.streaming import get_spinner_frame

for i in range(10):
    frame = get_spinner_frame(i)
    print(frame, end=" ")  # ⠋ ⠙ ⠹ ⠸ ⠼ ⠴ ⠦ ⠧ ⠇ ⠏
```

---

### `get_state_color(state: StreamState) -> Color`

Get Rich Color for a stream state.

**Args:**
- `state` - Stream state to get color for

**Returns:** Rich Color object following HomebrewTheme palette

**Color mapping:**
- IDLE: Gray `(150, 150, 150)`
- THINKING: Yellow `(255, 200, 100)`
- STREAMING: Coral-red `(255, 77, 77)` ← Primary
- COMPLETE: Green `(100, 255, 100)`
- ERROR: Red `(255, 50, 50)`

**Example:**
```python
from claude_multi_terminal.streaming import get_state_color, StreamState

color = get_state_color(StreamState.STREAMING)
print(f"RGB: {color.triplet}")  # RGB: (255, 77, 77)
```

---

## Complete Usage Example

```python
from claude_multi_terminal.streaming import StreamMonitor, StreamState
import time

# Initialize monitor
monitor = StreamMonitor()

# Start stream in thinking phase
session_id = monitor.start_stream(thinking=True)
print(monitor.format_stream_indicator(session_id))
# Output: "⠋ Thinking..."

time.sleep(1)

# Start receiving tokens
for i in range(10):
    monitor.update_stream(session_id, token_count=10, content=f"chunk_{i}")
    indicator = monitor.format_stream_indicator(session_id)
    print(indicator)
    # Output: "⠹ 50 tok (42 tok/s)"
    time.sleep(0.2)

# Complete stream
monitor.end_stream(session_id, success=True)
final = monitor.format_stream_indicator(session_id)
print(final)
# Output: "✓ 100 tok (48 tok/s avg)"

# Get statistics
stats = monitor.get_stats()
print(f"Total tokens: {stats['total_tokens_received']}")
print(f"Completed streams: {stats['total_streams_completed']}")

# Cleanup
monitor.clear_completed()
```

---

## Thread Safety

All public methods are thread-safe using `threading.RLock()`. Safe to use from:
- Multiple concurrent threads
- Event handlers
- Async callbacks
- Timer updates

**Example:**
```python
import threading

monitor = StreamMonitor()

def stream_handler_1():
    sid = monitor.start_stream()
    for _ in range(100):
        monitor.update_stream(sid, token_count=5)
        time.sleep(0.1)
    monitor.end_stream(sid)

def stream_handler_2():
    sid = monitor.start_stream()
    for _ in range(50):
        monitor.update_stream(sid, token_count=10)
        time.sleep(0.2)
    monitor.end_stream(sid)

# Safe concurrent execution
t1 = threading.Thread(target=stream_handler_1)
t2 = threading.Thread(target=stream_handler_2)
t1.start()
t2.start()
t1.join()
t2.join()

print(monitor.get_stats())
```

---

## Performance Notes

- **Memory**: ~1KB per active stream
- **CPU**: Minimal (O(n) where n < 20 speed samples)
- **Lock contention**: Low (short critical sections)
- **Update frequency**: 10 FPS for spinner animation
- **Speed window**: 2-second rolling window

---

**Module**: `claude_multi_terminal.streaming.stream_monitor`
**Version**: Phase 4 - Agent 1
**Lines**: 429
