"""
🔄 GATEWAY CIRCUIT BREAKER SERVICE - ENTERPRISE MICROSERVICE
Circuit breaker implementation for API gateway with sophisticated failure detection.

Author: Fahed Mlaiel
Copyright: © 2024-2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
import time
import math
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Callable, Union
from dataclasses import dataclass, asdict
from enum import Enum
import aioredis
import json
from collections import deque, defaultdict

logger = logging.getLogger(__name__)

class CircuitState(Enum):
    """Circuit breaker states"""
    CLOSED = "closed"       # Normal operation
    OPEN = "open"           # Blocking requests
    HALF_OPEN = "half_open" # Testing recovery

@dataclass
class CircuitBreakerConfig:
    """Circuit breaker configuration"""
    failure_threshold: int = 5
    recovery_timeout: int = 60
    request_volume_threshold: int = 10
    error_threshold_percentage: int = 50
    slow_call_threshold: float = 1.0
    slow_call_rate_threshold: int = 50
    half_open_max_calls: int = 3
    sliding_window_size: int = 100
    minimum_throughput: int = 5

@dataclass
class CallResult:
    """Result of a service call"""
    success: bool
    duration: float
    error_type: Optional[str] = None
    timestamp: datetime = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.utcnow()

class CircuitBreakerMetrics:
    """Metrics for circuit breaker"""
    
    def __init__(self, window_size: int = 100):
        self.window_size = window_size
        self.call_results: deque = deque(maxlen=window_size)
        self.total_calls = 0
        self.failed_calls = 0
        self.slow_calls = 0
        self.last_success_time: Optional[datetime] = None
        self.last_failure_time: Optional[datetime] = None
        
    def record_call(self, result: CallResult, slow_threshold: float):
        """Record a call result"""
        self.call_results.append(result)
        self.total_calls += 1
        
        if result.success:
            self.last_success_time = result.timestamp
        else:
            self.failed_calls += 1
            self.last_failure_time = result.timestamp
            
        if result.duration >= slow_threshold:
            self.slow_calls += 1
            
    def get_failure_rate(self) -> float:
        """Get current failure rate percentage"""
        if len(self.call_results) == 0:
            return 0.0
            
        failures = sum(1 for call in self.call_results if not call.success)
        return (failures / len(self.call_results)) * 100
        
    def get_slow_call_rate(self) -> float:
        """Get current slow call rate percentage"""
        if len(self.call_results) == 0:
            return 0.0
            
        slow_calls = sum(1 for call in self.call_results 
                        if call.duration >= 1.0)  # Using 1.0 as default threshold
        return (slow_calls / len(self.call_results)) * 100
        
    def get_recent_calls_count(self) -> int:
        """Get number of calls in the sliding window"""
        return len(self.call_results)
        
    def get_average_response_time(self) -> float:
        """Get average response time"""
        if len(self.call_results) == 0:
            return 0.0
            
        total_time = sum(call.duration for call in self.call_results)
        return total_time / len(self.call_results)

class CircuitBreaker:
    """Individual circuit breaker for a service endpoint"""
    
    def __init__(self, name: str, config: CircuitBreakerConfig):
        self.name = name
        self.config = config
        self.state = CircuitState.CLOSED
        self.metrics = CircuitBreakerMetrics(config.sliding_window_size)
        self.state_changed_time = datetime.utcnow()
        self.half_open_calls = 0
        self.consecutive_failures = 0
        
    def can_execute(self) -> bool:
        """Check if request can be executed"""
        current_time = datetime.utcnow()
        
        if self.state == CircuitState.CLOSED:
            return True
            
        elif self.state == CircuitState.OPEN:
            # Check if recovery timeout has passed
            if (current_time - self.state_changed_time).seconds >= self.config.recovery_timeout:
                self._transition_to_half_open()
                return True
            return False
            
        elif self.state == CircuitState.HALF_OPEN:
            # Allow limited number of calls in half-open state
            return self.half_open_calls < self.config.half_open_max_calls
            
        return False
        
    def record_success(self, duration: float):
        """Record a successful call"""
        result = CallResult(success=True, duration=duration)
        self.metrics.record_call(result, self.config.slow_call_threshold)
        self.consecutive_failures = 0
        
        if self.state == CircuitState.HALF_OPEN:
            self.half_open_calls += 1
            # If enough successful calls in half-open, close the circuit
            if self.half_open_calls >= self.config.half_open_max_calls:
                self._transition_to_closed()
                
    def record_failure(self, duration: float, error_type: str = "unknown"):
        """Record a failed call"""
        result = CallResult(success=False, duration=duration, error_type=error_type)
        self.metrics.record_call(result, self.config.slow_call_threshold)
        self.consecutive_failures += 1
        
        if self.state == CircuitState.HALF_OPEN:
            # Any failure in half-open state opens the circuit again
            self._transition_to_open()
        elif self.state == CircuitState.CLOSED:
            # Check if we should open the circuit
            self._check_failure_threshold()
            
    def _check_failure_threshold(self):
        """Check if failure threshold is exceeded"""
        # Check minimum request volume
        if self.metrics.get_recent_calls_count() < self.config.request_volume_threshold:
            return
            
        # Check failure rate
        failure_rate = self.metrics.get_failure_rate()
        slow_call_rate = self.metrics.get_slow_call_rate()
        
        should_open = (
            failure_rate >= self.config.error_threshold_percentage or
            slow_call_rate >= self.config.slow_call_rate_threshold or
            self.consecutive_failures >= self.config.failure_threshold
        )
        
        if should_open:
            self._transition_to_open()
            
    def _transition_to_open(self):
        """Transition to open state"""
        if self.state != CircuitState.OPEN:
            logger.warning(f"Circuit breaker {self.name} opened due to failures")
            self.state = CircuitState.OPEN
            self.state_changed_time = datetime.utcnow()
            self.half_open_calls = 0
            
    def _transition_to_half_open(self):
        """Transition to half-open state"""
        logger.info(f"Circuit breaker {self.name} transitioning to half-open")
        self.state = CircuitState.HALF_OPEN
        self.state_changed_time = datetime.utcnow()
        self.half_open_calls = 0
        
    def _transition_to_closed(self):
        """Transition to closed state"""
        logger.info(f"Circuit breaker {self.name} closed - service recovered")
        self.state = CircuitState.CLOSED
        self.state_changed_time = datetime.utcnow()
        self.half_open_calls = 0
        
    def get_state_info(self) -> Dict[str, Any]:
        """Get current state information"""
        return {
            'name': self.name,
            'state': self.state.value,
            'failure_rate': self.metrics.get_failure_rate(),
            'slow_call_rate': self.metrics.get_slow_call_rate(),
            'avg_response_time': self.metrics.get_average_response_time(),
            'total_calls': self.metrics.total_calls,
            'failed_calls': self.metrics.failed_calls,
            'consecutive_failures': self.consecutive_failures,
            'state_changed_time': self.state_changed_time.isoformat(),
            'last_success_time': self.metrics.last_success_time.isoformat() if self.metrics.last_success_time else None,
            'last_failure_time': self.metrics.last_failure_time.isoformat() if self.metrics.last_failure_time else None,
            'calls_in_window': self.metrics.get_recent_calls_count()
        }

class GatewayCircuitBreaker:
    """
    🔄 Gateway Circuit Breaker Service
    
    Comprehensive circuit breaker implementation for API gateway with support for
    multiple failure detection strategies, automatic recovery, and detailed metrics.
    """
    
    def __init__(self, redis_url: str = "redis://localhost:6379"):
        self.redis_url = redis_url
        self.redis = None
        
        # Circuit breakers registry
        self.circuit_breakers: Dict[str, CircuitBreaker] = {}
        self.default_config = CircuitBreakerConfig()
        
        # Global metrics
        self.global_metrics = {
            'total_requests': 0,
            'blocked_requests': 0,
            'circuit_trips': 0,
            'circuit_recoveries': 0
        }
        
        # Event callbacks
        self.on_state_change: List[Callable] = []
        
        self.running = False
        
    async def initialize(self):
        """Initialize circuit breaker service"""
        try:
            self.redis = await aioredis.from_url(self.redis_url)
            
            # Load circuit breaker configurations
            await self._load_configurations()
            
            # Start background tasks
            asyncio.create_task(self._metrics_update_task())
            asyncio.create_task(self._state_persistence_task())
            asyncio.create_task(self._cleanup_task())
            
            self.running = True
            logger.info("Gateway Circuit Breaker service initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize gateway circuit breaker: {e}")
            raise
            
    async def _load_configurations(self):
        """Load circuit breaker configurations from Redis"""
        try:
            configs_data = await self.redis.get("gateway:circuit_breaker:configs")
            if configs_data:
                configs = json.loads(configs_data)
                for name, config_dict in configs.items():
                    config = CircuitBreakerConfig(**config_dict)
                    if name not in self.circuit_breakers:
                        self.circuit_breakers[name] = CircuitBreaker(name, config)
                        
        except Exception as e:
            logger.error(f"Failed to load circuit breaker configurations: {e}")
            
    def register_circuit_breaker(self, name: str, config: Optional[CircuitBreakerConfig] = None):
        """Register a new circuit breaker"""
        if config is None:
            config = self.default_config
            
        self.circuit_breakers[name] = CircuitBreaker(name, config)
        logger.info(f"Registered circuit breaker: {name}")
        
    async def execute_with_circuit_breaker(self, name: str, operation: Callable, 
                                         *args, **kwargs) -> Any:
        """Execute operation with circuit breaker protection"""
        if name not in self.circuit_breakers:
            self.register_circuit_breaker(name)
            
        circuit_breaker = self.circuit_breakers[name]
        self.global_metrics['total_requests'] += 1
        
        # Check if circuit allows execution
        if not circuit_breaker.can_execute():
            self.global_metrics['blocked_requests'] += 1
            raise CircuitBreakerOpenException(f"Circuit breaker {name} is open")
            
        # Execute the operation
        start_time = time.time()
        try:
            result = await operation(*args, **kwargs)
            duration = time.time() - start_time
            
            # Record success
            circuit_breaker.record_success(duration)
            
            return result
            
        except Exception as e:
            duration = time.time() - start_time
            error_type = type(e).__name__
            
            # Record failure
            circuit_breaker.record_failure(duration, error_type)
            
            # Check for state changes
            await self._check_state_changes(circuit_breaker)
            
            raise
            
    async def _check_state_changes(self, circuit_breaker: CircuitBreaker):
        """Check and handle circuit breaker state changes"""
        old_state = getattr(circuit_breaker, '_previous_state', CircuitState.CLOSED)
        current_state = circuit_breaker.state
        
        if old_state != current_state:
            circuit_breaker._previous_state = current_state
            
            if current_state == CircuitState.OPEN:
                self.global_metrics['circuit_trips'] += 1
            elif current_state == CircuitState.CLOSED and old_state == CircuitState.HALF_OPEN:
                self.global_metrics['circuit_recoveries'] += 1
                
            # Notify callbacks
            for callback in self.on_state_change:
                try:
                    await callback(circuit_breaker.name, old_state, current_state)
                except Exception as e:
                    logger.error(f"Error in state change callback: {e}")
                    
    def add_state_change_callback(self, callback: Callable):
        """Add callback for state changes"""
        self.on_state_change.append(callback)
        
    async def force_open(self, name: str):
        """Force a circuit breaker to open state"""
        if name in self.circuit_breakers:
            circuit_breaker = self.circuit_breakers[name]
            circuit_breaker._transition_to_open()
            logger.info(f"Forced circuit breaker {name} to open state")
            
    async def force_close(self, name: str):
        """Force a circuit breaker to closed state"""
        if name in self.circuit_breakers:
            circuit_breaker = self.circuit_breakers[name]
            circuit_breaker._transition_to_closed()
            logger.info(f"Forced circuit breaker {name} to closed state")
            
    async def reset_circuit_breaker(self, name: str):
        """Reset a circuit breaker (clear metrics and close)"""
        if name in self.circuit_breakers:
            config = self.circuit_breakers[name].config
            self.circuit_breakers[name] = CircuitBreaker(name, config)
            logger.info(f"Reset circuit breaker {name}")
            
    def get_circuit_breaker_status(self, name: str) -> Optional[Dict[str, Any]]:
        """Get status of a specific circuit breaker"""
        if name in self.circuit_breakers:
            return self.circuit_breakers[name].get_state_info()
        return None
        
    def get_all_circuit_breakers_status(self) -> Dict[str, Dict[str, Any]]:
        """Get status of all circuit breakers"""
        return {
            name: cb.get_state_info() 
            for name, cb in self.circuit_breakers.items()
        }
        
    def get_global_metrics(self) -> Dict[str, Any]:
        """Get global circuit breaker metrics"""
        open_count = sum(1 for cb in self.circuit_breakers.values() 
                        if cb.state == CircuitState.OPEN)
        half_open_count = sum(1 for cb in self.circuit_breakers.values() 
                             if cb.state == CircuitState.HALF_OPEN)
        closed_count = sum(1 for cb in self.circuit_breakers.values() 
                          if cb.state == CircuitState.CLOSED)
                          
        return {
            **self.global_metrics,
            'total_circuit_breakers': len(self.circuit_breakers),
            'open_circuit_breakers': open_count,
            'half_open_circuit_breakers': half_open_count,
            'closed_circuit_breakers': closed_count,
            'success_rate': (
                (self.global_metrics['total_requests'] - self.global_metrics['blocked_requests']) 
                / max(self.global_metrics['total_requests'], 1) * 100
            )
        }
        
    async def _metrics_update_task(self):
        """Background task for updating metrics"""
        while self.running:
            try:
                # Update circuit breaker metrics in Redis
                all_status = self.get_all_circuit_breakers_status()
                global_metrics = self.get_global_metrics()
                
                metrics_data = {
                    'circuit_breakers': all_status,
                    'global_metrics': global_metrics,
                    'timestamp': datetime.utcnow().isoformat()
                }
                
                await self.redis.setex(
                    "gateway:circuit_breaker:metrics", 
                    60, 
                    json.dumps(metrics_data, default=str)
                )
                
                await asyncio.sleep(10)  # Update every 10 seconds
                
            except Exception as e:
                logger.error(f"Error in circuit breaker metrics update task: {e}")
                await asyncio.sleep(30)
                
    async def _state_persistence_task(self):
        """Background task for persisting circuit breaker states"""
        while self.running:
            try:
                # Persist circuit breaker states
                states_data = {}
                for name, cb in self.circuit_breakers.items():
                    states_data[name] = {
                        'state': cb.state.value,
                        'consecutive_failures': cb.consecutive_failures,
                        'state_changed_time': cb.state_changed_time.isoformat(),
                        'half_open_calls': cb.half_open_calls
                    }
                    
                await self.redis.setex(
                    "gateway:circuit_breaker:states", 
                    300, 
                    json.dumps(states_data, default=str)
                )
                
                await asyncio.sleep(30)  # Persist every 30 seconds
                
            except Exception as e:
                logger.error(f"Error in circuit breaker state persistence task: {e}")
                await asyncio.sleep(60)
                
    async def _cleanup_task(self):
        """Background task for cleanup operations"""
        while self.running:
            try:
                current_time = datetime.utcnow()
                
                # Clean up old circuit breakers that haven't been used
                to_remove = []
                for name, cb in self.circuit_breakers.items():
                    if (cb.metrics.last_success_time and 
                        (current_time - cb.metrics.last_success_time).days > 7 and
                        cb.metrics.get_recent_calls_count() == 0):
                        to_remove.append(name)
                        
                for name in to_remove:
                    del self.circuit_breakers[name]
                    logger.info(f"Cleaned up unused circuit breaker: {name}")
                    
                await asyncio.sleep(3600)  # Cleanup every hour
                
            except Exception as e:
                logger.error(f"Error in circuit breaker cleanup task: {e}")
                await asyncio.sleep(3600)
                
    async def health_check(self) -> Dict[str, Any]:
        """Health check for circuit breaker service"""
        try:
            await self.redis.ping()
            redis_status = "healthy"
        except Exception as e:
            redis_status = f"unhealthy: {e}"
            
        global_metrics = self.get_global_metrics()
        
        return {
            'service': 'gateway_circuit_breaker',
            'status': 'healthy' if redis_status == "healthy" else 'unhealthy',
            'redis': redis_status,
            'total_circuit_breakers': global_metrics['total_circuit_breakers'],
            'open_circuit_breakers': global_metrics['open_circuit_breakers'],
            'success_rate': global_metrics['success_rate'],
            'total_requests': global_metrics['total_requests'],
            'blocked_requests': global_metrics['blocked_requests']
        }
        
    async def shutdown(self):
        """Shutdown circuit breaker service"""
        self.running = False
        
        if self.redis:
            await self.redis.close()
            
        logger.info("Gateway Circuit Breaker service shut down")

class CircuitBreakerOpenException(Exception):
    """Exception raised when circuit breaker is open"""
    pass

# Example usage
async def create_gateway_circuit_breaker():
    """Factory function to create gateway circuit breaker service"""
    circuit_breaker = GatewayCircuitBreaker()
    await circuit_breaker.initialize()
    
    return circuit_breaker

if __name__ == "__main__":
    async def example_service_call():
        """Example service call that might fail"""
        import random
        await asyncio.sleep(0.1)
        
        if random.random() < 0.3:  # 30% failure rate
            raise Exception("Service temporarily unavailable")
            
        return "Success"
        
    async def main():
        cb_service = await create_gateway_circuit_breaker()
        
        # Register circuit breaker with custom config
        config = CircuitBreakerConfig(
            failure_threshold=3,
            recovery_timeout=30,
            error_threshold_percentage=40
        )
        cb_service.register_circuit_breaker("example-service", config)
        
        # Simulate multiple requests
        for i in range(20):
            try:
                result = await cb_service.execute_with_circuit_breaker(
                    "example-service", example_service_call
                )
                print(f"Request {i}: {result}")
            except CircuitBreakerOpenException as e:
                print(f"Request {i}: Blocked by circuit breaker")
            except Exception as e:
                print(f"Request {i}: Failed - {e}")
                
            await asyncio.sleep(0.1)
            
        # Check status
        status = cb_service.get_circuit_breaker_status("example-service")
        print("Circuit Breaker Status:", status)
        
        global_metrics = cb_service.get_global_metrics()
        print("Global Metrics:", global_metrics)
        
        await cb_service.shutdown()
        
    asyncio.run(main())