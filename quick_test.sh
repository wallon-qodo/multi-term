#!/bin/bash
# Quick test script for claude-multi-terminal

set -e

echo "🧪 Running Quick Tests for claude-multi-terminal"
echo "================================================"
echo ""

# Activate venv
source .venv/bin/activate

echo "✓ Virtual environment activated"
echo ""

# Test imports
echo "Testing imports..."
python -c "from claude_multi_terminal.app import ClaudeMultiTerminalApp; print('✓ App imports successfully')"
python -c "from claude_multi_terminal.api import AnthropicClient; print('✓ API client imports successfully')"
python -c "from claude_multi_terminal.visual import ScreenshotCapture; print('✓ Visual context imports successfully')"
python -c "from claude_multi_terminal.integrations import GitIntegration; print('✓ Integrations import successfully')"
echo ""

# Test instantiation
echo "Testing app instantiation..."
python -c "
from claude_multi_terminal.app import ClaudeMultiTerminalApp
app = ClaudeMultiTerminalApp()
print(f'✓ App instantiates: {app.__class__.__name__}')
print(f'✓ App has {len(app.BINDINGS)} key bindings')
"
echo ""

# Test API client (without real key)
echo "Testing API components..."
python -c "
from claude_multi_terminal.api import TokenTracker, CacheManager
tracker = TokenTracker()
cache = CacheManager()
print('✓ Token tracker created')
print('✓ Cache manager created')
"
echo ""

echo "================================================"
echo "✅ All quick tests passed!"
echo ""
echo "To run full test suite:"
echo "  pytest tests/ -v"
echo ""
echo "To run the app:"
echo "  export ANTHROPIC_API_KEY='your_key_here'"
echo "  multi-term"
