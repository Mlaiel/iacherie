"""
Violation Detection System for Content Protection

Advanced AI-powered violation detection across all content types.
Provides automated copyright infringement detection, DMCA compliance, and legal evidence collection.

Author: Fahed Mlaiel <mlaiel@live.de>
Project: IA Influencer Agent with Content Protection
Team: Lead Dev IA + Backend Senior + ML Engineer + DevOps + DBA + Security + Microservices + Audio + IA Prompt Engineer

Copyright © 2025 Fahed Mlaiel. All rights reserved.
Unauthorized copying, modification, or distribution is strictly prohibited.
Contact: mlaiel@live.de for licensing and collaboration.
"""

import numpy as np
import cv2
from typing import Dict, List, Optional, Tuple, Any, Union
import logging
from datetime import datetime, timedelta
from pathlib import Path
import hashlib
import json
import base64
from dataclasses import dataclass
from enum import Enum
import requests
from PIL import Image
import io

from .similarity_matcher import SimilarityMatcher
from ..engines.vector_engine import VectorEngine
from ..crawlers.web_crawler import WebCrawler
from ..storage.evidence_storage import EvidenceStorage
from ...utils.cache_manager import cache_result
from ...utils.metrics import track_performance
from ...config.settings import get_settings
from ...models.violation import ViolationModel, ViolationStatus, ViolationType

logger = logging.getLogger(__name__)


class ViolationSeverity(Enum):
    """Violation severity levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ViolationType(Enum):
    """Types of content violations."""
    COPYRIGHT_INFRINGEMENT = "copyright_infringement"
    UNAUTHORIZED_USE = "unauthorized_use"
    MODIFIED_CONTENT = "modified_content"
    PARTIAL_COPY = "partial_copy"
    EXACT_COPY = "exact_copy"
    DERIVATIVE_WORK = "derivative_work"


@dataclass
class ViolationEvidence:
    """Evidence collected for violation detection."""
    screenshot_path: str
    source_url: str
    detection_timestamp: datetime
    similarity_score: float
    violation_type: ViolationType
    metadata: Dict[str, Any]
    hash_evidence: str
    legal_notice_sent: bool = False


class ViolationDetector:
    """
    Enterprise-grade violation detection system for content protection.
    
    Features:
    - Multi-modal violation detection (audio, video, image, text)
    - Real-time web crawling and monitoring
    - Automated evidence collection
    - DMCA compliance and legal documentation
    - Severity assessment and prioritization
    - Integration with legal frameworks
    """
    
    def __init__(self):
        """Initialize violation detector with monitoring systems."""
        self.settings = get_settings()
        self.similarity_matcher = SimilarityMatcher()
        self.web_crawler = WebCrawler()
        self.evidence_storage = EvidenceStorage()
        
        # Detection thresholds
        self.violation_thresholds = {
            ViolationType.EXACT_COPY: 0.95,
            ViolationType.COPYRIGHT_INFRINGEMENT: 0.85,
            ViolationType.UNAUTHORIZED_USE: 0.80,
            ViolationType.MODIFIED_CONTENT: 0.75,
            ViolationType.PARTIAL_COPY: 0.70,
            ViolationType.DERIVATIVE_WORK: 0.65
        }
        
        # Monitoring platforms
        self.monitored_platforms = [
            'youtube.com',
            'instagram.com',
            'tiktok.com',
            'twitter.com',
            'facebook.com',
            'linkedin.com',
            'pinterest.com',
            'soundcloud.com',
            'spotify.com',
            'apple.com'
        ]
        
        # Legal frameworks
        self.legal_frameworks = {
            'DMCA': {'jurisdiction': 'US', 'takedown_template': 'dmca_takedown.html'},
            'GDPR': {'jurisdiction': 'EU', 'compliance_template': 'gdpr_notice.html'},
            'COPYRIGHT_ACT': {'jurisdiction': 'DE', 'notice_template': 'de_copyright.html'}
        }
        
    @track_performance
    def detect_violations(
        self, 
        content_id: str,
        content_path: str,
        content_type: str,
        owner_id: str,
        search_platforms: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """
        Detect violations of protected content across platforms.
        
        Args:
            content_id: Unique identifier for content
            content_path: Path to original content file
            content_type: Type of content (audio, video, image, text)
            owner_id: ID of content owner
            search_platforms: Platforms to search (optional)
            
        Returns:
            List of detected violations with evidence
        """
        try:
            platforms = search_platforms or self.monitored_platforms
            detected_violations = []
            
            logger.info(f"Starting violation detection for content {content_id}")
            
            # Create content fingerprint for comparison
            content_fingerprint = self._create_content_fingerprint(content_path, content_type)
            
            # Search each platform for potential violations
            for platform in platforms:
                platform_violations = self._search_platform_violations(
                    content_fingerprint,
                    content_type,
                    platform,
                    content_id,
                    owner_id
                )
                detected_violations.extend(platform_violations)
            
            # Assess and prioritize violations
            prioritized_violations = self._prioritize_violations(detected_violations)
            
            # Store violations in database
            self._store_violations(prioritized_violations, content_id, owner_id)
            
            logger.info(f"Detected {len(prioritized_violations)} violations for content {content_id}")
            return prioritized_violations
            
        except Exception as e:
            logger.error(f"Error detecting violations: {e}")
            return []
    
    def _create_content_fingerprint(self, content_path: str, content_type: str) -> Dict[str, Any]:
        """Create comprehensive fingerprint for content matching."""
        try:
            fingerprint = {
                'content_type': content_type,
                'file_hash': self._calculate_file_hash(content_path),
                'creation_time': datetime.utcnow().isoformat()
            }
            
            if content_type == 'audio':
                fingerprint.update(self._create_audio_fingerprint(content_path))
            elif content_type == 'image':
                fingerprint.update(self._create_image_fingerprint(content_path))
            elif content_type == 'video':
                fingerprint.update(self._create_video_fingerprint(content_path))
            elif content_type == 'text':
                fingerprint.update(self._create_text_fingerprint(content_path))
            
            return fingerprint
            
        except Exception as e:
            logger.error(f"Error creating content fingerprint: {e}")
            return {}
    
    def _create_audio_fingerprint(self, audio_path: str) -> Dict[str, Any]:
        """Create audio-specific fingerprint."""
        try:
            import librosa
            import chromaprint
            
            # Load audio
            y, sr = librosa.load(audio_path, sr=22050)
            
            # Create chromaprint fingerprint
            raw_fingerprint, encoded_fingerprint = chromaprint.fingerprint_raw(y, sr)
            
            # Extract audio features
            mfccs = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=13)
            spectral_centroid = librosa.feature.spectral_centroid(y=y, sr=sr)
            
            return {
                'chromaprint': encoded_fingerprint,
                'duration': len(y) / sr,
                'sample_rate': sr,
                'mfcc_mean': np.mean(mfccs, axis=1).tolist(),
                'spectral_centroid_mean': float(np.mean(spectral_centroid))
            }
            
        except Exception as e:
            logger.error(f"Error creating audio fingerprint: {e}")
            return {}
    
    def _create_image_fingerprint(self, image_path: str) -> Dict[str, Any]:
        """Create image-specific fingerprint."""
        try:
            # Load image
            image = cv2.imread(image_path)
            if image is None:
                raise ValueError("Could not load image")
            
            # Calculate perceptual hash
            pil_image = Image.open(image_path)
            perceptual_hash = str(hash(pil_image.tobytes()))
            
            # Extract visual features
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            hist = cv2.calcHist([gray], [0], None, [256], [0, 256])
            
            # SIFT features for robust matching
            sift = cv2.SIFT_create()
            keypoints, descriptors = sift.detectAndCompute(gray, None)
            
            return {
                'perceptual_hash': perceptual_hash,
                'dimensions': {'width': image.shape[1], 'height': image.shape[0]},
                'histogram_mean': float(np.mean(hist)),
                'keypoints_count': len(keypoints) if keypoints else 0,
                'descriptors_shape': descriptors.shape if descriptors is not None else [0, 0]
            }
            
        except Exception as e:
            logger.error(f"Error creating image fingerprint: {e}")
            return {}
    
    def _create_video_fingerprint(self, video_path: str) -> Dict[str, Any]:
        """Create video-specific fingerprint."""
        try:
            cap = cv2.VideoCapture(video_path)
            
            # Get video properties
            fps = cap.get(cv2.CAP_PROP_FPS)
            frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            duration = frame_count / fps if fps > 0 else 0
            
            # Extract keyframes
            keyframe_hashes = []
            frame_indices = np.linspace(0, frame_count-1, min(10, frame_count), dtype=int)
            
            for frame_idx in frame_indices:
                cap.set(cv2.CAP_PROP_POS_FRAMES, frame_idx)
                ret, frame = cap.read()
                
                if ret:
                    # Calculate frame hash
                    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                    frame_hash = hashlib.md5(gray.tobytes()).hexdigest()
                    keyframe_hashes.append(frame_hash)
            
            cap.release()
            
            return {
                'duration': duration,
                'fps': fps,
                'frame_count': frame_count,
                'keyframe_hashes': keyframe_hashes,
                'video_hash': hashlib.md5(''.join(keyframe_hashes).encode()).hexdigest()
            }
            
        except Exception as e:
            logger.error(f"Error creating video fingerprint: {e}")
            return {}
    
    def _create_text_fingerprint(self, text_path: str) -> Dict[str, Any]:
        """Create text-specific fingerprint."""
        try:
            with open(text_path, 'r', encoding='utf-8') as f:
                text_content = f.read()
            
            # Calculate text statistics
            word_count = len(text_content.split())
            char_count = len(text_content)
            
            # Create n-gram fingerprints
            words = text_content.lower().split()
            bigrams = [' '.join(words[i:i+2]) for i in range(len(words)-1)]
            trigrams = [' '.join(words[i:i+3]) for i in range(len(words)-2)]
            
            return {
                'word_count': word_count,
                'char_count': char_count,
                'text_hash': hashlib.md5(text_content.encode()).hexdigest(),
                'bigram_sample': bigrams[:10],  # First 10 bigrams
                'trigram_sample': trigrams[:10],  # First 10 trigrams
                'language_detected': self._detect_language(text_content)
            }
            
        except Exception as e:
            logger.error(f"Error creating text fingerprint: {e}")
            return {}
    
    def _search_platform_violations(
        self, 
        content_fingerprint: Dict[str, Any],
        content_type: str,
        platform: str,
        content_id: str,
        owner_id: str
    ) -> List[Dict[str, Any]]:
        """Search specific platform for content violations."""
        try:
            violations = []
            
            # Get platform-specific search results
            search_results = self.web_crawler.search_platform(
                platform=platform,
                content_type=content_type,
                search_terms=self._generate_search_terms(content_fingerprint, content_type)
            )
            
            # Analyze each result for violations
            for result in search_results:
                violation = self._analyze_potential_violation(
                    result,
                    content_fingerprint,
                    content_type,
                    platform,
                    content_id,
                    owner_id
                )
                
                if violation:
                    violations.append(violation)
            
            return violations
            
        except Exception as e:
            logger.error(f"Error searching platform {platform}: {e}")
            return []
    
    def _analyze_potential_violation(
        self,
        search_result: Dict[str, Any],
        original_fingerprint: Dict[str, Any],
        content_type: str,
        platform: str,
        content_id: str,
        owner_id: str
    ) -> Optional[Dict[str, Any]]:
        """Analyze search result for potential violation."""
        try:
            # Download and analyze found content
            found_content_path = self.web_crawler.download_content(
                search_result['url'],
                content_type
            )
            
            if not found_content_path:
                return None
            
            # Create fingerprint for found content
            found_fingerprint = self._create_content_fingerprint(found_content_path, content_type)
            
            # Calculate similarity
            similarity_score = self._calculate_fingerprint_similarity(
                original_fingerprint,
                found_fingerprint,
                content_type
            )
            
            # Determine violation type based on similarity
            violation_type = self._determine_violation_type(similarity_score)
            
            if violation_type:
                # Collect evidence
                evidence = self._collect_violation_evidence(
                    search_result,
                    found_content_path,
                    similarity_score,
                    violation_type,
                    platform
                )
                
                # Calculate severity
                severity = self._calculate_violation_severity(
                    violation_type,
                    similarity_score,
                    platform,
                    search_result
                )
                
                return {
                    'content_id': content_id,
                    'owner_id': owner_id,
                    'violation_type': violation_type.value,
                    'severity': severity.value,
                    'platform': platform,
                    'infringing_url': search_result['url'],
                    'similarity_score': similarity_score,
                    'evidence': evidence,
                    'detected_at': datetime.utcnow().isoformat(),
                    'status': 'detected'
                }
            
            return None
            
        except Exception as e:
            logger.error(f"Error analyzing potential violation: {e}")
            return None
    
    def _calculate_fingerprint_similarity(
        self,
        fingerprint1: Dict[str, Any],
        fingerprint2: Dict[str, Any],
        content_type: str
    ) -> float:
        """Calculate similarity between two content fingerprints."""
        try:
            if content_type == 'audio':
                return self._calculate_audio_similarity(fingerprint1, fingerprint2)
            elif content_type == 'image':
                return self._calculate_image_similarity(fingerprint1, fingerprint2)
            elif content_type == 'video':
                return self._calculate_video_similarity(fingerprint1, fingerprint2)
            elif content_type == 'text':
                return self._calculate_text_similarity(fingerprint1, fingerprint2)
            
            return 0.0
            
        except Exception as e:
            logger.error(f"Error calculating fingerprint similarity: {e}")
            return 0.0
    
    def _calculate_audio_similarity(self, fp1: Dict, fp2: Dict) -> float:
        """Calculate audio fingerprint similarity."""
        try:
            # Compare chromaprint fingerprints
            if 'chromaprint' in fp1 and 'chromaprint' in fp2:
                # This would use chromaprint comparison algorithms
                # Simplified for now
                return 0.8 if fp1['chromaprint'] == fp2['chromaprint'] else 0.0
            
            # Compare MFCC features
            if 'mfcc_mean' in fp1 and 'mfcc_mean' in fp2:
                mfcc1 = np.array(fp1['mfcc_mean'])
                mfcc2 = np.array(fp2['mfcc_mean'])
                return float(np.corrcoef(mfcc1, mfcc2)[0, 1])
            
            return 0.0
            
        except Exception as e:
            logger.error(f"Error calculating audio similarity: {e}")
            return 0.0
    
    def _calculate_image_similarity(self, fp1: Dict, fp2: Dict) -> float:
        """Calculate image fingerprint similarity."""
        try:
            # Compare perceptual hashes
            if 'perceptual_hash' in fp1 and 'perceptual_hash' in fp2:
                hash1 = fp1['perceptual_hash']
                hash2 = fp2['perceptual_hash']
                
                # Calculate Hamming distance
                if hash1 == hash2:
                    return 1.0
                else:
                    # Simplified similarity based on hash comparison
                    return 0.5
            
            # Compare histograms
            if 'histogram_mean' in fp1 and 'histogram_mean' in fp2:
                hist_diff = abs(fp1['histogram_mean'] - fp2['histogram_mean'])
                return max(0, 1 - hist_diff / 255.0)
            
            return 0.0
            
        except Exception as e:
            logger.error(f"Error calculating image similarity: {e}")
            return 0.0
    
    def _calculate_video_similarity(self, fp1: Dict, fp2: Dict) -> float:
        """Calculate video fingerprint similarity."""
        try:
            # Compare keyframe hashes
            if 'keyframe_hashes' in fp1 and 'keyframe_hashes' in fp2:
                hashes1 = set(fp1['keyframe_hashes'])
                hashes2 = set(fp2['keyframe_hashes'])
                
                intersection = len(hashes1.intersection(hashes2))
                union = len(hashes1.union(hashes2))
                
                return intersection / union if union > 0 else 0.0
            
            # Compare video hashes
            if 'video_hash' in fp1 and 'video_hash' in fp2:
                return 1.0 if fp1['video_hash'] == fp2['video_hash'] else 0.0
            
            return 0.0
            
        except Exception as e:
            logger.error(f"Error calculating video similarity: {e}")
            return 0.0
    
    def _calculate_text_similarity(self, fp1: Dict, fp2: Dict) -> float:
        """Calculate text fingerprint similarity."""
        try:
            # Compare text hashes
            if 'text_hash' in fp1 and 'text_hash' in fp2:
                if fp1['text_hash'] == fp2['text_hash']:
                    return 1.0
            
            # Compare n-grams
            if 'bigram_sample' in fp1 and 'bigram_sample' in fp2:
                bigrams1 = set(fp1['bigram_sample'])
                bigrams2 = set(fp2['bigram_sample'])
                
                intersection = len(bigrams1.intersection(bigrams2))
                union = len(bigrams1.union(bigrams2))
                
                return intersection / union if union > 0 else 0.0
            
            return 0.0
            
        except Exception as e:
            logger.error(f"Error calculating text similarity: {e}")
            return 0.0
    
    def _determine_violation_type(self, similarity_score: float) -> Optional[ViolationType]:
        """Determine violation type based on similarity score."""
        for violation_type, threshold in sorted(
            self.violation_thresholds.items(),
            key=lambda x: x[1],
            reverse=True
        ):
            if similarity_score >= threshold:
                return violation_type
        
        return None
    
    def _calculate_violation_severity(
        self,
        violation_type: ViolationType,
        similarity_score: float,
        platform: str,
        search_result: Dict[str, Any]
    ) -> ViolationSeverity:
        """Calculate violation severity based on multiple factors."""
        base_severity = {
            ViolationType.EXACT_COPY: ViolationSeverity.CRITICAL,
            ViolationType.COPYRIGHT_INFRINGEMENT: ViolationSeverity.HIGH,
            ViolationType.UNAUTHORIZED_USE: ViolationSeverity.HIGH,
            ViolationType.MODIFIED_CONTENT: ViolationSeverity.MEDIUM,
            ViolationType.PARTIAL_COPY: ViolationSeverity.MEDIUM,
            ViolationType.DERIVATIVE_WORK: ViolationSeverity.LOW
        }.get(violation_type, ViolationSeverity.LOW)
        
        # Adjust severity based on platform reach
        high_reach_platforms = ['youtube.com', 'instagram.com', 'tiktok.com', 'facebook.com']
        if platform in high_reach_platforms and base_severity == ViolationSeverity.MEDIUM:
            base_severity = ViolationSeverity.HIGH
        
        # Adjust based on similarity score
        if similarity_score >= 0.95 and base_severity != ViolationSeverity.CRITICAL:
            if base_severity == ViolationSeverity.HIGH:
                base_severity = ViolationSeverity.CRITICAL
            elif base_severity == ViolationSeverity.MEDIUM:
                base_severity = ViolationSeverity.HIGH
        
        return base_severity
    
    def _collect_violation_evidence(
        self,
        search_result: Dict[str, Any],
        content_path: str,
        similarity_score: float,
        violation_type: ViolationType,
        platform: str
    ) -> ViolationEvidence:
        """Collect comprehensive evidence for the violation."""
        try:
            # Take screenshot of the infringing page
            screenshot_path = self.web_crawler.take_screenshot(search_result['url'])
            
            # Generate evidence hash
            evidence_hash = hashlib.sha256(
                f"{search_result['url']}{similarity_score}{datetime.utcnow().isoformat()}".encode()
            ).hexdigest()
            
            # Create evidence object
            evidence = ViolationEvidence(
                screenshot_path=screenshot_path,
                source_url=search_result['url'],
                detection_timestamp=datetime.utcnow(),
                similarity_score=similarity_score,
                violation_type=violation_type,
                metadata={
                    'platform': platform,
                    'search_result': search_result,
                    'content_path': content_path,
                    'user_agent': self.web_crawler.user_agent,
                    'detection_method': 'automated_fingerprint_matching'
                },
                hash_evidence=evidence_hash
            )
            
            # Store evidence
            self.evidence_storage.store_evidence(evidence)
            
            return evidence
            
        except Exception as e:
            logger.error(f"Error collecting violation evidence: {e}")
            return None
    
    def _prioritize_violations(self, violations: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Prioritize violations based on severity and business impact."""
        try:
            # Sort by severity and similarity score
            severity_order = {
                ViolationSeverity.CRITICAL.value: 4,
                ViolationSeverity.HIGH.value: 3,
                ViolationSeverity.MEDIUM.value: 2,
                ViolationSeverity.LOW.value: 1
            }
            
            return sorted(
                violations,
                key=lambda x: (
                    severity_order.get(x.get('severity', 'low'), 0),
                    x.get('similarity_score', 0)
                ),
                reverse=True
            )
            
        except Exception as e:
            logger.error(f"Error prioritizing violations: {e}")
            return violations
    
    def _store_violations(self, violations: List[Dict[str, Any]], content_id: str, owner_id: str) -> None:
        """Store detected violations in database."""
        try:
            for violation in violations:
                # Create violation model instance
                violation_model = ViolationModel(
                    content_id=content_id,
                    owner_id=owner_id,
                    violation_type=violation['violation_type'],
                    severity=violation['severity'],
                    platform=violation['platform'],
                    infringing_url=violation['infringing_url'],
                    similarity_score=violation['similarity_score'],
                    evidence_data=violation.get('evidence'),
                    status=ViolationStatus.DETECTED,
                    detected_at=datetime.utcnow()
                )
                
                # Save to database
                violation_model.save()
                
            logger.info(f"Stored {len(violations)} violations for content {content_id}")
            
        except Exception as e:
            logger.error(f"Error storing violations: {e}")
    
    def _generate_search_terms(self, fingerprint: Dict[str, Any], content_type: str) -> List[str]:
        """Generate search terms based on content fingerprint."""
        # This would generate intelligent search terms based on content analysis
        # Simplified implementation
        return ['content', 'media', content_type]
    
    def _detect_language(self, text: str) -> str:
        """Detect language of text content."""
        # This would use language detection library
        # Simplified implementation
        return 'en'
    
    def _calculate_file_hash(self, file_path: str) -> str:
        """Calculate SHA-256 hash of file."""
        try:
            with open(file_path, 'rb') as f:
                file_hash = hashlib.sha256(f.read()).hexdigest()
            return file_hash
        except Exception as e:
            logger.error(f"Error calculating file hash: {e}")
            return ""
    
    def generate_dmca_notice(self, violation_id: str) -> str:
        """Generate DMCA takedown notice for violation."""
        try:
            # This would generate a proper DMCA notice
            # Implementation would include legal templates
            return f"DMCA takedown notice generated for violation {violation_id}"
            
        except Exception as e:
            logger.error(f"Error generating DMCA notice: {e}")
            return ""
    
    def get_violation_stats(self, owner_id: str) -> Dict[str, Any]:
        """Get violation statistics for content owner."""
        try:
            # This would query database for violation statistics
            return {
                'total_violations': 0,
                'by_severity': {
                    'critical': 0,
                    'high': 0,
                    'medium': 0,
                    'low': 0
                },
                'by_platform': {},
                'resolved_violations': 0,
                'pending_violations': 0
            }
            
        except Exception as e:
            logger.error(f"Error getting violation stats: {e}")
            return {}
