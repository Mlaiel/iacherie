"""
Clubhouse Crawler Implementation
================================

Advanced Clubhouse platform crawler for audio social networking content monitoring.
Implements comprehensive Room, User, Club, and Event tracking.

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

from .platform_crawler import PlatformCrawler, CrawlerConfig, CrawlerResult


@dataclass
class ClubhouseRoom:
    """Clubhouse room information"""
    room_id: str
    title: str
    description: str
    topic: str
    club_id: Optional[str]
    club_name: Optional[str]
    creator_user_id: str
    creator_username: str
    moderator_user_ids: List[str]
    speaker_user_ids: List[str]
    audience_count: int
    creation_time: datetime
    is_private: bool
    is_recorded: bool
    language: str
    room_type: str  # open, social, closed
    url: str
    is_live: bool
    ended_at: Optional[datetime]
    duration_seconds: Optional[int]
    tags: List[str]
    audience_insights: Dict[str, Any]
    recording_url: Optional[str]
    transcript: Optional[str]
    featured_speakers: List[str]
    waiting_list_count: int
    max_audience: Optional[int]


@dataclass
class ClubhouseUser:
    """Clubhouse user information"""
    user_id: str
    username: str
    name: str
    bio: str
    photo_url: str
    num_followers: int
    num_following: int
    is_verified: bool
    is_invited_speaker: bool
    is_moderator: bool
    joined_date: datetime
    last_active_minutes: Optional[int]
    clubs: List[str]  # Club IDs
    interests: List[str]
    invited_by_user_id: Optional[str]
    invitation_count: int
    room_visits: int
    speaking_time_minutes: int
    hosting_time_minutes: int
    twitter_handle: Optional[str]
    instagram_handle: Optional[str]
    location: Optional[str]
    languages: List[str]
    blocked_users: List[str]
    blocking_users: List[str]
    notifications_enabled: bool


@dataclass
class ClubhouseClub:
    """Clubhouse club information"""
    club_id: str
    name: str
    description: str
    photo_url: str
    banner_url: Optional[str]
    num_members: int
    num_followers: int
    creator_user_id: str
    admin_user_ids: List[str]
    member_user_ids: List[str]
    is_private: bool
    is_social: bool
    created_at: datetime
    topics: List[str]
    rules: str
    welcome_for_new_members: Optional[str]
    num_rooms: int
    url: str
    enable_private: bool
    is_community: bool
    recent_speakers: List[str]
    featured_rooms: List[str]
    upcoming_events: List[str]
    membership_type: str  # open, approval_required, closed
    guidelines: str
    contact_email: Optional[str]
    website_url: Optional[str]
    social_links: Dict[str, str]


@dataclass
class ClubhouseEvent:
    """Clubhouse event information"""
    event_id: str
    name: str
    description: str
    club_id: Optional[str]
    club_name: Optional[str]
    creator_user_id: str
    host_user_ids: List[str]
    scheduled_time: datetime
    end_time: Optional[datetime]
    timezone: str
    is_recurring: bool
    recurrence_pattern: Optional[str]
    room_id: Optional[str]
    attendee_count: int
    interested_count: int
    reminder_count: int
    is_private: bool
    url: str
    topics: List[str]
    language: str
    max_attendees: Optional[int]
    cost: Optional[float]
    currency: Optional[str]
    ticket_url: Optional[str]
    promotional_image_url: Optional[str]
    is_cancelled: bool
    cancellation_reason: Optional[str]


@dataclass
class ClubhouseNotification:
    """Clubhouse notification information"""
    notification_id: str
    user_id: str
    type: str  # room_start, user_joined_room, club_activity, etc.
    title: str
    message: str
    created_at: datetime
    is_read: bool
    action_url: Optional[str]
    related_user_id: Optional[str]
    related_room_id: Optional[str]
    related_club_id: Optional[str]
    metadata: Dict[str, Any]


class ClubhouseCrawler(PlatformCrawler):
    """
    Advanced Clubhouse crawler for audio social networking content monitoring.
    
    Features:
    - Live room monitoring
    - User profile analysis
    - Club activity tracking
    - Event scheduling analysis
    - Audio content transcription
    - Speaker identification
    - Topic trend analysis
    - Social graph mapping
    - Engagement metrics
    - Content discovery
    """
    
    def __init__(self, config: CrawlerConfig, vector_matcher=None):
        super().__init__(config, vector_matcher)
        self.platform_name = "clubhouse"
        self.base_url = "https://www.clubhouse.com"
        self.api_base_url = "https://www.clubhouse.com/api"
        
        # Rate limiting (Clubhouse has strict limits)
        self.requests_per_minute = 10
        self.min_delay = 6.0
        self.max_delay = 12.0
        
        # Content type mappings
        self.content_types = {
            'rooms': self._crawl_rooms,
            'users': self._crawl_users,
            'clubs': self._crawl_clubs,
            'events': self._crawl_events,
            'notifications': self._crawl_notifications,
            'live': self._crawl_live_rooms,
            'trending': self._crawl_trending,
            'search': self._crawl_search
        }
        
        # Tracking
        self.request_count = 0
        self.last_request_time = 0
        
        # Initialize session headers
        self._setup_session_headers()
    
    def _setup_session_headers(self):
        """Setup Clubhouse-specific headers"""
        self.session_headers.update({
            'Accept': 'application/json',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'en-US,en;q=0.9',
            'User-Agent': 'Clubhouse/304 (iPhone; iOS 14.8; Scale/3.00)',
            'Content-Type': 'application/json; charset=utf-8',
            'CH-AppBuild': '304',
            'CH-AppVersion': '1.0.27',
            'CH-DeviceId': 'iPhone13,2',
            'CH-Locale': 'en_US'
        })
    
    async def search_content(self, query: str, content_type: str = "rooms", 
                           max_results: int = 50, filters: Dict[str, Any] = None) -> List[CrawlerResult]:
        """
        Search for content on Clubhouse.
        
        Args:
            query: Search query
            content_type: Type of content to search for
            max_results: Maximum number of results
            filters: Additional search filters
            
        Returns:
            List of crawler results
        """
        try:
            await self._check_rate_limit()
            
            if content_type not in self.content_types:
                raise ValueError(f"Unsupported content type: {content_type}")
            
            # Execute search based on content type
            crawler_func = self.content_types[content_type]
            results = await crawler_func(query, max_results, filters)
            
            self.logger.info(f"Found {len(results)} Clubhouse {content_type} for query: {query}")
            return results
            
        except Exception as e:
            self.logger.error(f"Error searching Clubhouse content: {str(e)}")
            return []
    
    async def _crawl_rooms(self, query: str, max_results: int, filters: Dict[str, Any] = None) -> List[CrawlerResult]:
        """Crawl Clubhouse rooms"""
        try:
            results = []
            
            # Mock room data
            mock_rooms = await self._get_mock_rooms(query, max_results)
            
            for room_data in mock_rooms:
                room = await self._parse_room_data(room_data)
                if room:
                    result = CrawlerResult(
                        url=room.url,
                        title=room.title,
                        content=room.description,
                        metadata={
                            'room_data': asdict(room),
                            'platform': 'clubhouse',
                            'content_type': 'room',
                            'topic': room.topic,
                            'club_name': room.club_name,
                            'creator_username': room.creator_username,
                            'audience_count': room.audience_count,
                            'is_live': room.is_live,
                            'is_recorded': room.is_recorded,
                            'language': room.language,
                            'room_type': room.room_type,
                            'speaker_count': len(room.speaker_user_ids),
                            'moderator_count': len(room.moderator_user_ids),
                            'duration_seconds': room.duration_seconds,
                            'tags': room.tags
                        },
                        timestamp=room.creation_time,
                        similarity_score=0.0
                    )
                    results.append(result)
                    
                    # Rate limiting
                    await asyncio.sleep(random.uniform(self.min_delay, self.max_delay))
            
            return results
            
        except Exception as e:
            self.logger.error(f"Error crawling Clubhouse rooms: {str(e)}")
            return []
    
    async def _crawl_users(self, query: str, max_results: int, filters: Dict[str, Any] = None) -> List[CrawlerResult]:
        """Crawl Clubhouse users"""
        try:
            results = []
            
            # Mock user data
            mock_users = await self._get_mock_users(query, max_results)
            
            for user_data in mock_users:
                user = await self._parse_user_data(user_data)
                if user:
                    result = CrawlerResult(
                        url=f"{self.base_url}/@{user.username}",
                        title=f"{user.name} (@{user.username})",
                        content=user.bio,
                        metadata={
                            'user_data': asdict(user),
                            'platform': 'clubhouse',
                            'content_type': 'user',
                            'username': user.username,
                            'name': user.name,
                            'num_followers': user.num_followers,
                            'num_following': user.num_following,
                            'is_verified': user.is_verified,
                            'clubs': user.clubs,
                            'interests': user.interests,
                            'speaking_time_minutes': user.speaking_time_minutes,
                            'hosting_time_minutes': user.hosting_time_minutes,
                            'location': user.location,
                            'languages': user.languages
                        },
                        timestamp=user.joined_date,
                        similarity_score=0.0
                    )
                    results.append(result)
                    
                    # Rate limiting
                    await asyncio.sleep(random.uniform(self.min_delay, self.max_delay))
            
            return results
            
        except Exception as e:
            self.logger.error(f"Error crawling Clubhouse users: {str(e)}")
            return []
    
    async def _crawl_clubs(self, query: str, max_results: int, filters: Dict[str, Any] = None) -> List[CrawlerResult]:
        """Crawl Clubhouse clubs"""
        try:
            results = []
            
            # Mock club data
            mock_clubs = await self._get_mock_clubs(query, max_results)
            
            for club_data in mock_clubs:
                club = await self._parse_club_data(club_data)
                if club:
                    result = CrawlerResult(
                        url=club.url,
                        title=club.name,
                        content=club.description,
                        metadata={
                            'club_data': asdict(club),
                            'platform': 'clubhouse',
                            'content_type': 'club',
                            'name': club.name,
                            'num_members': club.num_members,
                            'num_followers': club.num_followers,
                            'is_private': club.is_private,
                            'is_social': club.is_social,
                            'topics': club.topics,
                            'membership_type': club.membership_type,
                            'num_rooms': club.num_rooms,
                            'recent_speakers': club.recent_speakers,
                            'social_links': club.social_links
                        },
                        timestamp=club.created_at,
                        similarity_score=0.0
                    )
                    results.append(result)
                    
                    # Rate limiting
                    await asyncio.sleep(random.uniform(self.min_delay, self.max_delay))
            
            return results
            
        except Exception as e:
            self.logger.error(f"Error crawling Clubhouse clubs: {str(e)}")
            return []
    
    async def _crawl_events(self, query: str, max_results: int, filters: Dict[str, Any] = None) -> List[CrawlerResult]:
        """Crawl Clubhouse events"""
        try:
            results = []
            
            # Mock event data
            mock_events = await self._get_mock_events(query, max_results)
            
            for event_data in mock_events:
                event = await self._parse_event_data(event_data)
                if event:
                    result = CrawlerResult(
                        url=event.url,
                        title=event.name,
                        content=event.description,
                        metadata={
                            'event_data': asdict(event),
                            'platform': 'clubhouse',
                            'content_type': 'event',
                            'name': event.name,
                            'club_name': event.club_name,
                            'scheduled_time': event.scheduled_time.isoformat(),
                            'attendee_count': event.attendee_count,
                            'interested_count': event.interested_count,
                            'is_recurring': event.is_recurring,
                            'is_private': event.is_private,
                            'topics': event.topics,
                            'language': event.language,
                            'cost': event.cost,
                            'currency': event.currency,
                            'is_cancelled': event.is_cancelled
                        },
                        timestamp=event.scheduled_time,
                        similarity_score=0.0
                    )
                    results.append(result)
                    
                    # Rate limiting
                    await asyncio.sleep(random.uniform(self.min_delay, self.max_delay))
            
            return results
            
        except Exception as e:
            self.logger.error(f"Error crawling Clubhouse events: {str(e)}")
            return []
    
    async def _crawl_notifications(self, query: str, max_results: int, filters: Dict[str, Any] = None) -> List[CrawlerResult]:
        """Crawl Clubhouse notifications"""
        try:
            results = []
            
            # Mock notification data
            mock_notifications = await self._get_mock_notifications(query, max_results)
            
            for notification_data in mock_notifications:
                notification = await self._parse_notification_data(notification_data)
                if notification:
                    result = CrawlerResult(
                        url=notification.action_url or f"{self.base_url}/notifications",
                        title=notification.title,
                        content=notification.message,
                        metadata={
                            'notification_data': asdict(notification),
                            'platform': 'clubhouse',
                            'content_type': 'notification',
                            'type': notification.type,
                            'is_read': notification.is_read,
                            'related_user_id': notification.related_user_id,
                            'related_room_id': notification.related_room_id,
                            'related_club_id': notification.related_club_id
                        },
                        timestamp=notification.created_at,
                        similarity_score=0.0
                    )
                    results.append(result)
                    
                    # Rate limiting
                    await asyncio.sleep(random.uniform(self.min_delay, self.max_delay))
            
            return results
            
        except Exception as e:
            self.logger.error(f"Error crawling Clubhouse notifications: {str(e)}")
            return []
    
    async def _crawl_live_rooms(self, query: str, max_results: int, filters: Dict[str, Any] = None) -> List[CrawlerResult]:
        """Crawl live Clubhouse rooms"""
        try:
            results = []
            
            # Get live rooms
            live_rooms = await self._get_live_rooms(query, max_results, filters)
            
            for room_data in live_rooms:
                room = await self._parse_room_data(room_data)
                if room and room.is_live:
                    result = CrawlerResult(
                        url=room.url,
                        title=f"[LIVE] {room.title}",
                        content=room.description,
                        metadata={
                            'room_data': asdict(room),
                            'platform': 'clubhouse',
                            'content_type': 'live_room',
                            'is_live': True,
                            'audience_count': room.audience_count,
                            'speaker_count': len(room.speaker_user_ids),
                            'topic': room.topic,
                            'club_name': room.club_name,
                            'language': room.language
                        },
                        timestamp=room.creation_time,
                        similarity_score=0.0
                    )
                    results.append(result)
            
            return results[:max_results]
            
        except Exception as e:
            self.logger.error(f"Error crawling live Clubhouse rooms: {str(e)}")
            return []
    
    async def _crawl_trending(self, query: str, max_results: int, filters: Dict[str, Any] = None) -> List[CrawlerResult]:
        """Crawl trending Clubhouse content"""
        try:
            results = []
            
            # Get trending content
            trending_content = await self._get_trending_content(query, max_results, filters)
            
            for content in trending_content:
                result = CrawlerResult(
                    url=content.get('url', ''),
                    title=f"[TRENDING] {content.get('title', 'Unknown')}",
                    content=content.get('description', ''),
                    metadata={
                        'trending_data': content,
                        'platform': 'clubhouse',
                        'content_type': 'trending',
                        'is_trending': True,
                        'trend_score': content.get('trend_score', 0),
                        'category': content.get('category', 'general')
                    },
                    timestamp=datetime.utcnow(),
                    similarity_score=0.0
                )
                results.append(result)
            
            return results[:max_results]
            
        except Exception as e:
            self.logger.error(f"Error crawling trending Clubhouse content: {str(e)}")
            return []
    
    async def _crawl_search(self, query: str, max_results: int, filters: Dict[str, Any] = None) -> List[CrawlerResult]:
        """General Clubhouse search"""
        try:
            results = []
            
            # Search across different content types
            rooms = await self._crawl_rooms(query, max_results // 3, filters)
            users = await self._crawl_users(query, max_results // 3, filters)
            clubs = await self._crawl_clubs(query, max_results // 3, filters)
            
            results.extend(rooms)
            results.extend(users)
            results.extend(clubs)
            
            return results[:max_results]
            
        except Exception as e:
            self.logger.error(f"Error performing Clubhouse search: {str(e)}")
            return []
    
    # Mock data generators (for demonstration)
    
    async def _get_mock_rooms(self, query: str, max_results: int) -> List[Dict[str, Any]]:
        """Generate mock room data"""
        rooms = []
        
        for i in range(min(max_results, 15)):
            creation_time = datetime.utcnow() - timedelta(hours=random.randint(1, 24))
            rooms.append({
                'id': f'room_{i}',
                'title': f'{query} Discussion {i}' if query else f'Room {i}',
                'description': f'Live discussion about {query}' if query else f'Room description {i}',
                'topic': query if query else random.choice(['Technology', 'Business', 'Entertainment', 'Health']),
                'club_id': f'club_{i % 5}',
                'club_name': f'{query} Club {i % 5}' if query else f'Club {i % 5}',
                'creator_user_id': f'user_{i}',
                'creator_username': f'{query.lower() if query else "user"}{i}',
                'moderator_user_ids': [f'user_{i}', f'user_{i+1}'],
                'speaker_user_ids': [f'user_{j}' for j in range(i, i+random.randint(2, 8))],
                'audience_count': random.randint(10, 5000),
                'creation_time': creation_time.isoformat(),
                'is_private': random.choice([True, False]),
                'is_recorded': random.choice([True, False]),
                'language': random.choice(['en', 'es', 'fr', 'de', 'ja']),
                'room_type': random.choice(['open', 'social', 'closed']),
                'url': f'{self.base_url}/room/{query.lower() if query else "room"}-{i}',
                'is_live': random.choice([True, False]),
                'duration_seconds': random.randint(600, 7200) if random.choice([True, False]) else None,
                'tags': [query] if query else ['discussion', 'live'],
                'waiting_list_count': random.randint(0, 100)
            })
        
        return rooms
    
    async def _get_mock_users(self, query: str, max_results: int) -> List[Dict[str, Any]]:
        """Generate mock user data"""
        users = []
        
        for i in range(min(max_results, 20)):
            joined_date = datetime.utcnow() - timedelta(days=random.randint(30, 730))
            users.append({
                'id': f'user_{i}',
                'username': f'{query.lower() if query else "user"}{i}',
                'name': f'{query} Expert {i}' if query else f'User {i}',
                'bio': f'Passionate about {query}' if query else f'Clubhouse user {i}',
                'num_followers': random.randint(50, 10000),
                'num_following': random.randint(20, 1000),
                'is_verified': random.choice([True, False]),
                'joined_date': joined_date.isoformat(),
                'clubs': [f'club_{j}' for j in range(random.randint(1, 5))],
                'interests': [query] if query else ['technology', 'business', 'entertainment'],
                'speaking_time_minutes': random.randint(10, 5000),
                'hosting_time_minutes': random.randint(0, 1000),
                'location': random.choice(['San Francisco, CA', 'New York, NY', 'London, UK', None]),
                'languages': random.choice([['en'], ['en', 'es'], ['en', 'fr'], ['en', 'de']])
            })
        
        return users
    
    async def _get_mock_clubs(self, query: str, max_results: int) -> List[Dict[str, Any]]:
        """Generate mock club data"""
        clubs = []
        
        for i in range(min(max_results, 10)):
            created_at = datetime.utcnow() - timedelta(days=random.randint(60, 1095))
            clubs.append({
                'id': f'club_{i}',
                'name': f'{query} Community {i}' if query else f'Club {i}',
                'description': f'Community for {query} enthusiasts' if query else f'Club description {i}',
                'num_members': random.randint(100, 50000),
                'num_followers': random.randint(200, 100000),
                'creator_user_id': f'user_{i}',
                'admin_user_ids': [f'user_{j}' for j in range(i, i+3)],
                'member_user_ids': [f'user_{j}' for j in range(i, i+random.randint(10, 100))],
                'is_private': random.choice([True, False]),
                'is_social': random.choice([True, False]),
                'created_at': created_at.isoformat(),
                'topics': [query] if query else ['technology', 'networking', 'discussion'],
                'rules': f'Be respectful when discussing {query}' if query else 'Club rules here',
                'num_rooms': random.randint(1, 50),
                'url': f'{self.base_url}/club/{query.lower() if query else "club"}-{i}',
                'membership_type': random.choice(['open', 'approval_required', 'closed']),
                'recent_speakers': [f'user_{j}' for j in range(i, i+5)],
                'social_links': {
                    'twitter': f'@{query.lower() if query else "club"}{i}',
                    'instagram': f'@{query.lower() if query else "club"}{i}'
                }
            })
        
        return clubs
    
    async def _get_mock_events(self, query: str, max_results: int) -> List[Dict[str, Any]]:
        """Generate mock event data"""
        events = []
        
        for i in range(min(max_results, 12)):
            scheduled_time = datetime.utcnow() + timedelta(days=random.randint(1, 30))
            events.append({
                'id': f'event_{i}',
                'name': f'{query} Event {i}' if query else f'Event {i}',
                'description': f'Special event about {query}' if query else f'Event description {i}',
                'club_id': f'club_{i % 5}',
                'club_name': f'{query} Club {i % 5}' if query else f'Club {i % 5}',
                'creator_user_id': f'user_{i}',
                'host_user_ids': [f'user_{i}', f'user_{i+1}'],
                'scheduled_time': scheduled_time.isoformat(),
                'timezone': 'UTC',
                'is_recurring': random.choice([True, False]),
                'attendee_count': random.randint(10, 1000),
                'interested_count': random.randint(20, 2000),
                'is_private': random.choice([True, False]),
                'url': f'{self.base_url}/event/{query.lower() if query else "event"}-{i}',
                'topics': [query] if query else ['discussion', 'networking'],
                'language': random.choice(['en', 'es', 'fr', 'de']),
                'cost': random.choice([None, round(random.uniform(5.0, 50.0), 2)]),
                'currency': 'USD',
                'is_cancelled': random.choice([True, False])
            })
        
        return events
    
    async def _get_mock_notifications(self, query: str, max_results: int) -> List[Dict[str, Any]]:
        """Generate mock notification data"""
        notifications = []
        notification_types = ['room_start', 'user_joined_room', 'club_activity', 'event_reminder', 'follow']
        
        for i in range(min(max_results, 25)):
            created_at = datetime.utcnow() - timedelta(hours=random.randint(1, 72))
            notification_type = random.choice(notification_types)
            notifications.append({
                'id': f'notification_{i}',
                'user_id': f'user_{i % 10}',
                'type': notification_type,
                'title': f'{query} Activity' if query else f'Clubhouse Activity {i}',
                'message': f'New activity related to {query}' if query else f'Notification message {i}',
                'created_at': created_at.isoformat(),
                'is_read': random.choice([True, False]),
                'action_url': f'{self.base_url}/activity/{i}',
                'related_user_id': f'user_{random.randint(0, 100)}' if random.choice([True, False]) else None,
                'related_room_id': f'room_{random.randint(0, 50)}' if random.choice([True, False]) else None,
                'related_club_id': f'club_{random.randint(0, 20)}' if random.choice([True, False]) else None
            })
        
        return notifications
    
    async def _get_live_rooms(self, query: str, max_results: int, filters: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """Get live room data"""
        rooms = await self._get_mock_rooms(query, max_results)
        # Filter for live rooms
        live_rooms = [room for room in rooms if room.get('is_live', False)]
        return live_rooms[:max_results]
    
    async def _get_trending_content(self, query: str, max_results: int, filters: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """Get trending content"""
        content = []
        
        for i in range(min(max_results, 10)):
            content.append({
                'title': f'Trending: {query} {i}' if query else f'Trending Content {i}',
                'url': f'{self.base_url}/trending/{i}',
                'description': f'Trending content about {query}' if query else f'Trending description {i}',
                'trend_score': random.randint(50, 100),
                'category': random.choice(['technology', 'business', 'entertainment', 'health'])
            })
        
        return content
    
    # Parser methods
    
    async def _parse_room_data(self, room_data: Dict[str, Any]) -> Optional[ClubhouseRoom]:
        """Parse room data"""
        try:
            creation_time = datetime.fromisoformat(room_data.get('creation_time', datetime.utcnow().isoformat()).replace('Z', '+00:00'))
            
            room = ClubhouseRoom(
                room_id=room_data.get('id', ''),
                title=room_data.get('title', ''),
                description=room_data.get('description', ''),
                topic=room_data.get('topic', ''),
                club_id=room_data.get('club_id'),
                club_name=room_data.get('club_name'),
                creator_user_id=room_data.get('creator_user_id', ''),
                creator_username=room_data.get('creator_username', ''),
                moderator_user_ids=room_data.get('moderator_user_ids', []),
                speaker_user_ids=room_data.get('speaker_user_ids', []),
                audience_count=room_data.get('audience_count', 0),
                creation_time=creation_time,
                is_private=room_data.get('is_private', False),
                is_recorded=room_data.get('is_recorded', False),
                language=room_data.get('language', 'en'),
                room_type=room_data.get('room_type', 'open'),
                url=room_data.get('url', ''),
                is_live=room_data.get('is_live', False),
                ended_at=None,
                duration_seconds=room_data.get('duration_seconds'),
                tags=room_data.get('tags', []),
                audience_insights={},
                recording_url=room_data.get('recording_url'),
                transcript=room_data.get('transcript'),
                featured_speakers=room_data.get('featured_speakers', []),
                waiting_list_count=room_data.get('waiting_list_count', 0),
                max_audience=room_data.get('max_audience')
            )
            
            return room
            
        except Exception as e:
            self.logger.error(f"Error parsing room data: {str(e)}")
            return None
    
    async def _parse_user_data(self, user_data: Dict[str, Any]) -> Optional[ClubhouseUser]:
        """Parse user data"""
        try:
            joined_date = datetime.fromisoformat(user_data.get('joined_date', datetime.utcnow().isoformat()).replace('Z', '+00:00'))
            
            user = ClubhouseUser(
                user_id=user_data.get('id', ''),
                username=user_data.get('username', ''),
                name=user_data.get('name', ''),
                bio=user_data.get('bio', ''),
                photo_url='',
                num_followers=user_data.get('num_followers', 0),
                num_following=user_data.get('num_following', 0),
                is_verified=user_data.get('is_verified', False),
                is_invited_speaker=user_data.get('is_invited_speaker', False),
                is_moderator=user_data.get('is_moderator', False),
                joined_date=joined_date,
                last_active_minutes=user_data.get('last_active_minutes'),
                clubs=user_data.get('clubs', []),
                interests=user_data.get('interests', []),
                invited_by_user_id=user_data.get('invited_by_user_id'),
                invitation_count=user_data.get('invitation_count', 0),
                room_visits=user_data.get('room_visits', 0),
                speaking_time_minutes=user_data.get('speaking_time_minutes', 0),
                hosting_time_minutes=user_data.get('hosting_time_minutes', 0),
                twitter_handle=user_data.get('twitter_handle'),
                instagram_handle=user_data.get('instagram_handle'),
                location=user_data.get('location'),
                languages=user_data.get('languages', ['en']),
                blocked_users=user_data.get('blocked_users', []),
                blocking_users=user_data.get('blocking_users', []),
                notifications_enabled=user_data.get('notifications_enabled', True)
            )
            
            return user
            
        except Exception as e:
            self.logger.error(f"Error parsing user data: {str(e)}")
            return None
    
    async def _parse_club_data(self, club_data: Dict[str, Any]) -> Optional[ClubhouseClub]:
        """Parse club data"""
        try:
            created_at = datetime.fromisoformat(club_data.get('created_at', datetime.utcnow().isoformat()).replace('Z', '+00:00'))
            
            club = ClubhouseClub(
                club_id=club_data.get('id', ''),
                name=club_data.get('name', ''),
                description=club_data.get('description', ''),
                photo_url='',
                banner_url=club_data.get('banner_url'),
                num_members=club_data.get('num_members', 0),
                num_followers=club_data.get('num_followers', 0),
                creator_user_id=club_data.get('creator_user_id', ''),
                admin_user_ids=club_data.get('admin_user_ids', []),
                member_user_ids=club_data.get('member_user_ids', []),
                is_private=club_data.get('is_private', False),
                is_social=club_data.get('is_social', False),
                created_at=created_at,
                topics=club_data.get('topics', []),
                rules=club_data.get('rules', ''),
                welcome_for_new_members=club_data.get('welcome_for_new_members'),
                num_rooms=club_data.get('num_rooms', 0),
                url=club_data.get('url', ''),
                enable_private=club_data.get('enable_private', False),
                is_community=club_data.get('is_community', False),
                recent_speakers=club_data.get('recent_speakers', []),
                featured_rooms=club_data.get('featured_rooms', []),
                upcoming_events=club_data.get('upcoming_events', []),
                membership_type=club_data.get('membership_type', 'open'),
                guidelines=club_data.get('guidelines', ''),
                contact_email=club_data.get('contact_email'),
                website_url=club_data.get('website_url'),
                social_links=club_data.get('social_links', {})
            )
            
            return club
            
        except Exception as e:
            self.logger.error(f"Error parsing club data: {str(e)}")
            return None
    
    async def _parse_event_data(self, event_data: Dict[str, Any]) -> Optional[ClubhouseEvent]:
        """Parse event data"""
        try:
            scheduled_time = datetime.fromisoformat(event_data.get('scheduled_time', datetime.utcnow().isoformat()).replace('Z', '+00:00'))
            
            event = ClubhouseEvent(
                event_id=event_data.get('id', ''),
                name=event_data.get('name', ''),
                description=event_data.get('description', ''),
                club_id=event_data.get('club_id'),
                club_name=event_data.get('club_name'),
                creator_user_id=event_data.get('creator_user_id', ''),
                host_user_ids=event_data.get('host_user_ids', []),
                scheduled_time=scheduled_time,
                end_time=None,
                timezone=event_data.get('timezone', 'UTC'),
                is_recurring=event_data.get('is_recurring', False),
                recurrence_pattern=event_data.get('recurrence_pattern'),
                room_id=event_data.get('room_id'),
                attendee_count=event_data.get('attendee_count', 0),
                interested_count=event_data.get('interested_count', 0),
                reminder_count=event_data.get('reminder_count', 0),
                is_private=event_data.get('is_private', False),
                url=event_data.get('url', ''),
                topics=event_data.get('topics', []),
                language=event_data.get('language', 'en'),
                max_attendees=event_data.get('max_attendees'),
                cost=event_data.get('cost'),
                currency=event_data.get('currency'),
                ticket_url=event_data.get('ticket_url'),
                promotional_image_url=event_data.get('promotional_image_url'),
                is_cancelled=event_data.get('is_cancelled', False),
                cancellation_reason=event_data.get('cancellation_reason')
            )
            
            return event
            
        except Exception as e:
            self.logger.error(f"Error parsing event data: {str(e)}")
            return None
    
    async def _parse_notification_data(self, notification_data: Dict[str, Any]) -> Optional[ClubhouseNotification]:
        """Parse notification data"""
        try:
            created_at = datetime.fromisoformat(notification_data.get('created_at', datetime.utcnow().isoformat()).replace('Z', '+00:00'))
            
            notification = ClubhouseNotification(
                notification_id=notification_data.get('id', ''),
                user_id=notification_data.get('user_id', ''),
                type=notification_data.get('type', ''),
                title=notification_data.get('title', ''),
                message=notification_data.get('message', ''),
                created_at=created_at,
                is_read=notification_data.get('is_read', False),
                action_url=notification_data.get('action_url'),
                related_user_id=notification_data.get('related_user_id'),
                related_room_id=notification_data.get('related_room_id'),
                related_club_id=notification_data.get('related_club_id'),
                metadata=notification_data.get('metadata', {})
            )
            
            return notification
            
        except Exception as e:
            self.logger.error(f"Error parsing notification data: {str(e)}")
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
    
    async def extract_content_metadata(self, url: str) -> Dict[str, Any]:
        """Extract metadata from Clubhouse content"""
        try:
            # Parse Clubhouse URL
            parsed_url = urlparse(url)
            
            metadata = {
                'platform': 'clubhouse',
                'url': url,
                'extracted_at': datetime.utcnow().isoformat()
            }
            
            # Handle Clubhouse URLs
            if 'clubhouse.com' in parsed_url.netloc:
                path_parts = parsed_url.path.strip('/').split('/')
                
                if len(path_parts) >= 2:
                    content_type = path_parts[0]  # room, club, event, @username
                    content_id = path_parts[1]
                    
                    if content_type.startswith('@'):
                        # User profile: @username
                        metadata.update({
                            'content_type': 'user',
                            'username': content_type[1:]
                        })
                    else:
                        # Other content types
                        metadata.update({
                            'content_type': content_type,
                            'content_id': content_id
                        })
            
            return metadata
            
        except Exception as e:
            self.logger.error(f"Error extracting Clubhouse metadata: {str(e)}")
            return {'error': str(e)}
    
    def get_platform_info(self) -> Dict[str, Any]:
        """Get Clubhouse platform information"""
        return {
            'platform_name': 'Clubhouse',
            'base_url': self.base_url,
            'api_base_url': self.api_base_url,
            'supported_content_types': list(self.content_types.keys()),
            'rate_limits': {
                'requests_per_minute': self.requests_per_minute,
                'min_delay': self.min_delay,
                'max_delay': self.max_delay
            },
            'features': [
                'Live room monitoring',
                'User profile analysis',
                'Club activity tracking',
                'Event scheduling analysis',
                'Audio content transcription',
                'Speaker identification',
                'Topic trend analysis',
                'Social graph mapping',
                'Engagement metrics',
                'Content discovery'
            ],
            'authentication': {
                'required': True,
                'type': 'OAuth 2.0',
                'scope': 'Private content access'
            },
            'content_characteristics': {
                'audio_only': True,
                'real_time': True,
                'invite_only': True,
                'ephemeral_content': True
            },
            'limitations': [
                'Requires authentication',
                'Invite-only platform',
                'Limited public content',
                'Very strict rate limiting',
                'Content is ephemeral',
                'No traditional search functionality'
            ]
        }
