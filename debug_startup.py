#!/usr/bin/env python3
"""Debug why the app exits immediately."""

import sys
import os

print("=" * 60)
print("DEBUG: Starting app startup test")
print("=" * 60)

# Check Claude CLI path
from claude_multi_terminal.config import Config
print(f"\n1. Claude CLI path: {Config.CLAUDE_PATH}")
print(f"   Exists: {os.path.exists(Config.CLAUDE_PATH)}")

# Try importing and creating app
print("\n2. Importing app...")
from claude_multi_terminal.app import ClaudeMultiTerminalApp

print("3. Creating app instance...")
app = ClaudeMultiTerminalApp()

print("4. About to call app.run()...")
print("   (This should take over the terminal)")
print()

try:
    app.run()
    print("\n5. app.run() returned normally")
except KeyboardInterrupt:
    print("\n5. User pressed Ctrl+C")
except Exception as e:
    print(f"\n5. ERROR: {e}")
    import traceback
    traceback.print_exc()

print("\n6. Script finished")
