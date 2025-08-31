"""IA Influencer Agent - Platform Alerts System
==========================================

Advanced platform-specific alerting system for content protection and violation detection.
Provides intelligent alert routing, escalation management, and automated response coordination.

Team Expertise: Lead Dev IA + Backend Senior + ML Engineer + DBA + Security + 
Microservices + Audio + DevOps + IA Prompt Engineer

Author: Fahed Mlaiel (mlaiel@live.de)
Email: mlaiel@live.de
Copyright: © 2025 Fahed Mlaiel - All Rights Reserved

⚠️  CRITICAL WARNING ⚠️
This code is PROPRIETARY and CONFIDENTIAL intellectual property.
Any unauthorized use, reproduction, distribution, or reverse engineering 
is STRICTLY PROHIBITED and will result in immediate legal action.

Unauthorized copying or theft of this concept, code, or methodology 
will be prosecuted to the FULL EXTENT OF THE LAW under German and 
International Copyright Laws.

For licensing inquiries, contact: mlaiel@live.de
"""
import asyncio
import logging
import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple, Union, Callable
from dataclasses import dataclass, field
from enum import Enum
import uuid
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import requests
import aiohttp
import aioredis

# Internal imports
from .config import FingerprintingSystemConfig
from .metadata import ContentMetadata
from .real_time_monitoring import AlertEvent, AlertLevel

logger = logging.getLogger(__name__)


class PlatformType(Enum):
    """Supported platform types for alerts"""
    YOUTUBE = "youtube"
    TIKTOK = "tiktok"
    INSTAGRAM = "instagram"
    TWITTER = "twitter"
    FACEBOOK = "facebook"
    SPOTIFY = "spotify"
    SOUNDCLOUD = "soundcloud"
    TWITCH = "twitch"
    LINKEDIN = "linkedin"
    DISCORD = "discord"
    SLACK = "slack"
    TELEGRAM = "telegram"
    GENERIC_WEB = "generic_web"


class AlertChannel(Enum):
    """Alert delivery channels"""
    EMAIL = "email"
    SMS = "sms"
    WEBHOOK = "webhook"
    SLACK = "slack"
    DISCORD = "discord"
    TELEGRAM = "telegram"
    PUSH_NOTIFICATION = "push_notification"
    PLATFORM_API = "platform_api"
    LEGAL_NOTICE = "legal_notice"


class AlertActionType(Enum):
    """Types of automated actions"""
    DMCA_TAKEDOWN = "dmca_takedown"
    PLATFORM_REPORT = "platform_report"
    LEGAL_NOTICE = "legal_notice"
    CEASE_DESIST = "cease_desist"
    CONTENT_CLAIM = "content_claim"
    MONETIZATION_CLAIM = "monetization_claim"
    ACCOUNT_SUSPENSION = "account_suspension"
    EVIDENCE_COLLECTION = "evidence_collection"


class AlertStatus(Enum):
    """Alert processing status"""
    PENDING = "pending"
    PROCESSING = "processing"
    SENT = "sent"
    DELIVERED = "delivered"
    ACKNOWLEDGED = "acknowledged"
    RESOLVED = "resolved"
    FAILED = "failed"
    ESCALATED = "escalated"


@dataclass
class PlatformCredentials:
    """Platform API credentials"""
    platform: PlatformType
    api_key: Optional[str] = None
    secret_key: Optional[str] = None
    access_token: Optional[str] = None
    refresh_token: Optional[str] = None
    username: Optional[str] = None
    password: Optional[str] = None
    additional_params: Dict[str, Any] = field(default_factory=dict)
    expires_at: Optional[datetime] = None
    rate_limit: int = 100  # requests per hour
    last_used: Optional[datetime] = None


@dataclass
class AlertTemplate:
    """Alert message template"""
    template_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    platform: PlatformType = PlatformType.GENERIC_WEB
    channel: AlertChannel = AlertChannel.EMAIL
    subject_template: str = ""
    message_template: str = ""
    variables: List[str] = field(default_factory=list)
    language: str = "en"
    is_legal_template: bool = False
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class AlertRule:
    """Alert routing and escalation rule"""
    rule_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    conditions: Dict[str, Any] = field(default_factory=dict)
    platforms: List[PlatformType] = field(default_factory=list)
    channels: List[AlertChannel] = field(default_factory=list)
    priority_threshold: int = 5  # 1-10
    auto_actions: List[AlertActionType] = field(default_factory=list)
    escalation_delay: int = 3600  # seconds
    max_escalations: int = 3
    active: bool = True
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class PlatformAlert:
    """Platform-specific alert"""
    alert_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    platform: PlatformType
    channel: AlertChannel
    fingerprint_id: str = ""
    content_id: str = ""
    violation_url: str = ""
    similarity_score: float = 0.0
    alert_level: AlertLevel = AlertLevel.INFO
    status: AlertStatus = AlertStatus.PENDING
    
    # Message content
    subject: str = ""
    message: str = ""
    evidence: Dict[str, Any] = field(default_factory=dict)
    legal_grounds: List[str] = field(default_factory=list)
    
    # Recipient information
    recipient_email: Optional[str] = None
    recipient_phone: Optional[str] = None
    webhook_url: Optional[str] = None
    platform_account: Optional[str] = None
    
    # Processing details
    attempts: int = 0
    max_attempts: int = 3
    last_attempt: Optional[datetime] = None
    next_retry: Optional[datetime] = None
    response_data: Dict[str, Any] = field(default_factory=dict)
    
    # Tracking
    created_at: datetime = field(default_factory=datetime.utcnow)
    sent_at: Optional[datetime] = None
    delivered_at: Optional[datetime] = None
    acknowledged_at: Optional[datetime] = None
    resolved_at: Optional[datetime] = None


@dataclass
class AlertResponse:
    """Alert delivery response"""
    alert_id: str
    channel: AlertChannel
    success: bool
    response_code: Optional[int] = None
    response_message: str = ""
    delivery_id: Optional[str] = None
    estimated_delivery: Optional[datetime] = None
    cost: Optional[float] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


class PlatformAlertsManager:
    """Advanced platform alerts management system"""
    
    def __init__(self, config: FingerprintingSystemConfig):
        self.config = config
        self.credentials: Dict[PlatformType, PlatformCredentials] = {}
        self.templates: Dict[str, AlertTemplate] = {}
        self.rules: Dict[str, AlertRule] = {}
        self.pending_alerts: Dict[str, PlatformAlert] = {}
        
        # Channel handlers
        self.channel_handlers: Dict[AlertChannel, Callable] = {}
        
        # Rate limiting
        self.rate_limiters: Dict[PlatformType, Dict[str, Any]] = {}
        
        # Background processing
        self.processing_task: Optional[asyncio.Task] = None
        self.running = False
        
        # Statistics
        self.stats = {
            'alerts_sent': 0,
            'alerts_failed': 0,
            'alerts_delivered': 0,
            'alerts_acknowledged': 0,
            'total_cost': 0.0
        }
        
        # Initialize system
        self._initialize_default_templates()
        self._initialize_default_rules()
        self._setup_channel_handlers()
        
        logger.info("Platform Alerts Manager initialized")
    
    def _initialize_default_templates(self):
        """Initialize default alert templates"""
        # DMCA Takedown Template
        dmca_template = AlertTemplate(
            name="DMCA Takedown Notice",
            platform=PlatformType.GENERIC_WEB,
            channel=AlertChannel.EMAIL,
            subject_template="DMCA Takedown Notice - Copyright Infringement",
            message_template="""Dear {platform_name} Content Team,

This is a formal DMCA takedown notice under the Digital Millennium Copyright Act (17 U.S.C. § 512).

**INFRINGEMENT DETAILS:**
- Infringing Content URL: {violation_url}
- Original Content ID: {content_id}
- Similarity Score: {similarity_score}%
- Detection Date: {detection_date}

**COPYRIGHT HOLDER INFORMATION:**
- Name: {copyright_holder_name}
- Email: {copyright_holder_email}
- Address: {copyright_holder_address}

**INFRINGEMENT CLAIM:**
The content at the above URL infringes upon copyrighted material owned by the copyright holder. 
This content was uploaded without authorization and constitutes copyright infringement.

**EVIDENCE:**
{evidence_details}

**GOOD FAITH STATEMENT:**
I have a good faith belief that the use of the copyrighted material described above is not authorized by the copyright owner, its agent, or the law.

**ACCURACY STATEMENT:**
The information in this notification is accurate, and under penalty of perjury, I am authorized to act on behalf of the copyright owner.

**REQUESTED ACTION:**
Please remove or disable access to the infringing material immediately.

Sincerely,
{copyright_holder_name}
{signature_date}
            """,
            variables=["platform_name", "violation_url", "content_id", "similarity_score", 
                      "detection_date", "copyright_holder_name", "copyright_holder_email",
                      "copyright_holder_address", "evidence_details", "signature_date"],
            is_legal_template=True
        )
        self.templates[dmca_template.template_id] = dmca_template
        
        # Platform Report Template
        report_template = AlertTemplate(
            name="Platform Violation Report",
            platform=PlatformType.GENERIC_WEB,
            channel=AlertChannel.PLATFORM_API,
            subject_template="Copyright Violation Report",
            message_template="""Automated copyright violation report:

Content URL: {violation_url}
Violation Type: Copyright Infringement
Original Content: {content_id}
Similarity: {similarity_score}%
Evidence: {evidence_summary}

Please review and take appropriate action.
            """,
            variables=["violation_url", "content_id", "similarity_score", "evidence_summary"]
        )
        self.templates[report_template.template_id] = report_template
        
        # Slack Alert Template
        slack_template = AlertTemplate(
            name="Slack Violation Alert",
            platform=PlatformType.GENERIC_WEB,
            channel=AlertChannel.SLACK,
            subject_template="🚨 Copyright Violation Detected",
            message_template="""🚨 **COPYRIGHT VIOLATION DETECTED** 🚨

📍 **Platform:** {platform_name}
🔗 **URL:** {violation_url}
📊 **Similarity:** {similarity_score}%
⏰ **Detected:** {detection_date}
🆔 **Content ID:** {content_id}

**Evidence:** {evidence_summary}

**Suggested Actions:**
• Review violation details
• Initiate takedown process
• Document evidence
• Monitor for similar violations
            """,
            variables=["platform_name", "violation_url", "similarity_score", 
                      "detection_date", "content_id", "evidence_summary"]
        )
        self.templates[slack_template.template_id] = slack_template
    
    def _initialize_default_rules(self):
        """Initialize default alert rules"""
        # High priority violations
        high_priority_rule = AlertRule(
            name="High Priority Violations",
            conditions={
                "similarity_score": {">=": 0.9},
                "alert_level": ["critical", "emergency"]
            },
            platforms=[PlatformType.YOUTUBE, PlatformType.TIKTOK, PlatformType.INSTAGRAM],
            channels=[AlertChannel.EMAIL, AlertChannel.SLACK, AlertChannel.PLATFORM_API],
            priority_threshold=8,
            auto_actions=[AlertActionType.PLATFORM_REPORT, AlertActionType.EVIDENCE_COLLECTION],
            escalation_delay=1800,  # 30 minutes
            max_escalations=5
        )
        self.rules[high_priority_rule.rule_id] = high_priority_rule
        
        # Medium priority violations
        medium_priority_rule = AlertRule(
            name="Medium Priority Violations",
            conditions={
                "similarity_score": {">=": 0.7, "<": 0.9},
                "alert_level": ["warning"]
            },
            platforms=list(PlatformType),
            channels=[AlertChannel.EMAIL, AlertChannel.SLACK],
            priority_threshold=5,
            auto_actions=[AlertActionType.EVIDENCE_COLLECTION],
            escalation_delay=3600,  # 1 hour
            max_escalations=3
        )
        self.rules[medium_priority_rule.rule_id] = medium_priority_rule
    
    def _setup_channel_handlers(self):
        """Setup handlers for different alert channels"""
        self.channel_handlers = {
            AlertChannel.EMAIL: self._send_email_alert,
            AlertChannel.SMS: self._send_sms_alert,
            AlertChannel.WEBHOOK: self._send_webhook_alert,
            AlertChannel.SLACK: self._send_slack_alert,
            AlertChannel.DISCORD: self._send_discord_alert,
            AlertChannel.TELEGRAM: self._send_telegram_alert,
            AlertChannel.PLATFORM_API: self._send_platform_api_alert,
            AlertChannel.LEGAL_NOTICE: self._send_legal_notice
        }
    
    async def start(self):
        """Start alert processing system"""
        if self.running:
            logger.warning("Platform alerts system already running")
            return
        
        self.running = True
        
        # Start background processing
        self.processing_task = asyncio.create_task(self._process_alerts_loop())
        
        logger.info("Platform alerts system started")
    
    async def stop(self):
        """Stop alert processing system"""
        if not self.running:
            return
        
        self.running = False
        
        # Cancel background processing
        if self.processing_task:
            self.processing_task.cancel()
            try:
                await self.processing_task
            except asyncio.CancelledError:
                pass
        
        logger.info("Platform alerts system stopped")
    
    async def send_platform_alert(
        self,
        fingerprint_id: str,
        content_id: str,
        platform: PlatformType,
        violation_url: str,
        similarity_score: float,
        evidence: Dict[str, Any],
        **kwargs
    ) -> List[str]:
        """Send platform-specific alert"""
        try:
            # Determine alert level
            if similarity_score >= 0.95:
                alert_level = AlertLevel.EMERGENCY
            elif similarity_score >= 0.9:
                alert_level = AlertLevel.CRITICAL
            elif similarity_score >= 0.8:
                alert_level = AlertLevel.WARNING
            else:
                alert_level = AlertLevel.INFO
            
            # Find matching rules
            matching_rules = self._find_matching_rules(
                platform, similarity_score, alert_level, evidence
            )
            
            alert_ids = []
            
            for rule in matching_rules:
                # Create alerts for each channel in the rule
                for channel in rule.channels:
                    alert = PlatformAlert(
                        platform=platform,
                        channel=channel,
                        fingerprint_id=fingerprint_id,
                        content_id=content_id,
                        violation_url=violation_url,
                        similarity_score=similarity_score,
                        alert_level=alert_level,
                        evidence=evidence,
                        **kwargs
                    )
                    
                    # Generate message content
                    await self._generate_alert_content(alert, rule)
                    
                    # Add to pending alerts
                    self.pending_alerts[alert.alert_id] = alert
                    alert_ids.append(alert.alert_id)
                    
                    logger.info(f"Created {channel.value} alert for {platform.value}: {alert.alert_id}")
                
                # Execute auto actions
                for action in rule.auto_actions:
                    await self._execute_auto_action(action, alert, evidence)
            
            return alert_ids
            
        except Exception as e:
            logger.error(f"Failed to send platform alert: {str(e)}")
            return []
    
    def _find_matching_rules(
        self,
        platform: PlatformType,
        similarity_score: float,
        alert_level: AlertLevel,
        evidence: Dict[str, Any]
    ) -> List[AlertRule]:
        """Find alert rules that match the violation"""
        matching_rules = []
        
        for rule in self.rules.values():
            if not rule.active:
                continue
            
            # Check platform match
            if rule.platforms and platform not in rule.platforms:
                continue
            
            # Check conditions
            matches = True
            for condition_key, condition_value in rule.conditions.items():
                if condition_key == "similarity_score":
                    if isinstance(condition_value, dict):
                        for operator, threshold in condition_value.items():
                            if operator == ">=" and similarity_score < threshold:
                                matches = False
                            elif operator == "<" and similarity_score >= threshold:
                                matches = False
                            elif operator == "==" and similarity_score != threshold:
                                matches = False
                    elif similarity_score < condition_value:
                        matches = False
                
                elif condition_key == "alert_level":
                    if isinstance(condition_value, list):
                        if alert_level.value not in condition_value:
                            matches = False
                    elif alert_level.value != condition_value:
                        matches = False
                
                if not matches:
                    break
            
            if matches:
                matching_rules.append(rule)
        
        return matching_rules
    
    async def _generate_alert_content(self, alert: PlatformAlert, rule: AlertRule):
        """Generate alert message content using templates"""
        try:
            # Find appropriate template
            template = self._find_template(alert.platform, alert.channel)
            
            if not template:
                # Use default template
                alert.subject = f"Copyright Violation Detected - {alert.similarity_score:.1%} similarity"
                alert.message = f"""A potential copyright violation has been detected:

Platform: {alert.platform.value}
URL: {alert.violation_url}
Similarity: {alert.similarity_score:.1%}
Content ID: {alert.content_id}
Detection Time: {alert.created_at.isoformat()}

Please review and take appropriate action.
                """
                return
            
            # Prepare template variables
            variables = {
                "platform_name": alert.platform.value.title(),
                "violation_url": alert.violation_url,
                "content_id": alert.content_id,
                "similarity_score": f"{alert.similarity_score * 100:.1f}",
                "detection_date": alert.created_at.strftime("%Y-%m-%d %H:%M:%S UTC"),
                "fingerprint_id": alert.fingerprint_id,
                "evidence_summary": self._summarize_evidence(alert.evidence),
                "evidence_details": self._format_evidence(alert.evidence),
                "copyright_holder_name": self.config.copyright_holder_name if hasattr(self.config, 'copyright_holder_name') else "Content Owner",
                "copyright_holder_email": self.config.copyright_holder_email if hasattr(self.config, 'copyright_holder_email') else "legal@example.com",
                "copyright_holder_address": self.config.copyright_holder_address if hasattr(self.config, 'copyright_holder_address') else "Legal Address",
                "signature_date": datetime.utcnow().strftime("%Y-%m-%d")
            }
            
            # Fill template
            alert.subject = template.subject_template.format(**variables)
            alert.message = template.message_template.format(**variables)
            
        except Exception as e:
            logger.error(f"Failed to generate alert content: {str(e)}")
            # Fallback to basic message
            alert.subject = "Copyright Violation Alert"
            alert.message = f"Violation detected at {alert.violation_url}"
    
    def _find_template(self, platform: PlatformType, channel: AlertChannel) -> Optional[AlertTemplate]:
        """Find appropriate template for platform and channel"""
        # First try platform-specific template
        for template in self.templates.values():
            if template.platform == platform and template.channel == channel:
                return template
        
        # Then try generic template for channel
        for template in self.templates.values():
            if template.platform == PlatformType.GENERIC_WEB and template.channel == channel:
                return template
        
        return None
    
    def _summarize_evidence(self, evidence: Dict[str, Any]) -> str:
        """Create a summary of evidence"""
        summary_parts = []
        
        if "screenshot_url" in evidence:
            summary_parts.append("Screenshot captured")
        
        if "audio_match" in evidence:
            summary_parts.append(f"Audio similarity: {evidence['audio_match']:.1%}")
        
        if "visual_match" in evidence:
            summary_parts.append(f"Visual similarity: {evidence['visual_match']:.1%}")
        
        if "text_match" in evidence:
            summary_parts.append(f"Text similarity: {evidence['text_match']:.1%}")
        
        if "metadata" in evidence:
            summary_parts.append("Metadata analysis available")
        
        return "; ".join(summary_parts) if summary_parts else "Automated detection"
    
    def _format_evidence(self, evidence: Dict[str, Any]) -> str:
        """Format detailed evidence for legal notices"""
        formatted = []
        
        for key, value in evidence.items():
            if key == "screenshot_url":
                formatted.append(f"- Screenshot Evidence: {value}")
            elif key == "detection_algorithm":
                formatted.append(f"- Detection Method: {value}")
            elif key == "confidence_score":
                formatted.append(f"- Confidence Level: {value:.1%}")
            elif isinstance(value, (int, float)):
                formatted.append(f"- {key.replace('_', ' ').title()}: {value}")
            elif isinstance(value, str):
                formatted.append(f"- {key.replace('_', ' ').title()}: {value}")
        
        return "\n".join(formatted) if formatted else "Detailed technical analysis available upon request."
    
    async def _execute_auto_action(
        self,
        action: AlertActionType,
        alert: PlatformAlert,
        evidence: Dict[str, Any]
    ):
        """Execute automated action"""
        try:
            if action == AlertActionType.EVIDENCE_COLLECTION:
                await self._collect_additional_evidence(alert, evidence)
            
            elif action == AlertActionType.PLATFORM_REPORT:
                await self._submit_platform_report(alert)
            
            elif action == AlertActionType.DMCA_TAKEDOWN:
                await self._initiate_dmca_takedown(alert)
            
            elif action == AlertActionType.CONTENT_CLAIM:
                await self._submit_content_claim(alert)
            
            logger.info(f"Executed auto action {action.value} for alert {alert.alert_id}")
            
        except Exception as e:
            logger.error(f"Failed to execute auto action {action.value}: {str(e)}")
    
    async def _collect_additional_evidence(self, alert: PlatformAlert, evidence: Dict[str, Any]):
        """Collect additional evidence for the violation"""
        # This would implement screenshot capture, metadata extraction, etc.
        logger.info(f"Collecting additional evidence for {alert.violation_url}")
    
    async def _submit_platform_report(self, alert: PlatformAlert):
        """Submit report to platform"""
        # This would implement platform-specific reporting APIs
        logger.info(f"Submitting platform report for {alert.platform.value}")
    
    async def _initiate_dmca_takedown(self, alert: PlatformAlert):
        """Initiate DMCA takedown process"""
        # This would implement DMCA notice submission
        logger.info(f"Initiating DMCA takedown for {alert.violation_url}")
    
    async def _submit_content_claim(self, alert: PlatformAlert):
        """Submit content claim"""
        # This would implement content claiming (YouTube Content ID, etc.)
        logger.info(f"Submitting content claim for {alert.content_id}")
    
    async def _process_alerts_loop(self):
        """Background loop to process pending alerts"""
        while self.running:
            try:
                await self._process_pending_alerts()
                await asyncio.sleep(10)  # Process every 10 seconds
            except Exception as e:
                logger.error(f"Alert processing loop error: {str(e)}")
                await asyncio.sleep(30)
    
    async def _process_pending_alerts(self):
        """Process all pending alerts"""
        current_time = datetime.utcnow()
        
        alerts_to_process = []
        for alert in self.pending_alerts.values():
            if alert.status == AlertStatus.PENDING:
                alerts_to_process.append(alert)
            elif (alert.status == AlertStatus.FAILED and 
                  alert.next_retry and 
                  current_time >= alert.next_retry):
                alerts_to_process.append(alert)
        
        # Process alerts concurrently
        if alerts_to_process:
            tasks = [self._process_single_alert(alert) for alert in alerts_to_process]
            await asyncio.gather(*tasks, return_exceptions=True)
    
    async def _process_single_alert(self, alert: PlatformAlert):
        """Process a single alert"""
        try:
            alert.status = AlertStatus.PROCESSING
            alert.attempts += 1
            alert.last_attempt = datetime.utcnow()
            
            # Get handler for channel
            handler = self.channel_handlers.get(alert.channel)
            if not handler:
                logger.error(f"No handler for channel {alert.channel.value}")
                alert.status = AlertStatus.FAILED
                return
            
            # Check rate limits
            if not await self._check_rate_limit(alert.platform, alert.channel):
                logger.warning(f"Rate limit exceeded for {alert.platform.value}/{alert.channel.value}")
                alert.next_retry = datetime.utcnow() + timedelta(minutes=30)
                alert.status = AlertStatus.PENDING
                return
            
            # Send alert
            response = await handler(alert)
            
            if response.success:
                alert.status = AlertStatus.SENT
                alert.sent_at = datetime.utcnow()
                alert.response_data = response.metadata
                self.stats['alerts_sent'] += 1
                
                if response.cost:
                    self.stats['total_cost'] += response.cost
                
                logger.info(f"Alert sent successfully: {alert.alert_id}")
            else:
                alert.status = AlertStatus.FAILED
                alert.response_data = {'error': response.response_message}
                self.stats['alerts_failed'] += 1
                
                # Schedule retry if attempts remaining
                if alert.attempts < alert.max_attempts:
                    retry_delay = min(300 * (2 ** alert.attempts), 3600)  # Exponential backoff, max 1 hour
                    alert.next_retry = datetime.utcnow() + timedelta(seconds=retry_delay)
                    alert.status = AlertStatus.PENDING
                
                logger.warning(f"Alert failed: {alert.alert_id} - {response.response_message}")
            
        except Exception as e:
            logger.error(f"Error processing alert {alert.alert_id}: {str(e)}")
            alert.status = AlertStatus.FAILED
            alert.response_data = {'error': str(e)}
    
    async def _check_rate_limit(self, platform: PlatformType, channel: AlertChannel) -> bool:
        """Check if request is within rate limits"""
        key = f"{platform.value}_{channel.value}"
        current_time = datetime.utcnow()
        
        if key not in self.rate_limiters:
            self.rate_limiters[key] = {
                'requests': [],
                'limit': 100,  # Default limit
                'window': 3600  # 1 hour window
            }
        
        limiter = self.rate_limiters[key]
        
        # Remove old requests outside the window
        cutoff_time = current_time - timedelta(seconds=limiter['window'])
        limiter['requests'] = [
            req_time for req_time in limiter['requests'] 
            if req_time > cutoff_time
        ]
        
        # Check if under limit
        if len(limiter['requests']) >= limiter['limit']:
            return False
        
        # Add current request
        limiter['requests'].append(current_time)
        return True
    
    # Channel handlers
    async def _send_email_alert(self, alert: PlatformAlert) -> AlertResponse:
        """Send email alert"""
        try:
            # Configure SMTP (these would come from config)
            smtp_server = getattr(self.config, 'smtp_server', 'localhost')
            smtp_port = getattr(self.config, 'smtp_port', 587)
            smtp_username = getattr(self.config, 'smtp_username', '')
            smtp_password = getattr(self.config, 'smtp_password', '')
            
            # Create message
            msg = MIMEMultipart()
            msg['From'] = smtp_username
            msg['To'] = alert.recipient_email
            msg['Subject'] = alert.subject
            
            msg.attach(MIMEText(alert.message, 'plain'))
            
            # Send email
            with smtplib.SMTP(smtp_server, smtp_port) as server:
                server.starttls()
                server.login(smtp_username, smtp_password)
                server.send_message(msg)
            
            return AlertResponse(
                alert_id=alert.alert_id,
                channel=AlertChannel.EMAIL,
                success=True,
                response_message="Email sent successfully"
            )
            
        except Exception as e:
            return AlertResponse(
                alert_id=alert.alert_id,
                channel=AlertChannel.EMAIL,
                success=False,
                response_message=str(e)
            )
    
    async def _send_webhook_alert(self, alert: PlatformAlert) -> AlertResponse:
        """Send webhook alert"""
        try:
            if not alert.webhook_url:
                return AlertResponse(
                    alert_id=alert.alert_id,
                    channel=AlertChannel.WEBHOOK,
                    success=False,
                    response_message="No webhook URL provided"
                )
            
            payload = {
                'alert_id': alert.alert_id,
                'platform': alert.platform.value,
                'violation_url': alert.violation_url,
                'similarity_score': alert.similarity_score,
                'alert_level': alert.alert_level.value,
                'subject': alert.subject,
                'message': alert.message,
                'evidence': alert.evidence,
                'timestamp': alert.created_at.isoformat()
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    alert.webhook_url,
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=30)
                ) as response:
                    if response.status in [200, 201, 202]:
                        return AlertResponse(
                            alert_id=alert.alert_id,
                            channel=AlertChannel.WEBHOOK,
                            success=True,
                            response_code=response.status,
                            response_message="Webhook delivered successfully"
                        )
                    else:
                        return AlertResponse(
                            alert_id=alert.alert_id,
                            channel=AlertChannel.WEBHOOK,
                            success=False,
                            response_code=response.status,
                            response_message=f"HTTP {response.status}"
                        )
            
        except Exception as e:
            return AlertResponse(
                alert_id=alert.alert_id,
                channel=AlertChannel.WEBHOOK,
                success=False,
                response_message=str(e)
            )
    
    async def _send_slack_alert(self, alert: PlatformAlert) -> AlertResponse:
        """Send Slack alert"""
        try:
            slack_webhook = getattr(self.config, 'slack_webhook_url', '')
            if not slack_webhook:
                return AlertResponse(
                    alert_id=alert.alert_id,
                    channel=AlertChannel.SLACK,
                    success=False,
                    response_message="No Slack webhook configured"
                )
            
            payload = {
                'text': alert.subject,
                'attachments': [{
                    'color': 'danger' if alert.alert_level in [AlertLevel.CRITICAL, AlertLevel.EMERGENCY] else 'warning',
                    'fields': [
                        {'title': 'Platform', 'value': alert.platform.value.title(), 'short': True},
                        {'title': 'Similarity', 'value': f"{alert.similarity_score:.1%}", 'short': True},
                        {'title': 'URL', 'value': alert.violation_url, 'short': False},
                        {'title': 'Content ID', 'value': alert.content_id, 'short': True}
                    ],
                    'footer': 'IA Influencer Agent',
                    'ts': int(alert.created_at.timestamp())
                }]
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    slack_webhook,
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=30)
                ) as response:
                    success = response.status == 200
                    return AlertResponse(
                        alert_id=alert.alert_id,
                        channel=AlertChannel.SLACK,
                        success=success,
                        response_code=response.status,
                        response_message="Slack message sent" if success else f"HTTP {response.status}"
                    )
            
        except Exception as e:
            return AlertResponse(
                alert_id=alert.alert_id,
                channel=AlertChannel.SLACK,
                success=False,
                response_message=str(e)
            )
    
    async def _send_sms_alert(self, alert: PlatformAlert) -> AlertResponse:
        """Send SMS alert"""
        # This would integrate with SMS providers like Twilio
        return AlertResponse(
            alert_id=alert.alert_id,
            channel=AlertChannel.SMS,
            success=False,
            response_message="SMS provider not configured"
        )
    
    async def _send_discord_alert(self, alert: PlatformAlert) -> AlertResponse:
        """Send Discord alert"""
        # This would integrate with Discord webhooks
        return AlertResponse(
            alert_id=alert.alert_id,
            channel=AlertChannel.DISCORD,
            success=False,
            response_message="Discord integration not configured"
        )
    
    async def _send_telegram_alert(self, alert: PlatformAlert) -> AlertResponse:
        """Send Telegram alert"""
        # This would integrate with Telegram Bot API
        return AlertResponse(
            alert_id=alert.alert_id,
            channel=AlertChannel.TELEGRAM,
            success=False,
            response_message="Telegram integration not configured"
        )
    
    async def _send_platform_api_alert(self, alert: PlatformAlert) -> AlertResponse:
        """Send alert via platform API"""
        # This would implement platform-specific API calls for reporting
        return AlertResponse(
            alert_id=alert.alert_id,
            channel=AlertChannel.PLATFORM_API,
            success=False,
            response_message="Platform API integration not implemented"
        )
    
    async def _send_legal_notice(self, alert: PlatformAlert) -> AlertResponse:
        """Send legal notice"""
        # This would integrate with legal document generation and delivery
        return AlertResponse(
            alert_id=alert.alert_id,
            channel=AlertChannel.LEGAL_NOTICE,
            success=False,
            response_message="Legal notice system not configured"
        )
    
    def get_alert_status(self, alert_id: str) -> Optional[Dict[str, Any]]:
        """Get status of specific alert"""
        alert = self.pending_alerts.get(alert_id)
        if not alert:
            return None
        
        return {
            'alert_id': alert.alert_id,
            'platform': alert.platform.value,
            'channel': alert.channel.value,
            'status': alert.status.value,
            'attempts': alert.attempts,
            'created_at': alert.created_at.isoformat(),
            'sent_at': alert.sent_at.isoformat() if alert.sent_at else None,
            'last_attempt': alert.last_attempt.isoformat() if alert.last_attempt else None,
            'next_retry': alert.next_retry.isoformat() if alert.next_retry else None,
            'response_data': alert.response_data
        }
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get alert system statistics"""
        return {
            **self.stats,
            'pending_alerts': len([a for a in self.pending_alerts.values() if a.status == AlertStatus.PENDING]),
            'processing_alerts': len([a for a in self.pending_alerts.values() if a.status == AlertStatus.PROCESSING]),
            'failed_alerts': len([a for a in self.pending_alerts.values() if a.status == AlertStatus.FAILED]),
            'total_alerts': len(self.pending_alerts),
            'active_rules': len([r for r in self.rules.values() if r.active]),
            'available_templates': len(self.templates),
            'running': self.running
        }


# Global platform alerts manager instance
_platform_alerts_manager: Optional[PlatformAlertsManager] = None


def get_platform_alerts_manager(config: Optional[FingerprintingSystemConfig] = None) -> PlatformAlertsManager:
    """Get or create platform alerts manager instance"""
    global _platform_alerts_manager
    
    if _platform_alerts_manager is None:
        if config is None:
            from .config import get_config
            config = get_config()
        _platform_alerts_manager = PlatformAlertsManager(config)
    
    return _platform_alerts_manager


def reset_platform_alerts_manager():
    """Reset platform alerts manager (for testing)"""
    global _platform_alerts_manager
    if _platform_alerts_manager:
        asyncio.create_task(_platform_alerts_manager.stop())
    _platform_alerts_manager = None


# Convenience functions
async def send_violation_alert(
    fingerprint_id: str,
    content_id: str,
    platform: PlatformType,
    violation_url: str,
    similarity_score: float,
    evidence: Dict[str, Any],
    **kwargs
) -> List[str]:
    """Send violation alert convenience function"""
    manager = get_platform_alerts_manager()
    return await manager.send_platform_alert(
        fingerprint_id, content_id, platform, violation_url, 
        similarity_score, evidence, **kwargs
    )
