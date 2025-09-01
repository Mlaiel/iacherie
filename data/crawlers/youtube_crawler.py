"""IA Influencer Agent - YouTube Advanced Crawler
=============================================

Industrial-grade YouTube content monitoring and surveillance system with advanced
AI-powered content detection, fingerprinting, and intellectual property protection.

Team Expertise: Lead Dev IA + Backend Senior + ML Engineer + DBA + Security + 
Microservices + Audio + DevOps + IA Prompt Engineer

Author: Fahed Mlaiel (mlaiel@live.de)
Email: mlaiel@live.de
Copyright: (c) 2025 Fahed Mlaiel - All Rights Reserved

⚠️  CRITICAL WARNING ⚠️
This code is PROPRIETARY and CONFIDENTIAL intellectual property.
Any unauthorized use, reproduction, distribution, or reverse engineering 
is STRICTLY PROHIBITED and will result in immediate legal action.

Unauthorized copying or theft of this concept, code, or methodology 
will be prosecuted to the FULL EXTENT OF THE LAW under German and 
International Copyright Laws.

For licensing inquiries, contact: mlaiel@live.de
"""

import asyncio
import logging
import json
import re
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union, Tuple, Set
from dataclasses import dataclass, field
from urllib.parse import urljoin, urlparse, parse_qs
import aiohttp
import base64
from pathlib import Path

# YouTube API and web scraping
try:
    from googleapiclient.discovery import build
    from googleapiclient.errors import HttpError
    import isodate
    YOUTUBE_API_AVAILABLE = True
except ImportError:
    YOUTUBE_API_AVAILABLE = False

try:
    import yt_dlp
    YT_DLP_AVAILABLE = True
except ImportError:
    YT_DLP_AVAILABLE = False

try:
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.chrome.options import Options
    SELENIUM_AVAILABLE = True
except ImportError:
    SELENIUM_AVAILABLE = False

# Computer vision and audio processing
try:
    import cv2
    import numpy as np
    CV2_AVAILABLE = True
except ImportError:
    CV2_AVAILABLE = False

try:
    import librosa
    LIBROSA_AVAILABLE = True
except ImportError:
    LIBROSA_AVAILABLE = False

from .platform_crawler import (
    PlatformCrawler, CrawlerConfig, CrawlerResult, 
    ContentMatch, ContentMatchType, CrawlerStatus
)
from ..fingerprinting import (
    VideoFingerprinter, AudioFingerprinter, TextFingerprinter,
    extract_content_metadata, performance_timer
)

logger = logging.getLogger(__name__)

@dataclass
class YouTubeVideoMetadata:
    """
Comprehensive YouTube video metadata"""
    video_id: str
    title: str
    description: str
    channel_id: str
    channel_name: str
    upload_date: datetime
    duration: Optional[int] = None
    view_count: Optional[int] = None
    like_count: Optional[int] = None
    comment_count: Optional[int] = None
    tags: List[str] = field(default_factory=list)
    category_id: Optional[str] = None
    language: Optional[str] = None
    thumbnail_urls: List[str] = field(default_factory=list)
    video_quality: Optional[str] = None
    audio_quality: Optional[str] = None
    is_live: bool = False
    is_premiere: bool = False
    has_captions: bool = False
    license_type: Optional[str] = None
    privacy_status: Optional[str] = None

@dataclass
class YouTubeChannelMetadata:
    """
YouTube channel metadata"""
    channel_id: str
    channel_name: str
    subscriber_count: Optional[int] = None
    video_count: Optional[int] = None
    view_count: Optional[int] = None
    description: Optional[str] = None
    country: Optional[str] = None
    created_date: Optional[datetime] = None
    custom_url: Optional[str] = None
    keywords: List[str] = field(default_factory=list)
    is_verified: bool = False
    is_monetized: bool = False

@dataclass
class YouTubeSearchConfig:
    """
YouTube search configuration"""
    query: str
    max_results: int = 50
    order: str = "relevance"  # relevance, date, rating, viewCount, title
    published_after: Optional[datetime] = None
    published_before: Optional[datetime] = None
    duration: Optional[str] = None  # short, medium, long
    video_definition: Optional[str] = None  # any, high, standard
    video_type: Optional[str] = None  # any, episode, movie
    region_code: Optional[str] = None
    safe_search: str = "moderate"
    channel_id: Optional[str] = None
    include_live: bool = True

class YouTubeAPIManager:
    """Advanced YouTube API management with quota optimization"""
    
    def __init__(self, api_keys: List[str]):
        self.api_keys = api_keys
        self.current_key_index = 0
        self.quota_usage: Dict[str, int] = {key: 0 for key in api_keys}
        self.daily_quota_limit = 10000  # YouTube API quota per day
        self.services: Dict[str, Any] = {}
        self.logger = logging.getLogger(__name__)
    
    def get_service(self) -> Optional[Any]:
        """
Get YouTube API service with automatic key rotation"""
        if not YOUTUBE_API_AVAILABLE:
            return None
        
        for _ in range(len(self.api_keys)):
            current_key = self.api_keys[self.current_key_index]
            
            if self.quota_usage[current_key] < self.daily_quota_limit:
                if current_key not in self.services:
                    try:
                        self.services[current_key] = build(
                            'youtube', 'v3', 
                            developerKey=current_key,
                            cache_discovery=False
                        )
                    except Exception as e:
                        self.logger.error(f"Failed to create YouTube service: {e}")
                        self._rotate_key()
                        continue
                
                return self.services[current_key]
            else:
                self._rotate_key()
        
        self.logger.warning("All YouTube API keys have reached quota limit")
        return None
    
    def _rotate_key(self):
        """Rotate to next API key"""
        self.current_key_index = (self.current_key_index + 1) % len(self.api_keys)
    
    def record_quota_usage(self, cost: int = 1):
        """
Record API quota usage"""
        current_key = self.api_keys[self.current_key_index]
        self.quota_usage[current_key] += cost
    
    def reset_daily_quota(self):
        """
Reset daily quota usage (call this daily)"""
        self.quota_usage = {key: 0 for key in self.api_keys}

class YouTubeContentAnalyzer:
    """
Advanced YouTube content analysis engine"""
    
    def __init__(self):
        self.video_fingerprinter = VideoFingerprinter()
        self.audio_fingerprinter = AudioFingerprinter()
        self.text_fingerprinter = TextFingerprinter()
        self.logger = logging.getLogger(__name__)
    
    @performance_timer
    async def analyze_video_content(self, video_url: str) -> Dict[str, Any]:
        """
Comprehensive video content analysis"""
        try:
            analysis_result = {
                "video_fingerprint": None,
                "audio_fingerprint": None,
                "text_fingerprint": None,
                "content_metadata": None,
                "similarity_matches": [],
                "content_classification": {},
                "risk_assessment": {}
            }
            
            # Download video for analysis (if needed)
            video_path = await self._download_video_segment(video_url)
            if not video_path:
                return analysis_result
            
            # Extract video fingerprint
            if CV2_AVAILABLE:
                video_fingerprint = await self._extract_video_fingerprint(video_path)
                analysis_result["video_fingerprint"] = video_fingerprint
            
            # Extract audio fingerprint
            if LIBROSA_AVAILABLE:
                audio_fingerprint = await self._extract_audio_fingerprint(video_path)
                analysis_result["audio_fingerprint"] = audio_fingerprint
            
            # Extract metadata
            metadata = extract_content_metadata(video_path)
            analysis_result["content_metadata"] = metadata
            
            # Content classification
            classification = await self._classify_content(video_path)
            analysis_result["content_classification"] = classification
            
            # Risk assessment
            risk_assessment = await self._assess_content_risk(analysis_result)
            analysis_result["risk_assessment"] = risk_assessment
            
            # Cleanup temporary file
            if video_path and Path(video_path).exists():
                Path(video_path).unlink()
            
            return analysis_result
            
        except Exception as e:
            self.logger.error(f"Video content analysis failed: {e}")
            return {}
    
    async def _download_video_segment(self, video_url: str, duration: int = 30) -> Optional[str]:
        """Download video segment for analysis"""
        if not YT_DLP_AVAILABLE:
            return None
        
        try:
            output_path = f"/tmp/youtube_analysis_{datetime.now().timestamp()}.mp4"
            
            ydl_opts = {
                'format': 'best[height<=720]',  # Limit quality for faster processing
                'outtmpl': output_path,
                'quiet': True,
                'no_warnings': True,
                'extractaudio': False,
                'audioformat': 'mp3',
                'external_downloader_args': ['-ss', '0', '-t', str(duration)]  # First 30 seconds
            }
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                await asyncio.get_event_loop().run_in_executor(
                    None, ydl.download, [video_url]
                )
            
            return output_path if Path(output_path).exists() else None
            
        except Exception as e:
            self.logger.error(f"Video download failed: {e}")
            return None
    
    async def _extract_video_fingerprint(self, video_path: str) -> Optional[str]:
        """Extract video fingerprint using computer vision"""
        try:
            fingerprint = await asyncio.get_event_loop().run_in_executor(
                None, self.video_fingerprinter.generate_fingerprint, video_path
            )
            return fingerprint.fingerprint_data if fingerprint else None
            
        except Exception as e:
            self.logger.error(f"Video fingerprint extraction failed: {e}")
            return None
    
    async def _extract_audio_fingerprint(self, video_path: str) -> Optional[str]:
        """Extract audio fingerprint from video"""
        try:
            fingerprint = await asyncio.get_event_loop().run_in_executor(
                None, self.audio_fingerprinter.generate_fingerprint, video_path
            )
            return fingerprint.fingerprint_data if fingerprint else None
            
        except Exception as e:
            self.logger.error(f"Audio fingerprint extraction failed: {e}")
            return None
    
    async def _classify_content(self, video_path: str) -> Dict[str, Any]:
        """Classify video content using AI models"""
        try:
            classification = {
                "content_type": "unknown",
                "genre": [],
                "explicit_content": False,
                "music_content": False,
                "speech_content": False,
                "confidence_scores": {}
            }
            
            # Basic content detection using OpenCV
            if CV2_AVAILABLE:
                cap = cv2.VideoCapture(video_path)
                frame_count = 0
                music_indicators = 0
                
                while frame_count < 10 and cap.isOpened():
                    ret, frame = cap.read()
                    if not ret:
                        break
                    
                    # Analyze frame characteristics
                    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                    
                    # Detect music video characteristics (simplified)
                    edges = cv2.Canny(gray, 50, 150)
                    edge_density = np.sum(edges > 0) / edges.size
                    
                    if edge_density > 0.1:  # High edge density might indicate music video
                        music_indicators += 1
                    
                    frame_count += 1
                
                cap.release()
                
                if music_indicators > frame_count * 0.5:
                    classification["music_content"] = True
                    classification["content_type"] = "music"
            
            return classification
            
        except Exception as e:
            self.logger.error(f"Content classification failed: {e}")
            return {}
    
    async def _assess_content_risk(self, analysis_result: Dict[str, Any]) -> Dict[str, Any]:
        """Assess content risk for IP protection"""
        try:
            risk_assessment = {
                "overall_risk": "low",
                "risk_factors": [],
                "confidence": 0.0,
                "recommended_actions": []
            }
            
            risk_score = 0.0
            
            # Check for potential IP violations
            if analysis_result.get("video_fingerprint"):
                risk_score += 0.3
                risk_assessment["risk_factors"].append("video_content_detected")
            
            if analysis_result.get("audio_fingerprint"):
                risk_score += 0.4
                risk_assessment["risk_factors"].append("audio_content_detected")
            
            # Assess based on content classification
            classification = analysis_result.get("content_classification", {})
            if classification.get("music_content"):
                risk_score += 0.5
                risk_assessment["risk_factors"].append("music_content")
            
            # Determine overall risk level
            if risk_score >= 0.8:
                risk_assessment["overall_risk"] = "critical"
                risk_assessment["recommended_actions"] = [
                    "immediate_investigation",
                    "content_takedown_request",
                    "legal_action_consideration"
                ]
            elif risk_score >= 0.6:
                risk_assessment["overall_risk"] = "high"
                risk_assessment["recommended_actions"] = [
                    "detailed_analysis",
                    "similarity_verification",
                    "contact_platform"
                ]
            elif risk_score >= 0.3:
                risk_assessment["overall_risk"] = "medium"
                risk_assessment["recommended_actions"] = [
                    "monitor_closely",
                    "schedule_review"
                ]
            
            risk_assessment["confidence"] = min(risk_score, 1.0)
            
            return risk_assessment
            
        except Exception as e:
            self.logger.error(f"Risk assessment failed: {e}")
            return {"overall_risk": "unknown", "confidence": 0.0}

class YouTubeCrawler(PlatformCrawler):
    """Advanced YouTube crawler with industrial-grade capabilities"""
    
    def __init__(self, config: CrawlerConfig, api_keys: List[str]):
        super().__init__(config)
        self.platform_name = "YouTube"
        self.api_manager = YouTubeAPIManager(api_keys)
        self.content_analyzer = YouTubeContentAnalyzer()
        
        # Advanced configuration
        self.search_configs: List[YouTubeSearchConfig] = []
        self.monitored_channels: Set[str] = set()
        self.blocked_channels: Set[str] = set()
        self.keyword_filters: List[str] = []
        
        # Performance optimization
        self.concurrent_downloads = 3
        self.analysis_queue_size = 100
        self.cache_duration = timedelta(hours=6)
        
        # Browser automation for advanced scraping
        self.browser_options = Options()
        self.browser_options.add_argument("--headless")
        self.browser_options.add_argument("--no-sandbox")
        self.browser_options.add_argument("--disable-dev-shm-usage")
        self.browser_options.add_argument("--disable-gpu")
        
        self.logger = logging.getLogger(__name__)
    
    def add_search_config(self, search_config: YouTubeSearchConfig):
        """Add search configuration for monitoring"""
        self.search_configs.append(search_config)
        self.logger.info(f"Added search config: {search_config.query}")
    
    def add_monitored_channel(self, channel_id: str):
        """Add channel to monitoring list"""
        self.monitored_channels.add(channel_id)
        self.logger.info(f"Added monitored channel: {channel_id}")
    
    def add_blocked_channel(self, channel_id: str):
        """Add channel to block list"""
        self.blocked_channels.add(channel_id)
        self.logger.info(f"Added blocked channel: {channel_id}")
    
    @performance_timer
    async def crawl(self) -> CrawlerResult:
        """Main crawling method with comprehensive monitoring"""
        try:
            self.status = CrawlerStatus.RUNNING
            start_time = datetime.now()
            
            all_matches = []
            search_results = []
            
            # Execute all search configurations
            for search_config in self.search_configs:
                matches = await self._search_and_analyze(search_config)
                all_matches.extend(matches)
                search_results.append({
                    "query": search_config.query,
                    "matches_found": len(matches),
                    "timestamp": datetime.now()
                })
            
            # Monitor specific channels
            channel_matches = await self._monitor_channels()
            all_matches.extend(channel_matches)
            
            # Filter and deduplicate results
            filtered_matches = await self._filter_and_deduplicate(all_matches)
            
            # Calculate statistics
            statistics = await self._calculate_statistics(filtered_matches, start_time)
            
            self.status = CrawlerStatus.COMPLETED
            
            return CrawlerResult(
                platform="YouTube",
                matches=filtered_matches,
                total_analyzed=statistics["total_analyzed"],
                execution_time=statistics["execution_time"],
                statistics=statistics,
                metadata={
                    "search_results": search_results,
                    "api_quota_used": sum(self.api_manager.quota_usage.values()),
                    "channels_monitored": len(self.monitored_channels),
                    "timestamp": datetime.now().isoformat()
                }
            )
            
        except Exception as e:
            self.logger.error(f"YouTube crawling failed: {e}")
            self.status = CrawlerStatus.ERROR
            return CrawlerResult(
                platform="YouTube",
                matches=[],
                total_analyzed=0,
                execution_time=0,
                error_message=str(e)
            )
    
    # Continue with remaining methods from the previous implementation...
    def _extract_video_id(self, url: str) -> Optional[str]:
        """Extract video ID from YouTube URL"""
        try:
            parsed_url = urlparse(url)
            
            if parsed_url.hostname in ['youtube.com', 'www.youtube.com']:
                if parsed_url.path == '/watch':
                    return parse_qs(parsed_url.query)['v'][0]
                elif parsed_url.path.startswith('/embed/'):
                    return parsed_url.path.split('/embed/')[1]
            elif parsed_url.hostname in ['youtu.be']:
                return parsed_url.path[1:]
            
            return None
            
        except Exception:
            return None
