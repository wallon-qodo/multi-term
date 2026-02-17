#!/usr/bin/env python3
"""Simple test to verify terminal works."""

print("=" * 50)
print("TERMINAL TEST")
print("=" * 50)
print()
print("If you can see this text, your terminal works!")
print()
print("Now testing colors:")
print("\033[31mRED TEXT\033[0m")
print("\033[32mGREEN TEXT\033[0m")
print("\033[34mBLUE TEXT\033[0m")
print()
print("Press Ctrl+C to exit...")

import time
try:
    while True:
        time.sleep(1)
        print(".", end="", flush=True)
except KeyboardInterrupt:
    print("\nDone!")
