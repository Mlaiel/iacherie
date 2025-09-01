"""Data Collection Manager - Advanced Multi-Source Data Collection System
Manages comprehensive data collection from multiple sources for competitor monitoring.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: Fahed Mlaiel. All rights reserved.
WARNING: Unauthorized use, copying, or distribution is strictly prohibited.
"""
import asyncio
import aiohttp
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
import json
import re
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
import feedparser
import tweepy
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

try:
    from core.exceptions import CollectionError, RateLimitError
except ImportError:
    # Fallback exception classes
    class ValidationError(Exception): pass
    class ConfigurationError(Exception): pass
    class ProcessingError(Exception): pass
    CollectionError, RateLimitError = globals().get('CollectionError, RateLimitError', Exception)
from ...security.request_manager import SecureRequestManager
from ...utils.rate_limiter import RateLimiter
from ...utils.cache_manager import CacheManager


@dataclass
class DataSource:
    """Data source configuration."""
    source_id: str
    name: str
    source_type: str
    url: str
    api_endpoint: Optional[str]
    credentials: Dict[str, str]
    rate_limit: int
    collection_interval: timedelta
    active: bool
    last_collection: Optional[datetime]
    data_types: List[str]


@dataclass
class CollectedData:
    """Structure for collected data."""
    data_id: str
    source_id: str
    competitor_id: str
    data_type: str
    content: Dict[str, Any]
    metadata: Dict[str, Any]
    collection_timestamp: datetime
    quality_score: float
    processed: bool


class DataCollectionManager:
    """
    Advanced data collection manager for competitor monitoring.
    
    Supports multiple data sources including:
    - Social media platforms
    - Websites and blogs
    - News feeds
    - Financial data
    - Public APIs
    """
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize the data collection manager."""
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Core components
        self.request_manager = SecureRequestManager()
        self.rate_limiter = RateLimiter()
        self.cache_manager = CacheManager()
        
        # Data sources
        self.data_sources: Dict[str, DataSource] = {}
        self.collected_data: List[CollectedData] = []
        
        # Collection settings
        self.max_concurrent_collections = config.get("max_concurrent", 10)
        self.collection_timeout = config.get("timeout", 30)
        self.retry_attempts = config.get("retry_attempts", 3)
        
        # Browser automation
        self.browser_options = self._setup_browser_options()
        
        # Initialize data sources
        asyncio.create_task(self._initialize_data_sources())
        
        self.logger.info("DataCollectionManager initialized")
    
    async def collect_competitor_data(self, competitor_id: str, data_types: List[str] = None) -> List[CollectedData]:
        """Collect data for a specific competitor from all relevant sources."""
        try:
            self.logger.info(f"Starting data collection for competitor: {competitor_id}")
            
            if not data_types:
                data_types = ["website", "social_media", "news", "financial"]
            
            # Get relevant data sources
            relevant_sources = [
                source for source in self.data_sources.values()
                if source.active and any(dt in source.data_types for dt in data_types)
            ]
            
            # Collect data from all sources concurrently
            collection_tasks = []
            for source in relevant_sources:
                if await self._should_collect_from_source(source):
                    task = self._collect_from_source(source, competitor_id, data_types)
                    collection_tasks.append(task)
            
            # Limit concurrent collections
            semaphore = asyncio.Semaphore(self.max_concurrent_collections)
            
            async def limited_collect(task):
                async with semaphore:
                    return await task
            
            # Execute collections
            results = await asyncio.gather(
                *[limited_collect(task) for task in collection_tasks],
                return_exceptions=True
            )
            
            # Process results
            collected_data = []
            for result in results:
                if isinstance(result, Exception):
                    self.logger.error(f"Collection error: {str(result)}")
                    continue
                
                if result:
                    collected_data.extend(result)
            
            # Store collected data
            self.collected_data.extend(collected_data)
            
            # Cache results
            await self._cache_collected_data(competitor_id, collected_data)
            
            self.logger.info(f"Collected {len(collected_data)} data points for competitor {competitor_id}")
            return collected_data
            
        except Exception as e:
            self.logger.error(f"Error collecting competitor data: {str(e)}")
            raise CollectionError(f"Failed to collect data for competitor {competitor_id}: {str(e)}")
    
    async def collect_website_data(self, competitor_id: str, website_url: str) -> List[CollectedData]:
        """Collect data from competitor website."""
        try:
            collected_data = []
            
            # Collect main website data
            main_data = await self._collect_main_website_data(competitor_id, website_url)
            if main_data:
                collected_data.append(main_data)
            
            # Collect blog/news data
            blog_data = await self._collect_blog_data(competitor_id, website_url)
            collected_data.extend(blog_data)
            
            # Collect product/service data
            product_data = await self._collect_product_data(competitor_id, website_url)
            collected_data.extend(product_data)
            
            # Collect pricing data
            pricing_data = await self._collect_pricing_data(competitor_id, website_url)
            if pricing_data:
                collected_data.append(pricing_data)
            
            return collected_data
            
        except Exception as e:
            self.logger.error(f"Error collecting website data: {str(e)}")
            return []
    
    async def collect_social_media_data(self, competitor_id: str, platforms: Dict[str, str]) -> List[CollectedData]:
        """Collect data from social media platforms."""
        try:
            collected_data = []
            
            for platform, profile_url in platforms.items():
                try:
                    platform_data = await self._collect_platform_data(competitor_id, platform, profile_url)
                    collected_data.extend(platform_data)
                    
                    # Respect rate limits
                    await asyncio.sleep(1)
                    
                except RateLimitError:
                    self.logger.warning(f"Rate limit reached for {platform}")
                    continue
                except Exception as e:
                    self.logger.error(f"Error collecting {platform} data: {str(e)}")
                    continue
            
            return collected_data
            
        except Exception as e:
            self.logger.error(f"Error collecting social media data: {str(e)}")
            return []
    
    async def collect_news_data(self, competitor_id: str, competitor_name: str) -> List[CollectedData]:
        """Collect news and media mentions."""
        try:
            collected_data = []
            
            # Search terms
            search_terms = [
                competitor_name,
                f'"{competitor_name}"',
                f"{competitor_name} company",
                f"{competitor_name} startup"
            ]
            
            # News sources
            news_sources = [
                "https://newsapi.org/v2/everything",
                "https://api.bing.microsoft.com/v7.0/news/search",
                "https://rss.cnn.com/rss/edition.rss",
                "https://feeds.reuters.com/reuters/businessNews"
            ]
            
            for term in search_terms:
                for source in news_sources:
                    try:
                        news_items = await self._collect_news_from_source(source, term)
                        
                        for item in news_items:
                            data = CollectedData(
                                data_id=f"news_{competitor_id}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
                                source_id=source,
                                competitor_id=competitor_id,
                                data_type="news",
                                content=item,
                                metadata={
                                    "search_term": term,
                                    "source_type": "news_feed"
                                },
                                collection_timestamp=datetime.utcnow(),
                                quality_score=await self._calculate_quality_score(item),
                                processed=False
                            )
                            collected_data.append(data)
                    
                    except Exception as e:
                        self.logger.error(f"Error collecting news from {source}: {str(e)}")
                        continue
                
                # Respect rate limits between searches
                await asyncio.sleep(2)
            
            return collected_data
            
        except Exception as e:
            self.logger.error(f"Error collecting news data: {str(e)}")
            return []
    
    async def collect_financial_data(self, competitor_id: str, company_info: Dict[str, Any]) -> List[CollectedData]:
        """Collect financial and business data."""
        try:
            collected_data = []
            
            # Company identifiers
            company_name = company_info.get("name", "")
            ticker = company_info.get("ticker")
            domain = company_info.get("domain", "")
            
            # Collect funding data
            funding_data = await self._collect_funding_data(company_name, domain)
            if funding_data:
                data = CollectedData(
                    data_id=f"funding_{competitor_id}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
                    source_id="crunchbase",
                    competitor_id=competitor_id,
                    data_type="financial",
                    content=funding_data,
                    metadata={"data_subtype": "funding"},
                    collection_timestamp=datetime.utcnow(),
                    quality_score=0.8,
                    processed=False
                )
                collected_data.append(data)
            
            # Collect stock data if public company
            if ticker:
                stock_data = await self._collect_stock_data(ticker)
                if stock_data:
                    data = CollectedData(
                        data_id=f"stock_{competitor_id}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
                        source_id="yahoo_finance",
                        competitor_id=competitor_id,
                        data_type="financial",
                        content=stock_data,
                        metadata={"data_subtype": "stock"},
                        collection_timestamp=datetime.utcnow(),
                        quality_score=0.9,
                        processed=False
                    )
                    collected_data.append(data)
            
            # Collect job postings data
            jobs_data = await self._collect_jobs_data(company_name)
            if jobs_data:
                data = CollectedData(
                    data_id=f"jobs_{competitor_id}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
                    source_id="linkedin_jobs",
                    competitor_id=competitor_id,
                    data_type="business",
                    content=jobs_data,
                    metadata={"data_subtype": "hiring"},
                    collection_timestamp=datetime.utcnow(),
                    quality_score=0.7,
                    processed=False
                )
                collected_data.append(data)
            
            return collected_data
            
        except Exception as e:
            self.logger.error(f"Error collecting financial data: {str(e)}")
            return []
    
    async def _collect_from_source(self, source: DataSource, competitor_id: str, data_types: List[str]) -> List[CollectedData]:
        """Collect data from a specific source."""
        try:
            # Check rate limits
            if not await self.rate_limiter.can_proceed(source.source_id, source.rate_limit):
                raise RateLimitError(f"Rate limit exceeded for source {source.name}")
            
            collected_data = []
            
            if source.source_type == "website":
                data = await self.collect_website_data(competitor_id, source.url)
                collected_data.extend(data)
                
            elif source.source_type == "social_media":
                platforms = {source.name.lower(): source.url}
                data = await self.collect_social_media_data(competitor_id, platforms)
                collected_data.extend(data)
                
            elif source.source_type == "news_feed":
                company_name = source.url  # In this case, URL contains company name
                data = await self.collect_news_data(competitor_id, company_name)
                collected_data.extend(data)
                
            elif source.source_type == "api":
                data = await self._collect_api_data(source, competitor_id)
                collected_data.extend(data)
            
            # Update last collection time
            source.last_collection = datetime.utcnow()
            
            return collected_data
            
        except Exception as e:
            self.logger.error(f"Error collecting from source {source.name}: {str(e)}")
            return []
    
    async def _collect_main_website_data(self, competitor_id: str, website_url: str) -> Optional[CollectedData]:
        """Collect main website information."""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(website_url, timeout=self.collection_timeout) as response:
                    if response.status == 200:
                        html_content = await response.text()
                        
                        # Parse HTML
                        soup = BeautifulSoup(html_content, 'html.parser')
                        
                        # Extract structured data
                        website_data = {
                            "title": soup.title.string if soup.title else "",
                            "meta_description": self._get_meta_description(soup),
                            "keywords": self._get_meta_keywords(soup),
                            "headings": self._extract_headings(soup),
                            "images": self._extract_images(soup),
                            "links": self._extract_links(soup, website_url),
                            "text_content": soup.get_text()[:5000],  # First 5000 chars
                            "structure": self._analyze_page_structure(soup),
                            "technologies": self._detect_technologies(html_content),
                            "contact_info": self._extract_contact_info(soup)
                        }
                        
                        return CollectedData(
                            data_id=f"website_{competitor_id}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
                            source_id=website_url,
                            competitor_id=competitor_id,
                            data_type="website",
                            content=website_data,
                            metadata={
                                "url": website_url,
                                "status_code": response.status,
                                "content_type": response.content_type
                            },
                            collection_timestamp=datetime.utcnow(),
                            quality_score=await self._calculate_quality_score(website_data),
                            processed=False
                        )
        
        except Exception as e:
            self.logger.error(f"Error collecting main website data: {str(e)}")
            return None
    
    async def _collect_platform_data(self, competitor_id: str, platform: str, profile_url: str) -> List[CollectedData]:
        """Collect data from a specific social media platform."""
        try:
            collected_data = []
            
            if platform.lower() == "twitter":
                data = await self._collect_twitter_data(competitor_id, profile_url)
                collected_data.extend(data)
                
            elif platform.lower() == "linkedin":
                data = await self._collect_linkedin_data(competitor_id, profile_url)
                collected_data.extend(data)
                
            elif platform.lower() == "instagram":
                data = await self._collect_instagram_data(competitor_id, profile_url)
                collected_data.extend(data)
                
            elif platform.lower() == "youtube":
                data = await self._collect_youtube_data(competitor_id, profile_url)
                collected_data.extend(data)
                
            elif platform.lower() == "facebook":
                data = await self._collect_facebook_data(competitor_id, profile_url)
                collected_data.extend(data)
            
            return collected_data
            
        except Exception as e:
            self.logger.error(f"Error collecting {platform} data: {str(e)}")
            return []
    
    def _setup_browser_options(self) -> Options:
        """Setup Chrome browser options for web scraping."""
        options = Options()
        options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu")
        options.add_argument("--window-size=1920,1080")
        options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")
        return options
    
    async def _calculate_quality_score(self, data: Dict[str, Any]) -> float:
        """Calculate quality score for collected data."""
        try:
            score = 0.5  # Base score
            
            # Check data completeness
            if data and len(data) > 0:
                score += 0.2
            
            # Check for rich content
            if isinstance(data, dict):
                if len(data.keys()) > 5:
                    score += 0.1
                    
                # Check for specific valuable fields
                valuable_fields = ["title", "description", "content", "metrics", "engagement"]
                for field in valuable_fields:
                    if field in data and data[field]:
                        score += 0.04
            
            return min(1.0, score)
            
        except Exception:
            return 0.5
    
    async def get_collection_status(self) -> Dict[str, Any]:
        """Get current collection status and metrics."""
        return {
            "total_sources": len(self.data_sources),
            "active_sources": len([s for s in self.data_sources.values() if s.active]),
            "total_collected": len(self.collected_data),
            "recent_collections": len([d for d in self.collected_data 
                                    if d.collection_timestamp > datetime.utcnow() - timedelta(hours=24)]),
            "average_quality": sum(d.quality_score for d in self.collected_data) / len(self.collected_data) if self.collected_data else 0,
            "last_collection": max([d.collection_timestamp for d in self.collected_data]) if self.collected_data else None
        }
