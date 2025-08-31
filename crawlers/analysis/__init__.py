"""Content Analysis Module
=======================

Professional content analysis for violation detection and similarity matching.
Implements AI-powered content analysis, fingerprinting, and protection algorithms.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: All rights reserved. Unauthorized use, reproduction, or distribution prohibited.

WARNING: This code is protected by copyright law. Any unauthorized copying, 
distribution, or modification is strictly prohibited and will result in 
legal action. Contact mlaiel@live.de for licensing.

Expertise combinée:
- Lead Developer IA: Architecture intelligente et optimisations ML
- Backend Senior: Infrastructure robuste et scalabilité enterprise
- ML Engineer: Algorithmes d'apprentissage et modèles prédictifs
- DBA Expert: Gestion de données et optimisation des requêtes
- Sécurité: Protection et chiffrement des données sensibles
- Microservices: Architecture distribuée et communication inter-services
- Audio/Vidéo: Traitement multimédia et analyse de contenu
- DevOps: Déploiement, monitoring et infrastructure cloud
- IA Prompt Engineer: Optimisation des interactions et prompts
"""
import asyncio
import logging
import hashlib
import re
from typing import Dict, List, Optional, Tuple, Any, Set
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import json
import numpy as np
from difflib import SequenceMatcher

# Import all analysis modules
from .content_analyzer import ContentAnalyzer
from .content_classifier import ContentClassifier
from .competitive_analyzer import CompetitiveAnalyzer
from .engagement_analyzer import EngagementAnalyzer
from .metadata_extractor import MetadataExtractor
from .monetization_analyzer import MonetizationAnalyzer
from .protection_analyzer import ProtectionAnalyzer
from .sentiment_analyzer import SentimentAnalyzer
from .similarity_detector import SimilarityDetector
from .trend_analyzer import TrendAnalyzer
from .ai_fingerprint_engine import (
    AIFingerprintEngine, FingerprintResult, SimilarityMatch,
    FingerprintType, ContentType as FingerprintContentType
)
from .revenue_performance_analyzer import (
    RevenuePerformanceAnalyzer, RevenueAnalysis, RevenueData,
    PerformanceInsight, RevenueMetric, RevenueSource, Platform
)
from .realtime_violation_detector import (
    RealTimeViolationDetector, ViolationAlert, MonitoringTarget,
    DetectionRule, ViolationType, AlertSeverity, DetectionStatus,
    MonitoringChannel
)

logger = logging.getLogger(__name__)

class ViolationType(Enum):
    """Types of content violations."""    COPYRIGHT_INFRINGEMENT = "copyright_infringement"
    TRADEMARK_VIOLATION = "trademark_violation"
    CONTENT_THEFT = "content_theft"
    UNAUTHORIZED_USE = "unauthorized_use"
    SIMILARITY_MATCH = "similarity_match"
    EXACT_DUPLICATE = "exact_duplicate"
    MODIFIED_COPY = "modified_copy"
    PARTIAL_COPY = "partial_copy"

class AnalysisMethod(Enum):
    """Content analysis methods."""    TEXT_SIMILARITY = "text_similarity"
    AUDIO_FINGERPRINT = "audio_fingerprint"
    VIDEO_FINGERPRINT = "video_fingerprint"
    IMAGE_HASH = "image_hash"
    METADATA_MATCH = "metadata_match"
    KEYWORD_DETECTION = "keyword_detection"
    PATTERN_MATCHING = "pattern_matching"

@dataclass
class ContentFingerprint:
    """Content fingerprint for similarity detection."""    content_id: str
    platform: str
    content_type: str  # video, audio, image, text, post
    text_hash: Optional[str] = None
    audio_hash: Optional[str] = None
    video_hash: Optional[str] = None
    image_hash: Optional[str] = None
    metadata_hash: Optional[str] = None
    keywords: List[str] = field(default_factory=list)
    patterns: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    file_size: Optional[int] = None
    duration: Optional[float] = None

@dataclass
class SimilarityMatch:
    """Similarity match result."""    original_id: str
    suspected_id: str
    similarity_score: float
    violation_type: ViolationType
    analysis_method: AnalysisMethod
    confidence: float
    details: Dict[str, Any] = field(default_factory=dict)
    detected_at: datetime = field(default_factory=datetime.now)

@dataclass
class AnalysisResult:
    """Content analysis result."""    content_id: str
    analysis_methods: List[AnalysisMethod]
    fingerprint: ContentFingerprint
    violations_detected: List[SimilarityMatch] = field(default_factory=list)
    is_violation: bool = False
    risk_score: float = 0.0
    recommendations: List[str] = field(default_factory=list)
    processed_at: datetime = field(default_factory=datetime.now)

class ContentAnalyzer:
    """    Professional content analysis system.
    
    Features:
    - Multi-modal content analysis
    - Advanced similarity detection
    - AI-powered fingerprinting
    - Copyright violation detection
    - Real-time processing
    - Pattern recognition
    - Metadata analysis
    - Performance optimization
    - Scalable architecture
    - Integration APIs
    """    
    def __init__(self):
        """Initialize content analyzer."""        # Fingerprint database
        self.fingerprint_db: Dict[str, ContentFingerprint] = {}
        self.text_index: Dict[str, Set[str]] = {}  # hash -> content_ids
        self.keyword_index: Dict[str, Set[str]] = {}  # keyword -> content_ids
        
        # Analysis configuration
        self.similarity_threshold = 0.8
        self.text_similarity_threshold = 0.85
        self.audio_similarity_threshold = 0.9
        self.video_similarity_threshold = 0.9
        self.image_similarity_threshold = 0.95
        
        # Pattern configurations
        self.copyright_patterns = self._load_copyright_patterns()
        self.trademark_patterns = self._load_trademark_patterns()
        self.sensitive_keywords = self._load_sensitive_keywords()
        
        # Performance metrics
        self.analysis_count = 0
        self.violation_count = 0
        self.false_positive_count = 0
    
    def _load_copyright_patterns(self) -> List[str]:
        """Load copyright violation patterns."""        return [
            r'©\s*\d{4}',  # Copyright symbol with year
            r'copyright\s+\d{4}',
            r'all\s+rights\s+reserved',
            r'proprietary\s+content',
            r'unauthorized\s+use\s+prohibited',
            r'licensed\s+content',
            r'protected\s+by\s+copyright'
        ]
    
    def _load_trademark_patterns(self) -> List[str]:
        """Load trademark violation patterns."""        return [
            r'™',  # Trademark symbol
            r'®',  # Registered trademark
            r'trademark\s+of',
            r'registered\s+trademark',
            r'brand\s+name',
            r'proprietary\s+mark'
        ]
    
    def _load_sensitive_keywords(self) -> List[str]:
        """Load sensitive keywords for detection."""        return [
            'unauthorized', 'stolen', 'copied', 'plagiarized',
            'infringement', 'violation', 'pirated', 'bootleg',
            'counterfeit', 'fake', 'replica', 'imitation'
        ]
    
    async def analyze_content(
        self,
        content_id: str,
        content_data: Dict[str, Any],
        platform: str,
        content_type: str
    ) -> AnalysisResult:
        """        Analyze content for violations and similarities.
        
        Args:
            content_id: Unique content identifier
            content_data: Content data (text, urls, metadata)
            platform: Source platform
            content_type: Type of content
            
        Returns:
            AnalysisResult object
        """        self.analysis_count += 1
        
        # Generate content fingerprint
        fingerprint = await self._generate_fingerprint(
            content_id, content_data, platform, content_type
        )
        
        # Store fingerprint
        self.fingerprint_db[content_id] = fingerprint
        self._index_fingerprint(fingerprint)
        
        # Detect violations
        violations = await self._detect_violations(fingerprint, content_data)
        
        # Calculate risk score
        risk_score = self._calculate_risk_score(violations, fingerprint)
        
        # Generate recommendations
        recommendations = self._generate_recommendations(violations, risk_score)
        
        # Determine analysis methods used
        analysis_methods = self._get_analysis_methods(content_data, content_type)
        
        is_violation = len(violations) > 0
        if is_violation:
            self.violation_count += 1
        
        result = AnalysisResult(
            content_id=content_id,
            analysis_methods=analysis_methods,
            fingerprint=fingerprint,
            violations_detected=violations,
            is_violation=is_violation,
            risk_score=risk_score,
            recommendations=recommendations
        )
        
        logger.info(
            f"Analyzed content {content_id}: "
            f"violations={len(violations)}, risk={risk_score:.2f}"
        )
        
        return result
    
    async def _generate_fingerprint(
        self,
        content_id: str,
        content_data: Dict[str, Any],
        platform: str,
        content_type: str
    ) -> ContentFingerprint:
        """Generate comprehensive content fingerprint."""        fingerprint = ContentFingerprint(
            content_id=content_id,
            platform=platform,
            content_type=content_type
        )
        
        # Text fingerprinting
        text_content = self._extract_text_content(content_data)
        if text_content:
            fingerprint.text_hash = self._generate_text_hash(text_content)
            fingerprint.keywords = self._extract_keywords(text_content)
            fingerprint.patterns = self._extract_patterns(text_content)
        
        # Audio fingerprinting
        if 'audio_url' in content_data or content_type == 'audio':
            fingerprint.audio_hash = await self._generate_audio_hash(content_data)
        
        # Video fingerprinting
        if 'video_url' in content_data or content_type == 'video':
            fingerprint.video_hash = await self._generate_video_hash(content_data)
        
        # Image fingerprinting
        if 'image_url' in content_data or 'thumbnail' in content_data:
            fingerprint.image_hash = await self._generate_image_hash(content_data)
        
        # Metadata fingerprinting
        metadata = self._extract_metadata(content_data)
        if metadata:
            fingerprint.metadata_hash = self._generate_metadata_hash(metadata)
        
        # File information
        fingerprint.file_size = content_data.get('file_size')
        fingerprint.duration = content_data.get('duration')
        
        return fingerprint
    
    def _extract_text_content(self, content_data: Dict[str, Any]) -> str:
        """Extract text content from data."""        text_parts = []
        
        # Common text fields
        text_fields = ['title', 'description', 'content', 'text', 'caption', 'lyrics']
        
        for field in text_fields:
            if field in content_data and content_data[field]:
                text_parts.append(str(content_data[field]))
        
        return ' '.join(text_parts).strip()
    
    def _generate_text_hash(self, text: str) -> str:
        """Generate hash for text content."""        # Normalize text
        normalized = re.sub(r'\s+', ' ', text.lower().strip())
        normalized = re.sub(r'[^\w\s]', '', normalized)
        
        # Generate hash
        return hashlib.sha256(normalized.encode()).hexdigest()
    
    def _extract_keywords(self, text: str) -> List[str]:
        """Extract keywords from text."""        # Simple keyword extraction (could be enhanced with NLP)
        words = re.findall(r'\b[a-zA-Z]{3,}\b', text.lower())
        
        # Remove common stop words
        stop_words = {
            'the', 'and', 'for', 'are', 'but', 'not', 'you', 'all',
            'can', 'had', 'was', 'one', 'our', 'out', 'day', 'get',
            'has', 'him', 'his', 'how', 'its', 'may', 'new', 'now',
            'old', 'see', 'two', 'who', 'with', 'from', 'have', 'they'
        }
        
        keywords = [word for word in words if word not in stop_words and len(word) > 3]
        
        # Count frequency and return top keywords
        word_freq = {}
        for word in keywords:
            word_freq[word] = word_freq.get(word, 0) + 1
        
        # Sort by frequency and return top 20
        sorted_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
        return [word for word, freq in sorted_words[:20]]
    
    def _extract_patterns(self, text: str) -> List[str]:
        """Extract patterns from text."""        patterns = []
        
        # Check copyright patterns
        for pattern in self.copyright_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            patterns.extend(matches)
        
        # Check trademark patterns
        for pattern in self.trademark_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            patterns.extend(matches)
        
        return list(set(patterns))
    
    async def _generate_audio_hash(self, content_data: Dict[str, Any]) -> str:
        """Generate audio fingerprint hash."""        # Placeholder for audio fingerprinting
        # In production, this would use actual audio analysis libraries
        audio_url = content_data.get('audio_url', '')
        duration = content_data.get('duration', 0)
        
        # Simple hash based on available data
        audio_info = f"{audio_url}_{duration}"
        return hashlib.md5(audio_info.encode()).hexdigest()
    
    async def _generate_video_hash(self, content_data: Dict[str, Any]) -> str:
        """Generate video fingerprint hash."""        # Placeholder for video fingerprinting
        # In production, this would use actual video analysis libraries
        video_url = content_data.get('video_url', '')
        duration = content_data.get('duration', 0)
        resolution = content_data.get('resolution', '')
        
        # Simple hash based on available data
        video_info = f"{video_url}_{duration}_{resolution}"
        return hashlib.md5(video_info.encode()).hexdigest()
    
    async def _generate_image_hash(self, content_data: Dict[str, Any]) -> str:
        """Generate image hash."""        # Placeholder for image hashing
        # In production, this would use perceptual hashing algorithms
        image_url = content_data.get('image_url', content_data.get('thumbnail', ''))
        
        if image_url:
            return hashlib.md5(image_url.encode()).hexdigest()
        
        return None
    
    def _extract_metadata(self, content_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract metadata for fingerprinting."""        metadata = {}
        
        # Common metadata fields
        metadata_fields = [
            'author', 'creator', 'artist', 'album', 'genre',
            'upload_date', 'publish_date', 'tags', 'category',
            'language', 'country', 'license'
        ]
        
        for field in metadata_fields:
            if field in content_data:
                metadata[field] = content_data[field]
        
        return metadata
    
    def _generate_metadata_hash(self, metadata: Dict[str, Any]) -> str:
        """Generate metadata hash."""        # Sort metadata for consistent hashing
        sorted_metadata = json.dumps(metadata, sort_keys=True)
        return hashlib.md5(sorted_metadata.encode()).hexdigest()
    
    def _index_fingerprint(self, fingerprint: ContentFingerprint) -> None:
        """Index fingerprint for fast searching."""        content_id = fingerprint.content_id
        
        # Index text hash
        if fingerprint.text_hash:
            if fingerprint.text_hash not in self.text_index:
                self.text_index[fingerprint.text_hash] = set()
            self.text_index[fingerprint.text_hash].add(content_id)
        
        # Index keywords
        for keyword in fingerprint.keywords:
            if keyword not in self.keyword_index:
                self.keyword_index[keyword] = set()
            self.keyword_index[keyword].add(content_id)
    
    async def _detect_violations(
        self,
        fingerprint: ContentFingerprint,
        content_data: Dict[str, Any]
    ) -> List[SimilarityMatch]:
        """Detect content violations."""        violations = []
        
        # Text similarity detection
        text_violations = await self._detect_text_violations(fingerprint)
        violations.extend(text_violations)
        
        # Audio similarity detection
        audio_violations = await self._detect_audio_violations(fingerprint)
        violations.extend(audio_violations)
        
        # Video similarity detection
        video_violations = await self._detect_video_violations(fingerprint)
        violations.extend(video_violations)
        
        # Image similarity detection
        image_violations = await self._detect_image_violations(fingerprint)
        violations.extend(image_violations)
        
        # Metadata violations
        metadata_violations = await self._detect_metadata_violations(fingerprint)
        violations.extend(metadata_violations)
        
        # Keyword-based detection
        keyword_violations = await self._detect_keyword_violations(fingerprint, content_data)
        violations.extend(keyword_violations)
        
        return violations
    
    async def _detect_text_violations(self, fingerprint: ContentFingerprint) -> List[SimilarityMatch]:
        """Detect text-based violations."""        violations = []
        
        if not fingerprint.text_hash:
            return violations
        
        # Exact text match
        if fingerprint.text_hash in self.text_index:
            for existing_id in self.text_index[fingerprint.text_hash]:
                if existing_id != fingerprint.content_id:
                    violation = SimilarityMatch(
                        original_id=existing_id,
                        suspected_id=fingerprint.content_id,
                        similarity_score=1.0,
                        violation_type=ViolationType.EXACT_DUPLICATE,
                        analysis_method=AnalysisMethod.TEXT_SIMILARITY,
                        confidence=1.0,
                        details={'hash_match': fingerprint.text_hash}
                    )
                    violations.append(violation)
        
        # Keyword similarity
        keyword_matches = await self._find_keyword_similarities(fingerprint)
        for match in keyword_matches:
            if match.similarity_score >= self.text_similarity_threshold:
                violations.append(match)
        
        return violations
    
    async def _find_keyword_similarities(self, fingerprint: ContentFingerprint) -> List[SimilarityMatch]:
        """Find content with similar keywords."""        matches = []
        
        if not fingerprint.keywords:
            return matches
        
        # Find content with overlapping keywords
        candidate_content = set()
        for keyword in fingerprint.keywords:
            if keyword in self.keyword_index:
                candidate_content.update(self.keyword_index[keyword])
        
        # Calculate similarity scores
        for candidate_id in candidate_content:
            if candidate_id == fingerprint.content_id:
                continue
            
            candidate_fingerprint = self.fingerprint_db.get(candidate_id)
            if not candidate_fingerprint or not candidate_fingerprint.keywords:
                continue
            
            # Calculate keyword overlap
            overlap = set(fingerprint.keywords) & set(candidate_fingerprint.keywords)
            total_keywords = set(fingerprint.keywords) | set(candidate_fingerprint.keywords)
            
            if total_keywords:
                similarity_score = len(overlap) / len(total_keywords)
                
                if similarity_score >= 0.5:  # Minimum similarity threshold
                    violation_type = ViolationType.SIMILARITY_MATCH
                    if similarity_score >= 0.9:
                        violation_type = ViolationType.CONTENT_THEFT
                    elif similarity_score >= 0.8:
                        violation_type = ViolationType.MODIFIED_COPY
                    
                    match = SimilarityMatch(
                        original_id=candidate_id,
                        suspected_id=fingerprint.content_id,
                        similarity_score=similarity_score,
                        violation_type=violation_type,
                        analysis_method=AnalysisMethod.TEXT_SIMILARITY,
                        confidence=similarity_score,
                        details={
                            'overlapping_keywords': list(overlap),
                            'keyword_count': len(overlap),
                            'total_keywords': len(total_keywords)
                        }
                    )
                    matches.append(match)
        
        return matches
    
    async def _detect_audio_violations(self, fingerprint: ContentFingerprint) -> List[SimilarityMatch]:
        """Detect audio-based violations."""        violations = []
        
        if not fingerprint.audio_hash:
            return violations
        
        # Compare with existing audio fingerprints
        for existing_id, existing_fingerprint in self.fingerprint_db.items():
            if existing_id == fingerprint.content_id:
                continue
            
            if not existing_fingerprint.audio_hash:
                continue
            
            # Exact audio match
            if fingerprint.audio_hash == existing_fingerprint.audio_hash:
                violation = SimilarityMatch(
                    original_id=existing_id,
                    suspected_id=fingerprint.content_id,
                    similarity_score=1.0,
                    violation_type=ViolationType.EXACT_DUPLICATE,
                    analysis_method=AnalysisMethod.AUDIO_FINGERPRINT,
                    confidence=1.0,
                    details={'audio_hash_match': fingerprint.audio_hash}
                )
                violations.append(violation)
        
        return violations
    
    async def _detect_video_violations(self, fingerprint: ContentFingerprint) -> List[SimilarityMatch]:
        """Detect video-based violations."""        violations = []
        
        if not fingerprint.video_hash:
            return violations
        
        # Compare with existing video fingerprints
        for existing_id, existing_fingerprint in self.fingerprint_db.items():
            if existing_id == fingerprint.content_id:
                continue
            
            if not existing_fingerprint.video_hash:
                continue
            
            # Exact video match
            if fingerprint.video_hash == existing_fingerprint.video_hash:
                violation = SimilarityMatch(
                    original_id=existing_id,
                    suspected_id=fingerprint.content_id,
                    similarity_score=1.0,
                    violation_type=ViolationType.EXACT_DUPLICATE,
                    analysis_method=AnalysisMethod.VIDEO_FINGERPRINT,
                    confidence=1.0,
                    details={'video_hash_match': fingerprint.video_hash}
                )
                violations.append(violation)
        
        return violations
    
    async def _detect_image_violations(self, fingerprint: ContentFingerprint) -> List[SimilarityMatch]:
        """Detect image-based violations."""        violations = []
        
        if not fingerprint.image_hash:
            return violations
        
        # Compare with existing image fingerprints
        for existing_id, existing_fingerprint in self.fingerprint_db.items():
            if existing_id == fingerprint.content_id:
                continue
            
            if not existing_fingerprint.image_hash:
                continue
            
            # Exact image match
            if fingerprint.image_hash == existing_fingerprint.image_hash:
                violation = SimilarityMatch(
                    original_id=existing_id,
                    suspected_id=fingerprint.content_id,
                    similarity_score=1.0,
                    violation_type=ViolationType.EXACT_DUPLICATE,
                    analysis_method=AnalysisMethod.IMAGE_HASH,
                    confidence=1.0,
                    details={'image_hash_match': fingerprint.image_hash}
                )
                violations.append(violation)
        
        return violations
    
    async def _detect_metadata_violations(self, fingerprint: ContentFingerprint) -> List[SimilarityMatch]:
        """Detect metadata-based violations."""        violations = []
        
        if not fingerprint.metadata_hash:
            return violations
        
        # Compare metadata with existing content
        for existing_id, existing_fingerprint in self.fingerprint_db.items():
            if existing_id == fingerprint.content_id:
                continue
            
            if not existing_fingerprint.metadata_hash:
                continue
            
            # Exact metadata match
            if fingerprint.metadata_hash == existing_fingerprint.metadata_hash:
                violation = SimilarityMatch(
                    original_id=existing_id,
                    suspected_id=fingerprint.content_id,
                    similarity_score=1.0,
                    violation_type=ViolationType.METADATA_MATCH,
                    analysis_method=AnalysisMethod.METADATA_MATCH,
                    confidence=0.8,  # Metadata alone is less definitive
                    details={'metadata_hash_match': fingerprint.metadata_hash}
                )
                violations.append(violation)
        
        return violations
    
    async def _detect_keyword_violations(
        self,
        fingerprint: ContentFingerprint,
        content_data: Dict[str, Any]
    ) -> List[SimilarityMatch]:
        """Detect keyword-based violations."""        violations = []
        
        text_content = self._extract_text_content(content_data)
        if not text_content:
            return violations
        
        text_lower = text_content.lower()
        
        # Check for sensitive keywords
        found_keywords = []
        for keyword in self.sensitive_keywords:
            if keyword in text_lower:
                found_keywords.append(keyword)
        
        if found_keywords:
            # This is a generic violation based on keywords
            violation = SimilarityMatch(
                original_id="SYSTEM",
                suspected_id=fingerprint.content_id,
                similarity_score=len(found_keywords) / len(self.sensitive_keywords),
                violation_type=ViolationType.UNAUTHORIZED_USE,
                analysis_method=AnalysisMethod.KEYWORD_DETECTION,
                confidence=0.6,
                details={
                    'detected_keywords': found_keywords,
                    'keyword_count': len(found_keywords)
                }
            )
            violations.append(violation)
        
        return violations
    
    def _calculate_risk_score(
        self,
        violations: List[SimilarityMatch],
        fingerprint: ContentFingerprint
    ) -> float:
        """Calculate overall risk score."""        if not violations:
            return 0.0
        
        # Base score from violations
        base_score = sum(v.similarity_score * v.confidence for v in violations) / len(violations)
        
        # Adjust for violation types
        violation_weights = {
            ViolationType.EXACT_DUPLICATE: 1.0,
            ViolationType.CONTENT_THEFT: 0.9,
            ViolationType.COPYRIGHT_INFRINGEMENT: 0.9,
            ViolationType.MODIFIED_COPY: 0.7,
            ViolationType.SIMILARITY_MATCH: 0.5,
            ViolationType.UNAUTHORIZED_USE: 0.4,
            ViolationType.PARTIAL_COPY: 0.3
        }
        
        weighted_score = 0.0
        for violation in violations:
            weight = violation_weights.get(violation.violation_type, 0.5)
            weighted_score += violation.similarity_score * weight
        
        weighted_score /= len(violations)
        
        # Combine scores
        final_score = (base_score + weighted_score) / 2
        
        return min(1.0, final_score)
    
    def _generate_recommendations(
        self,
        violations: List[SimilarityMatch],
        risk_score: float
    ) -> List[str]:
        """Generate recommendations based on analysis."""        recommendations = []
        
        if risk_score >= 0.8:
            recommendations.append("HIGH RISK: Immediate investigation recommended")
            recommendations.append("Consider issuing takedown notice")
            recommendations.append("Document evidence for legal action")
        elif risk_score >= 0.6:
            recommendations.append("MEDIUM RISK: Monitor closely")
            recommendations.append("Verify ownership and licensing")
            recommendations.append("Contact content creator for clarification")
        elif risk_score >= 0.3:
            recommendations.append("LOW RISK: Continue monitoring")
            recommendations.append("Review in 24-48 hours")
        else:
            recommendations.append("No immediate action required")
        
        # Specific recommendations based on violation types
        violation_types = {v.violation_type for v in violations}
        
        if ViolationType.EXACT_DUPLICATE in violation_types:
            recommendations.append("Exact duplicate detected - verify upload permissions")
        
        if ViolationType.COPYRIGHT_INFRINGEMENT in violation_types:
            recommendations.append("Potential copyright violation - review licensing")
        
        if ViolationType.CONTENT_THEFT in violation_types:
            recommendations.append("Possible content theft - investigate source")
        
        return recommendations
    
    def _get_analysis_methods(self, content_data: Dict[str, Any], content_type: str) -> List[AnalysisMethod]:
        """Determine which analysis methods were used."""        methods = []
        
        # Always check text if available
        if self._extract_text_content(content_data):
            methods.append(AnalysisMethod.TEXT_SIMILARITY)
            methods.append(AnalysisMethod.KEYWORD_DETECTION)
            methods.append(AnalysisMethod.PATTERN_MATCHING)
        
        # Check for media-specific methods
        if 'audio_url' in content_data or content_type == 'audio':
            methods.append(AnalysisMethod.AUDIO_FINGERPRINT)
        
        if 'video_url' in content_data or content_type == 'video':
            methods.append(AnalysisMethod.VIDEO_FINGERPRINT)
        
        if 'image_url' in content_data or 'thumbnail' in content_data:
            methods.append(AnalysisMethod.IMAGE_HASH)
        
        # Always check metadata
        if self._extract_metadata(content_data):
            methods.append(AnalysisMethod.METADATA_MATCH)
        
        return methods
    
    async def find_similar_content(
        self,
        content_id: str,
        limit: int = 10
    ) -> List[SimilarityMatch]:
        """Find content similar to specified content."""        fingerprint = self.fingerprint_db.get(content_id)
        if not fingerprint:
            return []
        
        # Use existing violation detection logic
        content_data = {'title': '', 'description': ''}  # Minimal data for compatibility
        violations = await self._detect_violations(fingerprint, content_data)
        
        # Sort by similarity score and return top matches
        violations.sort(key=lambda x: x.similarity_score, reverse=True)
        return violations[:limit]
    
    async def batch_analyze(
        self,
        content_batch: List[Tuple[str, Dict[str, Any], str, str]]
    ) -> List[AnalysisResult]:
        """Analyze multiple content items in batch."""        tasks = []
        
        for content_id, content_data, platform, content_type in content_batch:
            task = asyncio.create_task(
                self.analyze_content(content_id, content_data, platform, content_type)
            )
            tasks.append(task)
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Filter out exceptions and return successful results
        valid_results = [r for r in results if isinstance(r, AnalysisResult)]
        
        logger.info(f"Batch analyzed {len(valid_results)} out of {len(content_batch)} items")
        
        return valid_results
    
    def get_analysis_statistics(self) -> Dict[str, Any]:
        """Get analysis statistics."""        return {
            'total_analyses': self.analysis_count,
            'violations_detected': self.violation_count,
            'false_positives': self.false_positive_count,
            'fingerprints_stored': len(self.fingerprint_db),
            'text_index_size': len(self.text_index),
            'keyword_index_size': len(self.keyword_index),
            'violation_rate': self.violation_count / max(1, self.analysis_count),
            'average_keywords_per_content': sum(len(fp.keywords) for fp in self.fingerprint_db.values()) / max(1, len(self.fingerprint_db))
        }
    
    def mark_false_positive(self, suspected_id: str, original_id: str) -> None:
        """Mark a detection as false positive for learning."""        self.false_positive_count += 1
        logger.info(f"Marked false positive: {suspected_id} vs {original_id}")
    
    def update_thresholds(
        self,
        text_threshold: Optional[float] = None,
        audio_threshold: Optional[float] = None,
        video_threshold: Optional[float] = None,
        image_threshold: Optional[float] = None
    ) -> None:
        """Update similarity thresholds."""        if text_threshold is not None:
            self.text_similarity_threshold = text_threshold
        if audio_threshold is not None:
            self.audio_similarity_threshold = audio_threshold
        if video_threshold is not None:
            self.video_similarity_threshold = video_threshold
        if image_threshold is not None:
            self.image_similarity_threshold = image_threshold
        
        logger.info("Updated similarity thresholds")
    
    def clear_fingerprint_cache(self, older_than_days: int = 30) -> int:
        """Clear old fingerprints from cache."""        cutoff_date = datetime.now() - timedelta(days=older_than_days)
        removed_count = 0
        
        fingerprints_to_remove = []
        for content_id, fingerprint in self.fingerprint_db.items():
            if fingerprint.created_at < cutoff_date:
                fingerprints_to_remove.append(content_id)
        
        for content_id in fingerprints_to_remove:
            del self.fingerprint_db[content_id]
            removed_count += 1
            
            # Clean up indexes
            for hash_set in self.text_index.values():
                hash_set.discard(content_id)
            
            for keyword_set in self.keyword_index.values():
                keyword_set.discard(content_id)
        
        # Remove empty index entries
        self.text_index = {k: v for k, v in self.text_index.items() if v}
        self.keyword_index = {k: v for k, v in self.keyword_index.items() if v}
        
        logger.info(f"Cleared {removed_count} old fingerprints")
        return removed_count
