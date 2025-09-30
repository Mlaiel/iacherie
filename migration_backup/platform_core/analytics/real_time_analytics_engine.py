#!/usr/bin/env python3
"""
Real-Time Analytics Engine - Enterprise Creator Economy Platform
===============================================================

High-performance real-time analytics engine for live data processing,
streaming analytics, instant insights generation, and real-time alerting.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: © 2025 Fahed Mlaiel. All rights reserved.

⚠️ PROPRIÉTÉ INTELLECTUELLE EXCLUSIVE - Fahed Mlaiel (mlaiel@live.de)
Toute reproduction, distribution ou utilisation non autorisée est strictement interdite.
"""

import asyncio
import logging
import json
import time
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Callable, Set, Tuple
from dataclasses import dataclass, field
from enum import Enum
from collections import deque, defaultdict
import statistics
import numpy as np
from concurrent.futures import ThreadPoolExecutor
import queue
import weakref

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class StreamType(Enum):
    """Types of data streams"""
    CREATOR_METRICS = "creator_metrics"
    CONTENT_PERFORMANCE = "content_performance"
    ENGAGEMENT_DATA = "engagement_data"
    REVENUE_STREAM = "revenue_stream"
    USER_ACTIVITY = "user_activity"
    PLATFORM_EVENTS = "platform_events"
    SYSTEM_METRICS = "system_metrics"
    COLLABORATION_EVENTS = "collaboration_events"
    NOTIFICATION_EVENTS = "notification_events"
    SECURITY_EVENTS = "security_events"


class AlertSeverity(Enum):
    """Alert severity levels"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


class ProcessingMode(Enum):
    """Data processing modes"""
    REAL_TIME = "real_time"      # <100ms latency
    NEAR_REAL_TIME = "near_real_time"  # <1s latency
    MICRO_BATCH = "micro_batch"  # <5s latency
    STREAMING = "streaming"      # Continuous processing


@dataclass
class StreamDataPoint:
    """Individual data point in a stream"""
    stream_id: str
    stream_type: StreamType
    timestamp: datetime
    data: Dict[str, Any]
    source: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    processing_latency: Optional[float] = None


@dataclass
class RealTimeMetric:
    """Real-time metric with live updates"""
    metric_id: str
    metric_name: str
    current_value: float
    previous_value: float
    change_rate: float
    last_updated: datetime
    
    # Aggregation window
    window_size: int  # seconds
    data_points: deque = field(default_factory=lambda: deque(maxlen=1000))
    
    # Statistics
    min_value: float = float('inf')
    max_value: float = float('-inf')
    avg_value: float = 0.0
    std_deviation: float = 0.0
    
    # Alerting
    thresholds: Dict[str, float] = field(default_factory=dict)
    alert_conditions: List[str] = field(default_factory=list)


@dataclass
class RealTimeAlert:
    """Real-time alert"""
    alert_id: str
    alert_type: str
    severity: AlertSeverity
    message: str
    triggered_at: datetime
    
    # Source information
    stream_id: str
    metric_name: str
    current_value: float
    threshold_value: float
    
    # Context
    conditions_met: List[str]
    related_metrics: Dict[str, float]
    suggested_actions: List[str]
    
    # Status
    acknowledged: bool = False
    resolved: bool = False
    resolved_at: Optional[datetime] = None


@dataclass
class StreamingInsight:
    """Real-time generated insight"""
    insight_id: str
    insight_type: str
    title: str
    description: str
    confidence: float
    
    # Timing
    generated_at: datetime
    valid_until: datetime
    
    # Data
    supporting_data: Dict[str, Any]
    affected_streams: List[str]
    
    # Business impact
    impact_level: str
    recommended_actions: List[str]


class RealTimeProcessor:
    """
    High-performance real-time data processor
    
    Handles continuous data ingestion, processing, and analytics
    with minimal latency for creator economy insights.
    """
    
    def __init__(self, processing_mode: ProcessingMode = ProcessingMode.REAL_TIME):
        self.processing_mode = processing_mode
        self.data_queue = asyncio.Queue(maxsize=10000)
        self.processed_count = 0
        self.processing_errors = 0
        self.average_latency = 0.0
        self.is_running = False
        
        # Performance metrics
        self.latency_history = deque(maxlen=1000)
        self.throughput_history = deque(maxlen=100)
        self.last_throughput_check = time.time()
        self.throughput_counter = 0
        
        logger.info(f"📊 Real-time processor initialized ({processing_mode.value})")
    
    async def process_data_point(self, data_point: StreamDataPoint) -> Dict[str, Any]:
        """Process individual data point with latency tracking"""
        start_time = time.time()
        
        try:
            # Process based on stream type
            result = await self._process_by_stream_type(data_point)
            
            # Calculate latency
            processing_time = (time.time() - start_time) * 1000  # ms
            data_point.processing_latency = processing_time
            
            # Update performance metrics
            self.latency_history.append(processing_time)
            self.processed_count += 1
            self.throughput_counter += 1
            
            # Update average latency
            if len(self.latency_history) > 10:
                self.average_latency = statistics.mean(list(self.latency_history)[-100:])
            
            return result
            
        except Exception as e:
            self.processing_errors += 1
            logger.error(f"❌ Processing error for {data_point.stream_id}: {e}")
            return {"error": str(e), "data_point_id": data_point.stream_id}
    
    async def _process_by_stream_type(self, data_point: StreamDataPoint) -> Dict[str, Any]:
        """Process data point based on stream type"""
        processors = {
            StreamType.CREATOR_METRICS: self._process_creator_metrics,
            StreamType.CONTENT_PERFORMANCE: self._process_content_performance,
            StreamType.ENGAGEMENT_DATA: self._process_engagement_data,
            StreamType.REVENUE_STREAM: self._process_revenue_stream,
            StreamType.USER_ACTIVITY: self._process_user_activity,
            StreamType.PLATFORM_EVENTS: self._process_platform_events,
            StreamType.SYSTEM_METRICS: self._process_system_metrics,
            StreamType.COLLABORATION_EVENTS: self._process_collaboration_events
        }
        
        processor = processors.get(data_point.stream_type, self._process_generic)
        return await processor(data_point)
    
    async def _process_creator_metrics(self, data_point: StreamDataPoint) -> Dict[str, Any]:
        """Process creator metrics data"""
        data = data_point.data
        
        # Extract key metrics
        followers = data.get('followers', 0)
        engagement_rate = data.get('engagement_rate', 0.0)
        content_count = data.get('content_count', 0)
        
        # Calculate derived metrics
        engagement_score = followers * engagement_rate if followers > 0 else 0
        activity_level = "high" if content_count > 10 else "medium" if content_count > 5 else "low"
        
        return {
            'processed_metrics': {
                'followers': followers,
                'engagement_rate': engagement_rate,
                'engagement_score': engagement_score,
                'activity_level': activity_level
            },
            'insights': self._generate_creator_insights(data),
            'processing_timestamp': datetime.now().isoformat()
        }
    
    async def _process_content_performance(self, data_point: StreamDataPoint) -> Dict[str, Any]:
        """Process content performance data"""
        data = data_point.data
        
        # Extract performance metrics
        views = data.get('views', 0)
        likes = data.get('likes', 0)
        shares = data.get('shares', 0)
        comments = data.get('comments', 0)
        
        # Calculate performance indicators
        engagement_total = likes + shares + comments
        engagement_rate = (engagement_total / views * 100) if views > 0 else 0
        viral_score = self._calculate_viral_score(views, engagement_total, shares)
        
        return {
            'processed_performance': {
                'views': views,
                'engagement_rate': engagement_rate,
                'viral_score': viral_score,
                'performance_tier': self._classify_performance_tier(viral_score)
            },
            'insights': self._generate_content_insights(data),
            'processing_timestamp': datetime.now().isoformat()
        }
    
    async def _process_engagement_data(self, data_point: StreamDataPoint) -> Dict[str, Any]:
        """Process engagement data"""
        data = data_point.data
        
        # Process engagement patterns
        engagement_type = data.get('type', 'unknown')
        user_id = data.get('user_id')
        content_id = data.get('content_id')
        timestamp = data.get('timestamp', datetime.now().isoformat())
        
        # Calculate engagement velocity
        engagement_velocity = self._calculate_engagement_velocity(data)
        
        return {
            'processed_engagement': {
                'type': engagement_type,
                'velocity': engagement_velocity,
                'user_segment': self._classify_user_segment(user_id),
                'content_category': self._classify_content_category(content_id)
            },
            'insights': self._generate_engagement_insights(data),
            'processing_timestamp': datetime.now().isoformat()
        }
    
    async def _process_revenue_stream(self, data_point: StreamDataPoint) -> Dict[str, Any]:
        """Process revenue stream data"""
        data = data_point.data
        
        # Extract revenue data
        amount = data.get('amount', 0.0)
        currency = data.get('currency', 'USD')
        revenue_type = data.get('type', 'unknown')
        creator_id = data.get('creator_id')
        
        # Calculate revenue metrics
        normalized_amount = self._normalize_currency(amount, currency)
        revenue_category = self._classify_revenue_category(normalized_amount)
        
        return {
            'processed_revenue': {
                'normalized_amount': normalized_amount,
                'revenue_category': revenue_category,
                'revenue_velocity': self._calculate_revenue_velocity(data),
                'creator_tier': self._classify_creator_revenue_tier(creator_id, normalized_amount)
            },
            'insights': self._generate_revenue_insights(data),
            'processing_timestamp': datetime.now().isoformat()
        }
    
    async def _process_user_activity(self, data_point: StreamDataPoint) -> Dict[str, Any]:
        """Process user activity data"""
        data = data_point.data
        
        # Extract activity data
        activity_type = data.get('activity_type', 'unknown')
        user_id = data.get('user_id')
        duration = data.get('duration', 0)
        page_views = data.get('page_views', 0)
        
        # Calculate activity metrics
        engagement_intensity = self._calculate_engagement_intensity(duration, page_views)
        user_journey_stage = self._determine_user_journey_stage(data)
        
        return {
            'processed_activity': {
                'engagement_intensity': engagement_intensity,
                'journey_stage': user_journey_stage,
                'activity_score': self._calculate_activity_score(data),
                'behavior_pattern': self._identify_behavior_pattern(data)
            },
            'insights': self._generate_activity_insights(data),
            'processing_timestamp': datetime.now().isoformat()
        }
    
    async def _process_platform_events(self, data_point: StreamDataPoint) -> Dict[str, Any]:
        """Process platform events"""
        data = data_point.data
        
        event_type = data.get('event_type', 'unknown')
        severity = data.get('severity', 'info')
        affected_users = data.get('affected_users', 0)
        
        return {
            'processed_event': {
                'event_type': event_type,
                'severity': severity,
                'impact_scope': self._assess_event_impact(affected_users),
                'resolution_priority': self._determine_resolution_priority(severity, affected_users)
            },
            'insights': self._generate_platform_insights(data),
            'processing_timestamp': datetime.now().isoformat()
        }
    
    async def _process_system_metrics(self, data_point: StreamDataPoint) -> Dict[str, Any]:
        """Process system metrics"""
        data = data_point.data
        
        cpu_usage = data.get('cpu_usage', 0.0)
        memory_usage = data.get('memory_usage', 0.0)
        response_time = data.get('response_time', 0.0)
        
        system_health = self._calculate_system_health(cpu_usage, memory_usage, response_time)
        
        return {
            'processed_metrics': {
                'system_health': system_health,
                'performance_status': self._assess_performance_status(data),
                'scaling_recommendation': self._generate_scaling_recommendation(data)
            },
            'insights': self._generate_system_insights(data),
            'processing_timestamp': datetime.now().isoformat()
        }
    
    async def _process_collaboration_events(self, data_point: StreamDataPoint) -> Dict[str, Any]:
        """Process collaboration events"""
        data = data_point.data
        
        collaboration_type = data.get('type', 'unknown')
        creator_id = data.get('creator_id')
        brand_id = data.get('brand_id')
        status = data.get('status', 'unknown')
        
        return {
            'processed_collaboration': {
                'collaboration_type': collaboration_type,
                'matching_score': self._calculate_matching_score(creator_id, brand_id),
                'success_probability': self._predict_collaboration_success(data),
                'value_estimation': self._estimate_collaboration_value(data)
            },
            'insights': self._generate_collaboration_insights(data),
            'processing_timestamp': datetime.now().isoformat()
        }
    
    async def _process_generic(self, data_point: StreamDataPoint) -> Dict[str, Any]:
        """Generic data processor for unknown stream types"""
        return {
            'processed_data': data_point.data,
            'stream_type': data_point.stream_type.value,
            'processing_timestamp': datetime.now().isoformat(),
            'note': 'Processed with generic handler'
        }
    
    # Helper methods for processing logic
    def _generate_creator_insights(self, data: Dict[str, Any]) -> List[str]:
        """Generate insights for creator metrics"""
        insights = []
        
        followers = data.get('followers', 0)
        engagement_rate = data.get('engagement_rate', 0.0)
        
        if engagement_rate > 0.05:  # 5%
            insights.append("High engagement rate indicates strong audience connection")
        
        if followers > 100000:
            insights.append("Large follower base provides significant reach potential")
        
        return insights
    
    def _generate_content_insights(self, data: Dict[str, Any]) -> List[str]:
        """Generate insights for content performance"""
        insights = []
        
        views = data.get('views', 0)
        if views > 10000:
            insights.append("Content achieving significant reach")
        
        return insights
    
    def _generate_engagement_insights(self, data: Dict[str, Any]) -> List[str]:
        """Generate insights for engagement data"""
        return ["Real-time engagement tracking active"]
    
    def _generate_revenue_insights(self, data: Dict[str, Any]) -> List[str]:
        """Generate insights for revenue data"""
        insights = []
        
        amount = data.get('amount', 0.0)
        if amount > 1000:
            insights.append("High-value revenue transaction detected")
        
        return insights
    
    def _generate_activity_insights(self, data: Dict[str, Any]) -> List[str]:
        """Generate insights for user activity"""
        return ["User activity pattern analysis in progress"]
    
    def _generate_platform_insights(self, data: Dict[str, Any]) -> List[str]:
        """Generate insights for platform events"""
        return ["Platform event impact assessment completed"]
    
    def _generate_system_insights(self, data: Dict[str, Any]) -> List[str]:
        """Generate insights for system metrics"""
        insights = []
        
        cpu_usage = data.get('cpu_usage', 0.0)
        if cpu_usage > 80:
            insights.append("High CPU usage detected - consider scaling")
        
        return insights
    
    def _generate_collaboration_insights(self, data: Dict[str, Any]) -> List[str]:
        """Generate insights for collaboration events"""
        return ["Collaboration opportunity analysis completed"]
    
    # Calculation helper methods
    def _calculate_viral_score(self, views: int, engagement: int, shares: int) -> float:
        """Calculate viral score for content"""
        if views == 0:
            return 0.0
        
        engagement_rate = engagement / views
        share_rate = shares / views
        
        # Weighted viral score
        viral_score = (engagement_rate * 0.6 + share_rate * 0.4) * 100
        return min(viral_score, 100.0)  # Cap at 100
    
    def _classify_performance_tier(self, viral_score: float) -> str:
        """Classify content performance tier"""
        if viral_score >= 50:
            return "viral"
        elif viral_score >= 20:
            return "high_performing"
        elif viral_score >= 5:
            return "moderate"
        else:
            return "low"
    
    def _calculate_engagement_velocity(self, data: Dict[str, Any]) -> float:
        """Calculate engagement velocity"""
        # Simplified calculation - in real implementation would use time series
        return data.get('velocity', 1.0)
    
    def _classify_user_segment(self, user_id: Optional[str]) -> str:
        """Classify user segment"""
        # Simplified classification
        return "regular" if user_id else "anonymous"
    
    def _classify_content_category(self, content_id: Optional[str]) -> str:
        """Classify content category"""
        # Simplified classification
        return "multimedia" if content_id else "unknown"
    
    def _normalize_currency(self, amount: float, currency: str) -> float:
        """Normalize currency to USD"""
        # Simplified conversion - in real implementation would use live rates
        rates = {
            'USD': 1.0,
            'EUR': 1.1,
            'GBP': 1.25,
            'JPY': 0.007
        }
        return amount * rates.get(currency, 1.0)
    
    def _classify_revenue_category(self, amount: float) -> str:
        """Classify revenue category"""
        if amount >= 10000:
            return "enterprise"
        elif amount >= 1000:
            return "premium"
        elif amount >= 100:
            return "standard"
        else:
            return "basic"
    
    def _calculate_revenue_velocity(self, data: Dict[str, Any]) -> float:
        """Calculate revenue velocity"""
        return data.get('velocity', 0.0)
    
    def _classify_creator_revenue_tier(self, creator_id: Optional[str], amount: float) -> str:
        """Classify creator revenue tier"""
        if amount >= 5000:
            return "top_tier"
        elif amount >= 1000:
            return "mid_tier"
        else:
            return "emerging"
    
    def _calculate_engagement_intensity(self, duration: int, page_views: int) -> float:
        """Calculate engagement intensity"""
        if page_views == 0:
            return 0.0
        return duration / page_views  # Average time per page
    
    def _determine_user_journey_stage(self, data: Dict[str, Any]) -> str:
        """Determine user journey stage"""
        return data.get('journey_stage', 'exploration')
    
    def _calculate_activity_score(self, data: Dict[str, Any]) -> float:
        """Calculate user activity score"""
        duration = data.get('duration', 0)
        page_views = data.get('page_views', 0)
        
        # Simple scoring algorithm
        score = (duration * 0.1) + (page_views * 2)
        return min(score, 100.0)
    
    def _identify_behavior_pattern(self, data: Dict[str, Any]) -> str:
        """Identify user behavior pattern"""
        return data.get('behavior_pattern', 'exploring')
    
    def _assess_event_impact(self, affected_users: int) -> str:
        """Assess platform event impact"""
        if affected_users > 10000:
            return "high"
        elif affected_users > 1000:
            return "medium"
        else:
            return "low"
    
    def _determine_resolution_priority(self, severity: str, affected_users: int) -> str:
        """Determine resolution priority"""
        if severity in ['critical', 'high'] or affected_users > 5000:
            return "urgent"
        elif severity == 'medium' or affected_users > 1000:
            return "high"
        else:
            return "normal"
    
    def _calculate_system_health(self, cpu: float, memory: float, response_time: float) -> float:
        """Calculate overall system health score"""
        cpu_score = max(0, 100 - cpu)
        memory_score = max(0, 100 - memory)
        response_score = max(0, 100 - min(response_time * 10, 100))
        
        return (cpu_score + memory_score + response_score) / 3
    
    def _assess_performance_status(self, data: Dict[str, Any]) -> str:
        """Assess system performance status"""
        cpu_usage = data.get('cpu_usage', 0.0)
        memory_usage = data.get('memory_usage', 0.0)
        
        if cpu_usage > 90 or memory_usage > 90:
            return "critical"
        elif cpu_usage > 70 or memory_usage > 70:
            return "warning"
        else:
            return "healthy"
    
    def _generate_scaling_recommendation(self, data: Dict[str, Any]) -> str:
        """Generate scaling recommendation"""
        cpu_usage = data.get('cpu_usage', 0.0)
        memory_usage = data.get('memory_usage', 0.0)
        
        if cpu_usage > 80 or memory_usage > 80:
            return "scale_up"
        elif cpu_usage < 30 and memory_usage < 30:
            return "scale_down"
        else:
            return "maintain"
    
    def _calculate_matching_score(self, creator_id: Optional[str], brand_id: Optional[str]) -> float:
        """Calculate creator-brand matching score"""
        # Simplified calculation
        return 0.75 if creator_id and brand_id else 0.0
    
    def _predict_collaboration_success(self, data: Dict[str, Any]) -> float:
        """Predict collaboration success probability"""
        return data.get('success_probability', 0.7)
    
    def _estimate_collaboration_value(self, data: Dict[str, Any]) -> float:
        """Estimate collaboration value"""
        return data.get('estimated_value', 1000.0)
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get real-time processor performance metrics"""
        current_time = time.time()
        
        # Calculate throughput
        if current_time - self.last_throughput_check >= 60:  # Check every minute
            throughput_per_minute = self.throughput_counter
            self.throughput_history.append(throughput_per_minute)
            self.throughput_counter = 0
            self.last_throughput_check = current_time
        
        return {
            "processing_mode": self.processing_mode.value,
            "processed_count": self.processed_count,
            "processing_errors": self.processing_errors,
            "error_rate": self.processing_errors / max(self.processed_count, 1) * 100,
            "average_latency_ms": self.average_latency,
            "current_throughput": len(self.throughput_history),
            "queue_size": self.data_queue.qsize() if hasattr(self.data_queue, 'qsize') else 0,
            "is_running": self.is_running
        }


class RealTimeAnalyticsEngine:
    """
    Enterprise Real-Time Analytics Engine
    
    High-performance streaming analytics platform for creator economy
    with sub-100ms latency, real-time insights, and automated alerting.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize Real-Time Analytics Engine"""
        self.config = config or {}
        self.is_running = False
        self.start_time = datetime.now()
        
        # Core components
        self.processor = RealTimeProcessor(
            ProcessingMode(self.config.get('processing_mode', 'real_time'))
        )
        
        # Data management
        self.active_streams: Dict[str, Dict[str, Any]] = {}
        self.metrics: Dict[str, RealTimeMetric] = {}
        self.alerts: Dict[str, RealTimeAlert] = {}
        self.insights: Dict[str, StreamingInsight] = {}
        
        # Event handling
        self.event_handlers: Dict[str, List[Callable]] = defaultdict(list)
        self.alert_callbacks: List[Callable] = []
        self.insight_callbacks: List[Callable] = []
        
        # Performance
        self.data_queue = asyncio.Queue(maxsize=50000)
        self.processing_tasks: Set[asyncio.Task] = set()
        self.executor = ThreadPoolExecutor(max_workers=4)
        
        # Statistics
        self.total_processed = 0
        self.total_alerts = 0
        self.total_insights = 0
        self.uptime_start = datetime.now()
        
        logger.info("⚡ Real-Time Analytics Engine initialized successfully")
    
    async def start(self) -> None:
        """Start the real-time analytics engine"""
        if self.is_running:
            logger.warning("⚠️ Analytics engine is already running")
            return
        
        self.is_running = True
        self.uptime_start = datetime.now()
        
        # Start core processing tasks
        tasks = [
            asyncio.create_task(self._process_data_streams()),
            asyncio.create_task(self._monitor_metrics()),
            asyncio.create_task(self._generate_insights()),
            asyncio.create_task(self._cleanup_expired_data()),
            asyncio.create_task(self._performance_monitoring())
        ]
        
        self.processing_tasks.update(tasks)
        
        logger.info("🚀 Real-Time Analytics Engine started successfully")
        
        # Wait for all tasks
        try:
            await asyncio.gather(*tasks)
        except asyncio.CancelledError:
            logger.info("📊 Real-Time Analytics Engine stopped")
    
    async def stop(self) -> None:
        """Stop the real-time analytics engine"""
        if not self.is_running:
            return
        
        self.is_running = False
        
        # Cancel all processing tasks
        for task in self.processing_tasks:
            task.cancel()
        
        # Wait for tasks to complete
        await asyncio.gather(*self.processing_tasks, return_exceptions=True)
        
        # Cleanup
        self.processing_tasks.clear()
        self.executor.shutdown(wait=True)
        
        logger.info("⏹️ Real-Time Analytics Engine stopped")
    
    async def ingest_data(
        self,
        stream_id: str,
        stream_type: StreamType,
        data: Dict[str, Any],
        source: str = "unknown"
    ) -> bool:
        """Ingest real-time data point"""
        try:
            data_point = StreamDataPoint(
                stream_id=stream_id,
                stream_type=stream_type,
                timestamp=datetime.now(),
                data=data,
                source=source
            )
            
            # Add to processing queue
            await self.data_queue.put(data_point)
            
            # Update stream tracking
            if stream_id not in self.active_streams:
                self.active_streams[stream_id] = {
                    'stream_type': stream_type,
                    'first_seen': datetime.now(),
                    'last_seen': datetime.now(),
                    'data_points': 0,
                    'source': source
                }
            
            self.active_streams[stream_id]['last_seen'] = datetime.now()
            self.active_streams[stream_id]['data_points'] += 1
            
            return True
            
        except asyncio.QueueFull:
            logger.warning(f"⚠️ Data queue full, dropping data point from {stream_id}")
            return False
        except Exception as e:
            logger.error(f"❌ Failed to ingest data from {stream_id}: {e}")
            return False
    
    async def _process_data_streams(self) -> None:
        """Main data processing loop"""
        logger.info("📊 Starting data stream processing")
        
        while self.is_running:
            try:
                # Get data point with timeout
                data_point = await asyncio.wait_for(
                    self.data_queue.get(),
                    timeout=1.0
                )
                
                # Process data point
                result = await self.processor.process_data_point(data_point)
                
                # Update metrics
                await self._update_metrics(data_point, result)
                
                # Check for alerts
                await self._check_alerts(data_point, result)
                
                # Generate real-time insights
                await self._process_insights(data_point, result)
                
                # Trigger event handlers
                await self._trigger_event_handlers(data_point, result)
                
                self.total_processed += 1
                
            except asyncio.TimeoutError:
                # No data available, continue
                continue
            except Exception as e:
                logger.error(f"❌ Error processing data stream: {e}")
                await asyncio.sleep(0.1)  # Brief pause on error
    
    async def _update_metrics(
        self,
        data_point: StreamDataPoint,
        result: Dict[str, Any]
    ) -> None:
        """Update real-time metrics"""
        try:
            # Extract numeric values from result
            for key, value in result.get('processed_metrics', {}).items():
                if isinstance(value, (int, float)):
                    metric_id = f"{data_point.stream_id}_{key}"
                    
                    if metric_id not in self.metrics:
                        self.metrics[metric_id] = RealTimeMetric(
                            metric_id=metric_id,
                            metric_name=key,
                            current_value=value,
                            previous_value=value,
                            change_rate=0.0,
                            last_updated=datetime.now(),
                            window_size=300  # 5 minutes
                        )
                    else:
                        metric = self.metrics[metric_id]
                        metric.previous_value = metric.current_value
                        metric.current_value = value
                        metric.change_rate = ((value - metric.previous_value) / 
                                            max(metric.previous_value, 1)) * 100
                        metric.last_updated = datetime.now()
                        
                        # Update data points
                        metric.data_points.append({
                            'timestamp': datetime.now(),
                            'value': value
                        })
                        
                        # Update statistics
                        metric.min_value = min(metric.min_value, value)
                        metric.max_value = max(metric.max_value, value)
                        
                        # Calculate rolling average
                        recent_values = [dp['value'] for dp in list(metric.data_points)[-100:]]
                        metric.avg_value = statistics.mean(recent_values) if recent_values else value
                        
                        if len(recent_values) > 1:
                            metric.std_deviation = statistics.stdev(recent_values)
                        
        except Exception as e:
            logger.error(f"❌ Failed to update metrics: {e}")
    
    async def _check_alerts(
        self,
        data_point: StreamDataPoint,
        result: Dict[str, Any]
    ) -> None:
        """Check for alert conditions"""
        try:
            # Check metric thresholds
            for metric_id, metric in self.metrics.items():
                if not metric.thresholds:
                    continue
                
                alerts_triggered = []
                
                # Check each threshold
                for threshold_name, threshold_value in metric.thresholds.items():
                    if threshold_name == 'max' and metric.current_value > threshold_value:
                        alerts_triggered.append(f"Value {metric.current_value} exceeds maximum {threshold_value}")
                    elif threshold_name == 'min' and metric.current_value < threshold_value:
                        alerts_triggered.append(f"Value {metric.current_value} below minimum {threshold_value}")
                    elif threshold_name == 'change_rate' and abs(metric.change_rate) > threshold_value:
                        alerts_triggered.append(f"Change rate {metric.change_rate}% exceeds threshold {threshold_value}%")
                
                # Create alerts
                for alert_message in alerts_triggered:
                    await self._create_alert(
                        alert_type="threshold_exceeded",
                        severity=AlertSeverity.HIGH,
                        message=alert_message,
                        stream_id=data_point.stream_id,
                        metric_name=metric.metric_name,
                        current_value=metric.current_value,
                        threshold_value=threshold_value
                    )
            
            # Check for anomalies in processing result
            insights = result.get('insights', [])
            for insight in insights:
                if 'anomaly' in insight.lower() or 'alert' in insight.lower():
                    await self._create_alert(
                        alert_type="anomaly_detected",
                        severity=AlertSeverity.MEDIUM,
                        message=insight,
                        stream_id=data_point.stream_id,
                        metric_name="anomaly_detection",
                        current_value=0.0,
                        threshold_value=0.0
                    )
                    
        except Exception as e:
            logger.error(f"❌ Failed to check alerts: {e}")
    
    async def _create_alert(
        self,
        alert_type: str,
        severity: AlertSeverity,
        message: str,
        stream_id: str,
        metric_name: str,
        current_value: float,
        threshold_value: float
    ) -> None:
        """Create and process new alert"""
        try:
            alert_id = f"alert_{alert_type}_{stream_id}_{int(time.time())}"
            
            alert = RealTimeAlert(
                alert_id=alert_id,
                alert_type=alert_type,
                severity=severity,
                message=message,
                triggered_at=datetime.now(),
                stream_id=stream_id,
                metric_name=metric_name,
                current_value=current_value,
                threshold_value=threshold_value,
                conditions_met=[f"{alert_type} condition met"],
                related_metrics={metric_name: current_value},
                suggested_actions=self._generate_alert_actions(alert_type, severity)
            )
            
            self.alerts[alert_id] = alert
            self.total_alerts += 1
            
            # Trigger alert callbacks
            for callback in self.alert_callbacks:
                try:
                    await callback(alert)
                except Exception as e:
                    logger.error(f"❌ Alert callback error: {e}")
            
            logger.warning(f"🚨 Alert created: {alert.message}")
            
        except Exception as e:
            logger.error(f"❌ Failed to create alert: {e}")
    
    def _generate_alert_actions(self, alert_type: str, severity: AlertSeverity) -> List[str]:
        """Generate suggested actions for alert"""
        actions = []
        
        if severity in [AlertSeverity.CRITICAL, AlertSeverity.HIGH]:
            actions.extend([
                "Investigate immediately",
                "Check system logs",
                "Verify data sources"
            ])
        
        if alert_type == "threshold_exceeded":
            actions.extend([
                "Review threshold settings",
                "Analyze trend patterns",
                "Consider scaling if needed"
            ])
        elif alert_type == "anomaly_detected":
            actions.extend([
                "Analyze anomaly pattern",
                "Check for external factors",
                "Review recent changes"
            ])
        
        return actions
    
    async def _process_insights(
        self,
        data_point: StreamDataPoint,
        result: Dict[str, Any]
    ) -> None:
        """Process and generate real-time insights"""
        try:
            insights_data = result.get('insights', [])
            
            for insight_text in insights_data:
                insight_id = f"insight_{data_point.stream_id}_{int(time.time())}"
                
                insight = StreamingInsight(
                    insight_id=insight_id,
                    insight_type="real_time_analysis",
                    title=f"Real-time insight for {data_point.stream_type.value}",
                    description=insight_text,
                    confidence=0.8,  # Default confidence
                    generated_at=datetime.now(),
                    valid_until=datetime.now() + timedelta(minutes=30),
                    supporting_data=result,
                    affected_streams=[data_point.stream_id],
                    impact_level="medium",
                    recommended_actions=self._generate_insight_actions(insight_text)
                )
                
                self.insights[insight_id] = insight
                self.total_insights += 1
                
                # Trigger insight callbacks
                for callback in self.insight_callbacks:
                    try:
                        await callback(insight)
                    except Exception as e:
                        logger.error(f"❌ Insight callback error: {e}")
                        
        except Exception as e:
            logger.error(f"❌ Failed to process insights: {e}")
    
    def _generate_insight_actions(self, insight_text: str) -> List[str]:
        """Generate recommended actions for insight"""
        actions = []
        
        if "high" in insight_text.lower():
            actions.append("Capitalize on high performance")
        if "engagement" in insight_text.lower():
            actions.append("Optimize engagement strategies")
        if "revenue" in insight_text.lower():
            actions.append("Focus on revenue optimization")
        
        if not actions:
            actions.append("Monitor trend continuation")
        
        return actions
    
    async def _trigger_event_handlers(
        self,
        data_point: StreamDataPoint,
        result: Dict[str, Any]
    ) -> None:
        """Trigger registered event handlers"""
        try:
            stream_type_key = data_point.stream_type.value
            
            if stream_type_key in self.event_handlers:
                for handler in self.event_handlers[stream_type_key]:
                    try:
                        await handler(data_point, result)
                    except Exception as e:
                        logger.error(f"❌ Event handler error: {e}")
                        
        except Exception as e:
            logger.error(f"❌ Failed to trigger event handlers: {e}")
    
    async def _monitor_metrics(self) -> None:
        """Monitor metrics and maintain data quality"""
        logger.info("📈 Starting metrics monitoring")
        
        while self.is_running:
            try:
                # Clean up old data points
                current_time = datetime.now()
                for metric in self.metrics.values():
                    # Remove data points older than window size
                    window_start = current_time - timedelta(seconds=metric.window_size)
                    
                    # Filter data points
                    metric.data_points = deque([
                        dp for dp in metric.data_points 
                        if dp['timestamp'] > window_start
                    ], maxlen=metric.data_points.maxlen)
                
                await asyncio.sleep(60)  # Check every minute
                
            except Exception as e:
                logger.error(f"❌ Error in metrics monitoring: {e}")
                await asyncio.sleep(60)
    
    async def _generate_insights(self) -> None:
        """Generate periodic insights from accumulated data"""
        logger.info("💡 Starting insight generation")
        
        while self.is_running:
            try:
                # Generate insights every 5 minutes
                await asyncio.sleep(300)
                
                # Analyze metric trends
                await self._analyze_metric_trends()
                
                # Analyze cross-stream correlations
                await self._analyze_stream_correlations()
                
            except Exception as e:
                logger.error(f"❌ Error in insight generation: {e}")
                await asyncio.sleep(300)
    
    async def _analyze_metric_trends(self) -> None:
        """Analyze trends in metrics"""
        try:
            for metric in self.metrics.values():
                if len(metric.data_points) < 10:
                    continue
                
                # Extract values for trend analysis
                values = [dp['value'] for dp in list(metric.data_points)[-20:]]
                
                if len(values) >= 10:
                    # Simple trend detection
                    first_half = values[:len(values)//2]
                    second_half = values[len(values)//2:]
                    
                    first_avg = statistics.mean(first_half)
                    second_avg = statistics.mean(second_half)
                    
                    change_percent = ((second_avg - first_avg) / max(first_avg, 1)) * 100
                    
                    if abs(change_percent) > 20:  # Significant trend
                        trend_direction = "increasing" if change_percent > 0 else "decreasing"
                        
                        insight_id = f"trend_insight_{metric.metric_id}_{int(time.time())}"
                        insight = StreamingInsight(
                            insight_id=insight_id,
                            insight_type="trend_analysis",
                            title=f"Trend detected in {metric.metric_name}",
                            description=f"{trend_direction.title()} trend detected with {abs(change_percent):.1f}% change",
                            confidence=0.7,
                            generated_at=datetime.now(),
                            valid_until=datetime.now() + timedelta(hours=1),
                            supporting_data={
                                'change_percent': change_percent,
                                'trend_direction': trend_direction,
                                'data_points': len(values)
                            },
                            affected_streams=[metric.metric_id.split('_')[0]],
                            impact_level="medium" if abs(change_percent) > 50 else "low",
                            recommended_actions=[
                                f"Monitor {trend_direction} trend in {metric.metric_name}",
                                "Investigate underlying causes",
                                "Adjust strategies accordingly"
                            ]
                        )
                        
                        self.insights[insight_id] = insight
                        self.total_insights += 1
                        
        except Exception as e:
            logger.error(f"❌ Failed to analyze metric trends: {e}")
    
    async def _analyze_stream_correlations(self) -> None:
        """Analyze correlations between different streams"""
        try:
            # Simple correlation analysis between metrics
            metric_names = list(self.metrics.keys())
            
            for i, metric1_id in enumerate(metric_names):
                for metric2_id in metric_names[i+1:]:
                    metric1 = self.metrics[metric1_id]
                    metric2 = self.metrics[metric2_id]
                    
                    if (len(metric1.data_points) >= 10 and 
                        len(metric2.data_points) >= 10):
                        
                        # Extract recent values
                        values1 = [dp['value'] for dp in list(metric1.data_points)[-10:]]
                        values2 = [dp['value'] for dp in list(metric2.data_points)[-10:]]
                        
                        if len(values1) == len(values2):
                            # Calculate correlation
                            correlation = np.corrcoef(values1, values2)[0, 1]
                            
                            if not np.isnan(correlation) and abs(correlation) > 0.7:
                                insight_id = f"correlation_insight_{metric1_id}_{metric2_id}_{int(time.time())}"
                                
                                insight = StreamingInsight(
                                    insight_id=insight_id,
                                    insight_type="correlation_analysis",
                                    title=f"Strong correlation detected",
                                    description=f"Strong {'positive' if correlation > 0 else 'negative'} correlation ({correlation:.2f}) between {metric1.metric_name} and {metric2.metric_name}",
                                    confidence=abs(correlation),
                                    generated_at=datetime.now(),
                                    valid_until=datetime.now() + timedelta(hours=2),
                                    supporting_data={
                                        'correlation': correlation,
                                        'metric1': metric1.metric_name,
                                        'metric2': metric2.metric_name
                                    },
                                    affected_streams=[
                                        metric1_id.split('_')[0],
                                        metric2_id.split('_')[0]
                                    ],
                                    impact_level="medium",
                                    recommended_actions=[
                                        "Leverage correlation for optimization",
                                        "Monitor relationship stability",
                                        "Consider joint strategies"
                                    ]
                                )
                                
                                self.insights[insight_id] = insight
                                self.total_insights += 1
                                
        except Exception as e:
            logger.error(f"❌ Failed to analyze stream correlations: {e}")
    
    async def _cleanup_expired_data(self) -> None:
        """Clean up expired insights and alerts"""
        logger.info("🧹 Starting data cleanup")
        
        while self.is_running:
            try:
                current_time = datetime.now()
                
                # Clean up expired insights
                expired_insights = [
                    insight_id for insight_id, insight in self.insights.items()
                    if insight.valid_until < current_time
                ]
                
                for insight_id in expired_insights:
                    del self.insights[insight_id]
                
                # Clean up old alerts (keep for 24 hours)
                old_alerts = [
                    alert_id for alert_id, alert in self.alerts.items()
                    if (current_time - alert.triggered_at).total_seconds() > 86400
                ]
                
                for alert_id in old_alerts:
                    del self.alerts[alert_id]
                
                # Clean up inactive streams
                inactive_streams = [
                    stream_id for stream_id, stream_info in self.active_streams.items()
                    if (current_time - stream_info['last_seen']).total_seconds() > 3600  # 1 hour
                ]
                
                for stream_id in inactive_streams:
                    del self.active_streams[stream_id]
                
                logger.info(f"🧹 Cleaned up {len(expired_insights)} insights, {len(old_alerts)} alerts, {len(inactive_streams)} streams")
                
                await asyncio.sleep(1800)  # Clean every 30 minutes
                
            except Exception as e:
                logger.error(f"❌ Error in data cleanup: {e}")
                await asyncio.sleep(1800)
    
    async def _performance_monitoring(self) -> None:
        """Monitor system performance"""
        while self.is_running:
            try:
                # Log performance metrics every 5 minutes
                processor_metrics = self.processor.get_performance_metrics()
                engine_metrics = self.get_system_status()
                
                logger.info(f"📊 Performance: {processor_metrics['processed_count']} processed, "
                           f"{processor_metrics['average_latency_ms']:.1f}ms avg latency, "
                           f"{processor_metrics['error_rate']:.1f}% error rate")
                
                await asyncio.sleep(300)  # Every 5 minutes
                
            except Exception as e:
                logger.error(f"❌ Error in performance monitoring: {e}")
                await asyncio.sleep(300)
    
    # Event registration methods
    def register_event_handler(self, stream_type: StreamType, handler: Callable) -> None:
        """Register event handler for specific stream type"""
        self.event_handlers[stream_type.value].append(handler)
        logger.info(f"📝 Registered event handler for {stream_type.value}")
    
    def register_alert_callback(self, callback: Callable) -> None:
        """Register callback for alerts"""
        self.alert_callbacks.append(callback)
        logger.info("🚨 Registered alert callback")
    
    def register_insight_callback(self, callback: Callable) -> None:
        """Register callback for insights"""
        self.insight_callbacks.append(callback)
        logger.info("💡 Registered insight callback")
    
    # Configuration methods
    def set_metric_threshold(
        self,
        metric_pattern: str,
        threshold_type: str,
        threshold_value: float
    ) -> None:
        """Set threshold for metric pattern"""
        for metric_id, metric in self.metrics.items():
            if metric_pattern in metric_id:
                metric.thresholds[threshold_type] = threshold_value
                logger.info(f"📏 Set {threshold_type} threshold {threshold_value} for {metric_id}")
    
    def get_active_streams(self) -> Dict[str, Dict[str, Any]]:
        """Get information about active streams"""
        return dict(self.active_streams)
    
    def get_current_metrics(self) -> Dict[str, Dict[str, Any]]:
        """Get current metric values"""
        return {
            metric_id: {
                'current_value': metric.current_value,
                'change_rate': metric.change_rate,
                'last_updated': metric.last_updated.isoformat(),
                'data_points_count': len(metric.data_points),
                'avg_value': metric.avg_value,
                'min_value': metric.min_value,
                'max_value': metric.max_value
            }
            for metric_id, metric in self.metrics.items()
        }
    
    def get_active_alerts(self) -> Dict[str, Dict[str, Any]]:
        """Get active alerts"""
        return {
            alert_id: {
                'alert_type': alert.alert_type,
                'severity': alert.severity.value,
                'message': alert.message,
                'triggered_at': alert.triggered_at.isoformat(),
                'stream_id': alert.stream_id,
                'metric_name': alert.metric_name,
                'current_value': alert.current_value,
                'acknowledged': alert.acknowledged,
                'resolved': alert.resolved
            }
            for alert_id, alert in self.alerts.items()
            if not alert.resolved
        }
    
    def get_recent_insights(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent insights"""
        sorted_insights = sorted(
            self.insights.values(),
            key=lambda x: x.generated_at,
            reverse=True
        )
        
        return [
            {
                'insight_id': insight.insight_id,
                'insight_type': insight.insight_type,
                'title': insight.title,
                'description': insight.description,
                'confidence': insight.confidence,
                'generated_at': insight.generated_at.isoformat(),
                'impact_level': insight.impact_level,
                'affected_streams': insight.affected_streams,
                'recommended_actions': insight.recommended_actions
            }
            for insight in sorted_insights[:limit]
        ]
    
    def acknowledge_alert(self, alert_id: str) -> bool:
        """Acknowledge an alert"""
        if alert_id in self.alerts:
            self.alerts[alert_id].acknowledged = True
            logger.info(f"✅ Alert {alert_id} acknowledged")
            return True
        return False
    
    def resolve_alert(self, alert_id: str) -> bool:
        """Resolve an alert"""
        if alert_id in self.alerts:
            alert = self.alerts[alert_id]
            alert.resolved = True
            alert.resolved_at = datetime.now()
            logger.info(f"✅ Alert {alert_id} resolved")
            return True
        return False
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get comprehensive system status"""
        uptime = datetime.now() - self.uptime_start
        processor_metrics = self.processor.get_performance_metrics()
        
        return {
            "system_name": "Real-Time Analytics Engine",
            "system_status": "operational" if self.is_running else "stopped",
            "version": "1.0.0",
            "uptime_seconds": uptime.total_seconds(),
            "uptime_formatted": str(uptime),
            "started_at": self.uptime_start.isoformat(),
            "processing_status": {
                "is_running": self.is_running,
                "queue_size": self.data_queue.qsize() if hasattr(self.data_queue, 'qsize') else 0,
                "active_streams": len(self.active_streams),
                "active_metrics": len(self.metrics),
                "active_alerts": len([a for a in self.alerts.values() if not a.resolved]),
                "active_insights": len(self.insights)
            },
            "performance_metrics": {
                "total_processed": self.total_processed,
                "total_alerts": self.total_alerts,
                "total_insights": self.total_insights,
                "processing_rate": self.total_processed / max(uptime.total_seconds(), 1),
                **processor_metrics
            },
            "capabilities": [
                "Real-time data ingestion (<100ms latency)",
                "Streaming analytics and processing",
                "Automated anomaly detection",
                "Real-time alerting system",
                "Live insight generation",
                "Multi-stream correlation analysis",
                "Performance monitoring",
                "Event-driven architecture"
            ],
            "supported_streams": [stream_type.value for stream_type in StreamType],
            "last_updated": datetime.now().isoformat()
        }


# Export classes and functions
__all__ = [
    'RealTimeAnalyticsEngine',
    'RealTimeProcessor',
    'StreamDataPoint',
    'RealTimeMetric',
    'RealTimeAlert',
    'StreamingInsight',
    'StreamType',
    'AlertSeverity',
    'ProcessingMode'
]