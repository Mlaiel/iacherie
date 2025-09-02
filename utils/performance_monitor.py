"""Utility Classes for AI Agents Business Logic
Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import logging
import time
import asyncio
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)


class PerformanceMonitor:
    """
Monitor performance metrics"""
    
    def __init__(self):
        try:
            logger.info(f"Executing __init__")
            
            # Implementation for __init__
            # TODO: Add specific business logic here
            
            result = None  # Replace with actual implementation
            
            logger.info(f"__init__ completed successfully")
            return result
            
        except Exception as e:
            logger.error(f"__init__ failed: {e}")
            raise
    def set_memory_limit(self, limit_bytes: int):
        """
Set memory limit"""
        try:
            self.memory_limit = limit_bytes
            logger.info(f"Memory limit set to {limit_bytes} bytes ({limit_bytes / 1024 / 1024:.2f} MB)")
        except Exception as e:
            logger.error(f"Failed to set memory limit: {e}")
            raise
        
    def check_memory_usage(self) -> float:
        """
Check current memory usage"""
        try:
            import psutil
            process = psutil.Process()
            memory_info = process.memory_info()
            current_usage = memory_info.rss  # Resident Set Size in bytes
            
            if self.memory_limit:
                usage_percentage = (current_usage / self.memory_limit) * 100
                if usage_percentage > 80:
                    logger.warning(f"High memory usage: {usage_percentage:.1f}% ({current_usage / 1024 / 1024:.2f} MB)")
                return usage_percentage
            else:
                logger.info(f"Current memory usage: {current_usage / 1024 / 1024:.2f} MB")
                return float(current_usage)
        except ImportError:
            # Fallback if psutil is not available
            logger.warning("psutil not available, using basic memory monitoring")
            return 0.0
        except Exception as e:
            logger.error(f"Error checking memory usage: {e}")
            return 0.0


class RateLimiter:
    """
Rate limiting implementation"""
    
    def __init__(self, max_requests: int = 100, window_seconds: int = 60):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.requests = {}
    
    async def check_rate_limit(self, identifier: str) -> bool:
        """
Check if request is within rate limits"""
        current_time = time.time()
        if identifier not in self.requests:
            self.requests[identifier] = []
        
        # Clean old requests
        self.requests[identifier] = [
            req_time for req_time in self.requests[identifier]
            if current_time - req_time < self.window_seconds
        ]
        
        # Check limit
        if len(self.requests[identifier]) >= self.max_requests:
            return False
        
        # Add current request
        self.requests[identifier].append(current_time)
        return True


class CircuitBreaker:
    """
Circuit breaker pattern implementation"""
    
    def __init__(self, failure_threshold: int = 5, recovery_timeout: int = 60):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.failure_count = 0
        self.last_failure_time = None
        self.state = "closed"  # closed, open, half-open
    
    async def call(self, func, *args, **kwargs):
        """Execute function with circuit breaker protection"""
        if self.state == "open":
            if time.time() - self.last_failure_time > self.recovery_timeout:
                self.state = "half-open"
            else:
                raise Exception("Circuit breaker is open")
        
        try:
            result = await func(*args, **kwargs) if asyncio.iscoroutinefunction(func) else func(*args, **kwargs)
            if self.state == "half-open":
                self.state = "closed"
                self.failure_count = 0
            return result
        except Exception as e:
            self.failure_count += 1
            self.last_failure_time = time.time()
            if self.failure_count >= self.failure_threshold:
                self.state = "open"
            raise e