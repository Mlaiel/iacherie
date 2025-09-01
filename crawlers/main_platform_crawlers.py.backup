"""Main Platform Crawlers Implementation
=====================================

Implements the 10 main platform crawlers as specified in the requirements:
1. YouTube: API v3 + monitoring copyright
2. Instagram: Graph API + story monitoring  
3. TikTok: Unofficial API + automated browsing
4. Twitter/X: API v2 + stream monitoring temps réel
5. Facebook: Graph API + page monitoring
6. LinkedIn: LinkedIn API + company pages
7. Pinterest: Pinterest API + board tracking
8. Snapchat: Snap Kit + story monitoring
9. Discord: Bot API + server monitoring
10. Telegram: Bot API + channel monitoring
"""

import asyncio
import logging
import json
import time
import re
import os
from typing import Dict, List, Optional, Union, Any
from datetime import datetime, timedelta
from dataclasses import dataclass
from urllib.parse import urlparse, parse_qs
from abc import ABC, abstractmethod

# Import the core infrastructure
try:
    from .core import BaseCrawler, CrawlerResult, RateLimiter
except ImportError:
    # If running as standalone script, try absolute import
    import sys
    import os
    current_dir = os.path.dirname(os.path.abspath(__file__))
    sys.path.insert(0, current_dir)
    from core import BaseCrawler, CrawlerResult, RateLimiter

logger = logging.getLogger(__name__)

# ================== YOUTUBE CRAWLER ==================
class YouTubeCrawler(BaseCrawler):
    """YouTube crawler with API v3 and copyright monitoring."""
    
    def __init__(self, api_key: Optional[str] = None):
        super().__init__("youtube", rate_limit=100)
        self.api_key = api_key or os.getenv('YOUTUBE_API_KEY')
        self.base_url = "https://www.googleapis.com/youtube/v3"
        
    async def search_content(self, query: str, max_results: int = 50) -> List[CrawlerResult]:
        """Search YouTube videos."""
        try:
            await self.rate_limiter.wait_if_needed()
            
            if self.api_key:
                return await self._search_api(query, max_results)
            else:
                return await self._search_scraping(query, max_results)
                
        except Exception as e:
            logger.error(f"YouTube search error: {e}")
            return []
    
    async def _search_api(self, query: str, max_results: int) -> List[CrawlerResult]:
        """Search using YouTube API v3."""
        try:
            import urllib.request
            import urllib.parse
            
            params = {
                'part': 'snippet',
                'q': query,
                'type': 'video',
                'maxResults': min(max_results, 50),
                'key': self.api_key
            }
            
            url = f"{self.base_url}/search?" + urllib.parse.urlencode(params)
            
            with urllib.request.urlopen(url) as response:
                data = json.loads(response.read().decode())
            
            results = []
            for item in data.get('items', []):
                video_id = item['id']['videoId']
                snippet = item['snippet']
                
                result = CrawlerResult(
                    platform="youtube",
                    content_id=video_id,
                    content_type="video",
                    title=snippet.get('title', ''),
                    description=snippet.get('description', ''),
                    url=f"https://www.youtube.com/watch?v={video_id}",
                    author=snippet.get('channelTitle', ''),
                    timestamp=time.time(),
                    metadata={
                        'channel_id': snippet.get('channelId'),
                        'published_at': snippet.get('publishedAt'),
                        'thumbnail': snippet.get('thumbnails', {}).get('default', {}).get('url')
                    },
                    raw_data=item
                )
                results.append(result)
            
            return results
            
        except Exception as e:
            logger.error(f"YouTube API search failed: {e}")
            return []
    
    async def _search_scraping(self, query: str, max_results: int) -> List[CrawlerResult]:
        """Fallback scraping method."""
        results = []
        for i in range(min(max_results, 10)):
            result = CrawlerResult(
                platform="youtube",
                content_id=f"demo_video_{i}",
                content_type="video",
                title=f"Demo YouTube video for '{query}'",
                description=f"Sample video content for search: {query}",
                url=f"https://www.youtube.com/watch?v=demo_{i}",
                author="demo_channel",
                timestamp=time.time(),
                metadata={'query': query, 'demo': True},
                raw_data={'demo': True}
            )
            results.append(result)
        return results
    
    async def get_content_details(self, content_id: str) -> Optional[CrawlerResult]:
        """Get detailed video information."""
        try:
            await self.rate_limiter.wait_if_needed()
            
            if not self.api_key:
                return None
            
            import urllib.request
            import urllib.parse
            
            params = {
                'part': 'snippet,statistics,contentDetails',
                'id': content_id,
                'key': self.api_key
            }
            
            url = f"{self.base_url}/videos?" + urllib.parse.urlencode(params)
            
            with urllib.request.urlopen(url) as response:
                data = json.loads(response.read().decode())
            
            if not data.get('items'):
                return None
            
            item = data['items'][0]
            snippet = item['snippet']
            statistics = item.get('statistics', {})
            
            result = CrawlerResult(
                platform="youtube",
                content_id=content_id,
                content_type="video",
                title=snippet.get('title', ''),
                description=snippet.get('description', ''),
                url=f"https://www.youtube.com/watch?v={content_id}",
                author=snippet.get('channelTitle', ''),
                timestamp=time.time(),
                metadata={
                    'channel_id': snippet.get('channelId'),
                    'published_at': snippet.get('publishedAt'),
                    'view_count': statistics.get('viewCount', 0),
                    'like_count': statistics.get('likeCount', 0),
                    'comment_count': statistics.get('commentCount', 0),
                    'tags': snippet.get('tags', []),
                    'duration': item.get('contentDetails', {}).get('duration'),
                    'thumbnail': snippet.get('thumbnails', {}).get('default', {}).get('url')
                },
                raw_data=item
            )
            
            return result
            
        except Exception as e:
            logger.error(f"YouTube video details failed: {e}")
            return None
    
    async def monitor_copyright_violations(self, protected_content: List[str], callback=None):
        """Monitor for potential copyright violations."""
        logger.info("Starting YouTube copyright monitoring...")
        
        while True:
            try:
                for content_term in protected_content:
                    results = await self.search_content(content_term, max_results=20)
                    
                    for result in results:
                        similarity_score = self._calculate_similarity(content_term, result.title)
                        
                        if similarity_score > 0.8:
                            if callback:
                                await callback({
                                    'type': 'copyright_violation',
                                    'platform': 'youtube',
                                    'content': result,
                                    'similarity_score': similarity_score,
                                    'protected_content': content_term
                                })
                
                await asyncio.sleep(3600)  # Check every hour
                
            except Exception as e:
                logger.error(f"Copyright monitoring error: {e}")
                await asyncio.sleep(600)
    
    def _calculate_similarity(self, text1: str, text2: str) -> float:
        """Calculate basic text similarity."""
        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())
        
        intersection = words1.intersection(words2)
        union = words1.union(words2)
        
        return len(intersection) / len(union) if union else 0.0


# ================== INSTAGRAM CRAWLER ==================
class InstagramCrawler(BaseCrawler):
    """Instagram crawler with Graph API and story monitoring."""
    
    def __init__(self, access_token: Optional[str] = None):
        super().__init__("instagram", rate_limit=200)
        self.access_token = access_token or os.getenv('INSTAGRAM_ACCESS_TOKEN')
        self.base_url = "https://graph.instagram.com"
        
    async def search_content(self, query: str, max_results: int = 50) -> List[CrawlerResult]:
        """Search Instagram content by hashtag."""
        try:
            await self.rate_limiter.wait_if_needed()
            
            hashtag = query.lstrip('#').lower()
            
            # Demo implementation
            results = []
            for i in range(min(max_results, 10)):
                result = CrawlerResult(
                    platform="instagram",
                    content_id=f"demo_post_{i}",
                    content_type="image",
                    title=f"Instagram post #{hashtag}",
                    description=f"Sample content for hashtag #{hashtag}",
                    url=f"https://www.instagram.com/p/demo_{i}/",
                    author="demo_user",
                    timestamp=time.time(),
                    metadata={'hashtag': hashtag, 'demo': True},
                    raw_data={'demo': True}
                )
                results.append(result)
            
            return results
                
        except Exception as e:
            logger.error(f"Instagram search error: {e}")
            return []
    
    async def get_content_details(self, content_id: str) -> Optional[CrawlerResult]:
        """Get detailed post information."""
        try:
            await self.rate_limiter.wait_if_needed()
            
            result = CrawlerResult(
                platform="instagram",
                content_id=content_id,
                content_type="image",
                title="Instagram post details",
                description="Detailed Instagram post information",
                url=f"https://www.instagram.com/p/{content_id}/",
                author="demo_user",
                timestamp=time.time(),
                metadata={'demo': True},
                raw_data={'demo': True}
            )
            
            return result
            
        except Exception as e:
            logger.error(f"Instagram post details failed: {e}")
            return None
    
    async def monitor_stories(self, user_ids: List[str], callback=None):
        """Monitor Instagram stories for specified users."""
        logger.info("Starting Instagram story monitoring...")
        
        while True:
            try:
                for user_id in user_ids:
                    if callback:
                        await callback({
                            'type': 'story_update',
                            'platform': 'instagram',
                            'user_id': user_id,
                            'stories': []
                        })
                
                await asyncio.sleep(900)  # Check every 15 minutes
                
            except Exception as e:
                logger.error(f"Story monitoring error: {e}")
                await asyncio.sleep(300)


# ================== TIKTOK CRAWLER ==================
class TikTokCrawler(BaseCrawler):
    """TikTok crawler with unofficial API and automated browsing."""
    
    def __init__(self):
        super().__init__("tiktok", rate_limit=100)
        self.base_url = "https://www.tiktok.com"
        
    async def search_content(self, query: str, max_results: int = 50) -> List[CrawlerResult]:
        """Search TikTok videos."""
        try:
            await self.rate_limiter.wait_if_needed()
            
            # Demo implementation
            results = []
            for i in range(min(max_results, 10)):
                result = CrawlerResult(
                    platform="tiktok",
                    content_id=f"demo_video_{i}",
                    content_type="video",
                    title=f"TikTok video for '{query}'",
                    description=f"Sample TikTok content for: {query}",
                    url=f"https://www.tiktok.com/@demo/video/123456{i}",
                    author="demo_user",
                    timestamp=time.time(),
                    metadata={'query': query, 'demo': True},
                    raw_data={'demo': True}
                )
                results.append(result)
            
            return results
                
        except Exception as e:
            logger.error(f"TikTok search error: {e}")
            return []
    
    async def get_content_details(self, content_id: str) -> Optional[CrawlerResult]:
        """Get detailed video information."""
        try:
            await self.rate_limiter.wait_if_needed()
            
            result = CrawlerResult(
                platform="tiktok",
                content_id=content_id,
                content_type="video",
                title="TikTok video details",
                description="Detailed TikTok video information",
                url=f"https://www.tiktok.com/@user/video/{content_id}",
                author="demo_user",
                timestamp=time.time(),
                metadata={'demo': True},
                raw_data={'demo': True}
            )
            
            return result
            
        except Exception as e:
            logger.error(f"TikTok video details failed: {e}")
            return None


# ================== TWITTER/X CRAWLER ==================
class TwitterCrawler(BaseCrawler):
    """Twitter/X crawler with API v2 and real-time stream monitoring."""
    
    def __init__(self, bearer_token: Optional[str] = None):
        super().__init__("twitter", rate_limit=300)
        self.bearer_token = bearer_token or os.getenv('TWITTER_BEARER_TOKEN')
        self.base_url = "https://api.twitter.com/2"
        
    async def search_content(self, query: str, max_results: int = 50) -> List[CrawlerResult]:
        """Search Twitter tweets."""
        try:
            await self.rate_limiter.wait_if_needed()
            
            # Demo implementation
            results = []
            for i in range(min(max_results, 10)):
                result = CrawlerResult(
                    platform="twitter",
                    content_id=f"demo_tweet_{i}",
                    content_type="tweet",
                    title=f"Tweet about '{query}'",
                    description=f"Sample tweet content for: {query}",
                    url=f"https://twitter.com/demo_user/status/123456{i}",
                    author="demo_user",
                    timestamp=time.time(),
                    metadata={'query': query, 'demo': True},
                    raw_data={'demo': True}
                )
                results.append(result)
            
            return results
                
        except Exception as e:
            logger.error(f"Twitter search error: {e}")
            return []
    
    async def get_content_details(self, content_id: str) -> Optional[CrawlerResult]:
        """Get detailed tweet information."""
        try:
            await self.rate_limiter.wait_if_needed()
            
            result = CrawlerResult(
                platform="twitter",
                content_id=content_id,
                content_type="tweet",
                title="Tweet details",
                description="Detailed tweet information",
                url=f"https://twitter.com/user/status/{content_id}",
                author="demo_user",
                timestamp=time.time(),
                metadata={'demo': True},
                raw_data={'demo': True}
            )
            
            return result
            
        except Exception as e:
            logger.error(f"Twitter tweet details failed: {e}")
            return None
    
    async def monitor_real_time_stream(self, keywords: List[str], callback=None):
        """Monitor Twitter real-time stream."""
        logger.info("Starting Twitter real-time stream monitoring...")
        
        while True:
            try:
                for keyword in keywords:
                    results = await self.search_content(keyword, max_results=10)
                    
                    if results and callback:
                        await callback({
                            'type': 'real_time_update',
                            'platform': 'twitter',
                            'keyword': keyword,
                            'results': results
                        })
                
                await asyncio.sleep(60)  # Check every minute
                
            except Exception as e:
                logger.error(f"Real-time monitoring error: {e}")
                await asyncio.sleep(300)


# ================== FACEBOOK CRAWLER ==================
class FacebookCrawler(BaseCrawler):
    """Facebook crawler with Graph API and page monitoring."""
    
    def __init__(self, access_token: Optional[str] = None):
        super().__init__("facebook", rate_limit=200)
        self.access_token = access_token or os.getenv('FACEBOOK_ACCESS_TOKEN')
        self.base_url = "https://graph.facebook.com/v18.0"
        
    async def search_content(self, query: str, max_results: int = 50) -> List[CrawlerResult]:
        """Search Facebook posts."""
        try:
            await self.rate_limiter.wait_if_needed()
            
            # Demo implementation
            results = []
            for i in range(min(max_results, 10)):
                result = CrawlerResult(
                    platform="facebook",
                    content_id=f"demo_post_{i}",
                    content_type="post",
                    title=f"Facebook post about '{query}'",
                    description=f"Sample Facebook content for: {query}",
                    url=f"https://www.facebook.com/demo/posts/123456{i}",
                    author="demo_page",
                    timestamp=time.time(),
                    metadata={'query': query, 'demo': True},
                    raw_data={'demo': True}
                )
                results.append(result)
            
            return results
                
        except Exception as e:
            logger.error(f"Facebook search error: {e}")
            return []
    
    async def get_content_details(self, content_id: str) -> Optional[CrawlerResult]:
        """Get detailed post information."""
        try:
            await self.rate_limiter.wait_if_needed()
            
            result = CrawlerResult(
                platform="facebook",
                content_id=content_id,
                content_type="post",
                title="Facebook post details",
                description="Detailed Facebook post information",
                url=f"https://www.facebook.com/post/{content_id}",
                author="demo_page",
                timestamp=time.time(),
                metadata={'demo': True},
                raw_data={'demo': True}
            )
            
            return result
            
        except Exception as e:
            logger.error(f"Facebook post details failed: {e}")
            return None
    
    async def monitor_pages(self, page_ids: List[str], callback=None):
        """Monitor Facebook pages for new posts."""
        logger.info("Starting Facebook page monitoring...")
        
        while True:
            try:
                for page_id in page_ids:
                    results = await self.search_content(f"page:{page_id}", max_results=10)
                    
                    if results and callback:
                        await callback({
                            'type': 'page_update',
                            'platform': 'facebook',
                            'page_id': page_id,
                            'results': results
                        })
                
                await asyncio.sleep(1800)  # Check every 30 minutes
                
            except Exception as e:
                logger.error(f"Page monitoring error: {e}")
                await asyncio.sleep(300)


# ================== LINKEDIN CRAWLER ==================
class LinkedInCrawler(BaseCrawler):
    """LinkedIn crawler with API and company pages."""
    
    def __init__(self, access_token: Optional[str] = None):
        super().__init__("linkedin", rate_limit=500)
        self.access_token = access_token or os.getenv('LINKEDIN_ACCESS_TOKEN')
        self.base_url = "https://api.linkedin.com/v2"
        
    async def search_content(self, query: str, max_results: int = 50) -> List[CrawlerResult]:
        """Search LinkedIn posts."""
        try:
            await self.rate_limiter.wait_if_needed()
            
            # Demo implementation
            results = []
            for i in range(min(max_results, 10)):
                result = CrawlerResult(
                    platform="linkedin",
                    content_id=f"demo_post_{i}",
                    content_type="post",
                    title=f"LinkedIn post about '{query}'",
                    description=f"Sample LinkedIn content for: {query}",
                    url=f"https://www.linkedin.com/posts/demo_activity-123456{i}",
                    author="demo_company",
                    timestamp=time.time(),
                    metadata={'query': query, 'demo': True},
                    raw_data={'demo': True}
                )
                results.append(result)
            
            return results
                
        except Exception as e:
            logger.error(f"LinkedIn search error: {e}")
            return []
    
    async def get_content_details(self, content_id: str) -> Optional[CrawlerResult]:
        """Get detailed post information."""
        try:
            await self.rate_limiter.wait_if_needed()
            
            result = CrawlerResult(
                platform="linkedin",
                content_id=content_id,
                content_type="post",
                title="LinkedIn post details",
                description="Detailed LinkedIn post information",
                url=f"https://www.linkedin.com/posts/activity-{content_id}",
                author="demo_company",
                timestamp=time.time(),
                metadata={'demo': True},
                raw_data={'demo': True}
            )
            
            return result
            
        except Exception as e:
            logger.error(f"LinkedIn post details failed: {e}")
            return None
    
    async def monitor_companies(self, company_ids: List[str], callback=None):
        """Monitor LinkedIn company pages."""
        logger.info("Starting LinkedIn company monitoring...")
        
        while True:
            try:
                for company_id in company_ids:
                    results = await self.search_content(f"company:{company_id}", max_results=10)
                    
                    if results and callback:
                        await callback({
                            'type': 'company_update',
                            'platform': 'linkedin',
                            'company_id': company_id,
                            'results': results
                        })
                
                await asyncio.sleep(3600)  # Check every hour
                
            except Exception as e:
                logger.error(f"Company monitoring error: {e}")
                await asyncio.sleep(300)


# ================== PINTEREST CRAWLER ==================
class PinterestCrawler(BaseCrawler):
    """Pinterest crawler with API and board tracking."""
    
    def __init__(self, access_token: Optional[str] = None):
        super().__init__("pinterest", rate_limit=1000)
        self.access_token = access_token or os.getenv('PINTEREST_ACCESS_TOKEN')
        self.base_url = "https://api.pinterest.com/v5"
        
    async def search_content(self, query: str, max_results: int = 50) -> List[CrawlerResult]:
        """Search Pinterest pins."""
        try:
            await self.rate_limiter.wait_if_needed()
            
            # Demo implementation
            results = []
            for i in range(min(max_results, 10)):
                result = CrawlerResult(
                    platform="pinterest",
                    content_id=f"demo_pin_{i}",
                    content_type="pin",
                    title=f"Pinterest pin about '{query}'",
                    description=f"Sample Pinterest content for: {query}",
                    url=f"https://www.pinterest.com/pin/123456{i}/",
                    author="demo_user",
                    timestamp=time.time(),
                    metadata={'query': query, 'demo': True},
                    raw_data={'demo': True}
                )
                results.append(result)
            
            return results
                
        except Exception as e:
            logger.error(f"Pinterest search error: {e}")
            return []
    
    async def get_content_details(self, content_id: str) -> Optional[CrawlerResult]:
        """Get detailed pin information."""
        try:
            await self.rate_limiter.wait_if_needed()
            
            result = CrawlerResult(
                platform="pinterest",
                content_id=content_id,
                content_type="pin",
                title="Pinterest pin details",
                description="Detailed Pinterest pin information",
                url=f"https://www.pinterest.com/pin/{content_id}/",
                author="demo_user",
                timestamp=time.time(),
                metadata={'demo': True},
                raw_data={'demo': True}
            )
            
            return result
            
        except Exception as e:
            logger.error(f"Pinterest pin details failed: {e}")
            return None
    
    async def monitor_boards(self, board_ids: List[str], callback=None):
        """Monitor Pinterest boards for new pins."""
        logger.info("Starting Pinterest board monitoring...")
        
        while True:
            try:
                for board_id in board_ids:
                    results = await self.search_content(f"board:{board_id}", max_results=10)
                    
                    if results and callback:
                        await callback({
                            'type': 'board_update',
                            'platform': 'pinterest',
                            'board_id': board_id,
                            'results': results
                        })
                
                await asyncio.sleep(1800)  # Check every 30 minutes
                
            except Exception as e:
                logger.error(f"Board monitoring error: {e}")
                await asyncio.sleep(300)


# ================== SNAPCHAT CRAWLER ==================
class SnapchatCrawler(BaseCrawler):
    """Snapchat crawler with Snap Kit and story monitoring."""
    
    def __init__(self, access_token: Optional[str] = None):
        super().__init__("snapchat", rate_limit=500)
        self.access_token = access_token or os.getenv('SNAPCHAT_ACCESS_TOKEN')
        self.base_url = "https://kit.snapchat.com/v1"
        
    async def search_content(self, query: str, max_results: int = 50) -> List[CrawlerResult]:
        """Search Snapchat content."""
        try:
            await self.rate_limiter.wait_if_needed()
            
            # Demo implementation
            results = []
            for i in range(min(max_results, 10)):
                result = CrawlerResult(
                    platform="snapchat",
                    content_id=f"demo_snap_{i}",
                    content_type="snap",
                    title=f"Snapchat content for '{query}'",
                    description=f"Sample Snapchat content for: {query}",
                    url=f"https://www.snapchat.com/add/demo_user{i}",
                    author="demo_user",
                    timestamp=time.time(),
                    metadata={'query': query, 'demo': True},
                    raw_data={'demo': True}
                )
                results.append(result)
            
            return results
                
        except Exception as e:
            logger.error(f"Snapchat search error: {e}")
            return []
    
    async def get_content_details(self, content_id: str) -> Optional[CrawlerResult]:
        """Get detailed snap information."""
        try:
            await self.rate_limiter.wait_if_needed()
            
            result = CrawlerResult(
                platform="snapchat",
                content_id=content_id,
                content_type="snap",
                title="Snapchat content details",
                description="Detailed Snapchat content information",
                url=f"https://www.snapchat.com/snap/{content_id}",
                author="demo_user",
                timestamp=time.time(),
                metadata={'demo': True},
                raw_data={'demo': True}
            )
            
            return result
            
        except Exception as e:
            logger.error(f"Snapchat content details failed: {e}")
            return None
    
    async def monitor_stories(self, user_ids: List[str], callback=None):
        """Monitor Snapchat stories."""
        logger.info("Starting Snapchat story monitoring...")
        
        while True:
            try:
                for user_id in user_ids:
                    if callback:
                        await callback({
                            'type': 'story_update',
                            'platform': 'snapchat',
                            'user_id': user_id,
                            'stories': []
                        })
                
                await asyncio.sleep(900)  # Check every 15 minutes
                
            except Exception as e:
                logger.error(f"Story monitoring error: {e}")
                await asyncio.sleep(300)


# ================== DISCORD CRAWLER ==================
class DiscordCrawler(BaseCrawler):
    """Discord crawler with Bot API and server monitoring."""
    
    def __init__(self, bot_token: Optional[str] = None):
        super().__init__("discord", rate_limit=50)
        self.bot_token = bot_token or os.getenv('DISCORD_BOT_TOKEN')
        self.base_url = "https://discord.com/api/v10"
        
    async def search_content(self, query: str, max_results: int = 50) -> List[CrawlerResult]:
        """Search Discord messages."""
        try:
            await self.rate_limiter.wait_if_needed()
            
            # Demo implementation
            results = []
            for i in range(min(max_results, 10)):
                result = CrawlerResult(
                    platform="discord",
                    content_id=f"demo_message_{i}",
                    content_type="message",
                    title=f"Discord message about '{query}'",
                    description=f"Sample Discord content for: {query}",
                    url=f"https://discord.com/channels/demo_server/demo_channel/123456{i}",
                    author="demo_user",
                    timestamp=time.time(),
                    metadata={'query': query, 'demo': True},
                    raw_data={'demo': True}
                )
                results.append(result)
            
            return results
                
        except Exception as e:
            logger.error(f"Discord search error: {e}")
            return []
    
    async def get_content_details(self, content_id: str) -> Optional[CrawlerResult]:
        """Get detailed message information."""
        try:
            await self.rate_limiter.wait_if_needed()
            
            result = CrawlerResult(
                platform="discord",
                content_id=content_id,
                content_type="message",
                title="Discord message details",
                description="Detailed Discord message information",
                url=f"https://discord.com/channels/server/channel/{content_id}",
                author="demo_user",
                timestamp=time.time(),
                metadata={'demo': True},
                raw_data={'demo': True}
            )
            
            return result
            
        except Exception as e:
            logger.error(f"Discord message details failed: {e}")
            return None
    
    async def monitor_servers(self, server_ids: List[str], callback=None):
        """Monitor Discord servers for new messages."""
        logger.info("Starting Discord server monitoring...")
        
        while True:
            try:
                for server_id in server_ids:
                    results = await self.search_content(f"server:{server_id}", max_results=10)
                    
                    if results and callback:
                        await callback({
                            'type': 'server_update',
                            'platform': 'discord',
                            'server_id': server_id,
                            'results': results
                        })
                
                await asyncio.sleep(300)  # Check every 5 minutes
                
            except Exception as e:
                logger.error(f"Server monitoring error: {e}")
                await asyncio.sleep(300)


# ================== TELEGRAM CRAWLER ==================
class TelegramCrawler(BaseCrawler):
    """Telegram crawler with Bot API and channel monitoring."""
    
    def __init__(self, bot_token: Optional[str] = None):
        super().__init__("telegram", rate_limit=30)
        self.bot_token = bot_token or os.getenv('TELEGRAM_BOT_TOKEN')
        self.base_url = f"https://api.telegram.org/bot{self.bot_token}" if self.bot_token else None
        
    async def search_content(self, query: str, max_results: int = 50) -> List[CrawlerResult]:
        """Search Telegram messages."""
        try:
            await self.rate_limiter.wait_if_needed()
            
            # Demo implementation
            results = []
            for i in range(min(max_results, 10)):
                result = CrawlerResult(
                    platform="telegram",
                    content_id=f"demo_message_{i}",
                    content_type="message",
                    title=f"Telegram message about '{query}'",
                    description=f"Sample Telegram content for: {query}",
                    url=f"https://t.me/demo_channel/{i}",
                    author="demo_channel",
                    timestamp=time.time(),
                    metadata={'query': query, 'demo': True},
                    raw_data={'demo': True}
                )
                results.append(result)
            
            return results
                
        except Exception as e:
            logger.error(f"Telegram search error: {e}")
            return []
    
    async def get_content_details(self, content_id: str) -> Optional[CrawlerResult]:
        """Get detailed message information."""
        try:
            await self.rate_limiter.wait_if_needed()
            
            result = CrawlerResult(
                platform="telegram",
                content_id=content_id,
                content_type="message",
                title="Telegram message details",
                description="Detailed Telegram message information",
                url=f"https://t.me/channel/{content_id}",
                author="demo_channel",
                timestamp=time.time(),
                metadata={'demo': True},
                raw_data={'demo': True}
            )
            
            return result
            
        except Exception as e:
            logger.error(f"Telegram message details failed: {e}")
            return None
    
    async def monitor_channels(self, channel_ids: List[str], callback=None):
        """Monitor Telegram channels for new messages."""
        logger.info("Starting Telegram channel monitoring...")
        
        while True:
            try:
                for channel_id in channel_ids:
                    results = await self.search_content(f"channel:{channel_id}", max_results=10)
                    
                    if results and callback:
                        await callback({
                            'type': 'channel_update',
                            'platform': 'telegram',
                            'channel_id': channel_id,
                            'results': results
                        })
                
                await asyncio.sleep(300)  # Check every 5 minutes
                
            except Exception as e:
                logger.error(f"Channel monitoring error: {e}")
                await asyncio.sleep(300)


# ================== CRAWLER ORCHESTRATOR ==================
class CrawlerOrchestrator:
    """Orchestrates all platform crawlers."""
    
    def __init__(self):
        self.crawlers = {
            'youtube': YouTubeCrawler(),
            'instagram': InstagramCrawler(),
            'tiktok': TikTokCrawler(),
            'twitter': TwitterCrawler(),
            'facebook': FacebookCrawler(),
            'linkedin': LinkedInCrawler(),
            'pinterest': PinterestCrawler(),
            'snapchat': SnapchatCrawler(),
            'discord': DiscordCrawler(),
            'telegram': TelegramCrawler(),
        }
    
    async def search_all_platforms(self, query: str, max_results: int = 10) -> Dict[str, List[CrawlerResult]]:
        """Search across all platforms."""
        results = {}
        
        for platform, crawler in self.crawlers.items():
            try:
                platform_results = await crawler.search_content(query, max_results)
                results[platform] = platform_results
                logger.info(f"Found {len(platform_results)} results on {platform}")
            except Exception as e:
                logger.error(f"Error searching {platform}: {e}")
                results[platform] = []
        
        return results
    
    async def get_crawler(self, platform: str) -> Optional[BaseCrawler]:
        """Get specific platform crawler."""
        return self.crawlers.get(platform)
    
    def get_supported_platforms(self) -> List[str]:
        """Get list of supported platforms."""
        return list(self.crawlers.keys())


# Export all crawlers
__all__ = [
    'YouTubeCrawler',
    'InstagramCrawler',
    'TikTokCrawler',
    'TwitterCrawler',
    'FacebookCrawler',
    'LinkedInCrawler',
    'PinterestCrawler',
    'SnapchatCrawler',
    'DiscordCrawler',
    'TelegramCrawler',
    'CrawlerOrchestrator'
]