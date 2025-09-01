"""Specialized Rate Limiters for Crawler Platforms
=================================================

Rate limiting utilities for different crawler platform types to respect
API limits and avoid being blocked.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: All rights reserved.
"""
import asyncio
import time
from typing import Dict
from datetime import datetime, timedelta


class EcommerceRateLimiter:
    """Rate limiter for e-commerce platform crawling."""
    
    def __init__(self):
        self.platform_limits = {
            'amazon': {'requests_per_minute': 30, 'requests_per_hour': 500},
            'ebay': {'requests_per_minute': 60, 'requests_per_hour': 1000},
            'etsy': {'requests_per_minute': 40, 'requests_per_hour': 800}
        }
        self.usage_tracking = {}
        self.last_request_time = {}
    
    async def wait_if_needed(self, platform: str):
        """Wait if rate limit would be exceeded."""
        if platform not in self.platform_limits:
            return
        
        current_time = time.time()
        last_time = self.last_request_time.get(platform, 0)
        
        # Minimum delay between requests
        min_delay = 60.0 / self.platform_limits[platform]['requests_per_minute']
        time_since_last = current_time - last_time
        
        if time_since_last < min_delay:
            await asyncio.sleep(min_delay - time_since_last)
    
    async def update_usage(self, platform: str, request_count: int):
        """Update usage tracking."""
        self.last_request_time[platform] = time.time()
        if platform not in self.usage_tracking:
            self.usage_tracking[platform] = []
        
        self.usage_tracking[platform].append({
            'timestamp': datetime.utcnow(),
            'count': request_count
        })


class EducationalRateLimiter:
    """Rate limiter for educational platform crawling."""
    
    def __init__(self):
        self.platform_limits = {
            'coursera': {'requests_per_minute': 20, 'requests_per_hour': 400},
            'udemy': {'requests_per_minute': 30, 'requests_per_hour': 600},
            'khan_academy': {'requests_per_minute': 40, 'requests_per_hour': 800},
            'edx': {'requests_per_minute': 25, 'requests_per_hour': 500}
        }
        self.usage_tracking = {}
        self.last_request_time = {}
    
    async def wait_if_needed(self, platform: str):
        """Wait if rate limit would be exceeded."""
        if platform not in self.platform_limits:
            return
        
        current_time = time.time()
        last_time = self.last_request_time.get(platform, 0)
        
        min_delay = 60.0 / self.platform_limits[platform]['requests_per_minute']
        time_since_last = current_time - last_time
        
        if time_since_last < min_delay:
            await asyncio.sleep(min_delay - time_since_last)
    
    async def update_usage(self, platform: str, request_count: int):
        """Update usage tracking."""
        self.last_request_time[platform] = time.time()
        if platform not in self.usage_tracking:
            self.usage_tracking[platform] = []
        
        self.usage_tracking[platform].append({
            'timestamp': datetime.utcnow(),
            'count': request_count
        })


class NewsRateLimiter:
    """Rate limiter for news platform crawling."""
    
    def __init__(self):
        self.platform_limits = {
            'cnn': {'requests_per_minute': 30, 'requests_per_hour': 600},
            'bbc': {'requests_per_minute': 25, 'requests_per_hour': 500},
            'reuters': {'requests_per_minute': 20, 'requests_per_hour': 400},
            'ap_news': {'requests_per_minute': 15, 'requests_per_hour': 300},
            'guardian': {'requests_per_minute': 25, 'requests_per_hour': 500}
        }
        self.usage_tracking = {}
        self.last_request_time = {}
    
    async def wait_if_needed(self, platform: str):
        """Wait if rate limit would be exceeded."""
        if platform not in self.platform_limits:
            return
        
        current_time = time.time()
        last_time = self.last_request_time.get(platform, 0)
        
        min_delay = 60.0 / self.platform_limits[platform]['requests_per_minute']
        time_since_last = current_time - last_time
        
        if time_since_last < min_delay:
            await asyncio.sleep(min_delay - time_since_last)
    
    async def update_usage(self, platform: str, request_count: int):
        """Update usage tracking."""
        self.last_request_time[platform] = time.time()
        if platform not in self.usage_tracking:
            self.usage_tracking[platform] = []
        
        self.usage_tracking[platform].append({
            'timestamp': datetime.utcnow(),
            'count': request_count
        })


class PodcastRateLimiter:
    """Rate limiter for podcast platform crawling."""
    
    def __init__(self):
        self.platform_limits = {
            'spotify': {'requests_per_minute': 20, 'requests_per_hour': 400},
            'apple_podcasts': {'requests_per_minute': 30, 'requests_per_hour': 600},
            'google_podcasts': {'requests_per_minute': 25, 'requests_per_hour': 500},
            'podcast_index': {'requests_per_minute': 40, 'requests_per_hour': 800}
        }
        self.usage_tracking = {}
        self.last_request_time = {}
    
    async def wait_if_needed(self, platform: str):
        """Wait if rate limit would be exceeded."""
        if platform not in self.platform_limits:
            return
        
        current_time = time.time()
        last_time = self.last_request_time.get(platform, 0)
        
        min_delay = 60.0 / self.platform_limits[platform]['requests_per_minute']
        time_since_last = current_time - last_time
        
        if time_since_last < min_delay:
            await asyncio.sleep(min_delay - time_since_last)
    
    async def update_usage(self, platform: str, request_count: int):
        """Update usage tracking."""
        self.last_request_time[platform] = time.time()
        if platform not in self.usage_tracking:
            self.usage_tracking[platform] = []
        
        self.usage_tracking[platform].append({
            'timestamp': datetime.utcnow(),
            'count': request_count
        })


class GenericRateLimiter:
    """Generic rate limiter for general web crawling."""
    
    def __init__(self, requests_per_minute: int = 30, requests_per_hour: int = 600):
        self.requests_per_minute = requests_per_minute
        self.requests_per_hour = requests_per_hour
        self.usage_tracking = {}
        self.last_request_time = {}
    
    async def wait_if_needed(self, domain: str):
        """Wait if rate limit would be exceeded."""
        current_time = time.time()
        last_time = self.last_request_time.get(domain, 0)
        
        min_delay = 60.0 / self.requests_per_minute
        time_since_last = current_time - last_time
        
        if time_since_last < min_delay:
            await asyncio.sleep(min_delay - time_since_last)
    
    async def update_usage(self, domain: str, request_count: int):
        """Update usage tracking."""
        self.last_request_time[domain] = time.time()
        if domain not in self.usage_tracking:
            self.usage_tracking[domain] = []
        
        self.usage_tracking[domain].append({
            'timestamp': datetime.utcnow(),
            'count': request_count
        })


class RedditRateLimiter:
    """Rate limiter specific for Reddit API."""
    
    def __init__(self):
        # Reddit API allows 60 requests per minute for authenticated users
        self.requests_per_minute = 60
        self.requests_per_hour = 3600
        self.usage_tracking = []
        self.last_request_time = 0
    
    async def acquire(self):
        """Acquire permission to make a request."""
        current_time = time.time()
        min_delay = 60.0 / self.requests_per_minute
        time_since_last = current_time - self.last_request_time
        
        if time_since_last < min_delay:
            await asyncio.sleep(min_delay - time_since_last)
        
        self.last_request_time = time.time()
    
    def get_status(self) -> Dict:
        """Get current rate limiter status."""
        return {
            'requests_per_minute': self.requests_per_minute,
            'last_request': self.last_request_time,
            'usage_count': len(self.usage_tracking)
        }