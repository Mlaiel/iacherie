"""Enterprise WebDriver Factory System
===================================

Professional WebDriver creation and management factory for industrial-grade automation.
Provides standardized driver creation, configuration management, and optimization presets.

Key Features:
- Multi-browser driver factory (Chrome, Firefox, Edge, Safari)
- Configuration presets for different use cases
- Performance and stealth optimization profiles
- Resource management and cleanup
- Cross-platform compatibility
- Docker and cloud environment support

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: All rights reserved. Unauthorized use, reproduction, or distribution prohibited.

⚠️  LEGAL WARNING:
This code is proprietary and confidential. Any unauthorized copying, modification, 
distribution, or use without explicit written permission from Fahed Mlaiel is strictly 
prohibited and may result in legal action.
"""
import logging
import os
import platform
import shutil
import tempfile
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Any, Union, Callable
import json

from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.edge.options import Options as EdgeOptions
from selenium.webdriver.safari.options import Options as SafariOptions
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.edge.service import Service as EdgeService
from selenium.webdriver.safari.service import Service as SafariService
from selenium.common.exceptions import WebDriverException, SessionNotCreatedException
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.firefox import GeckoDriverManager
from webdriver_manager.microsoft import EdgeChromiumDriverManager

from ...core.config import settings
from ...core.exceptions import DriverError, ConfigurationError
from .browser_manager import BrowserType, BrowserMode, BrowserConfiguration, BrowserCapabilities

logger = logging.getLogger(__name__)


class DriverProfile(Enum):
    """Predefined driver configuration profiles"""
    STEALTH = "stealth"
    PERFORMANCE = "performance"
    DEBUGGING = "debugging"
    MOBILE = "mobile"
    TESTING = "testing"
    PRODUCTION = "production"
    DEVELOPMENT = "development"


class EnvironmentType(Enum):
    """Target environment types"""
    LOCAL = "local"
    DOCKER = "docker"
    CLOUD = "cloud"
    CI_CD = "ci_cd"


@dataclass
class DriverCapability:
    """Individual driver capability setting"""
    name: str
    value: Any
    required: bool = False
    description: str = ""


@dataclass
class DriverPreset:
    """Driver configuration preset"""
    profile: DriverProfile
    browser_type: BrowserType
    capabilities: List[DriverCapability]
    options: List[str]
    preferences: Dict[str, Any]
    description: str = ""
    recommended_use: str = ""


class WebDriverFactory:
    """
    Enterprise WebDriver Factory System
    
    Creates optimized WebDriver instances based on configuration profiles,
    environment requirements, and performance specifications.
    """
    
    def __init__(self, environment: EnvironmentType = EnvironmentType.LOCAL):
        self.environment = environment
        self.temp_directories: List[str] = []
        
        # Driver presets
        self.presets = self._initialize_presets()
        
        # Environment-specific settings
        self.env_settings = self._get_environment_settings()
        
        logger.info(f"WebDriverFactory initialized for {environment.value} environment")
    
    def create_driver(self, config: BrowserConfiguration, 
                     profile: Optional[DriverProfile] = None) -> webdriver.Remote:
        """Create optimized WebDriver instance"""
        try:
            # Apply preset if specified
            if profile:
                config = self._apply_preset(config, profile)
            
            # Environment-specific adjustments
            config = self._apply_environment_settings(config)
            
            # Create driver based on browser type
            if config.browser_type == BrowserType.CHROME:
                return self._create_chrome_driver(config)
            elif config.browser_type == BrowserType.FIREFOX:
                return self._create_firefox_driver(config)
            elif config.browser_type == BrowserType.EDGE:
                return self._create_edge_driver(config)
            elif config.browser_type == BrowserType.SAFARI:
                return self._create_safari_driver(config)
            else:
                raise DriverError(f"Unsupported browser type: {config.browser_type}")
                
        except Exception as e:
            logger.error(f"Failed to create WebDriver: {str(e)}")
            raise DriverError(f"Driver creation failed: {str(e)}")
    
    def create_stealth_driver(self, browser_type: BrowserType = BrowserType.CHROME) -> webdriver.Remote:
        """Create stealth-optimized driver for anti-detection"""
        config = BrowserConfiguration(
            browser_type=browser_type,
            mode=BrowserMode.STEALTH,
            capabilities=BrowserCapabilities(automation_hidden=True)
        )
        return self.create_driver(config, DriverProfile.STEALTH)
    
    def create_performance_driver(self, browser_type: BrowserType = BrowserType.CHROME) -> webdriver.Remote:
        """Create performance-optimized driver for speed"""
        config = BrowserConfiguration(
            browser_type=browser_type,
            mode=BrowserMode.HEADLESS,
            capabilities=BrowserCapabilities(
                images_enabled=False,
                css_enabled=False,
                plugins_enabled=False
            )
        )
        return self.create_driver(config, DriverProfile.PERFORMANCE)
    
    def create_mobile_driver(self, device_name: str = "iPhone 12") -> webdriver.Remote:
        """Create mobile-emulation driver"""
        config = BrowserConfiguration(
            browser_type=BrowserType.CHROME,
            mode=BrowserMode.GUI
        )
        return self._create_mobile_chrome_driver(config, device_name)
    
    def create_testing_driver(self, browser_type: BrowserType = BrowserType.CHROME) -> webdriver.Remote:
        """Create driver optimized for testing"""
        config = BrowserConfiguration(
            browser_type=browser_type,
            mode=BrowserMode.HEADLESS,
            timeout=60,
            page_load_timeout=60
        )
        return self.create_driver(config, DriverProfile.TESTING)
    
    def _create_chrome_driver(self, config: BrowserConfiguration) -> webdriver.Chrome:
        """Create Chrome WebDriver with advanced configuration"""
        options = ChromeOptions()
        
        # Basic configuration
        if config.mode in [BrowserMode.HEADLESS, BrowserMode.STEALTH]:
            options.add_argument("--headless=new")
        
        # Window size
        options.add_argument(f"--window-size={config.window_size[0]},{config.window_size[1]}")
        
        # Performance optimizations
        performance_args = [
            "--no-sandbox",
            "--disable-dev-shm-usage",
            "--disable-gpu",
            "--disable-background-timer-throttling",
            "--disable-backgrounding-occluded-windows",
            "--disable-renderer-backgrounding",
            "--disable-features=TranslateUI",
            "--disable-ipc-flooding-protection",
            "--max_old_space_size=4096",
            "--memory-pressure-off"
        ]
        
        for arg in performance_args:
            options.add_argument(arg)
        
        # Stealth optimizations
        if config.mode == BrowserMode.STEALTH:
            stealth_args = [
                "--disable-blink-features=AutomationControlled",
                "--disable-web-security",
                "--allow-running-insecure-content",
                "--disable-features=VizDisplayCompositor",
                "--disable-extensions",
                "--disable-plugins",
                "--disable-default-apps"
            ]
            
            for arg in stealth_args:
                options.add_argument(arg)
            
            options.add_experimental_option("excludeSwitches", ["enable-automation"])
            options.add_experimental_option('useAutomationExtension', False)
        
        # Capabilities configuration
        if not config.capabilities.images_enabled:
            prefs = {"profile.managed_default_content_settings.images": 2}
            options.add_experimental_option("prefs", prefs)
        
        if not config.capabilities.javascript_enabled:
            prefs = {"profile.managed_default_content_settings.javascript": 2}
            options.add_experimental_option("prefs", prefs)
        
        # User agent
        if config.user_agent:
            options.add_argument(f"--user-agent={config.user_agent}")
        
        # Proxy
        if config.proxy:
            options.add_argument(f"--proxy-server={config.proxy}")
        
        # Download directory
        if config.download_directory:
            prefs = {"download.default_directory": config.download_directory}
            options.add_experimental_option("prefs", prefs)
        
        # Custom preferences
        if config.preferences:
            options.add_experimental_option("prefs", config.preferences)
        
        # Custom arguments
        for arg in config.arguments:
            options.add_argument(arg)
        
        # Binary location
        if config.binary_location:
            options.binary_location = config.binary_location
        
        # Environment-specific adjustments
        if self.environment == EnvironmentType.DOCKER:
            options.add_argument("--disable-dev-shm-usage")
            options.add_argument("--no-sandbox")
        elif self.environment == EnvironmentType.CI_CD:
            options.add_argument("--headless=new")
            options.add_argument("--disable-gpu")
        
        try:
            # Create service
            if self.env_settings.get("driver_path"):
                service = ChromeService(executable_path=self.env_settings["driver_path"])
            else:
                service = ChromeService(ChromeDriverManager().install())
            
            # Create driver
            driver = webdriver.Chrome(service=service, options=options)
            
            # Configure timeouts
            driver.set_page_load_timeout(config.page_load_timeout)
            driver.implicitly_wait(config.implicit_wait)
            
            # Apply stealth scripts
            if config.mode == BrowserMode.STEALTH:
                self._apply_stealth_scripts(driver)
            
            return driver
            
        except Exception as e:
            logger.error(f"Chrome driver creation failed: {str(e)}")
            raise DriverError(f"Chrome driver creation failed: {str(e)}")
    
    def _create_firefox_driver(self, config: BrowserConfiguration) -> webdriver.Firefox:
        """Create Firefox WebDriver with advanced configuration"""
        options = FirefoxOptions()
        
        if config.mode in [BrowserMode.HEADLESS, BrowserMode.STEALTH]:
            options.add_argument("--headless")
        
        # User agent
        if config.user_agent:
            options.set_preference("general.useragent.override", config.user_agent)
        
        # Disable images
        if not config.capabilities.images_enabled:
            options.set_preference("permissions.default.image", 2)
        
        # Disable JavaScript
        if not config.capabilities.javascript_enabled:
            options.set_preference("javascript.enabled", False)
        
        # Proxy configuration
        if config.proxy:
            proxy_host, proxy_port = config.proxy.split(":")
            options.set_preference("network.proxy.type", 1)
            options.set_preference("network.proxy.http", proxy_host)
            options.set_preference("network.proxy.http_port", int(proxy_port))
        
        try:
            service = FirefoxService(GeckoDriverManager().install())
            driver = webdriver.Firefox(service=service, options=options)
            
            driver.set_page_load_timeout(config.page_load_timeout)
            driver.implicitly_wait(config.implicit_wait)
            
            return driver
            
        except Exception as e:
            logger.error(f"Firefox driver creation failed: {str(e)}")
            raise DriverError(f"Firefox driver creation failed: {str(e)}")
    
    def _create_edge_driver(self, config: BrowserConfiguration) -> webdriver.Edge:
        """Create Edge WebDriver with advanced configuration"""
        options = EdgeOptions()
        
        if config.mode in [BrowserMode.HEADLESS, BrowserMode.STEALTH]:
            options.add_argument("--headless")
        
        options.add_argument(f"--window-size={config.window_size[0]},{config.window_size[1]}")
        
        if config.user_agent:
            options.add_argument(f"--user-agent={config.user_agent}")
        
        try:
            service = EdgeService(EdgeChromiumDriverManager().install())
            driver = webdriver.Edge(service=service, options=options)
            
            driver.set_page_load_timeout(config.page_load_timeout)
            driver.implicitly_wait(config.implicit_wait)
            
            return driver
            
        except Exception as e:
            logger.error(f"Edge driver creation failed: {str(e)}")
            raise DriverError(f"Edge driver creation failed: {str(e)}")
    
    def _create_safari_driver(self, config: BrowserConfiguration) -> webdriver.Safari:
        """Create Safari WebDriver (macOS only)"""
        if platform.system() != "Darwin":
            raise DriverError("Safari WebDriver is only available on macOS")
        
        try:
            driver = webdriver.Safari()
            
            driver.set_page_load_timeout(config.page_load_timeout)
            driver.implicitly_wait(config.implicit_wait)
            
            return driver
            
        except Exception as e:
            logger.error(f"Safari driver creation failed: {str(e)}")
            raise DriverError(f"Safari driver creation failed: {str(e)}")
    
    def _create_mobile_chrome_driver(self, config: BrowserConfiguration, 
                                   device_name: str) -> webdriver.Chrome:
        """Create Chrome driver with mobile device emulation"""
        options = ChromeOptions()
        
        # Mobile emulation
        mobile_emulation = {"deviceName": device_name}
        options.add_experimental_option("mobileEmulation", mobile_emulation)
        
        # Standard configuration
        if config.mode == BrowserMode.HEADLESS:
            options.add_argument("--headless=new")
        
        try:
            service = ChromeService(ChromeDriverManager().install())
            driver = webdriver.Chrome(service=service, options=options)
            
            driver.set_page_load_timeout(config.page_load_timeout)
            driver.implicitly_wait(config.implicit_wait)
            
            return driver
            
        except Exception as e:
            logger.error(f"Mobile Chrome driver creation failed: {str(e)}")
            raise DriverError(f"Mobile Chrome driver creation failed: {str(e)}")
    
    def _apply_stealth_scripts(self, driver: webdriver.Remote) -> None:
        """Apply comprehensive stealth scripts to hide automation"""
        stealth_scripts = [
            # Hide webdriver property
            "Object.defineProperty(navigator, 'webdriver', {get: () => undefined});",
            
            # Mock plugins
            """
            Object.defineProperty(navigator, 'plugins', {
                get: () => [1, 2, 3, 4, 5]
            });
            """,
            
            # Mock languages
            """
            Object.defineProperty(navigator, 'languages', {
                get: () => ['en-US', 'en']
            });
            """,
            
            # Mock permissions
            """
            const originalQuery = window.navigator.permissions.query;
            window.navigator.permissions.query = (parameters) => (
                parameters.name === 'notifications' ?
                    Promise.resolve({ state: Notification.permission }) :
                    originalQuery(parameters)
            );
            """,
            
            # Mock chrome runtime
            """
            window.chrome = {
                runtime: {}
            };
            """,
            
            # Randomize screen properties
            """
            Object.defineProperty(screen, 'availHeight', {get: () => 1040});
            Object.defineProperty(screen, 'availWidth', {get: () => 1920});
            Object.defineProperty(screen, 'colorDepth', {get: () => 24});
            Object.defineProperty(screen, 'pixelDepth', {get: () => 24});
            """
        ]
        
        for script in stealth_scripts:
            try:
                driver.execute_script(script)
            except Exception as e:
                logger.warning(f"Failed to execute stealth script: {str(e)}")
    
    def _apply_preset(self, config: BrowserConfiguration, 
                     profile: DriverProfile) -> BrowserConfiguration:
        """Apply configuration preset to browser configuration"""
        preset = self.presets.get((profile, config.browser_type))
        if not preset:
            logger.warning(f"No preset found for {profile.value} + {config.browser_type.value}")
            return config
        
        # Apply preset preferences
        config.preferences.update(preset.preferences)
        
        # Apply preset arguments
        config.arguments.extend(preset.options)
        
        logger.info(f"Applied {profile.value} preset for {config.browser_type.value}")
        return config
    
    def _apply_environment_settings(self, config: BrowserConfiguration) -> BrowserConfiguration:
        """Apply environment-specific settings"""
        env_args = self.env_settings.get("arguments", [])
        config.arguments.extend(env_args)
        
        # Docker-specific settings
        if self.environment == EnvironmentType.DOCKER:
            config.arguments.extend([
                "--no-sandbox",
                "--disable-dev-shm-usage",
                "--disable-gpu"
            ])
        
        # CI/CD-specific settings
        elif self.environment == EnvironmentType.CI_CD:
            config.mode = BrowserMode.HEADLESS
            config.arguments.extend([
                "--headless=new",
                "--no-sandbox",
                "--disable-gpu",
                "--disable-dev-shm-usage"
            ])
        
        return config
    
    def _initialize_presets(self) -> Dict[tuple, DriverPreset]:
        """Initialize driver configuration presets"""
        presets = {}
        
        # Stealth preset for Chrome
        stealth_chrome = DriverPreset(
            profile=DriverProfile.STEALTH,
            browser_type=BrowserType.CHROME,
            capabilities=[],
            options=[
                "--disable-blink-features=AutomationControlled",
                "--disable-web-security",
                "--allow-running-insecure-content",
                "--disable-features=VizDisplayCompositor"
            ],
            preferences={
                "profile.default_content_setting_values.notifications": 2,
                "profile.default_content_settings.popups": 0,
                "profile.managed_default_content_settings.images": 1
            },
            description="Optimized for stealth crawling and anti-detection",
            recommended_use="Web scraping, automated testing, surveillance"
        )
        presets[(DriverProfile.STEALTH, BrowserType.CHROME)] = stealth_chrome
        
        # Performance preset for Chrome
        performance_chrome = DriverPreset(
            profile=DriverProfile.PERFORMANCE,
            browser_type=BrowserType.CHROME,
            capabilities=[],
            options=[
                "--disable-images",
                "--disable-javascript",
                "--disable-plugins",
                "--disable-extensions"
            ],
            preferences={
                "profile.managed_default_content_settings.images": 2,
                "profile.managed_default_content_settings.javascript": 2,
                "profile.managed_default_content_settings.plugins": 2
            },
            description="Optimized for maximum speed and minimal resource usage",
            recommended_use="High-volume crawling, performance testing"
        )
        presets[(DriverProfile.PERFORMANCE, BrowserType.CHROME)] = performance_chrome
        
        # Testing preset for Chrome
        testing_chrome = DriverPreset(
            profile=DriverProfile.TESTING,
            browser_type=BrowserType.CHROME,
            capabilities=[],
            options=[
                "--disable-web-security",
                "--allow-running-insecure-content",
                "--disable-features=VizDisplayCompositor"
            ],
            preferences={
                "profile.default_content_setting_values.notifications": 2
            },
            description="Optimized for automated testing and debugging",
            recommended_use="Unit testing, integration testing, debugging"
        )
        presets[(DriverProfile.TESTING, BrowserType.CHROME)] = testing_chrome
        
        return presets
    
    def _get_environment_settings(self) -> Dict[str, Any]:
        """Get environment-specific settings"""
        settings_map = {
            EnvironmentType.LOCAL: {
                "arguments": [],
                "driver_path": None
            },
            EnvironmentType.DOCKER: {
                "arguments": [
                    "--no-sandbox",
                    "--disable-dev-shm-usage",
                    "--disable-gpu"
                ],
                "driver_path": "/usr/bin/chromedriver"
            },
            EnvironmentType.CLOUD: {
                "arguments": [
                    "--headless=new",
                    "--no-sandbox",
                    "--disable-gpu",
                    "--disable-dev-shm-usage"
                ],
                "driver_path": None
            },
            EnvironmentType.CI_CD: {
                "arguments": [
                    "--headless=new",
                    "--no-sandbox",
                    "--disable-gpu",
                    "--disable-dev-shm-usage",
                    "--disable-extensions"
                ],
                "driver_path": None
            }
        }
        
        return settings_map.get(self.environment, settings_map[EnvironmentType.LOCAL])
    
    def get_available_presets(self) -> Dict[str, List[str]]:
        """Get list of available presets by browser type"""
        presets_by_browser = {}
        
        for (profile, browser_type), preset in self.presets.items():
            browser_name = browser_type.value
            if browser_name not in presets_by_browser:
                presets_by_browser[browser_name] = []
            presets_by_browser[browser_name].append({
                'profile': profile.value,
                'description': preset.description,
                'recommended_use': preset.recommended_use
            })
        
        return presets_by_browser
    
    def cleanup_temp_directories(self) -> None:
        """Cleanup temporary directories created during driver operations"""
        for temp_dir in self.temp_directories:
            try:
                shutil.rmtree(temp_dir, ignore_errors=True)
            except Exception as e:
                logger.warning(f"Failed to cleanup temp directory {temp_dir}: {str(e)}")
        
        self.temp_directories.clear()


# Factory functions for common use cases
def create_stealth_driver(environment: EnvironmentType = EnvironmentType.LOCAL) -> webdriver.Remote:
    """Create stealth-optimized Chrome driver"""
    factory = WebDriverFactory(environment)
    return factory.create_stealth_driver()


def create_performance_driver(environment: EnvironmentType = EnvironmentType.LOCAL) -> webdriver.Remote:
    """Create performance-optimized Chrome driver"""
    factory = WebDriverFactory(environment)
    return factory.create_performance_driver()


def create_mobile_driver(device_name: str = "iPhone 12", 
                        environment: EnvironmentType = EnvironmentType.LOCAL) -> webdriver.Remote:
    """Create mobile-emulation Chrome driver"""
    factory = WebDriverFactory(environment)
    return factory.create_mobile_driver(device_name)


def create_testing_driver(browser_type: BrowserType = BrowserType.CHROME,
                         environment: EnvironmentType = EnvironmentType.LOCAL) -> webdriver.Remote:
    """Create testing-optimized driver"""
    factory = WebDriverFactory(environment)
    return factory.create_testing_driver(browser_type)
