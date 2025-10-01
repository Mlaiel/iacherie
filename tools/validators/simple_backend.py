#!/usr/bin/env python3
"""
iacherie Backend Starter - Version Simplifiée
===========================================
Démarre le backend sans les modules IA complexes pour le développement.
Author: Fahed Mlaiel (mlaiel@live.de)
"""

import os
import sys
from pathlib import Path

# Protection TensorFlow
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'
os.environ['CUDA_VISIBLE_DEVICES'] = ''

# Supprimer les warnings
import warnings
warnings.filterwarnings('ignore')

# Ajouter le chemin du projet
sys.path.insert(0, str(Path(__file__).parent))

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
import time
import logging

# Configuration des logs
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Créer l'application FastAPI
app = FastAPI(
    title="iacherie Backend API",
    description="Backend API pour la plateforme iacherie",
    version="1.0.0"
)

# Configuration CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

start_time = time.time()

@app.get("/")
async def root():
    return {
        "message": "iacherie Backend API",
        "status": "running",
        "version": "1.0.0",
        "uptime": time.time() - start_time
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": time.time(),
        "uptime": time.time() - start_time
    }

@app.get("/system/status")
async def system_status():
    """Status système simplifié pour le développement"""
    return {
        "platform": "iacherie AI Platform - Development Mode",
        "status": "operational",
        "version": "1.0.0-dev",
        "uptime": time.time() - start_time,
        "components": {
            "api": {"status": "healthy", "uptime": time.time() - start_time},
            "database": {"status": "disconnected", "note": "Development mode"},
            "ai_engine": {"status": "disabled", "note": "Development mode"},
            "websocket": {"status": "available", "note": "Ready for connections"}
        },
        "microservices": {
            "total_count": 680,
            "active_count": 10,
            "note": "Development mode - Core services only"
        },
        "performance": {
            "response_time": "< 100ms",
            "cpu_usage": "low",
            "memory_usage": "low"
        }
    }

@app.post("/api/ai/generate")
async def ai_generate(data: dict = None):
    """Endpoint AI simplifié pour le développement"""
    return {
        "success": True,
        "message": "AI Generation - Development Mode",
        "result": "This is a development response. AI features are disabled for faster startup.",
        "timestamp": time.time()
    }

@app.get("/api/monitoring")
async def monitoring():
    """Endpoint de monitoring simplifié"""
    return {
        "system_metrics": {
            "total_modules": 680,
            "healthy_modules": 650,
            "degraded_modules": 25,
            "down_modules": 5,
            "average_response_time": 85,
            "system_uptime": 99.8,
            "total_requests": 125430,
            "total_errors": 23,
            "timestamp": time.time()
        },
        "module_status": [
            {
                "name": "API Gateway",
                "type": "infrastructure",
                "status": "healthy",
                "response_time": 45,
                "last_check": "2025-09-28T15:40:00Z",
                "error_count": 0,
                "uptime_percentage": 99.9
            },
            {
                "name": "Authentication Service",
                "type": "security",
                "status": "healthy",
                "response_time": 32,
                "last_check": "2025-09-28T15:40:00Z",
                "error_count": 0,
                "uptime_percentage": 100.0
            },
            {
                "name": "Content Processor",
                "type": "ai",
                "status": "degraded",
                "response_time": 156,
                "last_check": "2025-09-28T15:40:00Z",
                "error_count": 2,
                "uptime_percentage": 98.5
            }
        ]
    }

if __name__ == "__main__":
    logger.info("🚀 Démarrage du serveur iacherie en mode développement")
    logger.info("📍 API: http://localhost:8000")
    logger.info("📚 Docs: http://localhost:8000/docs")
    
    uvicorn.run(
        "simple_backend:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )