#!/usr/bin/env python3
"""Test the braille animations to verify they work correctly."""

import sys
import time
from claude_multi_terminal.widgets.session_pane import gen_pendulum, gen_compress, gen_sort


def test_animation(name, frames, color_code):
    """Display an animation to test it."""
    print(f"\n{name} Animation ({len(frames)} frames):")
    print("=" * 50)

    # Show first 10 frames
    for i in range(min(10, len(frames))):
        # Clear line and show frame
        print(f"\r\033[{color_code}m{frames[i]}\033[0m Frame {i+1}/{len(frames)}", end="", flush=True)
        time.sleep(0.05)

    print()  # New line after animation


def main():
    """Test all three braille animations."""
    print("\n" + "=" * 50)
    print("Braille Animation Test")
    print("=" * 50)

    # Test Pendulum
    print("\n1. Testing Pendulum animation...")
    pendulum_frames = gen_pendulum(10, 1.0)
    print(f"   Generated {len(pendulum_frames)} frames")
    print(f"   First frame: {pendulum_frames[0]}")
    test_animation("Pendulum", pendulum_frames, "93")  # Yellow

    # Test Compress
    print("\n2. Testing Compress animation...")
    compress_frames = gen_compress(10)
    print(f"   Generated {len(compress_frames)} frames")
    print(f"   First frame: {compress_frames[0]}")
    test_animation("Compress", compress_frames, "91")  # Red

    # Test Sort
    print("\n3. Testing Sort animation...")
    sort_frames = gen_sort(10)
    print(f"   Generated {len(sort_frames)} frames")
    print(f"   First frame: {sort_frames[0]}")
    test_animation("Sort", sort_frames, "94")  # Blue

    print("\n" + "=" * 50)
    print("✓ All animations generated successfully!")
    print("=" * 50 + "\n")

    # Show a longer demo of pendulum
    print("\nRunning 3-second Pendulum demo...")
    print("(Press Ctrl+C to stop)\n")
    try:
        frame_idx = 0
        while True:
            print(f"\r\033[93m{pendulum_frames[frame_idx]}\033[0m Pendulum ", end="", flush=True)
            frame_idx = (frame_idx + 1) % len(pendulum_frames)
            time.sleep(0.05)
    except KeyboardInterrupt:
        print("\n\n✓ Demo stopped\n")


if __name__ == "__main__":
    main()
