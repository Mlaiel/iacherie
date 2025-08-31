"""Advanced Content Processing Monitoring Module

Enterprise-grade monitoring for content processing pipelines supporting multi-format creators.
Tracks upload, protection, SEO, collaboration, and distribution workflows.

Created by: Fahed Mlaiel (mlaiel@live.de)
© 2025 Fahed Mlaiel. All rights reserved.

Business Logic: User Upload → AI Protection → SEO → Collaboration → Distribution
"""
import asyncio
import time
import json
from typing import Dict, Any, List, Optional, Callable, Union, Set
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from collections import defaultdict, deque
from enum import Enum
import logging
import statistics
import hashlib
from pathlib import Path
import aiofiles
import redis.asyncio as aioredis
from sqlalchemy.ext.asyncio import AsyncSession

from ..core.metrics import MetricsCollector, MetricEntry, MetricType, MetricPriority
from ..core.exceptions import MonitoringError, ContentProcessingError
from .ai_performance import ProcessingStage, AIModelType

logger = logging.getLogger(__name__)


class ContentType(Enum):
    """Types of content supported by the platform"""    AUDIO = "audio"
    VIDEO = "video"
    IMAGE = "image"
    TEXT = "text"
    PODCAST = "podcast"
    BLOG_POST = "blog_post"
    SOCIAL_MEDIA = "social_media"
    MUSIC_TRACK = "music_track"
    MUSIC_ALBUM = "music_album"
    PHOTOGRAPHY = "photography"
    COMEDY_SKIT = "comedy_skit"
    MIXED_MEDIA = "mixed_media"


class ContentStatus(Enum):
    """Content processing status"""    UPLOADED = "uploaded"
    VALIDATING = "validating"
    ANALYZING = "analyzing"
    PROTECTING = "protecting"
    OPTIMIZING_SEO = "optimizing_seo"
    MATCHING_COLLABORATORS = "matching_collaborators"
    DISTRIBUTING = "distributing"
    MONETIZING = "monetizing"
    COMPLETED = "completed"
    FAILED = "failed"
    QUARANTINED = "quarantined"


class QualityLevel(Enum):
    """Content quality assessment levels"""    EXCELLENT = "excellent"
    GOOD = "good"
    ACCEPTABLE = "acceptable"
    POOR = "poor"
    UNACCEPTABLE = "unacceptable"


@dataclass
class ContentMetrics:
    """Comprehensive content processing metrics"""    content_id: str
    user_id: str
    content_type: ContentType
    file_size: int
    processing_stage: ProcessingStage
    status: ContentStatus
    quality_score: float
    protection_strength: float
    seo_score: float
    collaboration_matches: int
    revenue_potential: float
    processing_time: float
    ai_models_used: List[str]
    resource_usage: Dict[str, float]
    error_messages: List[str] = field(default_factory=list)
    timestamp: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class PipelineFlow:
    """Complete pipeline flow tracking"""    flow_id: str
    user_id: str
    content_id: str
    content_type: ContentType
    start_time: datetime
    end_time: Optional[datetime] = None
    total_duration: Optional[float] = None
    stages_completed: List[ProcessingStage] = field(default_factory=list)
    current_stage: Optional[ProcessingStage] = None
    success: bool = False
    bottlenecks: List[str] = field(default_factory=list)
    optimization_suggestions: List[str] = field(default_factory=list)
    final_metrics: Optional[ContentMetrics] = None


@dataclass
class UserJourney:
    """User journey and engagement tracking"""    user_id: str
    session_id: str
    journey_start: datetime
    content_uploads: int = 0
    successful_protections: int = 0
    collaborations_initiated: int = 0
    revenue_generated: float = 0.0
    engagement_score: float = 0.0
    satisfaction_score: float = 0.0
    pain_points: List[str] = field(default_factory=list)
    feature_usage: Dict[str, int] = field(default_factory=dict)


class ContentProcessingMonitor:
    """    Advanced Content Processing Monitor
    
    Monitors the complete content processing pipeline from upload to monetization,
    tracking performance, quality, and user experience.
    """    
    def __init__(
        self,
        metrics_collector: Optional[MetricsCollector] = None,
        redis_client: Optional[aioredis.Redis] = None,
        storage_path: Optional[Path] = None
    ):
        self.metrics_collector = metrics_collector or MetricsCollector()
        self.redis_client = redis_client
        self.storage_path = storage_path or Path("/tmp/content_monitoring")
        self.storage_path.mkdir(exist_ok=True)
        
        # Real-time tracking
        self.active_flows: Dict[str, PipelineFlow] = {}
        self.content_metrics: Dict[str, deque] = defaultdict(
            lambda: deque(maxlen=1000)
        )
        self.user_journeys: Dict[str, UserJourney] = {}
        self.processing_queues: Dict[ProcessingStage, Set[str]] = defaultdict(set)
        
        # Performance analytics
        self.stage_performance: Dict[ProcessingStage, List[float]] = defaultdict(list)
        self.quality_trends: Dict[ContentType, List[float]] = defaultdict(list)
        self.user_satisfaction: Dict[str, List[float]] = defaultdict(list)
        
        # Business metrics
        self.revenue_tracking: Dict[str, float] = defaultdict(float)
        self.collaboration_success_rates: Dict[ContentType, float] = defaultdict(float)
        self.platform_health_score: float = 0.0
        
        # Monitoring state
        self.is_monitoring = False
        self._monitor_task: Optional[asyncio.Task] = None
        
    async def start_monitoring(self) -> None:
        """Start content processing monitoring"""        if self.is_monitoring:
            logger.warning("Content processing monitoring is already running")
            return
            
        self.is_monitoring = True
        self._monitor_task = asyncio.create_task(self._monitoring_loop())
        
        logger.info("Content processing monitoring started successfully")
        
    async def stop_monitoring(self) -> None:
        """Stop content processing monitoring"""        if not self.is_monitoring:
            return
            
        self.is_monitoring = False
        
        if self._monitor_task:
            self._monitor_task.cancel()
            try:
                await self._monitor_task
            except asyncio.CancelledError:
                pass
                
        logger.info("Content processing monitoring stopped")
        
    async def track_upload(
        self,
        user_id: str,
        content_id: str,
        content_type: ContentType,
        file_size: int,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """        Start tracking a new content upload
        
        Returns:
            flow_id: Unique identifier for this processing flow
        """        flow_id = self._generate_flow_id(user_id, content_id)
        
        # Create new pipeline flow
        flow = PipelineFlow(
            flow_id=flow_id,
            user_id=user_id,
            content_id=content_id,
            content_type=content_type,
            start_time=datetime.utcnow(),
            current_stage=ProcessingStage.UPLOAD
        )
        
        self.active_flows[flow_id] = flow
        self.processing_queues[ProcessingStage.UPLOAD].add(flow_id)
        
        # Initialize content metrics
        initial_metrics = ContentMetrics(
            content_id=content_id,
            user_id=user_id,
            content_type=content_type,
            file_size=file_size,
            processing_stage=ProcessingStage.UPLOAD,
            status=ContentStatus.UPLOADED,
            quality_score=0.0,
            protection_strength=0.0,
            seo_score=0.0,
            collaboration_matches=0,
            revenue_potential=0.0,
            processing_time=0.0,
            ai_models_used=[],
            resource_usage={},
            metadata=metadata or {}
        )
        
        await self._store_content_metrics(initial_metrics)
        
        # Update user journey
        await self._update_user_journey(user_id, "content_upload")
        
        # Collect metrics
        await self.metrics_collector.collect_metric(
            MetricEntry(
                name="content_upload_started",
                value=1,
                metric_type=MetricType.COUNTER,
                tags={
                    "content_type": content_type.value,
                    "file_size_mb": str(file_size // 1024 // 1024)
                },
                user_id=user_id,
                metadata={"content_id": content_id, "flow_id": flow_id}
            )
        )
        
        logger.info(f"Started tracking content upload: {flow_id}")
        return flow_id
        
    async def update_stage_progress(
        self,
        flow_id: str,
        new_stage: ProcessingStage,
        stage_metrics: Optional[Dict[str, Any]] = None,
        ai_models_used: Optional[List[str]] = None
    ) -> None:
        """Update the processing stage for a content flow"""        if flow_id not in self.active_flows:
            raise MonitoringError(f"Flow {flow_id} not found")
            
        flow = self.active_flows[flow_id]
        previous_stage = flow.current_stage
        
        # Calculate stage duration
        stage_duration = 0.0
        if previous_stage:
            stage_duration = (datetime.utcnow() - flow.start_time).total_seconds()
            self.stage_performance[previous_stage].append(stage_duration)
            
            # Remove from previous stage queue
            self.processing_queues[previous_stage].discard(flow_id)
            
        # Update flow
        flow.stages_completed.append(previous_stage) if previous_stage else None
        flow.current_stage = new_stage
        self.processing_queues[new_stage].add(flow_id)
        
        # Update content metrics
        updated_metrics = ContentMetrics(
            content_id=flow.content_id,
            user_id=flow.user_id,
            content_type=flow.content_type,
            file_size=0,  # Would be retrieved from storage
            processing_stage=new_stage,
            status=self._stage_to_status(new_stage),
            quality_score=stage_metrics.get("quality_score", 0.0) if stage_metrics else 0.0,
            protection_strength=stage_metrics.get("protection_strength", 0.0) if stage_metrics else 0.0,
            seo_score=stage_metrics.get("seo_score", 0.0) if stage_metrics else 0.0,
            collaboration_matches=stage_metrics.get("collaboration_matches", 0) if stage_metrics else 0,
            revenue_potential=stage_metrics.get("revenue_potential", 0.0) if stage_metrics else 0.0,
            processing_time=stage_duration,
            ai_models_used=ai_models_used or [],
            resource_usage=stage_metrics.get("resource_usage", {}) if stage_metrics else {},
            metadata=stage_metrics or {}
        )
        
        await self._store_content_metrics(updated_metrics)
        
        # Collect stage transition metrics
        await self.metrics_collector.collect_metric(
            MetricEntry(
                name="content_stage_transition",
                value=stage_duration,
                metric_type=MetricType.TIMER,
                tags={
                    "from_stage": previous_stage.value if previous_stage else "none",
                    "to_stage": new_stage.value,
                    "content_type": flow.content_type.value
                },
                user_id=flow.user_id,
                metadata={"flow_id": flow_id, "content_id": flow.content_id}
            )
        )
        
        # Check for bottlenecks
        await self._detect_bottlenecks(flow_id, stage_duration, new_stage)
        
        logger.info(f"Updated flow {flow_id} to stage {new_stage.value}")
        
    async def complete_processing(
        self,
        flow_id: str,
        success: bool,
        final_metrics: Optional[Dict[str, Any]] = None,
        error_message: Optional[str] = None
    ) -> PipelineFlow:
        """Complete the content processing flow"""        if flow_id not in self.active_flows:
            raise MonitoringError(f"Flow {flow_id} not found")
            
        flow = self.active_flows[flow_id]
        flow.end_time = datetime.utcnow()
        flow.total_duration = (flow.end_time - flow.start_time).total_seconds()
        flow.success = success
        
        # Remove from current stage queue
        if flow.current_stage:
            self.processing_queues[flow.current_stage].discard(flow_id)
            
        # Create final metrics
        if final_metrics:
            flow.final_metrics = ContentMetrics(
                content_id=flow.content_id,
                user_id=flow.user_id,
                content_type=flow.content_type,
                file_size=final_metrics.get("file_size", 0),
                processing_stage=ProcessingStage.DISTRIBUTION if success else flow.current_stage,
                status=ContentStatus.COMPLETED if success else ContentStatus.FAILED,
                quality_score=final_metrics.get("quality_score", 0.0),
                protection_strength=final_metrics.get("protection_strength", 0.0),
                seo_score=final_metrics.get("seo_score", 0.0),
                collaboration_matches=final_metrics.get("collaboration_matches", 0),
                revenue_potential=final_metrics.get("revenue_potential", 0.0),
                processing_time=flow.total_duration,
                ai_models_used=final_metrics.get("ai_models_used", []),
                resource_usage=final_metrics.get("resource_usage", {}),
                error_messages=[error_message] if error_message else []
            )
            
            await self._store_content_metrics(flow.final_metrics)
            
        # Update user journey
        if success:
            await self._update_user_journey(flow.user_id, "content_completed")
            
            # Update revenue tracking
            if final_metrics and "revenue_potential" in final_metrics:
                self.revenue_tracking[flow.user_id] += final_metrics["revenue_potential"]
        else:
            await self._update_user_journey(flow.user_id, "content_failed")
            
        # Collect completion metrics
        await self.metrics_collector.collect_metric(
            MetricEntry(
                name="content_processing_completed",
                value=flow.total_duration,
                metric_type=MetricType.TIMER,
                tags={
                    "content_type": flow.content_type.value,
                    "success": str(success),
                    "stages_completed": str(len(flow.stages_completed))
                },
                user_id=flow.user_id,
                priority=MetricPriority.HIGH if not success else MetricPriority.MEDIUM,
                metadata={
                    "flow_id": flow_id,
                    "content_id": flow.content_id,
                    "error_message": error_message
                }
            )
        )
        
        # Archive flow
        await self._archive_flow(flow)
        del self.active_flows[flow_id]
        
        logger.info(f"Completed processing flow {flow_id}: success={success}")
        return flow
        
    async def track_collaboration_matching(
        self,
        flow_id: str,
        matches_found: int,
        matching_criteria: Dict[str, Any],
        matching_duration: float
    ) -> None:
        """Track collaboration matching performance"""        if flow_id not in self.active_flows:
            return
            
        flow = self.active_flows[flow_id]
        
        # Update collaboration success rates
        content_type = flow.content_type
        current_rate = self.collaboration_success_rates[content_type]
        success_rate = 1.0 if matches_found > 0 else 0.0
        self.collaboration_success_rates[content_type] = (current_rate + success_rate) / 2
        
        # Collect metrics
        await self.metrics_collector.collect_metric(
            MetricEntry(
                name="collaboration_matching_performance",
                value=matching_duration,
                metric_type=MetricType.TIMER,
                tags={
                    "content_type": content_type.value,
                    "matches_found": str(matches_found),
                    "has_matches": str(matches_found > 0)
                },
                user_id=flow.user_id,
                metadata={
                    "flow_id": flow_id,
                    "matching_criteria": matching_criteria
                }
            )
        )
        
        await self._update_user_journey(flow.user_id, "collaboration_match")
        
    async def track_revenue_generation(
        self,
        user_id: str,
        content_id: str,
        revenue_amount: float,
        revenue_source: str
    ) -> None:
        """Track revenue generation from content"""        self.revenue_tracking[user_id] += revenue_amount
        
        await self.metrics_collector.collect_metric(
            MetricEntry(
                name="revenue_generated",
                value=revenue_amount,
                metric_type=MetricType.COUNTER,
                tags={
                    "revenue_source": revenue_source,
                    "content_id": content_id
                },
                user_id=user_id,
                priority=MetricPriority.HIGH,
                metadata={"revenue_amount": revenue_amount}
            )
        )
        
        await self._update_user_journey(user_id, "revenue_generated", revenue_amount)
        
    async def get_processing_analytics(
        self,
        time_window: timedelta = timedelta(hours=24)
    ) -> Dict[str, Any]:
        """Get comprehensive processing analytics"""        cutoff_time = datetime.utcnow() - time_window
        
        # Active flows analysis
        active_count = len(self.active_flows)
        stage_distribution = {}
        for stage, flows in self.processing_queues.items():
            stage_distribution[stage.value] = len(flows)
            
        # Performance analysis
        stage_performance_summary = {}
        for stage, durations in self.stage_performance.items():
            recent_durations = [d for d in durations if d is not None][-100:]  # Last 100 measurements
            if recent_durations:
                stage_performance_summary[stage.value] = {
                    "average_duration": statistics.mean(recent_durations),
                    "median_duration": statistics.median(recent_durations),
                    "min_duration": min(recent_durations),
                    "max_duration": max(recent_durations),
                    "total_executions": len(recent_durations)
                }
                
        # Quality trends
        quality_summary = {}
        for content_type, scores in self.quality_trends.items():
            recent_scores = scores[-50:]  # Last 50 scores
            if recent_scores:
                quality_summary[content_type.value] = {
                    "average_quality": statistics.mean(recent_scores),
                    "quality_trend": "improving" if len(recent_scores) > 1 and recent_scores[-1] > recent_scores[0] else "stable"
                }
                
        # Business metrics
        total_revenue = sum(self.revenue_tracking.values())
        active_users = len(self.user_journeys)
        
        return {
            "timestamp": datetime.utcnow().isoformat(),
            "time_window": str(time_window),
            "active_processing": {
                "total_active_flows": active_count,
                "stage_distribution": stage_distribution
            },
            "performance": {
                "stage_performance": stage_performance_summary,
                "bottlenecks": await self._identify_current_bottlenecks()
            },
            "quality": {
                "content_type_quality": quality_summary,
                "overall_platform_health": self.platform_health_score
            },
            "business_metrics": {
                "total_revenue": total_revenue,
                "active_users": active_users,
                "collaboration_success_rates": {
                    k.value: v for k, v in self.collaboration_success_rates.items()
                }
            },
            "user_experience": {
                "average_satisfaction": self._calculate_average_satisfaction(),
                "common_pain_points": await self._identify_common_pain_points()
            }
        }
        
    async def get_user_journey_analytics(
        self,
        user_id: str
    ) -> Optional[Dict[str, Any]]:
        """Get analytics for a specific user's journey"""        if user_id not in self.user_journeys:
            return None
            
        journey = self.user_journeys[user_id]
        
        return {
            "user_id": user_id,
            "journey_duration": (datetime.utcnow() - journey.journey_start).total_seconds(),
            "content_uploads": journey.content_uploads,
            "successful_protections": journey.successful_protections,
            "collaborations_initiated": journey.collaborations_initiated,
            "revenue_generated": journey.revenue_generated,
            "engagement_score": journey.engagement_score,
            "satisfaction_score": journey.satisfaction_score,
            "pain_points": journey.pain_points,
            "feature_usage": journey.feature_usage,
            "success_rate": (
                journey.successful_protections / journey.content_uploads
                if journey.content_uploads > 0 else 0.0
            )
        }
        
    def _generate_flow_id(self, user_id: str, content_id: str) -> str:
        """Generate unique flow ID"""        timestamp = str(int(time.time() * 1000))
        data = f"{user_id}:{content_id}:{timestamp}"
        return hashlib.sha256(data.encode()).hexdigest()[:16]
        
    def _stage_to_status(self, stage: ProcessingStage) -> ContentStatus:
        """Convert processing stage to content status"""        stage_status_map = {
            ProcessingStage.UPLOAD: ContentStatus.UPLOADED,
            ProcessingStage.VALIDATION: ContentStatus.VALIDATING,
            ProcessingStage.AI_ANALYSIS: ContentStatus.ANALYZING,
            ProcessingStage.PROTECTION: ContentStatus.PROTECTING,
            ProcessingStage.SEO_OPTIMIZATION: ContentStatus.OPTIMIZING_SEO,
            ProcessingStage.COLLABORATION_MATCHING: ContentStatus.MATCHING_COLLABORATORS,
            ProcessingStage.DISTRIBUTION: ContentStatus.DISTRIBUTING,
            ProcessingStage.MONETIZATION: ContentStatus.MONETIZING
        }
        return stage_status_map.get(stage, ContentStatus.UPLOADED)
        
    async def _store_content_metrics(self, metrics: ContentMetrics) -> None:
        """Store content metrics"""        # Store in memory
        self.content_metrics[metrics.content_id].append(metrics)
        
        # Update quality trends
        self.quality_trends[metrics.content_type].append(metrics.quality_score)
        
        # Store in Redis if available
        if self.redis_client:
            try:
                key = f"content_metrics:{metrics.content_id}:{int(metrics.timestamp.timestamp())}"
                await self.redis_client.setex(
                    key,
                    3600,  # 1 hour TTL
                    json.dumps({
                        "quality_score": metrics.quality_score,
                        "protection_strength": metrics.protection_strength,
                        "seo_score": metrics.seo_score,
                        "collaboration_matches": metrics.collaboration_matches,
                        "revenue_potential": metrics.revenue_potential,
                        "processing_time": metrics.processing_time,
                        "status": metrics.status.value
                    })
                )
            except Exception as e:
                logger.warning(f"Failed to store content metrics in Redis: {e}")
                
    async def _update_user_journey(
        self,
        user_id: str,
        event_type: str,
        value: float = 1.0
    ) -> None:
        """Update user journey tracking"""        if user_id not in self.user_journeys:
            self.user_journeys[user_id] = UserJourney(
                user_id=user_id,
                session_id=f"session_{int(time.time())}",
                journey_start=datetime.utcnow()
            )
            
        journey = self.user_journeys[user_id]
        
        # Update journey metrics based on event type
        if event_type == "content_upload":
            journey.content_uploads += 1
            journey.feature_usage["upload"] = journey.feature_usage.get("upload", 0) + 1
        elif event_type == "content_completed":
            journey.successful_protections += 1
            journey.engagement_score += 10.0
        elif event_type == "collaboration_match":
            journey.collaborations_initiated += 1
            journey.feature_usage["collaboration"] = journey.feature_usage.get("collaboration", 0) + 1
        elif event_type == "revenue_generated":
            journey.revenue_generated += value
            journey.satisfaction_score += 5.0
        elif event_type == "content_failed":
            journey.pain_points.append("content_processing_failure")
            journey.satisfaction_score -= 2.0
            
    async def _detect_bottlenecks(
        self,
        flow_id: str,
        stage_duration: float,
        stage: ProcessingStage
    ) -> None:
        """Detect processing bottlenecks"""        # Calculate average duration for this stage
        avg_duration = statistics.mean(self.stage_performance[stage][-10:]) if self.stage_performance[stage] else 0
        
        # If current duration is significantly higher than average, it's a bottleneck
        if avg_duration > 0 and stage_duration > avg_duration * 2:
            flow = self.active_flows[flow_id]
            bottleneck_msg = f"Stage {stage.value} took {stage_duration:.2f}s (avg: {avg_duration:.2f}s)"
            flow.bottlenecks.append(bottleneck_msg)
            
            logger.warning(f"Bottleneck detected in flow {flow_id}: {bottleneck_msg}")
            
    async def _identify_current_bottlenecks(self) -> List[str]:
        """Identify current system bottlenecks"""        bottlenecks = []
        
        # Check queue sizes
        for stage, flows in self.processing_queues.items():
            if len(flows) > 10:  # Threshold for bottleneck
                bottlenecks.append(f"High queue length in {stage.value}: {len(flows)} flows")
                
        # Check average processing times
        for stage, durations in self.stage_performance.items():
            if durations:
                recent_avg = statistics.mean(durations[-10:])
                if recent_avg > 60:  # More than 1 minute average
                    bottlenecks.append(f"Slow processing in {stage.value}: {recent_avg:.2f}s average")
                    
        return bottlenecks
        
    def _calculate_average_satisfaction(self) -> float:
        """Calculate average user satisfaction score"""        if not self.user_journeys:
            return 0.0
            
        total_satisfaction = sum(journey.satisfaction_score for journey in self.user_journeys.values())
        return total_satisfaction / len(self.user_journeys)
        
    async def _identify_common_pain_points(self) -> List[str]:
        """Identify common user pain points"""        pain_point_counts = defaultdict(int)
        
        for journey in self.user_journeys.values():
            for pain_point in journey.pain_points:
                pain_point_counts[pain_point] += 1
                
        # Return most common pain points
        return sorted(pain_point_counts.items(), key=lambda x: x[1], reverse=True)[:5]
        
    async def _archive_flow(self, flow: PipelineFlow) -> None:
        """Archive completed flow to storage"""        try:
            archive_file = self.storage_path / f"flow_{flow.flow_id}.json"
            
            flow_data = {
                "flow_id": flow.flow_id,
                "user_id": flow.user_id,
                "content_id": flow.content_id,
                "content_type": flow.content_type.value,
                "start_time": flow.start_time.isoformat(),
                "end_time": flow.end_time.isoformat() if flow.end_time else None,
                "total_duration": flow.total_duration,
                "stages_completed": [stage.value for stage in flow.stages_completed],
                "success": flow.success,
                "bottlenecks": flow.bottlenecks,
                "optimization_suggestions": flow.optimization_suggestions,
                "final_metrics": flow.final_metrics.__dict__ if flow.final_metrics else None
            }
            
            async with aiofiles.open(archive_file, 'w') as f:
                await f.write(json.dumps(flow_data, indent=2))
                
        except Exception as e:
            logger.error(f"Failed to archive flow {flow.flow_id}: {e}")
            
    async def _monitoring_loop(self) -> None:
        """Main monitoring loop"""        while self.is_monitoring:
            try:
                # Update platform health score
                self.platform_health_score = await self._calculate_platform_health()
                
                # Clean up old data
                await self._cleanup_old_data()
                
                # Generate optimization suggestions
                await self._generate_optimization_suggestions()
                
                # Wait before next iteration
                await asyncio.sleep(30)  # Monitor every 30 seconds
                
            except Exception as e:
                logger.error(f"Error in content monitoring loop: {e}")
                await asyncio.sleep(60)  # Wait longer on error
                
    async def _calculate_platform_health(self) -> float:
        """Calculate overall platform health score"""        health_factors = []
        
        # Processing success rate
        total_flows = len(self.active_flows)
        if total_flows > 0:
            success_rate = 1.0  # Would calculate from completed flows
            health_factors.append(success_rate * 30)  # 30% weight
            
        # Average quality score
        all_quality_scores = []
        for scores in self.quality_trends.values():
            all_quality_scores.extend(scores[-10:])  # Last 10 scores per content type
            
        if all_quality_scores:
            avg_quality = statistics.mean(all_quality_scores)
            health_factors.append(avg_quality * 25)  # 25% weight
            
        # User satisfaction
        avg_satisfaction = self._calculate_average_satisfaction()
        if avg_satisfaction > 0:
            health_factors.append((avg_satisfaction / 100) * 25)  # 25% weight
            
        # System performance (inverse of bottlenecks)
        bottleneck_count = len(await self._identify_current_bottlenecks())
        performance_score = max(0, 1 - (bottleneck_count / 10))  # Normalize to 0-1
        health_factors.append(performance_score * 20)  # 20% weight
        
        return sum(health_factors) if health_factors else 0.0
        
    async def _cleanup_old_data(self) -> None:
        """Clean up old tracking data"""        cutoff_time = datetime.utcnow() - timedelta(hours=24)
        
        # Clean up user journeys
        expired_journeys = [
            user_id for user_id, journey in self.user_journeys.items()
            if journey.journey_start < cutoff_time
        ]
        
        for user_id in expired_journeys:
            del self.user_journeys[user_id]
            
        # Clean up metrics
        for content_id, metrics_queue in self.content_metrics.items():
            while metrics_queue and metrics_queue[0].timestamp < cutoff_time:
                metrics_queue.popleft()
                
    async def _generate_optimization_suggestions(self) -> None:
        """Generate optimization suggestions for active flows"""        for flow_id, flow in self.active_flows.items():
            suggestions = []
            
            # Check for long-running flows
            flow_duration = (datetime.utcnow() - flow.start_time).total_seconds()
            if flow_duration > 300:  # 5 minutes
                suggestions.append("Consider optimizing AI model performance")
                
            # Check for repeated failures
            if len(flow.bottlenecks) > 2:
                suggestions.append("Review processing pipeline for bottlenecks")
                
            flow.optimization_suggestions.extend(suggestions)


# Global content processing monitor instance
content_processing_monitor = ContentProcessingMonitor()
