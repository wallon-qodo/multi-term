#!/bin/bash
echo "==================================="
echo "Claude Multi-Terminal Diagnostics"
echo "==================================="
echo ""

cd "$(dirname "$0")"

echo "1. Checking Python..."
source venv/bin/activate
python --version

echo ""
echo "2. Checking Claude CLI..."
if [ -f "/opt/homebrew/bin/claude" ]; then
    echo "✓ Claude CLI found at /opt/homebrew/bin/claude"
    ls -la /opt/homebrew/bin/claude
else
    echo "✗ Claude CLI not found"
    exit 1
fi

echo ""
echo "3. Checking if we have a TTY..."
if [ -t 0 ]; then
    echo "✓ Running in a TTY"
else
    echo "✗ NOT running in a TTY (this might be the problem)"
fi

echo ""
echo "4. Testing app import..."
python -c "from claude_multi_terminal.app import ClaudeMultiTerminalApp; print('✓ App imports successfully')" 2>&1

echo ""
echo "5. Checking terminal size..."
if command -v tput &> /dev/null; then
    echo "Terminal size: $(tput cols)x$(tput lines)"
else
    echo "Cannot determine terminal size"
fi

echo ""
echo "==================================="
echo "If all checks pass, try running:"
echo "  ./run_app.sh"
echo ""
echo "The app should take over your terminal."
echo "Press Ctrl+Q to quit the app."
echo "==================================="
