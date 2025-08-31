"""
BeReal Platform Crawler - Ultra-Advanced Implementation
Authentic Photo Sharing Platform Content Monitoring System

This module provides comprehensive crawling capabilities for BeReal platform,
focusing on authentic moment sharing, content protection, and real-time monitoring.

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
from typing import Dict, List, Optional, Any, Set, Tuple
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


class BeRealContentType(str, Enum):
    """BeReal content types for classification"""
    BEREAL_POST = "bereal_post"
    LATE_BEREAL = "late_bereal"
    MEMORY = "memory"
    COMMENT = "comment"
    REACTION = "reaction"
    DISCOVERY_POST = "discovery_post"


class BeRealVisibility(str, Enum):
    """BeReal post visibility settings"""
    FRIENDS = "friends"
    FRIENDS_OF_FRIENDS = "friends_of_friends"
    DISCOVERY = "discovery"
    PRIVATE = "private"


class BeRealLocation(BaseModel):
    """BeReal location data model"""
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    city: Optional[str] = None
    country: Optional[str] = None
    region: Optional[str] = None
    is_precise: bool = False
    location_id: Optional[str] = None


class BeRealPhoto(BaseModel):
    """BeReal photo data model"""
    front_camera_url: str
    back_camera_url: str
    front_camera_width: int
    front_camera_height: int
    back_camera_width: int
    back_camera_height: int
    taken_at: datetime
    upload_timestamp: datetime
    is_late: bool = False
    late_duration: Optional[int] = None  # seconds late
    retakes_count: int = 0
    photo_hash: Optional[str] = None


class BeRealUser(BaseModel):
    """BeReal user data model"""
    user_id: str
    username: str
    display_name: str
    profile_picture_url: Optional[str] = None
    bio: Optional[str] = None
    followers_count: int = 0
    following_count: int = 0
    friends_count: int = 0
    is_verified: bool = False
    account_created: datetime
    location: Optional[BeRealLocation] = None
    streak_count: int = 0
    total_posts: int = 0
    is_private: bool = True


class BeRealReaction(BaseModel):
    """BeReal reaction data model"""
    reaction_id: str
    user: BeRealUser
    emoji: str
    created_at: datetime
    reaction_type: str  # emoji, realoji, instant


class BeRealComment(BaseModel):
    """BeReal comment data model"""
    comment_id: str
    user: BeRealUser
    content: str
    created_at: datetime
    is_edited: bool = False
    edited_at: Optional[datetime] = None
    mentions: List[str] = Field(default_factory=list)
    replies_count: int = 0


class BeRealContent(BaseModel):
    """Main BeReal content data model"""
    post_id: str
    user: BeRealUser
    content_type: BeRealContentType
    photos: BeRealPhoto
    caption: Optional[str] = None
    location: Optional[BeRealLocation] = None
    visibility: BeRealVisibility
    created_at: datetime
    moment_id: str  # Daily BeReal moment ID
    is_late: bool = False
    late_duration: Optional[int] = None
    reactions: List[BeRealReaction] = Field(default_factory=list)
    comments: List[BeRealComment] = Field(default_factory=list)
    reactions_count: int = 0
    comments_count: int = 0
    screenshot_count: int = 0
    is_discovery_featured: bool = False
    content_warnings: List[str] = Field(default_factory=list)
    similarity_score: Optional[float] = None
    protection_status: str = "unprotected"


class BeRealSearchResults(BaseModel):
    """BeReal search results data model"""
    query: str
    total_results: int
    results: List[BeRealContent]
    search_type: str
    filters_applied: Dict[str, Any]
    search_timestamp: datetime
    has_more: bool = False
    next_cursor: Optional[str] = None


class BeRealAnalytics(BaseModel):
    """BeReal analytics data model"""
    user_id: str
    analysis_period: Tuple[datetime, datetime]
    total_posts: int
    average_late_duration: float
    most_active_time: str
    friend_interactions: int
    discovery_features: int
    content_warnings_received: int
    engagement_rate: float
    authenticity_score: float
    location_diversity: int
    streak_consistency: float
    content_similarity_alerts: int
    protection_violations: int


class BeRealCrawler(BaseCrawler):
    """
    Ultra-Advanced BeReal Platform Crawler
    
    Provides comprehensive crawling and monitoring capabilities for BeReal platform,
    specializing in authentic moment capture, content protection, and real-time analytics.
    """
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        
        self.base_url = "https://mobile.bereal.com"
        self.api_base = "https://mobile.bereal.com/api"
        self.discovery_base = "https://discovery.bereal.com"
        
        # Authentication and session management
        self.session_token: Optional[str] = None
        self.refresh_token: Optional[str] = None
        self.device_id: str = self._generate_device_id()
        self.client_version = "1.11.3"
        
        # Rate limiting - BeReal has strict limits
        self.rate_limiter = RateLimiter(
            requests_per_minute=30,
            requests_per_hour=500,
            burst_limit=10
        )
        
        # Cache management
        self.cache_manager = CacheManager(
            cache_ttl=300,  # 5 minutes for real-time content
            max_cache_size=1000
        )
        
        # Content protection
        self.content_encryption = ContentEncryption()
        self.fingerprinter = ContentFingerprinter()
        
        # Monitoring sets
        self.monitored_users: Set[str] = set()
        self.protected_content: Set[str] = set()
        self.similarity_threshold = config.get('similarity_threshold', 0.85)
        
        # BeReal-specific settings
        self.monitor_late_posts = config.get('monitor_late_posts', True)
        self.track_authenticity = config.get('track_authenticity', True)
        self.enable_discovery_monitoring = config.get('enable_discovery_monitoring', True)
        
        logger.info("BeReal crawler initialized with ultra-advanced monitoring capabilities")

    def _generate_device_id(self) -> str:
        """Generate unique device identifier for BeReal API"""
        import uuid
        return str(uuid.uuid4()).upper()

    async def authenticate(self, phone_number: str, verification_code: Optional[str] = None) -> bool:
        """
        Authenticate with BeReal platform
        
        Args:
            phone_number: User's phone number for authentication
            verification_code: SMS verification code
            
        Returns:
            bool: Authentication success status
        """



        try:
            headers = {
                "User-Agent": f"BeReal/{self.client_version} (com.bereal.ft; build:99999; iOS 16.0.0)",
                "Content-Type": "application/json",
                "bereal-device-id": self.device_id,
                "bereal-timezone": "Europe/Paris"
            }
            
            # Step 1: Request verification code
            if not verification_code:
                auth_data = {
                    "phoneNumber": phone_number,
                    "deviceId": self.device_id
                }
                
                async with self.session.post(
                    f"{self.api_base}/login/send-sms",
                    json=auth_data,
                    headers=headers
                ) as response:
                    if response.status == 200:
                        logger.info("Verification code sent successfully")
                        return False  # Need verification code
                    else:
                        logger.error(f"Failed to send verification code: {response.status}")
                        return False
            
            # Step 2: Verify code and get tokens
            else:
                verify_data = {
                    "phoneNumber": phone_number,
                    "otpCode": verification_code,
                    "deviceId": self.device_id
                }
                
                async with self.session.post(
                    f"{self.api_base}/login/verify",
                    json=verify_data,
                    headers=headers
                ) as response:
                    if response.status == 200:
                        auth_response = await response.json()
                        self.session_token = auth_response.get("token")
                        self.refresh_token = auth_response.get("refreshToken")
                        
                        # Update session headers
                        self.session.headers.update({
                            "authorization": f"Bearer {self.session_token}",
                            "bereal-device-id": self.device_id
                        })
                        
                        logger.info("BeReal authentication successful")
                        return True
                    else:
                        logger.error(f"Authentication failed: {response.status}")
                        return False
                        
        except Exception as e:
            logger.error(f"Authentication error: {str(e)}")
            return False

    async def _refresh_session(self) -> bool:
        """Refresh authentication session"""
        if not self.refresh_token:
            return False
            
        try:
            refresh_data = {
                "refreshToken": self.refresh_token,
                "deviceId": self.device_id
            }
            
            async with self.session.post(
                f"{self.api_base}/login/refresh",
                json=refresh_data
            ) as response:
                if response.status == 200:
                    auth_response = await response.json()
                    self.session_token = auth_response.get("token")
                    self.session.headers.update({
                        "authorization": f"Bearer {self.session_token}"
                    })
                    return True
                return False
                
        except Exception as e:
            logger.error(f"Session refresh error: {str(e)}")
            return False

    async def search_content(
        self,
        query: str = "",
        content_type: Optional[BeRealContentType] = None,
        location: Optional[BeRealLocation] = None,
        time_range: Optional[Tuple[datetime, datetime]] = None,
        limit: int = 50
    ) -> BeRealSearchResults:
        """
        Search BeReal content with advanced filtering
        
        Args:
            query: Search query (username, location, etc.)
            content_type: Type of content to search
            location: Geographic location filter
            time_range: Time range for content
            limit: Maximum results to return
            
        Returns:
            BeRealSearchResults: Comprehensive search results
        """
        await self.rate_limiter.acquire()
        
        try:
            # Check cache first
            cache_key = f"search_{hashlib.md5(f'{query}_{content_type}_{limit}'.encode()).hexdigest()}"
            cached_result = await self.cache_manager.get(cache_key)
            if cached_result:
                return BeRealSearchResults(**cached_result)
            
            results = []
            search_type = "general"
            
            # Search in discovery feed if enabled
            if self.enable_discovery_monitoring:
                discovery_results = await self._search_discovery(query, limit // 2)
                results.extend(discovery_results)
                search_type = "discovery"
            
            # Search user's friend feed
            if self.session_token:
                friends_results = await self._search_friends_feed(query, limit // 2)
                results.extend(friends_results)
                search_type = "friends" if not results else "combined"
            
            # Apply filters
            if content_type:
                results = [r for r in results if r.content_type == content_type]
            
            if time_range:
                start_time, end_time = time_range
                results = [r for r in results if start_time <= r.created_at <= end_time]
            
            if location:
                results = await self._filter_by_location(results, location)
            
            # Process content for protection
            for result in results:
                result.similarity_score = await self._calculate_similarity(result)
                result.protection_status = await self._check_protection_status(result)
            
            search_results = BeRealSearchResults(
                query=query,
                total_results=len(results),
                results=results[:limit],
                search_type=search_type,
                filters_applied={
                    "content_type": content_type.value if content_type else None,
                    "location": location.dict() if location else None,
                    "time_range": [t.isoformat() for t in time_range] if time_range else None
                },
                search_timestamp=datetime.utcnow(),
                has_more=len(results) > limit
            )
            
            # Cache results
            await self.cache_manager.set(cache_key, search_results.dict())
            
            logger.info(f"BeReal search completed: {len(results)} results for query '{query}'")
            return search_results
            
        except Exception as e:
            logger.error(f"Search error: {str(e)}")
            return BeRealSearchResults(
                query=query,
                total_results=0,
                results=[],
                search_type="error",
                filters_applied={},
                search_timestamp=datetime.utcnow()
            )

    async def _search_discovery(self, query: str, limit: int) -> List[BeRealContent]:
        """Search BeReal discovery feed"""



        try:
            params = {
                "limit": limit,
                "offset": 0
            }
            
            async with self.session.get(
                f"{self.discovery_base}/feed",
                params=params
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    return await self._parse_discovery_feed(data.get("posts", []))
                return []
                
        except Exception as e:
            logger.error(f"Discovery search error: {str(e)}")
            return []

    async def _search_friends_feed(self, query: str, limit: int) -> List[BeRealContent]:
        """Search user's friends feed"""



        try:
            params = {
                "limit": limit,
                "offset": 0
            }
            
            async with self.session.get(
                f"{self.api_base}/feeds/friends",
                params=params
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    return await self._parse_friends_feed(data.get("posts", []))
                return []
                
        except Exception as e:
            logger.error(f"Friends feed search error: {str(e)}")
            return []

    async def get_content_details(self, content_id: str) -> Optional[BeRealContent]:
        """
        Get detailed information about specific BeReal content
        
        Args:
            content_id: BeReal post ID
            
        Returns:
            Optional[BeRealContent]: Detailed content information
        """
        await self.rate_limiter.acquire()
        
        try:
            # Check cache first
            cache_key = f"content_{content_id}"
            cached_content = await self.cache_manager.get(cache_key)
            if cached_content:
                return BeRealContent(**cached_content)
            
            async with self.session.get(
                f"{self.api_base}/content/posts/{content_id}"
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    content = await self._parse_post_data(data)
                    
                    # Enhanced content analysis
                    content.similarity_score = await self._calculate_similarity(content)
                    content.protection_status = await self._check_protection_status(content)
                    
                    # Cache the result
                    await self.cache_manager.set(cache_key, content.dict())
                    
                    logger.info(f"Retrieved BeReal content details: {content_id}")
                    return content
                else:
                    logger.warning(f"Content not found: {content_id}")
                    return None
                    
        except Exception as e:
            logger.error(f"Error getting content details: {str(e)}")
            return None

    async def monitor_content(
        self,
        user_ids: List[str],
        keywords: List[str] = None,
        check_interval: int = 300  # 5 minutes
    ) -> AsyncGenerator[BeRealContent, None]:
        """
        Real-time content monitoring for BeReal
        
        Args:
            user_ids: List of user IDs to monitor
            keywords: Keywords to monitor in captions
            check_interval: Check interval in seconds
            
        Yields:
            BeRealContent: New content detected
        """
        self.monitored_users.update(user_ids)
        keywords = keywords or []
        
        logger.info(f"Starting BeReal monitoring for {len(user_ids)} users")
        
        last_check = datetime.utcnow()
        seen_posts = set()
        
        while True:
            try:
                await asyncio.sleep(check_interval)
                
                # Monitor friends feed for new content
                if self.session_token:
                    new_content = await self._check_friends_feed_updates(last_check)
                    
                    for content in new_content:
                        if content.post_id not in seen_posts:
                            # Apply monitoring filters
                            if (content.user.user_id in self.monitored_users or
                                any(keyword.lower() in (content.caption or "").lower() 
                                    for keyword in keywords)):
                                
                                # Enhanced monitoring analysis
                                content.similarity_score = await self._calculate_similarity(content)
                                content.protection_status = await self._check_protection_status(content)
                                
                                seen_posts.add(content.post_id)
                                
                                logger.info(f"New BeReal content detected: {content.post_id}")
                                yield content
                
                # Monitor discovery feed if enabled
                if self.enable_discovery_monitoring:
                    discovery_content = await self._check_discovery_updates(last_check)
                    
                    for content in discovery_content:
                        if content.post_id not in seen_posts:
                            if any(keyword.lower() in (content.caption or "").lower() 
                                   for keyword in keywords):
                                
                                content.similarity_score = await self._calculate_similarity(content)
                                content.protection_status = await self._check_protection_status(content)
                                
                                seen_posts.add(content.post_id)
                                yield content
                
                last_check = datetime.utcnow()
                
            except Exception as e:
                logger.error(f"Monitoring error: {str(e)}")
                await asyncio.sleep(60)  # Wait before retrying

    async def detect_similarity(
        self,
        target_content: BeRealContent,
        comparison_set: List[BeRealContent],
        threshold: float = None
    ) -> List[Tuple[BeRealContent, float]]:
        """
        Detect content similarity using advanced algorithms
        
        Args:
            target_content: Content to compare against
            comparison_set: Set of content to compare with
            threshold: Similarity threshold (0.0-1.0)
            
        Returns:
            List[Tuple[BeRealContent, float]]: Similar content with scores
        """
        threshold = threshold or self.similarity_threshold
        similar_content = []
        
        try:
            # Extract target features
            target_features = await self._extract_content_features(target_content)
            
            for content in comparison_set:
                if content.post_id == target_content.post_id:
                    continue
                
                # Extract comparison features
                comp_features = await self._extract_content_features(content)
                
                # Calculate similarity score
                similarity_score = await self._calculate_content_similarity(
                    target_features, comp_features
                )
                
                if similarity_score >= threshold:
                    similar_content.append((content, similarity_score))
            
            # Sort by similarity score (highest first)
            similar_content.sort(key=lambda x: x[1], reverse=True)
            
            logger.info(f"Similarity detection: {len(similar_content)} matches found")
            return similar_content
            
        except Exception as e:
            logger.error(f"Similarity detection error: {str(e)}")
            return []

    async def get_analytics(
        self,
        user_id: str,
        analysis_period: Tuple[datetime, datetime]
    ) -> BeRealAnalytics:
        """
        Generate comprehensive analytics for BeReal user
        
        Args:
            user_id: User ID to analyze
            analysis_period: Time period for analysis
            
        Returns:
            BeRealAnalytics: Comprehensive analytics data
        """



        try:
            start_time, end_time = analysis_period
            
            # Gather user's content in the period
            user_content = await self._get_user_content_in_period(user_id, start_time, end_time)
            
            if not user_content:
                return BeRealAnalytics(
                    user_id=user_id,
                    analysis_period=analysis_period,
                    total_posts=0,
                    average_late_duration=0.0,
                    most_active_time="N/A",
                    friend_interactions=0,
                    discovery_features=0,
                    content_warnings_received=0,
                    engagement_rate=0.0,
                    authenticity_score=0.0,
                    location_diversity=0,
                    streak_consistency=0.0,
                    content_similarity_alerts=0,
                    protection_violations=0
                )
            
            # Calculate analytics metrics
            total_posts = len(user_content)
            late_posts = [c for c in user_content if c.is_late]
            average_late_duration = sum(c.late_duration or 0 for c in late_posts) / len(late_posts) if late_posts else 0.0
            
            # Activity analysis
            post_hours = [c.created_at.hour for c in user_content]
            most_active_time = max(set(post_hours), key=post_hours.count) if post_hours else 0
            
            # Engagement metrics
            total_reactions = sum(c.reactions_count for c in user_content)
            total_comments = sum(c.comments_count for c in user_content)
            friend_interactions = total_reactions + total_comments
            
            engagement_rate = friend_interactions / total_posts if total_posts > 0 else 0.0
            
            # Discovery features
            discovery_features = sum(1 for c in user_content if c.is_discovery_featured)
            
            # Content warnings
            content_warnings_received = sum(len(c.content_warnings) for c in user_content)
            
            # Authenticity score (based on late posts and retakes)
            on_time_posts = total_posts - len(late_posts)
            authenticity_score = (on_time_posts / total_posts) if total_posts > 0 else 1.0
            
            # Location diversity
            unique_locations = set()
            for content in user_content:
                if content.location and content.location.city:
                    unique_locations.add(content.location.city)
            location_diversity = len(unique_locations)
            
            # Streak consistency (simplified calculation)
            days_in_period = (end_time - start_time).days
            posting_days = set(c.created_at.date() for c in user_content)
            streak_consistency = len(posting_days) / days_in_period if days_in_period > 0 else 0.0
            
            # Content protection metrics
            similarity_alerts = sum(1 for c in user_content if (c.similarity_score or 0) > self.similarity_threshold)
            protection_violations = sum(1 for c in user_content if c.protection_status == "violation")
            
            analytics = BeRealAnalytics(
                user_id=user_id,
                analysis_period=analysis_period,
                total_posts=total_posts,
                average_late_duration=average_late_duration,
                most_active_time=f"{most_active_time:02d}:00",
                friend_interactions=friend_interactions,
                discovery_features=discovery_features,
                content_warnings_received=content_warnings_received,
                engagement_rate=engagement_rate,
                authenticity_score=authenticity_score,
                location_diversity=location_diversity,
                streak_consistency=streak_consistency,
                content_similarity_alerts=similarity_alerts,
                protection_violations=protection_violations
            )
            
            logger.info(f"Analytics generated for user {user_id}: {total_posts} posts analyzed")
            return analytics
            
        except Exception as e:
            logger.error(f"Analytics generation error: {str(e)}")
            return BeRealAnalytics(
                user_id=user_id,
                analysis_period=analysis_period,
                total_posts=0,
                average_late_duration=0.0,
                most_active_time="N/A",
                friend_interactions=0,
                discovery_features=0,
                content_warnings_received=0,
                engagement_rate=0.0,
                authenticity_score=0.0,
                location_diversity=0,
                streak_consistency=0.0,
                content_similarity_alerts=0,
                protection_violations=0
            )

    async def _parse_post_data(self, data: Dict[str, Any]) -> BeRealContent:
        """Parse BeReal post data into structured format"""



        try:
            # Parse user data
            user_data = data.get("user", {})
            user = BeRealUser(
                user_id=user_data.get("id", ""),
                username=user_data.get("username", ""),
                display_name=user_data.get("fullname", ""),
                profile_picture_url=user_data.get("profilePicture", {}).get("url"),
                bio=user_data.get("biography", ""),
                followers_count=user_data.get("followersCount", 0),
                following_count=user_data.get("followingCount", 0),
                friends_count=user_data.get("friendsCount", 0),
                is_verified=user_data.get("isVerified", False),
                account_created=datetime.fromisoformat(user_data.get("createdAt", datetime.utcnow().isoformat())),
                streak_count=user_data.get("streakLength", 0),
                total_posts=user_data.get("postsCount", 0),
                is_private=user_data.get("isPrivate", True)
            )
            
            # Parse location data
            location_data = data.get("location", {})
            location = None
            if location_data:
                location = BeRealLocation(
                    latitude=location_data.get("latitude"),
                    longitude=location_data.get("longitude"),
                    city=location_data.get("city"),
                    country=location_data.get("country"),
                    region=location_data.get("region"),
                    is_precise=location_data.get("isPrecise", False),
                    location_id=location_data.get("id")
                )
            
            # Parse photo data
            photos_data = data.get("photoURL", {})
            photos = BeRealPhoto(
                front_camera_url=photos_data.get("primary", ""),
                back_camera_url=photos_data.get("secondary", ""),
                front_camera_width=photos_data.get("primaryWidth", 0),
                front_camera_height=photos_data.get("primaryHeight", 0),
                back_camera_width=photos_data.get("secondaryWidth", 0),
                back_camera_height=photos_data.get("secondaryHeight", 0),
                taken_at=datetime.fromisoformat(data.get("takenAt", datetime.utcnow().isoformat())),
                upload_timestamp=datetime.fromisoformat(data.get("createdAt", datetime.utcnow().isoformat())),
                is_late=data.get("isLate", False),
                late_duration=data.get("lateInSeconds"),
                retakes_count=data.get("retakeCounter", 0)
            )
            
            # Parse reactions
            reactions = []
            for reaction_data in data.get("realmojis", []):
                reaction_user_data = reaction_data.get("user", {})
                reaction_user = BeRealUser(
                    user_id=reaction_user_data.get("id", ""),
                    username=reaction_user_data.get("username", ""),
                    display_name=reaction_user_data.get("fullname", ""),
                    profile_picture_url=reaction_user_data.get("profilePicture", {}).get("url"),
                    account_created=datetime.utcnow(),
                    is_private=True
                )
                
                reaction = BeRealReaction(
                    reaction_id=reaction_data.get("id", ""),
                    user=reaction_user,
                    emoji=reaction_data.get("emoji", ""),
                    created_at=datetime.fromisoformat(reaction_data.get("postedAt", datetime.utcnow().isoformat())),
                    reaction_type=reaction_data.get("type", "emoji")
                )
                reactions.append(reaction)
            
            # Parse comments
            comments = []
            for comment_data in data.get("comments", []):
                comment_user_data = comment_data.get("user", {})
                comment_user = BeRealUser(
                    user_id=comment_user_data.get("id", ""),
                    username=comment_user_data.get("username", ""),
                    display_name=comment_user_data.get("fullname", ""),
                    profile_picture_url=comment_user_data.get("profilePicture", {}).get("url"),
                    account_created=datetime.utcnow(),
                    is_private=True
                )
                
                comment = BeRealComment(
                    comment_id=comment_data.get("id", ""),
                    user=comment_user,
                    content=comment_data.get("content", ""),
                    created_at=datetime.fromisoformat(comment_data.get("postedAt", datetime.utcnow().isoformat())),
                    mentions=comment_data.get("mentions", [])
                )
                comments.append(comment)
            
            # Create main content object
            content = BeRealContent(
                post_id=data.get("id", ""),
                user=user,
                content_type=BeRealContentType.BEREAL_POST,
                photos=photos,
                caption=data.get("caption"),
                location=location,
                visibility=BeRealVisibility(data.get("visibility", "friends")),
                created_at=datetime.fromisoformat(data.get("createdAt", datetime.utcnow().isoformat())),
                moment_id=data.get("momentId", ""),
                is_late=data.get("isLate", False),
                late_duration=data.get("lateInSeconds"),
                reactions=reactions,
                comments=comments,
                reactions_count=len(reactions),
                comments_count=len(comments),
                screenshot_count=data.get("screenshotCount", 0),
                is_discovery_featured=data.get("isPublic", False)
            )
            
            return content
            
        except Exception as e:
            logger.error(f"Error parsing post data: {str(e)}")
            raise

    async def _extract_content_features(self, content: BeRealContent) -> Dict[str, Any]:
        """Extract features for similarity comparison"""
        features = {
            "caption": content.caption or "",
            "location_city": content.location.city if content.location else "",
            "user_id": content.user.user_id,
            "is_late": content.is_late,
            "late_duration": content.late_duration or 0,
            "moment_id": content.moment_id,
            "timestamp_hour": content.created_at.hour
        }
        
        # Photo similarity features
        if content.photos:
            features["front_aspect_ratio"] = content.photos.front_camera_width / max(content.photos.front_camera_height, 1)
            features["back_aspect_ratio"] = content.photos.back_camera_width / max(content.photos.back_camera_height, 1)
            features["retakes_count"] = content.photos.retakes_count
        
        return features

    async def _calculate_content_similarity(
        self,
        features1: Dict[str, Any],
        features2: Dict[str, Any]
    ) -> float:
        """Calculate similarity score between two content features"""



        try:
            scores = []
            
            # Caption similarity
            caption_sim = SequenceMatcher(
                None,
                features1.get("caption", "").lower(),
                features2.get("caption", "").lower()
            ).ratio()
            scores.append(caption_sim * 0.3)  # 30% weight
            
            # Location similarity
            if features1.get("location_city") and features2.get("location_city"):
                location_sim = 1.0 if features1["location_city"] == features2["location_city"] else 0.0
                scores.append(location_sim * 0.2)  # 20% weight
            
            # Temporal similarity
            hour_diff = abs(features1.get("timestamp_hour", 0) - features2.get("timestamp_hour", 0))
            temporal_sim = max(0, 1 - hour_diff / 12)  # Normalize to 12-hour difference
            scores.append(temporal_sim * 0.15)  # 15% weight
            
            # Behavioral similarity
            late_sim = 1.0 if features1.get("is_late") == features2.get("is_late") else 0.0
            scores.append(late_sim * 0.1)  # 10% weight
            
            # Photo composition similarity
            aspect_diff1 = abs(features1.get("front_aspect_ratio", 1) - features2.get("front_aspect_ratio", 1))
            aspect_diff2 = abs(features1.get("back_aspect_ratio", 1) - features2.get("back_aspect_ratio", 1))
            photo_sim = max(0, 1 - (aspect_diff1 + aspect_diff2) / 2)
            scores.append(photo_sim * 0.25)  # 25% weight
            
            return sum(scores)
            
        except Exception as e:
            logger.error(f"Similarity calculation error: {str(e)}")
            return 0.0

    async def _calculate_similarity(self, content: BeRealContent) -> float:
        """Calculate similarity score against protected content"""
        if not self.protected_content:
            return 0.0
        
        try:
            # Get protected content for comparison
            protected_items = await self._get_protected_content()
            
            max_similarity = 0.0
            for protected_item in protected_items:
                features1 = await self._extract_content_features(content)
                features2 = await self._extract_content_features(protected_item)
                
                similarity = await self._calculate_content_similarity(features1, features2)
                max_similarity = max(max_similarity, similarity)
            
            return max_similarity
            
        except Exception as e:
            logger.error(f"Similarity calculation error: {str(e)}")
            return 0.0

    async def _check_protection_status(self, content: BeRealContent) -> str:
        """Check if content violates protection policies"""



        try:
            if content.post_id in self.protected_content:
                return "protected"
            
            if (content.similarity_score or 0) > self.similarity_threshold:
                return "violation"
            
            if content.content_warnings:
                return "flagged"
            
            return "unprotected"
            
        except Exception as e:
            logger.error(f"Protection status check error: {str(e)}")
            return "unknown"

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
            logger.info("BeReal crawler closed successfully")
        except Exception as e:
            logger.error(f"Error closing crawler: {str(e)}")
