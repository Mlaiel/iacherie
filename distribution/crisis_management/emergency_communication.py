"""Emergency Communication - Crisis Communication Management

Enterprise-grade emergency communication system for crisis management.
Handles automated crisis communication, stakeholder notifications, and
coordinated response messaging across all platforms and channels.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
import time
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional, Any, Tuple, Union
from dataclasses import dataclass, field
from enum import Enum

import numpy as np
from pydantic import BaseModel, Field, validator


class CrisisLevel(str, Enum):
    """Crisis severity levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"
    EMERGENCY = "emergency"


class CommunicationType(str, Enum):
    """Types of emergency communications"""
    INTERNAL_ALERT = "internal_alert"
    PUBLIC_STATEMENT = "public_statement"
    STAKEHOLDER_NOTIFICATION = "stakeholder_notification"
    MEDIA_RESPONSE = "media_response"
    PLATFORM_NOTICE = "platform_notice"
    CUSTOMER_COMMUNICATION = "customer_communication"
    LEGAL_NOTICE = "legal_notice"
    REGULATORY_FILING = "regulatory_filing"


class MessagePriority(str, Enum):
    """Message priority levels"""
    IMMEDIATE = "immediate"
    URGENT = "urgent"
    HIGH = "high"
    NORMAL = "normal"
    LOW = "low"


class CommunicationChannel(str, Enum):
    """Communication channels"""
    EMAIL = "email"
    SMS = "sms"
    PUSH_NOTIFICATION = "push_notification"
    SOCIAL_MEDIA = "social_media"
    WEBSITE_BANNER = "website_banner"
    BLOG_POST = "blog_post"
    PRESS_RELEASE = "press_release"
    PHONE_CALL = "phone_call"
    VIDEO_MESSAGE = "video_message"
    LIVE_STREAM = "live_stream"


@dataclass
class Stakeholder:
    """Stakeholder information for crisis communication"""
    stakeholder_id: str
    name: str
    type: str  # "investor", "customer", "employee", "media", "regulator", "partner"
    contact_info: Dict[str, str]
    preferred_channels: List[CommunicationChannel]
    priority_level: MessagePriority
    language: str = "en"
    timezone: str = "UTC"
    special_requirements: List[str] = field(default_factory=list)


@dataclass
class CommunicationTemplate:
    """Template for crisis communications"""
    template_id: str
    communication_type: CommunicationType
    crisis_level: CrisisLevel
    subject_template: str
    message_template: str
    channels: List[CommunicationChannel]
    approval_required: bool = True
    auto_send_threshold: CrisisLevel = CrisisLevel.CRITICAL
    language_variants: Dict[str, str] = field(default_factory=dict)


@dataclass
class CommunicationMessage:
    """Individual communication message"""
    message_id: str
    crisis_id: str
    communication_type: CommunicationType
    channel: CommunicationChannel
    recipient: Stakeholder
    subject: str
    content: str
    priority: MessagePriority
    
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    scheduled_at: Optional[datetime] = None
    sent_at: Optional[datetime] = None
    delivered_at: Optional[datetime] = None
    read_at: Optional[datetime] = None
    
    status: str = "draft"  # draft, approved, scheduled, sent, delivered, read, failed
    approval_required: bool = True
    approved_by: Optional[str] = None
    approved_at: Optional[datetime] = None
    
    tracking_data: Dict[str, Any] = field(default_factory=dict)
    response_data: Dict[str, Any] = field(default_factory=dict)


@dataclass
class CommunicationPlan:
    """Comprehensive crisis communication plan"""
    plan_id: str
    crisis_id: str
    crisis_level: CrisisLevel
    crisis_description: str
    
    # Communication strategy
    key_messages: List[str]
    target_audiences: List[str]
    communication_objectives: List[str]
    
    # Stakeholder mapping
    stakeholder_groups: Dict[str, List[Stakeholder]]
    communication_timeline: Dict[str, datetime]
    
    # Message coordination
    planned_messages: List[CommunicationMessage]
    sent_messages: List[CommunicationMessage]
    
    # Approval workflow
    approval_chain: List[str]
    escalation_rules: Dict[str, Any]
    
    # Monitoring and metrics
    success_metrics: Dict[str, float]
    response_tracking: Dict[str, Any]
    
    # Status and metadata
    status: str = "active"  # active, paused, completed, cancelled
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


class EmergencyCommunication:
    """Enterprise emergency communication management system"""
    
    def __init__(self,
                 auto_approval_threshold: CrisisLevel = CrisisLevel.EMERGENCY,
                 max_response_time_minutes: int = 15,
                 enable_multi_language: bool = True,
                 enable_sentiment_monitoring: bool = True):
        
        self.auto_approval_threshold = auto_approval_threshold
        self.max_response_time_minutes = max_response_time_minutes
        self.enable_multi_language = enable_multi_language
        self.enable_sentiment_monitoring = enable_sentiment_monitoring
        
        # Communication infrastructure
        self.stakeholder_registry: Dict[str, Stakeholder] = {}
        self.communication_templates: Dict[str, CommunicationTemplate] = {}
        self.active_plans: Dict[str, CommunicationPlan] = {}
        self.message_queue: List[CommunicationMessage] = []
        
        # Communication channels
        self.channel_handlers = self._initialize_channel_handlers()
        self.translation_service = self._initialize_translation_service()
        self.approval_system = self._initialize_approval_system()
        
        # Monitoring and analytics
        self.sentiment_tracker = self._initialize_sentiment_tracker()
        self.response_monitor = self._initialize_response_monitor()
        self.effectiveness_analyzer = self._initialize_effectiveness_analyzer()
        
        # Performance tracking
        self.communication_stats = {
            "total_messages_sent": 0,
            "average_response_time_minutes": 0.0,
            "approval_rate": 0.0,
            "delivery_success_rate": 0.0,
            "stakeholder_satisfaction": 0.0
        }
        
        self.logger = logging.getLogger(__name__)
    
    def _initialize_channel_handlers(self) -> Dict[CommunicationChannel, Any]:
        """Initialize communication channel handlers"""
        return {
            CommunicationChannel.EMAIL: self._create_email_handler(),
            CommunicationChannel.SMS: self._create_sms_handler(),
            CommunicationChannel.PUSH_NOTIFICATION: self._create_push_handler(),
            CommunicationChannel.SOCIAL_MEDIA: self._create_social_media_handler(),
            CommunicationChannel.WEBSITE_BANNER: self._create_website_handler(),
            CommunicationChannel.BLOG_POST: self._create_blog_handler(),
            CommunicationChannel.PRESS_RELEASE: self._create_press_handler(),
            CommunicationChannel.PHONE_CALL: self._create_phone_handler(),
            CommunicationChannel.VIDEO_MESSAGE: self._create_video_handler(),
            CommunicationChannel.LIVE_STREAM: self._create_livestream_handler()
        }
    
    def _create_email_handler(self) -> Dict[str, Any]:
        """Create email communication handler"""
        return {
            "service": "enterprise_email_service",
            "delivery_time_seconds": 30,
            "delivery_rate": 0.98,
            "read_tracking": True,
            "html_support": True,
            "attachment_support": True
        }
    
    def _create_sms_handler(self) -> Dict[str, Any]:
        """Create SMS communication handler"""
        return {
            "service": "enterprise_sms_service",
            "delivery_time_seconds": 10,
            "delivery_rate": 0.95,
            "character_limit": 160,
            "unicode_support": True,
            "delivery_receipts": True
        }
    
    def _create_push_handler(self) -> Dict[str, Any]:
        """Create push notification handler"""
        return {
            "service": "push_notification_service",
            "delivery_time_seconds": 5,
            "delivery_rate": 0.92,
            "rich_content": True,
            "action_buttons": True,
            "click_tracking": True
        }
    
    def _create_social_media_handler(self) -> Dict[str, Any]:
        """Create social media communication handler"""
        return {
            "platforms": ["twitter", "facebook", "linkedin", "instagram"],
            "delivery_time_seconds": 60,
            "reach_amplification": True,
            "hashtag_optimization": True,
            "cross_posting": True
        }
    
    def _create_website_handler(self) -> Dict[str, Any]:
        """Create website banner handler"""
        return {
            "service": "website_banner_service",
            "display_time_seconds": 1,
            "visibility_tracking": True,
            "click_tracking": True,
            "responsive_design": True
        }
    
    def _create_blog_handler(self) -> Dict[str, Any]:
        """Create blog post handler"""
        return {
            "service": "blog_publishing_service",
            "seo_optimization": True,
            "social_sharing": True,
            "comment_management": True,
            "analytics_tracking": True
        }
    
    def _create_press_handler(self) -> Dict[str, Any]:
        """Create press release handler"""
        return {
            "service": "press_release_service",
            "media_distribution": True,
            "journalist_targeting": True,
            "pickup_tracking": True,
            "embargo_support": True
        }
    
    def _create_phone_handler(self) -> Dict[str, Any]:
        """Create phone call handler"""
        return {
            "service": "automated_calling_service",
            "text_to_speech": True,
            "call_recording": True,
            "callback_support": True,
            "multi_language": True
        }
    
    def _create_video_handler(self) -> Dict[str, Any]:
        """Create video message handler"""
        return {
            "service": "video_messaging_service",
            "auto_generation": True,
            "personalization": True,
            "subtitle_support": True,
            "analytics_tracking": True
        }
    
    def _create_livestream_handler(self) -> Dict[str, Any]:
        """Create live stream handler"""
        return {
            "service": "live_streaming_service",
            "multi_platform": True,
            "chat_moderation": True,
            "recording": True,
            "viewer_analytics": True
        }
    
    def _initialize_translation_service(self) -> Dict[str, Any]:
        """Initialize translation service for multi-language support"""
        return {
            "service": "enterprise_translation_ai",
            "supported_languages": 50,
            "real_time_translation": True,
            "context_aware": True,
            "cultural_adaptation": True,
            "quality_assurance": True
        }
    
    def _initialize_approval_system(self) -> Dict[str, Any]:
        """Initialize message approval system"""
        return {
            "workflow_engine": "approval_workflow_system",
            "role_based_approval": True,
            "escalation_rules": True,
            "auto_approval_rules": True,
            "audit_trail": True,
            "sla_monitoring": True
        }
    
    def _initialize_sentiment_tracker(self) -> Dict[str, Any]:
        """Initialize sentiment tracking system"""
        return {
            "real_time_monitoring": True,
            "multi_platform_tracking": True,
            "sentiment_analysis": "advanced_nlp",
            "emotion_detection": True,
            "trend_analysis": True,
            "alert_system": True
        }
    
    def _initialize_response_monitor(self) -> Dict[str, Any]:
        """Initialize response monitoring system"""
        return {
            "delivery_tracking": True,
            "engagement_tracking": True,
            "response_analysis": True,
            "feedback_collection": True,
            "effectiveness_metrics": True,
            "real_time_dashboard": True
        }
    
    def _initialize_effectiveness_analyzer(self) -> Dict[str, Any]:
        """Initialize communication effectiveness analyzer"""
        return {
            "message_impact_analysis": True,
            "audience_response_analysis": True,
            "channel_performance_analysis": True,
            "optimization_recommendations": True,
            "a_b_testing": True,
            "predictive_analytics": True
        }
    
    async def activate_emergency_communication(self,
                                             crisis_id: str,
                                             crisis_level: CrisisLevel,
                                             crisis_description: str,
                                             immediate_response_required: bool = True) -> CommunicationPlan:
        """Activate emergency communication protocol"""
        
        activation_start = time.time()
        
        try:
            # Create communication plan
            plan = await self._create_emergency_plan(crisis_id, crisis_level, crisis_description)
            
            # Identify stakeholders to notify
            stakeholders_to_notify = await self._identify_stakeholders_for_crisis(crisis_level, crisis_description)
            
            # Generate emergency messages
            emergency_messages = await self._generate_emergency_messages(
                plan, stakeholders_to_notify, immediate_response_required
            )
            
            # Process approval workflow
            if crisis_level >= self.auto_approval_threshold:
                # Auto-approve for critical emergencies
                approved_messages = await self._auto_approve_messages(emergency_messages)
            else:
                # Route through approval workflow
                approved_messages = await self._route_approval_workflow(emergency_messages)
            
            # Schedule and send immediate messages
            await self._send_immediate_messages(approved_messages)
            
            # Update plan with sent messages
            plan.sent_messages.extend(approved_messages)
            plan.status = "active"
            plan.updated_at = datetime.now(timezone.utc)
            
            # Store active plan
            self.active_plans[crisis_id] = plan
            
            # Initialize monitoring
            await self._initialize_crisis_monitoring(crisis_id)
            
            # Log activation
            activation_time = (time.time() - activation_start) * 1000
            self.logger.info(
                f"Emergency communication activated for crisis {crisis_id} "
                f"(level: {crisis_level}) in {activation_time:.2f}ms"
            )
            
            return plan
            
        except Exception as e:
            self.logger.error(f"Failed to activate emergency communication for crisis {crisis_id}: {e}")
            raise
    
    async def _create_emergency_plan(self,
                                   crisis_id: str,
                                   crisis_level: CrisisLevel,
                                   crisis_description: str) -> CommunicationPlan:
        """Create emergency communication plan"""
        
        plan_id = f"comm_plan_{crisis_id}_{int(time.time())}"
        
        # Generate key messages based on crisis
        key_messages = await self._generate_key_messages(crisis_level, crisis_description)
        
        # Identify target audiences
        target_audiences = self._identify_target_audiences(crisis_level)
        
        # Define communication objectives
        communication_objectives = self._define_communication_objectives(crisis_level, crisis_description)
        
        # Create communication timeline
        timeline = self._create_communication_timeline(crisis_level)
        
        # Set up approval chain
        approval_chain = self._determine_approval_chain(crisis_level)
        
        # Define success metrics
        success_metrics = self._define_success_metrics(crisis_level)
        
        plan = CommunicationPlan(
            plan_id=plan_id,
            crisis_id=crisis_id,
            crisis_level=crisis_level,
            crisis_description=crisis_description,
            key_messages=key_messages,
            target_audiences=target_audiences,
            communication_objectives=communication_objectives,
            stakeholder_groups={},  # Will be populated later
            communication_timeline=timeline,
            planned_messages=[],
            sent_messages=[],
            approval_chain=approval_chain,
            escalation_rules=self._create_escalation_rules(crisis_level),
            success_metrics=success_metrics,
            response_tracking={}
        )
        
        return plan
    
    async def _generate_key_messages(self, crisis_level: CrisisLevel, crisis_description: str) -> List[str]:
        """Generate key messages for crisis communication"""
        
        # Base messages by crisis level
        base_messages = {
            CrisisLevel.LOW: [
                "We are aware of the situation and are monitoring closely.",
                "We are taking appropriate measures to address the issue.",
                "We will provide updates as more information becomes available."
            ],
            CrisisLevel.MEDIUM: [
                "We are actively addressing the situation.",
                "We take this matter seriously and are committed to resolution.",
                "We are working with relevant parties to ensure proper handling.",
                "We will communicate updates regularly."
            ],
            CrisisLevel.HIGH: [
                "We are treating this as a high priority situation.",
                "We have activated our response protocols immediately.",
                "We are committed to transparency and will provide frequent updates.",
                "We take full responsibility for our part in this situation."
            ],
            CrisisLevel.CRITICAL: [
                "We are responding to this critical situation with our full resources.",
                "We have implemented immediate protective measures.",
                "We are working around the clock to resolve this issue.",
                "We will provide hourly updates until resolution."
            ],
            CrisisLevel.EMERGENCY: [
                "This is an emergency situation requiring immediate action.",
                "We have activated all emergency protocols.",
                "Public safety is our top priority.",
                "We are coordinating with emergency services and authorities."
            ]
        }
        
        key_messages = base_messages.get(crisis_level, base_messages[CrisisLevel.MEDIUM])
        
        # Customize messages based on crisis description
        if "security" in crisis_description.lower():
            key_messages.append("We are conducting a thorough security review.")
            key_messages.append("User data protection remains our highest priority.")
        
        if "service" in crisis_description.lower() or "outage" in crisis_description.lower():
            key_messages.append("We are working to restore normal service as quickly as possible.")
            key_messages.append("We apologize for any inconvenience this may cause.")
        
        if "financial" in crisis_description.lower():
            key_messages.append("We are taking immediate steps to protect stakeholder interests.")
            key_messages.append("We are cooperating fully with regulatory authorities.")
        
        return key_messages
    
    def _identify_target_audiences(self, crisis_level: CrisisLevel) -> List[str]:
        """Identify target audiences based on crisis level"""
        
        audience_mapping = {
            CrisisLevel.LOW: ["internal_team", "direct_stakeholders"],
            CrisisLevel.MEDIUM: ["internal_team", "direct_stakeholders", "customers"],
            CrisisLevel.HIGH: ["internal_team", "stakeholders", "customers", "media"],
            CrisisLevel.CRITICAL: ["all_stakeholders", "media", "customers", "regulators"],
            CrisisLevel.EMERGENCY: ["all_stakeholders", "media", "public", "authorities", "regulators"]
        }
        
        return audience_mapping.get(crisis_level, audience_mapping[CrisisLevel.MEDIUM])
    
    def _define_communication_objectives(self, crisis_level: CrisisLevel, crisis_description: str) -> List[str]:
        """Define communication objectives for the crisis"""
        
        base_objectives = [
            "Maintain stakeholder confidence",
            "Provide accurate and timely information",
            "Demonstrate control and competence",
            "Minimize reputational damage"
        ]
        
        if crisis_level >= CrisisLevel.HIGH:
            base_objectives.extend([
                "Reassure affected parties",
                "Show accountability and responsibility",
                "Coordinate with authorities if needed"
            ])
        
        if crisis_level >= CrisisLevel.CRITICAL:
            base_objectives.extend([
                "Ensure public safety messaging",
                "Maintain regulatory compliance",
                "Prevent panic or misinformation"
            ])
        
        return base_objectives
    
    def _create_communication_timeline(self, crisis_level: CrisisLevel) -> Dict[str, datetime]:
        """Create communication timeline based on crisis level"""
        
        now = datetime.now(timezone.utc)
        
        timeline_templates = {
            CrisisLevel.LOW: {
                "initial_response": now + timedelta(hours=2),
                "stakeholder_update": now + timedelta(hours=8),
                "follow_up": now + timedelta(days=1)
            },
            CrisisLevel.MEDIUM: {
                "initial_response": now + timedelta(hours=1),
                "stakeholder_update": now + timedelta(hours=4),
                "media_response": now + timedelta(hours=8),
                "follow_up": now + timedelta(hours=12)
            },
            CrisisLevel.HIGH: {
                "immediate_response": now + timedelta(minutes=30),
                "stakeholder_alert": now + timedelta(hours=2),
                "media_statement": now + timedelta(hours=4),
                "public_update": now + timedelta(hours=8),
                "follow_up": now + timedelta(hours=12)
            },
            CrisisLevel.CRITICAL: {
                "immediate_response": now + timedelta(minutes=15),
                "stakeholder_emergency_alert": now + timedelta(minutes=30),
                "media_statement": now + timedelta(hours=1),
                "public_statement": now + timedelta(hours=2),
                "regulatory_notification": now + timedelta(hours=4),
                "hourly_updates": now + timedelta(hours=1)
            },
            CrisisLevel.EMERGENCY: {
                "immediate_response": now + timedelta(minutes=5),
                "emergency_alert": now + timedelta(minutes=10),
                "authority_notification": now + timedelta(minutes=15),
                "public_emergency_notice": now + timedelta(minutes=30),
                "media_briefing": now + timedelta(hours=1),
                "continuous_updates": now + timedelta(minutes=30)
            }
        }
        
        return timeline_templates.get(crisis_level, timeline_templates[CrisisLevel.MEDIUM])
    
    def _determine_approval_chain(self, crisis_level: CrisisLevel) -> List[str]:
        """Determine approval chain based on crisis level"""
        
        approval_chains = {
            CrisisLevel.LOW: ["team_lead", "department_manager"],
            CrisisLevel.MEDIUM: ["department_manager", "communications_director"],
            CrisisLevel.HIGH: ["communications_director", "executive_team"],
            CrisisLevel.CRITICAL: ["executive_team", "ceo"],
            CrisisLevel.EMERGENCY: ["ceo"]  # Emergency auto-approval
        }
        
        return approval_chains.get(crisis_level, approval_chains[CrisisLevel.MEDIUM])
    
    def _define_success_metrics(self, crisis_level: CrisisLevel) -> Dict[str, float]:
        """Define success metrics for communication effectiveness"""
        
        base_metrics = {
            "message_delivery_rate": 0.95,
            "stakeholder_awareness": 0.90,
            "sentiment_neutrality": 0.70,
            "media_coverage_tone": 0.60
        }
        
        if crisis_level >= CrisisLevel.HIGH:
            base_metrics.update({
                "crisis_containment_speed": 0.80,
                "reputation_recovery_rate": 0.70,
                "stakeholder_confidence": 0.65
            })
        
        if crisis_level >= CrisisLevel.CRITICAL:
            base_metrics.update({
                "public_safety_awareness": 0.95,
                "regulatory_compliance": 1.00,
                "emergency_response_time": 0.90
            })
        
        return base_metrics
    
    def _create_escalation_rules(self, crisis_level: CrisisLevel) -> Dict[str, Any]:
        """Create escalation rules for communication plan"""
        
        return {
            "time_based_escalation": {
                "no_approval_minutes": 30,
                "no_response_minutes": 60,
                "escalation_chain": ["manager", "director", "executive", "ceo"]
            },
            "severity_escalation": {
                "media_attention_threshold": 100,  # mentions per hour
                "sentiment_decline_threshold": 0.3,
                "stakeholder_complaints_threshold": 50
            },
            "auto_escalation_triggers": [
                "regulatory_inquiry",
                "legal_action",
                "safety_concern",
                "data_breach"
            ]
        }
    
    async def _identify_stakeholders_for_crisis(self, 
                                              crisis_level: CrisisLevel, 
                                              crisis_description: str) -> Dict[str, List[Stakeholder]]:
        """Identify stakeholders to notify for the crisis"""
        
        stakeholder_groups = {}
        
        # Get all stakeholders by type
        all_stakeholders = self._get_stakeholders_by_type()
        
        # Determine which groups to notify based on crisis level
        notification_rules = {
            CrisisLevel.LOW: ["employees", "direct_partners"],
            CrisisLevel.MEDIUM: ["employees", "partners", "key_customers"],
            CrisisLevel.HIGH: ["employees", "partners", "customers", "investors", "media"],
            CrisisLevel.CRITICAL: ["employees", "partners", "customers", "investors", "media", "regulators"],
            CrisisLevel.EMERGENCY: ["all"]
        }
        
        groups_to_notify = notification_rules.get(crisis_level, ["employees", "partners"])
        
        if "all" in groups_to_notify:
            stakeholder_groups = all_stakeholders
        else:
            for group in groups_to_notify:
                if group in all_stakeholders:
                    stakeholder_groups[group] = all_stakeholders[group]
        
        # Filter by crisis-specific relevance
        if "security" in crisis_description.lower():
            # Prioritize customers and regulators for security issues
            if "customers" in stakeholder_groups:
                for stakeholder in stakeholder_groups["customers"]:
                    stakeholder.priority_level = MessagePriority.URGENT
        
        if "financial" in crisis_description.lower():
            # Prioritize investors and regulators for financial issues
            if "investors" in stakeholder_groups:
                for stakeholder in stakeholder_groups["investors"]:
                    stakeholder.priority_level = MessagePriority.IMMEDIATE
        
        return stakeholder_groups
    
    def _get_stakeholders_by_type(self) -> Dict[str, List[Stakeholder]]:
        """Get stakeholders organized by type"""
        
        stakeholder_groups = {}
        
        for stakeholder in self.stakeholder_registry.values():
            stakeholder_type = stakeholder.type
            if stakeholder_type not in stakeholder_groups:
                stakeholder_groups[stakeholder_type] = []
            stakeholder_groups[stakeholder_type].append(stakeholder)
        
        return stakeholder_groups
    
    async def _generate_emergency_messages(self,
                                         plan: CommunicationPlan,
                                         stakeholder_groups: Dict[str, List[Stakeholder]],
                                         immediate_response: bool) -> List[CommunicationMessage]:
        """Generate emergency messages for stakeholders"""
        
        messages = []
        message_counter = 1
        
        for group_name, stakeholders in stakeholder_groups.items():
            for stakeholder in stakeholders:
                
                # Determine message type and priority
                message_type = self._determine_message_type(stakeholder.type, plan.crisis_level)
                priority = self._determine_message_priority(stakeholder.type, plan.crisis_level, immediate_response)
                
                # Select appropriate channels
                channels = self._select_communication_channels(stakeholder, plan.crisis_level, immediate_response)
                
                for channel in channels:
                    # Generate message content
                    subject, content = await self._generate_message_content(
                        plan, stakeholder, message_type, channel
                    )
                    
                    # Create message
                    message = CommunicationMessage(
                        message_id=f"emerg_{plan.crisis_id}_{message_counter:04d}",
                        crisis_id=plan.crisis_id,
                        communication_type=message_type,
                        channel=channel,
                        recipient=stakeholder,
                        subject=subject,
                        content=content,
                        priority=priority,
                        approval_required=plan.crisis_level < self.auto_approval_threshold,
                        scheduled_at=datetime.now(timezone.utc) if immediate_response else None
                    )
                    
                    messages.append(message)
                    message_counter += 1
        
        return messages
    
    def _determine_message_type(self, stakeholder_type: str, crisis_level: CrisisLevel) -> CommunicationType:
        """Determine appropriate message type for stakeholder"""
        
        type_mapping = {
            "employee": CommunicationType.INTERNAL_ALERT,
            "customer": CommunicationType.CUSTOMER_COMMUNICATION,
            "investor": CommunicationType.STAKEHOLDER_NOTIFICATION,
            "media": CommunicationType.MEDIA_RESPONSE,
            "regulator": CommunicationType.REGULATORY_FILING,
            "partner": CommunicationType.STAKEHOLDER_NOTIFICATION
        }
        
        # Override for high-level crises
        if crisis_level >= CrisisLevel.CRITICAL:
            if stakeholder_type in ["customer", "public"]:
                return CommunicationType.PUBLIC_STATEMENT
        
        return type_mapping.get(stakeholder_type, CommunicationType.STAKEHOLDER_NOTIFICATION)
    
    def _determine_message_priority(self, 
                                  stakeholder_type: str, 
                                  crisis_level: CrisisLevel, 
                                  immediate_response: bool) -> MessagePriority:
        """Determine message priority"""
        
        if crisis_level >= CrisisLevel.EMERGENCY:
            return MessagePriority.IMMEDIATE
        elif crisis_level >= CrisisLevel.CRITICAL:
            return MessagePriority.URGENT
        elif immediate_response:
            return MessagePriority.HIGH
        else:
            return MessagePriority.NORMAL
    
    def _select_communication_channels(self, 
                                     stakeholder: Stakeholder, 
                                     crisis_level: CrisisLevel, 
                                     immediate_response: bool) -> List[CommunicationChannel]:
        """Select appropriate communication channels"""
        
        # Start with stakeholder preferences
        preferred_channels = stakeholder.preferred_channels.copy()
        
        # Add emergency channels for critical situations
        if crisis_level >= CrisisLevel.CRITICAL:
            if CommunicationChannel.SMS not in preferred_channels:
                preferred_channels.append(CommunicationChannel.SMS)
            if CommunicationChannel.EMAIL not in preferred_channels:
                preferred_channels.append(CommunicationChannel.EMAIL)
        
        # Add immediate channels for urgent response
        if immediate_response and crisis_level >= CrisisLevel.HIGH:
            if CommunicationChannel.PUSH_NOTIFICATION not in preferred_channels:
                preferred_channels.insert(0, CommunicationChannel.PUSH_NOTIFICATION)
        
        # Limit channels for efficiency
        return preferred_channels[:3]
    
    async def _generate_message_content(self,
                                      plan: CommunicationPlan,
                                      stakeholder: Stakeholder,
                                      message_type: CommunicationType,
                                      channel: CommunicationChannel) -> Tuple[str, str]:
        """Generate personalized message content"""
        
        # Find appropriate template
        template = self._find_communication_template(message_type, plan.crisis_level)
        
        if template:
            # Use template
            subject = template.subject_template
            content = template.message_template
        else:
            # Generate default content
            subject, content = self._generate_default_content(plan, message_type)
        
        # Personalize content
        subject = self._personalize_message(subject, stakeholder, plan)
        content = self._personalize_message(content, stakeholder, plan)
        
        # Adapt for channel
        subject, content = self._adapt_for_channel(subject, content, channel)
        
        # Translate if needed
        if stakeholder.language != "en" and self.enable_multi_language:
            subject = await self._translate_content(subject, stakeholder.language)
            content = await self._translate_content(content, stakeholder.language)
        
        return subject, content
    
    def _find_communication_template(self, 
                                   message_type: CommunicationType, 
                                   crisis_level: CrisisLevel) -> Optional[CommunicationTemplate]:
        """Find appropriate communication template"""
        
        for template in self.communication_templates.values():
            if (template.communication_type == message_type and 
                template.crisis_level == crisis_level):
                return template
        
        return None
    
    def _generate_default_content(self, 
                                plan: CommunicationPlan, 
                                message_type: CommunicationType) -> Tuple[str, str]:
        """Generate default message content"""
        
        subject_templates = {
            CommunicationType.INTERNAL_ALERT: f"URGENT: Crisis Response - {plan.crisis_id}",
            CommunicationType.PUBLIC_STATEMENT: f"Important Update Regarding Recent Events",
            CommunicationType.STAKEHOLDER_NOTIFICATION: f"Stakeholder Alert: {plan.crisis_description[:50]}...",
            CommunicationType.CUSTOMER_COMMUNICATION: f"Important Service Update",
            CommunicationType.MEDIA_RESPONSE: f"Statement Regarding {plan.crisis_description[:50]}..."
        }
        
        content_templates = {
            CommunicationType.INTERNAL_ALERT: f"""
We are currently managing a {plan.crisis_level.value} level crisis situation.

Key points:
{chr(10).join(f"• {msg}" for msg in plan.key_messages)}

Please refer to our crisis management protocols and await further instructions.
            """,
            CommunicationType.PUBLIC_STATEMENT: f"""
We want to inform you about a situation that has come to our attention.

{chr(10).join(plan.key_messages)}

We are committed to keeping you informed as the situation develops.
            """,
            CommunicationType.CUSTOMER_COMMUNICATION: f"""
We want to make you aware of a situation that may affect our services.

{chr(10).join(plan.key_messages)}

We apologize for any inconvenience and appreciate your patience.
            """
        }
        
        subject = subject_templates.get(message_type, f"Important Update - {plan.crisis_id}")
        content = content_templates.get(message_type, 
                                      f"We are addressing the situation: {plan.crisis_description}")
        
        return subject, content
    
    def _personalize_message(self, 
                           message: str, 
                           stakeholder: Stakeholder, 
                           plan: CommunicationPlan) -> str:
        """Personalize message with stakeholder information"""
        
        personalization_map = {
            "{stakeholder_name}": stakeholder.name,
            "{crisis_id}": plan.crisis_id,
            "{crisis_level}": plan.crisis_level.value.title(),
            "{timestamp}": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
        }
        
        for placeholder, value in personalization_map.items():
            message = message.replace(placeholder, value)
        
        return message
    
    def _adapt_for_channel(self, 
                         subject: str, 
                         content: str, 
                         channel: CommunicationChannel) -> Tuple[str, str]:
        """Adapt message content for specific communication channel"""
        
        if channel == CommunicationChannel.SMS:
            # Truncate for SMS character limit
            max_chars = self.channel_handlers[channel]["character_limit"]
            if len(content) > max_chars:
                content = content[:max_chars-3] + "..."
            subject = ""  # SMS doesn't use subjects
        
        elif channel == CommunicationChannel.SOCIAL_MEDIA:
            # Add hashtags and optimize for social media
            content += " #CrisisUpdate #Transparency"
            if len(content) > 280:  # Twitter limit
                content = content[:277] + "..."
        
        elif channel == CommunicationChannel.PUSH_NOTIFICATION:
            # Optimize for mobile push notifications
            if len(subject) > 50:
                subject = subject[:47] + "..."
            if len(content) > 200:
                content = content[:197] + "..."
        
        return subject, content
    
    async def _translate_content(self, content: str, target_language: str) -> str:
        """Translate content to target language"""
        
        # In production, this would use actual translation service
        # For demonstration, returning translated placeholder
        
        if target_language != "en":
            return f"[{target_language.upper()}] {content}"
        
        return content
    
    async def monitor_communication_effectiveness(self, crisis_id: str) -> Dict[str, Any]:
        """Monitor communication effectiveness for active crisis"""
        
        if crisis_id not in self.active_plans:
            raise ValueError(f"No active communication plan found for crisis {crisis_id}")
        
        plan = self.active_plans[crisis_id]
        
        # Collect message delivery metrics
        delivery_metrics = await self._collect_delivery_metrics(plan.sent_messages)
        
        # Analyze stakeholder response
        response_analysis = await self._analyze_stakeholder_response(plan)
        
        # Monitor sentiment and media coverage
        sentiment_analysis = await self._monitor_sentiment_trends(crisis_id)
        
        # Evaluate against success metrics
        effectiveness_score = self._calculate_effectiveness_score(
            plan, delivery_metrics, response_analysis, sentiment_analysis
        )
        
        # Generate recommendations
        recommendations = self._generate_optimization_recommendations(
            plan, delivery_metrics, response_analysis
        )
        
        monitoring_report = {
            "crisis_id": crisis_id,
            "monitoring_timestamp": datetime.now(timezone.utc),
            "delivery_metrics": delivery_metrics,
            "response_analysis": response_analysis,
            "sentiment_analysis": sentiment_analysis,
            "effectiveness_score": effectiveness_score,
            "success_metrics_status": self._evaluate_success_metrics(plan, effectiveness_score),
            "recommendations": recommendations,
            "next_actions": self._suggest_next_actions(plan, effectiveness_score)
        }
        
        return monitoring_report
    
    def get_communication_stats(self) -> Dict[str, Any]:
        """Get communication system performance statistics"""
        return self.communication_stats.copy()


# Factory function for easy instantiation
def create_emergency_communication(**kwargs) -> EmergencyCommunication:
    """Create and configure an EmergencyCommunication instance"""
    return EmergencyCommunication(**kwargs)