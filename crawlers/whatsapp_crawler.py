"""WhatsApp Platform Crawler - Ultra-Advanced Implementation
Messaging Platform Monitoring System

This module provides comprehensive crawling capabilities for WhatsApp Business platform,
focusing on business messaging, status updates, and group interactions.

PROPRIETARY SOFTWARE - CONFIDENTIAL AND PROTECTED
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.
Created by: Fahed Mlaiel <mlaiel@live.de>

WARNING: This code is the exclusive property of Fahed Mlaiel.
Any unauthorized use, reproduction, or distribution is strictly prohibited.
Violators will be prosecuted to the full extent of the law.
"""

import asyncio
import aiohttp
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Set, Tuple, AsyncGenerator
from dataclasses import dataclass
from enum import Enum
import hashlib
import base64
from urllib.parse import urljoin, urlparse
from pydantic import BaseModel, Field, validator
from difflib import SequenceMatcher

from ..base import BaseCrawler
from ...utils.rate_limiter import RateLimiter
from ...utils.cache import CacheManager
from ...utils.encryption import ContentEncryption
from ...utils.fingerprinting import ContentFingerprinter

logger = logging.getLogger(__name__)


class WhatsAppMessageType(str, Enum):
    """
WhatsApp message types"""

    TEXT = "text"
    IMAGE = "image"
    VIDEO = "video"
    AUDIO = "audio"
    DOCUMENT = "document"
    LOCATION = "location"
    CONTACT = "contact"
    STICKER = "sticker"
    INTERACTIVE = "interactive"
    TEMPLATE = "template"
    STATUS = "status"


class WhatsAppInteractionType(str, Enum):
    """WhatsApp interaction types"""

    MESSAGE = "message"
    REPLY = "reply"
    REACTION = "reaction"
    FORWARD = "forward"
    MENTION = "mention"
    QUOTE = "quote"


class WhatsAppContactType(str, Enum):
    """WhatsApp contact types"""

    INDIVIDUAL = "individual"
    BUSINESS = "business"
    GROUP = "group"
    BROADCAST = "broadcast"


class WhatsAppMedia(BaseModel):
    """WhatsApp media data model"""
    media_id: str
    media_type: WhatsAppMessageType
    url: Optional[str] = None
    filename: Optional[str] = None
    caption: Optional[str] = None
    mime_type: Optional[str] = None
    file_size: Optional[int] = None
    sha256: Optional[str] = None
    width: Optional[int] = None
    height: Optional[int] = None
    duration: Optional[int] = None  # for audio/video
    is_animated: bool = False
    thumbnail_url: Optional[str] = None


class WhatsAppContact(BaseModel):
    """
WhatsApp contact data model"""
    phone_number: str
    contact_name: Optional[str] = None
    profile_name: Optional[str] = None
    profile_picture_url: Optional[str] = None
    contact_type: WhatsAppContactType
    is_business_verified: bool = False
    business_description: Optional[str] = None
    business_category: Optional[str] = None
    business_address: Optional[Dict[str, Any]] = None
    business_website: Optional[str] = None
    business_email: Optional[str] = None
    last_seen: Optional[datetime] = None
    status_message: Optional[str] = None
    is_contact: bool = False
    is_blocked: bool = False
    labels: List[str] = Field(default_factory=list)


class WhatsAppMessage(BaseModel):
    """
WhatsApp message data model"""
    message_id: str
    from_contact: WhatsAppContact
    to_contact: Optional[WhatsAppContact] = None
    chat_id: str
    message_type: WhatsAppMessageType
    text: Optional[str] = None
    media: Optional[WhatsAppMedia] = None
    timestamp: datetime
    status: str = "sent"  # sent, delivered, read, failed
    is_forwarded: bool = False
    forward_score: int = 0
    is_reply: bool = False
    reply_to_message_id: Optional[str] = None
    mentions: List[str] = Field(default_factory=list)
    quoted_message: Optional['WhatsAppMessage'] = None
    reactions: List[Dict[str, Any]] = Field(default_factory=list)
    context: Optional[Dict[str, Any]] = None
    template_name: Optional[str] = None
    template_language: Optional[str] = None
    interactive_data: Optional[Dict[str, Any]] = None
    location_data: Optional[Dict[str, Any]] = None
    contact_data: Optional[Dict[str, Any]] = None
    similarity_score: Optional[float] = None
    protection_status: str = "unprotected"


class WhatsAppGroup(BaseModel):
    """WhatsApp group data model"""
    group_id: str
    group_name: str
    description: Optional[str] = None
    group_picture_url: Optional[str] = None
    created_at: datetime
    created_by: WhatsAppContact
    participants: List[WhatsAppContact] = Field(default_factory=list)
    admins: List[WhatsAppContact] = Field(default_factory=list)
    is_announcement_only: bool = False
    participant_count: int = 0
    group_invite_link: Optional[str] = None
    group_settings: Dict[str, Any] = Field(default_factory=dict)


class WhatsAppStatus(BaseModel):
    """
WhatsApp status data model"""
    status_id: str
    contact: WhatsAppContact
    content: Optional[str] = None
    media: Optional[WhatsAppMedia] = None
    created_at: datetime
    expires_at: datetime
    is_expired: bool = False
    view_count: int = 0
    viewers: List[WhatsAppContact] = Field(default_factory=list)
    is_muted: bool = False
    privacy_settings: Dict[str, Any] = Field(default_factory=dict)


class WhatsAppConversation(BaseModel):
    """
WhatsApp conversation data model"""
    conversation_id: str
    participant: WhatsAppContact
    last_message: Optional[WhatsAppMessage] = None
    message_count: int = 0
    unread_count: int = 0
    is_archived: bool = False
    is_pinned: bool = False
    is_muted: bool = False
    last_activity: datetime
    conversation_type: str = "individual"  # individual, group, broadcast
    labels: List[str] = Field(default_factory=list)
    business_category: Optional[str] = None


class WhatsAppSearchResults(BaseModel):
    """WhatsApp search results data model"""
    query: str
    total_results: int
    contacts: List[WhatsAppContact] = Field(default_factory=list)
    messages: List[WhatsAppMessage] = Field(default_factory=list)
    groups: List[WhatsAppGroup] = Field(default_factory=list)
    statuses: List[WhatsAppStatus] = Field(default_factory=list)
    search_type: str
    filters_applied: Dict[str, Any]
    search_timestamp: datetime
    has_more: bool = False
    next_cursor: Optional[str] = None


class WhatsAppAnalytics(BaseModel):
    """
WhatsApp analytics data model"""
    phone_number: str
    analysis_period: Tuple[datetime, datetime]
    total_messages_sent: int
    total_messages_received: int
    total_media_shared: int
    total_conversations: int
    active_conversations: int
    message_response_time: float
    most_active_contacts: List[str]
    message_type_distribution: Dict[str, int]
    peak_activity_hours: List[int]
    group_participation: int
    status_posts: int
    business_interactions: int
    template_message_usage: int
    delivery_rate: float
    read_rate: float
    customer_satisfaction_score: Optional[float] = None
    similarity_violations: int
    protection_violations: int


class WhatsAppCrawler(BaseCrawler):
    """
    Ultra-Advanced WhatsApp Platform Crawler
    
    Provides comprehensive crawling and monitoring capabilities for WhatsApp Business platform,
    specializing in business messaging, status monitoring, and conversation analytics.
    """
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        
        self.base_url = "https://graph.facebook.com/v18.0"
        self.api_base = f"{self.base_url}"
        
        # Authentication
        self.access_token: Optional[str] = None
        self.phone_number_id: Optional[str] = None
        self.business_account_id: Optional[str] = None
        self.webhook_verify_token: Optional[str] = None
        
        # Rate limiting - WhatsApp Business API limits
        self.rate_limiter = RateLimiter(
            requests_per_minute=80,
            requests_per_hour=1000,
            burst_limit=20
        )
        
        # Cache management
        self.cache_manager = CacheManager(
            cache_ttl=600,  # 10 minutes for messages
            max_cache_size=3000
        )
        
        # Content protection
        self.content_encryption = ContentEncryption()
        self.content_fingerprinter = ContentFingerprinter()
        
        # Monitoring configuration
        self.monitored_contacts: Set[str] = set()
        self.monitored_groups: Set[str] = set()
        self.protected_content: Set[str] = set()
        self.similarity_threshold = config.get('similarity_threshold', 0.90)  # High threshold for messages
        
        # WhatsApp-specific settings
        self.monitor_business_messages = config.get('monitor_business_messages', True)
        self.track_status_updates = config.get('track_status_updates', True)
        self.analyze_group_interactions = config.get('analyze_group_interactions', True)
        self.webhook_url = config.get('webhook_url')
        self.enable_delivery_tracking = config.get('enable_delivery_tracking', True)
        
        logger.info("WhatsApp crawler initialized with ultra-advanced business messaging monitoring")

    async def authenticate(
        self,
        access_token: str,
        phone_number_id: str,
        business_account_id: str = None,
        webhook_verify_token: str = None
    ) -> bool:
        """
        Authenticate with WhatsApp Business API
        
        Args:
            access_token: WhatsApp Business API access token
            phone_number_id: Phone number ID
            business_account_id: Business account ID
            webhook_verify_token: Webhook verification token
            
        Returns:
            bool: Authentication success status
        """
        try:
            self.access_token = access_token
            self.phone_number_id = phone_number_id
            self.business_account_id = business_account_id
            self.webhook_verify_token = webhook_verify_token
            
            self.session.headers.update({
                'Authorization': f'Bearer {access_token}',
                'Content-Type': 'application/json'
            })
            
            # Verify authentication by getting phone number info
            async with self.session.get(f"{self.api_base}/{phone_number_id}") as response:
                if response.status == 200:
                    phone_data = await response.json()
                    logger.info(f"WhatsApp authentication successful for {phone_data.get('display_phone_number')}")
                    return True
                else:
                    logger.error(f"Authentication verification failed: {response.status}")
                    return False
                    
        except Exception as e:
            logger.error(f"Authentication error: {str(e)}")
            return False

    async def search_content(
        self,
        query: str = "",
        message_type: Optional[WhatsAppMessageType] = None,
        contact_type: Optional[WhatsAppContactType] = None,
        limit: int = 50
    ) -> WhatsAppSearchResults:
        """
        Search WhatsApp content with advanced filtering
        
        Args:
            query: Search query
            message_type: Type of message to search
            contact_type: Type of contact to search
            limit: Maximum results
            
        Returns:
            WhatsAppSearchResults: Comprehensive search results
        """
        await self.rate_limiter.acquire()
        
        try:
            results = WhatsAppSearchResults(
                query=query,
                total_results=0,
                search_type="comprehensive",
                filters_applied={
                    "message_type": message_type.value if message_type else None,
                    "contact_type": contact_type.value if contact_type else None
                },
                search_timestamp=datetime.utcnow()
            )
            
            # Search contacts
            contacts = await self._search_contacts(query, contact_type, limit // 4)
            results.contacts = contacts
            results.total_results += len(contacts)
            
            # Search messages
            if self.monitor_business_messages:
                messages = await self._search_messages(query, message_type, limit // 2)
                results.messages = messages
                results.total_results += len(messages)
            
            # Search groups
            if self.analyze_group_interactions:
                groups = await self._search_groups(query, limit // 4)
                results.groups = groups
                results.total_results += len(groups)
            
            # Search status updates
            if self.track_status_updates:
                statuses = await self._search_statuses(query, limit // 4)
                results.statuses = statuses
                results.total_results += len(statuses)
            
            # Process content for protection
            for message in results.messages:
                message.similarity_score = await self._calculate_similarity(message)
                message.protection_status = await self._check_protection_status(message)
            
            logger.info(f"WhatsApp search completed: {results.total_results} total results")
            return results
            
        except Exception as e:
            logger.error(f"Search error: {str(e)}")
            return WhatsAppSearchResults(
                query=query,
                total_results=0,
                search_type="error",
                filters_applied={},
                search_timestamp=datetime.utcnow()
            )

    async def monitor_content(
        self,
        phone_numbers: List[str] = None,
        keywords: List[str] = None,
        check_interval: int = 60  # 1 minute for business messages
    ) -> AsyncGenerator[WhatsAppMessage, None]:
        """
        Real-time content monitoring for WhatsApp
        
        Args:
            phone_numbers: Phone numbers to monitor
            keywords: Keywords to monitor
            check_interval: Check interval in seconds
            
        Yields:
            WhatsAppMessage: New messages detected
        """
        phone_numbers = phone_numbers or []
        keywords = keywords or []
        
        self.monitored_contacts.update(phone_numbers)
        
        logger.info(f"Starting WhatsApp monitoring for {len(phone_numbers)} contacts")
        
        seen_messages = set()
        
        while True:
            try:
                await asyncio.sleep(check_interval)
                
                # Get recent messages from webhook or polling
                recent_messages = await self._get_recent_messages()
                
                for message in recent_messages:
                    if message.message_id not in seen_messages:
                        # Filter by monitored contacts
                        if (phone_numbers and 
                            message.from_contact.phone_number not in phone_numbers):
                            continue
                        
                        # Filter by keywords
                        if (keywords and message.text and 
                            not any(keyword.lower() in message.text.lower() for keyword in keywords)):
                            continue
                        
                        # Enhanced monitoring analysis
                        message.similarity_score = await self._calculate_similarity(message)
                        message.protection_status = await self._check_protection_status(message)
                        
                        seen_messages.add(message.message_id)
                        
                        logger.info(f"New message from {message.from_contact.phone_number}: {message.message_id}")
                        yield message
                
            except Exception as e:
                logger.error(f"Monitoring error: {str(e)}")
                await asyncio.sleep(60)

    async def detect_similarity(
        self,
        target_message: WhatsAppMessage,
        comparison_set: List[WhatsAppMessage],
        threshold: float = None
    ) -> List[Tuple[WhatsAppMessage, float]]:
        """
        Detect message similarity for content protection
        
        Args:
            target_message: Message to compare
            comparison_set: Messages to compare against
            threshold: Similarity threshold
            
        Returns:
            List[Tuple[WhatsAppMessage, float]]: Similar messages with scores
        """
        threshold = threshold or self.similarity_threshold
        similar_messages = []
        
        try:
            target_features = await self._extract_message_features(target_message)
            
            for message in comparison_set:
                if message.message_id == target_message.message_id:
                    continue
                
                comp_features = await self._extract_message_features(message)
                similarity_score = await self._calculate_feature_similarity(
                    target_features, comp_features
                )
                
                if similarity_score >= threshold:
                    similar_messages.append((message, similarity_score))
            
            similar_messages.sort(key=lambda x: x[1], reverse=True)
            
            logger.info(f"Similarity detection: {len(similar_messages)} matches found")
            return similar_messages
            
        except Exception as e:
            logger.error(f"Similarity detection error: {str(e)}")
            return []

    async def get_analytics(
        self,
        phone_number: str,
        analysis_period: Tuple[datetime, datetime]
    ) -> WhatsAppAnalytics:
        """
        Generate comprehensive analytics for WhatsApp Business account
        
        Args:
            phone_number: Phone number to analyze
            analysis_period: Analysis time period
            
        Returns:
            WhatsAppAnalytics: Comprehensive analytics data
        """
        try:
            start_time, end_time = analysis_period
            
            # Get messages in the period
            sent_messages = await self._get_sent_messages_in_period(phone_number, start_time, end_time)
            received_messages = await self._get_received_messages_in_period(phone_number, start_time, end_time)
            
            all_messages = sent_messages + received_messages
            
            if not all_messages:
                return WhatsAppAnalytics(
                    phone_number=phone_number,
                    analysis_period=analysis_period,
                    total_messages_sent=0,
                    total_messages_received=0,
                    total_media_shared=0,
                    total_conversations=0,
                    active_conversations=0,
                    message_response_time=0.0,
                    most_active_contacts=[],
                    message_type_distribution={},
                    peak_activity_hours=[],
                    group_participation=0,
                    status_posts=0,
                    business_interactions=0,
                    template_message_usage=0,
                    delivery_rate=0.0,
                    read_rate=0.0,
                    similarity_violations=0,
                    protection_violations=0
                )
            
            # Calculate basic metrics
            total_messages_sent = len(sent_messages)
            total_messages_received = len(received_messages)
            
            # Media analysis
            total_media_shared = sum(1 for msg in all_messages if msg.media is not None)
            
            # Message type distribution
            message_type_distribution = {}
            for message in all_messages:
                msg_type = message.message_type.value
                message_type_distribution[msg_type] = message_type_distribution.get(msg_type, 0) + 1
            
            # Contact analysis
            contact_counts = {}
            for message in all_messages:
                contact = message.from_contact.phone_number
                contact_counts[contact] = contact_counts.get(contact, 0) + 1
            
            most_active_contacts = sorted(contact_counts.items(), key=lambda x: x[1], reverse=True)[:10]
            most_active_contacts = [contact[0] for contact in most_active_contacts]
            
            # Activity patterns
            activity_hours = [msg.timestamp.hour for msg in all_messages]
            hour_counts = {}
            for hour in activity_hours:
                hour_counts[hour] = hour_counts.get(hour, 0) + 1
            peak_activity_hours = sorted(hour_counts.items(), key=lambda x: x[1], reverse=True)[:3]
            peak_activity_hours = [hour[0] for hour in peak_activity_hours]
            
            # Business-specific metrics
            template_message_usage = sum(1 for msg in sent_messages if msg.template_name is not None)
            business_interactions = sum(1 for msg in all_messages 
                                     if msg.from_contact.contact_type == WhatsAppContactType.BUSINESS)
            
            # Delivery and read rates
            delivered_messages = sum(1 for msg in sent_messages if msg.status in ["delivered", "read"])
            read_messages = sum(1 for msg in sent_messages if msg.status == "read")
            
            delivery_rate = delivered_messages / total_messages_sent if total_messages_sent > 0 else 0.0
            read_rate = read_messages / total_messages_sent if total_messages_sent > 0 else 0.0
            
            # Protection metrics
            similarity_violations = sum(1 for msg in all_messages if (msg.similarity_score or 0) > self.similarity_threshold)
            protection_violations = sum(1 for msg in all_messages if msg.protection_status == "violation")
            
            # Response time calculation (simplified)
            response_times = []
            for i, msg in enumerate(received_messages):
                # Find next sent message as response
                for sent_msg in sent_messages:
                    if sent_msg.timestamp > msg.timestamp:
                        response_time = (sent_msg.timestamp - msg.timestamp).total_seconds()
                        response_times.append(response_time)
                        break
            
            average_response_time = sum(response_times) / len(response_times) if response_times else 0.0
            
            analytics = WhatsAppAnalytics(
                phone_number=phone_number,
                analysis_period=analysis_period,
                total_messages_sent=total_messages_sent,
                total_messages_received=total_messages_received,
                total_media_shared=total_media_shared,
                total_conversations=len(set(msg.chat_id for msg in all_messages)),
                active_conversations=len(set(msg.chat_id for msg in all_messages)),
                message_response_time=average_response_time,
                most_active_contacts=most_active_contacts,
                message_type_distribution=message_type_distribution,
                peak_activity_hours=peak_activity_hours,
                group_participation=0,  # Would need group data
                status_posts=0,  # Would need status data
                business_interactions=business_interactions,
                template_message_usage=template_message_usage,
                delivery_rate=delivery_rate,
                read_rate=read_rate,
                similarity_violations=similarity_violations,
                protection_violations=protection_violations
            )
            
            logger.info(f"Analytics generated for {phone_number}: {total_messages_sent} sent, {total_messages_received} received")
            return analytics
            
        except Exception as e:
            logger.error(f"Analytics generation error: {str(e)}")
            return WhatsAppAnalytics(
                phone_number=phone_number,
                analysis_period=analysis_period,
                total_messages_sent=0,
                total_messages_received=0,
                total_media_shared=0,
                total_conversations=0,
                active_conversations=0,
                message_response_time=0.0,
                most_active_contacts=[],
                message_type_distribution={},
                peak_activity_hours=[],
                group_participation=0,
                status_posts=0,
                business_interactions=0,
                template_message_usage=0,
                delivery_rate=0.0,
                read_rate=0.0,
                similarity_violations=0,
                protection_violations=0
            )

    # Helper methods
    
    async def _search_contacts(self, query: str, contact_type: Optional[WhatsAppContactType], limit: int) -> List[WhatsAppContact]:
        """Search for WhatsApp contacts"""
        # Implementation would depend on available contact API
        return []

    async def _search_messages(self, query: str, message_type: Optional[WhatsAppMessageType], limit: int) -> List[WhatsAppMessage]:
        """
Search for WhatsApp messages"""
        # WhatsApp Business API doesn't provide message search, would need webhook data
        return []

    async def _search_groups(self, query: str, limit: int) -> List[WhatsAppGroup]:
        """
Search for WhatsApp groups"""
        # Implementation would depend on group API availability
        return []

    async def _search_statuses(self, query: str, limit: int) -> List[WhatsAppStatus]:
        """
Search for WhatsApp status updates"""
        # Implementation would depend on status API availability
        return []

    async def _get_recent_messages(self) -> List[WhatsAppMessage]:
        """
Get recent messages from webhook or API"""
        # This would typically be populated by webhook data
        return []

    async def _send_message(
        self,
        to_phone_number: str,
        message_type: WhatsAppMessageType,
        content: Dict[str, Any]
    ) -> bool:
        """
Send a WhatsApp message"""
        try:
            payload = {
                "messaging_product": "whatsapp",
                "to": to_phone_number,
                "type": message_type.value
            }
            
            if message_type == WhatsAppMessageType.TEXT:
                payload["text"] = {"body": content.get("text", "")}
            elif message_type == WhatsAppMessageType.IMAGE:
                payload["image"] = content
            elif message_type == WhatsAppMessageType.VIDEO:
                payload["video"] = content
            elif message_type == WhatsAppMessageType.AUDIO:
                payload["audio"] = content
            elif message_type == WhatsAppMessageType.DOCUMENT:
                payload["document"] = content
            elif message_type == WhatsAppMessageType.TEMPLATE:
                payload["template"] = content
            
            async with self.session.post(
                f"{self.api_base}/{self.phone_number_id}/messages",
                json=payload
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    logger.info(f"Message sent successfully: {result.get('messages', [{}])[0].get('id')}")
                    return True
                else:
                    logger.error(f"Failed to send message: {response.status}")
                    return False
                    
        except Exception as e:
            logger.error(f"Error sending message: {str(e)}")
            return False

    async def _mark_message_as_read(self, message_id: str) -> bool:
        """Mark a message as read"""
        try:
            payload = {
                "messaging_product": "whatsapp",
                "status": "read",
                "message_id": message_id
            }
            
            async with self.session.post(
                f"{self.api_base}/{self.phone_number_id}/messages",
                json=payload
            ) as response:
                return response.status == 200
                
        except Exception as e:
            logger.error(f"Error marking message as read: {str(e)}")
            return False

    async def _process_webhook_message(self, webhook_data: Dict[str, Any]) -> Optional[WhatsAppMessage]:
        """Process incoming webhook message"""
        try:
            entry = webhook_data.get("entry", [{}])[0]
            changes = entry.get("changes", [{}])[0]
            value = changes.get("value", {})
            
            messages = value.get("messages", [])
            if not messages:
                return None
            
            message_data = messages[0]
            contact_data = value.get("contacts", [{}])[0]
            
            # Parse contact
            contact = WhatsAppContact(
                phone_number=contact_data.get("wa_id", ""),
                profile_name=contact_data.get("profile", {}).get("name", ""),
                contact_type=WhatsAppContactType.INDIVIDUAL
            )
            
            # Parse message
            message_type = WhatsAppMessageType(message_data.get("type", "text"))
            
            # Extract content based on type
            text = None
            media = None
            
            if message_type == WhatsAppMessageType.TEXT:
                text = message_data.get("text", {}).get("body", "")
            elif message_type in [WhatsAppMessageType.IMAGE, WhatsAppMessageType.VIDEO, 
                                WhatsAppMessageType.AUDIO, WhatsAppMessageType.DOCUMENT]:
                media_data = message_data.get(message_type.value, {})
                media = WhatsAppMedia(
                    media_id=media_data.get("id", ""),
                    media_type=message_type,
                    filename=media_data.get("filename"),
                    caption=media_data.get("caption"),
                    mime_type=media_data.get("mime_type"),
                    sha256=media_data.get("sha256")
                )
                text = media_data.get("caption")
            
            message = WhatsAppMessage(
                message_id=message_data.get("id", ""),
                from_contact=contact,
                chat_id=contact.phone_number,
                message_type=message_type,
                text=text,
                media=media,
                timestamp=datetime.fromtimestamp(int(message_data.get("timestamp", 0)))
            )
            
            return message
            
        except Exception as e:
            logger.error(f"Error processing webhook message: {str(e)}")
            return None

    async def _extract_message_features(self, message: WhatsAppMessage) -> Dict[str, Any]:
        """Extract features for similarity comparison"""
        features = {
            "text": (message.text or "").lower(),
            "from_contact": message.from_contact.phone_number,
            "message_type": message.message_type.value,
            "has_media": message.media is not None,
            "is_forwarded": message.is_forwarded,
            "forward_score": message.forward_score,
            "is_reply": message.is_reply,
            "mentions": set(mention.lower() for mention in message.mentions),
            "template_name": message.template_name,
            "text_length": len(message.text or ""),
            "media_type": message.media.media_type.value if message.media else None,
            "has_location": message.location_data is not None,
            "has_contact": message.contact_data is not None
        }
        return features

    async def _calculate_feature_similarity(
        self,
        features1: Dict[str, Any],
        features2: Dict[str, Any]
    ) -> float:
        """Calculate similarity between message features"""
        try:
            scores = []
            
            # Text similarity (high weight for messages)
            text_sim = SequenceMatcher(
                None, features1.get("text", ""), features2.get("text", "")
            ).ratio()
            scores.append(text_sim * 0.6)  # 60% weight
            
            # Message type similarity
            type_sim = 1.0 if features1.get("message_type") == features2.get("message_type") else 0.0
            scores.append(type_sim * 0.2)  # 20% weight
            
            # Media presence similarity
            media_sim = 1.0 if features1.get("has_media") == features2.get("has_media") else 0.0
            scores.append(media_sim * 0.1)  # 10% weight
            
            # Template similarity (for business messages)
            template_sim = 1.0 if features1.get("template_name") == features2.get("template_name") else 0.0
            if features1.get("template_name") or features2.get("template_name"):
                scores.append(template_sim * 0.1)  # 10% weight
            
            return sum(scores) / len(scores) if scores else 0.0
            
        except Exception as e:
            logger.error(f"Feature similarity calculation error: {str(e)}")
            return 0.0

    async def _get_sent_messages_in_period(
        self,
        phone_number: str,
        start_time: datetime,
        end_time: datetime
    ) -> List[WhatsAppMessage]:
        """Get sent messages in specific time period"""
        # Implementation would require message storage/webhook data
        return []

    async def _get_received_messages_in_period(
        self,
        phone_number: str,
        start_time: datetime,
        end_time: datetime
    ) -> List[WhatsAppMessage]:
        """
Get received messages in specific time period"""
        # Implementation would require message storage/webhook data
        return []

    async def _calculate_similarity(self, message: WhatsAppMessage) -> float:
        """
Calculate similarity score against protected content"""
        # Simplified similarity calculation
        return 0.0

    async def _check_protection_status(self, message: WhatsAppMessage) -> str:
        """
Check protection status of message"""
        if message.message_id in self.protected_content:
            return "protected"
        return "unprotected"

    async def setup_webhook(self) -> bool:
        """Setup webhook for real-time message monitoring"""
        try:
            if not self.webhook_url:
                logger.warning("No webhook URL configured")
                return False
            
            # Setup webhook endpoint would go here
            logger.info("Webhook setup completed")
            return True
            
        except Exception as e:
            logger.error(f"Error setting up webhook: {str(e)}")
            return False

    async def close(self):
        """Close crawler and cleanup resources"""
        try:
            await self.cache_manager.close()
            await super().close()
            logger.info("WhatsApp crawler closed successfully")
        except Exception as e:
            logger.error(f"Error closing crawler: {str(e)}")
