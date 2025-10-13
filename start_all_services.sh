#!/bin/bash
################################################################################
# Script de démarrage complet IACherie + IA2GOOD
# Démarre tous les services avec vraies implémentations IA
################################################################################

set -e

echo "🚀 Démarrage de tous les services IACherie + IA2GOOD..."
echo ""

# Couleurs
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
IACHERIE_DIR="/workspaces/iacherie"
EDUVERIFY_DIR="/workspaces/iacherie/ia2good/microservices/eduverify"
MEDCARE_DIR="/workspaces/iacherie/ia2good/microservices/medcare-ai"

# Export variables d'environnement
export IACHERIE_API_URL="http://localhost:8000"
# Ne pas forcer DATABASE_URL - laisser .env de chaque service

# Fonction health check
wait_for_service() {
    local name=$1
    local url=$2
    local max_attempts=30
    local attempt=0
    
    echo -n "⏳ Attente de $name..."
    while [ $attempt -lt $max_attempts ]; do
        if curl -s "$url" > /dev/null 2>&1; then
            echo -e " ${GREEN}✓${NC}"
            return 0
        fi
        sleep 2
        attempt=$((attempt + 1))
        echo -n "."
    done
    echo -e " ${YELLOW}⚠${NC} (timeout)"
    return 1
}

# 1. Démarrer IACherie API
echo -e "${BLUE}1. Démarrage IACherie API (port 8000)...${NC}"
cd "$IACHERIE_DIR"
nohup python ai_leader_server.py > /tmp/iacherie_api.log 2>&1 &
IACHERIE_PID=$!
echo "   PID: $IACHERIE_PID"
wait_for_service "IACherie" "http://localhost:8000/health"

# 2. Démarrer EduVerify
echo -e "${BLUE}2. Démarrage EduVerify (port 8002)...${NC}"
cd "$EDUVERIFY_DIR"
nohup python -m uvicorn main:app --host 0.0.0.0 --port 8002 > /tmp/eduverify_api.log 2>&1 &
EDUVERIFY_PID=$!
echo "   PID: $EDUVERIFY_PID"
wait_for_service "EduVerify" "http://localhost:8002/health"

# 3. Démarrer MedCare
echo -e "${BLUE}3. Démarrage MedCare AI (port 8003)...${NC}"
cd "$MEDCARE_DIR"
nohup python -m uvicorn main:app --host 0.0.0.0 --port 8003 > /tmp/medcare_api.log 2>&1 &
MEDCARE_PID=$!
echo "   PID: $MEDCARE_PID"
wait_for_service "MedCare" "http://localhost:8003/health"

echo ""
echo -e "${GREEN}════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}✅ TOUS LES SERVICES SONT DÉMARRÉS ET OPÉRATIONNELS!${NC}"
echo -e "${GREEN}════════════════════════════════════════════════════════${NC}"
echo ""

echo "📊 Services actifs:"
echo "   • IACherie API:  http://localhost:8000  (PID: $IACHERIE_PID)"
echo "   • EduVerify:     http://localhost:8002  (PID: $EDUVERIFY_PID)"
echo "   • MedCare AI:    http://localhost:8003  (PID: $MEDCARE_PID)"
echo ""

echo "📝 Logs disponibles:"
echo "   • IACherie:  tail -f /tmp/iacherie_api.log"
echo "   • EduVerify: tail -f /tmp/eduverify_api.log"
echo "   • MedCare:   tail -f /tmp/medcare_api.log"
echo ""

echo "🧪 Tests rapides:"
echo ""
echo "# Test générateur interne (GRATUIT)"
echo 'curl -X POST http://localhost:8000/api/generate/text -H "Content-Type: application/json" -d '"'"'{"prompt": "Explique la grippe", "model": "internal-gpt-xl"}'"'"' | jq .data.text'
echo ""
echo "# Test quiz EduVerify"
echo 'curl -X POST http://localhost:8002/api/eduverify/ai/generate-quiz -H "Content-Type: application/json" -d '"'"'{"content": "La photosynthèse", "num_questions": 2}'"'"' | jq .quiz.questions[0]'
echo ""
echo "# Test analyse médicale MedCare"
echo 'curl -X POST http://localhost:8003/api/medcare/ai/analyze-symptoms -H "Content-Type: application/json" -d '"'"'{"symptoms": "fièvre, toux", "severity": 6}'"'"' | jq .urgency'
echo ""
echo "# Test triage urgence"
echo 'curl -X POST http://localhost:8003/api/medcare/ai/emergency-triage -H "Content-Type: application/json" -d '"'"'{"symptoms": "douleur poitrine, essoufflement"}'"'"' | jq .priority'
echo ""

echo -e "${GREEN}🎉 Système prêt avec VRAIES implémentations IA (0€)!${NC}"
