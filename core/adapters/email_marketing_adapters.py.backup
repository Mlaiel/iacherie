"""Email Marketing Platform Adapters - Marketing Automation Integration

This module provides comprehensive adapter infrastructure for integrating with
email marketing platforms, newsletter services, and marketing automation tools.

Author: Fahed Mlaiel
Email: mlaiel@live.de
Copyright: All rights reserved. Unauthorized use, reproduction, or distribution
of this code is strictly prohibited without explicit written permission.

Features:
- Multi-platform email marketing support (Mailchimp, SendGrid, Klaviyo, etc.)
- Advanced audience segmentation and targeting
- Automated campaign creation and scheduling
- A/B testing and performance optimization
- Behavioral trigger automation
- Comprehensive analytics and reporting
"""
import asyncio
import logging
from abc import abstractmethod
from typing import Dict, List, Optional, Any, Union, Set
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
import json
import aiohttp
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
import smtplib
from tenacity import retry, stop_after_attempt, wait_exponential

from .base_adapter import (
    BasePlatformAdapter, PlatformType, AdapterStatus, AuthenticationType,
    AdapterCredentials, RateLimitConfig, AdapterError, PlatformError
)

logger = logging.getLogger(__name__)

class EmailPlatform(Enum):
    """Supported email marketing platforms."""
    MAILCHIMP = "mailchimp"
    SENDGRID = "sendgrid"
    KLAVIYO = "klaviyo"
    CONSTANT_CONTACT = "constant_contact"
    CAMPAIGN_MONITOR = "campaign_monitor"
    CONVERTKIT = "convertkit"
    MAILGUN = "mailgun"
    BREVO = "brevo"  # Formerly Sendinblue
    HUBSPOT = "hubspot"
    ACTIVECAMPAIGN = "activecampaign"
    SMTP_CUSTOM = "smtp_custom"

class CampaignType(Enum):
    """Types of email campaigns."""
    NEWSLETTER = "newsletter"
    PROMOTIONAL = "promotional"
    TRANSACTIONAL = "transactional"
    WELCOME_SERIES = "welcome_series"
    DRIP_CAMPAIGN = "drip_campaign"
    BEHAVIORAL_TRIGGER = "behavioral_trigger"
    PRODUCT_ANNOUNCEMENT = "product_announcement"
    EVENT_INVITATION = "event_invitation"
    SURVEY_FEEDBACK = "survey_feedback"
    RE_ENGAGEMENT = "re_engagement"
    ABANDONMENT_RECOVERY = "abandonment_recovery"

class SegmentCriteria(Enum):
    """Audience segmentation criteria."""
    DEMOGRAPHIC = "demographic"
    BEHAVIORAL = "behavioral"
    GEOGRAPHIC = "geographic"
    PSYCHOGRAPHIC = "psychographic"
    PURCHASE_HISTORY = "purchase_history"
    ENGAGEMENT_LEVEL = "engagement_level"
    SUBSCRIPTION_DATE = "subscription_date"
    PLATFORM_ACTIVITY = "platform_activity"
    CONTENT_PREFERENCE = "content_preference"
    DEVICE_TYPE = "device_type"

@dataclass
class EmailContact:
    """Represents an email contact/subscriber."""
    email: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone: Optional[str] = None
    tags: Set[str] = field(default_factory=set)
    custom_fields: Dict[str, Any] = field(default_factory=dict)
    subscription_date: Optional[datetime] = None
    last_engagement: Optional[datetime] = None
    engagement_score: float = 0.0
    status: str = "subscribed"
    source: Optional[str] = None
    preferences: Dict[str, Any] = field(default_factory=dict)

@dataclass
class EmailTemplate:
    """Email template configuration."""
    template_id: str
    name: str
    subject: str
    html_content: str
    text_content: Optional[str] = None
    template_type: CampaignType = CampaignType.NEWSLETTER
    variables: List[str] = field(default_factory=list)
    design_settings: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)
    is_active: bool = True

@dataclass
class EmailCampaign:
    """Email campaign configuration."""
    campaign_id: str
    name: str
    subject: str
    template_id: str
    campaign_type: CampaignType
    target_audience: List[str]  # Contact IDs or segment IDs
    scheduled_at: Optional[datetime] = None
    send_immediately: bool = False
    tracking_settings: Dict[str, bool] = field(default_factory=lambda: {
        'opens': True,
        'clicks': True,
        'bounces': True,
        'unsubscribes': True,
        'forwards': True
    })
    ab_test_settings: Optional[Dict[str, Any]] = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    status: str = "draft"

@dataclass
class CampaignStats:
    """Email campaign performance statistics."""
    campaign_id: str
    sent_count: int
    delivered_count: int
    opened_count: int
    clicked_count: int
    bounced_count: int
    unsubscribed_count: int
    spam_count: int
    delivery_rate: float
    open_rate: float
    click_rate: float
    click_to_open_rate: float
    bounce_rate: float
    unsubscribe_rate: float
    revenue_generated: float = 0.0
    avg_time_to_open: Optional[timedelta] = None
    last_updated: datetime = field(default_factory=datetime.utcnow)

class BaseEmailAdapter(BasePlatformAdapter):
    """Base class for email marketing platform adapters."""
    
    def __init__(
        self, 
        platform_name: str,
        email_platform: EmailPlatform,
        credentials: AdapterCredentials, 
        config: Dict[str, Any]
    ):
        super().__init__(
            platform_name=platform_name,
            platform_type=PlatformType.EMAIL_MARKETING,
            credentials=credentials,
            rate_limit_config=RateLimitConfig(
                requests_per_minute=300,  # Most email platforms are generous
                burst_limit=50,
                rate_limit_window=60
            )
        )
        self.email_platform = email_platform
        self.config = config
        self.contacts: Dict[str, EmailContact] = {}
        self.templates: Dict[str, EmailTemplate] = {}
        self.campaigns: Dict[str, EmailCampaign] = {}
        self.campaign_stats: Dict[str, CampaignStats] = {}
    
    @abstractmethod
    async def create_contact(self, contact: EmailContact) -> bool:
        """Create or update a contact in the email platform."""
        pass
    
    @abstractmethod
    async def create_template(self, template: EmailTemplate) -> bool:
        """Create an email template."""
        pass
    
    @abstractmethod
    async def create_campaign(self, campaign: EmailCampaign) -> bool:
        """Create an email campaign."""
        pass
    
    @abstractmethod
    async def send_campaign(self, campaign_id: str) -> bool:
        """Send an email campaign."""
        pass
    
    @abstractmethod
    async def get_campaign_stats(self, campaign_id: str) -> Optional[CampaignStats]:
        """Get campaign performance statistics."""
        pass
    
    @abstractmethod
    async def create_audience_segment(self, name: str, criteria: Dict[str, Any]) -> str:
        """Create an audience segment based on criteria."""
        pass
    
    async def validate_email(self, email: str) -> bool:
        """Validate email address format."""
        import re
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None
    
    async def calculate_engagement_score(self, contact: EmailContact) -> float:
        """Calculate engagement score for a contact."""
        score = 0.0
        
        # Recent engagement bonus
        if contact.last_engagement:
            days_since_engagement = (datetime.utcnow() - contact.last_engagement).days
            if days_since_engagement <= 7:
                score += 0.4
            elif days_since_engagement <= 30:
                score += 0.3
            elif days_since_engagement <= 90:
                score += 0.2
            else:
                score += 0.1
        
        # Subscription recency
        if contact.subscription_date:
            days_since_subscription = (datetime.utcnow() - contact.subscription_date).days
            if days_since_subscription <= 30:
                score += 0.2
            elif days_since_subscription <= 90:
                score += 0.15
            else:
                score += 0.1
        
        # Tag-based scoring
        engagement_tags = {'highly_engaged', 'frequent_opener', 'frequent_clicker', 'purchaser'}
        tag_bonus = len(contact.tags.intersection(engagement_tags)) * 0.1
        score += min(tag_bonus, 0.3)
        
        # Custom field indicators
        if contact.custom_fields.get('avg_open_rate', 0) > 0.3:
            score += 0.1
        if contact.custom_fields.get('avg_click_rate', 0) > 0.05:
            score += 0.1
        
        return min(score, 1.0)
    
    async def personalize_content(self, content: str, contact: EmailContact) -> str:
        """Personalize email content for a specific contact."""
        personalized = content
        
        # Basic personalization
        if contact.first_name:
            personalized = personalized.replace('{{first_name}}', contact.first_name)
        if contact.last_name:
            personalized = personalized.replace('{{last_name}}', contact.last_name)
        
        # Custom field personalization
        for field, value in contact.custom_fields.items():
            personalized = personalized.replace(f'{{{{{field}}}}}', str(value))
        
        # Behavioral personalization
        if 'music_lover' in contact.tags:
            personalized = personalized.replace('{{music_content}}', 'Check out our latest music releases!')
        
        return personalized

class MailchimpAdapter(BaseEmailAdapter):
    """Mailchimp API adapter implementation."""
    
    def __init__(self, credentials: AdapterCredentials, config: Dict[str, Any]):
        super().__init__(
            platform_name="mailchimp",
            email_platform=EmailPlatform.MAILCHIMP,
            credentials=credentials,
            config=config
        )
        self.api_base_url = f"https://{config.get('datacenter', 'us1')}.api.mailchimp.com/3.0"
        self.audience_id = config.get('audience_id')
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    async def create_contact(self, contact: EmailContact) -> bool:
        """Create or update a contact in Mailchimp."""
        try:
            headers = {
                "Authorization": f"Bearer {self.credentials.api_key}",
                "Content-Type": "application/json"
            }
            
            member_data = {
                "email_address": contact.email,
                "status": contact.status,
                "merge_fields": {
                    "FNAME": contact.first_name or "",
                    "LNAME": contact.last_name or "",
                    "PHONE": contact.phone or ""
                },
                "tags": list(contact.tags),
                "timestamp_signup": contact.subscription_date.isoformat() if contact.subscription_date else None
            }
            
            # Add custom fields
            for field, value in contact.custom_fields.items():
                member_data["merge_fields"][field.upper()] = value
            
            # Use PUT to create or update
            member_hash = hashlib.md5(contact.email.lower().encode()).hexdigest()
            
            async with aiohttp.ClientSession() as session:
                async with session.put(
                    f"{self.api_base_url}/lists/{self.audience_id}/members/{member_hash}",
                    headers=headers,
                    json=member_data
                ) as response:
                    if response.status in [200, 201]:
                        result = await response.json()
                        logger.info(f"Contact created/updated in Mailchimp: {contact.email}")
                        return True
                    else:
                        error_text = await response.text()
                        logger.error(f"Mailchimp contact creation failed: {error_text}")
                        return False
            
        except Exception as e:
            logger.error(f"Mailchimp contact creation error: {str(e)}")
            return False
    
    async def create_template(self, template: EmailTemplate) -> bool:
        """Create an email template in Mailchimp."""
        try:
            headers = {
                "Authorization": f"Bearer {self.credentials.api_key}",
                "Content-Type": "application/json"
            }
            
            template_data = {
                "name": template.name,
                "html": template.html_content,
                "folder_id": self.config.get('template_folder_id'),
                "type": "user"
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.api_base_url}/templates",
                    headers=headers,
                    json=template_data
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        template.template_id = str(result['id'])
                        self.templates[template.template_id] = template
                        logger.info(f"Template created in Mailchimp: {template.name}")
                        return True
                    else:
                        error_text = await response.text()
                        logger.error(f"Mailchimp template creation failed: {error_text}")
                        return False
            
        except Exception as e:
            logger.error(f"Mailchimp template creation error: {str(e)}")
            return False
    
    async def create_campaign(self, campaign: EmailCampaign) -> bool:
        """Create an email campaign in Mailchimp."""
        try:
            headers = {
                "Authorization": f"Bearer {self.credentials.api_key}",
                "Content-Type": "application/json"
            }
            
            # Create campaign
            campaign_data = {
                "type": "regular",
                "recipients": {
                    "list_id": self.audience_id,
                    "segment_opts": {
                        "saved_segment_id": campaign.target_audience[0] if campaign.target_audience else None
                    }
                },
                "settings": {
                    "subject_line": campaign.subject,
                    "title": campaign.name,
                    "from_name": self.config.get('from_name', 'IA Influencer'),
                    "reply_to": self.config.get('reply_to', 'noreply@example.com'),
                    "auto_footer": False,
                    "inline_css": True,
                    "authenticate": True,
                    "auto_tweet": False,
                    "fb_comments": False
                },
                "tracking": {
                    "opens": campaign.tracking_settings.get('opens', True),
                    "html_clicks": campaign.tracking_settings.get('clicks', True),
                    "text_clicks": campaign.tracking_settings.get('clicks', True),
                    "goal_tracking": True,
                    "ecomm360": True
                }
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.api_base_url}/campaigns",
                    headers=headers,
                    json=campaign_data
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        campaign.campaign_id = result['id']
                        
                        # Set campaign content
                        template = self.templates.get(campaign.template_id)
                        if template:
                            content_data = {
                                "html": template.html_content,
                                "plain_text": template.text_content
                            }
                            
                            async with session.put(
                                f"{self.api_base_url}/campaigns/{campaign.campaign_id}/content",
                                headers=headers,
                                json=content_data
                            ) as content_response:
                                if content_response.status == 200:
                                    self.campaigns[campaign.campaign_id] = campaign
                                    logger.info(f"Campaign created in Mailchimp: {campaign.name}")
                                    return True
                        
                        return False
                    else:
                        error_text = await response.text()
                        logger.error(f"Mailchimp campaign creation failed: {error_text}")
                        return False
            
        except Exception as e:
            logger.error(f"Mailchimp campaign creation error: {str(e)}")
            return False
    
    async def send_campaign(self, campaign_id: str) -> bool:
        """Send a Mailchimp campaign."""
        try:
            headers = {
                "Authorization": f"Bearer {self.credentials.api_key}",
                "Content-Type": "application/json"
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.api_base_url}/campaigns/{campaign_id}/actions/send",
                    headers=headers
                ) as response:
                    if response.status == 204:
                        campaign = self.campaigns.get(campaign_id)
                        if campaign:
                            campaign.status = "sent"
                        logger.info(f"Campaign sent in Mailchimp: {campaign_id}")
                        return True
                    else:
                        error_text = await response.text()
                        logger.error(f"Mailchimp campaign send failed: {error_text}")
                        return False
            
        except Exception as e:
            logger.error(f"Mailchimp campaign send error: {str(e)}")
            return False
    
    async def get_campaign_stats(self, campaign_id: str) -> Optional[CampaignStats]:
        """Get Mailchimp campaign statistics."""
        try:
            headers = {
                "Authorization": f"Bearer {self.credentials.api_key}"
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.api_base_url}/campaigns/{campaign_id}",
                    headers=headers
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        stats = CampaignStats(
                            campaign_id=campaign_id,
                            sent_count=data.get('emails_sent', 0),
                            delivered_count=data.get('emails_sent', 0) - data.get('bounces', {}).get('hard_bounces', 0),
                            opened_count=data.get('opens', {}).get('unique_opens', 0),
                            clicked_count=data.get('clicks', {}).get('unique_clicks', 0),
                            bounced_count=data.get('bounces', {}).get('hard_bounces', 0),
                            unsubscribed_count=data.get('unsubscribed', 0),
                            spam_count=data.get('abuse_reports', 0),
                            delivery_rate=0.0,
                            open_rate=0.0,
                            click_rate=0.0,
                            click_to_open_rate=0.0,
                            bounce_rate=0.0,
                            unsubscribe_rate=0.0
                        )
                        
                        # Calculate rates
                        if stats.sent_count > 0:
                            stats.delivery_rate = stats.delivered_count / stats.sent_count
                            stats.open_rate = stats.opened_count / stats.sent_count
                            stats.click_rate = stats.clicked_count / stats.sent_count
                            stats.bounce_rate = stats.bounced_count / stats.sent_count
                            stats.unsubscribe_rate = stats.unsubscribed_count / stats.sent_count
                        
                        if stats.opened_count > 0:
                            stats.click_to_open_rate = stats.clicked_count / stats.opened_count
                        
                        self.campaign_stats[campaign_id] = stats
                        return stats
                    else:
                        logger.error(f"Failed to get Mailchimp campaign stats: {await response.text()}")
                        return None
            
        except Exception as e:
            logger.error(f"Mailchimp campaign stats error: {str(e)}")
            return None
    
    async def create_audience_segment(self, name: str, criteria: Dict[str, Any]) -> str:
        """Create an audience segment in Mailchimp."""
        try:
            headers = {
                "Authorization": f"Bearer {self.credentials.api_key}",
                "Content-Type": "application/json"
            }
            
            # Convert criteria to Mailchimp segment conditions
            conditions = []
            
            if 'tags' in criteria:
                for tag in criteria['tags']:
                    conditions.append({
                        "condition_type": "StaticSegment",
                        "field": "static_segment",
                        "op": "static_is",
                        "value": tag
                    })
            
            if 'engagement_score' in criteria:
                conditions.append({
                    "condition_type": "Rating",
                    "field": "rating",
                    "op": "greater",
                    "value": criteria['engagement_score']
                })
            
            segment_data = {
                "name": name,
                "static_segment": [],
                "options": {
                    "match": "all",
                    "conditions": conditions
                }
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.api_base_url}/lists/{self.audience_id}/segments",
                    headers=headers,
                    json=segment_data
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        logger.info(f"Audience segment created in Mailchimp: {name}")
                        return str(result['id'])
                    else:
                        error_text = await response.text()
                        logger.error(f"Mailchimp segment creation failed: {error_text}")
                        return ""
            
        except Exception as e:
            logger.error(f"Mailchimp segment creation error: {str(e)}")
            return ""

class SendGridAdapter(BaseEmailAdapter):
    """SendGrid API adapter implementation."""
    
    def __init__(self, credentials: AdapterCredentials, config: Dict[str, Any]):
        super().__init__(
            platform_name="sendgrid",
            email_platform=EmailPlatform.SENDGRID,
            credentials=credentials,
            config=config
        )
        self.api_base_url = "https://api.sendgrid.com/v3"
    
    async def create_contact(self, contact: EmailContact) -> bool:
        """Create or update a contact in SendGrid."""
        try:
            headers = {
                "Authorization": f"Bearer {self.credentials.api_key}",
                "Content-Type": "application/json"
            }
            
            contact_data = {
                "contacts": [{
                    "email": contact.email,
                    "first_name": contact.first_name,
                    "last_name": contact.last_name,
                    "phone_number": contact.phone,
                    "custom_fields": contact.custom_fields
                }]
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.put(
                    f"{self.api_base_url}/marketing/contacts",
                    headers=headers,
                    json=contact_data
                ) as response:
                    if response.status == 202:
                        logger.info(f"Contact created/updated in SendGrid: {contact.email}")
                        return True
                    else:
                        error_text = await response.text()
                        logger.error(f"SendGrid contact creation failed: {error_text}")
                        return False
            
        except Exception as e:
            logger.error(f"SendGrid contact creation error: {str(e)}")
            return False
    
    async def create_template(self, template: EmailTemplate) -> bool:
        """Create a template in SendGrid."""
        try:
            headers = {
                "Authorization": f"Bearer {self.credentials.api_key}",
                "Content-Type": "application/json"
            }
            
            template_data = {
                "name": template.name,
                "generation": "dynamic"
            }
            
            async with aiohttp.ClientSession() as session:
                # Create template
                async with session.post(
                    f"{self.api_base_url}/templates",
                    headers=headers,
                    json=template_data
                ) as response:
                    if response.status == 201:
                        result = await response.json()
                        template_id = result['id']
                        
                        # Create template version
                        version_data = {
                            "template_id": template_id,
                            "active": 1,
                            "name": template.name,
                            "html_content": template.html_content,
                            "plain_content": template.text_content or "",
                            "subject": template.subject
                        }
                        
                        async with session.post(
                            f"{self.api_base_url}/templates/{template_id}/versions",
                            headers=headers,
                            json=version_data
                        ) as version_response:
                            if version_response.status == 201:
                                template.template_id = template_id
                                self.templates[template_id] = template
                                logger.info(f"Template created in SendGrid: {template.name}")
                                return True
                    
                    error_text = await response.text()
                    logger.error(f"SendGrid template creation failed: {error_text}")
                    return False
            
        except Exception as e:
            logger.error(f"SendGrid template creation error: {str(e)}")
            return False
    
    async def create_campaign(self, campaign: EmailCampaign) -> bool:
        """Create a campaign in SendGrid."""
        try:
            headers = {
                "Authorization": f"Bearer {self.credentials.api_key}",
                "Content-Type": "application/json"
            }
            
            campaign_data = {
                "name": campaign.name,
                "send_to": {
                    "list_ids": campaign.target_audience
                },
                "email_config": {
                    "subject": campaign.subject,
                    "html_content": self.templates[campaign.template_id].html_content,
                    "plain_content": self.templates[campaign.template_id].text_content,
                    "sender_id": self.config.get('sender_id'),
                    "suppression_group_id": self.config.get('suppression_group_id')
                }
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.api_base_url}/marketing/singlesends",
                    headers=headers,
                    json=campaign_data
                ) as response:
                    if response.status == 201:
                        result = await response.json()
                        campaign.campaign_id = result['id']
                        self.campaigns[campaign.campaign_id] = campaign
                        logger.info(f"Campaign created in SendGrid: {campaign.name}")
                        return True
                    else:
                        error_text = await response.text()
                        logger.error(f"SendGrid campaign creation failed: {error_text}")
                        return False
            
        except Exception as e:
            logger.error(f"SendGrid campaign creation error: {str(e)}")
            return False
    
    async def send_campaign(self, campaign_id: str) -> bool:
        """Send a SendGrid campaign."""
        try:
            headers = {
                "Authorization": f"Bearer {self.credentials.api_key}",
                "Content-Type": "application/json"
            }
            
            send_data = {
                "send_at": "now"
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.put(
                    f"{self.api_base_url}/marketing/singlesends/{campaign_id}/schedule",
                    headers=headers,
                    json=send_data
                ) as response:
                    if response.status == 202:
                        campaign = self.campaigns.get(campaign_id)
                        if campaign:
                            campaign.status = "sent"
                        logger.info(f"Campaign sent in SendGrid: {campaign_id}")
                        return True
                    else:
                        error_text = await response.text()
                        logger.error(f"SendGrid campaign send failed: {error_text}")
                        return False
            
        except Exception as e:
            logger.error(f"SendGrid campaign send error: {str(e)}")
            return False
    
    async def get_campaign_stats(self, campaign_id: str) -> Optional[CampaignStats]:
        """Get SendGrid campaign statistics."""
        try:
            headers = {
                "Authorization": f"Bearer {self.credentials.api_key}"
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.api_base_url}/marketing/singlesends/{campaign_id}/stats",
                    headers=headers
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        # SendGrid provides aggregated stats
                        stats_data = data.get('results', [{}])[0] if data.get('results') else {}
                        
                        stats = CampaignStats(
                            campaign_id=campaign_id,
                            sent_count=stats_data.get('requests', 0),
                            delivered_count=stats_data.get('delivered', 0),
                            opened_count=stats_data.get('unique_opens', 0),
                            clicked_count=stats_data.get('unique_clicks', 0),
                            bounced_count=stats_data.get('bounces', 0),
                            unsubscribed_count=stats_data.get('unsubscribes', 0),
                            spam_count=stats_data.get('spam_reports', 0),
                            delivery_rate=0.0,
                            open_rate=0.0,
                            click_rate=0.0,
                            click_to_open_rate=0.0,
                            bounce_rate=0.0,
                            unsubscribe_rate=0.0
                        )
                        
                        # Calculate rates
                        if stats.sent_count > 0:
                            stats.delivery_rate = stats.delivered_count / stats.sent_count
                            stats.open_rate = stats.opened_count / stats.sent_count
                            stats.click_rate = stats.clicked_count / stats.sent_count
                            stats.bounce_rate = stats.bounced_count / stats.sent_count
                            stats.unsubscribe_rate = stats.unsubscribed_count / stats.sent_count
                        
                        if stats.opened_count > 0:
                            stats.click_to_open_rate = stats.clicked_count / stats.opened_count
                        
                        self.campaign_stats[campaign_id] = stats
                        return stats
                    else:
                        logger.error(f"Failed to get SendGrid campaign stats: {await response.text()}")
                        return None
            
        except Exception as e:
            logger.error(f"SendGrid campaign stats error: {str(e)}")
            return None
    
    async def create_audience_segment(self, name: str, criteria: Dict[str, Any]) -> str:
        """Create an audience segment in SendGrid."""
        try:
            headers = {
                "Authorization": f"Bearer {self.credentials.api_key}",
                "Content-Type": "application/json"
            }
            
            # SendGrid uses contact lists rather than segments
            list_data = {
                "name": name
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.api_base_url}/marketing/lists",
                    headers=headers,
                    json=list_data
                ) as response:
                    if response.status == 201:
                        result = await response.json()
                        logger.info(f"Audience list created in SendGrid: {name}")
                        return result['id']
                    else:
                        error_text = await response.text()
                        logger.error(f"SendGrid list creation failed: {error_text}")
                        return ""
            
        except Exception as e:
            logger.error(f"SendGrid list creation error: {str(e)}")
            return ""

class EmailAdapterFactory:
    """Factory for creating email marketing adapters."""
    
    _adapters = {
        EmailPlatform.MAILCHIMP: MailchimpAdapter,
        EmailPlatform.SENDGRID: SendGridAdapter
    }
    
    @classmethod
    def create_adapter(
        cls, 
        platform: EmailPlatform, 
        credentials: AdapterCredentials, 
        config: Dict[str, Any]
    ) -> BaseEmailAdapter:
        """Create an email adapter instance."""
        adapter_class = cls._adapters.get(platform)
        if not adapter_class:
            raise ValueError(f"Unsupported email platform: {platform}")
        
        return adapter_class(credentials, config)
    
    @classmethod
    def get_supported_platforms(cls) -> List[EmailPlatform]:
        """Get list of supported email platforms."""
        return list(cls._adapters.keys())

class EmailAdapterManager:
    """Manager for email marketing adapter instances and campaign orchestration."""
    
    def __init__(self):
        self.adapters: Dict[EmailPlatform, BaseEmailAdapter] = {}
        self.primary_platform = EmailPlatform.MAILCHIMP
        self.backup_platforms = [EmailPlatform.SENDGRID]
    
    def register_adapter(self, platform: EmailPlatform, adapter: BaseEmailAdapter):
        """Register an email adapter."""
        self.adapters[platform] = adapter
        logger.info(f"Registered email adapter for platform: {platform.value}")
    
    async def sync_contact_across_platforms(self, contact: EmailContact) -> Dict[EmailPlatform, bool]:
        """Sync a contact across all registered platforms."""
        results = {}
        
        for platform, adapter in self.adapters.items():
            try:
                results[platform] = await adapter.create_contact(contact)
            except Exception as e:
                logger.error(f"Failed to sync contact to {platform.value}: {str(e)}")
                results[platform] = False
        
        return results
    
    async def send_multi_platform_campaign(self, campaign: EmailCampaign) -> Dict[EmailPlatform, bool]:
        """Send campaign across multiple platforms for redundancy."""
        results = {}
        
        # Try primary platform first
        if self.primary_platform in self.adapters:
            adapter = self.adapters[self.primary_platform]
            try:
                # Create and send campaign
                if await adapter.create_campaign(campaign):
                    results[self.primary_platform] = await adapter.send_campaign(campaign.campaign_id)
                else:
                    results[self.primary_platform] = False
            except Exception as e:
                logger.error(f"Primary platform {self.primary_platform.value} failed: {str(e)}")
                results[self.primary_platform] = False
        
        # Use backup platforms if primary failed
        if not results.get(self.primary_platform, False):
            for backup_platform in self.backup_platforms:
                if backup_platform in self.adapters:
                    adapter = self.adapters[backup_platform]
                    try:
                        if await adapter.create_campaign(campaign):
                            results[backup_platform] = await adapter.send_campaign(campaign.campaign_id)
                            if results[backup_platform]:
                                break  # Stop on first successful backup
                    except Exception as e:
                        logger.error(f"Backup platform {backup_platform.value} failed: {str(e)}")
                        results[backup_platform] = False
        
        return results
    
    async def get_consolidated_stats(self, campaign_id: str) -> Dict[str, Any]:
        """Get consolidated campaign statistics across platforms."""
        all_stats = {}
        
        for platform, adapter in self.adapters.items():
            try:
                stats = await adapter.get_campaign_stats(campaign_id)
                if stats:
                    all_stats[platform.value] = {
                        'sent_count': stats.sent_count,
                        'delivery_rate': stats.delivery_rate,
                        'open_rate': stats.open_rate,
                        'click_rate': stats.click_rate,
                        'bounce_rate': stats.bounce_rate,
                        'unsubscribe_rate': stats.unsubscribe_rate,
                        'revenue_generated': stats.revenue_generated
                    }
            except Exception as e:
                logger.error(f"Failed to get stats from {platform.value}: {str(e)}")
        
        # Calculate consolidated metrics
        if all_stats:
            total_sent = sum(stats['sent_count'] for stats in all_stats.values())
            if total_sent > 0:
                consolidated = {
                    'total_sent': total_sent,
                    'avg_delivery_rate': sum(stats['delivery_rate'] for stats in all_stats.values()) / len(all_stats),
                    'avg_open_rate': sum(stats['open_rate'] for stats in all_stats.values()) / len(all_stats),
                    'avg_click_rate': sum(stats['click_rate'] for stats in all_stats.values()) / len(all_stats),
                    'total_revenue': sum(stats['revenue_generated'] for stats in all_stats.values()),
                    'platform_breakdown': all_stats
                }
                return consolidated
        
        return {'error': 'No statistics available'}

# Export all classes and functions
__all__ = [
    'EmailPlatform', 'CampaignType', 'SegmentCriteria',
    'EmailContact', 'EmailTemplate', 'EmailCampaign', 'CampaignStats',
    'BaseEmailAdapter', 'MailchimpAdapter', 'SendGridAdapter',
    'EmailAdapterFactory', 'EmailAdapterManager'
]
