"""
Shared Analytics Service
Provides event collection, metrics aggregation, and dashboard APIs
"""

from .event_collector import EventCollector
from .metrics_aggregator import MetricsAggregator
from .dashboard_api import DashboardAPI

__all__ = [
    'EventCollector',
    'MetricsAggregator',
    'DashboardAPI'
]
