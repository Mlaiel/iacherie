"""
Notification Event Manager - Advanced Event-Driven Notification System

Enterprise-grade event management system for handling complex notification workflows,
event-driven triggers, business rule processing, and real-time notification orchestration
for the IA Influencer platform multi-format content creator ecosystem.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️  CRITICAL LEGAL NOTICE - INTELLECTUAL PROPERTY PROTECTION:
This code, concept, and intellectual property are the EXCLUSIVE PROPERTY of Fahed Mlaiel.

STRICTLY PROHIBITED WITHOUT EXPLICIT WRITTEN AUTHORIZATION:
- Copying, cloning, reproducing, or distributing this code
- Using concepts, methodologies, or approaches in other projects
- Commercial exploitation, monetization, or resale
- Reverse engineering, decompilation, or adaptation
- Creating derivative works based on this intellectual property

Contact for licensing inquiries: mlaiel@live.de

Violation of these terms will result in immediate legal action.
All usage is monitored, logged, and legally protected.

Team Specialties & Expertise:
- Lead AI Developer & Backend Senior Engineer: Fahed Mlaiel
- Machine Learning Engineer & Audio Processing Specialist
- Database Administrator & Security Expert
- Microservices Architect & DevOps Engineer
- AI Prompt Engineer & Content Protection Specialist
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union, Callable, Set
from enum import Enum
from dataclasses import dataclass, field
import json
import uuid
from abc import ABC, abstractmethod

from .notification_dispatcher import NotificationDispatcher, DispatchStrategy
from .priority_handler import PriorityHandler, UrgencyLevel
from ...core.events import EventBus, BaseEvent
from ...models.notification_models import NotificationModel, NotificationTrigger
from ...business.content_business import ContentBusinessLogic
from ...business.collaboration_business import CollaborationBusinessLogic
from ...business.monetization_business import MonetizationBusinessLogic


class NotificationEventType(Enum):
    """Comprehensive notification event types for IA Influencer business logic"""
    
    # Content Creator Events
    CONTENT_UPLOADED = "content_uploaded"
    CONTENT_PROCESSED = "content_processed"
    CONTENT_PROTECTED = "content_protected"
    CONTENT_DISTRIBUTED = "content_distributed"
    
    # AI Protection Events
    COPYRIGHT_DETECTED = "copyright_detected"
    INFRINGEMENT_ALERT = "infringement_alert"
    PROTECTION_ACTIVATED = "protection_activated"
    FINGERPRINT_GENERATED = "fingerprint_generated"
    
    # Collaboration Events
    COLLABORATION_MATCH_FOUND = "collaboration_match_found"
    COLLABORATION_REQUEST_RECEIVED = "collaboration_request_received"
    COLLABORATION_ACCEPTED = "collaboration_accepted"
    COLLABORATION_COMPLETED = "collaboration_completed"
    
    # Monetization Events
    REVENUE_OPPORTUNITY = "revenue_opportunity"
    PAYMENT_RECEIVED = "payment_received"
    EARNINGS_THRESHOLD_REACHED = "earnings_threshold_reached"
    MONETIZATION_MILESTONE = "monetization_milestone"
    
    # SEO and Distribution Events
    SEO_OPTIMIZATION_COMPLETE = "seo_optimization_complete"
    PLATFORM_DISTRIBUTION_COMPLETE = "platform_distribution_complete"
    ENGAGEMENT_SPIKE_DETECTED = "engagement_spike_detected"
    TRENDING_CONTENT_IDENTIFIED = "trending_content_identified"
    
    # User Engagement Events
    HIGH_ENGAGEMENT_DETECTED = "high_engagement_detected"
    USER_MILESTONE_REACHED = "user_milestone_reached"
    FOLLOWER_THRESHOLD_REACHED = "follower_threshold_reached"
    
    # System Events
    SYSTEM_MAINTENANCE = "system_maintenance"
    SECURITY_ALERT = "security_alert"
    PLATFORM_UPDATE = "platform_update"


class EventPriority(Enum):
    """Event priority levels for notification triggering"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    BACKGROUND = "background"


class EventProcessingStatus(Enum):
    """Event processing status tracking"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    RETRYING = "retrying"
    CANCELLED = "cancelled"


@dataclass
class NotificationEvent(BaseEvent):
    """Advanced notification event with rich business context"""
    event_type: NotificationEventType
    user_id: str
    priority: EventPriority
    business_context: Dict[str, Any] = field(default_factory=dict)
    content_metadata: Dict[str, Any] = field(default_factory=dict)
    ai_insights: Dict[str, Any] = field(default_factory=dict)
    collaboration_data: Dict[str, Any] = field(default_factory=dict)
    monetization_data: Dict[str, Any] = field(default_factory=dict)
    trigger_conditions: List[str] = field(default_factory=list)
    custom_attributes: Dict[str, Any] = field(default_factory=dict)


@dataclass
class EventRule:
    """Business rule for event-driven notification triggering"""
    rule_id: str
    event_types: List[NotificationEventType]
    conditions: List[Callable[[NotificationEvent], bool]]
    notification_template: str
    target_channels: List[str]
    priority_override: Optional[EventPriority] = None
    delay_seconds: int = 0
    batch_eligible: bool = False
    ai_personalization_enabled: bool = True


@dataclass
class EventProcessingResult:
    """Result of event processing with comprehensive details"""
    event_id: str
    processing_status: EventProcessingStatus
    notifications_triggered: List[str]
    processing_time_seconds: float
    rules_applied: List[str]
    errors: List[str] = field(default_factory=list)
    analytics_data: Dict[str, Any] = field(default_factory=dict)


class NotificationEventManager:
    """
    Advanced event-driven notification system with intelligent business rule processing
    
    Key Features:
    - Event-driven notification triggering with complex business rules
    - Multi-format content creator workflow integration
    - AI-powered content protection event handling
    - Collaboration matching and notification orchestration
    - Monetization opportunity detection and alerting
    - SEO optimization and distribution status management
    - Real-time event processing with intelligent batching
    - Comprehensive analytics and performance monitoring
    """
    
    def __init__(
        self,
        notification_dispatcher: NotificationDispatcher,
        priority_handler: PriorityHandler,
        event_bus: EventBus
    ):
        self.notification_dispatcher = notification_dispatcher
        self.priority_handler = priority_handler
        self.event_bus = event_bus
        
        self.logger = logging.getLogger(__name__)
        
        # Business logic integrations
        self.content_business = ContentBusinessLogic()
        self.collaboration_business = CollaborationBusinessLogic()
        self.monetization_business = MonetizationBusinessLogic()
        
        # Event processing state
        self._event_rules: Dict[str, EventRule] = {}
        self._event_queue: asyncio.Queue = asyncio.Queue()
        self._processing_semaphore = asyncio.Semaphore(100)  # Concurrency control
        
        # Analytics and monitoring
        self._event_metrics: Dict[str, Any] = {
            'events_processed': 0,
            'notifications_triggered': 0,
            'processing_errors': 0,
            'average_processing_time': 0.0,
            'rule_hit_rates': {}
        }
        
        # Initialize built-in business rules
        asyncio.create_task(self._initialize_business_rules())
        
        # Start event processing
        asyncio.create_task(self._start_event_processor())
    
    async def process_event(self, event: NotificationEvent) -> EventProcessingResult:
        """
        Process a notification event with business rule evaluation
        
        Args:
            event: The notification event to process
            
        Returns:
            Comprehensive processing result with triggered notifications
        """
        start_time = datetime.utcnow()
        processing_result = EventProcessingResult(
            event_id=event.event_id,
            processing_status=EventProcessingStatus.PROCESSING,
            notifications_triggered=[],
            processing_time_seconds=0.0,
            rules_applied=[]
        )
        
        try:
            # Enrich event with business context
            enriched_event = await self._enrich_event_with_business_context(event)
            
            # Evaluate applicable rules
            applicable_rules = await self._evaluate_event_rules(enriched_event)
            
            # Process each applicable rule
            for rule in applicable_rules:
                try:
                    notification_ids = await self._process_event_rule(
                        enriched_event, rule
                    )
                    processing_result.notifications_triggered.extend(notification_ids)
                    processing_result.rules_applied.append(rule.rule_id)
                    
                except Exception as e:
                    self.logger.error(f"Rule processing failed for {rule.rule_id}: {str(e)}")
                    processing_result.errors.append(f"Rule {rule.rule_id}: {str(e)}")
            
            # Update processing status
            processing_result.processing_status = (
                EventProcessingStatus.COMPLETED if not processing_result.errors
                else EventProcessingStatus.FAILED
            )
            
            # Calculate processing time
            processing_result.processing_time_seconds = (
                datetime.utcnow() - start_time
            ).total_seconds()
            
            # Update analytics
            await self._update_event_analytics(processing_result)
            
            return processing_result
            
        except Exception as e:
            self.logger.error(f"Event processing failed: {str(e)}")
            processing_result.processing_status = EventProcessingStatus.FAILED
            processing_result.errors.append(str(e))
            return processing_result
    
    async def register_event_rule(self, rule: EventRule) -> bool:
        """
        Register a new event-driven notification rule
        
        Args:
            rule: The event rule to register
            
        Returns:
            True if successfully registered
        """
        try:
            # Validate rule
            if not await self._validate_event_rule(rule):
                return False
            
            # Store rule
            self._event_rules[rule.rule_id] = rule
            
            self.logger.info(f"Event rule registered: {rule.rule_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to register rule {rule.rule_id}: {str(e)}")
            return False
    
    async def remove_event_rule(self, rule_id: str) -> bool:
        """Remove an event rule"""
        try:
            if rule_id in self._event_rules:
                del self._event_rules[rule_id]
                self.logger.info(f"Event rule removed: {rule_id}")
                return True
            return False
        except Exception as e:
            self.logger.error(f"Failed to remove rule {rule_id}: {str(e)}")
            return False
    
    async def _enrich_event_with_business_context(
        self, event: NotificationEvent
    ) -> NotificationEvent:
        """
        Enrich event with comprehensive business context for intelligent processing
        """
        # Content-related enrichment
        if event.event_type in [
            NotificationEventType.CONTENT_UPLOADED,
            NotificationEventType.CONTENT_PROCESSED,
            NotificationEventType.CONTENT_PROTECTED,
            NotificationEventType.CONTENT_DISTRIBUTED
        ]:
            content_context = await self.content_business.get_content_context(
                event.user_id, event.content_metadata
            )
            event.business_context.update(content_context)
        
        # Collaboration-related enrichment
        if event.event_type in [
            NotificationEventType.COLLABORATION_MATCH_FOUND,
            NotificationEventType.COLLABORATION_REQUEST_RECEIVED,
            NotificationEventType.COLLABORATION_ACCEPTED
        ]:
            collaboration_context = await self.collaboration_business.get_collaboration_context(
                event.user_id, event.collaboration_data
            )
            event.business_context.update(collaboration_context)
        
        # Monetization-related enrichment
        if event.event_type in [
            NotificationEventType.REVENUE_OPPORTUNITY,
            NotificationEventType.PAYMENT_RECEIVED,
            NotificationEventType.EARNINGS_THRESHOLD_REACHED
        ]:
            monetization_context = await self.monetization_business.get_monetization_context(
                event.user_id, event.monetization_data
            )
            event.business_context.update(monetization_context)
        
        return event
    
    async def _evaluate_event_rules(
        self, event: NotificationEvent
    ) -> List[EventRule]:
        """
        Evaluate which rules apply to the given event
        """
        applicable_rules = []
        
        for rule in self._event_rules.values():
            try:
                # Check if event type matches
                if event.event_type not in rule.event_types:
                    continue
                
                # Evaluate all conditions
                all_conditions_met = True
                for condition in rule.conditions:
                    if not await self._evaluate_condition(condition, event):
                        all_conditions_met = False
                        break
                
                if all_conditions_met:
                    applicable_rules.append(rule)
                    
            except Exception as e:
                self.logger.error(f"Rule evaluation failed for {rule.rule_id}: {str(e)}")
        
        return applicable_rules
    
    async def _process_event_rule(
        self, event: NotificationEvent, rule: EventRule
    ) -> List[str]:
        """
        Process a single event rule and trigger appropriate notifications
        """
        notification_ids = []
        
        try:
            # Create notification based on rule
            notification = await self._create_notification_from_rule(event, rule)
            
            # Apply delay if specified
            if rule.delay_seconds > 0:
                await asyncio.sleep(rule.delay_seconds)
            
            # Determine dispatch strategy
            dispatch_strategy = (
                DispatchStrategy.BATCH_OPTIMIZED if rule.batch_eligible
                else DispatchStrategy.INTELLIGENT_ROUTING
            )
            
            # Convert string channels to ChannelType
            from .channel_manager import ChannelType
            target_channels = [
                ChannelType(channel) for channel in rule.target_channels
                if channel in [ct.value for ct in ChannelType]
            ]
            
            # Dispatch notification
            dispatch_result = await self.notification_dispatcher.dispatch_notification(
                notification,
                target_channels=target_channels,
                strategy=dispatch_strategy
            )
            
            notification_ids.append(notification.id)
            
        except Exception as e:
            self.logger.error(f"Failed to process rule {rule.rule_id}: {str(e)}")
            raise
        
        return notification_ids
    
    async def _create_notification_from_rule(
        self, event: NotificationEvent, rule: EventRule
    ) -> NotificationModel:
        """
        Create a notification model from event and rule
        """
        # Determine priority
        priority = rule.priority_override or self._map_event_priority(event.priority)
        
        # Create notification
        notification = NotificationModel(
            id=str(uuid.uuid4()),
            user_id=event.user_id,
            notification_type=event.event_type.value,
            title=await self._generate_notification_title(event, rule),
            content=await self._generate_notification_content(event, rule),
            priority=priority,
            metadata={
                'event_id': event.event_id,
                'rule_id': rule.rule_id,
                'business_context': event.business_context,
                'ai_insights': event.ai_insights,
                'custom_attributes': event.custom_attributes
            }
        )
        
        return notification
    
    async def _initialize_business_rules(self):
        """
        Initialize built-in business rules for IA Influencer platform
        """
        # Content Upload Success Rule
        await self.register_event_rule(EventRule(
            rule_id="content_upload_success",
            event_types=[NotificationEventType.CONTENT_UPLOADED],
            conditions=[
                lambda event: event.business_context.get('upload_status') == 'success'
            ],
            notification_template="content_upload_success_template",
            target_channels=["email", "push_notification"],
            priority_override=EventPriority.HIGH
        ))
        
        # Copyright Infringement Alert Rule
        await self.register_event_rule(EventRule(
            rule_id="copyright_infringement_alert",
            event_types=[NotificationEventType.INFRINGEMENT_ALERT],
            conditions=[
                lambda event: event.business_context.get('confidence_score', 0) > 0.8
            ],
            notification_template="copyright_alert_template",
            target_channels=["email", "sms", "push_notification"],
            priority_override=EventPriority.CRITICAL,
            delay_seconds=0  # Immediate notification
        ))
        
        # Collaboration Match Rule
        await self.register_event_rule(EventRule(
            rule_id="collaboration_match_found",
            event_types=[NotificationEventType.COLLABORATION_MATCH_FOUND],
            conditions=[
                lambda event: event.collaboration_data.get('match_score', 0) > 0.75
            ],
            notification_template="collaboration_match_template",
            target_channels=["email", "push_notification"],
            priority_override=EventPriority.HIGH,
            batch_eligible=True
        ))
        
        # Revenue Opportunity Rule
        await self.register_event_rule(EventRule(
            rule_id="revenue_opportunity_alert",
            event_types=[NotificationEventType.REVENUE_OPPORTUNITY],
            conditions=[
                lambda event: event.monetization_data.get('potential_revenue', 0) > 100
            ],
            notification_template="revenue_opportunity_template",
            target_channels=["email", "push_notification"],
            priority_override=EventPriority.HIGH
        ))
        
        # High Engagement Detection Rule
        await self.register_event_rule(EventRule(
            rule_id="high_engagement_detected",
            event_types=[NotificationEventType.HIGH_ENGAGEMENT_DETECTED],
            conditions=[
                lambda event: event.business_context.get('engagement_score', 0) > 0.9
            ],
            notification_template="high_engagement_template",
            target_channels=["email", "push_notification"],
            priority_override=EventPriority.MEDIUM,
            batch_eligible=True
        ))
        
        # SEO Optimization Complete Rule
        await self.register_event_rule(EventRule(
            rule_id="seo_optimization_complete",
            event_types=[NotificationEventType.SEO_OPTIMIZATION_COMPLETE],
            conditions=[
                lambda event: event.business_context.get('optimization_improvements', 0) > 3
            ],
            notification_template="seo_optimization_template",
            target_channels=["email"],
            priority_override=EventPriority.MEDIUM,
            delay_seconds=300,  # 5-minute delay for batching
            batch_eligible=True
        ))
    
    async def _evaluate_condition(
        self, condition: Callable[[NotificationEvent], bool], event: NotificationEvent
    ) -> bool:
        """
        Safely evaluate a condition function
        """
        try:
            return condition(event)
        except Exception as e:
            self.logger.error(f"Condition evaluation failed: {str(e)}")
            return False
    
    async def _generate_notification_title(
        self, event: NotificationEvent, rule: EventRule
    ) -> str:
        """
        Generate appropriate notification title based on event and rule
        """
        title_templates = {
            NotificationEventType.CONTENT_UPLOADED: "Content Successfully Uploaded",
            NotificationEventType.INFRINGEMENT_ALERT: "Copyright Infringement Detected",
            NotificationEventType.COLLABORATION_MATCH_FOUND: "New Collaboration Opportunity",
            NotificationEventType.REVENUE_OPPORTUNITY: "New Revenue Opportunity Available",
            NotificationEventType.HIGH_ENGAGEMENT_DETECTED: "Your Content is Trending!",
            NotificationEventType.SEO_OPTIMIZATION_COMPLETE: "SEO Optimization Complete"
        }
        
        return title_templates.get(
            event.event_type, 
            f"IA Influencer Update - {event.event_type.value}"
        )
    
    async def _generate_notification_content(
        self, event: NotificationEvent, rule: EventRule
    ) -> str:
        """
        Generate appropriate notification content with business context
        """
        if event.event_type == NotificationEventType.CONTENT_UPLOADED:
            return (
                f"Your content has been successfully uploaded and is now being processed. "
                f"Content type: {event.content_metadata.get('content_type', 'Unknown')}. "
                f"Processing will complete shortly."
            )
        
        elif event.event_type == NotificationEventType.INFRINGEMENT_ALERT:
            confidence = event.business_context.get('confidence_score', 0) * 100
            return (
                f"Potential copyright infringement detected with {confidence:.1f}% confidence. "
                f"Content: {event.content_metadata.get('title', 'Unknown')}. "
                f"Take action to protect your intellectual property."
            )
        
        elif event.event_type == NotificationEventType.COLLABORATION_MATCH_FOUND:
            match_score = event.collaboration_data.get('match_score', 0) * 100
            collaborator_type = event.collaboration_data.get('collaborator_type', 'creator')
            return (
                f"We found a {match_score:.0f}% match with a {collaborator_type} "
                f"for potential collaboration. Review the opportunity in your dashboard."
            )
        
        elif event.event_type == NotificationEventType.REVENUE_OPPORTUNITY:
            potential_revenue = event.monetization_data.get('potential_revenue', 0)
            return (
                f"New monetization opportunity identified with potential revenue of ${potential_revenue:.2f}. "
                f"Check your dashboard for details and activation steps."
            )
        
        elif event.event_type == NotificationEventType.HIGH_ENGAGEMENT_DETECTED:
            engagement_score = event.business_context.get('engagement_score', 0) * 100
            return (
                f"Your content is performing exceptionally well with {engagement_score:.0f}% engagement! "
                f"Consider promoting it further or creating similar content."
            )
        
        return f"Update from IA Influencer platform regarding your {event.event_type.value}."
    
    def _map_event_priority(self, event_priority: EventPriority) -> str:
        """Map event priority to notification priority"""
        mapping = {
            EventPriority.CRITICAL: "critical",
            EventPriority.HIGH: "high",
            EventPriority.MEDIUM: "medium",
            EventPriority.LOW: "low",
            EventPriority.BACKGROUND: "low"
        }
        return mapping.get(event_priority, "medium")
    
    async def _validate_event_rule(self, rule: EventRule) -> bool:
        """Validate event rule configuration"""
        if not rule.rule_id or not rule.event_types:
            return False
        
        if not rule.notification_template or not rule.target_channels:
            return False
        
        return True
    
    async def _start_event_processor(self):
        """Start the background event processor"""
        while True:
            try:
                # Process events from queue
                if not self._event_queue.empty():
                    event = await self._event_queue.get()
                    asyncio.create_task(self._process_queued_event(event))
                
                # Small delay to prevent tight loop
                await asyncio.sleep(0.1)
                
            except Exception as e:
                self.logger.error(f"Event processor error: {str(e)}")
                await asyncio.sleep(1)
    
    async def _process_queued_event(self, event: NotificationEvent):
        """Process event from queue with concurrency control"""
        async with self._processing_semaphore:
            await self.process_event(event)
    
    async def _update_event_analytics(self, result: EventProcessingResult):
        """Update event processing analytics"""
        self._event_metrics['events_processed'] += 1
        self._event_metrics['notifications_triggered'] += len(result.notifications_triggered)
        
        if result.errors:
            self._event_metrics['processing_errors'] += 1
        
        # Update average processing time
        current_avg = self._event_metrics['average_processing_time']
        total_processed = self._event_metrics['events_processed']
        new_avg = ((current_avg * (total_processed - 1)) + result.processing_time_seconds) / total_processed
        self._event_metrics['average_processing_time'] = new_avg
        
        # Update rule hit rates
        for rule_id in result.rules_applied:
            if rule_id not in self._event_metrics['rule_hit_rates']:
                self._event_metrics['rule_hit_rates'][rule_id] = 0
            self._event_metrics['rule_hit_rates'][rule_id] += 1
    
    async def get_event_metrics(self) -> Dict[str, Any]:
        """Get comprehensive event processing metrics"""
        return self._event_metrics.copy()
    
    async def queue_event(self, event: NotificationEvent):
        """Queue an event for processing"""
        await self._event_queue.put(event)
