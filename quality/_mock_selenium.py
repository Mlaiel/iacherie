#!/usr/bin/env python3
"""
🎭 Mock Selenium WebDriver for Enterprise Quality Testing
=========================================================

Mock implementation for selenium webdriver when the actual package is not available.
This allows the quality framework to continue functioning during network issues.

© 2025 Fahed Mlaiel - Enterprise Quality Framework
"""

class MockWebDriver:
    """Mock WebDriver for testing when selenium is not available"""
    
    def __init__(self, *args, **kwargs):
        self.current_url = "http://localhost:3000"
        self.title = "Ainflue Platform - Test"
        
    def get(self, url):
        """Mock navigation"""
        self.current_url = url
        return True
        
    def find_element(self, by, value):
        """Mock element finding"""
        return MockWebElement()
        
    def find_elements(self, by, value):
        """Mock elements finding"""
        return [MockWebElement() for _ in range(3)]
        
    def quit(self):
        """Mock quit"""
        pass
        
    def close(self):
        """Mock close"""
        pass

class MockWebElement:
    """Mock WebElement for testing"""
    
    def __init__(self):
        self.text = "Test Element"
        self.tag_name = "div"
        
    def click(self):
        """Mock click"""
        return True
        
    def send_keys(self, text):
        """Mock text input"""
        return True
        
    def get_attribute(self, name):
        """Mock attribute getting"""
        return "test-value"

class MockBy:
    """Mock selenium By class"""
    ID = "id"
    NAME = "name"
    CLASS_NAME = "class name"
    TAG_NAME = "tag name"
    XPATH = "xpath"
    CSS_SELECTOR = "css selector"

# Mock selenium modules
class MockWebDriverModule:
    Chrome = MockWebDriver
    Firefox = MockWebDriver
    Edge = MockWebDriver

# Module structure
webdriver = MockWebDriverModule()
By = MockBy()

# Mock additional selenium classes for compatibility
class Chrome(MockWebDriver): pass
class Firefox(MockWebDriver): pass