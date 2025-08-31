"""User Agent Rotator Module
=========================

Professional user agent rotation for web crawling with realistic browser simulation.
Implements intelligent user agent selection, device fingerprinting, and browser behavior.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: All rights reserved. Unauthorized use, reproduction, or distribution prohibited.

WARNING: This code is protected by copyright law. Any unauthorized copying, 
distribution, or modification is strictly prohibited and will result in 
legal action. Contact mlaiel@live.de for licensing.
"""
import random
import logging
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime, timedelta
import json
import asyncio

logger = logging.getLogger(__name__)

@dataclass
class UserAgentInfo:
    """User agent information structure."""    string: str
    browser: str
    browser_version: str
    os: str
    os_version: str
    device_type: str  # desktop, mobile, tablet
    is_mobile: bool
    popularity_score: float
    last_updated: datetime

@dataclass
class BrowserFingerprint:
    """Browser fingerprint for realistic simulation."""    user_agent: str
    accept_language: str
    accept_encoding: str
    accept: str
    screen_resolution: Tuple[int, int]
    viewport_size: Tuple[int, int]
    timezone: str
    platform: str
    webgl_vendor: str
    webgl_renderer: str
    plugins: List[str]
    fonts: List[str]

class UserAgentRotator:
    """    Professional user agent rotation system.
    
    Features:
    - Realistic browser simulation
    - Device-specific user agents
    - Geographic targeting
    - Browser fingerprint generation
    - Usage tracking and rotation
    - Mobile/desktop optimization
    - Anti-detection measures
    - Performance monitoring
    """    
    def __init__(self):
        """Initialize user agent rotator."""        self.user_agents: List[UserAgentInfo] = []
        self.usage_history: Dict[str, int] = {}
        self.current_fingerprint: Optional[BrowserFingerprint] = None
        self.rotation_strategy = 'weighted_random'
        self.max_usage_per_agent = 100
        self.mobile_ratio = 0.3  # 30% mobile traffic
        
        # Load user agent database
        self._load_user_agents()
        
        # Popular browser configurations
        self.browser_configs = {
            'chrome': {
                'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
                'accept_encoding': 'gzip, deflate, br',
                'accept_language': 'en-US,en;q=0.9',
                'sec_fetch_dest': 'document',
                'sec_fetch_mode': 'navigate',
                'sec_fetch_site': 'none',
                'sec_fetch_user': '?1',
                'upgrade_insecure_requests': '1'
            },
            'firefox': {
                'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'accept_encoding': 'gzip, deflate, br',
                'accept_language': 'en-US,en;q=0.5',
                'upgrade_insecure_requests': '1'
            },
            'safari': {
                'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'accept_encoding': 'gzip, deflate, br',
                'accept_language': 'en-US,en;q=0.9',
                'upgrade_insecure_requests': '1'
            }
        }
    
    def _load_user_agents(self) -> None:
        """Load comprehensive user agent database."""        # Chrome user agents (most popular)
        chrome_agents = [
            # Windows Chrome
            UserAgentInfo(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
                "Chrome", "121.0.0.0", "Windows", "10", "desktop", False, 0.4,
                datetime.now()
            ),
            UserAgentInfo(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                "Chrome", "120.0.0.0", "Windows", "10", "desktop", False, 0.35,
                datetime.now()
            ),
            # macOS Chrome
            UserAgentInfo(
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
                "Chrome", "121.0.0.0", "macOS", "10.15.7", "desktop", False, 0.15,
                datetime.now()
            ),
            # Linux Chrome
            UserAgentInfo(
                "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
                "Chrome", "121.0.0.0", "Linux", "", "desktop", False, 0.05,
                datetime.now()
            ),
        ]
        
        # Firefox user agents
        firefox_agents = [
            UserAgentInfo(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:122.0) Gecko/20100101 Firefox/122.0",
                "Firefox", "122.0", "Windows", "10", "desktop", False, 0.08,
                datetime.now()
            ),
            UserAgentInfo(
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:122.0) Gecko/20100101 Firefox/122.0",
                "Firefox", "122.0", "macOS", "10.15", "desktop", False, 0.03,
                datetime.now()
            ),
        ]
        
        # Safari user agents
        safari_agents = [
            UserAgentInfo(
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2.1 Safari/605.1.15",
                "Safari", "17.2.1", "macOS", "10.15.7", "desktop", False, 0.06,
                datetime.now()
            ),
        ]
        
        # Mobile user agents
        mobile_agents = [
            # iOS Safari
            UserAgentInfo(
                "Mozilla/5.0 (iPhone; CPU iPhone OS 17_2_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Mobile/15E148 Safari/604.1",
                "Safari", "17.2", "iOS", "17.2.1", "mobile", True, 0.15,
                datetime.now()
            ),
            # Android Chrome
            UserAgentInfo(
                "Mozilla/5.0 (Linux; Android 14; SM-G998B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Mobile Safari/537.36",
                "Chrome", "121.0.0.0", "Android", "14", "mobile", True, 0.12,
                datetime.now()
            ),
            # iPad
            UserAgentInfo(
                "Mozilla/5.0 (iPad; CPU OS 17_2_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Mobile/15E148 Safari/604.1",
                "Safari", "17.2", "iPadOS", "17.2.1", "tablet", True, 0.04,
                datetime.now()
            ),
        ]
        
        # Combine all user agents
        self.user_agents = chrome_agents + firefox_agents + safari_agents + mobile_agents
        
        logger.info(f"Loaded {len(self.user_agents)} user agents")
    
    def get_user_agent(
        self,
        device_type: Optional[str] = None,
        browser: Optional[str] = None,
        mobile: Optional[bool] = None
    ) -> UserAgentInfo:
        """        Get user agent based on specified criteria.
        
        Args:
            device_type: desktop, mobile, tablet
            browser: chrome, firefox, safari
            mobile: Force mobile or desktop
            
        Returns:
            UserAgentInfo object
        """        # Filter user agents based on criteria
        candidates = self._filter_user_agents(device_type, browser, mobile)
        
        if not candidates:
            # Fallback to any available user agent
            candidates = self.user_agents
        
        # Select based on rotation strategy
        if self.rotation_strategy == 'weighted_random':
            return self._select_weighted_random(candidates)
        elif self.rotation_strategy == 'least_used':
            return self._select_least_used(candidates)
        elif self.rotation_strategy == 'random':
            return random.choice(candidates)
        else:
            return candidates[0]
    
    def _filter_user_agents(
        self,
        device_type: Optional[str],
        browser: Optional[str],
        mobile: Optional[bool]
    ) -> List[UserAgentInfo]:
        """Filter user agents based on criteria."""        candidates = self.user_agents.copy()
        
        if device_type:
            candidates = [ua for ua in candidates if ua.device_type == device_type]
        
        if browser:
            candidates = [ua for ua in candidates if ua.browser.lower() == browser.lower()]
        
        if mobile is not None:
            candidates = [ua for ua in candidates if ua.is_mobile == mobile]
        
        return candidates
    
    def _select_weighted_random(self, candidates: List[UserAgentInfo]) -> UserAgentInfo:
        """Select user agent using weighted random selection."""        total_weight = sum(ua.popularity_score for ua in candidates)
        
        if total_weight == 0:
            return random.choice(candidates)
        
        random_value = random.uniform(0, total_weight)
        current_weight = 0
        
        for ua in candidates:
            current_weight += ua.popularity_score
            if current_weight >= random_value:
                return ua
        
        return candidates[-1]
    
    def _select_least_used(self, candidates: List[UserAgentInfo]) -> UserAgentInfo:
        """Select least used user agent."""        min_usage = float('inf')
        selected_ua = candidates[0]
        
        for ua in candidates:
            usage_count = self.usage_history.get(ua.string, 0)
            if usage_count < min_usage:
                min_usage = usage_count
                selected_ua = ua
        
        return selected_ua
    
    def record_usage(self, user_agent: str) -> None:
        """Record user agent usage."""        self.usage_history[user_agent] = self.usage_history.get(user_agent, 0) + 1
    
    def generate_browser_fingerprint(self, user_agent: UserAgentInfo) -> BrowserFingerprint:
        """Generate realistic browser fingerprint."""        # Screen resolutions based on device type
        if user_agent.device_type == 'desktop':
            screen_resolutions = [
                (1920, 1080), (1366, 768), (1536, 864), (1440, 900),
                (1680, 1050), (2560, 1440), (3840, 2160)
            ]
        elif user_agent.device_type == 'mobile':
            screen_resolutions = [
                (375, 667), (414, 896), (390, 844), (360, 640),
                (393, 851), (412, 915)
            ]
        else:  # tablet
            screen_resolutions = [
                (768, 1024), (834, 1194), (810, 1080), (1024, 1366)
            ]
        
        screen_resolution = random.choice(screen_resolutions)
        
        # Viewport is slightly smaller than screen
        viewport_size = (
            screen_resolution[0] - random.randint(0, 20),
            screen_resolution[1] - random.randint(100, 200)
        )
        
        # Browser-specific configurations
        browser_lower = user_agent.browser.lower()
        config = self.browser_configs.get(browser_lower, self.browser_configs['chrome'])
        
        # Platform mapping
        platform_mapping = {
            'Windows': 'Win32',
            'macOS': 'MacIntel',
            'Linux': 'Linux x86_64',
            'iOS': 'iPhone',
            'Android': 'Linux armv7l',
            'iPadOS': 'iPad'
        }
        
        platform = platform_mapping.get(user_agent.os, 'Win32')
        
        # WebGL renderer based on OS
        webgl_configs = {
            'Windows': ('Google Inc. (NVIDIA)', 'ANGLE (NVIDIA, NVIDIA GeForce RTX 3070)'),
            'macOS': ('Apple Inc.', 'Apple GPU'),
            'Linux': ('Mesa/X.org', 'Mesa DRI Intel(R) UHD Graphics'),
            'iOS': ('Apple Inc.', 'Apple A15 GPU'),
            'Android': ('Qualcomm', 'Adreno (TM) 640')
        }
        
        webgl_vendor, webgl_renderer = webgl_configs.get(
            user_agent.os, 
            webgl_configs['Windows']
        )
        
        # Common plugins
        plugins = []
        if browser_lower == 'chrome':
            plugins = [
                'PDF Viewer', 'Chrome PDF Viewer', 'Chromium PDF Viewer',
                'Microsoft Edge PDF Viewer', 'WebKit built-in PDF'
            ]
        elif browser_lower == 'firefox':
            plugins = ['PDF.js']
        
        # Common fonts
        fonts = [
            'Arial', 'Times New Roman', 'Courier New', 'Verdana',
            'Georgia', 'Palatino', 'Garamond', 'Bookman',
            'Comic Sans MS', 'Trebuchet MS', 'Arial Black', 'Impact'
        ]
        
        # Timezone selection
        timezones = [
            'America/New_York', 'America/Los_Angeles', 'Europe/London',
            'Europe/Paris', 'Asia/Tokyo', 'Australia/Sydney'
        ]
        
        fingerprint = BrowserFingerprint(
            user_agent=user_agent.string,
            accept_language=config['accept_language'],
            accept_encoding=config['accept_encoding'],
            accept=config['accept'],
            screen_resolution=screen_resolution,
            viewport_size=viewport_size,
            timezone=random.choice(timezones),
            platform=platform,
            webgl_vendor=webgl_vendor,
            webgl_renderer=webgl_renderer,
            plugins=plugins,
            fonts=fonts
        )
        
        self.current_fingerprint = fingerprint
        return fingerprint
    
    def get_headers(self, user_agent: UserAgentInfo, referer: Optional[str] = None) -> Dict[str, str]:
        """Generate realistic HTTP headers."""        browser_lower = user_agent.browser.lower()
        config = self.browser_configs.get(browser_lower, self.browser_configs['chrome'])
        
        headers = {
            'User-Agent': user_agent.string,
            'Accept': config['accept'],
            'Accept-Language': config['accept_language'],
            'Accept-Encoding': config['accept_encoding'],
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': config.get('upgrade_insecure_requests', '1')
        }
        
        # Add browser-specific headers
        if browser_lower == 'chrome':
            headers.update({
                'sec-ch-ua': f'"{user_agent.browser}";v="{user_agent.browser_version.split(".")[0]}", "Not A(Brand";v="99", "Google Chrome";v="{user_agent.browser_version.split(".")[0]}"',
                'sec-ch-ua-mobile': '?1' if user_agent.is_mobile else '?0',
                'sec-ch-ua-platform': f'"{user_agent.os}"',
                'Sec-Fetch-Dest': config.get('sec_fetch_dest', 'document'),
                'Sec-Fetch-Mode': config.get('sec_fetch_mode', 'navigate'),
                'Sec-Fetch-Site': config.get('sec_fetch_site', 'none'),
                'Sec-Fetch-User': config.get('sec_fetch_user', '?1')
            })
        
        if referer:
            headers['Referer'] = referer
        
        # Record usage
        self.record_usage(user_agent.string)
        
        return headers
    
    def get_mobile_user_agent(self) -> UserAgentInfo:
        """Get a mobile user agent."""        return self.get_user_agent(mobile=True)
    
    def get_desktop_user_agent(self) -> UserAgentInfo:
        """Get a desktop user agent."""        return self.get_user_agent(mobile=False)
    
    def get_random_user_agent(self) -> UserAgentInfo:
        """Get a random user agent with realistic mobile/desktop distribution."""        if random.random() < self.mobile_ratio:
            return self.get_mobile_user_agent()
        else:
            return self.get_desktop_user_agent()
    
    def get_usage_statistics(self) -> Dict:
        """Get user agent usage statistics."""        total_usage = sum(self.usage_history.values())
        
        stats = {
            'total_requests': total_usage,
            'unique_user_agents': len(self.usage_history),
            'available_user_agents': len(self.user_agents),
            'mobile_ratio': self.mobile_ratio,
            'rotation_strategy': self.rotation_strategy,
            'top_used': []
        }
        
        # Get top used user agents
        sorted_usage = sorted(
            self.usage_history.items(),
            key=lambda x: x[1],
            reverse=True
        )
        
        for ua_string, count in sorted_usage[:10]:
            # Find corresponding UserAgentInfo
            ua_info = next(
                (ua for ua in self.user_agents if ua.string == ua_string),
                None
            )
            
            if ua_info:
                stats['top_used'].append({
                    'user_agent': ua_string,
                    'browser': ua_info.browser,
                    'os': ua_info.os,
                    'device_type': ua_info.device_type,
                    'usage_count': count,
                    'usage_percentage': (count / total_usage * 100) if total_usage > 0 else 0
                })
        
        return stats
    
    def reset_usage_history(self) -> None:
        """Reset usage history."""        self.usage_history.clear()
        logger.info("User agent usage history reset")
    
    def set_rotation_strategy(self, strategy: str) -> None:
        """Set rotation strategy."""        valid_strategies = ['weighted_random', 'least_used', 'random']
        if strategy in valid_strategies:
            self.rotation_strategy = strategy
            logger.info(f"User agent rotation strategy set to: {strategy}")
        else:
            logger.warning(f"Invalid rotation strategy: {strategy}")
    
    def set_mobile_ratio(self, ratio: float) -> None:
        """Set mobile traffic ratio."""        if 0 <= ratio <= 1:
            self.mobile_ratio = ratio
            logger.info(f"Mobile ratio set to: {ratio:.1%}")
        else:
            logger.warning(f"Invalid mobile ratio: {ratio}")
    
    def add_custom_user_agent(
        self,
        user_agent_string: str,
        browser: str,
        browser_version: str,
        os: str,
        os_version: str,
        device_type: str,
        is_mobile: bool,
        popularity_score: float = 0.01
    ) -> None:
        """Add custom user agent to the pool."""        user_agent = UserAgentInfo(
            string=user_agent_string,
            browser=browser,
            browser_version=browser_version,
            os=os,
            os_version=os_version,
            device_type=device_type,
            is_mobile=is_mobile,
            popularity_score=popularity_score,
            last_updated=datetime.now()
        )
        
        self.user_agents.append(user_agent)
        logger.info(f"Added custom user agent: {browser} {browser_version} on {os}")
    
    def update_user_agent_popularity(self, user_agent_string: str, new_score: float) -> None:
        """Update popularity score for a user agent."""        for ua in self.user_agents:
            if ua.string == user_agent_string:
                ua.popularity_score = new_score
                logger.info(f"Updated popularity score for {ua.browser}: {new_score}")
                break
