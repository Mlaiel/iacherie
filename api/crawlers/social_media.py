"""
Professional social media crawling system for content discovery and protection.

This module implements specialized crawlers for major social media platforms
including Instagram, TikTok, YouTube, Twitter/X, and others with advanced
anti-detection capabilities and content analysis.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 IA-Influencer Project. All rights reserved.
Licensed under proprietary license - reproduction forbidden without written authorization.

Project Team Specialties:
- Lead AI Developer & Senior Backend Engineer: Fahed Mlaiel
- Social Media API Specialist: Platform Integration Expert
- Content Discovery Engineer: Advanced Pattern Recognition
- Anti-Detection Specialist: Bot Evasion & Stealth Crawling
- Data Mining Engineer: Large-Scale Content Analysis
- Computer Vision Engineer: Image & Video Content Analysis

Contact: mlaiel@live.de

LEGAL WARNING: This software and all associated intellectual property
belong exclusively to Fahed Mlaiel. Any unauthorized copying, redistribution,
reverse engineering, or commercial use without explicit written permission
will result in immediate legal action under international copyright laws.
"""

from typing import Dict, Any, List, Optional, Union, Set, Tuple, AsyncIterator
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import asyncio
import logging
import json
import re
import time
import random
from urllib.parse import urljoin, urlparse, parse_qs
import hashlib
import uuid
import base64

# HTTP and web scraping
import aiohttp
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException

# API clients
import tweepy
from instagrapi import Client as InstagramClient
from pytube import YouTube
import yt_dlp

# Content analysis
import cv2
import numpy as np
from PIL import Image
import imagehash

from . import WebCrawler, CrawlResult, CrawlTarget, ContentType, PlatformType
from ..core.exceptions import CrawlerException, ValidationException
from ..core.models import BaseModel
from ..security.encryption import EncryptionManager
from ..utils.rate_limiter import RateLimiter


class SocialMediaPlatform(Enum):
    """Social media platform identifiers."""
    INSTAGRAM = "instagram"
    TIKTOK = "tiktok"
    YOUTUBE = "youtube"
    TWITTER = "twitter"
    FACEBOOK = "facebook"
    LINKEDIN = "linkedin"
    PINTEREST = "pinterest"
    SNAPCHAT = "snapchat"
    TWITCH = "twitch"
    DISCORD = "discord"
    REDDIT = "reddit"
    TELEGRAM = "telegram"


class ContentDiscoveryMode(Enum):
    """Content discovery modes."""
    HASHTAG_SEARCH = "hashtag_search"
    USER_PROFILE = "user_profile"
    TRENDING_CONTENT = "trending_content"
    SIMILAR_ACCOUNTS = "similar_accounts"
    COMPETITOR_ANALYSIS = "competitor_analysis"
    BRAND_MENTIONS = "brand_mentions"
    COPYRIGHT_MONITORING = "copyright_monitoring"


@dataclass
class SocialMediaPost:
    """Social media post data structure."""
    post_id: str
    platform: SocialMediaPlatform
    author_username: str
    author_id: str
    content_text: str = ""
    media_urls: List[str] = field(default_factory=list)
    hashtags: List[str] = field(default_factory=list)
    mentions: List[str] = field(default_factory=list)
    like_count: int = 0
    comment_count: int = 0
    share_count: int = 0
    view_count: int = 0
    posted_at: Optional[datetime] = None
    discovered_at: datetime = field(default_factory=datetime.utcnow)
    engagement_rate: float = 0.0
    similarity_score: float = 0.0
    potential_infringement: bool = False
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class SocialMediaProfile:
    """Social media profile data structure."""
    user_id: str
    username: str
    platform: SocialMediaPlatform
    display_name: str = ""
    bio: str = ""
    follower_count: int = 0
    following_count: int = 0
    post_count: int = 0
    profile_image_url: str = ""
    verified: bool = False
    category: str = ""
    contact_info: Dict[str, str] = field(default_factory=dict)
    external_links: List[str] = field(default_factory=list)
    discovered_at: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = field(default_factory=dict)


class SocialMediaCrawler(WebCrawler):
    """
    Advanced social media crawler with platform-specific implementations.
    
    Provides comprehensive crawling across major social media platforms
    with intelligent content discovery, anti-detection measures, and
    copyright infringement detection capabilities.
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__(config)
        self.logger = logging.getLogger("crawler.social_media")
        
        # Platform-specific configurations
        self.platform_configs = self.config.get("platforms", {})
        
        # API credentials (encrypted)
        self.api_credentials = self.config.get("api_credentials", {})
        self.encryption_manager = EncryptionManager()
        
        # Rate limiting per platform
        self.rate_limiters = {}
        self._initialize_rate_limiters()
        
        # Content analysis settings
        self.content_similarity_threshold = self.config.get("similarity_threshold", 0.8)
        self.image_hash_threshold = self.config.get("image_hash_threshold", 10)
        
        # Browser automation for social media
        self.browser_pool = []
        self.max_browsers = self.config.get("max_browsers", 5)
        
        # Initialize platform clients
        self._initialize_platform_clients()
        
        self.logger.info("SocialMediaCrawler initialized successfully")
    
    def _initialize_rate_limiters(self):
        """Initialize rate limiters for each platform."""
        rate_limits = {
            SocialMediaPlatform.INSTAGRAM: {"requests_per_hour": 200, "requests_per_minute": 10},
            SocialMediaPlatform.TIKTOK: {"requests_per_hour": 300, "requests_per_minute": 15},
            SocialMediaPlatform.YOUTUBE: {"requests_per_hour": 10000, "requests_per_minute": 100},
            SocialMediaPlatform.TWITTER: {"requests_per_hour": 500, "requests_per_minute": 25},
            SocialMediaPlatform.FACEBOOK: {"requests_per_hour": 600, "requests_per_minute": 20},
            SocialMediaPlatform.LINKEDIN: {"requests_per_hour": 100, "requests_per_minute": 5},
            SocialMediaPlatform.PINTEREST: {"requests_per_hour": 1000, "requests_per_minute": 30},
            SocialMediaPlatform.REDDIT: {"requests_per_hour": 2000, "requests_per_minute": 60}
        }
        
        for platform, limits in rate_limits.items():
            self.rate_limiters[platform] = RateLimiter(
                requests_per_hour=limits["requests_per_hour"],
                requests_per_minute=limits["requests_per_minute"]
            )
    
    def _initialize_platform_clients(self):
        """Initialize API clients for social media platforms."""
        try:
            # Instagram client
            if "instagram" in self.api_credentials:
                self.instagram_client = InstagramClient()
                # Login handled separately for security
            
            # Twitter client
            if "twitter" in self.api_credentials:
                twitter_creds = self.api_credentials["twitter"]
                self.twitter_client = tweepy.Client(
                    bearer_token=self._decrypt_credential(twitter_creds.get("bearer_token")),
                    consumer_key=self._decrypt_credential(twitter_creds.get("consumer_key")),
                    consumer_secret=self._decrypt_credential(twitter_creds.get("consumer_secret")),
                    access_token=self._decrypt_credential(twitter_creds.get("access_token")),
                    access_token_secret=self._decrypt_credential(twitter_creds.get("access_token_secret"))
                )
            
            # YouTube Data API client setup
            if "youtube" in self.api_credentials:
                self.youtube_api_key = self._decrypt_credential(
                    self.api_credentials["youtube"].get("api_key")
                )
            
            self.logger.info("Platform API clients initialized")
            
        except Exception as e:
            self.logger.warning(f"Some platform clients failed to initialize: {e}")
    
    def _decrypt_credential(self, encrypted_credential: str) -> str:
        """Decrypt API credentials securely."""
        if not encrypted_credential:
            return ""
        
        try:
            return self.encryption_manager.decrypt(encrypted_credential)
        except Exception as e:
            self.logger.error(f"Failed to decrypt credential: {e}")
            return ""
    
    async def discover_content_by_hashtag(
        self,
        hashtag: str,
        platforms: List[SocialMediaPlatform],
        max_posts: int = 100
    ) -> List[SocialMediaPost]:
        """
        Discover content across platforms using hashtag search.
        
        Performs intelligent hashtag-based content discovery with
        similarity analysis for potential copyright infringement detection.
        """
        try:
            self.logger.info(f"Starting hashtag discovery: #{hashtag} across {len(platforms)} platforms")
            
            discovered_posts = []
            discovery_tasks = []
            
            # Create discovery tasks for each platform
            for platform in platforms:
                task = self._discover_hashtag_content_platform(
                    hashtag, platform, max_posts // len(platforms)
                )
                discovery_tasks.append(task)
            
            # Execute discovery tasks concurrently
            platform_results = await asyncio.gather(*discovery_tasks, return_exceptions=True)
            
            # Aggregate results
            for result in platform_results:
                if isinstance(result, list):
                    discovered_posts.extend(result)
                elif isinstance(result, Exception):
                    self.logger.error(f"Platform discovery error: {result}")
            
            # Analyze content for similarities and potential infringement
            analyzed_posts = await self._analyze_content_similarities(discovered_posts)
            
            self.logger.info(f"Hashtag discovery completed: {len(analyzed_posts)} posts found")
            
            return analyzed_posts
            
        except Exception as e:
            self.logger.error(f"Hashtag discovery failed: {e}")
            raise CrawlerException(f"Hashtag discovery error: {e}")
    
    async def _discover_hashtag_content_platform(
        self,
        hashtag: str,
        platform: SocialMediaPlatform,
        max_posts: int
    ) -> List[SocialMediaPost]:
        """Discover hashtag content from specific platform."""
        await self.rate_limiters[platform].acquire()
        
        try:
            if platform == SocialMediaPlatform.INSTAGRAM:
                return await self._discover_instagram_hashtag(hashtag, max_posts)
            elif platform == SocialMediaPlatform.TIKTOK:
                return await self._discover_tiktok_hashtag(hashtag, max_posts)
            elif platform == SocialMediaPlatform.YOUTUBE:
                return await self._discover_youtube_hashtag(hashtag, max_posts)
            elif platform == SocialMediaPlatform.TWITTER:
                return await self._discover_twitter_hashtag(hashtag, max_posts)
            elif platform == SocialMediaPlatform.REDDIT:
                return await self._discover_reddit_hashtag(hashtag, max_posts)
            else:
                return await self._discover_generic_platform(hashtag, platform, max_posts)
        
        except Exception as e:
            self.logger.error(f"Platform {platform.value} hashtag discovery failed: {e}")
            return []
    
    async def _discover_instagram_hashtag(
        self, hashtag: str, max_posts: int
    ) -> List[SocialMediaPost]:
        """Discover Instagram posts by hashtag using both API and web scraping."""
        posts = []
        
        try:
            # Method 1: API-based discovery (if authenticated)
            if hasattr(self, 'instagram_client') and self.instagram_client.user_id:
                api_posts = await self._instagram_api_hashtag_search(hashtag, max_posts // 2)
                posts.extend(api_posts)
            
            # Method 2: Web scraping for additional coverage
            scraping_posts = await self._instagram_web_scraping_hashtag(
                hashtag, max_posts - len(posts)
            )
            posts.extend(scraping_posts)
            
        except Exception as e:
            self.logger.error(f"Instagram hashtag discovery error: {e}")
        
        return posts
    
    async def _instagram_api_hashtag_search(
        self, hashtag: str, max_posts: int
    ) -> List[SocialMediaPost]:
        """Use Instagram API for hashtag search."""
        posts = []
        
        try:
            # Get hashtag media using instagrapi
            media_items = self.instagram_client.hashtag_medias_recent(
                name=hashtag.replace('#', ''), amount=max_posts
            )
            
            for media in media_items:
                post = SocialMediaPost(
                    post_id=media.id,
                    platform=SocialMediaPlatform.INSTAGRAM,
                    author_username=media.user.username,
                    author_id=str(media.user.pk),
                    content_text=media.caption_text or "",
                    media_urls=[media.thumbnail_url] if media.thumbnail_url else [],
                    hashtags=self._extract_hashtags(media.caption_text or ""),
                    mentions=self._extract_mentions(media.caption_text or ""),
                    like_count=media.like_count,
                    comment_count=media.comment_count,
                    view_count=getattr(media, 'view_count', 0),
                    posted_at=media.taken_at,
                    metadata={
                        'media_type': media.media_type,
                        'location': media.location.name if media.location else None,
                        'is_video': media.media_type == 2
                    }
                )
                
                # Calculate engagement rate
                total_followers = getattr(media.user, 'follower_count', 1)
                post.engagement_rate = (
                    (post.like_count + post.comment_count) / max(total_followers, 1)
                ) * 100
                
                posts.append(post)
                
        except Exception as e:
            self.logger.error(f"Instagram API hashtag search error: {e}")
        
        return posts
    
    async def _instagram_web_scraping_hashtag(
        self, hashtag: str, max_posts: int
    ) -> List[SocialMediaPost]:
        """Web scraping for Instagram hashtag content."""
        posts = []
        
        try:
            driver = await self._get_browser_instance()
            hashtag_url = f"https://www.instagram.com/explore/tags/{hashtag.replace('#', '')}/"
            
            driver.get(hashtag_url)
            await asyncio.sleep(random.uniform(2, 4))
            
            # Scroll to load more posts
            for _ in range(max_posts // 12):  # Instagram loads ~12 posts per scroll
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                await asyncio.sleep(random.uniform(1, 2))
            
            # Extract post elements
            post_elements = driver.find_elements(By.CSS_SELECTOR, 'article a')
            
            for i, element in enumerate(post_elements[:max_posts]):
                try:
                    post_url = element.get_attribute('href')
                    post_id = post_url.split('/p/')[-1].split('/')[0]
                    
                    # Get post preview image
                    img_element = element.find_element(By.TAG_NAME, 'img')
                    img_url = img_element.get_attribute('src')
                    
                    post = SocialMediaPost(
                        post_id=post_id,
                        platform=SocialMediaPlatform.INSTAGRAM,
                        author_username="",  # Will be filled by detailed scraping
                        author_id="",
                        media_urls=[img_url] if img_url else [],
                        metadata={'post_url': post_url, 'scraped': True}
                    )
                    
                    posts.append(post)
                    
                except Exception as e:
                    self.logger.debug(f"Error extracting Instagram post {i}: {e}")
                    continue
            
            await self._return_browser_instance(driver)
            
        except Exception as e:
            self.logger.error(f"Instagram web scraping error: {e}")
        
        return posts
    
    async def _discover_tiktok_hashtag(
        self, hashtag: str, max_posts: int
    ) -> List[SocialMediaPost]:
        """Discover TikTok posts by hashtag using web scraping."""
        posts = []
        
        try:
            driver = await self._get_browser_instance()
            
            # TikTok hashtag URL
            hashtag_url = f"https://www.tiktok.com/tag/{hashtag.replace('#', '')}"
            driver.get(hashtag_url)
            
            # Wait for content to load
            await asyncio.sleep(random.uniform(3, 5))
            
            # Scroll to load more videos
            for _ in range(max_posts // 10):
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                await asyncio.sleep(random.uniform(2, 3))
            
            # Extract video elements
            video_elements = driver.find_elements(
                By.CSS_SELECTOR, 
                '[data-e2e="recommend-list-item-container"]'
            )
            
            for i, element in enumerate(video_elements[:max_posts]):
                try:
                    # Extract video data
                    video_link = element.find_element(By.CSS_SELECTOR, 'a').get_attribute('href')
                    video_id = video_link.split('/')[-1] if video_link else f"tiktok_{i}"
                    
                    # Extract author
                    author_element = element.find_element(By.CSS_SELECTOR, '[data-e2e="recommend-list-item-username"]')
                    author_username = author_element.text.replace('@', '') if author_element else ""
                    
                    # Extract description
                    desc_elements = element.find_elements(By.CSS_SELECTOR, '[data-e2e="recommend-list-item-desc"]')
                    description = desc_elements[0].text if desc_elements else ""
                    
                    # Extract engagement metrics
                    like_elements = element.find_elements(By.CSS_SELECTOR, '[data-e2e="like-count"]')
                    like_count = self._parse_tiktok_count(like_elements[0].text) if like_elements else 0
                    
                    comment_elements = element.find_elements(By.CSS_SELECTOR, '[data-e2e="comment-count"]')
                    comment_count = self._parse_tiktok_count(comment_elements[0].text) if comment_elements else 0
                    
                    share_elements = element.find_elements(By.CSS_SELECTOR, '[data-e2e="share-count"]')
                    share_count = self._parse_tiktok_count(share_elements[0].text) if share_elements else 0
                    
                    post = SocialMediaPost(
                        post_id=video_id,
                        platform=SocialMediaPlatform.TIKTOK,
                        author_username=author_username,
                        author_id="",
                        content_text=description,
                        hashtags=self._extract_hashtags(description),
                        mentions=self._extract_mentions(description),
                        like_count=like_count,
                        comment_count=comment_count,
                        share_count=share_count,
                        metadata={
                            'video_url': video_link,
                            'platform_specific': True
                        }
                    )
                    
                    posts.append(post)
                    
                except Exception as e:
                    self.logger.debug(f"Error extracting TikTok video {i}: {e}")
                    continue
            
            await self._return_browser_instance(driver)
            
        except Exception as e:
            self.logger.error(f"TikTok hashtag discovery error: {e}")
        
        return posts
    
    def _parse_tiktok_count(self, count_text: str) -> int:
        """Parse TikTok count strings (e.g., '1.2M', '500K', '1234')."""
        if not count_text:
            return 0
        
        count_text = count_text.strip().upper()
        
        try:
            if 'M' in count_text:
                return int(float(count_text.replace('M', '')) * 1000000)
            elif 'K' in count_text:
                return int(float(count_text.replace('K', '')) * 1000)
            else:
                return int(count_text)
        except (ValueError, TypeError):
            return 0
    
    async def _discover_youtube_hashtag(
        self, hashtag: str, max_posts: int
    ) -> List[SocialMediaPost]:
        """Discover YouTube videos by hashtag using YouTube Data API."""
        posts = []
        
        if not hasattr(self, 'youtube_api_key') or not self.youtube_api_key:
            self.logger.warning("YouTube API key not configured")
            return posts
        
        try:
            # YouTube Data API search
            search_url = "https://www.googleapis.com/youtube/v3/search"
            params = {
                'key': self.youtube_api_key,
                'q': f"#{hashtag}",
                'part': 'snippet',
                'type': 'video',
                'maxResults': min(max_posts, 50),
                'order': 'relevance'
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(search_url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        for item in data.get('items', []):
                            snippet = item['snippet']
                            video_id = item['id']['videoId']
                            
                            # Get video statistics
                            stats = await self._get_youtube_video_stats(video_id)
                            
                            post = SocialMediaPost(
                                post_id=video_id,
                                platform=SocialMediaPlatform.YOUTUBE,
                                author_username=snippet['channelTitle'],
                                author_id=snippet['channelId'],
                                content_text=snippet['description'],
                                media_urls=[snippet['thumbnails']['high']['url']],
                                hashtags=self._extract_hashtags(snippet['description']),
                                mentions=self._extract_mentions(snippet['description']),
                                like_count=stats.get('like_count', 0),
                                comment_count=stats.get('comment_count', 0),
                                view_count=stats.get('view_count', 0),
                                posted_at=datetime.fromisoformat(
                                    snippet['publishedAt'].replace('Z', '+00:00')
                                ),
                                metadata={
                                    'video_url': f"https://www.youtube.com/watch?v={video_id}",
                                    'duration': stats.get('duration', ''),
                                    'category_id': snippet.get('categoryId', ''),
                                    'tags': snippet.get('tags', [])
                                }
                            )
                            
                            posts.append(post)
                    
                    else:
                        self.logger.error(f"YouTube API error: {response.status}")
            
        except Exception as e:
            self.logger.error(f"YouTube hashtag discovery error: {e}")
        
        return posts
    
    async def _get_youtube_video_stats(self, video_id: str) -> Dict[str, Any]:
        """Get detailed statistics for YouTube video."""
        if not hasattr(self, 'youtube_api_key') or not self.youtube_api_key:
            return {}
        
        try:
            stats_url = "https://www.googleapis.com/youtube/v3/videos"
            params = {
                'key': self.youtube_api_key,
                'id': video_id,
                'part': 'statistics,contentDetails'
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(stats_url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        items = data.get('items', [])
                        
                        if items:
                            stats = items[0]['statistics']
                            content = items[0]['contentDetails']
                            
                            return {
                                'view_count': int(stats.get('viewCount', 0)),
                                'like_count': int(stats.get('likeCount', 0)),
                                'comment_count': int(stats.get('commentCount', 0)),
                                'duration': content.get('duration', '')
                            }
            
        except Exception as e:
            self.logger.debug(f"YouTube stats error for video {video_id}: {e}")
        
        return {}
    
    async def _discover_twitter_hashtag(
        self, hashtag: str, max_posts: int
    ) -> List[SocialMediaPost]:
        """Discover Twitter/X posts by hashtag using Twitter API."""
        posts = []
        
        if not hasattr(self, 'twitter_client'):
            self.logger.warning("Twitter client not configured")
            return posts
        
        try:
            # Search tweets with hashtag
            tweets = tweepy.Paginator(
                self.twitter_client.search_recent_tweets,
                query=f"#{hashtag} -is:retweet",
                max_results=min(max_posts, 100),
                tweet_fields=['author_id', 'created_at', 'public_metrics', 'context_annotations']
            ).flatten(limit=max_posts)
            
            for tweet in tweets:
                # Get user info
                user = self.twitter_client.get_user(id=tweet.author_id)
                
                post = SocialMediaPost(
                    post_id=str(tweet.id),
                    platform=SocialMediaPlatform.TWITTER,
                    author_username=user.data.username if user.data else "",
                    author_id=str(tweet.author_id),
                    content_text=tweet.text,
                    hashtags=self._extract_hashtags(tweet.text),
                    mentions=self._extract_mentions(tweet.text),
                    like_count=tweet.public_metrics['like_count'],
                    comment_count=tweet.public_metrics['reply_count'],
                    share_count=tweet.public_metrics['retweet_count'],
                    posted_at=tweet.created_at,
                    metadata={
                        'tweet_url': f"https://twitter.com/{user.data.username if user.data else 'unknown'}/status/{tweet.id}",
                        'context_annotations': tweet.context_annotations or []
                    }
                )
                
                posts.append(post)
                
        except Exception as e:
            self.logger.error(f"Twitter hashtag discovery error: {e}")
        
        return posts
    
    async def _discover_reddit_hashtag(
        self, hashtag: str, max_posts: int
    ) -> List[SocialMediaPost]:
        """Discover Reddit posts related to hashtag using web scraping."""
        posts = []
        
        try:
            # Reddit search URL
            search_url = f"https://www.reddit.com/search.json"
            params = {
                'q': hashtag,
                'sort': 'relevance',
                'limit': min(max_posts, 100)
            }
            
            headers = {
                'User-Agent': random.choice(self.user_agents)
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(search_url, params=params, headers=headers) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        for item in data['data']['children']:
                            post_data = item['data']
                            
                            post = SocialMediaPost(
                                post_id=post_data['id'],
                                platform=SocialMediaPlatform.REDDIT,
                                author_username=post_data['author'],
                                author_id=post_data['author'],
                                content_text=f"{post_data.get('title', '')} {post_data.get('selftext', '')}",
                                like_count=post_data.get('ups', 0),
                                comment_count=post_data.get('num_comments', 0),
                                posted_at=datetime.fromtimestamp(post_data['created_utc']),
                                metadata={
                                    'subreddit': post_data['subreddit'],
                                    'post_url': f"https://reddit.com{post_data['permalink']}",
                                    'score': post_data.get('score', 0),
                                    'upvote_ratio': post_data.get('upvote_ratio', 0.0)
                                }
                            )
                            
                            posts.append(post)
            
        except Exception as e:
            self.logger.error(f"Reddit hashtag discovery error: {e}")
        
        return posts
    
    async def _discover_generic_platform(
        self, hashtag: str, platform: SocialMediaPlatform, max_posts: int
    ) -> List[SocialMediaPost]:
        """Generic platform discovery using web scraping."""
        posts = []
        
        try:
            # Platform-specific search URLs and selectors
            platform_config = {
                SocialMediaPlatform.LINKEDIN: {
                    'search_url': f'https://www.linkedin.com/search/results/content/?keywords=%23{hashtag}',
                    'post_selector': '.feed-shared-update-v2'
                },
                SocialMediaPlatform.PINTEREST: {
                    'search_url': f'https://www.pinterest.com/search/pins/?q={hashtag}',
                    'post_selector': '[data-test-id="pin"]'
                }
            }
            
            if platform not in platform_config:
                return posts
            
            config = platform_config[platform]
            driver = await self._get_browser_instance()
            
            driver.get(config['search_url'])
            await asyncio.sleep(random.uniform(3, 5))
            
            # Scroll and extract posts
            elements = driver.find_elements(By.CSS_SELECTOR, config['post_selector'])
            
            for i, element in enumerate(elements[:max_posts]):
                try:
                    # Generic extraction - adapt based on platform
                    post_text = element.text
                    
                    post = SocialMediaPost(
                        post_id=f"{platform.value}_{i}_{int(time.time())}",
                        platform=platform,
                        author_username="unknown",
                        author_id="unknown",
                        content_text=post_text[:1000],  # Limit content
                        hashtags=self._extract_hashtags(post_text),
                        mentions=self._extract_mentions(post_text),
                        metadata={'scraped_generic': True}
                    )
                    
                    posts.append(post)
                    
                except Exception as e:
                    self.logger.debug(f"Error extracting {platform.value} post {i}: {e}")
                    continue
            
            await self._return_browser_instance(driver)
            
        except Exception as e:
            self.logger.error(f"Generic platform discovery error for {platform.value}: {e}")
        
        return posts
    
    def _extract_hashtags(self, text: str) -> List[str]:
        """Extract hashtags from text."""
        if not text:
            return []
        
        hashtag_pattern = r'#\w+'
        hashtags = re.findall(hashtag_pattern, text, re.IGNORECASE)
        return [tag.lower() for tag in hashtags]
    
    def _extract_mentions(self, text: str) -> List[str]:
        """Extract mentions from text."""
        if not text:
            return []
        
        mention_pattern = r'@\w+'
        mentions = re.findall(mention_pattern, text, re.IGNORECASE)
        return [mention.lower() for mention in mentions]
    
    async def _analyze_content_similarities(
        self, posts: List[SocialMediaPost]
    ) -> List[SocialMediaPost]:
        """Analyze content similarities for copyright infringement detection."""
        try:
            self.logger.info(f"Analyzing content similarities for {len(posts)} posts")
            
            # Group posts by content type for similarity analysis
            text_posts = [p for p in posts if p.content_text]
            image_posts = [p for p in posts if p.media_urls]
            
            # Analyze text similarities
            if text_posts:
                await self._analyze_text_similarities(text_posts)
            
            # Analyze image similarities
            if image_posts:
                await self._analyze_image_similarities(image_posts)
            
            # Mark potential infringements
            for post in posts:
                if post.similarity_score > self.content_similarity_threshold:
                    post.potential_infringement = True
            
            return posts
            
        except Exception as e:
            self.logger.error(f"Content similarity analysis error: {e}")
            return posts
    
    async def _analyze_text_similarities(self, posts: List[SocialMediaPost]):
        """Analyze text content similarities using NLP techniques."""
        try:
            # Simple text similarity using character-level comparison
            # In production, would use BERT/RoBERTa embeddings
            
            for i, post1 in enumerate(posts):
                for j, post2 in enumerate(posts[i+1:], i+1):
                    similarity = self._calculate_text_similarity(
                        post1.content_text, post2.content_text
                    )
                    
                    # Update similarity scores
                    post1.similarity_score = max(post1.similarity_score, similarity)
                    post2.similarity_score = max(post2.similarity_score, similarity)
        
        except Exception as e:
            self.logger.error(f"Text similarity analysis error: {e}")
    
    def _calculate_text_similarity(self, text1: str, text2: str) -> float:
        """Calculate similarity between two text strings."""
        if not text1 or not text2:
            return 0.0
        
        # Simple character-level similarity (Jaccard similarity)
        set1 = set(text1.lower())
        set2 = set(text2.lower())
        
        intersection = len(set1.intersection(set2))
        union = len(set1.union(set2))
        
        return intersection / max(union, 1)
    
    async def _analyze_image_similarities(self, posts: List[SocialMediaPost]):
        """Analyze image content similarities using perceptual hashing."""
        try:
            # Download and analyze images
            image_hashes = {}
            
            for post in posts:
                if post.media_urls:
                    primary_image_url = post.media_urls[0]
                    image_hash = await self._calculate_image_hash(primary_image_url)
                    
                    if image_hash:
                        image_hashes[post.post_id] = image_hash
            
            # Compare image hashes
            for post1_id, hash1 in image_hashes.items():
                for post2_id, hash2 in image_hashes.items():
                    if post1_id != post2_id:
                        hash_distance = hash1 - hash2
                        
                        if hash_distance < self.image_hash_threshold:
                            # Images are similar
                            similarity = 1.0 - (hash_distance / 64.0)  # Normalize to 0-1
                            
                            # Update similarity scores for both posts
                            for post in posts:
                                if post.post_id in [post1_id, post2_id]:
                                    post.similarity_score = max(post.similarity_score, similarity)
        
        except Exception as e:
            self.logger.error(f"Image similarity analysis error: {e}")
    
    async def _calculate_image_hash(self, image_url: str) -> Optional[imagehash.ImageHash]:
        """Calculate perceptual hash for image."""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(image_url) as response:
                    if response.status == 200:
                        image_data = await response.read()
                        
                        # Create PIL Image
                        image = Image.open(io.BytesIO(image_data))
                        
                        # Calculate perceptual hash
                        return imagehash.phash(image)
            
        except Exception as e:
            self.logger.debug(f"Image hash calculation error for {image_url}: {e}")
            return None
    
    async def monitor_competitor_accounts(
        self,
        competitor_usernames: List[str],
        platforms: List[SocialMediaPlatform],
        monitoring_duration: timedelta = timedelta(days=7)
    ) -> List[SocialMediaPost]:
        """
        Monitor competitor accounts for content analysis and inspiration.
        
        Provides comprehensive competitor content monitoring across platforms
        for strategic insights and trend analysis.
        """
        try:
            self.logger.info(f"Starting competitor monitoring for {len(competitor_usernames)} accounts")
            
            all_competitor_posts = []
            
            for username in competitor_usernames:
                for platform in platforms:
                    try:
                        posts = await self._monitor_account_platform(username, platform)
                        all_competitor_posts.extend(posts)
                        
                        # Rate limiting between accounts
                        await asyncio.sleep(random.uniform(1, 3))
                        
                    except Exception as e:
                        self.logger.error(f"Error monitoring {username} on {platform.value}: {e}")
                        continue
            
            # Analyze competitive intelligence
            analyzed_posts = await self._analyze_competitor_content(all_competitor_posts)
            
            self.logger.info(f"Competitor monitoring completed: {len(analyzed_posts)} posts analyzed")
            
            return analyzed_posts
            
        except Exception as e:
            self.logger.error(f"Competitor monitoring failed: {e}")
            raise CrawlerException(f"Competitor monitoring error: {e}")
    
    async def _monitor_account_platform(
        self, username: str, platform: SocialMediaPlatform
    ) -> List[SocialMediaPost]:
        """Monitor specific account on specific platform."""
        await self.rate_limiters[platform].acquire()
        
        try:
            if platform == SocialMediaPlatform.INSTAGRAM:
                return await self._monitor_instagram_account(username)
            elif platform == SocialMediaPlatform.TIKTOK:
                return await self._monitor_tiktok_account(username)
            elif platform == SocialMediaPlatform.YOUTUBE:
                return await self._monitor_youtube_account(username)
            elif platform == SocialMediaPlatform.TWITTER:
                return await self._monitor_twitter_account(username)
            else:
                return []
                
        except Exception as e:
            self.logger.error(f"Account monitoring error for {username} on {platform.value}: {e}")
            return []
    
    async def _monitor_instagram_account(self, username: str) -> List[SocialMediaPost]:
        """Monitor Instagram account for recent posts."""
        posts = []
        
        try:
            if hasattr(self, 'instagram_client') and self.instagram_client.user_id:
                # API method
                user_id = self.instagram_client.user_id_from_username(username)
                media_items = self.instagram_client.user_medias(user_id, amount=20)
                
                for media in media_items:
                    post = SocialMediaPost(
                        post_id=media.id,
                        platform=SocialMediaPlatform.INSTAGRAM,
                        author_username=username,
                        author_id=str(user_id),
                        content_text=media.caption_text or "",
                        media_urls=[media.thumbnail_url] if media.thumbnail_url else [],
                        hashtags=self._extract_hashtags(media.caption_text or ""),
                        mentions=self._extract_mentions(media.caption_text or ""),
                        like_count=media.like_count,
                        comment_count=media.comment_count,
                        posted_at=media.taken_at,
                        metadata={
                            'competitor_analysis': True,
                            'media_type': media.media_type
                        }
                    )
                    posts.append(post)
            
        except Exception as e:
            self.logger.error(f"Instagram account monitoring error for {username}: {e}")
        
        return posts
    
    async def _analyze_competitor_content(
        self, posts: List[SocialMediaPost]
    ) -> List[SocialMediaPost]:
        """Analyze competitor content for strategic insights."""
        try:
            # Analyze posting patterns
            posting_patterns = self._analyze_posting_patterns(posts)
            
            # Analyze hashtag strategies
            hashtag_analysis = self._analyze_hashtag_strategies(posts)
            
            # Analyze engagement patterns
            engagement_analysis = self._analyze_engagement_patterns(posts)
            
            # Add competitive intelligence metadata
            for post in posts:
                post.metadata.update({
                    'posting_patterns': posting_patterns,
                    'hashtag_strategy': hashtag_analysis,
                    'engagement_analysis': engagement_analysis
                })
            
            return posts
            
        except Exception as e:
            self.logger.error(f"Competitor content analysis error: {e}")
            return posts
    
    def _analyze_posting_patterns(self, posts: List[SocialMediaPost]) -> Dict[str, Any]:
        """Analyze posting time patterns and frequency."""
        if not posts:
            return {}
        
        # Analyze posting times
        posting_hours = []
        posting_days = []
        
        for post in posts:
            if post.posted_at:
                posting_hours.append(post.posted_at.hour)
                posting_days.append(post.posted_at.weekday())
        
        # Calculate optimal posting times
        if posting_hours:
            optimal_hour = max(set(posting_hours), key=posting_hours.count)
            optimal_day = max(set(posting_days), key=posting_days.count)
        else:
            optimal_hour = optimal_day = None
        
        return {
            'optimal_posting_hour': optimal_hour,
            'optimal_posting_day': optimal_day,
            'posting_frequency': len(posts),
            'average_posts_per_day': len(posts) / max((datetime.utcnow() - min(p.posted_at for p in posts if p.posted_at)).days, 1)
        }
    
    def _analyze_hashtag_strategies(self, posts: List[SocialMediaPost]) -> Dict[str, Any]:
        """Analyze hashtag usage strategies."""
        all_hashtags = []
        hashtag_counts = {}
        
        for post in posts:
            all_hashtags.extend(post.hashtags)
            hashtag_counts[len(post.hashtags)] = hashtag_counts.get(len(post.hashtags), 0) + 1
        
        # Most used hashtags
        hashtag_frequency = {}
        for hashtag in all_hashtags:
            hashtag_frequency[hashtag] = hashtag_frequency.get(hashtag, 0) + 1
        
        top_hashtags = sorted(hashtag_frequency.items(), key=lambda x: x[1], reverse=True)[:10]
        
        return {
            'top_hashtags': top_hashtags,
            'average_hashtags_per_post': len(all_hashtags) / max(len(posts), 1),
            'hashtag_distribution': hashtag_counts,
            'unique_hashtags': len(set(all_hashtags))
        }
    
    def _analyze_engagement_patterns(self, posts: List[SocialMediaPost]) -> Dict[str, Any]:
        """Analyze engagement patterns and performance."""
        if not posts:
            return {}
        
        # Calculate engagement metrics
        total_likes = sum(post.like_count for post in posts)
        total_comments = sum(post.comment_count for post in posts)
        total_shares = sum(post.share_count for post in posts)
        
        avg_likes = total_likes / len(posts)
        avg_comments = total_comments / len(posts)
        avg_shares = total_shares / len(posts)
        
        # Find best performing post
        best_post = max(posts, key=lambda p: p.like_count + p.comment_count + p.share_count)
        
        return {
            'average_likes': avg_likes,
            'average_comments': avg_comments,
            'average_shares': avg_shares,
            'total_engagement': total_likes + total_comments + total_shares,
            'best_performing_post': {
                'post_id': best_post.post_id,
                'total_engagement': best_post.like_count + best_post.comment_count + best_post.share_count,
                'content_preview': best_post.content_text[:100]
            }
        }
    
    async def _get_browser_instance(self):
        """Get browser instance from pool or create new one."""
        try:
            if self.browser_pool:
                return self.browser_pool.pop()
            
            # Create new browser instance
            options = self.chrome_options
            service = Service()  # Use default chromedriver
            
            driver = webdriver.Chrome(service=service, options=options)
            
            # Anti-detection measures
            driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            driver.execute_cdp_cmd('Network.setUserAgentOverride', {
                "userAgent": random.choice(self.user_agents)
            })
            
            return driver
            
        except Exception as e:
            self.logger.error(f"Failed to create browser instance: {e}")
            raise CrawlerException(f"Browser initialization error: {e}")
    
    async def _return_browser_instance(self, driver):
        """Return browser instance to pool or close if pool is full."""
        try:
            if len(self.browser_pool) < self.max_browsers:
                # Clear cookies and reset state
                driver.delete_all_cookies()
                driver.get("about:blank")
                self.browser_pool.append(driver)
            else:
                driver.quit()
                
        except Exception as e:
            self.logger.error(f"Error returning browser instance: {e}")
            try:
                driver.quit()
            except:
                pass
    
    async def cleanup_social_media_crawler(self):
        """Clean up social media crawler resources."""
        try:
            # Close all browser instances
            for driver in self.browser_pool:
                try:
                    driver.quit()
                except:
                    pass
            
            self.browser_pool.clear()
            
            # Call parent cleanup
            await self.cleanup_crawler_resources()
            
            self.logger.info("Social media crawler resources cleaned up")
            
        except Exception as e:
            self.logger.error(f"Error cleaning up social media crawler: {e}")


# Export classes
__all__ = [
    "SocialMediaCrawler",
    "SocialMediaPost", 
    "SocialMediaProfile",
    "SocialMediaPlatform",
    "ContentDiscoveryMode"
]
