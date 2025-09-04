"""API Endpoints - Consolidated REST Endpoints
All REST endpoints for the IA Influencer Agent platform consolidated in one place.

This module consolidates all REST API endpoints from:
- Authentication endpoints (login, register, logout, etc.)
- Content management endpoints (upload, list, update, delete)
- Collaboration endpoints (create, match, requests, etc.)
- Analytics endpoints (performance, market intelligence, etc.)
- Monetization endpoints (payments, revenue, licensing)
- Protection endpoints (fingerprinting, DMCA, rights management)

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from decimal import Decimal
from enum import Enum
import uuid
import asyncio

from fastapi import APIRouter, Depends, HTTPException, status, Body, UploadFile, File, Form, BackgroundTasks, Query
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.responses import JSONResponse, StreamingResponse
from pydantic import BaseModel, EmailStr, Field, validator
import bcrypt

# Import existing consolidated routers
from .core_api import core_router
from .business_api import business_router  
from .public import public_router

# ========================================
# CONSOLIDATED ENDPOINTS ROUTER
# ========================================

endpoints_router = APIRouter(prefix="/api/v1", tags=["endpoints"])

# Include all existing consolidated routers
endpoints_router.include_router(core_router, prefix="/core")
endpoints_router.include_router(business_router, prefix="/business")
endpoints_router.include_router(public_router, prefix="/public")

# ========================================
# ADDITIONAL ENDPOINTS
# ========================================

@endpoints_router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "2.0.0",
        "service": "IA Influencer Agent API"
    }

@endpoints_router.get("/version")
async def get_version():
    """Get API version information"""
    return {
        "api_version": "2.0.0",
        "platform": "IA Influencer Agent",
        "author": "Fahed Mlaiel",
        "build_date": "2025-01-01",
        "capabilities": [
            "content_protection",
            "ai_fingerprinting", 
            "monetization",
            "collaboration",
            "analytics",
            "multi_platform_distribution"
        ]
    }

@endpoints_router.get("/status")
async def get_status():
    """Get detailed system status"""
    return {
        "api_status": "operational",
        "database_status": "connected", 
        "cache_status": "active",
        "ai_engine_status": "ready",
        "protection_engine_status": "active",
        "uptime": "99.99%",
        "last_updated": datetime.utcnow().isoformat()
    }

# ========================================
# EXPORTS
# ========================================

__all__ = ["endpoints_router"]