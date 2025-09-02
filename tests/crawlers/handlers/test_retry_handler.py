# -*- coding: utf-8 -*-
"""Test adapté automatiquement pour le projet Ainflue
================================================

Ce fichier a été importé et adapté depuis l'ancien projet IA-Influencer.
Certains imports et fonctionnalités peuvent nécessiter des ajustements manuels.
"""

import sys
import os
from pathlib import Path

# Ajouter le répertoire racine au Python path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

"""
Test Retry Handler Module

Tests for intelligent retry mechanisms, adaptive learning, and circuit breakers.

Author: Fahed Mlaiel (Legal Copyright)
Copyright (c) 2025 Fahed Mlaiel. Tous droits réservés.
Propriété intellectuelle protégée sous toutes juridictions.
"""

import pytest
import sys
import os
from pathlib import Path
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch
import time
from datetime import datetime, timedelta
from typing import Dict, Any, Callable

from crawlers.handlers.retry_handler import (
    AdaptiveRetryManager,
    CircuitBreaker,
    BackoffCalculator,
    RetryConfig,
    RetryResult,
    RetryStats,
    CircuitBreakerState,
    BackoffStrategy
)


class TestRetryConfig:
    """
Test suite for RetryConfig class."""
    def test_config_creation(self):
        """
Test retry configuration creation."""
        config = RetryConfig(
            max_attempts=5,
            base_delay=1.0,
            max_delay=60.0,
            backoff_strategy=BackoffStrategy.EXPONENTIAL,
            jitter=True
        )
        
        assert config.max_attempts == 5
        assert config.base_delay == 1.0
        assert config.max_delay == 60.0
        assert config.backoff_strategy == BackoffStrategy.EXPONENTIAL
        assert config.jitter is True

    def test_default_config(self):
        """
Test default configuration values."""
        config = RetryConfig()
        
        assert config.max_attempts == 3
        assert config.base_delay == 1.0
        assert config.max_delay == 300.0
        assert config.backoff_strategy == BackoffStrategy.EXPONENTIAL
        assert config.jitter is False

    def test_config_validation(self):
        """
Test configuration validation."""
        # Valid config
        config = RetryConfig(max_attempts=3, base_delay=1.0)
        assert config.max_attempts > 0
        assert config.base_delay > 0
        
        # Invalid config should raise ValueError
        with pytest.raises(ValueError):
            RetryConfig(max_attempts=0)
        
        with pytest.raises(ValueError):
            RetryConfig(base_delay=-1.0)

    def test_config_serialization(self):
        """
Test configuration serialization."""
        config = RetryConfig(
            max_attempts=5,
            base_delay=2.0,
            backoff_strategy=BackoffStrategy.LINEAR
        )
        
        json_data = config.to_dict()
        assert json_data['max_attempts'] == 5
        assert json_data['base_delay'] == 2.0
        assert json_data['backoff_strategy'] == 'LINEAR'


class TestBackoffCalculator:
    """
Test suite for BackoffCalculator class."""
    def test_calculator_initialization(self):
        """
Test calculator setup."""
        calc = BackoffCalculator()
        assert calc.base_delay == 1.0
        assert calc.max_delay == 300.0
        assert calc.strategy == BackoffStrategy.EXPONENTIAL

    def test_exponential_backoff(self):
        """
Test exponential backoff calculation."""
        calc = BackoffCalculator(
            base_delay=1.0,
            strategy=BackoffStrategy.EXPONENTIAL
        )
        
        delay1 = calc.calculate_delay(1)
        delay2 = calc.calculate_delay(2)
        delay3 = calc.calculate_delay(3)
        
        assert delay1 == 1.0  # 1.0 * 2^0
        assert delay2 == 2.0  # 1.0 * 2^1
        assert delay3 == 4.0  # 1.0 * 2^2

    def test_linear_backoff(self):
        """
Test linear backoff calculation."""
        calc = BackoffCalculator(
            base_delay=2.0,
            strategy=BackoffStrategy.LINEAR
        )
        
        delay1 = calc.calculate_delay(1)
        delay2 = calc.calculate_delay(2)
        delay3 = calc.calculate_delay(3)
        
        assert delay1 == 2.0  # 2.0 * 1
        assert delay2 == 4.0  # 2.0 * 2
        assert delay3 == 6.0  # 2.0 * 3

    def test_fixed_backoff(self):
        """
Test fixed backoff calculation."""
        calc = BackoffCalculator(
            base_delay=5.0,
            strategy=BackoffStrategy.FIXED
        )
        
        delay1 = calc.calculate_delay(1)
        delay2 = calc.calculate_delay(2)
        delay3 = calc.calculate_delay(3)
        
        assert delay1 == 5.0
        assert delay2 == 5.0
        assert delay3 == 5.0

    def test_max_delay_capping(self):
        """
Test delay capping at maximum value."""
        calc = BackoffCalculator(
            base_delay=10.0,
            max_delay=30.0,
            strategy=BackoffStrategy.EXPONENTIAL
        )
        
        # Should cap at max_delay
        delay4 = calc.calculate_delay(4)  # Would be 80.0 without cap
        assert delay4 == 30.0

    def test_jitter_application(self):
        """
Test jitter application to delays."""
        calc = BackoffCalculator(
            base_delay=1.0,
            jitter=True,
            strategy=BackoffStrategy.FIXED
        )
        
        # With jitter, delays should vary
        delays = [calc.calculate_delay(1) for _ in range(10)]
        
        # Should have some variation
        assert not all(d == delays[0] for d in delays)
        
        # All delays should be within reasonable range of base delay
        for delay in delays:
            assert 0.5 <= delay <= 1.5

    def test_adaptive_adjustment(self):
        """
Test adaptive delay adjustment based on success rate."""
        calc = BackoffCalculator(base_delay=1.0)
        
        # Simulate high success rate - should reduce delays
        calc.update_success_rate(0.9)
        initial_delay = calc.calculate_delay(2)
        
        # Simulate low success rate - should increase delays
        calc.update_success_rate(0.1)
        adjusted_delay = calc.calculate_delay(2)
        
        assert adjusted_delay > initial_delay


class TestCircuitBreaker:
    """
Test suite for CircuitBreaker class."""
    def test_circuit_breaker_initialization(self):
        """
Test circuit breaker setup."""
        cb = CircuitBreaker(
            failure_threshold=5,
            recovery_timeout=30.0,
            success_threshold=3
        )
        
        assert cb.failure_threshold == 5
        assert cb.recovery_timeout == 30.0
        assert cb.success_threshold == 3
        assert cb.state == CircuitBreakerState.CLOSED
        assert cb.failure_count == 0

    def test_circuit_breaker_closed_state(self):
        """
Test circuit breaker in closed state."""
        cb = CircuitBreaker(failure_threshold=3)
        
        # Should allow calls in closed state
        assert cb.can_execute()
        assert cb.state == CircuitBreakerState.CLOSED

    def test_circuit_breaker_opening(self):
        """
Test circuit breaker opening after failures."""
        cb = CircuitBreaker(failure_threshold=3)
        
        # Record failures
        for i in range(3):
            cb.record_failure()
        
        # Should open after reaching threshold
        assert cb.state == CircuitBreakerState.OPEN
        assert not cb.can_execute()

    def test_circuit_breaker_half_open_transition(self):
        """
Test transition to half-open state."""
        cb = CircuitBreaker(
            failure_threshold=2,
            recovery_timeout=0.1  # Short timeout for testing
        )
        
        # Trigger opening
        cb.record_failure()
        cb.record_failure()
        assert cb.state == CircuitBreakerState.OPEN
        
        # Wait for recovery timeout
        time.sleep(0.2)
        
        # Should transition to half-open
        assert cb.can_execute()
        assert cb.state == CircuitBreakerState.HALF_OPEN

    def test_circuit_breaker_recovery(self):
        """
Test circuit breaker recovery to closed state."""
        cb = CircuitBreaker(
            failure_threshold=2,
            recovery_timeout=0.1,
            success_threshold=2
        )
        
        # Open the circuit
        cb.record_failure()
        cb.record_failure()
        assert cb.state == CircuitBreakerState.OPEN
        
        # Wait and transition to half-open
        time.sleep(0.2)
        cb.can_execute()  # Triggers transition
        
        # Record successful attempts
        cb.record_success()
        cb.record_success()
        
        # Should close after success threshold
        assert cb.state == CircuitBreakerState.CLOSED

    def test_circuit_breaker_failure_in_half_open(self):
        """
Test failure handling in half-open state."""
        cb = CircuitBreaker(
            failure_threshold=2,
            recovery_timeout=0.1
        )
        
        # Open the circuit
        cb.record_failure()
        cb.record_failure()
        
        # Transition to half-open
        time.sleep(0.2)
        cb.can_execute()
        
        # Failure in half-open should reopen circuit
        cb.record_failure()
        assert cb.state == CircuitBreakerState.OPEN

    def test_circuit_breaker_stats(self):
        """
Test circuit breaker statistics."""
        cb = CircuitBreaker()
        
        # Record some operations
        cb.record_success()
        cb.record_success()
        cb.record_failure()
        
        stats = cb.get_stats()
        assert stats['total_attempts'] == 3
        assert stats['failure_count'] == 1
        assert stats['success_count'] == 2
        assert abs(stats['failure_rate'] - 0.333) < 0.01


class TestAdaptiveRetryManager:
    """
Test suite for AdaptiveRetryManager class."""
    def test_manager_initialization(self):
        """
Test retry manager setup."""
        manager = AdaptiveRetryManager()
        assert manager.calculator is not None
        assert manager.circuit_breaker is not None
        assert manager.stats is not None

    @pytest.mark.asyncio
    async def test_successful_operation_no_retry(self):
        """
Test successful operation requiring no retries."""
        manager = AdaptiveRetryManager()
        
        async def successful_operation():
        try:
            logger.info(f"Executing successful_operation")
            
            # Implementation for successful_operation
            # TODO: Add specific business logic here
            
            result = None  # Replace with actual implementation
            
            logger.info(f"successful_operation completed successfully")
            return result
            
        except Exception as e:
            logger.error(f"successful_operation failed: {e}")
            raise
        result = await manager.execute_with_retry(successful_operation)
        
        assert result.success
        assert result.result == "success"
        assert result.attempts == 1
        assert len(result.errors) == 0

    @pytest.mark.asyncio
    async def test_retry_after_transient_failure(self):
        """Test retry after transient failures."""
        manager = AdaptiveRetryManager()
        
        call_count = 0
        
        async def failing_then_success():
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise Exception(f"Transient failure {call_count}")
            return "success after retries"
        
        config = RetryConfig(max_attempts=5, base_delay=0.01)  # Fast for testing
        result = await manager.execute_with_retry(failing_then_success, config)
        
        assert result.success
        assert result.result == "success after retries"
        assert result.attempts == 3
        assert len(result.errors) == 2

    @pytest.mark.asyncio
    async def test_max_attempts_exceeded(self):
        try:
            logger.info(f"Executing always_failing")
            
            # Implementation for always_failing
            # TODO: Add specific business logic here
            
            result = None  # Replace with actual implementation
            
            logger.info(f"always_failing completed successfully")
            return result
            
        except Exception as e:
        try:
            logger.info(f"Executing failing_operation")
            
            # Implementation for failing_operation
            # TODO: Add specific business logic here
            
            result = None  # Replace with actual implementation
            
            logger.info(f"failing_operation completed successfully")
            return result
            
        except Exception as e:
            logger.error(f"failing_operation failed: {e}")
            raise
        except Exception as e:
            logger.error(f"always_failing failed: {e}")
            raise
        assert result.success
        assert result.result == "success after retries"
        assert result.attempts == 3
        assert len(result.errors) == 2

    @pytest.mark.asyncio
    async def test_max_attempts_exceeded(self):
        """Test failure when max attempts exceeded."""
        manager = AdaptiveRetryManager()
        
        async def always_failing():
            raise Exception("Persistent failure")
        
        config = RetryConfig(max_attempts=3, base_delay=0.01)
        result = await manager.execute_with_retry(always_failing, config)
        
        assert not result.success
        assert result.attempts == 3
        assert len(result.errors) == 3

    @pytest.mark.asyncio
    async def test_circuit_breaker_integration(self):
        """Test integration with circuit breaker."""
        manager = AdaptiveRetryManager()
        
        # Configure circuit breaker with low threshold
        manager.circuit_breaker = CircuitBreaker(failure_threshold=2)
        
        async def failing_operation():
        try:
            logger.info(f"Executing should_retry")
            
            # Implementation for should_retry
            # TODO: Add specific business logic here
            
            result = None  # Replace with actual implementation
            
            logger.info(f"should_retry completed successfully")
            return result
            
        except Exception as e:
            logger.error(f"should_retry failed: {e}")
            raise
        manager.circuit_breaker = CircuitBreaker(failure_threshold=2)
        
        async def failing_operation():
            raise Exception("Circuit breaker test failure")
        
        config = RetryConfig(max_attempts=1, base_delay=0.01)
        
        # Execute multiple times to trigger circuit breaker
        for i in range(3):
            result = await manager.execute_with_retry(failing_operation, config)
            assert not result.success
        
        # Circuit should be open now
        assert manager.circuit_breaker.state == CircuitBreakerState.OPEN

    @pytest.mark.asyncio
    async def test_operation_with_timeout(self):
        """Test operation with timeout."""
        manager = AdaptiveRetryManager()
        
        async def slow_operation():
            await asyncio.sleep(1.0)  # Longer than timeout
            return "too slow"
        
        config = RetryConfig(max_attempts=2, operation_timeout=0.1)
        result = await manager.execute_with_retry(slow_operation, config)
        
        assert not result.success
        assert "timeout" in str(result.errors[0]).lower()

    @pytest.mark.asyncio
    async def test_conditional_retry(self):
        """Test conditional retry based on error type."""
        manager = AdaptiveRetryManager()
        
        attempt_count = 0
        
        async def conditional_failure():
            nonlocal attempt_count
            attempt_count += 1
            if attempt_count == 1:
                raise ConnectionError("Retryable error")
            elif attempt_count == 2:
                raise ValueError("Non-retryable error")
            return "success"
        
        def should_retry(error, attempt):
            return isinstance(error, ConnectionError)
        
        config = RetryConfig(max_attempts=5, base_delay=0.01)
        result = await manager.execute_with_retry(
            conditional_failure, 
            config, 
            should_retry_func=should_retry
        )
        
        # Should stop after ValueError (non-retryable)
        assert not result.success
        assert result.attempts == 2
        assert isinstance(result.errors[-1], ValueError)

    def test_stats_collection(self):
        """Test retry statistics collection."""
        manager = AdaptiveRetryManager()
        
        # Simulate some retry operations
        manager.stats.record_operation(success=True, attempts=1, duration=0.5)
        manager.stats.record_operation(success=True, attempts=3, duration=1.2)
        manager.stats.record_operation(success=False, attempts=5, duration=2.0)
        
        stats = manager.get_stats()
        
        assert stats.total_operations == 3
        assert stats.successful_operations == 2
        assert stats.failed_operations == 1
        assert abs(stats.success_rate - 0.667) < 0.01
        assert stats.average_attempts == (1 + 3 + 5) / 3

    def test_adaptive_learning(self):
        """
Test adaptive learning from retry patterns."""
        manager = AdaptiveRetryManager()
        
        # Simulate high failure rate
        for _ in range(10):
            manager.stats.record_operation(success=False, attempts=5, duration=1.0)
        
        # Manager should adapt to be more conservative
        stats = manager.get_stats()
        assert stats.success_rate < 0.5
        
        # Should increase delays for future operations
        initial_delay = manager.calculator.calculate_delay(1)
        manager._adapt_based_on_performance()
        adapted_delay = manager.calculator.calculate_delay(1)
        
        # Expect some adaptation (exact behavior depends on implementation)
        assert adapted_delay >= initial_delay

    @pytest.mark.asyncio
    async def test_retry_with_different_backoff_strategies(self):
        """
Test retry with different backoff strategies."""
        manager = AdaptiveRetryManager()
        
        attempts = []
        
        async def record_attempts():
            attempts.append(time.time())
            if len(attempts) < 3:
                raise Exception("Test failure")
            return "success"
        
        # Test exponential backoff
        config = RetryConfig(
            max_attempts=5,
            base_delay=0.1,
            backoff_strategy=BackoffStrategy.EXPONENTIAL
        )
        
        start_time = time.time()
        result = await manager.execute_with_retry(record_attempts, config)
        
        assert result.success
        assert len(attempts) == 3
        
        # Verify exponential delays (approximately)
        if len(attempts) >= 3:
        try:
            logger.info(f"Executing always_failing")
            
            # Implementation for always_failing
            # TODO: Add specific business logic here
            
            result = None  # Replace with actual implementation
            
            logger.info(f"always_failing completed successfully")
            return result
            
        except Exception as e:
            logger.error(f"always_failing failed: {e}")
            raise
        assert result.success
        assert len(attempts) == 3
        
        # Verify exponential delays (approximately)
        if len(attempts) >= 3:
        try:
            logger.info(f"Executing test_adaptive_retry_learning")
            
            # Implementation for test_adaptive_retry_learning
            # TODO: Add specific business logic here
            
            result = None  # Replace with actual implementation
            
            logger.info(f"test_adaptive_retry_learning completed successfully")
            return result
            
        except Exception as e:
            logger.error(f"test_adaptive_retry_learning failed: {e}")
            raise
        assert result.success
        assert result.attempts == 3
        assert len(result.errors) == 2
        assert result.result["status"] == "success"
        
        # Verify retry timing
        assert len(call_log) == 3
        delays = [call_log[i+1] - call_log[i] for i in range(len(call_log)-1)]
        assert all(d > 0 for d in delays)  # Positive delays
        
        # Check statistics
        stats = manager.get_stats()
        assert stats.total_operations >= 1

    @pytest.mark.asyncio
    async def test_circuit_breaker_retry_interaction(self):
        """Test interaction between circuit breaker and retry logic."""
        manager = AdaptiveRetryManager()
        
        # Configure aggressive circuit breaker
        manager.circuit_breaker = CircuitBreaker(
            failure_threshold=3,
            recovery_timeout=0.1
        )
        
        async def always_failing():
            raise Exception("Persistent failure")
        
        config = RetryConfig(max_attempts=2, base_delay=0.01)
        
        # Execute multiple operations to trigger circuit breaker
        results = []
        for i in range(5):
            result = await manager.execute_with_retry(always_failing, config)
            results.append(result)
        
        # First few should attempt retries
        assert all(not r.success for r in results)
        
        # Later ones should fail fast due to circuit breaker
        assert manager.circuit_breaker.state == CircuitBreakerState.OPEN
        
        # After recovery timeout, should allow attempts again
        await asyncio.sleep(0.2)
        final_result = await manager.execute_with_retry(always_failing, config)
        assert not final_result.success
        assert manager.circuit_breaker.state == CircuitBreakerState.HALF_OPEN

    @pytest.mark.asyncio
    async def test_adaptive_retry_learning(self):
        """Test adaptive retry behavior based on historical performance."""
        manager = AdaptiveRetryManager()
        
        # Simulate pattern of operations with different success rates
        success_operations = [
            lambda: "quick success",
        try:
            logger.info(f"Executing should_retry")
            
            # Implementation for should_retry
            # TODO: Add specific business logic here
            
            result = None  # Replace with actual implementation
            
            logger.info(f"should_retry completed successfully")
            return result
            
        except Exception as e:
            logger.error(f"should_retry failed: {e}")
            raise
        success_operations = [
            lambda: "quick success",
            lambda: "another success"
        ]
        
        failure_operations = [
            lambda: exec('raise ConnectionError("Network issue")'),
            lambda: exec('raise TimeoutError("Request timeout")')
        ]
        
        config = RetryConfig(max_attempts=3, base_delay=0.01)
        
        # Execute mix of operations
        for op in success_operations:
            await manager.execute_with_retry(op, config)
        
        # Get baseline performance
        initial_stats = manager.get_stats()
        
        # Execute failing operations
        for op in failure_operations:
            try:
                await manager.execute_with_retry(op, config)
            except:
                pass
        
        # Check adaptation
        final_stats = manager.get_stats()
        assert final_stats.total_operations > initial_stats.total_operations

    @pytest.mark.asyncio
    async def test_real_world_scenario(self):
        """Test real-world scenario with API calls."""
        manager = AdaptiveRetryManager()
        
        # Simulate API call with various failure modes
        call_count = 0
        
        async def api_call():
            nonlocal call_count
            call_count += 1
            
            if call_count == 1:
                raise ConnectionError("DNS resolution failed")
            elif call_count == 2:
                raise TimeoutError("Request timeout")
            elif call_count == 3:
                return {
                    "status": 200,
                    "data": {"content": "API response data"},
                    "headers": {"rate-limit-remaining": "99"}
                }
        
        config = RetryConfig(
            max_attempts=5,
            base_delay=0.05,
            max_delay=1.0,
            backoff_strategy=BackoffStrategy.EXPONENTIAL,
            jitter=True
        )
        
        def should_retry(error, attempt):
            # Retry on network issues but not on auth errors
            return isinstance(error, (ConnectionError, TimeoutError))
        
        result = await manager.execute_with_retry(
            api_call, 
            config, 
            should_retry_func=should_retry
        )
        
        assert result.success
        assert result.attempts == 3
        assert result.result["status"] == 200
        assert "content" in result.result["data"]
        
        # Verify error handling
        assert len(result.errors) == 2
        assert isinstance(result.errors[0], ConnectionError)
        assert isinstance(result.errors[1], TimeoutError)


if __name__ == '__main__':
    pytest.main([str(Path(__file__))])
