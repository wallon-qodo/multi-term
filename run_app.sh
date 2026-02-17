#!/bin/bash

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

# Activate virtual environment using full path
. "$SCRIPT_DIR/venv/bin/activate"

# Run the app using the venv's python
exec "$SCRIPT_DIR/venv/bin/python" -m claude_multi_terminal.app
