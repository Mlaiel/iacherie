"""Distribution Module Index

Enterprise-grade entry point for the IA Influencer Agent distribution system.
Provides unified access to all distribution components and services.

Author: Fahed Mlaiel
Email: mlaiel@live.de
Copyright: © 2025 Fahed Mlaiel - All Rights Reserved

WARNING: This code is proprietary and protected. Unauthorized use, reproduction, 
or distribution is strictly prohibited and will result in legal action.
"""
import asyncio
import logging
from typing import Dict, List, Optional, Any, Union
from datetime import datetime
from dataclasses import dataclass
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks
from sqlalchemy.orm import Session
import aioredis

from ....core.database import get_db
from ....core.config import settings
from ....core.logging import get_logger
from ....core.exceptions import DistributionError
from ....utils.monitoring import MetricsCollector

# Import all distribution components
from . import (
    DistributionModuleManager,
    PlatformDistributionManager,
    DistributionStrategyEngine,
    AdvancedAnalyticsTracker,
    RevenueTracker,
    ContentDistributionScheduler,
    EnterpriseContentAdapter,
    OptimizationEngine,
    create_distribution_manager,
    get_module_info,
    health_check
)

logger = get_logger(__name__)
metrics = MetricsCollector("distribution.index")

# Global distribution manager instance
_distribution_manager: Optional[DistributionModuleManager] = None
_redis_client: Optional[aioredis.Redis] = None


@dataclass
class DistributionConfig:
    """Distribution service configuration"""
    enable_analytics: bool = True
    enable_revenue_tracking: bool = True
    enable_scheduling: bool = True
    enable_content_adaptation: bool = True
    enable_optimization: bool = True
    cache_ttl: int = 300
    max_concurrent_operations: int = 10
    debug_mode: bool = False


class DistributionService:
    """
    Main distribution service providing unified access to all distribution features.
    
    This service acts as the primary interface for:
    - Content distribution across multiple platforms
    - Analytics and performance tracking
    - Revenue monitoring and optimization
    - Intelligent scheduling and timing
    - Content adaptation and formatting
    - Strategy optimization and recommendations
    """
    
    def __init__(self, config: DistributionConfig = None):
        self.config = config or DistributionConfig()
        self.manager: Optional[DistributionModuleManager] = None
        self.is_initialized = False
        
    async def initialize(self, db: Session) -> None:
        """Initialize the distribution service"""
        try:
            logger.info("Initializing Distribution Service...")
            
            # Create Redis connection
            global _redis_client
            _redis_client = await aioredis.from_url(settings.REDIS_URL)
            
            # Initialize distribution manager
            self.manager = await create_distribution_manager(db, _redis_client)
            
            # Store global reference
            global _distribution_manager
            _distribution_manager = self.manager
            
            self.is_initialized = True
            
            logger.info("Distribution Service successfully initialized")
            
        except Exception as e:
            logger.error(f"Failed to initialize Distribution Service: {e}")
            raise DistributionError(f"Service initialization failed: {e}")
    
    async def shutdown(self) -> None:
        """Shutdown the distribution service"""
        try:
            logger.info("Shutting down Distribution Service...")
            
            if self.manager:
                await self.manager.shutdown()
            
            if _redis_client:
                await _redis_client.close()
            
            self.is_initialized = False
            
            logger.info("Distribution Service successfully shutdown")
            
        except Exception as e:
            logger.error(f"Error during Distribution Service shutdown: {e}")
    
    async def distribute_content(
        self,
        user_id: int,
        content_id: int,
        platforms: List[str],
        strategy: str = "optimal_timing",
        schedule_time: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """Distribute content across specified platforms"""
        if not self.is_initialized:
            raise DistributionError("Distribution service not initialized")
        
        try:
            # Use platform manager for distribution
            platform_manager = self.manager.platform_manager
            
            # Convert platform strings to enum
            from .platform_manager import PlatformType
            platform_enums = [PlatformType(platform) for platform in platforms]
            
            # Distribute content
            results = await platform_manager.distribute_content(
                user_id=user_id,
                content_id=content_id,
                platforms=platform_enums,
                strategy=strategy,
                schedule_time=schedule_time
            )
            
            return {
                "success": True,
                "results": results,
                "message": f"Content distributed to {len(platforms)} platforms"
            }
            
        except Exception as e:
            logger.error(f"Content distribution failed: {e}")
            raise DistributionError(f"Distribution failed: {e}")
    
    async def get_analytics(
        self,
        user_id: int,
        time_range: str = "last_30_days",
        platforms: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Get comprehensive analytics for user content"""
        if not self.is_initialized:
            raise DistributionError("Distribution service not initialized")
        
        try:
            analytics_tracker = self.manager.analytics_tracker
            
            # Get analytics report
            report = await analytics_tracker.generate_comprehensive_report(
                user_id=user_id,
                time_range=time_range,
                platforms=platforms
            )
            
            return {
                "success": True,
                "analytics": report,
                "generated_at": datetime.utcnow()
            }
            
        except Exception as e:
            logger.error(f"Analytics retrieval failed: {e}")
            raise DistributionError(f"Analytics failed: {e}")
    
    async def get_revenue_data(
        self,
        user_id: int,
        time_range: str = "last_30_days"
    ) -> Dict[str, Any]:
        """Get revenue analytics and insights"""
        if not self.is_initialized:
            raise DistributionError("Distribution service not initialized")
        
        try:
            revenue_tracker = self.manager.revenue_tracker
            
            # Get revenue analytics
            analytics = await revenue_tracker.get_comprehensive_revenue_data(
                user_id=user_id,
                time_range=time_range
            )
            
            return {
                "success": True,
                "revenue_data": analytics,
                "generated_at": datetime.utcnow()
            }
            
        except Exception as e:
            logger.error(f"Revenue data retrieval failed: {e}")
            raise DistributionError(f"Revenue data failed: {e}")
    
    async def schedule_content(
        self,
        user_id: int,
        content_id: int,
        platforms: List[str],
        schedule_time: datetime,
        strategy: str = "optimal_timing"
    ) -> Dict[str, Any]:
        """Schedule content for future distribution"""
        if not self.is_initialized:
            raise DistributionError("Distribution service not initialized")
        
        try:
            scheduler = self.manager.scheduler
            
            # Convert platform strings to enum
            from .platform_manager import PlatformType
            platform_enums = [PlatformType(platform) for platform in platforms]
            
            # Schedule content
            tasks = await scheduler.schedule_content(
                user_id=user_id,
                content_id=content_id,
                platforms=platform_enums,
                target_time=schedule_time,
                strategy=strategy
            )
            
            return {
                "success": True,
                "scheduled_tasks": len(tasks),
                "schedule_time": schedule_time,
                "platforms": platforms
            }
            
        except Exception as e:
            logger.error(f"Content scheduling failed: {e}")
            raise DistributionError(f"Scheduling failed: {e}")
    
    async def adapt_content(
        self,
        content_id: int,
        target_platforms: List[str],
        quality_level: str = "high"
    ) -> Dict[str, Any]:
        """Adapt content for specified platforms"""
        if not self.is_initialized:
            raise DistributionError("Distribution service not initialized")
        
        try:
            content_adapter = self.manager.content_adapter
            
            # Convert platform strings to enum
            from .platform_manager import PlatformType
            platform_enums = [PlatformType(platform) for platform in platforms]
            
            # Create adaptation request
            from .content_adapters import AdaptationRequest, QualityLevel
            request = AdaptationRequest(
                content_id=content_id,
                target_platforms=platform_enums,
                quality_level=QualityLevel(quality_level)
            )
            
            # Adapt content
            variants = await content_adapter.adapt_content(request)
            
            return {
                "success": True,
                "variants_created": len(variants),
                "variants": variants
            }
            
        except Exception as e:
            logger.error(f"Content adaptation failed: {e}")
            raise DistributionError(f"Adaptation failed: {e}")


# Global service instance
_distribution_service: Optional[DistributionService] = None


async def get_distribution_service() -> DistributionService:
    """Get or create the global distribution service instance"""
    global _distribution_service
    
    if _distribution_service is None:
        _distribution_service = DistributionService()
    
    return _distribution_service


async def initialize_distribution_service(db: Session) -> DistributionService:
    """Initialize the distribution service"""
    service = await get_distribution_service()
    
    if not service.is_initialized:
        await service.initialize(db)
    
    return service


async def shutdown_distribution_service() -> None:
    """Shutdown the distribution service"""
    global _distribution_service
    
    if _distribution_service and _distribution_service.is_initialized:
        await _distribution_service.shutdown()
        _distribution_service = None


# FastAPI lifespan manager
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage FastAPI application lifespan"""
    # Startup
    logger.info("Starting Distribution Service...")
    
    try:
        # Initialize service would be done per request with DB session
        yield
    finally:
        # Shutdown
        logger.info("Shutting down Distribution Service...")
        await shutdown_distribution_service()


# FastAPI dependency
async def get_service(db: Session = Depends(get_db)) -> DistributionService:
    """FastAPI dependency to get distribution service"""
    return await initialize_distribution_service(db)


# Utility functions for external use
async def quick_distribute(
    user_id: int,
    content_id: int,
    platforms: List[str],
    db: Session
) -> Dict[str, Any]:
    """Quick content distribution function"""
    service = await initialize_distribution_service(db)
    return await service.distribute_content(user_id, content_id, platforms)


async def quick_analytics(
    user_id: int,
    time_range: str,
    db: Session
) -> Dict[str, Any]:
    """Quick analytics retrieval function"""
    service = await initialize_distribution_service(db)
    return await service.get_analytics(user_id, time_range)


async def quick_schedule(
    user_id: int,
    content_id: int,
    platforms: List[str],
    schedule_time: datetime,
    db: Session
) -> Dict[str, Any]:
    """Quick content scheduling function"""
    service = await initialize_distribution_service(db)
    return await service.schedule_content(user_id, content_id, platforms, schedule_time)


# Module status and health
async def get_distribution_status() -> Dict[str, Any]:
    """Get distribution module status"""
    if _distribution_manager:
        return await _distribution_manager.get_module_status()
    else:
        return {
            "status": "not_initialized",
            "message": "Distribution manager not initialized"
        }


async def get_distribution_health() -> Dict[str, Any]:
    """Get distribution module health check"""
    return await health_check()


# Export main components
__all__ = [
    "DistributionService",
    "DistributionConfig",
    "get_distribution_service",
    "initialize_distribution_service",
    "shutdown_distribution_service",
    "get_service",
    "quick_distribute",
    "quick_analytics",
    "quick_schedule",
    "get_distribution_status",
    "get_distribution_health",
    "lifespan"
]


# Initialize logging
logger.info("""🎯 Distribution Module Index v2.1.0 Loaded
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🚀 Enterprise Distribution Service Ready
✅ Multi-platform content distribution
✅ AI-powered analytics and insights  
✅ Revenue tracking and monetization
✅ Intelligent scheduling and optimization
✅ Content adaptation and formatting

👨‍💻 Author: Fahed Mlaiel (mlaiel@live.de)
🛡️  Protected by copyright - Unauthorized use prohibited

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
""")
