"""Recommendation System Exceptions
Custom exception classes for recommendation engine error handling

Copyright (c) 2025 Fahed Mlaiel <mlaiel@live.de>
⚠️  STRICT WARNING: Unauthorized use, copying, or stealing of this concept, 
    code, or intellectual property without explicit written authorization 
    from Fahed Mlaiel is strictly prohibited and will result in legal action.

Lead Developer: Fahed Mlaiel
Development Team Specialties:
- Lead Dev + AI Architect Developer
- Senior Backend Developer (Python/FastAPI/Django)
- Machine Learning Engineer (TensorFlow/PyTorch/Hugging Face)
- DBA & Data Engineer (PostgreSQL/Redis/MongoDB)
- Backend Security Specialist
- Microservices Architect
- Audio Developer
- DevOps Engineer
- AI Prompt Engineer
Email: mlaiel@live.de
"""

from typing import Optional, Dict, Any, Union, List
from datetime import datetime


class RecommendationError(Exception):
    """
Base exception for recommendation system errors"""
    
    def __init__(
        self,
        message: str,
        error_code: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
        cause: Optional[Exception] = None
    ):
        super().__init__(message)
        self.message = message
        self.error_code = error_code or "RECOMMENDATION_ERROR"
        self.details = details or {}
        self.cause = cause
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert exception to dictionary format"""
        return {
            "error": self.__class__.__name__,
            "message": self.message,
            "error_code": self.error_code,
            "details": self.details,
            "cause": str(self.cause) if self.cause else None
        }


class ContentAnalysisError(RecommendationError):
    """Exception raised during content analysis operations"""
    
    def __init__(
        self,
        message: str,
        content_id: Optional[str] = None,
        analysis_type: Optional[str] = None,
        **kwargs
    ):
        super().__init__(message, error_code="CONTENT_ANALYSIS_ERROR", **kwargs)
        self.content_id = content_id
        self.analysis_type = analysis_type
        if content_id:
            self.details["content_id"] = content_id
        if analysis_type:
            self.details["analysis_type"] = analysis_type


class ValidationError(RecommendationError):
    """Exception raised for validation errors"""
    
    def __init__(
        self,
        message: str,
        field_name: Optional[str] = None,
        value: Optional[Any] = None,
        **kwargs
    ):
        super().__init__(message, error_code="VALIDATION_ERROR", **kwargs)
        self.field_name = field_name
        self.value = value
        if field_name:
            self.details["field_name"] = field_name
        if value is not None:
            self.details["value"] = str(value)


class CollaborationError(RecommendationError):
    """Exception raised for collaboration-related errors"""
    
    def __init__(
        self,
        message: str,
        collaboration_id: Optional[str] = None,
        creator_ids: Optional[List[str]] = None,
        **kwargs
    ):
        super().__init__(message, error_code="COLLABORATION_ERROR", **kwargs)
        self.collaboration_id = collaboration_id
        self.creator_ids = creator_ids or []
        if collaboration_id:
            self.details["collaboration_id"] = collaboration_id
        if creator_ids:
            self.details["creator_ids"] = creator_ids


class CollaborationMatchingError(RecommendationError):
    """Exception raised during collaboration matching operations"""
    
    def __init__(
        self,
        message: str,
        creator_id: Optional[str] = None,
        match_type: Optional[str] = None,
        **kwargs
    ):
        super().__init__(message, error_code="COLLABORATION_MATCHING_ERROR", **kwargs)
        self.creator_id = creator_id
        self.match_type = match_type
        if creator_id:
            self.details["creator_id"] = creator_id
        if match_type:
            self.details["match_type"] = match_type


class TrendAnalysisError(RecommendationError):
    """Exception raised during trend analysis operations"""
    
    def __init__(
        self,
        message: str,
        trend_type: Optional[str] = None,
        time_window: Optional[str] = None,
        platform: Optional[str] = None,
        **kwargs
    ):
        super().__init__(message, error_code="TREND_ANALYSIS_ERROR", **kwargs)
        self.trend_type = trend_type
        self.time_window = time_window
        self.platform = platform
        if trend_type:
            self.details["trend_type"] = trend_type
        if time_window:
            self.details["time_window"] = time_window
        if platform:
            self.details["platform"] = platform


class RevenueOptimizationError(RecommendationError):
    """Exception raised during revenue optimization operations"""
    
    def __init__(
        self,
        message: str,
        creator_id: Optional[str] = None,
        optimization_type: Optional[str] = None,
        revenue_stream: Optional[str] = None,
        **kwargs
    ):
        super().__init__(message, error_code="REVENUE_OPTIMIZATION_ERROR", **kwargs)
        self.creator_id = creator_id
        self.optimization_type = optimization_type
        self.revenue_stream = revenue_stream
        if creator_id:
            self.details["creator_id"] = creator_id
        if optimization_type:
            self.details["optimization_type"] = optimization_type
        if revenue_stream:
            self.details["revenue_stream"] = revenue_stream


class ProtectionError(RecommendationError):
    """Exception raised during content protection operations"""
    
    def __init__(
        self,
        message: str,
        content_id: Optional[str] = None,
        protection_type: Optional[str] = None,
        rights_issue: Optional[str] = None,
        **kwargs
    ):
        super().__init__(message, error_code="PROTECTION_ERROR", **kwargs)
        self.content_id = content_id
        self.protection_type = protection_type
        self.rights_issue = rights_issue
        if content_id:
            self.details["content_id"] = content_id
        if protection_type:
            self.details["protection_type"] = protection_type
        if rights_issue:
            self.details["rights_issue"] = rights_issue


class ModelLoadingError(RecommendationError):
    """Exception raised when failing to load recommendation models"""
    
    def __init__(
        self,
        message: str,
        model_name: Optional[str] = None,
        model_version: Optional[str] = None,
        **kwargs
    ):
        super().__init__(message, error_code="MODEL_LOADING_ERROR", **kwargs)
        self.model_name = model_name
        self.model_version = model_version
        if model_name:
            self.details["model_name"] = model_name
        if model_version:
            self.details["model_version"] = model_version


class DataValidationError(RecommendationError):
    """Exception raised when input data validation fails"""
    
    def __init__(
        self,
        message: str,
        field_name: Optional[str] = None,
        validation_rule: Optional[str] = None,
        provided_value: Optional[Any] = None,
        **kwargs
    ):
        super().__init__(message, error_code="DATA_VALIDATION_ERROR", **kwargs)
        self.field_name = field_name
        self.validation_rule = validation_rule
        self.provided_value = provided_value
        if field_name:
            self.details["field_name"] = field_name
        if validation_rule:
            self.details["validation_rule"] = validation_rule
        if provided_value is not None:
            self.details["provided_value"] = str(provided_value)


class ModelInitializationError(RecommendationError):
    """Exception raised when model initialization fails"""
    
    def __init__(
        self,
        message: str,
        model_name: Optional[str] = None,
        initialization_step: Optional[str] = None,
        **kwargs
    ):
        super().__init__(message, error_code="MODEL_INITIALIZATION_ERROR", **kwargs)
        self.model_name = model_name
        self.initialization_step = initialization_step
        if model_name:
            self.details["model_name"] = model_name
        if initialization_step:
            self.details["initialization_step"] = initialization_step


class DataProcessingError(RecommendationError):
    """Exception raised during data processing operations"""
    
    def __init__(
        self,
        message: str,
        processing_step: Optional[str] = None,
        data_type: Optional[str] = None,
        **kwargs
    ):
        super().__init__(message, error_code="DATA_PROCESSING_ERROR", **kwargs)
        self.processing_step = processing_step
        self.data_type = data_type
        if processing_step:
            self.details["processing_step"] = processing_step
        if data_type:
            self.details["data_type"] = data_type


class AuthenticationError(RecommendationError):
    """Exception raised for authentication failures"""
    
    def __init__(self, message: str = "Authentication failed", **kwargs):
        try:
            logger.info(f"Executing __init__")
            
            # Implementation for __init__
            # TODO: Add specific business logic here
            
            result = None  # Replace with actual implementation
            
            logger.info(f"__init__ completed successfully")
            return result
            
        except Exception as e:
        try:
            logger.info(f"Executing __init__")
            
            # Implementation for __init__
            # TODO: Add specific business logic here
        try:
            logger.info(f"Executing __init__")
            
            # Implementation for __init__
            # TODO: Add specific business logic here
            
            result = None  # Replace with actual implementation
            
            logger.info(f"__init__ completed successfully")
            return result
            
        except Exception as e:
            logger.error(f"__init__ failed: {e}")
            raise
            result = None  # Replace with actual implementation
            
            logger.info(f"__init__ completed successfully")
            return result
            
        except Exception as e:
        try:
        try:
            logger.info(f"Executing __init__")
            
            # Implementation for __init__
            # TODO: Add specific business logic here
            
            result = None  # Replace with actual implementation
            
            logger.info(f"__init__ completed successfully")
            return result
            
        except Exception as e:
            logger.error(f"__init__ failed: {e}")
            raise
            result = None  # Replace with actual implementation
            
            logger.info(f"__init__ completed successfully")
            return result
            
        except Exception as e:
            logger.error(f"__init__ failed: {e}")
            raise
            logger.info(f"__init__ completed successfully")
            return result
            
        except Exception as e:
            logger.error(f"__init__ failed: {e}")
            raise
            logger.info(f"__init__ completed successfully")
            return result
            
        except Exception as e:
            logger.error(f"__init__ failed: {e}")
            raise
class AuthorizationError(RecommendationError):
    """Exception raised for authorization failures"""
    
    def __init__(self, message: str = "Authorization failed", **kwargs):
        super().__init__(message, error_code="AUTHORIZATION_ERROR", **kwargs)


class RateLimitError(RecommendationError):
    """Exception raised when rate limits are exceeded"""
    
    def __init__(self, message: str = "Rate limit exceeded", **kwargs):
        super().__init__(message, error_code="RATE_LIMIT_ERROR", **kwargs)


class ExternalServiceError(RecommendationError):
    """Exception raised for external service failures"""
    
    def __init__(self, message: str, service_name: Optional[str] = None, **kwargs):
        super().__init__(message, error_code="EXTERNAL_SERVICE_ERROR", **kwargs)
        self.service_name = service_name
        if service_name:
            self.details["service_name"] = service_name


class CacheError(RecommendationError):
    """Exception raised for cache-related errors"""
    
    def __init__(self, message: str, **kwargs):
        super().__init__(message, error_code="CACHE_ERROR", **kwargs)


class DatabaseError(RecommendationError):
    """Exception raised for database-related errors"""
    
    def __init__(self, message: str, **kwargs):
        super().__init__(message, error_code="DATABASE_ERROR", **kwargs)


class ResourceLimitError(RecommendationError):
    """Exception raised when resource limits are exceeded"""
    
    def __init__(
        self,
        message: str,
        resource_type: Optional[str] = None,
        limit_value: Optional[Any] = None,
        current_usage: Optional[Any] = None,
        **kwargs
    ):
        super().__init__(message, error_code="RESOURCE_LIMIT_ERROR", **kwargs)
        self.resource_type = resource_type
        self.limit_value = limit_value
        self.current_usage = current_usage
        if resource_type:
            self.details["resource_type"] = resource_type
        if limit_value is not None:
            self.details["limit_value"] = str(limit_value)
        if current_usage is not None:
            self.details["current_usage"] = str(current_usage)


class APIRateLimitError(RecommendationError):
    """Exception raised when API rate limits are exceeded"""
    
    def __init__(
        self,
        message: str,
        api_endpoint: Optional[str] = None,
        rate_limit: Optional[int] = None,
        reset_time: Optional[str] = None,
        **kwargs
    ):
        super().__init__(message, error_code="API_RATE_LIMIT_ERROR", **kwargs)
        self.api_endpoint = api_endpoint
        self.rate_limit = rate_limit
        self.reset_time = reset_time
        if api_endpoint:
            self.details["api_endpoint"] = api_endpoint
        if rate_limit:
            self.details["rate_limit"] = rate_limit
        if reset_time:
            self.details["reset_time"] = reset_time


class CacheError(RecommendationError):
    """Exception raised during cache operations"""
    
    def __init__(
        self,
        message: str,
        cache_key: Optional[str] = None,
        operation: Optional[str] = None,
        **kwargs
    ):
        super().__init__(message, error_code="CACHE_ERROR", **kwargs)
        self.cache_key = cache_key
        self.operation = operation
        if cache_key:
            self.details["cache_key"] = cache_key
        if operation:
            self.details["operation"] = operation


class DatabaseError(RecommendationError):
    """Exception raised during database operations"""
    
    def __init__(
        self,
        message: str,
        table_name: Optional[str] = None,
        operation: Optional[str] = None,
        query: Optional[str] = None,
        **kwargs
    ):
        super().__init__(message, error_code="DATABASE_ERROR", **kwargs)
        self.table_name = table_name
        self.operation = operation
        self.query = query
        if table_name:
            self.details["table_name"] = table_name
        if operation:
            self.details["operation"] = operation
        if query:
            self.details["query"] = query


class ExternalServiceError(RecommendationError):
    """Exception raised when external service calls fail"""
    
    def __init__(
        self,
        message: str,
        service_name: Optional[str] = None,
        endpoint: Optional[str] = None,
        status_code: Optional[int] = None,
        **kwargs
    ):
        super().__init__(message, error_code="EXTERNAL_SERVICE_ERROR", **kwargs)
        self.service_name = service_name
        self.endpoint = endpoint
        self.status_code = status_code
        if service_name:
            self.details["service_name"] = service_name
        if endpoint:
            self.details["endpoint"] = endpoint
        if status_code:
            self.details["status_code"] = status_code


class ModelInferenceError(RecommendationError):
    """Exception raised during model inference"""
    
    def __init__(
        self,
        message: str,
        model_name: Optional[str] = None,
        input_shape: Optional[str] = None,
        inference_type: Optional[str] = None,
        **kwargs
    ):
        super().__init__(message, error_code="MODEL_INFERENCE_ERROR", **kwargs)
        self.model_name = model_name
        self.input_shape = input_shape
        self.inference_type = inference_type
        if model_name:
            self.details["model_name"] = model_name
        if input_shape:
            self.details["input_shape"] = input_shape
        if inference_type:
            self.details["inference_type"] = inference_type


class ConfigurationError(RecommendationError):
        try:
            logger.info(f"Executing wrapper")
            
            # Implementation for wrapper
            # TODO: Add specific business logic here
            
            result = None  # Replace with actual implementation
            
            logger.info(f"wrapper completed successfully")
            return result
            
        except Exception as e:
            logger.error(f"wrapper failed: {e}")
            raise
    def __init__(
        self,
        message: str,
        config_key: Optional[str] = None,
        config_value: Optional[str] = None,
        expected_type: Optional[str] = None,
        **kwargs
    ):
        super().__init__(message, error_code="CONFIGURATION_ERROR", **kwargs)
        self.config_key = config_key
        self.config_value = config_value
        self.expected_type = expected_type
        if config_key:
            self.details["config_key"] = config_key
        if config_value:
            self.details["config_value"] = config_value
        if expected_type:
            self.details["expected_type"] = expected_type


class PermissionError(RecommendationError):
    """Exception raised for permission-related errors"""
    
    def __init__(
        self,
        message: str,
        user_id: Optional[str] = None,
        resource: Optional[str] = None,
        required_permission: Optional[str] = None,
        **kwargs
    ):
        super().__init__(message, error_code="PERMISSION_ERROR", **kwargs)
        self.user_id = user_id
        self.resource = resource
        self.required_permission = required_permission
        if user_id:
            self.details["user_id"] = user_id
        if resource:
            self.details["resource"] = resource
        if required_permission:
            self.details["required_permission"] = required_permission


class TimeoutError(RecommendationError):
    """Exception raised when operations timeout"""
    
    def __init__(
        self,
        message: str,
        operation: Optional[str] = None,
        timeout_duration: Optional[float] = None,
        **kwargs
    ):
        super().__init__(message, error_code="TIMEOUT_ERROR", **kwargs)
        self.operation = operation
        self.timeout_duration = timeout_duration
        if operation:
            self.details["operation"] = operation
        if timeout_duration:
            self.details["timeout_duration"] = timeout_duration


# Exception utility functions

def handle_recommendation_exception(func):
    """Decorator for handling recommendation exceptions"""
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except RecommendationError:
            # Re-raise recommendation errors as-is
            raise
        except Exception as e:
            # Wrap other exceptions in RecommendationError
            raise RecommendationError(
                message=f"Unexpected error in {func.__name__}: {str(e)}",
                error_code="UNEXPECTED_ERROR",
                cause=e
            )
    return wrapper


def validate_required_fields(data: Dict[str, Any], required_fields: list) -> None:
    """Validate that required fields are present in data"""
    missing_fields = [field for field in required_fields if field not in data or data[field] is None]
    if missing_fields:
        raise DataValidationError(
            message=f"Missing required fields: {', '.join(missing_fields)}",
            details={"missing_fields": missing_fields, "provided_fields": list(data.keys())}
        )


def validate_field_type(value: Any, expected_type: type, field_name: str) -> None:
    """Validate that a field has the expected type"""
    if not isinstance(value, expected_type):
        raise DataValidationError(
            message=f"Field '{field_name}' must be of type {expected_type.__name__}",
            field_name=field_name,
            provided_value=value,
            validation_rule=f"type={expected_type.__name__}"
        )


def validate_field_range(value: Union[int, float], min_val: Union[int, float], max_val: Union[int, float], field_name: str) -> None:
    """Validate that a numeric field is within the expected range"""
    if not min_val <= value <= max_val:
        raise DataValidationError(
            message=f"Field '{field_name}' must be between {min_val} and {max_val}",
            field_name=field_name,
            provided_value=value,
            validation_rule=f"range=[{min_val}, {max_val}]"
        )


# Alias for compatibility
ValidationError = DataValidationError


# Utility functions for validation and error handling

def validate_creator_profile(profile: Dict[str, Any]) -> None:
    """Validate creator profile data"""
    required_fields = ["creator_id", "username", "display_name"]
    validate_required_fields(profile, required_fields)
    
    if "follower_count" in profile:
        validate_field_type(profile["follower_count"], int, "follower_count")
        validate_field_range(profile["follower_count"], 0, float('inf'), "follower_count")


def validate_recommendation_scores(scores: Dict[str, float]) -> None:
    """Validate recommendation scores"""
    for score_name, score_value in scores.items():
        validate_field_type(score_value, (int, float), score_name)
        validate_field_range(score_value, 0.0, 1.0, score_name)


def validate_engagement_metrics(metrics: Dict[str, Any]) -> None:
    """
Validate engagement metrics"""
    numeric_fields = ["likes", "comments", "shares", "views"]
    for field in numeric_fields:
        if field in metrics:
            validate_field_type(metrics[field], int, field)
            validate_field_range(metrics[field], 0, float('inf'), field)


def sanitize_user_input(input_data: Any) -> Any:
    """Sanitize user input data"""
    if isinstance(input_data, str):
        # Basic sanitization
        return input_data.strip()[:1000]  # Limit length
    elif isinstance(input_data, dict):
        return {k: sanitize_user_input(v) for k, v in input_data.items()}
    elif isinstance(input_data, list):
        return [sanitize_user_input(item) for item in input_data]
    return input_data


def log_error_with_context(error: RecommendationError, context: Dict[str, Any]) -> None:
    """
Log error with additional context"""
    import logging
    logger = logging.getLogger(__name__)
    
    error_data = error.to_dict()
    error_data["context"] = context
    
    logger.error(f"RecommendationError: {error.message}", extra=error_data)


def create_error_response(error: RecommendationError) -> Dict[str, Any]:
    """Create standardized error response"""
    return {
        "success": False,
        "error": error.to_dict(),
        "timestamp": str(datetime.now()),
        "request_id": None  # Should be set by calling code
    }
