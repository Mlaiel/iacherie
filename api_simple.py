"""
Simple API application mock for testing without FastAPI dependency

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import json
from datetime import datetime


class MockApp:
    """Mock FastAPI application for testing"""
    
    def __init__(self, title="Ainflue AI Platform API", version="1.0.0"):
        self.title = title
        self.version = version
        self.routes = []
    
    def get(self, path):
        """Mock GET route decorator"""
        def decorator(func):
            self.routes.append({"method": "GET", "path": path, "handler": func})
            return func
        return decorator
    
    def health_check(self):
        """Health check endpoint"""
        return {
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "version": self.version,
            "service": "ainflue-api"
        }
    
    def api_info(self):
        """API info endpoint"""
        return {
            "message": f"Welcome to {self.title}",
            "version": self.version,
            "endpoints": [route["path"] for route in self.routes]
        }


# Try to import FastAPI, fall back to mock
try:
    from fastapi import FastAPI
    from fastapi.middleware.cors import CORSMiddleware
    from datetime import datetime
    
    # Create real FastAPI app
    app = FastAPI(
        title="Ainflue AI Platform API",
        version="1.0.0",
        description="AI-Powered Content Protection & Monetization Platform"
    )
    
    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    @app.get("/health")
    async def health():
        """Health check endpoint"""
        return {
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "version": "1.0.0",
            "service": "ainflue-api"
        }
    
    @app.get("/")
    async def root():
        """Root endpoint with API information"""
        return {
            "message": "Welcome to Ainflue AI Platform API",
            "version": "1.0.0",
            "docs": "/docs",
            "health": "/health"
        }
    
    @app.get("/api/v1/status")
    async def api_status():
        """API status endpoint"""
        return {
            "api_status": "running",
            "timestamp": datetime.utcnow().isoformat(),
            "endpoints": ["/health", "/api/v1/status"]
        }
    
    print("✅ Using FastAPI application")

except ImportError:
    # Create mock app
    app = MockApp()
    
    # Add mock routes
    app.get("/health")(app.health_check)
    app.get("/")(app.api_info)
    
    print("⚠️ Using mock API application (FastAPI not available)")


# Export the app
__all__ = ['app']