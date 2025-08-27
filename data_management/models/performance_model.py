"""
Performance Models - IA Influencer Agent Platform Enterprise
© 2025 Fahed Mlaiel. All Rights Reserved.

Advanced performance models for system monitoring and optimization.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
from enum import Enum
from dataclasses import dataclass
from decimal import Decimal

class PerformanceMetricType(str, Enum):
    """Performance metric types."""
    RESPONSE_TIME = "response_time"
    THROUGHPUT = "throughput"
    ERROR_RATE = "error_rate"
    CPU_USAGE = "cpu_usage"
    MEMORY_USAGE = "memory_usage"
    CACHE_HIT_RATE = "cache_hit_rate"

@dataclass
class PerformanceMetricModel:
    """System performance metric model."""
    metric_id: str
    service_name: str
    metric_type: PerformanceMetricType
    value: Decimal
    timestamp: datetime
    metadata: Dict[str, Any]

@dataclass
class SystemHealthModel:
    """System health status model."""
    health_id: str
    service_name: str
    status: str
    uptime: int
    last_check: datetime
    metrics: Dict[str, Decimal]
