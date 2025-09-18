"""
🔒 GRAPHQL ERROR HANDLING TEMPLATE - ENTERPRISE ERROR MANAGEMENT
===============================================================

© 2025 Fahed Mlaiel <mlaiel@live.de>
TOUS DROITS RÉSERVÉS

Enterprise-grade GraphQL error handling template with:
- Structured error responses
- Error classification and codes
- Security-safe error messages
- Monitoring and logging integration

Author: Fahed Mlaiel (mlaiel@live.de)
Version: 1.0.0
"""

from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass
from enum import Enum
import logging
import traceback
from datetime import datetime

import strawberry
from strawberry.types import Info
from strawberry.extensions import Extension
from graphql import GraphQLError, GraphQLFormattedError
from pydantic import BaseModel, Field

from ..template_registry import TemplateInterface, TemplateMetadata, TemplateType, TemplateCategory, SecurityLevel

logger = logging.getLogger(__name__)


class ErrorSeverity(Enum):
    """Error severity levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ErrorCategory(Enum):
    """Error categories."""
    AUTHENTICATION = "authentication"
    AUTHORIZATION = "authorization"
    VALIDATION = "validation"
    NOT_FOUND = "not_found"
    BUSINESS_LOGIC = "business_logic"
    EXTERNAL_SERVICE = "external_service"
    INTERNAL = "internal"
    RATE_LIMIT = "rate_limit"


class GraphQLErrorHandlingConfig(BaseModel):
    """Configuration for GraphQL error handling generation."""
    
    error_handling_name: str = Field(..., description="Name of the error handling configuration")
    description: str = Field("", description="Error handling description")
    
    # Error configuration
    error_config: Dict[str, Any] = Field(
        default_factory=lambda: {
            "include_stack_trace": False,
            "include_internal_details": False,
            "mask_sensitive_errors": True,
            "enable_error_codes": True,
            "enable_error_tracking": True
        }
    )
    
    # Error codes mapping
    error_codes: Dict[str, Dict[str, Any]] = Field(
        default_factory=lambda: {
            "AUTHENTICATION_REQUIRED": {
                "code": "AUTH_001",
                "message": "Authentication required",
                "severity": "medium",
                "category": "authentication"
            },
            "INSUFFICIENT_PERMISSIONS": {
                "code": "AUTH_002", 
                "message": "Insufficient permissions",
                "severity": "medium",
                "category": "authorization"
            },
            "VALIDATION_ERROR": {
                "code": "VAL_001",
                "message": "Input validation failed",
                "severity": "low",
                "category": "validation"
            },
            "RESOURCE_NOT_FOUND": {
                "code": "RES_001",
                "message": "Resource not found",
                "severity": "low",
                "category": "not_found"
            },
            "RATE_LIMIT_EXCEEDED": {
                "code": "RL_001",
                "message": "Rate limit exceeded",
                "severity": "medium",
                "category": "rate_limit"
            },
            "INTERNAL_ERROR": {
                "code": "INT_001",
                "message": "Internal server error",
                "severity": "high",
                "category": "internal"
            }
        }
    )


class GraphQLErrorHandlingTemplate(TemplateInterface):
    """Enterprise GraphQL error handling template."""
    
    @property
    def metadata(self) -> TemplateMetadata:
        return TemplateMetadata(
            name="graphql_error_handling_template",
            template_type=TemplateType.GRAPHQL,
            category=TemplateCategory.INFRASTRUCTURE,
            version="1.0.0",
            author="Fahed Mlaiel",
            description="Enterprise GraphQL error handling template with structured responses",
            security_level=SecurityLevel.ENTERPRISE,
            dependencies=["strawberry-graphql", "pydantic"],
            tags=["graphql", "error-handling", "monitoring", "security"],
            enterprise_features=[
                "Structured error responses",
                "Error classification",
                "Security-safe messages",
                "Error tracking integration"
            ]
        )
    
    def generate(self, config: Dict[str, Any]) -> str:
        """Generate GraphQL error handling based on configuration."""
        try:
            error_config = GraphQLErrorHandlingConfig(**config)
            return self._generate_error_handling_code(error_config)
        except Exception as e:
            logger.error(f"Failed to generate GraphQL error handling: {e}")
            raise
    
    def validate_config(self, config: Dict[str, Any]) -> bool:
        """Validate error handling configuration."""
        try:
            GraphQLErrorHandlingConfig(**config)
            return True
        except Exception as e:
            logger.error(f"Invalid GraphQL error handling config: {e}")
            return False
    
    def get_schema(self) -> Dict[str, Any]:
        """Return JSON schema for configuration."""
        return GraphQLErrorHandlingConfig.schema()
    
    def get_examples(self) -> List[Dict[str, Any]]:
        """Return example configurations."""
        return [
            {
                "error_handling_name": "CreatorErrorHandling",
                "description": "Error handling for creator economy GraphQL API"
            }
        ]
    
    def _generate_error_handling_code(self, config: GraphQLErrorHandlingConfig) -> str:
        """Generate the actual GraphQL error handling code."""
        
        code = f'''"""
{config.error_handling_name} GraphQL Error Handling
Generated by Ainflue GraphQL Error Handling Template

{config.description}

🔒 PROTECTION INTELLECTUELLE:
© 2025 Fahed Mlaiel <mlaiel@live.de>
TOUS DROITS RÉSERVÉS
"""

from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass
from enum import Enum
import logging
import traceback
from datetime import datetime
import uuid

import strawberry
from strawberry.types import Info
from strawberry.extensions import Extension
from graphql import GraphQLError, GraphQLFormattedError

logger = logging.getLogger(__name__)

# Error Types and Classes

class ErrorSeverity(Enum):
    """Error severity levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high" 
    CRITICAL = "critical"

class ErrorCategory(Enum):
    """Error categories."""
    AUTHENTICATION = "authentication"
    AUTHORIZATION = "authorization"
    VALIDATION = "validation"
    NOT_FOUND = "not_found"
    BUSINESS_LOGIC = "business_logic"
    EXTERNAL_SERVICE = "external_service"
    INTERNAL = "internal"
    RATE_LIMIT = "rate_limit"

@strawberry.type
class ErrorDetail:
    """Detailed error information."""
    code: str
    message: str
    category: str
    severity: str
    timestamp: str
    request_id: Optional[str] = None
    field_path: Optional[List[str]] = None
    extensions: Optional[str] = None

class AinflueGraphQLError(GraphQLError):
    """Custom GraphQL error with enhanced information."""
    
    def __init__(
        self,
        message: str,
        error_code: str = "UNKNOWN_ERROR",
        category: ErrorCategory = ErrorCategory.INTERNAL,
        severity: ErrorSeverity = ErrorSeverity.MEDIUM,
        original_error: Optional[Exception] = None,
        field_path: Optional[List[str]] = None,
        extensions: Optional[Dict[str, Any]] = None
    ):
        self.error_code = error_code
        self.category = category
        self.severity = severity
        self.original_error = original_error
        self.field_path = field_path or []
        self.request_id = str(uuid.uuid4())
        self.timestamp = datetime.now().isoformat()
        
        # Prepare extensions
        error_extensions = {{
            "code": error_code,
            "category": category.value,
            "severity": severity.value,
            "timestamp": self.timestamp,
            "requestId": self.request_id
        }}
        
        if extensions:
            error_extensions.update(extensions)
        
        super().__init__(message, extensions=error_extensions)

# Specific Error Classes

class AuthenticationError(AinflueGraphQLError):
    """Authentication-related errors."""
    
    def __init__(self, message: str = "Authentication required", **kwargs):
        super().__init__(
            message=message,
            error_code="AUTH_001",
            category=ErrorCategory.AUTHENTICATION,
            severity=ErrorSeverity.MEDIUM,
            **kwargs
        )

class AuthorizationError(AinflueGraphQLError):
    """Authorization-related errors."""
    
    def __init__(self, message: str = "Insufficient permissions", **kwargs):
        super().__init__(
            message=message,
            error_code="AUTH_002",
            category=ErrorCategory.AUTHORIZATION,
            severity=ErrorSeverity.MEDIUM,
            **kwargs
        )

class ValidationError(AinflueGraphQLError):
    """Validation-related errors."""
    
    def __init__(self, message: str, field: Optional[str] = None, **kwargs):
        field_path = [field] if field else []
        super().__init__(
            message=message,
            error_code="VAL_001",
            category=ErrorCategory.VALIDATION,
            severity=ErrorSeverity.LOW,
            field_path=field_path,
            **kwargs
        )

class NotFoundError(AinflueGraphQLError):
    """Resource not found errors."""
    
    def __init__(self, resource: str, identifier: str = "", **kwargs):
        message = f"{{resource}} not found"
        if identifier:
            message += f": {{identifier}}"
        
        super().__init__(
            message=message,
            error_code="RES_001",
            category=ErrorCategory.NOT_FOUND,
            severity=ErrorSeverity.LOW,
            **kwargs
        )

class BusinessLogicError(AinflueGraphQLError):
    """Business logic errors."""
    
    def __init__(self, message: str, **kwargs):
        super().__init__(
            message=message,
            error_code="BIZ_001",
            category=ErrorCategory.BUSINESS_LOGIC,
            severity=ErrorSeverity.MEDIUM,
            **kwargs
        )

class RateLimitError(AinflueGraphQLError):
    """Rate limiting errors."""
    
    def __init__(self, message: str = "Rate limit exceeded", **kwargs):
        super().__init__(
            message=message,
            error_code="RL_001",
            category=ErrorCategory.RATE_LIMIT,
            severity=ErrorSeverity.MEDIUM,
            **kwargs
        )

class ExternalServiceError(AinflueGraphQLError):
    """External service errors."""
    
    def __init__(self, service: str, message: str = "External service error", **kwargs):
        super().__init__(
            message=f"{{service}}: {{message}}",
            error_code="EXT_001",
            category=ErrorCategory.EXTERNAL_SERVICE,
            severity=ErrorSeverity.HIGH,
            **kwargs
        )

class InternalError(AinflueGraphQLError):
    """Internal server errors."""
    
    def __init__(self, message: str = "Internal server error", **kwargs):
        # Mask internal error details in production
        safe_message = "Internal server error" if {config.error_config['mask_sensitive_errors']} else message
        
        super().__init__(
            message=safe_message,
            error_code="INT_001",
            category=ErrorCategory.INTERNAL,
            severity=ErrorSeverity.HIGH,
            **kwargs
        )

# Error Handling Extension

class ErrorHandlingExtension(Extension):
    """Extension for comprehensive error handling."""
    
    def __init__(self):
        self.error_config = {config.error_config}
        self.error_codes = {config.error_codes}
    
    async def on_request_start(self):
        """Initialize error handling for request."""
        # Set up error tracking context
        self.execution_context.context["request_id"] = str(uuid.uuid4())
        self.execution_context.context["error_tracking"] = []
    
    async def on_request_end(self):
        """Handle errors after request completion."""
        errors = self.execution_context.errors or []
        
        for error in errors:
            await self._handle_error(error)
    
    async def _handle_error(self, error: GraphQLError):
        """Handle individual GraphQL error."""
        # Log error based on severity
        if isinstance(error, AinflueGraphQLError):
            self._log_structured_error(error)
        else:
            self._log_generic_error(error)
        
        # Track error metrics
        if self.error_config.get("enable_error_tracking", True):
            await self._track_error_metrics(error)
    
    def _log_structured_error(self, error: AinflueGraphQLError):
        """Log structured error with full context."""
        log_data = {{
            "error_code": error.error_code,
            "category": error.category.value,
            "severity": error.severity.value,
            "message": str(error),
            "request_id": error.request_id,
            "timestamp": error.timestamp,
            "field_path": error.field_path
        }}
        
        if error.original_error and self.error_config.get("include_stack_trace", False):
            log_data["stack_trace"] = traceback.format_exception(
                type(error.original_error),
                error.original_error,
                error.original_error.__traceback__
            )
        
        # Log based on severity
        if error.severity in [ErrorSeverity.HIGH, ErrorSeverity.CRITICAL]:
            logger.error("GraphQL error occurred", extra=log_data)
        else:
            logger.warning("GraphQL error occurred", extra=log_data)
    
    def _log_generic_error(self, error: GraphQLError):
        """Log generic GraphQL error."""
        log_data = {{
            "error_type": type(error).__name__,
            "message": str(error),
            "timestamp": datetime.now().isoformat()
        }}
        
        logger.error("Unhandled GraphQL error", extra=log_data)
    
    async def _track_error_metrics(self, error: GraphQLError):
        """Track error metrics."""
        # Implementation for error metrics tracking
        pass

# Error Formatting

def format_error(error: GraphQLError, debug: bool = False) -> GraphQLFormattedError:
    """Format GraphQL errors for response."""
    
    formatted_error = {{
        "message": str(error),
        "locations": error.locations,
        "path": error.path
    }}
    
    # Add extensions if available
    if hasattr(error, 'extensions') and error.extensions:
        formatted_error["extensions"] = error.extensions
    
    # Add debug information if enabled
    if debug and hasattr(error, 'original_error'):
        formatted_error["extensions"] = formatted_error.get("extensions", {{}})
        formatted_error["extensions"]["debug"] = {{
            "original_error": str(error.original_error),
            "stack_trace": traceback.format_exception(
                type(error.original_error),
                error.original_error,
                error.original_error.__traceback__
            ) if error.original_error else None
        }}
    
    return formatted_error

# Error Utilities

def handle_database_error(error: Exception) -> AinflueGraphQLError:
    """Convert database errors to GraphQL errors."""
    error_message = str(error)
    
    if "not found" in error_message.lower():
        return NotFoundError("Resource", str(error))
    elif "constraint" in error_message.lower():
        return ValidationError("Data constraint violation")
    else:
        return InternalError("Database operation failed", original_error=error)

def handle_external_api_error(service: str, error: Exception) -> AinflueGraphQLError:
    """Convert external API errors to GraphQL errors."""
    return ExternalServiceError(service, str(error), original_error=error)

def require_authentication(info: Info) -> Any:
    """Require authentication and return user."""
    user = info.context.get("user")
    if not user:
        raise AuthenticationError()
    return user

def require_authorization(info: Info, required_roles: List[str]) -> Any:
    """Require authorization and return user."""
    user = require_authentication(info)
    user_roles = user.get("roles", [])
    
    if not any(role in user_roles for role in required_roles):
        raise AuthorizationError(f"Required roles: {{', '.join(required_roles)}}")
    
    return user

def validate_creator_access(info: Info, creator_id: str) -> Any:
    """Validate creator access permissions."""
    user = require_authentication(info)
    
    # Creator can access their own resources
    if str(user.get("id")) == str(creator_id):
        return user
    
    # Admin can access all resources
    if "admin" in user.get("roles", []):
        return user
    
    raise AuthorizationError("Cannot access this creator's resources")

# Configuration

ERROR_CONFIG = {config.dict()}

def create_error_handling_extensions() -> List[Extension]:
    """Create error handling extensions."""
    return [ErrorHandlingExtension()]

if __name__ == "__main__":
    print(f"✅ {config.error_handling_name} initialized successfully")
    print(f"📊 Error handling statistics:")
    print(f"   - Error codes: {len(config.error_codes)}")
    print(f"   - Stack trace: {config.error_config['include_stack_trace']}")
    print(f"   - Error tracking: {config.error_config['enable_error_tracking']}")
    print(f"   - Sensitive masking: {config.error_config['mask_sensitive_errors']}")
'''
        
        return code


# Register template
from .template_registry import register_template

register_template(
    GraphQLErrorHandlingTemplate,
    GraphQLErrorHandlingTemplate().metadata
)