"""
🚀 AI LEADER BACKEND SERVER - FastAPI

Serveur principal pour l'AI Leader Agent avec monitoring en temps réel

Author: Fahed Mlaiel
Date: October 2025
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
import logging
from contextlib import asynccontextmanager
import os
from dotenv import load_dotenv

# Charger les variables d'environnement depuis .env
load_dotenv()

# Import des routes AI Leader
from backend.routes.ai_leader_routes import router as ai_leader_router
from backend.routes.ai_leader_examples import router as examples_router

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# Lifecycle management
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Gestion du lifecycle de l'application"""
    logger.info("🚀 Démarrage du AI Leader Backend Server...")
    
    # Startup
    from backend.ai_leader_agent import ai_leader_agent
    logger.info(f"✅ AI Leader Agent chargé - Phase: {ai_leader_agent.current_phase.value}")
    logger.info(f"📊 {len(ai_leader_agent.api_learning_data)} APIs observées")
    logger.info(f"🎯 {len(ai_leader_agent.internal_capabilities)} capacités développées")
    
    yield
    
    # Shutdown
    logger.info("🛑 Arrêt du AI Leader Backend Server...")
    await ai_leader_agent._save_state()
    logger.info("💾 État de l'agent sauvegardé")


# Créer l'application FastAPI
app = FastAPI(
    title="AI Leader Backend",
    description="Backend pour l'AI Leader Agent - Agent IA Autonome et Auto-Apprenant",
    version="1.0.0",
    lifespan=lifespan
)


# Configuration CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:3001",
        "http://localhost:3002",
        "https://*.preview.app.github.dev",
        "https://*.githubpreview.dev"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Health check
@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "AI Leader Backend API",
        "status": "operational",
        "version": "1.0.0"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    from backend.ai_leader_agent import ai_leader_agent
    
    return {
        "status": "healthy",
        "agent_phase": ai_leader_agent.current_phase.value,
        "apis_tracked": len(ai_leader_agent.api_learning_data),
        "capabilities_ready": sum(
            1 for c in ai_leader_agent.internal_capabilities.values()
            if c.ready_for_production
        ),
        "autonomy_percentage": ai_leader_agent.autonomy_percentage
    }


# Inclure les routes AI Leader
app.include_router(ai_leader_router, prefix="", tags=["AI Leader"])
app.include_router(examples_router, prefix="", tags=["Examples"])

# Inclure les routes d'intégration IA2GOOD (EduVerify + MedCare)
try:
    from backend.routes.ia2good_integration import router as ia2good_router
    app.include_router(ia2good_router, tags=["IA2GOOD Integration"])
    logger.info("✅ IA2GOOD Integration routes loaded - 6 endpoints")
except Exception as e:
    logger.warning(f"⚠️ IA2GOOD routes not available: {e}")

# Inclure les routes de traduction de langues
try:
    from backend.routes.language_translation import router as language_router
    app.include_router(language_router, tags=["Language Translation"])
    logger.info("✅ Language Translation routes loaded - 5 endpoints")
except Exception as e:
    logger.warning(f"⚠️ Language routes not available: {e}")

# Inclure les routes de génération d'images/texte/audio/vidéo/3D (import direct sans passer par backend.api.__init__)
try:
    import sys
    import importlib.util
    spec = importlib.util.spec_from_file_location("generation", "/workspaces/iacherie/backend/api/routes/generation.py")
    generation_module = importlib.util.module_from_spec(spec)
    sys.modules["generation"] = generation_module
    spec.loader.exec_module(generation_module)
    app.include_router(generation_module.router)
    logger.info("✅ AI Generation routes integrated - 6 endpoints (image/text/audio/video/code/3d)")
except Exception as e:
    logger.warning(f"⚠️ Generation routes not available: {e}")


# Gestionnaire d'erreurs global
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Gestionnaire d'erreurs global"""
    logger.error(f"Erreur non gérée: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "error": str(exc),
            "message": "Une erreur s'est produite"
        }
    )


if __name__ == "__main__":
    logger.info("🌟 Lancement du AI Leader Backend Server...")
    logger.info("📡 API disponible sur: http://localhost:8000")
    logger.info("📚 Documentation: http://localhost:8000/docs")
    
    uvicorn.run(
        "ai_leader_server:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
