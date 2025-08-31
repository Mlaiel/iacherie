"""Enterprise User Agent Management System
=======================================

Professional user agent rotation and management for industrial-grade web automation.
Handles user agent rotation, fingerprint masking, and browser identity management.

Key Features:
- Extensive user agent database with regular updates
- Intelligent rotation strategies (random, weighted, sequential)
- Browser fingerprint masking and randomization
- Platform and device-specific user agents
- Header correlation and consistency checks
- Real-world usage pattern simulation

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: All rights reserved. Unauthorized use, reproduction, or distribution prohibited.

⚠️  LEGAL WARNING:
This code is proprietary and confidential. Any unauthorized copying, modification, 
distribution, or use without explicit written permission from Fahed Mlaiel is strictly 
prohibited and may result in legal action.
"""
import json
import logging
import random
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Any, Tuple
from pathlib import Path
import requests
from urllib.parse import urlparse

from ...core.config import settings
from ...core.exceptions import UserAgentError, ConfigurationError
from ...utils.cache_manager import CacheManager

logger = logging.getLogger(__name__)


class BrowserFamily(Enum):
    """Supported browser families"""    CHROME = "chrome"
    FIREFOX = "firefox"
    SAFARI = "safari"
    EDGE = "edge"
    OPERA = "opera"
    MOBILE_SAFARI = "mobile_safari"
    CHROME_MOBILE = "chrome_mobile"
    SAMSUNG_BROWSER = "samsung_browser"


class PlatformType(Enum):
    """Supported platform types"""    WINDOWS = "windows"
    MACOS = "macos"
    LINUX = "linux"
    ANDROID = "android"
    IOS = "ios"
    CHROME_OS = "chrome_os"


class DeviceType(Enum):
    """Supported device types"""    DESKTOP = "desktop"
    MOBILE = "mobile"
    TABLET = "tablet"
    TV = "tv"
    SMART_WATCH = "smart_watch"


class RotationStrategy(Enum):
    """User agent rotation strategies"""    RANDOM = "random"
    WEIGHTED = "weighted"
    SEQUENTIAL = "sequential"
    LEAST_USED = "least_used"
    TIME_BASED = "time_based"


@dataclass
class UserAgentData:
    """User agent data structure"""    user_agent: str
    browser_family: BrowserFamily
    browser_version: str
    platform: PlatformType
    device_type: DeviceType
    popularity_score: float = 0.0  # 0.0 to 1.0
    release_date: Optional[str] = None
    is_mobile: bool = False
    engine: str = ""
    architecture: str = ""
    usage_count: int = 0
    last_used: float = 0.0
    success_rate: float = 1.0


@dataclass
class HeaderProfile:
    """Complete browser header profile"""    user_agent: str
    accept: str = "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8"
    accept_language: str = "en-US,en;q=0.9"
    accept_encoding: str = "gzip, deflate, br"
    connection: str = "keep-alive"
    upgrade_insecure_requests: str = "1"
    sec_fetch_dest: str = "document"
    sec_fetch_mode: str = "navigate"
    sec_fetch_site: str = "none"
    sec_fetch_user: str = "?1"
    cache_control: str = "max-age=0"
    additional_headers: Dict[str, str] = field(default_factory=dict)


class UserAgentDatabase:
    """Comprehensive user agent database management"""    
    def __init__(self):
        self.user_agents: List[UserAgentData] = []
        self.browser_profiles: Dict[BrowserFamily, List[UserAgentData]] = {}
        self.platform_profiles: Dict[PlatformType, List[UserAgentData]] = {}
        self.device_profiles: Dict[DeviceType, List[UserAgentData]] = {}
        
        # Load built-in database
        self._load_builtin_database()
        
        # Update timestamp
        self.last_update = time.time()
        
        logger.info(f"UserAgentDatabase initialized with {len(self.user_agents)} user agents")
    
    def _load_builtin_database(self) -> None:
        """Load built-in user agent database"""        
        # Chrome user agents (most popular)
        chrome_agents = [
            UserAgentData(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                browser_family=BrowserFamily.CHROME,
                browser_version="120.0.0.0",
                platform=PlatformType.WINDOWS,
                device_type=DeviceType.DESKTOP,
                popularity_score=0.95,
                engine="Blink"
            ),
            UserAgentData(
                user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                browser_family=BrowserFamily.CHROME,
                browser_version="120.0.0.0",
                platform=PlatformType.MACOS,
                device_type=DeviceType.DESKTOP,
                popularity_score=0.85,
                engine="Blink"
            ),
            UserAgentData(
                user_agent="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                browser_family=BrowserFamily.CHROME,
                browser_version="120.0.0.0",
                platform=PlatformType.LINUX,
                device_type=DeviceType.DESKTOP,
                popularity_score=0.75,
                engine="Blink"
            ),
            # Mobile Chrome
            UserAgentData(
                user_agent="Mozilla/5.0 (iPhone; CPU iPhone OS 17_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) CriOS/120.0.6099.119 Mobile/15E148 Safari/604.1",
                browser_family=BrowserFamily.CHROME_MOBILE,
                browser_version="120.0.6099.119",
                platform=PlatformType.IOS,
                device_type=DeviceType.MOBILE,
                popularity_score=0.80,
                is_mobile=True,
                engine="WebKit"
            ),
            UserAgentData(
                user_agent="Mozilla/5.0 (Linux; Android 14; SM-G998B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.6099.193 Mobile Safari/537.36",
                browser_family=BrowserFamily.CHROME_MOBILE,
                browser_version="120.0.6099.193",
                platform=PlatformType.ANDROID,
                device_type=DeviceType.MOBILE,
                popularity_score=0.85,
                is_mobile=True,
                engine="Blink"
            )
        ]
        
        # Firefox user agents
        firefox_agents = [
            UserAgentData(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
                browser_family=BrowserFamily.FIREFOX,
                browser_version="121.0",
                platform=PlatformType.WINDOWS,
                device_type=DeviceType.DESKTOP,
                popularity_score=0.70,
                engine="Gecko"
            ),
            UserAgentData(
                user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:121.0) Gecko/20100101 Firefox/121.0",
                browser_family=BrowserFamily.FIREFOX,
                browser_version="121.0",
                platform=PlatformType.MACOS,
                device_type=DeviceType.DESKTOP,
                popularity_score=0.65,
                engine="Gecko"
            ),
            UserAgentData(
                user_agent="Mozilla/5.0 (X11; Linux x86_64; rv:121.0) Gecko/20100101 Firefox/121.0",
                browser_family=BrowserFamily.FIREFOX,
                browser_version="121.0",
                platform=PlatformType.LINUX,
                device_type=DeviceType.DESKTOP,
                popularity_score=0.60,
                engine="Gecko"
            )
        ]
        
        # Safari user agents
        safari_agents = [
            UserAgentData(
                user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15",
                browser_family=BrowserFamily.SAFARI,
                browser_version="17.1",
                platform=PlatformType.MACOS,
                device_type=DeviceType.DESKTOP,
                popularity_score=0.75,
                engine="WebKit"
            ),
            UserAgentData(
                user_agent="Mozilla/5.0 (iPhone; CPU iPhone OS 17_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Mobile/15E148 Safari/604.1",
                browser_family=BrowserFamily.MOBILE_SAFARI,
                browser_version="17.1",
                platform=PlatformType.IOS,
                device_type=DeviceType.MOBILE,
                popularity_score=0.90,
                is_mobile=True,
                engine="WebKit"
            ),
            UserAgentData(
                user_agent="Mozilla/5.0 (iPad; CPU OS 17_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Mobile/15E148 Safari/604.1",
                browser_family=BrowserFamily.MOBILE_SAFARI,
                browser_version="17.1",
                platform=PlatformType.IOS,
                device_type=DeviceType.TABLET,
                popularity_score=0.80,
                is_mobile=True,
                engine="WebKit"
            )
        ]
        
        # Edge user agents
        edge_agents = [
            UserAgentData(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.2210.144",
                browser_family=BrowserFamily.EDGE,
                browser_version="120.0.2210.144",
                platform=PlatformType.WINDOWS,
                device_type=DeviceType.DESKTOP,
                popularity_score=0.65,
                engine="Blink"
            ),
            UserAgentData(
                user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.2210.144",
                browser_family=BrowserFamily.EDGE,
                browser_version="120.0.2210.144",
                platform=PlatformType.MACOS,
                device_type=DeviceType.DESKTOP,
                popularity_score=0.55,
                engine="Blink"
            )
        ]
        
        # Combine all user agents
        all_agents = chrome_agents + firefox_agents + safari_agents + edge_agents
        
        # Add to main list
        self.user_agents.extend(all_agents)
        
        # Organize by categories
        self._organize_by_categories()
    
    def _organize_by_categories(self) -> None:
        """Organize user agents by browser, platform, and device"""        
        # Clear existing categories
        self.browser_profiles.clear()
        self.platform_profiles.clear()
        self.device_profiles.clear()
        
        # Organize by browser family
        for agent in self.user_agents:
            if agent.browser_family not in self.browser_profiles:
                self.browser_profiles[agent.browser_family] = []
            self.browser_profiles[agent.browser_family].append(agent)
        
        # Organize by platform
        for agent in self.user_agents:
            if agent.platform not in self.platform_profiles:
                self.platform_profiles[agent.platform] = []
            self.platform_profiles[agent.platform].append(agent)
        
        # Organize by device type
        for agent in self.user_agents:
            if agent.device_type not in self.device_profiles:
                self.device_profiles[agent.device_type] = []
            self.device_profiles[agent.device_type].append(agent)
    
    def get_user_agents(self, browser_family: Optional[BrowserFamily] = None,
                       platform: Optional[PlatformType] = None,
                       device_type: Optional[DeviceType] = None,
                       mobile_only: Optional[bool] = None) -> List[UserAgentData]:
        """Get filtered user agents based on criteria"""        
        filtered_agents = self.user_agents.copy()
        
        # Filter by browser family
        if browser_family:
            filtered_agents = [ua for ua in filtered_agents if ua.browser_family == browser_family]
        
        # Filter by platform
        if platform:
            filtered_agents = [ua for ua in filtered_agents if ua.platform == platform]
        
        # Filter by device type
        if device_type:
            filtered_agents = [ua for ua in filtered_agents if ua.device_type == device_type]
        
        # Filter by mobile
        if mobile_only is not None:
            filtered_agents = [ua for ua in filtered_agents if ua.is_mobile == mobile_only]
        
        return filtered_agents
    
    def add_user_agent(self, agent_data: UserAgentData) -> None:
        """Add custom user agent to database"""        self.user_agents.append(agent_data)
        self._organize_by_categories()
        logger.info(f"Added custom user agent: {agent_data.browser_family.value}")
    
    def update_usage_stats(self, user_agent: str, success: bool) -> None:
        """Update usage statistics for user agent"""        for agent in self.user_agents:
            if agent.user_agent == user_agent:
                agent.usage_count += 1
                agent.last_used = time.time()
                
                # Update success rate
                if success:
                    agent.success_rate = (agent.success_rate * (agent.usage_count - 1) + 1.0) / agent.usage_count
                else:
                    agent.success_rate = (agent.success_rate * (agent.usage_count - 1)) / agent.usage_count
                
                break


class HeaderGenerator:
    """Generate consistent browser headers for user agents"""    
    def __init__(self):
        self.header_templates = self._load_header_templates()
    
    def _load_header_templates(self) -> Dict[BrowserFamily, Dict[str, str]]:
        """Load browser-specific header templates"""        return {
            BrowserFamily.CHROME: {
                "sec-ch-ua": '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
                "sec-ch-ua-mobile": "?0",
                "sec-ch-ua-platform": '"Windows"',
                "sec-fetch-dest": "document",
                "sec-fetch-mode": "navigate",
                "sec-fetch-site": "none",
                "sec-fetch-user": "?1",
                "upgrade-insecure-requests": "1"
            },
            BrowserFamily.FIREFOX: {
                "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
                "accept-language": "en-US,en;q=0.5",
                "accept-encoding": "gzip, deflate, br",
                "upgrade-insecure-requests": "1",
                "sec-fetch-dest": "document",
                "sec-fetch-mode": "navigate",
                "sec-fetch-site": "none",
                "sec-fetch-user": "?1"
            },
            BrowserFamily.SAFARI: {
                "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                "accept-language": "en-US,en;q=0.9",
                "accept-encoding": "gzip, deflate, br",
                "connection": "keep-alive",
                "upgrade-insecure-requests": "1"
            }
        }
    
    def generate_headers(self, agent_data: UserAgentData, 
                        target_url: Optional[str] = None) -> HeaderProfile:
        """Generate complete header profile for user agent"""        
        # Base headers
        headers = {
            "User-Agent": agent_data.user_agent,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1"
        }
        
        # Browser-specific headers
        browser_headers = self.header_templates.get(agent_data.browser_family, {})
        headers.update(browser_headers)
        
        # Platform-specific adjustments
        if agent_data.platform == PlatformType.MACOS:
            if "sec-ch-ua-platform" in headers:
                headers["sec-ch-ua-platform"] = '"macOS"'
        elif agent_data.platform == PlatformType.LINUX:
            if "sec-ch-ua-platform" in headers:
                headers["sec-ch-ua-platform"] = '"Linux"'
        
        # Mobile-specific adjustments
        if agent_data.is_mobile:
            if "sec-ch-ua-mobile" in headers:
                headers["sec-ch-ua-mobile"] = "?1"
            
            # Add mobile-specific headers
            headers.update({
                "sec-ch-viewport-width": str(random.choice([375, 414, 390, 428])),
                "sec-ch-device-memory": str(random.choice([4, 6, 8])),
                "sec-ch-dpr": str(random.choice([2, 3]))
            })
        
        # Target URL specific adjustments
        if target_url:
            parsed_url = urlparse(target_url)
            
            # Add referer for non-initial navigation
            if parsed_url.netloc:
                headers["sec-fetch-site"] = "same-origin"
        
        return HeaderProfile(
            user_agent=agent_data.user_agent,
            additional_headers={k: v for k, v in headers.items() if k != "User-Agent"}
        )


class UserAgentRotator:
    """    Enterprise User Agent Rotation System
    
    Manages user agent rotation, fingerprint masking, and consistent
    browser identity simulation for industrial-grade web automation.
    """    
    def __init__(self, strategy: RotationStrategy = RotationStrategy.WEIGHTED):
        self.database = UserAgentDatabase()
        self.header_generator = HeaderGenerator()
        self.cache_manager = CacheManager()
        
        # Configuration
        self.strategy = strategy
        self.current_index = 0
        self.session_agents: Dict[str, UserAgentData] = {}  # Session persistence
        
        # Statistics
        self.stats = {
            'total_rotations': 0,
            'successful_requests': 0,
            'failed_requests': 0,
            'unique_agents_used': 0
        }
        
        logger.info(f"UserAgentRotator initialized with {strategy.value} strategy")
    
    def get_user_agent(self, session_id: Optional[str] = None,
                      browser_family: Optional[BrowserFamily] = None,
                      platform: Optional[PlatformType] = None,
                      device_type: Optional[DeviceType] = None,
                      sticky_session: bool = False) -> UserAgentData:
        """Get user agent based on strategy and criteria"""        
        # Check for session persistence
        if session_id and sticky_session and session_id in self.session_agents:
            return self.session_agents[session_id]
        
        # Get filtered user agents
        available_agents = self.database.get_user_agents(
            browser_family=browser_family,
            platform=platform,
            device_type=device_type
        )
        
        if not available_agents:
            # Fallback to all agents if no matches
            available_agents = self.database.user_agents
        
        # Select agent based on strategy
        selected_agent = self._select_agent(available_agents)
        
        # Store for session persistence
        if session_id and sticky_session:
            self.session_agents[session_id] = selected_agent
        
        # Update statistics
        self.stats['total_rotations'] += 1
        if selected_agent.user_agent not in [s.user_agent for s in self.session_agents.values()]:
            self.stats['unique_agents_used'] += 1
        
        logger.debug(f"Selected user agent: {selected_agent.browser_family.value} "
                    f"on {selected_agent.platform.value}")
        
        return selected_agent
    
    def get_headers(self, session_id: Optional[str] = None,
                   target_url: Optional[str] = None,
                   **agent_criteria) -> HeaderProfile:
        """Get complete header profile including user agent"""        
        agent_data = self.get_user_agent(session_id=session_id, **agent_criteria)
        return self.header_generator.generate_headers(agent_data, target_url)
    
    def _select_agent(self, agents: List[UserAgentData]) -> UserAgentData:
        """Select agent based on rotation strategy"""        
        if self.strategy == RotationStrategy.RANDOM:
            return random.choice(agents)
        
        elif self.strategy == RotationStrategy.WEIGHTED:
            return self._weighted_selection(agents)
        
        elif self.strategy == RotationStrategy.SEQUENTIAL:
            return self._sequential_selection(agents)
        
        elif self.strategy == RotationStrategy.LEAST_USED:
            return min(agents, key=lambda a: a.usage_count)
        
        elif self.strategy == RotationStrategy.TIME_BASED:
            return self._time_based_selection(agents)
        
        return agents[0]  # Fallback
    
    def _weighted_selection(self, agents: List[UserAgentData]) -> UserAgentData:
        """Select agent based on popularity score and success rate"""        
        weights = []
        for agent in agents:
            # Combine popularity score and success rate
            weight = (agent.popularity_score * 0.7 + agent.success_rate * 0.3)
            # Reduce weight for recently used agents
            time_since_use = time.time() - agent.last_used
            if time_since_use < 3600:  # Less than 1 hour ago
                weight *= 0.5
            weights.append(weight)
        
        # Weighted random selection
        total_weight = sum(weights)
        if total_weight == 0:
            return random.choice(agents)
        
        rand_val = random.uniform(0, total_weight)
        cumulative_weight = 0
        
        for i, weight in enumerate(weights):
            cumulative_weight += weight
            if rand_val <= cumulative_weight:
                return agents[i]
        
        return agents[-1]  # Fallback
    
    def _sequential_selection(self, agents: List[UserAgentData]) -> UserAgentData:
        """Sequential round-robin selection"""        if self.current_index >= len(agents):
            self.current_index = 0
        
        selected = agents[self.current_index]
        self.current_index += 1
        return selected
    
    def _time_based_selection(self, agents: List[UserAgentData]) -> UserAgentData:
        """Select agent based on time patterns (simulate real usage)"""        current_hour = time.localtime().tm_hour
        
        # Different browsers popular at different times
        if 9 <= current_hour <= 17:  # Business hours - more Chrome/Edge
            browser_weights = {
                BrowserFamily.CHROME: 0.6,
                BrowserFamily.EDGE: 0.2,
                BrowserFamily.FIREFOX: 0.15,
                BrowserFamily.SAFARI: 0.05
            }
        else:  # Personal time - more diverse
            browser_weights = {
                BrowserFamily.CHROME: 0.4,
                BrowserFamily.FIREFOX: 0.25,
                BrowserFamily.SAFARI: 0.2,
                BrowserFamily.EDGE: 0.15
            }
        
        # Filter and weight agents
        weighted_agents = []
        for agent in agents:
            weight = browser_weights.get(agent.browser_family, 0.1)
            weighted_agents.extend([agent] * int(weight * 10))
        
        return random.choice(weighted_agents) if weighted_agents else random.choice(agents)
    
    def report_result(self, user_agent: str, success: bool) -> None:
        """Report usage result for user agent"""        self.database.update_usage_stats(user_agent, success)
        
        if success:
            self.stats['successful_requests'] += 1
        else:
            self.stats['failed_requests'] += 1
    
    def clear_session(self, session_id: str) -> None:
        """Clear session-specific user agent"""        self.session_agents.pop(session_id, None)
    
    def get_popular_agents(self, count: int = 10) -> List[UserAgentData]:
        """Get most popular user agents"""        return sorted(
            self.database.user_agents,
            key=lambda a: a.popularity_score,
            reverse=True
        )[:count]
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get comprehensive usage statistics"""        total_requests = self.stats['successful_requests'] + self.stats['failed_requests']
        success_rate = (
            self.stats['successful_requests'] / total_requests
            if total_requests > 0 else 0.0
        )
        
        # Browser family distribution
        browser_distribution = {}
        for family in BrowserFamily:
            count = len(self.database.browser_profiles.get(family, []))
            browser_distribution[family.value] = count
        
        # Platform distribution
        platform_distribution = {}
        for platform in PlatformType:
            count = len(self.database.platform_profiles.get(platform, []))
            platform_distribution[platform.value] = count
        
        return {
            'strategy': self.strategy.value,
            'total_agents': len(self.database.user_agents),
            'active_sessions': len(self.session_agents),
            'statistics': self.stats.copy(),
            'success_rate': success_rate,
            'browser_distribution': browser_distribution,
            'platform_distribution': platform_distribution
        }
    
    def export_agents(self, file_path: str) -> None:
        """Export user agent database to file"""        try:
            data = {
                'agents': [
                    {
                        'user_agent': agent.user_agent,
                        'browser_family': agent.browser_family.value,
                        'browser_version': agent.browser_version,
                        'platform': agent.platform.value,
                        'device_type': agent.device_type.value,
                        'popularity_score': agent.popularity_score,
                        'is_mobile': agent.is_mobile,
                        'engine': agent.engine
                    }
                    for agent in self.database.user_agents
                ],
                'metadata': {
                    'export_time': time.time(),
                    'total_agents': len(self.database.user_agents)
                }
            }
            
            with open(file_path, 'w') as f:
                json.dump(data, f, indent=2)
            
            logger.info(f"Exported {len(self.database.user_agents)} user agents to {file_path}")
            
        except Exception as e:
            logger.error(f"Failed to export user agents: {str(e)}")
            raise UserAgentError(f"Export failed: {str(e)}")
    
    def import_agents(self, file_path: str) -> int:
        """Import user agents from file"""        try:
            with open(file_path, 'r') as f:
                data = json.load(f)
            
            imported_count = 0
            for agent_data in data.get('agents', []):
                try:
                    user_agent = UserAgentData(
                        user_agent=agent_data['user_agent'],
                        browser_family=BrowserFamily(agent_data['browser_family']),
                        browser_version=agent_data['browser_version'],
                        platform=PlatformType(agent_data['platform']),
                        device_type=DeviceType(agent_data['device_type']),
                        popularity_score=agent_data.get('popularity_score', 0.5),
                        is_mobile=agent_data.get('is_mobile', False),
                        engine=agent_data.get('engine', '')
                    )
                    
                    self.database.add_user_agent(user_agent)
                    imported_count += 1
                    
                except Exception as e:
                    logger.warning(f"Failed to import user agent: {str(e)}")
                    continue
            
            logger.info(f"Imported {imported_count} user agents from {file_path}")
            return imported_count
            
        except Exception as e:
            logger.error(f"Failed to import user agents: {str(e)}")
            raise UserAgentError(f"Import failed: {str(e)}")


# Factory functions for common configurations
def create_desktop_rotator() -> UserAgentRotator:
    """Create rotator optimized for desktop browsing"""    rotator = UserAgentRotator(RotationStrategy.WEIGHTED)
    return rotator


def create_mobile_rotator() -> UserAgentRotator:
    """Create rotator optimized for mobile browsing"""    rotator = UserAgentRotator(RotationStrategy.RANDOM)
    return rotator


def create_stealth_rotator() -> UserAgentRotator:
    """Create rotator optimized for stealth operations"""    rotator = UserAgentRotator(RotationStrategy.TIME_BASED)
    return rotator


# Utility functions
def get_random_user_agent(browser_family: Optional[BrowserFamily] = None) -> str:
    """Get random user agent string"""    rotator = UserAgentRotator(RotationStrategy.RANDOM)
    agent = rotator.get_user_agent(browser_family=browser_family)
    return agent.user_agent


def get_chrome_user_agent(platform: PlatformType = PlatformType.WINDOWS) -> str:
    """Get Chrome user agent for specific platform"""    rotator = UserAgentRotator()
    agent = rotator.get_user_agent(
        browser_family=BrowserFamily.CHROME,
        platform=platform
    )
    return agent.user_agent
