"""
IA Chérie Platform - Multi-Platform Distribution Tracer Enterprise
==============================================================

Advanced multi-platform distribution tracing system for monitoring cross-platform sync,
content distribution tracking, social media API tracing, platform integration correlation,
and global distribution analytics with intelligent optimization.

Features:
- Cross-platform sync tracing with real-time conflict detection
- Content distribution tracking with performance analytics per platform
- Social media API tracing with rate limit optimization
- Platform integration correlation with failure prediction
- Global distribution analytics with audience insights
- Content adaptation tracking for platform-specific optimization
- Automated distribution workflow orchestration

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️ AVERTISSEMENT LÉGAL:
==========================================
© 2025 Fahed Mlaiel <mlaiel@live.de>
TOUS DROITS RÉSERVÉS

🚨 PROTECTION INTELLECTUELLE:
- Code propriétaire de Fahed Mlaiel
- Utilisation commerciale INTERDITE sans autorisation écrite
- Reverse engineering STRICTEMENT INTERDIT
- Distribution INTERDITE sans licence explicite
- Violation = Poursuites judiciaires automatiques
"""

import asyncio
import uuid
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple, Union, Set
from dataclasses import dataclass, field
from enum import Enum
import json
import statistics
from collections import defaultdict, deque
import numpy as np

from . import SpanType, TraceSpan, DistributedTrace, enterprise_tracing_system

logger = logging.getLogger(__name__)

class PlatformType(Enum):
    """Supported social media platforms for distribution."""
    INSTAGRAM = "instagram"
    TIKTOK = "tiktok"
    YOUTUBE = "youtube"
    TWITTER = "twitter"
    FACEBOOK = "facebook"
    LINKEDIN = "linkedin"
    SNAPCHAT = "snapchat"
    PINTEREST = "pinterest"
    TWITCH = "twitch"
    SPOTIFY = "spotify"
    APPLE_MUSIC = "apple_music"
    SOUNDCLOUD = "soundcloud"

class DistributionStage(Enum):
    """Distribution workflow stages."""
    CONTENT_PREPARATION = "content_preparation"
    PLATFORM_ADAPTATION = "platform_adaptation"
    SCHEDULING = "scheduling"
    PUBLISHING = "publishing"
    MONITORING = "monitoring"
    ENGAGEMENT_TRACKING = "engagement_tracking"
    PERFORMANCE_ANALYSIS = "performance_analysis"
    OPTIMIZATION = "optimization"

class DistributionStatus(Enum):
    """Distribution status tracking."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    PUBLISHED = "published"
    FAILED = "failed"
    SCHEDULED = "scheduled"
    CANCELLED = "cancelled"

@dataclass
class PlatformConfiguration:
    """Platform-specific configuration and requirements."""
    platform: PlatformType
    api_credentials: Dict[str, str] = field(default_factory=dict)
    content_requirements: Dict[str, Any] = field(default_factory=dict)
    rate_limits: Dict[str, int] = field(default_factory=dict)
    audience_insights: Dict[str, Any] = field(default_factory=dict)
    optimal_posting_times: List[str] = field(default_factory=list)
    hashtag_strategy: Dict[str, Any] = field(default_factory=dict)
    engagement_patterns: Dict[str, float] = field(default_factory=dict)

@dataclass
class DistributionMetrics:
    """Comprehensive distribution performance metrics."""
    total_platforms: int = 0
    successful_distributions: int = 0
    failed_distributions: int = 0
    total_reach: int = 0
    total_impressions: int = 0
    total_engagement: int = 0
    cross_platform_engagement_rate: float = 0.0
    platform_performance: Dict[str, Dict[str, float]] = field(default_factory=dict)
    audience_overlap: Dict[str, float] = field(default_factory=dict)
    content_adaptation_scores: Dict[str, float] = field(default_factory=dict)

@dataclass
class DistributionContext:
    """Rich context for multi-platform distribution tracing."""
    distribution_id: str
    content_id: str
    creator_id: str
    campaign_id: Optional[str] = None
    target_platforms: List[PlatformType] = field(default_factory=list)
    content_metadata: Dict[str, Any] = field(default_factory=dict)
    distribution_strategy: str = "simultaneous"
    stage: DistributionStage = DistributionStage.CONTENT_PREPARATION
    status: DistributionStatus = DistributionStatus.PENDING
    platform_configs: Dict[str, PlatformConfiguration] = field(default_factory=dict)
    metrics: DistributionMetrics = field(default_factory=DistributionMetrics)
    distribution_log: List[Dict[str, Any]] = field(default_factory=list)
    scheduled_times: Dict[str, datetime] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)

class MultiPlatformDistributionTracer:
    """
    Enterprise-grade multi-platform distribution tracer for creator content.
    
    Provides comprehensive tracing of cross-platform distribution workflows
    with intelligent optimization, performance analytics, and failure prediction.
    """
    
    def __init__(self, service_name: str = "multi_platform_distribution_tracer"):
        self.service_name = service_name
        self.active_distributions: Dict[str, DistributionContext] = {}
        self.platform_managers: Dict[str, Any] = {}
        self.distribution_optimizer = DistributionOptimizer()
        self.cross_platform_analyzer = CrossPlatformAnalyzer()
        self.api_rate_manager = APIRateLimitManager()
        
    async def trace_content_adaptation(
        self,
        parent_span: TraceSpan,
        distribution_id: str,
        content_data: Dict[str, Any],
        target_platforms: List[PlatformType],
        **kwargs
    ) -> TraceSpan:
        """Trace content adaptation for multiple platforms."""
        
        span = TraceSpan(
            trace_id=parent_span.trace_id,
            span_id=str(uuid.uuid4()),
            parent_id=parent_span.span_id,
            operation_name="content_adaptation_multi_platform",
            service_name=self.service_name,
            span_type=SpanType.CONTENT_PROCESSING,
            start_time=datetime.utcnow(),
            tags={
                "distribution.id": distribution_id,
                "content.type": content_data.get("type", "unknown"),
                "content.format": content_data.get("format", "unknown"),
                "distribution.platform_count": len(target_platforms),
                "distribution.platforms": ",".join([p.value for p in target_platforms]),
                "content.size_mb": content_data.get("size_mb", 0)
            }
        )
        
        try:
            adaptation_results = {}
            
            for platform in target_platforms:
                platform_span = await self._trace_platform_adaptation(
                    span, distribution_id, content_data, platform
                )
                
                adaptation_results[platform.value] = {
                    "span_id": platform_span.span_id,
                    "status": platform_span.status,
                    "adaptation_score": platform_span.tags.get("adaptation.score", 0),
                    "processing_time_ms": platform_span.tags.get("adaptation.processing_time_ms", 0)
                }
            
            # Calculate overall adaptation quality
            adaptation_quality = await self._calculate_adaptation_quality(adaptation_results)
            
            # Update distribution context
            if distribution_id in self.active_distributions:
                distribution = self.active_distributions[distribution_id]
                distribution.stage = DistributionStage.PLATFORM_ADAPTATION
                distribution.metrics.content_adaptation_scores = {
                    platform: result["adaptation_score"] 
                    for platform, result in adaptation_results.items()
                }
                distribution.updated_at = datetime.utcnow()
            
            span.tags.update({
                "adaptation.overall_quality": adaptation_quality,
                "adaptation.successful_platforms": len([r for r in adaptation_results.values() if r["status"] == "success"]),
                "adaptation.failed_platforms": len([r for r in adaptation_results.values() if r["status"] == "error"]),
                "adaptation.avg_processing_time": statistics.mean([r["processing_time_ms"] for r in adaptation_results.values()])
            })
            
            span.status = "success"
            span.end_time = datetime.utcnow()
            
            logger.info(f"Content adaptation completed for {len(target_platforms)} platforms: {distribution_id}")
            
            return span
            
        except Exception as e:
            span.status = "error"
            span.tags["error.type"] = type(e).__name__
            span.tags["error.message"] = str(e)
            span.end_time = datetime.utcnow()
            
            logger.error(f"Content adaptation failed: {distribution_id}, error: {e}")
            raise
    
    async def trace_cross_platform_publishing(
        self,
        parent_span: TraceSpan,
        distribution_id: str,
        publishing_strategy: str = "simultaneous",
        **kwargs
    ) -> TraceSpan:
        """Trace cross-platform publishing workflow."""
        
        span = TraceSpan(
            trace_id=parent_span.trace_id,
            span_id=str(uuid.uuid4()),
            parent_id=parent_span.span_id,
            operation_name="cross_platform_publishing",
            service_name=self.service_name,
            span_type=SpanType.EXTERNAL_API,
            start_time=datetime.utcnow(),
            tags={
                "distribution.id": distribution_id,
                "publishing.strategy": publishing_strategy,
                "publishing.start_time": datetime.utcnow().isoformat()
            }
        )
        
        try:
            if distribution_id not in self.active_distributions:
                raise ValueError(f"Distribution context not found: {distribution_id}")
            
            distribution = self.active_distributions[distribution_id]
            distribution.stage = DistributionStage.PUBLISHING
            distribution.distribution_strategy = publishing_strategy
            
            publishing_results = {}
            
            if publishing_strategy == "simultaneous":
                # Publish to all platforms simultaneously
                publishing_results = await self._execute_simultaneous_publishing(
                    span, distribution
                )
            elif publishing_strategy == "sequential":
                # Publish to platforms sequentially
                publishing_results = await self._execute_sequential_publishing(
                    span, distribution
                )
            elif publishing_strategy == "optimized":
                # Publish using optimized timing for each platform
                publishing_results = await self._execute_optimized_publishing(
                    span, distribution
                )
            
            # Calculate publishing success metrics
            success_rate = len([r for r in publishing_results.values() if r["status"] == "success"]) / len(publishing_results)
            
            # Update distribution metrics
            distribution.metrics.total_platforms = len(publishing_results)
            distribution.metrics.successful_distributions = len([r for r in publishing_results.values() if r["status"] == "success"])
            distribution.metrics.failed_distributions = len([r for r in publishing_results.values() if r["status"] == "error"])
            distribution.status = DistributionStatus.PUBLISHED if success_rate > 0.5 else DistributionStatus.FAILED
            distribution.updated_at = datetime.utcnow()
            
            span.tags.update({
                "publishing.success_rate": success_rate,
                "publishing.successful_platforms": distribution.metrics.successful_distributions,
                "publishing.failed_platforms": distribution.metrics.failed_distributions,
                "publishing.total_platforms": distribution.metrics.total_platforms
            })
            
            span.status = "success"
            span.end_time = datetime.utcnow()
            
            logger.info(f"Cross-platform publishing completed: {distribution_id}, "
                       f"success rate: {success_rate:.2f}")
            
            return span
            
        except Exception as e:
            span.status = "error"
            span.tags["error.type"] = type(e).__name__
            span.tags["error.message"] = str(e)
            span.end_time = datetime.utcnow()
            
            logger.error(f"Cross-platform publishing failed: {distribution_id}, error: {e}")
            raise
    
    async def trace_engagement_monitoring(
        self,
        parent_span: TraceSpan,
        distribution_id: str,
        monitoring_duration: timedelta = timedelta(hours=24),
        **kwargs
    ) -> TraceSpan:
        """Trace engagement monitoring across platforms."""
        
        span = TraceSpan(
            trace_id=parent_span.trace_id,
            span_id=str(uuid.uuid4()),
            parent_id=parent_span.span_id,
            operation_name="engagement_monitoring_cross_platform",
            service_name=self.service_name,
            span_type=SpanType.ANALYTICS,
            start_time=datetime.utcnow(),
            tags={
                "distribution.id": distribution_id,
                "monitoring.duration_hours": monitoring_duration.total_seconds() / 3600,
                "monitoring.start_time": datetime.utcnow().isoformat()
            }
        )
        
        try:
            if distribution_id not in self.active_distributions:
                raise ValueError(f"Distribution context not found: {distribution_id}")
            
            distribution = self.active_distributions[distribution_id]
            distribution.stage = DistributionStage.ENGAGEMENT_TRACKING
            
            # Monitor engagement across all platforms
            engagement_data = await self._collect_cross_platform_engagement(
                distribution, monitoring_duration
            )
            
            # Analyze cross-platform performance
            performance_analysis = await self.cross_platform_analyzer.analyze_performance(
                distribution_id, engagement_data
            )
            
            # Calculate cross-platform engagement metrics
            total_engagement = sum(platform_data.get("total_engagement", 0) 
                                 for platform_data in engagement_data.values())
            total_reach = sum(platform_data.get("reach", 0) 
                            for platform_data in engagement_data.values())
            total_impressions = sum(platform_data.get("impressions", 0) 
                                  for platform_data in engagement_data.values())
            
            cross_platform_engagement_rate = (total_engagement / total_impressions * 100) if total_impressions > 0 else 0
            
            # Update distribution metrics
            distribution.metrics.total_engagement = total_engagement
            distribution.metrics.total_reach = total_reach
            distribution.metrics.total_impressions = total_impressions
            distribution.metrics.cross_platform_engagement_rate = cross_platform_engagement_rate
            distribution.metrics.platform_performance = engagement_data
            distribution.updated_at = datetime.utcnow()
            
            span.tags.update({
                "engagement.total_engagement": total_engagement,
                "engagement.total_reach": total_reach,
                "engagement.total_impressions": total_impressions,
                "engagement.cross_platform_rate": cross_platform_engagement_rate,
                "engagement.best_performing_platform": performance_analysis.get("best_platform"),
                "engagement.worst_performing_platform": performance_analysis.get("worst_platform"),
                "engagement.platform_count": len(engagement_data)
            })
            
            span.status = "success"
            span.end_time = datetime.utcnow()
            
            logger.info(f"Engagement monitoring completed: {distribution_id}, "
                       f"total engagement: {total_engagement}")
            
            return span
            
        except Exception as e:
            span.status = "error"
            span.tags["error.type"] = type(e).__name__
            span.tags["error.message"] = str(e)
            span.end_time = datetime.utcnow()
            
            logger.error(f"Engagement monitoring failed: {distribution_id}, error: {e}")
            raise
    
    async def trace_distribution_optimization(
        self,
        parent_span: TraceSpan,
        distribution_id: str,
        optimization_goals: List[str],
        **kwargs
    ) -> TraceSpan:
        """Trace distribution optimization based on performance data."""
        
        span = TraceSpan(
            trace_id=parent_span.trace_id,
            span_id=str(uuid.uuid4()),
            parent_id=parent_span.span_id,
            operation_name="distribution_optimization",
            service_name=self.service_name,
            span_type=SpanType.AI_ML_PROCESSING,
            start_time=datetime.utcnow(),
            tags={
                "distribution.id": distribution_id,
                "optimization.goals": ",".join(optimization_goals),
                "optimization.goal_count": len(optimization_goals)
            }
        )
        
        try:
            if distribution_id not in self.active_distributions:
                raise ValueError(f"Distribution context not found: {distribution_id}")
            
            distribution = self.active_distributions[distribution_id]
            distribution.stage = DistributionStage.OPTIMIZATION
            
            # Generate optimization recommendations
            optimization_results = await self.distribution_optimizer.optimize_distribution(
                distribution, optimization_goals
            )
            
            # Apply optimization recommendations
            applied_optimizations = await self._apply_optimization_recommendations(
                distribution, optimization_results
            )
            
            # Calculate optimization impact
            optimization_impact = await self._calculate_optimization_impact(
                distribution, applied_optimizations
            )
            
            span.tags.update({
                "optimization.recommendations_count": len(optimization_results.get("recommendations", [])),
                "optimization.applied_count": len(applied_optimizations),
                "optimization.estimated_improvement": optimization_impact.get("estimated_improvement", 0),
                "optimization.confidence_score": optimization_impact.get("confidence_score", 0),
                "optimization.priority_level": optimization_results.get("priority_level", "medium")
            })
            
            span.status = "success"
            span.end_time = datetime.utcnow()
            
            logger.info(f"Distribution optimization completed: {distribution_id}, "
                       f"applied {len(applied_optimizations)} optimizations")
            
            return span
            
        except Exception as e:
            span.status = "error"
            span.tags["error.type"] = type(e).__name__
            span.tags["error.message"] = str(e)
            span.end_time = datetime.utcnow()
            
            logger.error(f"Distribution optimization failed: {distribution_id}, error: {e}")
            raise
    
    async def start_distribution_trace(
        self,
        distribution_id: str,
        content_id: str,
        creator_id: str,
        target_platforms: List[PlatformType],
        **kwargs
    ) -> DistributionContext:
        """Start comprehensive multi-platform distribution tracing."""
        
        distribution_context = DistributionContext(
            distribution_id=distribution_id,
            content_id=content_id,
            creator_id=creator_id,
            target_platforms=target_platforms,
            **kwargs
        )
        
        self.active_distributions[distribution_id] = distribution_context
        
        logger.info(f"Started distribution trace: {distribution_id} "
                   f"for {len(target_platforms)} platforms")
        
        return distribution_context
    
    async def _trace_platform_adaptation(
        self,
        parent_span: TraceSpan,
        distribution_id: str,
        content_data: Dict[str, Any],
        platform: PlatformType
    ) -> TraceSpan:
        """Trace content adaptation for specific platform."""
        
        span = TraceSpan(
            trace_id=parent_span.trace_id,
            span_id=str(uuid.uuid4()),
            parent_id=parent_span.span_id,
            operation_name=f"platform_adaptation_{platform.value}",
            service_name=self.service_name,
            span_type=SpanType.CONTENT_PROCESSING,
            start_time=datetime.utcnow(),
            tags={
                "platform.type": platform.value,
                "content.original_format": content_data.get("format"),
                "content.original_size": content_data.get("size_mb", 0)
            }
        )
        
        try:
            start_time = datetime.utcnow()
            
            # Adapt content for specific platform requirements
            adapted_content = await self._adapt_content_for_platform(content_data, platform)
            
            processing_time = (datetime.utcnow() - start_time).total_seconds() * 1000
            
            # Calculate adaptation quality score
            adaptation_score = await self._calculate_platform_adaptation_score(
                content_data, adapted_content, platform
            )
            
            span.tags.update({
                "adaptation.score": adaptation_score,
                "adaptation.processing_time_ms": processing_time,
                "adaptation.target_format": adapted_content.get("format"),
                "adaptation.target_size": adapted_content.get("size_mb", 0),
                "adaptation.quality_maintained": adapted_content.get("quality_score", 0)
            })
            
            span.status = "success"
            span.end_time = datetime.utcnow()
            
            return span
            
        except Exception as e:
            span.status = "error"
            span.tags["error.type"] = type(e).__name__
            span.tags["error.message"] = str(e)
            span.end_time = datetime.utcnow()
            
            logger.error(f"Platform adaptation failed: {platform.value}, error: {e}")
            raise
    
    async def _execute_simultaneous_publishing(
        self, parent_span: TraceSpan, distribution: DistributionContext
    ) -> Dict[str, Dict[str, Any]]:
        """Execute simultaneous publishing to all platforms."""
        
        publishing_tasks = []
        
        for platform in distribution.target_platforms:
            task = self._publish_to_platform(parent_span, distribution, platform)
            publishing_tasks.append((platform.value, task))
        
        results = {}
        completed_tasks = await asyncio.gather(
            *[task for _, task in publishing_tasks], 
            return_exceptions=True
        )
        
        for i, (platform_name, _) in enumerate(publishing_tasks):
            result = completed_tasks[i]
            if isinstance(result, Exception):
                results[platform_name] = {
                    "status": "error",
                    "error": str(result),
                    "timestamp": datetime.utcnow().isoformat()
                }
            else:
                results[platform_name] = result
        
        return results
    
    async def _execute_sequential_publishing(
        self, parent_span: TraceSpan, distribution: DistributionContext
    ) -> Dict[str, Dict[str, Any]]:
        """Execute sequential publishing to platforms."""
        
        results = {}
        
        for platform in distribution.target_platforms:
            try:
                result = await self._publish_to_platform(parent_span, distribution, platform)
                results[platform.value] = result
                
                # Add delay between publications to avoid rate limiting
                await asyncio.sleep(2)
                
            except Exception as e:
                results[platform.value] = {
                    "status": "error",
                    "error": str(e),
                    "timestamp": datetime.utcnow().isoformat()
                }
        
        return results
    
    async def _execute_optimized_publishing(
        self, parent_span: TraceSpan, distribution: DistributionContext
    ) -> Dict[str, Dict[str, Any]]:
        """Execute optimized publishing with platform-specific timing."""
        
        # Get optimal publishing times for each platform
        optimal_schedule = await self.distribution_optimizer.get_optimal_publishing_schedule(
            distribution.target_platforms, distribution.creator_id
        )
        
        results = {}
        
        for platform in distribution.target_platforms:
            optimal_time = optimal_schedule.get(platform.value)
            
            if optimal_time and optimal_time > datetime.utcnow():
                # Schedule for future publishing
                results[platform.value] = {
                    "status": "scheduled",
                    "scheduled_time": optimal_time.isoformat(),
                    "timestamp": datetime.utcnow().isoformat()
                }
                distribution.scheduled_times[platform.value] = optimal_time
            else:
                # Publish immediately
                try:
                    result = await self._publish_to_platform(parent_span, distribution, platform)
                    results[platform.value] = result
                except Exception as e:
                    results[platform.value] = {
                        "status": "error",
                        "error": str(e),
                        "timestamp": datetime.utcnow().isoformat()
                    }
        
        return results
    
    async def _publish_to_platform(
        self, parent_span: TraceSpan, distribution: DistributionContext, platform: PlatformType
    ) -> Dict[str, Any]:
        """Publish content to specific platform."""
        
        # Check API rate limits
        await self.api_rate_manager.check_rate_limit(platform.value)
        
        # Simulate platform publishing (in real implementation, this would call actual APIs)
        await asyncio.sleep(1)  # Simulate API call
        
        # Simulate success/failure (90% success rate)
        import random
        if random.random() < 0.9:
            return {
                "status": "success",
                "platform_post_id": f"{platform.value}_{uuid.uuid4().hex[:8]}",
                "timestamp": datetime.utcnow().isoformat(),
                "url": f"https://{platform.value}.com/post/{uuid.uuid4().hex[:8]}"
            }
        else:
            raise Exception(f"Platform API error: {platform.value}")


class DistributionOptimizer:
    """Advanced distribution optimization engine."""
    
    def __init__(self):
        self.optimization_models: Dict[str, Any] = {}
        self.platform_insights: Dict[str, Dict[str, Any]] = {}
    
    async def optimize_distribution(
        self, distribution: DistributionContext, goals: List[str]
    ) -> Dict[str, Any]:
        """Generate optimization recommendations for distribution."""
        
        recommendations = []
        
        # Analyze current performance
        current_performance = await self._analyze_current_performance(distribution)
        
        # Generate platform-specific recommendations
        for platform in distribution.target_platforms:
            platform_recommendations = await self._generate_platform_recommendations(
                platform, distribution, goals
            )
            recommendations.extend(platform_recommendations)
        
        # Generate cross-platform recommendations
        cross_platform_recommendations = await self._generate_cross_platform_recommendations(
            distribution, goals
        )
        recommendations.extend(cross_platform_recommendations)
        
        return {
            "recommendations": recommendations,
            "current_performance": current_performance,
            "priority_level": self._calculate_priority_level(recommendations),
            "estimated_impact": self._estimate_optimization_impact(recommendations)
        }
    
    async def get_optimal_publishing_schedule(
        self, platforms: List[PlatformType], creator_id: str
    ) -> Dict[str, datetime]:
        """Get optimal publishing schedule for platforms."""
        
        schedule = {}
        
        for platform in platforms:
            # Get audience insights for creator on platform
            audience_insights = await self._get_audience_insights(creator_id, platform)
            
            # Calculate optimal posting time
            optimal_time = await self._calculate_optimal_posting_time(
                platform, audience_insights
            )
            
            schedule[platform.value] = optimal_time
        
        return schedule


class CrossPlatformAnalyzer:
    """Advanced cross-platform performance analyzer."""
    
    def __init__(self):
        self.analysis_models: Dict[str, Any] = {}
        self.benchmark_data: Dict[str, Dict[str, float]] = {}
    
    async def analyze_performance(
        self, distribution_id: str, engagement_data: Dict[str, Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Analyze cross-platform performance."""
        
        performance_scores = {}
        
        for platform, data in engagement_data.items():
            score = await self._calculate_platform_performance_score(platform, data)
            performance_scores[platform] = score
        
        # Find best and worst performing platforms
        best_platform = max(performance_scores.items(), key=lambda x: x[1])[0]
        worst_platform = min(performance_scores.items(), key=lambda x: x[1])[0]
        
        # Calculate audience overlap
        audience_overlap = await self._calculate_audience_overlap(engagement_data)
        
        return {
            "performance_scores": performance_scores,
            "best_platform": best_platform,
            "worst_platform": worst_platform,
            "audience_overlap": audience_overlap,
            "cross_platform_insights": await self._generate_insights(engagement_data)
        }


class APIRateLimitManager:
    """API rate limit management system."""
    
    def __init__(self):
        self.rate_limits: Dict[str, Dict[str, Any]] = {
            "instagram": {"requests_per_hour": 200, "current_count": 0, "reset_time": datetime.utcnow()},
            "tiktok": {"requests_per_hour": 300, "current_count": 0, "reset_time": datetime.utcnow()},
            "youtube": {"requests_per_hour": 100, "current_count": 0, "reset_time": datetime.utcnow()},
            "twitter": {"requests_per_hour": 300, "current_count": 0, "reset_time": datetime.utcnow()},
            "facebook": {"requests_per_hour": 200, "current_count": 0, "reset_time": datetime.utcnow()},
        }
    
    async def check_rate_limit(self, platform: str) -> bool:
        """Check if API rate limit allows request."""
        
        if platform not in self.rate_limits:
            return True
        
        rate_info = self.rate_limits[platform]
        current_time = datetime.utcnow()
        
        # Reset counter if hour has passed
        if current_time >= rate_info["reset_time"]:
            rate_info["current_count"] = 0
            rate_info["reset_time"] = current_time + timedelta(hours=1)
        
        # Check if under limit
        if rate_info["current_count"] < rate_info["requests_per_hour"]:
            rate_info["current_count"] += 1
            return True
        else:
            # Wait until reset time
            wait_time = (rate_info["reset_time"] - current_time).total_seconds()
            if wait_time > 0:
                await asyncio.sleep(min(wait_time, 60))  # Wait max 1 minute
            return False