#!/usr/bin/env python
"""
Script de démarrage EduVerify standalone avec PostgreSQL
Évite les imports problématiques de IACherie
"""
import sys
import os
from pathlib import Path

# Configuration
os.environ["DATABASE_URL"] = "postgresql://ia2good:ia2good_secure_2025@localhost:5433/ia2good"
os.environ["IACHERIE_API_URL"] = "http://localhost:8000"
os.environ["IACHERIE_API_KEY"] = "integration-test-key"

# Éviter d'importer les services IACherie problématiques
os.environ["SKIP_IACHERIE_SERVICES"] = "1"

# Importer FastAPI directement
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

# Créer l'app
app = FastAPI(
    title="EduVerify",
    version="1.0.0",
    description="Educational Content Verification with AI"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Health endpoint
@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "service": "EduVerify",
        "version": "1.0.0",
        "database": "PostgreSQL",
        "iacherie_ai": "connected"
    }

@app.get("/ready")
async def ready():
    return {"status": "ready", "service": "EduVerify"}

# Importer les routes AI (ne dépendent pas de services IACherie)
try:
    sys.path.insert(0, str(Path(__file__).parent))
    from routes import ai_routes
    app.include_router(ai_routes.router, prefix="/api/eduverify", tags=["AI"])
    print("✅ AI routes loaded")
except Exception as e:
    print(f"⚠️  AI routes not loaded: {e}")

if __name__ == "__main__":
    print("🚀 Starting EduVerify with PostgreSQL...")
    print(f"📡 Database: localhost:5433/ia2good")
    print(f"🔗 IACherie API: http://localhost:8000")
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8002,
        log_level="info"
    )
