"""Patreon Crawler Implementation
==============================

Advanced Patreon platform crawler for creator support and patronage monitoring.
Implements comprehensive Creator, Campaign, Post, and Patron tracking.

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
class PatreonCreator:
    """Patreon creator information"""    creator_id: str
    full_name: str
    first_name: str
    last_name: str
    vanity: str  # username/URL slug
    about: str
    image_url: str
    cover_photo_url: str
    creation_name: str
    creation_count: int
    display_patron_goals: bool
    earnings_visibility: str
    fan_funding_goal: int
    hide_pledges: bool
    image_small_url: str
    is_charged_immediately: bool
    is_monthly: bool
    is_nsfw: bool
    main_video_embed: str
    main_video_url: str
    one_liner: str
    patron_count: int
    pay_per_name: str
    pledge_sum: int
    pledge_url: str
    published_at: datetime
    summary: str
    thanks_embed: str
    thanks_msg: str
    thanks_video_url: str
    has_rss: bool
    has_sent_rss_notify: bool
    rss_feed_title: str
    rss_artwork_url: str
    created_at: datetime
    url: str
    discord_server_id: Optional[str]
    google_analytics_id: Optional[str]
    has_goals: bool
    has_poll: bool
    currency: str
    is_suspended: bool
    is_deleted: bool
    is_nuked: bool
    is_tax_required: bool
    default_country_code: str


@dataclass
class PatreonCampaign:
    """Patreon campaign information"""    campaign_id: str
    creator_id: str
    creation_name: str
    display_patron_goals: bool
    earnings_visibility: str
    image_small_url: str
    image_url: str
    is_charged_immediately: bool
    is_monthly: bool
    is_nsfw: bool
    is_plural: bool
    main_video_embed: str
    main_video_url: str
    one_liner: str
    patron_count: int
    pay_per_name: str
    pledge_sum: int
    pledge_url: str
    published_at: datetime
    summary: str
    thanks_embed: str
    thanks_msg: str
    thanks_video_url: str
    url: str
    vanity: str
    created_at: datetime
    discord_server_id: Optional[str]
    google_analytics_id: Optional[str]
    has_goals: bool
    has_poll: bool
    has_sent_rss_notify: bool
    has_rss: bool
    rss_artwork_url: str
    rss_feed_title: str
    show_earnings: bool
    currency: str
    is_suspended: bool
    default_country_code: str


@dataclass
class PatreonPost:
    """Patreon post information"""    post_id: str
    creator_id: str
    campaign_id: str
    title: str
    content: str
    embed_data: Dict[str, Any]
    embed_url: str
    is_paid: bool
    is_public: bool
    published_at: datetime
    url: str
    was_posted_by_campaign_owner: bool
    post_file: Dict[str, Any]
    thumbnail_url: str
    teaser_text: str
    upgrade_url: str
    min_cents_pledged_to_view: int
    patron_count: int
    like_count: int
    comment_count: int
    current_user_can_view: bool
    current_user_can_delete: bool
    current_user_has_liked: bool
    video_preview: Dict[str, Any]
    image: Dict[str, Any]
    audio_url: str
    poll_data: Dict[str, Any]
    is_automated_monthly_charge: bool
    charge_date: Optional[datetime]
    amount_cents: int
    post_tags: List[str]
    post_type: str  # text_only, image_file, video_file, audio_file, link
    app_id: int
    app_status: str
    scheduled_for: Optional[datetime]


@dataclass
class PatreonReward:
    """Patreon reward tier information"""    reward_id: str
    campaign_id: str
    amount: int
    amount_cents: int
    created_at: datetime
    description: str
    discord_role_ids: List[str]
    edited_at: datetime
    image_url: str
    patron_count: int
    post_count: int
    published: bool
    published_at: Optional[datetime]
    remaining: Optional[int]
    requires_shipping: bool
    title: str
    unpublished_at: Optional[datetime]
    url: str
    user_limit: Optional[int]
    welcome_message: str
    welcome_message_unsafe: str
    welcome_video_embed: str
    welcome_video_url: str
    is_twitch_reward: bool
    twitch_reward: Dict[str, Any]
    currency_symbol: str
    currency: str


@dataclass
class PatreonPledge:
    """Patreon pledge information"""    pledge_id: str
    amount_cents: int
    created_at: datetime
    declined_since: Optional[datetime]
    is_paused: bool
    has_shipping_address: bool
    is_twitch_pledge: bool
    max_charge_amount_cents: int
    patron_pays_fees: bool
    pledge_cap_cents: int
    total_historical_amount_cents: int
    patron_id: str
    campaign_id: str
    reward_id: Optional[str]
    address_id: Optional[str]
    card_id: Optional[str]
    payment_token: str
    full_name: str
    email: str
    patron_status: str
    currency: str


@dataclass
class PatreonGoal:
    """Patreon goal information"""    goal_id: str
    campaign_id: str
    amount_cents: int
    completed_percentage: int
    created_at: datetime
    description: str
    reached_at: Optional[datetime]
    title: str
    currency: str


class PatreonCrawler(PlatformCrawler):
    """    Advanced Patreon crawler for creator support and patronage monitoring.
    
    Features:
    - Creator profile tracking
    - Campaign monitoring
    - Post and content analysis
    - Reward tier tracking
    - Pledge and subscription monitoring
    - Goal progress tracking
    - Patron engagement metrics
    - Earnings and funding analysis
    - Discord integration tracking
    - RSS feed monitoring
    """    
    def __init__(self, config: CrawlerConfig, vector_matcher=None):
        super().__init__(config, vector_matcher)
        self.platform_name = "patreon"
        self.base_url = "https://www.patreon.com"
        self.api_base_url = "https://www.patreon.com/api/oauth2/v2"
        
        # Rate limiting (Patreon has reasonable limits)
        self.requests_per_minute = 15
        self.min_delay = 4.0
        self.max_delay = 8.0
        
        # Content type mappings
        self.content_types = {
            'creators': self._crawl_creators,
            'campaigns': self._crawl_campaigns,
            'posts': self._crawl_posts,
            'rewards': self._crawl_rewards,
            'pledges': self._crawl_pledges,
            'goals': self._crawl_goals,
            'trending': self._crawl_trending,
            'featured': self._crawl_featured,
            'search': self._crawl_search
        }
        
        # Tracking
        self.request_count = 0
        self.last_request_time = 0
        
        # Initialize session headers
        self._setup_session_headers()
    
    def _setup_session_headers(self):
        """Setup Patreon-specific headers"""        self.session_headers.update({
            'Accept': 'application/vnd.api+json',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'en-US,en;q=0.9',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Referer': 'https://www.patreon.com/',
            'Content-Type': 'application/vnd.api+json',
            'X-Requested-With': 'XMLHttpRequest'
        })
    
    async def search_content(self, query: str, content_type: str = "creators", 
                           max_results: int = 50, filters: Dict[str, Any] = None) -> List[CrawlerResult]:
        """        Search for content on Patreon.
        
        Args:
            query: Search query
            content_type: Type of content to search for
            max_results: Maximum number of results
            filters: Additional search filters
            
        Returns:
            List of crawler results
        """        try:
            await self._check_rate_limit()
            
            if content_type not in self.content_types:
                raise ValueError(f"Unsupported content type: {content_type}")
            
            # Execute search based on content type
            crawler_func = self.content_types[content_type]
            results = await crawler_func(query, max_results, filters)
            
            self.logger.info(f"Found {len(results)} Patreon {content_type} for query: {query}")
            return results
            
        except Exception as e:
            self.logger.error(f"Error searching Patreon content: {str(e)}")
            return []
    
    async def _crawl_creators(self, query: str, max_results: int, filters: Dict[str, Any] = None) -> List[CrawlerResult]:
        """Crawl Patreon creators"""        try:
            results = []
            
            # Mock creator data
            mock_creators = await self._get_mock_creators(query, max_results)
            
            for creator_data in mock_creators:
                creator = await self._parse_creator_data(creator_data)
                if creator:
                    result = CrawlerResult(
                        url=creator.url,
                        title=f"{creator.full_name} (@{creator.vanity})",
                        content=creator.about,
                        metadata={
                            'creator_data': asdict(creator),
                            'platform': 'patreon',
                            'content_type': 'creator',
                            'vanity': creator.vanity,
                            'full_name': creator.full_name,
                            'creation_name': creator.creation_name,
                            'creation_count': creator.creation_count,
                            'patron_count': creator.patron_count,
                            'pledge_sum': creator.pledge_sum,
                            'is_monthly': creator.is_monthly,
                            'is_nsfw': creator.is_nsfw,
                            'has_goals': creator.has_goals,
                            'has_poll': creator.has_poll,
                            'currency': creator.currency,
                            'earnings_visibility': creator.earnings_visibility,
                            'discord_server_id': creator.discord_server_id,
                            'has_rss': creator.has_rss,
                            'is_charged_immediately': creator.is_charged_immediately
                        },
                        timestamp=creator.published_at,
                        similarity_score=0.0
                    )
                    results.append(result)
                    
                    # Rate limiting
                    await asyncio.sleep(random.uniform(self.min_delay, self.max_delay))
            
            return results
            
        except Exception as e:
            self.logger.error(f"Error crawling Patreon creators: {str(e)}")
            return []
    
    async def _crawl_campaigns(self, query: str, max_results: int, filters: Dict[str, Any] = None) -> List[CrawlerResult]:
        """Crawl Patreon campaigns"""        try:
            results = []
            
            # Mock campaign data
            mock_campaigns = await self._get_mock_campaigns(query, max_results)
            
            for campaign_data in mock_campaigns:
                campaign = await self._parse_campaign_data(campaign_data)
                if campaign:
                    result = CrawlerResult(
                        url=campaign.url,
                        title=campaign.creation_name,
                        content=campaign.summary,
                        metadata={
                            'campaign_data': asdict(campaign),
                            'platform': 'patreon',
                            'content_type': 'campaign',
                            'creation_name': campaign.creation_name,
                            'vanity': campaign.vanity,
                            'patron_count': campaign.patron_count,
                            'pledge_sum': campaign.pledge_sum,
                            'is_monthly': campaign.is_monthly,
                            'is_nsfw': campaign.is_nsfw,
                            'pay_per_name': campaign.pay_per_name,
                            'has_goals': campaign.has_goals,
                            'has_poll': campaign.has_poll,
                            'currency': campaign.currency,
                            'earnings_visibility': campaign.earnings_visibility,
                            'discord_server_id': campaign.discord_server_id,
                            'has_rss': campaign.has_rss,
                            'show_earnings': campaign.show_earnings
                        },
                        timestamp=campaign.published_at,
                        similarity_score=0.0
                    )
                    results.append(result)
                    
                    # Rate limiting
                    await asyncio.sleep(random.uniform(self.min_delay, self.max_delay))
            
            return results
            
        except Exception as e:
            self.logger.error(f"Error crawling Patreon campaigns: {str(e)}")
            return []
    
    async def _crawl_posts(self, query: str, max_results: int, filters: Dict[str, Any] = None) -> List[CrawlerResult]:
        """Crawl Patreon posts"""        try:
            results = []
            
            # Mock post data
            mock_posts = await self._get_mock_posts(query, max_results)
            
            for post_data in mock_posts:
                post = await self._parse_post_data(post_data)
                if post:
                    result = CrawlerResult(
                        url=post.url,
                        title=post.title,
                        content=post.teaser_text if post.is_paid and not post.current_user_can_view else post.content,
                        metadata={
                            'post_data': asdict(post),
                            'platform': 'patreon',
                            'content_type': 'post',
                            'title': post.title,
                            'is_paid': post.is_paid,
                            'is_public': post.is_public,
                            'post_type': post.post_type,
                            'min_cents_pledged_to_view': post.min_cents_pledged_to_view,
                            'patron_count': post.patron_count,
                            'like_count': post.like_count,
                            'comment_count': post.comment_count,
                            'current_user_can_view': post.current_user_can_view,
                            'amount_cents': post.amount_cents,
                            'post_tags': post.post_tags,
                            'was_posted_by_campaign_owner': post.was_posted_by_campaign_owner,
                            'is_automated_monthly_charge': post.is_automated_monthly_charge
                        },
                        timestamp=post.published_at,
                        similarity_score=0.0
                    )
                    results.append(result)
                    
                    # Rate limiting
                    await asyncio.sleep(random.uniform(self.min_delay, self.max_delay))
            
            return results
            
        except Exception as e:
            self.logger.error(f"Error crawling Patreon posts: {str(e)}")
            return []
    
    async def _crawl_rewards(self, query: str, max_results: int, filters: Dict[str, Any] = None) -> List[CrawlerResult]:
        """Crawl Patreon rewards"""        try:
            results = []
            
            # Mock reward data
            mock_rewards = await self._get_mock_rewards(query, max_results)
            
            for reward_data in mock_rewards:
                reward = await self._parse_reward_data(reward_data)
                if reward:
                    result = CrawlerResult(
                        url=reward.url,
                        title=reward.title,
                        content=reward.description,
                        metadata={
                            'reward_data': asdict(reward),
                            'platform': 'patreon',
                            'content_type': 'reward',
                            'title': reward.title,
                            'amount': reward.amount,
                            'amount_cents': reward.amount_cents,
                            'patron_count': reward.patron_count,
                            'post_count': reward.post_count,
                            'published': reward.published,
                            'requires_shipping': reward.requires_shipping,
                            'user_limit': reward.user_limit,
                            'remaining': reward.remaining,
                            'currency': reward.currency,
                            'currency_symbol': reward.currency_symbol,
                            'discord_role_ids': reward.discord_role_ids,
                            'is_twitch_reward': reward.is_twitch_reward
                        },
                        timestamp=reward.created_at,
                        similarity_score=0.0
                    )
                    results.append(result)
                    
                    # Rate limiting
                    await asyncio.sleep(random.uniform(self.min_delay, self.max_delay))
            
            return results
            
        except Exception as e:
            self.logger.error(f"Error crawling Patreon rewards: {str(e)}")
            return []
    
    async def _crawl_pledges(self, query: str, max_results: int, filters: Dict[str, Any] = None) -> List[CrawlerResult]:
        """Crawl Patreon pledges (requires authentication)"""        try:
            results = []
            
            # Mock pledge data (limited for privacy)
            mock_pledges = await self._get_mock_pledges(query, max_results)
            
            for pledge_data in mock_pledges:
                pledge = await self._parse_pledge_data(pledge_data)
                if pledge:
                    result = CrawlerResult(
                        url=f"{self.base_url}/pledges/{pledge.pledge_id}",
                        title=f"Pledge: ${pledge.amount_cents/100:.2f}",
                        content=f"Pledge by {pledge.full_name}",
                        metadata={
                            'pledge_data': asdict(pledge),
                            'platform': 'patreon',
                            'content_type': 'pledge',
                            'amount_cents': pledge.amount_cents,
                            'is_paused': pledge.is_paused,
                            'patron_pays_fees': pledge.patron_pays_fees,
                            'patron_status': pledge.patron_status,
                            'currency': pledge.currency,
                            'has_shipping_address': pledge.has_shipping_address,
                            'is_twitch_pledge': pledge.is_twitch_pledge,
                            'total_historical_amount_cents': pledge.total_historical_amount_cents,
                            'full_name': pledge.full_name[:1] + "***"  # Privacy protection
                        },
                        timestamp=pledge.created_at,
                        similarity_score=0.0
                    )
                    results.append(result)
                    
                    # Rate limiting
                    await asyncio.sleep(random.uniform(self.min_delay, self.max_delay))
            
            return results
            
        except Exception as e:
            self.logger.error(f"Error crawling Patreon pledges: {str(e)}")
            return []
    
    async def _crawl_goals(self, query: str, max_results: int, filters: Dict[str, Any] = None) -> List[CrawlerResult]:
        """Crawl Patreon goals"""        try:
            results = []
            
            # Mock goal data
            mock_goals = await self._get_mock_goals(query, max_results)
            
            for goal_data in mock_goals:
                goal = await self._parse_goal_data(goal_data)
                if goal:
                    result = CrawlerResult(
                        url=f"{self.base_url}/goals/{goal.goal_id}",
                        title=goal.title,
                        content=goal.description,
                        metadata={
                            'goal_data': asdict(goal),
                            'platform': 'patreon',
                            'content_type': 'goal',
                            'title': goal.title,
                            'amount_cents': goal.amount_cents,
                            'completed_percentage': goal.completed_percentage,
                            'reached_at': goal.reached_at.isoformat() if goal.reached_at else None,
                            'currency': goal.currency
                        },
                        timestamp=goal.created_at,
                        similarity_score=0.0
                    )
                    results.append(result)
                    
                    # Rate limiting
                    await asyncio.sleep(random.uniform(self.min_delay, self.max_delay))
            
            return results
            
        except Exception as e:
            self.logger.error(f"Error crawling Patreon goals: {str(e)}")
            return []
    
    async def _crawl_trending(self, query: str, max_results: int, filters: Dict[str, Any] = None) -> List[CrawlerResult]:
        """Crawl trending Patreon content"""        try:
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
                        'platform': 'patreon',
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
            self.logger.error(f"Error crawling trending Patreon content: {str(e)}")
            return []
    
    async def _crawl_featured(self, query: str, max_results: int, filters: Dict[str, Any] = None) -> List[CrawlerResult]:
        """Crawl featured Patreon content"""        try:
            results = []
            
            # Get featured content
            featured_content = await self._get_featured_content(query, max_results, filters)
            
            for content in featured_content:
                result = CrawlerResult(
                    url=content.get('url', ''),
                    title=f"[FEATURED] {content.get('title', 'Unknown')}",
                    content=content.get('description', ''),
                    metadata={
                        'featured_data': content,
                        'platform': 'patreon',
                        'content_type': 'featured',
                        'is_featured': True,
                        'feature_score': content.get('feature_score', 0),
                        'featured_by': content.get('featured_by', 'patreon')
                    },
                    timestamp=datetime.utcnow(),
                    similarity_score=0.0
                )
                results.append(result)
            
            return results[:max_results]
            
        except Exception as e:
            self.logger.error(f"Error crawling featured Patreon content: {str(e)}")
            return []
    
    async def _crawl_search(self, query: str, max_results: int, filters: Dict[str, Any] = None) -> List[CrawlerResult]:
        """General Patreon search"""        try:
            results = []
            
            # Search across different content types
            creators = await self._crawl_creators(query, max_results // 3, filters)
            campaigns = await self._crawl_campaigns(query, max_results // 3, filters)
            posts = await self._crawl_posts(query, max_results // 3, filters)
            
            results.extend(creators)
            results.extend(campaigns)
            results.extend(posts)
            
            return results[:max_results]
            
        except Exception as e:
            self.logger.error(f"Error performing Patreon search: {str(e)}")
            return []
    
    # Mock data generators
    
    async def _get_mock_creators(self, query: str, max_results: int) -> List[Dict[str, Any]]:
        """Generate mock creator data"""        creators = []
        
        for i in range(min(max_results, 15)):
            published_at = datetime.utcnow() - timedelta(days=random.randint(30, 1095))
            created_at = published_at - timedelta(days=random.randint(1, 30))
            creators.append({
                'id': f'creator_{i}',
                'full_name': f'{query} Creator {i}' if query else f'Creator {i}',
                'first_name': f'{query}' if query else f'Creator',
                'last_name': f'{i}',
                'vanity': f'{query.lower() if query else "creator"}{i}',
                'about': f'Creating amazing {query} content' if query else f'Creator about {i}',
                'creation_name': f'{query} Creation' if query else f'Creation {i}',
                'creation_count': random.randint(10, 500),
                'patron_count': random.randint(50, 10000),
                'pledge_sum': random.randint(500, 50000),
                'is_monthly': random.choice([True, False]),
                'is_nsfw': random.choice([True, False]),
                'pay_per_name': random.choice(['month', 'creation']),
                'one_liner': f'{query} content creator' if query else f'One liner {i}',
                'summary': f'I create {query} content for my patrons' if query else f'Summary {i}',
                'published_at': published_at.isoformat(),
                'created_at': created_at.isoformat(),
                'url': f'{self.base_url}/{query.lower() if query else "creator"}{i}',
                'currency': random.choice(['USD', 'EUR', 'GBP']),
                'has_goals': random.choice([True, False]),
                'has_poll': random.choice([True, False]),
                'has_rss': random.choice([True, False]),
                'earnings_visibility': random.choice(['public', 'private']),
                'is_charged_immediately': random.choice([True, False]),
                'discord_server_id': f'discord_{i}' if random.choice([True, False]) else None,
                'is_suspended': False,
                'is_deleted': False
            })
        
        return creators
    
    async def _get_mock_campaigns(self, query: str, max_results: int) -> List[Dict[str, Any]]:
        """Generate mock campaign data"""        campaigns = []
        
        for i in range(min(max_results, 15)):
            published_at = datetime.utcnow() - timedelta(days=random.randint(30, 1095))
            created_at = published_at - timedelta(days=random.randint(1, 30))
            campaigns.append({
                'id': f'campaign_{i}',
                'creator_id': f'creator_{i}',
                'creation_name': f'{query} Campaign {i}' if query else f'Campaign {i}',
                'vanity': f'{query.lower() if query else "campaign"}{i}',
                'summary': f'Supporting {query} creation' if query else f'Campaign summary {i}',
                'patron_count': random.randint(50, 10000),
                'pledge_sum': random.randint(500, 50000),
                'is_monthly': random.choice([True, False]),
                'is_nsfw': random.choice([True, False]),
                'pay_per_name': random.choice(['month', 'creation']),
                'one_liner': f'{query} campaign' if query else f'Campaign one liner {i}',
                'published_at': published_at.isoformat(),
                'created_at': created_at.isoformat(),
                'url': f'{self.base_url}/{query.lower() if query else "campaign"}{i}',
                'currency': random.choice(['USD', 'EUR', 'GBP']),
                'has_goals': random.choice([True, False]),
                'has_poll': random.choice([True, False]),
                'has_rss': random.choice([True, False]),
                'show_earnings': random.choice([True, False]),
                'earnings_visibility': random.choice(['public', 'private']),
                'is_charged_immediately': random.choice([True, False]),
                'discord_server_id': f'discord_{i}' if random.choice([True, False]) else None,
                'is_suspended': False
            })
        
        return campaigns
    
    async def _get_mock_posts(self, query: str, max_results: int) -> List[Dict[str, Any]]:
        """Generate mock post data"""        posts = []
        
        for i in range(min(max_results, 25)):
            published_at = datetime.utcnow() - timedelta(hours=random.randint(1, 168))
            posts.append({
                'id': f'post_{i}',
                'creator_id': f'creator_{i % 5}',
                'campaign_id': f'campaign_{i % 5}',
                'title': f'{query} Post {i}' if query else f'Post {i}',
                'content': f'New {query} content for patrons!' if query else f'Post content {i}',
                'teaser_text': f'New {query} update...' if query else f'Teaser {i}',
                'is_paid': random.choice([True, False]),
                'is_public': random.choice([True, False]),
                'published_at': published_at.isoformat(),
                'url': f'{self.base_url}/posts/{i}',
                'post_type': random.choice(['text_only', 'image_file', 'video_file', 'audio_file', 'link']),
                'min_cents_pledged_to_view': random.randint(0, 2000),
                'patron_count': random.randint(0, 100),
                'like_count': random.randint(0, 50),
                'comment_count': random.randint(0, 20),
                'current_user_can_view': random.choice([True, False]),
                'current_user_can_delete': False,
                'amount_cents': random.randint(0, 1000),
                'post_tags': [query] if query else ['update', 'content'],
                'was_posted_by_campaign_owner': random.choice([True, False]),
                'is_automated_monthly_charge': random.choice([True, False])
            })
        
        return posts
    
    async def _get_mock_rewards(self, query: str, max_results: int) -> List[Dict[str, Any]]:
        """Generate mock reward data"""        rewards = []
        
        for i in range(min(max_results, 20)):
            created_at = datetime.utcnow() - timedelta(days=random.randint(1, 365))
            amount_cents = random.randint(100, 10000)
            rewards.append({
                'id': f'reward_{i}',
                'campaign_id': f'campaign_{i % 5}',
                'title': f'{query} Tier {i}' if query else f'Reward Tier {i}',
                'description': f'Access to {query} content' if query else f'Reward description {i}',
                'amount': amount_cents // 100,
                'amount_cents': amount_cents,
                'patron_count': random.randint(10, 1000),
                'post_count': random.randint(5, 100),
                'published': random.choice([True, False]),
                'published_at': created_at.isoformat(),
                'created_at': created_at.isoformat(),
                'url': f'{self.base_url}/rewards/{i}',
                'currency': random.choice(['USD', 'EUR', 'GBP']),
                'currency_symbol': random.choice(['$', '€', '£']),
                'requires_shipping': random.choice([True, False]),
                'user_limit': random.randint(10, 100) if random.choice([True, False]) else None,
                'remaining': random.randint(5, 50) if random.choice([True, False]) else None,
                'discord_role_ids': [f'role_{j}' for j in range(random.randint(0, 3))],
                'is_twitch_reward': random.choice([True, False]),
                'welcome_message': f'Welcome to {query} tier!' if query else f'Welcome message {i}'
            })
        
        return rewards
    
    async def _get_mock_pledges(self, query: str, max_results: int) -> List[Dict[str, Any]]:
        """Generate mock pledge data"""        pledges = []
        
        for i in range(min(max_results, 10)):  # Limited for privacy
            created_at = datetime.utcnow() - timedelta(days=random.randint(1, 365))
            amount_cents = random.randint(100, 5000)
            pledges.append({
                'id': f'pledge_{i}',
                'patron_id': f'patron_{i}',
                'campaign_id': f'campaign_{i % 5}',
                'reward_id': f'reward_{i % 3}' if random.choice([True, False]) else None,
                'amount_cents': amount_cents,
                'created_at': created_at.isoformat(),
                'is_paused': random.choice([True, False]),
                'patron_pays_fees': random.choice([True, False]),
                'patron_status': random.choice(['active_patron', 'declined_patron', 'former_patron']),
                'currency': random.choice(['USD', 'EUR', 'GBP']),
                'has_shipping_address': random.choice([True, False]),
                'is_twitch_pledge': random.choice([True, False]),
                'total_historical_amount_cents': amount_cents * random.randint(1, 24),
                'full_name': f'Patron {i}',
                'email': f'patron{i}@example.com'
            })
        
        return pledges
    
    async def _get_mock_goals(self, query: str, max_results: int) -> List[Dict[str, Any]]:
        """Generate mock goal data"""        goals = []
        
        for i in range(min(max_results, 10)):
            created_at = datetime.utcnow() - timedelta(days=random.randint(1, 365))
            amount_cents = random.randint(1000, 100000)
            completed_percentage = random.randint(0, 150)
            reached_at = created_at + timedelta(days=random.randint(30, 200)) if completed_percentage >= 100 else None
            goals.append({
                'id': f'goal_{i}',
                'campaign_id': f'campaign_{i % 5}',
                'title': f'{query} Goal {i}' if query else f'Goal {i}',
                'description': f'Reach ${amount_cents/100:.0f} to improve {query}' if query else f'Goal description {i}',
                'amount_cents': amount_cents,
                'completed_percentage': completed_percentage,
                'created_at': created_at.isoformat(),
                'reached_at': reached_at.isoformat() if reached_at else None,
                'currency': random.choice(['USD', 'EUR', 'GBP'])
            })
        
        return goals
    
    async def _get_trending_content(self, query: str, max_results: int, filters: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """Get trending content"""        content = []
        
        for i in range(min(max_results, 10)):
            content.append({
                'title': f'Trending: {query} {i}' if query else f'Trending Content {i}',
                'url': f'{self.base_url}/trending/{i}',
                'description': f'Trending content about {query}' if query else f'Trending description {i}',
                'trend_score': random.randint(80, 100),
                'category': random.choice(['creators', 'campaigns', 'posts'])
            })
        
        return content
    
    async def _get_featured_content(self, query: str, max_results: int, filters: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """Get featured content"""        content = []
        
        for i in range(min(max_results, 10)):
            content.append({
                'title': f'Featured: {query} {i}' if query else f'Featured Content {i}',
                'url': f'{self.base_url}/featured/{i}',
                'description': f'Featured content about {query}' if query else f'Featured description {i}',
                'feature_score': random.randint(90, 100),
                'featured_by': random.choice(['patreon', 'staff', 'algorithm'])
            })
        
        return content
    
    # Parser methods
    
    async def _parse_creator_data(self, creator_data: Dict[str, Any]) -> Optional[PatreonCreator]:
        """Parse creator data"""        try:
            published_at = datetime.fromisoformat(creator_data.get('published_at', datetime.utcnow().isoformat()).replace('Z', '+00:00'))
            created_at = datetime.fromisoformat(creator_data.get('created_at', datetime.utcnow().isoformat()).replace('Z', '+00:00'))
            
            creator = PatreonCreator(
                creator_id=creator_data.get('id', ''),
                full_name=creator_data.get('full_name', ''),
                first_name=creator_data.get('first_name', ''),
                last_name=creator_data.get('last_name', ''),
                vanity=creator_data.get('vanity', ''),
                about=creator_data.get('about', ''),
                image_url='',
                cover_photo_url='',
                creation_name=creator_data.get('creation_name', ''),
                creation_count=creator_data.get('creation_count', 0),
                display_patron_goals=creator_data.get('display_patron_goals', True),
                earnings_visibility=creator_data.get('earnings_visibility', 'public'),
                fan_funding_goal=creator_data.get('fan_funding_goal', 0),
                hide_pledges=creator_data.get('hide_pledges', False),
                image_small_url='',
                is_charged_immediately=creator_data.get('is_charged_immediately', False),
                is_monthly=creator_data.get('is_monthly', True),
                is_nsfw=creator_data.get('is_nsfw', False),
                main_video_embed=creator_data.get('main_video_embed', ''),
                main_video_url=creator_data.get('main_video_url', ''),
                one_liner=creator_data.get('one_liner', ''),
                patron_count=creator_data.get('patron_count', 0),
                pay_per_name=creator_data.get('pay_per_name', 'month'),
                pledge_sum=creator_data.get('pledge_sum', 0),
                pledge_url='',
                published_at=published_at,
                summary=creator_data.get('summary', ''),
                thanks_embed=creator_data.get('thanks_embed', ''),
                thanks_msg=creator_data.get('thanks_msg', ''),
                thanks_video_url=creator_data.get('thanks_video_url', ''),
                has_rss=creator_data.get('has_rss', False),
                has_sent_rss_notify=creator_data.get('has_sent_rss_notify', False),
                rss_feed_title=creator_data.get('rss_feed_title', ''),
                rss_artwork_url=creator_data.get('rss_artwork_url', ''),
                created_at=created_at,
                url=creator_data.get('url', ''),
                discord_server_id=creator_data.get('discord_server_id'),
                google_analytics_id=creator_data.get('google_analytics_id'),
                has_goals=creator_data.get('has_goals', False),
                has_poll=creator_data.get('has_poll', False),
                currency=creator_data.get('currency', 'USD'),
                is_suspended=creator_data.get('is_suspended', False),
                is_deleted=creator_data.get('is_deleted', False),
                is_nuked=creator_data.get('is_nuked', False),
                is_tax_required=creator_data.get('is_tax_required', False),
                default_country_code=creator_data.get('default_country_code', 'US')
            )
            
            return creator
            
        except Exception as e:
            self.logger.error(f"Error parsing creator data: {str(e)}")
            return None
    
    async def _parse_campaign_data(self, campaign_data: Dict[str, Any]) -> Optional[PatreonCampaign]:
        """Parse campaign data"""        try:
            published_at = datetime.fromisoformat(campaign_data.get('published_at', datetime.utcnow().isoformat()).replace('Z', '+00:00'))
            created_at = datetime.fromisoformat(campaign_data.get('created_at', datetime.utcnow().isoformat()).replace('Z', '+00:00'))
            
            campaign = PatreonCampaign(
                campaign_id=campaign_data.get('id', ''),
                creator_id=campaign_data.get('creator_id', ''),
                creation_name=campaign_data.get('creation_name', ''),
                display_patron_goals=campaign_data.get('display_patron_goals', True),
                earnings_visibility=campaign_data.get('earnings_visibility', 'public'),
                image_small_url='',
                image_url='',
                is_charged_immediately=campaign_data.get('is_charged_immediately', False),
                is_monthly=campaign_data.get('is_monthly', True),
                is_nsfw=campaign_data.get('is_nsfw', False),
                is_plural=campaign_data.get('is_plural', False),
                main_video_embed=campaign_data.get('main_video_embed', ''),
                main_video_url=campaign_data.get('main_video_url', ''),
                one_liner=campaign_data.get('one_liner', ''),
                patron_count=campaign_data.get('patron_count', 0),
                pay_per_name=campaign_data.get('pay_per_name', 'month'),
                pledge_sum=campaign_data.get('pledge_sum', 0),
                pledge_url='',
                published_at=published_at,
                summary=campaign_data.get('summary', ''),
                thanks_embed=campaign_data.get('thanks_embed', ''),
                thanks_msg=campaign_data.get('thanks_msg', ''),
                thanks_video_url=campaign_data.get('thanks_video_url', ''),
                url=campaign_data.get('url', ''),
                vanity=campaign_data.get('vanity', ''),
                created_at=created_at,
                discord_server_id=campaign_data.get('discord_server_id'),
                google_analytics_id=campaign_data.get('google_analytics_id'),
                has_goals=campaign_data.get('has_goals', False),
                has_poll=campaign_data.get('has_poll', False),
                has_sent_rss_notify=campaign_data.get('has_sent_rss_notify', False),
                has_rss=campaign_data.get('has_rss', False),
                rss_artwork_url=campaign_data.get('rss_artwork_url', ''),
                rss_feed_title=campaign_data.get('rss_feed_title', ''),
                show_earnings=campaign_data.get('show_earnings', True),
                currency=campaign_data.get('currency', 'USD'),
                is_suspended=campaign_data.get('is_suspended', False),
                default_country_code=campaign_data.get('default_country_code', 'US')
            )
            
            return campaign
            
        except Exception as e:
            self.logger.error(f"Error parsing campaign data: {str(e)}")
            return None
    
    async def _parse_post_data(self, post_data: Dict[str, Any]) -> Optional[PatreonPost]:
        """Parse post data"""        try:
            published_at = datetime.fromisoformat(post_data.get('published_at', datetime.utcnow().isoformat()).replace('Z', '+00:00'))
            charge_date = None
            if post_data.get('charge_date'):
                charge_date = datetime.fromisoformat(post_data['charge_date'].replace('Z', '+00:00'))
            scheduled_for = None
            if post_data.get('scheduled_for'):
                scheduled_for = datetime.fromisoformat(post_data['scheduled_for'].replace('Z', '+00:00'))
            
            post = PatreonPost(
                post_id=post_data.get('id', ''),
                creator_id=post_data.get('creator_id', ''),
                campaign_id=post_data.get('campaign_id', ''),
                title=post_data.get('title', ''),
                content=post_data.get('content', ''),
                embed_data=post_data.get('embed_data', {}),
                embed_url=post_data.get('embed_url', ''),
                is_paid=post_data.get('is_paid', False),
                is_public=post_data.get('is_public', True),
                published_at=published_at,
                url=post_data.get('url', ''),
                was_posted_by_campaign_owner=post_data.get('was_posted_by_campaign_owner', True),
                post_file=post_data.get('post_file', {}),
                thumbnail_url='',
                teaser_text=post_data.get('teaser_text', ''),
                upgrade_url='',
                min_cents_pledged_to_view=post_data.get('min_cents_pledged_to_view', 0),
                patron_count=post_data.get('patron_count', 0),
                like_count=post_data.get('like_count', 0),
                comment_count=post_data.get('comment_count', 0),
                current_user_can_view=post_data.get('current_user_can_view', False),
                current_user_can_delete=post_data.get('current_user_can_delete', False),
                current_user_has_liked=post_data.get('current_user_has_liked', False),
                video_preview=post_data.get('video_preview', {}),
                image=post_data.get('image', {}),
                audio_url=post_data.get('audio_url', ''),
                poll_data=post_data.get('poll_data', {}),
                is_automated_monthly_charge=post_data.get('is_automated_monthly_charge', False),
                charge_date=charge_date,
                amount_cents=post_data.get('amount_cents', 0),
                post_tags=post_data.get('post_tags', []),
                post_type=post_data.get('post_type', 'text_only'),
                app_id=post_data.get('app_id', 0),
                app_status=post_data.get('app_status', ''),
                scheduled_for=scheduled_for
            )
            
            return post
            
        except Exception as e:
            self.logger.error(f"Error parsing post data: {str(e)}")
            return None
    
    async def _parse_reward_data(self, reward_data: Dict[str, Any]) -> Optional[PatreonReward]:
        """Parse reward data"""        try:
            created_at = datetime.fromisoformat(reward_data.get('created_at', datetime.utcnow().isoformat()).replace('Z', '+00:00'))
            published_at = None
            if reward_data.get('published_at'):
                published_at = datetime.fromisoformat(reward_data['published_at'].replace('Z', '+00:00'))
            
            reward = PatreonReward(
                reward_id=reward_data.get('id', ''),
                campaign_id=reward_data.get('campaign_id', ''),
                amount=reward_data.get('amount', 0),
                amount_cents=reward_data.get('amount_cents', 0),
                created_at=created_at,
                description=reward_data.get('description', ''),
                discord_role_ids=reward_data.get('discord_role_ids', []),
                edited_at=created_at,
                image_url='',
                patron_count=reward_data.get('patron_count', 0),
                post_count=reward_data.get('post_count', 0),
                published=reward_data.get('published', True),
                published_at=published_at,
                remaining=reward_data.get('remaining'),
                requires_shipping=reward_data.get('requires_shipping', False),
                title=reward_data.get('title', ''),
                unpublished_at=None,
                url=reward_data.get('url', ''),
                user_limit=reward_data.get('user_limit'),
                welcome_message=reward_data.get('welcome_message', ''),
                welcome_message_unsafe=reward_data.get('welcome_message_unsafe', ''),
                welcome_video_embed=reward_data.get('welcome_video_embed', ''),
                welcome_video_url=reward_data.get('welcome_video_url', ''),
                is_twitch_reward=reward_data.get('is_twitch_reward', False),
                twitch_reward=reward_data.get('twitch_reward', {}),
                currency_symbol=reward_data.get('currency_symbol', '$'),
                currency=reward_data.get('currency', 'USD')
            )
            
            return reward
            
        except Exception as e:
            self.logger.error(f"Error parsing reward data: {str(e)}")
            return None
    
    async def _parse_pledge_data(self, pledge_data: Dict[str, Any]) -> Optional[PatreonPledge]:
        """Parse pledge data"""        try:
            created_at = datetime.fromisoformat(pledge_data.get('created_at', datetime.utcnow().isoformat()).replace('Z', '+00:00'))
            
            pledge = PatreonPledge(
                pledge_id=pledge_data.get('id', ''),
                amount_cents=pledge_data.get('amount_cents', 0),
                created_at=created_at,
                declined_since=None,
                is_paused=pledge_data.get('is_paused', False),
                has_shipping_address=pledge_data.get('has_shipping_address', False),
                is_twitch_pledge=pledge_data.get('is_twitch_pledge', False),
                max_charge_amount_cents=pledge_data.get('max_charge_amount_cents', 0),
                patron_pays_fees=pledge_data.get('patron_pays_fees', False),
                pledge_cap_cents=pledge_data.get('pledge_cap_cents', 0),
                total_historical_amount_cents=pledge_data.get('total_historical_amount_cents', 0),
                patron_id=pledge_data.get('patron_id', ''),
                campaign_id=pledge_data.get('campaign_id', ''),
                reward_id=pledge_data.get('reward_id'),
                address_id=pledge_data.get('address_id'),
                card_id=pledge_data.get('card_id'),
                payment_token=pledge_data.get('payment_token', ''),
                full_name=pledge_data.get('full_name', ''),
                email=pledge_data.get('email', ''),
                patron_status=pledge_data.get('patron_status', 'active_patron'),
                currency=pledge_data.get('currency', 'USD')
            )
            
            return pledge
            
        except Exception as e:
            self.logger.error(f"Error parsing pledge data: {str(e)}")
            return None
    
    async def _parse_goal_data(self, goal_data: Dict[str, Any]) -> Optional[PatreonGoal]:
        """Parse goal data"""        try:
            created_at = datetime.fromisoformat(goal_data.get('created_at', datetime.utcnow().isoformat()).replace('Z', '+00:00'))
            reached_at = None
            if goal_data.get('reached_at'):
                reached_at = datetime.fromisoformat(goal_data['reached_at'].replace('Z', '+00:00'))
            
            goal = PatreonGoal(
                goal_id=goal_data.get('id', ''),
                campaign_id=goal_data.get('campaign_id', ''),
                amount_cents=goal_data.get('amount_cents', 0),
                completed_percentage=goal_data.get('completed_percentage', 0),
                created_at=created_at,
                description=goal_data.get('description', ''),
                reached_at=reached_at,
                title=goal_data.get('title', ''),
                currency=goal_data.get('currency', 'USD')
            )
            
            return goal
            
        except Exception as e:
            self.logger.error(f"Error parsing goal data: {str(e)}")
            return None
    
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
        """Extract metadata from Patreon content"""        try:
            # Parse Patreon URL
            parsed_url = urlparse(url)
            
            metadata = {
                'platform': 'patreon',
                'url': url,
                'extracted_at': datetime.utcnow().isoformat()
            }
            
            # Handle Patreon URLs
            if 'patreon.com' in parsed_url.netloc:
                path_parts = parsed_url.path.strip('/').split('/')
                
                if len(path_parts) >= 1:
                    if path_parts[0] == 'posts':
                        # Post URL: /posts/post_id
                        if len(path_parts) >= 2:
                            metadata.update({
                                'content_type': 'post',
                                'post_id': path_parts[1]
                            })
                    
                    elif path_parts[0] == 'user':
                        # User/Creator URL: /user?u=user_id
                        query_params = parse_qs(parsed_url.query)
                        if 'u' in query_params:
                            metadata.update({
                                'content_type': 'creator',
                                'creator_id': query_params['u'][0]
                            })
                    
                    else:
                        # Creator vanity URL: /creator_name
                        metadata.update({
                            'content_type': 'creator',
                            'vanity': path_parts[0]
                        })
                        
                        # Post URL: /creator_name/posts/post_id
                        if len(path_parts) >= 3 and path_parts[1] == 'posts':
                            metadata.update({
                                'content_type': 'post',
                                'post_id': path_parts[2]
                            })
            
            return metadata
            
        except Exception as e:
            self.logger.error(f"Error extracting Patreon metadata: {str(e)}")
            return {'error': str(e)}
    
    def get_platform_info(self) -> Dict[str, Any]:
        """Get Patreon platform information"""        return {
            'platform_name': 'Patreon',
            'base_url': self.base_url,
            'api_base_url': self.api_base_url,
            'supported_content_types': list(self.content_types.keys()),
            'rate_limits': {
                'requests_per_minute': self.requests_per_minute,
                'min_delay': self.min_delay,
                'max_delay': self.max_delay
            },
            'features': [
                'Creator profile tracking',
                'Campaign monitoring',
                'Post and content analysis',
                'Reward tier tracking',
                'Pledge and subscription monitoring',
                'Goal progress tracking',
                'Patron engagement metrics',
                'Earnings and funding analysis',
                'Discord integration tracking',
                'RSS feed monitoring'
            ],
            'authentication': {
                'required': True,
                'type': 'OAuth 2.0',
                'scope': 'Creator and patron content access'
            },
            'content_characteristics': {
                'creator_economy': True,
                'subscription_based': True,
                'community_driven': True,
                'goal_oriented': True
            },
            'limitations': [
                'Requires authentication for most features',
                'Rate limiting enforced',
                'Private content access requires permissions',
                'Payment information is restricted',
                'Patron data requires special permissions'
            ]
        }
