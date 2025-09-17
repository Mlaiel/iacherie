"""👤 User Interaction Performance Profiler
==========================================

Advanced user interaction performance profiling system for the Ainflue Creator Economy platform.
Monitors user sessions, click-to-load times, form submissions, and navigation patterns.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️ INTELLECTUAL PROPERTY WARNING:
=====================================
This code is proprietary to Fahed Mlaiel <mlaiel@live.de>
- Commercial use FORBIDDEN without written authorization
- Reverse engineering STRICTLY PROHIBITED
- Distribution FORBIDDEN without explicit license
- Violation = Automatic legal prosecution

🏢 ENTERPRISE USAGE:
- Enterprise license available on request
- Technical support included with license
- Maintenance and updates assured
- Technical team training provided
"""

import asyncio
import logging
import time
import threading
from typing import Dict, List, Optional, Any, Callable, Union
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import json
import statistics
from collections import defaultdict, deque
import uuid

from prometheus_client import Counter, Gauge, Histogram, Summary

logger = logging.getLogger(__name__)


class InteractionType(Enum):
    """Types of user interactions"""
    PAGE_LOAD = "page_load"
    BUTTON_CLICK = "button_click"
    FORM_SUBMISSION = "form_submission"
    SEARCH = "search"
    NAVIGATION = "navigation"
    SCROLL = "scroll"
    VIDEO_PLAY = "video_play"
    VIDEO_PAUSE = "video_pause"
    CONTENT_UPLOAD = "content_upload"
    COLLABORATION_REQUEST = "collaboration_request"
    PAYMENT = "payment"
    PROFILE_UPDATE = "profile_update"
    CHAT_MESSAGE = "chat_message"
    LIKE = "like"
    SHARE = "share"
    COMMENT = "comment"
    FOLLOW = "follow"


class UserRole(Enum):
    """User roles in Creator Economy"""
    CREATOR = "creator"
    BRAND = "brand"
    VIEWER = "viewer"
    ADMIN = "admin"
    MODERATOR = "moderator"
    GUEST = "guest"


class DeviceType(Enum):
    """Device types"""
    DESKTOP = "desktop"
    MOBILE = "mobile"
    TABLET = "tablet"
    TV = "tv"
    UNKNOWN = "unknown"


class SessionQuality(Enum):
    """Session quality levels"""
    EXCELLENT = "excellent"
    GOOD = "good"
    POOR = "poor"
    CRITICAL = "critical"


@dataclass
class UserContext:
    """User context information"""
    user_id: str
    session_id: str
    role: UserRole
    device_type: DeviceType
    
    # User characteristics
    registration_date: Optional[datetime] = None
    subscription_tier: str = "free"
    engagement_level: str = "medium"  # low, medium, high
    
    # Session context
    session_start_time: datetime = field(default_factory=datetime.utcnow)
    page_url: Optional[str] = None
    referrer: Optional[str] = None
    
    # Technical context
    browser: Optional[str] = None
    browser_version: Optional[str] = None
    os: Optional[str] = None
    screen_resolution: Optional[str] = None
    connection_type: str = "broadband"  # broadband, mobile, slow
    
    # Geographical context
    country: Optional[str] = None
    region: Optional[str] = None
    timezone: Optional[str] = None


@dataclass
class InteractionMetadata:
    """Metadata for user interactions"""
    interaction_id: str
    interaction_type: InteractionType
    user_context: UserContext
    
    # Interaction details
    element_id: Optional[str] = None
    element_type: Optional[str] = None  # "button", "link", "form", "video"
    element_text: Optional[str] = None
    
    # Content context
    page_type: str = "unknown"  # "dashboard", "profile", "content", "search"
    content_type: Optional[str] = None  # "video", "image", "text", "audio"
    content_id: Optional[str] = None
    creator_id: Optional[str] = None
    
    # Form data (for form submissions)
    form_fields_count: int = 0
    form_validation_errors: int = 0
    
    # Search data (for search interactions)
    search_query: Optional[str] = None
    search_filters_count: int = 0
    
    # Navigation data
    source_page: Optional[str] = None
    destination_page: Optional[str] = None


@dataclass
class UserInteractionMetrics:
    """User interaction performance metrics"""
    interaction_id: str
    metadata: InteractionMetadata
    
    # Performance metrics (all in milliseconds)
    total_time_ms: float
    dom_ready_time_ms: Optional[float] = None
    first_paint_time_ms: Optional[float] = None
    first_contentful_paint_ms: Optional[float] = None
    largest_contentful_paint_ms: Optional[float] = None
    first_input_delay_ms: Optional[float] = None
    cumulative_layout_shift: Optional[float] = None
    
    # Interaction-specific metrics
    click_to_response_ms: Optional[float] = None
    form_submit_time_ms: Optional[float] = None
    search_response_time_ms: Optional[float] = None
    video_load_time_ms: Optional[float] = None
    page_transition_time_ms: Optional[float] = None
    
    # Network metrics
    dns_lookup_time_ms: Optional[float] = None
    tcp_connect_time_ms: Optional[float] = None
    request_time_ms: Optional[float] = None
    response_time_ms: Optional[float] = None
    
    # Resource metrics
    resources_loaded: int = 0
    total_resource_size_kb: float = 0.0
    cached_resources_count: int = 0
    
    # User experience metrics
    bounce_rate_indicator: bool = False
    engagement_score: float = 0.0  # 0-100
    satisfaction_score: Optional[float] = None  # 1-5 if available
    
    # Error metrics
    javascript_errors: int = 0
    network_errors: int = 0
    timeout_occurred: bool = False
    
    # Business metrics
    conversion_event: bool = False
    revenue_impact_usd: Optional[float] = None
    
    # Quality metrics
    success: bool = True
    error_message: Optional[str] = None
    error_type: Optional[str] = None
    
    timestamp: datetime = field(default_factory=datetime.utcnow)


@dataclass
class UserInteractionBottleneck:
    """User interaction performance bottleneck detection"""
    bottleneck_id: str
    interaction_type: InteractionType
    user_role: UserRole
    device_type: DeviceType
    
    # Bottleneck details
    bottleneck_type: str  # "slow_page_load", "high_input_delay", "layout_shift", "poor_engagement"
    severity: str  # "low", "medium", "high", "critical"
    description: str
    
    # Performance impact
    current_performance: Dict[str, float]
    expected_performance: Dict[str, float]
    impact_percentage: float
    
    # Affected users
    affected_users: List[str]
    affected_pages: List[str]
    user_segments: List[str]
    
    # UX analysis
    ux_impact_analysis: Dict[str, Any]
    conversion_impact: Dict[str, float]
    
    # Optimization recommendations
    recommendations: List[str]
    estimated_improvement: Dict[str, float]
    
    timestamp: datetime = field(default_factory=datetime.utcnow)


class UserInteractionProfiler:
    """Advanced user interaction performance profiler"""
    
    def __init__(self,
                 monitoring_interval: float = 1.0,
                 max_history_size: int = 20000,
                 enable_web_vitals: bool = True,
                 enable_engagement_tracking: bool = True,
                 slow_interaction_threshold_ms: float = 300.0):
        """
        Initialize user interaction profiler
        
        Args:
            monitoring_interval: Monitoring interval in seconds
            max_history_size: Maximum number of metrics to store
            enable_web_vitals: Enable Core Web Vitals tracking
            enable_engagement_tracking: Enable user engagement tracking
            slow_interaction_threshold_ms: Threshold for slow interaction detection
        """
        self.monitoring_interval = monitoring_interval
        self.max_history_size = max_history_size
        self.enable_web_vitals = enable_web_vitals
        self.enable_engagement_tracking = enable_engagement_tracking
        self.slow_interaction_threshold_ms = slow_interaction_threshold_ms
        
        # Storage for metrics
        self.metrics_history: deque = deque(maxlen=max_history_size)
        self.active_sessions: Dict[str, List[UserInteractionMetrics]] = defaultdict(list)
        self.bottlenecks: List[UserInteractionBottleneck] = []
        
        # User session tracking
        self.session_data: Dict[str, Dict[str, Any]] = {}
        self.user_journeys: Dict[str, List[InteractionMetadata]] = defaultdict(list)
        
        # Performance patterns
        self.interaction_patterns: Dict[str, List[float]] = defaultdict(list)
        self.page_performance: Dict[str, List[float]] = defaultdict(list)
        self.user_segments: Dict[str, List[UserInteractionMetrics]] = defaultdict(list)
        
        # Performance thresholds
        self.thresholds = {
            'max_page_load_time_ms': 3000.0,
            'max_first_input_delay_ms': 100.0,
            'max_largest_contentful_paint_ms': 2500.0,
            'max_cumulative_layout_shift': 0.1,
            'max_interaction_time_ms': slow_interaction_threshold_ms,
            'min_engagement_score': 30.0,
            'max_bounce_rate_percent': 70.0
        }
        
        # Monitoring state
        self.is_monitoring = False
        self.monitoring_task: Optional[asyncio.Task] = None
        self._lock = threading.Lock()
        
        # Prometheus metrics
        self._init_prometheus_metrics()
        
        logger.info("UserInteractionProfiler initialized for Creator Economy platform")
    
    def _init_prometheus_metrics(self):
        """Initialize Prometheus metrics"""
        self.prometheus_metrics = {
            'user_interaction_duration': Histogram(
                'ainflue_user_interaction_duration_seconds',
                'Duration of user interactions',
                ['interaction_type', 'user_role', 'device_type', 'success']
            ),
            'page_load_time': Histogram(
                'ainflue_page_load_time_seconds',
                'Page load times',
                ['page_type', 'user_role', 'device_type']
            ),
            'web_vitals_lcp': Histogram(
                'ainflue_web_vitals_lcp_seconds',
                'Largest Contentful Paint timing',
                ['page_type', 'device_type']
            ),
            'web_vitals_fid': Histogram(
                'ainflue_web_vitals_fid_seconds',
                'First Input Delay timing',
                ['interaction_type', 'device_type']
            ),
            'web_vitals_cls': Gauge(
                'ainflue_web_vitals_cls_score',
                'Cumulative Layout Shift score',
                ['page_type', 'device_type']
            ),
            'user_engagement_score': Gauge(
                'ainflue_user_engagement_score',
                'User engagement score',
                ['user_role', 'device_type', 'page_type']
            ),
            'conversion_events': Counter(
                'ainflue_conversion_events_total',
                'Total conversion events',
                ['event_type', 'user_role', 'device_type']
            ),
            'user_errors': Counter(
                'ainflue_user_errors_total',
                'Total user-facing errors',
                ['error_type', 'page_type', 'device_type']
            ),
            'user_interaction_bottlenecks': Gauge(
                'ainflue_user_interaction_bottlenecks_active',
                'Number of active user interaction bottlenecks',
                ['bottleneck_type', 'severity']
            )
        }
    
    async def start_monitoring(self):
        """Start continuous user interaction monitoring"""
        if self.is_monitoring:
            logger.warning("User interaction monitoring already running")
            return
        
        self.is_monitoring = True
        self.monitoring_task = asyncio.create_task(self._monitoring_loop())
        logger.info("User interaction monitoring started")
    
    async def stop_monitoring(self):
        """Stop user interaction monitoring"""
        if not self.is_monitoring:
            return
        
        self.is_monitoring = False
        if self.monitoring_task:
            self.monitoring_task.cancel()
            try:
                await self.monitoring_task
            except asyncio.CancelledError:
                pass
        
        logger.info("User interaction monitoring stopped")
    
    async def profile_user_interaction(self,
                                     metadata: InteractionMetadata,
                                     interaction_func: Callable,
                                     *args, **kwargs) -> UserInteractionMetrics:
        """
        Profile a user interaction
        
        Args:
            metadata: User interaction metadata
            interaction_func: Function to execute and profile
            *args, **kwargs: Arguments for the interaction function
        
        Returns:
            UserInteractionMetrics: Detailed performance metrics
        """
        start_time = time.time()
        
        # Initialize metrics
        metrics = UserInteractionMetrics(
            interaction_id=metadata.interaction_id,
            metadata=metadata,
            total_time_ms=0.0
        )
        
        try:
            # Measure page load metrics if applicable
            if metadata.interaction_type == InteractionType.PAGE_LOAD:
                # Simulate DOM ready timing
                dom_start = time.time()
                await self._measure_dom_ready()
                dom_end = time.time()
                metrics.dom_ready_time_ms = (dom_end - dom_start) * 1000
                
                # Simulate paint timings
                if self.enable_web_vitals:
                    paint_metrics = await self._measure_paint_timings()
                    metrics.first_paint_time_ms = paint_metrics.get('first_paint')
                    metrics.first_contentful_paint_ms = paint_metrics.get('first_contentful_paint')
                    metrics.largest_contentful_paint_ms = paint_metrics.get('largest_contentful_paint')
                    metrics.cumulative_layout_shift = paint_metrics.get('cumulative_layout_shift')
            
            # Execute the interaction
            interaction_start = time.time()
            result = await self._execute_interaction_operation(interaction_func, *args, **kwargs)
            interaction_end = time.time()
            
            # Calculate interaction-specific timing
            interaction_time = (interaction_end - interaction_start) * 1000
            
            if metadata.interaction_type == InteractionType.BUTTON_CLICK:
                metrics.click_to_response_ms = interaction_time
            elif metadata.interaction_type == InteractionType.FORM_SUBMISSION:
                metrics.form_submit_time_ms = interaction_time
            elif metadata.interaction_type == InteractionType.SEARCH:
                metrics.search_response_time_ms = interaction_time
            elif metadata.interaction_type == InteractionType.VIDEO_PLAY:
                metrics.video_load_time_ms = interaction_time
            elif metadata.interaction_type == InteractionType.NAVIGATION:
                metrics.page_transition_time_ms = interaction_time
            
            # Measure First Input Delay for interactive elements
            if metadata.interaction_type in [InteractionType.BUTTON_CLICK, InteractionType.FORM_SUBMISSION]:
                fid_time = await self._measure_first_input_delay()
                metrics.first_input_delay_ms = fid_time
            
            # Extract result metrics
            metrics = await self._extract_interaction_result_metrics(result, metrics)
            
            # Calculate engagement score
            if self.enable_engagement_tracking:
                metrics.engagement_score = await self._calculate_engagement_score(metadata, metrics)
            
            # Calculate total time
            end_time = time.time()
            metrics.total_time_ms = (end_time - start_time) * 1000
            
            # Set success
            metrics.success = True
            
            # Store metrics
            await self._store_metrics(metrics)
            
            # Update session data
            await self._update_session_data(metadata, metrics)
            
            # Update user journey
            await self._update_user_journey(metadata)
            
            # Update Prometheus metrics
            self._update_prometheus_metrics(metrics)
            
            # Track interaction patterns
            await self._track_interaction_patterns(metrics)
            
            # Check for bottlenecks
            await self._detect_bottlenecks(metrics)
            
            logger.debug(f"User interaction profiled: {metadata.interaction_id} - {metrics.total_time_ms:.2f}ms")
            return metrics
            
        except Exception as e:
            # Handle interaction failure
            end_time = time.time()
            metrics.total_time_ms = (end_time - start_time) * 1000
            metrics.success = False
            metrics.error_message = str(e)
            metrics.error_type = type(e).__name__
            
            await self._store_metrics(metrics)
            self.prometheus_metrics['user_errors'].labels(
                error_type=metrics.error_type,
                page_type=metadata.page_type,
                device_type=metadata.user_context.device_type.value
            ).inc()
            
            logger.error(f"User interaction failed: {metadata.interaction_id} - {e}")
            return metrics
    
    async def _measure_dom_ready(self):
        """Measure DOM ready time"""
        # Simulate DOM ready measurement
        await asyncio.sleep(0.05)  # Simulated DOM ready time
    
    async def _measure_paint_timings(self) -> Dict[str, float]:
        """Measure paint timing metrics"""
        # Simulate Web Vitals measurements
        await asyncio.sleep(0.02)  # Simulated measurement time
        
        return {
            'first_paint': 100.0,  # Simulated values
            'first_contentful_paint': 150.0,
            'largest_contentful_paint': 800.0,
            'cumulative_layout_shift': 0.05
        }
    
    async def _measure_first_input_delay(self) -> float:
        """Measure first input delay"""
        # Simulate FID measurement
        await asyncio.sleep(0.001)
        return 20.0  # Simulated FID in milliseconds
    
    async def _execute_interaction_operation(self, operation_func: Callable, *args, **kwargs):
        """Execute interaction operation with proper async handling"""
        if asyncio.iscoroutinefunction(operation_func):
            return await operation_func(*args, **kwargs)
        else:
            return operation_func(*args, **kwargs)
    
    async def _extract_interaction_result_metrics(self, result: Any, metrics: UserInteractionMetrics) -> UserInteractionMetrics:
        """Extract metrics from interaction result"""
        if isinstance(result, dict):
            # Extract resource metrics
            if 'resources_loaded' in result:
                metrics.resources_loaded = result['resources_loaded']
            if 'total_resource_size_kb' in result:
                metrics.total_resource_size_kb = result['total_resource_size_kb']
            if 'cached_resources_count' in result:
                metrics.cached_resources_count = result['cached_resources_count']
            
            # Extract error metrics
            if 'javascript_errors' in result:
                metrics.javascript_errors = result['javascript_errors']
            if 'network_errors' in result:
                metrics.network_errors = result['network_errors']
            
            # Extract business metrics
            if 'conversion_event' in result:
                metrics.conversion_event = result['conversion_event']
            if 'revenue_impact_usd' in result:
                metrics.revenue_impact_usd = result['revenue_impact_usd']
        
        return metrics
    
    async def _calculate_engagement_score(self, metadata: InteractionMetadata, metrics: UserInteractionMetrics) -> float:
        """Calculate user engagement score"""
        score = 50.0  # Base score
        
        # Adjust based on interaction type
        interaction_scores = {
            InteractionType.PAGE_LOAD: 0,
            InteractionType.BUTTON_CLICK: 10,
            InteractionType.FORM_SUBMISSION: 20,
            InteractionType.SEARCH: 15,
            InteractionType.VIDEO_PLAY: 25,
            InteractionType.CONTENT_UPLOAD: 30,
            InteractionType.COLLABORATION_REQUEST: 35,
            InteractionType.PAYMENT: 40,
            InteractionType.LIKE: 5,
            InteractionType.SHARE: 15,
            InteractionType.COMMENT: 20,
            InteractionType.FOLLOW: 25
        }
        
        score += interaction_scores.get(metadata.interaction_type, 0)
        
        # Adjust based on performance
        if metrics.total_time_ms < self.slow_interaction_threshold_ms:
            score += 10
        elif metrics.total_time_ms > self.slow_interaction_threshold_ms * 2:
            score -= 20
        
        # Adjust based on errors
        if metrics.javascript_errors > 0 or metrics.network_errors > 0:
            score -= 15
        
        # Adjust based on user role
        if metadata.user_context.role == UserRole.CREATOR:
            score += 5  # Creators are typically more engaged
        
        return max(0.0, min(100.0, score))
    
    async def _store_metrics(self, metrics: UserInteractionMetrics):
        """Store metrics in history"""
        with self._lock:
            self.metrics_history.append(metrics)
            
            # Add to session data
            session_id = metrics.metadata.user_context.session_id
            self.active_sessions[session_id].append(metrics)
            
            # Add to user segments
            user_role = metrics.metadata.user_context.role.value
            device_type = metrics.metadata.user_context.device_type.value
            segment_key = f"{user_role}_{device_type}"
            self.user_segments[segment_key].append(metrics)
    
    async def _update_session_data(self, metadata: InteractionMetadata, metrics: UserInteractionMetrics):
        """Update session-level data"""
        session_id = metadata.user_context.session_id
        
        with self._lock:
            if session_id not in self.session_data:
                self.session_data[session_id] = {
                    'start_time': metadata.user_context.session_start_time,
                    'user_context': metadata.user_context,
                    'interactions_count': 0,
                    'total_time_ms': 0.0,
                    'errors_count': 0,
                    'conversions_count': 0,
                    'engagement_scores': []
                }
            
            session = self.session_data[session_id]
            session['interactions_count'] += 1
            session['total_time_ms'] += metrics.total_time_ms
            session['errors_count'] += metrics.javascript_errors + metrics.network_errors
            session['engagement_scores'].append(metrics.engagement_score)
            
            if metrics.conversion_event:
                session['conversions_count'] += 1
    
    async def _update_user_journey(self, metadata: InteractionMetadata):
        """Update user journey tracking"""
        user_id = metadata.user_context.user_id
        
        with self._lock:
            self.user_journeys[user_id].append(metadata)
            
            # Keep only recent journey data
            if len(self.user_journeys[user_id]) > 100:
                self.user_journeys[user_id] = self.user_journeys[user_id][-100:]
    
    def _update_prometheus_metrics(self, metrics: UserInteractionMetrics):
        """Update Prometheus metrics"""
        interaction_type = metrics.metadata.interaction_type.value
        user_role = metrics.metadata.user_context.role.value
        device_type = metrics.metadata.user_context.device_type.value
        page_type = metrics.metadata.page_type
        success = "success" if metrics.success else "error"
        
        # Update interaction duration
        self.prometheus_metrics['user_interaction_duration'].labels(
            interaction_type=interaction_type,
            user_role=user_role,
            device_type=device_type,
            success=success
        ).observe(metrics.total_time_ms / 1000)
        
        # Update page load time
        if metrics.metadata.interaction_type == InteractionType.PAGE_LOAD:
            self.prometheus_metrics['page_load_time'].labels(
                page_type=page_type,
                user_role=user_role,
                device_type=device_type
            ).observe(metrics.total_time_ms / 1000)
        
        # Update Web Vitals
        if self.enable_web_vitals:
            if metrics.largest_contentful_paint_ms is not None:
                self.prometheus_metrics['web_vitals_lcp'].labels(
                    page_type=page_type,
                    device_type=device_type
                ).observe(metrics.largest_contentful_paint_ms / 1000)
            
            if metrics.first_input_delay_ms is not None:
                self.prometheus_metrics['web_vitals_fid'].labels(
                    interaction_type=interaction_type,
                    device_type=device_type
                ).observe(metrics.first_input_delay_ms / 1000)
            
            if metrics.cumulative_layout_shift is not None:
                self.prometheus_metrics['web_vitals_cls'].labels(
                    page_type=page_type,
                    device_type=device_type
                ).set(metrics.cumulative_layout_shift)
        
        # Update engagement score
        if self.enable_engagement_tracking:
            self.prometheus_metrics['user_engagement_score'].labels(
                user_role=user_role,
                device_type=device_type,
                page_type=page_type
            ).set(metrics.engagement_score)
        
        # Update conversion events
        if metrics.conversion_event:
            self.prometheus_metrics['conversion_events'].labels(
                event_type=interaction_type,
                user_role=user_role,
                device_type=device_type
            ).inc()
    
    async def _track_interaction_patterns(self, metrics: UserInteractionMetrics):
        """Track interaction patterns for optimization"""
        interaction_key = f"{metrics.metadata.interaction_type.value}_{metrics.metadata.user_context.device_type.value}"
        page_key = f"{metrics.metadata.page_type}_{metrics.metadata.user_context.device_type.value}"
        
        with self._lock:
            self.interaction_patterns[interaction_key].append(metrics.total_time_ms)
            self.page_performance[page_key].append(metrics.total_time_ms)
            
            # Keep only recent patterns
            if len(self.interaction_patterns[interaction_key]) > 100:
                self.interaction_patterns[interaction_key] = self.interaction_patterns[interaction_key][-100:]
            if len(self.page_performance[page_key]) > 100:
                self.page_performance[page_key] = self.page_performance[page_key][-100:]
    
    async def _detect_bottlenecks(self, metrics: UserInteractionMetrics):
        """Detect user interaction performance bottlenecks"""
        bottlenecks = []
        
        # Slow interaction detection
        if metrics.total_time_ms > self.thresholds['max_interaction_time_ms']:
            bottleneck = UserInteractionBottleneck(
                bottleneck_id=f"slow_interaction_{int(time.time())}",
                interaction_type=metrics.metadata.interaction_type,
                user_role=metrics.metadata.user_context.role,
                device_type=metrics.metadata.user_context.device_type,
                bottleneck_type="slow_interaction",
                severity="high" if metrics.total_time_ms > self.thresholds['max_interaction_time_ms'] * 2 else "medium",
                description=f"Slow user interaction: {metrics.total_time_ms:.2f}ms",
                current_performance={"interaction_time_ms": metrics.total_time_ms},
                expected_performance={"interaction_time_ms": self.thresholds['max_interaction_time_ms']},
                impact_percentage=(metrics.total_time_ms - self.thresholds['max_interaction_time_ms']) / self.thresholds['max_interaction_time_ms'] * 100,
                affected_users=[metrics.metadata.user_context.user_id],
                affected_pages=[metrics.metadata.page_type],
                user_segments=[f"{metrics.metadata.user_context.role.value}_{metrics.metadata.user_context.device_type.value}"],
                ux_impact_analysis={
                    "user_satisfaction": "degraded",
                    "bounce_risk": "high",
                    "engagement_impact": "negative"
                },
                conversion_impact={"conversion_rate_reduction_percent": 15.0},
                recommendations=[
                    "Optimize frontend JavaScript and CSS",
                    "Implement code splitting and lazy loading",
                    "Optimize images and media assets",
                    "Use CDN for static asset delivery",
                    "Implement progressive web app features"
                ],
                estimated_improvement={"interaction_time_reduction_percent": 40.0}
            )
            bottlenecks.append(bottleneck)
        
        # Poor Web Vitals detection
        if (self.enable_web_vitals and 
            metrics.largest_contentful_paint_ms is not None and 
            metrics.largest_contentful_paint_ms > self.thresholds['max_largest_contentful_paint_ms']):
            bottleneck = UserInteractionBottleneck(
                bottleneck_id=f"poor_lcp_{int(time.time())}",
                interaction_type=metrics.metadata.interaction_type,
                user_role=metrics.metadata.user_context.role,
                device_type=metrics.metadata.user_context.device_type,
                bottleneck_type="poor_web_vitals",
                severity="medium",
                description=f"Poor Largest Contentful Paint: {metrics.largest_contentful_paint_ms:.2f}ms",
                current_performance={"lcp_ms": metrics.largest_contentful_paint_ms},
                expected_performance={"lcp_ms": self.thresholds['max_largest_contentful_paint_ms']},
                impact_percentage=(metrics.largest_contentful_paint_ms - self.thresholds['max_largest_contentful_paint_ms']) / self.thresholds['max_largest_contentful_paint_ms'] * 100,
                affected_users=[metrics.metadata.user_context.user_id],
                affected_pages=[metrics.metadata.page_type],
                user_segments=[f"{metrics.metadata.user_context.role.value}_{metrics.metadata.user_context.device_type.value}"],
                ux_impact_analysis={
                    "perceived_performance": "poor",
                    "seo_impact": "negative",
                    "user_experience": "degraded"
                },
                conversion_impact={"seo_ranking_impact": "negative"},
                recommendations=[
                    "Optimize largest content elements",
                    "Implement image optimization and WebP format",
                    "Preload critical resources",
                    "Optimize server response times",
                    "Use efficient image formats and compression"
                ],
                estimated_improvement={"lcp_improvement_percent": 30.0}
            )
            bottlenecks.append(bottleneck)
        
        # Low engagement detection
        if (self.enable_engagement_tracking and 
            metrics.engagement_score < self.thresholds['min_engagement_score']):
            bottleneck = UserInteractionBottleneck(
                bottleneck_id=f"low_engagement_{int(time.time())}",
                interaction_type=metrics.metadata.interaction_type,
                user_role=metrics.metadata.user_context.role,
                device_type=metrics.metadata.user_context.device_type,
                bottleneck_type="low_engagement",
                severity="medium",
                description=f"Low user engagement: {metrics.engagement_score:.1f}/100",
                current_performance={"engagement_score": metrics.engagement_score},
                expected_performance={"engagement_score": self.thresholds['min_engagement_score']},
                impact_percentage=(self.thresholds['min_engagement_score'] - metrics.engagement_score) / self.thresholds['min_engagement_score'] * 100,
                affected_users=[metrics.metadata.user_context.user_id],
                affected_pages=[metrics.metadata.page_type],
                user_segments=[f"{metrics.metadata.user_context.role.value}_{metrics.metadata.user_context.device_type.value}"],
                ux_impact_analysis={
                    "user_retention": "at_risk",
                    "interaction_quality": "poor",
                    "session_duration": "below_average"
                },
                conversion_impact={"retention_rate_reduction_percent": 25.0},
                recommendations=[
                    "Improve content relevance and personalization",
                    "Optimize user interface and navigation",
                    "Implement gamification elements",
                    "Reduce friction in user workflows",
                    "Enhance mobile user experience"
                ],
                estimated_improvement={"engagement_improvement_percent": 50.0}
            )
            bottlenecks.append(bottleneck)
        
        # Store bottlenecks
        for bottleneck in bottlenecks:
            self.bottlenecks.append(bottleneck)
            self.prometheus_metrics['user_interaction_bottlenecks'].labels(
                bottleneck_type=bottleneck.bottleneck_type,
                severity=bottleneck.severity
            ).inc()
    
    async def _monitoring_loop(self):
        """Background monitoring loop"""
        while self.is_monitoring:
            try:
                # Monitor session quality
                await self._monitor_session_quality()
                
                # Monitor user patterns
                await self._monitor_user_patterns()
                
                # Clean up old data
                await self._cleanup_old_data()
                
                await asyncio.sleep(self.monitoring_interval)
                
            except Exception as e:
                logger.error(f"Error in user interaction monitoring loop: {e}")
                await asyncio.sleep(self.monitoring_interval)
    
    async def _monitor_session_quality(self):
        """Monitor overall session quality"""
        try:
            current_time = datetime.utcnow()
            
            with self._lock:
                for session_id, session in self.session_data.items():
                    if session['interactions_count'] > 5:  # Enough data
                        # Calculate session metrics
                        avg_engagement = statistics.mean(session['engagement_scores']) if session['engagement_scores'] else 0
                        error_rate = session['errors_count'] / session['interactions_count'] * 100
                        
                        # Determine session quality
                        if avg_engagement > 70 and error_rate < 5:
                            quality = SessionQuality.EXCELLENT
                        elif avg_engagement > 50 and error_rate < 10:
                            quality = SessionQuality.GOOD
                        elif avg_engagement > 30 and error_rate < 20:
                            quality = SessionQuality.POOR
                        else:
                            quality = SessionQuality.CRITICAL
                        
                        if quality in [SessionQuality.POOR, SessionQuality.CRITICAL]:
                            logger.warning(f"Poor session quality detected: {session_id} - {quality.value}")
        
        except Exception as e:
            logger.error(f"Error monitoring session quality: {e}")
    
    async def _monitor_user_patterns(self):
        """Monitor user behavior patterns"""
        try:
            with self._lock:
                for pattern_key, times in self.interaction_patterns.items():
                    if len(times) > 10:  # Enough data points
                        avg_time = statistics.mean(times)
                        if avg_time > self.slow_interaction_threshold_ms:
                            logger.warning(f"Slow interaction pattern: {pattern_key} - avg {avg_time:.2f}ms")
        
        except Exception as e:
            logger.error(f"Error monitoring user patterns: {e}")
    
    async def _cleanup_old_data(self):
        """Clean up old monitoring data"""
        cutoff_time = datetime.utcnow() - timedelta(hours=2)
        
        # Clean up old bottlenecks
        self.bottlenecks = [b for b in self.bottlenecks if b.timestamp > cutoff_time]
        
        # Clean up old sessions
        old_sessions = [session_id for session_id, session in self.session_data.items() 
                       if session['start_time'] < cutoff_time]
        for session_id in old_sessions:
            if session_id in self.session_data:
                del self.session_data[session_id]
            if session_id in self.active_sessions:
                del self.active_sessions[session_id]
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """Get user interaction performance summary"""
        if not self.metrics_history:
            return {}
        
        recent_metrics = list(self.metrics_history)[-500:]  # Last 500 interactions
        
        # Calculate averages
        avg_interaction_time = statistics.mean([m.total_time_ms for m in recent_metrics])
        success_rate = sum(1 for m in recent_metrics if m.success) / len(recent_metrics) * 100
        avg_engagement = statistics.mean([m.engagement_score for m in recent_metrics])
        
        # Device breakdown
        device_breakdown = defaultdict(list)
        for metric in recent_metrics:
            device_breakdown[metric.metadata.user_context.device_type.value].append(metric)
        
        # User role breakdown
        role_breakdown = defaultdict(list)
        for metric in recent_metrics:
            role_breakdown[metric.metadata.user_context.role.value].append(metric)
        
        # Web Vitals summary
        web_vitals = {}
        if self.enable_web_vitals:
            lcp_values = [m.largest_contentful_paint_ms for m in recent_metrics if m.largest_contentful_paint_ms is not None]
            fid_values = [m.first_input_delay_ms for m in recent_metrics if m.first_input_delay_ms is not None]
            cls_values = [m.cumulative_layout_shift for m in recent_metrics if m.cumulative_layout_shift is not None]
            
            web_vitals = {
                "average_lcp_ms": statistics.mean(lcp_values) if lcp_values else None,
                "average_fid_ms": statistics.mean(fid_values) if fid_values else None,
                "average_cls": statistics.mean(cls_values) if cls_values else None
            }
        
        return {
            "overall_performance": {
                "average_interaction_time_ms": avg_interaction_time,
                "success_rate_percent": success_rate,
                "average_engagement_score": avg_engagement,
                "total_interactions": len(recent_metrics),
                "active_sessions": len(self.active_sessions)
            },
            "device_breakdown": {
                device: {
                    "interaction_count": len(metrics),
                    "avg_interaction_time_ms": statistics.mean([m.total_time_ms for m in metrics]),
                    "avg_engagement_score": statistics.mean([m.engagement_score for m in metrics])
                }
                for device, metrics in device_breakdown.items()
            },
            "user_role_breakdown": {
                role: {
                    "interaction_count": len(metrics),
                    "avg_interaction_time_ms": statistics.mean([m.total_time_ms for m in metrics]),
                    "avg_engagement_score": statistics.mean([m.engagement_score for m in metrics])
                }
                for role, metrics in role_breakdown.items()
            },
            "web_vitals": web_vitals,
            "active_bottlenecks": len([b for b in self.bottlenecks if b.timestamp > datetime.utcnow() - timedelta(minutes=5)]),
            "timestamp": datetime.utcnow().isoformat()
        }
    
    def get_bottleneck_report(self) -> List[Dict[str, Any]]:
        """Get detailed bottleneck report"""
        return [
            {
                "bottleneck_id": b.bottleneck_id,
                "interaction_type": b.interaction_type.value,
                "user_role": b.user_role.value,
                "device_type": b.device_type.value,
                "type": b.bottleneck_type,
                "severity": b.severity,
                "description": b.description,
                "impact_percentage": b.impact_percentage,
                "affected_users": b.affected_users,
                "affected_pages": b.affected_pages,
                "user_segments": b.user_segments,
                "ux_impact_analysis": b.ux_impact_analysis,
                "conversion_impact": b.conversion_impact,
                "recommendations": b.recommendations,
                "estimated_improvement": b.estimated_improvement,
                "timestamp": b.timestamp.isoformat()
            }
            for b in self.bottlenecks
        ]


def create_user_interaction_profiler(
    monitoring_interval: float = 1.0,
    enable_web_vitals: bool = True,
    enable_engagement_tracking: bool = True,
    slow_interaction_threshold_ms: float = 300.0,
    start_monitoring: bool = False
) -> UserInteractionProfiler:
    """
    Factory function to create user interaction profiler
    
    Args:
        monitoring_interval: Monitoring interval in seconds
        enable_web_vitals: Enable Core Web Vitals tracking
        enable_engagement_tracking: Enable user engagement tracking
        slow_interaction_threshold_ms: Threshold for slow interaction detection
        start_monitoring: Start monitoring immediately
    
    Returns:
        UserInteractionProfiler: Configured user interaction profiler instance
    """
    profiler = UserInteractionProfiler(
        monitoring_interval=monitoring_interval,
        enable_web_vitals=enable_web_vitals,
        enable_engagement_tracking=enable_engagement_tracking,
        slow_interaction_threshold_ms=slow_interaction_threshold_ms
    )
    
    if start_monitoring:
        import asyncio
        try:
            loop = asyncio.get_event_loop()
            loop.create_task(profiler.start_monitoring())
        except RuntimeError:
            logger.warning("No event loop running, monitoring will need to be started manually")
    
    return profiler


# Example usage for Creator Economy platform
async def example_user_interaction_profiling():
    """Example of profiling Creator Economy user interactions"""
    profiler = create_user_interaction_profiler(start_monitoring=True)
    
    # Example: Profile creator dashboard page load
    async def load_creator_dashboard():
        # Simulate page load
        await asyncio.sleep(0.2)  # Simulate page load time
        return {
            "resources_loaded": 45,
            "total_resource_size_kb": 1250.0,
            "cached_resources_count": 20,
            "javascript_errors": 0,
            "network_errors": 0
        }
    
    user_context = UserContext(
        user_id="creator_123",
        session_id="session_456",
        role=UserRole.CREATOR,
        device_type=DeviceType.DESKTOP,
        browser="Chrome",
        browser_version="91.0",
        os="Windows 10",
        screen_resolution="1920x1080",
        connection_type="broadband",
        country="US",
        region="California"
    )
    
    metadata = InteractionMetadata(
        interaction_id="page_load_789",
        interaction_type=InteractionType.PAGE_LOAD,
        user_context=user_context,
        page_type="dashboard",
        element_id="main_dashboard",
        element_type="page"
    )
    
    metrics = await profiler.profile_user_interaction(
        metadata,
        load_creator_dashboard
    )
    
    print(f"User interaction profiled:")
    print(f"- Total time: {metrics.total_time_ms:.2f}ms")
    print(f"- DOM ready: {metrics.dom_ready_time_ms:.2f}ms" if metrics.dom_ready_time_ms else "- No DOM timing")
    print(f"- LCP: {metrics.largest_contentful_paint_ms:.2f}ms" if metrics.largest_contentful_paint_ms else "- No LCP timing")
    print(f"- Engagement score: {metrics.engagement_score:.1f}/100")
    print(f"- Success: {metrics.success}")
    
    # Get performance summary
    summary = profiler.get_performance_summary()
    print(f"Performance summary: {json.dumps(summary, indent=2)}")
    
    await profiler.stop_monitoring()


if __name__ == "__main__":
    asyncio.run(example_user_interaction_profiling())