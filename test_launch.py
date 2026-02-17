#!/usr/bin/env python3
"""Test launching the app to see any errors."""

import sys
import traceback

try:
    from claude_multi_terminal.app import ClaudeMultiTerminalApp
    print("Import successful")

    app = ClaudeMultiTerminalApp()
    print("App created successfully")

    print("Starting app.run()...")
    app.run()

except Exception as e:
    print(f"ERROR: {e}")
    traceback.print_exc()
    sys.exit(1)
