"""BeReal Crawler Implementation
=============================

Advanced BeReal platform crawler for authentic social content monitoring.
Implements comprehensive Post, User, and Real Moments tracking.

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
class BeRealPost:
    """BeReal post information"""
    post_id: str
    user_id: str
    username: str
    display_name: str
    caption: str
    primary_photo_url: str
    secondary_photo_url: str  # selfie camera
    location: Optional[str]
    latitude: Optional[float]
    longitude: Optional[float]
    creation_time: datetime
    is_late: bool
    late_in_seconds: Optional[int]
    reaction_count: int
    comment_count: int
    realmoji_count: int
    retake_count: int
    is_public: bool
    is_discovery: bool
    music_track: Optional[str]
    music_artist: Optional[str]
    tags: List[str]
    mentioned_users: List[str]
    visibility: str  # friends, friends_of_friends, public
    device_type: str
    app_version: str
    is_screenshot: bool
    screenshot_count: int
    memory_type: str  # daily, bonus, custom


@dataclass
class BeRealUser:
    """BeReal user information"""
    user_id: str
    username: str
    display_name: str
    profile_picture_url: str
    bio: Optional[str]
    location: Optional[str]
    birthday: Optional[datetime]
    phone_number: Optional[str]  # Masked
    follower_count: int
    following_count: int
    friend_count: int
    posts_count: int
    streak_count: int
    creation_date: datetime
    last_post_time: Optional[datetime]
    is_verified: bool
    is_public: bool
    is_discovering: bool
    time_zone: str
    country_code: str
    phone_country_code: str
    relationship_status: Optional[str]
    notification_settings: Dict[str, bool]
    privacy_settings: Dict[str, str]
    blocked_users: List[str]
    close_friends: List[str]


@dataclass
class BeRealMemory:
    """BeReal memory information"""
    memory_id: str
    user_id: str
    date: datetime
    primary_photo_url: str
    secondary_photo_url: str
    location: Optional[str]
    caption: Optional[str]
    is_late: bool
    late_in_seconds: Optional[int]
    memory_type: str
    is_favorite: bool
    reaction_count: int
    comment_count: int
    music_track: Optional[str]
    tags: List[str]
    weather: Optional[str]
    temperature: Optional[float]


@dataclass
class BeRealComment:
    """BeReal comment information"""
    comment_id: str
    post_id: str
    user_id: str
    username: str
    display_name: str
    content: str
    creation_time: datetime
    reaction_count: int
    reply_count: int
    parent_comment_id: Optional[str]
    mentioned_users: List[str]
    is_author: bool
    is_deleted: bool


@dataclass
class BeRealReaction:
    """BeReal reaction information"""
    reaction_id: str
    post_id: str
    user_id: str
    username: str
    display_name: str
    emoji: str
    reaction_type: str  # realmoji, instant_realmoji
    creation_time: datetime
    reaction_photo_url: Optional[str]  # for realmoji
    is_instant: bool


class BeRealCrawler(PlatformCrawler):
    """
    Advanced BeReal crawler for authentic social content monitoring.
    
    Features:
    - Real moments tracking
    - User profile analysis
    - Friend network mapping
    - Daily streak monitoring
    - Location-based discovery
    - Memory collection tracking
    - Reaction and comment analysis
    - Authenticity verification
    - Time-based content analysis
    - Social interaction tracking
    """
    
    def __init__(self, config: CrawlerConfig, vector_matcher=None):
        super().__init__(config, vector_matcher)
        self.platform_name = "bereal"
        self.base_url = "https://bereal.com"
        self.api_base_url = "https://mobile.bereal.com/api"
        
        # Rate limiting (BeReal has strict limits)
        self.requests_per_minute = 15
        self.min_delay = 4.0
        self.max_delay = 8.0
        
        # Content type mappings
        self.content_types = {
            'posts': self._crawl_posts,
            'users': self._crawl_users,
            'memories': self._crawl_memories,
            'comments': self._crawl_comments,
            'reactions': self._crawl_reactions,
            'discovery': self._crawl_discovery,
            'friends': self._crawl_friends,
            'search': self._crawl_search
        }
        
        # Tracking
        self.request_count = 0
        self.last_request_time = 0
        
        # Initialize session headers
        self._setup_session_headers()
    
    def _setup_session_headers(self):
        """Setup BeReal-specific headers"""
        self.session_headers.update({
            'Accept': 'application/json',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'en-US,en;q=0.9',
            'User-Agent': 'BeReal/8.0.1 (iPhone; iOS 16.0; Scale/3.00)',
            'Content-Type': 'application/json',
            'bereal-app-version-code': '14549',
            'bereal-signature': 'MToxNjY5NzQwMzI5OjEyMzQ1Njc4OTA=',
            'bereal-device-id': 'iPhone14,2',
            'bereal-timezone': 'Europe/Paris'
        })
    
    async def search_content(self, query: str, content_type: str = "posts", 
                           max_results: int = 50, filters: Dict[str, Any] = None) -> List[CrawlerResult]:
        """
        Search for content on BeReal.
        
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
            
            self.logger.info(f"Found {len(results)} BeReal {content_type} for query: {query}")
            return results
            
        except Exception as e:
            self.logger.error(f"Error searching BeReal content: {str(e)}")
            return []
    
    async def _crawl_posts(self, query: str, max_results: int, filters: Dict[str, Any] = None) -> List[CrawlerResult]:
        """Crawl BeReal posts"""
        try:
            results = []
            
            # BeReal doesn't have traditional search, so we simulate discovery
            # In reality, this would use authenticated API endpoints
            mock_posts = await self._get_mock_posts(query, max_results)
            
            for post_data in mock_posts:
                post = await self._parse_post_data(post_data)
                if post:
                    result = CrawlerResult(
                        url=f"{self.base_url}/post/{post.post_id}",
                        title=f"BeReal by @{post.username}",
                        content=post.caption,
                        metadata={
                            'post_data': asdict(post),
                            'platform': 'bereal',
                            'content_type': 'post',
                            'username': post.username,
                            'is_late': post.is_late,
                            'late_in_seconds': post.late_in_seconds,
                            'location': post.location,
                            'reaction_count': post.reaction_count,
                            'comment_count': post.comment_count,
                            'realmoji_count': post.realmoji_count,
                            'is_public': post.is_public,
                            'memory_type': post.memory_type,
                            'retake_count': post.retake_count,
                            'music_track': post.music_track,
                            'tags': post.tags
                        },
                        timestamp=post.creation_time,
                        similarity_score=0.0
                    )
                    results.append(result)
                    
                    # Rate limiting
                    await asyncio.sleep(random.uniform(self.min_delay, self.max_delay))
            
            return results
            
        except Exception as e:
            self.logger.error(f"Error crawling BeReal posts: {str(e)}")
            return []
    
    async def _crawl_users(self, query: str, max_results: int, filters: Dict[str, Any] = None) -> List[CrawlerResult]:
        """Crawl BeReal users"""
        try:
            results = []
            
            # Mock user data
            mock_users = await self._get_mock_users(query, max_results)
            
            for user_data in mock_users:
                user = await self._parse_user_data(user_data)
                if user:
                    result = CrawlerResult(
                        url=f"{self.base_url}/user/{user.username}",
                        title=f"@{user.username} ({user.display_name})",
                        content=user.bio or f"BeReal user with {user.posts_count} posts",
                        metadata={
                            'user_data': asdict(user),
                            'platform': 'bereal',
                            'content_type': 'user',
                            'username': user.username,
                            'display_name': user.display_name,
                            'follower_count': user.follower_count,
                            'following_count': user.following_count,
                            'friend_count': user.friend_count,
                            'posts_count': user.posts_count,
                            'streak_count': user.streak_count,
                            'is_verified': user.is_verified,
                            'is_public': user.is_public,
                            'location': user.location,
                            'country_code': user.country_code
                        },
                        timestamp=user.creation_date,
                        similarity_score=0.0
                    )
                    results.append(result)
                    
                    # Rate limiting
                    await asyncio.sleep(random.uniform(self.min_delay, self.max_delay))
            
            return results
            
        except Exception as e:
            self.logger.error(f"Error crawling BeReal users: {str(e)}")
            return []
    
    async def _crawl_memories(self, query: str, max_results: int, filters: Dict[str, Any] = None) -> List[CrawlerResult]:
        """Crawl BeReal memories"""
        try:
            results = []
            
            # Mock memory data
            mock_memories = await self._get_mock_memories(query, max_results)
            
            for memory_data in mock_memories:
                memory = await self._parse_memory_data(memory_data)
                if memory:
                    result = CrawlerResult(
                        url=f"{self.base_url}/memory/{memory.memory_id}",
                        title=f"Memory from {memory.date.strftime('%Y-%m-%d')}",
                        content=memory.caption or f"BeReal memory from {memory.date.strftime('%B %d, %Y')}",
                        metadata={
                            'memory_data': asdict(memory),
                            'platform': 'bereal',
                            'content_type': 'memory',
                            'memory_type': memory.memory_type,
                            'is_late': memory.is_late,
                            'late_in_seconds': memory.late_in_seconds,
                            'location': memory.location,
                            'is_favorite': memory.is_favorite,
                            'reaction_count': memory.reaction_count,
                            'comment_count': memory.comment_count,
                            'weather': memory.weather,
                            'temperature': memory.temperature,
                            'tags': memory.tags
                        },
                        timestamp=memory.date,
                        similarity_score=0.0
                    )
                    results.append(result)
                    
                    # Rate limiting
                    await asyncio.sleep(random.uniform(self.min_delay, self.max_delay))
            
            return results
            
        except Exception as e:
            self.logger.error(f"Error crawling BeReal memories: {str(e)}")
            return []
    
    async def _crawl_comments(self, query: str, max_results: int, filters: Dict[str, Any] = None) -> List[CrawlerResult]:
        """Crawl BeReal comments"""
        try:
            results = []
            
            # Mock comment data
            mock_comments = await self._get_mock_comments(query, max_results)
            
            for comment_data in mock_comments:
                comment = await self._parse_comment_data(comment_data)
                if comment:
                    result = CrawlerResult(
                        url=f"{self.base_url}/post/{comment.post_id}#comment-{comment.comment_id}",
                        title=f"Comment by @{comment.username}",
                        content=comment.content,
                        metadata={
                            'comment_data': asdict(comment),
                            'platform': 'bereal',
                            'content_type': 'comment',
                            'username': comment.username,
                            'post_id': comment.post_id,
                            'reaction_count': comment.reaction_count,
                            'reply_count': comment.reply_count,
                            'is_author': comment.is_author,
                            'mentioned_users': comment.mentioned_users
                        },
                        timestamp=comment.creation_time,
                        similarity_score=0.0
                    )
                    results.append(result)
                    
                    # Rate limiting
                    await asyncio.sleep(random.uniform(self.min_delay, self.max_delay))
            
            return results
            
        except Exception as e:
            self.logger.error(f"Error crawling BeReal comments: {str(e)}")
            return []
    
    async def _crawl_reactions(self, query: str, max_results: int, filters: Dict[str, Any] = None) -> List[CrawlerResult]:
        """Crawl BeReal reactions"""
        try:
            results = []
            
            # Mock reaction data
            mock_reactions = await self._get_mock_reactions(query, max_results)
            
            for reaction_data in mock_reactions:
                reaction = await self._parse_reaction_data(reaction_data)
                if reaction:
                    result = CrawlerResult(
                        url=f"{self.base_url}/post/{reaction.post_id}#reaction-{reaction.reaction_id}",
                        title=f"Reaction {reaction.emoji} by @{reaction.username}",
                        content=f"Reacted with {reaction.emoji} ({reaction.reaction_type})",
                        metadata={
                            'reaction_data': asdict(reaction),
                            'platform': 'bereal',
                            'content_type': 'reaction',
                            'username': reaction.username,
                            'post_id': reaction.post_id,
                            'emoji': reaction.emoji,
                            'reaction_type': reaction.reaction_type,
                            'is_instant': reaction.is_instant
                        },
                        timestamp=reaction.creation_time,
                        similarity_score=0.0
                    )
                    results.append(result)
                    
                    # Rate limiting
                    await asyncio.sleep(random.uniform(self.min_delay, self.max_delay))
            
            return results
            
        except Exception as e:
            self.logger.error(f"Error crawling BeReal reactions: {str(e)}")
            return []
    
    async def _crawl_discovery(self, query: str, max_results: int, filters: Dict[str, Any] = None) -> List[CrawlerResult]:
        """Crawl BeReal discovery feed"""
        try:
            results = []
            
            # Get discovery content
            discovery_content = await self._get_discovery_content(query, max_results, filters)
            
            for content in discovery_content:
                result = CrawlerResult(
                    url=content.get('url', ''),
                    title=f"[DISCOVERY] {content.get('title', 'Unknown')}",
                    content=content.get('description', ''),
                    metadata={
                        'discovery_data': content,
                        'platform': 'bereal',
                        'content_type': 'discovery',
                        'is_discovery': True,
                        'location': content.get('location'),
                        'popularity_score': content.get('popularity_score', 0)
                    },
                    timestamp=datetime.utcnow(),
                    similarity_score=0.0
                )
                results.append(result)
            
            return results[:max_results]
            
        except Exception as e:
            self.logger.error(f"Error crawling BeReal discovery: {str(e)}")
            return []
    
    async def _crawl_friends(self, query: str, max_results: int, filters: Dict[str, Any] = None) -> List[CrawlerResult]:
        """Crawl BeReal friends feed"""
        try:
            results = []
            
            # Get friends feed content
            friends_content = await self._get_friends_content(query, max_results, filters)
            
            for content in friends_content:
                result = CrawlerResult(
                    url=content.get('url', ''),
                    title=f"[FRIENDS] {content.get('title', 'Unknown')}",
                    content=content.get('description', ''),
                    metadata={
                        'friends_data': content,
                        'platform': 'bereal',
                        'content_type': 'friends_feed',
                        'is_friend_content': True,
                        'friend_level': content.get('friend_level', 'friend')
                    },
                    timestamp=datetime.utcnow(),
                    similarity_score=0.0
                )
                results.append(result)
            
            return results[:max_results]
            
        except Exception as e:
            self.logger.error(f"Error crawling BeReal friends: {str(e)}")
            return []
    
    async def _crawl_search(self, query: str, max_results: int, filters: Dict[str, Any] = None) -> List[CrawlerResult]:
        """General BeReal search"""
        try:
            results = []
            
            # Search across different content types
            posts = await self._crawl_posts(query, max_results // 3, filters)
            users = await self._crawl_users(query, max_results // 3, filters)
            memories = await self._crawl_memories(query, max_results // 3, filters)
            
            results.extend(posts)
            results.extend(users)
            results.extend(memories)
            
            return results[:max_results]
            
        except Exception as e:
            self.logger.error(f"Error performing BeReal search: {str(e)}")
            return []
    
    # Mock data generators (for demonstration)
    
    async def _get_mock_posts(self, query: str, max_results: int) -> List[Dict[str, Any]]:
        """Generate mock post data"""
        posts = []
        
        for i in range(min(max_results, 20)):
            creation_time = datetime.utcnow() - timedelta(hours=random.randint(1, 72))
            posts.append({
                'id': f'post_{i}',
                'user_id': f'user_{i}',
                'username': f'{query.lower() if query else "user"}{i}',
                'display_name': f'{query} User {i}' if query else f'User {i}',
                'caption': f'Being real with {query}!' if query else f'Post caption {i}',
                'creation_time': creation_time.isoformat(),
                'is_late': random.choice([True, False]),
                'late_in_seconds': random.randint(0, 3600) if random.choice([True, False]) else None,
                'reaction_count': random.randint(0, 50),
                'comment_count': random.randint(0, 20),
                'realmoji_count': random.randint(0, 30),
                'retake_count': random.randint(0, 5),
                'is_public': random.choice([True, False]),
                'is_discovery': random.choice([True, False]),
                'location': random.choice(['Paris, France', 'New York, NY', 'Tokyo, Japan', None]),
                'music_track': f'{query} Song' if query and random.choice([True, False]) else None,
                'tags': [query] if query else ['bereal', 'authentic'],
                'memory_type': random.choice(['daily', 'bonus', 'custom']),
                'device_type': random.choice(['iPhone', 'Android'])
            })
        
        return posts
    
    async def _get_mock_users(self, query: str, max_results: int) -> List[Dict[str, Any]]:
        """Generate mock user data"""
        users = []
        
        for i in range(min(max_results, 15)):
            creation_date = datetime.utcnow() - timedelta(days=random.randint(30, 730))
            users.append({
                'id': f'user_{i}',
                'username': f'{query.lower() if query else "user"}{i}',
                'display_name': f'{query} User {i}' if query else f'User {i}',
                'bio': f'Love {query}!' if query else f'BeReal user {i}',
                'location': random.choice(['Paris, France', 'New York, NY', 'Tokyo, Japan', None]),
                'follower_count': random.randint(10, 1000),
                'following_count': random.randint(10, 500),
                'friend_count': random.randint(5, 100),
                'posts_count': random.randint(1, 365),
                'streak_count': random.randint(0, 100),
                'creation_date': creation_date.isoformat(),
                'is_verified': random.choice([True, False]),
                'is_public': random.choice([True, False]),
                'country_code': random.choice(['FR', 'US', 'JP', 'GB', 'DE'])
            })
        
        return users
    
    async def _get_mock_memories(self, query: str, max_results: int) -> List[Dict[str, Any]]:
        """Generate mock memory data"""
        memories = []
        
        for i in range(min(max_results, 25)):
            memory_date = datetime.utcnow() - timedelta(days=random.randint(1, 365))
            memories.append({
                'id': f'memory_{i}',
                'user_id': f'user_{i}',
                'date': memory_date.isoformat(),
                'caption': f'Memory with {query}' if query else f'Memory {i}',
                'location': random.choice(['Paris, France', 'New York, NY', 'Tokyo, Japan', None]),
                'is_late': random.choice([True, False]),
                'late_in_seconds': random.randint(0, 3600) if random.choice([True, False]) else None,
                'memory_type': random.choice(['daily', 'bonus', 'custom']),
                'is_favorite': random.choice([True, False]),
                'reaction_count': random.randint(0, 30),
                'comment_count': random.randint(0, 10),
                'weather': random.choice(['sunny', 'cloudy', 'rainy', None]),
                'temperature': random.randint(-10, 35) if random.choice([True, False]) else None,
                'tags': [query] if query else ['memory', 'throwback']
            })
        
        return memories
    
    async def _get_mock_comments(self, query: str, max_results: int) -> List[Dict[str, Any]]:
        """Generate mock comment data"""
        comments = []
        
        for i in range(min(max_results, 30)):
            creation_time = datetime.utcnow() - timedelta(hours=random.randint(1, 48))
            comments.append({
                'id': f'comment_{i}',
                'post_id': f'post_{i % 10}',
                'user_id': f'user_{i}',
                'username': f'{query.lower() if query else "user"}{i}',
                'display_name': f'{query} User {i}' if query else f'User {i}',
                'content': f'Great {query} post!' if query else f'Comment content {i}',
                'creation_time': creation_time.isoformat(),
                'reaction_count': random.randint(0, 10),
                'reply_count': random.randint(0, 5),
                'is_author': random.choice([True, False]),
                'mentioned_users': [f'user_{random.randint(0, 100)}'] if random.choice([True, False]) else []
            })
        
        return comments
    
    async def _get_mock_reactions(self, query: str, max_results: int) -> List[Dict[str, Any]]:
        """Generate mock reaction data"""
        reactions = []
        emojis = ['😍', '😂', '🔥', '👏', '💯', '😱', '🥰', '😭']
        
        for i in range(min(max_results, 40)):
            creation_time = datetime.utcnow() - timedelta(minutes=random.randint(1, 1440))
            reactions.append({
                'id': f'reaction_{i}',
                'post_id': f'post_{i % 10}',
                'user_id': f'user_{i}',
                'username': f'{query.lower() if query else "user"}{i}',
                'display_name': f'{query} User {i}' if query else f'User {i}',
                'emoji': random.choice(emojis),
                'reaction_type': random.choice(['realmoji', 'instant_realmoji']),
                'creation_time': creation_time.isoformat(),
                'is_instant': random.choice([True, False])
            })
        
        return reactions
    
    async def _get_discovery_content(self, query: str, max_results: int, filters: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """Get discovery feed content"""
        content = []
        
        for i in range(min(max_results, 15)):
            content.append({
                'title': f'Discovery: {query} {i}' if query else f'Discovery Content {i}',
                'url': f'{self.base_url}/discovery/{i}',
                'description': f'Discover {query} content' if query else f'Discovery description {i}',
                'location': random.choice(['Paris, France', 'New York, NY', 'Tokyo, Japan']),
                'popularity_score': random.randint(0, 100)
            })
        
        return content
    
    async def _get_friends_content(self, query: str, max_results: int, filters: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """Get friends feed content"""
        content = []
        
        for i in range(min(max_results, 20)):
            content.append({
                'title': f'Friend: {query} {i}' if query else f'Friend Content {i}',
                'url': f'{self.base_url}/friends/{i}',
                'description': f'Friend {query} activity' if query else f'Friend description {i}',
                'friend_level': random.choice(['friend', 'close_friend', 'best_friend'])
            })
        
        return content
    
    # Parser methods
    
    async def _parse_post_data(self, post_data: Dict[str, Any]) -> Optional[BeRealPost]:
        """Parse post data"""
        try:
            creation_time = datetime.fromisoformat(post_data.get('creation_time', datetime.utcnow().isoformat()).replace('Z', '+00:00'))
            
            post = BeRealPost(
                post_id=post_data.get('id', ''),
                user_id=post_data.get('user_id', ''),
                username=post_data.get('username', ''),
                display_name=post_data.get('display_name', ''),
                caption=post_data.get('caption', ''),
                primary_photo_url='',
                secondary_photo_url='',
                location=post_data.get('location'),
                latitude=post_data.get('latitude'),
                longitude=post_data.get('longitude'),
                creation_time=creation_time,
                is_late=post_data.get('is_late', False),
                late_in_seconds=post_data.get('late_in_seconds'),
                reaction_count=post_data.get('reaction_count', 0),
                comment_count=post_data.get('comment_count', 0),
                realmoji_count=post_data.get('realmoji_count', 0),
                retake_count=post_data.get('retake_count', 0),
                is_public=post_data.get('is_public', False),
                is_discovery=post_data.get('is_discovery', False),
                music_track=post_data.get('music_track'),
                music_artist=post_data.get('music_artist'),
                tags=post_data.get('tags', []),
                mentioned_users=post_data.get('mentioned_users', []),
                visibility=post_data.get('visibility', 'friends'),
                device_type=post_data.get('device_type', ''),
                app_version=post_data.get('app_version', ''),
                is_screenshot=post_data.get('is_screenshot', False),
                screenshot_count=post_data.get('screenshot_count', 0),
                memory_type=post_data.get('memory_type', 'daily')
            )
            
            return post
            
        except Exception as e:
            self.logger.error(f"Error parsing post data: {str(e)}")
            return None
    
    async def _parse_user_data(self, user_data: Dict[str, Any]) -> Optional[BeRealUser]:
        """Parse user data"""
        try:
            creation_date = datetime.fromisoformat(user_data.get('creation_date', datetime.utcnow().isoformat()).replace('Z', '+00:00'))
            
            user = BeRealUser(
                user_id=user_data.get('id', ''),
                username=user_data.get('username', ''),
                display_name=user_data.get('display_name', ''),
                profile_picture_url='',
                bio=user_data.get('bio'),
                location=user_data.get('location'),
                birthday=None,
                phone_number=user_data.get('phone_number'),
                follower_count=user_data.get('follower_count', 0),
                following_count=user_data.get('following_count', 0),
                friend_count=user_data.get('friend_count', 0),
                posts_count=user_data.get('posts_count', 0),
                streak_count=user_data.get('streak_count', 0),
                creation_date=creation_date,
                last_post_time=None,
                is_verified=user_data.get('is_verified', False),
                is_public=user_data.get('is_public', False),
                is_discovering=user_data.get('is_discovering', False),
                time_zone=user_data.get('time_zone', 'UTC'),
                country_code=user_data.get('country_code', ''),
                phone_country_code=user_data.get('phone_country_code', ''),
                relationship_status=user_data.get('relationship_status'),
                notification_settings=user_data.get('notification_settings', {}),
                privacy_settings=user_data.get('privacy_settings', {}),
                blocked_users=user_data.get('blocked_users', []),
                close_friends=user_data.get('close_friends', [])
            )
            
            return user
            
        except Exception as e:
            self.logger.error(f"Error parsing user data: {str(e)}")
            return None
    
    async def _parse_memory_data(self, memory_data: Dict[str, Any]) -> Optional[BeRealMemory]:
        """Parse memory data"""
        try:
            memory_date = datetime.fromisoformat(memory_data.get('date', datetime.utcnow().isoformat()).replace('Z', '+00:00'))
            
            memory = BeRealMemory(
                memory_id=memory_data.get('id', ''),
                user_id=memory_data.get('user_id', ''),
                date=memory_date,
                primary_photo_url='',
                secondary_photo_url='',
                location=memory_data.get('location'),
                caption=memory_data.get('caption'),
                is_late=memory_data.get('is_late', False),
                late_in_seconds=memory_data.get('late_in_seconds'),
                memory_type=memory_data.get('memory_type', 'daily'),
                is_favorite=memory_data.get('is_favorite', False),
                reaction_count=memory_data.get('reaction_count', 0),
                comment_count=memory_data.get('comment_count', 0),
                music_track=memory_data.get('music_track'),
                tags=memory_data.get('tags', []),
                weather=memory_data.get('weather'),
                temperature=memory_data.get('temperature')
            )
            
            return memory
            
        except Exception as e:
            self.logger.error(f"Error parsing memory data: {str(e)}")
            return None
    
    async def _parse_comment_data(self, comment_data: Dict[str, Any]) -> Optional[BeRealComment]:
        """Parse comment data"""
        try:
            creation_time = datetime.fromisoformat(comment_data.get('creation_time', datetime.utcnow().isoformat()).replace('Z', '+00:00'))
            
            comment = BeRealComment(
                comment_id=comment_data.get('id', ''),
                post_id=comment_data.get('post_id', ''),
                user_id=comment_data.get('user_id', ''),
                username=comment_data.get('username', ''),
                display_name=comment_data.get('display_name', ''),
                content=comment_data.get('content', ''),
                creation_time=creation_time,
                reaction_count=comment_data.get('reaction_count', 0),
                reply_count=comment_data.get('reply_count', 0),
                parent_comment_id=comment_data.get('parent_comment_id'),
                mentioned_users=comment_data.get('mentioned_users', []),
                is_author=comment_data.get('is_author', False),
                is_deleted=comment_data.get('is_deleted', False)
            )
            
            return comment
            
        except Exception as e:
            self.logger.error(f"Error parsing comment data: {str(e)}")
            return None
    
    async def _parse_reaction_data(self, reaction_data: Dict[str, Any]) -> Optional[BeRealReaction]:
        """Parse reaction data"""
        try:
            creation_time = datetime.fromisoformat(reaction_data.get('creation_time', datetime.utcnow().isoformat()).replace('Z', '+00:00'))
            
            reaction = BeRealReaction(
                reaction_id=reaction_data.get('id', ''),
                post_id=reaction_data.get('post_id', ''),
                user_id=reaction_data.get('user_id', ''),
                username=reaction_data.get('username', ''),
                display_name=reaction_data.get('display_name', ''),
                emoji=reaction_data.get('emoji', ''),
                reaction_type=reaction_data.get('reaction_type', 'realmoji'),
                creation_time=creation_time,
                reaction_photo_url=reaction_data.get('reaction_photo_url'),
                is_instant=reaction_data.get('is_instant', False)
            )
            
            return reaction
            
        except Exception as e:
            self.logger.error(f"Error parsing reaction data: {str(e)}")
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
        """Extract metadata from BeReal content"""
        try:
            # Parse BeReal URL
            parsed_url = urlparse(url)
            
            metadata = {
                'platform': 'bereal',
                'url': url,
                'extracted_at': datetime.utcnow().isoformat()
            }
            
            # Handle BeReal URLs
            if 'bereal.com' in parsed_url.netloc:
                path_parts = parsed_url.path.strip('/').split('/')
                
                if len(path_parts) >= 2:
                    content_type = path_parts[0]  # post, user, memory
                    content_id = path_parts[1]
                    
                    metadata.update({
                        'content_type': content_type,
                        'content_id': content_id
                    })
                    
                    # Extract additional info from fragment
                    if parsed_url.fragment:
                        if 'comment-' in parsed_url.fragment:
                            metadata['comment_id'] = parsed_url.fragment.replace('comment-', '')
                        elif 'reaction-' in parsed_url.fragment:
                            metadata['reaction_id'] = parsed_url.fragment.replace('reaction-', '')
            
            return metadata
            
        except Exception as e:
            self.logger.error(f"Error extracting BeReal metadata: {str(e)}")
            return {'error': str(e)}
    
    def get_platform_info(self) -> Dict[str, Any]:
        """Get BeReal platform information"""
        return {
            'platform_name': 'BeReal',
            'base_url': self.base_url,
            'api_base_url': self.api_base_url,
            'supported_content_types': list(self.content_types.keys()),
            'rate_limits': {
                'requests_per_minute': self.requests_per_minute,
                'min_delay': self.min_delay,
                'max_delay': self.max_delay
            },
            'features': [
                'Real moments tracking',
                'User profile analysis',
                'Friend network mapping',
                'Daily streak monitoring',
                'Location-based discovery',
                'Memory collection tracking',
                'Reaction and comment analysis',
                'Authenticity verification',
                'Time-based content analysis',
                'Social interaction tracking'
            ],
            'authentication': {
                'required': True,
                'type': 'OAuth 2.0',
                'scope': 'Private content access'
            },
            'content_characteristics': {
                'authentic_focus': True,
                'time_sensitive': True,
                'dual_camera': True,
                'social_verification': True
            },
            'limitations': [
                'Requires authentication',
                'Limited public content',
                'Strict rate limiting',
                'Content expires after 24 hours',
                'No traditional search functionality'
            ]
        }
