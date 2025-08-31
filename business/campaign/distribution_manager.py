"""
Distribution Manager - Multi-Platform Content Distribution System
================================================================

Advanced content distribution system for automated multi-platform publishing,
scheduling, optimization, and performance tracking across social media platforms.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: © 2025 Fahed Mlaiel. All rights reserved.

WARNING: This code is protected by copyright law. Unauthorized use, reproduction,
or distribution without explicit written permission from Fahed Mlaiel is strictly
prohibited and may result in legal action.
"""

from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Set
from enum import Enum
from dataclasses import dataclass
import asyncio
import json

from backend.core.logging import get_logger
from backend.ai.content.content_optimizer import ContentOptimizer
from backend.ai.ml.scheduling_optimizer import SchedulingOptimizer
from backend.ai.nlp.hashtag_generator import HashtagGenerator
from backend.business.analytics.distribution_analyzer import DistributionAnalyzer
from backend.integrations.platform_apis import PlatformAPIManager
from backend.integrations.social_media import SocialMediaManager
from backend.utils.content_formatter import ContentFormatter


class Platform(str, Enum):
    """Supported distribution platforms"""
    YOUTUBE = "youtube"
    INSTAGRAM = "instagram"
    TIKTOK = "tiktok"
    TWITTER = "twitter"
    FACEBOOK = "facebook"
    LINKEDIN = "linkedin"
    PINTEREST = "pinterest"
    SNAPCHAT = "snapchat"
    SPOTIFY = "spotify"
    APPLE_MUSIC = "apple_music"
    SOUNDCLOUD = "soundcloud"
    TWITCH = "twitch"


class DistributionStatus(str, Enum):
    """Distribution status states"""
    PENDING = "pending"
    SCHEDULED = "scheduled"
    PUBLISHING = "publishing"
    PUBLISHED = "published"
    FAILED = "failed"
    CANCELLED = "cancelled"
    ARCHIVED = "archived"


class ContentAdaptation(str, Enum):
    """Content adaptation types"""
    RESIZE_VIDEO = "resize_video"
    CROP_IMAGE = "crop_image"
    TRUNCATE_TEXT = "truncate_text"
    GENERATE_PREVIEW = "generate_preview"
    ADD_WATERMARK = "add_watermark"
    OPTIMIZE_QUALITY = "optimize_quality"
    ADD_CAPTIONS = "add_captions"
    GENERATE_THUMBNAIL = "generate_thumbnail"


@dataclass
class PlatformConfiguration:
    """Platform-specific configuration"""
    platform: Platform
    enabled: bool
    account_id: str
    publishing_settings: Dict[str, Any]
    content_adaptations: List[ContentAdaptation]
    scheduling_preferences: Dict[str, Any]
    hashtag_strategy: Dict[str, Any]
    engagement_settings: Dict[str, Any]


@dataclass
class DistributionSchedule:
    """Content distribution schedule"""
    content_id: str
    platform_schedules: Dict[Platform, datetime]
    timezone: str
    repeat_schedule: Optional[Dict[str, Any]] = None
    priority: int = 5
    dependencies: Optional[List[str]] = None


@dataclass
class DistributionResult:
    """Distribution execution result"""
    distribution_id: str
    content_id: str
    platform: Platform
    status: DistributionStatus
    published_url: Optional[str]
    published_at: Optional[datetime]
    engagement_metrics: Dict[str, Any]
    error_message: Optional[str] = None
    retry_count: int = 0


@dataclass
class DistributionMetrics:
    """Distribution performance metrics"""
    total_distributions: int
    successful_distributions: int
    failed_distributions: int
    success_rate: float
    average_engagement: Dict[str, float]
    reach_metrics: Dict[str, int]
    platform_performance: Dict[Platform, Dict[str, Any]]


class DistributionManager:
    """
    Advanced Multi-Platform Content Distribution System
    
    Provides comprehensive content distribution capabilities including
    automated multi-platform publishing, intelligent scheduling,
    content optimization, and performance analytics.
    """
    
    def __init__(self):
        self.logger = get_logger(__name__)
        self.content_optimizer = ContentOptimizer()
        self.scheduling_optimizer = SchedulingOptimizer()
        self.hashtag_generator = HashtagGenerator()
        self.distribution_analyzer = DistributionAnalyzer()
        self.platform_api_manager = PlatformAPIManager()
        self.social_media_manager = SocialMediaManager()
        self.content_formatter = ContentFormatter()
        
        self._distribution_queue: List[Dict] = []
        self._active_distributions: Dict[str, Dict] = {}
        self._distribution_history: Dict[str, List] = {}
        self._platform_configs: Dict[str, Dict[Platform, PlatformConfiguration]] = {}
        
        # Start distribution workers
        asyncio.create_task(self._distribution_worker())
        asyncio.create_task(self._metrics_collection_worker())
    
    async def setup_campaign_distribution(
        self,
        campaign_id: str,
        creator_id: str,
        platform_configs: List[PlatformConfiguration]
    ) -> Dict[str, Any]:
        """
        Setup multi-platform distribution for campaign
        
        Args:
            campaign_id: Campaign unique identifier
            creator_id: Creator unique identifier
            platform_configs: Platform configuration list
            
        Returns:
            Distribution setup result
        """



        try:
            distribution_setup_id = f"dist_{campaign_id}_{int(datetime.utcnow().timestamp())}"
            
            # Validate platform configurations
            validated_configs = {}
            for config in platform_configs:
                validation_result = await self._validate_platform_config(
                    config, creator_id
                )
                if validation_result["valid"]:
                    validated_configs[config.platform] = config
                else:
                    self.logger.warning(f"Invalid config for {config.platform}: {validation_result['errors']}")
            
            # Setup platform connections
            connection_results = {}
            for platform, config in validated_configs.items():
                connection_result = await self.platform_api_manager.setup_platform_connection(
                    platform, config.account_id, config.publishing_settings
                )
                connection_results[platform.value] = connection_result
            
            # Initialize content adaptation rules
            adaptation_rules = await self._setup_content_adaptations(validated_configs)
            
            # Setup scheduling optimization
            scheduling_config = await self.scheduling_optimizer.setup_campaign_scheduling(
                campaign_id, validated_configs
            )
            
            # Store distribution configuration
            self._platform_configs[campaign_id] = validated_configs
            
            # Initialize distribution tracking
            distribution_tracking = {
                "distribution_setup_id": distribution_setup_id,
                "campaign_id": campaign_id,
                "creator_id": creator_id,
                "platforms": list(validated_configs.keys()),
                "connection_results": connection_results,
                "adaptation_rules": adaptation_rules,
                "scheduling_config": scheduling_config,
                "created_at": datetime.utcnow(),
                "metrics": DistributionMetrics(
                    total_distributions=0,
                    successful_distributions=0,
                    failed_distributions=0,
                    success_rate=0.0,
                    average_engagement={},
                    reach_metrics={},
                    platform_performance={}
                )
            }
            
            self._active_distributions[campaign_id] = distribution_tracking
            
            self.logger.info(f"Campaign distribution setup completed: {distribution_setup_id}")
            
            return {
                "distribution_setup_id": distribution_setup_id,
                "campaign_id": campaign_id,
                "platforms_configured": len(validated_configs),
                "platforms_connected": len([r for r in connection_results.values() if r["connected"]]),
                "adaptation_rules_count": len(adaptation_rules),
                "scheduling_optimization_active": bool(scheduling_config),
                "status": "ready"
            }
            
        except Exception as e:
            self.logger.error(f"Campaign distribution setup failed: {str(e)}")
            raise
    
    async def distribute_content(
        self,
        campaign_id: str,
        content_id: str,
        content_data: Dict[str, Any],
        distribution_schedule: Optional[DistributionSchedule] = None,
        immediate_publish: bool = False
    ) -> Dict[str, Any]:
        """
        Distribute content across configured platforms
        
        Args:
            campaign_id: Campaign unique identifier
            content_id: Content unique identifier
            content_data: Content data and metadata
            distribution_schedule: Optional custom schedule
            immediate_publish: Whether to publish immediately
            
        Returns:
            Distribution execution result
        """



        try:
            if campaign_id not in self._active_distributions:
                raise ValueError(f"Campaign distribution not configured: {campaign_id}")
            
            distribution_config = self._active_distributions[campaign_id]
            platform_configs = self._platform_configs[campaign_id]
            
            distribution_id = f"pub_{content_id}_{int(datetime.utcnow().timestamp())}"
            
            # Optimize distribution schedule if not provided
            if not distribution_schedule:
                distribution_schedule = await self._optimize_distribution_schedule(
                    campaign_id, content_data, platform_configs
                )
            
            # Prepare content for each platform
            platform_content = {}
            for platform, config in platform_configs.items():
                adapted_content = await self._adapt_content_for_platform(
                    content_data, platform, config
                )
                platform_content[platform] = adapted_content
            
            # Generate platform-specific metadata
            platform_metadata = {}
            for platform in platform_configs.keys():
                metadata = await self._generate_platform_metadata(
                    content_data, platform, platform_configs[platform]
                )
                platform_metadata[platform] = metadata
            
            # Create distribution tasks
            distribution_tasks = []
            for platform, config in platform_configs.items():
                if config.enabled:
                    task_data = {
                        "distribution_id": distribution_id,
                        "content_id": content_id,
                        "platform": platform,
                        "content": platform_content[platform],
                        "metadata": platform_metadata[platform],
                        "config": config,
                        "schedule": distribution_schedule.platform_schedules.get(platform),
                        "immediate": immediate_publish
                    }
                    distribution_tasks.append(task_data)
            
            # Queue or execute distribution tasks
            if immediate_publish:
                results = await self._execute_immediate_distribution(distribution_tasks)
            else:
                results = await self._queue_scheduled_distribution(distribution_tasks)
            
            # Track distribution
            distribution_record = {
                "distribution_id": distribution_id,
                "campaign_id": campaign_id,
                "content_id": content_id,
                "platforms": list(platform_configs.keys()),
                "schedule": distribution_schedule,
                "tasks": distribution_tasks,
                "results": results,
                "status": "executed" if immediate_publish else "scheduled",
                "created_at": datetime.utcnow()
            }
            
            # Store distribution record
            if campaign_id not in self._distribution_history:
                self._distribution_history[campaign_id] = []
            self._distribution_history[campaign_id].append(distribution_record)
            
            return {
                "distribution_id": distribution_id,
                "content_id": content_id,
                "platforms_targeted": len(distribution_tasks),
                "immediate_publish": immediate_publish,
                "execution_results": results,
                "status": distribution_record["status"],
                "estimated_reach": await self._estimate_distribution_reach(distribution_tasks)
            }
            
        except Exception as e:
            self.logger.error(f"Content distribution failed: {str(e)}")
            raise
    
    async def optimize_distribution_timing(
        self,
        campaign_id: str,
        content_data: Dict[str, Any],
        optimization_goals: List[str]
    ) -> Dict[str, Any]:
        """
        Optimize content distribution timing using AI
        
        Args:
            campaign_id: Campaign unique identifier
            content_data: Content data for optimization
            optimization_goals: Optimization objectives
            
        Returns:
            Optimized distribution timing recommendations
        """



        try:
            if campaign_id not in self._active_distributions:
                raise ValueError(f"Campaign distribution not configured: {campaign_id}")
            
            distribution_config = self._active_distributions[campaign_id]
            platform_configs = self._platform_configs[campaign_id]
            
            # Analyze audience engagement patterns
            audience_analysis = await self._analyze_audience_patterns(
                campaign_id, platform_configs.keys()
            )
            
            # Get platform-specific optimal times
            platform_optimal_times = {}
            for platform in platform_configs.keys():
                optimal_times = await self.scheduling_optimizer.get_optimal_times(
                    platform, audience_analysis, optimization_goals
                )
                platform_optimal_times[platform.value] = optimal_times
            
            # Consider content type and performance history
            content_analysis = await self._analyze_content_timing_performance(
                campaign_id, content_data
            )
            
            # Generate optimized schedule
            optimized_schedule = await self.scheduling_optimizer.optimize_multi_platform_schedule(
                platform_optimal_times,
                content_analysis,
                optimization_goals
            )
            
            # Calculate expected performance
            performance_predictions = await self._predict_distribution_performance(
                optimized_schedule, content_data, platform_configs
            )
            
            return {
                "campaign_id": campaign_id,
                "optimization_goals": optimization_goals,
                "audience_analysis": audience_analysis,
                "platform_optimal_times": platform_optimal_times,
                "optimized_schedule": {
                    platform.value: schedule.isoformat() if isinstance(schedule, datetime) else schedule
                    for platform, schedule in optimized_schedule.items()
                },
                "performance_predictions": performance_predictions,
                "optimization_confidence": performance_predictions.get("confidence_score", 0.8)
            }
            
        except Exception as e:
            self.logger.error(f"Distribution timing optimization failed: {str(e)}")
            raise
    
    async def track_distribution_performance(
        self,
        campaign_id: str,
        content_id: Optional[str] = None,
        platform: Optional[Platform] = None,
        timeframe_days: int = 30
    ) -> Dict[str, Any]:
        """
        Track and analyze distribution performance
        
        Args:
            campaign_id: Campaign unique identifier
            content_id: Optional specific content to analyze
            platform: Optional specific platform to analyze
            timeframe_days: Analysis timeframe
            
        Returns:
            Distribution performance analytics
        """



        try:
            if campaign_id not in self._active_distributions:
                raise ValueError(f"Campaign distribution not configured: {campaign_id}")
            
            # Define analysis scope
            end_date = datetime.utcnow()
            start_date = end_date - timedelta(days=timeframe_days)
            
            # Collect performance data
            performance_data = await self._collect_distribution_performance_data(
                campaign_id, content_id, platform, start_date, end_date
            )
            
            # Analyze performance trends
            performance_trends = await self.distribution_analyzer.analyze_performance_trends(
                performance_data, timeframe_days
            )
            
            # Calculate engagement metrics
            engagement_metrics = await self._calculate_engagement_metrics(
                performance_data, platform
            )
            
            # Analyze platform effectiveness
            platform_analysis = await self._analyze_platform_effectiveness(
                performance_data, campaign_id
            )
            
            # Generate performance insights
            performance_insights = await self._generate_performance_insights(
                performance_data, performance_trends, platform_analysis
            )
            
            return {
                "campaign_id": campaign_id,
                "analysis_period": {
                    "start_date": start_date.isoformat(),
                    "end_date": end_date.isoformat(),
                    "days": timeframe_days
                },
                "scope": {
                    "content_id": content_id,
                    "platform": platform.value if platform else "all",
                    "total_distributions": len(performance_data)
                },
                "performance_summary": {
                    "total_reach": sum(d.get("reach", 0) for d in performance_data),
                    "total_engagement": sum(d.get("engagement", 0) for d in performance_data),
                    "average_engagement_rate": engagement_metrics.get("average_rate", 0),
                    "success_rate": len([d for d in performance_data if d.get("status") == "success"]) / len(performance_data) if performance_data else 0
                },
                "performance_trends": performance_trends,
                "engagement_metrics": engagement_metrics,
                "platform_analysis": platform_analysis,
                "insights": performance_insights,
                "recommendations": await self._generate_distribution_recommendations(
                    performance_data, performance_insights
                )
            }
            
        except Exception as e:
            self.logger.error(f"Distribution performance tracking failed: {str(e)}")
            raise
    
    async def manage_platform_connections(
        self,
        campaign_id: str,
        action: str,
        platform_data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Manage platform connections for campaign distribution
        
        Args:
            campaign_id: Campaign unique identifier
            action: Management action (add, remove, update, test)
            platform_data: Platform-specific data
            
        Returns:
            Platform connection management result
        """



        try:
            if campaign_id not in self._active_distributions:
                raise ValueError(f"Campaign distribution not configured: {campaign_id}")
            
            platform_configs = self._platform_configs[campaign_id]
            
            if action == "add":
                if not platform_data or "platform" not in platform_data:
                    raise ValueError("Platform data required for add action")
                
                platform = Platform(platform_data["platform"])
                config = PlatformConfiguration(
                    platform=platform,
                    enabled=platform_data.get("enabled", True),
                    account_id=platform_data["account_id"],
                    publishing_settings=platform_data.get("publishing_settings", {}),
                    content_adaptations=platform_data.get("content_adaptations", []),
                    scheduling_preferences=platform_data.get("scheduling_preferences", {}),
                    hashtag_strategy=platform_data.get("hashtag_strategy", {}),
                    engagement_settings=platform_data.get("engagement_settings", {})
                )
                
                # Test connection
                connection_test = await self.platform_api_manager.test_platform_connection(
                    platform, config.account_id, config.publishing_settings
                )
                
                if connection_test["success"]:
                    platform_configs[platform] = config
                    
                    return {
                        "campaign_id": campaign_id,
                        "action": "added",
                        "platform": platform.value,
                        "connection_status": "connected",
                        "config": config.__dict__
                    }
                else:
                    return {
                        "campaign_id": campaign_id,
                        "action": "failed",
                        "platform": platform.value,
                        "error": connection_test["error"]
                    }
            
            elif action == "remove":
                platform = Platform(platform_data["platform"])
                if platform in platform_configs:
                    del platform_configs[platform]
                    
                    return {
                        "campaign_id": campaign_id,
                        "action": "removed",
                        "platform": platform.value
                    }
                else:
                    raise ValueError(f"Platform not configured: {platform.value}")
            
            elif action == "test":
                test_results = {}
                platforms_to_test = [Platform(platform_data["platform"])] if platform_data and "platform" in platform_data else list(platform_configs.keys())
                
                for platform in platforms_to_test:
                    if platform in platform_configs:
                        config = platform_configs[platform]
                        test_result = await self.platform_api_manager.test_platform_connection(
                            platform, config.account_id, config.publishing_settings
                        )
                        test_results[platform.value] = test_result
                
                return {
                    "campaign_id": campaign_id,
                    "action": "tested",
                    "test_results": test_results
                }
            
            elif action == "list":
                return {
                    "campaign_id": campaign_id,
                    "platforms": {
                        platform.value: {
                            "enabled": config.enabled,
                            "account_id": config.account_id,
                            "last_used": "2025-08-13T10:00:00Z"  # Would be tracked in real implementation
                        }
                        for platform, config in platform_configs.items()
                    }
                }
            
            else:
                raise ValueError(f"Unknown action: {action}")
                
        except Exception as e:
            self.logger.error(f"Platform connection management failed: {str(e)}")
            raise
    
    # Private helper methods
    
    async def _distribution_worker(self) -> None:
        """Background distribution worker"""
        while True:
            try:
                await self._process_distribution_queue()
                await asyncio.sleep(60)  # Process every minute
                
            except Exception as e:
                self.logger.error(f"Distribution worker error: {str(e)}")
                await asyncio.sleep(120)
    
    async def _metrics_collection_worker(self) -> None:
        """Background metrics collection worker"""
        while True:
            try:
                await self._collect_platform_metrics()
                await asyncio.sleep(1800)  # Collect every 30 minutes
                
            except Exception as e:
                self.logger.error(f"Metrics collection worker error: {str(e)}")
                await asyncio.sleep(1800)
    
    async def _validate_platform_config(
        self,
        config: PlatformConfiguration,
        creator_id: str
    ) -> Dict[str, Any]:
        """Validate platform configuration"""
        # Implementation would validate API credentials, permissions, etc.
        return {"valid": True, "errors": []}
    
    async def _adapt_content_for_platform(
        self,
        content_data: Dict[str, Any],
        platform: Platform,
        config: PlatformConfiguration
    ) -> Dict[str, Any]:
        """Adapt content for specific platform requirements"""
        adapted_content = content_data.copy()
        
        # Apply content adaptations based on platform requirements
        for adaptation in config.content_adaptations:
            adapted_content = await self.content_formatter.apply_adaptation(
                adapted_content, adaptation, platform
            )
        
        return adapted_content
    
    async def _generate_platform_metadata(
        self,
        content_data: Dict[str, Any],
        platform: Platform,
        config: PlatformConfiguration
    ) -> Dict[str, Any]:
        """Generate platform-specific metadata"""
        metadata = {}
        
        # Generate hashtags
        if config.hashtag_strategy:
            hashtags = await self.hashtag_generator.generate_hashtags(
                content_data, platform, config.hashtag_strategy
            )
            metadata["hashtags"] = hashtags
        
        # Generate captions/descriptions
        if content_data.get("description"):
            adapted_description = await self.content_formatter.adapt_description(
                content_data["description"], platform
            )
            metadata["description"] = adapted_description
        
        return metadata
    
    async def _optimize_distribution_schedule(
        self,
        campaign_id: str,
        content_data: Dict[str, Any],
        platform_configs: Dict[Platform, PlatformConfiguration]
    ) -> DistributionSchedule:
        """Optimize distribution schedule for content"""
        optimal_times = await self.scheduling_optimizer.optimize_schedule(
            campaign_id, content_data, list(platform_configs.keys())
        )
        
        return DistributionSchedule(
            content_id=content_data["content_id"],
            platform_schedules=optimal_times,
            timezone="UTC"
        )
