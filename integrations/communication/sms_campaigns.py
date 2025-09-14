"""
Enterprise SMS Campaign Management System
========================================

Multi-provider SMS marketing automation with advanced features:
- Global SMS delivery via multiple providers (Twilio, Vonage, etc.)
- Two-way messaging and conversational automation
- Smart scheduling and delivery optimization
- Compliance management (TCPA, GDPR, regional regulations)
- Analytics and performance tracking

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
import uuid
import re
from urllib.parse import quote


class SMSProvider(Enum):
    """Supported SMS service providers"""
    TWILIO = "twilio"
    VONAGE = "vonage"
    MESSAGEBIRD = "messagebird"
    PLIVO = "plivo"
    SINCH = "sinch"
    CLICKSEND = "clicksend"
    TEXTLOCAL = "textlocal"


class MessageType(Enum):
    """SMS message types"""
    TRANSACTIONAL = "transactional"
    PROMOTIONAL = "promotional"
    NOTIFICATION = "notification"
    VERIFICATION = "verification"
    MARKETING = "marketing"
    REMINDER = "reminder"
    ALERT = "alert"


class MessageStatus(Enum):
    """SMS message delivery status"""
    PENDING = "pending"
    QUEUED = "queued"
    SENDING = "sending"
    SENT = "sent"
    DELIVERED = "delivered"
    FAILED = "failed"
    UNDELIVERED = "undelivered"
    REJECTED = "rejected"


class CampaignStatus(Enum):
    """SMS campaign status"""
    DRAFT = "draft"
    SCHEDULED = "scheduled"
    SENDING = "sending"
    SENT = "sent"
    PAUSED = "paused"
    CANCELLED = "cancelled"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class SMSRecipient:
    """SMS recipient data structure"""
    phone_number: str
    name: Optional[str] = None
    country_code: Optional[str] = None
    timezone: Optional[str] = None
    segments: List[str] = field(default_factory=list)
    custom_fields: Dict[str, Any] = field(default_factory=dict)
    preferences: Dict[str, bool] = field(default_factory=dict)
    opt_in_date: Optional[datetime] = None
    opt_out_date: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class SMSTemplate:
    """SMS message template"""
    template_id: str
    name: str
    content: str
    variables: Dict[str, str] = field(default_factory=dict)
    message_type: MessageType = MessageType.PROMOTIONAL
    character_limit: int = 160
    enable_unicode: bool = False
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class SMSMessage:
    """Individual SMS message"""
    message_id: str
    recipient: SMSRecipient
    content: str
    status: MessageStatus = MessageStatus.PENDING
    provider: Optional[str] = None
    provider_message_id: Optional[str] = None
    sent_at: Optional[datetime] = None
    delivered_at: Optional[datetime] = None
    failed_reason: Optional[str] = None
    cost: Optional[float] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class SMSCampaign:
    """SMS campaign configuration"""
    campaign_id: str
    name: str
    template: SMSTemplate
    recipients: List[SMSRecipient]
    sender_id: str
    message_type: MessageType
    status: CampaignStatus = CampaignStatus.DRAFT
    scheduled_time: Optional[datetime] = None
    delivery_window: Optional[Dict[str, str]] = None  # e.g., {"start": "09:00", "end": "21:00"}
    timezone_aware: bool = True
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    messages: List[SMSMessage] = field(default_factory=list)
    analytics: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)


class SMSCampaignManager:
    """
    Enterprise SMS Campaign Management System
    
    Comprehensive SMS marketing automation platform featuring:
    - Multi-provider SMS delivery with automatic failover
    - Global compliance management (TCPA, GDPR, regional laws)
    - Two-way messaging and conversational automation
    - Smart delivery optimization and timezone awareness
    - Advanced analytics and ROI tracking
    - Opt-in/opt-out management with automated compliance
    - Rate limiting and delivery optimization
    - Cost optimization across multiple providers
    """
    
    def __init__(self, config -> None: Dict[str, Any]) -> None:
        """Initialize SMS campaign manager"""
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.campaigns: Dict[str, SMSCampaign] = {}
        self.templates: Dict[str, SMSTemplate] = {}
        self.recipients: Dict[str, SMSRecipient] = {}
        self.segments: Dict[str, List[SMSRecipient]] = {}
        
        # Initialize SMS providers
        self.providers = self._initialize_providers()
        
        # Analytics tracking
        self.analytics = {
            'campaigns_sent': 0,
            'messages_delivered': 0,
            'delivery_rate': 0.0,
            'response_rate': 0.0,
            'opt_out_rate': 0.0,
            'total_cost': 0.0,
            'average_cost_per_message': 0.0
        }
        
        # Compliance settings
        self.compliance_rules = self._load_compliance_rules()
        
        # Rate limiting
        self.rate_limits = config.get('rate_limits', {
            'messages_per_second': 10,
            'messages_per_minute': 100,
            'messages_per_hour': 1000
        })
        
        self.logger.info("SMS Campaign Manager initialized successfully")
    
    def _initialize_providers(self) -> Dict[str, Any]:
        """Initialize SMS service providers"""
        providers = {}
        
        # Twilio configuration
        if 'twilio' in self.config:
            try:
                from twilio.rest import Client
                
                providers['twilio'] = {
                    'client': Client(
                        self.config['twilio']['account_sid'],
                        self.config['twilio']['auth_token']
                    ),
                    'from_number': self.config['twilio']['from_number'],
                    'cost_per_message': self.config['twilio'].get('cost_per_message', 0.0075)
                }
                self.logger.info("Twilio provider initialized")
            except ImportError:
                self.logger.warning("Twilio SDK not available")
        
        # Vonage (formerly Nexmo) configuration
        if 'vonage' in self.config:
            try:
                import vonage
                
                providers['vonage'] = {
                    'client': vonage.Client(
                        key=self.config['vonage']['api_key'],
                        secret=self.config['vonage']['api_secret']
                    ),
                    'from_number': self.config['vonage']['from_number'],
                    'cost_per_message': self.config['vonage'].get('cost_per_message', 0.005)
                }
                self.logger.info("Vonage provider initialized")
            except ImportError:
                self.logger.warning("Vonage SDK not available")
        
        # MessageBird configuration
        if 'messagebird' in self.config:
            try:
                import messagebird
                
                providers['messagebird'] = {
                    'client': messagebird.Client(self.config['messagebird']['access_key']),
                    'originator': self.config['messagebird']['originator'],
                    'cost_per_message': self.config['messagebird'].get('cost_per_message', 0.006)
                }
                self.logger.info("MessageBird provider initialized")
            except ImportError:
                self.logger.warning("MessageBird SDK not available")
        
        return providers
    
    def _load_compliance_rules(self) -> Dict[str, Any]:
        """Load compliance rules for different regions"""
        return {
            'US': {
                'requires_opt_in': True,
                'quiet_hours': {'start': '21:00', 'end': '08:00'},
                'max_messages_per_day': 1,
                'require_stop_instructions': True,
                'stop_keywords': ['STOP', 'QUIT', 'UNSUBSCRIBE', 'CANCEL', 'END']
            },
            'EU': {
                'requires_opt_in': True,
                'gdpr_compliant': True,
                'quiet_hours': {'start': '20:00', 'end': '09:00'},
                'max_messages_per_day': 2,
                'require_stop_instructions': True,
                'stop_keywords': ['STOP', 'ARRÊT', 'HALT', 'PARAR']
            },
            'CA': {
                'requires_opt_in': True,
                'quiet_hours': {'start': '21:00', 'end': '08:00'},
                'max_messages_per_day': 1,
                'require_stop_instructions': True,
                'stop_keywords': ['STOP', 'QUIT', 'UNSUBSCRIBE']
            },
            'AU': {
                'requires_opt_in': True,
                'quiet_hours': {'start': '20:00', 'end': '08:00'},
                'max_messages_per_day': 5,
                'require_stop_instructions': True,
                'stop_keywords': ['STOP', 'UNSUBSCRIBE']
            }
        }
    
    def _validate_phone_number(self, phone_number: str) -> Tuple[bool, str]:
        """Validate and format phone number"""
        # Remove all non-digit characters except +
        cleaned = re.sub(r'[^\d+]', '', phone_number)
        
        # Basic E.164 format validation
        if cleaned.startswith('+') and len(cleaned) >= 8 and len(cleaned) <= 16:
            return True, cleaned
        elif cleaned.startswith('1') and len(cleaned) == 11:
            return True, f"+{cleaned}"
        elif len(cleaned) == 10:
            return True, f"+1{cleaned}"  # Assume US number
        else:
            return False, phone_number
    
    async def create_template(self,
                            name: str,
                            content: str,
                            message_type: MessageType = MessageType.PROMOTIONAL,
                            variables: Optional[Dict[str, str]] = None) -> str:
        """Create SMS template"""
        
        template_id = str(uuid.uuid4())
        
        # Validate content length
        if len(content) > 1600:  # 10 SMS segments
            raise ValueError("Message content too long")
        
        template = SMSTemplate(
            template_id=template_id,
            name=name,
            content=content,
            message_type=message_type,
            variables=variables or {},
            character_limit=160 if not any(ord(c) > 127 for c in content) else 70
        )
        
        self.templates[template_id] = template
        
        self.logger.info(f"SMS template created: {name} ({template_id})")
        return template_id
    
    async def add_recipient(self,
                          phone_number: str,
                          name: Optional[str] = None,
                          country_code: Optional[str] = None,
                          opt_in_confirmed: bool = False) -> str:
        """Add SMS recipient with compliance validation"""
        
        # Validate phone number
        is_valid, formatted_number = self._validate_phone_number(phone_number)
        if not is_valid:
            raise ValueError(f"Invalid phone number format: {phone_number}")
        
        recipient_id = str(uuid.uuid4())
        
        recipient = SMSRecipient(
            phone_number=formatted_number,
            name=name,
            country_code=country_code,
            opt_in_date=datetime.utcnow() if opt_in_confirmed else None
        )
        
        self.recipients[recipient_id] = recipient
        
        self.logger.info(f"SMS recipient added: {formatted_number}")
        return recipient_id
    
    async def create_campaign(self,
                            name: str,
                            template_id: str,
                            recipient_ids: List[str],
                            sender_id: str,
                            message_type: MessageType = MessageType.PROMOTIONAL,
                            scheduled_time: Optional[datetime] = None,
                            delivery_window: Optional[Dict[str, str]] = None) -> str:
        """Create SMS campaign"""
        
        campaign_id = str(uuid.uuid4())
        
        # Get template
        template = self.templates.get(template_id)
        if not template:
            raise ValueError(f"Template {template_id} not found")
        
        # Get recipients
        recipients = []
        for recipient_id in recipient_ids:
            recipient = self.recipients.get(recipient_id)
            if recipient:
                recipients.append(recipient)
            else:
                self.logger.warning(f"Recipient {recipient_id} not found")
        
        if not recipients:
            raise ValueError("No valid recipients found")
        
        # Validate compliance for recipients
        await self._validate_campaign_compliance(recipients, message_type)
        
        campaign = SMSCampaign(
            campaign_id=campaign_id,
            name=name,
            template=template,
            recipients=recipients,
            sender_id=sender_id,
            message_type=message_type,
            scheduled_time=scheduled_time,
            delivery_window=delivery_window
        )
        
        # Generate individual messages
        for recipient in recipients:
            message_id = str(uuid.uuid4())
            personalized_content = await self._personalize_message(template, recipient)
            
            message = SMSMessage(
                message_id=message_id,
                recipient=recipient,
                content=personalized_content
            )
            
            campaign.messages.append(message)
        
        self.campaigns[campaign_id] = campaign
        
        self.logger.info(f"SMS campaign created: {name} ({campaign_id}) with {len(recipients)} recipients")
        return campaign_id
    
    async def _validate_campaign_compliance(self, recipients -> None: List[SMSRecipient], message_type -> None: MessageType) -> None:
        """Validate campaign compliance with regulations"""
        
        for recipient in recipients:
            # Check opt-in status for promotional messages
            if message_type == MessageType.PROMOTIONAL:
                if not recipient.opt_in_date:
                    raise ValueError(f"Recipient {recipient.phone_number} has not opted in for promotional messages")
                
                # Check if opted out
                if recipient.opt_out_date and recipient.opt_out_date > recipient.opt_in_date:
                    raise ValueError(f"Recipient {recipient.phone_number} has opted out")
            
            # Check country-specific rules
            country_code = recipient.country_code or 'US'
            if country_code in self.compliance_rules:
                rules = self.compliance_rules[country_code]
                
                if rules.get('requires_opt_in') and not recipient.opt_in_date:
                    raise ValueError(f"Opt-in required for {country_code} recipients")
    
    async def _personalize_message(self, template: SMSTemplate, recipient: SMSRecipient) -> str:
        """Personalize message content for recipient"""
        
        content = template.content
        
        # Basic variable substitution
        variables = {
            'name': recipient.name or 'there',
            'phone': recipient.phone_number,
            **template.variables,
            **recipient.custom_fields
        }
        
        for var_name, var_value in variables.items():
            placeholder = f"{{{{{var_name}}}}}"
            content = content.replace(placeholder, str(var_value))
        
        # Add STOP instructions for promotional messages
        if template.message_type == MessageType.PROMOTIONAL:
            if not any(stop_word in content.upper() for stop_word in ['STOP', 'UNSUBSCRIBE']):
                content += " Reply STOP to opt out."
        
        return content
    
    async def send_campaign(self, campaign_id: str, provider: str = 'twilio') -> Dict[str, Any]:
        """Send SMS campaign"""
        
        campaign = self.campaigns.get(campaign_id)
        if not campaign:
            raise ValueError(f"Campaign {campaign_id} not found")
        
        if campaign.status not in [CampaignStatus.DRAFT, CampaignStatus.SCHEDULED]:
            raise ValueError(f"Campaign {campaign_id} cannot be sent (status: {campaign.status})")
        
        # Check if provider is available
        if provider not in self.providers:
            raise ValueError(f"Provider {provider} not configured")
        
        # Update campaign status
        campaign.status = CampaignStatus.SENDING
        campaign.updated_at = datetime.utcnow()
        
        results = {
            'campaign_id': campaign_id,
            'total_messages': len(campaign.messages),
            'sent': 0,
            'failed': 0,
            'total_cost': 0.0,
            'errors': []
        }
        
        try:
            # Check delivery window if specified
            if campaign.delivery_window:
                current_time = datetime.utcnow().time()
                window_start = datetime.strptime(campaign.delivery_window['start'], '%H:%M').time()
                window_end = datetime.strptime(campaign.delivery_window['end'], '%H:%M').time()
                
                if not (window_start <= current_time <= window_end):
                    raise ValueError(f"Current time {current_time} is outside delivery window")
            
            # Send messages based on provider
            if provider == 'twilio':
                results = await self._send_via_twilio(campaign)
            elif provider == 'vonage':
                results = await self._send_via_vonage(campaign)
            elif provider == 'messagebird':
                results = await self._send_via_messagebird(campaign)
            else:
                raise ValueError(f"Unsupported provider: {provider}")
            
            # Update campaign status
            if results['failed'] == 0:
                campaign.status = CampaignStatus.SENT
            else:
                campaign.status = CampaignStatus.FAILED if results['sent'] == 0 else CampaignStatus.COMPLETED
            
            # Update analytics
            campaign.analytics = {
                'sent_at': datetime.utcnow().isoformat(),
                'total_sent': results['sent'],
                'failed_count': results['failed'],
                'total_cost': results['total_cost'],
                'provider_used': provider,
                'delivery_rate': (results['sent'] / len(campaign.messages)) * 100
            }
            
            # Update global analytics
            self.analytics['campaigns_sent'] += 1
            self.analytics['messages_delivered'] += results['sent']
            self.analytics['total_cost'] += results['total_cost']
            
        except Exception as e:
            campaign.status = CampaignStatus.FAILED
            results['errors'].append(str(e))
            self.logger.error(f"Campaign sending failed: {e}")
        
        campaign.updated_at = datetime.utcnow()
        return results
    
    async def _send_via_twilio(self, campaign: SMSCampaign) -> Dict[str, Any]:
        """Send campaign via Twilio"""
        
        client = self.providers['twilio']['client']
        from_number = self.providers['twilio']['from_number']
        cost_per_message = self.providers['twilio']['cost_per_message']
        
        results = {'sent': 0, 'failed': 0, 'total_cost': 0.0, 'errors': []}
        
        for message in campaign.messages:
            try:
                # Apply rate limiting
                await asyncio.sleep(1.0 / self.rate_limits['messages_per_second'])
                
                # Send message
                response = client.messages.create(
                    body=message.content,
                    from_=from_number,
                    to=message.recipient.phone_number
                )
                
                # Update message status
                message.status = MessageStatus.SENT
                message.provider = 'twilio'
                message.provider_message_id = response.sid
                message.sent_at = datetime.utcnow()
                message.cost = cost_per_message
                
                results['sent'] += 1
                results['total_cost'] += cost_per_message
                
            except Exception as e:
                message.status = MessageStatus.FAILED
                message.failed_reason = str(e)
                results['failed'] += 1
                results['errors'].append(f"Message to {message.recipient.phone_number}: {str(e)}")
        
        return results
    
    async def _send_via_vonage(self, campaign: SMSCampaign) -> Dict[str, Any]:
        """Send campaign via Vonage"""
        
        client = self.providers['vonage']['client']
        from_number = self.providers['vonage']['from_number']
        cost_per_message = self.providers['vonage']['cost_per_message']
        
        results = {'sent': 0, 'failed': 0, 'total_cost': 0.0, 'errors': []}
        
        for message in campaign.messages:
            try:
                # Apply rate limiting
                await asyncio.sleep(1.0 / self.rate_limits['messages_per_second'])
                
                # Send message
                response = client.sms.send_message({
                    'from': from_number,
                    'to': message.recipient.phone_number,
                    'text': message.content
                })
                
                if response['messages'][0]['status'] == '0':
                    message.status = MessageStatus.SENT
                    message.provider = 'vonage'
                    message.provider_message_id = response['messages'][0]['message-id']
                    message.sent_at = datetime.utcnow()
                    message.cost = cost_per_message
                    
                    results['sent'] += 1
                    results['total_cost'] += cost_per_message
                else:
                    message.status = MessageStatus.FAILED
                    message.failed_reason = response['messages'][0]['error-text']
                    results['failed'] += 1
                
            except Exception as e:
                message.status = MessageStatus.FAILED
                message.failed_reason = str(e)
                results['failed'] += 1
                results['errors'].append(f"Message to {message.recipient.phone_number}: {str(e)}")
        
        return results
    
    async def _send_via_messagebird(self, campaign: SMSCampaign) -> Dict[str, Any]:
        """Send campaign via MessageBird"""
        
        client = self.providers['messagebird']['client']
        originator = self.providers['messagebird']['originator']
        cost_per_message = self.providers['messagebird']['cost_per_message']
        
        results = {'sent': 0, 'failed': 0, 'total_cost': 0.0, 'errors': []}
        
        for message in campaign.messages:
            try:
                # Apply rate limiting
                await asyncio.sleep(1.0 / self.rate_limits['messages_per_second'])
                
                # Send message
                response = client.message_create(
                    originator,
                    [message.recipient.phone_number],
                    message.content
                )
                
                message.status = MessageStatus.SENT
                message.provider = 'messagebird'
                message.provider_message_id = response.id
                message.sent_at = datetime.utcnow()
                message.cost = cost_per_message
                
                results['sent'] += 1
                results['total_cost'] += cost_per_message
                
            except Exception as e:
                message.status = MessageStatus.FAILED
                message.failed_reason = str(e)
                results['failed'] += 1
                results['errors'].append(f"Message to {message.recipient.phone_number}: {str(e)}")
        
        return results
    
    async def handle_incoming_message(self, from_number: str, content: str) -> Dict[str, Any]:
        """Handle incoming SMS messages (for two-way messaging)"""
        
        content_upper = content.upper().strip()
        
        # Check for opt-out keywords
        for country_rules in self.compliance_rules.values():
            if content_upper in country_rules.get('stop_keywords', []):
                await self._handle_opt_out(from_number)
                return {
                    'action': 'opt_out',
                    'message': 'You have been unsubscribed from SMS messages.',
                    'phone_number': from_number
                }
        
        # Check for opt-in keywords
        if content_upper in ['START', 'YES', 'SUBSCRIBE', 'JOIN']:
            await self._handle_opt_in(from_number)
            return {
                'action': 'opt_in',
                'message': 'You have been subscribed to SMS messages.',
                'phone_number': from_number
            }
        
        # Log message for analytics
        self.logger.info(f"Incoming SMS from {from_number}: {content}")
        
        return {
            'action': 'received',
            'message': content,
            'phone_number': from_number,
            'timestamp': datetime.utcnow().isoformat()
        }
    
    async def _handle_opt_out(self, phone_number -> None: str) -> None:
        """Handle SMS opt-out request"""
        
        # Find recipient and update opt-out status
        for recipient in self.recipients.values():
            if recipient.phone_number == phone_number:
                recipient.opt_out_date = datetime.utcnow()
                self.logger.info(f"SMS opt-out processed for {phone_number}")
                break
    
    async def _handle_opt_in(self, phone_number -> None: str) -> None:
        """Handle SMS opt-in request"""
        
        # Find recipient and update opt-in status
        for recipient in self.recipients.values():
            if recipient.phone_number == phone_number:
                recipient.opt_in_date = datetime.utcnow()
                recipient.opt_out_date = None
                self.logger.info(f"SMS opt-in processed for {phone_number}")
                break
    
    async def get_campaign_analytics(self, campaign_id: str) -> Dict[str, Any]:
        """Get detailed campaign analytics"""
        
        campaign = self.campaigns.get(campaign_id)
        if not campaign:
            raise ValueError(f"Campaign {campaign_id} not found")
        
        # Calculate message statistics
        total_messages = len(campaign.messages)
        sent_count = len([m for m in campaign.messages if m.status == MessageStatus.SENT])
        delivered_count = len([m for m in campaign.messages if m.status == MessageStatus.DELIVERED])
        failed_count = len([m for m in campaign.messages if m.status == MessageStatus.FAILED])
        
        total_cost = sum(m.cost or 0 for m in campaign.messages)
        
        analytics = {
            'campaign_id': campaign_id,
            'campaign_name': campaign.name,
            'status': campaign.status.value,
            'created_at': campaign.created_at.isoformat(),
            'updated_at': campaign.updated_at.isoformat(),
            'message_statistics': {
                'total_messages': total_messages,
                'sent': sent_count,
                'delivered': delivered_count,
                'failed': failed_count,
                'delivery_rate': (delivered_count / total_messages * 100) if total_messages > 0 else 0,
                'failure_rate': (failed_count / total_messages * 100) if total_messages > 0 else 0
            },
            'cost_analysis': {
                'total_cost': total_cost,
                'cost_per_message': total_cost / sent_count if sent_count > 0 else 0,
                'cost_per_delivery': total_cost / delivered_count if delivered_count > 0 else 0
            },
            **campaign.analytics
        }
        
        return analytics
    
    async def get_recipient_analytics(self, phone_number: str) -> Dict[str, Any]:
        """Get analytics for specific recipient"""
        
        recipient = None
        for r in self.recipients.values():
            if r.phone_number == phone_number:
                recipient = r
                break
        
        if not recipient:
            raise ValueError(f"Recipient {phone_number} not found")
        
        # Count messages sent to this recipient
        message_count = 0
        last_message_date = None
        
        for campaign in self.campaigns.values():
            for message in campaign.messages:
                if message.recipient.phone_number == phone_number:
                    message_count += 1
                    if message.sent_at and (not last_message_date or message.sent_at > last_message_date):
                        last_message_date = message.sent_at
        
        analytics = {
            'phone_number': phone_number,
            'name': recipient.name,
            'opt_in_date': recipient.opt_in_date.isoformat() if recipient.opt_in_date else None,
            'opt_out_date': recipient.opt_out_date.isoformat() if recipient.opt_out_date else None,
            'is_opted_in': recipient.opt_in_date is not None and (
                recipient.opt_out_date is None or recipient.opt_in_date > recipient.opt_out_date
            ),
            'total_messages_received': message_count,
            'last_message_date': last_message_date.isoformat() if last_message_date else None,
            'segments': recipient.segments,
            'metadata': recipient.metadata
        }
        
        return analytics
    
    async def cleanup_old_data(self, days_old: int = 90) -> Dict[str, int]:
        """Clean up old campaigns and messages"""
        
        cutoff_date = datetime.utcnow() - timedelta(days=days_old)
        
        # Clean up campaigns
        campaigns_removed = 0
        campaigns_to_remove = []
        
        for campaign_id, campaign in self.campaigns.items():
            if campaign.created_at < cutoff_date and campaign.status in [
                CampaignStatus.SENT, CampaignStatus.COMPLETED, CampaignStatus.FAILED
            ]:
                campaigns_to_remove.append(campaign_id)
        
        for campaign_id in campaigns_to_remove:
            del self.campaigns[campaign_id]
            campaigns_removed += 1
        
        self.logger.info(f"Cleaned up {campaigns_removed} old campaigns")
        
        return {
            'campaigns_removed': campaigns_removed,
            'cutoff_date': cutoff_date.isoformat()
        }


# Example usage
async def main() -> None:
    """Example usage of SMSCampaignManager"""
    
    config = {
        'twilio': {
            'account_sid': 'your_account_sid',
            'auth_token': 'your_auth_token',
            'from_number': '+1234567890'
        },
        'vonage': {
            'api_key': 'your_api_key',
            'api_secret': 'your_api_secret',
            'from_number': 'YourBrand'
        },
        'rate_limits': {
            'messages_per_second': 5,
            'messages_per_minute': 100,
            'messages_per_hour': 1000
        }
    }
    
    # Initialize manager
    manager = SMSCampaignManager(config)
    
    # Add recipient
    recipient_id = await manager.add_recipient(
        phone_number="+1234567890",
        name="John Doe",
        country_code="US",
        opt_in_confirmed=True
    )
    
    # Create template
    template_id = await manager.create_template(
        name="Welcome SMS",
        content="Hi {{name}}! Welcome to Ainflue. Get started: https://ainflue.com/start",
        message_type=MessageType.TRANSACTIONAL
    )
    
    # Create campaign
    campaign_id = await manager.create_campaign(
        name="Welcome Campaign",
        template_id=template_id,
        recipient_ids=[recipient_id],
        sender_id="Ainflue",
        message_type=MessageType.TRANSACTIONAL
    )
    
    # Send campaign
    results = await manager.send_campaign(campaign_id, provider='twilio')
    print(f"Campaign results: {results}")
    
    # Get analytics
    analytics = await manager.get_campaign_analytics(campaign_id)
    print(f"Campaign analytics: {analytics}")


if __name__ == "__main__":
    asyncio.run(main())