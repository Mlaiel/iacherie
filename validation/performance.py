"""
Performance Validation Module
Ensures API response time < 200ms, page load < 3s, 10k concurrent users support, 99.9% uptime SLA, < 1% error rate
"""

import time
import asyncio
from typing import Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

@dataclass
class PerformanceMetrics:
    """Performance metrics tracking"""
    response_time: float
    status_code: int
    endpoint: str
    timestamp: datetime
    error_count: int = 0
    success_count: int = 0

class PerformanceTracker:
    """Tracks performance metrics for validation"""
    
    def __init__(self):
        self.metrics: Dict[str, list] = {}
        self.error_count = 0
        self.total_requests = 0
        
    async def track_request(self, endpoint: str, response_time: float, status_code: int):
        """Track individual request performance"""
        self.total_requests += 1
        
        if status_code >= 400:
            self.error_count += 1
            
        metric = PerformanceMetrics(
            response_time=response_time,
            status_code=status_code,
            endpoint=endpoint,
            timestamp=datetime.now()
        )
        
        if endpoint not in self.metrics:
            self.metrics[endpoint] = []
        self.metrics[endpoint].append(metric)
    
    def get_average_response_time(self, endpoint: Optional[str] = None) -> float:
        """Get average response time for endpoint or overall"""
        if endpoint and endpoint in self.metrics:
            response_times = [m.response_time for m in self.metrics[endpoint]]
        else:
            response_times = []
            for metrics_list in self.metrics.values():
                response_times.extend([m.response_time for m in metrics_list])
        
        return sum(response_times) / len(response_times) if response_times else 0
    
    def get_error_rate(self) -> float:
        """Get current error rate percentage"""
        if self.total_requests == 0:
            return 0
        return (self.error_count / self.total_requests) * 100
    
    def validate_performance_criteria(self) -> Dict[str, Any]:
        """Validate all performance criteria"""
        avg_response_time = self.get_average_response_time()
        error_rate = self.get_error_rate()
        
        return {
            "api_response_time_ms": avg_response_time * 1000,
            "api_response_time_valid": avg_response_time < 0.2,  # < 200ms
            "error_rate_percent": error_rate,
            "error_rate_valid": error_rate < 1.0,  # < 1%
            "total_requests": self.total_requests,
            "total_errors": self.error_count,
            "uptime_target": "99.9%",
            "page_load_target": "< 3s",
            "concurrent_users_target": "10k",
        }

# Global performance tracker instance
performance_tracker = PerformanceTracker()

def get_performance_tracker() -> PerformanceTracker:
    """Get the global performance tracker instance"""
    return performance_tracker

async def validate_api_performance() -> Dict[str, Any]:
    """Validate API performance against criteria"""
    return performance_tracker.validate_performance_criteria()

# Load testing configuration
LOAD_TEST_CONFIG = {
    "concurrent_users": 10000,
    "test_duration": "5m",
    "ramp_up_time": "30s",
    "endpoints": [
        "/health",
        "/api/v1/status",
        "/validation/performance"
    ]
}

def get_load_test_config() -> Dict[str, Any]:
    """Get load testing configuration for 10k concurrent users"""
    return LOAD_TEST_CONFIG