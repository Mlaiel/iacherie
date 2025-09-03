"""Sitemap Builder - Dynamic XML Sitemap Generation Service

Advanced dynamic sitemap generation service for automatic XML sitemap creation,
maintenance, and optimization for search engine discovery.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
import xml.etree.ElementTree as ET
from typing import Dict, List, Optional, Any, Union
from datetime import datetime, timezone
from dataclasses import dataclass, field
from enum import Enum
from urllib.parse import urljoin, urlparse

logger = logging.getLogger(__name__)


class ChangeFrequency(Enum):
    """XML sitemap change frequency values"""
    ALWAYS = "always"
    HOURLY = "hourly"
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    YEARLY = "yearly"
    NEVER = "never"


@dataclass
class SitemapUrl:
    """Individual URL entry for sitemap"""
    loc: str
    lastmod: Optional[datetime] = None
    changefreq: Optional[ChangeFrequency] = None
    priority: Optional[float] = None
    
    def __post_init__(self):
        if self.priority is not None:
            # Ensure priority is between 0.0 and 1.0
            self.priority = max(0.0, min(1.0, self.priority))


@dataclass
class SitemapConfig:
    """Configuration for sitemap generation"""
    base_url: str
    max_urls_per_sitemap: int = 50000
    include_images: bool = True
    include_videos: bool = False
    default_priority: float = 0.5
    default_changefreq: ChangeFrequency = ChangeFrequency.WEEKLY
    exclude_patterns: List[str] = field(default_factory=list)


@dataclass
class SitemapResult:
    """Result of sitemap generation"""
    xml_content: str
    url_count: int
    file_size: int
    timestamp: datetime
    sitemap_index: Optional[str] = None


class SitemapBuilder:
    """Dynamic XML sitemap generation service"""
    
    def __init__(self, config: Optional[SitemapConfig] = None):
        self.config = config or SitemapConfig(base_url="https://example.com")
        self.sitemap_namespace = "http://www.sitemaps.org/schemas/sitemap/0.9"
        logger.info("SitemapBuilder service initialized")
    
    def _should_exclude_url(self, url: str) -> bool:
        """Check if URL should be excluded from sitemap"""
        for pattern in self.config.exclude_patterns:
            if pattern in url:
                return True
        return False
    
    def _validate_url(self, url: str) -> bool:
        """Validate URL format"""
        try:
            parsed = urlparse(url)
            return bool(parsed.scheme and parsed.netloc)
        except Exception:
            return False
    
    def _format_datetime(self, dt: datetime) -> str:
        """Format datetime for XML sitemap"""
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt.strftime('%Y-%m-%dT%H:%M:%S%z')
    
    async def build_sitemap(self, urls: List[Union[str, SitemapUrl]]) -> SitemapResult:
        """
        Build XML sitemap from list of URLs
        
        Args:
            urls: List of URLs or SitemapUrl objects
            
        Returns:
            SitemapResult: Generated sitemap data
        """
        try:
            # Convert strings to SitemapUrl objects
            sitemap_urls = []
            for url in urls:
                if isinstance(url, str):
                    if not self._should_exclude_url(url) and self._validate_url(url):
                        sitemap_urls.append(SitemapUrl(
                            loc=url,
                            lastmod=datetime.now(timezone.utc),
                            changefreq=self.config.default_changefreq,
                            priority=self.config.default_priority
                        ))
                elif isinstance(url, SitemapUrl):
                    if not self._should_exclude_url(url.loc) and self._validate_url(url.loc):
                        sitemap_urls.append(url)
            
            # Create XML structure
            urlset = ET.Element('urlset')
            urlset.set('xmlns', self.sitemap_namespace)
            
            for sitemap_url in sitemap_urls[:self.config.max_urls_per_sitemap]:
                url_element = ET.SubElement(urlset, 'url')
                
                # Location (required)
                loc_element = ET.SubElement(url_element, 'loc')
                loc_element.text = sitemap_url.loc
                
                # Last modification date
                if sitemap_url.lastmod:
                    lastmod_element = ET.SubElement(url_element, 'lastmod')
                    lastmod_element.text = self._format_datetime(sitemap_url.lastmod)
                
                # Change frequency
                if sitemap_url.changefreq:
                    changefreq_element = ET.SubElement(url_element, 'changefreq')
                    changefreq_element.text = sitemap_url.changefreq.value
                
                # Priority
                if sitemap_url.priority is not None:
                    priority_element = ET.SubElement(url_element, 'priority')
                    priority_element.text = f"{sitemap_url.priority:.1f}"
            
            # Generate XML string
            ET.indent(urlset, space="  ", level=0)
            xml_content = ET.tostring(urlset, encoding='unicode', xml_declaration=True)
            
            result = SitemapResult(
                xml_content=xml_content,
                url_count=len(sitemap_urls),
                file_size=len(xml_content.encode('utf-8')),
                timestamp=datetime.now(timezone.utc)
            )
            
            logger.info(f"Sitemap generated with {result.url_count} URLs")
            return result
            
        except Exception as e:
            logger.error(f"Sitemap generation failed: {str(e)}")
            raise
    
    async def build_sitemap_index(self, sitemap_urls: List[str]) -> str:
        """
        Build sitemap index file for multiple sitemaps
        
        Args:
            sitemap_urls: List of sitemap file URLs
            
        Returns:
            str: XML content of sitemap index
        """
        try:
            sitemapindex = ET.Element('sitemapindex')
            sitemapindex.set('xmlns', self.sitemap_namespace)
            
            for sitemap_url in sitemap_urls:
                sitemap_element = ET.SubElement(sitemapindex, 'sitemap')
                
                loc_element = ET.SubElement(sitemap_element, 'loc')
                loc_element.text = sitemap_url
                
                lastmod_element = ET.SubElement(sitemap_element, 'lastmod')
                lastmod_element.text = self._format_datetime(datetime.now(timezone.utc))
            
            ET.indent(sitemapindex, space="  ", level=0)
            xml_content = ET.tostring(sitemapindex, encoding='unicode', xml_declaration=True)
            
            logger.info(f"Sitemap index generated with {len(sitemap_urls)} sitemaps")
            return xml_content
            
        except Exception as e:
            logger.error(f"Sitemap index generation failed: {str(e)}")
            raise
    
    async def discover_urls_from_database(self, db_session) -> List[SitemapUrl]:
        """
        Discover URLs from database for sitemap generation
        
        Args:
            db_session: Database session
            
        Returns:
            List[SitemapUrl]: Discovered URLs
        """
        try:
            urls = []
            
            # This would be implemented based on your database schema
            # Example implementation:
            
            # Static pages
            static_pages = [
                ('/', 1.0, ChangeFrequency.WEEKLY),
                ('/about', 0.8, ChangeFrequency.MONTHLY),
                ('/contact', 0.6, ChangeFrequency.MONTHLY),
                ('/privacy', 0.4, ChangeFrequency.YEARLY),
                ('/terms', 0.4, ChangeFrequency.YEARLY)
            ]
            
            for path, priority, changefreq in static_pages:
                url = urljoin(self.config.base_url, path)
                urls.append(SitemapUrl(
                    loc=url,
                    lastmod=datetime.now(timezone.utc),
                    changefreq=changefreq,
                    priority=priority
                ))
            
            # TODO: Add database queries for dynamic content
            # Example:
            # - Blog posts
            # - User profiles
            # - Product pages
            # - Category pages
            
            logger.info(f"Discovered {len(urls)} URLs from database")
            return urls
            
        except Exception as e:
            logger.error(f"URL discovery failed: {str(e)}")
            return []
    
    async def generate_dynamic_sitemap(self, db_session) -> SitemapResult:
        """
        Generate dynamic sitemap from database content
        
        Args:
            db_session: Database session
            
        Returns:
            SitemapResult: Generated sitemap
        """
        try:
            # Discover URLs from database
            urls = await self.discover_urls_from_database(db_session)
            
            # Build sitemap
            result = await self.build_sitemap(urls)
            
            logger.info(f"Dynamic sitemap generated with {result.url_count} URLs")
            return result
            
        except Exception as e:
            logger.error(f"Dynamic sitemap generation failed: {str(e)}")
            raise
    
    async def validate_sitemap(self, xml_content: str) -> Dict[str, Any]:
        """
        Validate XML sitemap format and content
        
        Args:
            xml_content: XML sitemap content
            
        Returns:
            Dict with validation results
        """
        try:
            validation_result = {
                'valid_xml': False,
                'valid_structure': False,
                'url_count': 0,
                'errors': [],
                'warnings': []
            }
            
            # Parse XML
            try:
                root = ET.fromstring(xml_content)
                validation_result['valid_xml'] = True
            except ET.ParseError as e:
                validation_result['errors'].append(f"Invalid XML: {str(e)}")
                return validation_result
            
            # Check structure
            if root.tag.endswith('urlset'):
                validation_result['valid_structure'] = True
                urls = root.findall('.//{http://www.sitemaps.org/schemas/sitemap/0.9}url')
                validation_result['url_count'] = len(urls)
                
                # Check URL limits
                if len(urls) > 50000:
                    validation_result['warnings'].append("Sitemap contains more than 50,000 URLs")
                
                # Check file size
                if len(xml_content.encode('utf-8')) > 50 * 1024 * 1024:  # 50MB
                    validation_result['errors'].append("Sitemap file size exceeds 50MB limit")
            
            return validation_result
            
        except Exception as e:
            logger.error(f"Sitemap validation failed: {str(e)}")
            return {'valid_xml': False, 'valid_structure': False, 'errors': [str(e)]}