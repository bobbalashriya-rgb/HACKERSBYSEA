#!/bin/bash
# Convenient wrapper for Finlytics AI AWS Instance Manager

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
ROOT_DIR="$(dirname "$DIR")"

cd "$ROOT_DIR"

# Ensure boto3 is installed
if ! python3 -c "import boto3" 2>/dev/null; then
    echo "Installing boto3..."
    python3 -m pip install boto3
fi

python3 scripts/aws_manager.py "$@"
