#!/bin/bash

# 🚀 AINFLUENCER ENTERPRISE QUICK START
# Script de démarrage rapide pour tous les services enterprise
# Author: Fahed Mlaiel - DevOps Expert Implementation

set -e

# Colors pour l'affichage
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Configuration par défaut
BACKEND_PORT=${BACKEND_PORT:-8000}
FRONTEND_PORT=${FRONTEND_PORT:-3000}
MONITORING_PORT=${MONITORING_PORT:-8080}

echo -e "${PURPLE}"
echo "======================================================"
echo "🚀 AINFLUENCER ENTERPRISE QUICK START"
echo "======================================================"
echo -e "${NC}"

# Fonction pour vérifier les prérequis
check_prerequisites() {
    echo -e "${BLUE}🔍 Checking prerequisites...${NC}"
    
    # Node.js
    if ! command -v node &> /dev/null; then
        echo -e "${RED}❌ Node.js not found. Please install Node.js 18+${NC}"
        exit 1
    fi
    NODE_VERSION=$(node --version | cut -d'v' -f2 | cut -d'.' -f1)
    if [ "$NODE_VERSION" -lt 18 ]; then
        echo -e "${RED}❌ Node.js version $NODE_VERSION found. Please upgrade to Node.js 18+${NC}"
        exit 1
    fi
    echo -e "${GREEN}✅ Node.js $(node --version) detected${NC}"
    
    # Python
    if ! command -v python3 &> /dev/null; then
        echo -e "${RED}❌ Python3 not found. Please install Python 3.8+${NC}"
        exit 1
    fi
    PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f2)
    if [ "$PYTHON_VERSION" -lt 8 ]; then
        echo -e "${RED}❌ Python version too old. Please upgrade to Python 3.8+${NC}"
        exit 1
    fi
    echo -e "${GREEN}✅ Python $(python3 --version) detected${NC}"
    
    # Docker (optionnel)
    if command -v docker &> /dev/null; then
        echo -e "${GREEN}✅ Docker $(docker --version | cut -d' ' -f3 | cut -d',' -f1) detected${NC}"
    else
        echo -e "${YELLOW}⚠️  Docker not found (optional for development)${NC}"
    fi
    
    echo ""
}

# Fonction pour installer les dépendances
install_dependencies() {
    echo -e "${BLUE}📦 Installing dependencies...${NC}"
    
    # Frontend dependencies
    echo -e "${CYAN}📱 Installing frontend dependencies...${NC}"
    if [ -d "frontend" ]; then
        cd frontend
        if [ ! -d "node_modules" ]; then
            npm install
            echo -e "${GREEN}✅ Frontend dependencies installed${NC}"
        else
            echo -e "${YELLOW}⚡ Frontend dependencies already installed${NC}"
        fi
        cd ..
    else
        echo -e "${YELLOW}⚠️  Frontend directory not found, skipping...${NC}"
    fi
    
    # Backend dependencies
    echo -e "${CYAN}🔧 Installing backend dependencies...${NC}"
    if [ -f "requirements.txt" ]; then
        if ! python3 -m pip list | grep -q fastapi; then
            python3 -m pip install -r requirements.txt
            echo -e "${GREEN}✅ Backend dependencies installed${NC}"
        else
            echo -e "${YELLOW}⚡ Backend dependencies already installed${NC}"
        fi
    else
        echo -e "${YELLOW}⚠️  requirements.txt not found, skipping...${NC}"
    fi
    
    # Monitoring dependencies
    if [ -f "requirements-monitoring.txt" ]; then
        python3 -m pip install -r requirements-monitoring.txt
    fi
    
    echo ""
}

# Fonction pour démarrer le backend
start_backend() {
    echo -e "${BLUE}🔧 Starting backend services...${NC}"
    
    if [ -f "main.py" ]; then
        echo -e "${CYAN}Starting FastAPI backend on port $BACKEND_PORT...${NC}"
        nohup python3 -m uvicorn main:app --host 0.0.0.0 --port $BACKEND_PORT --reload > backend.log 2>&1 &
        BACKEND_PID=$!
        echo $BACKEND_PID > .backend.pid
        echo -e "${GREEN}✅ Backend started (PID: $BACKEND_PID)${NC}"
        
        # Attendre que le backend soit prêt
        echo -e "${CYAN}⏳ Waiting for backend to be ready...${NC}"
        sleep 5
        
        # Vérifier si le backend répond
        if curl -sf http://localhost:$BACKEND_PORT/health > /dev/null 2>&1; then
            echo -e "${GREEN}✅ Backend health check passed${NC}"
        else
            echo -e "${YELLOW}⚠️  Backend health check failed, but service is running${NC}"
        fi
    else
        echo -e "${YELLOW}⚠️  main.py not found, skipping backend start${NC}"
    fi
    
    echo ""
}

# Fonction pour démarrer le frontend
start_frontend() {
    echo -e "${BLUE}📱 Starting frontend service...${NC}"
    
    if [ -d "frontend" ]; then
        cd frontend
        echo -e "${CYAN}Starting Next.js frontend on port $FRONTEND_PORT...${NC}"
        
        # Créer le fichier .env.local s'il n'existe pas
        if [ ! -f ".env.local" ]; then
            cat > .env.local << EOF
# Ainfluencer Frontend Configuration
NEXT_PUBLIC_API_URL=http://localhost:$BACKEND_PORT
NEXT_PUBLIC_WS_URL=ws://localhost:8765
BACKEND_URL=http://localhost:$BACKEND_PORT
NODE_ENV=development
EOF
            echo -e "${GREEN}✅ Created .env.local configuration${NC}"
        fi
        
        nohup npm run dev -- --port $FRONTEND_PORT > ../frontend.log 2>&1 &
        FRONTEND_PID=$!
        echo $FRONTEND_PID > ../.frontend.pid
        echo -e "${GREEN}✅ Frontend started (PID: $FRONTEND_PID)${NC}"
        cd ..
    else
        echo -e "${YELLOW}⚠️  Frontend directory not found, skipping frontend start${NC}"
    fi
    
    echo ""
}

# Fonction pour démarrer le monitoring
start_monitoring() {
    echo -e "${BLUE}📊 Starting monitoring services...${NC}"
    
    if [ -f "enterprise-monitor.py" ]; then
        echo -e "${CYAN}Starting enterprise monitoring...${NC}"
        nohup python3 enterprise-monitor.py > monitoring.log 2>&1 &
        MONITORING_PID=$!
        echo $MONITORING_PID > .monitoring.pid
        echo -e "${GREEN}✅ Monitoring started (PID: $MONITORING_PID)${NC}"
    else
        echo -e "${YELLOW}⚠️  enterprise-monitor.py not found, skipping monitoring${NC}"
    fi
    
    echo ""
}

# Fonction pour vérifier les services
check_services() {
    echo -e "${BLUE}🔍 Checking all services...${NC}"
    
    # Backend health
    if curl -sf http://localhost:$BACKEND_PORT/health > /dev/null 2>&1; then
        echo -e "${GREEN}✅ Backend (port $BACKEND_PORT): HEALTHY${NC}"
    else
        echo -e "${RED}❌ Backend (port $BACKEND_PORT): DOWN${NC}"
    fi
    
    # Frontend health  
    if curl -sf http://localhost:$FRONTEND_PORT > /dev/null 2>&1; then
        echo -e "${GREEN}✅ Frontend (port $FRONTEND_PORT): HEALTHY${NC}"
    else
        echo -e "${YELLOW}⏳ Frontend (port $FRONTEND_PORT): STARTING...${NC}"
    fi
    
    # API endpoints test
    echo -e "${CYAN}🧪 Testing API endpoints...${NC}"
    if [ -f "test-api-suite.py" ]; then
        python3 test-api-suite.py --url http://localhost:$FRONTEND_PORT > api-test-results.log 2>&1
        if [ $? -eq 0 ]; then
            echo -e "${GREEN}✅ API tests: PASSED${NC}"
        else
            echo -e "${YELLOW}⚠️  API tests: Some issues detected (check api-test-results.log)${NC}"
        fi
    fi
    
    echo ""
}

# Fonction pour afficher le résumé
show_summary() {
    echo -e "${PURPLE}"
    echo "======================================================"
    echo "🎉 AINFLUENCER ENTERPRISE STARTED SUCCESSFULLY!"
    echo "======================================================"
    echo -e "${NC}"
    
    echo -e "${GREEN}📱 Frontend Dashboard:${NC} http://localhost:$FRONTEND_PORT"
    echo -e "${GREEN}🔧 Backend API:${NC} http://localhost:$BACKEND_PORT"
    echo -e "${GREEN}📊 API Documentation:${NC} http://localhost:$BACKEND_PORT/docs"
    echo -e "${GREEN}🔍 Enterprise Monitoring:${NC} http://localhost:$FRONTEND_PORT/monitoring"
    echo ""
    
    echo -e "${CYAN}📋 Quick Links:${NC}"
    echo -e "  • AI Services: http://localhost:$FRONTEND_PORT/api/ai-services/agents"
    echo -e "  • Audio Processing: http://localhost:$FRONTEND_PORT/api/audio/generate"
    echo -e "  • Security Center: http://localhost:$FRONTEND_PORT/api/security/alerts"
    echo -e "  • System Monitoring: http://localhost:$FRONTEND_PORT/api/monitoring"
    echo ""
    
    echo -e "${YELLOW}📝 Log Files:${NC}"
    echo -e "  • Backend: backend.log"
    echo -e "  • Frontend: frontend.log"
    echo -e "  • Monitoring: monitoring.log"
    echo -e "  • API Tests: api-test-results.log"
    echo ""
    
    echo -e "${BLUE}🛠️  Management Commands:${NC}"
    echo -e "  • Stop all: ./quick-start.sh stop"
    echo -e "  • Restart: ./quick-start.sh restart"
    echo -e "  • Status: ./quick-start.sh status"
    echo -e "  • Logs: ./quick-start.sh logs"
    echo ""
}

# Fonction pour arrêter tous les services
stop_services() {
    echo -e "${YELLOW}🛑 Stopping all services...${NC}"
    
    # Backend
    if [ -f ".backend.pid" ]; then
        BACKEND_PID=$(cat .backend.pid)
        if kill -0 $BACKEND_PID 2>/dev/null; then
            kill $BACKEND_PID
            echo -e "${GREEN}✅ Backend stopped${NC}"
        fi
        rm -f .backend.pid
    fi
    
    # Frontend
    if [ -f ".frontend.pid" ]; then
        FRONTEND_PID=$(cat .frontend.pid)
        if kill -0 $FRONTEND_PID 2>/dev/null; then
            kill $FRONTEND_PID
            echo -e "${GREEN}✅ Frontend stopped${NC}"
        fi
        rm -f .frontend.pid
    fi
    
    # Monitoring
    if [ -f ".monitoring.pid" ]; then
        MONITORING_PID=$(cat .monitoring.pid)
        if kill -0 $MONITORING_PID 2>/dev/null; then
            kill $MONITORING_PID
            echo -e "${GREEN}✅ Monitoring stopped${NC}"
        fi
        rm -f .monitoring.pid
    fi
    
    echo -e "${GREEN}🎉 All services stopped successfully${NC}"
}

# Fonction pour afficher le statut
show_status() {
    echo -e "${BLUE}📊 Service Status:${NC}"
    
    # Backend
    if [ -f ".backend.pid" ]; then
        BACKEND_PID=$(cat .backend.pid)
        if kill -0 $BACKEND_PID 2>/dev/null; then
            echo -e "${GREEN}✅ Backend (PID: $BACKEND_PID): RUNNING${NC}"
        else
            echo -e "${RED}❌ Backend: STOPPED${NC}"
        fi
    else
        echo -e "${RED}❌ Backend: NOT STARTED${NC}"
    fi
    
    # Frontend
    if [ -f ".frontend.pid" ]; then
        FRONTEND_PID=$(cat .frontend.pid)
        if kill -0 $FRONTEND_PID 2>/dev/null; then
            echo -e "${GREEN}✅ Frontend (PID: $FRONTEND_PID): RUNNING${NC}"
        else
            echo -e "${RED}❌ Frontend: STOPPED${NC}"
        fi
    else
        echo -e "${RED}❌ Frontend: NOT STARTED${NC}"
    fi
    
    # Monitoring
    if [ -f ".monitoring.pid" ]; then
        MONITORING_PID=$(cat .monitoring.pid)
        if kill -0 $MONITORING_PID 2>/dev/null; then
            echo -e "${GREEN}✅ Monitoring (PID: $MONITORING_PID): RUNNING${NC}"
        else
            echo -e "${RED}❌ Monitoring: STOPPED${NC}"
        fi
    else
        echo -e "${RED}❌ Monitoring: NOT STARTED${NC}"
    fi
}

# Fonction pour afficher les logs
show_logs() {
    echo -e "${BLUE}📄 Recent Logs:${NC}"
    
    if [ -f "backend.log" ]; then
        echo -e "${CYAN}--- Backend Logs (last 10 lines) ---${NC}"
        tail -n 10 backend.log
        echo ""
    fi
    
    if [ -f "frontend.log" ]; then
        echo -e "${CYAN}--- Frontend Logs (last 10 lines) ---${NC}"
        tail -n 10 frontend.log
        echo ""
    fi
    
    if [ -f "monitoring.log" ]; then
        echo -e "${CYAN}--- Monitoring Logs (last 10 lines) ---${NC}"
        tail -n 10 monitoring.log
        echo ""
    fi
}

# Gestion des arguments
case "${1:-start}" in
    "start")
        check_prerequisites
        install_dependencies
        start_backend
        start_frontend
        start_monitoring
        sleep 10  # Attendre que tous les services démarrent
        check_services
        show_summary
        ;;
    "stop")
        stop_services
        ;;
    "restart")
        stop_services
        sleep 3
        $0 start
        ;;
    "status")
        show_status
        ;;
    "logs")
        show_logs
        ;;
    "test")
        if [ -f "test-api-suite.py" ]; then
            python3 test-api-suite.py --url http://localhost:$FRONTEND_PORT --save-report
        else
            echo -e "${RED}❌ test-api-suite.py not found${NC}"
        fi
        ;;
    *)
        echo -e "${YELLOW}Usage: $0 {start|stop|restart|status|logs|test}${NC}"
        echo ""
        echo -e "${CYAN}Commands:${NC}"
        echo -e "  start   - Start all enterprise services"
        echo -e "  stop    - Stop all services" 
        echo -e "  restart - Restart all services"
        echo -e "  status  - Show service status"
        echo -e "  logs    - Show recent logs"
        echo -e "  test    - Run API test suite"
        exit 1
        ;;
esac