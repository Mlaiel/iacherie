"""Advanced Content Scraper - IA-Influencer-Agent
==============================================

Specialized content extraction and analysis scraper.
Designed for content discovery and protection monitoring.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: All rights reserved. Unauthorized use, reproduction, or distribution prohibited.

⚠️ CRITICAL LEGAL WARNING ⚠️
UNAUTHORIZED USE, COPYING, OR DISTRIBUTION IS STRICTLY PROHIBITED AND WILL RESULT IN IMMEDIATE LEGAL ACTION.
This technology is EXCLUSIVE property of Fahed Mlaiel. Contact: mlaiel@live.de for licensing.
"""import asyncio
import hashlib
import mimetypes
import re
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from datetime import datetime
import logging
from urllib.parse import urlparse, urljoin
from bs4 import BeautifulSoup
import trafilatura
import newspaper
from goose3 import Goose
import textstat
from readability import Readability
import langdetect
import requests
from PIL import Image
import io
import base64
import json

@dataclass
class ContentResult:
    """Structured content extraction result."""    url: str
    title: str
    content: str
    summary: str
    authors: List[str]
    publish_date: Optional[datetime]
    language: str
    content_type: str
    word_count: int
    reading_time: int
    readability_score: float
    sentiment_score: float
    tags: List[str]
    images: List[Dict[str, str]]
    videos: List[Dict[str, str]]
    links: List[str]
    metadata: Dict[str, Any]
    fingerprint: str
    quality_score: float
    timestamp: datetime

@dataclass
class MediaContent:
    """Media content information."""    url: str
    type: str  # image, video, audio
    title: str
    description: str
    duration: Optional[int]
    size: Optional[int]
    format: str
    thumbnail: Optional[str]
    metadata: Dict[str, Any]

class ContentScraper:
    """    Advanced content extraction and analysis scraper.
    
    Features:
    - Multi-engine content extraction
    - Content quality analysis
    - Media detection and extraction
    - Language detection
    - Readability analysis
    - Content fingerprinting
    - Duplicate detection
    """    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.goose = Goose()
        self.extraction_engines = ['trafilatura', 'newspaper', 'goose', 'beautifulsoup']
        
    def extract_content(self, url: str, html: str) -> ContentResult:
        """Extract content using multiple engines with fallback."""        results = {}
        
        # Try each extraction engine
        for engine in self.extraction_engines:
            try:
                if engine == 'trafilatura':
                    results[engine] = self._extract_with_trafilatura(html, url)
                elif engine == 'newspaper':
                    results[engine] = self._extract_with_newspaper(url)
                elif engine == 'goose':
                    results[engine] = self._extract_with_goose(html)
                elif engine == 'beautifulsoup':
                    results[engine] = self._extract_with_beautifulsoup(html, url)
            except Exception as e:
                self.logger.warning(f"Engine {engine} failed for {url}: {e}")
                results[engine] = None
                
        # Combine results using best available data
        return self._combine_extraction_results(url, html, results)
        
    def _extract_with_trafilatura(self, html: str, url: str) -> Dict[str, Any]:
        """Extract content using Trafilatura."""        content = trafilatura.extract(
            html,
            include_comments=False,
            include_tables=True,
            include_formatting=True,
            favor_precision=True
        )
        
        metadata = trafilatura.extract_metadata(html)
        
        return {
            'content': content or '',
            'title': metadata.title if metadata else '',
            'author': metadata.author if metadata else '',
            'date': metadata.date if metadata else None,
            'description': metadata.description if metadata else '',
            'sitename': metadata.sitename if metadata else '',
            'url': metadata.url if metadata else url
        }
        
    def _extract_with_newspaper(self, url: str) -> Dict[str, Any]:
        """Extract content using Newspaper3k."""        try:
            article = newspaper.Article(url)
            article.download()
            article.parse()
            article.nlp()
            
            return {
                'content': article.text,
                'title': article.title,
                'authors': article.authors,
                'publish_date': article.publish_date,
                'summary': article.summary,
                'keywords': article.keywords,
                'top_image': article.top_image,
                'images': list(article.images),
                'videos': list(article.movies)
            }
        except Exception as e:
            self.logger.warning(f"Newspaper extraction failed: {e}")
            return {}
            
    def _extract_with_goose(self, html: str) -> Dict[str, Any]:
        """Extract content using Goose3."""        try:
            article = self.goose.extract(raw_html=html)
            
            return {
                'content': article.cleaned_text,
                'title': article.title,
                'meta_description': article.meta_description,
                'meta_keywords': article.meta_keywords,
                'publish_date': article.publish_date,
                'authors': [article.authors] if article.authors else [],
                'top_image': article.top_image.src if article.top_image else None,
                'images': [img.src for img in article.images] if article.images else [],
                'videos': [video.src for video in article.movies] if article.movies else []
            }
        except Exception as e:
            self.logger.warning(f"Goose extraction failed: {e}")
            return {}
            
    def _extract_with_beautifulsoup(self, html: str, url: str) -> Dict[str, Any]:
        """Extract content using BeautifulSoup."""        soup = BeautifulSoup(html, 'html.parser')
        
        # Remove script and style elements
        for script in soup(["script", "style", "nav", "header", "footer", "aside"]):
            script.decompose()
            
        # Extract title
        title = ''
        title_tag = soup.find('title')
        if title_tag:
            title = title_tag.get_text().strip()
            
        # Extract main content
        content_selectors = [
            'article', 'main', '[role="main"]', '.content', '.post-content',
            '.entry-content', '.article-content', '.post-body', '.story-body'
        ]
        
        content = ''
        for selector in content_selectors:
            content_tag = soup.select_one(selector)
            if content_tag:
                content = content_tag.get_text(separator=' ', strip=True)
                break
                
        if not content:
            # Fallback to body content
            body = soup.find('body')
            if body:
                content = body.get_text(separator=' ', strip=True)
                
        # Extract metadata
        meta_data = {}
        for meta in soup.find_all('meta'):
            name = meta.get('name') or meta.get('property')
            content_attr = meta.get('content')
            if name and content_attr:
                meta_data[name] = content_attr
                
        # Extract images
        images = []
        for img in soup.find_all('img'):
            src = img.get('src')
            if src:
                full_url = urljoin(url, src)
                images.append({
                    'src': full_url,
                    'alt': img.get('alt', ''),
                    'title': img.get('title', '')
                })
                
        # Extract links
        links = []
        for link in soup.find_all('a', href=True):
            href = link['href']
            full_url = urljoin(url, href)
            links.append(full_url)
            
        return {
            'content': content,
            'title': title,
            'meta_data': meta_data,
            'images': images,
            'links': links
        }
        
    def _combine_extraction_results(self, url: str, html: str, results: Dict[str, Any]) -> ContentResult:
        """Combine results from multiple extraction engines."""        # Choose best title
        title = (
            results.get('trafilatura', {}).get('title') or
            results.get('newspaper', {}).get('title') or
            results.get('goose', {}).get('title') or
            results.get('beautifulsoup', {}).get('title') or
            'Unknown Title'
        )
        
        # Choose best content
        content = (
            results.get('trafilatura', {}).get('content') or
            results.get('newspaper', {}).get('content') or
            results.get('goose', {}).get('content') or
            results.get('beautifulsoup', {}).get('content') or
            ''
        )
        
        # Combine authors
        authors = []
        for engine_result in results.values():
            if engine_result:
                if 'authors' in engine_result and engine_result['authors']:
                    authors.extend(engine_result['authors'])
                elif 'author' in engine_result and engine_result['author']:
                    authors.append(engine_result['author'])
                    
        authors = list(set(authors))  # Remove duplicates
        
        # Get publish date
        publish_date = None
        for engine_result in results.values():
            if engine_result and engine_result.get('publish_date'):
                publish_date = engine_result['publish_date']
                break
                
        # Combine images
        images = []
        for engine_result in results.values():
            if engine_result and 'images' in engine_result:
                images.extend(engine_result['images'])
                
        # Combine videos
        videos = []
        for engine_result in results.values():
            if engine_result and 'videos' in engine_result:
                videos.extend(engine_result['videos'])
                
        # Combine links
        links = []
        for engine_result in results.values():
            if engine_result and 'links' in engine_result:
                links.extend(engine_result['links'])
                
        # Get summary
        summary = (
            results.get('newspaper', {}).get('summary') or
            self._generate_summary(content)
        )
        
        # Detect language
        language = self._detect_language(content)
        
        # Calculate metrics
        word_count = len(content.split())
        reading_time = self._calculate_reading_time(word_count)
        readability_score = self._calculate_readability(content)
        
        # Generate content fingerprint
        fingerprint = self._generate_fingerprint(content)
        
        # Calculate quality score
        quality_score = self._calculate_quality_score(
            content, title, word_count, readability_score
        )
        
        return ContentResult(
            url=url,
            title=title,
            content=content,
            summary=summary,
            authors=authors,
            publish_date=publish_date,
            language=language,
            content_type=self._detect_content_type(html),
            word_count=word_count,
            reading_time=reading_time,
            readability_score=readability_score,
            sentiment_score=self._analyze_sentiment(content),
            tags=self._extract_tags(content),
            images=images,
            videos=videos,
            links=links,
            metadata=self._extract_metadata(html),
            fingerprint=fingerprint,
            quality_score=quality_score,
            timestamp=datetime.now()
        )
        
    def _detect_language(self, text: str) -> str:
        """Detect content language."""        try:
            if len(text) > 50:
                detected = langdetect.detect(text)
                # Validate detected language
                if detected in ['en', 'fr', 'de', 'es', 'it', 'pt', 'nl', 'ru', 'zh', 'ja', 'ko', 'ar']:
                    return detected
        except Exception as e:
            self.logger.debug(f"Language detection failed: {e}")
        return 'unknown'
    
    def _analyze_sentiment(self, text: str) -> float:
        """Analyze sentiment of content text."""        try:
            # Simple sentiment analysis using TextBlob
            from textblob import TextBlob
            
            if len(text) > 100:
                blob = TextBlob(text)
                # Return polarity (-1 to 1, where -1 is negative, 1 is positive)
                return float(blob.sentiment.polarity)
        except ImportError:
            # Fallback: basic keyword-based sentiment
            positive_words = ['good', 'great', 'excellent', 'amazing', 'wonderful', 'fantastic', 'love', 'best', 'awesome', 'perfect']
            negative_words = ['bad', 'terrible', 'awful', 'horrible', 'hate', 'worst', 'disgusting', 'annoying', 'stupid', 'useless']
            
            words = text.lower().split()
            positive_count = sum(1 for word in words if word in positive_words)
            negative_count = sum(1 for word in words if word in negative_words)
            
            total_sentiment_words = positive_count + negative_count
            if total_sentiment_words > 0:
                return (positive_count - negative_count) / total_sentiment_words
        except Exception as e:
            self.logger.debug(f"Sentiment analysis failed: {e}")
        
        return 0.0  # Neutral sentiment
        
    def _calculate_reading_time(self, word_count: int) -> int:
        """Calculate estimated reading time in minutes."""        words_per_minute = 200
        return max(1, word_count // words_per_minute)
        
    def _calculate_readability(self, text: str) -> float:
        """Calculate readability score."""        try:
            if len(text) > 100:
                # Use Flesch Reading Ease score (0-100, higher is easier)
                score = textstat.flesch_reading_ease(text)
                return max(0.0, min(100.0, score))  # Clamp between 0-100
        except Exception as e:
            self.logger.debug(f"Readability calculation failed: {e}")
            
        # Fallback: simple sentence/word ratio calculation
        try:
            sentences = len(re.split(r'[.!?]+', text))
            words = len(text.split())
            if sentences > 0:
                avg_sentence_length = words / sentences
                # Simple score: shorter sentences = higher readability
                # Scale to 0-100 range
                score = max(0, 100 - (avg_sentence_length * 2))
                return min(100.0, score)
        except:
            pass
            
        return 50.0  # Default medium readability
        
    def _generate_summary(self, content: str, max_sentences: int = 3) -> str:
        """Generate simple extractive summary."""        sentences = re.split(r'[.!?]+', content)
        sentences = [s.strip() for s in sentences if len(s.strip()) > 20]
        
        if len(sentences) <= max_sentences:
            return '. '.join(sentences) + '.'
            
        # Simple scoring based on sentence length and position
        scored_sentences = []
        for i, sentence in enumerate(sentences):
            score = len(sentence.split())  # Word count
            if i < 3:  # First few sentences get bonus
                score *= 1.5
            scored_sentences.append((score, sentence))
            
        # Sort by score and take top sentences
        scored_sentences.sort(reverse=True)
        top_sentences = [s[1] for s in scored_sentences[:max_sentences]]
        
        return '. '.join(top_sentences) + '.'
        
    def _generate_fingerprint(self, content: str) -> str:
        """Generate content fingerprint for similarity detection."""        # Normalize content
        normalized = re.sub(r'\s+', ' ', content.lower().strip())
        
        # Create hash
        return hashlib.sha256(normalized.encode()).hexdigest()
        
    def _calculate_quality_score(self, content: str, title: str, 
                                word_count: int, readability: float) -> float:
        """Calculate content quality score (0-100)."""        score = 0
        
        # Content length score (30 points)
        if word_count >= 300:
            score += 30
        elif word_count >= 100:
            score += 20
        elif word_count >= 50:
            score += 10
            
        # Title quality (20 points)
        if title and len(title) > 10:
            score += 20
        elif title and len(title) > 5:
            score += 10
            
        # Readability score (25 points)
        if readability >= 60:
            score += 25
        elif readability >= 30:
            score += 15
        elif readability >= 0:
            score += 5
            
        # Content structure (25 points)
        paragraphs = content.split('\n\n')
        if len(paragraphs) >= 3:
            score += 25
        elif len(paragraphs) >= 2:
            score += 15
        else:
            score += 5
            
        return min(100, score)
        
    def _extract_tags(self, content: str) -> List[str]:
        """Extract potential tags from content."""        # Simple keyword extraction
        words = re.findall(r'\b[A-Za-z]{3,}\b', content.lower())
        word_freq = {}
        
        for word in words:
            if word not in ['the', 'and', 'for', 'are', 'but', 'not', 'you', 'all', 'can', 'had', 'her', 'was', 'one', 'our', 'out', 'day', 'get', 'has', 'him', 'his', 'how', 'its', 'may', 'new', 'now', 'old', 'see', 'two', 'who', 'boy', 'did', 'she', 'use', 'way', 'what', 'with']:
                word_freq[word] = word_freq.get(word, 0) + 1
                
        # Get top 10 most frequent words
        sorted_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
        return [word for word, freq in sorted_words[:10] if freq >= 2]
        
    def _detect_content_type(self, html: str) -> str:
        """Detect content type from HTML structure."""        soup = BeautifulSoup(html, 'html.parser')
        
        # Check for common content types
        if soup.find('article'):
            return 'article'
        elif soup.find(class_=re.compile(r'blog|post')):
            return 'blog_post'
        elif soup.find(class_=re.compile(r'news')):
            return 'news'
        elif soup.find(class_=re.compile(r'product')):
            return 'product'
        elif soup.find('video') or soup.find('iframe'):
            return 'media'
        else:
            return 'webpage'
            
    def _extract_metadata(self, html: str) -> Dict[str, Any]:
        """Extract comprehensive metadata from HTML."""        soup = BeautifulSoup(html, 'html.parser')
        metadata = {}
        
        # Meta tags
        for meta in soup.find_all('meta'):
            name = meta.get('name') or meta.get('property') or meta.get('http-equiv')
            content = meta.get('content')
            if name and content:
                metadata[name] = content
                
        # Schema.org data
        schema_data = []
        for script in soup.find_all('script', type='application/ld+json'):
            try:
                data = json.loads(script.string)
                schema_data.append(data)
            except Exception as e:
                self.logger.debug(f"Failed to parse schema.org data: {e}")
                continue
                
        if schema_data:
            metadata['schema_org'] = schema_data
            
        return metadata
        
    def analyze_media_content(self, url: str) -> Optional[MediaContent]:
        """Analyze media content (images, videos, audio)."""        try:
            response = requests.head(url, timeout=10)
            content_type = response.headers.get('content-type', '')
            content_length = response.headers.get('content-length')
            
            media_type = None
            if content_type.startswith('image/'):
                media_type = 'image'
            elif content_type.startswith('video/'):
                media_type = 'video'
            elif content_type.startswith('audio/'):
                media_type = 'audio'
            else:
                return None
                
            # Get additional info for images
            format_info = content_type.split('/')[-1]
            
            return MediaContent(
                url=url,
                type=media_type,
                title=urlparse(url).path.split('/')[-1],
                description='',
                duration=None,
                size=int(content_length) if content_length else None,
                format=format_info,
                thumbnail=None,
                metadata={
                    'content_type': content_type,
                    'headers': dict(response.headers)
                }
            )
            
        except Exception as e:
            self.logger.warning(f"Failed to analyze media content {url}: {e}")
            return None
            
    def detect_duplicate_content(self, content1: str, content2: str, 
                               threshold: float = 0.8) -> bool:
        """Detect if two content pieces are duplicates."""        # Simple similarity check using character overlap
        if not content1 or not content2:
            return False
            
        # Normalize content
        norm1 = re.sub(r'\s+', ' ', content1.lower().strip())
        norm2 = re.sub(r'\s+', ' ', content2.lower().strip())
        
        # Calculate similarity
        longer = norm1 if len(norm1) > len(norm2) else norm2
        shorter = norm2 if len(norm1) > len(norm2) else norm1
        
        if len(longer) == 0:
            return True
            
        matches = 0
        for i in range(len(shorter)):
            if i < len(longer) and shorter[i] == longer[i]:
                matches += 1
                
        similarity = matches / len(longer)
        return similarity >= threshold
        
    def extract_contact_info(self, content: str) -> Dict[str, List[str]]:
        """Extract contact information from content."""        contact_info = {
            'emails': [],
            'phones': [],
            'urls': [],
            'social_media': []
        }
        
        # Email regex
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        contact_info['emails'] = re.findall(email_pattern, content)
        
        # Phone regex (basic)
        phone_pattern = r'(\+?1[-.\s]?)?\(?([0-9]{3})\)?[-.\s]?([0-9]{3})[-.\s]?([0-9]{4})'
        phones = re.findall(phone_pattern, content)
        contact_info['phones'] = [''.join(phone) for phone in phones]
        
        # URL regex
        url_pattern = r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
        contact_info['urls'] = re.findall(url_pattern, content)
        
        # Social media patterns
        social_patterns = [
            r'@([A-Za-z0-9_]+)',  # Twitter/Instagram handles
            r'facebook\.com/([A-Za-z0-9.]+)',
            r'linkedin\.com/in/([A-Za-z0-9-]+)',
            r'youtube\.com/c/([A-Za-z0-9_-]+)'
        ]
        
        for pattern in social_patterns:
            matches = re.findall(pattern, content)
            contact_info['social_media'].extend(matches)
            
        return contact_info
