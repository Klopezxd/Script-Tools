#!/usr/bin/env bash
# Script-Tools Unified Multiplatform CLI Launcher (Linux & macOS)
set -e

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

if [ -f "$DIR/.venv/bin/python" ]; then
    PYTHON_CMD="$DIR/.venv/bin/python"
elif [ -f "$DIR/.venv/Scripts/python.exe" ]; then
    PYTHON_CMD="$DIR/.venv/Scripts/python.exe"
elif command -v python3 >/dev/null 2>&1; then
    PYTHON_CMD="python3"
elif command -v python >/dev/null 2>&1; then
    PYTHON_CMD="python"
else
    echo "[ERROR] Python 3.10+ no está instalado o no se encuentra en el PATH." >&2
    exit 1
fi

if [ $# -eq 0 ]; then
    exec "$PYTHON_CMD" "$DIR/tools.py" menu
else
    exec "$PYTHON_CMD" "$DIR/tools.py" "$@"
fi
