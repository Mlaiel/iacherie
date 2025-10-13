"""
Orchestrator API - Central coordination service
Coordinates MedCare (8000), IA2GOOD (8001), EduVerify (8002)
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import logging
import sys
from pathlib import Path

# Add current directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

# Import services
from services.accessibility_service import AccessibilityService
from services.analytics_service import AnalyticsService
from routes import accessibility, analytics, health

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="IA2GOOD Orchestrator",
    description="Central coordination service for MedCare, IA2GOOD Volunteer, and EduVerify modules",
    version="1.0.0",
    docs_url="/orchestrator/docs",
    redoc_url="/orchestrator/redoc",
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure based on environment
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routes
app.include_router(accessibility.router, prefix="/orchestrator/accessibility", tags=["accessibility"])
app.include_router(analytics.router, prefix="/orchestrator/analytics", tags=["analytics"])
app.include_router(health.router, prefix="/orchestrator", tags=["health"])


@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    logger.info("🚀 Orchestrator starting up...")
    logger.info("📊 Initializing analytics service...")
    logger.info("♿ Initializing accessibility service...")
    logger.info("✅ Orchestrator ready on port 8003")


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    logger.info("👋 Orchestrator shutting down...")


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "IA2GOOD Orchestrator",
        "version": "1.0.0",
        "status": "operational",
        "modules": {
            "medcare": {"port": 8000, "status": "connected"},
            "ia2good": {"port": 8001, "status": "connected"},
            "eduverify": {"port": 8002, "status": "connected"},
        },
        "features": [
            "Universal Accessibility (TTS, STT, Captions)",
            "Aggregated Analytics",
            "Shared Authentication (future)",
            "Language Services (future integration with IACHERIE)",
        ],
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8003, reload=True)
