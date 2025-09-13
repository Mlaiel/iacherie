"""
Core Service Entry Point - Distribution Core Hub
==============================================

FastAPI service for core utilities and foundational services.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

from fastapi import APIRouter, Depends, HTTPException
from typing import Dict, List, Any, Optional
import logging

from . import (
    ABTestingEngine,
    ContentSecurity,
    CrossPlatformSync,
    FormatAdapter
)

logger = logging.getLogger(__name__)

# Core router
core_router = APIRouter(prefix="/core", tags=["core"])

# Initialize core services
ab_testing = ABTestingEngine()
content_security = ContentSecurity()
platform_sync = CrossPlatformSync()
format_adapter = FormatAdapter()

@core_router.get("/health")
async def core_health():
    """Core service health check"""
    return {"status": "healthy", "service": "core"}

@core_router.get("/utilities")
async def get_available_utilities():
    """Get list of available core utilities"""
    return {
        "ab_testing": "A/B Testing Engine",
        "content_security": "Content Security System", 
        "platform_sync": "Cross-Platform Synchronization",
        "format_adapter": "Format Adaptation Engine"
    }

# Export router for main application
__all__ = ["core_router"]