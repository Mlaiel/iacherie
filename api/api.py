"""
API Main Module
Centralizes all API routes and configurations
"""

from fastapi import APIRouter

# Import routes with error handling
try:
    from .routes.content_routes import router as content_router
    from .routes.agent_routes import router as agent_router
    from .routes.crawler_routes import router as crawler_router
    from .routes.analytics_routes import router as analytics_router
    from .routes.auth_routes import router as auth_router
    from .routes.violation_routes import router as violation_router
    from .routes.monitoring_routes import router as monitoring_router
    
    # Create main API router
    api_router = APIRouter(prefix="/api/v1")
    
    # Include all route modules
    api_router.include_router(content_router, prefix="/content", tags=["content"])
    api_router.include_router(agent_router, prefix="/agents", tags=["agents"])
    api_router.include_router(crawler_router, prefix="/crawlers", tags=["crawlers"])
    api_router.include_router(analytics_router, prefix="/analytics", tags=["analytics"])
    api_router.include_router(auth_router, prefix="/auth", tags=["authentication"])
    api_router.include_router(violation_router, prefix="/violations", tags=["violations"])
    api_router.include_router(monitoring_router, prefix="/monitoring", tags=["monitoring"])
    
except ImportError as e:
    print(f"Warning: Could not import all routes: {e}")
    # Create minimal fallback router
    api_router = APIRouter(prefix="/api/v1")
    
    @api_router.get("/health")
    async def health_check():
        return {"status": "ok", "message": "API is running"}

__all__ = ["api_router"]
