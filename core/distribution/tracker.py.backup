"""Distribution Tracker - Content Distribution Monitoring
======================================================

Advanced tracking system for monitoring content distribution across platforms,
analyzing performance, and providing real-time insights.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: © 2025 Fahed Mlaiel. All rights reserved.
"""
import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Set, Tuple
from enum import Enum
from dataclasses import dataclass, field
from uuid import UUID, uuid4
import json
from collections import defaultdict

from ..analytics.performance import PerformanceAnalyzer
from ..events.event_emitter import EventEmitter
from ..storage.database import DatabaseManager


class TrackingStatus(Enum):
    """Tracking status enumeration."""
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class DistributionPhase(Enum):
    """Distribution phase enumeration."""
    QUEUED = "queued"
    PROCESSING = "processing"
    UPLOADING = "uploading"
    PUBLISHED = "published"
    ANALYZING = "analyzing"
    OPTIMIZING = "optimizing"


@dataclass
class TrackingMetrics:
    """Tracking metrics data structure."""
    views: int = 0
    likes: int = 0
    shares: int = 0
    comments: int = 0
    saves: int = 0
    clicks: int = 0
    impressions: int = 0
    reach: int = 0
    engagement_rate: float = 0.0
    conversion_rate: float = 0.0
    revenue: float = 0.0
    cost: float = 0.0
    roi: float = 0.0


@dataclass
class PlatformTracking:
    """Platform-specific tracking data."""
    platform: str
    platform_id: str
    platform_url: str
    status: str = "unknown"
    published_at: Optional[datetime] = None
    last_updated: datetime = field(default_factory=datetime.utcnow)
    metrics: TrackingMetrics = field(default_factory=TrackingMetrics)
    analytics_data: Dict[str, Any] = field(default_factory=dict)
    performance_history: List[Dict[str, Any]] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)


@dataclass
class DistributionTracking:
    """Distribution tracking data structure."""
    tracking_id: UUID = field(default_factory=uuid4)
    content_id: UUID = field(default_factory=uuid4)
    user_id: UUID = field(default_factory=uuid4)
    distribution_id: UUID = field(default_factory=uuid4)
    
    # Status and phase
    status: TrackingStatus = TrackingStatus.ACTIVE
    current_phase: DistributionPhase = DistributionPhase.QUEUED
    
    # Platform tracking
    platforms: Dict[str, PlatformTracking] = field(default_factory=dict)
    
    # Aggregated metrics
    total_metrics: TrackingMetrics = field(default_factory=TrackingMetrics)
    
    # Performance data
    performance_score: float = 0.0
    engagement_quality: str = "unknown"
    audience_satisfaction: float = 0.0
    
    # Timeline
    created_at: datetime = field(default_factory=datetime.utcnow)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    last_update: datetime = field(default_factory=datetime.utcnow)
    
    # Configuration
    tracking_config: Dict[str, Any] = field(default_factory=dict)
    alert_thresholds: Dict[str, Any] = field(default_factory=dict)
    
    # Metadata
    content_metadata: Dict[str, Any] = field(default_factory=dict)
    campaign_data: Dict[str, Any] = field(default_factory=dict)


class DistributionTracker:
    """
    Distribution Tracker
    
    Provides comprehensive tracking and monitoring of content distribution
    across multiple platforms with real-time analytics and performance insights.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize distribution tracker."""
        self.config = config or {}
        self.logger = logging.getLogger(__name__)
        self.event_emitter = EventEmitter()
        
        # Core components
        self.performance_analyzer = PerformanceAnalyzer()
        self.database_manager = DatabaseManager()
        
        # Tracking state
        self.active_trackings: Dict[UUID, DistributionTracking] = {}
        self.completed_trackings: Dict[UUID, DistributionTracking] = {}
        
        # Platform connections
        self.platform_adapters: Dict[str, Any] = {}
        
        # Analytics and insights
        self.performance_insights: Dict[str, Dict[str, Any]] = {}
        self.trending_content: List[Dict[str, Any]] = []
        self.anomaly_alerts: List[Dict[str, Any]] = []
        
        # System configuration
        self.is_initialized = False
        self.is_running = False
        self.tracking_interval = config.get('tracking_interval', 300)  # 5 minutes
        self.analytics_interval = config.get('analytics_interval', 3600)  # 1 hour
        self.max_concurrent_tracking = config.get('max_concurrent_tracking', 100)
        
        # Performance metrics
        self.system_metrics = {
            'total_tracked_distributions': 0,
            'active_trackings': 0,
            'successful_trackings': 0,
            'failed_trackings': 0,
            'average_tracking_duration': 0.0,
            'data_collection_accuracy': 0.0,
            'alert_generation_rate': 0.0
        }
    
    async def initialize(self) -> bool:
        """
        Initialize the distribution tracker.
        
        Returns:
            bool: True if initialization successful
        """
        try:
            self.logger.info("Initializing Distribution Tracker")
            
            # Initialize core components
            await self.performance_analyzer.initialize()
            await self.database_manager.initialize()
            
            # Load existing trackings
            await self._load_existing_trackings()
            
            # Initialize platform adapters
            await self._initialize_platform_adapters()
            
            # Start background tasks
            await self._start_background_tasks()
            
            self.is_initialized = True
            self.is_running = True
            
            self.logger.info("Distribution Tracker initialized successfully")
            
            # Emit initialization event
            await self.event_emitter.emit('tracker_initialized', {
                'timestamp': datetime.utcnow(),
                'active_trackings': len(self.active_trackings)
            })
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize Distribution Tracker: {e}")
            return False
    
    async def shutdown(self) -> bool:
        """
        Gracefully shutdown the distribution tracker.
        
        Returns:
            bool: True if shutdown successful
        """
        try:
            self.logger.info("Shutting down Distribution Tracker")
            self.is_running = False
            
            # Save all tracking data
            await self._save_all_trackings()
            
            # Clear active trackings
            self.active_trackings.clear()
            
            self.is_initialized = False
            
            self.logger.info("Distribution Tracker shutdown complete")
            
            # Emit shutdown event
            await self.event_emitter.emit('tracker_shutdown', {
                'timestamp': datetime.utcnow()
            })
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error during Distribution Tracker shutdown: {e}")
            return False
    
    async def start_tracking(
        self,
        content_id: UUID,
        user_id: UUID,
        distribution_id: UUID,
        platforms: List[str],
        tracking_config: Optional[Dict[str, Any]] = None
    ) -> UUID:
        """
        Start tracking a content distribution.
        
        Args:
            content_id: Content being distributed
            user_id: User who initiated distribution
            distribution_id: Distribution request ID
            platforms: List of platforms being distributed to
            tracking_config: Optional tracking configuration
            
        Returns:
            UUID: Tracking ID
        """
        if not self.is_initialized:
            raise RuntimeError("Distribution Tracker not initialized")
        
        # Create tracking instance
        tracking = DistributionTracking(
            content_id=content_id,
            user_id=user_id,
            distribution_id=distribution_id,
            tracking_config=tracking_config or {},
            started_at=datetime.utcnow()
        )
        
        # Initialize platform tracking
        for platform in platforms:
            tracking.platforms[platform] = PlatformTracking(
                platform=platform,
                platform_id="",  # Will be updated when content is published
                platform_url=""
            )
        
        # Set default alert thresholds
        tracking.alert_thresholds = {
            'low_engagement_threshold': 0.02,  # 2%
            'high_error_rate_threshold': 0.1,  # 10%
            'performance_drop_threshold': 0.3,  # 30%
            'anomaly_detection_sensitivity': 0.8
        }
        
        # Add to active trackings
        self.active_trackings[tracking.tracking_id] = tracking
        
        # Update system metrics
        self.system_metrics['total_tracked_distributions'] += 1
        self.system_metrics['active_trackings'] = len(self.active_trackings)
        
        self.logger.info(f"Started tracking distribution {distribution_id} with tracking ID {tracking.tracking_id}")
        
        # Emit tracking started event
        await self.event_emitter.emit('tracking_started', {
            'tracking_id': tracking.tracking_id,
            'content_id': content_id,
            'platforms': platforms,
            'timestamp': datetime.utcnow()
        })
        
        return tracking.tracking_id
    
    async def update_platform_status(
        self,
        tracking_id: UUID,
        platform: str,
        platform_id: str,
        platform_url: str,
        status: str,
        published_at: Optional[datetime] = None
    ) -> bool:
        """
        Update platform-specific tracking information.
        
        Args:
            tracking_id: Tracking ID
            platform: Platform name
            platform_id: Platform-specific content ID
            platform_url: Platform-specific content URL
            status: Current status
            published_at: Publication timestamp
            
        Returns:
            bool: True if update successful
        """
        tracking = self.active_trackings.get(tracking_id)
        if not tracking:
            self.logger.warning(f"Tracking {tracking_id} not found")
            return False
        
        if platform not in tracking.platforms:
            self.logger.warning(f"Platform {platform} not being tracked for {tracking_id}")
            return False
        
        # Update platform tracking
        platform_tracking = tracking.platforms[platform]
        platform_tracking.platform_id = platform_id
        platform_tracking.platform_url = platform_url
        platform_tracking.status = status
        platform_tracking.published_at = published_at or datetime.utcnow()
        platform_tracking.last_updated = datetime.utcnow()
        
        # Update tracking last update time
        tracking.last_update = datetime.utcnow()
        
        # Update phase if all platforms are published
        if all(pt.status in ['published', 'live'] for pt in tracking.platforms.values()):
            tracking.current_phase = DistributionPhase.PUBLISHED
        
        self.logger.info(f"Updated platform {platform} status for tracking {tracking_id}: {status}")
        
        # Emit platform update event
        await self.event_emitter.emit('platform_status_updated', {
            'tracking_id': tracking_id,
            'platform': platform,
            'status': status,
            'platform_url': platform_url,
            'timestamp': datetime.utcnow()
        })
        
        return True
    
    async def collect_analytics_data(self, tracking_id: UUID) -> Dict[str, Any]:
        """
        Collect analytics data for all platforms in a tracking.
        
        Args:
            tracking_id: Tracking ID
            
        Returns:
            Dict containing collected analytics data
        """
        tracking = self.active_trackings.get(tracking_id)
        if not tracking:
            return {}
        
        collected_data = {}
        total_metrics = TrackingMetrics()
        
        for platform, platform_tracking in tracking.platforms.items():
            if not platform_tracking.platform_id:
                continue
            
            try:
                # Get analytics from platform adapter
                adapter = self.platform_adapters.get(platform)
                if adapter:
                    analytics = await adapter.get_analytics(platform_tracking.platform_id)
                    
                    # Convert to tracking metrics
                    metrics = self._convert_analytics_to_metrics(platform, analytics)
                    
                    # Update platform tracking
                    platform_tracking.metrics = metrics
                    platform_tracking.analytics_data = analytics
                    platform_tracking.last_updated = datetime.utcnow()
                    
                    # Add to performance history
                    platform_tracking.performance_history.append({
                        'timestamp': datetime.utcnow(),
                        'metrics': metrics.__dict__,
                        'analytics': analytics
                    })
                    
                    # Aggregate to total metrics
                    total_metrics.views += metrics.views
                    total_metrics.likes += metrics.likes
                    total_metrics.shares += metrics.shares
                    total_metrics.comments += metrics.comments
                    total_metrics.impressions += metrics.impressions
                    total_metrics.reach += metrics.reach
                    total_metrics.revenue += metrics.revenue
                    
                    collected_data[platform] = {
                        'metrics': metrics.__dict__,
                        'analytics': analytics,
                        'timestamp': datetime.utcnow()
                    }
                    
                    self.logger.debug(f"Collected analytics for {platform} in tracking {tracking_id}")
                
            except Exception as e:
                self.logger.error(f"Failed to collect analytics for {platform}: {e}")
                platform_tracking.errors.append(f"Analytics collection failed: {str(e)}")
        
        # Update total metrics
        tracking.total_metrics = total_metrics
        
        # Calculate engagement rates
        if total_metrics.impressions > 0:
            total_metrics.engagement_rate = (
                (total_metrics.likes + total_metrics.shares + total_metrics.comments) 
                / total_metrics.impressions
            )
        
        # Calculate ROI
        if total_metrics.cost > 0:
            total_metrics.roi = (total_metrics.revenue - total_metrics.cost) / total_metrics.cost
        
        # Update tracking
        tracking.last_update = datetime.utcnow()
        
        return collected_data
    
    async def analyze_performance(self, tracking_id: UUID) -> Dict[str, Any]:
        """
        Analyze performance for a tracked distribution.
        
        Args:
            tracking_id: Tracking ID
            
        Returns:
            Dict containing performance analysis
        """
        tracking = self.active_trackings.get(tracking_id)
        if not tracking:
            return {}
        
        try:
            # Perform comprehensive performance analysis
            analysis = await self.performance_analyzer.analyze_distribution_performance(
                tracking_id=tracking_id,
                content_metadata=tracking.content_metadata,
                platform_data={
                    platform: {
                        'metrics': pt.metrics.__dict__,
                        'analytics': pt.analytics_data,
                        'history': pt.performance_history
                    }
                    for platform, pt in tracking.platforms.items()
                },
                total_metrics=tracking.total_metrics.__dict__
            )
            
            # Update tracking with analysis results
            tracking.performance_score = analysis.get('overall_score', 0.0)
            tracking.engagement_quality = analysis.get('engagement_quality', 'unknown')
            tracking.audience_satisfaction = analysis.get('audience_satisfaction', 0.0)
            
            # Check for alerts and anomalies
            await self._check_performance_alerts(tracking, analysis)
            
            # Store insights
            self.performance_insights[str(tracking_id)] = {
                'analysis': analysis,
                'timestamp': datetime.utcnow(),
                'performance_score': tracking.performance_score
            }
            
            self.logger.info(f"Analyzed performance for tracking {tracking_id}: score {tracking.performance_score:.2f}")
            
            return analysis
            
        except Exception as e:
            self.logger.error(f"Performance analysis failed for tracking {tracking_id}: {e}")
            return {}
    
    async def get_tracking_status(self, tracking_id: UUID) -> Optional[Dict[str, Any]]:
        """
        Get current status of a tracking.
        
        Args:
            tracking_id: Tracking ID
            
        Returns:
            Dict containing tracking status or None if not found
        """
        # Check active trackings
        tracking = self.active_trackings.get(tracking_id)
        if not tracking:
            # Check completed trackings
            tracking = self.completed_trackings.get(tracking_id)
        
        if not tracking:
            return None
        
        return {
            'tracking_id': str(tracking.tracking_id),
            'content_id': str(tracking.content_id),
            'distribution_id': str(tracking.distribution_id),
            'status': tracking.status.value,
            'current_phase': tracking.current_phase.value,
            'performance_score': tracking.performance_score,
            'engagement_quality': tracking.engagement_quality,
            'platforms': {
                platform: {
                    'platform_id': pt.platform_id,
                    'platform_url': pt.platform_url,
                    'status': pt.status,
                    'published_at': pt.published_at.isoformat() if pt.published_at else None,
                    'metrics': pt.metrics.__dict__,
                    'last_updated': pt.last_updated.isoformat()
                }
                for platform, pt in tracking.platforms.items()
            },
            'total_metrics': tracking.total_metrics.__dict__,
            'created_at': tracking.created_at.isoformat(),
            'started_at': tracking.started_at.isoformat() if tracking.started_at else None,
            'completed_at': tracking.completed_at.isoformat() if tracking.completed_at else None,
            'last_update': tracking.last_update.isoformat()
        }
    
    async def stop_tracking(self, tracking_id: UUID, reason: str = "completed") -> bool:
        """
        Stop tracking a distribution.
        
        Args:
            tracking_id: Tracking ID
            reason: Reason for stopping (completed, cancelled, failed)
            
        Returns:
            bool: True if stopped successfully
        """
        tracking = self.active_trackings.get(tracking_id)
        if not tracking:
            return False
        
        # Update tracking status
        if reason == "completed":
            tracking.status = TrackingStatus.COMPLETED
        elif reason == "cancelled":
            tracking.status = TrackingStatus.CANCELLED
        elif reason == "failed":
            tracking.status = TrackingStatus.FAILED
        
        tracking.completed_at = datetime.utcnow()
        tracking.current_phase = DistributionPhase.COMPLETED
        
        # Perform final analytics collection
        await self.collect_analytics_data(tracking_id)
        
        # Perform final performance analysis
        final_analysis = await self.analyze_performance(tracking_id)
        
        # Move to completed trackings
        self.completed_trackings[tracking_id] = tracking
        del self.active_trackings[tracking_id]
        
        # Update system metrics
        self.system_metrics['active_trackings'] = len(self.active_trackings)
        if tracking.status == TrackingStatus.COMPLETED:
            self.system_metrics['successful_trackings'] += 1
        else:
            self.system_metrics['failed_trackings'] += 1
        
        # Calculate tracking duration
        if tracking.started_at:
            duration = (tracking.completed_at - tracking.started_at).total_seconds()
            current_avg = self.system_metrics['average_tracking_duration']
            total_completed = self.system_metrics['successful_trackings'] + self.system_metrics['failed_trackings']
            self.system_metrics['average_tracking_duration'] = (
                (current_avg * (total_completed - 1) + duration) / total_completed
            )
        
        self.logger.info(f"Stopped tracking {tracking_id} with reason: {reason}")
        
        # Emit tracking stopped event
        await self.event_emitter.emit('tracking_stopped', {
            'tracking_id': tracking_id,
            'reason': reason,
            'final_performance_score': tracking.performance_score,
            'total_metrics': tracking.total_metrics.__dict__,
            'timestamp': datetime.utcnow()
        })
        
        return True
    
    async def _convert_analytics_to_metrics(self, platform: str, analytics: Dict[str, Any]) -> TrackingMetrics:
        """Convert platform-specific analytics to tracking metrics."""
        metrics = TrackingMetrics()
        
        # Platform-specific conversions
        if platform == 'youtube':
            metrics.views = analytics.get('views', 0)
            metrics.likes = analytics.get('likes', 0)
            metrics.comments = analytics.get('comments', 0)
            metrics.shares = analytics.get('shares', 0)
            
        elif platform == 'instagram':
            metrics.likes = analytics.get('likes', 0)
            metrics.comments = analytics.get('comments', 0)
            metrics.shares = analytics.get('shares', 0)
            metrics.saves = analytics.get('saved', 0)
            metrics.impressions = analytics.get('impressions', 0)
            metrics.reach = analytics.get('reach', 0)
            
        elif platform == 'tiktok':
            metrics.views = analytics.get('views', 0)
            metrics.likes = analytics.get('likes', 0)
            metrics.comments = analytics.get('comments', 0)
            metrics.shares = analytics.get('shares', 0)
            
        elif platform == 'twitter':
            metrics.impressions = analytics.get('impressions', 0)
            metrics.likes = analytics.get('likes', 0)
            metrics.shares = analytics.get('retweets', 0)
            metrics.comments = analytics.get('replies', 0)
            
        elif platform == 'spotify':
            metrics.views = analytics.get('streams', 0)  # Streams as views
            metrics.saves = analytics.get('saves', 0)
            metrics.likes = analytics.get('playlist_adds', 0)  # Playlist adds as likes
        
        # Calculate engagement rate if possible
        if metrics.impressions > 0:
            total_engagement = metrics.likes + metrics.shares + metrics.comments + metrics.saves
            metrics.engagement_rate = total_engagement / metrics.impressions
        elif metrics.views > 0:
            total_engagement = metrics.likes + metrics.shares + metrics.comments
            metrics.engagement_rate = total_engagement / metrics.views
        
        return metrics
    
    async def _check_performance_alerts(self, tracking: DistributionTracking, analysis: Dict[str, Any]) -> None:
        """Check for performance alerts and anomalies."""
        alerts = []
        
        # Check engagement rate
        if tracking.total_metrics.engagement_rate < tracking.alert_thresholds['low_engagement_threshold']:
            alerts.append({
                'type': 'low_engagement',
                'message': f"Low engagement rate: {tracking.total_metrics.engagement_rate:.2%}",
                'severity': 'warning',
                'timestamp': datetime.utcnow()
            })
        
        # Check performance score
        if tracking.performance_score < tracking.alert_thresholds['performance_drop_threshold']:
            alerts.append({
                'type': 'performance_drop',
                'message': f"Performance score below threshold: {tracking.performance_score:.2f}",
                'severity': 'warning',
                'timestamp': datetime.utcnow()
            })
        
        # Check for platform errors
        error_platforms = [
            platform for platform, pt in tracking.platforms.items()
            if pt.errors
        ]
        
        if len(error_platforms) / len(tracking.platforms) > tracking.alert_thresholds['high_error_rate_threshold']:
            alerts.append({
                'type': 'high_error_rate',
                'message': f"High error rate: {len(error_platforms)}/{len(tracking.platforms)} platforms",
                'severity': 'error',
                'timestamp': datetime.utcnow()
            })
        
        # Check for anomalies
        anomalies = analysis.get('anomalies', [])
        for anomaly in anomalies:
            if anomaly.get('confidence', 0) > tracking.alert_thresholds['anomaly_detection_sensitivity']:
                alerts.append({
                    'type': 'anomaly_detected',
                    'message': f"Anomaly detected: {anomaly.get('description', 'Unknown')}",
                    'severity': 'info',
                    'timestamp': datetime.utcnow()
                })
        
        # Store alerts
        if alerts:
            self.anomaly_alerts.extend(alerts)
            
            # Emit alert events
            for alert in alerts:
                await self.event_emitter.emit('performance_alert', {
                    'tracking_id': tracking.tracking_id,
                    'alert': alert
                })
            
            self.logger.warning(f"Generated {len(alerts)} alerts for tracking {tracking.tracking_id}")
    
    async def _start_background_tasks(self) -> None:
        """Start background tracking tasks."""
        # Start analytics collection task
        asyncio.create_task(self._collect_analytics_continuously())
        
        # Start performance analysis task
        asyncio.create_task(self._analyze_performance_continuously())
        
        # Start trending content detection
        asyncio.create_task(self._detect_trending_content())
        
        # Start data cleanup task
        asyncio.create_task(self._cleanup_old_data())
    
    async def _collect_analytics_continuously(self) -> None:
        """Continuously collect analytics data for active trackings."""
        while self.is_running:
            try:
                # Collect analytics for all active trackings
                for tracking_id in list(self.active_trackings.keys()):
                    try:
                        await self.collect_analytics_data(tracking_id)
                    except Exception as e:
                        self.logger.error(f"Analytics collection failed for {tracking_id}: {e}")
                
                await asyncio.sleep(self.tracking_interval)
                
            except Exception as e:
                self.logger.error(f"Error in analytics collection loop: {e}")
                await asyncio.sleep(self.tracking_interval)
    
    async def _analyze_performance_continuously(self) -> None:
        """Continuously analyze performance for active trackings."""
        while self.is_running:
            try:
                # Analyze performance for all active trackings
                for tracking_id in list(self.active_trackings.keys()):
                    try:
                        await self.analyze_performance(tracking_id)
                    except Exception as e:
                        self.logger.error(f"Performance analysis failed for {tracking_id}: {e}")
                
                await asyncio.sleep(self.analytics_interval)
                
            except Exception as e:
                self.logger.error(f"Error in performance analysis loop: {e}")
                await asyncio.sleep(self.analytics_interval)
    
    async def _detect_trending_content(self) -> None:
        """Detect trending content based on performance metrics."""
        while self.is_running:
            try:
                trending_candidates = []
                
                # Analyze recent trackings for trending patterns
                for tracking in list(self.active_trackings.values()):
                    if tracking.performance_score > 0.8:  # High performance threshold
                        total_engagement = (
                            tracking.total_metrics.likes +
                            tracking.total_metrics.shares +
                            tracking.total_metrics.comments
                        )
                        
                        if total_engagement > 1000:  # Engagement threshold
                            trending_candidates.append({
                                'tracking_id': tracking.tracking_id,
                                'content_id': tracking.content_id,
                                'performance_score': tracking.performance_score,
                                'total_engagement': total_engagement,
                                'platforms': list(tracking.platforms.keys()),
                                'detected_at': datetime.utcnow()
                            })
                
                # Update trending content list
                self.trending_content = sorted(
                    trending_candidates,
                    key=lambda x: x['performance_score'],
                    reverse=True
                )[:20]  # Keep top 20
                
                await asyncio.sleep(1800)  # Check every 30 minutes
                
            except Exception as e:
                self.logger.error(f"Error in trending content detection: {e}")
                await asyncio.sleep(1800)
    
    async def _cleanup_old_data(self) -> None:
        """Clean up old tracking data."""
        while self.is_running:
            try:
                # Clean up completed trackings older than 30 days
                cutoff_date = datetime.utcnow() - timedelta(days=30)
                
                old_trackings = [
                    tracking_id for tracking_id, tracking in self.completed_trackings.items()
                    if tracking.completed_at and tracking.completed_at < cutoff_date
                ]
                
                for tracking_id in old_trackings:
                    # Archive to database before removing
                    await self._archive_tracking(self.completed_trackings[tracking_id])
                    del self.completed_trackings[tracking_id]
                
                if old_trackings:
                    self.logger.info(f"Archived {len(old_trackings)} old trackings")
                
                # Clean up old alerts
                cutoff_alert_date = datetime.utcnow() - timedelta(days=7)
                self.anomaly_alerts = [
                    alert for alert in self.anomaly_alerts
                    if alert['timestamp'] > cutoff_alert_date
                ]
                
                await asyncio.sleep(86400)  # Run daily
                
            except Exception as e:
                self.logger.error(f"Error in data cleanup: {e}")
                await asyncio.sleep(86400)
    
    async def _load_existing_trackings(self) -> None:
        """Load existing active trackings from storage."""
        # This would load from database
        # For now, start with empty state
        pass
    
    async def _initialize_platform_adapters(self) -> None:
        """Initialize platform adapters for analytics collection."""
        # This would initialize platform adapters
        # For now, use mock adapters
        pass
    
    async def _save_all_trackings(self) -> None:
        """Save all tracking data to persistent storage."""
        try:
            # Save active trackings
            for tracking in self.active_trackings.values():
                await self._save_tracking(tracking)
            
            # Save completed trackings
            for tracking in self.completed_trackings.values():
                await self._save_tracking(tracking)
            
            self.logger.info("All tracking data saved successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to save tracking data: {e}")
    
    async def _save_tracking(self, tracking: DistributionTracking) -> None:
        """Save individual tracking to database."""
        # This would save to database
        pass
    
    async def _archive_tracking(self, tracking: DistributionTracking) -> None:
        """Archive tracking to long-term storage."""
        # This would archive to long-term storage
        pass
    
    def get_system_metrics(self) -> Dict[str, Any]:
        """Get current system metrics."""
        return {
            **self.system_metrics,
            'timestamp': datetime.utcnow().isoformat(),
            'active_trackings_count': len(self.active_trackings),
            'completed_trackings_count': len(self.completed_trackings),
            'trending_content_count': len(self.trending_content),
            'recent_alerts_count': len([
                alert for alert in self.anomaly_alerts
                if alert['timestamp'] > datetime.utcnow() - timedelta(hours=24)
            ]),
            'system_status': {
                'initialized': self.is_initialized,
                'running': self.is_running,
                'tracking_interval': self.tracking_interval,
                'analytics_interval': self.analytics_interval
            }
        }
    
    def get_trending_content(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get trending content list."""
        return self.trending_content[:limit]
    
    def get_recent_alerts(self, hours: int = 24) -> List[Dict[str, Any]]:
        """Get recent alerts."""
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)
        return [
            alert for alert in self.anomaly_alerts
            if alert['timestamp'] > cutoff_time
        ]
    
    async def get_tracking_analytics(
        self,
        tracking_id: Optional[UUID] = None,
        content_id: Optional[UUID] = None,
        platform: Optional[str] = None,
        time_range: Optional[Tuple[datetime, datetime]] = None
    ) -> Dict[str, Any]:
        """Get analytics data with optional filtering."""
        analytics = {
            'trackings': [],
            'aggregated_metrics': TrackingMetrics().__dict__,
            'platform_breakdown': defaultdict(lambda: TrackingMetrics().__dict__),
            'time_series': [],
            'insights': []
        }
        
        # Filter trackings
        all_trackings = {**self.active_trackings, **self.completed_trackings}
        filtered_trackings = []
        
        for tracking in all_trackings.values():
            # Apply filters
            if tracking_id and tracking.tracking_id != tracking_id:
                continue
            if content_id and tracking.content_id != content_id:
                continue
            if time_range:
                start_time, end_time = time_range
                if tracking.created_at < start_time or tracking.created_at > end_time:
                    continue
            
            filtered_trackings.append(tracking)
        
        # Aggregate data
        total_metrics = TrackingMetrics()
        platform_metrics = defaultdict(lambda: TrackingMetrics())
        
        for tracking in filtered_trackings:
            # Add to aggregated metrics
            total_metrics.views += tracking.total_metrics.views
            total_metrics.likes += tracking.total_metrics.likes
            total_metrics.shares += tracking.total_metrics.shares
            total_metrics.comments += tracking.total_metrics.comments
            total_metrics.impressions += tracking.total_metrics.impressions
            total_metrics.reach += tracking.total_metrics.reach
            total_metrics.revenue += tracking.total_metrics.revenue
            
            # Platform breakdown
            if platform:
                if platform in tracking.platforms:
                    pt = tracking.platforms[platform]
                    pm = platform_metrics[platform]
                    pm.views += pt.metrics.views
                    pm.likes += pt.metrics.likes
                    pm.shares += pt.metrics.shares
                    pm.comments += pt.metrics.comments
                    pm.impressions += pt.metrics.impressions
                    pm.reach += pt.metrics.reach
                    pm.revenue += pt.metrics.revenue
            else:
                for platform_name, pt in tracking.platforms.items():
                    pm = platform_metrics[platform_name]
                    pm.views += pt.metrics.views
                    pm.likes += pt.metrics.likes
                    pm.shares += pt.metrics.shares
                    pm.comments += pt.metrics.comments
                    pm.impressions += pt.metrics.impressions
                    pm.reach += pt.metrics.reach
                    pm.revenue += pt.metrics.revenue
            
            # Add tracking summary
            analytics['trackings'].append({
                'tracking_id': str(tracking.tracking_id),
                'content_id': str(tracking.content_id),
                'status': tracking.status.value,
                'performance_score': tracking.performance_score,
                'total_metrics': tracking.total_metrics.__dict__,
                'platforms': list(tracking.platforms.keys()),
                'created_at': tracking.created_at.isoformat()
            })
        
        analytics['aggregated_metrics'] = total_metrics.__dict__
        analytics['platform_breakdown'] = {
            platform: metrics.__dict__
            for platform, metrics in platform_metrics.items()
        }
        
        return analytics
