"""
Pinterest Crawler Implementation
===============================

Advanced Pinterest content monitoring and discovery crawler.
Implements comprehensive board, pin, and user analysis with image recognition.

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
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import random
from urllib.parse import urljoin, urlparse, parse_qs
import re
import hashlib
from PIL import Image
import io
import base64

from .platform_crawler import PlatformCrawler, CrawlerConfig, CrawlerResult


@dataclass
class PinterestPin:
    """Pinterest pin information"""
    pin_id: str
    title: str
    description: str
    url: str
    image_url: str
    original_url: Optional[str]
    board_id: str
    board_name: str
    user_id: str
    username: str
    user_display_name: str
    user_profile_url: str
    created_at: datetime
    dominant_color: Optional[str]
    has_product: bool
    is_promoted: bool
    is_native: bool
    is_video: bool
    video_url: Optional[str]
    pin_join_id: str
    aggregated_pin_data: Optional[Dict[str, Any]]
    repin_count: int
    reaction_count: int
    comment_count: int
    rich_summary: Optional[Dict[str, Any]]
    product_rich_summary: Optional[Dict[str, Any]]
    story_pin_data: Optional[Dict[str, Any]]
    carousel_data: Optional[List[Dict[str, Any]]]
    section_id: Optional[str]
    link_domain: Optional[str]
    tracked_link: Optional[str]
    image_signature: Optional[str]
    image_width: int
    image_height: int
    alt_text: Optional[str]
    accessibility_label: Optional[str]
    visual_search_attrs: Optional[Dict[str, Any]]
    shopping_flags: List[str]
    image_crop: Optional[Dict[str, Any]]
    pin_metrics: Optional[Dict[str, Any]]


@dataclass
class PinterestBoard:
    """Pinterest board information"""
    board_id: str
    name: str
    description: str
    url: str
    cover_pin: Optional[PinterestPin]
    owner_id: str
    owner_username: str
    owner_display_name: str
    created_at: datetime
    updated_at: datetime
    pin_count: int
    follower_count: int
    is_collaborative: bool
    is_ads_only: bool
    privacy: str  # public, secret, private
    category: Optional[str]
    board_order_modified_at: Optional[datetime]
    followed_by_me: bool
    image_cover_url: Optional[str]
    image_thumbnail_url: Optional[str]
    layout: str  # default, places
    map_id: Optional[str]
    is_explore_board: bool
    should_show_followers: bool
    should_hide_attribution: bool
    collaborator_count: int
    collaborators: List[Dict[str, Any]]
    sections: List[Dict[str, Any]]
    board_topics: List[str]
    board_rules: Optional[Dict[str, Any]]


@dataclass
class PinterestUser:
    """Pinterest user information"""
    user_id: str
    username: str
    first_name: str
    last_name: str
    display_name: str
    about: Optional[str]
    location: Optional[str]
    website_url: Optional[str]
    profile_image: Optional[str]
    profile_image_small: Optional[str]
    image_xlarge_url: Optional[str]
    impressum_url: Optional[str]
    created_at: datetime
    pin_count: int
    board_count: int
    following_count: int
    follower_count: int
    is_verified_merchant: bool
    is_ads_only_profile: bool
    has_ads_only_profile: bool
    is_partner: bool
    is_tastemaker: bool
    is_employee: bool
    is_brand: bool
    is_indexed: bool
    is_verified: bool
    verified_identity: Optional[Dict[str, Any]]
    business_name: Optional[str]
    business_url: Optional[str]
    country: Optional[str]
    locale: str
    age_verification_required: bool
    show_impressum: bool
    is_any_website_verified: bool
    website_verification_disabled: bool
    domain_verified: bool
    profile_discovered_public: bool
    show_creator_profile: bool
    creator_class: Optional[str]
    ads_only_profile_site: Optional[str]
    featured_boards: List[str]
    board_order: List[str]
    engagement_domain_verified: bool
    social_connections: Dict[str, Any]
    monthly_views: Optional[int]
    partner_applications: List[Dict[str, Any]]


class PinterestCrawler(PlatformCrawler):
    """
    Advanced Pinterest crawler for visual content monitoring and discovery.
    
    Features:
    - Pin discovery and image analysis
    - Board and user monitoring
    - Visual similarity search
    - Shopping and product analysis
    - Trend detection and analytics
    - Image fingerprinting
    - Copyright violation detection
    - Engagement metrics tracking
    """
    
    def __init__(self, config: CrawlerConfig, vector_matcher=None, access_token: str = None):
        super().__init__(config, vector_matcher)
        self.platform_name = "pinterest"
        self.base_url = "https://pinterest.com"
        self.api_base_url = "https://api.pinterest.com/v5"
        
        # Pinterest API credentials
        self.access_token = access_token
        
        # Rate limiting (Pinterest is moderate)
        self.requests_per_minute = 200
        self.min_delay = 0.3
        self.max_delay = 1.0
        
        # Content type mappings
        self.content_types = {
            'pins': self._crawl_pins,
            'boards': self._crawl_boards,
            'users': self._crawl_users,
            'search': self._crawl_search,
            'trending': self._crawl_trending,
            'visual_search': self._crawl_visual_search,
            'shopping': self._crawl_shopping,
            'ideas': self._crawl_ideas
        }
        
        # Tracking
        self.request_count = 0
        self.last_request_time = 0
        
        # Initialize session headers
        self._setup_session_headers()
    
    def _setup_session_headers(self):
        """Setup Pinterest-specific headers"""
        self.session_headers.update({
            'Accept': 'application/json',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'en-US,en;q=0.9',
            'Origin': 'https://pinterest.com',
            'Referer': 'https://pinterest.com/',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin',
            'X-Requested-With': 'XMLHttpRequest',
            'X-Pinterest-Source-URL': '/',
            'X-APP-VERSION': 'web',
            'X-Pinterest-AppState': 'active'
        })
        
        if self.access_token:
            self.session_headers['Authorization'] = f'Bearer {self.access_token}'
    
    async def search_content(self, query: str, content_type: str = "pins", 
                           max_results: int = 50) -> List[CrawlerResult]:
        """
        Search for content on Pinterest.
        
        Args:
            query: Search query
            content_type: Type of content to search for
            max_results: Maximum number of results
            
        Returns:
            List of crawler results
        """
        try:
            await self._check_rate_limit()
            
            if content_type not in self.content_types:
                raise ValueError(f"Unsupported content type: {content_type}")
            
            # Execute search based on content type
            crawler_func = self.content_types[content_type]
            results = await crawler_func(query, max_results)
            
            self.logger.info(f"Found {len(results)} Pinterest {content_type} for query: {query}")
            return results
            
        except Exception as e:
            self.logger.error(f"Error searching Pinterest content: {str(e)}")
            return []
    
    async def _crawl_pins(self, query: str, max_results: int) -> List[CrawlerResult]:
        """Crawl Pinterest pins"""
        try:
            results = []
            
            # Search for pins using Pinterest API
            params = {
                'query': query,
                'ad_account_id': None,
                'page_size': min(max_results, 250),  # API limit
                'bookmark': None
            }
            
            api_url = f"{self.api_base_url}/search/pins"
            
            async with self.session.get(
                api_url,
                params=params,
                headers=self.session_headers
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    for pin_data in data.get('items', []):
                        # Parse pin data
                        pin = await self._parse_pin_data(pin_data)
                        if pin:
                            # Get image analysis if available
                            image_analysis = await self._analyze_pin_image(pin.image_url)
                            
                            result = CrawlerResult(
                                url=pin.url,
                                title=pin.title,
                                content=f"Pin: {pin.title} - {pin.description}",
                                metadata={
                                    'pin_data': asdict(pin),
                                    'platform': 'pinterest',
                                    'content_type': 'pin',
                                    'board_name': pin.board_name,
                                    'username': pin.username,
                                    'repin_count': pin.repin_count,
                                    'reaction_count': pin.reaction_count,
                                    'is_video': pin.is_video,
                                    'has_product': pin.has_product,
                                    'image_analysis': image_analysis
                                },
                                timestamp=pin.created_at,
                                similarity_score=0.0
                            )
                            results.append(result)
                    
                    # Rate limiting
                    await asyncio.sleep(random.uniform(self.min_delay, self.max_delay))
                
                else:
                    self.logger.error(f"Error fetching pins: {response.status}")
            
            return results
            
        except Exception as e:
            self.logger.error(f"Error crawling Pinterest pins: {str(e)}")
            return []
    
    async def _crawl_boards(self, query: str, max_results: int) -> List[CrawlerResult]:
        """Crawl Pinterest boards"""
        try:
            results = []
            
            # Search for boards using Pinterest API
            params = {
                'query': query,
                'ad_account_id': None,
                'page_size': min(max_results, 250),
                'bookmark': None
            }
            
            api_url = f"{self.api_base_url}/search/boards"
            
            async with self.session.get(
                api_url,
                params=params,
                headers=self.session_headers
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    for board_data in data.get('items', []):
                        # Parse board data
                        board = await self._parse_board_data(board_data)
                        if board:
                            result = CrawlerResult(
                                url=board.url,
                                title=board.name,
                                content=f"Board: {board.name} - {board.description}",
                                metadata={
                                    'board_data': asdict(board),
                                    'platform': 'pinterest',
                                    'content_type': 'board',
                                    'owner_username': board.owner_username,
                                    'pin_count': board.pin_count,
                                    'follower_count': board.follower_count,
                                    'is_collaborative': board.is_collaborative,
                                    'privacy': board.privacy,
                                    'category': board.category
                                },
                                timestamp=board.created_at,
                                similarity_score=0.0
                            )
                            results.append(result)
                    
                    # Rate limiting
                    await asyncio.sleep(random.uniform(self.min_delay, self.max_delay))
                
                else:
                    self.logger.error(f"Error fetching boards: {response.status}")
            
            return results
            
        except Exception as e:
            self.logger.error(f"Error crawling Pinterest boards: {str(e)}")
            return []
    
    async def _crawl_users(self, query: str, max_results: int) -> List[CrawlerResult]:
        """Crawl Pinterest users"""
        try:
            results = []
            
            # Search for users using Pinterest API
            params = {
                'query': query,
                'ad_account_id': None,
                'page_size': min(max_results, 250),
                'bookmark': None
            }
            
            api_url = f"{self.api_base_url}/search/user_accounts"
            
            async with self.session.get(
                api_url,
                params=params,
                headers=self.session_headers
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    for user_data in data.get('items', []):
                        # Parse user data
                        user = await self._parse_user_data(user_data)
                        if user:
                            result = CrawlerResult(
                                url=f"https://pinterest.com/{user.username}",
                                title=f"Pinterest User: {user.display_name}",
                                content=f"User: {user.display_name} (@{user.username}) - {user.about}",
                                metadata={
                                    'user_data': asdict(user),
                                    'platform': 'pinterest',
                                    'content_type': 'user',
                                    'pin_count': user.pin_count,
                                    'board_count': user.board_count,
                                    'follower_count': user.follower_count,
                                    'following_count': user.following_count,
                                    'is_verified': user.is_verified,
                                    'is_business': user.is_brand,
                                    'monthly_views': user.monthly_views
                                },
                                timestamp=user.created_at,
                                similarity_score=0.0
                            )
                            results.append(result)
                    
                    # Rate limiting
                    await asyncio.sleep(random.uniform(self.min_delay, self.max_delay))
                
                else:
                    self.logger.error(f"Error fetching users: {response.status}")
            
            return results
            
        except Exception as e:
            self.logger.error(f"Error crawling Pinterest users: {str(e)}")
            return []
    
    async def _crawl_search(self, query: str, max_results: int) -> List[CrawlerResult]:
        """General Pinterest search across all content types"""
        try:
            results = []
            
            # Search across different content types
            pins = await self._crawl_pins(query, max_results // 2)
            boards = await self._crawl_boards(query, max_results // 4)
            users = await self._crawl_users(query, max_results // 4)
            
            results.extend(pins)
            results.extend(boards)
            results.extend(users)
            
            return results[:max_results]
            
        except Exception as e:
            self.logger.error(f"Error performing Pinterest search: {str(e)}")
            return []
    
    async def _crawl_trending(self, query: str, max_results: int) -> List[CrawlerResult]:
        """Crawl trending content on Pinterest"""
        try:
            results = []
            
            # Get trending pins (Popular section)
            api_url = f"{self.api_base_url}/pins"
            params = {
                'pin_filter': 'popular',
                'page_size': min(max_results, 250)
            }
            
            async with self.session.get(
                api_url,
                params=params,
                headers=self.session_headers
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    for pin_data in data.get('items', []):
                        # Filter by query if provided
                        if query and query.lower() not in pin_data.get('title', '').lower() and query.lower() not in pin_data.get('description', '').lower():
                            continue
                        
                        pin = await self._parse_pin_data(pin_data)
                        if pin:
                            result = CrawlerResult(
                                url=pin.url,
                                title=f"[TRENDING] {pin.title}",
                                content=f"Trending pin: {pin.title} - {pin.description}",
                                metadata={
                                    'pin_data': asdict(pin),
                                    'platform': 'pinterest',
                                    'content_type': 'trending_pin',
                                    'trend_source': 'popular'
                                },
                                timestamp=pin.created_at,
                                similarity_score=0.0
                            )
                            results.append(result)
                
                else:
                    self.logger.error(f"Error fetching trending content: {response.status}")
            
            return results
            
        except Exception as e:
            self.logger.error(f"Error crawling Pinterest trending: {str(e)}")
            return []
    
    async def _crawl_visual_search(self, query: str, max_results: int) -> List[CrawlerResult]:
        """Crawl using visual search capabilities"""
        try:
            results = []
            
            # Pinterest visual search requires an image
            # For now, search for visually similar content based on query
            params = {
                'query': f"visual {query}",
                'visual_search_type': 'mixed',
                'page_size': min(max_results, 250)
            }
            
            api_url = f"{self.api_base_url}/search/pins"
            
            async with self.session.get(
                api_url,
                params=params,
                headers=self.session_headers
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    for pin_data in data.get('items', []):
                        pin = await self._parse_pin_data(pin_data)
                        if pin:
                            result = CrawlerResult(
                                url=pin.url,
                                title=f"[VISUAL] {pin.title}",
                                content=f"Visual search result: {pin.title} - {pin.description}",
                                metadata={
                                    'pin_data': asdict(pin),
                                    'platform': 'pinterest',
                                    'content_type': 'visual_search',
                                    'search_type': 'visual'
                                },
                                timestamp=pin.created_at,
                                similarity_score=0.0
                            )
                            results.append(result)
            
            return results
            
        except Exception as e:
            self.logger.error(f"Error crawling Pinterest visual search: {str(e)}")
            return []
    
    async def _crawl_shopping(self, query: str, max_results: int) -> List[CrawlerResult]:
        """Crawl shopping and product pins"""
        try:
            results = []
            
            # Search for shopping pins
            params = {
                'query': query,
                'rich_search_types': ['product'],
                'page_size': min(max_results, 250)
            }
            
            api_url = f"{self.api_base_url}/search/pins"
            
            async with self.session.get(
                api_url,
                params=params,
                headers=self.session_headers
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    for pin_data in data.get('items', []):
                        # Only process pins with product data
                        if not pin_data.get('has_product', False):
                            continue
                        
                        pin = await self._parse_pin_data(pin_data)
                        if pin:
                            result = CrawlerResult(
                                url=pin.url,
                                title=f"[SHOPPING] {pin.title}",
                                content=f"Product pin: {pin.title} - {pin.description}",
                                metadata={
                                    'pin_data': asdict(pin),
                                    'platform': 'pinterest',
                                    'content_type': 'shopping_pin',
                                    'has_product': pin.has_product,
                                    'shopping_flags': pin.shopping_flags,
                                    'product_data': pin.product_rich_summary
                                },
                                timestamp=pin.created_at,
                                similarity_score=0.0
                            )
                            results.append(result)
            
            return results
            
        except Exception as e:
            self.logger.error(f"Error crawling Pinterest shopping: {str(e)}")
            return []
    
    async def _crawl_ideas(self, query: str, max_results: int) -> List[CrawlerResult]:
        """Crawl Pinterest Ideas (story pins)"""
        try:
            results = []
            
            # Search for idea pins (story pins)
            params = {
                'query': query,
                'pin_type': 'story',
                'page_size': min(max_results, 250)
            }
            
            api_url = f"{self.api_base_url}/search/pins"
            
            async with self.session.get(
                api_url,
                params=params,
                headers=self.session_headers
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    for pin_data in data.get('items', []):
                        # Only process story pins
                        if not pin_data.get('story_pin_data'):
                            continue
                        
                        pin = await self._parse_pin_data(pin_data)
                        if pin:
                            result = CrawlerResult(
                                url=pin.url,
                                title=f"[IDEA] {pin.title}",
                                content=f"Idea pin: {pin.title} - {pin.description}",
                                metadata={
                                    'pin_data': asdict(pin),
                                    'platform': 'pinterest',
                                    'content_type': 'idea_pin',
                                    'story_data': pin.story_pin_data,
                                    'carousel_data': pin.carousel_data
                                },
                                timestamp=pin.created_at,
                                similarity_score=0.0
                            )
                            results.append(result)
            
            return results
            
        except Exception as e:
            self.logger.error(f"Error crawling Pinterest ideas: {str(e)}")
            return []
    
    # Helper methods
    
    async def _parse_pin_data(self, pin_data: Dict[str, Any]) -> Optional[PinterestPin]:
        """Parse pin data from API response"""
        try:
            created_time = pin_data.get('created_at')
            created_at = datetime.fromisoformat(created_time.replace('Z', '+00:00')) if created_time else datetime.utcnow()
            
            # Parse board information
            board_data = pin_data.get('board', {})
            
            # Parse user information
            owner_data = board_data.get('owner', {}) or pin_data.get('pinner', {})
            
            # Extract image information
            media = pin_data.get('media', {})
            images = media.get('images', {})
            image_url = None
            image_width = 0
            image_height = 0
            
            if 'orig' in images:
                image_url = images['orig']['url']
                image_width = images['orig'].get('width', 0)
                image_height = images['orig'].get('height', 0)
            elif images:
                # Get largest available image
                largest_image = max(images.values(), key=lambda x: x.get('width', 0) * x.get('height', 0))
                image_url = largest_image['url']
                image_width = largest_image.get('width', 0)
                image_height = largest_image.get('height', 0)
            
            pin = PinterestPin(
                pin_id=pin_data.get('id', ''),
                title=pin_data.get('title', ''),
                description=pin_data.get('description', ''),
                url=pin_data.get('url', ''),
                image_url=image_url or '',
                original_url=pin_data.get('link', ''),
                board_id=board_data.get('id', ''),
                board_name=board_data.get('name', ''),
                user_id=owner_data.get('id', ''),
                username=owner_data.get('username', ''),
                user_display_name=owner_data.get('first_name', '') + ' ' + owner_data.get('last_name', ''),
                user_profile_url=f"https://pinterest.com/{owner_data.get('username', '')}",
                created_at=created_at,
                dominant_color=pin_data.get('dominant_color'),
                has_product=pin_data.get('has_product', False),
                is_promoted=pin_data.get('is_promoted', False),
                is_native=pin_data.get('is_native', False),
                is_video=media.get('media_type') == 'video',
                video_url=media.get('video_url'),
                pin_join_id=pin_data.get('pin_join_id', ''),
                aggregated_pin_data=pin_data.get('aggregated_pin_data'),
                repin_count=pin_data.get('repin_count', 0),
                reaction_count=pin_data.get('reaction_count', 0),
                comment_count=pin_data.get('comment_count', 0),
                rich_summary=pin_data.get('rich_summary'),
                product_rich_summary=pin_data.get('product_rich_summary'),
                story_pin_data=pin_data.get('story_pin_data'),
                carousel_data=pin_data.get('carousel_data'),
                section_id=pin_data.get('section_id'),
                link_domain=pin_data.get('link_domain'),
                tracked_link=pin_data.get('tracked_link'),
                image_signature=pin_data.get('image_signature'),
                image_width=image_width,
                image_height=image_height,
                alt_text=pin_data.get('alt_text'),
                accessibility_label=pin_data.get('accessibility_label'),
                visual_search_attrs=pin_data.get('visual_search_attrs'),
                shopping_flags=pin_data.get('shopping_flags', []),
                image_crop=pin_data.get('image_crop'),
                pin_metrics=pin_data.get('pin_metrics')
            )
            
            return pin
            
        except Exception as e:
            self.logger.error(f"Error parsing pin data: {str(e)}")
            return None
    
    async def _parse_board_data(self, board_data: Dict[str, Any]) -> Optional[PinterestBoard]:
        """Parse board data from API response"""
        try:
            created_time = board_data.get('created_at')
            created_at = datetime.fromisoformat(created_time.replace('Z', '+00:00')) if created_time else datetime.utcnow()
            
            updated_time = board_data.get('updated_at')
            updated_at = datetime.fromisoformat(updated_time.replace('Z', '+00:00')) if updated_time else created_at
            
            # Parse owner information
            owner_data = board_data.get('owner', {})
            
            # Parse cover pin
            cover_pin_data = board_data.get('cover_pin')
            cover_pin = None
            if cover_pin_data:
                cover_pin = await self._parse_pin_data(cover_pin_data)
            
            board = PinterestBoard(
                board_id=board_data.get('id', ''),
                name=board_data.get('name', ''),
                description=board_data.get('description', ''),
                url=board_data.get('url', ''),
                cover_pin=cover_pin,
                owner_id=owner_data.get('id', ''),
                owner_username=owner_data.get('username', ''),
                owner_display_name=owner_data.get('first_name', '') + ' ' + owner_data.get('last_name', ''),
                created_at=created_at,
                updated_at=updated_at,
                pin_count=board_data.get('pin_count', 0),
                follower_count=board_data.get('follower_count', 0),
                is_collaborative=board_data.get('is_collaborative', False),
                is_ads_only=board_data.get('is_ads_only', False),
                privacy=board_data.get('privacy', 'public'),
                category=board_data.get('category'),
                board_order_modified_at=None,  # Would need additional parsing
                followed_by_me=board_data.get('followed_by_me', False),
                image_cover_url=board_data.get('image_cover_url'),
                image_thumbnail_url=board_data.get('image_thumbnail_url'),
                layout=board_data.get('layout', 'default'),
                map_id=board_data.get('map_id'),
                is_explore_board=board_data.get('is_explore_board', False),
                should_show_followers=board_data.get('should_show_followers', True),
                should_hide_attribution=board_data.get('should_hide_attribution', False),
                collaborator_count=board_data.get('collaborator_count', 0),
                collaborators=board_data.get('collaborators', []),
                sections=board_data.get('sections', []),
                board_topics=board_data.get('board_topics', []),
                board_rules=board_data.get('board_rules')
            )
            
            return board
            
        except Exception as e:
            self.logger.error(f"Error parsing board data: {str(e)}")
            return None
    
    async def _parse_user_data(self, user_data: Dict[str, Any]) -> Optional[PinterestUser]:
        """Parse user data from API response"""
        try:
            created_time = user_data.get('created_at')
            created_at = datetime.fromisoformat(created_time.replace('Z', '+00:00')) if created_time else datetime.utcnow()
            
            user = PinterestUser(
                user_id=user_data.get('id', ''),
                username=user_data.get('username', ''),
                first_name=user_data.get('first_name', ''),
                last_name=user_data.get('last_name', ''),
                display_name=user_data.get('first_name', '') + ' ' + user_data.get('last_name', ''),
                about=user_data.get('about'),
                location=user_data.get('location'),
                website_url=user_data.get('website_url'),
                profile_image=user_data.get('profile_image'),
                profile_image_small=user_data.get('profile_image_small'),
                image_xlarge_url=user_data.get('image_xlarge_url'),
                impressum_url=user_data.get('impressum_url'),
                created_at=created_at,
                pin_count=user_data.get('pin_count', 0),
                board_count=user_data.get('board_count', 0),
                following_count=user_data.get('following_count', 0),
                follower_count=user_data.get('follower_count', 0),
                is_verified_merchant=user_data.get('is_verified_merchant', False),
                is_ads_only_profile=user_data.get('is_ads_only_profile', False),
                has_ads_only_profile=user_data.get('has_ads_only_profile', False),
                is_partner=user_data.get('is_partner', False),
                is_tastemaker=user_data.get('is_tastemaker', False),
                is_employee=user_data.get('is_employee', False),
                is_brand=user_data.get('is_brand', False),
                is_indexed=user_data.get('is_indexed', True),
                is_verified=user_data.get('is_verified', False),
                verified_identity=user_data.get('verified_identity'),
                business_name=user_data.get('business_name'),
                business_url=user_data.get('business_url'),
                country=user_data.get('country'),
                locale=user_data.get('locale', 'en-US'),
                age_verification_required=user_data.get('age_verification_required', False),
                show_impressum=user_data.get('show_impressum', False),
                is_any_website_verified=user_data.get('is_any_website_verified', False),
                website_verification_disabled=user_data.get('website_verification_disabled', False),
                domain_verified=user_data.get('domain_verified', False),
                profile_discovered_public=user_data.get('profile_discovered_public', True),
                show_creator_profile=user_data.get('show_creator_profile', False),
                creator_class=user_data.get('creator_class'),
                ads_only_profile_site=user_data.get('ads_only_profile_site'),
                featured_boards=user_data.get('featured_boards', []),
                board_order=user_data.get('board_order', []),
                engagement_domain_verified=user_data.get('engagement_domain_verified', False),
                social_connections=user_data.get('social_connections', {}),
                monthly_views=user_data.get('monthly_views'),
                partner_applications=user_data.get('partner_applications', [])
            )
            
            return user
            
        except Exception as e:
            self.logger.error(f"Error parsing user data: {str(e)}")
            return None
    
    async def _analyze_pin_image(self, image_url: str) -> Optional[Dict[str, Any]]:
        """Analyze pin image for visual features"""
        try:
            if not image_url:
                return None
            
            # Download image
            async with self.session.get(image_url) as response:
                if response.status == 200:
                    image_data = await response.read()
                    
                    # Basic image analysis
                    image = Image.open(io.BytesIO(image_data))
                    
                    analysis = {
                        'width': image.width,
                        'height': image.height,
                        'aspect_ratio': image.width / image.height,
                        'format': image.format,
                        'mode': image.mode,
                        'size_bytes': len(image_data),
                        'dominant_colors': self._extract_dominant_colors(image),
                        'image_hash': hashlib.md5(image_data).hexdigest()
                    }
                    
                    return analysis
                
        except Exception as e:
            self.logger.error(f"Error analyzing pin image: {str(e)}")
            return None
    
    def _extract_dominant_colors(self, image: Image.Image, num_colors: int = 5) -> List[str]:
        """Extract dominant colors from image"""
        try:
            # Convert to RGB if needed
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            # Resize for faster processing
            image = image.resize((150, 150))
            
            # Get colors
            colors = image.getcolors(maxcolors=256*256*256)
            if colors:
                # Sort by frequency
                colors.sort(key=lambda x: x[0], reverse=True)
                
                # Convert to hex
                dominant_colors = []
                for count, color in colors[:num_colors]:
                    hex_color = '#{:02x}{:02x}{:02x}'.format(color[0], color[1], color[2])
                    dominant_colors.append(hex_color)
                
                return dominant_colors
            
        except Exception as e:
            self.logger.error(f"Error extracting colors: {str(e)}")
        
        return []
    
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
        """Extract metadata from Pinterest content"""
        try:
            # Parse Pinterest URL
            parsed_url = urlparse(url)
            path_parts = parsed_url.path.strip('/').split('/')
            
            metadata = {
                'platform': 'pinterest',
                'url': url,
                'extracted_at': datetime.utcnow().isoformat()
            }
            
            if 'pin' in path_parts:
                idx = path_parts.index('pin')
                if len(path_parts) > idx + 1:
                    pin_id = path_parts[idx + 1]
                    metadata.update({
                        'pin_id': pin_id,
                        'content_type': 'pin'
                    })
            
            elif len(path_parts) >= 2 and not path_parts[0].startswith('_'):
                username = path_parts[0]
                if len(path_parts) == 1:
                    # User profile
                    metadata.update({
                        'username': username,
                        'content_type': 'user'
                    })
                else:
                    # Board
                    board_name = path_parts[1]
                    metadata.update({
                        'username': username,
                        'board_name': board_name,
                        'content_type': 'board'
                    })
            
            return metadata
            
        except Exception as e:
            self.logger.error(f"Error extracting Pinterest metadata: {str(e)}")
            return {'error': str(e)}
    
    def get_platform_info(self) -> Dict[str, Any]:
        """Get Pinterest platform information"""
        return {
            'platform_name': 'Pinterest',
            'base_url': self.base_url,
            'api_base_url': self.api_base_url,
            'supported_content_types': list(self.content_types.keys()),
            'rate_limits': {
                'requests_per_minute': self.requests_per_minute,
                'min_delay': self.min_delay,
                'max_delay': self.max_delay
            },
            'features': [
                'Pin discovery and image analysis',
                'Board and user monitoring',
                'Visual similarity search',
                'Shopping and product analysis',
                'Trend detection and analytics',
                'Image fingerprinting',
                'Copyright violation detection',
                'Engagement metrics tracking'
            ],
            'authentication': {
                'required': True,
                'type': 'OAuth2 Access Token',
                'scope': 'Read access to pins, boards, and users'
            },
            'limitations': [
                'Rate limited by Pinterest API',
                'Visual search requires image input',
                'Some features require business account',
                'Private boards not accessible'
            ]
        }
