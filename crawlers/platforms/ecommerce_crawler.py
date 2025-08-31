"""E-commerce Platform Crawler
==============================

Specialized crawler for e-commerce product monitoring and derived product tracking.
Monitors products across Amazon, eBay, Etsy and other e-commerce platforms.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: All rights reserved. Unauthorized use, reproduction, or distribution prohibited.

WARNING: This code is protected by copyright law. Any unauthorized copying, 
distribution, or modification is strictly prohibited and will result in 
legal action. Contact mlaiel@live.de for licensing.

Features:
- Multi-platform product monitoring (Amazon, eBay, Etsy)
- Price tracking and availability monitoring
- Product derivative detection
- Review and rating tracking
- Seller monitoring and verification
- Product image fingerprinting
- Category and trend analysis
"""
import asyncio
import logging
from typing import Dict, List, Optional, Union, AsyncGenerator
from datetime import datetime, timedelta
from dataclasses import dataclass
import json
import re
from urllib.parse import urljoin, urlparse, parse_qs
import hashlib

import aiohttp
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from ..utils.specialized_rate_limiters import EcommerceRateLimiter
from ..utils.proxy_manager import ProxyManager
from ..utils.user_agent_rotator import UserAgentRotator
from ...core.config import get_settings
from ...core.exceptions import CrawlerError, RateLimitError
from ...database.models import CrawlResult, ContentMatch

logger = logging.getLogger(__name__)
settings = get_settings()

@dataclass
class EcommerceProduct:
    """E-commerce product data structure."""
    product_id: str
    platform: str
    title: str
    description: str
    price: Optional[str]
    currency: str
    availability: str
    seller_name: str
    seller_rating: Optional[float]
    product_rating: Optional[float]
    review_count: int
    category: str
    brand: Optional[str]
    url: str
    image_urls: List[str]
    specifications: Dict[str, str]
    shipping_info: Dict[str, str]
    last_updated: datetime
    price_history: List[Dict]
    similar_products: List[str]
    product_fingerprint: str

@dataclass
class EcommerceSeller:
    """E-commerce seller data structure."""
    seller_id: str
    platform: str
    name: str
    rating: float
    review_count: int
    store_url: str
    verified: bool
    join_date: Optional[datetime]
    location: Optional[str]
    product_count: int
    categories: List[str]

class EcommerceCrawler:
    """
    Professional e-commerce platform crawler for product monitoring.
    
    Features:
    - Multi-platform support (Amazon, eBay, Etsy)
    - Product derivative detection
    - Price tracking and monitoring
    - Seller verification and monitoring
    - Product image fingerprinting
    - Category trend analysis
    """
    
    def __init__(self):
        """Initialize e-commerce crawler."""
        self.rate_limiter = EcommerceRateLimiter()
        self.proxy_manager = ProxyManager()
        self.user_agent_rotator = UserAgentRotator()
        self.session = None
        
        # Crawler configuration
        self.max_redirects = 5
        self.timeout = 30
        self.max_content_size = 10 * 1024 * 1024  # 10MB
        
        # Platform configurations
        self.platforms = {
            'amazon': {
                'base_url': 'https://www.amazon.com',
                'search_endpoint': '/s',
                'product_selectors': {
                    'title': '[data-component-type="s-search-result"] h2 a span',
                    'price': '.a-price-whole, .a-offscreen',
                    'rating': '.a-icon-alt',
                    'image': '.s-image',
                    'availability': '.a-size-base-plus'
                }
            },
            'ebay': {
                'base_url': 'https://www.ebay.com',
                'search_endpoint': '/sch',
                'product_selectors': {
                    'title': '.s-item__title',
                    'price': '.s-item__price',
                    'shipping': '.s-item__shipping',
                    'image': '.s-item__image'
                }
            },
            'etsy': {
                'base_url': 'https://www.etsy.com',
                'search_endpoint': '/search',
                'product_selectors': {
                    'title': '.listing-link',
                    'price': '.currency-value',
                    'seller': '.shop-name',
                    'image': '.listing-page-image'
                }
            }
        }
        
        # Selenium configuration
        self.selenium_options = webdriver.ChromeOptions()
        self.selenium_options.add_argument('--headless')
        self.selenium_options.add_argument('--no-sandbox')
        self.selenium_options.add_argument('--disable-dev-shm-usage')
        self.selenium_options.add_argument('--disable-gpu')
        self.selenium_options.add_argument('--disable-blink-features=AutomationControlled')
    
    async def __aenter__(self):
        """Async context manager entry."""
        headers = {
            'User-Agent': self.user_agent_rotator.get_user_agent(),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        }
        
        connector = aiohttp.TCPConnector(limit=100, limit_per_host=10)
        timeout = aiohttp.ClientTimeout(total=self.timeout)
        
        self.session = aiohttp.ClientSession(
            headers=headers,
            connector=connector,
            timeout=timeout
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if self.session:
            await self.session.close()
    
    async def search_products(
        self,
        query: str,
        platform: str,
        max_results: int = 50,
        price_range: Optional[tuple] = None
    ) -> List[EcommerceProduct]:
        """
        Search for products on a specific e-commerce platform.
        
        Args:
            query: Search query
            platform: Platform to search ('amazon', 'ebay', 'etsy')
            max_results: Maximum results to return
            price_range: Optional price range filter (min_price, max_price)
            
        Returns:
            List of matching products
        """
        try:
            # Check rate limiting
            await self.rate_limiter.wait_if_needed(platform)
            
            if platform not in self.platforms:
                raise CrawlerError(f"Unsupported platform: {platform}")
            
            platform_config = self.platforms[platform]
            search_url = self._build_search_url(platform, query, price_range)
            
            products = []
            if platform == 'amazon':
                products = await self._search_amazon(search_url, max_results)
            elif platform == 'ebay':
                products = await self._search_ebay(search_url, max_results)
            elif platform == 'etsy':
                products = await self._search_etsy(search_url, max_results)
            
            # Update rate limiter
            await self.rate_limiter.update_usage(platform, len(products))
            
            return products
            
        except Exception as e:
            logger.error(f"Product search failed for {platform}: {e}")
            return []
    
    async def monitor_product(self, product_url: str, platform: str) -> Optional[EcommerceProduct]:
        """
        Monitor a specific product for changes.
        
        Args:
            product_url: Product URL to monitor
            platform: Platform name
            
        Returns:
            Updated product information
        """
        try:
            await self.rate_limiter.wait_if_needed(platform)
            
            if platform == 'amazon':
                return await self._monitor_amazon_product(product_url)
            elif platform == 'ebay':
                return await self._monitor_ebay_product(product_url)
            elif platform == 'etsy':
                return await self._monitor_etsy_product(product_url)
            else:
                raise CrawlerError(f"Unsupported platform for monitoring: {platform}")
            
        except Exception as e:
            logger.error(f"Product monitoring failed for {product_url}: {e}")
            return None
    
    async def detect_derivative_products(
        self,
        original_product: EcommerceProduct,
        similarity_threshold: float = 0.8
    ) -> List[EcommerceProduct]:
        """
        Detect derivative/copycat products based on original product.
        
        Args:
            original_product: Original product to check against
            similarity_threshold: Minimum similarity score for detection
            
        Returns:
            List of potential derivative products
        """
        try:
            derivative_products = []
            
            # Generate search queries from original product
            search_queries = self._generate_derivative_search_queries(original_product)
            
            # Search across all platforms
            for platform in self.platforms.keys():
                for query in search_queries:
                    search_results = await self.search_products(
                        query=query,
                        platform=platform,
                        max_results=20
                    )
                    
                    for product in search_results:
                        # Skip if same product
                        if product.url == original_product.url:
                            continue
                        
                        # Calculate similarity
                        similarity = await self._calculate_product_similarity(
                            original_product, product
                        )
                        
                        if similarity >= similarity_threshold:
                            product.similarity_score = similarity
                            derivative_products.append(product)
            
            # Remove duplicates and sort by similarity
            unique_derivatives = self._deduplicate_products(derivative_products)
            unique_derivatives.sort(key=lambda x: getattr(x, 'similarity_score', 0), reverse=True)
            
            logger.info(f"Found {len(unique_derivatives)} potential derivative products")
            return unique_derivatives
            
        except Exception as e:
            logger.error(f"Derivative product detection failed: {e}")
            return []
    
    async def track_price_changes(
        self,
        product_urls: List[str],
        check_interval: int = 3600
    ) -> AsyncGenerator[List[Dict], None]:
        """
        Track price changes for multiple products.
        
        Args:
            product_urls: List of product URLs to track
            check_interval: Check interval in seconds
            
        Yields:
            List of price change notifications
        """
        price_history = {}
        
        while True:
            try:
                price_changes = []
                
                for url in product_urls:
                    platform = self._detect_platform_from_url(url)
                    if not platform:
                        continue
                    
                    product = await self.monitor_product(url, platform)
                    if not product:
                        continue
                    
                    current_price = self._parse_price(product.price)
                    previous_price = price_history.get(url)
                    
                    if previous_price and current_price != previous_price:
                        change_percentage = ((current_price - previous_price) / previous_price) * 100
                        
                        price_change = {
                            'product_id': product.product_id,
                            'url': url,
                            'title': product.title,
                            'previous_price': previous_price,
                            'current_price': current_price,
                            'change_percentage': change_percentage,
                            'change_type': 'increase' if current_price > previous_price else 'decrease',
                            'timestamp': datetime.utcnow()
                        }
                        price_changes.append(price_change)
                    
                    price_history[url] = current_price
                
                if price_changes:
                    yield price_changes
                
                await asyncio.sleep(check_interval)
                
            except Exception as e:
                logger.error(f"Price tracking error: {e}")
                await asyncio.sleep(60)
    
    async def _search_amazon(self, search_url: str, max_results: int) -> List[EcommerceProduct]:
        """Search Amazon for products."""
        try:
            async with self.session.get(search_url) as response:
                if response.status != 200:
                    logger.warning(f"Amazon search failed with status: {response.status}")
                    return []
                
                html_content = await response.text()
                soup = BeautifulSoup(html_content, 'html.parser')
                
                products = []
                product_containers = soup.select('[data-component-type="s-search-result"]')
                
                for container in product_containers[:max_results]:
                    product = await self._parse_amazon_product(container)
                    if product:
                        products.append(product)
                
                return products
                
        except Exception as e:
            logger.error(f"Amazon search error: {e}")
            return []
    
    async def _search_ebay(self, search_url: str, max_results: int) -> List[EcommerceProduct]:
        """Search eBay for products."""
        try:
            async with self.session.get(search_url) as response:
                if response.status != 200:
                    logger.warning(f"eBay search failed with status: {response.status}")
                    return []
                
                html_content = await response.text()
                soup = BeautifulSoup(html_content, 'html.parser')
                
                products = []
                product_containers = soup.select('.s-item')
                
                for container in product_containers[:max_results]:
                    product = await self._parse_ebay_product(container)
                    if product:
                        products.append(product)
                
                return products
                
        except Exception as e:
            logger.error(f"eBay search error: {e}")
            return []
    
    async def _search_etsy(self, search_url: str, max_results: int) -> List[EcommerceProduct]:
        """Search Etsy for products."""
        try:
            async with self.session.get(search_url) as response:
                if response.status != 200:
                    logger.warning(f"Etsy search failed with status: {response.status}")
                    return []
                
                html_content = await response.text()
                soup = BeautifulSoup(html_content, 'html.parser')
                
                products = []
                product_containers = soup.select('.listing-link')
                
                for container in product_containers[:max_results]:
                    product = await self._parse_etsy_product(container)
                    if product:
                        products.append(product)
                
                return products
                
        except Exception as e:
            logger.error(f"Etsy search error: {e}")
            return []
    
    async def _parse_amazon_product(self, container) -> Optional[EcommerceProduct]:
        """Parse Amazon product data from HTML container."""
        try:
            title_elem = container.select_one('h2 a span')
            title = title_elem.get_text().strip() if title_elem else ""
            
            price_elem = container.select_one('.a-price-whole, .a-offscreen')
            price = price_elem.get_text().strip() if price_elem else ""
            
            rating_elem = container.select_one('.a-icon-alt')
            rating_text = rating_elem.get_text() if rating_elem else ""
            rating = self._extract_rating_from_text(rating_text)
            
            image_elem = container.select_one('.s-image')
            image_url = image_elem.get('src') if image_elem else ""
            
            url_elem = container.select_one('h2 a')
            product_url = f"https://amazon.com{url_elem.get('href')}" if url_elem else ""
            
            # Generate product ID from URL
            product_id = self._extract_amazon_product_id(product_url)
            
            # Generate product fingerprint
            fingerprint_data = f"{title}{price}{rating}"
            product_fingerprint = hashlib.md5(fingerprint_data.encode()).hexdigest()
            
            return EcommerceProduct(
                product_id=product_id,
                platform="amazon",
                title=title,
                description="",
                price=price,
                currency="USD",
                availability="unknown",
                seller_name="",
                seller_rating=None,
                product_rating=rating,
                review_count=0,
                category="",
                brand=None,
                url=product_url,
                image_urls=[image_url] if image_url else [],
                specifications={},
                shipping_info={},
                last_updated=datetime.utcnow(),
                price_history=[],
                similar_products=[],
                product_fingerprint=product_fingerprint
            )
            
        except Exception as e:
            logger.error(f"Amazon product parsing error: {e}")
            return None
    
    async def _parse_ebay_product(self, container) -> Optional[EcommerceProduct]:
        """Parse eBay product data from HTML container."""
        try:
            title_elem = container.select_one('.s-item__title')
            title = title_elem.get_text().strip() if title_elem else ""
            
            price_elem = container.select_one('.s-item__price')
            price = price_elem.get_text().strip() if price_elem else ""
            
            image_elem = container.select_one('.s-item__image')
            image_url = image_elem.get('src') if image_elem else ""
            
            url_elem = container.select_one('.s-item__link')
            product_url = url_elem.get('href') if url_elem else ""
            
            # Generate product ID from URL
            product_id = self._extract_ebay_product_id(product_url)
            
            # Generate product fingerprint
            fingerprint_data = f"{title}{price}"
            product_fingerprint = hashlib.md5(fingerprint_data.encode()).hexdigest()
            
            return EcommerceProduct(
                product_id=product_id,
                platform="ebay",
                title=title,
                description="",
                price=price,
                currency="USD",
                availability="unknown",
                seller_name="",
                seller_rating=None,
                product_rating=None,
                review_count=0,
                category="",
                brand=None,
                url=product_url,
                image_urls=[image_url] if image_url else [],
                specifications={},
                shipping_info={},
                last_updated=datetime.utcnow(),
                price_history=[],
                similar_products=[],
                product_fingerprint=product_fingerprint
            )
            
        except Exception as e:
            logger.error(f"eBay product parsing error: {e}")
            return None
    
    async def _parse_etsy_product(self, container) -> Optional[EcommerceProduct]:
        """Parse Etsy product data from HTML container."""
        try:
            title_elem = container.select_one('p[data-test-id="listing-card-title"]')
            title = title_elem.get_text().strip() if title_elem else ""
            
            price_elem = container.select_one('.currency-value')
            price = price_elem.get_text().strip() if price_elem else ""
            
            image_elem = container.select_one('img')
            image_url = image_elem.get('src') if image_elem else ""
            
            product_url = container.get('href', "")
            if product_url and not product_url.startswith('http'):
                product_url = f"https://etsy.com{product_url}"
            
            # Generate product ID from URL
            product_id = self._extract_etsy_product_id(product_url)
            
            # Generate product fingerprint
            fingerprint_data = f"{title}{price}"
            product_fingerprint = hashlib.md5(fingerprint_data.encode()).hexdigest()
            
            return EcommerceProduct(
                product_id=product_id,
                platform="etsy",
                title=title,
                description="",
                price=price,
                currency="USD",
                availability="unknown",
                seller_name="",
                seller_rating=None,
                product_rating=None,
                review_count=0,
                category="",
                brand=None,
                url=product_url,
                image_urls=[image_url] if image_url else [],
                specifications={},
                shipping_info={},
                last_updated=datetime.utcnow(),
                price_history=[],
                similar_products=[],
                product_fingerprint=product_fingerprint
            )
            
        except Exception as e:
            logger.error(f"Etsy product parsing error: {e}")
            return None
    
    def _build_search_url(self, platform: str, query: str, price_range: Optional[tuple] = None) -> str:
        """Build platform-specific search URL."""
        platform_config = self.platforms[platform]
        base_url = platform_config['base_url']
        search_endpoint = platform_config['search_endpoint']
        
        encoded_query = query.replace(' ', '+')
        
        if platform == 'amazon':
            url = f"{base_url}{search_endpoint}?k={encoded_query}"
            if price_range:
                url += f"&low-price={price_range[0]}&high-price={price_range[1]}"
        elif platform == 'ebay':
            url = f"{base_url}{search_endpoint}/i.html?_nkw={encoded_query}"
            if price_range:
                url += f"&_udlo={price_range[0]}&_udhi={price_range[1]}"
        elif platform == 'etsy':
            url = f"{base_url}{search_endpoint}?q={encoded_query}"
            if price_range:
                url += f"&min={price_range[0]}&max={price_range[1]}"
        else:
            url = f"{base_url}{search_endpoint}?q={encoded_query}"
        
        return url
    
    def _detect_platform_from_url(self, url: str) -> Optional[str]:
        """Detect e-commerce platform from URL."""
        domain = urlparse(url).netloc.lower()
        
        if 'amazon.' in domain:
            return 'amazon'
        elif 'ebay.' in domain:
            return 'ebay'
        elif 'etsy.' in domain:
            return 'etsy'
        
        return None
    
    def _extract_amazon_product_id(self, url: str) -> str:
        """Extract Amazon product ID from URL."""
        match = re.search(r'/dp/([A-Z0-9]{10})', url)
        return match.group(1) if match else ""
    
    def _extract_ebay_product_id(self, url: str) -> str:
        """Extract eBay product ID from URL."""
        match = re.search(r'/itm/([0-9]+)', url)
        return match.group(1) if match else ""
    
    def _extract_etsy_product_id(self, url: str) -> str:
        """Extract Etsy product ID from URL."""
        match = re.search(r'/listing/([0-9]+)', url)
        return match.group(1) if match else ""
    
    def _extract_rating_from_text(self, text: str) -> Optional[float]:
        """Extract rating from text."""
        match = re.search(r'(\d+\.?\d*)\s*out of\s*(\d+)', text)
        if match:
            return float(match.group(1))
        return None
    
    def _parse_price(self, price_str: str) -> float:
        """Parse price string to float."""
        if not price_str:
            return 0.0
        
        # Remove currency symbols and extract numbers
        price_match = re.search(r'[\d,]+\.?\d*', price_str.replace(',', ''))
        return float(price_match.group()) if price_match else 0.0
    
    def _generate_derivative_search_queries(self, product: EcommerceProduct) -> List[str]:
        """Generate search queries to find derivative products."""
        queries = []
        
        # Use product title words
        title_words = product.title.split()
        if len(title_words) > 2:
            queries.append(' '.join(title_words[:3]))
            queries.append(' '.join(title_words[-3:]))
        
        # Use brand if available
        if product.brand:
            queries.append(product.brand)
        
        # Use key product features
        key_terms = self._extract_key_terms(product.title)
        queries.extend(key_terms[:3])
        
        return queries[:5]  # Limit to 5 queries
    
    def _extract_key_terms(self, text: str) -> List[str]:
        """Extract key terms from product title."""
        # Simple keyword extraction
        words = text.lower().split()
        stop_words = {'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by'}
        key_terms = [word for word in words if word not in stop_words and len(word) > 3]
        return key_terms
    
    async def _calculate_product_similarity(
        self,
        product1: EcommerceProduct,
        product2: EcommerceProduct
    ) -> float:
        """Calculate similarity between two products."""
        from difflib import SequenceMatcher
        
        # Title similarity
        title_similarity = SequenceMatcher(
            None,
            product1.title.lower(),
            product2.title.lower()
        ).ratio()
        
        # Brand similarity
        brand_similarity = 0.0
        if product1.brand and product2.brand:
            brand_similarity = SequenceMatcher(
                None,
                product1.brand.lower(),
                product2.brand.lower()
            ).ratio()
        
        # Weighted average
        return (title_similarity * 0.7) + (brand_similarity * 0.3)
    
    def _deduplicate_products(self, products: List[EcommerceProduct]) -> List[EcommerceProduct]:
        """Remove duplicate products from list."""
        seen_fingerprints = set()
        unique_products = []
        
        for product in products:
            if product.product_fingerprint not in seen_fingerprints:
                seen_fingerprints.add(product.product_fingerprint)
                unique_products.append(product)
        
        return unique_products
    
    async def _monitor_amazon_product(self, url: str) -> Optional[EcommerceProduct]:
        """Monitor specific Amazon product."""
        # Implementation would fetch product page and extract details
        # For now, return None as placeholder
        return None
    
    async def _monitor_ebay_product(self, url: str) -> Optional[EcommerceProduct]:
        """Monitor specific eBay product."""
        # Implementation would fetch product page and extract details
        return None
    
    async def _monitor_etsy_product(self, url: str) -> Optional[EcommerceProduct]:
        """Monitor specific Etsy product."""
        # Implementation would fetch product page and extract details
        return None

# Example usage
if __name__ == "__main__":
    async def test_ecommerce_crawler():
        async with EcommerceCrawler() as crawler:
            # Search for products
            products = await crawler.search_products("wireless headphones", "amazon", 10)
            print(f"Found {len(products)} products")
            
            if products:
                # Monitor first product
                monitored = await crawler.monitor_product(products[0].url, "amazon")
                print(f"Monitored product: {monitored}")
                
                # Detect derivatives
                derivatives = await crawler.detect_derivative_products(products[0])
                print(f"Found {len(derivatives)} potential derivatives")
    
    # asyncio.run(test_ecommerce_crawler())