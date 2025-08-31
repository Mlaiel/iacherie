"""
Notification Service - Core Business Logic Service for Multi-Channel Notifications

Enterprise-grade notification service providing comprehensive business logic integration
for the IA Influencer Agent platform. Handles content creators, AI protection,
collaboration matching, monetization opportunities, and multi-platform distribution.

Key Features:
- Multi-format content creator support (musicians, bloggers, photographers, influencers, comedians)
- AI-powered content protection notification workflows
- Intelligent collaboration matching and opportunity alerts
- Revenue optimization and monetization notifications
- SEO professional notifications and performance tracking
- Multi-platform distribution status management

Business Logic Flow:
1. Content Creator Upload → AI Analysis → Protection Rights Check → Notification Trigger
2. Collaboration Detection → Match Scoring → Opportunity Notification → Follow-up
3. SEO Analysis → Optimization Recommendations → Performance Alerts
4. Monetization Analysis → Revenue Opportunities → Monetization Alerts

Architecture:
- Service Layer: Business logic coordination and orchestration
- Engine Layer: Core notification processing and delivery
- Processor Layer: Business-specific notification handling
- Channel Layer: Multi-channel delivery optimization

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.
"""

from typing import Dict, List, Optional, Any, Union, Tuple
import logging
import asyncio
from datetime import datetime, timezone
from dataclasses import dataclass
from enum import Enum

from .notification_engine import NotificationEngine
from .notification_models import (
    NotificationRequest,
    NotificationResponse,
    NotificationMetrics,
    DeliveryStatus,
    BusinessRules
)
from .config import NotificationConfig
from .constants import NOTIFICATION_TYPES, PRIORITY_LEVELS, BUSINESS_RULES
from .processors import (
    ContentProtectionProcessor,
    CollaborationProcessor,
    MonetizationProcessor,
    SEOProcessor,
    DistributionProcessor
)

logger = logging.getLogger(__name__)


class NotificationServiceError(Exception):
    """Custom exception for notification service errors."""
    pass


class NotificationService:
    """
    Core notification service for IA Influencer Agent business logic.
    
    Provides enterprise-grade notification management with AI-powered features,
    multi-channel delivery, workflow orchestration, and comprehensive analytics.
    """
    
    def __init__(
        self,
        engine: NotificationEngine,
        processors: Dict[str, Any],
        config: NotificationConfig
    ):
        """
        Initialize notification service with business logic components.
        
        Args:
            engine: Core notification processing engine
            processors: Business-specific notification processors
            config: Notification configuration
        """
        self.engine = engine
        self.processors = processors
        self.config = config
        self.business_rules = BUSINESS_RULES
        
        # Service state
        self._active_workflows: Dict[str, Any] = {}
        self._metrics_cache: Dict[str, NotificationMetrics] = {}
        self._service_health = {
            "status": "healthy",
            "last_check": datetime.now(timezone.utc),
            "processed_notifications": 0,
            "failed_notifications": 0,
            "average_processing_time": 0.0
        }
        
        logger.info("NotificationService initialized with business processors")
    
    async def send_notification(
        self,
        request: NotificationRequest,
        business_context: Optional[Dict[str, Any]] = None
    ) -> NotificationResponse:
        """
        Send notification with business logic processing.
        
        Args:
            request: Notification request with recipient, content, and metadata
            business_context: Optional business context for enhanced processing
        
        Returns:
            Notification response with delivery status and metadata
        
        Raises:
            NotificationServiceError: If notification processing fails
        """



        try:
            start_time = datetime.now(timezone.utc)
            
            # Validate request
            if not self._validate_request(request):
                raise NotificationServiceError("Invalid notification request")
            
            # Apply business rules
            enhanced_request = await self._apply_business_rules(request, business_context)
            
            # Process through appropriate business processor
            processed_request = await self._process_business_logic(enhanced_request)
            
            # Send through notification engine
            response = await self.engine.process_notification(processed_request)
            
            # Update metrics
            processing_time = (datetime.now(timezone.utc) - start_time).total_seconds()
            await self._update_metrics(request.notification_type, processing_time, response.status)
            
            logger.info(
                f"Notification sent successfully: {request.notification_id} "
                f"in {processing_time:.3f}s"
            )
            
            return response
            
        except Exception as e:
            logger.error(f"Failed to send notification {request.notification_id}: {e}")
            self._service_health["failed_notifications"] += 1
            raise NotificationServiceError(f"Notification processing failed: {e}")
    
    async def send_bulk_notifications(
        self,
        requests: List[NotificationRequest],
        business_context: Optional[Dict[str, Any]] = None,
        batch_size: int = 100
    ) -> List[NotificationResponse]:
        """
        Send multiple notifications with intelligent batching and optimization.
        
        Args:
            requests: List of notification requests
            business_context: Optional business context for enhanced processing
            batch_size: Maximum batch size for processing
        
        Returns:
            List of notification responses
        """



        try:
            responses = []
            
            # Process in batches
            for i in range(0, len(requests), batch_size):
                batch = requests[i:i + batch_size]
                
                # Process batch concurrently
                batch_tasks = [
                    self.send_notification(req, business_context)
                    for req in batch
                ]
                
                batch_responses = await asyncio.gather(*batch_tasks, return_exceptions=True)
                
                # Handle exceptions
                for response in batch_responses:
                    if isinstance(response, Exception):
                        logger.error(f"Bulk notification failed: {response}")
                        responses.append(NotificationResponse(
                            notification_id="failed",
                            status=DeliveryStatus.FAILED,
                            message=str(response),
                            timestamp=datetime.now(timezone.utc)
                        ))
                    else:
                        responses.append(response)
            
            logger.info(f"Bulk notification completed: {len(responses)} notifications processed")
            return responses
            
        except Exception as e:
            logger.error(f"Bulk notification processing failed: {e}")
            raise NotificationServiceError(f"Bulk processing failed: {e}")
    
    async def create_notification_workflow(
        self,
        workflow_type: str,
        steps: List[Dict[str, Any]],
        business_context: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Create and start a notification workflow for complex business processes.
        
        Args:
            workflow_type: Type of workflow (onboarding, protection, collaboration, etc.)
            steps: List of workflow steps with conditions and actions
            business_context: Business context for workflow execution
        
        Returns:
            Workflow ID for tracking
        """



        try:
            workflow_id = f"{workflow_type}_{datetime.now(timezone.utc).timestamp()}"
            
            # Create workflow configuration
            workflow_config = {
                "id": workflow_id,
                "type": workflow_type,
                "steps": steps,
                "business_context": business_context or {},
                "status": "active",
                "created_at": datetime.now(timezone.utc),
                "current_step": 0,
                "completed_steps": []
            }
            
            # Start workflow through engine
            if hasattr(self.engine, 'workflow_orchestrator') and self.engine.workflow_orchestrator:
                await self.engine.workflow_orchestrator.start_workflow(workflow_config)
            
            # Track active workflow
            self._active_workflows[workflow_id] = workflow_config
            
            logger.info(f"Notification workflow created: {workflow_id} ({workflow_type})")
            return workflow_id
            
        except Exception as e:
            logger.error(f"Failed to create workflow: {e}")
            raise NotificationServiceError(f"Workflow creation failed: {e}")
    
    async def get_workflow_status(self, workflow_id: str) -> Dict[str, Any]:
        """
        Get status of active notification workflow.
        
        Args:
            workflow_id: Workflow identifier
        
        Returns:
            Workflow status information
        """



        try:
            if workflow_id not in self._active_workflows:
                raise NotificationServiceError(f"Workflow not found: {workflow_id}")
            
            workflow = self._active_workflows[workflow_id]
            
            # Get detailed status from engine if available
            if hasattr(self.engine, 'workflow_orchestrator') and self.engine.workflow_orchestrator:
                detailed_status = await self.engine.workflow_orchestrator.get_workflow_status(workflow_id)
                workflow.update(detailed_status)
            
            return workflow
            
        except Exception as e:
            logger.error(f"Failed to get workflow status: {e}")
            raise NotificationServiceError(f"Workflow status retrieval failed: {e}")
    
    async def get_notification_metrics(
        self,
        notification_type: Optional[str] = None,
        time_period: Optional[str] = "24h"
    ) -> NotificationMetrics:
        """
        Get comprehensive notification metrics and analytics.
        
        Args:
            notification_type: Optional filter by notification type
            time_period: Time period for metrics (1h, 24h, 7d, 30d)
        
        Returns:
            Notification metrics and analytics
        """



        try:
            # Get metrics from analytics engine
            if hasattr(self.engine, 'analytics_engine') and self.engine.analytics_engine:
                metrics = await self.engine.analytics_engine.get_metrics(
                    notification_type=notification_type,
                    time_period=time_period
                )
            else:
                # Basic metrics from cache
                cache_key = f"{notification_type or 'all'}_{time_period}"
                metrics = self._metrics_cache.get(cache_key, NotificationMetrics(
                    total_sent=0,
                    successful_deliveries=0,
                    failed_deliveries=0,
                    average_processing_time=0.0,
                    channel_performance={},
                    business_metrics={}
                ))
            
            logger.debug(f"Retrieved metrics for {notification_type or 'all'} ({time_period})")
            return metrics
            
        except Exception as e:
            logger.error(f"Failed to get metrics: {e}")
            raise NotificationServiceError(f"Metrics retrieval failed: {e}")
    
    async def update_user_preferences(
        self,
        user_id: str,
        preferences: Dict[str, Any]
    ) -> bool:
        """
        Update user notification preferences with business rule validation.
        
        Args:
            user_id: User identifier
            preferences: Updated notification preferences
        
        Returns:
            True if update successful, False otherwise
        """



        try:
            # Validate preferences against business rules
            validated_preferences = self._validate_user_preferences(preferences)
            
            # Update through engine
            if hasattr(self.engine, 'subscription_manager'):
                success = await self.engine.subscription_manager.update_preferences(
                    user_id, validated_preferences
                )
            else:
                # Basic preference storage
                success = True
                logger.warning("No subscription manager available for preference updates")
            
            if success:
                logger.info(f"User preferences updated: {user_id}")
            else:
                logger.error(f"Failed to update preferences for user: {user_id}")
            
            return success
            
        except Exception as e:
            logger.error(f"Failed to update user preferences: {e}")
            return False
    
    async def get_service_health(self) -> Dict[str, Any]:
        """
        Get comprehensive service health status and diagnostics.
        
        Returns:
            Service health information
        """



        try:
            # Update health metrics
            self._service_health["last_check"] = datetime.now(timezone.utc)
            
            # Calculate success rate
            total_notifications = (
                self._service_health["processed_notifications"] +
                self._service_health["failed_notifications"]
            )
            
            if total_notifications > 0:
                success_rate = (
                    self._service_health["processed_notifications"] / total_notifications
                ) * 100
            else:
                success_rate = 100.0
            
            # Determine overall health status
            if success_rate >= 95.0:
                status = "healthy"
            elif success_rate >= 90.0:
                status = "warning"
            else:
                status = "critical"
            
            health_info = {
                **self._service_health,
                "success_rate": success_rate,
                "status": status,
                "engine_health": await self.engine.get_health_status() if hasattr(self.engine, 'get_health_status') else "unknown",
                "active_workflows": len(self._active_workflows),
                "processor_status": {
                    name: "healthy" for name in self.processors.keys()
                }
            }
            
            return health_info
            
        except Exception as e:
            logger.error(f"Failed to get service health: {e}")
            return {
                "status": "error",
                "message": str(e),
                "last_check": datetime.now(timezone.utc)
            }
    
    # Private methods
    
    def _validate_request(self, request: NotificationRequest) -> bool:
        """Validate notification request."""



        try:
            # Check required fields
            if not request.recipient or not request.notification_type:
                return False
            
            # Validate notification type
            if request.notification_type not in NOTIFICATION_TYPES:
                return False
            
            # Validate content
            if not request.content:
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Request validation error: {e}")
            return False
    
    async def _apply_business_rules(
        self,
        request: NotificationRequest,
        business_context: Optional[Dict[str, Any]]
    ) -> NotificationRequest:
        """Apply business rules to notification request."""



        try:
            # Get business rules for notification type
            rules = self.business_rules.get(request.notification_type, {})
            
            # Apply priority rules
            if "priority" in rules:
                request.priority = rules["priority"]
            
            # Apply channel selection rules
            if "notification_channels" in rules:
                request.channels = rules["notification_channels"]
            
            # Apply time-sensitive rules
            if rules.get("time_sensitive", False):
                request.delivery_time = "immediate"
            
            # Apply personalization level
            if "personalization_level" in rules:
                request.metadata = request.metadata or {}
                request.metadata["personalization_level"] = rules["personalization_level"]
            
            # Apply business context
            if business_context:
                request.metadata = request.metadata or {}
                request.metadata["business_context"] = business_context
            
            return request
            
        except Exception as e:
            logger.error(f"Failed to apply business rules: {e}")
            return request
    
    async def _process_business_logic(self, request: NotificationRequest) -> NotificationRequest:
        """Process notification through appropriate business processor."""



        try:
            # Determine processor based on notification type
            processor_map = {
                "content_protection": "content_protection",
                "copyright_infringement": "content_protection",
                "collaboration_match": "collaboration",
                "partnership_opportunity": "collaboration",
                "monetization_opportunity": "monetization",
                "revenue_alert": "monetization",
                "seo_optimization": "seo",
                "performance_alert": "seo",
                "distribution_status": "distribution",
                "platform_sync": "distribution"
            }
            
            processor_name = processor_map.get(request.notification_type)
            
            if processor_name and processor_name in self.processors:
                processor = self.processors[processor_name]
                request = await processor.process_notification(request)
            
            return request
            
        except Exception as e:
            logger.error(f"Business logic processing failed: {e}")
            return request
    
    async def _update_metrics(
        self,
        notification_type: str,
        processing_time: float,
        status: DeliveryStatus
    ):
        """Update notification metrics."""



        try:
            # Update service health
            if status == DeliveryStatus.DELIVERED:
                self._service_health["processed_notifications"] += 1
            else:
                self._service_health["failed_notifications"] += 1
            
            # Update average processing time
            total_notifications = (
                self._service_health["processed_notifications"] +
                self._service_health["failed_notifications"]
            )
            
            current_avg = self._service_health["average_processing_time"]
            self._service_health["average_processing_time"] = (
                (current_avg * (total_notifications - 1) + processing_time) /
                total_notifications
            )
            
            # Update analytics engine if available
            if hasattr(self.engine, 'analytics_engine') and self.engine.analytics_engine:
                await self.engine.analytics_engine.record_metric(
                    notification_type, processing_time, status
                )
            
        except Exception as e:
            logger.error(f"Failed to update metrics: {e}")
    
    def _validate_user_preferences(self, preferences: Dict[str, Any]) -> Dict[str, Any]:
        """Validate user preferences against business rules."""



        try:
            validated = {}
            
            # Validate channel preferences
            if "channels" in preferences:
                valid_channels = ["email", "sms", "push", "webhook"]
                validated["channels"] = {
                    k: v for k, v in preferences["channels"].items()
                    if k in valid_channels
                }
            
            # Validate notification type preferences
            if "notification_types" in preferences:
                validated["notification_types"] = {
                    k: v for k, v in preferences["notification_types"].items()
                    if k in NOTIFICATION_TYPES
                }
            
            # Validate delivery preferences
            if "delivery_preferences" in preferences:
                validated["delivery_preferences"] = preferences["delivery_preferences"]
            
            # Apply business rule constraints
            for notification_type, rules in self.business_rules.items():
                if rules.get("mandatory", False):
                    if "notification_types" not in validated:
                        validated["notification_types"] = {}
                    validated["notification_types"][notification_type] = True
            
            return validated
            
        except Exception as e:
            logger.error(f"Preference validation failed: {e}")
            return preferences
