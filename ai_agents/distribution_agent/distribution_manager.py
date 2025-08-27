"""
Advanced Distribution Manager for IA Influencer Agent.
Orchestrates content distribution across ALL platforms with intelligent optimization.

COMPLETE PLATFORM COVERAGE:
✅ Social Media: Instagram, TikTok, YouTube, Facebook, Twitter/X  
✅ Professional: LinkedIn
✅ Visual Discovery: Pinterest
✅ Music Streaming: Spotify
✅ Live Streaming: Twitch  
✅ Community: Discord
✅ Future Ready: Reddit, Telegram, Snapchat, Medium, Behance

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 IA Influencer Agent. All rights reserved.
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
import uuid

from .platform_registry import get_platform_registry, PlatformRegistry
from .models.distribution_models import (
    DistributionRequest, DistributionResult, ContentMetadata,
    PlatformAnalytics, RevenueData
)
from .content_optimizer import ContentOptimizer
from .platform_router import PlatformRouter
from .analytics_aggregator import AnalyticsAggregator
from .revenue_tracker import RevenueTracker
from .utils.exceptions import DistributionError

logger = logging.getLogger(__name__)

@dataclass
class DistributionCampaign:
    """Complete distribution campaign configuration."""
    campaign_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    content_metadata: ContentMetadata = None
    target_platforms: List[str] = field(default_factory=list)
    distribution_schedule: Dict[str, datetime] = field(default_factory=dict)
    budget_allocation: Dict[str, float] = field(default_factory=dict)
    success_metrics: Dict[str, float] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    status: str = "pending"  # pending, running, completed, failed
    results: Dict[str, DistributionResult] = field(default_factory=dict)

class AdvancedDistributionManager:
    """
    Enterprise-grade distribution manager with complete platform coverage.
    Handles intelligent routing, optimization, scheduling, and analytics across all platforms.
    """
    
    def __init__(self):
        self.platform_registry: PlatformRegistry = get_platform_registry()
        self.content_optimizer = ContentOptimizer()
        self.platform_router = PlatformRouter()
        self.analytics_aggregator = AnalyticsAggregator()
        self.revenue_tracker = RevenueTracker()
        
        self.active_campaigns: Dict[str, DistributionCampaign] = {}
        self.platform_credentials: Dict[str, Any] = {}
        
        logger.info("Advanced Distribution Manager initialized with complete platform coverage")
    
    def configure_platform_credentials(self, platform_credentials: Dict[str, Any]):
        """Configure credentials for all platforms."""
        self.platform_credentials.update(platform_credentials)
        
        # Initialize all available adapters
        for platform_name in platform_credentials.keys():
            credentials = platform_credentials[platform_name]
            adapter = self.platform_registry.initialize_adapter(platform_name, credentials)
            if adapter:
                logger.info(f"Successfully configured {platform_name} adapter")
            else:
                logger.warning(f"Failed to configure {platform_name} adapter")
    
    async def create_distribution_campaign(
        self,
        campaign_name: str,
        content_metadata: ContentMetadata,
        target_platforms: Optional[List[str]] = None,
        budget_tier: str = "medium",
        schedule_optimization: bool = True
    ) -> DistributionCampaign:
        """Create a comprehensive distribution campaign across multiple platforms."""
        try:
            # Auto-select platforms if not specified
            if not target_platforms:
                target_platforms = self.platform_registry.get_platform_recommendations(content_metadata)
            
            # Validate platform compatibility
            compatible_platforms = []
            for platform in target_platforms:
                compatibility = self.platform_registry.validate_platform_compatibility(platform, content_metadata)
                if compatibility["compatible"]:
                    compatible_platforms.append(platform)
                else:
                    logger.warning(f"Platform {platform} incompatible: {compatibility['reason']}")
            
            if not compatible_platforms:
                raise DistributionError("No compatible platforms found for content")
            
            # Get distribution strategy
            strategy = self.platform_registry.get_distribution_strategy(content_metadata, budget_tier)
            
            # Optimize content for each platform
            optimized_content = {}
            for platform in compatible_platforms:
                try:
                    optimized = await self.content_optimizer.optimize_for_platform(
                        content_metadata, platform
                    )
                    optimized_content[platform] = optimized
                except Exception as e:
                    logger.error(f"Content optimization failed for {platform}: {e}")
                    optimized_content[platform] = content_metadata  # Use original as fallback
            
            # Generate optimal schedule if requested
            distribution_schedule = {}
            if schedule_optimization:
                for platform in compatible_platforms:
                    optimal_time = await self._calculate_optimal_posting_time(platform, content_metadata)
                    distribution_schedule[platform] = optimal_time
            else:
                # Immediate distribution
                base_time = datetime.now()
                for i, platform in enumerate(compatible_platforms):
                    # Stagger distribution by 5 minutes to avoid rate limits
                    distribution_schedule[platform] = base_time + timedelta(minutes=i*5)
            
            # Create campaign
            campaign = DistributionCampaign(
                name=campaign_name,
                content_metadata=content_metadata,
                target_platforms=compatible_platforms,
                distribution_schedule=distribution_schedule,
                budget_allocation=strategy["budget_allocation"],
                success_metrics=await self._define_success_metrics(compatible_platforms, content_metadata)
            )
            
            self.active_campaigns[campaign.campaign_id] = campaign
            
            logger.info(f"Created distribution campaign '{campaign_name}' for {len(compatible_platforms)} platforms")
            return campaign
            
        except Exception as e:
            logger.error(f"Failed to create distribution campaign: {e}")
            raise DistributionError(f"Campaign creation failed: {e}")
    
    async def execute_campaign(self, campaign_id: str) -> Dict[str, DistributionResult]:
        """Execute distribution campaign across all target platforms."""
        try:
            campaign = self.active_campaigns.get(campaign_id)
            if not campaign:
                raise DistributionError(f"Campaign {campaign_id} not found")
            
            campaign.status = "running"
            results = {}
            
            # Execute distribution on each platform
            tasks = []
            for platform in campaign.target_platforms:
                task = self._distribute_to_platform(
                    platform,
                    campaign.content_metadata,
                    campaign.distribution_schedule.get(platform, datetime.now())
                )
                tasks.append((platform, task))
            
            # Wait for all distributions to complete
            for platform, task in tasks:
                try:
                    result = await task
                    results[platform] = result
                    
                    if result.success:
                        logger.info(f"Successfully distributed to {platform}: {result.url}")
                    else:
                        logger.error(f"Distribution failed for {platform}: {result.error}")
                        
                except Exception as e:
                    logger.error(f"Distribution to {platform} failed: {e}")
                    results[platform] = DistributionResult(
                        success=False,
                        platform=platform,
                        error=str(e)
                    )
            
            # Update campaign results
            campaign.results = results
            campaign.status = "completed" if any(r.success for r in results.values()) else "failed"
            
            # Start analytics tracking
            await self._start_analytics_tracking(campaign_id, results)
            
            logger.info(f"Campaign {campaign_id} execution completed: {len([r for r in results.values() if r.success])}/{len(results)} successful")
            return results
            
        except Exception as e:
            logger.error(f"Campaign execution failed: {e}")
            if campaign_id in self.active_campaigns:
                self.active_campaigns[campaign_id].status = "failed"
            raise DistributionError(f"Campaign execution failed: {e}")
    
    async def _distribute_to_platform(
        self,
        platform_name: str,
        content_metadata: ContentMetadata,
        scheduled_time: datetime
    ) -> DistributionResult:
        """Distribute content to a specific platform."""
        try:
            # Get platform adapter
            adapter = self.platform_registry.get_adapter(platform_name)
            if not adapter:
                credentials = self.platform_credentials.get(platform_name)
                if not credentials:
                    raise DistributionError(f"No credentials configured for {platform_name}")
                
                adapter = self.platform_registry.initialize_adapter(platform_name, credentials)
                if not adapter:
                    raise DistributionError(f"Failed to initialize {platform_name} adapter")
            
            # Wait for scheduled time if in future
            if scheduled_time > datetime.now():
                wait_seconds = (scheduled_time - datetime.now()).total_seconds()
                if wait_seconds > 0:
                    logger.info(f"Waiting {wait_seconds:.0f} seconds for {platform_name} distribution")
                    await asyncio.sleep(wait_seconds)
            
            # Optimize content for platform
            optimized_content = await self.content_optimizer.optimize_for_platform(
                content_metadata, platform_name
            )
            
            # Create distribution request
            distribution_request = DistributionRequest(
                content_metadata=optimized_content,
                target_platform=platform_name,
                user_id="system",  # This would come from the actual user context
                priority="normal"
            )
            
            # Execute distribution
            result = await adapter.upload_content(distribution_request)
            
            return result
            
        except Exception as e:
            logger.error(f"Platform distribution failed for {platform_name}: {e}")
            return DistributionResult(
                success=False,
                platform=platform_name,
                error=str(e)
            )
    
    async def _calculate_optimal_posting_time(
        self,
        platform_name: str,
        content_metadata: ContentMetadata
    ) -> datetime:
        """Calculate optimal posting time for platform based on audience analytics."""
        try:
            # This would use historical analytics data to determine optimal times
            # For now, using platform-specific best practices
            
            optimal_hours = {
                "instagram": [11, 13, 17],  # 11am, 1pm, 5pm
                "facebook": [9, 13, 15],    # 9am, 1pm, 3pm  
                "twitter": [9, 12, 17],     # 9am, 12pm, 5pm
                "linkedin": [9, 12, 17],    # Business hours
                "youtube": [14, 17, 20],    # 2pm, 5pm, 8pm
                "tiktok": [18, 19, 20],     # 6pm, 7pm, 8pm
                "pinterest": [20, 21, 22],  # 8pm, 9pm, 10pm
                "spotify": [17, 19, 21],    # Evening listening times
                "twitch": [19, 20, 21],     # Prime streaming hours
                "discord": [18, 19, 20]     # Community active hours
            }
            
            platform_hours = optimal_hours.get(platform_name, [12, 15, 18])  # Default
            
            # Select next available optimal hour
            now = datetime.now()
            today = now.date()
            
            for hour in platform_hours:
                optimal_time = datetime.combine(today, datetime.min.time().replace(hour=hour))
                if optimal_time > now:
                    return optimal_time
            
            # If all today's optimal times have passed, use tomorrow's first slot
            tomorrow = today + timedelta(days=1)
            return datetime.combine(tomorrow, datetime.min.time().replace(hour=platform_hours[0]))
            
        except Exception as e:
            logger.error(f"Failed to calculate optimal time for {platform_name}: {e}")
            # Return immediate distribution as fallback
            return datetime.now() + timedelta(minutes=5)
    
    async def _define_success_metrics(
        self,
        platforms: List[str],
        content_metadata: ContentMetadata
    ) -> Dict[str, float]:
        """Define success metrics for the campaign."""
        # Base metrics that apply to all platforms
        base_metrics = {
            "total_reach": 10000,        # Total reach across all platforms
            "engagement_rate": 5.0,      # Minimum 5% engagement rate
            "total_revenue": 100.0,      # Minimum $100 revenue
            "successful_platforms": len(platforms) * 0.7  # 70% platform success rate
        }
        
        # Platform-specific adjustments based on content type
        content_type = getattr(content_metadata, 'content_type', 'text').lower()
        
        if content_type == "video":
            base_metrics.update({
                "video_completion_rate": 60.0,  # 60% completion rate
                "video_shares": 100            # Minimum 100 shares
            })
        elif content_type == "audio":
            base_metrics.update({
                "audio_plays": 1000,           # Minimum 1000 plays
                "audio_saves": 50              # Minimum 50 saves/playlists
            })
        
        return base_metrics
    
    async def _start_analytics_tracking(
        self,
        campaign_id: str,
        distribution_results: Dict[str, DistributionResult]
    ):
        """Start tracking analytics for successful distributions."""
        try:
            for platform, result in distribution_results.items():
                if result.success:
                    # Start tracking analytics for this content
                    await self.analytics_aggregator.start_tracking(
                        platform=platform,
                        content_id=result.content_id,
                        campaign_id=campaign_id
                    )
                    
                    # Start revenue tracking if platform supports monetization
                    platform_config = self.platform_registry.get_platform_config(platform)
                    if platform_config and platform_config.monetization_available:
                        await self.revenue_tracker.start_tracking(
                            platform=platform,
                            content_id=result.content_id,
                            campaign_id=campaign_id
                        )
            
            logger.info(f"Started analytics tracking for campaign {campaign_id}")
            
        except Exception as e:
            logger.error(f"Failed to start analytics tracking: {e}")
    
    async def get_campaign_analytics(self, campaign_id: str) -> Dict[str, Any]:
        """Get comprehensive analytics for a campaign."""
        try:
            campaign = self.active_campaigns.get(campaign_id)
            if not campaign:
                raise DistributionError(f"Campaign {campaign_id} not found")
            
            analytics = {
                "campaign_info": {
                    "id": campaign.campaign_id,
                    "name": campaign.name,
                    "status": campaign.status,
                    "platforms": campaign.target_platforms,
                    "created_at": campaign.created_at.isoformat()
                },
                "platform_results": {},
                "aggregated_metrics": {
                    "total_reach": 0,
                    "total_engagement": 0,
                    "total_revenue": 0.0,
                    "successful_platforms": 0,
                    "average_engagement_rate": 0.0
                }
            }
            
            total_reach = 0
            total_engagement = 0
            total_revenue = 0.0
            successful_platforms = 0
            
            # Collect analytics from each platform
            for platform, result in campaign.results.items():
                if result.success:
                    try:
                        # Get platform analytics
                        platform_analytics = await self.analytics_aggregator.get_platform_analytics(
                            platform, result.content_id
                        )
                        
                        # Get revenue data
                        revenue_data = await self.revenue_tracker.get_revenue_data(
                            platform, result.content_id
                        )
                        
                        analytics["platform_results"][platform] = {
                            "analytics": platform_analytics.dict() if platform_analytics else None,
                            "revenue": revenue_data.dict() if revenue_data else None,
                            "distribution_result": result.dict()
                        }
                        
                        # Aggregate metrics
                        if platform_analytics:
                            total_reach += platform_analytics.reach
                            total_engagement += (platform_analytics.likes + platform_analytics.comments + platform_analytics.shares)
                            successful_platforms += 1
                        
                        if revenue_data:
                            total_revenue += revenue_data.net_revenue
                            
                    except Exception as e:
                        logger.error(f"Failed to get analytics for {platform}: {e}")
                        analytics["platform_results"][platform] = {
                            "error": str(e),
                            "distribution_result": result.dict()
                        }
            
            # Update aggregated metrics
            analytics["aggregated_metrics"].update({
                "total_reach": total_reach,
                "total_engagement": total_engagement,
                "total_revenue": total_revenue,
                "successful_platforms": successful_platforms,
                "average_engagement_rate": (total_engagement / total_reach * 100) if total_reach > 0 else 0.0
            })
            
            return analytics
            
        except Exception as e:
            logger.error(f"Failed to get campaign analytics: {e}")
            raise DistributionError(f"Analytics retrieval failed: {e}")
    
    async def get_platform_performance_summary(self) -> Dict[str, Any]:
        """Get performance summary across all platforms."""
        try:
            summary = {
                "platform_stats": {},
                "total_campaigns": len(self.active_campaigns),
                "registry_stats": self.platform_registry.get_platform_statistics()
            }
            
            # Aggregate performance across all campaigns
            platform_performance = {}
            
            for campaign in self.active_campaigns.values():
                for platform, result in campaign.results.items():
                    if platform not in platform_performance:
                        platform_performance[platform] = {
                            "total_distributions": 0,
                            "successful_distributions": 0,
                            "total_reach": 0,
                            "total_revenue": 0.0
                        }
                    
                    platform_performance[platform]["total_distributions"] += 1
                    if result.success:
                        platform_performance[platform]["successful_distributions"] += 1
            
            # Calculate success rates
            for platform, stats in platform_performance.items():
                if stats["total_distributions"] > 0:
                    stats["success_rate"] = (stats["successful_distributions"] / stats["total_distributions"]) * 100
                else:
                    stats["success_rate"] = 0.0
            
            summary["platform_stats"] = platform_performance
            
            return summary
            
        except Exception as e:
            logger.error(f"Failed to get platform performance summary: {e}")
            return {"error": str(e)}
    
    async def optimize_future_distributions(self, content_metadata: ContentMetadata) -> Dict[str, Any]:
        """Get AI-powered recommendations for optimizing future distributions."""
        try:
            recommendations = {
                "recommended_platforms": [],
                "optimal_timing": {},
                "content_optimizations": {},
                "budget_recommendations": {},
                "expected_performance": {}
            }
            
            # Get platform recommendations
            recommended_platforms = self.platform_registry.get_platform_recommendations(content_metadata)
            recommendations["recommended_platforms"] = recommended_platforms[:5]  # Top 5
            
            # Get optimal timing for each platform
            for platform in recommended_platforms[:5]:
                optimal_time = await self._calculate_optimal_posting_time(platform, content_metadata)
                recommendations["optimal_timing"][platform] = optimal_time.isoformat()
            
            # Get content optimization suggestions
            for platform in recommended_platforms[:3]:  # Top 3 for detailed optimization
                try:
                    optimized = await self.content_optimizer.get_optimization_suggestions(
                        content_metadata, platform
                    )
                    recommendations["content_optimizations"][platform] = optimized
                except Exception as e:
                    logger.warning(f"Content optimization suggestion failed for {platform}: {e}")
            
            # Budget recommendations based on platform performance
            strategy = self.platform_registry.get_distribution_strategy(content_metadata, "medium")
            recommendations["budget_recommendations"] = strategy["budget_allocation"]
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Failed to generate optimization recommendations: {e}")
            return {"error": str(e)}

# Create global instance
distribution_manager = AdvancedDistributionManager()
