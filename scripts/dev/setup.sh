#!/bin/bash
# Ainflue Platform Development Setup Script
# This script sets up the development environment

set -e

echo "🚀 Setting up Ainflue Development Environment..."

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "⬆️ Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo "📚 Installing dependencies..."
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Create necessary directories
echo "📁 Creating necessary directories..."
mkdir -p logs data storage backups

# Copy environment files
echo "⚙️ Setting up environment configuration..."
if [ ! -f ".env" ]; then
    cp .env.development .env
    echo "✅ Created .env file from .env.development"
fi

# Setup pre-commit hooks
echo "🔗 Setting up pre-commit hooks..."
pre-commit install

# Initialize database (if needed)
echo "🗄️ Database setup..."
# Add database initialization commands here if needed

# Create .gitignore additions for development
echo "📝 Updating .gitignore for development..."
cat >> .gitignore << EOF

# Development additions
.vscode/settings.json.local
.env.local
*.local
profile.svg
bandit-report.json
safety-report.json
htmlcov/
.coverage
.nyc_output
coverage.xml
*.cover
.hypothesis/
.pytest_cache/
EOF

echo "✅ Development environment setup complete!"
echo ""
echo "🎯 Quick start commands:"
echo "  source venv/bin/activate    # Activate virtual environment"
echo "  python main.py              # Run the application"
echo "  ./scripts/dev/run.sh        # Run with hot-reload"
echo "  ./scripts/dev/test.sh       # Run tests"
echo "  docker-compose up           # Run with Docker"
echo ""
echo "📖 Open http://localhost:8000/docs for API documentation"