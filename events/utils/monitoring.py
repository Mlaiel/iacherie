"""Monitoring Utilities for Events

Metrics collection and monitoring utilities for the event system.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import logging
from typing import Dict, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class MetricsCollector:
    """Collects and manages metrics for event processing"""
    
    def __init__(self):
        self.metrics = {}
        self.enabled = True
        logger.info("MetricsCollector initialized (placeholder implementation)")
    
    def record_event(self, event_type: str, event_data: Dict[str, Any] = None):
        """Record an event metric"""
        if not self.enabled:
            return
            
        timestamp = datetime.utcnow()
        metric_key = f"event.{event_type}"
        
        if metric_key not in self.metrics:
            self.metrics[metric_key] = {
                'count': 0,
                'first_seen': timestamp,
                'last_seen': timestamp
            }
        
        self.metrics[metric_key]['count'] += 1
        self.metrics[metric_key]['last_seen'] = timestamp
        
        logger.debug(f"Recorded metric: {metric_key}")
    
    def record_processing_time(self, event_type: str, processing_time: float):
        """Record processing time for an event type"""
        if not self.enabled:
            return
            
        metric_key = f"processing_time.{event_type}"
        
        if metric_key not in self.metrics:
            self.metrics[metric_key] = {
                'total_time': 0.0,
                'count': 0,
                'min_time': processing_time,
                'max_time': processing_time
            }
        
        metric = self.metrics[metric_key]
        metric['total_time'] += processing_time
        metric['count'] += 1
        metric['min_time'] = min(metric['min_time'], processing_time)
        metric['max_time'] = max(metric['max_time'], processing_time)
        
        logger.debug(f"Recorded processing time: {processing_time:.3f}s for {event_type}")
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get all collected metrics"""
        return self.metrics.copy()
    
    def reset_metrics(self):
        """Reset all metrics"""
        self.metrics.clear()
        logger.info("Metrics reset")
    
    def enable(self):
        """Enable metrics collection"""
        self.enabled = True
        logger.info("Metrics collection enabled")
    
    def disable(self):
        """Disable metrics collection"""
        self.enabled = False
        logger.info("Metrics collection disabled")


# Export for compatibility
__all__ = ['MetricsCollector']