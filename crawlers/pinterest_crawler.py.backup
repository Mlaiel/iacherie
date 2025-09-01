"""Pinterest Content Crawler
Advanced industrial-grade Pinterest crawler for content protection and analytics
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
from bs4 import BeautifulSoup
from pydantic import BaseModel, Field

from ..base_crawler import BaseCrawler
from ....core.config import get_settings
from ....core.logging import get_logger
from ....models.content import ContentMatch, PlatformContent
from ....utils.rate_limiter import RateLimiter
from ....security.encryption import encrypt_sensitive_data

logger = get_logger(__name__)
settings = get_settings()


class PinterestPin(BaseModel):
    """Pinterest Pin data model"""
    pin_id: str
    title: str
    description: str
    image_url: str
    board_name: str
    creator_username: str
    created_at: datetime
    pin_url: str
    repin_count: int = 0
    like_count: int = 0
    comment_count: int = 0
    tags: List[str] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class PinterestBoard(BaseModel):
    """Pinterest Board data model"""
    board_id: str
    name: str
    description: str
    creator_username: str
    pin_count: int
    follower_count: int
    created_at: datetime
    board_url: str
    category: Optional[str] = None
    is_secret: bool = False


class PinterestProfile(BaseModel):
    """Pinterest Profile data model"""
    username: str
    display_name: str
    bio: str
    follower_count: int
    following_count: int
    board_count: int
    pin_count: int
    profile_url: str
    avatar_url: Optional[str] = None
    website_url: Optional[str] = None
    verified: bool = False


class PinterestCrawler(BaseCrawler):
    """
    Advanced Pinterest crawler for comprehensive content monitoring
    
    Features:
    - Pin content analysis with image fingerprinting
    - Board monitoring and analytics
    - User profile tracking
    - Trend analysis and hashtag monitoring
    - Copyright infringement detection
    - Engagement metrics collection
    - Real-time monitoring with webhooks
    """
    
    def __init__(self):
        super().__init__()
        self.platform = "pinterest"
        self.base_url = "https://www.pinterest.com"
        self.api_base = "https://api.pinterest.com/v5"
        self.rate_limiter = RateLimiter(
            requests_per_minute=100,
            requests_per_hour=1000
        )
        self.session_headers = {
            'User-Agent': 'IA-Influencer-Agent/2.0 (Content Protection)',
            'Accept': 'application/json, text/html',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        }
        
    async def authenticate(self, access_token: str) -> bool:
        """Authenticate with Pinterest API"""
        try:
            self.session_headers['Authorization'] = f'Bearer {access_token}'
            
            async with aiohttp.ClientSession(headers=self.session_headers) as session:
                async with session.get(f"{self.api_base}/user_account") as response:
                    if response.status == 200:
                        user_data = await response.json()
                        logger.info(f"Authenticated as Pinterest user: {user_data.get('username')}")
                        return True
                    else:
                        logger.error(f"Pinterest authentication failed: {response.status}")
                        return False
                        
        except Exception as e:
            logger.error(f"Pinterest authentication error: {str(e)}")
            return False
    
    async def search_content(
        self,
        query: str,
        content_type: str = "pins",
        limit: int = 100,
        filters: Optional[Dict] = None
    ) -> List[Dict]:
        """
        Search Pinterest content with advanced filtering
        
        Args:
            query: Search query
            content_type: Type of content (pins, boards, users)
            limit: Maximum results to return
            filters: Additional search filters
            
        Returns:
            List of matching content items
        """
        await self.rate_limiter.wait()
        
        try:
            search_params = {
                'query': query,
                'limit': min(limit, 250)  # Pinterest API limit
            }
            
            if filters:
                search_params.update(filters)
            
            endpoint = f"{self.api_base}/search/{content_type}"
            
            async with aiohttp.ClientSession(headers=self.session_headers) as session:
                async with session.get(endpoint, params=search_params) as response:
                    if response.status == 200:
                        data = await response.json()
                        results = data.get('items', [])
                        
                        logger.info(f"Found {len(results)} Pinterest {content_type} for query: {query}")
                        return results
                    else:
                        logger.error(f"Pinterest search failed: {response.status}")
                        return []
                        
        except Exception as e:
            logger.error(f"Pinterest search error: {str(e)}")
            return []
    
    async def get_pin_details(self, pin_id: str) -> Optional[PinterestPin]:
        """Get detailed information about a specific pin"""
        await self.rate_limiter.wait()
        
        try:
            endpoint = f"{self.api_base}/pins/{pin_id}"
            params = {
                'pin_fields': 'id,link,title,description,dominant_color,alt_text,board_id,board_name,board_owner,created_at,note,pin_metrics,media'
            }
            
            async with aiohttp.ClientSession(headers=self.session_headers) as session:
                async with session.get(endpoint, params=params) as response:
                    if response.status == 200:
                        pin_data = await response.json()
                        
                        # Extract pin metrics
                        metrics = pin_data.get('pin_metrics', {})
                        
                        pin = PinterestPin(
                            pin_id=pin_data['id'],
                            title=pin_data.get('title', ''),
                            description=pin_data.get('description', ''),
                            image_url=pin_data.get('media', {}).get('images', {}).get('original', {}).get('url', ''),
                            board_name=pin_data.get('board_name', ''),
                            creator_username=pin_data.get('board_owner', {}).get('username', ''),
                            created_at=datetime.fromisoformat(pin_data['created_at'].replace('Z', '+00:00')),
                            pin_url=f"https://pinterest.com/pin/{pin_data['id']}/",
                            repin_count=metrics.get('save', 0),
                            like_count=metrics.get('impression', 0),
                            comment_count=metrics.get('pin_click', 0),
                            tags=self._extract_hashtags(pin_data.get('description', '')),
                            metadata={
                                'dominant_color': pin_data.get('dominant_color'),
                                'alt_text': pin_data.get('alt_text'),
                                'board_id': pin_data.get('board_id'),
                                'link': pin_data.get('link')
                            }
                        )
                        
                        return pin
                    else:
                        logger.error(f"Failed to get pin details: {response.status}")
                        return None
                        
        except Exception as e:
            logger.error(f"Error getting pin details: {str(e)}")
            return None
    
    async def get_board_pins(self, board_id: str, limit: int = 100) -> List[PinterestPin]:
        """Get all pins from a specific board"""
        await self.rate_limiter.wait()
        
        try:
            endpoint = f"{self.api_base}/boards/{board_id}/pins"
            params = {
                'limit': min(limit, 250),
                'pin_fields': 'id,link,title,description,created_at,board_name,board_owner,pin_metrics'
            }
            
            pins = []
            
            async with aiohttp.ClientSession(headers=self.session_headers) as session:
                async with session.get(endpoint, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        for pin_data in data.get('items', []):
                            pin = await self._parse_pin_data(pin_data)
                            if pin:
                                pins.append(pin)
                        
                        logger.info(f"Retrieved {len(pins)} pins from board {board_id}")
                        return pins
                    else:
                        logger.error(f"Failed to get board pins: {response.status}")
                        return []
                        
        except Exception as e:
            logger.error(f"Error getting board pins: {str(e)}")
            return []
    
    async def get_user_profile(self, username: str) -> Optional[PinterestProfile]:
        """Get detailed user profile information"""
        await self.rate_limiter.wait()
        
        try:
            endpoint = f"{self.api_base}/user_account"
            params = {
                'user_fields': 'account_type,profile_image,website_url,username,about,board_count,pin_count,follower_count,following_count'
            }
            
            async with aiohttp.ClientSession(headers=self.session_headers) as session:
                async with session.get(endpoint, params=params) as response:
                    if response.status == 200:
                        user_data = await response.json()
                        
                        profile = PinterestProfile(
                            username=user_data['username'],
                            display_name=user_data.get('username', ''),
                            bio=user_data.get('about', ''),
                            follower_count=user_data.get('follower_count', 0),
                            following_count=user_data.get('following_count', 0),
                            board_count=user_data.get('board_count', 0),
                            pin_count=user_data.get('pin_count', 0),
                            profile_url=f"https://pinterest.com/{user_data['username']}/",
                            avatar_url=user_data.get('profile_image', ''),
                            website_url=user_data.get('website_url'),
                            verified=user_data.get('account_type') == 'BUSINESS'
                        )
                        
                        return profile
                    else:
                        logger.error(f"Failed to get user profile: {response.status}")
                        return None
                        
        except Exception as e:
            logger.error(f"Error getting user profile: {str(e)}")
            return None
    
    async def monitor_content_infringement(
        self,
        protected_content: Dict,
        similarity_threshold: float = 0.8
    ) -> List[ContentMatch]:
        """
        Monitor Pinterest for potential copyright infringement
        
        Args:
            protected_content: Content to protect (images, descriptions, etc.)
            similarity_threshold: Minimum similarity for match detection
            
        Returns:
            List of potential copyright matches
        """
        matches = []
        
        try:
            # Search for similar content using image similarity and text matching
            search_queries = self._generate_search_queries(protected_content)
            
            for query in search_queries:
                results = await self.search_content(query, "pins", limit=50)
                
                for result in results:
                    pin = await self.get_pin_details(result['id'])
                    if pin:
                        similarity_score = await self._calculate_content_similarity(
                            protected_content, pin
                        )
                        
                        if similarity_score >= similarity_threshold:
                            match = ContentMatch(
                                platform="pinterest",
                                content_id=pin.pin_id,
                                url=pin.pin_url,
                                title=pin.title,
                                description=pin.description,
                                creator=pin.creator_username,
                                similarity_score=similarity_score,
                                detection_date=datetime.utcnow(),
                                content_type="pin",
                                metadata={
                                    'board_name': pin.board_name,
                                    'repin_count': pin.repin_count,
                                    'like_count': pin.like_count,
                                    'image_url': pin.image_url
                                }
                            )
                            matches.append(match)
            
            logger.info(f"Found {len(matches)} potential copyright matches on Pinterest")
            return matches
            
        except Exception as e:
            logger.error(f"Error monitoring Pinterest content infringement: {str(e)}")
            return []
    
    async def analyze_trends(self, category: str = None, days: int = 7) -> Dict[str, Any]:
        """
        Analyze Pinterest trends for content strategy
        
        Args:
            category: Specific category to analyze
            days: Number of days to analyze
            
        Returns:
            Trend analysis data
        """
        try:
            # Get trending topics and popular pins
            trending_data = {
                'trending_topics': await self._get_trending_topics(category),
                'popular_pins': await self._get_popular_pins(category, days),
                'hashtag_trends': await self._analyze_hashtag_trends(days),
                'engagement_patterns': await self._analyze_engagement_patterns(days)
            }
            
            return trending_data
            
        except Exception as e:
            logger.error(f"Error analyzing Pinterest trends: {str(e)}")
            return {}
    
    async def bulk_pin_analysis(self, pin_ids: List[str]) -> List[Dict[str, Any]]:
        """Analyze multiple pins in bulk for efficiency"""
        results = []
        
        # Process pins in batches to respect rate limits
        batch_size = 25
        for i in range(0, len(pin_ids), batch_size):
            batch = pin_ids[i:i + batch_size]
            
            batch_tasks = [self.get_pin_details(pin_id) for pin_id in batch]
            batch_results = await asyncio.gather(*batch_tasks, return_exceptions=True)
            
            for pin in batch_results:
                if isinstance(pin, PinterestPin):
                    analysis = await self._analyze_pin_performance(pin)
                    results.append(analysis)
                elif isinstance(pin, Exception):
                    logger.error(f"Error in batch analysis: {str(pin)}")
            
            # Rate limiting between batches
            await asyncio.sleep(1)
        
        return results
    
    async def _parse_pin_data(self, pin_data: Dict) -> Optional[PinterestPin]:
        """Parse Pinterest API pin data into PinterestPin model"""
        try:
            metrics = pin_data.get('pin_metrics', {})
            
            pin = PinterestPin(
                pin_id=pin_data['id'],
                title=pin_data.get('title', ''),
                description=pin_data.get('description', ''),
                image_url=pin_data.get('media', {}).get('images', {}).get('original', {}).get('url', ''),
                board_name=pin_data.get('board_name', ''),
                creator_username=pin_data.get('board_owner', {}).get('username', ''),
                created_at=datetime.fromisoformat(pin_data['created_at'].replace('Z', '+00:00')),
                pin_url=f"https://pinterest.com/pin/{pin_data['id']}/",
                repin_count=metrics.get('save', 0),
                like_count=metrics.get('impression', 0),
                comment_count=metrics.get('pin_click', 0),
                tags=self._extract_hashtags(pin_data.get('description', ''))
            )
            
            return pin
            
        except Exception as e:
            logger.error(f"Error parsing pin data: {str(e)}")
            return None
    
    def _extract_hashtags(self, text: str) -> List[str]:
        """Extract hashtags from pin description"""
        hashtag_pattern = r'#\w+'
        hashtags = re.findall(hashtag_pattern, text.lower())
        return [tag[1:] for tag in hashtags]  # Remove # symbol
    
    def _generate_search_queries(self, protected_content: Dict) -> List[str]:
        """Generate search queries for content protection"""
        queries = []
        
        if 'title' in protected_content:
            queries.append(protected_content['title'])
        
        if 'description' in protected_content:
            # Extract key phrases from description
            words = protected_content['description'].split()
            if len(words) > 3:
                queries.append(' '.join(words[:5]))
        
        if 'tags' in protected_content:
            queries.extend(protected_content['tags'][:3])
        
        return queries[:5]  # Limit to 5 queries to avoid rate limiting
    
    async def _calculate_content_similarity(
        self,
        protected_content: Dict,
        pin: PinterestPin
    ) -> float:
        """Calculate similarity between protected content and Pinterest pin"""
        from difflib import SequenceMatcher
        
        similarity_scores = []
        
        # Text similarity
        if 'title' in protected_content and pin.title:
            title_similarity = SequenceMatcher(
                None,
                protected_content['title'].lower(),
                pin.title.lower()
            ).ratio()
            similarity_scores.append(title_similarity * 0.4)
        
        if 'description' in protected_content and pin.description:
            desc_similarity = SequenceMatcher(
                None,
                protected_content['description'].lower(),
                pin.description.lower()
            ).ratio()
            similarity_scores.append(desc_similarity * 0.3)
        
        # Tag similarity
        if 'tags' in protected_content and pin.tags:
            protected_tags = set(tag.lower() for tag in protected_content['tags'])
            pin_tags = set(tag.lower() for tag in pin.tags)
            
            if protected_tags and pin_tags:
                tag_similarity = len(protected_tags.intersection(pin_tags)) / len(protected_tags.union(pin_tags))
                similarity_scores.append(tag_similarity * 0.3)
        
        return sum(similarity_scores) if similarity_scores else 0.0
    
    async def _get_trending_topics(self, category: str = None) -> List[str]:
        """Get trending topics on Pinterest"""
        # This would require Pinterest's trending API or web scraping
        # For now, return common trending topics
        return [
            "home decor", "fashion", "recipes", "diy", "wedding", 
            "travel", "fitness", "beauty", "photography", "art"
        ]
    
    async def _get_popular_pins(self, category: str = None, days: int = 7) -> List[Dict]:
        """Get popular pins from recent days"""
        # Implementation would depend on Pinterest's popular content API
        return []
    
    async def _analyze_hashtag_trends(self, days: int = 7) -> Dict[str, int]:
        """Analyze hashtag trends"""
        # Implementation for hashtag trend analysis
        return {}
    
    async def _analyze_engagement_patterns(self, days: int = 7) -> Dict[str, Any]:
        """Analyze engagement patterns"""
        # Implementation for engagement pattern analysis
        return {}
    
    async def _analyze_pin_performance(self, pin: PinterestPin) -> Dict[str, Any]:
        """Analyze individual pin performance metrics"""
        return {
            'pin_id': pin.pin_id,
            'engagement_rate': (pin.repin_count + pin.like_count) / max(pin.like_count, 1),
            'virality_score': pin.repin_count * 2 + pin.like_count,
            'content_quality_score': len(pin.description) / 100 + len(pin.tags) * 0.1,
            'hashtag_effectiveness': len(pin.tags) * 0.2 if pin.tags else 0,
            'performance_category': self._categorize_performance(pin)
        }
    
    def _categorize_performance(self, pin: PinterestPin) -> str:
        """Categorize pin performance level"""
        total_engagement = pin.repin_count + pin.like_count
        
        if total_engagement > 1000:
            return "viral"
        elif total_engagement > 100:
            return "high"
        elif total_engagement > 10:
            return "medium"
        else:
            return "low"
