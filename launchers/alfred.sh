#!/usr/bin/env bash
#
# Alfred Global Launcher (Linux/macOS)
#
# Installation:
#   1. chmod +x launchers/alfred.sh
#   2. sudo cp launchers/alfred.sh /usr/local/bin/alfred
#   3. alfred  (from any directory)
#
# Author: Daniel J Rita (BATDAN)

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Determine Alfred root directory
if [[ -f "$SCRIPT_DIR/../alfred/__init__.py" ]]; then
    # Script is in launchers/ subdirectory
    ALFRED_ROOT="$SCRIPT_DIR/.."
elif [[ -f "$SCRIPT_DIR/alfred/__init__.py" ]]; then
    # Script is in alfred root
    ALFRED_ROOT="$SCRIPT_DIR"
else
    # Fallback: try to find alfred in Python path
    ALFRED_ROOT=""
fi

# Change to Alfred directory if found
if [[ -n "$ALFRED_ROOT" ]]; then
    cd "$ALFRED_ROOT" || exit 1
fi

# Run Alfred as Python module
exec python3 -m alfred "$@"
