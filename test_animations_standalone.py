#!/usr/bin/env python3
"""Standalone test of braille animations (no dependencies)."""

import math
import time

# Braille Animation Generators
DOT_BITS = [[0x01, 0x08], [0x02, 0x10], [0x04, 0x20], [0x40, 0x80]]


def seeded_random(seed: int):
    """Seeded random number generator for consistent animations."""
    s = seed
    def _rand():
        nonlocal s
        s = (s * 1664525 + 1013904223) & 0xffffffff
        return s / 0xffffffff
    return _rand


def gen_pendulum(width: int = 10, max_spread: float = 1.0):
    """Generate pendulum wave animation frames using braille characters."""
    total_frames = 120
    pixel_cols = width * 2
    frames = []

    for t in range(total_frames):
        codes = [0x2800] * width
        progress = t / total_frames
        spread = math.sin(math.pi * progress) * max_spread
        base_phase = progress * math.pi * 8

        for pc in range(pixel_cols):
            swing = math.sin(base_phase + pc * spread)
            center = (1 - swing) * 1.5

            for row in range(4):
                if abs(row - center) < 0.7:
                    codes[pc // 2] |= DOT_BITS[row][pc % 2]

        frames.append(''.join(chr(c) for c in codes))

    return frames


def gen_compress(width: int = 10):
    """Generate compress/squeeze animation frames using braille characters."""
    total_frames = 100
    pixel_cols = width * 2
    total_dots = pixel_cols * 4
    frames = []

    rand = seeded_random(42)
    importance = [rand() for _ in range(total_dots)]

    for t in range(total_frames):
        codes = [0x2800] * width
        progress = t / total_frames
        sieve_threshold = max(0.1, 1 - progress * 1.2)
        squeeze = min(1, progress / 0.85)
        active_width = max(1, pixel_cols * (1 - squeeze * 0.95))

        for pc in range(pixel_cols):
            mapped_pc = (pc / pixel_cols) * active_width
            if mapped_pc >= active_width:
                continue

            target_pc = round(mapped_pc)
            if target_pc >= pixel_cols:
                continue

            char_idx = target_pc // 2
            dc = target_pc % 2

            for row in range(4):
                if importance[pc * 4 + row] < sieve_threshold:
                    codes[char_idx] |= DOT_BITS[row][dc]

        frames.append(''.join(chr(c) for c in codes))

    return frames


def gen_sort(width: int = 10):
    """Generate sorting visualization animation frames using braille characters."""
    pixel_cols = width * 2
    total_frames = 100
    frames = []

    rand = seeded_random(19)
    shuffled = [rand() * 3 for _ in range(pixel_cols)]
    target = [(i / (pixel_cols - 1)) * 3 for i in range(pixel_cols)]

    for t in range(total_frames):
        codes = [0x2800] * width
        progress = t / total_frames
        cursor = progress * pixel_cols * 1.2

        for pc in range(pixel_cols):
            char_idx = pc // 2
            dc = pc % 2
            d = pc - cursor

            if d < -3:
                center = target[pc]
            elif d < 2:
                blend = 1 - (d + 3) / 5
                ease = blend * blend * (3 - 2 * blend)
                center = shuffled[pc] + (target[pc] - shuffled[pc]) * ease

                if abs(d) < 0.8:
                    for r in range(4):
                        codes[char_idx] |= DOT_BITS[r][dc]
                    continue
            else:
                center = (shuffled[pc] +
                         math.sin(progress * math.pi * 16 + pc * 2.7) * 0.6 +
                         math.sin(progress * math.pi * 9 + pc * 1.3) * 0.4)

            center = max(0, min(3, center))

            for r in range(4):
                if abs(r - center) < 0.7:
                    codes[char_idx] |= DOT_BITS[r][dc]

        frames.append(''.join(chr(c) for c in codes))

    return frames


def main():
    """Test all three animations."""
    print("\n" + "=" * 60)
    print("Braille Animation Test - Standalone")
    print("=" * 60)

    # Generate animations
    print("\n1. Generating Pendulum animation...")
    pendulum = gen_pendulum(10, 1.0)
    print(f"   ✓ Generated {len(pendulum)} frames")

    print("\n2. Generating Compress animation...")
    compress = gen_compress(10)
    print(f"   ✓ Generated {len(compress)} frames")

    print("\n3. Generating Sort animation...")
    sort_anim = gen_sort(10)
    print(f"   ✓ Generated {len(sort_anim)} frames")

    print("\n" + "=" * 60)
    print("✓ All animations generated successfully!")
    print("=" * 60)

    # Demo each animation
    animations = [
        ("Pendulum", pendulum, "\033[93m"),  # Yellow
        ("Compress", compress, "\033[91m"),   # Red
        ("Sort", sort_anim, "\033[94m")       # Blue
    ]

    print("\nShowing each animation for 3 seconds...")
    print("(Press Ctrl+C to stop)\n")

    try:
        for name, frames, color in animations:
            print(f"\n{name}:")
            for _ in range(60):  # 3 seconds at 0.05s per frame
                for i in range(len(frames)):
                    print(f"\r{color}{frames[i]}\033[0m {name} ", end="", flush=True)
                    time.sleep(0.05)
            print()

    except KeyboardInterrupt:
        print("\n\n✓ Demo stopped\n")


if __name__ == "__main__":
    main()
