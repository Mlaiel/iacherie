"""
Main API application for Ainflue AI Platform
Creates and configures the FastAPI application with basic endpoints.
"""

from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
import logging

# Create FastAPI app
app = FastAPI(
    title="Ainflue AI Platform",
    description="AI-Powered Content Protection & Monetization Platform",
    version="1.0.0"
)

logger = logging.getLogger(__name__)

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "message": "Ainflue API is running"}

@app.get("/")
async def root():
    """Root endpoint"""
    return {"message": "Welcome to Ainflue AI Platform API"}

# Add exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )
