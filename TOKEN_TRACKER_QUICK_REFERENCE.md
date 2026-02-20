# Token Tracker - Quick Reference

## Import
```python
from claude_multi_terminal.streaming import (
    TokenTracker,
    format_usage_compact,
    format_usage_detailed,
    MODEL_PRICING,
)
```

## Initialize
```python
tracker = TokenTracker()  # Uses ~/.multi-term/token_usage.json
# Or custom path:
tracker = TokenTracker(persistence_path="/custom/path.json")
```

## Track Requests
```python
tracker.track_request(
    session_id="session-123",
    model_name="claude-sonnet-4.5",
    input_tokens=1500,
    output_tokens=800,
    cached_tokens=400,  # Optional, default=0
)
```

## Get Usage
```python
# Session usage
session = tracker.get_session_usage("session-123")
print(session.total_usage.total_tokens)  # 2300
print(session.total_cost_usd)            # 0.02

# Global usage (all sessions)
global_usage = tracker.get_global_usage()
print(global_usage.total_tokens)
```

## Display Formats

### Compact (for status bars)
```python
text = format_usage_compact(session.total_usage, session.model_name)
# Output: "2.3K tok (400 cached) $0.02"
```

### Detailed (for reports)
```python
text = format_usage_detailed(session.total_usage, session.model_name)
# Output: "In: 1.5K tok, Out: 800 tok, Cost: $0.02 (400 cached)"
```

## Model Pricing

| Model | Input/1K | Output/1K |
|-------|----------|-----------|
| claude-opus-4.6 | $0.015 | $0.075 |
| claude-sonnet-4.5 | $0.003 | $0.015 |
| claude-haiku-4.5 | $0.001 | $0.005 |

**Cached tokens**: 90% discount on input

## Example Integration

### Status Bar Update
```python
def update_status(session_id: str):
    session = tracker.get_session_usage(session_id)
    if session:
        return format_usage_compact(session.total_usage, session.model_name)
    return "No usage"
```

### Cost Alert
```python
session = tracker.get_session_usage(session_id)
if session and session.total_cost_usd > 1.0:
    show_warning(f"Session cost: ${session.total_cost_usd:.2f}")
```

## Thread Safety
All methods are thread-safe - use from multiple threads/async tasks safely.

## Data Persistence
- Auto-saves after every `track_request()`
- Auto-loads on initialization
- Default location: `~/.multi-term/token_usage.json`
