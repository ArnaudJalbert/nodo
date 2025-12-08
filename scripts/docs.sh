#!/bin/bash
# Script to build and serve MkDocs documentation

set -e

# Check if we're in the project root
if [ ! -f "mkdocs.yml" ]; then
    echo "Error: mkdocs.yml not found. Please run this script from the project root."
    exit 1
fi

# Check if uv is available
if ! command -v uv &> /dev/null; then
    echo "Error: uv is not installed. Please install uv first."
    exit 1
fi

# Install dependencies if needed
if [ ! -d ".venv" ] || [ ! -f "uv.lock" ]; then
    echo "Installing dependencies..."
    uv sync --dev
fi

# Serve documentation (mkdocs serve automatically builds and serves)
echo "Starting MkDocs server..."
echo "Documentation will be available at http://127.0.0.1:8000"
echo "Press Ctrl+C to stop the server"
echo ""

uv run mkdocs serve

