"""
Distribution Manager - Main Distribution Controller
================================================

Enterprise-grade distribution management system coordinating all aspects
of multi-platform content distribution, optimization, and analytics.

Features:
- Multi-platform content distribution coordination
- AI-powered optimization and scheduling
- Real-time analytics and performance monitoring
- Compliance and security management
- Revenue distribution and monetization tracking

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field
from enum import Enum
import json
from datetime import datetime, timedelta
import uuid

# Import all subsystem managers
from .analytics import AnalyticsAggregator
from .connectors import PlatformConnectors
from .scheduling import PublicationScheduler
from .optimization import DistributionIntelligence
from .management import AutomationOrchestrator, HealthChecker
from .core import CrossPlatformSync, ContentSecurity

logger = logging.getLogger(__name__)

class DistributionStatus(Enum):
    """Distribution status enumeration"""
    PENDING = "pending"
    PROCESSING = "processing"
    DISTRIBUTED = "distributed"
    FAILED = "failed"
    OPTIMIZING = "optimizing"

@dataclass
class DistributionRequest:
    """Distribution request data structure"""
    content_id: str
    creator_id: str
    platforms: List[str]
    schedule_time: Optional[datetime] = None
    optimization_level: str = "high"
    security_level: str = "standard"
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class DistributionResult:
    """Distribution result data structure"""
    request_id: str
    status: DistributionStatus
    platforms_results: Dict[str, Dict[str, Any]]
    analytics_data: Dict[str, Any]
    optimization_metrics: Dict[str, Any]
    timestamp: datetime = field(default_factory=datetime.now)

class DistributionManager:
    """
    Main Distribution Management System
    
    Coordinates all aspects of content distribution across multiple platforms
    with AI optimization, security, and comprehensive analytics.
    """
    
    def __init__(self) -> None:
        """Initialize distribution manager with all subsystems"""
        self.analytics = AnalyticsAggregator()
        self.connectors = PlatformConnectors()
        self.scheduler = PublicationScheduler()
        self.intelligence = DistributionIntelligence()
        self.orchestrator = AutomationOrchestrator()
        self.health_checker = HealthChecker()
        self.platform_sync = CrossPlatformSync()
        self.content_security = ContentSecurity()
        
        self.active_distributions: Dict[str, DistributionRequest] = {}
        self.distribution_history: List[DistributionResult] = []
        self.performance_metrics: Dict[str, Any] = {}
        
        logger.info("Distribution Manager initialized successfully")
    
    async def distribute_content(self, request: DistributionRequest) -> DistributionResult:
        """
        Main content distribution orchestration
        
        Args:
            request: Distribution request with content and platform details
            
        Returns:
            DistributionResult with comprehensive distribution outcome
        """
        request_id = str(uuid.uuid4())
        self.active_distributions[request_id] = request
        
        try:
            # Security validation
            security_validation = await self.content_security.validate_content(
                request.content_id, request.security_level
            )
            
            if not security_validation["valid"]:
                return DistributionResult(
                    request_id=request_id,
                    status=DistributionStatus.FAILED,
                    platforms_results={},
                    analytics_data={"error": "Security validation failed"},
                    optimization_metrics={}
                )
            
            # AI optimization recommendations
            optimization_data = await self.intelligence.get_optimization_recommendations(
                content_id=request.content_id,
                platforms=request.platforms,
                optimization_level=request.optimization_level
            )
            
            # Schedule optimization if needed
            if request.schedule_time:
                scheduled_result = await self.scheduler.schedule_distribution(
                    request_id, request.schedule_time, optimization_data
                )
                if not scheduled_result["success"]:
                    return DistributionResult(
                        request_id=request_id,
                        status=DistributionStatus.FAILED,
                        platforms_results={},
                        analytics_data={"error": "Scheduling failed"},
                        optimization_metrics=optimization_data
                    )
            
            # Execute distribution across platforms
            platforms_results = {}
            for platform in request.platforms:
                try:
                    platform_result = await self.connectors.distribute_to_platform(
                        platform=platform,
                        content_id=request.content_id,
                        optimization_data=optimization_data.get(platform, {}),
                        metadata=request.metadata
                    )
                    platforms_results[platform] = platform_result
                except Exception as e:
                    platforms_results[platform] = {
                        "success": False,
                        "error": str(e)
                    }
                    logger.error(f"Distribution to {platform} failed: {e}")
            
            # Collect analytics data
            analytics_data = await self.analytics.collect_distribution_analytics(
                request_id=request_id,
                platforms_results=platforms_results,
                optimization_data=optimization_data
            )
            
            # Cross-platform synchronization
            sync_result = await self.platform_sync.synchronize_distribution(
                request_id, platforms_results
            )
            
            # Determine overall status
            successful_platforms = [
                p for p, r in platforms_results.items() 
                if r.get("success", False)
            ]
            
            if len(successful_platforms) == len(request.platforms):
                status = DistributionStatus.DISTRIBUTED
            elif len(successful_platforms) > 0:
                status = DistributionStatus.PROCESSING
            else:
                status = DistributionStatus.FAILED
            
            result = DistributionResult(
                request_id=request_id,
                status=status,
                platforms_results=platforms_results,
                analytics_data=analytics_data,
                optimization_metrics=optimization_data
            )
            
            # Store result and cleanup
            self.distribution_history.append(result)
            if request_id in self.active_distributions:
                del self.active_distributions[request_id]
            
            logger.info(f"Distribution {request_id} completed with status: {status}")
            return result
            
        except Exception as e:
            logger.error(f"Distribution {request_id} failed: {e}")
            
            # Cleanup on failure
            if request_id in self.active_distributions:
                del self.active_distributions[request_id]
            
            return DistributionResult(
                request_id=request_id,
                status=DistributionStatus.FAILED,
                platforms_results={},
                analytics_data={"error": str(e)},
                optimization_metrics={}
            )
    
    async def get_distribution_status(self, request_id: str) -> Optional[Dict[str, Any]]:
        """Get status of specific distribution request"""
        # Check active distributions
        if request_id in self.active_distributions:
            return {
                "request_id": request_id,
                "status": "processing",
                "request": self.active_distributions[request_id]
            }
        
        # Check history
        for result in self.distribution_history:
            if result.request_id == request_id:
                return {
                    "request_id": request_id,
                    "status": result.status.value,
                    "result": result
                }
        
        return None
    
    async def get_system_health(self) -> Dict[str, Any]:
        """Get comprehensive distribution system health"""
        return {
            "distribution_manager": "healthy",
            "active_distributions": len(self.active_distributions),
            "total_processed": len(self.distribution_history),
            "subsystems": await self.health_checker.get_subsystems_health(),
            "performance_metrics": self.performance_metrics
        }
    
    async def get_analytics_dashboard(self) -> Dict[str, Any]:
        """Get analytics dashboard data"""
        return await self.analytics.get_distribution_dashboard()
    
    async def optimize_distribution_strategy(self, creator_id: str) -> Dict[str, Any]:
        """Get AI-powered distribution strategy optimization"""
        return await self.intelligence.optimize_creator_strategy(creator_id)
    
    async def emergency_stop_distribution(self, request_id: str) -> Dict[str, Any]:
        """Emergency stop for active distribution"""
        if request_id in self.active_distributions:
            # Stop all platform distributions
            stop_results = await self.orchestrator.emergency_stop_distribution(request_id)
            
            # Remove from active distributions
            del self.active_distributions[request_id]
            
            return {
                "success": True,
                "request_id": request_id,
                "stop_results": stop_results
            }
        
        return {
            "success": False,
            "error": "Distribution not found or already completed"
        }