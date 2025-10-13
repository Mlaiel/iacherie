#!/bin/bash

# Script de démarrage pour tous les services IA2GOOD avec IACherie

echo "🚀 Démarrage de l'intégration IACherie + IA2GOOD"
echo "=============================================="

# Configuration IACherie
export IACHERIE_API_URL="http://localhost:8000"
export IACHERIE_API_KEY=""

# Configuration Database
export DATABASE_URL="postgresql://ia2good:ia2good_secure_2025@localhost:5433/ia2good"

# Arrêter les services existants
echo "📋 Arrêt des services existants..."
pkill -f "python.*ai_leader_server.py" 2>/dev/null
pkill -f "uvicorn.*eduverify" 2>/dev/null
pkill -f "uvicorn.*medcare" 2>/dev/null
sleep 2

# Démarrer IACherie API
echo "🔧 Démarrage IACherie API (port 8000)..."
cd /workspaces/iacherie
nohup python ai_leader_server.py > /tmp/iacherie_api.log 2>&1 &
sleep 5

# Vérifier IACherie
echo "⏳ Vérification IACherie..."
for i in {1..12}; do
    if curl -s http://localhost:8000/health > /dev/null 2>&1; then
        echo "✅ IACherie API démarré"
        break
    fi
    echo "   Tentative $i/12..."
    sleep 5
done

# Démarrer EduVerify
echo "📚 Démarrage EduVerify (port 8002)..."
cd /workspaces/iacherie/ia2good/microservices/eduverify
nohup python -m uvicorn main:app --host 0.0.0.0 --port 8002 > /tmp/eduverify_api.log 2>&1 &
sleep 3

# Démarrer MedCare
echo "🏥 Démarrage MedCare AI (port 8003)..."
cd /workspaces/iacherie/ia2good/microservices/medcare-ai
nohup python -m uvicorn main:app --host 0.0.0.0 --port 8003 > /tmp/medcare_api.log 2>&1 &
sleep 3

echo ""
echo "⏳ Attente démarrage complet (15 secondes)..."
sleep 15

echo ""
echo "🧪 Tests Health Checks"
echo "=============================================="

# Test IACherie
echo "🔧 IACherie API:"
curl -s http://localhost:8000/health | jq -r '"\(.status) - \(.apis_tracked) APIs"'

# Test EduVerify
echo "📚 EduVerify:"
curl -s http://localhost:8002/health | jq -r '"\(.status) - \(.service) v\(.version)"'

# Test MedCare
echo "🏥 MedCare AI:"
curl -s http://localhost:8003/health | jq -r '"\(.status) - \(.service) v\(.version)"'

# Test Endpoints IACherie IA2GOOD
echo ""
echo "🎯 IACherie IA2GOOD Endpoints:"
curl -s http://localhost:8000/api/ai-agents/health | jq -r '"  \(.status) - \(.service)"'
curl -s http://localhost:8000/api/ai-agents/health | jq -r '.endpoints_available[]' | sed 's/^/  • /'

echo ""
echo "=============================================="
echo "✅ Tous les services démarrés!"
echo ""
echo "📋 URLs des services:"
echo "  • IACherie API:     http://localhost:8000"
echo "  • EduVerify:        http://localhost:8002"
echo "  • MedCare AI:       http://localhost:8003"
echo ""
echo "📄 Logs disponibles:"
echo "  • tail -f /tmp/iacherie_api.log"
echo "  • tail -f /tmp/eduverify_api.log"
echo "  • tail -f /tmp/medcare_api.log"
echo ""
echo "🧪 Tester fact-check:"
echo '  curl -X POST http://localhost:8002/api/eduverify/ai/fact-check \\'
echo '    -H "Content-Type: application/json" \\'
echo '    -d '"'"'{"content": "La Terre tourne autour du Soleil"}'"'"' | jq '"'"'.'"'"
