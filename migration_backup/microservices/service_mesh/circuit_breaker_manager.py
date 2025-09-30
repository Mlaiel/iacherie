#!/usr/bin/env python3
"""
⚡ CIRCUIT BREAKER MANAGER
=========================

Advanced circuit breaker pattern implementation for the Ainflue platform.
Provides fault tolerance, failure detection, and automatic recovery mechanisms.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel - All Rights Reserved

⚠️ STRICT COPYRIGHT WARNING ⚠️
This code is proprietary and confidential. Unauthorized use, reproduction,
distribution, or modification is strictly prohibited and will be prosecuted
to the full extent of the law.
"""

import asyncio
import logging
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Callable, Union
from dataclasses import dataclass, asdict
from enum import Enum
import functools
import inspect
from collections import deque, defaultdict
import threading
import json
import redis.asyncio as redis

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CircuitBreakerState(Enum):
    """Circuit breaker state enumeration"""
    CLOSED = "closed"      # Normal operation
    OPEN = "open"          # Circuit is open, rejecting calls
    HALF_OPEN = "half_open"  # Testing if service is recovered

class FailureType(Enum):
    """Failure type enumeration"""
    TIMEOUT = "timeout"
    EXCEPTION = "exception"
    HTTP_ERROR = "http_error"
    CUSTOM = "custom"

@dataclass
class CircuitBreakerConfig:
    """Circuit breaker configuration"""
    name: str
    failure_threshold: int = 5           # Number of failures before opening
    recovery_timeout: int = 60           # Seconds before trying half-open
    expected_exception: type = Exception  # Exception type to handle
    timeout: float = 30.0               # Timeout for operations
    half_open_max_calls: int = 3        # Max calls in half-open state
    failure_rate_threshold: float = 0.5  # Failure rate threshold (0.5 = 50%)
    sliding_window_size: int = 10       # Size of sliding window for failure rate
    minimum_throughput: int = 5         # Minimum calls before failure rate check

@dataclass
class CircuitBreakerMetrics:
    """Circuit breaker metrics"""
    name: str
    state: CircuitBreakerState
    failure_count: int
    success_count: int
    total_calls: int
    failure_rate: float
    last_failure_time: Optional[datetime]
    last_state_change: datetime
    recovery_attempts: int
    open_duration: float = 0.0
    average_response_time: float = 0.0

@dataclass
class CallResult:
    """Result of a circuit breaker protected call"""
    success: bool
    response_time: float
    exception: Optional[Exception] = None
    failure_type: Optional[FailureType] = None
    timestamp: datetime = None

class CircuitBreaker:
    """Circuit breaker implementation"""
    
    def __init__(self, config: CircuitBreakerConfig):
        self.config = config
        self.state = CircuitBreakerState.CLOSED
        self.failure_count = 0
        self.success_count = 0
        self.total_calls = 0
        self.last_failure_time: Optional[datetime] = None
        self.last_state_change = datetime.now()
        self.recovery_attempts = 0
        self.call_history: deque = deque(maxlen=config.sliding_window_size)
        self.response_times: deque = deque(maxlen=100)
        self.lock = threading.Lock()
        
        logger.info(f"✅ Circuit breaker '{config.name}' initialized")
    
    async def call(self, func: Callable, *args, **kwargs) -> Any:
        """Execute a function with circuit breaker protection"""
        with self.lock:
            if self._should_reject_call():
                raise CircuitBreakerOpenException(
                    f"Circuit breaker '{self.config.name}' is OPEN"
                )
        
        start_time = time.time()
        call_result = None
        
        try:
            # Execute the function with timeout
            if inspect.iscoroutinefunction(func):
                result = await asyncio.wait_for(
                    func(*args, **kwargs),
                    timeout=self.config.timeout
                )
            else:
                # Run sync function in thread pool
                result = await asyncio.get_event_loop().run_in_executor(
                    None, functools.partial(func, *args, **kwargs)
                )
            
            response_time = time.time() - start_time
            call_result = CallResult(
                success=True,
                response_time=response_time,
                timestamp=datetime.now()
            )
            
            self._record_success(call_result)
            return result
            
        except asyncio.TimeoutError as e:
            response_time = time.time() - start_time
            call_result = CallResult(
                success=False,
                response_time=response_time,
                exception=e,
                failure_type=FailureType.TIMEOUT,
                timestamp=datetime.now()
            )
            self._record_failure(call_result)
            raise CircuitBreakerTimeoutException(
                f"Circuit breaker '{self.config.name}' call timed out"
            ) from e
            
        except self.config.expected_exception as e:
            response_time = time.time() - start_time
            call_result = CallResult(
                success=False,
                response_time=response_time,
                exception=e,
                failure_type=FailureType.EXCEPTION,
                timestamp=datetime.now()
            )
            self._record_failure(call_result)
            raise
            
        except Exception as e:
            response_time = time.time() - start_time
            call_result = CallResult(
                success=False,
                response_time=response_time,
                exception=e,
                failure_type=FailureType.CUSTOM,
                timestamp=datetime.now()
            )
            self._record_failure(call_result)
            raise
    
    def _should_reject_call(self) -> bool:
        """Determine if the call should be rejected"""
        current_time = datetime.now()
        
        if self.state == CircuitBreakerState.CLOSED:
            return False
        
        elif self.state == CircuitBreakerState.OPEN:
            # Check if recovery timeout has passed
            if (self.last_failure_time and 
                current_time - self.last_failure_time >= timedelta(seconds=self.config.recovery_timeout)):
                self._transition_to_half_open()
                return False
            return True
            
        elif self.state == CircuitBreakerState.HALF_OPEN:
            # Allow limited calls in half-open state
            return self.success_count >= self.config.half_open_max_calls
        
        return False
    
    def _record_success(self, call_result: CallResult):
        """Record a successful call"""
        with self.lock:
            self.success_count += 1
            self.total_calls += 1
            self.call_history.append(call_result)
            self.response_times.append(call_result.response_time)
            
            if self.state == CircuitBreakerState.HALF_OPEN:
                if self.success_count >= self.config.half_open_max_calls:
                    self._transition_to_closed()
            
            logger.debug(f"✅ Success recorded for '{self.config.name}' "
                        f"(successes: {self.success_count}, total: {self.total_calls})")
    
    def _record_failure(self, call_result: CallResult):
        """Record a failed call"""
        with self.lock:
            self.failure_count += 1
            self.total_calls += 1
            self.last_failure_time = call_result.timestamp
            self.call_history.append(call_result)
            self.response_times.append(call_result.response_time)
            
            # Check if we should open the circuit
            if self._should_open_circuit():
                self._transition_to_open()
            
            logger.warning(f"❌ Failure recorded for '{self.config.name}' "
                          f"(failures: {self.failure_count}, total: {self.total_calls})")
    
    def _should_open_circuit(self) -> bool:
        """Determine if the circuit should be opened"""
        if self.state == CircuitBreakerState.OPEN:
            return False
        
        # Check failure count threshold
        if self.failure_count >= self.config.failure_threshold:
            return True
        
        # Check failure rate threshold
        if (self.total_calls >= self.config.minimum_throughput and
            len(self.call_history) >= self.config.minimum_throughput):
            
            recent_failures = sum(1 for call in self.call_history if not call.success)
            failure_rate = recent_failures / len(self.call_history)
            
            if failure_rate >= self.config.failure_rate_threshold:
                return True
        
        return False
    
    def _transition_to_open(self):
        """Transition circuit breaker to OPEN state"""
        old_state = self.state
        self.state = CircuitBreakerState.OPEN
        self.last_state_change = datetime.now()
        
        logger.warning(f"🔴 Circuit breaker '{self.config.name}' transitioned "
                      f"from {old_state.value} to OPEN")
    
    def _transition_to_half_open(self):
        """Transition circuit breaker to HALF_OPEN state"""
        old_state = self.state
        self.state = CircuitBreakerState.HALF_OPEN
        self.last_state_change = datetime.now()
        self.success_count = 0  # Reset success count for half-open testing
        self.recovery_attempts += 1
        
        logger.info(f"🟡 Circuit breaker '{self.config.name}' transitioned "
                   f"from {old_state.value} to HALF_OPEN")
    
    def _transition_to_closed(self):
        """Transition circuit breaker to CLOSED state"""
        old_state = self.state
        self.state = CircuitBreakerState.CLOSED
        self.last_state_change = datetime.now()
        self.failure_count = 0  # Reset failure count
        
        logger.info(f"🟢 Circuit breaker '{self.config.name}' transitioned "
                   f"from {old_state.value} to CLOSED")
    
    def get_metrics(self) -> CircuitBreakerMetrics:
        """Get circuit breaker metrics"""
        failure_rate = 0.0
        if self.total_calls > 0:
            recent_failures = sum(1 for call in self.call_history if not call.success)
            failure_rate = recent_failures / len(self.call_history) if self.call_history else 0.0
        
        open_duration = 0.0
        if self.state == CircuitBreakerState.OPEN and self.last_failure_time:
            open_duration = (datetime.now() - self.last_state_change).total_seconds()
        
        avg_response_time = 0.0
        if self.response_times:
            avg_response_time = sum(self.response_times) / len(self.response_times)
        
        return CircuitBreakerMetrics(
            name=self.config.name,
            state=self.state,
            failure_count=self.failure_count,
            success_count=self.success_count,
            total_calls=self.total_calls,
            failure_rate=failure_rate,
            last_failure_time=self.last_failure_time,
            last_state_change=self.last_state_change,
            recovery_attempts=self.recovery_attempts,
            open_duration=open_duration,
            average_response_time=avg_response_time
        )
    
    def reset(self):
        """Reset circuit breaker to initial state"""
        with self.lock:
            self.state = CircuitBreakerState.CLOSED
            self.failure_count = 0
            self.success_count = 0
            self.total_calls = 0
            self.last_failure_time = None
            self.last_state_change = datetime.now()
            self.recovery_attempts = 0
            self.call_history.clear()
            self.response_times.clear()
        
        logger.info(f"🔄 Circuit breaker '{self.config.name}' reset")

class CircuitBreakerOpenException(Exception):
    """Exception raised when circuit breaker is open"""
    pass

class CircuitBreakerTimeoutException(Exception):
    """Exception raised when circuit breaker call times out"""
    pass

class CircuitBreakerManager:
    """Circuit breaker manager for multiple circuit breakers"""
    
    def __init__(self):
        self.service_name = "CircuitBreakerManager"
        self.version = "1.0.0"
        self.circuit_breakers: Dict[str, CircuitBreaker] = {}
        self.redis_client: Optional[redis.Redis] = None
        self.monitoring_enabled = True
        self.monitoring_task: Optional[asyncio.Task] = None
        
        logger.info(f"✅ {self.service_name} v{self.version} initialized")
    
    async def initialize(self, redis_url: str = "redis://localhost:6379/0"):
        """Initialize the circuit breaker manager"""
        try:
            # Initialize Redis connection
            self.redis_client = redis.from_url(redis_url, decode_responses=True)
            await self.redis_client.ping()
            
            # Start monitoring
            await self.start_monitoring()
            
            logger.info(f"⚡ {self.service_name} initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize {self.service_name}: {str(e)}")
            return False
    
    def create_circuit_breaker(self, config: CircuitBreakerConfig) -> CircuitBreaker:
        """Create a new circuit breaker"""
        if config.name in self.circuit_breakers:
            logger.warning(f"⚠️ Circuit breaker '{config.name}' already exists")
            return self.circuit_breakers[config.name]
        
        circuit_breaker = CircuitBreaker(config)
        self.circuit_breakers[config.name] = circuit_breaker
        
        logger.info(f"🔧 Created circuit breaker: {config.name}")
        return circuit_breaker
    
    def get_circuit_breaker(self, name: str) -> Optional[CircuitBreaker]:
        """Get a circuit breaker by name"""
        return self.circuit_breakers.get(name)
    
    def circuit_breaker(self, name: str, **config_kwargs):
        """Decorator for circuit breaker protection"""
        def decorator(func: Callable):
            # Create circuit breaker if it doesn't exist
            if name not in self.circuit_breakers:
                config = CircuitBreakerConfig(name=name, **config_kwargs)
                self.create_circuit_breaker(config)
            
            @functools.wraps(func)
            async def wrapper(*args, **kwargs):
                cb = self.circuit_breakers[name]
                return await cb.call(func, *args, **kwargs)
            
            return wrapper
        return decorator
    
    async def protected_call(self, name: str, func: Callable, *args, **kwargs) -> Any:
        """Make a protected call using circuit breaker"""
        if name not in self.circuit_breakers:
            raise ValueError(f"Circuit breaker '{name}' not found")
        
        circuit_breaker = self.circuit_breakers[name]
        return await circuit_breaker.call(func, *args, **kwargs)
    
    async def start_monitoring(self):
        """Start monitoring circuit breakers"""
        if self.monitoring_task is None and self.monitoring_enabled:
            self.monitoring_task = asyncio.create_task(self._monitoring_loop())
            logger.info("📊 Circuit breaker monitoring started")
    
    async def stop_monitoring(self):
        """Stop monitoring circuit breakers"""
        self.monitoring_enabled = False
        if self.monitoring_task:
            self.monitoring_task.cancel()
            try:
                await self.monitoring_task
            except asyncio.CancelledError:
                pass
            self.monitoring_task = None
        
        if self.redis_client:
            await self.redis_client.close()
        
        logger.info("📊 Circuit breaker monitoring stopped")
    
    async def _monitoring_loop(self):
        """Monitor circuit breakers and store metrics"""
        while self.monitoring_enabled:
            try:
                # Collect metrics from all circuit breakers
                all_metrics = {}
                for name, cb in self.circuit_breakers.items():
                    metrics = cb.get_metrics()
                    all_metrics[name] = asdict(metrics)
                    
                    # Convert datetime objects to ISO strings
                    for key, value in all_metrics[name].items():
                        if isinstance(value, datetime):
                            all_metrics[name][key] = value.isoformat() if value else None
                        elif isinstance(value, CircuitBreakerState):
                            all_metrics[name][key] = value.value
                
                # Store metrics in Redis
                if self.redis_client and all_metrics:
                    metrics_data = {
                        'timestamp': datetime.now().isoformat(),
                        'circuit_breakers': all_metrics
                    }
                    
                    await self.redis_client.set(
                        'circuit_breaker:metrics',
                        json.dumps(metrics_data)
                    )
                    
                    # Store metrics history
                    await self.redis_client.lpush(
                        'circuit_breaker:metrics_history',
                        json.dumps(metrics_data)
                    )
                    await self.redis_client.ltrim('circuit_breaker:metrics_history', 0, 999)
                
                await asyncio.sleep(30)  # Monitor every 30 seconds
                
            except Exception as e:
                logger.error(f"❌ Error in monitoring loop: {str(e)}")
                await asyncio.sleep(10)
    
    def get_all_metrics(self) -> Dict[str, CircuitBreakerMetrics]:
        """Get metrics for all circuit breakers"""
        return {name: cb.get_metrics() for name, cb in self.circuit_breakers.items()}
    
    def get_healthy_circuit_breakers(self) -> List[str]:
        """Get list of healthy (closed) circuit breakers"""
        return [
            name for name, cb in self.circuit_breakers.items()
            if cb.state == CircuitBreakerState.CLOSED
        ]
    
    def get_unhealthy_circuit_breakers(self) -> List[str]:
        """Get list of unhealthy (open/half-open) circuit breakers"""
        return [
            name for name, cb in self.circuit_breakers.items()
            if cb.state in [CircuitBreakerState.OPEN, CircuitBreakerState.HALF_OPEN]
        ]
    
    def reset_circuit_breaker(self, name: str) -> bool:
        """Reset a specific circuit breaker"""
        if name in self.circuit_breakers:
            self.circuit_breakers[name].reset()
            logger.info(f"🔄 Reset circuit breaker: {name}")
            return True
        return False
    
    def reset_all_circuit_breakers(self):
        """Reset all circuit breakers"""
        for name, cb in self.circuit_breakers.items():
            cb.reset()
        logger.info("🔄 Reset all circuit breakers")
    
    async def get_service_health(self) -> Dict[str, Any]:
        """Get circuit breaker manager health status"""
        total_breakers = len(self.circuit_breakers)
        healthy_breakers = len(self.get_healthy_circuit_breakers())
        unhealthy_breakers = len(self.get_unhealthy_circuit_breakers())
        
        return {
            'service': self.service_name,
            'version': self.version,
            'total_circuit_breakers': total_breakers,
            'healthy_circuit_breakers': healthy_breakers,
            'unhealthy_circuit_breakers': unhealthy_breakers,
            'health_percentage': (healthy_breakers / total_breakers * 100) if total_breakers > 0 else 100,
            'monitoring_enabled': self.monitoring_enabled,
            'redis_connected': self.redis_client is not None,
            'timestamp': datetime.now().isoformat()
        }
    
    def create_default_circuit_breakers(self):
        """Create default circuit breakers for common services"""
        default_configs = [
            CircuitBreakerConfig(
                name="database",
                failure_threshold=5,
                recovery_timeout=60,
                timeout=10.0,
                failure_rate_threshold=0.5
            ),
            CircuitBreakerConfig(
                name="external_api",
                failure_threshold=3,
                recovery_timeout=30,
                timeout=15.0,
                failure_rate_threshold=0.6
            ),
            CircuitBreakerConfig(
                name="cache",
                failure_threshold=10,
                recovery_timeout=20,
                timeout=5.0,
                failure_rate_threshold=0.7
            ),
            CircuitBreakerConfig(
                name="message_queue",
                failure_threshold=5,
                recovery_timeout=45,
                timeout=20.0,
                failure_rate_threshold=0.5
            )
        ]
        
        for config in default_configs:
            self.create_circuit_breaker(config)
        
        logger.info(f"🔧 Created {len(default_configs)} default circuit breakers")

# Service instance
circuit_breaker_manager = CircuitBreakerManager()

# Example functions to test circuit breaker
async def unreliable_service():
    """Simulate an unreliable service"""
    import random
    
    if random.random() < 0.3:  # 30% failure rate
        raise Exception("Service unavailable")
    
    await asyncio.sleep(0.1)  # Simulate work
    return "Success"

async def slow_service():
    """Simulate a slow service"""
    await asyncio.sleep(5)  # This will timeout
    return "Slow response"

# Example usage
async def main():
    """Example usage of the circuit breaker manager"""
    try:
        # Initialize service
        await circuit_breaker_manager.initialize()
        
        # Create default circuit breakers
        circuit_breaker_manager.create_default_circuit_breakers()
        
        # Create a custom circuit breaker
        config = CircuitBreakerConfig(
            name="test_service",
            failure_threshold=3,
            recovery_timeout=30,
            timeout=2.0
        )
        circuit_breaker_manager.create_circuit_breaker(config)
        
        # Test the circuit breaker with unreliable service
        print("Testing circuit breaker with unreliable service...")
        for i in range(10):
            try:
                result = await circuit_breaker_manager.protected_call(
                    "test_service", unreliable_service
                )
                print(f"Call {i+1}: {result}")
            except Exception as e:
                print(f"Call {i+1}: Failed - {str(e)}")
            
            await asyncio.sleep(1)
        
        # Test with decorator
        @circuit_breaker_manager.circuit_breaker("decorated_service", timeout=3.0)
        async def decorated_unreliable_service():
            return await unreliable_service()
        
        print("\nTesting with decorator...")
        for i in range(5):
            try:
                result = await decorated_unreliable_service()
                print(f"Decorated call {i+1}: {result}")
            except Exception as e:
                print(f"Decorated call {i+1}: Failed - {str(e)}")
            
            await asyncio.sleep(1)
        
        # Get metrics
        print("\nCircuit breaker metrics:")
        all_metrics = circuit_breaker_manager.get_all_metrics()
        for name, metrics in all_metrics.items():
            print(f"{name}: {metrics.state.value} "
                  f"(failures: {metrics.failure_count}, "
                  f"successes: {metrics.success_count}, "
                  f"rate: {metrics.failure_rate:.2f})")
        
        # Service health
        health = await circuit_breaker_manager.get_service_health()
        print(f"\nService health: {json.dumps(health, indent=2)}")
        
        # Wait a bit to see monitoring in action
        await asyncio.sleep(10)
        
    except Exception as e:
        logger.error(f"❌ Error in main: {str(e)}")
    finally:
        await circuit_breaker_manager.stop_monitoring()

if __name__ == "__main__":
    asyncio.run(main())