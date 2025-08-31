"""
Threads Content Crawling Engine

Advanced industry-grade engine for Meta Threads content crawling and social analysis.
Implements real-time conversation tracking with AI-powered engagement optimization.

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
from ...core.platforms.threads import ThreadsPlatform
from ...protection.content_guardian import ContentGuardian
from ...ai.content_analyzer import ContentAnalyzer
from ...security.encryption import SecurityManager
from ...monitoring.metrics import MetricsCollector


class ThreadType(Enum):
    """Thread content types"""
    TEXT = "text"
    IMAGE = "image"
    VIDEO = "video"
    CAROUSEL = "carousel"
    REPOST = "repost"
    QUOTE = "quote"
    POLL = "poll"


class ConversationStatus(Enum):
    """Conversation status"""
    ACTIVE = "active"
    TRENDING = "trending"
    VIRAL = "viral"
    DECLINING = "declining"
    ENDED = "ended"


@dataclass
class ThreadsPost:
    """Threads post data structure"""
    post_id: str
    user_id: str
    username: str
    thread_type: ThreadType
    content: str
    media_urls: List[str]
    parent_post_id: Optional[str]
    conversation_id: str
    likes_count: int
    replies_count: int
    reposts_count: int
    quotes_count: int
    views_count: int
    created_at: datetime
    engagement_rate: float
    conversation_momentum: float
    viral_potential: float
    sentiment_score: float
    content_fingerprint: str
    protection_level: str
    monetization_potential: float


class ThreadsEngine(BaseCrawlerEngine):
    """
    Professional Threads crawling engine with advanced conversation analysis
    and real-time engagement optimization for social media creators.
    """
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.platform = ThreadsPlatform(config.get('threads', {}))
        self.content_guardian = ContentGuardian()
        self.content_analyzer = ContentAnalyzer()
        self.security_manager = SecurityManager()
        self.metrics_collector = MetricsCollector()
        self.logger = logging.getLogger(__name__)
        
        # Threads specific configuration
        self.rate_limit_per_minute = config.get('rate_limit_per_minute', 250)
        self.max_concurrent_requests = config.get('max_concurrent_requests', 15)
        self.content_quality_threshold = config.get('content_quality_threshold', 0.6)
        self.enable_conversation_analysis = config.get('enable_conversation_analysis', True)
        self.real_time_monitoring = config.get('real_time_monitoring', True)
        
    async def crawl_user_threads(
        self, 
        user_id: str, 
        thread_types: List[ThreadType] = None,
        include_replies: bool = True,
        date_range: Optional[tuple] = None
    ) -> AsyncGenerator[ThreadsPost, None]:
        """
        Crawl threads from a specific user with conversation context
        
        Args:
            user_id: User identifier
            thread_types: List of thread types to crawl
            include_replies: Whether to include reply threads
            date_range: Optional date range tuple (start_date, end_date)
            
        Yields:
            ThreadsPost: Processed thread objects
        """
        self.logger.info(f"Starting Threads crawl for user: {user_id}")
        
        try:
            async with self._create_session() as session:
                thread_types = thread_types or list(ThreadType)
                
                # Get user's threads
                async for thread in self._crawl_user_threads_internal(
                    session, user_id, thread_types, include_replies, date_range
                ):
                    # Apply content protection and analysis
                    processed_thread = await self._process_thread(thread)
                    if processed_thread:
                        yield processed_thread
                        
        except Exception as e:
            self.logger.error(f"Error crawling user threads: {str(e)}")
            await self.metrics_collector.record_error('threads_crawl_error', str(e))
            raise
            
    async def _crawl_user_threads_internal(
        self,
        session: aiohttp.ClientSession,
        user_id: str,
        thread_types: List[ThreadType],
        include_replies: bool,
        date_range: Optional[tuple]
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """Internal method to crawl user threads"""
        
        max_id = None
        max_pages = 50
        page_count = 0
        
        while page_count < max_pages:
            try:
                # Apply rate limiting
                await self._apply_rate_limiting()
                
                # Fetch threads page
                threads_data = await self._fetch_threads_page(
                    session, user_id, max_id, include_replies, date_range
                )
                
                if not threads_data or not threads_data.get('data'):
                    break
                    
                for thread in threads_data['data']:
                    # Apply thread type filter
                    if self._matches_thread_type_filter(thread, thread_types):
                        yield thread
                        
                # Get pagination info
                pagination = threads_data.get('paging', {})
                max_id = pagination.get('cursors', {}).get('after')
                
                if not max_id:
                    break
                    
                page_count += 1
                
            except Exception as e:
                self.logger.error(f"Error fetching threads page {page_count}: {str(e)}")
                break
                
    async def _fetch_threads_page(
        self,
        session: aiohttp.ClientSession,
        user_id: str,
        max_id: Optional[str],
        include_replies: bool,
        date_range: Optional[tuple]
    ) -> Dict[str, Any]:
        """Fetch a single page of threads"""
        
        url = f"https://graph.threads.net/v1.0/{user_id}/threads"
        
        params = {
            'fields': 'id,media_type,media_url,permalink,username,text,timestamp,shortcode,thumbnail_url,children,is_quote_post',
            'limit': 25
        }
        
        if max_id:
            params['after'] = max_id
            
        if not include_replies:
            params['exclude_replies'] = 'true'
            
        if date_range:
            start_date, end_date = date_range
            params['since'] = int(start_date.timestamp())
            params['until'] = int(end_date.timestamp())
            
        headers = await self._get_authenticated_headers()
        
        try:
            async with session.get(url, params=params, headers=headers) as response:
                if response.status == 200:
                    return await response.json()
                elif response.status == 429:
                    # Rate limit hit, wait and retry
                    await asyncio.sleep(60)
                    return await self._fetch_threads_page(
                        session, user_id, max_id, include_replies, date_range
                    )
                else:
                    self.logger.error(f"HTTP {response.status}: {await response.text()}")
                    return {}
                    
        except Exception as e:
            self.logger.error(f"Request error: {str(e)}")
            return {}
            
    def _matches_thread_type_filter(self, thread: Dict[str, Any], thread_types: List[ThreadType]) -> bool:
        """Check if thread matches the thread type filter"""
        
        thread_type = self._determine_thread_type(thread)
        return thread_type in thread_types
        
    def _determine_thread_type(self, thread: Dict[str, Any]) -> ThreadType:
        """Determine thread type from thread data"""
        
        media_type = thread.get('media_type', 'TEXT')
        has_children = thread.get('children', {}).get('data', [])
        is_quote = thread.get('is_quote_post', False)
        
        if is_quote:
            return ThreadType.QUOTE
        elif media_type == 'VIDEO':
            return ThreadType.VIDEO
        elif media_type == 'IMAGE':
            if has_children:
                return ThreadType.CAROUSEL
            else:
                return ThreadType.IMAGE
        elif media_type == 'CAROUSEL_ALBUM':
            return ThreadType.CAROUSEL
        else:
            return ThreadType.TEXT
            
    async def _process_thread(self, raw_thread: Dict[str, Any]) -> Optional[ThreadsPost]:
        """Process and analyze thread with conversation context"""



        
        try:
            post_id = raw_thread.get('id')
            if not post_id:
                return None
                
            # Extract thread information
            username = raw_thread.get('username', '')
            content = raw_thread.get('text', '')
            thread_type = self._determine_thread_type(raw_thread)
            
            # Extract media URLs
            media_urls = self._extract_media_urls(raw_thread)
            
            # Get conversation context
            conversation_id = await self._get_conversation_id(raw_thread)
            parent_post_id = raw_thread.get('parent_id')
            
            # Generate content fingerprint
            content_fingerprint = await self.content_guardian.generate_fingerprint(
                f"{content}{''.join(media_urls)}{username}"
            )
            
            # Analyze content quality
            quality_score = await self.content_analyzer.analyze_social_content({
                'text': content,
                'media_urls': media_urls,
                'thread_type': thread_type.value,
                'username': username
            })
            
            if quality_score < self.content_quality_threshold:
                return None
                
            # Get engagement metrics (would need to fetch from insights API)
            engagement_metrics = await self._fetch_engagement_metrics(post_id)
            
            # Calculate engagement rate
            engagement_rate = self._calculate_engagement_rate(engagement_metrics)
            
            # Analyze conversation momentum
            conversation_momentum = await self._analyze_conversation_momentum(
                conversation_id, post_id
            )
            
            # Calculate viral potential
            viral_potential = await self._calculate_viral_potential(
                raw_thread, engagement_metrics
            )
            
            # Analyze sentiment
            sentiment_score = await self._analyze_sentiment(content)
            
            # Calculate monetization potential
            monetization_potential = await self._calculate_monetization_potential(
                raw_thread, engagement_metrics, quality_score
            )
            
            # Determine protection level
            protection_level = "premium" if monetization_potential > 0.7 else "standard"
            
            # Create Threads post object
            threads_post = ThreadsPost(
                post_id=post_id,
                user_id=raw_thread.get('user_id', ''),
                username=username,
                thread_type=thread_type,
                content=content,
                media_urls=media_urls,
                parent_post_id=parent_post_id,
                conversation_id=conversation_id,
                likes_count=engagement_metrics.get('likes', 0),
                replies_count=engagement_metrics.get('replies', 0),
                reposts_count=engagement_metrics.get('reposts', 0),
                quotes_count=engagement_metrics.get('quotes', 0),
                views_count=engagement_metrics.get('views', 0),
                created_at=datetime.fromisoformat(
                    raw_thread.get('timestamp', '').replace('Z', '+00:00')
                ),
                engagement_rate=engagement_rate,
                conversation_momentum=conversation_momentum,
                viral_potential=viral_potential,
                sentiment_score=sentiment_score,
                content_fingerprint=content_fingerprint,
                protection_level=protection_level,
                monetization_potential=monetization_potential
            )
            
            # Record metrics
            await self.metrics_collector.record_content_processed(
                platform='threads',
                content_type=thread_type.value,
                quality_score=quality_score
            )
            
            return threads_post
            
        except Exception as e:
            self.logger.error(f"Error processing thread: {str(e)}")
            return None
            
    def _extract_media_urls(self, thread: Dict[str, Any]) -> List[str]:
        """Extract media URLs from thread"""
        
        urls = []
        
        # Main media URL
        media_url = thread.get('media_url')
        if media_url:
            urls.append(media_url)
            
        # Thumbnail URL
        thumbnail_url = thread.get('thumbnail_url')
        if thumbnail_url:
            urls.append(thumbnail_url)
            
        # Children media (for carousels)
        children = thread.get('children', {}).get('data', [])
        for child in children:
            child_media = child.get('media_url')
            if child_media:
                urls.append(child_media)
                
        return urls
        
    async def _get_conversation_id(self, thread: Dict[str, Any]) -> str:
        """Get or generate conversation ID for thread grouping"""
        
        # If it's a reply, find the root thread
        parent_id = thread.get('parent_id')
        if parent_id:
            # Would need to recursively find root thread
            return f"conv_{parent_id}"
        else:
            # Root thread creates new conversation
            return f"conv_{thread.get('id', '')}"
            
    async def _fetch_engagement_metrics(self, post_id: str) -> Dict[str, int]:
        """Fetch engagement metrics for a post"""
        
        # This would use Threads Insights API
        # Placeholder implementation
        return {
            'likes': 0,
            'replies': 0,
            'reposts': 0,
            'quotes': 0,
            'views': 0
        }
        
    def _calculate_engagement_rate(self, metrics: Dict[str, int]) -> float:
        """Calculate engagement rate from metrics"""
        
        views = metrics.get('views', 1)
        likes = metrics.get('likes', 0)
        replies = metrics.get('replies', 0)
        reposts = metrics.get('reposts', 0)
        quotes = metrics.get('quotes', 0)
        
        if views == 0:
            return 0.0
            
        # Weight different engagement types
        total_engagement = likes + (replies * 2) + (reposts * 1.5) + (quotes * 2)
        engagement_rate = total_engagement / views
        
        return min(engagement_rate, 1.0)  # Cap at 100%
        
    async def _analyze_conversation_momentum(
        self, 
        conversation_id: str,
        post_id: str
    ) -> float:
        """Analyze the momentum of the conversation this thread is part of"""
        
        if not self.enable_conversation_analysis:
            return 0.5
            
        try:
            # Get recent activity in conversation
            conversation_data = await self._fetch_conversation_data(conversation_id)
            
            # Calculate momentum based on recent activity
            recent_replies = len([
                r for r in conversation_data.get('replies', [])
                if self._is_recent_activity(r.get('timestamp', ''))
            ])
            
            # Calculate reply velocity
            time_span = self._calculate_conversation_timespan(conversation_data)
            reply_velocity = recent_replies / max(time_span, 1)
            
            # Normalize momentum score
            momentum = min(reply_velocity / 10, 1.0)
            
            return momentum
            
        except Exception as e:
            self.logger.error(f"Error analyzing conversation momentum: {str(e)}")
            return 0.5
            
    async def _fetch_conversation_data(self, conversation_id: str) -> Dict[str, Any]:
        """Fetch conversation data and replies"""
        
        # This would fetch the full conversation thread
        # Placeholder implementation
        return {
            'replies': [],
            'participants': [],
            'start_time': datetime.now().isoformat()
        }
        
    def _is_recent_activity(self, timestamp: str) -> bool:
        """Check if activity is recent (within last hour)"""



        
        try:
            activity_time = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
            cutoff_time = datetime.now() - timedelta(hours=1)
            return activity_time.replace(tzinfo=None) > cutoff_time
        except Exception:
            return False
            
    def _calculate_conversation_timespan(self, conversation_data: Dict[str, Any]) -> float:
        """Calculate conversation timespan in hours"""



        
        try:
            start_time = datetime.fromisoformat(
                conversation_data.get('start_time', '').replace('Z', '+00:00')
            )
            timespan = (datetime.now() - start_time.replace(tzinfo=None)).total_seconds() / 3600
            return max(timespan, 1.0)
        except Exception:
            return 1.0
            
    async def _calculate_viral_potential(
        self,
        thread: Dict[str, Any],
        metrics: Dict[str, int]
    ) -> float:
        """Calculate viral potential for the thread"""
        
        # Factors: engagement rate, repost velocity, content type
        engagement_rate = self._calculate_engagement_rate(metrics)
        reposts = metrics.get('reposts', 0)
        views = metrics.get('views', 1)
        
        # Repost rate is strong viral indicator
        repost_rate = reposts / views if views > 0 else 0
        
        # Content factors
        content = thread.get('text', '').lower()
        viral_keywords = ['breaking', 'urgent', 'wow', 'incredible', 'shocking', 'viral']
        keyword_score = sum(1 for keyword in viral_keywords if keyword in content)
        keyword_factor = min(keyword_score / len(viral_keywords), 1.0)
        
        # Media boost
        has_media = bool(thread.get('media_url'))
        media_boost = 0.2 if has_media else 0.0
        
        # Combine factors
        viral_potential = (
            engagement_rate * 0.4 +
            repost_rate * 0.3 +
            keyword_factor * 0.2 +
            media_boost * 0.1
        )
        
        return min(viral_potential, 1.0)
        
    async def _analyze_sentiment(self, content: str) -> float:
        """Analyze sentiment of the content"""
        
        # This would use advanced sentiment analysis
        # Placeholder implementation with simple keyword analysis
        positive_words = ['great', 'amazing', 'love', 'awesome', 'fantastic', 'excellent']
        negative_words = ['hate', 'terrible', 'awful', 'bad', 'worst', 'horrible']
        
        content_lower = content.lower()
        
        positive_count = sum(1 for word in positive_words if word in content_lower)
        negative_count = sum(1 for word in negative_words if word in content_lower)
        
        if positive_count + negative_count == 0:
            return 0.5  # Neutral
            
        sentiment = positive_count / (positive_count + negative_count)
        return sentiment
        
    async def _calculate_monetization_potential(
        self,
        thread: Dict[str, Any],
        metrics: Dict[str, int],
        quality_score: float
    ) -> float:
        """Calculate monetization potential for the thread"""
        
        # Factors: engagement, reach, content quality, brand safety
        engagement_rate = self._calculate_engagement_rate(metrics)
        views = metrics.get('views', 0)
        
        # Reach score
        reach_score = min(views / 10000, 1.0)  # Max score at 10k views
        
        # Brand safety check
        content = thread.get('text', '').lower()
        brand_unsafe_words = ['controversial', 'political', 'nsfw', 'adult']
        brand_safety = 1.0 - (0.3 * sum(1 for word in brand_unsafe_words if word in content))
        brand_safety = max(brand_safety, 0.0)
        
        # Professional content indicators
        professional_keywords = ['business', 'tips', 'advice', 'tutorial', 'guide']
        professional_score = min(
            sum(1 for keyword in professional_keywords if keyword in content) / len(professional_keywords),
            1.0
        )
        
        # Combine factors
        monetization_potential = (
            engagement_rate * 0.3 +
            reach_score * 0.2 +
            quality_score * 0.2 +
            brand_safety * 0.15 +
            professional_score * 0.15
        )
        
        return min(monetization_potential, 1.0)
        
    async def crawl_trending_threads(
        self, 
        limit: int = 100,
        time_range: str = '24h'
    ) -> List[ThreadsPost]:
        """Crawl trending threads across the platform"""
        
        self.logger.info(f"Crawling trending threads, limit: {limit}")
        
        trending_threads = []
        
        try:
            async with self._create_session() as session:
                threads_data = await self._fetch_trending_threads(session, limit, time_range)
                
                for thread_data in threads_data:
                    thread = await self._process_thread(thread_data)
                    if thread:
                        trending_threads.append(thread)
                        
        except Exception as e:
            self.logger.error(f"Error crawling trending threads: {str(e)}")
            
        return trending_threads[:limit]
        
    async def _fetch_trending_threads(
        self,
        session: aiohttp.ClientSession,
        limit: int,
        time_range: str
    ) -> List[Dict[str, Any]]:
        """Fetch trending threads data"""
        
        # This would use Threads trending API
        # Placeholder implementation
        return []
        
    async def monitor_real_time_conversations(
        self, 
        keywords: List[str],
        monitoring_duration: timedelta = timedelta(hours=1)
    ) -> Dict[str, Any]:
        """Monitor real-time conversations around specific keywords"""
        
        self.logger.info(f"Monitoring real-time conversations for: {keywords}")
        
        if not self.real_time_monitoring:
            return {}
            
        monitoring_results = {
            'keywords': keywords,
            'monitoring_duration': monitoring_duration.total_seconds(),
            'conversations_tracked': [],
            'trending_topics': [],
            'engagement_patterns': {},
            'sentiment_analysis': {},
            'viral_moments': []
        }
        
        start_time = datetime.now()
        end_time = start_time + monitoring_duration
        
        try:
            while datetime.now() < end_time:
                # Search for recent threads containing keywords
                for keyword in keywords:
                    conversations = await self._search_keyword_conversations(keyword)
                    monitoring_results['conversations_tracked'].extend(conversations)
                    
                # Analyze patterns every 10 minutes
                await asyncio.sleep(600)  # 10 minutes
                
                # Update monitoring results
                monitoring_results['trending_topics'] = await self._identify_trending_topics(
                    monitoring_results['conversations_tracked']
                )
                
                monitoring_results['engagement_patterns'] = await self._analyze_engagement_patterns(
                    monitoring_results['conversations_tracked']
                )
                
        except Exception as e:
            self.logger.error(f"Error in real-time monitoring: {str(e)}")
            
        return monitoring_results
        
    async def _search_keyword_conversations(self, keyword: str) -> List[Dict[str, Any]]:
        """Search for conversations containing specific keyword"""
        
        # This would use Threads search API
        # Placeholder implementation
        return []
        
    async def _identify_trending_topics(self, conversations: List[Dict[str, Any]]) -> List[str]:
        """Identify trending topics from conversations"""
        
        # Analyze conversation content for trending topics
        # Placeholder implementation
        return ['ai', 'technology', 'social media']
        
    async def _analyze_engagement_patterns(self, conversations: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze engagement patterns from conversations"""
        
        if not conversations:
            return {}
            
        # Calculate engagement metrics
        total_engagements = sum(
            conv.get('likes', 0) + conv.get('replies', 0) + conv.get('reposts', 0)
            for conv in conversations
        )
        
        avg_engagement = total_engagements / len(conversations) if conversations else 0
        
        return {
            'total_conversations': len(conversations),
            'avg_engagement_per_thread': avg_engagement,
            'peak_engagement_time': datetime.now().hour,
            'conversation_velocity': len(conversations) / max(1, len(conversations) // 10)
        }
        
    async def _get_authenticated_headers(self) -> Dict[str, str]:
        """Get authenticated headers for API requests"""



        
        return {
            'User-Agent': 'Threads/1.0',
            'Accept': 'application/json',
            'Authorization': f'Bearer {self.config.get("access_token", "")}',
            'X-Threads-App-Id': self.config.get('app_id', '')
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
        
        await asyncio.sleep(60 / self.rate_limit_per_minute)
