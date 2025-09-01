"""Crawling Agent Utilities - Advanced Helper Functions & Tools

Comprehensive utility collection for URL processing, content analysis,
performance optimization, and common crawling operations.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️  IMPORTANT LEGAL NOTICE:
This code and concept are the exclusive intellectual property of Fahed Mlaiel.
Any unauthorized use, copying, distribution, or commercialization without explicit written permission is strictly prohibited.
Contact: mlaiel@live.de for licensing inquiries.

Team Specialties:
- Lead AI Developer & Backend Senior Engineer
- Machine Learning Engineer & Audio Processing Specialist  
- Database Administrator & Security Expert
- Microservices Architect & DevOps Engineer
- AI Prompt Engineer & Content Protection Specialist
"""
import asyncio
import logging
import hashlib
import time
import random
import re
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Set, Tuple, Union, Generator
from urllib.parse import urlparse, urljoin, parse_qs, urlencode, urlunparse
from urllib.robotparser import RobotFileParser
import json
import base64
from collections import defaultdict, deque
import string

import aiofiles
import yaml
from bs4 import BeautifulSoup, Comment
import tldextract
from langdetect import detect, LangDetectError
import requests
from user_agents import parse as parse_user_agent
import magic
from PIL import Image, ImageEnhance, ImageFilter
import cv2
import numpy as np

logger = logging.getLogger(__name__)


class URLProcessor:
    """
    Advanced URL processing and normalization utilities
    """
    
    @staticmethod
    def normalize_url(url: str) -> str:
        """
        Normalize URL by removing unnecessary parameters and fragments
        """
        try:
            parsed = urlparse(url.strip())
            
            # Remove fragment
            parsed = parsed._replace(fragment='')
            
            # Remove common tracking parameters
            tracking_params = {
                'utm_source', 'utm_medium', 'utm_campaign', 'utm_term', 'utm_content',
                'fbclid', 'gclid', 'ref', 'referrer', '_ga', 'campaign_id'
            }
            
            if parsed.query:
                query_params = parse_qs(parsed.query)
                filtered_params = {
                    k: v for k, v in query_params.items() 
                    if k.lower() not in tracking_params
                }
                new_query = urlencode(filtered_params, doseq=True)
                parsed = parsed._replace(query=new_query)
            
            # Ensure lowercase domain
            parsed = parsed._replace(netloc=parsed.netloc.lower())
            
            # Remove trailing slash for paths
            if parsed.path.endswith('/') and len(parsed.path) > 1:
                parsed = parsed._replace(path=parsed.path.rstrip('/'))
            
            return urlunparse(parsed)
            
        except Exception as e:
            logger.warning(f"URL normalization failed for {url}: {str(e)}")
            return url
    
    @staticmethod
    def extract_domain_info(url: str) -> Dict[str, str]:
        """
        Extract comprehensive domain information
        """
        try:
            parsed = urlparse(url)
            extracted = tldextract.extract(url)
            
            return {
                'full_url': url,
                'scheme': parsed.scheme,
                'domain': extracted.domain,
                'subdomain': extracted.subdomain,
                'suffix': extracted.suffix,
                'registered_domain': extracted.registered_domain,
                'fqdn': extracted.fqdn,
                'port': parsed.port,
                'path': parsed.path,
                'is_ip': URLProcessor._is_ip_address(parsed.netloc)
            }
        except Exception as e:
            logger.error(f"Domain extraction failed for {url}: {str(e)}")
            return {'error': str(e)}
    
    @staticmethod
    def _is_ip_address(address: str) -> bool:
        """Check if address is IP address"""
        import ipaddress
        try:
            ipaddress.ip_address(address.split(':')[0])
            return True
        except ValueError:
            return False
    
    @staticmethod
    def is_valid_url(url: str) -> bool:
        """
        Validate URL format and structure
        """
        try:
            parsed = urlparse(url)
            return all([
                parsed.scheme in ['http', 'https'],
                parsed.netloc,
                len(parsed.netloc) > 0
            ])
        except Exception:
            return False
    
    @staticmethod
    def generate_url_variations(url: str) -> List[str]:
        """
        Generate common URL variations for comprehensive crawling
        """
        variations = [url]
        parsed = urlparse(url)
        
        # Protocol variations
        if parsed.scheme == 'http':
            variations.append(url.replace('http://', 'https://'))
        elif parsed.scheme == 'https':
            variations.append(url.replace('https://', 'http://'))
        
        # www variations
        if parsed.netloc.startswith('www.'):
            no_www_url = url.replace('www.', '')
            variations.append(no_www_url)
        else:
            www_url = url.replace(f'{parsed.scheme}://', f'{parsed.scheme}://www.')
            variations.append(www_url)
        
        # Trailing slash variations
        if url.endswith('/'):
            variations.append(url.rstrip('/'))
        else:
            variations.append(url + '/')
        
        return list(set(variations))  # Remove duplicates


class ContentAnalyzer:
    """
    Advanced content analysis utilities
    """
    
    @staticmethod
    def extract_text_statistics(text: str) -> Dict[str, Any]:
        """
        Extract comprehensive text statistics
        """
        if not text:
            return {}
        
        words = text.split()
        sentences = re.split(r'[.!?]+', text)
        paragraphs = text.split('\n\n')
        
        return {
            'character_count': len(text),
            'character_count_no_spaces': len(text.replace(' ', '')),
            'word_count': len(words),
            'sentence_count': len([s for s in sentences if s.strip()]),
            'paragraph_count': len([p for p in paragraphs if p.strip()]),
            'average_word_length': sum(len(word) for word in words) / len(words) if words else 0,
            'average_sentence_length': len(words) / len(sentences) if sentences else 0,
            'reading_time_minutes': len(words) / 200,  # Assume 200 WPM reading speed
            'has_uppercase': any(c.isupper() for c in text),
            'has_lowercase': any(c.islower() for c in text),
            'has_numbers': any(c.isdigit() for c in text),
            'has_special_chars': any(not c.isalnum() and not c.isspace() for c in text)
        }
    
    @staticmethod
    def detect_content_language(text: str) -> Dict[str, Any]:
        """
        Detect content language with confidence score
        """
        try:
            if not text.strip():
                return {'language': 'unknown', 'confidence': 0.0}
            
            # Use langdetect for primary detection
            detected_lang = detect(text)
            
            # Calculate confidence based on text length and characteristics
            confidence = min(len(text) / 1000.0, 1.0)  # More text = higher confidence
            
            return {
                'language': detected_lang,
                'confidence': confidence,
                'text_length': len(text),
                'detection_method': 'langdetect'
            }
        except LangDetectError:
            return {
                'language': 'unknown',
                'confidence': 0.0,
                'error': 'Language detection failed'
            }
    
    @staticmethod
    def extract_keywords(text: str, top_n: int = 20) -> List[Dict[str, Any]]:
        """
        Extract keywords from text using multiple methods
        """
        if not text:
            return []
        
        # Simple frequency-based extraction
        words = re.findall(r'\b[a-zA-Z]{3,}\b', text.lower())
        word_freq = defaultdict(int)
        
        # Filter out common stop words
        stop_words = {
            'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of',
            'with', 'by', 'from', 'up', 'about', 'into', 'through', 'during',
            'before', 'after', 'above', 'below', 'between', 'among', 'since',
            'this', 'that', 'these', 'those', 'i', 'me', 'my', 'myself',
            'we', 'our', 'ours', 'ourselves', 'you', 'your', 'yours'
        }
        
        for word in words:
            if word not in stop_words and len(word) > 3:
                word_freq[word] += 1
        
        # Sort by frequency and return top N
        sorted_keywords = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
        
        return [
            {
                'keyword': word,
                'frequency': count,
                'relevance_score': count / len(words) if words else 0
            }
            for word, count in sorted_keywords[:top_n]
        ]
    
    @staticmethod
    def extract_entities(text: str) -> Dict[str, List[str]]:
        """
        Extract named entities from text (simple regex-based approach)
        """
        entities = {
            'emails': [],
            'urls': [],
            'phone_numbers': [],
            'hashtags': [],
            'mentions': [],
            'monetary_amounts': [],
            'dates': []
        }
        
        # Email pattern
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        entities['emails'] = re.findall(email_pattern, text)
        
        # URL pattern
        url_pattern = r'https?://(?:[-\w.])+(?:[:\d]+)?(?:/(?:[\w/_.])*(?:\?(?:[\w&=%.])*)?(?:#(?:[\w.])*)?)?'
        entities['urls'] = re.findall(url_pattern, text)
        
        # Phone pattern (simple)
        phone_pattern = r'[\+]?[1-9]?[0-9]{7,12}'
        entities['phone_numbers'] = re.findall(phone_pattern, text)
        
        # Hashtag pattern
        hashtag_pattern = r'#\w+'
        entities['hashtags'] = re.findall(hashtag_pattern, text)
        
        # Mention pattern
        mention_pattern = r'@\w+'
        entities['mentions'] = re.findall(mention_pattern, text)
        
        # Monetary amounts
        money_pattern = r'\$[\d,]+\.?\d*'
        entities['monetary_amounts'] = re.findall(money_pattern, text)
        
        return entities
    
    @staticmethod
    def calculate_readability_score(text: str) -> Dict[str, float]:
        """
        Calculate multiple readability scores
        """
        if not text:
            return {}
        
        words = text.split()
        sentences = re.split(r'[.!?]+', text)
        sentences = [s for s in sentences if s.strip()]
        
        if not words or not sentences:
            return {}
        
        avg_sentence_length = len(words) / len(sentences)
        
        # Count syllables (approximation)
        def count_syllables(word):
            vowels = 'aeiouy'
            count = sum(1 for char in word.lower() if char in vowels)
            if word.endswith('e'):
                count -= 1
            return max(count, 1)
        
        total_syllables = sum(count_syllables(word) for word in words)
        avg_syllables_per_word = total_syllables / len(words)
        
        # Flesch Reading Ease Score
        flesch_score = 206.835 - (1.015 * avg_sentence_length) - (84.6 * avg_syllables_per_word)
        
        # Flesch-Kincaid Grade Level
        fk_grade = (0.39 * avg_sentence_length) + (11.8 * avg_syllables_per_word) - 15.59
        
        return {
            'flesch_reading_ease': max(0, min(100, flesch_score)),
            'flesch_kincaid_grade': max(0, fk_grade),
            'average_sentence_length': avg_sentence_length,
            'average_syllables_per_word': avg_syllables_per_word,
            'total_words': len(words),
            'total_sentences': len(sentences)
        }


class HTMLProcessor:
    """
    Advanced HTML processing utilities
    """
    
    @staticmethod
    def extract_clean_text(html: str) -> str:
        """
        Extract clean text from HTML content
        """
        try:
            soup = BeautifulSoup(html, 'html.parser')
            
            # Remove script and style elements
            for element in soup(['script', 'style', 'meta', 'link']):
                element.decompose()
            
            # Remove comments
            for comment in soup.find_all(string=lambda text: isinstance(text, Comment)):
                comment.extract()
            
            # Get text and normalize whitespace
            text = soup.get_text(separator=' ', strip=True)
            text = re.sub(r'\s+', ' ', text)
            
            return text.strip()
            
        except Exception as e:
            logger.error(f"HTML text extraction failed: {str(e)}")
            return ""
    
    @staticmethod
    def extract_metadata(html: str) -> Dict[str, Any]:
        """
        Extract comprehensive metadata from HTML
        """
        try:
            soup = BeautifulSoup(html, 'html.parser')
            metadata = {}
            
            # Title
            title_tag = soup.find('title')
            if title_tag:
                metadata['title'] = title_tag.get_text().strip()
            
            # Meta tags
            meta_tags = {}
            for meta in soup.find_all('meta'):
                name = meta.get('name') or meta.get('property') or meta.get('http-equiv')
                content = meta.get('content')
                if name and content:
                    meta_tags[name.lower()] = content
            
            metadata['meta_tags'] = meta_tags
            
            # Open Graph tags
            og_tags = {}
            for meta in soup.find_all('meta', property=lambda x: x and x.startswith('og:')):
                property_name = meta.get('property')[3:]  # Remove 'og:' prefix
                og_tags[property_name] = meta.get('content')
            
            if og_tags:
                metadata['open_graph'] = og_tags
            
            # Twitter Card tags
            twitter_tags = {}
            for meta in soup.find_all('meta', attrs={'name': lambda x: x and x.startswith('twitter:')}):
                name = meta.get('name')[8:]  # Remove 'twitter:' prefix
                twitter_tags[name] = meta.get('content')
            
            if twitter_tags:
                metadata['twitter_card'] = twitter_tags
            
            # JSON-LD structured data
            json_ld_scripts = soup.find_all('script', type='application/ld+json')
            structured_data = []
            for script in json_ld_scripts:
                try:
                    data = json.loads(script.string)
                    structured_data.append(data)
                except json.JSONDecodeError:
                    continue
            
            if structured_data:
                metadata['structured_data'] = structured_data
            
            # Links
            links = {
                'canonical': None,
                'alternate': [],
                'stylesheet': [],
                'icon': [],
                'next': None,
                'prev': None
            }
            
            for link in soup.find_all('link'):
                rel = link.get('rel')
                href = link.get('href')
                
                if rel and href:
                    rel_str = ' '.join(rel) if isinstance(rel, list) else rel
                    
                    if rel_str == 'canonical':
                        links['canonical'] = href
                    elif rel_str == 'next':
                        links['next'] = href
                    elif rel_str == 'prev':
                        links['prev'] = href
                    elif rel_str in ['alternate', 'stylesheet', 'icon']:
                        links[rel_str].append({
                            'href': href,
                            'type': link.get('type'),
                            'media': link.get('media')
                        })
            
            metadata['links'] = links
            
            return metadata
            
        except Exception as e:
            logger.error(f"HTML metadata extraction failed: {str(e)}")
            return {}
    
    @staticmethod
    def extract_images(html: str, base_url: str = "") -> List[Dict[str, Any]]:
        """
        Extract image information from HTML
        """
        try:
            soup = BeautifulSoup(html, 'html.parser')
            images = []
            
            for img in soup.find_all('img'):
                src = img.get('src')
                if not src:
                    continue
                
                # Convert relative URLs to absolute
                if base_url and not src.startswith(('http://', 'https://')):
                    src = urljoin(base_url, src)
                
                image_info = {
                    'src': src,
                    'alt': img.get('alt', ''),
                    'title': img.get('title', ''),
                    'width': img.get('width'),
                    'height': img.get('height'),
                    'loading': img.get('loading'),
                    'srcset': img.get('srcset')
                }
                
                images.append(image_info)
            
            return images
            
        except Exception as e:
            logger.error(f"HTML image extraction failed: {str(e)}")
            return []


class PerformanceOptimizer:
    """
    Performance optimization utilities
    """
    
    @staticmethod
    async def batch_process(items: List[Any], 
                          process_func: callable, 
                          batch_size: int = 10,
                          max_concurrent: int = 5) -> List[Any]:
        """
        Process items in batches with concurrency control
        """
        results = []
        semaphore = asyncio.Semaphore(max_concurrent)
        
        async def process_item(item):
            async with semaphore:
                return await process_func(item)
        
        # Process items in batches
        for i in range(0, len(items), batch_size):
            batch = items[i:i + batch_size]
            batch_tasks = [process_item(item) for item in batch]
            batch_results = await asyncio.gather(*batch_tasks, return_exceptions=True)
            results.extend(batch_results)
            
            # Small delay between batches to prevent overwhelming
            if i + batch_size < len(items):
                await asyncio.sleep(0.1)
        
        return results
    
    @staticmethod
    def create_content_hash(content: str, algorithm: str = 'sha256') -> str:
        """
        Create hash of content for caching and deduplication
        """
        if algorithm == 'md5':
            hasher = hashlib.md5()
        elif algorithm == 'sha1':
            hasher = hashlib.sha1()
        elif algorithm == 'sha256':
            hasher = hashlib.sha256()
        else:
            hasher = hashlib.sha256()
        
        hasher.update(content.encode('utf-8'))
        return hasher.hexdigest()
    
    @staticmethod
    def compress_content(content: str, method: str = 'gzip') -> bytes:
        """
        Compress content for efficient storage
        """
        import gzip
        import zlib
        
        if method == 'gzip':
            return gzip.compress(content.encode('utf-8'))
        elif method == 'zlib':
            return zlib.compress(content.encode('utf-8'))
        else:
            return content.encode('utf-8')
    
    @staticmethod
    def decompress_content(compressed_data: bytes, method: str = 'gzip') -> str:
        """
        Decompress content
        """
        import gzip
        import zlib
        
        try:
            if method == 'gzip':
                return gzip.decompress(compressed_data).decode('utf-8')
            elif method == 'zlib':
                return zlib.decompress(compressed_data).decode('utf-8')
            else:
                return compressed_data.decode('utf-8')
        except Exception as e:
            logger.error(f"Decompression failed: {str(e)}")
            return ""


class RobotsChecker:
    """
    Robots.txt compliance checker
    """
    
    def __init__(self, user_agent: str = "*"):
        self.user_agent = user_agent
        self._cache = {}
        self._cache_ttl = 3600  # 1 hour
    
    async def can_fetch(self, url: str) -> bool:
        """
        Check if URL can be fetched according to robots.txt
        """
        try:
            parsed_url = urlparse(url)
            robots_url = f"{parsed_url.scheme}://{parsed_url.netloc}/robots.txt"
            
            # Check cache first
            cache_key = f"{robots_url}:{self.user_agent}"
            if cache_key in self._cache:
                cached_data, timestamp = self._cache[cache_key]
                if time.time() - timestamp < self._cache_ttl:
                    rp = cached_data
                else:
                    del self._cache[cache_key]
                    rp = await self._fetch_robots(robots_url)
            else:
                rp = await self._fetch_robots(robots_url)
            
            if rp:
                return rp.can_fetch(self.user_agent, url)
            else:
                # If robots.txt cannot be fetched, assume allowed
                return True
                
        except Exception as e:
            logger.warning(f"Robots.txt check failed for {url}: {str(e)}")
            return True  # Default to allowing if check fails
    
    async def _fetch_robots(self, robots_url: str) -> Optional[RobotFileParser]:
        """
        Fetch and parse robots.txt
        """
        try:
            rp = RobotFileParser()
            rp.set_url(robots_url)
            
            # Fetch robots.txt content
            response = requests.get(robots_url, timeout=10)
            if response.status_code == 200:
                rp.set_url(robots_url)
                rp.feed(response.text)
                
                # Cache the result
                cache_key = f"{robots_url}:{self.user_agent}"
                self._cache[cache_key] = (rp, time.time())
                
                return rp
            else:
                return None
                
        except Exception as e:
            logger.warning(f"Failed to fetch robots.txt from {robots_url}: {str(e)}")
            return None


class UserAgentRotator:
    """
    User agent rotation utility
    """
    
    def __init__(self):
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Safari/605.1.15',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Edge/120.0.0.0',
        ]
        self.current_index = 0
    
    def get_random_user_agent(self) -> str:
        """Get random user agent string"""
        return random.choice(self.user_agents)
    
    def get_next_user_agent(self) -> str:
        """Get next user agent in rotation"""
        ua = self.user_agents[self.current_index]
        self.current_index = (self.current_index + 1) % len(self.user_agents)
        return ua
    
    def add_user_agent(self, user_agent: str) -> None:
        """Add custom user agent to rotation"""
        if user_agent not in self.user_agents:
            self.user_agents.append(user_agent)


def create_fingerprint(data: Union[str, dict]) -> str:
    """
    Create unique fingerprint for data
    """
    if isinstance(data, dict):
        # Sort dictionary keys for consistent hashing
        sorted_data = json.dumps(data, sort_keys=True)
    else:
        sorted_data = str(data)
    
    return hashlib.sha256(sorted_data.encode('utf-8')).hexdigest()


def sanitize_filename(filename: str, max_length: int = 255) -> str:
    """
    Sanitize filename for safe storage
    """
    # Remove or replace invalid characters
    invalid_chars = '<>:"/\\|?*'
    for char in invalid_chars:
        filename = filename.replace(char, '_')
    
    # Remove control characters
    filename = ''.join(char for char in filename if ord(char) >= 32)
    
    # Truncate if too long
    if len(filename) > max_length:
        name, ext = filename.rsplit('.', 1) if '.' in filename else (filename, '')
        max_name_length = max_length - len(ext) - 1 if ext else max_length
        filename = name[:max_name_length] + ('.' + ext if ext else '')
    
    return filename.strip()


def calculate_similarity_score(text1: str, text2: str) -> float:
    """
    Calculate simple similarity score between two texts
    """
    if not text1 or not text2:
        return 0.0
    
    # Simple Jaccard similarity
    words1 = set(text1.lower().split())
    words2 = set(text2.lower().split())
    
    intersection = words1.intersection(words2)
    union = words1.union(words2)
    
    if not union:
        return 0.0
    
    return len(intersection) / len(union)


async def retry_with_backoff(func: callable, 
                           max_retries: int = 3,
                           base_delay: float = 1.0,
                           max_delay: float = 60.0) -> Any:
    """
    Retry function with exponential backoff
    """
    for attempt in range(max_retries):
        try:
            return await func()
        except Exception as e:
            if attempt == max_retries - 1:
                raise e
            
            delay = min(base_delay * (2 ** attempt), max_delay)
            logger.warning(f"Attempt {attempt + 1} failed, retrying in {delay}s: {str(e)}")
            await asyncio.sleep(delay)


def format_bytes(bytes_count: int) -> str:
    """
    Format bytes into human readable format
    """
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if bytes_count < 1024.0:
            return f"{bytes_count:.1f} {unit}"
        bytes_count /= 1024.0
    return f"{bytes_count:.1f} PB"


def format_duration(seconds: float) -> str:
    """
    Format duration in seconds to human readable format
    """
    if seconds < 60:
        return f"{seconds:.1f}s"
    elif seconds < 3600:
        minutes = seconds / 60
        return f"{minutes:.1f}m"
    elif seconds < 86400:
        hours = seconds / 3600
        return f"{hours:.1f}h"
    else:
        days = seconds / 86400
        return f"{days:.1f}d"


# Export main utilities
__all__ = [
    'URLProcessor',
    'ContentAnalyzer',
    'HTMLProcessor',
    'PerformanceOptimizer',
    'RobotsChecker',
    'UserAgentRotator',
    'create_fingerprint',
    'sanitize_filename',
    'calculate_similarity_score',
    'retry_with_backoff',
    'format_bytes',
    'format_duration'
]
