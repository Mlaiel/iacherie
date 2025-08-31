"""Enterprise Browser Management System
====================================

Professional browser automation and management for industrial-grade crawling operations.
Handles WebDriver lifecycle, session management, and browser optimization for stealth crawling.

Key Features:
- Multi-browser support (Chrome, Firefox, Safari, Edge)
- Stealth mode configuration with anti-detection
- Session pooling and resource optimization
- Headless and GUI mode switching
- Browser fingerprint randomization
- Performance monitoring and health checks

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: All rights reserved. Unauthorized use, reproduction, or distribution prohibited.

⚠️  LEGAL WARNING:
This code is proprietary and confidential. Any unauthorized copying, modification, 
distribution, or use without explicit written permission from Fahed Mlaiel is strictly 
prohibited and may result in legal action.
"""import asyncio
import logging
import time
import uuid
from abc import ABC, abstractmethod
from contextlib import asynccontextmanager
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Any, Union, Set, Callable
from urllib.parse import urlparse
import json
import random
import platform
import subprocess
import psutil

from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.edge.options import Options as EdgeOptions
from selenium.webdriver.safari.options import Options as SafariOptions
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import (
    WebDriverException, TimeoutException, NoSuchElementException,
    StaleElementReferenceException, SessionNotCreatedException
)
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.firefox.service import Service as FirefoxService
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.firefox import GeckoDriverManager

from ...core.config import settings
from ...core.exceptions import BrowserError, ConfigurationError, ResourceError
from ...utils.cache_manager import CacheManager
from ...utils.performance_monitor import PerformanceMonitor
from ...utils.health_checker import HealthChecker

logger = logging.getLogger(__name__)


class BrowserType(Enum):
    """Supported browser types for automation"""    CHROME = "chrome"
    FIREFOX = "firefox"
    EDGE = "edge"
    SAFARI = "safari"


class BrowserMode(Enum):
    """Browser operation modes"""    HEADLESS = "headless"
    GUI = "gui"
    STEALTH = "stealth"
    PERFORMANCE = "performance"


class SessionStatus(Enum):
    """Browser session lifecycle status"""    INITIALIZING = "initializing"
    ACTIVE = "active"
    IDLE = "idle"
    BUSY = "busy"
    ERROR = "error"
    TERMINATED = "terminated"


@dataclass
class BrowserCapabilities:
    """Browser-specific capabilities configuration"""    javascript_enabled: bool = True
    images_enabled: bool = True
    css_enabled: bool = True
    plugins_enabled: bool = False
    popups_blocked: bool = True
    notifications_blocked: bool = True
    location_sharing_blocked: bool = True
    microphone_blocked: bool = True
    camera_blocked: bool = True
    automation_hidden: bool = True
    webgl_enabled: bool = False
    webrtc_enabled: bool = False


@dataclass
class BrowserConfiguration:
    """Comprehensive browser configuration settings"""    browser_type: BrowserType = BrowserType.CHROME
    mode: BrowserMode = BrowserMode.HEADLESS
    capabilities: BrowserCapabilities = field(default_factory=BrowserCapabilities)
    window_size: tuple = (1920, 1080)
    user_agent: Optional[str] = None
    proxy: Optional[str] = None
    timeout: int = 30
    page_load_timeout: int = 30
    implicit_wait: int = 10
    download_directory: Optional[str] = None
    profile_path: Optional[str] = None
    extensions: List[str] = field(default_factory=list)
    preferences: Dict[str, Any] = field(default_factory=dict)
    arguments: List[str] = field(default_factory=list)
    binary_location: Optional[str] = None
    stealth_config: Dict[str, Any] = field(default_factory=dict)


@dataclass
class BrowserSession:
    """Browser session management container"""    session_id: str
    browser_type: BrowserType
    driver: webdriver.Remote
    config: BrowserConfiguration
    status: SessionStatus
    created_at: float
    last_activity: float
    page_count: int = 0
    error_count: int = 0
    memory_usage: float = 0.0
    cpu_usage: float = 0.0
    tabs: List[str] = field(default_factory=list)
    cookies: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)


class BrowserDriver(ABC):
    """Abstract base class for browser driver implementations"""    
    def __init__(self, config: BrowserConfiguration):
        self.config = config
        self.capabilities = self._build_capabilities()
        
    @abstractmethod
    def _build_capabilities(self) -> Dict[str, Any]:
        """Build browser-specific capabilities"""        pass
    
    @abstractmethod
    def _setup_options(self) -> Any:
        """Setup browser-specific options"""        pass
    
    @abstractmethod
    def create_driver(self) -> webdriver.Remote:
        """Create and configure browser driver instance"""        pass
    
    @abstractmethod
    def optimize_for_stealth(self, driver: webdriver.Remote) -> None:
        """Apply stealth optimizations to browser"""        pass


class ChromeDriver(BrowserDriver):
    """Chrome browser driver implementation"""    
    def _build_capabilities(self) -> Dict[str, Any]:
        """Build Chrome-specific capabilities"""        caps = DesiredCapabilities.CHROME.copy()
        caps.update({
            'browserName': 'chrome',
            'version': '',
            'platform': 'ANY',
            'javascriptEnabled': self.config.capabilities.javascript_enabled,
            'acceptSslCerts': True,
            'acceptInsecureCerts': True,
            'goog:loggingPrefs': {
                'performance': 'ALL',
                'browser': 'ALL',
                'driver': 'ALL'
            }
        })
        return caps
    
    def _setup_options(self) -> ChromeOptions:
        """Setup Chrome-specific options"""        options = ChromeOptions()
        
        # Basic configuration
        if self.config.mode in [BrowserMode.HEADLESS, BrowserMode.STEALTH]:
            options.add_argument('--headless=new')
        
        options.add_argument(f'--window-size={self.config.window_size[0]},{self.config.window_size[1]}')
        
        # Performance optimizations
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-gpu')
        options.add_argument('--disable-background-timer-throttling')
        options.add_argument('--disable-backgrounding-occluded-windows')
        options.add_argument('--disable-renderer-backgrounding')
        options.add_argument('--disable-features=TranslateUI')
        options.add_argument('--disable-ipc-flooding-protection')
        options.add_argument('--max_old_space_size=4096')
        options.add_argument('--memory-pressure-off')
        
        # Security and stealth
        if self.config.mode == BrowserMode.STEALTH:
            options.add_argument('--disable-blink-features=AutomationControlled')
            options.add_experimental_option("excludeSwitches", ["enable-automation"])
            options.add_experimental_option('useAutomationExtension', False)
            options.add_argument('--disable-web-security')
            options.add_argument('--allow-running-insecure-content')
            options.add_argument('--disable-features=VizDisplayCompositor')
        
        # Capabilities-based configuration
        if not self.config.capabilities.images_enabled:
            options.add_argument('--disable-images')
        
        if not self.config.capabilities.javascript_enabled:
            options.add_argument('--disable-javascript')
        
        if not self.config.capabilities.plugins_enabled:
            options.add_argument('--disable-plugins')
        
        # User agent
        if self.config.user_agent:
            options.add_argument(f'--user-agent={self.config.user_agent}')
        
        # Proxy configuration
        if self.config.proxy:
            options.add_argument(f'--proxy-server={self.config.proxy}')
        
        # Binary location
        if self.config.binary_location:
            options.binary_location = self.config.binary_location
        
        # Download directory
        if self.config.download_directory:
            prefs = {"download.default_directory": self.config.download_directory}
            options.add_experimental_option("prefs", prefs)
        
        # Custom preferences
        if self.config.preferences:
            options.add_experimental_option("prefs", self.config.preferences)
        
        # Custom arguments
        for arg in self.config.arguments:
            options.add_argument(arg)
        
        # Extensions
        for extension in self.config.extensions:
            options.add_extension(extension)
        
        return options
    
    def create_driver(self) -> webdriver.Chrome:
        """Create and configure Chrome driver instance"""        try:
            options = self._setup_options()
            service = ChromeService(ChromeDriverManager().install())
            
            driver = webdriver.Chrome(
                service=service,
                options=options,
                desired_capabilities=self.capabilities
            )
            
            # Configure timeouts
            driver.set_page_load_timeout(self.config.page_load_timeout)
            driver.implicitly_wait(self.config.implicit_wait)
            
            # Apply stealth optimizations
            if self.config.mode == BrowserMode.STEALTH:
                self.optimize_for_stealth(driver)
            
            return driver
            
        except Exception as e:
            logger.error(f"Failed to create Chrome driver: {str(e)}")
            raise BrowserError(f"Chrome driver creation failed: {str(e)}")
    
    def optimize_for_stealth(self, driver: webdriver.Chrome) -> None:
        """Apply stealth optimizations to Chrome"""        stealth_script = """        // Hide webdriver property
        Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
        
        // Mock plugins
        Object.defineProperty(navigator, 'plugins', {
            get: () => [1, 2, 3, 4, 5]
        });
        
        // Mock languages
        Object.defineProperty(navigator, 'languages', {
            get: () => ['en-US', 'en']
        });
        
        // Mock permissions
        const originalQuery = window.navigator.permissions.query;
        window.navigator.permissions.query = (parameters) => (
            parameters.name === 'notifications' ?
                Promise.resolve({ state: Notification.permission }) :
                originalQuery(parameters)
        );
        
        // Mock chrome runtime
        window.chrome = {
            runtime: {}
        };
        
        // Randomize screen properties
        Object.defineProperty(screen, 'availHeight', {get: () => 1040});
        Object.defineProperty(screen, 'availWidth', {get: () => 1920});
        """        
        driver.execute_script(stealth_script)


class FirefoxDriver(BrowserDriver):
    """Firefox browser driver implementation"""    
    def _build_capabilities(self) -> Dict[str, Any]:
        """Build Firefox-specific capabilities"""        caps = DesiredCapabilities.FIREFOX.copy()
        caps.update({
            'browserName': 'firefox',
            'marionette': True,
            'acceptInsecureCerts': True,
            'moz:firefoxOptions': {
                'log': {'level': 'trace'}
            }
        })
        return caps
    
    def _setup_options(self) -> FirefoxOptions:
        """Setup Firefox-specific options"""        options = FirefoxOptions()
        
        if self.config.mode in [BrowserMode.HEADLESS, BrowserMode.STEALTH]:
            options.add_argument('--headless')
        
        # User agent
        if self.config.user_agent:
            options.set_preference('general.useragent.override', self.config.user_agent)
        
        # Disable images
        if not self.config.capabilities.images_enabled:
            options.set_preference('permissions.default.image', 2)
        
        # Disable JavaScript
        if not self.config.capabilities.javascript_enabled:
            options.set_preference('javascript.enabled', False)
        
        return options
    
    def create_driver(self) -> webdriver.Firefox:
        """Create and configure Firefox driver instance"""        try:
            options = self._setup_options()
            service = FirefoxService(GeckoDriverManager().install())
            
            driver = webdriver.Firefox(
                service=service,
                options=options,
                desired_capabilities=self.capabilities
            )
            
            driver.set_page_load_timeout(self.config.page_load_timeout)
            driver.implicitly_wait(self.config.implicit_wait)
            
            if self.config.mode == BrowserMode.STEALTH:
                self.optimize_for_stealth(driver)
            
            return driver
            
        except Exception as e:
            logger.error(f"Failed to create Firefox driver: {str(e)}")
            raise BrowserError(f"Firefox driver creation failed: {str(e)}")
    
    def optimize_for_stealth(self, driver: webdriver.Firefox) -> None:
        """Apply stealth optimizations to Firefox"""        # Firefox stealth script
        stealth_script = """        Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
        """        driver.execute_script(stealth_script)


class BrowserManager:
    """    Enterprise Browser Management System
    
    Manages browser sessions, pools, and optimization for industrial-grade web automation.
    Provides session pooling, health monitoring, and resource management.
    """    
    def __init__(self, max_sessions: int = 10, session_timeout: int = 3600):
        self.max_sessions = max_sessions
        self.session_timeout = session_timeout
        
        # Session management
        self.sessions: Dict[str, BrowserSession] = {}
        self.session_pool: Set[str] = set()
        self.active_sessions: Set[str] = set()
        
        # Monitoring and optimization
        self.performance_monitor = PerformanceMonitor()
        self.health_checker = HealthChecker()
        self.cache_manager = CacheManager()
        
        # Statistics
        self.stats = {
            'sessions_created': 0,
            'sessions_destroyed': 0,
            'total_pages_loaded': 0,
            'total_errors': 0,
            'average_session_duration': 0.0
        }
        
        # Driver factory mapping
        self.driver_factory = {
            BrowserType.CHROME: ChromeDriver,
            BrowserType.FIREFOX: FirefoxDriver,
            # EdgeDriver and SafariDriver implementations would go here
        }
        
        logger.info("BrowserManager initialized successfully")
    
    async def create_session(self, config: BrowserConfiguration) -> str:
        """Create a new browser session with specified configuration"""        if len(self.sessions) >= self.max_sessions:
            await self._cleanup_expired_sessions()
            
            if len(self.sessions) >= self.max_sessions:
                raise ResourceError("Maximum browser sessions reached")
        
        session_id = str(uuid.uuid4())
        
        try:
            # Create driver instance
            driver_class = self.driver_factory.get(config.browser_type)
            if not driver_class:
                raise BrowserError(f"Unsupported browser type: {config.browser_type}")
            
            driver_instance = driver_class(config)
            driver = driver_instance.create_driver()
            
            # Create session object
            session = BrowserSession(
                session_id=session_id,
                browser_type=config.browser_type,
                driver=driver,
                config=config,
                status=SessionStatus.ACTIVE,
                created_at=time.time(),
                last_activity=time.time()
            )
            
            # Store session
            self.sessions[session_id] = session
            self.active_sessions.add(session_id)
            self.stats['sessions_created'] += 1
            
            # Start monitoring
            await self._start_session_monitoring(session_id)
            
            logger.info(f"Browser session {session_id} created successfully")
            return session_id
            
        except Exception as e:
            logger.error(f"Failed to create browser session: {str(e)}")
            raise BrowserError(f"Session creation failed: {str(e)}")
    
    async def get_session(self, session_id: str) -> Optional[BrowserSession]:
        """Retrieve browser session by ID"""        session = self.sessions.get(session_id)
        if session and await self._is_session_healthy(session_id):
            session.last_activity = time.time()
            return session
        return None
    
    async def destroy_session(self, session_id: str) -> bool:
        """Destroy browser session and cleanup resources"""        session = self.sessions.get(session_id)
        if not session:
            return False
        
        try:
            # Update session status
            session.status = SessionStatus.TERMINATED
            
            # Close browser
            if session.driver:
                session.driver.quit()
            
            # Remove from tracking
            self.sessions.pop(session_id, None)
            self.active_sessions.discard(session_id)
            self.session_pool.discard(session_id)
            
            # Update statistics
            self.stats['sessions_destroyed'] += 1
            session_duration = time.time() - session.created_at
            self._update_average_session_duration(session_duration)
            
            logger.info(f"Browser session {session_id} destroyed successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to destroy session {session_id}: {str(e)}")
            return False
    
    async def navigate_to(self, session_id: str, url: str, 
                         wait_condition: Optional[Callable] = None) -> bool:
        """Navigate browser session to specified URL"""        session = await self.get_session(session_id)
        if not session:
            raise BrowserError(f"Session {session_id} not found or unhealthy")
        
        try:
            session.status = SessionStatus.BUSY
            session.driver.get(url)
            
            # Wait for custom condition if specified
            if wait_condition:
                WebDriverWait(session.driver, session.config.timeout).until(wait_condition)
            
            # Update session metrics
            session.page_count += 1
            session.last_activity = time.time()
            session.status = SessionStatus.ACTIVE
            self.stats['total_pages_loaded'] += 1
            
            return True
            
        except Exception as e:
            session.error_count += 1
            session.status = SessionStatus.ERROR
            self.stats['total_errors'] += 1
            
            logger.error(f"Navigation failed for session {session_id}: {str(e)}")
            raise BrowserError(f"Navigation failed: {str(e)}")
    
    async def execute_script(self, session_id: str, script: str, 
                           *args) -> Any:
        """Execute JavaScript in browser session"""        session = await self.get_session(session_id)
        if not session:
            raise BrowserError(f"Session {session_id} not found")
        
        try:
            result = session.driver.execute_script(script, *args)
            session.last_activity = time.time()
            return result
            
        except Exception as e:
            session.error_count += 1
            logger.error(f"Script execution failed for session {session_id}: {str(e)}")
            raise BrowserError(f"Script execution failed: {str(e)}")
    
    async def take_screenshot(self, session_id: str, 
                            filename: Optional[str] = None) -> str:
        """Take screenshot of current page"""        session = await self.get_session(session_id)
        if not session:
            raise BrowserError(f"Session {session_id} not found")
        
        try:
            if not filename:
                filename = f"screenshot_{session_id}_{int(time.time())}.png"
            
            screenshot_path = session.driver.save_screenshot(filename)
            session.last_activity = time.time()
            
            return screenshot_path
            
        except Exception as e:
            logger.error(f"Screenshot failed for session {session_id}: {str(e)}")
            raise BrowserError(f"Screenshot failed: {str(e)}")
    
    async def get_page_source(self, session_id: str) -> str:
        """Get current page source"""        session = await self.get_session(session_id)
        if not session:
            raise BrowserError(f"Session {session_id} not found")
        
        try:
            source = session.driver.page_source
            session.last_activity = time.time()
            return source
            
        except Exception as e:
            logger.error(f"Failed to get page source for session {session_id}: {str(e)}")
            raise BrowserError(f"Failed to get page source: {str(e)}")
    
    @asynccontextmanager
    async def session_context(self, config: BrowserConfiguration):
        """Context manager for automatic session lifecycle management"""        session_id = None
        try:
            session_id = await self.create_session(config)
            session = await self.get_session(session_id)
            yield session
        finally:
            if session_id:
                await self.destroy_session(session_id)
    
    async def _start_session_monitoring(self, session_id: str) -> None:
        """Start monitoring for browser session"""        asyncio.create_task(self._monitor_session_health(session_id))
    
    async def _monitor_session_health(self, session_id: str) -> None:
        """Monitor session health and performance"""        while session_id in self.sessions:
            try:
                session = self.sessions[session_id]
                
                # Check if session expired
                if time.time() - session.last_activity > self.session_timeout:
                    logger.warning(f"Session {session_id} expired, destroying")
                    await self.destroy_session(session_id)
                    break
                
                # Update performance metrics
                await self._update_session_metrics(session_id)
                
                # Health check
                if not await self._is_session_healthy(session_id):
                    logger.warning(f"Session {session_id} unhealthy, destroying")
                    await self.destroy_session(session_id)
                    break
                
                await asyncio.sleep(30)  # Check every 30 seconds
                
            except Exception as e:
                logger.error(f"Session monitoring error for {session_id}: {str(e)}")
                break
    
    async def _is_session_healthy(self, session_id: str) -> bool:
        """Check if browser session is healthy and responsive"""        session = self.sessions.get(session_id)
        if not session or session.status == SessionStatus.TERMINATED:
            return False
        
        try:
            # Test driver responsiveness
            session.driver.current_url
            return True
        except Exception:
            return False
    
    async def _update_session_metrics(self, session_id: str) -> None:
        """Update performance metrics for session"""        session = self.sessions.get(session_id)
        if not session:
            return
        
        try:
            # Get browser process info if available
            if hasattr(session.driver, 'service') and session.driver.service.process:
                process = psutil.Process(session.driver.service.process.pid)
                session.memory_usage = process.memory_info().rss / 1024 / 1024  # MB
                session.cpu_usage = process.cpu_percent()
                
        except Exception as e:
            logger.debug(f"Failed to update metrics for session {session_id}: {str(e)}")
    
    async def _cleanup_expired_sessions(self) -> None:
        """Cleanup expired and unhealthy sessions"""        current_time = time.time()
        expired_sessions = []
        
        for session_id, session in self.sessions.items():
            if (current_time - session.last_activity > self.session_timeout or
                not await self._is_session_healthy(session_id)):
                expired_sessions.append(session_id)
        
        for session_id in expired_sessions:
            await self.destroy_session(session_id)
    
    def _update_average_session_duration(self, duration: float) -> None:
        """Update average session duration statistic"""        total_sessions = self.stats['sessions_destroyed']
        if total_sessions > 0:
            current_avg = self.stats['average_session_duration']
            self.stats['average_session_duration'] = (
                (current_avg * (total_sessions - 1) + duration) / total_sessions
            )
    
    async def get_statistics(self) -> Dict[str, Any]:
        """Get comprehensive browser manager statistics"""        active_count = len(self.active_sessions)
        total_memory = sum(session.memory_usage for session in self.sessions.values())
        average_cpu = (
            sum(session.cpu_usage for session in self.sessions.values()) / active_count
            if active_count > 0 else 0
        )
        
        return {
            **self.stats,
            'active_sessions': active_count,
            'total_sessions': len(self.sessions),
            'total_memory_usage_mb': total_memory,
            'average_cpu_usage': average_cpu,
            'session_pool_size': len(self.session_pool)
        }
    
    async def shutdown(self) -> None:
        """Shutdown browser manager and cleanup all resources"""        logger.info("Shutting down BrowserManager...")
        
        # Destroy all active sessions
        session_ids = list(self.sessions.keys())
        for session_id in session_ids:
            await self.destroy_session(session_id)
        
        # Clear collections
        self.sessions.clear()
        self.active_sessions.clear()
        self.session_pool.clear()
        
        logger.info("BrowserManager shutdown completed")


# Factory function for easy instantiation
def create_browser_manager(max_sessions: int = 10, 
                          session_timeout: int = 3600) -> BrowserManager:
    """Create and configure browser manager instance"""    return BrowserManager(max_sessions=max_sessions, session_timeout=session_timeout)


# Configuration helpers
def create_stealth_config() -> BrowserConfiguration:
    """Create configuration optimized for stealth operations"""    return BrowserConfiguration(
        browser_type=BrowserType.CHROME,
        mode=BrowserMode.STEALTH,
        capabilities=BrowserCapabilities(
            automation_hidden=True,
            plugins_enabled=False,
            popups_blocked=True,
            notifications_blocked=True
        )
    )


def create_performance_config() -> BrowserConfiguration:
    """Create configuration optimized for performance"""    return BrowserConfiguration(
        browser_type=BrowserType.CHROME,
        mode=BrowserMode.HEADLESS,
        capabilities=BrowserCapabilities(
            images_enabled=False,
            css_enabled=False,
            plugins_enabled=False,
            webgl_enabled=False
        )
    )
