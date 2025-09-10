"""Integration Error Handling System
===================================

Comprehensive error handling and recovery system for all platform integrations.
Provides standardized error processing, logging, and recovery mechanisms.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
import traceback
import json
from typing import Dict, List, Optional, Any, Callable, Union
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from enum import Enum
import aiohttp


class ErrorSeverity(Enum):
    """Error severity levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ErrorCategory(Enum):
    """Error categories"""
    AUTHENTICATION = "authentication"
    AUTHORIZATION = "authorization"
    RATE_LIMIT = "rate_limit"
    NETWORK = "network"
    TIMEOUT = "timeout"
    VALIDATION = "validation"
    API_ERROR = "api_error"
    CONFIGURATION = "configuration"
    QUOTA_EXCEEDED = "quota_exceeded"
    SERVICE_UNAVAILABLE = "service_unavailable"
    UNKNOWN = "unknown"


@dataclass
class IntegrationError:
    """Integration error data structure"""
    id: str
    integration: str
    category: ErrorCategory
    severity: ErrorSeverity
    message: str
    details: Optional[Dict[str, Any]] = None
    timestamp: datetime = None
    resolved: bool = False
    resolution_note: Optional[str] = None
    stack_trace: Optional[str] = None
    user_id: Optional[str] = None
    retry_count: int = 0
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.utcnow()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        data = asdict(self)
        data['timestamp'] = self.timestamp.isoformat()
        data['category'] = self.category.value
        data['severity'] = self.severity.value
        return data


class IntegrationErrorHandler:
    """Centralized error handling system"""
    
    def __init__(self):
        """Initialize error handler"""
        self.logger = logging.getLogger(__name__)
        
        # Error storage
        self.errors: Dict[str, IntegrationError] = {}
        self.error_patterns: Dict[str, ErrorCategory] = {}
        
        # Error handlers
        self.error_handlers: Dict[ErrorCategory, List[Callable]] = {}
        self.recovery_handlers: Dict[str, Callable] = {}
        
        # Statistics
        self.stats = {
            "total_errors": 0,
            "errors_by_category": {},
            "errors_by_integration": {},
            "errors_by_severity": {},
            "resolved_errors": 0,
            "unresolved_errors": 0
        }
        
        # Auto-recovery settings
        self.auto_recovery_enabled = True
        self.max_retry_attempts = 3
        self.retry_delays = [60, 300, 900]  # 1min, 5min, 15min
        
        self._setup_error_patterns()
        self._setup_default_handlers()
    
    def _setup_error_patterns(self):
        """Setup common error patterns for categorization"""
        self.error_patterns = {
            # Authentication errors
            "unauthorized": ErrorCategory.AUTHENTICATION,
            "invalid_token": ErrorCategory.AUTHENTICATION,
            "token_expired": ErrorCategory.AUTHENTICATION,
            "authentication_failed": ErrorCategory.AUTHENTICATION,
            "401": ErrorCategory.AUTHENTICATION,
            
            # Authorization errors
            "forbidden": ErrorCategory.AUTHORIZATION,
            "access_denied": ErrorCategory.AUTHORIZATION,
            "insufficient_permissions": ErrorCategory.AUTHORIZATION,
            "403": ErrorCategory.AUTHORIZATION,
            
            # Rate limiting
            "rate_limit": ErrorCategory.RATE_LIMIT,
            "too_many_requests": ErrorCategory.RATE_LIMIT,
            "quota_exceeded": ErrorCategory.QUOTA_EXCEEDED,
            "429": ErrorCategory.RATE_LIMIT,
            
            # Network errors
            "connection_error": ErrorCategory.NETWORK,
            "network_error": ErrorCategory.NETWORK,
            "dns_error": ErrorCategory.NETWORK,
            "ssl_error": ErrorCategory.NETWORK,
            
            # Timeout errors
            "timeout": ErrorCategory.TIMEOUT,
            "request_timeout": ErrorCategory.TIMEOUT,
            "read_timeout": ErrorCategory.TIMEOUT,
            "504": ErrorCategory.TIMEOUT,
            
            # Service unavailable
            "service_unavailable": ErrorCategory.SERVICE_UNAVAILABLE,
            "server_error": ErrorCategory.SERVICE_UNAVAILABLE,
            "500": ErrorCategory.SERVICE_UNAVAILABLE,
            "502": ErrorCategory.SERVICE_UNAVAILABLE,
            "503": ErrorCategory.SERVICE_UNAVAILABLE,
            
            # Validation errors
            "validation_error": ErrorCategory.VALIDATION,
            "invalid_request": ErrorCategory.VALIDATION,
            "bad_request": ErrorCategory.VALIDATION,
            "400": ErrorCategory.VALIDATION,
        }
    
    def _setup_default_handlers(self):
        """Setup default error handlers"""
        
        # Authentication error handler
        async def handle_auth_error(error: IntegrationError):
            """Handle authentication errors"""
            self.logger.warning(f"Authentication error in {error.integration}: {error.message}")
            
            # Trigger token refresh if applicable
            if "token" in error.message.lower():
                await self._trigger_token_refresh(error.integration, error.user_id)
        
        # Rate limit handler
        async def handle_rate_limit_error(error: IntegrationError):
            """Handle rate limit errors"""
            self.logger.warning(f"Rate limit exceeded for {error.integration}: {error.message}")
            
            # Extract retry-after if available
            retry_after = self._extract_retry_after(error)
            if retry_after:
                self.logger.info(f"Will retry {error.integration} after {retry_after} seconds")
        
        # Network error handler
        async def handle_network_error(error: IntegrationError):
            """Handle network errors"""
            self.logger.error(f"Network error in {error.integration}: {error.message}")
            
            # Schedule retry for transient network issues
            if error.retry_count < self.max_retry_attempts:
                await self._schedule_retry(error)
        
        # Service unavailable handler
        async def handle_service_error(error: IntegrationError):
            """Handle service unavailable errors"""
            self.logger.error(f"Service unavailable for {error.integration}: {error.message}")
            
            # Check service status and schedule retry
            await self._check_service_status(error.integration)
            if error.retry_count < self.max_retry_attempts:
                await self._schedule_retry(error)
        
        # Register handlers
        self.register_error_handler(ErrorCategory.AUTHENTICATION, handle_auth_error)
        self.register_error_handler(ErrorCategory.RATE_LIMIT, handle_rate_limit_error)
        self.register_error_handler(ErrorCategory.NETWORK, handle_network_error)
        self.register_error_handler(ErrorCategory.SERVICE_UNAVAILABLE, handle_service_error)
    
    def register_error_handler(self, category: ErrorCategory, handler: Callable):
        """Register error handler for category
        
        Args:
            category: Error category
            handler: Handler function
        """
        if category not in self.error_handlers:
            self.error_handlers[category] = []
        
        self.error_handlers[category].append(handler)
        self.logger.info(f"Registered error handler for category: {category.value}")
    
    def register_recovery_handler(self, integration: str, handler: Callable):
        """Register recovery handler for integration
        
        Args:
            integration: Integration name
            handler: Recovery handler function
        """
        self.recovery_handlers[integration] = handler
        self.logger.info(f"Registered recovery handler for integration: {integration}")
    
    async def handle_error(self, integration: str, error: Exception, 
                         user_id: Optional[str] = None, **context) -> IntegrationError:
        """Handle integration error
        
        Args:
            integration: Integration name
            error: Exception object
            user_id: User identifier
            **context: Additional context
            
        Returns:
            IntegrationError: Created error object
        """
        try:
            # Create error object
            integration_error = self._create_error_object(
                integration, error, user_id, context
            )
            
            # Store error
            self.errors[integration_error.id] = integration_error
            
            # Update statistics
            self._update_stats(integration_error)
            
            # Log error
            self._log_error(integration_error)
            
            # Process error
            await self._process_error(integration_error)
            
            return integration_error
            
        except Exception as e:
            self.logger.error(f"Error in error handler: {e}")
            # Create minimal error object
            return IntegrationError(
                id=f"err_{int(datetime.utcnow().timestamp())}",
                integration=integration,
                category=ErrorCategory.UNKNOWN,
                severity=ErrorSeverity.MEDIUM,
                message=str(error)
            )
    
    def _create_error_object(self, integration: str, error: Exception, 
                           user_id: Optional[str], context: Dict[str, Any]) -> IntegrationError:
        """Create error object from exception
        
        Args:
            integration: Integration name
            error: Exception object
            user_id: User identifier
            context: Additional context
            
        Returns:
            IntegrationError: Error object
        """
        error_message = str(error).lower()
        
        # Categorize error
        category = self._categorize_error(error_message)
        
        # Determine severity
        severity = self._determine_severity(category, error)
        
        # Extract details
        details = self._extract_error_details(error, context)
        
        # Generate error ID
        error_id = f"err_{integration}_{int(datetime.utcnow().timestamp())}_{hash(str(error)) % 10000:04d}"
        
        return IntegrationError(
            id=error_id,
            integration=integration,
            category=category,
            severity=severity,
            message=str(error),
            details=details,
            user_id=user_id,
            stack_trace=traceback.format_exc()
        )
    
    def _categorize_error(self, error_message: str) -> ErrorCategory:
        """Categorize error based on message
        
        Args:
            error_message: Error message
            
        Returns:
            ErrorCategory: Error category
        """
        for pattern, category in self.error_patterns.items():
            if pattern in error_message:
                return category
        
        return ErrorCategory.UNKNOWN
    
    def _determine_severity(self, category: ErrorCategory, error: Exception) -> ErrorSeverity:
        """Determine error severity
        
        Args:
            category: Error category
            error: Exception object
            
        Returns:
            ErrorSeverity: Error severity
        """
        # Critical errors
        if category in [ErrorCategory.SERVICE_UNAVAILABLE, ErrorCategory.CONFIGURATION]:
            return ErrorSeverity.CRITICAL
        
        # High priority errors
        elif category in [ErrorCategory.AUTHENTICATION, ErrorCategory.AUTHORIZATION]:
            return ErrorSeverity.HIGH
        
        # Medium priority errors
        elif category in [ErrorCategory.RATE_LIMIT, ErrorCategory.QUOTA_EXCEEDED]:
            return ErrorSeverity.MEDIUM
        
        # Low priority errors
        else:
            return ErrorSeverity.LOW
    
    def _extract_error_details(self, error: Exception, context: Dict[str, Any]) -> Dict[str, Any]:
        """Extract additional error details
        
        Args:
            error: Exception object
            context: Context information
            
        Returns:
            Dict[str, Any]: Error details
        """
        details = {
            "error_type": type(error).__name__,
            "context": context
        }
        
        # HTTP errors
        if hasattr(error, 'status'):
            details['http_status'] = error.status
        
        if hasattr(error, 'headers'):
            details['response_headers'] = dict(error.headers)
        
        # Request details
        if 'request' in context:
            request = context['request']
            details['request_url'] = getattr(request, 'url', None)
            details['request_method'] = getattr(request, 'method', None)
        
        return details
    
    def _update_stats(self, error: IntegrationError):
        """Update error statistics
        
        Args:
            error: Integration error
        """
        self.stats["total_errors"] += 1
        
        # By category
        category = error.category.value
        if category not in self.stats["errors_by_category"]:
            self.stats["errors_by_category"][category] = 0
        self.stats["errors_by_category"][category] += 1
        
        # By integration
        integration = error.integration
        if integration not in self.stats["errors_by_integration"]:
            self.stats["errors_by_integration"][integration] = 0
        self.stats["errors_by_integration"][integration] += 1
        
        # By severity
        severity = error.severity.value
        if severity not in self.stats["errors_by_severity"]:
            self.stats["errors_by_severity"][severity] = 0
        self.stats["errors_by_severity"][severity] += 1
        
        # Update resolved/unresolved counts
        if error.resolved:
            self.stats["resolved_errors"] += 1
        else:
            self.stats["unresolved_errors"] += 1
    
    def _log_error(self, error: IntegrationError):
        """Log error with appropriate level
        
        Args:
            error: Integration error
        """
        log_message = f"[{error.integration}] {error.category.value}: {error.message}"
        
        if error.severity == ErrorSeverity.CRITICAL:
            self.logger.critical(log_message)
        elif error.severity == ErrorSeverity.HIGH:
            self.logger.error(log_message)
        elif error.severity == ErrorSeverity.MEDIUM:
            self.logger.warning(log_message)
        else:
            self.logger.info(log_message)
        
        # Log stack trace for high/critical errors
        if error.severity in [ErrorSeverity.HIGH, ErrorSeverity.CRITICAL] and error.stack_trace:
            self.logger.debug(f"Stack trace for {error.id}:\n{error.stack_trace}")
    
    async def _process_error(self, error: IntegrationError):
        """Process error with appropriate handlers
        
        Args:
            error: Integration error
        """
        try:
            # Get handlers for this category
            handlers = self.error_handlers.get(error.category, [])
            
            # Process with all handlers
            for handler in handlers:
                try:
                    if asyncio.iscoroutinefunction(handler):
                        await handler(error)
                    else:
                        handler(error)
                except Exception as e:
                    self.logger.error(f"Error handler failed: {e}")
            
            # Attempt auto-recovery if enabled
            if self.auto_recovery_enabled and not error.resolved:
                await self._attempt_recovery(error)
                
        except Exception as e:
            self.logger.error(f"Error processing error {error.id}: {e}")
    
    async def _attempt_recovery(self, error: IntegrationError):
        """Attempt automatic error recovery
        
        Args:
            error: Integration error
        """
        try:
            # Check if recovery handler exists
            if error.integration in self.recovery_handlers:
                recovery_handler = self.recovery_handlers[error.integration]
                
                success = False
                if asyncio.iscoroutinefunction(recovery_handler):
                    success = await recovery_handler(error)
                else:
                    success = recovery_handler(error)
                
                if success:
                    await self.resolve_error(error.id, "Auto-recovery successful")
                    self.logger.info(f"Auto-recovery successful for error {error.id}")
                else:
                    self.logger.warning(f"Auto-recovery failed for error {error.id}")
            
            # Category-specific recovery
            elif error.category == ErrorCategory.RATE_LIMIT:
                # Wait for rate limit reset
                retry_after = self._extract_retry_after(error)
                if retry_after and retry_after <= 3600:  # Max 1 hour wait
                    await asyncio.sleep(retry_after)
                    await self.resolve_error(error.id, f"Rate limit recovery after {retry_after}s")
            
            elif error.category == ErrorCategory.AUTHENTICATION:
                # Trigger token refresh
                if error.user_id:
                    await self._trigger_token_refresh(error.integration, error.user_id)
                    
        except Exception as e:
            self.logger.error(f"Recovery attempt failed for error {error.id}: {e}")
    
    async def resolve_error(self, error_id: str, resolution_note: str = ""):
        """Mark error as resolved
        
        Args:
            error_id: Error ID
            resolution_note: Resolution note
        """
        if error_id in self.errors:
            error = self.errors[error_id]
            error.resolved = True
            error.resolution_note = resolution_note
            
            # Update statistics
            self.stats["resolved_errors"] += 1
            self.stats["unresolved_errors"] -= 1
            
            self.logger.info(f"Resolved error {error_id}: {resolution_note}")
    
    async def get_error(self, error_id: str) -> Optional[IntegrationError]:
        """Get error by ID
        
        Args:
            error_id: Error ID
            
        Returns:
            Optional[IntegrationError]: Error object
        """
        return self.errors.get(error_id)
    
    async def get_errors(self, integration: Optional[str] = None, 
                       category: Optional[ErrorCategory] = None,
                       severity: Optional[ErrorSeverity] = None,
                       resolved: Optional[bool] = None,
                       limit: int = 100) -> List[IntegrationError]:
        """Get errors with filters
        
        Args:
            integration: Filter by integration
            category: Filter by category
            severity: Filter by severity
            resolved: Filter by resolution status
            limit: Maximum number of errors
            
        Returns:
            List[IntegrationError]: Filtered errors
        """
        errors = list(self.errors.values())
        
        # Apply filters
        if integration:
            errors = [e for e in errors if e.integration == integration]
        
        if category:
            errors = [e for e in errors if e.category == category]
        
        if severity:
            errors = [e for e in errors if e.severity == severity]
        
        if resolved is not None:
            errors = [e for e in errors if e.resolved == resolved]
        
        # Sort by timestamp (newest first)
        errors.sort(key=lambda e: e.timestamp, reverse=True)
        
        return errors[:limit]
    
    async def get_error_statistics(self) -> Dict[str, Any]:
        """Get error statistics
        
        Returns:
            Dict[str, Any]: Error statistics
        """
        stats = self.stats.copy()
        
        # Calculate rates
        total = stats["total_errors"]
        if total > 0:
            stats["resolution_rate"] = stats["resolved_errors"] / total
            stats["error_rate_by_category"] = {}
            
            for category, count in stats["errors_by_category"].items():
                stats["error_rate_by_category"][category] = count / total
        
        return stats
    
    async def cleanup_old_errors(self, max_age_days: int = 30):
        """Clean up old resolved errors
        
        Args:
            max_age_days: Maximum age in days
        """
        cutoff_date = datetime.utcnow() - timedelta(days=max_age_days)
        
        errors_to_remove = []
        for error_id, error in self.errors.items():
            if error.resolved and error.timestamp < cutoff_date:
                errors_to_remove.append(error_id)
        
        for error_id in errors_to_remove:
            del self.errors[error_id]
        
        self.logger.info(f"Cleaned up {len(errors_to_remove)} old errors")
    
    def _extract_retry_after(self, error: IntegrationError) -> Optional[int]:
        """Extract retry-after value from error
        
        Args:
            error: Integration error
            
        Returns:
            Optional[int]: Retry after seconds
        """
        if error.details and 'response_headers' in error.details:
            headers = error.details['response_headers']
            
            # Check for Retry-After header
            retry_after = headers.get('Retry-After') or headers.get('retry-after')
            if retry_after:
                try:
                    return int(retry_after)
                except ValueError:
                    pass
        
        # Default retry delays based on category
        if error.category == ErrorCategory.RATE_LIMIT:
            return 300  # 5 minutes
        elif error.category == ErrorCategory.SERVICE_UNAVAILABLE:
            return 600  # 10 minutes
        
        return None
    
    async def _trigger_token_refresh(self, integration: str, user_id: str):
        """Trigger token refresh for integration
        
        Args:
            integration: Integration name
            user_id: User identifier
        """
        try:
            # This would typically trigger the OAuth manager to refresh tokens
            self.logger.info(f"Triggering token refresh for {integration}:{user_id}")
            # Implementation would depend on OAuth manager integration
            
        except Exception as e:
            self.logger.error(f"Failed to trigger token refresh: {e}")
    
    async def _schedule_retry(self, error: IntegrationError):
        """Schedule retry for error
        
        Args:
            error: Integration error
        """
        if error.retry_count < len(self.retry_delays):
            delay = self.retry_delays[error.retry_count]
            error.retry_count += 1
            
            self.logger.info(f"Scheduling retry for {error.id} in {delay} seconds")
            
            # In a real implementation, this would schedule the retry
            # For now, just log the intent
            
    async def _check_service_status(self, integration: str):
        """Check service status for integration
        
        Args:
            integration: Integration name
        """
        try:
            # This would check the service status
            self.logger.info(f"Checking service status for {integration}")
            
            # Implementation would depend on service monitoring integration
            
        except Exception as e:
            self.logger.error(f"Failed to check service status for {integration}: {e}")


# Global error handler instance
error_handler = IntegrationErrorHandler()


async def get_error_handler() -> IntegrationErrorHandler:
    """Get global error handler instance
    
    Returns:
        IntegrationErrorHandler: Global instance
    """
    return error_handler