"""Retry Handler - Intelligent Retry Mechanism
==========================================

Advanced retry handling system for integration failures.
Provides exponential backoff, jitter, and intelligent retry strategies.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
import random
import time
from typing import Dict, List, Optional, Any, Callable, Union
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import json


class RetryStrategy(Enum):
    """Retry strategies."""
    FIXED_DELAY = "fixed_delay"
    EXPONENTIAL_BACKOFF = "exponential_backoff"
    LINEAR_BACKOFF = "linear_backoff"
    CUSTOM = "custom"


class JitterType(Enum):
    """Jitter types for retry delays."""
    NONE = "none"
    FULL = "full"           # Random delay between 0 and calculated delay
    EQUAL = "equal"         # Half calculated delay + random half
    DECORRELATED = "decorrelated"  # Based on previous delay


@dataclass
class RetryConfig:
    """Retry configuration."""
    integration_name: str
    max_attempts: int = 3
    base_delay: float = 1.0      # Base delay in seconds
    max_delay: float = 300.0     # Maximum delay in seconds
    strategy: RetryStrategy = RetryStrategy.EXPONENTIAL_BACKOFF
    backoff_multiplier: float = 2.0
    jitter_type: JitterType = JitterType.EQUAL
    retry_on_exceptions: List[str] = field(default_factory=lambda: [
        "ConnectionError", "TimeoutError", "HTTPStatusError"
    ])
    retry_on_status_codes: List[int] = field(default_factory=lambda: [
        429, 500, 502, 503, 504
    ])
    stop_on_status_codes: List[int] = field(default_factory=lambda: [
        400, 401, 403, 404
    ])
    custom_retry_condition: Optional[Callable] = None
    custom_delay_function: Optional[Callable] = None
    enabled: bool = True
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class RetryAttempt:
    """Individual retry attempt record."""
    attempt_number: int
    timestamp: datetime
    delay_before_attempt: float
    error_type: str
    error_message: str
    status_code: Optional[int] = None
    response_time: float = 0.0
    success: bool = False


@dataclass
class RetrySession:
    """Retry session tracking."""
    id: str
    integration_name: str
    original_request: Dict[str, Any]
    config: RetryConfig
    attempts: List[RetryAttempt] = field(default_factory=list)
    started_at: datetime = field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None
    final_success: bool = False
    total_delay: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class RetryStats:
    """Retry statistics."""
    total_sessions: int = 0
    successful_retries: int = 0
    failed_retries: int = 0
    total_attempts: int = 0
    average_attempts_per_session: float = 0.0
    average_total_delay: float = 0.0
    success_rate_after_retry: float = 0.0
    most_common_errors: Dict[str, int] = field(default_factory=dict)


class RetryHandler:
    """Intelligent retry mechanism for integration failures.
    
    Provides advanced retry handling with multiple strategies,
    intelligent backoff, jitter, and detailed retry analytics.
    """
    
    def __init__(self):
        """Initialize retry handler."""
        self.logger = logging.getLogger(__name__)
        
        # Retry configurations by integration
        self.configs: Dict[str, RetryConfig] = {}
        
        # Active retry sessions
        self.active_sessions: Dict[str, RetrySession] = {}
        
        # Completed sessions (keep recent history)
        self.completed_sessions: List[RetrySession] = []
        self.max_completed_sessions = 1000
        
        # Retry statistics
        self.stats: Dict[str, RetryStats] = {}
        
        # Global settings
        self.session_timeout = 3600  # 1 hour max session duration
        self.max_concurrent_retries = 100
        
        # Initialize default configurations
        self._initialize_default_configs()
    
    def _initialize_default_configs(self) -> None:
        """Initialize default retry configurations."""
        default_configs = [
            # Social media platforms - aggressive retries
            RetryConfig(
                integration_name="youtube",
                max_attempts=5,
                base_delay=2.0,
                max_delay=120.0,
                backoff_multiplier=2.0,
                jitter_type=JitterType.EQUAL,
                retry_on_status_codes=[429, 500, 502, 503, 504],
                stop_on_status_codes=[400, 401, 403, 404]
            ),
            RetryConfig(
                integration_name="instagram",
                max_attempts=4,
                base_delay=1.5,
                max_delay=60.0,
                backoff_multiplier=1.8,
                jitter_type=JitterType.FULL,
                retry_on_status_codes=[429, 500, 502, 503, 504]
            ),
            RetryConfig(
                integration_name="tiktok",
                max_attempts=3,
                base_delay=2.0,
                max_delay=60.0,
                backoff_multiplier=2.0,
                jitter_type=JitterType.DECORRELATED
            ),
            RetryConfig(
                integration_name="spotify",
                max_attempts=4,
                base_delay=1.0,
                max_delay=90.0,
                backoff_multiplier=2.0,
                jitter_type=JitterType.EQUAL
            ),
            
            # AI services - conservative retries due to cost
            RetryConfig(
                integration_name="openai",
                max_attempts=3,
                base_delay=5.0,
                max_delay=180.0,
                backoff_multiplier=2.5,
                jitter_type=JitterType.EQUAL,
                retry_on_status_codes=[429, 500, 503],
                stop_on_status_codes=[400, 401, 403, 404, 422]
            ),
            RetryConfig(
                integration_name="anthropic",
                max_attempts=3,
                base_delay=3.0,
                max_delay=120.0,
                backoff_multiplier=2.0,
                jitter_type=JitterType.EQUAL,
                retry_on_status_codes=[429, 500, 503]
            ),
            
            # Payment gateways - very conservative retries
            RetryConfig(
                integration_name="stripe",
                max_attempts=2,
                base_delay=10.0,
                max_delay=60.0,
                backoff_multiplier=1.5,
                jitter_type=JitterType.NONE,
                retry_on_status_codes=[429, 500, 503],
                stop_on_status_codes=[400, 401, 402, 403, 404, 422]
            ),
            RetryConfig(
                integration_name="paypal",
                max_attempts=2,
                base_delay=8.0,
                max_delay=45.0,
                backoff_multiplier=1.5,
                jitter_type=JitterType.NONE,
                retry_on_status_codes=[429, 500, 503]
            ),
            
            # Cloud providers - moderate retries
            RetryConfig(
                integration_name="aws",
                max_attempts=4,
                base_delay=1.0,
                max_delay=60.0,
                strategy=RetryStrategy.EXPONENTIAL_BACKOFF,
                backoff_multiplier=2.0,
                jitter_type=JitterType.FULL
            ),
            RetryConfig(
                integration_name="gcp",
                max_attempts=4,
                base_delay=1.0,
                max_delay=60.0,
                strategy=RetryStrategy.EXPONENTIAL_BACKOFF,
                backoff_multiplier=2.0,
                jitter_type=JitterType.DECORRELATED
            ),
        ]
        
        for config in default_configs:
            self.configs[config.integration_name] = config
            self.stats[config.integration_name] = RetryStats()
    
    async def handle_failed_request(
        self,
        integration_name: str,
        method: str,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        error: str = "",
        status_code: Optional[int] = None,
        session_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Handle failed request with intelligent retry logic."""
        try:
            # Get or create retry configuration
            if integration_name not in self.configs:
                await self._initialize_integration_retry(integration_name)
            
            config = self.configs[integration_name]
            
            if not config.enabled:
                return {
                    "success": False,
                    "error": "Retry disabled for integration",
                    "retry_attempted": False
                }
            
            # Check if we should retry this error
            if not await self._should_retry(config, error, status_code):
                return {
                    "success": False,
                    "error": error,
                    "retry_attempted": False,
                    "reason": "Error not retryable"
                }
            
            # Create or get retry session
            if session_id and session_id in self.active_sessions:
                session = self.active_sessions[session_id]
            else:
                session = await self._create_retry_session(
                    integration_name, method, endpoint, data, headers, config
                )
            
            # Check if we've exceeded max attempts
            if len(session.attempts) >= config.max_attempts:
                await self._complete_session(session, False)
                return {
                    "success": False,
                    "error": f"Max retry attempts ({config.max_attempts}) exceeded",
                    "retry_attempted": True,
                    "total_attempts": len(session.attempts),
                    "session_id": session.id
                }
            
            # Record this attempt
            attempt = RetryAttempt(
                attempt_number=len(session.attempts) + 1,
                timestamp=datetime.utcnow(),
                delay_before_attempt=0.0,
                error_type=type(Exception(error)).__name__,
                error_message=error,
                status_code=status_code
            )
            
            # Calculate retry delay
            delay = await self._calculate_retry_delay(session, config)
            attempt.delay_before_attempt = delay
            session.total_delay += delay
            
            # Add attempt to session
            session.attempts.append(attempt)
            
            # Log retry attempt
            self.logger.info(
                f"Retry attempt {attempt.attempt_number}/{config.max_attempts} "
                f"for {integration_name} after {delay:.2f}s delay"
            )
            
            # Wait for retry delay
            await asyncio.sleep(delay)
            
            # This would typically trigger the actual retry request
            # For now, we'll simulate the retry logic
            retry_result = await self._execute_retry(session, config)
            
            # Update statistics
            await self._update_retry_stats(integration_name, session)
            
            return retry_result
            
        except Exception as e:
            self.logger.error(f"Retry handler error for {integration_name}: {str(e)}")
            return {
                "success": False,
                "error": f"Retry handler error: {str(e)}",
                "retry_attempted": False
            }
    
    async def _should_retry(
        self,
        config: RetryConfig,
        error: str,
        status_code: Optional[int]
    ) -> bool:
        """Determine if request should be retried."""
        # Check status codes first
        if status_code:
            if status_code in config.stop_on_status_codes:
                return False
            if status_code in config.retry_on_status_codes:
                return True
        
        # Check exception types
        for retry_exception in config.retry_on_exceptions:
            if retry_exception.lower() in error.lower():
                return True
        
        # Use custom retry condition if provided
        if config.custom_retry_condition:
            try:
                return await config.custom_retry_condition(error, status_code)
            except Exception as e:
                self.logger.error(f"Custom retry condition error: {str(e)}")
                return False
        
        # Default behavior - retry on server errors and timeouts
        server_error_indicators = ["500", "502", "503", "504", "timeout", "connection"]
        return any(indicator in error.lower() for indicator in server_error_indicators)
    
    async def _create_retry_session(
        self,
        integration_name: str,
        method: str,
        endpoint: str,
        data: Optional[Dict[str, Any]],
        headers: Optional[Dict[str, str]],
        config: RetryConfig
    ) -> RetrySession:
        """Create new retry session."""
        import uuid
        
        session = RetrySession(
            id=str(uuid.uuid4()),
            integration_name=integration_name,
            original_request={
                "method": method,
                "endpoint": endpoint,
                "data": data,
                "headers": headers
            },
            config=config
        )
        
        self.active_sessions[session.id] = session
        return session
    
    async def _calculate_retry_delay(self, session: RetrySession, config: RetryConfig) -> float:
        """Calculate retry delay based on strategy and jitter."""
        attempt_number = len(session.attempts)
        
        # Calculate base delay using strategy
        if config.strategy == RetryStrategy.FIXED_DELAY:
            base_delay = config.base_delay
            
        elif config.strategy == RetryStrategy.EXPONENTIAL_BACKOFF:
            base_delay = config.base_delay * (config.backoff_multiplier ** (attempt_number - 1))
            
        elif config.strategy == RetryStrategy.LINEAR_BACKOFF:
            base_delay = config.base_delay * attempt_number
            
        elif config.strategy == RetryStrategy.CUSTOM and config.custom_delay_function:
            try:
                base_delay = await config.custom_delay_function(attempt_number, session)
            except Exception as e:
                self.logger.error(f"Custom delay function error: {str(e)}")
                base_delay = config.base_delay
        else:
            base_delay = config.base_delay
        
        # Apply maximum delay limit
        base_delay = min(base_delay, config.max_delay)
        
        # Apply jitter
        if config.jitter_type == JitterType.NONE:
            final_delay = base_delay
            
        elif config.jitter_type == JitterType.FULL:
            final_delay = random.uniform(0, base_delay)
            
        elif config.jitter_type == JitterType.EQUAL:
            jitter_amount = base_delay * 0.5
            final_delay = (base_delay * 0.5) + random.uniform(0, jitter_amount)
            
        elif config.jitter_type == JitterType.DECORRELATED:
            if session.attempts:
                previous_delay = session.attempts[-1].delay_before_attempt
                final_delay = random.uniform(config.base_delay, previous_delay * 3)
            else:
                final_delay = base_delay
        else:
            final_delay = base_delay
        
        return max(0.1, final_delay)  # Minimum 0.1 second delay
    
    async def _execute_retry(self, session: RetrySession, config: RetryConfig) -> Dict[str, Any]:
        """Execute the actual retry (placeholder for integration with API gateway)."""
        # This would integrate with the actual API gateway to retry the request
        # For now, we'll simulate success/failure based on attempt number
        
        attempt_number = len(session.attempts)
        
        # Simulate increasing success probability with each attempt
        success_probability = min(0.1 + (attempt_number * 0.3), 0.9)
        success = random.random() < success_probability
        
        if success:
            await self._complete_session(session, True)
            return {
                "success": True,
                "data": {"simulated": "retry_success"},
                "retry_attempted": True,
                "total_attempts": len(session.attempts),
                "total_delay": session.total_delay,
                "session_id": session.id
            }
        else:
            # Continue with more retries if available
            return {
                "success": False,
                "error": f"Retry attempt {attempt_number} failed",
                "retry_attempted": True,
                "will_retry_again": attempt_number < config.max_attempts,
                "session_id": session.id
            }
    
    async def _complete_session(self, session: RetrySession, success: bool) -> None:
        """Complete retry session."""
        session.completed_at = datetime.utcnow()
        session.final_success = success
        
        # Move to completed sessions
        if session.id in self.active_sessions:
            del self.active_sessions[session.id]
        
        self.completed_sessions.append(session)
        
        # Maintain completed sessions limit
        if len(self.completed_sessions) > self.max_completed_sessions:
            self.completed_sessions.pop(0)
        
        # Log completion
        duration = (session.completed_at - session.started_at).total_seconds()
        outcome = "succeeded" if success else "failed"
        
        self.logger.info(
            f"Retry session {session.id} {outcome} after {len(session.attempts)} attempts "
            f"and {duration:.2f}s (total delay: {session.total_delay:.2f}s)"
        )
    
    async def _update_retry_stats(self, integration_name: str, session: RetrySession) -> None:
        """Update retry statistics."""
        stats = self.stats[integration_name]
        
        if session.completed_at:  # Session is complete
            stats.total_sessions += 1
            
            if session.final_success:
                stats.successful_retries += 1
            else:
                stats.failed_retries += 1
            
            # Update averages
            stats.average_attempts_per_session = (
                (stats.average_attempts_per_session * (stats.total_sessions - 1) + len(session.attempts)) /
                stats.total_sessions
            )
            
            stats.average_total_delay = (
                (stats.average_total_delay * (stats.total_sessions - 1) + session.total_delay) /
                stats.total_sessions
            )
            
            # Update success rate
            if stats.total_sessions > 0:
                stats.success_rate_after_retry = (stats.successful_retries / stats.total_sessions) * 100
        
        # Update attempt count
        stats.total_attempts += 1
        
        # Track common errors
        if session.attempts:
            latest_attempt = session.attempts[-1]
            error_type = latest_attempt.error_type
            
            if error_type not in stats.most_common_errors:
                stats.most_common_errors[error_type] = 0
            stats.most_common_errors[error_type] += 1
    
    async def _initialize_integration_retry(self, integration_name: str) -> None:
        """Initialize retry configuration for new integration."""
        if integration_name not in self.configs:
            self.configs[integration_name] = RetryConfig(integration_name=integration_name)
        
        if integration_name not in self.stats:
            self.stats[integration_name] = RetryStats()
    
    async def configure_retry(
        self,
        integration_name: str,
        max_attempts: Optional[int] = None,
        base_delay: Optional[float] = None,
        max_delay: Optional[float] = None,
        strategy: Optional[RetryStrategy] = None,
        backoff_multiplier: Optional[float] = None,
        jitter_type: Optional[JitterType] = None,
        **kwargs
    ) -> bool:
        """Configure retry settings for integration."""
        try:
            if integration_name not in self.configs:
                await self._initialize_integration_retry(integration_name)
            
            config = self.configs[integration_name]
            
            # Update configuration
            if max_attempts is not None:
                config.max_attempts = max_attempts
            if base_delay is not None:
                config.base_delay = base_delay
            if max_delay is not None:
                config.max_delay = max_delay
            if strategy is not None:
                config.strategy = strategy
            if backoff_multiplier is not None:
                config.backoff_multiplier = backoff_multiplier
            if jitter_type is not None:
                config.jitter_type = jitter_type
            
            # Update additional properties
            for key, value in kwargs.items():
                if hasattr(config, key):
                    setattr(config, key, value)
            
            self.logger.info(f"Retry configuration updated for {integration_name}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error configuring retry for {integration_name}: {str(e)}")
            return False
    
    async def get_retry_status(self, integration_name: str) -> Dict[str, Any]:
        """Get retry status for integration."""
        if integration_name not in self.configs:
            return {"error": "Integration not configured"}
        
        config = self.configs[integration_name]
        stats = self.stats[integration_name]
        
        # Count active sessions for this integration
        active_sessions_count = len([
            s for s in self.active_sessions.values()
            if s.integration_name == integration_name
        ])
        
        return {
            "integration_name": integration_name,
            "configuration": {
                "enabled": config.enabled,
                "max_attempts": config.max_attempts,
                "base_delay": config.base_delay,
                "max_delay": config.max_delay,
                "strategy": config.strategy.value,
                "backoff_multiplier": config.backoff_multiplier,
                "jitter_type": config.jitter_type.value,
                "retry_on_status_codes": config.retry_on_status_codes,
                "stop_on_status_codes": config.stop_on_status_codes
            },
            "statistics": {
                "total_sessions": stats.total_sessions,
                "successful_retries": stats.successful_retries,
                "failed_retries": stats.failed_retries,
                "total_attempts": stats.total_attempts,
                "success_rate_after_retry": round(stats.success_rate_after_retry, 2),
                "average_attempts_per_session": round(stats.average_attempts_per_session, 2),
                "average_total_delay": round(stats.average_total_delay, 2),
                "most_common_errors": dict(list(stats.most_common_errors.items())[:5])  # Top 5
            },
            "active_sessions": active_sessions_count,
            "max_concurrent_retries": self.max_concurrent_retries
        }
    
    async def get_all_retry_status(self) -> Dict[str, Any]:
        """Get retry status for all integrations."""
        all_status = {}
        
        for integration_name in self.configs:
            all_status[integration_name] = await self.get_retry_status(integration_name)
        
        # Calculate global statistics
        total_sessions = sum(status["statistics"]["total_sessions"] for status in all_status.values())
        successful_retries = sum(status["statistics"]["successful_retries"] for status in all_status.values())
        total_attempts = sum(status["statistics"]["total_attempts"] for status in all_status.values())
        total_active_sessions = len(self.active_sessions)
        
        global_success_rate = (successful_retries / total_sessions * 100) if total_sessions > 0 else 0
        
        return {
            "integrations": all_status,
            "global_statistics": {
                "total_integrations": len(self.configs),
                "total_sessions": total_sessions,
                "successful_retries": successful_retries,
                "total_attempts": total_attempts,
                "global_success_rate": round(global_success_rate, 2),
                "active_sessions": total_active_sessions,
                "completed_sessions_history": len(self.completed_sessions)
            }
        }
    
    async def get_session_details(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get details of specific retry session."""
        # Check active sessions first
        session = self.active_sessions.get(session_id)
        
        # Check completed sessions if not found in active
        if not session:
            session = next(
                (s for s in self.completed_sessions if s.id == session_id),
                None
            )
        
        if not session:
            return None
        
        return {
            "id": session.id,
            "integration_name": session.integration_name,
            "original_request": session.original_request,
            "started_at": session.started_at.isoformat(),
            "completed_at": session.completed_at.isoformat() if session.completed_at else None,
            "final_success": session.final_success,
            "total_delay": round(session.total_delay, 2),
            "attempts": [
                {
                    "attempt_number": attempt.attempt_number,
                    "timestamp": attempt.timestamp.isoformat(),
                    "delay_before_attempt": round(attempt.delay_before_attempt, 2),
                    "error_type": attempt.error_type,
                    "error_message": attempt.error_message,
                    "status_code": attempt.status_code,
                    "success": attempt.success
                }
                for attempt in session.attempts
            ],
            "configuration": {
                "max_attempts": session.config.max_attempts,
                "strategy": session.config.strategy.value,
                "base_delay": session.config.base_delay,
                "max_delay": session.config.max_delay
            }
        }
    
    async def cancel_retry_session(self, session_id: str) -> bool:
        """Cancel active retry session."""
        try:
            if session_id in self.active_sessions:
                session = self.active_sessions[session_id]
                await self._complete_session(session, False)
                
                self.logger.info(f"Retry session {session_id} cancelled")
                return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"Error cancelling retry session {session_id}: {str(e)}")
            return False
    
    async def enable_retry(self, integration_name: str) -> bool:
        """Enable retry for integration."""
        try:
            if integration_name not in self.configs:
                await self._initialize_integration_retry(integration_name)
            
            self.configs[integration_name].enabled = True
            self.logger.info(f"Retry enabled for {integration_name}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error enabling retry for {integration_name}: {str(e)}")
            return False
    
    async def disable_retry(self, integration_name: str) -> bool:
        """Disable retry for integration."""
        try:
            if integration_name in self.configs:
                self.configs[integration_name].enabled = False
                self.logger.info(f"Retry disabled for {integration_name}")
                return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"Error disabling retry for {integration_name}: {str(e)}")
            return False
    
    async def cleanup_old_sessions(self, hours: int = 24) -> int:
        """Clean up old completed sessions."""
        try:
            cutoff_time = datetime.utcnow() - timedelta(hours=hours)
            
            # Remove old completed sessions
            initial_count = len(self.completed_sessions)
            self.completed_sessions = [
                session for session in self.completed_sessions
                if session.completed_at and session.completed_at >= cutoff_time
            ]
            
            # Check for stuck active sessions
            stuck_sessions = []
            for session_id, session in self.active_sessions.items():
                if (datetime.utcnow() - session.started_at).total_seconds() > self.session_timeout:
                    stuck_sessions.append(session_id)
            
            # Cancel stuck sessions
            for session_id in stuck_sessions:
                await self.cancel_retry_session(session_id)
            
            cleaned_count = initial_count - len(self.completed_sessions) + len(stuck_sessions)
            
            self.logger.info(f"Cleaned up {cleaned_count} old retry sessions")
            return cleaned_count
            
        except Exception as e:
            self.logger.error(f"Error cleaning up old sessions: {str(e)}")
            return 0
    
    async def shutdown(self) -> None:
        """Shutdown retry handler."""
        self.logger.info("Shutting down retry handler...")
        
        # Cancel all active sessions
        active_session_ids = list(self.active_sessions.keys())
        for session_id in active_session_ids:
            await self.cancel_retry_session(session_id)
        
        # Clear data
        self.active_sessions.clear()
        self.completed_sessions.clear()
        
        self.logger.info("Retry handler shutdown complete")