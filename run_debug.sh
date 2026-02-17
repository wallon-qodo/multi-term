#!/bin/bash

echo "======================================"
echo "Claude Multi-Terminal - Debug Mode"
echo "======================================"
echo ""
echo "Step 1: Changing directory..."
cd "$(dirname "$0")"
echo "Current directory: $(pwd)"
echo ""

echo "Step 2: Activating virtual environment..."
source venv/bin/activate
echo "Python: $(which python)"
echo "Python version: $(python --version)"
echo ""

echo "Step 3: Checking Claude CLI..."
if [ -f "/opt/homebrew/bin/claude" ]; then
    echo "✓ Claude CLI found"
else
    echo "✗ Claude CLI NOT found"
    read -p "Press Enter to exit..."
    exit 1
fi
echo ""

echo "Step 4: Starting app..."
echo "The app should take over this window in 2 seconds..."
echo "If nothing happens, press Ctrl+C and report back."
sleep 2

python -m claude_multi_terminal.app 2>&1

EXIT_CODE=$?
echo ""
echo "======================================"
echo "App exited with code: $EXIT_CODE"
echo "======================================"
echo ""
read -p "Press Enter to close..."
