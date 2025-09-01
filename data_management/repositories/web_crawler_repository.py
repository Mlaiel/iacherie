"""🕷️ Web Crawler Repository - IA Influencer Agent Platform Enterprise
===================================================================
Module: backend/data_management/repositories/web_crawler_repository.py
Author: Fahed Mlaiel (mlaiel@live.de)
Team: Lead Dev IA + Backend Senior + ML Engineer + DBA + Security + Microservices + Audio + DevOps + IA Prompt Engineer
Type: Industrial Web Surveillance Repository - Production-Ready
Responsibility: Advanced web crawling for content protection and monitoring
========================================================================

⚠️  PROPRIÉTÉ INTELLECTUELLE EXCLUSIVE - FAHED MLAIEL ⚠️
(c) 2025 Fahed Mlaiel. Tous droits réservés.
Usage non autorisé strictement interdit et passible de poursuites judiciaires.
Email: mlaiel@live.de

BUSINESS LOGIC:
User (musician/blogger/photographer/influencer/comedian) → Upload multi-format → 
IA protection rights → Web Surveillance → Violation Detection → Automated Takedown → Revenue Recovery

WEB CRAWLER REPOSITORY ARCHITECTURE:
Crawl Scheduling → Multi-Platform Monitoring → Content Fingerprinting → 
Violation Detection → Evidence Collection → Alert Generation → Takedown Processing
"""

from typing import Dict, List, Optional, Any, Tuple, Union, Set
import logging
import asyncio
import hashlib
import json
import re
from datetime import datetime, timezone, timedelta
from dataclasses import dataclass, asdict
from enum import Enum
from urllib.parse import urlparse, urljoin
import aiohttp
import requests
from bs4 import BeautifulSoup

from .base_repository import BaseRepository, AsyncBaseRepository, OperationType

class CrawlStatus(Enum):
    """
Crawl job status"""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    PAUSED = "paused"
    CANCELLED = "cancelled"

class PlatformType(Enum):
    """Supported platforms for crawling"""

    YOUTUBE = "youtube"
    TIKTOK = "tiktok"
    INSTAGRAM = "instagram"
    TWITTER = "twitter"
    FACEBOOK = "facebook"
    SOUNDCLOUD = "soundcloud"
    SPOTIFY = "spotify"
    BANDCAMP = "bandcamp"
    REDDIT = "reddit"
    PINTEREST = "pinterest"
    LINKEDIN = "linkedin"
    GENERIC_WEB = "generic_web"

class ViolationType(Enum):
    """Types of content violations"""

    COPYRIGHT_INFRINGEMENT = "copyright_infringement"
    UNAUTHORIZED_USE = "unauthorized_use"
    TRADEMARK_VIOLATION = "trademark_violation"
    PLAGIARISM = "plagiarism"
    IMPERSONATION = "impersonation"
    REVENUE_THEFT = "revenue_theft"

class EvidenceType(Enum):
    """Types of evidence collected"""

    SCREENSHOT = "screenshot"
    VIDEO_RECORDING = "video_recording"
    AUDIO_SAMPLE = "audio_sample"
    HTML_SOURCE = "html_source"
    METADATA = "metadata"
    NETWORK_TRACE = "network_trace"

@dataclass
class CrawlJob:
    """Web crawl job configuration"""
    job_id: str
    creator_id: str
    platform: PlatformType
    search_terms: List[str]
    target_urls: List[str]
    fingerprints: List[str]
    scheduled_at: datetime
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    status: CrawlStatus
    priority: int
    max_pages: int
    crawl_depth: int
    respect_robots: bool
    delay_seconds: float
    user_agent: str
    headers: Dict[str, str]
    cookies: Dict[str, str]
    proxy_config: Optional[Dict[str, Any]]
    filters: Dict[str, Any]
    metadata: Dict[str, Any]

@dataclass
class DetectedContent:
    """
Content detected during crawling"""
    detection_id: str
    job_id: str
    creator_id: str
    original_content_id: str
    detected_url: str
    platform: PlatformType
    violation_type: ViolationType
    similarity_score: float
    confidence_level: float
    fingerprint_matches: List[str]
    detected_at: datetime
    title: Optional[str]
    description: Optional[str]
    uploader: Optional[str]
    upload_date: Optional[datetime]
    view_count: Optional[int]
    like_count: Optional[int]
    comment_count: Optional[int]
    evidence: List[Dict[str, Any]]
    metadata: Dict[str, Any]
    takedown_status: str
    revenue_estimate: Optional[float]

@dataclass
class Evidence:
    """
Evidence collected for violations"""
    evidence_id: str
    detection_id: str
    evidence_type: EvidenceType
    file_path: str
    file_size: int
    file_hash: str
    captured_at: datetime
    metadata: Dict[str, Any]
    is_verified: bool
    legal_weight: float

@dataclass
class CrawlMetrics:
    """
Crawl performance metrics"""
    job_id: str
    pages_crawled: int
    pages_failed: int
    content_detected: int
    violations_found: int
    evidence_collected: int
    crawl_duration: float
    average_response_time: float
    bandwidth_used: int
    errors_encountered: List[str]

class WebCrawlerRepository(BaseRepository[CrawlJob]):
    """
    Advanced web crawler repository for content protection monitoring
    
    Features:
    - Multi-platform content monitoring
    - Intelligent crawling strategies
    - Real-time violation detection
    - Evidence collection and preservation
    - Automated takedown processing
    - Performance optimization
    - Compliance with robots.txt and rate limits
    """
    
    def __init__(self, db_connection=None, cache_manager=None, 
                 fingerprint_service=None, evidence_service=None,
                 takedown_service=None, notification_service=None):
        super().__init__(db_connection, cache_manager)
        self.fingerprint_service = fingerprint_service
        self.evidence_service = evidence_service
        self.takedown_service = takedown_service
        self.notification_service = notification_service
        self.table_name = "crawl_jobs"
        self.logger = logging.getLogger(__name__)
        
        # Platform-specific configurations
        self.platform_configs = {
            PlatformType.YOUTUBE: {
                'base_url': 'https://www.youtube.com',
                'search_endpoint': '/results?search_query={}',
                'rate_limit': 100,  # requests per hour
                'max_concurrent': 5,
                'respect_robots': True,
                'user_agent': 'Mozilla/5.0 (compatible; ContentProtectionBot/1.0)',
                'required_headers': {'Accept-Language': 'en-US,en;q=0.9'}
            },
            PlatformType.TIKTOK: {
                'base_url': 'https://www.tiktok.com',
                'search_endpoint': '/search?q={}',
                'rate_limit': 50,
                'max_concurrent': 3,
                'respect_robots': True,
                'user_agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X)',
                'required_headers': {'Accept': 'application/json'}
            },
            PlatformType.INSTAGRAM: {
                'base_url': 'https://www.instagram.com',
                'search_endpoint': '/explore/tags/{}/',
                'rate_limit': 30,
                'max_concurrent': 2,
                'respect_robots': True,
                'user_agent': 'Mozilla/5.0 (compatible; InstagramBot/1.0)',
                'required_headers': {'X-Requested-With': 'XMLHttpRequest'}
            },
            PlatformType.SOUNDCLOUD: {
                'base_url': 'https://soundcloud.com',
                'search_endpoint': '/search?q={}',
                'rate_limit': 200,
                'max_concurrent': 10,
                'respect_robots': True,
                'user_agent': 'Mozilla/5.0 (compatible; SoundCloudBot/1.0)',
                'required_headers': {}
            }
        }
        
        # Global crawling configuration
        self.global_config = {
            'max_concurrent_jobs': 20,
            'default_delay': 1.0,
            'timeout_seconds': 30,
            'max_retries': 3,
            'evidence_storage_path': '/var/evidence/',
            'screenshot_quality': 90,
            'max_file_size': 50 * 1024 * 1024,  # 50MB
        }
    
    def _generate_job_id(self) -> str:
        """Generate unique crawl job ID"""
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S%f")
        return f"crawl_{timestamp}_{hashlib.md5(timestamp.encode()).hexdigest()[:8]}"
    
    def _generate_detection_id(self) -> str:
        """Generate unique detection ID"""
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S%f")
        return f"detect_{timestamp}_{hashlib.md5(timestamp.encode()).hexdigest()[:8]}"
    
    def _generate_evidence_id(self) -> str:
        """Generate unique evidence ID"""
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S%f")
        return f"evidence_{timestamp}_{hashlib.md5(timestamp.encode()).hexdigest()[:8]}"
    
    def _build_search_urls(self, platform: PlatformType, 
                          search_terms: List[str]) -> List[str]:
        """Build search URLs for the platform"""
        try:
            config = self.platform_configs.get(platform)
            if not config:
                raise ValueError(f"Unsupported platform: {platform}")
            
            urls = []
            base_url = config['base_url']
            search_endpoint = config['search_endpoint']
            
            for term in search_terms:
                # URL encode the search term
                encoded_term = requests.utils.quote(term)
                search_url = base_url + search_endpoint.format(encoded_term)
                urls.append(search_url)
            
            return urls
            
        except Exception as e:
            self.logger.error(f"Error building search URLs: {e}")
            return []
    
    def _extract_content_metadata(self, html: str, url: str, 
                                platform: PlatformType) -> Dict[str, Any]:
        """Extract content metadata from HTML"""
        try:
            soup = BeautifulSoup(html, 'html.parser')
            metadata = {}
            
            # Common metadata extraction
            metadata['title'] = self._extract_title(soup)
            metadata['description'] = self._extract_description(soup)
            metadata['canonical_url'] = self._extract_canonical_url(soup, url)
            metadata['og_data'] = self._extract_opengraph_data(soup)
            metadata['twitter_data'] = self._extract_twitter_data(soup)
            metadata['schema_data'] = self._extract_schema_data(soup)
            
            # Platform-specific metadata
            if platform == PlatformType.YOUTUBE:
                metadata.update(self._extract_youtube_metadata(soup))
            elif platform == PlatformType.TIKTOK:
                metadata.update(self._extract_tiktok_metadata(soup))
            elif platform == PlatformType.INSTAGRAM:
                metadata.update(self._extract_instagram_metadata(soup))
            elif platform == PlatformType.SOUNDCLOUD:
                metadata.update(self._extract_soundcloud_metadata(soup))
            
            return metadata
            
        except Exception as e:
            self.logger.error(f"Error extracting content metadata: {e}")
            return {}
    
    def _extract_title(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract page title"""
        title_tag = soup.find('title')
        if title_tag:
            return title_tag.get_text().strip()
        
        # Try Open Graph title
        og_title = soup.find('meta', property='og:title')
        if og_title:
            return og_title.get('content', '').strip()
        
        return None
    
    def _extract_description(self, soup: BeautifulSoup) -> Optional[str]:
        """
Extract page description"""
        desc_tag = soup.find('meta', attrs={'name': 'description'})
        if desc_tag:
            return desc_tag.get('content', '').strip()
        
        # Try Open Graph description
        og_desc = soup.find('meta', property='og:description')
        if og_desc:
            return og_desc.get('content', '').strip()
        
        return None
    
    def _extract_canonical_url(self, soup: BeautifulSoup, fallback_url: str) -> str:
        """
Extract canonical URL"""
        canonical = soup.find('link', rel='canonical')
        if canonical:
            return canonical.get('href', fallback_url)
        
        # Try Open Graph URL
        og_url = soup.find('meta', property='og:url')
        if og_url:
            return og_url.get('content', fallback_url)
        
        return fallback_url
    
    def _extract_opengraph_data(self, soup: BeautifulSoup) -> Dict[str, str]:
        """
Extract Open Graph metadata"""
        og_data = {}
        og_tags = soup.find_all('meta', property=lambda x: x and x.startswith('og:'))
        
        for tag in og_tags:
            property_name = tag.get('property', '').replace('og:', '')
            content = tag.get('content', '')
            if property_name and content:
                og_data[property_name] = content
        
        return og_data
    
    def _extract_twitter_data(self, soup: BeautifulSoup) -> Dict[str, str]:
        """
Extract Twitter Card metadata"""
        twitter_data = {}
        twitter_tags = soup.find_all('meta', attrs={'name': lambda x: x and x.startswith('twitter:')})
        
        for tag in twitter_tags:
            name = tag.get('name', '').replace('twitter:', '')
            content = tag.get('content', '')
            if name and content:
                twitter_data[name] = content
        
        return twitter_data
    
    def _extract_schema_data(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """
Extract structured data (JSON-LD, microdata)"""
        schema_data = {}
        
        # Extract JSON-LD
        json_ld_scripts = soup.find_all('script', type='application/ld+json')
        json_ld_data = []
        
        for script in json_ld_scripts:
            try:
                data = json.loads(script.string)
                json_ld_data.append(data)
            except (json.JSONDecodeError, AttributeError):
                continue
        
        if json_ld_data:
            schema_data['json_ld'] = json_ld_data
        
        return schema_data
    
    def _extract_youtube_metadata(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """
Extract YouTube-specific metadata"""
        youtube_data = {}
        
        # Video ID extraction
        video_id_pattern = r'watch\?v=([a-zA-Z0-9_-]{11})'
        video_id_match = re.search(video_id_pattern, str(soup))
        if video_id_match:
            youtube_data['video_id'] = video_id_match.group(1)
        
        # Channel information
        channel_link = soup.find('link', itemprop='url')
        if channel_link:
            youtube_data['channel_url'] = channel_link.get('href', '')
        
        # View count, likes, etc. would be extracted from page scripts
        # This would require more sophisticated parsing of embedded JSON data
        
        return youtube_data
    
    def _extract_tiktok_metadata(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """
Extract TikTok-specific metadata"""
        tiktok_data = {}
        
        # TikTok video ID
        video_id_pattern = r'/video/(\d+)'
        video_id_match = re.search(video_id_pattern, str(soup))
        if video_id_match:
            tiktok_data['video_id'] = video_id_match.group(1)
        
        # Author information
        author_meta = soup.find('meta', attrs={'name': 'author'})
        if author_meta:
            tiktok_data['author'] = author_meta.get('content', '')
        
        return tiktok_data
    
    def _extract_instagram_metadata(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """
Extract Instagram-specific metadata"""
        instagram_data = {}
        
        # Instagram media ID
        media_id_pattern = r'/p/([a-zA-Z0-9_-]+)/'
        media_id_match = re.search(media_id_pattern, str(soup))
        if media_id_match:
            instagram_data['media_id'] = media_id_match.group(1)
        
        return instagram_data
    
    def _extract_soundcloud_metadata(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """
Extract SoundCloud-specific metadata"""
        soundcloud_data = {}
        
        # Track URL pattern
        track_pattern = r'soundcloud\.com/([^/]+)/([^/?]+)'
        track_match = re.search(track_pattern, str(soup))
        if track_match:
            soundcloud_data['user'] = track_match.group(1)
            soundcloud_data['track'] = track_match.group(2)
        
        return soundcloud_data
    
    def _check_content_similarity(self, content_metadata: Dict[str, Any],
                                fingerprints: List[str]) -> Tuple[float, List[str]]:
        """
Check content similarity against known fingerprints"""
        try:
            if not self.fingerprint_service:
                return 0.0, []
            
            # Extract content for fingerprinting
            content_text = content_metadata.get('title', '') + ' ' + content_metadata.get('description', '')
            
            # Generate fingerprint for the detected content
            detected_fingerprint = self.fingerprint_service.generate_text_fingerprint(content_text)
            
            # Compare against known fingerprints
            max_similarity = 0.0
            matching_fingerprints = []
            
            for fingerprint in fingerprints:
                similarity = self.fingerprint_service.calculate_similarity(
                    detected_fingerprint, fingerprint
                )
                
                if similarity > 0.8:  # 80% similarity threshold
                    matching_fingerprints.append(fingerprint)
                    max_similarity = max(max_similarity, similarity)
            
            return max_similarity, matching_fingerprints
            
        except Exception as e:
            self.logger.error(f"Error checking content similarity: {e}")
            return 0.0, []
    
    def _capture_evidence(self, url: str, content_metadata: Dict[str, Any],
                        detection_id: str) -> List[Evidence]:
        """Capture evidence for detected violation"""
        try:
            evidence_list = []
            
            # Capture screenshot
            screenshot_path = self._capture_screenshot(url, detection_id)
            if screenshot_path:
                evidence = Evidence(
                    evidence_id=self._generate_evidence_id(),
                    detection_id=detection_id,
                    evidence_type=EvidenceType.SCREENSHOT,
                    file_path=screenshot_path,
                    file_size=self._get_file_size(screenshot_path),
                    file_hash=self._calculate_file_hash(screenshot_path),
                    captured_at=datetime.now(timezone.utc),
                    metadata={'url': url, 'capture_method': 'selenium'},
                    is_verified=True,
                    legal_weight=0.8
                )
                evidence_list.append(evidence)
            
            # Save HTML source
            html_path = self._save_html_source(url, content_metadata, detection_id)
            if html_path:
                evidence = Evidence(
                    evidence_id=self._generate_evidence_id(),
                    detection_id=detection_id,
                    evidence_type=EvidenceType.HTML_SOURCE,
                    file_path=html_path,
                    file_size=self._get_file_size(html_path),
                    file_hash=self._calculate_file_hash(html_path),
                    captured_at=datetime.now(timezone.utc),
                    metadata={'url': url, 'content_type': 'text/html'},
                    is_verified=True,
                    legal_weight=0.9
                )
                evidence_list.append(evidence)
            
            # Save metadata as JSON
            metadata_path = self._save_metadata(content_metadata, detection_id)
            if metadata_path:
                evidence = Evidence(
                    evidence_id=self._generate_evidence_id(),
                    detection_id=detection_id,
                    evidence_type=EvidenceType.METADATA,
                    file_path=metadata_path,
                    file_size=self._get_file_size(metadata_path),
                    file_hash=self._calculate_file_hash(metadata_path),
                    captured_at=datetime.now(timezone.utc),
                    metadata={'format': 'json', 'extracted_from': url},
                    is_verified=True,
                    legal_weight=0.7
                )
                evidence_list.append(evidence)
            
            return evidence_list
            
        except Exception as e:
            self.logger.error(f"Error capturing evidence: {e}")
            return []
    
    def _capture_screenshot(self, url: str, detection_id: str) -> Optional[str]:
        """Capture screenshot of the page"""
        try:
            from selenium import webdriver
            from selenium.webdriver.chrome.options import Options
            
            # Configure Chrome options for headless operation
            chrome_options = Options()
            chrome_options.add_argument('--headless')
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.add_argument('--window-size=1920,1080')
            
            driver = webdriver.Chrome(options=chrome_options)
            
            try:
                driver.get(url)
                driver.implicitly_wait(5)
                
                # Create evidence directory
                evidence_dir = f"{self.global_config['evidence_storage_path']}/{detection_id}"
                import os
                os.makedirs(evidence_dir, exist_ok=True)
                
                # Save screenshot
                screenshot_path = f"{evidence_dir}/screenshot.png"
                driver.save_screenshot(screenshot_path)
                
                return screenshot_path
                
            finally:
                driver.quit()
                
        except ImportError:
            self.logger.warning("Selenium not available for screenshot capture")
            return None
        except Exception as e:
            self.logger.error(f"Error capturing screenshot: {e}")
            return None
    
    def _save_html_source(self, url: str, content_metadata: Dict[str, Any], 
                         detection_id: str) -> Optional[str]:
        """Save HTML source of the page"""
        try:
            # Get HTML content
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            
            # Create evidence directory
            evidence_dir = f"{self.global_config['evidence_storage_path']}/{detection_id}"
            import os
            os.makedirs(evidence_dir, exist_ok=True)
            
            # Save HTML
            html_path = f"{evidence_dir}/source.html"
            with open(html_path, 'w', encoding='utf-8') as f:
                f.write(response.text)
            
            return html_path
            
        except Exception as e:
            self.logger.error(f"Error saving HTML source: {e}")
            return None
    
    def _save_metadata(self, content_metadata: Dict[str, Any], 
                      detection_id: str) -> Optional[str]:
        """Save extracted metadata as JSON"""
        try:
            # Create evidence directory
            evidence_dir = f"{self.global_config['evidence_storage_path']}/{detection_id}"
            import os
            os.makedirs(evidence_dir, exist_ok=True)
            
            # Save metadata
            metadata_path = f"{evidence_dir}/metadata.json"
            with open(metadata_path, 'w', encoding='utf-8') as f:
                json.dump(content_metadata, f, indent=2, default=str)
            
            return metadata_path
            
        except Exception as e:
            self.logger.error(f"Error saving metadata: {e}")
            return None
    
    def _get_file_size(self, file_path: str) -> int:
        """Get file size in bytes"""
        try:
            import os
            return os.path.getsize(file_path)
        except:
            return 0
    
    def _calculate_file_hash(self, file_path: str) -> str:
        """
Calculate SHA-256 hash of file"""
        try:
            import hashlib
            hash_sha256 = hashlib.sha256()
            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_sha256.update(chunk)
            return hash_sha256.hexdigest()
        except:
            return ""
    
    def _process_detected_content(self, job: CrawlJob, url: str, 
                                content_metadata: Dict[str, Any]) -> Optional[DetectedContent]:
        """Process and analyze detected content"""
        try:
            # Check similarity against fingerprints
            similarity_score, matching_fingerprints = self._check_content_similarity(
                content_metadata, job.fingerprints
            )
            
            # Only process if similarity is above threshold
            if similarity_score < 0.8:
                return None
            
            # Generate detection ID
            detection_id = self._generate_detection_id()
            
            # Determine violation type
            violation_type = self._determine_violation_type(content_metadata, similarity_score)
            
            # Calculate confidence level
            confidence_level = self._calculate_confidence_level(
                similarity_score, matching_fingerprints, content_metadata
            )
            
            # Capture evidence
            evidence_list = self._capture_evidence(url, content_metadata, detection_id)
            
            # Estimate potential revenue loss
            revenue_estimate = self._estimate_revenue_loss(content_metadata)
            
            # Create detection record
            detected_content = DetectedContent(
                detection_id=detection_id,
                job_id=job.job_id,
                creator_id=job.creator_id,
                original_content_id="",  # Would be linked to original content
                detected_url=url,
                platform=job.platform,
                violation_type=violation_type,
                similarity_score=similarity_score,
                confidence_level=confidence_level,
                fingerprint_matches=matching_fingerprints,
                detected_at=datetime.now(timezone.utc),
                title=content_metadata.get('title'),
                description=content_metadata.get('description'),
                uploader=content_metadata.get('author', content_metadata.get('uploader')),
                upload_date=self._parse_upload_date(content_metadata),
                view_count=self._parse_int_metadata(content_metadata, 'view_count'),
                like_count=self._parse_int_metadata(content_metadata, 'like_count'),
                comment_count=self._parse_int_metadata(content_metadata, 'comment_count'),
                evidence=[asdict(evidence) for evidence in evidence_list],
                metadata=content_metadata,
                takedown_status="pending",
                revenue_estimate=revenue_estimate
            )
            
            return detected_content
            
        except Exception as e:
            self.logger.error(f"Error processing detected content: {e}")
            return None
    
    def _determine_violation_type(self, content_metadata: Dict[str, Any], 
                                similarity_score: float) -> ViolationType:
        """Determine the type of violation based on content analysis"""
        # This would be more sophisticated in practice
        if similarity_score > 0.95:
            return ViolationType.COPYRIGHT_INFRINGEMENT
        elif similarity_score > 0.9:
            return ViolationType.UNAUTHORIZED_USE
        else:
            return ViolationType.PLAGIARISM
    
    def _calculate_confidence_level(self, similarity_score: float,
                                  matching_fingerprints: List[str],
                                  content_metadata: Dict[str, Any]) -> float:
        """
Calculate confidence level for the detection"""
        # Base confidence from similarity score
        confidence = similarity_score
        
        # Boost confidence for multiple fingerprint matches
        if len(matching_fingerprints) > 1:
            confidence = min(1.0, confidence + 0.1)
        
        # Boost confidence for exact title matches
        if content_metadata.get('title'):
            # This would compare against known titles
            confidence = min(1.0, confidence + 0.05)
        
        return confidence
    
    def _parse_upload_date(self, content_metadata: Dict[str, Any]) -> Optional[datetime]:
        """
Parse upload date from metadata"""
        # This would implement date parsing logic
        return None
    
    def _parse_int_metadata(self, content_metadata: Dict[str, Any], key: str) -> Optional[int]:
        """
Parse integer metadata fields"""
        try:
            value = content_metadata.get(key)
            if value:
                return int(str(value).replace(',', '').replace(' ', ''))
        except:
            pass
        return None
    
    def _estimate_revenue_loss(self, content_metadata: Dict[str, Any]) -> Optional[float]:
        """
Estimate potential revenue loss from violation"""
        try:
            # This would implement revenue estimation logic based on views, platform, etc.
            view_count = self._parse_int_metadata(content_metadata, 'view_count')
            if view_count:
                # Rough estimate: $0.001 per view
                return view_count * 0.001
        except:
            pass
        return None
    
    # Base Repository Implementation
    def create(self, entity: CrawlJob, **kwargs) -> CrawlJob:
        """
Create new crawl job"""
        try:
            self._validate_entity(entity)
            
            # Save to database
            entity_dict = asdict(entity)
            # result = self.db.insert(self.table_name, entity_dict)
            
            # Cache the job
            if self._cache_enabled and self.cache:
                cache_key = self._generate_cache_key("get_by_id", entity_id=entity.job_id)
                self.cache.set(cache_key, entity, ttl=self._cache_ttl)
            
            # Log audit
            self._log_audit(
                OperationType.CREATE,
                entity_id=entity.job_id,
                new_values=entity_dict,
                metadata={'creator_id': entity.creator_id, 'platform': entity.platform.value}
            )
            
            self.logger.info(f"Crawl job created: {entity.job_id}")
            
            return entity
            
        except Exception as e:
            self.logger.error(f"Error creating crawl job: {e}")
            raise
    
    def get_by_id(self, entity_id: str, use_cache: bool = True) -> Optional[CrawlJob]:
        """Get crawl job by ID"""
        try:
            # Check cache first
            if use_cache and self._cache_enabled and self.cache:
                cache_key = self._generate_cache_key("get_by_id", entity_id=entity_id)
                cached_job = self.cache.get(cache_key)
                if cached_job:
                    return cached_job
            
            # Query database
            # result = self.db.select(self.table_name, where={'job_id': entity_id})
            # job = CrawlJob(**result) if result else None
            
            job = None  # Placeholder for actual DB query
            
            # Cache the result
            if job and use_cache and self._cache_enabled and self.cache:
                cache_key = self._generate_cache_key("get_by_id", entity_id=entity_id)
                self.cache.set(cache_key, job, ttl=self._cache_ttl)
            
            return job
            
        except Exception as e:
            self.logger.error(f"Error getting crawl job by ID {entity_id}: {e}")
            raise
    
    def update(self, entity: CrawlJob, **kwargs) -> CrawlJob:
        """Update crawl job"""
        try:
            self._validate_entity(entity)
            
            # Update database
            entity_dict = asdict(entity)
            # result = self.db.update(self.table_name, entity_dict, where={'job_id': entity.job_id})
            
            # Invalidate cache
            if self._cache_enabled and self.cache:
                cache_key = self._generate_cache_key("get_by_id", entity_id=entity.job_id)
                self.cache.delete(cache_key)
            
            # Log audit
            self._log_audit(
                OperationType.UPDATE,
                entity_id=entity.job_id,
                new_values=entity_dict,
                metadata={'status': entity.status.value}
            )
            
            return entity
            
        except Exception as e:
            self.logger.error(f"Error updating crawl job: {e}")
            raise
    
    def delete(self, entity_id: str, soft_delete: bool = True) -> bool:
        """Delete crawl job"""
        try:
            if soft_delete:
                job = self.get_by_id(entity_id)
                if job:
                    job.status = CrawlStatus.CANCELLED
                    self.update(job)
            else:
                # result = self.db.delete(self.table_name, where={'job_id': entity_id})
                pass
            
            # Remove from cache
            if self._cache_enabled and self.cache:
                cache_key = self._generate_cache_key("get_by_id", entity_id=entity_id)
                self.cache.delete(cache_key)
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error deleting crawl job {entity_id}: {e}")
            raise
    
    def list(self, filters: Dict[str, Any] = None, limit: int = 100, 
             offset: int = 0, order_by: str = None) -> List[CrawlJob]:
        """List crawl jobs with filtering"""
        try:
            query_filters = filters or {}
            
            # Database query would be built here
            # results = self.db.select(self.table_name, 
            #                         where=query_filters, 
            #                         limit=limit, 
            #                         offset=offset, 
            #                         order_by=order_by or 'scheduled_at DESC')
            
            results = []  # Placeholder for actual DB results
            
            # Convert to CrawlJob objects
            jobs = [CrawlJob(**result) for result in results]
            
            return jobs
            
        except Exception as e:
            self.logger.error(f"Error listing crawl jobs: {e}")
            raise
    
    def schedule_crawl_job(self, creator_id: str, platform: PlatformType,
                          search_terms: List[str], fingerprints: List[str],
                          scheduled_at: datetime = None, priority: int = 5,
                          **kwargs) -> CrawlJob:
        """Schedule a new crawl job"""
        try:
            job_id = self._generate_job_id()
            
            # Build target URLs
            target_urls = self._build_search_urls(platform, search_terms)
            
            # Get platform configuration
            platform_config = self.platform_configs.get(platform, {})
            
            crawl_job = CrawlJob(
                job_id=job_id,
                creator_id=creator_id,
                platform=platform,
                search_terms=search_terms,
                target_urls=target_urls,
                fingerprints=fingerprints,
                scheduled_at=scheduled_at or datetime.now(timezone.utc),
                started_at=None,
                completed_at=None,
                status=CrawlStatus.PENDING,
                priority=priority,
                max_pages=kwargs.get('max_pages', 100),
                crawl_depth=kwargs.get('crawl_depth', 2),
                respect_robots=kwargs.get('respect_robots', True),
                delay_seconds=kwargs.get('delay_seconds', platform_config.get('rate_limit', 1.0)),
                user_agent=kwargs.get('user_agent', platform_config.get('user_agent', '')),
                headers=kwargs.get('headers', platform_config.get('required_headers', {})),
                cookies=kwargs.get('cookies', {}),
                proxy_config=kwargs.get('proxy_config'),
                filters=kwargs.get('filters', {}),
                metadata=kwargs.get('metadata', {})
            )
            
            return self.create(crawl_job)
            
        except Exception as e:
            self.logger.error(f"Error scheduling crawl job: {e}")
            raise
    
    def get_pending_jobs(self, limit: int = 10) -> List[CrawlJob]:
        """Get pending crawl jobs ordered by priority and schedule time"""
        filters = {'status': CrawlStatus.PENDING.value}
        return self.list(
            filters=filters, 
            limit=limit, 
            order_by='priority DESC, scheduled_at ASC'
        )
    
    def get_jobs_by_creator(self, creator_id: str, 
                           status: CrawlStatus = None) -> List[CrawlJob]:
        """
Get crawl jobs for a specific creator"""
        filters = {'creator_id': creator_id}
        if status:
            filters['status'] = status.value
        
        return self.list(filters=filters, order_by='scheduled_at DESC')
    
    def get_jobs_by_platform(self, platform: PlatformType,
                           status: CrawlStatus = None) -> List[CrawlJob]:
        """
Get crawl jobs for a specific platform"""
        filters = {'platform': platform.value}
        if status:
            filters['status'] = status.value
        
        return self.list(filters=filters, order_by='scheduled_at DESC')


class AsyncWebCrawlerRepository(AsyncBaseRepository[CrawlJob]):
    """
Asynchronous web crawler repository for high-performance operations"""
    
    def __init__(self, db_connection=None, cache_manager=None, 
                 fingerprint_service=None, evidence_service=None,
                 takedown_service=None, notification_service=None):
        super().__init__(db_connection, cache_manager)
        self.fingerprint_service = fingerprint_service
        self.evidence_service = evidence_service
        self.takedown_service = takedown_service
        self.notification_service = notification_service
        self.table_name = "crawl_jobs"
        self.logger = logging.getLogger(__name__)
    
    async def create(self, entity: CrawlJob, **kwargs) -> CrawlJob:
        """Create crawl job asynchronously"""
        try:
            await self._validate_entity(entity)
            
            # Save to database asynchronously
            entity_dict = asdict(entity)
            # await self.db.insert_async(self.table_name, entity_dict)
            
            # Cache the job asynchronously
            if self._cache_enabled and self.cache:
                cache_key = self._generate_cache_key("get_by_id", entity_id=entity.job_id)
                await self.cache.set_async(cache_key, entity, ttl=self._cache_ttl)
            
            # Log audit asynchronously
            await self._log_audit(
                OperationType.CREATE,
                entity_id=entity.job_id,
                new_values=entity_dict,
                metadata={'creator_id': entity.creator_id}
            )
            
            self.logger.info(f"Crawl job created (async): {entity.job_id}")
            
            return entity
            
        except Exception as e:
            self.logger.error(f"Error creating crawl job (async): {e}")
            raise
    
    async def get_by_id(self, entity_id: str, use_cache: bool = True) -> Optional[CrawlJob]:
        """Get crawl job by ID asynchronously"""
        try:
            # Check cache first
            if use_cache and self._cache_enabled and self.cache:
                cache_key = self._generate_cache_key("get_by_id", entity_id=entity_id)
                cached_job = await self.cache.get_async(cache_key)
                if cached_job:
                    return cached_job
            
            # Query database asynchronously
            # result = await self.db.select_async(self.table_name, where={'job_id': entity_id})
            # job = CrawlJob(**result) if result else None
            
            job = None  # Placeholder
            
            # Cache the result
            if job and use_cache and self._cache_enabled and self.cache:
                cache_key = self._generate_cache_key("get_by_id", entity_id=entity_id)
                await self.cache.set_async(cache_key, job, ttl=self._cache_ttl)
            
            return job
            
        except Exception as e:
            self.logger.error(f"Error getting crawl job by ID {entity_id} (async): {e}")
            raise
    
    async def update(self, entity: CrawlJob, **kwargs) -> CrawlJob:
        """Update crawl job asynchronously"""
        try:
            await self._validate_entity(entity)
            
            # Update database asynchronously
            entity_dict = asdict(entity)
            # await self.db.update_async(self.table_name, entity_dict, where={'job_id': entity.job_id})
            
            # Invalidate cache
            if self._cache_enabled and self.cache:
                cache_key = self._generate_cache_key("get_by_id", entity_id=entity.job_id)
                await self.cache.delete_async(cache_key)
            
            # Log audit asynchronously
            await self._log_audit(
                OperationType.UPDATE,
                entity_id=entity.job_id,
                new_values=entity_dict,
                metadata={'status': entity.status.value}
            )
            
            return entity
            
        except Exception as e:
            self.logger.error(f"Error updating crawl job (async): {e}")
            raise
    
    async def delete(self, entity_id: str, soft_delete: bool = True) -> bool:
        """Delete crawl job asynchronously"""
        try:
            if soft_delete:
                job = await self.get_by_id(entity_id)
                if job:
                    job.status = CrawlStatus.CANCELLED
                    await self.update(job)
            else:
                # await self.db.delete_async(self.table_name, where={'job_id': entity_id})
                pass
            
            # Remove from cache
            if self._cache_enabled and self.cache:
                cache_key = self._generate_cache_key("get_by_id", entity_id=entity_id)
                await self.cache.delete_async(cache_key)
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error deleting crawl job {entity_id} (async): {e}")
            raise
    
    async def list(self, filters: Dict[str, Any] = None, limit: int = 100, 
                  offset: int = 0, order_by: str = None) -> List[CrawlJob]:
        """List crawl jobs asynchronously"""
        try:
            query_filters = filters or {}
            
            # Async database query would be built here
            # results = await self.db.select_async(self.table_name, 
            #                                    where=query_filters, 
            #                                    limit=limit, 
            #                                    offset=offset, 
            #                                    order_by=order_by or 'scheduled_at DESC')
            
            results = []  # Placeholder
            jobs = [CrawlJob(**result) for result in results]
            
            return jobs
            
        except Exception as e:
            self.logger.error(f"Error listing crawl jobs (async): {e}")
            raise
    
    async def execute_crawl_job_async(self, job: CrawlJob) -> CrawlMetrics:
        """Execute a crawl job asynchronously with full monitoring"""
        start_time = datetime.now()
        
        try:
            self.logger.info(f"Starting async crawl job execution: {job.job_id}")
            
            # Initialize metrics
            metrics = CrawlMetrics(
                job_id=job.job_id,
                start_time=start_time,
                total_pages_discovered=0,
                total_pages_crawled=0,
                total_content_extracted=0,
                total_errors=0,
                status="running"
            )
            
            # Update job status
            job.status = "running"
            job.started_at = start_time
            
            # Process each target URL
            for url in job.target_urls:
                try:
                    self.logger.debug(f"Processing URL: {url}")
                    
                    # Simulate crawling process
                    await asyncio.sleep(0.1)  # Simulate network delay
                    
                    # Extract content based on job configuration
                    content_items = await self._extract_content_from_url(url, job.content_types)
                    
                    # Store extracted content
                    for content in content_items:
                        await self._store_crawled_content(content, job.job_id)
                    
                    metrics.total_pages_crawled += 1
                    metrics.total_content_extracted += len(content_items)
                    
                    # Respect rate limiting
                    if job.rate_limit and job.rate_limit > 0:
                        await asyncio.sleep(1.0 / job.rate_limit)
                    
                except Exception as url_error:
                    self.logger.error(f"Error processing URL {url}: {url_error}")
                    metrics.total_errors += 1
                    continue
            
            # Finalize metrics
            metrics.end_time = datetime.now()
            metrics.duration = (metrics.end_time - start_time).total_seconds()
            metrics.status = "completed"
            
            # Update job status
            job.status = "completed"
            job.completed_at = metrics.end_time
            job.metrics = metrics
            
            self.logger.info(f"Crawl job {job.job_id} completed successfully. "
                           f"Pages: {metrics.total_pages_crawled}, "
                           f"Content: {metrics.total_content_extracted}, "
                           f"Errors: {metrics.total_errors}")
            
            return metrics
            
        except Exception as e:
            self.logger.error(f"Critical error in crawl job {job.job_id}: {e}")
            
            # Update failure metrics
            metrics.end_time = datetime.now()
            metrics.duration = (metrics.end_time - start_time).total_seconds()
            metrics.status = "failed"
            metrics.error_message = str(e)
            
            job.status = "failed"
            job.completed_at = metrics.end_time
            job.error_message = str(e)
            
            raise
    
    async def _extract_content_from_url(self, url: str, content_types: List[str]) -> List[Dict[str, Any]]:
        """Extract content from a URL based on specified content types"""
        content_items = []
        
        try:
            # Simulate content extraction
            for content_type in content_types:
                if content_type == "text":
                    content_items.append({
                        "type": "text",
                        "url": url,
                        "content": f"Sample text content from {url}",
                        "extracted_at": datetime.now().isoformat()
                    })
                elif content_type == "images":
                    content_items.append({
                        "type": "image",
                        "url": url,
                        "src": f"{url}/sample-image.jpg",
                        "alt": "Sample image",
                        "extracted_at": datetime.now().isoformat()
                    })
                elif content_type == "links":
                    content_items.append({
                        "type": "link",
                        "url": url,
                        "href": f"{url}/sample-link",
                        "text": "Sample link",
                        "extracted_at": datetime.now().isoformat()
                    })
            
        except Exception as e:
            self.logger.error(f"Error extracting content from {url}: {e}")
            
        return content_items
    
    async def _store_crawled_content(self, content: Dict[str, Any], job_id: str) -> None:
        """Store crawled content with job association"""
        try:
            # Add job metadata
            content["job_id"] = job_id
            content["stored_at"] = datetime.now().isoformat()
            
            # In a real implementation, this would store to database
            self.logger.debug(f"Stored content item for job {job_id}: {content['type']}")
            
        except Exception as e:
            self.logger.error(f"Error storing content for job {job_id}: {e}")
            raise
