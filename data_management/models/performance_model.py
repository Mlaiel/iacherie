"""Performance Models - IA Influencer Agent Platform Enterprise
(c) 2025 Fahed Mlaiel. All Rights Reserved.

Advanced performance models for system monitoring and optimization.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
from enum import Enum
from dataclasses import dataclass
from decimal import Decimal

class PerformanceMetricType(str, Enum):
    """
Performance metric types."""

    RESPONSE_TIME = "response_time"
    THROUGHPUT = "throughput"
    ERROR_RATE = "error_rate"
    CPU_USAGE = "cpu_usage"
    MEMORY_USAGE = "memory_usage"
    CACHE_HIT_RATE = "cache_hit_rate"

# For backwards compatibility, alias to expected name
@dataclass
class PerformanceMetric:
    """System performance metric model."""
    metric_id: str
    service_name: str
    metric_type: PerformanceMetricType
    value: Decimal
    timestamp: datetime
    metadata: Dict[str, Any]

# Additional models for the performance system
@dataclass
class MetricType:
    """
Metric type definition."""
    type_id: str
    name: str
    unit: str
    description: str
    
@dataclass
class PerformanceTrend:
    """
Performance trend analysis."""
    trend_id: str
    metric_type: str
    direction: str  # "up", "down", "stable"
    percentage_change: Decimal
    period_start: datetime
    period_end: datetime
    
@dataclass
class PerformanceAlert:
    """Performance alert definition."""
    alert_id: str
    metric_type: str
    threshold: Decimal
    comparison_operator: str  # ">", "<", ">=", "<=", "=="
    severity: str  # "low", "medium", "high", "critical"
    
@dataclass
class BenchmarkComparison:
    """Benchmark comparison data."""
    comparison_id: str
    current_value: Decimal
    baseline_value: Decimal
    improvement_percentage: Decimal
    metric_type: str
    comparison_date: datetime
    
@dataclass
class PerformanceReport:
    """
Performance report structure."""
    report_id: str
    report_type: str
    generated_at: datetime
    metrics: List[PerformanceMetric]
    trends: List[PerformanceTrend]
    alerts: List[PerformanceAlert]
    summary: Dict[str, Any]
    
@dataclass
class OptimizationRecommendation:
    """
Performance optimization recommendation."""
    recommendation_id: str
    category: str
    title: str
    description: str
    impact_level: str  # "low", "medium", "high"
    effort_level: str  # "low", "medium", "high"
    estimated_improvement: Decimal
    implementation_steps: List[str]

# Keep the original name as well for compatibility
PerformanceMetricModel = PerformanceMetric

@dataclass
class SystemHealthModel:
    """System health status model."""
    health_id: str
    service_name: str
    status: str
    uptime: int
    last_check: datetime
    metrics: Dict[str, Decimal]
