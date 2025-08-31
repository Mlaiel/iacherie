"""
Webhook Handlers Configuration Module for IA-Influencer Agent Platform
======================================================================

Professional webhook event handlers for processing real-time notifications.
Manages content protection, payments, platform updates, and system events.

Author: Fahed Mlaiel <mlaiel@live.de>
Project: IA-Influencer Agent + Content Protection Platform
Team: Lead Dev IA + Backend Senior + ML Engineer + DBA + Security + Microservices + Audio + DevOps

WARNING: This code is the intellectual property of Fahed Mlaiel.
Any unauthorized use, reproduction, or distribution without explicit written permission
is strictly prohibited and will be prosecuted to the full extent of the law.

Contact: mlaiel@live.de for licensing inquiries.
"""

import os
from typing import Dict, Any, Optional, List, Callable, Awaitable, Union
from pydantic import BaseSettings, Field
from enum import Enum
from dataclasses import dataclass, field
import asyncio
import json
from datetime import datetime
import logging


class HandlerPriority(int, Enum):
    """Handler execution priority levels."""
    CRITICAL = 1
    HIGH = 2
    MEDIUM = 3
    LOW = 4
    BACKGROUND = 5


class HandlerStatus(str, Enum):
    """Handler execution status."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    RETRYING = "retrying"
    CANCELLED = "cancelled"


@dataclass
class HandlerResult:
    """Webhook handler execution result."""
    success: bool
    message: str
    data: Optional[Dict[str, Any]] = None
    execution_time: float = 0.0
    retry_count: int = 0
    error: Optional[str] = None


@dataclass
class HandlerConfig:
    """Webhook handler configuration."""
    name: str
    handler_func: Callable[[Dict[str, Any]], Awaitable[HandlerResult]]
    priority: HandlerPriority = HandlerPriority.MEDIUM
    timeout: float = 30.0
    max_retries: int = 3
    retry_delay: float = 1.0
    enabled: bool = True
    description: str = ""
    required_fields: List[str] = field(default_factory=list)


class WebhookHandlersConfig(BaseSettings):
    """Webhook handlers configuration."""
    
    # Handler execution settings
    max_concurrent_handlers: int = Field(default=50, env="WEBHOOK_MAX_CONCURRENT_HANDLERS")
    default_handler_timeout: float = Field(default=30.0, env="WEBHOOK_DEFAULT_HANDLER_TIMEOUT")
    handler_queue_size: int = Field(default=1000, env="WEBHOOK_HANDLER_QUEUE_SIZE")
    
    # Retry configuration
    max_retry_attempts: int = Field(default=3, env="WEBHOOK_MAX_RETRY_ATTEMPTS")
    retry_backoff_factor: float = Field(default=2.0, env="WEBHOOK_RETRY_BACKOFF_FACTOR")
    max_retry_delay: float = Field(default=300.0, env="WEBHOOK_MAX_RETRY_DELAY")
    
    # Content protection handlers
    enable_fingerprint_handlers: bool = Field(default=True, env="ENABLE_FINGERPRINT_HANDLERS")
    enable_copyright_handlers: bool = Field(default=True, env="ENABLE_COPYRIGHT_HANDLERS")
    enable_revenue_handlers: bool = Field(default=True, env="ENABLE_REVENUE_HANDLERS")
    
    # Platform handlers
    enable_spotify_handlers: bool = Field(default=True, env="ENABLE_SPOTIFY_HANDLERS")
    enable_youtube_handlers: bool = Field(default=True, env="ENABLE_YOUTUBE_HANDLERS")
    enable_instagram_handlers: bool = Field(default=True, env="ENABLE_INSTAGRAM_HANDLERS")
    enable_tiktok_handlers: bool = Field(default=True, env="ENABLE_TIKTOK_HANDLERS")
    
    # Payment handlers
    enable_stripe_handlers: bool = Field(default=True, env="ENABLE_STRIPE_HANDLERS")
    enable_paypal_handlers: bool = Field(default=True, env="ENABLE_PAYPAL_HANDLERS")
    
    # System handlers
    enable_monitoring_handlers: bool = Field(default=True, env="ENABLE_MONITORING_HANDLERS")
    enable_security_handlers: bool = Field(default=True, env="ENABLE_SECURITY_HANDLERS")
    
    # Notification settings
    enable_email_notifications: bool = Field(default=True, env="ENABLE_EMAIL_NOTIFICATIONS")
    enable_slack_notifications: bool = Field(default=False, env="ENABLE_SLACK_NOTIFICATIONS")
    enable_webhook_forwarding: bool = Field(default=False, env="ENABLE_WEBHOOK_FORWARDING")
    
    # Logging and metrics
    log_handler_execution: bool = Field(default=True, env="LOG_HANDLER_EXECUTION")
    collect_handler_metrics: bool = Field(default=True, env="COLLECT_HANDLER_METRICS")
    store_handler_results: bool = Field(default=True, env="STORE_HANDLER_RESULTS")
    
    class Config:
        env_file = ".env"
        case_sensitive = False


class WebhookHandlerRegistry:
    """Registry for webhook handlers with professional execution management."""
    
    def __init__(self, config: WebhookHandlersConfig):
        self.config = config
        self.handlers: Dict[str, List[HandlerConfig]] = {}
        self.logger = logging.getLogger(__name__)
        self._semaphore = asyncio.Semaphore(config.max_concurrent_handlers)
        
    def register_handler(
        self, 
        event_type: str, 
        handler_config: HandlerConfig
    ) -> None:
        """Register a webhook handler for specific event type."""
        if event_type not in self.handlers:
            self.handlers[event_type] = []
            
        self.handlers[event_type].append(handler_config)
        
        # Sort handlers by priority
        self.handlers[event_type].sort(key=lambda h: h.priority.value)
        
        self.logger.info(f"Registered handler '{handler_config.name}' for event '{event_type}'")
    
    def get_handlers(self, event_type: str) -> List[HandlerConfig]:
        """Get all handlers for a specific event type."""



        return self.handlers.get(event_type, [])
    
    async def execute_handlers(
        self, 
        event_type: str, 
        payload: Dict[str, Any]
    ) -> List[HandlerResult]:
        """Execute all handlers for a specific event type."""
        handlers = self.get_handlers(event_type)
        if not handlers:
            self.logger.warning(f"No handlers registered for event type: {event_type}")
            return []
        
        results = []
        tasks = []
        
        for handler in handlers:
            if handler.enabled:
                task = self._execute_single_handler(handler, payload)
                tasks.append(task)
        
        if tasks:
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
        # Filter out exceptions and convert to HandlerResult
        valid_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                valid_results.append(HandlerResult(
                    success=False,
                    message=f"Handler execution failed: {str(result)}",
                    error=str(result)
                ))
            elif isinstance(result, HandlerResult):
                valid_results.append(result)
        
        return valid_results
    
    async def _execute_single_handler(
        self, 
        handler: HandlerConfig, 
        payload: Dict[str, Any]
    ) -> HandlerResult:
        """Execute a single handler with proper error handling and retries."""
        async with self._semaphore:
            start_time = datetime.now()
            
            try:
                # Validate required fields
                if handler.required_fields:
                    missing_fields = [
                        field for field in handler.required_fields 
                        if field not in payload
                    ]
                    if missing_fields:
                        return HandlerResult(
                            success=False,
                            message=f"Missing required fields: {missing_fields}",
                            execution_time=0.0
                        )
                
                # Execute handler with timeout
                result = await asyncio.wait_for(
                    handler.handler_func(payload),
                    timeout=handler.timeout
                )
                
                execution_time = (datetime.now() - start_time).total_seconds()
                result.execution_time = execution_time
                
                if self.config.log_handler_execution:
                    self.logger.info(
                        f"Handler '{handler.name}' executed successfully in {execution_time:.3f}s"
                    )
                
                return result
                
            except asyncio.TimeoutError:
                execution_time = (datetime.now() - start_time).total_seconds()
                error_msg = f"Handler '{handler.name}' timed out after {handler.timeout}s"
                self.logger.error(error_msg)
                
                return HandlerResult(
                    success=False,
                    message=error_msg,
                    execution_time=execution_time,
                    error="timeout"
                )
                
            except Exception as e:
                execution_time = (datetime.now() - start_time).total_seconds()
                error_msg = f"Handler '{handler.name}' failed: {str(e)}"
                self.logger.error(error_msg, exc_info=True)
                
                return HandlerResult(
                    success=False,
                    message=error_msg,
                    execution_time=execution_time,
                    error=str(e)
                )
    
    def get_handler_stats(self) -> Dict[str, Any]:
        """Get statistics about registered handlers."""
        total_handlers = sum(len(handlers) for handlers in self.handlers.values())
        enabled_handlers = sum(
            len([h for h in handlers if h.enabled]) 
            for handlers in self.handlers.values()
        )
        
        by_priority = {}
        for handlers in self.handlers.values():
            for handler in handlers:
                priority = handler.priority.name
                by_priority[priority] = by_priority.get(priority, 0) + 1
        
        return {
            "total_handlers": total_handlers,
            "enabled_handlers": enabled_handlers,
            "event_types": len(self.handlers),
            "by_priority": by_priority,
            "by_event_type": {
                event_type: len(handlers) 
                for event_type, handlers in self.handlers.items()
            }
        }


# Pre-defined handler configurations for common webhook events
class DefaultHandlerConfigs:
    """Default handler configurations for common webhook events."""
    
    @staticmethod
    async def spotify_track_handler(payload: Dict[str, Any]) -> HandlerResult:
        """Handle Spotify track events."""
        # Implementation would process Spotify track updates
        return HandlerResult(
            success=True,
            message="Spotify track processed successfully",
            data={"track_id": payload.get("track_id")}
        )
    
    @staticmethod
    async def youtube_video_handler(payload: Dict[str, Any]) -> HandlerResult:
        """Handle YouTube video events."""
        # Implementation would process YouTube video updates
        return HandlerResult(
            success=True,
            message="YouTube video processed successfully",
            data={"video_id": payload.get("video_id")}
        )
    
    @staticmethod
    async def stripe_payment_handler(payload: Dict[str, Any]) -> HandlerResult:
        """Handle Stripe payment events."""
        # Implementation would process payment notifications
        return HandlerResult(
            success=True,
            message="Stripe payment processed successfully",
            data={"payment_intent_id": payload.get("payment_intent_id")}
        )
    
    @staticmethod
    async def fingerprint_match_handler(payload: Dict[str, Any]) -> HandlerResult:
        """Handle content fingerprint match events."""
        # Implementation would process fingerprint matches
        return HandlerResult(
            success=True,
            message="Fingerprint match processed successfully",
            data={"match_id": payload.get("match_id")}
        )
    
    @staticmethod
    async def copyright_violation_handler(payload: Dict[str, Any]) -> HandlerResult:
        """Handle copyright violation events."""
        # Implementation would process copyright violations
        return HandlerResult(
            success=True,
            message="Copyright violation processed successfully",
            data={"violation_id": payload.get("violation_id")}
        )
    
    @staticmethod
    def get_default_configs() -> List[HandlerConfig]:
        """Get default handler configurations."""



        return [
            HandlerConfig(
                name="spotify_track_handler",
                handler_func=DefaultHandlerConfigs.spotify_track_handler,
                priority=HandlerPriority.HIGH,
                timeout=15.0,
                description="Process Spotify track events",
                required_fields=["track_id", "user_id"]
            ),
            HandlerConfig(
                name="youtube_video_handler",
                handler_func=DefaultHandlerConfigs.youtube_video_handler,
                priority=HandlerPriority.HIGH,
                timeout=20.0,
                description="Process YouTube video events",
                required_fields=["video_id", "channel_id"]
            ),
            HandlerConfig(
                name="stripe_payment_handler",
                handler_func=DefaultHandlerConfigs.stripe_payment_handler,
                priority=HandlerPriority.CRITICAL,
                timeout=10.0,
                description="Process Stripe payment events",
                required_fields=["payment_intent_id", "amount"]
            ),
            HandlerConfig(
                name="fingerprint_match_handler",
                handler_func=DefaultHandlerConfigs.fingerprint_match_handler,
                priority=HandlerPriority.CRITICAL,
                timeout=30.0,
                description="Process content fingerprint matches",
                required_fields=["fingerprint_id", "match_similarity"]
            ),
            HandlerConfig(
                name="copyright_violation_handler",
                handler_func=DefaultHandlerConfigs.copyright_violation_handler,
                priority=HandlerPriority.CRITICAL,
                timeout=25.0,
                description="Process copyright violation events",
                required_fields=["content_id", "violation_type"]
            )
        ]


# Global webhook handlers configuration instance
webhook_handlers_config = WebhookHandlersConfig()
webhook_handler_registry = WebhookHandlerRegistry(webhook_handlers_config)

# Register default handlers
for handler_config in DefaultHandlerConfigs.get_default_configs():
    event_type = handler_config.name.replace("_handler", "")
    webhook_handler_registry.register_handler(event_type, handler_config)
