# -*- coding: utf-8 -*-
"""Test adapté automatiquement pour le projet Ainflue
================================================

Ce fichier a été importé et adapté depuis l'ancien projet IA-Influencer.
Certains imports et fonctionnalités peuvent nécessiter des ajustements manuels.
"""import sys
import os
from pathlib import Path

# Ajouter le répertoire racine au Python path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

"""Test Suite for Exception Handling Module

Comprehensive tests for enterprise-grade exception handling system.
Tests all custom exceptions, error tracking, and recovery mechanisms.

Created by: Fahed Mlaiel (mlaiel@live.de)
© 2025 Fahed Mlaiel. All rights reserved.

Business Logic: User Upload → AI Protection → SEO → Collaboration → Distribution
"""import pytest
import sys
import os
from pathlib import Path
import json
import sys
from datetime import datetime
from unittest.mock import Mock, patch
from pathlib import Path

# Import the exceptions module
try:
    from ai.core import exceptions
    from ai.core.exceptions import (
        BaseAIException,
        ContentGenerationError,
        ModelConnectionError,
        ContentValidationError,
        RateLimitError,
        ConfigurationError,
        QualityCheckError,
        DistributionError,
        OptimizationError,
        ProtectionError,
        CollaborationError,
        MonetizationError,
        AuthenticationError,
        AuthorizationError,
        ResourceNotFoundError,
        ErrorSeverity,
        ErrorCategory,
        EXCEPTION_REGISTRY,
        get_exception_by_code
    )
except ImportError as e:
    pytest.skip(f"Could not import exceptions module: {e}", allow_module_level=True)


class TestBaseAIException:
    """Test cases for BaseAIException class"""    
    def test_base_exception_creation(self):
        """Test basic exception creation with all parameters"""        context = {"user_id": "test_123", "operation": "content_upload"}
        
        error = BaseAIException(
            message="Test error message",
            error_code="TEST_001",
            context=context,
            severity=ErrorSeverity.HIGH,
            category=ErrorCategory.BUSINESS_LOGIC
        )
        
        assert str(error) == "[TEST_001] Test error message"
        assert error.error_code == "TEST_001"
        assert error.context == context
        assert error.severity == ErrorSeverity.HIGH
        assert error.category == ErrorCategory.BUSINESS_LOGIC
        assert isinstance(error.timestamp, datetime)
        assert error.correlation_id is None  # Par défaut à None si non spécifié
        
    def test_base_exception_minimal_creation(self):
        """Test exception creation with minimal parameters"""        error = BaseAIException("Simple error")
        
        assert str(error) == "Simple error"
        assert error.error_code == "AI_ERROR_000"  # Default code
        assert error.context == {}
        assert error.severity == ErrorSeverity.MEDIUM
        assert error.category == ErrorCategory.SYSTEM
        assert isinstance(error.timestamp, datetime)
        
    def test_exception_serialization(self):
        """Test exception serialization to dictionary"""        context = {"operation": "test", "data": {"key": "value"}}
        error = BaseAIException(
            "Test serialization",
            error_code="SERIALIZE_001",
            context=context
        )
        
        error_dict = error.to_dict()
        
        assert error_dict["message"] == "Test serialization"
        assert error_dict["error_code"] == "SERIALIZE_001"
        assert error_dict["context"] == context
        assert error_dict["severity"] == "medium"
        assert error_dict["category"] == "system"
        assert "timestamp" in error_dict
        assert "request_id" in error_dict
        
    def test_exception_json_serialization(self):
        """Test exception JSON serialization"""        error = BaseAIException("JSON test", error_code="JSON_001")
        json_str = error.to_json()
        
        # Should be valid JSON
        parsed = json.loads(json_str)
        assert parsed["message"] == "JSON test"
        assert parsed["error_code"] == "JSON_001"
        
    def test_exception_equality(self):
        """Test exception equality comparison"""        error1 = BaseAIException("Test", error_code="TEST_001")
        error2 = BaseAIException("Test", error_code="TEST_001")
        error3 = BaseAIException("Different", error_code="TEST_002")
        
        # Same error code should be equal
        assert error1 == error2
        # Different error code should not be equal
        assert error1 != error3
        
    def test_exception_hash(self):
        """Test exception hashing for use in sets/dicts"""        error1 = BaseAIException("Test", error_code="TEST_001")
        error2 = BaseAIException("Test", error_code="TEST_001")
        
        # Should be hashable and equal hashes for same error code
        error_set = {error1, error2}
        assert len(error_set) == 1  # Should deduplicate
        
    def test_exception_repr(self):
        """Test exception string representation"""        error = BaseAIException("Test repr", error_code="REPR_001")
        repr_str = repr(error)
        
        assert "BaseAIException" in repr_str
        assert "REPR_001" in repr_str
        assert "Test repr" in repr_str


class TestSpecificExceptions:
    """Test cases for specific exception types"""    
    def test_content_validation_error(self):
        """Test ContentValidationError specific functionality"""        validation_info = {
            "content_type": "audio",
            "file_size": 10485760,
            "validation_rules": ["format", "size", "quality"]
        }
        
        error = ContentValidationError(
            "Content validation failed",
            validation_type="format",
            content_info=validation_info
        )
        
        assert error.validation_type == "format"
        assert error.content_info == validation_info
        assert error.error_code.startswith("VALIDATION_")
        assert error.category == ErrorCategory.VALIDATION
        
    def test_ai_engine_error(self):
        """Test AIEngineError specific functionality"""        model_info = {
            "model_name": "test_classifier",
            "model_version": "1.0.0",
            "input_shape": [1, 224, 224, 3]
        }
        
        from ai.core.exceptions import AIEngineError
        error = AIEngineError(
            "Model inference failed",
            model_name="test_classifier",
            model_info=model_info
        )
        
        assert error.model_name == "test_classifier"
        assert error.model_info == model_info
        assert error.category == ErrorCategory.AI_ENGINE
        
    def test_performance_error(self):
        """Test PerformanceError specific functionality"""        performance_data = {
            "cpu_percent": 95.5,
            "memory_percent": 89.2,
            "response_time": 5.5
        }
        
        from ai.core.exceptions import PerformanceError
        error = PerformanceError(
            "Performance threshold exceeded",
            metric_type="response_time",
            current_value=5.5,
            threshold=2.0,
            performance_data=performance_data
        )
        
        assert error.metric_type == "response_time"
        assert error.current_value == 5.5
        assert error.threshold == 2.0
        assert error.performance_data == performance_data
        
    def test_business_logic_error(self):
        """Test BusinessLogicError for business workflow failures"""        workflow_data = {
            "stage": "ai_protection",
            "user_id": "musician_123",
            "content_id": "audio_456",
            "creator_type": "musician"
        }
        
        error = ProtectionError(
            "Content protection failed",
            protection_type="copyright",
            workflow_stage="ai_protection",
            business_data=workflow_data
        )
        
        assert error.protection_type == "copyright"
        assert error.workflow_stage == "ai_protection"
        assert error.business_data == workflow_data
        assert error.category == ErrorCategory.BUSINESS_LOGIC


class TestExceptionRegistry:
    """Test cases for exception registry system"""    
    def test_exception_registry_population(self):
        """Test that exception registry is properly populated"""        assert isinstance(EXCEPTION_REGISTRY, dict)
        assert len(EXCEPTION_REGISTRY) > 0
        
        # Check for key exception types
        expected_exceptions = [
            "BaseAIException",
            "ContentValidationError", 
            "AIEngineError",
            "PerformanceError",
            "BusinessLogicError"
        ]
        
        for exc_name in expected_exceptions:
            assert exc_name in EXCEPTION_REGISTRY
            
    def test_get_exception_by_code(self):
        """Test retrieving exception class by error code"""        # Test known error codes
        validation_exc = get_exception_by_code("VALIDATION_001")
        assert validation_exc == ContentValidationError
        
        ai_engine_exc = get_exception_by_code("AI_ENGINE_001")
        from ai.core.exceptions import AIEngineError
        assert ai_engine_exc == AIEngineError
        
        # Test unknown error code
        unknown_exc = get_exception_by_code("UNKNOWN_999")
        assert unknown_exc == BaseAIException
        
    def test_exception_code_uniqueness(self):
        """Test that error codes are unique across exception types"""        error_codes = set()
        
        # Create instances of different exceptions and check codes
        exceptions_to_test = [
            ContentValidationError("Test"),
            ModelConnectionError("Test"),
            RateLimitError("Test"),
            ConfigurationError("Test")
        ]
        
        for exc in exceptions_to_test:
            assert exc.error_code not in error_codes
            error_codes.add(exc.error_code)


class TestErrorSeverityAndCategory:
    """Test cases for error severity and category enums"""    
    def test_error_severity_enum(self):
        """Test ErrorSeverity enum values"""        assert ErrorSeverity.LOW.value == "low"
        assert ErrorSeverity.MEDIUM.value == "medium" 
        assert ErrorSeverity.HIGH.value == "high"
        assert ErrorSeverity.CRITICAL.value == "critical"
        
    def test_error_category_enum(self):
        """Test ErrorCategory enum values"""        expected_categories = [
            "system", "validation", "ai_engine", "performance",
            "business_logic", "security", "network", "database"
        ]
        
        for category in expected_categories:
            # Check that category exists in enum
            category_found = any(cat.value == category for cat in ErrorCategory)
            assert category_found, f"Category '{category}' not found in ErrorCategory enum"
            
    def test_severity_ordering(self):
        """Test that severity levels can be compared"""        assert ErrorSeverity.LOW < ErrorSeverity.MEDIUM
        assert ErrorSeverity.MEDIUM < ErrorSeverity.HIGH  
        assert ErrorSeverity.HIGH < ErrorSeverity.CRITICAL
        
        # Test reverse ordering
        assert ErrorSeverity.CRITICAL > ErrorSeverity.HIGH
        assert ErrorSeverity.HIGH > ErrorSeverity.MEDIUM
        assert ErrorSeverity.MEDIUM > ErrorSeverity.LOW


class TestExceptionHandling:
    """Test cases for exception handling scenarios"""    
    def test_exception_chaining(self):
        """Test exception chaining for debugging"""        try:
            # Simulate nested exception scenario
            try:
                raise ValueError("Original error")
            except ValueError as e:
                raise ContentValidationError(
                    "Validation failed due to format error",
                    validation_type="format"
                ) from e
        except ContentValidationError as ve:
            assert ve.__cause__ is not None
            assert isinstance(ve.__cause__, ValueError)
            assert str(ve.__cause__) == "Original error"
            
    def test_exception_context_preservation(self):
        """Test that exception context is preserved across raises"""        context = {
            "user_id": "test_user",
            "content_type": "audio",
            "file_path": "/test/audio.mp3"
        }
        
        try:
            raise ContentValidationError(
                "File not found",
                validation_type="existence",
                context=context
            )
        except ContentValidationError as e:
            assert e.context == context
            assert e.validation_type == "existence"
            
    def test_multiple_exception_handling(self):
        """Test handling multiple types of exceptions"""        exceptions_raised = []
        
        # Test different exception scenarios
        test_scenarios = [
            (ContentValidationError, "Invalid content"),
            (ModelConnectionError, "Model unavailable"),
            (RateLimitError, "Rate limit exceeded"),
            (ConfigurationError, "Invalid config")
        ]
        
        for exc_class, message in test_scenarios:
            try:
                raise exc_class(message)
            except BaseAIException as e:
                exceptions_raised.append(type(e))
                
        # All should be caught as BaseAIException
        assert len(exceptions_raised) == len(test_scenarios)
        for exc_type in exceptions_raised:
            assert issubclass(exc_type, BaseAIException)


class TestBusinessLogicExceptions:
    """Test cases for business logic specific exceptions"""    
    def test_monetization_error(self):
        """Test MonetizationError for revenue-related failures"""        monetization_data = {
            "creator_type": "musician",
            "content_type": "audio",
            "pricing_tier": "premium",
            "revenue_share": 0.7
        }
        
        error = MonetizationError(
            "Revenue calculation failed",
            monetization_type="revenue_share",
            creator_data=monetization_data
        )
        
        assert error.monetization_type == "revenue_share"
        assert error.creator_data == monetization_data
        assert error.category == ErrorCategory.BUSINESS_LOGIC
        
    def test_collaboration_error(self):
        """Test CollaborationError for collaboration workflow failures"""        collaboration_data = {
            "primary_creator": "musician_123",
            "collaborators": ["producer_456", "vocalist_789"],
            "collaboration_type": "music_production",
            "permissions": ["edit", "distribute"]
        }
        
        error = CollaborationError(
            "Collaboration permission denied",
            collaboration_type="music_production",
            permission_type="edit",
            collaboration_data=collaboration_data
        )
        
        assert error.collaboration_type == "music_production"
        assert error.permission_type == "edit"
        assert error.collaboration_data == collaboration_data
        
    def test_distribution_error(self):
        """Test DistributionError for content distribution failures"""        distribution_data = {
            "platforms": ["spotify", "youtube", "instagram"],
            "content_id": "audio_123",
            "distribution_rules": {"auto_publish": True, "schedule": "immediate"}
        }
        
        error = DistributionError(
            "Platform distribution failed",
            platform="spotify",
            distribution_type="auto_publish",
            distribution_data=distribution_data
        )
        
        assert error.platform == "spotify"
        assert error.distribution_type == "auto_publish"
        assert error.distribution_data == distribution_data


class TestExceptionLogging:
    """Test cases for exception logging and tracking"""    
    def test_exception_logging(self, capture_logs):
        """Test that exceptions are properly logged"""        error = ContentValidationError(
            "Test logging error",
            validation_type="format"
        )
        
        # Simulate logging the error
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Exception occurred: {error}", exc_info=True)
        
        log_output = capture_logs.getvalue()
        assert "Test logging error" in log_output
        assert "ContentValidationError" in log_output
        
    def test_exception_tracking(self):
        """Test exception tracking for monitoring"""        # Simulate tracking multiple exceptions
        tracked_exceptions = []
        
        exceptions_to_track = [
            ContentValidationError("Validation failed"),
            ModelConnectionError("Model connection lost"),
            RateLimitError("Rate limit exceeded")
        ]
        
        for exc in exceptions_to_track:
            tracked_exceptions.append({
                "type": type(exc).__name__,
                "code": exc.error_code,
                "severity": exc.severity.value,
                "timestamp": exc.timestamp.isoformat()
            })
            
        assert len(tracked_exceptions) == 3
        assert tracked_exceptions[0]["type"] == "ContentValidationError"
        assert tracked_exceptions[1]["type"] == "ModelConnectionError"
        assert tracked_exceptions[2]["type"] == "RateLimitError"


class TestCreatorSpecificExceptions:
    """Test cases for creator-specific exception scenarios"""    
    def test_musician_exceptions(self):
        """Test exceptions specific to musician workflows"""        # Audio content validation error
        audio_error = ContentValidationError(
            "Audio format not supported",
            validation_type="format",
            content_info={
                "creator_type": "musician",
                "content_type": "audio",
                "format": "wav",
                "sample_rate": 44100
            }
        )
        
        assert audio_error.content_info["creator_type"] == "musician"
        assert audio_error.content_info["content_type"] == "audio"
        
        # Copyright protection error
        protection_error = ProtectionError(
            "Copyright verification failed",
            protection_type="copyright",
            workflow_stage="ai_protection",
            business_data={
                "creator_type": "musician",
                "track_title": "Summer Vibes",
                "copyright_status": "pending"
            }
        )
        
        assert protection_error.protection_type == "copyright"
        assert protection_error.business_data["creator_type"] == "musician"
        
    def test_photographer_exceptions(self):
        """Test exceptions specific to photographer workflows"""        # Image validation error
        image_error = ContentValidationError(
            "Image resolution too low",
            validation_type="quality",
            content_info={
                "creator_type": "photographer",
                "content_type": "image",
                "resolution": "800x600",
                "min_resolution": "1920x1080"
            }
        )
        
        assert image_error.content_info["creator_type"] == "photographer"
        assert image_error.content_info["content_type"] == "image"
        
    def test_blogger_exceptions(self):
        """Test exceptions specific to blogger workflows"""        # SEO validation error
        seo_error = OptimizationError(
            "SEO optimization failed",
            optimization_type="seo",
            target_metric="readability_score",
            current_value=45.0,
            target_value=60.0,
            optimization_data={
                "creator_type": "blogger",
                "content_type": "text",
                "word_count": 500,
                "keywords": ["tech", "ai", "programming"]
            }
        )
        
        assert seo_error.optimization_type == "seo"
        assert seo_error.optimization_data["creator_type"] == "blogger"
        
    def test_influencer_exceptions(self):
        """Test exceptions specific to influencer workflows"""        # Multi-platform distribution error
        platform_error = DistributionError(
            "Multi-platform sync failed",
            platform="instagram",
            distribution_type="cross_platform",
            distribution_data={
                "creator_type": "influencer",
                "content_types": ["image", "video", "text"],
                "target_platforms": ["instagram", "tiktok", "youtube"],
                "sync_status": "failed"
            }
        )
        
        assert platform_error.platform == "instagram"
        assert platform_error.distribution_data["creator_type"] == "influencer"


class TestExceptionRecovery:
    """Test cases for exception recovery mechanisms"""    
    def test_graceful_degradation(self):
        """Test graceful degradation when non-critical errors occur"""        # Simulate a scenario where some operations fail but system continues
        operations_completed = []
        
        operations = [
            ("validation", False),  # This will fail
            ("ai_analysis", True),  # This will succeed
            ("protection", True),   # This will succeed
            ("seo", False),        # This will fail
            ("distribution", True)  # This will succeed
        ]
        
        for operation, should_succeed in operations:
            try:
                if not should_succeed:
                    if operation == "validation":
                        raise ContentValidationError(f"{operation} failed")
                    elif operation == "seo":
                        raise OptimizationError(f"{operation} failed")
                else:
                    operations_completed.append(operation)
            except BaseAIException as e:
                # Log error but continue with other operations
                print(f"Operation {operation} failed: {e}")
                continue
                
        # Should have completed 3 out of 5 operations
        assert len(operations_completed) == 3
        assert "ai_analysis" in operations_completed
        assert "protection" in operations_completed
        assert "distribution" in operations_completed
        
    def test_retry_mechanism(self):
        """Test retry mechanism for transient failures"""        attempt_count = 0
        max_retries = 3
        
        def operation_with_retries():
            nonlocal attempt_count
            attempt_count += 1
            
            if attempt_count < 3:
                raise ModelConnectionError("Temporary connection failure")
            return "Success"
            
        # Simulate retry logic
        for retry in range(max_retries):
            try:
                result = operation_with_retries()
                break
            except ModelConnectionError as e:
                if retry == max_retries - 1:
                    raise  # Re-raise on final attempt
                continue
                
        assert result == "Success"
        assert attempt_count == 3


# Performance and integration tests
class TestExceptionPerformance:
    """Test cases for exception performance"""    
    @pytest.mark.performance
    def test_exception_creation_performance(self, performance_tracker):
        """Test performance of exception creation"""        performance_tracker.start()
        
        # Create many exceptions to test performance
        exceptions = []
        for i in range(1000):
            exc = BaseAIException(
                f"Test exception {i}",
                error_code=f"TEST_{i:03d}",
                context={"iteration": i, "data": f"test_data_{i}"}
            )
            exceptions.append(exc)
            
        performance_tracker.stop()
        
        duration = performance_tracker.get_duration()
        assert duration < 1.0  # Should create 1000 exceptions in under 1 second
        assert len(exceptions) == 1000
        
    @pytest.mark.performance
    def test_exception_serialization_performance(self, performance_tracker):
        """Test performance of exception serialization"""        # Create a complex exception
        complex_context = {
            "user_data": {"id": "user_123", "type": "musician"},
            "content_data": {"type": "audio", "size": 10485760},
            "metadata": {"tags": ["music", "electronic"], "duration": 180}
        }
        
        error = ContentValidationError(
            "Complex validation error",
            validation_type="comprehensive",
            content_info=complex_context
        )
        
        performance_tracker.start()
        
        # Serialize many times
        for _ in range(100):
            json_data = error.to_json()
            dict_data = error.to_dict()
            
        performance_tracker.stop()
        
        duration = performance_tracker.get_duration()
        assert duration < 0.1  # Should serialize 100 times in under 100ms


if __name__ == "__main__":
    pytest.main([str(Path(__file__)), "-v"])
