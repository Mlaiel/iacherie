#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Performance Monitor Utility
===========================

Performance monitoring and metrics collection utility for the IA Influencer Agent system.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.
"""
import time
import logging
import threading
from typing import Dict, Any, Optional, List, Callable
from contextlib import contextmanager
from dataclasses import dataclass, field
from collections import defaultdict, deque
import asyncio
import functools

logger = logging.getLogger(__name__)

@dataclass
class PerformanceMetric:
    """Performance metric data structure"""    name: str
    value: float
    timestamp: float
    tags: Dict[str, str] = field(default_factory=dict)
    unit: str = "ms"

class PerformanceMonitor:
    """    Performance monitoring utility with metrics collection and analysis.
    
    Provides timing decorators, context managers, and performance tracking
    for system components.
    """    
    def __init__(self, name: str = "default"):
        """Initialize performance monitor"""        self.name = name
        self.metrics: Dict[str, deque] = defaultdict(lambda: deque(maxlen=1000))
        self.active_timers: Dict[str, float] = {}
        self.lock = threading.Lock()
        self.enabled = True
    
    def enable(self):
        """Enable performance monitoring"""        self.enabled = True
    
    def disable(self):
        """Disable performance monitoring"""        self.enabled = False
    
    @contextmanager
    def timer(self, operation_name: str, tags: Optional[Dict[str, str]] = None):
        """Context manager for timing operations"""        if not self.enabled:
            yield
            return
        
        tags = tags or {}
        start_time = time.time()
        
        try:
            yield
        finally:
            end_time = time.time()
            duration = (end_time - start_time) * 1000  # Convert to milliseconds
            self.record_metric(operation_name, duration, tags)
    
    def record_metric(self, name: str, value: float, tags: Optional[Dict[str, str]] = None, unit: str = "ms"):
        """Record a performance metric"""        if not self.enabled:
            return
        
        tags = tags or {}
        metric = PerformanceMetric(
            name=name,
            value=value,
            timestamp=time.time(),
            tags=tags,
            unit=unit
        )
        
        with self.lock:
            self.metrics[name].append(metric)
    
    def start_timer(self, operation_name: str) -> str:
        """Start a named timer"""        if not self.enabled:
            return operation_name
        
        timer_id = f"{operation_name}_{time.time()}"
        self.active_timers[timer_id] = time.time()
        return timer_id
    
    def stop_timer(self, timer_id: str, tags: Optional[Dict[str, str]] = None) -> float:
        """Stop a named timer and record metric"""        if not self.enabled or timer_id not in self.active_timers:
            return 0.0
        
        start_time = self.active_timers.pop(timer_id)
        duration = (time.time() - start_time) * 1000
        
        # Extract operation name from timer_id
        operation_name = "_".join(timer_id.split("_")[:-1])
        self.record_metric(operation_name, duration, tags)
        
        return duration
    
    def timing_decorator(self, operation_name: Optional[str] = None, tags: Optional[Dict[str, str]] = None):
        """Decorator for timing function execution"""        def decorator(func):
            name = operation_name or f"{func.__module__}.{func.__name__}"
            
            if asyncio.iscoroutinefunction(func):
                @functools.wraps(func)
                async def async_wrapper(*args, **kwargs):
                    if not self.enabled:
                        return await func(*args, **kwargs)
                    
                    start_time = time.time()
                    try:
                        result = await func(*args, **kwargs)
                        return result
                    finally:
                        duration = (time.time() - start_time) * 1000
                        self.record_metric(name, duration, tags)
                
                return async_wrapper
            else:
                @functools.wraps(func)
                def sync_wrapper(*args, **kwargs):
                    if not self.enabled:
                        return func(*args, **kwargs)
                    
                    start_time = time.time()
                    try:
                        result = func(*args, **kwargs)
                        return result
                    finally:
                        duration = (time.time() - start_time) * 1000
                        self.record_metric(name, duration, tags)
                
                return sync_wrapper
        
        return decorator
    
    def get_metrics(self, metric_name: Optional[str] = None) -> Dict[str, List[PerformanceMetric]]:
        """Get collected metrics"""        with self.lock:
            if metric_name:
                return {metric_name: list(self.metrics.get(metric_name, []))}
            else:
                return {name: list(metrics) for name, metrics in self.metrics.items()}
    
    def get_stats(self, metric_name: str) -> Dict[str, float]:
        """Get statistics for a specific metric"""        with self.lock:
            metrics = list(self.metrics.get(metric_name, []))
        
        if not metrics:
            return {}
        
        values = [m.value for m in metrics]
        
        stats = {
            'count': len(values),
            'min': min(values),
            'max': max(values),
            'avg': sum(values) / len(values),
            'total': sum(values)
        }
        
        # Calculate percentiles
        sorted_values = sorted(values)
        n = len(sorted_values)
        
        if n > 0:
            stats['p50'] = sorted_values[int(n * 0.5)]
            stats['p90'] = sorted_values[int(n * 0.9)]
            stats['p95'] = sorted_values[int(n * 0.95)]
            stats['p99'] = sorted_values[int(n * 0.99)]
        
        return stats
    
    def get_summary(self) -> Dict[str, Any]:
        """Get performance summary for all metrics"""        summary = {
            'monitor_name': self.name,
            'enabled': self.enabled,
            'total_metrics': sum(len(metrics) for metrics in self.metrics.values()),
            'metric_types': len(self.metrics),
            'active_timers': len(self.active_timers),
            'metrics': {}
        }
        
        for metric_name in self.metrics.keys():
            summary['metrics'][metric_name] = self.get_stats(metric_name)
        
        return summary
    
    def clear_metrics(self, metric_name: Optional[str] = None):
        """Clear collected metrics"""        with self.lock:
            if metric_name:
                self.metrics.pop(metric_name, None)
            else:
                self.metrics.clear()
    
    def reset(self):
        """Reset all performance data"""        with self.lock:
            self.metrics.clear()
            self.active_timers.clear()

# Global performance monitor instance
default_monitor = PerformanceMonitor("global")

# Convenience functions using global monitor
def timer(operation_name: str, tags: Optional[Dict[str, str]] = None):
    """Global timer context manager"""    return default_monitor.timer(operation_name, tags)

def timing_decorator(operation_name: Optional[str] = None, tags: Optional[Dict[str, str]] = None):
    """Global timing decorator"""    return default_monitor.timing_decorator(operation_name, tags)

def record_metric(name: str, value: float, tags: Optional[Dict[str, str]] = None, unit: str = "ms"):
    """Record metric using global monitor"""    default_monitor.record_metric(name, value, tags, unit)

def get_performance_summary() -> Dict[str, Any]:
    """Get global performance summary"""    return default_monitor.get_summary()
