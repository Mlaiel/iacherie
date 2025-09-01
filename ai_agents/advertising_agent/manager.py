"""Advertising Manager - Central Management System

Central management system for advertising monetization with comprehensive
control and monitoring capabilities.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
from enum import Enum
from dataclasses import dataclass

from .core.advertising_engine import AdvertisingEngine

logger = logging.getLogger(__name__)

class AdvertisingSystemStatus(Enum):
    """
System status for advertising management"""

    INITIALIZING = "initializing"
    RUNNING = "running"
    PAUSED = "paused"
    ERROR = "error"
    SHUTDOWN = "shutdown"

@dataclass
class SystemMetrics:
    """System metrics for advertising management"""
    total_campaigns: int
    active_campaigns: int
    processing_queue_size: int
    total_revenue: float
    uptime: float
    last_updated: datetime

class AdvertisingManager:
    """
    Central Advertising Management System
    
    Provides comprehensive advertising monetization with:
    - Centralized campaign control
    - Real-time performance monitoring
    - Revenue optimization
    - Multi-network coordination
    - Analytics and reporting
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.status = AdvertisingSystemStatus.INITIALIZING
        self.advertising_engine = AdvertisingEngine(self.config.get('engine', {}))
        self.start_time = datetime.utcnow()
        self.metrics = SystemMetrics(
            total_campaigns=0,
            active_campaigns=0,
            processing_queue_size=0,
            total_revenue=0.0,
            uptime=0.0,
            last_updated=datetime.utcnow()
        )
        
    async def initialize(self) -> Dict[str, Any]:
        """
Initialize the advertising management system"""
        try:
            logger.info("Initializing Advertising Manager...")
            
            # Initialize advertising engine
            engine_result = await self.advertising_engine.initialize()
            
            # Update status
            self.status = AdvertisingSystemStatus.RUNNING
            
            # Update metrics
            await self._update_metrics()
            
            logger.info("Advertising Manager initialized successfully")
            
            return {
                "status": "initialized",
                "manager_status": self.status.value,
                "engine_result": engine_result,
                "metrics": self.metrics.__dict__
            }
            
        except Exception as e:
            logger.error(f"Failed to initialize advertising manager: {e}")
            self.status = AdvertisingSystemStatus.ERROR
            raise
    
    async def shutdown(self):
        """Shutdown the advertising management system"""
        logger.info("Shutting down Advertising Manager...")
        
        self.status = AdvertisingSystemStatus.SHUTDOWN
        await self.advertising_engine.shutdown()
        
        logger.info("Advertising Manager shutdown complete")
    
    async def optimize_content_ads(
        self,
        content_id: str,
        content_metadata: Dict[str, Any],
        audience_data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Optimize advertising for content"""
        try:
            result = await self.advertising_engine.optimize_ad_placement(
                content_id=content_id,
                content_metadata=content_metadata,
                audience_data=audience_data
            )
            
            return {
                "success": result.success,
                "job_id": result.job_id,
                "optimization": result.data,
                "error": result.error
            }
            
        except Exception as e:
            logger.error(f"Failed to optimize content ads: {e}")
            return {"success": False, "error": str(e)}
    
    async def create_campaign(
        self,
        content_id: str,
        ad_config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Create advertising campaign"""
        try:
            result = await self.advertising_engine.create_ad_campaign(content_id, ad_config)
            
            # Update metrics
            await self._update_metrics()
            
            return {
                "success": result.success,
                "ad_id": result.ad_id,
                "campaign_data": result.data,
                "error": result.error
            }
            
        except Exception as e:
            logger.error(f"Failed to create campaign: {e}")
            return {"success": False, "error": str(e)}
    
    async def get_campaign_performance(self, ad_id: str) -> Dict[str, Any]:
        """Get campaign performance metrics"""
        try:
            return await self.advertising_engine.track_ad_performance(ad_id)
            
        except Exception as e:
            logger.error(f"Failed to get campaign performance: {e}")
            return {"error": str(e)}
    
    async def get_content_revenue(self, content_id: str) -> Dict[str, Any]:
        """Get advertising revenue for content"""
        try:
            return await self.advertising_engine.get_content_revenue(content_id)
            
        except Exception as e:
            logger.error(f"Failed to get content revenue: {e}")
            return {"error": str(e)}
    
    async def get_analytics(self, time_range: str = "30d") -> Dict[str, Any]:
        """Get advertising analytics"""
        try:
            return await self.advertising_engine.get_advertising_analytics(time_range)
            
        except Exception as e:
            logger.error(f"Failed to get analytics: {e}")
            return {"error": str(e)}
    
    async def get_system_status(self) -> Dict[str, Any]:
        """Get system status and metrics"""
        await self._update_metrics()
        
        return {
            "status": self.status.value,
            "metrics": self.metrics.__dict__,
            "uptime_hours": (datetime.utcnow() - self.start_time).total_seconds() / 3600,
            "engine_running": self.advertising_engine.is_running
        }
    
    async def health_check(self) -> Dict[str, Any]:
        """Perform health check"""
        try:
            health_status = {
                "manager_status": self.status.value,
                "engine_running": self.advertising_engine.is_running,
                "total_campaigns": len(self.advertising_engine.advertisements),
                "active_jobs": len(self.advertising_engine.active_jobs),
                "timestamp": datetime.utcnow().isoformat()
            }
            
            # Check if system is healthy
            is_healthy = (
                self.status == AdvertisingSystemStatus.RUNNING and
                self.advertising_engine.is_running
            )
            
            health_status["healthy"] = is_healthy
            
            return health_status
            
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return {
                "healthy": False,
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
    
    # Private helper methods
    async def _update_metrics(self):
        """Update system metrics"""
        try:
            self.metrics.total_campaigns = len(self.advertising_engine.advertisements)
            self.metrics.active_campaigns = len([
                ad for ad in self.advertising_engine.advertisements.values()
                if ad.start_date and (not ad.end_date or ad.end_date > datetime.utcnow())
            ])
            self.metrics.processing_queue_size = len(self.advertising_engine.active_jobs)
            self.metrics.total_revenue = sum(
                ad.revenue for ad in self.advertising_engine.advertisements.values()
            )
            self.metrics.uptime = (datetime.utcnow() - self.start_time).total_seconds()
            self.metrics.last_updated = datetime.utcnow()
            
        except Exception as e:
            logger.error(f"Failed to update metrics: {e}")