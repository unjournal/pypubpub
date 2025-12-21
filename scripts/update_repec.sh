#!/bin/bash
# Wrapper script to generate and deploy RePEc RDF files
# This ensures the correct Python version (3.10+) is used

set -e  # Exit on error

# Get script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

cd "$PROJECT_ROOT"

# Try to find Python 3.10+ (required for union type syntax)
PYTHON=""

# Check for venv (Python 3.13)
if [ -f "venv/bin/python" ]; then
    VERSION=$(venv/bin/python --version 2>&1 | grep -oE '[0-9]+\.[0-9]+' | head -1)
    MAJOR=$(echo $VERSION | cut -d. -f1)
    MINOR=$(echo $VERSION | cut -d. -f2)
    if [ "$MAJOR" -ge 3 ] && [ "$MINOR" -ge 10 ]; then
        PYTHON="venv/bin/python"
        echo "✓ Using Python $VERSION from venv/"
    fi
fi

# Check for .venv (might be older)
if [ -z "$PYTHON" ] && [ -f ".venv/bin/python" ]; then
    VERSION=$(.venv/bin/python --version 2>&1 | grep -oE '[0-9]+\.[0-9]+' | head -1)
    MAJOR=$(echo $VERSION | cut -d. -f1)
    MINOR=$(echo $VERSION | cut -d. -f2)
    if [ "$MAJOR" -ge 3 ] && [ "$MINOR" -ge 10 ]; then
        PYTHON=".venv/bin/python"
        echo "✓ Using Python $VERSION from .venv/"
    fi
fi

# Check system Python 3
if [ -z "$PYTHON" ] && command -v python3 &> /dev/null; then
    VERSION=$(python3 --version 2>&1 | grep -oE '[0-9]+\.[0-9]+' | head -1)
    MAJOR=$(echo $VERSION | cut -d. -f1)
    MINOR=$(echo $VERSION | cut -d. -f2)
    if [ "$MAJOR" -ge 3 ] && [ "$MINOR" -ge 10 ]; then
        PYTHON="python3"
        echo "✓ Using system Python $VERSION"
    fi
fi

if [ -z "$PYTHON" ]; then
    echo "❌ Error: Python 3.10+ required but not found"
    echo "Available Python versions:"
    [ -f "venv/bin/python" ] && venv/bin/python --version
    [ -f ".venv/bin/python" ] && .venv/bin/python --version
    command -v python3 &> /dev/null && python3 --version
    exit 1
fi

# Run the script with all passed arguments
echo "Running RePEc generator..."
$PYTHON scripts/generate_and_deploy_repec.py "$@"
