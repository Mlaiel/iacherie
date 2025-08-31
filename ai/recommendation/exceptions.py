"""AI Recommendation Exceptions - Error Handling for Recommendation System
======================================================================

Comprehensive exception handling and validation for the Ainflue AI recommendation system.
Provides custom exceptions, validation functions, and error management utilities.

Created by: Fahed Mlaiel (mlaiel@live.de)
© 2025 Fahed Mlaiel. All rights reserved.
"""
from typing import Any, Dict, List, Optional, Union
import logging
import traceback


# Base Exception Classes
class RecommendationError(Exception):
    """Base exception for recommendation system errors."""    
    def __init__(self, message: str, error_code: str = None, details: Dict[str, Any] = None):
        super().__init__(message)
        self.message = message
        self.error_code = error_code or "RECOMMENDATION_ERROR"
        self.details = details or {}


class ContentAnalysisError(RecommendationError):
    """Exception for content analysis errors."""    
    def __init__(self, message: str, content_id: str = None, **kwargs):
        super().__init__(message, "CONTENT_ANALYSIS_ERROR", **kwargs)
        self.content_id = content_id


class CollaborationMatchingError(RecommendationError):
    """Exception for collaboration matching errors."""    
    def __init__(self, message: str, creator_ids: List[str] = None, **kwargs):
        super().__init__(message, "COLLABORATION_MATCHING_ERROR", **kwargs)
        self.creator_ids = creator_ids or []


class TrendAnalysisError(RecommendationError):
    """Exception for trend analysis errors."""    
    def __init__(self, message: str, trend_id: str = None, **kwargs):
        super().__init__(message, "TREND_ANALYSIS_ERROR", **kwargs)
        self.trend_id = trend_id


class RevenueOptimizationError(RecommendationError):
    """Exception for revenue optimization errors."""    
    def __init__(self, message: str, strategy_id: str = None, **kwargs):
        super().__init__(message, "REVENUE_OPTIMIZATION_ERROR", **kwargs)
        self.strategy_id = strategy_id


class ProtectionError(RecommendationError):
    """Exception for content protection errors."""    
    def __init__(self, message: str, protection_type: str = None, **kwargs):
        super().__init__(message, "PROTECTION_ERROR", **kwargs)
        self.protection_type = protection_type


# System Errors
class ModelInitializationError(RecommendationError):
    """Exception for model initialization errors."""    
    def __init__(self, message: str, model_name: str = None, **kwargs):
        super().__init__(message, "MODEL_INITIALIZATION_ERROR", **kwargs)
        self.model_name = model_name


class ValidationError(RecommendationError):
    """Exception for data validation errors."""    
    def __init__(self, message: str, field_name: str = None, **kwargs):
        super().__init__(message, "VALIDATION_ERROR", **kwargs)
        self.field_name = field_name


class DataProcessingError(RecommendationError):
    """Exception for data processing errors."""    
    def __init__(self, message: str, data_type: str = None, **kwargs):
        super().__init__(message, "DATA_PROCESSING_ERROR", **kwargs)
        self.data_type = data_type


# Infrastructure Errors
class AuthenticationError(RecommendationError):
    """Exception for authentication errors."""    
    def __init__(self, message: str, user_id: str = None, **kwargs):
        super().__init__(message, "AUTHENTICATION_ERROR", **kwargs)
        self.user_id = user_id


class AuthorizationError(RecommendationError):
    """Exception for authorization errors."""    
    def __init__(self, message: str, required_permission: str = None, **kwargs):
        super().__init__(message, "AUTHORIZATION_ERROR", **kwargs)
        self.required_permission = required_permission


class RateLimitError(RecommendationError):
    """Exception for rate limiting errors."""    
    def __init__(self, message: str, retry_after: int = None, **kwargs):
        super().__init__(message, "RATE_LIMIT_ERROR", **kwargs)
        self.retry_after = retry_after


class ExternalServiceError(RecommendationError):
    """Exception for external service errors."""    
    def __init__(self, message: str, service_name: str = None, **kwargs):
        super().__init__(message, "EXTERNAL_SERVICE_ERROR", **kwargs)
        self.service_name = service_name


class CacheError(RecommendationError):
    """Exception for cache-related errors."""    
    def __init__(self, message: str, cache_key: str = None, **kwargs):
        super().__init__(message, "CACHE_ERROR", **kwargs)
        self.cache_key = cache_key


class DatabaseError(RecommendationError):
    """Exception for database errors."""    
    def __init__(self, message: str, query: str = None, **kwargs):
        super().__init__(message, "DATABASE_ERROR", **kwargs)
        self.query = query


# Validation Functions
def validate_creator_profile(profile_data: Dict[str, Any]) -> bool:
    """    Validate creator profile data.
    
    Args:
        profile_data: Creator profile data to validate
        
    Returns:
        bool: True if valid
        
    Raises:
        ValidationError: If validation fails
    """    required_fields = ['creator_id', 'username', 'display_name']
    
    for field in required_fields:
        if field not in profile_data:
            raise ValidationError(f"Missing required field: {field}", field_name=field)
        
        if not profile_data[field]:
            raise ValidationError(f"Empty value for required field: {field}", field_name=field)
    
    # Validate creator_id format
    creator_id = profile_data['creator_id']
    if not isinstance(creator_id, str) or len(creator_id) < 3:
        raise ValidationError("Creator ID must be a string with at least 3 characters", field_name="creator_id")
    
    return True


def validate_recommendation_scores(scores: List[float]) -> bool:
    """    Validate recommendation confidence scores.
    
    Args:
        scores: List of confidence scores to validate
        
    Returns:
        bool: True if valid
        
    Raises:
        ValidationError: If validation fails
    """    if not isinstance(scores, list):
        raise ValidationError("Scores must be a list", field_name="scores")
    
    if not scores:
        raise ValidationError("Scores list cannot be empty", field_name="scores")
    
    for i, score in enumerate(scores):
        if not isinstance(score, (int, float)):
            raise ValidationError(f"Score at index {i} must be numeric", field_name=f"scores[{i}]")
        
        if not 0.0 <= score <= 1.0:
            raise ValidationError(f"Score at index {i} must be between 0.0 and 1.0", field_name=f"scores[{i}]")
    
    return True


def validate_engagement_metrics(metrics: Dict[str, Any]) -> bool:
    """    Validate engagement metrics data.
    
    Args:
        metrics: Engagement metrics to validate
        
    Returns:
        bool: True if valid
        
    Raises:
        ValidationError: If validation fails
    """    required_fields = ['likes', 'comments', 'shares', 'views']
    
    for field in required_fields:
        if field not in metrics:
            raise ValidationError(f"Missing required engagement field: {field}", field_name=field)
        
        value = metrics[field]
        if not isinstance(value, int) or value < 0:
            raise ValidationError(f"Field {field} must be a non-negative integer", field_name=field)
    
    # Validate engagement rate if present
    if 'engagement_rate' in metrics:
        rate = metrics['engagement_rate']
        if not isinstance(rate, (int, float)) or not 0.0 <= rate <= 1.0:
            raise ValidationError("Engagement rate must be between 0.0 and 1.0", field_name="engagement_rate")
    
    return True


def sanitize_user_input(user_input: str, max_length: int = 1000) -> str:
    """    Sanitize user input for security.
    
    Args:
        user_input: Raw user input
        max_length: Maximum allowed length
        
    Returns:
        str: Sanitized input
        
    Raises:
        ValidationError: If input is invalid
    """    if not isinstance(user_input, str):
        raise ValidationError("User input must be a string")
    
    if len(user_input) > max_length:
        raise ValidationError(f"Input too long, maximum {max_length} characters allowed")
    
    # Basic sanitization - remove potential harmful characters
    sanitized = user_input.strip()
    
    # Remove or escape potentially dangerous characters
    dangerous_chars = ['<', '>', '"', "'", '&', '\x00']
    for char in dangerous_chars:
        sanitized = sanitized.replace(char, '')
    
    return sanitized


def log_error_with_context(
    error: Exception, 
    context: Dict[str, Any] = None,
    logger: logging.Logger = None
) -> None:
    """    Log error with context information.
    
    Args:
        error: Exception to log
        context: Additional context information
        logger: Logger instance to use
    """    if logger is None:
        logger = logging.getLogger(__name__)
    
    context = context or {}
    
    error_info = {
        'error_type': type(error).__name__,
        'error_message': str(error),
        'traceback': traceback.format_exc(),
        'context': context
    }
    
    # Add specific error details if it's a RecommendationError
    if isinstance(error, RecommendationError):
        error_info.update({
            'error_code': error.error_code,
            'error_details': error.details
        })
    
    logger.error(f"Error occurred: {error_info}")


def create_error_response(
    error: Exception, 
    request_id: str = None,
    include_traceback: bool = False
) -> Dict[str, Any]:
    """    Create standardized error response.
    
    Args:
        error: Exception that occurred
        request_id: Request ID for tracking
        include_traceback: Whether to include traceback in response
        
    Returns:
        dict: Standardized error response
    """    response = {
        'success': False,
        'error': {
            'type': type(error).__name__,
            'message': str(error)
        }
    }
    
    if request_id:
        response['request_id'] = request_id
    
    # Add specific error details if it's a RecommendationError
    if isinstance(error, RecommendationError):
        response['error'].update({
            'code': error.error_code,
            'details': error.details
        })
    
    if include_traceback:
        response['error']['traceback'] = traceback.format_exc()
    
    return response


# Export all exceptions and functions
__all__ = [
    # Base Exceptions
    'RecommendationError',
    'ContentAnalysisError', 
    'CollaborationMatchingError',
    'TrendAnalysisError',
    'RevenueOptimizationError',
    'ProtectionError',
    
    # System Exceptions
    'ModelInitializationError',
    'ValidationError',
    'DataProcessingError',
    
    # Infrastructure Exceptions
    'AuthenticationError',
    'AuthorizationError', 
    'RateLimitError',
    'ExternalServiceError',
    'CacheError',
    'DatabaseError',
    
    # Validation Functions
    'validate_creator_profile',
    'validate_recommendation_scores',
    'validate_engagement_metrics',
    'sanitize_user_input',
    
    # Utility Functions
    'log_error_with_context',
    'create_error_response'
]