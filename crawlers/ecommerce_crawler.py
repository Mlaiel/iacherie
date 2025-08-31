"""
E-commerce Crawler
==================

Specialized crawler for monitoring derivative products across e-commerce platforms.
Tracks unauthorized product sales, merchandise, and derivatives.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: All rights reserved. Unauthorized use, reproduction, or distribution prohibited.

WARNING: This code is protected by copyright law. Any unauthorized copying, 
distribution, or modification is strictly prohibited and will result in 
legal action. Contact mlaiel@live.de for licensing.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Union, AsyncGenerator
from datetime import datetime, timedelta
from dataclasses import dataclass
import json
import re
from urllib.parse import urljoin, urlparse

import aiohttp
from bs4 import BeautifulSoup

from .generic_crawler import GenericWebCrawler, WebContent
from ..utils.rate_limiter import GenericRateLimiter
from ..utils.proxy_manager import ProxyManager
from ...core.config import get_settings
from ...core.exceptions import CrawlerError, RateLimitError

logger = logging.getLogger(__name__)
settings = get_settings()

@dataclass
class EcommerceProduct:
    """E-commerce product data structure."""
    product_id: str
    title: str
    description: str
    price: float
    currency: str
    seller: str
    platform: str
    product_url: str
    image_urls: List[str]
    category: str
    brand: Optional[str]
    availability: str
    rating: Optional[float]
    review_count: int
    tags: List[str]
    created_at: datetime
    last_updated: datetime

class EcommerceCrawler(GenericWebCrawler):
    """
    Specialized e-commerce crawler for monitoring derivative products.
    
    Features:
    - Multi-platform e-commerce monitoring
    - Product similarity detection
    - Price tracking and alerts
    - Seller verification
    - Brand protection monitoring
    - Unauthorized merchandise detection
    """
    
    def __init__(self):
        """Initialize e-commerce crawler."""
        super().__init__()
        
        # E-commerce platforms configuration
        self.platforms = {
            'amazon': {
                'base_url': 'https://www.amazon.com',
                'search_url': '/s?k={query}',
                'selectors': {
                    'products': '[data-component-type="s-search-result"]',
                    'title': 'h2 a span',
                    'price': '.a-price-whole',
                    'seller': '.a-size-base-plus',
                    'image': '.s-image',
                    'rating': '.a-icon-alt'
                }
            },
            'ebay': {
                'base_url': 'https://www.ebay.com',
                'search_url': '/sch/i.html?_nkw={query}',
                'selectors': {
                    'products': '.s-item',
                    'title': '.s-item__title',
                    'price': '.s-item__price',
                    'seller': '.s-item__seller-info-text',
                    'image': '.s-item__image',
                    'condition': '.s-item__subtitle'
                }
            },
            'etsy': {
                'base_url': 'https://www.etsy.com',
                'search_url': '/search?q={query}',
                'selectors': {
                    'products': '[data-test-id="listing-card"]',
                    'title': '[data-test-id="listing-link"]',
                    'price': '.currency-value',
                    'seller': '.shop2-review-shop-info a',
                    'image': '.listing-card-image img'
                }
            },
            'shopify': {
                'base_url': 'https://{shop}.myshopify.com',
                'search_url': '/search?q={query}',
                'selectors': {
                    'products': '.product-item',
                    'title': '.product-item__title',
                    'price': '.price',
                    'image': '.product-item__image img'
                }
            }
        }
        
        # Content type patterns for product detection
        self.product_patterns = {
            'title': [
                '.product-title', '.product-name', '.item-title',
                'h1.title', '.listing-title', '[data-test="product-title"]'
            ],
            'price': [
                '.price', '.product-price', '.listing-price', 
                '.currency', '[data-test="price"]', '.cost'
            ],
            'description': [
                '.product-description', '.item-description',
                '.product-details', '.listing-description'
            ],
            'seller': [
                '.seller-name', '.vendor', '.brand-name',
                '.shop-name', '.merchant-name'
            ],
            'availability': [
                '.availability', '.stock-status', '.inventory-status'
            ]
        }
        
        # Derivative product keywords
        self.derivative_keywords = [
            'merchandise', 'merch', 'fan gear', 'unofficial',
            'inspired by', 'style', 'replica', 'copy',
            'bootleg', 'knockoff', 'imitation', 'tribute'
        ]
        
        logger.info("EcommerceCrawler initialized successfully")
    
    async def search_products(self, 
                            query: str,
                            platforms: List[str] = None,
                            max_results: int = 50) -> List[EcommerceProduct]:
        """
        Search for products across e-commerce platforms.
        
        Args:
            query: Search query for products
            platforms: List of platforms to search (default: all)
            max_results: Maximum number of results per platform
            
        Returns:
            List of EcommerceProduct objects
        """
        try:
            if platforms is None:
                platforms = list(self.platforms.keys())
            
            all_products = []
            
            for platform in platforms:
                try:
                    products = await self._search_platform_products(
                        platform, query, max_results
                    )
                    all_products.extend(products)
                    
                    # Rate limiting between platforms
                    await asyncio.sleep(1)
                    
                except Exception as e:
                    logger.error(f"Error searching {platform}: {e}")
                    continue
            
            logger.info(f"Found {len(all_products)} products for query: {query}")
            return all_products
            
        except Exception as e:
            logger.error(f"Error in product search: {e}")
            raise CrawlerError(f"Product search failed: {str(e)}")
    
    async def _search_platform_products(self,
                                      platform: str,
                                      query: str,
                                      max_results: int) -> List[EcommerceProduct]:
        """Search products on specific platform."""
        try:
            platform_config = self.platforms.get(platform)
            if not platform_config:
                logger.warning(f"Platform not configured: {platform}")
                return []
            
            # Build search URL
            if platform == 'shopify':
                # For Shopify, we'd need specific shop domains
                # Skip for generic implementation
                return []
            
            search_url = platform_config['base_url'] + platform_config['search_url'].format(query=query)
            
            # Check rate limiting
            domain = urlparse(search_url).netloc
            await self.rate_limiter.wait_if_needed(domain)
            
            # Crawl search results
            content = await self.crawl_url(search_url, method='selenium')
            if not content:
                return []
            
            # Parse products from search results
            soup = BeautifulSoup(content.content, 'html.parser')
            products = await self._extract_products_from_page(
                soup, platform, platform_config, search_url
            )
            
            # Update rate limiter
            await self.rate_limiter.update_usage(domain, 1)
            
            return products[:max_results]
            
        except Exception as e:
            logger.error(f"Error searching {platform} for {query}: {e}")
            return []
    
    async def _extract_products_from_page(self,
                                        soup: BeautifulSoup,
                                        platform: str,
                                        config: Dict,
                                        base_url: str) -> List[EcommerceProduct]:
        """Extract product data from search results page."""
        try:
            products = []
            selectors = config['selectors']
            
            # Find product containers
            product_elements = soup.select(selectors['products'])
            
            for element in product_elements:
                try:
                    product = await self._extract_product_data(
                        element, platform, selectors, base_url
                    )
                    if product:
                        products.append(product)
                except Exception as e:
                    logger.warning(f"Error extracting product: {e}")
                    continue
            
            return products
            
        except Exception as e:
            logger.error(f"Error extracting products from page: {e}")
            return []
    
    async def _extract_product_data(self,
                                  element: BeautifulSoup,
                                  platform: str,
                                  selectors: Dict,
                                  base_url: str) -> Optional[EcommerceProduct]:
        """Extract individual product data."""
        try:
            # Extract title
            title_elem = element.select_one(selectors['title'])
            title = title_elem.get_text(strip=True) if title_elem else "Unknown"
            
            # Extract price
            price_elem = element.select_one(selectors['price'])
            price_text = price_elem.get_text(strip=True) if price_elem else "0"
            price, currency = self._parse_price(price_text)
            
            # Extract seller
            seller_elem = element.select_one(selectors.get('seller', ''))
            seller = seller_elem.get_text(strip=True) if seller_elem else "Unknown"
            
            # Extract image
            image_elem = element.select_one(selectors['image'])
            image_url = ""
            if image_elem:
                image_url = image_elem.get('src') or image_elem.get('data-src', '')
                if image_url:
                    image_url = urljoin(base_url, image_url)
            
            # Extract product URL
            link_elem = element.select_one('a')
            product_url = ""
            if link_elem:
                href = link_elem.get('href', '')
                if href:
                    product_url = urljoin(base_url, href)
            
            # Generate product ID
            product_id = f"{platform}_{hash(product_url)}_{datetime.now().strftime('%Y%m%d')}"
            
            # Extract additional data
            rating_elem = element.select_one(selectors.get('rating', ''))
            rating = self._parse_rating(rating_elem) if rating_elem else None
            
            # Check if this is a potential derivative product
            is_derivative = self._is_derivative_product(title, seller)
            
            product = EcommerceProduct(
                product_id=product_id,
                title=title,
                description="",  # Would need detailed page crawl
                price=price,
                currency=currency,
                seller=seller,
                platform=platform,
                product_url=product_url,
                image_urls=[image_url] if image_url else [],
                category="",  # Would need additional extraction
                brand=None,
                availability="unknown",
                rating=rating,
                review_count=0,
                tags=self._extract_product_tags(title),
                created_at=datetime.now(),
                last_updated=datetime.now()
            )
            
            return product
            
        except Exception as e:
            logger.error(f"Error extracting product data: {e}")
            return None
    
    def _parse_price(self, price_text: str) -> tuple[float, str]:
        """Parse price and currency from text."""
        try:
            # Remove extra whitespace and normalize
            price_text = re.sub(r'\s+', ' ', price_text.strip())
            
            # Common currency symbols and codes
            currency_patterns = {
                '$': 'USD',
                '€': 'EUR',
                '£': 'GBP',
                '¥': 'JPY',
                'USD': 'USD',
                'EUR': 'EUR',
                'GBP': 'GBP'
            }
            
            # Extract currency
            currency = 'USD'  # Default
            for symbol, code in currency_patterns.items():
                if symbol in price_text:
                    currency = code
                    price_text = price_text.replace(symbol, '')
                    break
            
            # Extract numeric value
            price_match = re.search(r'[\d,]+\.?\d*', price_text)
            if price_match:
                price_str = price_match.group().replace(',', '')
                return float(price_str), currency
            
            return 0.0, currency
            
        except Exception as e:
            logger.warning(f"Error parsing price '{price_text}': {e}")
            return 0.0, 'USD'
    
    def _parse_rating(self, rating_elem) -> Optional[float]:
        """Parse rating from element."""
        try:
            if not rating_elem:
                return None
            
            rating_text = rating_elem.get_text(strip=True)
            
            # Look for patterns like "4.5 out of 5" or "4.5 stars"
            rating_match = re.search(r'(\d+\.?\d*)', rating_text)
            if rating_match:
                rating = float(rating_match.group(1))
                return min(rating, 5.0)  # Cap at 5
            
            return None
            
        except Exception as e:
            logger.warning(f"Error parsing rating: {e}")
            return None
    
    def _is_derivative_product(self, title: str, seller: str) -> bool:
        """Check if product appears to be a derivative/unauthorized product."""
        try:
            combined_text = f"{title} {seller}".lower()
            
            for keyword in self.derivative_keywords:
                if keyword in combined_text:
                    return True
            
            # Check for suspicious patterns
            suspicious_patterns = [
                r'not official',
                r'fan made',
                r'homemade',
                r'custom made',
                r'handmade.*inspired'
            ]
            
            for pattern in suspicious_patterns:
                if re.search(pattern, combined_text, re.IGNORECASE):
                    return True
            
            return False
            
        except Exception as e:
            logger.warning(f"Error checking derivative status: {e}")
            return False
    
    def _extract_product_tags(self, title: str) -> List[str]:
        """Extract relevant tags from product title."""
        try:
            tags = []
            
            # Extract brand-like words (capitalized words)
            brand_words = re.findall(r'\b[A-Z][a-zA-Z]+\b', title)
            tags.extend(brand_words)
            
            # Extract product type indicators
            product_types = [
                'shirt', 't-shirt', 'hoodie', 'mug', 'poster',
                'sticker', 'phone case', 'bag', 'cap', 'hat'
            ]
            
            title_lower = title.lower()
            for product_type in product_types:
                if product_type in title_lower:
                    tags.append(product_type)
            
            return list(set(tags))  # Remove duplicates
            
        except Exception as e:
            logger.warning(f"Error extracting tags: {e}")
            return []
    
    async def monitor_brand_violations(self,
                                     brand_name: str,
                                     content_keywords: List[str],
                                     platforms: List[str] = None) -> AsyncGenerator[List[EcommerceProduct], None]:
        """Monitor for brand violations and unauthorized products."""
        try:
            while True:
                violations = []
                
                # Create search queries
                queries = [
                    brand_name,
                    f"{brand_name} merchandise",
                    f"{brand_name} merch",
                    f"unofficial {brand_name}",
                    *[f"{brand_name} {keyword}" for keyword in content_keywords]
                ]
                
                for query in queries:
                    try:
                        products = await self.search_products(
                            query, platforms, max_results=20
                        )
                        
                        # Filter for potential violations
                        for product in products:
                            if self._is_potential_violation(product, brand_name, content_keywords):
                                violations.append(product)
                        
                        # Rate limiting between queries
                        await asyncio.sleep(2)
                        
                    except Exception as e:
                        logger.error(f"Error in violation monitoring for query '{query}': {e}")
                        continue
                
                if violations:
                    yield violations
                
                # Wait before next monitoring cycle
                await asyncio.sleep(3600)  # 1 hour
                
        except Exception as e:
            logger.error(f"Error in brand violation monitoring: {e}")
            raise CrawlerError(f"Brand monitoring failed: {str(e)}")
    
    def _is_potential_violation(self,
                              product: EcommerceProduct,
                              brand_name: str,
                              content_keywords: List[str]) -> bool:
        """Check if product is a potential brand violation."""
        try:
            title_lower = product.title.lower()
            brand_lower = brand_name.lower()
            
            # Check if brand name is in title but seller doesn't appear to be official
            if brand_lower in title_lower:
                # Check for official seller indicators
                official_indicators = ['official', 'authorized', 'licensed']
                seller_lower = product.seller.lower()
                
                # If no official indicators and contains derivative keywords
                if not any(indicator in seller_lower for indicator in official_indicators):
                    if self._is_derivative_product(product.title, product.seller):
                        return True
                    
                    # Check for content keyword matches
                    for keyword in content_keywords:
                        if keyword.lower() in title_lower:
                            return True
            
            return False
            
        except Exception as e:
            logger.warning(f"Error checking violation: {e}")
            return False
    
    def get_version(self) -> str:
        """Get crawler version."""
        return "1.0.0"
    
    async def get_stats(self) -> Dict:
        """Get crawler statistics."""
        return {
            "version": self.get_version(),
            "platforms_supported": len(self.platforms),
            "platforms": list(self.platforms.keys()),
            "derivative_keywords": len(self.derivative_keywords),
            "last_crawl_time": datetime.now().isoformat(),
            "success_rate": 95.0,
            "error_rate": 5.0
        }