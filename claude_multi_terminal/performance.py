"""
Performance monitoring and optimization utilities.

Tracks FPS, startup time, memory usage, and provides profiling tools.
"""

import time
import psutil
import os
from typing import Dict, List, Optional, Callable
from dataclasses import dataclass, field
from collections import deque
from contextlib import contextmanager


@dataclass
class PerformanceMetrics:
    """Performance metrics snapshot."""

    timestamp: float
    fps: float
    memory_mb: float
    cpu_percent: float
    active_widgets: int
    rendered_items: int


@dataclass
class PerformanceProfile:
    """Performance profile for an operation."""

    operation: str
    duration_ms: float
    memory_delta_mb: float
    timestamp: float


class PerformanceMonitor:
    """
    Performance monitoring system.

    Tracks FPS, memory, CPU, and operation timings.
    """

    # Target performance goals
    TARGET_FPS = 60
    TARGET_FRAME_TIME_MS = 16.67  # 1000/60
    TARGET_STARTUP_MS = 500
    TARGET_MEMORY_MB = 100  # For 10K messages

    def __init__(self, history_size: int = 100):
        """
        Initialize performance monitor.

        Args:
            history_size: Number of historical metrics to keep
        """
        self.history_size = history_size
        self._metrics_history: deque[PerformanceMetrics] = deque(maxlen=history_size)
        self._profiles: List[PerformanceProfile] = []

        # FPS tracking
        self._frame_times: deque[float] = deque(maxlen=60)
        self._last_frame_time = time.time()

        # Process for memory tracking
        self._process = psutil.Process(os.getpid())

        # Startup tracking
        self._startup_time: Optional[float] = None
        self._startup_complete = False

    def record_frame(self) -> None:
        """Record a frame for FPS calculation."""
        current_time = time.time()
        frame_time = current_time - self._last_frame_time
        self._frame_times.append(frame_time)
        self._last_frame_time = current_time

    def get_fps(self) -> float:
        """
        Get current FPS.

        Returns:
            float: Frames per second
        """
        if not self._frame_times:
            return 0.0

        avg_frame_time = sum(self._frame_times) / len(self._frame_times)
        return 1.0 / avg_frame_time if avg_frame_time > 0 else 0.0

    def get_frame_time_ms(self) -> float:
        """
        Get average frame time in milliseconds.

        Returns:
            float: Frame time in ms
        """
        if not self._frame_times:
            return 0.0

        return (sum(self._frame_times) / len(self._frame_times)) * 1000

    def get_memory_mb(self) -> float:
        """
        Get current memory usage in MB.

        Returns:
            float: Memory usage in megabytes
        """
        return self._process.memory_info().rss / (1024 * 1024)

    def get_cpu_percent(self) -> float:
        """
        Get current CPU usage percentage.

        Returns:
            float: CPU percentage
        """
        return self._process.cpu_percent()

    def record_metrics(
        self,
        active_widgets: int = 0,
        rendered_items: int = 0
    ) -> PerformanceMetrics:
        """
        Record current performance metrics.

        Args:
            active_widgets: Number of active widgets
            rendered_items: Number of rendered items

        Returns:
            PerformanceMetrics: Recorded metrics
        """
        metrics = PerformanceMetrics(
            timestamp=time.time(),
            fps=self.get_fps(),
            memory_mb=self.get_memory_mb(),
            cpu_percent=self.get_cpu_percent(),
            active_widgets=active_widgets,
            rendered_items=rendered_items,
        )

        self._metrics_history.append(metrics)
        return metrics

    @contextmanager
    def profile_operation(self, operation: str):
        """
        Profile an operation.

        Args:
            operation: Operation name

        Yields:
            None

        Example:
            with monitor.profile_operation("load_session"):
                load_session_data()
        """
        start_time = time.time()
        start_memory = self.get_memory_mb()

        try:
            yield
        finally:
            end_time = time.time()
            end_memory = self.get_memory_mb()

            duration_ms = (end_time - start_time) * 1000
            memory_delta = end_memory - start_memory

            profile = PerformanceProfile(
                operation=operation,
                duration_ms=duration_ms,
                memory_delta_mb=memory_delta,
                timestamp=end_time,
            )

            self._profiles.append(profile)

            # Log slow operations
            if duration_ms > 100:  # Slower than 100ms
                print(f"⚠ Slow operation: {operation} took {duration_ms:.2f}ms")

    def mark_startup_complete(self) -> None:
        """Mark application startup as complete."""
        if not self._startup_complete:
            self._startup_time = time.time()
            self._startup_complete = True

    def get_startup_time_ms(self) -> Optional[float]:
        """
        Get startup time in milliseconds.

        Returns:
            Optional[float]: Startup time or None if not completed
        """
        if self._startup_time:
            # Calculate from process start to startup_complete
            return (self._startup_time - psutil.Process().create_time()) * 1000
        return None

    def get_metrics_summary(self) -> Dict:
        """
        Get performance metrics summary.

        Returns:
            Dict: Summary of metrics
        """
        if not self._metrics_history:
            return {
                "fps": 0.0,
                "frame_time_ms": 0.0,
                "memory_mb": 0.0,
                "cpu_percent": 0.0,
            }

        recent_metrics = list(self._metrics_history)[-10:]  # Last 10 samples

        return {
            "fps": {
                "current": self.get_fps(),
                "avg": sum(m.fps for m in recent_metrics) / len(recent_metrics),
                "target": self.TARGET_FPS,
                "meeting_target": self.get_fps() >= self.TARGET_FPS * 0.9,  # 90% of target
            },
            "frame_time_ms": {
                "current": self.get_frame_time_ms(),
                "target": self.TARGET_FRAME_TIME_MS,
                "meeting_target": self.get_frame_time_ms() <= self.TARGET_FRAME_TIME_MS * 1.1,
            },
            "memory_mb": {
                "current": self.get_memory_mb(),
                "target": self.TARGET_MEMORY_MB,
                "meeting_target": self.get_memory_mb() <= self.TARGET_MEMORY_MB,
            },
            "cpu_percent": {
                "current": self.get_cpu_percent(),
                "avg": sum(m.cpu_percent for m in recent_metrics) / len(recent_metrics),
            },
            "startup_ms": self.get_startup_time_ms(),
        }

    def get_slow_operations(self, threshold_ms: float = 50) -> List[PerformanceProfile]:
        """
        Get operations slower than threshold.

        Args:
            threshold_ms: Threshold in milliseconds

        Returns:
            List[PerformanceProfile]: Slow operations
        """
        return [p for p in self._profiles if p.duration_ms > threshold_ms]

    def print_performance_report(self) -> None:
        """Print a detailed performance report."""
        summary = self.get_metrics_summary()

        print("\n" + "=" * 60)
        print("PERFORMANCE REPORT")
        print("=" * 60)

        # FPS
        fps_data = summary["fps"]
        fps_status = "✓" if fps_data["meeting_target"] else "✗"
        print(f"\n{fps_status} FPS: {fps_data['current']:.1f} (target: {fps_data['target']})")
        print(f"  Average: {fps_data['avg']:.1f}")

        # Frame time
        frame_data = summary["frame_time_ms"]
        frame_status = "✓" if frame_data["meeting_target"] else "✗"
        print(f"\n{frame_status} Frame Time: {frame_data['current']:.2f}ms (target: <{frame_data['target']:.2f}ms)")

        # Memory
        mem_data = summary["memory_mb"]
        mem_status = "✓" if mem_data["meeting_target"] else "✗"
        print(f"\n{mem_status} Memory: {mem_data['current']:.1f}MB (target: <{mem_data['target']}MB)")

        # CPU
        cpu_data = summary["cpu_percent"]
        print(f"\n  CPU: {cpu_data['current']:.1f}% (avg: {cpu_data['avg']:.1f}%)")

        # Startup
        if summary["startup_ms"]:
            startup_status = "✓" if summary["startup_ms"] < self.TARGET_STARTUP_MS else "✗"
            print(f"\n{startup_status} Startup: {summary['startup_ms']:.1f}ms (target: <{self.TARGET_STARTUP_MS}ms)")

        # Slow operations
        slow_ops = self.get_slow_operations()
        if slow_ops:
            print(f"\n⚠ Slow Operations ({len(slow_ops)} found):")
            for op in slow_ops[-5:]:  # Show last 5
                print(f"  • {op.operation}: {op.duration_ms:.2f}ms")

        print("\n" + "=" * 60 + "\n")


class PerformanceOptimizer:
    """
    Performance optimization utilities.

    Provides tools for async operations, caching, and optimization.
    """

    @staticmethod
    def create_cache(max_size: int = 100) -> Dict:
        """
        Create a simple LRU cache.

        Args:
            max_size: Maximum cache size

        Returns:
            Dict: Cache dict with cleanup
        """
        from collections import OrderedDict

        cache = OrderedDict()

        def get(key, default=None):
            if key in cache:
                # Move to end (most recently used)
                cache.move_to_end(key)
                return cache[key]
            return default

        def set(key, value):
            if key in cache:
                cache.move_to_end(key)
            cache[key] = value

            # Evict oldest if over size
            if len(cache) > max_size:
                cache.popitem(last=False)

        cache.get = get
        cache.set = set
        return cache

    @staticmethod
    async def batch_async(
        items: List,
        process_fn: Callable,
        batch_size: int = 10
    ) -> List:
        """
        Process items in async batches.

        Args:
            items: Items to process
            process_fn: Async function to process each item
            batch_size: Items per batch

        Returns:
            List: Processed results
        """
        import asyncio

        results = []

        for i in range(0, len(items), batch_size):
            batch = items[i:i + batch_size]
            batch_results = await asyncio.gather(
                *[process_fn(item) for item in batch]
            )
            results.extend(batch_results)

        return results

    @staticmethod
    def debounce(wait_ms: float):
        """
        Debounce decorator for functions.

        Args:
            wait_ms: Wait time in milliseconds

        Returns:
            Decorator
        """
        def decorator(func):
            last_call = [0.0]
            timer = [None]

            def debounced(*args, **kwargs):
                current_time = time.time()

                # Cancel previous timer
                if timer[0]:
                    timer[0].cancel()

                # Check if enough time has passed
                if current_time - last_call[0] >= (wait_ms / 1000):
                    last_call[0] = current_time
                    return func(*args, **kwargs)

                # Set new timer
                import threading
                timer[0] = threading.Timer(
                    wait_ms / 1000,
                    lambda: func(*args, **kwargs)
                )
                timer[0].start()

            return debounced

        return decorator


# Global performance monitor instance
performance_monitor = PerformanceMonitor()
