"""
Pinterest Content Crawling Engine

Advanced industry-grade engine for Pinterest content crawling and visual discovery.
Implements visual content analysis with AI-powered trend detection and monetization.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.

WARNING: This code is proprietary and confidential. 
Unauthorized copying, distribution, or use is strictly prohibited.
Any violation will result in legal action.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, AsyncGenerator
from datetime import datetime, timedelta
import aiohttp
from dataclasses import dataclass
from enum import Enum

from ..base import BaseCrawlerEngine
from ...core.platforms.pinterest import PinterestPlatform
from ...protection.content_guardian import ContentGuardian
from ...ai.content_analyzer import ContentAnalyzer
from ...security.encryption import SecurityManager
from ...monitoring.metrics import MetricsCollector


class PinType(Enum):
    """Pinterest pin types"""
    STANDARD = "standard"
    VIDEO = "video"
    STORY = "story"
    PRODUCT = "product"
    CAROUSEL = "carousel"
    IDEA = "idea"


class BoardCategory(Enum):
    """Pinterest board categories"""
    ART = "art"
    FASHION = "fashion"
    FOOD = "food"
    HOME = "home"
    TRAVEL = "travel"
    PHOTOGRAPHY = "photography"
    DESIGN = "design"
    LIFESTYLE = "lifestyle"
    BUSINESS = "business"
    EDUCATION = "education"


@dataclass
class PinterestPin:
    """Pinterest pin data structure"""
    pin_id: str
    board_id: str
    user_id: str
    title: str
    description: str
    pin_type: PinType
    image_url: str
    video_url: Optional[str]
    link_url: Optional[str]
    board_name: str
    category: BoardCategory
    saves_count: int
    comments_count: int
    impressions: int
    clicks: int
    created_at: datetime
    engagement_rate: float
    viral_potential: float
    monetization_score: float
    content_fingerprint: str
    protection_level: str
    trend_score: float


class PinterestEngine(BaseCrawlerEngine):
    """
    Professional Pinterest crawling engine with advanced visual content analysis
    and trend detection for creators and marketers.
    """
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.platform = PinterestPlatform(config.get('pinterest', {}))
        self.content_guardian = ContentGuardian()
        self.content_analyzer = ContentAnalyzer()
        self.security_manager = SecurityManager()
        self.metrics_collector = MetricsCollector()
        self.logger = logging.getLogger(__name__)
        
        # Pinterest specific configuration
        self.rate_limit_per_minute = config.get('rate_limit_per_minute', 200)
        self.max_concurrent_requests = config.get('max_concurrent_requests', 15)
        self.content_quality_threshold = config.get('content_quality_threshold', 0.6)
        self.enable_trend_analysis = config.get('enable_trend_analysis', True)
        
    async def crawl_user_pins(
        self, 
        user_id: str, 
        pin_types: List[PinType] = None,
        board_filter: Optional[str] = None,
        date_range: Optional[tuple] = None
    ) -> AsyncGenerator[PinterestPin, None]:
        """
        Crawl pins from a specific Pinterest user with advanced filtering
        
        Args:
            user_id: User identifier
            pin_types: List of pin types to crawl
            board_filter: Optional board name filter
            date_range: Optional date range tuple (start_date, end_date)
            
        Yields:
            PinterestPin: Processed pin objects
        """
        self.logger.info(f"Starting Pinterest pins crawl for user: {user_id}")
        
        try:
            async with self._create_session() as session:
                pin_types = pin_types or list(PinType)
                
                # Get user's boards first
                boards = await self._fetch_user_boards(session, user_id)
                
                for board in boards:
                    if board_filter and board.get('name', '') != board_filter:
                        continue
                        
                    async for pin in self._crawl_board_pins(
                        session, board['id'], pin_types, date_range
                    ):
                        # Apply content protection and analysis
                        processed_pin = await self._process_pin(pin, board)
                        if processed_pin:
                            yield processed_pin
                            
        except Exception as e:
            self.logger.error(f"Error crawling user pins: {str(e)}")
            await self.metrics_collector.record_error('pinterest_crawl_error', str(e))
            raise
            
    async def _fetch_user_boards(
        self,
        session: aiohttp.ClientSession,
        user_id: str
    ) -> List[Dict[str, Any]]:
        """Fetch user's boards"""
        
        url = f"https://api.pinterest.com/v5/boards"
        
        params = {
            'owner_id': user_id,
            'fields': 'id,name,description,pin_count,follower_count,created_at,privacy'
        }
        
        headers = await self._get_authenticated_headers()
        boards = []
        
        try:
            async with session.get(url, params=params, headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    boards = data.get('items', [])
                else:
                    self.logger.error(f"Failed to fetch boards: HTTP {response.status}")
                    
        except Exception as e:
            self.logger.error(f"Error fetching user boards: {str(e)}")
            
        return boards
        
    async def _crawl_board_pins(
        self,
        session: aiohttp.ClientSession,
        board_id: str,
        pin_types: List[PinType],
        date_range: Optional[tuple]
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """Crawl pins from a specific board"""
        
        bookmark = None
        max_pages = 100
        page_count = 0
        
        while page_count < max_pages:
            try:
                # Apply rate limiting
                await self._apply_rate_limiting()
                
                # Fetch pins page
                pins_data = await self._fetch_pins_page(
                    session, board_id, bookmark, date_range
                )
                
                if not pins_data or not pins_data.get('items'):
                    break
                    
                for pin in pins_data['items']:
                    # Apply pin type filter
                    if self._matches_pin_type_filter(pin, pin_types):
                        yield pin
                        
                # Get next bookmark
                bookmark = pins_data.get('bookmark')
                if not bookmark:
                    break
                    
                page_count += 1
                
            except Exception as e:
                self.logger.error(f"Error fetching board pins page {page_count}: {str(e)}")
                break
                
    async def _fetch_pins_page(
        self,
        session: aiohttp.ClientSession,
        board_id: str,
        bookmark: Optional[str],
        date_range: Optional[tuple]
    ) -> Dict[str, Any]:
        """Fetch a single page of pins from a board"""
        
        url = f"https://api.pinterest.com/v5/boards/{board_id}/pins"
        
        params = {
            'fields': 'id,title,description,link,media,board_id,created_at,note,pin_metrics',
            'page_size': 25
        }
        
        if bookmark:
            params['bookmark'] = bookmark
            
        headers = await self._get_authenticated_headers()
        
        try:
            async with session.get(url, params=params, headers=headers) as response:
                if response.status == 200:
                    return await response.json()
                elif response.status == 429:
                    # Rate limit hit, wait and retry
                    await asyncio.sleep(60)
                    return await self._fetch_pins_page(session, board_id, bookmark, date_range)
                else:
                    self.logger.error(f"HTTP {response.status}: {await response.text()}")
                    return {}
                    
        except Exception as e:
            self.logger.error(f"Request error: {str(e)}")
            return {}
            
    def _matches_pin_type_filter(self, pin: Dict[str, Any], pin_types: List[PinType]) -> bool:
        """Check if pin matches the pin type filter"""
        
        pin_type = self._determine_pin_type(pin)
        return pin_type in pin_types
        
    def _determine_pin_type(self, pin: Dict[str, Any]) -> PinType:
        """Determine pin type from pin data"""
        
        media = pin.get('media', {})
        
        if media.get('media_type') == 'video':
            return PinType.VIDEO
        elif media.get('media_type') == 'story':
            return PinType.STORY
        elif pin.get('product_tags'):
            return PinType.PRODUCT
        elif media.get('images') and len(media.get('images', [])) > 1:
            return PinType.CAROUSEL
        else:
            return PinType.STANDARD
            
    async def _process_pin(
        self, 
        raw_pin: Dict[str, Any],
        board_info: Dict[str, Any]
    ) -> Optional[PinterestPin]:
        """Process and analyze pin with advanced metrics"""



        
        try:
            pin_id = raw_pin.get('id')
            if not pin_id:
                return None
                
            # Extract pin information
            title = raw_pin.get('title', '')
            description = raw_pin.get('description', '')
            pin_type = self._determine_pin_type(raw_pin)
            
            # Extract media information
            media = raw_pin.get('media', {})
            image_url = self._extract_image_url(media)
            video_url = self._extract_video_url(media)
            
            if not image_url:
                return None
                
            # Generate content fingerprint
            content_fingerprint = await self.content_guardian.generate_fingerprint(
                f"{title}{description}{image_url}"
            )
            
            # Analyze content quality
            quality_score = await self.content_analyzer.analyze_visual_content({
                'title': title,
                'description': description,
                'image_url': image_url,
                'pin_type': pin_type.value
            })
            
            if quality_score < self.content_quality_threshold:
                return None
                
            # Extract metrics
            pin_metrics = raw_pin.get('pin_metrics', {})
            saves_count = pin_metrics.get('save', 0)
            comments_count = pin_metrics.get('comment', 0)
            impressions = pin_metrics.get('impression', 0)
            clicks = pin_metrics.get('outbound_click', 0)
            
            # Calculate engagement and viral potential
            engagement_rate = self._calculate_engagement_rate(pin_metrics)
            viral_potential = await self._calculate_viral_potential(raw_pin, pin_metrics)
            
            # Calculate monetization score
            monetization_score = await self._calculate_monetization_score(
                raw_pin, pin_metrics, quality_score
            )
            
            # Determine board category
            board_category = self._determine_board_category(board_info)
            
            # Calculate trend score
            trend_score = await self._calculate_trend_score(raw_pin, board_category)
            
            # Determine protection level
            protection_level = "premium" if monetization_score > 0.7 else "standard"
            
            # Create Pinterest pin object
            pinterest_pin = PinterestPin(
                pin_id=pin_id,
                board_id=board_info.get('id', ''),
                user_id=raw_pin.get('board_owner', {}).get('username', ''),
                title=title,
                description=description,
                pin_type=pin_type,
                image_url=image_url,
                video_url=video_url,
                link_url=raw_pin.get('link'),
                board_name=board_info.get('name', ''),
                category=board_category,
                saves_count=saves_count,
                comments_count=comments_count,
                impressions=impressions,
                clicks=clicks,
                created_at=datetime.fromisoformat(
                    raw_pin.get('created_at', '').replace('Z', '+00:00')
                ),
                engagement_rate=engagement_rate,
                viral_potential=viral_potential,
                monetization_score=monetization_score,
                content_fingerprint=content_fingerprint,
                protection_level=protection_level,
                trend_score=trend_score
            )
            
            # Record metrics
            await self.metrics_collector.record_content_processed(
                platform='pinterest',
                content_type=pin_type.value,
                quality_score=quality_score
            )
            
            return pinterest_pin
            
        except Exception as e:
            self.logger.error(f"Error processing pin: {str(e)}")
            return None
            
    def _extract_image_url(self, media: Dict[str, Any]) -> Optional[str]:
        """Extract the highest quality image URL"""
        
        images = media.get('images', {})
        
        # Try to get the highest resolution available
        for size in ['orig', '736x', '564x', '474x', '236x']:
            if size in images and images[size].get('url'):
                return images[size]['url']
                
        return None
        
    def _extract_video_url(self, media: Dict[str, Any]) -> Optional[str]:
        """Extract video URL if available"""
        
        if media.get('media_type') == 'video':
            video_list = media.get('video_list', {})
            if 'V_720P' in video_list:
                return video_list['V_720P'].get('url')
            elif 'V_HLSV4' in video_list:
                return video_list['V_HLSV4'].get('url')
                
        return None
        
    def _calculate_engagement_rate(self, pin_metrics: Dict[str, Any]) -> float:
        """Calculate engagement rate for the pin"""
        
        saves = pin_metrics.get('save', 0)
        comments = pin_metrics.get('comment', 0)
        impressions = pin_metrics.get('impression', 1)  # Avoid division by zero
        
        if impressions == 0:
            return 0.0
            
        engagement_rate = (saves + comments * 2) / impressions
        return min(engagement_rate, 1.0)  # Cap at 100%
        
    async def _calculate_viral_potential(
        self,
        pin: Dict[str, Any],
        pin_metrics: Dict[str, Any]
    ) -> float:
        """Calculate viral potential based on growth patterns"""
        
        # Factors: saves rate, repin rate, impression growth
        saves = pin_metrics.get('save', 0)
        impressions = pin_metrics.get('impression', 1)
        
        # Calculate save rate
        save_rate = saves / impressions if impressions > 0 else 0
        
        # Analyze content characteristics for viral potential
        title = pin.get('title', '').lower()
        description = pin.get('description', '').lower()
        
        # Viral keywords (simplified)
        viral_keywords = ['diy', 'hack', 'tip', 'secret', 'amazing', 'incredible', 'easy', 'quick']
        keyword_score = sum(1 for keyword in viral_keywords if keyword in f"{title} {description}")
        keyword_factor = min(keyword_score / len(viral_keywords), 1.0)
        
        # Combine factors
        viral_potential = (save_rate * 0.6 + keyword_factor * 0.4)
        
        return min(viral_potential, 1.0)
        
    async def _calculate_monetization_score(
        self,
        pin: Dict[str, Any],
        pin_metrics: Dict[str, Any],
        quality_score: float
    ) -> float:
        """Calculate monetization potential score"""
        
        # Factors: clicks, link presence, engagement, quality
        clicks = pin_metrics.get('outbound_click', 0)
        impressions = pin_metrics.get('impression', 1)
        
        click_rate = clicks / impressions if impressions > 0 else 0
        has_link = 1.0 if pin.get('link') else 0.0
        engagement_rate = self._calculate_engagement_rate(pin_metrics)
        
        # Calculate monetization score
        monetization_score = (
            click_rate * 0.3 +
            has_link * 0.2 +
            engagement_rate * 0.3 +
            quality_score * 0.2
        )
        
        return min(monetization_score, 1.0)
        
    def _determine_board_category(self, board_info: Dict[str, Any]) -> BoardCategory:
        """Determine board category from board information"""
        
        board_name = board_info.get('name', '').lower()
        board_description = board_info.get('description', '').lower()
        
        content = f"{board_name} {board_description}"
        
        # Simple keyword-based categorization
        category_keywords = {
            BoardCategory.ART: ['art', 'drawing', 'painting', 'artwork', 'creative'],
            BoardCategory.FASHION: ['fashion', 'style', 'outfit', 'clothing', 'trend'],
            BoardCategory.FOOD: ['food', 'recipe', 'cooking', 'baking', 'meal'],
            BoardCategory.HOME: ['home', 'decor', 'interior', 'furniture', 'house'],
            BoardCategory.TRAVEL: ['travel', 'vacation', 'destination', 'trip', 'adventure'],
            BoardCategory.PHOTOGRAPHY: ['photo', 'photography', 'camera', 'picture', 'shot'],
            BoardCategory.DESIGN: ['design', 'graphic', 'ui', 'ux', 'layout'],
            BoardCategory.LIFESTYLE: ['lifestyle', 'life', 'inspiration', 'motivation', 'wellness'],
            BoardCategory.BUSINESS: ['business', 'marketing', 'entrepreneur', 'startup', 'finance'],
            BoardCategory.EDUCATION: ['education', 'learning', 'study', 'school', 'tutorial']
        }
        
        for category, keywords in category_keywords.items():
            if any(keyword in content for keyword in keywords):
                return category
                
        return BoardCategory.LIFESTYLE  # Default category
        
    async def _calculate_trend_score(
        self,
        pin: Dict[str, Any],
        category: BoardCategory
    ) -> float:
        """Calculate trend score based on current trends"""
        
        if not self.enable_trend_analysis:
            return 0.5  # Default neutral score
            
        # This would integrate with trend analysis systems
        # For now, return a simple score based on engagement timing
        created_at = pin.get('created_at', '')
        if created_at:
            try:
                pin_date = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                days_old = (datetime.now() - pin_date.replace(tzinfo=None)).days
                
                # Recent pins get higher trend scores
                if days_old <= 7:
                    return 0.9
                elif days_old <= 30:
                    return 0.7
                elif days_old <= 90:
                    return 0.5
                else:
                    return 0.3
                    
            except Exception:
                pass
                
        return 0.5
        
    async def crawl_trending_pins(
        self, 
        category: Optional[BoardCategory] = None,
        limit: int = 100
    ) -> List[PinterestPin]:
        """Crawl trending pins across Pinterest"""
        
        self.logger.info(f"Crawling trending pins, category: {category}, limit: {limit}")
        
        trending_pins = []
        
        try:
            async with self._create_session() as session:
                pins_data = await self._fetch_trending_pins(session, category, limit)
                
                for pin_data in pins_data:
                    pin = await self._process_pin(pin_data, {'name': 'trending', 'id': 'trending'})
                    if pin:
                        trending_pins.append(pin)
                        
        except Exception as e:
            self.logger.error(f"Error crawling trending pins: {str(e)}")
            
        return trending_pins[:limit]
        
    async def _fetch_trending_pins(
        self,
        session: aiohttp.ClientSession,
        category: Optional[BoardCategory],
        limit: int
    ) -> List[Dict[str, Any]]:
        """Fetch trending pins data"""
        
        url = "https://api.pinterest.com/v5/pins/search"
        
        params = {
            'query': 'trending',
            'fields': 'id,title,description,link,media,created_at,pin_metrics',
            'limit': min(limit, 50)
        }
        
        if category:
            params['category'] = category.value
            
        headers = await self._get_authenticated_headers()
        pins = []
        
        try:
            async with session.get(url, params=params, headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    pins = data.get('items', [])
                    
        except Exception as e:
            self.logger.error(f"Error fetching trending pins: {str(e)}")
            
        return pins
        
    async def search_pins(
        self, 
        query: str,
        pin_types: List[PinType] = None,
        category: Optional[BoardCategory] = None,
        filters: Dict[str, Any] = None
    ) -> List[PinterestPin]:
        """Search pins with advanced filtering"""
        
        self.logger.info(f"Searching pins: {query}")
        
        pin_types = pin_types or list(PinType)
        filters = filters or {}
        
        search_results = []
        
        try:
            async with self._create_session() as session:
                pins_data = await self._search_pins_api(session, query, category, filters)
                
                for pin_data in pins_data:
                    if self._matches_pin_type_filter(pin_data, pin_types):
                        pin = await self._process_pin(pin_data, {'name': 'search', 'id': 'search'})
                        if pin and self._matches_advanced_filters(pin, filters):
                            search_results.append(pin)
                            
        except Exception as e:
            self.logger.error(f"Error searching pins: {str(e)}")
            
        return search_results
        
    async def _search_pins_api(
        self,
        session: aiohttp.ClientSession,
        query: str,
        category: Optional[BoardCategory],
        filters: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Search pins using Pinterest API"""
        
        url = "https://api.pinterest.com/v5/pins/search"
        
        params = {
            'query': query,
            'fields': 'id,title,description,link,media,created_at,pin_metrics',
            'limit': filters.get('limit', 50)
        }
        
        if category:
            params['category'] = category.value
            
        headers = await self._get_authenticated_headers()
        pins = []
        
        try:
            async with session.get(url, params=params, headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    pins = data.get('items', [])
                    
        except Exception as e:
            self.logger.error(f"Error in search API: {str(e)}")
            
        return pins
        
    def _matches_advanced_filters(self, pin: PinterestPin, filters: Dict[str, Any]) -> bool:
        """Check if pin matches advanced filters"""
        
        if filters.get('min_saves') and pin.saves_count < filters['min_saves']:
            return False
            
        if filters.get('min_engagement') and pin.engagement_rate < filters['min_engagement']:
            return False
            
        if filters.get('min_viral_potential') and pin.viral_potential < filters['min_viral_potential']:
            return False
            
        if filters.get('has_link') and not pin.link_url:
            return False
            
        return True
        
    async def monitor_board_performance(
        self, 
        board_id: str,
        monitoring_period: timedelta = timedelta(days=30)
    ) -> Dict[str, Any]:
        """Monitor board performance metrics"""
        
        self.logger.info(f"Monitoring board performance: {board_id}")
        
        try:
            async with self._create_session() as session:
                # Get recent pins from board
                end_date = datetime.now()
                start_date = end_date - monitoring_period
                
                pins_metrics = []
                async for pin in self._crawl_board_pins(
                    session, board_id, list(PinType), (start_date, end_date)
                ):
                    processed_pin = await self._process_pin(pin, {'id': board_id, 'name': 'monitored'})
                    if processed_pin:
                        pins_metrics.append({
                            'engagement_rate': processed_pin.engagement_rate,
                            'viral_potential': processed_pin.viral_potential,
                            'monetization_score': processed_pin.monetization_score,
                            'trend_score': processed_pin.trend_score,
                            'saves_count': processed_pin.saves_count,
                            'impressions': processed_pin.impressions
                        })
                        
                # Calculate board metrics
                metrics = {
                    'total_pins': len(pins_metrics),
                    'avg_engagement_rate': sum(p['engagement_rate'] for p in pins_metrics) / len(pins_metrics) if pins_metrics else 0,
                    'avg_viral_potential': sum(p['viral_potential'] for p in pins_metrics) / len(pins_metrics) if pins_metrics else 0,
                    'avg_monetization_score': sum(p['monetization_score'] for p in pins_metrics) / len(pins_metrics) if pins_metrics else 0,
                    'avg_trend_score': sum(p['trend_score'] for p in pins_metrics) / len(pins_metrics) if pins_metrics else 0,
                    'total_saves': sum(p['saves_count'] for p in pins_metrics),
                    'total_impressions': sum(p['impressions'] for p in pins_metrics),
                    'board_growth_rate': self._calculate_board_growth_rate(pins_metrics),
                    'content_performance_distribution': self._analyze_content_performance(pins_metrics)
                }
                
                # Record monitoring metrics
                await self.metrics_collector.record_board_performance(board_id, metrics)
                
                return metrics
                
        except Exception as e:
            self.logger.error(f"Error monitoring board performance: {str(e)}")
            return {}
            
    def _calculate_board_growth_rate(self, pins_metrics: List[Dict[str, Any]]) -> float:
        """Calculate board growth rate based on recent activity"""
        
        if not pins_metrics:
            return 0.0
            
        # Simple growth calculation based on average metrics
        avg_engagement = sum(p['engagement_rate'] for p in pins_metrics) / len(pins_metrics)
        avg_viral = sum(p['viral_potential'] for p in pins_metrics) / len(pins_metrics)
        
        growth_rate = (avg_engagement * 0.6 + avg_viral * 0.4)
        return min(growth_rate, 1.0)
        
    def _analyze_content_performance(self, pins_metrics: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze content performance distribution"""
        
        if not pins_metrics:
            return {}
            
        # Categorize pins by performance
        high_performers = len([p for p in pins_metrics if p['engagement_rate'] > 0.7])
        medium_performers = len([p for p in pins_metrics if 0.3 < p['engagement_rate'] <= 0.7])
        low_performers = len([p for p in pins_metrics if p['engagement_rate'] <= 0.3])
        
        total = len(pins_metrics)
        
        return {
            'high_performers_ratio': high_performers / total,
            'medium_performers_ratio': medium_performers / total,
            'low_performers_ratio': low_performers / total,
            'top_monetization_pins': sorted(pins_metrics, key=lambda x: x['monetization_score'], reverse=True)[:5],
            'trending_pins': sorted(pins_metrics, key=lambda x: x['trend_score'], reverse=True)[:5]
        }
        
    async def _get_authenticated_headers(self) -> Dict[str, str]:
        """Get authenticated headers for API requests"""



        
        return {
            'User-Agent': 'Pinterest/1.0',
            'Accept': 'application/json',
            'Authorization': f'Bearer {self.config.get("access_token", "")}',
            'X-Pinterest-App-Id': self.config.get('app_id', '')
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
        
        # Pinterest has generous rate limits
        await asyncio.sleep(60 / self.rate_limit_per_minute)
