"""
Ainflue Platform - Enterprise Metrics System
============================================

Advanced enterprise metrics collection, aggregation, and analysis system
for comprehensive monitoring of business KPIs, performance metrics, and
operational insights across the Ainflue platform.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
import time
import uuid
import json
import numpy as np
from typing import Dict, List, Optional, Any, Tuple, Set, Union, Callable
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
from collections import defaultdict, deque
import threading
from concurrent.futures import ThreadPoolExecutor
import statistics
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)

class MetricType(Enum):
    """Types of metrics collected."""
    COUNTER = "counter"
    GAUGE = "gauge"
    HISTOGRAM = "histogram"
    TIMER = "timer"
    RATE = "rate"
    PERCENTAGE = "percentage"
    BUSINESS_KPI = "business_kpi"
    PERFORMANCE_METRIC = "performance_metric"
    USER_BEHAVIOR = "user_behavior"
    FINANCIAL_METRIC = "financial_metric"

class MetricDimension(Enum):
    """Metric dimensionality for categorization."""
    AUDIO_PROCESSING = "audio_processing"
    CONTENT_PROTECTION = "content_protection"
    COLLABORATION = "collaboration"
    MONETIZATION = "monetization"
    GAMIFICATION = "gamification"
    SEO_OPTIMIZATION = "seo_optimization"
    DISTRIBUTION = "distribution"
    ANALYTICS = "analytics"
    USER_ENGAGEMENT = "user_engagement"
    PLATFORM_PERFORMANCE = "platform_performance"
    BUSINESS_INTELLIGENCE = "business_intelligence"

class AggregationMethod(Enum):
    """Methods for metric aggregation."""
    SUM = "sum"
    AVERAGE = "average"
    MEDIAN = "median"
    MIN = "min"
    MAX = "max"
    COUNT = "count"
    PERCENTILE_95 = "percentile_95"
    PERCENTILE_99 = "percentile_99"
    RATE_PER_SECOND = "rate_per_second"
    RATE_PER_MINUTE = "rate_per_minute"

class AlertSeverity(Enum):
    """Alert severity levels."""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"

@dataclass
class MetricValue:
    """Individual metric value."""
    metric_name: str
    value: Union[float, int]
    metric_type: MetricType
    dimension: MetricDimension
    tags: Dict[str, str]
    timestamp: datetime
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class AggregatedMetric:
    """Aggregated metric result."""
    metric_name: str
    aggregated_value: float
    aggregation_method: AggregationMethod
    time_window: Tuple[datetime, datetime]
    sample_count: int
    dimension: MetricDimension
    tags: Dict[str, str]
    confidence_interval: Optional[Tuple[float, float]] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class MetricAlert:
    """Metric alert definition."""
    alert_id: str
    metric_name: str
    condition: str  # e.g., "> 100", "< 0.95", "change > 10%"
    threshold_value: float
    severity: AlertSeverity
    time_window: timedelta
    is_active: bool
    last_triggered: Optional[datetime] = None
    trigger_count: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class BusinessKPI:
    """Business Key Performance Indicator."""
    kpi_id: str
    name: str
    description: str
    target_value: float
    current_value: float
    unit: str
    category: str
    calculation_method: str
    last_updated: datetime
    trend_direction: str  # "up", "down", "stable"
    achievement_percentage: float
    related_metrics: List[str] = field(default_factory=list)

class MetricCollector(ABC):
    """Abstract base class for metric collectors."""
    
    @abstractmethod
    async def collect_metrics(self) -> List[MetricValue]:
        """Collect metrics from specific source."""
        pass

class AinflueMetricsEngine:
    """
    Enterprise metrics engine for comprehensive monitoring and analytics.
    
    Features:
    - Multi-dimensional metric collection
    - Real-time aggregation and analysis
    - Business KPI tracking
    - Intelligent alerting
    - Performance optimization insights
    - Historical trend analysis
    - Predictive analytics
    - Custom dashboard support
    """
    
    def __init__(self, config -> None: Optional[Dict[str, Any]] = None) -> None:
        self.config = config or {}
        self.metric_storage: Dict[str, deque] = defaultdict(lambda: deque(maxlen=10000))
        self.aggregated_metrics: Dict[str, List[AggregatedMetric]] = defaultdict(list)
        self.business_kpis: Dict[str, BusinessKPI] = {}
        self.metric_alerts: Dict[str, MetricAlert] = {}
        self.collectors: List[MetricCollector] = []
        
        # Performance tracking
        self.metrics_collected: int = 0
        self.alerts_triggered: int = 0
        self.aggregations_performed: int = 0
        
        # Threading for background processing
        self.executor = ThreadPoolExecutor(max_workers=4)
        self.collection_interval = self.config.get('collection_interval', 30)  # seconds
        self.is_running = False
        
        logger.info("AinflueMetricsEngine initialized with enterprise features")

    async def record_metric(self, metric -> None: MetricValue) -> None:
        """Record a metric value."""
        try:
            # Store metric
            self.metric_storage[metric.metric_name].append(metric)
            self.metrics_collected += 1
            
            logger.debug(f"Recorded metric: {metric.metric_name} = {metric.value}")
            
        except Exception as e:
            logger.error(f"Error recording metric: {e}")

    async def get_metric_values(
        self,
        metric_name: str,
        time_window: Optional[timedelta] = None,
        tags_filter: Optional[Dict[str, str]] = None
    ) -> List[MetricValue]:
        """Get metric values with optional filtering."""
        try:
            metrics = self.metric_storage.get(metric_name, [])
            
            # Apply time window filter
            if time_window:
                cutoff_time = datetime.now() - time_window
                metrics = [m for m in metrics if m.timestamp >= cutoff_time]
            
            # Apply tags filter
            if tags_filter:
                filtered_metrics = []
                for metric in metrics:
                    if all(metric.tags.get(key) == value for key, value in tags_filter.items()):
                        filtered_metrics.append(metric)
                metrics = filtered_metrics
            
            return list(metrics)
            
        except Exception as e:
            logger.error(f"Error getting metric values: {e}")
            return []

    async def get_engine_metrics(self) -> Dict[str, Any]:
        """Get metrics engine performance metrics."""
        try:
            return {
                'metrics_collected': self.metrics_collected,
                'alerts_triggered': self.alerts_triggered,
                'aggregations_performed': self.aggregations_performed,
                'collectors_count': len(self.collectors),
                'stored_metrics_count': sum(len(metrics) for metrics in self.metric_storage.values()),
                'business_kpis_count': len(self.business_kpis),
                'active_alerts_count': len([a for a in self.metric_alerts.values() if a.is_active]),
                'collection_interval': self.collection_interval,
                'is_running': self.is_running
            }
            
        except Exception as e:
            logger.error(f"Error getting engine metrics: {e}")
            return {'error': str(e)}

# Global metrics engine instance
_metrics_engine = None

def get_metrics_engine(config: Optional[Dict[str, Any]] = None) -> AinflueMetricsEngine:
    """Get the global metrics engine instance."""
    global _metrics_engine
    if _metrics_engine is None:
        _metrics_engine = AinflueMetricsEngine(config)
    return _metrics_engine

# Convenience functions for metric recording
async def record_audio_processing_time(processing_time -> None: float, format_pair -> None: str = "") -> None:
    """Record audio processing time metric."""
    engine = get_metrics_engine()
    metric = MetricValue(
        metric_name="audio_processing_time",
        value=processing_time,
        metric_type=MetricType.TIMER,
        dimension=MetricDimension.AUDIO_PROCESSING,
        tags={"format_pair": format_pair},
        timestamp=datetime.now()
    )
    await engine.record_metric(metric)

async def record_collaboration_success(success -> None: bool, partnership_id -> None: str = "") -> None:
    """Record collaboration success metric."""
    engine = get_metrics_engine()
    metric = MetricValue(
        metric_name="collaboration_success",
        value=1.0 if success else 0.0,
        metric_type=MetricType.COUNTER,
        dimension=MetricDimension.COLLABORATION,
        tags={"partnership_id": partnership_id},
        timestamp=datetime.now()
    )
    await engine.record_metric(metric)

async def record_payment_transaction(amount -> None: float, success -> None: bool, gateway -> None: str = "") -> None:
    """Record payment transaction metric."""
    engine = get_metrics_engine()
    
    # Record transaction amount
    amount_metric = MetricValue(
        metric_name="payment_transaction_amount",
        value=amount,
        metric_type=MetricType.GAUGE,
        dimension=MetricDimension.MONETIZATION,
        tags={"gateway": gateway},
        timestamp=datetime.now()
    )
    await engine.record_metric(amount_metric)
    
    # Record success/failure
    success_metric = MetricValue(
        metric_name="payment_transaction_success",
        value=1.0 if success else 0.0,
        metric_type=MetricType.COUNTER,
        dimension=MetricDimension.MONETIZATION,
        tags={"gateway": gateway},
        timestamp=datetime.now()
    )
    await engine.record_metric(success_metric)

async def record_api_response_time(endpoint -> None: str, response_time_ms -> None: float) -> None:
    """Record API response time metric."""
    engine = get_metrics_engine()
    metric = MetricValue(
        metric_name="api_response_time",
        value=response_time_ms,
        metric_type=MetricType.TIMER,
        dimension=MetricDimension.PLATFORM_PERFORMANCE,
        tags={"endpoint": endpoint},
        timestamp=datetime.now()
    )
    await engine.record_metric(metric)

__all__ = [
    'AinflueMetricsEngine',
    'MetricType',
    'MetricDimension',
    'AggregationMethod',
    'AlertSeverity',
    'MetricValue',
    'AggregatedMetric',
    'MetricAlert',
    'BusinessKPI',
    'MetricCollector',
    'get_metrics_engine',
    'record_audio_processing_time',
    'record_collaboration_success',
    'record_payment_transaction',
    'record_api_response_time'
]