"""Merchandise Manager - Central Management System

Central management system for merchandise and product monetization with comprehensive
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

from .core.merchandise_engine import MerchandiseEngine

logger = logging.getLogger(__name__)

class MerchandiseSystemStatus(Enum):
    """System status for merchandise management"""
    INITIALIZING = "initializing"
    RUNNING = "running"
    PAUSED = "paused"
    ERROR = "error"
    SHUTDOWN = "shutdown"

@dataclass
class SystemMetrics:
    """System metrics for merchandise management"""
    total_operations: int
    active_jobs: int
    processing_queue_size: int
    uptime: float
    last_updated: datetime

class MerchandiseManager:
    """
    Central Merchandise Management System
    
    Provides comprehensive merchandise and product monetization with:
    - Centralized operation control
    - Real-time monitoring and metrics
    - Performance optimization
    - Analytics and reporting
    - System health monitoring
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.status = MerchandiseSystemStatus.INITIALIZING
        self.merchandise_engine = MerchandiseEngine(self.config.get('engine', {}))
        self.start_time = datetime.utcnow()
        self.metrics = SystemMetrics(
            total_operations=0,
            active_jobs=0,
            processing_queue_size=0,
            uptime=0.0,
            last_updated=datetime.utcnow()
        )
        
    async def initialize(self) -> Dict[str, Any]:
        """Initialize the merchandise management system"""
        try:
            logger.info("Initializing Merchandise Manager...")
            
            # Initialize engine
            engine_result = await self.merchandise_engine.initialize()
            
            # Update status
            self.status = MerchandiseSystemStatus.RUNNING
            
            # Update metrics
            await self._update_metrics()
            
            logger.info("Merchandise Manager initialized successfully")
            
            return {
                "status": "initialized",
                "manager_status": self.status.value,
                "engine_result": engine_result,
                "metrics": self.metrics.__dict__
            }
            
        except Exception as e:
            logger.error(f"Failed to initialize merchandise manager: {e}")
            self.status = MerchandiseSystemStatus.ERROR
            raise
    
    async def shutdown(self):
        """Shutdown the merchandise management system"""
        logger.info("Shutting down Merchandise Manager...")
        
        self.status = MerchandiseSystemStatus.SHUTDOWN
        await self.merchandise_engine.shutdown()
        
        logger.info("Merchandise Manager shutdown complete")
    
    async def process_operation(
        self,
        operation: str,
        data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Process merchandise operation"""
        try:
            result = await self.merchandise_engine.process_operation(operation, data)
            
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
        """Get merchandise analytics"""
        try:
            return await self.merchandise_engine.get_analytics()
            
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
            "engine_running": self.merchandise_engine.is_running
        }
    
    async def health_check(self) -> Dict[str, Any]:
        """Perform health check"""
        try:
            health_status = {
                "manager_status": self.status.value,
                "engine_running": self.merchandise_engine.is_running,
                "total_operations": self.metrics.total_operations,
                "active_jobs": len(self.merchandise_engine.active_jobs),
                "timestamp": datetime.utcnow().isoformat()
            }
            
            # Check if system is healthy
            is_healthy = (
                self.status == MerchandiseSystemStatus.RUNNING and
                self.merchandise_engine.is_running
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
            self.metrics.active_jobs = len(self.merchandise_engine.active_jobs)
            self.metrics.processing_queue_size = len(self.merchandise_engine.active_jobs)
            self.metrics.uptime = (datetime.utcnow() - self.start_time).total_seconds()
            self.metrics.last_updated = datetime.utcnow()
            
        except Exception as e:
            logger.error(f"Failed to update metrics: {e}")