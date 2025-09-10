"""
WhatsApp Business Connector for Ainflue Distribution
Provides enterprise-grade integration with WhatsApp Business API

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import json
import logging
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, asdict
from enum import Enum
import uuid
import base64

import aiohttp
import numpy as np
from pydantic import BaseModel, Field, validator

# Configure logging
logger = logging.getLogger(__name__)


class WhatsAppMessageType(str, Enum):
    """WhatsApp message types"""
    TEXT = "text"
    IMAGE = "image"
    VIDEO = "video"
    AUDIO = "audio"
    DOCUMENT = "document"
    TEMPLATE = "template"
    INTERACTIVE = "interactive"
    LOCATION = "location"
    CONTACT = "contact"
    STICKER = "sticker"


class WhatsAppBusinessType(str, Enum):
    """WhatsApp Business account types"""
    BUSINESS = "business"
    ENTERPRISE = "enterprise"
    API = "api"


class MessageStatus(str, Enum):
    """Message delivery status"""
    SENT = "sent"
    DELIVERED = "delivered"
    READ = "read"
    FAILED = "failed"
    PENDING = "pending"


@dataclass
class WhatsAppCredentials:
    """WhatsApp Business API credentials"""
    access_token: str
    phone_number_id: str
    business_account_id: str
    app_id: str
    app_secret: str
    webhook_verify_token: str
    api_version: str = "v18.0"
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class WhatsAppMessage(BaseModel):
    """WhatsApp message model"""
    message_id: Optional[str] = Field(None, description="Message ID after sending")
    recipient: str = Field(..., description="Recipient phone number")
    message_type: WhatsAppMessageType = Field(default=WhatsAppMessageType.TEXT)
    text: Optional[str] = Field(None, description="Message text")
    media_url: Optional[str] = Field(None, description="Media file URL")
    media_caption: Optional[str] = Field(None, description="Media caption")
    template_name: Optional[str] = Field(None, description="Template name")
    template_language: Optional[str] = Field(None, description="Template language")
    template_components: Optional[List[Dict[str, Any]]] = Field(None, description="Template components")
    interactive_data: Optional[Dict[str, Any]] = Field(None, description="Interactive message data")
    scheduled_time: Optional[datetime] = Field(None, description="Scheduled send time")
    context: Optional[Dict[str, Any]] = Field(None, description="Message context")
    
    @validator('scheduled_time')
    def validate_scheduled_time(cls, v):
        if isinstance(v, str):
            return datetime.fromisoformat(v.replace('Z', '+00:00'))
        return v


class WhatsAppContact(BaseModel):
    """WhatsApp contact model"""
    phone_number: str = Field(..., description="Contact phone number")
    display_name: Optional[str] = Field(None, description="Contact display name")
    profile_name: Optional[str] = Field(None, description="Profile name")
    is_business: bool = Field(default=False, description="Business account")
    last_seen: Optional[datetime] = Field(None, description="Last seen timestamp")
    status: str = Field(default="available", description="Contact status")
    
    @validator('last_seen')
    def validate_last_seen(cls, v):
        if isinstance(v, str):
            return datetime.fromisoformat(v.replace('Z', '+00:00'))
        return v


class WhatsAppMetrics(BaseModel):
    """WhatsApp message/campaign metrics"""
    message_id: str
    recipient: str
    status: MessageStatus = MessageStatus.PENDING
    sent_at: Optional[datetime] = None
    delivered_at: Optional[datetime] = None
    read_at: Optional[datetime] = None
    response_received: bool = False
    response_time_seconds: Optional[int] = None
    engagement_score: float = 0.0
    cost: float = 0.0
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class WhatsAppConnector:
    """
    Advanced WhatsApp Business connector for direct customer communication
    Features: Template messaging, interactive messages, media sharing, analytics
    """
    
    def __init__(self, credentials: WhatsAppCredentials):
        self.credentials = credentials
        self.base_url = f"https://graph.facebook.com/{credentials.api_version}"
        self.session: Optional[aiohttp.ClientSession] = None
        self.rate_limits = {
            'messages_per_second': 20,
            'messages_per_minute': 1000,
            'messages_per_day': 100000
        }
        self.message_queue: List[WhatsAppMessage] = []
        self.current_requests = 0
        self.last_reset = datetime.now(timezone.utc)
        self.templates: Dict[str, Dict[str, Any]] = {}
        
    async def __aenter__(self):
        """Async context manager entry"""
        await self.initialize()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        await self.cleanup()
        
    async def initialize(self) -> bool:
        """Initialize WhatsApp Business connector"""
        try:
            self.session = aiohttp.ClientSession(
                headers={
                    'Authorization': f'Bearer {self.credentials.access_token}',
                    'Content-Type': 'application/json'
                },
                timeout=aiohttp.ClientTimeout(total=30)
            )
            
            # Verify phone number
            if await self._verify_phone_number():
                logger.info("WhatsApp Business connector initialized successfully")
                
                # Load message templates
                await self._load_message_templates()
                
                # Start message queue processor
                asyncio.create_task(self._process_message_queue())
                return True
            else:
                logger.error("WhatsApp Business phone number verification failed")
                return False
                
        except Exception as e:
            logger.error(f"Failed to initialize WhatsApp Business connector: {e}")
            return False
            
    async def cleanup(self):
        """Cleanup resources"""
        if self.session:
            await self.session.close()
            
    async def _verify_phone_number(self) -> bool:
        """Verify phone number configuration"""
        try:
            url = f"{self.base_url}/{self.credentials.phone_number_id}"
            
            async with self.session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    phone_info = data
                    logger.info(f"Phone number verified: {phone_info.get('display_phone_number', 'Unknown')}")
                    return True
                return False
                
        except Exception as e:
            logger.error(f"Phone number verification failed: {e}")
            return False
            
    async def _load_message_templates(self):
        """Load approved message templates"""
        try:
            url = f"{self.base_url}/{self.credentials.business_account_id}/message_templates"
            
            async with self.session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    templates = data.get('data', [])
                    
                    for template in templates:
                        if template.get('status') == 'APPROVED':
                            template_name = template.get('name')
                            self.templates[template_name] = template
                            
                    logger.info(f"Loaded {len(self.templates)} approved message templates")
                    
        except Exception as e:
            logger.error(f"Failed to load message templates: {e}")
            
    async def _check_rate_limits(self) -> bool:
        """Check and enforce rate limits"""
        now = datetime.now(timezone.utc)
        if (now - self.last_reset).total_seconds() >= 60:
            self.current_requests = 0
            self.last_reset = now
            
        if self.current_requests >= self.rate_limits['messages_per_minute']:
            logger.warning("Rate limit exceeded, waiting...")
            await asyncio.sleep(60)
            self.current_requests = 0
            
        self.current_requests += 1
        return True
        
    async def send_message(self, message: WhatsAppMessage) -> Dict[str, Any]:
        """
        Send a WhatsApp message
        
        Args:
            message: Message configuration
            
        Returns:
            Send result with message ID
        """
        if message.scheduled_time and message.scheduled_time > datetime.now(timezone.utc):
            # Add to queue for scheduled sending
            self.message_queue.append(message)
            logger.info(f"Message queued for {message.scheduled_time}")
            return {
                'success': True,
                'queued': True,
                'scheduled_time': message.scheduled_time.isoformat()
            }
            
        await self._check_rate_limits()
        
        try:
            if message.message_type == WhatsAppMessageType.TEXT:
                return await self._send_text_message(message)
            elif message.message_type == WhatsAppMessageType.IMAGE:
                return await self._send_image_message(message)
            elif message.message_type == WhatsAppMessageType.VIDEO:
                return await self._send_video_message(message)
            elif message.message_type == WhatsAppMessageType.AUDIO:
                return await self._send_audio_message(message)
            elif message.message_type == WhatsAppMessageType.DOCUMENT:
                return await self._send_document_message(message)
            elif message.message_type == WhatsAppMessageType.TEMPLATE:
                return await self._send_template_message(message)
            elif message.message_type == WhatsAppMessageType.INTERACTIVE:
                return await self._send_interactive_message(message)
            else:
                return {'success': False, 'error': f'Unsupported message type: {message.message_type}'}
                
        except Exception as e:
            logger.error(f"Message send error: {e}")
            return {'success': False, 'error': str(e)}
            
    async def _send_text_message(self, message: WhatsAppMessage) -> Dict[str, Any]:
        """Send text message"""
        url = f"{self.base_url}/{self.credentials.phone_number_id}/messages"
        
        payload = {
            'messaging_product': 'whatsapp',
            'to': message.recipient,
            'type': 'text',
            'text': {
                'body': message.text
            }
        }
        
        if message.context:
            payload['context'] = message.context
            
        async with self.session.post(url, json=payload) as response:
            if response.status == 200:
                data = await response.json()
                if 'messages' in data and data['messages']:
                    message_id = data['messages'][0].get('id')
                    logger.info(f"Text message sent successfully: {message_id}")
                    return {
                        'success': True,
                        'message_id': message_id,
                        'recipient': message.recipient
                    }
                    
            error_text = await response.text()
            logger.error(f"Failed to send text message: {error_text}")
            return {'success': False, 'error': error_text}
            
    async def _send_image_message(self, message: WhatsAppMessage) -> Dict[str, Any]:
        """Send image message"""
        url = f"{self.base_url}/{self.credentials.phone_number_id}/messages"
        
        payload = {
            'messaging_product': 'whatsapp',
            'to': message.recipient,
            'type': 'image',
            'image': {
                'link': message.media_url
            }
        }
        
        if message.media_caption:
            payload['image']['caption'] = message.media_caption
            
        if message.context:
            payload['context'] = message.context
            
        async with self.session.post(url, json=payload) as response:
            if response.status == 200:
                data = await response.json()
                if 'messages' in data and data['messages']:
                    message_id = data['messages'][0].get('id')
                    logger.info(f"Image message sent successfully: {message_id}")
                    return {
                        'success': True,
                        'message_id': message_id,
                        'recipient': message.recipient
                    }
                    
            error_text = await response.text()
            logger.error(f"Failed to send image message: {error_text}")
            return {'success': False, 'error': error_text}
            
    async def _send_video_message(self, message: WhatsAppMessage) -> Dict[str, Any]:
        """Send video message"""
        url = f"{self.base_url}/{self.credentials.phone_number_id}/messages"
        
        payload = {
            'messaging_product': 'whatsapp',
            'to': message.recipient,
            'type': 'video',
            'video': {
                'link': message.media_url
            }
        }
        
        if message.media_caption:
            payload['video']['caption'] = message.media_caption
            
        if message.context:
            payload['context'] = message.context
            
        async with self.session.post(url, json=payload) as response:
            if response.status == 200:
                data = await response.json()
                if 'messages' in data and data['messages']:
                    message_id = data['messages'][0].get('id')
                    logger.info(f"Video message sent successfully: {message_id}")
                    return {
                        'success': True,
                        'message_id': message_id,
                        'recipient': message.recipient
                    }
                    
            error_text = await response.text()
            logger.error(f"Failed to send video message: {error_text}")
            return {'success': False, 'error': error_text}
            
    async def _send_audio_message(self, message: WhatsAppMessage) -> Dict[str, Any]:
        """Send audio message"""
        url = f"{self.base_url}/{self.credentials.phone_number_id}/messages"
        
        payload = {
            'messaging_product': 'whatsapp',
            'to': message.recipient,
            'type': 'audio',
            'audio': {
                'link': message.media_url
            }
        }
        
        if message.context:
            payload['context'] = message.context
            
        async with self.session.post(url, json=payload) as response:
            if response.status == 200:
                data = await response.json()
                if 'messages' in data and data['messages']:
                    message_id = data['messages'][0].get('id')
                    logger.info(f"Audio message sent successfully: {message_id}")
                    return {
                        'success': True,
                        'message_id': message_id,
                        'recipient': message.recipient
                    }
                    
            error_text = await response.text()
            logger.error(f"Failed to send audio message: {error_text}")
            return {'success': False, 'error': error_text}
            
    async def _send_document_message(self, message: WhatsAppMessage) -> Dict[str, Any]:
        """Send document message"""
        url = f"{self.base_url}/{self.credentials.phone_number_id}/messages"
        
        payload = {
            'messaging_product': 'whatsapp',
            'to': message.recipient,
            'type': 'document',
            'document': {
                'link': message.media_url
            }
        }
        
        if message.media_caption:
            payload['document']['caption'] = message.media_caption
            
        if message.context:
            payload['context'] = message.context
            
        async with self.session.post(url, json=payload) as response:
            if response.status == 200:
                data = await response.json()
                if 'messages' in data and data['messages']:
                    message_id = data['messages'][0].get('id')
                    logger.info(f"Document message sent successfully: {message_id}")
                    return {
                        'success': True,
                        'message_id': message_id,
                        'recipient': message.recipient
                    }
                    
            error_text = await response.text()
            logger.error(f"Failed to send document message: {error_text}")
            return {'success': False, 'error': error_text}
            
    async def _send_template_message(self, message: WhatsAppMessage) -> Dict[str, Any]:
        """Send template message"""
        if not message.template_name or message.template_name not in self.templates:
            return {'success': False, 'error': 'Invalid or unapproved template'}
            
        url = f"{self.base_url}/{self.credentials.phone_number_id}/messages"
        
        payload = {
            'messaging_product': 'whatsapp',
            'to': message.recipient,
            'type': 'template',
            'template': {
                'name': message.template_name,
                'language': {
                    'code': message.template_language or 'en'
                }
            }
        }
        
        if message.template_components:
            payload['template']['components'] = message.template_components
            
        async with self.session.post(url, json=payload) as response:
            if response.status == 200:
                data = await response.json()
                if 'messages' in data and data['messages']:
                    message_id = data['messages'][0].get('id')
                    logger.info(f"Template message sent successfully: {message_id}")
                    return {
                        'success': True,
                        'message_id': message_id,
                        'recipient': message.recipient,
                        'template': message.template_name
                    }
                    
            error_text = await response.text()
            logger.error(f"Failed to send template message: {error_text}")
            return {'success': False, 'error': error_text}
            
    async def _send_interactive_message(self, message: WhatsAppMessage) -> Dict[str, Any]:
        """Send interactive message (buttons, lists)"""
        if not message.interactive_data:
            return {'success': False, 'error': 'Interactive data required'}
            
        url = f"{self.base_url}/{self.credentials.phone_number_id}/messages"
        
        payload = {
            'messaging_product': 'whatsapp',
            'to': message.recipient,
            'type': 'interactive',
            'interactive': message.interactive_data
        }
        
        if message.context:
            payload['context'] = message.context
            
        async with self.session.post(url, json=payload) as response:
            if response.status == 200:
                data = await response.json()
                if 'messages' in data and data['messages']:
                    message_id = data['messages'][0].get('id')
                    logger.info(f"Interactive message sent successfully: {message_id}")
                    return {
                        'success': True,
                        'message_id': message_id,
                        'recipient': message.recipient
                    }
                    
            error_text = await response.text()
            logger.error(f"Failed to send interactive message: {error_text}")
            return {'success': False, 'error': error_text}
            
    async def _process_message_queue(self):
        """Background processor for scheduled messages"""
        while True:
            try:
                now = datetime.now(timezone.utc)
                messages_to_send = []
                
                # Find messages ready to send
                for i, message in enumerate(self.message_queue):
                    if message.scheduled_time and message.scheduled_time <= now:
                        messages_to_send.append((i, message))
                        
                # Send messages and remove from queue
                for i, message in reversed(messages_to_send):
                    await self.send_message(message)
                    self.message_queue.pop(i)
                    
                await asyncio.sleep(30)  # Check every 30 seconds
                
            except Exception as e:
                logger.error(f"Message queue processing error: {e}")
                await asyncio.sleep(60)
                
    async def get_message_status(self, message_id: str) -> Optional[WhatsAppMetrics]:
        """
        Get message delivery status
        
        Args:
            message_id: Message identifier
            
        Returns:
            Message status and metrics
        """
        try:
            # Note: WhatsApp API doesn't provide direct message status endpoint
            # Status updates come via webhooks
            
            # Return basic metrics structure
            return WhatsAppMetrics(
                message_id=message_id,
                recipient="unknown",  # Would be stored separately
                status=MessageStatus.SENT  # Default status
            )
            
        except Exception as e:
            logger.error(f"Message status retrieval error: {e}")
            return None
            
    async def get_phone_number_info(self, phone_number: str) -> Optional[WhatsAppContact]:
        """
        Get information about a phone number
        
        Args:
            phone_number: Phone number to query
            
        Returns:
            Contact information if available
        """
        try:
            # Note: WhatsApp API has limited contact info endpoints
            # Most information comes from chat interactions
            
            return WhatsAppContact(
                phone_number=phone_number,
                display_name=None,
                is_business=False
            )
            
        except Exception as e:
            logger.error(f"Phone number info retrieval error: {e}")
            return None
            
    async def create_interactive_buttons(self, header: str, body: str, 
                                       buttons: List[Dict[str, str]]) -> Dict[str, Any]:
        """
        Create interactive button message data
        
        Args:
            header: Message header
            body: Message body text
            buttons: List of button definitions
            
        Returns:
            Interactive message data
        """
        try:
            interactive_data = {
                'type': 'button',
                'header': {
                    'type': 'text',
                    'text': header
                },
                'body': {
                    'text': body
                },
                'action': {
                    'buttons': []
                }
            }
            
            for i, button in enumerate(buttons[:3]):  # Max 3 buttons
                interactive_data['action']['buttons'].append({
                    'type': 'reply',
                    'reply': {
                        'id': button.get('id', f'btn_{i}'),
                        'title': button.get('title', f'Button {i+1}')
                    }
                })
                
            return interactive_data
            
        except Exception as e:
            logger.error(f"Interactive buttons creation error: {e}")
            return {}
            
    async def create_interactive_list(self, header: str, body: str, button_text: str,
                                    sections: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Create interactive list message data
        
        Args:
            header: Message header
            body: Message body text
            button_text: List button text
            sections: List sections with rows
            
        Returns:
            Interactive message data
        """
        try:
            interactive_data = {
                'type': 'list',
                'header': {
                    'type': 'text',
                    'text': header
                },
                'body': {
                    'text': body
                },
                'action': {
                    'button': button_text,
                    'sections': sections
                }
            }
            
            return interactive_data
            
        except Exception as e:
            logger.error(f"Interactive list creation error: {e}")
            return {}
            
    async def bulk_send_messages(self, messages: List[WhatsAppMessage]) -> List[Dict[str, Any]]:
        """
        Send multiple messages with rate limiting
        
        Args:
            messages: List of messages to send
            
        Returns:
            List of send results
        """
        results = []
        
        for i, message in enumerate(messages):
            # Rate limiting for bulk sends
            if i > 0 and i % 20 == 0:  # Every 20 messages
                logger.info("Rate limiting bulk send, waiting 60 seconds...")
                await asyncio.sleep(60)
                
            result = await self.send_message(message)
            results.append(result)
            
            # Small delay between messages
            await asyncio.sleep(1)
            
        logger.info(f"Bulk send completed: {len(results)} messages processed")
        return results
        
    def get_available_templates(self) -> List[Dict[str, Any]]:
        """Get list of available message templates"""
        return [
            {
                'name': name,
                'category': template.get('category'),
                'language': template.get('language'),
                'status': template.get('status'),
                'components': template.get('components', [])
            }
            for name, template in self.templates.items()
        ]
        
    async def upload_media(self, media_path: str, media_type: str) -> Optional[str]:
        """
        Upload media file and get media ID
        
        Args:
            media_path: Path to media file
            media_type: Type of media (image, video, audio, document)
            
        Returns:
            Media ID for use in messages
        """
        try:
            url = f"{self.base_url}/{self.credentials.phone_number_id}/media"
            
            # Read media file
            with open(media_path, 'rb') as media_file:
                media_data = media_file.read()
                
            # Prepare form data
            form_data = aiohttp.FormData()
            form_data.add_field('file', media_data, filename=media_path.split('/')[-1])
            form_data.add_field('type', media_type)
            form_data.add_field('messaging_product', 'whatsapp')
            
            async with self.session.post(url, data=form_data) as response:
                if response.status == 200:
                    data = await response.json()
                    media_id = data.get('id')
                    logger.info(f"Media uploaded successfully: {media_id}")
                    return media_id
                else:
                    error_text = await response.text()
                    logger.error(f"Media upload failed: {error_text}")
                    return None
                    
        except Exception as e:
            logger.error(f"Media upload error: {e}")
            return None


class WhatsAppDistributionManager:
    """
    High-level manager for WhatsApp Business distribution strategies
    Handles customer engagement, broadcast campaigns, and personalized messaging
    """
    
    def __init__(self, connector: WhatsAppConnector):
        self.connector = connector
        self.contacts: List[WhatsAppContact] = []
        self.campaigns: Dict[str, Dict[str, Any]] = {}
        self.performance_history: List[WhatsAppMetrics] = []
        
    async def add_contact(self, phone_number: str, display_name: str = None) -> bool:
        """
        Add a contact to distribution list
        
        Args:
            phone_number: Contact phone number
            display_name: Optional display name
            
        Returns:
            Success status
        """
        try:
            contact = WhatsAppContact(
                phone_number=phone_number,
                display_name=display_name
            )
            
            # Check if contact already exists
            existing = next((c for c in self.contacts if c.phone_number == phone_number), None)
            if not existing:
                self.contacts.append(contact)
                logger.info(f"Added contact: {phone_number}")
                return True
            else:
                # Update existing contact
                existing.display_name = display_name or existing.display_name
                logger.info(f"Updated contact: {phone_number}")
                return True
                
        except Exception as e:
            logger.error(f"Failed to add contact: {e}")
            return False
            
    async def create_broadcast_campaign(self, campaign_name: str, template_name: str,
                                      target_contacts: List[str] = None) -> Dict[str, Any]:
        """
        Create a broadcast campaign using approved templates
        
        Args:
            campaign_name: Campaign identifier
            template_name: WhatsApp template to use
            target_contacts: Specific contacts (if None, uses all)
            
        Returns:
            Campaign creation result
        """
        try:
            if template_name not in self.connector.templates:
                return {'success': False, 'error': 'Template not found or not approved'}
                
            # Get target contacts
            if target_contacts:
                contacts = [c for c in self.contacts if c.phone_number in target_contacts]
            else:
                contacts = self.contacts
                
            if not contacts:
                return {'success': False, 'error': 'No target contacts found'}
                
            # Create campaign
            campaign_id = str(uuid.uuid4())
            campaign = {
                'campaign_id': campaign_id,
                'name': campaign_name,
                'template_name': template_name,
                'target_contacts': [c.phone_number for c in contacts],
                'status': 'created',
                'created_at': datetime.now(timezone.utc),
                'messages_sent': 0,
                'messages_delivered': 0,
                'responses_received': 0
            }
            
            self.campaigns[campaign_id] = campaign
            
            logger.info(f"Created broadcast campaign: {campaign_name} targeting {len(contacts)} contacts")
            return {
                'success': True,
                'campaign_id': campaign_id,
                'target_count': len(contacts)
            }
            
        except Exception as e:
            logger.error(f"Campaign creation error: {e}")
            return {'success': False, 'error': str(e)}
            
    async def execute_campaign(self, campaign_id: str) -> Dict[str, Any]:
        """
        Execute a broadcast campaign
        
        Args:
            campaign_id: Campaign identifier
            
        Returns:
            Execution results
        """
        try:
            if campaign_id not in self.campaigns:
                return {'success': False, 'error': 'Campaign not found'}
                
            campaign = self.campaigns[campaign_id]
            template_name = campaign['template_name']
            target_contacts = campaign['target_contacts']
            
            # Prepare messages
            messages = []
            for contact in target_contacts:
                message = WhatsAppMessage(
                    recipient=contact,
                    message_type=WhatsAppMessageType.TEMPLATE,
                    template_name=template_name,
                    template_language='en'
                )
                messages.append(message)
                
            # Send messages
            campaign['status'] = 'executing'
            results = await self.connector.bulk_send_messages(messages)
            
            # Update campaign metrics
            successful_sends = sum(1 for result in results if result.get('success'))
            campaign['messages_sent'] = successful_sends
            campaign['status'] = 'completed'
            campaign['executed_at'] = datetime.now(timezone.utc)
            
            logger.info(f"Campaign executed: {campaign['name']} - {successful_sends}/{len(messages)} sent")
            
            return {
                'success': True,
                'messages_sent': successful_sends,
                'total_targets': len(messages),
                'send_rate': successful_sends / len(messages) if messages else 0
            }
            
        except Exception as e:
            logger.error(f"Campaign execution error: {e}")
            return {'success': False, 'error': str(e)}
            
    async def send_personalized_message(self, recipient: str, content: Dict[str, Any]) -> Dict[str, Any]:
        """
        Send personalized message to individual contact
        
        Args:
            recipient: Recipient phone number
            content: Message content with personalization
            
        Returns:
            Send result
        """
        try:
            # Get contact info for personalization
            contact = next((c for c in self.contacts if c.phone_number == recipient), None)
            
            message_text = content.get('text', '')
            
            # Apply personalization
            if contact and contact.display_name:
                message_text = message_text.replace('{name}', contact.display_name)
            else:
                message_text = message_text.replace('{name}', 'there')
                
            # Create message
            message = WhatsAppMessage(
                recipient=recipient,
                message_type=WhatsAppMessageType(content.get('type', 'text')),
                text=message_text,
                media_url=content.get('media_url'),
                media_caption=content.get('caption')
            )
            
            # Send message
            result = await self.connector.send_message(message)
            
            if result.get('success'):
                logger.info(f"Personalized message sent to {recipient}")
                
            return result
            
        except Exception as e:
            logger.error(f"Personalized message error: {e}")
            return {'success': False, 'error': str(e)}
            
    def get_campaign_analytics(self) -> Dict[str, Any]:
        """Get analytics across all campaigns"""
        if not self.campaigns:
            return {'message': 'No campaigns found'}
            
        total_campaigns = len(self.campaigns)
        total_messages = sum(c.get('messages_sent', 0) for c in self.campaigns.values())
        total_delivered = sum(c.get('messages_delivered', 0) for c in self.campaigns.values())
        total_responses = sum(c.get('responses_received', 0) for c in self.campaigns.values())
        
        # Calculate rates
        delivery_rate = total_delivered / total_messages if total_messages > 0 else 0
        response_rate = total_responses / total_delivered if total_delivered > 0 else 0
        
        # Recent campaign performance
        recent_campaigns = [
            c for c in self.campaigns.values()
            if c.get('executed_at') and 
            c['executed_at'] > datetime.now(timezone.utc) - timedelta(days=30)
        ]
        
        return {
            'total_campaigns': total_campaigns,
            'recent_campaigns': len(recent_campaigns),
            'total_messages_sent': total_messages,
            'total_delivered': total_delivered,
            'total_responses': total_responses,
            'delivery_rate': round(delivery_rate * 100, 2),
            'response_rate': round(response_rate * 100, 2),
            'average_campaign_size': total_messages / total_campaigns if total_campaigns > 0 else 0,
            'total_contacts': len(self.contacts)
        }


# Export main classes
__all__ = [
    'WhatsAppConnector',
    'WhatsAppDistributionManager',
    'WhatsAppMessage',
    'WhatsAppContact',
    'WhatsAppMetrics',
    'WhatsAppCredentials',
    'WhatsAppMessageType',
    'WhatsAppBusinessType',
    'MessageStatus'
]