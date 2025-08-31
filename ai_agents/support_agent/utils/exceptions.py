"""Support Agent Exceptions

Specialized exception classes for Support Agent with detailed error handling,
logging integration, and recovery suggestions.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️  CRITICAL LEGAL NOTICE:
This code and architectural design are the exclusive intellectual property of Fahed Mlaiel.
Unauthorized use, copying, distribution, or commercialization is strictly prohibited.
"""
from typing import Dict, Any, Optional, List
from datetime import datetime, timezone
from enum import Enum

class SupportErrorCategory(Enum):
    """Categories of support errors"""
    CONFIGURATION = "configuration"
    AI_MODEL = "ai_model"
    DATABASE = "database"
    KNOWLEDGE_BASE = "knowledge_base"
    CONVERSATION = "conversation"
    TICKET_MANAGEMENT = "ticket_management"
    ESCALATION = "escalation"
    PERFORMANCE = "performance"
    SECURITY = "security"
    VALIDATION = "validation"
    EXTERNAL_SERVICE = "external_service"

class SupportErrorSeverity(Enum):
    """Error severity levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class SupportAgentException(Exception):
    """Base exception class for Support Agent"""
    
    def __init__(
        self,
        message: str,
        category: SupportErrorCategory = SupportErrorCategory.CONFIGURATION,
        severity: SupportErrorSeverity = SupportErrorSeverity.MEDIUM,
        error_code: str = None,
        context: Dict[str, Any] = None,
        recovery_suggestions: List[str] = None
    ):
        super().__init__(message)
        self.message = message
        self.category = category
        self.severity = severity
        self.error_code = error_code or self._generate_error_code()
        self.context = context or {}
        self.recovery_suggestions = recovery_suggestions or []
        self.timestamp = datetime.now(timezone.utc)
        
    def _generate_error_code(self) -> str:
        """Generate error code based on category and timestamp"""
        timestamp_str = self.timestamp.strftime("%Y%m%d%H%M")
        return f"SUP_{self.category.value.upper()}_{timestamp_str}"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert exception to dictionary for logging/API responses"""
        return {
            "error_code": self.error_code,
            "message": self.message,
            "category": self.category.value,
            "severity": self.severity.value,
            "timestamp": self.timestamp.isoformat(),
            "context": self.context,
            "recovery_suggestions": self.recovery_suggestions
        }
    
    def __str__(self) -> str:
        return f"[{self.error_code}] {self.message}"

class ConfigurationError(SupportAgentException):
    """Configuration-related errors"""
    
    def __init__(
        self,
        message: str,
        missing_config: str = None,
        config_value: Any = None,
        **kwargs
    ):
        context = kwargs.get('context', {})
        if missing_config:
            context['missing_config'] = missing_config
        if config_value is not None:
            context['config_value'] = str(config_value)
        
        recovery_suggestions = kwargs.get('recovery_suggestions', [
            "Check environment variables",
            "Verify configuration file",
            "Review config documentation"
        ])
        
        super().__init__(
            message,
            category=SupportErrorCategory.CONFIGURATION,
            context=context,
            recovery_suggestions=recovery_suggestions,
            **kwargs
        )

class AIModelError(SupportAgentException):
    """AI model loading and processing errors"""
    
    def __init__(
        self,
        message: str,
        model_name: str = None,
        model_operation: str = None,
        **kwargs
    ):
        context = kwargs.get('context', {})
        if model_name:
            context['model_name'] = model_name
        if model_operation:
            context['operation'] = model_operation
        
        recovery_suggestions = kwargs.get('recovery_suggestions', [
            "Check model availability",
            "Verify GPU/CPU resources", 
            "Try reloading the model",
            "Check model cache directory"
        ])
        
        super().__init__(
            message,
            category=SupportErrorCategory.AI_MODEL,
            context=context,
            recovery_suggestions=recovery_suggestions,
            **kwargs
        )

class DatabaseError(SupportAgentException):
    """Database connection and query errors"""
    
    def __init__(
        self,
        message: str,
        operation: str = None,
        table_name: str = None,
        query: str = None,
        **kwargs
    ):
        context = kwargs.get('context', {})
        if operation:
            context['operation'] = operation
        if table_name:
            context['table_name'] = table_name
        if query:
            context['query'] = query[:500]  # Truncate long queries
        
        recovery_suggestions = kwargs.get('recovery_suggestions', [
            "Check database connection",
            "Verify credentials",
            "Check database server status",
            "Review query syntax"
        ])
        
        super().__init__(
            message,
            category=SupportErrorCategory.DATABASE,
            context=context,
            recovery_suggestions=recovery_suggestions,
            **kwargs
        )

class KnowledgeBaseError(SupportAgentException):
    """Knowledge base and search errors"""
    
    def __init__(
        self,
        message: str,
        search_query: str = None,
        index_name: str = None,
        **kwargs
    ):
        context = kwargs.get('context', {})
        if search_query:
            context['search_query'] = search_query
        if index_name:
            context['index_name'] = index_name
        
        recovery_suggestions = kwargs.get('recovery_suggestions', [
            "Check search index integrity",
            "Verify embedding model",
            "Try rebuilding index",
            "Check search parameters"
        ])
        
        super().__init__(
            message,
            category=SupportErrorCategory.KNOWLEDGE_BASE,
            context=context,
            recovery_suggestions=recovery_suggestions,
            **kwargs
        )

class ConversationError(SupportAgentException):
    """Conversation handling and processing errors"""
    
    def __init__(
        self,
        message: str,
        conversation_id: str = None,
        user_id: str = None,
        turn_count: int = None,
        **kwargs
    ):
        context = kwargs.get('context', {})
        if conversation_id:
            context['conversation_id'] = conversation_id
        if user_id:
            context['user_id'] = user_id
        if turn_count:
            context['turn_count'] = turn_count
        
        recovery_suggestions = kwargs.get('recovery_suggestions', [
            "Check conversation state",
            "Verify user context",
            "Try resetting conversation",
            "Check message format"
        ])
        
        super().__init__(
            message,
            category=SupportErrorCategory.CONVERSATION,
            context=context,
            recovery_suggestions=recovery_suggestions,
            **kwargs
        )

class TicketManagementError(SupportAgentException):
    """Ticket creation, update, and management errors"""
    
    def __init__(
        self,
        message: str,
        ticket_id: str = None,
        operation: str = None,
        **kwargs
    ):
        context = kwargs.get('context', {})
        if ticket_id:
            context['ticket_id'] = ticket_id
        if operation:
            context['operation'] = operation
        
        recovery_suggestions = kwargs.get('recovery_suggestions', [
            "Check ticket data validity",
            "Verify ticket exists",
            "Check user permissions",
            "Review ticket status"
        ])
        
        super().__init__(
            message,
            category=SupportErrorCategory.TICKET_MANAGEMENT,
            context=context,
            recovery_suggestions=recovery_suggestions,
            **kwargs
        )

class EscalationError(SupportAgentException):
    """Escalation process and routing errors"""
    
    def __init__(
        self,
        message: str,
        escalation_reason: str = None,
        assigned_agent: str = None,
        **kwargs
    ):
        context = kwargs.get('context', {})
        if escalation_reason:
            context['escalation_reason'] = escalation_reason
        if assigned_agent:
            context['assigned_agent'] = assigned_agent
        
        recovery_suggestions = kwargs.get('recovery_suggestions', [
            "Check agent availability",
            "Verify escalation rules",
            "Review priority settings",
            "Check human agent queue"
        ])
        
        super().__init__(
            message,
            category=SupportErrorCategory.ESCALATION,
            context=context,
            recovery_suggestions=recovery_suggestions,
            **kwargs
        )

class PerformanceError(SupportAgentException):
    """Performance and resource-related errors"""
    
    def __init__(
        self,
        message: str,
        metric_name: str = None,
        current_value: Any = None,
        threshold: Any = None,
        **kwargs
    ):
        context = kwargs.get('context', {})
        if metric_name:
            context['metric_name'] = metric_name
        if current_value is not None:
            context['current_value'] = current_value
        if threshold is not None:
            context['threshold'] = threshold
        
        recovery_suggestions = kwargs.get('recovery_suggestions', [
            "Check system resources",
            "Review performance metrics",
            "Scale up if needed",
            "Optimize configuration"
        ])
        
        super().__init__(
            message,
            category=SupportErrorCategory.PERFORMANCE,
            severity=SupportErrorSeverity.HIGH,
            context=context,
            recovery_suggestions=recovery_suggestions,
            **kwargs
        )

class SecurityError(SupportAgentException):
    """Security and authentication errors"""
    
    def __init__(
        self,
        message: str,
        security_context: str = None,
        user_id: str = None,
        **kwargs
    ):
        context = kwargs.get('context', {})
        if security_context:
            context['security_context'] = security_context
        if user_id:
            context['user_id'] = user_id
        
        recovery_suggestions = kwargs.get('recovery_suggestions', [
            "Verify user permissions",
            "Check authentication status",
            "Review security policies",
            "Contact security team"
        ])
        
        super().__init__(
            message,
            category=SupportErrorCategory.SECURITY,
            severity=SupportErrorSeverity.CRITICAL,
            context=context,
            recovery_suggestions=recovery_suggestions,
            **kwargs
        )

class ValidationError(SupportAgentException):
    """Input validation and data format errors"""
    
    def __init__(
        self,
        message: str,
        field_name: str = None,
        field_value: Any = None,
        validation_rule: str = None,
        **kwargs
    ):
        context = kwargs.get('context', {})
        if field_name:
            context['field_name'] = field_name
        if field_value is not None:
            context['field_value'] = str(field_value)[:200]  # Truncate long values
        if validation_rule:
            context['validation_rule'] = validation_rule
        
        recovery_suggestions = kwargs.get('recovery_suggestions', [
            "Check input format",
            "Verify required fields",
            "Review validation rules",
            "Check data types"
        ])
        
        super().__init__(
            message,
            category=SupportErrorCategory.VALIDATION,
            severity=SupportErrorSeverity.LOW,
            context=context,
            recovery_suggestions=recovery_suggestions,
            **kwargs
        )

class ExternalServiceError(SupportAgentException):
    """External service integration errors"""
    
    def __init__(
        self,
        message: str,
        service_name: str = None,
        endpoint: str = None,
        status_code: int = None,
        **kwargs
    ):
        context = kwargs.get('context', {})
        if service_name:
            context['service_name'] = service_name
        if endpoint:
            context['endpoint'] = endpoint
        if status_code:
            context['status_code'] = status_code
        
        recovery_suggestions = kwargs.get('recovery_suggestions', [
            "Check service availability",
            "Verify API credentials",
            "Review endpoint URL",
            "Check network connectivity"
        ])
        
        super().__init__(
            message,
            category=SupportErrorCategory.EXTERNAL_SERVICE,
            context=context,
            recovery_suggestions=recovery_suggestions,
            **kwargs
        )

# Utility functions for error handling

def handle_exception(
    exception: Exception,
    context: Dict[str, Any] = None,
    logger = None
) -> SupportAgentException:
    """Convert generic exception to SupportAgentException"""
    
    if isinstance(exception, SupportAgentException):
        return exception
    
    # Map common exception types
    if isinstance(exception, ConnectionError):
        return DatabaseError(
            f"Database connection failed: {str(exception)}",
            context=context
        )
    
    elif isinstance(exception, ValueError):
        return ValidationError(
            f"Validation failed: {str(exception)}",
            context=context
        )
    
    elif isinstance(exception, PermissionError):
        return SecurityError(
            f"Permission denied: {str(exception)}",
            context=context
        )
    
    elif isinstance(exception, TimeoutError):
        return PerformanceError(
            f"Operation timed out: {str(exception)}",
            context=context
        )
    
    else:
        # Generic conversion
        return SupportAgentException(
            f"Unexpected error: {str(exception)}",
            context=context or {"original_exception": type(exception).__name__}
        )

def log_exception(
    exception: SupportAgentException,
    logger,
    include_context: bool = True,
    include_recovery: bool = True
):
    """Log exception with appropriate level and formatting"""
    
    log_data = {
        "error_code": exception.error_code,
        "message": exception.message,
        "category": exception.category.value,
        "severity": exception.severity.value
    }
    
    if include_context and exception.context:
        log_data["context"] = exception.context
    
    if include_recovery and exception.recovery_suggestions:
        log_data["recovery_suggestions"] = exception.recovery_suggestions
    
    # Log with appropriate level
    if exception.severity == SupportErrorSeverity.CRITICAL:
        logger.critical("Support Agent Critical Error", extra=log_data)
    elif exception.severity == SupportErrorSeverity.HIGH:
        logger.error("Support Agent Error", extra=log_data)
    elif exception.severity == SupportErrorSeverity.MEDIUM:
        logger.warning("Support Agent Warning", extra=log_data)
    else:
        logger.info("Support Agent Info", extra=log_data)

class ErrorRecoveryManager:
    """Manages error recovery and retry logic"""
    
    def __init__(self, max_retries: int = 3, backoff_factor: float = 1.5):
        self.max_retries = max_retries
        self.backoff_factor = backoff_factor
    
    async def execute_with_retry(
        self,
        operation,
        exception_types: List[type] = None,
        context: Dict[str, Any] = None
    ):
        """Execute operation with retry logic"""
        import asyncio
        
        exception_types = exception_types or [Exception]
        retry_count = 0
        last_exception = None
        
        while retry_count <= self.max_retries:
            try:
                return await operation()
            
            except tuple(exception_types) as e:
                last_exception = e
                retry_count += 1
                
                if retry_count <= self.max_retries:
                    delay = self.backoff_factor ** retry_count
                    await asyncio.sleep(delay)
                else:
                    # Convert to SupportAgentException for consistent handling
                    support_exception = handle_exception(e, context)
                    support_exception.context['retry_count'] = retry_count
                    raise support_exception
        
        # Should not reach here, but just in case
        raise handle_exception(last_exception, context)
