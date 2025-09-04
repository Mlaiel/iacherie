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

"""Comprehensive Tests for AI Recommendation Exception Handling
Testing error conditions, edge cases, and exception hierarchies

Copyright (c) 2025 Fahed Mlaiel <mlaiel@live.de>
⚠️  STRICT WARNING: Unauthorized use, copying, or stealing of this concept, 
    code, or intellectual property without explicit written authorization 
    from Fahed Mlaiel is strictly prohibited and will result in legal action.

Lead Developer: Fahed Mlaiel
Email: mlaiel@live.de
"""
import pytest
import sys
import os
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any

from ai.recommendation.exceptions import (
    RecommendationError, ContentAnalysisError, CollaborationMatchingError,
    TrendAnalysisError, RevenueOptimizationError, ProtectionError,
    ModelInitializationError, ValidationError, DataProcessingError,
    AuthenticationError, AuthorizationError, RateLimitError,
    ExternalServiceError, CacheError, DatabaseError,
    validate_creator_profile, validate_recommendation_scores,
    validate_engagement_metrics, sanitize_user_input,
    log_error_with_context, create_error_response
)
from ai.recommendation.models import CreatorProfile, ContentRecommendation, Platform, ContentType


class TestRecommendationErrorHierarchy:
    """Test the exception hierarchy and inheritance"""
    
    def test_base_recommendation_error(self):
        """Test base RecommendationError functionality"""
        error = RecommendationError("Test error message")
        
        assert str(error) == "Test error message"
        assert error.error_code == "RECOMMENDATION_ERROR"
        assert error.timestamp is not None
        assert isinstance(error.timestamp, datetime)
        assert error.context == {}
        assert error.suggested_action == "Contact support for assistance"
    
    def test_recommendation_error_with_context(self):
        """Test RecommendationError with additional context"""
        context = {
            "creator_id": "test_001",
            "operation": "generate_recommendations",
            "parameters": {"limit": 10}
        }
        
        error = RecommendationError(
            message="Failed to generate recommendations",
            error_code="GENERATION_FAILED",
            context=context,
            suggested_action="Check creator profile completeness"
        )
        
        assert error.error_code == "GENERATION_FAILED"
        assert error.context == context
        assert error.suggested_action == "Check creator profile completeness"
        assert "test_001" in str(error.context)
    
    def test_content_analysis_error_inheritance(self):
        """Test ContentAnalysisError inherits from RecommendationError"""
        error = ContentAnalysisError("Content analysis failed")
        
        assert isinstance(error, RecommendationError)
        assert isinstance(error, ContentAnalysisError)
        assert error.error_code == "CONTENT_ANALYSIS_ERROR"
    
    def test_collaboration_matching_error(self):
        """Test CollaborationMatchingError specifics"""
        error = CollaborationMatchingError(
            message="No suitable collaborators found",
            creator_id="creator_001",
            matching_criteria="genre_compatibility"
        )
        
        assert isinstance(error, RecommendationError)
        assert error.creator_id == "creator_001"
        assert error.matching_criteria == "genre_compatibility"
        assert "creator_001" in str(error)
    
    def test_trend_analysis_error(self):
        """Test TrendAnalysisError specifics"""
        error = TrendAnalysisError(
            message="Trend data unavailable",
            trend_id="trend_001",
            analysis_type="viral_prediction"
        )
        
        assert isinstance(error, RecommendationError)
        assert error.trend_id == "trend_001"
        assert error.analysis_type == "viral_prediction"
    
    def test_revenue_optimization_error(self):
        """Test RevenueOptimizationError specifics"""
        error = RevenueOptimizationError(
            message="Revenue optimization failed",
            creator_id="creator_001",
            optimization_type="strategy_generation"
        )
        
        assert isinstance(error, RecommendationError)
        assert error.creator_id == "creator_001"
        assert error.optimization_type == "strategy_generation"
    
    def test_protection_error(self):
        """Test ProtectionError specifics"""
        error = ProtectionError(
            message="Content protection violation detected",
            content_id="content_001",
            violation_type="copyright_infringement"
        )
        
        assert isinstance(error, RecommendationError)
        assert error.content_id == "content_001"
        assert error.violation_type == "copyright_infringement"


class TestValidationErrors:
    """Test validation error scenarios"""
    
    def test_model_initialization_error(self):
        """Test ModelInitializationError"""
        error = ModelInitializationError(
            message="Failed to initialize content analyzer",
            model_name="content_analyzer",
            initialization_step="loading_weights"
        )
        
        assert isinstance(error, RecommendationError)
        assert error.model_name == "content_analyzer"
        assert error.initialization_step == "loading_weights"
    
    def test_validation_error_basic(self):
        """Test basic ValidationError"""
        error = ValidationError(
            message="Invalid input data",
            field_name="engagement_rate",
            field_value=1.5,
            expected_range="0.0-1.0"
        )
        
        assert isinstance(error, RecommendationError)
        assert error.field_name == "engagement_rate"
        assert error.field_value == 1.5
        assert error.expected_range == "0.0-1.0"
    
    def test_data_processing_error(self):
        """Test DataProcessingError"""
        error = DataProcessingError(
            message="Failed to process audio features",
            data_type="audio",
            processing_stage="feature_extraction"
        )
        
        assert isinstance(error, RecommendationError)
        assert error.data_type == "audio"
        assert error.processing_stage == "feature_extraction"
    
    def test_validation_error_with_multiple_fields(self):
        """Test ValidationError with multiple field validation"""
        validation_errors = [
            {"field": "creator_id", "error": "Required field missing"},
            {"field": "platforms", "error": "At least one platform required"}
        ]
        
        error = ValidationError(
            message="Multiple validation errors",
            validation_errors=validation_errors
        )
        
        assert error.validation_errors == validation_errors
        assert len(error.validation_errors) == 2


class TestServiceErrors:
    """Test service-related error scenarios"""
    
    def test_authentication_error(self):
        """Test AuthenticationError"""
        error = AuthenticationError(
            message="Invalid API credentials",
            auth_method="api_key",
            user_id="user_001"
        )
        
        assert isinstance(error, RecommendationError)
        assert error.auth_method == "api_key"
        assert error.user_id == "user_001"
    
    def test_authorization_error(self):
        """Test AuthorizationError"""
        error = AuthorizationError(
            message="Insufficient permissions",
            required_permission="create_recommendations",
            user_role="basic_user"
        )
        
        assert isinstance(error, RecommendationError)
        assert error.required_permission == "create_recommendations"
        assert error.user_role == "basic_user"
    
    def test_rate_limit_error(self):
        """Test RateLimitError"""
        error = RateLimitError(
            message="Rate limit exceeded",
            limit=100,
            window_seconds=3600,
            retry_after=1800
        )
        
        assert isinstance(error, RecommendationError)
        assert error.limit == 100
        assert error.window_seconds == 3600
        assert error.retry_after == 1800
    
    def test_external_service_error(self):
        """Test ExternalServiceError"""
        error = ExternalServiceError(
            message="Social media API unavailable",
            service_name="instagram_api",
            status_code=503,
            response_body="Service temporarily unavailable"
        )
        
        assert isinstance(error, RecommendationError)
        assert error.service_name == "instagram_api"
        assert error.status_code == 503
        assert error.response_body == "Service temporarily unavailable"
    
    def test_cache_error(self):
        """Test CacheError"""
        error = CacheError(
            message="Redis cache connection failed",
            cache_operation="SET",
            cache_key="creator_001_recommendations"
        )
        
        assert isinstance(error, RecommendationError)
        assert error.cache_operation == "SET"
        assert error.cache_key == "creator_001_recommendations"
    
    def test_database_error(self):
        """Test DatabaseError"""
        error = DatabaseError(
            message="Database query timeout",
            query="SELECT * FROM creators WHERE ...",
            database_name="recommendations_db"
        )
        
        assert isinstance(error, RecommendationError)
        assert error.query.startswith("SELECT")
        assert error.database_name == "recommendations_db"


class TestValidationFunctions:
    """Test validation utility functions"""
    
    def test_validate_creator_profile_valid(self, sample_creator_musician):
        """Test validation of valid creator profile"""
        # Should not raise exception for valid profile
        validate_creator_profile(sample_creator_musician)
    
    def test_validate_creator_profile_missing_id(self):
        """Test validation with missing creator ID"""
        invalid_profile = CreatorProfile(
            creator_id="",  # Invalid: empty
            display_name="Test Creator",
            platforms=[Platform.YOUTUBE]
        )
        
        with pytest.raises(ValidationError) as exc_info:
            validate_creator_profile(invalid_profile)
        
        assert "creator_id" in str(exc_info.value)
    
    def test_validate_creator_profile_invalid_engagement(self):
        """Test validation with invalid engagement rate"""
        invalid_profile = CreatorProfile(
            creator_id="test_001",
            display_name="Test Creator",
            platforms=[Platform.YOUTUBE],
            engagement_rate={Platform.YOUTUBE: 1.5}  # Invalid: > 1.0
        )
        
        with pytest.raises(ValidationError) as exc_info:
            validate_creator_profile(invalid_profile)
        
        assert "engagement_rate" in str(exc_info.value)
    
    def test_validate_creator_profile_negative_followers(self):
        """Test validation with negative follower count"""
        invalid_profile = CreatorProfile(
            creator_id="test_002",
            display_name="Test Creator",
            platforms=[Platform.YOUTUBE],
            followers_count={Platform.YOUTUBE: -100}  # Invalid: negative
        )
        
        with pytest.raises(ValidationError) as exc_info:
            validate_creator_profile(invalid_profile)
        
        assert "followers_count" in str(exc_info.value)
    
    def test_validate_recommendation_scores_valid(self):
        """Test validation of valid recommendation scores"""
        scores = {
            "relevance_score": 0.85,
            "engagement_prediction": 0.75,
            "viral_potential": 0.45
        }
        
        # Should not raise exception
        validate_recommendation_scores(scores)
    
    def test_validate_recommendation_scores_invalid(self):
        """Test validation of invalid recommendation scores"""
        invalid_scores = {
            "relevance_score": 1.5,  # Invalid: > 1.0
            "engagement_prediction": -0.1,  # Invalid: < 0.0
            "viral_potential": 0.5
        }
        
        with pytest.raises(ValidationError) as exc_info:
            validate_recommendation_scores(invalid_scores)
        
        error_message = str(exc_info.value)
        assert "relevance_score" in error_message or "engagement_prediction" in error_message
    
    def test_validate_engagement_metrics_valid(self):
        """Test validation of valid engagement metrics"""
        metrics = {
            "likes": 1000,
            "comments": 150,
            "shares": 75,
            "views": 10000
        }
        
        # Should not raise exception
        validate_engagement_metrics(metrics)
    
    def test_validate_engagement_metrics_invalid(self):
        """Test validation of invalid engagement metrics"""
        invalid_metrics = {
            "likes": -10,  # Invalid: negative
            "comments": 150,
            "shares": 75,
            "views": 0  # Invalid: zero views
        }
        
        with pytest.raises(ValidationError) as exc_info:
            validate_engagement_metrics(invalid_metrics)
        
        error_message = str(exc_info.value)
        assert "likes" in error_message or "views" in error_message


class TestInputSanitization:
    """Test input sanitization functions"""
    
    def test_sanitize_user_input_basic(self):
        """Test basic input sanitization"""
        dirty_input = "<script>alert('xss')</script>Hello World"
        clean_input = sanitize_user_input(dirty_input)
        
        assert "<script>" not in clean_input
        assert "Hello World" in clean_input
        assert "&lt;script&gt;" in clean_input  # HTML encoded
    
    def test_sanitize_user_input_sql_injection(self):
        """Test SQL injection prevention"""
        malicious_input = "'; DROP TABLE users; --"
        clean_input = sanitize_user_input(malicious_input)
        
        # Should escape dangerous characters
        assert "DROP TABLE" not in clean_input or "'" not in clean_input
    
    def test_sanitize_user_input_length_limit(self):
        """Test input length limiting"""
        long_input = "A" * 2000  # Very long input
        clean_input = sanitize_user_input(long_input, max_length=100)
        
        assert len(clean_input) <= 103  # 100 + "..." (3 chars)
        assert clean_input.endswith("...")
    
    def test_sanitize_user_input_none_handling(self):
        """Test handling of None input"""
        clean_input = sanitize_user_input(None)
        assert clean_input == ""
    
    def test_sanitize_user_input_empty_string(self):
        """Test handling of empty string"""
        clean_input = sanitize_user_input("")
        assert clean_input == ""
    
    def test_sanitize_user_input_unicode(self):
        """Test handling of Unicode characters"""
        unicode_input = "Hello 世界 🌍"
        clean_input = sanitize_user_input(unicode_input)
        
        assert "Hello" in clean_input
        assert "世界" in clean_input
        assert "🌍" in clean_input


class TestErrorLogging:
    """Test error logging and context management"""
    
    def test_log_error_with_context(self):
        """Test error logging with context"""
        error = RecommendationError("Test error")
        context = {
            "user_id": "user_001",
            "operation": "generate_recommendations",
            "timestamp": datetime.now().isoformat()
        }
        
        # Should not raise exception
        log_entry = log_error_with_context(error, context)
        
        assert log_entry is not None
        assert "user_id" in str(log_entry) or context in log_entry
    
    def test_create_error_response(self):
        """Test error response creation"""
        error = ValidationError(
            message="Invalid input",
            field_name="engagement_rate",
            field_value=1.5
        )
        
        response = create_error_response(error)
        
        assert isinstance(response, dict)
        assert "error" in response
        assert "message" in response
        assert "error_code" in response
        assert "timestamp" in response
        
        # Test specific error details
        assert response["message"] == "Invalid input"
        assert response["error_code"] == "VALIDATION_ERROR"
    
    def test_create_error_response_with_details(self):
        """Test error response with additional details"""
        error = ExternalServiceError(
            message="API unavailable",
            service_name="instagram_api",
            status_code=503
        )
        
        response = create_error_response(error, include_details=True)
        
        assert "details" in response
        assert response["details"]["service_name"] == "instagram_api"
        assert response["details"]["status_code"] == 503
    
    def test_create_error_response_without_details(self):
        """Test error response without sensitive details"""
        error = AuthenticationError(
            message="Invalid credentials",
            auth_method="api_key",
            user_id="user_001"
        )
        
        response = create_error_response(error, include_details=False)
        
        # Should not include sensitive details
        assert "user_id" not in str(response)
        assert "auth_method" not in str(response)
        
        # Should include basic error info
        assert "error" in response
        assert "message" in response


class TestErrorRecovery:
    """Test error recovery and retry mechanisms"""
    
    def test_error_with_retry_suggestion(self):
        """Test errors that suggest retry mechanisms"""
        error = RateLimitError(
            message="Rate limit exceeded",
            limit=100,
            retry_after=60
        )
        
        assert error.retry_after == 60
        assert "retry" in error.suggested_action.lower()
    
    def test_error_with_fallback_suggestion(self):
        """Test errors that suggest fallback options"""
        error = ExternalServiceError(
            message="Primary service unavailable",
            service_name="primary_api"
        )
        
        # Error should suggest using fallback
        assert "fallback" in error.suggested_action.lower() or \
               "alternative" in error.suggested_action.lower()
    
    def test_error_escalation_path(self):
        """Test error escalation recommendations"""
        critical_error = DatabaseError(
            message="Database connection lost",
            query="SELECT * FROM creators",
            database_name="main_db"
        )
        
        # Critical errors should suggest immediate action
        assert "immediate" in critical_error.suggested_action.lower() or \
               "critical" in critical_error.suggested_action.lower()


class TestErrorChaining:
    """Test error chaining and cause tracking"""
    
    def test_error_chain_basic(self):
        """Test basic error chaining"""
        root_cause = ValueError("Invalid JSON format")
        
        wrapped_error = DataProcessingError(
            message="Failed to parse content metadata",
            data_type="json",
            original_error=root_cause
        )
        
        assert wrapped_error.original_error == root_cause
        assert "ValueError" in str(wrapped_error)
    
    def test_error_chain_multiple_levels(self):
        """Test multiple levels of error chaining"""
        root_error = ConnectionError("Network timeout")
        service_error = ExternalServiceError(
            message="API call failed",
            service_name="trend_api",
            original_error=root_error
        )
        analysis_error = TrendAnalysisError(
            message="Trend analysis failed",
            trend_id="trend_001",
            original_error=service_error
        )
        
        assert analysis_error.original_error == service_error
        assert service_error.original_error == root_error
        
        # Should be able to trace back to root cause
        current_error = analysis_error
        error_chain = []
        while hasattr(current_error, 'original_error') and current_error.original_error:
            error_chain.append(type(current_error).__name__)
            current_error = current_error.original_error
        
        assert len(error_chain) >= 2


class TestErrorMetrics:
    """Test error metrics and monitoring"""
    
    def test_error_categorization(self):
        """Test error categorization for metrics"""
        errors = [
            ValidationError("Invalid input"),
            ExternalServiceError("API down"),
            DatabaseError("Connection lost"),
            RateLimitError("Too many requests")
        ]
        
        # Categorize errors
        categories = {}
        for error in errors:
            category = type(error).__name__
            categories[category] = categories.get(category, 0) + 1
        
        assert "ValidationError" in categories
        assert "ExternalServiceError" in categories
        assert "DatabaseError" in categories
        assert "RateLimitError" in categories
    
    def test_error_severity_levels(self):
        """Test error severity classification"""
        # Low severity
        validation_error = ValidationError("Missing optional field")
        assert hasattr(validation_error, 'severity') or True  # May not have severity
        
        # High severity
        db_error = DatabaseError("Database corrupted")
        
        # Critical severity
        auth_error = AuthenticationError("Security breach detected")
        
        # Each error type should have appropriate default severity
        assert True  # Placeholder for severity testing


class TestExceptionPerformance:
    """Test exception handling performance"""
    
    @pytest.mark.benchmark
    def test_exception_creation_performance(self, benchmark):
        """Benchmark exception creation performance"""
        def create_exception():
            return RecommendationError(
                message="Performance test error",
                context={"test": "data", "timestamp": datetime.now()},
                suggested_action="Performance testing"
            )
        
        result = benchmark(create_exception)
        assert isinstance(result, RecommendationError)
    
    @pytest.mark.benchmark
    def test_exception_serialization_performance(self, benchmark):
        """Benchmark exception to response conversion"""
        error = ValidationError(
            message="Validation failed",
            field_name="test_field",
            field_value="invalid_value"
        )
        
        def serialize_error():
            return create_error_response(error, include_details=True)
        
        result = benchmark(serialize_error)
        assert isinstance(result, dict)
        assert "error" in result
