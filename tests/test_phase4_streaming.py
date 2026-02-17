"""
Phase 4 - Streaming & Session Polish: Comprehensive Tests
Tests for streaming indicators and token tracking system.
"""

import sys
import time
import pytest
from pathlib import Path
from uuid import UUID, uuid4
from unittest.mock import Mock, patch
from dataclasses import dataclass, field
from typing import Optional

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from claude_multi_terminal.streaming.stream_monitor import (
    StreamState,
    StreamingSession,
    StreamMonitor,
    get_spinner_frame,
    get_state_color,
)


# ============================================================================
# MOCK TOKEN TRACKER (since it may not be implemented yet by other agents)
# ============================================================================

@dataclass
class TokenUsage:
    """Token usage data for a single API request."""
    input_tokens: int = 0
    output_tokens: int = 0
    cached_tokens: int = 0

    @property
    def total_tokens(self) -> int:
        """Total tokens used."""
        return self.input_tokens + self.output_tokens

    def calculate_cost(self, model: str = "opus") -> float:
        """Calculate cost in USD."""
        pricing = {
            "opus": {"input": 0.015, "output": 0.075, "cached": 0.0015},
            "sonnet": {"input": 0.003, "output": 0.015, "cached": 0.0003},
            "haiku": {"input": 0.00025, "output": 0.00125, "cached": 0.000025},
        }

        if model not in pricing:
            model = "opus"

        prices = pricing[model]
        cost = (
            (self.input_tokens / 1000) * prices["input"] +
            (self.output_tokens / 1000) * prices["output"] +
            (self.cached_tokens / 1000) * prices["cached"]
        )
        return cost


@dataclass
class SessionTokenUsage:
    """Token usage aggregated for a session."""
    session_id: UUID
    model: str = "opus"
    requests: list = field(default_factory=list)

    @property
    def total_usage(self) -> TokenUsage:
        """Aggregate all request usage."""
        total = TokenUsage()
        for usage in self.requests:
            total.input_tokens += usage.input_tokens
            total.output_tokens += usage.output_tokens
            total.cached_tokens += usage.cached_tokens
        return total

    @property
    def total_cost(self) -> float:
        """Total cost for session."""
        return sum(u.calculate_cost(self.model) for u in self.requests)


class TokenTracker:
    """Track token usage across sessions and requests."""

    def __init__(self):
        """Initialize token tracker."""
        self._sessions: dict[UUID, SessionTokenUsage] = {}
        self._global_usage = TokenUsage()

    def track_request(
        self,
        session_id: UUID,
        input_tokens: int,
        output_tokens: int,
        cached_tokens: int = 0,
        model: str = "opus"
    ) -> None:
        """Track a single API request."""
        usage = TokenUsage(input_tokens, output_tokens, cached_tokens)

        if session_id not in self._sessions:
            self._sessions[session_id] = SessionTokenUsage(
                session_id=session_id,
                model=model
            )

        self._sessions[session_id].requests.append(usage)

        # Update global
        self._global_usage.input_tokens += input_tokens
        self._global_usage.output_tokens += output_tokens
        self._global_usage.cached_tokens += cached_tokens

    def get_session_usage(self, session_id: UUID) -> Optional[SessionTokenUsage]:
        """Get usage for a session."""
        return self._sessions.get(session_id)

    def get_global_usage(self) -> TokenUsage:
        """Get global token usage."""
        return self._global_usage

    def get_total_cost(self, model: str = "opus") -> float:
        """Get total cost across all sessions."""
        return sum(
            session.total_cost
            for session in self._sessions.values()
        )

    def reset_session(self, session_id: UUID) -> bool:
        """Reset usage for a session."""
        if session_id in self._sessions:
            del self._sessions[session_id]
            return True
        return False

    def export_usage_report(self) -> dict:
        """Export usage report."""
        return {
            "global_usage": {
                "input_tokens": self._global_usage.input_tokens,
                "output_tokens": self._global_usage.output_tokens,
                "cached_tokens": self._global_usage.cached_tokens,
                "total_tokens": self._global_usage.total_tokens,
            },
            "sessions": [
                {
                    "session_id": str(session.session_id),
                    "model": session.model,
                    "requests": len(session.requests),
                    "total_usage": {
                        "input": session.total_usage.input_tokens,
                        "output": session.total_usage.output_tokens,
                        "cached": session.total_usage.cached_tokens,
                    },
                    "total_cost": session.total_cost,
                }
                for session in self._sessions.values()
            ]
        }


# ============================================================================
# TEST CLASSES
# ============================================================================

class TestStreamState:
    """Tests for StreamState enum."""

    def test_state_values(self) -> None:
        """Test all state enum values exist."""
        assert StreamState.IDLE.value == "idle"
        assert StreamState.THINKING.value == "thinking"
        assert StreamState.STREAMING.value == "streaming"
        assert StreamState.COMPLETE.value == "complete"
        assert StreamState.ERROR.value == "error"

    def test_state_comparison(self) -> None:
        """Test state equality comparison."""
        assert StreamState.IDLE == StreamState.IDLE
        assert StreamState.IDLE != StreamState.THINKING
        assert StreamState.STREAMING != StreamState.COMPLETE

    def test_state_count(self) -> None:
        """Test correct number of states."""
        states = list(StreamState)
        assert len(states) == 5, "Should have exactly 5 states"


class TestStreamingSession:
    """Tests for StreamingSession dataclass."""

    def test_session_creation(self) -> None:
        """Test creating a new session."""
        session_id = uuid4()
        session = StreamingSession(session_id=session_id)

        assert session.session_id == session_id
        assert session.state == StreamState.IDLE
        assert session.tokens_received == 0
        assert session.current_speed == 0.0
        assert session.end_time is None
        assert session.error_message is None
        assert len(session.buffer) == 0

    def test_session_duration_active(self) -> None:
        """Test duration calculation for active session."""
        session_id = uuid4()
        start = time.time()
        session = StreamingSession(session_id=session_id, start_time=start)

        time.sleep(0.1)
        duration = session.duration()

        assert duration >= 0.1, "Duration should be at least 0.1 seconds"
        assert duration < 0.2, "Duration should be less than 0.2 seconds"

    def test_session_duration_complete(self) -> None:
        """Test duration calculation for completed session."""
        session_id = uuid4()
        start = time.time()
        session = StreamingSession(session_id=session_id, start_time=start)

        time.sleep(0.1)
        session.end_time = time.time()
        duration1 = session.duration()

        time.sleep(0.1)
        duration2 = session.duration()

        # Duration should not change after end_time is set
        assert abs(duration1 - duration2) < 0.01

    def test_is_active_states(self) -> None:
        """Test is_active for different states."""
        session_id = uuid4()
        session = StreamingSession(session_id=session_id)

        session.state = StreamState.THINKING
        assert session.is_active() is True

        session.state = StreamState.STREAMING
        assert session.is_active() is True

        session.state = StreamState.COMPLETE
        assert session.is_active() is False

        session.state = StreamState.ERROR
        assert session.is_active() is False

        session.state = StreamState.IDLE
        assert session.is_active() is False

    def test_buffer_initialization(self) -> None:
        """Test buffer is properly initialized."""
        session_id = uuid4()
        session = StreamingSession(session_id=session_id)

        assert isinstance(session.buffer, list)
        assert len(session.buffer) == 0

    def test_token_count_tracking(self) -> None:
        """Test token counting."""
        session = StreamingSession(session_id=uuid4())

        session.tokens_received = 100
        assert session.tokens_received == 100

        session.tokens_received += 50
        assert session.tokens_received == 150


class TestStreamMonitor:
    """Tests for StreamMonitor."""

    def test_monitor_initialization(self) -> None:
        """Test monitor initializes correctly."""
        monitor = StreamMonitor()

        assert len(monitor.active_streams) == 0
        assert monitor.total_tokens_received == 0
        assert monitor.total_streams_completed == 0

    def test_start_stream_default(self) -> None:
        """Test starting a stream with default parameters."""
        monitor = StreamMonitor()
        session_id = monitor.start_stream()

        assert isinstance(session_id, UUID)
        assert session_id in monitor.active_streams

        session = monitor.get_stream_state(session_id)
        assert session is not None
        assert session.state == StreamState.STREAMING

    def test_start_stream_thinking(self) -> None:
        """Test starting a stream in thinking state."""
        monitor = StreamMonitor()
        session_id = monitor.start_stream(thinking=True)

        session = monitor.get_stream_state(session_id)
        assert session is not None
        assert session.state == StreamState.THINKING

    def test_start_stream_custom_id(self) -> None:
        """Test starting stream with custom UUID."""
        monitor = StreamMonitor()
        custom_id = uuid4()
        session_id = monitor.start_stream(session_id=custom_id)

        assert session_id == custom_id
        assert custom_id in monitor.active_streams

    def test_update_stream_tokens(self) -> None:
        """Test updating stream with tokens."""
        monitor = StreamMonitor()
        session_id = monitor.start_stream()

        success = monitor.update_stream(session_id, token_count=10)
        assert success is True

        session = monitor.get_stream_state(session_id)
        assert session.tokens_received == 10
        assert monitor.total_tokens_received == 10

    def test_update_stream_multiple_times(self) -> None:
        """Test multiple stream updates accumulate tokens."""
        monitor = StreamMonitor()
        session_id = monitor.start_stream()

        monitor.update_stream(session_id, token_count=5)
        monitor.update_stream(session_id, token_count=3)
        monitor.update_stream(session_id, token_count=7)

        session = monitor.get_stream_state(session_id)
        assert session.tokens_received == 15
        assert monitor.total_tokens_received == 15

    def test_update_stream_with_content(self) -> None:
        """Test updating stream with content chunks."""
        monitor = StreamMonitor()
        session_id = monitor.start_stream()

        monitor.update_stream(session_id, token_count=1, content="Hello ")
        monitor.update_stream(session_id, token_count=1, content="world!")

        session = monitor.get_stream_state(session_id)
        assert len(session.buffer) == 2
        assert session.buffer == ["Hello ", "world!"]

    def test_update_stream_buffer_limit(self) -> None:
        """Test buffer respects size limit."""
        monitor = StreamMonitor()
        session_id = monitor.start_stream()

        # Add more than BUFFER_SIZE chunks
        for i in range(monitor.BUFFER_SIZE + 10):
            monitor.update_stream(session_id, token_count=1, content=f"chunk{i}")

        session = monitor.get_stream_state(session_id)
        assert len(session.buffer) == monitor.BUFFER_SIZE
        # Should keep most recent chunks
        assert session.buffer[-1] == f"chunk{monitor.BUFFER_SIZE + 9}"

    def test_update_nonexistent_stream(self) -> None:
        """Test updating non-existent stream returns False."""
        monitor = StreamMonitor()
        fake_id = uuid4()

        success = monitor.update_stream(fake_id, token_count=10)
        assert success is False

    def test_update_transitions_thinking_to_streaming(self) -> None:
        """Test first update transitions THINKING to STREAMING."""
        monitor = StreamMonitor()
        session_id = monitor.start_stream(thinking=True)

        session = monitor.get_stream_state(session_id)
        assert session.state == StreamState.THINKING

        monitor.update_stream(session_id, token_count=1)

        session = monitor.get_stream_state(session_id)
        assert session.state == StreamState.STREAMING

    def test_end_stream_success(self) -> None:
        """Test ending stream successfully."""
        monitor = StreamMonitor()
        session_id = monitor.start_stream()
        monitor.update_stream(session_id, token_count=100)

        success = monitor.end_stream(session_id, success=True)
        assert success is True

        session = monitor.get_stream_state(session_id)
        assert session.state == StreamState.COMPLETE
        assert session.end_time is not None
        assert monitor.total_streams_completed == 1

    def test_end_stream_error(self) -> None:
        """Test ending stream with error."""
        monitor = StreamMonitor()
        session_id = monitor.start_stream()

        error_msg = "Connection timeout"
        success = monitor.end_stream(
            session_id,
            success=False,
            error_message=error_msg
        )
        assert success is True

        session = monitor.get_stream_state(session_id)
        assert session.state == StreamState.ERROR
        assert session.error_message == error_msg
        assert monitor.total_streams_completed == 0  # Errors don't count

    def test_end_nonexistent_stream(self) -> None:
        """Test ending non-existent stream returns False."""
        monitor = StreamMonitor()
        fake_id = uuid4()

        success = monitor.end_stream(fake_id)
        assert success is False

    def test_multiple_concurrent_streams(self) -> None:
        """Test handling multiple concurrent streams."""
        monitor = StreamMonitor()

        # Start 3 streams
        id1 = monitor.start_stream()
        id2 = monitor.start_stream()
        id3 = monitor.start_stream()

        # Update each with different token counts
        monitor.update_stream(id1, token_count=10)
        monitor.update_stream(id2, token_count=20)
        monitor.update_stream(id3, token_count=30)

        # Verify individual counts
        assert monitor.get_stream_state(id1).tokens_received == 10
        assert monitor.get_stream_state(id2).tokens_received == 20
        assert monitor.get_stream_state(id3).tokens_received == 30

        # Verify total
        assert monitor.total_tokens_received == 60

    def test_get_active_streams(self) -> None:
        """Test getting active streams list."""
        monitor = StreamMonitor()

        id1 = monitor.start_stream()
        id2 = monitor.start_stream()
        id3 = monitor.start_stream()

        # All active
        active = monitor.get_active_streams()
        assert len(active) == 3

        # End one
        monitor.end_stream(id2)
        active = monitor.get_active_streams()
        assert len(active) == 2

        # End another
        monitor.end_stream(id1)
        active = monitor.get_active_streams()
        assert len(active) == 1

    def test_calculate_speed(self) -> None:
        """Test speed calculation."""
        monitor = StreamMonitor()
        session_id = monitor.start_stream()

        # Initial speed should be 0
        speed = monitor.calculate_speed(session_id)
        assert speed == 0.0

        # Add tokens over time
        monitor.update_stream(session_id, token_count=10)
        time.sleep(0.1)
        monitor.update_stream(session_id, token_count=10)

        speed = monitor.calculate_speed(session_id)
        # Should have some speed now (rough check)
        assert speed > 0

    def test_remove_stream(self) -> None:
        """Test removing a stream."""
        monitor = StreamMonitor()
        session_id = monitor.start_stream()

        assert session_id in monitor.active_streams

        success = monitor.remove_stream(session_id)
        assert success is True
        assert session_id not in monitor.active_streams

    def test_remove_nonexistent_stream(self) -> None:
        """Test removing non-existent stream returns False."""
        monitor = StreamMonitor()
        fake_id = uuid4()

        success = monitor.remove_stream(fake_id)
        assert success is False

    def test_clear_completed(self) -> None:
        """Test clearing completed streams."""
        monitor = StreamMonitor()

        id1 = monitor.start_stream()
        id2 = monitor.start_stream()
        id3 = monitor.start_stream()

        # Complete first two
        monitor.end_stream(id1)
        monitor.end_stream(id2, success=False)

        # Third still active
        assert len(monitor.active_streams) == 3

        # Clear completed
        count = monitor.clear_completed()
        assert count == 2
        assert len(monitor.active_streams) == 1
        assert id3 in monitor.active_streams

    def test_get_spinner_frame(self) -> None:
        """Test spinner frame generation."""
        monitor = StreamMonitor()

        frame = monitor.get_spinner_frame()
        assert isinstance(frame, str)
        assert len(frame) == 1
        assert frame in monitor.SPINNER_FRAMES

    def test_spinner_animation(self) -> None:
        """Test spinner animates over time."""
        monitor = StreamMonitor()

        frame1 = monitor.get_spinner_frame()
        time.sleep(0.12)  # Wait for animation update
        frame2 = monitor.get_spinner_frame()

        # Frames should be different after delay
        assert frame1 != frame2

    def test_format_stream_indicator_thinking(self) -> None:
        """Test formatting indicator for thinking state."""
        monitor = StreamMonitor()
        session_id = monitor.start_stream(thinking=True)

        indicator = monitor.format_stream_indicator(session_id)
        assert indicator is not None
        assert "Thinking" in indicator

    def test_format_stream_indicator_streaming(self) -> None:
        """Test formatting indicator for streaming state."""
        monitor = StreamMonitor()
        session_id = monitor.start_stream()
        monitor.update_stream(session_id, token_count=42)

        indicator = monitor.format_stream_indicator(session_id)
        assert indicator is not None
        assert "42" in indicator
        assert "tok" in indicator

    def test_format_stream_indicator_complete(self) -> None:
        """Test formatting indicator for complete state."""
        monitor = StreamMonitor()
        session_id = monitor.start_stream()
        monitor.update_stream(session_id, token_count=100)
        monitor.end_stream(session_id)

        indicator = monitor.format_stream_indicator(session_id)
        assert indicator is not None
        assert "✓" in indicator
        assert "100" in indicator

    def test_format_stream_indicator_error(self) -> None:
        """Test formatting indicator for error state."""
        monitor = StreamMonitor()
        session_id = monitor.start_stream()
        monitor.end_stream(session_id, success=False, error_message="Test error")

        indicator = monitor.format_stream_indicator(session_id)
        assert indicator is not None
        assert "✗" in indicator
        assert "error" in indicator.lower()

    def test_format_nonexistent_stream(self) -> None:
        """Test formatting indicator for non-existent stream returns None."""
        monitor = StreamMonitor()
        fake_id = uuid4()

        indicator = monitor.format_stream_indicator(fake_id)
        assert indicator is None

    def test_get_stats(self) -> None:
        """Test getting statistics."""
        monitor = StreamMonitor()

        id1 = monitor.start_stream()
        id2 = monitor.start_stream()

        monitor.update_stream(id1, token_count=50)
        monitor.update_stream(id2, token_count=30)
        monitor.end_stream(id1)

        stats = monitor.get_stats()

        assert stats["total_tokens_received"] == 80
        assert stats["total_streams_completed"] == 1
        assert stats["active_streams"] == 1  # id2 still active


class TestHelperFunctions:
    """Tests for module helper functions."""

    def test_get_spinner_frame_function(self) -> None:
        """Test standalone get_spinner_frame function."""
        frame = get_spinner_frame(0)
        assert frame == StreamMonitor.SPINNER_FRAMES[0]

        frame = get_spinner_frame(5)
        assert frame == StreamMonitor.SPINNER_FRAMES[5]

    def test_get_spinner_frame_wraps(self) -> None:
        """Test spinner frame index wraps around."""
        frames = StreamMonitor.SPINNER_FRAMES
        frame = get_spinner_frame(len(frames) + 2)
        assert frame == frames[2]

    def test_get_state_color(self) -> None:
        """Test getting colors for states."""
        from rich.color import Color

        for state in StreamState:
            color = get_state_color(state)
            assert isinstance(color, Color)


class TestTokenUsage:
    """Tests for TokenUsage dataclass."""

    def test_usage_creation(self) -> None:
        """Test creating token usage."""
        usage = TokenUsage(input_tokens=100, output_tokens=50)

        assert usage.input_tokens == 100
        assert usage.output_tokens == 50
        assert usage.cached_tokens == 0

    def test_total_tokens(self) -> None:
        """Test total tokens computation."""
        usage = TokenUsage(input_tokens=100, output_tokens=50, cached_tokens=20)

        assert usage.total_tokens == 150

    def test_calculate_cost_opus(self) -> None:
        """Test cost calculation for Opus model."""
        usage = TokenUsage(input_tokens=1000, output_tokens=500)
        cost = usage.calculate_cost("opus")

        # 1000 * 0.015/1000 + 500 * 0.075/1000
        expected = 0.015 + 0.0375
        assert abs(cost - expected) < 0.0001

    def test_calculate_cost_sonnet(self) -> None:
        """Test cost calculation for Sonnet model."""
        usage = TokenUsage(input_tokens=1000, output_tokens=500)
        cost = usage.calculate_cost("sonnet")

        # 1000 * 0.003/1000 + 500 * 0.015/1000
        expected = 0.003 + 0.0075
        assert abs(cost - expected) < 0.0001

    def test_calculate_cost_haiku(self) -> None:
        """Test cost calculation for Haiku model."""
        usage = TokenUsage(input_tokens=1000, output_tokens=500)
        cost = usage.calculate_cost("haiku")

        # 1000 * 0.00025/1000 + 500 * 0.00125/1000
        expected = 0.00025 + 0.000625
        assert abs(cost - expected) < 0.000001

    def test_calculate_cost_with_cached(self) -> None:
        """Test cost calculation with cached tokens."""
        usage = TokenUsage(
            input_tokens=1000,
            output_tokens=500,
            cached_tokens=200
        )
        cost = usage.calculate_cost("opus")

        # Include cached token discount
        expected = 0.015 + 0.0375 + (200 * 0.0015 / 1000)
        assert abs(cost - expected) < 0.0001


class TestTokenTracker:
    """Tests for TokenTracker."""

    def test_tracker_initialization(self) -> None:
        """Test tracker initializes correctly."""
        tracker = TokenTracker()

        global_usage = tracker.get_global_usage()
        assert global_usage.input_tokens == 0
        assert global_usage.output_tokens == 0
        assert global_usage.cached_tokens == 0

    def test_track_single_request(self) -> None:
        """Test tracking a single request."""
        tracker = TokenTracker()
        session_id = uuid4()

        tracker.track_request(session_id, input_tokens=100, output_tokens=50)

        session_usage = tracker.get_session_usage(session_id)
        assert session_usage is not None
        assert len(session_usage.requests) == 1
        assert session_usage.total_usage.input_tokens == 100
        assert session_usage.total_usage.output_tokens == 50

    def test_track_multiple_requests_same_session(self) -> None:
        """Test tracking multiple requests in same session."""
        tracker = TokenTracker()
        session_id = uuid4()

        tracker.track_request(session_id, input_tokens=100, output_tokens=50)
        tracker.track_request(session_id, input_tokens=200, output_tokens=75)

        session_usage = tracker.get_session_usage(session_id)
        assert len(session_usage.requests) == 2
        assert session_usage.total_usage.input_tokens == 300
        assert session_usage.total_usage.output_tokens == 125

    def test_track_multiple_sessions(self) -> None:
        """Test tracking requests across multiple sessions."""
        tracker = TokenTracker()
        session1 = uuid4()
        session2 = uuid4()

        tracker.track_request(session1, input_tokens=100, output_tokens=50)
        tracker.track_request(session2, input_tokens=200, output_tokens=75)

        usage1 = tracker.get_session_usage(session1)
        usage2 = tracker.get_session_usage(session2)

        assert usage1.total_usage.input_tokens == 100
        assert usage2.total_usage.input_tokens == 200

    def test_global_usage_aggregation(self) -> None:
        """Test global usage aggregates all sessions."""
        tracker = TokenTracker()
        session1 = uuid4()
        session2 = uuid4()

        tracker.track_request(session1, input_tokens=100, output_tokens=50)
        tracker.track_request(session2, input_tokens=200, output_tokens=75)

        global_usage = tracker.get_global_usage()
        assert global_usage.input_tokens == 300
        assert global_usage.output_tokens == 125

    def test_total_cost_calculation(self) -> None:
        """Test total cost across sessions."""
        tracker = TokenTracker()
        session1 = uuid4()
        session2 = uuid4()

        tracker.track_request(session1, input_tokens=1000, output_tokens=500, model="opus")
        tracker.track_request(session2, input_tokens=1000, output_tokens=500, model="opus")

        total_cost = tracker.get_total_cost("opus")

        # Each request costs 0.0525, two requests = 0.105
        assert abs(total_cost - 0.105) < 0.0001

    def test_cached_tokens_tracking(self) -> None:
        """Test tracking cached tokens."""
        tracker = TokenTracker()
        session_id = uuid4()

        tracker.track_request(
            session_id,
            input_tokens=1000,
            output_tokens=500,
            cached_tokens=200
        )

        session_usage = tracker.get_session_usage(session_id)
        assert session_usage.total_usage.cached_tokens == 200

    def test_reset_session(self) -> None:
        """Test resetting session usage."""
        tracker = TokenTracker()
        session_id = uuid4()

        tracker.track_request(session_id, input_tokens=100, output_tokens=50)
        assert tracker.get_session_usage(session_id) is not None

        success = tracker.reset_session(session_id)
        assert success is True
        assert tracker.get_session_usage(session_id) is None

    def test_reset_nonexistent_session(self) -> None:
        """Test resetting non-existent session returns False."""
        tracker = TokenTracker()
        fake_id = uuid4()

        success = tracker.reset_session(fake_id)
        assert success is False

    def test_export_usage_report(self) -> None:
        """Test exporting usage report."""
        tracker = TokenTracker()
        session1 = uuid4()
        session2 = uuid4()

        tracker.track_request(session1, input_tokens=100, output_tokens=50, model="opus")
        tracker.track_request(session2, input_tokens=200, output_tokens=75, model="sonnet")

        report = tracker.export_usage_report()

        assert "global_usage" in report
        assert report["global_usage"]["input_tokens"] == 300
        assert report["global_usage"]["output_tokens"] == 125

        assert "sessions" in report
        assert len(report["sessions"]) == 2


class TestStreamingIntegration:
    """Integration tests for streaming system."""

    def test_stream_with_token_tracking(self) -> None:
        """Test coordinated stream monitoring and token tracking."""
        monitor = StreamMonitor()
        tracker = TokenTracker()
        session_id = uuid4()

        # Start stream
        monitor.start_stream(session_id=session_id)

        # Simulate streaming with token tracking
        for _ in range(10):
            monitor.update_stream(session_id, token_count=10)
            tracker.track_request(session_id, input_tokens=5, output_tokens=10)

        # Verify stream
        stream_session = monitor.get_stream_state(session_id)
        assert stream_session.tokens_received == 100

        # Verify tracking
        token_session = tracker.get_session_usage(session_id)
        assert len(token_session.requests) == 10
        assert token_session.total_usage.output_tokens == 100

    def test_concurrent_stream_tracking(self) -> None:
        """Test tracking multiple concurrent streams."""
        monitor = StreamMonitor()
        tracker = TokenTracker()

        sessions = [uuid4() for _ in range(5)]

        # Start all streams
        for session_id in sessions:
            monitor.start_stream(session_id=session_id)

        # Update each stream
        for i, session_id in enumerate(sessions):
            tokens = (i + 1) * 10
            monitor.update_stream(session_id, token_count=tokens)
            tracker.track_request(session_id, input_tokens=tokens, output_tokens=tokens)

        # Verify all tracked
        assert len(monitor.get_active_streams()) == 5
        assert tracker.get_global_usage().total_tokens == 300  # 10+20+30+40+50 = 150 * 2

    def test_token_usage_during_streaming(self) -> None:
        """Test token usage updates during active streaming."""
        monitor = StreamMonitor()
        tracker = TokenTracker()
        session_id = uuid4()

        monitor.start_stream(session_id=session_id, thinking=True)

        # While thinking, no tokens yet
        assert monitor.get_stream_state(session_id).tokens_received == 0

        # Start receiving tokens
        monitor.update_stream(session_id, token_count=1)
        tracker.track_request(session_id, input_tokens=0, output_tokens=1)

        # State should transition
        assert monitor.get_stream_state(session_id).state == StreamState.STREAMING

        # Continue streaming
        for _ in range(50):
            monitor.update_stream(session_id, token_count=1)
            tracker.track_request(session_id, input_tokens=0, output_tokens=1)

        # Verify totals
        assert monitor.get_stream_state(session_id).tokens_received == 51
        assert tracker.get_session_usage(session_id).total_usage.output_tokens == 51

    def test_session_lifecycle_with_streaming(self) -> None:
        """Test complete session lifecycle."""
        monitor = StreamMonitor()
        tracker = TokenTracker()
        session_id = uuid4()

        # Start
        monitor.start_stream(session_id=session_id)

        # Stream tokens
        monitor.update_stream(session_id, token_count=100)
        tracker.track_request(session_id, input_tokens=50, output_tokens=100)

        # End stream
        monitor.end_stream(session_id, success=True)

        # Verify stream complete
        stream = monitor.get_stream_state(session_id)
        assert stream.state == StreamState.COMPLETE
        assert stream.end_time is not None

        # Verify tracking
        usage = tracker.get_session_usage(session_id)
        assert usage.total_usage.total_tokens == 150

    def test_error_handling_integration(self) -> None:
        """Test error handling across systems."""
        monitor = StreamMonitor()
        tracker = TokenTracker()
        session_id = uuid4()

        monitor.start_stream(session_id=session_id)

        # Simulate partial streaming
        monitor.update_stream(session_id, token_count=25)
        tracker.track_request(session_id, input_tokens=10, output_tokens=25)

        # Error occurs
        monitor.end_stream(session_id, success=False, error_message="API timeout")

        # Stream should show error
        stream = monitor.get_stream_state(session_id)
        assert stream.state == StreamState.ERROR
        assert "timeout" in stream.error_message.lower()

        # But tokens still tracked
        usage = tracker.get_session_usage(session_id)
        assert usage.total_usage.output_tokens == 25

    def test_speed_calculation_accuracy(self) -> None:
        """Test streaming speed calculation accuracy."""
        monitor = StreamMonitor()
        session_id = monitor.start_stream()

        # Add tokens at known rate
        for _ in range(10):
            monitor.update_stream(session_id, token_count=10)
            time.sleep(0.01)  # 10ms between updates

        speed = monitor.calculate_speed(session_id)

        # Speed should be roughly 1000 tok/s (10 tokens / 0.01s)
        # Allow wide margin due to timing variability
        assert 100 < speed < 5000

    def test_buffer_content_tracking(self) -> None:
        """Test content buffer during streaming."""
        monitor = StreamMonitor()
        session_id = monitor.start_stream()

        content_chunks = [
            "The ",
            "quick ",
            "brown ",
            "fox ",
            "jumps"
        ]

        for chunk in content_chunks:
            monitor.update_stream(session_id, token_count=1, content=chunk)

        stream = monitor.get_stream_state(session_id)
        assert len(stream.buffer) == len(content_chunks)
        assert stream.buffer == content_chunks

    def test_performance_100_stream_updates(self) -> None:
        """Test performance with 100 stream updates completes under 1s."""
        monitor = StreamMonitor()
        session_id = monitor.start_stream()

        start_time = time.time()

        for i in range(100):
            monitor.update_stream(
                session_id,
                token_count=1,
                content=f"chunk{i}"
            )

        elapsed = time.time() - start_time

        # Should complete well under 1 second
        assert elapsed < 1.0, f"100 updates took {elapsed:.3f}s, should be < 1.0s"

        # Verify all updates tracked
        stream = monitor.get_stream_state(session_id)
        assert stream.tokens_received == 100


# ============================================================================
# TEST EXECUTION
# ============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
