#!/bin/bash

# NoteBook AI Startup Script
# This script will help you get NoteBook AI running quickly

echo "🤖 Welcome to NoteBook AI Setup!"
echo "=================================="

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.8+ first."
    exit 1
fi

echo "✅ Python 3 found"

# Check if pip is installed
if ! command -v pip3 &> /dev/null; then
    echo "❌ pip3 is not installed. Please install pip first."
    exit 1
fi

echo "✅ pip3 found"

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔄 Activating virtual environment..."
source venv/bin/activate

# Install requirements
echo "📥 Installing dependencies..."
pip install -r requirements.txt

# Check if Ollama is installed
if ! command -v ollama &> /dev/null; then
    echo "⚠️  Ollama is not installed. Please install Ollama first:"
    echo "   Visit: https://ollama.ai"
    echo "   Or run: curl -fsSL https://ollama.ai/install.sh | sh"
    echo ""
    echo "After installing Ollama, run:"
    echo "   ollama pull gemma2:2b"
    echo ""
    read -p "Press Enter to continue when Ollama is ready..."
fi

# Check if model is available
echo "🤖 Checking if AI model is available..."
if ! ollama list | grep -q "gemma"; then
    echo "📥 Downloading AI model (this may take a few minutes)..."
    ollama pull gemma2:2b
fi

echo "✅ Setup complete!"
echo ""
echo "🚀 Starting NoteBook AI..."
echo "   Access the app at: http://localhost:8501"
echo "   Press Ctrl+C to stop"
echo ""

# Start the application
streamlit run app.py --server.port=8501 --server.address=localhost
