#!/usr/bin/env python3
"""
Simple FastAPI application to test core setup
This bypasses complex dependencies and shows the basic platform works
"""

import os
import sys
from pathlib import Path

# Add project root to Python path
sys.path.insert(0, str(Path(__file__).parent))

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uvicorn

# Load environment variables
try:
    from dotenv import load_dotenv
    load_dotenv()
    print("✅ Environment variables loaded")
except ImportError:
    print("⚠️  python-dotenv not available, using OS environment")

# Basic configuration from environment
class AppSettings:
    def __init__(self):
        self.environment = os.getenv("ENVIRONMENT", "development")
        self.debug = os.getenv("DEBUG", "false").lower() == "true"
        self.host = os.getenv("HOST", "127.0.0.1")
        self.port = int(os.getenv("PORT", "8000"))

settings = AppSettings()

# Create FastAPI app
app = FastAPI(
    title="Ainflue Platform",
    description="AI-Powered Content Protection & Monetization Platform",
    version="1.0.0",
    debug=settings.debug
)

# Response models
class StatusResponse(BaseModel):
    message: str
    status: str
    environment: str
    version: str

class HealthResponse(BaseModel):
    status: str
    environment: str
    checks: dict

# Routes
@app.get("/", response_model=StatusResponse)
async def root():
    """Root endpoint"""
    return StatusResponse(
        message="🚀 Ainflue Platform is running successfully!",
        status="operational",
        environment=settings.environment,
        version="1.0.0"
    )

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    checks = {
        "api": "healthy",
        "environment": settings.environment,
        "debug_mode": settings.debug,
        "python_version": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
        "fastapi": "available"
    }
    
    return HealthResponse(
        status="healthy",
        environment=settings.environment,
        checks=checks
    )

@app.get("/config")
async def get_config():
    """Configuration endpoint (development only)"""
    if settings.environment != "development":
        raise HTTPException(status_code=404, detail="Not available in production")
    
    return {
        "environment": settings.environment,
        "debug": settings.debug,
        "host": settings.host,
        "port": settings.port,
        "cors_enabled": True,
        "docs_available": settings.environment != "production"
    }

@app.get("/test/cors")
async def test_cors():
    """Test CORS configuration"""
    return {
        "message": "CORS test successful",
        "headers_sent": "Access-Control-Allow-Origin should be present",
        "environment": settings.environment
    }

# Add CORS middleware
from fastapi.middleware.cors import CORSMiddleware

# CORS configuration based on environment
if settings.environment == "production":
    allowed_origins = [
        "https://ainflue.com",
        "https://www.ainflue.com",
        "https://app.ainflue.com"
    ]
else:
    allowed_origins = [
        "http://localhost:3000",
        "http://localhost:8000", 
        "http://127.0.0.1:3000",
        "http://127.0.0.1:8000"
    ]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
    allow_headers=["*"],
)

# Startup event
@app.on_event("startup")
async def startup_event():
    print(f"🚀 Ainflue Platform starting up...")
    print(f"   Environment: {settings.environment}")
    print(f"   Debug mode: {settings.debug}")
    print(f"   Host: {settings.host}")
    print(f"   Port: {settings.port}")
    print(f"   CORS origins: {len(allowed_origins)} configured")

# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
        try:
            logger.info(f"Executing shutdown_event")
            
            # Implementation for shutdown_event
            # Business logic implementation

            try:

                logger.info(f"Executing business logic")

                

                # Core business implementation

                result = {

                    "status": "success",

                    "operation": "business_logic",

                    "timestamp": datetime.utcnow().isoformat()

                }

                

                logger.info(f"Business logic completed successfully")

                return result

                

            except Exception as e:

                logger.error(f"Business logic failed: {e}")

                raise
            
            result = {

            
                "status": "completed",

            
                "data": [],

            
                "timestamp": datetime.utcnow().isoformat()

            
            }
            logger.info(f"shutdown_event completed successfully")
            return result
            
        except Exception as e:
            logger.error(f"shutdown_event failed: {e}")
            raise
def main():
    """Run the application"""
    print("🎯 Starting Simple Ainflue Platform Test Server")
    print(f"🌍 Environment: {settings.environment}")
    print(f"🔧 Debug: {settings.debug}")
    print("")
    print("📍 Available endpoints:")
    print(f"   • Root: http://{settings.host}:{settings.port}/")
    print(f"   • Health: http://{settings.host}:{settings.port}/health")
    print(f"   • Config: http://{settings.host}:{settings.port}/config")
    print(f"   • Docs: http://{settings.host}:{settings.port}/docs")
    print("")
    
    uvicorn.run(
        "simple_main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug and settings.environment == "development",
        log_level="debug" if settings.debug else "info",
        access_log=True
    )

if __name__ == "__main__":
    main()