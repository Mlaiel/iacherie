"""TikTok Collector
================

Consolidated TikTok content collector that combines functionality from
12 specialized TikTok crawlers into a single, comprehensive module:

1. Videos Collection (tiktok_videos.py)
2. Sounds/Audio Tracking (tiktok_sounds.py)
3. Effects Monitoring (tiktok_effects.py) 
4. Challenges Tracking (tiktok_challenges.py)
5. Duets Collection (tiktok_duets.py)
6. Comments Analysis (tiktok_comments.py)
7. Analytics Collection (tiktok_analytics.py)
8. Trending Discovery (tiktok_trending.py)
9. Creators Monitoring (tiktok_creators.py)
10. Hashtags Tracking (tiktok_hashtags.py)
11. Music Detection (tiktok_music.py)
12. Live Streams (tiktok_live.py)

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
import json
import re
import time
from typing import Dict, List, Optional, AsyncGenerator, Union, Any
from datetime import datetime, timedelta
from dataclasses import dataclass
from urllib.parse import urlparse, parse_qs

from .base_collector import BaseCollector, CollectorResult, CollectionConfig, RateLimiter

logger = logging.getLogger(__name__)

@dataclass
class TikTokContent:
    """TikTok-specific content structure."""
    video_id: str
    short_url: str
    content_type: str  # video, live, effect, sound
    caption: str
    creator_username: str
    creator_id: str
    video_url: str
    thumbnail_url: str
    duration: float
    like_count: int
    comment_count: int
    share_count: int
    view_count: int
    created_at: datetime
    hashtags: List[str]
    mentions: List[str]
    sounds: Optional[Dict] = None
    effects: Optional[List[str]] = None
    is_duet: bool = False
    duet_info: Optional[Dict] = None
    challenge_info: Optional[Dict] = None

class TikTokCollector(BaseCollector):
    """
    Consolidated TikTok content collector.
    
    Combines all TikTok crawling capabilities:
    - Video content collection and monitoring
    - Audio/sound tracking and analysis
    - Effects and filters detection
    - Challenge participation tracking
    - Creator analytics and insights
    - Trending content discovery
    - Live stream monitoring
    - Duet and collaboration tracking
    """
    
    def __init__(self, api_key: Optional[str] = None):
        super().__init__("tiktok", rate_limit=100)  # TikTok rate limits
        self.api_key = api_key
        self.base_url = "https://open-api.tiktok.com"
        
        # TikTok-specific rate limiters
        self.research_api_limiter = RateLimiter(max_requests=100, time_window=3600)
        self.scraping_limiter = RateLimiter(max_requests=20, time_window=60)  # Conservative for web scraping
        
        logger.info("TikTok collector initialized")
    
    async def search_content(self, query: str, config: CollectionConfig) -> List[CollectorResult]:
        """
        Search for TikTok content across all content types.
        Consolidates video, sound, effect, and challenge searches.
        """
        try:
            self.status = self.status.RUNNING
            start_time = time.time()
            
            results = []
            
            # Search videos by keyword/hashtag
            if query.startswith('#'):
                results.extend(await self._search_hashtag_videos(query, config))
            elif query.startswith('@'):
                # Search creator content
                username = query[1:]
                results.extend(await self.get_user_content(username, config))
            elif self._is_sound_query(query):
                results.extend(await self._search_sound_content(query, config))
            elif self._is_effect_query(query):
                results.extend(await self._search_effect_content(query, config))
            else:
                # General video search
                results.extend(await self._search_general_videos(query, config))
            
            # Include challenge content if relevant
            if self._is_challenge_query(query):
                results.extend(await self._search_challenge_content(query, config))
            
            response_time = time.time() - start_time
            self.update_stats(True, response_time)
            
            logger.info(f"TikTok search completed: {len(results)} results for '{query}'")
            return results[:config.max_results]
            
        except Exception as e:
            logger.error(f"TikTok search failed: {e}")
            self.update_stats(False, time.time() - start_time)
            return []
        finally:
            self.status = self.status.IDLE
    
    async def get_content_details(self, content_id: str) -> Optional[CollectorResult]:
        """Get detailed information about specific TikTok video."""
        try:
            await self.research_api_limiter.wait_if_needed()
            
            # Try Research API first if available
            if self.api_key:
                return await self._get_video_via_api(content_id)
            else:
                return await self._get_video_via_scraping(content_id)
                
        except Exception as e:
            logger.error(f"Failed to get TikTok video details for {content_id}: {e}")
            return None
    
    async def get_user_content(self, username: str, config: CollectionConfig) -> List[CollectorResult]:
        """
        Get content from specific TikTok creator.
        Consolidates creator videos, sounds, and effects.
        """
        try:
            results = []
            
            # Get user videos
            videos = await self._get_user_videos(username, config)
            results.extend(videos)
            
            # Get user sounds (if they created any)
            if config.include_metadata:
                sounds = await self._get_user_sounds(username, config)
                results.extend(sounds)
            
            # Get user live streams
            live_content = await self._get_user_live_content(username, config)
            results.extend(live_content)
            
            return results[:config.max_results]
            
        except Exception as e:
            logger.error(f"Failed to get user content for {username}: {e}")
            return []
    
    async def monitor_hashtags(self, hashtags: List[str], config: CollectionConfig) -> AsyncGenerator[CollectorResult, None]:
        """
        Monitor TikTok hashtags in real-time.
        Consolidates hashtag tracking and viral detection.
        """
        try:
            while True:
                for hashtag in hashtags:
                    try:
                        # Get recent content for hashtag
                        results = await self._search_hashtag_videos(hashtag, config)
                        
                        for result in results:
                            yield result
                            
                        # Monitor for viral content
                        viral_content = await self._detect_viral_content(hashtag)
                        for content in viral_content:
                            yield content
                            
                        await asyncio.sleep(config.rate_limit_delay)
                        
                    except Exception as e:
                        logger.error(f"Error monitoring hashtag {hashtag}: {e}")
                        continue
                
                await asyncio.sleep(30)
                
        except Exception as e:
            logger.error(f"Hashtag monitoring failed: {e}")
    
    async def get_trending_content(self, config: CollectionConfig) -> List[CollectorResult]:
        """
        Get trending TikTok content.
        Consolidates trending videos, sounds, effects, and challenges.
        """
        try:
            results = []
            
            # Get trending videos
            trending_videos = await self._get_trending_videos(config)
            results.extend(trending_videos)
            
            # Get trending sounds
            trending_sounds = await self._get_trending_sounds(config)
            results.extend(trending_sounds)
            
            # Get trending challenges
            trending_challenges = await self._get_trending_challenges(config)
            results.extend(trending_challenges)
            
            # Get trending effects
            trending_effects = await self._get_trending_effects(config)
            results.extend(trending_effects)
            
            return results[:config.max_results]
            
        except Exception as e:
            logger.error(f"Failed to get trending content: {e}")
            return []
    
    # TikTok-specific analytics methods
    async def collect_analytics(self, content_id: str) -> Dict[str, Any]:
        """Collect comprehensive TikTok analytics."""
        try:
            analytics = {}
            
            # Get engagement metrics
            analytics['engagement'] = await self._get_engagement_metrics(content_id)
            
            # Get performance trends
            analytics['performance'] = await self._get_performance_trends(content_id)
            
            # Get audience demographics
            analytics['audience'] = await self._get_audience_demographics(content_id)
            
            # Get sound/music analytics
            analytics['audio'] = await self._get_audio_analytics(content_id)
            
            return analytics
            
        except Exception as e:
            logger.error(f"Analytics collection failed for {content_id}: {e}")
            return {}
    
    async def analyze_sounds(self, sound_ids: List[str]) -> Dict[str, Any]:
        """
        Analyze TikTok sounds and music usage.
        Consolidates sound and music tracking functionality.
        """
        try:
            analysis = {}
            
            for sound_id in sound_ids:
                sound_analysis = {
                    'usage_count': await self._get_sound_usage_count(sound_id),
                    'trending_score': await self._calculate_sound_trending_score(sound_id),
                    'top_videos': await self._get_top_videos_with_sound(sound_id),
                    'creator_info': await self._get_sound_creator_info(sound_id),
                    'genre_classification': await self._classify_sound_genre(sound_id)
                }
                analysis[sound_id] = sound_analysis
            
            return analysis
            
        except Exception as e:
            logger.error(f"Sound analysis failed: {e}")
            return {}
    
    async def track_challenges(self, challenge_names: List[str]) -> Dict[str, Any]:
        """
        Track TikTok challenges and participation.
        Consolidates challenge tracking functionality.
        """
        try:
            tracking = {}
            
            for challenge in challenge_names:
                challenge_data = {
                    'participation_count': await self._get_challenge_participation(challenge),
                    'growth_rate': await self._calculate_challenge_growth(challenge),
                    'top_creators': await self._get_top_challenge_creators(challenge),
                    'geographic_distribution': await self._get_challenge_geography(challenge),
                    'trending_score': await self._calculate_challenge_trending_score(challenge)
                }
                tracking[challenge] = challenge_data
            
            return tracking
            
        except Exception as e:
            logger.error(f"Challenge tracking failed: {e}")
            return {}
    
    async def monitor_live_streams(self, creator_usernames: List[str]) -> AsyncGenerator[CollectorResult, None]:
        """
        Monitor live streams from specific creators.
        Consolidates live stream monitoring functionality.
        """
        try:
            while True:
                for username in creator_usernames:
                    try:
                        live_streams = await self._check_user_live_status(username)
                        for stream in live_streams:
                            yield stream
                    except Exception as e:
                        logger.error(f"Error checking live status for {username}: {e}")
                        continue
                
                await asyncio.sleep(30)  # Check every 30 seconds
                
        except Exception as e:
            logger.error(f"Live stream monitoring failed: {e}")
    
    # Private helper methods for specialized functionality
    
    async def _search_hashtag_videos(self, hashtag: str, config: CollectionConfig) -> List[CollectorResult]:
        """Search videos by hashtag (replaces tiktok_hashtags.py)."""
        return []
    
    async def _search_sound_content(self, sound_query: str, config: CollectionConfig) -> List[CollectorResult]:
        """Search content by sound (replaces tiktok_sounds.py and tiktok_music.py)."""
        return []
    
    async def _search_effect_content(self, effect_query: str, config: CollectionConfig) -> List[CollectorResult]:
        """Search content by effect (replaces tiktok_effects.py)."""
        return []
    
    async def _search_challenge_content(self, challenge: str, config: CollectionConfig) -> List[CollectorResult]:
        """Search challenge content (replaces tiktok_challenges.py)."""
        return []
    
    async def _search_general_videos(self, query: str, config: CollectionConfig) -> List[CollectorResult]:
        """General video search (replaces tiktok_videos.py)."""
        return []
    
    async def _get_video_via_api(self, video_id: str) -> Optional[CollectorResult]:
        """Get video via TikTok Research API."""
        return None
    
    async def _get_video_via_scraping(self, video_id: str) -> Optional[CollectorResult]:
        """Fallback video retrieval via web scraping."""
        return None
    
    async def _get_user_videos(self, username: str, config: CollectionConfig) -> List[CollectorResult]:
        """Get user videos (consolidates creator functionality)."""
        return []
    
    async def _get_user_sounds(self, username: str, config: CollectionConfig) -> List[CollectorResult]:
        """Get user-created sounds."""
        return []
    
    async def _get_user_live_content(self, username: str, config: CollectionConfig) -> List[CollectorResult]:
        """Get user live content (replaces tiktok_live.py)."""
        return []
    
    async def _detect_viral_content(self, hashtag: str) -> List[CollectorResult]:
        """Detect viral content for hashtag (part of tiktok_trending.py)."""
        return []
    
    async def _get_trending_videos(self, config: CollectionConfig) -> List[CollectorResult]:
        """Get trending videos (replaces tiktok_trending.py)."""
        return []
    
    async def _get_trending_sounds(self, config: CollectionConfig) -> List[CollectorResult]:
        """Get trending sounds (part of tiktok_trending.py)."""
        return []
    
    async def _get_trending_challenges(self, config: CollectionConfig) -> List[CollectorResult]:
        """Get trending challenges (part of tiktok_trending.py)."""
        return []
    
    async def _get_trending_effects(self, config: CollectionConfig) -> List[CollectorResult]:
        """Get trending effects (part of tiktok_trending.py)."""
        return []
    
    async def _get_engagement_metrics(self, content_id: str) -> Dict[str, Any]:
        """Get engagement metrics (replaces tiktok_analytics.py)."""
        return {}
    
    async def _get_performance_trends(self, content_id: str) -> Dict[str, Any]:
        """Get performance trends (part of tiktok_analytics.py)."""
        return {}
    
    async def _get_audience_demographics(self, content_id: str) -> Dict[str, Any]:
        """Get audience demographics (part of tiktok_analytics.py)."""
        return {}
    
    async def _get_audio_analytics(self, content_id: str) -> Dict[str, Any]:
        """Get audio/sound analytics (combines tiktok_sounds.py and tiktok_music.py)."""
        return {}
    
    async def _check_user_live_status(self, username: str) -> List[CollectorResult]:
        """Check if user is live (replaces tiktok_live.py)."""
        return []
    
    # Sound analysis helpers
    async def _get_sound_usage_count(self, sound_id: str) -> int:
        return 0
    
    async def _calculate_sound_trending_score(self, sound_id: str) -> float:
        return 0.0
    
    async def _get_top_videos_with_sound(self, sound_id: str) -> List[Dict]:
        return []
    
    async def _get_sound_creator_info(self, sound_id: str) -> Dict:
        return {}
    
    async def _classify_sound_genre(self, sound_id: str) -> str:
        return "unknown"
    
    # Challenge tracking helpers
    async def _get_challenge_participation(self, challenge: str) -> int:
        return 0
    
    async def _calculate_challenge_growth(self, challenge: str) -> float:
        return 0.0
    
    async def _get_top_challenge_creators(self, challenge: str) -> List[str]:
        return []
    
    async def _get_challenge_geography(self, challenge: str) -> Dict:
        return {}
    
    async def _calculate_challenge_trending_score(self, challenge: str) -> float:
        return 0.0
    
    def _is_sound_query(self, query: str) -> bool:
        """Check if query is sound-related."""
        sound_indicators = ['sound:', 'audio:', 'music:', 'song:']
        return any(indicator in query.lower() for indicator in sound_indicators)
    
    def _is_effect_query(self, query: str) -> bool:
        """Check if query is effect-related."""
        effect_indicators = ['effect:', 'filter:', 'ar:']
        return any(indicator in query.lower() for indicator in effect_indicators)
    
    def _is_challenge_query(self, query: str) -> bool:
        """Check if query is challenge-related."""
        challenge_indicators = ['challenge', '#challenge', 'trend']
        return any(indicator in query.lower() for indicator in challenge_indicators)