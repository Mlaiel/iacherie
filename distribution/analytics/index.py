"""
import asyncio

Analytics Service Entry Point - Distribution Analytics Hub
========================================================

FastAPI service for analytics and intelligence systems in content distribution.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

from fastapi import APIRouter, Depends, HTTPException
from typing import Dict, List, Any, Optional
import logging

from . import (
    AnalyticsAggregator,
    AttributionAnalytics,
    CohortAnalytics,
    CompetitiveAnalytics,
    FunnelAnalytics,
    LifetimeValueAnalytics,
    PredictiveAnalytics,
    ROIAnalytics,
    SentimentAnalytics
)

logger = logging.getLogger(__name__)

# Analytics router
analytics_router = APIRouter(prefix="/analytics", tags=["analytics"])

# Initialize analytics services
analytics_aggregator = AnalyticsAggregator()
attribution_analytics = AttributionAnalytics()
cohort_analytics = CohortAnalytics()
competitive_analytics = CompetitiveAnalytics()
funnel_analytics = FunnelAnalytics()
lifetime_value_analytics = LifetimeValueAnalytics()
predictive_analytics = PredictiveAnalytics()
roi_analytics = ROIAnalytics()
sentiment_analytics = SentimentAnalytics()

@analytics_router.get("/health")
async def analytics_health() -> None:
    """Analytics service health check"""
    return {"status": "healthy", "service": "analytics"}

@analytics_router.get("/metrics")
async def analytics_metrics() -> None:
    """Get analytics service metrics"""
    return await analytics_aggregator.get_service_metrics()

# Export router for main application
__all__ = ["analytics_router"]