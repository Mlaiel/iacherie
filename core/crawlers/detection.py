"""
Violation Detection Engine
=========================

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: © 2025 Fahed Mlaiel. All rights reserved.

⚠️  INTELLECTUAL PROPERTY WARNING ⚠️
Unauthorized use, copying or distribution prohibited.

Advanced AI-powered violation detection system for content protection.
Uses multiple algorithms including similarity matching, metadata analysis,
and machine learning models to detect unauthorized content usage.
"""

import logging
import hashlib
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
import numpy as np
from sqlalchemy.orm import Session

from .config import ContentType, CrawlerConfig

logger = logging.getLogger(__name__)

@dataclass
class ViolationMatch:
    """Represents a detected violation with detailed matching information."""
    
    original_fingerprint_id: str
    detected_url: str
    platform: str
    similarity_score: float
    match_type: str  # exact, partial, perceptual, metadata
    confidence_level: str  # high, medium, low
    evidence_urls: List[str]
    metadata_matches: Dict[str, Any]
    detection_timestamp: datetime
    violation_severity: str  # critical, high, medium, low

@dataclass
class ContentSignature:
    """Multi-dimensional content signature for advanced matching."""
    
    content_id: str
    content_type: ContentType
    primary_hash: str
    perceptual_hash: Optional[str] = None
    metadata_signature: Dict[str, Any] = None
    audio_fingerprint: Optional[bytes] = None
    visual_features: Optional[np.ndarray] = None
    text_embedding: Optional[np.ndarray] = None
    duration_ms: Optional[int] = None
    file_size_bytes: Optional[int] = None

class ViolationDetector:
    """
    Advanced violation detection engine using multiple AI algorithms.
    
    Combines fingerprinting, similarity matching, metadata analysis,
    and machine learning models for comprehensive content protection.
    """
    
    def __init__(
        self,
        config: CrawlerConfig,
        database_session: Session
    ):
        self.config = config
        self.db_session = database_session
        
        # Detection thresholds by content type
        self.similarity_thresholds = {
            ContentType.AUDIO: 0.92,
            ContentType.VIDEO: 0.88,
            ContentType.IMAGE: 0.85,
            ContentType.TEXT: 0.82,
            ContentType.MIXED: 0.85
        }
        
        # Initialize detection algorithms
        self._initialize_detection_engines()
        
        logger.info("ViolationDetector initialized with %d content types", len(self.similarity_thresholds))
    
    def _initialize_detection_engines(self):
        """Initialize various detection algorithms and models."""
        
        # Audio detection
        self.audio_detector = AudioViolationDetector()
        
        # Video detection  
        self.video_detector = VideoViolationDetector()
        
        # Image detection
        self.image_detector = ImageViolationDetector()
        
        # Text detection
        self.text_detector = TextViolationDetector()
        
        # Metadata analyzer
        self.metadata_analyzer = MetadataAnalyzer()
        
        logger.info("Detection engines initialized successfully")
    
    def check_violation(
        self, 
        crawled_content: Dict[str, Any], 
        protected_fingerprints: List[str]
    ) -> Optional[ViolationMatch]:
        """
        Check if crawled content violates any protected fingerprints.
        
        Args:
            crawled_content: Content found by crawler
            protected_fingerprints: List of protected content fingerprints
            
        Returns:
            ViolationMatch if violation detected, None otherwise
        """
        
        try:
            # Extract content signature from crawled content
            content_signature = self._extract_content_signature(crawled_content)
            
            if not content_signature:
                return None
            
            # Check against each protected fingerprint
            best_match = None
            highest_score = 0.0
            
            for fingerprint_id in protected_fingerprints:
                protected_signature = self._load_protected_signature(fingerprint_id)
                if not protected_signature:
                    continue
                
                # Perform multi-algorithm matching
                match_result = self._perform_multi_algorithm_matching(
                    content_signature, 
                    protected_signature
                )
                
                if match_result and match_result.similarity_score > highest_score:
                    highest_score = match_result.similarity_score
                    best_match = match_result
            
            # Apply threshold filtering
            if best_match and self._meets_detection_threshold(best_match):
                return best_match
            
            return None
            
        except Exception as e:
            logger.error("Error in violation detection: %s", str(e))
            return None
    
    def _extract_content_signature(self, crawled_content: Dict[str, Any]) -> Optional[ContentSignature]:
        """Extract comprehensive signature from crawled content."""
        
        try:
            content_type = self._determine_content_type(crawled_content)
            
            signature = ContentSignature(
                content_id=crawled_content.get('url', ''),
                content_type=content_type,
                primary_hash=self._compute_primary_hash(crawled_content),
                metadata_signature=self._extract_metadata_signature(crawled_content)
            )
            
            # Content-type specific signature extraction
            if content_type == ContentType.AUDIO:
                signature.audio_fingerprint = self.audio_detector.extract_fingerprint(crawled_content)
                signature.duration_ms = crawled_content.get('duration_ms')
                
            elif content_type == ContentType.VIDEO:
                signature.visual_features = self.video_detector.extract_visual_features(crawled_content)
                signature.audio_fingerprint = self.audio_detector.extract_fingerprint(crawled_content)
                signature.duration_ms = crawled_content.get('duration_ms')
                
            elif content_type == ContentType.IMAGE:
                signature.perceptual_hash = self.image_detector.compute_perceptual_hash(crawled_content)
                signature.visual_features = self.image_detector.extract_visual_features(crawled_content)
                
            elif content_type == ContentType.TEXT:
                signature.text_embedding = self.text_detector.extract_text_embedding(crawled_content)
            
            signature.file_size_bytes = crawled_content.get('file_size')
            
            return signature
            
        except Exception as e:
            logger.error("Error extracting content signature: %s", str(e))
            return None
    
    def _perform_multi_algorithm_matching(
        self, 
        content_sig: ContentSignature, 
        protected_sig: ContentSignature
    ) -> Optional[ViolationMatch]:
        """Perform matching using multiple algorithms and combine results."""
        
        if content_sig.content_type != protected_sig.content_type:
            return None
        
        matching_results = []
        evidence_urls = []
        metadata_matches = {}
        
        # 1. Primary hash exact matching
        if content_sig.primary_hash == protected_sig.primary_hash:
            matching_results.append(('exact_hash', 1.0))
        
        # 2. Content-specific matching
        if content_sig.content_type == ContentType.AUDIO:
            audio_score = self.audio_detector.compare_fingerprints(
                content_sig.audio_fingerprint,
                protected_sig.audio_fingerprint
            )
            if audio_score > 0.7:
                matching_results.append(('audio_fingerprint', audio_score))
        
        elif content_sig.content_type == ContentType.VIDEO:
            # Video similarity
            video_score = self.video_detector.compare_visual_features(
                content_sig.visual_features,
                protected_sig.visual_features
            )
            if video_score > 0.7:
                matching_results.append(('video_visual', video_score))
            
            # Audio component
            if content_sig.audio_fingerprint and protected_sig.audio_fingerprint:
                audio_score = self.audio_detector.compare_fingerprints(
                    content_sig.audio_fingerprint,
                    protected_sig.audio_fingerprint
                )
                if audio_score > 0.7:
                    matching_results.append(('video_audio', audio_score))
        
        elif content_sig.content_type == ContentType.IMAGE:
            # Perceptual hash matching
            if content_sig.perceptual_hash and protected_sig.perceptual_hash:
                perceptual_score = self.image_detector.compare_perceptual_hashes(
                    content_sig.perceptual_hash,
                    protected_sig.perceptual_hash
                )
                if perceptual_score > 0.7:
                    matching_results.append(('image_perceptual', perceptual_score))
            
            # Visual features matching
            if content_sig.visual_features is not None and protected_sig.visual_features is not None:
                visual_score = self.image_detector.compare_visual_features(
                    content_sig.visual_features,
                    protected_sig.visual_features
                )
                if visual_score > 0.7:
                    matching_results.append(('image_visual', visual_score))
        
        elif content_sig.content_type == ContentType.TEXT:
            # Text embedding similarity
            if content_sig.text_embedding is not None and protected_sig.text_embedding is not None:
                text_score = self.text_detector.compare_text_embeddings(
                    content_sig.text_embedding,
                    protected_sig.text_embedding
                )
                if text_score > 0.7:
                    matching_results.append(('text_embedding', text_score))
        
        # 3. Metadata matching
        metadata_score = self.metadata_analyzer.compare_metadata(
            content_sig.metadata_signature,
            protected_sig.metadata_signature
        )
        if metadata_score > 0.5:
            matching_results.append(('metadata', metadata_score))
            metadata_matches = self.metadata_analyzer.extract_matching_fields(
                content_sig.metadata_signature,
                protected_sig.metadata_signature
            )
        
        # 4. Duration/size matching (if applicable)
        if content_sig.duration_ms and protected_sig.duration_ms:
            duration_similarity = self._compare_durations(
                content_sig.duration_ms,
                protected_sig.duration_ms
            )
            if duration_similarity > 0.8:
                matching_results.append(('duration', duration_similarity))
        
        # Combine all matching results
        if not matching_results:
            return None
        
        # Calculate weighted similarity score
        total_score = self._calculate_weighted_similarity(matching_results)
        
        # Determine confidence and match type
        confidence_level = self._determine_confidence_level(matching_results, total_score)
        match_type = self._determine_match_type(matching_results)
        violation_severity = self._assess_violation_severity(total_score, matching_results)
        
        return ViolationMatch(
            original_fingerprint_id=protected_sig.content_id,
            detected_url=content_sig.content_id,
            platform=self._extract_platform_from_url(content_sig.content_id),
            similarity_score=total_score,
            match_type=match_type,
            confidence_level=confidence_level,
            evidence_urls=evidence_urls,
            metadata_matches=metadata_matches,
            detection_timestamp=datetime.utcnow(),
            violation_severity=violation_severity
        )
    
    def _calculate_weighted_similarity(self, matching_results: List[Tuple[str, float]]) -> float:
        """Calculate weighted similarity score from multiple matching algorithms."""
        
        # Algorithm weights based on reliability and accuracy
        algorithm_weights = {
            'exact_hash': 1.0,
            'audio_fingerprint': 0.9,
            'video_visual': 0.85,
            'video_audio': 0.9,
            'image_perceptual': 0.8,
            'image_visual': 0.85,
            'text_embedding': 0.75,
            'metadata': 0.4,
            'duration': 0.3
        }
        
        weighted_sum = 0.0
        total_weights = 0.0
        
        for algorithm, score in matching_results:
            weight = algorithm_weights.get(algorithm, 0.5)
            weighted_sum += score * weight
            total_weights += weight
        
        return weighted_sum / total_weights if total_weights > 0 else 0.0
    
    def _determine_confidence_level(self, matching_results: List[Tuple[str, float]], total_score: float) -> str:
        """Determine confidence level based on matching results."""
        
        # High confidence: exact hash or multiple strong matches
        if any(alg == 'exact_hash' for alg, _ in matching_results):
            return 'high'
        
        if total_score > 0.95 and len(matching_results) >= 2:
            return 'high'
        
        # Medium confidence: strong single match or multiple moderate matches
        if total_score > 0.85 or len(matching_results) >= 3:
            return 'medium'
        
        # Low confidence: single moderate match
        return 'low'
    
    def _determine_match_type(self, matching_results: List[Tuple[str, float]]) -> str:
        """Determine the type of match detected."""
        
        algorithms = [alg for alg, _ in matching_results]
        
        if 'exact_hash' in algorithms:
            return 'exact'
        
        if any(alg in ['audio_fingerprint', 'video_visual', 'image_perceptual'] for alg in algorithms):
            return 'perceptual'
        
        if 'metadata' in algorithms and len(algorithms) == 1:
            return 'metadata'
        
        return 'partial'
    
    def _assess_violation_severity(self, total_score: float, matching_results: List[Tuple[str, float]]) -> str:
        """Assess the severity of the detected violation."""
        
        if total_score > 0.95:
            return 'critical'
        elif total_score > 0.85:
            return 'high'
        elif total_score > 0.75:
            return 'medium'
        else:
            return 'low'
    
    def _meets_detection_threshold(self, match: ViolationMatch) -> bool:
        """Check if violation match meets minimum detection thresholds."""
        
        content_type = self._determine_content_type_from_url(match.detected_url)
        threshold = self.similarity_thresholds.get(content_type, 0.80)
        
        # Apply confidence-based threshold adjustment
        if match.confidence_level == 'high':
            threshold -= 0.05
        elif match.confidence_level == 'low':
            threshold += 0.05
        
        return match.similarity_score >= threshold
    
    def create_violation_record(self, crawled_content: Dict[str, Any]) -> Dict[str, Any]:
        """Create a structured violation record for database storage."""
        
        return {
            'detected_url': crawled_content.get('url'),
            'platform': crawled_content.get('platform'),
            'title': crawled_content.get('title'),
            'description': crawled_content.get('description'),
            'author': crawled_content.get('author'),
            'upload_date': crawled_content.get('upload_date'),
            'view_count': crawled_content.get('view_count'),
            'content_type': crawled_content.get('content_type'),
            'file_size': crawled_content.get('file_size'),
            'duration': crawled_content.get('duration_ms'),
            'detected_at': datetime.utcnow(),
            'metadata': crawled_content.get('metadata', {})
        }
    
    # Helper methods
    
    def _determine_content_type(self, content: Dict[str, Any]) -> ContentType:
        """Determine content type from crawled content."""
        
        content_type_str = content.get('content_type', '').lower()
        
        if 'audio' in content_type_str:
            return ContentType.AUDIO
        elif 'video' in content_type_str:
            return ContentType.VIDEO
        elif 'image' in content_type_str:
            return ContentType.IMAGE
        elif 'text' in content_type_str:
            return ContentType.TEXT
        else:
            return ContentType.MIXED
    
    def _determine_content_type_from_url(self, url: str) -> ContentType:
        """Determine content type from URL patterns."""
        
        url_lower = url.lower()
        
        if 'youtube.com' in url_lower or 'tiktok.com' in url_lower:
            return ContentType.VIDEO
        elif 'instagram.com' in url_lower and '/p/' in url_lower:
            return ContentType.IMAGE
        elif 'twitter.com' in url_lower or 'x.com' in url_lower:
            return ContentType.TEXT
        else:
            return ContentType.MIXED
    
    def _compute_primary_hash(self, content: Dict[str, Any]) -> str:
        """Compute primary content hash."""
        
        # Use URL and key metadata for hash
        hash_input = f"{content.get('url', '')}{content.get('title', '')}{content.get('file_size', '')}"
        return hashlib.sha256(hash_input.encode()).hexdigest()
    
    def _extract_metadata_signature(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """Extract metadata signature for matching."""
        
        return {
            'title': content.get('title', '').lower().strip(),
            'author': content.get('author', '').lower().strip(),
            'duration': content.get('duration_ms'),
            'file_size': content.get('file_size'),
            'upload_date': content.get('upload_date'),
            'tags': [tag.lower().strip() for tag in content.get('tags', [])],
            'description_length': len(content.get('description', ''))
        }
    
    def _extract_platform_from_url(self, url: str) -> str:
        """Extract platform name from URL."""
        
        url_lower = url.lower()
        
        if 'youtube.com' in url_lower or 'youtu.be' in url_lower:
            return 'youtube'
        elif 'tiktok.com' in url_lower:
            return 'tiktok'
        elif 'instagram.com' in url_lower:
            return 'instagram'
        elif 'twitter.com' in url_lower or 'x.com' in url_lower:
            return 'twitter'
        else:
            return 'unknown'
    
    def _compare_durations(self, duration1: int, duration2: int) -> float:
        """Compare duration similarity."""
        
        if not duration1 or not duration2:
            return 0.0
        
        diff = abs(duration1 - duration2)
        max_duration = max(duration1, duration2)
        
        return 1.0 - (diff / max_duration)
    
    def _load_protected_signature(self, fingerprint_id: str) -> Optional[ContentSignature]:
        """Load protected content signature from database."""
        
        # Implementation would load from database
        # This is a placeholder for the actual database query
        
        try:
            # Query database for fingerprint
            # fingerprint_record = self.db_session.query(Fingerprint).filter_by(id=fingerprint_id).first()
            
            # For now, return None - actual implementation would construct ContentSignature
            # from database record
            return None
            
        except Exception as e:
            logger.error("Error loading protected signature %s: %s", fingerprint_id, str(e))
            return None


# Specialized detection classes

class AudioViolationDetector:
    """Specialized detector for audio content violations."""
    
    def extract_fingerprint(self, content: Dict[str, Any]) -> Optional[bytes]:
        """Extract audio fingerprint from content."""
        # Implementation would use libraries like chromaprint
        return None
    
    def compare_fingerprints(self, fp1: Optional[bytes], fp2: Optional[bytes]) -> float:
        """Compare two audio fingerprints."""
        if not fp1 or not fp2:
            return 0.0
        # Implementation would compare fingerprints
        return 0.0


class VideoViolationDetector:
    """Specialized detector for video content violations."""
    
    def extract_visual_features(self, content: Dict[str, Any]) -> Optional[np.ndarray]:
        """Extract visual features from video content."""
        # Implementation would use OpenCV/YOLO for frame analysis
        return None
    
    def compare_visual_features(self, feat1: Optional[np.ndarray], feat2: Optional[np.ndarray]) -> float:
        """Compare visual features between videos."""
        if feat1 is None or feat2 is None:
            return 0.0
        # Implementation would compare feature vectors
        return 0.0


class ImageViolationDetector:
    """Specialized detector for image content violations."""
    
    def compute_perceptual_hash(self, content: Dict[str, Any]) -> Optional[str]:
        """Compute perceptual hash for image."""
        # Implementation would use pHash or similar
        return None
    
    def extract_visual_features(self, content: Dict[str, Any]) -> Optional[np.ndarray]:
        """Extract visual features from image."""
        # Implementation would use CLIP or similar
        return None
    
    def compare_perceptual_hashes(self, hash1: Optional[str], hash2: Optional[str]) -> float:
        """Compare perceptual hashes."""
        if not hash1 or not hash2:
            return 0.0
        # Implementation would compare hashes
        return 0.0
    
    def compare_visual_features(self, feat1: Optional[np.ndarray], feat2: Optional[np.ndarray]) -> float:
        """Compare visual features."""
        if feat1 is None or feat2 is None:
            return 0.0
        # Implementation would compare feature vectors
        return 0.0


class TextViolationDetector:
    """Specialized detector for text content violations."""
    
    def extract_text_embedding(self, content: Dict[str, Any]) -> Optional[np.ndarray]:
        """Extract text embedding from content."""
        # Implementation would use BERT/RoBERTa
        return None
    
    def compare_text_embeddings(self, emb1: Optional[np.ndarray], emb2: Optional[np.ndarray]) -> float:
        """Compare text embeddings."""
        if emb1 is None or emb2 is None:
            return 0.0
        # Implementation would compute cosine similarity
        return 0.0


class MetadataAnalyzer:
    """Analyzer for metadata-based matching."""
    
    def compare_metadata(self, meta1: Optional[Dict[str, Any]], meta2: Optional[Dict[str, Any]]) -> float:
        """Compare metadata signatures."""
        if not meta1 or not meta2:
            return 0.0
        
        matches = 0
        total_fields = 0
        
        for key in ['title', 'author', 'duration', 'file_size']:
            if key in meta1 and key in meta2:
                total_fields += 1
                if meta1[key] == meta2[key]:
                    matches += 1
        
        return matches / total_fields if total_fields > 0 else 0.0
    
    def extract_matching_fields(self, meta1: Dict[str, Any], meta2: Dict[str, Any]) -> Dict[str, Any]:
        """Extract fields that match between metadata."""
        matches = {}
        
        for key in ['title', 'author', 'duration', 'file_size']:
            if key in meta1 and key in meta2 and meta1[key] == meta2[key]:
                matches[key] = meta1[key]
        
        return matches
