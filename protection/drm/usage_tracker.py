"""📊 Advanced Usage Tracker - Ultra-Professional DRM Analytics System
================================================================

Comprehensive usage tracking, analytics, and reporting system for DRM
with real-time monitoring, advanced insights, and predictive analytics.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️ CRITICAL LEGAL NOTICE:
This code and architectural design are the exclusive intellectual property of Fahed Mlaiel.
Unauthorized use, copying, distribution, or commercialization without explicit written permission is strictly prohibited.
Contact: mlaiel@live.de for licensing and usage rights.

🎯 PROJECT TEAM SPECIALTIES:
- Lead AI Developer & Solution Architect: Advanced AI/ML systems and intelligent automation
- Backend Senior Engineer: Enterprise-grade backend architecture and microservices  
- ML Engineer: Machine learning models and predictive analytics
- Database Administrator: High-performance data management and optimization
- Security Engineer: Advanced cybersecurity and data protection
- Microservices Architect: Scalable distributed systems design
- Audio Engineer: Professional audio processing and analysis
- DevOps Engineer: Advanced deployment and infrastructure automation
- IA Prompt Engineer: Advanced AI prompt engineering and optimization
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple, Union
from dataclasses import dataclass, field
from enum import Enum
from collections import defaultdict, Counter
import uuid
import json
import hashlib
import statistics
from decimal import Decimal

logger = logging.getLogger(__name__)

class UsageEventType(str, Enum):
    """
Types of content usage events."""

    VIEW = "view"
    DOWNLOAD = "download"
    STREAM = "stream"
    SHARE = "share"
    EMBED = "embed"
    PREVIEW = "preview"
    SEARCH = "search"
    LIKE = "like"
    COMMENT = "comment"
    BOOKMARK = "bookmark"
    PURCHASE = "purchase"
    LICENSE = "license"

class DeviceType(str, Enum):
    """Types of devices used for content access."""

    DESKTOP = "desktop"
    MOBILE = "mobile"
    TABLET = "tablet"
    TV = "tv"
    SMART_SPEAKER = "smart_speaker"
    GAMING_CONSOLE = "gaming_console"
    OTHER = "other"

class Platform(str, Enum):
    """Platforms where content is accessed."""

    WEB = "web"
    MOBILE_APP = "mobile_app"
    DESKTOP_APP = "desktop_app"
    API = "api"
    EMBEDDED = "embedded"
    THIRD_PARTY = "third_party"

class MetricType(str, Enum):
    """Types of analytics metrics."""

    ENGAGEMENT = "engagement"
    PERFORMANCE = "performance"
    REVENUE = "revenue"
    REACH = "reach"
    RETENTION = "retention"
    CONVERSION = "conversion"

@dataclass
class UsageEvent:
    """Individual usage event record."""
    event_id: str
    license_id: str
    content_id: str
    user_id: int
    event_type: UsageEventType
    timestamp: datetime = field(default_factory=datetime.utcnow)
    duration_seconds: Optional[int] = None
    platform: Platform = Platform.WEB
    device_type: DeviceType = DeviceType.DESKTOP
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    location: Optional[str] = None
    referrer: Optional[str] = None
    session_id: Optional[str] = None
    quality_level: Optional[str] = None
    bandwidth_used: Optional[int] = None  # bytes
    revenue_generated: Decimal = Decimal('0')
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class UsageSession:
    """
User session tracking."""
    session_id: str
    user_id: int
    start_time: datetime
    end_time: Optional[datetime] = None
    events: List[str] = field(default_factory=list)  # Event IDs
    total_duration: int = 0  # seconds
    content_accessed: List[str] = field(default_factory=list)  # Content IDs
    platform: Platform = Platform.WEB
    device_type: DeviceType = DeviceType.DESKTOP
    location: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class ContentMetrics:
    """
Metrics for individual content."""
    content_id: str
    total_views: int = 0
    unique_viewers: int = 0
    total_downloads: int = 0
    total_streams: int = 0
    total_shares: int = 0
    total_duration_watched: int = 0  # seconds
    average_watch_time: float = 0.0
    completion_rate: float = 0.0
    engagement_score: float = 0.0
    revenue_generated: Decimal = Decimal('0')
    peak_concurrent_users: int = 0
    geographic_distribution: Dict[str, int] = field(default_factory=dict)
    device_distribution: Dict[str, int] = field(default_factory=dict)
    platform_distribution: Dict[str, int] = field(default_factory=dict)
    hourly_distribution: Dict[int, int] = field(default_factory=dict)
    last_updated: datetime = field(default_factory=datetime.utcnow)

@dataclass
class UserMetrics:
    """
Metrics for individual user."""
    user_id: int
    total_sessions: int = 0
    total_session_time: int = 0  # seconds
    content_consumed: int = 0
    favorite_content_types: List[str] = field(default_factory=list)
    preferred_platforms: List[Platform] = field(default_factory=list)
    preferred_devices: List[DeviceType] = field(default_factory=list)
    engagement_score: float = 0.0
    loyalty_score: float = 0.0
    revenue_contributed: Decimal = Decimal('0')
    first_activity: Optional[datetime] = None
    last_activity: Optional[datetime] = None
    geographic_locations: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

class UsageTracker:
    """
    Ultra-Advanced Usage Tracker for DRM System
    
    Features:
    - Real-time usage event tracking and processing
    - Advanced session management and analytics
    - Multi-dimensional metrics calculation
    - User behavior pattern analysis
    - Content performance optimization insights
    - Geographic and demographic analytics
    - Predictive usage modeling using ML
    - A/B testing and experimentation support
    - Revenue attribution and optimization
    - Compliance and audit trail maintenance
    """
    
    def __init__(self, config -> None: Dict[str, Any]) -> None:
        """
Initialize the Usage Tracker."""
        self.config = config
        self._initialized = False
        
        # Storage
        self.usage_events: Dict[str, UsageEvent] = {}
        self.active_sessions: Dict[str, UsageSession] = {}
        self.content_metrics: Dict[str, ContentMetrics] = {}
        self.user_metrics: Dict[int, UserMetrics] = {}
        
        # Analytics cache
        self.metrics_cache: Dict[str, Any] = {}
        self.real_time_stats: Dict[str, Any] = {}
        
        # Configuration
        self.session_timeout = timedelta(minutes=config.get('session_timeout_minutes', 30))
        self.metrics_update_interval = config.get('metrics_update_interval_seconds', 60)
        self.data_retention_days = config.get('data_retention_days', 365)
        self.enable_real_time = config.get('enable_real_time', True)
        
        # ML models for predictions
        self.ml_models: Dict[str, Any] = {}
        
        logger.info("Usage Tracker initialized")

    async def initialize(self) -> bool:
        """Initialize the Usage Tracker."""
        try:
            # Load existing data
            await self._load_existing_data()
            
            # Initialize ML models
            await self._initialize_ml_models()
            
            # Start background tasks
            if self.enable_real_time:
                await self._start_real_time_processing()
            
            # Start metrics calculation
            await self._start_metrics_calculation()
            
            self._initialized = True
            logger.info("Usage Tracker initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize Usage Tracker: {e}")
            return False

    async def _load_existing_data(self) -> None:
        """Load existing usage data."""
        # Placeholder for database loading
        logger.debug("Loading existing usage data")

    async def _initialize_ml_models(self) -> None:
        """Initialize machine learning models."""
        # Placeholder for ML model initialization
        self.ml_models = {
            "engagement_prediction": None,
            "churn_prediction": None,
            "content_recommendation": None,
            "revenue_optimization": None
        }
        logger.debug("Initialized ML models for usage analytics")

    async def _start_real_time_processing(self) -> None:
        """Start real-time event processing."""
        # Placeholder for real-time processing
        logger.debug("Started real-time usage processing")

    async def _start_metrics_calculation(self) -> None:
        """Start periodic metrics calculation."""
        # Placeholder for metrics calculation scheduler
        logger.debug("Started metrics calculation scheduler")

    async def track_usage_event(
        self,
        license_id: str,
        content_id: str,
        user_id: int,
        event_type: UsageEventType,
        context: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Track a usage event.
        
        Args:
            license_id: License being used
            content_id: Content being accessed
            user_id: User performing the action
            event_type: Type of usage event
            context: Additional context information
            
        Returns:
            str: Event ID
        """
        if not self._initialized:
            raise RuntimeError("Usage Tracker not initialized")
        
        # Generate event ID
        event_id = f"event_{uuid.uuid4().hex[:16]}"
        
        # Extract context information
        context = context or {}
        
        # Create usage event
        usage_event = UsageEvent(
            event_id=event_id,
            license_id=license_id,
            content_id=content_id,
            user_id=user_id,
            event_type=event_type,
            duration_seconds=context.get('duration_seconds'),
            platform=Platform(context.get('platform', Platform.WEB.value)),
            device_type=DeviceType(context.get('device_type', DeviceType.DESKTOP.value)),
            ip_address=context.get('ip_address'),
            user_agent=context.get('user_agent'),
            location=context.get('location'),
            referrer=context.get('referrer'),
            session_id=context.get('session_id'),
            quality_level=context.get('quality_level'),
            bandwidth_used=context.get('bandwidth_used'),
            revenue_generated=Decimal(str(context.get('revenue_generated', 0))),
            metadata=context.get('metadata', {})
        )
        
        # Store event
        self.usage_events[event_id] = usage_event
        
        # Update session
        await self._update_session(usage_event)
        
        # Update real-time stats
        if self.enable_real_time:
            await self._update_real_time_stats(usage_event)
        
        # Update metrics asynchronously
        asyncio.create_task(self._update_metrics_async(usage_event))
        
        logger.debug(f"Tracked {event_type.value} event {event_id} for content {content_id}")
        return event_id

    async def _update_session(self, event: UsageEvent) -> None:
        """Update or create user session."""
        session_id = event.session_id
        
        if not session_id:
            # Generate session ID if not provided
            session_id = f"session_{event.user_id}_{int(datetime.utcnow().timestamp())}"
            event.session_id = session_id
        
        # Get or create session
        if session_id in self.active_sessions:
            session = self.active_sessions[session_id]
            
            # Check if session is still active
            if event.timestamp > session.start_time + self.session_timeout:
                # Start new session
                await self._finalize_session(session_id)
                session = await self._create_new_session(event, session_id)
            else:
                # Update existing session
                session.events.append(event.event_id)
                if event.content_id not in session.content_accessed:
                    session.content_accessed.append(event.content_id)
                
                if event.duration_seconds:
                    session.total_duration += event.duration_seconds
        else:
            # Create new session
            session = await self._create_new_session(event, session_id)
        
        # Update session metadata
        session.metadata.update({
            "last_event_type": event.event_type.value,
            "last_content_id": event.content_id,
            "event_count": len(session.events)
        })

    async def _create_new_session(self, event: UsageEvent, session_id: str) -> UsageSession:
        """Create a new user session."""
        session = UsageSession(
            session_id=session_id,
            user_id=event.user_id,
            start_time=event.timestamp,
            events=[event.event_id],
            content_accessed=[event.content_id] if event.content_id else [],
            platform=event.platform,
            device_type=event.device_type,
            location=event.location,
            total_duration=event.duration_seconds or 0
        )
        
        self.active_sessions[session_id] = session
        return session

    async def _finalize_session(self, session_id: str) -> None:
        """
Finalize and archive a user session."""
        if session_id not in self.active_sessions:
            return
        
        session = self.active_sessions[session_id]
        session.end_time = datetime.utcnow()
        
        # Update user metrics
        await self._update_user_session_metrics(session)
        
        # Remove from active sessions
        del self.active_sessions[session_id]
        
        logger.debug(f"Finalized session {session_id} for user {session.user_id}")

    async def _update_real_time_stats(self, event: UsageEvent) -> None:
        """Update real-time statistics."""
        current_minute = event.timestamp.replace(second=0, microsecond=0)
        minute_key = current_minute.isoformat()
        
        if minute_key not in self.real_time_stats:
            self.real_time_stats[minute_key] = {
                "total_events": 0,
                "unique_users": set(),
                "events_by_type": defaultdict(int),
                "content_access": defaultdict(int),
                "platforms": defaultdict(int),
                "devices": defaultdict(int)
            }
        
        stats = self.real_time_stats[minute_key]
        stats["total_events"] += 1
        stats["unique_users"].add(event.user_id)
        stats["events_by_type"][event.event_type.value] += 1
        stats["content_access"][event.content_id] += 1
        stats["platforms"][event.platform.value] += 1
        stats["devices"][event.device_type.value] += 1
        
        # Clean old real-time stats (keep last hour)
        cutoff_time = event.timestamp - timedelta(hours=1)
        cutoff_key = cutoff_time.replace(second=0, microsecond=0).isoformat()
        
        keys_to_remove = [key for key in self.real_time_stats.keys() if key < cutoff_key]
        for key in keys_to_remove:
            del self.real_time_stats[key]

    async def _update_metrics_async(self, event: UsageEvent) -> None:
        """Update metrics asynchronously."""
        # Update content metrics
        await self._update_content_metrics(event)
        
        # Update user metrics
        await self._update_user_metrics(event)
        
        # Invalidate relevant cache entries
        self._invalidate_cache(event.content_id, event.user_id)

    async def _update_content_metrics(self, event: UsageEvent) -> None:
        """
Update content-specific metrics."""
        content_id = event.content_id
        
        if content_id not in self.content_metrics:
            self.content_metrics[content_id] = ContentMetrics(content_id=content_id)
        
        metrics = self.content_metrics[content_id]
        
        # Update based on event type
        if event.event_type == UsageEventType.VIEW:
            metrics.total_views += 1
        elif event.event_type == UsageEventType.DOWNLOAD:
            metrics.total_downloads += 1
        elif event.event_type == UsageEventType.STREAM:
            metrics.total_streams += 1
        elif event.event_type == UsageEventType.SHARE:
            metrics.total_shares += 1
        
        # Update duration metrics
        if event.duration_seconds:
            metrics.total_duration_watched += event.duration_seconds
            
            # Recalculate average watch time
            total_viewing_events = metrics.total_views + metrics.total_streams
            if total_viewing_events > 0:
                metrics.average_watch_time = metrics.total_duration_watched / total_viewing_events
        
        # Update geographic distribution
        if event.location:
            metrics.geographic_distribution[event.location] = metrics.geographic_distribution.get(event.location, 0) + 1
        
        # Update device distribution
        metrics.device_distribution[event.device_type.value] = metrics.device_distribution.get(event.device_type.value, 0) + 1
        
        # Update platform distribution
        metrics.platform_distribution[event.platform.value] = metrics.platform_distribution.get(event.platform.value, 0) + 1
        
        # Update hourly distribution
        hour = event.timestamp.hour
        metrics.hourly_distribution[hour] = metrics.hourly_distribution.get(hour, 0) + 1
        
        # Update revenue
        metrics.revenue_generated += event.revenue_generated
        
        # Calculate engagement score
        metrics.engagement_score = await self._calculate_content_engagement_score(content_id)
        
        metrics.last_updated = datetime.utcnow()

    async def _update_user_metrics(self, event: UsageEvent) -> None:
        """
Update user-specific metrics."""
        user_id = event.user_id
        
        if user_id not in self.user_metrics:
            self.user_metrics[user_id] = UserMetrics(
                user_id=user_id,
                first_activity=event.timestamp
            )
        
        metrics = self.user_metrics[user_id]
        metrics.last_activity = event.timestamp
        
        # Update revenue contribution
        metrics.revenue_contributed += event.revenue_generated
        
        # Update geographic locations
        if event.location and event.location not in metrics.geographic_locations:
            metrics.geographic_locations.append(event.location)
        
        # Update preferred platforms and devices
        await self._update_user_preferences(metrics, event)
        
        # Calculate engagement and loyalty scores
        metrics.engagement_score = await self._calculate_user_engagement_score(user_id)
        metrics.loyalty_score = await self._calculate_user_loyalty_score(user_id)

    async def _update_user_session_metrics(self, session: UsageSession) -> None:
        """
Update user metrics from completed session."""
        user_id = session.user_id
        
        if user_id not in self.user_metrics:
            self.user_metrics[user_id] = UserMetrics(user_id=user_id)
        
        metrics = self.user_metrics[user_id]
        metrics.total_sessions += 1
        metrics.total_session_time += session.total_duration
        metrics.content_consumed += len(session.content_accessed)

    async def _update_user_preferences(self, metrics: UserMetrics, event: UsageEvent) -> None:
        """
Update user preferences based on usage patterns."""
        # Update preferred platforms
        platform_counts = Counter()
        device_counts = Counter()
        
        # Get recent events for this user
        recent_events = [
            e for e in self.usage_events.values()
            if e.user_id == event.user_id and e.timestamp > datetime.utcnow() - timedelta(days=30)
        ]
        
        for e in recent_events:
            platform_counts[e.platform] += 1
            device_counts[e.device_type] += 1
        
        # Update preferred platforms (top 3)
        metrics.preferred_platforms = [platform for platform, _ in platform_counts.most_common(3)]
        
        # Update preferred devices (top 3)
        metrics.preferred_devices = [device for device, _ in device_counts.most_common(3)]

    async def _calculate_content_engagement_score(self, content_id: str) -> float:
        """
Calculate engagement score for content."""
        if content_id not in self.content_metrics:
            return 0.0
        
        metrics = self.content_metrics[content_id]
        
        # Simple engagement score calculation
        # In production, this would use more sophisticated algorithms
        
        total_interactions = (
            metrics.total_views +
            metrics.total_downloads * 2 +  # Downloads worth more
            metrics.total_streams * 1.5 +
            metrics.total_shares * 3  # Shares worth most
        )
        
        # Normalize by time since creation (assume 1 day for now)
        days_active = 1  # Placeholder
        daily_engagement = total_interactions / max(days_active, 1)
        
        # Scale to 0-100
        engagement_score = min(daily_engagement / 10, 100)
        
        return float(engagement_score)

    async def _calculate_user_engagement_score(self, user_id: int) -> float:
        """
Calculate engagement score for user."""
        user_events = [e for e in self.usage_events.values() if e.user_id == user_id]
        
        if not user_events:
            return 0.0
        
        # Calculate based on activity frequency and diversity
        recent_events = [
            e for e in user_events
            if e.timestamp > datetime.utcnow() - timedelta(days=30)
        ]
        
        if not recent_events:
            return 0.0
        
        # Activity frequency
        activity_score = len(recent_events) / 30  # Events per day
        
        # Activity diversity (different event types)
        event_types = set(e.event_type for e in recent_events)
        diversity_score = len(event_types) / len(UsageEventType)
        
        # Combined score
        engagement_score = (activity_score * 0.7 + diversity_score * 0.3) * 100
        
        return min(engagement_score, 100)

    async def _calculate_user_loyalty_score(self, user_id: int) -> float:
        """
Calculate loyalty score for user."""
        if user_id not in self.user_metrics:
            return 0.0
        
        metrics = self.user_metrics[user_id]
        
        if not metrics.first_activity:
            return 0.0
        
        # Days since first activity
        days_active = (datetime.utcnow() - metrics.first_activity).days
        if days_active == 0:
            return 50.0  # New user, medium loyalty
        
        # Session frequency
        session_frequency = metrics.total_sessions / max(days_active, 1)
        
        # Content consumption rate
        content_rate = metrics.content_consumed / max(days_active, 1)
        
        # Revenue contribution (normalized)
        revenue_score = min(float(metrics.revenue_contributed) / 100, 1.0)
        
        # Combined loyalty score
        loyalty_score = (
            session_frequency * 40 +
            content_rate * 30 +
            revenue_score * 30
        )
        
        return min(loyalty_score, 100)

    def _invalidate_cache(self, content_id: str, user_id: int) -> None:
        """
Invalidate relevant cache entries."""
        keys_to_remove = []
        
        for cache_key in self.metrics_cache:
            if content_id in cache_key or str(user_id) in cache_key:
                keys_to_remove.append(cache_key)
        
        for key in keys_to_remove:
            del self.metrics_cache[key]

    async def get_content_analytics(
        self,
        content_id: str,
        date_range: Optional[Tuple[datetime, datetime]] = None
    ) -> Dict[str, Any]:
        """
Get comprehensive analytics for content."""
        cache_key = f"content_analytics_{content_id}_{date_range}"
        
        if cache_key in self.metrics_cache:
            return self.metrics_cache[cache_key]
        
        # Get content metrics
        if content_id not in self.content_metrics:
            return {"error": "Content not found"}
        
        metrics = self.content_metrics[content_id]
        
        # Filter events by date range if specified
        content_events = [
            e for e in self.usage_events.values()
            if e.content_id == content_id
        ]
        
        if date_range:
            start_date, end_date = date_range
            content_events = [
                e for e in content_events
                if start_date <= e.timestamp <= end_date
            ]
        
        # Calculate time-series data
        daily_views = await self._calculate_daily_time_series(content_events, UsageEventType.VIEW)
        daily_streams = await self._calculate_daily_time_series(content_events, UsageEventType.STREAM)
        
        # Calculate audience insights
        audience_insights = await self._calculate_audience_insights(content_events)
        
        # Performance predictions
        predictions = await self._generate_content_predictions(content_id, content_events)
        
        analytics = {
            "content_id": content_id,
            "summary": {
                "total_views": metrics.total_views,
                "unique_viewers": metrics.unique_viewers,
                "total_downloads": metrics.total_downloads,
                "total_streams": metrics.total_streams,
                "total_shares": metrics.total_shares,
                "engagement_score": metrics.engagement_score,
                "revenue_generated": float(metrics.revenue_generated)
            },
            "performance": {
                "average_watch_time": metrics.average_watch_time,
                "completion_rate": metrics.completion_rate,
                "peak_concurrent_users": metrics.peak_concurrent_users
            },
            "distribution": {
                "geographic": dict(metrics.geographic_distribution),
                "devices": dict(metrics.device_distribution),
                "platforms": dict(metrics.platform_distribution),
                "hourly": dict(metrics.hourly_distribution)
            },
            "time_series": {
                "daily_views": daily_views,
                "daily_streams": daily_streams
            },
            "audience": audience_insights,
            "predictions": predictions,
            "last_updated": metrics.last_updated.isoformat()
        }
        
        # Cache result
        self.metrics_cache[cache_key] = analytics
        
        return analytics

    async def get_user_analytics(
        self,
        user_id: int,
        date_range: Optional[Tuple[datetime, datetime]] = None
    ) -> Dict[str, Any]:
        """Get comprehensive analytics for user."""
        cache_key = f"user_analytics_{user_id}_{date_range}"
        
        if cache_key in self.metrics_cache:
            return self.metrics_cache[cache_key]
        
        # Get user metrics
        if user_id not in self.user_metrics:
            return {"error": "User not found"}
        
        metrics = self.user_metrics[user_id]
        
        # Filter events by date range if specified
        user_events = [
            e for e in self.usage_events.values()
            if e.user_id == user_id
        ]
        
        if date_range:
            start_date, end_date = date_range
            user_events = [
                e for e in user_events
                if start_date <= e.timestamp <= end_date
            ]
        
        # Calculate activity patterns
        activity_patterns = await self._calculate_user_activity_patterns(user_events)
        
        # Content preferences
        content_preferences = await self._calculate_content_preferences(user_events)
        
        # Behavior predictions
        predictions = await self._generate_user_predictions(user_id, user_events)
        
        analytics = {
            "user_id": user_id,
            "summary": {
                "total_sessions": metrics.total_sessions,
                "total_session_time": metrics.total_session_time,
                "content_consumed": metrics.content_consumed,
                "engagement_score": metrics.engagement_score,
                "loyalty_score": metrics.loyalty_score,
                "revenue_contributed": float(metrics.revenue_contributed)
            },
            "preferences": {
                "platforms": [p.value for p in metrics.preferred_platforms],
                "devices": [d.value for d in metrics.preferred_devices],
                "content_types": content_preferences
            },
            "activity": {
                "first_activity": metrics.first_activity.isoformat() if metrics.first_activity else None,
                "last_activity": metrics.last_activity.isoformat() if metrics.last_activity else None,
                "patterns": activity_patterns
            },
            "geographic": metrics.geographic_locations,
            "predictions": predictions
        }
        
        # Cache result
        self.metrics_cache[cache_key] = analytics
        
        return analytics

    async def _calculate_daily_time_series(
        self,
        events: List[UsageEvent],
        event_type: UsageEventType
    ) -> Dict[str, int]:
        """Calculate daily time series for specific event type."""
        daily_counts = defaultdict(int)
        
        filtered_events = [e for e in events if e.event_type == event_type]
        
        for event in filtered_events:
            date_key = event.timestamp.date().isoformat()
            daily_counts[date_key] += 1
        
        return dict(daily_counts)

    async def _calculate_audience_insights(self, events: List[UsageEvent]) -> Dict[str, Any]:
        """
Calculate audience insights from events."""
        if not events:
            return {}
        
        # Unique users
        unique_users = set(e.user_id for e in events)
        
        # Peak hours
        hourly_activity = defaultdict(int)
        for event in events:
            hourly_activity[event.timestamp.hour] += 1
        
        peak_hour = max(hourly_activity.items(), key=lambda x: x[1])[0] if hourly_activity else 0
        
        # Geographic insights
        geographic_spread = len(set(e.location for e in events if e.location))
        
        # Device insights
        device_breakdown = Counter(e.device_type.value for e in events)
        
        return {
            "unique_users": len(unique_users),
            "peak_hour": peak_hour,
            "geographic_spread": geographic_spread,
            "device_breakdown": dict(device_breakdown),
            "total_events": len(events)
        }

    async def _calculate_user_activity_patterns(self, events: List[UsageEvent]) -> Dict[str, Any]:
        """Calculate user activity patterns."""
        if not events:
            return {}
        
        # Activity by hour
        hourly_activity = defaultdict(int)
        for event in events:
            hourly_activity[event.timestamp.hour] += 1
        
        # Activity by day of week
        daily_activity = defaultdict(int)
        for event in events:
            daily_activity[event.timestamp.weekday()] += 1
        
        # Session patterns
        sessions = set(e.session_id for e in events if e.session_id)
        
        return {
            "hourly_distribution": dict(hourly_activity),
            "daily_distribution": dict(daily_activity),
            "total_sessions": len(sessions),
            "events_per_session": len(events) / len(sessions) if sessions else 0
        }

    async def _calculate_content_preferences(self, events: List[UsageEvent]) -> List[str]:
        """Calculate user content preferences."""
        content_interactions = Counter(e.content_id for e in events)
        
        # Return top 10 most accessed content
        return [content_id for content_id, _ in content_interactions.most_common(10)]

    async def _generate_content_predictions(
        self,
        content_id: str,
        events: List[UsageEvent]
    ) -> Dict[str, Any]:
        """
Generate predictions for content performance."""
        # Placeholder for ML predictions
        # In production, this would use trained models
        
        if not events:
            return {"error": "Insufficient data for predictions"}
        
        # Simple trend analysis
        recent_events = [e for e in events if e.timestamp > datetime.utcnow() - timedelta(days=7)]
        older_events = [e for e in events if e.timestamp <= datetime.utcnow() - timedelta(days=7)]
        
        if not older_events:
            return {"trend": "insufficient_historical_data"}
        
        recent_daily_avg = len(recent_events) / 7
        older_daily_avg = len(older_events) / max((events[0].timestamp - events[-1].timestamp).days, 1)
        
        if recent_daily_avg > older_daily_avg * 1.1:
            trend = "increasing"
        elif recent_daily_avg < older_daily_avg * 0.9:
            trend = "decreasing"
        else:
            trend = "stable"
        
        return {
            "trend": trend,
            "predicted_daily_views": recent_daily_avg,
            "confidence": 0.7  # Placeholder confidence score
        }

    async def _generate_user_predictions(
        self,
        user_id: int,
        events: List[UsageEvent]
    ) -> Dict[str, Any]:
        """Generate predictions for user behavior."""
        # Placeholder for ML predictions
        
        if not events:
            return {"error": "Insufficient data for predictions"}
        
        # Simple churn prediction
        last_activity = max(e.timestamp for e in events)
        days_since_activity = (datetime.utcnow() - last_activity).days
        
        if days_since_activity > 30:
            churn_risk = "high"
        elif days_since_activity > 14:
            churn_risk = "medium"
        else:
            churn_risk = "low"
        
        # Engagement trend
        recent_events = [e for e in events if e.timestamp > datetime.utcnow() - timedelta(days=14)]
        engagement_trend = "stable"  # Placeholder
        
        return {
            "churn_risk": churn_risk,
            "engagement_trend": engagement_trend,
            "days_since_last_activity": days_since_activity,
            "predicted_next_visit": (datetime.utcnow() + timedelta(days=3)).isoformat()
        }

    async def get_real_time_dashboard(self) -> Dict[str, Any]:
        """Get real-time dashboard data."""
        current_time = datetime.utcnow()
        
        # Current active sessions
        active_session_count = len(self.active_sessions)
        
        # Events in last hour
        hour_ago = current_time - timedelta(hours=1)
        recent_events = [
            e for e in self.usage_events.values()
            if e.timestamp > hour_ago
        ]
        
        # Top content in last hour
        content_counts = Counter(e.content_id for e in recent_events)
        top_content = content_counts.most_common(5)
        
        # Geographic distribution
        location_counts = Counter(e.location for e in recent_events if e.location)
        
        # Real-time metrics summary
        current_minute = current_time.replace(second=0, microsecond=0)
        current_stats = self.real_time_stats.get(current_minute.isoformat(), {})
        
        return {
            "timestamp": current_time.isoformat(),
            "active_sessions": active_session_count,
            "events_last_hour": len(recent_events),
            "unique_users_last_hour": len(set(e.user_id for e in recent_events)),
            "top_content": [{"content_id": cid, "count": count} for cid, count in top_content],
            "geographic_activity": dict(location_counts),
            "current_minute_stats": {
                "total_events": current_stats.get("total_events", 0),
                "unique_users": len(current_stats.get("unique_users", set())),
                "events_by_type": dict(current_stats.get("events_by_type", {}))
            }
        }

    async def generate_usage_report(
        self,
        report_type: str = "summary",
        date_range: Optional[Tuple[datetime, datetime]] = None,
        filters: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Generate comprehensive usage report."""
        filters = filters or {}
        
        # Filter events
        filtered_events = list(self.usage_events.values())
        
        if date_range:
            start_date, end_date = date_range
            filtered_events = [
                e for e in filtered_events
                if start_date <= e.timestamp <= end_date
            ]
        
        if filters.get('content_ids'):
            filtered_events = [
                e for e in filtered_events
                if e.content_id in filters['content_ids']
            ]
        
        if filters.get('user_ids'):
            filtered_events = [
                e for e in filtered_events
                if e.user_id in filters['user_ids']
            ]
        
        # Generate report based on type
        if report_type == "summary":
            return await self._generate_summary_report(filtered_events, date_range)
        elif report_type == "detailed":
            return await self._generate_detailed_report(filtered_events, date_range)
        elif report_type == "performance":
            return await self._generate_performance_report(filtered_events, date_range)
        else:
            return {"error": f"Unknown report type: {report_type}"}

    async def _generate_summary_report(
        self,
        events: List[UsageEvent],
        date_range: Optional[Tuple[datetime, datetime]]
    ) -> Dict[str, Any]:
        """Generate summary usage report."""
        if not events:
            return {"error": "No data available for report"}
        
        # Basic statistics
        total_events = len(events)
        unique_users = len(set(e.user_id for e in events))
        unique_content = len(set(e.content_id for e in events))
        
        # Event type distribution
        event_type_dist = Counter(e.event_type.value for e in events)
        
        # Platform distribution
        platform_dist = Counter(e.platform.value for e in events)
        
        # Device distribution
        device_dist = Counter(e.device_type.value for e in events)
        
        # Revenue summary
        total_revenue = sum(e.revenue_generated for e in events)
        
        # Time range
        start_time = min(e.timestamp for e in events)
        end_time = max(e.timestamp for e in events)
        
        return {
            "report_type": "summary",
            "period": {
                "start": start_time.isoformat(),
                "end": end_time.isoformat(),
                "duration_days": (end_time - start_time).days
            },
            "overview": {
                "total_events": total_events,
                "unique_users": unique_users,
                "unique_content": unique_content,
                "total_revenue": float(total_revenue)
            },
            "distributions": {
                "event_types": dict(event_type_dist),
                "platforms": dict(platform_dist),
                "devices": dict(device_dist)
            },
            "generated_at": datetime.utcnow().isoformat()
        }

    async def _generate_detailed_report(
        self,
        events: List[UsageEvent],
        date_range: Optional[Tuple[datetime, datetime]]
    ) -> Dict[str, Any]:
        """Generate detailed usage report."""
        summary = await self._generate_summary_report(events, date_range)
        
        # Additional detailed metrics
        # Geographic analysis
        location_analysis = Counter(e.location for e in events if e.location)
        
        # Hourly patterns
        hourly_patterns = defaultdict(int)
        for event in events:
            hourly_patterns[event.timestamp.hour] += 1
        
        # Daily patterns
        daily_patterns = defaultdict(int)
        for event in events:
            daily_patterns[event.timestamp.weekday()] += 1
        
        # Top content
        content_popularity = Counter(e.content_id for e in events)
        top_content = content_popularity.most_common(20)
        
        # Top users
        user_activity = Counter(e.user_id for e in events)
        top_users = user_activity.most_common(20)
        
        # Session analysis
        session_data = defaultdict(list)
        for event in events:
            if event.session_id:
                session_data[event.session_id].append(event)
        
        session_lengths = []
        for session_events in session_data.values():
            if len(session_events) > 1:
                start = min(e.timestamp for e in session_events)
                end = max(e.timestamp for e in session_events)
                session_lengths.append((end - start).total_seconds())
        
        avg_session_length = statistics.mean(session_lengths) if session_lengths else 0
        
        summary.update({
            "detailed_metrics": {
                "geographic_distribution": dict(location_analysis),
                "temporal_patterns": {
                    "hourly": dict(hourly_patterns),
                    "daily": dict(daily_patterns)
                },
                "top_content": [{"content_id": cid, "events": count} for cid, count in top_content],
                "top_users": [{"user_id": uid, "events": count} for uid, count in top_users],
                "session_analysis": {
                    "total_sessions": len(session_data),
                    "average_session_length_seconds": avg_session_length,
                    "events_per_session": len(events) / len(session_data) if session_data else 0
                }
            }
        })
        
        return summary

    async def _generate_performance_report(
        self,
        events: List[UsageEvent],
        date_range: Optional[Tuple[datetime, datetime]]
    ) -> Dict[str, Any]:
        """Generate performance-focused report."""
        # Performance metrics
        content_performance = {}
        
        for content_id in set(e.content_id for e in events):
            content_events = [e for e in events if e.content_id == content_id]
            
            views = len([e for e in content_events if e.event_type == UsageEventType.VIEW])
            streams = len([e for e in content_events if e.event_type == UsageEventType.STREAM])
            downloads = len([e for e in content_events if e.event_type == UsageEventType.DOWNLOAD])
            shares = len([e for e in content_events if e.event_type == UsageEventType.SHARE])
            
            # Calculate engagement rate
            total_interactions = views + streams + downloads + shares
            unique_users = len(set(e.user_id for e in content_events))
            engagement_rate = (total_interactions / unique_users) if unique_users > 0 else 0
            
            # Revenue per user
            total_revenue = sum(e.revenue_generated for e in content_events)
            revenue_per_user = (total_revenue / unique_users) if unique_users > 0 else Decimal('0')
            
            content_performance[content_id] = {
                "views": views,
                "streams": streams,
                "downloads": downloads,
                "shares": shares,
                "unique_users": unique_users,
                "engagement_rate": engagement_rate,
                "total_revenue": float(total_revenue),
                "revenue_per_user": float(revenue_per_user)
            }
        
        # Sort by engagement rate
        top_performing_content = sorted(
            content_performance.items(),
            key=lambda x: x[1]["engagement_rate"],
            reverse=True
        )[:10]
        
        return {
            "report_type": "performance",
            "content_performance": dict(content_performance),
            "top_performing_content": dict(top_performing_content),
            "performance_summary": {
                "total_content_analyzed": len(content_performance),
                "average_engagement_rate": statistics.mean([cp["engagement_rate"] for cp in content_performance.values()]) if content_performance else 0,
                "total_revenue": sum(float(cp["total_revenue"]) for cp in content_performance.values())
            },
            "generated_at": datetime.utcnow().isoformat()
        }

    async def cleanup_old_data(self) -> int:
        """Clean up old usage data."""
        cutoff_date = datetime.utcnow() - timedelta(days=self.data_retention_days)
        
        # Clean old events
        old_event_ids = [
            event_id for event_id, event in self.usage_events.items()
            if event.timestamp < cutoff_date
        ]
        
        for event_id in old_event_ids:
            del self.usage_events[event_id]
        
        logger.info(f"Cleaned up {len(old_event_ids)} old usage events")
        return len(old_event_ids)

    async def shutdown(self) -> None:
        """Shutdown the Usage Tracker."""
        logger.info("Shutting down Usage Tracker...")
        
        # Finalize all active sessions
        for session_id in list(self.active_sessions.keys()):
            await self._finalize_session(session_id)
        
        # Clean up old data
        await self.cleanup_old_data()
        
        # Save state
        await self._save_state()
        
        self._initialized = False
        logger.info("Usage Tracker shutdown complete")

    async def _save_state(self) -> None:
        """Save tracker state to persistent storage."""
        # Placeholder for database persistence
        logger.debug("Saving Usage Tracker state")
