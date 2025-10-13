"""FastAPI application for IA2GOOD module"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import sys
import os

# Add shared-services to path for IACherie AI integration
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../shared-services'))

from config import settings
from api.routes import cases, volunteers, matching, assignments, geolocation, analytics, auth, issues, events, campaigns, media, chat

# Import AI routes if available
try:
    from routes import ai_routes
    AI_ROUTES_AVAILABLE = True
except ImportError as e:
    AI_ROUTES_AVAILABLE = False
    print(f"⚠️ AI routes not available: {e}")

# Import IACherie AI integration
try:
    from ai_orchestrator import get_orchestrator, close_orchestrator
    from iacherie_ai_client import get_ai_client, close_ai_client
    AI_INTEGRATION_ENABLED = True
except ImportError as e:
    print(f"⚠️ AI Integration not available: {e}")
    AI_INTEGRATION_ENABLED = False

# Create FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Humanitarian Case Management & Volunteer Matching Platform",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json"
)

# CORS middleware - Allow all origins in development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins
    allow_credentials=False,  # Must be False when allow_origins=["*"]
    allow_methods=["*"],
    allow_headers=["*"],
)


# =============================================
# STARTUP/SHUTDOWN EVENTS - AI Integration
# =============================================

@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    print("🚀 Starting IA2GOOD Guardian API...")
    
    if AI_INTEGRATION_ENABLED:
        print("✅ IACherie AI Integration enabled")
        # Test connection to IACherie API
        try:
            orchestrator = get_orchestrator()
            health = await orchestrator.health_check()
            if health.get("status") == "healthy":
                print("✅ Connected to IACherie AI models successfully")
            else:
                print(f"⚠️ IACherie API health check failed: {health}")
        except Exception as e:
            print(f"❌ Failed to connect to IACherie AI: {e}")
    else:
        print("⚠️ Running without AI integration")


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    print("🛑 Shutting down IA2GOOD Guardian API...")
    
    if AI_INTEGRATION_ENABLED:
        try:
            await close_orchestrator()
            await close_ai_client()
            print("✅ AI clients closed successfully")
        except Exception as e:
            print(f"⚠️ Error closing AI clients: {e}")


# =============================================
# HEALTH CHECK ENDPOINTS
# =============================================

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    health_status = {
        "status": "healthy",
        "service": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "ai_integration": AI_INTEGRATION_ENABLED
    }
    
    # Check IACherie AI connection if enabled
    if AI_INTEGRATION_ENABLED:
        try:
            orchestrator = get_orchestrator()
            ai_health = await orchestrator.health_check()
            health_status["iacherie_ai"] = ai_health.get("status", "unknown")
        except Exception as e:
            health_status["iacherie_ai"] = "unhealthy"
            health_status["ai_error"] = str(e)
    
    return health_status


@app.get("/ready")
async def readiness_check():
    """Readiness check for Kubernetes"""
    return {
        "status": "ready",
        "service": settings.APP_NAME
    }


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": f"Welcome to {settings.APP_NAME} API",
        "version": settings.APP_VERSION,
        "docs": "/api/docs"
    }


# Include routers
app.include_router(auth.router, prefix="/api/guardian", tags=["Authentication"])
app.include_router(cases.router, prefix="/api/guardian", tags=["Cases"])
app.include_router(volunteers.router, prefix="/api/guardian", tags=["Volunteers"])
app.include_router(matching.router, prefix="/api/guardian", tags=["Matching"])
app.include_router(assignments.router, prefix="/api/guardian", tags=["Assignments"])
app.include_router(geolocation.router, prefix="/api/guardian", tags=["Geolocation"])
app.include_router(analytics.router, prefix="/api/guardian", tags=["Analytics"])
# Civic engagement modules
app.include_router(issues.router, prefix="/api/guardian", tags=["Issues"])
app.include_router(events.router, prefix="/api/guardian", tags=["Events"])
app.include_router(campaigns.router, prefix="/api/guardian", tags=["Campaigns"])
# Real-time communication
app.include_router(chat.router, prefix="/api/guardian", tags=["Chat"])
# Media and streaming
app.include_router(media.router, prefix="/api/guardian", tags=["Media"])

# AI Integration routes (IACherie models)
if AI_ROUTES_AVAILABLE:
    app.include_router(ai_routes.router, prefix="/api/guardian", tags=["AI Integration"])
    print("✅ AI routes included")


# Exception handlers
@app.exception_handler(404)
async def not_found_handler(request, exc):
    """Handle 404 errors"""
    return JSONResponse(
        status_code=404,
        content={"detail": "Resource not found"}
    )


@app.exception_handler(500)
async def internal_error_handler(request, exc):
    """Handle 500 errors"""
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8001,  # Guardian API port
        reload=settings.DEBUG
    )
