"""
🔍 Content Similarity Analyzer - Enterprise Content Duplication Detection
Advanced similarity analysis for content protection and deduplication

Role Expertise Applied:
- ML Engineer: Advanced similarity algorithms and neural embeddings
- Audio Engineer: Audio fingerprinting and acoustic similarity analysis
- Security Engineer: Content protection and theft detection
- Backend Senior: High-performance similarity processing pipeline
- Lead Dev IA: Intelligent pattern recognition and content classification
"""

import asyncio
import hashlib
import json
import logging
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple, Union, Set
from dataclasses import dataclass, asdict
from enum import Enum
import numpy as np

class SimilarityType(Enum):
    """Types of content similarity"""
    EXACT_DUPLICATE = "exact_duplicate"
    NEAR_DUPLICATE = "near_duplicate"
    PARTIAL_MATCH = "partial_match"
    SEMANTIC_SIMILARITY = "semantic_similarity"
    STRUCTURAL_SIMILARITY = "structural_similarity"
    ACOUSTIC_SIMILARITY = "acoustic_similarity"
    VISUAL_SIMILARITY = "visual_similarity"
    METADATA_SIMILARITY = "metadata_similarity"

class MatchConfidence(Enum):
    """Confidence levels for similarity matches"""
    VERY_HIGH = "very_high"  # 95-100%
    HIGH = "high"           # 85-95%
    MEDIUM = "medium"       # 70-85%
    LOW = "low"            # 50-70%
    VERY_LOW = "very_low"   # Below 50%

class ContentType(Enum):
    """Supported content types for analysis"""
    AUDIO = "audio"
    VIDEO = "video"
    IMAGE = "image"
    TEXT = "text"
    MIXED_MEDIA = "mixed_media"

@dataclass
class SimilarityMatch:
    """Individual similarity match result"""
    target_content_id: str
    similarity_score: float
    similarity_type: SimilarityType
    confidence: MatchConfidence
    match_segments: List[Dict[str, Any]]
    analysis_details: Dict[str, Any]
    processing_time_ms: float
    match_timestamp: datetime

@dataclass
class ContentFingerprint:
    """Content fingerprint for similarity analysis"""
    content_id: str
    fingerprint_type: str
    fingerprint_data: np.ndarray
    metadata_hash: str
    structural_features: Dict[str, Any]
    acoustic_features: Optional[Dict[str, Any]]
    visual_features: Optional[Dict[str, Any]]
    creation_timestamp: datetime

@dataclass
class SimilarityAnalysisResult:
    """Comprehensive similarity analysis result"""
    content_id: str
    total_matches_found: int
    exact_duplicates: List[SimilarityMatch]
    near_duplicates: List[SimilarityMatch]
    partial_matches: List[SimilarityMatch]
    semantic_matches: List[SimilarityMatch]
    highest_similarity_score: float
    analysis_confidence: float
    potential_violations: List[Dict[str, Any]]
    recommendation: str
    total_processing_time_ms: float
    analysis_timestamp: datetime

class ContentSimilarityAnalyzer:
    """Enterprise content similarity analysis system"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.logger = self._setup_logging()
        
        # Similarity thresholds
        self.similarity_thresholds = {
            SimilarityType.EXACT_DUPLICATE: 0.98,
            SimilarityType.NEAR_DUPLICATE: 0.90,
            SimilarityType.PARTIAL_MATCH: 0.75,
            SimilarityType.SEMANTIC_SIMILARITY: 0.70,
            SimilarityType.STRUCTURAL_SIMILARITY: 0.80,
            SimilarityType.ACOUSTIC_SIMILARITY: 0.85,
            SimilarityType.VISUAL_SIMILARITY: 0.82,
            SimilarityType.METADATA_SIMILARITY: 0.65
        }
        
        # Content fingerprint database
        self.fingerprint_database = {}
        
        # Analysis algorithms
        self.similarity_algorithms = {
            ContentType.AUDIO: self._analyze_audio_similarity,
            ContentType.VIDEO: self._analyze_video_similarity,
            ContentType.IMAGE: self._analyze_image_similarity,
            ContentType.TEXT: self._analyze_text_similarity,
            ContentType.MIXED_MEDIA: self._analyze_mixed_media_similarity
        }
        
        # Feature extractors
        self.feature_extractors = {
            'audio_mfcc': self._extract_audio_mfcc,
            'audio_chroma': self._extract_audio_chroma,
            'audio_spectral': self._extract_audio_spectral,
            'image_sift': self._extract_image_sift,
            'image_color_histogram': self._extract_image_color_histogram,
            'text_embeddings': self._extract_text_embeddings
        }
        
        # Performance metrics
        self.analysis_metrics = {
            'total_analyses': 0,
            'exact_duplicates_found': 0,
            'near_duplicates_found': 0,
            'false_positives': 0,
            'average_processing_time': 0.0,
            'database_size': 0,
            'accuracy_rate': 0.0
        }
        
        # Cache for similarity computations
        self.similarity_cache = {}
        self.cache_ttl = 3600  # 1 hour
    
    def _setup_logging(self) -> logging.Logger:
        """Setup comprehensive logging"""
        logger = logging.getLogger('content_similarity_analyzer')
        logger.setLevel(logging.INFO)
        
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        
        return logger
    
    async def analyze_content_similarity(self, content_data: Dict[str, Any]) -> SimilarityAnalysisResult:
        """
        Comprehensive content similarity analysis
        
        Args:
            content_data: Content data for similarity analysis
            
        Returns:
            SimilarityAnalysisResult: Comprehensive similarity analysis result
        """
        start_time = time.time()
        
        try:
            content_id = content_data.get('content_id', '')
            content_type = ContentType(content_data.get('content_type', 'mixed_media'))
            
            # Generate content fingerprint
            fingerprint = await self._generate_content_fingerprint(content_data)
            
            # Perform similarity search against database
            similarity_matches = await self._search_similar_content(fingerprint, content_type)
            
            # Categorize matches by similarity type
            categorized_matches = self._categorize_similarity_matches(similarity_matches)
            
            # Analyze potential violations
            potential_violations = self._analyze_potential_violations(categorized_matches, content_data)
            
            # Generate recommendations
            recommendation = self._generate_recommendation(categorized_matches, potential_violations)
            
            # Calculate analysis confidence
            analysis_confidence = self._calculate_analysis_confidence(categorized_matches, fingerprint)
            
            # Create result
            total_processing_time = (time.time() - start_time) * 1000
            
            result = SimilarityAnalysisResult(
                content_id=content_id,
                total_matches_found=len(similarity_matches),
                exact_duplicates=categorized_matches.get(SimilarityType.EXACT_DUPLICATE, []),
                near_duplicates=categorized_matches.get(SimilarityType.NEAR_DUPLICATE, []),
                partial_matches=categorized_matches.get(SimilarityType.PARTIAL_MATCH, []),
                semantic_matches=categorized_matches.get(SimilarityType.SEMANTIC_SIMILARITY, []),
                highest_similarity_score=max([m.similarity_score for m in similarity_matches], default=0.0),
                analysis_confidence=analysis_confidence,
                potential_violations=potential_violations,
                recommendation=recommendation,
                total_processing_time_ms=total_processing_time,
                analysis_timestamp=datetime.now()
            )
            
            # Store fingerprint in database
            self._store_fingerprint(fingerprint)
            
            # Update metrics
            self._update_analysis_metrics(result)
            
            self.logger.info(f"Similarity analysis completed for {content_id}: "
                           f"{result.total_matches_found} matches, highest score: {result.highest_similarity_score:.3f}")
            
            return result
            
        except Exception as e:
            self.logger.error(f"Content similarity analysis failed: {str(e)}")
            return SimilarityAnalysisResult(
                content_id=content_data.get('content_id', ''),
                total_matches_found=0,
                exact_duplicates=[],
                near_duplicates=[],
                partial_matches=[],
                semantic_matches=[],
                highest_similarity_score=0.0,
                analysis_confidence=0.0,
                potential_violations=[],
                recommendation="Analysis failed - manual review required",
                total_processing_time_ms=(time.time() - start_time) * 1000,
                analysis_timestamp=datetime.now()
            )
    
    async def _generate_content_fingerprint(self, content_data: Dict[str, Any]) -> ContentFingerprint:
        """Generate comprehensive content fingerprint"""
        content_id = content_data.get('content_id', '')
        content_type = content_data.get('content_type', 'mixed_media')
        
        # Extract various features based on content type
        feature_extraction_tasks = []
        
        if content_type in ['audio', 'mp3', 'wav', 'flac']:
            feature_extraction_tasks.extend([
                self._extract_audio_mfcc(content_data),
                self._extract_audio_chroma(content_data),
                self._extract_audio_spectral(content_data)
            ])
        
        if content_type in ['image', 'jpg', 'png', 'gif']:
            feature_extraction_tasks.extend([
                self._extract_image_sift(content_data),
                self._extract_image_color_histogram(content_data)
            ])
        
        if content_type in ['text', 'lyrics']:
            feature_extraction_tasks.append(
                self._extract_text_embeddings(content_data)
            )
        
        # Execute feature extraction
        features = await asyncio.gather(*feature_extraction_tasks, return_exceptions=True)
        
        # Compile features
        compiled_features = {}
        acoustic_features = {}
        visual_features = {}
        
        for feature in features:
            if isinstance(feature, dict) and not isinstance(feature, Exception):
                feature_type = feature.get('type', 'unknown')
                if feature_type.startswith('audio'):
                    acoustic_features.update(feature)
                elif feature_type.startswith('image'):
                    visual_features.update(feature)
                else:
                    compiled_features.update(feature)
        
        # Generate combined fingerprint
        fingerprint_data = self._combine_features_to_fingerprint(compiled_features, acoustic_features, visual_features)
        
        # Generate metadata hash
        metadata = content_data.get('metadata', {})
        metadata_hash = hashlib.sha256(json.dumps(metadata, sort_keys=True).encode()).hexdigest()
        
        # Extract structural features
        structural_features = {
            'duration': content_data.get('duration', 0),
            'file_size': content_data.get('file_size', 0),
            'bitrate': content_data.get('bitrate', 0),
            'sample_rate': content_data.get('sample_rate', 0),
            'channels': content_data.get('channels', 0),
            'format': content_data.get('format', 'unknown')
        }
        
        return ContentFingerprint(
            content_id=content_id,
            fingerprint_type='composite',
            fingerprint_data=fingerprint_data,
            metadata_hash=metadata_hash,
            structural_features=structural_features,
            acoustic_features=acoustic_features if acoustic_features else None,
            visual_features=visual_features if visual_features else None,
            creation_timestamp=datetime.now()
        )
    
    async def _extract_audio_mfcc(self, content_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract MFCC (Mel-Frequency Cepstral Coefficients) features"""
        # Simulate MFCC extraction
        await asyncio.sleep(0.05)
        
        # Mock MFCC features
        import random
        mfcc_features = np.random.random((13, 100))  # 13 MFCC coefficients, 100 time frames
        
        return {
            'type': 'audio_mfcc',
            'mfcc_coefficients': mfcc_features.tolist(),
            'feature_dimension': mfcc_features.shape,
            'extraction_quality': 0.85 + random.random() * 0.15
        }
    
    async def _extract_audio_chroma(self, content_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract chroma features for harmonic analysis"""
        await asyncio.sleep(0.03)
        
        import random
        chroma_features = np.random.random((12, 100))  # 12 chroma bins, 100 time frames
        
        return {
            'type': 'audio_chroma',
            'chroma_vector': chroma_features.tolist(),
            'tonal_centroid': np.mean(chroma_features, axis=1).tolist(),
            'harmonic_strength': 0.7 + random.random() * 0.3
        }
    
    async def _extract_audio_spectral(self, content_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract spectral features"""
        await asyncio.sleep(0.04)
        
        import random
        return {
            'type': 'audio_spectral',
            'spectral_centroid': random.uniform(1000, 8000),
            'spectral_rolloff': random.uniform(6000, 15000),
            'spectral_bandwidth': random.uniform(2000, 6000),
            'zero_crossing_rate': random.uniform(0.01, 0.15),
            'spectral_contrast': np.random.random(7).tolist()
        }
    
    async def _extract_image_sift(self, content_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract SIFT (Scale-Invariant Feature Transform) features"""
        await asyncio.sleep(0.08)
        
        import random
        num_keypoints = random.randint(50, 500)
        sift_descriptors = np.random.random((num_keypoints, 128))
        
        return {
            'type': 'image_sift',
            'keypoints_count': num_keypoints,
            'descriptors': sift_descriptors.tolist(),
            'feature_strength': 0.75 + random.random() * 0.25
        }
    
    async def _extract_image_color_histogram(self, content_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract color histogram features"""
        await asyncio.sleep(0.02)
        
        # Mock color histogram
        color_histogram = {
            'red_channel': np.random.random(256).tolist(),
            'green_channel': np.random.random(256).tolist(),
            'blue_channel': np.random.random(256).tolist()
        }
        
        return {
            'type': 'image_color_histogram',
            'histogram': color_histogram,
            'dominant_colors': np.random.randint(0, 256, (5, 3)).tolist(),
            'color_variance': np.random.random()
        }
    
    async def _extract_text_embeddings(self, content_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract text embeddings for semantic analysis"""
        await asyncio.sleep(0.06)
        
        # Mock text embedding
        text_embedding = np.random.random(384)  # Common embedding dimension
        
        return {
            'type': 'text_embeddings',
            'embedding_vector': text_embedding.tolist(),
            'text_length': len(content_data.get('text_content', '')),
            'language_confidence': 0.9 + np.random.random() * 0.1
        }
    
    def _combine_features_to_fingerprint(self, compiled_features: Dict[str, Any], 
                                       acoustic_features: Dict[str, Any], 
                                       visual_features: Dict[str, Any]) -> np.ndarray:
        """Combine all features into a single fingerprint vector"""
        fingerprint_components = []
        
        # Add acoustic features
        if acoustic_features:
            for key, value in acoustic_features.items():
                if isinstance(value, list) and len(value) > 0:
                    if isinstance(value[0], list):
                        # Flatten 2D arrays
                        flattened = np.array(value).flatten()
                        fingerprint_components.extend(flattened[:100])  # Limit size
                    else:
                        fingerprint_components.extend(value[:50])  # Limit size
        
        # Add visual features
        if visual_features:
            for key, value in visual_features.items():
                if isinstance(value, list) and len(value) > 0:
                    if isinstance(value[0], list):
                        flattened = np.array(value).flatten()
                        fingerprint_components.extend(flattened[:100])
                    else:
                        fingerprint_components.extend(value[:50])
        
        # Add other features
        for key, value in compiled_features.items():
            if isinstance(value, list):
                fingerprint_components.extend(value[:50])
            elif isinstance(value, (int, float)):
                fingerprint_components.append(value)
        
        # Ensure fixed size
        if len(fingerprint_components) < 512:
            fingerprint_components.extend([0.0] * (512 - len(fingerprint_components)))
        else:
            fingerprint_components = fingerprint_components[:512]
        
        return np.array(fingerprint_components)
    
    async def _search_similar_content(self, query_fingerprint: ContentFingerprint, content_type: ContentType) -> List[SimilarityMatch]:
        """Search for similar content in the database"""
        similarity_matches = []
        
        # Search against all stored fingerprints
        for stored_fingerprint in self.fingerprint_database.values():
            if stored_fingerprint.content_id == query_fingerprint.content_id:
                continue  # Skip self-comparison
            
            # Calculate similarity score
            similarity_score = self._calculate_similarity_score(query_fingerprint, stored_fingerprint)
            
            if similarity_score > 0.5:  # Minimum threshold for consideration
                # Determine similarity type
                similarity_type = self._determine_similarity_type(similarity_score)
                
                # Determine confidence level
                confidence = self._determine_confidence_level(similarity_score)
                
                # Find match segments (simplified)
                match_segments = self._identify_match_segments(query_fingerprint, stored_fingerprint)
                
                # Create similarity match
                match = SimilarityMatch(
                    target_content_id=stored_fingerprint.content_id,
                    similarity_score=similarity_score,
                    similarity_type=similarity_type,
                    confidence=confidence,
                    match_segments=match_segments,
                    analysis_details={
                        'fingerprint_distance': 1.0 - similarity_score,
                        'structural_similarity': self._calculate_structural_similarity(query_fingerprint, stored_fingerprint),
                        'metadata_similarity': self._calculate_metadata_similarity(query_fingerprint, stored_fingerprint)
                    },
                    processing_time_ms=5.0,  # Mock processing time
                    match_timestamp=datetime.now()
                )
                
                similarity_matches.append(match)
        
        # Sort by similarity score
        similarity_matches.sort(key=lambda x: x.similarity_score, reverse=True)
        
        return similarity_matches[:50]  # Return top 50 matches
    
    def _calculate_similarity_score(self, fingerprint1: ContentFingerprint, fingerprint2: ContentFingerprint) -> float:
        """Calculate similarity score between two fingerprints"""
        # Calculate cosine similarity
        fp1_norm = np.linalg.norm(fingerprint1.fingerprint_data)
        fp2_norm = np.linalg.norm(fingerprint2.fingerprint_data)
        
        if fp1_norm == 0 or fp2_norm == 0:
            return 0.0
        
        cosine_similarity = np.dot(fingerprint1.fingerprint_data, fingerprint2.fingerprint_data) / (fp1_norm * fp2_norm)
        
        # Normalize to 0-1 range
        cosine_similarity = (cosine_similarity + 1) / 2
        
        return max(0.0, min(1.0, cosine_similarity))
    
    def _calculate_structural_similarity(self, fingerprint1: ContentFingerprint, fingerprint2: ContentFingerprint) -> float:
        """Calculate structural similarity between content"""
        struct1 = fingerprint1.structural_features
        struct2 = fingerprint2.structural_features
        
        similarities = []
        
        # Duration similarity
        if struct1.get('duration', 0) > 0 and struct2.get('duration', 0) > 0:
            duration_ratio = min(struct1['duration'], struct2['duration']) / max(struct1['duration'], struct2['duration'])
            similarities.append(duration_ratio)
        
        # Bitrate similarity
        if struct1.get('bitrate', 0) > 0 and struct2.get('bitrate', 0) > 0:
            bitrate_ratio = min(struct1['bitrate'], struct2['bitrate']) / max(struct1['bitrate'], struct2['bitrate'])
            similarities.append(bitrate_ratio)
        
        # Sample rate similarity
        if struct1.get('sample_rate', 0) > 0 and struct2.get('sample_rate', 0) > 0:
            sr_ratio = min(struct1['sample_rate'], struct2['sample_rate']) / max(struct1['sample_rate'], struct2['sample_rate'])
            similarities.append(sr_ratio)
        
        return np.mean(similarities) if similarities else 0.0
    
    def _calculate_metadata_similarity(self, fingerprint1: ContentFingerprint, fingerprint2: ContentFingerprint) -> float:
        """Calculate metadata similarity"""
        # Simple hash comparison for now
        return 1.0 if fingerprint1.metadata_hash == fingerprint2.metadata_hash else 0.0
    
    def _determine_similarity_type(self, similarity_score: float) -> SimilarityType:
        """Determine the type of similarity based on score"""
        if similarity_score >= self.similarity_thresholds[SimilarityType.EXACT_DUPLICATE]:
            return SimilarityType.EXACT_DUPLICATE
        elif similarity_score >= self.similarity_thresholds[SimilarityType.NEAR_DUPLICATE]:
            return SimilarityType.NEAR_DUPLICATE
        elif similarity_score >= self.similarity_thresholds[SimilarityType.PARTIAL_MATCH]:
            return SimilarityType.PARTIAL_MATCH
        else:
            return SimilarityType.SEMANTIC_SIMILARITY
    
    def _determine_confidence_level(self, similarity_score: float) -> MatchConfidence:
        """Determine confidence level based on similarity score"""
        if similarity_score >= 0.95:
            return MatchConfidence.VERY_HIGH
        elif similarity_score >= 0.85:
            return MatchConfidence.HIGH
        elif similarity_score >= 0.70:
            return MatchConfidence.MEDIUM
        elif similarity_score >= 0.50:
            return MatchConfidence.LOW
        else:
            return MatchConfidence.VERY_LOW
    
    def _identify_match_segments(self, fingerprint1: ContentFingerprint, fingerprint2: ContentFingerprint) -> List[Dict[str, Any]]:
        """Identify specific segments where content matches"""
        # Mock segment identification
        import random
        num_segments = random.randint(1, 5)
        
        segments = []
        for i in range(num_segments):
            start_time = random.uniform(0, 100)
            duration = random.uniform(5, 30)
            
            segments.append({
                'segment_id': f"segment_{i+1}",
                'start_time_seconds': start_time,
                'duration_seconds': duration,
                'similarity_score': 0.8 + random.random() * 0.2,
                'segment_type': random.choice(['intro', 'chorus', 'verse', 'bridge', 'outro'])
            })
        
        return segments
    
    def _categorize_similarity_matches(self, matches: List[SimilarityMatch]) -> Dict[SimilarityType, List[SimilarityMatch]]:
        """Categorize similarity matches by type"""
        categorized = {similarity_type: [] for similarity_type in SimilarityType}
        
        for match in matches:
            categorized[match.similarity_type].append(match)
        
        return categorized
    
    def _analyze_potential_violations(self, categorized_matches: Dict[SimilarityType, List[SimilarityMatch]], 
                                   content_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Analyze potential copyright violations"""
        violations = []
        
        # Check for exact duplicates
        exact_duplicates = categorized_matches.get(SimilarityType.EXACT_DUPLICATE, [])
        for match in exact_duplicates:
            violations.append({
                'violation_type': 'exact_duplicate',
                'target_content_id': match.target_content_id,
                'severity': 'high',
                'similarity_score': match.similarity_score,
                'confidence': match.confidence.value,
                'recommendation': 'Immediate takedown required'
            })
        
        # Check for near duplicates
        near_duplicates = categorized_matches.get(SimilarityType.NEAR_DUPLICATE, [])
        for match in near_duplicates:
            if match.confidence in [MatchConfidence.VERY_HIGH, MatchConfidence.HIGH]:
                violations.append({
                    'violation_type': 'near_duplicate',
                    'target_content_id': match.target_content_id,
                    'severity': 'medium',
                    'similarity_score': match.similarity_score,
                    'confidence': match.confidence.value,
                    'recommendation': 'Manual review required'
                })
        
        return violations
    
    def _generate_recommendation(self, categorized_matches: Dict[SimilarityType, List[SimilarityMatch]], 
                               violations: List[Dict[str, Any]]) -> str:
        """Generate recommendation based on analysis results"""
        if not any(categorized_matches.values()):
            return "No similar content found. Content appears to be original."
        
        if violations:
            high_severity_violations = [v for v in violations if v['severity'] == 'high']
            if high_severity_violations:
                return "High risk: Exact duplicates detected. Immediate action required."
            else:
                return "Medium risk: Potential violations detected. Manual review recommended."
        
        total_matches = sum(len(matches) for matches in categorized_matches.values())
        if total_matches > 10:
            return "Multiple similar content detected. Consider originality verification."
        elif total_matches > 5:
            return "Some similar content found. Monitor for potential issues."
        else:
            return "Low similarity detected. Content appears sufficiently original."
    
    def _calculate_analysis_confidence(self, categorized_matches: Dict[SimilarityType, List[SimilarityMatch]], 
                                     fingerprint: ContentFingerprint) -> float:
        """Calculate overall confidence in the analysis"""
        if not any(categorized_matches.values()):
            return 0.95  # High confidence when no matches found
        
        # Calculate based on match quality and consistency
        all_matches = []
        for matches in categorized_matches.values():
            all_matches.extend(matches)
        
        if not all_matches:
            return 0.95
        
        # Average confidence of all matches
        avg_confidence = np.mean([
            {'very_high': 0.95, 'high': 0.85, 'medium': 0.70, 'low': 0.50, 'very_low': 0.30}[match.confidence.value]
            for match in all_matches
        ])
        
        # Factor in fingerprint quality
        fingerprint_quality = 0.9  # Mock fingerprint quality
        
        return min(1.0, (avg_confidence * 0.7 + fingerprint_quality * 0.3))
    
    def _store_fingerprint(self, fingerprint: ContentFingerprint):
        """Store fingerprint in the database"""
        self.fingerprint_database[fingerprint.content_id] = fingerprint
        self.analysis_metrics['database_size'] = len(self.fingerprint_database)
    
    def _update_analysis_metrics(self, result: SimilarityAnalysisResult):
        """Update analysis performance metrics"""
        self.analysis_metrics['total_analyses'] += 1
        self.analysis_metrics['exact_duplicates_found'] += len(result.exact_duplicates)
        self.analysis_metrics['near_duplicates_found'] += len(result.near_duplicates)
        
        # Update average processing time
        current_avg = self.analysis_metrics['average_processing_time']
        total_analyses = self.analysis_metrics['total_analyses']
        self.analysis_metrics['average_processing_time'] = (
            (current_avg * (total_analyses - 1) + result.total_processing_time_ms) / total_analyses
        )
    
    async def get_analysis_metrics(self) -> Dict[str, Any]:
        """Get comprehensive analysis metrics"""
        return {
            "performance_metrics": self.analysis_metrics.copy(),
            "similarity_thresholds": {stype.value: threshold for stype, threshold in self.similarity_thresholds.items()},
            "supported_content_types": [ctype.value for ctype in ContentType],
            "feature_extractors": list(self.feature_extractors.keys()),
            "database_statistics": {
                "total_fingerprints": len(self.fingerprint_database),
                "fingerprint_types": list(set(fp.fingerprint_type for fp in self.fingerprint_database.values())),
                "oldest_fingerprint": min((fp.creation_timestamp for fp in self.fingerprint_database.values()), default=datetime.now()).isoformat(),
                "newest_fingerprint": max((fp.creation_timestamp for fp in self.fingerprint_database.values()), default=datetime.now()).isoformat()
            },
            "cache_statistics": {
                "cache_size": len(self.similarity_cache),
                "cache_ttl_hours": self.cache_ttl / 3600,
                "cache_hit_rate": 0.75  # Mock hit rate
            }
        }

# Global content similarity analyzer instance
content_similarity_analyzer = ContentSimilarityAnalyzer()

async def analyze_content_similarity(content_data: Dict[str, Any]) -> SimilarityAnalysisResult:
    """Global function for content similarity analysis"""
    return await content_similarity_analyzer.analyze_content_similarity(content_data)

async def get_analysis_metrics() -> Dict[str, Any]:
    """Global function to get analysis metrics"""
    return await content_similarity_analyzer.get_analysis_metrics()
