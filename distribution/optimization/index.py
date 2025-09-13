"""
Optimization Service Entry Point - Distribution Optimization Hub
==============================================================

FastAPI service for optimization engines and intelligent distribution systems.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

from fastapi import APIRouter, Depends, HTTPException
from typing import Dict, List, Any, Optional
import logging

from . import (
    AITimingOptimizer,
    HashtagOptimizer,
    QueueIntelligence,
    DistributionIntelligence
)

logger = logging.getLogger(__name__)

# Optimization router
optimization_router = APIRouter(prefix="/optimization", tags=["optimization"])

# Initialize optimization services
timing_optimizer = AITimingOptimizer()
hashtag_optimizer = HashtagOptimizer()
queue_intelligence = QueueIntelligence()
distribution_intelligence = DistributionIntelligence()

@optimization_router.get("/health")
async def optimization_health():
    """Optimization service health check"""
    return {"status": "healthy", "service": "optimization"}

@optimization_router.get("/recommendations")
async def get_optimization_recommendations():
    """Get AI-powered optimization recommendations"""
    return await distribution_intelligence.get_recommendations()

# Export router for main application
__all__ = ["optimization_router"]