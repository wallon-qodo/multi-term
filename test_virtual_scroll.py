#!/usr/bin/env python3
"""
Test script for virtual scrolling performance with large message counts.

Tests:
1. Memory usage with 10,000 messages
2. Scrolling performance (60 FPS target)
3. Rendering latency
4. Message append performance
"""

from textual.app import App, ComposeResult
from textual.containers import Container, Vertical
from textual.widgets import Header, Footer, Static, Button
from textual.reactive import reactive
from claude_multi_terminal.widgets.virtual_scroll import MessageVirtualScroll
import time
import psutil
import os
from dataclasses import dataclass
from typing import List


@dataclass
class PerformanceMetrics:
    """Performance metrics for virtual scrolling."""
    message_count: int
    memory_usage_mb: float
    render_time_ms: float
    scroll_fps: float
    append_time_ms: float


class VirtualScrollTest(App):
    """Test app for virtual scrolling performance."""

    CSS = """
    Screen {
        background: rgb(24,24,24);
    }

    #test-container {
        width: 100%;
        height: 1fr;
        border: solid rgb(255,77,77);
        padding: 1;
    }

    #metrics-panel {
        width: 100%;
        height: auto;
        background: rgb(32,32,32);
        border: solid rgb(100,180,255);
        padding: 1;
        margin-bottom: 1;
    }

    .metric-row {
        width: 100%;
        height: 1;
        color: rgb(240,240,240);
    }

    .metric-label {
        color: rgb(150,150,150);
    }

    .metric-value {
        color: rgb(100,255,100);
    }

    .metric-value-warning {
        color: rgb(255,200,100);
    }

    .metric-value-error {
        color: rgb(255,100,100);
    }

    #button-panel {
        width: 100%;
        height: auto;
        layout: horizontal;
        margin-bottom: 1;
    }

    Button {
        margin-right: 1;
    }
    """

    # Reactive metrics
    message_count = reactive(0)
    memory_mb = reactive(0.0)
    render_time_ms = reactive(0.0)
    scroll_fps = reactive(0.0)

    def compose(self) -> ComposeResult:
        """Compose the test UI."""
        yield Header()

        # Metrics panel
        with Vertical(id="metrics-panel"):
            yield Static(
                self._render_metrics(),
                id="metrics-display",
                classes="metric-row"
            )

        # Button panel
        with Container(id="button-panel"):
            yield Button("Add 100 Messages", id="add-100")
            yield Button("Add 1,000 Messages", id="add-1k")
            yield Button("Add 10,000 Messages", id="add-10k")
            yield Button("Scroll Test", id="scroll-test")
            yield Button("Clear", id="clear")

        # Virtual scroll container
        with Vertical(id="test-container"):
            yield MessageVirtualScroll(
                auto_scroll=True,
                id="virtual-scroll"
            )

        yield Footer()

    def _render_metrics(self) -> str:
        """Render metrics display."""
        lines = []
        lines.append(f"Messages: {self.message_count:,}")
        lines.append(f"Memory: {self.memory_mb:.2f} MB")
        lines.append(f"Render Time: {self.render_time_ms:.2f} ms")
        lines.append(f"Scroll FPS: {self.scroll_fps:.1f}")

        # Add status indicators
        status = []
        if self.message_count >= 10000:
            status.append("✓ 10K test")
        if self.memory_mb < 100:
            status.append("✓ Memory OK")
        else:
            status.append("⚠ Memory high")
        if self.scroll_fps >= 60:
            status.append("✓ 60 FPS")
        elif self.scroll_fps >= 30:
            status.append("⚠ 30+ FPS")
        else:
            status.append("✗ <30 FPS")

        lines.append(f"Status: {' | '.join(status)}")

        return "\n".join(lines)

    def on_mount(self) -> None:
        """Initialize on mount."""
        # Update metrics display
        self._update_metrics()

        # Set timer to update metrics periodically
        self.set_interval(0.5, self._update_metrics)

    def _update_metrics(self) -> None:
        """Update performance metrics."""
        # Get memory usage
        process = psutil.Process(os.getpid())
        self.memory_mb = process.memory_info().rss / 1024 / 1024

        # Get message count
        scroll_widget = self.query_one("#virtual-scroll", MessageVirtualScroll)
        self.message_count = scroll_widget.item_count

        # Update display
        metrics_display = self.query_one("#metrics-display", Static)
        metrics_display.update(self._render_metrics())

    def _generate_messages(self, count: int) -> List[dict]:
        """Generate test messages."""
        messages = []
        for i in range(count):
            # Vary message length for realistic testing
            if i % 10 == 0:
                # Long message (multiple lines)
                content = (
                    f"This is a longer test message #{i} with multiple lines. "
                    * 5
                )
            elif i % 5 == 0:
                # Medium message
                content = f"Medium length message #{i} " * 3
            else:
                # Short message
                content = f"Test message #{i}"

            messages.append({
                "role": "assistant" if i % 2 == 0 else "user",
                "content": content,
                "timestamp": f"{i // 3600:02d}:{(i % 3600) // 60:02d}:{i % 60:02d}"
            })

        return messages

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses."""
        button_id = event.button.id

        if button_id == "add-100":
            self._add_messages(100)
        elif button_id == "add-1k":
            self._add_messages(1000)
        elif button_id == "add-10k":
            self._add_messages(10000)
        elif button_id == "scroll-test":
            self._run_scroll_test()
        elif button_id == "clear":
            self._clear_messages()

    def _add_messages(self, count: int) -> None:
        """Add messages and measure performance."""
        scroll_widget = self.query_one("#virtual-scroll", MessageVirtualScroll)

        # Measure append time
        start_time = time.time()

        messages = self._generate_messages(count)
        for msg in messages:
            scroll_widget.append_message(msg)

        end_time = time.time()
        elapsed_ms = (end_time - start_time) * 1000

        self.render_time_ms = elapsed_ms

        # Show notification
        self.notify(
            f"Added {count:,} messages in {elapsed_ms:.1f}ms "
            f"({count / (elapsed_ms / 1000):.0f} msg/s)",
            severity="information",
            timeout=3
        )

        # Update metrics
        self._update_metrics()

    def _clear_messages(self) -> None:
        """Clear all messages."""
        scroll_widget = self.query_one("#virtual-scroll", MessageVirtualScroll)
        scroll_widget.clear_items()

        self.notify("Cleared all messages", severity="information")
        self._update_metrics()

    def _run_scroll_test(self) -> None:
        """Run scroll performance test."""
        scroll_widget = self.query_one("#virtual-scroll", MessageVirtualScroll)

        if scroll_widget.item_count < 100:
            self.notify(
                "Need at least 100 messages for scroll test",
                severity="warning"
            )
            return

        # Measure scroll FPS
        self.notify("Running scroll test...", severity="information")

        # Schedule scroll test
        self.set_timer(0.1, self._perform_scroll_test)

    async def _perform_scroll_test(self) -> None:
        """Perform the actual scroll test."""
        scroll_widget = self.query_one("#virtual-scroll", MessageVirtualScroll)

        # Scroll to top
        scroll_widget.scroll_to_index(0, animate=False)

        # Measure FPS during scroll
        frames = 0
        start_time = time.time()
        test_duration = 2.0  # 2 seconds

        # Scroll incrementally and count frames
        while time.time() - start_time < test_duration:
            # Scroll down a bit
            current_index = scroll_widget.viewport_start
            next_index = min(
                current_index + 10,
                scroll_widget.item_count - 1
            )

            scroll_widget.scroll_to_index(next_index, animate=False)
            frames += 1

            # Small delay to simulate frame time
            await self._wait(0.016)  # ~60 FPS target

            # If we reached the end, go back to top
            if next_index >= scroll_widget.item_count - 1:
                scroll_widget.scroll_to_index(0, animate=False)

        end_time = time.time()
        elapsed = end_time - start_time
        fps = frames / elapsed

        self.scroll_fps = fps

        # Show results
        if fps >= 60:
            severity = "information"
            status = "✓ Excellent"
        elif fps >= 30:
            severity = "warning"
            status = "⚠ Acceptable"
        else:
            severity = "error"
            status = "✗ Poor"

        self.notify(
            f"Scroll test: {fps:.1f} FPS {status}",
            severity=severity,
            timeout=5
        )

        self._update_metrics()

    async def _wait(self, seconds: float) -> None:
        """Async wait for specified seconds."""
        import asyncio
        await asyncio.sleep(seconds)


def main():
    """Run the virtual scroll test."""
    app = VirtualScrollTest()
    app.run()


if __name__ == "__main__":
    main()
