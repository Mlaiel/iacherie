#!/bin/bash

set -e

echo "================================================================"
echo "🚀 DÉMARRAGE COMPLET - IACHERIE + IA2GOOD (PostgreSQL)"
echo "================================================================"
echo ""

# Configuration
export PYTHONPATH="/workspaces/iacherie:/workspaces/iacherie/ia2good/shared-services:$PYTHONPATH"
export IACHERIE_API_URL="http://localhost:8000"
export IACHERIE_API_KEY="integration-test-key"
export DATABASE_URL="postgresql://ia2good:ia2good_secure_2025@localhost:5433/ia2good"

# 1. Nettoyage des anciens processus
echo "🧹 Nettoyage des anciens processus..."
pkill -f "uvicorn.*8000" 2>/dev/null || true
pkill -f "uvicorn.*8001" 2>/dev/null || true
pkill -f "uvicorn.*8002" 2>/dev/null || true
pkill -f "uvicorn.*8003" 2>/dev/null || true
pkill -f "python.*ai_leader_server" 2>/dev/null || true
sleep 2
echo ""

# 2. Vérifier PostgreSQL
echo "🔍 Vérification PostgreSQL..."
if docker ps | grep -q ia2good-postgres; then
    echo "✅ PostgreSQL container actif"
else
    echo "⚠️  Démarrage du container PostgreSQL..."
    docker start ia2good-postgres 2>/dev/null || \
    docker run -d --name ia2good-postgres \
        --restart unless-stopped \
        -e POSTGRES_PASSWORD=ia2good_secure_2025 \
        -e POSTGRES_USER=ia2good \
        -e POSTGRES_DB=ia2good \
        -p 5433:5432 \
        postgres:16-alpine
    sleep 3
    echo "✅ PostgreSQL démarré"
fi
echo ""

# 3. Démarrer IACherie API
echo "🚀 Démarrage IACherie API (Port 8000)..."
cd /workspaces/iacherie
nohup python ai_leader_server.py > /tmp/iacherie_api.log 2>&1 &
IACHERIE_PID=$!
echo "   PID: $IACHERIE_PID"
echo "⏳ Attente du chargement des modèles IA (15 secondes)..."
sleep 15

# Vérifier IACherie
if curl -f -s -o /dev/null http://localhost:8000/health; then
    echo "✅ IACherie API opérationnelle"
else
    echo "⚠️  IACherie API en cours de démarrage (modèles en chargement)..."
    echo "   Attente supplémentaire (10 secondes)..."
    sleep 10
    if curl -f -s -o /dev/null http://localhost:8000/health; then
        echo "✅ IACherie API opérationnelle"
    else
        echo "⚠️  IACherie API prend plus de temps - Continuons quand même"
        echo "   Logs: tail -f /tmp/iacherie_api.log"
    fi
fi
echo ""

# 4. Démarrer Guardian
echo "🚀 Démarrage Guardian (Port 8001)..."
cd /workspaces/iacherie/ia2good/microservices/ia2good
nohup python -m uvicorn main:app --host 0.0.0.0 --port 8001 > /tmp/guardian.log 2>&1 &
GUARDIAN_PID=$!
echo "   PID: $GUARDIAN_PID"
sleep 3

if curl -f -s -o /dev/null http://localhost:8001/health; then
    echo "✅ Guardian opérationnel"
else
    echo "⚠️  Guardian en cours de démarrage..."
fi
echo ""

# 5. Démarrer EduVerify avec PostgreSQL
echo "🚀 Démarrage EduVerify (Port 8002) avec PostgreSQL..."
cd /workspaces/iacherie/ia2good/microservices/eduverify
nohup python -m uvicorn main:app --host 0.0.0.0 --port 8002 > /tmp/eduverify.log 2>&1 &
EDUVERIFY_PID=$!
echo "   PID: $EDUVERIFY_PID"
sleep 3

if curl -f -s -o /dev/null http://localhost:8002/health; then
    echo "✅ EduVerify opérationnel"
else
    echo "⚠️  EduVerify en cours de démarrage..."
fi
echo ""

# 6. Démarrer MedCare avec PostgreSQL
echo "🚀 Démarrage MedCare (Port 8003) avec PostgreSQL..."
cd /workspaces/iacherie/ia2good/microservices/medcare-ai
nohup python -m uvicorn main:app --host 0.0.0.0 --port 8003 > /tmp/medcare.log 2>&1 &
MEDCARE_PID=$!
echo "   PID: $MEDCARE_PID"
sleep 3

if curl -f -s -o /dev/null http://localhost:8003/health; then
    echo "✅ MedCare opérationnel"
else
    echo "⚠️  MedCare en cours de démarrage..."
fi
echo ""

# 7. Résumé final
echo "================================================================"
echo "✅ TOUS LES SERVICES SONT DÉMARRÉS"
echo "================================================================"
echo ""
echo "📊 Services actifs:"
echo "  • IACherie API:  http://localhost:8000  (PID: $IACHERIE_PID)"
echo "  • Guardian:      http://localhost:8001  (PID: $GUARDIAN_PID)"
echo "  • EduVerify:     http://localhost:8002  (PID: $EDUVERIFY_PID)"
echo "  • MedCare:       http://localhost:8003  (PID: $MEDCARE_PID)"
echo "  • PostgreSQL:    localhost:5433         (Docker)"
echo ""
echo "📝 Logs disponibles:"
echo "  • tail -f /tmp/iacherie_api.log"
echo "  • tail -f /tmp/guardian.log"
echo "  • tail -f /tmp/eduverify.log"
echo "  • tail -f /tmp/medcare.log"
echo ""
echo "🔍 Tests de santé:"
echo "  • curl http://localhost:8000/health"
echo "  • curl http://localhost:8001/health"
echo "  • curl http://localhost:8002/health"
echo "  • curl http://localhost:8003/health"
echo ""
echo "🛑 Pour arrêter tous les services:"
echo "  pkill -f 'uvicorn.*800[0-3]' && pkill -f 'python.*ai_leader_server'"
echo ""
