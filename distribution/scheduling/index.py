"""
Scheduling Service Entry Point - Content Scheduling Hub
=====================================================

FastAPI service for scheduling and timing optimization systems.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

from fastapi import APIRouter, Depends, HTTPException
from typing import Dict, List, Any, Optional
import logging

from . import (
    BulkScheduler,
    EventBasedScheduler,
    PublicationScheduler,
    SeasonalScheduler,
    TimezoneAwareScheduler
)

logger = logging.getLogger(__name__)

# Scheduling router
scheduling_router = APIRouter(prefix="/scheduling", tags=["scheduling"])

# Initialize scheduling services
bulk_scheduler = BulkScheduler()
event_scheduler = EventBasedScheduler()
publication_scheduler = PublicationScheduler()
seasonal_scheduler = SeasonalScheduler()
timezone_scheduler = TimezoneAwareScheduler()

@scheduling_router.get("/health")
async def scheduling_health():
    """Scheduling service health check"""
    return {"status": "healthy", "service": "scheduling"}

@scheduling_router.get("/active-schedules")
async def get_active_schedules():
    """Get all active content schedules"""
    return await publication_scheduler.get_active_schedules()

# Export router for main application
__all__ = ["scheduling_router"]