"""Patreon Content Crawling Engine

Advanced industry-grade engine for Patreon content crawling and creator support.
Implements subscription-based content management with AI-powered monetization.

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
from ...core.platforms.patreon import PatreonPlatform
from ...protection.content_guardian import ContentGuardian
from ...ai.content_analyzer import ContentAnalyzer
from ...security.encryption import SecurityManager
from ...monitoring.metrics import MetricsCollector


class PatreonTier(Enum):
    """Patreon subscription tiers"""
    FREE = "free"
    BRONZE = "bronze"
    SILVER = "silver"
    GOLD = "gold"
    PLATINUM = "platinum"
    DIAMOND = "diamond"


class ContentAccessLevel(Enum):
    """Content access levels"""
    PUBLIC = "public"
    PATRON_ONLY = "patron_only"
    TIER_LOCKED = "tier_locked"
    EXCLUSIVE = "exclusive"


@dataclass
class PatreonContent:
    """Patreon content data structure"""
    content_id: str
    creator_id: str
    title: str
    description: str
    content_type: str
    media_urls: List[str]
    thumbnail_url: Optional[str]
    tier_requirement: PatreonTier
    access_level: ContentAccessLevel
    monthly_cost: float
    patron_count: int
    likes_count: int
    comments_count: int
    published_at: datetime
    engagement_rate: float
    revenue_potential: float
    content_fingerprint: str
    protection_level: str
    monetization_tier: str


class PatreonEngine(BaseCrawlerEngine):
    """
    Professional Patreon crawling engine with advanced creator monetization
    and subscription management features.
    """
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.platform = PatreonPlatform(config.get('patreon', {}))
        self.content_guardian = ContentGuardian()
        self.content_analyzer = ContentAnalyzer()
        self.security_manager = SecurityManager()
        self.metrics_collector = MetricsCollector()
        self.logger = logging.getLogger(__name__)
        
        # Patreon specific configuration
        self.rate_limit_per_minute = config.get('rate_limit_per_minute', 60)
        self.max_concurrent_requests = config.get('max_concurrent_requests', 10)
        self.content_quality_threshold = config.get('content_quality_threshold', 0.7)
        self.enable_revenue_tracking = config.get('enable_revenue_tracking', True)
        
    async def crawl_creator_content(
        self, 
        creator_id: str, 
        tier_filter: Optional[PatreonTier] = None,
        access_level: Optional[ContentAccessLevel] = None,
        date_range: Optional[tuple] = None
    ) -> AsyncGenerator[PatreonContent, None]:
        """
        Crawl content from a specific Patreon creator with tier filtering
        
        Args:
            creator_id: Creator identifier
            tier_filter: Optional tier filter
            access_level: Optional access level filter
            date_range: Optional date range tuple (start_date, end_date)
            
        Yields:
            PatreonContent: Processed content objects
        """
        self.logger.info(f"Starting Patreon content crawl for creator: {creator_id}")
        
        try:
            async with self._create_session() as session:
                # Get creator information first
                creator_info = await self._fetch_creator_info(session, creator_id)
                if not creator_info:
                    return
                    
                # Crawl posts with filtering
                async for content in self._crawl_creator_posts(
                    session, creator_id, tier_filter, access_level, date_range
                ):
                    # Apply content protection and analysis
                    protected_content = await self._process_content(content, creator_info)
                    if protected_content:
                        yield protected_content
                        
        except Exception as e:
            self.logger.error(f"Error crawling creator content: {str(e)}")
            await self.metrics_collector.record_error('patreon_crawl_error', str(e))
            raise
            
    async def _crawl_creator_posts(
        self,
        session: aiohttp.ClientSession,
        creator_id: str,
        tier_filter: Optional[PatreonTier],
        access_level: Optional[ContentAccessLevel],
        date_range: Optional[tuple]
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """Crawl creator posts with advanced filtering"""
        
        cursor = None
        max_pages = 50  # Prevent infinite loops
        page_count = 0
        
        while page_count < max_pages:
            try:
                # Apply rate limiting
                await self._apply_rate_limiting()
                
                # Fetch posts page
                posts_data = await self._fetch_posts_page(
                    session, creator_id, cursor, date_range
                )
                
                if not posts_data or not posts_data.get('data'):
                    break
                    
                for post in posts_data['data']:
                    # Apply filters
                    if self._matches_filters(post, tier_filter, access_level):
                        yield post
                        
                # Get next cursor
                pagination = posts_data.get('meta', {}).get('pagination', {})
                cursor = pagination.get('cursors', {}).get('next')
                
                if not cursor:
                    break
                    
                page_count += 1
                
            except Exception as e:
                self.logger.error(f"Error fetching posts page {page_count}: {str(e)}")
                break
                
    async def _fetch_creator_info(
        self,
        session: aiohttp.ClientSession,
        creator_id: str
    ) -> Optional[Dict[str, Any]]:
        """Fetch creator information and tier structure"""
        
        url = f"https://www.patreon.com/api/oauth2/v2/campaigns/{creator_id}"
        
        params = {
            'include': 'tiers,creator,goals,benefits',
            'fields[campaign]': 'creation_name,patron_count,earnings_visibility,published_at',
            'fields[tier]': 'amount_cents,title,description,patron_count,published',
            'fields[user]': 'full_name,url,image_url,thumb_url'
        }
        
        headers = await self._get_authenticated_headers()
        
        try:
            async with session.get(url, params=params, headers=headers) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    self.logger.error(f"Failed to fetch creator info: HTTP {response.status}")
                    return None
                    
        except Exception as e:
            self.logger.error(f"Error fetching creator info: {str(e)}")
            return None
            
    async def _fetch_posts_page(
        self,
        session: aiohttp.ClientSession,
        creator_id: str,
        cursor: Optional[str],
        date_range: Optional[tuple]
    ) -> Dict[str, Any]:
        """Fetch a single page of posts"""
        
        url = f"https://www.patreon.com/api/oauth2/v2/campaigns/{creator_id}/posts"
        
        params = {
            'include': 'user,campaign,attachments,user_defined_tags,campaign.tiers',
            'fields[post]': 'content,embed,image,is_paid,like_count,comment_count,patreon_url,post_file,published_at,title,url',
            'fields[user]': 'full_name,image_url',
            'fields[campaign]': 'creation_name,patron_count',
            'page[count]': 25
        }
        
        if cursor:
            params['page[cursor]'] = cursor
            
        if date_range:
            start_date, end_date = date_range
            params['filter[created_at][min]'] = start_date.isoformat()
            params['filter[created_at][max]'] = end_date.isoformat()
            
        headers = await self._get_authenticated_headers()
        
        try:
            async with session.get(url, params=params, headers=headers) as response:
                if response.status == 200:
                    return await response.json()
                elif response.status == 429:
                    # Rate limit hit, wait and retry
                    await asyncio.sleep(120)
                    return await self._fetch_posts_page(session, creator_id, cursor, date_range)
                else:
                    self.logger.error(f"HTTP {response.status}: {await response.text()}")
                    return {}
                    
        except Exception as e:
            self.logger.error(f"Request error: {str(e)}")
            return {}
            
    def _matches_filters(
        self,
        post: Dict[str, Any],
        tier_filter: Optional[PatreonTier],
        access_level: Optional[ContentAccessLevel]
    ) -> bool:
        """Check if post matches the specified filters"""
        
        if tier_filter:
            post_tier = self._determine_post_tier(post)
            if post_tier != tier_filter:
                return False
                
        if access_level:
            post_access = self._determine_access_level(post)
            if post_access != access_level:
                return False
                
        return True
        
    def _determine_post_tier(self, post: Dict[str, Any]) -> PatreonTier:
        """Determine the tier requirement for a post"""
        
        attributes = post.get('attributes', {})
        
        if attributes.get('is_paid', False):
            # Try to determine tier from tier requirements
            # This would need to be enhanced based on actual API response structure
            return PatreonTier.BRONZE
        else:
            return PatreonTier.FREE
            
    def _determine_access_level(self, post: Dict[str, Any]) -> ContentAccessLevel:
        """Determine the access level for a post"""
        
        attributes = post.get('attributes', {})
        
        if attributes.get('is_paid', False):
            return ContentAccessLevel.PATRON_ONLY
        else:
            return ContentAccessLevel.PUBLIC
            
    async def _process_content(
        self, 
        raw_post: Dict[str, Any],
        creator_info: Dict[str, Any]
    ) -> Optional[PatreonContent]:
        """Process and protect content with advanced analysis"""
        
        try:
            attributes = raw_post.get('attributes', {})
            post_id = raw_post.get('id')
            
            if not post_id:
                return None
                
            # Extract creator ID from relationships or creator_info
            creator_data = creator_info.get('data', {})
            creator_id = creator_data.get('id', '')
            
            # Extract content information
            title = attributes.get('title', '')
            content = attributes.get('content', '')
            
            # Extract media URLs
            media_urls = self._extract_media_urls(raw_post)
            
            # Generate content fingerprint
            content_fingerprint = await self.content_guardian.generate_fingerprint(
                f"{title}{content}{''.join(media_urls)}"
            )
            
            # Analyze content quality
            quality_score = await self.content_analyzer.analyze_quality({
                'title': title,
                'content': content,
                'media_count': len(media_urls)
            })
            
            if quality_score < self.content_quality_threshold:
                return None
                
            # Determine tier and access level
            tier_requirement = self._determine_post_tier(raw_post)
            access_level = self._determine_access_level(raw_post)
            
            # Calculate revenue potential
            revenue_potential = await self._calculate_revenue_potential(
                raw_post, creator_info
            )
            
            # Determine protection level
            protection_level = "premium" if access_level != ContentAccessLevel.PUBLIC else "standard"
            
            # Determine monetization tier
            monetization_tier = await self._determine_monetization_tier(
                revenue_potential, tier_requirement
            )
            
            # Create Patreon content object
            patreon_content = PatreonContent(
                content_id=post_id,
                creator_id=creator_id,
                title=title,
                description=content[:500],  # Limit description length
                content_type=self._determine_content_type(raw_post),
                media_urls=media_urls,
                thumbnail_url=attributes.get('image', {}).get('url'),
                tier_requirement=tier_requirement,
                access_level=access_level,
                monthly_cost=self._calculate_monthly_cost(tier_requirement),
                patron_count=creator_data.get('attributes', {}).get('patron_count', 0),
                likes_count=attributes.get('like_count', 0),
                comments_count=attributes.get('comment_count', 0),
                published_at=datetime.fromisoformat(
                    attributes.get('published_at', '').replace('Z', '+00:00')
                ),
                engagement_rate=self._calculate_engagement_rate(raw_post, creator_info),
                revenue_potential=revenue_potential,
                content_fingerprint=content_fingerprint,
                protection_level=protection_level,
                monetization_tier=monetization_tier
            )
            
            # Record metrics
            await self.metrics_collector.record_content_processed(
                platform='patreon',
                content_type=patreon_content.content_type,
                quality_score=quality_score
            )
            
            return patreon_content
            
        except Exception as e:
            self.logger.error(f"Error processing content: {str(e)}")
            return None
            
    def _extract_media_urls(self, post: Dict[str, Any]) -> List[str]:
        """Extract media URLs from post"""
        
        urls = []
        attributes = post.get('attributes', {})
        
        # Extract main image
        image = attributes.get('image')
        if image and isinstance(image, dict) and image.get('url'):
            urls.append(image['url'])
            
        # Extract post file
        post_file = attributes.get('post_file')
        if post_file and isinstance(post_file, dict) and post_file.get('url'):
            urls.append(post_file['url'])
            
        # Extract embed media
        embed = attributes.get('embed')
        if embed and isinstance(embed, dict) and embed.get('url'):
            urls.append(embed['url'])
            
        return urls
        
    def _determine_content_type(self, post: Dict[str, Any]) -> str:
        """Determine content type from post data"""
        
        attributes = post.get('attributes', {})
        
        if attributes.get('post_file'):
            return "file"
        elif attributes.get('image'):
            return "image"
        elif attributes.get('embed'):
            return "video"
        else:
            return "text"
            
    def _calculate_monthly_cost(self, tier: PatreonTier) -> float:
        """Calculate monthly cost based on tier"""
        
        tier_costs = {
            PatreonTier.FREE: 0.0,
            PatreonTier.BRONZE: 5.0,
            PatreonTier.SILVER: 10.0,
            PatreonTier.GOLD: 25.0,
            PatreonTier.PLATINUM: 50.0,
            PatreonTier.DIAMOND: 100.0
        }
        
        return tier_costs.get(tier, 0.0)
        
    def _calculate_engagement_rate(
        self, 
        post: Dict[str, Any],
        creator_info: Dict[str, Any]
    ) -> float:
        """Calculate engagement rate for the post"""
        
        attributes = post.get('attributes', {})
        likes = attributes.get('like_count', 0)
        comments = attributes.get('comment_count', 0)
        
        creator_data = creator_info.get('data', {})
        patron_count = creator_data.get('attributes', {}).get('patron_count', 1)
        
        if patron_count == 0:
            return 0.0
            
        engagement_rate = (likes + comments * 2) / patron_count
        return min(engagement_rate, 1.0)  # Cap at 100%
        
    async def _calculate_revenue_potential(
        self,
        post: Dict[str, Any],
        creator_info: Dict[str, Any]
    ) -> float:
        """Calculate revenue potential for the post"""
        
        # Factors: engagement rate, tier requirement, patron count
        engagement_rate = self._calculate_engagement_rate(post, creator_info)
        tier_requirement = self._determine_post_tier(post)
        monthly_cost = self._calculate_monthly_cost(tier_requirement)
        
        creator_data = creator_info.get('data', {})
        patron_count = creator_data.get('attributes', {}).get('patron_count', 0)
        
        # Estimate revenue potential
        base_revenue = patron_count * monthly_cost
        engagement_multiplier = 1 + engagement_rate
        
        revenue_potential = base_revenue * engagement_multiplier
        
        # Normalize to 0-1 scale
        return min(revenue_potential / 10000, 1.0)
        
    async def _determine_monetization_tier(
        self,
        revenue_potential: float,
        tier_requirement: PatreonTier
    ) -> str:
        """Determine monetization tier"""
        
        if revenue_potential > 0.7 and tier_requirement in [PatreonTier.PLATINUM, PatreonTier.DIAMOND]:
            return "premium"
        elif revenue_potential > 0.4 and tier_requirement in [PatreonTier.SILVER, PatreonTier.GOLD]:
            return "standard"
        else:
            return "basic"
            
    async def crawl_trending_creators(
        self, 
        limit: int = 50,
        category: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Crawl trending creators on Patreon"""
        
        self.logger.info(f"Crawling trending creators, limit: {limit}")
        
        trending_creators = []
        
        try:
            async with self._create_session() as session:
                creators_data = await self._fetch_trending_creators(session, limit, category)
                
                for creator in creators_data.get('data', []):
                    creator_metrics = await self._analyze_creator_metrics(session, creator)
                    if creator_metrics:
                        trending_creators.append(creator_metrics)
                        
        except Exception as e:
            self.logger.error(f"Error crawling trending creators: {str(e)}")
            
        return trending_creators[:limit]
        
    async def _fetch_trending_creators(
        self,
        session: aiohttp.ClientSession,
        limit: int,
        category: Optional[str]
    ) -> Dict[str, Any]:
        """Fetch trending creators data"""
        
        url = "https://www.patreon.com/api/oauth2/v2/campaigns"
        
        params = {
            'include': 'creator,tiers,goals',
            'fields[campaign]': 'creation_name,patron_count,published_at,summary',
            'fields[user]': 'full_name,image_url,url',
            'sort': '-patron_count',
            'page[count]': min(limit, 50)
        }
        
        if category:
            params['filter[category]'] = category
            
        headers = await self._get_authenticated_headers()
        
        try:
            async with session.get(url, params=params, headers=headers) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    self.logger.error(f"Failed to fetch trending creators: HTTP {response.status}")
                    return {}
                    
        except Exception as e:
            self.logger.error(f"Error fetching trending creators: {str(e)}")
            return {}
            
    async def _analyze_creator_metrics(
        self,
        session: aiohttp.ClientSession,
        creator_data: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """Analyze creator metrics for trending analysis"""
        
        try:
            creator_id = creator_data.get('id')
            attributes = creator_data.get('attributes', {})
            
            # Basic metrics from creator data
            metrics = {
                'creator_id': creator_id,
                'name': attributes.get('creation_name', ''),
                'patron_count': attributes.get('patron_count', 0),
                'published_at': attributes.get('published_at', ''),
                'summary': attributes.get('summary', ''),
                'growth_rate': 0.0,  # Would need historical data
                'engagement_rate': 0.0,  # Would need post analysis
                'revenue_estimate': 0.0  # Would need tier analysis
            }
            
            # Enhanced analysis could be added here
            return metrics
            
        except Exception as e:
            self.logger.error(f"Error analyzing creator metrics: {str(e)}")
            return None
            
    async def monitor_subscription_metrics(
        self, 
        creator_id: str,
        monitoring_period: timedelta = timedelta(days=30)
    ) -> Dict[str, Any]:
        """Monitor subscription and revenue metrics"""
        
        self.logger.info(f"Monitoring subscription metrics: {creator_id}")
        
        try:
            async with self._create_session() as session:
                # Get current creator info
                creator_info = await self._fetch_creator_info(session, creator_id)
                if not creator_info:
                    return {}
                    
                # Get recent content performance
                end_date = datetime.now()
                start_date = end_date - monitoring_period
                
                content_metrics = []
                async for content in self.crawl_creator_content(
                    creator_id, date_range=(start_date, end_date)
                ):
                    content_metrics.append({
                        'engagement_rate': content.engagement_rate,
                        'revenue_potential': content.revenue_potential,
                        'tier_requirement': content.tier_requirement.value,
                        'access_level': content.access_level.value
                    })
                    
                # Calculate subscription metrics
                metrics = {
                    'total_content': len(content_metrics),
                    'avg_engagement_rate': sum(c['engagement_rate'] for c in content_metrics) / len(content_metrics) if content_metrics else 0,
                    'avg_revenue_potential': sum(c['revenue_potential'] for c in content_metrics) / len(content_metrics) if content_metrics else 0,
                    'tier_distribution': self._calculate_tier_distribution(content_metrics),
                    'access_level_distribution': self._calculate_access_distribution(content_metrics),
                    'monetization_effectiveness': self._calculate_monetization_effectiveness(content_metrics),
                    'subscription_conversion_potential': await self._estimate_conversion_potential(creator_info, content_metrics)
                }
                
                # Record monitoring metrics
                await self.metrics_collector.record_subscription_metrics(creator_id, metrics)
                
                return metrics
                
        except Exception as e:
            self.logger.error(f"Error monitoring subscription metrics: {str(e)}")
            return {}
            
    def _calculate_tier_distribution(self, content_metrics: List[Dict[str, Any]]) -> Dict[str, float]:
        """Calculate tier requirement distribution"""
        
        if not content_metrics:
            return {}
            
        total = len(content_metrics)
        distribution = {}
        
        for tier in PatreonTier:
            count = len([c for c in content_metrics if c['tier_requirement'] == tier.value])
            distribution[tier.value] = count / total
            
        return distribution
        
    def _calculate_access_distribution(self, content_metrics: List[Dict[str, Any]]) -> Dict[str, float]:
        """Calculate access level distribution"""
        
        if not content_metrics:
            return {}
            
        total = len(content_metrics)
        distribution = {}
        
        for access_level in ContentAccessLevel:
            count = len([c for c in content_metrics if c['access_level'] == access_level.value])
            distribution[access_level.value] = count / total
            
        return distribution
        
    def _calculate_monetization_effectiveness(self, content_metrics: List[Dict[str, Any]]) -> float:
        """Calculate overall monetization effectiveness"""
        
        if not content_metrics:
            return 0.0
            
        # Weighted average of revenue potential and engagement
        total_score = 0.0
        for content in content_metrics:
            engagement_score = content['engagement_rate']
            revenue_score = content['revenue_potential']
            combined_score = (engagement_score * 0.6 + revenue_score * 0.4)
            total_score += combined_score
            
        return total_score / len(content_metrics)
        
    async def _estimate_conversion_potential(
        self,
        creator_info: Dict[str, Any],
        content_metrics: List[Dict[str, Any]]
    ) -> float:
        """Estimate subscription conversion potential"""
        
        # Factors: content quality, engagement rates, tier distribution
        if not content_metrics:
            return 0.0
            
        avg_engagement = sum(c['engagement_rate'] for c in content_metrics) / len(content_metrics)
        avg_revenue = sum(c['revenue_potential'] for c in content_metrics) / len(content_metrics)
        
        # Premium content ratio
        premium_ratio = len([c for c in content_metrics if c['access_level'] != 'public']) / len(content_metrics)
        
        # Combine factors
        conversion_potential = (avg_engagement * 0.4 + avg_revenue * 0.4 + premium_ratio * 0.2)
        
        return min(conversion_potential, 1.0)
        
    async def _get_authenticated_headers(self) -> Dict[str, str]:
        """Get authenticated headers for API requests"""
        
        return {
            'User-Agent': 'Patreon/1.0',
            'Accept': 'application/vnd.api+json',
            'Authorization': f'Bearer {self.config.get("access_token", "")}',
            'Cookie': self.config.get('cookie', '')
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
        
        # Patreon has stricter rate limits
        await asyncio.sleep(60 / self.rate_limit_per_minute)
