"""Circuit Breaker - Circuit Breaker Pattern Implementation
========================================================

Implements circuit breaker pattern for integration resilience.
Provides automatic failure detection and recovery management.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
import time
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import json


class CircuitState(Enum):
    """Circuit breaker states."""
    CLOSED = "closed"      # Normal operation
    OPEN = "open"          # Blocking requests due to failures
    HALF_OPEN = "half_open"  # Testing if service has recovered


@dataclass
class CircuitConfig:
    """Circuit breaker configuration."""
    integration_name: str
    failure_threshold: int = 5          # Number of failures to open circuit
    recovery_timeout: int = 60          # Seconds before attempting recovery
    success_threshold: int = 3          # Successes needed to close circuit from half-open
    timeout: int = 30                   # Request timeout in seconds
    volume_threshold: int = 10          # Minimum requests before evaluating failures
    error_percentage_threshold: float = 50.0  # Error percentage to open circuit
    slow_call_duration_threshold: float = 5.0  # Slow call threshold in seconds
    slow_call_rate_threshold: float = 50.0     # Slow call percentage threshold
    max_wait_duration_in_half_open: int = 60   # Max time in half-open state
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class CircuitMetrics:
    """Circuit breaker metrics."""
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    slow_requests: int = 0
    rejected_requests: int = 0
    average_response_time: float = 0.0
    success_rate: float = 100.0
    failure_rate: float = 0.0
    slow_call_rate: float = 0.0
    last_failure_time: Optional[datetime] = None
    last_success_time: Optional[datetime] = None


@dataclass
class CircuitCall:
    """Circuit breaker call record."""
    timestamp: datetime
    duration: float
    success: bool
    error: Optional[str] = None


class CircuitBreaker:
    """Circuit breaker implementation for integration resilience.
    
    Implements the circuit breaker pattern to prevent cascading failures
    and provide automatic recovery for third-party integrations.
    """
    
    def __init__(self):
        """Initialize circuit breaker."""
        self.logger = logging.getLogger(__name__)
        
        # Circuit configurations by integration
        self.configs: Dict[str, CircuitConfig] = {}
        
        # Circuit states
        self.states: Dict[str, CircuitState] = {}
        
        # Circuit metrics
        self.metrics: Dict[str, CircuitMetrics] = {}
        
        # Call history for each circuit (sliding window)
        self.call_history: Dict[str, List[CircuitCall]] = {}
        
        # State change listeners
        self.state_change_listeners: List[Callable] = []
        
        # Recovery tasks
        self.recovery_tasks: Dict[str, asyncio.Task] = {}
        
        # Global settings
        self.sliding_window_size = 100  # Number of calls to keep in history
        self.sliding_window_time = 300  # 5 minutes in seconds
    
    async def initialize_breaker(self, integration_name: str, config: Optional[CircuitConfig] = None) -> bool:
        """Initialize circuit breaker for integration."""
        try:
            # Use provided config or create default
            if config:
                self.configs[integration_name] = config
            else:
                self.configs[integration_name] = CircuitConfig(integration_name=integration_name)
            
            # Initialize state and metrics
            self.states[integration_name] = CircuitState.CLOSED
            self.metrics[integration_name] = CircuitMetrics()
            self.call_history[integration_name] = []
            
            self.logger.info(f"Circuit breaker initialized for {integration_name}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize circuit breaker for {integration_name}: {str(e)}")
            return False
    
    async def is_available(self, integration_name: str) -> bool:
        """Check if integration is available (circuit is closed or half-open)."""
        if integration_name not in self.states:
            await self.initialize_breaker(integration_name)
        
        state = self.states[integration_name]
        
        if state == CircuitState.CLOSED:
            return True
        elif state == CircuitState.HALF_OPEN:
            return True  # Allow limited requests in half-open state
        else:  # OPEN
            # Check if recovery timeout has passed
            config = self.configs[integration_name]
            metrics = self.metrics[integration_name]
            
            if (metrics.last_failure_time and 
                datetime.utcnow() - metrics.last_failure_time >= timedelta(seconds=config.recovery_timeout)):
                await self._transition_to_half_open(integration_name)
                return True
            
            return False
    
    async def record_success(self, integration_name: str, response_time: float = 0.0) -> None:
        """Record successful request."""
        try:
            if integration_name not in self.configs:
                await self.initialize_breaker(integration_name)
            
            config = self.configs[integration_name]
            metrics = self.metrics[integration_name]
            
            # Record call
            call = CircuitCall(
                timestamp=datetime.utcnow(),
                duration=response_time,
                success=True
            )
            
            await self._record_call(integration_name, call)
            
            # Update metrics
            metrics.total_requests += 1
            metrics.successful_requests += 1
            metrics.last_success_time = datetime.utcnow()
            
            # Check for slow calls
            if response_time > config.slow_call_duration_threshold:
                metrics.slow_requests += 1
            
            # Update response time (exponential moving average)
            alpha = 0.1
            metrics.average_response_time = (
                alpha * response_time + (1 - alpha) * metrics.average_response_time
            )
            
            await self._update_rates(integration_name)
            
            # Handle state transitions for successful calls
            await self._handle_success_transition(integration_name)
            
        except Exception as e:
            self.logger.error(f"Error recording success for {integration_name}: {str(e)}")
    
    async def record_failure(self, integration_name: str, error: str = "", response_time: float = 0.0) -> None:
        """Record failed request."""
        try:
            if integration_name not in self.configs:
                await self.initialize_breaker(integration_name)
            
            metrics = self.metrics[integration_name]
            
            # Record call
            call = CircuitCall(
                timestamp=datetime.utcnow(),
                duration=response_time,
                success=False,
                error=error
            )
            
            await self._record_call(integration_name, call)
            
            # Update metrics
            metrics.total_requests += 1
            metrics.failed_requests += 1
            metrics.last_failure_time = datetime.utcnow()
            
            await self._update_rates(integration_name)
            
            # Handle state transitions for failed calls
            await self._handle_failure_transition(integration_name)
            
        except Exception as e:
            self.logger.error(f"Error recording failure for {integration_name}: {str(e)}")
    
    async def record_rejection(self, integration_name: str) -> None:
        """Record rejected request (circuit is open)."""
        try:
            if integration_name not in self.metrics:
                await self.initialize_breaker(integration_name)
            
            self.metrics[integration_name].rejected_requests += 1
            
        except Exception as e:
            self.logger.error(f"Error recording rejection for {integration_name}: {str(e)}")
    
    async def force_open(self, integration_name: str, reason: str = "") -> bool:
        """Force circuit to open state."""
        try:
            if integration_name not in self.states:
                await self.initialize_breaker(integration_name)
            
            await self._transition_to_open(integration_name, f"Force opened: {reason}")
            
            self.logger.warning(f"Circuit breaker force opened for {integration_name}: {reason}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error force opening circuit for {integration_name}: {str(e)}")
            return False
    
    async def force_close(self, integration_name: str, reason: str = "") -> bool:
        """Force circuit to closed state."""
        try:
            if integration_name not in self.states:
                await self.initialize_breaker(integration_name)
            
            await self._transition_to_closed(integration_name, f"Force closed: {reason}")
            
            self.logger.info(f"Circuit breaker force closed for {integration_name}: {reason}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error force closing circuit for {integration_name}: {str(e)}")
            return False
    
    async def get_status(self, integration_name: str) -> Dict[str, Any]:
        """Get circuit breaker status."""
        if integration_name not in self.configs:
            return {"error": "Circuit breaker not initialized"}
        
        config = self.configs[integration_name]
        state = self.states[integration_name]
        metrics = self.metrics[integration_name]
        
        return {
            "integration_name": integration_name,
            "state": state.value,
            "configuration": {
                "failure_threshold": config.failure_threshold,
                "recovery_timeout": config.recovery_timeout,
                "success_threshold": config.success_threshold,
                "timeout": config.timeout,
                "volume_threshold": config.volume_threshold,
                "error_percentage_threshold": config.error_percentage_threshold,
                "slow_call_duration_threshold": config.slow_call_duration_threshold,
                "slow_call_rate_threshold": config.slow_call_rate_threshold
            },
            "metrics": {
                "total_requests": metrics.total_requests,
                "successful_requests": metrics.successful_requests,
                "failed_requests": metrics.failed_requests,
                "slow_requests": metrics.slow_requests,
                "rejected_requests": metrics.rejected_requests,
                "success_rate": metrics.success_rate,
                "failure_rate": metrics.failure_rate,
                "slow_call_rate": metrics.slow_call_rate,
                "average_response_time": round(metrics.average_response_time, 3),
                "last_failure_time": metrics.last_failure_time.isoformat() if metrics.last_failure_time else None,
                "last_success_time": metrics.last_success_time.isoformat() if metrics.last_success_time else None
            },
            "is_available": await self.is_available(integration_name),
            "call_history_size": len(self.call_history.get(integration_name, []))
        }
    
    async def get_all_status(self) -> Dict[str, Any]:
        """Get status of all circuit breakers."""
        all_status = {}
        
        for integration_name in self.configs:
            all_status[integration_name] = await self.get_status(integration_name)
        
        # Calculate global statistics
        total_requests = sum(status["metrics"]["total_requests"] for status in all_status.values())
        successful_requests = sum(status["metrics"]["successful_requests"] for status in all_status.values())
        failed_requests = sum(status["metrics"]["failed_requests"] for status in all_status.values())
        rejected_requests = sum(status["metrics"]["rejected_requests"] for status in all_status.values())
        
        open_circuits = len([status for status in all_status.values() if status["state"] == "open"])
        half_open_circuits = len([status for status in all_status.values() if status["state"] == "half_open"])
        closed_circuits = len([status for status in all_status.values() if status["state"] == "closed"])
        
        global_success_rate = (successful_requests / total_requests * 100) if total_requests > 0 else 100.0
        
        return {
            "circuit_breakers": all_status,
            "global_statistics": {
                "total_circuits": len(self.configs),
                "open_circuits": open_circuits,
                "half_open_circuits": half_open_circuits,
                "closed_circuits": closed_circuits,
                "total_requests": total_requests,
                "successful_requests": successful_requests,
                "failed_requests": failed_requests,
                "rejected_requests": rejected_requests,
                "global_success_rate": round(global_success_rate, 2)
            }
        }
    
    async def _record_call(self, integration_name: str, call: CircuitCall) -> None:
        """Record call in sliding window history."""
        if integration_name not in self.call_history:
            self.call_history[integration_name] = []
        
        history = self.call_history[integration_name]
        history.append(call)
        
        # Maintain sliding window by time
        cutoff_time = datetime.utcnow() - timedelta(seconds=self.sliding_window_time)
        self.call_history[integration_name] = [
            c for c in history if c.timestamp >= cutoff_time
        ]
        
        # Maintain sliding window by size
        if len(self.call_history[integration_name]) > self.sliding_window_size:
            self.call_history[integration_name] = self.call_history[integration_name][-self.sliding_window_size:]
    
    async def _update_rates(self, integration_name: str) -> None:
        """Update success, failure, and slow call rates."""
        metrics = self.metrics[integration_name]
        
        if metrics.total_requests > 0:
            metrics.success_rate = (metrics.successful_requests / metrics.total_requests) * 100
            metrics.failure_rate = (metrics.failed_requests / metrics.total_requests) * 100
            metrics.slow_call_rate = (metrics.slow_requests / metrics.total_requests) * 100
        else:
            metrics.success_rate = 100.0
            metrics.failure_rate = 0.0
            metrics.slow_call_rate = 0.0
    
    async def _handle_success_transition(self, integration_name: str) -> None:
        """Handle state transitions for successful calls."""
        state = self.states[integration_name]
        config = self.configs[integration_name]
        
        if state == CircuitState.HALF_OPEN:
            # Check if we have enough successes to close the circuit
            recent_calls = await self._get_recent_calls(integration_name, config.success_threshold)
            successful_calls = [c for c in recent_calls if c.success]
            
            if len(successful_calls) >= config.success_threshold:
                await self._transition_to_closed(integration_name, "Sufficient successful calls in half-open state")
    
    async def _handle_failure_transition(self, integration_name: str) -> None:
        """Handle state transitions for failed calls."""
        state = self.states[integration_name]
        config = self.configs[integration_name]
        metrics = self.metrics[integration_name]
        
        if state == CircuitState.CLOSED:
            # Check if we should open the circuit
            should_open = False
            reason = ""
            
            # Check failure threshold
            if metrics.failed_requests >= config.failure_threshold:
                should_open = True
                reason = f"Failure threshold reached: {metrics.failed_requests}/{config.failure_threshold}"
            
            # Check volume and error percentage
            elif (metrics.total_requests >= config.volume_threshold and 
                  metrics.failure_rate >= config.error_percentage_threshold):
                should_open = True
                reason = f"Error percentage threshold reached: {metrics.failure_rate:.1f}%"
            
            # Check slow call rate
            elif (metrics.total_requests >= config.volume_threshold and 
                  metrics.slow_call_rate >= config.slow_call_rate_threshold):
                should_open = True
                reason = f"Slow call rate threshold reached: {metrics.slow_call_rate:.1f}%"
            
            if should_open:
                await self._transition_to_open(integration_name, reason)
        
        elif state == CircuitState.HALF_OPEN:
            # Any failure in half-open state should open the circuit
            await self._transition_to_open(integration_name, "Failure detected in half-open state")
    
    async def _transition_to_open(self, integration_name: str, reason: str) -> None:
        """Transition circuit to open state."""
        old_state = self.states[integration_name]
        self.states[integration_name] = CircuitState.OPEN
        
        # Cancel any existing recovery task
        if integration_name in self.recovery_tasks:
            self.recovery_tasks[integration_name].cancel()
        
        # Start recovery task
        self.recovery_tasks[integration_name] = asyncio.create_task(
            self._schedule_recovery(integration_name)
        )
        
        await self._notify_state_change(integration_name, old_state, CircuitState.OPEN, reason)
        
        self.logger.warning(f"Circuit breaker opened for {integration_name}: {reason}")
    
    async def _transition_to_half_open(self, integration_name: str) -> None:
        """Transition circuit to half-open state."""
        old_state = self.states[integration_name]
        self.states[integration_name] = CircuitState.HALF_OPEN
        
        # Start half-open timeout
        config = self.configs[integration_name]
        asyncio.create_task(self._half_open_timeout(integration_name, config.max_wait_duration_in_half_open))
        
        await self._notify_state_change(integration_name, old_state, CircuitState.HALF_OPEN, "Recovery timeout reached")
        
        self.logger.info(f"Circuit breaker transitioned to half-open for {integration_name}")
    
    async def _transition_to_closed(self, integration_name: str, reason: str) -> None:
        """Transition circuit to closed state."""
        old_state = self.states[integration_name]
        self.states[integration_name] = CircuitState.CLOSED
        
        # Cancel recovery task if exists
        if integration_name in self.recovery_tasks:
            self.recovery_tasks[integration_name].cancel()
            del self.recovery_tasks[integration_name]
        
        # Reset some metrics
        metrics = self.metrics[integration_name]
        metrics.failed_requests = 0  # Reset failure count when closing
        await self._update_rates(integration_name)
        
        await self._notify_state_change(integration_name, old_state, CircuitState.CLOSED, reason)
        
        self.logger.info(f"Circuit breaker closed for {integration_name}: {reason}")
    
    async def _schedule_recovery(self, integration_name: str) -> None:
        """Schedule recovery attempt after timeout."""
        try:
            config = self.configs[integration_name]
            await asyncio.sleep(config.recovery_timeout)
            
            # Transition to half-open if still in open state
            if self.states[integration_name] == CircuitState.OPEN:
                await self._transition_to_half_open(integration_name)
                
        except asyncio.CancelledError:
            pass  # Task was cancelled
    
    async def _half_open_timeout(self, integration_name: str, timeout: int) -> None:
        """Handle half-open state timeout."""
        try:
            await asyncio.sleep(timeout)
            
            # If still in half-open state, transition back to open
            if self.states[integration_name] == CircuitState.HALF_OPEN:
                await self._transition_to_open(integration_name, "Half-open timeout exceeded")
                
        except asyncio.CancelledError:
            pass  # Task was cancelled
    
    async def _get_recent_calls(self, integration_name: str, count: int) -> List[CircuitCall]:
        """Get most recent calls."""
        if integration_name not in self.call_history:
            return []
        
        history = self.call_history[integration_name]
        return history[-count:] if len(history) >= count else history
    
    async def _notify_state_change(
        self, 
        integration_name: str, 
        old_state: CircuitState, 
        new_state: CircuitState, 
        reason: str
    ) -> None:
        """Notify listeners of state change."""
        event_data = {
            "integration_name": integration_name,
            "old_state": old_state.value,
            "new_state": new_state.value,
            "reason": reason,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        for listener in self.state_change_listeners:
            try:
                await listener(event_data)
            except Exception as e:
                self.logger.error(f"State change listener error: {str(e)}")
    
    async def add_state_change_listener(self, listener: Callable) -> None:
        """Add state change listener."""
        self.state_change_listeners.append(listener)
        self.logger.info("State change listener added")
    
    async def remove_state_change_listener(self, listener: Callable) -> bool:
        """Remove state change listener."""
        if listener in self.state_change_listeners:
            self.state_change_listeners.remove(listener)
            self.logger.info("State change listener removed")
            return True
        return False
    
    async def reset_metrics(self, integration_name: str) -> bool:
        """Reset metrics for integration."""
        try:
            if integration_name not in self.metrics:
                return False
            
            self.metrics[integration_name] = CircuitMetrics()
            self.call_history[integration_name] = []
            
            self.logger.info(f"Metrics reset for {integration_name}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error resetting metrics for {integration_name}: {str(e)}")
            return False
    
    async def update_config(self, integration_name: str, config: CircuitConfig) -> bool:
        """Update circuit breaker configuration."""
        try:
            if integration_name not in self.configs:
                return False
            
            self.configs[integration_name] = config
            
            self.logger.info(f"Configuration updated for {integration_name}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error updating config for {integration_name}: {str(e)}")
            return False
    
    async def shutdown(self) -> None:
        """Shutdown circuit breaker system."""
        self.logger.info("Shutting down circuit breaker system...")
        
        # Cancel all recovery tasks
        for task in self.recovery_tasks.values():
            task.cancel()
        
        if self.recovery_tasks:
            await asyncio.gather(*self.recovery_tasks.values(), return_exceptions=True)
        
        self.recovery_tasks.clear()
        self.state_change_listeners.clear()
        
        self.logger.info("Circuit breaker system shutdown complete")