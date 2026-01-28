#!/bin/bash
# Quick activation script for the virtual environment

if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found. Please run ./setup.sh first."
    exit 1
fi

source venv/bin/activate
echo "✅ Virtual environment activated!"
echo "You can now run: icon-gen generate --subject \"your subject\""
