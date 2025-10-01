#!/usr/bin/env python3
"""Circuit Breaker Manager - Resilience Pattern Enterprise
=========================================================

Advanced circuit breaker implementation for IA Chéries platform error handling.
Provides adaptive circuit breakers with intelligent failure detection,
state management, and integration with existing error handling infrastructure.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel - All Rights Reserved

⚠️ PROPRIÉTÉ INTELLECTUELLE EXCLUSIVE - FAHED MLAIEL ⚠️
Utilisation non autorisée strictement interdite.
Contact: mlaiel@live.de
"""

import asyncio
import logging
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Callable, Union
from dataclasses import dataclass, field
from enum import Enum
import json
import hashlib
from collections import defaultdict, deque

from .error_handler import ErrorHandler, ErrorSeverity, ErrorCategory

logger = logging.getLogger(__name__)


class CircuitState(Enum):
    """Circuit breaker state enumeration."""
    CLOSED = "closed"      # Normal operation
    OPEN = "open"          # Circuit is open, rejecting calls
    HALF_OPEN = "half_open"  # Testing if service is recovered


@dataclass
class CircuitBreakerConfig:
    """Circuit breaker configuration."""
    failure_threshold: int = 5
    recovery_timeout: int = 30
    success_threshold: int = 3
    request_volume_threshold: int = 10
    error_percentage_threshold: float = 50.0
    sliding_window_size: int = 100
    min_requests_for_evaluation: int = 5


@dataclass
class CircuitBreakerMetrics:
    """Circuit breaker metrics tracking."""
    total_requests: int = 0
    failed_requests: int = 0
    successful_requests: int = 0
    circuit_open_count: int = 0
    last_failure_time: Optional[datetime] = None
    last_success_time: Optional[datetime] = None
    average_response_time: float = 0.0
    failure_rate: float = 0.0


class CircuitBreakerException(Exception):
    """Exception raised when circuit breaker is open."""
    pass


class CircuitBreakerManager:
    """Circuit breaker enterprise avec intelligent failure detection."""
    
    def __init__(self, error_handler: Optional[ErrorHandler] = None):
        """Initialize circuit breaker manager.
        
        Args:
            error_handler: Optional error handler for integration
        """
        self.error_handler = error_handler
        self.circuit_breakers: Dict[str, 'CircuitBreaker'] = {}
        self.global_config = CircuitBreakerConfig()
        self.logger = logger
        
    def get_circuit_breaker(
        self,
        service_name: str,
        config: Optional[CircuitBreakerConfig] = None
    ) -> 'CircuitBreaker':
        """Get or create circuit breaker for service.
        
        Args:
            service_name: Name of the service
            config: Optional specific configuration
            
        Returns:
            CircuitBreaker instance
        """
        if service_name not in self.circuit_breakers:
            circuit_config = config or self.global_config
            self.circuit_breakers[service_name] = CircuitBreaker(
                service_name=service_name,
                config=circuit_config,
                error_handler=self.error_handler
            )
            
        return self.circuit_breakers[service_name]
    
    async def adaptive_circuit_breaker_implementation(self) -> Dict[str, Any]:
        """Adaptive circuit breaker implementation with intelligent adjustment."""
        adaptive_results = {}
        
        for service_name, circuit_breaker in self.circuit_breakers.items():
            metrics = circuit_breaker.get_metrics()
            
            # Adaptive threshold adjustment based on historical data
            if metrics.total_requests > 100:
                failure_rate = metrics.failure_rate
                
                # Adjust failure threshold based on service reliability
                if failure_rate < 5.0:  # Very reliable service
                    circuit_breaker.config.failure_threshold = max(
                        circuit_breaker.config.failure_threshold + 1, 10
                    )
                elif failure_rate > 20.0:  # Unreliable service
                    circuit_breaker.config.failure_threshold = max(
                        circuit_breaker.config.failure_threshold - 1, 3
                    )
            
            adaptive_results[service_name] = {
                "current_state": circuit_breaker.state.value,
                "failure_threshold": circuit_breaker.config.failure_threshold,
                "failure_rate": metrics.failure_rate,
                "total_requests": metrics.total_requests,
                "adaptation_applied": True
            }
        
        return adaptive_results
    
    async def failure_threshold_management(self) -> Dict[str, Any]:
        """Manage failure thresholds across all circuit breakers."""
        threshold_stats = {}
        
        for service_name, circuit_breaker in self.circuit_breakers.items():
            metrics = circuit_breaker.get_metrics()
            config = circuit_breaker.config
            
            threshold_stats[service_name] = {
                "current_threshold": config.failure_threshold,
                "current_failures": metrics.failed_requests,
                "threshold_ratio": metrics.failed_requests / max(config.failure_threshold, 1),
                "recommended_threshold": await self._calculate_optimal_threshold(metrics),
                "threshold_effectiveness": await self._evaluate_threshold_effectiveness(circuit_breaker)
            }
        
        return threshold_stats
    
    async def half_open_state_monitoring(self) -> Dict[str, Any]:
        """Monitor half-open state performance across circuit breakers."""
        half_open_stats = {}
        
        for service_name, circuit_breaker in self.circuit_breakers.items():
            if circuit_breaker.state == CircuitState.HALF_OPEN:
                half_open_stats[service_name] = {
                    "time_in_half_open": (
                        datetime.now() - circuit_breaker.last_state_change
                    ).total_seconds(),
                    "success_count": circuit_breaker.consecutive_successes,
                    "required_successes": circuit_breaker.config.success_threshold,
                    "progress_percentage": (
                        circuit_breaker.consecutive_successes / 
                        circuit_breaker.config.success_threshold * 100
                    )
                }
        
        return half_open_stats
    
    async def circuit_breaker_metrics_collection(self) -> Dict[str, Any]:
        """Collect comprehensive metrics from all circuit breakers."""
        all_metrics = {
            "global_stats": {
                "total_circuit_breakers": len(self.circuit_breakers),
                "open_circuits": sum(
                    1 for cb in self.circuit_breakers.values() 
                    if cb.state == CircuitState.OPEN
                ),
                "half_open_circuits": sum(
                    1 for cb in self.circuit_breakers.values() 
                    if cb.state == CircuitState.HALF_OPEN
                ),
                "closed_circuits": sum(
                    1 for cb in self.circuit_breakers.values() 
                    if cb.state == CircuitState.CLOSED
                )
            },
            "service_metrics": {}
        }
        
        for service_name, circuit_breaker in self.circuit_breakers.items():
            metrics = circuit_breaker.get_metrics()
            all_metrics["service_metrics"][service_name] = {
                "state": circuit_breaker.state.value,
                "total_requests": metrics.total_requests,
                "failed_requests": metrics.failed_requests,
                "successful_requests": metrics.successful_requests,
                "failure_rate": metrics.failure_rate,
                "average_response_time": metrics.average_response_time,
                "circuit_open_count": metrics.circuit_open_count,
                "last_failure": metrics.last_failure_time.isoformat() if metrics.last_failure_time else None,
                "last_success": metrics.last_success_time.isoformat() if metrics.last_success_time else None
            }
        
        return all_metrics
    
    async def multi_service_circuit_coordination(self) -> Dict[str, Any]:
        """Coordinate circuit breakers across multiple services."""
        coordination_results = {
            "cascading_failure_prevention": {},
            "service_dependencies": {},
            "coordinated_actions": []
        }
        
        # Analyze service dependencies and potential cascading failures
        for service_name, circuit_breaker in self.circuit_breakers.items():
            if circuit_breaker.state == CircuitState.OPEN:
                # Identify dependent services that might be affected
                dependent_services = await self._identify_dependent_services(service_name)
                
                coordination_results["cascading_failure_prevention"][service_name] = {
                    "dependent_services": dependent_services,
                    "preventive_actions": await self._generate_preventive_actions(
                        service_name, dependent_services
                    )
                }
        
        return coordination_results
    
    async def circuit_breaker_configuration_management(self) -> Dict[str, Any]:
        """Manage circuit breaker configurations dynamically."""
        config_management = {
            "current_configurations": {},
            "optimization_suggestions": {},
            "configuration_changes": []
        }
        
        for service_name, circuit_breaker in self.circuit_breakers.items():
            config = circuit_breaker.config
            metrics = circuit_breaker.get_metrics()
            
            config_management["current_configurations"][service_name] = {
                "failure_threshold": config.failure_threshold,
                "recovery_timeout": config.recovery_timeout,
                "success_threshold": config.success_threshold,
                "error_percentage_threshold": config.error_percentage_threshold
            }
            
            # Generate optimization suggestions
            suggestions = await self._generate_config_suggestions(metrics, config)
            config_management["optimization_suggestions"][service_name] = suggestions
        
        return config_management
    
    async def _calculate_optimal_threshold(self, metrics: CircuitBreakerMetrics) -> int:
        """Calculate optimal failure threshold based on metrics."""
        if metrics.total_requests < 50:
            return 5  # Default for low traffic
        
        failure_rate = metrics.failure_rate
        
        if failure_rate < 1.0:
            return min(10, max(7, int(metrics.total_requests * 0.1)))
        elif failure_rate < 5.0:
            return 7
        elif failure_rate < 10.0:
            return 5
        else:
            return 3
    
    async def _evaluate_threshold_effectiveness(self, circuit_breaker: 'CircuitBreaker') -> float:
        """Evaluate effectiveness of current threshold setting."""
        metrics = circuit_breaker.get_metrics()
        
        if metrics.total_requests == 0:
            return 0.0
        
        # Calculate effectiveness based on prevention of cascading failures
        prevented_failures = max(0, metrics.failed_requests - circuit_breaker.config.failure_threshold)
        effectiveness = 1.0 - (prevented_failures / metrics.total_requests)
        
        return max(0.0, min(1.0, effectiveness))
    
    async def _identify_dependent_services(self, service_name: str) -> List[str]:
        """Identify services that depend on the given service."""
        # In a real implementation, this would analyze service dependency graph
        # For now, return empty list as placeholder
        return []
    
    async def _generate_preventive_actions(self, service_name: str, dependent_services: List[str]) -> List[str]:
        """Generate preventive actions for dependent services."""
        actions = []
        
        if dependent_services:
            actions.append(f"Increase timeout for services depending on {service_name}")
            actions.append(f"Enable fallback mechanisms for {', '.join(dependent_services)}")
            actions.append(f"Reduce request rate to {service_name} from dependent services")
        
        return actions
    
    async def _generate_config_suggestions(
        self, 
        metrics: CircuitBreakerMetrics, 
        config: CircuitBreakerConfig
    ) -> List[str]:
        """Generate configuration optimization suggestions."""
        suggestions = []
        
        if metrics.failure_rate > 30 and config.failure_threshold > 3:
            suggestions.append("Consider reducing failure threshold for faster failure detection")
        
        if metrics.failure_rate < 1 and config.failure_threshold < 8:
            suggestions.append("Consider increasing failure threshold for more tolerance")
        
        if metrics.circuit_open_count > 10:
            suggestions.append("Consider increasing recovery timeout")
        
        return suggestions


class CircuitBreaker:
    """Individual circuit breaker implementation."""
    
    def __init__(
        self,
        service_name: str,
        config: CircuitBreakerConfig,
        error_handler: Optional[ErrorHandler] = None
    ):
        """Initialize circuit breaker.
        
        Args:
            service_name: Name of the service
            config: Circuit breaker configuration
            error_handler: Optional error handler for integration
        """
        self.service_name = service_name
        self.config = config
        self.error_handler = error_handler
        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.consecutive_successes = 0
        self.last_failure_time: Optional[datetime] = None
        self.last_success_time: Optional[datetime] = None
        self.last_state_change = datetime.now()
        self.request_history = deque(maxlen=config.sliding_window_size)
        self.metrics = CircuitBreakerMetrics()
        self.response_times = deque(maxlen=100)
        
    async def call(self, func: Callable, *args, **kwargs) -> Any:
        """Execute function with circuit breaker protection.
        
        Args:
            func: Function to execute
            *args: Function arguments
            **kwargs: Function keyword arguments
            
        Returns:
            Function result
            
        Raises:
            CircuitBreakerException: When circuit is open
        """
        # Check circuit state
        if self.state == CircuitState.OPEN:
            if self._should_attempt_reset():
                self.state = CircuitState.HALF_OPEN
                self.last_state_change = datetime.now()
                self.consecutive_successes = 0
            else:
                raise CircuitBreakerException(
                    f"Circuit breaker open for service: {self.service_name}"
                )
        
        start_time = time.time()
        
        try:
            result = await func(*args, **kwargs) if asyncio.iscoroutinefunction(func) else func(*args, **kwargs)
            execution_time = time.time() - start_time
            await self._on_success(execution_time)
            return result
            
        except Exception as e:
            execution_time = time.time() - start_time
            await self._on_failure(e, execution_time)
            raise
    
    def _should_attempt_reset(self) -> bool:
        """Check if circuit should attempt reset to half-open."""
        if self.last_failure_time is None:
            return True
        
        time_since_failure = (datetime.now() - self.last_failure_time).total_seconds()
        return time_since_failure >= self.config.recovery_timeout
    
    async def _on_success(self, execution_time: float):
        """Handle successful execution."""
        self.metrics.total_requests += 1
        self.metrics.successful_requests += 1
        self.last_success_time = datetime.now()
        self.response_times.append(execution_time)
        
        # Update average response time
        self.metrics.average_response_time = sum(self.response_times) / len(self.response_times)
        
        # Record in sliding window
        self.request_history.append({"success": True, "timestamp": datetime.now()})
        
        if self.state == CircuitState.HALF_OPEN:
            self.consecutive_successes += 1
            if self.consecutive_successes >= self.config.success_threshold:
                self.state = CircuitState.CLOSED
                self.last_state_change = datetime.now()
                self.failure_count = 0
                self.consecutive_successes = 0
        elif self.state == CircuitState.CLOSED:
            # Reduce failure count on success
            self.failure_count = max(0, self.failure_count - 1)
        
        # Update failure rate
        self._update_failure_rate()
    
    async def _on_failure(self, exception: Exception, execution_time: float):
        """Handle failed execution."""
        self.metrics.total_requests += 1
        self.metrics.failed_requests += 1
        self.failure_count += 1
        self.last_failure_time = datetime.now()
        self.response_times.append(execution_time)
        
        # Update average response time
        self.metrics.average_response_time = sum(self.response_times) / len(self.response_times)
        
        # Record in sliding window
        self.request_history.append({"success": False, "timestamp": datetime.now()})
        
        # Integrate with error handler if available
        if self.error_handler:
            await self.error_handler.handle_error(
                exception=exception,
                context={
                    "service": self.service_name,
                    "circuit_breaker_state": self.state.value,
                    "failure_count": self.failure_count,
                    "execution_time": execution_time
                },
                severity=ErrorSeverity.HIGH if self.failure_count > self.config.failure_threshold else ErrorSeverity.MEDIUM,
                category=ErrorCategory.INTEGRATION_DOWN
            )
        
        # Check if circuit should open
        if (self.failure_count >= self.config.failure_threshold or 
            self.state == CircuitState.HALF_OPEN):
            self.state = CircuitState.OPEN
            self.last_state_change = datetime.now()
            self.metrics.circuit_open_count += 1
            self.consecutive_successes = 0
        
        # Update failure rate
        self._update_failure_rate()
    
    def _update_failure_rate(self):
        """Update current failure rate based on sliding window."""
        if not self.request_history:
            self.metrics.failure_rate = 0.0
            return
        
        recent_requests = [
            req for req in self.request_history
            if (datetime.now() - req["timestamp"]).total_seconds() < 300  # Last 5 minutes
        ]
        
        if not recent_requests:
            self.metrics.failure_rate = 0.0
            return
        
        failed_requests = sum(1 for req in recent_requests if not req["success"])
        self.metrics.failure_rate = (failed_requests / len(recent_requests)) * 100
    
    def get_metrics(self) -> CircuitBreakerMetrics:
        """Get current circuit breaker metrics."""
        return self.metrics
    
    def get_state(self) -> CircuitState:
        """Get current circuit breaker state."""
        return self.state
    
    def reset(self):
        """Reset circuit breaker to closed state."""
        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.consecutive_successes = 0
        self.last_state_change = datetime.now()
        self.request_history.clear()