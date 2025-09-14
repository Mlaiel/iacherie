"""
User Journey Tester module
Enterprise implementation for Ainflue platform
"""

#!/usr/bin/env python3
"""
User Journey Tester - Ainflue Quality Platform
==============================================

End-to-end user journey testing framework for complete workflow validation.
Demonstrates ML Engineer + DevOps + Lead Dev IA expertise.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
import json
import time
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Tuple, Union
from datetime import datetime, timedelta
from pathlib import Path
from enum import Enum
import yaml
import aiohttp
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import pandas as pd

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class JourneyStatus(Enum):
    """User journey test status"""
    PENDING = "pending"
    RUNNING = "running"
    PASSED = "passed"
    FAILED = "failed"
    BLOCKED = "blocked"
    TIMEOUT = "timeout"


class UserType(Enum):
    """User types for journey testing"""
    CREATOR = "creator"
    VIEWER = "viewer"
    ADMIN = "admin"
    GUEST = "guest"
    PREMIUM = "premium"


@dataclass
class JourneyStep:
    """Individual step in user journey"""
    step_id: str
    step_name: str
    action_type: str  # 'click', 'input', 'wait', 'validate', 'api_call'
    target: str  # selector, url, or element identifier
    expected_result: str
    timeout: int = 30
    retry_count: int = 3
    optional: bool = False
    data: Optional[Dict[str, Any]] = None
    validation_criteria: Optional[Dict[str, Any]] = None


@dataclass
class UserJourney:
    """Complete user journey definition"""
    journey_id: str
    journey_name: str
    user_type: UserType
    description: str
    priority: str  # 'critical', 'high', 'medium', 'low'
    estimated_duration: int  # seconds
    preconditions: List[str]
    steps: List[JourneyStep]
    postconditions: List[str]
    success_criteria: Dict[str, Any]
    tags: List[str] = field(default_factory=list)
    environment: str = "staging"


@dataclass
class JourneyResult:
    """User journey test result"""
    journey_id: str
    status: JourneyStatus
    start_time: datetime
    end_time: Optional[datetime] = None
    duration: Optional[float] = None
    steps_executed: int = 0
    steps_passed: int = 0
    steps_failed: int = 0
    failed_step: Optional[str] = None
    error_message: Optional[str] = None
    screenshots: List[str] = field(default_factory=list)
    performance_metrics: Dict[str, float] = field(default_factory=dict)
    user_experience_score: Optional[float] = None


class UserJourneyTester:
    """
    Enterprise user journey testing framework
    """
    
    def __init__(self, config_path -> None: Optional[str] = None) -> None:
        self.config_path = Path(config_path) if config_path else Path("config/user_journey_config.yaml")
        self.config = self._load_config()
        self.driver = None
        self.wait = None
        self.results: List[JourneyResult] = []
        self.journey_definitions: Dict[str, UserJourney] = {}
        self.performance_baseline: Dict[str, float] = {}
        
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration"""
        default_config = {
            "selenium": {
                "headless": True,
                "window_size": "1920,1080",
                "implicit_wait": 10,
                "page_load_timeout": 30,
                "script_timeout": 30
            },
            "api": {
                "base_url": "http://localhost:8000",
                "timeout": 30
            },
            "screenshots": {
                "enabled": True,
                "on_failure": True,
                "directory": "test_screenshots"
            },
            "performance": {
                "track_metrics": True,
                "baseline_percentile": 95
            },
            "reporting": {
                "format": "json",
                "include_screenshots": True
            }
        }
        
        if self.config_path.exists():
            with open(self.config_path, 'r') as f:
                user_config = yaml.safe_load(f)
                default_config.update(user_config)
        
        return default_config
    
    async def initialize_driver(self) -> None:
        """Initialize Selenium WebDriver"""
        try:
            chrome_options = Options()
            if self.config["selenium"]["headless"]:
                chrome_options.add_argument("--headless")
            chrome_options.add_argument(f"--window-size={self.config['selenium']['window_size']}")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-gpu")
            
            self.driver = webdriver.Chrome(options=chrome_options)
            self.driver.implicitly_wait(self.config["selenium"]["implicit_wait"])
            self.driver.set_page_load_timeout(self.config["selenium"]["page_load_timeout"])
            self.driver.set_script_timeout(self.config["selenium"]["script_timeout"])
            
            self.wait = WebDriverWait(self.driver, 30)
            
            logger.info("WebDriver initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize WebDriver: {e}")
            raise

    async def load_journey_definitions(self, definitions_path -> None: str = "config/user_journeys.yaml") -> None:
        """Load user journey definitions from YAML file"""
        try:
            definitions_file = Path(definitions_path)
            if not definitions_file.exists():
                # Create default journey definitions
                await self._create_default_journeys(definitions_file)
            
            with open(definitions_file, 'r') as f:
                definitions = yaml.safe_load(f)
            
            for journey_data in definitions.get("journeys", []):
                journey = UserJourney(
                    journey_id=journey_data["journey_id"],
                    journey_name=journey_data["journey_name"],
                    user_type=UserType(journey_data["user_type"]),
                    description=journey_data["description"],
                    priority=journey_data["priority"],
                    estimated_duration=journey_data["estimated_duration"],
                    preconditions=journey_data["preconditions"],
                    steps=[JourneyStep(**step) for step in journey_data["steps"]],
                    postconditions=journey_data["postconditions"],
                    success_criteria=journey_data["success_criteria"],
                    tags=journey_data.get("tags", []),
                    environment=journey_data.get("environment", "staging")
                )
                self.journey_definitions[journey.journey_id] = journey
            
            logger.info(f"Loaded {len(self.journey_definitions)} journey definitions")
            
        except Exception as e:
            logger.error(f"Failed to load journey definitions: {e}")
            raise

    async def _create_default_journeys(self, file_path -> None: Path) -> None:
        """Create default journey definitions"""
        default_journeys = {
            "journeys": [
                {
                    "journey_id": "creator_upload_flow",
                    "journey_name": "Creator Content Upload Flow",
                    "user_type": "creator",
                    "description": "Complete flow for creator uploading and publishing content",
                    "priority": "critical",
                    "estimated_duration": 120,
                    "preconditions": ["User logged in as creator", "Content ready for upload"],
                    "steps": [
                        {
                            "step_id": "login",
                            "step_name": "Login to platform",
                            "action_type": "input",
                            "target": "#login-form",
                            "expected_result": "Dashboard visible"
                        },
                        {
                            "step_id": "navigate_upload",
                            "step_name": "Navigate to upload page",
                            "action_type": "click",
                            "target": "#upload-button",
                            "expected_result": "Upload form visible"
                        },
                        {
                            "step_id": "upload_content",
                            "step_name": "Upload content file",
                            "action_type": "input",
                            "target": "#file-upload",
                            "expected_result": "Upload progress visible"
                        },
                        {
                            "step_id": "add_metadata",
                            "step_name": "Add content metadata",
                            "action_type": "input",
                            "target": "#metadata-form",
                            "expected_result": "Metadata saved"
                        },
                        {
                            "step_id": "publish_content",
                            "step_name": "Publish content",
                            "action_type": "click",
                            "target": "#publish-button",
                            "expected_result": "Content published successfully"
                        }
                    ],
                    "postconditions": ["Content visible in creator dashboard", "Content available to viewers"],
                    "success_criteria": {
                        "upload_time": "< 30 seconds",
                        "processing_time": "< 60 seconds",
                        "success_rate": "> 95%"
                    },
                    "tags": ["upload", "creator", "critical"],
                    "environment": "staging"
                },
                {
                    "journey_id": "viewer_content_discovery",
                    "journey_name": "Viewer Content Discovery Flow",
                    "user_type": "viewer",
                    "description": "Flow for viewer discovering and consuming content",
                    "priority": "high",
                    "estimated_duration": 90,
                    "preconditions": ["Content available on platform"],
                    "steps": [
                        {
                            "step_id": "visit_homepage",
                            "step_name": "Visit platform homepage",
                            "action_type": "navigate",
                            "target": "/",
                            "expected_result": "Homepage loaded"
                        },
                        {
                            "step_id": "search_content",
                            "step_name": "Search for content",
                            "action_type": "input",
                            "target": "#search-input",
                            "expected_result": "Search results displayed"
                        },
                        {
                            "step_id": "select_content",
                            "step_name": "Select content to view",
                            "action_type": "click",
                            "target": ".content-item:first",
                            "expected_result": "Content player opened"
                        },
                        {
                            "step_id": "play_content",
                            "step_name": "Play content",
                            "action_type": "click",
                            "target": "#play-button",
                            "expected_result": "Content playing"
                        }
                    ],
                    "postconditions": ["Content played successfully", "User engagement tracked"],
                    "success_criteria": {
                        "search_time": "< 5 seconds",
                        "load_time": "< 10 seconds",
                        "playback_quality": "HD"
                    },
                    "tags": ["viewer", "discovery", "playback"],
                    "environment": "staging"
                }
            ]
        }
        
        file_path.parent.mkdir(parents=True, exist_ok=True)
        with open(file_path, 'w') as f:
            yaml.dump(default_journeys, f, default_flow_style=False)

    async def execute_journey(self, journey_id: str) -> JourneyResult:
        """Execute a specific user journey"""
        if journey_id not in self.journey_definitions:
            raise ValueError(f"Journey {journey_id} not found")
        
        journey = self.journey_definitions[journey_id]
        result = JourneyResult(
            journey_id=journey_id,
            status=JourneyStatus.PENDING,
            start_time=datetime.now()
        )
        
        try:
            logger.info(f"Starting journey: {journey.journey_name}")
            result.status = JourneyStatus.RUNNING
            
            # Execute preconditions
            await self._verify_preconditions(journey.preconditions)
            
            # Execute journey steps
            for i, step in enumerate(journey.steps):
                try:
                    result.steps_executed += 1
                    await self._execute_step(step, journey)
                    result.steps_passed += 1
                    logger.info(f"Step {i+1}/{len(journey.steps)} passed: {step.step_name}")
                    
                except Exception as e:
                    result.steps_failed += 1
                    result.failed_step = step.step_name
                    result.error_message = str(e)
                    
                    if self.config["screenshots"]["on_failure"]:
                        screenshot_path = await self._take_screenshot(f"failure_{journey_id}_{step.step_id}")
                        result.screenshots.append(screenshot_path)
                    
                    if not step.optional:
                        result.status = JourneyStatus.FAILED
                        logger.error(f"Journey failed at step: {step.step_name} - {e}")
                        break
                    
                    logger.warning(f"Optional step failed: {step.step_name} - {e}")
            
            # Verify postconditions
            if result.status != JourneyStatus.FAILED:
                await self._verify_postconditions(journey.postconditions)
                result.status = JourneyStatus.PASSED
            
            # Calculate performance metrics
            result.performance_metrics = await self._calculate_performance_metrics(journey)
            result.user_experience_score = await self._calculate_ux_score(result)
            
        except Exception as e:
            result.status = JourneyStatus.FAILED
            result.error_message = str(e)
            logger.error(f"Journey execution failed: {e}")
        
        finally:
            result.end_time = datetime.now()
            result.duration = (result.end_time - result.start_time).total_seconds()
            
        self.results.append(result)
        return result

    async def _execute_step(self, step -> None: JourneyStep, journey -> None: UserJourney) -> None:
        """Execute individual journey step"""
        start_time = time.time()
        
        try:
            if step.action_type == "navigate":
                url = step.target if step.target.startswith("http") else f"{self.config['api']['base_url']}{step.target}"
                self.driver.get(url)
                
            elif step.action_type == "click":
                element = self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, step.target)))
                element.click()
                
            elif step.action_type == "input":
                element = self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, step.target)))
                if step.data and "value" in step.data:
                    element.clear()
                    element.send_keys(step.data["value"])
                
            elif step.action_type == "wait":
                await asyncio.sleep(int(step.target))
                
            elif step.action_type == "validate":
                await self._validate_step(step)
                
            elif step.action_type == "api_call":
                await self._execute_api_call(step)
            
            # Wait for expected result
            if step.expected_result and step.expected_result != "":
                await self._verify_expected_result(step.expected_result)
            
            execution_time = time.time() - start_time
            if execution_time > step.timeout:
                raise TimeoutException(f"Step timeout: {step.step_name}")
                
        except Exception as e:
            raise Exception(f"Step execution failed: {step.step_name} - {e}")

    async def _verify_expected_result(self, expected_result -> None: str) -> None:
        """Verify step expected result"""
        # Simple text-based verification
        if "visible" in expected_result.lower():
            # Check if page contains expected text
            page_text = self.driver.page_source.lower()
            if "dashboard" in expected_result.lower() and "dashboard" not in page_text:
                raise Exception(f"Expected result not found: {expected_result}")

    async def _take_screenshot(self, name: str) -> str:
        """Take screenshot for debugging"""
        if not self.config["screenshots"]["enabled"]:
            return ""
        
        screenshot_dir = Path(self.config["screenshots"]["directory"])
        screenshot_dir.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{name}_{timestamp}.png"
        filepath = screenshot_dir / filename
        
        self.driver.save_screenshot(str(filepath))
        return str(filepath)

    async def _calculate_performance_metrics(self, journey: UserJourney) -> Dict[str, float]:
        """Calculate performance metrics for journey"""
        # Use browser performance API to get metrics
        performance_data = self.driver.execute_script("""
            return {
                navigationStart: performance.timing.navigationStart,
                loadEventEnd: performance.timing.loadEventEnd,
                domContentLoaded: performance.timing.domContentLoadedEventEnd,
                firstPaint: performance.getEntriesByType('paint')[0]?.startTime || 0,
                firstContentfulPaint: performance.getEntriesByType('paint')[1]?.startTime || 0
            };
        """)
        
        metrics = {
            "page_load_time": (performance_data["loadEventEnd"] - performance_data["navigationStart"]) / 1000,
            "dom_content_loaded": (performance_data["domContentLoaded"] - performance_data["navigationStart"]) / 1000,
            "first_paint": performance_data["firstPaint"] / 1000,
            "first_contentful_paint": performance_data["firstContentfulPaint"] / 1000
        }
        
        return metrics

    async def _calculate_ux_score(self, result: JourneyResult) -> float:
        """Calculate user experience score"""
        score = 100.0
        
        # Deduct points for failures
        if result.status == JourneyStatus.FAILED:
            score -= 50
        
        # Deduct points for failed steps
        if result.steps_failed > 0:
            score -= (result.steps_failed / result.steps_executed) * 30
        
        # Deduct points for poor performance
        if result.performance_metrics:
            page_load_time = result.performance_metrics.get("page_load_time", 0)
            if page_load_time > 3:
                score -= min(20, (page_load_time - 3) * 5)
        
        # Deduct points for long duration
        if result.duration and result.duration > 60:
            score -= min(10, (result.duration - 60) / 10)
        
        return max(0, score)

    async def run_journey_suite(self, journey_ids: Optional[List[str]] = None) -> Dict[str, Any]:
        """Run complete journey test suite"""
        try:
            await self.initialize_driver()
            await self.load_journey_definitions()
            
            if not journey_ids:
                journey_ids = list(self.journey_definitions.keys())
            
            logger.info(f"Running {len(journey_ids)} user journeys")
            
            results = []
            for journey_id in journey_ids:
                result = await self.execute_journey(journey_id)
                results.append(result)
            
            # Generate summary report
            summary = await self._generate_summary_report(results)
            
            return {
                "summary": summary,
                "results": results,
                "timestamp": datetime.now().isoformat()
            }
            
        finally:
            if self.driver:
                self.driver.quit()

    async def _generate_summary_report(self, results: List[JourneyResult]) -> Dict[str, Any]:
        """Generate summary report"""
        total_journeys = len(results)
        passed = sum(1 for r in results if r.status == JourneyStatus.PASSED)
        failed = sum(1 for r in results if r.status == JourneyStatus.FAILED)
        
        avg_duration = np.mean([r.duration for r in results if r.duration])
        avg_ux_score = np.mean([r.user_experience_score for r in results if r.user_experience_score])
        
        return {
            "total_journeys": total_journeys,
            "passed": passed,
            "failed": failed,
            "success_rate": (passed / total_journeys) * 100 if total_journeys > 0 else 0,
            "average_duration": avg_duration,
            "average_ux_score": avg_ux_score,
            "performance_summary": {
                "avg_page_load_time": np.mean([
                    r.performance_metrics.get("page_load_time", 0) 
                    for r in results if r.performance_metrics
                ]) if results else 0
            }
        }

    async def _verify_preconditions(self, preconditions -> None: List[str]) -> None:
        """Verify journey preconditions"""
        for condition in preconditions:
            logger.info(f"Verifying precondition: {condition}")
            # Implementation depends on specific conditions

    async def _verify_postconditions(self, postconditions -> None: List[str]) -> None:
        """Verify journey postconditions"""
        for condition in postconditions:
            logger.info(f"Verifying postcondition: {condition}")
            # Implementation depends on specific conditions

    async def _validate_step(self, step -> None: JourneyStep) -> None:
        """Validate step-specific criteria"""
        if step.validation_criteria:
            for criterion, expected in step.validation_criteria.items():
                # Implement specific validation logic
                pass

    async def _execute_api_call(self, step -> None: JourneyStep) -> None:
        """Execute API call step"""
        if not step.data:
            raise ValueError("API call step requires data")
        
        method = step.data.get("method", "GET")
        url = step.data.get("url", "")
        headers = step.data.get("headers", {})
        payload = step.data.get("payload", {})
        
        async with aiohttp.ClientSession() as session:
            async with session.request(method, url, headers=headers, json=payload) as response:
                if response.status >= 400:
                    raise Exception(f"API call failed: {response.status}")


# Global instance
user_journey_tester = UserJourneyTester()

# Convenience functions
async def test_creator_journey() -> None:
    """Test creator upload journey"""
    return await user_journey_tester.execute_journey("creator_upload_flow")

async def test_viewer_journey() -> None:
    """Test viewer discovery journey"""
    return await user_journey_tester.execute_journey("viewer_content_discovery")

async def run_all_journeys() -> None:
    """Run all defined user journeys"""
    return await user_journey_tester.run_journey_suite()

if __name__ == "__main__":
    # Example usage
    async def main() -> None:
        suite_results = await run_all_journeys()
        print(json.dumps(suite_results["summary"], indent=2))
    
    asyncio.run(main())