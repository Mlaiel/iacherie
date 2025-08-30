"""
Ainflue Platform API Main Module
FastAPI application configuration and routes.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import os
import sys
from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

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

class HealthResponse(BaseModel):
    healthy: bool
    status: str
    services: dict = {}

# Basic routes
@app.get("/", response_model=StatusResponse)
async def root():
    """Root endpoint - API status"""
    return StatusResponse(
        status="success",
        message="Ainflue AI Platform API is running"
    )

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    return HealthResponse(
        healthy=True,
        status="healthy",
        services={
            "api": "healthy",
            "database": "unknown",
            "cache": "unknown"
        }
    )

@app.get("/api/status", response_model=StatusResponse)
async def api_status():
    """API status endpoint"""
    return StatusResponse(
        status="success",
        message="Ainflue API v1.0.0 is operational"
    )

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(
        app, 
        host="0.0.0.0", 
        port=port, 
        log_level="info", 
        reload=os.getenv("DEV_MODE", "0") == "1"
    )
