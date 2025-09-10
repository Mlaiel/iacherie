"""Circuit Breaker Pattern Implementation
=======================================

Circuit breaker pattern for integration failure isolation and automatic recovery.
Prevents cascading failures and provides graceful degradation.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
import time
from typing import Dict, Optional, Any, Callable, Awaitable
from dataclasses import dataclass
from enum import Enum
from datetime import datetime, timedelta


class CircuitBreakerState(Enum):
    """Circuit breaker states"""
    CLOSED = "closed"      # Normal operation
    OPEN = "open"          # Failing, blocking calls
    HALF_OPEN = "half_open"  # Testing recovery


@dataclass
class CircuitBreakerConfig:
    """Circuit breaker configuration"""
    failure_threshold: int = 5  # Failures before opening
    recovery_timeout: int = 60  # Seconds before attempting recovery
    success_threshold: int = 3  # Successes to close from half-open
    timeout: int = 30  # Call timeout in seconds
    rolling_window: int = 300  # Rolling window for failure counting


@dataclass
class CircuitBreakerStats:
    """Circuit breaker statistics"""
    state: CircuitBreakerState
    failure_count: int
    success_count: int
    last_failure_time: Optional[datetime]
    last_success_time: Optional[datetime]
    total_calls: int
    failed_calls: int
    successful_calls: int
    opened_count: int
    half_opened_count: int


class CircuitBreaker:
    """Circuit breaker implementation for integration protection"""
    
    def __init__(self):
        """Initialize circuit breaker"""
        self.logger = logging.getLogger(__name__)
        
        # Circuit breaker instances per integration
        self.breakers: Dict[str, Dict[str, Any]] = {}
        
        # Default configuration
        self.default_config = CircuitBreakerConfig()
        
        # Global statistics
        self.global_stats = {
            "total_breakers": 0,
            "open_breakers": 0,
            "half_open_breakers": 0,
            "closed_breakers": 0
        }
    
    def register_breaker(self, integration_name: str, 
                        config: Optional[CircuitBreakerConfig] = None):
        """Register circuit breaker for integration
        
        Args:
            integration_name: Integration name
            config: Circuit breaker configuration
        """
        if integration_name not in self.breakers:
            breaker_config = config or self.default_config
            
            self.breakers[integration_name] = {
                "state": CircuitBreakerState.CLOSED,
                "config": breaker_config,
                "failure_count": 0,
                "success_count": 0,
                "last_failure_time": None,
                "last_success_time": None,
                "last_state_change": datetime.utcnow(),
                "total_calls": 0,
                "failed_calls": 0,
                "successful_calls": 0,
                "opened_count": 0,
                "half_opened_count": 0,
                "failure_times": []  # Rolling window of failure times
            }
            
            self.global_stats["total_breakers"] += 1
            self.global_stats["closed_breakers"] += 1
            
            self.logger.info(f"Registered circuit breaker for: {integration_name}")
    
    async def call_allowed(self, integration_name: str) -> bool:
        """Check if call is allowed through circuit breaker
        
        Args:
            integration_name: Integration name
            
        Returns:
            bool: Whether call is allowed
        """
        # Auto-register if not exists
        if integration_name not in self.breakers:
            self.register_breaker(integration_name)
        
        breaker = self.breakers[integration_name]
        current_state = breaker["state"]
        config = breaker["config"]
        
        # Clean old failures from rolling window
        self._clean_old_failures(integration_name)
        
        if current_state == CircuitBreakerState.CLOSED:
            return True
        
        elif current_state == CircuitBreakerState.OPEN:
            # Check if recovery timeout has passed
            if breaker["last_state_change"]:
                time_since_open = (datetime.utcnow() - breaker["last_state_change"]).total_seconds()
                
                if time_since_open >= config.recovery_timeout:
                    # Transition to half-open
                    await self._transition_to_half_open(integration_name)
                    return True
                else:
                    return False
            return False
        
        elif current_state == CircuitBreakerState.HALF_OPEN:
            # Allow limited calls to test recovery
            return True
        
        return False
    
    async def record_success(self, integration_name: str):
        """Record successful call
        
        Args:
            integration_name: Integration name
        """
        if integration_name not in self.breakers:
            return
        
        breaker = self.breakers[integration_name]
        current_state = breaker["state"]
        config = breaker["config"]
        
        # Update statistics
        breaker["total_calls"] += 1
        breaker["successful_calls"] += 1
        breaker["last_success_time"] = datetime.utcnow()
        
        if current_state == CircuitBreakerState.HALF_OPEN:
            breaker["success_count"] += 1
            
            # Check if we have enough successes to close
            if breaker["success_count"] >= config.success_threshold:
                await self._transition_to_closed(integration_name)
        
        elif current_state == CircuitBreakerState.CLOSED:
            # Reset failure count on success
            breaker["failure_count"] = 0
            breaker["failure_times"] = []
    
    async def record_failure(self, integration_name: str, error: Optional[Exception] = None):
        """Record failed call
        
        Args:
            integration_name: Integration name
            error: Exception that caused the failure
        """
        if integration_name not in self.breakers:
            return
        
        breaker = self.breakers[integration_name]
        current_state = breaker["state"]
        config = breaker["config"]
        
        # Update statistics
        breaker["total_calls"] += 1
        breaker["failed_calls"] += 1
        breaker["failure_count"] += 1
        breaker["last_failure_time"] = datetime.utcnow()
        
        # Add to rolling window
        breaker["failure_times"].append(datetime.utcnow())
        
        # Log failure
        error_msg = str(error) if error else "Unknown error"
        self.logger.warning(f"Circuit breaker recorded failure for {integration_name}: {error_msg}")
        
        if current_state == CircuitBreakerState.CLOSED:
            # Check if we should open the circuit
            if breaker["failure_count"] >= config.failure_threshold:
                await self._transition_to_open(integration_name)
        
        elif current_state == CircuitBreakerState.HALF_OPEN:
            # Any failure in half-open state goes back to open
            await self._transition_to_open(integration_name)
    
    async def _transition_to_open(self, integration_name: str):
        """Transition circuit breaker to open state
        
        Args:
            integration_name: Integration name
        """
        breaker = self.breakers[integration_name]
        old_state = breaker["state"]
        
        breaker["state"] = CircuitBreakerState.OPEN
        breaker["last_state_change"] = datetime.utcnow()
        breaker["opened_count"] += 1
        breaker["success_count"] = 0  # Reset success count
        
        # Update global stats
        if old_state == CircuitBreakerState.CLOSED:
            self.global_stats["closed_breakers"] -= 1
        elif old_state == CircuitBreakerState.HALF_OPEN:
            self.global_stats["half_open_breakers"] -= 1
        
        self.global_stats["open_breakers"] += 1
        
        self.logger.error(f"Circuit breaker OPENED for {integration_name} - "
                         f"Failure threshold reached: {breaker['failure_count']} failures")
    
    async def _transition_to_half_open(self, integration_name: str):
        """Transition circuit breaker to half-open state
        
        Args:
            integration_name: Integration name
        """
        breaker = self.breakers[integration_name]
        old_state = breaker["state"]
        
        breaker["state"] = CircuitBreakerState.HALF_OPEN
        breaker["last_state_change"] = datetime.utcnow()
        breaker["half_opened_count"] += 1
        breaker["success_count"] = 0  # Reset success count for testing
        
        # Update global stats
        if old_state == CircuitBreakerState.OPEN:
            self.global_stats["open_breakers"] -= 1
        elif old_state == CircuitBreakerState.CLOSED:
            self.global_stats["closed_breakers"] -= 1
        
        self.global_stats["half_open_breakers"] += 1
        
        self.logger.info(f"Circuit breaker HALF-OPEN for {integration_name} - Testing recovery")
    
    async def _transition_to_closed(self, integration_name: str):
        """Transition circuit breaker to closed state
        
        Args:
            integration_name: Integration name
        """
        breaker = self.breakers[integration_name]
        old_state = breaker["state"]
        
        breaker["state"] = CircuitBreakerState.CLOSED
        breaker["last_state_change"] = datetime.utcnow()
        breaker["failure_count"] = 0  # Reset failure count
        breaker["success_count"] = 0  # Reset success count
        breaker["failure_times"] = []  # Clear failure history
        
        # Update global stats
        if old_state == CircuitBreakerState.OPEN:
            self.global_stats["open_breakers"] -= 1
        elif old_state == CircuitBreakerState.HALF_OPEN:
            self.global_stats["half_open_breakers"] -= 1
        
        self.global_stats["closed_breakers"] += 1
        
        self.logger.info(f"Circuit breaker CLOSED for {integration_name} - Recovery successful")
    
    def _clean_old_failures(self, integration_name: str):
        """Clean old failures from rolling window
        
        Args:
            integration_name: Integration name
        """
        breaker = self.breakers[integration_name]
        config = breaker["config"]
        cutoff_time = datetime.utcnow() - timedelta(seconds=config.rolling_window)
        
        # Remove old failures
        breaker["failure_times"] = [
            failure_time for failure_time in breaker["failure_times"]
            if failure_time > cutoff_time
        ]
        
        # Update failure count based on rolling window
        breaker["failure_count"] = len(breaker["failure_times"])
    
    async def get_breaker_status(self, integration_name: str) -> Optional[CircuitBreakerStats]:
        """Get circuit breaker status
        
        Args:
            integration_name: Integration name
            
        Returns:
            Optional[CircuitBreakerStats]: Breaker statistics
        """
        if integration_name not in self.breakers:
            return None
        
        breaker = self.breakers[integration_name]
        
        return CircuitBreakerStats(
            state=breaker["state"],
            failure_count=breaker["failure_count"],
            success_count=breaker["success_count"],
            last_failure_time=breaker["last_failure_time"],
            last_success_time=breaker["last_success_time"],
            total_calls=breaker["total_calls"],
            failed_calls=breaker["failed_calls"],
            successful_calls=breaker["successful_calls"],
            opened_count=breaker["opened_count"],
            half_opened_count=breaker["half_opened_count"]
        )
    
    async def get_all_statuses(self) -> Dict[str, CircuitBreakerStats]:
        """Get all circuit breaker statuses
        
        Returns:
            Dict[str, CircuitBreakerStats]: All breaker statistics
        """
        statuses = {}
        
        for integration_name in self.breakers:
            status = await self.get_breaker_status(integration_name)
            if status:
                statuses[integration_name] = status
        
        return statuses
    
    async def reset_breaker(self, integration_name: str):
        """Reset circuit breaker to closed state
        
        Args:
            integration_name: Integration name
        """
        if integration_name in self.breakers:
            await self._transition_to_closed(integration_name)
            self.logger.info(f"Circuit breaker manually reset for: {integration_name}")
    
    async def force_open(self, integration_name: str):
        """Force circuit breaker to open state
        
        Args:
            integration_name: Integration name
        """
        if integration_name in self.breakers:
            await self._transition_to_open(integration_name)
            self.logger.warning(f"Circuit breaker manually opened for: {integration_name}")
    
    async def get_global_stats(self) -> Dict[str, Any]:
        """Get global circuit breaker statistics
        
        Returns:
            Dict[str, Any]: Global statistics
        """
        stats = self.global_stats.copy()
        
        # Calculate health metrics
        total = stats["total_breakers"]
        if total > 0:
            stats["health_percentage"] = (stats["closed_breakers"] / total) * 100
            stats["degraded_percentage"] = (stats["half_open_breakers"] / total) * 100
            stats["failed_percentage"] = (stats["open_breakers"] / total) * 100
        else:
            stats["health_percentage"] = 100.0
            stats["degraded_percentage"] = 0.0
            stats["failed_percentage"] = 0.0
        
        stats["timestamp"] = datetime.utcnow().isoformat()
        
        return stats
    
    async def health_check(self) -> Dict[str, Any]:
        """Perform health check on all circuit breakers
        
        Returns:
            Dict[str, Any]: Health check result
        """
        global_stats = await self.get_global_stats()
        
        # Determine overall health
        if global_stats["failed_percentage"] > 50:
            health_status = "critical"
        elif global_stats["failed_percentage"] > 25:
            health_status = "degraded"
        elif global_stats["degraded_percentage"] > 25:
            health_status = "warning"
        else:
            health_status = "healthy"
        
        return {
            "status": health_status,
            "global_stats": global_stats,
            "individual_breakers": await self.get_all_statuses(),
            "timestamp": datetime.utcnow().isoformat()
        }
    
    async def execute_with_breaker(self, integration_name: str, 
                                 func: Callable[..., Awaitable[Any]], 
                                 *args, **kwargs) -> Any:
        """Execute function with circuit breaker protection
        
        Args:
            integration_name: Integration name
            func: Async function to execute
            *args: Function arguments
            **kwargs: Function keyword arguments
            
        Returns:
            Any: Function result
            
        Raises:
            Exception: If circuit breaker is open or function fails
        """
        # Check if call is allowed
        if not await self.call_allowed(integration_name):
            raise Exception(f"Circuit breaker is OPEN for {integration_name}")
        
        try:
            # Execute function with timeout
            breaker = self.breakers.get(integration_name, {})
            config = breaker.get("config", self.default_config)
            
            result = await asyncio.wait_for(
                func(*args, **kwargs),
                timeout=config.timeout
            )
            
            # Record success
            await self.record_success(integration_name)
            
            return result
            
        except Exception as e:
            # Record failure
            await self.record_failure(integration_name, e)
            raise
    
    async def cleanup_breakers(self, max_age_hours: int = 24):
        """Clean up old circuit breaker data
        
        Args:
            max_age_hours: Maximum age in hours
        """
        cutoff_time = datetime.utcnow() - timedelta(hours=max_age_hours)
        
        for integration_name, breaker in self.breakers.items():
            # Clean old failure times
            breaker["failure_times"] = [
                failure_time for failure_time in breaker["failure_times"]
                if failure_time > cutoff_time
            ]
            
            # Update failure count
            breaker["failure_count"] = len(breaker["failure_times"])
        
        self.logger.info("Circuit breaker cleanup completed")


# Global circuit breaker instance
circuit_breaker = CircuitBreaker()


async def get_circuit_breaker() -> CircuitBreaker:
    """Get global circuit breaker instance
    
    Returns:
        CircuitBreaker: Global instance
    """
    return circuit_breaker