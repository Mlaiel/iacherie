"""
Simplified Ainflue Platform Main Entry Point
Minimal working FastAPI application to test dependencies.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import os
import sys
from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# Create FastAPI app
app = FastAPI(
    title="Ainflue AI Platform",
    description="AI-Powered Content Protection & Monetization Platform",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Response models
class StatusResponse(BaseModel):
    status: str
    message: str
    version: str = "1.0.0"
    environment: str = "development"
    dependencies: dict = {}

class HealthResponse(BaseModel):
    healthy: bool
    status: str
    services: dict = {}

# Test dependency imports
def check_dependencies():
    """Check if all required dependencies are available"""
    deps = {}
    
    try:
        import fastapi
        deps["fastapi"] = fastapi.__version__
    except ImportError:
        deps["fastapi"] = "❌ Missing"
    
    try:
        import passlib
        deps["passlib"] = passlib.__version__
    except ImportError:
        deps["passlib"] = "❌ Missing"
    
    try:
        import pydantic_settings
        deps["pydantic-settings"] = "✓ Available"
    except ImportError:
        deps["pydantic-settings"] = "❌ Missing"
    
    try:
        import aiohttp
        deps["aiohttp"] = aiohttp.__version__
    except ImportError:
        deps["aiohttp"] = "❌ Missing"
    
    try:
        import cryptography
        deps["cryptography"] = cryptography.__version__
    except ImportError:
        deps["cryptography"] = "❌ Missing"
    
    try:
        import pytest_asyncio
        deps["pytest-asyncio"] = "✓ Available"
    except ImportError:
        deps["pytest-asyncio"] = "❌ Missing"
    
    return deps

# Basic routes
@app.get("/", response_model=StatusResponse)
async def root():
    """Root endpoint - API status with dependency check"""
    return StatusResponse(
        status="success",
        message="Ainflue AI Platform API is running successfully",
        dependencies=check_dependencies()
    )

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    return HealthResponse(
        healthy=True,
        status="healthy",
        services={
            "api": "healthy",
            "dependencies": "verified",
            "fastapi": "running"
        }
    )

@app.get("/dependencies")
async def dependencies_check():
    """Check all dependencies"""
    deps = check_dependencies()
    all_good = all("❌" not in str(v) for v in deps.values())
    
    return {
        "status": "success" if all_good else "partial",
        "all_dependencies_satisfied": all_good,
        "dependencies": deps,
        "missing_count": sum(1 for v in deps.values() if "❌" in str(v))
    }

def main():
    """Main entry point"""
    print("[INFO] Starting Simplified Ainflue AI Platform")
    print(f"[INFO] Environment: {os.getenv('ENVIRONMENT', 'development')}")
    print(f"[INFO] Debug mode: {os.getenv('DEBUG', 'true')}")
    
    # Check dependencies on startup
    deps = check_dependencies()
    print("\n[INFO] Dependency Check:")
    for name, status in deps.items():
        print(f"  - {name}: {status}")
    
    missing = [name for name, status in deps.items() if "❌" in str(status)]
    if missing:
        print(f"\n[WARNING] Missing dependencies: {', '.join(missing)}")
    else:
        print("\n[SUCCESS] ✅ All required dependencies are installed!")
    
    try:
        import uvicorn
        debug_mode = os.getenv("DEBUG", "true").lower() == "true"
        
        if debug_mode:
            # Use import string for reload
            uvicorn.run(
                "simple_main:app",
                host=os.getenv("HOST", "0.0.0.0"),
                port=int(os.getenv("PORT", "8000")),
                reload=True,
                log_level="info",
                access_log=True
            )
        else:
            # Use app object for production
            uvicorn.run(
                app,
                host=os.getenv("HOST", "0.0.0.0"),
                port=int(os.getenv("PORT", "8000")),
                log_level="info",
                access_log=True
            )
        
    except KeyboardInterrupt:
        print("[INFO] Platform stopped by user")
    except Exception as e:
        print(f"[ERROR] Platform startup failed: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()