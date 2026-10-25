#!/bin/bash
# Convenient wrapper for Finlytics AI AWS Instance Manager

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
ROOT_DIR="$(dirname "$DIR")"

cd "$ROOT_DIR"

# Prefer venv python if available
if [ -f "$ROOT_DIR/venv/bin/python" ]; then
    PYTHON_CMD="$ROOT_DIR/venv/bin/python"
elif [ -f "$ROOT_DIR/backend/venv/bin/python" ]; then
    PYTHON_CMD="$ROOT_DIR/backend/venv/bin/python"
else
    PYTHON_CMD="python3"
fi

"$PYTHON_CMD" "$DIR/aws_manager.py" "$@"
