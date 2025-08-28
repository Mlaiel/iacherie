"""
Data collection utility classes
Mock implementations for essential data harvester dependencies
"""

import asyncio
import time
from typing import Dict, Any, List, Optional
from datetime import datetime
import logging


class RateLimiter:
    """Simple rate limiter for controlling request frequency"""
    
    def __init__(self, rate_limit: float = 1.0, max_burst: int = 5):
        self.rate_limit = rate_limit  # seconds between requests
        self.max_burst = max_burst
        self.last_request = 0.0
        self.request_count = 0
        self.logger = logging.getLogger(__name__)
    
    async def acquire(self):
        """Acquire permission to make a request"""
        current_time = time.time()
        time_since_last = current_time - self.last_request
        
        if time_since_last < self.rate_limit:
            sleep_time = self.rate_limit - time_since_last
            self.logger.debug(f"Rate limiting: sleeping for {sleep_time:.2f}s")
            await asyncio.sleep(sleep_time)
        
        self.last_request = time.time()
        self.request_count += 1


class DataValidator:
    """Simple data validator for harvested data"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def validate(self, data: Dict[str, Any], schema: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Validate data against a schema
        
        Args:
            data: Data to validate
            schema: Validation schema (optional)
            
        Returns:
            Validated data
        """
        if not schema:
            return data
        
        validated = {}
        
        for field, rules in schema.items():
            if field in data:
                value = data[field]
                
                # Type validation
                expected_type = rules.get('type')
                if expected_type:
                    if expected_type == 'string' and not isinstance(value, str):
                        continue
                    elif expected_type == 'number' and not isinstance(value, (int, float)):
                        continue
                    elif expected_type == 'list' and not isinstance(value, list):
                        continue
                    elif expected_type == 'dict' and not isinstance(value, dict):
                        continue
                
                # Required validation
                if rules.get('required', False) and not value:
                    continue
                
                # Length validation for strings
                if isinstance(value, str):
                    min_length = rules.get('min_length', 0)
                    max_length = rules.get('max_length', float('inf'))
                    if not (min_length <= len(value) <= max_length):
                        continue
                
                validated[field] = value
            elif rules.get('required', False):
                # Required field missing
                self.logger.warning(f"Required field missing: {field}")
        
        # Include non-schema fields
        for field, value in data.items():
            if field not in validated:
                validated[field] = value
        
        return validated


class ContentAnalyzer:
    """Simple content analyzer for text and media analysis"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    async def analyze_text(self, text: str) -> Dict[str, Any]:
        """
        Analyze text content
        
        Args:
            text: Text to analyze
            
        Returns:
            Analysis results
        """
        if not text:
            return {}
        
        # Basic text analysis
        analysis = {
            'length': len(text),
            'word_count': len(text.split()),
            'language': 'auto-detected',
            'sentiment': 'neutral',
            'topics': [],
            'entities': [],
            'readability_score': 0.5
        }
        
        # Simple keyword extraction
        words = text.lower().split()
        word_freq = {}
        for word in words:
            if len(word) > 3:  # Only longer words
                word_freq[word] = word_freq.get(word, 0) + 1
        
        # Get top keywords
        top_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)[:5]
        analysis['keywords'] = [word for word, freq in top_words]
        
        # Basic sentiment analysis (mock)
        positive_words = ['good', 'great', 'excellent', 'amazing', 'wonderful', 'fantastic']
        negative_words = ['bad', 'terrible', 'awful', 'horrible', 'disappointing']
        
        positive_count = sum(1 for word in positive_words if word in text.lower())
        negative_count = sum(1 for word in negative_words if word in text.lower())
        
        if positive_count > negative_count:
            analysis['sentiment'] = 'positive'
        elif negative_count > positive_count:
            analysis['sentiment'] = 'negative'
        
        return analysis
    
    async def analyze_image(self, image_url: str) -> Dict[str, Any]:
        """
        Analyze image content
        
        Args:
            image_url: URL of image to analyze
            
        Returns:
            Analysis results
        """
        # Mock image analysis
        analysis = {
            'url': image_url,
            'format': self._detect_image_format(image_url),
            'estimated_size': 'medium',
            'objects_detected': [],
            'text_detected': '',
            'colors': ['#000000', '#FFFFFF'],
            'quality_score': 0.8
        }
        
        return analysis
    
    def _detect_image_format(self, url: str) -> str:
        """Detect image format from URL"""
        url_lower = url.lower()
        if '.jpg' in url_lower or '.jpeg' in url_lower:
            return 'jpeg'
        elif '.png' in url_lower:
            return 'png'
        elif '.gif' in url_lower:
            return 'gif'
        elif '.webp' in url_lower:
            return 'webp'
        else:
            return 'unknown'


class DataTransformer:
    """Data transformation utilities"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def normalize_text(self, text: str) -> str:
        """Normalize text content"""
        if not text:
            return ""
        
        # Basic normalization
        normalized = text.strip()
        normalized = ' '.join(normalized.split())  # Remove extra whitespace
        return normalized
    
    def extract_urls(self, text: str) -> List[str]:
        """Extract URLs from text"""
        import re
        url_pattern = r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
        return re.findall(url_pattern, text)
    
    def extract_hashtags(self, text: str) -> List[str]:
        """Extract hashtags from text"""
        import re
        hashtag_pattern = r'#\w+'
        return re.findall(hashtag_pattern, text)
    
    def extract_mentions(self, text: str) -> List[str]:
        """Extract mentions from text"""
        import re
        mention_pattern = r'@\w+'
        return re.findall(mention_pattern, text)


class ProxyManager:
    """Simple proxy manager for web requests"""
    
    def __init__(self, proxies: List[str] = None):
        self.proxies = proxies or []
        self.current_proxy_index = 0
        self.logger = logging.getLogger(__name__)
    
    def get_proxy(self) -> Optional[str]:
        """Get next proxy in rotation"""
        if not self.proxies:
            return None
        
        proxy = self.proxies[self.current_proxy_index]
        self.current_proxy_index = (self.current_proxy_index + 1) % len(self.proxies)
        return proxy
    
    def add_proxy(self, proxy: str):
        """Add a proxy to the pool"""
        if proxy not in self.proxies:
            self.proxies.append(proxy)
    
    def remove_proxy(self, proxy: str):
        """Remove a proxy from the pool"""
        if proxy in self.proxies:
            self.proxies.remove(proxy)