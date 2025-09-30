# WARNING: Potential SQL injection risk - use parameterized queries
"""
Crisis Communication Manager for PagerDuty - Ainflue Platform
Public communication and stakeholder notification during incidents

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️  AVERTISSEMENT LÉGAL:
© 2025 Fahed Mlaiel <mlaiel@live.de>
TOUS DROITS RÉSERVÉS

🚨 PROTECTION INTELLECTUELLE:
- Code propriétaire de Fahed Mlaiel
- Utilisation commerciale INTERDITE sans autorisation écrite
- Reverse engineering STRICTEMENT INTERDIT
- Distribution INTERDITE sans licence explicite
- Violation = Poursuites judiciaires automatiques
"""

import logging
import json
import asyncio
from typing import Dict, Any, List, Optional, Set
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from enum import Enum
import uuid
import hashlib
import re

logger = logging.getLogger(__name__)


class CrisisLevel(Enum):
    """Crisis severity levels"""
    MINOR = "minor"
    MODERATE = "moderate"
    MAJOR = "major"
    CRITICAL = "critical"
    CATASTROPHIC = "catastrophic"


class CommunicationChannel(Enum):
    """Communication channels for crisis messaging"""
    STATUS_PAGE = "status_page"
    EMAIL = "email"
    SMS = "sms"
    SOCIAL_MEDIA = "social_media"
    PUSH_NOTIFICATION = "push_notification"
    IN_APP_BANNER = "in_app_banner"
    BLOG_POST = "blog_post"
    PRESS_RELEASE = "press_release"
    SLACK = "slack"
    DISCORD = "discord"
    WEBSITE_BANNER = "website_banner"


class StakeholderType(Enum):
    """Types of stakeholders for communication"""
    CREATORS = "creators"
    BRANDS = "brands"
    USERS = "users"
    EMPLOYEES = "employees"
    INVESTORS = "investors"
    MEDIA = "media"
    REGULATORY = "regulatory"
    PARTNERS = "partners"
    LEGAL = "legal"
    TECHNICAL_TEAM = "technical_team"


class MessageType(Enum):
    """Types of crisis messages"""
    INITIAL_ALERT = "initial_alert"
    STATUS_UPDATE = "status_update"
    RESOLUTION_NOTICE = "resolution_notice"
    POST_MORTEM = "post_mortem"
    PREVENTIVE_ACTION = "preventive_action"
    APOLOGY = "apology"
    COMPENSATION_OFFER = "compensation_offer"


@dataclass
class StakeholderGroup:
    """Stakeholder group configuration"""
    group_id: str
    group_name: str
    stakeholder_type: StakeholderType
    priority_level: int
    preferred_channels: List[CommunicationChannel]
    contact_info: Dict[str, List[str]]
    escalation_threshold_minutes: int
    requires_approval: bool
    message_templates: Dict[str, str]
    language_preferences: List[str]
    timezone: str
    business_hours_only: bool


@dataclass
class CrisisMessage:
    """Crisis communication message"""
    message_id: str
    crisis_id: str
    message_type: MessageType
    stakeholder_groups: List[str]
    channels: List[CommunicationChannel]
    subject: str
    content: Dict[str, str]  # Language -> content mapping
    scheduled_time: datetime
    sent_time: Optional[datetime]
    approval_status: str
    approved_by: Optional[str]
    delivery_status: Dict[str, str]  # Channel -> status mapping
    engagement_metrics: Dict[str, Any]
    follow_up_required: bool
    expiry_time: Optional[datetime]
    metadata: Dict[str, Any]


@dataclass
class CrisisEvent:
    """Crisis event definition"""
    crisis_id: str
    title: str
    description: str
    crisis_level: CrisisLevel
    affected_services: List[str]
    affected_regions: List[str]
    estimated_impact: Dict[str, Any]
    start_time: datetime
    estimated_resolution: Optional[datetime]
    actual_resolution: Optional[datetime]
    status: str
    incident_commander: str
    communication_lead: str
    stakeholder_impact: Dict[StakeholderType, str]
    messages_sent: List[str]
    social_media_monitoring: Dict[str, Any]
    media_coverage: List[Dict[str, Any]]
    public_sentiment: Dict[str, float]


@dataclass
class SocialMediaPost:
    """Social media post for crisis communication"""
    post_id: str
    platform: str
    content: str
    media_attachments: List[str]
    scheduled_time: datetime
    posted_time: Optional[datetime]
    engagement_metrics: Dict[str, int]
    responses_received: List[Dict[str, Any]]
    escalated_comments: List[Dict[str, Any]]


class CrisisCommunicationManager:
    """
    Crisis communication management for Creator Economy incidents
    Handles public communication, stakeholder notifications, and media responses
    """
    
    def __init__(self, pagerduty_client=None):
        """Initialize crisis communication manager"""
        self.pagerduty_client = pagerduty_client
        self.active_crises = {}
        self.stakeholder_groups = {}
        self.message_templates = {}
        self.communication_history = {}
        self.social_media_monitors = {}
        
        # Initialize stakeholder groups and templates
        self._initialize_stakeholder_groups()
        self._initialize_message_templates()
        
        # Configuration
        self.config = {
            "auto_approval_threshold": "minor",
            "approval_timeout_minutes": 30,
            "escalation_intervals": [15, 30, 60, 120],  # minutes
            "social_media_monitoring": True,
            "sentiment_analysis": True,
            "multi_language_support": ["en", "fr", "de", "ar", "es"],
            "status_page_integration": True,
            "media_contact_threshold": "major"
        }
        
        logger.info("Crisis Communication Manager initialized")
    
    def _initialize_stakeholder_groups(self):
        """Initialize Creator Economy stakeholder groups"""
        
        # Content Creators
        self.stakeholder_groups["creators"] = StakeholderGroup(
            group_id="creators",
            group_name="Content Creators",
            stakeholder_type=StakeholderType.CREATORS,
            priority_level=1,
            preferred_channels=[
                CommunicationChannel.EMAIL,
                CommunicationChannel.IN_APP_BANNER,
                CommunicationChannel.PUSH_NOTIFICATION,
                CommunicationChannel.DISCORD
            ],
            contact_info={
                "email": ["creators@ainflue.com"],
                "discord": ["creator-alerts"],
                "push_tokens": []
            },
            escalation_threshold_minutes=15,
            requires_approval=False,
            message_templates={
                "initial_alert": "creator_incident_alert",
                "status_update": "creator_status_update",
                "resolution": "creator_resolution"
            },
            language_preferences=["en", "fr", "de", "ar", "es"],
            timezone="UTC",
            business_hours_only=False
        )
        
        # Brand Partners
        self.stakeholder_groups["brands"] = StakeholderGroup(
            group_id="brands",
            group_name="Brand Partners", 
            stakeholder_type=StakeholderType.BRANDS,
            priority_level=1,
            preferred_channels=[
                CommunicationChannel.EMAIL,
                CommunicationChannel.SLACK,
                CommunicationChannel.STATUS_PAGE
            ],
            contact_info={
                "email": ["partnerships@ainflue.com", "brands@ainflue.com"],
                "slack": ["#brand-partners", "#incident-updates"]
            },
            escalation_threshold_minutes=30,
            requires_approval=True,
            message_templates={
                "initial_alert": "brand_incident_alert",
                "status_update": "brand_status_update", 
                "resolution": "brand_resolution"
            },
            language_preferences=["en"],
            timezone="UTC",
            business_hours_only=True
        )
        
        # End Users
        self.stakeholder_groups["users"] = StakeholderGroup(
            group_id="users",
            group_name="Platform Users",
            stakeholder_type=StakeholderType.USERS,
            priority_level=2,
            preferred_channels=[
                CommunicationChannel.STATUS_PAGE,
                CommunicationChannel.IN_APP_BANNER,
                CommunicationChannel.SOCIAL_MEDIA
            ],
            contact_info={
                "status_page": ["https://status.ainflue.com"],
                "twitter": ["@AinfluePlatform"],
                "linkedin": ["ainflue-platform"]
            },
            escalation_threshold_minutes=60,
            requires_approval=True,
            message_templates={
                "initial_alert": "user_incident_alert",
                "status_update": "user_status_update",
                "resolution": "user_resolution"
            },
            language_preferences=["en", "fr", "de", "ar", "es"],
            timezone="UTC",
            business_hours_only=False
        )
        
        # Employees
        self.stakeholder_groups["employees"] = StakeholderGroup(
            group_id="employees",
            group_name="Ainflue Employees",
            stakeholder_type=StakeholderType.EMPLOYEES,
            priority_level=1,
            preferred_channels=[
                CommunicationChannel.SLACK,
                CommunicationChannel.EMAIL
            ],
            contact_info={
                "slack": ["#all-hands", "#incident-response"],
                "email": ["all@ainflue.com"]
            },
            escalation_threshold_minutes=5,
            requires_approval=False,
            message_templates={
                "initial_alert": "employee_incident_alert",
                "status_update": "employee_status_update",
                "resolution": "employee_resolution"
            },
            language_preferences=["en"],
            timezone="UTC",
            business_hours_only=False
        )
        
        # Investors
        self.stakeholder_groups["investors"] = StakeholderGroup(
            group_id="investors",
            group_name="Investors & Board",
            stakeholder_type=StakeholderType.INVESTORS,
            priority_level=1,
            preferred_channels=[
                CommunicationChannel.EMAIL
            ],
            contact_info={
                "email": ["investors@ainflue.com", "board@ainflue.com"]
            },
            escalation_threshold_minutes=60,
            requires_approval=True,
            message_templates={
                "initial_alert": "investor_incident_alert",
                "status_update": "investor_status_update",
                "resolution": "investor_resolution"
            },
            language_preferences=["en"],
            timezone="UTC",
            business_hours_only=True
        )
        
        # Media
        self.stakeholder_groups["media"] = StakeholderGroup(
            group_id="media",
            group_name="Media & Press",
            stakeholder_type=StakeholderType.MEDIA,
            priority_level=3,
            preferred_channels=[
                CommunicationChannel.PRESS_RELEASE,
                CommunicationChannel.EMAIL
            ],
            contact_info={
                "email": ["press@ainflue.com"],
                "press_contacts": ["techcrunch@tc.com", "verge@vox.com"]
            },
            escalation_threshold_minutes=120,
            requires_approval=True,
            message_templates={
                "initial_alert": "media_incident_statement",
                "status_update": "media_status_update",
                "resolution": "media_resolution"
            },
            language_preferences=["en"],
            timezone="UTC",
            business_hours_only=True
        )
    
    def _initialize_message_templates(self):
        """Initialize crisis communication templates"""
        
        # Creator incident templates
        self.message_templates["creator_incident_alert"] = {
            "en": {
                "subject": "⚠️ Platform Issue Affecting Creator Tools",
                "content": """
Dear Creator,

We're currently experiencing technical difficulties that may affect some creator features on the Ainflue platform. Our engineering team is actively working to resolve this issue.

**What's happening:** {incident_description}
**Services affected:** {affected_services}
**Estimated resolution:** {estimated_resolution}

We'll keep you updated as we work to restore full functionality. Thank you for your patience.

The Ainflue Team
                """.strip()
            },
            "fr": {
                "subject": "⚠️ Problème Technique Affectant les Outils Créateur",
                "content": """
Cher Créateur,

Nous rencontrons actuellement des difficultés techniques qui peuvent affecter certaines fonctionnalités créateur sur la plateforme Ainflue. Notre équipe d'ingénieurs travaille activement pour résoudre ce problème.

**Ce qui se passe:** {incident_description}
**Services affectés:** {affected_services}
**Résolution estimée:** {estimated_resolution}

Nous vous tiendrons informé pendant que nous travaillons à restaurer toutes les fonctionnalités. Merci pour votre patience.

L'équipe Ainflue
                """.strip()
            }
        }
        
        # Brand incident templates
        self.message_templates["brand_incident_alert"] = {
            "en": {
                "subject": "🔴 URGENT: Service Disruption - Ainflue Platform",
                "content": """
Dear Brand Partner,

We are experiencing a service disruption on the Ainflue platform that may impact collaboration campaigns and analytics reporting.

**Incident Details:**
- Issue: {incident_description}
- Impact: {brand_impact}
- Affected Features: {affected_services}
- ETA: {estimated_resolution}

**Immediate Actions:**
- Our incident response team is actively working on resolution
- Regular updates will be provided every 30 minutes
- Your account manager will reach out if specific campaigns are affected

We apologize for any inconvenience and appreciate your patience.

Best regards,
Ainflue Partnership Team
                """.strip()
            }
        }
        
        # User public templates
        self.message_templates["user_incident_alert"] = {
            "en": {
                "subject": "Service Update - Ainflue Platform",
                "content": """
We're currently experiencing technical issues that may affect your experience on Ainflue.

Our team is working to resolve this quickly. We'll provide updates as they become available.

For real-time updates: https://status.ainflue.com

Thank you for your patience.
                """.strip()
            }
        }
        
        # Employee templates
        self.message_templates["employee_incident_alert"] = {
            "en": {
                "subject": "🚨 INCIDENT: {incident_title}",
                "content": """
Team,

We have an active incident affecting our platform:

**Incident:** {incident_title}
**Severity:** {crisis_level}
**Impact:** {incident_description}
**Commander:** {incident_commander}
**Started:** {start_time}

**Next Steps:**
- All hands standby for potential escalation
- Customer Support team prepare for increased inquiries
- Marketing team hold all promotional activities

War room: #incident-response
Status updates: Every 15 minutes

Stay alert and ready to assist.
                """.strip()
            }
        }
        
        # Media templates
        self.message_templates["media_incident_statement"] = {
            "en": {
                "subject": "Ainflue Platform Statement - Service Issue",
                "content": """
FOR IMMEDIATE RELEASE

Ainflue Platform Statement on Current Service Issues

{date} - Ainflue, the leading Creator Economy platform, is currently addressing technical issues affecting some platform services. The company's engineering team is working to restore full functionality as quickly as possible.

"We take any service disruption extremely seriously," said {spokesperson}, {title} at Ainflue. "Our priority is restoring service to our creator community and brand partners while ensuring data security and platform integrity."

**Key Points:**
- Issue detected at {start_time}
- Affects: {affected_services}
- No data loss or security breach
- Estimated resolution: {estimated_resolution}
- Regular updates at https://status.ainflue.com

Ainflue serves over {creator_count} content creators and {brand_count} brand partners worldwide, facilitating authentic collaborations in the Creator Economy.

For media inquiries:
Press Team: press@ainflue.com
Phone: +1-555-AINFLUE

###
                """.strip()
            }
        }
    
    async def initiate_crisis_communication(self, incident_data: Dict[str, Any]) -> Optional[CrisisEvent]:
        """Initiate crisis communication workflow"""
        try:
            # Assess crisis level
            crisis_level = self._assess_crisis_level(incident_data)
            
            # Create crisis event
            crisis = CrisisEvent(
                crisis_id=str(uuid.uuid4()),
                title=incident_data.get("title", "Platform Incident"),
                description=incident_data.get("description", ""),
                crisis_level=crisis_level,
                affected_services=incident_data.get("affected_services", []),
                affected_regions=incident_data.get("affected_regions", ["global"]),
                estimated_impact=incident_data.get("estimated_impact", {}),
                start_time=datetime.utcnow(),
                estimated_resolution=incident_data.get("estimated_resolution"),
                actual_resolution=None,
                status="active",
                incident_commander=incident_data.get("incident_commander", "unknown"),
                communication_lead=incident_data.get("communication_lead", "communications@ainflue.com"),
                stakeholder_impact={},
                messages_sent=[],
                social_media_monitoring={},
                media_coverage=[],
                public_sentiment={}
            )
            
            # Store crisis
            self.active_crises[crisis.crisis_id] = crisis
            
            # Determine affected stakeholder groups
            affected_groups = self._determine_affected_stakeholders(crisis)
            
            # Calculate stakeholder impact
            await self._calculate_stakeholder_impact(crisis, affected_groups)
            
            # Start communication workflow
            await self._execute_communication_plan(crisis, affected_groups)
            
            # Start social media monitoring
            if self.config["social_media_monitoring"]:
                await self._start_social_media_monitoring(crisis)
            
            logger.info(f"Crisis communication initiated for {crisis.crisis_id}")
            return crisis
            
        except Exception as e:
            logger.error(f"Crisis communication initiation failed: {e}")
            return None
    
    def _assess_crisis_level(self, incident_data: Dict[str, Any]) -> CrisisLevel:
        """Assess crisis level based on incident data"""
        try:
            # Factors for crisis assessment
            affected_users = incident_data.get("affected_users", 0)
            revenue_impact = incident_data.get("revenue_impact_hourly", 0)
            service_count = len(incident_data.get("affected_services", []))
            security_breach = incident_data.get("security_breach", False)
            data_loss = incident_data.get("data_loss", False)
            
            # Crisis level scoring
            score = 0
            
            # User impact scoring
            if affected_users > 100000:
                score += 4
            elif affected_users > 50000:
                score += 3
            elif affected_users > 10000:
                score += 2
            elif affected_users > 1000:
                score += 1
            
            # Revenue impact scoring
            if revenue_impact > 10000:
                score += 4
            elif revenue_impact > 5000:
                score += 3
            elif revenue_impact > 1000:
                score += 2
            elif revenue_impact > 100:
                score += 1
            
            # Service impact scoring
            if service_count > 5:
                score += 3
            elif service_count > 3:
                score += 2
            elif service_count > 1:
                score += 1
            
            # Security and data impact
            if security_breach:
                score += 5
            if data_loss:
                score += 5
            
            # Map score to crisis level
            if score >= 15:
                return CrisisLevel.CATASTROPHIC
            elif score >= 12:
                return CrisisLevel.CRITICAL
            elif score >= 8:
                return CrisisLevel.MAJOR
            elif score >= 4:
                return CrisisLevel.MODERATE
            else:
                return CrisisLevel.MINOR
                
        except Exception as e:
            logger.error(f"Crisis level assessment failed: {e}")
            return CrisisLevel.MINOR
    
    def _determine_affected_stakeholders(self, crisis: CrisisEvent) -> List[str]:
        """Determine which stakeholder groups are affected"""
        affected_groups = []
        
        try:
            # Always notify employees
            affected_groups.append("employees")
            
            # Determine based on crisis level
            if crisis.crisis_level in [CrisisLevel.MAJOR, CrisisLevel.CRITICAL, CrisisLevel.CATASTROPHIC]:
                affected_groups.extend(["creators", "brands", "users"])
                
                if crisis.crisis_level in [CrisisLevel.CRITICAL, CrisisLevel.CATASTROPHIC]:
                    affected_groups.extend(["investors", "media"])
            
            elif crisis.crisis_level == CrisisLevel.MODERATE:
                affected_groups.extend(["creators", "brands"])
                
                # Check if users are directly affected
                if any(service in ["user_login", "content_viewing", "search"] 
                      for service in crisis.affected_services):
                    affected_groups.append("users")
            
            elif crisis.crisis_level == CrisisLevel.MINOR:
                # Only notify if specific services are affected
                if any(service in ["creator_dashboard", "content_upload"] 
                      for service in crisis.affected_services):
                    affected_groups.append("creators")
                
                if any(service in ["brand_dashboard", "campaign_management"] 
                      for service in crisis.affected_services):
                    affected_groups.append("brands")
            
            # Remove duplicates
            return list(set(affected_groups))
            
        except Exception as e:
            logger.error(f"Stakeholder determination failed: {e}")
            return ["employees"]
    
    async def _calculate_stakeholder_impact(self, crisis: CrisisEvent, affected_groups: List[str]):
        """Calculate impact on each stakeholder group"""
        try:
            for group_id in affected_groups:
                group = self.stakeholder_groups.get(group_id)
                if not group:
                    continue
                
                impact_description = ""
                
                if group.stakeholder_type == StakeholderType.CREATORS:
                    creator_services = [s for s in crisis.affected_services 
                                     if s in ["content_upload", "creator_dashboard", "analytics", "monetization"]]
                    if creator_services:
                        impact_description = f"Creator tools affected: {', '.join(creator_services)}"
                    else:
                        impact_description = "Potential indirect impact on creator workflow"
                
                elif group.stakeholder_type == StakeholderType.BRANDS:
                    brand_services = [s for s in crisis.affected_services 
                                    if s in ["brand_dashboard", "campaign_management", "analytics", "collaboration"]]
                    if brand_services:
                        impact_description = f"Brand features affected: {', '.join(brand_services)}"
                    else:
                        impact_description = "Potential impact on brand campaigns"
                
                elif group.stakeholder_type == StakeholderType.USERS:
                    user_services = [s for s in crisis.affected_services 
                                   if s in ["user_login", "content_viewing", "search", "recommendations"]]
                    if user_services:
                        impact_description = f"User experience affected: {', '.join(user_services)}"
                    else:
                        impact_description = "Limited impact on user experience"
                
                elif group.stakeholder_type == StakeholderType.EMPLOYEES:
                    impact_description = f"Platform incident requiring {crisis.crisis_level.value} response"
                
                elif group.stakeholder_type == StakeholderType.INVESTORS:
                    impact_description = f"Business continuity event - {crisis.crisis_level.value} severity"
                
                elif group.stakeholder_type == StakeholderType.MEDIA:
                    impact_description = f"Public platform incident requiring transparency"
                
                crisis.stakeholder_impact[group.stakeholder_type] = impact_description
                
        except Exception as e:
            logger.error(f"Stakeholder impact calculation failed: {e}")
    
    async def _execute_communication_plan(self, crisis: CrisisEvent, affected_groups: List[str]):
        """Execute communication plan for crisis"""
        try:
            communication_tasks = []
            
            for group_id in affected_groups:
                group = self.stakeholder_groups.get(group_id)
                if not group:
                    continue
                
                # Create initial alert message
                message = await self._create_crisis_message(
                    crisis, group, MessageType.INITIAL_ALERT
                )
                
                if message:
                    # Schedule immediate sending for high priority groups
                    if group.priority_level <= 1:
                        message.scheduled_time = datetime.utcnow()
                    else:
                        # Delay for lower priority groups
                        message.scheduled_time = datetime.utcnow() + timedelta(minutes=group.priority_level * 15)
                    
                    # Add to sending queue
                    task = self._send_crisis_message(message)
                    communication_tasks.append(task)
                    
                    crisis.messages_sent.append(message.message_id)
            
            # Execute communication tasks
            if communication_tasks:
                await asyncio.gather(*communication_tasks, return_exceptions=True)
            
            logger.info(f"Communication plan executed for crisis {crisis.crisis_id}")
            
        except Exception as e:
            logger.error(f"Communication plan execution failed: {e}")
    
    async def _create_crisis_message(self, crisis: CrisisEvent, 
                                   stakeholder_group: StakeholderGroup,
                                   message_type: MessageType) -> Optional[CrisisMessage]:
        """Create crisis message for stakeholder group"""
        try:
            # Get template
            template_key = stakeholder_group.message_templates.get(message_type.value)
            template = self.message_templates.get(template_key, {})
            
            if not template:
                logger.warning(f"No template found for {template_key}")
                return None
            
            # Create message content for each language
            message_content = {}
            
            for lang in stakeholder_group.language_preferences:
                if lang in template:
                    # Fill template variables
                    content = self._fill_template_variables(
                        template[lang]["content"], crisis, stakeholder_group
                    )
                    subject = self._fill_template_variables(
                        template[lang]["subject"], crisis, stakeholder_group
                    )
                    
                    message_content[lang] = {
                        "subject": subject,
                        "content": content
                    }
            
            if not message_content:
                return None
            
            # Determine channels based on crisis level and group preferences
            channels = self._select_communication_channels(crisis, stakeholder_group)
            
            message = CrisisMessage(
                message_id=str(uuid.uuid4()),
                crisis_id=crisis.crisis_id,
                message_type=message_type,
                stakeholder_groups=[stakeholder_group.group_id],
                channels=channels,
                subject=list(message_content.values())[0]["subject"],
                content=message_content,
                scheduled_time=datetime.utcnow(),
                sent_time=None,
                approval_status="pending" if stakeholder_group.requires_approval else "approved",
                approved_by=None,
                delivery_status={},
                engagement_metrics={},
                follow_up_required=crisis.crisis_level in [CrisisLevel.MAJOR, CrisisLevel.CRITICAL],
                expiry_time=datetime.utcnow() + timedelta(hours=24),
                metadata={
                    "crisis_level": crisis.crisis_level.value,
                    "stakeholder_type": stakeholder_group.stakeholder_type.value
                }
            )
            
            return message
            
        except Exception as e:
            logger.error(f"Crisis message creation failed: {e}")
            return None
    
    def _fill_template_variables(self, template: str, crisis: CrisisEvent, 
                               stakeholder_group: StakeholderGroup) -> str:
        """Fill template variables with crisis data"""
        try:
            variables = {
                "incident_title": crisis.title,
                "incident_description": crisis.description,
                "crisis_level": crisis.crisis_level.value.upper(),
                "affected_services": ", ".join(crisis.affected_services),
                "estimated_resolution": crisis.estimated_resolution.strftime("%H:%M UTC") if crisis.estimated_resolution else "Unknown",
                "start_time": crisis.start_time.strftime("%H:%M UTC"),
                "incident_commander": crisis.incident_commander,
                "date": datetime.utcnow().strftime("%B %d, %Y"),
                "stakeholder_impact": crisis.stakeholder_impact.get(stakeholder_group.stakeholder_type, ""),
                "brand_impact": self._get_brand_specific_impact(crisis),
                "creator_count": "500,000+",  # Mock data
                "brand_count": "10,000+",     # Mock data
                "spokesperson": "Sarah Johnson",  # Mock data
                "title": "Head of Communications"  # Mock data
            }
            
            # Replace variables in template
            result = template
            for key, value in variables.items():
                result = result.replace(f"{{{key}}}", str(value))
            
            return result
            
        except Exception as e:
            logger.error(f"Template variable filling failed: {e}")
            return template
    
    def _get_brand_specific_impact(self, crisis: CrisisEvent) -> str:
        """Get brand-specific impact description"""
        brand_impacts = []
        
        if "campaign_management" in crisis.affected_services:
            brand_impacts.append("Campaign creation and management")
        if "analytics" in crisis.affected_services:
            brand_impacts.append("Performance analytics and reporting")
        if "collaboration" in crisis.affected_services:
            brand_impacts.append("Creator collaboration workflows")
        if "monetization" in crisis.affected_services:
            brand_impacts.append("Payment and billing systems")
        
        if brand_impacts:
            return "Affected features: " + ", ".join(brand_impacts)
        else:
            return "Minimal direct impact on brand operations"
    
    def _select_communication_channels(self, crisis: CrisisEvent, 
                                     stakeholder_group: StakeholderGroup) -> List[CommunicationChannel]:
        """Select appropriate communication channels"""
        channels = []
        
        try:
            # Start with preferred channels
            channels.extend(stakeholder_group.preferred_channels)
            
            # Add additional channels based on crisis level
            if crisis.crisis_level in [CrisisLevel.CRITICAL, CrisisLevel.CATASTROPHIC]:
                # Use all available channels for critical incidents
                if stakeholder_group.stakeholder_type == StakeholderType.USERS:
                    channels.extend([
                        CommunicationChannel.SOCIAL_MEDIA,
                        CommunicationChannel.WEBSITE_BANNER,
                        CommunicationChannel.PUSH_NOTIFICATION
                    ])
                elif stakeholder_group.stakeholder_type == StakeholderType.CREATORS:
                    channels.extend([
                        CommunicationChannel.SMS,
                        CommunicationChannel.DISCORD
                    ])
                elif stakeholder_group.stakeholder_type == StakeholderType.MEDIA:
                    channels.extend([
                        CommunicationChannel.PRESS_RELEASE,
                        CommunicationChannel.BLOG_POST
                    ])
            
            # Remove duplicates and return
            return list(set(channels))
            
        except Exception as e:
            logger.error(f"Channel selection failed: {e}")
            return stakeholder_group.preferred_channels
    
    async def _send_crisis_message(self, message: CrisisMessage):
        """Send crisis message through selected channels"""
        try:
            # Check if approval required
            if message.approval_status == "pending":
                # In real implementation, wait for approval or timeout
                await asyncio.sleep(1)  # Mock approval delay
                message.approval_status = "approved"
                message.approved_by = "auto-approved"
            
            if message.approval_status != "approved":
                logger.warning(f"Message {message.message_id} not approved for sending")
                return
            
            # Send through each channel
            for channel in message.channels:
                try:
                    delivery_status = await self._send_via_channel(message, channel)
                    message.delivery_status[channel.value] = delivery_status
                except Exception as e:
                    logger.error(f"Failed to send via {channel.value}: {e}")
                    message.delivery_status[channel.value] = f"failed: {str(e)}"
            
            message.sent_time = datetime.utcnow()
            
            logger.info(f"Crisis message {message.message_id} sent via {len(message.channels)} channels")
            
        except Exception as e:
            logger.error(f"Crisis message sending failed: {e}")
    
    async def _send_via_channel(self, message: CrisisMessage, 
                              channel: CommunicationChannel) -> str:
        """Send message via specific channel"""
        try:
            # Mock implementations - in real system, integrate with actual services
            
            if channel == CommunicationChannel.EMAIL:
                # Integrate with email service (SendGrid, SES, etc.)
                return "sent_successfully"
            
            elif channel == CommunicationChannel.SMS:
                # Integrate with SMS service (Twilio, etc.)
                return "sent_successfully"
            
            elif channel == CommunicationChannel.SLACK:
                # Integrate with Slack API
                return "sent_successfully"
            
            elif channel == CommunicationChannel.DISCORD:
                # Integrate with Discord webhooks
                return "sent_successfully"
            
            elif channel == CommunicationChannel.SOCIAL_MEDIA:
                # Send via social media platforms
                await self._post_to_social_media(message)
                return "posted_successfully"
            
            elif channel == CommunicationChannel.STATUS_PAGE:
                # Update status page
                await self._update_status_page(message)
                return "updated_successfully"
            
            elif channel == CommunicationChannel.PUSH_NOTIFICATION:
                # Send push notifications
                return "sent_successfully"
            
            elif channel == CommunicationChannel.IN_APP_BANNER:
                # Update in-app banner
                return "displayed_successfully"
            
            elif channel == CommunicationChannel.WEBSITE_BANNER:
                # Update website banner
                return "displayed_successfully"
            
            elif channel == CommunicationChannel.PRESS_RELEASE:
                # Distribute press release
                await self._distribute_press_release(message)
                return "distributed_successfully"
            
            elif channel == CommunicationChannel.BLOG_POST:
                # Publish blog post
                return "published_successfully"
            
            else:
                return "channel_not_implemented"
                
        except Exception as e:
            logger.error(f"Channel {channel.value} sending failed: {e}")
            return f"failed: {str(e)}"
    
    async def _post_to_social_media(self, message: CrisisMessage):
        """Post crisis update to social media platforms"""
        try:
            platforms = ["twitter", "linkedin", "facebook"]
            
            for platform in platforms:
                # Create platform-appropriate content
                content = self._adapt_content_for_platform(message, platform)
                
                social_post = SocialMediaPost(
                    post_id=str(uuid.uuid4()),
                    platform=platform,
                    content=content,
                    media_attachments=[],
                    scheduled_time=datetime.utcnow(),
                    posted_time=datetime.utcnow(),
                    engagement_metrics={},
                    responses_received=[],
                    escalated_comments=[]
                )
                
                # Store for monitoring
                if message.crisis_id not in self.social_media_monitors:
                    self.social_media_monitors[message.crisis_id] = []
                self.social_media_monitors[message.crisis_id].append(social_post)
                
                logger.info(f"Posted crisis update to {platform}")
            
        except Exception as e:
            logger.error(f"Social media posting failed: {e}")
    
    def _adapt_content_for_platform(self, message: CrisisMessage, platform: str) -> str:
        """Adapt message content for specific social media platform"""
        try:
            base_content = message.content.get("en", {}).get("content", "")
            
            if platform == "twitter":
                # Twitter character limit
                if len(base_content) > 280:
                    return base_content[:250] + "... Status: https://status.ainflue.com"
                else:
                    return base_content + " Status: https://status.ainflue.com"
            
            elif platform == "linkedin":
                # Professional tone for LinkedIn
                return f"Ainflue Platform Update:\n\n{base_content}\n\nFor real-time updates: https://status.ainflue.com\n\n#PlatformUpdate #Transparency"
            
            elif platform == "facebook":
                # More detailed for Facebook
                return f"{base_content}\n\nWe appreciate your patience as we work to resolve this issue. Updates: https://status.ainflue.com"
            
            else:
                return base_content
                
        except Exception as e:
            logger.error(f"Content adaptation failed: {e}")
            return message.content.get("en", {}).get("content", "")
    
    async def _update_status_page(self, message: CrisisMessage):
        """Update status page with incident information"""
        try:
            # Mock status page update
            status_update = {
                "incident_id": message.crisis_id,
                "title": message.subject,
                "description": message.content.get("en", {}).get("content", ""),
                "status": "investigating",
                "impact": "partial_outage",
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat()
            }
            
            logger.info(f"Status page updated for crisis {message.crisis_id}")
            
        except Exception as e:
            logger.error(f"Status page update failed: {e}")
    
    async def _distribute_press_release(self, message: CrisisMessage):
        """Distribute press release to media contacts"""
        try:
            # Mock press release distribution
            distribution_list = [
                "techcrunch@tc.com",
                "news@theverge.com", 
                "tips@mashable.com",
                "press@reuters.com"
            ]
            
            for contact in distribution_list:
                # In real implementation, send via email service
                logger.info(f"Press release sent to {contact}")
            
        except Exception as e:
            logger.error(f"Press release distribution failed: {e}")
    
    async def _start_social_media_monitoring(self, crisis: CrisisEvent):
        """Start monitoring social media for crisis-related mentions"""
        try:
            monitoring_config = {
                "keywords": [
                    "ainflue",
                    "ainflue down",
                    "ainflue not working",
                    crisis.title.lower()
                ],
                "platforms": ["twitter", "reddit", "instagram"],
                "sentiment_analysis": True,
                "alert_threshold": 10  # Alert if >10 mentions per hour
            }
            
            crisis.social_media_monitoring = monitoring_config
            
            # In real implementation, start actual monitoring
            logger.info(f"Social media monitoring started for crisis {crisis.crisis_id}")
            
        except Exception as e:
            logger.error(f"Social media monitoring setup failed: {e}")
    
    async def send_status_update(self, crisis_id: str, update_message: str,
                               stakeholder_groups: List[str] = None) -> bool:
        """Send status update for ongoing crisis"""
        try:
            crisis = self.active_crises.get(crisis_id)
            if not crisis:
                logger.error(f"Crisis {crisis_id} not found")
                return False
            
            # Default to all affected groups if not specified
            if not stakeholder_groups:
                stakeholder_groups = list(crisis.stakeholder_impact.keys())
            
            # Create and send update messages
            for group_id in stakeholder_groups:
                group = self.stakeholder_groups.get(group_id)
                if not group:
                    continue
                
                # Create status update message
                message = await self._create_status_update_message(
                    crisis, group, update_message
                )
                
                if message:
                    await self._send_crisis_message(message)
                    crisis.messages_sent.append(message.message_id)
            
            logger.info(f"Status update sent for crisis {crisis_id}")
            return True
            
        except Exception as e:
            logger.error(f"Status update sending failed: {e}")
            return False
    
    async def _create_status_update_message(self, crisis: CrisisEvent,
                                          stakeholder_group: StakeholderGroup,
                                          update_text: str) -> Optional[CrisisMessage]:
        """Create status update message"""
        try:
            # Create simple update message
            content = {
                "en": {
                    "subject": f"Update: {crisis.title}",
                    "content": f"""
Status Update - {datetime.utcnow().strftime('%H:%M UTC')}

{update_text}

We'll continue to provide updates as the situation develops.

For real-time status: https://status.ainflue.com
                    """.strip()
                }
            }
            
            message = CrisisMessage(
                message_id=str(uuid.uuid4()),
                crisis_id=crisis.crisis_id,
                message_type=MessageType.STATUS_UPDATE,
                stakeholder_groups=[stakeholder_group.group_id],
                channels=stakeholder_group.preferred_channels,
                subject=content["en"]["subject"],
                content=content,
                scheduled_time=datetime.utcnow(),
                sent_time=None,
                approval_status="approved",  # Status updates typically don't need approval
                approved_by="auto-approved",
                delivery_status={},
                engagement_metrics={},
                follow_up_required=False,
                expiry_time=datetime.utcnow() + timedelta(hours=12),
                metadata={"message_type": "status_update"}
            )
            
            return message
            
        except Exception as e:
            logger.error(f"Status update message creation failed: {e}")
            return None
    
    async def resolve_crisis(self, crisis_id: str, resolution_message: str) -> bool:
        """Resolve crisis and send resolution notifications"""
        try:
            crisis = self.active_crises.get(crisis_id)
            if not crisis:
                logger.error(f"Crisis {crisis_id} not found")
                return False
            
            # Update crisis status
            crisis.status = "resolved"
            crisis.actual_resolution = datetime.utcnow()
            
            # Send resolution messages to all stakeholder groups
            for stakeholder_type in crisis.stakeholder_impact.keys():
                # Find stakeholder group
                group = None
                for g in self.stakeholder_groups.values():
                    if g.stakeholder_type == stakeholder_type:
                        group = g
                        break
                
                if not group:
                    continue
                
                # Create resolution message
                message = await self._create_resolution_message(
                    crisis, group, resolution_message
                )
                
                if message:
                    await self._send_crisis_message(message)
                    crisis.messages_sent.append(message.message_id)
            
            # Update status page
            await self._update_status_page_resolved(crisis)
            
            # Post resolution to social media
            await self._post_resolution_to_social_media(crisis, resolution_message)
            
            logger.info(f"Crisis {crisis_id} resolved and notifications sent")
            return True
            
        except Exception as e:
            logger.error(f"Crisis resolution failed: {e}")
            return False
    
    async def _create_resolution_message(self, crisis: CrisisEvent,
                                       stakeholder_group: StakeholderGroup,
                                       resolution_text: str) -> Optional[CrisisMessage]:
        """Create crisis resolution message"""
        try:
            duration = crisis.actual_resolution - crisis.start_time
            duration_str = f"{int(duration.total_seconds() // 3600)}h {int((duration.total_seconds() % 3600) // 60)}m"
            
            content = {
                "en": {
                    "subject": f"✅ Resolved: {crisis.title}",
                    "content": f"""
RESOLVED - {datetime.utcnow().strftime('%H:%M UTC')}

{resolution_text}

**Incident Summary:**
- Started: {crisis.start_time.strftime('%H:%M UTC')}
- Resolved: {crisis.actual_resolution.strftime('%H:%M UTC')}
- Duration: {duration_str}
- Services Affected: {', '.join(crisis.affected_services)}

All systems are now operating normally. Thank you for your patience during this incident.

We'll be conducting a thorough post-mortem analysis and will share our findings to prevent similar issues in the future.
                    """.strip()
                }
            }
            
            message = CrisisMessage(
                message_id=str(uuid.uuid4()),
                crisis_id=crisis.crisis_id,
                message_type=MessageType.RESOLUTION_NOTICE,
                stakeholder_groups=[stakeholder_group.group_id],
                channels=stakeholder_group.preferred_channels,
                subject=content["en"]["subject"],
                content=content,
                scheduled_time=datetime.utcnow(),
                sent_time=None,
                approval_status="approved",
                approved_by="auto-approved",
                delivery_status={},
                engagement_metrics={},
                follow_up_required=False,
                expiry_time=datetime.utcnow() + timedelta(days=1),
                metadata={"message_type": "resolution"}
            )
            
            return message
            
        except Exception as e:
            logger.error(f"Resolution message creation failed: {e}")
            return None
    
    async def _update_status_page_resolved(self, crisis: CrisisEvent):
        """Update status page with resolution"""
        try:
            # Mock status page resolution update
            resolution_update = {
                "incident_id": crisis.crisis_id,
                "status": "resolved",
                "resolved_at": crisis.actual_resolution.isoformat(),
                "resolution_message": "All systems operational"
            }
            
            logger.info(f"Status page updated with resolution for crisis {crisis.crisis_id}")
            
        except Exception as e:
            logger.error(f"Status page resolution update failed: {e}")
    
    async def _post_resolution_to_social_media(self, crisis: CrisisEvent, resolution_message: str):
        """Post crisis resolution to social media"""
        try:
            platforms = ["twitter", "linkedin", "facebook"]
            
            for platform in platforms:
                content = f"✅ Update: The platform issues have been resolved. All Ainflue services are now operating normally. Thank you for your patience! #Resolved"
                
                if platform == "linkedin":
                    content = f"Ainflue Platform Update: ✅ Resolved\n\n{resolution_message}\n\nAll services are now operating normally. Thank you for your patience and continued trust in our platform.\n\n#PlatformUpdate #Resolved #BackOnline"
                
                # Store social media post
                social_post = SocialMediaPost(
                    post_id=str(uuid.uuid4()),
                    platform=platform,
                    content=content,
                    media_attachments=[],
                    scheduled_time=datetime.utcnow(),
                    posted_time=datetime.utcnow(),
                    engagement_metrics={},
                    responses_received=[],
                    escalated_comments=[]
                )
                
                logger.info(f"Resolution posted to {platform}")
            
        except Exception as e:
            logger.error(f"Social media resolution posting failed: {e}")
    
    async def get_crisis_dashboard(self) -> Dict[str, Any]:
        """Get crisis communication dashboard"""
        try:
            active_crises = [c for c in self.active_crises.values() if c.status == "active"]
            
            dashboard = {
                "summary": {
                    "total_crises": len(self.active_crises),
                    "active_crises": len(active_crises),
                    "resolved_crises": len([c for c in self.active_crises.values() if c.status == "resolved"]),
                    "critical_crises": len([c for c in active_crises if c.crisis_level in [CrisisLevel.CRITICAL, CrisisLevel.CATASTROPHIC]])
                },
                "active_crises": [
                    {
                        "crisis_id": c.crisis_id,
                        "title": c.title,
                        "level": c.crisis_level.value,
                        "start_time": c.start_time.isoformat(),
                        "affected_services": c.affected_services,
                        "messages_sent": len(c.messages_sent)
                    }
                    for c in active_crises
                ],
                "communication_metrics": {
                    "total_messages_sent": sum(len(c.messages_sent) for c in self.active_crises.values()),
                    "avg_response_time": "5 minutes",  # Mock data
                    "stakeholder_reach": "1.2M",  # Mock data
                    "social_media_engagement": "95%"  # Mock data
                },
                "recent_activities": []  # Could be populated with recent message activities
            }
            
            return dashboard
            
        except Exception as e:
            logger.error(f"Crisis dashboard generation failed: {e}")
            return {}


# Global crisis communication manager instance
_crisis_communication_manager = None


def get_crisis_communication_manager(pagerduty_client=None) -> CrisisCommunicationManager:
    """Get crisis communication manager instance"""
    global _crisis_communication_manager
    if _crisis_communication_manager is None:
        _crisis_communication_manager = CrisisCommunicationManager(pagerduty_client)
    return _crisis_communication_manager


def create_crisis_communication_manager(pagerduty_client=None) -> CrisisCommunicationManager:
    """Create new crisis communication manager instance"""
    return CrisisCommunicationManager(pagerduty_client)


# Export main classes and functions
__all__ = [
    'CrisisCommunicationManager',
    'CrisisEvent',
    'CrisisMessage',
    'StakeholderGroup',
    'SocialMediaPost',
    'CrisisLevel',
    'CommunicationChannel',
    'StakeholderType',
    'MessageType',
    'get_crisis_communication_manager',
    'create_crisis_communication_manager'
]