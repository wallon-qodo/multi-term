"""Stream monitoring and visual indicators for Claude responses.

This module provides real-time monitoring of streaming responses with
visual feedback indicators following TUIOS design principles.
"""

import time
import threading
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional
from uuid import UUID, uuid4

from rich.color import Color


class StreamState(Enum):
    """States for streaming response lifecycle."""

    IDLE = "idle"
    THINKING = "thinking"  # Model thinking before stream starts
    STREAMING = "streaming"  # Actively receiving tokens
    COMPLETE = "complete"  # Stream finished successfully
    ERROR = "error"  # Stream failed


@dataclass
class StreamingSession:
    """Data for an active streaming session.

    Attributes:
        session_id: Unique identifier for this stream
        state: Current state of the stream
        start_time: When streaming started (Unix timestamp)
        end_time: When streaming ended (None if active)
        tokens_received: Total tokens received so far
        current_speed: Current streaming speed (tokens/sec)
        buffer: Recent output chunks for display
        error_message: Error details if state is ERROR
    """

    session_id: UUID
    state: StreamState = StreamState.IDLE
    start_time: float = field(default_factory=time.time)
    end_time: Optional[float] = None
    tokens_received: int = 0
    current_speed: float = 0.0
    buffer: List[str] = field(default_factory=list)
    error_message: Optional[str] = None

    def duration(self) -> float:
        """Get duration of stream in seconds."""
        end = self.end_time if self.end_time else time.time()
        return end - self.start_time

    def is_active(self) -> bool:
        """Check if stream is currently active."""
        return self.state in (StreamState.THINKING, StreamState.STREAMING)


class StreamMonitor:
    """Monitor and track streaming response sessions.

    Thread-safe monitoring of multiple concurrent streaming sessions
    with real-time metrics and visual indicators.
    """

    # Spinner animation frames (Braille patterns)
    SPINNER_FRAMES = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]

    # Buffer size for recent output
    BUFFER_SIZE = 50

    # Speed calculation window (seconds)
    SPEED_WINDOW = 2.0

    def __init__(self):
        """Initialize stream monitor."""
        self._active_streams: Dict[UUID, StreamingSession] = {}
        self._total_tokens_received: int = 0
        self._total_streams_completed: int = 0
        self._lock = threading.RLock()
        self._spinner_index: int = 0
        self._last_spinner_update: float = time.time()

        # Speed calculation tracking
        self._token_timestamps: Dict[UUID, List[tuple[float, int]]] = {}

    @property
    def active_streams(self) -> Dict[UUID, StreamingSession]:
        """Get all active streaming sessions."""
        with self._lock:
            return self._active_streams.copy()

    @property
    def total_tokens_received(self) -> int:
        """Get total tokens received across all sessions."""
        with self._lock:
            return self._total_tokens_received

    @property
    def total_streams_completed(self) -> int:
        """Get total number of completed streams."""
        with self._lock:
            return self._total_streams_completed

    def start_stream(
        self,
        session_id: Optional[UUID] = None,
        thinking: bool = False
    ) -> UUID:
        """Start a new streaming session.

        Args:
            session_id: Optional UUID to use (generates new if None)
            thinking: If True, start in THINKING state

        Returns:
            Session ID for this stream
        """
        if session_id is None:
            session_id = uuid4()

        with self._lock:
            initial_state = StreamState.THINKING if thinking else StreamState.STREAMING
            session = StreamingSession(
                session_id=session_id,
                state=initial_state,
                start_time=time.time()
            )
            self._active_streams[session_id] = session
            self._token_timestamps[session_id] = []

        return session_id

    def update_stream(
        self,
        session_id: UUID,
        token_count: int = 1,
        content: Optional[str] = None
    ) -> bool:
        """Update stream with new tokens/content.

        Args:
            session_id: ID of stream to update
            token_count: Number of new tokens received
            content: Optional content chunk to add to buffer

        Returns:
            True if update successful, False if session not found
        """
        with self._lock:
            session = self._active_streams.get(session_id)
            if not session:
                return False

            # Transition from THINKING to STREAMING on first token
            if session.state == StreamState.THINKING:
                session.state = StreamState.STREAMING

            # Update token count
            session.tokens_received += token_count
            self._total_tokens_received += token_count

            # Track for speed calculation
            current_time = time.time()
            self._token_timestamps[session_id].append((current_time, token_count))

            # Clean old timestamps outside speed window
            cutoff = current_time - self.SPEED_WINDOW
            self._token_timestamps[session_id] = [
                (t, c) for t, c in self._token_timestamps[session_id]
                if t >= cutoff
            ]

            # Calculate current speed
            session.current_speed = self._calculate_speed(session_id)

            # Add content to buffer
            if content:
                session.buffer.append(content)
                if len(session.buffer) > self.BUFFER_SIZE:
                    session.buffer = session.buffer[-self.BUFFER_SIZE:]

            return True

    def end_stream(
        self,
        session_id: UUID,
        success: bool = True,
        error_message: Optional[str] = None
    ) -> bool:
        """Mark stream as complete or failed.

        Args:
            session_id: ID of stream to end
            success: True if completed successfully
            error_message: Error details if success=False

        Returns:
            True if ended successfully, False if session not found
        """
        with self._lock:
            session = self._active_streams.get(session_id)
            if not session:
                return False

            session.end_time = time.time()
            session.state = StreamState.COMPLETE if success else StreamState.ERROR

            if error_message:
                session.error_message = error_message

            if success:
                self._total_streams_completed += 1

            # Clean up speed tracking
            if session_id in self._token_timestamps:
                del self._token_timestamps[session_id]

            return True

    def get_stream_state(self, session_id: UUID) -> Optional[StreamingSession]:
        """Get current state of a stream.

        Args:
            session_id: ID of stream to query

        Returns:
            StreamingSession object or None if not found
        """
        with self._lock:
            session = self._active_streams.get(session_id)
            return session

    def get_active_streams(self) -> List[StreamingSession]:
        """Get all currently active streams.

        Returns:
            List of active StreamingSession objects
        """
        with self._lock:
            return [
                session for session in self._active_streams.values()
                if session.is_active()
            ]

    def calculate_speed(self, session_id: UUID) -> float:
        """Calculate current streaming speed.

        Args:
            session_id: ID of stream to calculate speed for

        Returns:
            Speed in tokens/second, or 0.0 if unavailable
        """
        with self._lock:
            return self._calculate_speed(session_id)

    def _calculate_speed(self, session_id: UUID) -> float:
        """Internal speed calculation (assumes lock held).

        Args:
            session_id: ID of stream to calculate speed for

        Returns:
            Speed in tokens/second
        """
        timestamps = self._token_timestamps.get(session_id, [])
        if len(timestamps) < 2:
            return 0.0

        # Calculate tokens in window
        current_time = time.time()
        cutoff = current_time - self.SPEED_WINDOW
        recent = [(t, c) for t, c in timestamps if t >= cutoff]

        if not recent:
            return 0.0

        total_tokens = sum(c for _, c in recent)
        time_span = current_time - recent[0][0]

        if time_span < 0.1:  # Avoid division by very small numbers
            return 0.0

        return total_tokens / time_span

    def remove_stream(self, session_id: UUID) -> bool:
        """Remove a stream from active tracking.

        Args:
            session_id: ID of stream to remove

        Returns:
            True if removed, False if not found
        """
        with self._lock:
            if session_id in self._active_streams:
                del self._active_streams[session_id]
                if session_id in self._token_timestamps:
                    del self._token_timestamps[session_id]
                return True
            return False

    def clear_completed(self) -> int:
        """Remove all completed/error streams.

        Returns:
            Number of streams removed
        """
        with self._lock:
            to_remove = [
                sid for sid, session in self._active_streams.items()
                if not session.is_active()
            ]

            for sid in to_remove:
                self.remove_stream(sid)

            return len(to_remove)

    def get_spinner_frame(self) -> str:
        """Get current spinner animation frame.

        Updates spinner index on each call, respecting frame rate.

        Returns:
            Single character spinner frame
        """
        with self._lock:
            current_time = time.time()
            # Update spinner at ~10 FPS
            if current_time - self._last_spinner_update > 0.1:
                self._spinner_index = (self._spinner_index + 1) % len(self.SPINNER_FRAMES)
                self._last_spinner_update = current_time

            return self.SPINNER_FRAMES[self._spinner_index]

    def format_stream_indicator(
        self,
        session_id: UUID,
        include_speed: bool = True
    ) -> Optional[str]:
        """Format visual indicator for a stream.

        Args:
            session_id: ID of stream to format
            include_speed: Whether to include speed information

        Returns:
            Formatted indicator string or None if session not found
        """
        session = self.get_stream_state(session_id)
        if not session:
            return None

        spinner = self.get_spinner_frame()
        tokens = session.tokens_received

        if session.state == StreamState.THINKING:
            return f"{spinner} Thinking..."

        elif session.state == StreamState.STREAMING:
            if include_speed and session.current_speed > 0:
                return f"{spinner} {tokens} tok ({session.current_speed:.0f} tok/s)"
            else:
                return f"{spinner} {tokens} tok"

        elif session.state == StreamState.COMPLETE:
            duration = session.duration()
            avg_speed = tokens / duration if duration > 0 else 0
            return f"✓ {tokens} tok ({avg_speed:.0f} tok/s avg)"

        elif session.state == StreamState.ERROR:
            error_msg = session.error_message or "Stream failed"
            return f"✗ {error_msg}"

        return None

    def get_stats(self) -> Dict[str, any]:
        """Get overall streaming statistics.

        Returns:
            Dictionary with statistics
        """
        with self._lock:
            active = self.get_active_streams()

            return {
                "total_tokens_received": self._total_tokens_received,
                "total_streams_completed": self._total_streams_completed,
                "active_streams": len(active),
                "active_sessions": [str(s.session_id) for s in active],
            }


# Helper functions for external use

def get_spinner_frame(frame_index: int = 0) -> str:
    """Get a specific spinner frame.

    Args:
        frame_index: Index of frame to get (0-9)

    Returns:
        Single character spinner frame
    """
    frames = StreamMonitor.SPINNER_FRAMES
    return frames[frame_index % len(frames)]


def get_state_color(state: StreamState) -> Color:
    """Get Rich Color for a stream state.

    Args:
        state: Stream state to get color for

    Returns:
        Rich Color object following HomebrewTheme palette
    """
    color_map = {
        StreamState.IDLE: Color.from_rgb(150, 150, 150),  # Gray
        StreamState.THINKING: Color.from_rgb(255, 200, 100),  # Yellow
        StreamState.STREAMING: Color.from_rgb(255, 77, 77),  # Coral-red
        StreamState.COMPLETE: Color.from_rgb(100, 255, 100),  # Green
        StreamState.ERROR: Color.from_rgb(255, 50, 50),  # Red
    }
    return color_map.get(state, Color.from_rgb(255, 255, 255))
