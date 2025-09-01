"""Crowdfunding Manager - Central Management System

Central management system for crowdfunding and campaign management with comprehensive
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

from .core.crowdfunding_engine import CrowdfundingEngine

logger = logging.getLogger(__name__)

class CrowdfundingSystemStatus(Enum):
    """System status for crowdfunding management"""
    INITIALIZING = "initializing"
    RUNNING = "running"
    PAUSED = "paused"
    ERROR = "error"
    SHUTDOWN = "shutdown"

@dataclass
class SystemMetrics:
    """System metrics for crowdfunding management"""
    total_operations: int
    active_jobs: int
    processing_queue_size: int
    uptime: float
    last_updated: datetime

class CrowdfundingManager:
    """
    Central Crowdfunding Management System
    
    Provides comprehensive crowdfunding and campaign management with:
    - Centralized operation control
    - Real-time monitoring and metrics
    - Performance optimization
    - Analytics and reporting
    - System health monitoring
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.status = CrowdfundingSystemStatus.INITIALIZING
        self.crowdfunding_engine = CrowdfundingEngine(self.config.get('engine', {}))
        self.start_time = datetime.utcnow()
        self.metrics = SystemMetrics(
            total_operations=0,
            active_jobs=0,
            processing_queue_size=0,
            uptime=0.0,
            last_updated=datetime.utcnow()
        )
        
    async def initialize(self) -> Dict[str, Any]:
        """Initialize the crowdfunding management system"""
        try:
            logger.info("Initializing Crowdfunding Manager...")
            
            # Initialize engine
            engine_result = await self.crowdfunding_engine.initialize()
            
            # Update status
            self.status = CrowdfundingSystemStatus.RUNNING
            
            # Update metrics
            await self._update_metrics()
            
            logger.info("Crowdfunding Manager initialized successfully")
            
            return {
                "status": "initialized",
                "manager_status": self.status.value,
                "engine_result": engine_result,
                "metrics": self.metrics.__dict__
            }
            
        except Exception as e:
            logger.error(f"Failed to initialize crowdfunding manager: {e}")
            self.status = CrowdfundingSystemStatus.ERROR
            raise
    
    async def shutdown(self):
        """Shutdown the crowdfunding management system"""
        logger.info("Shutting down Crowdfunding Manager...")
        
        self.status = CrowdfundingSystemStatus.SHUTDOWN
        await self.crowdfunding_engine.shutdown()
        
        logger.info("Crowdfunding Manager shutdown complete")
    
    async def process_operation(
        self,
        operation: str,
        data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Process crowdfunding operation"""
        try:
            result = await self.crowdfunding_engine.process_operation(operation, data)
            
            # Update metrics
            self.metrics.total_operations += 1
            await self._update_metrics()
            
            return {
                "success": result.success,
                "job_id": result.job_id,
                "data": result.data,
                "error": result.error
            }
            
        except Exception as e:
            logger.error(f"Failed to process operation: {e}")
            return {"success": False, "error": str(e)}
    
    async def get_analytics(self) -> Dict[str, Any]:
        """Get crowdfunding analytics"""
        try:
            return await self.crowdfunding_engine.get_analytics()
            
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
            "engine_running": self.crowdfunding_engine.is_running
        }
    
    async def health_check(self) -> Dict[str, Any]:
        """Perform health check"""
        try:
            health_status = {
                "manager_status": self.status.value,
                "engine_running": self.crowdfunding_engine.is_running,
                "total_operations": self.metrics.total_operations,
                "active_jobs": len(self.crowdfunding_engine.active_jobs),
                "timestamp": datetime.utcnow().isoformat()
            }
            
            # Check if system is healthy
            is_healthy = (
                self.status == CrowdfundingSystemStatus.RUNNING and
                self.crowdfunding_engine.is_running
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
            self.metrics.active_jobs = len(self.crowdfunding_engine.active_jobs)
            self.metrics.processing_queue_size = len(self.crowdfunding_engine.active_jobs)
            self.metrics.uptime = (datetime.utcnow() - self.start_time).total_seconds()
            self.metrics.last_updated = datetime.utcnow()
            
        except Exception as e:
            logger.error(f"Failed to update metrics: {e}")