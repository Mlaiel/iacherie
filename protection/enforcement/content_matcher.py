"""Advanced Content Matching Engine for Copyright Enforcement
Sophisticated algorithms for detecting content violations across multiple media types
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Tuple, Set
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import hashlib
import json
from pathlib import Path
import numpy as np
from concurrent.futures import ThreadPoolExecutor
import aiohttp

from pydantic import BaseModel, Field


logger = logging.getLogger(__name__)


class MatchingAlgorithm(Enum):
    """
Content matching algorithms"""

    EXACT_HASH = "exact_hash"
    PERCEPTUAL_HASH = "perceptual_hash"
    AUDIO_FINGERPRINT = "audio_fingerprint"
    VIDEO_FINGERPRINT = "video_fingerprint"
    TEXT_SIMILARITY = "text_similarity"
    VECTOR_SIMILARITY = "vector_similarity"
    MACHINE_LEARNING = "machine_learning"


class MatchConfidence(Enum):
    """Confidence levels for content matches"""

    VERY_LOW = "very_low"      # 0.0 - 0.3
    LOW = "low"                # 0.3 - 0.5
    MEDIUM = "medium"          # 0.5 - 0.7
    HIGH = "high"              # 0.7 - 0.9
    VERY_HIGH = "very_high"    # 0.9 - 1.0


@dataclass
class ContentSignature:
    """Digital signature of content for matching"""
    content_id: str
    content_type: str  # audio, video, image, text
    signature_hash: str
    perceptual_hash: Optional[str] = None
    feature_vector: Optional[List[float]] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)
    
    # Audio-specific
    audio_duration: Optional[float] = None
    tempo: Optional[float] = None
    key_signature: Optional[str] = None
    
    # Video-specific
    video_duration: Optional[float] = None
    resolution: Optional[str] = None
    fps: Optional[float] = None
    
    # Image-specific
    image_dimensions: Optional[Tuple[int, int]] = None
    color_palette: Optional[List[str]] = None
    
    # Text-specific
    text_length: Optional[int] = None
    language: Optional[str] = None
    keywords: List[str] = field(default_factory=list)


@dataclass
class MatchResult:
    """
Result of content matching operation"""
    original_signature: ContentSignature
    matched_signature: ContentSignature
    algorithm_used: MatchingAlgorithm
    similarity_score: float
    confidence_level: MatchConfidence
    match_details: Dict[str, Any] = field(default_factory=dict)
    processing_time: float = 0.0
    timestamp: datetime = field(default_factory=datetime.utcnow)


class AudioMatcher:
    """
Advanced audio content matching using multiple algorithms"""
    
    def __init__(self, config -> None: Optional[Dict[str, Any]] = None) -> None:
        self.config = config or {}
        self.chromaprint_enabled = self.config.get('chromaprint_enabled', True)
        self.spectral_enabled = self.config.get('spectral_enabled', True)
        self.ml_enabled = self.config.get('ml_enabled', False)
        
    async def generate_signature(self, audio_data: bytes, metadata: Dict[str, Any]) -> ContentSignature:
        """
Generate comprehensive audio signature"""
        try:
            # Basic hash
            content_hash = hashlib.sha256(audio_data).hexdigest()
            
            # Audio-specific processing would go here
            # For now, simulating advanced fingerprinting
            perceptual_hash = self._generate_audio_perceptual_hash(audio_data)
            feature_vector = await self._extract_audio_features(audio_data)
            
            signature = ContentSignature(
                content_id=metadata.get('content_id', content_hash[:16]),
                content_type='audio',
                signature_hash=content_hash,
                perceptual_hash=perceptual_hash,
                feature_vector=feature_vector,
                metadata=metadata,
                audio_duration=metadata.get('duration'),
                tempo=metadata.get('tempo'),
                key_signature=metadata.get('key')
            )
            
            logger.debug(f"Generated audio signature for {signature.content_id}")
            return signature
            
        except Exception as e:
            logger.error(f"Error generating audio signature: {e}")
            raise
    
    def _generate_audio_perceptual_hash(self, audio_data: bytes) -> str:
        """Generate perceptual hash for audio content"""
        try:
            # Simulate advanced audio fingerprinting
            # In real implementation, would use Chromaprint or similar
            hash_input = str(len(audio_data)) + str(hash(audio_data[:1024]))
            return hashlib.md5(hash_input.encode()).hexdigest()
            
        except Exception as e:
            logger.error(f"Error generating audio perceptual hash: {e}")
            return ""
    
    async def _extract_audio_features(self, audio_data: bytes) -> List[float]:
        """Extract ML features from audio"""
        try:
            # Simulate feature extraction
            # In real implementation, would use librosa, essentia, or similar
            features = [float(i % 128) / 128.0 for i in range(128)]
            return features
            
        except Exception as e:
            logger.error(f"Error extracting audio features: {e}")
            return []
    
    async def match_audio(
        self,
        signature1: ContentSignature,
        signature2: ContentSignature
    ) -> MatchResult:
        """Match two audio signatures"""
        try:
            start_time = datetime.utcnow()
            
            # Exact hash comparison
            if signature1.signature_hash == signature2.signature_hash:
                similarity_score = 1.0
                algorithm = MatchingAlgorithm.EXACT_HASH
            else:
                # Perceptual hash comparison
                perceptual_similarity = self._compare_perceptual_hashes(
                    signature1.perceptual_hash,
                    signature2.perceptual_hash
                )
                
                # Feature vector comparison
                feature_similarity = 0.0
                if signature1.feature_vector and signature2.feature_vector:
                    feature_similarity = self._compare_feature_vectors(
                        signature1.feature_vector,
                        signature2.feature_vector
                    )
                
                # Combined similarity
                similarity_score = max(perceptual_similarity, feature_similarity)
                algorithm = MatchingAlgorithm.AUDIO_FINGERPRINT
            
            # Determine confidence level
            confidence = self._determine_confidence(similarity_score)
            
            processing_time = (datetime.utcnow() - start_time).total_seconds()
            
            result = MatchResult(
                original_signature=signature1,
                matched_signature=signature2,
                algorithm_used=algorithm,
                similarity_score=similarity_score,
                confidence_level=confidence,
                match_details={
                    'perceptual_similarity': perceptual_similarity if 'perceptual_similarity' in locals() else 1.0,
                    'feature_similarity': feature_similarity if 'feature_similarity' in locals() else 1.0,
                    'duration_match': abs((signature1.audio_duration or 0) - (signature2.audio_duration or 0)) < 5.0
                },
                processing_time=processing_time
            )
            
            logger.debug(f"Audio match result: {similarity_score:.3f} confidence: {confidence.value}")
            return result
            
        except Exception as e:
            logger.error(f"Error matching audio signatures: {e}")
            raise
    
    def _compare_perceptual_hashes(self, hash1: Optional[str], hash2: Optional[str]) -> float:
        """Compare perceptual hashes"""
        if not hash1 or not hash2:
            return 0.0
        
        if hash1 == hash2:
            return 1.0
        
        # Hamming distance for perceptual hashes
        try:
            diff = sum(c1 != c2 for c1, c2 in zip(hash1, hash2))
            similarity = 1.0 - (diff / len(hash1))
            return max(0.0, similarity)
        except:
            return 0.0
    
    def _compare_feature_vectors(self, vec1: List[float], vec2: List[float]) -> float:
        """
Compare feature vectors using cosine similarity"""
        try:
            if len(vec1) != len(vec2):
                return 0.0
            
            # Cosine similarity
            dot_product = sum(a * b for a, b in zip(vec1, vec2))
            magnitude1 = sum(a * a for a in vec1) ** 0.5
            magnitude2 = sum(b * b for b in vec2) ** 0.5
            
            if magnitude1 == 0 or magnitude2 == 0:
                return 0.0
            
            similarity = dot_product / (magnitude1 * magnitude2)
            return max(0.0, min(1.0, similarity))
            
        except Exception as e:
            logger.error(f"Error comparing feature vectors: {e}")
            return 0.0
    
    def _determine_confidence(self, similarity_score: float) -> MatchConfidence:
        """Determine confidence level based on similarity score"""
        if similarity_score >= 0.9:
            return MatchConfidence.VERY_HIGH
        elif similarity_score >= 0.7:
            return MatchConfidence.HIGH
        elif similarity_score >= 0.5:
            return MatchConfidence.MEDIUM
        elif similarity_score >= 0.3:
            return MatchConfidence.LOW
        else:
            return MatchConfidence.VERY_LOW


class VideoMatcher:
    """
Advanced video content matching"""
    
    def __init__(self, config -> None: Optional[Dict[str, Any]] = None) -> None:
        self.config = config or {}
        self.frame_sampling_rate = self.config.get('frame_sampling_rate', 1.0)  # frames per second
        self.visual_hash_enabled = self.config.get('visual_hash_enabled', True)
        self.object_detection_enabled = self.config.get('object_detection_enabled', False)
    
    async def generate_signature(self, video_data: bytes, metadata: Dict[str, Any]) -> ContentSignature:
        """
Generate comprehensive video signature"""
        try:
            content_hash = hashlib.sha256(video_data).hexdigest()
            
            # Video-specific processing
            perceptual_hash = await self._generate_video_perceptual_hash(video_data)
            feature_vector = await self._extract_video_features(video_data)
            
            signature = ContentSignature(
                content_id=metadata.get('content_id', content_hash[:16]),
                content_type='video',
                signature_hash=content_hash,
                perceptual_hash=perceptual_hash,
                feature_vector=feature_vector,
                metadata=metadata,
                video_duration=metadata.get('duration'),
                resolution=metadata.get('resolution'),
                fps=metadata.get('fps')
            )
            
            logger.debug(f"Generated video signature for {signature.content_id}")
            return signature
            
        except Exception as e:
            logger.error(f"Error generating video signature: {e}")
            raise
    
    async def _generate_video_perceptual_hash(self, video_data: bytes) -> str:
        """Generate perceptual hash for video content"""
        try:
            # Simulate video frame hashing
            # In real implementation, would extract key frames and hash them
            hash_input = str(len(video_data)) + str(hash(video_data[:2048]))
            return hashlib.md5(hash_input.encode()).hexdigest()
            
        except Exception as e:
            logger.error(f"Error generating video perceptual hash: {e}")
            return ""
    
    async def _extract_video_features(self, video_data: bytes) -> List[float]:
        """Extract ML features from video"""
        try:
            # Simulate video feature extraction
            # In real implementation, would use OpenCV, YOLO, or similar
            features = [float(i % 256) / 256.0 for i in range(256)]
            return features
            
        except Exception as e:
            logger.error(f"Error extracting video features: {e}")
            return []
    
    async def match_video(
        self,
        signature1: ContentSignature,
        signature2: ContentSignature
    ) -> MatchResult:
        """Match two video signatures"""
        try:
            start_time = datetime.utcnow()
            
            # Exact hash comparison
            if signature1.signature_hash == signature2.signature_hash:
                similarity_score = 1.0
                algorithm = MatchingAlgorithm.EXACT_HASH
            else:
                # Perceptual comparison
                perceptual_similarity = self._compare_perceptual_hashes(
                    signature1.perceptual_hash,
                    signature2.perceptual_hash
                )
                
                # Feature vector comparison
                feature_similarity = 0.0
                if signature1.feature_vector and signature2.feature_vector:
                    feature_similarity = self._compare_feature_vectors(
                        signature1.feature_vector,
                        signature2.feature_vector
                    )
                
                similarity_score = max(perceptual_similarity, feature_similarity)
                algorithm = MatchingAlgorithm.VIDEO_FINGERPRINT
            
            confidence = self._determine_confidence(similarity_score)
            processing_time = (datetime.utcnow() - start_time).total_seconds()
            
            result = MatchResult(
                original_signature=signature1,
                matched_signature=signature2,
                algorithm_used=algorithm,
                similarity_score=similarity_score,
                confidence_level=confidence,
                match_details={
                    'perceptual_similarity': perceptual_similarity if 'perceptual_similarity' in locals() else 1.0,
                    'feature_similarity': feature_similarity if 'feature_similarity' in locals() else 1.0,
                    'resolution_match': signature1.resolution == signature2.resolution,
                    'duration_match': abs((signature1.video_duration or 0) - (signature2.video_duration or 0)) < 10.0
                },
                processing_time=processing_time
            )
            
            logger.debug(f"Video match result: {similarity_score:.3f} confidence: {confidence.value}")
            return result
            
        except Exception as e:
            logger.error(f"Error matching video signatures: {e}")
            raise
    
    def _compare_perceptual_hashes(self, hash1: Optional[str], hash2: Optional[str]) -> float:
        """Compare video perceptual hashes"""
        if not hash1 or not hash2:
            return 0.0
        
        if hash1 == hash2:
            return 1.0
        
        # Hamming distance comparison
        try:
            diff = sum(c1 != c2 for c1, c2 in zip(hash1, hash2))
            similarity = 1.0 - (diff / len(hash1))
            return max(0.0, similarity)
        except:
            return 0.0
    
    def _compare_feature_vectors(self, vec1: List[float], vec2: List[float]) -> float:
        """
Compare video feature vectors"""
        try:
            if len(vec1) != len(vec2):
                return 0.0
            
            # Cosine similarity
            dot_product = sum(a * b for a, b in zip(vec1, vec2))
            magnitude1 = sum(a * a for a in vec1) ** 0.5
            magnitude2 = sum(b * b for b in vec2) ** 0.5
            
            if magnitude1 == 0 or magnitude2 == 0:
                return 0.0
            
            similarity = dot_product / (magnitude1 * magnitude2)
            return max(0.0, min(1.0, similarity))
            
        except Exception as e:
            logger.error(f"Error comparing video feature vectors: {e}")
            return 0.0
    
    def _determine_confidence(self, similarity_score: float) -> MatchConfidence:
        """Determine confidence level for video matches"""
        if similarity_score >= 0.9:
            return MatchConfidence.VERY_HIGH
        elif similarity_score >= 0.7:
            return MatchConfidence.HIGH
        elif similarity_score >= 0.5:
            return MatchConfidence.MEDIUM
        elif similarity_score >= 0.3:
            return MatchConfidence.LOW
        else:
            return MatchConfidence.VERY_LOW


class TextMatcher:
    """
Advanced text content matching"""
    
    def __init__(self, config -> None: Optional[Dict[str, Any]] = None) -> None:
        self.config = config or {}
        self.semantic_enabled = self.config.get('semantic_enabled', True)
        self.language_detection_enabled = self.config.get('language_detection_enabled', True)
    
    async def generate_signature(self, text_content: str, metadata: Dict[str, Any]) -> ContentSignature:
        """
Generate comprehensive text signature"""
        try:
            content_hash = hashlib.sha256(text_content.encode()).hexdigest()
            
            # Text-specific processing
            perceptual_hash = self._generate_text_semantic_hash(text_content)
            feature_vector = await self._extract_text_features(text_content)
            keywords = self._extract_keywords(text_content)
            
            signature = ContentSignature(
                content_id=metadata.get('content_id', content_hash[:16]),
                content_type='text',
                signature_hash=content_hash,
                perceptual_hash=perceptual_hash,
                feature_vector=feature_vector,
                metadata=metadata,
                text_length=len(text_content),
                language=metadata.get('language', 'unknown'),
                keywords=keywords
            )
            
            logger.debug(f"Generated text signature for {signature.content_id}")
            return signature
            
        except Exception as e:
            logger.error(f"Error generating text signature: {e}")
            raise
    
    def _generate_text_semantic_hash(self, text: str) -> str:
        """Generate semantic hash for text content"""
        try:
            # Simulate semantic hashing
            # In real implementation, would use word embeddings or similar
            normalized_text = text.lower().strip()
            words = normalized_text.split()
            word_hash = hash(tuple(sorted(set(words))))
            return hashlib.md5(str(word_hash).encode()).hexdigest()
            
        except Exception as e:
            logger.error(f"Error generating text semantic hash: {e}")
            return ""
    
    async def _extract_text_features(self, text: str) -> List[float]:
        """Extract ML features from text"""
        try:
            # Simulate text feature extraction
            # In real implementation, would use BERT, RoBERTa, or similar
            features = []
            
            # Basic text statistics
            features.append(len(text) / 10000.0)  # normalized length
            features.append(len(text.split()) / 1000.0)  # normalized word count
            features.append(len(set(text.split())) / len(text.split()) if text.split() else 0)  # lexical diversity
            
            # Character frequency features
            char_counts = {}
            for char in text.lower():
                if char.isalpha():
                    char_counts[char] = char_counts.get(char, 0) + 1
            
            for i in range(26):
                char = chr(ord('a') + i)
                freq = char_counts.get(char, 0) / len(text) if text else 0
                features.append(freq)
            
            # Pad to fixed size
            while len(features) < 128:
                features.append(0.0)
            
            return features[:128]
            
        except Exception as e:
            logger.error(f"Error extracting text features: {e}")
            return [0.0] * 128
    
    def _extract_keywords(self, text: str) -> List[str]:
        """Extract keywords from text"""
        try:
            # Simple keyword extraction
            # In real implementation, would use NLP libraries like spaCy or NLTK
            words = text.lower().split()
            
            # Filter common words
            stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'from', 'this', 'that', 'these', 'those', 'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should', 'may', 'might', 'can', 'cannot', 'must'}
            
            keywords = [word for word in words if len(word) > 3 and word not in stop_words]
            
            # Return most frequent keywords
            word_counts = {}
            for word in keywords:
                word_counts[word] = word_counts.get(word, 0) + 1
            
            sorted_keywords = sorted(word_counts.items(), key=lambda x: x[1], reverse=True)
            return [word for word, count in sorted_keywords[:20]]
            
        except Exception as e:
            logger.error(f"Error extracting keywords: {e}")
            return []
    
    async def match_text(
        self,
        signature1: ContentSignature,
        signature2: ContentSignature
    ) -> MatchResult:
        """Match two text signatures"""
        try:
            start_time = datetime.utcnow()
            
            # Exact hash comparison
            if signature1.signature_hash == signature2.signature_hash:
                similarity_score = 1.0
                algorithm = MatchingAlgorithm.EXACT_HASH
            else:
                # Semantic similarity
                semantic_similarity = self._compare_semantic_hashes(
                    signature1.perceptual_hash,
                    signature2.perceptual_hash
                )
                
                # Feature vector similarity
                feature_similarity = 0.0
                if signature1.feature_vector and signature2.feature_vector:
                    feature_similarity = self._compare_feature_vectors(
                        signature1.feature_vector,
                        signature2.feature_vector
                    )
                
                # Keyword similarity
                keyword_similarity = self._compare_keywords(
                    signature1.keywords,
                    signature2.keywords
                )
                
                # Combined similarity
                similarity_score = max(semantic_similarity, feature_similarity, keyword_similarity)
                algorithm = MatchingAlgorithm.TEXT_SIMILARITY
            
            confidence = self._determine_confidence(similarity_score)
            processing_time = (datetime.utcnow() - start_time).total_seconds()
            
            result = MatchResult(
                original_signature=signature1,
                matched_signature=signature2,
                algorithm_used=algorithm,
                similarity_score=similarity_score,
                confidence_level=confidence,
                match_details={
                    'semantic_similarity': semantic_similarity if 'semantic_similarity' in locals() else 1.0,
                    'feature_similarity': feature_similarity if 'feature_similarity' in locals() else 1.0,
                    'keyword_similarity': keyword_similarity if 'keyword_similarity' in locals() else 1.0,
                    'language_match': signature1.language == signature2.language,
                    'length_ratio': min(signature1.text_length or 1, signature2.text_length or 1) / max(signature1.text_length or 1, signature2.text_length or 1)
                },
                processing_time=processing_time
            )
            
            logger.debug(f"Text match result: {similarity_score:.3f} confidence: {confidence.value}")
            return result
            
        except Exception as e:
            logger.error(f"Error matching text signatures: {e}")
            raise
    
    def _compare_semantic_hashes(self, hash1: Optional[str], hash2: Optional[str]) -> float:
        """Compare semantic hashes"""
        if not hash1 or not hash2:
            return 0.0
        
        if hash1 == hash2:
            return 1.0
        
        # Simple hash distance
        try:
            diff = sum(c1 != c2 for c1, c2 in zip(hash1, hash2))
            similarity = 1.0 - (diff / len(hash1))
            return max(0.0, similarity)
        except:
            return 0.0
    
    def _compare_feature_vectors(self, vec1: List[float], vec2: List[float]) -> float:
        """
Compare text feature vectors"""
        try:
            if len(vec1) != len(vec2):
                return 0.0
            
            # Cosine similarity
            dot_product = sum(a * b for a, b in zip(vec1, vec2))
            magnitude1 = sum(a * a for a in vec1) ** 0.5
            magnitude2 = sum(b * b for b in vec2) ** 0.5
            
            if magnitude1 == 0 or magnitude2 == 0:
                return 0.0
            
            similarity = dot_product / (magnitude1 * magnitude2)
            return max(0.0, min(1.0, similarity))
            
        except Exception as e:
            logger.error(f"Error comparing text feature vectors: {e}")
            return 0.0
    
    def _compare_keywords(self, keywords1: List[str], keywords2: List[str]) -> float:
        """Compare keyword lists using Jaccard similarity"""
        try:
            if not keywords1 or not keywords2:
                return 0.0
            
            set1 = set(keywords1)
            set2 = set(keywords2)
            
            intersection = len(set1 & set2)
            union = len(set1 | set2)
            
            return intersection / union if union > 0 else 0.0
            
        except Exception as e:
            logger.error(f"Error comparing keywords: {e}")
            return 0.0
    
    def _determine_confidence(self, similarity_score: float) -> MatchConfidence:
        """Determine confidence level for text matches"""
        if similarity_score >= 0.9:
            return MatchConfidence.VERY_HIGH
        elif similarity_score >= 0.7:
            return MatchConfidence.HIGH
        elif similarity_score >= 0.5:
            return MatchConfidence.MEDIUM
        elif similarity_score >= 0.3:
            return MatchConfidence.LOW
        else:
            return MatchConfidence.VERY_LOW


class ContentMatchingEngine:
    """
Central engine for content matching across all media types"""
    
    def __init__(self, config -> None: Optional[Dict[str, Any]] = None) -> None:
        self.config = config or {}
        self.audio_matcher = AudioMatcher(self.config.get('audio', {}))
        self.video_matcher = VideoMatcher(self.config.get('video', {}))
        self.text_matcher = TextMatcher(self.config.get('text', {}))
        
        self.similarity_threshold = self.config.get('similarity_threshold', 0.7)
        self.batch_size = self.config.get('batch_size', 100)
        self.max_concurrent_matches = self.config.get('max_concurrent_matches', 10)
        
        self.executor = ThreadPoolExecutor(max_workers=self.max_concurrent_matches)
        
        # In-memory signature cache for performance
        self.signature_cache: Dict[str, ContentSignature] = {}
        self.cache_max_size = self.config.get('cache_max_size', 10000)
    
    async def generate_signature(
        self,
        content_data: bytes,
        content_type: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> ContentSignature:
        """
Generate content signature based on type"""
        try:
            metadata = metadata or {}
            
            if content_type == 'audio':
                signature = await self.audio_matcher.generate_signature(content_data, metadata)
            elif content_type == 'video':
                signature = await self.video_matcher.generate_signature(content_data, metadata)
            elif content_type == 'text':
                text_content = content_data.decode('utf-8', errors='ignore')
                signature = await self.text_matcher.generate_signature(text_content, metadata)
            else:
                raise ValueError(f"Unsupported content type: {content_type}")
            
            # Cache signature
            self._cache_signature(signature)
            
            logger.info(f"Generated {content_type} signature: {signature.content_id}")
            return signature
            
        except Exception as e:
            logger.error(f"Error generating signature for {content_type}: {e}")
            raise
    
    async def match_content(
        self,
        signature1: ContentSignature,
        signature2: ContentSignature
    ) -> MatchResult:
        """Match two content signatures"""
        try:
            if signature1.content_type != signature2.content_type:
                raise ValueError("Cannot match signatures of different content types")
            
            content_type = signature1.content_type
            
            if content_type == 'audio':
                result = await self.audio_matcher.match_audio(signature1, signature2)
            elif content_type == 'video':
                result = await self.video_matcher.match_video(signature1, signature2)
            elif content_type == 'text':
                result = await self.text_matcher.match_text(signature1, signature2)
            else:
                raise ValueError(f"Unsupported content type for matching: {content_type}")
            
            logger.debug(f"Content match completed: {result.similarity_score:.3f}")
            return result
            
        except Exception as e:
            logger.error(f"Error matching content: {e}")
            raise
    
    async def batch_match(
        self,
        target_signature: ContentSignature,
        candidate_signatures: List[ContentSignature],
        min_similarity: Optional[float] = None
    ) -> List[MatchResult]:
        """Batch match target against multiple candidates"""
        try:
            min_similarity = min_similarity or self.similarity_threshold
            
            # Filter by content type
            valid_candidates = [
                sig for sig in candidate_signatures
                if sig.content_type == target_signature.content_type
            ]
            
            if not valid_candidates:
                return []
            
            # Process in batches
            results = []
            for i in range(0, len(valid_candidates), self.batch_size):
                batch = valid_candidates[i:i + self.batch_size]
                
                # Concurrent matching within batch
                tasks = [
                    self.match_content(target_signature, candidate)
                    for candidate in batch
                ]
                
                batch_results = await asyncio.gather(*tasks, return_exceptions=True)
                
                # Filter successful results above threshold
                for result in batch_results:
                    if isinstance(result, MatchResult) and result.similarity_score >= min_similarity:
                        results.append(result)
            
            # Sort by similarity score descending
            results.sort(key=lambda r: r.similarity_score, reverse=True)
            
            logger.info(f"Batch match completed: {len(results)} matches above {min_similarity:.2f}")
            return results
            
        except Exception as e:
            logger.error(f"Error in batch matching: {e}")
            return []
    
    async def find_duplicates(
        self,
        signatures: List[ContentSignature],
        similarity_threshold: Optional[float] = None
    ) -> List[Tuple[ContentSignature, ContentSignature, float]]:
        """Find duplicate content within a set of signatures"""
        try:
            threshold = similarity_threshold or self.similarity_threshold
            duplicates = []
            
            # Group by content type
            type_groups = {}
            for sig in signatures:
                if sig.content_type not in type_groups:
                    type_groups[sig.content_type] = []
                type_groups[sig.content_type].append(sig)
            
            # Find duplicates within each type
            for content_type, type_signatures in type_groups.items():
                for i in range(len(type_signatures)):
                    for j in range(i + 1, len(type_signatures)):
                        sig1 = type_signatures[i]
                        sig2 = type_signatures[j]
                        
                        result = await self.match_content(sig1, sig2)
                        
                        if result.similarity_score >= threshold:
                            duplicates.append((sig1, sig2, result.similarity_score))
            
            # Sort by similarity score descending
            duplicates.sort(key=lambda x: x[2], reverse=True)
            
            logger.info(f"Found {len(duplicates)} duplicates above {threshold:.2f}")
            return duplicates
            
        except Exception as e:
            logger.error(f"Error finding duplicates: {e}")
            return []
    
    def _cache_signature(self, signature -> None: ContentSignature) -> None:
        """Cache signature for performance"""
        try:
            # Implement LRU cache behavior
            if len(self.signature_cache) >= self.cache_max_size:
                # Remove oldest signature
                oldest_key = next(iter(self.signature_cache))
                del self.signature_cache[oldest_key]
            
            self.signature_cache[signature.content_id] = signature
            
        except Exception as e:
            logger.error(f"Error caching signature: {e}")
    
    def get_cached_signature(self, content_id: str) -> Optional[ContentSignature]:
        """Retrieve signature from cache"""
        return self.signature_cache.get(content_id)
    
    def clear_cache(self) -> None:
        """
Clear signature cache"""
        self.signature_cache.clear()
        logger.info("Signature cache cleared")
    
    async def get_matching_statistics(self) -> Dict[str, Any]:
        """Get matching engine statistics"""
        try:
            stats = {
                'cache_size': len(self.signature_cache),
                'cache_max_size': self.cache_max_size,
                'similarity_threshold': self.similarity_threshold,
                'batch_size': self.batch_size,
                'max_concurrent_matches': self.max_concurrent_matches,
                'supported_types': ['audio', 'video', 'text'],
                'algorithms': [alg.value for alg in MatchingAlgorithm],
                'confidence_levels': [conf.value for conf in MatchConfidence]
            }
            
            return stats
            
        except Exception as e:
            logger.error(f"Error getting matching statistics: {e}")
            return {}
    
    async def shutdown(self) -> None:
        """Shutdown matching engine"""
        try:
            self.executor.shutdown(wait=True)
            self.clear_cache()
            logger.info("Content matching engine shutdown complete")
            
        except Exception as e:
            logger.error(f"Error shutting down matching engine: {e}")


# Global instance
matching_engine = ContentMatchingEngine()


async def get_matching_engine() -> ContentMatchingEngine:
    """Get the global content matching engine instance"""
    return matching_engine


__all__ = [
    'ContentMatchingEngine',
    'ContentSignature',
    'MatchResult',
    'MatchingAlgorithm',
    'MatchConfidence',
    'AudioMatcher',
    'VideoMatcher',
    'TextMatcher',
    'get_matching_engine'
]
