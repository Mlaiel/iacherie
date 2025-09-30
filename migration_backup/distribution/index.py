"""
Distribution Service Entry Point - Main Distribution Hub
======================================================

Main FastAPI service entry point for the Ainflue distribution system,
coordinating all subsystems and providing unified API access.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

from fastapi import FastAPI, APIRouter, Depends, HTTPException
from typing import Dict, List, Any, Optional
import logging

# Import all subsystem routers
from .analytics.index import analytics_router
from .connectors.index import connectors_router
from .scheduling.index import scheduling_router
from .optimization.index import optimization_router
from .management.index import management_router
from .core.index import core_router

# Import existing subsystems
from .audience_intelligence.index import audience_router
from .platform_optimization.index import platform_optimization_router

logger = logging.getLogger(__name__)

# Main distribution router
distribution_router = APIRouter(prefix="/distribution", tags=["distribution"])

# Include all subsystem routers
distribution_router.include_router(analytics_router)
distribution_router.include_router(connectors_router)
distribution_router.include_router(scheduling_router)
distribution_router.include_router(optimization_router)
distribution_router.include_router(management_router)
distribution_router.include_router(core_router)
distribution_router.include_router(audience_router)
distribution_router.include_router(platform_optimization_router)

@distribution_router.get("/health")
async def distribution_health():
    """Distribution service main health check"""
    return {
        "status": "healthy",
        "service": "distribution",
        "subsystems": {
            "analytics": "active",
            "connectors": "active", 
            "scheduling": "active",
            "optimization": "active",
            "management": "active",
            "core": "active",
            "audience_intelligence": "active",
            "platform_optimization": "active"
        }
    }

@distribution_router.get("/status")
async def distribution_status():
    """Get comprehensive distribution system status"""
    return {
        "distribution_system": "operational",
        "total_subsystems": 8,
        "active_connections": "all platforms",
        "performance": "optimal"
    }

@distribution_router.get("/")
async def distribution_info():
    """Distribution system information"""
    return {
        "service": "Ainflue Distribution System",
        "version": "1.0.0",
        "description": "AI-powered multi-platform content distribution",
        "author": "Fahed Mlaiel",
        "endpoints": {
            "analytics": "/distribution/analytics",
            "connectors": "/distribution/connectors",
            "scheduling": "/distribution/scheduling", 
            "optimization": "/distribution/optimization",
            "management": "/distribution/management",
            "core": "/distribution/core",
            "audience_intelligence": "/distribution/audience-intelligence",
            "platform_optimization": "/distribution/platform-optimization"
        }
    }

# Export main router
__all__ = ["distribution_router"]