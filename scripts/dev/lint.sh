#!/bin/bash
# Ainflue Platform Code Quality Checker
# Runs linting, formatting, and security checks

set -e

echo "🔍 Running Ainflue Code Quality Checks..."

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# Create reports directory
mkdir -p reports

echo "🎨 Formatting code with Black..."
black . --check --diff

echo ""
echo "📦 Checking import order with isort..."
isort . --check-only --diff

echo ""
echo "🔧 Running Flake8 linting..."
flake8 . --output-file=reports/flake8.txt --tee

echo ""
echo "🔒 Running type checking with MyPy..."
mypy . > reports/mypy.txt 2>&1 || echo "Type checking completed with warnings"

echo ""
echo "🛡️ Running security checks with Bandit..."
bandit -r . -f json -o reports/bandit.json || echo "Security scan completed"

echo ""
echo "🔍 Running safety check for vulnerabilities..."
safety check --json --output reports/safety.json || echo "Safety check completed"

echo ""
echo "📊 Running code complexity analysis..."
if command -v radon &> /dev/null; then
    radon cc . --json > reports/complexity.json
    radon mi . --json > reports/maintainability.json
else
    echo "Install radon for complexity analysis: pip install radon"
fi

echo ""
echo "✅ Code quality checks completed!"
echo "📄 Reports available in the 'reports/' directory"