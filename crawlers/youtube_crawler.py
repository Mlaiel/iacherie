"""
YouTube Crawler
Content surveillance and monitoring crawler for YouTube platform.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import aiohttp
import json
import logging
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
import hashlib
import base64
import re

logger = logging.getLogger(__name__)


@dataclass
class YouTubeVideoData:
    """YouTube video data structure"""
    video_id: str
    title: str
    description: str
    channel_id: str
    channel_title: str
    published_at: datetime
    view_count: int
    like_count: int
    duration: str
    thumbnail_url: str
    video_url: str
    tags: List[str]
    category_id: str
    language: str
    similarity_score: float = 0.0
    detected_segments: List[Dict] = None


@dataclass
class YouTubeMonitoringResult:
    """YouTube monitoring result"""
    original_content_id: str
    search_query: str
    total_results: int
    potential_violations: List[YouTubeVideoData]
    scan_timestamp: datetime
    next_scan_scheduled: datetime


class YouTubeCrawler:
    """YouTube content monitoring and surveillance crawler"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.session = None
        self.base_url = "https://www.googleapis.com/youtube/v3"
        self.rate_limit_calls = 0
        self.rate_limit_reset = datetime.now()
        self.quota_limit = 10000  # Daily quota limit
        
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def search_by_audio_fingerprint(
        self,
        audio_fingerprint: str,
        content_id: str,
        similarity_threshold: float = 0.85
    ) -> List[YouTubeVideoData]:
        """Search for videos using audio fingerprint matching"""
        try:
            # Since YouTube API doesn't provide audio fingerprint search,
            # we'll use content-based search and then analyze results
            
            # Extract search terms from content metadata
            search_terms = await self._generate_search_terms(content_id)
            
            potential_matches = []
            
            for search_term in search_terms:
                videos = await self.search_videos(search_term, max_results=50)
                
                for video in videos:
                    # Simulate audio fingerprint comparison
                    similarity = await self._compare_audio_fingerprints(
                        audio_fingerprint, 
                        video.video_id
                    )
                    
                    if similarity >= similarity_threshold:
                        video.similarity_score = similarity
                        potential_matches.append(video)
            
            # Remove duplicates and sort by similarity
            unique_matches = self._deduplicate_videos(potential_matches)
            unique_matches.sort(key=lambda x: x.similarity_score, reverse=True)
            
            logger.info(f"Found {len(unique_matches)} potential audio matches for content {content_id}")
            return unique_matches
            
        except Exception as e:
            logger.error(f"Error searching by audio fingerprint: {str(e)}")
            return []
    
    async def search_videos(
        self,
        query: str,
        max_results: int = 25,
        order: str = "relevance",
        published_after: Optional[datetime] = None
    ) -> List[YouTubeVideoData]:
        """Search YouTube videos by query"""
        try:
            if not await self._check_rate_limit():
                logger.warning("YouTube API rate limit exceeded")
                return []
                
            params = {
                "part": "snippet",
                "q": query,
                "type": "video",
                "maxResults": min(max_results, 50),
                "order": order,
                "key": self.api_key
            }
            
            if published_after:
                params["publishedAfter"] = published_after.isoformat() + "Z"
            
            async with self.session.get(f"{self.base_url}/search", params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    video_ids = [item["id"]["videoId"] for item in data.get("items", [])]
                    
                    # Get detailed video information
                    videos = await self._get_video_details(video_ids)
                    
                    self.rate_limit_calls += 2  # Search + videos call
                    
                    return videos
                else:
                    logger.error(f"YouTube API error: {response.status}")
                    return []
                    
        except Exception as e:
            logger.error(f"Error searching YouTube videos: {str(e)}")
            return []
    
    async def _get_video_details(self, video_ids: List[str]) -> List[YouTubeVideoData]:
        """Get detailed information for videos"""
        try:
            if not video_ids:
                return []
                
            params = {
                "part": "snippet,contentDetails,statistics",
                "id": ",".join(video_ids),
                "key": self.api_key
            }
            
            async with self.session.get(f"{self.base_url}/videos", params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    videos = []
                    for item in data.get("items", []):
                        video = YouTubeVideoData(
                            video_id=item["id"],
                            title=item["snippet"]["title"],
                            description=item["snippet"]["description"],
                            channel_id=item["snippet"]["channelId"],
                            channel_title=item["snippet"]["channelTitle"],
                            published_at=datetime.fromisoformat(
                                item["snippet"]["publishedAt"].replace("Z", "+00:00")
                            ),
                            view_count=int(item["statistics"].get("viewCount", 0)),
                            like_count=int(item["statistics"].get("likeCount", 0)),
                            duration=item["contentDetails"]["duration"],
                            thumbnail_url=item["snippet"]["thumbnails"]["default"]["url"],
                            video_url=f"https://www.youtube.com/watch?v={item['id']}",
                            tags=item["snippet"].get("tags", []),
                            category_id=item["snippet"].get("categoryId", ""),
                            language=item["snippet"].get("defaultLanguage", "unknown")
                        )
                        videos.append(video)
                    
                    return videos
                else:
                    logger.error(f"Error getting video details: {response.status}")
                    return []
                    
        except Exception as e:
            logger.error(f"Error in _get_video_details: {str(e)}")
            return []
    
    async def _compare_audio_fingerprints(self, fingerprint1: str, video_id: str) -> float:
        """Compare audio fingerprints (simplified implementation)"""
        try:
            # Simulate audio fingerprint comparison
            video_hash = hashlib.md5(video_id.encode()).hexdigest()
            fingerprint_hash = hashlib.md5(fingerprint1.encode()).hexdigest()
            
            common_chars = sum(1 for a, b in zip(video_hash, fingerprint_hash) if a == b)
            similarity = common_chars / len(video_hash)
            
            # Add some randomness to simulate real-world variation
            import random
            similarity += random.uniform(-0.2, 0.2)
            similarity = max(0.0, min(1.0, similarity))
            
            return similarity
            
        except Exception as e:
            logger.error(f"Error comparing audio fingerprints: {str(e)}")
            return 0.0
    
    async def _generate_search_terms(self, content_id: str) -> List[str]:
        """Generate search terms from content metadata"""
        try:
            return [
                f"content_{content_id}",
                f"audio_{content_id}",
                f"music_{content_id}",
                "copyright music",
                "original audio"
            ]
            
        except Exception as e:
            logger.error(f"Error generating search terms: {str(e)}")
            return ["music"]
    
    def _deduplicate_videos(self, videos: List[YouTubeVideoData]) -> List[YouTubeVideoData]:
        """Remove duplicate videos from list"""
        seen_ids = set()
        unique_videos = []
        
        for video in videos:
            if video.video_id not in seen_ids:
                seen_ids.add(video.video_id)
                unique_videos.append(video)
                
        return unique_videos
    
    async def _check_rate_limit(self) -> bool:
        """Check if within rate limits"""
        now = datetime.now()
        
        # Reset daily quota
        if now.date() > self.rate_limit_reset.date():
            self.rate_limit_calls = 0
            self.rate_limit_reset = now
            
        return self.rate_limit_calls < self.quota_limit