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
Test Error Handler Module

Tests for comprehensive error handling, classification, and recovery mechanisms.

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
import json
from datetime import datetime, timedelta
from typing import Dict, Any, List

from crawlers.handlers.error_handler import (
    ErrorClassifier,
    ErrorRecoveryManager,
    ErrorAggregator,
    CrawlerError,
    ErrorCategory,
    ErrorSeverity,
    RecoveryStrategy,
    ErrorContext,
    ErrorStats,
    AlertLevel
)


class TestCrawlerError:
    """
Test suite for CrawlerError class."""
    def test_error_creation(self):
        """
Test error object creation."""
        error = CrawlerError(
            error_id="test-001",
            message="Test error message",
            category=ErrorCategory.NETWORK,
            severity=ErrorSeverity.HIGH,
            context={"url": "https://example.com", "status_code": 500}
        )
        
        assert error.error_id == "test-001"
        assert error.message == "Test error message"
        assert error.category == ErrorCategory.NETWORK
        assert error.severity == ErrorSeverity.HIGH
        assert error.context["url"] == "https://example.com"
        assert isinstance(error.timestamp, datetime)

    def test_error_serialization(self):
        """Test error JSON serialization."""
        error = CrawlerError(
            error_id="test-002",
            message="Serialization test",
            category=ErrorCategory.VALIDATION,
            severity=ErrorSeverity.MEDIUM
        )
        
        json_data = error.to_json()
        assert 'error_id' in json_data
        assert 'message' in json_data
        assert 'category' in json_data
        assert 'severity' in json_data
        assert 'timestamp' in json_data

    def test_error_from_exception(self):
        """Test creating error from exception."""
        try:
            raise ValueError("Test exception")
        except Exception as e:
            error = CrawlerError.from_exception("exc-001", e, ErrorCategory.VALIDATION)
            
            assert error.error_id == "exc-001"
            assert "ValueError" in error.message
            assert "Test exception" in error.message
            assert error.category == ErrorCategory.VALIDATION

    def test_error_string_representation(self):
        """Test error string representation."""
        error = CrawlerError(
            error_id="str-001",
            message="String test",
            category=ErrorCategory.AUTHENTICATION,
            severity=ErrorSeverity.CRITICAL
        )
        
        error_str = str(error)
        assert "str-001" in error_str
        assert "String test" in error_str
        assert "AUTHENTICATION" in error_str
        assert "CRITICAL" in error_str


class TestErrorClassifier:
    """Test suite for ErrorClassifier class."""
    def test_classifier_initialization(self):
        """
Test classifier setup."""
        classifier = ErrorClassifier()
        assert classifier.patterns is not None
        assert len(classifier.patterns) > 0
        assert classifier.ml_model is not None

    def test_classify_network_error(self):
        """
Test network error classification."""
        classifier = ErrorClassifier()
        
        # Connection timeout
        error = Exception("Connection timed out")
        category, severity = classifier.classify_error(error)
        assert category == ErrorCategory.NETWORK
        assert severity in [ErrorSeverity.HIGH, ErrorSeverity.MEDIUM]
        
        # DNS resolution failure
        error = Exception("Failed to resolve hostname")
        category, severity = classifier.classify_error(error)
        assert category == ErrorCategory.NETWORK

    def test_classify_authentication_error(self):
        """Test authentication error classification."""
        classifier = ErrorClassifier()
        
        # Invalid API key
        error = Exception("Invalid API key provided")
        category, severity = classifier.classify_error(error)
        assert category == ErrorCategory.AUTHENTICATION
        assert severity == ErrorSeverity.CRITICAL
        
        # Token expired
        error = Exception("Access token has expired")
        category, severity = classifier.classify_error(error)
        assert category == ErrorCategory.AUTHENTICATION

    def test_classify_rate_limit_error(self):
        """Test rate limit error classification."""
        classifier = ErrorClassifier()
        
        # Rate limit exceeded
        error = Exception("Rate limit exceeded. Try again later")
        category, severity = classifier.classify_error(error)
        assert category == ErrorCategory.RATE_LIMIT
        assert severity == ErrorSeverity.MEDIUM

    def test_classify_validation_error(self):
        """Test validation error classification."""
        classifier = ErrorClassifier()
        
        # Invalid data format
        error = Exception("Invalid JSON format in response")
        category, severity = classifier.classify_error(error)
        assert category == ErrorCategory.VALIDATION
        
        # Schema validation failure
        error = Exception("Required field 'id' is missing")
        category, severity = classifier.classify_error(error)
        assert category == ErrorCategory.VALIDATION

    def test_classify_parsing_error(self):
        """Test parsing error classification."""
        classifier = ErrorClassifier()
        
        # JSON parsing error
        error = Exception("Expecting ',' delimiter: line 1 column 15")
        category, severity = classifier.classify_error(error)
        assert category == ErrorCategory.PARSING

    def test_classify_unknown_error(self):
        """Test unknown error classification."""
        classifier = ErrorClassifier()
        
        # Unrecognized error
        error = Exception("This is a completely unknown error type")
        category, severity = classifier.classify_error(error)
        assert category == ErrorCategory.UNKNOWN
        assert severity == ErrorSeverity.MEDIUM

    @patch('backend.crawlers.handlers.error_handler.ErrorClassifier._predict_with_ml')
    def test_ml_classification(self, mock_ml_predict):
        """Test ML-based error classification."""
        mock_ml_predict.return_value = (ErrorCategory.NETWORK, ErrorSeverity.HIGH, 0.95)
        
        classifier = ErrorClassifier()
        error = Exception("Complex network error scenario")
        
        category, severity = classifier.classify_error(error)
        assert category == ErrorCategory.NETWORK
        assert severity == ErrorSeverity.HIGH

    def test_learn_from_feedback(self):
        """Test learning from classification feedback."""
        classifier = ErrorClassifier()
        
        error = CrawlerError(
            error_id="learn-001",
            message="Learning test error",
            category=ErrorCategory.NETWORK,
            severity=ErrorSeverity.HIGH
        )
        
        # Provide feedback
        classifier.learn_from_feedback(error, ErrorCategory.VALIDATION, ErrorSeverity.MEDIUM)
        
        # Verify learning was recorded
        assert len(classifier.feedback_data) > 0


class TestErrorRecoveryManager:
    """Test suite for ErrorRecoveryManager class."""
    def test_recovery_manager_initialization(self):
        """
Test recovery manager setup."""
        manager = ErrorRecoveryManager()
        assert manager.strategies is not None
        assert len(manager.strategies) > 0

    @pytest.mark.asyncio
    async def test_retry_strategy(self):
        """
Test retry recovery strategy."""
        manager = ErrorRecoveryManager()
        
        error = CrawlerError(
            error_id="retry-001",
            message="Temporary network error",
            category=ErrorCategory.NETWORK,
            severity=ErrorSeverity.MEDIUM
        )
        
        async def failing_operation():
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
        with patch.object(manager, '_execute_with_backoff') as mock_backoff:
            mock_backoff.return_value = "Success after retry"
            
            result = await manager.attempt_recovery(error, failing_operation)
            assert result.success
            assert result.result == "Success after retry"

    @pytest.mark.asyncio
    async def test_fallback_strategy(self):
        try:
            logger.info(f"Executing primary_operation")
            
            # Implementation for primary_operation
            # TODO: Add specific business logic here
        try:
            logger.info(f"Executing fallback_operation")
            
            # Implementation for fallback_operation
            # TODO: Add specific business logic here
            
            result = None  # Replace with actual implementation
            
            logger.info(f"fallback_operation completed successfully")
            return result
            
        except Exception as e:
            logger.error(f"fallback_operation failed: {e}")
            raise
            result = None  # Replace with actual implementation
            
            logger.info(f"primary_operation completed successfully")
            return result
            
        except Exception as e:
            logger.error(f"primary_operation failed: {e}")
            raise
        """Test fallback recovery strategy."""
        manager = ErrorRecoveryManager()
        
        error = CrawlerError(
            error_id="fallback-001",
            message="Primary source unavailable",
            category=ErrorCategory.NETWORK,
            severity=ErrorSeverity.HIGH
        )
        
        async def primary_operation():
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
        manager = ErrorRecoveryManager()
        
        error = CrawlerError(
            error_id="fallback-001",
            message="Primary source unavailable",
            category=ErrorCategory.NETWORK,
            severity=ErrorSeverity.HIGH
        )
        
        async def primary_operation():
        try:
            logger.info(f"Executing critical_operation")
            
            # Implementation for critical_operation
            # TODO: Add specific business logic here
            
            result = None  # Replace with actual implementation
            
            logger.info(f"critical_operation completed successfully")
            return result
            
        except Exception as e:
            logger.error(f"critical_operation failed: {e}")
            raise
        error = CrawlerError(
            error_id="fallback-001",
            message="Primary source unavailable",
            category=ErrorCategory.NETWORK,
            severity=ErrorSeverity.HIGH
        )
        
        async def primary_operation():
            raise Exception("Primary failed")
        
        async def fallback_operation():
            return "Fallback success"
        
        result = await manager.attempt_recovery(
            error, 
            primary_operation, 
            fallback_operation=fallback_operation
        )
        assert result.success
        assert result.result == "Fallback success"

    @pytest.mark.asyncio
    async def test_circuit_breaker_strategy(self):
        """Test circuit breaker recovery strategy."""
        manager = ErrorRecoveryManager()
        
        # Simulate repeated failures to trigger circuit breaker
        for i in range(5):
            error = CrawlerError(
                error_id=f"cb-{i}",
                message="Repeated failure",
                category=ErrorCategory.NETWORK,
                severity=ErrorSeverity.HIGH
            )
            
            async def failing_operation():
                raise Exception("Consistent failure")
            
            result = await manager.attempt_recovery(error, failing_operation)
            
            if i < 4:
                assert not result.success
            else:
                # Circuit breaker should be triggered
                assert result.strategy_used == RecoveryStrategy.CIRCUIT_BREAKER

    @pytest.mark.asyncio
    async def test_escalation_strategy(self):
        """Test escalation recovery strategy."""
        manager = ErrorRecoveryManager()
        
        error = CrawlerError(
            error_id="escalate-001",
            message="Critical system error",
            category=ErrorCategory.SYSTEM,
            severity=ErrorSeverity.CRITICAL
        )
        
        with patch.object(manager, '_escalate_to_admin') as mock_escalate:
            mock_escalate.return_value = True
            
            async def critical_operation():
                raise Exception("Critical failure")
            
            result = await manager.attempt_recovery(error, critical_operation)
            assert result.strategy_used == RecoveryStrategy.ESCALATION
            mock_escalate.assert_called_once()

    def test_should_retry_logic(self):
        """Test retry decision logic."""
        manager = ErrorRecoveryManager()
        
        # Retryable error
        retryable_error = CrawlerError(
            error_id="retry-test",
            message="Temporary network issue",
            category=ErrorCategory.NETWORK,
            severity=ErrorSeverity.MEDIUM
        )
        assert manager._should_retry(retryable_error, attempt=1)
        
        # Non-retryable error
        auth_error = CrawlerError(
            error_id="auth-test",
            message="Invalid credentials",
            category=ErrorCategory.AUTHENTICATION,
            severity=ErrorSeverity.CRITICAL
        )
        assert not manager._should_retry(auth_error, attempt=1)
        
        # Max attempts exceeded
        assert not manager._should_retry(retryable_error, attempt=5)

    def test_calculate_backoff_delay(self):
        """Test backoff delay calculation."""
        manager = ErrorRecoveryManager()
        
        # Exponential backoff
        delay1 = manager._calculate_backoff_delay(1, "exponential")
        delay2 = manager._calculate_backoff_delay(2, "exponential")
        delay3 = manager._calculate_backoff_delay(3, "exponential")
        
        assert delay2 > delay1
        assert delay3 > delay2
        
        # Linear backoff
        linear_delay1 = manager._calculate_backoff_delay(1, "linear")
        linear_delay2 = manager._calculate_backoff_delay(2, "linear")
        
        assert linear_delay2 == linear_delay1 * 2


class TestErrorAggregator:
    """Test suite for ErrorAggregator class."""
    def test_aggregator_initialization(self):
        """
Test aggregator setup."""
        aggregator = ErrorAggregator()
        assert aggregator.error_buffer == []
        assert aggregator.stats is not None

    def test_collect_error(self):
        """
Test error collection."""
        aggregator = ErrorAggregator()
        
        error = CrawlerError(
            error_id="collect-001",
            message="Collection test",
            category=ErrorCategory.NETWORK,
            severity=ErrorSeverity.MEDIUM
        )
        
        aggregator.collect_error(error)
        assert len(aggregator.error_buffer) == 1
        assert aggregator.error_buffer[0] == error

    def test_generate_stats(self):
        """Test error statistics generation."""
        aggregator = ErrorAggregator()
        
        # Add various errors
        errors = [
            CrawlerError("e1", "Error 1", ErrorCategory.NETWORK, ErrorSeverity.HIGH),
            CrawlerError("e2", "Error 2", ErrorCategory.NETWORK, ErrorSeverity.MEDIUM),
            CrawlerError("e3", "Error 3", ErrorCategory.VALIDATION, ErrorSeverity.LOW),
            CrawlerError("e4", "Error 4", ErrorCategory.AUTHENTICATION, ErrorSeverity.CRITICAL)
        ]
        
        for error in errors:
            aggregator.collect_error(error)
        
        stats = aggregator.generate_stats()
        
        assert stats.total_errors == 4
        assert stats.by_category[ErrorCategory.NETWORK] == 2
        assert stats.by_category[ErrorCategory.VALIDATION] == 1
        assert stats.by_severity[ErrorSeverity.CRITICAL] == 1
        assert stats.by_severity[ErrorSeverity.HIGH] == 1

    def test_detect_patterns(self):
        """Test error pattern detection."""
        aggregator = ErrorAggregator()
        
        # Create pattern of similar errors
        for i in range(10):
            error = CrawlerError(
                f"pattern-{i}",
                "Connection timeout",
                ErrorCategory.NETWORK,
                ErrorSeverity.MEDIUM
            )
            aggregator.collect_error(error)
        
        patterns = aggregator.detect_patterns()
        assert len(patterns) > 0
        
        # Should detect network timeout pattern
        network_pattern = next(
            (p for p in patterns if p['category'] == ErrorCategory.NETWORK), 
            None
        )
        assert network_pattern is not None
        assert network_pattern['count'] == 10

    def test_should_alert_logic(self):
        """Test alerting decision logic."""
        aggregator = ErrorAggregator()
        
        # High frequency of errors should trigger alert
        for i in range(20):
        try:
            logger.info(f"Executing failed_operation")
            
            # Implementation for failed_operation
            # TODO: Add specific business logic here
            
            result = None  # Replace with actual implementation
            
            logger.info(f"failed_operation completed successfully")
            return result
            
        except Exception as e:
            logger.error(f"failed_operation failed: {e}")
            raise
        for i in range(20):
            error = CrawlerError(
                f"alert-{i}",
                "Frequent error",
                ErrorCategory.NETWORK,
                ErrorSeverity.MEDIUM
            )
            aggregator.collect_error(error)
        
        should_alert, level = aggregator.should_alert()
        assert should_alert
        assert level in [AlertLevel.WARNING, AlertLevel.CRITICAL]

    @pytest.mark.asyncio
    async def test_send_alert(self):
        """Test alert sending."""
        aggregator = ErrorAggregator()
        
        with patch.object(aggregator, '_send_notification') as mock_send:
            mock_send.return_value = True
            
            await aggregator.send_alert(
                AlertLevel.WARNING,
                "Test alert message",
                {"test": "context"}
            )
            
            mock_send.assert_called_once()

    def test_cleanup_old_errors(self):
        """Test old error cleanup."""
        aggregator = ErrorAggregator()
        
        # Create old error
        old_error = CrawlerError(
            "old-001",
            "Old error",
            ErrorCategory.NETWORK,
            ErrorSeverity.LOW
        )
        old_error.timestamp = datetime.now() - timedelta(hours=25)  # Older than 24h
        
        # Create recent error
        recent_error = CrawlerError(
            "recent-001",
            "Recent error",
            ErrorCategory.VALIDATION,
            ErrorSeverity.MEDIUM
        )
        
        aggregator.error_buffer = [old_error, recent_error]
        aggregator.cleanup_old_errors()
        
        assert len(aggregator.error_buffer) == 1
        assert aggregator.error_buffer[0] == recent_error


class TestIntegration:
        try:
            logger.info(f"Executing network_operation")
            
            # Implementation for network_operation
            # TODO: Add specific business logic here
        try:
            logger.info(f"Executing auth_operation")
            
            # Implementation for auth_operation
            # TODO: Add specific business logic here
            
            result = None  # Replace with actual implementation
            
            logger.info(f"auth_operation completed successfully")
            return result
            
        except Exception as e:
            logger.error(f"auth_operation failed: {e}")
            raise
            result = None  # Replace with actual implementation
            
            logger.info(f"network_operation completed successfully")
            return result
            
        except Exception as e:
            logger.error(f"network_operation failed: {e}")
            raise
        recent_error = CrawlerError(
            "recent-001",
            "Recent error",
            ErrorCategory.VALIDATION,
            ErrorSeverity.MEDIUM
        )
        
        aggregator.error_buffer = [old_error, recent_error]
        aggregator.cleanup_old_errors()
        
        assert len(aggregator.error_buffer) == 1
        assert aggregator.error_buffer[0] == recent_error


class TestIntegration:
    """Integration tests for error handling system."""
    @pytest.mark.asyncio
    async def test_complete_error_handling_flow(self):
        """
Test complete error handling pipeline."""
        classifier = ErrorClassifier()
        recovery_manager = ErrorRecoveryManager()
        aggregator = ErrorAggregator()
        
        # Simulate a network error
        try:
            raise ConnectionError("Connection timed out after 30 seconds")
        except Exception as e:
            # Classify the error
            category, severity = classifier.classify_error(e)
            
            # Create error object
            error = CrawlerError.from_exception("flow-001", e, category)
            error.severity = severity
            
            # Collect for aggregation
            aggregator.collect_error(error)
            
            # Attempt recovery
            async def failed_operation():
                raise e
            
            recovery_result = await recovery_manager.attempt_recovery(
                error, 
                failed_operation
            )
            
            # Verify complete flow
            assert category == ErrorCategory.NETWORK
            assert severity in [ErrorSeverity.HIGH, ErrorSeverity.MEDIUM]
            assert len(aggregator.error_buffer) == 1
            assert not recovery_result.success  # Failed operation should fail

    @pytest.mark.asyncio
    async def test_error_pattern_detection_and_alerting(self):
        """Test error pattern detection and alerting system."""
        aggregator = ErrorAggregator()
        
        # Simulate burst of authentication errors
        for i in range(15):
            error = CrawlerError(
                f"auth-burst-{i}",
                "Authentication failed",
                ErrorCategory.AUTHENTICATION,
                ErrorSeverity.CRITICAL
            )
            aggregator.collect_error(error)
        
        # Detect patterns
        patterns = aggregator.detect_patterns()
        auth_pattern = next(
            (p for p in patterns if p['category'] == ErrorCategory.AUTHENTICATION),
            None
        )
        
        assert auth_pattern is not None
        assert auth_pattern['count'] == 15
        
        # Check if alert should be triggered
        should_alert, level = aggregator.should_alert()
        assert should_alert
        assert level == AlertLevel.CRITICAL  # Auth errors are critical

    @pytest.mark.asyncio
    async def test_recovery_strategy_selection(self):
        """Test recovery strategy selection based on error type."""
        recovery_manager = ErrorRecoveryManager()
        
        # Network error - should use retry strategy
        network_error = CrawlerError(
            "strategy-001",
            "Network timeout",
            ErrorCategory.NETWORK,
            ErrorSeverity.MEDIUM
        )
        
        async def network_operation():
            return "Network success"
        
        # Mock successful retry
        with patch.object(recovery_manager, '_execute_with_backoff') as mock_retry:
            mock_retry.return_value = "Retry success"
            
            result = await recovery_manager.attempt_recovery(
                network_error, 
                network_operation
            )
            
            assert result.strategy_used == RecoveryStrategy.RETRY
            
        # Authentication error - should escalate
        auth_error = CrawlerError(
            "strategy-002",
            "Invalid API key",
            ErrorCategory.AUTHENTICATION,
            ErrorSeverity.CRITICAL
        )
        
        async def auth_operation():
            raise Exception("Auth failed")
        
        with patch.object(recovery_manager, '_escalate_to_admin') as mock_escalate:
            mock_escalate.return_value = True
            
            result = await recovery_manager.attempt_recovery(
                auth_error, 
                auth_operation
            )
            
            assert result.strategy_used == RecoveryStrategy.ESCALATION

    def test_error_learning_and_improvement(self):
        """Test error classification learning and improvement."""
        classifier = ErrorClassifier()
        
        # Create an error that might be misclassified initially
        error_message = "Custom timeout error in new API endpoint"
        error = Exception(error_message)
        
        # Get initial classification
        initial_category, initial_severity = classifier.classify_error(error)
        
        # Provide feedback for correct classification
        crawler_error = CrawlerError.from_exception(
            "learn-001", 
            error, 
            initial_category
        )
        crawler_error.severity = initial_severity
        
        # Simulate feedback that it should be network/high severity
        classifier.learn_from_feedback(
            crawler_error, 
            ErrorCategory.NETWORK, 
            ErrorSeverity.HIGH
        )
        
        # Verify feedback was recorded
        assert len(classifier.feedback_data) > 0
        feedback = classifier.feedback_data[-1]
        assert feedback['correct_category'] == ErrorCategory.NETWORK
        assert feedback['correct_severity'] == ErrorSeverity.HIGH


if __name__ == '__main__':
    pytest.main([str(Path(__file__))])
