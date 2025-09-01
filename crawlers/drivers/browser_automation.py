"""Enterprise Browser Automation Manager
====================================

Advanced browser automation and WebDriver management system.
Provides intelligent session management, stealth configurations, and performance optimization.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: All rights reserved. Unauthorized use, reproduction, or distribution prohibited.

⚠️  LEGAL WARNING:
This code is proprietary and confidential. Any unauthorized copying, modification, 
distribution, or use without explicit written permission from Fahed Mlaiel is strictly 
prohibited and may result in legal action.

Professional Development Team Specialties:
🥇 Lead AI Developer & Backend Senior Engineer - Advanced automation systems
🥇 Machine Learning Engineer & Audio Processing Specialist - Intelligence optimization  
🥇 Database Administrator & Security Expert - Data protection and performance
🥇 Microservices Architect & DevOps Engineer - Scalable infrastructure
🥇 AI Prompt Engineer & Content Protection Specialist - Content security
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Union, Any, Callable
from dataclasses import dataclass, field
from enum import Enum
from contextlib import asynccontextmanager
import json
import random
import time
from pathlib import Path

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.edge.options import Options as EdgeOptions
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.edge.service import Service as EdgeService
from selenium.common.exceptions import TimeoutException, WebDriverException
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.firefox import GeckoDriverManager
from webdriver_manager.microsoft import EdgeChromiumDriverManager


class BrowserType(Enum):
    """
Supported browser types"""

    CHROME = "chrome"
    FIREFOX = "firefox"
    EDGE = "edge"
    SAFARI = "safari"


class BrowserMode(Enum):
    """Browser execution modes"""

    HEADLESS = "headless"
    VISIBLE = "visible"
    STEALTH = "stealth"
    PERFORMANCE = "performance"


class SessionStatus(Enum):
    """Browser session status"""

    IDLE = "idle"
    ACTIVE = "active"
    BUSY = "busy"
    ERROR = "error"
    CLOSING = "closing"
    CLOSED = "closed"


@dataclass
class BrowserConfiguration:
    """Browser configuration settings"""
    browser_type: BrowserType = BrowserType.CHROME
    mode: BrowserMode = BrowserMode.HEADLESS
    window_size: tuple = (1920, 1080)
    user_agent: Optional[str] = None
    proxy: Optional[str] = None
    enable_javascript: bool = True
    enable_images: bool = True
    enable_cookies: bool = True
    enable_plugins: bool = False
    enable_extensions: bool = False
    page_load_timeout: int = 30
    implicit_wait: int = 10
    script_timeout: int = 30
    download_directory: Optional[str] = None
    profile_path: Optional[str] = None
    binary_location: Optional[str] = None
    custom_options: List[str] = field(default_factory=list)
    experimental_options: Dict[str, Any] = field(default_factory=dict)


@dataclass
class BrowserCapabilities:
    """
Browser capabilities and features"""
    supports_javascript: bool = True
    supports_cookies: bool = True
    supports_css: bool = True
    supports_popups: bool = False
    supports_alerts: bool = True
    supports_file_upload: bool = True
    supports_file_download: bool = True
    supports_screenshots: bool = True
    supports_mobile_emulation: bool = True
    maximum_sessions: int = 10


@dataclass
class BrowserSession:
    """
Browser session information"""
    session_id: str
    driver: webdriver.Remote
    config: BrowserConfiguration
    status: SessionStatus = SessionStatus.IDLE
    created_at: datetime = field(default_factory=datetime.utcnow)
    last_activity: datetime = field(default_factory=datetime.utcnow)
    requests_count: int = 0
    errors_count: int = 0
    current_url: Optional[str] = None
    page_title: Optional[str] = None
    cookies: List[Dict] = field(default_factory=list)
    local_storage: Dict[str, str] = field(default_factory=dict)
    session_storage: Dict[str, str] = field(default_factory=dict)


class ChromeDriver:
    """
Chrome WebDriver implementation with advanced configurations"""
    
    @staticmethod
    def create_options(config: BrowserConfiguration) -> ChromeOptions:
        """
Create Chrome options based on configuration"""
        options = ChromeOptions()
        
        # Basic configurations
        if config.mode in [BrowserMode.HEADLESS, BrowserMode.STEALTH]:
            options.add_argument("--headless=new")
        
        options.add_argument(f"--window-size={config.window_size[0]},{config.window_size[1]}")
        
        if config.user_agent:
            options.add_argument(f"--user-agent={config.user_agent}")
        
        if config.proxy:
            options.add_argument(f"--proxy-server={config.proxy}")
        
        # Performance optimizations
        if config.mode == BrowserMode.PERFORMANCE:
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            options.add_argument("--disable-gpu")
            options.add_argument("--disable-web-security")
            options.add_argument("--disable-features=VizDisplayCompositor")
            options.add_argument("--disable-background-timer-throttling")
            options.add_argument("--disable-backgrounding-occluded-windows")
            options.add_argument("--disable-renderer-backgrounding")
        
        # Stealth configurations
        if config.mode == BrowserMode.STEALTH:
            options.add_argument("--no-first-run")
            options.add_argument("--no-default-browser-check")
            options.add_argument("--disable-blink-features=AutomationControlled")
            options.add_argument("--disable-infobars")
            options.add_argument("--disable-notifications")
            options.add_argument("--disable-popup-blocking")
            options.add_experimental_option("excludeSwitches", ["enable-automation"])
            options.add_experimental_option('useAutomationExtension', False)
        
        # Resource loading controls
        if not config.enable_images:
            prefs = {"profile.managed_default_content_settings.images": 2}
            options.add_experimental_option("prefs", prefs)
        
        if not config.enable_javascript:
            prefs = {"profile.managed_default_content_settings.javascript": 2}
            options.add_experimental_option("prefs", prefs)
        
        # Download directory
        if config.download_directory:
            prefs = {
                "download.default_directory": config.download_directory,
                "download.prompt_for_download": False,
                "download.directory_upgrade": True,
                "safebrowsing.enabled": True
            }
            options.add_experimental_option("prefs", prefs)
        
        # Profile path
        if config.profile_path:
            options.add_argument(f"--user-data-dir={config.profile_path}")
        
        # Binary location
        if config.binary_location:
            options.binary_location = config.binary_location
        
        # Custom options
        for option in config.custom_options:
            options.add_argument(option)
        
        # Experimental options
        for key, value in config.experimental_options.items():
            options.add_experimental_option(key, value)
        
        return options
    
    @staticmethod
    def create_service() -> ChromeService:
        """Create Chrome service with automatic driver management"""
        return ChromeService(ChromeDriverManager().install())


class FirefoxDriver:
    """
Firefox WebDriver implementation with advanced configurations"""
    
    @staticmethod
    def create_options(config: BrowserConfiguration) -> FirefoxOptions:
        """
Create Firefox options based on configuration"""
        options = FirefoxOptions()
        
        # Basic configurations
        if config.mode in [BrowserMode.HEADLESS, BrowserMode.STEALTH]:
            options.add_argument("--headless")
        
        options.add_argument(f"--width={config.window_size[0]}")
        options.add_argument(f"--height={config.window_size[1]}")
        
        if config.user_agent:
            options.set_preference("general.useragent.override", config.user_agent)
        
        # Performance optimizations
        if config.mode == BrowserMode.PERFORMANCE:
            options.set_preference("browser.cache.disk.enable", False)
            options.set_preference("browser.cache.memory.enable", False)
            options.set_preference("browser.cache.offline.enable", False)
            options.set_preference("network.http.use-cache", False)
        
        # Resource loading controls
        if not config.enable_images:
            options.set_preference("permissions.default.image", 2)
        
        if not config.enable_javascript:
            options.set_preference("javascript.enabled", False)
        
        # Download directory
        if config.download_directory:
            options.set_preference("browser.download.dir", config.download_directory)
            options.set_preference("browser.download.folderList", 2)
            options.set_preference("browser.helperApps.neverAsk.saveToDisk", "application/octet-stream")
        
        # Profile path
        if config.profile_path:
            options.set_preference("profile", config.profile_path)
        
        # Binary location
        if config.binary_location:
            options.binary_location = config.binary_location
        
        return options
    
    @staticmethod
    def create_service() -> FirefoxService:
        """Create Firefox service with automatic driver management"""
        return FirefoxService(GeckoDriverManager().install())


class BrowserManager:
    """
    Enterprise browser management system for WebDriver automation.
    
    Features:
    - Multi-browser support (Chrome, Firefox, Edge)
    - Session pooling and reuse
    - Stealth and performance configurations
    - Automatic driver management
    - Health monitoring and recovery
    """
    
    def __init__(
        self,
        max_sessions: int = 5,
        session_timeout: int = 3600,
        enable_monitoring: bool = True
    ):
        self.max_sessions = max_sessions
        self.session_timeout = session_timeout
        self.enable_monitoring = enable_monitoring
        
        # Session management
        self.sessions: Dict[str, BrowserSession] = {}
        self.session_pool: List[str] = []
        
        # Driver factories
        self.driver_factories = {
            BrowserType.CHROME: self._create_chrome_driver,
            BrowserType.FIREFOX: self._create_firefox_driver,
            BrowserType.EDGE: self._create_edge_driver
        }
        
        # Monitoring
        self.total_sessions_created = 0
        self.total_requests_processed = 0
        self.total_errors = 0
        
        # Setup logging
        self.logger = logging.getLogger(__name__)
    
    async def initialize(self) -> bool:
        """
Initialize browser manager"""
        try:
            self.logger.info("Initializing browser manager...")
            
            # Start monitoring if enabled
            if self.enable_monitoring:
                asyncio.create_task(self._monitoring_loop())
            
            self.logger.info("Browser manager initialized successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize browser manager: {e}")
            return False
    
    async def create_session(
        self,
        config: BrowserConfiguration,
        session_id: Optional[str] = None
    ) -> str:
        """Create a new browser session"""
        if len(self.sessions) >= self.max_sessions:
            # Clean up idle sessions
            await self._cleanup_idle_sessions()
            
            if len(self.sessions) >= self.max_sessions:
                raise RuntimeError("Maximum browser sessions reached")
        
        if not session_id:
            session_id = f"session_{int(time.time() * 1000)}_{random.randint(1000, 9999)}"
        
        try:
            # Create WebDriver
            driver = await self._create_driver(config)
            
            # Create session object
            session = BrowserSession(
                session_id=session_id,
                driver=driver,
                config=config,
                status=SessionStatus.IDLE
            )
            
            # Apply stealth modifications if needed
            if config.mode == BrowserMode.STEALTH:
                await self._apply_stealth_modifications(session)
            
            self.sessions[session_id] = session
            self.total_sessions_created += 1
            
            self.logger.info(f"Created browser session: {session_id}")
            return session_id
            
        except Exception as e:
            self.logger.error(f"Failed to create browser session: {e}")
            raise
    
    async def get_session(self, session_id: str) -> Optional[BrowserSession]:
        """Get browser session by ID"""
        session = self.sessions.get(session_id)
        if session and session.status != SessionStatus.CLOSED:
            session.last_activity = datetime.utcnow()
            return session
        return None
    
    async def close_session(self, session_id: str) -> bool:
        """
Close browser session"""
        session = self.sessions.get(session_id)
        if not session:
            return False
        
        try:
            session.status = SessionStatus.CLOSING
            session.driver.quit()
            session.status = SessionStatus.CLOSED
            
            # Remove from sessions
            self.sessions.pop(session_id, None)
            
            self.logger.info(f"Closed browser session: {session_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error closing session {session_id}: {e}")
            return False
    
    async def navigate_to(self, session_id: str, url: str) -> bool:
        """Navigate session to URL"""
        session = await self.get_session(session_id)
        if not session:
            return False
        
        try:
            session.status = SessionStatus.BUSY
            session.driver.get(url)
            session.current_url = url
            session.page_title = session.driver.title
            session.requests_count += 1
            session.status = SessionStatus.ACTIVE
            self.total_requests_processed += 1
            
            return True
            
        except Exception as e:
            session.errors_count += 1
            session.status = SessionStatus.ERROR
            self.total_errors += 1
            self.logger.error(f"Navigation error in session {session_id}: {e}")
            return False
    
    async def execute_script(
        self,
        session_id: str,
        script: str,
        *args
    ) -> Any:
        """Execute JavaScript in session"""
        session = await self.get_session(session_id)
        if not session:
            return None
        
        try:
            session.status = SessionStatus.BUSY
            result = session.driver.execute_script(script, *args)
            session.status = SessionStatus.ACTIVE
            return result
            
        except Exception as e:
            session.errors_count += 1
            session.status = SessionStatus.ERROR
            self.logger.error(f"Script execution error in session {session_id}: {e}")
            return None
    
    async def take_screenshot(
        self,
        session_id: str,
        filename: Optional[str] = None
    ) -> Optional[str]:
        """Take screenshot of current page"""
        session = await self.get_session(session_id)
        if not session:
            return None
        
        try:
            if not filename:
                timestamp = int(time.time())
                filename = f"screenshot_{session_id}_{timestamp}.png"
            
            success = session.driver.save_screenshot(filename)
            return filename if success else None
            
        except Exception as e:
            self.logger.error(f"Screenshot error in session {session_id}: {e}")
            return None
    
    async def get_page_source(self, session_id: str) -> Optional[str]:
        """Get page source from session"""
        session = await self.get_session(session_id)
        if not session:
            return None
        
        try:
            return session.driver.page_source
        except Exception as e:
            self.logger.error(f"Page source error in session {session_id}: {e}")
            return None
    
    async def wait_for_element(
        self,
        session_id: str,
        locator: tuple,
        timeout: int = 10
    ) -> bool:
        """Wait for element to be present"""
        session = await self.get_session(session_id)
        if not session:
            return False
        
        try:
            wait = WebDriverWait(session.driver, timeout)
            wait.until(EC.presence_of_element_located(locator))
            return True
            
        except TimeoutException:
            return False
        except Exception as e:
            self.logger.error(f"Wait for element error in session {session_id}: {e}")
            return False
    
    async def cleanup(self):
        """Cleanup all browser sessions"""
        self.logger.info("Cleaning up browser manager...")
        
        for session_id in list(self.sessions.keys()):
            await self.close_session(session_id)
        
        self.logger.info("Browser manager cleanup completed")
    
    async def health_check(self) -> bool:
        """Perform health check on browser manager"""
        try:
            # Check if we can create a test session
            test_config = BrowserConfiguration(
                browser_type=BrowserType.CHROME,
                mode=BrowserMode.HEADLESS
            )
            
            session_id = await self.create_session(test_config)
            success = await self.navigate_to(session_id, "data:text/html,<html><body>Test</body></html>")
            await self.close_session(session_id)
            
            return success
            
        except Exception as e:
            self.logger.error(f"Health check failed: {e}")
            return False
    
    async def _create_driver(self, config: BrowserConfiguration) -> webdriver.Remote:
        """Create WebDriver instance based on configuration"""
        factory = self.driver_factories.get(config.browser_type)
        if not factory:
            raise ValueError(f"Unsupported browser type: {config.browser_type}")
        
        return await factory(config)
    
    async def _create_chrome_driver(self, config: BrowserConfiguration) -> webdriver.Chrome:
        """Create Chrome WebDriver"""
        options = ChromeDriver.create_options(config)
        service = ChromeDriver.create_service()
        
        driver = webdriver.Chrome(service=service, options=options)
        
        # Set timeouts
        driver.set_page_load_timeout(config.page_load_timeout)
        driver.implicitly_wait(config.implicit_wait)
        driver.set_script_timeout(config.script_timeout)
        
        return driver
    
    async def _create_firefox_driver(self, config: BrowserConfiguration) -> webdriver.Firefox:
        """
Create Firefox WebDriver"""
        options = FirefoxDriver.create_options(config)
        service = FirefoxDriver.create_service()
        
        driver = webdriver.Firefox(service=service, options=options)
        
        # Set timeouts
        driver.set_page_load_timeout(config.page_load_timeout)
        driver.implicitly_wait(config.implicit_wait)
        driver.set_script_timeout(config.script_timeout)
        
        return driver
    
    async def _create_edge_driver(self, config: BrowserConfiguration) -> webdriver.Edge:
        """
Create Edge WebDriver"""
        options = EdgeOptions()
        
        if config.mode in [BrowserMode.HEADLESS, BrowserMode.STEALTH]:
            options.add_argument("--headless")
        
        options.add_argument(f"--window-size={config.window_size[0]},{config.window_size[1]}")
        
        service = EdgeService(EdgeChromiumDriverManager().install())
        driver = webdriver.Edge(service=service, options=options)
        
        # Set timeouts
        driver.set_page_load_timeout(config.page_load_timeout)
        driver.implicitly_wait(config.implicit_wait)
        driver.set_script_timeout(config.script_timeout)
        
        return driver
    
    async def _apply_stealth_modifications(self, session: BrowserSession):
        """Apply stealth modifications to browser session"""
        try:
            # Remove webdriver property
            session.driver.execute_script(
                "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
            )
            
            # Override user agent
            if session.config.user_agent:
                session.driver.execute_cdp_cmd('Network.setUserAgentOverride', {
                    "userAgent": session.config.user_agent
                })
            
            # Override permissions
            session.driver.execute_cdp_cmd('Browser.grantPermissions', {
                "permissions": ['audioCapture', 'videoCapture'],
                "origin": session.driver.current_url
            })
            
        except Exception as e:
            self.logger.warning(f"Could not apply all stealth modifications: {e}")
    
    async def _cleanup_idle_sessions(self):
        """Clean up idle sessions that have exceeded timeout"""
        current_time = datetime.utcnow()
        idle_sessions = []
        
        for session_id, session in self.sessions.items():
            if session.status == SessionStatus.IDLE:
                idle_time = (current_time - session.last_activity).total_seconds()
                if idle_time > self.session_timeout:
                    idle_sessions.append(session_id)
        
        for session_id in idle_sessions:
            await self.close_session(session_id)
    
    async def _monitoring_loop(self):
        """
Monitoring loop for session health and cleanup"""
        while True:
            try:
                await self._cleanup_idle_sessions()
                
                # Log statistics
                active_sessions = len([s for s in self.sessions.values() if s.status == SessionStatus.ACTIVE])
                self.logger.debug(f"Browser sessions: {len(self.sessions)} total, {active_sessions} active")
                
                await asyncio.sleep(60)  # Check every minute
                
            except Exception as e:
                self.logger.error(f"Error in monitoring loop: {e}")
                await asyncio.sleep(60)


# Convenience functions
def create_browser_manager(max_sessions: int = 5, **kwargs) -> BrowserManager:
    """Create browser manager instance"""
    return BrowserManager(max_sessions=max_sessions, **kwargs)


def create_stealth_config(
    browser_type: BrowserType = BrowserType.CHROME,
    user_agent: Optional[str] = None
) -> BrowserConfiguration:
    """
Create stealth browser configuration"""
    return BrowserConfiguration(
        browser_type=browser_type,
        mode=BrowserMode.STEALTH,
        user_agent=user_agent,
        enable_images=False,
        enable_plugins=False,
        enable_extensions=False
    )


def create_performance_config(
    browser_type: BrowserType = BrowserType.CHROME
) -> BrowserConfiguration:
    """
Create performance-optimized browser configuration"""
    return BrowserConfiguration(
        browser_type=browser_type,
        mode=BrowserMode.PERFORMANCE,
        enable_images=False,
        enable_plugins=False,
        enable_extensions=False,
        page_load_timeout=15,
        implicit_wait=5
    )
