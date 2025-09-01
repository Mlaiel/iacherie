"""YouTube Crawler
===============

Professional YouTube content crawler with advanced monitoring capabilities.
Implements YouTube Data API v3 integration with intelligent rate limiting.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: All rights reserved. Unauthorized use, reproduction, or distribution prohibited.

WARNING: This code is protected by copyright law. Any unauthorized copying, 
distribution, or modification is strictly prohibited and will result in 
legal action. Contact mlaiel@live.de for licensing.
"""

import asyncio
import logging
import json
import time
import re
import os
from typing import Dict, List, Optional, Union
from datetime import datetime, timedelta
from dataclasses import dataclass
from urllib.parse import urlparse, parse_qs

from .core import BaseCrawler, CrawlerResult, RateLimiter

logger = logging.getLogger(__name__)

@dataclass
class YouTubeVideo:
    """
YouTube video data structure."""
    video_id: str
    title: str
    description: str
    channel_id: str
    channel_title: str
    published_at: datetime
    duration: str
    view_count: int
    like_count: int
    comment_count: int
    tags: List[str]
    thumbnail_url: str

class YouTubeCrawler(BaseCrawler):
    """
    Professional YouTube crawler with API v3 and copyright monitoring.
    
    Features:
    - YouTube Data API v3 integration
    - Copyright violation detection
    - Real-time monitoring
    - Advanced search capabilities
    - Channel and playlist monitoring
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
Initialize YouTube crawler."""
        super().__init__("youtube", rate_limit=100)  # 100 requests per window
        self.api_key = api_key or os.getenv('YOUTUBE_API_KEY')
        self.base_url = "https://www.googleapis.com/youtube/v3"
        
    async def search_content(self, query: str, max_results: int = 50) -> List[CrawlerResult]:
        """
        Search YouTube videos with advanced filtering.
        
        Args:
            query: Search query string
            max_results: Maximum number of results to return
            
        Returns:
            List of crawler results
        """
        try:
            await self.rate_limiter.wait_if_needed()
            
            if not self.api_key:
                return await self._search_content_scraping(query, max_results)
            
            return await self._search_content_api(query, max_results)
            
        except Exception as e:
            logger.error(f"YouTube search error: {e}")
            return []
    
    async def _search_content_api(self, query: str, max_results: int) -> List[CrawlerResult]:
        """Search using YouTube API v3."""
        try:
            import urllib.request
            import urllib.parse
            
            # Build search URL
            params = {
                'part': 'snippet',
                'q': query,
                'type': 'video',
                'maxResults': min(max_results, 50),
                'key': self.api_key
            }
            
            url = f"{self.base_url}/search?" + urllib.parse.urlencode(params)
            
            # Make API request
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
    
    async def _search_content_scraping(self, query: str, max_results: int) -> List[CrawlerResult]:
        """Fallback scraping method when API is not available."""
        try:
            import urllib.request
            import urllib.parse
            
            # Simple web scraping approach
            search_url = f"https://www.youtube.com/results?search_query={urllib.parse.quote(query)}"
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            req = urllib.request.Request(search_url, headers=headers)
            
            with urllib.request.urlopen(req) as response:
                html = response.read().decode('utf-8')
            
            # Extract video data using regex (basic implementation)
            video_pattern = r'"videoId":"([^"]+)".*?"title":{"runs":\[{"text":"([^"]+)"}\]}'
            matches = re.findall(video_pattern, html)
            
            results = []
            for video_id, title in matches[:max_results]:
                result = CrawlerResult(
                    platform="youtube",
                    content_id=video_id,
                    content_type="video",
                    title=title,
                    description="",
                    url=f"https://www.youtube.com/watch?v={video_id}",
                    author="",
                    timestamp=time.time(),
                    metadata={'scraped': True},
                    raw_data={'video_id': video_id, 'title': title}
                )
                results.append(result)
            
            return results
            
        except Exception as e:
            logger.error(f"YouTube scraping failed: {e}")
            return []
    
    async def get_content_details(self, content_id: str) -> Optional[CrawlerResult]:
        """Get detailed information about specific video."""
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
        logger.info("Starting copyright monitoring...")
        
        while True:
            try:
                for content_term in protected_content:
                    results = await self.search_content(content_term, max_results=20)
                    
                    for result in results:
                        # Simple copyright detection (enhance with ML/AI models)
                        similarity_score = self._calculate_similarity(content_term, result.title)
                        
                        if similarity_score > 0.8:  # High similarity threshold
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
                await asyncio.sleep(600)  # Wait 10 minutes on error
    
    def _calculate_similarity(self, text1: str, text2: str) -> float:
        """Calculate basic text similarity."""
        # Simple Jaccard similarity
        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())
        
        intersection = words1.intersection(words2)
        union = words1.union(words2)
        
        return len(intersection) / len(union) if union else 0.0
    
    async def crawl(self, targets: List[str], **kwargs) -> List[CrawlerResult]:
        """
        Standard crawl method for industrial compliance.
        Crawls YouTube content based on targets (URLs, channels, or queries).
        """
        results = []
        
        for target in targets:
            try:
                # Determine target type
                if target.startswith('http'):
                    # URL-based crawling
                    video_id = self._extract_video_id(target)
                    if video_id:
                        detail = await self.get_content_details(video_id)
                        if detail:
                            results.append(detail)
                else:
                    # Query-based crawling
                    search_results = await self.search_content(target, max_results=10)
                    results.extend(search_results)
                    
            except Exception as e:
                logger.error(f"Crawl failed for target {target}: {e}")
        
        return results
    
    def extract(self, raw_data: Dict) -> CrawlerResult:
        """
        Standard extract method for industrial compliance.
        Extracts structured data from raw YouTube API response.
        """
        try:
            if 'snippet' in raw_data:
                snippet = raw_data['snippet']
                statistics = raw_data.get('statistics', {})
                
                return CrawlerResult(
                    platform="youtube",
                    content_id=raw_data.get('id', ''),
                    content_type="video",
                    title=snippet.get('title', ''),
                    description=snippet.get('description', ''),
                    url=f"https://www.youtube.com/watch?v={raw_data.get('id', '')}",
                    author=snippet.get('channelTitle', ''),
                    timestamp=time.time(),
                    metadata={
                        'channel_id': snippet.get('channelId'),
                        'published_at': snippet.get('publishedAt'),
                        'view_count': statistics.get('viewCount', 0),
                        'like_count': statistics.get('likeCount', 0),
                        'thumbnail': snippet.get('thumbnails', {}).get('default', {}).get('url')
                    },
                    raw_data=raw_data
                )
            else:
                # Handle other data formats
                return CrawlerResult(
                    platform="youtube",
                    content_id=raw_data.get('id', 'unknown'),
                    content_type="unknown",
                    title=raw_data.get('title', ''),
                    description=raw_data.get('description', ''),
                    url=raw_data.get('url', ''),
                    author=raw_data.get('author', ''),
                    timestamp=time.time(),
                    metadata=raw_data,
                    raw_data=raw_data
                )
                
        except Exception as e:
            logger.error(f"Extract failed: {e}")
            return CrawlerResult(
                platform="youtube",
                content_id="error",
                content_type="error",
                title="Extraction Error",
                description=str(e),
                url="",
                author="",
                timestamp=time.time(),
                metadata={'error': str(e)},
                raw_data=raw_data
            )
    
    def _extract_video_id(self, url: str) -> Optional[str]:
        """Extract video ID from YouTube URL."""
        import re
        
        patterns = [
            r'(?:youtube\.com/watch\?v=)([^&]+)',
            r'(?:youtu\.be/)([^?]+)',
            r'(?:youtube\.com/embed/)([^?]+)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        
        return None