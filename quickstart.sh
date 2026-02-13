#!/bin/bash

# Quick Start Script for Multimodal Moderation Project

echo "🚀 Multimodal Moderation Project - Quick Start"
echo "=============================================="
echo ""

# Check if .env exists
if [ ! -f .env ]; then
    echo "⚠️  No .env file found. Copying from .env.example..."
    cp .env.example .env
    echo "✅ Created .env file"
    echo "⚠️  Please edit .env and add your GEMINI_API_KEY before continuing"
    echo ""
    read -p "Press Enter after you've added your API key..."
fi

# Check if virtual environment exists
if [ ! -d ".venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv .venv
    echo "✅ Virtual environment created"
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source .venv/bin/activate

# Install dependencies
echo "📦 Installing dependencies..."
pip install -e . --quiet

echo ""
echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "1. Run tests: uv run pytest tests/ -vv"
echo "2. Run evals: uv run evals/text/test_cases.py"
echo "3. Start app: uv run multimodal-moderation"
echo ""
