"""Selenium Scraper - IA-Influencer-Agent
======================================

Advanced Selenium-based scraper for JavaScript-heavy sites.
Handles dynamic content and complex interactions.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: All rights reserved. Unauthorized use, reproduction, or distribution prohibited.

⚠️ CRITICAL LEGAL WARNING ⚠️
UNAUTHORIZED USE, COPYING, OR DISTRIBUTION IS STRICTLY PROHIBITED AND WILL RESULT IN IMMEDIATE LEGAL ACTION.
This technology is EXCLUSIVE property of Fahed Mlaiel. Contact: mlaiel@live.de for licensing.
"""import asyncio
import logging
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass
from datetime import datetime
import time
import random
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException, NoSuchElementException, WebDriverException
import undetected_chromedriver as uc
from fake_useragent import UserAgent

@dataclass
class SeleniumConfig:
    """Selenium scraper configuration."""    headless: bool = True
    window_size: tuple = (1920, 1080)
    timeout: int = 30
    page_load_timeout: int = 60
    implicit_wait: int = 10
    use_undetected_chrome: bool = True
    disable_images: bool = True
    disable_css: bool = False
    user_agent: Optional[str] = None
    proxy: Optional[str] = None
    extensions: List[str] = None
    custom_options: List[str] = None

@dataclass
class InteractionStep:
    """Selenium interaction step definition."""    action: str  # click, type, scroll, wait, screenshot, etc.
    selector: str
    value: Optional[str] = None
    timeout: int = 10
    optional: bool = False

class SeleniumScraper:
    """    Advanced Selenium-based web scraper.
    
    Features:
    - JavaScript execution
    - Dynamic content loading
    - User interaction simulation
    - Screenshot capture
    - Anti-detection mechanisms
    - Headless and headed modes
    - Custom browser profiles
    - Extension support
    """    
    def __init__(self, config: Optional[SeleniumConfig] = None):
        self.config = config or SeleniumConfig()
        self.logger = logging.getLogger(__name__)
        self.driver: Optional[webdriver.Chrome] = None
        self.user_agent = UserAgent()
        
    async def __aenter__(self):
        """Async context manager entry."""        await self.start_driver()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""        await self.close_driver()
        
    async def start_driver(self):
        """Initialize and start Chrome driver."""        if self.driver:
            return
            
        options = self._create_chrome_options()
        
        try:
            if self.config.use_undetected_chrome:
                self.driver = uc.Chrome(options=options)
            else:
                self.driver = webdriver.Chrome(options=options)
                
            # Configure timeouts
            self.driver.set_page_load_timeout(self.config.page_load_timeout)
            self.driver.implicitly_wait(self.config.implicit_wait)
            
            # Set window size
            self.driver.set_window_size(*self.config.window_size)
            
            # Execute anti-detection scripts
            if self.config.use_undetected_chrome:
                self._execute_stealth_scripts()
                
            self.logger.info("Chrome driver started successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to start Chrome driver: {e}")
            raise
            
    async def close_driver(self):
        """Close Chrome driver."""        if self.driver:
            try:
                self.driver.quit()
                self.driver = None
                self.logger.info("Chrome driver closed")
            except Exception as e:
                self.logger.error(f"Error closing driver: {e}")
                
    def _create_chrome_options(self) -> Options:
        """Create Chrome options with optimizations."""        options = uc.ChromeOptions() if self.config.use_undetected_chrome else Options()
        
        # Basic options
        if self.config.headless:
            options.add_argument('--headless')
            
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-gpu')
        options.add_argument('--disable-web-security')
        options.add_argument('--disable-features=VizDisplayCompositor')
        
        # Performance optimizations
        if self.config.disable_images:
            prefs = {"profile.managed_default_content_settings.images": 2}
            options.add_experimental_option("prefs", prefs)
            
        if self.config.disable_css:
            options.add_argument('--disable-extensions')
            options.add_argument('--disable-plugins')
            
        # Anti-detection
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        
        # User agent
        if self.config.user_agent:
            options.add_argument(f'--user-agent={self.config.user_agent}')
        else:
            options.add_argument(f'--user-agent={self.user_agent.chrome}')
            
        # Proxy
        if self.config.proxy:
            options.add_argument(f'--proxy-server={self.config.proxy}')
            
        # Custom options
        if self.config.custom_options:
            for option in self.config.custom_options:
                options.add_argument(option)
                
        return options
        
    def _execute_stealth_scripts(self):
        """Execute stealth scripts to avoid detection."""        if not self.driver:
            return
            
        # Remove webdriver property
        self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
        # Override plugins and languages
        self.driver.execute_script("""            Object.defineProperty(navigator, 'plugins', {
                get: () => [1, 2, 3, 4, 5]
            });
            Object.defineProperty(navigator, 'languages', {
                get: () => ['en-US', 'en']
            });
        """)
        
    async def navigate_to(self, url: str, wait_for_element: Optional[str] = None) -> bool:
        """Navigate to URL and optionally wait for element."""        if not self.driver:
            await self.start_driver()
            
        try:
            self.logger.info(f"Navigating to: {url}")
            self.driver.get(url)
            
            # Wait for specific element if provided
            if wait_for_element:
                await self._wait_for_element(wait_for_element, self.config.timeout)
                
            # Add random delay to simulate human behavior
            await asyncio.sleep(random.uniform(1, 3))
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to navigate to {url}: {e}")
            return False
            
    async def execute_interactions(self, steps: List[InteractionStep]) -> Dict[str, Any]:
        """Execute series of interaction steps."""        results = {
            'success': True,
            'steps_completed': 0,
            'errors': [],
            'screenshots': [],
            'data_extracted': {}
        }
        
        for i, step in enumerate(steps):
            try:
                result = await self._execute_step(step)
                results['steps_completed'] += 1
                
                if result:
                    results['data_extracted'][f'step_{i}'] = result
                    
            except Exception as e:
                error_msg = f"Step {i} ({step.action}) failed: {e}"
                self.logger.error(error_msg)
                results['errors'].append(error_msg)
                
                if not step.optional:
                    results['success'] = False
                    break
                    
        return results
        
    async def _execute_step(self, step: InteractionStep) -> Any:
        """Execute single interaction step."""        if not self.driver:
            raise Exception("Driver not initialized")
            
        element = None
        
        # Find element if selector provided
        if step.selector:
            element = await self._find_element(step.selector, step.timeout)
            
        # Execute action
        if step.action == 'click':
            return await self._click_element(element)
        elif step.action == 'type':
            return await self._type_text(element, step.value)
        elif step.action == 'clear':
            return await self._clear_element(element)
        elif step.action == 'scroll':
            return await self._scroll_to_element(element)
        elif step.action == 'wait':
            await asyncio.sleep(step.timeout)
            return True
        elif step.action == 'screenshot':
            return await self._take_screenshot(step.value)
        elif step.action == 'extract_text':
            return await self._extract_text(element)
        elif step.action == 'extract_attribute':
            return await self._extract_attribute(element, step.value)
        elif step.action == 'extract_html':
            return await self._extract_html(element)
        elif step.action == 'javascript':
            return await self._execute_javascript(step.value)
        elif step.action == 'hover':
            return await self._hover_element(element)
        elif step.action == 'select_dropdown':
            return await self._select_dropdown(element, step.value)
        else:
            raise Exception(f"Unknown action: {step.action}")
            
    async def _find_element(self, selector: str, timeout: int):
        """Find element with timeout."""        wait = WebDriverWait(self.driver, timeout)
        
        # Try different selector strategies
        try:
            # CSS selector
            return wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, selector)))
        except TimeoutException:
            try:
                # XPath
                return wait.until(EC.presence_of_element_located((By.XPATH, selector)))
            except TimeoutException:
                try:
                    # ID
                    return wait.until(EC.presence_of_element_located((By.ID, selector)))
                except TimeoutException:
                    try:
                        # Class name
                        return wait.until(EC.presence_of_element_located((By.CLASS_NAME, selector)))
                    except TimeoutException:
                        raise NoSuchElementException(f"Element not found: {selector}")
                        
    async def _click_element(self, element) -> bool:
        """Click element with human-like behavior."""        try:
            # Scroll to element first
            self.driver.execute_script("arguments[0].scrollIntoView(true);", element)
            await asyncio.sleep(random.uniform(0.5, 1.5))
            
            # Wait until clickable
            wait = WebDriverWait(self.driver, 10)
            clickable_element = wait.until(EC.element_to_be_clickable(element))
            
            # Add random mouse movement before click
            actions = ActionChains(self.driver)
            actions.move_to_element(clickable_element)
            actions.pause(random.uniform(0.1, 0.5))
            actions.click()
            actions.perform()
            
            await asyncio.sleep(random.uniform(0.5, 2))
            return True
            
        except Exception as e:
            self.logger.error(f"Click failed: {e}")
            return False
            
    async def _type_text(self, element, text: str) -> bool:
        """Type text with human-like typing speed."""        try:
            element.clear()
            await asyncio.sleep(random.uniform(0.2, 0.5))
            
            # Type character by character with random delays
            for char in text:
                element.send_keys(char)
                await asyncio.sleep(random.uniform(0.05, 0.2))
                
            await asyncio.sleep(random.uniform(0.5, 1))
            return True
            
        except Exception as e:
            self.logger.error(f"Type failed: {e}")
            return False
            
    async def _clear_element(self, element) -> bool:
        """Clear element content."""        try:
            element.clear()
            return True
        except Exception as e:
            self.logger.error(f"Clear failed: {e}")
            return False
            
    async def _scroll_to_element(self, element) -> bool:
        """Scroll to element."""        try:
            self.driver.execute_script("arguments[0].scrollIntoView(true);", element)
            await asyncio.sleep(random.uniform(0.5, 1.5))
            return True
        except Exception as e:
            self.logger.error(f"Scroll failed: {e}")
            return False
            
    async def _take_screenshot(self, filename: Optional[str] = None) -> str:
        """Take screenshot and return filename."""        try:
            if not filename:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"screenshot_{timestamp}.png"
                
            self.driver.save_screenshot(filename)
            self.logger.info(f"Screenshot saved: {filename}")
            return filename
            
        except Exception as e:
            self.logger.error(f"Screenshot failed: {e}")
            return ""
            
    async def _extract_text(self, element) -> str:
        """Extract text from element."""        try:
            return element.text
        except Exception as e:
            self.logger.error(f"Text extraction failed: {e}")
            return ""
            
    async def _extract_attribute(self, element, attribute: str) -> str:
        """Extract attribute from element."""        try:
            return element.get_attribute(attribute) or ""
        except Exception as e:
            self.logger.error(f"Attribute extraction failed: {e}")
            return ""
            
    async def _extract_html(self, element) -> str:
        """Extract HTML from element."""        try:
            return element.get_attribute('outerHTML') or ""
        except Exception as e:
            self.logger.error(f"HTML extraction failed: {e}")
            return ""
            
    async def _execute_javascript(self, script: str) -> Any:
        """Execute JavaScript code."""        try:
            return self.driver.execute_script(script)
        except Exception as e:
            self.logger.error(f"JavaScript execution failed: {e}")
            return None
            
    async def _hover_element(self, element) -> bool:
        """Hover over element."""        try:
            actions = ActionChains(self.driver)
            actions.move_to_element(element)
            actions.perform()
            await asyncio.sleep(random.uniform(0.5, 1))
            return True
        except Exception as e:
            self.logger.error(f"Hover failed: {e}")
            return False
            
    async def _select_dropdown(self, element, value: str) -> bool:
        """Select dropdown value."""        try:
            from selenium.webdriver.support.ui import Select
            select = Select(element)
            select.select_by_visible_text(value)
            await asyncio.sleep(random.uniform(0.5, 1))
            return True
        except Exception as e:
            self.logger.error(f"Dropdown selection failed: {e}")
            return False
            
    async def _wait_for_element(self, selector: str, timeout: int):
        """Wait for element to appear."""        return await self._find_element(selector, timeout)
        
    async def scroll_page(self, direction: str = 'down', amount: int = 3) -> bool:
        """Scroll page in specified direction."""        try:
            body = self.driver.find_element(By.TAG_NAME, 'body')
            
            for _ in range(amount):
                if direction == 'down':
                    body.send_keys(Keys.PAGE_DOWN)
                elif direction == 'up':
                    body.send_keys(Keys.PAGE_UP)
                elif direction == 'end':
                    body.send_keys(Keys.END)
                elif direction == 'home':
                    body.send_keys(Keys.HOME)
                    
                await asyncio.sleep(random.uniform(0.5, 1.5))
                
            return True
            
        except Exception as e:
            self.logger.error(f"Page scroll failed: {e}")
            return False
            
    async def infinite_scroll(self, max_scrolls: int = 10, 
                            pause_time: float = 2.0) -> int:
        """Perform infinite scroll to load dynamic content."""        scrolls_performed = 0
        last_height = self.driver.execute_script("return document.body.scrollHeight")
        
        for i in range(max_scrolls):
            # Scroll to bottom
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            
            # Wait for new content to load
            await asyncio.sleep(pause_time)
            
            # Check if new content loaded
            new_height = self.driver.execute_script("return document.body.scrollHeight")
            
            if new_height == last_height:
                self.logger.info(f"No new content loaded after {i+1} scrolls")
                break
                
            last_height = new_height
            scrolls_performed += 1
            self.logger.debug(f"Performed scroll {i+1}, new height: {new_height}")
            
        return scrolls_performed
        
    async def extract_all_links(self) -> List[Dict[str, str]]:
        """Extract all links from current page."""        try:
            links = self.driver.find_elements(By.TAG_NAME, 'a')
            
            link_data = []
            for link in links:
                href = link.get_attribute('href')
                text = link.text.strip()
                
                if href:
                    link_data.append({
                        'url': href,
                        'text': text,
                        'title': link.get_attribute('title') or ''
                    })
                    
            return link_data
            
        except Exception as e:
            self.logger.error(f"Link extraction failed: {e}")
            return []
            
    async def extract_all_images(self) -> List[Dict[str, str]]:
        """Extract all images from current page."""        try:
            images = self.driver.find_elements(By.TAG_NAME, 'img')
            
            image_data = []
            for img in images:
                src = img.get_attribute('src')
                
                if src:
                    image_data.append({
                        'src': src,
                        'alt': img.get_attribute('alt') or '',
                        'title': img.get_attribute('title') or '',
                        'width': img.get_attribute('width') or '',
                        'height': img.get_attribute('height') or ''
                    })
                    
            return image_data
            
        except Exception as e:
            self.logger.error(f"Image extraction failed: {e}")
            return []
            
    async def get_page_source(self) -> str:
        """Get current page source."""        try:
            return self.driver.page_source
        except Exception as e:
            self.logger.error(f"Failed to get page source: {e}")
            return ""
            
    async def get_current_url(self) -> str:
        """Get current page URL."""        try:
            return self.driver.current_url
        except Exception as e:
            self.logger.error(f"Failed to get current URL: {e}")
            return ""
            
    async def refresh_page(self):
        """Refresh current page."""        try:
            self.driver.refresh()
            await asyncio.sleep(random.uniform(2, 4))
        except Exception as e:
            self.logger.error(f"Page refresh failed: {e}")
            
    async def go_back(self):
        """Navigate back in browser history."""        try:
            self.driver.back()
            await asyncio.sleep(random.uniform(1, 2))
        except Exception as e:
            self.logger.error(f"Back navigation failed: {e}")
            
    async def go_forward(self):
        """Navigate forward in browser history."""        try:
            self.driver.forward()
            await asyncio.sleep(random.uniform(1, 2))
        except Exception as e:
            self.logger.error(f"Forward navigation failed: {e}")
            
    def is_driver_alive(self) -> bool:
        """Check if driver is still alive."""        if not self.driver:
            return False
            
        try:
            self.driver.current_url
            return True
        except WebDriverException:
            return False
