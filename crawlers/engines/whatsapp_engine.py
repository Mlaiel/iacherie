"""
WhatsApp Business Monitoring Engine
===================================

Advanced WhatsApp Business API crawler for business account monitoring,
message analytics, and customer engagement tracking.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: All rights reserved. Unauthorized use, reproduction, or distribution prohibited.

  AVERTISSEMENT LÉGAL 
Ce code est la propriété exclusive de Fahed Mlaiel (mlaiel@live.de).
Toute utilisation, reproduction, ou distribution sans autorisation écrite explicite est strictement interdite.
Les contrevenants seront poursuivis selon la loi allemande et internationale.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, AsyncGenerator
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
import re
import hashlib
import json
from urllib.parse import urljoin, urlparse, quote

import aiohttp
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

from ..core.base_engine import BaseCrawlerEngine
from ..core.exceptions import (
    CrawlerError, 
    RateLimitError, 
    AuthenticationError,
    ContentNotFoundError
)
from ..utils.rate_limiter import RateLimiter
from ..utils.cache_manager import CacheManager
from ..models.content_models import MessageContent, BusinessContent
from ...core.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


@dataclass
class WhatsAppMessage:
    """WhatsApp message data structure"""
    id: str
    type: str  # text, image, video, audio, document, location, etc.
    timestamp: datetime
    from_phone: str
    to_phone: str
    status: str  # sent, delivered, read, failed
    text: Optional[str]
    media_url: Optional[str]
    media_type: Optional[str]
    media_caption: Optional[str]
    location: Optional[Dict[str, float]]
    contacts: Optional[List[Dict[str, str]]]
    is_forwarded: bool
    context: Optional[Dict[str, str]]  # Reply/quote context
    interactive: Optional[Dict[str, Any]]  # Buttons, lists, etc.
    errors: Optional[List[Dict[str, str]]]


@dataclass
class WhatsAppContact:
    """WhatsApp contact data structure"""
    phone: str
    name: Optional[str]
    profile: Optional[Dict[str, Any]]
    last_seen: Optional[datetime]
    is_business: bool
    business_info: Optional[Dict[str, Any]]
    labels: List[str]
    tags: List[str]
    conversation_started: datetime
    last_message_time: Optional[datetime]
    message_count: int
    unread_count: int
    is_blocked: bool
    is_archived: bool


@dataclass
class WhatsAppBusinessProfile:
    """WhatsApp Business profile data structure"""
    business_id: str
    display_name: str
    phone_number: str
    about: Optional[str]
    address: Optional[str]
    description: Optional[str]
    email: Optional[str]
    websites: List[str]
    categories: List[str]
    profile_picture_url: Optional[str]
    is_verified: bool
    messaging_product: str
    quality_rating: str
    response_time: Optional[int]
    business_hours: Optional[Dict[str, Any]]
    away_message: Optional[str]
    greeting_message: Optional[str]


@dataclass
class WhatsAppCampaign:
    """WhatsApp marketing campaign data structure"""
    id: str
    name: str
    template_name: str
    template_language: str
    status: str
    created_time: datetime
    start_time: Optional[datetime]
    end_time: Optional[datetime]
    target_audience: Dict[str, Any]
    message_template: Dict[str, Any]
    delivery_stats: Dict[str, int]
    engagement_stats: Dict[str, int]
    cost_stats: Dict[str, float]


class WhatsAppCrawlerEngine(BaseCrawlerEngine):
    """
    Professional WhatsApp Business crawler engine for message monitoring and business analytics.
    
    Features:
    - Business account monitoring
    - Message analytics and tracking
    - Customer engagement analysis
    - Campaign performance monitoring
    - Contact management insights
    - Automated response analysis
    - Quality rating tracking
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize WhatsApp crawler engine"""
        super().__init__(platform="whatsapp", config=config)
        
        # Rate limiting (WhatsApp Business API has strict limits)
        self.rate_limiter = RateLimiter(
            requests_per_minute=80,
            requests_per_hour=1000
        )
        
        # Cache configuration
        self.cache_manager = CacheManager(
            cache_ttl=timedelta(minutes=30),
            max_cache_size=2000
        )
        
        # API configuration
        self.base_url = "https://graph.facebook.com"
        self.api_version = "v18.0"
        self.business_api_url = f"{self.base_url}/{self.api_version}"
        
        # Authentication
        self.access_token = self.config.get("whatsapp_access_token")
        self.phone_number_id = self.config.get("whatsapp_phone_number_id")
        self.business_account_id = self.config.get("whatsapp_business_account_id")
        
        # Session management
        self.session: Optional[aiohttp.ClientSession] = None
        
        logger.info("WhatsApp Business crawler engine initialized")
    
    async def initialize(self) -> None:
        """Initialize the crawler engine"""



        try:
            await self._create_session()
            await self._verify_credentials()
            logger.info("WhatsApp engine initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize WhatsApp engine: {e}")
            raise CrawlerError(f"Initialization failed: {e}")
    
    async def _create_session(self) -> None:
        """Create HTTP session with proper headers"""
        headers = {
            'User-Agent': 'IA-Influencer-Agent/1.0',
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        }
        
        if self.access_token:
            headers['Authorization'] = f'Bearer {self.access_token}'
        
        timeout = aiohttp.ClientTimeout(total=30)
        self.session = aiohttp.ClientSession(
            headers=headers,
            timeout=timeout,
            connector=aiohttp.TCPConnector(limit=50)
        )
    
    async def _verify_credentials(self) -> None:
        """Verify WhatsApp Business API credentials"""
        if not self.access_token:
            raise AuthenticationError("WhatsApp access token required")
        
        if not self.phone_number_id:
            raise AuthenticationError("WhatsApp phone number ID required")
        
        try:
            # Test API access by getting business profile
            await self.get_business_profile()
        except Exception as e:
            raise AuthenticationError(f"Credential verification failed: {e}")
    
    async def get_business_profile(self) -> Optional[WhatsAppBusinessProfile]:
        """
        Get WhatsApp Business profile information
        
        Returns:
            Business profile data
        """



        try:
            await self.rate_limiter.acquire()
            
            # Check cache
            cache_key = f"business_profile:{self.phone_number_id}"
            cached_result = await self.cache_manager.get(cache_key)
            if cached_result:
                return cached_result
            
            url = f"{self.business_api_url}/{self.phone_number_id}"
            params = {
                'fields': 'id,verified_name,display_phone_number,quality_rating,messaging_limit,account_mode'
            }
            
            async with self.session.get(url, params=params) as response:
                if response.status == 429:
                    raise RateLimitError("WhatsApp API rate limit exceeded")
                elif response.status == 401:
                    raise AuthenticationError("Invalid WhatsApp access token")
                elif response.status != 200:
                    raise CrawlerError(f"Profile request failed: {response.status}")
                
                data = await response.json()
                profile = self._parse_business_profile(data)
                
                # Cache result
                await self.cache_manager.set(cache_key, profile)
                
                return profile
                
        except Exception as e:
            logger.error(f"Error getting business profile: {e}")
            raise CrawlerError(f"Business profile retrieval failed: {e}")
    
    async def get_messages(
        self,
        limit: int = 100,
        after: Optional[str] = None,
        before: Optional[str] = None
    ) -> List[WhatsAppMessage]:
        """
        Get messages for the business account
        
        Args:
            limit: Maximum number of messages to return
            after: Pagination cursor for messages after this point
            before: Pagination cursor for messages before this point
            
        Returns:
            List of messages
        """



        try:
            await self.rate_limiter.acquire()
            
            # Check cache
            cache_key = f"messages:{limit}:{after}:{before}"
            cached_result = await self.cache_manager.get(cache_key)
            if cached_result:
                return cached_result
            
            url = f"{self.business_api_url}/{self.phone_number_id}/messages"
            params = {
                'limit': min(limit, 100),
                'fields': 'id,type,timestamp,from,to,status,text,image,video,audio,document,location,contacts,context,interactive,errors'
            }
            
            if after:
                params['after'] = after
            if before:
                params['before'] = before
            
            async with self.session.get(url, params=params) as response:
                if response.status == 429:
                    raise RateLimitError("WhatsApp API rate limit exceeded")
                elif response.status != 200:
                    raise CrawlerError(f"Messages request failed: {response.status}")
                
                data = await response.json()
                messages = []
                
                for message_data in data.get('data', []):
                    message = self._parse_message_data(message_data)
                    messages.append(message)
                
                # Cache results
                await self.cache_manager.set(cache_key, messages)
                
                logger.info(f"Retrieved {len(messages)} messages")
                return messages
                
        except Exception as e:
            logger.error(f"Error getting messages: {e}")
            raise CrawlerError(f"Messages retrieval failed: {e}")
    
    async def send_message(
        self,
        to_phone: str,
        message_type: str,
        content: Dict[str, Any]
    ) -> Optional[str]:
        """
        Send a message through WhatsApp Business API
        
        Args:
            to_phone: Recipient phone number
            message_type: Type of message (text, template, etc.)
            content: Message content
            
        Returns:
            Message ID if successful
        """



        try:
            await self.rate_limiter.acquire()
            
            url = f"{self.business_api_url}/{self.phone_number_id}/messages"
            
            payload = {
                'messaging_product': 'whatsapp',
                'to': to_phone,
                'type': message_type
            }
            
            # Add content based on message type
            if message_type == 'text':
                payload['text'] = {'body': content.get('body', '')}
            elif message_type == 'template':
                payload['template'] = content
            elif message_type == 'interactive':
                payload['interactive'] = content
            
            async with self.session.post(url, json=payload) as response:
                if response.status == 429:
                    raise RateLimitError("WhatsApp API rate limit exceeded")
                elif response.status not in [200, 201]:
                    raise CrawlerError(f"Message send failed: {response.status}")
                
                data = await response.json()
                message_id = data.get('messages', [{}])[0].get('id')
                
                logger.info(f"Message sent successfully: {message_id}")
                return message_id
                
        except Exception as e:
            logger.error(f"Error sending message: {e}")
            raise CrawlerError(f"Message send failed: {e}")
    
    async def analyze_conversation_patterns(
        self,
        days_back: int = 30
    ) -> Dict[str, Any]:
        """
        Analyze conversation patterns and customer engagement
        
        Args:
            days_back: Number of days to analyze
            
        Returns:
            Conversation analytics data
        """



        try:
            # Get messages from the specified period
            messages = await self.get_messages(limit=1000)
            
            # Filter messages by date
            cutoff_date = datetime.utcnow() - timedelta(days=days_back)
            recent_messages = [
                msg for msg in messages 
                if msg.timestamp >= cutoff_date
            ]
            
            # Analyze patterns
            analytics = {
                'period_days': days_back,
                'total_messages': len(recent_messages),
                'incoming_messages': len([msg for msg in recent_messages if msg.to_phone == self.phone_number_id]),
                'outgoing_messages': len([msg for msg in recent_messages if msg.from_phone == self.phone_number_id]),
                'unique_contacts': len(set(
                    msg.from_phone if msg.to_phone == self.phone_number_id else msg.to_phone
                    for msg in recent_messages
                )),
                'message_types': self._analyze_message_types(recent_messages),
                'hourly_distribution': self._analyze_hourly_distribution(recent_messages),
                'response_times': self._analyze_response_times(recent_messages),
                'engagement_metrics': self._calculate_engagement_metrics(recent_messages),
                'analysis_date': datetime.utcnow().isoformat()
            }
            
            logger.info(f"Conversation analysis completed for {days_back} days")
            return analytics
            
        except Exception as e:
            logger.error(f"Error analyzing conversations: {e}")
            raise CrawlerError(f"Conversation analysis failed: {e}")
    
    def _parse_business_profile(self, data: Dict[str, Any]) -> WhatsAppBusinessProfile:
        """Parse business profile data from API response"""



        try:
            return WhatsAppBusinessProfile(
                business_id=str(data.get('id', '')),
                display_name=data.get('verified_name', ''),
                phone_number=data.get('display_phone_number', ''),
                about=data.get('about'),
                address=data.get('address'),
                description=data.get('description'),
                email=data.get('email'),
                websites=data.get('websites', []),
                categories=data.get('categories', []),
                profile_picture_url=data.get('profile_picture_url'),
                is_verified=data.get('is_verified', False),
                messaging_product=data.get('messaging_product', 'whatsapp'),
                quality_rating=data.get('quality_rating', 'UNKNOWN'),
                response_time=data.get('response_time'),
                business_hours=data.get('business_hours'),
                away_message=data.get('away_message'),
                greeting_message=data.get('greeting_message')
            )
        except Exception as e:
            logger.error(f"Error parsing business profile: {e}")
            raise CrawlerError(f"Business profile parsing failed: {e}")
    
    def _parse_message_data(self, message_data: Dict[str, Any]) -> WhatsAppMessage:
        """Parse message data from API response"""



        try:
            return WhatsAppMessage(
                id=str(message_data.get('id', '')),
                type=message_data.get('type', 'unknown'),
                timestamp=datetime.fromtimestamp(int(message_data.get('timestamp', 0))),
                from_phone=message_data.get('from', ''),
                to_phone=message_data.get('to', ''),
                status=message_data.get('status', 'unknown'),
                text=message_data.get('text', {}).get('body') if message_data.get('text') else None,
                media_url=self._extract_media_url(message_data),
                media_type=self._extract_media_type(message_data),
                media_caption=self._extract_media_caption(message_data),
                location=message_data.get('location'),
                contacts=message_data.get('contacts', []),
                is_forwarded=message_data.get('context', {}).get('forwarded', False),
                context=message_data.get('context'),
                interactive=message_data.get('interactive'),
                errors=message_data.get('errors', [])
            )
        except Exception as e:
            logger.error(f"Error parsing message data: {e}")
            raise CrawlerError(f"Message data parsing failed: {e}")
    
    def _extract_media_url(self, message_data: Dict[str, Any]) -> Optional[str]:
        """Extract media URL from message data"""
        for media_type in ['image', 'video', 'audio', 'document']:
            if media_type in message_data:
                return message_data[media_type].get('url')
        return None
    
    def _extract_media_type(self, message_data: Dict[str, Any]) -> Optional[str]:
        """Extract media type from message data"""
        for media_type in ['image', 'video', 'audio', 'document']:
            if media_type in message_data:
                return media_type
        return None
    
    def _extract_media_caption(self, message_data: Dict[str, Any]) -> Optional[str]:
        """Extract media caption from message data"""
        for media_type in ['image', 'video', 'audio', 'document']:
            if media_type in message_data:
                return message_data[media_type].get('caption')
        return None
    
    def _analyze_message_types(self, messages: List[WhatsAppMessage]) -> Dict[str, int]:
        """Analyze distribution of message types"""
        type_counts = {}
        for message in messages:
            type_counts[message.type] = type_counts.get(message.type, 0) + 1
        return type_counts
    
    def _analyze_hourly_distribution(self, messages: List[WhatsAppMessage]) -> Dict[int, int]:
        """Analyze hourly distribution of messages"""
        hourly_counts = {hour: 0 for hour in range(24)}
        for message in messages:
            hour = message.timestamp.hour
            hourly_counts[hour] += 1
        return hourly_counts
    
    def _analyze_response_times(self, messages: List[WhatsAppMessage]) -> Dict[str, float]:
        """Analyze response times for business messages"""
        response_times = []
        
        # Group messages by conversation
        conversations = {}
        for message in messages:
            contact = message.from_phone if message.to_phone == self.phone_number_id else message.to_phone
            if contact not in conversations:
                conversations[contact] = []
            conversations[contact].append(message)
        
        # Calculate response times
        for contact, msgs in conversations.items():
            msgs.sort(key=lambda x: x.timestamp)
            for i in range(len(msgs) - 1):
                current_msg = msgs[i]
                next_msg = msgs[i + 1]
                
                # Check if this is a customer message followed by business response
                if (current_msg.to_phone == self.phone_number_id and
                    next_msg.from_phone == self.phone_number_id):
                    response_time = (next_msg.timestamp - current_msg.timestamp).total_seconds() / 60
                    response_times.append(response_time)
        
        if response_times:
            return {
                'average_minutes': sum(response_times) / len(response_times),
                'median_minutes': sorted(response_times)[len(response_times) // 2],
                'max_minutes': max(response_times),
                'min_minutes': min(response_times),
                'total_responses': len(response_times)
            }
        
        return {'average_minutes': 0, 'median_minutes': 0, 'max_minutes': 0, 'min_minutes': 0, 'total_responses': 0}
    
    def _calculate_engagement_metrics(self, messages: List[WhatsAppMessage]) -> Dict[str, float]:
        """Calculate engagement metrics"""
        total_messages = len(messages)
        if total_messages == 0:
            return {'engagement_rate': 0.0, 'media_rate': 0.0, 'interactive_rate': 0.0}
        
        media_messages = len([msg for msg in messages if msg.media_url])
        interactive_messages = len([msg for msg in messages if msg.interactive])
        
        return {
            'engagement_rate': (total_messages / max(1, total_messages)) * 100,
            'media_rate': (media_messages / total_messages) * 100,
            'interactive_rate': (interactive_messages / total_messages) * 100
        }
    
    async def cleanup(self) -> None:
        """Clean up resources"""



        try:
            if self.session:
                await self.session.close()
            await super().cleanup()
            logger.info("WhatsApp engine cleanup completed")
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")
    
    def __str__(self) -> str:
        return f"WhatsAppCrawlerEngine(platform=whatsapp)"
