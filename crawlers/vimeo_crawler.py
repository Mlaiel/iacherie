"""
Vimeo Content Crawler
Advanced industrial-grade Vimeo crawler for video content protection and analytics
Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 - All rights reserved
"""

import asyncio
import json
import re
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Set, Any
from urllib.parse import urljoin, urlparse

import aiohttp
import pandas as pd
from pydantic import BaseModel, Field

from ..base_crawler import BaseCrawler
from ....core.config import get_settings
from ....core.logging import get_logger
from ....models.content import ContentMatch, PlatformContent
from ....utils.rate_limiter import RateLimiter
from ....security.encryption import encrypt_sensitive_data

logger = get_logger(__name__)
settings = get_settings()


class VimeoVideo(BaseModel):
    """Vimeo Video data model"""
    video_id: str
    title: str
    description: str
    duration: int  # in seconds
    view_count: int = 0
    like_count: int = 0
    comment_count: int = 0
    download_count: int = 0
    created_at: datetime
    modified_at: Optional[datetime] = None
    video_url: str
    embed_url: str
    thumbnail_url: Optional[str] = None
    creator_name: str
    creator_url: str
    tags: List[str] = Field(default_factory=list)
    categories: List[str] = Field(default_factory=list)
    language: Optional[str] = None
    license: Optional[str] = None
    privacy_status: str = "public"
    quality_available: List[str] = Field(default_factory=list)
    file_size: Optional[int] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


class VimeoChannel(BaseModel):
    """Vimeo Channel/User data model"""
    user_id: str
    name: str
    bio: str
    location: Optional[str] = None
    website: Optional[str] = None
    profile_url: str
    avatar_url: Optional[str] = None
    follower_count: int = 0
    following_count: int = 0
    video_count: int = 0
    total_views: int = 0
    account_type: str = "basic"  # basic, plus, pro, business
    verified: bool = False
    created_at: datetime


class VimeoAlbum(BaseModel):
    """Vimeo Album/Showcase data model"""
    album_id: str
    title: str
    description: str
    video_count: int
    creator_name: str
    created_at: datetime
    modified_at: Optional[datetime] = None
    album_url: str
    thumbnail_url: Optional[str] = None
    privacy_status: str = "public"


class VimeoCrawler(BaseCrawler):
    """
    Advanced Vimeo crawler for comprehensive video content monitoring
    
    Features:
    - Video content analysis with AI-powered categorization
    - Creator profile monitoring and analytics
    - Album/showcase tracking
    - Advanced video quality analysis
    - Copyright infringement detection
    - Engagement metrics and trend analysis
    - Live stream monitoring
    - API rate limiting with exponential backoff
    """
    
    def __init__(self):
        super().__init__()
        self.platform = "vimeo"
        self.base_url = "https://vimeo.com"
        self.api_base = "https://api.vimeo.com"
        self.rate_limiter = RateLimiter(
            requests_per_minute=1000,  # Vimeo's API limit
            requests_per_hour=5000
        )
        self.session_headers = {
            'User-Agent': 'IA-Influencer-Agent/2.0 (Content Protection)',
            'Accept': 'application/vnd.vimeo.*+json;version=3.4',
            'Content-Type': 'application/json'
        }
        
    async def authenticate(self, access_token: str) -> bool:
        """Authenticate with Vimeo API using OAuth2"""



        try:
            self.session_headers['Authorization'] = f'Bearer {access_token}'
            
            async with aiohttp.ClientSession(headers=self.session_headers) as session:
                async with session.get(f"{self.api_base}/me") as response:
                    if response.status == 200:
                        user_data = await response.json()
                        logger.info(f"Authenticated as Vimeo user: {user_data.get('name')}")
                        return True
                    else:
                        logger.error(f"Vimeo authentication failed: {response.status}")
                        return False
                        
        except Exception as e:
            logger.error(f"Vimeo authentication error: {str(e)}")
            return False
    
    async def search_videos(
        self,
        query: str,
        sort: str = "relevant",
        direction: str = "desc",
        limit: int = 100,
        filters: Optional[Dict] = None
    ) -> List[Dict]:
        """
        Search Vimeo videos with advanced filtering
        
        Args:
            query: Search query
            sort: Sort method (relevant, alphabetical, date, duration, plays)
            direction: Sort direction (asc, desc)
            limit: Maximum results to return
            filters: Additional search filters
            
        Returns:
            List of matching videos
        """
        await self.rate_limiter.wait()
        
        try:
            search_params = {
                'query': query,
                'sort': sort,
                'direction': direction,
                'per_page': min(limit, 50),  # Vimeo API limit per request
                'fields': 'uri,name,description,duration,created_time,modified_time,link,embed,pictures,stats,tags,categories,language,license,privacy,files'
            }
            
            if filters:
                # Add filter support for duration, upload_date, etc.
                if 'duration' in filters:
                    search_params['filter'] = f"duration={filters['duration']}"
                if 'upload_date' in filters:
                    search_params['filter_upload_date'] = filters['upload_date']
            
            endpoint = f"{self.api_base}/videos"
            all_videos = []
            page = 1
            
            while len(all_videos) < limit:
                search_params['page'] = page
                
                async with aiohttp.ClientSession(headers=self.session_headers) as session:
                    async with session.get(endpoint, params=search_params) as response:
                        if response.status == 200:
                            data = await response.json()
                            videos = data.get('data', [])
                            
                            if not videos:
                                break
                                
                            all_videos.extend(videos)
                            
                            # Check if we have more pages
                            if data.get('paging', {}).get('next') is None:
                                break
                                
                            page += 1
                            
                            # Rate limiting between pages
                            await asyncio.sleep(0.2)
                        else:
                            logger.error(f"Vimeo search failed: {response.status}")
                            break
            
            logger.info(f"Found {len(all_videos)} videos for query: {query}")
            return all_videos[:limit]
            
        except Exception as e:
            logger.error(f"Vimeo search error: {str(e)}")
            return []
    
    async def get_video_details(self, video_id: str) -> Optional[VimeoVideo]:
        """Get detailed information about a specific video"""
        await self.rate_limiter.wait()
        
        try:
            # Clean video ID (remove /videos/ prefix if present)
            if video_id.startswith('/videos/'):
                video_id = video_id.replace('/videos/', '')
            
            endpoint = f"{self.api_base}/videos/{video_id}"
            params = {
                'fields': 'uri,name,description,duration,created_time,modified_time,link,embed,pictures,stats,tags,categories,language,license,privacy,files,user'
            }
            
            async with aiohttp.ClientSession(headers=self.session_headers) as session:
                async with session.get(endpoint, params=params) as response:
                    if response.status == 200:
                        video_data = await response.json()
                        return await self._parse_video_data(video_data)
                    else:
                        logger.error(f"Failed to get video details: {response.status}")
                        return None
                        
        except Exception as e:
            logger.error(f"Error getting video details: {str(e)}")
            return None
    
    async def get_user_profile(self, user_id: str) -> Optional[VimeoChannel]:
        """Get detailed user profile information"""
        await self.rate_limiter.wait()
        
        try:
            endpoint = f"{self.api_base}/users/{user_id}"
            params = {
                'fields': 'uri,name,bio,location,link,pictures,websites,metadata,account'
            }
            
            async with aiohttp.ClientSession(headers=self.session_headers) as session:
                async with session.get(endpoint, params=params) as response:
                    if response.status == 200:
                        user_data = await response.json()
                        return await self._parse_user_data(user_data)
                    else:
                        logger.error(f"Failed to get user profile: {response.status}")
                        return None
                        
        except Exception as e:
            logger.error(f"Error getting user profile: {str(e)}")
            return None
    
    async def get_user_videos(self, user_id: str, limit: int = 100) -> List[VimeoVideo]:
        """Get all videos from a specific user"""
        await self.rate_limiter.wait()
        
        try:
            endpoint = f"{self.api_base}/users/{user_id}/videos"
            params = {
                'per_page': min(limit, 50),
                'fields': 'uri,name,description,duration,created_time,stats,tags,link,embed,pictures',
                'sort': 'date',
                'direction': 'desc'
            }
            
            videos = []
            page = 1
            
            while len(videos) < limit:
                params['page'] = page
                
                async with aiohttp.ClientSession(headers=self.session_headers) as session:
                    async with session.get(endpoint, params=params) as response:
                        if response.status == 200:
                            data = await response.json()
                            video_list = data.get('data', [])
                            
                            if not video_list:
                                break
                            
                            for video_data in video_list:
                                video = await self._parse_video_data(video_data)
                                if video:
                                    videos.append(video)
                            
                            if data.get('paging', {}).get('next') is None:
                                break
                                
                            page += 1
                            await asyncio.sleep(0.2)
                        else:
                            logger.error(f"Failed to get user videos: {response.status}")
                            break
            
            logger.info(f"Retrieved {len(videos)} videos from user {user_id}")
            return videos[:limit]
            
        except Exception as e:
            logger.error(f"Error getting user videos: {str(e)}")
            return []
    
    async def monitor_content_infringement(
        self,
        protected_content: Dict,
        similarity_threshold: float = 0.8
    ) -> List[ContentMatch]:
        """
        Monitor Vimeo for potential copyright infringement
        
        Args:
            protected_content: Content to protect
            similarity_threshold: Minimum similarity for match detection
            
        Returns:
            List of potential copyright matches
        """
        matches = []
        
        try:
            # Generate search queries from protected content
            search_queries = self._generate_search_queries(protected_content)
            
            for query in search_queries:
                results = await self.search_videos(query, limit=50)
                
                for result in results:
                    video = await self._parse_video_data(result)
                    if video:
                        similarity_score = await self._calculate_content_similarity(
                            protected_content, video
                        )
                        
                        if similarity_score >= similarity_threshold:
                            match = ContentMatch(
                                platform="vimeo",
                                content_id=video.video_id,
                                url=video.video_url,
                                title=video.title,
                                description=video.description,
                                creator=video.creator_name,
                                similarity_score=similarity_score,
                                detection_date=datetime.utcnow(),
                                content_type="video",
                                metadata={
                                    'duration': video.duration,
                                    'view_count': video.view_count,
                                    'like_count': video.like_count,
                                    'embed_url': video.embed_url,
                                    'quality_available': video.quality_available
                                }
                            )
                            matches.append(match)
            
            logger.info(f"Found {len(matches)} potential copyright matches on Vimeo")
            return matches
            
        except Exception as e:
            logger.error(f"Error monitoring Vimeo content infringement: {str(e)}")
            return []
    
    async def analyze_video_performance(self, video_id: str) -> Dict[str, Any]:
        """
        Analyze video performance metrics and engagement
        
        Args:
            video_id: Vimeo video ID
            
        Returns:
            Comprehensive performance analysis
        """



        try:
            video = await self.get_video_details(video_id)
            if not video:
                return {}
            
            # Calculate performance metrics
            engagement_rate = (video.like_count + video.comment_count) / max(video.view_count, 1)
            views_per_day = video.view_count / max((datetime.utcnow() - video.created_at).days, 1)
            
            performance_analysis = {
                'video_id': video.video_id,
                'basic_metrics': {
                    'views': video.view_count,
                    'likes': video.like_count,
                    'comments': video.comment_count,
                    'downloads': video.download_count
                },
                'engagement_metrics': {
                    'engagement_rate': engagement_rate,
                    'views_per_day': views_per_day,
                    'virality_score': self._calculate_virality_score(video)
                },
                'content_analysis': {
                    'duration_category': self._categorize_duration(video.duration),
                    'title_optimization_score': self._analyze_title_optimization(video.title),
                    'description_quality_score': self._analyze_description_quality(video.description),
                    'tag_effectiveness': len(video.tags) * 0.1 if video.tags else 0
                },
                'technical_quality': {
                    'quality_available': video.quality_available,
                    'file_size': video.file_size,
                    'thumbnail_quality': 'high' if video.thumbnail_url else 'none'
                },
                'performance_category': self._categorize_performance(video),
                'optimization_suggestions': self._generate_optimization_suggestions(video)
            }
            
            return performance_analysis
            
        except Exception as e:
            logger.error(f"Error analyzing video performance: {str(e)}")
            return {}
    
    async def get_trending_videos(
        self,
        category: str = None,
        time_period: str = "week",
        limit: int = 50
    ) -> List[VimeoVideo]:
        """
        Get trending videos on Vimeo
        
        Args:
            category: Video category filter
            time_period: Time period (day, week, month, year, all)
            limit: Maximum videos to return
            
        Returns:
            List of trending videos
        """



        try:
            # Vimeo doesn't have a direct trending API, so we'll use popular/staff picks
            endpoint = f"{self.api_base}/channels/staffpicks/videos"
            params = {
                'per_page': min(limit, 50),
                'fields': 'uri,name,description,duration,created_time,stats,tags,link,embed,pictures,user',
                'sort': 'manual',
                'direction': 'desc'
            }
            
            videos = []
            
            async with aiohttp.ClientSession(headers=self.session_headers) as session:
                async with session.get(endpoint, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        for video_data in data.get('data', []):
                            video = await self._parse_video_data(video_data)
                            if video:
                                videos.append(video)
                        
                        logger.info(f"Retrieved {len(videos)} trending videos")
                        return videos
                    else:
                        logger.error(f"Failed to get trending videos: {response.status}")
                        return []
                        
        except Exception as e:
            logger.error(f"Error getting trending videos: {str(e)}")
            return []
    
    async def bulk_video_analysis(self, video_ids: List[str]) -> List[Dict[str, Any]]:
        """Analyze multiple videos in bulk for efficiency"""
        results = []
        
        # Process videos in batches to respect rate limits
        batch_size = 10
        for i in range(0, len(video_ids), batch_size):
            batch = video_ids[i:i + batch_size]
            
            batch_tasks = [self.analyze_video_performance(video_id) for video_id in batch]
            batch_results = await asyncio.gather(*batch_tasks, return_exceptions=True)
            
            for result in batch_results:
                if isinstance(result, dict) and result:
                    results.append(result)
                elif isinstance(result, Exception):
                    logger.error(f"Error in bulk analysis: {str(result)}")
            
            # Rate limiting between batches
            await asyncio.sleep(1)
        
        return results
    
    async def _parse_video_data(self, video_data: Dict) -> Optional[VimeoVideo]:
        """Parse Vimeo API video data into VimeoVideo model"""



        try:
            # Extract video ID from URI
            video_id = video_data.get('uri', '').split('/')[-1]
            
            # Parse user information
            user_info = video_data.get('user', {})
            creator_name = user_info.get('name', 'Unknown')
            creator_url = user_info.get('link', '')
            
            # Parse stats
            stats = video_data.get('stats', {})
            
            # Parse tags
            tags = [tag.get('name', '') for tag in video_data.get('tags', [])]
            
            # Parse categories
            categories = [cat.get('name', '') for cat in video_data.get('categories', [])]
            
            # Parse quality options
            files = video_data.get('files', [])
            quality_available = [f.get('quality', '') for f in files if f.get('quality')]
            
            # Parse thumbnail
            pictures = video_data.get('pictures', {})
            thumbnail_url = None
            if pictures and pictures.get('sizes'):
                # Get the largest thumbnail
                largest_thumb = max(pictures['sizes'], key=lambda x: x.get('width', 0))
                thumbnail_url = largest_thumb.get('link')
            
            video = VimeoVideo(
                video_id=video_id,
                title=video_data.get('name', ''),
                description=video_data.get('description', ''),
                duration=video_data.get('duration', 0),
                view_count=stats.get('plays', 0),
                like_count=stats.get('likes', 0),
                comment_count=stats.get('comments', 0),
                download_count=stats.get('downloads', 0),
                created_at=datetime.fromisoformat(video_data['created_time'].replace('Z', '+00:00')),
                modified_at=datetime.fromisoformat(video_data['modified_time'].replace('Z', '+00:00')) if video_data.get('modified_time') else None,
                video_url=video_data.get('link', ''),
                embed_url=video_data.get('embed', {}).get('html', ''),
                thumbnail_url=thumbnail_url,
                creator_name=creator_name,
                creator_url=creator_url,
                tags=tags,
                categories=categories,
                language=video_data.get('language'),
                license=video_data.get('license'),
                privacy_status=video_data.get('privacy', {}).get('view', 'public'),
                quality_available=quality_available,
                file_size=sum(f.get('size', 0) for f in files),
                metadata={
                    'embed_domains': video_data.get('privacy', {}).get('embed', 'public'),
                    'password_protected': video_data.get('password') is not None,
                    'content_rating': video_data.get('content_rating', [])
                }
            )
            
            return video
            
        except Exception as e:
            logger.error(f"Error parsing video data: {str(e)}")
            return None
    
    async def _parse_user_data(self, user_data: Dict) -> Optional[VimeoChannel]:
        """Parse Vimeo API user data into VimeoChannel model"""



        try:
            user_id = user_data.get('uri', '').split('/')[-1]
            
            # Parse metadata
            metadata = user_data.get('metadata', {})
            connections = metadata.get('connections', {})
            
            # Parse pictures
            pictures = user_data.get('pictures', {})
            avatar_url = None
            if pictures and pictures.get('sizes'):
                largest_avatar = max(pictures['sizes'], key=lambda x: x.get('width', 0))
                avatar_url = largest_avatar.get('link')
            
            # Extract website
            websites = user_data.get('websites', [])
            website = websites[0].get('link') if websites else None
            
            channel = VimeoChannel(
                user_id=user_id,
                name=user_data.get('name', ''),
                bio=user_data.get('bio', ''),
                location=user_data.get('location', ''),
                website=website,
                profile_url=user_data.get('link', ''),
                avatar_url=avatar_url,
                follower_count=connections.get('followers', {}).get('total', 0),
                following_count=connections.get('following', {}).get('total', 0),
                video_count=connections.get('videos', {}).get('total', 0),
                total_views=metadata.get('public_videos', {}).get('total', 0),
                account_type=user_data.get('account', 'basic'),
                verified=user_data.get('verified', False),
                created_at=datetime.fromisoformat(user_data['created_time'].replace('Z', '+00:00'))
            )
            
            return channel
            
        except Exception as e:
            logger.error(f"Error parsing user data: {str(e)}")
            return None
    
    def _generate_search_queries(self, protected_content: Dict) -> List[str]:
        """Generate search queries for content protection"""
        queries = []
        
        if 'title' in protected_content:
            queries.append(protected_content['title'])
        
        if 'description' in protected_content:
            # Extract key phrases from description
            words = protected_content['description'].split()
            if len(words) > 3:
                queries.append(' '.join(words[:8]))
        
        if 'tags' in protected_content:
            queries.extend(protected_content['tags'][:3])
        
        return queries[:5]
    
    async def _calculate_content_similarity(
        self,
        protected_content: Dict,
        video: VimeoVideo
    ) -> float:
        """Calculate similarity between protected content and Vimeo video"""
        from difflib import SequenceMatcher
        
        similarity_scores = []
        
        # Title similarity
        if 'title' in protected_content and video.title:
            title_similarity = SequenceMatcher(
                None,
                protected_content['title'].lower(),
                video.title.lower()
            ).ratio()
            similarity_scores.append(title_similarity * 0.4)
        
        # Description similarity
        if 'description' in protected_content and video.description:
            desc_similarity = SequenceMatcher(
                None,
                protected_content['description'].lower(),
                video.description.lower()
            ).ratio()
            similarity_scores.append(desc_similarity * 0.3)
        
        # Tag similarity
        if 'tags' in protected_content and video.tags:
            protected_tags = set(tag.lower() for tag in protected_content['tags'])
            video_tags = set(tag.lower() for tag in video.tags)
            
            if protected_tags and video_tags:
                tag_similarity = len(protected_tags.intersection(video_tags)) / len(protected_tags.union(video_tags))
                similarity_scores.append(tag_similarity * 0.3)
        
        return sum(similarity_scores) if similarity_scores else 0.0
    
    def _calculate_virality_score(self, video: VimeoVideo) -> float:
        """Calculate video virality score"""
        days_since_upload = (datetime.utcnow() - video.created_at).days
        if days_since_upload == 0:
            days_since_upload = 1
        
        views_per_day = video.view_count / days_since_upload
        engagement_ratio = (video.like_count + video.comment_count) / max(video.view_count, 1)
        
        return min(views_per_day * engagement_ratio * 100, 1000)
    
    def _categorize_duration(self, duration: int) -> str:
        """Categorize video duration"""
        if duration < 60:
            return "short"
        elif duration < 300:
            return "medium"
        elif duration < 1800:
            return "long"
        else:
            return "extended"
    
    def _analyze_title_optimization(self, title: str) -> float:
        """Analyze title optimization score"""
        if not title:
            return 0.0
        
        score = 0.0
        
        # Length optimization (50-60 characters is optimal)
        if 30 <= len(title) <= 70:
            score += 0.3
        
        # Word count (5-10 words is optimal)
        word_count = len(title.split())
        if 3 <= word_count <= 12:
            score += 0.3
        
        # Contains keywords/emotional words
        emotional_words = ['amazing', 'incredible', 'beautiful', 'stunning', 'epic', 'ultimate']
        if any(word.lower() in title.lower() for word in emotional_words):
            score += 0.2
        
        # No excessive punctuation
        punct_count = sum(1 for char in title if char in '!?.:;')
        if punct_count <= 3:
            score += 0.2
        
        return min(score, 1.0)
    
    def _analyze_description_quality(self, description: str) -> float:
        """Analyze description quality score"""
        if not description:
            return 0.0
        
        score = 0.0
        
        # Length (125-150 words is optimal)
        word_count = len(description.split())
        if 50 <= word_count <= 200:
            score += 0.4
        
        # Contains call-to-action
        cta_phrases = ['subscribe', 'like', 'comment', 'share', 'follow', 'check out']
        if any(phrase in description.lower() for phrase in cta_phrases):
            score += 0.3
        
        # Contains links or mentions
        if 'http' in description or '@' in description:
            score += 0.2
        
        # Good formatting (line breaks, structure)
        if '\n' in description or len(description.split('.')) > 2:
            score += 0.1
        
        return min(score, 1.0)
    
    def _categorize_performance(self, video: VimeoVideo) -> str:
        """Categorize video performance level"""
        views = video.view_count
        engagement = video.like_count + video.comment_count
        
        if views > 100000 and engagement > 1000:
            return "viral"
        elif views > 10000 and engagement > 100:
            return "high"
        elif views > 1000 and engagement > 10:
            return "medium"
        else:
            return "low"
    
    def _generate_optimization_suggestions(self, video: VimeoVideo) -> List[str]:
        """Generate optimization suggestions for video"""
        suggestions = []
        
        if len(video.title) < 30:
            suggestions.append("Consider expanding the title for better SEO")
        
        if len(video.description) < 100:
            suggestions.append("Add more detailed description for better discoverability")
        
        if len(video.tags) < 5:
            suggestions.append("Add more relevant tags to improve categorization")
        
        if not video.thumbnail_url:
            suggestions.append("Add a custom thumbnail to increase click-through rate")
        
        if video.view_count < 100:
            suggestions.append("Promote video on social media for initial traction")
        
        return suggestions
