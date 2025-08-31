"""YouTube Advanced API Integration
===============================

Professional YouTube API integration for content monitoring and analytics.
Combines official YouTube Data API v3 with advanced scraping techniques
for comprehensive content surveillance and rights protection.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: © 2025 Fahed Mlaiel. All rights reserved.

⚠️  INTELLECTUAL PROPERTY WARNING ⚠️
This code is the exclusive property of Fahed Mlaiel (mlaiel@live.de).
Unauthorized use, copying, modification, or distribution is strictly prohibited.
Violators will face immediate legal action under German and international law.
"""import asyncio
import logging
import re
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, asdict
import aiohttp
import json
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import yt_dlp

from .base import BaseCrawler, CrawlResult
from ..config import ContentType
from ..security.encryption import SecurityManager
from ..utils.rate_limiter import RateLimiter

logger = logging.getLogger(__name__)

@dataclass
class YouTubeVideoData:
    """Comprehensive YouTube video metadata structure."""    
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
    category_id: str
    tags: List[str]
    thumbnail_url: str
    default_language: Optional[str]
    captions_available: bool
    live_status: str
    privacy_status: str
    embeddable: bool
    content_rating: Dict[str, Any]
    statistics: Dict[str, Any]
    
    # Advanced metadata
    audio_codec: Optional[str] = None
    video_codec: Optional[str] = None
    resolution: Optional[str] = None
    fps: Optional[int] = None
    audio_quality: Optional[str] = None
    file_size: Optional[int] = None
    download_url: Optional[str] = None

@dataclass
class YouTubeChannelData:
    """YouTube channel comprehensive information."""    
    channel_id: str
    title: str
    description: str
    custom_url: Optional[str]
    published_at: datetime
    subscriber_count: int
    video_count: int
    view_count: int
    country: Optional[str]
    default_language: Optional[str]
    avatar_url: str
    banner_url: Optional[str]
    keywords: List[str]
    verification_status: str
    content_categories: List[str]

class YouTubeAPIManager:
    """Professional YouTube API management with advanced capabilities."""    
    def __init__(self, api_key: str, quota_manager: Optional[Any] = None):
        """Initialize YouTube API service with quota management."""        self.api_key = api_key
        self.service = None
        self.quota_manager = quota_manager
        self.rate_limiter = RateLimiter(
            max_calls=100,  # YouTube API quota per 100 seconds
            time_window=100
        )
        self._initialize_service()
    
    def _initialize_service(self):
        """Initialize YouTube Data API v3 service."""        try:
            self.service = build('youtube', 'v3', developerKey=self.api_key)
            logger.info("YouTube API service initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize YouTube API: {e}")
            raise
    
    async def get_video_details(self, video_id: str) -> Optional[YouTubeVideoData]:
        """Fetch comprehensive video details from YouTube API."""        await self.rate_limiter.acquire()
        
        try:
            # Request video details with all available parts
            request = self.service.videos().list(
                part='snippet,statistics,contentDetails,status,recordingDetails',
                id=video_id
            )
            response = request.execute()
            
            if not response.get('items'):
                return None
            
            video_data = response['items'][0]
            snippet = video_data['snippet']
            statistics = video_data.get('statistics', {})
            content_details = video_data.get('contentDetails', {})
            status = video_data.get('status', {})
            
            # Parse video data into structured format
            return YouTubeVideoData(
                video_id=video_id,
                title=snippet.get('title', ''),
                description=snippet.get('description', ''),
                channel_id=snippet.get('channelId', ''),
                channel_title=snippet.get('channelTitle', ''),
                published_at=datetime.fromisoformat(
                    snippet.get('publishedAt', '').replace('Z', '+00:00')
                ),
                duration=content_details.get('duration', ''),
                view_count=int(statistics.get('viewCount', 0)),
                like_count=int(statistics.get('likeCount', 0)),
                comment_count=int(statistics.get('commentCount', 0)),
                category_id=snippet.get('categoryId', ''),
                tags=snippet.get('tags', []),
                thumbnail_url=snippet.get('thumbnails', {}).get('high', {}).get('url', ''),
                default_language=snippet.get('defaultLanguage'),
                captions_available=content_details.get('caption') == 'true',
                live_status=snippet.get('liveBroadcastContent', 'none'),
                privacy_status=status.get('privacyStatus', 'public'),
                embeddable=status.get('embeddable', True),
                content_rating=content_details.get('contentRating', {}),
                statistics=statistics
            )
            
        except HttpError as e:
            logger.error(f"YouTube API error for video {video_id}: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error fetching video {video_id}: {e}")
            return None
    
    async def search_videos(
        self,
        query: str,
        max_results: int = 50,
        published_after: Optional[datetime] = None,
        content_type: str = 'video'
    ) -> List[str]:
        """Search YouTube videos with advanced filtering."""        await self.rate_limiter.acquire()
        
        try:
            search_params = {
                'part': 'id',
                'q': query,
                'type': content_type,
                'maxResults': min(max_results, 50),  # API limit
                'order': 'relevance'
            }
            
            if published_after:
                search_params['publishedAfter'] = published_after.isoformat() + 'Z'
            
            request = self.service.search().list(**search_params)
            response = request.execute()
            
            video_ids = []
            for item in response.get('items', []):
                if item['id']['kind'] == 'youtube#video':
                    video_ids.append(item['id']['videoId'])
            
            return video_ids
            
        except HttpError as e:
            logger.error(f"YouTube search error: {e}")
            return []
        except Exception as e:
            logger.error(f"Unexpected search error: {e}")
            return []

    async def get_channel_videos(
        self,
        channel_id: str,
        max_results: int = 50,
        published_after: Optional[datetime] = None
    ) -> List[str]:
        """Get all videos from a specific channel."""        await self.rate_limiter.acquire()
        
        try:
            # First get the uploads playlist ID
            channel_request = self.service.channels().list(
                part='contentDetails',
                id=channel_id
            )
            channel_response = channel_request.execute()
            
            if not channel_response.get('items'):
                return []
            
            uploads_playlist_id = (
                channel_response['items'][0]
                ['contentDetails']['relatedPlaylists']['uploads']
            )
            
            # Get videos from uploads playlist
            playlist_params = {
                'part': 'contentDetails',
                'playlistId': uploads_playlist_id,
                'maxResults': min(max_results, 50)
            }
            
            if published_after:
                playlist_params['publishedAfter'] = published_after.isoformat() + 'Z'
            
            playlist_request = self.service.playlistItems().list(**playlist_params)
            playlist_response = playlist_request.execute()
            
            video_ids = []
            for item in playlist_response.get('items', []):
                video_ids.append(item['contentDetails']['videoId'])
            
            return video_ids
            
        except HttpError as e:
            logger.error(f"Channel videos fetch error: {e}")
            return []
        except Exception as e:
            logger.error(f"Unexpected channel fetch error: {e}")
            return []

class YouTubeContentExtractor:
    """Advanced YouTube content extraction using yt-dlp."""    
    def __init__(self):
        """Initialize yt-dlp extractor with optimized settings."""        self.ydl_opts = {
            'format': 'bestaudio/best',
            'extractaudio': True,
            'audioformat': 'mp3',
            'outtmpl': '/tmp/%(id)s.%(ext)s',
            'writesubtitles': True,
            'writeautomaticsub': True,
            'subtitleslangs': ['en', 'fr', 'de', 'es'],
            'ignoreerrors': True,
            'no_warnings': True
        }
    
    async def extract_audio_metadata(self, video_url: str) -> Dict[str, Any]:
        """Extract detailed audio metadata from YouTube video."""        try:
            with yt_dlp.YoutubeDL(self.ydl_opts) as ydl:
                info = ydl.extract_info(video_url, download=False)
                
                audio_metadata = {
                    'duration': info.get('duration'),
                    'abr': info.get('abr'),  # Audio bitrate
                    'acodec': info.get('acodec'),
                    'asr': info.get('asr'),  # Audio sample rate
                    'filesize': info.get('filesize'),
                    'format_id': info.get('format_id'),
                    'ext': info.get('ext'),
                    'uploader': info.get('uploader'),
                    'upload_date': info.get('upload_date'),
                    'tags': info.get('tags', []),
                    'categories': info.get('categories', []),
                    'subtitles': list(info.get('subtitles', {}).keys()),
                    'automatic_captions': list(info.get('automatic_captions', {}).keys())
                }
                
                return audio_metadata
                
        except Exception as e:
            logger.error(f"Audio extraction error for {video_url}: {e}")
            return {}
    
    async def download_audio_sample(
        self,
        video_url: str,
        start_time: int = 0,
        duration: int = 30
    ) -> Optional[str]:
        """Download audio sample for fingerprinting analysis."""        try:
            import tempfile
            import os
            
            with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as temp_file:
                temp_path = temp_file.name
            
            # Configure yt-dlp for sample extraction
            sample_opts = self.ydl_opts.copy()
            sample_opts.update({
                'outtmpl': temp_path,
                'postprocessor_args': [
                    '-ss', str(start_time),
                    '-t', str(duration)
                ]
            })
            
            with yt_dlp.YoutubeDL(sample_opts) as ydl:
                ydl.download([video_url])
            
            if os.path.exists(temp_path):
                return temp_path
            
            return None
            
        except Exception as e:
            logger.error(f"Audio sample download error: {e}")
            return None

class YouTubeCrawler(BaseCrawler):
    """Professional YouTube crawler with advanced monitoring capabilities."""    
    def __init__(self, config: Dict[str, Any]):
        """Initialize YouTube crawler with configuration."""        super().__init__(config)
        self.api_manager = YouTubeAPIManager(
            api_key=config.get('youtube_api_key')
        )
        self.content_extractor = YouTubeContentExtractor()
        self.platform = 'youtube'
    
    async def crawl_video(self, video_id: str) -> Optional[CrawlResult]:
        """Crawl comprehensive data for a specific YouTube video."""        try:
            # Get video metadata from API
            video_data = await self.api_manager.get_video_details(video_id)
            if not video_data:
                return None
            
            # Extract audio metadata
            video_url = f"https://www.youtube.com/watch?v={video_id}"
            audio_metadata = await self.content_extractor.extract_audio_metadata(video_url)
            
            # Create standardized crawl result
            result = CrawlResult(
                url=video_url,
                platform=self.platform,
                content_type=ContentType.VIDEO.value,
                title=video_data.title,
                description=video_data.description,
                author=video_data.channel_title,
                upload_date=video_data.published_at,
                view_count=video_data.view_count,
                duration_ms=self._parse_duration_to_ms(video_data.duration),
                thumbnail_url=video_data.thumbnail_url,
                tags=video_data.tags,
                metadata={
                    'video_data': asdict(video_data),
                    'audio_metadata': audio_metadata,
                    'platform_specific': {
                        'video_id': video_id,
                        'channel_id': video_data.channel_id,
                        'category_id': video_data.category_id,
                        'privacy_status': video_data.privacy_status,
                        'live_status': video_data.live_status
                    }
                }
            )
            
            return result
            
        except Exception as e:
            logger.error(f"YouTube video crawl error {video_id}: {e}")
            return None
    
    async def search_similar_content(
        self,
        query: str,
        limit: int = 100,
        time_range: Optional[timedelta] = None
    ) -> List[CrawlResult]:
        """Search for potentially infringing content on YouTube."""        try:
            published_after = None
            if time_range:
                published_after = datetime.now() - time_range
            
            # Search for videos
            video_ids = await self.api_manager.search_videos(
                query=query,
                max_results=limit,
                published_after=published_after
            )
            
            # Crawl each video
            results = []
            for video_id in video_ids:
                result = await self.crawl_video(video_id)
                if result:
                    results.append(result)
                
                # Rate limiting
                await asyncio.sleep(0.1)
            
            return results
            
        except Exception as e:
            logger.error(f"YouTube search crawl error: {e}")
            return []
    
    async def monitor_channel(
        self,
        channel_id: str,
        check_period: timedelta = timedelta(hours=24)
    ) -> List[CrawlResult]:
        """Monitor a specific channel for new content."""        try:
            published_after = datetime.now() - check_period
            
            video_ids = await self.api_manager.get_channel_videos(
                channel_id=channel_id,
                published_after=published_after
            )
            
            results = []
            for video_id in video_ids:
                result = await self.crawl_video(video_id)
                if result:
                    results.append(result)
                
                await asyncio.sleep(0.1)
            
            return results
            
        except Exception as e:
            logger.error(f"Channel monitoring error {channel_id}: {e}")
            return []
    
    def _parse_duration_to_ms(self, duration: str) -> Optional[int]:
        """Convert ISO 8601 duration to milliseconds."""        try:
            # Parse ISO 8601 duration format (PT4M20S)
            import re
            pattern = r'PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?'
            match = re.match(pattern, duration)
            
            if not match:
                return None
            
            hours = int(match.group(1) or 0)
            minutes = int(match.group(2) or 0)
            seconds = int(match.group(3) or 0)
            
            total_ms = (hours * 3600 + minutes * 60 + seconds) * 1000
            return total_ms
            
        except Exception:
            return None

    async def get_content_for_fingerprinting(
        self,
        video_id: str
    ) -> Optional[str]:
        """Download audio sample for fingerprinting analysis."""        try:
            video_url = f"https://www.youtube.com/watch?v={video_id}"
            audio_path = await self.content_extractor.download_audio_sample(
                video_url=video_url,
                start_time=30,  # Skip intro
                duration=60     # 1 minute sample
            )
            
            return audio_path
            
        except Exception as e:
            logger.error(f"Fingerprinting content extraction error: {e}")
            return None
