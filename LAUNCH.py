#!/usr/bin/env python3
"""Direct launcher with verbose output."""

import sys
import os

print("=" * 60)
print("CLAUDE MULTI-TERMINAL LAUNCHER")
print("=" * 60)

# Step 1: Check Python version
print(f"\n1. Python version: {sys.version}")

# Step 2: Check working directory
os.chdir("/Users/wallonwalusayi/claude-multi-terminal")
print(f"2. Working directory: {os.getcwd()}")

# Step 3: Check if we can import the app
print("\n3. Importing app...")
try:
    from claude_multi_terminal.app import ClaudeMultiTerminalApp
    print("   ✓ Import successful")
except Exception as e:
    print(f"   ✗ Import failed: {e}")
    sys.exit(1)

# Step 4: Check Claude CLI
print("\n4. Checking Claude CLI...")
claude_path = "/opt/homebrew/bin/claude"
if os.path.exists(claude_path):
    print(f"   ✓ Found at {claude_path}")
else:
    print(f"   ✗ Not found at {claude_path}")
    sys.exit(1)

# Step 5: Check if we have a TTY
print("\n5. Checking terminal...")
if sys.stdin.isatty():
    print("   ✓ Running in a TTY")
else:
    print("   ✗ NOT in a TTY (this is a problem)")

# Step 6: Launch
print("\n6. Launching app...")
print("   The screen should clear and show the multi-terminal interface.")
print("   Press Ctrl+Q to quit when you're done.")
print("")
input("   Press Enter to start...")

try:
    app = ClaudeMultiTerminalApp()
    app.run()
    print("\n✓ App exited normally")
except KeyboardInterrupt:
    print("\n✓ App interrupted by user")
except Exception as e:
    print(f"\n✗ App crashed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
