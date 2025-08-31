"""OnlyFans Content Crawling Engine

Advanced industry-grade engine for OnlyFans content crawling and protection.
Implements full content lifecycle management with AI-powered content protection.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.

WARNING: This code is proprietary and confidential. 
Unauthorized copying, distribution, or use is strictly prohibited.
Any violation will result in legal action.
"""import asyncio
import logging
from typing import Dict, List, Optional, Any, AsyncGenerator
from datetime import datetime, timedelta
import aiohttp
from dataclasses import dataclass
from enum import Enum

from ..base import BaseCrawlerEngine
from ...core.platforms.onlyfans import OnlyFansPlatform
from ...protection.content_guardian import ContentGuardian
from ...ai.content_analyzer import ContentAnalyzer
from ...security.encryption import SecurityManager
from ...monitoring.metrics import MetricsCollector


class ContentType(Enum):
    """Content types for OnlyFans"""    IMAGE = "image"
    VIDEO = "video"
    LIVE_STREAM = "live_stream"
    MESSAGE = "message"
    STORY = "story"
    POST = "post"


@dataclass
class OnlyFansContent:
    """OnlyFans content data structure"""    content_id: str
    creator_id: str
    content_type: ContentType
    title: Optional[str]
    description: Optional[str]
    media_urls: List[str]
    thumbnail_url: Optional[str]
    price: Optional[float]
    is_premium: bool
    subscriber_count: int
    likes_count: int
    comments_count: int
    created_at: datetime
    engagement_rate: float
    content_fingerprint: str
    protection_level: str
    monetization_tier: str


class OnlyFansEngine(BaseCrawlerEngine):
    """    Professional OnlyFans crawling engine with advanced content protection
    and monetization features for creator content management.
    """    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.platform = OnlyFansPlatform(config.get('onlyfans', {}))
        self.content_guardian = ContentGuardian()
        self.content_analyzer = ContentAnalyzer()
        self.security_manager = SecurityManager()
        self.metrics_collector = MetricsCollector()
        self.logger = logging.getLogger(__name__)
        
        # OnlyFans specific configuration
        self.rate_limit_per_minute = config.get('rate_limit_per_minute', 30)
        self.max_concurrent_requests = config.get('max_concurrent_requests', 5)
        self.content_quality_threshold = config.get('content_quality_threshold', 0.8)
        self.enable_content_protection = config.get('enable_content_protection', True)
        
    async def crawl_creator_content(
        self, 
        creator_id: str, 
        content_types: List[ContentType] = None,
        date_range: Optional[tuple] = None
    ) -> AsyncGenerator[OnlyFansContent, None]:
        """        Crawl content from a specific OnlyFans creator with advanced filtering
        
        Args:
            creator_id: Creator identifier
            content_types: List of content types to crawl
            date_range: Optional date range tuple (start_date, end_date)
            
        Yields:
            OnlyFansContent: Processed content objects
        """        self.logger.info(f"Starting content crawl for creator: {creator_id}")
        
        try:
            # Initialize rate limiting and session management
            async with self._create_session() as session:
                content_types = content_types or list(ContentType)
                
                for content_type in content_types:
                    async for content in self._crawl_content_by_type(
                        session, creator_id, content_type, date_range
                    ):
                        # Apply content protection and analysis
                        protected_content = await self._process_content(content)
                        if protected_content:
                            yield protected_content
                            
        except Exception as e:
            self.logger.error(f"Error crawling creator content: {str(e)}")
            await self.metrics_collector.record_error('creator_crawl_error', str(e))
            raise
            
    async def _crawl_content_by_type(
        self,
        session: aiohttp.ClientSession,
        creator_id: str,
        content_type: ContentType,
        date_range: Optional[tuple]
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """Crawl content by specific type with advanced filtering"""        
        page = 1
        max_pages = 100  # Prevent infinite loops
        
        while page <= max_pages:
            try:
                # Apply rate limiting
                await self._apply_rate_limiting()
                
                # Fetch content page
                content_data = await self._fetch_content_page(
                    session, creator_id, content_type, page, date_range
                )
                
                if not content_data or not content_data.get('items'):
                    break
                    
                for item in content_data['items']:
                    yield item
                    
                # Check for more pages
                if not content_data.get('has_more', False):
                    break
                    
                page += 1
                
            except Exception as e:
                self.logger.error(f"Error fetching page {page}: {str(e)}")
                break
                
    async def _fetch_content_page(
        self,
        session: aiohttp.ClientSession,
        creator_id: str,
        content_type: ContentType,
        page: int,
        date_range: Optional[tuple]
    ) -> Dict[str, Any]:
        """Fetch a single page of content with advanced error handling"""        
        url = f"https://onlyfans.com/api2/v2/users/{creator_id}/posts"
        
        params = {
            'limit': 50,
            'offset': (page - 1) * 50,
            'type': content_type.value,
            'order': 'publish_date_desc'
        }
        
        if date_range:
            start_date, end_date = date_range
            params['date_from'] = start_date.isoformat()
            params['date_to'] = end_date.isoformat()
            
        headers = await self._get_authenticated_headers()
        
        try:
            async with session.get(url, params=params, headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    return data
                elif response.status == 429:
                    # Rate limit hit, wait and retry
                    await asyncio.sleep(60)
                    return await self._fetch_content_page(
                        session, creator_id, content_type, page, date_range
                    )
                else:
                    self.logger.error(f"HTTP {response.status}: {await response.text()}")
                    return {}
                    
        except Exception as e:
            self.logger.error(f"Request error: {str(e)}")
            return {}
            
    async def _process_content(self, raw_content: Dict[str, Any]) -> Optional[OnlyFansContent]:
        """Process and protect content with advanced AI analysis"""        
        try:
            # Extract content metadata
            content_id = raw_content.get('id')
            creator_id = raw_content.get('author', {}).get('id')
            
            if not content_id or not creator_id:
                return None
                
            # Determine content type
            content_type = self._determine_content_type(raw_content)
            
            # Extract media URLs
            media_urls = self._extract_media_urls(raw_content)
            
            if not media_urls:
                return None
                
            # Generate content fingerprint for protection
            content_fingerprint = await self.content_guardian.generate_fingerprint(
                media_urls[0] if media_urls else ""
            )
            
            # Analyze content quality and engagement potential
            quality_score = await self.content_analyzer.analyze_quality(raw_content)
            
            if quality_score < self.content_quality_threshold:
                return None
                
            # Apply content protection
            protection_level = "premium" if raw_content.get('price', 0) > 0 else "standard"
            
            # Determine monetization tier
            monetization_tier = await self._determine_monetization_tier(raw_content)
            
            # Create OnlyFans content object
            content = OnlyFansContent(
                content_id=content_id,
                creator_id=creator_id,
                content_type=content_type,
                title=raw_content.get('text', '')[:100],
                description=raw_content.get('text', ''),
                media_urls=media_urls,
                thumbnail_url=raw_content.get('preview', {}).get('url'),
                price=raw_content.get('price'),
                is_premium=raw_content.get('canPurchase', False),
                subscriber_count=raw_content.get('author', {}).get('subscribersCount', 0),
                likes_count=raw_content.get('favoritesCount', 0),
                comments_count=raw_content.get('commentsCount', 0),
                created_at=datetime.fromisoformat(raw_content.get('postedAt', '')),
                engagement_rate=self._calculate_engagement_rate(raw_content),
                content_fingerprint=content_fingerprint,
                protection_level=protection_level,
                monetization_tier=monetization_tier
            )
            
            # Record metrics
            await self.metrics_collector.record_content_processed(
                platform='onlyfans',
                content_type=content_type.value,
                quality_score=quality_score
            )
            
            return content
            
        except Exception as e:
            self.logger.error(f"Error processing content: {str(e)}")
            return None
            
    def _determine_content_type(self, content: Dict[str, Any]) -> ContentType:
        """Determine content type from raw data"""        
        media = content.get('media', [])
        if not media:
            return ContentType.MESSAGE
            
        first_media = media[0]
        media_type = first_media.get('type', '')
        
        if 'video' in media_type.lower():
            return ContentType.VIDEO
        elif 'image' in media_type.lower():
            return ContentType.IMAGE
        else:
            return ContentType.POST
            
    def _extract_media_urls(self, content: Dict[str, Any]) -> List[str]:
        """Extract media URLs from content"""        
        urls = []
        media = content.get('media', [])
        
        for item in media:
            if item.get('full'):
                urls.append(item['full'])
            elif item.get('source'):
                urls.append(item['source']['source'])
                
        return urls
        
    def _calculate_engagement_rate(self, content: Dict[str, Any]) -> float:
        """Calculate engagement rate for content"""        
        likes = content.get('favoritesCount', 0)
        comments = content.get('commentsCount', 0)
        subscribers = content.get('author', {}).get('subscribersCount', 1)
        
        if subscribers == 0:
            return 0.0
            
        engagement_rate = (likes + comments * 2) / subscribers
        return min(engagement_rate, 1.0)  # Cap at 100%
        
    async def _determine_monetization_tier(self, content: Dict[str, Any]) -> str:
        """Determine monetization tier based on content analysis"""        
        price = content.get('price', 0)
        engagement = self._calculate_engagement_rate(content)
        
        if price > 50 or engagement > 0.1:
            return "premium"
        elif price > 10 or engagement > 0.05:
            return "standard"
        else:
            return "basic"
            
    async def crawl_trending_content(
        self, 
        limit: int = 100,
        content_types: List[ContentType] = None
    ) -> List[OnlyFansContent]:
        """Crawl trending content across the platform"""        
        self.logger.info(f"Crawling trending content, limit: {limit}")
        
        trending_content = []
        content_types = content_types or list(ContentType)
        
        try:
            async with self._create_session() as session:
                for content_type in content_types:
                    type_content = await self._fetch_trending_by_type(
                        session, content_type, limit // len(content_types)
                    )
                    trending_content.extend(type_content)
                    
        except Exception as e:
            self.logger.error(f"Error crawling trending content: {str(e)}")
            
        return trending_content[:limit]
        
    async def _fetch_trending_by_type(
        self,
        session: aiohttp.ClientSession,
        content_type: ContentType,
        limit: int
    ) -> List[OnlyFansContent]:
        """Fetch trending content by type"""        
        url = "https://onlyfans.com/api2/v2/posts/trending"
        
        params = {
            'limit': limit,
            'type': content_type.value,
            'period': '24h'
        }
        
        headers = await self._get_authenticated_headers()
        content_list = []
        
        try:
            async with session.get(url, params=params, headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    for item in data.get('list', []):
                        content = await self._process_content(item)
                        if content:
                            content_list.append(content)
                            
        except Exception as e:
            self.logger.error(f"Error fetching trending content: {str(e)}")
            
        return content_list
        
    async def monitor_creator_performance(
        self, 
        creator_id: str,
        monitoring_period: timedelta = timedelta(days=7)
    ) -> Dict[str, Any]:
        """Monitor creator performance metrics"""        
        self.logger.info(f"Monitoring creator performance: {creator_id}")
        
        end_date = datetime.now()
        start_date = end_date - monitoring_period
        
        try:
            # Collect content from monitoring period
            content_list = []
            async for content in self.crawl_creator_content(
                creator_id, date_range=(start_date, end_date)
            ):
                content_list.append(content)
                
            # Calculate performance metrics
            metrics = {
                'total_content': len(content_list),
                'avg_engagement_rate': sum(c.engagement_rate for c in content_list) / len(content_list) if content_list else 0,
                'total_likes': sum(c.likes_count for c in content_list),
                'total_comments': sum(c.comments_count for c in content_list),
                'premium_content_ratio': len([c for c in content_list if c.is_premium]) / len(content_list) if content_list else 0,
                'avg_price': sum(c.price or 0 for c in content_list) / len(content_list) if content_list else 0,
                'content_type_distribution': self._calculate_content_distribution(content_list),
                'monetization_potential': self._calculate_monetization_potential(content_list),
                'protection_coverage': len([c for c in content_list if c.protection_level == 'premium']) / len(content_list) if content_list else 0
            }
            
            # Record monitoring metrics
            await self.metrics_collector.record_creator_performance(creator_id, metrics)
            
            return metrics
            
        except Exception as e:
            self.logger.error(f"Error monitoring creator performance: {str(e)}")
            return {}
            
    def _calculate_content_distribution(self, content_list: List[OnlyFansContent]) -> Dict[str, float]:
        """Calculate content type distribution"""        
        if not content_list:
            return {}
            
        total = len(content_list)
        distribution = {}
        
        for content_type in ContentType:
            count = len([c for c in content_list if c.content_type == content_type])
            distribution[content_type.value] = count / total
            
        return distribution
        
    def _calculate_monetization_potential(self, content_list: List[OnlyFansContent]) -> float:
        """Calculate monetization potential score"""        
        if not content_list:
            return 0.0
            
        # Factors: engagement rate, premium content ratio, average price
        avg_engagement = sum(c.engagement_rate for c in content_list) / len(content_list)
        premium_ratio = len([c for c in content_list if c.is_premium]) / len(content_list)
        avg_price = sum(c.price or 0 for c in content_list) / len(content_list)
        
        # Weighted score calculation
        score = (avg_engagement * 0.4 + premium_ratio * 0.3 + min(avg_price / 100, 1.0) * 0.3)
        
        return min(score, 1.0)
        
    async def search_content(
        self, 
        query: str,
        content_types: List[ContentType] = None,
        filters: Dict[str, Any] = None
    ) -> List[OnlyFansContent]:
        """Search content with advanced filtering"""        
        self.logger.info(f"Searching content: {query}")
        
        content_types = content_types or list(ContentType)
        filters = filters or {}
        
        search_results = []
        
        try:
            async with self._create_session() as session:
                for content_type in content_types:
                    type_results = await self._search_content_by_type(
                        session, query, content_type, filters
                    )
                    search_results.extend(type_results)
                    
        except Exception as e:
            self.logger.error(f"Error searching content: {str(e)}")
            
        return search_results
        
    async def _search_content_by_type(
        self,
        session: aiohttp.ClientSession,
        query: str,
        content_type: ContentType,
        filters: Dict[str, Any]
    ) -> List[OnlyFansContent]:
        """Search content by type with filters"""        
        url = "https://onlyfans.com/api2/v2/posts/search"
        
        params = {
            'query': query,
            'type': content_type.value,
            'limit': filters.get('limit', 50)
        }
        
        # Add additional filters
        if filters.get('min_price'):
            params['min_price'] = filters['min_price']
        if filters.get('max_price'):
            params['max_price'] = filters['max_price']
        if filters.get('min_engagement'):
            params['min_engagement'] = filters['min_engagement']
            
        headers = await self._get_authenticated_headers()
        results = []
        
        try:
            async with session.get(url, params=params, headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    for item in data.get('list', []):
                        content = await self._process_content(item)
                        if content and self._matches_filters(content, filters):
                            results.append(content)
                            
        except Exception as e:
            self.logger.error(f"Error searching content by type: {str(e)}")
            
        return results
        
    def _matches_filters(self, content: OnlyFansContent, filters: Dict[str, Any]) -> bool:
        """Check if content matches additional filters"""        
        if filters.get('min_engagement') and content.engagement_rate < filters['min_engagement']:
            return False
            
        if filters.get('min_likes') and content.likes_count < filters['min_likes']:
            return False
            
        if filters.get('only_premium') and not content.is_premium:
            return False
            
        if filters.get('monetization_tier') and content.monetization_tier != filters['monetization_tier']:
            return False
            
        return True
        
    async def _get_authenticated_headers(self) -> Dict[str, str]:
        """Get authenticated headers for API requests"""        
        return {
            'User-Agent': 'OnlyFans/1.0',
            'Accept': 'application/json',
            'Authorization': f'Bearer {self.config.get("access_token", "")}',
            'X-BC': self.config.get('x_bc', ''),
            'Cookie': self.config.get('cookie', '')
        }
        
    async def _create_session(self) -> aiohttp.ClientSession:
        """Create configured HTTP session"""        
        connector = aiohttp.TCPConnector(
            limit=self.max_concurrent_requests,
            limit_per_host=self.max_concurrent_requests
        )
        
        timeout = aiohttp.ClientTimeout(total=30)
        
        return aiohttp.ClientSession(
            connector=connector,
            timeout=timeout
        )
        
    async def _apply_rate_limiting(self):
        """Apply rate limiting to prevent API abuse"""        
        # Simple rate limiting implementation
        await asyncio.sleep(60 / self.rate_limit_per_minute)
