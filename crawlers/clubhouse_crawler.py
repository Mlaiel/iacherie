"""
Clubhouse Platform Crawler - Ultra-Advanced Implementation
Audio-First Social Network Content Monitoring System

This module provides comprehensive crawling capabilities for Clubhouse platform,
focusing on live audio conversations, content protection, and real-time monitoring.

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
import speech_recognition as sr
import io
import wave

from ..base import BaseCrawler
from ...utils.rate_limiter import RateLimiter
from ...utils.cache import CacheManager
from ...utils.encryption import ContentEncryption
from ...utils.fingerprinting import AudioFingerprinter

logger = logging.getLogger(__name__)


class ClubhouseRoomType(str, Enum):
    """Clubhouse room types"""
    OPEN = "open"
    SOCIAL = "social"
    CLOSED = "closed"


class ClubhouseRoomStatus(str, Enum):
    """Clubhouse room status"""
    LIVE = "live"
    ENDED = "ended"
    SCHEDULED = "scheduled"
    CANCELLED = "cancelled"


class ClubhouseUserRole(str, Enum):
    """User roles in Clubhouse rooms"""
    MODERATOR = "moderator"
    SPEAKER = "speaker"
    LISTENER = "listener"
    FOLLOWER = "follower"


class ClubhouseContentType(str, Enum):
    """Clubhouse content types"""
    ROOM = "room"
    CONVERSATION = "conversation"
    ANNOUNCEMENT = "announcement"
    EVENT = "event"
    REPLAY = "replay"


class ClubhouseAudioSegment(BaseModel):
    """Audio segment data model"""
    segment_id: str
    speaker_user_id: str
    start_time: float  # seconds from room start
    end_time: float
    audio_url: Optional[str] = None
    transcript: Optional[str] = None
    confidence_score: Optional[float] = None
    language: str = "en"
    audio_quality: str = "standard"
    is_processed: bool = False
    waveform_data: Optional[str] = None  # Base64 encoded
    audio_fingerprint: Optional[str] = None


class ClubhouseUser(BaseModel):
    """Clubhouse user data model"""
    user_id: str
    username: str
    name: str
    bio: Optional[str] = None
    photo_url: Optional[str] = None
    followers_count: int = 0
    following_count: int = 0
    invited_by_user_id: Optional[str] = None
    is_speaker: bool = False
    is_moderator: bool = False
    is_invited_speaker: bool = False
    is_followed_by_speaker: bool = False
    time_created: datetime
    url: Optional[str] = None
    twitter: Optional[str] = None
    instagram: Optional[str] = None
    num_mutual_followers: int = 0
    notification_type: Optional[str] = None
    club_role: Optional[str] = None
    is_blocked_by_network: bool = False


class ClubhouseClub(BaseModel):
    """Clubhouse club data model"""
    club_id: str
    name: str
    description: Optional[str] = None
    photo_url: Optional[str] = None
    num_members: int = 0
    num_followers: int = 0
    enable_private: bool = False
    is_follow_allowed: bool = True
    is_membership_private: bool = False
    is_community: bool = False
    rules: List[str] = Field(default_factory=list)
    topics: List[str] = Field(default_factory=list)
    created_at: datetime
    updated_at: datetime


class ClubhouseRoom(BaseModel):
    """Clubhouse room data model"""
    channel: str  # room ID
    channel_user: ClubhouseUser
    topic: str
    is_private: bool = False
    is_social_mode: bool = False
    url: str
    creation_datetime: datetime
    language: str = "en"
    room_type: ClubhouseRoomType = ClubhouseRoomType.OPEN
    status: ClubhouseRoomStatus = ClubhouseRoomStatus.LIVE
    num_other: int = 0
    has_blocked_speakers: bool = False
    is_explore_feature: bool = False
    num_speakers: int = 0
    num_all: int = 0
    users: List[ClubhouseUser] = Field(default_factory=list)
    success: bool = True
    is_handraise_enabled: bool = True
    handraise_permission: int = 1
    is_club_member: bool = False
    is_club_admin: bool = False
    club: Optional[ClubhouseClub] = None
    club_id: Optional[str] = None
    welcome_for_user_profile: Optional[ClubhouseUser] = None
    is_empty: bool = False
    thank_you_artists: List[ClubhouseUser] = Field(default_factory=list)
    feature_flags: List[str] = Field(default_factory=list)
    club_name: Optional[str] = None
    club_topic: Optional[str] = None
    is_official: bool = False


class ClubhouseConversation(BaseModel):
    """Clubhouse conversation data model"""
    conversation_id: str
    room: ClubhouseRoom
    audio_segments: List[ClubhouseAudioSegment] = Field(default_factory=list)
    duration: int = 0  # seconds
    participant_count: int = 0
    peak_audience: int = 0
    language_distribution: Dict[str, int] = Field(default_factory=dict)
    topics_discussed: List[str] = Field(default_factory=list)
    keywords: List[str] = Field(default_factory=list)
    sentiment_score: Optional[float] = None
    toxicity_score: Optional[float] = None
    content_warnings: List[str] = Field(default_factory=list)
    is_recorded: bool = False
    recording_url: Optional[str] = None
    transcript_summary: Optional[str] = None
    start_time: datetime
    end_time: Optional[datetime] = None
    similarity_score: Optional[float] = None
    protection_status: str = "unprotected"


class ClubhouseEvent(BaseModel):
    """Clubhouse event data model"""
    event_id: str
    name: str
    description: Optional[str] = None
    time_start: datetime
    club: Optional[ClubhouseClub] = None
    hosts: List[ClubhouseUser] = Field(default_factory=list)
    is_member_only: bool = False
    url: str
    num_attending: int = 0
    is_attending: bool = False


class ClubhouseSearchResults(BaseModel):
    """Clubhouse search results data model"""
    query: str
    total_results: int
    rooms: List[ClubhouseRoom] = Field(default_factory=list)
    conversations: List[ClubhouseConversation] = Field(default_factory=list)
    users: List[ClubhouseUser] = Field(default_factory=list)
    clubs: List[ClubhouseClub] = Field(default_factory=list)
    events: List[ClubhouseEvent] = Field(default_factory=list)
    search_type: str
    filters_applied: Dict[str, Any]
    search_timestamp: datetime
    has_more: bool = False
    next_cursor: Optional[str] = None


class ClubhouseAnalytics(BaseModel):
    """Clubhouse analytics data model"""
    user_id: str
    analysis_period: Tuple[datetime, datetime]
    total_rooms_created: int
    total_rooms_joined: int
    speaking_time: int  # seconds
    listening_time: int  # seconds
    average_room_duration: float
    most_active_topics: List[str]
    speaking_frequency: float
    audience_growth: int
    follower_conversion_rate: float
    engagement_score: float
    content_quality_score: float
    network_influence: float
    room_completion_rate: float
    audio_quality_average: float
    language_distribution: Dict[str, float]
    toxicity_incidents: int
    content_warnings_received: int
    similarity_violations: int
    protection_violations: int


class ClubhouseCrawler(BaseCrawler):
    """
    Ultra-Advanced Clubhouse Platform Crawler
    
    Provides comprehensive crawling and monitoring capabilities for Clubhouse platform,
    specializing in live audio content, conversation analysis, and real-time protection.
    """
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        
        self.base_url = "https://www.clubhouseapi.com/api"
        self.client_url = "https://clubhouseapi.com"
        
        # Authentication
        self.auth_token: Optional[str] = None
        self.refresh_token: Optional[str] = None
        self.device_id: str = self._generate_device_id()
        self.user_id: Optional[str] = None
        
        # Rate limiting - Clubhouse has strict audio streaming limits
        self.rate_limiter = RateLimiter(
            requests_per_minute=20,
            requests_per_hour=300,
            burst_limit=5
        )
        
        # Cache management
        self.cache_manager = CacheManager(
            cache_ttl=180,  # 3 minutes for live content
            max_cache_size=500
        )
        
        # Audio processing
        self.speech_recognizer = sr.Recognizer()
        self.audio_fingerprinter = AudioFingerprinter()
        self.content_encryption = ContentEncryption()
        
        # Monitoring configuration
        self.monitored_users: Set[str] = set()
        self.monitored_topics: Set[str] = set()
        self.protected_content: Set[str] = set()
        self.similarity_threshold = config.get('similarity_threshold', 0.8)
        
        # Audio settings
        self.enable_transcription = config.get('enable_transcription', True)
        self.enable_audio_fingerprinting = config.get('enable_audio_fingerprinting', True)
        self.audio_quality_threshold = config.get('audio_quality_threshold', 0.7)
        self.max_recording_duration = config.get('max_recording_duration', 3600)  # 1 hour
        
        # Content analysis
        self.enable_sentiment_analysis = config.get('enable_sentiment_analysis', True)
        self.enable_toxicity_detection = config.get('enable_toxicity_detection', True)
        self.content_warning_keywords = config.get('content_warning_keywords', [])
        
        logger.info("Clubhouse crawler initialized with ultra-advanced audio monitoring")

    def _generate_device_id(self) -> str:
        """Generate unique device identifier"""
        import uuid
        return str(uuid.uuid4()).replace('-', '').upper()[:16]

    async def authenticate(self, phone_number: str, verification_code: Optional[str] = None) -> bool:
        """
        Authenticate with Clubhouse platform
        
        Args:
            phone_number: Phone number for authentication
            verification_code: SMS verification code
            
        Returns:
            bool: Authentication success status
        """
        try:
            headers = {
                "CH-Languages": "en-US",
                "CH-Locale": "en_US",
                "Accept": "application/json",
                "Accept-Language": "en-US;q=1.0",
                "Accept-Encoding": "gzip, deflate",
                "CH-AppBuild": "4770",
                "CH-AppVersion": "1.2.12",
                "User-Agent": "clubhouse/4770 (iPhone; iOS 14.7.1; Scale/3.00)",
                "CH-DeviceId": self.device_id,
                "Connection": "close",
                "Content-Type": "application/json; charset=utf-8"
            }
            
            if not verification_code:
                # Request verification code
                auth_data = {
                    "phone_number": phone_number
                }
                
                async with self.session.post(
                    f"{self.base_url}/start_phone_number_auth",
                    json=auth_data,
                    headers=headers
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        if result.get("success"):
                            logger.info("Verification code sent successfully")
                            return False  # Need verification code
                    
                    logger.error(f"Failed to send verification code: {response.status}")
                    return False
            
            else:
                # Complete authentication
                verify_data = {
                    "phone_number": phone_number,
                    "verification_code": verification_code
                }
                
                async with self.session.post(
                    f"{self.base_url}/complete_phone_number_auth",
                    json=verify_data,
                    headers=headers
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        
                        if result.get("success"):
                            self.auth_token = result.get("auth_token")
                            self.refresh_token = result.get("refresh_token")
                            self.user_id = result.get("user_profile", {}).get("user_id")
                            
                            # Update session headers
                            self.session.headers.update({
                                "Authorization": f"Token {self.auth_token}",
                                "CH-DeviceId": self.device_id,
                                "CH-UserID": self.user_id or ""
                            })
                            
                            logger.info("Clubhouse authentication successful")
                            return True
                        else:
                            logger.error("Authentication failed: Invalid verification code")
                            return False
                    else:
                        logger.error(f"Authentication failed: {response.status}")
                        return False
                        
        except Exception as e:
            logger.error(f"Authentication error: {str(e)}")
            return False

    async def search_content(
        self,
        query: str = "",
        content_type: Optional[ClubhouseContentType] = None,
        language: Optional[str] = None,
        is_live_only: bool = False,
        limit: int = 50
    ) -> ClubhouseSearchResults:
        """
        Search Clubhouse content with advanced filtering
        
        Args:
            query: Search query
            content_type: Type of content to search
            language: Language filter
            is_live_only: Only return live rooms
            limit: Maximum results
            
        Returns:
            ClubhouseSearchResults: Comprehensive search results
        """
        await self.rate_limiter.acquire()
        
        try:
            # Check cache first
            cache_key = f"search_{hashlib.md5(f'{query}_{content_type}_{language}_{is_live_only}'.encode()).hexdigest()}"
            cached_result = await self.cache_manager.get(cache_key)
            if cached_result:
                return ClubhouseSearchResults(**cached_result)
            
            results = ClubhouseSearchResults(
                query=query,
                total_results=0,
                search_type="comprehensive",
                filters_applied={
                    "content_type": content_type.value if content_type else None,
                    "language": language,
                    "is_live_only": is_live_only
                },
                search_timestamp=datetime.utcnow()
            )
            
            # Search rooms
            if not content_type or content_type == ClubhouseContentType.ROOM:
                rooms = await self._search_rooms(query, language, is_live_only, limit // 4)
                results.rooms = rooms
                results.total_results += len(rooms)
            
            # Search users
            if not content_type or content_type in [ClubhouseContentType.CONVERSATION]:
                users = await self._search_users(query, limit // 4)
                results.users = users
                results.total_results += len(users)
            
            # Search clubs
            clubs = await self._search_clubs(query, limit // 4)
            results.clubs = clubs
            results.total_results += len(clubs)
            
            # Search events
            if not content_type or content_type == ClubhouseContentType.EVENT:
                events = await self._search_events(query, limit // 4)
                results.events = events
                results.total_results += len(events)
            
            # Process content for protection analysis
            for room in results.rooms:
                conversation = await self._analyze_room_content(room)
                if conversation:
                    conversation.similarity_score = await self._calculate_similarity(conversation)
                    conversation.protection_status = await self._check_protection_status(conversation)
                    results.conversations.append(conversation)
            
            # Cache results
            await self.cache_manager.set(cache_key, results.dict())
            
            logger.info(f"Clubhouse search completed: {results.total_results} total results")
            return results
            
        except Exception as e:
            logger.error(f"Search error: {str(e)}")
            return ClubhouseSearchResults(
                query=query,
                total_results=0,
                search_type="error",
                filters_applied={},
                search_timestamp=datetime.utcnow()
            )

    async def _search_rooms(
        self,
        query: str,
        language: Optional[str],
        is_live_only: bool,
        limit: int
    ) -> List[ClubhouseRoom]:
        """Search for Clubhouse rooms"""
        try:
            # Get current live rooms
            async with self.session.get(f"{self.base_url}/get_channels") as response:
                if response.status == 200:
                    data = await response.json()
                    rooms = []
                    
                    for channel_data in data.get("channels", [])[:limit]:
                        try:
                            room = await self._parse_room_data(channel_data)
                            
                            # Apply filters
                            if query and query.lower() not in room.topic.lower():
                                continue
                            
                            if language and room.language != language:
                                continue
                            
                            if is_live_only and room.status != ClubhouseRoomStatus.LIVE:
                                continue
                            
                            rooms.append(room)
                            
                        except Exception as e:
                            logger.warning(f"Error parsing room data: {str(e)}")
                            continue
                    
                    return rooms
                else:
                    logger.error(f"Failed to fetch rooms: {response.status}")
                    return []
                    
        except Exception as e:
            logger.error(f"Room search error: {str(e)}")
            return []

    async def _search_users(self, query: str, limit: int) -> List[ClubhouseUser]:
        """Search for Clubhouse users"""
        try:
            search_data = {
                "query": query,
                "followers_only": False,
                "following_only": False,
                "cofollows_only": False
            }
            
            async with self.session.post(
                f"{self.base_url}/search_users",
                json=search_data
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    users = []
                    
                    for user_data in data.get("users", [])[:limit]:
                        try:
                            user = await self._parse_user_data(user_data)
                            users.append(user)
                        except Exception as e:
                            logger.warning(f"Error parsing user data: {str(e)}")
                            continue
                    
                    return users
                else:
                    return []
                    
        except Exception as e:
            logger.error(f"User search error: {str(e)}")
            return []

    async def _search_clubs(self, query: str, limit: int) -> List[ClubhouseClub]:
        """Search for Clubhouse clubs"""
        try:
            search_data = {
                "query": query
            }
            
            async with self.session.post(
                f"{self.base_url}/search_clubs",
                json=search_data
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    clubs = []
                    
                    for club_data in data.get("clubs", [])[:limit]:
                        try:
                            club = await self._parse_club_data(club_data)
                            clubs.append(club)
                        except Exception as e:
                            logger.warning(f"Error parsing club data: {str(e)}")
                            continue
                    
                    return clubs
                else:
                    return []
                    
        except Exception as e:
            logger.error(f"Club search error: {str(e)}")
            return []

    async def _search_events(self, query: str, limit: int) -> List[ClubhouseEvent]:
        """Search for Clubhouse events"""
        try:
            async with self.session.get(f"{self.base_url}/get_events") as response:
                if response.status == 200:
                    data = await response.json()
                    events = []
                    
                    for event_data in data.get("events", [])[:limit]:
                        try:
                            if query.lower() in event_data.get("name", "").lower():
                                event = await self._parse_event_data(event_data)
                                events.append(event)
                        except Exception as e:
                            logger.warning(f"Error parsing event data: {str(e)}")
                            continue
                    
                    return events
                else:
                    return []
                    
        except Exception as e:
            logger.error(f"Event search error: {str(e)}")
            return []

    async def get_content_details(self, room_id: str) -> Optional[ClubhouseConversation]:
        """
        Get detailed information about specific Clubhouse room/conversation
        
        Args:
            room_id: Room/channel ID
            
        Returns:
            Optional[ClubhouseConversation]: Detailed conversation data
        """
        await self.rate_limiter.acquire()
        
        try:
            # Check cache first
            cache_key = f"room_{room_id}"
            cached_content = await self.cache_manager.get(cache_key)
            if cached_content:
                return ClubhouseConversation(**cached_content)
            
            # Get room details
            join_data = {
                "channel": room_id,
                "attribution_source": "feed",
                "attribution_details": "eyJpc19leHBsb3JlIjpmYWxzZSwicmFuayI6MX0"
            }
            
            async with self.session.post(
                f"{self.base_url}/join_channel",
                json=join_data
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    if data.get("success"):
                        room = await self._parse_room_data(data)
                        conversation = await self._analyze_room_content(room)
                        
                        if conversation:
                            # Enhanced analysis
                            conversation.similarity_score = await self._calculate_similarity(conversation)
                            conversation.protection_status = await self._check_protection_status(conversation)
                            
                            # Cache the result
                            await self.cache_manager.set(cache_key, conversation.dict())
                            
                            logger.info(f"Retrieved Clubhouse room details: {room_id}")
                            return conversation
                    
                    return None
                else:
                    logger.warning(f"Room not accessible: {room_id}")
                    return None
                    
        except Exception as e:
            logger.error(f"Error getting room details: {str(e)}")
            return None

    async def monitor_content(
        self,
        user_ids: List[str] = None,
        topics: List[str] = None,
        keywords: List[str] = None,
        check_interval: int = 300
    ) -> AsyncGenerator[ClubhouseConversation, None]:
        """
        Real-time content monitoring for Clubhouse
        
        Args:
            user_ids: User IDs to monitor
            topics: Topics to monitor
            keywords: Keywords to monitor
            check_interval: Check interval in seconds
            
        Yields:
            ClubhouseConversation: New conversations detected
        """
        user_ids = user_ids or []
        topics = topics or []
        keywords = keywords or []
        
        self.monitored_users.update(user_ids)
        self.monitored_topics.update(topics)
        
        logger.info(f"Starting Clubhouse monitoring for {len(user_ids)} users, {len(topics)} topics")
        
        seen_rooms = set()
        
        while True:
            try:
                await asyncio.sleep(check_interval)
                
                # Get current live rooms
                current_rooms = await self._search_rooms("", None, True, 100)
                
                for room in current_rooms:
                    if room.channel not in seen_rooms:
                        # Check if room matches monitoring criteria
                        should_monitor = False
                        
                        # Check users
                        for user in room.users:
                            if user.user_id in self.monitored_users:
                                should_monitor = True
                                break
                        
                        # Check topics
                        if any(topic.lower() in room.topic.lower() for topic in topics):
                            should_monitor = True
                        
                        # Check keywords in room topic
                        if any(keyword.lower() in room.topic.lower() for keyword in keywords):
                            should_monitor = True
                        
                        if should_monitor:
                            conversation = await self._analyze_room_content(room)
                            if conversation:
                                # Enhanced monitoring analysis
                                conversation.similarity_score = await self._calculate_similarity(conversation)
                                conversation.protection_status = await self._check_protection_status(conversation)
                                
                                seen_rooms.add(room.channel)
                                
                                logger.info(f"New monitored Clubhouse room: {room.channel}")
                                yield conversation
                
            except Exception as e:
                logger.error(f"Monitoring error: {str(e)}")
                await asyncio.sleep(60)

    async def _analyze_room_content(self, room: ClubhouseRoom) -> Optional[ClubhouseConversation]:
        """Analyze room content and create conversation object"""
        try:
            conversation = ClubhouseConversation(
                conversation_id=f"conv_{room.channel}",
                room=room,
                participant_count=room.num_all,
                peak_audience=room.num_all,
                start_time=room.creation_datetime,
                language_distribution={room.language: 100}
            )
            
            # Extract topics from room topic
            conversation.topics_discussed = await self._extract_topics(room.topic)
            
            # Basic keyword extraction
            conversation.keywords = await self._extract_keywords(room.topic)
            
            # Check for content warnings
            conversation.content_warnings = await self._detect_content_warnings(room.topic)
            
            return conversation
            
        except Exception as e:
            logger.error(f"Error analyzing room content: {str(e)}")
            return None

    async def _extract_topics(self, text: str) -> List[str]:
        """Extract topics from text"""
        # Simplified topic extraction
        topics = []
        common_topics = [
            "technology", "business", "startup", "investing", "crypto", "nft",
            "music", "art", "entertainment", "sports", "politics", "news",
            "education", "health", "wellness", "travel", "food", "fashion"
        ]
        
        text_lower = text.lower()
        for topic in common_topics:
            if topic in text_lower:
                topics.append(topic)
        
        return topics

    async def _extract_keywords(self, text: str) -> List[str]:
        """Extract keywords from text"""
        # Simple keyword extraction
        words = text.lower().split()
        keywords = [word.strip('.,!?') for word in words if len(word) > 3]
        return keywords[:10]  # Limit to 10 keywords

    async def _detect_content_warnings(self, text: str) -> List[str]:
        """Detect content warnings in text"""
        warnings = []
        warning_keywords = [
            "explicit", "adult", "sensitive", "trigger", "warning",
            "violence", "drug", "alcohol", "mental health"
        ]
        
        text_lower = text.lower()
        for keyword in warning_keywords:
            if keyword in text_lower:
                warnings.append(keyword)
        
        return warnings

    async def detect_similarity(
        self,
        target_conversation: ClubhouseConversation,
        comparison_set: List[ClubhouseConversation],
        threshold: float = None
    ) -> List[Tuple[ClubhouseConversation, float]]:
        """
        Detect conversation similarity
        
        Args:
            target_conversation: Conversation to compare
            comparison_set: Conversations to compare against
            threshold: Similarity threshold
            
        Returns:
            List[Tuple[ClubhouseConversation, float]]: Similar conversations with scores
        """
        threshold = threshold or self.similarity_threshold
        similar_conversations = []
        
        try:
            target_features = await self._extract_conversation_features(target_conversation)
            
            for conversation in comparison_set:
                if conversation.conversation_id == target_conversation.conversation_id:
                    continue
                
                comp_features = await self._extract_conversation_features(conversation)
                similarity_score = await self._calculate_conversation_similarity(
                    target_features, comp_features
                )
                
                if similarity_score >= threshold:
                    similar_conversations.append((conversation, similarity_score))
            
            similar_conversations.sort(key=lambda x: x[1], reverse=True)
            
            logger.info(f"Similarity detection: {len(similar_conversations)} matches found")
            return similar_conversations
            
        except Exception as e:
            logger.error(f"Similarity detection error: {str(e)}")
            return []

    async def _extract_conversation_features(self, conversation: ClubhouseConversation) -> Dict[str, Any]:
        """Extract features for similarity comparison"""
        features = {
            "topic": conversation.room.topic.lower(),
            "participant_count": conversation.participant_count,
            "duration": conversation.duration,
            "language": conversation.room.language,
            "topics": set(conversation.topics_discussed),
            "keywords": set(conversation.keywords),
            "has_club": conversation.room.club_id is not None,
            "is_social": conversation.room.is_social_mode,
            "hour_of_day": conversation.start_time.hour
        }
        return features

    async def _calculate_conversation_similarity(
        self,
        features1: Dict[str, Any],
        features2: Dict[str, Any]
    ) -> float:
        """Calculate similarity between conversation features"""
        try:
            scores = []
            
            # Topic similarity
            topic_sim = SequenceMatcher(
                None, features1.get("topic", ""), features2.get("topic", "")
            ).ratio()
            scores.append(topic_sim * 0.4)  # 40% weight
            
            # Topics overlap
            topics1 = features1.get("topics", set())
            topics2 = features2.get("topics", set())
            if topics1 and topics2:
                topic_overlap = len(topics1.intersection(topics2)) / len(topics1.union(topics2))
                scores.append(topic_overlap * 0.3)  # 30% weight
            
            # Keywords overlap
            keywords1 = features1.get("keywords", set())
            keywords2 = features2.get("keywords", set())
            if keywords1 and keywords2:
                keyword_overlap = len(keywords1.intersection(keywords2)) / len(keywords1.union(keywords2))
                scores.append(keyword_overlap * 0.2)  # 20% weight
            
            # Temporal similarity
            hour_diff = abs(features1.get("hour_of_day", 0) - features2.get("hour_of_day", 0))
            temporal_sim = max(0, 1 - hour_diff / 12)
            scores.append(temporal_sim * 0.1)  # 10% weight
            
            return sum(scores) / len(scores) if scores else 0.0
            
        except Exception as e:
            logger.error(f"Similarity calculation error: {str(e)}")
            return 0.0

    async def get_analytics(
        self,
        user_id: str,
        analysis_period: Tuple[datetime, datetime]
    ) -> ClubhouseAnalytics:
        """
        Generate comprehensive analytics for Clubhouse user
        
        Args:
            user_id: User ID to analyze
            analysis_period: Analysis time period
            
        Returns:
            ClubhouseAnalytics: Comprehensive analytics data
        """
        try:
            start_time, end_time = analysis_period
            
            # This would require extensive API calls to gather user activity
            # For now, return a basic analytics structure
            
            analytics = ClubhouseAnalytics(
                user_id=user_id,
                analysis_period=analysis_period,
                total_rooms_created=0,
                total_rooms_joined=0,
                speaking_time=0,
                listening_time=0,
                average_room_duration=0.0,
                most_active_topics=[],
                speaking_frequency=0.0,
                audience_growth=0,
                follower_conversion_rate=0.0,
                engagement_score=0.0,
                content_quality_score=0.0,
                network_influence=0.0,
                room_completion_rate=0.0,
                audio_quality_average=0.0,
                language_distribution={},
                toxicity_incidents=0,
                content_warnings_received=0,
                similarity_violations=0,
                protection_violations=0
            )
            
            logger.info(f"Analytics generated for user {user_id}")
            return analytics
            
        except Exception as e:
            logger.error(f"Analytics generation error: {str(e)}")
            return ClubhouseAnalytics(
                user_id=user_id,
                analysis_period=analysis_period,
                total_rooms_created=0,
                total_rooms_joined=0,
                speaking_time=0,
                listening_time=0,
                average_room_duration=0.0,
                most_active_topics=[],
                speaking_frequency=0.0,
                audience_growth=0,
                follower_conversion_rate=0.0,
                engagement_score=0.0,
                content_quality_score=0.0,
                network_influence=0.0,
                room_completion_rate=0.0,
                audio_quality_average=0.0,
                language_distribution={},
                toxicity_incidents=0,
                content_warnings_received=0,
                similarity_violations=0,
                protection_violations=0
            )

    async def _parse_room_data(self, data: Dict[str, Any]) -> ClubhouseRoom:
        """Parse room data from API response"""
        try:
            # Parse channel user
            channel_user_data = data.get("channel_user", {})
            channel_user = ClubhouseUser(
                user_id=channel_user_data.get("user_id", ""),
                username=channel_user_data.get("username", ""),
                name=channel_user_data.get("name", ""),
                bio=channel_user_data.get("bio"),
                photo_url=channel_user_data.get("photo_url"),
                followers_count=channel_user_data.get("num_followers", 0),
                following_count=channel_user_data.get("num_following", 0),
                time_created=datetime.utcnow(),
                is_speaker=channel_user_data.get("is_speaker", False),
                is_moderator=channel_user_data.get("is_moderator", False)
            )
            
            # Parse users in room
            users = []
            for user_data in data.get("users", []):
                user = ClubhouseUser(
                    user_id=user_data.get("user_id", ""),
                    username=user_data.get("username", ""),
                    name=user_data.get("name", ""),
                    bio=user_data.get("bio"),
                    photo_url=user_data.get("photo_url"),
                    followers_count=user_data.get("num_followers", 0),
                    following_count=user_data.get("num_following", 0),
                    time_created=datetime.utcnow(),
                    is_speaker=user_data.get("is_speaker", False),
                    is_moderator=user_data.get("is_moderator", False),
                    is_invited_speaker=user_data.get("is_invited_speaker", False),
                    is_followed_by_speaker=user_data.get("is_followed_by_speaker", False)
                )
                users.append(user)
            
            # Parse club data if available
            club = None
            club_data = data.get("club")
            if club_data:
                club = ClubhouseClub(
                    club_id=club_data.get("club_id", ""),
                    name=club_data.get("name", ""),
                    description=club_data.get("description"),
                    photo_url=club_data.get("photo_url"),
                    num_members=club_data.get("num_members", 0),
                    num_followers=club_data.get("num_followers", 0),
                    created_at=datetime.utcnow(),
                    updated_at=datetime.utcnow()
                )
            
            # Create room object
            room = ClubhouseRoom(
                channel=data.get("channel", ""),
                channel_user=channel_user,
                topic=data.get("topic", ""),
                is_private=data.get("is_private", False),
                is_social_mode=data.get("is_social_mode", False),
                url=data.get("url", ""),
                creation_datetime=datetime.fromisoformat(
                    data.get("creation_datetime", datetime.utcnow().isoformat())
                ),
                language=data.get("language", "en"),
                room_type=ClubhouseRoomType(data.get("room_type", "open")),
                status=ClubhouseRoomStatus.LIVE,
                num_other=data.get("num_other", 0),
                num_speakers=data.get("num_speakers", 0),
                num_all=data.get("num_all", 0),
                users=users,
                success=data.get("success", True),
                is_handraise_enabled=data.get("is_handraise_enabled", True),
                handraise_permission=data.get("handraise_permission", 1),
                club=club,
                club_id=data.get("club_id"),
                club_name=data.get("club_name"),
                club_topic=data.get("club_topic"),
                is_official=data.get("is_official", False)
            )
            
            return room
            
        except Exception as e:
            logger.error(f"Error parsing room data: {str(e)}")
            raise

    async def _parse_user_data(self, data: Dict[str, Any]) -> ClubhouseUser:
        """Parse user data from API response"""
        return ClubhouseUser(
            user_id=data.get("user_id", ""),
            username=data.get("username", ""),
            name=data.get("name", ""),
            bio=data.get("bio"),
            photo_url=data.get("photo_url"),
            followers_count=data.get("num_followers", 0),
            following_count=data.get("num_following", 0),
            invited_by_user_id=data.get("invited_by_user_id"),
            time_created=datetime.fromisoformat(
                data.get("time_created", datetime.utcnow().isoformat())
            ),
            url=data.get("url"),
            twitter=data.get("twitter"),
            instagram=data.get("instagram"),
            num_mutual_followers=data.get("num_mutual_followers", 0),
            is_blocked_by_network=data.get("is_blocked_by_network", False)
        )

    async def _parse_club_data(self, data: Dict[str, Any]) -> ClubhouseClub:
        """Parse club data from API response"""
        return ClubhouseClub(
            club_id=data.get("club_id", ""),
            name=data.get("name", ""),
            description=data.get("description"),
            photo_url=data.get("photo_url"),
            num_members=data.get("num_members", 0),
            num_followers=data.get("num_followers", 0),
            enable_private=data.get("enable_private", False),
            is_follow_allowed=data.get("is_follow_allowed", True),
            is_membership_private=data.get("is_membership_private", False),
            is_community=data.get("is_community", False),
            rules=data.get("rules", []),
            topics=data.get("topics", []),
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )

    async def _parse_event_data(self, data: Dict[str, Any]) -> ClubhouseEvent:
        """Parse event data from API response"""
        hosts = []
        for host_data in data.get("hosts", []):
            host = ClubhouseUser(
                user_id=host_data.get("user_id", ""),
                username=host_data.get("username", ""),
                name=host_data.get("name", ""),
                photo_url=host_data.get("photo_url"),
                time_created=datetime.utcnow(),
                followers_count=0,
                following_count=0
            )
            hosts.append(host)
        
        return ClubhouseEvent(
            event_id=data.get("event_id", ""),
            name=data.get("name", ""),
            description=data.get("description"),
            time_start=datetime.fromisoformat(
                data.get("time_start", datetime.utcnow().isoformat())
            ),
            hosts=hosts,
            is_member_only=data.get("is_member_only", False),
            url=data.get("url", ""),
            num_attending=data.get("num_attending", 0),
            is_attending=data.get("is_attending", False)
        )

    async def _calculate_similarity(self, conversation: ClubhouseConversation) -> float:
        """Calculate similarity score against protected content"""
        # Simplified similarity calculation
        return 0.0

    async def _check_protection_status(self, conversation: ClubhouseConversation) -> str:
        """Check protection status of conversation"""
        if conversation.content_warnings:
            return "flagged"
        return "unprotected"

    async def _handle_rate_limit(self, response: aiohttp.ClientResponse) -> bool:
        """Handle rate limiting responses"""
        if response.status == 429:
            retry_after = int(response.headers.get('Retry-After', 60))
            logger.warning(f"Rate limited. Waiting {retry_after} seconds")
            await asyncio.sleep(retry_after)
            return True
        return False

    async def close(self):
        """Close crawler and cleanup resources"""
        try:
            await self.cache_manager.close()
            await super().close()
            logger.info("Clubhouse crawler closed successfully")
        except Exception as e:
            logger.error(f"Error closing crawler: {str(e)}")
