#!/bin/bash

# 🛡️ SCRIPT DE PROTECTION API ROUTE REELLE - Stop Simulation Overwrites
# Surveille et protège l'API route.ts contre les écrasements automatiques
# Author: Fahed Mlaiel

set -e

API_FILE="/workspaces/iaCherie/frontend/app/api/ai/generate/route.ts"
BACKUP_FILE="/workspaces/iaCherie/frontend/app/api/ai/generate/route.ts.backup.real"
LOG_FILE="/workspaces/iaCherie/api-protection.log"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log() {
    echo -e "${GREEN}[$(date +%H:%M:%S)]${NC} $1" | tee -a $LOG_FILE
}

warn() {
    echo -e "${YELLOW}[$(date +%H:%M:%S)] WARNING:${NC} $1" | tee -a $LOG_FILE
}

error() {
    echo -e "${RED}[$(date +%H:%M:%S)] ERROR:${NC} $1" | tee -a $LOG_FILE
}

# Fonction pour vérifier si le fichier contient du code de simulation
is_simulation() {
    local file="$1"
    if grep -q "generateSimulatedContent\|Simulation de génération\|FAKE.*CONTENT\|simulatedData" "$file" 2>/dev/null; then
        return 0  # C'est une simulation
    else
        return 1  # C'est le vrai code
    fi
}

# Fonction pour restaurer l'API réelle
restore_real_api() {
    log "🔥 CORRUPTION DÉTECTÉE! Restauration de l'API réelle..."
    cp "$BACKUP_FILE" "$API_FILE"
    log "✅ API réelle restaurée depuis la sauvegarde"
    
    # Identifier le processus responsable si possible
    if lsof "$API_FILE" 2>/dev/null; then
        warn "Processus utilisant le fichier API:"
        lsof "$API_FILE" 2>/dev/null | tee -a $LOG_FILE
    fi
}

# Fonction pour faire une protection en mode continu
protect_continuously() {
    log "🛡️ DÉMARRAGE PROTECTION CONTINUE DE L'API RÉELLE"
    log "📁 Surveillance: $API_FILE"
    
    while true; do
        if [ -f "$API_FILE" ]; then
            # Vérifier si le fichier a été corrompu avec du code de simulation
            if is_simulation "$API_FILE"; then
                error "🚨 CORRUPTION DÉTECTÉE: L'API contient du code de simulation!"
                restore_real_api
            else
                # Vérifier que le fichier contient bien la connexion au vrai backend
                if grep -q "BACKEND_URL.*localhost:8000\|REAL AI CONNECTION.*NO SIMULATION" "$API_FILE" 2>/dev/null; then
                    log "✅ API réelle confirmée - Connexion au vrai backend détectée"
                else
                    warn "⚠️  Contenu suspect dans l'API - Vérification approfondie"
                    if ! grep -q "fetch.*ai-agents" "$API_FILE" 2>/dev/null; then
                        error "🚨 API compromise - Pas de connexion au backend réel!"
                        restore_real_api
                    fi
                fi
            fi
        else
            error "🚨 FICHIER API SUPPRIMÉ! Restauration immédiate..."
            restore_real_api
        fi
        
        sleep 5  # Vérification toutes les 5 secondes
    done
}

# Fonction pour identifier les scripts suspects
find_suspicious_scripts() {
    log "🔍 Recherche de scripts suspects qui pourraient écraser l'API..."
    
    # Chercher dans les fichiers Python, Shell et JS récemment modifiés
    find /workspaces/iaCherie -type f \( -name "*.py" -o -name "*.sh" -o -name "*.js" \) -newermt "1 day ago" | \
    while read file; do
        if grep -q "route\.ts\|api.*generate.*route\|cat.*EOF.*route" "$file" 2>/dev/null; then
            warn "🚨 Script suspect trouvé: $file"
            echo "   Contenu suspect:" | tee -a $LOG_FILE
            grep -n "route\.ts\|api.*generate.*route\|cat.*EOF.*route" "$file" | head -3 | tee -a $LOG_FILE
            echo "" | tee -a $LOG_FILE
        fi
    done
}

# Fonction pour créer une protection en lecture seule
make_readonly_protection() {
    log "🔒 Activation protection lecture seule sur l'API"
    chmod 444 "$API_FILE"
    log "✅ Fichier API maintenant en lecture seule"
}

# Fonction pour désactiver la protection lecture seule
remove_readonly_protection() {
    log "🔓 Désactivation protection lecture seule"
    chmod 664 "$API_FILE"
    log "✅ Fichier API maintenant modifiable"
}

# Menu principal
case "${1:-help}" in
    "protect")
        protect_continuously
        ;;
    "check")
        log "🔍 Vérification de l'état de l'API..."
        if [ -f "$API_FILE" ]; then
            if is_simulation "$API_FILE"; then
                error "🚨 L'API contient du code de simulation!"
                restore_real_api
            else
                log "✅ L'API contient le vrai code de connexion backend"
            fi
        else
            error "🚨 Le fichier API n'existe pas!"
        fi
        ;;
    "restore")
        restore_real_api
        ;;
    "backup")
        log "💾 Création sauvegarde de l'API actuelle..."
        cp "$API_FILE" "$BACKUP_FILE"
        log "✅ Sauvegarde créée: $BACKUP_FILE"
        ;;
    "find-suspects")
        find_suspicious_scripts
        ;;
    "readonly")
        make_readonly_protection
        ;;
    "writable")
        remove_readonly_protection
        ;;
    "help"|*)
        echo "🛡️ SCRIPT DE PROTECTION API RÉELLE"
        echo "Usage: $0 {protect|check|restore|backup|find-suspects|readonly|writable|help}"
        echo ""
        echo "Commandes:"
        echo "  protect       - Surveillance continue et restauration automatique"
        echo "  check         - Vérification unique de l'état de l'API"
        echo "  restore       - Restauration immédiate de l'API réelle"
        echo "  backup        - Créer une sauvegarde de l'API actuelle"
        echo "  find-suspects - Rechercher scripts suspects qui écrasent l'API"
        echo "  readonly      - Mettre l'API en lecture seule"
        echo "  writable      - Enlever protection lecture seule"
        echo "  help          - Afficher cette aide"
        echo ""
        echo "Exemple: $0 protect    # Démarre protection continue"
        echo "         $0 check      # Vérification rapide"
        ;;
esac