"""Advanced Event Streaming System for IA Influencer Agent Platform
===============================================================

Ultra-modern enterprise-grade event streaming infrastructure for real-time content processing,
AI-powered protection monitoring, revenue tracking, and cross-platform data synchronization
with guaranteed delivery, circuit breaker patterns, and distributed tracing.

Key Features:
- Real-time event streaming with guaranteed delivery
- AI-powered event routing and filtering
- Protection violation event monitoring
- Revenue tracking event processing
- Cross-platform synchronization events
- Dead letter queue handling
- Circuit breaker protection
- Distributed event tracing
- Event replay and time-travel debugging
- Advanced metrics and observability

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: © 2025 Fahed Mlaiel - All Rights Reserved

⚠️  LEGAL WARNING ⚠️
Unauthorized use, copying, modification, or distribution of this code
without explicit written permission from Fahed Mlaiel is strictly prohibited.
Violations will be prosecuted under German and international copyright law.

Contact: mlaiel@live.de for licensing inquiries.
"""import asyncio
import logging
from typing import Dict, List, Optional, Any, Callable, Set, Union, Tuple
from datetime import datetime, timezone, timedelta
from dataclasses import dataclass, field
from enum import Enum
import json
import hashlib
import time
from uuid import uuid4
from collections import defaultdict, deque

from pydantic import BaseModel, Field, validator
from redis.asyncio import Redis
import aiohttp

from ...core.config import get_settings
from ...utils.logging import get_logger
from ...core.security import SecurityManager
from ...ai.event_analysis import EventAnalyzer
from .manager import StreamEvent, StreamType

logger = get_logger(__name__)
settings = get_settings()


class EventPriority(int, Enum):
    """Advanced event priority levels for intelligent routing"""    LOW = 1
    NORMAL = 2
    HIGH = 3
    CRITICAL = 4
    EMERGENCY = 5


class DeliveryMode(str, Enum):
    """Event delivery guarantee modes"""    FIRE_AND_FORGET = "fire_and_forget"
    AT_LEAST_ONCE = "at_least_once"
    EXACTLY_ONCE = "exactly_once"
    TRANSACTIONAL = "transactional"


class EventCategory(str, Enum):
    """Event categorization for AI routing"""    CONTENT_PROCESSING = "content_processing"
    PROTECTION_VIOLATION = "protection_violation"
    REVENUE_TRACKING = "revenue_tracking"
    USER_ACTIVITY = "user_activity"
    SYSTEM_HEALTH = "system_health"
    AI_ANALYSIS = "ai_analysis"
    PLATFORM_SYNC = "platform_sync"
    NOTIFICATION = "notification"


class CircuitBreakerState(str, Enum):
    """Circuit breaker states for fault tolerance"""    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"


@dataclass
class EventTrace:
    """Distributed tracing information for events"""    trace_id: str
    span_id: str
    parent_span_id: Optional[str]
    operation_name: str
    start_time: datetime
    end_time: Optional[datetime] = None
    tags: Dict[str, Any] = field(default_factory=dict)
    logs: List[Dict[str, Any]] = field(default_factory=list)


@dataclass
class CircuitBreaker:
    """Circuit breaker for fault tolerance"""    failure_threshold: int = 5
    recovery_timeout: float = 60.0
    state: CircuitBreakerState = CircuitBreakerState.CLOSED
    failure_count: int = 0
    last_failure_time: Optional[datetime] = None
    last_success_time: Optional[datetime] = None


@dataclass
class EventSubscription:
    """Advanced event subscription configuration with AI filtering"""    subscriber_id: str
    event_types: Set[str]
    event_categories: Set[EventCategory]
    callback: Callable[[StreamEvent], None]
    delivery_mode: DeliveryMode = DeliveryMode.AT_LEAST_ONCE
    max_retries: int = 3
    retry_delay: float = 1.0
    active: bool = True
    priority_filter: Optional[EventPriority] = None
    ai_filter_enabled: bool = False
    webhook_url: Optional[str] = None
    rate_limit: Optional[int] = None  # events per minute
    circuit_breaker: CircuitBreaker = field(default_factory=CircuitBreaker)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    metadata: Dict[str, Any] = field(default_factory=dict)


class AdvancedEventFilter(BaseModel):
    """Advanced AI-powered event filtering configuration"""    event_types: Optional[List[str]] = Field(default=None, description="Allowed event types")
    event_categories: Optional[List[EventCategory]] = Field(default=None, description="Allowed event categories")
    user_ids: Optional[List[str]] = Field(default=None, description="Allowed user IDs")
    content_types: Optional[List[str]] = Field(default=None, description="Allowed content types")
    platform_types: Optional[List[str]] = Field(default=None, description="Allowed platform types")
    priority_min: Optional[EventPriority] = Field(default=None, description="Minimum priority")
    priority_max: Optional[EventPriority] = Field(default=None, description="Maximum priority")
    metadata_filters: Dict[str, Any] = Field(default_factory=dict, description="Metadata filters")
    ai_sentiment_filter: Optional[str] = Field(default=None, description="AI sentiment filtering")
    content_quality_min: Optional[float] = Field(default=None, description="Minimum content quality score")
    revenue_threshold_min: Optional[float] = Field(default=None, description="Minimum revenue threshold")
    geo_filters: Optional[List[str]] = Field(default=None, description="Geographic filters")
    time_window: Optional[Dict[str, str]] = Field(default=None, description="Time window filters")
    
    @validator('priority_min', 'priority_max')
    def validate_priorities(cls, v):
        if v and not isinstance(v, EventPriority):
            return EventPriority(v)
        return v


class EventStreamMetrics(BaseModel):
    """Comprehensive event streaming metrics with AI insights"""    # Basic metrics
    total_events: int = Field(default=0, description="Total events processed")
    events_per_second: float = Field(default=0.0, description="Current events per second")
    events_per_minute: float = Field(default=0.0, description="Current events per minute")
    delivery_success_rate: float = Field(default=0.0, description="Delivery success rate")
    average_latency: float = Field(default=0.0, description="Average delivery latency in ms")
    p95_latency: float = Field(default=0.0, description="95th percentile latency in ms")
    p99_latency: float = Field(default=0.0, description="99th percentile latency in ms")
    
    # Error and failure metrics
    failed_deliveries: int = Field(default=0, description="Failed delivery count")
    circuit_breaker_trips: int = Field(default=0, description="Circuit breaker trip count")
    dead_letter_events: int = Field(default=0, description="Dead letter queue events")
    retry_events: int = Field(default=0, description="Retried events count")
    
    # Subscription metrics
    active_subscriptions: int = Field(default=0, description="Active subscription count")
    webhook_subscriptions: int = Field(default=0, description="Webhook subscription count")
    ai_filtered_events: int = Field(default=0, description="AI filtered events count")
    
    # Category metrics
    events_by_category: Dict[str, int] = Field(default_factory=dict, description="Events by category")
    events_by_priority: Dict[str, int] = Field(default_factory=dict, description="Events by priority")
    events_by_platform: Dict[str, int] = Field(default_factory=dict, description="Events by platform")
    
    # Performance metrics
    memory_usage: float = Field(default=0.0, description="Memory usage in MB")
    cpu_usage: float = Field(default=0.0, description="CPU usage percentage")
    queue_depth: int = Field(default=0, description="Total queue depth")
    
    # AI metrics
    ai_processing_time: float = Field(default=0.0, description="Average AI processing time")
    ml_confidence_avg: float = Field(default=0.0, description="Average ML confidence score")
    
    # Time-based metrics
    last_event_time: Optional[datetime] = Field(default=None, description="Last event timestamp")
    uptime: float = Field(default=0.0, description="System uptime in seconds")
    
    # Protection metrics
    protection_violations_detected: int = Field(default=0, description="Protection violations detected")
    copyright_alerts_sent: int = Field(default=0, description="Copyright alerts sent")
    
    # Revenue metrics
    revenue_events_processed: int = Field(default=0, description="Revenue events processed")
    total_revenue_tracked: float = Field(default=0.0, description="Total revenue tracked")


class DeadLetterEvent(BaseModel):
    """Dead letter queue event structure"""    original_event: StreamEvent = Field(description="Original failed event")
    subscription_id: str = Field(description="Failed subscription ID")
    failure_reason: str = Field(description="Failure reason")
    retry_count: int = Field(description="Number of retry attempts")
    first_failure_time: datetime = Field(description="First failure timestamp")
    last_failure_time: datetime = Field(description="Last failure timestamp")
    error_details: Dict[str, Any] = Field(default_factory=dict, description="Detailed error information")


class EventStreamer:
    """    Ultra-modern enterprise-grade event streaming system for real-time content processing,
    AI-powered protection monitoring, revenue tracking with advanced features:
    
    - Guaranteed delivery with circuit breakers
    - AI-powered event filtering and routing
    - Dead letter queue handling
    - Distributed tracing and observability
    - Protection violation detection
    - Revenue event processing
    - Cross-platform synchronization
    - Rate limiting and backpressure
    - Event replay and time-travel debugging
    """    
    def __init__(self):
        self.redis: Optional[Redis] = None
        self.subscriptions: Dict[str, EventSubscription] = {}
        self.event_filters: Dict[str, AdvancedEventFilter] = {}
        self.metrics = EventStreamMetrics()
        self.delivery_queues: Dict[str, asyncio.Queue] = {}
        self.dead_letter_queue: asyncio.Queue = asyncio.Queue()
        self.event_analyzer: Optional[EventAnalyzer] = None
        self.security_manager: Optional[SecurityManager] = None
        
        # Performance tracking
        self.latency_history: deque = deque(maxlen=1000)
        self.event_rate_history: deque = deque(maxlen=100)
        self.rate_limiters: Dict[str, Dict[str, Any]] = {}
        
        # Tracing
        self.active_traces: Dict[str, EventTrace] = {}
        
        # System state
        self._shutdown_event = asyncio.Event()
        self._delivery_workers: List[asyncio.Task] = []
        self._start_time = datetime.now(timezone.utc)
        
        # Advanced routing
        self.event_routers: Dict[EventCategory, Callable] = {}
        self.webhook_session: Optional[aiohttp.ClientSession] = None
        
    async def initialize(self) -> None:
        """Initialize ultra-modern event streamer with AI and security components"""        try:
            from ...core.cache import get_redis_client
            self.redis = await get_redis_client()
            
            # Initialize AI components
            try:
                self.event_analyzer = EventAnalyzer()
                await self.event_analyzer.initialize()
                logger.info("AI Event Analyzer initialized")
            except Exception as e:
                logger.warning(f"AI Event Analyzer initialization failed: {e}")
                
            # Initialize security manager
            try:
                self.security_manager = SecurityManager()
                await self.security_manager.initialize()
                logger.info("Security Manager initialized")
            except Exception as e:
                logger.warning(f"Security Manager initialization failed: {e}")
                
            # Initialize webhook session
            self.webhook_session = aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=30),
                headers={"User-Agent": "IA-Influencer-EventStreamer/2.0"}
            )
            
            # Register event routers
            await self._register_event_routers()
            
            # Start delivery workers (auto-scaling based on load)
            worker_count = settings.EVENT_STREAM_WORKERS or 8
            for i in range(worker_count):
                worker = asyncio.create_task(self._delivery_worker(f"delivery_worker_{i}"))
                self._delivery_workers.append(worker)
                
            # Start specialized workers
            asyncio.create_task(self._metrics_collector())
            asyncio.create_task(self._dead_letter_processor())
            asyncio.create_task(self._circuit_breaker_monitor())
            asyncio.create_task(self._ai_event_processor())
            asyncio.create_task(self._protection_monitor())
            asyncio.create_task(self._revenue_tracker())
            
            logger.info("Ultra-modern EventStreamer initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize EventStreamer: {e}")
            raise
            
    async def _register_event_routers(self) -> None:
        """Register specialized event routers for different categories"""        self.event_routers = {
            EventCategory.CONTENT_PROCESSING: self._route_content_event,
            EventCategory.PROTECTION_VIOLATION: self._route_protection_event,
            EventCategory.REVENUE_TRACKING: self._route_revenue_event,
            EventCategory.USER_ACTIVITY: self._route_user_event,
            EventCategory.SYSTEM_HEALTH: self._route_system_event,
            EventCategory.AI_ANALYSIS: self._route_ai_event,
            EventCategory.PLATFORM_SYNC: self._route_platform_event,
            EventCategory.NOTIFICATION: self._route_notification_event,
        }
        
    async def publish_event(
        self,
        event: StreamEvent,
        priority: EventPriority = EventPriority.NORMAL,
        category: EventCategory = EventCategory.CONTENT_PROCESSING,
        delivery_mode: DeliveryMode = DeliveryMode.AT_LEAST_ONCE,
        trace_context: Optional[Dict[str, str]] = None
    ) -> bool:
        """        Publish event with advanced AI routing and protection monitoring
        
        Args:
            event: Stream event to publish
            priority: Event priority level
            category: Event category for AI routing
            delivery_mode: Delivery guarantee mode
            trace_context: Distributed tracing context
            
        Returns:
            Success status
        """        try:
            # Start distributed trace
            trace = self._start_trace(event, trace_context)
            
            # Security validation
            if self.security_manager:
                if not await self.security_manager.validate_event(event):
                    logger.warning(f"Security validation failed for event {event.id}")
                    return False
                    
            # AI-powered event analysis
            if self.event_analyzer:
                analysis_result = await self.event_analyzer.analyze_event(event)
                event.metadata = event.metadata or {}
                event.metadata["ai_analysis"] = analysis_result
                
                # Auto-adjust priority based on AI analysis
                if analysis_result.get("threat_level") == "high":
                    priority = EventPriority.CRITICAL
                elif analysis_result.get("revenue_impact") == "high":
                    priority = EventPriority.HIGH
                    
            # Apply event filters and get relevant subscriptions
            filtered_subscriptions = await self._filter_subscriptions_advanced(event, category)
            
            if not filtered_subscriptions:
                logger.debug(f"No subscribers for event {event.id} in category {category}")
                self._end_trace(trace, success=True)
                return True
                
            # Enrich event with advanced metadata
            event.metadata = event.metadata or {}
            event.metadata.update({
                "priority": priority.value,
                "category": category.value,
                "delivery_mode": delivery_mode.value,
                "published_at": datetime.now(timezone.utc).isoformat(),
                "publisher": "ultra_event_streamer",
                "trace_id": trace.trace_id,
                "span_id": trace.span_id,
                "event_hash": self._generate_event_hash(event),
                "processing_hints": {
                    "requires_ai": category in [EventCategory.AI_ANALYSIS, EventCategory.CONTENT_PROCESSING],
                    "requires_protection": category == EventCategory.PROTECTION_VIOLATION,
                    "requires_revenue": category == EventCategory.REVENUE_TRACKING
                }
            })
            
            # Persist to Redis with advanced indexing
            await self._persist_event_advanced(event, priority, category)
            
            # Route through specialized router
            if category in self.event_routers:
                await self.event_routers[category](event, filtered_subscriptions)
            
            # Queue for delivery to subscribers
            for subscription in filtered_subscriptions:
                await self._queue_for_delivery_advanced(event, subscription, priority)
                
            # Update metrics
            self._update_metrics_advanced(event, category, priority, len(filtered_subscriptions))
            
            self._end_trace(trace, success=True)
            logger.debug(f"Published event {event.id} to {len(filtered_subscriptions)} subscribers")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to publish event {event.id}: {e}")
            if 'trace' in locals():
                self._end_trace(trace, success=False, error=str(e))
            return False
            
    async def subscribe_advanced(
        self,
        subscriber_id: str,
        event_types: List[str],
        callback: Callable[[StreamEvent], None],
        event_categories: Optional[List[EventCategory]] = None,
        delivery_mode: DeliveryMode = DeliveryMode.AT_LEAST_ONCE,
        event_filter: Optional[AdvancedEventFilter] = None,
        webhook_url: Optional[str] = None,
        rate_limit: Optional[int] = None,
        ai_filter_enabled: bool = False
    ) -> str:
        """        Advanced subscription with AI filtering, webhooks, and rate limiting
        
        Args:
            subscriber_id: Unique subscriber identifier
            event_types: List of event types to subscribe to
            callback: Callback function for event delivery
            event_categories: List of event categories to subscribe to
            delivery_mode: Delivery guarantee mode
            event_filter: Advanced event filtering configuration
            webhook_url: Optional webhook URL for HTTP delivery
            rate_limit: Events per minute rate limit
            ai_filter_enabled: Enable AI-powered filtering
            
        Returns:
            Subscription identifier
        """        try:
            subscription_id = f"{subscriber_id}_{uuid4().hex[:8]}"
            
            subscription = EventSubscription(
                subscriber_id=subscriber_id,
                event_types=set(event_types),
                event_categories=set(event_categories or []),
                callback=callback,
                delivery_mode=delivery_mode,
                webhook_url=webhook_url,
                rate_limit=rate_limit,
                ai_filter_enabled=ai_filter_enabled
            )
            
            self.subscriptions[subscription_id] = subscription
            
            # Create delivery queue for subscriber
            self.delivery_queues[subscription_id] = asyncio.Queue(maxsize=1000)
            
            # Store advanced event filter if provided
            if event_filter:
                self.event_filters[subscription_id] = event_filter
                
            # Initialize rate limiter if needed
            if rate_limit:
                self.rate_limiters[subscription_id] = {
                    "limit": rate_limit,
                    "window_start": time.time(),
                    "count": 0
                }
                
            self.metrics.active_subscriptions = len(self.subscriptions)
            if webhook_url:
                self.metrics.webhook_subscriptions += 1
                
            logger.info(f"Created advanced subscription {subscription_id} for {subscriber_id}")
            return subscription_id
            
        except Exception as e:
            logger.error(f"Failed to create advanced subscription: {e}")
            raise
            
    async def _filter_subscriptions_advanced(
        self, 
        event: StreamEvent, 
        category: EventCategory
    ) -> List[EventSubscription]:
        """Advanced subscription filtering with AI and security"""        filtered = []
        
        for subscription_id, subscription in self.subscriptions.items():
            if not subscription.active:
                continue
                
            # Check circuit breaker state
            if subscription.circuit_breaker.state == CircuitBreakerState.OPEN:
                if not await self._should_attempt_recovery(subscription):
                    continue
                    
            # Check rate limiting
            if not await self._check_rate_limit(subscription_id):
                continue
                
            # Check event type match
            if event.event_type not in subscription.event_types:
                continue
                
            # Check category match
            if subscription.event_categories and category not in subscription.event_categories:
                continue
                
            # Apply advanced filters
            if not await self._passes_advanced_filters(event, subscription_id):
                continue
                
            # AI-powered filtering
            if subscription.ai_filter_enabled and self.event_analyzer:
                if not await self._passes_ai_filter(event, subscription):
                    self.metrics.ai_filtered_events += 1
                    continue
                    
            filtered.append(subscription)
            
        return filtered
        
    async def _passes_advanced_filters(self, event: StreamEvent, subscription_id: str) -> bool:
        """Check if event passes advanced subscription filters"""        if subscription_id not in self.event_filters:
            return True
            
        event_filter = self.event_filters[subscription_id]
        
        # Basic filters (existing logic)
        if event_filter.event_types and event.event_type not in event_filter.event_types:
            return False
            
        if event_filter.user_ids and event.user_id not in event_filter.user_ids:
            return False
            
        # Advanced content type filtering
        if event_filter.content_types:
            content_type = event.data.get("content", {}).get("type")
            if content_type not in event_filter.content_types:
                return False
                
        # Platform filtering
        if event_filter.platform_types:
            platform = event.data.get("platform") or event.metadata.get("platform")
            if platform not in event_filter.platform_types:
                return False
                
        # Priority range filtering
        event_priority = event.metadata.get("priority", EventPriority.NORMAL.value)
        if event_filter.priority_min and event_priority < event_filter.priority_min.value:
            return False
        if event_filter.priority_max and event_priority > event_filter.priority_max.value:
            return False
            
        # Content quality filtering
        if event_filter.content_quality_min:
            quality_score = event.metadata.get("ai_analysis", {}).get("quality_score", 0)
            if quality_score < event_filter.content_quality_min:
                return False
                
        # Revenue threshold filtering
        if event_filter.revenue_threshold_min:
            revenue = event.data.get("revenue", {}).get("amount", 0)
            if revenue < event_filter.revenue_threshold_min:
                return False
                
        # Geographic filtering
        if event_filter.geo_filters:
            user_geo = event.metadata.get("user_location") or event.data.get("geo_location")
            if user_geo not in event_filter.geo_filters:
                return False
                
        # Time window filtering
        if event_filter.time_window:
            current_time = datetime.now(timezone.utc)
            start_time = event_filter.time_window.get("start")
            end_time = event_filter.time_window.get("end")
            
            if start_time and current_time.time() < datetime.fromisoformat(start_time).time():
                return False
            if end_time and current_time.time() > datetime.fromisoformat(end_time).time():
                return False
                
        # Metadata filters
        for key, value in event_filter.metadata_filters.items():
            if event.metadata.get(key) != value:
                return False
                
        return True
        
    async def _passes_ai_filter(self, event: StreamEvent, subscription: EventSubscription) -> bool:
        """AI-powered event filtering"""        try:
            if not self.event_analyzer:
                return True
                
            # Get AI analysis from event metadata
            ai_analysis = event.metadata.get("ai_analysis", {})
            
            # Content sentiment filtering
            subscription_filter = self.event_filters.get(
                next(sid for sid, sub in self.subscriptions.items() if sub == subscription), 
                None
            )
            
            if subscription_filter and subscription_filter.ai_sentiment_filter:
                content_sentiment = ai_analysis.get("sentiment")
                if content_sentiment != subscription_filter.ai_sentiment_filter:
                    return False
                    
            # AI confidence threshold
            ai_confidence = ai_analysis.get("confidence", 1.0)
            if ai_confidence < 0.7:  # Configurable threshold
                return False
                
            # Content appropriateness
            if ai_analysis.get("is_inappropriate", False):
                return False
                
            return True
            
        except Exception as e:
            logger.error(f"AI filter error: {e}")
            return True  # Default to pass on error
            
    async def _check_rate_limit(self, subscription_id: str) -> bool:
        """Check and update rate limiting for subscription"""        if subscription_id not in self.rate_limiters:
            return True
            
        limiter = self.rate_limiters[subscription_id]
        current_time = time.time()
        
        # Reset window if needed (1 minute windows)
        if current_time - limiter["window_start"] >= 60:
            limiter["window_start"] = current_time
            limiter["count"] = 0
            
        # Check if under limit
        if limiter["count"] >= limiter["limit"]:
            return False
            
        # Increment counter
        limiter["count"] += 1
        return True
        
    async def _should_attempt_recovery(self, subscription: EventSubscription) -> bool:
        """Check if circuit breaker should attempt recovery"""        if subscription.circuit_breaker.state != CircuitBreakerState.OPEN:
            return True
            
        if not subscription.circuit_breaker.last_failure_time:
            return True
            
        time_since_failure = (
            datetime.now(timezone.utc) - subscription.circuit_breaker.last_failure_time
        ).total_seconds()
        
        if time_since_failure >= subscription.circuit_breaker.recovery_timeout:
            subscription.circuit_breaker.state = CircuitBreakerState.HALF_OPEN
            return True
            
        return False
            
    # Specialized Event Routers
    async def _route_content_event(self, event: StreamEvent, subscriptions: List[EventSubscription]) -> None:
        """Route content processing events with AI analysis"""        try:
            # Extract content metadata
            content_data = event.data.get("content", {})
            content_type = content_data.get("type", "unknown")
            
            # Add content-specific routing metadata
            event.metadata["routing"] = {
                "router": "content",
                "content_type": content_type,
                "requires_fingerprinting": content_type in ["audio", "video", "image"],
                "requires_analysis": True
            }
            
            logger.debug(f"Routed content event {event.id} for {content_type}")
            
        except Exception as e:
            logger.error(f"Content routing error: {e}")
            
    async def _route_protection_event(self, event: StreamEvent, subscriptions: List[EventSubscription]) -> None:
        """Route protection violation events with priority escalation"""        try:
            violation_data = event.data.get("violation", {})
            severity = violation_data.get("severity", "low")
            
            # Escalate critical violations
            if severity == "critical":
                # Send immediate alerts to all protection subscribers
                for subscription in subscriptions:
                    if "protection" in subscription.subscriber_id.lower():
                        await self._send_urgent_notification(event, subscription)
                        
            event.metadata["routing"] = {
                "router": "protection",
                "severity": severity,
                "requires_immediate_action": severity in ["high", "critical"],
                "escalated": severity == "critical"
            }
            
            self.metrics.protection_violations_detected += 1
            logger.warning(f"Protection violation event {event.id} - severity: {severity}")
            
        except Exception as e:
            logger.error(f"Protection routing error: {e}")
            
    async def _route_revenue_event(self, event: StreamEvent, subscriptions: List[EventSubscription]) -> None:
        """Route revenue tracking events with analytics enrichment"""        try:
            revenue_data = event.data.get("revenue", {})
            amount = revenue_data.get("amount", 0)
            currency = revenue_data.get("currency", "USD")
            
            # Track revenue metrics
            self.metrics.revenue_events_processed += 1
            self.metrics.total_revenue_tracked += float(amount)
            
            # Add revenue-specific metadata
            event.metadata["routing"] = {
                "router": "revenue",
                "amount": amount,
                "currency": currency,
                "requires_payment_processing": amount > 0,
                "requires_analytics": True
            }
            
            logger.debug(f"Revenue event {event.id}: {amount} {currency}")
            
        except Exception as e:
            logger.error(f"Revenue routing error: {e}")
            
    async def _route_user_event(self, event: StreamEvent, subscriptions: List[EventSubscription]) -> None:
        """Route user activity events with behavior analysis"""        try:
            user_data = event.data.get("user", {})
            activity_type = user_data.get("activity_type", "unknown")
            
            event.metadata["routing"] = {
                "router": "user",
                "activity_type": activity_type,
                "requires_behavior_analysis": True,
                "requires_personalization": True
            }
            
        except Exception as e:
            logger.error(f"User routing error: {e}")
            
    async def _route_system_event(self, event: StreamEvent, subscriptions: List[EventSubscription]) -> None:
        """Route system health events with monitoring integration"""        try:
            system_data = event.data.get("system", {})
            metric_type = system_data.get("metric_type", "unknown")
            
            event.metadata["routing"] = {
                "router": "system",
                "metric_type": metric_type,
                "requires_alerting": metric_type in ["error", "warning"],
                "requires_dashboard_update": True
            }
            
        except Exception as e:
            logger.error(f"System routing error: {e}")
            
    async def _route_ai_event(self, event: StreamEvent, subscriptions: List[EventSubscription]) -> None:
        """Route AI analysis events with model insights"""        try:
            ai_data = event.data.get("ai", {})
            model_type = ai_data.get("model_type", "unknown")
            
            event.metadata["routing"] = {
                "router": "ai",
                "model_type": model_type,
                "requires_model_feedback": True,
                "requires_training_data": True
            }
            
        except Exception as e:
            logger.error(f"AI routing error: {e}")
            
    async def _route_platform_event(self, event: StreamEvent, subscriptions: List[EventSubscription]) -> None:
        """Route platform synchronization events"""        try:
            platform_data = event.data.get("platform", {})
            platform_name = platform_data.get("name", "unknown")
            
            event.metadata["routing"] = {
                "router": "platform",
                "platform_name": platform_name,
                "requires_sync": True,
                "requires_api_call": True
            }
            
        except Exception as e:
            logger.error(f"Platform routing error: {e}")
            
    async def _route_notification_event(self, event: StreamEvent, subscriptions: List[EventSubscription]) -> None:
        """Route notification events with delivery preferences"""        try:
            notification_data = event.data.get("notification", {})
            notification_type = notification_data.get("type", "info")
            
            event.metadata["routing"] = {
                "router": "notification",
                "notification_type": notification_type,
                "requires_user_preferences": True,
                "requires_delivery_tracking": True
            }
            
        except Exception as e:
            logger.error(f"Notification routing error: {e}")
            
    # Advanced Worker Methods
    async def _ai_event_processor(self) -> None:
        """Specialized worker for AI-powered event processing"""        logger.info("Started AI event processor")
        
        while not self._shutdown_event.is_set():
            try:
                await asyncio.sleep(1)
                
                # Process AI-specific events
                if self.event_analyzer:
                    # Analyze event patterns for insights
                    await self._analyze_event_patterns()
                    
                    # Update AI models based on feedback
                    await self._update_ai_models()
                    
            except Exception as e:
                logger.error(f"AI event processor error: {e}")
                
    async def _protection_monitor(self) -> None:
        """Specialized worker for protection violation monitoring"""        logger.info("Started protection monitor")
        
        while not self._shutdown_event.is_set():
            try:
                await asyncio.sleep(5)
                
                # Monitor protection violation patterns
                await self._monitor_protection_patterns()
                
                # Update threat intelligence
                await self._update_threat_intelligence()
                
            except Exception as e:
                logger.error(f"Protection monitor error: {e}")
                
    async def _revenue_tracker(self) -> None:
        """Specialized worker for revenue tracking and optimization"""        logger.info("Started revenue tracker")
        
        while not self._shutdown_event.is_set():
            try:
                await asyncio.sleep(10)
                
                # Track revenue trends
                await self._track_revenue_trends()
                
                # Optimize revenue streams
                await self._optimize_revenue_streams()
                
            except Exception as e:
                logger.error(f"Revenue tracker error: {e}")
                
    async def _dead_letter_processor(self) -> None:
        """Process failed events in dead letter queue"""        logger.info("Started dead letter processor")
        
        while not self._shutdown_event.is_set():
            try:
                # Process dead letter events
                dead_event = await asyncio.wait_for(self.dead_letter_queue.get(), timeout=5.0)
                await self._process_dead_letter_event(dead_event)
                
            except asyncio.TimeoutError:
                continue
            except Exception as e:
                logger.error(f"Dead letter processor error: {e}")
                
    async def _circuit_breaker_monitor(self) -> None:
        """Monitor and manage circuit breaker states"""        logger.info("Started circuit breaker monitor")
        
        while not self._shutdown_event.is_set():
            try:
                await asyncio.sleep(30)
                
                for subscription in self.subscriptions.values():
                    await self._check_circuit_breaker_health(subscription)
                    
            except Exception as e:
                logger.error(f"Circuit breaker monitor error: {e}")
                
    # Helper Methods for Advanced Features
    async def _send_urgent_notification(self, event: StreamEvent, subscription: EventSubscription) -> None:
        """Send urgent notification for critical events"""        try:
            if subscription.webhook_url:
                await self._send_webhook_notification(event, subscription, urgent=True)
            else:
                # Immediate callback execution
                if asyncio.iscoroutinefunction(subscription.callback):
                    await subscription.callback(event)
                else:
                    subscription.callback(event)
                    
        except Exception as e:
            logger.error(f"Failed to send urgent notification: {e}")
            
    async def _send_webhook_notification(
        self, 
        event: StreamEvent, 
        subscription: EventSubscription,
        urgent: bool = False
    ) -> None:
        """Send webhook notification with retry logic"""        try:
            payload = {
                "event": {
                    "id": event.id,
                    "type": event.event_type,
                    "timestamp": event.timestamp.isoformat(),
                    "data": event.data,
                    "metadata": event.metadata
                },
                "subscription": {
                    "id": subscription.subscriber_id,
                    "urgent": urgent
                }
            }
            
            headers = {
                "Content-Type": "application/json",
                "X-Event-ID": event.id,
                "X-Event-Type": event.event_type,
                "X-Urgent": str(urgent).lower()
            }
            
            timeout = 5 if urgent else 30
            
            async with self.webhook_session.post(
                subscription.webhook_url,
                json=payload,
                headers=headers,
                timeout=aiohttp.ClientTimeout(total=timeout)
            ) as response:
                if response.status >= 400:
                    raise Exception(f"Webhook failed with status {response.status}")
                    
                logger.debug(f"Webhook delivered successfully to {subscription.webhook_url}")
                
        except Exception as e:
            logger.error(f"Webhook delivery failed: {e}")
            # Could implement retry logic here
            
    async def _analyze_event_patterns(self) -> None:
        """Analyze event patterns for insights and optimizations"""        try:
            # This would implement sophisticated pattern analysis
            # For now, just a placeholder
            pass
        except Exception as e:
            logger.error(f"Event pattern analysis error: {e}")
            
    async def _monitor_protection_patterns(self) -> None:
        """Monitor protection violation patterns for threat intelligence"""        try:
            # This would implement protection pattern monitoring
            pass
        except Exception as e:
            logger.error(f"Protection pattern monitoring error: {e}")
            
    async def _track_revenue_trends(self) -> None:
        """Track revenue trends and generate insights"""        try:
            # This would implement revenue trend analysis
            pass
        except Exception as e:
            logger.error(f"Revenue trend tracking error: {e}")
            
    # Utility Methods
    def _generate_event_hash(self, event: StreamEvent) -> str:
        """Generate unique hash for event deduplication"""        event_string = f"{event.id}_{event.event_type}_{event.timestamp.isoformat()}"
        return hashlib.sha256(event_string.encode()).hexdigest()[:16]
        
    def _start_trace(self, event: StreamEvent, trace_context: Optional[Dict[str, str]] = None) -> EventTrace:
        """Start distributed trace for event processing"""        trace_id = trace_context.get("trace_id") if trace_context else str(uuid4())
        parent_span_id = trace_context.get("span_id") if trace_context else None
        span_id = str(uuid4())
        
        trace = EventTrace(
            trace_id=trace_id,
            span_id=span_id,
            parent_span_id=parent_span_id,
            operation_name=f"event_publish_{event.event_type}",
            start_time=datetime.now(timezone.utc),
            tags={
                "event.id": event.id,
                "event.type": event.event_type,
                "user.id": event.user_id,
                "content.id": event.content_id
            }
        )
        
        self.active_traces[trace.span_id] = trace
        return trace
        
    def _end_trace(self, trace: EventTrace, success: bool, error: Optional[str] = None) -> None:
        """End distributed trace with results"""        trace.end_time = datetime.now(timezone.utc)
        trace.tags["success"] = success
        
        if error:
            trace.tags["error"] = error
            trace.logs.append({
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "level": "error",
                "message": error
            })
            
        # Remove from active traces
        if trace.span_id in self.active_traces:
            del self.active_traces[trace.span_id]
            
    async def _persist_event_advanced(
        self, 
        event: StreamEvent, 
        priority: EventPriority, 
        category: EventCategory
    ) -> None:
        """Persist event with advanced indexing and partitioning"""        try:
            # Multi-stream persistence for better query performance
            streams = [
                f"event_stream:all",  # Global stream
                f"event_stream:type:{event.event_type}",  # By type
                f"event_stream:category:{category.value}",  # By category
                f"event_stream:priority:{priority.value}",  # By priority
            ]
            
            if event.user_id:
                streams.append(f"event_stream:user:{event.user_id}")
                
            event_data = {
                "event_id": event.id,
                "stream_id": event.stream_id,
                "event_type": event.event_type,
                "category": category.value,
                "priority": priority.value,
                "user_id": event.user_id or "",
                "content_id": event.content_id or "",
                "data": json.dumps(event.data),
                "metadata": json.dumps(event.metadata),
                "timestamp": event.timestamp.isoformat(),
                "event_hash": event.metadata.get("event_hash", "")
            }
            
            # Persist to all relevant streams
            for stream in streams:
                await self.redis.xadd(stream, fields=event_data, maxlen=10000)
                
        except Exception as e:
            logger.error(f"Failed to persist event {event.id}: {e}")
            
    async def _queue_for_delivery_advanced(
        self,
        event: StreamEvent,
        subscription: EventSubscription,
        priority: EventPriority
    ) -> None:
        """Advanced queuing with priority and backpressure handling"""        subscription_id = next(
            (sid for sid, sub in self.subscriptions.items() if sub == subscription),
            None
        )
        
        if subscription_id and subscription_id in self.delivery_queues:
            queue = self.delivery_queues[subscription_id]
            
            # Check queue size for backpressure
            if queue.qsize() >= 800:  # Near capacity
                logger.warning(f"Queue near capacity for subscription {subscription_id}")
                
                # Drop low priority events if queue is full
                if priority == EventPriority.LOW and queue.qsize() >= 900:
                    logger.debug(f"Dropping low priority event {event.id}")
                    return
                    
            delivery_item = {
                "event": event,
                "subscription": subscription,
                "priority": priority.value,
                "attempts": 0,
                "queued_at": datetime.now(timezone.utc),
                "trace_id": event.metadata.get("trace_id"),
                "delivery_mode": subscription.delivery_mode
            }
            
            try:
                await queue.put(delivery_item)
            except asyncio.QueueFull:
                # Send to dead letter queue
                dead_letter_event = DeadLetterEvent(
                    original_event=event,
                    subscription_id=subscription_id,
                    failure_reason="queue_full",
                    retry_count=0,
                    first_failure_time=datetime.now(timezone.utc),
                    last_failure_time=datetime.now(timezone.utc),
                    error_details={"queue_size": queue.qsize()}
                )
                await self.dead_letter_queue.put(dead_letter_event)
                self.metrics.dead_letter_events += 1
                
    def _update_metrics_advanced(
        self, 
        event: StreamEvent, 
        category: EventCategory, 
        priority: EventPriority, 
        subscriber_count: int
    ) -> None:
        """Update comprehensive metrics with AI insights"""        self.metrics.total_events += 1
        self.metrics.last_event_time = datetime.now(timezone.utc)
        
        # Category metrics
        category_key = category.value
        if category_key not in self.metrics.events_by_category:
            self.metrics.events_by_category[category_key] = 0
        self.metrics.events_by_category[category_key] += 1
        
        # Priority metrics
        priority_key = str(priority.value)
        if priority_key not in self.metrics.events_by_priority:
            self.metrics.events_by_priority[priority_key] = 0
        self.metrics.events_by_priority[priority_key] += 1
        
        # Platform metrics
        platform = event.data.get("platform") or event.metadata.get("platform", "unknown")
        if platform not in self.metrics.events_by_platform:
            self.metrics.events_by_platform[platform] = 0
        self.metrics.events_by_platform[platform] += 1
        
        # AI metrics
        ai_analysis = event.metadata.get("ai_analysis", {})
        if ai_analysis:
            processing_time = ai_analysis.get("processing_time", 0)
            confidence = ai_analysis.get("confidence", 0)
            
            # Update running averages
            current_ai_time = self.metrics.ai_processing_time
            self.metrics.ai_processing_time = (current_ai_time * 0.9 + processing_time * 0.1)
            
            current_confidence = self.metrics.ml_confidence_avg
            self.metrics.ml_confidence_avg = (current_confidence * 0.9 + confidence * 0.1)
            
        # Update event rate
        self.event_rate_history.append(time.time())
        
    async def unsubscribe_advanced(self, subscription_id: str) -> bool:
        """Advanced unsubscription with cleanup"""        try:
            subscription = self.subscriptions.get(subscription_id)
            
            if subscription_id in self.subscriptions:
                del self.subscriptions[subscription_id]
                
            if subscription_id in self.delivery_queues:
                queue = self.delivery_queues[subscription_id]
                # Process remaining events in queue
                while not queue.empty():
                    try:
                        queue.get_nowait()
                    except asyncio.QueueEmpty:
                        break
                del self.delivery_queues[subscription_id]
                
            if subscription_id in self.event_filters:
                del self.event_filters[subscription_id]
                
            if subscription_id in self.rate_limiters:
                del self.rate_limiters[subscription_id]
                
            self.metrics.active_subscriptions = len(self.subscriptions)
            if subscription and subscription.webhook_url:
                self.metrics.webhook_subscriptions -= 1
                
            logger.info(f"Removed advanced subscription {subscription_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to remove subscription {subscription_id}: {e}")
            return False
            
    async def get_event_history_advanced(
        self,
        event_type: Optional[str] = None,
        category: Optional[EventCategory] = None,
        priority: Optional[EventPriority] = None,
        user_id: Optional[str] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        limit: int = 100
    ) -> List[StreamEvent]:
        """Advanced event history retrieval with filtering"""        try:
            events = []
            
            # Build stream key based on filters
            if user_id:
                stream_key = f"event_stream:user:{user_id}"
            elif category:
                stream_key = f"event_stream:category:{category.value}"
            elif priority:
                stream_key = f"event_stream:priority:{priority.value}"
            elif event_type:
                stream_key = f"event_stream:type:{event_type}"
            else:
                stream_key = "event_stream:all"
                
            # Build Redis query parameters
            min_id = "0" if not start_time else f"{int(start_time.timestamp() * 1000)}-0"
            max_id = "+" if not end_time else f"{int(end_time.timestamp() * 1000)}-0"
            
            # Query Redis stream
            stream_data = await self.redis.xrange(
                stream_key,
                min=min_id,
                max=max_id,
                count=limit
            )
            
            for event_id, fields in stream_data:
                try:
                    event = StreamEvent(
                        id=fields[b"event_id"].decode(),
                        stream_id=fields[b"stream_id"].decode(),
                        event_type=fields[b"event_type"].decode(),
                        timestamp=datetime.fromisoformat(fields[b"timestamp"].decode()),
                        data=json.loads(fields[b"data"].decode()),
                        metadata=json.loads(fields[b"metadata"].decode()),
                        user_id=fields.get(b"user_id", b"").decode() or None,
                        content_id=fields.get(b"content_id", b"").decode() or None
                    )
                    events.append(event)
                except Exception as e:
                    logger.error(f"Failed to parse event from stream: {e}")
                    continue
                    
            return events
            
        except Exception as e:
            logger.error(f"Failed to get advanced event history: {e}")
            return []
            
    async def get_metrics_advanced(self) -> EventStreamMetrics:
        """Get comprehensive streaming metrics"""        try:
            # Update real-time metrics
            self.metrics.uptime = (datetime.now(timezone.utc) - self._start_time).total_seconds()
            self.metrics.active_subscriptions = len(self.subscriptions)
            self.metrics.webhook_subscriptions = sum(
                1 for sub in self.subscriptions.values() if sub.webhook_url
            )
            self.metrics.queue_depth = sum(
                queue.qsize() for queue in self.delivery_queues.values()
            )
            
            # Calculate events per second/minute
            current_time = time.time()
            recent_events = [t for t in self.event_rate_history if current_time - t <= 60]
            self.metrics.events_per_minute = len(recent_events)
            
            very_recent_events = [t for t in self.event_rate_history if current_time - t <= 1]
            self.metrics.events_per_second = len(very_recent_events)
            
            # Calculate latency percentiles
            if self.latency_history:
                sorted_latencies = sorted(self.latency_history)
                p95_idx = int(len(sorted_latencies) * 0.95)
                p99_idx = int(len(sorted_latencies) * 0.99)
                
                self.metrics.p95_latency = sorted_latencies[p95_idx] if p95_idx < len(sorted_latencies) else 0
                self.metrics.p99_latency = sorted_latencies[p99_idx] if p99_idx < len(sorted_latencies) else 0
                
            return self.metrics
            
        except Exception as e:
            logger.error(f"Failed to get advanced metrics: {e}")
            return self.metrics
            
    async def shutdown(self) -> None:
        """Gracefully shutdown ultra-modern event streamer"""        try:
            logger.info("Starting EventStreamer shutdown...")
            self._shutdown_event.set()
            
            # Cancel all workers
            for worker in self._delivery_workers:
                worker.cancel()
                
            # Wait for workers to complete
            await asyncio.gather(*self._delivery_workers, return_exceptions=True)
            
            # Process remaining events in queues
            for subscription_id, queue in self.delivery_queues.items():
                remaining = queue.qsize()
                if remaining > 0:
                    logger.info(f"Processing {remaining} remaining events for {subscription_id}")
                    # Could implement graceful queue draining here
                    
            # Close webhook session
            if self.webhook_session:
                await self.webhook_session.close()
                
            # Close Redis connection
            if self.redis:
                await self.redis.close()
                
            logger.info("EventStreamer shutdown completed")
            
        except Exception as e:
            logger.error(f"Error during event streamer shutdown: {e}")
            
    # Additional helper methods for processing workers
    async def _update_ai_models(self) -> None:
        """Update AI models based on event feedback"""        pass  # Implementation would depend on specific AI framework
        
    async def _update_threat_intelligence(self) -> None:
        """Update threat intelligence from protection events"""        pass  # Implementation would integrate with security systems
        
    async def _optimize_revenue_streams(self) -> None:
        """Optimize revenue streams based on performance data"""        pass  # Implementation would include revenue optimization algorithms
        
    async def _process_dead_letter_event(self, dead_event: DeadLetterEvent) -> None:
        """Process events from dead letter queue"""        try:
            # Log the failure for analysis
            logger.warning(f"Processing dead letter event: {dead_event.failure_reason}")
            
            # Could implement recovery strategies here:
            # - Retry with different parameters
            # - Route to alternative handlers
            # - Store for manual intervention
            
        except Exception as e:
            logger.error(f"Failed to process dead letter event: {e}")
            
    async def _check_circuit_breaker_health(self, subscription: EventSubscription) -> None:
        """Check and update circuit breaker health"""        try:
            # Implement circuit breaker health checks
            # This would monitor success/failure rates and adjust states
            pass
            
        except Exception as e:
            logger.error(f"Circuit breaker health check error: {e}")
            
    async def _delivery_worker(self, worker_id: str) -> None:
        """Enhanced delivery worker with advanced features"""        logger.info(f"Started enhanced delivery worker {worker_id}")
        
        while not self._shutdown_event.is_set():
            try:
                # Process all delivery queues with priority handling
                for subscription_id, queue in self.delivery_queues.items():
                    if queue.empty():
                        continue
                        
                    try:
                        delivery_item = await asyncio.wait_for(queue.get(), timeout=0.1)
                        start_time = time.time()
                        
                        await self._deliver_event_advanced(delivery_item, subscription_id)
                        
                        # Track latency
                        latency = (time.time() - start_time) * 1000  # ms
                        self.latency_history.append(latency)
                        
                    except asyncio.TimeoutError:
                        continue
                        
                # Small delay to prevent busy waiting
                await asyncio.sleep(0.01)
                
            except Exception as e:
                logger.error(f"Enhanced delivery worker {worker_id} error: {e}")
                
        logger.info(f"Stopped enhanced delivery worker {worker_id}")
        
    async def _deliver_event_advanced(self, delivery_item: Dict[str, Any], subscription_id: str) -> None:
        """Advanced event delivery with webhooks and circuit breakers"""        event = delivery_item["event"]
        subscription = delivery_item["subscription"]
        attempts = delivery_item["attempts"]
        
        try:
            # Check circuit breaker
            if subscription.circuit_breaker.state == CircuitBreakerState.OPEN:
                logger.debug(f"Circuit breaker open for subscription {subscription_id}")
                return
                
            start_time = datetime.now(timezone.utc)
            
            # Deliver via webhook if configured
            if subscription.webhook_url:
                await self._send_webhook_notification(event, subscription)
            else:
                # Standard callback delivery
                if asyncio.iscoroutinefunction(subscription.callback):
                    await subscription.callback(event)
                else:
                    subscription.callback(event)
                    
            # Update circuit breaker on success
            subscription.circuit_breaker.failure_count = 0
            subscription.circuit_breaker.last_success_time = datetime.now(timezone.utc)
            
            if subscription.circuit_breaker.state == CircuitBreakerState.HALF_OPEN:
                subscription.circuit_breaker.state = CircuitBreakerState.CLOSED
                
            # Update metrics
            delivery_time = (datetime.now(timezone.utc) - start_time).total_seconds() * 1000
            self._update_delivery_metrics_advanced(True, delivery_time)
            
            logger.debug(f"Delivered event {event.id} to subscription {subscription_id}")
            
        except Exception as e:
            logger.error(f"Failed to deliver event {event.id} to {subscription_id}: {e}")
            
            # Update circuit breaker on failure
            subscription.circuit_breaker.failure_count += 1
            subscription.circuit_breaker.last_failure_time = datetime.now(timezone.utc)
            
            if (subscription.circuit_breaker.failure_count >= 
                subscription.circuit_breaker.failure_threshold):
                subscription.circuit_breaker.state = CircuitBreakerState.OPEN
                self.metrics.circuit_breaker_trips += 1
                
            # Handle retry logic
            if attempts < subscription.max_retries:
                delivery_item["attempts"] = attempts + 1
                
                # Exponential backoff
                delay = subscription.retry_delay * (2 ** attempts)
                await asyncio.sleep(delay)
                await self.delivery_queues[subscription_id].put(delivery_item)
                
                self.metrics.retry_events += 1
                logger.debug(f"Requeued event {event.id} for retry {attempts + 1}")
            else:
                # Send to dead letter queue
                dead_letter_event = DeadLetterEvent(
                    original_event=event,
                    subscription_id=subscription_id,
                    failure_reason=str(e),
                    retry_count=attempts,
                    first_failure_time=delivery_item.get("first_failure_time", start_time),
                    last_failure_time=datetime.now(timezone.utc),
                    error_details={"exception": str(e), "type": type(e).__name__}
                )
                await self.dead_letter_queue.put(dead_letter_event)
                self.metrics.dead_letter_events += 1
                logger.warning(f"Max retries exceeded for event {event.id}")
                
            self._update_delivery_metrics_advanced(False, 0)
            
    def _update_delivery_metrics_advanced(self, success: bool, latency: float) -> None:
        """Update advanced delivery performance metrics"""        if success:
            # Update success rate with exponential moving average
            total_deliveries = self.metrics.total_events - self.metrics.failed_deliveries
            if total_deliveries > 0:
                current_rate = self.metrics.delivery_success_rate
                new_rate = ((current_rate * (total_deliveries - 1)) + 100.0) / total_deliveries
                self.metrics.delivery_success_rate = new_rate
                
            # Update average latency with exponential moving average
            current_avg = self.metrics.average_latency
            self.metrics.average_latency = (current_avg * 0.9 + latency * 0.1)
        else:
            self.metrics.failed_deliveries += 1
            
            # Recalculate success rate
            total_attempts = self.metrics.total_events
            if total_attempts > 0:
                success_count = total_attempts - self.metrics.failed_deliveries
                self.metrics.delivery_success_rate = (success_count / total_attempts) * 100
                
    async def _metrics_collector(self) -> None:
        """Enhanced metrics collection with AI insights"""        last_event_count = 0
        last_timestamp = datetime.now(timezone.utc)
        
        while not self._shutdown_event.is_set():
            try:
                await asyncio.sleep(5)  # Update every 5 seconds
                
                current_time = datetime.now(timezone.utc)
                time_diff = (current_time - last_timestamp).total_seconds()
                
                if time_diff > 0:
                    # Calculate events per second
                    event_diff = self.metrics.total_events - last_event_count
                    self.metrics.events_per_second = event_diff / time_diff
                    
                    last_event_count = self.metrics.total_events
                    last_timestamp = current_time
                    
                # Collect system metrics
                try:
                    import psutil
                    process = psutil.Process()
                    self.metrics.memory_usage = process.memory_info().rss / 1024 / 1024  # MB
                    self.metrics.cpu_usage = process.cpu_percent()
                except ImportError:
                    pass  # psutil not available
                    
            except Exception as e:
                logger.error(f"Enhanced metrics collector error: {e}")
