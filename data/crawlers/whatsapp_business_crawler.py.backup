"""WhatsApp Business API Crawler Implementation
===========================================

Enterprise-grade WhatsApp Business API content monitoring and analysis crawler.
Implements comprehensive message tracking for business communications.

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
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Set
from dataclasses import dataclass, asdict
import aiohttp
import time
import random
from urllib.parse import urljoin, urlparse, parse_qs
import re
import hashlib
import base64

from .platform_crawler import PlatformCrawler, CrawlerConfig, CrawlerResult


@dataclass
class WhatsAppMessage:
    """WhatsApp Business message information"""
    message_id: str
    wa_id: str  # WhatsApp ID of sender
    phone_number: str
    profile_name: Optional[str]
    text: Optional[str]
    message_type: str  # text, image, audio, video, document, location, contacts, interactive
    timestamp: datetime
    status: str  # sent, delivered, read, failed
    context: Optional[Dict[str, Any]]  # Reply context
    interactive: Optional[Dict[str, Any]]  # Interactive message data
    location: Optional[Dict[str, Any]]
    contacts: Optional[List[Dict[str, Any]]]
    media: Optional[Dict[str, Any]]
    media_id: Optional[str]
    media_url: Optional[str]
    media_mime_type: Optional[str]
    media_sha256: Optional[str]
    media_file_size: Optional[int]
    caption: Optional[str]
    filename: Optional[str]
    audio_recognition: Optional[str]  # Voice message transcription
    button_reply: Optional[Dict[str, Any]]
    list_reply: Optional[Dict[str, Any]]
    webhook_id: str
    business_phone_number_id: str
    metadata: Dict[str, Any]
    conversation_id: Optional[str]
    direction: str  # inbound, outbound
    billing_category: Optional[str]
    error_info: Optional[Dict[str, Any]]


@dataclass
class WhatsAppContact:
    """WhatsApp Business contact information"""
    wa_id: str
    phone_number: str
    profile_name: Optional[str]
    profile_picture_url: Optional[str]
    status: str  # valid, invalid, processing, failed
    first_seen: datetime
    last_seen: datetime
    message_count: int
    conversation_count: int
    labels: List[str]
    custom_fields: Dict[str, Any]
    opt_in_status: bool
    language: Optional[str]
    timezone: Optional[str]
    business_relationship: str  # customer, prospect, blocked
    tags: List[str]
    notes: Optional[str]
    last_message: Optional[WhatsAppMessage]
    conversation_history: List[WhatsAppMessage]


@dataclass
class WhatsAppBusinessAccount:
    """WhatsApp Business account information"""
    business_account_id: str
    business_phone_number_id: str
    display_phone_number: str
    verified_name: str
    code_verification_status: str
    quality_rating: str  # GREEN, YELLOW, RED, UNKNOWN
    messaging_limit: str  # TIER_NOT_SET, TIER_250, TIER_1K, TIER_10K, TIER_100K, TIER_UNLIMITED
    webhook_configuration: Optional[Dict[str, Any]]
    business_profile: Dict[str, Any]
    certificate: Optional[str]
    name_status: str
    new_name_status: str
    status: List[str]
    search_visibility: bool
    is_official_business_account: bool
    throughput: Dict[str, Any]
    analytics: Dict[str, Any]
    template_analytics: Dict[str, Any]


class WhatsAppBusinessCrawler(PlatformCrawler):
    """
    Advanced WhatsApp Business API crawler for messaging content monitoring.
    
    Features:
    - Message content analysis
    - Media file tracking
    - Contact management
    - Conversation analytics
    - Template message monitoring
    - Webhook event processing
    - Business metrics tracking
    - Compliance and audit trails
    - Multi-language support
    - Real-time notifications
    """
    
    def __init__(self, config: CrawlerConfig, vector_matcher=None, 
                 access_token: str = None, business_account_id: str = None,
                 phone_number_id: str = None, webhook_verify_token: str = None):
        super().__init__(config, vector_matcher)
        self.platform_name = "whatsapp_business"
        self.base_url = "https://graph.facebook.com/v18.0"
        
        # WhatsApp Business API credentials
        self.access_token = access_token
        self.business_account_id = business_account_id
        self.phone_number_id = phone_number_id
        self.webhook_verify_token = webhook_verify_token
        
        # Rate limiting (WhatsApp Business has strict limits)
        self.requests_per_minute = 80  # Conservative limit
        self.min_delay = 0.75
        self.max_delay = 1.5
        
        # Content type mappings
        self.content_types = {
            'messages': self._crawl_messages,
            'contacts': self._crawl_contacts,
            'templates': self._crawl_templates,
            'media': self._crawl_media,
            'conversations': self._crawl_conversations,
            'analytics': self._crawl_analytics,
            'webhooks': self._crawl_webhooks
        }
        
        # Tracking
        self.request_count = 0
        self.last_request_time = 0
        self.processed_message_ids = set()
        
        # Initialize session headers
        self._setup_session_headers()
    
    def _setup_session_headers(self):
        """Setup WhatsApp Business API specific headers"""
        self.session_headers.update({
            'Accept': 'application/json',
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.access_token}' if self.access_token else '',
            'User-Agent': 'WhatsApp-Business-Crawler/1.0'
        })
    
    async def search_content(self, query: str, content_type: str = "messages", 
                           max_results: int = 50, **kwargs) -> List[CrawlerResult]:
        """
        Search for content via WhatsApp Business API.
        
        Args:
            query: Search query (phone number, contact name, etc.)
            content_type: Type of content to search for
            max_results: Maximum number of results
            **kwargs: Additional parameters
            
        Returns:
            List of crawler results
        """
        try:
            await self._check_rate_limit()
            
            if content_type not in self.content_types:
                raise ValueError(f"Unsupported content type: {content_type}")
            
            if not self.access_token:
                self.logger.error("WhatsApp Business API access token not configured")
                return []
            
            # Execute search based on content type
            crawler_func = self.content_types[content_type]
            results = await crawler_func(query, max_results, **kwargs)
            
            self.logger.info(f"Found {len(results)} WhatsApp Business {content_type} for query: {query}")
            return results
            
        except Exception as e:
            self.logger.error(f"Error searching WhatsApp Business content: {str(e)}")
            return []
    
    async def _crawl_messages(self, query: str, max_results: int, **kwargs) -> List[CrawlerResult]:
        """Crawl WhatsApp Business messages"""
        try:
            results = []
            
            if not self.phone_number_id:
                self.logger.error("Phone number ID not configured")
                return []
            
            # Search for messages
            url = f"{self.base_url}/{self.phone_number_id}/messages"
            
            # Prepare query parameters
            params = {
                'limit': min(max_results, 100),
                'fields': 'id,from,to,type,timestamp,text,image,audio,video,document,location,contacts,interactive,context,status,pricing,errors'
            }
            
            # Add date range if provided
            if 'since' in kwargs:
                params['since'] = kwargs['since']
            if 'until' in kwargs:
                params['until'] = kwargs['until']
            
            # Execute API request
            async with aiohttp.ClientSession(headers=self.session_headers) as session:
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        if 'data' in data:
                            for message_data in data['data']:
                                # Filter by query if provided
                                if query:
                                    message_text = message_data.get('text', {}).get('body', '')
                                    profile_name = message_data.get('contacts', [{}])[0].get('profile', {}).get('name', '')
                                    from_number = message_data.get('from', '')
                                    
                                    if (query.lower() not in message_text.lower() and 
                                        query.lower() not in profile_name.lower() and 
                                        query not in from_number):
                                        continue
                                
                                # Parse message data
                                whatsapp_message = await self._parse_message_data(message_data)
                                if whatsapp_message:
                                    result = CrawlerResult(
                                        url=f"whatsapp://message/{whatsapp_message.message_id}",
                                        title=f"WhatsApp Message from {whatsapp_message.profile_name or whatsapp_message.phone_number}",
                                        content=whatsapp_message.text or f"[{whatsapp_message.message_type.upper()}]",
                                        metadata={
                                            'message_data': asdict(whatsapp_message),
                                            'platform': 'whatsapp_business',
                                            'content_type': 'message',
                                            'phone_number': whatsapp_message.phone_number,
                                            'message_type': whatsapp_message.message_type,
                                            'status': whatsapp_message.status,
                                            'direction': whatsapp_message.direction,
                                            'has_media': bool(whatsapp_message.media),
                                            'conversation_id': whatsapp_message.conversation_id
                                        },
                                        timestamp=whatsapp_message.timestamp,
                                        similarity_score=0.0
                                    )
                                    results.append(result)
                        
                        # Handle pagination
                        while 'paging' in data and 'next' in data['paging'] and len(results) < max_results:
                            await asyncio.sleep(random.uniform(self.min_delay, self.max_delay))
                            
                            async with session.get(data['paging']['next']) as next_response:
                                if next_response.status == 200:
                                    data = await next_response.json()
                                    
                                    if 'data' in data:
                                        for message_data in data['data']:
                                            if len(results) >= max_results:
                                                break
                                            
                                            # Filter and parse
                                            if query:
                                                message_text = message_data.get('text', {}).get('body', '')
                                                profile_name = message_data.get('contacts', [{}])[0].get('profile', {}).get('name', '')
                                                from_number = message_data.get('from', '')
                                                
                                                if (query.lower() not in message_text.lower() and 
                                                    query.lower() not in profile_name.lower() and 
                                                    query not in from_number):
                                                    continue
                                            
                                            whatsapp_message = await self._parse_message_data(message_data)
                                            if whatsapp_message:
                                                result = CrawlerResult(
                                                    url=f"whatsapp://message/{whatsapp_message.message_id}",
                                                    title=f"WhatsApp Message from {whatsapp_message.profile_name or whatsapp_message.phone_number}",
                                                    content=whatsapp_message.text or f"[{whatsapp_message.message_type.upper()}]",
                                                    metadata={
                                                        'message_data': asdict(whatsapp_message),
                                                        'platform': 'whatsapp_business',
                                                        'content_type': 'message',
                                                        'phone_number': whatsapp_message.phone_number,
                                                        'message_type': whatsapp_message.message_type,
                                                        'status': whatsapp_message.status,
                                                        'direction': whatsapp_message.direction,
                                                        'has_media': bool(whatsapp_message.media),
                                                        'conversation_id': whatsapp_message.conversation_id
                                                    },
                                                    timestamp=whatsapp_message.timestamp,
                                                    similarity_score=0.0
                                                )
                                                results.append(result)
                                else:
                                    break
                    else:
                        self.logger.error(f"API request failed with status {response.status}")
            
            return results[:max_results]
            
        except Exception as e:
            self.logger.error(f"Error crawling WhatsApp Business messages: {str(e)}")
            return []
    
    async def _crawl_contacts(self, query: str, max_results: int, **kwargs) -> List[CrawlerResult]:
        """Crawl WhatsApp Business contacts"""
        try:
            results = []
            
            if not self.business_account_id:
                self.logger.error("Business account ID not configured")
                return []
            
            # Search for contacts via phone number lookup
            # Note: WhatsApp Business API doesn't have a direct contact search,
            # so we implement this through message history analysis
            
            # Get message history and extract unique contacts
            messages_results = await self._crawl_messages(query, max_results * 2, **kwargs)
            
            contact_map = {}
            for message_result in messages_results:
                message_data = message_result.metadata.get('message_data', {})
                phone_number = message_data.get('phone_number')
                profile_name = message_data.get('profile_name')
                
                if phone_number:
                    if phone_number not in contact_map:
                        contact_map[phone_number] = {
                            'phone_number': phone_number,
                            'profile_name': profile_name,
                            'first_seen': message_result.timestamp,
                            'last_seen': message_result.timestamp,
                            'message_count': 1,
                            'messages': [message_data]
                        }
                    else:
                        contact_info = contact_map[phone_number]
                        contact_info['message_count'] += 1
                        contact_info['messages'].append(message_data)
                        if message_result.timestamp > contact_info['last_seen']:
                            contact_info['last_seen'] = message_result.timestamp
                        if message_result.timestamp < contact_info['first_seen']:
                            contact_info['first_seen'] = message_result.timestamp
                        if not contact_info['profile_name'] and profile_name:
                            contact_info['profile_name'] = profile_name
            
            # Convert to results
            for phone_number, contact_info in list(contact_map.items())[:max_results]:
                # Filter by query
                if query:
                    if (query.lower() not in (contact_info['profile_name'] or '').lower() and 
                        query not in phone_number):
                        continue
                
                result = CrawlerResult(
                    url=f"whatsapp://contact/{phone_number}",
                    title=f"WhatsApp Contact: {contact_info['profile_name'] or phone_number}",
                    content=f"Contact: {contact_info['profile_name'] or 'Unknown'} ({phone_number}) - {contact_info['message_count']} messages",
                    metadata={
                        'contact_data': contact_info,
                        'platform': 'whatsapp_business',
                        'content_type': 'contact',
                        'phone_number': phone_number,
                        'profile_name': contact_info['profile_name'],
                        'message_count': contact_info['message_count'],
                        'conversation_span': (contact_info['last_seen'] - contact_info['first_seen']).days
                    },
                    timestamp=contact_info['last_seen'],
                    similarity_score=0.0
                )
                results.append(result)
            
            return results
            
        except Exception as e:
            self.logger.error(f"Error crawling WhatsApp Business contacts: {str(e)}")
            return []
    
    async def _crawl_templates(self, query: str, max_results: int, **kwargs) -> List[CrawlerResult]:
        """Crawl WhatsApp Business message templates"""
        try:
            results = []
            
            if not self.business_account_id:
                self.logger.error("Business account ID not configured")
                return []
            
            # Get message templates
            url = f"{self.base_url}/{self.business_account_id}/message_templates"
            
            params = {
                'limit': min(max_results, 100),
                'fields': 'id,name,category,language,status,components,quality_score,rejected_reason,created_time'
            }
            
            if query:
                params['name'] = query
            
            async with aiohttp.ClientSession(headers=self.session_headers) as session:
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        if 'data' in data:
                            for template_data in data['data']:
                                # Filter by query if not already filtered by API
                                if query and 'name' not in params:
                                    template_name = template_data.get('name', '')
                                    if query.lower() not in template_name.lower():
                                        continue
                                
                                # Extract template content
                                components = template_data.get('components', [])
                                template_content = ""
                                for component in components:
                                    if component.get('type') == 'BODY':
                                        template_content = component.get('text', '')
                                        break
                                
                                result = CrawlerResult(
                                    url=f"whatsapp://template/{template_data.get('id')}",
                                    title=f"WhatsApp Template: {template_data.get('name')}",
                                    content=template_content,
                                    metadata={
                                        'template_data': template_data,
                                        'platform': 'whatsapp_business',
                                        'content_type': 'template',
                                        'template_name': template_data.get('name'),
                                        'category': template_data.get('category'),
                                        'language': template_data.get('language'),
                                        'status': template_data.get('status'),
                                        'quality_score': template_data.get('quality_score'),
                                        'component_count': len(components)
                                    },
                                    timestamp=datetime.fromisoformat(template_data.get('created_time', '').replace('Z', '+00:00')) if template_data.get('created_time') else datetime.utcnow(),
                                    similarity_score=0.0
                                )
                                results.append(result)
                        
                        # Handle pagination
                        while 'paging' in data and 'next' in data['paging'] and len(results) < max_results:
                            await asyncio.sleep(random.uniform(self.min_delay, self.max_delay))
                            
                            async with session.get(data['paging']['next']) as next_response:
                                if next_response.status == 200:
                                    data = await next_response.json()
                                    
                                    if 'data' in data:
                                        for template_data in data['data']:
                                            if len(results) >= max_results:
                                                break
                                            
                                            # Filter and parse
                                            if query and 'name' not in params:
                                                template_name = template_data.get('name', '')
                                                if query.lower() not in template_name.lower():
                                                    continue
                                            
                                            components = template_data.get('components', [])
                                            template_content = ""
                                            for component in components:
                                                if component.get('type') == 'BODY':
                                                    template_content = component.get('text', '')
                                                    break
                                            
                                            result = CrawlerResult(
                                                url=f"whatsapp://template/{template_data.get('id')}",
                                                title=f"WhatsApp Template: {template_data.get('name')}",
                                                content=template_content,
                                                metadata={
                                                    'template_data': template_data,
                                                    'platform': 'whatsapp_business',
                                                    'content_type': 'template',
                                                    'template_name': template_data.get('name'),
                                                    'category': template_data.get('category'),
                                                    'language': template_data.get('language'),
                                                    'status': template_data.get('status'),
                                                    'quality_score': template_data.get('quality_score'),
                                                    'component_count': len(components)
                                                },
                                                timestamp=datetime.fromisoformat(template_data.get('created_time', '').replace('Z', '+00:00')) if template_data.get('created_time') else datetime.utcnow(),
                                                similarity_score=0.0
                                            )
                                            results.append(result)
                                else:
                                    break
                    else:
                        self.logger.error(f"API request failed with status {response.status}")
            
            return results[:max_results]
            
        except Exception as e:
            self.logger.error(f"Error crawling WhatsApp Business templates: {str(e)}")
            return []
    
    async def _crawl_media(self, query: str, max_results: int, **kwargs) -> List[CrawlerResult]:
        """Crawl WhatsApp Business media messages"""
        try:
            results = []
            
            # Get all messages and filter for media
            all_messages = await self._crawl_messages("", max_results * 2, **kwargs)
            
            for message_result in all_messages:
                message_data = message_result.metadata.get('message_data', {})
                media_type = message_data.get('message_type')
                
                # Filter for media messages
                if media_type not in ['image', 'audio', 'video', 'document']:
                    continue
                
                # Filter by query
                if query:
                    caption = message_data.get('caption', '')
                    filename = message_data.get('filename', '')
                    if (query.lower() not in caption.lower() and 
                        query.lower() not in filename.lower()):
                        continue
                
                # Update result for media focus
                message_result.title = f"[{media_type.upper()}] {message_result.title}"
                message_result.metadata['content_type'] = 'media'
                message_result.metadata['media_type'] = media_type
                message_result.metadata['media_id'] = message_data.get('media_id')
                message_result.metadata['media_url'] = message_data.get('media_url')
                message_result.metadata['file_size'] = message_data.get('media_file_size')
                message_result.metadata['mime_type'] = message_data.get('media_mime_type')
                
                results.append(message_result)
                
                if len(results) >= max_results:
                    break
            
            return results
            
        except Exception as e:
            self.logger.error(f"Error crawling WhatsApp Business media: {str(e)}")
            return []
    
    async def _crawl_conversations(self, query: str, max_results: int, **kwargs) -> List[CrawlerResult]:
        """Crawl WhatsApp Business conversations (grouped by contact)"""
        try:
            results = []
            
            # Get contacts first
            contacts_results = await self._crawl_contacts(query, max_results, **kwargs)
            
            for contact_result in contacts_results:
                contact_data = contact_result.metadata.get('contact_data', {})
                phone_number = contact_data.get('phone_number')
                messages = contact_data.get('messages', [])
                
                if messages:
                    # Create conversation summary
                    conversation_content = f"Conversation with {contact_data.get('profile_name', phone_number)}\n"
                    conversation_content += f"Messages: {len(messages)}\n"
                    conversation_content += f"Duration: {(contact_data['last_seen'] - contact_data['first_seen']).days} days\n\n"
                    
                    # Add recent messages
                    for msg in messages[-5:]:  # Last 5 messages
                        msg_text = msg.get('text', f"[{msg.get('message_type', 'unknown').upper()}]")
                        conversation_content += f"- {msg_text[:100]}...\n"
                    
                    result = CrawlerResult(
                        url=f"whatsapp://conversation/{phone_number}",
                        title=f"WhatsApp Conversation: {contact_data.get('profile_name', phone_number)}",
                        content=conversation_content,
                        metadata={
                            'conversation_data': contact_data,
                            'platform': 'whatsapp_business',
                            'content_type': 'conversation',
                            'phone_number': phone_number,
                            'message_count': len(messages),
                            'conversation_span_days': (contact_data['last_seen'] - contact_data['first_seen']).days,
                            'last_activity': contact_data['last_seen'].isoformat()
                        },
                        timestamp=contact_data['last_seen'],
                        similarity_score=0.0
                    )
                    results.append(result)
            
            return results[:max_results]
            
        except Exception as e:
            self.logger.error(f"Error crawling WhatsApp Business conversations: {str(e)}")
            return []
    
    async def _crawl_analytics(self, query: str, max_results: int, **kwargs) -> List[CrawlerResult]:
        """Crawl WhatsApp Business analytics data"""
        try:
            results = []
            
            if not self.business_account_id:
                self.logger.error("Business account ID not configured")
                return []
            
            # Get analytics data
            url = f"{self.base_url}/{self.business_account_id}/conversation_analytics"
            
            # Prepare date range
            end_date = kwargs.get('end_date', datetime.utcnow())
            start_date = kwargs.get('start_date', end_date - timedelta(days=30))
            
            params = {
                'start': int(start_date.timestamp()),
                'end': int(end_date.timestamp()),
                'granularity': kwargs.get('granularity', 'DAILY'),
                'metric_types': 'COST,CONVERSATION'
            }
            
            async with aiohttp.ClientSession(headers=self.session_headers) as session:
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        if 'data' in data:
                            for analytics_data in data['data']:
                                # Filter by query if provided
                                if query and query.lower() not in str(analytics_data).lower():
                                    continue
                                
                                data_points = analytics_data.get('data_points', [])
                                total_conversations = sum(dp.get('conversation', 0) for dp in data_points)
                                total_cost = sum(dp.get('cost', 0) for dp in data_points)
                                
                                result = CrawlerResult(
                                    url=f"whatsapp://analytics/{self.business_account_id}",
                                    title=f"WhatsApp Business Analytics: {analytics_data.get('granularity', 'Unknown')}",
                                    content=f"Analytics Data\nConversations: {total_conversations}\nCost: ${total_cost:.2f}\nPeriod: {start_date.date()} to {end_date.date()}",
                                    metadata={
                                        'analytics_data': analytics_data,
                                        'platform': 'whatsapp_business',
                                        'content_type': 'analytics',
                                        'total_conversations': total_conversations,
                                        'total_cost': total_cost,
                                        'data_points_count': len(data_points),
                                        'period_start': start_date.isoformat(),
                                        'period_end': end_date.isoformat()
                                    },
                                    timestamp=datetime.utcnow(),
                                    similarity_score=0.0
                                )
                                results.append(result)
                                
                                if len(results) >= max_results:
                                    break
                    else:
                        self.logger.error(f"Analytics API request failed with status {response.status}")
            
            return results
            
        except Exception as e:
            self.logger.error(f"Error crawling WhatsApp Business analytics: {str(e)}")
            return []
    
    async def _crawl_webhooks(self, query: str, max_results: int, **kwargs) -> List[CrawlerResult]:
        """Crawl WhatsApp Business webhook events (simulation)"""
        try:
            results = []
            
            # Note: This is a simulation as webhook events are received in real-time
            # In a real implementation, this would query a webhook event storage system
            
            # Simulate recent webhook events based on recent messages
            messages_results = await self._crawl_messages("", max_results, **kwargs)
            
            for message_result in messages_results:
                message_data = message_result.metadata.get('message_data', {})
                
                # Filter by query
                if query and query.lower() not in str(message_data).lower():
                    continue
                
                # Create webhook event simulation
                webhook_event = {
                    'object': 'whatsapp_business_account',
                    'entry': [{
                        'id': self.business_account_id,
                        'changes': [{
                            'value': {
                                'messaging_product': 'whatsapp',
                                'metadata': {
                                    'display_phone_number': message_data.get('business_phone_number_id'),
                                    'phone_number_id': self.phone_number_id
                                },
                                'messages': [message_data] if message_data.get('direction') == 'inbound' else [],
                                'statuses': [message_data] if message_data.get('direction') == 'outbound' else []
                            },
                            'field': 'messages'
                        }]
                    }]
                }
                
                result = CrawlerResult(
                    url=f"whatsapp://webhook/{message_data.get('message_id')}",
                    title=f"WhatsApp Webhook Event: {message_data.get('message_type', 'unknown').upper()}",
                    content=f"Webhook Event\nType: {message_data.get('message_type')}\nFrom: {message_data.get('phone_number')}\nTimestamp: {message_data.get('timestamp')}",
                    metadata={
                        'webhook_data': webhook_event,
                        'platform': 'whatsapp_business',
                        'content_type': 'webhook',
                        'event_type': 'messages' if message_data.get('direction') == 'inbound' else 'statuses',
                        'phone_number': message_data.get('phone_number'),
                        'message_type': message_data.get('message_type'),
                        'webhook_id': message_data.get('webhook_id')
                    },
                    timestamp=message_result.timestamp,
                    similarity_score=0.0
                )
                results.append(result)
            
            return results[:max_results]
            
        except Exception as e:
            self.logger.error(f"Error crawling WhatsApp Business webhooks: {str(e)}")
            return []
    
    # Helper methods
    
    async def _parse_message_data(self, message_data: Dict[str, Any]) -> Optional[WhatsAppMessage]:
        """Parse message data from WhatsApp Business API"""
        try:
            # Extract basic message info
            message_id = message_data.get('id', '')
            wa_id = message_data.get('from', '')
            timestamp_str = message_data.get('timestamp', '')
            
            # Parse timestamp
            if timestamp_str:
                timestamp = datetime.fromtimestamp(int(timestamp_str))
            else:
                timestamp = datetime.utcnow()
            
            # Determine message type and extract content
            message_type = message_data.get('type', 'unknown')
            text_content = None
            media_info = None
            interactive_info = None
            location_info = None
            contacts_info = None
            
            if message_type == 'text':
                text_content = message_data.get('text', {}).get('body', '')
            
            elif message_type in ['image', 'audio', 'video', 'document']:
                media_data = message_data.get(message_type, {})
                media_info = {
                    'id': media_data.get('id'),
                    'mime_type': media_data.get('mime_type'),
                    'sha256': media_data.get('sha256'),
                    'file_size': media_data.get('file_size'),
                    'caption': media_data.get('caption'),
                    'filename': media_data.get('filename')
                }
                text_content = media_data.get('caption', '')
            
            elif message_type == 'interactive':
                interactive_data = message_data.get('interactive', {})
                interactive_info = interactive_data
                text_content = interactive_data.get('body', {}).get('text', '')
            
            elif message_type == 'location':
                location_data = message_data.get('location', {})
                location_info = location_data
                text_content = f"Location: {location_data.get('name', 'Unknown')}"
            
            elif message_type == 'contacts':
                contacts_data = message_data.get('contacts', [])
                contacts_info = contacts_data
                text_content = f"Contact(s): {len(contacts_data)} shared"
            
            # Extract context (reply info)
            context_info = message_data.get('context')
            
            # Extract profile information
            profile_name = None
            if 'contacts' in message_data and message_data['contacts']:
                profile_name = message_data['contacts'][0].get('profile', {}).get('name')
            
            # Determine direction (requires business logic)
            direction = 'inbound'  # Default assumption for received messages
            
            # Create WhatsApp message object
            whatsapp_message = WhatsAppMessage(
                message_id=message_id,
                wa_id=wa_id,
                phone_number=wa_id,
                profile_name=profile_name,
                text=text_content,
                message_type=message_type,
                timestamp=timestamp,
                status=message_data.get('status', 'received'),
                context=context_info,
                interactive=interactive_info,
                location=location_info,
                contacts=contacts_info,
                media=media_info,
                media_id=media_info.get('id') if media_info else None,
                media_url=None,  # Would need separate API call to get URL
                media_mime_type=media_info.get('mime_type') if media_info else None,
                media_sha256=media_info.get('sha256') if media_info else None,
                media_file_size=media_info.get('file_size') if media_info else None,
                caption=media_info.get('caption') if media_info else None,
                filename=media_info.get('filename') if media_info else None,
                audio_recognition=None,  # Would need speech-to-text processing
                button_reply=interactive_info.get('button_reply') if interactive_info else None,
                list_reply=interactive_info.get('list_reply') if interactive_info else None,
                webhook_id=message_data.get('webhook_id', ''),
                business_phone_number_id=self.phone_number_id or '',
                metadata=message_data,
                conversation_id=None,  # Would need conversation tracking
                direction=direction,
                billing_category=message_data.get('pricing', {}).get('category'),
                error_info=message_data.get('errors')
            )
            
            return whatsapp_message
            
        except Exception as e:
            self.logger.error(f"Error parsing WhatsApp message data: {str(e)}")
            return None
    
    async def _check_rate_limit(self):
        """Check and enforce rate limiting"""
        try:
            current_time = time.time()
            time_since_last = current_time - self.last_request_time
            
            # Enforce minimum delay between requests
            min_interval = 60.0 / self.requests_per_minute
            if time_since_last < min_interval:
                await asyncio.sleep(min_interval - time_since_last)
            
            self.last_request_time = current_time
            self.request_count += 1
            
        except Exception as e:
            self.logger.error(f"Error in rate limiting: {str(e)}")
    
    async def download_media(self, media_id: str, output_path: str = None) -> Optional[str]:
        """Download media file from WhatsApp Business API"""
        try:
            # Get media URL
            url = f"{self.base_url}/{media_id}"
            
            async with aiohttp.ClientSession(headers=self.session_headers) as session:
                # First, get media info
                async with session.get(url) as response:
                    if response.status == 200:
                        media_info = await response.json()
                        media_url = media_info.get('url')
                        
                        if media_url:
                            # Download the actual media file
                            async with session.get(media_url) as media_response:
                                if media_response.status == 200:
                                    media_content = await media_response.read()
                                    
                                    if output_path:
                                        with open(output_path, 'wb') as f:
                                            f.write(media_content)
                                        return output_path
                                    else:
                                        # Return base64 encoded content
                                        return base64.b64encode(media_content).decode('utf-8')
                    
            return None
            
        except Exception as e:
            self.logger.error(f"Error downloading WhatsApp media: {str(e)}")
            return None
    
    async def extract_content_metadata(self, url: str) -> Dict[str, Any]:
        """Extract metadata from WhatsApp Business content"""
        try:
            metadata = {
                'platform': 'whatsapp_business',
                'url': url,
                'extracted_at': datetime.utcnow().isoformat()
            }
            
            # Parse WhatsApp URLs
            if 'whatsapp://' in url:
                parts = url.replace('whatsapp://', '').split('/')
                if len(parts) >= 2:
                    content_type = parts[0]
                    content_id = parts[1]
                    
                    metadata.update({
                        'content_type': content_type,
                        'content_id': content_id
                    })
                    
                    if content_type == 'message':
                        metadata['message_id'] = content_id
                    elif content_type == 'contact':
                        metadata['phone_number'] = content_id
                    elif content_type == 'template':
                        metadata['template_id'] = content_id
                    elif content_type == 'conversation':
                        metadata['conversation_phone'] = content_id
            
            return metadata
            
        except Exception as e:
            self.logger.error(f"Error extracting WhatsApp Business metadata: {str(e)}")
            return {'error': str(e)}
    
    def get_platform_info(self) -> Dict[str, Any]:
        """Get WhatsApp Business platform information"""
        return {
            'platform_name': 'WhatsApp Business',
            'base_url': self.base_url,
            'supported_content_types': list(self.content_types.keys()),
            'rate_limits': {
                'requests_per_minute': self.requests_per_minute,
                'min_delay': self.min_delay,
                'max_delay': self.max_delay
            },
            'features': [
                'Message content analysis',
                'Media file tracking',
                'Contact management',
                'Conversation analytics',
                'Template message monitoring',
                'Webhook event processing',
                'Business metrics tracking',
                'Compliance and audit trails',
                'Multi-language support',
                'Real-time notifications'
            ],
            'authentication': {
                'required': True,
                'type': 'Facebook Graph API Access Token',
                'scope': 'WhatsApp Business Management'
            },
            'limitations': [
                'Requires WhatsApp Business Account',
                'Strict rate limiting',
                'API access restrictions',
                'Media download limitations',
                'Webhook configuration required for real-time events',
                'Business verification required for advanced features'
            ],
            'message_types': [
                'text', 'image', 'audio', 'video', 'document',
                'location', 'contacts', 'interactive', 'template'
            ]
        }
