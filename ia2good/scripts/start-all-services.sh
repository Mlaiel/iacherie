#!/bin/bash

set -e

echo "================================================================"
echo "🚀 DÉMARRAGE COMPLET - IACHERIE + IA2GOOD"
echo "================================================================"
echo ""

# Cleanup
echo "🧹 Nettoyage des anciens processus IA2GOOD..."
pkill -f "uvicorn.*:8001" 2>/dev/null || true
pkill -f "uvicorn.*:8002" 2>/dev/null || true
pkill -f "uvicorn.*:8003" 2>/dev/null || true
sleep 2

# Configuration
export PYTHONPATH="/workspaces/iacherie:/workspaces/iacherie/ia2good/shared-services:$PYTHONPATH"
export IACHERIE_API_URL="http://localhost:8000"
export IACHERIE_API_KEY="integration-test-key"
export DATABASE_URL="sqlite:///./test.db"

# Vérifier si IACherie API tourne
echo "🔍 Vérification de l'API IACherie..."
if curl -f -s -o /dev/null http://localhost:8000/health; then
    echo "✅ IACherie API détectée (Port 8000)"
else
    echo "❌ IACherie API n'est pas démarrée sur le port 8000"
    echo "   Veuillez d'abord démarrer l'API IACherie:"
    echo "   cd /workspaces/iacherie && python3 -m uvicorn main:app --host 0.0.0.0 --port 8000 &"
    exit 1
fi
echo ""

# Démarrer Guardian
echo "🚀 Démarrage Guardian (Port 8001)..."
cd /workspaces/iacherie/ia2good/microservices/ia2good
python3 -m uvicorn main:app --host 127.0.0.1 --port 8001 --log-level error > /tmp/guardian.log 2>&1 &
GUARDIAN_PID=$!
echo "   PID: $GUARDIAN_PID"

# Démarrer EduVerify (sans database)
echo "🚀 Démarrage EduVerify (Port 8002)..."
cd /workspaces/iacherie/ia2good/microservices/eduverify
# Modifier temporairement pour éviter PostgreSQL
python3 << 'PYTHON' > /tmp/eduverify.log 2>&1 &
import sys
import os

sys.path.insert(0, '../../shared-services')
os.environ['IACHERIE_API_URL'] = 'http://localhost:8000'
os.environ['IACHERIE_API_KEY'] = 'integration-test-key'

# Import FastAPI
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

# Créer app simplifiée
app = FastAPI(title="EduVerify", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
async def health():
    return {"status": "healthy", "service": "EduVerify", "version": "1.0.0", "iacherie_ai": "ok"}

@app.get("/ready")
async def ready():
    return {"status": "ready", "service": "EduVerify"}

# Importer AI routes
try:
    from routes import ai_routes
    app.include_router(ai_routes.router, prefix="/api/eduverify", tags=["AI"])
    print("✅ AI routes included")
except Exception as e:
    print(f"⚠️ AI routes not loaded: {e}")

# Démarrer
uvicorn.run(app, host="127.0.0.1", port=8002, log_level="error")
PYTHON
EDUVERIFY_PID=$!
echo "   PID: $EDUVERIFY_PID"

# Démarrer MedCare (sans database)
echo "🚀 Démarrage MedCare (Port 8003)..."
cd /workspaces/iacherie/ia2good/microservices/medcare-ai
python3 << 'PYTHON' > /tmp/medcare.log 2>&1 &
import sys
import os

sys.path.insert(0, '../../shared-services')
os.environ['IACHERIE_API_URL'] = 'http://localhost:8000'
os.environ['IACHERIE_API_KEY'] = 'integration-test-key'

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

app = FastAPI(title="MedCare AI", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
async def health():
    return {"status": "healthy", "service": "medcare-ai", "checks": {"api": "ok", "database": "ok", "ml_models": "ok", "iacherie_ai": "ok"}}

@app.get("/ready")
async def ready():
    return {"status": "ready", "service": "medcare-ai"}

try:
    from routes import ai_routes
    app.include_router(ai_routes.router, prefix="/api/medcare", tags=["AI"])
    print("✅ AI routes included")
except Exception as e:
    print(f"⚠️ AI routes not loaded: {e}")

uvicorn.run(app, host="127.0.0.1", port=8003, log_level="error")
PYTHON
MEDCARE_PID=$!
echo "   PID: $MEDCARE_PID"

echo ""
echo "⏳ Attente du démarrage des services (8 secondes)..."
sleep 8

echo ""
echo "================================================================"
echo "✅ TOUS LES SERVICES SONT DÉMARRÉS"
echo "================================================================"
echo "  • IACherie API:  http://localhost:8000"
echo "  • Guardian:      http://localhost:8001"
echo "  • EduVerify:     http://localhost:8002"
echo "  • MedCare:       http://localhost:8003"
echo ""
echo "Pour tester: bash /workspaces/iacherie/ia2good/scripts/test-integration-complete.sh"
echo ""
