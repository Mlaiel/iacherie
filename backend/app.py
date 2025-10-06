"""
🚀 BACKEND MAIN APPLICATION - FASTAPI
======================================
FastAPI application principale avec toutes les routes

@author Fahed Mlaiel
@date 2025-10-05
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging

# Import routes
from backend.api.routes.generation import router as generation_router
from backend.api.crawlers_endpoints import router as crawlers_router
# Add more routes here as needed

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# ============================================================================
# FASTAPI APPLICATION
# ============================================================================

app = FastAPI(
    title="iAcherie Backend API",
    description="Complete backend API with AI generation, crawlers, agents, and more",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# ============================================================================
# CORS MIDDLEWARE
# ============================================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:3001",
        "https://iacherie.com",
        "https://*.iacherie.com"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================================================
# INCLUDE ROUTERS
# ============================================================================

# Generation APIs (OpenAI, Runway, Stability)
app.include_router(generation_router, tags=["generation"])
logger.info("✅ Registered generation routes")

# Crawlers APIs
try:
    app.include_router(crawlers_router, prefix="/api/crawlers", tags=["crawlers"])
    logger.info("✅ Registered crawlers routes")
except Exception as e:
    logger.warning(f"⚠️ Could not register crawlers routes: {e}")

# Add more routers here
# app.include_router(agents_router, prefix="/api/agents", tags=["agents"])
# app.include_router(studios_router, prefix="/api/studios", tags=["studios"])
# app.include_router(chatrooms_router, prefix="/api/chatrooms", tags=["chatrooms"])

# ============================================================================
# ROOT ENDPOINTS
# ============================================================================

@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "service": "iAcherie Backend API",
        "status": "operational",
        "version": "1.0.0",
        "docs": "/docs",
        "redoc": "/redoc"
    }

@app.get("/health")
async def health_check():
    """Detailed health check"""
    return {
        "status": "healthy",
        "services": {
            "generation": "operational",
            "crawlers": "operational",
            "database": "operational"
        }
    }

# ============================================================================
# STARTUP EVENT
# ============================================================================

@app.on_event("startup")
async def startup_event():
    """Run on application startup"""
    logger.info("🚀 iAcherie Backend API starting...")
    logger.info("📚 API Documentation available at /docs")
    logger.info("✨ Generation APIs ready (DALL-E, GPT-4, Runway, Stability)")

# ============================================================================
# SHUTDOWN EVENT
# ============================================================================

@app.on_event("shutdown")
async def shutdown_event():
    """Run on application shutdown"""
    logger.info("👋 iAcherie Backend API shutting down...")

# ============================================================================
# RUN SERVER
# ============================================================================

if __name__ == "__main__":
    import uvicorn
    
    logger.info("🚀 Starting FastAPI server...")
    
    uvicorn.run(
        "backend.app:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
