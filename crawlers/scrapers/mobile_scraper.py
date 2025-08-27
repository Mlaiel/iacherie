"""
Mobile Scraper - IA-Influencer-Agent
====================================

Mobile-optimized web scraping with responsive content extraction.
Handles mobile user agents, viewport emulation, and app-specific content.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: All rights reserved. Unauthorized use, reproduction, or distribution prohibited.

⚠️ CRITICAL LEGAL WARNING ⚠️
UNAUTHORIZED USE, COPYING, OR DISTRIBUTION IS STRICTLY PROHIBITED AND WILL RESULT IN IMMEDIATE LEGAL ACTION.
This technology is EXCLUSIVE property of Fahed Mlaiel. Contact: mlaiel@live.de for licensing.
"""

import asyncio
import aiohttp
import logging
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass
from datetime import datetime
import random
import json
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup

@dataclass
class MobileDevice:
    """Mobile device configuration."""
    name: str
    user_agent: str
    viewport: Dict[str, int]
    screen: Dict[str, int]
    device_pixel_ratio: float = 1.0
    touch_enabled: bool = True

@dataclass
class MobileContent:
    """Mobile-optimized content structure."""
    url: str
    title: Optional[str] = None
    content: Optional[str] = None
    description: Optional[str] = None
    images: List[str] = None
    videos: List[str] = None
    amp_url: Optional[str] = None
    mobile_app_url: Optional[str] = None
    viewport_meta: Optional[str] = None
    responsive_design: bool = False
    mobile_optimized: bool = False
    app_banner: Optional[Dict[str, str]] = None
    touch_icons: List[str] = None
    scraped_at: datetime = None

    def __post_init__(self):
        if self.images is None:
            self.images = []
        if self.videos is None:
            self.videos = []
        if self.touch_icons is None:
            self.touch_icons = []
        if self.scraped_at is None:
            self.scraped_at = datetime.now()

class MobileScraper:
    """
    Mobile-optimized web scraper.
    
    Features:
    - Mobile user agent simulation
    - Responsive design detection
    - AMP content extraction
    - Mobile app detection
    - Touch-optimized interface analysis
    - Viewport emulation
    - Mobile-specific metadata
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.session: Optional[aiohttp.ClientSession] = None
        
        # Mobile device configurations
        self.devices = {
            'iphone_13': MobileDevice(
                name='iPhone 13',
                user_agent='Mozilla/5.0 (iPhone; CPU iPhone OS 15_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.0 Mobile/15E148 Safari/604.1',
                viewport={'width': 390, 'height': 844},
                screen={'width': 390, 'height': 844},
                device_pixel_ratio=3.0
            ),
            'samsung_galaxy': MobileDevice(
                name='Samsung Galaxy S21',
                user_agent='Mozilla/5.0 (Linux; Android 11; SM-G991B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.120 Mobile Safari/537.36',
                viewport={'width': 360, 'height': 800},
                screen={'width': 360, 'height': 800},
                device_pixel_ratio=3.0
            ),
            'ipad': MobileDevice(
                name='iPad',
                user_agent='Mozilla/5.0 (iPad; CPU OS 15_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.0 Mobile/15E148 Safari/604.1',
                viewport={'width': 768, 'height': 1024},
                screen={'width': 768, 'height': 1024},
                device_pixel_ratio=2.0
            ),
            'pixel_6': MobileDevice(
                name='Google Pixel 6',
                user_agent='Mozilla/5.0 (Linux; Android 12; Pixel 6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.81 Mobile Safari/537.36',
                viewport={'width': 393, 'height': 851},
                screen={'width': 393, 'height': 851},
                device_pixel_ratio=2.75
            )
        }
        
        self.current_device = self.devices['iphone_13']
        
    async def __aenter__(self):
        """Async context manager entry."""
        await self._initialize_session()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if self.session:
            await self.session.close()
            
    async def _initialize_session(self):
        """Initialize HTTP session with mobile headers."""
        headers = {
            'User-Agent': self.current_device.user_agent,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1'
        }
        
        connector = aiohttp.TCPConnector(limit=30)
        timeout = aiohttp.ClientTimeout(total=30)
        
        self.session = aiohttp.ClientSession(
            headers=headers,
            connector=connector,
            timeout=timeout
        )
        
    def set_device(self, device_name: str):
        """Set mobile device for emulation."""
        if device_name in self.devices:
            self.current_device = self.devices[device_name]
            self.logger.info(f"Set device to: {self.current_device.name}")
        else:
            self.logger.warning(f"Unknown device: {device_name}")
            
    async def scrape_mobile_content(self, url: str) -> MobileContent:
        """Scrape content optimized for mobile."""
        try:
            async with self.session.get(url) as response:
                html = await response.text()
                soup = BeautifulSoup(html, 'html.parser')
                
                content = MobileContent(url=url)
                
                # Extract basic content
                content.title = self._extract_title(soup)
                content.description = self._extract_description(soup)
                content.content = self._extract_main_content(soup)
                
                # Extract mobile-specific elements
                content.viewport_meta = self._extract_viewport(soup)
                content.amp_url = self._extract_amp_url(soup)
                content.mobile_app_url = self._extract_app_url(soup)
                content.app_banner = self._extract_app_banner(soup)
                content.touch_icons = self._extract_touch_icons(soup)
                
                # Extract media
                content.images = self._extract_images(soup, url)
                content.videos = self._extract_videos(soup, url)
                
                # Analyze mobile optimization
                content.responsive_design = self._detect_responsive_design(soup)
                content.mobile_optimized = self._detect_mobile_optimization(soup)
                
                return content
                
        except Exception as e:
            self.logger.error(f"Failed to scrape mobile content from {url}: {e}")
            return MobileContent(url=url)
            
    def _extract_title(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract page title."""
        # Try mobile-specific title first
        mobile_title = soup.find('meta', property='og:title')
        if mobile_title and mobile_title.get('content'):
            return mobile_title['content']
            
        # Fallback to regular title
        title_tag = soup.find('title')
        return title_tag.get_text().strip() if title_tag else None
        
    def _extract_description(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract page description."""
        # Try various meta description tags
        selectors = [
            'meta[name="description"]',
            'meta[property="og:description"]',
            'meta[name="twitter:description"]'
        ]
        
        for selector in selectors:
            meta = soup.select_one(selector)
            if meta and meta.get('content'):
                return meta['content']
                
        return None
        
    def _extract_main_content(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract main content from mobile-optimized selectors."""
        # Mobile-first content selectors
        selectors = [
            'main',
            'article',
            '[role="main"]',
            '.content',
            '.main-content',
            '.post-content',
            '.entry-content',
            '#content',
            '#main'
        ]
        
        for selector in selectors:
            element = soup.select_one(selector)
            if element:
                # Clean mobile-specific elements
                for unwanted in element.select('.advertisement, .ads, .social-share, .related-posts'):
                    unwanted.decompose()
                    
                return element.get_text(strip=True)
                
        return None
        
    def _extract_viewport(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract viewport meta tag."""
        viewport = soup.find('meta', attrs={'name': 'viewport'})
        return viewport.get('content') if viewport else None
        
    def _extract_amp_url(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract AMP (Accelerated Mobile Pages) URL."""
        amp_link = soup.find('link', rel='amphtml')
        return amp_link.get('href') if amp_link else None
        
    def _extract_app_url(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract mobile app URL."""
        # iOS app store
        ios_app = soup.find('meta', attrs={'name': 'apple-itunes-app'})
        if ios_app and ios_app.get('content'):
            return ios_app['content']
            
        # Android app
        android_app = soup.find('meta', attrs={'name': 'google-play-app'})
        if android_app and android_app.get('content'):
            return android_app['content']
            
        return None
        
    def _extract_app_banner(self, soup: BeautifulSoup) -> Optional[Dict[str, str]]:
        """Extract app banner information."""
        banner = {}
        
        # Smart app banner
        smart_banner = soup.find('meta', attrs={'name': 'apple-itunes-app'})
        if smart_banner:
            banner['ios'] = smart_banner.get('content', '')
            
        # Google Play banner
        play_banner = soup.find('meta', attrs={'name': 'google-play-app'})
        if play_banner:
            banner['android'] = play_banner.get('content', '')
            
        return banner if banner else None
        
    def _extract_touch_icons(self, soup: BeautifulSoup) -> List[str]:
        """Extract touch icons for mobile devices."""
        icons = []
        
        # Apple touch icons
        touch_icons = soup.find_all('link', rel=lambda x: x and 'apple-touch-icon' in x)
        for icon in touch_icons:
            if icon.get('href'):
                icons.append(icon['href'])
                
        # Android icons
        android_icons = soup.find_all('link', rel='icon', sizes=True)
        for icon in android_icons:
            if icon.get('href'):
                icons.append(icon['href'])
                
        return icons
        
    def _extract_images(self, soup: BeautifulSoup, base_url: str) -> List[str]:
        """Extract images with mobile optimization."""
        images = []
        
        # Find all images
        img_tags = soup.find_all('img')
        for img in img_tags:
            src = img.get('src') or img.get('data-src') or img.get('data-lazy-src')
            if src:
                # Convert relative URLs to absolute
                absolute_url = urljoin(base_url, src)
                images.append(absolute_url)
                
        # Remove duplicates
        return list(set(images))
        
    def _extract_videos(self, soup: BeautifulSoup, base_url: str) -> List[str]:
        """Extract videos with mobile support."""
        videos = []
        
        # Video tags
        video_tags = soup.find_all('video')
        for video in video_tags:
            src = video.get('src')
            if src:
                absolute_url = urljoin(base_url, src)
                videos.append(absolute_url)
                
            # Source tags within video
            sources = video.find_all('source')
            for source in sources:
                src = source.get('src')
                if src:
                    absolute_url = urljoin(base_url, src)
                    videos.append(absolute_url)
                    
        return list(set(videos))
        
    def _detect_responsive_design(self, soup: BeautifulSoup) -> bool:
        """Detect if the page uses responsive design."""
        # Check viewport meta tag
        viewport = soup.find('meta', attrs={'name': 'viewport'})
        if viewport and 'width=device-width' in viewport.get('content', ''):
            return True
            
        # Check for CSS media queries
        styles = soup.find_all('style')
        for style in styles:
            if '@media' in style.get_text():
                return True
                
        # Check for responsive CSS classes
        responsive_classes = [
            'responsive', 'mobile', 'tablet', 'desktop',
            'col-', 'grid', 'flex', 'container'
        ]
        
        for element in soup.find_all(class_=True):
            classes = ' '.join(element.get('class', []))
            if any(cls in classes for cls in responsive_classes):
                return True
                
        return False
        
    def _detect_mobile_optimization(self, soup: BeautifulSoup) -> bool:
        """Detect mobile-specific optimizations."""
        mobile_indicators = [
            # Touch-friendly elements
            'touch', 'tap', 'swipe',
            # Mobile frameworks
            'jquery.mobile', 'framework7', 'ionic',
            # Mobile meta tags
            'apple-mobile-web-app',
            # Mobile-specific CSS
            'mobile-', '-mobile'
        ]
        
        page_text = str(soup).lower()
        return any(indicator in page_text for indicator in mobile_indicators)
        
    async def scrape_amp_content(self, amp_url: str) -> Optional[MobileContent]:
        """Scrape AMP (Accelerated Mobile Pages) content."""
        try:
            async with self.session.get(amp_url) as response:
                html = await response.text()
                soup = BeautifulSoup(html, 'html.parser')
                
                content = MobileContent(url=amp_url)
                content.title = self._extract_title(soup)
                content.description = self._extract_description(soup)
                
                # AMP-specific content extraction
                amp_content = soup.find('amp-story') or soup.find('[amp-custom]')
                if amp_content:
                    content.content = amp_content.get_text(strip=True)
                    
                content.mobile_optimized = True
                return content
                
        except Exception as e:
            self.logger.error(f"Failed to scrape AMP content from {amp_url}: {e}")
            return None
            
    def get_device_capabilities(self) -> Dict[str, Any]:
        """Get current device capabilities."""
        return {
            'name': self.current_device.name,
            'user_agent': self.current_device.user_agent,
            'viewport': self.current_device.viewport,
            'screen': self.current_device.screen,
            'device_pixel_ratio': self.current_device.device_pixel_ratio,
            'touch_enabled': self.current_device.touch_enabled
        }
