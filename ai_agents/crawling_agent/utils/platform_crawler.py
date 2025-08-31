"""
Advanced Platform Crawler - Multi-Platform Content Harvesting & API Integration

Industrial platform-specific crawling system with API integration, rate limiting,
and intelligent content extraction for major social and content platforms.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️  IMPORTANT LEGAL NOTICE:
This code and concept are the exclusive intellectual property of Fahed Mlaiel.
Any unauthorized use, copying, distribution, or commercialization without explicit written permission is strictly prohibited.
Contact: mlaiel@live.de for licensing inquiries.

Team Specialties:
- Lead AI Developer & Backend Senior Engineer
- Machine Learning Engineer & Audio Processing Specialist  
- Database Administrator & Security Expert
- Microservices Architect & DevOps Engineer
- AI Prompt Engineer & Content Protection Specialist
"""

import asyncio
import logging
import time
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Set, Union, AsyncGenerator
from dataclasses import dataclass, field
from enum import Enum
from urllib.parse import urlencode, urlparse
import re

import aiohttp
import tweepy
from instagram_api import InstagramAPI
import googleapiclient.discovery
from google.oauth2.credentials import Credentials
import facebook
import linkedin_api
import tiktokapi
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import soundcloud
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup

try:
    from core.config import settings
except ImportError:
    # Fallback settings
    settings = type('Settings', (), {'debug': True, 'log_level': 'INFO'})()
try:
    from core.exceptions import PlatformCrawlingError, ValidationError, RateLimitError
except ImportError:
    # Fallback exception classes
    class ValidationError(Exception): pass
    class ConfigurationError(Exception): pass
    class ProcessingError(Exception): pass
    PlatformCrawlingError, ValidationError, RateLimitError = globals().get('PlatformCrawlingError, ValidationError, RateLimitError', Exception)
from ...utils.rate_limiter import AdvancedRateLimiter
from ...utils.proxy_manager import ProxyManager
from ...utils.cache_manager import CacheManager
from ...security.api_key_manager import APIKeyManager
from .web_crawler import WebCrawler

logger = logging.getLogger(__name__)

class PlatformType(Enum):
    """Supported platform types"""
    TWITTER = "twitter"
    INSTAGRAM = "instagram"
    FACEBOOK = "facebook"
    YOUTUBE = "youtube"
    TIKTOK = "tiktok"
    LINKEDIN = "linkedin"
    SPOTIFY = "spotify"
    SOUNDCLOUD = "soundcloud"
    PINTEREST = "pinterest"
    REDDIT = "reddit"
    GITHUB = "github"
    MEDIUM = "medium"
    SUBSTACK = "substack"
    PATREON = "patreon"
    ONLYFANS = "onlyfans"
    TWITCH = "twitch"

class CrawlingMethod(Enum):
    """Platform crawling methods"""
    API = "api"
    WEB_SCRAPING = "web_scraping"
    RSS = "rss"
    WEBHOOK = "webhook"
    HYBRID = "hybrid"

class ContentCategory(Enum):
    """Content categories for filtering"""
    TEXT = "text"
    IMAGE = "image"
    VIDEO = "video"
    AUDIO = "audio"
    STORY = "story"
    LIVE = "live"
    REEL = "reel"
    SHORT = "short"
    POST = "post"
    ARTICLE = "article"
    COMMENT = "comment"

@dataclass
class PlatformConfig:
    """Platform-specific configuration"""
    platform_type: PlatformType
    crawling_method: CrawlingMethod
    api_keys: Dict[str, str] = field(default_factory=dict)
    rate_limits: Dict[str, int] = field(default_factory=dict)
    endpoints: Dict[str, str] = field(default_factory=dict)
    request_headers: Dict[str, str] = field(default_factory=dict)
    authentication: Dict[str, Any] = field(default_factory=dict)
    content_filters: Dict[str, Any] = field(default_factory=dict)
    max_concurrent_requests: int = 5
    enable_caching: bool = True
    cache_ttl_minutes: int = 30

@dataclass
class PlatformContent:
    """Standardized platform content structure"""
    platform: PlatformType
    content_id: str
    content_type: ContentCategory
    
    # Core content
    title: str = ""
    description: str = ""
    content: str = ""
    media_urls: List[str] = field(default_factory=list)
    
    # Author information
    author_id: str = ""
    author_name: str = ""
    author_handle: str = ""
    author_avatar: str = ""
    author_verified: bool = False
    
    # Engagement metrics
    likes: int = 0
    shares: int = 0
    comments: int = 0
    views: int = 0
    saves: int = 0
    
    # Metadata
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    hashtags: List[str] = field(default_factory=list)
    mentions: List[str] = field(default_factory=list)
    location: Dict[str, Any] = field(default_factory=dict)
    language: str = ""
    
    # Platform-specific data
    platform_data: Dict[str, Any] = field(default_factory=dict)
    
    # Technical metadata
    url: str = ""
    extracted_at: datetime = field(default_factory=datetime.now)
    extraction_method: CrawlingMethod = CrawlingMethod.API

class PlatformCrawler:
    """
    Advanced Multi-Platform Content Crawler
    
    Handles crawling and content extraction from major social media and content platforms
    using APIs, web scraping, and hybrid approaches with rate limiting and authentication.
    """
    
    def __init__(self, config: Optional[Dict[str, PlatformConfig]] = None):
        self.platform_configs = config or {}
        
        # Core components
        self.rate_limiters: Dict[str, AdvancedRateLimiter] = {}
        self.proxy_manager = ProxyManager()
        self.cache_manager = CacheManager()
        self.api_key_manager = APIKeyManager()
        self.web_crawler = WebCrawler()
        
        # Platform clients
        self.platform_clients: Dict[PlatformType, Any] = {}
        self.session: Optional[aiohttp.ClientSession] = None
        
        # State management
        self.crawling_stats: Dict[str, Dict] = {}
        self.active_crawls: Set[str] = set()
        
        logger.info("Platform Crawler initialized")

    async def initialize(self) -> None:
        """Initialize platform clients and connections"""
        try:
            # Initialize HTTP session
            connector = aiohttp.TCPConnector(
                limit=100,
                limit_per_host=20,
                ttl_dns_cache=300
            )
            
            self.session = aiohttp.ClientSession(
                connector=connector,
                timeout=aiohttp.ClientTimeout(total=30)
            )
            
            # Initialize platform-specific clients
            await self._initialize_platform_clients()
            
            # Setup rate limiters
            await self._setup_rate_limiters()
            
            # Initialize cache
            await self.cache_manager.initialize()
            
            logger.info("Platform Crawler initialization complete")
            
        except Exception as e:
            logger.error(f"Failed to initialize Platform Crawler: {str(e)}")
            raise PlatformCrawlingError(f"Initialization failed: {str(e)}")

    async def _initialize_platform_clients(self) -> None:
        """Initialize API clients for supported platforms"""
        
        # Twitter API v2
        if PlatformType.TWITTER in self.platform_configs:
            config = self.platform_configs[PlatformType.TWITTER]
            if 'bearer_token' in config.api_keys:
                self.platform_clients[PlatformType.TWITTER] = tweepy.Client(
                    bearer_token=config.api_keys['bearer_token'],
                    wait_on_rate_limit=True
                )
        
        # YouTube Data API
        if PlatformType.YOUTUBE in self.platform_configs:
            config = self.platform_configs[PlatformType.YOUTUBE]
            if 'api_key' in config.api_keys:
                self.platform_clients[PlatformType.YOUTUBE] = googleapiclient.discovery.build(
                    'youtube', 'v3', developerKey=config.api_keys['api_key']
                )
        
        # Spotify API
        if PlatformType.SPOTIFY in self.platform_configs:
            config = self.platform_configs[PlatformType.SPOTIFY]
            if 'client_id' in config.api_keys and 'client_secret' in config.api_keys:
                credentials = SpotifyClientCredentials(
                    client_id=config.api_keys['client_id'],
                    client_secret=config.api_keys['client_secret']
                )
                self.platform_clients[PlatformType.SPOTIFY] = spotipy.Spotify(
                    client_credentials_manager=credentials
                )
        
        # Add other platform clients as needed
        logger.info(f"Initialized {len(self.platform_clients)} platform clients")

    async def _setup_rate_limiters(self) -> None:
        """Setup rate limiters for each platform"""
        for platform_type, config in self.platform_configs.items():
            rate_limits = config.rate_limits
            
            # Default rate limits if not specified
            if not rate_limits:
                rate_limits = self._get_default_rate_limits(platform_type)
            
            self.rate_limiters[platform_type.value] = AdvancedRateLimiter(
                max_requests=rate_limits.get('requests_per_minute', 60),
                window_seconds=60,
                burst_limit=rate_limits.get('burst_limit', 10)
            )

    def _get_default_rate_limits(self, platform: PlatformType) -> Dict[str, int]:
        """Get default rate limits for platforms"""
        defaults = {
            PlatformType.TWITTER: {'requests_per_minute': 300, 'burst_limit': 15},
            PlatformType.INSTAGRAM: {'requests_per_minute': 200, 'burst_limit': 10},
            PlatformType.YOUTUBE: {'requests_per_minute': 100, 'burst_limit': 5},
            PlatformType.SPOTIFY: {'requests_per_minute': 100, 'burst_limit': 10},
            PlatformType.REDDIT: {'requests_per_minute': 60, 'burst_limit': 5}
        }
        return defaults.get(platform, {'requests_per_minute': 60, 'burst_limit': 5})

    async def crawl_platform(self, platform: PlatformType, query: Dict[str, Any],
                           max_results: int = 100) -> List[PlatformContent]:
        """Crawl specific platform for content"""
        crawl_id = f"{platform.value}_{int(time.time())}"
        self.active_crawls.add(crawl_id)
        
        try:
            # Check if platform is configured
            if platform not in self.platform_configs:
                raise ValidationError(f"Platform {platform.value} not configured")
            
            config = self.platform_configs[platform]
            
            # Apply rate limiting
            await self.rate_limiters[platform.value].acquire()
            
            # Choose crawling method
            if config.crawling_method == CrawlingMethod.API:
                results = await self._crawl_via_api(platform, query, max_results)
            elif config.crawling_method == CrawlingMethod.WEB_SCRAPING:
                results = await self._crawl_via_scraping(platform, query, max_results)
            elif config.crawling_method == CrawlingMethod.HYBRID:
                results = await self._crawl_hybrid(platform, query, max_results)
            else:
                results = await self._crawl_via_api(platform, query, max_results)
            
            # Update statistics
            self._update_crawling_stats(platform.value, len(results))
            
            return results
            
        except Exception as e:
            logger.error(f"Platform crawling failed for {platform.value}: {str(e)}")
            raise PlatformCrawlingError(f"Platform crawling failed: {str(e)}")
        
        finally:
            self.active_crawls.discard(crawl_id)

    async def _crawl_via_api(self, platform: PlatformType, query: Dict[str, Any],
                           max_results: int) -> List[PlatformContent]:
        """Crawl platform using official API"""
        if platform == PlatformType.TWITTER:
            return await self._crawl_twitter_api(query, max_results)
        elif platform == PlatformType.YOUTUBE:
            return await self._crawl_youtube_api(query, max_results)
        elif platform == PlatformType.SPOTIFY:
            return await self._crawl_spotify_api(query, max_results)
        elif platform == PlatformType.REDDIT:
            return await self._crawl_reddit_api(query, max_results)
        else:
            logger.warning(f"API crawling not implemented for {platform.value}")
            return []

    async def _crawl_twitter_api(self, query: Dict[str, Any], max_results: int) -> List[PlatformContent]:
        """Crawl Twitter using API v2"""
        results = []
        
        if PlatformType.TWITTER not in self.platform_clients:
            return results
        
        client = self.platform_clients[PlatformType.TWITTER]
        
        try:
            search_query = query.get('query', '')
            tweet_fields = [
                'id', 'text', 'author_id', 'created_at', 'public_metrics',
                'context_annotations', 'entities', 'geo', 'lang', 'reply_settings'
            ]
            user_fields = ['id', 'name', 'username', 'verified', 'profile_image_url']
            expansions = ['author_id', 'attachments.media_keys']
            
            # Search tweets
            tweets = client.search_recent_tweets(
                query=search_query,
                max_results=min(max_results, 100),  # API limit
                tweet_fields=tweet_fields,
                user_fields=user_fields,
                expansions=expansions
            )
            
            if not tweets.data:
                return results
            
            # Process tweets
            users_dict = {user.id: user for user in tweets.includes.get('users', [])}
            
            for tweet in tweets.data:
                author = users_dict.get(tweet.author_id)
                
                content = PlatformContent(
                    platform=PlatformType.TWITTER,
                    content_id=tweet.id,
                    content_type=ContentCategory.POST,
                    title="",
                    description=tweet.text,
                    content=tweet.text,
                    author_id=str(tweet.author_id),
                    author_name=author.name if author else "",
                    author_handle=author.username if author else "",
                    author_verified=author.verified if author else False,
                    likes=tweet.public_metrics.get('like_count', 0),
                    shares=tweet.public_metrics.get('retweet_count', 0),
                    comments=tweet.public_metrics.get('reply_count', 0),
                    created_at=tweet.created_at,
                    hashtags=self._extract_hashtags(tweet.text),
                    mentions=self._extract_mentions(tweet.text),
                    language=tweet.lang or "",
                    url=f"https://twitter.com/{author.username if author else 'user'}/status/{tweet.id}",
                    extraction_method=CrawlingMethod.API,
                    platform_data={
                        'tweet_id': tweet.id,
                        'conversation_id': getattr(tweet, 'conversation_id', ''),
                        'context_annotations': getattr(tweet, 'context_annotations', []),
                        'entities': getattr(tweet, 'entities', {}),
                        'geo': getattr(tweet, 'geo', {}),
                        'reply_settings': getattr(tweet, 'reply_settings', '')
                    }
                )
                
                results.append(content)
                
        except Exception as e:
            logger.error(f"Twitter API crawling failed: {str(e)}")
        
        return results

    async def _crawl_youtube_api(self, query: Dict[str, Any], max_results: int) -> List[PlatformContent]:
        """Crawl YouTube using Data API v3"""
        results = []
        
        if PlatformType.YOUTUBE not in self.platform_clients:
            return results
        
        client = self.platform_clients[PlatformType.YOUTUBE]
        
        try:
            search_query = query.get('query', '')
            search_type = query.get('type', 'video')  # video, channel, playlist
            
            # Search videos
            search_response = client.search().list(
                q=search_query,
                type=search_type,
                part='snippet',
                maxResults=min(max_results, 50),  # API limit
                order='relevance',
                publishedAfter=query.get('published_after'),
                publishedBefore=query.get('published_before'),
                videoDuration=query.get('duration'),
                videoDefinition=query.get('definition')
            ).execute()
            
            # Get video details for statistics
            video_ids = [item['id']['videoId'] for item in search_response['items'] 
                        if item['id']['kind'] == 'youtube#video']
            
            if video_ids:
                videos_response = client.videos().list(
                    part='statistics,contentDetails',
                    id=','.join(video_ids)
                ).execute()
                
                stats_dict = {video['id']: video for video in videos_response['items']}
            else:
                stats_dict = {}
            
            # Process results
            for item in search_response['items']:
                if item['id']['kind'] != 'youtube#video':
                    continue
                
                video_id = item['id']['videoId']
                snippet = item['snippet']
                stats = stats_dict.get(video_id, {}).get('statistics', {})
                
                content = PlatformContent(
                    platform=PlatformType.YOUTUBE,
                    content_id=video_id,
                    content_type=ContentCategory.VIDEO,
                    title=snippet.get('title', ''),
                    description=snippet.get('description', ''),
                    content=snippet.get('description', ''),
                    author_id=snippet.get('channelId', ''),
                    author_name=snippet.get('channelTitle', ''),
                    author_handle=snippet.get('channelTitle', ''),
                    likes=int(stats.get('likeCount', 0)),
                    views=int(stats.get('viewCount', 0)),
                    comments=int(stats.get('commentCount', 0)),
                    created_at=self._parse_youtube_date(snippet.get('publishedAt')),
                    hashtags=self._extract_hashtags(snippet.get('description', '')),
                    language=snippet.get('defaultLanguage', ''),
                    url=f"https://www.youtube.com/watch?v={video_id}",
                    extraction_method=CrawlingMethod.API,
                    platform_data={
                        'channel_id': snippet.get('channelId'),
                        'category_id': snippet.get('categoryId'),
                        'live_broadcast_content': snippet.get('liveBroadcastContent'),
                        'thumbnails': snippet.get('thumbnails', {}),
                        'tags': snippet.get('tags', [])
                    }
                )
                
                # Add thumbnail as media URL
                if 'thumbnails' in snippet and 'high' in snippet['thumbnails']:
                    content.media_urls.append(snippet['thumbnails']['high']['url'])
                
                results.append(content)
                
        except Exception as e:
            logger.error(f"YouTube API crawling failed: {str(e)}")
        
        return results

    async def _crawl_spotify_api(self, query: Dict[str, Any], max_results: int) -> List[PlatformContent]:
        """Crawl Spotify using Web API"""
        results = []
        
        if PlatformType.SPOTIFY not in self.platform_clients:
            return results
        
        client = self.platform_clients[PlatformType.SPOTIFY]
        
        try:
            search_query = query.get('query', '')
            search_types = query.get('types', ['track'])  # track, album, artist, playlist
            market = query.get('market', 'US')
            
            for search_type in search_types:
                search_results = client.search(
                    q=search_query,
                    limit=min(max_results, 50),  # API limit per type
                    type=search_type,
                    market=market
                )
                
                items_key = f"{search_type}s"
                if items_key not in search_results:
                    continue
                
                for item in search_results[items_key]['items']:
                    if search_type == 'track':
                        content = self._process_spotify_track(item)
                    elif search_type == 'album':
                        content = self._process_spotify_album(item)
                    elif search_type == 'artist':
                        content = self._process_spotify_artist(item)
                    elif search_type == 'playlist':
                        content = self._process_spotify_playlist(item)
                    else:
                        continue
                    
                    if content:
                        results.append(content)
                        
        except Exception as e:
            logger.error(f"Spotify API crawling failed: {str(e)}")
        
        return results

    def _process_spotify_track(self, track: Dict) -> PlatformContent:
        """Process Spotify track data"""
        artists = [artist['name'] for artist in track.get('artists', [])]
        
        return PlatformContent(
            platform=PlatformType.SPOTIFY,
            content_id=track['id'],
            content_type=ContentCategory.AUDIO,
            title=track.get('name', ''),
            description=f"Track by {', '.join(artists)}",
            content=track.get('name', ''),
            author_id=track['artists'][0]['id'] if track.get('artists') else '',
            author_name=', '.join(artists),
            author_handle=artists[0] if artists else '',
            views=track.get('popularity', 0),
            url=track.get('external_urls', {}).get('spotify', ''),
            extraction_method=CrawlingMethod.API,
            platform_data={
                'album': track.get('album', {}),
                'artists': track.get('artists', []),
                'duration_ms': track.get('duration_ms', 0),
                'explicit': track.get('explicit', False),
                'popularity': track.get('popularity', 0),
                'preview_url': track.get('preview_url'),
                'track_number': track.get('track_number', 0),
                'disc_number': track.get('disc_number', 0)
            }
        )

    def _process_spotify_album(self, album: Dict) -> PlatformContent:
        """Process Spotify album data"""
        artists = [artist['name'] for artist in album.get('artists', [])]
        
        return PlatformContent(
            platform=PlatformType.SPOTIFY,
            content_id=album['id'],
            content_type=ContentCategory.AUDIO,
            title=album.get('name', ''),
            description=f"Album by {', '.join(artists)}",
            content=album.get('name', ''),
            author_id=album['artists'][0]['id'] if album.get('artists') else '',
            author_name=', '.join(artists),
            author_handle=artists[0] if artists else '',
            url=album.get('external_urls', {}).get('spotify', ''),
            extraction_method=CrawlingMethod.API,
            platform_data={
                'album_type': album.get('album_type'),
                'artists': album.get('artists', []),
                'total_tracks': album.get('total_tracks', 0),
                'release_date': album.get('release_date'),
                'release_date_precision': album.get('release_date_precision'),
                'genres': album.get('genres', []),
                'images': album.get('images', [])
            }
        )

    def _process_spotify_artist(self, artist: Dict) -> PlatformContent:
        """Process Spotify artist data"""
        return PlatformContent(
            platform=PlatformType.SPOTIFY,
            content_id=artist['id'],
            content_type=ContentCategory.TEXT,
            title=artist.get('name', ''),
            description=f"Artist with {artist.get('followers', {}).get('total', 0)} followers",
            content=artist.get('name', ''),
            author_id=artist['id'],
            author_name=artist.get('name', ''),
            author_handle=artist.get('name', ''),
            views=artist.get('popularity', 0),
            url=artist.get('external_urls', {}).get('spotify', ''),
            extraction_method=CrawlingMethod.API,
            platform_data={
                'followers': artist.get('followers', {}),
                'genres': artist.get('genres', []),
                'images': artist.get('images', []),
                'popularity': artist.get('popularity', 0)
            }
        )

    def _process_spotify_playlist(self, playlist: Dict) -> PlatformContent:
        """Process Spotify playlist data"""
        return PlatformContent(
            platform=PlatformType.SPOTIFY,
            content_id=playlist['id'],
            content_type=ContentCategory.TEXT,
            title=playlist.get('name', ''),
            description=playlist.get('description', ''),
            content=playlist.get('description', ''),
            author_id=playlist.get('owner', {}).get('id', ''),
            author_name=playlist.get('owner', {}).get('display_name', ''),
            author_handle=playlist.get('owner', {}).get('display_name', ''),
            url=playlist.get('external_urls', {}).get('spotify', ''),
            extraction_method=CrawlingMethod.API,
            platform_data={
                'collaborative': playlist.get('collaborative', False),
                'followers': playlist.get('followers', {}),
                'images': playlist.get('images', []),
                'owner': playlist.get('owner', {}),
                'public': playlist.get('public'),
                'tracks': playlist.get('tracks', {}),
                'snapshot_id': playlist.get('snapshot_id')
            }
        )

    async def _crawl_reddit_api(self, query: Dict[str, Any], max_results: int) -> List[PlatformContent]:
        """Crawl Reddit using API (through web scraping due to API restrictions)"""
        results = []
        
        try:
            subreddit = query.get('subreddit', 'all')
            search_query = query.get('query', '')
            sort = query.get('sort', 'hot')  # hot, new, top, rising
            
            # Build Reddit URL
            if search_query:
                url = f"https://www.reddit.com/r/{subreddit}/search.json"
                params = {
                    'q': search_query,
                    'sort': sort,
                    'limit': min(max_results, 100),
                    'restrict_sr': '1'
                }
            else:
                url = f"https://www.reddit.com/r/{subreddit}/{sort}.json"
                params = {
                    'limit': min(max_results, 100)
                }
            
            headers = {
                'User-Agent': 'IA-Influencer-Agent/1.0 Content Crawler'
            }
            
            async with self.session.get(url, params=params, headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    for post_data in data.get('data', {}).get('children', []):
                        post = post_data.get('data', {})
                        
                        content = PlatformContent(
                            platform=PlatformType.REDDIT,
                            content_id=post.get('id', ''),
                            content_type=ContentCategory.POST,
                            title=post.get('title', ''),
                            description=post.get('selftext', ''),
                            content=post.get('selftext', ''),
                            author_id=post.get('author', ''),
                            author_name=post.get('author', ''),
                            author_handle=f"u/{post.get('author', '')}",
                            likes=post.get('ups', 0),
                            comments=post.get('num_comments', 0),
                            created_at=datetime.fromtimestamp(post.get('created_utc', 0)),
                            url=f"https://reddit.com{post.get('permalink', '')}",
                            extraction_method=CrawlingMethod.API,
                            platform_data={
                                'subreddit': post.get('subreddit'),
                                'subreddit_subscribers': post.get('subreddit_subscribers'),
                                'score': post.get('score', 0),
                                'upvote_ratio': post.get('upvote_ratio', 0),
                                'gilded': post.get('gilded', 0),
                                'stickied': post.get('stickied', False),
                                'over_18': post.get('over_18', False),
                                'spoiler': post.get('spoiler', False),
                                'flair_text': post.get('link_flair_text'),
                                'post_hint': post.get('post_hint')
                            }
                        )
                        
                        # Add media URLs if available
                        if post.get('url') and self._is_media_url(post['url']):
                            content.media_urls.append(post['url'])
                        
                        results.append(content)
                        
        except Exception as e:
            logger.error(f"Reddit API crawling failed: {str(e)}")
        
        return results

    async def _crawl_via_scraping(self, platform: PlatformType, query: Dict[str, Any],
                                max_results: int) -> List[PlatformContent]:
        """Crawl platform using web scraping"""
        if platform == PlatformType.INSTAGRAM:
            return await self._crawl_instagram_scraping(query, max_results)
        elif platform == PlatformType.TIKTOK:
            return await self._crawl_tiktok_scraping(query, max_results)
        elif platform == PlatformType.LINKEDIN:
            return await self._crawl_linkedin_scraping(query, max_results)
        else:
            logger.warning(f"Web scraping not implemented for {platform.value}")
            return []

    async def _crawl_instagram_scraping(self, query: Dict[str, Any], max_results: int) -> List[PlatformContent]:
        """Crawl Instagram using web scraping"""
        results = []
        
        # Note: Instagram heavily restricts scraping. This is a simplified example.
        # In production, use official API or respect robots.txt
        
        try:
            hashtag = query.get('hashtag', '')
            username = query.get('username', '')
            
            if hashtag:
                url = f"https://www.instagram.com/explore/tags/{hashtag.lstrip('#')}/"
            elif username:
                url = f"https://www.instagram.com/{username}/"
            else:
                return results
            
            # Use web crawler for scraping
            crawl_result = await self.web_crawler.crawl_url(url, require_js=True)
            
            if not crawl_result or crawl_result.status_code != 200:
                return results
            
            # Parse Instagram content (simplified)
            soup = BeautifulSoup(crawl_result.html, 'html.parser')
            
            # Extract posts (this is highly simplified and may not work due to Instagram's dynamic loading)
            # In practice, would need more sophisticated approach
            
        except Exception as e:
            logger.error(f"Instagram scraping failed: {str(e)}")
        
        return results

    async def _crawl_tiktok_scraping(self, query: Dict[str, Any], max_results: int) -> List[PlatformContent]:
        """Crawl TikTok using web scraping"""
        results = []
        
        try:
            hashtag = query.get('hashtag', '')
            username = query.get('username', '')
            
            if hashtag:
                url = f"https://www.tiktok.com/tag/{hashtag.lstrip('#')}"
            elif username:
                url = f"https://www.tiktok.com/@{username}"
            else:
                return results
            
            # Use web crawler with JavaScript support
            crawl_result = await self.web_crawler.crawl_url(url, require_js=True, js_wait_time=3)
            
            if not crawl_result or crawl_result.status_code != 200:
                return results
            
            # Parse TikTok content (simplified)
            # Note: TikTok heavily relies on JavaScript and has anti-scraping measures
            
        except Exception as e:
            logger.error(f"TikTok scraping failed: {str(e)}")
        
        return results

    async def _crawl_linkedin_scraping(self, query: Dict[str, Any], max_results: int) -> List[PlatformContent]:
        """Crawl LinkedIn using web scraping"""
        results = []
        
        try:
            # LinkedIn requires authentication for most content
            # This is a placeholder implementation
            search_query = query.get('query', '')
            
            if not search_query:
                return results
            
            # Note: LinkedIn has strict anti-scraping policies
            # Consider using their official API instead
            
        except Exception as e:
            logger.error(f"LinkedIn scraping failed: {str(e)}")
        
        return results

    async def _crawl_hybrid(self, platform: PlatformType, query: Dict[str, Any],
                          max_results: int) -> List[PlatformContent]:
        """Use hybrid approach combining API and scraping"""
        api_results = await self._crawl_via_api(platform, query, max_results // 2)
        scraping_results = await self._crawl_via_scraping(platform, query, max_results // 2)
        
        # Combine and deduplicate results
        all_results = api_results + scraping_results
        seen_ids = set()
        unique_results = []
        
        for result in all_results:
            if result.content_id not in seen_ids:
                seen_ids.add(result.content_id)
                unique_results.append(result)
        
        return unique_results[:max_results]

    def _extract_hashtags(self, text: str) -> List[str]:
        """Extract hashtags from text"""
        hashtag_pattern = r'#\w+'
        hashtags = re.findall(hashtag_pattern, text, re.IGNORECASE)
        return [tag[1:] for tag in hashtags]  # Remove # symbol

    def _extract_mentions(self, text: str) -> List[str]:
        """Extract mentions from text"""
        mention_pattern = r'@\w+'
        mentions = re.findall(mention_pattern, text, re.IGNORECASE)
        return [mention[1:] for mention in mentions]  # Remove @ symbol

    def _parse_youtube_date(self, date_string: str) -> Optional[datetime]:
        """Parse YouTube API date format"""
        if not date_string:
            return None
        
        try:
            return datetime.fromisoformat(date_string.replace('Z', '+00:00'))
        except:
            return None

    def _is_media_url(self, url: str) -> bool:
        """Check if URL points to media content"""
        media_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.mp4', '.webm', '.mp3', '.wav']
        return any(url.lower().endswith(ext) for ext in media_extensions)

    def _update_crawling_stats(self, platform: str, results_count: int) -> None:
        """Update crawling statistics"""
        if platform not in self.crawling_stats:
            self.crawling_stats[platform] = {
                'total_requests': 0,
                'total_results': 0,
                'last_crawl': None,
                'average_results_per_request': 0
            }
        
        stats = self.crawling_stats[platform]
        stats['total_requests'] += 1
        stats['total_results'] += results_count
        stats['last_crawl'] = datetime.now()
        stats['average_results_per_request'] = stats['total_results'] / stats['total_requests']

    async def get_user_content(self, platform: PlatformType, user_id: str,
                             content_types: List[ContentCategory] = None,
                             max_results: int = 50) -> List[PlatformContent]:
        """Get content from specific user across platforms"""
        query = {
            'user_id': user_id,
            'username': user_id,
            'content_types': content_types or [ContentCategory.POST]
        }
        
        return await self.crawl_platform(platform, query, max_results)

    async def search_hashtag(self, platform: PlatformType, hashtag: str,
                           max_results: int = 100) -> List[PlatformContent]:
        """Search for content by hashtag"""
        query = {
            'hashtag': hashtag,
            'query': f"#{hashtag.lstrip('#')}"
        }
        
        return await self.crawl_platform(platform, query, max_results)

    async def search_keywords(self, platform: PlatformType, keywords: List[str],
                            max_results: int = 100) -> List[PlatformContent]:
        """Search for content by keywords"""
        query = {
            'query': ' '.join(keywords),
            'keywords': keywords
        }
        
        return await self.crawl_platform(platform, query, max_results)

    async def monitor_user(self, platform: PlatformType, user_id: str,
                         check_interval_minutes: int = 60) -> str:
        """Setup monitoring for specific user"""
        monitor_id = f"{platform.value}_{user_id}_{int(time.time())}"
        
        # This would typically involve setting up a background task
        # For now, return the monitor ID
        
        logger.info(f"Set up monitoring for {user_id} on {platform.value} (ID: {monitor_id})")
        return monitor_id

    def get_platform_statistics(self) -> Dict[str, Dict]:
        """Get crawling statistics for all platforms"""
        return self.crawling_stats.copy()

    def get_active_crawls(self) -> List[str]:
        """Get list of active crawl IDs"""
        return list(self.active_crawls)

    async def cleanup(self) -> None:
        """Clean up resources"""
        if self.session:
            await self.session.close()
        
        await self.cache_manager.cleanup()
        logger.info("Platform Crawler cleanup complete")


class APIHarvester:
    """
    Specialized API Content Harvester
    
    Focused on efficient bulk content harvesting using official APIs
    with advanced rate limiting, caching, and data enrichment.
    """
    
    def __init__(self, platform_crawler: PlatformCrawler):
        self.platform_crawler = platform_crawler
        self.harvest_queue: asyncio.Queue = asyncio.Queue()
        self.harvest_results: Dict[str, List[PlatformContent]] = {}
        self.active_harvests: Set[str] = set()
        
    async def schedule_harvest(self, platform: PlatformType, harvest_config: Dict[str, Any]) -> str:
        """Schedule content harvest operation"""
        harvest_id = f"harvest_{platform.value}_{int(time.time())}"
        
        harvest_task = {
            'harvest_id': harvest_id,
            'platform': platform,
            'config': harvest_config,
            'scheduled_at': datetime.now(),
            'status': 'scheduled'
        }
        
        await self.harvest_queue.put(harvest_task)
        return harvest_id
    
    async def execute_harvest(self, harvest_id: str) -> List[PlatformContent]:
        """Execute scheduled harvest"""
        if harvest_id in self.harvest_results:
            return self.harvest_results[harvest_id]
        
        # Implementation would execute the harvest based on stored config
        # This is a placeholder
        return []
    
    async def bulk_user_harvest(self, platform: PlatformType, user_ids: List[str],
                              max_content_per_user: int = 50) -> Dict[str, List[PlatformContent]]:
        """Harvest content from multiple users efficiently"""
        results = {}
        
        for user_id in user_ids:
            try:
                user_content = await self.platform_crawler.get_user_content(
                    platform, user_id, max_results=max_content_per_user
                )
                results[user_id] = user_content
                
                # Rate limiting between users
                await asyncio.sleep(1)
                
            except Exception as e:
                logger.error(f"Failed to harvest content for user {user_id}: {str(e)}")
                results[user_id] = []
        
        return results
    
    async def trending_content_harvest(self, platforms: List[PlatformType],
                                     max_results_per_platform: int = 100) -> Dict[str, List[PlatformContent]]:
        """Harvest trending content across multiple platforms"""
        results = {}
        
        for platform in platforms:
            try:
                # Platform-specific trending queries
                if platform == PlatformType.TWITTER:
                    query = {'query': 'trending OR viral', 'result_type': 'popular'}
                elif platform == PlatformType.YOUTUBE:
                    query = {'chart': 'mostPopular', 'type': 'video'}
                elif platform == PlatformType.REDDIT:
                    query = {'subreddit': 'all', 'sort': 'hot'}
                else:
                    query = {'query': 'trending'}
                
                trending_content = await self.platform_crawler.crawl_platform(
                    platform, query, max_results_per_platform
                )
                results[platform.value] = trending_content
                
            except Exception as e:
                logger.error(f"Failed to harvest trending content from {platform.value}: {str(e)}")
                results[platform.value] = []
        
        return results
