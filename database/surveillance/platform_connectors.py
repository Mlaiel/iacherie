"""
Platform Connectors Module
==========================

Platform-specific connectors for surveillance monitoring.
Provides specialized integration with major social media and content platforms.

Author: Fahed Mlaiel (mlaiel@live.de)
© 2025 Fahed Mlaiel. All Rights Reserved.
"""

import asyncio
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from abc import ABC, abstractmethod
from enum import Enum
import aiohttp
import json
import hashlib
from dataclasses import dataclass

logger = logging.getLogger(__name__)


class PlatformType(Enum):
    """Platform type enumeration."""
    SOCIAL_MEDIA = "social_media"
    VIDEO_PLATFORM = "video_platform"
    MUSIC_PLATFORM = "music_platform"
    IMAGE_PLATFORM = "image_platform"
    GENERIC_WEB = "generic_web"


class ConnectionStatus(Enum):
    """Connection status enumeration."""
    CONNECTED = "connected"
    DISCONNECTED = "disconnected"
    AUTHENTICATING = "authenticating"
    ERROR = "error"
    RATE_LIMITED = "rate_limited"


@dataclass
class SearchResult:
    """Search result data structure."""
    platform: str
    url: str
    title: str
    description: str
    content_type: str
    upload_date: datetime
    author: str
    view_count: Optional[int]
    metadata: Dict[str, Any]
    similarity_indicators: Dict[str, Any]


@dataclass
class PlatformCredentials:
    """Platform credentials structure."""
    api_key: Optional[str] = None
    api_secret: Optional[str] = None
    access_token: Optional[str] = None
    refresh_token: Optional[str] = None
    oauth_tokens: Optional[Dict[str, str]] = None


class BasePlatformConnector(ABC):
    """Base class for platform connectors."""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.platform_name = config.get("platform_name", "unknown")
        self.platform_type = PlatformType(config.get("platform_type", "generic_web"))
        self.credentials = PlatformCredentials(**config.get("credentials", {}))
        self.rate_limits = config.get("rate_limits", {})
        self.status = ConnectionStatus.DISCONNECTED
        self.session: Optional[aiohttp.ClientSession] = None
        
        # Rate limiting
        self.request_count = 0
        self.last_request_time = None
        self.rate_limit_reset_time = None
        
    @abstractmethod
    async def initialize(self) -> bool:
        """Initialize platform connector."""
        pass
    
    @abstractmethod
    async def authenticate(self) -> bool:
        """Authenticate with platform."""
        pass
    
    @abstractmethod
    async def search_similar_content(self, 
                                   fingerprint_hash: str,
                                   content_type: str,
                                   metadata: Dict[str, Any]) -> List[SearchResult]:
        """Search for similar content on platform."""
        pass
    
    @abstractmethod
    async def get_content_metadata(self, content_url: str) -> Dict[str, Any]:
        """Get metadata for specific content."""
        pass
    
    async def _check_rate_limits(self) -> bool:
        """Check if request is allowed based on rate limits."""
        if not self.rate_limits:
            return True
        
        now = datetime.utcnow()
        
        # Check if we're in a rate limit reset period
        if self.rate_limit_reset_time and now < self.rate_limit_reset_time:
            return False
        
        # Check requests per minute limit
        requests_per_minute = self.rate_limits.get("requests_per_minute", 100)
        if self.last_request_time:
            time_since_last = (now - self.last_request_time).total_seconds()
            if time_since_last < 60 and self.request_count >= requests_per_minute:
                return False
        
        return True
    
    async def _record_request(self) -> None:
        """Record API request for rate limiting."""
        now = datetime.utcnow()
        
        if self.last_request_time:
            time_since_last = (now - self.last_request_time).total_seconds()
            if time_since_last >= 60:
                self.request_count = 0
        
        self.request_count += 1
        self.last_request_time = now
    
    async def _make_request(self, 
                          method: str,
                          url: str,
                          headers: Optional[Dict[str, str]] = None,
                          params: Optional[Dict[str, Any]] = None,
                          data: Optional[Dict[str, Any]] = None) -> Optional[Dict[str, Any]]:
        """Make HTTP request with rate limiting and error handling."""
        if not await self._check_rate_limits():
            logger.warning(f"Rate limit exceeded for {self.platform_name}")
            self.status = ConnectionStatus.RATE_LIMITED
            return None
        
        try:
            if not self.session:
                self.session = aiohttp.ClientSession()
            
            await self._record_request()
            
            async with self.session.request(
                method=method,
                url=url,
                headers=headers,
                params=params,
                json=data
            ) as response:
                if response.status == 200:
                    return await response.json()
                elif response.status == 429:  # Rate limited
                    self.status = ConnectionStatus.RATE_LIMITED
                    retry_after = response.headers.get("Retry-After", "60")
                    self.rate_limit_reset_time = datetime.utcnow() + timedelta(seconds=int(retry_after))
                    logger.warning(f"Rate limited by {self.platform_name}, retry after {retry_after}s")
                elif response.status == 401:  # Unauthorized
                    self.status = ConnectionStatus.ERROR
                    logger.error(f"Authentication failed for {self.platform_name}")
                    await self.authenticate()  # Try to re-authenticate
                else:
                    logger.error(f"Request failed for {self.platform_name}: {response.status}")
                
                return None
                
        except Exception as e:
            logger.error(f"Request error for {self.platform_name}: {e}")
            self.status = ConnectionStatus.ERROR
            return None
    
    async def get_status(self) -> Dict[str, Any]:
        """Get connector status."""



        return {
            "platform": self.platform_name,
            "platform_type": self.platform_type.value,
            "status": self.status.value,
            "request_count": self.request_count,
            "last_request": self.last_request_time.isoformat() if self.last_request_time else None,
            "rate_limit_reset": self.rate_limit_reset_time.isoformat() if self.rate_limit_reset_time else None
        }
    
    async def shutdown(self) -> None:
        """Shutdown connector."""
        if self.session:
            await self.session.close()
        self.status = ConnectionStatus.DISCONNECTED
        logger.info(f"{self.platform_name} connector shutdown")


class YouTubeConnector(BasePlatformConnector):
    """
    YouTube platform connector.
    
    Integrates with YouTube Data API for content monitoring
    and similarity detection.
    """
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.api_base_url = "https://www.googleapis.com/youtube/v3"
        self.search_quota_cost = 100  # YouTube API quota cost for search
        
    async def initialize(self) -> bool:
        """Initialize YouTube connector."""



        try:
            if not self.credentials.api_key:
                logger.error("YouTube API key not provided")
                return False
            
            # Test API connection
            test_result = await self.authenticate()
            if test_result:
                self.status = ConnectionStatus.CONNECTED
                logger.info("YouTube connector initialized successfully")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Failed to initialize YouTube connector: {e}")
            self.status = ConnectionStatus.ERROR
            return False
    
    async def authenticate(self) -> bool:
        """Authenticate with YouTube API."""



        try:
            # Test API key with a simple request
            test_url = f"{self.api_base_url}/search"
            headers = {"Accept": "application/json"}
            params = {
                "key": self.credentials.api_key,
                "part": "snippet",
                "q": "test",
                "maxResults": 1,
                "type": "video"
            }
            
            response = await self._make_request("GET", test_url, headers=headers, params=params)
            
            if response:
                logger.info("YouTube authentication successful")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"YouTube authentication failed: {e}")
            return False
    
    async def search_similar_content(self, 
                                   fingerprint_hash: str,
                                   content_type: str,
                                   metadata: Dict[str, Any]) -> List[SearchResult]:
        """Search for similar content on YouTube."""



        try:
            if self.status != ConnectionStatus.CONNECTED:
                logger.warning("YouTube connector not connected")
                return []
            
            search_results = []
            
            # Build search queries from metadata
            search_queries = self._build_search_queries(metadata)
            
            for query in search_queries:
                # Search YouTube
                youtube_results = await self._search_youtube(query, content_type)
                
                for result in youtube_results:
                    # Calculate similarity indicators
                    similarity_indicators = await self._calculate_similarity_indicators(
                        result, fingerprint_hash, metadata
                    )
                    
                    search_result = SearchResult(
                        platform="youtube",
                        url=f"https://www.youtube.com/watch?v={result['id']['videoId']}",
                        title=result['snippet']['title'],
                        description=result['snippet']['description'],
                        content_type="video",
                        upload_date=datetime.fromisoformat(result['snippet']['publishedAt'].replace('Z', '+00:00')),
                        author=result['snippet']['channelTitle'],
                        view_count=None,  # Requires additional API call
                        metadata=result,
                        similarity_indicators=similarity_indicators
                    )
                    
                    search_results.append(search_result)
            
            logger.info(f"Found {len(search_results)} potential matches on YouTube")
            return search_results
            
        except Exception as e:
            logger.error(f"Error searching YouTube for similar content: {e}")
            return []
    
    def _build_search_queries(self, metadata: Dict[str, Any]) -> List[str]:
        """Build search queries from content metadata."""
        queries = []
        
        # Use title if available
        if metadata.get("title"):
            queries.append(metadata["title"])
        
        # Use artist/author if available
        if metadata.get("artist"):
            queries.append(metadata["artist"])
        
        # Use keywords if available
        if metadata.get("keywords"):
            keywords = metadata["keywords"]
            if isinstance(keywords, list):
                queries.extend(keywords[:3])  # Limit to first 3 keywords
            elif isinstance(keywords, str):
                queries.append(keywords)
        
        # Use description fragments
        if metadata.get("description"):
            description = metadata["description"]
            if len(description) > 50:
                # Extract meaningful phrases
                words = description.split()
                if len(words) > 10:
                    phrases = [" ".join(words[i:i+3]) for i in range(0, min(len(words), 15), 3)]
                    queries.extend(phrases[:3])
        
        return queries[:5]  # Limit to 5 queries to manage API quota
    
    async def _search_youtube(self, query: str, content_type: str) -> List[Dict[str, Any]]:
        """Search YouTube for specific query."""



        try:
            search_url = f"{self.api_base_url}/search"
            headers = {"Accept": "application/json"}
            params = {
                "key": self.credentials.api_key,
                "part": "snippet",
                "q": query,
                "maxResults": 10,
                "type": "video",
                "order": "relevance"
            }
            
            # Add content type specific filters
            if content_type == "audio":
                params["videoCategoryId"] = "10"  # Music category
            
            response = await self._make_request("GET", search_url, headers=headers, params=params)
            
            if response and "items" in response:
                return response["items"]
            
            return []
            
        except Exception as e:
            logger.error(f"Error searching YouTube with query '{query}': {e}")
            return []
    
    async def _calculate_similarity_indicators(self, 
                                             youtube_result: Dict[str, Any],
                                             fingerprint_hash: str,
                                             original_metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate similarity indicators between YouTube result and original content."""
        indicators = {
            "title_similarity": 0.0,
            "description_similarity": 0.0,
            "author_similarity": 0.0,
            "temporal_proximity": 0.0,
            "overall_confidence": 0.0
        }
        
        try:
            # Title similarity
            original_title = original_metadata.get("title", "")
            youtube_title = youtube_result["snippet"]["title"]
            indicators["title_similarity"] = self._calculate_text_similarity(original_title, youtube_title)
            
            # Description similarity
            original_desc = original_metadata.get("description", "")
            youtube_desc = youtube_result["snippet"]["description"]
            indicators["description_similarity"] = self._calculate_text_similarity(original_desc, youtube_desc)
            
            # Author similarity
            original_author = original_metadata.get("artist", original_metadata.get("author", ""))
            youtube_author = youtube_result["snippet"]["channelTitle"]
            indicators["author_similarity"] = self._calculate_text_similarity(original_author, youtube_author)
            
            # Temporal proximity (how close the upload dates are)
            if original_metadata.get("creation_date"):
                original_date = datetime.fromisoformat(original_metadata["creation_date"])
                youtube_date = datetime.fromisoformat(youtube_result["snippet"]["publishedAt"].replace('Z', '+00:00'))
                
                time_diff = abs((youtube_date - original_date).days)
                if time_diff <= 7:
                    indicators["temporal_proximity"] = 1.0
                elif time_diff <= 30:
                    indicators["temporal_proximity"] = 0.7
                elif time_diff <= 90:
                    indicators["temporal_proximity"] = 0.3
                else:
                    indicators["temporal_proximity"] = 0.1
            
            # Calculate overall confidence
            weights = {
                "title_similarity": 0.4,
                "description_similarity": 0.3,
                "author_similarity": 0.2,
                "temporal_proximity": 0.1
            }
            
            indicators["overall_confidence"] = sum(
                indicators[key] * weight for key, weight in weights.items()
            )
            
        except Exception as e:
            logger.error(f"Error calculating similarity indicators: {e}")
        
        return indicators
    
    def _calculate_text_similarity(self, text1: str, text2: str) -> float:
        """Calculate text similarity using simple word overlap."""
        if not text1 or not text2:
            return 0.0
        
        # Simple word-based similarity
        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())
        
        if not words1 or not words2:
            return 0.0
        
        intersection = len(words1.intersection(words2))
        union = len(words1.union(words2))
        
        return intersection / union if union > 0 else 0.0
    
    async def get_content_metadata(self, content_url: str) -> Dict[str, Any]:
        """Get metadata for specific YouTube video."""



        try:
            # Extract video ID from URL
            video_id = self._extract_video_id(content_url)
            if not video_id:
                return {}
            
            # Get video details
            details_url = f"{self.api_base_url}/videos"
            headers = {"Accept": "application/json"}
            params = {
                "key": self.credentials.api_key,
                "part": "snippet,statistics,contentDetails",
                "id": video_id
            }
            
            response = await self._make_request("GET", details_url, headers=headers, params=params)
            
            if response and "items" in response and response["items"]:
                video_data = response["items"][0]
                
                return {
                    "platform": "youtube",
                    "video_id": video_id,
                    "title": video_data["snippet"]["title"],
                    "description": video_data["snippet"]["description"],
                    "channel": video_data["snippet"]["channelTitle"],
                    "upload_date": video_data["snippet"]["publishedAt"],
                    "view_count": video_data["statistics"].get("viewCount"),
                    "like_count": video_data["statistics"].get("likeCount"),
                    "duration": video_data["contentDetails"]["duration"],
                    "raw_data": video_data
                }
            
            return {}
            
        except Exception as e:
            logger.error(f"Error getting YouTube content metadata: {e}")
            return {}
    
    def _extract_video_id(self, url: str) -> Optional[str]:
        """Extract video ID from YouTube URL."""



        try:
            if "youtube.com/watch?v=" in url:
                return url.split("v=")[1].split("&")[0]
            elif "youtu.be/" in url:
                return url.split("youtu.be/")[1].split("?")[0]
            return None
        except Exception:
            return None


class InstagramConnector(BasePlatformConnector):
    """
    Instagram platform connector.
    
    Integrates with Instagram Basic Display API for content monitoring.
    """
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.api_base_url = "https://graph.instagram.com"
        
    async def initialize(self) -> bool:
        """Initialize Instagram connector."""



        try:
            if not self.credentials.access_token:
                logger.error("Instagram access token not provided")
                return False
            
            test_result = await self.authenticate()
            if test_result:
                self.status = ConnectionStatus.CONNECTED
                logger.info("Instagram connector initialized successfully")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Failed to initialize Instagram connector: {e}")
            self.status = ConnectionStatus.ERROR
            return False
    
    async def authenticate(self) -> bool:
        """Authenticate with Instagram API."""



        try:
            # Test access token
            test_url = f"{self.api_base_url}/me"
            headers = {"Accept": "application/json"}
            params = {
                "access_token": self.credentials.access_token,
                "fields": "id,username"
            }
            
            response = await self._make_request("GET", test_url, headers=headers, params=params)
            
            if response:
                logger.info("Instagram authentication successful")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Instagram authentication failed: {e}")
            return False
    
    async def search_similar_content(self, 
                                   fingerprint_hash: str,
                                   content_type: str,
                                   metadata: Dict[str, Any]) -> List[SearchResult]:
        """Search for similar content on Instagram."""



        try:
            # Instagram Basic Display API has limited search capabilities
            # This would typically require Instagram Graph API with business account
            logger.info("Instagram content search requires Graph API with business permissions")
            return []
            
        except Exception as e:
            logger.error(f"Error searching Instagram for similar content: {e}")
            return []
    
    async def get_content_metadata(self, content_url: str) -> Dict[str, Any]:
        """Get metadata for specific Instagram content."""



        try:
            # Extract media ID from URL and get details
            # This is a simplified implementation
            return {
                "platform": "instagram",
                "url": content_url,
                "metadata_available": False,
                "note": "Full metadata requires Instagram Graph API"
            }
            
        except Exception as e:
            logger.error(f"Error getting Instagram content metadata: {e}")
            return {}


class TikTokConnector(BasePlatformConnector):
    """
    TikTok platform connector.
    
    Integrates with TikTok API for content monitoring.
    """
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.api_base_url = "https://open-api.tiktok.com"
        
    async def initialize(self) -> bool:
        """Initialize TikTok connector."""



        try:
            if not self.credentials.api_key:
                logger.error("TikTok API key not provided")
                return False
            
            test_result = await self.authenticate()
            if test_result:
                self.status = ConnectionStatus.CONNECTED
                logger.info("TikTok connector initialized successfully")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Failed to initialize TikTok connector: {e}")
            self.status = ConnectionStatus.ERROR
            return False
    
    async def authenticate(self) -> bool:
        """Authenticate with TikTok API."""



        try:
            # TikTok API authentication implementation
            logger.info("TikTok authentication - implementation required")
            return True  # Placeholder
            
        except Exception as e:
            logger.error(f"TikTok authentication failed: {e}")
            return False
    
    async def search_similar_content(self, 
                                   fingerprint_hash: str,
                                   content_type: str,
                                   metadata: Dict[str, Any]) -> List[SearchResult]:
        """Search for similar content on TikTok."""



        try:
            # TikTok content search implementation
            logger.info("TikTok content search - implementation required")
            return []
            
        except Exception as e:
            logger.error(f"Error searching TikTok for similar content: {e}")
            return []
    
    async def get_content_metadata(self, content_url: str) -> Dict[str, Any]:
        """Get metadata for specific TikTok content."""



        try:
            # TikTok metadata extraction implementation
            return {
                "platform": "tiktok",
                "url": content_url,
                "metadata_available": False,
                "note": "TikTok API integration in development"
            }
            
        except Exception as e:
            logger.error(f"Error getting TikTok content metadata: {e}")
            return {}


class TwitterConnector(BasePlatformConnector):
    """
    Twitter platform connector.
    
    Integrates with Twitter API v2 for content monitoring.
    """
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.api_base_url = "https://api.twitter.com/2"
        
    async def initialize(self) -> bool:
        """Initialize Twitter connector."""



        try:
            if not self.credentials.api_key:
                logger.error("Twitter API key not provided")
                return False
            
            test_result = await self.authenticate()
            if test_result:
                self.status = ConnectionStatus.CONNECTED
                logger.info("Twitter connector initialized successfully")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Failed to initialize Twitter connector: {e}")
            self.status = ConnectionStatus.ERROR
            return False
    
    async def authenticate(self) -> bool:
        """Authenticate with Twitter API."""



        try:
            # Test API credentials
            test_url = f"{self.api_base_url}/users/me"
            headers = {
                "Authorization": f"Bearer {self.credentials.access_token}",
                "Accept": "application/json"
            }
            
            response = await self._make_request("GET", test_url, headers=headers)
            
            if response:
                logger.info("Twitter authentication successful")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Twitter authentication failed: {e}")
            return False
    
    async def search_similar_content(self, 
                                   fingerprint_hash: str,
                                   content_type: str,
                                   metadata: Dict[str, Any]) -> List[SearchResult]:
        """Search for similar content on Twitter."""



        try:
            search_results = []
            
            # Build search queries
            search_queries = self._build_twitter_search_queries(metadata)
            
            for query in search_queries:
                twitter_results = await self._search_twitter(query)
                
                for result in twitter_results:
                    similarity_indicators = await self._calculate_twitter_similarity(
                        result, fingerprint_hash, metadata
                    )
                    
                    search_result = SearchResult(
                        platform="twitter",
                        url=f"https://twitter.com/i/status/{result['id']}",
                        title=result.get('text', '')[:100],
                        description=result.get('text', ''),
                        content_type="text",
                        upload_date=datetime.fromisoformat(result['created_at'].replace('Z', '+00:00')),
                        author=result.get('author_id', ''),
                        view_count=result.get('public_metrics', {}).get('view_count'),
                        metadata=result,
                        similarity_indicators=similarity_indicators
                    )
                    
                    search_results.append(search_result)
            
            logger.info(f"Found {len(search_results)} potential matches on Twitter")
            return search_results
            
        except Exception as e:
            logger.error(f"Error searching Twitter for similar content: {e}")
            return []
    
    def _build_twitter_search_queries(self, metadata: Dict[str, Any]) -> List[str]:
        """Build Twitter search queries from metadata."""
        queries = []
        
        # Use title/text content
        if metadata.get("title"):
            queries.append(f'"{metadata["title"]}"')
        
        # Use keywords
        if metadata.get("keywords"):
            keywords = metadata["keywords"]
            if isinstance(keywords, list):
                for keyword in keywords[:3]:
                    queries.append(keyword)
            elif isinstance(keywords, str):
                queries.append(keywords)
        
        # Use hashtags if available
        if metadata.get("hashtags"):
            hashtags = metadata["hashtags"]
            if isinstance(hashtags, list):
                for hashtag in hashtags[:3]:
                    queries.append(f"#{hashtag}")
        
        return queries[:5]
    
    async def _search_twitter(self, query: str) -> List[Dict[str, Any]]:
        """Search Twitter for specific query."""



        try:
            search_url = f"{self.api_base_url}/tweets/search/recent"
            headers = {
                "Authorization": f"Bearer {self.credentials.access_token}",
                "Accept": "application/json"
            }
            params = {
                "query": query,
                "max_results": 10,
                "tweet.fields": "created_at,author_id,public_metrics,text"
            }
            
            response = await self._make_request("GET", search_url, headers=headers, params=params)
            
            if response and "data" in response:
                return response["data"]
            
            return []
            
        except Exception as e:
            logger.error(f"Error searching Twitter with query '{query}': {e}")
            return []
    
    async def _calculate_twitter_similarity(self, 
                                          twitter_result: Dict[str, Any],
                                          fingerprint_hash: str,
                                          original_metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate similarity indicators for Twitter content."""
        indicators = {
            "text_similarity": 0.0,
            "hashtag_similarity": 0.0,
            "temporal_proximity": 0.0,
            "overall_confidence": 0.0
        }
        
        try:
            # Text similarity
            original_text = original_metadata.get("text", original_metadata.get("description", ""))
            twitter_text = twitter_result.get("text", "")
            indicators["text_similarity"] = self._calculate_text_similarity(original_text, twitter_text)
            
            # Hashtag similarity
            original_hashtags = set(original_metadata.get("hashtags", []))
            twitter_hashtags = set(self._extract_hashtags(twitter_text))
            
            if original_hashtags and twitter_hashtags:
                hashtag_overlap = len(original_hashtags.intersection(twitter_hashtags))
                hashtag_union = len(original_hashtags.union(twitter_hashtags))
                indicators["hashtag_similarity"] = hashtag_overlap / hashtag_union if hashtag_union > 0 else 0.0
            
            # Temporal proximity
            if original_metadata.get("creation_date"):
                original_date = datetime.fromisoformat(original_metadata["creation_date"])
                twitter_date = datetime.fromisoformat(twitter_result["created_at"].replace('Z', '+00:00'))
                
                time_diff = abs((twitter_date - original_date).days)
                if time_diff <= 1:
                    indicators["temporal_proximity"] = 1.0
                elif time_diff <= 7:
                    indicators["temporal_proximity"] = 0.7
                elif time_diff <= 30:
                    indicators["temporal_proximity"] = 0.3
                else:
                    indicators["temporal_proximity"] = 0.1
            
            # Calculate overall confidence
            weights = {
                "text_similarity": 0.5,
                "hashtag_similarity": 0.3,
                "temporal_proximity": 0.2
            }
            
            indicators["overall_confidence"] = sum(
                indicators[key] * weight for key, weight in weights.items()
            )
            
        except Exception as e:
            logger.error(f"Error calculating Twitter similarity indicators: {e}")
        
        return indicators
    
    def _extract_hashtags(self, text: str) -> List[str]:
        """Extract hashtags from text."""
        import re
        hashtags = re.findall(r'#(\w+)', text)
        return [tag.lower() for tag in hashtags]
    
    def _calculate_text_similarity(self, text1: str, text2: str) -> float:
        """Calculate text similarity using simple word overlap."""
        if not text1 or not text2:
            return 0.0
        
        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())
        
        if not words1 or not words2:
            return 0.0
        
        intersection = len(words1.intersection(words2))
        union = len(words1.union(words2))
        
        return intersection / union if union > 0 else 0.0
    
    async def get_content_metadata(self, content_url: str) -> Dict[str, Any]:
        """Get metadata for specific Twitter content."""



        try:
            # Extract tweet ID from URL
            tweet_id = self._extract_tweet_id(content_url)
            if not tweet_id:
                return {}
            
            # Get tweet details
            tweet_url = f"{self.api_base_url}/tweets/{tweet_id}"
            headers = {
                "Authorization": f"Bearer {self.credentials.access_token}",
                "Accept": "application/json"
            }
            params = {
                "tweet.fields": "created_at,author_id,public_metrics,text,context_annotations"
            }
            
            response = await self._make_request("GET", tweet_url, headers=headers, params=params)
            
            if response and "data" in response:
                tweet_data = response["data"]
                
                return {
                    "platform": "twitter",
                    "tweet_id": tweet_id,
                    "text": tweet_data.get("text", ""),
                    "author_id": tweet_data.get("author_id", ""),
                    "created_at": tweet_data.get("created_at", ""),
                    "public_metrics": tweet_data.get("public_metrics", {}),
                    "raw_data": tweet_data
                }
            
            return {}
            
        except Exception as e:
            logger.error(f"Error getting Twitter content metadata: {e}")
            return {}
    
    def _extract_tweet_id(self, url: str) -> Optional[str]:
        """Extract tweet ID from Twitter URL."""



        try:
            if "twitter.com" in url and "/status/" in url:
                return url.split("/status/")[1].split("?")[0]
            return None
        except Exception:
            return None


class GenericWebConnector(BasePlatformConnector):
    """
    Generic web connector for general web content monitoring.
    
    Uses web scraping and crawling techniques to monitor content
    across websites that don't have specific APIs.
    """
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.user_agent = config.get("user_agent", "IA-Influencer-Surveillance-Bot/1.0")
        self.respect_robots_txt = config.get("respect_robots_txt", True)
        
    async def initialize(self) -> bool:
        """Initialize generic web connector."""



        try:
            self.status = ConnectionStatus.CONNECTED
            logger.info("Generic web connector initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize generic web connector: {e}")
            self.status = ConnectionStatus.ERROR
            return False
    
    async def authenticate(self) -> bool:
        """Authentication not required for generic web scraping."""



        return True
    
    async def search_similar_content(self, 
                                   fingerprint_hash: str,
                                   content_type: str,
                                   metadata: Dict[str, Any]) -> List[SearchResult]:
        """Search for similar content using web search engines."""



        try:
            search_results = []
            
            # Build search queries
            search_queries = self._build_web_search_queries(metadata)
            
            for query in search_queries:
                # Use search engines like Google, Bing, etc.
                web_results = await self._search_web(query)
                
                for result in web_results:
                    similarity_indicators = await self._calculate_web_similarity(
                        result, fingerprint_hash, metadata
                    )
                    
                    search_result = SearchResult(
                        platform="web",
                        url=result.get("url", ""),
                        title=result.get("title", ""),
                        description=result.get("description", ""),
                        content_type="web",
                        upload_date=datetime.utcnow(),  # Unknown for web content
                        author="",
                        view_count=None,
                        metadata=result,
                        similarity_indicators=similarity_indicators
                    )
                    
                    search_results.append(search_result)
            
            logger.info(f"Found {len(search_results)} potential matches on web")
            return search_results
            
        except Exception as e:
            logger.error(f"Error searching web for similar content: {e}")
            return []
    
    def _build_web_search_queries(self, metadata: Dict[str, Any]) -> List[str]:
        """Build web search queries from metadata."""
        queries = []
        
        # Use exact title in quotes
        if metadata.get("title"):
            queries.append(f'"{metadata["title"]}"')
        
        # Use artist/author with title
        if metadata.get("artist") and metadata.get("title"):
            queries.append(f'{metadata["artist"]} "{metadata["title"]}"')
        
        # Use description fragments
        if metadata.get("description"):
            description = metadata["description"]
            if len(description) > 20:
                # Extract meaningful phrases
                words = description.split()
                if len(words) > 5:
                    phrase = " ".join(words[:8])
                    queries.append(f'"{phrase}"')
        
        return queries[:3]  # Limit to avoid excessive requests
    
    async def _search_web(self, query: str) -> List[Dict[str, Any]]:
        """Search web using search engines."""



        try:
            # This is a placeholder implementation
            # In a real implementation, you would use:
            # 1. Google Custom Search API
            # 2. Bing Search API
            # 3. DuckDuckGo API
            # 4. Or scrape search results (with respect to terms of service)
            
            logger.info(f"Web search for: {query}")
            return []  # Placeholder
            
        except Exception as e:
            logger.error(f"Error searching web with query '{query}': {e}")
            return []
    
    async def _calculate_web_similarity(self, 
                                      web_result: Dict[str, Any],
                                      fingerprint_hash: str,
                                      original_metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate similarity indicators for web content."""



        return {
            "title_similarity": 0.0,
            "url_similarity": 0.0,
            "content_similarity": 0.0,
            "overall_confidence": 0.0
        }
    
    async def get_content_metadata(self, content_url: str) -> Dict[str, Any]:
        """Get metadata for specific web content."""



        try:
            headers = {
                "User-Agent": self.user_agent,
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
            }
            
            response = await self._make_request("GET", content_url, headers=headers)
            
            if response:
                # Parse HTML and extract metadata
                # This would typically use BeautifulSoup or similar
                return {
                    "platform": "web",
                    "url": content_url,
                    "metadata_extraction": "requires_html_parsing"
                }
            
            return {}
            
        except Exception as e:
            logger.error(f"Error getting web content metadata: {e}")
            return {}


# Global platform connectors registry
_platform_connectors: Dict[str, BasePlatformConnector] = {}


def register_platform_connector(platform: str, connector: BasePlatformConnector) -> None:
    """Register platform connector."""
    _platform_connectors[platform] = connector


def get_platform_connector(platform: str) -> Optional[BasePlatformConnector]:
    """Get platform connector by name."""



    return _platform_connectors.get(platform)


def get_all_platform_connectors() -> Dict[str, BasePlatformConnector]:
    """Get all registered platform connectors."""



    return _platform_connectors.copy()


async def initialize_platform_connectors(config: Dict[str, Any]) -> bool:
    """Initialize all platform connectors."""



    try:
        connectors_config = config.get("platform_connectors", {})
        
        # Initialize YouTube connector
        if connectors_config.get("youtube", {}).get("enabled", False):
            youtube_connector = YouTubeConnector(connectors_config["youtube"])
            if await youtube_connector.initialize():
                register_platform_connector("youtube", youtube_connector)
        
        # Initialize Instagram connector
        if connectors_config.get("instagram", {}).get("enabled", False):
            instagram_connector = InstagramConnector(connectors_config["instagram"])
            if await instagram_connector.initialize():
                register_platform_connector("instagram", instagram_connector)
        
        # Initialize TikTok connector
        if connectors_config.get("tiktok", {}).get("enabled", False):
            tiktok_connector = TikTokConnector(connectors_config["tiktok"])
            if await tiktok_connector.initialize():
                register_platform_connector("tiktok", tiktok_connector)
        
        # Initialize Twitter connector
        if connectors_config.get("twitter", {}).get("enabled", False):
            twitter_connector = TwitterConnector(connectors_config["twitter"])
            if await twitter_connector.initialize():
                register_platform_connector("twitter", twitter_connector)
        
        # Initialize Generic Web connector
        if connectors_config.get("generic_web", {}).get("enabled", False):
            web_connector = GenericWebConnector(connectors_config["generic_web"])
            if await web_connector.initialize():
                register_platform_connector("generic_web", web_connector)
        
        logger.info(f"Initialized {len(_platform_connectors)} platform connectors")
        return True
        
    except Exception as e:
        logger.error(f"Error initializing platform connectors: {e}")
        return False


async def shutdown_platform_connectors() -> None:
    """Shutdown all platform connectors."""
    logger.info("Shutting down platform connectors...")
    
    for connector in _platform_connectors.values():
        await connector.shutdown()
    
    _platform_connectors.clear()
    logger.info("Platform connectors shutdown complete")
