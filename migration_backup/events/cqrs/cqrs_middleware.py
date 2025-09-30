"""🚀 Enterprise CQRS Middleware - CQRS Architecture
===================================================
Module: events/cqrs/cqrs_middleware.py
Author: Fahed Mlaiel (mlaiel@live.de)
===================================================

⚠️ PROPRIÉTÉ INTELLECTUELLE EXCLUSIVE - FAHED MLAIEL ⚠️
(c) 2025 Fahed Mlaiel. Tous droits réservés.
Contact: mlaiel@live.de

🎯 ENTERPRISE CQRS MIDDLEWARE
Advanced middleware pipeline for CQRS operations
- Authentication and authorization middleware
- Validation and sanitization middleware
- Performance monitoring and metrics collection
- Rate limiting and throttling middleware
- Audit logging and compliance middleware
- Error handling and recovery middleware
"""

import asyncio
import logging
import time
import uuid
import json
from typing import Dict, List, Optional, Any, Callable, Union, Type
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import weakref
from concurrent.futures import ThreadPoolExecutor
from collections import defaultdict, deque
import hashlib
import inspect

from .command_bus import Command, CommandResult, CommandStatus
from .query_bus import Query, QueryResult, QueryStatus
from ..core.base_event import BaseEvent
from ..core.event_priority import EventPriority
from ..core.exceptions import EventProcessingError, EventValidationError

logger = logging.getLogger(__name__)


class MiddlewareExecutionPhase(Enum):
    """Middleware execution phases"""
    PRE_VALIDATION = "pre_validation"
    POST_VALIDATION = "post_validation"
    PRE_EXECUTION = "pre_execution"
    POST_EXECUTION = "post_execution"
    ERROR_HANDLING = "error_handling"
    FINALLY = "finally"


class AuthenticationResult(Enum):
    """Authentication result states"""
    SUCCESS = "success"
    FAILED = "failed"
    EXPIRED = "expired"
    INVALID = "invalid"
    MISSING = "missing"


class AuthorizationResult(Enum):
    """Authorization result states"""
    ALLOWED = "allowed"
    DENIED = "denied"
    INSUFFICIENT_PERMISSIONS = "insufficient_permissions"
    RESOURCE_NOT_FOUND = "resource_not_found"


@dataclass
class MiddlewareContext:
    """Context passed through middleware pipeline"""
    operation_id: str
    operation_type: str  # "command" or "query"
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    correlation_id: Optional[str] = None
    start_time: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = field(default_factory=dict)
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    metrics: Dict[str, Any] = field(default_factory=dict)
    audit_data: Dict[str, Any] = field(default_factory=dict)


@dataclass
class AuthenticationContext:
    """Authentication context"""
    token: Optional[str] = None
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    expires_at: Optional[datetime] = None
    permissions: List[str] = field(default_factory=list)
    roles: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


class BaseMiddleware:
    """Base class for CQRS middleware"""
    
    def __init__(self, name: str, enabled: bool = True, priority: int = 0):
        self.name = name
        self.enabled = enabled
        self.priority = priority
    
    async def process_command(self, command: Command, context: MiddlewareContext, 
                            next_middleware: Callable) -> CommandResult:
        """Process command through middleware"""
        if not self.enabled:
            return await next_middleware(command, context)
        
        return await self._process_command_internal(command, context, next_middleware)
    
    async def process_query(self, query: Query, context: MiddlewareContext,
                          next_middleware: Callable) -> QueryResult:
        """Process query through middleware"""
        if not self.enabled:
            return await next_middleware(query, context)
        
        return await self._process_query_internal(query, context, next_middleware)
    
    async def _process_command_internal(self, command: Command, context: MiddlewareContext,
                                      next_middleware: Callable) -> CommandResult:
        """Internal command processing - override in subclasses"""
        return await next_middleware(command, context)
    
    async def _process_query_internal(self, query: Query, context: MiddlewareContext,
                                    next_middleware: Callable) -> QueryResult:
        """Internal query processing - override in subclasses"""
        return await next_middleware(query, context)


class AuthenticationMiddleware(BaseMiddleware):
    """Authentication middleware for CQRS operations"""
    
    def __init__(self, auth_service: Optional[Callable] = None, **kwargs):
        super().__init__("authentication", **kwargs)
        self._auth_service = auth_service
        self._token_cache: Dict[str, AuthenticationContext] = {}
        self._cache_ttl_seconds = 300  # 5 minutes
    
    async def _process_command_internal(self, command: Command, context: MiddlewareContext,
                                      next_middleware: Callable) -> CommandResult:
        """Authenticate command"""
        auth_result = await self._authenticate_request(command, context)
        
        if auth_result != AuthenticationResult.SUCCESS:
            return CommandResult(
                command_id=command.command_id,
                status=CommandStatus.FAILED,
                error=f"Authentication failed: {auth_result.value}"
            )
        
        return await next_middleware(command, context)
    
    async def _process_query_internal(self, query: Query, context: MiddlewareContext,
                                    next_middleware: Callable) -> QueryResult:
        """Authenticate query"""
        auth_result = await self._authenticate_request(query, context)
        
        if auth_result != AuthenticationResult.SUCCESS:
            return QueryResult(
                query_id=query.query_id,
                status=QueryStatus.FAILED,
                error=f"Authentication failed: {auth_result.value}"
            )
        
        return await next_middleware(query, context)
    
    async def _authenticate_request(self, request: Union[Command, Query], 
                                  context: MiddlewareContext) -> AuthenticationResult:
        """Authenticate request"""
        # Extract token from request metadata
        token = request.metadata.get("auth_token") or context.metadata.get("auth_token")
        
        if not token:
            return AuthenticationResult.MISSING
        
        # Check cache first
        if token in self._token_cache:
            auth_context = self._token_cache[token]
            if auth_context.expires_at and auth_context.expires_at > datetime.utcnow():
                context.user_id = auth_context.user_id
                context.session_id = auth_context.session_id
                context.metadata["permissions"] = auth_context.permissions
                context.metadata["roles"] = auth_context.roles
                return AuthenticationResult.SUCCESS
            else:
                # Token expired, remove from cache
                del self._token_cache[token]
                return AuthenticationResult.EXPIRED
        
        # Authenticate with auth service
        if self._auth_service:
            try:
                auth_context = await self._auth_service(token)
                if auth_context:
                    # Cache the result
                    self._token_cache[token] = auth_context
                    
                    # Update context
                    context.user_id = auth_context.user_id
                    context.session_id = auth_context.session_id
                    context.metadata["permissions"] = auth_context.permissions
                    context.metadata["roles"] = auth_context.roles
                    
                    return AuthenticationResult.SUCCESS
                else:
                    return AuthenticationResult.INVALID
            except Exception as e:
                logger.error(f"Authentication service error: {e}")
                return AuthenticationResult.FAILED
        
        # Default to success if no auth service configured
        return AuthenticationResult.SUCCESS


class AuthorizationMiddleware(BaseMiddleware):
    """Authorization middleware for CQRS operations"""
    
    def __init__(self, **kwargs):
        super().__init__("authorization", **kwargs)
        self._permissions_cache: Dict[str, List[str]] = {}
        self._resource_permissions: Dict[str, List[str]] = {}
    
    def register_resource_permissions(self, resource_type: str, required_permissions: List[str]) -> None:
        """Register required permissions for resource type"""
        self._resource_permissions[resource_type] = required_permissions
    
    async def _process_command_internal(self, command: Command, context: MiddlewareContext,
                                      next_middleware: Callable) -> CommandResult:
        """Authorize command"""
        auth_result = await self._authorize_request(command, context)
        
        if auth_result != AuthorizationResult.ALLOWED:
            return CommandResult(
                command_id=command.command_id,
                status=CommandStatus.FAILED,
                error=f"Authorization failed: {auth_result.value}"
            )
        
        return await next_middleware(command, context)
    
    async def _process_query_internal(self, query: Query, context: MiddlewareContext,
                                    next_middleware: Callable) -> QueryResult:
        """Authorize query"""
        auth_result = await self._authorize_request(query, context)
        
        if auth_result != AuthorizationResult.ALLOWED:
            return QueryResult(
                query_id=query.query_id,
                status=QueryStatus.FAILED,
                error=f"Authorization failed: {auth_result.value}"
            )
        
        return await next_middleware(query, context)
    
    async def _authorize_request(self, request: Union[Command, Query], 
                               context: MiddlewareContext) -> AuthorizationResult:
        """Authorize request"""
        if not context.user_id:
            return AuthorizationResult.DENIED
        
        # Get user permissions from context
        user_permissions = context.metadata.get("permissions", [])
        user_roles = context.metadata.get("roles", [])
        
        # Determine required permissions for this operation
        operation_type = getattr(request, "command_type", getattr(request, "query_type", ""))
        required_permissions = self._resource_permissions.get(operation_type, [])
        
        # Check if user has required permissions
        if required_permissions:
            for permission in required_permissions:
                if permission not in user_permissions:
                    # Check if user has a role that grants this permission
                    if not self._check_role_permission(user_roles, permission):
                        return AuthorizationResult.INSUFFICIENT_PERMISSIONS
        
        # Additional business logic authorization can be added here
        return AuthorizationResult.ALLOWED
    
    def _check_role_permission(self, user_roles: List[str], permission: str) -> bool:
        """Check if user roles grant the required permission"""
        # Simplified role-based access control
        role_permissions = {
            "admin": ["*"],  # Admin has all permissions
            "user": ["read", "write_own"],
            "readonly": ["read"]
        }
        
        for role in user_roles:
            role_perms = role_permissions.get(role, [])
            if "*" in role_perms or permission in role_perms:
                return True
        
        return False


class ValidationMiddleware(BaseMiddleware):
    """Validation middleware for CQRS operations"""
    
    def __init__(self, **kwargs):
        super().__init__("validation", **kwargs)
        self._validators: Dict[str, List[Callable]] = defaultdict(list)
    
    def register_validator(self, operation_type: str, validator: Callable) -> None:
        """Register validator for operation type"""
        self._validators[operation_type].append(validator)
    
    async def _process_command_internal(self, command: Command, context: MiddlewareContext,
                                      next_middleware: Callable) -> CommandResult:
        """Validate command"""
        validation_errors = await self._validate_request(command, context)
        
        if validation_errors:
            return CommandResult(
                command_id=command.command_id,
                status=CommandStatus.FAILED,
                error=f"Validation failed: {'; '.join(validation_errors)}"
            )
        
        return await next_middleware(command, context)
    
    async def _process_query_internal(self, query: Query, context: MiddlewareContext,
                                    next_middleware: Callable) -> QueryResult:
        """Validate query"""
        validation_errors = await self._validate_request(query, context)
        
        if validation_errors:
            return QueryResult(
                query_id=query.query_id,
                status=QueryStatus.FAILED,
                error=f"Validation failed: {'; '.join(validation_errors)}"
            )
        
        return await next_middleware(query, context)
    
    async def _validate_request(self, request: Union[Command, Query], 
                              context: MiddlewareContext) -> List[str]:
        """Validate request"""
        errors = []
        
        # Get operation type
        operation_type = getattr(request, "command_type", getattr(request, "query_type", ""))
        
        # Run registered validators
        validators = self._validators.get(operation_type, [])
        
        for validator in validators:
            try:
                if asyncio.iscoroutinefunction(validator):
                    result = await validator(request, context)
                else:
                    result = validator(request, context)
                
                if isinstance(result, list):
                    errors.extend(result)
                elif isinstance(result, str) and result:
                    errors.append(result)
                elif result is False:
                    errors.append(f"Validation failed for {operation_type}")
                    
            except Exception as e:
                logger.error(f"Validator error for {operation_type}: {e}")
                errors.append(f"Validation error: {str(e)}")
        
        return errors


class MetricsMiddleware(BaseMiddleware):
    """Metrics collection middleware for CQRS operations"""
    
    def __init__(self, **kwargs):
        super().__init__("metrics", **kwargs)
        self._metrics: Dict[str, Dict[str, Any]] = defaultdict(lambda: {
            "count": 0,
            "success_count": 0,
            "error_count": 0,
            "total_duration_ms": 0.0,
            "avg_duration_ms": 0.0,
            "min_duration_ms": float('inf'),
            "max_duration_ms": 0.0
        })
        self._request_history: deque = deque(maxlen=10000)
    
    async def _process_command_internal(self, command: Command, context: MiddlewareContext,
                                      next_middleware: Callable) -> CommandResult:
        """Collect command metrics"""
        start_time = time.time()
        
        try:
            result = await next_middleware(command, context)
            
            # Record metrics
            duration_ms = (time.time() - start_time) * 1000
            success = result.status == CommandStatus.COMPLETED
            
            await self._record_metrics("command", command.command_type, duration_ms, success)
            
            return result
            
        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            await self._record_metrics("command", command.command_type, duration_ms, False)
            raise
    
    async def _process_query_internal(self, query: Query, context: MiddlewareContext,
                                    next_middleware: Callable) -> QueryResult:
        """Collect query metrics"""
        start_time = time.time()
        
        try:
            result = await next_middleware(query, context)
            
            # Record metrics
            duration_ms = (time.time() - start_time) * 1000
            success = result.status in [QueryStatus.COMPLETED, QueryStatus.CACHED]
            
            await self._record_metrics("query", query.query_type, duration_ms, success)
            
            return result
            
        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            await self._record_metrics("query", query.query_type, duration_ms, False)
            raise
    
    async def _record_metrics(self, operation_type: str, operation_name: str, 
                            duration_ms: float, success: bool) -> None:
        """Record operation metrics"""
        key = f"{operation_type}.{operation_name}"
        metrics = self._metrics[key]
        
        metrics["count"] += 1
        metrics["total_duration_ms"] += duration_ms
        
        if success:
            metrics["success_count"] += 1
        else:
            metrics["error_count"] += 1
        
        # Update duration statistics
        metrics["avg_duration_ms"] = metrics["total_duration_ms"] / metrics["count"]
        metrics["min_duration_ms"] = min(metrics["min_duration_ms"], duration_ms)
        metrics["max_duration_ms"] = max(metrics["max_duration_ms"], duration_ms)
        
        # Add to history
        self._request_history.append({
            "operation_type": operation_type,
            "operation_name": operation_name,
            "duration_ms": duration_ms,
            "success": success,
            "timestamp": datetime.utcnow()
        })
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get collected metrics"""
        return dict(self._metrics)
    
    def get_request_history(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get request history"""
        return list(self._request_history)[-limit:]


class RateLimitingMiddleware(BaseMiddleware):
    """Rate limiting middleware for CQRS operations"""
    
    def __init__(self, default_limit: int = 100, window_seconds: int = 60, **kwargs):
        super().__init__("rate_limiting", **kwargs)
        self._default_limit = default_limit
        self._window_seconds = window_seconds
        self._request_counts: Dict[str, deque] = defaultdict(lambda: deque())
        self._custom_limits: Dict[str, int] = {}
    
    def set_custom_limit(self, operation_type: str, limit: int) -> None:
        """Set custom rate limit for operation type"""
        self._custom_limits[operation_type] = limit
    
    async def _process_command_internal(self, command: Command, context: MiddlewareContext,
                                      next_middleware: Callable) -> CommandResult:
        """Apply rate limiting to command"""
        if not await self._check_rate_limit(command.command_type, context):
            return CommandResult(
                command_id=command.command_id,
                status=CommandStatus.FAILED,
                error="Rate limit exceeded"
            )
        
        return await next_middleware(command, context)
    
    async def _process_query_internal(self, query: Query, context: MiddlewareContext,
                                    next_middleware: Callable) -> QueryResult:
        """Apply rate limiting to query"""
        if not await self._check_rate_limit(query.query_type, context):
            return QueryResult(
                query_id=query.query_id,
                status=QueryStatus.FAILED,
                error="Rate limit exceeded"
            )
        
        return await next_middleware(query, context)
    
    async def _check_rate_limit(self, operation_type: str, context: MiddlewareContext) -> bool:
        """Check if request is within rate limit"""
        # Use user_id for rate limiting, fallback to session_id or operation_type
        rate_limit_key = context.user_id or context.session_id or operation_type
        key = f"{rate_limit_key}:{operation_type}"
        
        now = datetime.utcnow()
        window_start = now - timedelta(seconds=self._window_seconds)
        
        # Clean old requests
        request_times = self._request_counts[key]
        while request_times and request_times[0] < window_start:
            request_times.popleft()
        
        # Check limit
        limit = self._custom_limits.get(operation_type, self._default_limit)
        
        if len(request_times) >= limit:
            return False
        
        # Record this request
        request_times.append(now)
        return True


class AuditLoggingMiddleware(BaseMiddleware):
    """Audit logging middleware for CQRS operations"""
    
    def __init__(self, audit_logger: Optional[logging.Logger] = None, **kwargs):
        super().__init__("audit_logging", **kwargs)
        self._audit_logger = audit_logger or logging.getLogger(f"{__name__}.audit")
        self._audit_history: deque = deque(maxlen=10000)
    
    async def _process_command_internal(self, command: Command, context: MiddlewareContext,
                                      next_middleware: Callable) -> CommandResult:
        """Audit command execution"""
        audit_entry = await self._create_audit_entry("command", command, context)
        
        try:
            result = await next_middleware(command, context)
            
            # Update audit entry with result
            audit_entry["result_status"] = result.status.value
            audit_entry["success"] = result.status == CommandStatus.COMPLETED
            audit_entry["error"] = result.error
            
            await self._log_audit_entry(audit_entry)
            
            return result
            
        except Exception as e:
            audit_entry["result_status"] = "exception"
            audit_entry["success"] = False
            audit_entry["error"] = str(e)
            
            await self._log_audit_entry(audit_entry)
            raise
    
    async def _process_query_internal(self, query: Query, context: MiddlewareContext,
                                    next_middleware: Callable) -> QueryResult:
        """Audit query execution"""
        audit_entry = await self._create_audit_entry("query", query, context)
        
        try:
            result = await next_middleware(query, context)
            
            # Update audit entry with result
            audit_entry["result_status"] = result.status.value
            audit_entry["success"] = result.status in [QueryStatus.COMPLETED, QueryStatus.CACHED]
            audit_entry["error"] = result.error
            audit_entry["cache_hit"] = result.cache_hit
            
            await self._log_audit_entry(audit_entry)
            
            return result
            
        except Exception as e:
            audit_entry["result_status"] = "exception"
            audit_entry["success"] = False
            audit_entry["error"] = str(e)
            
            await self._log_audit_entry(audit_entry)
            raise
    
    async def _create_audit_entry(self, operation_type: str, 
                                request: Union[Command, Query], 
                                context: MiddlewareContext) -> Dict[str, Any]:
        """Create audit log entry"""
        return {
            "operation_id": context.operation_id,
            "operation_type": operation_type,
            "operation_name": getattr(request, f"{operation_type}_type", ""),
            "user_id": context.user_id,
            "session_id": context.session_id,
            "correlation_id": context.correlation_id,
            "timestamp": datetime.utcnow().isoformat(),
            "request_data": self._sanitize_data(getattr(request, "data", {})),
            "metadata": request.metadata,
            "ip_address": context.metadata.get("ip_address"),
            "user_agent": context.metadata.get("user_agent")
        }
    
    async def _log_audit_entry(self, audit_entry: Dict[str, Any]) -> None:
        """Log audit entry"""
        self._audit_logger.info("CQRS Operation", extra=audit_entry)
        self._audit_history.append(audit_entry)
    
    def _sanitize_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Sanitize sensitive data from audit logs"""
        sensitive_fields = ["password", "token", "secret", "key", "credential"]
        sanitized = {}
        
        for key, value in data.items():
            if any(sensitive in key.lower() for sensitive in sensitive_fields):
                sanitized[key] = "***REDACTED***"
            else:
                sanitized[key] = value
        
        return sanitized
    
    def get_audit_history(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get audit history"""
        return list(self._audit_history)[-limit:]


class ErrorHandlingMiddleware(BaseMiddleware):
    """Error handling middleware for CQRS operations"""
    
    def __init__(self, **kwargs):
        super().__init__("error_handling", **kwargs)
        self._error_handlers: Dict[Type[Exception], Callable] = {}
        self._error_stats: Dict[str, int] = defaultdict(int)
    
    def register_error_handler(self, exception_type: Type[Exception], handler: Callable) -> None:
        """Register custom error handler"""
        self._error_handlers[exception_type] = handler
    
    async def _process_command_internal(self, command: Command, context: MiddlewareContext,
                                      next_middleware: Callable) -> CommandResult:
        """Handle command errors"""
        try:
            return await next_middleware(command, context)
        except Exception as e:
            return await self._handle_error(e, command.command_id, "command", context)
    
    async def _process_query_internal(self, query: Query, context: MiddlewareContext,
                                    next_middleware: Callable) -> QueryResult:
        """Handle query errors"""
        try:
            return await next_middleware(query, context)
        except Exception as e:
            return await self._handle_error(e, query.query_id, "query", context)
    
    async def _handle_error(self, error: Exception, operation_id: str, 
                          operation_type: str, context: MiddlewareContext) -> Union[CommandResult, QueryResult]:
        """Handle error with custom handlers"""
        error_type = type(error).__name__
        self._error_stats[error_type] += 1
        
        # Try custom error handlers
        for exception_type, handler in self._error_handlers.items():
            if isinstance(error, exception_type):
                try:
                    result = await handler(error, operation_id, operation_type, context)
                    if result:
                        return result
                except Exception as handler_error:
                    logger.error(f"Error handler failed: {handler_error}")
        
        # Default error handling
        error_message = str(error)
        
        if operation_type == "command":
            return CommandResult(
                command_id=operation_id,
                status=CommandStatus.FAILED,
                error=error_message
            )
        else:
            return QueryResult(
                query_id=operation_id,
                status=QueryStatus.FAILED,
                error=error_message
            )
    
    def get_error_statistics(self) -> Dict[str, int]:
        """Get error statistics"""
        return dict(self._error_stats)


class CQRSMiddlewarePipeline:
    """CQRS middleware pipeline manager"""
    
    def __init__(self):
        self._middleware: List[BaseMiddleware] = []
        self._enabled = True
    
    def add_middleware(self, middleware: BaseMiddleware) -> None:
        """Add middleware to pipeline"""
        self._middleware.append(middleware)
        self._middleware.sort(key=lambda m: m.priority, reverse=True)
    
    def remove_middleware(self, name: str) -> bool:
        """Remove middleware by name"""
        for i, middleware in enumerate(self._middleware):
            if middleware.name == name:
                del self._middleware[i]
                return True
        return False
    
    def enable_middleware(self, name: str) -> bool:
        """Enable middleware by name"""
        for middleware in self._middleware:
            if middleware.name == name:
                middleware.enabled = True
                return True
        return False
    
    def disable_middleware(self, name: str) -> bool:
        """Disable middleware by name"""
        for middleware in self._middleware:
            if middleware.name == name:
                middleware.enabled = False
                return True
        return False
    
    async def process_command(self, command: Command) -> CommandResult:
        """Process command through middleware pipeline"""
        if not self._enabled:
            raise EventProcessingError("Middleware pipeline is disabled")
        
        context = MiddlewareContext(
            operation_id=str(uuid.uuid4()),
            operation_type="command",
            correlation_id=command.correlation_id
        )
        
        # Create middleware chain
        async def execute_middleware_chain(cmd: Command, ctx: MiddlewareContext, 
                                         middleware_index: int = 0) -> CommandResult:
            if middleware_index >= len(self._middleware):
                # End of pipeline - this should not happen in normal execution
                return CommandResult(
                    command_id=cmd.command_id,
                    status=CommandStatus.FAILED,
                    error="No command handler in pipeline"
                )
            
            current_middleware = self._middleware[middleware_index]
            
            async def next_middleware(c: Command, ctx: MiddlewareContext) -> CommandResult:
                return await execute_middleware_chain(c, ctx, middleware_index + 1)
            
            return await current_middleware.process_command(cmd, ctx, next_middleware)
        
        return await execute_middleware_chain(command, context)
    
    async def process_query(self, query: Query) -> QueryResult:
        """Process query through middleware pipeline"""
        if not self._enabled:
            raise EventProcessingError("Middleware pipeline is disabled")
        
        context = MiddlewareContext(
            operation_id=str(uuid.uuid4()),
            operation_type="query",
            correlation_id=query.correlation_id
        )
        
        # Create middleware chain
        async def execute_middleware_chain(q: Query, ctx: MiddlewareContext, 
                                         middleware_index: int = 0) -> QueryResult:
            if middleware_index >= len(self._middleware):
                # End of pipeline - this should not happen in normal execution
                return QueryResult(
                    query_id=q.query_id,
                    status=QueryStatus.FAILED,
                    error="No query handler in pipeline"
                )
            
            current_middleware = self._middleware[middleware_index]
            
            async def next_middleware(q: Query, ctx: MiddlewareContext) -> QueryResult:
                return await execute_middleware_chain(q, ctx, middleware_index + 1)
            
            return await current_middleware.process_query(q, ctx, next_middleware)
        
        return await execute_middleware_chain(query, context)
    
    def get_middleware_status(self) -> List[Dict[str, Any]]:
        """Get status of all middleware"""
        return [
            {
                "name": middleware.name,
                "enabled": middleware.enabled,
                "priority": middleware.priority,
                "type": type(middleware).__name__
            }
            for middleware in self._middleware
        ]
    
    def enable_pipeline(self) -> None:
        """Enable middleware pipeline"""
        self._enabled = True
    
    def disable_pipeline(self) -> None:
        """Disable middleware pipeline"""
        self._enabled = False


# Default pipeline instance
_default_pipeline: Optional[CQRSMiddlewarePipeline] = None


def get_default_middleware_pipeline() -> CQRSMiddlewarePipeline:
    """Get default middleware pipeline instance"""
    global _default_pipeline
    if _default_pipeline is None:
        _default_pipeline = CQRSMiddlewarePipeline()
        
        # Add default middleware
        _default_pipeline.add_middleware(ErrorHandlingMiddleware(priority=1000))
        _default_pipeline.add_middleware(MetricsMiddleware(priority=900))
        _default_pipeline.add_middleware(AuditLoggingMiddleware(priority=800))
        _default_pipeline.add_middleware(RateLimitingMiddleware(priority=700))
        _default_pipeline.add_middleware(AuthenticationMiddleware(priority=600))
        _default_pipeline.add_middleware(AuthorizationMiddleware(priority=500))
        _default_pipeline.add_middleware(ValidationMiddleware(priority=400))
    
    return _default_pipeline


def reset_default_middleware_pipeline() -> None:
    """Reset default middleware pipeline (for testing)"""
    global _default_pipeline
    _default_pipeline = None