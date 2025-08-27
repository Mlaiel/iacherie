"""
Ainflue Platform Main API Application
FastAPI application with comprehensive security, monitoring, and performance optimization.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
from contextlib import asynccontextmanager
from typing import Dict, Any
import time

from fastapi import FastAPI, Request, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.openapi.utils import get_openapi
import uvicorn

from ..config import settings
from ..core.database import database_manager
from ..core.security import security_manager
from ..core.cache import cache_manager
from ..core.logging import logger_manager, logger
from ..ai_engine.vector_database import vector_database
from ..protection.monitoring import protection_monitor


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan management"""
    logger_manager.log_startup()
    
    try:
        # Initialize core systems
        await database_manager.initialize()
        await cache_manager.initialize(await database_manager.get_redis_client())
        await vector_database.initialize()
        await protection_monitor.initialize()
        
        # Create database indexes
        await database_manager.create_indexes()
        
        # Start background tasks
        monitoring_task = asyncio.create_task(protection_monitor.start_monitoring())
        
        logger.info("Ainflue platform started successfully")
        
        yield
        
        # Cleanup
        await protection_monitor.stop_monitoring()
        monitoring_task.cancel()
        await vector_database.save_all_indexes()
        await database_manager.close_connections()
        
        logger_manager.log_shutdown()
        
    except Exception as e:
        logger.error(f"Application startup failed: {str(e)}")
        raise


def create_application() -> FastAPI:
    """Create and configure FastAPI application"""
    
    app = FastAPI(
        title=settings.app.app_name,
        description=settings.app.app_description,
        version=settings.app.app_version,
        docs_url=settings.app.docs_url if settings.app.debug else None,
        redoc_url=settings.app.redoc_url if settings.app.debug else None,
        lifespan=lifespan
    )
    
    # Add middleware
    add_middleware(app)
    
    # Add routes
    add_routes(app)
    
    # Add exception handlers
    add_exception_handlers(app)
    
    return app


def add_middleware(app: FastAPI):
    """Add middleware to the application"""
    
    # CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.app.cors_origins,
        allow_credentials=True,
        allow_methods=settings.app.cors_methods,
        allow_headers=["*"],
    )
    
    # Compression middleware
    app.add_middleware(GZipMiddleware, minimum_size=1000)
    
    # Custom middleware
    @app.middleware("http")
    async def security_middleware(request: Request, call_next):
        """Security and monitoring middleware"""
        start_time = time.time()
        
        # Generate correlation ID
        correlation_id = logger_manager.generate_correlation_id()
        
        # Rate limiting check
        try:
            security_manager.check_rate_limit(request)
        except HTTPException as e:
            logger.warning(f"Rate limit exceeded for {request.client.host}")
            return JSONResponse(
                status_code=e.status_code,
                content={"detail": e.detail}
            )
        
        # Process request
        response = await call_next(request)
        
        # Log request
        process_time = time.time() - start_time
        logger.info(
            f"Request processed",
            extra={
                "method": request.method,
                "url": str(request.url),
                "status_code": response.status_code,
                "process_time": process_time,
                "client_ip": request.client.host
            }
        )
        
        # Add security headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Correlation-ID"] = correlation_id
        
        return response


def add_routes(app: FastAPI):
    """Add API routes"""
    from .routes import auth, content, protection, analytics, platform_integration
    
    # Include routers with prefix
    app.include_router(auth.router, prefix=f"{settings.app.api_prefix}/auth", tags=["authentication"])
    app.include_router(content.router, prefix=f"{settings.app.api_prefix}/content", tags=["content"])
    app.include_router(protection.router, prefix=f"{settings.app.api_prefix}/protection", tags=["protection"])
    app.include_router(analytics.router, prefix=f"{settings.app.api_prefix}/analytics", tags=["analytics"])
    app.include_router(platform_integration.router, prefix=f"{settings.app.api_prefix}/platforms", tags=["platforms"])
    
    # Health check endpoint
    @app.get("/health", include_in_schema=False)
    async def health_check():
        """Health check endpoint"""
        try:
            # Check database health
            db_health = await database_manager.get_health_status()
            
            # Check cache health
            cache_stats = cache_manager.get_stats()
            
            # Check vector database
            vector_stats = await vector_database.get_database_stats()
            
            health_status = {
                "status": "healthy",
                "timestamp": time.time(),
                "version": settings.app.app_version,
                "environment": settings.app.environment,
                "database": db_health,
                "cache": {
                    "hit_rate": cache_stats["hit_rate"],
                    "total_requests": cache_stats["total_requests"]
                },
                "vector_database": {
                    "total_content": vector_stats["total_content"],
                    "content_by_type": vector_stats["content_by_type"]
                }
            }
            
            # Determine overall health
            if not all(db_health.values()):
                health_status["status"] = "degraded"
            
            status_code = 200 if health_status["status"] == "healthy" else 503
            
            return JSONResponse(content=health_status, status_code=status_code)
            
        except Exception as e:
            logger.error(f"Health check failed: {str(e)}")
            return JSONResponse(
                content={
                    "status": "unhealthy",
                    "error": str(e),
                    "timestamp": time.time()
                },
                status_code=503
            )
    
    # Metrics endpoint for monitoring
    @app.get("/metrics", include_in_schema=False)
    async def metrics():
        """Prometheus-compatible metrics endpoint"""
        try:
            cache_stats = cache_manager.get_stats()
            vector_stats = await vector_database.get_database_stats()
            
            metrics_text = f"""
# HELP ainflue_cache_hit_rate Cache hit rate percentage
# TYPE ainflue_cache_hit_rate gauge
ainflue_cache_hit_rate {cache_stats['hits'] / (cache_stats['hits'] + cache_stats['misses']) * 100 if (cache_stats['hits'] + cache_stats['misses']) > 0 else 0}

# HELP ainflue_total_content Total content in vector database
# TYPE ainflue_total_content gauge
ainflue_total_content {vector_stats['total_content']}

# HELP ainflue_cache_operations_total Total cache operations
# TYPE ainflue_cache_operations_total counter
ainflue_cache_operations_total{{operation="hits"}} {cache_stats['hits']}
ainflue_cache_operations_total{{operation="misses"}} {cache_stats['misses']}
ainflue_cache_operations_total{{operation="sets"}} {cache_stats['sets']}
"""
            
            return Response(content=metrics_text.strip(), media_type="text/plain")
            
        except Exception as e:
            logger.error(f"Metrics endpoint failed: {str(e)}")
            raise HTTPException(status_code=500, detail="Metrics unavailable")


def add_exception_handlers(app: FastAPI):
    """Add global exception handlers"""
    
    @app.exception_handler(HTTPException)
    async def http_exception_handler(request: Request, exc: HTTPException):
        """Handle HTTP exceptions"""
        logger.warning(f"HTTP exception: {exc.status_code} - {exc.detail}")
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "detail": exc.detail,
                "status_code": exc.status_code,
                "timestamp": time.time()
            }
        )
    
    @app.exception_handler(Exception)
    async def general_exception_handler(request: Request, exc: Exception):
        """Handle general exceptions"""
        logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={
                "detail": "Internal server error",
                "status_code": 500,
                "timestamp": time.time()
            }
        )


def custom_openapi(app: FastAPI):
    """Customize OpenAPI schema"""
    if app.openapi_schema:
        return app.openapi_schema
    
    openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
    )
    
    # Add security schemes
    openapi_schema["components"]["securitySchemes"] = {
        "BearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
        }
    }
    
    # Add global security requirement
    for path in openapi_schema["paths"]:
        for method in openapi_schema["paths"][path]:
            if method not in ["options"]:
                openapi_schema["paths"][path][method]["security"] = [
                    {"BearerAuth": []}
                ]
    
    app.openapi_schema = openapi_schema
    return app.openapi_schema


# Create the application instance
app = create_application()

# Set custom OpenAPI
app.openapi = lambda: custom_openapi(app)


if __name__ == "__main__":
    # Development server
    uvicorn.run(
        "api.main:app",
        host=settings.app.host,
        port=settings.app.port,
        reload=settings.app.debug,
        log_level=settings.monitoring.log_level.lower()
    )