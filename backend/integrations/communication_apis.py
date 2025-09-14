"""Communication APIs Integration - Email, SMS, and Notification Services
=======================================================================

Professional integration for automated marketing and user communication
including SendGrid, Mailchimp, Twilio, and Push notifications.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union, AsyncGenerator
from decimal import Decimal
from enum import Enum
from dataclasses import dataclass
import json
import aiohttp
import hashlib
import hmac
import base64
import uuid

logger = logging.getLogger(__name__)


class CommunicationChannel(str, Enum):
    """Supported communication channels."""
    EMAIL = "email"
    SMS = "sms"
    PUSH_NOTIFICATION = "push_notification"
    WHATSAPP = "whatsapp"
    SLACK = "slack"
    DISCORD = "discord"
    WEBHOOK = "webhook"


class MessageType(str, Enum):
    """Message types for communication."""
    TRANSACTIONAL = "transactional"
    MARKETING = "marketing"
    NOTIFICATION = "notification"
    ALERT = "alert"
    REMINDER = "reminder"
    WELCOME = "welcome"
    RETENTION = "retention"


class MessageStatus(str, Enum):
    """Message delivery status."""
    PENDING = "pending"
    SENT = "sent"
    DELIVERED = "delivered"
    OPENED = "opened"
    CLICKED = "clicked"
    FAILED = "failed"
    BOUNCED = "bounced"
    SPAM = "spam"
    UNSUBSCRIBED = "unsubscribed"


class CampaignType(str, Enum):
    """Marketing campaign types."""
    ONBOARDING = "onboarding"
    ENGAGEMENT = "engagement"
    RETENTION = "retention"
    REACTIVATION = "reactivation"
    MONETIZATION = "monetization"
    ANNOUNCEMENT = "announcement"


class TemplateCategory(str, Enum):
    """Template categories."""
    WELCOME = "welcome"
    VERIFICATION = "verification"
    PASSWORD_RESET = "password_reset"
    PAYMENT_CONFIRMATION = "payment_confirmation"
    CONTENT_APPROVED = "content_approved"
    PAYOUT_NOTIFICATION = "payout_notification"
    ENGAGEMENT_UPDATE = "engagement_update"


@dataclass
class CommunicationAccount:
    """Communication service account configuration."""
    channel: CommunicationChannel
    service_name: str
    account_id: str
    credentials: Dict[str, str]
    is_active: bool
    rate_limits: Dict[str, int]
    supported_features: List[str]
    metadata: Dict[str, Any]


@dataclass
class MessageRecipient:
    """Message recipient information."""
    recipient_id: str
    channel: CommunicationChannel
    address: str  # email, phone number, device token, etc.
    name: Optional[str] = None
    preferences: Dict[str, Any] = None
    metadata: Dict[str, Any] = None


@dataclass
class MessageTemplate:
    """Message template configuration."""
    template_id: str
    name: str
    category: TemplateCategory
    channel: CommunicationChannel
    subject: Optional[str] = None
    content: str = ""
    html_content: Optional[str] = None
    variables: List[str] = None
    metadata: Dict[str, Any] = None


@dataclass
class CommunicationMessage:
    """Communication message data."""
    message_id: str
    channel: CommunicationChannel
    message_type: MessageType
    recipient: MessageRecipient
    subject: Optional[str]
    content: str
    html_content: Optional[str]
    template_id: Optional[str]
    status: MessageStatus
    sent_at: Optional[datetime]
    delivered_at: Optional[datetime]
    opened_at: Optional[datetime]
    clicked_at: Optional[datetime]
    metadata: Dict[str, Any]


@dataclass
class MarketingCampaign:
    """Marketing campaign configuration."""
    campaign_id: str
    name: str
    campaign_type: CampaignType
    channels: List[CommunicationChannel]
    target_audience: Dict[str, Any]
    schedule: Dict[str, Any]
    templates: Dict[CommunicationChannel, str]
    status: str
    metrics: Dict[str, Any]
    created_at: datetime
    metadata: Dict[str, Any]


class CommunicationAPIsIntegration:
    """Professional communication APIs integration."""
    
    def __init__(
        self,
        # SendGrid credentials
        sendgrid_api_key -> None: Optional[str] = None,
        sendgrid_from_email -> None: Optional[str] = None,
        # Mailchimp credentials  
        mailchimp_api_key -> None: Optional[str] = None,
        mailchimp_server_prefix -> None: Optional[str] = None,
        # Twilio credentials
        twilio_account_sid -> None: Optional[str] = None,
        twilio_auth_token -> None: Optional[str] = None,
        twilio_phone_number -> None: Optional[str] = None,
        # Firebase/FCM credentials
        fcm_server_key -> None: Optional[str] = None,
        fcm_project_id -> None: Optional[str] = None,
        # Slack credentials
        slack_bot_token -> None: Optional[str] = None,
        slack_webhook_url -> None: Optional[str] = None,
        # General settings
        timeout -> None: int = 30
    ) -> None:
        # Credentials storage
        self.sendgrid_api_key = sendgrid_api_key
        self.sendgrid_from_email = sendgrid_from_email
        self.mailchimp_api_key = mailchimp_api_key
        self.mailchimp_server_prefix = mailchimp_server_prefix
        self.twilio_account_sid = twilio_account_sid
        self.twilio_auth_token = twilio_auth_token
        self.twilio_phone_number = twilio_phone_number
        self.fcm_server_key = fcm_server_key
        self.fcm_project_id = fcm_project_id
        self.slack_bot_token = slack_bot_token
        self.slack_webhook_url = slack_webhook_url
        
        self.timeout = timeout
        self.session: Optional[aiohttp.ClientSession] = None
        
        # Connected accounts storage
        self.communication_accounts: Dict[str, CommunicationAccount] = {}
        self.message_templates: Dict[str, MessageTemplate] = {}
        self.active_campaigns: Dict[str, MarketingCampaign] = {}
        
        # Usage tracking
        self.total_messages_sent = 0
        self.total_campaigns = 0
        self.request_count = 0
        self.channel_usage = {}
        self.engagement_metrics = {
            "total_opens": 0,
            "total_clicks": 0,
            "total_unsubscribes": 0
        }
        
        # Service URLs
        self.service_urls = {
            CommunicationChannel.EMAIL: {
                "sendgrid": "https://api.sendgrid.com/v3",
                "mailchimp": f"https://{mailchimp_server_prefix}.api.mailchimp.com/3.0" if mailchimp_server_prefix else ""
            },
            CommunicationChannel.SMS: {
                "twilio": "https://api.twilio.com/2010-04-01"
            },
            CommunicationChannel.PUSH_NOTIFICATION: {
                "fcm": "https://fcm.googleapis.com/fcm/send"
            },
            CommunicationChannel.SLACK: {
                "api": "https://slack.com/api"
            }
        }
        
        logger.info("Communication APIs integration initialized")
    
    async def __aenter__(self) -> None:
        """Async context manager entry."""
        await self._ensure_session()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        """Async context manager exit."""
        await self.close()
    
    async def _ensure_session(self) -> None:
        """Ensure HTTP session is available."""
        if self.session is None or self.session.closed:
            headers = {
                "User-Agent": "Ainflue/1.0 Communication Hub",
                "Accept": "application/json",
                "Content-Type": "application/json"
            }
            
            self.session = aiohttp.ClientSession(
                headers=headers,
                timeout=aiohttp.ClientTimeout(total=self.timeout)
            )
    
    async def close(self) -> None:
        """Close HTTP session."""
        if self.session and not self.session.closed:
            await self.session.close()
    
    async def initialize_sendgrid_account(self) -> CommunicationAccount:
        """Initialize SendGrid email account."""
        await self._ensure_session()
        
        if not self.sendgrid_api_key:
            raise ValueError("SendGrid API key not configured")
        
        try:
            headers = {"Authorization": f"Bearer {self.sendgrid_api_key}"}
            
            # Test API connection
            async with self.session.get(
                f"{self.service_urls[CommunicationChannel.EMAIL]['sendgrid']}/user/profile",
                headers=headers
            ) as response:
                if response.status != 200:
                    error_data = await response.json()
                    raise Exception(f"SendGrid account error: {error_data}")
                
                profile = await response.json()
                
                account = CommunicationAccount(
                    channel=CommunicationChannel.EMAIL,
                    service_name="SendGrid",
                    account_id=profile.get("username", "unknown"),
                    credentials={"api_key": self.sendgrid_api_key},
                    is_active=True,
                    rate_limits={"per_minute": 600, "daily": 100000},
                    supported_features=["transactional", "marketing", "templates", "analytics"],
                    metadata={"profile": profile}
                )
                
                self.communication_accounts[f"sendgrid_{account.account_id}"] = account
                self.channel_usage[CommunicationChannel.EMAIL] = 0
                self.request_count += 1
                
                logger.info(f"SendGrid account initialized: {account.account_id}")
                return account
        
        except Exception as e:
            logger.error(f"SendGrid account initialization failed: {e}")
            raise
    
    async def initialize_mailchimp_account(self) -> CommunicationAccount:
        """Initialize Mailchimp marketing account."""
        await self._ensure_session()
        
        if not self.mailchimp_api_key or not self.mailchimp_server_prefix:
            raise ValueError("Mailchimp credentials not configured")
        
        try:
            headers = {"Authorization": f"apikey {self.mailchimp_api_key}"}
            
            async with self.session.get(
                f"{self.service_urls[CommunicationChannel.EMAIL]['mailchimp']}/",
                headers=headers
            ) as response:
                if response.status != 200:
                    error_data = await response.json()
                    raise Exception(f"Mailchimp account error: {error_data}")
                
                account_info = await response.json()
                
                account = CommunicationAccount(
                    channel=CommunicationChannel.EMAIL,
                    service_name="Mailchimp",
                    account_id=account_info.get("account_id", "unknown"),
                    credentials={"api_key": self.mailchimp_api_key},
                    is_active=True,
                    rate_limits={"per_minute": 120, "daily": 10000},
                    supported_features=["marketing", "automation", "segmentation", "analytics"],
                    metadata={"account_info": account_info}
                )
                
                self.communication_accounts[f"mailchimp_{account.account_id}"] = account
                self.request_count += 1
                
                logger.info(f"Mailchimp account initialized: {account.account_id}")
                return account
        
        except Exception as e:
            logger.error(f"Mailchimp account initialization failed: {e}")
            raise
    
    async def initialize_twilio_account(self) -> CommunicationAccount:
        """Initialize Twilio SMS account."""
        await self._ensure_session()
        
        if not self.twilio_account_sid or not self.twilio_auth_token:
            raise ValueError("Twilio credentials not configured")
        
        try:
            auth = aiohttp.BasicAuth(self.twilio_account_sid, self.twilio_auth_token)
            
            async with self.session.get(
                f"{self.service_urls[CommunicationChannel.SMS]['twilio']}/Accounts/{self.twilio_account_sid}.json",
                auth=auth
            ) as response:
                if response.status != 200:
                    error_data = await response.json()
                    raise Exception(f"Twilio account error: {error_data}")
                
                account_info = await response.json()
                
                account = CommunicationAccount(
                    channel=CommunicationChannel.SMS,
                    service_name="Twilio",
                    account_id=account_info.get("sid", "unknown"),
                    credentials={"account_sid": self.twilio_account_sid, "auth_token": self.twilio_auth_token},
                    is_active=account_info.get("status") == "active",
                    rate_limits={"per_minute": 600, "daily": 100000},
                    supported_features=["sms", "mms", "voice", "verify"],
                    metadata={"account_info": account_info}
                )
                
                self.communication_accounts[f"twilio_{account.account_id}"] = account
                self.channel_usage[CommunicationChannel.SMS] = 0
                self.request_count += 1
                
                logger.info(f"Twilio account initialized: {account.account_id}")
                return account
        
        except Exception as e:
            logger.error(f"Twilio account initialization failed: {e}")
            raise
    
    async def initialize_fcm_account(self) -> CommunicationAccount:
        """Initialize Firebase Cloud Messaging account."""
        if not self.fcm_server_key or not self.fcm_project_id:
            raise ValueError("FCM credentials not configured")
        
        try:
            account = CommunicationAccount(
                channel=CommunicationChannel.PUSH_NOTIFICATION,
                service_name="Firebase Cloud Messaging",
                account_id=self.fcm_project_id,
                credentials={"server_key": self.fcm_server_key},
                is_active=True,
                rate_limits={"per_minute": 600, "daily": 1000000},
                supported_features=["push_notifications", "topics", "targeting"],
                metadata={"project_id": self.fcm_project_id}
            )
            
            self.communication_accounts[f"fcm_{account.account_id}"] = account
            self.channel_usage[CommunicationChannel.PUSH_NOTIFICATION] = 0
            
            logger.info(f"FCM account initialized: {account.account_id}")
            return account
        
        except Exception as e:
            logger.error(f"FCM account initialization failed: {e}")
            raise
    
    async def create_message_template(
        self,
        name: str,
        category: TemplateCategory,
        channel: CommunicationChannel,
        subject: Optional[str] = None,
        content: str = "",
        html_content: Optional[str] = None,
        variables: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> MessageTemplate:
        """Create a message template."""
        template_id = str(uuid.uuid4())
        
        template = MessageTemplate(
            template_id=template_id,
            name=name,
            category=category,
            channel=channel,
            subject=subject,
            content=content,
            html_content=html_content,
            variables=variables or [],
            metadata=metadata or {}
        )
        
        self.message_templates[template_id] = template
        
        logger.info(f"Message template created: {name} ({template_id})")
        return template
    
    async def send_message(
        self,
        channel: CommunicationChannel,
        recipient: MessageRecipient,
        message_type: MessageType,
        subject: Optional[str] = None,
        content: Optional[str] = None,
        template_id: Optional[str] = None,
        template_variables: Optional[Dict[str, Any]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> CommunicationMessage:
        """Send message through specified channel."""
        await self._ensure_session()
        
        message_id = str(uuid.uuid4())
        
        # Use template if specified
        if template_id and template_id in self.message_templates:
            template = self.message_templates[template_id]
            subject = subject or template.subject
            content = content or template.content
            
            # Replace template variables
            if template_variables:
                for var, value in template_variables.items():
                    if content:
                        content = content.replace(f"{{{var}}}", str(value))
                    if subject:
                        subject = subject.replace(f"{{{var}}}", str(value))
        
        if channel == CommunicationChannel.EMAIL:
            return await self._send_email(message_id, recipient, message_type, subject, content, metadata)
        elif channel == CommunicationChannel.SMS:
            return await self._send_sms(message_id, recipient, message_type, content, metadata)
        elif channel == CommunicationChannel.PUSH_NOTIFICATION:
            return await self._send_push_notification(message_id, recipient, message_type, subject, content, metadata)
        elif channel == CommunicationChannel.SLACK:
            return await self._send_slack_message(message_id, recipient, message_type, content, metadata)
        else:
            raise ValueError(f"Unsupported channel: {channel}")
    
    async def _send_email(
        self,
        message_id: str,
        recipient: MessageRecipient,
        message_type: MessageType,
        subject: str,
        content: str,
        metadata: Dict[str, Any]
    ) -> CommunicationMessage:
        """Send email via SendGrid."""
        try:
            if not self.sendgrid_api_key:
                raise ValueError("SendGrid not configured")
            
            headers = {"Authorization": f"Bearer {self.sendgrid_api_key}"}
            
            email_data = {
                "personalizations": [{
                    "to": [{"email": recipient.address, "name": recipient.name or ""}],
                    "subject": subject
                }],
                "from": {
                    "email": self.sendgrid_from_email,
                    "name": "Ainflue Platform"
                },
                "content": [{
                    "type": "text/plain",
                    "value": content
                }],
                "tracking_settings": {
                    "click_tracking": {"enable": True},
                    "open_tracking": {"enable": True}
                },
                "custom_args": {
                    "message_id": message_id,
                    "message_type": message_type.value,
                    "recipient_id": recipient.recipient_id
                }
            }
            
            async with self.session.post(
                f"{self.service_urls[CommunicationChannel.EMAIL]['sendgrid']}/mail/send",
                json=email_data,
                headers=headers
            ) as response:
                if response.status not in [200, 202]:
                    error_data = await response.text()
                    raise Exception(f"SendGrid email error: {error_data}")
                
                message = CommunicationMessage(
                    message_id=message_id,
                    channel=CommunicationChannel.EMAIL,
                    message_type=message_type,
                    recipient=recipient,
                    subject=subject,
                    content=content,
                    html_content=None,
                    template_id=None,
                    status=MessageStatus.SENT,
                    sent_at=datetime.now(),
                    delivered_at=None,
                    opened_at=None,
                    clicked_at=None,
                    metadata=metadata or {}
                )
                
                self.total_messages_sent += 1
                self.request_count += 1
                self.channel_usage[CommunicationChannel.EMAIL] = self.channel_usage.get(CommunicationChannel.EMAIL, 0) + 1
                
                logger.info(f"Email sent: {message_id} to {recipient.address}")
                return message
        
        except Exception as e:
            logger.error(f"Email sending failed: {e}")
            raise
    
    async def _send_sms(
        self,
        message_id: str,
        recipient: MessageRecipient,
        message_type: MessageType,
        content: str,
        metadata: Dict[str, Any]
    ) -> CommunicationMessage:
        """Send SMS via Twilio."""
        try:
            if not self.twilio_account_sid or not self.twilio_auth_token:
                raise ValueError("Twilio not configured")
            
            auth = aiohttp.BasicAuth(self.twilio_account_sid, self.twilio_auth_token)
            
            sms_data = {
                "From": self.twilio_phone_number,
                "To": recipient.address,
                "Body": content[:1600]  # SMS length limit
            }
            
            async with self.session.post(
                f"{self.service_urls[CommunicationChannel.SMS]['twilio']}/Accounts/{self.twilio_account_sid}/Messages.json",
                data=sms_data,
                auth=auth
            ) as response:
                if response.status not in [200, 201]:
                    error_data = await response.json()
                    raise Exception(f"Twilio SMS error: {error_data}")
                
                result = await response.json()
                
                message = CommunicationMessage(
                    message_id=result["sid"],
                    channel=CommunicationChannel.SMS,
                    message_type=message_type,
                    recipient=recipient,
                    subject=None,
                    content=content,
                    html_content=None,
                    template_id=None,
                    status=MessageStatus.SENT,
                    sent_at=datetime.now(),
                    delivered_at=None,
                    opened_at=None,
                    clicked_at=None,
                    metadata=metadata or {}
                )
                
                self.total_messages_sent += 1
                self.request_count += 1
                self.channel_usage[CommunicationChannel.SMS] = self.channel_usage.get(CommunicationChannel.SMS, 0) + 1
                
                logger.info(f"SMS sent: {message_id} to {recipient.address}")
                return message
        
        except Exception as e:
            logger.error(f"SMS sending failed: {e}")
            raise
    
    async def _send_push_notification(
        self,
        message_id: str,
        recipient: MessageRecipient,
        message_type: MessageType,
        title: str,
        content: str,
        metadata: Dict[str, Any]
    ) -> CommunicationMessage:
        """Send push notification via FCM."""
        try:
            if not self.fcm_server_key:
                raise ValueError("FCM not configured")
            
            headers = {"Authorization": f"key={self.fcm_server_key}"}
            
            notification_data = {
                "to": recipient.address,  # Device token
                "notification": {
                    "title": title,
                    "body": content,
                    "icon": "ic_notification",
                    "click_action": "FLUTTER_NOTIFICATION_CLICK"
                },
                "data": {
                    "message_id": message_id,
                    "message_type": message_type.value,
                    "recipient_id": recipient.recipient_id
                }
            }
            
            async with self.session.post(
                self.service_urls[CommunicationChannel.PUSH_NOTIFICATION]["fcm"],
                json=notification_data,
                headers=headers
            ) as response:
                if response.status != 200:
                    error_data = await response.json()
                    raise Exception(f"FCM push notification error: {error_data}")
                
                result = await response.json()
                
                message = CommunicationMessage(
                    message_id=message_id,
                    channel=CommunicationChannel.PUSH_NOTIFICATION,
                    message_type=message_type,
                    recipient=recipient,
                    subject=title,
                    content=content,
                    html_content=None,
                    template_id=None,
                    status=MessageStatus.SENT if result.get("success") == 1 else MessageStatus.FAILED,
                    sent_at=datetime.now(),
                    delivered_at=None,
                    opened_at=None,
                    clicked_at=None,
                    metadata=metadata or {}
                )
                
                self.total_messages_sent += 1
                self.request_count += 1
                self.channel_usage[CommunicationChannel.PUSH_NOTIFICATION] = self.channel_usage.get(CommunicationChannel.PUSH_NOTIFICATION, 0) + 1
                
                logger.info(f"Push notification sent: {message_id} to {recipient.address}")
                return message
        
        except Exception as e:
            logger.error(f"Push notification sending failed: {e}")
            raise
    
    async def _send_slack_message(
        self,
        message_id: str,
        recipient: MessageRecipient,
        message_type: MessageType,
        content: str,
        metadata: Dict[str, Any]
    ) -> CommunicationMessage:
        """Send Slack message."""
        try:
            if self.slack_webhook_url:
                # Use webhook for simple messages
                slack_data = {
                    "text": content,
                    "channel": recipient.address,
                    "username": "Ainflue Bot"
                }
                
                async with self.session.post(
                    self.slack_webhook_url,
                    json=slack_data
                ) as response:
                    if response.status != 200:
                        error_data = await response.text()
                        raise Exception(f"Slack webhook error: {error_data}")
            
            elif self.slack_bot_token:
                # Use API for advanced features
                headers = {"Authorization": f"Bearer {self.slack_bot_token}"}
                
                slack_data = {
                    "channel": recipient.address,
                    "text": content
                }
                
                async with self.session.post(
                    f"{self.service_urls[CommunicationChannel.SLACK]['api']}/chat.postMessage",
                    json=slack_data,
                    headers=headers
                ) as response:
                    if response.status != 200:
                        error_data = await response.json()
                        raise Exception(f"Slack API error: {error_data}")
            
            else:
                raise ValueError("Slack not configured")
            
            message = CommunicationMessage(
                message_id=message_id,
                channel=CommunicationChannel.SLACK,
                message_type=message_type,
                recipient=recipient,
                subject=None,
                content=content,
                html_content=None,
                template_id=None,
                status=MessageStatus.SENT,
                sent_at=datetime.now(),
                delivered_at=None,
                opened_at=None,
                clicked_at=None,
                metadata=metadata or {}
            )
            
            self.total_messages_sent += 1
            self.request_count += 1
            self.channel_usage[CommunicationChannel.SLACK] = self.channel_usage.get(CommunicationChannel.SLACK, 0) + 1
            
            logger.info(f"Slack message sent: {message_id} to {recipient.address}")
            return message
        
        except Exception as e:
            logger.error(f"Slack message sending failed: {e}")
            raise
    
    async def create_marketing_campaign(
        self,
        name: str,
        campaign_type: CampaignType,
        channels: List[CommunicationChannel],
        target_audience: Dict[str, Any],
        templates: Dict[CommunicationChannel, str],
        schedule: Optional[Dict[str, Any]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> MarketingCampaign:
        """Create a marketing campaign."""
        campaign_id = str(uuid.uuid4())
        
        campaign = MarketingCampaign(
            campaign_id=campaign_id,
            name=name,
            campaign_type=campaign_type,
            channels=channels,
            target_audience=target_audience,
            schedule=schedule or {},
            templates=templates,
            status="draft",
            metrics={
                "total_recipients": 0,
                "messages_sent": 0,
                "delivered": 0,
                "opened": 0,
                "clicked": 0,
                "unsubscribed": 0
            },
            created_at=datetime.now(),
            metadata=metadata or {}
        )
        
        self.active_campaigns[campaign_id] = campaign
        self.total_campaigns += 1
        
        logger.info(f"Marketing campaign created: {name} ({campaign_id})")
        return campaign
    
    async def execute_campaign(
        self,
        campaign_id: str,
        recipients: List[MessageRecipient],
        template_variables: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Execute a marketing campaign."""
        if campaign_id not in self.active_campaigns:
            raise ValueError(f"Campaign not found: {campaign_id}")
        
        campaign = self.active_campaigns[campaign_id]
        results = {"sent": 0, "failed": 0, "details": []}
        
        for recipient in recipients:
            for channel in campaign.channels:
                try:
                    if channel in campaign.templates:
                        template_id = campaign.templates[channel]
                        
                        message = await self.send_message(
                            channel=channel,
                            recipient=recipient,
                            message_type=MessageType.MARKETING,
                            template_id=template_id,
                            template_variables=template_variables,
                            metadata={"campaign_id": campaign_id}
                        )
                        
                        results["sent"] += 1
                        results["details"].append({
                            "recipient": recipient.address,
                            "channel": channel,
                            "status": "sent",
                            "message_id": message.message_id
                        })
                
                except Exception as e:
                    results["failed"] += 1
                    results["details"].append({
                        "recipient": recipient.address,
                        "channel": channel,
                        "status": "failed",
                        "error": str(e)
                    })
                    logger.error(f"Campaign message failed: {e}")
        
        # Update campaign metrics
        campaign.metrics["total_recipients"] = len(recipients)
        campaign.metrics["messages_sent"] += results["sent"]
        campaign.status = "executed"
        
        logger.info(f"Campaign executed: {campaign_id} - {results['sent']} sent, {results['failed']} failed")
        return results
    
    async def send_transactional_email(
        self,
        recipient_email: str,
        template_category: TemplateCategory,
        variables: Dict[str, Any],
        recipient_name: Optional[str] = None
    ) -> CommunicationMessage:
        """Send transactional email using predefined templates."""
        
        # Define default templates for common transactional emails
        default_templates = {
            TemplateCategory.WELCOME: {
                "subject": "Welcome to Ainflue, {name}!",
                "content": "Hi {name},\n\nWelcome to Ainflue! We're excited to have you on board.\n\nBest regards,\nThe Ainflue Team"
            },
            TemplateCategory.VERIFICATION: {
                "subject": "Verify your email address",
                "content": "Hi {name},\n\nPlease verify your email address by clicking the link below:\n{verification_link}\n\nBest regards,\nThe Ainflue Team"
            },
            TemplateCategory.PASSWORD_RESET: {
                "subject": "Reset your password",
                "content": "Hi {name},\n\nYou requested a password reset. Click the link below to reset your password:\n{reset_link}\n\nBest regards,\nThe Ainflue Team"
            },
            TemplateCategory.PAYMENT_CONFIRMATION: {
                "subject": "Payment confirmation - {amount}",
                "content": "Hi {name},\n\nYour payment of {amount} has been processed successfully.\n\nTransaction ID: {transaction_id}\n\nBest regards,\nThe Ainflue Team"
            },
            TemplateCategory.PAYOUT_NOTIFICATION: {
                "subject": "Your payout is ready - {amount}",
                "content": "Hi {name},\n\nYour payout of {amount} has been processed and should arrive within 1-3 business days.\n\nBest regards,\nThe Ainflue Team"
            }
        }
        
        template = default_templates.get(template_category)
        if not template:
            raise ValueError(f"Template not found for category: {template_category}")
        
        # Replace variables in template
        subject = template["subject"]
        content = template["content"]
        
        for var, value in variables.items():
            subject = subject.replace(f"{{{var}}}", str(value))
            content = content.replace(f"{{{var}}}", str(value))
        
        recipient = MessageRecipient(
            recipient_id=recipient_email,
            channel=CommunicationChannel.EMAIL,
            address=recipient_email,
            name=recipient_name
        )
        
        return await self.send_message(
            channel=CommunicationChannel.EMAIL,
            recipient=recipient,
            message_type=MessageType.TRANSACTIONAL,
            subject=subject,
            content=content,
            metadata={"template_category": template_category.value}
        )
    
    async def send_bulk_notifications(
        self,
        recipients: List[MessageRecipient],
        channels: List[CommunicationChannel],
        subject: str,
        content: str,
        message_type: MessageType = MessageType.NOTIFICATION
    ) -> Dict[str, Any]:
        """Send bulk notifications across multiple channels."""
        
        tasks = []
        for recipient in recipients:
            for channel in channels:
                if channel == recipient.channel:
                    task = self.send_message(
                        channel=channel,
                        recipient=recipient,
                        message_type=message_type,
                        subject=subject,
                        content=content
                    )
                    tasks.append(task)
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        successful_sends = [r for r in results if isinstance(r, CommunicationMessage)]
        failed_sends = [r for r in results if isinstance(r, Exception)]
        
        logger.info(f"Bulk notification completed: {len(successful_sends)} sent, {len(failed_sends)} failed")
        
        return {
            "total_attempted": len(tasks),
            "successful": len(successful_sends),
            "failed": len(failed_sends),
            "success_rate": len(successful_sends) / max(len(tasks), 1),
            "successful_messages": successful_sends
        }
    
    async def track_engagement(
        self,
        message_id: str,
        event_type: str,
        timestamp: Optional[datetime] = None
    ) -> bool:
        """Track message engagement events."""
        timestamp = timestamp or datetime.now()
        
        if event_type == "opened":
            self.engagement_metrics["total_opens"] += 1
        elif event_type == "clicked":
            self.engagement_metrics["total_clicks"] += 1
        elif event_type == "unsubscribed":
            self.engagement_metrics["total_unsubscribes"] += 1
        
        logger.info(f"Engagement tracked: {message_id} - {event_type}")
        return True
    
    async def get_campaign_analytics(self, campaign_id: str) -> Dict[str, Any]:
        """Get analytics for a specific campaign."""
        if campaign_id not in self.active_campaigns:
            raise ValueError(f"Campaign not found: {campaign_id}")
        
        campaign = self.active_campaigns[campaign_id]
        
        # Calculate engagement rates
        total_sent = campaign.metrics["messages_sent"]
        open_rate = (campaign.metrics["opened"] / max(total_sent, 1)) * 100
        click_rate = (campaign.metrics["clicked"] / max(total_sent, 1)) * 100
        unsubscribe_rate = (campaign.metrics["unsubscribed"] / max(total_sent, 1)) * 100
        
        analytics = {
            "campaign_id": campaign_id,
            "campaign_name": campaign.name,
            "campaign_type": campaign.campaign_type,
            "status": campaign.status,
            "created_at": campaign.created_at.isoformat(),
            "metrics": campaign.metrics,
            "engagement_rates": {
                "open_rate": round(open_rate, 2),
                "click_rate": round(click_rate, 2),
                "unsubscribe_rate": round(unsubscribe_rate, 2)
            },
            "channels_used": campaign.channels,
            "target_audience": campaign.target_audience
        }
        
        logger.info(f"Campaign analytics retrieved: {campaign_id}")
        return analytics
    
    async def get_communication_accounts(self) -> List[CommunicationAccount]:
        """Get all configured communication accounts."""
        return list(self.communication_accounts.values())
    
    async def get_message_templates(self) -> List[MessageTemplate]:
        """Get all message templates."""
        return list(self.message_templates.values())
    
    def get_usage_stats(self) -> Dict[str, Any]:
        """Get communication usage statistics."""
        return {
            "total_requests": self.request_count,
            "total_messages_sent": self.total_messages_sent,
            "total_campaigns": self.total_campaigns,
            "channel_usage": dict(self.channel_usage),
            "engagement_metrics": dict(self.engagement_metrics),
            "connected_accounts": len(self.communication_accounts),
            "message_templates": len(self.message_templates),
            "active_campaigns": len(self.active_campaigns)
        }


# Utility functions
async def create_communication_apis_integration(
    sendgrid_api_key: Optional[str] = None,
    mailchimp_api_key: Optional[str] = None,
    twilio_account_sid: Optional[str] = None,
    twilio_auth_token: Optional[str] = None
) -> CommunicationAPIsIntegration:
    """Create and initialize communication APIs integration."""
    integration = CommunicationAPIsIntegration(
        sendgrid_api_key=sendgrid_api_key,
        mailchimp_api_key=mailchimp_api_key,
        twilio_account_sid=twilio_account_sid,
        twilio_auth_token=twilio_auth_token
    )
    await integration._ensure_session()
    return integration


async def send_welcome_email_sequence(
    integration: CommunicationAPIsIntegration,
    new_user_email: str,
    user_name: str,
    sequence_days: List[int] = [0, 3, 7, 14]
) -> List[CommunicationMessage]:
    """Send automated welcome email sequence."""
    
    welcome_templates = [
        {
            "day": 0,
            "subject": "Welcome to Ainflue, {name}!",
            "content": "Hi {name},\n\nWelcome to Ainflue! We're excited to have you join our creator community.\n\nGet started by uploading your first content and connecting your social media accounts.\n\nBest regards,\nThe Ainflue Team"
        },
        {
            "day": 3,
            "subject": "Getting started with Ainflue",
            "content": "Hi {name},\n\nHow are you finding Ainflue so far? Here are some tips to help you get the most out of our platform:\n\n1. Connect all your social media accounts\n2. Upload high-quality content\n3. Engage with your audience\n\nNeed help? Reply to this email and we'll assist you!\n\nBest regards,\nThe Ainflue Team"
        },
        {
            "day": 7,
            "subject": "Your first week on Ainflue",
            "content": "Hi {name},\n\nIt's been a week since you joined Ainflue! We hope you're enjoying the platform.\n\nHere's what you can do next:\n- Explore monetization options\n- Check your analytics\n- Join our creator community\n\nKeep creating amazing content!\n\nBest regards,\nThe Ainflue Team"
        },
        {
            "day": 14,
            "subject": "Maximize your earnings on Ainflue",
            "content": "Hi {name},\n\nTwo weeks in! You're becoming a pro at this. Let's talk about maximizing your earnings:\n\n- Optimize your content for engagement\n- Use our AI tools for content creation\n- Set up automated payouts\n\nYour success is our success!\n\nBest regards,\nThe Ainflue Team"
        }
    ]
    
    messages = []
    recipient = MessageRecipient(
        recipient_id=new_user_email,
        channel=CommunicationChannel.EMAIL,
        address=new_user_email,
        name=user_name
    )
    
    for template in welcome_templates:
        if template["day"] in sequence_days:
            variables = {"name": user_name}
            
            message = await integration.send_message(
                channel=CommunicationChannel.EMAIL,
                recipient=recipient,
                message_type=MessageType.WELCOME,
                subject=template["subject"].format(**variables),
                content=template["content"].format(**variables),
                metadata={"sequence_day": template["day"], "sequence_type": "welcome"}
            )
            messages.append(message)
    
    logger.info(f"Welcome email sequence sent to {new_user_email}: {len(messages)} emails")
    return messages


if __name__ == "__main__":
    # Example usage
    async def main() -> None:
        import os
        
        async with CommunicationAPIsIntegration(
            sendgrid_api_key=os.getenv("SENDGRID_API_KEY"),
            sendgrid_from_email=os.getenv("SENDGRID_FROM_EMAIL"),
            twilio_account_sid=os.getenv("TWILIO_ACCOUNT_SID"),
            twilio_auth_token=os.getenv("TWILIO_AUTH_TOKEN")
        ) as comm:
            # Initialize accounts
            try:
                if comm.sendgrid_api_key:
                    sendgrid_account = await comm.initialize_sendgrid_account()
                    print(f"SendGrid account: {sendgrid_account.account_id}")
            except Exception as e:
                print(f"SendGrid initialization failed: {e}")
            
            # Create a welcome email template
            template = await comm.create_message_template(
                name="Welcome Email",
                category=TemplateCategory.WELCOME,
                channel=CommunicationChannel.EMAIL,
                subject="Welcome to Ainflue, {name}!",
                content="Hi {name}, welcome to our platform!"
            )
            print(f"Template created: {template.name}")
            
            # Check usage stats
            stats = comm.get_usage_stats()
            print(f"Usage stats: {stats}")
    
    asyncio.run(main())