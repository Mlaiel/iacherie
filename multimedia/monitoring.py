"""Professional Content Monitoring and Web Surveillance System
Enterprise-grade content monitoring with AI-powered violation detection

Project Team: Lead AI Developer + Backend Senior Engineer + ML Engineer + 
              Database Administrator + Security Expert + Microservices Architect +
              Multimedia Processing Specialist + DevOps Engineer + AI Prompt Engineer

Created by: Fahed Mlaiel <mlaiel@live.de>

⚠️ STRICT COPYRIGHT WARNING ⚠️
This code is proprietary and confidential. Any unauthorized use, reproduction, 
distribution, or modification without written permission from Fahed Mlaiel 
(mlaiel@live.de) is strictly prohibited and will be prosecuted to the full 
extent of the law. All rights reserved.

Contact: mlaiel@live.de for licensing and authorization inquiries.
"""

import asyncio
import logging
import json
import hashlib
from typing import Dict, List, Optional, Any, Union, Tuple, AsyncGenerator, Set
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from abc import ABC, abstractmethod
import aiohttp
import httpx
from urllib.parse import urljoin, urlparse
import cv2
import numpy as np
from PIL import Image
import librosa
import soundfile as sf
from bs4 import BeautifulSoup
import selenium
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import torch
from transformers import CLIPProcessor, CLIPModel
import faiss
from sqlalchemy import select, insert, update
from sqlalchemy.ext.asyncio import AsyncSession

from .formats import ContentFormat
from .ai_analysis import ContentAnalyzer, SceneDetector, ObjectDetector
from .protection import FingerprintGenerator
from ..core.exceptions import MonitoringError, CrawlingError
from ..core.config import get_settings
from ..core.database import get_session
from ..utils.caching import cache_result
from ..utils.retry import async_retry
from ..utils.notifications import NotificationService

logger = logging.getLogger(__name__)
settings = get_settings()


class ViolationType(Enum):
    """
Types of content violations"""

    COPYRIGHT_INFRINGEMENT = "copyright_infringement"
    UNAUTHORIZED_USE = "unauthorized_use"
    CONTENT_THEFT = "content_theft"
    TRADEMARK_VIOLATION = "trademark_violation"
    IMPERSONATION = "impersonation"
    PLAGIARISM = "plagiarism"
    DEEPFAKE = "deepfake"
    MODIFIED_CONTENT = "modified_content"


class PlatformType(Enum):
    """Monitored platform types"""

    YOUTUBE = "youtube"
    INSTAGRAM = "instagram"
    TIKTOK = "tiktok"
    TWITTER = "twitter"
    FACEBOOK = "facebook"
    PINTEREST = "pinterest"
    REDDIT = "reddit"
    GENERIC_WEB = "generic_web"
    SOUNDCLOUD = "soundcloud"
    SPOTIFY = "spotify"


class ActionType(Enum):
    """Actions to take on violations"""

    NOTIFY_USER = "notify_user"
    SEND_TAKEDOWN = "send_takedown"
    ESCALATE = "escalate"
    COLLECT_EVIDENCE = "collect_evidence"
    LEGAL_ACTION = "legal_action"
    AUTOMATED_CLAIM = "automated_claim"


@dataclass
class MonitoringConfig:
    """Content monitoring configuration"""
    platforms: List[PlatformType]
    search_keywords: List[str] = field(default_factory=list)
    monitoring_frequency: int = 24  # Hours between scans
    similarity_threshold: float = 0.85  # Similarity threshold for matches
    auto_action: bool = False  # Automatically take action on violations
    notification_enabled: bool = True
    evidence_collection: bool = True
    deep_scan: bool = False  # More thorough but slower scanning
    
    # Advanced options
    monitor_derivatives: bool = True  # Monitor modified versions
    reverse_image_search: bool = True
    audio_fingerprint_matching: bool = True
    text_similarity_matching: bool = True
    face_recognition_matching: bool = False


@dataclass
class ViolationAlert:
    """
Content violation alert"""
    violation_id: str
    user_id: str
    original_content_id: str
    violation_type: ViolationType
    platform: PlatformType
    detected_url: str
    similarity_score: float
    detected_at: datetime
    
    # Evidence
    screenshot_url: Optional[str] = None
    extracted_content: Optional[bytes] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    # Status
    status: str = "pending"  # pending, verified, false_positive, resolved
    action_taken: Optional[ActionType] = None
    resolution_notes: Optional[str] = None
    
    # Legal
    dmca_notice_sent: bool = False
    legal_case_opened: bool = False
    estimated_damages: float = 0.0


@dataclass
class SearchResult:
    """Search result from platform crawling"""
    platform: PlatformType
    url: str
    title: str
    content_type: str
    thumbnail_url: Optional[str] = None
    description: Optional[str] = None
    author: Optional[str] = None
    upload_date: Optional[datetime] = None
    view_count: int = 0
    engagement_metrics: Dict[str, Any] = field(default_factory=dict)
    content_hash: Optional[str] = None


class BaseCrawler(ABC):
    """
Base class for platform crawlers"""
    
    def __init__(self, config: MonitoringConfig):
        self.config = config
        self.session = None
        self.rate_limiter = None
        self.browser_driver = None
        
    @abstractmethod
    async def search_content(
        self, 
        query: str,
        try:
            logger.info(f"Executing search_content")
            
            # Implementation for search_content
            # TODO: Add specific business logic here
            
            result = None  # Replace with actual implementation
            
            logger.info(f"search_content completed successfully")
            return result
            
        except Exception as e:
            logger.error(f"Error: {e}")
            raise

    def placeholder_method(self):
        """Placeholder method"""  
        try:
                    # AI model processing
                    if not hasattr(self, 'model') or self.model is None:
        try:
                    # Request validation
                    if not url:
                        raise ValueError("Invalid request")
            
                    # Process request
                    result = await self._handle_get_content_metadata_request(url)
            
                    # Return response
                    return {"status": "success", "data": result}
            
                except Exception as e:
                    logger.error(f"API handler get_content_metadata failed: {e}")
                    return {"status": "error", "message": str(e)}
                    processed_input = await self._preprocess_extract_content_input(url)
            
                    # Run inference
                    result = await self.model.predict(processed_input)
            
                    # Postprocess result
                    final_result = await self._postprocess_extract_content_result(result)
            
                    logger.info(f"AI processing extract_content completed")
                    return final_result
            
                except Exception as e:
                    logger.error(f"AI processing extract_content failed: {e}")
                    raise
            logger.error(f"search_content failed: {e}")
            raise
    @abstractmethod
    async def extract_content(self, url: str) -> Optional[bytes]:
        """
Extract content from URL"""
        pass
    
    @abstractmethod
    async def get_content_metadata(self, url: str) -> Dict[str, Any]:
        """
Get content metadata"""
        pass
    
    async def _init_session(self):
        """
Initialize HTTP session"""
        if not self.session:
            timeout = aiohttp.ClientTimeout(total=30)
            self.session = aiohttp.ClientSession(
                timeout=timeout,
                headers={
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
                    "Accept-Language": "en-US,en;q=0.5",
                    "Accept-Encoding": "gzip, deflate",
                    "DNT": "1",
                    "Connection": "keep-alive"
                }
            )
    
    async def _init_browser(self):
        """Initialize headless browser for JavaScript-heavy sites"""
        if not self.browser_driver:
            chrome_options = Options()
            chrome_options.add_argument("--headless")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--window-size=1920,1080")
            chrome_options.add_argument(f"--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")
            
            self.browser_driver = webdriver.Chrome(options=chrome_options)
    
    async def _close_resources(self):
        """Clean up resources"""
        if self.session:
            await self.session.close()
            self.session = None
            
        if self.browser_driver:
            self.browser_driver.quit()
            self.browser_driver = None


class YouTubeCrawler(BaseCrawler):
    """
YouTube content crawler"""

    
    API_BASE_URL = "https://www.googleapis.com/youtube/v3"
    SEARCH_URL = "https://www.youtube.com/results"
    
    async def search_content(
        self, 
        query: str,
        content_type: Optional[str] = None,
        max_results: int = 100
    ) -> List[SearchResult]:
        """Search YouTube for content"""
        try:
            await self._init_session()
            
            # Use YouTube Data API if available
            if hasattr(settings, 'YOUTUBE_API_KEY') and settings.YOUTUBE_API_KEY:
                return await self._search_with_api(query, content_type, max_results)
            else:
                return await self._search_with_scraping(query, content_type, max_results)
                
        except Exception as e:
            logger.error(f"YouTube search failed: {str(e)}")
            return []
    
    async def _search_with_api(
        self, 
        query: str, 
        content_type: Optional[str], 
        max_results: int
    ) -> List[SearchResult]:
        """Search using YouTube Data API"""
        try:
            url = f"{self.API_BASE_URL}/search"
            params = {
                "part": "snippet",
                "q": query,
                "type": "video",
                "maxResults": min(max_results, 50),
                "key": settings.YOUTUBE_API_KEY,
                "order": "relevance"
            }
            
            if content_type:
                params["videoDuration"] = content_type
            
            async with self.session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    return await self._parse_api_results(data)
                else:
                    logger.error(f"YouTube API error: {response.status}")
                    return []
                    
        except Exception as e:
            logger.error(f"YouTube API search failed: {str(e)}")
            return []
    
    async def _search_with_scraping(
        self, 
        query: str, 
        content_type: Optional[str], 
        max_results: int
    ) -> List[SearchResult]:
        """Search using web scraping"""
        try:
            await self._init_browser()
            
            search_url = f"{self.SEARCH_URL}?search_query={query}"
            self.browser_driver.get(search_url)
            
            # Wait for content to load
            await asyncio.sleep(3)
            
            # Extract video elements
            video_elements = self.browser_driver.find_elements(
                By.CSS_SELECTOR, 
                "ytd-video-renderer, ytd-grid-video-renderer"
            )
            
            results = []
            for element in video_elements[:max_results]:
                try:
                    result = await self._parse_video_element(element)
                    if result:
                        results.append(result)
                except Exception as e:
                    logger.warning(f"Failed to parse video element: {str(e)}")
                    continue
            
            return results
            
        except Exception as e:
            logger.error(f"YouTube scraping failed: {str(e)}")
            return []
    
    async def _parse_api_results(self, data: Dict[str, Any]) -> List[SearchResult]:
        """Parse YouTube API results"""
        results = []
        
        for item in data.get("items", []):
            snippet = item.get("snippet", {})
            video_id = item.get("id", {}).get("videoId")
            
            if video_id:
                results.append(SearchResult(
                    platform=PlatformType.YOUTUBE,
                    url=f"https://www.youtube.com/watch?v={video_id}",
                    title=snippet.get("title", ""),
                    content_type="video",
                    thumbnail_url=snippet.get("thumbnails", {}).get("high", {}).get("url"),
                    description=snippet.get("description", ""),
                    author=snippet.get("channelTitle", ""),
                    upload_date=datetime.fromisoformat(snippet.get("publishedAt", "").replace("Z", "+00:00")),
                ))
        
        return results
    
    async def _parse_video_element(self, element) -> Optional[SearchResult]:
        """Parse individual video element from scraping"""
        try:
            # Extract video URL
            link_element = element.find_element(By.CSS_SELECTOR, "a#video-title")
            video_url = link_element.get_attribute("href")
            video_title = link_element.get_attribute("title")
            
            # Extract thumbnail
            thumbnail_element = element.find_element(By.CSS_SELECTOR, "img")
            thumbnail_url = thumbnail_element.get_attribute("src")
            
            # Extract author
            author_element = element.find_element(By.CSS_SELECTOR, "a.yt-simple-endpoint.style-scope.yt-formatted-string")
            author = author_element.text if author_element else ""
            
            return SearchResult(
                platform=PlatformType.YOUTUBE,
                url=video_url,
                title=video_title,
                content_type="video",
                thumbnail_url=thumbnail_url,
                author=author
            )
            
        except Exception as e:
            logger.warning(f"Failed to parse video element: {str(e)}")
            return None
    
    async def extract_content(self, url: str) -> Optional[bytes]:
        """Extract video content from YouTube URL"""
        try:
            # Use youtube-dl or similar tool to extract video
            import yt_dlp
            
            ydl_opts = {
                'format': 'best[height<=720]',  # Limit quality for processing
                'no_warnings': True,
                'quiet': True
            }
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                video_url = info.get('url')
                
                if video_url:
                    async with self.session.get(video_url) as response:
                        if response.status == 200:
                            return await response.read()
            
            return None
            
        except Exception as e:
            logger.error(f"YouTube content extraction failed: {str(e)}")
            return None
    
    async def get_content_metadata(self, url: str) -> Dict[str, Any]:
        """Get YouTube video metadata"""
        try:
            import yt_dlp
            
            ydl_opts = {
                'no_warnings': True,
                'quiet': True
            }
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                
                return {
                    "title": info.get("title", ""),
                    "description": info.get("description", ""),
                    "duration": info.get("duration", 0),
                    "view_count": info.get("view_count", 0),
                    "like_count": info.get("like_count", 0),
                    "upload_date": info.get("upload_date", ""),
                    "uploader": info.get("uploader", ""),
                    "thumbnail": info.get("thumbnail", "")
                }
            
        except Exception as e:
            logger.error(f"YouTube metadata extraction failed: {str(e)}")
            return {}


class InstagramCrawler(BaseCrawler):
    """Instagram content crawler"""

    
    BASE_URL = "https://www.instagram.com"
    
    async def search_content(
        self, 
        query: str,
        content_type: Optional[str] = None,
        max_results: int = 100
    ) -> List[SearchResult]:
        """Search Instagram for content"""
        try:
            await self._init_browser()
            
            # Search by hashtag
            if query.startswith("#"):
                search_url = f"{self.BASE_URL}/explore/tags/{query[1:]}/"
            else:
                search_url = f"{self.BASE_URL}/explore/search/keyword/?q={query}"
            
            self.browser_driver.get(search_url)
            await asyncio.sleep(5)  # Wait for content to load
            
            # Scroll to load more content
            for _ in range(3):
                self.browser_driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                await asyncio.sleep(2)
            
            # Extract post elements
            post_elements = self.browser_driver.find_elements(
                By.CSS_SELECTOR, 
                "article a"
            )
            
            results = []
            for element in post_elements[:max_results]:
                try:
                    post_url = element.get_attribute("href")
                    if post_url and "/p/" in post_url:
                        result = await self._parse_instagram_post(element, post_url)
                        if result:
                            results.append(result)
                except Exception as e:
                    logger.warning(f"Failed to parse Instagram post: {str(e)}")
                    continue
            
            return results
            
        except Exception as e:
            logger.error(f"Instagram search failed: {str(e)}")
            return []
    
    async def _parse_instagram_post(self, element, post_url: str) -> Optional[SearchResult]:
        """Parse Instagram post element"""
        try:
            # Extract thumbnail
            img_element = element.find_element(By.CSS_SELECTOR, "img")
            thumbnail_url = img_element.get_attribute("src")
            alt_text = img_element.get_attribute("alt")
            
            return SearchResult(
                platform=PlatformType.INSTAGRAM,
                url=post_url,
                title=alt_text or "Instagram Post",
                content_type="image",
                thumbnail_url=thumbnail_url
            )
            
        except Exception as e:
            logger.warning(f"Failed to parse Instagram post element: {str(e)}")
            return None
    
    async def extract_content(self, url: str) -> Optional[bytes]:
        """Extract content from Instagram post"""
        try:
            await self._init_browser()
            
            self.browser_driver.get(url)
            await asyncio.sleep(3)
            
            # Find main image/video element
            media_elements = self.browser_driver.find_elements(
                By.CSS_SELECTOR, 
                "article img, article video"
            )
            
            if media_elements:
                media_url = media_elements[0].get_attribute("src")
                if media_url:
                    async with self.session.get(media_url) as response:
                        if response.status == 200:
                            return await response.read()
            
            return None
            
        except Exception as e:
            logger.error(f"Instagram content extraction failed: {str(e)}")
            return None
    
    async def get_content_metadata(self, url: str) -> Dict[str, Any]:
        """Get Instagram post metadata"""
        try:
            await self._init_browser()
            
            self.browser_driver.get(url)
            await asyncio.sleep(3)
            
            # Extract metadata using page source
            soup = BeautifulSoup(self.browser_driver.page_source, 'html.parser')
            
            # Look for JSON-LD data
            json_scripts = soup.find_all('script', type='application/ld+json')
            for script in json_scripts:
                try:
                    data = json.loads(script.string)
                    if isinstance(data, dict) and '@type' in data:
                        return {
                            "title": data.get("headline", ""),
                            "description": data.get("description", ""),
                            "author": data.get("author", {}).get("name", ""),
                            "date_published": data.get("datePublished", ""),
                            "interaction_count": data.get("interactionStatistic", {}).get("userInteractionCount", 0)
                        }
                except json.JSONDecodeError:
                    continue
            
            return {}
            
        except Exception as e:
            logger.error(f"Instagram metadata extraction failed: {str(e)}")
            return {}


class TikTokCrawler(BaseCrawler):
    """TikTok content crawler"""

    
    BASE_URL = "https://www.tiktok.com"
    
    async def search_content(
        self, 
        query: str,
        content_type: Optional[str] = None,
        max_results: int = 100
    ) -> List[SearchResult]:
        """Search TikTok for content"""
        try:
            await self._init_browser()
            
            search_url = f"{self.BASE_URL}/search?q={query}"
            self.browser_driver.get(search_url)
            await asyncio.sleep(5)
            
            # Scroll to load more videos
            for _ in range(5):
                self.browser_driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                await asyncio.sleep(2)
            
            # Extract video elements
            video_elements = self.browser_driver.find_elements(
                By.CSS_SELECTOR,
                "[data-e2e='search-card-item']"
            )
            
            results = []
            for element in video_elements[:max_results]:
                try:
                    result = await self._parse_tiktok_video(element)
                    if result:
                        results.append(result)
                except Exception as e:
                    logger.warning(f"Failed to parse TikTok video: {str(e)}")
                    continue
            
            return results
            
        except Exception as e:
            logger.error(f"TikTok search failed: {str(e)}")
            return []
    
    async def _parse_tiktok_video(self, element) -> Optional[SearchResult]:
        """Parse TikTok video element"""
        try:
            # Extract video URL
            link_element = element.find_element(By.CSS_SELECTOR, "a")
            video_url = link_element.get_attribute("href")
            
            # Extract thumbnail
            img_element = element.find_element(By.CSS_SELECTOR, "img")
            thumbnail_url = img_element.get_attribute("src")
            
            return SearchResult(
                platform=PlatformType.TIKTOK,
                url=video_url,
                title="TikTok Video",
                content_type="video",
                thumbnail_url=thumbnail_url
            )
            
        except Exception as e:
            logger.warning(f"Failed to parse TikTok video element: {str(e)}")
            return None
    
    async def extract_content(self, url: str) -> Optional[bytes]:
        """Extract TikTok video content"""
        try:
            # TikTok content extraction requires specialized tools
            # This would integrate with TikTok downloaders
            logger.info(f"TikTok content extraction not implemented for: {url}")
            return None
            
        except Exception as e:
            logger.error(f"TikTok content extraction failed: {str(e)}")
            return None
    
    async def get_content_metadata(self, url: str) -> Dict[str, Any]:
        """Get TikTok video metadata"""
        try:
            await self._init_browser()
            
            self.browser_driver.get(url)
            await asyncio.sleep(3)
            
            # Extract basic metadata
            soup = BeautifulSoup(self.browser_driver.page_source, 'html.parser')
            
            # Look for meta tags
            title_tag = soup.find('meta', property='og:title')
            description_tag = soup.find('meta', property='og:description')
            
            return {
                "title": title_tag.get('content', '') if title_tag else '',
                "description": description_tag.get('content', '') if description_tag else ''
            }
            
        except Exception as e:
            logger.error(f"TikTok metadata extraction failed: {str(e)}")
            return {}


class ContentMonitor:
    """Main content monitoring orchestrator"""
    
    def __init__(self, config: MonitoringConfig):
        self.config = config
        self.crawlers: Dict[PlatformType, BaseCrawler] = {}
        self.analyzer = ContentAnalyzer()
        self.fingerprint_generator = FingerprintGenerator()
        self.notification_service = NotificationService()
        
        # Initialize crawlers
        self._init_crawlers()
        
        # Vector database for similarity matching
        self.vector_index = None
        self.content_vectors = {}
        
    def _init_crawlers(self):
        """
Initialize platform crawlers"""
        for platform in self.config.platforms:
            if platform == PlatformType.YOUTUBE:
                self.crawlers[platform] = YouTubeCrawler(self.config)
            elif platform == PlatformType.INSTAGRAM:
                self.crawlers[platform] = InstagramCrawler(self.config)
            elif platform == PlatformType.TIKTOK:
                self.crawlers[platform] = TikTokCrawler(self.config)
            # Add other platform crawlers as needed
    
    async def register_content_for_monitoring(
        self,
        user_id: str,
        content_id: str,
        content: bytes,
        content_format: ContentFormat,
        keywords: List[str] = None
    ) -> bool:
        """
Register content for monitoring"""
        try:
            # Generate fingerprints for the content
            fingerprints = await self.fingerprint_generator.generate_comprehensive_fingerprint(
                content, content_format
            )
            
            # Generate vector embeddings for similarity matching
            vector_embedding = await self._generate_vector_embedding(content, content_format)
            
            # Store in database
            async with get_session() as session:
                monitoring_record = {
                    "user_id": user_id,
                    "content_id": content_id,
                    "content_format": content_format.mime_type,
                    "fingerprints": json.dumps(fingerprints.to_dict()),
                    "vector_embedding": vector_embedding.tobytes(),
                    "keywords": json.dumps(keywords or []),
                    "monitoring_enabled": True,
                    "created_at": datetime.utcnow(),
                    "last_scan": None
                }
                
                stmt = insert("content_monitoring").values(**monitoring_record)
                await session.execute(stmt)
                await session.commit()
                
                # Add to vector index
                await self._add_to_vector_index(content_id, vector_embedding)
                
                logger.info(f"Content {content_id} registered for monitoring")
                return True
                
        except Exception as e:
            logger.error(f"Failed to register content for monitoring: {str(e)}")
            return False
    
    async def scan_for_violations(self, user_id: Optional[str] = None) -> List[ViolationAlert]:
        """Scan all platforms for content violations"""
        violations = []
        
        try:
            # Get monitored content
            monitored_content = await self._get_monitored_content(user_id)
            
            for content_record in monitored_content:
                content_violations = await self._scan_content_violations(content_record)
                violations.extend(content_violations)
            
            # Store violations in database
            await self._store_violations(violations)
            
            # Send notifications for new violations
            await self._notify_violations(violations)
            
            return violations
            
        except Exception as e:
            logger.error(f"Violation scan failed: {str(e)}")
            return []
    
    async def _get_monitored_content(self, user_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get content that needs to be monitored"""
        try:
            async with get_session() as session:
                stmt = select("content_monitoring").where("monitoring_enabled" == True)
                
                if user_id:
                    stmt = stmt.where("user_id" == user_id)
                
                # Only scan content that hasn't been scanned recently
                recent_scan_threshold = datetime.utcnow() - timedelta(hours=self.config.monitoring_frequency)
                stmt = stmt.where(
                    ("last_scan" < recent_scan_threshold) | ("last_scan" == None)
                )
                
                result = await session.execute(stmt)
                return [dict(row) for row in result.fetchall()]
                
        except Exception as e:
            logger.error(f"Failed to get monitored content: {str(e)}")
            return []
    
    async def _scan_content_violations(self, content_record: Dict[str, Any]) -> List[ViolationAlert]:
        """Scan for violations of specific content"""
        violations = []
        
        try:
            content_id = content_record["content_id"]
            user_id = content_record["user_id"]
            keywords = json.loads(content_record.get("keywords", "[]"))
            fingerprints = json.loads(content_record.get("fingerprints", "{}"))
            
            # Search on each platform
            for platform, crawler in self.crawlers.items():
                try:
                    # Search using keywords
                    for keyword in keywords + [content_id]:
                        search_results = await crawler.search_content(keyword, max_results=50)
                        
                        for result in search_results:
                            # Check for potential violation
                            violation = await self._check_potential_violation(
                                content_record, result, fingerprints
                            )
                            
                            if violation:
                                violations.append(violation)
                    
                except Exception as e:
                    logger.error(f"Platform {platform} scan failed: {str(e)}")
                    continue
            
            # Update last scan time
            await self._update_last_scan(content_id)
            
            return violations
            
        except Exception as e:
            logger.error(f"Content violation scan failed: {str(e)}")
            return []
    
    async def _check_potential_violation(
        self,
        original_content: Dict[str, Any],
        search_result: SearchResult,
        fingerprints: Dict[str, Any]
    ) -> Optional[ViolationAlert]:
        """Check if search result is a potential violation"""
        try:
            # Extract content from search result
            crawler = self.crawlers[search_result.platform]
            suspected_content = await crawler.extract_content(search_result.url)
            
            if not suspected_content:
                return None
            
            # Calculate similarity
            similarity_score = await self._calculate_content_similarity(
                original_content, suspected_content, fingerprints
            )
            
            if similarity_score >= self.config.similarity_threshold:
                # Collect evidence
                evidence = await self._collect_evidence(search_result, suspected_content)
                
                # Determine violation type
                violation_type = await self._determine_violation_type(
                    original_content, search_result, similarity_score
                )
                
                # Create violation alert
                violation = ViolationAlert(
                    violation_id=f"viol_{hashlib.md5(f'{original_content['content_id']}_{search_result.url}_{datetime.utcnow()}'.encode()).hexdigest()[:16]}",
                    user_id=original_content["user_id"],
                    original_content_id=original_content["content_id"],
                    violation_type=violation_type,
                    platform=search_result.platform,
                    detected_url=search_result.url,
                    similarity_score=similarity_score,
                    detected_at=datetime.utcnow(),
                    screenshot_url=evidence.get("screenshot_url"),
                    extracted_content=suspected_content,
                    metadata={
                        "search_result": {
                            "title": search_result.title,
                            "author": search_result.author,
                            "upload_date": search_result.upload_date.isoformat() if search_result.upload_date else None,
                            "view_count": search_result.view_count
                        },
                        "similarity_details": evidence.get("similarity_details", {}),
                        "evidence": evidence
                    }
                )
                
                return violation
            
            return None
            
        except Exception as e:
            logger.error(f"Violation check failed: {str(e)}")
            return None
    
    async def _calculate_content_similarity(
        self,
        original_content: Dict[str, Any],
        suspected_content: bytes,
        original_fingerprints: Dict[str, Any]
    ) -> float:
        """Calculate similarity between original and suspected content"""
        try:
            # Generate fingerprints for suspected content
            suspected_format = ContentFormat.detect(suspected_content)
            suspected_fingerprints = await self.fingerprint_generator.generate_comprehensive_fingerprint(
                suspected_content, suspected_format
            )
            
            # Compare different types of fingerprints
            similarities = []
            
            # Perceptual hash similarity
            if "perceptual_hash" in original_fingerprints and "perceptual_hash" in suspected_fingerprints.to_dict():
                phash_similarity = await self._compare_perceptual_hashes(
                    original_fingerprints["perceptual_hash"],
                    suspected_fingerprints.to_dict()["perceptual_hash"]
                )
                similarities.append(phash_similarity)
            
            # Vector similarity
            if self.config.monitoring_frequency:  # Use as proxy for vector similarity enabled
                original_vector = np.frombuffer(original_content.get("vector_embedding", b""), dtype=np.float32)
                suspected_vector = await self._generate_vector_embedding(suspected_content, suspected_format)
                
                if len(original_vector) > 0 and len(suspected_vector) > 0:
                    vector_similarity = 1 - np.dot(original_vector, suspected_vector) / (
                        np.linalg.norm(original_vector) * np.linalg.norm(suspected_vector)
                    )
                    similarities.append(1 - vector_similarity)  # Convert distance to similarity
            
            # Audio fingerprint similarity (if audio content)
            if suspected_format.is_audio() and "audio_fingerprint" in original_fingerprints:
                audio_similarity = await self._compare_audio_fingerprints(
                    original_fingerprints["audio_fingerprint"],
                    suspected_fingerprints.to_dict().get("audio_fingerprint", {})
                )
                similarities.append(audio_similarity)
            
            # Return average similarity if we have any matches
            return float(np.mean(similarities)) if similarities else 0.0
            
        except Exception as e:
            logger.error(f"Similarity calculation failed: {str(e)}")
            return 0.0
    
    async def _compare_perceptual_hashes(
        self,
        hash1: str,
        hash2: str
    ) -> float:
        """Compare perceptual hashes and return similarity score"""
        try:
            import imagehash
            
            # Convert hex strings to hashes
            h1 = imagehash.hex_to_hash(hash1)
            h2 = imagehash.hex_to_hash(hash2)
            
            # Calculate Hamming distance
            hamming_distance = h1 - h2
            
            # Convert to similarity (0-1 scale)
            max_distance = len(hash1) * 4  # 4 bits per hex character
            similarity = 1.0 - (hamming_distance / max_distance)
            
            return max(0.0, similarity)
            
        except Exception as e:
            logger.error(f"Perceptual hash comparison failed: {str(e)}")
            return 0.0
    
    async def _compare_audio_fingerprints(
        self,
        fingerprint1: Dict[str, Any],
        fingerprint2: Dict[str, Any]
    ) -> float:
        """Compare audio fingerprints"""
        try:
            if not fingerprint1 or not fingerprint2:
                return 0.0
            
            # Compare spectral features
            similarities = []
            
            for feature in ["mfcc", "spectral_centroid", "chroma"]:
                if feature in fingerprint1 and feature in fingerprint2:
                    f1 = np.array(fingerprint1[feature])
                    f2 = np.array(fingerprint2[feature])
                    
                    # Calculate cosine similarity
                    if len(f1) > 0 and len(f2) > 0:
                        similarity = np.dot(f1, f2) / (np.linalg.norm(f1) * np.linalg.norm(f2))
                        similarities.append(max(0.0, similarity))
            
            return float(np.mean(similarities)) if similarities else 0.0
            
        except Exception as e:
            logger.error(f"Audio fingerprint comparison failed: {str(e)}")
            return 0.0
    
    async def _generate_vector_embedding(
        self,
        content: bytes,
        content_format: ContentFormat
    ) -> np.ndarray:
        """Generate vector embedding for content similarity matching"""
        try:
            if content_format.is_image():
                return await self._generate_image_embedding(content)
            elif content_format.is_video():
                return await self._generate_video_embedding(content)
            elif content_format.is_audio():
                return await self._generate_audio_embedding(content)
            else:
                return np.array([])
                
        except Exception as e:
            logger.error(f"Vector embedding generation failed: {str(e)}")
            return np.array([])
    
    async def _generate_image_embedding(self, image_content: bytes) -> np.ndarray:
        """Generate image embedding using CLIP"""
        try:
            # Load CLIP model if not already loaded
            if not hasattr(self, 'clip_processor'):
                self.clip_processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")
                self.clip_model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32")
            
            # Process image
            image = Image.open(io.BytesIO(image_content))
            inputs = self.clip_processor(images=image, return_tensors="pt")
            
            with torch.no_grad():
                image_features = self.clip_model.get_image_features(**inputs)
                return image_features.numpy().flatten()
                
        except Exception as e:
            logger.error(f"Image embedding generation failed: {str(e)}")
            return np.array([])
    
    async def _generate_video_embedding(self, video_content: bytes) -> np.ndarray:
        """Generate video embedding from key frames"""
        try:
            import tempfile
            import cv2
            
            # Save video to temporary file
            with tempfile.NamedTemporaryFile(suffix='.mp4') as temp_file:
                temp_file.write(video_content)
                temp_file.flush()
                
                # Extract key frames
                cap = cv2.VideoCapture(temp_file.name)
                frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
                
                if frame_count == 0:
                    return np.array([])
                
                # Sample frames
                sample_indices = np.linspace(0, frame_count-1, min(5, frame_count), dtype=int)
                frame_embeddings = []
                
                for frame_idx in sample_indices:
                    cap.set(cv2.CAP_PROP_POS_FRAMES, frame_idx)
                    ret, frame = cap.read()
                    
                    if ret:
                        # Convert frame to RGB and create embedding
                        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                        _, frame_bytes = cv2.imencode('.jpg', frame_rgb)
                        frame_embedding = await self._generate_image_embedding(frame_bytes.tobytes())
                        
                        if len(frame_embedding) > 0:
                            frame_embeddings.append(frame_embedding)
                
                cap.release()
                
                # Average frame embeddings
                if frame_embeddings:
                    return np.mean(frame_embeddings, axis=0)
                else:
                    return np.array([])
                    
        except Exception as e:
            logger.error(f"Video embedding generation failed: {str(e)}")
            return np.array([])
    
    async def _generate_audio_embedding(self, audio_content: bytes) -> np.ndarray:
        """Generate audio embedding"""
        try:
            import tempfile
            
            # Save audio to temporary file
            with tempfile.NamedTemporaryFile(suffix='.wav') as temp_file:
                temp_file.write(audio_content)
                temp_file.flush()
                
                # Load audio
                y, sr = librosa.load(temp_file.name, sr=22050)
                
                # Extract audio features
                mfcc = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=13)
                spectral_centroid = librosa.feature.spectral_centroid(y=y, sr=sr)
                chroma = librosa.feature.chroma_stft(y=y, sr=sr)
                
                # Combine features
                features = np.concatenate([
                    np.mean(mfcc, axis=1),
                    np.mean(spectral_centroid, axis=1),
                    np.mean(chroma, axis=1)
                ])
                
                return features
                
        except Exception as e:
            logger.error(f"Audio embedding generation failed: {str(e)}")
            return np.array([])
    
    async def _collect_evidence(
        self,
        search_result: SearchResult,
        content: bytes
    ) -> Dict[str, Any]:
        """Collect evidence for violation"""
        evidence = {
            "search_result_metadata": {
                "title": search_result.title,
                "url": search_result.url,
                "platform": search_result.platform.value,
                "author": search_result.author,
                "upload_date": search_result.upload_date.isoformat() if search_result.upload_date else None
            }
        }
        
        try:
            # Take screenshot if enabled
            if self.config.evidence_collection:
                screenshot_url = await self._take_screenshot(search_result.url)
                if screenshot_url:
                    evidence["screenshot_url"] = screenshot_url
            
            # Extract additional metadata
            crawler = self.crawlers[search_result.platform]
            metadata = await crawler.get_content_metadata(search_result.url)
            evidence["content_metadata"] = metadata
            
            return evidence
            
        except Exception as e:
            logger.error(f"Evidence collection failed: {str(e)}")
            return evidence
    
    async def _take_screenshot(self, url: str) -> Optional[str]:
        """Take screenshot of content page"""
        try:
            # This would integrate with screenshot service or use Selenium
            # For now, return placeholder
            return f"screenshot_{hashlib.md5(url.encode()).hexdigest()}.png"
            
        except Exception as e:
            logger.error(f"Screenshot failed: {str(e)}")
            return None
    
    async def _determine_violation_type(
        self,
        original_content: Dict[str, Any],
        search_result: SearchResult,
        similarity_score: float
    ) -> ViolationType:
        """Determine the type of violation"""
        try:
            # Simple heuristics for violation type determination
            if similarity_score > 0.95:
                return ViolationType.COPYRIGHT_INFRINGEMENT
            elif similarity_score > 0.85:
                if search_result.author != original_content.get("original_author"):
                    return ViolationType.UNAUTHORIZED_USE
                else:
                    return ViolationType.MODIFIED_CONTENT
            else:
                return ViolationType.CONTENT_THEFT
                
        except Exception as e:
            logger.error(f"Violation type determination failed: {str(e)}")
            return ViolationType.UNAUTHORIZED_USE
    
    async def _store_violations(self, violations: List[ViolationAlert]):
        """Store violations in database"""
        try:
            if not violations:
                return
                
            async with get_session() as session:
                for violation in violations:
                    violation_record = {
                        "violation_id": violation.violation_id,
                        "user_id": violation.user_id,
                        "original_content_id": violation.original_content_id,
                        "violation_type": violation.violation_type.value,
                        "platform": violation.platform.value,
                        "detected_url": violation.detected_url,
                        "similarity_score": violation.similarity_score,
                        "detected_at": violation.detected_at,
                        "status": violation.status,
                        "screenshot_url": violation.screenshot_url,
                        "metadata": json.dumps(violation.metadata),
                        "created_at": datetime.utcnow()
                    }
                    
                    # Check if violation already exists
                    existing = await session.execute(
                        select("content_violations").where("violation_id" == violation.violation_id)
                    )
                    
                    if not existing.fetchone():
                        stmt = insert("content_violations").values(**violation_record)
                        await session.execute(stmt)
                
                await session.commit()
                logger.info(f"Stored {len(violations)} violations")
                
        except Exception as e:
            logger.error(f"Failed to store violations: {str(e)}")
    
    async def _notify_violations(self, violations: List[ViolationAlert]):
        """Send notifications for violations"""
        try:
            for violation in violations:
                if self.config.notification_enabled:
                    await self.notification_service.send_violation_alert(violation)
                    
        except Exception as e:
            logger.error(f"Violation notifications failed: {str(e)}")
    
    async def _update_last_scan(self, content_id: str):
        """Update last scan timestamp"""
        try:
            async with get_session() as session:
                stmt = update("content_monitoring").where(
                    "content_id" == content_id
                ).values(last_scan=datetime.utcnow())
                await session.execute(stmt)
                await session.commit()
                
        except Exception as e:
            logger.error(f"Failed to update last scan: {str(e)}")
    
    async def _add_to_vector_index(self, content_id: str, vector: np.ndarray):
        """Add content vector to FAISS index for similarity search"""
        try:
            if self.vector_index is None and len(vector) > 0:
                # Initialize FAISS index
                dimension = len(vector)
                self.vector_index = faiss.IndexFlatL2(dimension)
            
            if self.vector_index is not None and len(vector) > 0:
                # Add vector to index
                vector_2d = vector.reshape(1, -1).astype(np.float32)
                self.vector_index.add(vector_2d)
                self.content_vectors[content_id] = len(self.content_vectors)
                
        except Exception as e:
            logger.error(f"Failed to add vector to index: {str(e)}")
    
    async def cleanup(self):
        """Clean up resources"""
        try:
            for crawler in self.crawlers.values():
                await crawler._close_resources()
                
        except Exception as e:
            logger.error(f"Cleanup failed: {str(e)}")
