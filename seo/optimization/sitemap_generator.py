"""Sitemap Generator - Dynamic Multilingual SEO Sitemaps

This module provides comprehensive sitemap generation with multilingual support,
dynamic content discovery, and SEO optimization for improved search engine indexing.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import re
import logging
import json
import hashlib
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from enum import Enum
from urllib.parse import urljoin, urlparse
from datetime import datetime, timezone
import xml.etree.ElementTree as ET

logger = logging.getLogger(__name__)


class SitemapType(Enum):
    """Types of sitemaps"""
    
    INDEX = "index"  # Sitemap index file
    PAGES = "pages"  # Regular pages
    IMAGES = "images"  # Image sitemap
    VIDEOS = "videos"  # Video sitemap
    NEWS = "news"  # News sitemap
    MOBILE = "mobile"  # Mobile sitemap


class ChangeFrequency(Enum):
    """Change frequency values for sitemap entries"""
    
    ALWAYS = "always"
    HOURLY = "hourly"
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    YEARLY = "yearly"
    NEVER = "never"


class Priority(Enum):
    """Priority levels for sitemap entries"""
    
    HIGHEST = 1.0
    HIGH = 0.8
    MEDIUM = 0.6
    LOW = 0.4
    LOWEST = 0.2


@dataclass
class SitemapEntry:
    """Individual sitemap entry"""
    url: str
    last_modified: Optional[datetime]
    change_frequency: ChangeFrequency
    priority: Priority
    images: List[Dict[str, str]]
    videos: List[Dict[str, str]]
    alternate_urls: Dict[str, str]  # Language alternatives
    mobile_url: Optional[str]


@dataclass
class SitemapStats:
    """Sitemap generation statistics"""
    total_urls: int
    total_images: int
    total_videos: int
    languages_count: int
    file_size_bytes: int
    generation_time_ms: float
    last_generated: datetime


@dataclass
class SitemapResult:
    """Complete sitemap generation result"""
    sitemap_xml: str
    sitemap_index_xml: str
    individual_sitemaps: Dict[str, str]  # Type -> XML content
    stats: SitemapStats
    validation_errors: List[str]
    optimization_recommendations: List[str]


class SitemapGenerator:
    """
    Advanced sitemap generator with multilingual support, dynamic content discovery,
    and comprehensive SEO optimization for better search engine indexing.
    """
    
    def __init__(self, base_url -> None: str, max_urls_per_sitemap -> None: int = 50000) -> None:
        """
        Initialize the sitemap generator.
        
        Args:
            base_url: Base URL of the website
            max_urls_per_sitemap: Maximum URLs per sitemap file
        """
        self.base_url = base_url.rstrip('/')
        self.max_urls_per_sitemap = max_urls_per_sitemap
        self.namespaces = {
            'sitemap': 'http://www.sitemaps.org/schemas/sitemap/0.9',
            'image': 'http://www.google.com/schemas/sitemap-image/1.1',
            'video': 'http://www.google.com/schemas/sitemap-video/1.1',
            'mobile': 'http://www.google.com/schemas/sitemap-mobile/1.0',
            'news': 'http://www.google.com/schemas/sitemap-news/0.9',
            'xhtml': 'http://www.w3.org/1999/xhtml'
        }
        
    def generate_comprehensive_sitemap(
        self,
        content_data: List[Dict[str, Any]],
        languages: List[str] = ["en"],
        include_images: bool = True,
        include_videos: bool = True,
        include_mobile: bool = True,
        include_news: bool = False,
        custom_entries: Optional[List[SitemapEntry]] = None
    ) -> SitemapResult:
        """
        Generate comprehensive multilingual sitemap with all content types.
        
        Args:
            content_data: List of content data with URLs, metadata, etc.
            languages: List of supported languages
            include_images: Whether to include image sitemap
            include_videos: Whether to include video sitemap  
            include_mobile: Whether to include mobile sitemap
            include_news: Whether to include news sitemap
            custom_entries: Additional custom sitemap entries
            
        Returns:
            SitemapResult with all generated sitemaps and statistics
        """
        try:
            start_time = datetime.now()
            logger.info(f"Generating comprehensive sitemap for {len(content_data)} items in {len(languages)} languages")
            
            # Process content data into sitemap entries
            sitemap_entries = self._process_content_data(content_data, languages)
            
            # Add custom entries if provided
            if custom_entries:
                sitemap_entries.extend(custom_entries)
            
            # Generate individual sitemaps
            individual_sitemaps = {}
            
            # Main pages sitemap
            pages_sitemap = self._generate_pages_sitemap(sitemap_entries)
            individual_sitemaps['pages'] = pages_sitemap
            
            # Image sitemap
            if include_images:
                image_entries = [entry for entry in sitemap_entries if entry.images]
                if image_entries:
                    images_sitemap = self._generate_images_sitemap(image_entries)
                    individual_sitemaps['images'] = images_sitemap
            
            # Video sitemap
            if include_videos:
                video_entries = [entry for entry in sitemap_entries if entry.videos]
                if video_entries:
                    videos_sitemap = self._generate_videos_sitemap(video_entries)
                    individual_sitemaps['videos'] = videos_sitemap
            
            # Mobile sitemap
            if include_mobile:
                mobile_entries = [entry for entry in sitemap_entries if entry.mobile_url]
                if mobile_entries:
                    mobile_sitemap = self._generate_mobile_sitemap(mobile_entries)
                    individual_sitemaps['mobile'] = mobile_sitemap
            
            # News sitemap
            if include_news:
                news_entries = self._filter_news_entries(sitemap_entries)
                if news_entries:
                    news_sitemap = self._generate_news_sitemap(news_entries)
                    individual_sitemaps['news'] = news_sitemap
            
            # Generate sitemap index
            sitemap_index_xml = self._generate_sitemap_index(individual_sitemaps)
            
            # Generate main sitemap (can be the pages sitemap or index)
            main_sitemap_xml = sitemap_index_xml if len(individual_sitemaps) > 1 else pages_sitemap
            
            # Calculate statistics
            end_time = datetime.now()
            stats = self._calculate_stats(sitemap_entries, individual_sitemaps, start_time, end_time)
            
            # Validate sitemaps
            validation_errors = self._validate_sitemaps(individual_sitemaps, sitemap_index_xml)
            
            # Generate optimization recommendations
            optimization_recommendations = self._generate_optimization_recommendations(
                sitemap_entries, stats, validation_errors
            )
            
            return SitemapResult(
                sitemap_xml=main_sitemap_xml,
                sitemap_index_xml=sitemap_index_xml,
                individual_sitemaps=individual_sitemaps,
                stats=stats,
                validation_errors=validation_errors,
                optimization_recommendations=optimization_recommendations
            )
            
        except Exception as e:
            logger.error(f"Error generating sitemap: {str(e)}")
            raise
    
    def _process_content_data(self, content_data: List[Dict[str, Any]], languages: List[str]) -> List[SitemapEntry]:
        """Process content data into sitemap entries"""
        
        sitemap_entries = []
        
        for content in content_data:
            # Extract basic information
            base_url = content.get('url', '')
            if not base_url:
                continue
            
            # Ensure absolute URL
            if not base_url.startswith('http'):
                base_url = urljoin(self.base_url, base_url)
            
            # Determine change frequency and priority based on content type
            content_type = content.get('type', 'page')
            change_freq, priority = self._determine_frequency_and_priority(content_type, content)
            
            # Process last modified date
            last_modified = None
            if 'last_modified' in content:
                if isinstance(content['last_modified'], str):
                    try:
                        last_modified = datetime.fromisoformat(content['last_modified'].replace('Z', '+00:00'))
                    except ValueError:
                        pass
                elif isinstance(content['last_modified'], datetime):
                    last_modified = content['last_modified']
            
            if not last_modified:
                last_modified = datetime.now(timezone.utc)
            
            # Process images
            images = []
            if 'images' in content:
                for img in content['images']:
                    if isinstance(img, str):
                        images.append({
                            'url': self._make_absolute_url(img),
                            'caption': '',
                            'title': content.get('title', '')
                        })
                    elif isinstance(img, dict):
                        images.append({
                            'url': self._make_absolute_url(img.get('url', '')),
                            'caption': img.get('caption', ''),
                            'title': img.get('title', content.get('title', ''))
                        })
            
            # Process videos
            videos = []
            if 'videos' in content:
                for video in content['videos']:
                    if isinstance(video, str):
                        videos.append({
                            'url': self._make_absolute_url(video),
                            'title': content.get('title', ''),
                            'description': content.get('description', '')[:2000],  # Max 2000 chars
                            'thumbnail_url': ''
                        })
                    elif isinstance(video, dict):
                        videos.append({
                            'url': self._make_absolute_url(video.get('url', '')),
                            'title': video.get('title', content.get('title', '')),
                            'description': video.get('description', content.get('description', ''))[:2000],
                            'thumbnail_url': self._make_absolute_url(video.get('thumbnail_url', ''))
                        })
            
            # Process multilingual alternatives
            alternate_urls = {}
            for lang in languages:
                if lang == 'en':
                    continue  # Skip default language
                
                # Generate language-specific URL
                lang_url = self._generate_language_url(base_url, lang, content)
                if lang_url:
                    alternate_urls[lang] = lang_url
            
            # Mobile URL (if different from main URL)
            mobile_url = content.get('mobile_url')
            if mobile_url:
                mobile_url = self._make_absolute_url(mobile_url)
            
            # Create sitemap entry
            entry = SitemapEntry(
                url=base_url,
                last_modified=last_modified,
                change_frequency=change_freq,
                priority=priority,
                images=images,
                videos=videos,
                alternate_urls=alternate_urls,
                mobile_url=mobile_url
            )
            
            sitemap_entries.append(entry)
            
            # Create entries for alternate language versions
            for lang, lang_url in alternate_urls.items():
                lang_entry = SitemapEntry(
                    url=lang_url,
                    last_modified=last_modified,
                    change_frequency=change_freq,
                    priority=Priority.MEDIUM,  # Slightly lower priority for translations
                    images=images,  # Same images
                    videos=videos,  # Same videos
                    alternate_urls={**alternate_urls, 'en': base_url},  # Include original
                    mobile_url=mobile_url
                )
                sitemap_entries.append(lang_entry)
        
        return sitemap_entries
    
    def _determine_frequency_and_priority(self, content_type: str, content: Dict[str, Any]) -> Tuple[ChangeFrequency, Priority]:
        """Determine change frequency and priority based on content type and metadata"""
        
        # Default mappings
        type_mappings = {
            'homepage': (ChangeFrequency.DAILY, Priority.HIGHEST),
            'category': (ChangeFrequency.WEEKLY, Priority.HIGH),
            'product': (ChangeFrequency.WEEKLY, Priority.HIGH),
            'article': (ChangeFrequency.MONTHLY, Priority.MEDIUM),
            'blog_post': (ChangeFrequency.MONTHLY, Priority.MEDIUM),
            'news': (ChangeFrequency.DAILY, Priority.HIGH),
            'video': (ChangeFrequency.MONTHLY, Priority.MEDIUM),
            'image': (ChangeFrequency.YEARLY, Priority.LOW),
            'contact': (ChangeFrequency.YEARLY, Priority.LOW),
            'about': (ChangeFrequency.YEARLY, Priority.LOW),
            'terms': (ChangeFrequency.YEARLY, Priority.LOWEST),
            'privacy': (ChangeFrequency.YEARLY, Priority.LOWEST)
        }
        
        # Check for explicit settings in content
        if 'change_frequency' in content:
            try:
                change_freq = ChangeFrequency(content['change_frequency'])
            except ValueError:
                change_freq = type_mappings.get(content_type, (ChangeFrequency.MONTHLY, Priority.MEDIUM))[0]
        else:
            change_freq = type_mappings.get(content_type, (ChangeFrequency.MONTHLY, Priority.MEDIUM))[0]
        
        if 'priority' in content:
            try:
                priority = Priority(float(content['priority']))
            except (ValueError, TypeError):
                priority = type_mappings.get(content_type, (ChangeFrequency.MONTHLY, Priority.MEDIUM))[1]
        else:
            priority = type_mappings.get(content_type, (ChangeFrequency.MONTHLY, Priority.MEDIUM))[1]
        
        # Adjust based on recency
        if 'last_modified' in content:
            try:
                last_mod = datetime.fromisoformat(content['last_modified'].replace('Z', '+00:00'))
                days_old = (datetime.now(timezone.utc) - last_mod).days
                
                # Boost priority for recent content
                if days_old < 7:
                    if priority.value < 0.8:
                        priority = Priority.HIGH
                elif days_old < 30:
                    if priority.value < 0.6:
                        priority = Priority.MEDIUM
            except (ValueError, AttributeError):
                pass
        
        return change_freq, priority
    
    def _generate_language_url(self, base_url: str, language: str, content: Dict[str, Any]) -> str:
        """Generate language-specific URL"""
        
        # Check if explicit language URL is provided
        if f'url_{language}' in content:
            return self._make_absolute_url(content[f'url_{language}'])
        
        # Generate based on URL structure patterns
        parsed = urlparse(base_url)
        
        # Pattern 1: Subdirectory (e.g., /fr/page)
        if language != 'en':
            path = f"/{language}{parsed.path}"
            if path.endswith('//'):
                path = path[:-1]
            
            lang_url = f"{parsed.scheme}://{parsed.netloc}{path}"
            if parsed.query:
                lang_url += f"?{parsed.query}"
            if parsed.fragment:
                lang_url += f"#{parsed.fragment}"
            
            return lang_url
        
        return base_url
    
    def _make_absolute_url(self, url: str) -> str:
        """Ensure URL is absolute"""
        if not url:
            return url
        
        if url.startswith('http'):
            return url
        
        return urljoin(self.base_url, url)
    
    def _generate_pages_sitemap(self, entries: List[SitemapEntry]) -> str:
        """Generate main pages sitemap"""
        
        # Create XML structure
        urlset = ET.Element('urlset')
        urlset.set('xmlns', self.namespaces['sitemap'])
        urlset.set('xmlns:xhtml', self.namespaces['xhtml'])
        
        for entry in entries:
            url_elem = ET.SubElement(urlset, 'url')
            
            # Location
            loc_elem = ET.SubElement(url_elem, 'loc')
            loc_elem.text = entry.url
            
            # Last modified
            if entry.last_modified:
                lastmod_elem = ET.SubElement(url_elem, 'lastmod')
                lastmod_elem.text = entry.last_modified.strftime('%Y-%m-%dT%H:%M:%S%z')
            
            # Change frequency
            changefreq_elem = ET.SubElement(url_elem, 'changefreq')
            changefreq_elem.text = entry.change_frequency.value
            
            # Priority
            priority_elem = ET.SubElement(url_elem, 'priority')
            priority_elem.text = str(entry.priority.value)
            
            # Alternate language links
            for lang, alt_url in entry.alternate_urls.items():
                alternate_elem = ET.SubElement(url_elem, 'xhtml:link')
                alternate_elem.set('rel', 'alternate')
                alternate_elem.set('hreflang', lang)
                alternate_elem.set('href', alt_url)
        
        return self._xml_to_string(urlset)
    
    def _generate_images_sitemap(self, entries: List[SitemapEntry]) -> str:
        """Generate image sitemap"""
        
        urlset = ET.Element('urlset')
        urlset.set('xmlns', self.namespaces['sitemap'])
        urlset.set('xmlns:image', self.namespaces['image'])
        
        for entry in entries:
            if not entry.images:
                continue
            
            url_elem = ET.SubElement(urlset, 'url')
            
            # Location
            loc_elem = ET.SubElement(url_elem, 'loc')
            loc_elem.text = entry.url
            
            # Images
            for img in entry.images:
                if not img.get('url'):
                    continue
                
                image_elem = ET.SubElement(url_elem, 'image:image')
                
                # Image location
                img_loc_elem = ET.SubElement(image_elem, 'image:loc')
                img_loc_elem.text = img['url']
                
                # Image title
                if img.get('title'):
                    img_title_elem = ET.SubElement(image_elem, 'image:title')
                    img_title_elem.text = img['title']
                
                # Image caption
                if img.get('caption'):
                    img_caption_elem = ET.SubElement(image_elem, 'image:caption')
                    img_caption_elem.text = img['caption']
        
        return self._xml_to_string(urlset)
    
    def _generate_videos_sitemap(self, entries: List[SitemapEntry]) -> str:
        """Generate video sitemap"""
        
        urlset = ET.Element('urlset')
        urlset.set('xmlns', self.namespaces['sitemap'])
        urlset.set('xmlns:video', self.namespaces['video'])
        
        for entry in entries:
            if not entry.videos:
                continue
            
            url_elem = ET.SubElement(urlset, 'url')
            
            # Location
            loc_elem = ET.SubElement(url_elem, 'loc')
            loc_elem.text = entry.url
            
            # Videos
            for video in entry.videos:
                if not video.get('url'):
                    continue
                
                video_elem = ET.SubElement(url_elem, 'video:video')
                
                # Video thumbnail
                if video.get('thumbnail_url'):
                    thumbnail_elem = ET.SubElement(video_elem, 'video:thumbnail_loc')
                    thumbnail_elem.text = video['thumbnail_url']
                
                # Video title
                if video.get('title'):
                    title_elem = ET.SubElement(video_elem, 'video:title')
                    title_elem.text = video['title']
                
                # Video description
                if video.get('description'):
                    desc_elem = ET.SubElement(video_elem, 'video:description')
                    desc_elem.text = video['description']
                
                # Video content location
                content_elem = ET.SubElement(video_elem, 'video:content_loc')
                content_elem.text = video['url']
        
        return self._xml_to_string(urlset)
    
    def _generate_mobile_sitemap(self, entries: List[SitemapEntry]) -> str:
        """Generate mobile sitemap"""
        
        urlset = ET.Element('urlset')
        urlset.set('xmlns', self.namespaces['sitemap'])
        urlset.set('xmlns:mobile', self.namespaces['mobile'])
        
        for entry in entries:
            if not entry.mobile_url:
                continue
            
            url_elem = ET.SubElement(urlset, 'url')
            
            # Location (mobile URL)
            loc_elem = ET.SubElement(url_elem, 'loc')
            loc_elem.text = entry.mobile_url
            
            # Mobile indicator
            mobile_elem = ET.SubElement(url_elem, 'mobile:mobile')
        
        return self._xml_to_string(urlset)
    
    def _filter_news_entries(self, entries: List[SitemapEntry]) -> List[SitemapEntry]:
        """Filter entries for news sitemap (recent articles/news)"""
        
        cutoff_date = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
        cutoff_date = cutoff_date.replace(day=cutoff_date.day - 2)  # Last 48 hours for news
        
        news_entries = []
        
        for entry in entries:
            # Check if it's recent enough for news
            if entry.last_modified and entry.last_modified >= cutoff_date:
                # Check if URL suggests it's news content
                if any(keyword in entry.url.lower() for keyword in ['news', 'article', 'blog', 'press']):
                    news_entries.append(entry)
        
        return news_entries
    
    def _generate_news_sitemap(self, entries: List[SitemapEntry]) -> str:
        """Generate news sitemap"""
        
        urlset = ET.Element('urlset')
        urlset.set('xmlns', self.namespaces['sitemap'])
        urlset.set('xmlns:news', self.namespaces['news'])
        
        for entry in entries:
            url_elem = ET.SubElement(urlset, 'url')
            
            # Location
            loc_elem = ET.SubElement(url_elem, 'loc')
            loc_elem.text = entry.url
            
            # News information
            news_elem = ET.SubElement(url_elem, 'news:news')
            
            # Publication
            publication_elem = ET.SubElement(news_elem, 'news:publication')
            
            name_elem = ET.SubElement(publication_elem, 'news:name')
            name_elem.text = "Ainflue Platform"
            
            language_elem = ET.SubElement(publication_elem, 'news:language')
            language_elem.text = "en"
            
            # Publication date
            if entry.last_modified:
                pub_date_elem = ET.SubElement(news_elem, 'news:publication_date')
                pub_date_elem.text = entry.last_modified.strftime('%Y-%m-%dT%H:%M:%S%z')
        
        return self._xml_to_string(urlset)
    
    def _generate_sitemap_index(self, individual_sitemaps: Dict[str, str]) -> str:
        """Generate sitemap index file"""
        
        sitemapindex = ET.Element('sitemapindex')
        sitemapindex.set('xmlns', self.namespaces['sitemap'])
        
        for sitemap_type, sitemap_content in individual_sitemaps.items():
            sitemap_elem = ET.SubElement(sitemapindex, 'sitemap')
            
            # Sitemap location
            loc_elem = ET.SubElement(sitemap_elem, 'loc')
            loc_elem.text = f"{self.base_url}/sitemap-{sitemap_type}.xml"
            
            # Last modified
            lastmod_elem = ET.SubElement(sitemap_elem, 'lastmod')
            lastmod_elem.text = datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%S%z')
        
        return self._xml_to_string(sitemapindex)
    
    def _calculate_stats(
        self,
        entries: List[SitemapEntry],
        individual_sitemaps: Dict[str, str],
        start_time: datetime,
        end_time: datetime
    ) -> SitemapStats:
        """Calculate sitemap generation statistics"""
        
        total_urls = len(entries)
        total_images = sum(len(entry.images) for entry in entries)
        total_videos = sum(len(entry.videos) for entry in entries)
        
        # Count unique languages
        languages = set()
        for entry in entries:
            for lang in entry.alternate_urls.keys():
                languages.add(lang)
        languages.add('en')  # Default language
        
        # Calculate total file size
        total_size = sum(len(content.encode('utf-8')) for content in individual_sitemaps.values())
        
        generation_time = (end_time - start_time).total_seconds() * 1000
        
        return SitemapStats(
            total_urls=total_urls,
            total_images=total_images,
            total_videos=total_videos,
            languages_count=len(languages),
            file_size_bytes=total_size,
            generation_time_ms=generation_time,
            last_generated=end_time
        )
    
    def _validate_sitemaps(self, individual_sitemaps: Dict[str, str], sitemap_index: str) -> List[str]:
        """Validate generated sitemaps for common issues"""
        
        errors = []
        
        # Validate URL count limits
        for sitemap_type, content in individual_sitemaps.items():
            url_count = content.count('<url>')
            if url_count > self.max_urls_per_sitemap:
                errors.append(f"{sitemap_type} sitemap has {url_count} URLs, exceeding limit of {self.max_urls_per_sitemap}")
        
        # Validate XML structure
        for sitemap_type, content in individual_sitemaps.items():
            try:
                ET.fromstring(content)
            except ET.ParseError as e:
                errors.append(f"{sitemap_type} sitemap has invalid XML: {str(e)}")
        
        # Validate sitemap index
        try:
            ET.fromstring(sitemap_index)
        except ET.ParseError as e:
            errors.append(f"Sitemap index has invalid XML: {str(e)}")
        
        # Check for duplicate URLs
        all_urls = set()
        duplicates = []
        
        for sitemap_type, content in individual_sitemaps.items():
            urls = re.findall(r'<loc>(.*?)</loc>', content)
            for url in urls:
                if url in all_urls:
                    duplicates.append(url)
                all_urls.add(url)
        
        if duplicates:
            errors.append(f"Duplicate URLs found: {', '.join(duplicates[:5])}")
        
        return errors
    
    def _generate_optimization_recommendations(
        self,
        entries: List[SitemapEntry],
        stats: SitemapStats,
        validation_errors: List[str]
    ) -> List[str]:
        """Generate optimization recommendations"""
        
        recommendations = []
        
        # File size recommendations
        if stats.file_size_bytes > 50 * 1024 * 1024:  # 50MB
            recommendations.append("Consider splitting sitemap into smaller files for better performance")
        
        # URL count recommendations
        if stats.total_urls > self.max_urls_per_sitemap:
            recommendations.append("Split sitemap into multiple files to stay within URL limits")
        
        # Language recommendations
        if stats.languages_count > 1:
            recommendations.append("Implement hreflang tags in HTML pages to complement sitemap language information")
        
        # Image/video recommendations
        if stats.total_images > 1000:
            recommendations.append("Consider creating separate image sitemaps for better organization")
        
        if stats.total_videos > 100:
            recommendations.append("Ensure video thumbnails are properly optimized for sitemap display")
        
        # Priority distribution
        priority_distribution = {}
        for entry in entries:
            priority = entry.priority.value
            priority_distribution[priority] = priority_distribution.get(priority, 0) + 1
        
        highest_priority_count = priority_distribution.get(1.0, 0)
        if highest_priority_count > len(entries) * 0.1:  # More than 10% have highest priority
            recommendations.append("Review priority distribution - too many pages have highest priority")
        
        # Change frequency recommendations
        daily_count = sum(1 for entry in entries if entry.change_frequency == ChangeFrequency.DAILY)
        if daily_count > len(entries) * 0.2:  # More than 20% update daily
            recommendations.append("Review change frequency settings - many pages set to update daily")
        
        # Validation error recommendations
        if validation_errors:
            recommendations.append("Fix XML validation errors to ensure proper sitemap functionality")
        
        # General recommendations
        recommendations.extend([
            "Submit sitemap to Google Search Console and Bing Webmaster Tools",
            "Monitor sitemap access logs to ensure search engines are crawling effectively",
            "Update sitemap whenever new content is published or modified",
            "Consider implementing automatic sitemap generation for dynamic content"
        ])
        
        return recommendations
    
    def _xml_to_string(self, element: ET.Element) -> str:
        """Convert XML element to formatted string"""
        
        # Create a rough string representation
        xml_str = ET.tostring(element, encoding='unicode')
        
        # Add XML declaration
        xml_declaration = '<?xml version="1.0" encoding="UTF-8"?>\n'
        
        return xml_declaration + xml_str
    
    def export_sitemap_files(self, result: SitemapResult, output_directory: str) -> Dict[str, str]:
        """Export sitemap files to directory"""
        
        import os
        
        exported_files = {}
        
        # Ensure output directory exists
        os.makedirs(output_directory, exist_ok=True)
        
        # Export individual sitemaps
        for sitemap_type, content in result.individual_sitemaps.items():
            filename = f"sitemap-{sitemap_type}.xml"
            filepath = os.path.join(output_directory, filename)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            
            exported_files[sitemap_type] = filepath
        
        # Export sitemap index
        if result.sitemap_index_xml:
            index_filepath = os.path.join(output_directory, "sitemap-index.xml")
            with open(index_filepath, 'w', encoding='utf-8') as f:
                f.write(result.sitemap_index_xml)
            exported_files['index'] = index_filepath
        
        # Export main sitemap
        main_filepath = os.path.join(output_directory, "sitemap.xml")
        with open(main_filepath, 'w', encoding='utf-8') as f:
            f.write(result.sitemap_xml)
        exported_files['main'] = main_filepath
        
        return exported_files
    
    def generate_robots_txt(self, sitemap_urls: List[str], additional_rules: Optional[Dict[str, List[str]]] = None) -> str:
        """Generate robots.txt file with sitemap references"""
        
        robots_content = []
        
        # User-agent rules
        robots_content.append("User-agent: *")
        robots_content.append("Allow: /")
        
        # Add additional rules if provided
        if additional_rules:
            for user_agent, rules in additional_rules.items():
                robots_content.append(f"\nUser-agent: {user_agent}")
                for rule in rules:
                    robots_content.append(rule)
        
        # Common disallow patterns
        robots_content.extend([
            "\n# Disallow common admin/private areas",
            "Disallow: /admin/",
            "Disallow: /private/",
            "Disallow: /tmp/",
            "Disallow: /*.json$",
            "Disallow: /*.xml$",
            "Disallow: /*?print=1",
            "Disallow: /*?utm_*"
        ])
        
        # Sitemap references
        robots_content.append("\n# Sitemaps")
        for sitemap_url in sitemap_urls:
            if not sitemap_url.startswith('http'):
                sitemap_url = urljoin(self.base_url, sitemap_url)
            robots_content.append(f"Sitemap: {sitemap_url}")
        
        return '\n'.join(robots_content)


# Export for module usage
__all__ = [
    "SitemapGenerator",
    "SitemapType",
    "ChangeFrequency",
    "Priority",
    "SitemapEntry",
    "SitemapStats",
    "SitemapResult"
]