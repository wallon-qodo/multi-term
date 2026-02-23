#!/bin/bash
# Setup script for Anthropic API key

echo "🔑 Anthropic API Key Setup"
echo "=========================="
echo ""

# Check if key is provided
if [ -z "$1" ]; then
    echo "Usage: ./setup_api_key.sh YOUR_API_KEY"
    echo ""
    echo "To get your API key:"
    echo "  1. Visit: https://console.anthropic.com/settings/keys"
    echo "  2. Click 'Create Key'"
    echo "  3. Copy the key (starts with sk-ant-)"
    echo ""
    echo "Then run:"
    echo "  ./setup_api_key.sh sk-ant-api03-YOUR_KEY_HERE"
    exit 1
fi

API_KEY="$1"

# Validate key format
if [[ ! "$API_KEY" =~ ^sk-ant- ]]; then
    echo "❌ Error: Invalid API key format!"
    echo ""
    echo "Anthropic API keys must start with: sk-ant-"
    echo "Your key starts with: ${API_KEY:0:10}..."
    echo ""
    echo "Please get a valid key from:"
    echo "  https://console.anthropic.com/settings/keys"
    exit 1
fi

echo "✓ API key format looks valid"
echo ""

# Add to shell config
SHELL_CONFIG=""
if [ -f "$HOME/.zshrc" ]; then
    SHELL_CONFIG="$HOME/.zshrc"
elif [ -f "$HOME/.bashrc" ]; then
    SHELL_CONFIG="$HOME/.bashrc"
else
    echo "⚠ Could not find .zshrc or .bashrc"
    echo "Add this to your shell config manually:"
    echo ""
    echo "export ANTHROPIC_API_KEY='$API_KEY'"
    echo ""
    exit 0
fi

# Check if already exists
if grep -q "ANTHROPIC_API_KEY" "$SHELL_CONFIG"; then
    echo "⚠ ANTHROPIC_API_KEY already exists in $SHELL_CONFIG"
    echo "Update it manually if needed."
else
    echo "" >> "$SHELL_CONFIG"
    echo "# Anthropic API Key for claude-multi-terminal" >> "$SHELL_CONFIG"
    echo "export ANTHROPIC_API_KEY='$API_KEY'" >> "$SHELL_CONFIG"
    echo "✓ Added ANTHROPIC_API_KEY to $SHELL_CONFIG"
fi

# Set for current session
export ANTHROPIC_API_KEY="$API_KEY"

echo ""
echo "✅ Setup complete!"
echo ""
echo "To use in current terminal:"
echo "  export ANTHROPIC_API_KEY='$API_KEY'"
echo ""
echo "To use in new terminals:"
echo "  source $SHELL_CONFIG"
echo ""
echo "To test the app:"
echo "  cd $(pwd)"
echo "  source .venv/bin/activate"
echo "  multi-term"
