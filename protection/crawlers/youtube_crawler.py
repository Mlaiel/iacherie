"""🎬 YouTube Content Crawler
==========================

Professional YouTube content discovery and monitoring system.
Integrates YouTube Data API v3 with Selenium for comprehensive crawling.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️ STRICT WARNING: Unauthorized use, copying, or distribution of this code 
is strictly prohibited without explicit written permission from Fahed Mlaiel.
Contact: mlaiel@live.de for licensing and authorization.
"""

import asyncio
import logging
import re
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import requests
import json
import time

from .base_crawler import BasePlatformCrawler, CrawlResult, CrawlerStatus

logger = logging.getLogger(__name__)

@dataclass
class YouTubeVideoInfo:
    """
YouTube video information structure."""
    video_id: str
    title: str
    description: str
    channel_id: str
    channel_name: str
    published_at: datetime
    duration: str
    view_count: int
    like_count: int
    comment_count: int
    category_id: str
    tags: List[str]
    thumbnail_url: str
    video_url: str
    download_url: Optional[str] = None
    metadata: Dict[str, Any] = None

@dataclass
class YouTubeChannelInfo:
    """
YouTube channel information structure."""
    channel_id: str
    title: str
    description: str
    subscriber_count: int
    video_count: int
    view_count: int
    published_at: datetime
    thumbnail_url: str
    country: Optional[str] = None
    custom_url: Optional[str] = None

class YouTubeAPIClient:
    """
YouTube Data API v3 client with advanced features."""
    
    def __init__(self, api_key -> None: str, quota_limit -> None: int = 10000) -> None:
        """
Initialize YouTube API client."""
        self.api_key = api_key
        self.quota_limit = quota_limit
        self.quota_used = 0
        self.service = None
        self.last_reset = datetime.utcnow()
        
        # Initialize YouTube service
        try:
            self.service = build('youtube', 'v3', developerKey=api_key)
            logger.info("YouTube API client initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize YouTube API: {e}")
            raise
    
    def _check_quota(self, cost: int = 1) -> bool:
        """Check if API quota allows operation."""
        # Reset quota daily
        if datetime.utcnow() - self.last_reset > timedelta(days=1):
            self.quota_used = 0
            self.last_reset = datetime.utcnow()
        
        if self.quota_used + cost > self.quota_limit:
            logger.warning(f"YouTube API quota limit reached: {self.quota_used}/{self.quota_limit}")
            return False
        
        return True
    
    async def search_videos(
        self,
        query: str,
        max_results: int = 50,
        order: str = 'relevance',
        published_after: Optional[datetime] = None,
        video_duration: Optional[str] = None
    ) -> List[YouTubeVideoInfo]:
        """Search for videos using YouTube API."""
        if not self._check_quota(100):  # Search costs 100 quota units
            raise Exception("YouTube API quota exceeded")
        
        try:
            search_params = {
                'part': 'snippet',
                'q': query,
                'type': 'video',
                'maxResults': min(max_results, 50),
                'order': order
            }
            
            if published_after:
                search_params['publishedAfter'] = published_after.isoformat() + 'Z'
            
            if video_duration:
                search_params['videoDuration'] = video_duration
            
            # Execute search
            search_response = self.service.search().list(**search_params).execute()
            self.quota_used += 100
            
            video_ids = [item['id']['videoId'] for item in search_response['items']]
            
            # Get detailed video information
            videos_info = await self.get_videos_details(video_ids)
            
            logger.info(f"Found {len(videos_info)} videos for query: {query}")
            return videos_info
            
        except HttpError as e:
            logger.error(f"YouTube API search error: {e}")
            raise
        except Exception as e:
            logger.error(f"YouTube search error: {e}")
            raise
    
    async def get_videos_details(self, video_ids: List[str]) -> List[YouTubeVideoInfo]:
        """Get detailed information for videos."""
        if not video_ids:
            return []
        
        if not self._check_quota(1):  # Videos.list costs 1 quota unit per request
            raise Exception("YouTube API quota exceeded")
        
        try:
            # YouTube API accepts max 50 IDs per request
            all_videos = []
            
            for i in range(0, len(video_ids), 50):
                batch_ids = video_ids[i:i+50]
                
                response = self.service.videos().list(
                    part='snippet,statistics,contentDetails',
                    id=','.join(batch_ids)
                ).execute()
                
                self.quota_used += 1
                
                for item in response['items']:
                    video_info = self._parse_video_details(item)
                    all_videos.append(video_info)
                
                # Rate limiting
                await asyncio.sleep(0.1)
            
            return all_videos
            
        except HttpError as e:
            logger.error(f"YouTube API videos details error: {e}")
            raise
        except Exception as e:
            logger.error(f"YouTube videos details error: {e}")
            raise
    
    def _parse_video_details(self, item: Dict) -> YouTubeVideoInfo:
        """Parse video details from API response."""
        snippet = item['snippet']
        statistics = item.get('statistics', {})
        content_details = item.get('contentDetails', {})
        
        return YouTubeVideoInfo(
            video_id=item['id'],
            title=snippet.get('title', ''),
            description=snippet.get('description', ''),
            channel_id=snippet.get('channelId', ''),
            channel_name=snippet.get('channelTitle', ''),
            published_at=datetime.fromisoformat(snippet['publishedAt'].replace('Z', '+00:00')),
            duration=content_details.get('duration', ''),
            view_count=int(statistics.get('viewCount', 0)),
            like_count=int(statistics.get('likeCount', 0)),
            comment_count=int(statistics.get('commentCount', 0)),
            category_id=snippet.get('categoryId', ''),
            tags=snippet.get('tags', []),
            thumbnail_url=snippet.get('thumbnails', {}).get('high', {}).get('url', ''),
            video_url=f"https://www.youtube.com/watch?v={item['id']}",
            metadata={
                'definition': content_details.get('definition', ''),
                'caption': content_details.get('caption', ''),
                'licensedContent': content_details.get('licensedContent', False),
                'projection': content_details.get('projection', '')
            }
        )
    
    async def get_channel_info(self, channel_id: str) -> Optional[YouTubeChannelInfo]:
        """Get channel information."""
        if not self._check_quota(1):
            raise Exception("YouTube API quota exceeded")
        
        try:
            response = self.service.channels().list(
                part='snippet,statistics',
                id=channel_id
            ).execute()
            
            self.quota_used += 1
            
            if not response['items']:
                return None
            
            item = response['items'][0]
            snippet = item['snippet']
            statistics = item['statistics']
            
            return YouTubeChannelInfo(
                channel_id=channel_id,
                title=snippet.get('title', ''),
                description=snippet.get('description', ''),
                subscriber_count=int(statistics.get('subscriberCount', 0)),
                video_count=int(statistics.get('videoCount', 0)),
                view_count=int(statistics.get('viewCount', 0)),
                published_at=datetime.fromisoformat(snippet['publishedAt'].replace('Z', '+00:00')),
                thumbnail_url=snippet.get('thumbnails', {}).get('high', {}).get('url', ''),
                country=snippet.get('country'),
                custom_url=snippet.get('customUrl')
            )
            
        except HttpError as e:
            logger.error(f"YouTube API channel info error: {e}")
            return None
        except Exception as e:
            logger.error(f"YouTube channel info error: {e}")
            return None

class YouTubeSeleniumCrawler:
    """Selenium-based YouTube crawler for advanced scraping."""
    
    def __init__(self, headless -> None: bool = True, proxy -> None: Optional[str] = None) -> None:
        """
Initialize Selenium crawler."""
        self.headless = headless
        self.proxy = proxy
        self.driver = None
        self.wait = None
        
    def _setup_driver(self) -> webdriver.Chrome:
        """
Setup Chrome WebDriver with optimal configuration."""
        options = Options()
        
        if self.headless:
            options.add_argument('--headless')
        
        # Performance optimizations
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-gpu')
        options.add_argument('--disable-extensions')
        options.add_argument('--disable-logging')
        options.add_argument('--disable-web-security')
        options.add_argument('--allow-running-insecure-content')
        
        # User agent
        options.add_argument(
            '--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
            'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        )
        
        if self.proxy:
            options.add_argument(f'--proxy-server={self.proxy}')
        
        try:
            driver = webdriver.Chrome(options=options)
            driver.set_page_load_timeout(30)
            return driver
        except Exception as e:
            logger.error(f"Failed to setup Chrome driver: {e}")
            raise
    
    async def scrape_video_page(self, video_url: str) -> Dict[str, Any]:
        """Scrape detailed information from YouTube video page."""
        if not self.driver:
            self.driver = self._setup_driver()
            self.wait = WebDriverWait(self.driver, 10)
        
        try:
            # Navigate to video
            self.driver.get(video_url)
            
            # Wait for page to load
            await asyncio.sleep(3)
            
            # Extract video information
            video_data = {}
            
            # Title
            try:
                title_element = self.wait.until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, 'h1.title yt-formatted-string'))
                )
                video_data['title'] = title_element.text
            except:
                video_data['title'] = ''
            
            # Views
            try:
                views_element = self.driver.find_element(By.CSS_SELECTOR, '#info #count .view-count')
                views_text = views_element.text
                video_data['views'] = self._parse_view_count(views_text)
            except:
                video_data['views'] = 0
            
            # Upload date
            try:
                date_element = self.driver.find_element(By.CSS_SELECTOR, '#info-strings yt-formatted-string')
                video_data['upload_date'] = date_element.text
            except:
                video_data['upload_date'] = ''
            
            # Description
            try:
                description_element = self.driver.find_element(
                    By.CSS_SELECTOR, '#description yt-formatted-string'
                )
                video_data['description'] = description_element.text
            except:
                video_data['description'] = ''
            
            # Channel name
            try:
                channel_element = self.driver.find_element(
                    By.CSS_SELECTOR, '#upload-info #channel-name a'
                )
                video_data['channel_name'] = channel_element.text
                video_data['channel_url'] = channel_element.get_attribute('href')
            except:
                video_data['channel_name'] = ''
                video_data['channel_url'] = ''
            
            # Likes/Dislikes (if available)
            try:
                like_button = self.driver.find_element(
                    By.CSS_SELECTOR, '#segmented-like-button button[aria-pressed="false"]'
                )
                like_text = like_button.get_attribute('aria-label')
                video_data['likes'] = self._parse_like_count(like_text)
            except:
                video_data['likes'] = 0
            
            # Comments count
            try:
                comments_element = self.driver.find_element(
                    By.CSS_SELECTOR, '#comments #count yt-formatted-string'
                )
                comments_text = comments_element.text
                video_data['comments_count'] = self._parse_view_count(comments_text)
            except:
                video_data['comments_count'] = 0
            
            return video_data
            
        except Exception as e:
            logger.error(f"Error scraping YouTube video page: {e}")
            return {}
    
    def _parse_view_count(self, text: str) -> int:
        """Parse view count from text."""
        if not text:
            return 0
        
        # Remove non-numeric characters except K, M, B
        clean_text = re.sub(r'[^\d\.,KMB]', '', text.upper())
        
        try:
            if 'B' in clean_text:
                return int(float(clean_text.replace('B', '')) * 1_000_000_000)
            elif 'M' in clean_text:
                return int(float(clean_text.replace('M', '')) * 1_000_000)
            elif 'K' in clean_text:
                return int(float(clean_text.replace('K', '')) * 1_000)
            else:
                return int(clean_text.replace(',', ''))
        except:
            return 0
    
    def _parse_like_count(self, text: str) -> int:
        """
Parse like count from aria-label."""
        if not text:
            return 0
        
        # Extract number from aria-label like "123 likes"
        match = re.search(r'(\d+(?:,\d+)*)', text)
        if match:
            return int(match.group(1).replace(',', ''))
        return 0
    
    def close(self) -> None:
        """Close Selenium driver."""
        if self.driver:
            self.driver.quit()
            self.driver = None

class YouTubeCrawler(BasePlatformCrawler):
    """
    Professional YouTube Content Crawler
    ====================================
    
    Advanced YouTube content discovery and monitoring system combining:
    - YouTube Data API v3 for comprehensive metadata
    - Selenium WebDriver for advanced scraping
    - Intelligent rate limiting and quota management
    - Real-time content monitoring
    - Multi-format content detection
    """
    
    def __init__(self, config -> None: Dict[str, Any]) -> None:
        """
Initialize YouTube crawler."""
        super().__init__("youtube", config)
        
        # API configuration
        self.api_key = config.get('api_key')
        self.quota_limit = config.get('quota_limit', 10000)
        
        # Selenium configuration
        self.use_selenium = config.get('use_selenium', True)
        self.headless = config.get('headless', True)
        self.proxy = config.get('proxy')
        
        # Search configuration
        self.max_results_per_search = config.get('max_results_per_search', 50)
        self.search_orders = config.get('search_orders', ['relevance', 'date', 'viewCount'])
        
        # Initialize clients
        self.api_client = None
        self.selenium_crawler = None
        
        if self.api_key:
            try:
                self.api_client = YouTubeAPIClient(self.api_key, self.quota_limit)
                logger.info("YouTube API client initialized")
            except Exception as e:
                logger.error(f"Failed to initialize YouTube API: {e}")
        
        if self.use_selenium:
            try:
                self.selenium_crawler = YouTubeSeleniumCrawler(self.headless, self.proxy)
                logger.info("YouTube Selenium crawler initialized")
            except Exception as e:
                logger.error(f"Failed to initialize Selenium crawler: {e}")
    
    async def search_content(
        self,
        query: str,
        content_type: str = 'video',
        max_results: int = None,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[CrawlResult]:
        """Search for content on YouTube."""
        if not self.api_client and not self.selenium_crawler:
            raise Exception("No YouTube crawling methods available")
        
        max_results = max_results or self.max_results_per_search
        results = []
        
        try:
            # Primary: Use API if available
            if self.api_client:
                api_results = await self._search_with_api(query, max_results, filters)
                results.extend(api_results)
            
            # Secondary: Use Selenium for additional data
            if self.selenium_crawler and len(results) < max_results:
                remaining = max_results - len(results)
                selenium_results = await self._search_with_selenium(query, remaining, filters)
                results.extend(selenium_results)
            
            # Post-process results
            processed_results = await self._post_process_results(results)
            
            logger.info(f"YouTube search '{query}' returned {len(processed_results)} results")
            return processed_results
            
        except Exception as e:
            logger.error(f"YouTube search error: {e}")
            return []
    
    async def _search_with_api(
        self,
        query: str,
        max_results: int,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[CrawlResult]:
        """Search using YouTube API."""
        try:
            # Apply filters
            search_params = {}
            if filters:
                if 'published_after' in filters:
                    search_params['published_after'] = filters['published_after']
                if 'duration' in filters:
                    search_params['video_duration'] = filters['duration']
                if 'order' in filters:
                    search_params['order'] = filters['order']
            
            # Search videos
            videos = await self.api_client.search_videos(
                query=query,
                max_results=max_results,
                **search_params
            )
            
            # Convert to CrawlResult format
            results = []
            for video in videos:
                result = CrawlResult(
                    platform="youtube",
                    url=video.video_url,
                    title=video.title,
                    description=video.description,
                    content_type="video",
                    file_url=video.video_url,
                    metadata={
                        'video_id': video.video_id,
                        'channel_id': video.channel_id,
                        'channel_name': video.channel_name,
                        'published_at': video.published_at.isoformat(),
                        'duration': video.duration,
                        'view_count': video.view_count,
                        'like_count': video.like_count,
                        'comment_count': video.comment_count,
                        'category_id': video.category_id,
                        'tags': video.tags,
                        'thumbnail_url': video.thumbnail_url,
                        **video.metadata
                    },
                    discovered_at=datetime.utcnow(),
                    fingerprint_candidates=[video.video_url, video.title]
                )
                results.append(result)
            
            return results
            
        except Exception as e:
            logger.error(f"YouTube API search error: {e}")
            return []
    
    async def _search_with_selenium(
        self,
        query: str,
        max_results: int,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[CrawlResult]:
        """Search using Selenium scraping."""
        if not self.selenium_crawler:
            return []
        
        try:
            # For now, return empty - full Selenium search implementation
            # would involve navigating to YouTube search page and scraping results
            logger.info("Selenium search not fully implemented yet")
            return []
            
        except Exception as e:
            logger.error(f"YouTube Selenium search error: {e}")
            return []
    
    async def _post_process_results(self, results: List[CrawlResult]) -> List[CrawlResult]:
        """Post-process crawl results with additional information."""
        processed_results = []
        
        for result in results:
            try:
                # Add enhanced metadata if Selenium is available
                if self.selenium_crawler and result.url:
                    enhanced_data = await self.selenium_crawler.scrape_video_page(result.url)
                    if enhanced_data:
                        result.metadata.update(enhanced_data)
                
                # Generate additional fingerprint candidates
                if result.title:
                    result.fingerprint_candidates.extend([
                        result.title.lower(),
                        result.metadata.get('channel_name', '').lower()
                    ])
                
                processed_results.append(result)
                
            except Exception as e:
                logger.error(f"Error post-processing result {result.url}: {e}")
                processed_results.append(result)  # Add original result
        
        return processed_results
    
    async def monitor_channel(
        self,
        channel_id: str,
        callback_func: callable = None
    ) -> bool:
        """Monitor a YouTube channel for new content."""
        if not self.api_client:
            logger.error("YouTube API not available for channel monitoring")
            return False
        
        try:
            # Get channel info
            channel_info = await self.api_client.get_channel_info(channel_id)
            if not channel_info:
                logger.error(f"Channel {channel_id} not found")
                return False
            
            logger.info(f"Started monitoring channel: {channel_info.title}")
            
            # Store monitoring state
            self.monitoring_channels[channel_id] = {
                'channel_info': channel_info,
                'last_check': datetime.utcnow(),
                'callback': callback_func
            }
            
            return True
            
        except Exception as e:
            logger.error(f"Error starting channel monitoring: {e}")
            return False
    
    async def check_rate_limits(self) -> bool:
        """Check if crawler is within rate limits."""
        if self.api_client:
            return self.api_client._check_quota(1)
        return True
    
    async def get_quota_status(self) -> Dict[str, Any]:
        """
Get current API quota status."""
        if not self.api_client:
            return {"error": "API client not available"}
        
        return {
            "quota_limit": self.api_client.quota_limit,
            "quota_used": self.api_client.quota_used,
            "quota_remaining": self.api_client.quota_limit - self.api_client.quota_used,
            "last_reset": self.api_client.last_reset.isoformat(),
            "next_reset": (self.api_client.last_reset + timedelta(days=1)).isoformat()
        }
    
    def cleanup(self) -> None:
        """Cleanup crawler resources."""
        if self.selenium_crawler:
            self.selenium_crawler.close()
        
        logger.info("YouTube crawler cleanup completed")

# Export main classes
__all__ = [
    'YouTubeCrawler',
    'YouTubeAPIClient', 
    'YouTubeSeleniumCrawler',
    'YouTubeVideoInfo',
    'YouTubeChannelInfo'
]
