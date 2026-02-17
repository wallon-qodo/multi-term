#!/bin/bash
# Quick launch script for Claude Multi-Terminal

cd "$(dirname "$0")"

# Activate venv if it exists
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# Run the app
python3 -m claude_multi_terminal
