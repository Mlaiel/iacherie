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

"""Unit tests for utils.performance_monitor module
Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.
"""
import pytest
import sys
import os
from pathlib import Path
import time
import asyncio
from unittest.mock import patch, AsyncMock
from utils.performance_monitor import PerformanceMonitor, RateLimiter, CircuitBreaker


class TestPerformanceMonitor:
    """Test cases for PerformanceMonitor class"""
    def test_init(self):
        """Test PerformanceMonitor initialization"""        monitor = PerformanceMonitor()
        assert monitor.memory_limit is None

    def test_set_memory_limit(self):
        """Test setting memory limit"""        monitor = PerformanceMonitor()
        limit = 1024 * 1024  # 1MB
        monitor.set_memory_limit(limit)
        assert monitor.memory_limit == limit

    def test_check_memory_usage(self):
        """Test memory usage check"""        monitor = PerformanceMonitor()
        usage = monitor.check_memory_usage()
        assert isinstance(usage, float)
        assert usage >= 0.0


class TestRateLimiter:
    """Test cases for RateLimiter class"""
    def test_init_default_params(self):
        """Test RateLimiter initialization with default parameters"""        limiter = RateLimiter()
        assert limiter.max_requests == 100
        assert limiter.window_seconds == 60
        assert limiter.requests == {}

    def test_init_custom_params(self):
        """Test RateLimiter initialization with custom parameters"""        max_req = 50
        window = 30
        limiter = RateLimiter(max_req, window)
        assert limiter.max_requests == max_req
        assert limiter.window_seconds == window

    @pytest.mark.asyncio
    async def test_check_rate_limit_first_request(self):
        """Test rate limit check for first request"""        limiter = RateLimiter(max_requests=5, window_seconds=60)
        result = await limiter.check_rate_limit("user1")
        assert result is True
        assert "user1" in limiter.requests
        assert len(limiter.requests["user1"]) == 1

    @pytest.mark.asyncio
    async def test_check_rate_limit_within_limit(self):
        """Test rate limit check within limit"""        limiter = RateLimiter(max_requests=5, window_seconds=60)
        
        # Make multiple requests within limit
        for _ in range(4):
            result = await limiter.check_rate_limit("user1")
            assert result is True
        
        assert len(limiter.requests["user1"]) == 4

    @pytest.mark.asyncio
    async def test_check_rate_limit_exceeds_limit(self):
        """Test rate limit check when exceeding limit"""        limiter = RateLimiter(max_requests=3, window_seconds=60)
        
        # Make requests up to limit
        for _ in range(3):
            result = await limiter.check_rate_limit("user1")
            assert result is True
        
        # Exceed limit
        result = await limiter.check_rate_limit("user1")
        assert result is False

    @pytest.mark.asyncio
    async def test_check_rate_limit_window_cleanup(self):
        """Test rate limit window cleanup"""        limiter = RateLimiter(max_requests=2, window_seconds=1)
        
        # Make requests up to limit
        for _ in range(2):
            result = await limiter.check_rate_limit("user1")
            assert result is True
        
        # Exceed limit
        result = await limiter.check_rate_limit("user1")
        assert result is False
        
        # Wait for window to pass
        await asyncio.sleep(1.1)
        
        # Should be allowed again
        result = await limiter.check_rate_limit("user1")
        assert result is True

    @pytest.mark.asyncio
    async def test_check_rate_limit_multiple_users(self):
        """Test rate limit check for multiple users"""        limiter = RateLimiter(max_requests=2, window_seconds=60)
        
        # User1 makes requests
        for _ in range(2):
            result = await limiter.check_rate_limit("user1")
            assert result is True
        
        # User2 should still be allowed
        result = await limiter.check_rate_limit("user2")
        assert result is True
        
        # User1 should be blocked
        result = await limiter.check_rate_limit("user1")
        assert result is False


class TestCircuitBreaker:
    """Test cases for CircuitBreaker class"""
    def test_init_default_params(self):
        """Test CircuitBreaker initialization with default parameters"""        breaker = CircuitBreaker()
        assert breaker.failure_threshold == 5
        assert breaker.recovery_timeout == 60
        assert breaker.failure_count == 0
        assert breaker.last_failure_time is None
        assert breaker.state == "closed"

    def test_init_custom_params(self):
        """Test CircuitBreaker initialization with custom parameters"""        threshold = 3
        timeout = 30
        breaker = CircuitBreaker(threshold, timeout)
        assert breaker.failure_threshold == threshold
        assert breaker.recovery_timeout == timeout

    @pytest.mark.asyncio
    async def test_call_successful_function(self):
        """Test circuit breaker with successful function"""        breaker = CircuitBreaker()
        
        def test_func():
            return "success"
        
        result = await breaker.call(test_func)
        assert result == "success"
        assert breaker.state == "closed"
        assert breaker.failure_count == 0

    @pytest.mark.asyncio
    async def test_call_successful_async_function(self):
        """Test circuit breaker with successful async function"""        breaker = CircuitBreaker()
        
        async def test_async_func():
            return "async_success"
        
        result = await breaker.call(test_async_func)
        assert result == "async_success"
        assert breaker.state == "closed"

    @pytest.mark.asyncio
    async def test_call_failing_function(self):
        """Test circuit breaker with failing function"""        breaker = CircuitBreaker(failure_threshold=2, recovery_timeout=60)
        
        def failing_func():
            raise ValueError("Test error")
        
        # First failure
        with pytest.raises(ValueError):
            await breaker.call(failing_func)
        assert breaker.failure_count == 1
        assert breaker.state == "closed"
        
        # Second failure - should open circuit
        with pytest.raises(ValueError):
            await breaker.call(failing_func)
        assert breaker.failure_count == 2
        assert breaker.state == "open"

    @pytest.mark.asyncio
    async def test_call_open_circuit(self):
        """Test circuit breaker when circuit is open"""        breaker = CircuitBreaker(failure_threshold=1, recovery_timeout=60)
        
        def failing_func():
            raise ValueError("Test error")
        
        # Trigger circuit to open
        with pytest.raises(ValueError):
            await breaker.call(failing_func)
        assert breaker.state == "open"
        
        # Subsequent calls should be blocked
        with pytest.raises(Exception, match="Circuit breaker is open"):
            await breaker.call(failing_func)

    @pytest.mark.asyncio
    async def test_call_recovery_timeout(self):
        """Test circuit breaker recovery after timeout"""        breaker = CircuitBreaker(failure_threshold=1, recovery_timeout=1)
        
        def failing_func():
            raise ValueError("Test error")
        
        def success_func():
            return "recovered"
        
        # Trigger circuit to open
        with pytest.raises(ValueError):
            await breaker.call(failing_func)
        assert breaker.state == "open"
        
        # Wait for recovery timeout
        await asyncio.sleep(1.1)
        
        # Should move to half-open and succeed
        result = await breaker.call(success_func)
        assert result == "recovered"
        assert breaker.state == "closed"
        assert breaker.failure_count == 0

    @pytest.mark.asyncio
    async def test_call_half_open_success(self):
        """Test circuit breaker half-open state with success"""        breaker = CircuitBreaker()
        breaker.state = "half-open"
        
        def success_func():
            return "success"
        
        result = await breaker.call(success_func)
        assert result == "success"
        assert breaker.state == "closed"
        assert breaker.failure_count == 0

    @pytest.mark.asyncio
    async def test_call_half_open_failure(self):
        """Test circuit breaker half-open state with failure"""        breaker = CircuitBreaker(failure_threshold=2)
        breaker.state = "half-open"
        breaker.failure_count = 1
        
        def failing_func():
            raise ValueError("Test error")
        
        with pytest.raises(ValueError):
            await breaker.call(failing_func)
        assert breaker.state == "open"
        assert breaker.failure_count == 2