"""Distribution System Index - Main Interface
==========================================

Central index file providing the main distribution system interface and factory functions.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: © 2025 Fahed Mlaiel. All rights reserved.
"""
import asyncio
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any, Union
from enum import Enum
from dataclasses import dataclass
from uuid import UUID, uuid4

from .manager import DistributionManager
from .publisher import ContentPublisher
from .scheduler import DistributionScheduler
from .tracker import DistributionTracker
from .analytics import DistributionAnalytics
from .monitor import DistributionMonitor


class DistributionStatus(Enum):
    """Distribution system status enumeration."""
    INACTIVE = "inactive"
    INITIALIZING = "initializing"
    ACTIVE = "active"
    PAUSED = "paused"
    ERROR = "error"
    MAINTENANCE = "maintenance"


@dataclass
class DistributionSystemConfig:
    """Configuration for distribution system."""
    max_concurrent_distributions: int = 50
    retry_attempts: int = 3
    timeout_seconds: int = 300
    rate_limit_per_minute: int = 100
    enable_analytics: bool = True
    enable_monitoring: bool = True
    auto_recovery: bool = True
    debug_mode: bool = False


class DistributionSystem:
    """
    Main Distribution System Interface
    
    Provides unified access to all distribution functionality including
    multi-platform publishing, scheduling, tracking, and analytics.
    """
    
    def __init__(self, config: Optional[DistributionSystemConfig] = None):
        """Initialize distribution system with configuration."""
        self.config = config or DistributionSystemConfig()
        self.system_id = uuid4()
        self.status = DistributionStatus.INACTIVE
        self.created_at = datetime.utcnow()
        self.logger = logging.getLogger(__name__)
        
        # Core components
        self.manager: Optional[DistributionManager] = None
        self.publisher: Optional[ContentPublisher] = None
        self.scheduler: Optional[DistributionScheduler] = None
        self.tracker: Optional[DistributionTracker] = None
        self.analytics: Optional[DistributionAnalytics] = None
        self.monitor: Optional[DistributionMonitor] = None
        
        # System metrics
        self.metrics = {
            'total_distributions': 0,
            'successful_distributions': 0,
            'failed_distributions': 0,
            'active_distributions': 0,
            'platforms_connected': 0,
            'uptime_seconds': 0
        }
    
    async def initialize(self) -> bool:
        """
        Initialize all distribution system components.
        
        Returns:
            bool: True if initialization successful, False otherwise
        """
        try:
            self.status = DistributionStatus.INITIALIZING
            self.logger.info(f"Initializing distribution system {self.system_id}")
            
            # Initialize core components
            self.manager = DistributionManager(self.config)
            self.publisher = ContentPublisher(self.config)
            self.scheduler = DistributionScheduler(self.config)
            self.tracker = DistributionTracker(self.config)
            
            if self.config.enable_analytics:
                self.analytics = DistributionAnalytics(self.config)
                await self.analytics.initialize()
            
            if self.config.enable_monitoring:
                self.monitor = DistributionMonitor(self.config)
                await self.monitor.start()
            
            # Initialize all components
            await self.manager.initialize()
            await self.publisher.initialize()
            await self.scheduler.initialize()
            await self.tracker.initialize()
            
            self.status = DistributionStatus.ACTIVE
            self.logger.info("Distribution system initialized successfully")
            return True
            
        except Exception as e:
            self.status = DistributionStatus.ERROR
            self.logger.error(f"Failed to initialize distribution system: {e}")
            return False
    
    async def shutdown(self) -> bool:
        """
        Gracefully shutdown the distribution system.
        
        Returns:
            bool: True if shutdown successful, False otherwise
        """
        try:
            self.logger.info("Shutting down distribution system")
            self.status = DistributionStatus.INACTIVE
            
            # Shutdown components in reverse order
            if self.monitor:
                await self.monitor.stop()
            
            if self.analytics:
                await self.analytics.shutdown()
            
            if self.tracker:
                await self.tracker.shutdown()
            
            if self.scheduler:
                await self.scheduler.shutdown()
            
            if self.publisher:
                await self.publisher.shutdown()
            
            if self.manager:
                await self.manager.shutdown()
            
            self.logger.info("Distribution system shutdown complete")
            return True
            
        except Exception as e:
            self.logger.error(f"Error during distribution system shutdown: {e}")
            return False
    
    async def distribute_content(
        self,
        content_id: UUID,
        platforms: List[str],
        schedule_time: Optional[datetime] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Distribute content to specified platforms.
        
        Args:
            content_id: Unique identifier for content
            platforms: List of target platforms
            schedule_time: Optional scheduled distribution time
            metadata: Additional distribution metadata
            
        Returns:
            Dict containing distribution results
        """
        if self.status != DistributionStatus.ACTIVE:
            raise RuntimeError("Distribution system not active")
        
        try:
            # Delegate to manager
            result = await self.manager.distribute_content(
                content_id=content_id,
                platforms=platforms,
                schedule_time=schedule_time,
                metadata=metadata
            )
            
            # Update metrics
            self.metrics['total_distributions'] += 1
            if result.get('success', False):
                self.metrics['successful_distributions'] += 1
            else:
                self.metrics['failed_distributions'] += 1
            
            return result
            
        except Exception as e:
            self.logger.error(f"Distribution failed: {e}")
            self.metrics['failed_distributions'] += 1
            raise
    
    async def get_distribution_status(self, distribution_id: UUID) -> Dict[str, Any]:
        """Get status of specific distribution."""
        if not self.tracker:
            raise RuntimeError("Tracker not initialized")
        
        return await self.tracker.get_distribution_status(distribution_id)
    
    async def get_analytics(
        self,
        content_id: Optional[UUID] = None,
        platform: Optional[str] = None,
        time_range: Optional[tuple] = None
    ) -> Dict[str, Any]:
        """Get distribution analytics."""
        if not self.analytics:
            raise RuntimeError("Analytics not enabled")
        
        return await self.analytics.get_analytics(
            content_id=content_id,
            platform=platform,
            time_range=time_range
        )
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get current system status and metrics."""
        return {
            'system_id': str(self.system_id),
            'status': self.status.value,
            'created_at': self.created_at.isoformat(),
            'config': {
                'max_concurrent_distributions': self.config.max_concurrent_distributions,
                'retry_attempts': self.config.retry_attempts,
                'timeout_seconds': self.config.timeout_seconds,
                'rate_limit_per_minute': self.config.rate_limit_per_minute,
                'enable_analytics': self.config.enable_analytics,
                'enable_monitoring': self.config.enable_monitoring
            },
            'metrics': self.metrics.copy(),
            'components': {
                'manager': self.manager is not None,
                'publisher': self.publisher is not None,
                'scheduler': self.scheduler is not None,
                'tracker': self.tracker is not None,
                'analytics': self.analytics is not None,
                'monitor': self.monitor is not None
            }
        }


async def create_distribution_system(
    config: Optional[DistributionSystemConfig] = None
) -> DistributionSystem:
    """
    Factory function to create and initialize a distribution system.
    
    Args:
        config: Optional system configuration
        
    Returns:
        Initialized DistributionSystem instance
    """
    system = DistributionSystem(config)
    
    if await system.initialize():
        return system
    else:
        raise RuntimeError("Failed to initialize distribution system")


# Health check function
async def health_check() -> Dict[str, Any]:
    """Perform distribution system health check."""
    return {
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat(),
        'module': 'distribution',
        'version': '1.0.0'
    }
