"""
Content Monitoring System for Real-time Protection

This module provides comprehensive content monitoring capabilities:
- Real-time content surveillance across multiple platforms
- Automated detection of protected content usage
- Platform-specific monitoring strategies
- Scheduled monitoring tasks with configurable intervals
- Integration with external APIs and web scraping

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: © 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import aiohttp
from typing import Dict, List, Optional, Set, Any, Callable
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
import logging
from pathlib import Path
import json
import hashlib
from urllib.parse import urljoin, urlparse
import re

# Web scraping
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup

# Image processing for screenshot comparison
from PIL import Image
import imagehash

# Internal imports
from ...utils.logging import get_logger
from ...database.models.content import ContentFingerprint, MonitoringTask
from ...config.settings import get_settings
from .fingerprint_engine import FingerprintEngine, FingerprintResult

logger = get_logger(__name__)
settings = get_settings()


class MonitoringPlatform(Enum):
    """Supported platforms for content monitoring"""
    YOUTUBE = "youtube"
    INSTAGRAM = "instagram"
    TIKTOK = "tiktok"
    TWITTER = "twitter"
    FACEBOOK = "facebook"
    SPOTIFY = "spotify"
    SOUNDCLOUD = "soundcloud"
    TWITCH = "twitch"
    GENERIC_WEB = "generic_web"


class MonitoringStatus(Enum):
    """Status of monitoring tasks"""
    ACTIVE = "active"
    PAUSED = "paused"
    STOPPED = "stopped"
    ERROR = "error"
    RATE_LIMITED = "rate_limited"


@dataclass
class MonitoringResult:
    """Result of a monitoring scan"""
    platform: MonitoringPlatform
    detected_urls: List[str] = field(default_factory=list)
    screenshots: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    scan_duration: float = 0.0
    timestamp: datetime = field(default_factory=datetime.utcnow)
    error_message: Optional[str] = None


@dataclass
class MonitoringConfig:
    """Configuration for content monitoring"""
    platform: MonitoringPlatform
    search_terms: List[str]
    interval_minutes: int = 60
    max_results: int = 50
    deep_scan: bool = False
    screenshot_enabled: bool = True
    api_key: Optional[str] = None
    rate_limit_delay: float = 1.0


class PlatformMonitor:
    """Base class for platform-specific monitoring"""
    
    def __init__(self, config: MonitoringConfig):
        self.config = config
        self.session = None
        self.driver = None
        
    async def initialize(self):
        """Initialize monitoring resources"""
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=30),
            headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
        )
    
    async def cleanup(self):
        """Cleanup monitoring resources"""
        if self.session:
            await self.session.close()
        if self.driver:
            self.driver.quit()
    
    async def scan_content(self) -> MonitoringResult:
        """Perform content scan on platform"""
        raise NotImplementedError
    
    def _setup_selenium_driver(self) -> webdriver.Chrome:
        """Setup Selenium Chrome driver for dynamic content"""
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--window-size=1920,1080')
        
        driver = webdriver.Chrome(options=chrome_options)
        return driver


class YouTubeMonitor(PlatformMonitor):
    """YouTube content monitoring implementation"""
    
    def __init__(self, config: MonitoringConfig):
        super().__init__(config)
        self.api_base = "https://www.googleapis.com/youtube/v3"
    
    async def scan_content(self) -> MonitoringResult:
        """Scan YouTube for protected content"""
        start_time = datetime.utcnow()
        result = MonitoringResult(platform=MonitoringPlatform.YOUTUBE)
        
        try:
            if self.config.api_key:
                await self._scan_with_api(result)
            else:
                await self._scan_with_scraping(result)
                
        except Exception as e:
            result.error_message = str(e)
            logger.error(f"YouTube monitoring error: {e}")
        
        result.scan_duration = (datetime.utcnow() - start_time).total_seconds()
        return result
    
    async def _scan_with_api(self, result: MonitoringResult):
        """Scan using YouTube Data API"""
        for search_term in self.config.search_terms:
            url = f"{self.api_base}/search"
            params = {
                'part': 'snippet',
                'q': search_term,
                'type': 'video',
                'maxResults': self.config.max_results,
                'key': self.config.api_key
            }
            
            async with self.session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    for item in data.get('items', []):
                        video_id = item['id']['videoId']
                        video_url = f"https://www.youtube.com/watch?v={video_id}"
                        result.detected_urls.append(video_url)
                        
                        # Store metadata
                        snippet = item['snippet']
                        result.metadata[video_url] = {
                            'title': snippet.get('title'),
                            'channel': snippet.get('channelTitle'),
                            'published_at': snippet.get('publishedAt'),
                            'description': snippet.get('description', '')[:500]
                        }
                
                elif response.status == 403:
                    raise Exception("YouTube API quota exceeded")
                
                await asyncio.sleep(self.config.rate_limit_delay)
    
    async def _scan_with_scraping(self, result: MonitoringResult):
        """Scan using web scraping as fallback"""
        if not self.driver:
            self.driver = self._setup_selenium_driver()
        
        for search_term in self.config.search_terms:
            search_url = f"https://www.youtube.com/results?search_query={search_term.replace(' ', '+')}"
            
            self.driver.get(search_url)
            await asyncio.sleep(3)  # Wait for dynamic content
            
            # Find video links
            video_elements = self.driver.find_elements(By.CSS_SELECTOR, 'a[href*="/watch?v="]')
            
            for element in video_elements[:self.config.max_results]:
                video_url = urljoin("https://www.youtube.com", element.get_attribute('href'))
                if video_url not in result.detected_urls:
                    result.detected_urls.append(video_url)
                    
                    # Extract basic metadata
                    try:
                        title_element = element.find_element(By.CSS_SELECTOR, '#video-title')
                        title = title_element.get_attribute('title') or title_element.text
                        result.metadata[video_url] = {'title': title}
                    except:
                        pass
            
            await asyncio.sleep(self.config.rate_limit_delay)


class InstagramMonitor(PlatformMonitor):
    """Instagram content monitoring implementation"""
    
    async def scan_content(self) -> MonitoringResult:
        """Scan Instagram for protected content"""
        start_time = datetime.utcnow()
        result = MonitoringResult(platform=MonitoringPlatform.INSTAGRAM)
        
        try:
            if not self.driver:
                self.driver = self._setup_selenium_driver()
            
            for search_term in self.config.search_terms:
                # Instagram hashtag search
                search_url = f"https://www.instagram.com/explore/tags/{search_term.replace('#', '').replace(' ', '')}"
                
                self.driver.get(search_url)
                await asyncio.sleep(5)  # Wait for content load
                
                # Scroll to load more content
                if self.config.deep_scan:
                    for _ in range(3):
                        self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                        await asyncio.sleep(2)
                
                # Find post links
                post_elements = self.driver.find_elements(By.CSS_SELECTOR, 'a[href*="/p/"]')
                
                for element in post_elements[:self.config.max_results]:
                    post_url = urljoin("https://www.instagram.com", element.get_attribute('href'))
                    if post_url not in result.detected_urls:
                        result.detected_urls.append(post_url)
                        
                        # Take screenshot if enabled
                        if self.config.screenshot_enabled:
                            screenshot_path = await self._take_screenshot(element)
                            if screenshot_path:
                                result.screenshots.append(screenshot_path)
                
                await asyncio.sleep(self.config.rate_limit_delay)
                
        except Exception as e:
            result.error_message = str(e)
            logger.error(f"Instagram monitoring error: {e}")
        
        result.scan_duration = (datetime.utcnow() - start_time).total_seconds()
        return result
    
    async def _take_screenshot(self, element) -> Optional[str]:
        """Take screenshot of specific element"""
        try:
            # Scroll element into view
            self.driver.execute_script("arguments[0].scrollIntoView();", element)
            await asyncio.sleep(1)
            
            # Take screenshot
            screenshot_data = element.screenshot_as_png
            
            # Save screenshot
            timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
            screenshot_path = f"/tmp/screenshot_{timestamp}_{hashlib.md5(screenshot_data).hexdigest()[:8]}.png"
            
            with open(screenshot_path, 'wb') as f:
                f.write(screenshot_data)
            
            return screenshot_path
            
        except Exception as e:
            logger.warning(f"Screenshot failed: {e}")
            return None


class TikTokMonitor(PlatformMonitor):
    """TikTok content monitoring implementation"""
    
    async def scan_content(self) -> MonitoringResult:
        """Scan TikTok for protected content"""
        start_time = datetime.utcnow()
        result = MonitoringResult(platform=MonitoringPlatform.TIKTOK)
        
        try:
            # TikTok requires more sophisticated anti-bot measures
            # This is a simplified implementation
            
            if not self.driver:
                self.driver = self._setup_selenium_driver()
                # Add TikTok-specific settings
                self.driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
                    "source": """
                        Object.defineProperty(navigator, 'webdriver', {
                            get: () => undefined
                        })
                    """
                })
            
            for search_term in self.config.search_terms:
                search_url = f"https://www.tiktok.com/search?q={search_term.replace(' ', '%20')}"
                
                self.driver.get(search_url)
                await asyncio.sleep(5)
                
                # Handle cookie consent and overlays
                try:
                    cookie_button = WebDriverWait(self.driver, 10).until(
                        EC.element_to_be_clickable((By.CSS_SELECTOR, 'button[data-e2e="cookie-banner-accept"]'))
                    )
                    cookie_button.click()
                    await asyncio.sleep(2)
                except:
                    pass  # No cookie banner or already accepted
                
                # Find video links
                video_elements = self.driver.find_elements(By.CSS_SELECTOR, 'a[href*="/video/"]')
                
                for element in video_elements[:self.config.max_results]:
                    video_url = urljoin("https://www.tiktok.com", element.get_attribute('href'))
                    if video_url not in result.detected_urls:
                        result.detected_urls.append(video_url)
                
                await asyncio.sleep(self.config.rate_limit_delay)
                
        except Exception as e:
            result.error_message = str(e)
            logger.error(f"TikTok monitoring error: {e}")
        
        result.scan_duration = (datetime.utcnow() - start_time).total_seconds()
        return result


class TwitterMonitor(PlatformMonitor):
    """Twitter/X content monitoring implementation"""
    
    async def scan_content(self) -> MonitoringResult:
        """Scan Twitter for protected content"""
        start_time = datetime.utcnow()
        result = MonitoringResult(platform=MonitoringPlatform.TWITTER)
        
        try:
            # Twitter/X has strict API access requirements
            # This implementation uses web scraping as primary method
            
            if not self.driver:
                self.driver = self._setup_selenium_driver()
            
            for search_term in self.config.search_terms:
                search_url = f"https://twitter.com/search?q={search_term.replace(' ', '%20')}&src=typed_query&f=live"
                
                self.driver.get(search_url)
                await asyncio.sleep(5)
                
                # Scroll to load more tweets
                if self.config.deep_scan:
                    for _ in range(5):
                        self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                        await asyncio.sleep(2)
                
                # Find tweet links
                tweet_elements = self.driver.find_elements(By.CSS_SELECTOR, 'a[href*="/status/"]')
                
                for element in tweet_elements[:self.config.max_results]:
                    tweet_url = urljoin("https://twitter.com", element.get_attribute('href'))
                    if tweet_url not in result.detected_urls:
                        result.detected_urls.append(tweet_url)
                
                await asyncio.sleep(self.config.rate_limit_delay)
                
        except Exception as e:
            result.error_message = str(e)
            logger.error(f"Twitter monitoring error: {e}")
        
        result.scan_duration = (datetime.utcnow() - start_time).total_seconds()
        return result


class GenericWebMonitor(PlatformMonitor):
    """Generic web monitoring for any website"""
    
    async def scan_content(self) -> MonitoringResult:
        """Scan generic websites for protected content"""
        start_time = datetime.utcnow()
        result = MonitoringResult(platform=MonitoringPlatform.GENERIC_WEB)
        
        try:
            for search_term in self.config.search_terms:
                # Use Google search as entry point
                search_url = f"https://www.google.com/search?q=\"{search_term}\""
                
                async with self.session.get(search_url) as response:
                    if response.status == 200:
                        html = await response.text()
                        soup = BeautifulSoup(html, 'html.parser')
                        
                        # Find search result links
                        for link in soup.find_all('a', href=True):
                            href = link['href']
                            if href.startswith('/url?q='):
                                # Extract actual URL from Google redirect
                                actual_url = href.split('/url?q=')[1].split('&')[0]
                                if self._is_valid_url(actual_url):
                                    result.detected_urls.append(actual_url)
                
                await asyncio.sleep(self.config.rate_limit_delay)
                
        except Exception as e:
            result.error_message = str(e)
            logger.error(f"Generic web monitoring error: {e}")
        
        result.scan_duration = (datetime.utcnow() - start_time).total_seconds()
        return result
    
    def _is_valid_url(self, url: str) -> bool:
        """Check if URL is valid and not from excluded domains"""
        try:
            parsed = urlparse(url)
            excluded_domains = ['google.com', 'youtube.com', 'facebook.com', 'instagram.com']
            return (parsed.scheme in ['http', 'https'] and 
                    not any(domain in parsed.netloc for domain in excluded_domains))
        except:
            return False


class ContentMonitor:
    """Main content monitoring coordinator"""
    
    def __init__(self):
        self.fingerprint_engine = FingerprintEngine()
        self.active_monitors: Dict[str, PlatformMonitor] = {}
        self.monitoring_tasks: Dict[str, asyncio.Task] = {}
        self.results_cache: Dict[str, List[MonitoringResult]] = {}
        
    def create_monitor(self, config: MonitoringConfig) -> str:
        """Create a new content monitor"""
        monitor_id = hashlib.md5(
            f"{config.platform.value}_{config.search_terms}_{datetime.utcnow().isoformat()}".encode()
        ).hexdigest()[:16]
        
        # Select appropriate monitor class
        monitor_classes = {
            MonitoringPlatform.YOUTUBE: YouTubeMonitor,
            MonitoringPlatform.INSTAGRAM: InstagramMonitor,
            MonitoringPlatform.TIKTOK: TikTokMonitor,
            MonitoringPlatform.TWITTER: TwitterMonitor,
            MonitoringPlatform.GENERIC_WEB: GenericWebMonitor
        }
        
        monitor_class = monitor_classes.get(config.platform, GenericWebMonitor)
        monitor = monitor_class(config)
        
        self.active_monitors[monitor_id] = monitor
        self.results_cache[monitor_id] = []
        
        logger.info(f"Created monitor {monitor_id} for {config.platform.value}")
        return monitor_id
    
    async def start_monitoring(self, monitor_id: str) -> bool:
        """Start monitoring task"""
        try:
            if monitor_id not in self.active_monitors:
                return False
            
            monitor = self.active_monitors[monitor_id]
            await monitor.initialize()
            
            # Create monitoring task
            task = asyncio.create_task(self._monitor_loop(monitor_id))
            self.monitoring_tasks[monitor_id] = task
            
            logger.info(f"Started monitoring task {monitor_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error starting monitoring {monitor_id}: {e}")
            return False
    
    async def stop_monitoring(self, monitor_id: str) -> bool:
        """Stop monitoring task"""
        try:
            # Cancel task
            if monitor_id in self.monitoring_tasks:
                task = self.monitoring_tasks[monitor_id]
                task.cancel()
                del self.monitoring_tasks[monitor_id]
            
            # Cleanup monitor
            if monitor_id in self.active_monitors:
                monitor = self.active_monitors[monitor_id]
                await monitor.cleanup()
                del self.active_monitors[monitor_id]
            
            logger.info(f"Stopped monitoring task {monitor_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error stopping monitoring {monitor_id}: {e}")
            return False
    
    async def _monitor_loop(self, monitor_id: str):
        """Main monitoring loop for a monitor"""
        monitor = self.active_monitors[monitor_id]
        
        while True:
            try:
                # Perform content scan
                result = await monitor.scan_content()
                
                # Store result
                self.results_cache[monitor_id].append(result)
                
                # Keep only last 100 results
                if len(self.results_cache[monitor_id]) > 100:
                    self.results_cache[monitor_id] = self.results_cache[monitor_id][-100:]
                
                logger.info(f"Monitor {monitor_id} found {len(result.detected_urls)} URLs")
                
                # Wait for next interval
                interval_seconds = monitor.config.interval_minutes * 60
                await asyncio.sleep(interval_seconds)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in monitoring loop {monitor_id}: {e}")
                await asyncio.sleep(60)  # Wait 1 minute before retrying
    
    def get_monitor_results(self, monitor_id: str, limit: int = 10) -> List[MonitoringResult]:
        """Get recent monitoring results"""
        if monitor_id not in self.results_cache:
            return []
        
        return self.results_cache[monitor_id][-limit:]
    
    def get_all_detected_urls(self, hours: int = 24) -> List[str]:
        """Get all URLs detected in the last N hours"""
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)
        all_urls = []
        
        for results in self.results_cache.values():
            for result in results:
                if result.timestamp >= cutoff_time:
                    all_urls.extend(result.detected_urls)
        
        return list(set(all_urls))  # Remove duplicates
    
    def get_monitoring_statistics(self) -> Dict[str, Any]:
        """Get monitoring system statistics"""
        return {
            'active_monitors': len(self.active_monitors),
            'running_tasks': len(self.monitoring_tasks),
            'total_results': sum(len(results) for results in self.results_cache.values()),
            'platforms': list(set(monitor.config.platform.value for monitor in self.active_monitors.values())),
            'last_scan_times': {
                monitor_id: results[-1].timestamp.isoformat() if results else None
                for monitor_id, results in self.results_cache.items()
            }
        }
