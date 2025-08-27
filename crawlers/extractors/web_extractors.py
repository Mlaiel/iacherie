"""
Web Extractors - Industrial IA Web Content Processing System
===========================================================

Ultra-advanced professional web content extractors for HTML, web pages, and online resources.
Implements enterprise-grade web scraping, content analysis, and metadata extraction capabilities with AI.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: All rights reserved. Unauthorized use, reproduction, or distribution prohibited.

WARNING: This code is protected by copyright law. Any unauthorized copying, 
distribution, or modification is strictly prohibited and will result in 
legal action. Contact mlaiel@live.de for licensing.

⚠️ STRICT COPYRIGHT PROTECTION ⚠️
This code is the intellectual property of Fahed Mlaiel (mlaiel@live.de).
UNAUTHORIZED USE STRICTLY PROHIBITED - Legal action will be taken.

Technical Team Expertise:
- Lead IA Developer: Advanced AI/ML algorithms and neural networks
- Backend Senior: Enterprise architecture and microservices
- ML Engineer: Machine learning pipelines and model optimization
- Database Administrator: Data architecture and optimization
- Security Specialist: Cybersecurity and data protection
- Microservices Architect: Distributed systems and scalability
- Audio Engineer: Digital signal processing and audio analysis
- DevOps Engineer: Infrastructure automation and deployment
- IA Prompt Engineer: Prompt optimization and AI interaction

Project Owner: Fahed Mlaiel - mlaiel@live.de
"""

import asyncio
import logging
import re
import time
import hashlib
from typing import Dict, List, Optional, Any, Union, Tuple, Set
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from urllib.parse import urljoin, urlparse, parse_qs, unquote
from pathlib import Path
import mimetypes
import base64

# Import core extraction components
from .extraction_engine import BaseExtractor, ExtractionRequest, ExtractionResult, ExtractionStatus, ContentType

# Import third-party libraries conditionally
try:
    import aiohttp
    import aiofiles
    HAS_AIOHTTP = True
except ImportError:
    HAS_AIOHTTP = False

try:
    from bs4 import BeautifulSoup, Tag, NavigableString
    import bs4
    HAS_BS4 = True
except ImportError:
    HAS_BS4 = False

try:
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.chrome.options import Options
    from selenium.common.exceptions import TimeoutException, WebDriverException
    HAS_SELENIUM = True
except ImportError:
    HAS_SELENIUM = False

try:
    import requests
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False

try:
    from readability import Document
    HAS_READABILITY = True
except ImportError:
    HAS_READABILITY = False

try:
    import trafilatura
    HAS_TRAFILATURA = True
except ImportError:
    HAS_TRAFILATURA = False

logger = logging.getLogger(__name__)


@dataclass
class WebMetadata:
    """Web content metadata container"""
    
    url: Optional[str] = None
    canonical_url: Optional[str] = None
    title: Optional[str] = None
    description: Optional[str] = None
    author: Optional[str] = None
    published_date: Optional[datetime] = None
    modified_date: Optional[datetime] = None
    language: Optional[str] = None
    keywords: List[str] = field(default_factory=list)
    category: Optional[str] = None
    site_name: Optional[str] = None
    content_type: Optional[str] = None
    word_count: int = 0
    reading_time: int = 0
    social_media: Dict[str, Any] = field(default_factory=dict)
    seo_data: Dict[str, Any] = field(default_factory=dict)
    performance_metrics: Dict[str, Any] = field(default_factory=dict)


@dataclass
class LinkData:
    """Link metadata container"""
    
    url: str
    text: Optional[str] = None
    title: Optional[str] = None
    is_internal: bool = False
    is_external: bool = False
    link_type: Optional[str] = None  # anchor, image, stylesheet, script, etc.
    status_code: Optional[int] = None
    target: Optional[str] = None
    rel: List[str] = field(default_factory=list)


class BaseWebExtractor(BaseExtractor):
    """Base class for web content extractors"""
    
    def __init__(self, name: str):
        super().__init__(name)
        self.session_timeout = 30
        self.max_content_size = 50 * 1024 * 1024  # 50MB
        self.user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        
    async def create_session(self) -> Optional[aiohttp.ClientSession]:
        """Create HTTP session with proper configuration"""
        if not HAS_AIOHTTP:
            return None
        
        connector = aiohttp.TCPConnector(
            limit=100,
            limit_per_host=30,
            ttl_dns_cache=300,
            use_dns_cache=True,
            ssl=False  # For development - should be True in production
        )
        
        timeout = aiohttp.ClientTimeout(total=self.session_timeout)
        
        headers = {
            'User-Agent': self.user_agent,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Cache-Control': 'no-cache'
        }
        
        return aiohttp.ClientSession(
            connector=connector,
            timeout=timeout,
            headers=headers
        )
    
    async def fetch_content(self, url: str, session: aiohttp.ClientSession) -> Tuple[str, Dict[str, Any]]:
        """Fetch web content with metadata"""
        try:
            async with session.get(url) as response:
                if response.status >= 400:
                    raise aiohttp.ClientError(f"HTTP {response.status}: {response.reason}")
                
                content = await response.text()
                
                metadata = {
                    'status_code': response.status,
                    'headers': dict(response.headers),
                    'content_type': response.headers.get('content-type', ''),
                    'content_length': len(content),
                    'final_url': str(response.url),
                    'response_time': response.headers.get('server-timing', ''),
                    'encoding': response.charset or 'utf-8'
                }
                
                return content, metadata
                
        except Exception as e:
            self.logger.error(f"Failed to fetch content from {url}: {str(e)}")
            raise


class HTMLExtractor(BaseWebExtractor):
    """Advanced HTML content extractor"""
    
    def __init__(self):
        super().__init__("HTMLExtractor")
        
    async def can_handle(self, request: ExtractionRequest) -> bool:
        """Check if request contains HTML content"""
        if request.source_url:
            return True  # Can try to fetch any URL
        
        if request.source_data:
            try:
                content = request.source_data.decode('utf-8')
                return '<html' in content.lower() or '<!doctype html' in content.lower()
            except UnicodeDecodeError:
                return False
        
        return False
    
    async def extract(self, request: ExtractionRequest) -> ExtractionResult:
        """Extract HTML content and metadata"""
        try:
            content = ""
            fetch_metadata = {}
            
            # Get content
            if request.source_url:
                if HAS_AIOHTTP:
                    session = await self.create_session()
                    content, fetch_metadata = await self.fetch_content(request.source_url, session)
                    await session.close()
                else:
                    return ExtractionResult(
                        request_id=request.request_id,
                        status=ExtractionStatus.FAILED,
                        error="HTTP client not available"
                    )
            elif request.source_data:
                content = request.source_data.decode('utf-8')
            else:
                return ExtractionResult(
                    request_id=request.request_id,
                    status=ExtractionStatus.FAILED,
                    error="No data source provided"
                )
            
            # Parse HTML
            if not HAS_BS4:
                return ExtractionResult(
                    request_id=request.request_id,
                    status=ExtractionStatus.FAILED,
                    error="HTML parser not available"
                )
            
            soup = BeautifulSoup(content, 'html.parser')
            
            # Extract comprehensive HTML data
            extracted_data = await self._process_html(soup, content, request.source_url)
            extracted_data.update(fetch_metadata)
            
            # Extract web metadata
            web_meta = await self._extract_web_metadata(soup, request.source_url)
            
            return ExtractionResult(
                request_id=request.request_id,
                status=ExtractionStatus.COMPLETED,
                extracted_data=extracted_data,
                metadata={"web": web_meta},
                content_type=ContentType.TEXT,
                processing_time=time.time() - time.time()
            )
            
        except Exception as e:
            self.logger.error(f"HTML extraction failed: {str(e)}")
            return ExtractionResult(
                request_id=request.request_id,
                status=ExtractionStatus.FAILED,
                error=str(e)
            )
    
    async def _process_html(self, soup: BeautifulSoup, content: str, url: Optional[str]) -> Dict[str, Any]:
        """Process HTML content comprehensively"""
        result = {
            'type': 'html',
            'url': url,
            'raw_html': content,
            'html_size': len(content)
        }
        
        # Extract basic structure
        result.update(await self._extract_html_structure(soup))
        
        # Extract text content
        result.update(await self._extract_text_content(soup))
        
        # Extract metadata tags
        result.update(await self._extract_meta_tags(soup))
        
        # Extract links
        result['links'] = await self._extract_links(soup, url)
        
        # Extract media elements
        result['media'] = await self._extract_media_elements(soup, url)
        
        # Extract forms
        result['forms'] = await self._extract_forms(soup)
        
        # Extract structured data
        result['structured_data'] = await self._extract_structured_data(soup)
        
        # Performance analysis
        result['performance'] = await self._analyze_performance(soup, content)
        
        # SEO analysis
        result['seo'] = await self._analyze_seo(soup, content)
        
        return result
    
    async def _extract_html_structure(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """Extract HTML document structure"""
        return {
            'doctype': self._extract_doctype(soup),
            'html_tag': soup.html.attrs if soup.html else {},
            'head_tags': len(soup.head.find_all() if soup.head else []),
            'body_tags': len(soup.body.find_all() if soup.body else []),
            'total_tags': len(soup.find_all()),
            'unique_tags': len(set(tag.name for tag in soup.find_all() if tag.name)),
            'nesting_depth': self._calculate_nesting_depth(soup),
            'comments': len(soup.find_all(string=lambda text: isinstance(text, bs4.Comment)))
        }
    
    def _extract_doctype(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract DOCTYPE declaration"""
        for item in soup.contents:
            if isinstance(item, bs4.Doctype):
                return str(item)
        return None
    
    def _calculate_nesting_depth(self, soup: BeautifulSoup, max_depth: int = 20) -> int:
        """Calculate maximum nesting depth of HTML elements"""
        def get_depth(element, current_depth=0):
            if current_depth > max_depth:
                return current_depth
            
            if hasattr(element, 'children'):
                depths = [get_depth(child, current_depth + 1) for child in element.children if hasattr(child, 'name')]
                return max(depths) if depths else current_depth
            return current_depth
        
        return get_depth(soup)
    
    async def _extract_text_content(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """Extract and analyze text content"""
        # Get clean text
        text = soup.get_text(separator=' ', strip=True)
        
        # Extract specific text elements
        headings = {}
        for i in range(1, 7):
            heading_tags = soup.find_all(f'h{i}')
            headings[f'h{i}'] = [tag.get_text(strip=True) for tag in heading_tags]
        
        paragraphs = [p.get_text(strip=True) for p in soup.find_all('p')]
        
        # Text statistics
        words = text.split()
        word_count = len(words)
        char_count = len(text)
        sentence_count = len(re.split(r'[.!?]+', text))
        
        return {
            'text_content': text,
            'headings': headings,
            'paragraphs': paragraphs[:10],  # Sample first 10 paragraphs
            'word_count': word_count,
            'character_count': char_count,
            'sentence_count': sentence_count,
            'reading_time': max(1, word_count // 200),  # Assume 200 WPM
            'text_density': word_count / len(soup.find_all()) if soup.find_all() else 0
        }
    
    async def _extract_meta_tags(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """Extract meta tags and document metadata"""
        meta_data = {
            'title': soup.title.string if soup.title else None,
            'meta_tags': {},
            'og_tags': {},
            'twitter_tags': {},
            'schema_org': []
        }
        
        # Extract meta tags
        for meta in soup.find_all('meta'):
            name = meta.get('name') or meta.get('property') or meta.get('http-equiv')
            content = meta.get('content')
            
            if name and content:
                if name.startswith('og:'):
                    meta_data['og_tags'][name] = content
                elif name.startswith('twitter:'):
                    meta_data['twitter_tags'][name] = content
                else:
                    meta_data['meta_tags'][name] = content
        
        # Extract link tags
        meta_data['link_tags'] = {}
        for link in soup.find_all('link'):
            rel = link.get('rel')
            href = link.get('href')
            if rel and href:
                rel_str = ' '.join(rel) if isinstance(rel, list) else rel
                meta_data['link_tags'][rel_str] = href
        
        return meta_data
    
    async def _extract_links(self, soup: BeautifulSoup, base_url: Optional[str]) -> List[LinkData]:
        """Extract and analyze all links"""
        links = []
        
        for link in soup.find_all('a', href=True):
            href = link['href']
            
            # Resolve relative URLs
            if base_url:
                absolute_url = urljoin(base_url, href)
            else:
                absolute_url = href
            
            # Determine link type
            parsed_base = urlparse(base_url) if base_url else None
            parsed_link = urlparse(absolute_url)
            
            is_internal = (parsed_base and parsed_link.netloc == parsed_base.netloc) if parsed_base else False
            is_external = parsed_link.netloc and not is_internal
            
            link_data = LinkData(
                url=absolute_url,
                text=link.get_text(strip=True),
                title=link.get('title'),
                is_internal=is_internal,
                is_external=is_external,
                link_type='anchor',
                target=link.get('target'),
                rel=link.get('rel', [])
            )
            
            links.append(link_data)
        
        return links
    
    async def _extract_media_elements(self, soup: BeautifulSoup, base_url: Optional[str]) -> Dict[str, List[Dict[str, Any]]]:
        """Extract media elements (images, videos, audio)"""
        media = {
            'images': [],
            'videos': [],
            'audio': [],
            'iframes': []
        }
        
        # Extract images
        for img in soup.find_all('img'):
            src = img.get('src') or img.get('data-src')
            if src:
                if base_url:
                    src = urljoin(base_url, src)
                
                media['images'].append({
                    'src': src,
                    'alt': img.get('alt'),
                    'title': img.get('title'),
                    'width': img.get('width'),
                    'height': img.get('height'),
                    'loading': img.get('loading'),
                    'srcset': img.get('srcset')
                })
        
        # Extract videos
        for video in soup.find_all('video'):
            src = video.get('src')
            if not src:
                source = video.find('source')
                src = source.get('src') if source else None
            
            if src and base_url:
                src = urljoin(base_url, src)
            
            media['videos'].append({
                'src': src,
                'controls': video.has_attr('controls'),
                'autoplay': video.has_attr('autoplay'),
                'loop': video.has_attr('loop'),
                'muted': video.has_attr('muted'),
                'width': video.get('width'),
                'height': video.get('height')
            })
        
        # Extract audio
        for audio in soup.find_all('audio'):
            src = audio.get('src')
            if not src:
                source = audio.find('source')
                src = source.get('src') if source else None
            
            if src and base_url:
                src = urljoin(base_url, src)
            
            media['audio'].append({
                'src': src,
                'controls': audio.has_attr('controls'),
                'autoplay': audio.has_attr('autoplay'),
                'loop': audio.has_attr('loop'),
                'muted': audio.has_attr('muted')
            })
        
        # Extract iframes
        for iframe in soup.find_all('iframe'):
            src = iframe.get('src')
            if src and base_url:
                src = urljoin(base_url, src)
            
            media['iframes'].append({
                'src': src,
                'width': iframe.get('width'),
                'height': iframe.get('height'),
                'title': iframe.get('title'),
                'loading': iframe.get('loading')
            })
        
        return media
    
    async def _extract_forms(self, soup: BeautifulSoup) -> List[Dict[str, Any]]:
        """Extract form information"""
        forms = []
        
        for form in soup.find_all('form'):
            form_data = {
                'action': form.get('action'),
                'method': form.get('method', 'get').lower(),
                'enctype': form.get('enctype'),
                'inputs': [],
                'textareas': [],
                'selects': []
            }
            
            # Extract inputs
            for input_tag in form.find_all('input'):
                form_data['inputs'].append({
                    'type': input_tag.get('type', 'text'),
                    'name': input_tag.get('name'),
                    'id': input_tag.get('id'),
                    'placeholder': input_tag.get('placeholder'),
                    'required': input_tag.has_attr('required'),
                    'value': input_tag.get('value')
                })
            
            # Extract textareas
            for textarea in form.find_all('textarea'):
                form_data['textareas'].append({
                    'name': textarea.get('name'),
                    'id': textarea.get('id'),
                    'placeholder': textarea.get('placeholder'),
                    'required': textarea.has_attr('required'),
                    'rows': textarea.get('rows'),
                    'cols': textarea.get('cols')
                })
            
            # Extract selects
            for select in form.find_all('select'):
                options = [{'value': opt.get('value'), 'text': opt.get_text(strip=True)} 
                          for opt in select.find_all('option')]
                
                form_data['selects'].append({
                    'name': select.get('name'),
                    'id': select.get('id'),
                    'multiple': select.has_attr('multiple'),
                    'required': select.has_attr('required'),
                    'options': options
                })
            
            forms.append(form_data)
        
        return forms
    
    async def _extract_structured_data(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """Extract structured data (JSON-LD, microdata, etc.)"""
        structured_data = {
            'json_ld': [],
            'microdata': [],
            'rdfa': []
        }
        
        # Extract JSON-LD
        for script in soup.find_all('script', type='application/ld+json'):
            try:
                import json
                data = json.loads(script.string)
                structured_data['json_ld'].append(data)
            except (json.JSONDecodeError, TypeError):
                continue
        
        # Extract microdata
        for element in soup.find_all(attrs={'itemscope': True}):
            microdata_item = {
                'itemtype': element.get('itemtype'),
                'properties': {}
            }
            
            for prop in element.find_all(attrs={'itemprop': True}):
                prop_name = prop.get('itemprop')
                prop_value = prop.get('content') or prop.get_text(strip=True)
                microdata_item['properties'][prop_name] = prop_value
            
            structured_data['microdata'].append(microdata_item)
        
        return structured_data
    
    async def _analyze_performance(self, soup: BeautifulSoup, content: str) -> Dict[str, Any]:
        """Analyze page performance metrics"""
        # Count external resources
        external_scripts = len([script for script in soup.find_all('script', src=True) 
                               if script.get('src') and 'http' in script.get('src')])
        
        external_styles = len([link for link in soup.find_all('link', rel='stylesheet') 
                              if link.get('href') and 'http' in link.get('href')])
        
        external_images = len([img for img in soup.find_all('img', src=True) 
                              if img.get('src') and 'http' in img.get('src')])
        
        # Calculate DOM complexity
        total_elements = len(soup.find_all())
        
        return {
            'html_size': len(content),
            'total_elements': total_elements,
            'external_scripts': external_scripts,
            'external_stylesheets': external_styles,
            'external_images': external_images,
            'inline_styles': len(soup.find_all('style')),
            'inline_scripts': len([script for script in soup.find_all('script') if not script.get('src')]),
            'performance_score': self._calculate_performance_score(
                len(content), total_elements, external_scripts + external_styles + external_images
            )
        }
    
    def _calculate_performance_score(self, html_size: int, total_elements: int, external_resources: int) -> float:
        """Calculate simple performance score (0-100)"""
        score = 100
        
        # Deduct for large HTML size
        if html_size > 100000:  # 100KB
            score -= min(30, (html_size - 100000) // 10000)
        
        # Deduct for too many DOM elements
        if total_elements > 1000:
            score -= min(20, (total_elements - 1000) // 100)
        
        # Deduct for too many external resources
        if external_resources > 10:
            score -= min(25, (external_resources - 10) * 2)
        
        return max(0, score)
    
    async def _analyze_seo(self, soup: BeautifulSoup, content: str) -> Dict[str, Any]:
        """Analyze SEO factors"""
        seo_analysis = {
            'title_length': 0,
            'meta_description_length': 0,
            'has_h1': False,
            'h1_count': 0,
            'has_meta_description': False,
            'has_canonical': False,
            'images_without_alt': 0,
            'internal_links': 0,
            'external_links': 0,
            'seo_score': 0
        }
        
        # Title analysis
        title = soup.find('title')
        if title and title.string:
            seo_analysis['title_length'] = len(title.string.strip())
        
        # Meta description
        meta_desc = soup.find('meta', attrs={'name': 'description'})
        if meta_desc and meta_desc.get('content'):
            seo_analysis['has_meta_description'] = True
            seo_analysis['meta_description_length'] = len(meta_desc['content'])
        
        # H1 tags
        h1_tags = soup.find_all('h1')
        seo_analysis['has_h1'] = len(h1_tags) > 0
        seo_analysis['h1_count'] = len(h1_tags)
        
        # Canonical URL
        canonical = soup.find('link', rel='canonical')
        seo_analysis['has_canonical'] = canonical is not None
        
        # Images without alt text
        images = soup.find_all('img')
        seo_analysis['images_without_alt'] = len([img for img in images if not img.get('alt')])
        
        # Calculate SEO score
        seo_analysis['seo_score'] = self._calculate_seo_score(seo_analysis)
        
        return seo_analysis
    
    def _calculate_seo_score(self, analysis: Dict[str, Any]) -> float:
        """Calculate SEO score (0-100)"""
        score = 0
        
        # Title (20 points)
        title_length = analysis['title_length']
        if 30 <= title_length <= 60:
            score += 20
        elif title_length > 0:
            score += 10
        
        # Meta description (20 points)
        if analysis['has_meta_description']:
            desc_length = analysis['meta_description_length']
            if 120 <= desc_length <= 160:
                score += 20
            elif desc_length > 0:
                score += 10
        
        # H1 tag (20 points)
        if analysis['has_h1'] and analysis['h1_count'] == 1:
            score += 20
        elif analysis['has_h1']:
            score += 10
        
        # Canonical URL (10 points)
        if analysis['has_canonical']:
            score += 10
        
        # Images with alt text (15 points)
        if analysis['images_without_alt'] == 0:
            score += 15
        
        # Basic structure (15 points)
        score += 15  # Base points for having analyzable content
        
        return score
    
    async def _extract_web_metadata(self, soup: BeautifulSoup, url: Optional[str]) -> WebMetadata:
        """Extract web-specific metadata"""
        meta_tags = {}
        for meta in soup.find_all('meta'):
            name = meta.get('name') or meta.get('property')
            content = meta.get('content')
            if name and content:
                meta_tags[name] = content
        
        # Extract social media data
        social_media = {}
        for key, value in meta_tags.items():
            if key.startswith('og:') or key.startswith('twitter:'):
                social_media[key] = value
        
        # Calculate reading time
        text = soup.get_text()
        word_count = len(text.split())
        reading_time = max(1, word_count // 200)
        
        return WebMetadata(
            url=url,
            canonical_url=self._extract_canonical_url(soup),
            title=soup.title.string.strip() if soup.title and soup.title.string else None,
            description=meta_tags.get('description'),
            author=meta_tags.get('author'),
            language=meta_tags.get('language') or soup.html.get('lang') if soup.html else None,
            keywords=meta_tags.get('keywords', '').split(',') if meta_tags.get('keywords') else [],
            site_name=meta_tags.get('og:site_name'),
            word_count=word_count,
            reading_time=reading_time,
            social_media=social_media,
            seo_data=await self._analyze_seo(soup, str(soup))
        )
    
    def _extract_canonical_url(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract canonical URL"""
        canonical = soup.find('link', rel='canonical')
        return canonical.get('href') if canonical else None


class ArticleExtractor(BaseWebExtractor):
    """Specialized article content extractor"""
    
    def __init__(self):
        super().__init__("ArticleExtractor")
        
    async def can_handle(self, request: ExtractionRequest) -> bool:
        """Check if request contains article content"""
        # This would typically be used as a secondary extractor
        # after HTML extraction to clean up article content
        return request.source_url is not None
    
    async def extract(self, request: ExtractionRequest) -> ExtractionResult:
        """Extract clean article content"""
        try:
            if not request.source_url:
                return ExtractionResult(
                    request_id=request.request_id,
                    status=ExtractionStatus.FAILED,
                    error="Article extraction requires URL"
                )
            
            # Get raw HTML first
            if HAS_AIOHTTP:
                session = await self.create_session()
                content, fetch_metadata = await self.fetch_content(request.source_url, session)
                await session.close()
            else:
                return ExtractionResult(
                    request_id=request.request_id,
                    status=ExtractionStatus.FAILED,
                    error="HTTP client not available"
                )
            
            # Extract clean article content
            extracted_data = await self._extract_article_content(content, request.source_url)
            extracted_data.update(fetch_metadata)
            
            return ExtractionResult(
                request_id=request.request_id,
                status=ExtractionStatus.COMPLETED,
                extracted_data=extracted_data,
                metadata={},
                content_type=ContentType.TEXT,
                processing_time=time.time() - time.time()
            )
            
        except Exception as e:
            self.logger.error(f"Article extraction failed: {str(e)}")
            return ExtractionResult(
                request_id=request.request_id,
                status=ExtractionStatus.FAILED,
                error=str(e)
            )
    
    async def _extract_article_content(self, html: str, url: str) -> Dict[str, Any]:
        """Extract clean article content using multiple methods"""
        result = {
            'type': 'article',
            'url': url,
            'extraction_methods': {}
        }
        
        # Method 1: Readability
        if HAS_READABILITY:
            try:
                doc = Document(html)
                result['extraction_methods']['readability'] = {
                    'title': doc.title(),
                    'content': doc.summary(),
                    'short_title': doc.short_title()
                }
            except Exception as e:
                self.logger.warning(f"Readability extraction failed: {str(e)}")
        
        # Method 2: Trafilatura
        if HAS_TRAFILATURA:
            try:
                extracted_text = trafilatura.extract(html, include_comments=False, include_tables=True)
                metadata = trafilatura.extract_metadata(html)
                
                result['extraction_methods']['trafilatura'] = {
                    'content': extracted_text,
                    'metadata': {
                        'title': metadata.title if metadata else None,
                        'author': metadata.author if metadata else None,
                        'date': metadata.date if metadata else None,
                        'description': metadata.description if metadata else None,
                        'sitename': metadata.sitename if metadata else None,
                        'tags': metadata.tags if metadata else None,
                        'categories': metadata.categories if metadata else None
                    } if metadata else {}
                }
            except Exception as e:
                self.logger.warning(f"Trafilatura extraction failed: {str(e)}")
        
        # Method 3: Custom extraction with BeautifulSoup
        if HAS_BS4:
            try:
                soup = BeautifulSoup(html, 'html.parser')
                result['extraction_methods']['custom'] = await self._custom_article_extraction(soup)
            except Exception as e:
                self.logger.warning(f"Custom extraction failed: {str(e)}")
        
        # Combine results
        result['combined'] = await self._combine_extraction_results(result['extraction_methods'])
        
        return result
    
    async def _custom_article_extraction(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """Custom article extraction logic"""
        # Remove script and style elements
        for script in soup(["script", "style"]):
            script.decompose()
        
        # Look for article-like containers
        article_selectors = [
            'article',
            '.article-content',
            '.post-content',
            '.entry-content',
            '.content',
            '#content',
            'main',
            '.main-content'
        ]
        
        article_content = None
        for selector in article_selectors:
            element = soup.select_one(selector)
            if element:
                article_content = element
                break
        
        if not article_content:
            # Fallback to body
            article_content = soup.body or soup
        
        # Extract text with structure
        paragraphs = [p.get_text(strip=True) for p in article_content.find_all('p') if p.get_text(strip=True)]
        headings = {}
        for i in range(1, 7):
            headings[f'h{i}'] = [h.get_text(strip=True) for h in article_content.find_all(f'h{i}')]
        
        # Extract article metadata
        title = soup.find('h1')
        if title:
            title = title.get_text(strip=True)
        else:
            title = soup.title.string if soup.title else None
        
        return {
            'title': title,
            'content': '\n\n'.join(paragraphs),
            'paragraphs': paragraphs,
            'headings': headings,
            'word_count': len(' '.join(paragraphs).split()),
            'reading_time': max(1, len(' '.join(paragraphs).split()) // 200)
        }
    
    async def _combine_extraction_results(self, methods: Dict[str, Dict]) -> Dict[str, Any]:
        """Combine results from different extraction methods"""
        combined = {
            'title': None,
            'content': None,
            'author': None,
            'date': None,
            'word_count': 0,
            'reading_time': 0,
            'confidence_score': 0.0
        }
        
        # Prioritize extraction methods
        method_priority = ['trafilatura', 'readability', 'custom']
        
        for method in method_priority:
            if method in methods and methods[method]:
                data = methods[method]
                
                # Title
                if not combined['title'] and ('title' in data and data['title']):
                    combined['title'] = data['title']
                
                # Content
                if not combined['content'] and ('content' in data and data['content']):
                    combined['content'] = data['content']
                
                # Author
                if not combined['author']:
                    if method == 'trafilatura' and 'metadata' in data:
                        combined['author'] = data['metadata'].get('author')
                
                # Date
                if not combined['date']:
                    if method == 'trafilatura' and 'metadata' in data:
                        combined['date'] = data['metadata'].get('date')
        
        # Calculate final metrics
        if combined['content']:
            words = combined['content'].split()
            combined['word_count'] = len(words)
            combined['reading_time'] = max(1, len(words) // 200)
        
        # Calculate confidence score based on available data
        score = 0
        if combined['title']:
            score += 25
        if combined['content'] and len(combined['content']) > 100:
            score += 50
        if combined['author']:
            score += 10
        if combined['date']:
            score += 10
        if combined['word_count'] > 50:
            score += 5
        
        combined['confidence_score'] = score / 100.0
        
        return combined


# Web Extractor Factory
class WebExtractorFactory:
    """Factory for creating web extractors"""
    
    _extractors: List[BaseWebExtractor] = []
    
    @classmethod
    def register_extractor(cls, extractor: BaseWebExtractor):
        """Register a web extractor"""
        cls._extractors.append(extractor)
    
    @classmethod
    def get_extractor(cls, request: ExtractionRequest) -> Optional[BaseWebExtractor]:
        """Get appropriate extractor for request"""
        for extractor in cls._extractors:
            if asyncio.run(extractor.can_handle(request)):
                return extractor
        return None
    
    @classmethod
    def get_extractors_for_url(cls, url: str) -> List[BaseWebExtractor]:
        """Get all extractors that can handle URL"""
        request = ExtractionRequest(source_url=url)
        return [extractor for extractor in cls._extractors 
                if asyncio.run(extractor.can_handle(request))]


# Register default extractors
def register_default_web_extractors():
    """Register all default web extractors"""
    factory = WebExtractorFactory
    
    factory.register_extractor(HTMLExtractor())
    factory.register_extractor(ArticleExtractor())


# Initialize on import
register_default_web_extractors()


__all__ = [
    'WebMetadata',
    'LinkData',
    'BaseWebExtractor',
    'HTMLExtractor',
    'ArticleExtractor',
    'WebExtractorFactory',
    'register_default_web_extractors'
]
