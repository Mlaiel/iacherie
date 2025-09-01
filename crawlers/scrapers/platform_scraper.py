"""Platform Scraper - IA-Influencer-Agent
======================================

Specialized scraper for social media and content platforms.
Integrates with platform-specific crawlers and APIs.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: All rights reserved. Unauthorized use, reproduction, or distribution prohibited.

⚠️ CRITICAL LEGAL WARNING ⚠️
UNAUTHORIZED USE, COPYING, OR DISTRIBUTION IS STRICTLY PROHIBITED AND WILL RESULT IN IMMEDIATE LEGAL ACTION.
This technology is EXCLUSIVE property of Fahed Mlaiel. Contact: mlaiel@live.de for licensing.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass
from datetime import datetime
from urllib.parse import urlparse, parse_qs
import re
import json

from ..platforms.youtube_crawler import YouTubeCrawler
from ..platforms.instagram_crawler import InstagramCrawler
from ..platforms.tiktok_crawler import TikTokCrawler
from ..platforms.twitter_crawler import TwitterCrawler
from ..platforms.facebook_crawler import FacebookCrawler
from ..platforms.linkedin_crawler import LinkedInCrawler
from ..platforms.spotify_crawler import SpotifyCrawler
from ..platforms.soundcloud_crawler import SoundCloudCrawler
from ..platforms.twitch_crawler import TwitchCrawler
from ..platforms.reddit_crawler import RedditCrawler
from ..platforms.medium_crawler import MediumCrawler
from ..platforms.pinterest_crawler import PinterestCrawler
from ..platforms.generic_crawler import GenericCrawler

@dataclass
class PlatformContent:
    """
Standardized platform content structure."""
    platform: str
    content_id: str
    url: str
    title: str
    description: str
    author: str
    author_id: str
    author_followers: int
    created_at: Optional[datetime]
    engagement: Dict[str, int]  # likes, shares, comments, views
    hashtags: List[str]
    mentions: List[str]
    media_urls: List[str]
    content_type: str  # post, video, image, story, etc.
    language: str
    location: Optional[str]
    metadata: Dict[str, Any]
    raw_data: Dict[str, Any]
    extracted_at: datetime

@dataclass
class PlatformProfile:
    """
Standardized platform profile structure."""
    platform: str
    username: str
    user_id: str
    display_name: str
    bio: str
    profile_image: str
    followers_count: int
    following_count: int
    posts_count: int
    verified: bool
    account_type: str  # personal, business, creator
    created_at: Optional[datetime]
    location: Optional[str]
    website: Optional[str]
    contact_info: Dict[str, Any]
    metadata: Dict[str, Any]
    extracted_at: datetime

class PlatformScraper:
    """
    Unified platform scraping interface.
    
    Features:
    - Multi-platform support
    - Standardized data structures
    - Rate limiting and compliance
    - Error handling and retries
    - Content normalization
    - Engagement tracking
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.crawlers = self._initialize_crawlers()
        self.supported_platforms = list(self.crawlers.keys())
        
    def _initialize_crawlers(self) -> Dict[str, Any]:
        """
Initialize platform-specific crawlers."""
        return {
            'youtube': YouTubeCrawler(),
            'instagram': InstagramCrawler(),
            'tiktok': TikTokCrawler(),
            'twitter': TwitterCrawler(),
            'facebook': FacebookCrawler(),
            'linkedin': LinkedInCrawler(),
            'spotify': SpotifyCrawler(),
            'soundcloud': SoundCloudCrawler(),
            'twitch': TwitchCrawler(),
            'reddit': RedditCrawler(),
            'medium': MediumCrawler(),
            'pinterest': PinterestCrawler(),
            'generic': GenericCrawler()
        }
        
    def detect_platform(self, url: str) -> str:
        """
Detect platform from URL."""
        domain = urlparse(url).netloc.lower()
        
        platform_domains = {
            'youtube.com': 'youtube',
            'youtu.be': 'youtube',
            'instagram.com': 'instagram',
            'tiktok.com': 'tiktok',
            'twitter.com': 'twitter',
            'x.com': 'twitter',
            'facebook.com': 'facebook',
            'fb.com': 'facebook',
            'linkedin.com': 'linkedin',
            'spotify.com': 'spotify',
            'soundcloud.com': 'soundcloud',
            'twitch.tv': 'twitch',
            'reddit.com': 'reddit',
            'medium.com': 'medium',
            'pinterest.com': 'pinterest',
            'pin.it': 'pinterest'
        }
        
        for domain_key, platform in platform_domains.items():
            if domain_key in domain:
                return platform
                
        return 'generic'
        
    async def scrape_content(self, url: str, **kwargs) -> Optional[PlatformContent]:
        """
Scrape content from platform URL."""
        platform = self.detect_platform(url)
        
        if platform not in self.crawlers:
            self.logger.warning(f"Unsupported platform for URL: {url}")
            return None
            
        try:
            crawler = self.crawlers[platform]
            raw_data = await crawler.extract_content(url, **kwargs)
            
            if not raw_data:
                return None
                
            return self._normalize_content(platform, url, raw_data)
            
        except Exception as e:
            self.logger.error(f"Error scraping content from {url}: {e}")
            return None
            
    async def scrape_profile(self, url: str, **kwargs) -> Optional[PlatformProfile]:
        """Scrape profile from platform URL."""
        platform = self.detect_platform(url)
        
        if platform not in self.crawlers:
            self.logger.warning(f"Unsupported platform for URL: {url}")
            return None
            
        try:
            crawler = self.crawlers[platform]
            raw_data = await crawler.extract_profile(url, **kwargs)
            
            if not raw_data:
                return None
                
            return self._normalize_profile(platform, url, raw_data)
            
        except Exception as e:
            self.logger.error(f"Error scraping profile from {url}: {e}")
            return None
            
    async def search_content(self, platform: str, query: str, 
                           content_type: str = 'all', limit: int = 50,
                           **kwargs) -> List[PlatformContent]:
        """Search for content on specific platform."""
        if platform not in self.crawlers:
            self.logger.warning(f"Unsupported platform: {platform}")
            return []
            
        try:
            crawler = self.crawlers[platform]
            if hasattr(crawler, 'search_content'):
                results = await crawler.search_content(
                    query, content_type=content_type, limit=limit, **kwargs
                )
                
                normalized_results = []
                for result in results:
                    normalized = self._normalize_content(platform, result.get('url', ''), result)
                    if normalized:
                        normalized_results.append(normalized)
                        
                return normalized_results
            else:
                self.logger.warning(f"Search not supported for platform: {platform}")
                return []
                
        except Exception as e:
            self.logger.error(f"Error searching content on {platform}: {e}")
            return []
            
    async def monitor_hashtag(self, platform: str, hashtag: str, 
                            limit: int = 100) -> List[PlatformContent]:
        """Monitor hashtag across platform."""
        query = f"#{hashtag}" if not hashtag.startswith('#') else hashtag
        return await self.search_content(platform, query, limit=limit)
        
    async def monitor_user(self, platform: str, username: str, 
                         limit: int = 50) -> List[PlatformContent]:
        """Monitor user content across platform."""
        if platform not in self.crawlers:
            return []
            
        try:
            crawler = self.crawlers[platform]
            if hasattr(crawler, 'get_user_content'):
                results = await crawler.get_user_content(username, limit=limit)
                
                normalized_results = []
                for result in results:
                    normalized = self._normalize_content(platform, result.get('url', ''), result)
                    if normalized:
                        normalized_results.append(normalized)
                        
                return normalized_results
            else:
                # Fallback to search
                return await self.search_content(platform, f"from:{username}", limit=limit)
                
        except Exception as e:
            self.logger.error(f"Error monitoring user {username} on {platform}: {e}")
            return []
            
    def _normalize_content(self, platform: str, url: str, raw_data: Dict[str, Any]) -> PlatformContent:
        """Normalize raw platform data to standard structure."""
        # Common field mappings across platforms
        field_mappings = {
            'youtube': {
                'content_id': 'video_id',
                'title': 'title',
                'description': 'description',
                'author': 'channel_name',
                'author_id': 'channel_id',
                'created_at': 'published_at',
                'views': 'view_count',
                'likes': 'like_count',
                'comments': 'comment_count'
            },
            'instagram': {
                'content_id': 'id',
                'title': 'caption',
                'description': 'caption',
                'author': 'username',
                'author_id': 'user_id',
                'created_at': 'timestamp',
                'likes': 'like_count',
                'comments': 'comment_count'
            },
            'tiktok': {
                'content_id': 'id',
                'title': 'desc',
                'description': 'desc',
                'author': 'author',
                'author_id': 'authorId',
                'created_at': 'createTime',
                'likes': 'diggCount',
                'shares': 'shareCount',
                'comments': 'commentCount',
                'views': 'playCount'
            },
            'twitter': {
                'content_id': 'id_str',
                'title': 'text',
                'description': 'text',
                'author': 'user.screen_name',
                'author_id': 'user.id_str',
                'created_at': 'created_at',
                'likes': 'favorite_count',
                'shares': 'retweet_count',
                'comments': 'reply_count'
            }
        }
        
        mapping = field_mappings.get(platform, {})
        
        # Extract basic fields
        content_id = self._get_nested_value(raw_data, mapping.get('content_id', 'id'))
        title = self._get_nested_value(raw_data, mapping.get('title', 'title'))
        description = self._get_nested_value(raw_data, mapping.get('description', 'description'))
        author = self._get_nested_value(raw_data, mapping.get('author', 'author'))
        author_id = self._get_nested_value(raw_data, mapping.get('author_id', 'author_id'))
        
        # Parse created_at
        created_at = None
        created_at_raw = self._get_nested_value(raw_data, mapping.get('created_at', 'created_at'))
        if created_at_raw:
            created_at = self._parse_datetime(created_at_raw)
            
        # Extract engagement metrics
        engagement = {
            'likes': self._get_nested_value(raw_data, mapping.get('likes', 'likes')) or 0,
            'shares': self._get_nested_value(raw_data, mapping.get('shares', 'shares')) or 0,
            'comments': self._get_nested_value(raw_data, mapping.get('comments', 'comments')) or 0,
            'views': self._get_nested_value(raw_data, mapping.get('views', 'views')) or 0
        }
        
        # Extract hashtags and mentions
        hashtags = self._extract_hashtags(title or description or '')
        mentions = self._extract_mentions(title or description or '')
        
        # Extract media URLs
        media_urls = self._extract_media_urls(raw_data, platform)
        
        # Detect content type
        content_type = self._detect_content_type(raw_data, platform)
        
        # Detect language
        language = self._detect_language(title or description or '')
        
        return PlatformContent(
            platform=platform,
            content_id=str(content_id) if content_id else '',
            url=url,
            title=str(title) if title else '',
            description=str(description) if description else '',
            author=str(author) if author else '',
            author_id=str(author_id) if author_id else '',
            author_followers=self._get_nested_value(raw_data, 'author_followers') or 0,
            created_at=created_at,
            engagement=engagement,
            hashtags=hashtags,
            mentions=mentions,
            media_urls=media_urls,
            content_type=content_type,
            language=language,
            location=self._get_nested_value(raw_data, 'location'),
            metadata=self._extract_metadata(raw_data, platform),
            raw_data=raw_data,
            extracted_at=datetime.now()
        )
        
    def _normalize_profile(self, platform: str, url: str, raw_data: Dict[str, Any]) -> PlatformProfile:
        """
Normalize raw profile data to standard structure."""
        return PlatformProfile(
            platform=platform,
            username=str(self._get_nested_value(raw_data, 'username') or ''),
            user_id=str(self._get_nested_value(raw_data, 'user_id') or ''),
            display_name=str(self._get_nested_value(raw_data, 'display_name') or ''),
            bio=str(self._get_nested_value(raw_data, 'bio') or ''),
            profile_image=str(self._get_nested_value(raw_data, 'profile_image') or ''),
            followers_count=self._get_nested_value(raw_data, 'followers_count') or 0,
            following_count=self._get_nested_value(raw_data, 'following_count') or 0,
            posts_count=self._get_nested_value(raw_data, 'posts_count') or 0,
            verified=bool(self._get_nested_value(raw_data, 'verified')),
            account_type=str(self._get_nested_value(raw_data, 'account_type') or 'personal'),
            created_at=self._parse_datetime(self._get_nested_value(raw_data, 'created_at')),
            location=self._get_nested_value(raw_data, 'location'),
            website=self._get_nested_value(raw_data, 'website'),
            contact_info=self._extract_contact_info(raw_data),
            metadata=self._extract_metadata(raw_data, platform),
            extracted_at=datetime.now()
        )
        
    def _get_nested_value(self, data: Dict[str, Any], path: str) -> Any:
        """
Get nested dictionary value using dot notation."""
        keys = path.split('.')
        value = data
        
        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return None
                
        return value
        
    def _parse_datetime(self, date_str: Any) -> Optional[datetime]:
        """
Parse datetime from various formats."""
        if not date_str:
            return None
            
        if isinstance(date_str, datetime):
            return date_str
            
        # Common datetime formats
        formats = [
            '%Y-%m-%dT%H:%M:%SZ',
            '%Y-%m-%d %H:%M:%S',
            '%Y-%m-%d',
            '%a %b %d %H:%M:%S %z %Y',  # Twitter format
        ]
        
        for fmt in formats:
            try:
                return datetime.strptime(str(date_str), fmt)
            except:
                continue
                
        return None
        
    def _extract_hashtags(self, text: str) -> List[str]:
        """
Extract hashtags from text."""
        if not text:
            return []
        return re.findall(r'#(\w+)', text)
        
    def _extract_mentions(self, text: str) -> List[str]:
        """
Extract mentions from text."""
        if not text:
            return []
        return re.findall(r'@(\w+)', text)
        
    def _extract_media_urls(self, raw_data: Dict[str, Any], platform: str) -> List[str]:
        """
Extract media URLs from raw data."""
        media_urls = []
        
        # Common media fields across platforms
        media_fields = [
            'thumbnail_url', 'image_url', 'video_url', 'audio_url',
            'media', 'images', 'videos', 'attachments'
        ]
        
        for field in media_fields:
            value = self._get_nested_value(raw_data, field)
            if value:
                if isinstance(value, str):
                    media_urls.append(value)
                elif isinstance(value, list):
                    media_urls.extend([str(v) for v in value if v])
                    
        return media_urls
        
    def _detect_content_type(self, raw_data: Dict[str, Any], platform: str) -> str:
        """
Detect content type from raw data."""
        # Platform-specific content type detection
        if platform == 'youtube':
            return 'video'
        elif platform == 'instagram':
            media_type = self._get_nested_value(raw_data, 'media_type')
            if media_type:
                return media_type
            return 'image'
        elif platform == 'tiktok':
            return 'video'
        elif platform == 'twitter':
            if self._get_nested_value(raw_data, 'media'):
                return 'media'
            return 'text'
        elif platform == 'spotify' or platform == 'soundcloud':
            return 'audio'
            
        return 'post'
        
    def _detect_language(self, text: str) -> str:
        """
Detect language from text."""
        try:
            import langdetect
            if text and len(text) > 20:
                return langdetect.detect(text)
        except:
            pass
        return 'unknown'
        
    def _extract_contact_info(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """
Extract contact information from profile data."""
        contact_info = {}
        
        # Common contact fields
        contact_fields = ['email', 'phone', 'website', 'business_email']
        
        for field in contact_fields:
            value = self._get_nested_value(raw_data, field)
            if value:
                contact_info[field] = value
                
        return contact_info
        
    def _extract_metadata(self, raw_data: Dict[str, Any], platform: str) -> Dict[str, Any]:
        """
Extract platform-specific metadata."""
        metadata = {
            'platform_specific': {},
            'extraction_method': 'api' if 'api_response' in raw_data else 'scraping',
            'data_quality': self._assess_data_quality(raw_data)
        }
        
        # Platform-specific metadata extraction
        if platform == 'youtube':
            metadata['platform_specific'] = {
                'category': self._get_nested_value(raw_data, 'category'),
                'tags': self._get_nested_value(raw_data, 'tags'),
                'duration': self._get_nested_value(raw_data, 'duration'),
                'definition': self._get_nested_value(raw_data, 'definition'),
                'live_broadcast': self._get_nested_value(raw_data, 'live_broadcast')
            }
        elif platform == 'instagram':
            metadata['platform_specific'] = {
                'filter': self._get_nested_value(raw_data, 'filter'),
                'location_id': self._get_nested_value(raw_data, 'location.id'),
                'media_type': self._get_nested_value(raw_data, 'media_type'),
                'product_type': self._get_nested_value(raw_data, 'product_type')
            }
        elif platform == 'tiktok':
            metadata['platform_specific'] = {
                'music': self._get_nested_value(raw_data, 'music'),
                'effects': self._get_nested_value(raw_data, 'effects'),
                'challenges': self._get_nested_value(raw_data, 'challenges'),
                'duet_info': self._get_nested_value(raw_data, 'duet_info')
            }
        elif platform == 'twitter':
            metadata['platform_specific'] = {
                'source': self._get_nested_value(raw_data, 'source'),
                'in_reply_to': self._get_nested_value(raw_data, 'in_reply_to_status_id'),
                'coordinates': self._get_nested_value(raw_data, 'coordinates'),
                'entities': self._get_nested_value(raw_data, 'entities')
            }
            
        return metadata
        
    def _assess_data_quality(self, raw_data: Dict[str, Any]) -> str:
        """
Assess quality of extracted data."""
        required_fields = ['id', 'title', 'author']
        present_fields = sum(1 for field in required_fields if self._get_nested_value(raw_data, field))
        
        if present_fields == len(required_fields):
            return 'high'
        elif present_fields >= len(required_fields) * 0.7:
            return 'medium'
        else:
            return 'low'
            
    def get_supported_platforms(self) -> List[str]:
        """
Get list of supported platforms."""
        return self.supported_platforms
        
    def get_platform_capabilities(self, platform: str) -> Dict[str, bool]:
        """
Get capabilities of specific platform crawler."""
        if platform not in self.crawlers:
            return {}
            
        crawler = self.crawlers[platform]
        
        return {
            'content_extraction': hasattr(crawler, 'extract_content'),
            'profile_extraction': hasattr(crawler, 'extract_profile'),
            'search': hasattr(crawler, 'search_content'),
            'user_content': hasattr(crawler, 'get_user_content'),
            'trending': hasattr(crawler, 'get_trending'),
            'api_support': hasattr(crawler, 'use_api') and crawler.use_api,
            'rate_limited': hasattr(crawler, 'rate_limit') and crawler.rate_limit
        }
