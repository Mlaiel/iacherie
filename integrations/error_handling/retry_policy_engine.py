#!/usr/bin/env python3
"""Retry Policy Engine - Intelligent Retry Strategies
===================================================

Advanced retry policy engine for Ainflue platform error handling.
Provides intelligent retry policies with exponential backoff, jitter,
ML-based optimization, and integration with error handling infrastructure.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel - All Rights Reserved

⚠️ PROPRIÉTÉ INTELLECTUELLE EXCLUSIVE - FAHED MLAIEL ⚠️
Utilisation non autorisée strictement interdite.
Contact: mlaiel@live.de
"""

import asyncio
import logging
import time
import random
import math
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Callable, Union, Type
from dataclasses import dataclass, field
from enum import Enum
import json
from collections import defaultdict, deque

from .error_handler import ErrorHandler, ErrorSeverity, ErrorCategory

logger = logging.getLogger(__name__)


class RetryStrategy(Enum):
    """Retry strategy enumeration."""
    FIXED_DELAY = "fixed_delay"
    EXPONENTIAL_BACKOFF = "exponential_backoff"
    LINEAR_BACKOFF = "linear_backoff"
    FIBONACCI_BACKOFF = "fibonacci_backoff"
    ADAPTIVE = "adaptive"
    ML_OPTIMIZED = "ml_optimized"


class StopCondition(Enum):
    """Stop condition for retries."""
    MAX_ATTEMPTS = "max_attempts"
    MAX_DELAY = "max_delay"
    MAX_TOTAL_TIME = "max_total_time"
    CUSTOM = "custom"


@dataclass
class RetryConfig:
    """Retry policy configuration."""
    max_attempts: int = 3
    base_delay: float = 1.0
    max_delay: float = 60.0
    exponential_base: float = 2.0
    jitter_factor: float = 0.1
    strategy: RetryStrategy = RetryStrategy.EXPONENTIAL_BACKOFF
    stop_condition: StopCondition = StopCondition.MAX_ATTEMPTS
    max_total_time: float = 300.0
    retryable_exceptions: List[Type[Exception]] = field(default_factory=list)
    non_retryable_exceptions: List[Type[Exception]] = field(default_factory=list)


@dataclass
class RetryContext:
    """Context information for retry execution."""
    service_name: str
    operation_name: str
    start_time: datetime
    attempt_count: int = 0
    total_delay: float = 0.0
    exceptions: List[Exception] = field(default_factory=list)
    success_history: List[bool] = field(default_factory=list)
    timing_history: List[float] = field(default_factory=list)


@dataclass
class RetryMetrics:
    """Retry execution metrics."""
    total_executions: int = 0
    successful_executions: int = 0
    failed_executions: int = 0
    total_attempts: int = 0
    success_rate: float = 0.0
    average_attempts_to_success: float = 0.0
    average_delay_to_success: float = 0.0
    most_common_exceptions: Dict[str, int] = field(default_factory=dict)


class RetryPolicyEngine:
    """Retry policies enterprise avec exponential backoff et jitter."""
    
    def __init__(self, error_handler: Optional[ErrorHandler] = None):
        """Initialize retry policy engine.
        
        Args:
            error_handler: Optional error handler for integration
        """
        self.error_handler = error_handler
        self.retry_policies: Dict[str, RetryConfig] = {}
        self.global_config = RetryConfig()
        self.metrics: Dict[str, RetryMetrics] = defaultdict(RetryMetrics)
        self.ml_model = None  # Placeholder for ML model
        self.success_patterns: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
        self.logger = logger
        
    def register_retry_policy(self, service_name: str, config: RetryConfig):
        """Register retry policy for a specific service.
        
        Args:
            service_name: Name of the service
            config: Retry configuration
        """
        self.retry_policies[service_name] = config
        
    def get_retry_policy(self, service_name: str) -> RetryConfig:
        """Get retry policy for service.
        
        Args:
            service_name: Name of the service
            
        Returns:
            RetryConfig for the service
        """
        return self.retry_policies.get(service_name, self.global_config)
    
    async def execute_with_retry(
        self,
        func: Callable,
        context: RetryContext,
        config: Optional[RetryConfig] = None,
        *args, **kwargs
    ) -> Any:
        """Execute function with intelligent retry strategy.
        
        Args:
            func: Function to execute
            context: Retry context information
            config: Optional specific retry configuration
            *args: Function arguments
            **kwargs: Function keyword arguments
            
        Returns:
            Function result
            
        Raises:
            Exception: Last exception if all retry attempts fail
        """
        retry_config = config or self.get_retry_policy(context.service_name)
        context.start_time = datetime.now()
        
        last_exception = None
        
        for attempt in range(1, retry_config.max_attempts + 1):
            context.attempt_count = attempt
            
            try:
                start_time = time.time()
                result = await func(*args, **kwargs) if asyncio.iscoroutinefunction(func) else func(*args, **kwargs)
                execution_time = time.time() - start_time
                
                # Record successful execution
                await self._record_success(context, attempt, execution_time)
                return result
                
            except Exception as e:
                execution_time = time.time() - start_time
                context.exceptions.append(e)
                context.timing_history.append(execution_time)
                last_exception = e
                
                # Check if exception is retryable
                if not self._is_retryable_exception(e, retry_config):
                    await self._record_final_failure(context, e, attempt)
                    raise e
                
                # Check if we should continue retrying
                if attempt == retry_config.max_attempts:
                    await self._record_final_failure(context, e, attempt)
                    break
                
                if not await self._should_continue_retry(context, retry_config):
                    await self._record_early_termination(context, e, attempt)
                    break
                
                # Calculate delay and wait
                delay = await self._calculate_delay(context, attempt, retry_config, e)
                context.total_delay += delay
                
                # Integrate with error handler
                if self.error_handler:
                    await self.error_handler.handle_error(
                        exception=e,
                        context={
                            "service": context.service_name,
                            "operation": context.operation_name,
                            "attempt": attempt,
                            "max_attempts": retry_config.max_attempts,
                            "delay": delay,
                            "strategy": retry_config.strategy.value
                        },
                        severity=ErrorSeverity.MEDIUM,
                        category=self._categorize_exception(e)
                    )
                
                await asyncio.sleep(delay)
        
        # All retry attempts exhausted
        if last_exception:
            raise last_exception
    
    async def exponential_backoff_with_jitter(
        self,
        attempt: int,
        base_delay: float = 1.0,
        exponential_base: float = 2.0,
        max_delay: float = 60.0,
        jitter_factor: float = 0.1
    ) -> float:
        """Calculate exponential backoff delay with jitter.
        
        Args:
            attempt: Current attempt number
            base_delay: Base delay in seconds
            exponential_base: Exponential base for backoff
            max_delay: Maximum delay in seconds
            jitter_factor: Jitter factor (0.0 to 1.0)
            
        Returns:
            Delay in seconds
        """
        # Calculate exponential delay
        exponential_delay = base_delay * (exponential_base ** (attempt - 1))
        
        # Apply maximum delay limit
        delay = min(exponential_delay, max_delay)
        
        # Add jitter
        jitter = delay * jitter_factor * random.uniform(-1, 1)
        final_delay = max(0, delay + jitter)
        
        return final_delay
    
    async def adaptive_retry_strategies(self, context: RetryContext) -> RetryStrategy:
        """Determine adaptive retry strategy based on context and history.
        
        Args:
            context: Retry context information
            
        Returns:
            Recommended retry strategy
        """
        service_metrics = self.metrics[context.service_name]
        
        # Analyze success patterns
        if service_metrics.total_executions < 10:
            return RetryStrategy.EXPONENTIAL_BACKOFF
        
        # If high success rate with quick success, use fixed delay
        if (service_metrics.success_rate > 0.9 and 
            service_metrics.average_attempts_to_success < 2):
            return RetryStrategy.FIXED_DELAY
        
        # If moderate success rate, use exponential backoff
        if service_metrics.success_rate > 0.5:
            return RetryStrategy.EXPONENTIAL_BACKOFF
        
        # If low success rate, use adaptive strategy with longer delays
        return RetryStrategy.ADAPTIVE
    
    async def retry_policy_configuration(self) -> Dict[str, Any]:
        """Get comprehensive retry policy configuration.
        
        Returns:
            Dictionary containing all retry configurations
        """
        configuration = {
            "global_config": {
                "max_attempts": self.global_config.max_attempts,
                "base_delay": self.global_config.base_delay,
                "max_delay": self.global_config.max_delay,
                "strategy": self.global_config.strategy.value,
                "jitter_factor": self.global_config.jitter_factor
            },
            "service_configs": {},
            "optimization_suggestions": {}
        }
        
        for service_name, config in self.retry_policies.items():
            configuration["service_configs"][service_name] = {
                "max_attempts": config.max_attempts,
                "base_delay": config.base_delay,
                "max_delay": config.max_delay,
                "strategy": config.strategy.value,
                "jitter_factor": config.jitter_factor,
                "retryable_exceptions": [exc.__name__ for exc in config.retryable_exceptions],
                "non_retryable_exceptions": [exc.__name__ for exc in config.non_retryable_exceptions]
            }
            
            # Generate optimization suggestions
            suggestions = await self._generate_optimization_suggestions(service_name)
            configuration["optimization_suggestions"][service_name] = suggestions
        
        return configuration
    
    async def retry_attempt_analytics(self) -> Dict[str, Any]:
        """Analyze retry attempt patterns and performance.
        
        Returns:
            Analytics data for retry attempts
        """
        analytics = {
            "global_metrics": {
                "total_services": len(self.metrics),
                "overall_success_rate": 0.0,
                "total_executions": 0,
                "total_attempts": 0
            },
            "service_analytics": {},
            "pattern_analysis": {},
            "exception_analysis": {}
        }
        
        # Calculate global metrics
        total_executions = sum(m.total_executions for m in self.metrics.values())
        total_successful = sum(m.successful_executions for m in self.metrics.values())
        total_attempts = sum(m.total_attempts for m in self.metrics.values())
        
        analytics["global_metrics"]["total_executions"] = total_executions
        analytics["global_metrics"]["total_attempts"] = total_attempts
        analytics["global_metrics"]["overall_success_rate"] = (
            total_successful / total_executions if total_executions > 0 else 0.0
        )
        
        # Service-specific analytics
        for service_name, metrics in self.metrics.items():
            analytics["service_analytics"][service_name] = {
                "success_rate": metrics.success_rate,
                "total_executions": metrics.total_executions,
                "average_attempts": metrics.average_attempts_to_success,
                "average_delay": metrics.average_delay_to_success,
                "most_common_exceptions": dict(metrics.most_common_exceptions)
            }
        
        # Pattern analysis
        analytics["pattern_analysis"] = await self._analyze_success_patterns()
        
        # Exception analysis
        analytics["exception_analysis"] = await self._analyze_exception_patterns()
        
        return analytics
    
    async def failure_pattern_learning(self) -> Dict[str, Any]:
        """Learn from failure patterns to improve retry strategies.
        
        Returns:
            Learned patterns and recommendations
        """
        learning_results = {
            "learned_patterns": {},
            "strategy_recommendations": {},
            "configuration_adjustments": {}
        }
        
        for service_name, metrics in self.metrics.items():
            if metrics.total_executions < 5:
                continue
            
            # Analyze failure patterns
            patterns = await self._extract_failure_patterns(service_name)
            learning_results["learned_patterns"][service_name] = patterns
            
            # Generate strategy recommendations
            recommendations = await self._generate_strategy_recommendations(service_name, patterns)
            learning_results["strategy_recommendations"][service_name] = recommendations
            
            # Suggest configuration adjustments
            adjustments = await self._suggest_config_adjustments(service_name, metrics)
            learning_results["configuration_adjustments"][service_name] = adjustments
        
        return learning_results
    
    async def retry_coordination_across_services(self) -> Dict[str, Any]:
        """Coordinate retry policies across multiple services.
        
        Returns:
            Coordination results and recommendations
        """
        coordination = {
            "service_dependencies": {},
            "cascading_retry_prevention": {},
            "coordinated_backoff": {},
            "resource_contention_analysis": {}
        }
        
        # Analyze service interaction patterns
        for service_name in self.metrics.keys():
            # Identify services that might be affected by retries
            dependent_services = await self._identify_dependent_services(service_name)
            coordination["service_dependencies"][service_name] = dependent_services
            
            # Generate cascading retry prevention strategies
            prevention_strategies = await self._generate_cascading_prevention(service_name)
            coordination["cascading_retry_prevention"][service_name] = prevention_strategies
        
        # Analyze resource contention
        coordination["resource_contention_analysis"] = await self._analyze_resource_contention()
        
        return coordination
    
    async def _calculate_delay(
        self,
        context: RetryContext,
        attempt: int,
        config: RetryConfig,
        exception: Exception
    ) -> float:
        """Calculate delay for next retry attempt.
        
        Args:
            context: Retry context
            attempt: Current attempt number
            config: Retry configuration
            exception: Exception that occurred
            
        Returns:
            Delay in seconds
        """
        if config.strategy == RetryStrategy.FIXED_DELAY:
            return config.base_delay
        
        elif config.strategy == RetryStrategy.EXPONENTIAL_BACKOFF:
            return await self.exponential_backoff_with_jitter(
                attempt, config.base_delay, config.exponential_base,
                config.max_delay, config.jitter_factor
            )
        
        elif config.strategy == RetryStrategy.LINEAR_BACKOFF:
            linear_delay = config.base_delay * attempt
            jitter = linear_delay * config.jitter_factor * random.uniform(-1, 1)
            return max(0, min(linear_delay + jitter, config.max_delay))
        
        elif config.strategy == RetryStrategy.FIBONACCI_BACKOFF:
            fib_delay = config.base_delay * self._fibonacci(attempt)
            jitter = fib_delay * config.jitter_factor * random.uniform(-1, 1)
            return max(0, min(fib_delay + jitter, config.max_delay))
        
        elif config.strategy == RetryStrategy.ADAPTIVE:
            return await self._calculate_adaptive_delay(context, attempt, config)
        
        elif config.strategy == RetryStrategy.ML_OPTIMIZED:
            return await self._calculate_ml_optimized_delay(context, attempt, exception)
        
        else:
            return config.base_delay
    
    def _fibonacci(self, n: int) -> int:
        """Calculate nth Fibonacci number."""
        if n <= 1:
            return 1
        a, b = 1, 1
        for _ in range(2, n + 1):
            a, b = b, a + b
        return b
    
    async def _calculate_adaptive_delay(
        self,
        context: RetryContext,
        attempt: int,
        config: RetryConfig
    ) -> float:
        """Calculate adaptive delay based on context and history."""
        service_metrics = self.metrics[context.service_name]
        
        # Base exponential backoff
        base_delay = await self.exponential_backoff_with_jitter(
            attempt, config.base_delay, config.exponential_base,
            config.max_delay, config.jitter_factor
        )
        
        # Adjust based on service success rate
        if service_metrics.success_rate > 0.8:
            # High success rate, reduce delay
            adjustment_factor = 0.7
        elif service_metrics.success_rate > 0.5:
            # Moderate success rate, normal delay
            adjustment_factor = 1.0
        else:
            # Low success rate, increase delay
            adjustment_factor = 1.5
        
        return min(base_delay * adjustment_factor, config.max_delay)
    
    async def _calculate_ml_optimized_delay(
        self,
        context: RetryContext,
        attempt: int,
        exception: Exception
    ) -> float:
        """Calculate ML-optimized delay (placeholder for ML implementation)."""
        # In a real implementation, this would use an ML model
        # For now, fall back to adaptive strategy
        config = self.get_retry_policy(context.service_name)
        return await self._calculate_adaptive_delay(context, attempt, config)
    
    def _is_retryable_exception(self, exception: Exception, config: RetryConfig) -> bool:
        """Check if exception is retryable based on configuration."""
        # Check non-retryable exceptions first
        for non_retryable in config.non_retryable_exceptions:
            if isinstance(exception, non_retryable):
                return False
        
        # If retryable exceptions are specified, check them
        if config.retryable_exceptions:
            for retryable in config.retryable_exceptions:
                if isinstance(exception, retryable):
                    return True
            return False
        
        # Default retryable exceptions (common transient errors)
        retryable_types = (
            ConnectionError,
            TimeoutError,
            OSError,
        )
        
        return isinstance(exception, retryable_types)
    
    async def _should_continue_retry(self, context: RetryContext, config: RetryConfig) -> bool:
        """Check if retry should continue based on stop conditions."""
        # Check max total time
        if config.stop_condition == StopCondition.MAX_TOTAL_TIME:
            elapsed_time = (datetime.now() - context.start_time).total_seconds()
            if elapsed_time >= config.max_total_time:
                return False
        
        # Check max delay
        if config.stop_condition == StopCondition.MAX_DELAY:
            if context.total_delay >= config.max_delay:
                return False
        
        return True
    
    def _categorize_exception(self, exception: Exception) -> ErrorCategory:
        """Categorize exception for error handling integration."""
        if isinstance(exception, (ConnectionError, OSError)):
            return ErrorCategory.NETWORK
        elif isinstance(exception, TimeoutError):
            return ErrorCategory.TIMEOUT
        elif isinstance(exception, ValueError):
            return ErrorCategory.VALIDATION
        else:
            return ErrorCategory.UNKNOWN
    
    async def _record_success(self, context: RetryContext, attempts: int, execution_time: float):
        """Record successful execution metrics."""
        service_metrics = self.metrics[context.service_name]
        service_metrics.total_executions += 1
        service_metrics.successful_executions += 1
        service_metrics.total_attempts += attempts
        
        # Update success rate
        service_metrics.success_rate = (
            service_metrics.successful_executions / service_metrics.total_executions
        )
        
        # Update average attempts to success
        service_metrics.average_attempts_to_success = (
            service_metrics.total_attempts / service_metrics.successful_executions
        )
        
        # Update average delay to success
        service_metrics.average_delay_to_success = (
            context.total_delay / service_metrics.successful_executions
        )
        
        # Record success pattern
        self.success_patterns[context.service_name].append({
            "attempts": attempts,
            "total_delay": context.total_delay,
            "execution_time": execution_time,
            "timestamp": datetime.now().isoformat()
        })
    
    async def _record_final_failure(self, context: RetryContext, exception: Exception, attempts: int):
        """Record final failure metrics."""
        service_metrics = self.metrics[context.service_name]
        service_metrics.total_executions += 1
        service_metrics.failed_executions += 1
        service_metrics.total_attempts += attempts
        
        # Update success rate
        service_metrics.success_rate = (
            service_metrics.successful_executions / service_metrics.total_executions
        )
        
        # Update exception tracking
        exception_name = type(exception).__name__
        service_metrics.most_common_exceptions[exception_name] = (
            service_metrics.most_common_exceptions.get(exception_name, 0) + 1
        )
    
    async def _record_early_termination(self, context: RetryContext, exception: Exception, attempts: int):
        """Record early termination metrics."""
        await self._record_final_failure(context, exception, attempts)
    
    async def _generate_optimization_suggestions(self, service_name: str) -> List[str]:
        """Generate optimization suggestions for service retry policy."""
        suggestions = []
        metrics = self.metrics[service_name]
        
        if metrics.total_executions < 5:
            return ["Insufficient data for optimization suggestions"]
        
        if metrics.success_rate < 0.5:
            suggestions.append("Consider increasing max_attempts or base_delay")
        
        if metrics.average_attempts_to_success > 3:
            suggestions.append("Consider adjusting retry strategy or increasing delays")
        
        if metrics.success_rate > 0.9 and metrics.average_attempts_to_success < 1.5:
            suggestions.append("Consider reducing max_attempts for faster failure")
        
        return suggestions
    
    async def _analyze_success_patterns(self) -> Dict[str, Any]:
        """Analyze success patterns across services."""
        patterns = {}
        
        for service_name, success_list in self.success_patterns.items():
            if len(success_list) < 3:
                continue
            
            attempts = [s["attempts"] for s in success_list]
            delays = [s["total_delay"] for s in success_list]
            
            patterns[service_name] = {
                "average_successful_attempts": sum(attempts) / len(attempts),
                "average_successful_delay": sum(delays) / len(delays),
                "success_on_first_attempt_rate": sum(1 for a in attempts if a == 1) / len(attempts),
                "max_attempts_to_success": max(attempts),
                "min_attempts_to_success": min(attempts)
            }
        
        return patterns
    
    async def _analyze_exception_patterns(self) -> Dict[str, Any]:
        """Analyze exception patterns across services."""
        all_exceptions = defaultdict(int)
        
        for service_metrics in self.metrics.values():
            for exception_name, count in service_metrics.most_common_exceptions.items():
                all_exceptions[exception_name] += count
        
        return dict(all_exceptions)
    
    async def _extract_failure_patterns(self, service_name: str) -> Dict[str, Any]:
        """Extract failure patterns for a specific service."""
        metrics = self.metrics[service_name]
        
        return {
            "failure_rate": 1.0 - metrics.success_rate,
            "most_common_exception": max(
                metrics.most_common_exceptions.items(),
                key=lambda x: x[1],
                default=("None", 0)
            )[0],
            "retry_effectiveness": (
                metrics.successful_executions / max(metrics.total_attempts, 1)
            )
        }
    
    async def _generate_strategy_recommendations(
        self,
        service_name: str,
        patterns: Dict[str, Any]
    ) -> List[str]:
        """Generate strategy recommendations based on patterns."""
        recommendations = []
        
        if patterns["failure_rate"] > 0.5:
            recommendations.append("Consider circuit breaker pattern for this service")
        
        if patterns["retry_effectiveness"] < 0.3:
            recommendations.append("Current retry strategy is ineffective, consider alternative approach")
        
        return recommendations
    
    async def _suggest_config_adjustments(
        self,
        service_name: str,
        metrics: RetryMetrics
    ) -> Dict[str, Any]:
        """Suggest configuration adjustments based on metrics."""
        adjustments = {}
        
        if metrics.success_rate < 0.3:
            adjustments["max_attempts"] = "increase"
            adjustments["base_delay"] = "increase"
        
        if metrics.average_attempts_to_success > 4:
            adjustments["strategy"] = "use_adaptive_or_ml_optimized"
        
        return adjustments
    
    async def _identify_dependent_services(self, service_name: str) -> List[str]:
        """Identify services that depend on the given service."""
        # Placeholder implementation
        return []
    
    async def _generate_cascading_prevention(self, service_name: str) -> List[str]:
        """Generate strategies to prevent cascading retry failures."""
        return [
            f"Implement exponential backoff for {service_name}",
            f"Add jitter to prevent thundering herd",
            f"Consider circuit breaker coordination with dependent services"
        ]
    
    async def _analyze_resource_contention(self) -> Dict[str, Any]:
        """Analyze resource contention from retry patterns."""
        return {
            "high_retry_services": [
                service for service, metrics in self.metrics.items()
                if metrics.average_attempts_to_success > 3
            ],
            "recommendations": [
                "Consider implementing retry coordination to prevent resource exhaustion",
                "Monitor system resources during high retry periods"
            ]
        }