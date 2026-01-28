#!/bin/bash
# Setup script for iOS App Icon Generator

set -e

echo "🚀 Setting up iOS App Icon Generator..."

# Check if Python 3.13 is available
if ! command -v python3.13 &> /dev/null; then
    echo "❌ Python 3.13 is required but not found."
    echo "Please install Python 3.13 using Homebrew:"
    echo "  brew install python@3.13"
    exit 1
fi

# Create virtual environment
echo "📦 Creating virtual environment with Python 3.13..."
python3.13 -m venv venv

# Activate virtual environment
echo "⚡ Activating virtual environment..."
source venv/bin/activate

# Install package
echo "📥 Installing package and dependencies..."
pip install --upgrade pip
pip install -e .

# Check if .env exists
if [ ! -f .env ]; then
    echo ""
    echo "⚠️  No .env file found. Creating from .env.example..."
    cp .env.example .env
    echo ""
    echo "📝 Please edit .env and add your Replicate API token:"
    echo "   Get your token from: https://replicate.com/account/api-tokens"
    echo ""
fi

echo ""
echo "✅ Setup complete!"
echo ""
echo "To use the tool:"
echo "  1. Activate the virtual environment: source venv/bin/activate"
echo "  2. Add your Replicate API token to the .env file"
echo "  3. Run: icon-gen generate --subject \"your subject\""
echo ""
echo "For more information, run: icon-gen --help"
