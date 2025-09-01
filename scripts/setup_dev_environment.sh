#!/bin/bash
# Development Environment Setup Script for Ainflue Platform
# Author: Fahed Mlaiel (mlaiel@live.de)
# Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

set -e

echo "🚀 Setting up Ainflue Development Environment..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

# Check if running in Docker
if [ -f /.dockerenv ]; then
    print_info "Running inside Docker container"
    IN_DOCKER=true
else
    print_info "Running on host system"
    IN_DOCKER=false
fi

# Install Python dependencies
print_info "Installing Python dependencies..."
if [ -f "requirements-dev.txt" ]; then
    pip install -r requirements-dev.txt
    print_status "Development dependencies installed"
else
    print_warning "requirements-dev.txt not found, installing basic dependencies"
    pip install pytest black flake8 mypy pre-commit
fi

# Setup pre-commit hooks
if command -v pre-commit &> /dev/null; then
    print_info "Setting up pre-commit hooks..."
    pre-commit install
    print_status "Pre-commit hooks installed"
else
    print_warning "pre-commit not available, skipping hook installation"
fi

# Create necessary directories
print_info "Creating development directories..."
mkdir -p logs storage data test-results performance-reports coverage-reports
print_status "Development directories created"

# Setup environment variables
if [ ! -f ".env.development" ]; then
    print_info "Creating development environment file..."
    cat > .env.development << EOF
# Ainflue Development Environment Configuration
ENVIRONMENT=development
DEBUG=true
LOG_LEVEL=debug

# Database
POSTGRES_HOST=postgres-dev
POSTGRES_PORT=5432
POSTGRES_DB=ainflue_dev
POSTGRES_USER=dev_user
POSTGRES_PASSWORD=dev_password

# Redis
REDIS_HOST=redis-dev
REDIS_PORT=6379
REDIS_DB=0

# MongoDB
MONGODB_HOST=mongodb-dev
MONGODB_PORT=27017
MONGODB_DB=ainflue_dev
MONGODB_USER=dev_user
MONGODB_PASSWORD=dev_password

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
API_WORKERS=1

# Hot Reload
HOT_RELOAD=true
WATCHDOG_ENABLED=true

# Development Features
ENABLE_DEBUG_TOOLBAR=true
ENABLE_PROFILING=true
ENABLE_METRICS=true

# Security (Development Only)
SECRET_KEY=dev-secret-key-change-in-production
JWT_SECRET=dev-jwt-secret
ENCRYPTION_KEY=dev-encryption-key

# External Services (Development)
OPENAI_API_KEY=your-openai-api-key
ANTHROPIC_API_KEY=your-anthropic-api-key
EOF
    print_status "Development environment file created"
fi

# Initialize database (if running with Docker Compose)
if $IN_DOCKER; then
    print_info "Initializing development database..."
    cat > /docker-entrypoint-initdb.d/init-dev.sql << 'EOF'
-- Development database initialization
CREATE DATABASE IF NOT EXISTS ainflue_dev;
CREATE DATABASE IF NOT EXISTS ainflue_test;

-- Create development user
CREATE USER IF NOT EXISTS 'dev_user'@'%' IDENTIFIED BY 'dev_password';
GRANT ALL PRIVILEGES ON ainflue_dev.* TO 'dev_user'@'%';
GRANT ALL PRIVILEGES ON ainflue_test.* TO 'dev_user'@'%';

-- Create test user  
CREATE USER IF NOT EXISTS 'test_user'@'%' IDENTIFIED BY 'test_password';
GRANT ALL PRIVILEGES ON ainflue_test.* TO 'test_user'@'%';

FLUSH PRIVILEGES;
EOF
    print_status "Database initialization script created"
fi

# Setup VS Code configuration
if [ ! -d ".vscode" ]; then
    print_warning "VS Code configuration not found, please ensure .vscode directory exists"
else
    print_status "VS Code configuration found"
fi

# Setup testing environment
print_info "Setting up testing environment..."
if [ ! -f "pytest.ini" ]; then
    cat > pytest.ini << EOF
[tool:pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = 
    -v
    --tb=short
    --strict-markers
    --disable-warnings
    --cov=.
    --cov-report=html:coverage-reports
    --cov-report=term-missing
    --html=test-results/report.html
    --self-contained-html
markers =
    slow: marks tests as slow (deselect with '-m "not slow"')
    integration: marks tests as integration tests
    unit: marks tests as unit tests
    api: marks tests as API tests
    database: marks tests as database tests
    external: marks tests that require external services
EOF
    print_status "pytest configuration created"
fi

# Setup code quality configuration
if [ ! -f "setup.cfg" ]; then
    cat > setup.cfg << EOF
[flake8]
max-line-length = 88
extend-ignore = E203, W503, E501
exclude = 
    .git,
    __pycache__,
    .pytest_cache,
    .venv,
    venv,
    build,
    dist,
    *.egg-info

[mypy]
python_version = 3.11
warn_return_any = True
warn_unused_configs = True
disallow_untyped_defs = True
ignore_missing_imports = True

[isort]
profile = black
multi_line_output = 3
line_length = 88
known_first_party = ainflue
EOF
    print_status "Code quality configuration created"
fi

# Make scripts executable
print_info "Making scripts executable..."
chmod +x scripts/*.py
chmod +x scripts/*.sh
print_status "Scripts made executable"

# Final status check
print_info "Running development environment checks..."

# Check Python version
python_version=$(python --version 2>&1)
print_info "Python version: $python_version"

# Check if required tools are available
tools=("pytest" "black" "flake8" "mypy")
for tool in "${tools[@]}"; do
    if command -v $tool &> /dev/null; then
        print_status "$tool is available"
    else
        print_warning "$tool is not available"
    fi
done

echo ""
echo "🎉 Development environment setup complete!"
echo ""
echo "📝 Next steps:"
echo "1. Start development services: docker-compose -f docker-compose.dev.yml up"
echo "2. Run tests: pytest tests/"
echo "3. Format code: black ."
echo "4. Check code quality: flake8 ."
echo "5. Type check: mypy ."
echo ""
echo "🔧 Development URLs:"
echo "- Main API: http://localhost:8000"
echo "- Swagger UI: http://localhost:8080"
echo "- Database: localhost:5433"
echo "- Redis: localhost:6380"
echo "- MongoDB: localhost:27018"
echo ""
echo "Happy coding! 🚀"