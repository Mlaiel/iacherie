"""XML Sitemap Generator
Advanced XML sitemap generation system for enterprise SEO optimization.

Features:
- Dynamic XML sitemap generation with priority and frequency
- Multi-sitemap management (regular, image, video, news)
- Sitemap index generation for large sites
- Automatic sitemap updates and validation
- Creator-specific sitemap optimization
- Performance-optimized crawl budget management

Author: Fahed Mlaiel (mlaiel@live.de)
Lead Dev IA + Backend Senior expertise applied
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Tuple, Any, Union
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import xml.etree.ElementTree as ET
from urllib.parse import urljoin, urlparse
import gzip
import os
import hashlib

logger = logging.getLogger(__name__)

class SitemapType(Enum):
    """Types of sitemaps supported."""
    STANDARD = "standard"
    IMAGE = "image"
    VIDEO = "video"
    NEWS = "news"
    MOBILE = "mobile"

class ChangeFrequency(Enum):
    """URL change frequency options."""
    ALWAYS = "always"
    HOURLY = "hourly"
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    YEARLY = "yearly"
    NEVER = "never"

@dataclass
class URLEntry:
    """URL entry for sitemap."""
    url: str
    lastmod: Optional[datetime] = None
    changefreq: Optional[ChangeFrequency] = None
    priority: Optional[float] = None
    # For image sitemaps
    images: List[Dict[str, str]] = field(default_factory=list)
    # For video sitemaps
    videos: List[Dict[str, Any]] = field(default_factory=list)
    # For news sitemaps
    news: Optional[Dict[str, Any]] = None
    # Creator-specific metadata
    creator_metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class SitemapConfig:
    """Configuration for sitemap generation."""
    base_url: str
    max_urls_per_sitemap: int = 50000
    max_file_size_mb: float = 50.0
    compress_sitemaps: bool = True
    include_images: bool = True
    include_videos: bool = True
    include_news: bool = False
    validate_urls: bool = True
    creator_optimization: bool = True

class XMLSitemapGenerator:
    """
    Enterprise XML sitemap generator with advanced SEO optimization.
    Handles multiple sitemap types, compression, and creator-specific optimization.
    """
    
    def __init__(self, config: SitemapConfig):
        self.config = config
        self.base_url = config.base_url.rstrip('/')
        self.sitemaps: Dict[SitemapType, List[URLEntry]] = {
            sitemap_type: [] for sitemap_type in SitemapType
        }
        self.sitemap_files: List[str] = []
        self.total_urls = 0
        
    async def add_url(self, 
                     url: str,
                     lastmod: Optional[datetime] = None,
                     changefreq: Optional[ChangeFrequency] = None,
                     priority: Optional[float] = None,
                     sitemap_type: SitemapType = SitemapType.STANDARD,
                     **metadata) -> bool:
        """
        Add URL to appropriate sitemap.
        
        Args:
            url: URL to add
            lastmod: Last modification date
            changefreq: Change frequency
            priority: Priority (0.0-1.0)
            sitemap_type: Type of sitemap
            **metadata: Additional metadata for specific sitemap types
            
        Returns:
            Success status
        """
        try:
            # Validate URL if configured
            if self.config.validate_urls and not self._validate_url(url):
                logger.warning(f"Invalid URL skipped: {url}")
                return False
                
            # Ensure URL is absolute
            if not url.startswith(('http://', 'https://')):
                url = urljoin(self.base_url, url)
                
            # Create URL entry
            entry = URLEntry(
                url=url,
                lastmod=lastmod or datetime.now(),
                changefreq=changefreq,
                priority=priority
            )
            
            # Add type-specific metadata
            if sitemap_type == SitemapType.IMAGE and 'images' in metadata:
                entry.images = metadata['images']
            elif sitemap_type == SitemapType.VIDEO and 'videos' in metadata:
                entry.videos = metadata['videos']
            elif sitemap_type == SitemapType.NEWS and 'news' in metadata:
                entry.news = metadata['news']
                
            # Add creator metadata if available
            if 'creator_metadata' in metadata:
                entry.creator_metadata = metadata['creator_metadata']
                
            self.sitemaps[sitemap_type].append(entry)
            self.total_urls += 1
            
            logger.debug(f"Added URL to {sitemap_type.value} sitemap: {url}")
            return True
            
        except Exception as e:
            logger.error(f"Error adding URL {url}: {str(e)}")
            return False
    
    async def add_creator_content(self,
                                creator_id: str,
                                content_urls: List[Dict[str, Any]]) -> int:
        """
        Add creator-specific content with optimized SEO.
        
        Args:
            creator_id: Creator identifier
            content_urls: List of content with metadata
            
        Returns:
            Number of URLs successfully added
        """
        added_count = 0
        
        try:
            for content in content_urls:
                url = content.get('url')
                content_type = content.get('type', 'standard')
                
                if not url:
                    continue
                    
                # Determine sitemap type based on content
                sitemap_type = SitemapType.STANDARD
                metadata = {
                    'creator_metadata': {
                        'creator_id': creator_id,
                        'content_type': content_type,
                        'monetization_enabled': content.get('monetizable', False)
                    }
                }
                
                if content_type in ['image', 'photo']:
                    sitemap_type = SitemapType.IMAGE
                    metadata['images'] = [{
                        'loc': url,
                        'caption': content.get('title', ''),
                        'title': content.get('title', ''),
                        'license': content.get('license', '')
                    }]
                elif content_type in ['video', 'audio']:
                    sitemap_type = SitemapType.VIDEO
                    metadata['videos'] = [{
                        'thumbnail_loc': content.get('thumbnail', ''),
                        'title': content.get('title', ''),
                        'description': content.get('description', ''),
                        'content_loc': url,
                        'duration': content.get('duration', 0)
                    }]
                    
                # Set creator-optimized priority and frequency
                priority = self._calculate_creator_priority(content)
                changefreq = self._determine_content_frequency(content_type)
                
                success = await self.add_url(
                    url=url,
                    lastmod=content.get('created_at'),
                    changefreq=changefreq,
                    priority=priority,
                    sitemap_type=sitemap_type,
                    **metadata
                )
                
                if success:
                    added_count += 1
                    
        except Exception as e:
            logger.error(f"Error adding creator content for {creator_id}: {str(e)}")
            
        return added_count
    
    async def generate_sitemaps(self, output_dir: str) -> Dict[str, Any]:
        """
        Generate all sitemap files.
        
        Args:
            output_dir: Directory to save sitemap files
            
        Returns:
            Generation results with file paths and statistics
        """
        try:
            os.makedirs(output_dir, exist_ok=True)
            
            results = {
                'sitemap_files': [],
                'sitemap_index_file': None,
                'total_urls': self.total_urls,
                'compression_enabled': self.config.compress_sitemaps,
                'generation_time': datetime.now().isoformat()
            }
            
            # Generate individual sitemaps
            for sitemap_type, urls in self.sitemaps.items():
                if not urls:
                    continue
                    
                files = await self._generate_sitemap_type(
                    sitemap_type, urls, output_dir
                )
                results['sitemap_files'].extend(files)
                
            # Generate sitemap index if multiple files
            if len(results['sitemap_files']) > 1:
                index_file = await self._generate_sitemap_index(
                    results['sitemap_files'], output_dir
                )
                results['sitemap_index_file'] = index_file
                
            logger.info(f"Generated {len(results['sitemap_files'])} sitemap files")
            return results
            
        except Exception as e:
            logger.error(f"Error generating sitemaps: {str(e)}")
            raise
    
    async def _generate_sitemap_type(self,
                                   sitemap_type: SitemapType,
                                   urls: List[URLEntry],
                                   output_dir: str) -> List[str]:
        """Generate sitemaps for specific type."""
        files = []
        
        # Split URLs into chunks if needed
        chunks = self._chunk_urls(urls)
        
        for i, chunk in enumerate(chunks):
            suffix = f"_{i+1}" if len(chunks) > 1 else ""
            filename = f"sitemap_{sitemap_type.value}{suffix}.xml"
            
            if self.config.compress_sitemaps:
                filename += ".gz"
                
            filepath = os.path.join(output_dir, filename)
            
            # Generate XML content
            xml_content = await self._generate_xml_content(sitemap_type, chunk)
            
            # Write file
            if self.config.compress_sitemaps:
                with gzip.open(filepath, 'wt', encoding='utf-8') as f:
                    f.write(xml_content)
            else:
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(xml_content)
                    
            files.append(filename)
            
        return files
    
    async def _generate_xml_content(self,
                                  sitemap_type: SitemapType,
                                  urls: List[URLEntry]) -> str:
        """Generate XML content for sitemap."""
        if sitemap_type == SitemapType.IMAGE:
            return self._generate_image_sitemap(urls)
        elif sitemap_type == SitemapType.VIDEO:
            return self._generate_video_sitemap(urls)
        elif sitemap_type == SitemapType.NEWS:
            return self._generate_news_sitemap(urls)
        else:
            return self._generate_standard_sitemap(urls)
    
    def _generate_standard_sitemap(self, urls: List[URLEntry]) -> str:
        """Generate standard XML sitemap."""
        root = ET.Element("urlset")
        root.set("xmlns", "http://www.sitemaps.org/schemas/sitemap/0.9")
        
        for entry in urls:
            url_elem = ET.SubElement(root, "url")
            
            # Required: location
            loc_elem = ET.SubElement(url_elem, "loc")
            loc_elem.text = entry.url
            
            # Optional: last modified
            if entry.lastmod:
                lastmod_elem = ET.SubElement(url_elem, "lastmod")
                lastmod_elem.text = entry.lastmod.isoformat()
                
            # Optional: change frequency
            if entry.changefreq:
                changefreq_elem = ET.SubElement(url_elem, "changefreq")
                changefreq_elem.text = entry.changefreq.value
                
            # Optional: priority
            if entry.priority is not None:
                priority_elem = ET.SubElement(url_elem, "priority")
                priority_elem.text = f"{entry.priority:.1f}"
                
        return self._format_xml(root)
    
    def _generate_image_sitemap(self, urls: List[URLEntry]) -> str:
        """Generate image XML sitemap."""
        root = ET.Element("urlset")
        root.set("xmlns", "http://www.sitemaps.org/schemas/sitemap/0.9")
        root.set("xmlns:image", "http://www.google.com/schemas/sitemap-image/1.1")
        
        for entry in urls:
            url_elem = ET.SubElement(root, "url")
            
            loc_elem = ET.SubElement(url_elem, "loc")
            loc_elem.text = entry.url
            
            # Add image information
            for image in entry.images:
                image_elem = ET.SubElement(url_elem, "image:image")
                
                image_loc = ET.SubElement(image_elem, "image:loc")
                image_loc.text = image.get('loc', '')
                
                if image.get('caption'):
                    caption = ET.SubElement(image_elem, "image:caption")
                    caption.text = image['caption']
                    
                if image.get('title'):
                    title = ET.SubElement(image_elem, "image:title")
                    title.text = image['title']
                    
        return self._format_xml(root)
    
    def _generate_video_sitemap(self, urls: List[URLEntry]) -> str:
        """Generate video XML sitemap."""
        root = ET.Element("urlset")
        root.set("xmlns", "http://www.sitemaps.org/schemas/sitemap/0.9")
        root.set("xmlns:video", "http://www.google.com/schemas/sitemap-video/1.1")
        
        for entry in urls:
            url_elem = ET.SubElement(root, "url")
            
            loc_elem = ET.SubElement(url_elem, "loc")
            loc_elem.text = entry.url
            
            # Add video information
            for video in entry.videos:
                video_elem = ET.SubElement(url_elem, "video:video")
                
                if video.get('thumbnail_loc'):
                    thumbnail = ET.SubElement(video_elem, "video:thumbnail_loc")
                    thumbnail.text = video['thumbnail_loc']
                    
                if video.get('title'):
                    title = ET.SubElement(video_elem, "video:title")
                    title.text = video['title']
                    
                if video.get('description'):
                    desc = ET.SubElement(video_elem, "video:description")
                    desc.text = video['description']
                    
                if video.get('content_loc'):
                    content = ET.SubElement(video_elem, "video:content_loc")
                    content.text = video['content_loc']
                    
                if video.get('duration'):
                    duration = ET.SubElement(video_elem, "video:duration")
                    duration.text = str(video['duration'])
                    
        return self._format_xml(root)
    
    def _generate_news_sitemap(self, urls: List[URLEntry]) -> str:
        """Generate news XML sitemap."""
        root = ET.Element("urlset")
        root.set("xmlns", "http://www.sitemaps.org/schemas/sitemap/0.9")
        root.set("xmlns:news", "http://www.google.com/schemas/sitemap-news/0.9")
        
        for entry in urls:
            if not entry.news:
                continue
                
            url_elem = ET.SubElement(root, "url")
            
            loc_elem = ET.SubElement(url_elem, "loc")
            loc_elem.text = entry.url
            
            news_elem = ET.SubElement(url_elem, "news:news")
            
            # Publication info
            pub_elem = ET.SubElement(news_elem, "news:publication")
            name_elem = ET.SubElement(pub_elem, "news:name")
            name_elem.text = entry.news.get('publication_name', 'Ainflue')
            
            lang_elem = ET.SubElement(pub_elem, "news:language")
            lang_elem.text = entry.news.get('language', 'en')
            
            # Publication date
            if entry.news.get('publication_date'):
                pub_date = ET.SubElement(news_elem, "news:publication_date")
                pub_date.text = entry.news['publication_date']
                
            # Title
            if entry.news.get('title'):
                title = ET.SubElement(news_elem, "news:title")
                title.text = entry.news['title']
                
        return self._format_xml(root)
    
    async def _generate_sitemap_index(self,
                                    sitemap_files: List[str],
                                    output_dir: str) -> str:
        """Generate sitemap index file."""
        index_filename = "sitemap_index.xml"
        
        if self.config.compress_sitemaps:
            index_filename += ".gz"
            
        index_filepath = os.path.join(output_dir, index_filename)
        
        root = ET.Element("sitemapindex")
        root.set("xmlns", "http://www.sitemaps.org/schemas/sitemap/0.9")
        
        for sitemap_file in sitemap_files:
            sitemap_elem = ET.SubElement(root, "sitemap")
            
            loc_elem = ET.SubElement(sitemap_elem, "loc")
            loc_elem.text = urljoin(self.base_url, sitemap_file)
            
            lastmod_elem = ET.SubElement(sitemap_elem, "lastmod")
            lastmod_elem.text = datetime.now().isoformat()
            
        xml_content = self._format_xml(root)
        
        # Write index file
        if self.config.compress_sitemaps:
            with gzip.open(index_filepath, 'wt', encoding='utf-8') as f:
                f.write(xml_content)
        else:
            with open(index_filepath, 'w', encoding='utf-8') as f:
                f.write(xml_content)
                
        return index_filename
    
    def _format_xml(self, root: ET.Element) -> str:
        """Format XML with proper declaration and indentation."""
        # Add XML declaration
        xml_str = '<?xml version="1.0" encoding="UTF-8"?>\n'
        xml_str += ET.tostring(root, encoding='unicode')
        return xml_str
    
    def _chunk_urls(self, urls: List[URLEntry]) -> List[List[URLEntry]]:
        """Split URLs into chunks based on limits."""
        chunks = []
        current_chunk = []
        
        for url in urls:
            current_chunk.append(url)
            
            if len(current_chunk) >= self.config.max_urls_per_sitemap:
                chunks.append(current_chunk)
                current_chunk = []
                
        if current_chunk:
            chunks.append(current_chunk)
            
        return chunks
    
    def _validate_url(self, url: str) -> bool:
        """Validate URL format."""
        try:
            result = urlparse(url)
            return all([result.scheme, result.netloc])
        except:
            return False
    
    def _calculate_creator_priority(self, content: Dict[str, Any]) -> float:
        """Calculate SEO priority for creator content."""
        base_priority = 0.5
        
        # Boost for monetizable content
        if content.get('monetizable'):
            base_priority += 0.2
            
        # Boost for recent content
        created_at = content.get('created_at')
        if created_at and isinstance(created_at, datetime):
            days_old = (datetime.now() - created_at).days
            if days_old < 7:
                base_priority += 0.2
            elif days_old < 30:
                base_priority += 0.1
                
        # Boost for popular content
        views = content.get('views', 0)
        if views > 10000:
            base_priority += 0.2
        elif views > 1000:
            base_priority += 0.1
            
        return min(1.0, base_priority)
    
    def _determine_content_frequency(self, content_type: str) -> ChangeFrequency:
        """Determine change frequency based on content type."""
        frequency_map = {
            'blog': ChangeFrequency.WEEKLY,
            'news': ChangeFrequency.DAILY,
            'video': ChangeFrequency.MONTHLY,
            'audio': ChangeFrequency.MONTHLY,
            'image': ChangeFrequency.YEARLY,
            'page': ChangeFrequency.MONTHLY,
            'product': ChangeFrequency.WEEKLY
        }
        
        return frequency_map.get(content_type, ChangeFrequency.MONTHLY)
    
    async def get_sitemap_stats(self) -> Dict[str, Any]:
        """Get comprehensive sitemap statistics."""
        stats = {
            'total_urls': self.total_urls,
            'sitemap_types': {},
            'estimated_files': 0,
            'compression_enabled': self.config.compress_sitemaps
        }
        
        for sitemap_type, urls in self.sitemaps.items():
            if urls:
                stats['sitemap_types'][sitemap_type.value] = {
                    'url_count': len(urls),
                    'estimated_files': max(1, len(urls) // self.config.max_urls_per_sitemap + 1)
                }
                stats['estimated_files'] += stats['sitemap_types'][sitemap_type.value]['estimated_files']
                
        return stats
    
    async def validate_sitemaps(self, sitemap_dir: str) -> Dict[str, Any]:
        """Validate generated sitemap files."""
        validation_results = {
            'valid_files': [],
            'invalid_files': [],
            'total_urls_found': 0,
            'validation_errors': []
        }
        
        try:
            sitemap_files = [f for f in os.listdir(sitemap_dir) 
                           if f.startswith('sitemap') and f.endswith(('.xml', '.xml.gz'))]
            
            for filename in sitemap_files:
                filepath = os.path.join(sitemap_dir, filename)
                
                try:
                    if filename.endswith('.gz'):
                        with gzip.open(filepath, 'rt', encoding='utf-8') as f:
                            content = f.read()
                    else:
                        with open(filepath, 'r', encoding='utf-8') as f:
                            content = f.read()
                            
                    # Parse XML to validate
                    root = ET.fromstring(content)
                    
                    # Count URLs
                    url_count = len(root.findall('.//{http://www.sitemaps.org/schemas/sitemap/0.9}url'))
                    validation_results['total_urls_found'] += url_count
                    
                    validation_results['valid_files'].append({
                        'filename': filename,
                        'url_count': url_count,
                        'file_size': os.path.getsize(filepath)
                    })
                    
                except Exception as e:
                    validation_results['invalid_files'].append({
                        'filename': filename,
                        'error': str(e)
                    })
                    validation_results['validation_errors'].append(f"{filename}: {str(e)}")
                    
        except Exception as e:
            validation_results['validation_errors'].append(f"Directory validation error: {str(e)}")
            
        return validation_results

# Enterprise usage examples and utilities
class SitemapManager:
    """High-level sitemap management for Ainflue platform."""
    
    def __init__(self, base_url: str):
        self.base_url = base_url
        self.generator = None
        
    async def setup_creator_sitemaps(self, 
                                   creators_data: List[Dict[str, Any]],
                                   output_dir: str) -> Dict[str, Any]:
        """Setup sitemaps optimized for creator economy."""
        config = SitemapConfig(
            base_url=self.base_url,
            max_urls_per_sitemap=10000,  # Smaller chunks for creator content
            include_images=True,
            include_videos=True,
            creator_optimization=True
        )
        
        self.generator = XMLSitemapGenerator(config)
        
        total_added = 0
        for creator_data in creators_data:
            creator_id = creator_data.get('id')
            content_urls = creator_data.get('content', [])
            
            added = await self.generator.add_creator_content(creator_id, content_urls)
            total_added += added
            
        results = await self.generator.generate_sitemaps(output_dir)
        results['creators_processed'] = len(creators_data)
        results['total_urls_added'] = total_added
        
        return results