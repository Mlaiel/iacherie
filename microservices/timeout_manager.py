"""
Timeout Manager module
Enterprise implementation for Ainflue platform
"""

#!/usr/bin/env python3
"""
Enterprise Timeout Manager Service
Advanced timeout management and optimization service for microservices architecture

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️ STRICT COPYRIGHT WARNING ⚠️
This implementation is proprietary and confidential. Unauthorized use, reproduction,
distribution, or modification without written permission from Fahed Mlaiel
(mlaiel@live.de) is strictly prohibited and will be prosecuted to the full extent
of the law. All rights reserved.
"""

import asyncio
import time
import logging
from typing import Dict, Any, Optional, Callable, Awaitable, Union, List
from dataclasses import dataclass, field
from enum import Enum
import threading
from contextlib import asynccontextmanager
import signal
import weakref
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class TimeoutStrategy(Enum):
    """Timeout strategy enumeration"""
    FIXED = "fixed"
    ADAPTIVE = "adaptive"
    CIRCUIT_BREAKER = "circuit_breaker"
    PROGRESSIVE = "progressive"

class TimeoutResult(Enum):
    """Timeout operation result"""
    SUCCESS = "success"
    TIMEOUT = "timeout"
    ERROR = "error"
    CANCELLED = "cancelled"

@dataclass
class TimeoutConfig:
    """Timeout configuration settings"""
    default_timeout: float = 30.0
    max_timeout: float = 300.0
    min_timeout: float = 1.0
    adaptive_factor: float = 1.2
    circuit_breaker_threshold: int = 5
    progressive_multiplier: float = 1.5
    cleanup_interval: float = 60.0
    
@dataclass
class TimeoutContext:
    """Timeout operation context"""
    operation_id: str
    service_name: str
    method_name: str
    timeout_value: float
    strategy: TimeoutStrategy
    start_time: float = field(default_factory=time.time)
    end_time: Optional[float] = None
    result: Optional[TimeoutResult] = None
    error: Optional[Exception] = None
    
@dataclass
class ServiceMetrics:
    """Service timeout metrics"""
    total_operations: int = 0
    successful_operations: int = 0
    timeout_operations: int = 0
    error_operations: int = 0
    average_duration: float = 0.0
    adaptive_timeout: float = 30.0
    failure_rate: float = 0.0

class TimeoutManager:
    """
    Enterprise Timeout Manager Service
    
    Provides comprehensive timeout management with multiple strategies:
    - Fixed timeouts
    - Adaptive timeouts based on historical performance
    - Circuit breaker integration
    - Progressive timeouts for retries
    """
    
    def __init__(self, config -> None: Optional[TimeoutConfig] = None) -> None:
        """Initialize timeout manager"""
        self.config = config or TimeoutConfig()
        self.metrics: Dict[str, ServiceMetrics] = {}
        self.active_operations: Dict[str, TimeoutContext] = {}
        self.cleanup_task: Optional[asyncio.Task] = None
        self.shutdown_event = asyncio.Event()
        self._lock = asyncio.Lock()
        
        # Weak reference set for cleanup
        self._operation_refs = weakref.WeakSet()
        
        logger.info("TimeoutManager initialized with config: %s", self.config)
    
    async def start(self) -> None:
        """Start the timeout manager"""
        try:
            # Start cleanup task
            self.cleanup_task = asyncio.create_task(self._cleanup_task())
            logger.info("TimeoutManager started successfully")
        except Exception as e:
            logger.error("Failed to start TimeoutManager: %s", e)
            raise
    
    async def stop(self) -> None:
        """Stop the timeout manager"""
        try:
            self.shutdown_event.set()
            
            # Cancel cleanup task
            if self.cleanup_task:
                self.cleanup_task.cancel()
                try:
                    await self.cleanup_task
                except asyncio.CancelledError:
                    pass
            
            # Cancel all active operations
            await self._cancel_all_operations()
            
            logger.info("TimeoutManager stopped successfully")
        except Exception as e:
            logger.error("Error stopping TimeoutManager: %s", e)
    
    async def execute_with_timeout(
        self,
        operation: Callable[..., Awaitable[Any]],
        service_name: str,
        method_name: str,
        timeout: Optional[float] = None,
        strategy: TimeoutStrategy = TimeoutStrategy.FIXED,
        operation_id: Optional[str] = None,
        *args,
        **kwargs
    ) -> Any:
        """
        Execute operation with timeout management
        
        Args:
            operation: Async function to execute
            service_name: Name of the service
            method_name: Name of the method
            timeout: Custom timeout value
            strategy: Timeout strategy to use
            operation_id: Optional operation identifier
            *args, **kwargs: Arguments to pass to operation
            
        Returns:
            Result of the operation
            
        Raises:
            asyncio.TimeoutError: If operation times out
            Exception: Any exception from the operation
        """
        operation_id = operation_id or f"{service_name}_{method_name}_{int(time.time() * 1000)}"
        
        # Calculate timeout based on strategy
        calculated_timeout = await self._calculate_timeout(
            service_name, method_name, timeout, strategy
        )
        
        # Create timeout context
        context = TimeoutContext(
            operation_id=operation_id,
            service_name=service_name,
            method_name=method_name,
            timeout_value=calculated_timeout,
            strategy=strategy
        )
        
        async with self._track_operation(context):
            try:
                # Execute operation with timeout
                result = await asyncio.wait_for(
                    operation(*args, **kwargs),
                    timeout=calculated_timeout
                )
                
                context.result = TimeoutResult.SUCCESS
                context.end_time = time.time()
                
                # Update metrics
                await self._update_metrics(context)
                
                return result
                
            except asyncio.TimeoutError:
                context.result = TimeoutResult.TIMEOUT
                context.end_time = time.time()
                context.error = asyncio.TimeoutError(f"Operation timed out after {calculated_timeout}s")
                
                await self._update_metrics(context)
                logger.warning(
                    "Operation timeout: %s.%s after %ss",
                    service_name, method_name, calculated_timeout
                )
                raise
                
            except asyncio.CancelledError:
                context.result = TimeoutResult.CANCELLED
                context.end_time = time.time()
                
                await self._update_metrics(context)
                logger.info("Operation cancelled: %s.%s", service_name, method_name)
                raise
                
            except Exception as e:
                context.result = TimeoutResult.ERROR
                context.end_time = time.time()
                context.error = e
                
                await self._update_metrics(context)
                logger.error("Operation error: %s.%s - %s", service_name, method_name, e)
                raise
    
    @asynccontextmanager
    async def timeout_context(
        self,
        service_name -> None: str,
        method_name -> None: str,
        timeout -> None: Optional[float] = None,
        strategy -> None: TimeoutStrategy = TimeoutStrategy.FIXED
    ) -> None:
        """Context manager for timeout operations"""
        operation_id = f"{service_name}_{method_name}_{int(time.time() * 1000)}"
        
        calculated_timeout = await self._calculate_timeout(
            service_name, method_name, timeout, strategy
        )
        
        context = TimeoutContext(
            operation_id=operation_id,
            service_name=service_name,
            method_name=method_name,
            timeout_value=calculated_timeout,
            strategy=strategy
        )
        
        async with self._track_operation(context):
            try:
                yield calculated_timeout
                context.result = TimeoutResult.SUCCESS
                context.end_time = time.time()
                await self._update_metrics(context)
                
            except Exception as e:
                context.result = TimeoutResult.ERROR
                context.end_time = time.time()
                context.error = e
                await self._update_metrics(context)
                raise
    
    async def _calculate_timeout(
        self,
        service_name: str,
        method_name: str,
        custom_timeout: Optional[float],
        strategy: TimeoutStrategy
    ) -> float:
        """Calculate timeout based on strategy"""
        if custom_timeout:
            return min(max(custom_timeout, self.config.min_timeout), self.config.max_timeout)
        
        service_key = f"{service_name}.{method_name}"
        
        if strategy == TimeoutStrategy.FIXED:
            return self.config.default_timeout
        
        elif strategy == TimeoutStrategy.ADAPTIVE:
            async with self._lock:
                metrics = self.metrics.get(service_key)
                if metrics and metrics.total_operations > 0:
                    # Adaptive timeout based on historical performance
                    return min(
                        max(
                            metrics.average_duration * self.config.adaptive_factor,
                            self.config.min_timeout
                        ),
                        self.config.max_timeout
                    )
                return self.config.default_timeout
        
        elif strategy == TimeoutStrategy.CIRCUIT_BREAKER:
            async with self._lock:
                metrics = self.metrics.get(service_key)
                if metrics and metrics.failure_rate > 0.5:
                    # Reduced timeout for failing services
                    return self.config.min_timeout * 2
                return self.config.default_timeout
        
        elif strategy == TimeoutStrategy.PROGRESSIVE:
            # Progressive timeout for retries (would need retry context)
            return self.config.default_timeout * self.config.progressive_multiplier
        
        return self.config.default_timeout
    
    @asynccontextmanager
    async def _track_operation(self, context -> None: TimeoutContext) -> None:
        """Track operation lifecycle"""
        async with self._lock:
            self.active_operations[context.operation_id] = context
        
        try:
            yield context
        finally:
            async with self._lock:
                self.active_operations.pop(context.operation_id, None)
    
    async def _update_metrics(self, context -> None: TimeoutContext) -> None:
        """Update service metrics"""
        service_key = f"{context.service_name}.{context.method_name}"
        duration = (context.end_time or time.time()) - context.start_time
        
        async with self._lock:
            if service_key not in self.metrics:
                self.metrics[service_key] = ServiceMetrics()
            
            metrics = self.metrics[service_key]
            metrics.total_operations += 1
            
            if context.result == TimeoutResult.SUCCESS:
                metrics.successful_operations += 1
                # Update running average
                old_avg = metrics.average_duration
                metrics.average_duration = (
                    (old_avg * (metrics.successful_operations - 1) + duration) /
                    metrics.successful_operations
                )
            elif context.result == TimeoutResult.TIMEOUT:
                metrics.timeout_operations += 1
            elif context.result == TimeoutResult.ERROR:
                metrics.error_operations += 1
            
            # Update failure rate
            failed_ops = metrics.timeout_operations + metrics.error_operations
            metrics.failure_rate = failed_ops / metrics.total_operations if metrics.total_operations > 0 else 0.0
            
            # Update adaptive timeout
            if metrics.successful_operations > 0:
                metrics.adaptive_timeout = min(
                    max(
                        metrics.average_duration * self.config.adaptive_factor,
                        self.config.min_timeout
                    ),
                    self.config.max_timeout
                )
    
    async def _cleanup_task(self) -> None:
        """Background cleanup task"""
        while not self.shutdown_event.is_set():
            try:
                await asyncio.sleep(self.config.cleanup_interval)
                await self._cleanup_expired_operations()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error("Error in cleanup task: %s", e)
    
    async def _cleanup_expired_operations(self) -> None:
        """Cleanup expired operations"""
        current_time = time.time()
        expired_operations = []
        
        async with self._lock:
            for op_id, context in self.active_operations.items():
                if (current_time - context.start_time) > (context.timeout_value * 2):
                    expired_operations.append(op_id)
            
            for op_id in expired_operations:
                self.active_operations.pop(op_id, None)
        
        if expired_operations:
            logger.info("Cleaned up %d expired operations", len(expired_operations))
    
    async def _cancel_all_operations(self) -> None:
        """Cancel all active operations"""
        async with self._lock:
            operation_count = len(self.active_operations)
            self.active_operations.clear()
        
        if operation_count > 0:
            logger.info("Cancelled %d active operations", operation_count)
    
    async def get_metrics(self, service_name: Optional[str] = None) -> Dict[str, Any]:
        """Get timeout metrics"""
        async with self._lock:
            if service_name:
                filtered_metrics = {
                    k: v for k, v in self.metrics.items()
                    if k.startswith(f"{service_name}.")
                }
                return {
                    "service_metrics": filtered_metrics,
                    "active_operations": len(self.active_operations)
                }
            
            return {
                "all_metrics": dict(self.metrics),
                "active_operations": len(self.active_operations),
                "total_services": len(self.metrics)
            }
    
    async def get_health_status(self) -> Dict[str, Any]:
        """Get health status"""
        async with self._lock:
            active_count = len(self.active_operations)
            total_services = len(self.metrics)
            
            # Calculate overall health
            healthy_services = sum(
                1 for metrics in self.metrics.values()
                if metrics.failure_rate < 0.1
            )
            
            health_ratio = healthy_services / total_services if total_services > 0 else 1.0
            
            return {
                "status": "healthy" if health_ratio > 0.8 else "degraded" if health_ratio > 0.5 else "unhealthy",
                "active_operations": active_count,
                "total_services": total_services,
                "healthy_services": healthy_services,
                "health_ratio": health_ratio,
                "config": {
                    "default_timeout": self.config.default_timeout,
                    "max_timeout": self.config.max_timeout,
                    "min_timeout": self.config.min_timeout
                }
            }

# Global timeout manager instance
_timeout_manager: Optional[TimeoutManager] = None

async def get_timeout_manager() -> TimeoutManager:
    """Get global timeout manager instance"""
    global _timeout_manager
    if _timeout_manager is None:
        _timeout_manager = TimeoutManager()
        await _timeout_manager.start()
    return _timeout_manager

async def shutdown_timeout_manager() -> None:
    """Shutdown global timeout manager"""
    global _timeout_manager
    if _timeout_manager:
        await _timeout_manager.stop()
        _timeout_manager = None

# Convenience decorators and functions
def timeout(
    timeout_value -> None: Optional[float] = None,
    strategy -> None: TimeoutStrategy = TimeoutStrategy.FIXED,
    service_name -> None: Optional[str] = None
) -> None:
    """Decorator for timeout management"""
    def decorator(func) -> None:
        async def wrapper(*args, **kwargs) -> None:
            manager = await get_timeout_manager()
            svc_name = service_name or func.__module__.split('.')[-1]
            method_name = func.__name__
            
            return await manager.execute_with_timeout(
                func, svc_name, method_name, timeout_value, strategy, None, *args, **kwargs
            )
        return wrapper
    return decorator

if __name__ == "__main__":
    async def test_timeout_manager() -> None:
        """Test timeout manager functionality"""
        manager = TimeoutManager()
        await manager.start()
        
        try:
            # Test successful operation
            async def quick_operation() -> None:
                await asyncio.sleep(0.1)
                return "success"
            
            result = await manager.execute_with_timeout(
                quick_operation, "test_service", "quick_method", 1.0
            )
            print(f"Quick operation result: {result}")
            
            # Test timeout operation
            async def slow_operation() -> None:
                await asyncio.sleep(2.0)
                return "too_slow"
            
            try:
                await manager.execute_with_timeout(
                    slow_operation, "test_service", "slow_method", 0.5
                )
            except asyncio.TimeoutError:
                print("Slow operation timed out as expected")
            
            # Get metrics
            metrics = await manager.get_metrics()
            print(f"Metrics: {metrics}")
            
            # Get health status
            health = await manager.get_health_status()
            print(f"Health: {health}")
            
        finally:
            await manager.stop()
    
    # Run test
    asyncio.run(test_timeout_manager())