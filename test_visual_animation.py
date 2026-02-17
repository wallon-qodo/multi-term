#!/usr/bin/env python3
"""Visual test for the animation fix - run this to see it in action."""

import sys
import os

# Change to app directory
os.chdir("/Users/wallonwalusayi/claude-multi-terminal")

print("\n" + "="*70)
print("VISUAL ANIMATION TEST")
print("="*70)
print("\nThis will launch the app. To test the animation:")
print("1. Wait for the app to load")
print("2. Type a question like 'what is 2+2?'")
print("3. Press Enter")
print("4. Watch the processing indicator - it should:")
print("   - Show ONE line that cycles through emojis and dots")
print("   - NOT accumulate multiple lines")
print("5. Press Ctrl+Q to quit when done")
print("\n" + "="*70 + "\n")

input("Press Enter to launch the app...")

try:
    from claude_multi_terminal.app import ClaudeMultiTerminalApp
    app = ClaudeMultiTerminalApp()
    app.run()
    print("\nApp exited normally")
except KeyboardInterrupt:
    print("\nApp interrupted")
except Exception as e:
    print(f"\nError: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
