"""
Sentry Error Tracking Integration for Ainflue Platform
Production-ready error tracking with intelligent filtering and context

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import os
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
from dataclasses import dataclass

try:
    import sentry_sdk
    from sentry_sdk.integrations.logging import LoggingIntegration
    
    SENTRY_AVAILABLE = True
    
    # Check for optional integrations
    FLASK_AVAILABLE = False
    SQLALCHEMY_AVAILABLE = False
    REDIS_AVAILABLE = False
    CELERY_AVAILABLE = False
    
    try:
        from sentry_sdk.integrations.flask import FlaskIntegration
        FLASK_AVAILABLE = True
    except:
        pass
    
    try:
        from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration
        SQLALCHEMY_AVAILABLE = True
    except:
        pass
    
    try:
        from sentry_sdk.integrations.redis import RedisIntegration
        REDIS_AVAILABLE = True
    except:
        pass
    
    try:
        from sentry_sdk.integrations.celery import CeleryIntegration
        CELERY_AVAILABLE = True
    except:
        pass
    
except ImportError:
    SENTRY_AVAILABLE = False
    sentry_sdk = None
    FLASK_AVAILABLE = False
    SQLALCHEMY_AVAILABLE = False
    REDIS_AVAILABLE = False
    CELERY_AVAILABLE = False

logger = logging.getLogger(__name__)


@dataclass
class ErrorContext:
    """Error context information for enhanced tracking"""
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    request_id: Optional[str] = None
    service_name: Optional[str] = None
    business_context: Optional[str] = None
    workflow_stage: Optional[str] = None
    additional_data: Optional[Dict[str, Any]] = None


class SentryErrorTracker:
    """
    Production-grade Sentry error tracking integration
    Handles error capturing, filtering, and context enrichment
    """
    
    def __init__(self, dsn -> None: Optional[str] = None, environment -> None: str = "production") -> None:
        """
        Initialize Sentry error tracker
        
        Args:
            dsn: Sentry Data Source Name
            environment: Deployment environment
        """
        self.dsn = dsn or os.environ.get('SENTRY_DSN')
        self.environment = environment
        self.initialized = False
        
        if not SENTRY_AVAILABLE:
            logger.warning("Sentry SDK not available. Install with: pip install sentry-sdk")
            return
            
        if not self.dsn:
            logger.warning("Sentry DSN not configured. Error tracking disabled.")
            return
            
        self._initialize_sentry()
    
    def _initialize_sentry(self) -> None:
        """Initialize Sentry SDK with comprehensive configuration"""
        try:
            integrations = [
                LoggingIntegration(level=logging.ERROR)
            ]
            
            # Add optional integrations if available
            if FLASK_AVAILABLE:
                from sentry_sdk.integrations.flask import FlaskIntegration
                integrations.append(FlaskIntegration(auto_add_breadcrumbs=False))
            if SQLALCHEMY_AVAILABLE:
                from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration
                integrations.append(SqlalchemyIntegration())
            if REDIS_AVAILABLE:
                from sentry_sdk.integrations.redis import RedisIntegration
                integrations.append(RedisIntegration())
            if CELERY_AVAILABLE:
                from sentry_sdk.integrations.celery import CeleryIntegration
                integrations.append(CeleryIntegration())
            
            sentry_sdk.init(
                dsn=self.dsn,
                environment=self.environment,
                integrations=integrations,
                traces_sample_rate=self._get_traces_sample_rate(),
                profiles_sample_rate=self._get_profiles_sample_rate(),
                send_default_pii=False,
                attach_stacktrace=True,
                before_send=self._before_send_filter,
                before_send_transaction=self._before_send_transaction_filter,
                release=self._get_release_version(),
                max_breadcrumbs=50,
                in_app_include=['ainflue'],
                in_app_exclude=[
                    'sentry_sdk',
                    'celery',
                    'gunicorn',
                    'uvicorn'
                ]
            )
            
            # Set global tags
            sentry_sdk.set_tag("platform", "ainflue")
            sentry_sdk.set_tag("service_type", "ai_content_platform")
            
            self.initialized = True
            logger.info("Sentry error tracking initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize Sentry: {e}")
    
    def _get_traces_sample_rate(self) -> float:
        """Get traces sample rate based on environment"""
        rates = {
            'production': 0.1,
            'staging': 0.5,
            'development': 1.0
        }
        return rates.get(self.environment, 0.1)
    
    def _get_profiles_sample_rate(self) -> float:
        """Get profiles sample rate based on environment"""
        rates = {
            'production': 0.05,
            'staging': 0.2,
            'development': 0.5
        }
        return rates.get(self.environment, 0.05)
    
    def _get_release_version(self) -> str:
        """Get release version from environment or file"""
        # Try environment variable first
        version = os.environ.get('RELEASE_VERSION')
        if version:
            return version
            
        # Try reading from version file
        try:
            with open('/app/VERSION', 'r') as f:
                return f.read().strip()
        except FileNotFoundError:
            pass
            
        # Default fallback
        return "unknown"
    
    def _before_send_filter(self, event: Dict[str, Any], hint: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Filter events before sending to Sentry
        Prevents noise and sensitive data leakage
        """
        # Filter out known non-critical errors
        if 'exception' in event:
            for exception in event['exception']['values']:
                exc_type = exception.get('type', '')
                exc_value = exception.get('value', '')
                
                # Skip health check errors
                if 'health' in exc_value.lower():
                    return None
                
                # Skip connection timeouts during startup
                if 'connection timeout' in exc_value.lower() and 'startup' in exc_value.lower():
                    return None
                
                # Skip rate limiting errors
                if 'rate limit' in exc_value.lower():
                    return None
        
        # Add business context if available
        if hasattr(hint, 'business_context'):
            event.setdefault('tags', {})['business_context'] = hint.business_context
        
        return event
    
    def _before_send_transaction_filter(self, event: Dict[str, Any], hint: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Filter transaction events before sending"""
        transaction_name = event.get('transaction', '')
        
        # Skip health check transactions
        if '/health' in transaction_name or '/metrics' in transaction_name:
            return None
            
        return event
    
    def capture_error(self, 
                     error: Exception, 
                     context: Optional[ErrorContext] = None,
                     level: str = "error",
                     fingerprint: Optional[List[str]] = None) -> Optional[str]:
        """
        Capture error with enhanced context
        
        Args:
            error: Exception to capture
            context: Additional error context
            level: Error severity level
            fingerprint: Custom fingerprint for grouping
            
        Returns:
            Event ID if captured successfully
        """
        if not self.initialized:
            logger.error(f"Sentry not initialized. Error: {error}")
            return None
            
        try:
            with sentry_sdk.configure_scope() as scope:
                # Set severity level
                scope.level = level
                
                # Set user context
                if context and context.user_id:
                    scope.user = {
                        "id": context.user_id,
                        "session_id": context.session_id
                    }
                
                # Set tags
                if context:
                    if context.service_name:
                        scope.set_tag("service", context.service_name)
                    if context.business_context:
                        scope.set_tag("business_context", context.business_context)
                    if context.workflow_stage:
                        scope.set_tag("workflow_stage", context.workflow_stage)
                    if context.request_id:
                        scope.set_tag("request_id", context.request_id)
                
                # Set extra context
                if context and context.additional_data:
                    for key, value in context.additional_data.items():
                        scope.set_extra(key, value)
                
                # Set custom fingerprint for intelligent grouping
                if fingerprint:
                    scope.fingerprint = fingerprint
                else:
                    # Auto-generate fingerprint based on business context
                    fingerprint_parts = [error.__class__.__name__]
                    if context:
                        if context.service_name:
                            fingerprint_parts.append(context.service_name)
                        if context.workflow_stage:
                            fingerprint_parts.append(context.workflow_stage)
                    scope.fingerprint = fingerprint_parts
                
                # Add breadcrumb for error context
                sentry_sdk.add_breadcrumb(
                    message=f"Error captured in {context.service_name if context else 'unknown service'}",
                    category="error_tracking",
                    level="error",
                    data={
                        "workflow_stage": context.workflow_stage if context else None,
                        "timestamp": datetime.utcnow().isoformat()
                    }
                )
                
                # Capture the exception
                event_id = sentry_sdk.capture_exception(error)
                
                logger.info(f"Error captured to Sentry: {event_id}")
                return event_id
                
        except Exception as e:
            logger.error(f"Failed to capture error to Sentry: {e}")
            return None
    
    def capture_message(self, 
                       message: str, 
                       level: str = "info",
                       context: Optional[ErrorContext] = None) -> Optional[str]:
        """
        Capture custom message with context
        
        Args:
            message: Message to capture
            level: Message severity level
            context: Additional context
            
        Returns:
            Event ID if captured successfully
        """
        if not self.initialized:
            logger.warning(f"Sentry not initialized. Message: {message}")
            return None
            
        try:
            with sentry_sdk.configure_scope() as scope:
                scope.level = level
                
                if context:
                    if context.user_id:
                        scope.user = {"id": context.user_id}
                    if context.service_name:
                        scope.set_tag("service", context.service_name)
                    if context.business_context:
                        scope.set_tag("business_context", context.business_context)
                
                event_id = sentry_sdk.capture_message(message, level)
                return event_id
                
        except Exception as e:
            logger.error(f"Failed to capture message to Sentry: {e}")
            return None
    
    def set_user_context(self, user_id -> None: str, email -> None: Optional[str] = None, 
                        additional_data -> None: Optional[Dict[str, Any]] = None) -> None:
        """Set user context for error tracking"""
        if not self.initialized:
            return
            
        try:
            with sentry_sdk.configure_scope() as scope:
                user_data = {"id": user_id}
                if email:
                    user_data["email"] = email
                if additional_data:
                    user_data.update(additional_data)
                scope.user = user_data
                
        except Exception as e:
            logger.error(f"Failed to set user context: {e}")
    
    def add_breadcrumb(self, message -> None: str, category -> None: str = "custom", 
                      level -> None: str = "info", data -> None: Optional[Dict[str, Any]] = None) -> None:
        """Add breadcrumb for error context"""
        if not self.initialized:
            return
            
        try:
            sentry_sdk.add_breadcrumb(
                message=message,
                category=category,
                level=level,
                data=data or {}
            )
        except Exception as e:
            logger.error(f"Failed to add breadcrumb: {e}")
    
    def flush(self, timeout -> None: int = 2) -> None:
        """Flush pending events to Sentry"""
        if not self.initialized:
            return
            
        try:
            sentry_sdk.flush(timeout=timeout)
        except Exception as e:
            logger.error(f"Failed to flush Sentry events: {e}")


# Global instance for easy access
error_tracker = SentryErrorTracker()


def capture_business_error(error: Exception, 
                          workflow_stage: str,
                          user_id: Optional[str] = None,
                          additional_context: Optional[Dict[str, Any]] = None) -> Optional[str]:
    """
    Convenience function for capturing business logic errors
    
    Args:
        error: Exception to capture
        workflow_stage: Business workflow stage (upload, ai_processing, protection, etc.)
        user_id: User ID if available
        additional_context: Additional context data
        
    Returns:
        Event ID if captured successfully
    """
    context = ErrorContext(
        user_id=user_id,
        business_context="business_workflow",
        workflow_stage=workflow_stage,
        additional_data=additional_context
    )
    
    return error_tracker.capture_error(error, context, level="error")


def capture_ai_processing_error(error: Exception,
                               model_name: str,
                               processing_type: str,
                               user_id: Optional[str] = None) -> Optional[str]:
    """
    Specialized function for AI processing errors
    
    Args:
        error: Exception to capture
        model_name: AI model name
        processing_type: Type of AI processing
        user_id: User ID if available
        
    Returns:
        Event ID if captured successfully
    """
    context = ErrorContext(
        user_id=user_id,
        service_name="ai_engine",
        business_context="ai_processing",
        workflow_stage="ai_analysis",
        additional_data={
            "model_name": model_name,
            "processing_type": processing_type
        }
    )
    
    return error_tracker.capture_error(error, context, level="error")