#!/bin/bash

# =============================================================================
# IA Chéries Platform - Development Startup Script
# =============================================================================
# Quick development environment setup
# Author: Fahed Mlaiel (mlaiel@live.de)
# =============================================================================

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_header() {
    echo -e "${BLUE}================================${NC}"
    echo -e "${BLUE}   IA Chéries Development Server   ${NC}"
    echo -e "${BLUE}================================${NC}"
    echo ""
}

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

print_header

# Check if in correct directory
if [[ ! -f "docker-compose.development.yml" ]]; then
    log_error "docker-compose.development.yml not found! Make sure you're in the project root directory."
    exit 1
fi

log_info "Starting IA Chéries development environment..."

# Method 1: Try with Docker Compose
if command -v "docker" &> /dev/null && docker compose version &> /dev/null; then
    log_info "Using Docker Compose to start services..."
    
    # Pull required images first
    log_info "Pulling base images..."
    docker compose -f docker-compose.development.yml pull postgres redis mongo elasticsearch || true
    
    # Start infrastructure services first
    log_info "Starting infrastructure services..."
    docker compose -f docker-compose.development.yml up -d postgres redis mongo elasticsearch
    
    # Wait a bit for infrastructure to be ready
    log_info "Waiting for infrastructure services..."
    sleep 10
    
    # Start main services
    log_info "Starting main application services..."
    docker compose -f docker-compose.development.yml up -d ainflue-backend ainflue-frontend
    
    log_success "Services starting in background!"
    
else
    log_warning "Docker not available, starting services manually..."
    
    # Method 2: Manual startup
    log_info "Starting backend manually..."
    
    # Check for Python
    if command -v python3 &> /dev/null; then
        # Install requirements
        if [[ -f "requirements.txt" ]]; then
            log_info "Installing Python dependencies..."
            python3 -m pip install -r requirements.txt
        fi
        
        # Start backend
        log_info "Starting backend server..."
        cd backend 2>/dev/null || true
        python3 -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload &
        BACKEND_PID=$!
        cd ..
        
        log_success "Backend started (PID: $BACKEND_PID)"
    else
        log_error "Python3 not found!"
        exit 1
    fi
    
    # Start frontend
    if command -v npm &> /dev/null; then
        log_info "Starting frontend..."
        cd frontend
        
        # Install dependencies
        if [[ -f "package.json" ]]; then
            log_info "Installing npm dependencies..."
            npm install
        fi
        
        # Start frontend
        log_info "Starting frontend server..."
        npm run dev &
        FRONTEND_PID=$!
        cd ..
        
        log_success "Frontend started (PID: $FRONTEND_PID)"
    else
        log_warning "npm not found, skipping frontend"
    fi
fi

echo ""
log_success "Development environment is starting!"
echo ""
echo -e "${YELLOW}📍 Available services:${NC}"
echo "   🌐 Frontend: http://localhost:3000"
echo "   🔧 Backend API: http://localhost:8000"
echo "   📚 API Docs: http://localhost:8000/docs"
echo "   ❤️  Health Check: http://localhost:8000/health"
echo ""
echo -e "${YELLOW}🛠️  Useful commands:${NC}"
echo "   📊 Check services: docker compose -f docker-compose.development.yml ps"
echo "   📋 View logs: docker compose -f docker-compose.development.yml logs -f"
echo "   🛑 Stop services: docker compose -f docker-compose.development.yml down"
echo ""
log_info "Press Ctrl+C to stop services when running manually"