"""
Cache Analytics - Advanced Cache Performance Analysis

Comprehensive analytics system providing deep insights into cache performance,
usage patterns, optimization opportunities, and business impact metrics.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
import time
import statistics
from collections import defaultdict, Counter
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from enum import Enum
import json
import uuid

logger = logging.getLogger(__name__)

class MetricType(Enum):
    """Types of cache metrics"""
    HIT_RATE = "hit_rate"
    MISS_RATE = "miss_rate"
    RESPONSE_TIME = "response_time"
    THROUGHPUT = "throughput"
    MEMORY_USAGE = "memory_usage"
    EVICTION_RATE = "eviction_rate"
    ERROR_RATE = "error_rate"
    COST_SAVINGS = "cost_savings"

class AnalyticsPeriod(Enum):
    """Time periods for analytics aggregation"""
    MINUTE = "minute"
    HOUR = "hour" 
    DAY = "day"
    WEEK = "week"
    MONTH = "month"

@dataclass
class CacheMetric:
    """Individual cache metric data point"""
    metric_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    metric_type: MetricType = MetricType.HIT_RATE
    value: float = 0.0
    timestamp: datetime = field(default_factory=datetime.utcnow)
    tags: Dict[str, str] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class PerformanceReport:
    """Comprehensive performance analysis report"""
    report_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    period_start: datetime = field(default_factory=datetime.utcnow)
    period_end: datetime = field(default_factory=datetime.utcnow)
    
    # Core metrics
    overall_hit_rate: float = 0.0
    total_requests: int = 0
    total_hits: int = 0
    total_misses: int = 0
    
    # Performance metrics
    average_response_time: float = 0.0
    p95_response_time: float = 0.0
    p99_response_time: float = 0.0
    peak_throughput: float = 0.0
    
    # Resource metrics
    memory_usage_stats: Dict[str, float] = field(default_factory=dict)
    storage_efficiency: float = 0.0
    compression_ratio: float = 0.0
    
    # Patterns and insights
    top_accessed_keys: List[Tuple[str, int]] = field(default_factory=list)
    access_patterns_by_hour: List[int] = field(default_factory=lambda: [0] * 24)
    geographic_distribution: Dict[str, int] = field(default_factory=dict)
    user_behavior_insights: Dict[str, Any] = field(default_factory=dict)
    
    # Optimization recommendations
    optimization_opportunities: List[Dict[str, Any]] = field(default_factory=list)
    cost_savings_estimate: float = 0.0
    
    # Trends and forecasts
    trend_analysis: Dict[str, Any] = field(default_factory=dict)
    capacity_forecast: Dict[str, Any] = field(default_factory=dict)

@dataclass 
class AlertRule:
    """Cache performance alert rule"""
    rule_id: str
    name: str
    metric_type: MetricType
    threshold: float
    comparison: str  # "greater_than", "less_than", "equals"
    enabled: bool = True
    alert_frequency: int = 300  # seconds
    last_triggered: Optional[datetime] = None

class CacheAnalytics:
    """
    Advanced cache analytics engine providing comprehensive insights
    into cache performance, usage patterns, and optimization opportunities.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        
        # Metrics storage
        self.metrics_history: Dict[MetricType, List[CacheMetric]] = defaultdict(list)
        self.real_time_metrics: Dict[str, Any] = {}
        
        # Access pattern tracking
        self.access_patterns: Dict[str, Any] = defaultdict(dict)
        self.geographic_data: Dict[str, Counter] = defaultdict(Counter)
        self.temporal_patterns: Dict[int, int] = defaultdict(int)  # hour -> count
        
        # Performance tracking
        self.response_times: List[float] = []
        self.throughput_samples: List[Tuple[datetime, int]] = []
        self.error_log: List[Dict[str, Any]] = []
        
        # Alert system
        self.alert_rules: Dict[str, AlertRule] = {}
        self.active_alerts: List[Dict[str, Any]] = []
        
        # Analytics state
        self.last_report_time = datetime.utcnow()
        self.collection_enabled = True
        
    async def initialize(self):
        """Initialize analytics engine"""
        # Start background tasks
        asyncio.create_task(self._metrics_collection_loop())
        asyncio.create_task(self._alert_monitoring_loop())
        asyncio.create_task(self._cleanup_old_metrics())
        
        logger.info("CacheAnalytics initialized")
    
    async def record_cache_hit(
        self,
        key: str,
        response_time: float,
        user_id: Optional[str] = None,
        location: Optional[str] = None,
        content_type: Optional[str] = None
    ):
        """Record cache hit with contextual information"""
        if not self.collection_enabled:
            return
        
        # Record basic metrics
        self.real_time_metrics['total_hits'] = self.real_time_metrics.get('total_hits', 0) + 1
        self.real_time_metrics['total_requests'] = self.real_time_metrics.get('total_requests', 0) + 1
        
        # Record response time
        self.response_times.append(response_time)
        if len(self.response_times) > 10000:
            self.response_times = self.response_times[-5000:]  # Keep recent data
        
        # Update access patterns
        await self._update_access_pattern(key, user_id, location, content_type, hit=True)
        
        # Record geographic data
        if location:
            self.geographic_data[location]['hits'] += 1
        
        # Record temporal pattern
        hour = datetime.utcnow().hour
        self.temporal_patterns[hour] += 1
    
    async def record_cache_miss(
        self,
        key: str,
        response_time: float,
        user_id: Optional[str] = None,
        location: Optional[str] = None,
        content_type: Optional[str] = None
    ):
        """Record cache miss with analysis"""
        if not self.collection_enabled:
            return
        
        # Record basic metrics
        self.real_time_metrics['total_misses'] = self.real_time_metrics.get('total_misses', 0) + 1
        self.real_time_metrics['total_requests'] = self.real_time_metrics.get('total_requests', 0) + 1
        
        # Record response time (typically higher for misses)
        self.response_times.append(response_time)
        
        # Update access patterns
        await self._update_access_pattern(key, user_id, location, content_type, hit=False)
        
        # Record geographic data
        if location:
            self.geographic_data[location]['misses'] += 1
        
        # Analyze miss reasons
        await self._analyze_cache_miss(key, content_type)
    
    async def record_operation(self, entry: Any, operation: str):
        """Record cache operation for detailed analysis"""
        if not self.collection_enabled:
            return
        
        operation_data = {
            'key': entry.key,
            'operation': operation,
            'timestamp': datetime.utcnow(),
            'size_bytes': getattr(entry, 'size_bytes', 0),
            'ttl': getattr(entry, 'ttl', None),
            'priority': getattr(entry, 'priority', None)
        }
        
        # Store operation for pattern analysis
        if operation not in self.access_patterns:
            self.access_patterns[operation] = []
        
        self.access_patterns[operation].append(operation_data)
        
        # Keep recent operations only
        if len(self.access_patterns[operation]) > 1000:
            self.access_patterns[operation] = self.access_patterns[operation][-500:]
    
    async def record_miss(self, key: str):
        """Record cache miss for analytics"""
        miss_data = {
            'key': key,
            'timestamp': datetime.utcnow(),
            'reason': await self._determine_miss_reason(key)
        }
        
        if 'misses' not in self.access_patterns:
            self.access_patterns['misses'] = []
        
        self.access_patterns['misses'].append(miss_data)
    
    async def record_eviction(
        self,
        key: str,
        reason: str,
        size_bytes: int = 0
    ):
        """Record cache eviction event"""
        eviction_data = {
            'key': key,
            'reason': reason,
            'size_bytes': size_bytes,
            'timestamp': datetime.utcnow()
        }
        
        if 'evictions' not in self.access_patterns:
            self.access_patterns['evictions'] = []
        
        self.access_patterns['evictions'].append(eviction_data)
        
        # Update eviction metrics
        self.real_time_metrics['total_evictions'] = self.real_time_metrics.get('total_evictions', 0) + 1
    
    async def record_error(
        self,
        operation: str,
        error_type: str,
        error_message: str,
        key: Optional[str] = None
    ):
        """Record cache operation error"""
        error_data = {
            'operation': operation,
            'error_type': error_type,
            'error_message': error_message,
            'key': key,
            'timestamp': datetime.utcnow()
        }
        
        self.error_log.append(error_data)
        
        # Keep error log size manageable
        if len(self.error_log) > 1000:
            self.error_log = self.error_log[-500:]
        
        self.real_time_metrics['total_errors'] = self.real_time_metrics.get('total_errors', 0) + 1
    
    def add_alert_rule(self, rule: AlertRule):
        """Add performance alert rule"""
        self.alert_rules[rule.rule_id] = rule
        logger.info(f"Added cache alert rule: {rule.name}")
    
    def remove_alert_rule(self, rule_id: str):
        """Remove alert rule"""
        if rule_id in self.alert_rules:
            del self.alert_rules[rule_id]
            logger.info(f"Removed cache alert rule: {rule_id}")
    
    async def generate_performance_report(
        self,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None
    ) -> PerformanceReport:
        """Generate comprehensive performance analysis report"""
        if not start_time:
            start_time = datetime.utcnow() - timedelta(hours=24)
        if not end_time:
            end_time = datetime.utcnow()
        
        report = PerformanceReport(
            period_start=start_time,
            period_end=end_time
        )
        
        # Calculate core metrics
        total_requests = self.real_time_metrics.get('total_requests', 0)
        total_hits = self.real_time_metrics.get('total_hits', 0)
        total_misses = self.real_time_metrics.get('total_misses', 0)
        
        report.total_requests = total_requests
        report.total_hits = total_hits
        report.total_misses = total_misses
        
        if total_requests > 0:
            report.overall_hit_rate = total_hits / total_requests
        
        # Calculate performance metrics
        if self.response_times:
            report.average_response_time = statistics.mean(self.response_times)
            sorted_times = sorted(self.response_times)
            
            if len(sorted_times) >= 20:  # Sufficient data for percentiles
                p95_index = int(0.95 * len(sorted_times))
                p99_index = int(0.99 * len(sorted_times))
                report.p95_response_time = sorted_times[p95_index]
                report.p99_response_time = sorted_times[p99_index]
        
        # Analyze access patterns
        report.access_patterns_by_hour = [self.temporal_patterns.get(hour, 0) for hour in range(24)]
        
        # Geographic distribution
        for location, counters in self.geographic_data.items():
            total_location_requests = counters['hits'] + counters['misses']
            report.geographic_distribution[location] = total_location_requests
        
        # Top accessed keys
        if 'set' in self.access_patterns:
            key_access_counts = Counter()
            for operation in self.access_patterns['set']:
                key_access_counts[operation['key']] += 1
            
            report.top_accessed_keys = key_access_counts.most_common(10)
        
        # Generate optimization recommendations
        report.optimization_opportunities = await self._generate_optimization_recommendations()
        
        # Calculate cost savings estimate
        report.cost_savings_estimate = await self._calculate_cost_savings(report)
        
        # Trend analysis
        report.trend_analysis = await self._analyze_trends()
        
        # Capacity forecast
        report.capacity_forecast = await self._forecast_capacity_needs()
        
        return report
    
    async def get_real_time_metrics(self) -> Dict[str, Any]:
        """Get current real-time metrics"""
        metrics = self.real_time_metrics.copy()
        
        # Calculate derived metrics
        total_requests = metrics.get('total_requests', 0)
        total_hits = metrics.get('total_hits', 0)
        
        if total_requests > 0:
            metrics['hit_rate'] = total_hits / total_requests
            metrics['miss_rate'] = 1 - metrics['hit_rate']
        
        if self.response_times:
            metrics['average_response_time'] = statistics.mean(self.response_times[-100:])  # Recent average
        
        # Current throughput (requests per second)
        current_time = datetime.utcnow()
        recent_samples = [
            count for timestamp, count in self.throughput_samples
            if (current_time - timestamp).seconds < 60
        ]
        
        if recent_samples:
            metrics['current_throughput'] = sum(recent_samples) / len(recent_samples)
        
        metrics['active_alerts'] = len(self.active_alerts)
        metrics['error_rate'] = metrics.get('total_errors', 0) / max(total_requests, 1)
        
        return metrics
    
    async def get_top_keys_by_metric(
        self,
        metric: str,
        limit: int = 10,
        time_range_hours: int = 24
    ) -> List[Tuple[str, float]]:
        """Get top cache keys by specific metric"""
        cutoff_time = datetime.utcnow() - timedelta(hours=time_range_hours)
        
        if metric == "access_count":
            key_counts = Counter()
            
            for operations in self.access_patterns.values():
                if isinstance(operations, list):
                    for op in operations:
                        if op.get('timestamp', datetime.min) > cutoff_time:
                            key_counts[op['key']] += 1
            
            return key_counts.most_common(limit)
        
        elif metric == "miss_rate":
            key_stats = defaultdict(lambda: {'hits': 0, 'misses': 0})
            
            # This would need more detailed tracking implementation
            # For now, return empty list
            return []
        
        return []
    
    # Private helper methods
    
    async def _update_access_pattern(
        self,
        key: str,
        user_id: Optional[str],
        location: Optional[str],
        content_type: Optional[str],
        hit: bool
    ):
        """Update detailed access pattern analysis"""
        pattern_key = f"access_pattern_{key}"
        
        if pattern_key not in self.access_patterns:
            self.access_patterns[pattern_key] = {
                'key': key,
                'total_accesses': 0,
                'hits': 0,
                'misses': 0,
                'unique_users': set(),
                'locations': set(),
                'content_types': set(),
                'access_times': []
            }
        
        pattern = self.access_patterns[pattern_key]
        pattern['total_accesses'] += 1
        
        if hit:
            pattern['hits'] += 1
        else:
            pattern['misses'] += 1
        
        if user_id:
            pattern['unique_users'].add(user_id)
        
        if location:
            pattern['locations'].add(location)
        
        if content_type:
            pattern['content_types'].add(content_type)
        
        pattern['access_times'].append(datetime.utcnow())
        
        # Keep only recent access times
        if len(pattern['access_times']) > 100:
            pattern['access_times'] = pattern['access_times'][-50:]
    
    async def _analyze_cache_miss(self, key: str, content_type: Optional[str]):
        """Analyze cache miss for insights"""
        miss_analysis = {
            'key': key,
            'content_type': content_type,
            'timestamp': datetime.utcnow(),
            'potential_reasons': []
        }
        
        # Analyze potential miss reasons
        if content_type and 'real_time' in content_type:
            miss_analysis['potential_reasons'].append('real_time_data')
        
        if len(key) > 100:  # Very long keys might indicate complex queries
            miss_analysis['potential_reasons'].append('complex_key')
        
        # Store analysis results
        if 'miss_analysis' not in self.access_patterns:
            self.access_patterns['miss_analysis'] = []
        
        self.access_patterns['miss_analysis'].append(miss_analysis)
    
    async def _determine_miss_reason(self, key: str) -> str:
        """Determine likely reason for cache miss"""
        # Simple heuristic-based analysis
        if 'temp' in key.lower():
            return 'temporary_data'
        elif 'user_' in key.lower():
            return 'user_specific_data'
        elif 'session' in key.lower():
            return 'session_expired'
        else:
            return 'not_cached'
    
    async def _generate_optimization_recommendations(self) -> List[Dict[str, Any]]:
        """Generate cache optimization recommendations"""
        recommendations = []
        
        # Analyze hit rate
        total_requests = self.real_time_metrics.get('total_requests', 0)
        total_hits = self.real_time_metrics.get('total_hits', 0)
        
        if total_requests > 100:  # Sufficient data
            hit_rate = total_hits / total_requests
            
            if hit_rate < 0.7:
                recommendations.append({
                    'type': 'hit_rate_improvement',
                    'priority': 'high',
                    'description': f'Hit rate is {hit_rate:.2%}, consider increasing cache size or TTL',
                    'potential_impact': 'high'
                })
        
        # Analyze response times
        if self.response_times and len(self.response_times) > 50:
            avg_time = statistics.mean(self.response_times)
            
            if avg_time > 0.1:  # > 100ms
                recommendations.append({
                    'type': 'response_time_optimization',
                    'priority': 'medium',
                    'description': f'Average response time is {avg_time:.3f}s, consider cache warming',
                    'potential_impact': 'medium'
                })
        
        # Analyze eviction patterns
        total_evictions = self.real_time_metrics.get('total_evictions', 0)
        if total_evictions > total_requests * 0.1:  # High eviction rate
            recommendations.append({
                'type': 'memory_optimization',
                'priority': 'high',
                'description': 'High eviction rate detected, consider increasing cache memory',
                'potential_impact': 'high'
            })
        
        return recommendations
    
    async def _calculate_cost_savings(self, report: PerformanceReport) -> float:
        """Calculate estimated cost savings from caching"""
        # Simplified calculation based on avoided database/API calls
        saved_requests = report.total_hits
        estimated_cost_per_request = 0.001  # $0.001 per request
        
        return saved_requests * estimated_cost_per_request
    
    async def _analyze_trends(self) -> Dict[str, Any]:
        """Analyze performance trends"""
        trends = {
            'hit_rate_trend': 'stable',
            'response_time_trend': 'stable',
            'throughput_trend': 'stable'
        }
        
        # This would implement more sophisticated trend analysis
        # using historical data and statistical methods
        
        return trends
    
    async def _forecast_capacity_needs(self) -> Dict[str, Any]:
        """Forecast future capacity requirements"""
        forecast = {
            'projected_memory_usage': 'stable',
            'projected_request_volume': 'increasing',
            'recommended_scaling_actions': []
        }
        
        # This would implement capacity forecasting based on
        # historical trends and growth patterns
        
        return forecast
    
    async def _metrics_collection_loop(self):
        """Background task for periodic metrics collection"""
        while self.collection_enabled:
            try:
                current_time = datetime.utcnow()
                
                # Record throughput sample
                total_requests = self.real_time_metrics.get('total_requests', 0)
                self.throughput_samples.append((current_time, total_requests))
                
                # Keep only recent samples
                cutoff_time = current_time - timedelta(minutes=10)
                self.throughput_samples = [
                    (ts, count) for ts, count in self.throughput_samples
                    if ts > cutoff_time
                ]
                
                await asyncio.sleep(60)  # Collect every minute
                
            except Exception as e:
                logger.error(f"Metrics collection error: {e}")
                await asyncio.sleep(60)
    
    async def _alert_monitoring_loop(self):
        """Background task for alert monitoring"""
        while self.collection_enabled:
            try:
                current_metrics = await self.get_real_time_metrics()
                
                for rule_id, rule in self.alert_rules.items():
                    if not rule.enabled:
                        continue
                    
                    # Check if enough time has passed since last alert
                    if (rule.last_triggered and 
                        (datetime.utcnow() - rule.last_triggered).seconds < rule.alert_frequency):
                        continue
                    
                    # Check threshold
                    metric_value = current_metrics.get(rule.metric_type.value, 0)
                    threshold_met = False
                    
                    if rule.comparison == "greater_than" and metric_value > rule.threshold:
                        threshold_met = True
                    elif rule.comparison == "less_than" and metric_value < rule.threshold:
                        threshold_met = True
                    elif rule.comparison == "equals" and abs(metric_value - rule.threshold) < 0.001:
                        threshold_met = True
                    
                    if threshold_met:
                        await self._trigger_alert(rule, metric_value)
                
                await asyncio.sleep(30)  # Check every 30 seconds
                
            except Exception as e:
                logger.error(f"Alert monitoring error: {e}")
                await asyncio.sleep(30)
    
    async def _trigger_alert(self, rule: AlertRule, current_value: float):
        """Trigger performance alert"""
        alert = {
            'alert_id': str(uuid.uuid4()),
            'rule_id': rule.rule_id,
            'rule_name': rule.name,
            'metric_type': rule.metric_type.value,
            'threshold': rule.threshold,
            'current_value': current_value,
            'timestamp': datetime.utcnow(),
            'severity': 'high' if abs(current_value - rule.threshold) > rule.threshold * 0.5 else 'medium'
        }
        
        self.active_alerts.append(alert)
        rule.last_triggered = datetime.utcnow()
        
        logger.warning(f"Cache alert triggered: {rule.name} - {rule.metric_type.value} = {current_value}")
    
    async def _cleanup_old_metrics(self):
        """Cleanup old metrics to prevent memory buildup"""
        while self.collection_enabled:
            try:
                cutoff_time = datetime.utcnow() - timedelta(days=7)
                
                # Clean up old access patterns
                for pattern_key in list(self.access_patterns.keys()):
                    pattern = self.access_patterns[pattern_key]
                    
                    if isinstance(pattern, list):
                        # Filter out old entries
                        self.access_patterns[pattern_key] = [
                            item for item in pattern
                            if item.get('timestamp', datetime.min) > cutoff_time
                        ]
                        
                        # Remove empty patterns
                        if not self.access_patterns[pattern_key]:
                            del self.access_patterns[pattern_key]
                
                # Clean up old alerts
                self.active_alerts = [
                    alert for alert in self.active_alerts
                    if alert['timestamp'] > cutoff_time
                ]
                
                await asyncio.sleep(3600)  # Cleanup every hour
                
            except Exception as e:
                logger.error(f"Metrics cleanup error: {e}")
                await asyncio.sleep(3600)
