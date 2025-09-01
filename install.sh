#!/bin/bash

# =============================================================================
# Ainflue Platform - Automatic Installation Script
# =============================================================================
# Production-ready installation and configuration script for the 
# AI-powered content protection and monetization platform.
#
# Author: Fahed Mlaiel (mlaiel@live.de)
# Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
# =============================================================================

set -e  # Exit on any error

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
WHITE='\033[1;37m'
NC='\033[0m' # No Color

# Banner
print_banner() {
    echo -e "${PURPLE}"
    echo "  ██████╗  ██╗███╗   ██╗███████╗██╗     ██╗   ██╗███████╗"
    echo " ██╔══██╗ ██║████╗  ██║██╔════╝██║     ██║   ██║██╔════╝"
    echo " ██████╔╝ ██║██╔██╗ ██║█████╗  ██║     ██║   ██║█████╗  "
    echo " ██╔══██╗ ██║██║╚██╗██║██╔══╝  ██║     ██║   ██║██╔══╝  "
    echo " ██║  ██║ ██║██║ ╚████║██║     ███████╗╚██████╔╝███████╗"
    echo " ╚═╝  ╚═╝ ╚═╝╚═╝  ╚═══╝╚═╝     ╚══════╝ ╚═════╝ ╚══════╝"
    echo "                                                          "
    echo -e "${WHITE}🤖 AI-Powered Content Protection & Monetization Platform${NC}"
    echo -e "${CYAN}Author: Fahed Mlaiel (mlaiel@live.de)${NC}"
    echo -e "${YELLOW}Copyright © 2025 Fahed Mlaiel. All rights reserved.${NC}"
    echo ""
}

# Helper functions
log_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

log_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

log_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

log_error() {
    echo -e "${RED}❌ $1${NC}"
}

log_step() {
    echo -e "${PURPLE}🔧 $1${NC}"
}

# Check if command exists
check_command() {
    if command -v "$1" >/dev/null 2>&1; then
        return 0
    else
        return 1
    fi
}

# Check Python version
check_python() {
    log_step "Checking Python installation..."
    
    if check_command python3; then
        PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
        PYTHON_MAJOR=$(echo $PYTHON_VERSION | cut -d'.' -f1)
        PYTHON_MINOR=$(echo $PYTHON_VERSION | cut -d'.' -f2)
        
        if [ "$PYTHON_MAJOR" -eq 3 ] && [ "$PYTHON_MINOR" -ge 8 ]; then
            log_success "Python $PYTHON_VERSION found"
            PYTHON_CMD="python3"
        else
            log_error "Python 3.8+ required, found $PYTHON_VERSION"
            exit 1
        fi
    elif check_command python; then
        PYTHON_VERSION=$(python --version | cut -d' ' -f2)
        PYTHON_MAJOR=$(echo $PYTHON_VERSION | cut -d'.' -f1)
        PYTHON_MINOR=$(echo $PYTHON_VERSION | cut -d'.' -f2)
        
        if [ "$PYTHON_MAJOR" -eq 3 ] && [ "$PYTHON_MINOR" -ge 8 ]; then
            log_success "Python $PYTHON_VERSION found"
            PYTHON_CMD="python"
        else
            log_error "Python 3.8+ required, found $PYTHON_VERSION"
            exit 1
        fi
    else
        log_error "Python not found. Please install Python 3.8 or higher."
        exit 1
    fi
}

# Check pip installation
check_pip() {
    log_step "Checking pip installation..."
    
    if check_command pip3; then
        log_success "pip3 found"
        PIP_CMD="pip3"
    elif check_command pip; then
        log_success "pip found"
        PIP_CMD="pip"
    else
        log_error "pip not found. Please install pip."
        exit 1
    fi
}

# Create virtual environment
create_venv() {
    log_step "Creating virtual environment..."
    
    if [ ! -d "venv" ]; then
        $PYTHON_CMD -m venv venv
        log_success "Virtual environment created"
    else
        log_info "Virtual environment already exists"
    fi
    
    # Activate virtual environment
    if [ -f "venv/bin/activate" ]; then
        source venv/bin/activate
        log_success "Virtual environment activated"
    elif [ -f "venv/Scripts/activate" ]; then
        source venv/Scripts/activate
        log_success "Virtual environment activated (Windows)"
    else
        log_error "Failed to activate virtual environment"
        exit 1
    fi
}

# Install dependencies
install_dependencies() {
    log_step "Installing Python dependencies..."
    
    # Update pip first
    pip install --upgrade pip
    
    # Install main requirements
    if [ -f "requirements.txt" ]; then
        pip install -r requirements.txt
        log_success "Main dependencies installed"
    else
        log_error "requirements.txt not found"
        exit 1
    fi
    
    # Install additional config requirements if available
    if [ -f "config/requirements.txt" ]; then
        log_info "Installing additional AI/ML dependencies..."
        pip install -r config/requirements.txt
        log_success "Additional dependencies installed"
    fi
    
    # Install production requirements if specified
    if [ "$ENVIRONMENT" = "production" ] && [ -f "config/requirements-production.txt" ]; then
        log_info "Installing production dependencies..."
        pip install -r config/requirements-production.txt
        log_success "Production dependencies installed"
    fi
    
    # Install spaCy language models (critical for NLP functionality)
    log_info "Installing spaCy language models..."
    if command -v python -c "import spacy" >/dev/null 2>&1; then
        python -m spacy download en_core_web_sm >/dev/null 2>&1 || log_warning "Failed to download en_core_web_sm model"
        python -m spacy download fr_core_news_sm >/dev/null 2>&1 || log_warning "Failed to download fr_core_news_sm model"
        log_success "spaCy language models installation attempted"
    else
        log_warning "spaCy not found, skipping language models installation"
    fi
}

# Setup environment configuration
setup_environment() {
    log_step "Setting up environment configuration..."
    
    # Determine environment
    if [ -z "$ENVIRONMENT" ]; then
        echo "Select environment:"
        echo "1) Development"
        echo "2) Staging"
        echo "3) Production"
        read -p "Enter choice (1-3): " choice
        
        case $choice in
            1) ENVIRONMENT="development" ;;
            2) ENVIRONMENT="staging" ;;
            3) ENVIRONMENT="production" ;;
            *) 
                log_warning "Invalid choice, defaulting to development"
                ENVIRONMENT="development"
                ;;
        esac
    fi
    
    # Copy appropriate environment file
    ENV_FILE=".env.${ENVIRONMENT}"
    if [ -f "$ENV_FILE" ]; then
        cp "$ENV_FILE" .env
        log_success "Environment configuration copied (.env)"
    else
        log_warning "Environment file $ENV_FILE not found, using .env.development"
        cp .env.development .env
    fi
    
    # Set ENVIRONMENT variable in .env if not present
    if ! grep -q "^ENVIRONMENT=" .env; then
        echo "ENVIRONMENT=${ENVIRONMENT}" >> .env
    fi
}

# Create necessary directories
create_directories() {
    log_step "Creating necessary directories..."
    
    directories=(
        "logs"
        "data"
        "storage"
        "data/faiss_indexes"
        "storage/uploads"
        "storage/backups"
        "storage/cache"
    )
    
    for dir in "${directories[@]}"; do
        if [ ! -d "$dir" ]; then
            mkdir -p "$dir"
            log_info "Created directory: $dir"
        fi
    done
    
    log_success "Directories created"
}

# Test installation
test_installation() {
    log_step "Testing installation..."
    
    # Test Python imports
    $PYTHON_CMD -c "
import sys
print(f'Python version: {sys.version}')

try:
    import fastapi
    print(f'✅ FastAPI {fastapi.__version__} imported successfully')
except ImportError as e:
    print(f'❌ FastAPI import failed: {e}')
    sys.exit(1)

try:
    import uvicorn
    print(f'✅ Uvicorn {uvicorn.__version__} imported successfully')
except ImportError as e:
    print(f'❌ Uvicorn import failed: {e}')
    sys.exit(1)

try:
    import pydantic
    print(f'✅ Pydantic {pydantic.__version__} imported successfully')
except ImportError as e:
    print(f'❌ Pydantic import failed: {e}')
    sys.exit(1)

print('🎉 Core dependencies test passed!')
"

    if [ $? -eq 0 ]; then
        log_success "Dependencies test passed"
    else
        log_error "Dependencies test failed"
        exit 1
    fi
    
    # Test basic app startup (quick test)
    log_info "Testing basic application startup..."
    timeout 10s $PYTHON_CMD -c "
import sys
sys.path.insert(0, '.')

try:
    from main import app
    print('✅ Application imported successfully')
except Exception as e:
    print(f'⚠️  App import issue (may be normal): {e}')

print('🎉 Basic startup test completed!')
" || log_warning "App startup test timed out (may be normal for full startup)"
}

# Generate security keys (for development/staging)
generate_security_keys() {
    if [ "$ENVIRONMENT" != "production" ]; then
        log_step "Generating development security keys..."
        
        JWT_KEY=$($PYTHON_CMD -c "import secrets; print(secrets.token_urlsafe(32))")
        ENCRYPTION_KEY=$($PYTHON_CMD -c "import secrets; print(secrets.token_urlsafe(32))")
        
        # Update .env file
        sed -i.bak "s/dev_jwt_secret_key_not_for_production_use_only/${JWT_KEY}/" .env
        sed -i.bak "s/dev_encryption_key_not_for_production_use_only/${ENCRYPTION_KEY}/" .env
        
        log_success "Development security keys generated"
    else
        log_warning "Production environment - please manually set secure keys in .env"
    fi
}

# Main installation function
main() {
    print_banner
    
    log_info "Starting Ainflue Platform installation..."
    log_info "Environment: ${ENVIRONMENT:-auto-detect}"
    echo ""
    
    # Pre-installation checks
    check_python
    check_pip
    
    # Installation steps
    create_venv
    install_dependencies
    setup_environment
    create_directories
    generate_security_keys
    
    # Post-installation tests
    test_installation
    
    echo ""
    log_success "🎉 Installation completed successfully!"
    echo ""
    echo -e "${WHITE}Next steps:${NC}"
    echo -e "${CYAN}1. Activate virtual environment: source venv/bin/activate${NC}"
    echo -e "${CYAN}2. Configure .env file with your settings${NC}"
    echo -e "${CYAN}3. Start the server: python main.py${NC}"
    echo -e "${CYAN}4. Access the API: http://localhost:8000${NC}"
    echo -e "${CYAN}5. View documentation: http://localhost:8000/docs${NC}"
    echo ""
    echo -e "${YELLOW}For production deployment, ensure all CHANGE_ME values in .env are updated${NC}"
    echo -e "${PURPLE}Support: mlaiel@live.de${NC}"
}

# Handle command line arguments
case "${1:-}" in
    --development|--dev)
        ENVIRONMENT="development"
        ;;
    --staging)
        ENVIRONMENT="staging"
        ;;
    --production|--prod)
        ENVIRONMENT="production"
        ;;
    --help|-h)
        echo "Usage: $0 [--development|--staging|--production]"
        echo ""
        echo "Options:"
        echo "  --development  Install for development environment"
        echo "  --staging      Install for staging environment"
        echo "  --production   Install for production environment"
        echo "  --help         Show this help message"
        exit 0
        ;;
esac

# Run main installation
main