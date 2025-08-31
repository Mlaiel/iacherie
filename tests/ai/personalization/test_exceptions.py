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

"""Exception Handling Tests

Comprehensive tests for custom exceptions, error handling, and recovery mechanisms.
Tests all exception scenarios and error recovery strategies.

Created by: Fahed Mlaiel (mlaiel@live.de)
© 2025 Fahed Mlaiel. All rights reserved.
"""
import pytest
import sys
import os
from pathlib import Path
import asyncio
from unittest import IsolatedAsyncioTestCase
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple, Union
import time
import os
import sys
from unittest.mock import Mock, patch, AsyncMock

# Import the exception modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', 'backend'))

from ai.personalization.exceptions import (
    PersonalizationError,
    PersonalizationConfigError,
    ProfileNotFoundError,
    RecommendationError,
    ModelTrainingError,
    InsufficientDataError,
    CacheConnectionError,
    ValidationError,
    ModelNotLoadedError,
    EmbeddingGenerationError,
    CollaborationMatchingError,
    PersonalizationTimeoutError,
    ContentFilteringError,
    AnalyticsError,
    PersonalizationErrorType
)


class TestPersonalizationError(IsolatedAsyncioTestCase):
    """Test base personalization exception classes"""

class TestPersonalizationBaseExceptions(IsolatedAsyncioTestCase):
    """Test base personalization exception classes"""
    async def test_personalization_error_base(self):
        """Test base PersonalizationError exception"""        error_message = "Base personalization error"
        error_code = "PERS_001"
        
        exception = PersonalizationError(
            message=error_message,
            error_code=error_code,
            details={'component': 'test'}
        )
        
        self.assertEqual(str(exception), error_message)
        self.assertEqual(exception.error_code, error_code)
        self.assertEqual(exception.details['component'], 'test')
        self.assertIsInstance(exception.timestamp, datetime)

    async def test_exception_inheritance(self):
        """Test exception inheritance hierarchy"""        config_error = PersonalizationConfigError("Config error")
        data_error = PersonalizationDataError("Data error")
        model_error = PersonalizationModelError("Model error")
        
        # All should inherit from PersonalizationError
        self.assertIsInstance(config_error, PersonalizationError)
        self.assertIsInstance(data_error, PersonalizationError)
        self.assertIsInstance(model_error, PersonalizationError)

    async def test_exception_serialization(self):
        """Test exception serialization for logging"""        exception = PersonalizationError(
            message="Test error",
            error_code="TEST_001",
            details={'user_id': 'user_123', 'operation': 'recommendation'}
        )
        
        serialized = exception.to_dict()
        
        self.assertIsInstance(serialized, dict)
        self.assertEqual(serialized['message'], "Test error")
        self.assertEqual(serialized['error_code'], "TEST_001")
        self.assertIn('user_id', serialized['details'])
        self.assertIn('timestamp', serialized)

    async def test_exception_chaining(self):
        """Test exception chaining and cause tracking"""        original_error = ValueError("Original error")
        
        personalization_error = PersonalizationError(
            message="Wrapper error",
            error_code="WRAP_001",
            cause=original_error
        )
        
        self.assertEqual(personalization_error.cause, original_error)
        self.assertIn("Original error", str(personalization_error.cause))


class TestConfigurationExceptions(IsolatedAsyncioTestCase):
    """Test configuration-related exceptions"""
    async def test_config_error_scenarios(self):
        """Test various configuration error scenarios"""        # Missing required configuration
        with self.assertRaises(PersonalizationConfigError) as context:
            raise PersonalizationConfigError(
                "Missing required configuration: model.learning_rate",
                error_code="CONFIG_MISSING"
            )
        
        self.assertIn("Missing required configuration", str(context.exception))
        self.assertEqual(context.exception.error_code, "CONFIG_MISSING")

    async def test_invalid_config_values(self):
        """Test invalid configuration value errors"""        invalid_configs = [
            {"learning_rate": -1.0, "error": "Learning rate must be positive"},
            {"batch_size": 0, "error": "Batch size must be greater than 0"},
            {"model_type": "invalid", "error": "Unknown model type"}
        ]
        
        for config in invalid_configs:
            with self.assertRaises(PersonalizationConfigError):
                raise PersonalizationConfigError(
                    config["error"],
                    error_code="CONFIG_INVALID",
                    details=config
                )

    async def test_config_validation_errors(self):
        """Test configuration validation errors"""        # Test schema validation error
        with self.assertRaises(PersonalizationValidationError) as context:
            raise PersonalizationValidationError(
                "Configuration schema validation failed",
                error_code="CONFIG_SCHEMA",
                details={
                    'field': 'n_factors',
                    'expected_type': 'int',
                    'actual_type': 'str',
                    'value': 'fifty'
                }
            )
        
        exception = context.exception
        self.assertEqual(exception.details['field'], 'n_factors')
        self.assertEqual(exception.details['expected_type'], 'int')


class TestDataExceptions(IsolatedAsyncioTestCase):
    """Test data-related exceptions"""
    async def test_data_error_types(self):
        """Test various data error types"""        # Missing data
        with self.assertRaises(PersonalizationDataError):
            raise PersonalizationDataError(
                "Required dataset not found",
                error_code="DATA_MISSING"
            )
        
        # Corrupted data
        with self.assertRaises(PersonalizationDataError):
            raise PersonalizationDataError(
                "Data corruption detected",
                error_code="DATA_CORRUPTED",
                details={'corrupted_rows': 150, 'total_rows': 1000}
            )

    async def test_insufficient_data_error(self):
        """Test insufficient data scenarios"""        with self.assertRaises(InsufficientDataError) as context:
            raise InsufficientDataError(
                "Insufficient training data for user modeling",
                minimum_required=100,
                actual_count=25,
                user_id="user_123"
            )
        
        exception = context.exception
        self.assertEqual(exception.minimum_required, 100)
        self.assertEqual(exception.actual_count, 25)
        self.assertEqual(exception.user_id, "user_123")

    async def test_data_validation_errors(self):
        """Test data validation errors"""        validation_errors = [
            {
                'field': 'rating',
                'value': 10.0,
                'error': 'Rating must be between 0 and 5'
            },
            {
                'field': 'user_id',
                'value': '',
                'error': 'User ID cannot be empty'
            },
            {
                'field': 'timestamp',
                'value': 'invalid_date',
                'error': 'Invalid timestamp format'
            }
        ]
        
        for error_info in validation_errors:
            with self.assertRaises(PersonalizationValidationError):
                raise PersonalizationValidationError(
                    error_info['error'],
                    error_code="DATA_VALIDATION",
                    details=error_info
                )

    async def test_data_format_errors(self):
        """Test data format errors"""        with self.assertRaises(PersonalizationDataError) as context:
            raise PersonalizationDataError(
                "Unsupported data format",
                error_code="DATA_FORMAT",
                details={
                    'expected_format': 'JSON',
                    'actual_format': 'XML',
                    'file_path': '/data/interactions.xml'
                }
            )
        
        exception = context.exception
        self.assertEqual(exception.details['expected_format'], 'JSON')


class TestModelExceptions(IsolatedAsyncioTestCase):
    """Test model-related exceptions"""
    async def test_model_not_trained_error(self):
        """Test model not trained scenarios"""        with self.assertRaises(ModelNotTrainedError) as context:
            raise ModelNotTrainedError(
                "Model must be trained before making predictions",
                model_id="collaborative_filter_v1",
                required_training_samples=1000
            )
        
        exception = context.exception
        self.assertEqual(exception.model_id, "collaborative_filter_v1")
        self.assertEqual(exception.required_training_samples, 1000)

    async def test_model_loading_errors(self):
        """Test model loading error scenarios"""        loading_errors = [
            {
                'error': 'Model file not found',
                'code': 'MODEL_NOT_FOUND',
                'path': '/models/collaborative_filter.pkl'
            },
            {
                'error': 'Model version incompatible',
                'code': 'MODEL_VERSION',
                'expected': '2.1.0',
                'actual': '1.9.0'
            },
            {
                'error': 'Model corruption detected',
                'code': 'MODEL_CORRUPTED',
                'checksum_expected': 'abc123',
                'checksum_actual': 'def456'
            }
        ]
        
        for error_info in loading_errors:
            with self.assertRaises(PersonalizationModelError):
                raise PersonalizationModelError(
                    error_info['error'],
                    error_code=error_info['code'],
                    details=error_info
                )

    async def test_model_training_errors(self):
        """Test model training error scenarios"""        # Convergence failure
        with self.assertRaises(PersonalizationModelError) as context:
            raise PersonalizationModelError(
                "Model failed to converge after maximum iterations",
                error_code="TRAINING_CONVERGENCE",
                details={
                    'max_iterations': 1000,
                    'final_loss': 0.85,
                    'target_loss': 0.01,
                    'learning_rate': 0.001
                }
            )
        
        exception = context.exception
        self.assertEqual(exception.details['max_iterations'], 1000)
        self.assertEqual(exception.details['final_loss'], 0.85)

    async def test_model_prediction_errors(self):
        """Test model prediction error scenarios"""        with self.assertRaises(PersonalizationModelError):
            raise PersonalizationModelError(
                "Prediction failed: invalid input dimensions",
                error_code="PREDICTION_ERROR",
                details={
                    'expected_dimensions': (1, 50),
                    'actual_dimensions': (1, 30),
                    'user_id': 'user_456'
                }
            )


class TestServiceExceptions(IsolatedAsyncioTestCase):
    """Test service-related exceptions"""
    async def test_service_unavailable_error(self):
        """Test service unavailable scenarios"""        with self.assertRaises(ServiceUnavailableError) as context:
            raise ServiceUnavailableError(
                "Personalization service temporarily unavailable",
                service_name="recommendation_engine",
                retry_after=300,
                reason="maintenance"
            )
        
        exception = context.exception
        self.assertEqual(exception.service_name, "recommendation_engine")
        self.assertEqual(exception.retry_after, 300)
        self.assertEqual(exception.reason, "maintenance")

    async def test_external_service_errors(self):
        """Test external service error scenarios"""        external_errors = [
            {
                'service': 'spotify_api',
                'error': 'API rate limit exceeded',
                'status_code': 429,
                'retry_after': 3600
            },
            {
                'service': 'ml_model_api',
                'error': 'Service timeout',
                'status_code': 504,
                'timeout': 30
            },
            {
                'service': 'user_profile_api',
                'error': 'Authentication failed',
                'status_code': 401,
                'details': 'Invalid API key'
            }
        ]
        
        for error_info in external_errors:
            with self.assertRaises(ExternalServiceError):
                raise ExternalServiceError(
                    error_info['error'],
                    service_name=error_info['service'],
                    status_code=error_info['status_code'],
                    details=error_info
                )

    async def test_timeout_errors(self):
        """Test timeout error scenarios"""        with self.assertRaises(PersonalizationTimeoutError) as context:
            raise PersonalizationTimeoutError(
                "Operation timed out",
                operation="model_training",
                timeout_duration=1800,
                elapsed_time=2100
            )
        
        exception = context.exception
        self.assertEqual(exception.operation, "model_training")
        self.assertEqual(exception.timeout_duration, 1800)
        self.assertEqual(exception.elapsed_time, 2100)


class TestSecurityExceptions(IsolatedAsyncioTestCase):
    """Test security-related exceptions"""
    async def test_authentication_errors(self):
        """Test authentication error scenarios"""        auth_errors = [
            {
                'error': 'Invalid credentials',
                'user_id': 'user_789',
                'attempt_count': 3
            },
            {
                'error': 'Token expired',
                'token_type': 'access_token',
                'expired_at': datetime.utcnow()
            },
            {
                'error': 'Account locked',
                'user_id': 'user_456',
                'locked_until': datetime.utcnow() + timedelta(hours=1)
            }
        ]
        
        for error_info in auth_errors:
            with self.assertRaises(AuthenticationError):
                raise AuthenticationError(
                    error_info['error'],
                    error_code="AUTH_FAILED",
                    details=error_info
                )

    async def test_authorization_errors(self):
        """Test authorization error scenarios"""        with self.assertRaises(AuthorizationError) as context:
            raise AuthorizationError(
                "Insufficient permissions for operation",
                user_id="user_123",
                required_permission="model.train",
                user_permissions=["model.read", "model.predict"]
            )
        
        exception = context.exception
        self.assertEqual(exception.user_id, "user_123")
        self.assertEqual(exception.required_permission, "model.train")

    async def test_rate_limit_exceeded(self):
        """Test rate limiting errors"""        with self.assertRaises(RateLimitExceededError) as context:
            raise RateLimitExceededError(
                "API rate limit exceeded",
                user_id="user_123",
                limit=1000,
                window="1h",
                current_count=1050,
                reset_time=datetime.utcnow() + timedelta(minutes=45)
            )
        
        exception = context.exception
        self.assertEqual(exception.limit, 1000)
        self.assertEqual(exception.current_count, 1050)

    async def test_security_violations(self):
        """Test security violation scenarios"""        with self.assertRaises(PersonalizationSecurityError):
            raise PersonalizationSecurityError(
                "Suspicious activity detected",
                error_code="SECURITY_VIOLATION",
                details={
                    'violation_type': 'unusual_access_pattern',
                    'user_id': 'user_suspicious',
                    'ip_address': '192.168.1.100',
                    'risk_score': 0.85
                }
            )


class TestErrorHandler(IsolatedAsyncioTestCase):
    """Test ErrorHandler utility class"""
    async def asyncSetUp(self):
        """Set up test environment"""        self.error_handler = ErrorHandler()

    async def test_exception_handling_decorator(self):
        """Test exception handling decorator"""        @self.error_handler.handle_exceptions
        async def function_that_raises():
            raise PersonalizationDataError("Test data error")
        
        # Should catch and wrap the exception
        with self.assertRaises(PersonalizationError):
            await function_that_raises()

    async def test_retry_mechanism(self):
        """Test retry mechanism for transient errors"""        call_count = 0
        
        @self.error_handler.retry_on_failure(max_retries=3, delay=0.1)
        async def flaky_function():
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise ServiceUnavailableError("Temporary failure")
            return "success"
        
        # Should succeed after 3 attempts
        result = await flaky_function()
        self.assertEqual(result, "success")
        self.assertEqual(call_count, 3)

    async def test_circuit_breaker_pattern(self):
        """Test circuit breaker pattern"""        circuit_breaker = self.error_handler.create_circuit_breaker(
            failure_threshold=3,
            timeout=1.0
        )
        
        # Simulate failures to trip circuit breaker
        for i in range(3):
            with self.assertRaises(ExternalServiceError):
                await circuit_breaker.call(self._failing_service)
        
        # Circuit should be open now
        self.assertTrue(circuit_breaker.is_open)
        
        # Should fail fast
        with self.assertRaises(ServiceUnavailableError):
            await circuit_breaker.call(self._working_service)

    async def _failing_service(self):
        """Mock failing service"""        raise ExternalServiceError("Service failed")

    async def _working_service(self):
        """Mock working service"""        return "success"

    async def test_error_categorization(self):
        """Test error categorization by type and severity"""        errors = [
            PersonalizationConfigError("Config error"),
            InsufficientDataError("Not enough data"),
            ServiceUnavailableError("Service down"),
            AuthenticationError("Auth failed")
        ]
        
        for error in errors:
            category = self.error_handler.categorize_error(error)
            severity = self.error_handler.get_error_severity(error)
            
            self.assertIsInstance(category, str)
            self.assertIn(severity, ['low', 'medium', 'high', 'critical'])

    async def test_error_recovery_strategies(self):
        """Test error recovery strategies"""        # Test fallback strategy
        async def primary_function():
            raise PersonalizationModelError("Model unavailable")
        
        async def fallback_function():
            return "fallback_result"
        
        result = await self.error_handler.with_fallback(
            primary_function,
            fallback_function
        )
        
        self.assertEqual(result, "fallback_result")

    async def test_bulk_error_handling(self):
        """Test handling multiple errors in batch operations"""        async def process_item(item):
            if item == 'error_item':
                raise PersonalizationDataError(f"Error processing {item}")
            return f"processed_{item}"
        
        items = ['item1', 'error_item', 'item3', 'item4']
        
        results, errors = await self.error_handler.process_with_error_collection(
            process_item,
            items
        )
        
        self.assertEqual(len(results), 3)  # 3 successful items
        self.assertEqual(len(errors), 1)   # 1 error item
        self.assertIn('processed_item1', results)


class TestErrorRecovery(IsolatedAsyncioTestCase):
    """Test ErrorRecovery mechanisms"""
    async def asyncSetUp(self):
        """Set up test environment"""        self.error_recovery = ErrorRecovery()

    async def test_data_recovery_strategies(self):
        """Test data recovery strategies"""        # Simulate corrupted data scenario
        corrupted_data = [
            {'user_id': 'user_1', 'rating': 4.5},
            {'user_id': '', 'rating': None},  # Corrupted entry
            {'user_id': 'user_3', 'rating': 3.0}
        ]
        
        # Apply data recovery
        recovered_data = await self.error_recovery.recover_corrupted_data(
            corrupted_data,
            strategies=['remove_invalid', 'impute_missing']
        )
        
        # Should have clean data
        self.assertGreater(len(recovered_data), 0)
        for entry in recovered_data:
            self.assertIsNotNone(entry.get('user_id'))
            self.assertNotEqual(entry.get('user_id'), '')

    async def test_model_recovery_strategies(self):
        """Test model recovery strategies"""        # Simulate model failure scenario
        async def failing_model_predict(user_id):
            raise ModelNotTrainedError("Model not available")
        
        # Use fallback model
        async def fallback_model_predict(user_id):
            return f"fallback_prediction_for_{user_id}"
        
        prediction = await self.error_recovery.recover_model_failure(
            failing_model_predict,
            fallback_model_predict,
            user_id="user_123"
        )
        
        self.assertEqual(prediction, "fallback_prediction_for_user_123")

    async def test_service_recovery_strategies(self):
        """Test service recovery strategies"""        # Simulate service failure with retry
        attempt_count = 0
        
        async def unreliable_service():
            nonlocal attempt_count
            attempt_count += 1
            if attempt_count < 3:
                raise ServiceUnavailableError("Service temporarily down")
            return "service_result"
        
        result = await self.error_recovery.recover_service_failure(
            unreliable_service,
            max_retries=3,
            backoff_strategy='exponential'
        )
        
        self.assertEqual(result, "service_result")
        self.assertEqual(attempt_count, 3)

    async def test_cache_recovery_strategies(self):
        """Test cache recovery strategies"""        # Simulate cache miss/failure
        async def cache_miss_handler(key):
            # Simulate expensive computation
            await asyncio.sleep(0.1)
            return f"computed_value_for_{key}"
        
        result = await self.error_recovery.recover_cache_failure(
            cache_key="user_profile_123",
            fallback_function=cache_miss_handler
        )
        
        self.assertEqual(result, "computed_value_for_user_profile_123")

    async def test_graceful_degradation(self):
        """Test graceful degradation strategies"""        # Simulate system under stress
        system_load = 0.95  # High load
        
        degraded_config = await self.error_recovery.apply_graceful_degradation(
            current_load=system_load,
            degradation_strategies=[
                'reduce_model_complexity',
                'disable_real_time_features',
                'use_cached_results'
            ]
        )
        
        self.assertIsInstance(degraded_config, dict)
        self.assertIn('model_complexity', degraded_config)


class TestErrorLogger(IsolatedAsyncioTestCase):
    """Test ErrorLogger functionality"""
    async def asyncSetUp(self):
        """Set up test environment"""        self.error_logger = ErrorLogger()

    async def test_error_logging_formats(self):
        """Test different error logging formats"""        exception = PersonalizationError(
            "Test error for logging",
            error_code="TEST_001",
            details={'user_id': 'user_test', 'operation': 'test'}
        )
        
        # Test JSON format
        json_log = await self.error_logger.format_error(exception, format='json')
        self.assertIsInstance(json_log, str)
        self.assertIn('TEST_001', json_log)
        
        # Test structured format
        structured_log = await self.error_logger.format_error(exception, format='structured')
        self.assertIsInstance(structured_log, dict)
        self.assertEqual(structured_log['error_code'], 'TEST_001')

    async def test_error_aggregation(self):
        """Test error aggregation and reporting"""        # Simulate multiple errors
        errors = [
            PersonalizationDataError("Data error 1"),
            PersonalizationDataError("Data error 2"),
            PersonalizationModelError("Model error 1"),
            AuthenticationError("Auth error 1")
        ]
        
        for error in errors:
            await self.error_logger.log_error(error)
        
        # Get error summary
        summary = await self.error_logger.get_error_summary(
            time_window=timedelta(hours=1)
        )
        
        self.assertIn('PersonalizationDataError', summary)
        self.assertIn('PersonalizationModelError', summary)
        self.assertEqual(summary['PersonalizationDataError']['count'], 2)

    async def test_error_alerting(self):
        """Test error alerting mechanisms"""        # Configure alert thresholds
        await self.error_logger.configure_alerts({
            'PersonalizationModelError': {'threshold': 5, 'window': '1h'},
            'ServiceUnavailableError': {'threshold': 3, 'window': '5m'}
        })
        
        # Simulate error burst that should trigger alert
        for i in range(6):
            await self.error_logger.log_error(
                PersonalizationModelError(f"Model error {i}")
            )
        
        # Check if alert was triggered
        alerts = await self.error_logger.get_active_alerts()
        self.assertGreater(len(alerts), 0)

    async def test_error_metrics_collection(self):
        """Test error metrics collection"""        # Log various errors with different patterns
        error_patterns = [
            ('user_1', PersonalizationDataError("Data error")),
            ('user_1', PersonalizationModelError("Model error")),
            ('user_2', AuthenticationError("Auth error")),
            ('user_3', PersonalizationDataError("Data error"))
        ]
        
        for user_id, error in error_patterns:
            await self.error_logger.log_error(error, context={'user_id': user_id})
        
        # Collect metrics
        metrics = await self.error_logger.collect_error_metrics()
        
        self.assertIn('total_errors', metrics)
        self.assertIn('error_rate', metrics)
        self.assertIn('error_distribution', metrics)
        self.assertEqual(metrics['total_errors'], 4)


class TestExceptionPerformanceAndIntegration(IsolatedAsyncioTestCase):
    """Performance and integration tests for exception handling"""
    async def test_exception_handling_performance(self):
        """Test exception handling performance under load"""        error_handler = ErrorHandler()
        
        # Measure exception handling overhead
        start_time = time.time()
        
        for i in range(1000):
            try:
                raise PersonalizationError(f"Test error {i}")
            except PersonalizationError as e:
                # Simulate error processing
                _ = e.to_dict()
        
        handling_time = time.time() - start_time
        
        # Should handle exceptions efficiently
        self.assertLess(handling_time, 1.0)  # Less than 1 second for 1000 exceptions

    async def test_concurrent_error_handling(self):
        """Test concurrent error handling"""        error_handler = ErrorHandler()
        
        async def error_producing_task(task_id):
            if task_id % 3 == 0:
                raise PersonalizationDataError(f"Data error {task_id}")
            elif task_id % 5 == 0:
                raise PersonalizationModelError(f"Model error {task_id}")
            return f"success_{task_id}"
        
        # Run concurrent tasks with errors
        tasks = [error_producing_task(i) for i in range(100)]
        
        results = []
        errors = []
        
        for task in tasks:
            try:
                result = await task
                results.append(result)
            except PersonalizationError as e:
                errors.append(e)
        
        # Should handle concurrent errors properly
        self.assertGreater(len(results), 0)
        self.assertGreater(len(errors), 0)
        self.assertEqual(len(results) + len(errors), 100)

    async def test_error_recovery_integration(self):
        """Test integration between error handling and recovery"""        error_handler = ErrorHandler()
        error_recovery = ErrorRecovery()
        
        # Simulate complex failure scenario
        async def complex_operation():
            # First failure: data corruption
            raise PersonalizationDataError("Data corrupted")
        
        async def recovery_operation():
            # Recovery: use cached data
            return "recovered_data"
        
        # Apply integrated error handling and recovery
        result = await error_handler.with_recovery(
            complex_operation,
            error_recovery.get_recovery_strategy('data_corruption'),
            fallback=recovery_operation
        )
        
        self.assertEqual(result, "recovered_data")

    async def test_error_monitoring_integration(self):
        """Test integration with monitoring systems"""        error_logger = ErrorLogger()
        
        # Configure monitoring integration
        await error_logger.configure_monitoring({
            'metrics_backend': 'prometheus',
            'logging_backend': 'elasticsearch',
            'alerting_backend': 'pagerduty'
        })
        
        # Simulate error that should be monitored
        critical_error = PersonalizationSecurityError(
            "Security breach detected",
            error_code="SECURITY_CRITICAL",
            details={'severity': 'critical', 'user_id': 'admin_user'}
        )
        
        # Log error and verify monitoring integration
        await error_logger.log_error(critical_error)
        
        # Check if monitoring systems were notified
        monitoring_events = await error_logger.get_monitoring_events()
        self.assertGreater(len(monitoring_events), 0)


# Test runner configuration
if __name__ == '__main__':
    pytest.main([
        __file__,
        '-v',
        '--tb=short',
        '--asyncio-mode=auto',
        '--maxfail=10'
    ])
