#!/bin/bash

# AI Leader Agent - Quick Start Script

set -e

echo "🤖 Starting AI Leader Agent..."
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed"
    exit 1
fi

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "📥 Installing dependencies..."
pip install -q -r backend/ai_leader/requirements.txt

# Create storage directory
echo "📁 Creating storage directory..."
mkdir -p backend/ai_leader/storage

# Start server
echo ""
echo "✅ Starting AI Leader Server on http://localhost:8001"
echo ""
echo "📊 Dashboard: http://localhost:3001/ai-leader"
echo "📖 Docs: http://localhost:8001/docs"
echo ""
echo "Press Ctrl+C to stop"
echo ""

python backend/ai_leader_server.py
