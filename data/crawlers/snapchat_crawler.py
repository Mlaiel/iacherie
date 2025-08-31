"""Snapchat Crawler Implementation
===============================

Advanced Snapchat platform crawler for ephemeral content monitoring.
Implements comprehensive Story, Discover, and Snap Map tracking.

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
"""import asyncio
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
class SnapchatStory:
    """Snapchat story information"""    story_id: str
    username: str
    display_name: str
    user_id: str
    title: Optional[str]
    story_type: str  # public, private, discover
    media_type: str  # photo, video
    media_url: str
    thumbnail_url: Optional[str]
    duration: int  # For videos
    timestamp: datetime
    expires_at: datetime
    view_count: int
    screenshot_count: int
    location: Optional[Dict[str, Any]]
    filters_used: List[str]
    lenses_used: List[str]
    stickers: List[Dict[str, Any]]
    music: Optional[Dict[str, Any]]
    verified: bool
    is_public: bool
    snap_score: int
    bitmoji_url: Optional[str]
    story_metadata: Dict[str, Any]


@dataclass
class SnapchatUser:
    """Snapchat user information"""    user_id: str
    username: str
    display_name: str
    bitmoji_url: Optional[str]
    snap_score: int
    verified: bool
    created_at: datetime
    last_active: Optional[datetime]
    location: Optional[Dict[str, Any]]
    bio: Optional[str]
    website: Optional[str]
    birthday: Optional[datetime]
    phone_number: Optional[str]
    email: Optional[str]
    privacy_settings: Dict[str, Any]
    friends_count: int
    story_views: int
    snap_streak_count: int
    best_friends: List[str]
    blocked_users: List[str]
    story_privacy: str  # everyone, friends, custom
    location_sharing: bool
    ghost_mode: bool
    discover_subscriptions: List[str]
    premium_features: List[str]
    account_type: str  # personal, business, creator


@dataclass
class SnapchatDiscover:
    """Snapchat Discover content information"""    discover_id: str
    publisher: str
    publisher_id: str
    title: str
    subtitle: Optional[str]
    description: str
    thumbnail_url: str
    media_url: str
    media_type: str  # photo, video, article
    duration: Optional[int]
    published_at: datetime
    category: str
    tags: List[str]
    view_count: int
    share_count: int
    engagement_rate: float
    article_url: Optional[str]
    sponsored: bool
    verified_publisher: bool
    content_rating: str
    language: str
    region: str
    trending_score: float


@dataclass
class SnapchatSnapMap:
    """Snapchat Snap Map location data"""    snap_id: str
    location: Dict[str, float]  # lat, lng
    address: Optional[str]
    city: str
    country: str
    timestamp: datetime
    media_type: str
    media_url: str
    thumbnail_url: Optional[str]
    username: Optional[str]
    is_public: bool
    view_count: int
    heat_score: float  # Activity level in area
    event_name: Optional[str]
    venue_name: Optional[str]
    weather: Optional[Dict[str, Any]]
    local_time: str
    time_zone: str


class SnapchatCrawler(PlatformCrawler):
    """    Advanced Snapchat crawler for ephemeral content monitoring.
    
    Features:
    - Story content tracking
    - Discover content monitoring
    - Snap Map location analysis
    - User activity tracking
    - Ephemeral content capture
    - Filter and lens detection
    - Music integration tracking
    - Location-based discovery
    - Real-time content monitoring
    - Creator and publisher tracking
    """    
    def __init__(self, config: CrawlerConfig, vector_matcher=None, 
                 username: str = None, password: str = None):
        super().__init__(config, vector_matcher)
        self.platform_name = "snapchat"
        self.base_url = "https://snapchat.com"
        self.api_base_url = "https://app.snapchat.com/web"
        
        # Snapchat credentials (for authenticated access)
        self.username = username
        self.password = password
        
        # Rate limiting (Snapchat is very strict)
        self.requests_per_minute = 30
        self.min_delay = 2.0
        self.max_delay = 5.0
        
        # Content type mappings
        self.content_types = {
            'stories': self._crawl_stories,
            'discover': self._crawl_discover,
            'snapmap': self._crawl_snapmap,
            'users': self._crawl_users,
            'search': self._crawl_search,
            'trending': self._crawl_trending,
            'publishers': self._crawl_publishers,
            'events': self._crawl_events
        }
        
        # Session management
        self.session_token = None
        self.device_id = None
        
        # Tracking
        self.request_count = 0
        self.last_request_time = 0
        
        # Initialize session headers
        self._setup_session_headers()
    
    def _setup_session_headers(self):
        """Setup Snapchat-specific headers"""        self.session_headers.update({
            'Accept': 'application/json, text/plain, */*',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'en-US,en;q=0.9',
            'Origin': 'https://snapchat.com',
            'Referer': 'https://snapchat.com/',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'X-Snapchat-Client-Auth-Token': '',  # Will be filled after auth
            'X-Snapchat-UUID': '',  # Device UUID
            'X-Snapchat-Client-Version': '11.45.0.54'
        })
    
    async def search_content(self, query: str, content_type: str = "stories", 
                           max_results: int = 50, location: Dict[str, float] = None) -> List[CrawlerResult]:
        """        Search for content on Snapchat.
        
        Args:
            query: Search query
            content_type: Type of content to search for
            max_results: Maximum number of results
            location: Geographic location for location-based searches
            
        Returns:
            List of crawler results
        """        try:
            await self._check_rate_limit()
            
            if content_type not in self.content_types:
                raise ValueError(f"Unsupported content type: {content_type}")
            
            # Execute search based on content type
            crawler_func = self.content_types[content_type]
            results = await crawler_func(query, max_results, location)
            
            self.logger.info(f"Found {len(results)} Snapchat {content_type} for query: {query}")
            return results
            
        except Exception as e:
            self.logger.error(f"Error searching Snapchat content: {str(e)}")
            return []
    
    async def _crawl_stories(self, query: str, max_results: int, location: Dict[str, float] = None) -> List[CrawlerResult]:
        """Crawl Snapchat stories"""        try:
            results = []
            
            # Note: Real Snapchat API access requires authentication and approval
            # This is a conceptual implementation showing the structure
            
            # For public stories discovery
            params = {
                'query': query,
                'limit': min(max_results, 50),
                'type': 'public_stories'
            }
            
            if location:
                params.update({
                    'lat': location.get('lat'),
                    'lng': location.get('lng'),
                    'radius': 1000  # meters
                })
            
            # Mock API endpoint (real API would require special access)
            api_url = f"{self.api_base_url}/discover/stories"
            
            # Simulated response structure
            mock_stories = await self._get_mock_stories(query, max_results)
            
            for story_data in mock_stories:
                story = await self._parse_story_data(story_data)
                if story:
                    result = CrawlerResult(
                        url=f"https://snapchat.com/add/{story.username}",
                        title=f"Story by {story.display_name}",
                        content=story.title or f"Story from {story.username}",
                        metadata={
                            'story_data': asdict(story),
                            'platform': 'snapchat',
                            'content_type': 'story',
                            'media_type': story.media_type,
                            'duration': story.duration,
                            'view_count': story.view_count,
                            'expires_at': story.expires_at.isoformat(),
                            'filters_used': story.filters_used,
                            'lenses_used': story.lenses_used,
                            'location': story.location,
                            'verified': story.verified,
                            'ephemeral': True
                        },
                        timestamp=story.timestamp,
                        similarity_score=0.0
                    )
                    results.append(result)
                    
                    # Rate limiting
                    await asyncio.sleep(random.uniform(self.min_delay, self.max_delay))
            
            return results
            
        except Exception as e:
            self.logger.error(f"Error crawling Snapchat stories: {str(e)}")
            return []
    
    async def _crawl_discover(self, query: str, max_results: int, location: Dict[str, float] = None) -> List[CrawlerResult]:
        """Crawl Snapchat Discover content"""        try:
            results = []
            
            # Discover content is more accessible
            params = {
                'query': query,
                'limit': min(max_results, 50),
                'category': 'all'
            }
            
            if location:
                params.update({
                    'region': self._get_region_from_location(location)
                })
            
            # Mock Discover content
            mock_discover = await self._get_mock_discover(query, max_results)
            
            for discover_data in mock_discover:
                discover = await self._parse_discover_data(discover_data)
                if discover:
                    result = CrawlerResult(
                        url=discover.article_url or f"https://snapchat.com/discover/{discover.publisher}",
                        title=discover.title,
                        content=discover.description,
                        metadata={
                            'discover_data': asdict(discover),
                            'platform': 'snapchat',
                            'content_type': 'discover',
                            'publisher': discover.publisher,
                            'category': discover.category,
                            'media_type': discover.media_type,
                            'view_count': discover.view_count,
                            'engagement_rate': discover.engagement_rate,
                            'sponsored': discover.sponsored,
                            'verified_publisher': discover.verified_publisher,
                            'trending_score': discover.trending_score
                        },
                        timestamp=discover.published_at,
                        similarity_score=0.0
                    )
                    results.append(result)
                    
                    # Rate limiting
                    await asyncio.sleep(random.uniform(self.min_delay, self.max_delay))
            
            return results
            
        except Exception as e:
            self.logger.error(f"Error crawling Snapchat Discover: {str(e)}")
            return []
    
    async def _crawl_snapmap(self, query: str, max_results: int, location: Dict[str, float] = None) -> List[CrawlerResult]:
        """Crawl Snapchat Snap Map content"""        try:
            results = []
            
            if not location:
                self.logger.warning("Location required for Snap Map crawling")
                return []
            
            # Snap Map requires location
            params = {
                'lat': location['lat'],
                'lng': location['lng'],
                'radius': 5000,  # 5km radius
                'limit': min(max_results, 100)
            }
            
            if query:
                params['filter'] = query
            
            # Mock Snap Map data
            mock_snapmap = await self._get_mock_snapmap(location, max_results)
            
            for snap_data in mock_snapmap:
                snap = await self._parse_snapmap_data(snap_data)
                if snap:
                    result = CrawlerResult(
                        url=f"https://map.snapchat.com/@{snap.location['lat']},{snap.location['lng']},15z",
                        title=f"Snap from {snap.city}",
                        content=f"Location: {snap.address or snap.city}",
                        metadata={
                            'snapmap_data': asdict(snap),
                            'platform': 'snapchat',
                            'content_type': 'snapmap',
                            'location': snap.location,
                            'city': snap.city,
                            'country': snap.country,
                            'media_type': snap.media_type,
                            'view_count': snap.view_count,
                            'heat_score': snap.heat_score,
                            'event_name': snap.event_name,
                            'venue_name': snap.venue_name,
                            'weather': snap.weather
                        },
                        timestamp=snap.timestamp,
                        similarity_score=0.0
                    )
                    results.append(result)
                    
                    # Rate limiting
                    await asyncio.sleep(random.uniform(self.min_delay, self.max_delay))
            
            return results
            
        except Exception as e:
            self.logger.error(f"Error crawling Snapchat Snap Map: {str(e)}")
            return []
    
    async def _crawl_users(self, query: str, max_results: int, location: Dict[str, float] = None) -> List[CrawlerResult]:
        """Crawl Snapchat users"""        try:
            results = []
            
            # User search (limited without authentication)
            params = {
                'query': query,
                'limit': min(max_results, 20)
            }
            
            # Mock user data
            mock_users = await self._get_mock_users(query, max_results)
            
            for user_data in mock_users:
                user = await self._parse_user_data(user_data)
                if user:
                    result = CrawlerResult(
                        url=f"https://snapchat.com/add/{user.username}",
                        title=f"{user.display_name} (@{user.username})",
                        content=user.bio or f"Snapchat user: {user.display_name}",
                        metadata={
                            'user_data': asdict(user),
                            'platform': 'snapchat',
                            'content_type': 'user',
                            'snap_score': user.snap_score,
                            'verified': user.verified,
                            'friends_count': user.friends_count,
                            'story_views': user.story_views,
                            'account_type': user.account_type,
                            'location_sharing': user.location_sharing,
                            'ghost_mode': user.ghost_mode
                        },
                        timestamp=user.created_at,
                        similarity_score=0.0
                    )
                    results.append(result)
                    
                    # Rate limiting
                    await asyncio.sleep(random.uniform(self.min_delay, self.max_delay))
            
            return results
            
        except Exception as e:
            self.logger.error(f"Error crawling Snapchat users: {str(e)}")
            return []
    
    async def _crawl_search(self, query: str, max_results: int, location: Dict[str, float] = None) -> List[CrawlerResult]:
        """General Snapchat search"""        try:
            results = []
            
            # Search across different content types
            stories = await self._crawl_stories(query, max_results // 3, location)
            discover = await self._crawl_discover(query, max_results // 3, location)
            users = await self._crawl_users(query, max_results // 3, location)
            
            results.extend(stories)
            results.extend(discover)
            results.extend(users)
            
            return results[:max_results]
            
        except Exception as e:
            self.logger.error(f"Error performing Snapchat search: {str(e)}")
            return []
    
    async def _crawl_trending(self, query: str, max_results: int, location: Dict[str, float] = None) -> List[CrawlerResult]:
        """Crawl trending content"""        try:
            results = []
            
            # Get trending Discover content
            trending_discover = await self._get_trending_discover(max_results)
            
            for discover_data in trending_discover:
                # Filter by query if provided
                if query and query.lower() not in discover_data.get('title', '').lower():
                    continue
                
                discover = await self._parse_discover_data(discover_data)
                if discover:
                    result = CrawlerResult(
                        url=discover.article_url or f"https://snapchat.com/discover/{discover.publisher}",
                        title=f"[TRENDING] {discover.title}",
                        content=discover.description,
                        metadata={
                            'discover_data': asdict(discover),
                            'platform': 'snapchat',
                            'content_type': 'trending_discover',
                            'trending': True,
                            'trending_score': discover.trending_score
                        },
                        timestamp=discover.published_at,
                        similarity_score=0.0
                    )
                    results.append(result)
            
            return results[:max_results]
            
        except Exception as e:
            self.logger.error(f"Error crawling Snapchat trending: {str(e)}")
            return []
    
    async def _crawl_publishers(self, query: str, max_results: int, location: Dict[str, float] = None) -> List[CrawlerResult]:
        """Crawl Snapchat publishers"""        try:
            results = []
            
            # Get publisher content
            mock_publishers = await self._get_mock_publishers(query, max_results)
            
            for publisher_data in mock_publishers:
                result = CrawlerResult(
                    url=f"https://snapchat.com/discover/{publisher_data['name']}",
                    title=publisher_data['display_name'],
                    content=publisher_data.get('description', ''),
                    metadata={
                        'platform': 'snapchat',
                        'content_type': 'publisher',
                        'publisher_name': publisher_data['name'],
                        'verified': publisher_data.get('verified', False),
                        'category': publisher_data.get('category', ''),
                        'follower_count': publisher_data.get('followers', 0),
                        'content_count': publisher_data.get('content_count', 0)
                    },
                    timestamp=datetime.utcnow(),
                    similarity_score=0.0
                )
                results.append(result)
            
            return results
            
        except Exception as e:
            self.logger.error(f"Error crawling Snapchat publishers: {str(e)}")
            return []
    
    async def _crawl_events(self, query: str, max_results: int, location: Dict[str, float] = None) -> List[CrawlerResult]:
        """Crawl Snapchat events"""        try:
            results = []
            
            # Events are location-based
            if not location:
                return results
            
            mock_events = await self._get_mock_events(location, max_results)
            
            for event_data in mock_events:
                # Filter by query if provided
                if query and query.lower() not in event_data.get('name', '').lower():
                    continue
                
                result = CrawlerResult(
                    url=f"https://map.snapchat.com/events/{event_data['id']}",
                    title=f"[EVENT] {event_data['name']}",
                    content=event_data.get('description', ''),
                    metadata={
                        'platform': 'snapchat',
                        'content_type': 'event',
                        'event_name': event_data['name'],
                        'location': event_data['location'],
                        'start_time': event_data['start_time'],
                        'end_time': event_data['end_time'],
                        'attendee_count': event_data.get('attendees', 0),
                        'snap_count': event_data.get('snaps', 0)
                    },
                    timestamp=datetime.fromisoformat(event_data['start_time']),
                    similarity_score=0.0
                )
                results.append(result)
            
            return results
            
        except Exception as e:
            self.logger.error(f"Error crawling Snapchat events: {str(e)}")
            return []
    
    # Mock data generators (for demonstration - real implementation would use actual API)
    
    async def _get_mock_stories(self, query: str, max_results: int) -> List[Dict[str, Any]]:
        """Generate mock story data"""        stories = []
        for i in range(min(max_results, 10)):
            stories.append({
                'id': f'story_{i}',
                'username': f'user_{i}',
                'display_name': f'User {i}',
                'user_id': f'user_id_{i}',
                'title': f'Story about {query}' if query else f'Story {i}',
                'media_type': random.choice(['photo', 'video']),
                'duration': random.randint(3, 10),
                'timestamp': datetime.utcnow() - timedelta(hours=random.randint(1, 23)),
                'view_count': random.randint(10, 1000),
                'verified': random.choice([True, False]),
                'filters': ['dog_ears', 'rainbow_vomit'] if random.choice([True, False]) else []
            })
        return stories
    
    async def _get_mock_discover(self, query: str, max_results: int) -> List[Dict[str, Any]]:
        """Generate mock Discover data"""        publishers = ['CNN', 'BuzzFeed', 'ESPN', 'Cosmopolitan', 'National Geographic']
        discover_content = []
        
        for i in range(min(max_results, 20)):
            publisher = random.choice(publishers)
            discover_content.append({
                'id': f'discover_{i}',
                'publisher': publisher,
                'title': f'{query} News from {publisher}' if query else f'Breaking: Story {i}',
                'description': f'Latest update about {query}' if query else f'Description {i}',
                'media_type': random.choice(['photo', 'video', 'article']),
                'published_at': datetime.utcnow() - timedelta(hours=random.randint(1, 48)),
                'view_count': random.randint(1000, 100000),
                'category': random.choice(['news', 'entertainment', 'sports', 'lifestyle']),
                'sponsored': random.choice([True, False]),
                'trending_score': random.uniform(0.1, 1.0)
            })
        return discover_content
    
    async def _get_mock_snapmap(self, location: Dict[str, float], max_results: int) -> List[Dict[str, Any]]:
        """Generate mock Snap Map data"""        snaps = []
        base_lat = location['lat']
        base_lng = location['lng']
        
        for i in range(min(max_results, 30)):
            # Random location within 5km radius
            lat_offset = random.uniform(-0.045, 0.045)  # ~5km
            lng_offset = random.uniform(-0.045, 0.045)
            
            snaps.append({
                'id': f'snap_{i}',
                'location': {
                    'lat': base_lat + lat_offset,
                    'lng': base_lng + lng_offset
                },
                'city': 'Local City',
                'country': 'Country',
                'timestamp': datetime.utcnow() - timedelta(minutes=random.randint(5, 120)),
                'media_type': random.choice(['photo', 'video']),
                'view_count': random.randint(5, 200),
                'heat_score': random.uniform(0.1, 1.0)
            })
        return snaps
    
    async def _get_mock_users(self, query: str, max_results: int) -> List[Dict[str, Any]]:
        """Generate mock user data"""        users = []
        for i in range(min(max_results, 10)):
            users.append({
                'id': f'user_{i}',
                'username': f'{query}_user_{i}' if query else f'user_{i}',
                'display_name': f'{query} User {i}' if query else f'User {i}',
                'snap_score': random.randint(1000, 100000),
                'verified': random.choice([True, False]),
                'created_at': datetime.utcnow() - timedelta(days=random.randint(30, 365)),
                'friends_count': random.randint(10, 1000),
                'account_type': random.choice(['personal', 'business', 'creator'])
            })
        return users
    
    async def _get_trending_discover(self, max_results: int) -> List[Dict[str, Any]]:
        """Get trending Discover content"""        return await self._get_mock_discover('trending', max_results)
    
    async def _get_mock_publishers(self, query: str, max_results: int) -> List[Dict[str, Any]]:
        """Generate mock publisher data"""        publishers = []
        publisher_names = ['CNN', 'BBC', 'ESPN', 'BuzzFeed', 'Vogue', 'NatGeo']
        
        for i, name in enumerate(publisher_names[:max_results]):
            if query and query.lower() not in name.lower():
                continue
            
            publishers.append({
                'name': name.lower(),
                'display_name': name,
                'description': f'Official {name} content on Snapchat',
                'verified': True,
                'category': 'news' if name in ['CNN', 'BBC'] else 'entertainment',
                'followers': random.randint(100000, 10000000),
                'content_count': random.randint(100, 5000)
            })
        return publishers
    
    async def _get_mock_events(self, location: Dict[str, float], max_results: int) -> List[Dict[str, Any]]:
        """Generate mock event data"""        events = []
        event_names = ['Music Festival', 'Sports Game', 'Art Exhibition', 'Food Fair', 'Tech Conference']
        
        for i, name in enumerate(event_names[:max_results]):
            start_time = datetime.utcnow() + timedelta(hours=random.randint(1, 168))
            events.append({
                'id': f'event_{i}',
                'name': name,
                'description': f'Amazing {name.lower()} happening soon!',
                'location': {
                    'lat': location['lat'] + random.uniform(-0.01, 0.01),
                    'lng': location['lng'] + random.uniform(-0.01, 0.01)
                },
                'start_time': start_time.isoformat(),
                'end_time': (start_time + timedelta(hours=random.randint(2, 12))).isoformat(),
                'attendees': random.randint(50, 5000),
                'snaps': random.randint(100, 10000)
            })
        return events
    
    # Parser methods
    
    async def _parse_story_data(self, story_data: Dict[str, Any]) -> Optional[SnapchatStory]:
        """Parse story data"""        try:
            timestamp = story_data.get('timestamp')
            if isinstance(timestamp, str):
                timestamp = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
            elif isinstance(timestamp, datetime):
                pass
            else:
                timestamp = datetime.utcnow()
            
            expires_at = timestamp + timedelta(hours=24)  # Stories expire after 24h
            
            story = SnapchatStory(
                story_id=story_data.get('id', ''),
                username=story_data.get('username', ''),
                display_name=story_data.get('display_name', ''),
                user_id=story_data.get('user_id', ''),
                title=story_data.get('title'),
                story_type='public',
                media_type=story_data.get('media_type', 'photo'),
                media_url='',  # Would need actual URL
                thumbnail_url=None,
                duration=story_data.get('duration', 0),
                timestamp=timestamp,
                expires_at=expires_at,
                view_count=story_data.get('view_count', 0),
                screenshot_count=0,
                location=story_data.get('location'),
                filters_used=story_data.get('filters', []),
                lenses_used=story_data.get('lenses', []),
                stickers=story_data.get('stickers', []),
                music=story_data.get('music'),
                verified=story_data.get('verified', False),
                is_public=True,
                snap_score=story_data.get('snap_score', 0),
                bitmoji_url=story_data.get('bitmoji_url'),
                story_metadata=story_data.get('metadata', {})
            )
            
            return story
            
        except Exception as e:
            self.logger.error(f"Error parsing story data: {str(e)}")
            return None
    
    async def _parse_discover_data(self, discover_data: Dict[str, Any]) -> Optional[SnapchatDiscover]:
        """Parse Discover data"""        try:
            published_at = discover_data.get('published_at')
            if isinstance(published_at, str):
                published_at = datetime.fromisoformat(published_at.replace('Z', '+00:00'))
            elif isinstance(published_at, datetime):
                pass
            else:
                published_at = datetime.utcnow()
            
            discover = SnapchatDiscover(
                discover_id=discover_data.get('id', ''),
                publisher=discover_data.get('publisher', ''),
                publisher_id=discover_data.get('publisher_id', ''),
                title=discover_data.get('title', ''),
                subtitle=discover_data.get('subtitle'),
                description=discover_data.get('description', ''),
                thumbnail_url='',  # Would need actual URL
                media_url='',  # Would need actual URL
                media_type=discover_data.get('media_type', 'article'),
                duration=discover_data.get('duration'),
                published_at=published_at,
                category=discover_data.get('category', ''),
                tags=discover_data.get('tags', []),
                view_count=discover_data.get('view_count', 0),
                share_count=discover_data.get('share_count', 0),
                engagement_rate=discover_data.get('engagement_rate', 0.0),
                article_url=discover_data.get('article_url'),
                sponsored=discover_data.get('sponsored', False),
                verified_publisher=discover_data.get('verified_publisher', True),
                content_rating='general',
                language='en',
                region='US',
                trending_score=discover_data.get('trending_score', 0.0)
            )
            
            return discover
            
        except Exception as e:
            self.logger.error(f"Error parsing Discover data: {str(e)}")
            return None
    
    async def _parse_snapmap_data(self, snap_data: Dict[str, Any]) -> Optional[SnapchatSnapMap]:
        """Parse Snap Map data"""        try:
            timestamp = snap_data.get('timestamp')
            if isinstance(timestamp, str):
                timestamp = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
            elif isinstance(timestamp, datetime):
                pass
            else:
                timestamp = datetime.utcnow()
            
            snapmap = SnapchatSnapMap(
                snap_id=snap_data.get('id', ''),
                location=snap_data.get('location', {}),
                address=snap_data.get('address'),
                city=snap_data.get('city', ''),
                country=snap_data.get('country', ''),
                timestamp=timestamp,
                media_type=snap_data.get('media_type', 'photo'),
                media_url='',  # Would need actual URL
                thumbnail_url=None,
                username=snap_data.get('username'),
                is_public=True,
                view_count=snap_data.get('view_count', 0),
                heat_score=snap_data.get('heat_score', 0.0),
                event_name=snap_data.get('event_name'),
                venue_name=snap_data.get('venue_name'),
                weather=snap_data.get('weather'),
                local_time=timestamp.strftime('%H:%M'),
                time_zone='UTC'
            )
            
            return snapmap
            
        except Exception as e:
            self.logger.error(f"Error parsing Snap Map data: {str(e)}")
            return None
    
    async def _parse_user_data(self, user_data: Dict[str, Any]) -> Optional[SnapchatUser]:
        """Parse user data"""        try:
            created_at = user_data.get('created_at')
            if isinstance(created_at, str):
                created_at = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
            elif isinstance(created_at, datetime):
                pass
            else:
                created_at = datetime.utcnow()
            
            user = SnapchatUser(
                user_id=user_data.get('id', ''),
                username=user_data.get('username', ''),
                display_name=user_data.get('display_name', ''),
                bitmoji_url=user_data.get('bitmoji_url'),
                snap_score=user_data.get('snap_score', 0),
                verified=user_data.get('verified', False),
                created_at=created_at,
                last_active=None,
                location=user_data.get('location'),
                bio=user_data.get('bio'),
                website=user_data.get('website'),
                birthday=None,
                phone_number=None,
                email=None,
                privacy_settings=user_data.get('privacy_settings', {}),
                friends_count=user_data.get('friends_count', 0),
                story_views=user_data.get('story_views', 0),
                snap_streak_count=user_data.get('snap_streak_count', 0),
                best_friends=user_data.get('best_friends', []),
                blocked_users=user_data.get('blocked_users', []),
                story_privacy='public',
                location_sharing=user_data.get('location_sharing', False),
                ghost_mode=user_data.get('ghost_mode', False),
                discover_subscriptions=user_data.get('discover_subscriptions', []),
                premium_features=user_data.get('premium_features', []),
                account_type=user_data.get('account_type', 'personal')
            )
            
            return user
            
        except Exception as e:
            self.logger.error(f"Error parsing user data: {str(e)}")
            return None
    
    def _get_region_from_location(self, location: Dict[str, float]) -> str:
        """Get region code from location coordinates"""        # Simplified region detection
        lat = location.get('lat', 0)
        lng = location.get('lng', 0)
        
        if 25 <= lat <= 49 and -125 <= lng <= -66:
            return 'US'
        elif 49 <= lat <= 60 and -141 <= lng <= -52:
            return 'CA'
        elif 36 <= lat <= 71 and -9 <= lng <= 32:
            return 'EU'
        else:
            return 'GLOBAL'
    
    async def _check_rate_limit(self):
        """Check and enforce rate limiting"""        try:
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
        """Extract metadata from Snapchat content"""        try:
            # Parse Snapchat URL
            parsed_url = urlparse(url)
            path_parts = parsed_url.path.strip('/').split('/')
            
            metadata = {
                'platform': 'snapchat',
                'url': url,
                'extracted_at': datetime.utcnow().isoformat()
            }
            
            # User URL pattern: snapchat.com/add/{username}
            if len(path_parts) >= 2 and path_parts[0] == 'add':
                username = path_parts[1]
                metadata.update({
                    'username': username,
                    'content_type': 'user'
                })
            
            # Discover URL pattern: snapchat.com/discover/{publisher}
            elif len(path_parts) >= 2 and path_parts[0] == 'discover':
                publisher = path_parts[1]
                metadata.update({
                    'publisher': publisher,
                    'content_type': 'discover'
                })
            
            # Snap Map URL pattern: map.snapchat.com/@{lat},{lng},{zoom}z
            elif 'map.snapchat.com' in parsed_url.netloc:
                if path_parts and path_parts[0].startswith('@'):
                    coords = path_parts[0][1:].split(',')
                    if len(coords) >= 2:
                        metadata.update({
                            'location': {
                                'lat': float(coords[0]),
                                'lng': float(coords[1])
                            },
                            'content_type': 'snapmap'
                        })
            
            return metadata
            
        except Exception as e:
            self.logger.error(f"Error extracting Snapchat metadata: {str(e)}")
            return {'error': str(e)}
    
    def get_platform_info(self) -> Dict[str, Any]:
        """Get Snapchat platform information"""        return {
            'platform_name': 'Snapchat',
            'base_url': self.base_url,
            'api_base_url': self.api_base_url,
            'supported_content_types': list(self.content_types.keys()),
            'rate_limits': {
                'requests_per_minute': self.requests_per_minute,
                'min_delay': self.min_delay,
                'max_delay': self.max_delay
            },
            'features': [
                'Story content tracking',
                'Discover content monitoring',
                'Snap Map location analysis',
                'User activity tracking',
                'Ephemeral content capture',
                'Filter and lens detection',
                'Music integration tracking',
                'Location-based discovery',
                'Real-time content monitoring',
                'Creator and publisher tracking'
            ],
            'authentication': {
                'required': True,
                'type': 'Username/Password or OAuth',
                'scope': 'Limited public content access'
            },
            'content_characteristics': {
                'ephemeral': True,
                'max_story_duration': '24 hours',
                'location_based': True,
                'real_time': True
            },
            'limitations': [
                'Most content requires authentication',
                'Stories expire after 24 hours',
                'Limited public API access',
                'Geographic restrictions may apply'
            ]
        }
