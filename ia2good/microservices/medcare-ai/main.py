"""
MedCare-AI Microservice
Main FastAPI application for telemedicine and AI diagnostic service
"""
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging
import sys
import os

# Add shared-services to path for IACherie AI integration
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../shared-services'))

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

app = FastAPI(
    title="MedCare-AI Service",
    description="AI-powered telemedicine and diagnostic service for rural healthcare",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Import routes
try:
    from api.routes import (
        symptoms, diagnosis, consultations, prescriptions, image_analysis,
        medical_documents, community, solidarity, webrtc, ai_learning_routes
    )
    
    # Original routes
    app.include_router(symptoms.router)
    app.include_router(diagnosis.router)
    app.include_router(consultations.router)
    app.include_router(prescriptions.router)
    app.include_router(image_analysis.router)
    
    # New community features routes
    app.include_router(medical_documents.router)
    app.include_router(community.router)
    app.include_router(solidarity.router)
    
    # WebRTC signaling routes
    app.include_router(webrtc.router)
    
    # AI Self-Learning routes
    app.include_router(ai_learning_routes.router, prefix="/api/medcare", tags=["AI Self-Learning"])
    
    logger.info("All routes loaded successfully")
except ImportError as e:
    logger.warning(f"Some routes could not be loaded: {e}")

# Import AI routes if available (IACherie integration)
try:
    from routes import ai_routes
    app.include_router(ai_routes.router, prefix="/api/medcare", tags=["AI Integration"])
    AI_ROUTES_AVAILABLE = True
    logger.info("✅ AI routes included")
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

@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "service": "MedCare-AI",
        "status": "healthy",
        "version": "1.0.0"
    }

@app.get("/health")
async def health_check():
    """Detailed health check"""
    health_status = {
        "status": "healthy",
        "service": "medcare-ai",
        "checks": {
            "api": "ok",
            "database": "ok",  # TODO: Add real DB check
            "ml_models": "ok"  # TODO: Add real ML model check
        }
    }
    
    # Check IACherie AI integration
    if AI_INTEGRATION_ENABLED:
        try:
            ai_client = get_ai_client()
            iacherie_health = await ai_client.health_check()
            health_status["checks"]["iacherie_ai"] = "ok" if iacherie_health.get("status") == "healthy" else "degraded"
        except Exception as e:
            health_status["checks"]["iacherie_ai"] = f"error: {str(e)}"
    else:
        health_status["checks"]["iacherie_ai"] = "not_configured"
    
    return health_status

@app.get("/ready")
async def readiness_check():
    """Readiness check endpoint for Kubernetes"""
    return {
        "status": "ready",
        "service": "medcare-ai"
    }

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler"""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "detail": "Internal server error",
            "path": str(request.url)
        }
    )

@app.on_event("startup")
async def startup_event():
    """Startup event handler"""
    logger.info("Starting MedCare-AI microservice")
    
    # Start AI Self-Learning Service
    try:
        from services import start_continuous_learning
        await start_continuous_learning()
        logger.info("✅ AI Self-Learning Service started (Few-Shot Learning for medical diagnostics)")
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

@app.on_event("shutdown")
async def shutdown_event():
    """Shutdown event handler"""
    logger.info("Shutting down MedCare-AI microservice")
    
    # Close IACherie AI integration
    if AI_INTEGRATION_ENABLED:
        try:
            await close_orchestrator()
            await close_ai_client()
            logger.info("✅ IACherie AI integration closed")
        except Exception as e:
            logger.error(f"❌ Error closing AI integration: {e}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8003)  # MedCare API port
