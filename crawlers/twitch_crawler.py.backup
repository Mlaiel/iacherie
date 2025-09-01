"""Twitch Crawler
==============

Professional Twitch content crawler for live streaming and gaming content monitoring.
Implements Twitch Helix API integration with advanced stream discovery.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: All rights reserved. Unauthorized use, reproduction, or distribution prohibited.

WARNING: This code is protected by copyright law. Any unauthorized copying, 
distribution, or modification is strictly prohibited and will result in 
legal action. Contact mlaiel@live.de for licensing.

Project Team Specialties:
- Lead Dev IA: Advanced AI integration and machine learning
- Backend Senior: Scalable architecture and microservices  
- ML Engineer: Content analysis and recommendation systems
- DBA: High-performance database optimization
- Security Expert: Enterprise-grade security and encryption
- Microservices Architect: Distributed systems design
- Audio Engineer: Advanced audio processing and analysis
- DevOps Engineer: CI/CD and infrastructure automation
- IA Prompt Engineer: Intelligent prompt optimization
"""
import asyncio
import logging
from typing import Dict, List, Optional, Union, AsyncGenerator
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
import json
import re

import aiohttp
import websockets
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options

from ..utils.rate_limiter import TwitchRateLimiter
from ..utils.proxy_manager import ProxyManager
from ..utils.user_agent_rotator import UserAgentRotator
from ..utils.content_analyzer import ContentAnalyzer
from ...core.config import get_settings
from ...core.exceptions import CrawlerError, RateLimitError
from ...database.models import CrawlResult, ContentMatch
from ...security.encryption import FieldEncryption

logger = logging.getLogger(__name__)
settings = get_settings()

@dataclass
class TwitchStream:
    """Twitch stream data structure."""
    stream_id: str
    user_id: str
    user_login: str
    user_name: str
    game_id: str
    game_name: str
    type: str  # live, playlist, watch_party, premiere, rerun
    title: str
    viewer_count: int
    started_at: datetime
    language: str
    thumbnail_url: str
    tag_ids: List[str]
    tags: List[str]
    is_mature: bool

@dataclass
class TwitchClip:
    """Twitch clip data structure."""
    clip_id: str
    url: str
    embed_url: str
    broadcaster_id: str
    broadcaster_name: str
    creator_id: str
    creator_name: str
    video_id: str
    game_id: str
    language: str
    title: str
    view_count: int
    created_at: datetime
    thumbnail_url: str
    duration: float
    vod_offset: Optional[int]

@dataclass
class TwitchVideo:
    """Twitch video/VOD data structure."""
    video_id: str
    stream_id: Optional[str]
    user_id: str
    user_login: str
    user_name: str
    title: str
    description: str
    created_at: datetime
    published_at: datetime
    url: str
    thumbnail_url: str
    viewable: str
    view_count: int
    language: str
    type: str  # upload, archive, highlight
    duration: str
    muted_segments: List[Dict]

@dataclass
class TwitchUser:
    """Twitch user/channel data structure."""
    user_id: str
    login: str
    display_name: str
    type: str  # staff, admin, global_mod, ""
    broadcaster_type: str  # partner, affiliate, ""
    description: str
    profile_image_url: str
    offline_image_url: str
    view_count: int
    created_at: datetime
    email: Optional[str]

class TwitchCrawler:
    """
    Professional Twitch crawler implementation.
    
    Features:
    - Twitch Helix API integration
    - Live stream monitoring
    - Clip and VOD discovery
    - Chat message extraction
    - Gaming content analysis
    - Streamer analytics
    - Real-time alerts
    - Content categorization
    - Audience engagement metrics
    - Gaming trend analysis
    """
    
    def __init__(self):
        """Initialize Twitch crawler."""
        self.client_id = settings.TWITCH_CLIENT_ID
        self.client_secret = settings.TWITCH_CLIENT_SECRET
        self.access_token = None
        self.rate_limiter = TwitchRateLimiter()
        self.proxy_manager = ProxyManager()
        self.user_agent_rotator = UserAgentRotator()
        self.content_analyzer = ContentAnalyzer()
        self.encryption = FieldEncryption()
        
        # API endpoints
        self.base_api_url = "https://api.twitch.tv/helix"
        self.oauth_url = "https://id.twitch.tv/oauth2/token"
        
        # Headers for API requests
        self.headers = {
            "Client-ID": self.client_id,
            "Content-Type": "application/json"
        }
        
        # WebSocket connection for real-time data
        self.websocket = None
        
        # Game categories
        self.game_categories = {
            "Just Chatting": "509658",
            "Music": "26936",
            "Art": "509660",
            "ASMR": "509659",
            "Talk Shows & Podcasts": "417752"
        }
    
    async def authenticate(self):
        """Authenticate with Twitch API using client credentials."""
        try:
            async with aiohttp.ClientSession() as session:
                auth_data = {
                    "client_id": self.client_id,
                    "client_secret": self.client_secret,
                    "grant_type": "client_credentials"
                }
                
                async with session.post(self.oauth_url, data=auth_data) as response:
                    if response.status == 200:
                        auth_response = await response.json()
                        self.access_token = auth_response["access_token"]
                        self.headers["Authorization"] = f"Bearer {self.access_token}"
                        logger.info("Twitch authentication successful")
                    else:
                        raise CrawlerError(f"Twitch authentication failed: {response.status}")
                        
        except Exception as e:
            logger.error(f"Error authenticating with Twitch: {e}")
            raise CrawlerError(f"Twitch authentication error: {e}")
    
    async def search_streams(
        self,
        game_name: Optional[str] = None,
        language: Optional[str] = None,
        max_results: int = 100
    ) -> AsyncGenerator[TwitchStream, None]:
        """
        Search live streams with filtering options.
        
        Args:
            game_name: Filter by game/category name
            language: Filter by language (e.g., 'en', 'es')
            max_results: Maximum number of results
            
        Yields:
            TwitchStream: Stream data
        """
        if not self.access_token:
            await self.authenticate()
        
        await self.rate_limiter.wait_if_needed("streams")
        
        try:
            params = {
                "first": min(max_results, 20)
            }
            
            if game_name:
                game_id = await self._get_game_id(game_name)
                if game_id:
                    params["game_id"] = game_id
            
            if language:
                params["language"] = language
            
            async with aiohttp.ClientSession() as session:
                url = f"{self.base_api_url}/streams"
                async with session.get(url, headers=self.headers, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        for stream_data in data.get("data", []):
                            stream = self._parse_stream_data(stream_data)
                            if stream:
                                yield stream
                    
                    elif response.status == 429:
                        raise RateLimitError("Twitch API rate limit exceeded")
                    else:
                        logger.error(f"Twitch API error: {response.status}")
                        
        except Exception as e:
            logger.error(f"Error searching Twitch streams: {e}")
            raise CrawlerError(f"Twitch stream search failed: {e}")
    
    async def monitor_channel(
        self,
        channel_name: str,
        check_interval: int = 300
    ) -> AsyncGenerator[TwitchStream, None]:
        """
        Monitor Twitch channel for live streams.
        
        Args:
            channel_name: Twitch channel username
            check_interval: Check interval in seconds
            
        Yields:
            TwitchStream: Live stream when channel goes live
        """
        if not self.access_token:
            await self.authenticate()
        
        user_id = await self._get_user_id(channel_name)
        if not user_id:
            raise CrawlerError(f"Channel not found: {channel_name}")
        
        last_stream_id = None
        
        while True:
            try:
                await self.rate_limiter.wait_if_needed("streams")
                
                async with aiohttp.ClientSession() as session:
                    url = f"{self.base_api_url}/streams"
                    params = {"user_id": user_id}
                    
                    async with session.get(url, headers=self.headers, params=params) as response:
                        if response.status == 200:
                            data = await response.json()
                            streams = data.get("data", [])
                            
                            if streams:
                                stream_data = streams[0]
                                current_stream_id = stream_data["id"]
                                
                                if current_stream_id != last_stream_id:
                                    stream = self._parse_stream_data(stream_data)
                                    if stream:
                                        yield stream
                                        last_stream_id = current_stream_id
                            else:
                                last_stream_id = None
                        
                        elif response.status == 429:
                            logger.warning("Rate limit hit, backing off")
                            await asyncio.sleep(300)
                
                await asyncio.sleep(check_interval)
                
            except Exception as e:
                logger.error(f"Error monitoring Twitch channel: {e}")
                await asyncio.sleep(60)
    
    async def get_channel_clips(
        self,
        channel_name: str,
        period: str = "week",
        max_results: int = 50
    ) -> List[TwitchClip]:
        """
        Get clips from Twitch channel.
        
        Args:
            channel_name: Twitch channel username
            period: Time period (day, week, month, all)
            max_results: Maximum number of clips
            
        Returns:
            List[TwitchClip]: Channel clips
        """
        if not self.access_token:
            await self.authenticate()
        
        user_id = await self._get_user_id(channel_name)
        if not user_id:
            raise CrawlerError(f"Channel not found: {channel_name}")
        
        await self.rate_limiter.wait_if_needed("clips")
        
        try:
            # Calculate date range
            end_date = datetime.now()
            if period == "day":
                start_date = end_date - timedelta(days=1)
            elif period == "week":
                start_date = end_date - timedelta(weeks=1)
            elif period == "month":
                start_date = end_date - timedelta(days=30)
            else:
                start_date = end_date - timedelta(days=365)
            
            params = {
                "broadcaster_id": user_id,
                "started_at": start_date.isoformat() + "Z",
                "ended_at": end_date.isoformat() + "Z",
                "first": min(max_results, 20)
            }
            
            async with aiohttp.ClientSession() as session:
                url = f"{self.base_api_url}/clips"
                async with session.get(url, headers=self.headers, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        clips = []
                        
                        for clip_data in data.get("data", []):
                            clip = self._parse_clip_data(clip_data)
                            if clip:
                                clips.append(clip)
                        
                        return clips
                    
                    elif response.status == 429:
                        raise RateLimitError("Twitch API rate limit exceeded")
                    else:
                        logger.error(f"Twitch API error: {response.status}")
                        return []
                        
        except Exception as e:
            logger.error(f"Error getting Twitch clips: {e}")
            raise CrawlerError(f"Twitch clips retrieval failed: {e}")
    
    async def get_channel_videos(
        self,
        channel_name: str,
        video_type: str = "all",
        max_results: int = 50
    ) -> List[TwitchVideo]:
        """
        Get videos/VODs from Twitch channel.
        
        Args:
            channel_name: Twitch channel username
            video_type: Type of videos (all, upload, archive, highlight)
            max_results: Maximum number of videos
            
        Returns:
            List[TwitchVideo]: Channel videos
        """
        if not self.access_token:
            await self.authenticate()
        
        user_id = await self._get_user_id(channel_name)
        if not user_id:
            raise CrawlerError(f"Channel not found: {channel_name}")
        
        await self.rate_limiter.wait_if_needed("videos")
        
        try:
            params = {
                "user_id": user_id,
                "first": min(max_results, 20)
            }
            
            if video_type != "all":
                params["type"] = video_type
            
            async with aiohttp.ClientSession() as session:
                url = f"{self.base_api_url}/videos"
                async with session.get(url, headers=self.headers, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        videos = []
                        
                        for video_data in data.get("data", []):
                            video = self._parse_video_data(video_data)
                            if video:
                                videos.append(video)
                        
                        return videos
                    
                    elif response.status == 429:
                        raise RateLimitError("Twitch API rate limit exceeded")
                    else:
                        logger.error(f"Twitch API error: {response.status}")
                        return []
                        
        except Exception as e:
            logger.error(f"Error getting Twitch videos: {e}")
            raise CrawlerError(f"Twitch videos retrieval failed: {e}")
    
    async def monitor_chat_realtime(
        self,
        channel_name: str
    ) -> AsyncGenerator[Dict, None]:
        """
        Monitor Twitch chat in real-time using IRC.
        
        Args:
            channel_name: Twitch channel to monitor
            
        Yields:
            Dict: Chat message data
        """
        try:
            import websockets
            
            # Connect to Twitch IRC WebSocket
            uri = "wss://irc-ws.chat.twitch.tv:443"
            
            async with websockets.connect(uri) as websocket:
                # Authenticate as anonymous user
                await websocket.send("CAP REQ :twitch.tv/tags twitch.tv/commands")
                await websocket.send("PASS SCHMOOPIIE")
                await websocket.send("NICK justinfan67420")
                await websocket.send(f"JOIN #{channel_name.lower()}")
                
                while True:
                    try:
                        message = await websocket.recv()
                        parsed_message = self._parse_irc_message(message)
                        
                        if parsed_message and parsed_message.get("command") == "PRIVMSG":
                            yield {
                                "channel": channel_name,
                                "username": parsed_message.get("username", ""),
                                "message": parsed_message.get("message", ""),
                                "timestamp": datetime.now(),
                                "tags": parsed_message.get("tags", {})
                            }
                    
                    except websockets.exceptions.ConnectionClosed:
                        logger.warning("Chat connection closed, reconnecting...")
                        break
                    except Exception as e:
                        logger.error(f"Error in chat monitoring: {e}")
                        await asyncio.sleep(1)
                        
        except Exception as e:
            logger.error(f"Error setting up chat monitoring: {e}")
    
    async def scrape_with_selenium(
        self,
        search_query: str,
        max_scroll: int = 3
    ) -> List[TwitchStream]:
        """
        Scrape Twitch using Selenium as fallback.
        
        Args:
            search_query: Search query
            max_scroll: Maximum number of scrolls
            
        Returns:
            List[TwitchStream]: Scraped streams
        """
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument(f"--user-agent={self.user_agent_rotator.get_random()}")
        
        if self.proxy_manager.get_current_proxy():
            proxy = self.proxy_manager.get_current_proxy()
            chrome_options.add_argument(f"--proxy-server={proxy}")
        
        driver = None
        streams = []
        
        try:
            driver = webdriver.Chrome(options=chrome_options)
            
            # Navigate to Twitch search
            search_url = f"https://www.twitch.tv/search?term={search_query}"
            driver.get(search_url)
            
            # Wait for content to load
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "[data-target='search-result-item']"))
            )
            
            # Scroll to load more content
            for _ in range(max_scroll):
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                await asyncio.sleep(2)
            
            # Extract stream elements
            stream_elements = driver.find_elements(By.CSS_SELECTOR, "[data-target='search-result-item']")
            
            for element in stream_elements:
                try:
                    stream_data = self._extract_stream_from_element(element)
                    if stream_data:
                        streams.append(stream_data)
                except Exception as e:
                    logger.debug(f"Error extracting stream: {e}")
                    continue
            
            return streams
            
        except Exception as e:
            logger.error(f"Error in Twitch Selenium scraping: {e}")
            return streams
            
        finally:
            if driver:
                driver.quit()
    
    async def _get_user_id(self, username: str) -> Optional[str]:
        """Get Twitch user ID from username."""
        try:
            async with aiohttp.ClientSession() as session:
                url = f"{self.base_api_url}/users"
                params = {"login": username.lower()}
                
                async with session.get(url, headers=self.headers, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        users = data.get("data", [])
                        if users:
                            return users[0]["id"]
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting user ID: {e}")
            return None
    
    async def _get_game_id(self, game_name: str) -> Optional[str]:
        """Get Twitch game ID from game name."""
        try:
            async with aiohttp.ClientSession() as session:
                url = f"{self.base_api_url}/games"
                params = {"name": game_name}
                
                async with session.get(url, headers=self.headers, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        games = data.get("data", [])
                        if games:
                            return games[0]["id"]
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting game ID: {e}")
            return None
    
    def _parse_stream_data(self, stream_data: Dict) -> Optional[TwitchStream]:
        """Parse Twitch stream data from API response."""
        try:
            return TwitchStream(
                stream_id=stream_data["id"],
                user_id=stream_data["user_id"],
                user_login=stream_data["user_login"],
                user_name=stream_data["user_name"],
                game_id=stream_data["game_id"],
                game_name=stream_data["game_name"],
                type=stream_data["type"],
                title=stream_data["title"],
                viewer_count=stream_data["viewer_count"],
                started_at=datetime.fromisoformat(stream_data["started_at"].replace("Z", "+00:00")),
                language=stream_data["language"],
                thumbnail_url=stream_data["thumbnail_url"],
                tag_ids=stream_data.get("tag_ids", []),
                tags=stream_data.get("tags", []),
                is_mature=stream_data.get("is_mature", False)
            )
            
        except Exception as e:
            logger.error(f"Error parsing stream data: {e}")
            return None
    
    def _parse_clip_data(self, clip_data: Dict) -> Optional[TwitchClip]:
        """Parse Twitch clip data from API response."""
        try:
            return TwitchClip(
                clip_id=clip_data["id"],
                url=clip_data["url"],
                embed_url=clip_data["embed_url"],
                broadcaster_id=clip_data["broadcaster_id"],
                broadcaster_name=clip_data["broadcaster_name"],
                creator_id=clip_data["creator_id"],
                creator_name=clip_data["creator_name"],
                video_id=clip_data["video_id"],
                game_id=clip_data["game_id"],
                language=clip_data["language"],
                title=clip_data["title"],
                view_count=clip_data["view_count"],
                created_at=datetime.fromisoformat(clip_data["created_at"].replace("Z", "+00:00")),
                thumbnail_url=clip_data["thumbnail_url"],
                duration=clip_data["duration"],
                vod_offset=clip_data.get("vod_offset")
            )
            
        except Exception as e:
            logger.error(f"Error parsing clip data: {e}")
            return None
    
    def _parse_video_data(self, video_data: Dict) -> Optional[TwitchVideo]:
        """Parse Twitch video data from API response."""
        try:
            return TwitchVideo(
                video_id=video_data["id"],
                stream_id=video_data.get("stream_id"),
                user_id=video_data["user_id"],
                user_login=video_data["user_login"],
                user_name=video_data["user_name"],
                title=video_data["title"],
                description=video_data["description"],
                created_at=datetime.fromisoformat(video_data["created_at"].replace("Z", "+00:00")),
                published_at=datetime.fromisoformat(video_data["published_at"].replace("Z", "+00:00")),
                url=video_data["url"],
                thumbnail_url=video_data["thumbnail_url"],
                viewable=video_data["viewable"],
                view_count=video_data["view_count"],
                language=video_data["language"],
                type=video_data["type"],
                duration=video_data["duration"],
                muted_segments=video_data.get("muted_segments", [])
            )
            
        except Exception as e:
            logger.error(f"Error parsing video data: {e}")
            return None
    
    def _parse_irc_message(self, message: str) -> Optional[Dict]:
        """Parse IRC message from Twitch chat."""
        try:
            if "PRIVMSG" not in message:
                return None
            
            parts = message.split(" ", 3)
            if len(parts) < 4:
                return None
            
            tags = {}
            prefix = ""
            
            # Parse tags if present
            if message.startswith("@"):
                tag_part, rest = message.split(" ", 1)
                for tag in tag_part[1:].split(";"):
                    if "=" in tag:
                        key, value = tag.split("=", 1)
                        tags[key] = value
                message = rest
            
            # Parse prefix and extract username
            if message.startswith(":"):
                prefix_part, rest = message.split(" ", 1)
                prefix = prefix_part[1:]
                username = prefix.split("!")[0] if "!" in prefix else prefix
                message = rest
            else:
                username = "unknown"
            
            # Extract message content
            msg_parts = message.split(" :", 1)
            if len(msg_parts) > 1:
                content = msg_parts[1].strip()
            else:
                content = ""
            
            return {
                "command": "PRIVMSG",
                "username": username,
                "message": content,
                "tags": tags
            }
            
        except Exception as e:
            logger.debug(f"Error parsing IRC message: {e}")
            return None
    
    def _extract_stream_from_element(self, element) -> Optional[TwitchStream]:
        """Extract stream data from Selenium web element."""
        try:
            # This would be implemented based on Twitch's current HTML structure
            title_element = element.find_element(By.CSS_SELECTOR, "[data-a-target='preview-card-title-link']")
            title = title_element.text if title_element else ""
            
            return TwitchStream(
                stream_id=f"scraped_{hash(title)}",
                user_id="",
                user_login="",
                user_name="",
                game_id="",
                game_name="",
                type="live",
                title=title,
                viewer_count=0,
                started_at=datetime.now(),
                language="en",
                thumbnail_url="",
                tag_ids=[],
                tags=[],
                is_mature=False
            )
            
        except Exception as e:
            logger.debug(f"Error extracting stream from element: {e}")
            return None
    
    async def close(self):
        """Clean up resources."""
        if self.websocket:
            await self.websocket.close()
        
        logger.info("Twitch crawler closed")

# Export for module
__all__ = ["TwitchCrawler", "TwitchStream", "TwitchClip", "TwitchVideo", "TwitchUser"]
