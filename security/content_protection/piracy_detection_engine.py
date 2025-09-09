"""
Piracy Detection Engine
======================

Advanced AI-powered piracy detection system for real-time monitoring and enforcement.
Detects unauthorized content distribution across platforms, provides automated takedown
capabilities, and maintains comprehensive piracy analytics.

Author: Fahed Mlaiel (mlaiel@live.de)
"""

import logging
import hashlib
import json
import asyncio
import aiohttp
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import uuid
import re
from urllib.parse import urlparse, urljoin
import base64

# ML imports for content analysis
try:
    import numpy as np
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity
    ML_SUPPORT = True
except ImportError:
    ML_SUPPORT = False


class PiracyType(Enum):
    """Types of piracy detection"""
    DIRECT_COPY = "direct_copy"
    MODIFIED_CONTENT = "modified_content"
    UNAUTHORIZED_DISTRIBUTION = "unauthorized_distribution"
    TRADEMARK_INFRINGEMENT = "trademark_infringement"
    COPYRIGHT_VIOLATION = "copyright_violation"
    DEEP_FAKE = "deep_fake"
    SCRAPED_CONTENT = "scraped_content"


class DetectionSource(Enum):
    """Sources of piracy detection"""
    WEB_CRAWLER = "web_crawler"
    PLATFORM_API = "platform_api"
    USER_REPORT = "user_report"
    AUTOMATED_SCAN = "automated_scan"
    THIRD_PARTY_SERVICE = "third_party_service"
    MANUAL_REVIEW = "manual_review"


class PiracyStatus(Enum):
    """Status of piracy cases"""
    DETECTED = "detected"
    INVESTIGATING = "investigating"
    CONFIRMED = "confirmed"
    FALSE_POSITIVE = "false_positive"
    TAKEDOWN_REQUESTED = "takedown_requested"
    TAKEDOWN_COMPLETED = "takedown_completed"
    RESOLVED = "resolved"
    ESCALATED = "escalated"


@dataclass
class PiracyDetection:
    """Piracy detection result"""
    detection_id: str
    original_content_id: str
    infringing_url: str
    piracy_type: PiracyType
    detection_source: DetectionSource
    confidence_score: float
    detected_at: datetime
    platform: str
    uploader_info: Dict[str, Any]
    content_similarity: float
    metadata_analysis: Dict[str, Any]
    status: PiracyStatus = PiracyStatus.DETECTED
    evidence: List[Dict] = None
    takedown_actions: List[Dict] = None

    def __post_init__(self):
        if self.evidence is None:
            self.evidence = []
        if self.takedown_actions is None:
            self.takedown_actions = []


@dataclass
class MonitoringTarget:
    """Content monitoring configuration"""
    target_id: str
    content_id: str
    owner_id: str
    original_urls: List[str]
    fingerprints: List[str]
    keywords: List[str]
    monitoring_platforms: List[str]
    alert_threshold: float
    monitoring_frequency: int  # hours
    created_at: datetime
    is_active: bool = True


@dataclass
class TakedownRequest:
    """DMCA/Copyright takedown request"""
    request_id: str
    detection_id: str
    platform: str
    infringing_url: str
    content_owner: str
    legal_basis: str
    request_type: str  # DMCA, Copyright, Trademark
    submitted_at: datetime
    status: str = "pending"
    response_received_at: Optional[datetime] = None
    response_details: Dict[str, Any] = None

    def __post_init__(self):
        if self.response_details is None:
            self.response_details = {}


class PiracyDetectionEngine:
    """
    Advanced Piracy Detection Engine
    
    Provides comprehensive anti-piracy capabilities:
    - Real-time content monitoring across platforms
    - AI-powered similarity detection
    - Automated DMCA takedown generation
    - Multi-platform crawling and scanning
    - Deep fake and modified content detection
    - Comprehensive piracy analytics and reporting
    - Legal compliance and evidence collection
    """

    def __init__(self, config: Dict[str, Any] = None):
        """Initialize piracy detection engine"""
        self.config = config or {}
        self.logger = logging.getLogger(__name__)
        
        # Storage (in production, use database)
        self.detections: Dict[str, PiracyDetection] = {}
        self.monitoring_targets: Dict[str, MonitoringTarget] = {}
        self.takedown_requests: Dict[str, TakedownRequest] = {}
        
        # Platform configurations
        self.monitored_platforms = {
            'youtube': {
                'api_endpoint': 'https://www.googleapis.com/youtube/v3',
                'search_method': 'api',
                'takedown_method': 'dmca_form'
            },
            'instagram': {
                'api_endpoint': 'https://graph.instagram.com',
                'search_method': 'api',
                'takedown_method': 'copyright_form'
            },
            'tiktok': {
                'api_endpoint': 'https://open-api.tiktok.com',
                'search_method': 'scraping',
                'takedown_method': 'dmca_form'
            },
            'twitter': {
                'api_endpoint': 'https://api.twitter.com/2',
                'search_method': 'api',
                'takedown_method': 'copyright_form'
            },
            'facebook': {
                'api_endpoint': 'https://graph.facebook.com',
                'search_method': 'api',
                'takedown_method': 'ip_form'
            }
        }
        
        # Detection algorithms
        self.detection_algorithms = {
            'fingerprint_match': self._fingerprint_detection,
            'visual_similarity': self._visual_similarity_detection,
            'audio_similarity': self._audio_similarity_detection,
            'metadata_analysis': self._metadata_analysis_detection,
            'keyword_monitoring': self._keyword_monitoring_detection,
            'deep_fake_detection': self._deep_fake_detection
        }
        
        # Performance metrics
        self.metrics = {
            'total_detections': 0,
            'confirmed_piracy': 0,
            'false_positives': 0,
            'takedown_requests': 0,
            'successful_takedowns': 0,
            'monitoring_targets': 0,
            'platforms_monitored': len(self.monitored_platforms)
        }
        
        # ML models (simplified)
        if ML_SUPPORT:
            self.text_vectorizer = TfidfVectorizer(max_features=1000, stop_words='english')
            self.similarity_threshold = 0.85
        
        self.logger.info("Piracy Detection Engine initialized")

    async def add_monitoring_target(self, 
                                  content_id: str,
                                  owner_id: str,
                                  original_urls: List[str],
                                  fingerprints: List[str] = None,
                                  keywords: List[str] = None,
                                  platforms: List[str] = None) -> MonitoringTarget:
        """Add content for piracy monitoring"""
        
        target_id = str(uuid.uuid4())
        
        target = MonitoringTarget(
            target_id=target_id,
            content_id=content_id,
            owner_id=owner_id,
            original_urls=original_urls,
            fingerprints=fingerprints or [],
            keywords=keywords or [],
            monitoring_platforms=platforms or list(self.monitored_platforms.keys()),
            alert_threshold=0.8,
            monitoring_frequency=24,  # 24 hours
            created_at=datetime.utcnow()
        )
        
        self.monitoring_targets[target_id] = target
        self.metrics['monitoring_targets'] += 1
        
        self.logger.info(f"Added monitoring target: {target_id} for content: {content_id}")
        return target

    async def scan_for_piracy(self, target_id: str) -> List[PiracyDetection]:
        """Perform piracy scan for a monitoring target"""
        
        if target_id not in self.monitoring_targets:
            raise ValueError(f"Monitoring target not found: {target_id}")
        
        target = self.monitoring_targets[target_id]
        detections = []
        
        # Scan each platform
        for platform in target.monitoring_platforms:
            platform_detections = await self._scan_platform(target, platform)
            detections.extend(platform_detections)
        
        # Store all detections
        for detection in detections:
            self.detections[detection.detection_id] = detection
            self.metrics['total_detections'] += 1
        
        self.logger.info(f"Scan completed for target {target_id}: {len(detections)} detections")
        return detections

    async def _scan_platform(self, target: MonitoringTarget, platform: str) -> List[PiracyDetection]:
        """Scan specific platform for piracy"""
        
        platform_config = self.monitored_platforms.get(platform, {})
        detections = []
        
        try:
            if platform_config.get('search_method') == 'api':
                search_results = await self._api_search(target, platform)
            else:
                search_results = await self._web_scraping_search(target, platform)
            
            # Analyze each result
            for result in search_results:
                detection = await self._analyze_potential_infringement(target, result, platform)
                if detection and detection.confidence_score >= target.alert_threshold:
                    detections.append(detection)
                    
        except Exception as e:
            self.logger.error(f"Platform scan failed for {platform}: {str(e)}")
        
        return detections

    async def _api_search(self, target: MonitoringTarget, platform: str) -> List[Dict]:
        """Search platform using API"""
        
        results = []
        
        # Search by keywords
        for keyword in target.keywords:
            try:
                async with aiohttp.ClientSession() as session:
                    # Simulate API search (replace with actual API calls)
                    search_url = f"https://mock-api.{platform}.com/search"
                    params = {
                        'q': keyword,
                        'type': 'content',
                        'limit': 50
                    }
                    
                    # In real implementation, use proper API authentication
                    async with session.get(search_url, params=params) as response:
                        if response.status == 200:
                            data = await response.json()
                            results.extend(data.get('items', []))
                        
            except Exception as e:
                self.logger.debug(f"API search failed for {keyword} on {platform}: {str(e)}")
        
        return results

    async def _web_scraping_search(self, target: MonitoringTarget, platform: str) -> List[Dict]:
        """Search platform using web scraping"""
        
        results = []
        
        # Simulate web scraping results
        for keyword in target.keywords:
            try:
                async with aiohttp.ClientSession() as session:
                    search_url = f"https://www.{platform}.com/search?q={keyword}"
                    
                    async with session.get(search_url) as response:
                        if response.status == 200:
                            html_content = await response.text()
                            # Parse HTML and extract content URLs
                            urls = self._extract_urls_from_html(html_content, platform)
                            
                            for url in urls:
                                results.append({
                                    'url': url,
                                    'title': f"Content found for {keyword}",
                                    'platform': platform,
                                    'found_via': 'scraping'
                                })
                                
            except Exception as e:
                self.logger.debug(f"Web scraping failed for {keyword} on {platform}: {str(e)}")
        
        return results

    def _extract_urls_from_html(self, html: str, platform: str) -> List[str]:
        """Extract content URLs from HTML"""
        
        # Simplified URL extraction
        url_patterns = {
            'youtube': r'"/watch\?v=([a-zA-Z0-9_-]+)"',
            'instagram': r'"/p/([a-zA-Z0-9_-]+)/"',
            'tiktok': r'"/video/(\d+)"',
            'twitter': r'"/[^/]+/status/(\d+)"'
        }
        
        pattern = url_patterns.get(platform, r'"/([a-zA-Z0-9_-]+)"')
        matches = re.findall(pattern, html)
        
        base_urls = {
            'youtube': 'https://www.youtube.com/watch?v=',
            'instagram': 'https://www.instagram.com/p/',
            'tiktok': 'https://www.tiktok.com/video/',
            'twitter': 'https://twitter.com/user/status/'
        }
        
        base_url = base_urls.get(platform, f'https://www.{platform}.com/')
        urls = [base_url + match for match in matches[:20]]  # Limit results
        
        return urls

    async def _analyze_potential_infringement(self, 
                                            target: MonitoringTarget, 
                                            result: Dict, 
                                            platform: str) -> Optional[PiracyDetection]:
        """Analyze potential copyright infringement"""
        
        detection_id = str(uuid.uuid4())
        infringing_url = result.get('url', '')
        
        # Run multiple detection algorithms
        algorithm_results = {}
        
        for algo_name, algo_func in self.detection_algorithms.items():
            try:
                score = await algo_func(target, result)
                algorithm_results[algo_name] = score
            except Exception as e:
                self.logger.debug(f"Algorithm {algo_name} failed: {str(e)}")
                algorithm_results[algo_name] = 0.0
        
        # Calculate overall confidence
        confidence_score = np.mean(list(algorithm_results.values()))
        
        # Determine piracy type
        piracy_type = self._determine_piracy_type(algorithm_results)
        
        # Extract uploader information
        uploader_info = self._extract_uploader_info(result)
        
        # Create detection if confidence is high enough
        if confidence_score >= 0.5:  # Lower threshold for initial detection
            detection = PiracyDetection(
                detection_id=detection_id,
                original_content_id=target.content_id,
                infringing_url=infringing_url,
                piracy_type=piracy_type,
                detection_source=DetectionSource.AUTOMATED_SCAN,
                confidence_score=confidence_score,
                detected_at=datetime.utcnow(),
                platform=platform,
                uploader_info=uploader_info,
                content_similarity=algorithm_results.get('fingerprint_match', 0.0),
                metadata_analysis=algorithm_results,
                evidence=[
                    {
                        'type': 'algorithm_scores',
                        'data': algorithm_results,
                        'collected_at': datetime.utcnow().isoformat()
                    }
                ]
            )
            
            return detection
        
        return None

    async def _fingerprint_detection(self, target: MonitoringTarget, result: Dict) -> float:
        """Detect using content fingerprints"""
        
        # Simulate fingerprint matching
        # In practice, would compare actual content fingerprints
        
        if target.fingerprints and result.get('content_hash'):
            for fingerprint in target.fingerprints:
                # Simple hash comparison (in practice, use perceptual hashing)
                if fingerprint in result.get('content_hash', ''):
                    return 0.95
        
        return 0.1

    async def _visual_similarity_detection(self, target: MonitoringTarget, result: Dict) -> float:
        """Detect using visual similarity"""
        
        # Simulate visual similarity analysis
        # In practice, would use computer vision algorithms
        
        return np.random.uniform(0.1, 0.9)  # Placeholder

    async def _audio_similarity_detection(self, target: MonitoringTarget, result: Dict) -> float:
        """Detect using audio similarity"""
        
        # Simulate audio similarity analysis
        # In practice, would use audio fingerprinting
        
        return np.random.uniform(0.1, 0.8)  # Placeholder

    async def _metadata_analysis_detection(self, target: MonitoringTarget, result: Dict) -> float:
        """Detect using metadata analysis"""
        
        score = 0.0
        
        # Check title similarity
        if ML_SUPPORT and target.keywords:
            result_title = result.get('title', '').lower()
            for keyword in target.keywords:
                if keyword.lower() in result_title:
                    score += 0.3
        
        # Check description similarity
        result_description = result.get('description', '').lower()
        for url in target.original_urls:
            if url in result_description:
                score += 0.4
        
        # Check upload timing (suspicious if very recent)
        upload_date = result.get('upload_date')
        if upload_date:
            # Simple recency check
            score += 0.2
        
        return min(score, 1.0)

    async def _keyword_monitoring_detection(self, target: MonitoringTarget, result: Dict) -> float:
        """Detect using keyword monitoring"""
        
        score = 0.0
        result_text = (result.get('title', '') + ' ' + result.get('description', '')).lower()
        
        matched_keywords = 0
        for keyword in target.keywords:
            if keyword.lower() in result_text:
                matched_keywords += 1
        
        if target.keywords:
            score = matched_keywords / len(target.keywords)
        
        return score

    async def _deep_fake_detection(self, target: MonitoringTarget, result: Dict) -> float:
        """Detect deep fakes and AI-generated content"""
        
        # Simulate deep fake detection
        # In practice, would use specialized AI models
        
        return np.random.uniform(0.0, 0.3)  # Usually low unless actual deep fake

    def _determine_piracy_type(self, algorithm_results: Dict[str, float]) -> PiracyType:
        """Determine the type of piracy based on algorithm results"""
        
        # Get highest scoring algorithm
        best_algorithm = max(algorithm_results.items(), key=lambda x: x[1])
        
        type_mapping = {
            'fingerprint_match': PiracyType.DIRECT_COPY,
            'visual_similarity': PiracyType.MODIFIED_CONTENT,
            'audio_similarity': PiracyType.MODIFIED_CONTENT,
            'metadata_analysis': PiracyType.UNAUTHORIZED_DISTRIBUTION,
            'keyword_monitoring': PiracyType.COPYRIGHT_VIOLATION,
            'deep_fake_detection': PiracyType.DEEP_FAKE
        }
        
        return type_mapping.get(best_algorithm[0], PiracyType.COPYRIGHT_VIOLATION)

    def _extract_uploader_info(self, result: Dict) -> Dict[str, Any]:
        """Extract uploader information from result"""
        
        return {
            'username': result.get('uploader', 'unknown'),
            'user_id': result.get('uploader_id', ''),
            'channel': result.get('channel', ''),
            'upload_date': result.get('upload_date', ''),
            'view_count': result.get('view_count', 0),
            'subscriber_count': result.get('subscriber_count', 0)
        }

    async def confirm_detection(self, detection_id: str, is_confirmed: bool) -> bool:
        """Manually confirm or reject a detection"""
        
        if detection_id not in self.detections:
            return False
        
        detection = self.detections[detection_id]
        
        if is_confirmed:
            detection.status = PiracyStatus.CONFIRMED
            self.metrics['confirmed_piracy'] += 1
        else:
            detection.status = PiracyStatus.FALSE_POSITIVE
            self.metrics['false_positives'] += 1
        
        self.logger.info(f"Detection {detection_id} marked as {'confirmed' if is_confirmed else 'false positive'}")
        return True

    async def generate_takedown_request(self, detection_id: str) -> TakedownRequest:
        """Generate DMCA/Copyright takedown request"""
        
        if detection_id not in self.detections:
            raise ValueError(f"Detection not found: {detection_id}")
        
        detection = self.detections[detection_id]
        request_id = str(uuid.uuid4())
        
        # Determine appropriate takedown method
        platform_config = self.monitored_platforms.get(detection.platform, {})
        takedown_method = platform_config.get('takedown_method', 'dmca_form')
        
        # Generate takedown request
        takedown_request = TakedownRequest(
            request_id=request_id,
            detection_id=detection_id,
            platform=detection.platform,
            infringing_url=detection.infringing_url,
            content_owner=detection.original_content_id,  # Should be actual owner info
            legal_basis="Copyright infringement under DMCA",
            request_type="DMCA",
            submitted_at=datetime.utcnow()
        )
        
        self.takedown_requests[request_id] = takedown_request
        detection.status = PiracyStatus.TAKEDOWN_REQUESTED
        detection.takedown_actions.append({
            'request_id': request_id,
            'type': 'dmca_request',
            'submitted_at': datetime.utcnow().isoformat()
        })
        
        self.metrics['takedown_requests'] += 1
        
        self.logger.info(f"Takedown request generated: {request_id} for detection: {detection_id}")
        return takedown_request

    async def process_takedown_response(self, request_id: str, response: Dict[str, Any]) -> bool:
        """Process response to takedown request"""
        
        if request_id not in self.takedown_requests:
            return False
        
        takedown_request = self.takedown_requests[request_id]
        detection = self.detections[takedown_request.detection_id]
        
        takedown_request.response_received_at = datetime.utcnow()
        takedown_request.response_details = response
        
        # Process response
        if response.get('status') == 'accepted':
            takedown_request.status = 'accepted'
            detection.status = PiracyStatus.TAKEDOWN_COMPLETED
            self.metrics['successful_takedowns'] += 1
        elif response.get('status') == 'rejected':
            takedown_request.status = 'rejected'
            detection.status = PiracyStatus.ESCALATED
        else:
            takedown_request.status = 'pending'
        
        self.logger.info(f"Takedown response processed: {request_id} - {response.get('status')}")
        return True

    async def get_detection_analytics(self, detection_id: str) -> Dict[str, Any]:
        """Get analytics for a specific detection"""
        
        if detection_id not in self.detections:
            return {}
        
        detection = self.detections[detection_id]
        
        # Get related takedown requests
        takedown_requests = [
            tr for tr in self.takedown_requests.values() 
            if tr.detection_id == detection_id
        ]
        
        analytics = {
            'detection_id': detection_id,
            'content_id': detection.original_content_id,
            'piracy_type': detection.piracy_type.value,
            'platform': detection.platform,
            'confidence_score': detection.confidence_score,
            'status': detection.status.value,
            'detected_at': detection.detected_at.isoformat(),
            'takedown_requests': len(takedown_requests),
            'evidence_count': len(detection.evidence),
            'uploader_info': detection.uploader_info
        }
        
        return analytics

    async def get_system_metrics(self) -> Dict[str, Any]:
        """Get overall piracy detection system metrics"""
        
        # Calculate detection accuracy
        total_confirmed = self.metrics['confirmed_piracy'] + self.metrics['false_positives']
        accuracy = (self.metrics['confirmed_piracy'] / total_confirmed * 100) if total_confirmed > 0 else 0
        
        # Calculate takedown success rate
        takedown_success_rate = (
            self.metrics['successful_takedowns'] / self.metrics['takedown_requests'] * 100
        ) if self.metrics['takedown_requests'] > 0 else 0
        
        return {
            'metrics': self.metrics,
            'detection_accuracy': f"{accuracy:.1f}%",
            'takedown_success_rate': f"{takedown_success_rate:.1f}%",
            'total_monitored_content': len(self.monitoring_targets),
            'active_monitoring_targets': sum(1 for t in self.monitoring_targets.values() if t.is_active),
            'recent_detections': len([d for d in self.detections.values() 
                                   if d.detected_at > datetime.utcnow() - timedelta(days=7)]),
            'platform_coverage': list(self.monitored_platforms.keys()),
            'system_status': 'operational'
        }

    async def run_continuous_monitoring(self, interval_hours: int = 24):
        """Run continuous monitoring for all active targets"""
        
        while True:
            try:
                active_targets = [t for t in self.monitoring_targets.values() if t.is_active]
                
                for target in active_targets:
                    # Check if it's time to scan this target
                    time_since_creation = datetime.utcnow() - target.created_at
                    if time_since_creation.total_seconds() >= target.monitoring_frequency * 3600:
                        
                        self.logger.info(f"Running scheduled scan for target: {target.target_id}")
                        detections = await self.scan_for_piracy(target.target_id)
                        
                        # Auto-confirm high confidence detections
                        for detection in detections:
                            if detection.confidence_score >= 0.9:
                                await self.confirm_detection(detection.detection_id, True)
                                await self.generate_takedown_request(detection.detection_id)
                
                # Wait for next monitoring cycle
                await asyncio.sleep(interval_hours * 3600)
                
            except Exception as e:
                self.logger.error(f"Continuous monitoring error: {str(e)}")
                await asyncio.sleep(3600)  # Wait 1 hour before retrying


# Utility functions
async def create_piracy_detection_engine(config: Dict[str, Any] = None) -> PiracyDetectionEngine:
    """Factory function to create piracy detection engine"""
    engine = PiracyDetectionEngine(config)
    return engine


# Example usage
if __name__ == "__main__":
    async def demo():
        """Demonstrate piracy detection engine capabilities"""
        engine = await create_piracy_detection_engine()
        
        # Add monitoring target
        target = await engine.add_monitoring_target(
            content_id="audio_123",
            owner_id="creator_456",
            original_urls=["https://example.com/original"],
            fingerprints=["abc123def456"],
            keywords=["my song title", "artist name"],
            platforms=["youtube", "instagram"]
        )
        
        print(f"Added monitoring target: {target.target_id}")
        
        # Perform piracy scan
        detections = await engine.scan_for_piracy(target.target_id)
        print(f"Piracy scan completed: {len(detections)} detections")
        
        # Process detections
        for detection in detections:
            print(f"Detection: {detection.detection_id} - Confidence: {detection.confidence_score:.2f}")
            
            if detection.confidence_score >= 0.8:
                # Confirm high confidence detections
                await engine.confirm_detection(detection.detection_id, True)
                
                # Generate takedown request
                takedown = await engine.generate_takedown_request(detection.detection_id)
                print(f"Takedown request generated: {takedown.request_id}")
        
        # Get analytics
        metrics = await engine.get_system_metrics()
        print(f"System metrics: {metrics}")
    
    asyncio.run(demo())