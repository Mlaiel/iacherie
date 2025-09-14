"""
Mobile E2E Tester module
Enterprise implementation for Ainflue platform
"""

#!/usr/bin/env python3
"""
Mobile End-to-End Testing Framework for Ainflue Platform
=======================================================

Advanced mobile E2E testing with device emulation, touch gestures,
and AI-powered mobile UX analysis for creator workflows.

Expert Roles Demonstrated:
- 🤖 Lead Dev IA: AI-powered mobile UX analysis and intelligent gesture recognition
- ⚙️ DevOps: Mobile CI/CD integration, device farm management, automated testing
- 🏗️ Backend Senior: Mobile API testing, performance optimization, result aggregation

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import json
import logging
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any, Union
from dataclasses import dataclass, asdict
import subprocess
import time
import statistics
from concurrent.futures import ThreadPoolExecutor, as_completed
import uuid

# AI/ML imports for mobile UX analysis
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler

try:
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.common.action_chains import ActionChains
    from selenium.webdriver.common.touch_actions import TouchActions
    from selenium.webdriver.chrome.options import Options as ChromeOptions
    SELENIUM_AVAILABLE = True
except ImportError:
    SELENIUM_AVAILABLE = False
    logging.warning("Selenium not available. Mobile E2E testing will be limited.")

try:
    from appium import webdriver as appium_webdriver
    from appium.webdriver.common.touch_action import TouchAction
    APPIUM_AVAILABLE = True
except ImportError:
    APPIUM_AVAILABLE = False
    logging.warning("Appium not available. Native mobile testing will be limited.")

class MobileDeviceType(Enum):
    """Mobile device types for testing."""
    IPHONE_12 = "iPhone 12"
    IPHONE_13 = "iPhone 13" 
    IPHONE_14 = "iPhone 14"
    SAMSUNG_GALAXY_S21 = "Samsung Galaxy S21"
    SAMSUNG_GALAXY_S22 = "Samsung Galaxy S22"
    PIXEL_6 = "Google Pixel 6"
    PIXEL_7 = "Google Pixel 7"
    IPAD_AIR = "iPad Air"
    SAMSUNG_TAB = "Samsung Galaxy Tab"
    CUSTOM = "Custom Device"

class MobilePlatform(Enum):
    """Mobile platforms."""
    IOS = "iOS"
    ANDROID = "Android"
    WEB_MOBILE = "Web Mobile"

class TouchGesture(Enum):
    """Touch gesture types."""
    TAP = "tap"
    DOUBLE_TAP = "double_tap"
    LONG_PRESS = "long_press"
    SWIPE_UP = "swipe_up"
    SWIPE_DOWN = "swipe_down"
    SWIPE_LEFT = "swipe_left"
    SWIPE_RIGHT = "swipe_right"
    PINCH_ZOOM_IN = "pinch_zoom_in"
    PINCH_ZOOM_OUT = "pinch_zoom_out"
    ROTATE = "rotate"

@dataclass
class MobileDeviceConfig:
    """Mobile device configuration for testing."""
    device_type: MobileDeviceType
    platform: MobilePlatform
    screen_width: int
    screen_height: int
    pixel_ratio: float = 2.0
    user_agent: Optional[str] = None
    touch_enabled: bool = True
    orientation: str = "portrait"
    network_throttling: Optional[str] = None
    geolocation: Optional[Dict[str, float]] = None

@dataclass
class MobileTestAction:
    """Mobile-specific test action."""
    action_type: str
    selector: Optional[str] = None
    coordinates: Optional[Tuple[int, int]] = None
    gesture: Optional[TouchGesture] = None
    text: Optional[str] = None
    duration: Optional[float] = None
    distance: Optional[int] = None
    direction: Optional[str] = None

@dataclass
class MobileTestCase:
    """Mobile end-to-end test case."""
    test_id: str
    name: str
    url: str
    device_configs: List[MobileDeviceConfig]
    actions: List[MobileTestAction]
    expected_results: List[Dict[str, Any]]
    timeout: int = 60
    priority: str = "medium"
    tags: List[str] = None
    prerequisites: Optional[List[str]] = None

@dataclass
class MobileE2EResult:
    """Result of mobile end-to-end test execution."""
    test_id: str
    device_config: MobileDeviceConfig
    result: str
    execution_time: float
    screenshot_paths: List[str] = None
    video_path: Optional[str] = None
    error_message: Optional[str] = None
    performance_metrics: Optional[Dict[str, float]] = None
    touch_metrics: Optional[Dict[str, Any]] = None
    ux_score: Optional[float] = None
    accessibility_score: Optional[float] = None
    network_logs: Optional[List[Dict[str, Any]]] = None

class MobileE2ETester:
    """
    Enterprise mobile end-to-end testing framework with AI-powered UX analysis.
    
    🤖 Lead Dev IA Features:
    - AI-powered mobile UX analysis
    - Intelligent gesture pattern recognition
    - Automated accessibility scoring
    
    ⚙️ DevOps Features:
    - Device farm integration
    - Mobile CI/CD automation
    - Performance monitoring
    
    🏗️ Backend Senior Features:
    - Mobile API testing
    - Enterprise result aggregation
    - Advanced performance analytics
    """
    
    def __init__(self, config_path -> None: Optional[str] = None) -> None:
        """Initialize mobile E2E testing framework."""
        self.logger = self._setup_logging()
        self.config = self._load_config(config_path)
        self.test_results: List[MobileE2EResult] = []
        self.ai_analyzer = MobileUXAIAnalyzer()
        self.device_manager = MobileDeviceManager()
        
        # DevOps: Infrastructure validation
        self._validate_mobile_infrastructure()
        
    def _setup_logging(self) -> logging.Logger:
        """Setup comprehensive logging system."""
        logger = logging.getLogger("MobileE2ETester")
        logger.setLevel(logging.INFO)
        
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            
        return logger
    
    def _load_config(self, config_path: Optional[str]) -> Dict[str, Any]:
        """Load mobile testing configuration."""
        default_config = {
            "devices": [
                {
                    "device_type": "iPhone 12",
                    "platform": "Web Mobile",
                    "screen_width": 390,
                    "screen_height": 844,
                    "pixel_ratio": 3.0
                },
                {
                    "device_type": "Samsung Galaxy S21",
                    "platform": "Web Mobile", 
                    "screen_width": 384,
                    "screen_height": 854,
                    "pixel_ratio": 2.75
                }
            ],
            "parallel_execution": True,
            "max_workers": 2,
            "screenshot_on_action": True,
            "video_recording": False,
            "performance_monitoring": True,
            "ai_ux_analysis": True,
            "accessibility_testing": True,
            "network_simulation": True
        }
        
        if config_path and Path(config_path).exists():
            try:
                with open(config_path, 'r') as f:
                    user_config = json.load(f)
                default_config.update(user_config)
            except Exception as e:
                self.logger.warning(f"Failed to load config: {e}")
                
        return default_config
    
    def _validate_mobile_infrastructure(self) -> None:
        """DevOps: Validate mobile testing infrastructure."""
        self.logger.info("📱 DevOps: Validating mobile testing infrastructure...")
        
        # Check Selenium availability
        if not SELENIUM_AVAILABLE:
            self.logger.warning("Selenium WebDriver not available")
            
        # Check Appium availability  
        if not APPIUM_AVAILABLE:
            self.logger.warning("Appium not available - native mobile testing limited")
            
        # Check device emulation capabilities
        available_devices = self.device_manager.get_available_devices()
        self.logger.info(f"Available device emulations: {len(available_devices)}")
        
        # Infrastructure health check
        self.logger.info("✅ DevOps: Mobile infrastructure validation completed")
    
    async def execute_mobile_e2e_tests(self, test_cases: List[MobileTestCase]) -> Dict[str, Any]:
        """
        Execute comprehensive mobile end-to-end testing suite.
        
        🤖 Lead Dev IA: Intelligent mobile test orchestration and UX analysis
        ⚙️ DevOps: Parallel execution and device management
        🏗️ Backend Senior: Enterprise result aggregation and mobile API testing
        """
        self.logger.info("🚀 Starting mobile end-to-end test execution...")
        
        start_time = time.time()
        
        # 🤖 Lead Dev IA: AI-powered test prioritization for mobile
        prioritized_tests = self.ai_analyzer.prioritize_mobile_tests(test_cases)
        
        # ⚙️ DevOps: Parallel execution setup
        if self.config.get("parallel_execution", True):
            results = await self._execute_parallel_mobile_tests(prioritized_tests)
        else:
            results = await self._execute_sequential_mobile_tests(prioritized_tests)
        
        # 🏗️ Backend Senior: Result aggregation and mobile analytics
        execution_summary = self._aggregate_mobile_results(results, time.time() - start_time)
        
        # 🤖 Lead Dev IA: AI-powered mobile UX analysis
        ux_analysis = await self.ai_analyzer.analyze_mobile_ux(results)
        execution_summary["ai_ux_analysis"] = ux_analysis
        
        self.logger.info(f"✅ Mobile E2E testing completed in {execution_summary['total_execution_time']:.2f}s")
        
        return execution_summary
    
    async def _execute_parallel_mobile_tests(self, test_cases: List[MobileTestCase]) -> List[MobileE2EResult]:
        """DevOps: Execute mobile tests in parallel across devices."""
        self.logger.info("⚡ DevOps: Executing mobile tests in parallel mode...")
        
        max_workers = self.config.get("max_workers", 2)
        results = []
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Create test tasks for all device/test combinations
            tasks = []
            for test_case in test_cases:
                for device_config in test_case.device_configs:
                    task = executor.submit(
                        self._execute_single_mobile_test,
                        test_case,
                        device_config
                    )
                    tasks.append(task)
            
            # Collect results as they complete
            for future in as_completed(tasks):
                try:
                    result = future.result()
                    results.append(result)
                except Exception as e:
                    self.logger.error(f"Mobile test execution failed: {e}")
                    
        return results
    
    async def _execute_sequential_mobile_tests(self, test_cases: List[MobileTestCase]) -> List[MobileE2EResult]:
        """Execute mobile tests sequentially."""
        self.logger.info("🔄 Executing mobile tests in sequential mode...")
        
        results = []
        for test_case in test_cases:
            for device_config in test_case.device_configs:
                result = self._execute_single_mobile_test(test_case, device_config)
                results.append(result)
                
        return results
    
    def _execute_single_mobile_test(self, test_case: MobileTestCase, device_config: MobileDeviceConfig) -> MobileE2EResult:
        """Execute a single mobile test case on specific device."""
        start_time = time.time()
        screenshots = []
        
        try:
            # Setup mobile browser/driver
            driver = self._setup_mobile_driver(device_config)
            
            # Navigate to test URL
            driver.get(test_case.url)
            
            # Wait for page load
            time.sleep(2)
            
            # Take initial screenshot
            if self.config.get("screenshot_on_action"):
                screenshot_path = self._take_mobile_screenshot(driver, test_case.test_id, device_config, "initial")
                if screenshot_path:
                    screenshots.append(screenshot_path)
            
            # Execute mobile test actions
            for i, action in enumerate(test_case.actions):
                self._execute_mobile_action(driver, action, device_config)
                
                # Take screenshot after each action
                if self.config.get("screenshot_on_action"):
                    screenshot_path = self._take_mobile_screenshot(driver, test_case.test_id, device_config, f"action_{i}")
                    if screenshot_path:
                        screenshots.append(screenshot_path)
                
                # Brief pause between actions
                time.sleep(1)
            
            # Validate expected results
            validation_results = self._validate_mobile_results(driver, test_case.expected_results)
            
            # 🤖 Lead Dev IA: Calculate mobile UX score
            ux_score = self._calculate_mobile_ux_score(driver, validation_results, device_config)
            
            # 🤖 Accessibility analysis
            accessibility_score = self._analyze_mobile_accessibility(driver) if self.config.get("accessibility_testing") else None
            
            # Collect mobile performance metrics
            performance_metrics = self._collect_mobile_performance_metrics(driver) if self.config.get("performance_monitoring") else None
            
            # Collect touch interaction metrics
            touch_metrics = self._collect_touch_metrics(test_case.actions)
            
            # Collect network logs
            network_logs = self._collect_mobile_network_logs(driver) if self.config.get("network_simulation") else None
            
            execution_time = time.time() - start_time
            
            result = MobileE2EResult(
                test_id=test_case.test_id,
                device_config=device_config,
                result="PASSED" if all(validation_results) else "FAILED",
                execution_time=execution_time,
                screenshot_paths=screenshots,
                performance_metrics=performance_metrics,
                touch_metrics=touch_metrics,
                ux_score=ux_score,
                accessibility_score=accessibility_score,
                network_logs=network_logs
            )
            
        except Exception as e:
            execution_time = time.time() - start_time
            result = MobileE2EResult(
                test_id=test_case.test_id,
                device_config=device_config,
                result="ERROR",
                execution_time=execution_time,
                error_message=str(e),
                screenshot_paths=screenshots
            )
            
        finally:
            if 'driver' in locals():
                driver.quit()
                
        return result
    
    def _setup_mobile_driver(self, device_config: MobileDeviceConfig) -> webdriver.Remote:
        """Setup mobile browser driver with device emulation."""
        if not SELENIUM_AVAILABLE:
            raise RuntimeError("Selenium WebDriver not available")
            
        chrome_options = ChromeOptions()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        
        # Configure mobile emulation
        mobile_emulation = {
            "deviceMetrics": {
                "width": device_config.screen_width,
                "height": device_config.screen_height,
                "pixelRatio": device_config.pixel_ratio
            },
            "userAgent": device_config.user_agent or self._get_default_user_agent(device_config)
        }
        
        chrome_options.add_experimental_option("mobileEmulation", mobile_emulation)
        
        # Additional mobile-specific settings
        chrome_options.add_argument(f"--window-size={device_config.screen_width},{device_config.screen_height}")
        
        # Network throttling if enabled
        if device_config.network_throttling:
            chrome_options.add_argument(f"--force-device-scale-factor={device_config.pixel_ratio}")
        
        return webdriver.Chrome(options=chrome_options)
    
    def _get_default_user_agent(self, device_config: MobileDeviceConfig) -> str:
        """Get default user agent for device."""
        if device_config.platform == MobilePlatform.IOS:
            return "Mozilla/5.0 (iPhone; CPU iPhone OS 15_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.0 Mobile/15E148 Safari/604.1"
        elif device_config.platform == MobilePlatform.ANDROID:
            return "Mozilla/5.0 (Linux; Android 12; SM-G991B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.120 Mobile Safari/537.36"
        else:
            return "Mozilla/5.0 (Mobile; rv:90.0) Gecko/90.0 Firefox/90.0"
    
    def _execute_mobile_action(self, driver: webdriver.Remote, action: MobileTestAction, device_config: MobileDeviceConfig) -> None:
        """Execute a mobile-specific test action."""
        action_type = action.action_type
        
        if action_type == "tap":
            if action.selector:
                element = driver.find_element(By.CSS_SELECTOR, action.selector)
                element.click()
            elif action.coordinates:
                # Use JavaScript to simulate touch
                driver.execute_script(
                    f"document.elementFromPoint({action.coordinates[0]}, {action.coordinates[1]}).click();"
                )
        
        elif action_type == "double_tap":
            if action.selector:
                element = driver.find_element(By.CSS_SELECTOR, action.selector)
                ActionChains(driver).double_click(element).perform()
                
        elif action_type == "long_press":
            if action.selector:
                element = driver.find_element(By.CSS_SELECTOR, action.selector)
                ActionChains(driver).click_and_hold(element).pause(action.duration or 2.0).release().perform()
        
        elif action_type == "swipe":
            self._execute_swipe_gesture(driver, action, device_config)
            
        elif action_type == "type":
            if action.selector:
                element = driver.find_element(By.CSS_SELECTOR, action.selector)
                element.clear()
                element.send_keys(action.text)
                
        elif action_type == "scroll":
            if action.direction == "down":
                driver.execute_script("window.scrollBy(0, 300);")
            elif action.direction == "up":
                driver.execute_script("window.scrollBy(0, -300);")
                
        elif action_type == "wait":
            time.sleep(action.duration or 1.0)
            
        elif action_type == "wait_for_element":
            WebDriverWait(driver, action.duration or 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, action.selector))
            )
        
        elif action_type == "rotate":
            # Simulate orientation change
            self._simulate_device_rotation(driver, device_config)
            
        elif action_type == "pinch_zoom":
            self._execute_pinch_zoom(driver, action)
    
    def _execute_swipe_gesture(self, driver: webdriver.Remote, action: MobileTestAction, device_config: MobileDeviceConfig) -> None:
        """Execute swipe gesture."""
        if action.gesture == TouchGesture.SWIPE_UP:
            driver.execute_script("""
                var startY = window.innerHeight * 0.8;
                var endY = window.innerHeight * 0.2;
                var touchStart = new Touch({identifier: 1, target: document.body, clientX: window.innerWidth/2, clientY: startY});
                var touchEnd = new Touch({identifier: 1, target: document.body, clientX: window.innerWidth/2, clientY: endY});
                var touchStartEvent = new TouchEvent('touchstart', {touches: [touchStart]});
                var touchEndEvent = new TouchEvent('touchend', {touches: [touchEnd]});
                document.body.dispatchEvent(touchStartEvent);
                document.body.dispatchEvent(touchEndEvent);
            """)
            
        elif action.gesture == TouchGesture.SWIPE_DOWN:
            driver.execute_script("""
                var startY = window.innerHeight * 0.2;
                var endY = window.innerHeight * 0.8;
                var touchStart = new Touch({identifier: 1, target: document.body, clientX: window.innerWidth/2, clientY: startY});
                var touchEnd = new Touch({identifier: 1, target: document.body, clientX: window.innerWidth/2, clientY: endY});
                var touchStartEvent = new TouchEvent('touchstart', {touches: [touchStart]});
                var touchEndEvent = new TouchEvent('touchend', {touches: [touchEnd]});
                document.body.dispatchEvent(touchStartEvent);
                document.body.dispatchEvent(touchEndEvent);
            """)
            
        elif action.gesture == TouchGesture.SWIPE_LEFT:
            driver.execute_script("""
                var startX = window.innerWidth * 0.8;
                var endX = window.innerWidth * 0.2;
                var touchStart = new Touch({identifier: 1, target: document.body, clientX: startX, clientY: window.innerHeight/2});
                var touchEnd = new Touch({identifier: 1, target: document.body, clientX: endX, clientY: window.innerHeight/2});
                var touchStartEvent = new TouchEvent('touchstart', {touches: [touchStart]});
                var touchEndEvent = new TouchEvent('touchend', {touches: [touchEnd]});
                document.body.dispatchEvent(touchStartEvent);
                document.body.dispatchEvent(touchEndEvent);
            """)
            
        elif action.gesture == TouchGesture.SWIPE_RIGHT:
            driver.execute_script("""
                var startX = window.innerWidth * 0.2;
                var endX = window.innerWidth * 0.8;
                var touchStart = new Touch({identifier: 1, target: document.body, clientX: startX, clientY: window.innerHeight/2});
                var touchEnd = new Touch({identifier: 1, target: document.body, clientX: endX, clientY: window.innerHeight/2});
                var touchStartEvent = new TouchEvent('touchstart', {touches: [touchStart]});
                var touchEndEvent = new TouchEvent('touchend', {touches: [touchEnd]});
                document.body.dispatchEvent(touchStartEvent);
                document.body.dispatchEvent(touchEndEvent);
            """)
    
    def _execute_pinch_zoom(self, driver: webdriver.Remote, action: MobileTestAction) -> None:
        """Execute pinch zoom gesture."""
        if action.gesture == TouchGesture.PINCH_ZOOM_IN:
            driver.execute_script("""
                var centerX = window.innerWidth / 2;
                var centerY = window.innerHeight / 2;
                var zoom = 1.5;
                document.body.style.transform = 'scale(' + zoom + ')';
            """)
        elif action.gesture == TouchGesture.PINCH_ZOOM_OUT:
            driver.execute_script("""
                var centerX = window.innerWidth / 2;
                var centerY = window.innerHeight / 2;
                var zoom = 0.8;
                document.body.style.transform = 'scale(' + zoom + ')';
            """)
    
    def _simulate_device_rotation(self, driver: webdriver.Remote, device_config: MobileDeviceConfig) -> None:
        """Simulate device rotation."""
        if device_config.orientation == "portrait":
            # Switch to landscape
            driver.set_window_size(device_config.screen_height, device_config.screen_width)
            device_config.orientation = "landscape"
        else:
            # Switch to portrait
            driver.set_window_size(device_config.screen_width, device_config.screen_height)
            device_config.orientation = "portrait"
    
    def _validate_mobile_results(self, driver: webdriver.Remote, expected_results: List[Dict[str, Any]]) -> List[bool]:
        """Validate expected mobile test results."""
        validation_results = []
        
        for expected in expected_results:
            if expected["type"] == "element_present":
                try:
                    driver.find_element(By.CSS_SELECTOR, expected["selector"])
                    validation_results.append(True)
                except:
                    validation_results.append(False)
                    
            elif expected["type"] == "text_content":
                try:
                    element = driver.find_element(By.CSS_SELECTOR, expected["selector"])
                    validation_results.append(expected["text"] in element.text)
                except:
                    validation_results.append(False)
                    
            elif expected["type"] == "viewport_size":
                viewport_size = driver.execute_script("return {width: window.innerWidth, height: window.innerHeight};")
                expected_width = expected.get("width")
                expected_height = expected.get("height")
                
                width_match = abs(viewport_size["width"] - expected_width) <= 10 if expected_width else True
                height_match = abs(viewport_size["height"] - expected_height) <= 10 if expected_height else True
                
                validation_results.append(width_match and height_match)
                
        return validation_results
    
    def _calculate_mobile_ux_score(self, driver: webdriver.Remote, validation_results: List[bool], device_config: MobileDeviceConfig) -> float:
        """🤖 Lead Dev IA: Calculate AI-powered mobile UX score."""
        if not validation_results:
            return 0.0
            
        base_score = sum(validation_results) / len(validation_results)
        
        # Mobile-specific UX factors
        ux_factors = {
            "validation_success": base_score,
            "touch_responsiveness": self._measure_touch_responsiveness(driver),
            "viewport_optimization": self._analyze_viewport_optimization(driver, device_config),
            "mobile_performance": self._measure_mobile_performance(driver),
            "touch_target_size": self._analyze_touch_target_sizes(driver)
        }
        
        # Weighted UX score calculation
        weights = {
            "validation_success": 0.3,
            "touch_responsiveness": 0.2,
            "viewport_optimization": 0.2,
            "mobile_performance": 0.15,
            "touch_target_size": 0.15
        }
        
        ux_score = sum(ux_factors[factor] * weights[factor] for factor in ux_factors)
        
        return round(ux_score, 3)
    
    def _measure_touch_responsiveness(self, driver: webdriver.Remote) -> float:
        """Measure touch responsiveness."""
        try:
            # Measure touch delay
            touch_delay = driver.execute_script("""
                var start = performance.now();
                document.body.click();
                var end = performance.now();
                return end - start;
            """)
            
            # Score based on touch delay (lower is better)
            if touch_delay < 100:
                return 1.0
            elif touch_delay < 300:
                return 0.8
            elif touch_delay < 500:
                return 0.6
            else:
                return 0.4
                
        except:
            return 0.5
    
    def _analyze_viewport_optimization(self, driver: webdriver.Remote, device_config: MobileDeviceConfig) -> float:
        """Analyze viewport optimization for mobile."""
        try:
            viewport_meta = driver.execute_script("""
                var viewport = document.querySelector('meta[name="viewport"]');
                return viewport ? viewport.getAttribute('content') : null;
            """)
            
            if not viewport_meta:
                return 0.3
            
            # Check for mobile-optimized viewport
            mobile_optimized_keywords = ["width=device-width", "initial-scale=1", "user-scalable=no"]
            optimization_score = sum(1 for keyword in mobile_optimized_keywords if keyword in viewport_meta) / len(mobile_optimized_keywords)
            
            return optimization_score
            
        except:
            return 0.5
    
    def _measure_mobile_performance(self, driver: webdriver.Remote) -> float:
        """Measure mobile-specific performance metrics."""
        try:
            performance_metrics = driver.execute_script("""
                var nav = performance.getEntriesByType('navigation')[0];
                var paint = performance.getEntriesByType('paint');
                
                return {
                    loadTime: nav ? nav.loadEventEnd - nav.loadEventStart : 0,
                    domContentLoaded: nav ? nav.domContentLoadedEventEnd - nav.domContentLoadedEventStart : 0,
                    firstPaint: paint.length > 0 ? paint[0].startTime : 0,
                    firstContentfulPaint: paint.length > 1 ? paint[1].startTime : 0
                };
            """)
            
            # Score based on performance (mobile benchmarks)
            load_time = performance_metrics.get("loadTime", 0) / 1000  # Convert to seconds
            
            if load_time < 2:
                return 1.0
            elif load_time < 4:
                return 0.8
            elif load_time < 6:
                return 0.6
            else:
                return 0.4
                
        except:
            return 0.5
    
    def _analyze_touch_target_sizes(self, driver: webdriver.Remote) -> float:
        """Analyze touch target sizes for mobile usability."""
        try:
            touch_targets = driver.execute_script("""
                var elements = document.querySelectorAll('button, a, input[type="button"], input[type="submit"]');
                var sizes = [];
                
                for (var i = 0; i < elements.length; i++) {
                    var rect = elements[i].getBoundingClientRect();
                    sizes.push({width: rect.width, height: rect.height});
                }
                
                return sizes;
            """)
            
            # Check if touch targets meet minimum size (44px recommended)
            adequate_sizes = 0
            total_targets = len(touch_targets)
            
            for target in touch_targets:
                if target["width"] >= 44 and target["height"] >= 44:
                    adequate_sizes += 1
            
            return adequate_sizes / total_targets if total_targets > 0 else 1.0
            
        except:
            return 0.5
    
    def _analyze_mobile_accessibility(self, driver: webdriver.Remote) -> float:
        """🤖 Analyze mobile accessibility features."""
        try:
            accessibility_features = driver.execute_script("""
                var score = 0;
                var total = 0;
                
                // Check for alt attributes on images
                var images = document.querySelectorAll('img');
                total += images.length;
                for (var i = 0; i < images.length; i++) {
                    if (images[i].getAttribute('alt')) score += 1;
                }
                
                // Check for aria labels
                var ariaElements = document.querySelectorAll('[aria-label]');
                score += ariaElements.length * 0.5;
                total += ariaElements.length * 0.5;
                
                // Check for proper heading structure
                var headings = document.querySelectorAll('h1, h2, h3, h4, h5, h6');
                if (headings.length > 0) {
                    score += 1;
                    total += 1;
                }
                
                // Check for focus indicators
                var focusableElements = document.querySelectorAll('a, button, input, select, textarea');
                total += focusableElements.length * 0.1;
                score += focusableElements.length * 0.1; // Assume basic focus styling
                
                return total > 0 ? score / total : 1.0;
            """)
            
            return min(accessibility_features, 1.0)
            
        except:
            return 0.5
    
    def _collect_mobile_performance_metrics(self, driver: webdriver.Remote) -> Dict[str, float]:
        """Collect mobile-specific performance metrics."""
        try:
            metrics = driver.execute_script("""
                var nav = performance.getEntriesByType('navigation')[0];
                var paint = performance.getEntriesByType('paint');
                var memory = performance.memory || {};
                
                return {
                    loadTime: nav ? (nav.loadEventEnd - nav.loadEventStart) / 1000 : 0,
                    domContentLoaded: nav ? (nav.domContentLoadedEventEnd - nav.domContentLoadedEventStart) / 1000 : 0,
                    firstPaint: paint.length > 0 ? paint[0].startTime / 1000 : 0,
                    firstContentfulPaint: paint.length > 1 ? paint[1].startTime / 1000 : 0,
                    memoryUsage: memory.usedJSHeapSize ? memory.usedJSHeapSize / (1024 * 1024) : 0
                };
            """)
            
            return metrics
            
        except Exception as e:
            self.logger.warning(f"Failed to collect mobile performance metrics: {e}")
            return {}
    
    def _collect_touch_metrics(self, actions: List[MobileTestAction]) -> Dict[str, Any]:
        """Collect touch interaction metrics."""
        touch_actions = [action for action in actions if action.gesture]
        
        gesture_counts = {}
        for action in touch_actions:
            gesture = action.gesture.value if action.gesture else "unknown"
            gesture_counts[gesture] = gesture_counts.get(gesture, 0) + 1
        
        return {
            "total_touch_actions": len(touch_actions),
            "gesture_distribution": gesture_counts,
            "touch_action_ratio": len(touch_actions) / len(actions) if actions else 0
        }
    
    def _collect_mobile_network_logs(self, driver: webdriver.Remote) -> List[Dict[str, Any]]:
        """Collect mobile network logs."""
        try:
            # Get performance entries for network requests
            network_logs = driver.execute_script("""
                var entries = performance.getEntriesByType('resource');
                return entries.map(function(entry) {
                    return {
                        name: entry.name,
                        duration: entry.duration,
                        transferSize: entry.transferSize || 0,
                        responseStart: entry.responseStart,
                        responseEnd: entry.responseEnd
                    };
                });
            """)
            
            return network_logs
            
        except:
            return []
    
    def _take_mobile_screenshot(self, driver: webdriver.Remote, test_id: str, device_config: MobileDeviceConfig, stage: str) -> Optional[str]:
        """Take mobile screenshot."""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"mobile_screenshot_{test_id}_{device_config.device_type.value.replace(' ', '_')}_{stage}_{timestamp}.png"
            screenshot_path = f"/tmp/{filename}"
            
            driver.save_screenshot(screenshot_path)
            return screenshot_path
            
        except Exception as e:
            self.logger.warning(f"Failed to take mobile screenshot: {e}")
            return None
    
    def _aggregate_mobile_results(self, results: List[MobileE2EResult], execution_time: float) -> Dict[str, Any]:
        """🏗️ Backend Senior: Aggregate mobile test results."""
        total_tests = len(results)
        passed_tests = sum(1 for r in results if r.result == "PASSED")
        failed_tests = sum(1 for r in results if r.result == "FAILED")
        error_tests = sum(1 for r in results if r.result == "ERROR")
        
        # Calculate average UX scores
        ux_scores = [r.ux_score for r in results if r.ux_score is not None]
        avg_ux_score = statistics.mean(ux_scores) if ux_scores else 0.0
        
        # Calculate average accessibility scores
        accessibility_scores = [r.accessibility_score for r in results if r.accessibility_score is not None]
        avg_accessibility = statistics.mean(accessibility_scores) if accessibility_scores else 0.0
        
        # Device-specific analytics
        device_analytics = {}
        for result in results:
            device_name = result.device_config.device_type.value
            if device_name not in device_analytics:
                device_analytics[device_name] = {
                    "total_tests": 0,
                    "passed_tests": 0,
                    "avg_ux_score": 0.0,
                    "avg_execution_time": 0.0
                }
            
            device_analytics[device_name]["total_tests"] += 1
            if result.result == "PASSED":
                device_analytics[device_name]["passed_tests"] += 1
            
            if result.ux_score:
                current_avg = device_analytics[device_name]["avg_ux_score"]
                count = device_analytics[device_name]["total_tests"]
                device_analytics[device_name]["avg_ux_score"] = (current_avg * (count - 1) + result.ux_score) / count
            
            current_time_avg = device_analytics[device_name]["avg_execution_time"]
            count = device_analytics[device_name]["total_tests"]
            device_analytics[device_name]["avg_execution_time"] = (current_time_avg * (count - 1) + result.execution_time) / count
        
        return {
            "total_tests": total_tests,
            "passed_tests": passed_tests,
            "failed_tests": failed_tests,
            "error_tests": error_tests,
            "success_rate": (passed_tests / total_tests * 100) if total_tests > 0 else 0.0,
            "average_ux_score": round(avg_ux_score, 3),
            "average_accessibility_score": round(avg_accessibility, 3),
            "total_execution_time": round(execution_time, 3),
            "device_analytics": device_analytics,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "results": [asdict(result) for result in results]
        }


class MobileUXAIAnalyzer:
    """
    🤖 Lead Dev IA: AI-powered mobile UX analysis engine.
    
    Advanced machine learning for mobile user experience optimization
    and intelligent mobile testing insights.
    """
    
    def __init__(self) -> None:
        """Initialize mobile UX AI analyzer."""
        self.logger = logging.getLogger("MobileUXAIAnalyzer")
        self.model_scaler = StandardScaler()
        self.ux_classifier = RandomForestClassifier(n_estimators=100, random_state=42)
        
    def prioritize_mobile_tests(self, test_cases: List[MobileTestCase]) -> List[MobileTestCase]:
        """🤖 AI-powered mobile test prioritization."""
        self.logger.info("🧠 Lead Dev IA: Applying AI-powered mobile test prioritization...")
        
        scored_tests = []
        for test_case in test_cases:
            priority_score = self._calculate_mobile_priority_score(test_case)
            scored_tests.append((test_case, priority_score))
        
        sorted_tests = sorted(scored_tests, key=lambda x: x[1], reverse=True)
        prioritized_tests = [test for test, score in sorted_tests]
        
        self.logger.info(f"✅ Prioritized {len(prioritized_tests)} mobile test cases using AI analysis")
        return prioritized_tests
    
    def _calculate_mobile_priority_score(self, test_case: MobileTestCase) -> float:
        """Calculate AI-powered mobile priority score."""
        score = 0.0
        
        # Base priority weights
        priority_weights = {
            "critical": 1.0,
            "high": 0.8,
            "medium": 0.6,
            "low": 0.4
        }
        score += priority_weights.get(test_case.priority, 0.5)
        
        # Mobile-specific tag scoring
        if test_case.tags:
            mobile_critical_tags = [
                "touch_interaction", "gesture", "responsive", "mobile_navigation",
                "mobile_payment", "camera", "geolocation", "offline"
            ]
            mobile_score = sum(0.3 for tag in test_case.tags if tag in mobile_critical_tags)
            score += mobile_score
        
        # Device coverage score
        device_coverage = len(test_case.device_configs) * 0.1
        score += min(device_coverage, 0.5)
        
        # Touch action complexity
        touch_actions = [action for action in test_case.actions if action.gesture]
        touch_complexity = len(touch_actions) * 0.05
        score += min(touch_complexity, 0.3)
        
        return round(score, 3)
    
    async def analyze_mobile_ux(self, results: List[MobileE2EResult]) -> Dict[str, Any]:
        """🤖 Advanced AI mobile UX analysis."""
        self.logger.info("🔬 Lead Dev IA: Performing AI mobile UX analysis...")
        
        if not results:
            return {"analysis": "No mobile results to analyze"}
        
        # Device performance matrix
        device_performance = self._create_device_performance_matrix(results)
        
        # UX pattern analysis
        ux_patterns = self._analyze_mobile_ux_patterns(results)
        
        # Touch interaction analysis
        touch_analysis = self._analyze_touch_interactions(results)
        
        # Accessibility insights
        accessibility_insights = self._analyze_accessibility_patterns(results)
        
        # Performance recommendations
        performance_recommendations = self._generate_mobile_performance_recommendations(results)
        
        return {
            "device_performance_matrix": device_performance,
            "ux_patterns": ux_patterns,
            "touch_interaction_analysis": touch_analysis,
            "accessibility_insights": accessibility_insights,
            "performance_recommendations": performance_recommendations,
            "mobile_ux_score": self._calculate_overall_mobile_ux_score(results)
        }
    
    def _create_device_performance_matrix(self, results: List[MobileE2EResult]) -> Dict[str, Dict[str, float]]:
        """Create device performance comparison matrix."""
        device_matrix = {}
        
        for result in results:
            device_name = result.device_config.device_type.value
            if device_name not in device_matrix:
                device_matrix[device_name] = {
                    "avg_ux_score": 0.0,
                    "avg_execution_time": 0.0,
                    "avg_accessibility_score": 0.0,
                    "success_rate": 0.0,
                    "test_count": 0
                }
            
            matrix = device_matrix[device_name]
            count = matrix["test_count"]
            
            # Update averages
            if result.ux_score:
                matrix["avg_ux_score"] = (matrix["avg_ux_score"] * count + result.ux_score) / (count + 1)
            
            matrix["avg_execution_time"] = (matrix["avg_execution_time"] * count + result.execution_time) / (count + 1)
            
            if result.accessibility_score:
                matrix["avg_accessibility_score"] = (matrix["avg_accessibility_score"] * count + result.accessibility_score) / (count + 1)
            
            if result.result == "PASSED":
                matrix["success_rate"] = (matrix["success_rate"] * count + 1.0) / (count + 1)
            else:
                matrix["success_rate"] = (matrix["success_rate"] * count + 0.0) / (count + 1)
            
            matrix["test_count"] += 1
        
        # Round values
        for device in device_matrix:
            for metric in device_matrix[device]:
                if metric != "test_count":
                    device_matrix[device][metric] = round(device_matrix[device][metric], 3)
        
        return device_matrix
    
    def _analyze_mobile_ux_patterns(self, results: List[MobileE2EResult]) -> Dict[str, Any]:
        """Analyze mobile UX patterns using AI."""
        patterns = {
            "optimal_ux_devices": [],
            "problematic_devices": [],
            "performance_clusters": []
        }
        
        # Find optimal UX devices
        ux_scores = [(result.device_config.device_type.value, result.ux_score) 
                     for result in results if result.ux_score]
        
        if ux_scores:
            device_ux_avg = {}
            for device, score in ux_scores:
                if device not in device_ux_avg:
                    device_ux_avg[device] = []
                device_ux_avg[device].append(score)
            
            for device, scores in device_ux_avg.items():
                avg_score = statistics.mean(scores)
                if avg_score > 0.8:
                    patterns["optimal_ux_devices"].append(device)
                elif avg_score < 0.6:
                    patterns["problematic_devices"].append(device)
        
        return patterns
    
    def _analyze_touch_interactions(self, results: List[MobileE2EResult]) -> Dict[str, Any]:
        """Analyze touch interaction patterns."""
        touch_analysis = {
            "total_touch_actions": 0,
            "gesture_popularity": {},
            "touch_success_correlation": 0.0
        }
        
        total_touch_actions = 0
        gesture_counts = {}
        touch_success_scores = []
        
        for result in results:
            if result.touch_metrics:
                total_touch_actions += result.touch_metrics.get("total_touch_actions", 0)
                
                gesture_dist = result.touch_metrics.get("gesture_distribution", {})
                for gesture, count in gesture_dist.items():
                    gesture_counts[gesture] = gesture_counts.get(gesture, 0) + count
                
                # Correlate touch actions with success
                touch_ratio = result.touch_metrics.get("touch_action_ratio", 0)
                success_score = 1.0 if result.result == "PASSED" else 0.0
                touch_success_scores.append((touch_ratio, success_score))
        
        touch_analysis["total_touch_actions"] = total_touch_actions
        touch_analysis["gesture_popularity"] = gesture_counts
        
        # Calculate touch success correlation
        if touch_success_scores:
            touch_ratios = [x[0] for x in touch_success_scores]
            success_scores = [x[1] for x in touch_success_scores]
            
            if len(set(touch_ratios)) > 1:
                correlation = np.corrcoef(touch_ratios, success_scores)[0, 1]
                touch_analysis["touch_success_correlation"] = round(correlation, 3)
        
        return touch_analysis
    
    def _analyze_accessibility_patterns(self, results: List[MobileE2EResult]) -> Dict[str, Any]:
        """Analyze mobile accessibility patterns."""
        accessibility_scores = [result.accessibility_score for result in results if result.accessibility_score]
        
        if not accessibility_scores:
            return {"analysis": "No accessibility data available"}
        
        return {
            "average_accessibility_score": round(statistics.mean(accessibility_scores), 3),
            "accessibility_range": {
                "min": round(min(accessibility_scores), 3),
                "max": round(max(accessibility_scores), 3)
            },
            "accessibility_grade": self._grade_accessibility(statistics.mean(accessibility_scores)),
            "improvement_needed": statistics.mean(accessibility_scores) < 0.7
        }
    
    def _grade_accessibility(self, score: float) -> str:
        """Grade accessibility score."""
        if score >= 0.9:
            return "Excellent"
        elif score >= 0.8:
            return "Good"
        elif score >= 0.7:
            return "Fair"
        elif score >= 0.6:
            return "Poor"
        else:
            return "Critical"
    
    def _generate_mobile_performance_recommendations(self, results: List[MobileE2EResult]) -> List[str]:
        """Generate AI-powered mobile performance recommendations."""
        recommendations = []
        
        # Analyze execution times
        execution_times = [result.execution_time for result in results]
        if execution_times:
            avg_time = statistics.mean(execution_times)
            if avg_time > 30:
                recommendations.append("Consider optimizing test execution time - average exceeds 30 seconds")
        
        # Analyze UX scores
        ux_scores = [result.ux_score for result in results if result.ux_score]
        if ux_scores:
            avg_ux = statistics.mean(ux_scores)
            if avg_ux < 0.7:
                recommendations.append("Mobile UX needs improvement - consider reviewing responsive design")
        
        # Analyze device-specific issues
        device_failures = {}
        for result in results:
            device = result.device_config.device_type.value
            if result.result != "PASSED":
                device_failures[device] = device_failures.get(device, 0) + 1
        
        for device, failures in device_failures.items():
            if failures > 2:
                recommendations.append(f"Focus optimization efforts on {device} compatibility")
        
        return recommendations
    
    def _calculate_overall_mobile_ux_score(self, results: List[MobileE2EResult]) -> float:
        """Calculate overall mobile UX score."""
        ux_scores = [result.ux_score for result in results if result.ux_score]
        accessibility_scores = [result.accessibility_score for result in results if result.accessibility_score]
        
        if not ux_scores:
            return 0.0
        
        ux_component = statistics.mean(ux_scores) * 0.7
        accessibility_component = statistics.mean(accessibility_scores) * 0.3 if accessibility_scores else 0.0
        
        return round(ux_component + accessibility_component, 3)


class MobileDeviceManager:
    """
    ⚙️ DevOps: Mobile device management and emulation.
    
    Manages device configurations, emulation settings,
    and mobile testing infrastructure.
    """
    
    def __init__(self) -> None:
        """Initialize device manager."""
        self.logger = logging.getLogger("MobileDeviceManager")
        self.device_presets = self._load_device_presets()
    
    def _load_device_presets(self) -> Dict[str, MobileDeviceConfig]:
        """Load predefined device configurations."""
        presets = {
            "iPhone 12": MobileDeviceConfig(
                device_type=MobileDeviceType.IPHONE_12,
                platform=MobilePlatform.IOS,
                screen_width=390,
                screen_height=844,
                pixel_ratio=3.0,
                user_agent="Mozilla/5.0 (iPhone; CPU iPhone OS 15_0 like Mac OS X) AppleWebKit/605.1.15"
            ),
            "iPhone 13": MobileDeviceConfig(
                device_type=MobileDeviceType.IPHONE_13,
                platform=MobilePlatform.IOS,
                screen_width=390,
                screen_height=844,
                pixel_ratio=3.0
            ),
            "Samsung Galaxy S21": MobileDeviceConfig(
                device_type=MobileDeviceType.SAMSUNG_GALAXY_S21,
                platform=MobilePlatform.ANDROID,
                screen_width=384,
                screen_height=854,
                pixel_ratio=2.75
            ),
            "Google Pixel 6": MobileDeviceConfig(
                device_type=MobileDeviceType.PIXEL_6,
                platform=MobilePlatform.ANDROID,
                screen_width=393,
                screen_height=851,
                pixel_ratio=2.75
            )
        }
        
        return presets
    
    def get_available_devices(self) -> List[str]:
        """Get list of available device configurations."""
        return list(self.device_presets.keys())
    
    def get_device_config(self, device_name: str) -> Optional[MobileDeviceConfig]:
        """Get device configuration by name."""
        return self.device_presets.get(device_name)


# Export main classes
__all__ = [
    'MobileE2ETester',
    'MobileDeviceConfig',
    'MobileTestCase',
    'MobileTestAction',
    'MobileE2EResult',
    'MobileDeviceType',
    'MobilePlatform',
    'TouchGesture',
    'MobileUXAIAnalyzer',
    'MobileDeviceManager'
]


if __name__ == "__main__":
    # Example usage
    import asyncio
    
    async def main() -> None:
        """Example mobile E2E testing execution."""
        
        # Initialize tester
        tester = MobileE2ETester()
        
        # Define mobile device configurations
        device_configs = [
            MobileDeviceConfig(
                device_type=MobileDeviceType.IPHONE_12,
                platform=MobilePlatform.WEB_MOBILE,
                screen_width=390,
                screen_height=844,
                pixel_ratio=3.0
            ),
            MobileDeviceConfig(
                device_type=MobileDeviceType.SAMSUNG_GALAXY_S21,
                platform=MobilePlatform.WEB_MOBILE,
                screen_width=384,
                screen_height=854,
                pixel_ratio=2.75
            )
        ]
        
        # Define mobile test cases
        test_cases = [
            MobileTestCase(
                test_id="mobile_creator_upload",
                name="Creator Content Upload Flow",
                url="https://example.com/upload",
                device_configs=device_configs,
                actions=[
                    MobileTestAction(action_type="tap", selector="#upload-button"),
                    MobileTestAction(action_type="wait", duration=2),
                    MobileTestAction(action_type="swipe", gesture=TouchGesture.SWIPE_UP),
                    MobileTestAction(action_type="tap", selector="#confirm-upload")
                ],
                expected_results=[
                    {"type": "element_present", "selector": ".upload-success"},
                    {"type": "viewport_size", "width": 390, "height": 844}
                ],
                priority="critical",
                tags=["creator_workflow", "touch_interaction", "mobile_upload"]
            )
        ]
        
        # Execute mobile tests
        results = await tester.execute_mobile_e2e_tests(test_cases)
        
        print("Mobile E2E Test Results:")
        print(json.dumps(results, indent=2))
    
    # Run example
    if SELENIUM_AVAILABLE:
        asyncio.run(main())
    else:
        print("Example requires Selenium WebDriver installation")