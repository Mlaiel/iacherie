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
from typing import Dict, List, Optional, Union, AsyncGenerator
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
import json

import aiohttp
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import isodate
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from ..utils.rate_limiter import YouTubeRateLimiter
from ..utils.proxy_manager import ProxyManager
from ..utils.user_agent_rotator import UserAgentRotator
from ...core.config import get_settings
from ...core.exceptions import CrawlerError, RateLimitError
from ...database.models import CrawlResult, ContentMatch

logger = logging.getLogger(__name__)
settings = get_settings()

@dataclass
class YouTubeVideo:
    """YouTube video data structure."""    video_id: str
    title: str
    description: str
    channel_id: str
    channel_title: str
    published_at: datetime
    duration: str
    view_count: int
    like_count: int
    comment_count: int
    thumbnail_url: str
    tags: List[str]
    category_id: str
    language: str
    captions_available: bool
    live_broadcast_content: str
    privacy_status: str

@dataclass
class YouTubeChannel:
    """YouTube channel data structure."""    channel_id: str
    title: str
    description: str
    subscriber_count: int
    video_count: int
    view_count: int
    created_at: datetime
    country: str
    custom_url: str
    thumbnail_url: str
    keywords: List[str]

class YouTubeCrawler:
    """    Professional YouTube crawler implementation.
    
    Features:
    - YouTube Data API v3 integration
    - Intelligent rate limiting and quota management
    - Multi-threaded content discovery
    - Advanced search and filtering
    - Real-time monitoring capabilities
    - Content similarity detection
    - Channel and video analytics
    - Caption and transcript extraction
    - Selenium fallback for scraping
    """    
    def __init__(self):
        """Initialize YouTube crawler."""        self.api_key = settings.YOUTUBE_API_KEY
        self.service = None
        self.rate_limiter = YouTubeRateLimiter()
        self.proxy_manager = ProxyManager()
        self.user_agent_rotator = UserAgentRotator()
        self.session = None
        
        # Initialize YouTube API service
        if self.api_key:
            try:
                self.service = build('youtube', 'v3', developerKey=self.api_key)
            except Exception as e:
                logger.error(f"Failed to initialize YouTube API service: {e}")
        
        # Selenium configuration
        self.selenium_options = webdriver.ChromeOptions()
        self.selenium_options.add_argument('--headless')
        self.selenium_options.add_argument('--no-sandbox')
        self.selenium_options.add_argument('--disable-dev-shm-usage')
        self.selenium_options.add_argument('--disable-gpu')
        
    async def __aenter__(self):
        """Async context manager entry."""        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""        if self.session:
            await self.session.close()
    
    async def search_videos(
        self,
        query: str,
        max_results: int = 50,
        order: str = 'relevance',
        published_after: Optional[datetime] = None,
        published_before: Optional[datetime] = None,
        video_duration: Optional[str] = None,
        video_type: str = 'any'
    ) -> List[YouTubeVideo]:
        """        Search YouTube videos with advanced filtering.
        
        Args:
            query: Search query string
            max_results: Maximum number of results to return
            order: Sort order (relevance, date, rating, viewCount, title)
            published_after: Filter videos published after this date
            published_before: Filter videos published before this date
            video_duration: Filter by duration (short, medium, long, any)
            video_type: Filter by type (any, episode, movie)
            
        Returns:
            List of YouTube video objects
        """        try:
            # Rate limiting check
            await self.rate_limiter.wait_if_needed()
            
            if not self.service:
                raise CrawlerError("YouTube API service not available")
            
            # Build search parameters
            search_params = {
                'part': 'snippet',
                'q': query,
                'type': 'video',
                'maxResults': min(max_results, 50),  # API limit
                'order': order,
                'videoType': video_type
            }
            
            # Add date filters
            if published_after:
                search_params['publishedAfter'] = published_after.isoformat() + 'Z'
            if published_before:
                search_params['publishedBefore'] = published_before.isoformat() + 'Z'
            
            # Add duration filter
            if video_duration:
                search_params['videoDuration'] = video_duration
            
            videos = []
            next_page_token = None
            
            while len(videos) < max_results:
                if next_page_token:
                    search_params['pageToken'] = next_page_token
                
                # Execute search request
                search_response = self.service.search().list(**search_params).execute()
                
                # Extract video IDs
                video_ids = [item['id']['videoId'] for item in search_response['items']]
                
                if not video_ids:
                    break
                
                # Get detailed video information
                video_details = await self._get_video_details(video_ids)
                videos.extend(video_details)
                
                # Check for next page
                next_page_token = search_response.get('nextPageToken')
                if not next_page_token or len(videos) >= max_results:
                    break
                
                # Update rate limiter
                await self.rate_limiter.update_usage(len(search_response['items']))
            
            return videos[:max_results]
            
        except HttpError as e:
            if e.resp.status == 403:
                raise RateLimitError("YouTube API quota exceeded")
            raise CrawlerError(f"YouTube API error: {e}")
        except Exception as e:
            logger.error(f"YouTube search error: {e}")
            raise CrawlerError(f"Search failed: {e}")
    
    async def _get_video_details(self, video_ids: List[str]) -> List[YouTubeVideo]:
        """Get detailed information for video IDs."""        try:
            # Rate limiting check
            await self.rate_limiter.wait_if_needed()
            
            video_response = self.service.videos().list(
                part='snippet,statistics,contentDetails,status',
                id=','.join(video_ids)
            ).execute()
            
            videos = []
            for item in video_response['items']:
                try:
                    video = self._parse_video_data(item)
                    videos.append(video)
                except Exception as e:
                    logger.warning(f"Failed to parse video {item.get('id', 'unknown')}: {e}")
            
            await self.rate_limiter.update_usage(len(video_ids))
            return videos
            
        except Exception as e:
            logger.error(f"Failed to get video details: {e}")
            return []
    
    def _parse_video_data(self, item: dict) -> YouTubeVideo:
        """Parse YouTube API video data into YouTubeVideo object."""        snippet = item['snippet']
        statistics = item.get('statistics', {})
        content_details = item.get('contentDetails', {})
        status = item.get('status', {})
        
        # Parse duration
        duration = content_details.get('duration', 'PT0S')
        try:
            duration_seconds = isodate.parse_duration(duration).total_seconds()
            duration_str = str(timedelta(seconds=int(duration_seconds)))
        except:
            duration_str = "00:00:00"
        
        # Parse published date
        published_at = datetime.fromisoformat(
            snippet['publishedAt'].replace('Z', '+00:00')
        )
        
        return YouTubeVideo(
            video_id=item['id'],
            title=snippet.get('title', ''),
            description=snippet.get('description', ''),
            channel_id=snippet.get('channelId', ''),
            channel_title=snippet.get('channelTitle', ''),
            published_at=published_at,
            duration=duration_str,
            view_count=int(statistics.get('viewCount', 0)),
            like_count=int(statistics.get('likeCount', 0)),
            comment_count=int(statistics.get('commentCount', 0)),
            thumbnail_url=snippet.get('thumbnails', {}).get('high', {}).get('url', ''),
            tags=snippet.get('tags', []),
            category_id=snippet.get('categoryId', ''),
            language=snippet.get('defaultLanguage', 'en'),
            captions_available=content_details.get('caption', 'false') == 'true',
            live_broadcast_content=snippet.get('liveBroadcastContent', 'none'),
            privacy_status=status.get('privacyStatus', 'public')
        )
    
    async def get_channel_info(self, channel_id: str) -> Optional[YouTubeChannel]:
        """Get detailed channel information."""        try:
            await self.rate_limiter.wait_if_needed()
            
            channel_response = self.service.channels().list(
                part='snippet,statistics,brandingSettings',
                id=channel_id
            ).execute()
            
            if not channel_response['items']:
                return None
            
            item = channel_response['items'][0]
            snippet = item['snippet']
            statistics = item.get('statistics', {})
            branding = item.get('brandingSettings', {}).get('channel', {})
            
            created_at = datetime.fromisoformat(
                snippet['publishedAt'].replace('Z', '+00:00')
            )
            
            await self.rate_limiter.update_usage(1)
            
            return YouTubeChannel(
                channel_id=channel_id,
                title=snippet.get('title', ''),
                description=snippet.get('description', ''),
                subscriber_count=int(statistics.get('subscriberCount', 0)),
                video_count=int(statistics.get('videoCount', 0)),
                view_count=int(statistics.get('viewCount', 0)),
                created_at=created_at,
                country=snippet.get('country', ''),
                custom_url=snippet.get('customUrl', ''),
                thumbnail_url=snippet.get('thumbnails', {}).get('high', {}).get('url', ''),
                keywords=branding.get('keywords', '').split() if branding.get('keywords') else []
            )
            
        except Exception as e:
            logger.error(f"Failed to get channel info for {channel_id}: {e}")
            return None
    
    async def monitor_channel(
        self,
        channel_id: str,
        check_interval: int = 300,
        max_videos: int = 10
    ) -> AsyncGenerator[List[YouTubeVideo], None]:
        """Monitor channel for new uploads."""        last_check = datetime.now()
        
        while True:
            try:
                # Search for recent videos from channel
                recent_videos = await self.search_videos(
                    query=f"",
                    max_results=max_videos,
                    order='date',
                    published_after=last_check
                )
                
                # Filter videos from specific channel
                channel_videos = [
                    video for video in recent_videos 
                    if video.channel_id == channel_id
                ]
                
                if channel_videos:
                    yield channel_videos
                
                last_check = datetime.now()
                await asyncio.sleep(check_interval)
                
            except Exception as e:
                logger.error(f"Channel monitoring error: {e}")
                await asyncio.sleep(60)  # Wait before retry
    
    async def search_similar_content(
        self,
        reference_video: YouTubeVideo,
        similarity_threshold: float = 0.8
    ) -> List[Dict]:
        """Search for content similar to reference video."""        try:
            # Create search queries based on video metadata
            search_queries = [
                reference_video.title,
                f"{reference_video.channel_title} {reference_video.title[:50]}",
                " ".join(reference_video.tags[:5]) if reference_video.tags else reference_video.title
            ]
            
            similar_videos = []
            
            for query in search_queries:
                if not query.strip():
                    continue
                
                # Search for potentially similar videos
                search_results = await self.search_videos(
                    query=query,
                    max_results=20,
                    order='relevance'
                )
                
                for video in search_results:
                    # Skip the original video
                    if video.video_id == reference_video.video_id:
                        continue
                    
                    # Calculate similarity score
                    similarity = self._calculate_video_similarity(reference_video, video)
                    
                    if similarity >= similarity_threshold:
                        similar_videos.append({
                            'video': video,
                            'similarity_score': similarity,
                            'match_type': 'content_similarity'
                        })
            
            # Remove duplicates and sort by similarity
            unique_videos = {}
            for match in similar_videos:
                video_id = match['video'].video_id
                if video_id not in unique_videos or match['similarity_score'] > unique_videos[video_id]['similarity_score']:
                    unique_videos[video_id] = match
            
            return sorted(unique_videos.values(), key=lambda x: x['similarity_score'], reverse=True)
            
        except Exception as e:
            logger.error(f"Similar content search error: {e}")
            return []
    
    def _calculate_video_similarity(self, video1: YouTubeVideo, video2: YouTubeVideo) -> float:
        """Calculate similarity score between two videos."""        # Title similarity (Jaccard similarity)
        title1_words = set(video1.title.lower().split())
        title2_words = set(video2.title.lower().split())
        title_similarity = len(title1_words & title2_words) / len(title1_words | title2_words) if title1_words | title2_words else 0
        
        # Channel similarity
        channel_similarity = 1.0 if video1.channel_id == video2.channel_id else 0.0
        
        # Duration similarity
        duration1_seconds = self._duration_to_seconds(video1.duration)
        duration2_seconds = self._duration_to_seconds(video2.duration)
        if duration1_seconds > 0 and duration2_seconds > 0:
            duration_diff = abs(duration1_seconds - duration2_seconds)
            duration_similarity = max(0, 1 - (duration_diff / max(duration1_seconds, duration2_seconds)))
        else:
            duration_similarity = 0.0
        
        # Tag similarity
        if video1.tags and video2.tags:
            tags1 = set(tag.lower() for tag in video1.tags)
            tags2 = set(tag.lower() for tag in video2.tags)
            tag_similarity = len(tags1 & tags2) / len(tags1 | tags2) if tags1 | tags2 else 0
        else:
            tag_similarity = 0.0
        
        # Weighted average
        weights = {
            'title': 0.4,
            'channel': 0.3,
            'duration': 0.2,
            'tags': 0.1
        }
        
        similarity = (
            weights['title'] * title_similarity +
            weights['channel'] * channel_similarity +
            weights['duration'] * duration_similarity +
            weights['tags'] * tag_similarity
        )
        
        return similarity
    
    def _duration_to_seconds(self, duration_str: str) -> int:
        """Convert duration string to seconds."""        try:
            parts = duration_str.split(':')
            if len(parts) == 3:  # HH:MM:SS
                hours, minutes, seconds = map(int, parts)
                return hours * 3600 + minutes * 60 + seconds
            elif len(parts) == 2:  # MM:SS
                minutes, seconds = map(int, parts)
                return minutes * 60 + seconds
            else:
                return 0
        except:
            return 0
    
    async def scrape_with_selenium(self, url: str) -> Dict:
        """Fallback scraping using Selenium when API limits are reached."""        try:
            driver = webdriver.Chrome(options=self.selenium_options)
            driver.get(url)
            
            # Wait for page to load
            wait = WebDriverWait(driver, 10)
            
            # Extract basic video information
            title_element = wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "h1.title"))
            )
            
            video_data = {
                'title': title_element.text if title_element else '',
                'url': url,
                'scraped_at': datetime.now().isoformat(),
                'method': 'selenium'
            }
            
            # Extract additional metadata if available
            try:
                description_element = driver.find_element(By.ID, "description")
                video_data['description'] = description_element.text
            except:
                pass
            
            try:
                views_element = driver.find_element(By.CSS_SELECTOR, ".view-count")
                video_data['views'] = views_element.text
            except:
                pass
            
            driver.quit()
            return video_data
            
        except Exception as e:
            logger.error(f"Selenium scraping failed for {url}: {e}")
            if 'driver' in locals():
                driver.quit()
            return {}
    
    async def get_video_captions(self, video_id: str, language: str = 'en') -> Optional[str]:
        """Extract video captions/transcripts."""        try:
            await self.rate_limiter.wait_if_needed()
            
            # Get available caption tracks
            captions_response = self.service.captions().list(
                part='snippet',
                videoId=video_id
            ).execute()
            
            if not captions_response['items']:
                return None
            
            # Find requested language or fallback to first available
            caption_id = None
            for caption in captions_response['items']:
                if caption['snippet']['language'] == language:
                    caption_id = caption['id']
                    break
            
            if not caption_id:
                caption_id = captions_response['items'][0]['id']
            
            # Download caption content
            caption_content = self.service.captions().download(
                id=caption_id,
                tfmt='srt'
            ).execute()
            
            await self.rate_limiter.update_usage(2)
            return caption_content.decode('utf-8')
            
        except Exception as e:
            logger.error(f"Failed to get captions for video {video_id}: {e}")
            return None
    
    async def analyze_engagement_metrics(self, video: YouTubeVideo) -> Dict:
        """Analyze video engagement metrics."""        try:
            # Calculate engagement rate
            total_interactions = video.like_count + video.comment_count
            engagement_rate = (total_interactions / video.view_count * 100) if video.view_count > 0 else 0
            
            # Performance categorization
            if engagement_rate > 5:
                performance = "high"
            elif engagement_rate > 2:
                performance = "medium"
            else:
                performance = "low"
            
            # Video age analysis
            video_age = datetime.now() - video.published_at
            views_per_day = video.view_count / max(video_age.days, 1)
            
            return {
                'engagement_rate': round(engagement_rate, 2),
                'performance_category': performance,
                'total_interactions': total_interactions,
                'views_per_day': round(views_per_day, 0),
                'video_age_days': video_age.days,
                'like_to_view_ratio': round((video.like_count / video.view_count * 100), 3) if video.view_count > 0 else 0,
                'comment_to_view_ratio': round((video.comment_count / video.view_count * 100), 3) if video.view_count > 0 else 0
            }
            
        except Exception as e:
            logger.error(f"Failed to analyze engagement metrics: {e}")
            return {}
    
    async def get_trending_content(self, region_code: str = 'US', category_id: str = '0') -> List[YouTubeVideo]:
        """Get trending videos for region and category."""        try:
            await self.rate_limiter.wait_if_needed()
            
            videos_response = self.service.videos().list(
                part='snippet,statistics,contentDetails',
                chart='mostPopular',
                regionCode=region_code,
                videoCategoryId=category_id,
                maxResults=50
            ).execute()
            
            videos = []
            for item in videos_response['items']:
                try:
                    video = self._parse_video_data(item)
                    videos.append(video)
                except Exception as e:
                    logger.warning(f"Failed to parse trending video: {e}")
            
            await self.rate_limiter.update_usage(1)
            return videos
            
        except Exception as e:
            logger.error(f"Failed to get trending content: {e}")
            return []
