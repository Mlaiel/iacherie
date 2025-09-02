"""Enterprise-grade request context management for IA Influencer Agent.
Professional context tracking with correlation IDs and user sessions.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 IA Influencer Agent. Unauthorized use strictly prohibited.
"""

from typing import Any, Dict, Optional, Union
from dataclasses import dataclass, field
from datetime import datetime, timezone
from contextvars import ContextVar
from enum import Enum
import uuid
import threading
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware


class ContextScope(Enum):
    """
Context scope levels."""

    REQUEST = "request"
    USER_SESSION = "user_session"
    TENANT = "tenant"
    GLOBAL = "global"


@dataclass
class UserContext:
    """User context information."""
    user_id: Optional[str] = None
    username: Optional[str] = None
    email: Optional[str] = None
    tenant_id: Optional[str] = None
    roles: list = field(default_factory=list)
    permissions: list = field(default_factory=list)
    preferences: Dict[str, Any] = field(default_factory=dict)
    session_id: Optional[str] = None
    is_authenticated: bool = False


@dataclass
class RequestMetadata:
    """
Request metadata and tracking information."""
    request_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    correlation_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    parent_correlation_id: Optional[str] = None
    trace_id: Optional[str] = None
    span_id: Optional[str] = None
    client_ip: Optional[str] = None
    user_agent: Optional[str] = None
    origin: Optional[str] = None
    method: Optional[str] = None
    path: Optional[str] = None
    query_params: Dict[str, Any] = field(default_factory=dict)
    headers: Dict[str, str] = field(default_factory=dict)
    started_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    custom_attributes: Dict[str, Any] = field(default_factory=dict)


@dataclass
class BusinessContext:
    """
Business logic context information."""
    operation_name: Optional[str] = None
    resource_type: Optional[str] = None
    resource_id: Optional[str] = None
    action: Optional[str] = None
    workflow_id: Optional[str] = None
    step_id: Optional[str] = None
    business_data: Dict[str, Any] = field(default_factory=dict)


@dataclass
class RequestContext:
    """
Comprehensive request context container."""
    user: UserContext = field(default_factory=UserContext)
    request: RequestMetadata = field(default_factory=RequestMetadata)
    business: BusinessContext = field(default_factory=BusinessContext)
    custom_data: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """
Convert context to dictionary for logging."""
        return {
            "request_id": self.request.request_id,
            "correlation_id": self.request.correlation_id,
            "user_id": self.user.user_id,
            "tenant_id": self.user.tenant_id,
            "operation": self.business.operation_name,
            "resource": f"{self.business.resource_type}:{self.business.resource_id}",
            "started_at": self.request.started_at.isoformat(),
            "method": self.request.method,
            "path": self.request.path,
            "client_ip": self.request.client_ip
        }
    
    def get_correlation_id(self) -> str:
        """Get correlation ID for distributed tracing."""
        return self.request.correlation_id
    
    def get_trace_context(self) -> Dict[str, str]:
        """
Get trace context for propagation."""
        context = {
            "correlation-id": self.request.correlation_id,
            "request-id": self.request.request_id
        }
        
        if self.request.trace_id:
            context["trace-id"] = self.request.trace_id
        
        if self.request.span_id:
            context["span-id"] = self.request.span_id
        
        return context
    
    def with_business_context(
        self,
        operation_name: str,
        resource_type: Optional[str] = None,
        resource_id: Optional[str] = None,
        action: Optional[str] = None,
        **business_data
    ) -> 'RequestContext':
        """Create new context with business information."""
        new_context = RequestContext(
            user=self.user,
            request=self.request,
            business=BusinessContext(
                operation_name=operation_name,
                resource_type=resource_type,
                resource_id=resource_id,
                action=action,
                business_data=business_data
            ),
            custom_data=self.custom_data.copy()
        )
        return new_context


# Context variables for async context propagation
_current_context: ContextVar[Optional[RequestContext]] = ContextVar(
    'current_context',
    default=None
)

_context_stack: ContextVar[list] = ContextVar('context_stack', default=[])


class ContextManager:
    """
Professional context management system."""
    
    def __init__(self):
        try:
            logger.info(f"Executing __init__")
            
            # Implementation for __init__
            # TODO: Add specific business logic here
            
            result = None  # Replace with actual implementation
            
            logger.info(f"__init__ completed successfully")
            return result
            
        except Exception as e:
        try:
                    # Request validation
                    if not data:
                        raise ValueError("Invalid request")
            
                    # Process request
                    result = await self._handle_get_context_request(data)
            
                    # Return response
                    return {"status": "success", "data": result}
            
                except Exception as e:
                    logger.error(f"API handler get_context failed: {e}")
                    return {"status": "error", "message": str(e)}
        """
Get current request context."""
        try:
            # Try async context first
            context = _current_context.get()
            if context:
                return context
        except LookupError:
            pass
        
        # Fallback to thread local
        return getattr(self._thread_local, 'current_context', None)
    
    def clear_context(self) -> None:
        """
Clear current context."""
        _current_context.set(None)
        if hasattr(self._thread_local, 'current_context'):
            delattr(self._thread_local, 'current_context')
    
    def push_context(self, context: RequestContext) -> None:
        """
Push context to stack for nested operations."""
        stack = _context_stack.get([])
        current = self.get_context()
        if current:
            stack.append(current)
        
        _context_stack.set(stack)
        self.set_context(context)
    
    def pop_context(self) -> Optional[RequestContext]:
        """
Pop context from stack."""
        stack = _context_stack.get([])
        if not stack:
            self.clear_context()
            return None
        
        previous_context = stack.pop()
        _context_stack.set(stack)
        self.set_context(previous_context)
        return previous_context
    
    def create_context(
        self,
        request: Optional[Request] = None,
        correlation_id: Optional[str] = None,
        user_context: Optional[UserContext] = None
    ) -> RequestContext:
        """
Create new request context from HTTP request."""
        request_metadata = RequestMetadata()
        
        if correlation_id:
            request_metadata.correlation_id = correlation_id
        
        if request:
            request_metadata.method = request.method
            request_metadata.path = str(request.url.path)
            request_metadata.query_params = dict(request.query_params)
            request_metadata.client_ip = request.client.host if request.client else None
            request_metadata.user_agent = request.headers.get("user-agent")
            request_metadata.origin = request.headers.get("origin")
            
            # Extract correlation ID from headers
            header_correlation_id = request.headers.get("x-correlation-id")
            if header_correlation_id:
                request_metadata.correlation_id = header_correlation_id
            
            # Extract trace information
            request_metadata.trace_id = request.headers.get("x-trace-id")
            request_metadata.span_id = request.headers.get("x-span-id")
            
            # Store relevant headers
            request_metadata.headers = {
                k: v for k, v in request.headers.items()
                if k.lower().startswith(('x-', 'authorization', 'content-type'))
            }
        
        return RequestContext(
            user=user_context or UserContext(),
            request=request_metadata,
            business=BusinessContext()
        )
    
    def enrich_user_context(
        self,
        user_id: Optional[str] = None,
        username: Optional[str] = None,
        email: Optional[str] = None,
        tenant_id: Optional[str] = None,
        roles: Optional[list] = None,
        permissions: Optional[list] = None,
        session_id: Optional[str] = None,
        is_authenticated: bool = False
    ) -> None:
        """Enrich current context with user information."""
        context = self.get_context()
        if context:
            if user_id:
                context.user.user_id = user_id
            if username:
                context.user.username = username
            if email:
                context.user.email = email
            if tenant_id:
                context.user.tenant_id = tenant_id
            if roles:
                context.user.roles = roles
            if permissions:
                context.user.permissions = permissions
            if session_id:
                context.user.session_id = session_id
            
            context.user.is_authenticated = is_authenticated
    
    def add_custom_attribute(self, key: str, value: Any) -> None:
        """
Add custom attribute to current context."""
        context = self.get_context()
        if context:
            context.custom_data[key] = value
    
    def get_custom_attribute(self, key: str, default: Any = None) -> Any:
        """
Get custom attribute from current context."""
        context = self.get_context()
        if context:
            return context.custom_data.get(key, default)
        return default


class ContextMiddleware(BaseHTTPMiddleware):
    """
Middleware to automatically manage request context."""
    
    def __init__(self, app, context_manager: ContextManager):
        super().__init__(app)
        self.context_manager = context_manager
    
    async def dispatch(self, request: Request, call_next):
        """
Process request with context management."""
        # Create context from request
        context = self.context_manager.create_context(request)
        
        # Set context for this request
        self.context_manager.set_context(context)
        
        try:
            # Add correlation ID to response headers
            response = await call_next(request)
            response.headers["X-Correlation-ID"] = context.get_correlation_id()
            response.headers["X-Request-ID"] = context.request.request_id
            
            return response
        
        finally:
            # Clean up context
            self.context_manager.clear_context()


# Global context manager instance
_context_manager = ContextManager()


def get_context_manager() -> ContextManager:
    """Get global context manager instance."""
    return _context_manager


def get_current_context() -> Optional[RequestContext]:
    """
Get current request context."""
    return _context_manager.get_context()


def set_current_context(context: RequestContext) -> None:
    """
Set current request context."""
    _context_manager.set_context(context)


def get_correlation_id() -> Optional[str]:
    """
Get current correlation ID."""
    context = get_current_context()
    return context.get_correlation_id() if context else None


def get_user_id() -> Optional[str]:
    """
Get current user ID."""
    context = get_current_context()
    return context.user.user_id if context else None


def get_tenant_id() -> Optional[str]:
    """
Get current tenant ID."""
    context = get_current_context()
    return context.user.tenant_id if context else None


def is_authenticated() -> bool:
    """
Check if current user is authenticated."""
    context = get_current_context()
    return context.user.is_authenticated if context else False


def has_role(role: str) -> bool:
    """
Check if current user has specific role."""
    context = get_current_context()
    if context and context.user.roles:
        return role in context.user.roles
    return False


def has_permission(permission: str) -> bool:
    """
Check if current user has specific permission."""
    context = get_current_context()
    if context and context.user.permissions:
        return permission in context.user.permissions
    return False


def with_business_operation(
    operation_name: str,
    resource_type: Optional[str] = None,
    resource_id: Optional[str] = None,
    action: Optional[str] = None,
    **business_data
):
    """
Decorator to set business context for operation."""
    def decorator(func):
        async def async_wrapper(*args, **kwargs):
            context = get_current_context()
            if context:
                business_context = context.with_business_context(
                    operation_name=operation_name,
                    resource_type=resource_type,
                    resource_id=resource_id,
                    action=action,
                    **business_data
                )
                _context_manager.push_context(business_context)
                try:
                    return await func(*args, **kwargs)
                finally:
                    _context_manager.pop_context()
            else:
                return await func(*args, **kwargs)
        
        def sync_wrapper(*args, **kwargs):
            context = get_current_context()
            if context:
                business_context = context.with_business_context(
                    operation_name=operation_name,
                    resource_type=resource_type,
                    resource_id=resource_id,
                    action=action,
                    **business_data
                )
                _context_manager.push_context(business_context)
                try:
                    return func(*args, **kwargs)
                finally:
                    _context_manager.pop_context()
            else:
                return func(*args, **kwargs)
        
        # Return appropriate wrapper based on function type
        import asyncio
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator
