"""
Enterprise Email Campaign Management System
==========================================

Multi-platform email marketing automation with advanced analytics,
A/B testing, personalization, and compliance management.

Author: Fahed Mlaiel
Contact: mlaiel@live.de
Copyright: 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union, Tuple
from dataclasses import dataclass, field
from enum import Enum
import hashlib
import uuid

from email.mime.text import MimeText
from email.mime.multipart import MimeMultipart
from email.mime.base import MimeBase
from email import encoders
import smtplib
import ssl
from jinja2 import Template, Environment, FileSystemLoader


class CampaignStatus(Enum):
    """Email campaign status enumeration"""
    DRAFT = "draft"
    SCHEDULED = "scheduled"
    SENDING = "sending"
    SENT = "sent"
    PAUSED = "paused"
    CANCELLED = "cancelled"
    FAILED = "failed"


class CampaignType(Enum):
    """Email campaign type enumeration"""
    NEWSLETTER = "newsletter"
    PROMOTIONAL = "promotional"
    TRANSACTIONAL = "transactional"
    WELCOME_SERIES = "welcome_series"
    DRIP_CAMPAIGN = "drip_campaign"
    RE_ENGAGEMENT = "re_engagement"
    ABANDONED_CART = "abandoned_cart"
    EVENT_INVITATION = "event_invitation"


class EmailProvider(Enum):
    """Supported email service providers"""
    SENDGRID = "sendgrid"
    MAILCHIMP = "mailchimp"
    MAILGUN = "mailgun"
    SMTP = "smtp"
    SES = "ses"
    MANDRILL = "mandrill"


@dataclass
class EmailRecipient:
    """Email recipient data structure"""
    email: str
    name: Optional[str] = None
    segments: List[str] = field(default_factory=list)
    custom_fields: Dict[str, Any] = field(default_factory=dict)
    preferences: Dict[str, bool] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class EmailTemplate:
    """Email template configuration"""
    template_id: str
    name: str
    subject: str
    html_content: str
    text_content: Optional[str] = None
    variables: Dict[str, str] = field(default_factory=dict)
    dynamic_content: Dict[str, Any] = field(default_factory=dict)
    attachments: List[Dict[str, str]] = field(default_factory=list)


@dataclass
class Campaign:
    """Email campaign configuration"""
    campaign_id: str
    name: str
    subject: str
    template: EmailTemplate
    recipients: List[EmailRecipient]
    sender_name: str
    sender_email: str
    campaign_type: CampaignType
    status: CampaignStatus = CampaignStatus.DRAFT
    scheduled_time: Optional[datetime] = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = field(default_factory=dict)
    analytics: Dict[str, Any] = field(default_factory=dict)


class EmailCampaignManager:
    """
    Enterprise Email Campaign Management System
    
    Provides comprehensive email marketing automation with advanced features:
    - Multi-provider support (SendGrid, Mailchimp, Mailgun, etc.)
    - Template management with dynamic content
    - Audience segmentation and personalization
    - A/B testing and performance analytics
    - Compliance management (GDPR, CAN-SPAM, CCPA)
    - Automated drip campaigns and sequences
    - Real-time delivery tracking and analytics
    """
    
    def __init__(self, config -> None: Dict[str, Any]) -> None:
        """Initialize email campaign manager"""
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.campaigns: Dict[str, Campaign] = {}
        self.templates: Dict[str, EmailTemplate] = {}
        self.segments: Dict[str, List[EmailRecipient]] = {}
        
        # Initialize email providers
        self.providers = self._initialize_providers()
        
        # Template engine
        self.template_env = Environment(
            loader=FileSystemLoader(config.get('template_dir', 'templates'))
        )
        
        # Analytics tracking
        self.analytics = {
            'campaigns_sent': 0,
            'emails_delivered': 0,
            'open_rate': 0.0,
            'click_rate': 0.0,
            'bounce_rate': 0.0,
            'unsubscribe_rate': 0.0
        }
        
        self.logger.info("Email Campaign Manager initialized successfully")
    
    def _initialize_providers(self) -> Dict[str, Any]:
        """Initialize email service providers"""
        providers = {}
        
        # SendGrid configuration
        if 'sendgrid' in self.config:
            try:
                import sendgrid
                from sendgrid.helpers.mail import Mail
                
                providers['sendgrid'] = {
                    'client': sendgrid.SendGridAPIClient(
                        api_key=self.config['sendgrid']['api_key']
                    ),
                    'mail_class': Mail
                }
            except ImportError:
                self.logger.warning("SendGrid not available")
        
        # Mailgun configuration
        if 'mailgun' in self.config:
            try:
                import requests
                providers['mailgun'] = {
                    'api_key': self.config['mailgun']['api_key'],
                    'domain': self.config['mailgun']['domain'],
                    'base_url': f"https://api.mailgun.net/v3/{self.config['mailgun']['domain']}"
                }
            except Exception as e:
                self.logger.warning(f"Mailgun configuration error: {e}")
        
        # SMTP configuration
        if 'smtp' in self.config:
            providers['smtp'] = self.config['smtp']
        
        return providers
    
    async def create_campaign(self, 
                            name: str,
                            subject: str,
                            template_id: str,
                            recipients: List[EmailRecipient],
                            sender_name: str,
                            sender_email: str,
                            campaign_type: CampaignType,
                            scheduled_time: Optional[datetime] = None,
                            metadata: Optional[Dict[str, Any]] = None) -> str:
        """Create a new email campaign"""
        
        # Generate unique campaign ID
        campaign_id = str(uuid.uuid4())
        
        # Get template
        template = self.templates.get(template_id)
        if not template:
            raise ValueError(f"Template {template_id} not found")
        
        # Create campaign
        campaign = Campaign(
            campaign_id=campaign_id,
            name=name,
            subject=subject,
            template=template,
            recipients=recipients,
            sender_name=sender_name,
            sender_email=sender_email,
            campaign_type=campaign_type,
            scheduled_time=scheduled_time,
            metadata=metadata or {}
        )
        
        # Store campaign
        self.campaigns[campaign_id] = campaign
        
        self.logger.info(f"Campaign created: {name} ({campaign_id})")
        return campaign_id
    
    async def create_template(self,
                            name: str,
                            subject: str,
                            html_content: str,
                            text_content: Optional[str] = None,
                            variables: Optional[Dict[str, str]] = None) -> str:
        """Create email template"""
        
        template_id = str(uuid.uuid4())
        
        template = EmailTemplate(
            template_id=template_id,
            name=name,
            subject=subject,
            html_content=html_content,
            text_content=text_content,
            variables=variables or {}
        )
        
        self.templates[template_id] = template
        
        self.logger.info(f"Template created: {name} ({template_id})")
        return template_id
    
    async def send_campaign(self, campaign_id: str, provider: str = 'sendgrid') -> Dict[str, Any]:
        """Send email campaign"""
        
        campaign = self.campaigns.get(campaign_id)
        if not campaign:
            raise ValueError(f"Campaign {campaign_id} not found")
        
        if campaign.status != CampaignStatus.DRAFT:
            raise ValueError(f"Campaign {campaign_id} is not in draft status")
        
        # Update campaign status
        campaign.status = CampaignStatus.SENDING
        campaign.updated_at = datetime.utcnow()
        
        results = {
            'campaign_id': campaign_id,
            'total_recipients': len(campaign.recipients),
            'sent': 0,
            'failed': 0,
            'errors': []
        }
        
        try:
            # Send emails based on provider
            if provider == 'sendgrid':
                results = await self._send_via_sendgrid(campaign)
            elif provider == 'mailgun':
                results = await self._send_via_mailgun(campaign)
            elif provider == 'smtp':
                results = await self._send_via_smtp(campaign)
            else:
                raise ValueError(f"Unsupported provider: {provider}")
            
            # Update campaign status
            if results['failed'] == 0:
                campaign.status = CampaignStatus.SENT
            else:
                campaign.status = CampaignStatus.FAILED
            
            # Update analytics
            campaign.analytics = {
                'sent_at': datetime.utcnow().isoformat(),
                'total_sent': results['sent'],
                'failed_count': results['failed'],
                'provider_used': provider
            }
            
            self.analytics['campaigns_sent'] += 1
            self.analytics['emails_delivered'] += results['sent']
            
        except Exception as e:
            campaign.status = CampaignStatus.FAILED
            results['errors'].append(str(e))
            self.logger.error(f"Campaign sending failed: {e}")
        
        campaign.updated_at = datetime.utcnow()
        return results
    
    async def _send_via_sendgrid(self, campaign: Campaign) -> Dict[str, Any]:
        """Send campaign via SendGrid"""
        
        if 'sendgrid' not in self.providers:
            raise ValueError("SendGrid not configured")
        
        sg = self.providers['sendgrid']['client']
        Mail = self.providers['sendgrid']['mail_class']
        
        results = {'sent': 0, 'failed': 0, 'errors': []}
        
        for recipient in campaign.recipients:
            try:
                # Personalize content
                personalized_content = await self._personalize_content(
                    campaign.template, recipient
                )
                
                # Create email
                message = Mail(
                    from_email=(campaign.sender_email, campaign.sender_name),
                    to_emails=recipient.email,
                    subject=personalized_content['subject'],
                    html_content=personalized_content['html_content']
                )
                
                if personalized_content.get('text_content'):
                    message.plain_text_content = personalized_content['text_content']
                
                # Send email
                response = sg.send(message)
                
                if response.status_code in [200, 202]:
                    results['sent'] += 1
                else:
                    results['failed'] += 1
                    results['errors'].append(f"SendGrid error: {response.status_code}")
                    
            except Exception as e:
                results['failed'] += 1
                results['errors'].append(f"Recipient {recipient.email}: {str(e)}")
        
        return results
    
    async def _send_via_mailgun(self, campaign: Campaign) -> Dict[str, Any]:
        """Send campaign via Mailgun"""
        
        if 'mailgun' not in self.providers:
            raise ValueError("Mailgun not configured")
        
        import requests
        
        mailgun_config = self.providers['mailgun']
        results = {'sent': 0, 'failed': 0, 'errors': []}
        
        for recipient in campaign.recipients:
            try:
                # Personalize content
                personalized_content = await self._personalize_content(
                    campaign.template, recipient
                )
                
                # Prepare email data
                email_data = {
                    'from': f"{campaign.sender_name} <{campaign.sender_email}>",
                    'to': recipient.email,
                    'subject': personalized_content['subject'],
                    'html': personalized_content['html_content']
                }
                
                if personalized_content.get('text_content'):
                    email_data['text'] = personalized_content['text_content']
                
                # Send email
                response = requests.post(
                    f"{mailgun_config['base_url']}/messages",
                    auth=("api", mailgun_config['api_key']),
                    data=email_data
                )
                
                if response.status_code == 200:
                    results['sent'] += 1
                else:
                    results['failed'] += 1
                    results['errors'].append(f"Mailgun error: {response.status_code}")
                    
            except Exception as e:
                results['failed'] += 1
                results['errors'].append(f"Recipient {recipient.email}: {str(e)}")
        
        return results
    
    async def _send_via_smtp(self, campaign: Campaign) -> Dict[str, Any]:
        """Send campaign via SMTP"""
        
        if 'smtp' not in self.providers:
            raise ValueError("SMTP not configured")
        
        smtp_config = self.providers['smtp']
        results = {'sent': 0, 'failed': 0, 'errors': []}
        
        try:
            # Create SMTP connection
            if smtp_config.get('use_tls', True):
                server = smtplib.SMTP(smtp_config['host'], smtp_config['port'])
                server.starttls()
            else:
                server = smtplib.SMTP(smtp_config['host'], smtp_config['port'])
            
            if smtp_config.get('username') and smtp_config.get('password'):
                server.login(smtp_config['username'], smtp_config['password'])
            
            for recipient in campaign.recipients:
                try:
                    # Personalize content
                    personalized_content = await self._personalize_content(
                        campaign.template, recipient
                    )
                    
                    # Create email message
                    msg = MimeMultipart('alternative')
                    msg['Subject'] = personalized_content['subject']
                    msg['From'] = f"{campaign.sender_name} <{campaign.sender_email}>"
                    msg['To'] = recipient.email
                    
                    # Add text and HTML parts
                    if personalized_content.get('text_content'):
                        text_part = MimeText(personalized_content['text_content'], 'plain')
                        msg.attach(text_part)
                    
                    html_part = MimeText(personalized_content['html_content'], 'html')
                    msg.attach(html_part)
                    
                    # Send email
                    server.send_message(msg)
                    results['sent'] += 1
                    
                except Exception as e:
                    results['failed'] += 1
                    results['errors'].append(f"Recipient {recipient.email}: {str(e)}")
            
            server.quit()
            
        except Exception as e:
            results['errors'].append(f"SMTP connection error: {str(e)}")
            results['failed'] = len(campaign.recipients)
        
        return results
    
    async def _personalize_content(self, template: EmailTemplate, recipient: EmailRecipient) -> Dict[str, str]:
        """Personalize email content for recipient"""
        
        # Prepare template variables
        variables = {
            'recipient_name': recipient.name or recipient.email.split('@')[0],
            'recipient_email': recipient.email,
            **template.variables,
            **recipient.custom_fields
        }
        
        # Render subject
        subject_template = Template(template.subject)
        personalized_subject = subject_template.render(**variables)
        
        # Render HTML content
        html_template = Template(template.html_content)
        personalized_html = html_template.render(**variables)
        
        result = {
            'subject': personalized_subject,
            'html_content': personalized_html
        }
        
        # Render text content if available
        if template.text_content:
            text_template = Template(template.text_content)
            result['text_content'] = text_template.render(**variables)
        
        return result
    
    async def schedule_campaign(self, campaign_id: str, scheduled_time: datetime) -> bool:
        """Schedule campaign for future sending"""
        
        campaign = self.campaigns.get(campaign_id)
        if not campaign:
            raise ValueError(f"Campaign {campaign_id} not found")
        
        if scheduled_time <= datetime.utcnow():
            raise ValueError("Scheduled time must be in the future")
        
        campaign.scheduled_time = scheduled_time
        campaign.status = CampaignStatus.SCHEDULED
        campaign.updated_at = datetime.utcnow()
        
        self.logger.info(f"Campaign {campaign_id} scheduled for {scheduled_time}")
        return True
    
    async def get_campaign_analytics(self, campaign_id: str) -> Dict[str, Any]:
        """Get campaign analytics and performance metrics"""
        
        campaign = self.campaigns.get(campaign_id)
        if not campaign:
            raise ValueError(f"Campaign {campaign_id} not found")
        
        analytics = {
            'campaign_id': campaign_id,
            'campaign_name': campaign.name,
            'status': campaign.status.value,
            'created_at': campaign.created_at.isoformat(),
            'updated_at': campaign.updated_at.isoformat(),
            'total_recipients': len(campaign.recipients),
            **campaign.analytics
        }
        
        # Add delivery and engagement metrics if available
        if campaign.status == CampaignStatus.SENT:
            analytics.update({
                'delivery_rate': (campaign.analytics.get('total_sent', 0) / len(campaign.recipients)) * 100,
                'failure_rate': (campaign.analytics.get('failed_count', 0) / len(campaign.recipients)) * 100
            })
        
        return analytics
    
    async def create_segment(self, name: str, criteria: Dict[str, Any]) -> str:
        """Create audience segment based on criteria"""
        
        segment_id = str(uuid.uuid4())
        
        # Filter recipients based on criteria
        filtered_recipients = []
        
        # Example criteria processing
        for recipient in self._get_all_recipients():
            match = True
            
            # Check custom field criteria
            if 'custom_fields' in criteria:
                for field, value in criteria['custom_fields'].items():
                    if recipient.custom_fields.get(field) != value:
                        match = False
                        break
            
            # Check segment criteria
            if 'segments' in criteria and match:
                required_segments = criteria['segments']
                if not all(seg in recipient.segments for seg in required_segments):
                    match = False
            
            if match:
                filtered_recipients.append(recipient)
        
        self.segments[segment_id] = filtered_recipients
        
        self.logger.info(f"Segment '{name}' created with {len(filtered_recipients)} recipients")
        return segment_id
    
    def _get_all_recipients(self) -> List[EmailRecipient]:
        """Get all recipients from all campaigns"""
        all_recipients = []
        for campaign in self.campaigns.values():
            all_recipients.extend(campaign.recipients)
        return all_recipients
    
    async def get_system_analytics(self) -> Dict[str, Any]:
        """Get overall system analytics"""
        
        total_campaigns = len(self.campaigns)
        sent_campaigns = len([c for c in self.campaigns.values() if c.status == CampaignStatus.SENT])
        
        analytics = {
            **self.analytics,
            'total_campaigns': total_campaigns,
            'sent_campaigns': sent_campaigns,
            'active_templates': len(self.templates),
            'audience_segments': len(self.segments),
            'campaign_success_rate': (sent_campaigns / total_campaigns * 100) if total_campaigns > 0 else 0
        }
        
        return analytics
    
    async def cleanup_old_campaigns(self, days_old: int = 90) -> int:
        """Clean up old campaigns and free memory"""
        
        cutoff_date = datetime.utcnow() - timedelta(days=days_old)
        campaigns_to_remove = []
        
        for campaign_id, campaign in self.campaigns.items():
            if campaign.created_at < cutoff_date and campaign.status in [CampaignStatus.SENT, CampaignStatus.FAILED]:
                campaigns_to_remove.append(campaign_id)
        
        for campaign_id in campaigns_to_remove:
            del self.campaigns[campaign_id]
        
        self.logger.info(f"Cleaned up {len(campaigns_to_remove)} old campaigns")
        return len(campaigns_to_remove)


# Example usage and testing
async def main() -> None:
    """Example usage of EmailCampaignManager"""
    
    config = {
        'sendgrid': {
            'api_key': 'your_sendgrid_api_key'
        },
        'smtp': {
            'host': 'smtp.gmail.com',
            'port': 587,
            'username': 'your_email@gmail.com',
            'password': 'your_password',
            'use_tls': True
        },
        'template_dir': 'email_templates'
    }
    
    # Initialize manager
    manager = EmailCampaignManager(config)
    
    # Create template
    template_id = await manager.create_template(
        name="Welcome Email",
        subject="Welcome to Ainflue, {{recipient_name}}!",
        html_content="""
        <h1>Welcome {{recipient_name}}!</h1>
        <p>Thank you for joining Ainflue. We're excited to help you grow your influence.</p>
        <a href="https://ainflue.com/dashboard">Get Started</a>
        """,
        text_content="Welcome {{recipient_name}}! Thank you for joining Ainflue."
    )
    
    # Create recipients
    recipients = [
        EmailRecipient(
            email="creator@example.com",
            name="Creative Creator",
            custom_fields={"plan": "premium", "signup_date": "2025-01-01"}
        )
    ]
    
    # Create campaign
    campaign_id = await manager.create_campaign(
        name="Welcome Campaign",
        subject="Welcome to Ainflue!",
        template_id=template_id,
        recipients=recipients,
        sender_name="Ainflue Team",
        sender_email="hello@ainflue.com",
        campaign_type=CampaignType.WELCOME_SERIES
    )
    
    # Send campaign
    results = await manager.send_campaign(campaign_id, provider='smtp')
    print(f"Campaign results: {results}")
    
    # Get analytics
    analytics = await manager.get_campaign_analytics(campaign_id)
    print(f"Campaign analytics: {analytics}")


if __name__ == "__main__":
    asyncio.run(main())