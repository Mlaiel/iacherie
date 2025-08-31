"""Rumble Content Crawling Engine

Advanced industry-grade engine for Rumble video platform crawling and content analysis.
Implements video content protection with AI-powered monetization and alternative platform strategy.

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
from ...core.platforms.rumble import RumblePlatform
from ...protection.content_guardian import ContentGuardian
from ...ai.content_analyzer import ContentAnalyzer
from ...security.encryption import SecurityManager
from ...monitoring.metrics import MetricsCollector


class VideoQuality(Enum):
    """Video quality levels"""
    LOW = "240p"
    MEDIUM = "480p"
    HIGH = "720p"
    HD = "1080p"
    UHD = "1440p"
    UHD_4K = "2160p"


class ContentCategory(Enum):
    """Rumble content categories"""
    NEWS = "news"
    POLITICS = "politics"
    ENTERTAINMENT = "entertainment"
    SPORTS = "sports"
    TECHNOLOGY = "technology"
    GAMING = "gaming"
    EDUCATION = "education"
    LIFESTYLE = "lifestyle"
    COMEDY = "comedy"
    MUSIC = "music"


@dataclass
class RumbleVideo:
    """Rumble video data structure"""
    video_id: str
    channel_id: str
    title: str
    description: str
    thumbnail_url: str
    video_url: str
    duration: int
    category: ContentCategory
    quality: VideoQuality
    views_count: int
    likes_count: int
    dislikes_count: int
    comments_count: int
    shares_count: int
    published_at: datetime
    engagement_rate: float
    monetization_potential: float
    viral_score: float
    content_fingerprint: str
    protection_level: str
    revenue_estimate: float


class RumbleEngine(BaseCrawlerEngine):
    """
    Professional Rumble crawling engine with advanced video content analysis
    and alternative platform monetization strategies.
    """
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.platform = RumblePlatform(config.get('rumble', {}))
        self.content_guardian = ContentGuardian()
        self.content_analyzer = ContentAnalyzer()
        self.security_manager = SecurityManager()
        self.metrics_collector = MetricsCollector()
        self.logger = logging.getLogger(__name__)
        
        # Rumble specific configuration
        self.rate_limit_per_minute = config.get('rate_limit_per_minute', 120)
        self.max_concurrent_requests = config.get('max_concurrent_requests', 8)
        self.content_quality_threshold = config.get('content_quality_threshold', 0.6)
        self.enable_monetization_analysis = config.get('enable_monetization_analysis', True)
        
    async def crawl_channel_videos(
        self, 
        channel_id: str, 
        categories: List[ContentCategory] = None,
        quality_filter: Optional[VideoQuality] = None,
        date_range: Optional[tuple] = None
    ) -> AsyncGenerator[RumbleVideo, None]:
        """
        Crawl videos from a specific Rumble channel with advanced filtering
        
        Args:
            channel_id: Channel identifier
            categories: List of content categories to crawl
            quality_filter: Optional video quality filter
            date_range: Optional date range tuple (start_date, end_date)
            
        Yields:
            RumbleVideo: Processed video objects
        """
        self.logger.info(f"Starting Rumble channel crawl: {channel_id}")
        
        try:
            async with self._create_session() as session:
                categories = categories or list(ContentCategory)
                
                # Get channel information first
                channel_info = await self._fetch_channel_info(session, channel_id)
                if not channel_info:
                    return
                    
                async for video in self._crawl_channel_videos_internal(
                    session, channel_id, categories, quality_filter, date_range
                ):
                    # Apply content protection and analysis
                    processed_video = await self._process_video(video, channel_info)
                    if processed_video:
                        yield processed_video
                        
        except Exception as e:
            self.logger.error(f"Error crawling channel videos: {str(e)}")
            await self.metrics_collector.record_error('rumble_crawl_error', str(e))
            raise
            
    async def _crawl_channel_videos_internal(
        self,
        session: aiohttp.ClientSession,
        channel_id: str,
        categories: List[ContentCategory],
        quality_filter: Optional[VideoQuality],
        date_range: Optional[tuple]
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """Internal method to crawl channel videos"""
        
        page = 1
        max_pages = 100
        
        while page <= max_pages:
            try:
                # Apply rate limiting
                await self._apply_rate_limiting()
                
                # Fetch videos page
                videos_data = await self._fetch_videos_page(
                    session, channel_id, page, date_range
                )
                
                if not videos_data or not videos_data.get('videos'):
                    break
                    
                for video in videos_data['videos']:
                    # Apply filters
                    if self._matches_filters(video, categories, quality_filter):
                        yield video
                        
                # Check for more pages
                if not videos_data.get('has_more', False):
                    break
                    
                page += 1
                
            except Exception as e:
                self.logger.error(f"Error fetching videos page {page}: {str(e)}")
                break
                
    async def _fetch_channel_info(
        self,
        session: aiohttp.ClientSession,
        channel_id: str
    ) -> Optional[Dict[str, Any]]:
        """Fetch channel information"""
        
        url = f"https://rumble.com/api/channel/{channel_id}"
        
        headers = await self._get_authenticated_headers()
        
        try:
            async with session.get(url, headers=headers) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    self.logger.error(f"Failed to fetch channel info: HTTP {response.status}")
                    return None
                    
        except Exception as e:
            self.logger.error(f"Error fetching channel info: {str(e)}")
            return None
            
    async def _fetch_videos_page(
        self,
        session: aiohttp.ClientSession,
        channel_id: str,
        page: int,
        date_range: Optional[tuple]
    ) -> Dict[str, Any]:
        """Fetch a single page of videos"""
        
        url = f"https://rumble.com/api/channel/{channel_id}/videos"
        
        params = {
            'page': page,
            'per_page': 25,
            'sort': 'date_desc'
        }
        
        if date_range:
            start_date, end_date = date_range
            params['from_date'] = start_date.strftime('%Y-%m-%d')
            params['to_date'] = end_date.strftime('%Y-%m-%d')
            
        headers = await self._get_authenticated_headers()
        
        try:
            async with session.get(url, params=params, headers=headers) as response:
                if response.status == 200:
                    return await response.json()
                elif response.status == 429:
                    # Rate limit hit, wait and retry
                    await asyncio.sleep(60)
                    return await self._fetch_videos_page(session, channel_id, page, date_range)
                else:
                    self.logger.error(f"HTTP {response.status}: {await response.text()}")
                    return {}
                    
        except Exception as e:
            self.logger.error(f"Request error: {str(e)}")
            return {}
            
    def _matches_filters(
        self,
        video: Dict[str, Any],
        categories: List[ContentCategory],
        quality_filter: Optional[VideoQuality]
    ) -> bool:
        """Check if video matches the specified filters"""
        
        # Category filter
        video_category = self._determine_video_category(video)
        if video_category not in categories:
            return False
            
        # Quality filter
        if quality_filter:
            video_quality = self._determine_video_quality(video)
            if video_quality != quality_filter:
                return False
                
        return True
        
    def _determine_video_category(self, video: Dict[str, Any]) -> ContentCategory:
        """Determine video category from metadata"""
        
        title = video.get('title', '').lower()
        description = video.get('description', '').lower()
        tags = ' '.join(video.get('tags', [])).lower()
        
        content = f"{title} {description} {tags}"
        
        # Simple keyword-based categorization
        category_keywords = {
            ContentCategory.NEWS: ['news', 'breaking', 'report', 'journalist', 'update'],
            ContentCategory.POLITICS: ['politics', 'election', 'government', 'policy', 'debate'],
            ContentCategory.ENTERTAINMENT: ['entertainment', 'celebrity', 'movie', 'show', 'star'],
            ContentCategory.SPORTS: ['sports', 'game', 'match', 'team', 'player', 'football', 'basketball'],
            ContentCategory.TECHNOLOGY: ['tech', 'technology', 'software', 'hardware', 'review', 'gadget'],
            ContentCategory.GAMING: ['gaming', 'game', 'gameplay', 'stream', 'esports', 'gamer'],
            ContentCategory.EDUCATION: ['education', 'tutorial', 'learn', 'course', 'lesson', 'how to'],
            ContentCategory.LIFESTYLE: ['lifestyle', 'vlog', 'daily', 'life', 'personal', 'family'],
            ContentCategory.COMEDY: ['comedy', 'funny', 'humor', 'joke', 'laugh', 'comic'],
            ContentCategory.MUSIC: ['music', 'song', 'album', 'artist', 'concert', 'band']
        }
        
        for category, keywords in category_keywords.items():
            if any(keyword in content for keyword in keywords):
                return category
                
        return ContentCategory.ENTERTAINMENT  # Default category
        
    def _determine_video_quality(self, video: Dict[str, Any]) -> VideoQuality:
        """Determine video quality from metadata"""
        
        # Check available quality levels
        quality_data = video.get('quality', {})
        available_qualities = list(quality_data.keys())
        
        # Return highest available quality
        quality_order = [VideoQuality.UHD_4K, VideoQuality.UHD, VideoQuality.HD, 
                        VideoQuality.HIGH, VideoQuality.MEDIUM, VideoQuality.LOW]
        
        for quality in quality_order:
            if quality.value in available_qualities:
                return quality
                
        return VideoQuality.MEDIUM  # Default quality
        
    async def _process_video(
        self, 
        raw_video: Dict[str, Any],
        channel_info: Dict[str, Any]
    ) -> Optional[RumbleVideo]:
        """Process and analyze video with advanced metrics"""
        
        try:
            video_id = raw_video.get('id')
            if not video_id:
                return None
                
            # Extract video information
            title = raw_video.get('title', '')
            description = raw_video.get('description', '')
            thumbnail_url = raw_video.get('thumbnail')
            video_url = raw_video.get('video_url')
            duration = raw_video.get('duration', 0)
            
            if not video_url:
                return None
                
            # Generate content fingerprint
            content_fingerprint = await self.content_guardian.generate_fingerprint(
                f"{title}{description}{video_url}"
            )
            
            # Analyze content quality
            quality_score = await self.content_analyzer.analyze_video_content({
                'title': title,
                'description': description,
                'duration': duration,
                'thumbnail_url': thumbnail_url
            })
            
            if quality_score < self.content_quality_threshold:
                return None
                
            # Extract metrics
            views_count = raw_video.get('views', 0)
            likes_count = raw_video.get('likes', 0)
            dislikes_count = raw_video.get('dislikes', 0)
            comments_count = raw_video.get('comments', 0)
            shares_count = raw_video.get('shares', 0)
            
            # Calculate engagement rate
            engagement_rate = self._calculate_engagement_rate(raw_video)
            
            # Calculate monetization potential
            monetization_potential = await self._calculate_monetization_potential(
                raw_video, channel_info, quality_score
            )
            
            # Calculate viral score
            viral_score = await self._calculate_viral_score(raw_video)
            
            # Estimate revenue
            revenue_estimate = await self._estimate_revenue(raw_video, monetization_potential)
            
            # Determine category and quality
            category = self._determine_video_category(raw_video)
            quality = self._determine_video_quality(raw_video)
            
            # Determine protection level
            protection_level = "premium" if monetization_potential > 0.7 else "standard"
            
            # Create Rumble video object
            rumble_video = RumbleVideo(
                video_id=video_id,
                channel_id=channel_info.get('id', ''),
                title=title,
                description=description[:1000],  # Limit description length
                thumbnail_url=thumbnail_url,
                video_url=video_url,
                duration=duration,
                category=category,
                quality=quality,
                views_count=views_count,
                likes_count=likes_count,
                dislikes_count=dislikes_count,
                comments_count=comments_count,
                shares_count=shares_count,
                published_at=datetime.fromisoformat(
                    raw_video.get('published_at', '').replace('Z', '+00:00')
                ),
                engagement_rate=engagement_rate,
                monetization_potential=monetization_potential,
                viral_score=viral_score,
                content_fingerprint=content_fingerprint,
                protection_level=protection_level,
                revenue_estimate=revenue_estimate
            )
            
            # Record metrics
            await self.metrics_collector.record_content_processed(
                platform='rumble',
                content_type='video',
                quality_score=quality_score
            )
            
            return rumble_video
            
        except Exception as e:
            self.logger.error(f"Error processing video: {str(e)}")
            return None
            
    def _calculate_engagement_rate(self, video: Dict[str, Any]) -> float:
        """Calculate engagement rate for the video"""
        
        views = video.get('views', 1)
        likes = video.get('likes', 0)
        dislikes = video.get('dislikes', 0)
        comments = video.get('comments', 0)
        shares = video.get('shares', 0)
        
        if views == 0:
            return 0.0
            
        # Weight different engagement types
        total_engagement = likes + (dislikes * 0.5) + (comments * 2) + (shares * 3)
        engagement_rate = total_engagement / views
        
        return min(engagement_rate, 1.0)  # Cap at 100%
        
    async def _calculate_monetization_potential(
        self,
        video: Dict[str, Any],
        channel_info: Dict[str, Any],
        quality_score: float
    ) -> float:
        """Calculate monetization potential for the video"""
        
        if not self.enable_monetization_analysis:
            return 0.5
            
        # Factors: views, engagement, channel size, content quality
        views = video.get('views', 0)
        engagement_rate = self._calculate_engagement_rate(video)
        channel_subscribers = channel_info.get('subscribers', 0)
        
        # Normalize factors
        views_score = min(views / 100000, 1.0)  # Max score at 100k views
        subscriber_score = min(channel_subscribers / 50000, 1.0)  # Max score at 50k subs
        
        # Calculate monetization potential
        monetization_potential = (
            views_score * 0.3 +
            engagement_rate * 0.3 +
            subscriber_score * 0.2 +
            quality_score * 0.2
        )
        
        return min(monetization_potential, 1.0)
        
    async def _calculate_viral_score(self, video: Dict[str, Any]) -> float:
        """Calculate viral potential score"""
        
        # Factors: rapid view growth, high engagement, shares
        views = video.get('views', 0)
        shares = video.get('shares', 0)
        engagement_rate = self._calculate_engagement_rate(video)
        
        # Calculate share rate
        share_rate = shares / views if views > 0 else 0
        
        # Check for viral indicators in content
        title = video.get('title', '').lower()
        viral_keywords = ['viral', 'trending', 'breaking', 'shocking', 'amazing', 'incredible']
        keyword_score = sum(1 for keyword in viral_keywords if keyword in title)
        keyword_factor = min(keyword_score / len(viral_keywords), 1.0)
        
        # Combine factors
        viral_score = (
            share_rate * 0.4 +
            engagement_rate * 0.4 +
            keyword_factor * 0.2
        )
        
        return min(viral_score, 1.0)
        
    async def _estimate_revenue(
        self,
        video: Dict[str, Any],
        monetization_potential: float
    ) -> float:
        """Estimate potential revenue for the video"""
        
        views = video.get('views', 0)
        
        # Rumble revenue model (simplified)
        # Typically lower CPM than YouTube but growing
        base_cpm = 1.5  # USD per 1000 views
        
        # Apply monetization potential multiplier
        effective_cpm = base_cpm * monetization_potential
        
        # Calculate estimated revenue
        revenue_estimate = (views / 1000) * effective_cpm
        
        return revenue_estimate
        
    async def crawl_trending_videos(
        self, 
        category: Optional[ContentCategory] = None,
        limit: int = 100
    ) -> List[RumbleVideo]:
        """Crawl trending videos on Rumble"""
        
        self.logger.info(f"Crawling trending videos, category: {category}, limit: {limit}")
        
        trending_videos = []
        
        try:
            async with self._create_session() as session:
                videos_data = await self._fetch_trending_videos(session, category, limit)
                
                for video_data in videos_data:
                    video = await self._process_video(video_data, {'id': 'trending'})
                    if video:
                        trending_videos.append(video)
                        
        except Exception as e:
            self.logger.error(f"Error crawling trending videos: {str(e)}")
            
        return trending_videos[:limit]
        
    async def _fetch_trending_videos(
        self,
        session: aiohttp.ClientSession,
        category: Optional[ContentCategory],
        limit: int
    ) -> List[Dict[str, Any]]:
        """Fetch trending videos data"""
        
        url = "https://rumble.com/api/trending"
        
        params = {
            'limit': min(limit, 50),
            'time_range': '24h'
        }
        
        if category:
            params['category'] = category.value
            
        headers = await self._get_authenticated_headers()
        videos = []
        
        try:
            async with session.get(url, params=params, headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    videos = data.get('videos', [])
                    
        except Exception as e:
            self.logger.error(f"Error fetching trending videos: {str(e)}")
            
        return videos
        
    async def search_videos(
        self, 
        query: str,
        categories: List[ContentCategory] = None,
        quality_filter: Optional[VideoQuality] = None,
        filters: Dict[str, Any] = None
    ) -> List[RumbleVideo]:
        """Search videos with advanced filtering"""
        
        self.logger.info(f"Searching videos: {query}")
        
        categories = categories or list(ContentCategory)
        filters = filters or {}
        
        search_results = []
        
        try:
            async with self._create_session() as session:
                videos_data = await self._search_videos_api(session, query, filters)
                
                for video_data in videos_data:
                    if self._matches_filters(video_data, categories, quality_filter):
                        video = await self._process_video(video_data, {'id': 'search'})
                        if video and self._matches_advanced_filters(video, filters):
                            search_results.append(video)
                            
        except Exception as e:
            self.logger.error(f"Error searching videos: {str(e)}")
            
        return search_results
        
    async def _search_videos_api(
        self,
        session: aiohttp.ClientSession,
        query: str,
        filters: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Search videos using Rumble API"""
        
        url = "https://rumble.com/api/search"
        
        params = {
            'q': query,
            'type': 'video',
            'limit': filters.get('limit', 50),
            'sort': filters.get('sort', 'relevance')
        }
        
        headers = await self._get_authenticated_headers()
        videos = []
        
        try:
            async with session.get(url, params=params, headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    videos = data.get('videos', [])
                    
        except Exception as e:
            self.logger.error(f"Error in search API: {str(e)}")
            
        return videos
        
    def _matches_advanced_filters(self, video: RumbleVideo, filters: Dict[str, Any]) -> bool:
        """Check if video matches advanced filters"""
        
        if filters.get('min_views') and video.views_count < filters['min_views']:
            return False
            
        if filters.get('min_engagement') and video.engagement_rate < filters['min_engagement']:
            return False
            
        if filters.get('min_duration') and video.duration < filters['min_duration']:
            return False
            
        if filters.get('max_duration') and video.duration > filters['max_duration']:
            return False
            
        return True
        
    async def monitor_channel_performance(
        self, 
        channel_id: str,
        monitoring_period: timedelta = timedelta(days=30)
    ) -> Dict[str, Any]:
        """Monitor channel performance metrics"""
        
        self.logger.info(f"Monitoring channel performance: {channel_id}")
        
        try:
            async with self._create_session() as session:
                # Get channel info
                channel_info = await self._fetch_channel_info(session, channel_id)
                if not channel_info:
                    return {}
                    
                # Get recent videos
                end_date = datetime.now()
                start_date = end_date - monitoring_period
                
                videos_metrics = []
                async for video in self.crawl_channel_videos(
                    channel_id, date_range=(start_date, end_date)
                ):
                    videos_metrics.append({
                        'views': video.views_count,
                        'engagement_rate': video.engagement_rate,
                        'monetization_potential': video.monetization_potential,
                        'viral_score': video.viral_score,
                        'revenue_estimate': video.revenue_estimate,
                        'category': video.category.value,
                        'duration': video.duration
                    })
                    
                # Calculate channel metrics
                metrics = {
                    'total_videos': len(videos_metrics),
                    'total_views': sum(v['views'] for v in videos_metrics),
                    'avg_engagement_rate': sum(v['engagement_rate'] for v in videos_metrics) / len(videos_metrics) if videos_metrics else 0,
                    'avg_monetization_potential': sum(v['monetization_potential'] for v in videos_metrics) / len(videos_metrics) if videos_metrics else 0,
                    'avg_viral_score': sum(v['viral_score'] for v in videos_metrics) / len(videos_metrics) if videos_metrics else 0,
                    'total_revenue_estimate': sum(v['revenue_estimate'] for v in videos_metrics),
                    'category_distribution': self._calculate_category_distribution(videos_metrics),
                    'content_performance_analysis': self._analyze_content_performance(videos_metrics),
                    'growth_metrics': await self._calculate_growth_metrics(channel_info, videos_metrics)
                }
                
                # Record monitoring metrics
                await self.metrics_collector.record_channel_performance(channel_id, metrics)
                
                return metrics
                
        except Exception as e:
            self.logger.error(f"Error monitoring channel performance: {str(e)}")
            return {}
            
    def _calculate_category_distribution(self, videos_metrics: List[Dict[str, Any]]) -> Dict[str, float]:
        """Calculate category distribution"""
        
        if not videos_metrics:
            return {}
            
        total = len(videos_metrics)
        distribution = {}
        
        for category in ContentCategory:
            count = len([v for v in videos_metrics if v['category'] == category.value])
            distribution[category.value] = count / total
            
        return distribution
        
    def _analyze_content_performance(self, videos_metrics: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze content performance patterns"""
        
        if not videos_metrics:
            return {}
            
        # Performance tiers
        high_performers = [v for v in videos_metrics if v['engagement_rate'] > 0.7]
        medium_performers = [v for v in videos_metrics if 0.3 < v['engagement_rate'] <= 0.7]
        low_performers = [v for v in videos_metrics if v['engagement_rate'] <= 0.3]
        
        return {
            'high_performers_count': len(high_performers),
            'medium_performers_count': len(medium_performers),
            'low_performers_count': len(low_performers),
            'top_performing_categories': self._get_top_categories(high_performers),
            'optimal_duration_range': self._calculate_optimal_duration(high_performers),
            'revenue_leaders': sorted(videos_metrics, key=lambda x: x['revenue_estimate'], reverse=True)[:5]
        }
        
    def _get_top_categories(self, high_performers: List[Dict[str, Any]]) -> List[str]:
        """Get top performing categories"""
        
        if not high_performers:
            return []
            
        category_counts = {}
        for video in high_performers:
            category = video['category']
            category_counts[category] = category_counts.get(category, 0) + 1
            
        return sorted(category_counts.keys(), key=lambda x: category_counts[x], reverse=True)
        
    def _calculate_optimal_duration(self, high_performers: List[Dict[str, Any]]) -> Dict[str, int]:
        """Calculate optimal video duration range"""
        
        if not high_performers:
            return {'min': 0, 'max': 0}
            
        durations = [v['duration'] for v in high_performers]
        
        return {
            'min': min(durations),
            'max': max(durations),
            'avg': sum(durations) // len(durations)
        }
        
    async def _calculate_growth_metrics(
        self,
        channel_info: Dict[str, Any],
        videos_metrics: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Calculate channel growth metrics"""
        
        if not videos_metrics:
            return {}
            
        # Simple growth calculations
        recent_videos = sorted(videos_metrics, key=lambda x: x.get('published_at', ''), reverse=True)[:10]
        older_videos = videos_metrics[10:] if len(videos_metrics) > 10 else []
        
        recent_avg_views = sum(v['views'] for v in recent_videos) / len(recent_videos) if recent_videos else 0
        older_avg_views = sum(v['views'] for v in older_videos) / len(older_videos) if older_videos else recent_avg_views
        
        growth_rate = (recent_avg_views - older_avg_views) / older_avg_views if older_avg_views > 0 else 0
        
        return {
            'view_growth_rate': growth_rate,
            'recent_avg_views': recent_avg_views,
            'channel_momentum': min(growth_rate + 1, 2.0),  # Normalized momentum score
            'consistency_score': self._calculate_consistency_score(videos_metrics)
        }
        
    def _calculate_consistency_score(self, videos_metrics: List[Dict[str, Any]]) -> float:
        """Calculate content consistency score"""
        
        if len(videos_metrics) < 3:
            return 0.5
            
        # Calculate variance in engagement rates
        engagement_rates = [v['engagement_rate'] for v in videos_metrics]
        avg_engagement = sum(engagement_rates) / len(engagement_rates)
        
        variance = sum((rate - avg_engagement) ** 2 for rate in engagement_rates) / len(engagement_rates)
        consistency_score = 1 / (1 + variance)  # Higher consistency = lower variance
        
        return min(consistency_score, 1.0)
        
    async def _get_authenticated_headers(self) -> Dict[str, str]:
        """Get authenticated headers for API requests"""
        
        return {
            'User-Agent': 'Rumble/1.0',
            'Accept': 'application/json',
            'Authorization': f'Bearer {self.config.get("access_token", "")}',
            'X-Rumble-Client': self.config.get('client_id', '')
        }
        
    async def _create_session(self) -> aiohttp.ClientSession:
        """Create configured HTTP session"""
        
        connector = aiohttp.TCPConnector(
            limit=self.max_concurrent_requests,
            limit_per_host=self.max_concurrent_requests
        )
        
        timeout = aiohttp.ClientTimeout(total=45)
        
        return aiohttp.ClientSession(
            connector=connector,
            timeout=timeout
        )
        
    async def _apply_rate_limiting(self):
        """Apply rate limiting to prevent API abuse"""
        
        await asyncio.sleep(60 / self.rate_limit_per_minute)
