#!/usr/bin/env python3
"""Quick test script to verify search panel functionality."""

import sys
import os

# Add the package to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from claude_multi_terminal.app import ClaudeMultiTerminalApp

if __name__ == "__main__":
    app = ClaudeMultiTerminalApp()
    app.run()
