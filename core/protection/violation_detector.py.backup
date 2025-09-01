"""Violation Detection System for Content Protection

This module provides advanced violation detection capabilities:
- Automated similarity analysis between protected and detected content
- Multi-modal content comparison (audio, video, image, text)
- Confidence scoring and threshold management
- False positive reduction algorithms
- Evidence compilation for legal proceedings

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: © 2025 Fahed Mlaiel. All rights reserved.
"""
import asyncio
import numpy as np
from typing import Dict, List, Optional, Tuple, Any, Set
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
import logging
from pathlib import Path
import json
import hashlib
from urllib.parse import urlparse
import aiohttp
from PIL import Image
import io

# ML and similarity computation
from sklearn.metrics.pairwise import cosine_similarity
import faiss
from scipy.spatial.distance import hamming
import cv2

# Internal imports
from ...utils.logging import get_logger
from ...database.models.content import ContentFingerprint, ViolationAlert, ContentType
from ...config.settings import get_settings
from .fingerprint_engine import FingerprintEngine, FingerprintResult, FingerprintType
from .content_monitor import MonitoringResult, ContentMonitor

logger = get_logger(__name__)
settings = get_settings()


class ViolationType(Enum):
    """Types of content violations"""
    EXACT_DUPLICATE = "exact_duplicate"
    MODIFIED_CONTENT = "modified_content"
    PARTIAL_USAGE = "partial_usage"
    DERIVATIVE_WORK = "derivative_work"
    UNAUTHORIZED_REMIX = "unauthorized_remix"
    THUMBNAIL_THEFT = "thumbnail_theft"
    METADATA_COPYING = "metadata_copying"


class ViolationSeverity(Enum):
    """Severity levels for violations"""
    CRITICAL = "critical"      # >95% similarity
    HIGH = "high"             # 85-95% similarity
    MEDIUM = "medium"         # 70-85% similarity
    LOW = "low"              # 50-70% similarity
    SUSPICIOUS = "suspicious" # 30-50% similarity


@dataclass
class SimilarityScore:
    """Similarity score between content pieces"""
    fingerprint_type: FingerprintType
    similarity_score: float
    hash_match: bool = False
    vector_similarity: Optional[float] = None
    metadata_match: Optional[float] = None
    confidence: float = 0.0


@dataclass
class ViolationEvidence:
    """Evidence for a content violation"""
    violation_id: str
    original_content_id: str
    detected_url: str
    violation_type: ViolationType
    severity: ViolationSeverity
    similarity_scores: List[SimilarityScore] = field(default_factory=list)
    screenshots: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.utcnow)
    verified: bool = False
    false_positive_score: float = 0.0


@dataclass
class DetectionConfig:
    """Configuration for violation detection"""
    similarity_threshold: float = 0.75
    exact_match_threshold: float = 0.95
    partial_match_threshold: float = 0.60
    false_positive_threshold: float = 0.30
    enable_hash_matching: bool = True
    enable_vector_matching: bool = True
    enable_metadata_matching: bool = True
    cross_platform_detection: bool = True
    deep_analysis: bool = False


class SimilarityAnalyzer:
    """Advanced similarity analysis for content comparison"""
    
    def __init__(self):
        self.hash_similarity_cache = {}
        self.vector_similarity_cache = {}
    
    async def analyze_similarity(self, 
                               original_fingerprints: List[FingerprintResult],
                               detected_content_url: str,
                               config: DetectionConfig) -> List[SimilarityScore]:
        """Analyze similarity between original and detected content"""
        similarity_scores = []
        
        try:
            # Download and analyze detected content
            detected_fingerprints = await self._analyze_detected_content(detected_content_url)
            
            # Compare fingerprints
            for original_fp in original_fingerprints:
                for detected_fp in detected_fingerprints:
                    if original_fp.fingerprint_type == detected_fp.fingerprint_type:
                        score = await self._compare_fingerprints(original_fp, detected_fp, config)
                        if score:
                            similarity_scores.append(score)
            
            # Sort by similarity score
            similarity_scores.sort(key=lambda x: x.similarity_score, reverse=True)
            
        except Exception as e:
            logger.error(f"Error analyzing similarity: {e}")
        
        return similarity_scores
    
    async def _analyze_detected_content(self, url: str) -> List[FingerprintResult]:
        """Download and analyze detected content to generate fingerprints"""
        fingerprints = []
        
        try:
            # Determine content type from URL
            content_type = self._detect_content_type(url)
            
            if content_type == ContentType.IMAGE:
                fingerprints = await self._analyze_image_from_url(url)
            elif content_type == ContentType.VIDEO:
                fingerprints = await self._analyze_video_from_url(url)
            elif content_type == ContentType.AUDIO:
                fingerprints = await self._analyze_audio_from_url(url)
            elif content_type == ContentType.TEXT:
                fingerprints = await self._analyze_text_from_url(url)
            
        except Exception as e:
            logger.warning(f"Could not analyze detected content from {url}: {e}")
        
        return fingerprints
    
    def _detect_content_type(self, url: str) -> ContentType:
        """Detect content type from URL"""
        url_lower = url.lower()
        
        if any(ext in url_lower for ext in ['.jpg', '.jpeg', '.png', '.gif', '.webp']):
            return ContentType.IMAGE
        elif any(ext in url_lower for ext in ['.mp4', '.avi', '.mov', '.webm']):
            return ContentType.VIDEO
        elif any(ext in url_lower for ext in ['.mp3', '.wav', '.flac', '.ogg']):
            return ContentType.AUDIO
        elif 'youtube.com' in url_lower or 'youtu.be' in url_lower:
            return ContentType.VIDEO
        elif 'instagram.com' in url_lower:
            return ContentType.IMAGE  # Could also be video
        elif 'tiktok.com' in url_lower:
            return ContentType.VIDEO
        elif 'spotify.com' in url_lower or 'soundcloud.com' in url_lower:
            return ContentType.AUDIO
        else:
            return ContentType.TEXT
    
    async def _analyze_image_from_url(self, url: str) -> List[FingerprintResult]:
        """Analyze image content from URL"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    if response.status == 200:
                        image_data = await response.read()
                        image = Image.open(io.BytesIO(image_data))
                        
                        # Save temporarily for analysis
                        temp_path = Path(f"/tmp/detected_image_{hashlib.md5(image_data).hexdigest()}.png")
                        image.save(temp_path)
                        
                        # Generate fingerprints
                        from .fingerprint_engine import ImageFingerprinter
                        image_fingerprinter = ImageFingerprinter()
                        
                        fingerprints = []
                        fingerprints.append(await image_fingerprinter.generate_perceptual_fingerprint(temp_path))
                        
                        try:
                            fingerprints.append(await image_fingerprinter.generate_clip_fingerprint(temp_path))
                        except:
                            pass  # CLIP might not be available
                        
                        # Cleanup
                        temp_path.unlink()
                        
                        return fingerprints
        except Exception as e:
            logger.error(f"Error analyzing image from URL: {e}")
        
        return []
    
    async def _analyze_video_from_url(self, url: str) -> List[FingerprintResult]:
        """Analyze video content from URL (placeholder implementation)"""
        # In production, this would download video thumbnails or extract frames
        # For now, return empty list
        logger.info(f"Video analysis for {url} - placeholder implementation")
        return []
    
    async def _analyze_audio_from_url(self, url: str) -> List[FingerprintResult]:
        """Analyze audio content from URL (placeholder implementation)"""
        # In production, this would download audio samples or use platform APIs
        # For now, return empty list
        logger.info(f"Audio analysis for {url} - placeholder implementation")
        return []
    
    async def _analyze_text_from_url(self, url: str) -> List[FingerprintResult]:
        """Analyze text content from URL"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    if response.status == 200:
                        html_content = await response.text()
                        
                        # Extract text content (simplified)
                        from bs4 import BeautifulSoup
                        soup = BeautifulSoup(html_content, 'html.parser')
                        text_content = soup.get_text()
                        
                        # Generate text fingerprints
                        from .fingerprint_engine import TextFingerprinter
                        text_fingerprinter = TextFingerprinter()
                        
                        fingerprints = []
                        fingerprints.append(await text_fingerprinter.generate_semantic_fingerprint(text_content))
                        fingerprints.append(await text_fingerprinter.generate_syntactic_fingerprint(text_content))
                        
                        return fingerprints
        except Exception as e:
            logger.error(f"Error analyzing text from URL: {e}")
        
        return []
    
    async def _compare_fingerprints(self, 
                                  original: FingerprintResult,
                                  detected: FingerprintResult,
                                  config: DetectionConfig) -> Optional[SimilarityScore]:
        """Compare two fingerprints and calculate similarity"""
        try:
            similarity_score = 0.0
            hash_match = False
            vector_similarity = None
            
            # Hash comparison
            if config.enable_hash_matching:
                hash_match = original.hash_value == detected.hash_value
                if hash_match:
                    similarity_score = 1.0
            
            # Vector similarity comparison
            if (config.enable_vector_matching and 
                original.vector_embedding is not None and 
                detected.vector_embedding is not None):
                
                # Ensure same dimensionality
                if len(original.vector_embedding) == len(detected.vector_embedding):
                    vector_sim = cosine_similarity(
                        [original.vector_embedding], 
                        [detected.vector_embedding]
                    )[0][0]
                    vector_similarity = float(vector_sim)
                    
                    # Use vector similarity if no exact hash match
                    if not hash_match:
                        similarity_score = max(similarity_score, vector_similarity)
            
            # Calculate confidence based on fingerprint type
            confidence = self._calculate_confidence(original.fingerprint_type, similarity_score)
            
            return SimilarityScore(
                fingerprint_type=original.fingerprint_type,
                similarity_score=similarity_score,
                hash_match=hash_match,
                vector_similarity=vector_similarity,
                confidence=confidence
            )
            
        except Exception as e:
            logger.error(f"Error comparing fingerprints: {e}")
            return None
    
    def _calculate_confidence(self, fingerprint_type: FingerprintType, similarity: float) -> float:
        """Calculate confidence score based on fingerprint type and similarity"""
        # Different fingerprint types have different reliability
        type_confidence = {
            FingerprintType.AUDIO_CHROMAPRINT: 0.95,
            FingerprintType.AUDIO_SPECTRAL: 0.90,
            FingerprintType.VIDEO_PERCEPTUAL: 0.85,
            FingerprintType.VIDEO_OBJECT: 0.75,
            FingerprintType.IMAGE_PERCEPTUAL: 0.90,
            FingerprintType.IMAGE_CLIP: 0.95,
            FingerprintType.TEXT_SEMANTIC: 0.88,
            FingerprintType.TEXT_SYNTACTIC: 0.80
        }
        
        base_confidence = type_confidence.get(fingerprint_type, 0.75)
        return base_confidence * similarity


class FalsePositiveFilter:
    """Advanced false positive detection and filtering"""
    
    def __init__(self):
        self.whitelist_domains = set()
        self.common_patterns = set()
        self.user_confirmations = {}
    
    async def assess_false_positive_risk(self, evidence: ViolationEvidence) -> float:
        """Assess the risk that a violation is a false positive"""
        risk_factors = []
        
        # Domain-based assessment
        domain_risk = self._assess_domain_risk(evidence.detected_url)
        risk_factors.append(domain_risk)
        
        # Similarity pattern assessment
        pattern_risk = self._assess_similarity_patterns(evidence.similarity_scores)
        risk_factors.append(pattern_risk)
        
        # Metadata assessment
        metadata_risk = self._assess_metadata_risk(evidence.metadata)
        risk_factors.append(metadata_risk)
        
        # Time-based assessment
        temporal_risk = self._assess_temporal_risk(evidence.timestamp)
        risk_factors.append(temporal_risk)
        
        # Calculate overall risk
        total_risk = np.mean(risk_factors)
        
        return min(1.0, max(0.0, total_risk))
    
    def _assess_domain_risk(self, url: str) -> float:
        """Assess false positive risk based on domain"""
        try:
            domain = urlparse(url).netloc.lower()
            
            # Whitelist of known safe domains
            safe_domains = {
                'archive.org', 'wikipedia.org', 'commons.wikimedia.org',
                'creativecommons.org', 'publicdomain.org'
            }
            
            if any(safe_domain in domain for safe_domain in safe_domains):
                return 0.8  # High risk of false positive
            
            # Educational and institutional domains
            if domain.endswith('.edu') or domain.endswith('.gov'):
                return 0.6
            
            return 0.1  # Low risk
            
        except Exception:
            return 0.2
    
    def _assess_similarity_patterns(self, scores: List[SimilarityScore]) -> float:
        """Assess false positive risk based on similarity patterns"""
        if not scores:
            return 0.5
        
        # Check for suspiciously perfect matches across all types
        perfect_matches = sum(1 for score in scores if score.similarity_score > 0.99)
        
        if perfect_matches == len(scores) and len(scores) > 2:
            return 0.7  # Might be same content legitimately used
        
        # Check for very low but consistent similarities
        low_similarities = sum(1 for score in scores if 0.3 < score.similarity_score < 0.6)
        
        if low_similarities == len(scores):
            return 0.6  # Might be coincidental similarities
        
        return 0.2
    
    def _assess_metadata_risk(self, metadata: Dict[str, Any]) -> float:
        """Assess false positive risk based on metadata"""
        risk = 0.0
        
        # Check for attribution indicators
        if any(keyword in str(metadata).lower() for keyword in 
               ['creative commons', 'public domain', 'fair use', 'attribution']):
            risk += 0.4
        
        # Check for educational context
        if any(keyword in str(metadata).lower() for keyword in 
               ['education', 'research', 'academic', 'study']):
            risk += 0.3
        
        return min(1.0, risk)
    
    def _assess_temporal_risk(self, timestamp: datetime) -> float:
        """Assess false positive risk based on timing"""
        # Recent detections might be more legitimate violations
        age_hours = (datetime.utcnow() - timestamp).total_seconds() / 3600
        
        if age_hours < 1:
            return 0.1  # Very recent, likely real violation
        elif age_hours < 24:
            return 0.2  # Recent, probably real
        elif age_hours < 168:  # 1 week
            return 0.3
        else:
            return 0.5  # Older content, higher chance of legitimate use


class ViolationDetector:
    """Main violation detection engine"""
    
    def __init__(self):
        self.similarity_analyzer = SimilarityAnalyzer()
        self.false_positive_filter = FalsePositiveFilter()
        self.fingerprint_engine = FingerprintEngine()
        
        # Detection thresholds by content type
        self.detection_thresholds = {
            ContentType.AUDIO: 0.85,
            ContentType.VIDEO: 0.80,
            ContentType.IMAGE: 0.75,
            ContentType.TEXT: 0.70
        }
    
    async def detect_violations(self, 
                              protected_content_id: str,
                              monitoring_results: List[MonitoringResult],
                              config: DetectionConfig) -> List[ViolationEvidence]:
        """Detect violations from monitoring results"""
        violations = []
        
        try:
            # Get original fingerprints for protected content
            original_fingerprints = await self._get_content_fingerprints(protected_content_id)
            
            if not original_fingerprints:
                logger.warning(f"No fingerprints found for content {protected_content_id}")
                return violations
            
            # Analyze each detected URL
            for result in monitoring_results:
                for url in result.detected_urls:
                    violation = await self._analyze_potential_violation(
                        protected_content_id, url, original_fingerprints, config
                    )
                    
                    if violation:
                        violations.append(violation)
            
            # Sort by severity and similarity
            violations.sort(key=lambda v: (v.severity.value, -max(s.similarity_score for s in v.similarity_scores)))
            
        except Exception as e:
            logger.error(f"Error detecting violations: {e}")
        
        return violations
    
    async def _analyze_potential_violation(self,
                                         protected_content_id: str,
                                         detected_url: str,
                                         original_fingerprints: List[FingerprintResult],
                                         config: DetectionConfig) -> Optional[ViolationEvidence]:
        """Analyze a single potential violation"""
        try:
            # Analyze similarity
            similarity_scores = await self.similarity_analyzer.analyze_similarity(
                original_fingerprints, detected_url, config
            )
            
            if not similarity_scores:
                return None
            
            # Get highest similarity score
            max_similarity = max(s.similarity_score for s in similarity_scores)
            
            # Check if meets threshold
            if max_similarity < config.similarity_threshold:
                return None
            
            # Determine violation type and severity
            violation_type = self._determine_violation_type(similarity_scores, max_similarity)
            severity = self._determine_severity(max_similarity)
            
            # Create violation evidence
            violation_id = hashlib.md5(
                f"{protected_content_id}_{detected_url}_{datetime.utcnow().isoformat()}".encode()
            ).hexdigest()[:16]
            
            violation = ViolationEvidence(
                violation_id=violation_id,
                original_content_id=protected_content_id,
                detected_url=detected_url,
                violation_type=violation_type,
                severity=severity,
                similarity_scores=similarity_scores
            )
            
            # Assess false positive risk
            violation.false_positive_score = await self.false_positive_filter.assess_false_positive_risk(violation)
            
            # Skip if high false positive risk
            if violation.false_positive_score > config.false_positive_threshold:
                logger.info(f"Skipping potential false positive: {violation_id}")
                return None
            
            return violation
            
        except Exception as e:
            logger.error(f"Error analyzing potential violation: {e}")
            return None
    
    def _determine_violation_type(self, scores: List[SimilarityScore], max_similarity: float) -> ViolationType:
        """Determine the type of violation based on similarity scores"""
        if max_similarity > 0.95:
            # Check if exact match
            has_hash_match = any(s.hash_match for s in scores)
            if has_hash_match:
                return ViolationType.EXACT_DUPLICATE
            else:
                return ViolationType.MODIFIED_CONTENT
        
        elif max_similarity > 0.85:
            return ViolationType.DERIVATIVE_WORK
        
        elif max_similarity > 0.70:
            return ViolationType.PARTIAL_USAGE
        
        else:
            return ViolationType.UNAUTHORIZED_REMIX
    
    def _determine_severity(self, similarity: float) -> ViolationSeverity:
        """Determine violation severity based on similarity score"""
        if similarity > 0.95:
            return ViolationSeverity.CRITICAL
        elif similarity > 0.85:
            return ViolationSeverity.HIGH
        elif similarity > 0.70:
            return ViolationSeverity.MEDIUM
        elif similarity > 0.50:
            return ViolationSeverity.LOW
        else:
            return ViolationSeverity.SUSPICIOUS
    
    async def _get_content_fingerprints(self, content_id: str) -> List[FingerprintResult]:
        """Get fingerprints for protected content"""
        # This would typically query the database
        # For now, return empty list as placeholder
        logger.info(f"Getting fingerprints for content {content_id}")
        return []
    
    async def verify_violation(self, violation_id: str, user_confirmation: bool) -> bool:
        """Verify a violation based on user feedback"""
        try:
            # Store user confirmation for learning
            self.false_positive_filter.user_confirmations[violation_id] = {
                'confirmed': user_confirmation,
                'timestamp': datetime.utcnow()
            }
            
            # Update violation status in database
            # This would typically update the database record
            logger.info(f"Violation {violation_id} {'confirmed' if user_confirmation else 'rejected'}")
            
            return True
            
        except Exception as e:
            logger.error(f"Error verifying violation: {e}")
            return False
    
    def get_detection_statistics(self) -> Dict[str, Any]:
        """Get violation detection statistics"""
        return {
            'detection_thresholds': self.detection_thresholds,
            'user_confirmations': len(self.false_positive_filter.user_confirmations),
            'confirmed_violations': sum(1 for conf in self.false_positive_filter.user_confirmations.values() 
                                      if conf['confirmed']),
            'false_positives': sum(1 for conf in self.false_positive_filter.user_confirmations.values() 
                                 if not conf['confirmed']),
            'version': '2.0.0'
        }
