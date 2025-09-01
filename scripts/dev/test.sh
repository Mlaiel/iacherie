#!/bin/bash
# Ainflue Platform Test Runner
# Comprehensive testing with coverage and reporting

set -e

echo "🧪 Running Ainflue Platform Tests..."

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# Set testing environment
export ENVIRONMENT=testing
export PYTHONPATH=$(pwd)

# Create test reports directory
mkdir -p test_reports

# Run tests with coverage
echo "📊 Running tests with coverage..."
python -m pytest \
    tests/ \
    -v \
    --tb=short \
    --cov=. \
    --cov-report=html:test_reports/htmlcov \
    --cov-report=xml:test_reports/coverage.xml \
    --cov-report=term-missing \
    --junitxml=test_reports/junit.xml \
    --benchmark-only \
    --benchmark-sort=mean \
    --benchmark-json=test_reports/benchmark.json

echo ""
echo "✅ Tests completed!"
echo "📊 Coverage report: test_reports/htmlcov/index.html"
echo "📈 Benchmark results: test_reports/benchmark.json"