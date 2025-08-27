"""
URL Validator Module
====================

Professional URL validation and normalization for web crawling operations.
Implements comprehensive URL validation with security checks and platform-specific rules.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: All rights reserved. Unauthorized use, reproduction, or distribution prohibited.

WARNING: This code is protected by copyright law. Any unauthorized copying, 
distribution, or modification is strictly prohibited and will result in 
legal action. Contact mlaiel@live.de for licensing.

Project Team Specialties:
- Lead Dev IA: Advanced AI integration and machine learning
- Backend Senior: Scalable architecture and microservices  
- ML Engineer: Content analysis and recommendation systems
- DBA: High-performance database optimization
- Security Expert: Enterprise-grade security and encryption
- Microservices Architect: Distributed systems design
- Audio Engineer: Advanced audio processing and analysis
- DevOps Engineer: CI/CD and infrastructure automation
- IA Prompt Engineer: Intelligent prompt optimization
"""

import re
import logging
from typing import Dict, List, Optional, Tuple, Set
from urllib.parse import urlparse, urljoin, quote, unquote, parse_qs
from dataclasses import dataclass
import tldextract
import requests
import asyncio
import aiohttp
from enum import Enum

logger = logging.getLogger(__name__)

class URLType(Enum):
    """URL type classification."""
    YOUTUBE_VIDEO = "youtube_video"
    YOUTUBE_CHANNEL = "youtube_channel"
    YOUTUBE_PLAYLIST = "youtube_playlist"
    INSTAGRAM_POST = "instagram_post"
    INSTAGRAM_PROFILE = "instagram_profile"
    INSTAGRAM_REEL = "instagram_reel"
    TIKTOK_VIDEO = "tiktok_video"
    TIKTOK_PROFILE = "tiktok_profile"
    TWITTER_POST = "twitter_post"
    TWITTER_PROFILE = "twitter_profile"
    FACEBOOK_POST = "facebook_post"
    FACEBOOK_PAGE = "facebook_page"
    SPOTIFY_TRACK = "spotify_track"
    SPOTIFY_ALBUM = "spotify_album"
    SPOTIFY_ARTIST = "spotify_artist"
    SPOTIFY_PLAYLIST = "spotify_playlist"
    SUBSTACK_POST = "substack_post"
    SUBSTACK_PROFILE = "substack_profile"
    GENERIC_WEB = "generic_web"
    UNKNOWN = "unknown"

@dataclass
class URLValidationResult:
    """URL validation result structure."""
    is_valid: bool
    normalized_url: str
    url_type: URLType
    platform: str
    content_id: Optional[str]
    metadata: Dict
    security_score: float
    validation_errors: List[str]

@dataclass
class URLMetadata:
    """URL metadata extraction result."""
    title: Optional[str]
    description: Optional[str]
    canonical_url: Optional[str]
    content_type: Optional[str]
    language: Optional[str]
    author: Optional[str]
    published_date: Optional[str]
    tags: List[str]
    thumbnail_url: Optional[str]

class URLValidator:
    """
    Professional URL validator with comprehensive validation and normalization.
    
    Features:
    - Platform-specific URL validation
    - Security assessment
    - Content type detection
    - URL normalization and cleanup
    - Metadata extraction
    - Malicious URL detection
    - Content accessibility verification
    """
    
    def __init__(self):
        """Initialize URL validator."""
        self.blocked_domains = set()
        self.allowed_domains = set()
        self.suspicious_patterns = []
        self._load_security_rules()
        
        # Platform-specific URL patterns
        self.platform_patterns = {
            'youtube': {
                'domain_pattern': r'(?:youtube\.com|youtu\.be)',
                'video_pattern': r'(?:watch\?v=|youtu\.be/)([a-zA-Z0-9_-]{11})',
                'channel_pattern': r'(?:channel/|user/|c/)([a-zA-Z0-9_-]+)',
                'playlist_pattern': r'playlist\?list=([a-zA-Z0-9_-]+)'
            },
            'instagram': {
                'domain_pattern': r'instagram\.com',
                'post_pattern': r'/p/([a-zA-Z0-9_-]+)',
                'profile_pattern': r'/([a-zA-Z0-9_.]+)/?$',
                'reel_pattern': r'/reel/([a-zA-Z0-9_-]+)'
            },
            'tiktok': {
                'domain_pattern': r'tiktok\.com',
                'video_pattern': r'/@[a-zA-Z0-9_.]+/video/(\d+)',
                'profile_pattern': r'/@([a-zA-Z0-9_.]+)'
            },
            'twitter': {
                'domain_pattern': r'(?:twitter\.com|x\.com)',
                'post_pattern': r'/status/(\d+)',
                'profile_pattern': r'/([a-zA-Z0-9_]+)/?$'
            },
            'facebook': {
                'domain_pattern': r'facebook\.com',
                'post_pattern': r'/posts/(\d+)',
                'page_pattern': r'/([a-zA-Z0-9.]+)/?$'
            },
            'spotify': {
                'domain_pattern': r'(?:open\.spotify\.com|spotify\.com)',
                'track_pattern': r'/track/([a-zA-Z0-9]+)',
                'album_pattern': r'/album/([a-zA-Z0-9]+)',
                'artist_pattern': r'/artist/([a-zA-Z0-9]+)',
                'playlist_pattern': r'/playlist/([a-zA-Z0-9]+)'
            },
            'substack': {
                'domain_pattern': r'\.substack\.com',
                'post_pattern': r'/p/([a-zA-Z0-9-]+)',
                'profile_pattern': r'^https://([a-zA-Z0-9-]+)\.substack\.com/?$'
            }
        }
    
    def _load_security_rules(self) -> None:
        """Load security rules for URL validation."""
        # Blocked domains (malware, phishing, etc.)
        self.blocked_domains.update([
            'malware-example.com',
            'phishing-site.net',
            'suspicious-domain.org'
        ])
        
        # Suspicious URL patterns
        self.suspicious_patterns = [
            r'bit\.ly/[a-zA-Z0-9]+',  # Shortened URLs
            r'tinyurl\.com/',
            r'[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}',  # IP addresses
            r'localhost',
            r'127\.0\.0\.1',
            r'\.tk$',  # Suspicious TLD
            r'\.ml$',
            r'data:',  # Data URLs
            r'javascript:',  # JavaScript URLs
        ]
    
    async def validate_url(self, url: str) -> URLValidationResult:
        """
        Comprehensive URL validation.
        
        Args:
            url: URL to validate
            
        Returns:
            URLValidationResult with validation details
        """
        validation_errors = []
        metadata = {}
        
        try:
            # Basic URL structure validation
            if not self._is_valid_url_structure(url):
                validation_errors.append("Invalid URL structure")
                return URLValidationResult(
                    is_valid=False,
                    normalized_url=url,
                    url_type=URLType.UNKNOWN,
                    platform="unknown",
                    content_id=None,
                    metadata=metadata,
                    security_score=0.0,
                    validation_errors=validation_errors
                )
            
            # Normalize URL
            normalized_url = self._normalize_url(url)
            
            # Security assessment
            security_score = self._assess_security(normalized_url)
            if security_score < 0.5:
                validation_errors.append("URL failed security assessment")
            
            # Platform and content type detection
            url_type, platform, content_id = self._detect_platform_and_type(normalized_url)
            
            # Content accessibility check
            is_accessible = await self._check_accessibility(normalized_url)
            if not is_accessible:
                validation_errors.append("URL is not accessible")
            
            # Extract metadata
            if is_accessible:
                metadata = await self._extract_metadata(normalized_url)
            
            is_valid = len(validation_errors) == 0 and security_score >= 0.5
            
            return URLValidationResult(
                is_valid=is_valid,
                normalized_url=normalized_url,
                url_type=url_type,
                platform=platform,
                content_id=content_id,
                metadata=metadata,
                security_score=security_score,
                validation_errors=validation_errors
            )
            
        except Exception as e:
            logger.error(f"URL validation error: {str(e)}")
            validation_errors.append(f"Validation exception: {str(e)}")
            
            return URLValidationResult(
                is_valid=False,
                normalized_url=url,
                url_type=URLType.UNKNOWN,
                platform="unknown",
                content_id=None,
                metadata=metadata,
                security_score=0.0,
                validation_errors=validation_errors
            )
    
    def _is_valid_url_structure(self, url: str) -> bool:
        """Validate basic URL structure."""
        try:
            result = urlparse(url)
            return all([result.scheme, result.netloc])
        except Exception:
            return False
    
    def _normalize_url(self, url: str) -> str:
        """Normalize URL for consistent processing."""
        try:
            # Parse URL
            parsed = urlparse(url)
            
            # Normalize scheme
            scheme = parsed.scheme.lower()
            if scheme not in ['http', 'https']:
                scheme = 'https'
            
            # Normalize domain
            domain = parsed.netloc.lower()
            
            # Remove common tracking parameters
            query_params = parse_qs(parsed.query)
            clean_params = {}
            
            # Keep only essential parameters
            essential_params = {
                'v',  # YouTube video ID
                'list',  # YouTube playlist
                'p',  # Instagram post
                't',  # Time parameter
                'utm_source', 'utm_medium', 'utm_campaign'  # Analytics
            }
            
            for param, values in query_params.items():
                if param in essential_params:
                    clean_params[param] = values
            
            # Rebuild query string
            query_parts = []
            for param, values in clean_params.items():
                for value in values:
                    query_parts.append(f"{param}={quote(value)}")
            
            clean_query = '&'.join(query_parts)
            
            # Rebuild URL
            normalized = f"{scheme}://{domain}{parsed.path}"
            if clean_query:
                normalized += f"?{clean_query}"
            
            return normalized
            
        except Exception as e:
            logger.warning(f"URL normalization failed: {e}")
            return url
    
    def _assess_security(self, url: str) -> float:
        """Assess URL security (0.0 = dangerous, 1.0 = safe)."""
        score = 1.0
        
        try:
            parsed = urlparse(url)
            domain = parsed.netloc.lower()
            
            # Check blocked domains
            if domain in self.blocked_domains:
                return 0.0
            
            # Check suspicious patterns
            for pattern in self.suspicious_patterns:
                if re.search(pattern, url, re.IGNORECASE):
                    score -= 0.3
            
            # Check for HTTPS
            if parsed.scheme != 'https':
                score -= 0.2
            
            # Check domain reputation
            extracted = tldextract.extract(url)
            
            # Suspicious TLDs
            suspicious_tlds = ['tk', 'ml', 'ga', 'cf']
            if extracted.suffix in suspicious_tlds:
                score -= 0.3
            
            # Very short domains (potential typosquatting)
            if len(extracted.domain) < 4:
                score -= 0.2
            
            # Multiple subdomains (potential phishing)
            if len(extracted.subdomain.split('.')) > 2:
                score -= 0.1
            
            return max(0.0, min(1.0, score))
            
        except Exception as e:
            logger.warning(f"Security assessment failed: {e}")
            return 0.5
    
    def _detect_platform_and_type(self, url: str) -> Tuple[URLType, str, Optional[str]]:
        """Detect platform and content type from URL."""
        try:
            for platform, patterns in self.platform_patterns.items():
                domain_pattern = patterns['domain_pattern']
                
                if re.search(domain_pattern, url, re.IGNORECASE):
                    # Check specific content types for this platform
                    for content_type, pattern in patterns.items():
                        if content_type == 'domain_pattern':
                            continue
                        
                        match = re.search(pattern, url, re.IGNORECASE)
                        if match:
                            content_id = match.group(1) if match.groups() else None
                            url_type = self._get_url_type(platform, content_type)
                            return url_type, platform, content_id
                    
                    # Default type for platform
                    return URLType.GENERIC_WEB, platform, None
            
            return URLType.GENERIC_WEB, "unknown", None
            
        except Exception as e:
            logger.warning(f"Platform detection failed: {e}")
            return URLType.UNKNOWN, "unknown", None
    
    def _get_url_type(self, platform: str, content_type: str) -> URLType:
        """Map platform and content type to URLType enum."""
        type_mapping = {
            ('youtube', 'video_pattern'): URLType.YOUTUBE_VIDEO,
            ('youtube', 'channel_pattern'): URLType.YOUTUBE_CHANNEL,
            ('youtube', 'playlist_pattern'): URLType.YOUTUBE_PLAYLIST,
            ('instagram', 'post_pattern'): URLType.INSTAGRAM_POST,
            ('instagram', 'profile_pattern'): URLType.INSTAGRAM_PROFILE,
            ('instagram', 'reel_pattern'): URLType.INSTAGRAM_REEL,
            ('tiktok', 'video_pattern'): URLType.TIKTOK_VIDEO,
            ('tiktok', 'profile_pattern'): URLType.TIKTOK_PROFILE,
            ('twitter', 'post_pattern'): URLType.TWITTER_POST,
            ('twitter', 'profile_pattern'): URLType.TWITTER_PROFILE,
            ('facebook', 'post_pattern'): URLType.FACEBOOK_POST,
            ('facebook', 'page_pattern'): URLType.FACEBOOK_PAGE,
            ('spotify', 'track_pattern'): URLType.SPOTIFY_TRACK,
            ('spotify', 'album_pattern'): URLType.SPOTIFY_ALBUM,
            ('spotify', 'artist_pattern'): URLType.SPOTIFY_ARTIST,
            ('spotify', 'playlist_pattern'): URLType.SPOTIFY_PLAYLIST,
            ('substack', 'post_pattern'): URLType.SUBSTACK_POST,
            ('substack', 'profile_pattern'): URLType.SUBSTACK_PROFILE,
        }
        
        return type_mapping.get((platform, content_type), URLType.GENERIC_WEB)
    
    async def _check_accessibility(self, url: str, timeout: int = 10) -> bool:
        """Check if URL is accessible."""
        try:
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=timeout)) as session:
                async with session.head(url) as response:
                    return 200 <= response.status < 400
        except Exception as e:
            logger.debug(f"Accessibility check failed for {url}: {e}")
            return False
    
    async def _extract_metadata(self, url: str) -> Dict:
        """Extract metadata from URL."""
        metadata = {}
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=aiohttp.ClientTimeout(total=15)) as response:
                    if response.status == 200:
                        html = await response.text()
                        metadata = self._parse_html_metadata(html)
                        
        except Exception as e:
            logger.debug(f"Metadata extraction failed for {url}: {e}")
        
        return metadata
    
    def _parse_html_metadata(self, html: str) -> Dict:
        """Parse HTML metadata using regex patterns."""
        metadata = {}
        
        try:
            # Title
            title_match = re.search(r'<title[^>]*>([^<]+)</title>', html, re.IGNORECASE)
            if title_match:
                metadata['title'] = title_match.group(1).strip()
            
            # Meta tags
            meta_patterns = {
                'description': r'<meta[^>]*name=["\']description["\'][^>]*content=["\']([^"\']+)["\']',
                'canonical_url': r'<link[^>]*rel=["\']canonical["\'][^>]*href=["\']([^"\']+)["\']',
                'author': r'<meta[^>]*name=["\']author["\'][^>]*content=["\']([^"\']+)["\']',
                'language': r'<meta[^>]*name=["\']language["\'][^>]*content=["\']([^"\']+)["\']',
            }
            
            for key, pattern in meta_patterns.items():
                match = re.search(pattern, html, re.IGNORECASE)
                if match:
                    metadata[key] = match.group(1).strip()
            
            # Open Graph tags
            og_patterns = {
                'og_title': r'<meta[^>]*property=["\']og:title["\'][^>]*content=["\']([^"\']+)["\']',
                'og_description': r'<meta[^>]*property=["\']og:description["\'][^>]*content=["\']([^"\']+)["\']',
                'og_image': r'<meta[^>]*property=["\']og:image["\'][^>]*content=["\']([^"\']+)["\']',
                'og_type': r'<meta[^>]*property=["\']og:type["\'][^>]*content=["\']([^"\']+)["\']',
            }
            
            for key, pattern in og_patterns.items():
                match = re.search(pattern, html, re.IGNORECASE)
                if match:
                    metadata[key] = match.group(1).strip()
            
            # Twitter Card tags
            twitter_patterns = {
                'twitter_title': r'<meta[^>]*name=["\']twitter:title["\'][^>]*content=["\']([^"\']+)["\']',
                'twitter_description': r'<meta[^>]*name=["\']twitter:description["\'][^>]*content=["\']([^"\']+)["\']',
                'twitter_image': r'<meta[^>]*name=["\']twitter:image["\'][^>]*content=["\']([^"\']+)["\']',
            }
            
            for key, pattern in twitter_patterns.items():
                match = re.search(pattern, html, re.IGNORECASE)
                if match:
                    metadata[key] = match.group(1).strip()
                    
        except Exception as e:
            logger.warning(f"HTML metadata parsing failed: {e}")
        
        return metadata
    
    def validate_batch_urls(self, urls: List[str]) -> List[URLValidationResult]:
        """Validate multiple URLs synchronously."""
        results = []
        
        for url in urls:
            try:
                # Basic validation without async operations
                validation_errors = []
                metadata = {}
                
                if not self._is_valid_url_structure(url):
                    validation_errors.append("Invalid URL structure")
                    result = URLValidationResult(
                        is_valid=False,
                        normalized_url=url,
                        url_type=URLType.UNKNOWN,
                        platform="unknown",
                        content_id=None,
                        metadata=metadata,
                        security_score=0.0,
                        validation_errors=validation_errors
                    )
                else:
                    normalized_url = self._normalize_url(url)
                    security_score = self._assess_security(normalized_url)
                    url_type, platform, content_id = self._detect_platform_and_type(normalized_url)
                    
                    if security_score < 0.5:
                        validation_errors.append("URL failed security assessment")
                    
                    is_valid = len(validation_errors) == 0 and security_score >= 0.5
                    
                    result = URLValidationResult(
                        is_valid=is_valid,
                        normalized_url=normalized_url,
                        url_type=url_type,
                        platform=platform,
                        content_id=content_id,
                        metadata=metadata,
                        security_score=security_score,
                        validation_errors=validation_errors
                    )
                
                results.append(result)
                
            except Exception as e:
                logger.error(f"Batch URL validation error for {url}: {e}")
                results.append(URLValidationResult(
                    is_valid=False,
                    normalized_url=url,
                    url_type=URLType.UNKNOWN,
                    platform="unknown",
                    content_id=None,
                    metadata={},
                    security_score=0.0,
                    validation_errors=[f"Validation exception: {str(e)}"]
                ))
        
        return results
    
    def get_platform_from_url(self, url: str) -> str:
        """Quick platform detection from URL."""
        try:
            for platform, patterns in self.platform_patterns.items():
                if re.search(patterns['domain_pattern'], url, re.IGNORECASE):
                    return platform
            return "unknown"
        except Exception:
            return "unknown"
    
    def extract_content_id(self, url: str, platform: str) -> Optional[str]:
        """Extract content ID for specific platform."""
        try:
            if platform not in self.platform_patterns:
                return None
            
            patterns = self.platform_patterns[platform]
            
            for content_type, pattern in patterns.items():
                if content_type == 'domain_pattern':
                    continue
                
                match = re.search(pattern, url, re.IGNORECASE)
                if match:
                    return match.group(1)
            
            return None
            
        except Exception as e:
            logger.warning(f"Content ID extraction failed: {e}")
            return None
    
    def is_supported_platform(self, url: str) -> bool:
        """Check if platform is supported for crawling."""
        platform = self.get_platform_from_url(url)
        return platform in self.platform_patterns
    
    def add_custom_pattern(self, platform: str, content_type: str, pattern: str) -> None:
        """Add custom URL pattern for platform."""
        if platform not in self.platform_patterns:
            self.platform_patterns[platform] = {}
        
        self.platform_patterns[platform][content_type] = pattern
    
    def update_security_rules(self, blocked_domains: Set[str], suspicious_patterns: List[str]) -> None:
        """Update security rules."""
        self.blocked_domains.update(blocked_domains)
        self.suspicious_patterns.extend(suspicious_patterns)

class URLNormalizer:
    """
    Advanced URL normalizer for consistent URL handling.
    
    Features:
    - Parameter cleanup
    - Canonical URL generation
    - Platform-specific normalization
    - Duplicate detection
    """
    
    @staticmethod
    def normalize_youtube_url(url: str) -> str:
        """Normalize YouTube URL."""
        try:
            # Extract video ID
            video_match = re.search(r'(?:v=|youtu\.be/)([a-zA-Z0-9_-]{11})', url)
            if video_match:
                video_id = video_match.group(1)
                return f"https://www.youtube.com/watch?v={video_id}"
            
            # Extract channel info
            channel_match = re.search(r'(?:channel/|user/|c/)([a-zA-Z0-9_-]+)', url)
            if channel_match:
                channel_id = channel_match.group(1)
                return f"https://www.youtube.com/channel/{channel_id}"
            
            return url
            
        except Exception:
            return url
    
    @staticmethod
    def normalize_instagram_url(url: str) -> str:
        """Normalize Instagram URL."""
        try:
            # Extract post ID
            post_match = re.search(r'/p/([a-zA-Z0-9_-]+)', url)
            if post_match:
                post_id = post_match.group(1)
                return f"https://www.instagram.com/p/{post_id}/"
            
            # Extract profile
            profile_match = re.search(r'instagram\.com/([a-zA-Z0-9_.]+)', url)
            if profile_match:
                username = profile_match.group(1)
                if username not in ['p', 'reel', 'tv']:
                    return f"https://www.instagram.com/{username}/"
            
            return url
            
        except Exception:
            return url
    
    @staticmethod
    def get_canonical_url(url: str, platform: str) -> str:
        """Get canonical URL for platform."""
        normalizers = {
            'youtube': URLNormalizer.normalize_youtube_url,
            'instagram': URLNormalizer.normalize_instagram_url,
        }
        
        normalizer = normalizers.get(platform)
        if normalizer:
            return normalizer(url)
        
        return url

# URL validation utilities
def quick_validate_url(url: str) -> bool:
    """Quick URL validation."""
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except Exception:
        return False

def extract_domain(url: str) -> str:
    """Extract domain from URL."""
    try:
        return urlparse(url).netloc.lower()
    except Exception:
        return ""

def is_same_domain(url1: str, url2: str) -> bool:
    """Check if two URLs are from same domain."""
    try:
        domain1 = extract_domain(url1)
        domain2 = extract_domain(url2)
        return domain1 == domain2
    except Exception:
        return False

def clean_url_parameters(url: str, keep_params: Optional[List[str]] = None) -> str:
    """Clean URL parameters keeping only specified ones."""
    try:
        parsed = urlparse(url)
        if not keep_params:
            return f"{parsed.scheme}://{parsed.netloc}{parsed.path}"
        
        query_params = parse_qs(parsed.query)
        clean_params = {}
        
        for param in keep_params:
            if param in query_params:
                clean_params[param] = query_params[param]
        
        if clean_params:
            query_parts = []
            for param, values in clean_params.items():
                for value in values:
                    query_parts.append(f"{param}={quote(value)}")
            query_string = '&'.join(query_parts)
            return f"{parsed.scheme}://{parsed.netloc}{parsed.path}?{query_string}"
        
        return f"{parsed.scheme}://{parsed.netloc}{parsed.path}"
        
    except Exception:
        return url
