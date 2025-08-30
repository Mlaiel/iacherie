"""
FastAPI Application Entry Point
Simple and functional API for the Ainflue platform.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import os
import sys
from pathlib import Path

# Add project root to Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
import uvicorn

# Create FastAPI app
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

# Health endpoint
@app.get("/health")
async def health():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0",
        "service": "ainflue-api"
    }

# Root endpoint
@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "Welcome to Ainflue AI Platform API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health"
    }

# API endpoints placeholder
@app.get("/api/v1/status")
async def api_status():
    """API status endpoint"""
    return {
        "api_status": "running",
        "timestamp": datetime.utcnow().isoformat(),
        "endpoints": ["/health", "/api/v1/status"]
    }

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port, log_level="info", reload=os.getenv("DEV_MODE", "0") == "1")
