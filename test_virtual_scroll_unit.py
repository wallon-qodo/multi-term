#!/usr/bin/env python3
"""
Unit tests for virtual scrolling implementation.

Tests virtual scroll data structures and algorithms without GUI.
"""

import sys
import time
import psutil
import os
from typing import List, Dict


# Mock classes for testing without Textual
class MockVirtualItem:
    """Mock virtual item for testing."""
    def __init__(self, index: int, content: dict, height: int = 1):
        self.index = index
        self.content = content
        self.height = height
        self.rendered = None


class VirtualScrollCore:
    """Core virtual scrolling logic (no UI dependencies)."""

    def __init__(self):
        self._items: List[MockVirtualItem] = []
        self.viewport_start = 0
        self.viewport_end = 0
        self.viewport_height = 50  # Simulated viewport
        self.overscan_count = 20
        self.max_items_per_render = 100

    def add_items(self, items: List[dict]) -> None:
        """Add items to the virtual list."""
        for i, item in enumerate(items):
            index = len(self._items)
            height = self._estimate_height(item)
            self._items.append(MockVirtualItem(index, item, height))

    def _estimate_height(self, item: dict) -> int:
        """Estimate item height."""
        content = item.get("content", "")
        # Rough estimate: 80 chars per line
        lines = len(content) // 80 + 1
        return max(3, lines + 2)

    def update_viewport(self, scroll_y: int) -> None:
        """Update viewport based on scroll position."""
        if not self._items:
            self.viewport_start = 0
            self.viewport_end = 0
            return

        # Find first visible item
        cumulative_height = 0
        start_index = 0
        for i, item in enumerate(self._items):
            if cumulative_height + item.height > scroll_y:
                start_index = i
                break
            cumulative_height += item.height

        # Find last visible item
        visible_height = 0
        end_index = start_index
        for i in range(start_index, len(self._items)):
            visible_height += self._items[i].height
            end_index = i + 1
            if visible_height >= self.viewport_height + (self.overscan_count * 2):
                break

        # Add overscan at start
        start_index = max(0, start_index - self.overscan_count)

        # Limit maximum rendered items
        if end_index - start_index > self.max_items_per_render:
            end_index = start_index + self.max_items_per_render

        self.viewport_start = start_index
        self.viewport_end = end_index

    def get_visible_items(self) -> List[MockVirtualItem]:
        """Get items in current viewport."""
        return self._items[self.viewport_start:self.viewport_end]

    def get_total_height(self) -> int:
        """Get total content height."""
        return sum(item.height for item in self._items)

    def clear(self) -> None:
        """Clear all items."""
        self._items.clear()
        self.viewport_start = 0
        self.viewport_end = 0


def generate_test_messages(count: int) -> List[dict]:
    """Generate test messages."""
    messages = []
    for i in range(count):
        if i % 10 == 0:
            content = f"Long message #{i} " * 50
        elif i % 5 == 0:
            content = f"Medium message #{i} " * 10
        else:
            content = f"Short message #{i}"

        messages.append({
            "role": "assistant" if i % 2 == 0 else "user",
            "content": content,
            "timestamp": f"{i // 3600:02d}:{(i % 3600) // 60:02d}:{i % 60:02d}"
        })

    return messages


def test_memory_usage():
    """Test memory usage with 10K messages."""
    print("\n" + "=" * 60)
    print("TEST 1: Memory Usage with 10,000 Messages")
    print("=" * 60)

    process = psutil.Process(os.getpid())
    initial_memory = process.memory_info().rss / 1024 / 1024

    scroll = VirtualScrollCore()

    # Add 10K messages
    print(f"Initial memory: {initial_memory:.2f} MB")
    messages = generate_test_messages(10000)

    start_time = time.time()
    scroll.add_items(messages)
    elapsed = time.time() - start_time

    final_memory = process.memory_info().rss / 1024 / 1024
    delta_memory = final_memory - initial_memory

    print(f"Final memory: {final_memory:.2f} MB")
    print(f"Memory delta: {delta_memory:.2f} MB")
    print(f"Load time: {elapsed * 1000:.2f} ms")
    print(f"Messages/second: {10000 / elapsed:.0f}")

    # Check memory constraint
    if delta_memory < 100:
        print("✓ PASS: Memory usage < 100MB")
        return True
    else:
        print("✗ FAIL: Memory usage >= 100MB")
        return False


def test_viewport_calculation():
    """Test viewport calculation accuracy."""
    print("\n" + "=" * 60)
    print("TEST 2: Viewport Calculation")
    print("=" * 60)

    scroll = VirtualScrollCore()
    messages = generate_test_messages(1000)
    scroll.add_items(messages)

    # Test at different scroll positions
    test_positions = [0, 100, 500, 900]
    all_passed = True

    for scroll_y in test_positions:
        scroll.update_viewport(scroll_y)
        visible = scroll.get_visible_items()

        print(f"\nScroll Y: {scroll_y}")
        print(f"  Viewport: [{scroll.viewport_start}:{scroll.viewport_end}]")
        print(f"  Visible items: {len(visible)}")
        print(f"  Items rendered: {scroll.viewport_end - scroll.viewport_start}")

        # Verify constraints
        items_rendered = scroll.viewport_end - scroll.viewport_start
        if items_rendered <= scroll.max_items_per_render:
            print(f"  ✓ Items <= {scroll.max_items_per_render}")
        else:
            print(f"  ✗ Items > {scroll.max_items_per_render}")
            all_passed = False

    if all_passed:
        print("\n✓ PASS: Viewport calculations correct")
    else:
        print("\n✗ FAIL: Viewport calculations incorrect")

    return all_passed


def test_scroll_performance():
    """Test scrolling performance (simulate 60 FPS)."""
    print("\n" + "=" * 60)
    print("TEST 3: Scroll Performance (60 FPS target)")
    print("=" * 60)

    scroll = VirtualScrollCore()
    messages = generate_test_messages(10000)
    scroll.add_items(messages)

    # Simulate scrolling for 2 seconds at 60 FPS
    target_fps = 60
    duration = 2.0
    frames = int(duration * target_fps)

    total_height = scroll.get_total_height()
    scroll_step = total_height // frames

    print(f"Total height: {total_height} lines")
    print(f"Scroll step: {scroll_step} lines/frame")
    print(f"Simulating {frames} frames...")

    start_time = time.time()
    scroll_y = 0

    for frame in range(frames):
        scroll.update_viewport(scroll_y)
        visible = scroll.get_visible_items()

        # Simulate some rendering work
        _ = len(visible)

        scroll_y = min(scroll_y + scroll_step, total_height - scroll.viewport_height)

    elapsed = time.time() - start_time
    actual_fps = frames / elapsed
    avg_frame_time = (elapsed / frames) * 1000

    print(f"\nCompleted {frames} frames in {elapsed:.3f}s")
    print(f"Actual FPS: {actual_fps:.1f}")
    print(f"Average frame time: {avg_frame_time:.3f} ms")
    print(f"Target frame time: {1000/60:.3f} ms (60 FPS)")

    if actual_fps >= 60:
        print("✓ PASS: >= 60 FPS")
        return True
    else:
        print("✗ FAIL: < 60 FPS")
        return False


def test_append_performance():
    """Test message append performance."""
    print("\n" + "=" * 60)
    print("TEST 4: Append Performance")
    print("=" * 60)

    scroll = VirtualScrollCore()

    # Test batch sizes
    batch_sizes = [10, 100, 1000]
    all_passed = True

    for batch_size in batch_sizes:
        messages = generate_test_messages(batch_size)

        start_time = time.time()
        scroll.add_items(messages)
        elapsed = time.time() - start_time

        rate = batch_size / elapsed
        avg_time = (elapsed / batch_size) * 1000

        print(f"\nBatch size: {batch_size}")
        print(f"  Time: {elapsed * 1000:.2f} ms")
        print(f"  Rate: {rate:.0f} msg/s")
        print(f"  Avg per message: {avg_time:.3f} ms")

        # Should handle at least 1000 msg/s
        if rate >= 1000:
            print(f"  ✓ >= 1000 msg/s")
        else:
            print(f"  ✗ < 1000 msg/s")
            all_passed = False

    if all_passed:
        print("\n✓ PASS: Append performance acceptable")
    else:
        print("\n✗ FAIL: Append performance too slow")

    return all_passed


def main():
    """Run all tests."""
    print("\n" + "=" * 60)
    print("VIRTUAL SCROLLING PERFORMANCE TEST SUITE")
    print("=" * 60)

    results = {
        "Memory Usage": test_memory_usage(),
        "Viewport Calculation": test_viewport_calculation(),
        "Scroll Performance": test_scroll_performance(),
        "Append Performance": test_append_performance(),
    }

    print("\n" + "=" * 60)
    print("TEST RESULTS SUMMARY")
    print("=" * 60)

    for test_name, passed in results.items():
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"{test_name:30s} {status}")

    all_passed = all(results.values())
    print("\n" + "=" * 60)
    if all_passed:
        print("ALL TESTS PASSED ✓")
        print("=" * 60)
        return 0
    else:
        print("SOME TESTS FAILED ✗")
        print("=" * 60)
        return 1


if __name__ == "__main__":
    sys.exit(main())
