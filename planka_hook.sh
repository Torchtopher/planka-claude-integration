#!/bin/bash
# Hook script to create Planka cards from completed tasks
# Usage: ./planka_hook.sh "Task name" ["Optional description"]

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PLANKA_SCRIPT="$SCRIPT_DIR/planka_token_integration.py"

# Check if Python script exists
if [ ! -f "$PLANKA_SCRIPT" ]; then
    echo "Error: planka_token_integration.py not found"
    exit 1
fi

# Check if task name is provided
if [ -z "$1" ]; then
    echo "Usage: $0 'Task name' ['Description']"
    exit 1
fi

# Run the Python integration script with uv
cd "$(dirname "$SCRIPT_DIR")" && uv run python "$PLANKA_SCRIPT" "$1" "${2:-}"
