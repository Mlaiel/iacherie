"""
⏱️ GATEWAY TIMEOUT HANDLER SERVICE - ENTERPRISE MICROSERVICE
Comprehensive timeout handling for API gateway with adaptive timeout strategies.

Author: Fahed Mlaiel
Copyright: © 2024-2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
import time
import signal
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Callable, Union
from dataclasses import dataclass, asdict
from enum import Enum
import aioredis
import json
from collections import defaultdict, deque

logger = logging.getLogger(__name__)

class TimeoutStrategy(Enum):
    """Timeout strategy types"""
    FIXED = "fixed"
    ADAPTIVE = "adaptive"
    PERCENTILE_BASED = "percentile_based"
    CONNECTION_BASED = "connection_based"

@dataclass
class TimeoutConfig:
    """Timeout configuration"""
    connect_timeout: float = 5.0
    read_timeout: float = 30.0
    write_timeout: float = 30.0
    total_timeout: float = 60.0
    strategy: TimeoutStrategy = TimeoutStrategy.FIXED
    adaptive_factor: float = 1.5
    percentile: int = 95
    min_timeout: float = 1.0
    max_timeout: float = 300.0
    backoff_factor: float = 2.0
    max_retries: int = 3

@dataclass
class TimeoutEvent:
    """Timeout event data"""
    request_id: str
    endpoint: str
    timeout_type: str
    duration: float
    expected_timeout: float
    timestamp: datetime
    retry_count: int = 0
    
class TimeoutMetrics:
    """Metrics for timeout handling"""
    
    def __init__(self, window_size: int = 1000):
        self.window_size = window_size
        self.response_times: deque = deque(maxlen=window_size)
        self.timeout_events: deque = deque(maxlen=window_size)
        self.total_requests = 0
        self.timeout_count = 0
        
    def record_response_time(self, duration: float):
        """Record response time"""
        self.response_times.append(duration)
        self.total_requests += 1
        
    def record_timeout(self, event: TimeoutEvent):
        """Record timeout event"""
        self.timeout_events.append(event)
        self.timeout_count += 1
        
    def get_percentile_response_time(self, percentile: int = 95) -> float:
        """Get percentile response time"""
        if not self.response_times:
            return 1.0
            
        sorted_times = sorted(self.response_times)
        index = int((percentile / 100) * len(sorted_times))
        return sorted_times[min(index, len(sorted_times) - 1)]
        
    def get_average_response_time(self) -> float:
        """Get average response time"""
        if not self.response_times:
            return 1.0
        return sum(self.response_times) / len(self.response_times)
        
    def get_timeout_rate(self) -> float:
        """Get timeout rate percentage"""
        if self.total_requests == 0:
            return 0.0
        return (self.timeout_count / self.total_requests) * 100

class GatewayTimeoutHandler:
    """
    ⏱️ Gateway Timeout Handler Service
    
    Comprehensive timeout handling for API gateway with adaptive timeout strategies,
    connection pooling awareness, and detailed timeout analytics.
    """
    
    def __init__(self, redis_url: str = "redis://localhost:6379"):
        self.redis_url = redis_url
        self.redis = None
        
        # Timeout configurations per endpoint
        self.timeout_configs: Dict[str, TimeoutConfig] = {}
        self.default_config = TimeoutConfig()
        
        # Metrics tracking
        self.endpoint_metrics: Dict[str, TimeoutMetrics] = defaultdict(TimeoutMetrics)
        
        # Active timeouts tracking
        self.active_timeouts: Dict[str, asyncio.Task] = {}
        self.timeout_callbacks: Dict[str, Callable] = {}
        
        # Global timeout statistics
        self.global_stats = {
            'total_requests': 0,
            'total_timeouts': 0,
            'total_retries': 0,
            'average_timeout_duration': 0.0
        }
        
        self.running = False
        
    async def initialize(self):
        """Initialize timeout handler service"""
        try:
            self.redis = await aioredis.from_url(self.redis_url)
            
            # Load timeout configurations
            await self._load_timeout_configs()
            
            # Start background tasks
            asyncio.create_task(self._adaptive_timeout_task())
            asyncio.create_task(self._metrics_update_task())
            asyncio.create_task(self._cleanup_task())
            
            self.running = True
            logger.info("Gateway Timeout Handler service initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize gateway timeout handler: {e}")
            raise
            
    async def _load_timeout_configs(self):
        """Load timeout configurations from Redis"""
        try:
            configs_data = await self.redis.get("gateway:timeout:configs")
            if configs_data:
                configs = json.loads(configs_data)
                for endpoint, config_dict in configs.items():
                    self.timeout_configs[endpoint] = TimeoutConfig(**config_dict)
                    
        except Exception as e:
            logger.error(f"Failed to load timeout configurations: {e}")
            
    def configure_timeout(self, endpoint: str, config: TimeoutConfig):
        """Configure timeout for specific endpoint"""
        self.timeout_configs[endpoint] = config
        logger.info(f"Configured timeout for endpoint {endpoint}")
        
    async def execute_with_timeout(self, request_id: str, endpoint: str, 
                                 operation: Callable, *args, **kwargs) -> Any:
        """Execute operation with timeout protection"""
        config = self.timeout_configs.get(endpoint, self.default_config)
        metrics = self.endpoint_metrics[endpoint]
        
        # Calculate adaptive timeout
        timeout_value = await self._calculate_timeout(endpoint, config, metrics)
        
        self.global_stats['total_requests'] += 1
        start_time = time.time()
        
        try:
            # Create timeout task
            timeout_task = asyncio.create_task(self._timeout_monitor(request_id, endpoint, timeout_value))
            self.active_timeouts[request_id] = timeout_task
            
            # Execute operation with timeout
            result = await asyncio.wait_for(
                operation(*args, **kwargs), 
                timeout=timeout_value
            )
            
            # Record successful response time
            duration = time.time() - start_time
            metrics.record_response_time(duration)
            
            return result
            
        except asyncio.TimeoutError:
            duration = time.time() - start_time
            
            # Record timeout event
            timeout_event = TimeoutEvent(
                request_id=request_id,
                endpoint=endpoint,
                timeout_type="execution_timeout",
                duration=duration,
                expected_timeout=timeout_value,
                timestamp=datetime.utcnow()
            )
            
            metrics.record_timeout(timeout_event)
            self.global_stats['total_timeouts'] += 1
            
            logger.warning(f"Request {request_id} to {endpoint} timed out after {duration:.2f}s")
            
            # Execute timeout callback if registered
            if endpoint in self.timeout_callbacks:
                try:
                    await self.timeout_callbacks[endpoint](timeout_event)
                except Exception as e:
                    logger.error(f"Error in timeout callback for {endpoint}: {e}")
                    
            raise TimeoutException(f"Request timed out after {duration:.2f}s", timeout_event)
            
        finally:
            # Cleanup timeout task
            if request_id in self.active_timeouts:
                self.active_timeouts[request_id].cancel()
                del self.active_timeouts[request_id]
                
    async def execute_with_retries(self, request_id: str, endpoint: str, 
                                 operation: Callable, *args, **kwargs) -> Any:
        """Execute operation with timeout and retry logic"""
        config = self.timeout_configs.get(endpoint, self.default_config)
        last_exception = None
        
        for attempt in range(config.max_retries + 1):
            try:
                retry_request_id = f"{request_id}_retry_{attempt}"
                return await self.execute_with_timeout(
                    retry_request_id, endpoint, operation, *args, **kwargs
                )
                
            except TimeoutException as e:
                last_exception = e
                
                if attempt < config.max_retries:
                    # Calculate backoff delay
                    delay = config.backoff_factor ** attempt
                    
                    logger.info(f"Retrying request {request_id} to {endpoint} after {delay}s "
                              f"(attempt {attempt + 1}/{config.max_retries + 1})")
                    
                    self.global_stats['total_retries'] += 1
                    
                    await asyncio.sleep(delay)
                else:
                    logger.error(f"All retry attempts exhausted for request {request_id} to {endpoint}")
                    
        raise last_exception
        
    async def _calculate_timeout(self, endpoint: str, config: TimeoutConfig, 
                               metrics: TimeoutMetrics) -> float:
        """Calculate timeout based on strategy"""
        
        if config.strategy == TimeoutStrategy.FIXED:
            return config.total_timeout
            
        elif config.strategy == TimeoutStrategy.ADAPTIVE:
            avg_response_time = metrics.get_average_response_time()
            adaptive_timeout = avg_response_time * config.adaptive_factor
            return max(min(adaptive_timeout, config.max_timeout), config.min_timeout)
            
        elif config.strategy == TimeoutStrategy.PERCENTILE_BASED:
            percentile_time = metrics.get_percentile_response_time(config.percentile)
            percentile_timeout = percentile_time * config.adaptive_factor
            return max(min(percentile_timeout, config.max_timeout), config.min_timeout)
            
        elif config.strategy == TimeoutStrategy.CONNECTION_BASED:
            # Adjust timeout based on current connection load
            # This is a simplified implementation
            base_timeout = config.total_timeout
            load_factor = len(self.active_timeouts) / 100  # Assume 100 max connections
            adjusted_timeout = base_timeout * (1 + load_factor)
            return max(min(adjusted_timeout, config.max_timeout), config.min_timeout)
            
        else:
            return config.total_timeout
            
    async def _timeout_monitor(self, request_id: str, endpoint: str, timeout_value: float):
        """Monitor timeout for a specific request"""
        try:
            await asyncio.sleep(timeout_value)
            # If we reach here, the request has timed out
            logger.debug(f"Timeout monitor triggered for request {request_id}")
        except asyncio.CancelledError:
            # Normal completion - timeout was cancelled
            pass
            
    def register_timeout_callback(self, endpoint: str, callback: Callable):
        """Register callback for timeout events"""
        self.timeout_callbacks[endpoint] = callback
        logger.info(f"Registered timeout callback for endpoint {endpoint}")
        
    async def cancel_request_timeout(self, request_id: str):
        """Cancel timeout for a specific request"""
        if request_id in self.active_timeouts:
            self.active_timeouts[request_id].cancel()
            del self.active_timeouts[request_id]
            logger.debug(f"Cancelled timeout for request {request_id}")
            
    async def get_endpoint_timeout_metrics(self, endpoint: str) -> Dict[str, Any]:
        """Get timeout metrics for specific endpoint"""
        if endpoint not in self.endpoint_metrics:
            return {}
            
        metrics = self.endpoint_metrics[endpoint]
        config = self.timeout_configs.get(endpoint, self.default_config)
        
        current_timeout = await self._calculate_timeout(endpoint, config, metrics)
        
        return {
            'endpoint': endpoint,
            'current_timeout': current_timeout,
            'timeout_strategy': config.strategy.value,
            'total_requests': metrics.total_requests,
            'timeout_count': metrics.timeout_count,
            'timeout_rate': metrics.get_timeout_rate(),
            'average_response_time': metrics.get_average_response_time(),
            'p95_response_time': metrics.get_percentile_response_time(95),
            'p99_response_time': metrics.get_percentile_response_time(99),
            'active_requests': len([req_id for req_id in self.active_timeouts.keys() 
                                  if endpoint in req_id]),
            'config': asdict(config)
        }
        
    async def get_all_timeout_metrics(self) -> Dict[str, Any]:
        """Get timeout metrics for all endpoints"""
        endpoint_metrics = {}
        
        for endpoint in self.endpoint_metrics.keys():
            endpoint_metrics[endpoint] = await self.get_endpoint_timeout_metrics(endpoint)
            
        return {
            'global_stats': self.global_stats,
            'active_timeouts': len(self.active_timeouts),
            'configured_endpoints': len(self.timeout_configs),
            'endpoint_metrics': endpoint_metrics
        }
        
    async def update_timeout_strategy(self, endpoint: str, strategy: TimeoutStrategy, 
                                    **kwargs):
        """Update timeout strategy for endpoint"""
        if endpoint in self.timeout_configs:
            config = self.timeout_configs[endpoint]
        else:
            config = TimeoutConfig()
            
        config.strategy = strategy
        
        # Update additional parameters
        for key, value in kwargs.items():
            if hasattr(config, key):
                setattr(config, key, value)
                
        self.timeout_configs[endpoint] = config
        
        # Save to Redis
        await self._save_timeout_configs()
        
        logger.info(f"Updated timeout strategy for {endpoint} to {strategy.value}")
        
    async def _save_timeout_configs(self):
        """Save timeout configurations to Redis"""
        try:
            configs_data = {
                endpoint: asdict(config) 
                for endpoint, config in self.timeout_configs.items()
            }
            
            await self.redis.set(
                "gateway:timeout:configs", 
                json.dumps(configs_data, default=str)
            )
            
        except Exception as e:
            logger.error(f"Failed to save timeout configurations: {e}")
            
    async def _adaptive_timeout_task(self):
        """Background task for adaptive timeout adjustments"""
        while self.running:
            try:
                current_time = datetime.utcnow()
                
                for endpoint, metrics in self.endpoint_metrics.items():
                    config = self.timeout_configs.get(endpoint)
                    if not config or config.strategy != TimeoutStrategy.ADAPTIVE:
                        continue
                        
                    # Analyze recent timeout patterns
                    recent_timeouts = [
                        event for event in metrics.timeout_events
                        if (current_time - event.timestamp).seconds < 300  # Last 5 minutes
                    ]
                    
                    # Adjust timeout if needed
                    if len(recent_timeouts) > 5:  # Too many timeouts
                        new_timeout = min(config.total_timeout * 1.2, config.max_timeout)
                        config.total_timeout = new_timeout
                        logger.info(f"Increased timeout for {endpoint} to {new_timeout}s due to frequent timeouts")
                        
                    elif len(recent_timeouts) == 0 and metrics.total_requests > 100:
                        # No recent timeouts, can reduce timeout
                        avg_time = metrics.get_average_response_time()
                        if avg_time * 2 < config.total_timeout:
                            new_timeout = max(avg_time * 2, config.min_timeout)
                            config.total_timeout = new_timeout
                            logger.info(f"Reduced timeout for {endpoint} to {new_timeout}s due to good performance")
                            
                await asyncio.sleep(60)  # Adjust every minute
                
            except Exception as e:
                logger.error(f"Error in adaptive timeout task: {e}")
                await asyncio.sleep(60)
                
    async def _metrics_update_task(self):
        """Background task for updating timeout metrics"""
        while self.running:
            try:
                # Update timeout metrics in Redis
                all_metrics = await self.get_all_timeout_metrics()
                
                await self.redis.setex(
                    "gateway:timeout:metrics", 
                    60, 
                    json.dumps(all_metrics, default=str)
                )
                
                await asyncio.sleep(15)  # Update every 15 seconds
                
            except Exception as e:
                logger.error(f"Error in timeout metrics update task: {e}")
                await asyncio.sleep(60)
                
    async def _cleanup_task(self):
        """Background task for cleaning up old data"""
        while self.running:
            try:
                current_time = datetime.utcnow()
                cleanup_cutoff = current_time - timedelta(hours=24)
                
                # Clean up old timeout events and response times
                for metrics in self.endpoint_metrics.values():
                    # Clean timeout events
                    metrics.timeout_events = deque(
                        (event for event in metrics.timeout_events 
                         if event.timestamp > cleanup_cutoff),
                        maxlen=metrics.window_size
                    )
                    
                # Clean up completed timeout tasks
                completed_tasks = [
                    req_id for req_id, task in self.active_timeouts.items()
                    if task.done()
                ]
                
                for req_id in completed_tasks:
                    del self.active_timeouts[req_id]
                    
                await asyncio.sleep(3600)  # Cleanup every hour
                
            except Exception as e:
                logger.error(f"Error in timeout cleanup task: {e}")
                await asyncio.sleep(3600)
                
    async def health_check(self) -> Dict[str, Any]:
        """Health check for timeout handler service"""
        try:
            await self.redis.ping()
            redis_status = "healthy"
        except Exception as e:
            redis_status = f"unhealthy: {e}"
            
        total_timeouts = sum(metrics.timeout_count for metrics in self.endpoint_metrics.values())
        total_requests = sum(metrics.total_requests for metrics in self.endpoint_metrics.values())
        
        timeout_rate = (total_timeouts / max(total_requests, 1)) * 100
        
        return {
            'service': 'gateway_timeout_handler',
            'status': 'healthy' if redis_status == "healthy" and timeout_rate < 10 else 'degraded',
            'redis': redis_status,
            'active_timeouts': len(self.active_timeouts),
            'configured_endpoints': len(self.timeout_configs),
            'total_requests': total_requests,
            'total_timeouts': total_timeouts,
            'timeout_rate': timeout_rate
        }
        
    async def shutdown(self):
        """Shutdown timeout handler service"""
        self.running = False
        
        # Cancel all active timeouts
        for task in self.active_timeouts.values():
            task.cancel()
            
        self.active_timeouts.clear()
        
        if self.redis:
            await self.redis.close()
            
        logger.info("Gateway Timeout Handler service shut down")

class TimeoutException(Exception):
    """Exception raised when operation times out"""
    
    def __init__(self, message: str, timeout_event: TimeoutEvent):
        super().__init__(message)
        self.timeout_event = timeout_event

# Example usage
async def create_gateway_timeout_handler():
    """Factory function to create gateway timeout handler service"""
    timeout_handler = GatewayTimeoutHandler()
    await timeout_handler.initialize()
    
    return timeout_handler

if __name__ == "__main__":
    async def example_slow_operation():
        """Example operation that might be slow"""
        import random
        delay = random.uniform(0.1, 2.0)
        await asyncio.sleep(delay)
        return f"Completed after {delay:.2f}s"
        
    async def timeout_callback(timeout_event: TimeoutEvent):
        """Example timeout callback"""
        print(f"Timeout callback: {timeout_event.endpoint} timed out after {timeout_event.duration:.2f}s")
        
    async def main():
        timeout_handler = await create_gateway_timeout_handler()
        
        # Configure timeout for endpoint
        config = TimeoutConfig(
            total_timeout=1.0,
            strategy=TimeoutStrategy.ADAPTIVE,
            max_retries=2
        )
        timeout_handler.configure_timeout("/api/v1/slow-service", config)
        
        # Register timeout callback
        timeout_handler.register_timeout_callback("/api/v1/slow-service", timeout_callback)
        
        # Execute operations
        for i in range(10):
            try:
                result = await timeout_handler.execute_with_retries(
                    f"req_{i}", "/api/v1/slow-service", example_slow_operation
                )
                print(f"Request {i}: {result}")
            except TimeoutException as e:
                print(f"Request {i}: Timed out - {e}")
                
        # Get metrics
        metrics = await timeout_handler.get_endpoint_timeout_metrics("/api/v1/slow-service")
        print("Timeout Metrics:", metrics)
        
        await timeout_handler.shutdown()
        
    asyncio.run(main())