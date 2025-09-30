#!/usr/bin/env python3
"""
E2E Test Orchestrator - Ainflue Quality Platform
==============================================

Enterprise-grade End-to-End testing orchestration system.
Demonstrates Lead Dev IA + DevOps + Microservices expertise.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
import json
import time
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Callable, Tuple
from datetime import datetime, timedelta
from pathlib import Path
import yaml
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException
import aiohttp
import asyncpg

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class E2ETestStep:
    """Single step in an E2E test scenario."""
    name: str
    action: str  # 'navigate', 'click', 'type', 'wait', 'assert', 'api_call'
    target: Optional[str] = None  # CSS selector, URL, API endpoint
    value: Optional[str] = None  # Text to type, expected value
    timeout: int = 10
    screenshot: bool = False
    critical: bool = True  # If False, failure won't stop the test


@dataclass
class E2ETestScenario:
    """Complete E2E test scenario."""
    name: str
    description: str
    tags: List[str]
    setup_steps: List[E2ETestStep] = field(default_factory=list)
    test_steps: List[E2ETestStep] = field(default_factory=list)
    cleanup_steps: List[E2ETestStep] = field(default_factory=list)
    timeout: int = 300  # Total scenario timeout in seconds
    browser: str = "chrome"  # chrome, firefox, edge
    mobile: bool = False


@dataclass
class E2ETestResult:
    """E2E test execution result."""
    scenario_name: str
    status: str  # 'passed', 'failed', 'error', 'skipped'
    execution_time_ms: float
    steps_executed: int
    steps_passed: int
    steps_failed: int
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    screenshots: List[str] = field(default_factory=list)
    performance_metrics: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)


class BrowserManager:
    """Browser management for E2E testing."""
    
    def __init__(self, browser_type: str = "chrome", headless: bool = True, mobile: bool = False):
        self.browser_type = browser_type
        self.headless = headless
        self.mobile = mobile
        self.driver = None
        
    def get_driver_options(self):
        """Get browser driver options."""
        if self.browser_type == "chrome":
            options = Options()
            if self.headless:
                options.add_argument("--headless")
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            options.add_argument("--disable-gpu")
            options.add_argument("--window-size=1920,1080")
            
            if self.mobile:
                mobile_emulation = {
                    "deviceMetrics": {"width": 375, "height": 667, "pixelRatio": 2.0},
                    "userAgent": "Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X) AppleWebKit/605.1.15"
                }
                options.add_experimental_option("mobileEmulation", mobile_emulation)
            
            return options
        
        # Add other browsers as needed
        return None
    
    def start_browser(self):
        """Start browser session."""
        try:
            options = self.get_driver_options()
            
            if self.browser_type == "chrome":
                from selenium.webdriver.chrome.service import Service
                from webdriver_manager.chrome import ChromeDriverManager
                
                service = Service(ChromeDriverManager().install())
                self.driver = webdriver.Chrome(service=service, options=options)
            
            logger.info(f"Started {self.browser_type} browser session")
            return self.driver
            
        except Exception as e:
            logger.error(f"Failed to start browser: {e}")
            raise
    
    def stop_browser(self):
        """Stop browser session."""
        if self.driver:
            try:
                self.driver.quit()
                logger.info("Browser session closed")
            except Exception as e:
                logger.error(f"Error closing browser: {e}")


class PerformanceMonitor:
    """Monitor performance metrics during E2E tests."""
    
    def __init__(self, driver):
        self.driver = driver
        self.start_time = None
        self.metrics = {}
    
    def start_monitoring(self):
        """Start performance monitoring."""
        self.start_time = time.time()
        
        # Get initial navigation timing
        try:
            timing = self.driver.execute_script("""
                var timing = performance.timing;
                return {
                    navigationStart: timing.navigationStart,
                    loadEventEnd: timing.loadEventEnd,
                    domContentLoadedEventEnd: timing.domContentLoadedEventEnd
                };
            """)
            self.metrics['initial_timing'] = timing
        except Exception as e:
            logger.warning(f"Could not get initial timing: {e}")
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get current performance metrics."""
        metrics = {}
        
        try:
            # Navigation timing
            navigation_timing = self.driver.execute_script("""
                var timing = performance.timing;
                var navigation = performance.navigation;
                return {
                    type: navigation.type,
                    redirectCount: navigation.redirectCount,
                    timing: {
                        navigationStart: timing.navigationStart,
                        unloadEventStart: timing.unloadEventStart,
                        unloadEventEnd: timing.unloadEventEnd,
                        redirectStart: timing.redirectStart,
                        redirectEnd: timing.redirectEnd,
                        fetchStart: timing.fetchStart,
                        domainLookupStart: timing.domainLookupStart,
                        domainLookupEnd: timing.domainLookupEnd,
                        connectStart: timing.connectStart,
                        connectEnd: timing.connectEnd,
                        secureConnectionStart: timing.secureConnectionStart,
                        requestStart: timing.requestStart,
                        responseStart: timing.responseStart,
                        responseEnd: timing.responseEnd,
                        domLoading: timing.domLoading,
                        domInteractive: timing.domInteractive,
                        domContentLoadedEventStart: timing.domContentLoadedEventStart,
                        domContentLoadedEventEnd: timing.domContentLoadedEventEnd,
                        domComplete: timing.domComplete,
                        loadEventStart: timing.loadEventStart,
                        loadEventEnd: timing.loadEventEnd
                    }
                };
            """)
            
            # Calculate key metrics
            timing = navigation_timing['timing']
            if timing['loadEventEnd'] > 0:
                metrics['page_load_time'] = timing['loadEventEnd'] - timing['navigationStart']
                metrics['dom_content_loaded'] = timing['domContentLoadedEventEnd'] - timing['navigationStart']
                metrics['dom_interactive'] = timing['domInteractive'] - timing['navigationStart']
                metrics['first_byte'] = timing['responseStart'] - timing['navigationStart']
            
            # Resource timing
            resources = self.driver.execute_script("""
                return performance.getEntriesByType('resource').map(function(entry) {
                    return {
                        name: entry.name,
                        duration: entry.duration,
                        size: entry.transferSize || entry.encodedBodySize,
                        type: entry.initiatorType
                    };
                });
            """)
            
            metrics['resources'] = {
                'total_resources': len(resources),
                'total_size': sum(r.get('size', 0) for r in resources),
                'average_load_time': sum(r['duration'] for r in resources) / len(resources) if resources else 0,
                'by_type': {}
            }
            
            # Group by resource type
            for resource in resources:
                res_type = resource['type']
                if res_type not in metrics['resources']['by_type']:
                    metrics['resources']['by_type'][res_type] = {
                        'count': 0,
                        'total_size': 0,
                        'total_duration': 0
                    }
                
                metrics['resources']['by_type'][res_type]['count'] += 1
                metrics['resources']['by_type'][res_type]['total_size'] += resource.get('size', 0)
                metrics['resources']['by_type'][res_type]['total_duration'] += resource['duration']
            
        except Exception as e:
            logger.warning(f"Could not get performance metrics: {e}")
        
        return metrics


class E2ETestOrchestrator:
    """
    Enterprise E2E Test Orchestration Engine
    ======================================
    
    Comprehensive end-to-end testing orchestration for web applications.
    Demonstrates Lead Dev IA + DevOps + Microservices expertise.
    """
    
    def __init__(self, config_path: Optional[str] = None):
        self.config = self._load_config(config_path)
        self.browser_manager = None
        self.performance_monitor = None
        self.test_results: List[E2ETestResult] = []
        self.screenshots_dir = Path("screenshots")
        self.screenshots_dir.mkdir(exist_ok=True)
        
        # Test execution state
        self.current_scenario = None
        self.current_step = 0
    
    def _load_config(self, config_path: Optional[str]) -> Dict[str, Any]:
        """Load E2E testing configuration."""
        default_config = {
            'browser': {
                'type': 'chrome',
                'headless': True,
                'window_size': '1920,1080',
                'timeout': 30
            },
            'test_settings': {
                'parallel_tests': 3,
                'retry_failed': True,
                'max_retries': 2,
                'screenshot_on_failure': True,
                'performance_monitoring': True
            },
            'environments': {
                'development': 'http://localhost:8000',
                'staging': 'https://staging.ainflue.com',
                'production': 'https://ainflue.com'
            },
            'test_data': {
                'users': {
                    'creator': {'email': 'creator@test.com', 'password': 'test123'},
                    'admin': {'email': 'admin@test.com', 'password': 'admin123'}
                }
            }
        }
        
        if config_path and Path(config_path).exists():
            with open(config_path, 'r') as f:
                user_config = yaml.safe_load(f)
                default_config.update(user_config)
        
        return default_config
    
    async def load_scenarios(self, scenarios_dir: str) -> List[E2ETestScenario]:
        """Load E2E test scenarios from directory."""
        scenarios = []
        scenarios_path = Path(scenarios_dir)
        
        if not scenarios_path.exists():
            logger.warning(f"Scenarios directory not found: {scenarios_dir}")
            return scenarios
        
        for scenario_file in scenarios_path.glob("*.yaml"):
            try:
                with open(scenario_file, 'r') as f:
                    scenario_data = yaml.safe_load(f)
                
                scenario = E2ETestScenario(
                    name=scenario_data.get('name', scenario_file.stem),
                    description=scenario_data.get('description', ''),
                    tags=scenario_data.get('tags', []),
                    setup_steps=[E2ETestStep(**step) for step in scenario_data.get('setup_steps', [])],
                    test_steps=[E2ETestStep(**step) for step in scenario_data.get('test_steps', [])],
                    cleanup_steps=[E2ETestStep(**step) for step in scenario_data.get('cleanup_steps', [])],
                    timeout=scenario_data.get('timeout', 300),
                    browser=scenario_data.get('browser', 'chrome'),
                    mobile=scenario_data.get('mobile', False)
                )
                
                scenarios.append(scenario)
                logger.info(f"Loaded E2E scenario: {scenario.name}")
                
            except Exception as e:
                logger.error(f"Failed to load scenario {scenario_file}: {e}")
        
        return scenarios
    
    async def execute_step(self, step: E2ETestStep) -> Tuple[bool, List[str]]:
        """Execute a single test step."""
        errors = []
        
        try:
            driver = self.browser_manager.driver
            wait = WebDriverWait(driver, step.timeout)
            
            if step.action == 'navigate':
                logger.info(f"Navigating to: {step.target}")
                driver.get(step.target)
                
                # Wait for page load
                wait.until(lambda d: d.execute_script("return document.readyState") == "complete")
                
            elif step.action == 'click':
                logger.info(f"Clicking element: {step.target}")
                element = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, step.target)))
                driver.execute_script("arguments[0].scrollIntoView(true);", element)
                element.click()
                
            elif step.action == 'type':
                logger.info(f"Typing in element: {step.target}")
                element = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, step.target)))
                element.clear()
                element.send_keys(step.value)
                
            elif step.action == 'wait':
                logger.info(f"Waiting for element: {step.target}")
                if step.target:
                    wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, step.target)))
                else:
                    await asyncio.sleep(int(step.value or 1))
                
            elif step.action == 'assert':
                logger.info(f"Asserting element: {step.target}")
                if step.target:
                    element = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, step.target)))
                    if step.value:
                        actual_text = element.text
                        if step.value not in actual_text:
                            errors.append(f"Expected text '{step.value}' not found in '{actual_text}'")
                
            elif step.action == 'api_call':
                logger.info(f"Making API call to: {step.target}")
                # Implement API call logic
                async with aiohttp.ClientSession() as session:
                    async with session.get(step.target) as response:
                        if response.status not in [200, 201, 204]:
                            errors.append(f"API call failed with status {response.status}")
            
            # Take screenshot if requested
            if step.screenshot:
                screenshot_path = self.screenshots_dir / f"{self.current_scenario.name}_{step.name}_{int(time.time())}.png"
                driver.save_screenshot(str(screenshot_path))
                logger.info(f"Screenshot saved: {screenshot_path}")
            
            return len(errors) == 0, errors
            
        except TimeoutException as e:
            errors.append(f"Timeout waiting for {step.action} on {step.target}: {str(e)}")
            return False, errors
            
        except WebDriverException as e:
            errors.append(f"WebDriver error during {step.action}: {str(e)}")
            return False, errors
            
        except Exception as e:
            errors.append(f"Unexpected error during {step.action}: {str(e)}")
            return False, errors
    
    async def execute_scenario(self, scenario: E2ETestScenario) -> E2ETestResult:
        """Execute a complete E2E test scenario."""
        start_time = time.time()
        self.current_scenario = scenario
        
        result = E2ETestResult(
            scenario_name=scenario.name,
            status='error',
            execution_time_ms=0.0,
            steps_executed=0,
            steps_passed=0,
            steps_failed=0
        )
        
        try:
            # Initialize browser
            self.browser_manager = BrowserManager(
                browser_type=scenario.browser,
                headless=self.config['browser']['headless'],
                mobile=scenario.mobile
            )
            
            driver = self.browser_manager.start_browser()
            
            # Initialize performance monitoring
            if self.config['test_settings']['performance_monitoring']:
                self.performance_monitor = PerformanceMonitor(driver)
                self.performance_monitor.start_monitoring()
            
            # Execute setup steps
            logger.info(f"Executing setup steps for scenario: {scenario.name}")
            for step in scenario.setup_steps:
                success, errors = await self.execute_step(step)
                result.steps_executed += 1
                
                if success:
                    result.steps_passed += 1
                else:
                    result.steps_failed += 1
                    result.errors.extend(errors)
                    
                    if step.critical:
                        logger.error(f"Critical setup step failed: {step.name}")
                        result.status = 'failed'
                        return result
            
            # Execute test steps
            logger.info(f"Executing test steps for scenario: {scenario.name}")
            for step in scenario.test_steps:
                success, errors = await self.execute_step(step)
                result.steps_executed += 1
                
                if success:
                    result.steps_passed += 1
                else:
                    result.steps_failed += 1
                    result.errors.extend(errors)
                    
                    # Take screenshot on failure
                    if self.config['test_settings']['screenshot_on_failure']:
                        screenshot_path = self.screenshots_dir / f"{scenario.name}_failure_{int(time.time())}.png"
                        driver.save_screenshot(str(screenshot_path))
                        result.screenshots.append(str(screenshot_path))
                    
                    if step.critical:
                        logger.error(f"Critical test step failed: {step.name}")
                        result.status = 'failed'
                        break
            
            # Execute cleanup steps (always run)
            logger.info(f"Executing cleanup steps for scenario: {scenario.name}")
            for step in scenario.cleanup_steps:
                try:
                    success, errors = await self.execute_step(step)
                    result.steps_executed += 1
                    
                    if success:
                        result.steps_passed += 1
                    else:
                        result.steps_failed += 1
                        result.warnings.extend(errors)  # Cleanup errors are warnings
                        
                except Exception as e:
                    result.warnings.append(f"Cleanup step error: {str(e)}")
            
            # Get performance metrics
            if self.performance_monitor:
                result.performance_metrics = self.performance_monitor.get_performance_metrics()
            
            # Determine final status
            if result.status != 'failed':
                if result.steps_failed == 0:
                    result.status = 'passed'
                else:
                    result.status = 'failed'
            
        except Exception as e:
            logger.error(f"Scenario execution error: {e}")
            result.errors.append(f"Scenario execution error: {str(e)}")
            result.status = 'error'
        
        finally:
            # Calculate execution time
            end_time = time.time()
            result.execution_time_ms = (end_time - start_time) * 1000
            
            # Cleanup browser
            if self.browser_manager:
                self.browser_manager.stop_browser()
        
        return result
    
    async def run_e2e_tests(self, scenarios: List[E2ETestScenario], tags: Optional[List[str]] = None) -> Dict[str, Any]:
        """Run E2E tests for specified scenarios."""
        logger.info(f"Starting E2E tests for {len(scenarios)} scenarios")
        
        # Filter scenarios by tags if specified
        if tags:
            scenarios = [s for s in scenarios if any(tag in s.tags for tag in tags)]
            logger.info(f"Filtered to {len(scenarios)} scenarios by tags: {tags}")
        
        results = []
        
        # Execute scenarios
        for scenario in scenarios:
            logger.info(f"Executing scenario: {scenario.name}")
            
            try:
                result = await self.execute_scenario(scenario)
                results.append(result)
                
                # Retry failed scenarios if configured
                if (result.status == 'failed' and 
                    self.config['test_settings']['retry_failed'] and 
                    self.config['test_settings']['max_retries'] > 0):
                    
                    logger.info(f"Retrying failed scenario: {scenario.name}")
                    retry_result = await self.execute_scenario(scenario)
                    
                    # Use better result
                    if retry_result.status == 'passed':
                        results[-1] = retry_result
                        logger.info(f"Retry successful for scenario: {scenario.name}")
                
            except Exception as e:
                logger.error(f"Failed to execute scenario {scenario.name}: {e}")
                # Create error result
                error_result = E2ETestResult(
                    scenario_name=scenario.name,
                    status='error',
                    execution_time_ms=0.0,
                    steps_executed=0,
                    steps_passed=0,
                    steps_failed=0,
                    errors=[f"Execution failed: {str(e)}"]
                )
                results.append(error_result)
        
        self.test_results = results
        
        # Generate comprehensive report
        return self._generate_report()
    
    def _generate_report(self) -> Dict[str, Any]:
        """Generate comprehensive E2E test report."""
        report = {
            'summary': {
                'timestamp': datetime.now().isoformat(),
                'total_scenarios': len(self.test_results),
                'passed_scenarios': len([r for r in self.test_results if r.status == 'passed']),
                'failed_scenarios': len([r for r in self.test_results if r.status == 'failed']),
                'error_scenarios': len([r for r in self.test_results if r.status == 'error']),
                'total_steps': sum(r.steps_executed for r in self.test_results),
                'passed_steps': sum(r.steps_passed for r in self.test_results),
                'failed_steps': sum(r.steps_failed for r in self.test_results),
            },
            'scenarios': [],
            'performance': {
                'total_execution_time': sum(r.execution_time_ms for r in self.test_results),
                'average_scenario_time': 0.0,
                'fastest_scenario': None,
                'slowest_scenario': None
            },
            'failures': []
        }
        
        # Calculate success rate
        total_scenarios = report['summary']['total_scenarios']
        if total_scenarios > 0:
            report['summary']['success_rate'] = (report['summary']['passed_scenarios'] / total_scenarios) * 100
            report['performance']['average_scenario_time'] = report['performance']['total_execution_time'] / total_scenarios
        else:
            report['summary']['success_rate'] = 0.0
        
        # Process each scenario result
        for result in self.test_results:
            scenario_report = {
                'name': result.scenario_name,
                'status': result.status,
                'execution_time_ms': result.execution_time_ms,
                'steps_executed': result.steps_executed,
                'steps_passed': result.steps_passed,
                'steps_failed': result.steps_failed,
                'errors': result.errors,
                'warnings': result.warnings,
                'screenshots': result.screenshots,
                'performance_metrics': result.performance_metrics
            }
            
            report['scenarios'].append(scenario_report)
            
            # Add failures
            if result.status in ['failed', 'error']:
                report['failures'].append({
                    'scenario': result.scenario_name,
                    'status': result.status,
                    'errors': result.errors
                })
        
        # Performance analysis
        if self.test_results:
            fastest = min(self.test_results, key=lambda r: r.execution_time_ms)
            slowest = max(self.test_results, key=lambda r: r.execution_time_ms)
            
            report['performance']['fastest_scenario'] = {
                'name': fastest.scenario_name,
                'time_ms': fastest.execution_time_ms
            }
            
            report['performance']['slowest_scenario'] = {
                'name': slowest.scenario_name,
                'time_ms': slowest.execution_time_ms
            }
        
        return report
    
    async def save_report(self, report: Dict[str, Any], output_path: str = "e2e_test_report.json"):
        """Save test report to file."""
        with open(output_path, 'w') as f:
            json.dump(report, f, indent=2, default=str)
        logger.info(f"E2E test report saved to: {output_path}")


# CLI Interface
async def main():
    """Main CLI interface for E2E testing."""
    import argparse
    
    parser = argparse.ArgumentParser(description="E2E Test Orchestration Engine")
    parser.add_argument("--scenarios-dir", required=True, help="Directory containing test scenarios")
    parser.add_argument("--config", help="Configuration file path")
    parser.add_argument("--tags", nargs='+', help="Filter scenarios by tags")
    parser.add_argument("--output", default="e2e_test_report.json", help="Output report file")
    parser.add_argument("--headless", action="store_true", help="Run browser in headless mode")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose logging")
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Initialize orchestrator
    orchestrator = E2ETestOrchestrator(args.config)
    
    # Override headless setting if specified
    if args.headless:
        orchestrator.config['browser']['headless'] = True
    
    try:
        # Load scenarios
        scenarios = await orchestrator.load_scenarios(args.scenarios_dir)
        
        if not scenarios:
            logger.error("No scenarios found to execute")
            return
        
        # Run tests
        report = await orchestrator.run_e2e_tests(scenarios, args.tags)
        
        # Save report
        await orchestrator.save_report(report, args.output)
        
        # Print summary
        summary = report['summary']
        print(f"\n🎭 E2E Test Results")
        print(f"{'='*50}")
        print(f"Scenarios Executed: {summary['total_scenarios']}")
        print(f"Success Rate: {summary['success_rate']:.2f}%")
        print(f"Steps Executed: {summary['total_steps']}")
        print(f"Average Scenario Time: {report['performance']['average_scenario_time']:.2f}ms")
        
        if summary['success_rate'] < 100:
            print(f"\n❌ {len(report['failures'])} failures detected")
            for failure in report['failures'][:5]:  # Show first 5 failures
                print(f"  - {failure['scenario']}: {failure['status']}")
        else:
            print(f"\n✅ All scenarios passed!")
    
    except Exception as e:
        logger.error(f"E2E test execution failed: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(main())