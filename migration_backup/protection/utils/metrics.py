#!/usr/bin/env python3
"""
📊 Protection Metrics Module
============================

Metrics collection utilities for the protection system.

Author: Fahed Mlaiel (mlaiel@live.de)
Protection Metrics Module
"""

from typing import Dict, Any, Optional
from datetime import datetime
import time

class ProtectionMetrics:
    """Protection system metrics collector."""
    
    def __init__(self):
        """Initialize metrics collector."""
        self._metrics = {}
        self._start_time = time.time()
    
    def increment(self, metric_name: str, value: int = 1) -> None:
        """Increment a counter metric."""
        if metric_name not in self._metrics:
            self._metrics[metric_name] = 0
        self._metrics[metric_name] += value
    
    def gauge(self, metric_name: str, value: float) -> None:
        """Set a gauge metric."""
        self._metrics[metric_name] = value
    
    def timer(self, metric_name: str, duration: float) -> None:
        """Record a timer metric."""
        if f"{metric_name}_times" not in self._metrics:
            self._metrics[f"{metric_name}_times"] = []
        self._metrics[f"{metric_name}_times"].append(duration)
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get all collected metrics."""
        return self._metrics.copy()
    
    def get_uptime(self) -> float:
        """Get system uptime in seconds."""
        return time.time() - self._start_time
    
    def reset(self) -> None:
        """Reset all metrics."""
        self._metrics.clear()
        self._start_time = time.time()

# Global metrics instance
metrics = ProtectionMetrics()

def get_metrics() -> ProtectionMetrics:
    """Get the global metrics instance."""
    return metrics

# Alias for backward compatibility
MetricsCollector = ProtectionMetrics