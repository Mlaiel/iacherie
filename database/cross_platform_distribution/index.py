"""Cross-Platform Distribution - Main Index Module

Enterprise-grade cross-platform content distribution system entry point.
Provides centralized access to all distribution components and services.

Author: Fahed Mlaiel (mlaiel@live.de)
Development Team: Lead AI Developer, Senior Backend Engineer, ML Engineer, DBA, Security Expert
Architecture: Enterprise-grade, microservices-ready, production-optimized

⚠️ INTELLECTUAL PROPERTY WARNING ⚠️
This code is the exclusive property of Fahed Mlaiel (mlaiel@live.de).
Any unauthorized use, copying, or distribution is STRICTLY PROHIBITED.
Violations will be prosecuted under international copyright law.
"""from typing import Dict, List, Optional, Any, Union
import logging
from datetime import datetime

# Import all main components
from .distribution_manager import (
    CrossPlatformDistributionManager,
    DistributionJob,
    DistributionTemplate,
    DistributionStatus,
    DistributionPriority,
    ContentFormat,
    TargetPlatform,
    OptimizationStrategy,
    DistributionMetrics
)

from .platform_adapters import (
    BasePlatformAdapter,
    YouTubeAdapter,
    SpotifyAdapter,
    InstagramAdapter,
    PlatformAdapterFactory,
    PlatformCredentials,
    UploadResult,
    ContentMetadata,
    PlatformType,
    AuthenticationType,
    UploadStatus
)

from .content_optimizer import (
    ContentOptimizer,
    OptimizationRequest,
    OptimizationResult,
    PlatformConstraints,
    OptimizationType,
    ContentType,
    PlatformTarget
)

from .scheduling_engine import (
    SchedulingEngine,
    SchedulingRequest,
    SchedulingResult,
    TimeSlot,
    ScheduleTemplate,
    PerformanceHistory,
    SchedulingStrategy,
    TimeSlotPriority,
    AudienceSegment
)

from .analytics_collector import (
    AnalyticsCollector,
    MetricData,
    AnalyticsReport,
    DistributionMetrics as MetricsModel,
    AnalyticsSnapshot,
    MetricType,
    AnalyticsTimeframe,
    DataSource
)

logger = logging.getLogger(__name__)

class CrossPlatformDistributionSystem:
    """    Comprehensive cross-platform distribution system
    
    Main entry point for all distribution operations including:
    - Content distribution management
    - Platform-specific adaptations
    - AI-powered content optimization
    - Intelligent scheduling
    - Performance analytics
    """    
    def __init__(self, db_session=None, config: Optional[Dict[str, Any]] = None):
        """        Initialize the distribution system
        
        Args:
            db_session: Database session for data persistence
            config: System configuration parameters
        """        self.db_session = db_session
        self.config = config or {}
        self.logger = logging.getLogger(__name__)
        
        # Initialize core components
        self.distribution_manager = CrossPlatformDistributionManager(db_session)
        self.content_optimizer = ContentOptimizer()
        self.scheduling_engine = SchedulingEngine(db_session)
        self.analytics_collector = AnalyticsCollector(db_session)
        
        # Platform adapter factory
        self.adapter_factory = PlatformAdapterFactory()
        
        self.logger.info("Cross-platform distribution system initialized")
    
    async def create_distribution_campaign(
        self,
        user_id: int,
        content_id: int,
        campaign_config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """        Create comprehensive distribution campaign
        
        Args:
            user_id: User identifier
            content_id: Content identifier
            campaign_config: Campaign configuration
            
        Returns:
            Campaign creation result with job details
        """        try:
            self.logger.info(f"Creating distribution campaign for user {user_id}")
            
            # Extract campaign parameters
            campaign_name = campaign_config.get("name", f"Campaign_{content_id}")
            target_platforms = campaign_config.get("platforms", [])
            content_format = campaign_config.get("content_format", ContentFormat.AUDIO)
            content_title = campaign_config.get("title", "")
            content_description = campaign_config.get("description")
            optimization_goals = campaign_config.get("optimization_goals", [])
            scheduling_strategy = campaign_config.get("scheduling_strategy", SchedulingStrategy.BALANCED_DISTRIBUTION)
            
            # Step 1: Content Optimization
            optimization_result = None
            if optimization_goals:
                optimization_request = OptimizationRequest(
                    content_id=str(content_id),
                    content_type=ContentType(campaign_config.get("content_type", "music_track")),
                    target_platforms=[PlatformTarget(p) for p in target_platforms],
                    original_title=content_title,
                    original_description=content_description,
                    optimization_goals=optimization_goals
                )
                
                optimization_result = await self.content_optimizer.optimize_content(
                    optimization_request
                )
            
            # Step 2: Scheduling Optimization
            scheduling_result = None
            if campaign_config.get("enable_scheduling", True):
                preferred_date_range = campaign_config.get("date_range")
                if preferred_date_range:
                    scheduling_request = SchedulingRequest(
                        content_id=str(content_id),
                        target_platforms=target_platforms,
                        content_type=campaign_config.get("content_type", "music_track"),
                        target_audience=AudienceSegment(campaign_config.get("target_audience", "global")),
                        preferred_date_range=preferred_date_range,
                        strategy=scheduling_strategy
                    )
                    
                    scheduling_result = await self.scheduling_engine.optimize_schedule(
                        scheduling_request
                    )
            
            # Step 3: Create Distribution Job
            distribution_job = await self.distribution_manager.create_distribution_job(
                user_id=user_id,
                content_id=content_id,
                job_name=campaign_name,
                target_platforms=[TargetPlatform(p) for p in target_platforms],
                content_format=content_format,
                content_title=content_title,
                content_description=content_description,
                scheduled_at=scheduling_result.recommended_schedule.get(target_platforms[0]) if scheduling_result else None,
                optimization_strategy=OptimizationStrategy(campaign_config.get("optimization_strategy", "balanced")),
                auto_optimize=campaign_config.get("auto_optimize", True)
            )
            
            # Compile campaign result
            campaign_result = {
                "success": True,
                "campaign_id": distribution_job.job_uuid,
                "distribution_job": {
                    "id": distribution_job.id,
                    "uuid": distribution_job.job_uuid,
                    "status": distribution_job.status,
                    "platforms": distribution_job.target_platforms,
                    "created_at": distribution_job.created_at.isoformat()
                },
                "optimization": {
                    "applied": optimization_result is not None,
                    "seo_score": optimization_result.seo_score if optimization_result else None,
                    "platform_optimizations": optimization_result.platform_optimizations if optimization_result else {}
                },
                "scheduling": {
                    "applied": scheduling_result is not None,
                    "recommended_times": scheduling_result.recommended_schedule if scheduling_result else {},
                    "optimization_score": scheduling_result.optimization_score if scheduling_result else None
                }
            }
            
            self.logger.info(f"Distribution campaign created: {distribution_job.job_uuid}")
            return campaign_result
            
        except Exception as e:
            self.logger.error(f"Failed to create distribution campaign: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "campaign_id": None
            }
    
    async def get_campaign_status(self, campaign_id: str) -> Dict[str, Any]:
        """        Get comprehensive campaign status and analytics
        
        Args:
            campaign_id: Campaign/job UUID
            
        Returns:
            Campaign status with analytics
        """        try:
            # Get distribution job details
            job = await self.distribution_manager.get_distribution_job(campaign_id)
            if not job:
                return {"success": False, "error": "Campaign not found"}
            
            # Collect latest analytics if job is completed
            analytics_data = {}
            if job.status == DistributionStatus.COMPLETED.value:
                analytics_data = await self.analytics_collector.collect_metrics(
                    str(job.content_id),
                    job.target_platforms,
                    AnalyticsTimeframe.DAILY
                )
            
            return {
                "success": True,
                "campaign_id": campaign_id,
                "status": job.status,
                "progress": float(job.progress_percentage),
                "platforms": {
                    "total": len(job.target_platforms),
                    "statuses": job.platform_statuses,
                    "links": job.platform_links or {}
                },
                "performance": {
                    "total_reach": job.total_reach,
                    "total_engagement": job.total_engagement,
                    "total_views": job.total_views,
                    "platform_metrics": job.platform_metrics or {}
                },
                "analytics": {
                    "available": len(analytics_data) > 0,
                    "platforms": list(analytics_data.keys()),
                    "last_updated": datetime.utcnow().isoformat()
                },
                "created_at": job.created_at.isoformat(),
                "completed_at": job.completed_at.isoformat() if job.completed_at else None
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get campaign status: {str(e)}")
            return {"success": False, "error": str(e)}
    
    async def generate_performance_report(
        self,
        content_id: str,
        platforms: List[str],
        timeframe: AnalyticsTimeframe = AnalyticsTimeframe.WEEKLY
    ) -> AnalyticsReport:
        """        Generate comprehensive performance report
        
        Args:
            content_id: Content identifier
            platforms: Platforms to include in report
            timeframe: Report timeframe
            
        Returns:
            Comprehensive analytics report
        """        try:
            end_date = datetime.utcnow()
            
            # Calculate start date based on timeframe
            if timeframe == AnalyticsTimeframe.DAILY:
                start_date = end_date.replace(hour=0, minute=0, second=0, microsecond=0)
            elif timeframe == AnalyticsTimeframe.WEEKLY:
                start_date = end_date - timedelta(days=7)
            elif timeframe == AnalyticsTimeframe.MONTHLY:
                start_date = end_date - timedelta(days=30)
            else:
                start_date = end_date - timedelta(days=1)
            
            report = await self.analytics_collector.generate_analytics_report(
                content_id=content_id,
                platforms=platforms,
                timeframe=timeframe,
                start_date=start_date,
                end_date=end_date
            )
            
            return report
            
        except Exception as e:
            self.logger.error(f"Failed to generate performance report: {str(e)}")
            return AnalyticsReport(
                content_id=content_id,
                report_id="error_report",
                timeframe=timeframe,
                start_date=datetime.utcnow(),
                end_date=datetime.utcnow(),
                platforms=platforms
            )
    
    async def optimize_content_for_platforms(
        self,
        content_data: Dict[str, Any],
        target_platforms: List[str]
    ) -> OptimizationResult:
        """        Optimize content for specific platforms
        
        Args:
            content_data: Content details
            target_platforms: Target platforms
            
        Returns:
            Optimization results
        """        try:
            optimization_request = OptimizationRequest(
                content_id=content_data.get("id", ""),
                content_type=ContentType(content_data.get("type", "music_track")),
                target_platforms=[PlatformTarget(p) for p in target_platforms],
                original_title=content_data.get("title", ""),
                original_description=content_data.get("description"),
                original_tags=content_data.get("tags", []),
                genre=content_data.get("genre"),
                target_audience=content_data.get("target_audience"),
                optimization_goals=[
                    OptimizationType.SEO_KEYWORDS,
                    OptimizationType.HASHTAGS,
                    OptimizationType.ENGAGEMENT_PREDICTION,
                    OptimizationType.PLATFORM_ADAPTATION
                ]
            )
            
            return await self.content_optimizer.optimize_content(optimization_request)
            
        except Exception as e:
            self.logger.error(f"Content optimization failed: {str(e)}")
            return OptimizationResult(
                content_id=content_data.get("id", ""),
                success=False,
                warnings=[f"Optimization failed: {str(e)}"]
            )
    
    async def get_platform_adapter(
        self,
        platform_name: str,
        credentials: PlatformCredentials
    ) -> Optional[BasePlatformAdapter]:
        """        Get platform adapter instance
        
        Args:
            platform_name: Platform name
            credentials: Platform credentials
            
        Returns:
            Platform adapter instance
        """        try:
            return self.adapter_factory.create_adapter(platform_name, credentials)
        except Exception as e:
            self.logger.error(f"Failed to create platform adapter: {str(e)}")
            return None
    
    async def get_supported_platforms(self) -> List[str]:
        """Get list of supported platforms"""        return self.adapter_factory.get_supported_platforms()
    
    async def validate_platform_credentials(
        self,
        platform_name: str,
        credentials: PlatformCredentials
    ) -> bool:
        """        Validate platform credentials
        
        Args:
            platform_name: Platform name
            credentials: Platform credentials
            
        Returns:
            True if credentials are valid
        """        try:
            adapter = await self.get_platform_adapter(platform_name, credentials)
            if not adapter:
                return False
            
            async with adapter:
                return await adapter.authenticate()
            
        except Exception as e:
            self.logger.error(f"Credential validation failed: {str(e)}")
            return False
    
    def get_system_health(self) -> Dict[str, Any]:
        """Get system health status"""        return {
            "status": "healthy",
            "components": {
                "distribution_manager": "operational",
                "content_optimizer": "operational",
                "scheduling_engine": "operational",
                "analytics_collector": "operational",
                "platform_adapters": "operational"
            },
            "supported_platforms": len(self.adapter_factory.get_supported_platforms()),
            "database_connected": self.db_session is not None,
            "last_check": datetime.utcnow().isoformat()
        }

# Convenience function for system initialization
def create_distribution_system(
    db_session=None,
    config: Optional[Dict[str, Any]] = None
) -> CrossPlatformDistributionSystem:
    """    Create and initialize cross-platform distribution system
    
    Args:
        db_session: Database session
        config: System configuration
        
    Returns:
        Initialized distribution system
    """    return CrossPlatformDistributionSystem(db_session, config)

# Export all public classes and functions
__all__ = [
    # Main system class
    "CrossPlatformDistributionSystem",
    "create_distribution_system",
    
    # Core managers
    "CrossPlatformDistributionManager",
    "ContentOptimizer",
    "SchedulingEngine",
    "AnalyticsCollector",
    
    # Platform adapters
    "BasePlatformAdapter",
    "YouTubeAdapter",
    "SpotifyAdapter", 
    "InstagramAdapter",
    "PlatformAdapterFactory",
    
    # Data models
    "DistributionJob",
    "DistributionTemplate",
    "ScheduleTemplate",
    "PerformanceHistory",
    "MetricsModel",
    "AnalyticsSnapshot",
    
    # Request/Response models
    "OptimizationRequest",
    "OptimizationResult",
    "SchedulingRequest",
    "SchedulingResult",
    "AnalyticsReport",
    "MetricData",
    "PlatformCredentials",
    "UploadResult",
    "ContentMetadata",
    "TimeSlot",
    "PlatformConstraints",
    
    # Enums
    "DistributionStatus",
    "DistributionPriority",
    "ContentFormat",
    "TargetPlatform",
    "OptimizationStrategy",
    "OptimizationType",
    "ContentType",
    "PlatformTarget",
    "SchedulingStrategy",
    "TimeSlotPriority",
    "AudienceSegment",
    "MetricType",
    "AnalyticsTimeframe",
    "DataSource",
    "PlatformType",
    "AuthenticationType",
    "UploadStatus"
]
