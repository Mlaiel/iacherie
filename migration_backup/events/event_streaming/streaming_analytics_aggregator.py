"""IA Influencer Agent - Streaming Analytics Aggregator
Real-time Analytics and Aggregations for Ainflue Platform Streaming Events

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
Version: 3.0.0

⚠️ LEGAL WARNING: Unauthorized use prohibited. This is proprietary technology.
"""

from typing import Dict, Any, List, Optional, Callable, Union, Set, Tuple
from datetime import datetime, timezone, timedelta
from dataclasses import dataclass, field
from abc import ABC, abstractmethod
from enum import Enum
import asyncio
import json
import logging
import time
import statistics
import math
from uuid import uuid4
from collections import defaultdict, deque, Counter

logger = logging.getLogger(__name__)


class AggregationFunction(Enum):
    """Aggregation function types"""
    COUNT = "count"
    SUM = "sum"
    AVERAGE = "average"
    MIN = "minimum"
    MAX = "maximum"
    DISTINCT_COUNT = "distinct_count"
    PERCENTILE_50 = "p50"
    PERCENTILE_95 = "p95"
    PERCENTILE_99 = "p99"
    STANDARD_DEVIATION = "stddev"
    VARIANCE = "variance"


class WindowType(Enum):
    """Window types for aggregations"""
    TUMBLING = "tumbling"
    SLIDING = "sliding"
    SESSION = "session"
    GLOBAL = "global"


class AlertSeverity(Enum):
    """Alert severity levels"""
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"


@dataclass
class AggregationSpec:
    """Specification for an aggregation"""
    
    name: str
    function: AggregationFunction
    field: str
    group_by: List[str] = field(default_factory=list)
    filter_condition: Optional[str] = None
    window_size: Optional[timedelta] = None
    percentile: Optional[float] = None


@dataclass
class WindowSpec:
    """Window specification for aggregations"""
    
    window_type: WindowType
    size: timedelta
    slide: Optional[timedelta] = None
    session_timeout: Optional[timedelta] = None
    allowed_lateness: timedelta = timedelta(minutes=5)
    grace_period: timedelta = timedelta(minutes=1)


@dataclass
class AggregationResult:
    """Result of an aggregation computation"""
    
    aggregation_name: str
    window_start: datetime
    window_end: datetime
    group_key: Dict[str, Any]
    value: Union[float, int, Dict[str, Any]]
    count: int
    timestamp: datetime


@dataclass
class AlertRule:
    """Alert rule configuration"""
    
    rule_name: str
    aggregation_name: str
    condition: str  # e.g., "value > 1000"
    severity: AlertSeverity
    cooldown_minutes: int = 15
    message_template: str = "Alert: {rule_name} triggered with value {value}"


class AggregationWindow:
    """Manages aggregation windows and computations"""
    
    def __init__(self, spec: WindowSpec):
        self.spec = spec
        self.events: List[Tuple[datetime, Dict[str, Any]]] = []
        self.watermark = datetime.min.replace(tzinfo=timezone.utc)
        
    def add_event(self, event_time: datetime, event_data: Dict[str, Any]):
        """Add event to window"""
        self.events.append((event_time, event_data))
        
        # Sort events by time
        self.events.sort(key=lambda x: x[0])
        
        # Remove events outside allowed lateness
        cutoff_time = self.watermark - self.spec.allowed_lateness
        self.events = [(t, d) for t, d in self.events if t >= cutoff_time]
    
    def update_watermark(self, new_watermark: datetime):
        """Update watermark and trigger window computations"""
        if new_watermark > self.watermark:
            self.watermark = new_watermark
    
    def get_active_windows(self, current_time: datetime) -> List[Tuple[datetime, datetime]]:
        """Get active windows for current time"""
        windows = []
        
        if self.spec.window_type == WindowType.TUMBLING:
            window_size_seconds = self.spec.size.total_seconds()
            
            # Calculate window boundaries
            for event_time, _ in self.events:
                window_start = datetime.fromtimestamp(
                    (event_time.timestamp() // window_size_seconds) * window_size_seconds,
                    tz=timezone.utc
                )
                window_end = window_start + self.spec.size
                
                if (window_start, window_end) not in windows:
                    windows.append((window_start, window_end))
        
        elif self.spec.window_type == WindowType.SLIDING:
            slide_seconds = self.spec.slide.total_seconds() if self.spec.slide else self.spec.size.total_seconds()
            window_size_seconds = self.spec.size.total_seconds()
            
            # Calculate sliding windows
            start_time = min(event_time for event_time, _ in self.events) if self.events else current_time
            current_window_start = start_time
            
            while current_window_start <= current_time:
                window_end = current_window_start + self.spec.size
                windows.append((current_window_start, window_end))
                current_window_start += timedelta(seconds=slide_seconds)
        
        elif self.spec.window_type == WindowType.SESSION:
            # Group events into sessions based on timeout
            sessions = []
            current_session_start = None
            current_session_end = None
            
            for event_time, _ in sorted(self.events):
                if current_session_start is None:
                    current_session_start = event_time
                    current_session_end = event_time
                elif event_time - current_session_end <= self.spec.session_timeout:
                    current_session_end = event_time
                else:
                    sessions.append((current_session_start, current_session_end))
                    current_session_start = event_time
                    current_session_end = event_time
            
            if current_session_start is not None:
                sessions.append((current_session_start, current_session_end))
            
            windows = sessions
        
        elif self.spec.window_type == WindowType.GLOBAL:
            if self.events:
                start_time = min(event_time for event_time, _ in self.events)
                end_time = max(event_time for event_time, _ in self.events)
                windows = [(start_time, end_time)]
        
        return windows
    
    def get_events_in_window(self, window_start: datetime, window_end: datetime) -> List[Dict[str, Any]]:
        """Get events within a specific window"""
        return [
            event_data for event_time, event_data in self.events
            if window_start <= event_time < window_end
        ]


class AggregationComputer:
    """Computes aggregations on event data"""
    
    @staticmethod
    def compute(events: List[Dict[str, Any]], spec: AggregationSpec) -> Union[float, int, Dict[str, Any]]:
        """Compute aggregation for events"""
        try:
            if not events:
                return 0
            
            # Extract field values
            values = []
            for event in events:
                value = AggregationComputer._extract_field_value(event, spec.field)
                if value is not None:
                    values.append(value)
            
            if not values:
                return 0
            
            # Compute aggregation
            if spec.function == AggregationFunction.COUNT:
                return len(values)
            
            elif spec.function == AggregationFunction.SUM:
                return sum(values)
            
            elif spec.function == AggregationFunction.AVERAGE:
                return statistics.mean(values)
            
            elif spec.function == AggregationFunction.MIN:
                return min(values)
            
            elif spec.function == AggregationFunction.MAX:
                return max(values)
            
            elif spec.function == AggregationFunction.DISTINCT_COUNT:
                return len(set(values))
            
            elif spec.function == AggregationFunction.PERCENTILE_50:
                return statistics.median(values)
            
            elif spec.function == AggregationFunction.PERCENTILE_95:
                return AggregationComputer._percentile(values, 0.95)
            
            elif spec.function == AggregationFunction.PERCENTILE_99:
                return AggregationComputer._percentile(values, 0.99)
            
            elif spec.function == AggregationFunction.STANDARD_DEVIATION:
                return statistics.stdev(values) if len(values) > 1 else 0
            
            elif spec.function == AggregationFunction.VARIANCE:
                return statistics.variance(values) if len(values) > 1 else 0
            
            else:
                logger.warning(f"Unsupported aggregation function: {spec.function}")
                return 0
                
        except Exception as e:
            logger.error(f"Error computing aggregation {spec.name}: {e}")
            return 0
    
    @staticmethod
    def _extract_field_value(event: Dict[str, Any], field_path: str) -> Any:
        """Extract field value from event using dot notation"""
        try:
            value = event
            for part in field_path.split('.'):
                value = value.get(part)
                if value is None:
                    return None
            return value
        except Exception:
            return None
    
    @staticmethod
    def _percentile(values: List[float], percentile: float) -> float:
        """Calculate percentile value"""
        if not values:
            return 0
        
        sorted_values = sorted(values)
        index = percentile * (len(sorted_values) - 1)
        
        if index.is_integer():
            return sorted_values[int(index)]
        else:
            lower_index = int(math.floor(index))
            upper_index = int(math.ceil(index))
            weight = index - lower_index
            
            return sorted_values[lower_index] * (1 - weight) + sorted_values[upper_index] * weight


class CreatorPerformanceAggregator:
    """Aggregator for creator performance metrics"""
    
    def __init__(self):
        self.window = AggregationWindow(WindowSpec(
            window_type=WindowType.SLIDING,
            size=timedelta(hours=1),
            slide=timedelta(minutes=5)
        ))
        
        self.aggregations = [
            AggregationSpec("uploads_per_hour", AggregationFunction.COUNT, "event_id", ["creator_id"]),
            AggregationSpec("avg_content_size", AggregationFunction.AVERAGE, "payload.content_size", ["creator_id"]),
            AggregationSpec("total_content_size", AggregationFunction.SUM, "payload.content_size", ["creator_id"]),
            AggregationSpec("unique_content_types", AggregationFunction.DISTINCT_COUNT, "payload.content_type", ["creator_id"])
        ]
    
    async def process_event(self, event: Dict[str, Any]) -> List[AggregationResult]:
        """Process event and compute creator performance aggregations"""
        try:
            event_time = datetime.fromisoformat(event.get("timestamp", datetime.now(timezone.utc).isoformat()))
            self.window.add_event(event_time, event)
            
            # Update watermark
            current_time = datetime.now(timezone.utc)
            self.window.update_watermark(current_time)
            
            results = []
            
            # Get active windows
            windows = self.window.get_active_windows(current_time)
            
            for window_start, window_end in windows:
                window_events = self.window.get_events_in_window(window_start, window_end)
                
                # Group events by creator_id
                events_by_creator = defaultdict(list)
                for window_event in window_events:
                    creator_id = window_event.get("payload", {}).get("creator_id")
                    if creator_id:
                        events_by_creator[creator_id].append(window_event)
                
                # Compute aggregations for each creator
                for creator_id, creator_events in events_by_creator.items():
                    for agg_spec in self.aggregations:
                        value = AggregationComputer.compute(creator_events, agg_spec)
                        
                        result = AggregationResult(
                            aggregation_name=agg_spec.name,
                            window_start=window_start,
                            window_end=window_end,
                            group_key={"creator_id": creator_id},
                            value=value,
                            count=len(creator_events),
                            timestamp=current_time
                        )
                        results.append(result)
            
            return results
            
        except Exception as e:
            logger.error(f"Error processing creator performance event: {e}")
            return []


class PlatformBusinessAggregator:
    """Aggregator for platform business metrics"""
    
    def __init__(self):
        self.revenue_window = AggregationWindow(WindowSpec(
            window_type=WindowType.TUMBLING,
            size=timedelta(hours=1)
        ))
        
        self.engagement_window = AggregationWindow(WindowSpec(
            window_type=WindowType.SLIDING,
            size=timedelta(minutes=15),
            slide=timedelta(minutes=1)
        ))
        
        self.revenue_aggregations = [
            AggregationSpec("total_revenue", AggregationFunction.SUM, "payload.amount"),
            AggregationSpec("avg_transaction_value", AggregationFunction.AVERAGE, "payload.amount"),
            AggregationSpec("transaction_count", AggregationFunction.COUNT, "event_id"),
            AggregationSpec("unique_creators_earning", AggregationFunction.DISTINCT_COUNT, "payload.creator_id")
        ]
        
        self.engagement_aggregations = [
            AggregationSpec("total_interactions", AggregationFunction.COUNT, "event_id"),
            AggregationSpec("unique_users", AggregationFunction.DISTINCT_COUNT, "payload.user_id"),
            AggregationSpec("avg_engagement_score", AggregationFunction.AVERAGE, "payload.engagement_score"),
            AggregationSpec("high_engagement_count", AggregationFunction.COUNT, "event_id")  # Custom filter needed
        ]
    
    async def process_revenue_event(self, event: Dict[str, Any]) -> List[AggregationResult]:
        """Process revenue event"""
        try:
            event_time = datetime.fromisoformat(event.get("timestamp", datetime.now(timezone.utc).isoformat()))
            self.revenue_window.add_event(event_time, event)
            
            current_time = datetime.now(timezone.utc)
            self.revenue_window.update_watermark(current_time)
            
            results = []
            windows = self.revenue_window.get_active_windows(current_time)
            
            for window_start, window_end in windows:
                window_events = self.revenue_window.get_events_in_window(window_start, window_end)
                
                for agg_spec in self.revenue_aggregations:
                    value = AggregationComputer.compute(window_events, agg_spec)
                    
                    result = AggregationResult(
                        aggregation_name=agg_spec.name,
                        window_start=window_start,
                        window_end=window_end,
                        group_key={},
                        value=value,
                        count=len(window_events),
                        timestamp=current_time
                    )
                    results.append(result)
            
            return results
            
        except Exception as e:
            logger.error(f"Error processing revenue event: {e}")
            return []
    
    async def process_engagement_event(self, event: Dict[str, Any]) -> List[AggregationResult]:
        """Process engagement event"""
        try:
            event_time = datetime.fromisoformat(event.get("timestamp", datetime.now(timezone.utc).isoformat()))
            self.engagement_window.add_event(event_time, event)
            
            current_time = datetime.now(timezone.utc)
            self.engagement_window.update_watermark(current_time)
            
            results = []
            windows = self.engagement_window.get_active_windows(current_time)
            
            for window_start, window_end in windows:
                window_events = self.engagement_window.get_events_in_window(window_start, window_end)
                
                for agg_spec in self.engagement_aggregations:
                    # Apply custom filtering for high engagement
                    filtered_events = window_events
                    if agg_spec.name == "high_engagement_count":
                        filtered_events = [
                            e for e in window_events 
                            if e.get("payload", {}).get("engagement_score", 0) > 0.8
                        ]
                    
                    value = AggregationComputer.compute(filtered_events, agg_spec)
                    
                    result = AggregationResult(
                        aggregation_name=agg_spec.name,
                        window_start=window_start,
                        window_end=window_end,
                        group_key={},
                        value=value,
                        count=len(filtered_events),
                        timestamp=current_time
                    )
                    results.append(result)
            
            return results
            
        except Exception as e:
            logger.error(f"Error processing engagement event: {e}")
            return []


class TrendingDetectionAggregator:
    """Aggregator for detecting trending content and creators"""
    
    def __init__(self):
        self.short_term_window = AggregationWindow(WindowSpec(
            window_type=WindowType.SLIDING,
            size=timedelta(minutes=30),
            slide=timedelta(minutes=5)
        ))
        
        self.long_term_window = AggregationWindow(WindowSpec(
            window_type=WindowType.SLIDING,
            size=timedelta(hours=6),
            slide=timedelta(minutes=30)
        ))
        
        self.trend_threshold = 2.0  # Minimum ratio for trending detection
    
    async def process_event(self, event: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Process event and detect trends"""
        try:
            event_time = datetime.fromisoformat(event.get("timestamp", datetime.now(timezone.utc).isoformat()))
            
            # Add to both windows
            self.short_term_window.add_event(event_time, event)
            self.long_term_window.add_event(event_time, event)
            
            current_time = datetime.now(timezone.utc)
            self.short_term_window.update_watermark(current_time)
            self.long_term_window.update_watermark(current_time)
            
            # Get recent windows
            short_windows = self.short_term_window.get_active_windows(current_time)
            long_windows = self.long_term_window.get_active_windows(current_time)
            
            trending_items = []
            
            # Analyze trending for most recent windows
            if short_windows and long_windows:
                recent_short_window = short_windows[-1]
                recent_long_window = long_windows[-1]
                
                short_events = self.short_term_window.get_events_in_window(*recent_short_window)
                long_events = self.long_term_window.get_events_in_window(*recent_long_window)
                
                # Analyze creator trends
                creator_trends = self._analyze_creator_trends(short_events, long_events)
                trending_items.extend(creator_trends)
                
                # Analyze content trends
                content_trends = self._analyze_content_trends(short_events, long_events)
                trending_items.extend(content_trends)
            
            return trending_items
            
        except Exception as e:
            logger.error(f"Error processing trending detection event: {e}")
            return []
    
    def _analyze_creator_trends(self, short_events: List[Dict[str, Any]], long_events: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Analyze creator trends"""
        try:
            # Count events by creator in both time periods
            short_creator_counts = Counter()
            long_creator_counts = Counter()
            
            for event in short_events:
                creator_id = event.get("payload", {}).get("creator_id")
                if creator_id:
                    short_creator_counts[creator_id] += 1
            
            for event in long_events:
                creator_id = event.get("payload", {}).get("creator_id")
                if creator_id:
                    long_creator_counts[creator_id] += 1
            
            # Calculate trend ratios
            trending_creators = []
            
            for creator_id, short_count in short_creator_counts.items():
                long_count = long_creator_counts.get(creator_id, 1)  # Avoid division by zero
                
                # Normalize by time period
                short_rate = short_count / 0.5  # events per hour in 30-min window
                long_rate = long_count / 6.0   # events per hour in 6-hour window
                
                if long_rate > 0:
                    trend_ratio = short_rate / long_rate
                    
                    if trend_ratio >= self.trend_threshold and short_count >= 5:  # Minimum activity threshold
                        trending_creators.append({
                            "type": "trending_creator",
                            "creator_id": creator_id,
                            "trend_ratio": trend_ratio,
                            "short_term_count": short_count,
                            "long_term_count": long_creator_counts[creator_id],
                            "timestamp": datetime.now(timezone.utc).isoformat()
                        })
            
            # Sort by trend ratio
            trending_creators.sort(key=lambda x: x["trend_ratio"], reverse=True)
            
            return trending_creators[:10]  # Top 10 trending creators
            
        except Exception as e:
            logger.error(f"Error analyzing creator trends: {e}")
            return []
    
    def _analyze_content_trends(self, short_events: List[Dict[str, Any]], long_events: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Analyze content type trends"""
        try:
            # Count events by content type
            short_content_counts = Counter()
            long_content_counts = Counter()
            
            for event in short_events:
                content_type = event.get("payload", {}).get("content_type")
                if content_type:
                    short_content_counts[content_type] += 1
            
            for event in long_events:
                content_type = event.get("payload", {}).get("content_type")
                if content_type:
                    long_content_counts[content_type] += 1
            
            # Calculate trend ratios
            trending_content = []
            
            for content_type, short_count in short_content_counts.items():
                long_count = long_content_counts.get(content_type, 1)
                
                short_rate = short_count / 0.5
                long_rate = long_count / 6.0
                
                if long_rate > 0:
                    trend_ratio = short_rate / long_rate
                    
                    if trend_ratio >= self.trend_threshold and short_count >= 3:
                        trending_content.append({
                            "type": "trending_content_type",
                            "content_type": content_type,
                            "trend_ratio": trend_ratio,
                            "short_term_count": short_count,
                            "long_term_count": long_content_counts[content_type],
                            "timestamp": datetime.now(timezone.utc).isoformat()
                        })
            
            trending_content.sort(key=lambda x: x["trend_ratio"], reverse=True)
            
            return trending_content[:5]  # Top 5 trending content types
            
        except Exception as e:
            logger.error(f"Error analyzing content trends: {e}")
            return []


class AlertManager:
    """Manages alerts based on aggregation results"""
    
    def __init__(self):
        self.alert_rules: List[AlertRule] = []
        self.alert_history: deque = deque(maxlen=1000)
        self.last_alert_times: Dict[str, datetime] = {}
        
    def add_alert_rule(self, rule: AlertRule):
        """Add alert rule"""
        self.alert_rules.append(rule)
        logger.info(f"Added alert rule: {rule.rule_name}")
    
    async def check_alerts(self, results: List[AggregationResult]) -> List[Dict[str, Any]]:
        """Check aggregation results against alert rules"""
        try:
            alerts = []
            current_time = datetime.now(timezone.utc)
            
            for result in results:
                for rule in self.alert_rules:
                    if rule.aggregation_name == result.aggregation_name:
                        if await self._evaluate_alert_condition(rule, result):
                            # Check cooldown
                            last_alert_time = self.last_alert_times.get(rule.rule_name)
                            
                            if (last_alert_time is None or 
                                current_time - last_alert_time >= timedelta(minutes=rule.cooldown_minutes)):
                                
                                alert = {
                                    "rule_name": rule.rule_name,
                                    "severity": rule.severity.value,
                                    "message": rule.message_template.format(
                                        rule_name=rule.rule_name,
                                        value=result.value,
                                        aggregation_name=result.aggregation_name
                                    ),
                                    "aggregation_result": result,
                                    "timestamp": current_time.isoformat()
                                }
                                
                                alerts.append(alert)
                                self.alert_history.append(alert)
                                self.last_alert_times[rule.rule_name] = current_time
                                
                                logger.warning(f"Alert triggered: {alert['message']}")
            
            return alerts
            
        except Exception as e:
            logger.error(f"Error checking alerts: {e}")
            return []
    
    async def _evaluate_alert_condition(self, rule: AlertRule, result: AggregationResult) -> bool:
        """Evaluate alert condition"""
        try:
            # Simple condition evaluation
            # In production, would use a proper expression evaluator
            condition = rule.condition.replace("value", str(result.value))
            
            # Basic condition patterns
            if ">" in condition:
                parts = condition.split(">")
                if len(parts) == 2:
                    left_value = float(parts[0].strip())
                    right_value = float(parts[1].strip())
                    return left_value > right_value
            
            elif "<" in condition:
                parts = condition.split("<")
                if len(parts) == 2:
                    left_value = float(parts[0].strip())
                    right_value = float(parts[1].strip())
                    return left_value < right_value
            
            elif "==" in condition:
                parts = condition.split("==")
                if len(parts) == 2:
                    left_value = parts[0].strip()
                    right_value = parts[1].strip()
                    return left_value == right_value
            
            return False
            
        except Exception as e:
            logger.error(f"Error evaluating alert condition: {e}")
            return False


class StreamingAnalyticsAggregator:
    """Main streaming analytics aggregator for Ainflue platform"""
    
    def __init__(self, metrics_collector=None):
        self.metrics_collector = metrics_collector
        self.creator_aggregator = CreatorPerformanceAggregator()
        self.platform_aggregator = PlatformBusinessAggregator()
        self.trending_aggregator = TrendingDetectionAggregator()
        self.alert_manager = AlertManager()
        self._aggregator_task: Optional[asyncio.Task] = None
        self._shutdown_event = asyncio.Event()
        
        # Setup default alert rules
        self._setup_default_alerts()
    
    async def start(self):
        """Start the streaming analytics aggregator"""
        try:
            logger.info("Starting Streaming Analytics Aggregator")
            
            # Start aggregator monitoring task
            self._aggregator_task = asyncio.create_task(self._aggregator_loop())
            
            logger.info("Streaming Analytics Aggregator started successfully")
            
        except Exception as e:
            logger.error(f"Failed to start streaming analytics aggregator: {e}")
            raise
    
    async def stop(self):
        """Stop the aggregator"""
        try:
            logger.info("Stopping Streaming Analytics Aggregator")
            
            # Signal shutdown
            self._shutdown_event.set()
            
            # Wait for aggregator task
            if self._aggregator_task:
                await self._aggregator_task
            
            logger.info("Streaming Analytics Aggregator stopped successfully")
            
        except Exception as e:
            logger.error(f"Error stopping streaming analytics aggregator: {e}")
            raise
    
    def _setup_default_alerts(self):
        """Setup default alert rules for Ainflue platform"""
        try:
            # High revenue alert
            self.alert_manager.add_alert_rule(AlertRule(
                rule_name="high_hourly_revenue",
                aggregation_name="total_revenue",
                condition="value > 10000",
                severity=AlertSeverity.INFO,
                cooldown_minutes=60,
                message_template="High revenue hour detected: ${value:.2f}"
            ))
            
            # Low engagement alert
            self.alert_manager.add_alert_rule(AlertRule(
                rule_name="low_engagement",
                aggregation_name="total_interactions",
                condition="value < 100",
                severity=AlertSeverity.WARNING,
                cooldown_minutes=30,
                message_template="Low engagement detected: {value} interactions"
            ))
            
            # High creator activity alert
            self.alert_manager.add_alert_rule(AlertRule(
                rule_name="high_creator_uploads",
                aggregation_name="uploads_per_hour",
                condition="value > 50",
                severity=AlertSeverity.INFO,
                cooldown_minutes=60,
                message_template="High creator activity: {value} uploads per hour"
            ))
            
            logger.info("Setup default alert rules")
            
        except Exception as e:
            logger.error(f"Error setting up default alerts: {e}")
    
    async def process_content_event(self, event: Dict[str, Any]) -> Dict[str, Any]:
        """Process content-related event"""
        try:
            start_time = time.time()
            
            # Process with creator aggregator
            creator_results = await self.creator_aggregator.process_event(event)
            
            # Check for trending
            trending_results = await self.trending_aggregator.process_event(event)
            
            # Check alerts
            alerts = await self.alert_manager.check_alerts(creator_results)
            
            processing_time = (time.time() - start_time) * 1000
            
            if self.metrics_collector:
                self.metrics_collector.histogram("analytics_processing_time", processing_time)
                self.metrics_collector.increment_counter("analytics_events_processed")
            
            return {
                "aggregation_results": [
                    {
                        "aggregation_name": r.aggregation_name,
                        "value": r.value,
                        "group_key": r.group_key,
                        "window_start": r.window_start.isoformat(),
                        "window_end": r.window_end.isoformat()
                    }
                    for r in creator_results
                ],
                "trending_results": trending_results,
                "alerts": alerts,
                "processing_time_ms": processing_time
            }
            
        except Exception as e:
            logger.error(f"Error processing content event: {e}")
            if self.metrics_collector:
                self.metrics_collector.increment_counter("analytics_processing_errors")
            return {"error": str(e)}
    
    async def process_revenue_event(self, event: Dict[str, Any]) -> Dict[str, Any]:
        """Process revenue-related event"""
        try:
            start_time = time.time()
            
            # Process with platform aggregator
            revenue_results = await self.platform_aggregator.process_revenue_event(event)
            
            # Check alerts
            alerts = await self.alert_manager.check_alerts(revenue_results)
            
            processing_time = (time.time() - start_time) * 1000
            
            return {
                "aggregation_results": [
                    {
                        "aggregation_name": r.aggregation_name,
                        "value": r.value,
                        "window_start": r.window_start.isoformat(),
                        "window_end": r.window_end.isoformat()
                    }
                    for r in revenue_results
                ],
                "alerts": alerts,
                "processing_time_ms": processing_time
            }
            
        except Exception as e:
            logger.error(f"Error processing revenue event: {e}")
            return {"error": str(e)}
    
    async def process_engagement_event(self, event: Dict[str, Any]) -> Dict[str, Any]:
        """Process engagement-related event"""
        try:
            start_time = time.time()
            
            # Process with platform aggregator
            engagement_results = await self.platform_aggregator.process_engagement_event(event)
            
            # Check alerts
            alerts = await self.alert_manager.check_alerts(engagement_results)
            
            processing_time = (time.time() - start_time) * 1000
            
            return {
                "aggregation_results": [
                    {
                        "aggregation_name": r.aggregation_name,
                        "value": r.value,
                        "window_start": r.window_start.isoformat(),
                        "window_end": r.window_end.isoformat()
                    }
                    for r in engagement_results
                ],
                "alerts": alerts,
                "processing_time_ms": processing_time
            }
            
        except Exception as e:
            logger.error(f"Error processing engagement event: {e}")
            return {"error": str(e)}
    
    async def _aggregator_loop(self):
        """Main aggregator monitoring loop"""
        try:
            while not self._shutdown_event.is_set():
                # Perform periodic maintenance
                await self._perform_maintenance()
                
                # Sleep before next iteration
                await asyncio.sleep(60)  # Check every minute
                
        except Exception as e:
            logger.error(f"Error in aggregator loop: {e}")
    
    async def _perform_maintenance(self):
        """Perform routine maintenance tasks"""
        try:
            # Log system status
            logger.debug("Streaming analytics aggregator health check")
            
            # Could add cleanup of old windows, metrics reporting, etc.
            
        except Exception as e:
            logger.error(f"Error performing maintenance: {e}")
    
    def get_aggregator_metrics(self) -> Dict[str, Any]:
        """Get comprehensive aggregator metrics"""
        try:
            metrics = {
                "alert_rules": len(self.alert_manager.alert_rules),
                "recent_alerts": len(self.alert_manager.alert_history),
                "aggregators": {
                    "creator_performance": "active",
                    "platform_business": "active",
                    "trending_detection": "active"
                }
            }
            
            return metrics
            
        except Exception as e:
            logger.error(f"Error getting aggregator metrics: {e}")
            return {"error": str(e)}


# Export public API
__all__ = [
    "StreamingAnalyticsAggregator", "AggregationSpec", "WindowSpec", "AggregationResult",
    "AlertRule", "CreatorPerformanceAggregator", "PlatformBusinessAggregator",
    "TrendingDetectionAggregator", "AlertManager", "AggregationFunction", "WindowType",
    "AlertSeverity"
]