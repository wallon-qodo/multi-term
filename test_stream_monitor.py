#!/usr/bin/env python3
"""Quick test of streaming monitor functionality."""

import time
from uuid import uuid4

from claude_multi_terminal.streaming import StreamMonitor, StreamState, get_state_color


def main():
    """Demonstrate stream monitor features."""
    monitor = StreamMonitor()

    print("Stream Monitor Test")
    print("=" * 60)

    # Test 1: Spinner animation
    print("\n1. Spinner Animation (10 frames):")
    for i in range(10):
        frame = monitor.get_spinner_frame()
        print(f"   Frame {i}: {frame}", end=" ")
        time.sleep(0.1)
    print()

    # Test 2: State colors
    print("\n2. State Colors:")
    for state in StreamState:
        color = get_state_color(state)
        print(f"   {state.value:12} -> RGB({color.triplet.red}, {color.triplet.green}, {color.triplet.blue})")

    # Test 3: Thinking -> Streaming -> Complete
    print("\n3. Stream Lifecycle:")
    session_id = monitor.start_stream(thinking=True)
    print(f"   Started stream: {session_id}")

    # Thinking phase
    indicator = monitor.format_stream_indicator(session_id)
    print(f"   Thinking: {indicator}")
    time.sleep(0.5)

    # Streaming phase
    for i in range(5):
        monitor.update_stream(session_id, token_count=10, content=f"chunk_{i}")
        indicator = monitor.format_stream_indicator(session_id)
        print(f"   Streaming: {indicator}")
        time.sleep(0.2)

    # Complete
    monitor.end_stream(session_id, success=True)
    indicator = monitor.format_stream_indicator(session_id)
    print(f"   Complete: {indicator}")

    # Test 4: Multiple concurrent streams
    print("\n4. Concurrent Streams:")
    stream1 = monitor.start_stream()
    stream2 = monitor.start_stream(thinking=True)
    stream3 = monitor.start_stream()

    for i in range(3):
        monitor.update_stream(stream1, token_count=5)
        monitor.update_stream(stream3, token_count=8)
        time.sleep(0.1)

    monitor.update_stream(stream2, token_count=15)  # Transition from thinking

    active = monitor.get_active_streams()
    print(f"   Active streams: {len(active)}")
    for session in active:
        indicator = monitor.format_stream_indicator(session.session_id)
        print(f"   - {indicator}")

    # Test 5: Statistics
    print("\n5. Statistics:")
    stats = monitor.get_stats()
    print(f"   Total tokens: {stats['total_tokens_received']}")
    print(f"   Completed streams: {stats['total_streams_completed']}")
    print(f"   Active streams: {stats['active_streams']}")

    # Cleanup
    monitor.end_stream(stream1)
    monitor.end_stream(stream2)
    monitor.end_stream(stream3)
    cleared = monitor.clear_completed()
    print(f"\n   Cleared {cleared} completed streams")

    print("\n" + "=" * 60)
    print("All tests completed successfully!")


if __name__ == "__main__":
    main()
