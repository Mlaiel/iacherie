"""Stealth Scraper - IA-Influencer-Agent
=====================================

Advanced anti-detection scraping with stealth techniques.
Designed to bypass bot detection and maintain anonymity.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: All rights reserved. Unauthorized use, reproduction, or distribution prohibited.

⚠️ CRITICAL LEGAL WARNING ⚠️
UNAUTHORIZED USE, COPYING, OR DISTRIBUTION IS STRICTLY PROHIBITED AND WILL RESULT IN IMMEDIATE LEGAL ACTION.
This technology is EXCLUSIVE property of Fahed Mlaiel. Contact: mlaiel@live.de for licensing.
"""
import asyncio
import random
import time
import json
import logging
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from datetime import datetime, timedelta
import aiohttp
from fake_useragent import UserAgent
import undetected_chromedriver as uc
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, WebDriverException
import requests
from urllib.parse import urlparse
import hashlib

@dataclass
class StealthConfig:
    """Stealth scraping configuration."""    use_proxies: bool = True
    rotate_user_agents: bool = True
    randomize_headers: bool = True
    add_noise_delay: bool = True
    min_delay: float = 1.0
    max_delay: float = 5.0
    use_selenium: bool = False
    headless: bool = True
    viewport_randomization: bool = True
    disable_images: bool = True
    disable_css: bool = False
    max_retries: int = 3
    session_rotation_interval: int = 50

@dataclass
class ProxyConfig:
    """Proxy configuration."""    host: str
    port: int
    username: Optional[str] = None
    password: Optional[str] = None
    protocol: str = 'http'  # http, https, socks4, socks5

class StealthScraper:
    """    Advanced stealth web scraper with anti-detection capabilities.
    
    Features:
    - Proxy rotation
    - User agent rotation
    - Header randomization
    - Behavioral simulation
    - Browser fingerprint randomization
    - CAPTCHA detection
    - Session management
    - Request timing randomization
    """    
    def __init__(self, config: Optional[StealthConfig] = None):
        self.config = config or StealthConfig()
        self.logger = logging.getLogger(__name__)
        self.user_agent = UserAgent()
        self.session: Optional[aiohttp.ClientSession] = None
        self.driver: Optional[webdriver.Chrome] = None
        self.proxy_pool: List[ProxyConfig] = []
        self.current_proxy_index = 0
        self.request_count = 0
        self.session_start_time = datetime.now()
        self.fingerprint_cache = {}
        
    async def __aenter__(self):
        """Async context manager entry."""        await self._initialize_session()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""        await self._cleanup()
        
    async def _initialize_session(self):
        """Initialize stealth session."""        if self.config.use_proxies:
            await self._load_proxy_pool()
            
        connector = aiohttp.TCPConnector(
            limit=10,
            limit_per_host=2,
            ttl_dns_cache=300,
            use_dns_cache=True,
            enable_cleanup_closed=True
        )
        
        timeout = aiohttp.ClientTimeout(total=30)
        
        self.session = aiohttp.ClientSession(
            connector=connector,
            timeout=timeout
        )
        
    async def _cleanup(self):
        """Cleanup resources."""        if self.session:
            await self.session.close()
            
        if self.driver:
            self.driver.quit()
            
    async def _load_proxy_pool(self):
        """Load and validate proxy pool."""        # In production, load from secure proxy service
        # For now, using placeholder
        sample_proxies = [
            ProxyConfig('proxy1.example.com', 8080),
            ProxyConfig('proxy2.example.com', 8080),
            ProxyConfig('proxy3.example.com', 8080)
        ]
        
        # Validate proxies
        valid_proxies = []
        for proxy in sample_proxies:
            if await self._validate_proxy(proxy):
                valid_proxies.append(proxy)
                
        self.proxy_pool = valid_proxies
        self.logger.info(f"Loaded {len(self.proxy_pool)} valid proxies")
        
    async def _validate_proxy(self, proxy: ProxyConfig) -> bool:
        """Validate proxy connectivity."""        try:
            proxy_url = f"{proxy.protocol}://"
            if proxy.username and proxy.password:
                proxy_url += f"{proxy.username}:{proxy.password}@"
            proxy_url += f"{proxy.host}:{proxy.port}"
            
            connector = aiohttp.TCPConnector()
            timeout = aiohttp.ClientTimeout(total=10)
            
            async with aiohttp.ClientSession(
                connector=connector,
                timeout=timeout
            ) as session:
                async with session.get(
                    'http://httpbin.org/ip',
                    proxy=proxy_url
                ) as response:
                    return response.status == 200
                    
        except Exception as e:
            self.logger.debug(f"Proxy validation failed for {proxy.host}:{proxy.port}: {e}")
            return False
            
    def _get_random_proxy(self) -> Optional[ProxyConfig]:
        """Get random proxy from pool."""        if not self.proxy_pool:
            return None
            
        # Rotate through proxies
        proxy = self.proxy_pool[self.current_proxy_index]
        self.current_proxy_index = (self.current_proxy_index + 1) % len(self.proxy_pool)
        return proxy
        
    def _generate_stealth_headers(self) -> Dict[str, str]:
        """Generate randomized stealth headers."""        headers = {
            'Accept': random.choice([
                'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8'
            ]),
            'Accept-Language': random.choice([
                'en-US,en;q=0.9',
                'en-US,en;q=0.8',
                'en-GB,en;q=0.9',
                'en-US,en;q=0.5',
                'en-US,en;q=0.9,es;q=0.8'
            ]),
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': random.choice(['none', 'same-origin', 'cross-site']),
            'Cache-Control': random.choice(['no-cache', 'max-age=0']),
            'DNT': str(random.choice([0, 1]))
        }
        
        if self.config.rotate_user_agents:
            headers['User-Agent'] = self._get_random_user_agent()
            
        # Add random additional headers
        if random.random() > 0.5:
            headers['Accept-CH'] = 'Sec-CH-UA-Platform-Version, Sec-CH-UA-Model'
            
        if random.random() > 0.7:
            headers['Sec-CH-UA'] = '"Chromium";v="116", "Not)A;Brand";v="24", "Google Chrome";v="116"'
            headers['Sec-CH-UA-Mobile'] = '?0'
            headers['Sec-CH-UA-Platform'] = '"Windows"'
            
        return headers
        
    def _get_random_user_agent(self) -> str:
        """Get randomized user agent."""        try:
            return self.user_agent.random
        except:
            # Fallback user agents
            fallback_agents = [
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36',
                'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36',
                'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36',
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:117.0) Gecko/20100101 Firefox/117.0',
                'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:117.0) Gecko/20100101 Firefox/117.0'
            ]
            return random.choice(fallback_agents)
            
    async def _add_behavioral_delay(self):
        """Add human-like behavioral delay."""        if self.config.add_noise_delay:
            delay = random.uniform(self.config.min_delay, self.config.max_delay)
            await asyncio.sleep(delay)
            
    async def _check_session_rotation(self):
        """Check if session should be rotated."""        self.request_count += 1
        
        if (self.request_count >= self.config.session_rotation_interval or
            datetime.now() - self.session_start_time > timedelta(hours=1)):
            
            await self._rotate_session()
            
    async def _rotate_session(self):
        """Rotate session to avoid detection."""        self.logger.info("Rotating session for stealth")
        
        if self.session:
            await self.session.close()
            
        await asyncio.sleep(random.uniform(2, 5))  # Cool-down period
        await self._initialize_session()
        
        self.request_count = 0
        self.session_start_time = datetime.now()
        
    async def stealth_get(self, url: str, **kwargs) -> aiohttp.ClientResponse:
        """Perform stealth GET request."""        await self._check_session_rotation()
        await self._add_behavioral_delay()
        
        headers = self._generate_stealth_headers()
        if 'headers' in kwargs:
            headers.update(kwargs['headers'])
        kwargs['headers'] = headers
        
        # Add proxy if available
        if self.config.use_proxies and self.proxy_pool:
            proxy = self._get_random_proxy()
            if proxy:
                proxy_url = f"{proxy.protocol}://"
                if proxy.username and proxy.password:
                    proxy_url += f"{proxy.username}:{proxy.password}@"
                proxy_url += f"{proxy.host}:{proxy.port}"
                kwargs['proxy'] = proxy_url
                
        return await self.session.get(url, **kwargs)
        
    def _create_stealth_driver(self) -> webdriver.Chrome:
        """Create stealth Selenium driver."""        options = uc.ChromeOptions()
        
        if self.config.headless:
            options.add_argument('--headless')
            
        # Anti-detection options
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        
        # Performance options
        if self.config.disable_images:
            prefs = {"profile.managed_default_content_settings.images": 2}
            options.add_experimental_option("prefs", prefs)
            
        if self.config.disable_css:
            options.add_argument('--disable-extensions')
            
        # Random viewport
        if self.config.viewport_randomization:
            width = random.randint(1200, 1920)
            height = random.randint(800, 1080)
            options.add_argument(f'--window-size={width},{height}')
            
        # Random user agent
        if self.config.rotate_user_agents:
            options.add_argument(f'--user-agent={self._get_random_user_agent()}')
            
        # Proxy support
        if self.config.use_proxies and self.proxy_pool:
            proxy = self._get_random_proxy()
            if proxy:
                proxy_arg = f'--proxy-server={proxy.protocol}://{proxy.host}:{proxy.port}'
                options.add_argument(proxy_arg)
                
        driver = uc.Chrome(options=options)
        
        # Execute stealth script
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
        return driver
        
    async def stealth_selenium_get(self, url: str, wait_for_element: Optional[str] = None,
                                 wait_timeout: int = 10) -> str:
        """Get page content using stealth Selenium."""        if not self.driver:
            self.driver = self._create_stealth_driver()
            
        try:
            # Add random delay before navigation
            await asyncio.sleep(random.uniform(1, 3))
            
            self.driver.get(url)
            
            # Wait for specific element if provided
            if wait_for_element:
                wait = WebDriverWait(self.driver, wait_timeout)
                wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, wait_for_element)))
                
            # Simulate human behavior
            await self._simulate_human_behavior()
            
            return self.driver.page_source
            
        except TimeoutException:
            self.logger.warning(f"Timeout waiting for element: {wait_for_element}")
            return self.driver.page_source
        except WebDriverException as e:
            self.logger.error(f"WebDriver error: {e}")
            # Recreate driver on error
            if self.driver:
                self.driver.quit()
            self.driver = self._create_stealth_driver()
            raise
            
    async def _simulate_human_behavior(self):
        """Simulate human browsing behavior."""        if not self.driver:
            return
            
        # Random scroll
        if random.random() > 0.7:
            scroll_height = self.driver.execute_script("return document.body.scrollHeight")
            random_scroll = random.randint(0, scroll_height // 2)
            self.driver.execute_script(f"window.scrollTo(0, {random_scroll})")
            await asyncio.sleep(random.uniform(0.5, 2))
            
        # Random mouse movement simulation
        if random.random() > 0.8:
            self.driver.execute_script("""                var event = new MouseEvent('mousemove', {
                    'view': window,
                    'bubbles': true,
                    'cancelable': true,
                    'clientX': Math.random() * window.innerWidth,
                    'clientY': Math.random() * window.innerHeight
                });
                document.dispatchEvent(event);
            """)
            
    def detect_captcha(self, html: str) -> bool:
        """Detect CAPTCHA presence in HTML."""        captcha_indicators = [
            'captcha', 'recaptcha', 'hcaptcha', 'cloudflare',
            'verify you are human', 'robot', 'automation',
            'security check', 'blocked', 'access denied'
        ]
        
        html_lower = html.lower()
        return any(indicator in html_lower for indicator in captcha_indicators)
        
    def detect_bot_detection(self, html: str, status_code: int) -> bool:
        """Detect bot detection mechanisms."""        if status_code in [403, 429, 503]:
            return True
            
        bot_detection_indicators = [
            'access denied', 'blocked', 'bot detected',
            'unusual traffic', 'automated requests',
            'rate limit', 'too many requests'
        ]
        
        html_lower = html.lower()
        return any(indicator in html_lower for indicator in bot_detection_indicators)
        
    async def handle_challenge(self, url: str, html: str) -> Optional[str]:
        """Handle anti-bot challenges."""        self.logger.warning(f"Challenge detected for {url}")
        
        if self.detect_captcha(html):
            self.logger.warning("CAPTCHA detected - manual intervention required")
            return None
            
        # Try different strategies
        strategies = [
            self._retry_with_new_session,
            self._retry_with_selenium,
            self._retry_with_different_proxy
        ]
        
        for strategy in strategies:
            try:
                result = await strategy(url)
                if result and not self.detect_bot_detection(result, 200):
                    return result
            except Exception as e:
                self.logger.debug(f"Strategy failed: {e}")
                continue
                
        return None
        
    async def _retry_with_new_session(self, url: str) -> Optional[str]:
        """Retry with new session."""        await self._rotate_session()
        await asyncio.sleep(random.uniform(5, 10))
        
        async with await self.stealth_get(url) as response:
            return await response.text()
            
    async def _retry_with_selenium(self, url: str) -> Optional[str]:
        """Retry with Selenium."""        return await self.stealth_selenium_get(url)
        
    async def _retry_with_different_proxy(self, url: str) -> Optional[str]:
        """Retry with different proxy."""        if self.proxy_pool and len(self.proxy_pool) > 1:
            # Force proxy rotation
            self.current_proxy_index = (self.current_proxy_index + 1) % len(self.proxy_pool)
            
            async with await self.stealth_get(url) as response:
                return await response.text()
                
        return None
        
    def generate_session_fingerprint(self) -> str:
        """Generate unique session fingerprint."""        components = [
            self._get_random_user_agent(),
            str(random.randint(1200, 1920)),  # screen width
            str(random.randint(800, 1080)),   # screen height
            str(random.randint(24, 32)),      # color depth
            random.choice(['UTC+0', 'UTC-5', 'UTC-8', 'UTC+1']),  # timezone
            random.choice(['en-US', 'en-GB', 'en-CA']),  # language
        ]
        
        fingerprint_string = '|'.join(components)
        return hashlib.md5(fingerprint_string.encode()).hexdigest()
        
    async def stealth_scrape(self, url: str, use_selenium: Optional[bool] = None) -> Optional[str]:
        """Main stealth scraping method."""        use_sel = use_selenium if use_selenium is not None else self.config.use_selenium
        
        try:
            if use_sel:
                html = await self.stealth_selenium_get(url)
            else:
                async with await self.stealth_get(url) as response:
                    html = await response.text()
                    
                    if self.detect_bot_detection(html, response.status):
                        html = await self.handle_challenge(url, html)
                        
            return html
            
        except Exception as e:
            self.logger.error(f"Stealth scraping failed for {url}: {e}")
            return None
            
    def get_stealth_stats(self) -> Dict[str, Any]:
        """Get stealth scraping statistics."""        return {
            'request_count': self.request_count,
            'session_age': (datetime.now() - self.session_start_time).total_seconds(),
            'proxy_pool_size': len(self.proxy_pool),
            'current_proxy_index': self.current_proxy_index,
            'selenium_active': self.driver is not None,
            'session_fingerprint': self.generate_session_fingerprint()
        }
