#!/usr/bin/env python3
"""Test app startup and capture output."""

import sys
import os

print("="*70)
print("APP STARTUP TEST")
print("="*70)
print()

print("Environment:")
print(f"  TERM: {os.environ.get('TERM', 'not set')}")
print(f"  TERM_PROGRAM: {os.environ.get('TERM_PROGRAM', 'not set')}")
print(f"  Python: {sys.version}")
print()

print("Step 1: Importing app...")
try:
    from claude_multi_terminal.app import ClaudeMultiTerminalApp
    print("  ✓ Import successful")
except Exception as e:
    print(f"  ✗ Import failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print()
print("Step 2: Creating app instance...")
try:
    app = ClaudeMultiTerminalApp()
    print("  ✓ App created")
except Exception as e:
    print(f"  ✗ App creation failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print()
print("Step 3: Checking app configuration...")
print(f"  Title: {app.TITLE}")
print(f"  Has run method: {hasattr(app, 'run')}")
print()

print("Step 4: Starting app...")
print("  The app will now start.")
print("  If you see the interface, the app is working!")
print("  Press Ctrl+C or 'q' to exit.")
print()
print("="*70)
print()

import time
time.sleep(1)

try:
    app.run()
    print()
    print("✓ App exited cleanly")
except KeyboardInterrupt:
    print()
    print("✓ App interrupted by user")
except Exception as e:
    print()
    print(f"✗ App crashed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
