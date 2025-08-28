"""
Circuit Breaker - Fault Tolerance System

Advanced circuit breaker implementation with intelligent failure detection,
recovery mechanisms, and service health monitoring for microservices resilience.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️  CRITICAL LEGAL NOTICE:
This code and architectural design are the exclusive intellectual property of Fahed Mlaiel.
Unauthorized use, copying, distribution, or commercialization is strictly prohibited.
"""

import asyncio
import logging
import time
from typing import Dict, List, Optional, Any, Callable, Union
from dataclasses import dataclass
from enum import Enum
from datetime import datetime, timedelta
import statistics

logger = logging.getLogger(__name__)


class CircuitState(str, Enum):
    """Circuit breaker states"""
    CLOSED = "closed"      # Normal operation
    OPEN = "open"         # Blocking requests
    HALF_OPEN = "half_open"  # Testing recovery


@dataclass
class CircuitBreakerConfig:
    """Circuit breaker configuration"""
    failure_threshold: int = 5
    recovery_timeout: int = 60
    success_threshold: int = 3
    timeout: float = 30.0
    expected_exception: Optional[type] = None
    
    # Advanced settings
    slow_call_rate_threshold: float = 0.5
    slow_call_duration_threshold: float = 10.0
    minimum_number_of_calls: int = 10
    sliding_window_size: int = 100
    permitted_number_of_calls_in_half_open_state: int = 3


@dataclass
class CallResult:
    """Individual call result"""
    success: bool
    duration: float
    error: Optional[str] = None
    timestamp: float = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = time.time()


class CircuitBreaker:
    """
    Enterprise Circuit Breaker
    
    Features:
    - Multiple failure detection strategies
    - Sliding window failure rate calculation
    - Slow call detection
    - Automatic recovery testing
    - Service health monitoring
    - Configurable thresholds and timeouts
    - Event-driven notifications
    """
    
    def __init__(self, config: Optional[CircuitBreakerConfig] = None):
        """Initialize circuit breaker"""
        self.config = config or CircuitBreakerConfig()
        
        # State management
        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.success_count = 0
        self.last_failure_time = 0
        self.next_attempt_time = 0
        
        # Call history for sliding window
        self.call_history: List[CallResult] = []
        self.max_history_size = self.config.sliding_window_size
        
        # Statistics
        self.total_calls = 0
        self.total_failures = 0
        self.total_timeouts = 0
        self.total_slow_calls = 0
        
        # Event callbacks
        self.on_state_change: Optional[Callable[[CircuitState, CircuitState], None]] = None
        self.on_call_success: Optional[Callable[[float], None]] = None
        self.on_call_failure: Optional[Callable[[str], None]] = None
        
        logger.info(f"Circuit breaker initialized with config: {self.config.__dict__}")
    
    async def call(self, func: Callable, *args, **kwargs) -> Any:
        """
        Execute function with circuit breaker protection
        
        Args:
            func: Function to execute
            *args: Function arguments
            **kwargs: Function keyword arguments
            
        Returns:
            Function result
            
        Raises:
            CircuitBreakerOpenError: If circuit is open
            Original exception: If function fails and circuit allows it
        """
        # Check if call is permitted
        if not self._is_call_permitted():
            raise CircuitBreakerOpenError("Circuit breaker is OPEN")
        
        start_time = time.time()
        
        try:
            # Execute function with timeout
            if asyncio.iscoroutinefunction(func):
                result = await asyncio.wait_for(
                    func(*args, **kwargs),
                    timeout=self.config.timeout
                )
            else:
                result = func(*args, **kwargs)
            
            # Record successful call
            call_duration = time.time() - start_time
            await self._record_success(call_duration)
            
            return result
            
        except asyncio.TimeoutError as e:
            call_duration = time.time() - start_time
            await self._record_failure("Timeout", call_duration)
            self.total_timeouts += 1
            raise
        
        except Exception as e:
            call_duration = time.time() - start_time
            
            # Check if this is an expected exception
            if (self.config.expected_exception and 
                isinstance(e, self.config.expected_exception)):
                await self._record_failure(str(e), call_duration)
            else:
                # Unexpected exception - don't count as circuit breaker failure
                await self._record_success(call_duration)
            
            raise
    
    def _is_call_permitted(self) -> bool:
        """Check if call is permitted based on current state"""
        current_time = time.time()
        
        if self.state == CircuitState.CLOSED:
            return True
        
        elif self.state == CircuitState.OPEN:
            # Check if recovery timeout has passed
            if current_time >= self.next_attempt_time:
                self._transition_to_half_open()
                return True
            return False
        
        elif self.state == CircuitState.HALF_OPEN:
            # Allow limited number of calls for testing
            return self.success_count < self.config.permitted_number_of_calls_in_half_open_state
        
        return False
    
    async def _record_success(self, duration: float):
        """Record successful call"""
        self.total_calls += 1
        
        # Add to call history
        call_result = CallResult(success=True, duration=duration)
        self._add_call_to_history(call_result)
        
        # Check if call was slow
        if duration > self.config.slow_call_duration_threshold:
            self.total_slow_calls += 1
        
        if self.state == CircuitState.HALF_OPEN:
            self.success_count += 1
            
            # Check if we should transition to closed
            if self.success_count >= self.config.success_threshold:
                self._transition_to_closed()
        
        # Reset failure count on success (if not in half-open)
        if self.state == CircuitState.CLOSED:
            self.failure_count = 0
        
        # Trigger callback
        if self.on_call_success:
            self.on_call_success(duration)
    
    async def _record_failure(self, error: str, duration: float):
        """Record failed call"""
        self.total_calls += 1
        self.total_failures += 1
        self.last_failure_time = time.time()
        
        # Add to call history
        call_result = CallResult(success=False, duration=duration, error=error)
        self._add_call_to_history(call_result)
        
        if self.state == CircuitState.CLOSED:
            self.failure_count += 1
            
            # Check if we should open the circuit
            if self._should_open_circuit():
                self._transition_to_open()
        
        elif self.state == CircuitState.HALF_OPEN:
            # Immediately transition back to open on failure
            self._transition_to_open()
        
        # Trigger callback
        if self.on_call_failure:
            self.on_call_failure(error)
    
    def _add_call_to_history(self, call_result: CallResult):
        """Add call result to sliding window history"""
        self.call_history.append(call_result)
        
        # Maintain sliding window size
        if len(self.call_history) > self.max_history_size:
            self.call_history = self.call_history[-self.max_history_size:]
    
    def _should_open_circuit(self) -> bool:
        """Determine if circuit should be opened based on failure criteria"""
        # Simple failure count threshold
        if self.failure_count >= self.config.failure_threshold:
            return True
        
        # Advanced criteria using sliding window
        if len(self.call_history) >= self.config.minimum_number_of_calls:
            # Calculate failure rate
            recent_calls = self.call_history[-self.config.minimum_number_of_calls:]
            failure_rate = sum(1 for call in recent_calls if not call.success) / len(recent_calls)
            
            if failure_rate >= 0.5:  # 50% failure rate
                return True
            
            # Check slow call rate
            slow_call_rate = sum(
                1 for call in recent_calls 
                if call.duration > self.config.slow_call_duration_threshold
            ) / len(recent_calls)
            
            if slow_call_rate >= self.config.slow_call_rate_threshold:
                return True
        
        return False
    
    def _transition_to_open(self):
        """Transition circuit to OPEN state"""
        old_state = self.state
        self.state = CircuitState.OPEN
        self.next_attempt_time = time.time() + self.config.recovery_timeout
        self.failure_count = 0
        self.success_count = 0
        
        logger.warning(f"Circuit breaker transitioned from {old_state} to OPEN")
        
        if self.on_state_change:
            self.on_state_change(old_state, self.state)
    
    def _transition_to_half_open(self):
        """Transition circuit to HALF_OPEN state"""
        old_state = self.state
        self.state = CircuitState.HALF_OPEN
        self.success_count = 0
        
        logger.info(f"Circuit breaker transitioned from {old_state} to HALF_OPEN")
        
        if self.on_state_change:
            self.on_state_change(old_state, self.state)
    
    def _transition_to_closed(self):
        """Transition circuit to CLOSED state"""
        old_state = self.state
        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.success_count = 0
        
        logger.info(f"Circuit breaker transitioned from {old_state} to CLOSED")
        
        if self.on_state_change:
            self.on_state_change(old_state, self.state)
    
    def get_state(self) -> CircuitState:
        """Get current circuit state"""
        return self.state
    
    def get_failure_rate(self) -> float:
        """Get current failure rate from sliding window"""
        if not self.call_history:
            return 0.0
        
        failures = sum(1 for call in self.call_history if not call.success)
        return failures / len(self.call_history)
    
    def get_slow_call_rate(self) -> float:
        """Get current slow call rate from sliding window"""
        if not self.call_history:
            return 0.0
        
        slow_calls = sum(
            1 for call in self.call_history 
            if call.duration > self.config.slow_call_duration_threshold
        )
        return slow_calls / len(self.call_history)
    
    def get_average_response_time(self) -> float:
        """Get average response time from sliding window"""
        if not self.call_history:
            return 0.0
        
        durations = [call.duration for call in self.call_history]
        return statistics.mean(durations)
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get comprehensive circuit breaker metrics"""
        current_time = time.time()
        
        metrics = {
            "state": self.state.value,
            "total_calls": self.total_calls,
            "total_failures": self.total_failures,
            "total_timeouts": self.total_timeouts,
            "total_slow_calls": self.total_slow_calls,
            "failure_count": self.failure_count,
            "success_count": self.success_count,
            "failure_rate": self.get_failure_rate(),
            "slow_call_rate": self.get_slow_call_rate(),
            "average_response_time": self.get_average_response_time(),
            "last_failure_time": self.last_failure_time,
            "next_attempt_time": self.next_attempt_time,
            "time_until_next_attempt": max(0, self.next_attempt_time - current_time),
            "call_history_size": len(self.call_history),
            "config": {
                "failure_threshold": self.config.failure_threshold,
                "recovery_timeout": self.config.recovery_timeout,
                "success_threshold": self.config.success_threshold,
                "timeout": self.config.timeout,
                "slow_call_duration_threshold": self.config.slow_call_duration_threshold,
                "slow_call_rate_threshold": self.config.slow_call_rate_threshold
            }
        }
        
        return metrics
    
    def reset(self):
        """Reset circuit breaker to initial state"""
        old_state = self.state
        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.success_count = 0
        self.last_failure_time = 0
        self.next_attempt_time = 0
        self.call_history.clear()
        
        logger.info(f"Circuit breaker reset from {old_state} to CLOSED")
        
        if self.on_state_change and old_state != self.state:
            self.on_state_change(old_state, self.state)
    
    def force_open(self):
        """Force circuit breaker to OPEN state"""
        self._transition_to_open()
    
    def force_close(self):
        """Force circuit breaker to CLOSED state"""
        self._transition_to_closed()
    
    def set_event_callback(
        self, 
        event_type: str, 
        callback: Callable
    ):
        """Set event callback"""
        if event_type == "state_change":
            self.on_state_change = callback
        elif event_type == "call_success":
            self.on_call_success = callback
        elif event_type == "call_failure":
            self.on_call_failure = callback
        else:
            logger.warning(f"Unknown event type: {event_type}")


class CircuitBreakerOpenError(Exception):
    """Exception raised when circuit breaker is open"""
    pass


class CircuitBreakerRegistry:
    """
    Registry for managing multiple circuit breakers
    
    Useful for having separate circuit breakers for different services
    or operations with different failure characteristics.
    """
    
    def __init__(self):
        """Initialize circuit breaker registry"""
        self.circuit_breakers: Dict[str, CircuitBreaker] = {}
        self.default_config = CircuitBreakerConfig()
        
        logger.info("Circuit breaker registry initialized")
    
    def get_circuit_breaker(
        self, 
        name: str, 
        config: Optional[CircuitBreakerConfig] = None
    ) -> CircuitBreaker:
        """Get or create circuit breaker by name"""
        if name not in self.circuit_breakers:
            breaker_config = config or self.default_config
            self.circuit_breakers[name] = CircuitBreaker(breaker_config)
            logger.info(f"Created circuit breaker: {name}")
        
        return self.circuit_breakers[name]
    
    def remove_circuit_breaker(self, name: str) -> bool:
        """Remove circuit breaker by name"""
        if name in self.circuit_breakers:
            del self.circuit_breakers[name]
            logger.info(f"Removed circuit breaker: {name}")
            return True
        return False
    
    def get_all_metrics(self) -> Dict[str, Dict[str, Any]]:
        """Get metrics for all circuit breakers"""
        return {
            name: breaker.get_metrics() 
            for name, breaker in self.circuit_breakers.items()
        }
    
    def reset_all(self):
        """Reset all circuit breakers"""
        for name, breaker in self.circuit_breakers.items():
            breaker.reset()
            logger.info(f"Reset circuit breaker: {name}")
    
    def get_registry_stats(self) -> Dict[str, Any]:
        """Get registry statistics"""
        stats = {
            "total_circuit_breakers": len(self.circuit_breakers),
            "states": {"closed": 0, "open": 0, "half_open": 0},
            "total_calls": 0,
            "total_failures": 0
        }
        
        for breaker in self.circuit_breakers.values():
            metrics = breaker.get_metrics()
            stats["states"][metrics["state"]] += 1
            stats["total_calls"] += metrics["total_calls"]
            stats["total_failures"] += metrics["total_failures"]
        
        return stats


# Global circuit breaker registry
circuit_breaker_registry = CircuitBreakerRegistry()
