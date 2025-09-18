"""
🔥 RETRY COORDINATOR - INTELLIGENT RETRY STRATEGIES
Advanced retry coordination with exponential backoff and smart patterns
Performance Target: < 10ms retry coordination

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️ PROPRIETARY CODE - TOUS DROITS RÉSERVÉS
Commercial use forbidden without written authorization
Reverse engineering strictly prohibited
"""

import asyncio
import math
import random
import time
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Callable, Dict, List, Optional
from uuid import uuid4

import logging


class RetryStrategy(Enum):
    """Retry strategies for different scenarios."""
    FIXED_DELAY = "fixed_delay"
    LINEAR_BACKOFF = "linear_backoff"
    EXPONENTIAL_BACKOFF = "exponential_backoff"
    FIBONACCI_BACKOFF = "fibonacci_backoff"
    ADAPTIVE = "adaptive"


@dataclass
class RetryConfig:
    """Retry configuration for different scenarios."""
    max_attempts: int = 3
    base_delay: float = 1.0
    max_delay: float = 60.0
    jitter: bool = True
    strategy: RetryStrategy = RetryStrategy.EXPONENTIAL_BACKOFF
    
    # Creator Economy specific
    content_type_multipliers: Dict[str, float] = field(default_factory=lambda: {
        'music': 1.2,    # Music needs more careful handling
        'video': 1.5,    # Video processing is expensive to retry
        'photo': 1.0,    # Standard retry for photos
        'blog': 0.8     # Text processing can retry faster
    })


class RetryCoordinator:
    """
    🔥 ENTERPRISE RETRY COORDINATOR - CREATOR ECONOMY OPTIMIZED
    Ultra-fast retry coordination with <10ms operations
    """
    
    def __init__(self):
        self.retry_strategy = RetryStrategyManager()
        self.backoff_calculator = BackoffCalculator()
        self.retry_monitor = RetryMonitor()
        
        # Performance metrics
        self.coordination_metrics = {
            'retry_operations': 0,
            'total_coordination_time': 0.0,
            'successful_retries': 0,
            'failed_after_max_retries': 0
        }
    
    async def coordinate_retry_operations(
        self,
        operation: Callable,
        config: RetryConfig,
        context: Dict[str, Any] = None
    ) -> Any:
        """Coordinate retry operations with intelligent backoff."""
        start_time = time.perf_counter()
        
        context = context or {}
        content_type = context.get('content_type', 'unknown')
        
        # Apply content type multiplier
        effective_config = self._apply_content_type_optimization(config, content_type)
        
        last_exception = None
        
        for attempt in range(effective_config.max_attempts):
            try:
                # Execute operation
                if asyncio.iscoroutinefunction(operation):
                    result = await operation()
                else:
                    result = operation()
                
                # Record success
                await self.retry_monitor.record_success(operation.__name__, attempt)
                
                if attempt > 0:
                    self.coordination_metrics['successful_retries'] += 1
                
                coordination_time = time.perf_counter() - start_time
                self.coordination_metrics['retry_operations'] += 1
                self.coordination_metrics['total_coordination_time'] += coordination_time
                
                return result
                
            except Exception as e:
                last_exception = e
                await self.retry_monitor.record_failure(operation.__name__, attempt, str(e))
                
                # Don't wait after last attempt
                if attempt < effective_config.max_attempts - 1:
                    delay = await self.backoff_calculator.calculate_delay(
                        attempt, effective_config
                    )
                    await asyncio.sleep(delay)
        
        # All retries failed
        self.coordination_metrics['failed_after_max_retries'] += 1
        raise RetryExhaustedException(
            f"Operation failed after {effective_config.max_attempts} attempts",
            last_exception
        )
    
    def _apply_content_type_optimization(
        self, 
        config: RetryConfig, 
        content_type: str
    ) -> RetryConfig:
        """Apply Creator Economy specific optimizations."""
        multiplier = config.content_type_multipliers.get(content_type, 1.0)
        
        optimized_config = RetryConfig(
            max_attempts=config.max_attempts,
            base_delay=config.base_delay * multiplier,
            max_delay=config.max_delay * multiplier,
            jitter=config.jitter,
            strategy=config.strategy,
            content_type_multipliers=config.content_type_multipliers
        )
        
        return optimized_config


class RetryStrategyManager:
    """Manage different retry strategies."""
    
    def __init__(self):
        self.strategies = {
            RetryStrategy.FIXED_DELAY: self._fixed_delay,
            RetryStrategy.LINEAR_BACKOFF: self._linear_backoff,
            RetryStrategy.EXPONENTIAL_BACKOFF: self._exponential_backoff,
            RetryStrategy.FIBONACCI_BACKOFF: self._fibonacci_backoff,
            RetryStrategy.ADAPTIVE: self._adaptive_backoff
        }
    
    async def get_delay(self, attempt: int, config: RetryConfig) -> float:
        """Get delay for retry attempt based on strategy."""
        strategy_func = self.strategies[config.strategy]
        return await strategy_func(attempt, config)
    
    async def _fixed_delay(self, attempt: int, config: RetryConfig) -> float:
        """Fixed delay retry strategy."""
        return config.base_delay
    
    async def _linear_backoff(self, attempt: int, config: RetryConfig) -> float:
        """Linear backoff retry strategy."""
        delay = config.base_delay * (attempt + 1)
        return min(delay, config.max_delay)
    
    async def _exponential_backoff(self, attempt: int, config: RetryConfig) -> float:
        """Exponential backoff retry strategy."""
        delay = config.base_delay * (2 ** attempt)
        return min(delay, config.max_delay)
    
    async def _fibonacci_backoff(self, attempt: int, config: RetryConfig) -> float:
        """Fibonacci backoff retry strategy."""
        fib_multiplier = self._fibonacci(attempt + 1)
        delay = config.base_delay * fib_multiplier
        return min(delay, config.max_delay)
    
    async def _adaptive_backoff(self, attempt: int, config: RetryConfig) -> float:
        """Adaptive backoff based on historical performance."""
        # Start with exponential backoff
        base_delay = config.base_delay * (2 ** attempt)
        
        # Add adaptive component (simplified)
        adaptive_factor = 1.0 + (attempt * 0.1)  # Increase delay over attempts
        
        delay = base_delay * adaptive_factor
        return min(delay, config.max_delay)
    
    def _fibonacci(self, n: int) -> int:
        """Calculate Fibonacci number."""
        if n <= 2:
            return 1
        a, b = 1, 1
        for _ in range(2, n):
            a, b = b, a + b
        return b


class BackoffCalculator:
    """Calculate backoff delays with jitter and optimization."""
    
    async def calculate_delay(self, attempt: int, config: RetryConfig) -> float:
        """Calculate delay with jitter and optimization."""
        # Get base delay from strategy
        strategy_manager = RetryStrategyManager()
        base_delay = await strategy_manager.get_delay(attempt, config)
        
        # Apply jitter if enabled
        if config.jitter:
            jitter_range = base_delay * 0.1  # 10% jitter
            jitter = random.uniform(-jitter_range, jitter_range)
            base_delay += jitter
        
        # Ensure delay is positive and within bounds
        delay = max(0.1, min(base_delay, config.max_delay))
        
        return delay


class RetryMonitor:
    """Monitor retry patterns and performance."""
    
    def __init__(self):
        self.retry_stats = {}
        self.operation_history = {}
    
    async def record_success(self, operation_name: str, attempt: int):
        """Record successful retry."""
        if operation_name not in self.retry_stats:
            self.retry_stats[operation_name] = {
                'total_attempts': 0,
                'successful_retries': 0,
                'failed_operations': 0,
                'attempt_distribution': {}
            }
        
        stats = self.retry_stats[operation_name]
        stats['total_attempts'] += attempt + 1
        
        if attempt > 0:
            stats['successful_retries'] += 1
        
        # Track attempt distribution
        if attempt not in stats['attempt_distribution']:
            stats['attempt_distribution'][attempt] = 0
        stats['attempt_distribution'][attempt] += 1
    
    async def record_failure(self, operation_name: str, attempt: int, error: str):
        """Record failed retry attempt."""
        if operation_name not in self.retry_stats:
            self.retry_stats[operation_name] = {
                'total_attempts': 0,
                'successful_retries': 0,
                'failed_operations': 0,
                'attempt_distribution': {},
                'error_patterns': {}
            }
        
        stats = self.retry_stats[operation_name]
        
        # Track error patterns
        if 'error_patterns' not in stats:
            stats['error_patterns'] = {}
        if error not in stats['error_patterns']:
            stats['error_patterns'][error] = 0
        stats['error_patterns'][error] += 1
    
    async def get_retry_analytics(self) -> Dict[str, Any]:
        """Get comprehensive retry analytics."""
        analytics = {
            'operations_monitored': len(self.retry_stats),
            'operation_stats': {}
        }
        
        for operation_name, stats in self.retry_stats.items():
            total_operations = sum(stats['attempt_distribution'].values())
            
            analytics['operation_stats'][operation_name] = {
                'total_operations': total_operations,
                'retry_rate': stats['successful_retries'] / max(1, total_operations),
                'average_attempts': stats['total_attempts'] / max(1, total_operations),
                'most_common_attempt': max(
                    stats['attempt_distribution'].keys(),
                    key=lambda k: stats['attempt_distribution'][k]
                ) if stats['attempt_distribution'] else 0
            }
        
        return analytics


class RetryExhaustedException(Exception):
    """Exception raised when all retry attempts are exhausted."""
    
    def __init__(self, message: str, last_exception: Exception = None):
        super().__init__(message)
        self.last_exception = last_exception


# Convenience decorators
def retry(config: RetryConfig = None):
    """Decorator for automatic retry functionality."""
    def decorator(func):
        async def wrapper(*args, **kwargs):
            coordinator = RetryCoordinator()
            retry_config = config or RetryConfig()
            
            async def operation():
                return await func(*args, **kwargs) if asyncio.iscoroutinefunction(func) else func(*args, **kwargs)
            
            return await coordinator.coordinate_retry_operations(operation, retry_config)
        
        return wrapper
    return decorator


# Enterprise factory function
async def create_enterprise_retry_coordinator() -> RetryCoordinator:
    """Factory function for enterprise retry coordinator."""
    return RetryCoordinator()