"""
Monitoring and Metrics Collection System
Track API usage, performance metrics, and system health
"""
import time
from typing import Dict, Any, List, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class MetricsCollector:
    """
    Collects and manages application metrics
    """
    
    def __init__(self):
        self.metrics = {
            "counters": {},
            "histograms": {},
            "gauges": {}
        }
    
    async def increment_counter(self, name: str, labels: Optional[Dict[str, str]] = None):
        """Increment a counter metric"""
        key = f"{name}:{','.join(f'{k}={v}' for k, v in (labels or {}).items())}"
        if key not in self.metrics["counters"]:
            self.metrics["counters"][key] = 0
        self.metrics["counters"][key] += 1
    
    async def record_histogram(self, name: str, value: float, labels: Optional[Dict[str, str]] = None):
        """Record a histogram value"""
        key = f"{name}:{','.join(f'{k}={v}' for k, v in (labels or {}).items())}"
        if key not in self.metrics["histograms"]:
            self.metrics["histograms"][key] = []
        self.metrics["histograms"][key].append(value)
    
    async def set_gauge(self, name: str, value: float, labels: Optional[Dict[str, str]] = None):
        """Set a gauge value"""
        key = f"{name}:{','.join(f'{k}={v}' for k, v in (labels or {}).items())}"
        self.metrics["gauges"][key] = value
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get all collected metrics"""
        return self.metrics.copy()

# Global metrics collector
metrics_collector = MetricsCollector()

async def track_api_usage(endpoint: str, user_id: str, usage_data: Dict[str, Any]):
    """
        Track API usage for monitoring and billing purposes"""
    try:
        await metrics_collector.increment_counter(
            "api_requests_total",
            {"endpoint": endpoint, "user_id": user_id}
        )

        
        if "total_tokens" in usage_data:
            await metrics_collector.record_histogram(
                "api_tokens_used",
                usage_data["total_tokens"],
                {"endpoint": endpoint, "user_id": user_id}
            )

        
        if "duration_seconds" in usage_data:
            await metrics_collector.record_histogram(
                "api_response_time",
                usage_data["duration_seconds"],
                {"endpoint": endpoint}
            )

        
        logger.info(f"Tracked usage for {endpoint}: user={user_id}, data={usage_data}")

        
    except Exception as e:
        logger.error(f"Failed to track API usage: {e}")

# Export for use in other modules
__all__ = ["MetricsCollector", "metrics_collector", "track_api_usage"]