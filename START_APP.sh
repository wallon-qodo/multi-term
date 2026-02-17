#!/bin/bash
# Simple script to start the app properly

cd "$(dirname "$0")"

echo "Starting Claude Multi-Terminal..."
echo

# Activate venv
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# Run the app
python3 -m claude_multi_terminal.app

echo
echo "App exited."
