#!/bin/bash

##############################################################################
# 🔍 ENTERPRISE MONITORING LAUNCHER - DevOps + Monitoring Expert
# Script de démarrage complet du système de monitoring IA Chéries
# Author: Fahed Mlaiel - Multi-Expert Implementation
##############################################################################

set -euo pipefail

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOG_DIR="$SCRIPT_DIR/logs"
PID_DIR="$SCRIPT_DIR/pids"

# Couleurs pour les logs
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Fonctions utilitaires
log_info() {
    echo -e "${BLUE}[INFO]${NC} $(date '+%Y-%m-%d %H:%M:%S') - $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $(date '+%Y-%m-%d %H:%M:%S') - $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $(date '+%Y-%m-%d %H:%M:%S') - $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $(date '+%Y-%m-%d %H:%M:%S') - $1"
}

# Créer les répertoires nécessaires
setup_directories() {
    log_info "Création des répertoires de monitoring..."
    
    mkdir -p "$LOG_DIR"
    mkdir -p "$PID_DIR"
    mkdir -p "$SCRIPT_DIR/data"
    mkdir -p "$SCRIPT_DIR/backups"
    
    log_success "Répertoires créés avec succès"
}

# Vérifier les dépendances
check_dependencies() {
    log_info "Vérification des dépendances..."
    
    local deps=("python3" "node" "npm")
    local missing_deps=()
    
    for dep in "${deps[@]}"; do
        if ! command -v "$dep" &> /dev/null; then
            missing_deps+=("$dep")
        fi
    done
    
    if [ ${#missing_deps[@]} -ne 0 ]; then
        log_error "Dépendances manquantes: ${missing_deps[*]}"
        log_info "Installation des dépendances..."
        
        # Installation automatique selon l'OS
        if [[ "$OSTYPE" == "linux-gnu"* ]]; then
            sudo apt-get update
            for dep in "${missing_deps[@]}"; do
                case $dep in
                    "python3")
                        sudo apt-get install -y python3 python3-pip
                        ;;
                    "node"|"npm")
                        curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
                        sudo apt-get install -y nodejs
                        ;;
                esac
            done
        elif [[ "$OSTYPE" == "darwin"* ]]; then
            # macOS avec Homebrew
            if ! command -v brew &> /dev/null; then
                log_error "Homebrew requis pour macOS"
                exit 1
            fi
            
            for dep in "${missing_deps[@]}"; do
                case $dep in
                    "python3")
                        brew install python3
                        ;;
                    "node"|"npm")
                        brew install node
                        ;;
                esac
            done
        fi
    fi
    
    log_success "Toutes les dépendances sont disponibles"
}

# Installer les packages Python
setup_python_environment() {
    log_info "Configuration de l'environnement Python..."
    
    # Vérifier si un environnement virtuel existe
    if [ ! -d "$SCRIPT_DIR/venv" ]; then
        log_info "Création de l'environnement virtuel Python..."
        python3 -m venv "$SCRIPT_DIR/venv"
    fi
    
    # Activer l'environnement virtuel
    source "$SCRIPT_DIR/venv/bin/activate"
    
    # Installer les dépendances Python
    log_info "Installation des packages Python..."
    pip install --upgrade pip
    pip install aiohttp sqlite3 asyncio logging dataclasses
    
    log_success "Environnement Python configuré"
}

# Configurer le frontend Next.js
setup_frontend_environment() {
    log_info "Configuration de l'environnement Frontend..."
    
    cd "$SCRIPT_DIR/frontend"
    
    # Installer les dépendances Node.js si nécessaire
    if [ ! -d "node_modules" ]; then
        log_info "Installation des dépendances Node.js..."
        npm install
    fi
    
    # Installer sqlite3 pour l'API de monitoring
    npm install sqlite3
    
    cd "$SCRIPT_DIR"
    log_success "Environnement Frontend configuré"
}

# Démarrer le monitoring backend Python
start_backend_monitoring() {
    log_info "Démarrage du monitoring backend Python..."
    
    # Activer l'environnement virtuel
    source "$SCRIPT_DIR/venv/bin/activate"
    
    # Démarrer le script de monitoring en arrière-plan
    nohup python3 "$SCRIPT_DIR/enterprise-monitor.py" > "$LOG_DIR/backend-monitoring.log" 2>&1 &
    echo $! > "$PID_DIR/backend-monitoring.pid"
    
    log_success "Monitoring backend démarré (PID: $(cat "$PID_DIR/backend-monitoring.pid"))"
}

# Démarrer le frontend Next.js
start_frontend_dashboard() {
    log_info "Démarrage du dashboard frontend Next.js..."
    
    cd "$SCRIPT_DIR/frontend"
    
    # Démarrer Next.js en mode développement
    nohup npm run dev > "$LOG_DIR/frontend-dashboard.log" 2>&1 &
    echo $! > "$PID_DIR/frontend-dashboard.pid"
    
    cd "$SCRIPT_DIR"
    log_success "Dashboard frontend démarré (PID: $(cat "$PID_DIR/frontend-dashboard.pid"))"
}

# Vérifier le statut des services
check_services_status() {
    log_info "Vérification du statut des services..."
    
    local services=("backend-monitoring" "frontend-dashboard")
    
    for service in "${services[@]}"; do
        if [ -f "$PID_DIR/$service.pid" ]; then
            local pid=$(cat "$PID_DIR/$service.pid")
            if ps -p $pid > /dev/null 2>&1; then
                log_success "$service est en cours d'exécution (PID: $pid)"
            else
                log_warning "$service n'est pas en cours d'exécution"
                rm -f "$PID_DIR/$service.pid"
            fi
        else
            log_warning "Pas de PID trouvé pour $service"
        fi
    done
}

# Afficher les informations de connexion
show_connection_info() {
    log_info "Informations de connexion:"
    echo
    echo "🔍 Enterprise Monitoring Dashboard:"
    echo "   Frontend: http://localhost:3000"
    echo "   Monitoring API: http://localhost:3000/api/monitoring"
    echo
    echo "📊 Logs de monitoring:"
    echo "   Backend: tail -f $LOG_DIR/backend-monitoring.log"
    echo "   Frontend: tail -f $LOG_DIR/frontend-dashboard.log"
    echo "   Monitoring Principal: tail -f enterprise-monitoring.log"
    echo
    echo "🛠️ Gestion des services:"
    echo "   Arrêter tout: $0 stop"
    echo "   Redémarrer: $0 restart"
    echo "   Statut: $0 status"
    echo
}

# Arrêter les services
stop_services() {
    log_info "Arrêt des services de monitoring..."
    
    local services=("backend-monitoring" "frontend-dashboard")
    
    for service in "${services[@]}"; do
        if [ -f "$PID_DIR/$service.pid" ]; then
            local pid=$(cat "$PID_DIR/$service.pid")
            if ps -p $pid > /dev/null 2>&1; then
                log_info "Arrêt de $service (PID: $pid)..."
                kill $pid
                sleep 2
                
                # Force kill si nécessaire
                if ps -p $pid > /dev/null 2>&1; then
                    kill -9 $pid
                fi
                
                log_success "$service arrêté"
            fi
            rm -f "$PID_DIR/$service.pid"
        fi
    done
}

# Redémarrer les services
restart_services() {
    log_info "Redémarrage des services de monitoring..."
    stop_services
    sleep 3
    start_all_services
}

# Démarrer tous les services
start_all_services() {
    setup_directories
    check_dependencies
    setup_python_environment
    setup_frontend_environment
    start_backend_monitoring
    sleep 5
    start_frontend_dashboard
    sleep 3
    check_services_status
    show_connection_info
}

# Fonction principale
main() {
    case "${1:-start}" in
        "start")
            log_info "🔍 Démarrage du système Enterprise Monitoring..."
            start_all_services
            ;;
        "stop")
            log_info "🛑 Arrêt du système Enterprise Monitoring..."
            stop_services
            ;;
        "restart")
            log_info "🔄 Redémarrage du système Enterprise Monitoring..."
            restart_services
            ;;
        "status")
            log_info "📊 Statut du système Enterprise Monitoring..."
            check_services_status
            ;;
        "logs")
            log_info "📋 Affichage des logs en temps réel..."
            if [ -f "$LOG_DIR/backend-monitoring.log" ] && [ -f "$LOG_DIR/frontend-dashboard.log" ]; then
                tail -f "$LOG_DIR/backend-monitoring.log" "$LOG_DIR/frontend-dashboard.log"
            else
                log_warning "Logs non trouvés. Les services sont-ils démarrés?"
            fi
            ;;
        "clean")
            log_info "🧹 Nettoyage des fichiers temporaires..."
            stop_services
            rm -rf "$LOG_DIR" "$PID_DIR" "$SCRIPT_DIR/data" "$SCRIPT_DIR/venv"
            log_success "Nettoyage terminé"
            ;;
        *)
            echo "Usage: $0 {start|stop|restart|status|logs|clean}"
            echo
            echo "Commandes disponibles:"
            echo "  start   - Démarre le système de monitoring complet"
            echo "  stop    - Arrête tous les services"
            echo "  restart - Redémarre tous les services"
            echo "  status  - Affiche le statut des services"
            echo "  logs    - Affiche les logs en temps réel"
            echo "  clean   - Nettoie tous les fichiers temporaires"
            exit 1
            ;;
    esac
}

# Gestion des signaux pour arrêt propre
trap 'log_warning "Signal reçu, arrêt des services..."; stop_services; exit 0' SIGINT SIGTERM

# Exécution du script
main "$@"