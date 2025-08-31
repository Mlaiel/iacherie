"""Content Extractor Module
========================

Professional content extraction for web crawling with AI-powered analysis.
Implements intelligent content parsing, data extraction, and content analysis.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: All rights reserved. Unauthorized use, reproduction, or distribution prohibited.

WARNING: This code is protected by copyright law. Any unauthorized copying, 
distribution, or modification is strictly prohibited and will result in 
legal action. Contact mlaiel@live.de for licensing.
"""
import re
import asyncio
import logging
from typing import Dict, List, Optional, Set, Tuple, Any
from dataclasses import dataclass
from datetime import datetime
from urllib.parse import urljoin, urlparse
import html
import json

# Third-party imports
from bs4 import BeautifulSoup, Comment
from readability import Document
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import aiohttp
import langdetect
from textstat import flesch_reading_ease, automated_readability_index
import nltk
from collections import Counter
import base64
from io import BytesIO
from PIL import Image
import hashlib

logger = logging.getLogger(__name__)

@dataclass
class ExtractedContent:
    """Structure for extracted content."""
    title: Optional[str] = None
    description: Optional[str] = None
    content: Optional[str] = None
    clean_text: Optional[str] = None
    metadata: Dict[str, Any] = None
    links: List[Dict[str, str]] = None
    images: List[Dict[str, str]] = None
    videos: List[Dict[str, str]] = None
    social_media_links: List[Dict[str, str]] = None
    contact_info: Dict[str, Any] = None
    language: Optional[str] = None
    keywords: List[str] = None
    author: Optional[str] = None
    publish_date: Optional[datetime] = None
    word_count: int = 0
    reading_time_minutes: int = 0
    readability_score: float = 0.0
    sentiment_score: float = 0.0
    content_quality_score: float = 0.0
    fingerprint_hash: Optional[str] = None
    extracted_entities: List[Dict[str, str]] = None
    topic_categories: List[str] = None
    content_type: str = "article"
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}
        if self.links is None:
            self.links = []
        if self.images is None:
            self.images = []
        if self.videos is None:
            self.videos = []
        if self.social_media_links is None:
            self.social_media_links = []
        if self.contact_info is None:
            self.contact_info = {}
        if self.keywords is None:
            self.keywords = []
        if self.extracted_entities is None:
            self.extracted_entities = []
        if self.topic_categories is None:
            self.topic_categories = []

@dataclass
class SocialMediaContent:
    """Structure for social media content."""
    platform: str
    content_type: str
    text: Optional[str] = None
    author: Optional[str] = None
    author_url: Optional[str] = None
    author_id: Optional[str] = None
    author_verified: bool = False
    author_follower_count: Optional[int] = None
    post_url: Optional[str] = None
    post_id: Optional[str] = None
    timestamp: Optional[datetime] = None
    engagement: Dict[str, int] = None
    hashtags: List[str] = None
    mentions: List[str] = None
    media_urls: List[str] = None
    media_types: List[str] = None
    video_duration: Optional[int] = None
    view_count: Optional[int] = None
    comment_count: Optional[int] = None
    share_count: Optional[int] = None
    like_count: Optional[int] = None
    language: Optional[str] = None
    location: Optional[str] = None
    sponsored: bool = False
    content_warnings: List[str] = None
    reply_to: Optional[str] = None
    thread_id: Optional[str] = None
    
    def __post_init__(self):
        if self.engagement is None:
            self.engagement = {}
        if self.hashtags is None:
            self.hashtags = []
        if self.mentions is None:
            self.mentions = []
        if self.media_urls is None:
            self.media_urls = []
        if self.media_types is None:
            self.media_types = []
        if self.content_warnings is None:
            self.content_warnings = []

class ContentExtractor:
    """
    Professional content extraction system.
    
    Features:
    - Intelligent HTML parsing
    - Content cleaning and normalization
    - Metadata extraction
    - Social media content parsing
    - Multi-media content detection
    - Language detection
    - Keyword extraction
    - Contact information parsing
    - Structured data extraction
    - Anti-bot detection handling
    """
    
    def __init__(self):
        """Initialize content extractor."""
        self.social_media_patterns = self._load_social_media_patterns()
        self.contact_patterns = self._load_contact_patterns()
        self.content_selectors = self._load_content_selectors()
        
        # Initialize readability
        self.readability_doc = None
    
    def _load_social_media_patterns(self) -> Dict[str, Dict[str, str]]:
        """Load social media URL patterns."""
        return {
            'youtube': {
                'channel': r'youtube\.com/(?:c/|channel/|user/|@)([^/?]+)',
                'video': r'youtube\.com/watch\?v=([^&]+)',
                'playlist': r'youtube\.com/playlist\?list=([^&]+)'
            },
            'instagram': {
                'profile': r'instagram\.com/([^/?]+)',
                'post': r'instagram\.com/p/([^/?]+)',
                'reel': r'instagram\.com/reel/([^/?]+)'
            },
            'tiktok': {
                'profile': r'tiktok\.com/@([^/?]+)',
                'video': r'tiktok\.com/@[^/]+/video/(\d+)'
            },
            'twitter': {
                'profile': r'twitter\.com/([^/?]+)',
                'tweet': r'twitter\.com/[^/]+/status/(\d+)'
            },
            'facebook': {
                'page': r'facebook\.com/([^/?]+)',
                'post': r'facebook\.com/[^/]+/posts/(\d+)'
            },
            'spotify': {
                'artist': r'spotify\.com/artist/([^/?]+)',
                'track': r'spotify\.com/track/([^/?]+)',
                'album': r'spotify\.com/album/([^/?]+)',
                'playlist': r'spotify\.com/playlist/([^/?]+)'
            },
            'soundcloud': {
                'profile': r'soundcloud\.com/([^/?]+)',
                'track': r'soundcloud\.com/[^/]+/([^/?]+)'
            }
        }
    
    def _load_contact_patterns(self) -> Dict[str, str]:
        """Load contact information patterns."""
        return {
            'email': r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
            'phone': r'(\+?1?[-.\s]?)?\(?([0-9]{3})\)?[-.\s]?([0-9]{3})[-.\s]?([0-9]{4})',
            'phone_international': r'\+\d{1,3}[-.\s]?\d{1,14}',
            'website': r'https?://(?:[-\w.])+(?:\:[0-9]+)?(?:/(?:[\w/_.])*(?:\?(?:[\w&=%.])*)?(?:\#(?:[\w.])*)?)?',
            'address': r'\d+\s+[A-Za-z0-9\s,.-]+(?:Street|St|Avenue|Ave|Road|Rd|Boulevard|Blvd|Lane|Ln|Drive|Dr|Court|Ct|Place|Pl)'
        }
    
    def _load_content_selectors(self) -> Dict[str, List[str]]:
        """Load CSS selectors for content extraction."""
        return {
            'title': [
                'h1',
                '[data-testid="title"]',
                '.title',
                '.post-title',
                '.entry-title',
                '.article-title'
            ],
            'content': [
                'article',
                '.content',
                '.post-content',
                '.entry-content',
                '.article-content',
                '.main-content',
                'main',
                '#content'
            ],
            'description': [
                'meta[name="description"]',
                'meta[property="og:description"]',
                '.description',
                '.excerpt',
                '.summary'
            ],
            'author': [
                '[rel="author"]',
                '.author',
                '.byline',
                '.post-author',
                '.article-author',
                'meta[name="author"]'
            ],
            'date': [
                'time[datetime]',
                '.date',
                '.published',
                '.post-date',
                '.article-date',
                'meta[property="article:published_time"]'
            ]
        }
    
    async def extract_content(
        self,
        html: str,
        url: str,
        driver=None
    ) -> ExtractedContent:
        """
        Extract comprehensive content from HTML.
        
        Args:
            html: HTML content
            url: Source URL
            driver: Optional Selenium WebDriver for dynamic content
            
        Returns:
            ExtractedContent object
        """
        soup = BeautifulSoup(html, 'html.parser')
        
        # Remove unwanted elements
        self._clean_html(soup)
        
        # Extract basic content
        title = self._extract_title(soup)
        description = self._extract_description(soup)
        content = self._extract_main_content(soup)
        clean_text = self._extract_clean_text(soup)
        
        # Extract metadata
        metadata = self._extract_metadata(soup)
        
        # Extract media and links
        links = self._extract_links(soup, url)
        images = self._extract_images(soup, url)
        videos = self._extract_videos(soup, url)
        
        # Extract social media information
        social_media_links = self._extract_social_media_links(soup, url)
        
        # Extract contact information
        contact_info = self._extract_contact_info(clean_text)
        
        # Extract additional information
        language = self._detect_language(soup)
        keywords = self._extract_keywords(clean_text)
        author = self._extract_author(soup)
        publish_date = self._extract_publish_date(soup)
        
        # Calculate reading metrics
        word_count = len(clean_text.split()) if clean_text else 0
        reading_time_minutes = max(1, word_count // 200)  # Average reading speed
        
        # Calculate advanced metrics
        readability_score = self._calculate_readability(clean_text)
        sentiment_score = self._analyze_sentiment(clean_text)
        content_quality_score = self._assess_content_quality(clean_text, word_count)
        fingerprint_hash = self._generate_content_fingerprint(clean_text)
        extracted_entities = self._extract_entities(clean_text)
        topic_categories = self._classify_topics(clean_text)
        content_type = self._determine_content_type(soup, metadata)
        
        # Handle dynamic content if driver is provided
        if driver:
            dynamic_content = await self._extract_dynamic_content(driver)
            if dynamic_content:
                # Merge dynamic content
                content = content or dynamic_content.get('content', '')
                clean_text = clean_text or dynamic_content.get('text', '')
        
        return ExtractedContent(
            title=title,
            description=description,
            content=content,
            clean_text=clean_text,
            metadata=metadata,
            links=links,
            images=images,
            videos=videos,
            social_media_links=social_media_links,
            contact_info=contact_info,
            language=language,
            keywords=keywords,
            author=author,
            publish_date=publish_date,
            word_count=word_count,
            reading_time_minutes=reading_time_minutes,
            readability_score=readability_score,
            sentiment_score=sentiment_score,
            content_quality_score=content_quality_score,
            fingerprint_hash=fingerprint_hash,
            extracted_entities=extracted_entities,
            topic_categories=topic_categories,
            content_type=content_type
        )
    
    def _clean_html(self, soup: BeautifulSoup) -> None:
        """Remove unwanted HTML elements."""
        # Remove scripts, styles, and comments
        for element in soup(['script', 'style', 'nav', 'footer', 'header']):
            element.decompose()
        
        # Remove comments
        comments = soup.findAll(text=lambda text: isinstance(text, Comment))
        for comment in comments:
            comment.extract()
        
        # Remove ads and tracking elements
        ad_selectors = [
            '[class*="ad"]',
            '[id*="ad"]',
            '[class*="advertisement"]',
            '[class*="banner"]',
            '[class*="popup"]',
            '[class*="modal"]',
            '.google-ads',
            '.facebook-ads'
        ]
        
        for selector in ad_selectors:
            for element in soup.select(selector):
                element.decompose()
    
    def _extract_title(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract page title."""
        # Try multiple selectors
        for selector in self.content_selectors['title']:
            element = soup.select_one(selector)
            if element and element.get_text(strip=True):
                return element.get_text(strip=True)
        
        # Fallback to HTML title
        title_tag = soup.find('title')
        if title_tag:
            return title_tag.get_text(strip=True)
        
        return None
    
    def _extract_description(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract page description."""
        # Try meta descriptions first
        meta_desc = soup.find('meta', {'name': 'description'})
        if meta_desc and meta_desc.get('content'):
            return meta_desc['content'].strip()
        
        # Try Open Graph description
        og_desc = soup.find('meta', {'property': 'og:description'})
        if og_desc and og_desc.get('content'):
            return og_desc['content'].strip()
        
        # Try other selectors
        for selector in self.content_selectors['description'][2:]:
            element = soup.select_one(selector)
            if element and element.get_text(strip=True):
                return element.get_text(strip=True)
        
        return None
    
    def _extract_main_content(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract main content."""
        # Try content selectors
        for selector in self.content_selectors['content']:
            element = soup.select_one(selector)
            if element:
                return str(element)
        
        # Fallback to body
        body = soup.find('body')
        if body:
            return str(body)
        
        return str(soup)
    
    def _extract_clean_text(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract clean text content."""
        # Try to use readability for better content extraction
        try:
            if self.readability_doc:
                clean_html = self.readability_doc.summary()
                clean_soup = BeautifulSoup(clean_html, 'html.parser')
                return clean_soup.get_text(separator=' ', strip=True)
        except Exception as e:
            logger.debug(f"Readability extraction failed: {e}")
        
        # Fallback to manual extraction
        for selector in self.content_selectors['content']:
            element = soup.select_one(selector)
            if element:
                return element.get_text(separator=' ', strip=True)
        
        # Final fallback
        return soup.get_text(separator=' ', strip=True)
    
    def _extract_metadata(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """Extract page metadata."""
        metadata = {}
        
        # Extract all meta tags
        for meta in soup.find_all('meta'):
            if meta.get('name'):
                metadata[meta['name']] = meta.get('content', '')
            elif meta.get('property'):
                metadata[meta['property']] = meta.get('content', '')
        
        # Extract structured data (JSON-LD)
        json_ld_scripts = soup.find_all('script', {'type': 'application/ld+json'})
        structured_data = []
        
        for script in json_ld_scripts:
            try:
                data = json.loads(script.string)
                structured_data.append(data)
            except Exception as e:
                logger.debug(f"Failed to parse JSON-LD: {e}")
        
        if structured_data:
            metadata['structured_data'] = structured_data
        
        return metadata
    
    def _extract_links(self, soup: BeautifulSoup, base_url: str) -> List[Dict[str, str]]:
        """Extract all links."""
        links = []
        
        for link in soup.find_all('a', href=True):
            href = link['href']
            text = link.get_text(strip=True)
            
            # Convert relative URLs to absolute
            absolute_url = urljoin(base_url, href)
            
            links.append({
                'url': absolute_url,
                'text': text,
                'title': link.get('title', ''),
                'rel': link.get('rel', [])
            })
        
        return links
    
    def _extract_images(self, soup: BeautifulSoup, base_url: str) -> List[Dict[str, str]]:
        """Extract all images."""
        images = []
        
        for img in soup.find_all('img', src=True):
            src = img['src']
            
            # Convert relative URLs to absolute
            absolute_url = urljoin(base_url, src)
            
            images.append({
                'url': absolute_url,
                'alt': img.get('alt', ''),
                'title': img.get('title', ''),
                'width': img.get('width', ''),
                'height': img.get('height', '')
            })
        
        return images
    
    def _extract_videos(self, soup: BeautifulSoup, base_url: str) -> List[Dict[str, str]]:
        """Extract all videos."""
        videos = []
        
        # Extract video elements
        for video in soup.find_all('video'):
            src = video.get('src')
            if not src:
                source = video.find('source')
                if source:
                    src = source.get('src')
            
            if src:
                absolute_url = urljoin(base_url, src)
                videos.append({
                    'url': absolute_url,
                    'type': 'video',
                    'poster': video.get('poster', ''),
                    'duration': video.get('duration', ''),
                    'controls': video.get('controls', '') != None
                })
        
        # Extract embedded videos (iframe)
        for iframe in soup.find_all('iframe', src=True):
            src = iframe['src']
            if any(platform in src for platform in ['youtube', 'vimeo', 'dailymotion']):
                videos.append({
                    'url': src,
                    'type': 'embedded',
                    'width': iframe.get('width', ''),
                    'height': iframe.get('height', '')
                })
        
        return videos
    
    def _extract_social_media_links(self, soup: BeautifulSoup, base_url: str) -> List[Dict[str, str]]:
        """Extract social media links."""
        social_links = []
        
        for link in soup.find_all('a', href=True):
            href = link['href']
            
            for platform, patterns in self.social_media_patterns.items():
                for content_type, pattern in patterns.items():
                    match = re.search(pattern, href, re.IGNORECASE)
                    if match:
                        social_links.append({
                            'platform': platform,
                            'type': content_type,
                            'url': href,
                            'identifier': match.group(1) if match.groups() else '',
                            'text': link.get_text(strip=True)
                        })
                        break
        
        return social_links
    
    def _extract_contact_info(self, text: str) -> Dict[str, Any]:
        """Extract contact information."""
        if not text:
            return {}
        
        contact = {}
        
        # Extract emails
        emails = re.findall(self.contact_patterns['email'], text, re.IGNORECASE)
        if emails:
            contact['emails'] = list(set(emails))
        
        # Extract phone numbers
        phones = re.findall(self.contact_patterns['phone'], text)
        if phones:
            contact['phones'] = ['-'.join(phone[1:]) for phone in phones]
        
        # Extract international phone numbers
        intl_phones = re.findall(self.contact_patterns['phone_international'], text)
        if intl_phones:
            contact['international_phones'] = list(set(intl_phones))
        
        # Extract websites
        websites = re.findall(self.contact_patterns['website'], text, re.IGNORECASE)
        if websites:
            contact['websites'] = list(set(websites))
        
        # Extract addresses
        addresses = re.findall(self.contact_patterns['address'], text, re.IGNORECASE)
        if addresses:
            contact['addresses'] = list(set(addresses))
        
        return contact
    
    def _detect_language(self, soup: BeautifulSoup) -> Optional[str]:
        """Detect content language."""
        # Check HTML lang attribute
        html_tag = soup.find('html')
        if html_tag and html_tag.get('lang'):
            return html_tag['lang']
        
        # Check meta language
        lang_meta = soup.find('meta', {'name': 'language'})
        if lang_meta and lang_meta.get('content'):
            return lang_meta['content']
        
        # Check Open Graph locale
        og_locale = soup.find('meta', {'property': 'og:locale'})
        if og_locale and og_locale.get('content'):
            return og_locale['content']
        
        return None
    
    def _extract_keywords(self, text: str) -> List[str]:
        """Extract keywords from text."""
        if not text:
            return []
        
        # Simple keyword extraction (in production, use more sophisticated NLP)
        words = re.findall(r'\b[a-zA-Z]{3,}\b', text.lower())
        
        # Remove common stop words
        stop_words = {
            'the', 'and', 'for', 'are', 'but', 'not', 'you', 'all', 'can', 'had',
            'was', 'one', 'our', 'out', 'day', 'get', 'has', 'him', 'his', 'how',
            'its', 'may', 'new', 'now', 'old', 'see', 'two', 'who', 'boy', 'did',
            'man', 'way', 'what', 'with', 'from', 'have', 'they', 'this', 'that',
            'will', 'your', 'been', 'each', 'like', 'she', 'than', 'many', 'some',
            'time', 'very', 'when', 'much', 'would', 'there', 'make', 'could',
            'come', 'into', 'over', 'think', 'also', 'back', 'after', 'use',
            'her', 'can', 'only', 'work', 'life', 'which', 'their'
        }
        
        keywords = [word for word in words if word not in stop_words and len(word) > 3]
        
        # Count frequency and return top keywords
        word_freq = {}
        for word in keywords:
            word_freq[word] = word_freq.get(word, 0) + 1
        
        # Sort by frequency and return top 20
        sorted_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
        return [word for word, freq in sorted_words[:20]]
    
    def _extract_author(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract author information."""
        for selector in self.content_selectors['author']:
            element = soup.select_one(selector)
            if element:
                if element.name == 'meta':
                    return element.get('content', '').strip()
                else:
                    return element.get_text(strip=True)
        
        return None
    
    def _extract_publish_date(self, soup: BeautifulSoup) -> Optional[datetime]:
        """Extract publication date."""
        for selector in self.content_selectors['date']:
            element = soup.select_one(selector)
            if element:
                date_str = None
                
                if element.name == 'time' and element.get('datetime'):
                    date_str = element['datetime']
                elif element.name == 'meta':
                    date_str = element.get('content', '')
                else:
                    date_str = element.get_text(strip=True)
                
                if date_str:
                    try:
                        # Try different date formats
                        date_formats = [
                            '%Y-%m-%dT%H:%M:%S%z',
                            '%Y-%m-%d %H:%M:%S',
                            '%Y-%m-%d',
                            '%d/%m/%Y',
                            '%m/%d/%Y'
                        ]
                        
                        for fmt in date_formats:
                            try:
                                return datetime.strptime(date_str, fmt)
                            except ValueError:
                                continue
                                
                    except Exception as e:
                        logger.debug(f"Failed to parse date '{date_str}': {e}")
        
        return None
    
    async def _extract_dynamic_content(self, driver) -> Optional[Dict[str, str]]:
        """Extract content from dynamic pages using Selenium."""
        try:
            # Wait for content to load
            await asyncio.sleep(2)
            
            # Try to find main content
            content_selectors = [
                'main', 'article', '.content', '#content',
                '.post-content', '.entry-content'
            ]
            
            for selector in content_selectors:
                try:
                    element = WebDriverWait(driver, 5).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                    )
                    
                    if element:
                        return {
                            'content': element.get_attribute('innerHTML'),
                            'text': element.text
                        }
                except:
                    continue
            
            # Fallback to body
            body = driver.find_element(By.TAG_NAME, 'body')
            if body:
                return {
                    'content': body.get_attribute('innerHTML'),
                    'text': body.text
                }
                
        except Exception as e:
            logger.debug(f"Dynamic content extraction failed: {e}")
        
        return None
    
    async def extract_social_media_content(
        self,
        html: str,
        platform: str,
        url: str
    ) -> Optional[SocialMediaContent]:
        """Extract social media specific content."""
        soup = BeautifulSoup(html, 'html.parser')
        
        if platform.lower() == 'twitter':
            return self._extract_twitter_content(soup, url)
        elif platform.lower() == 'instagram':
            return self._extract_instagram_content(soup, url)
        elif platform.lower() == 'youtube':
            return self._extract_youtube_content(soup, url)
        elif platform.lower() == 'tiktok':
            return self._extract_tiktok_content(soup, url)
        elif platform.lower() == 'facebook':
            return self._extract_facebook_content(soup, url)
        else:
            return None
    
    def _extract_twitter_content(self, soup: BeautifulSoup, url: str) -> Optional[SocialMediaContent]:
        """Extract Twitter-specific content."""
        # Twitter content extraction logic
        text_element = soup.select_one('[data-testid="tweetText"]')
        text = text_element.get_text(strip=True) if text_element else None
        
        author_element = soup.select_one('[data-testid="User-Name"]')
        author = author_element.get_text(strip=True) if author_element else None
        
        # Extract hashtags and mentions
        hashtags = re.findall(r'#(\w+)', text) if text else []
        mentions = re.findall(r'@(\w+)', text) if text else []
        
        return SocialMediaContent(
            platform='twitter',
            content_type='tweet',
            text=text,
            author=author,
            post_url=url,
            hashtags=hashtags,
            mentions=mentions
        )
    
    def _extract_instagram_content(self, soup: BeautifulSoup, url: str) -> Optional[SocialMediaContent]:
        """Extract Instagram-specific content."""
        # Instagram content extraction logic
        return SocialMediaContent(
            platform='instagram',
            content_type='post',
            post_url=url
        )
    
    def _extract_youtube_content(self, soup: BeautifulSoup, url: str) -> Optional[SocialMediaContent]:
        """Extract YouTube-specific content."""
        # YouTube content extraction logic
        return SocialMediaContent(
            platform='youtube',
            content_type='video',
            post_url=url
        )
    
    def _extract_tiktok_content(self, soup: BeautifulSoup, url: str) -> Optional[SocialMediaContent]:
        """Extract TikTok-specific content."""
        # TikTok content extraction logic
        return SocialMediaContent(
            platform='tiktok',
            content_type='video',
            post_url=url
        )
    
    def _extract_facebook_content(self, soup: BeautifulSoup, url: str) -> Optional[SocialMediaContent]:
        """Extract Facebook-specific content."""
        # Facebook content extraction logic
        return SocialMediaContent(
            platform='facebook',
            content_type='post',
            post_url=url
        )
    
    def _calculate_readability(self, text: str) -> float:
        """Calculate readability score using multiple metrics."""
        if not text or len(text) < 50:
            return 0.0
        
        try:
            # Use Flesch Reading Ease as primary metric
            flesch_score = flesch_reading_ease(text)
            
            # Normalize to 0-1 scale (100 = very easy, 0 = very difficult)
            normalized_score = max(0.0, min(1.0, flesch_score / 100.0))
            
            return normalized_score
            
        except Exception as e:
            logger.debug(f"Readability calculation failed: {e}")
            return 0.5  # Default neutral score
    
    def _analyze_sentiment(self, text: str) -> float:
        """Analyze sentiment of text content."""
        if not text or len(text) < 10:
            return 0.0
        
        try:
            # Simple sentiment analysis using keyword counts
            positive_words = {
                'good', 'great', 'excellent', 'amazing', 'wonderful', 'fantastic',
                'awesome', 'brilliant', 'outstanding', 'perfect', 'love', 'like',
                'enjoy', 'happy', 'pleased', 'satisfied', 'positive', 'successful',
                'best', 'beautiful', 'incredible', 'spectacular', 'remarkable'
            }
            
            negative_words = {
                'bad', 'terrible', 'awful', 'horrible', 'disgusting', 'hate',
                'dislike', 'angry', 'sad', 'disappointed', 'frustrated', 'annoying',
                'worst', 'ugly', 'stupid', 'ridiculous', 'pathetic', 'useless',
                'broken', 'failed', 'wrong', 'error', 'problem', 'issue'
            }
            
            words = text.lower().split()
            positive_count = sum(1 for word in words if word in positive_words)
            negative_count = sum(1 for word in words if word in negative_words)
            
            total_sentiment_words = positive_count + negative_count
            
            if total_sentiment_words == 0:
                return 0.0  # Neutral
            
            # Calculate sentiment score (-1 to 1)
            sentiment = (positive_count - negative_count) / total_sentiment_words
            
            return sentiment
            
        except Exception as e:
            logger.debug(f"Sentiment analysis failed: {e}")
            return 0.0
    
    def _assess_content_quality(self, text: str, word_count: int) -> float:
        """Assess overall content quality."""
        if not text or word_count < 10:
            return 0.0
        
        quality_score = 0.0
        
        try:
            # Factor 1: Word count (0.3 weight)
            if word_count >= 300:
                word_score = min(1.0, word_count / 1000.0)
            else:
                word_score = word_count / 300.0
            
            quality_score += word_score * 0.3
            
            # Factor 2: Sentence structure (0.2 weight)
            sentences = text.split('.')
            avg_sentence_length = sum(len(s.split()) for s in sentences) / len(sentences)
            
            # Optimal sentence length is 15-20 words
            if 10 <= avg_sentence_length <= 25:
                sentence_score = 1.0
            else:
                sentence_score = max(0.0, 1.0 - abs(avg_sentence_length - 17.5) / 17.5)
            
            quality_score += sentence_score * 0.2
            
            # Factor 3: Vocabulary diversity (0.2 weight)
            words = text.lower().split()
            unique_words = set(words)
            vocabulary_diversity = len(unique_words) / len(words) if words else 0
            
            quality_score += vocabulary_diversity * 0.2
            
            # Factor 4: Structure indicators (0.3 weight)
            structure_score = 0.0
            
            # Check for headers, lists, etc.
            if any(indicator in text for indicator in [':', '•', '-', '1.', '2.']):
                structure_score += 0.5
            
            # Check for proper capitalization
            sentences_with_caps = sum(1 for s in sentences if s.strip() and s.strip()[0].isupper())
            cap_ratio = sentences_with_caps / len(sentences) if sentences else 0
            structure_score += cap_ratio * 0.5
            
            quality_score += structure_score * 0.3
            
            return min(1.0, quality_score)
            
        except Exception as e:
            logger.debug(f"Content quality assessment failed: {e}")
            return 0.5
    
    def _generate_content_fingerprint(self, text: str) -> Optional[str]:
        """Generate content fingerprint for duplicate detection."""
        if not text or len(text) < 50:
            return None
        
        try:
            # Normalize text for fingerprinting
            normalized = re.sub(r'\s+', ' ', text.lower().strip())
            normalized = re.sub(r'[^\w\s]', '', normalized)
            
            # Create hash
            return hashlib.sha256(normalized.encode('utf-8')).hexdigest()
            
        except Exception as e:
            logger.debug(f"Content fingerprinting failed: {e}")
            return None
    
    def _extract_entities(self, text: str) -> List[Dict[str, str]]:
        """Extract named entities from text."""
        entities = []
        
        if not text or len(text) < 20:
            return entities
        
        try:
            # Simple entity extraction using patterns
            # In production, use spaCy or NLTK for better NER
            
            # Extract potential person names (capitalized words)
            person_pattern = r'\b[A-Z][a-z]+ [A-Z][a-z]+\b'
            persons = re.findall(person_pattern, text)
            
            for person in persons:
                entities.append({
                    'text': person,
                    'type': 'PERSON',
                    'confidence': 0.7
                })
            
            # Extract potential organizations
            org_indicators = ['Inc', 'LLC', 'Ltd', 'Corp', 'Company', 'Foundation']
            org_pattern = r'\b[A-Z][a-zA-Z\s]+(?:' + '|'.join(org_indicators) + r')\b'
            orgs = re.findall(org_pattern, text)
            
            for org in orgs:
                entities.append({
                    'text': org.strip(),
                    'type': 'ORGANIZATION',
                    'confidence': 0.6
                })
            
            # Extract potential locations (cities, countries)
            # This is a simplified version - use proper geographic databases in production
            location_pattern = r'\b[A-Z][a-z]+(?:\s[A-Z][a-z]+)*,\s[A-Z]{2,}\b'
            locations = re.findall(location_pattern, text)
            
            for location in locations:
                entities.append({
                    'text': location,
                    'type': 'LOCATION',
                    'confidence': 0.5
                })
            
            return entities[:10]  # Limit to top 10 entities
            
        except Exception as e:
            logger.debug(f"Entity extraction failed: {e}")
            return entities
    
    def _classify_topics(self, text: str) -> List[str]:
        """Classify content into topic categories."""
        if not text or len(text) < 100:
            return []
        
        try:
            text_lower = text.lower()
            
            # Define topic keywords
            topic_keywords = {
                'technology': [
                    'software', 'programming', 'coding', 'developer', 'app', 'website',
                    'computer', 'digital', 'tech', 'artificial intelligence', 'ai',
                    'machine learning', 'blockchain', 'cryptocurrency', 'cloud'
                ],
                'business': [
                    'business', 'company', 'corporate', 'enterprise', 'startup',
                    'entrepreneur', 'marketing', 'sales', 'revenue', 'profit',
                    'investment', 'finance', 'economy', 'market', 'strategy'
                ],
                'health': [
                    'health', 'medical', 'doctor', 'hospital', 'medicine', 'treatment',
                    'wellness', 'fitness', 'nutrition', 'diet', 'exercise', 'healthcare'
                ],
                'education': [
                    'education', 'school', 'university', 'learning', 'student',
                    'teacher', 'course', 'training', 'knowledge', 'study', 'academic'
                ],
                'entertainment': [
                    'entertainment', 'movie', 'film', 'music', 'game', 'gaming',
                    'tv', 'show', 'celebrity', 'actor', 'singer', 'artist', 'fun'
                ],
                'sports': [
                    'sports', 'football', 'basketball', 'soccer', 'baseball',
                    'tennis', 'golf', 'athlete', 'team', 'game', 'match', 'championship'
                ],
                'travel': [
                    'travel', 'trip', 'vacation', 'tourism', 'hotel', 'flight',
                    'destination', 'journey', 'adventure', 'explore', 'visit'
                ],
                'food': [
                    'food', 'restaurant', 'recipe', 'cooking', 'chef', 'cuisine',
                    'meal', 'dish', 'ingredient', 'taste', 'flavor', 'dining'
                ],
                'fashion': [
                    'fashion', 'style', 'clothing', 'dress', 'designer', 'trend',
                    'outfit', 'brand', 'model', 'beauty', 'cosmetics', 'makeup'
                ],
                'science': [
                    'science', 'research', 'study', 'experiment', 'discovery',
                    'physics', 'chemistry', 'biology', 'mathematics', 'data'
                ]
            }
            
            detected_topics = []
            
            for topic, keywords in topic_keywords.items():
                keyword_count = sum(1 for keyword in keywords if keyword in text_lower)
                
                # Calculate topic relevance
                relevance = keyword_count / len(keywords)
                
                if relevance > 0.1:  # At least 10% of keywords present
                    detected_topics.append(topic)
            
            return detected_topics[:5]  # Return top 5 topics
            
        except Exception as e:
            logger.debug(f"Topic classification failed: {e}")
            return []
    
    def _determine_content_type(self, soup: BeautifulSoup, metadata: Dict) -> str:
        """Determine the type of content."""
        try:
            # Check Open Graph type
            og_type = metadata.get('og:type', '').lower()
            if og_type:
                return og_type
            
            # Check structured data
            structured_data = metadata.get('structured_data', [])
            for data in structured_data:
                if isinstance(data, dict) and '@type' in data:
                    return data['@type'].lower()
            
            # Check HTML structure
            if soup.find('article'):
                return 'article'
            elif soup.find('video') or soup.find('iframe', src=lambda x: x and 'youtube' in x):
                return 'video'
            elif soup.find('audio'):
                return 'audio'
            elif soup.select('.product, [itemtype*="Product"]'):
                return 'product'
            elif soup.select('.recipe, [itemtype*="Recipe"]'):
                return 'recipe'
            elif soup.select('.event, [itemtype*="Event"]'):
                return 'event'
            else:
                return 'webpage'
                
        except Exception as e:
            logger.debug(f"Content type determination failed: {e}")
            return 'webpage'
    
    async def extract_multimedia_content(self, soup: BeautifulSoup, base_url: str) -> Dict[str, List]:
        """Extract and analyze multimedia content."""
        multimedia = {
            'images': [],
            'videos': [],
            'audio': [],
            'documents': []
        }
        
        try:
            # Enhanced image extraction
            for img in soup.find_all(['img', 'picture', 'source']):
                src = img.get('src') or img.get('srcset') or img.get('data-src')
                if src:
                    # Handle srcset
                    if 'srcset' in src:
                        src = src.split(',')[0].split()[0]
                    
                    absolute_url = urljoin(base_url, src)
                    
                    image_info = {
                        'url': absolute_url,
                        'alt': img.get('alt', ''),
                        'title': img.get('title', ''),
                        'width': img.get('width', ''),
                        'height': img.get('height', ''),
                        'loading': img.get('loading', ''),
                        'format': self._get_image_format(absolute_url),
                        'is_responsive': bool(img.get('srcset')),
                        'size_category': self._categorize_image_size(img)
                    }
                    
                    multimedia['images'].append(image_info)
            
            # Enhanced video extraction
            for video in soup.find_all(['video', 'iframe']):
                if video.name == 'video':
                    src = video.get('src')
                    if not src:
                        source = video.find('source')
                        if source:
                            src = source.get('src')
                    
                    if src:
                        absolute_url = urljoin(base_url, src)
                        video_info = {
                            'url': absolute_url,
                            'type': 'native_video',
                            'poster': video.get('poster', ''),
                            'duration': video.get('duration', ''),
                            'controls': video.get('controls') is not None,
                            'autoplay': video.get('autoplay') is not None,
                            'muted': video.get('muted') is not None,
                            'width': video.get('width', ''),
                            'height': video.get('height', '')
                        }
                        multimedia['videos'].append(video_info)
                
                elif video.name == 'iframe':
                    src = video.get('src', '')
                    if any(platform in src.lower() for platform in ['youtube', 'vimeo', 'dailymotion', 'twitch']):
                        platform = self._identify_video_platform(src)
                        video_info = {
                            'url': src,
                            'type': 'embedded_video',
                            'platform': platform,
                            'width': video.get('width', ''),
                            'height': video.get('height', ''),
                            'frameborder': video.get('frameborder', ''),
                            'allowfullscreen': video.get('allowfullscreen') is not None
                        }
                        multimedia['videos'].append(video_info)
            
            # Audio extraction
            for audio in soup.find_all('audio'):
                src = audio.get('src')
                if not src:
                    source = audio.find('source')
                    if source:
                        src = source.get('src')
                
                if src:
                    absolute_url = urljoin(base_url, src)
                    audio_info = {
                        'url': absolute_url,
                        'controls': audio.get('controls') is not None,
                        'autoplay': audio.get('autoplay') is not None,
                        'loop': audio.get('loop') is not None,
                        'muted': audio.get('muted') is not None,
                        'preload': audio.get('preload', ''),
                        'format': self._get_audio_format(absolute_url)
                    }
                    multimedia['audio'].append(audio_info)
            
            # Document links extraction
            document_extensions = ['.pdf', '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx', '.txt']
            for link in soup.find_all('a', href=True):
                href = link['href']
                if any(ext in href.lower() for ext in document_extensions):
                    absolute_url = urljoin(base_url, href)
                    doc_info = {
                        'url': absolute_url,
                        'text': link.get_text(strip=True),
                        'title': link.get('title', ''),
                        'format': self._get_document_format(absolute_url),
                        'download': link.get('download') is not None
                    }
                    multimedia['documents'].append(doc_info)
            
        except Exception as e:
            logger.error(f"Multimedia content extraction failed: {e}")
        
        return multimedia
    
    def _get_image_format(self, url: str) -> str:
        """Determine image format from URL."""
        url_lower = url.lower()
        if '.jpg' in url_lower or '.jpeg' in url_lower:
            return 'jpeg'
        elif '.png' in url_lower:
            return 'png'
        elif '.gif' in url_lower:
            return 'gif'
        elif '.webp' in url_lower:
            return 'webp'
        elif '.svg' in url_lower:
            return 'svg'
        else:
            return 'unknown'
    
    def _categorize_image_size(self, img) -> str:
        """Categorize image size."""
        try:
            width = int(img.get('width', 0))
            height = int(img.get('height', 0))
            
            if width == 0 or height == 0:
                return 'unknown'
            
            area = width * height
            
            if area < 10000:  # < 100x100
                return 'thumbnail'
            elif area < 250000:  # < 500x500
                return 'small'
            elif area < 1000000:  # < 1000x1000
                return 'medium'
            else:
                return 'large'
                
        except (ValueError, TypeError):
            return 'unknown'
    
    def _identify_video_platform(self, url: str) -> str:
        """Identify video platform from URL."""
        url_lower = url.lower()
        if 'youtube' in url_lower:
            return 'youtube'
        elif 'vimeo' in url_lower:
            return 'vimeo'
        elif 'dailymotion' in url_lower:
            return 'dailymotion'
        elif 'twitch' in url_lower:
            return 'twitch'
        elif 'tiktok' in url_lower:
            return 'tiktok'
        else:
            return 'unknown'
    
    def _get_audio_format(self, url: str) -> str:
        """Determine audio format from URL."""
        url_lower = url.lower()
        if '.mp3' in url_lower:
            return 'mp3'
        elif '.wav' in url_lower:
            return 'wav'
        elif '.ogg' in url_lower:
            return 'ogg'
        elif '.m4a' in url_lower:
            return 'm4a'
        elif '.flac' in url_lower:
            return 'flac'
        else:
            return 'unknown'
    
    def _get_document_format(self, url: str) -> str:
        """Determine document format from URL."""
        url_lower = url.lower()
        if '.pdf' in url_lower:
            return 'pdf'
        elif '.doc' in url_lower:
            return 'doc'
        elif '.docx' in url_lower:
            return 'docx'
        elif '.xls' in url_lower:
            return 'xls'
        elif '.xlsx' in url_lower:
            return 'xlsx'
        elif '.ppt' in url_lower:
            return 'ppt'
        elif '.pptx' in url_lower:
            return 'pptx'
        elif '.txt' in url_lower:
            return 'txt'
        else:
            return 'unknown'
    
    async def extract_schema_markup(self, soup: BeautifulSoup) -> List[Dict]:
        """Extract structured data markup."""
        structured_data = []
        
        try:
            # JSON-LD
            json_ld_scripts = soup.find_all('script', {'type': 'application/ld+json'})
            for script in json_ld_scripts:
                try:
                    data = json.loads(script.string)
                    structured_data.append({
                        'format': 'json-ld',
                        'data': data
                    })
                except json.JSONDecodeError as e:
                    logger.debug(f"Failed to parse JSON-LD: {e}")
            
            # Microdata
            microdata_elements = soup.find_all(attrs={'itemscope': True})
            for element in microdata_elements:
                try:
                    microdata = self._extract_microdata(element)
                    if microdata:
                        structured_data.append({
                            'format': 'microdata',
                            'data': microdata
                        })
                except Exception as e:
                    logger.debug(f"Failed to extract microdata: {e}")
            
            # RDFa (basic extraction)
            rdfa_elements = soup.find_all(attrs={'typeof': True})
            for element in rdfa_elements:
                try:
                    rdfa = self._extract_rdfa(element)
                    if rdfa:
                        structured_data.append({
                            'format': 'rdfa',
                            'data': rdfa
                        })
                except Exception as e:
                    logger.debug(f"Failed to extract RDFa: {e}")
            
        except Exception as e:
            logger.error(f"Schema markup extraction failed: {e}")
        
        return structured_data
    
    def _extract_microdata(self, element) -> Dict:
        """Extract microdata from element."""
        data = {}
        
        # Get item type
        itemtype = element.get('itemtype')
        if itemtype:
            data['@type'] = itemtype
        
        # Extract properties
        for prop_element in element.find_all(attrs={'itemprop': True}):
            prop_name = prop_element.get('itemprop')
            
            # Get property value
            if prop_element.name in ['meta', 'link']:
                prop_value = prop_element.get('content') or prop_element.get('href')
            elif prop_element.get('datetime'):
                prop_value = prop_element.get('datetime')
            else:
                prop_value = prop_element.get_text(strip=True)
            
            if prop_name and prop_value:
                if prop_name in data:
                    # Handle multiple values
                    if not isinstance(data[prop_name], list):
                        data[prop_name] = [data[prop_name]]
                    data[prop_name].append(prop_value)
                else:
                    data[prop_name] = prop_value
        
        return data
    
    def _extract_rdfa(self, element) -> Dict:
        """Extract RDFa from element."""
        data = {}
        
        # Get type
        typeof = element.get('typeof')
        if typeof:
            data['@type'] = typeof
        
        # Extract properties
        for prop_element in element.find_all(attrs={'property': True}):
            prop_name = prop_element.get('property')
            
            # Get property value
            content = prop_element.get('content')
            if content:
                prop_value = content
            else:
                prop_value = prop_element.get_text(strip=True)
            
            if prop_name and prop_value:
                data[prop_name] = prop_value
        
        return data

# Utility functions for content extraction
async def extract_content_from_url(url: str, timeout: int = 30) -> Optional[ExtractedContent]:
    """Extract content directly from URL."""
    try:
        async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=timeout)) as session:
            async with session.get(url) as response:
                if response.status == 200:
                    html = await response.text()
                    extractor = ContentExtractor()
                    return await extractor.extract_content(html, url)
    except Exception as e:
        logger.error(f"Failed to extract content from {url}: {e}")
    
    return None

def clean_extracted_text(text: str) -> str:
    """Clean and normalize extracted text."""
    if not text:
        return ""
    
    # Remove excessive whitespace
    text = re.sub(r'\s+', ' ', text)
    
    # Remove HTML entities
    text = html.unescape(text)
    
    # Remove control characters
    text = ''.join(char for char in text if ord(char) >= 32 or char in '\n\t')
    
    # Normalize line breaks
    text = re.sub(r'\n\s*\n', '\n\n', text)
    
    return text.strip()

def extract_domain_info(url: str) -> Dict[str, str]:
    """Extract domain information from URL."""
    try:
        parsed = urlparse(url)
        return {
            'domain': parsed.netloc,
            'subdomain': parsed.netloc.split('.')[0] if '.' in parsed.netloc else '',
            'root_domain': '.'.join(parsed.netloc.split('.')[-2:]) if '.' in parsed.netloc else parsed.netloc,
            'tld': parsed.netloc.split('.')[-1] if '.' in parsed.netloc else '',
            'scheme': parsed.scheme,
            'path': parsed.path
        }
    except Exception:
        return {}
