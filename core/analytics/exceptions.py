"""Analytics Exceptions - Specialized Exception Classes

Custom exception classes for analytics operations with detailed error handling
and debugging information for industrial IA influencer platform.

Created by: Fahed Mlaiel (mlaiel@live.de)
© 2025 Fahed Mlaiel. All rights reserved.

⚠️ STRICT COPYRIGHT WARNING ⚠️
This code is the intellectual property of Fahed Mlaiel (mlaiel@live.de).
ANY unauthorized use, reproduction, or distribution is STRICTLY PROHIBITED.
Legal action will be taken against violators under German and international law.
Contact mlaiel@live.de for licensing inquiries.

Team Specialists:
- Lead IA Developer: Fahed Mlaiel (mlaiel@live.de)
- Backend Senior Engineer: Advanced microservices architecture
- ML Engineer: Deep learning & analytics algorithms
- Database Administrator: High-performance data optimization
- Security Expert: Enterprise-grade protection systems
- Microservices Architect: Scalable distributed systems
- Audio Processing Specialist: Advanced audio AI algorithms
- DevOps Engineer: Production-ready infrastructure
- IA Prompt Engineer: Optimized AI model interactions
"""
from typing import Dict, Any, Optional, List
from datetime import datetime
from enum import Enum


class ErrorSeverity(Enum):
    """Error severity levels"""    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ErrorCategory(Enum):
    """Error category classification"""    VALIDATION = "validation"
    PROCESSING = "processing"
    STORAGE = "storage"
    NETWORK = "network"
    AUTHENTICATION = "authentication"
    AUTHORIZATION = "authorization"
    CONFIGURATION = "configuration"
    RESOURCE = "resource"
    BUSINESS_LOGIC = "business_logic"
    EXTERNAL_SERVICE = "external_service"


class AnalyticsBaseError(Exception):
    """Base exception class for all analytics errors"""    
    def __init__(
        self,
        message: str,
        error_code: Optional[str] = None,
        severity: ErrorSeverity = ErrorSeverity.MEDIUM,
        category: ErrorCategory = ErrorCategory.PROCESSING,
        details: Optional[Dict[str, Any]] = None,
        context: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message)
        
        self.message = message
        self.error_code = error_code or self._generate_error_code()
        self.severity = severity
        self.category = category
        self.details = details or {}
        self.context = context or {}
        self.timestamp = datetime.now()
        
        # Add class name to context
        self.context['exception_class'] = self.__class__.__name__
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert exception to dictionary for logging/serialization"""        return {
            'error_code': self.error_code,
            'message': self.message,
            'severity': self.severity.value,
            'category': self.category.value,
            'timestamp': self.timestamp.isoformat(),
            'details': self.details,
            'context': self.context
        }
    
    def _generate_error_code(self) -> str:
        """Generate unique error code"""        import uuid
        return f"{self.__class__.__name__.upper()}_{uuid.uuid4().hex[:8]}"


class AnalyticsError(AnalyticsBaseError):
    """General analytics operation error"""    
    def __init__(self, message: str, **kwargs):
        super().__init__(
            message,
            category=ErrorCategory.PROCESSING,
            **kwargs
        )


class MetricsError(AnalyticsBaseError):
    """Metrics collection and processing error"""    
    def __init__(self, message: str, **kwargs):
        super().__init__(
            message,
            category=ErrorCategory.PROCESSING,
            **kwargs
        )


class ReportingError(AnalyticsBaseError):
    """Report generation and delivery error"""    
    def __init__(self, message: str, **kwargs):
        super().__init__(
            message,
            category=ErrorCategory.PROCESSING,
            **kwargs
        )


class DataValidationError(AnalyticsBaseError):
    """Data validation error"""    
    def __init__(
        self,
        message: str,
        field_name: Optional[str] = None,
        field_value: Optional[Any] = None,
        validation_rule: Optional[str] = None,
        **kwargs
    ):
        details = kwargs.get('details', {})
        details.update({
            'field_name': field_name,
            'field_value': field_value,
            'validation_rule': validation_rule
        })
        
        super().__init__(
            message,
            category=ErrorCategory.VALIDATION,
            severity=ErrorSeverity.MEDIUM,
            details=details,
            **kwargs
        )


class DataProcessingError(AnalyticsBaseError):
    """Data processing error"""    
    def __init__(
        self,
        message: str,
        operation: Optional[str] = None,
        input_data: Optional[Dict[str, Any]] = None,
        **kwargs
    ):
        details = kwargs.get('details', {})
        details.update({
            'operation': operation,
            'input_data_size': len(str(input_data)) if input_data else 0
        })
        
        super().__init__(
            message,
            category=ErrorCategory.PROCESSING,
            details=details,
            **kwargs
        )


class StorageError(AnalyticsBaseError):
    """Storage operation error"""    
    def __init__(
        self,
        message: str,
        storage_type: Optional[str] = None,
        operation: Optional[str] = None,
        **kwargs
    ):
        details = kwargs.get('details', {})
        details.update({
            'storage_type': storage_type,
            'operation': operation
        })
        
        super().__init__(
            message,
            category=ErrorCategory.STORAGE,
            details=details,
            **kwargs
        )


class AggregationError(AnalyticsBaseError):
    """Data aggregation error"""    
    def __init__(
        self,
        message: str,
        aggregation_type: Optional[str] = None,
        time_period: Optional[str] = None,
        **kwargs
    ):
        details = kwargs.get('details', {})
        details.update({
            'aggregation_type': aggregation_type,
            'time_period': time_period
        })
        
        super().__init__(
            message,
            category=ErrorCategory.PROCESSING,
            details=details,
            **kwargs
        )


class DashboardError(AnalyticsBaseError):
    """Dashboard generation error"""    
    def __init__(
        self,
        message: str,
        dashboard_type: Optional[str] = None,
        component: Optional[str] = None,
        **kwargs
    ):
        details = kwargs.get('details', {})
        details.update({
            'dashboard_type': dashboard_type,
            'component': component
        })
        
        super().__init__(
            message,
            category=ErrorCategory.PROCESSING,
            details=details,
            **kwargs
        )


class PredictionError(AnalyticsBaseError):
    """Predictive analytics error"""    
    def __init__(
        self,
        message: str,
        model_type: Optional[str] = None,
        prediction_type: Optional[str] = None,
        **kwargs
    ):
        details = kwargs.get('details', {})
        details.update({
            'model_type': model_type,
            'prediction_type': prediction_type
        })
        
        super().__init__(
            message,
            category=ErrorCategory.PROCESSING,
            severity=ErrorSeverity.HIGH,
            details=details,
            **kwargs
        )


class BusinessIntelligenceError(AnalyticsBaseError):
    """Business intelligence processing error"""    
    def __init__(
        self,
        message: str,
        analysis_type: Optional[str] = None,
        data_period: Optional[str] = None,
        **kwargs
    ):
        details = kwargs.get('details', {})
        details.update({
            'analysis_type': analysis_type,
            'data_period': data_period
        })
        
        super().__init__(
            message,
            category=ErrorCategory.BUSINESS_LOGIC,
            details=details,
            **kwargs
        )


class TrackingError(AnalyticsBaseError):
    """User/content tracking error"""    
    def __init__(
        self,
        message: str,
        tracking_type: Optional[str] = None,
        entity_id: Optional[str] = None,
        **kwargs
    ):
        details = kwargs.get('details', {})
        details.update({
            'tracking_type': tracking_type,
            'entity_id': entity_id
        })
        
        super().__init__(
            message,
            category=ErrorCategory.PROCESSING,
            details=details,
            **kwargs
        )


class ConfigurationError(AnalyticsBaseError):
    """Configuration error"""    
    def __init__(
        self,
        message: str,
        config_section: Optional[str] = None,
        config_key: Optional[str] = None,
        **kwargs
    ):
        details = kwargs.get('details', {})
        details.update({
            'config_section': config_section,
            'config_key': config_key
        })
        
        super().__init__(
            message,
            category=ErrorCategory.CONFIGURATION,
            severity=ErrorSeverity.HIGH,
            details=details,
            **kwargs
        )


class ResourceError(AnalyticsBaseError):
    """Resource limitation error"""    
    def __init__(
        self,
        message: str,
        resource_type: Optional[str] = None,
        current_usage: Optional[float] = None,
        limit: Optional[float] = None,
        **kwargs
    ):
        details = kwargs.get('details', {})
        details.update({
            'resource_type': resource_type,
            'current_usage': current_usage,
            'limit': limit,
            'usage_percentage': (current_usage / limit * 100) if current_usage and limit else None
        })
        
        super().__init__(
            message,
            category=ErrorCategory.RESOURCE,
            severity=ErrorSeverity.HIGH,
            details=details,
            **kwargs
        )


class ExternalServiceError(AnalyticsBaseError):
    """External service integration error"""    
    def __init__(
        self,
        message: str,
        service_name: Optional[str] = None,
        endpoint: Optional[str] = None,
        status_code: Optional[int] = None,
        **kwargs
    ):
        details = kwargs.get('details', {})
        details.update({
            'service_name': service_name,
            'endpoint': endpoint,
            'status_code': status_code
        })
        
        super().__init__(
            message,
            category=ErrorCategory.EXTERNAL_SERVICE,
            details=details,
            **kwargs
        )


class AuthenticationError(AnalyticsBaseError):
    """Authentication error"""    
    def __init__(self, message: str, **kwargs):
        super().__init__(
            message,
            category=ErrorCategory.AUTHENTICATION,
            severity=ErrorSeverity.HIGH,
            **kwargs
        )


class AuthorizationError(AnalyticsBaseError):
    """Authorization error"""    
    def __init__(
        self,
        message: str,
        user_id: Optional[str] = None,
        required_permission: Optional[str] = None,
        **kwargs
    ):
        details = kwargs.get('details', {})
        details.update({
            'user_id': user_id,
            'required_permission': required_permission
        })
        
        super().__init__(
            message,
            category=ErrorCategory.AUTHORIZATION,
            severity=ErrorSeverity.HIGH,
            details=details,
            **kwargs
        )


class CriticalSystemError(AnalyticsBaseError):
    """Critical system error that requires immediate attention"""    
    def __init__(
        self,
        message: str,
        system_component: Optional[str] = None,
        impact_level: Optional[str] = None,
        **kwargs
    ):
        details = kwargs.get('details', {})
        details.update({
            'system_component': system_component,
            'impact_level': impact_level
        })
        
        super().__init__(
            message,
            category=ErrorCategory.PROCESSING,
            severity=ErrorSeverity.CRITICAL,
            details=details,
            **kwargs
        )


def handle_analytics_exception(
    func: callable,
    *args,
    error_context: Optional[Dict[str, Any]] = None,
    **kwargs
) -> Any:
    """    Decorator function for handling analytics exceptions with context
    
    Args:
        func: Function to execute
        error_context: Additional context for error handling
        *args, **kwargs: Function arguments
    
    Returns:
        Function result or raises appropriate exception
    """    try:
        return func(*args, **kwargs)
    except AnalyticsBaseError:
        # Re-raise analytics errors as-is
        raise
    except Exception as e:
        # Convert generic exceptions to analytics errors
        context = error_context or {}
        context.update({
            'function_name': func.__name__,
            'original_exception': str(e),
            'original_exception_type': type(e).__name__
        })
        
        raise AnalyticsError(
            f"Unexpected error in {func.__name__}: {str(e)}",
            context=context,
            severity=ErrorSeverity.HIGH
        ) from e


def create_error_response(
    error: AnalyticsBaseError,
    include_details: bool = False
) -> Dict[str, Any]:
    """    Create standardized error response for API endpoints
    
    Args:
        error: Analytics exception
        include_details: Whether to include detailed error information
    
    Returns:
        Standardized error response dictionary
    """    response = {
        'success': False,
        'error': {
            'code': error.error_code,
            'message': error.message,
            'severity': error.severity.value,
            'category': error.category.value,
            'timestamp': error.timestamp.isoformat()
        }
    }
    
    if include_details:
        response['error']['details'] = error.details
        response['error']['context'] = error.context
    
    return response
