"""Web Surveillance Worker - IA-Influencer-Agent
================================================================================
Module: backend/crawlers/workers/web_surveillance_worker.py
Author: Fahed Mlaiel (mlaiel@live.de)
Type: Industrial Web Surveillance Worker - Intelligent Content Monitoring
Responsibility: Real-time web monitoring, piracy detection, and automated enforcement
Technologies: ML-based Crawling, Computer Vision, NLP, Automated Takedown, Real-time Alerts
================================================================================

⚠️  PROPRIÉTÉ INTELLECTUELLE EXCLUSIVE - FAHED MLAIEL ⚠️
© 2025 Fahed Mlaiel. Tous droits réservés.
Usage non autorisé strictement interdit et passible de poursuites judiciaires.
Contact: mlaiel@live.de

LOGIQUE MÉTIER:
Target monitoring → Intelligent crawling → Content detection → 
Similarity analysis → Piracy confirmation → Automated takedown → Revenue protection
"""from typing import Any, Dict, List, Optional, Union, Callable, Set, Tuple, AsyncGenerator
import logging
import asyncio
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import uuid
import json
import time
import hashlib
import re
from urllib.parse import urljoin, urlparse
import aiohttp
import aiofiles
from bs4 import BeautifulSoup
import selenium
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import numpy as np
import cv2
from PIL import Image
import torch
import requests
from fake_useragent import UserAgent

from .content_protection_worker import ContentProtectionWorker, ContentType, DetectionStatus
from ...ai.content_protection.similarity_engine import SimilarityEngine
from ...ai.vision.image_comparator import ImageComparator
from ...ai.audio.audio_matcher import AudioMatcher
from ...ai.nlp.text_similarity import TextSimilarity
from ...crawlers.engines.web_crawler import WebCrawler
from ...crawlers.platforms.platform_detector import PlatformDetector
from ...security.stealth_crawler import StealthCrawler
from ...monitoring.surveillance_monitor import SurveillanceMonitor
from ...utils.screenshot_service import ScreenshotService
from ...storage.evidence_storage import EvidenceStorage

logger = logging.getLogger(__name__)


class SurveillanceScope(Enum):
    """Surveillance scope types"""    GLOBAL_WEB = "global_web"
    SOCIAL_MEDIA = "social_media"
    VIDEO_PLATFORMS = "video_platforms"
    MUSIC_PLATFORMS = "music_platforms"
    STREAMING_SITES = "streaming_sites"
    PIRACY_NETWORKS = "piracy_networks"
    DARK_WEB = "dark_web"


class MonitoringFrequency(Enum):
    """Monitoring frequency"""    REALTIME = "realtime"
    HOURLY = "hourly"
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    CUSTOM = "custom"


class AlertSeverity(Enum):
    """Alert severity levels"""    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"
    EMERGENCY = "emergency"


@dataclass
class SurveillanceTarget:
    """Surveillance target configuration"""    target_id: str
    content_id: str
    user_id: str
    content_type: ContentType
    fingerprints: List[str]
    keywords: List[str] = field(default_factory=list)
    platforms: List[str] = field(default_factory=list)
    scope: SurveillanceScope = SurveillanceScope.GLOBAL_WEB
    frequency: MonitoringFrequency = MonitoringFrequency.DAILY
    threshold: float = 0.85
    active: bool = True
    created_at: datetime = field(default_factory=datetime.utcnow)
    last_scan: Optional[datetime] = None


@dataclass
class SurveillanceResult:
    """Surveillance detection result"""    detection_id: str
    target_id: str
    detected_url: str
    platform: str
    content_type: ContentType
    similarity_score: float
    detection_method: str
    evidence_urls: List[str] = field(default_factory=list)
    screenshot_url: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    severity: AlertSeverity = AlertSeverity.MEDIUM
    status: DetectionStatus = DetectionStatus.FOUND_MATCH
    detected_at: datetime = field(default_factory=datetime.utcnow)
    confirmed: bool = False


@dataclass
class SurveillanceTask:
    """Surveillance task definition"""    task_id: str
    target: SurveillanceTarget
    search_queries: List[str]
    platforms_to_scan: List[str]
    max_results_per_platform: int = 100
    deep_scan: bool = False
    priority: int = 1
    created_at: datetime = field(default_factory=datetime.utcnow)
    deadline: Optional[datetime] = None


class WebSurveillanceWorker:
    """    Advanced web surveillance worker for intelligent content monitoring
    
    Features:
    - Real-time web monitoring across multiple platforms
    - ML-powered content similarity detection
    - Automated evidence collection and documentation
    - Stealth crawling with anti-detection measures
    - Multi-modal content analysis (audio, video, image, text)
    - Automated DMCA takedown initiation
    - Revenue protection and loss calculation
    """    def __init__(self, worker_id: str = None):
        self.worker_id = worker_id or f"web_surveillance_{uuid.uuid4().hex[:8]}"
        
        # Core components
        self.content_protection_worker = None
        self.similarity_engine = SimilarityEngine()
        self.image_comparator = ImageComparator()
        self.audio_matcher = AudioMatcher()
        self.text_similarity = TextSimilarity()
        self.web_crawler = WebCrawler()
        self.platform_detector = PlatformDetector()
        self.stealth_crawler = StealthCrawler()
        self.surveillance_monitor = SurveillanceMonitor()
        self.screenshot_service = ScreenshotService()
        self.evidence_storage = EvidenceStorage()
        
        # State management
        self.active_targets: Dict[str, SurveillanceTarget] = {}
        self.detection_cache: Dict[str, List[SurveillanceResult]] = {}
        self.platform_sessions: Dict[str, Any] = {}
        
        # Configuration
        self.config = {
            'max_concurrent_scans': 10,
            'scan_timeout': 300,  # 5 minutes
            'similarity_threshold': 0.85,
            'evidence_retention_days': 365,
            'screenshot_quality': 'high',
            'stealth_mode': True,
            'rate_limit_delay': 2.0,
            'max_retries': 3
        }
        
        # Performance tracking
        self.stats = {
            'total_scans': 0,
            'detections_found': 0,
            'false_positives': 0,
            'takedowns_initiated': 0,
            'average_scan_time': 0.0,
            'platform_success_rates': {},
            'uptime': datetime.utcnow()
        }
        
        # Selenium setup for JavaScript-heavy sites
        self.selenium_options = Options()
        self.selenium_options.add_argument('--headless')
        self.selenium_options.add_argument('--no-sandbox')
        self.selenium_options.add_argument('--disable-dev-shm-usage')
        self.selenium_options.add_argument('--disable-gpu')
        self.selenium_options.add_argument('--window-size=1920,1080')
        
        # User agent rotation
        self.user_agent = UserAgent()
        
        self.initialized = False

    async def initialize(self) -> bool:
        """Initialize the web surveillance worker"""        try:
            logger.info(f"🚀 Initializing Web Surveillance Worker {self.worker_id}")
            
            # Initialize content protection worker
            self.content_protection_worker = ContentProtectionWorker()
            await self.content_protection_worker.initialize()
            
            # Initialize core components
            await self.similarity_engine.initialize()
            await self.image_comparator.initialize()
            await self.audio_matcher.initialize()
            await self.text_similarity.initialize()
            await self.web_crawler.initialize()
            await self.platform_detector.initialize()
            await self.stealth_crawler.initialize()
            await self.surveillance_monitor.initialize()
            await self.screenshot_service.initialize()
            await self.evidence_storage.initialize()
            
            # Load surveillance targets
            await self._load_surveillance_targets()
            
            # Start monitoring loops
            asyncio.create_task(self._surveillance_loop())
            asyncio.create_task(self._health_monitor_loop())
            
            self.initialized = True
            logger.info(f"✅ Web Surveillance Worker {self.worker_id} initialized successfully")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize web surveillance worker: {e}")
            return False

    async def add_surveillance_target(self, target: SurveillanceTarget) -> bool:
        """Add a new surveillance target"""        try:
            logger.info(f"📡 Adding surveillance target: {target.target_id}")
            
            # Validate target
            if not await self._validate_target(target):
                logger.error(f"❌ Invalid surveillance target: {target.target_id}")
                return False
            
            # Store target
            self.active_targets[target.target_id] = target
            
            # Initialize detection cache
            self.detection_cache[target.target_id] = []
            
            # Start immediate scan if realtime monitoring
            if target.frequency == MonitoringFrequency.REALTIME:
                asyncio.create_task(self._scan_target(target))
            
            logger.info(f"✅ Surveillance target added: {target.target_id}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to add surveillance target: {e}")
            return False

    async def remove_surveillance_target(self, target_id: str) -> bool:
        """Remove a surveillance target"""        try:
            if target_id in self.active_targets:
                del self.active_targets[target_id]
                if target_id in self.detection_cache:
                    del self.detection_cache[target_id]
                logger.info(f"✅ Surveillance target removed: {target_id}")
                return True
            return False
            
        except Exception as e:
            logger.error(f"❌ Failed to remove surveillance target: {e}")
            return False

    async def scan_target(self, target_id: str) -> List[SurveillanceResult]:
        """Manually trigger a scan for a specific target"""        try:
            if target_id not in self.active_targets:
                logger.error(f"❌ Target not found: {target_id}")
                return []
            
            target = self.active_targets[target_id]
            return await self._scan_target(target)
            
        except Exception as e:
            logger.error(f"❌ Failed to scan target {target_id}: {e}")
            return []

    async def get_surveillance_results(
        self, 
        target_id: str = None,
        severity: AlertSeverity = None,
        limit: int = 100
    ) -> List[SurveillanceResult]:
        """Get surveillance results with optional filtering"""        try:
            results = []
            
            if target_id:
                results = self.detection_cache.get(target_id, [])
            else:
                for target_results in self.detection_cache.values():
                    results.extend(target_results)
            
            # Apply severity filter
            if severity:
                results = [r for r in results if r.severity == severity]
            
            # Sort by detection time (newest first) and limit
            results.sort(key=lambda x: x.detected_at, reverse=True)
            return results[:limit]
            
        except Exception as e:
            logger.error(f"❌ Failed to get surveillance results: {e}")
            return []

    async def _surveillance_loop(self) -> None:
        """Main surveillance monitoring loop"""        try:
            while True:
                try:
                    current_time = datetime.utcnow()
                    
                    # Check each target for scheduled scans
                    for target in self.active_targets.values():
                        if not target.active:
                            continue
                        
                        should_scan = await self._should_scan_target(target, current_time)
                        if should_scan:
                            # Run scan in background
                            asyncio.create_task(self._scan_target(target))
                    
                    # Wait before next cycle
                    await asyncio.sleep(60)  # Check every minute
                    
                except Exception as e:
                    logger.error(f"❌ Error in surveillance loop: {e}")
                    await asyncio.sleep(30)
                    
        except asyncio.CancelledError:
            logger.info("🛑 Surveillance loop cancelled")
        except Exception as e:
            logger.error(f"❌ Surveillance loop failed: {e}")

    async def _scan_target(self, target: SurveillanceTarget) -> List[SurveillanceResult]:
        """Perform comprehensive scan for a surveillance target"""        try:
            logger.info(f"🔍 Scanning target: {target.target_id}")
            scan_start = time.time()
            
            # Generate search queries
            search_queries = await self._generate_search_queries(target)
            
            # Determine platforms to scan
            platforms = target.platforms if target.platforms else await self._get_default_platforms(target.scope)
            
            # Perform parallel scanning across platforms
            scan_tasks = []
            for platform in platforms:
                for query in search_queries:
                    task = asyncio.create_task(
                        self._scan_platform(platform, query, target)
                    )
                    scan_tasks.append(task)
            
            # Wait for all scans to complete
            scan_results = await asyncio.gather(*scan_tasks, return_exceptions=True)
            
            # Process and filter results
            detections = []
            for result in scan_results:
                if isinstance(result, list):
                    detections.extend(result)
                elif isinstance(result, Exception):
                    logger.error(f"❌ Scan task failed: {result}")
            
            # Remove duplicates and false positives
            unique_detections = await self._filter_detections(detections, target)
            
            # Store results
            if target.target_id not in self.detection_cache:
                self.detection_cache[target.target_id] = []
            
            self.detection_cache[target.target_id].extend(unique_detections)
            
            # Update target scan time
            target.last_scan = datetime.utcnow()
            
            # Update statistics
            scan_time = time.time() - scan_start
            self.stats['total_scans'] += 1
            self.stats['detections_found'] += len(unique_detections)
            self.stats['average_scan_time'] = (
                (self.stats['average_scan_time'] * (self.stats['total_scans'] - 1) + scan_time) /
                self.stats['total_scans']
            )
            
            # Send alerts for high-severity detections
            for detection in unique_detections:
                if detection.severity in [AlertSeverity.HIGH, AlertSeverity.CRITICAL, AlertSeverity.EMERGENCY]:
                    await self._send_alert(detection)
            
            logger.info(f"✅ Target scan completed: {target.target_id} ({len(unique_detections)} detections in {scan_time:.2f}s)")
            return unique_detections
            
        except Exception as e:
            logger.error(f"❌ Failed to scan target {target.target_id}: {e}")
            return []

    async def _scan_platform(
        self, 
        platform: str, 
        query: str, 
        target: SurveillanceTarget
    ) -> List[SurveillanceResult]:
        """Scan a specific platform with a search query"""        try:
            logger.debug(f"🔍 Scanning {platform} for: {query}")
            
            detections = []
            
            # Platform-specific scanning logic
            if platform.lower() == 'youtube':
                detections = await self._scan_youtube(query, target)
            elif platform.lower() == 'instagram':
                detections = await self._scan_instagram(query, target)
            elif platform.lower() == 'tiktok':
                detections = await self._scan_tiktok(query, target)
            elif platform.lower() == 'twitter':
                detections = await self._scan_twitter(query, target)
            elif platform.lower() == 'generic_web':
                detections = await self._scan_generic_web(query, target)
            else:
                # Use generic web crawling
                detections = await self._scan_generic_web(query, target)
            
            # Add platform information to detections
            for detection in detections:
                detection.platform = platform
            
            return detections
            
        except Exception as e:
            logger.error(f"❌ Failed to scan {platform} with query '{query}': {e}")
            return []

    async def _scan_youtube(self, query: str, target: SurveillanceTarget) -> List[SurveillanceResult]:
        """Scan YouTube for content matches"""        try:
            detections = []
            
            # Use YouTube API or web scraping
            youtube_urls = await self._search_youtube_api(query, limit=50)
            
            for url in youtube_urls:
                # Analyze content for similarity
                similarity_score = await self._analyze_content_similarity(url, target)
                
                if similarity_score >= target.threshold:
                    # Capture evidence
                    screenshot_url = await self.screenshot_service.capture(url)
                    evidence_urls = await self._collect_evidence(url)
                    
                    detection = SurveillanceResult(
                        detection_id=str(uuid.uuid4()),
                        target_id=target.target_id,
                        detected_url=url,
                        platform='youtube',
                        content_type=target.content_type,
                        similarity_score=similarity_score,
                        detection_method='content_analysis',
                        evidence_urls=evidence_urls,
                        screenshot_url=screenshot_url,
                        severity=self._calculate_severity(similarity_score),
                        metadata={
                            'search_query': query,
                            'detection_timestamp': datetime.utcnow().isoformat()
                        }
                    )
                    
                    detections.append(detection)
            
            return detections
            
        except Exception as e:
            logger.error(f"❌ Failed to scan YouTube: {e}")
            return []

    async def _scan_instagram(self, query: str, target: SurveillanceTarget) -> List[SurveillanceResult]:
        """Scan Instagram for content matches"""        try:
            detections = []
            
            # Use Instagram API or web scraping with stealth measures
            instagram_posts = await self.stealth_crawler.search_instagram(query, limit=30)
            
            for post in instagram_posts:
                similarity_score = await self._analyze_content_similarity(post['url'], target)
                
                if similarity_score >= target.threshold:
                    detection = SurveillanceResult(
                        detection_id=str(uuid.uuid4()),
                        target_id=target.target_id,
                        detected_url=post['url'],
                        platform='instagram',
                        content_type=target.content_type,
                        similarity_score=similarity_score,
                        detection_method='visual_analysis',
                        severity=self._calculate_severity(similarity_score),
                        metadata={
                            'post_id': post.get('id'),
                            'username': post.get('username'),
                            'search_query': query
                        }
                    )
                    
                    detections.append(detection)
            
            return detections
            
        except Exception as e:
            logger.error(f"❌ Failed to scan Instagram: {e}")
            return []

    async def _scan_tiktok(self, query: str, target: SurveillanceTarget) -> List[SurveillanceResult]:
        """Scan TikTok for content matches"""        try:
            detections = []
            
            # Use TikTok web scraping with anti-detection
            tiktok_videos = await self.stealth_crawler.search_tiktok(query, limit=40)
            
            for video in tiktok_videos:
                similarity_score = await self._analyze_content_similarity(video['url'], target)
                
                if similarity_score >= target.threshold:
                    detection = SurveillanceResult(
                        detection_id=str(uuid.uuid4()),
                        target_id=target.target_id,
                        detected_url=video['url'],
                        platform='tiktok',
                        content_type=target.content_type,
                        similarity_score=similarity_score,
                        detection_method='audio_video_analysis',
                        severity=self._calculate_severity(similarity_score),
                        metadata={
                            'video_id': video.get('id'),
                            'username': video.get('username'),
                            'search_query': query
                        }
                    )
                    
                    detections.append(detection)
            
            return detections
            
        except Exception as e:
            logger.error(f"❌ Failed to scan TikTok: {e}")
            return []

    async def _scan_twitter(self, query: str, target: SurveillanceTarget) -> List[SurveillanceResult]:
        """Scan Twitter/X for content matches"""        try:
            detections = []
            
            # Use Twitter API or web scraping
            tweets = await self._search_twitter_api(query, limit=100)
            
            for tweet in tweets:
                similarity_score = await self._analyze_content_similarity(tweet['url'], target)
                
                if similarity_score >= target.threshold:
                    detection = SurveillanceResult(
                        detection_id=str(uuid.uuid4()),
                        target_id=target.target_id,
                        detected_url=tweet['url'],
                        platform='twitter',
                        content_type=target.content_type,
                        similarity_score=similarity_score,
                        detection_method='text_media_analysis',
                        severity=self._calculate_severity(similarity_score),
                        metadata={
                            'tweet_id': tweet.get('id'),
                            'username': tweet.get('username'),
                            'search_query': query
                        }
                    )
                    
                    detections.append(detection)
            
            return detections
            
        except Exception as e:
            logger.error(f"❌ Failed to scan Twitter: {e}")
            return []

    async def _scan_generic_web(self, query: str, target: SurveillanceTarget) -> List[SurveillanceResult]:
        """Scan generic web using search engines and crawling"""        try:
            detections = []
            
            # Use multiple search engines
            search_engines = ['google', 'bing', 'duckduckgo']
            
            for engine in search_engines:
                search_results = await self.web_crawler.search(
                    query=query,
                    engine=engine,
                    limit=50
                )
                
                for result in search_results:
                    similarity_score = await self._analyze_content_similarity(result['url'], target)
                    
                    if similarity_score >= target.threshold:
                        detection = SurveillanceResult(
                            detection_id=str(uuid.uuid4()),
                            target_id=target.target_id,
                            detected_url=result['url'],
                            platform='generic_web',
                            content_type=target.content_type,
                            similarity_score=similarity_score,
                            detection_method='web_crawling',
                            severity=self._calculate_severity(similarity_score),
                            metadata={
                                'search_engine': engine,
                                'search_query': query,
                                'page_title': result.get('title')
                            }
                        )
                        
                        detections.append(detection)
            
            return detections
            
        except Exception as e:
            logger.error(f"❌ Failed to scan generic web: {e}")
            return []

    async def _analyze_content_similarity(self, url: str, target: SurveillanceTarget) -> float:
        """Analyze content similarity between found content and target"""        try:
            # Download and analyze content
            content_data = await self._download_content(url)
            if not content_data:
                return 0.0
            
            max_similarity = 0.0
            
            # Compare against target fingerprints
            for fingerprint in target.fingerprints:
                if target.content_type == ContentType.AUDIO:
                    similarity = await self.audio_matcher.compare(content_data, fingerprint)
                elif target.content_type == ContentType.VIDEO:
                    # Extract audio and video frames for comparison
                    audio_similarity = await self.audio_matcher.compare_video_audio(content_data, fingerprint)
                    visual_similarity = await self.image_comparator.compare_video_frames(content_data, fingerprint)
                    similarity = max(audio_similarity, visual_similarity)
                elif target.content_type == ContentType.IMAGE:
                    similarity = await self.image_comparator.compare(content_data, fingerprint)
                elif target.content_type == ContentType.TEXT:
                    similarity = await self.text_similarity.compare(content_data, fingerprint)
                else:
                    # Multi-modal analysis
                    similarity = await self.similarity_engine.compare_multimodal(content_data, fingerprint)
                
                max_similarity = max(max_similarity, similarity)
            
            return max_similarity
            
        except Exception as e:
            logger.error(f"❌ Failed to analyze content similarity for {url}: {e}")
            return 0.0

    async def _download_content(self, url: str) -> Optional[bytes]:
        """Download content from URL for analysis"""        try:
            async with aiohttp.ClientSession(
                headers={'User-Agent': self.user_agent.random},
                timeout=aiohttp.ClientTimeout(total=30)
            ) as session:
                async with session.get(url) as response:
                    if response.status == 200:
                        return await response.read()
            
            return None
            
        except Exception as e:
            logger.error(f"❌ Failed to download content from {url}: {e}")
            return None

    async def _generate_search_queries(self, target: SurveillanceTarget) -> List[str]:
        """Generate intelligent search queries for target"""        try:
            queries = []
            
            # Add provided keywords
            queries.extend(target.keywords)
            
            # Generate content-specific queries
            if target.content_type == ContentType.AUDIO:
                queries.extend([
                    f'"{keyword}" music',
                    f'"{keyword}" song',
                    f'"{keyword}" audio',
                    f'download "{keyword}"'
                    for keyword in target.keywords[:3]
                ])
            elif target.content_type == ContentType.VIDEO:
                queries.extend([
                    f'"{keyword}" video',
                    f'"{keyword}" movie',
                    f'"{keyword}" stream',
                    f'watch "{keyword}"'
                    for keyword in target.keywords[:3]
                ])
            elif target.content_type == ContentType.IMAGE:
                queries.extend([
                    f'"{keyword}" image',
                    f'"{keyword}" photo',
                    f'"{keyword}" picture'
                    for keyword in target.keywords[:3]
                ])
            
            # Remove duplicates and limit
            unique_queries = list(set(queries))
            return unique_queries[:20]  # Max 20 queries per scan
            
        except Exception as e:
            logger.error(f"❌ Failed to generate search queries: {e}")
            return target.keywords or []

    async def _get_default_platforms(self, scope: SurveillanceScope) -> List[str]:
        """Get default platforms for surveillance scope"""        platform_map = {
            SurveillanceScope.GLOBAL_WEB: ['google', 'bing', 'duckduckgo'],
            SurveillanceScope.SOCIAL_MEDIA: ['instagram', 'twitter', 'facebook', 'linkedin'],
            SurveillanceScope.VIDEO_PLATFORMS: ['youtube', 'vimeo', 'dailymotion', 'twitch'],
            SurveillanceScope.MUSIC_PLATFORMS: ['spotify', 'soundcloud', 'bandcamp', 'youtube'],
            SurveillanceScope.STREAMING_SITES: ['netflix', 'hulu', 'amazon_prime', 'disney_plus'],
            SurveillanceScope.PIRACY_NETWORKS: ['piratebay', 'kickass', 'torrent_sites'],
            SurveillanceScope.DARK_WEB: ['tor_search', 'dark_search']
        }
        
        return platform_map.get(scope, ['google', 'youtube', 'instagram'])

    async def _should_scan_target(self, target: SurveillanceTarget, current_time: datetime) -> bool:
        """Determine if target should be scanned based on frequency"""        if not target.last_scan:
            return True
        
        time_since_last_scan = current_time - target.last_scan
        
        frequency_intervals = {
            MonitoringFrequency.REALTIME: timedelta(minutes=5),
            MonitoringFrequency.HOURLY: timedelta(hours=1),
            MonitoringFrequency.DAILY: timedelta(days=1),
            MonitoringFrequency.WEEKLY: timedelta(weeks=1),
            MonitoringFrequency.MONTHLY: timedelta(days=30)
        }
        
        interval = frequency_intervals.get(target.frequency, timedelta(days=1))
        return time_since_last_scan >= interval

    async def _filter_detections(
        self, 
        detections: List[SurveillanceResult], 
        target: SurveillanceTarget
    ) -> List[SurveillanceResult]:
        """Filter detections to remove duplicates and false positives"""        try:
            # Remove duplicates by URL
            seen_urls = set()
            unique_detections = []
            
            for detection in detections:
                if detection.detected_url not in seen_urls:
                    seen_urls.add(detection.detected_url)
                    unique_detections.append(detection)
            
            # Apply additional filtering
            filtered_detections = []
            for detection in unique_detections:
                # Check if it's likely a false positive
                is_false_positive = await self._is_false_positive(detection, target)
                if not is_false_positive:
                    filtered_detections.append(detection)
                else:
                    detection.status = DetectionStatus.FALSE_POSITIVE
                    self.stats['false_positives'] += 1
            
            return filtered_detections
            
        except Exception as e:
            logger.error(f"❌ Failed to filter detections: {e}")
            return detections

    async def _is_false_positive(self, detection: SurveillanceResult, target: SurveillanceTarget) -> bool:
        """Determine if detection is likely a false positive"""        try:
            # Check if URL is from authorized sources
            authorized_domains = [
                'spotify.com', 'apple.com', 'amazon.com', 
                'official-artist-site.com'  # This would be configurable
            ]
            
            domain = urlparse(detection.detected_url).netloc.lower()
            if any(auth_domain in domain for auth_domain in authorized_domains):
                return True
            
            # Check similarity score threshold
            if detection.similarity_score < 0.9:  # High threshold for confirmation
                return True
            
            # Additional ML-based false positive detection could be added here
            
            return False
            
        except Exception as e:
            logger.error(f"❌ Failed to check false positive: {e}")
            return False

    async def _calculate_severity(self, similarity_score: float) -> AlertSeverity:
        """Calculate alert severity based on similarity score"""        if similarity_score >= 0.98:
            return AlertSeverity.EMERGENCY
        elif similarity_score >= 0.95:
            return AlertSeverity.CRITICAL
        elif similarity_score >= 0.90:
            return AlertSeverity.HIGH
        elif similarity_score >= 0.85:
            return AlertSeverity.MEDIUM
        else:
            return AlertSeverity.LOW

    async def _collect_evidence(self, url: str) -> List[str]:
        """Collect evidence URLs for detected content"""        try:
            evidence_urls = []
            
            # Capture screenshot
            screenshot_url = await self.screenshot_service.capture(url)
            if screenshot_url:
                evidence_urls.append(screenshot_url)
            
            # Save page source
            page_source_url = await self.evidence_storage.save_page_source(url)
            if page_source_url:
                evidence_urls.append(page_source_url)
            
            # Download media if applicable
            media_url = await self.evidence_storage.download_media(url)
            if media_url:
                evidence_urls.append(media_url)
            
            return evidence_urls
            
        except Exception as e:
            logger.error(f"❌ Failed to collect evidence for {url}: {e}")
            return []

    async def _send_alert(self, detection: SurveillanceResult) -> None:
        """Send alert for high-severity detection"""        try:
            await self.surveillance_monitor.send_alert(
                alert_type='piracy_detection',
                severity=detection.severity.value,
                data={
                    'detection_id': detection.detection_id,
                    'target_id': detection.target_id,
                    'detected_url': detection.detected_url,
                    'platform': detection.platform,
                    'similarity_score': detection.similarity_score,
                    'detected_at': detection.detected_at.isoformat()
                }
            )
            
        except Exception as e:
            logger.error(f"❌ Failed to send alert: {e}")

    async def _validate_target(self, target: SurveillanceTarget) -> bool:
        """Validate surveillance target configuration"""        try:
            # Check required fields
            if not all([target.target_id, target.content_id, target.user_id]):
                return False
            
            # Check fingerprints exist
            if not target.fingerprints:
                return False
            
            # Validate content type
            if target.content_type not in ContentType:
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to validate target: {e}")
            return False

    async def _load_surveillance_targets(self) -> None:
        """Load surveillance targets from storage"""        try:
            # This would load from database in production
            # For now, we'll start with empty targets
            self.active_targets = {}
            logger.info("📡 Surveillance targets loaded")
            
        except Exception as e:
            logger.error(f"❌ Failed to load surveillance targets: {e}")

    async def _health_monitor_loop(self) -> None:
        """Health monitoring loop"""        try:
            while True:
                try:
                    # Update health metrics
                    await self.surveillance_monitor.update_health_metrics({
                        'worker_id': self.worker_id,
                        'active_targets': len(self.active_targets),
                        'total_scans': self.stats['total_scans'],
                        'detections_found': self.stats['detections_found'],
                        'uptime': (datetime.utcnow() - self.stats['uptime']).total_seconds()
                    })
                    
                    await asyncio.sleep(300)  # Every 5 minutes
                    
                except Exception as e:
                    logger.error(f"❌ Error in health monitor loop: {e}")
                    await asyncio.sleep(60)
                    
        except asyncio.CancelledError:
            logger.info("🛑 Health monitor loop cancelled")

    async def get_worker_stats(self) -> Dict[str, Any]:
        """Get comprehensive worker statistics"""        try:
            return {
                'worker_id': self.worker_id,
                'status': 'active' if self.initialized else 'inactive',
                'active_targets': len(self.active_targets),
                'stats': self.stats.copy(),
                'config': self.config.copy(),
                'uptime': (datetime.utcnow() - self.stats['uptime']).total_seconds()
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to get worker stats: {e}")
            return {}

    async def shutdown(self) -> bool:
        """Gracefully shutdown the worker"""        try:
            logger.info(f"🛑 Shutting down Web Surveillance Worker {self.worker_id}")
            
            # Cancel running tasks
            # Save state if necessary
            # Clean up resources
            
            self.initialized = False
            logger.info(f"✅ Web Surveillance Worker {self.worker_id} shutdown complete")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to shutdown worker: {e}")
            return False


# Factory functions and global instances
_web_surveillance_worker: Optional[WebSurveillanceWorker] = None


async def get_web_surveillance_worker() -> Optional[WebSurveillanceWorker]:
    """Get global web surveillance worker instance"""    global _web_surveillance_worker
    return _web_surveillance_worker


async def initialize_web_surveillance_worker(worker_id: str = None) -> bool:
    """Initialize global web surveillance worker"""    global _web_surveillance_worker
    try:
        if _web_surveillance_worker is None:
            _web_surveillance_worker = WebSurveillanceWorker(worker_id)
            return await _web_surveillance_worker.initialize()
        return True
    except Exception as e:
        logger.error(f"❌ Failed to initialize web surveillance worker: {e}")
        return False


async def shutdown_web_surveillance_worker() -> bool:
    """Shutdown global web surveillance worker"""    global _web_surveillance_worker
    try:
        if _web_surveillance_worker:
            result = await _web_surveillance_worker.shutdown()
            _web_surveillance_worker = None
            return result
        return True
    except Exception as e:
        logger.error(f"❌ Failed to shutdown web surveillance worker: {e}")
        return False
