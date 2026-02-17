#!/usr/bin/env python3
"""Quick test to ensure no import errors."""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from claude_multi_terminal.app import ClaudeMultiTerminalApp
    from claude_multi_terminal.widgets.resizable_grid import ResizableSessionGrid
    from claude_multi_terminal.widgets.selectable_richlog import SelectableRichLog
    from claude_multi_terminal.widgets.session_pane import SessionPane

    print("✓ All imports successful")
    print("✓ No AttributeError or import errors")
    print("✓ Application is ready to run")
    print("\nYou can now launch with: python -m claude_multi_terminal")
    sys.exit(0)
except Exception as e:
    print(f"✗ Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
