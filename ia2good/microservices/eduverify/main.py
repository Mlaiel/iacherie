"""
EduVerify Main Application
FastAPI application for educational AI platform
"""

import os
import sys
import logging

# CRITICAL: Configure Python paths BEFORE any other imports
# Order matters: EduVerify local modules MUST come before workspace modules
eduverify_root = os.path.abspath(os.path.dirname(__file__))
root_workspace = os.path.abspath(os.path.join(eduverify_root, '../../../..'))
shared_services_path = os.path.abspath(os.path.join(eduverify_root, '../../shared-services'))

# Step 1: Remove any existing paths to avoid duplicates
for path in [eduverify_root, shared_services_path, root_workspace]:
    while path in sys.path:
        sys.path.remove(path)

# Step 2: Add paths in correct priority order
# Priority 1: EduVerify local modules (database, config, utils, api)
sys.path.insert(0, eduverify_root)

# Priority 2: Shared services (common utilities)
sys.path.insert(1, shared_services_path)

# Priority 3: Workspace root (backend, protection, etc.) - LAST to avoid conflicts
sys.path.append(root_workspace)

# Now safe to import FastAPI and other dependencies
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from config import settings

# ✅ CORRECTION: Forcer IACHERIE_API_URL depuis settings AVANT l'import du client
os.environ["IACHERIE_API_URL"] = settings.IACHERIE_API_URL

# Configure logging
logging.basicConfig(
    level=logging.INFO if not settings.DEBUG else logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="""
    EduVerify: Plateforme éducative IA interactive
    
    ## Fonctionnalités
    
    * **Content Processing**: Upload multi-format (PDF, vidéo, audio, URL)
    * **Quiz Generation**: Génération automatique avec IA (GPT-4, Claude, Gemini)
    * **Fact-Checking**: Vérification faits temps réel (>92% précision)
    * **100+ Langues**: Support multilingue avec détection dialectes
    * **Live Lecture**: Capture cours en direct (<3s latency)
    * **Explanations**: Explications professionnelles niveau universitaire
    * **Educational Chatroom**: Chat temps réel avec accessibilité intégrée
    
    ## Modules
    
    * **Content**: `/eduverify/content/*` - Gestion contenu éducatif
    * **Quizzes**: `/eduverify/quizzes/*` - Génération et gestion quiz
    * **Fact-Check**: `/eduverify/fact-check/*` - Vérification faits
    * **Explanations**: `/eduverify/explanations/*` - Explications professionnelles
    * **Analytics**: `/eduverify/analytics/*` - Statistiques apprentissage
    * **Chatroom**: `/eduverify/chatrooms/*` + WebSocket - Chat éducatif accessible
    
    ## Accessibilité ♿
    
    * **Pour Aveugles**: TTS, screen readers, audio descriptions
    * **Pour Sourds**: Captions automatiques, alertes visuelles, transcriptions temps réel
    * **Orchestrateur**: Service central d'accessibilité sur port 8003
    """,
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # TODO: Configure properly for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routers
from api.routes import (
    content_router,
    quizzes_router,
    fact_checking_router,
    explanations_router,
    analytics_router,
    chatroom_router,
)

# Import AI Learning routes
try:
    from api.routes import ai_learning_routes
    AI_LEARNING_AVAILABLE = True
except ImportError:
    AI_LEARNING_AVAILABLE = False
    logger.warning("⚠️ AI Learning routes not available")

# Import AI routes if available (IACherie integration)
try:
    from routes import ai_routes
    AI_ROUTES_AVAILABLE = True
except ImportError as e:
    AI_ROUTES_AVAILABLE = False
    logger.warning(f"⚠️ AI routes not available: {e}")

# Import IACherie AI integration
try:
    from ai_orchestrator import get_orchestrator, close_orchestrator
    from iacherie_ai_client import get_ai_client, close_ai_client
    AI_INTEGRATION_ENABLED = True
except ImportError as e:
    logger.warning(f"⚠️ AI Integration not available: {e}")
    AI_INTEGRATION_ENABLED = False

app.include_router(content_router)
app.include_router(quizzes_router)
app.include_router(fact_checking_router)
app.include_router(explanations_router)
app.include_router(analytics_router)
app.include_router(chatroom_router)

# AI Self-Learning routes
if AI_LEARNING_AVAILABLE:
    app.include_router(ai_learning_routes.router, prefix="/api/eduverify", tags=["AI Self-Learning"])
    logger.info("✅ AI Learning routes included")

# AI Integration routes (IACherie models)
if AI_ROUTES_AVAILABLE:
    app.include_router(ai_routes.router, prefix="/api/eduverify", tags=["AI Integration"])
    logger.info("✅ AI routes included")


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "online",
        "docs": "/docs",
        "features": [
            "Multi-format content processing",
            "AI-powered quiz generation",
            "Real-time fact-checking",
            "100+ languages support",
            "Live lecture capture",
            "Professional explanations",
            "Educational chatroom with accessibility (TTS, captions, visual alerts)"
        ]
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    health_status = {
        "status": "healthy",
        "service": settings.APP_NAME,
        "version": settings.APP_VERSION
    }
    
    # Check IACherie AI integration
    if AI_INTEGRATION_ENABLED:
        try:
            ai_client = get_ai_client()
            iacherie_health = await ai_client.health_check()
            health_status["iacherie_ai"] = "ok" if iacherie_health.get("status") == "healthy" else "degraded"
        except Exception as e:
            health_status["iacherie_ai"] = f"error: {str(e)}"
    
    return health_status


@app.get("/ready")
async def readiness_check():
    """Readiness check endpoint for Kubernetes"""
    return {
        "status": "ready",
        "service": settings.APP_NAME
    }


@app.on_event("startup")
async def startup_event():
    """Startup event handler"""
    logger.info(f"Starting {settings.APP_NAME} v{settings.APP_VERSION}")
    
    # Start AI Self-Learning Service
    try:
        from services import start_continuous_learning
        await start_continuous_learning()
        logger.info("✅ AI Self-Learning Service started (Few-Shot Learning for educational content)")
    except Exception as e:
        logger.error(f"❌ AI Learning Service failed: {e}")
    
    # Initialize IACherie AI integration
    if AI_INTEGRATION_ENABLED:
        try:
            orchestrator = get_orchestrator()
            ai_client = get_ai_client()
            health = await ai_client.health_check()
            if health.get("status") == "healthy":
                logger.info("✅ IACherie AI integration healthy")
            else:
                logger.warning("⚠️ IACherie AI integration unhealthy")
        except Exception as e:
            logger.error(f"❌ IACherie AI integration failed: {e}")
    
    # Initialize database - create all tables if not exist
    try:
        from eduverify_database import init_db
        init_db()
        logger.info("✅ Database initialized successfully")
    except Exception as e:
        logger.error(f"❌ Database initialization failed: {e}")
        raise
    
    logger.info("EduVerify microservice is ready")
    logger.info(f"📚 Content upload: /eduverify/content/upload")
    logger.info(f"🎯 Quiz generation: /eduverify/quizzes/generate")
    logger.info(f"✓ Fact-checking: /eduverify/fact-check/verify")
    logger.info(f"💬 Chatroom WebSocket: ws://localhost:8002/ws/chatroom")


@app.on_event("shutdown")
async def shutdown_event():
    """Shutdown event handler"""
    logger.info("Shutting down EduVerify microservice")
    
    # Close IACherie AI integration
    if AI_INTEGRATION_ENABLED:
        try:
            await close_orchestrator()
            await close_ai_client()
            logger.info("✅ IACherie AI integration closed")
        except Exception as e:
            logger.error(f"❌ Error closing AI integration: {e}")
    
    # Close database connections gracefully
    from eduverify_database import engine
    engine.dispose()
    logger.info("✅ Database connections closed")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8002,
        reload=settings.DEBUG
    )
