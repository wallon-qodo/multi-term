#!/usr/bin/env python3
"""Test if the app can start."""

print("Testing app startup...")
print()

try:
    print("1. Importing app...")
    from claude_multi_terminal.app import ClaudeMultiTerminalApp
    print("   ✓ Import successful")

    print("2. Creating app instance...")
    app = ClaudeMultiTerminalApp()
    print("   ✓ App created")

    print("3. Starting app...")
    print("   (If the app works, your screen will change now)")
    print()
    app.run()

except Exception as e:
    print(f"   ✗ ERROR: {e}")
    import traceback
    traceback.print_exc()
