#!/usr/bin/env python3
"""Simulate the metrics display to visualize the output."""

import time
import sys

def format_time(seconds):
    """Format elapsed time."""
    if seconds < 60:
        return f"{int(seconds)}s"
    else:
        mins = int(seconds / 60)
        secs = int(seconds % 60)
        return f"{mins}m {secs}s"

def format_tokens(count):
    """Format token count."""
    if count < 1000:
        return f"{count}"
    else:
        token_k = count / 1000
        return f"{token_k:.1f}k"

print("=" * 80)
print("METRICS DISPLAY SIMULATION")
print("=" * 80)
print()
print("This simulates how the processing indicator will look with metrics:")
print()

emojis = ["🥘", "🍳", "🍲", "🥄", "🔥"]
verbs = ["Brewing", "Thinking", "Processing", "Cooking", "Working"]

# Simulate different time points and token counts
scenarios = [
    (0, 0, "Initial state"),
    (1, 23, "First second"),
    (2, 87, "After 2 seconds"),
    (5, 234, "After 5 seconds"),
    (10, 567, "After 10 seconds"),
    (30, 1234, "After 30 seconds - note 1.2k format"),
    (70, 1876, "After 1 minute 10 seconds"),
    (125, 3456, "After 2 minutes 5 seconds"),
]

for i, (elapsed, tokens, description) in enumerate(scenarios):
    emoji = emojis[i % len(emojis)]
    verb = verbs[i % len(verbs)]

    time_str = format_time(elapsed)
    token_str = format_tokens(tokens)
    thinking_str = time_str

    # Simulate the actual display
    line = f"📝 Response: {emoji} {verb} ({time_str} · ↓ {token_str} tokens · thought for {thinking_str})"

    print(f"{description:45} | {line}")
    time.sleep(0.5)

print()
print("=" * 80)
print("SIMULATION COMPLETE")
print("=" * 80)
print()
print("Notice how:")
print("  - The emoji and verb change (would shimmer in real UI)")
print("  - Time increments naturally")
print("  - Token count grows")
print("  - Format changes from '234' to '1.2k' at 1000 tokens")
print("  - Minutes format appears after 60 seconds")
print()
print("In the actual UI:")
print("  - The emoji/verb would animate with shimmer effect")
print("  - Metrics would be in dim colors (less distracting)")
print("  - Updates would occur every 0.5 seconds")
print()
