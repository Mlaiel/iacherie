"""Advanced Scrapers Index - IA-Influencer-Agent
==============================================

Central index for professional web scraping components.
Provides unified access to all scraping functionalities.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: All rights reserved. Unauthorized use, reproduction, or distribution prohibited.

⚠️ CRITICAL LEGAL WARNING ⚠️
UNAUTHORIZED USE, COPYING, OR DISTRIBUTION IS STRICTLY PROHIBITED AND WILL RESULT IN IMMEDIATE LEGAL ACTION.
This technology is EXCLUSIVE property of Fahed Mlaiel. Contact: mlaiel@live.de for licensing.

Team Specializations:
- Lead AI Developer & Backend Senior Engineer
- ML Engineering & Data Science Expert  
- Database Administrator & Security Specialist
- Microservices Architect & DevOps Engineer
- AI Prompt Engineer & Content Protection Specialist
- Audio Processing & Digital Rights Management Expert
"""

from .web_scraper import WebScraper
from .content_scraper import ContentScraper
from .platform_scraper import PlatformScraper
from .stealth_scraper import StealthScraper
from .batch_scraper import BatchScraper
from .realtime_scraper import RealtimeScraper
from .social_scraper import SocialScraper
from .media_scraper import MediaScraper
from .selenium_scraper import SeleniumScraper
from .api_scraper import ApiScraper
from .proxy_scraper import ProxyScraper
from .mobile_scraper import MobileScraper

import logging
from typing import Dict, Any, Optional, Union

__all__ = [
    'ScrapersManager',
    'WebScraper',
    'ContentScraper',
    'PlatformScraper',
    'StealthScraper',
    'BatchScraper',
    'RealtimeScraper',
    'SocialScraper',
    'MediaScraper',
    'SeleniumScraper',
    'ApiScraper',
    'ProxyScraper',
    'MobileScraper'
]

class ScrapersManager:
    """
    Central manager for all scraping components.
    
    Provides unified access to all available scrapers with proper
    initialization and resource management.
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Initialize all scrapers
        self.web_scraper = WebScraper()
        self.content_scraper = ContentScraper()
        self.platform_scraper = PlatformScraper()
        self.stealth_scraper = StealthScraper()
        self.batch_scraper = BatchScraper()
        self.realtime_scraper = RealtimeScraper()
        self.social_scraper = SocialScraper()
        self.media_scraper = MediaScraper()
        self.selenium_scraper = SeleniumScraper()
        self.api_scraper = ApiScraper()
        self.proxy_scraper = ProxyScraper()
        self.mobile_scraper = MobileScraper()
        
        self.logger.info("ScrapersManager initialized with all scraping components")
        
    def get_scraper(self, scraper_type: str) -> Optional[Any]:
        """Get specific scraper by type."""
        scrapers = {
            'web': self.web_scraper,
            'content': self.content_scraper,
            'platform': self.platform_scraper,
            'stealth': self.stealth_scraper,
            'batch': self.batch_scraper,
            'realtime': self.realtime_scraper,
            'social': self.social_scraper,
            'media': self.media_scraper,
            'selenium': self.selenium_scraper,
            'api': self.api_scraper,
            'proxy': self.proxy_scraper,
            'mobile': self.mobile_scraper
        }
        return scrapers.get(scraper_type.lower())
        
    def get_all_scrapers(self) -> Dict[str, Any]:
        """
Get all available scrapers."""
        return {
            'web': self.web_scraper,
            'content': self.content_scraper,
            'platform': self.platform_scraper,
            'stealth': self.stealth_scraper,
            'batch': self.batch_scraper,
            'realtime': self.realtime_scraper,
            'social': self.social_scraper,
            'media': self.media_scraper,
            'selenium': self.selenium_scraper,
            'api': self.api_scraper,
            'proxy': self.proxy_scraper,
            'mobile': self.mobile_scraper
        }
        
    def list_available_scrapers(self) -> list:
        """
List all available scraper types."""
        return ['web', 'content', 'platform', 'stealth', 'batch', 'realtime', 
                'social', 'media', 'selenium', 'api', 'proxy', 'mobile']
