"""🚀 SMS Notification Service - Enterprise Multi-Provider System
================================================================
Module: platform_core/notifications/sms_notification_service.py
Author: Fahed Mlaiel (mlaiel@live.de)
================================================================

⚠️  PROPRIÉTÉ INTELLECTUELLE EXCLUSIVE - FAHED MLAIEL ⚠️
(c) 2025 Fahed Mlaiel. Tous droits réservés.
Contact: mlaiel@live.de

🚨 PROTECTION INTELLECTUELLE:
- Code propriétaire de Fahed Mlaiel
- Utilisation commerciale INTERDITE sans autorisation écrite
- Reverse engineering STRICTEMENT INTERDIT
- Distribution INTERDITE sans licence explicite
- Violation = Poursuites judiciaires automatiques

🏢 USAGE ENTREPRISE:
- Licence entreprise disponible sur demande
- Support technique inclus avec licence
- Maintenance et mises à jour assurées
- Formation équipe technique fournie

🎯 SMS NOTIFICATION SERVICE - MULTI-PROVIDER ENTERPRISE
- Twilio/AWS SNS/MessageBird failover automatique
- Template rendering avec personnalisation IA
- International SMS avec carrier optimization
- Delivery tracking et analytics temps réel
"""

import asyncio
import logging
import json
import re
from typing import Dict, List, Optional, Any, Union
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import aiohttp
import boto3
from botocore.exceptions import ClientError
from twilio.rest import Client as TwilioClient
from twilio.base.exceptions import TwilioException
import phonenumbers
from phonenumbers import carrier, geocoder, timezone

logger = logging.getLogger(__name__)


class SMSProvider(Enum):
    """SMS service providers."""
    TWILIO = "twilio"
    AWS_SNS = "aws_sns"
    MESSAGEBIRD = "messagebird"
    NEXMO = "nexmo"
    PLIVO = "plivo"


class SMSPriority(Enum):
    """SMS priority levels."""
    LOW = 1
    NORMAL = 2
    HIGH = 3
    URGENT = 4


class SMSStatus(Enum):
    """SMS delivery status."""
    PENDING = "pending"
    QUEUED = "queued"
    SENDING = "sending"
    SENT = "sent"
    DELIVERED = "delivered"
    FAILED = "failed"
    UNDELIVERED = "undelivered"


class SMSType(Enum):
    """SMS message types."""
    TRANSACTIONAL = "transactional"
    PROMOTIONAL = "promotional"
    OTP = "otp"
    ALERT = "alert"
    MARKETING = "marketing"


@dataclass
class SMSRecipient:
    """SMS recipient information."""
    phone_number: str
    name: Optional[str] = None
    country_code: Optional[str] = None
    carrier: Optional[str] = None
    timezone: Optional[str] = None
    personalization_data: Dict[str, Any] = field(default_factory=dict)
    opt_in_status: bool = True
    
    def __post_init__(self):
        """Validate and normalize phone number."""
        try:
            parsed = phonenumbers.parse(self.phone_number, self.country_code)
            if phonenumbers.is_valid_number(parsed):
                self.phone_number = phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.E164)
                
                # Extract metadata
                if not self.carrier:
                    self.carrier = carrier.name_for_number(parsed, "en")
                if not self.timezone:
                    timezones = timezone.time_zones_for_number(parsed)
                    if timezones:
                        self.timezone = timezones[0]
                        
        except Exception as e:
            logger.warning(f"Failed to parse phone number {self.phone_number}: {e}")


@dataclass
class SMSTemplate:
    """SMS template configuration."""
    id: str
    name: str
    content_template: str
    variables: List[str] = field(default_factory=list)
    max_length: int = 160
    type: SMSType = SMSType.TRANSACTIONAL
    category: Optional[str] = None
    tags: List[str] = field(default_factory=list)
    compliance_note: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class SMSRequest:
    """SMS sending request."""
    recipients: List[SMSRecipient]
    message: str
    template_id: Optional[str] = None
    template_data: Dict[str, Any] = field(default_factory=dict)
    sender_id: Optional[str] = None
    priority: SMSPriority = SMSPriority.NORMAL
    type: SMSType = SMSType.TRANSACTIONAL
    send_at: Optional[datetime] = None
    tags: List[str] = field(default_factory=list)
    category: Optional[str] = None
    unicode_enabled: bool = True
    flash_sms: bool = False
    validity_period: int = 4320  # minutes (72 hours)
    callback_url: Optional[str] = None


@dataclass
class SMSResult:
    """SMS sending result."""
    message_id: str
    status: SMSStatus
    provider: SMSProvider
    sent_at: datetime
    recipients_count: int
    cost: Optional[float] = None
    segments: int = 1
    error_message: Optional[str] = None
    provider_response: Optional[Dict[str, Any]] = None
    tracking_id: Optional[str] = None


class SMSProviderInterface:
    """Interface for SMS providers."""
    
    async def send_sms(self, request: SMSRequest) -> SMSResult:
        """Send SMS through provider."""
        raise NotImplementedError
    
    async def get_delivery_status(self, message_id: str) -> SMSStatus:
        """Get delivery status for message."""
        raise NotImplementedError
    
    async def handle_webhook(self, payload: Dict[str, Any]) -> None:
        """Handle provider webhook."""
        raise NotImplementedError
    
    async def get_balance(self) -> float:
        """Get account balance."""
        raise NotImplementedError


class TwilioProvider(SMSProviderInterface):
    """Twilio SMS provider implementation."""
    
    def __init__(self, account_sid: str, auth_token: str, from_number: Optional[str] = None):
        self.client = TwilioClient(account_sid, auth_token)
        self.from_number = from_number
        self.account_sid = account_sid
    
    async def send_sms(self, request: SMSRequest) -> SMSResult:
        """Send SMS via Twilio."""
        try:
            sent_messages = []
            total_cost = 0.0
            
            for recipient in request.recipients:
                try:
                    # Create message
                    message = self.client.messages.create(
                        body=request.message,
                        from_=request.sender_id or self.from_number,
                        to=recipient.phone_number,
                        status_callback=request.callback_url,
                        validity_period=request.validity_period,
                        max_price=1.0  # Maximum price per message
                    )
                    
                    sent_messages.append(message)
                    total_cost += float(message.price or 0)
                    
                except TwilioException as e:
                    logger.error(f"Twilio SMS failed for {recipient.phone_number}: {e}")
                    continue
            
            if not sent_messages:
                raise Exception("No messages were sent successfully")
            
            # Use first message for result
            first_message = sent_messages[0]
            
            return SMSResult(
                message_id=first_message.sid,
                status=SMSStatus.SENT,
                provider=SMSProvider.TWILIO,
                sent_at=datetime.utcnow(),
                recipients_count=len(sent_messages),
                cost=total_cost,
                segments=first_message.num_segments,
                provider_response={
                    "messages": [{"sid": msg.sid, "status": msg.status} for msg in sent_messages]
                }
            )
            
        except Exception as e:
            logger.error(f"Twilio SMS failed: {e}")
            return SMSResult(
                message_id="",
                status=SMSStatus.FAILED,
                provider=SMSProvider.TWILIO,
                sent_at=datetime.utcnow(),
                recipients_count=len(request.recipients),
                error_message=str(e)
            )
    
    async def get_delivery_status(self, message_id: str) -> SMSStatus:
        """Get delivery status from Twilio."""
        try:
            message = self.client.messages(message_id).fetch()
            
            status_mapping = {
                'queued': SMSStatus.QUEUED,
                'sending': SMSStatus.SENDING,
                'sent': SMSStatus.SENT,
                'delivered': SMSStatus.DELIVERED,
                'failed': SMSStatus.FAILED,
                'undelivered': SMSStatus.UNDELIVERED
            }
            
            return status_mapping.get(message.status, SMSStatus.PENDING)
            
        except Exception as e:
            logger.error(f"Failed to get Twilio status: {e}")
            return SMSStatus.FAILED
    
    async def handle_webhook(self, payload: Dict[str, Any]) -> None:
        """Handle Twilio webhook events."""
        try:
            message_sid = payload.get('MessageSid')
            message_status = payload.get('MessageStatus')
            
            if message_status == 'delivered':
                logger.info(f"SMS {message_sid} delivered successfully")
            elif message_status in ['failed', 'undelivered']:
                error_code = payload.get('ErrorCode')
                logger.warning(f"SMS {message_sid} failed with error {error_code}")
                
        except Exception as e:
            logger.error(f"Twilio webhook error: {e}")
    
    async def get_balance(self) -> float:
        """Get Twilio account balance."""
        try:
            account = self.client.api.accounts(self.account_sid).fetch()
            return float(account.balance) if account.balance else 0.0
        except Exception as e:
            logger.error(f"Failed to get Twilio balance: {e}")
            return 0.0


class AWSSNSProvider(SMSProviderInterface):
    """AWS SNS SMS provider implementation."""
    
    def __init__(self, access_key: str, secret_key: str, region: str = "us-east-1"):
        self.client = boto3.client(
            'sns',
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key,
            region_name=region
        )
    
    async def send_sms(self, request: SMSRequest) -> SMSResult:
        """Send SMS via AWS SNS."""
        try:
            sent_messages = []
            total_cost = 0.0
            
            for recipient in request.recipients:
                try:
                    # Set SMS attributes
                    attributes = {
                        'AWS.SNS.SMS.SMSType': {
                            'DataType': 'String',
                            'StringValue': 'Transactional' if request.type == SMSType.TRANSACTIONAL else 'Promotional'
                        }
                    }
                    
                    if request.sender_id:
                        attributes['AWS.SNS.SMS.SenderID'] = {
                            'DataType': 'String',
                            'StringValue': request.sender_id
                        }
                    
                    # Send message
                    response = self.client.publish(
                        PhoneNumber=recipient.phone_number,
                        Message=request.message,
                        MessageAttributes=attributes
                    )
                    
                    sent_messages.append(response['MessageId'])
                    total_cost += 0.0075  # Approximate cost per SMS
                    
                except ClientError as e:
                    logger.error(f"AWS SNS SMS failed for {recipient.phone_number}: {e}")
                    continue
            
            if not sent_messages:
                raise Exception("No messages were sent successfully")
            
            return SMSResult(
                message_id=sent_messages[0],
                status=SMSStatus.SENT,
                provider=SMSProvider.AWS_SNS,
                sent_at=datetime.utcnow(),
                recipients_count=len(sent_messages),
                cost=total_cost,
                provider_response={"message_ids": sent_messages}
            )
            
        except Exception as e:
            logger.error(f"AWS SNS SMS failed: {e}")
            return SMSResult(
                message_id="",
                status=SMSStatus.FAILED,
                provider=SMSProvider.AWS_SNS,
                sent_at=datetime.utcnow(),
                recipients_count=len(request.recipients),
                error_message=str(e)
            )
    
    async def get_delivery_status(self, message_id: str) -> SMSStatus:
        """Get delivery status from AWS SNS."""
        try:
            # AWS SNS doesn't provide detailed delivery status
            # Would need to use CloudWatch logs or delivery status feature
            return SMSStatus.SENT
        except Exception as e:
            logger.error(f"Failed to get AWS SNS status: {e}")
            return SMSStatus.FAILED
    
    async def handle_webhook(self, payload: Dict[str, Any]) -> None:
        """Handle AWS SNS webhook events."""
        try:
            # Parse SNS notification
            message = json.loads(payload.get('Message', '{}'))
            notification_type = message.get('notificationType')
            
            if notification_type == 'Delivery':
                logger.info(f"SMS delivered: {message.get('messageId')}")
            elif notification_type == 'Failure':
                logger.warning(f"SMS delivery failed: {message.get('failureReason')}")
                
        except Exception as e:
            logger.error(f"AWS SNS webhook error: {e}")
    
    async def get_balance(self) -> float:
        """Get AWS SNS balance."""
        try:
            # AWS SNS doesn't have a direct balance API
            # Would need to use AWS Billing API
            return 0.0
        except Exception as e:
            logger.error(f"Failed to get AWS SNS balance: {e}")
            return 0.0


class MessageBirdProvider(SMSProviderInterface):
    """MessageBird SMS provider implementation."""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://rest.messagebird.com"
    
    async def send_sms(self, request: SMSRequest) -> SMSResult:
        """Send SMS via MessageBird."""
        try:
            recipients = [recipient.phone_number for recipient in request.recipients]
            
            data = {
                'recipients': recipients,
                'body': request.message,
                'originator': request.sender_id or 'Ainflue'
            }
            
            if request.type == SMSType.TRANSACTIONAL:
                data['type'] = 'sms'
            elif request.type == SMSType.PROMOTIONAL:
                data['type'] = 'sms'
            
            headers = {
                'Authorization': f'AccessKey {self.api_key}',
                'Content-Type': 'application/json'
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.base_url}/messages",
                    json=data,
                    headers=headers
                ) as response:
                    result = await response.json()
                    
                    if response.status == 201:
                        return SMSResult(
                            message_id=result['id'],
                            status=SMSStatus.SENT,
                            provider=SMSProvider.MESSAGEBIRD,
                            sent_at=datetime.utcnow(),
                            recipients_count=len(recipients),
                            provider_response=result
                        )
                    else:
                        raise Exception(f"MessageBird API error: {result}")
                        
        except Exception as e:
            logger.error(f"MessageBird SMS failed: {e}")
            return SMSResult(
                message_id="",
                status=SMSStatus.FAILED,
                provider=SMSProvider.MESSAGEBIRD,
                sent_at=datetime.utcnow(),
                recipients_count=len(request.recipients),
                error_message=str(e)
            )
    
    async def get_delivery_status(self, message_id: str) -> SMSStatus:
        """Get delivery status from MessageBird."""
        try:
            headers = {'Authorization': f'AccessKey {self.api_key}'}
            
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.base_url}/messages/{message_id}",
                    headers=headers
                ) as response:
                    result = await response.json()
                    
                    status_mapping = {
                        'scheduled': SMSStatus.QUEUED,
                        'sent': SMSStatus.SENT,
                        'buffered': SMSStatus.SENDING,
                        'delivered': SMSStatus.DELIVERED,
                        'failed': SMSStatus.FAILED
                    }
                    
                    return status_mapping.get(result.get('status'), SMSStatus.PENDING)
                    
        except Exception as e:
            logger.error(f"Failed to get MessageBird status: {e}")
            return SMSStatus.FAILED
    
    async def handle_webhook(self, payload: Dict[str, Any]) -> None:
        """Handle MessageBird webhook events."""
        try:
            message_id = payload.get('id')
            status = payload.get('status')
            
            if status == 'delivered':
                logger.info(f"SMS {message_id} delivered successfully")
            elif status == 'failed':
                logger.warning(f"SMS {message_id} delivery failed")
                
        except Exception as e:
            logger.error(f"MessageBird webhook error: {e}")
    
    async def get_balance(self) -> float:
        """Get MessageBird balance."""
        try:
            headers = {'Authorization': f'AccessKey {self.api_key}'}
            
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.base_url}/balance",
                    headers=headers
                ) as response:
                    result = await response.json()
                    return float(result.get('amount', 0))
                    
        except Exception as e:
            logger.error(f"Failed to get MessageBird balance: {e}")
            return 0.0


class SMSNotificationService:
    """Enterprise SMS notification service with multi-provider failover."""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.providers: Dict[SMSProvider, SMSProviderInterface] = {}
        self.primary_provider = SMSProvider.TWILIO
        self.failover_providers = [SMSProvider.AWS_SNS, SMSProvider.MESSAGEBIRD]
        self.analytics_data: Dict[str, Any] = {}
        self.opt_out_list: set = set()
        
        # Initialize providers
        self._initialize_providers()
    
    def _initialize_providers(self) -> None:
        """Initialize SMS providers based on configuration."""
        try:
            # Initialize Twilio
            if 'twilio' in self.config:
                self.providers[SMSProvider.TWILIO] = TwilioProvider(
                    self.config['twilio']['account_sid'],
                    self.config['twilio']['auth_token'],
                    self.config['twilio'].get('from_number')
                )
            
            # Initialize AWS SNS
            if 'aws_sns' in self.config:
                self.providers[SMSProvider.AWS_SNS] = AWSSNSProvider(
                    self.config['aws_sns']['access_key'],
                    self.config['aws_sns']['secret_key'],
                    self.config['aws_sns'].get('region', 'us-east-1')
                )
            
            # Initialize MessageBird
            if 'messagebird' in self.config:
                self.providers[SMSProvider.MESSAGEBIRD] = MessageBirdProvider(
                    self.config['messagebird']['api_key']
                )
                
            logger.info(f"Initialized {len(self.providers)} SMS providers")
            
        except Exception as e:
            logger.error(f"Failed to initialize SMS providers: {e}")
    
    async def send_sms(self, request: SMSRequest) -> SMSResult:
        """Send SMS with automatic failover."""
        # Filter opted-out recipients
        original_count = len(request.recipients)
        request.recipients = [r for r in request.recipients if r.phone_number not in self.opt_out_list]
        
        if len(request.recipients) < original_count:
            logger.info(f"Filtered {original_count - len(request.recipients)} opted-out recipients")
        
        if not request.recipients:
            return SMSResult(
                message_id="",
                status=SMSStatus.FAILED,
                provider=self.primary_provider,
                sent_at=datetime.utcnow(),
                recipients_count=0,
                error_message="All recipients have opted out"
            )
        
        # Validate message content
        validation_result = await self._validate_sms_content(request.message, request.type)
        if not validation_result['is_valid']:
            return SMSResult(
                message_id="",
                status=SMSStatus.FAILED,
                provider=self.primary_provider,
                sent_at=datetime.utcnow(),
                recipients_count=len(request.recipients),
                error_message=f"Content validation failed: {validation_result['error']}"
            )
        
        # Try providers with failover
        providers_to_try = [self.primary_provider] + self.failover_providers
        last_error = None
        
        for provider_type in providers_to_try:
            if provider_type not in self.providers:
                continue
                
            try:
                provider = self.providers[provider_type]
                result = await provider.send_sms(request)
                
                if result.status != SMSStatus.FAILED:
                    # Track successful send
                    await self._track_sms_sent(request, result)
                    return result
                    
                last_error = result.error_message
                
            except Exception as e:
                logger.error(f"Provider {provider_type.value} failed: {e}")
                last_error = str(e)
                continue
        
        # All providers failed
        logger.error(f"All SMS providers failed. Last error: {last_error}")
        return SMSResult(
            message_id="",
            status=SMSStatus.FAILED,
            provider=self.primary_provider,
            sent_at=datetime.utcnow(),
            recipients_count=len(request.recipients),
            error_message=f"All providers failed: {last_error}"
        )
    
    async def send_template_sms(self, template_id: str, recipients: List[SMSRecipient], 
                              template_data: Dict[str, Any]) -> SMSResult:
        """Send SMS using template with personalization."""
        try:
            # Load template
            template = await self._load_template(template_id)
            if not template:
                raise ValueError(f"Template {template_id} not found")
            
            # Render template for each recipient
            rendered_messages = []
            for recipient in recipients:
                # Merge global and recipient-specific data
                render_data = {**template_data, **recipient.personalization_data}
                
                # Simple template rendering
                message = template.content_template
                for key, value in render_data.items():
                    message = message.replace(f"{{{{{key}}}}}", str(value))
                
                rendered_messages.append(message)
            
            # Use first rendered message for the request
            if rendered_messages:
                request = SMSRequest(
                    recipients=recipients,
                    message=rendered_messages[0],
                    template_id=template_id,
                    template_data=template_data,
                    type=template.type,
                    category=template.category,
                    tags=template.tags
                )
                
                return await self.send_sms(request)
            
            raise Exception("No messages rendered from template")
            
        except Exception as e:
            logger.error(f"Template SMS failed: {e}")
            return SMSResult(
                message_id="",
                status=SMSStatus.FAILED,
                provider=self.primary_provider,
                sent_at=datetime.utcnow(),
                recipients_count=len(recipients),
                error_message=str(e)
            )
    
    async def _load_template(self, template_id: str) -> Optional[SMSTemplate]:
        """Load SMS template from storage."""
        try:
            # Implementation would load from database
            # For now, return a sample template
            return SMSTemplate(
                id=template_id,
                name=f"Template {template_id}",
                content_template="Welcome to {{platform_name}}, {{user_name}}! Your verification code is {{code}}.",
                variables=["platform_name", "user_name", "code"],
                type=SMSType.OTP,
                category="verification",
                tags=["welcome", "otp"]
            )
            
        except Exception as e:
            logger.error(f"Failed to load template {template_id}: {e}")
            return None
    
    async def _validate_sms_content(self, message: str, sms_type: SMSType) -> Dict[str, Any]:
        """Validate SMS content for compliance."""
        try:
            validation_result = {
                'is_valid': True,
                'error': None,
                'warnings': []
            }
            
            # Check message length
            if len(message) > 1600:  # 10 SMS segments
                validation_result['is_valid'] = False
                validation_result['error'] = "Message too long (max 1600 characters)"
                return validation_result
            
            # Check for promotional content in transactional SMS
            if sms_type == SMSType.TRANSACTIONAL:
                promotional_words = ['sale', 'discount', 'offer', 'deal', 'promotion']
                for word in promotional_words:
                    if word.lower() in message.lower():
                        validation_result['warnings'].append(f"Promotional word '{word}' in transactional SMS")
            
            # Check for required opt-out message in promotional SMS
            if sms_type == SMSType.PROMOTIONAL:
                if 'stop' not in message.lower() and 'unsubscribe' not in message.lower():
                    validation_result['warnings'].append("Missing opt-out instructions in promotional SMS")
            
            # Check for spam indicators
            spam_indicators = ['free money', 'guaranteed', 'act now', 'limited time']
            for indicator in spam_indicators:
                if indicator.lower() in message.lower():
                    validation_result['warnings'].append(f"Potential spam indicator: '{indicator}'")
            
            return validation_result
            
        except Exception as e:
            logger.error(f"SMS content validation failed: {e}")
            return {'is_valid': False, 'error': str(e), 'warnings': []}
    
    async def _track_sms_sent(self, request: SMSRequest, result: SMSResult) -> None:
        """Track SMS sending analytics."""
        try:
            analytics_key = f"sms_analytics_{datetime.utcnow().strftime('%Y-%m-%d')}"
            
            if analytics_key not in self.analytics_data:
                self.analytics_data[analytics_key] = {
                    'total_sent': 0,
                    'total_cost': 0.0,
                    'by_provider': {},
                    'by_type': {},
                    'by_country': {}
                }
            
            analytics = self.analytics_data[analytics_key]
            analytics['total_sent'] += result.recipients_count
            analytics['total_cost'] += result.cost or 0.0
            
            # Track by provider
            provider_key = result.provider.value
            analytics['by_provider'][provider_key] = analytics['by_provider'].get(provider_key, 0) + 1
            
            # Track by type
            type_key = request.type.value
            analytics['by_type'][type_key] = analytics['by_type'].get(type_key, 0) + 1
            
            # Track by country (simplified)
            for recipient in request.recipients:
                try:
                    parsed = phonenumbers.parse(recipient.phone_number, None)
                    country = geocoder.country_name_for_number(parsed, "en")
                    if country:
                        analytics['by_country'][country] = analytics['by_country'].get(country, 0) + 1
                except:
                    pass
            
            logger.info(f"SMS analytics updated: {analytics}")
            
        except Exception as e:
            logger.error(f"Failed to track SMS analytics: {e}")
    
    async def handle_opt_out(self, phone_number: str, keyword: str = "STOP") -> None:
        """Handle SMS opt-out request."""
        try:
            # Normalize phone number
            parsed = phonenumbers.parse(phone_number, None)
            normalized_number = phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.E164)
            
            # Add to opt-out list
            self.opt_out_list.add(normalized_number)
            
            logger.info(f"Phone number {normalized_number} opted out with keyword '{keyword}'")
            
            # Send confirmation SMS
            confirmation_message = "You have successfully unsubscribed from SMS notifications. Reply HELP for assistance or START to resubscribe."
            
            confirmation_request = SMSRequest(
                recipients=[SMSRecipient(phone_number=normalized_number)],
                message=confirmation_message,
                type=SMSType.TRANSACTIONAL
            )
            
            await self.send_sms(confirmation_request)
            
        except Exception as e:
            logger.error(f"Failed to handle opt-out for {phone_number}: {e}")
    
    async def handle_opt_in(self, phone_number: str, keyword: str = "START") -> None:
        """Handle SMS opt-in request."""
        try:
            # Normalize phone number
            parsed = phonenumbers.parse(phone_number, None)
            normalized_number = phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.E164)
            
            # Remove from opt-out list
            self.opt_out_list.discard(normalized_number)
            
            logger.info(f"Phone number {normalized_number} opted in with keyword '{keyword}'")
            
            # Send confirmation SMS
            confirmation_message = "Welcome back! You have resubscribed to SMS notifications. Reply STOP to unsubscribe at any time."
            
            confirmation_request = SMSRequest(
                recipients=[SMSRecipient(phone_number=normalized_number)],
                message=confirmation_message,
                type=SMSType.TRANSACTIONAL
            )
            
            await self.send_sms(confirmation_request)
            
        except Exception as e:
            logger.error(f"Failed to handle opt-in for {phone_number}: {e}")
    
    async def get_analytics(self, date: Optional[datetime] = None) -> Dict[str, Any]:
        """Get SMS analytics for specific date."""
        try:
            if not date:
                date = datetime.utcnow()
            
            analytics_key = f"sms_analytics_{date.strftime('%Y-%m-%d')}"
            return self.analytics_data.get(analytics_key, {})
            
        except Exception as e:
            logger.error(f"Failed to get SMS analytics: {e}")
            return {}
    
    async def get_provider_balance(self, provider: SMSProvider) -> float:
        """Get balance for specific provider."""
        try:
            if provider in self.providers:
                return await self.providers[provider].get_balance()
            return 0.0
        except Exception as e:
            logger.error(f"Failed to get balance for {provider.value}: {e}")
            return 0.0
    
    async def optimize_send_time(self, recipient: SMSRecipient) -> datetime:
        """Optimize SMS send time based on recipient timezone."""
        try:
            if recipient.timezone:
                # Send during appropriate hours (9 AM - 8 PM)
                current_time = datetime.utcnow()
                # Simple timezone handling - in production would use proper timezone conversion
                optimal_hour = 12  # 12 PM
                optimal_time = current_time.replace(
                    hour=optimal_hour,
                    minute=0,
                    second=0,
                    microsecond=0
                )
                
                return optimal_time
            
            # Default to immediate send
            return datetime.utcnow()
            
        except Exception as e:
            logger.error(f"Failed to optimize send time: {e}")
            return datetime.utcnow()


# Factory function for creating service instance
def create_sms_service(config: Dict[str, Any]) -> SMSNotificationService:
    """Create and configure SMS notification service."""
    return SMSNotificationService(config)


# Export main classes and functions
__all__ = [
    'SMSNotificationService',
    'SMSProvider',
    'SMSPriority',
    'SMSStatus',
    'SMSType',
    'SMSRecipient',
    'SMSTemplate',
    'SMSRequest',
    'SMSResult',
    'create_sms_service'
]