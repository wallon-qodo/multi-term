#!/bin/bash
cd "$(dirname "$0")"
source venv/bin/activate

echo "Starting Claude Multi-Terminal..."
echo "Press Ctrl+Q to quit when ready"
echo ""

python -m claude_multi_terminal.app 2>&1 | tee /tmp/app_error.log

EXIT_CODE=$?

if [ $EXIT_CODE -ne 0 ]; then
    echo ""
    echo "App exited with error code: $EXIT_CODE"
    echo "Error log saved to /tmp/app_error.log"
    echo ""
    echo "Press Enter to continue..."
    read
fi
