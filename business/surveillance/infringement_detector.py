"""🚨 Infringement Detection Engine - IA Influencer Agent Surveillance Module
==========================================================================

Advanced AI-powered infringement detection system for multi-format content
using machine learning and fingerprinting technologies.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: © 2025 Fahed Mlaiel. All rights reserved.
"""
import asyncio
import logging
import time
import hashlib
from typing import Dict, List, Optional, Any, Union, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
import numpy as np
import json

logger = logging.getLogger(__name__)


class InfringementType(Enum):
    """Types of content infringement"""
    EXACT_COPY = "exact_copy"
    PARTIAL_COPY = "partial_copy"
    DERIVATIVE_WORK = "derivative_work"
    UNAUTHORIZED_REMIX = "unauthorized_remix"
    THUMBNAIL_THEFT = "thumbnail_theft"
    METADATA_COPYING = "metadata_copying"
    STYLE_IMITATION = "style_imitation"


class RiskLevel(Enum):
    """Risk levels for infringement"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class ContentFingerprint:
    """Fingerprint data for content identification"""
    fingerprint_id: str
    content_id: str
    content_type: str  # audio, video, image, text
    fingerprint_data: Dict[str, Any]
    quality_score: float
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    
    # Audio fingerprints
    audio_hash: Optional[str] = None
    spectral_features: Optional[List[float]] = None
    tempo: Optional[float] = None
    key: Optional[str] = None
    
    # Video fingerprints
    video_hash: Optional[str] = None
    frame_hashes: Optional[List[str]] = None
    scene_descriptors: Optional[List[Dict[str, Any]]] = None
    
    # Image fingerprints
    image_hash: Optional[str] = None
    perceptual_hash: Optional[str] = None
    color_histogram: Optional[List[float]] = None
    visual_features: Optional[List[float]] = None
    
    # Text fingerprints
    text_hash: Optional[str] = None
    semantic_vectors: Optional[List[float]] = None
    style_features: Optional[Dict[str, Any]] = None
    keywords: Optional[List[str]] = None


@dataclass
class InfringementMatch:
    """Detected infringement match"""
    match_id: str
    original_content_id: str
    infringing_url: str
    platform: str
    infringement_type: InfringementType
    risk_level: RiskLevel
    similarity_score: float
    confidence_score: float
    detected_features: Dict[str, Any]
    estimated_revenue_loss: float
    uploader_info: Dict[str, Any] = field(default_factory=dict)
    engagement_metrics: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class InfringementAnalysis:
    """Analysis result for infringement detection"""
    analysis_id: str
    original_content_id: str
    total_matches_analyzed: int
    infringements: List[InfringementMatch]
    estimated_total_revenue_loss: float
    threat_assessment: Dict[str, Any]
    recommendations: List[str]
    processing_time: float
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


class AudioFingerprintMatcher:
    """Audio content fingerprint matching"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.similarity_threshold = config.get("audio_similarity_threshold", 0.85)
    
    async def analyze_audio_similarity(
        self, 
        original_fingerprint: ContentFingerprint,
        candidate_audio: Dict[str, Any]
    ) -> Tuple[float, Dict[str, Any]]:
        """Analyze audio similarity between original and candidate"""
        similarity_score = 0.0
        analysis_details = {}
        
        try:
            # Simulate advanced audio fingerprinting analysis
            # In production, this would use libraries like:
            # - Chromaprint for audio fingerprinting
            # - librosa for spectral analysis
            # - PyAudio for audio processing
            
            # Hash-based comparison
            if original_fingerprint.audio_hash and candidate_audio.get("audio_hash"):
                hash_similarity = self._compare_hashes(
                    original_fingerprint.audio_hash,
                    candidate_audio["audio_hash"]
                )
                analysis_details["hash_similarity"] = hash_similarity
                similarity_score = max(similarity_score, hash_similarity)
            
            # Spectral features comparison
            if (original_fingerprint.spectral_features and 
                candidate_audio.get("spectral_features")):
                spectral_similarity = self._compare_spectral_features(
                    original_fingerprint.spectral_features,
                    candidate_audio["spectral_features"]
                )
                analysis_details["spectral_similarity"] = spectral_similarity
                similarity_score = max(similarity_score, spectral_similarity)
            
            # Tempo and key matching
            if original_fingerprint.tempo and candidate_audio.get("tempo"):
                tempo_similarity = self._compare_tempo(
                    original_fingerprint.tempo,
                    candidate_audio["tempo"]
                )
                analysis_details["tempo_similarity"] = tempo_similarity
            
            if original_fingerprint.key and candidate_audio.get("key"):
                key_match = original_fingerprint.key == candidate_audio["key"]
                analysis_details["key_match"] = key_match
                if key_match:
                    similarity_score += 0.1
            
            # Weighted combination of similarity scores
            similarity_score = min(similarity_score, 1.0)
            
        except Exception as e:
            logger.error(f"Audio similarity analysis failed: {e}")
            analysis_details["error"] = str(e)
        
        return similarity_score, analysis_details
    
    def _compare_hashes(self, hash1: str, hash2: str) -> float:
        """Compare audio hashes using Hamming distance"""
        if len(hash1) != len(hash2):
            return 0.0
        
        hamming_distance = sum(c1 != c2 for c1, c2 in zip(hash1, hash2))
        similarity = 1.0 - (hamming_distance / len(hash1))
        return similarity
    
    def _compare_spectral_features(self, features1: List[float], features2: List[float]) -> float:
        """Compare spectral features using cosine similarity"""
        try:
            # Convert to numpy arrays
            f1 = np.array(features1)
            f2 = np.array(features2)
            
            # Ensure same length
            min_len = min(len(f1), len(f2))
            f1 = f1[:min_len]
            f2 = f2[:min_len]
            
            # Calculate cosine similarity
            dot_product = np.dot(f1, f2)
            norms = np.linalg.norm(f1) * np.linalg.norm(f2)
            
            if norms == 0:
                return 0.0
            
            similarity = dot_product / norms
            return max(0.0, similarity)  # Ensure non-negative
            
        except Exception as e:
            logger.error(f"Spectral feature comparison failed: {e}")
            return 0.0
    
    def _compare_tempo(self, tempo1: float, tempo2: float) -> float:
        """Compare tempo similarity"""
        tempo_diff = abs(tempo1 - tempo2)
        max_diff = 20.0  # Max acceptable BPM difference
        
        if tempo_diff <= max_diff:
            return 1.0 - (tempo_diff / max_diff)
        return 0.0


class VideoFingerprintMatcher:
    """Video content fingerprint matching"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.similarity_threshold = config.get("video_similarity_threshold", 0.80)
    
    async def analyze_video_similarity(
        self, 
        original_fingerprint: ContentFingerprint,
        candidate_video: Dict[str, Any]
    ) -> Tuple[float, Dict[str, Any]]:
        """Analyze video similarity between original and candidate"""
        similarity_score = 0.0
        analysis_details = {}
        
        try:
            # Video hash comparison
            if original_fingerprint.video_hash and candidate_video.get("video_hash"):
                hash_similarity = self._compare_video_hashes(
                    original_fingerprint.video_hash,
                    candidate_video["video_hash"]
                )
                analysis_details["hash_similarity"] = hash_similarity
                similarity_score = max(similarity_score, hash_similarity)
            
            # Frame-by-frame comparison
            if (original_fingerprint.frame_hashes and 
                candidate_video.get("frame_hashes")):
                frame_similarity = self._compare_frame_sequences(
                    original_fingerprint.frame_hashes,
                    candidate_video["frame_hashes"]
                )
                analysis_details["frame_similarity"] = frame_similarity
                similarity_score = max(similarity_score, frame_similarity)
            
            # Scene descriptor comparison
            if (original_fingerprint.scene_descriptors and 
                candidate_video.get("scene_descriptors")):
                scene_similarity = self._compare_scene_descriptors(
                    original_fingerprint.scene_descriptors,
                    candidate_video["scene_descriptors"]
                )
                analysis_details["scene_similarity"] = scene_similarity
                similarity_score = max(similarity_score, scene_similarity)
            
        except Exception as e:
            logger.error(f"Video similarity analysis failed: {e}")
            analysis_details["error"] = str(e)
        
        return similarity_score, analysis_details
    
    def _compare_video_hashes(self, hash1: str, hash2: str) -> float:
        """Compare video hashes"""
        return self._hamming_similarity(hash1, hash2)
    
    def _compare_frame_sequences(self, frames1: List[str], frames2: List[str]) -> float:
        """Compare frame hash sequences"""
        if not frames1 or not frames2:
            return 0.0
        
        # Find longest common subsequence of similar frames
        matching_frames = 0
        total_frames = max(len(frames1), len(frames2))
        
        for i, frame1 in enumerate(frames1):
            for j, frame2 in enumerate(frames2):
                if abs(i - j) <= 5:  # Allow some temporal shift
                    frame_similarity = self._hamming_similarity(frame1, frame2)
                    if frame_similarity > 0.9:
                        matching_frames += 1
                        break
        
        return matching_frames / total_frames
    
    def _compare_scene_descriptors(
        self, 
        scenes1: List[Dict[str, Any]], 
        scenes2: List[Dict[str, Any]]
    ) -> float:
        """Compare scene descriptors"""
        if not scenes1 or not scenes2:
            return 0.0
        
        # Simplified scene comparison
        matching_scenes = 0
        
        for scene1 in scenes1:
            for scene2 in scenes2:
                # Compare scene features (simplified)
                if self._scenes_similar(scene1, scene2):
                    matching_scenes += 1
                    break
        
        return matching_scenes / max(len(scenes1), len(scenes2))
    
    def _scenes_similar(self, scene1: Dict[str, Any], scene2: Dict[str, Any]) -> bool:
        """Check if two scenes are similar"""
        # Simplified scene similarity check
        color1 = scene1.get("dominant_colors", [])
        color2 = scene2.get("dominant_colors", [])
        
        if color1 and color2:
            color_similarity = self._compare_color_lists(color1, color2)
            return color_similarity > 0.7
        
        return False
    
    def _compare_color_lists(self, colors1: List, colors2: List) -> float:
        """Compare color lists"""
        # Simplified color comparison
        if not colors1 or not colors2:
            return 0.0
        
        return 0.8  # Placeholder similarity score
    
    def _hamming_similarity(self, hash1: str, hash2: str) -> float:
        """Calculate Hamming similarity between hashes"""
        if len(hash1) != len(hash2):
            return 0.0
        
        hamming_distance = sum(c1 != c2 for c1, c2 in zip(hash1, hash2))
        return 1.0 - (hamming_distance / len(hash1))


class ImageFingerprintMatcher:
    """Image content fingerprint matching"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.similarity_threshold = config.get("image_similarity_threshold", 0.90)
    
    async def analyze_image_similarity(
        self, 
        original_fingerprint: ContentFingerprint,
        candidate_image: Dict[str, Any]
    ) -> Tuple[float, Dict[str, Any]]:
        """Analyze image similarity between original and candidate"""
        similarity_score = 0.0
        analysis_details = {}
        
        try:
            # Perceptual hash comparison
            if original_fingerprint.perceptual_hash and candidate_image.get("perceptual_hash"):
                phash_similarity = self._compare_perceptual_hashes(
                    original_fingerprint.perceptual_hash,
                    candidate_image["perceptual_hash"]
                )
                analysis_details["perceptual_hash_similarity"] = phash_similarity
                similarity_score = max(similarity_score, phash_similarity)
            
            # Color histogram comparison
            if (original_fingerprint.color_histogram and 
                candidate_image.get("color_histogram")):
                color_similarity = self._compare_color_histograms(
                    original_fingerprint.color_histogram,
                    candidate_image["color_histogram"]
                )
                analysis_details["color_similarity"] = color_similarity
                similarity_score = max(similarity_score, color_similarity)
            
            # Visual features comparison
            if (original_fingerprint.visual_features and 
                candidate_image.get("visual_features")):
                feature_similarity = self._compare_visual_features(
                    original_fingerprint.visual_features,
                    candidate_image["visual_features"]
                )
                analysis_details["visual_feature_similarity"] = feature_similarity
                similarity_score = max(similarity_score, feature_similarity)
            
        except Exception as e:
            logger.error(f"Image similarity analysis failed: {e}")
            analysis_details["error"] = str(e)
        
        return similarity_score, analysis_details
    
    def _compare_perceptual_hashes(self, hash1: str, hash2: str) -> float:
        """Compare perceptual hashes"""
        return self._hamming_similarity(hash1, hash2)
    
    def _compare_color_histograms(self, hist1: List[float], hist2: List[float]) -> float:
        """Compare color histograms using correlation"""
        try:
            h1 = np.array(hist1)
            h2 = np.array(hist2)
            
            # Ensure same length
            min_len = min(len(h1), len(h2))
            h1 = h1[:min_len]
            h2 = h2[:min_len]
            
            # Calculate correlation
            correlation = np.corrcoef(h1, h2)[0, 1]
            return max(0.0, correlation)
            
        except Exception as e:
            logger.error(f"Color histogram comparison failed: {e}")
            return 0.0
    
    def _compare_visual_features(self, features1: List[float], features2: List[float]) -> float:
        """Compare visual features using cosine similarity"""
        try:
            f1 = np.array(features1)
            f2 = np.array(features2)
            
            # Calculate cosine similarity
            dot_product = np.dot(f1, f2)
            norms = np.linalg.norm(f1) * np.linalg.norm(f2)
            
            if norms == 0:
                return 0.0
            
            similarity = dot_product / norms
            return max(0.0, similarity)
            
        except Exception as e:
            logger.error(f"Visual feature comparison failed: {e}")
            return 0.0
    
    def _hamming_similarity(self, hash1: str, hash2: str) -> float:
        """Calculate Hamming similarity"""
        if len(hash1) != len(hash2):
            return 0.0
        
        hamming_distance = sum(c1 != c2 for c1, c2 in zip(hash1, hash2))
        return 1.0 - (hamming_distance / len(hash1))


class TextFingerprintMatcher:
    """Text content fingerprint matching"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.similarity_threshold = config.get("text_similarity_threshold", 0.85)
    
    async def analyze_text_similarity(
        self, 
        original_fingerprint: ContentFingerprint,
        candidate_text: Dict[str, Any]
    ) -> Tuple[float, Dict[str, Any]]:
        """Analyze text similarity between original and candidate"""
        similarity_score = 0.0
        analysis_details = {}
        
        try:
            # Semantic vector comparison
            if (original_fingerprint.semantic_vectors and 
                candidate_text.get("semantic_vectors")):
                semantic_similarity = self._compare_semantic_vectors(
                    original_fingerprint.semantic_vectors,
                    candidate_text["semantic_vectors"]
                )
                analysis_details["semantic_similarity"] = semantic_similarity
                similarity_score = max(similarity_score, semantic_similarity)
            
            # Keyword overlap
            if original_fingerprint.keywords and candidate_text.get("keywords"):
                keyword_similarity = self._compare_keywords(
                    original_fingerprint.keywords,
                    candidate_text["keywords"]
                )
                analysis_details["keyword_similarity"] = keyword_similarity
                similarity_score = max(similarity_score, keyword_similarity)
            
            # Style features comparison
            if (original_fingerprint.style_features and 
                candidate_text.get("style_features")):
                style_similarity = self._compare_style_features(
                    original_fingerprint.style_features,
                    candidate_text["style_features"]
                )
                analysis_details["style_similarity"] = style_similarity
                similarity_score = max(similarity_score, style_similarity * 0.5)  # Lower weight for style
            
        except Exception as e:
            logger.error(f"Text similarity analysis failed: {e}")
            analysis_details["error"] = str(e)
        
        return similarity_score, analysis_details
    
    def _compare_semantic_vectors(self, vectors1: List[float], vectors2: List[float]) -> float:
        """Compare semantic vectors using cosine similarity"""
        try:
            v1 = np.array(vectors1)
            v2 = np.array(vectors2)
            
            dot_product = np.dot(v1, v2)
            norms = np.linalg.norm(v1) * np.linalg.norm(v2)
            
            if norms == 0:
                return 0.0
            
            similarity = dot_product / norms
            return max(0.0, similarity)
            
        except Exception as e:
            logger.error(f"Semantic vector comparison failed: {e}")
            return 0.0
    
    def _compare_keywords(self, keywords1: List[str], keywords2: List[str]) -> float:
        """Compare keyword lists using Jaccard similarity"""
        set1 = set(keyword.lower() for keyword in keywords1)
        set2 = set(keyword.lower() for keyword in keywords2)
        
        intersection = len(set1.intersection(set2))
        union = len(set1.union(set2))
        
        if union == 0:
            return 0.0
        
        return intersection / union
    
    def _compare_style_features(
        self, 
        features1: Dict[str, Any], 
        features2: Dict[str, Any]
    ) -> float:
        """Compare writing style features"""
        similarity_scores = []
        
        # Compare numerical features
        numeric_features = ["avg_sentence_length", "avg_word_length", "readability_score"]
        
        for feature in numeric_features:
            if feature in features1 and feature in features2:
                val1 = features1[feature]
                val2 = features2[feature]
                
                # Normalized difference (closer to 0 means more similar)
                max_val = max(val1, val2, 1.0)  # Prevent division by zero
                diff = abs(val1 - val2) / max_val
                similarity = 1.0 - diff
                similarity_scores.append(similarity)
        
        if similarity_scores:
            return sum(similarity_scores) / len(similarity_scores)
        
        return 0.0


class InfringementDetectionEngine:
    """
    Advanced infringement detection engine using AI and ML techniques
    for comprehensive content analysis and similarity matching
    """
    
    def __init__(self, surveillance_config):
        self.config = surveillance_config
        self.audio_matcher = AudioFingerprintMatcher(surveillance_config.__dict__)
        self.video_matcher = VideoFingerprintMatcher(surveillance_config.__dict__)
        self.image_matcher = ImageFingerprintMatcher(surveillance_config.__dict__)
        self.text_matcher = TextFingerprintMatcher(surveillance_config.__dict__)
        self.initialized = False
    
    async def initialize(self) -> None:
        """Initialize the infringement detection engine"""
        try:
            # Initialize AI models and resources
            # In production, this would load ML models for feature extraction
            self.initialized = True
            logger.info("Infringement Detection Engine initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize Infringement Detection Engine: {e}")
            raise
    
    async def analyze_results(
        self,
        original_fingerprints: Dict[str, Any],
        crawling_results: Dict[str, Any],
        similarity_threshold: float = 0.85
    ) -> InfringementAnalysis:
        """Analyze crawling results for content infringements"""
        start_time = time.time()
        analysis_id = f"analysis_{int(time.time())}_{hash(str(original_fingerprints))}"
        
        # Create fingerprint objects from original data
        fingerprints = await self._create_fingerprints(original_fingerprints)
        
        all_infringements = []
        total_matches_analyzed = 0
        estimated_total_revenue_loss = 0.0
        
        try:
            # Analyze results from each platform
            for platform, platform_results in crawling_results.items():
                if isinstance(platform_results, dict) and "content_found" in platform_results:
                    content_items = platform_results["content_found"]
                    
                    for content_item in content_items:
                        total_matches_analyzed += 1
                        
                        # Analyze each content item for infringement
                        infringement_match = await self._analyze_content_item(
                            fingerprints, content_item, platform, similarity_threshold
                        )
                        
                        if infringement_match:
                            all_infringements.append(infringement_match)
                            estimated_total_revenue_loss += infringement_match.estimated_revenue_loss
            
            # Generate threat assessment
            threat_assessment = self._assess_threats(all_infringements)
            
            # Generate recommendations
            recommendations = self._generate_recommendations(all_infringements, threat_assessment)
            
            analysis = InfringementAnalysis(
                analysis_id=analysis_id,
                original_content_id=original_fingerprints.get("content_id", "unknown"),
                total_matches_analyzed=total_matches_analyzed,
                infringements=all_infringements,
                estimated_total_revenue_loss=estimated_total_revenue_loss,
                threat_assessment=threat_assessment,
                recommendations=recommendations,
                processing_time=time.time() - start_time
            )
            
            logger.info(
                f"Infringement analysis completed: {len(all_infringements)} "
                f"infringements found from {total_matches_analyzed} matches analyzed"
            )
            
            return analysis
            
        except Exception as e:
            logger.error(f"Infringement analysis failed: {e}")
            # Return empty analysis with error information
            return InfringementAnalysis(
                analysis_id=analysis_id,
                original_content_id=original_fingerprints.get("content_id", "unknown"),
                total_matches_analyzed=total_matches_analyzed,
                infringements=all_infringements,
                estimated_total_revenue_loss=0.0,
                threat_assessment={"error": str(e)},
                recommendations=["Review system logs for analysis errors"],
                processing_time=time.time() - start_time
            )
    
    async def _create_fingerprints(self, fingerprint_data: Dict[str, Any]) -> List[ContentFingerprint]:
        """Create fingerprint objects from raw data"""
        fingerprints = []
        
        content_types = fingerprint_data.get("content_types", ["mixed"])
        
        for content_type in content_types:
            fingerprint = ContentFingerprint(
                fingerprint_id=f"fp_{content_type}_{int(time.time())}",
                content_id=fingerprint_data.get("content_id", "unknown"),
                content_type=content_type,
                fingerprint_data=fingerprint_data,
                quality_score=fingerprint_data.get("quality_score", 0.8)
            )
            
            # Populate type-specific fingerprint data
            if content_type == "audio":
                fingerprint.audio_hash = fingerprint_data.get("audio_hash")
                fingerprint.spectral_features = fingerprint_data.get("spectral_features")
                fingerprint.tempo = fingerprint_data.get("tempo")
                fingerprint.key = fingerprint_data.get("key")
            
            elif content_type == "video":
                fingerprint.video_hash = fingerprint_data.get("video_hash")
                fingerprint.frame_hashes = fingerprint_data.get("frame_hashes")
                fingerprint.scene_descriptors = fingerprint_data.get("scene_descriptors")
            
            elif content_type == "image":
                fingerprint.image_hash = fingerprint_data.get("image_hash")
                fingerprint.perceptual_hash = fingerprint_data.get("perceptual_hash")
                fingerprint.color_histogram = fingerprint_data.get("color_histogram")
                fingerprint.visual_features = fingerprint_data.get("visual_features")
            
            elif content_type == "text":
                fingerprint.text_hash = fingerprint_data.get("text_hash")
                fingerprint.semantic_vectors = fingerprint_data.get("semantic_vectors")
                fingerprint.style_features = fingerprint_data.get("style_features")
                fingerprint.keywords = fingerprint_data.get("keywords")
            
            fingerprints.append(fingerprint)
        
        return fingerprints
    
    async def _analyze_content_item(
        self,
        fingerprints: List[ContentFingerprint],
        content_item: Dict[str, Any],
        platform: str,
        similarity_threshold: float
    ) -> Optional[InfringementMatch]:
        """Analyze a single content item for infringement"""
        best_match = None
        best_similarity = 0.0
        
        try:
            for fingerprint in fingerprints:
                similarity_score, analysis_details = await self._compare_fingerprints(
                    fingerprint, content_item
                )
                
                if similarity_score > best_similarity and similarity_score >= similarity_threshold:
                    best_similarity = similarity_score
                    
                    # Determine infringement type and risk level
                    infringement_type = self._determine_infringement_type(similarity_score, analysis_details)
                    risk_level = self._determine_risk_level(similarity_score, content_item, platform)
                    
                    # Estimate revenue loss
                    revenue_loss = self._estimate_revenue_loss(content_item, platform, similarity_score)
                    
                    best_match = InfringementMatch(
                        match_id=f"match_{platform}_{hash(content_item.get('url', ''))}",
                        original_content_id=fingerprint.content_id,
                        infringing_url=content_item.get("url", ""),
                        platform=platform,
                        infringement_type=infringement_type,
                        risk_level=risk_level,
                        similarity_score=similarity_score,
                        confidence_score=min(similarity_score * 1.1, 1.0),
                        detected_features=analysis_details,
                        estimated_revenue_loss=revenue_loss,
                        uploader_info={
                            "uploader_id": content_item.get("uploader_id", "unknown"),
                            "channel_name": content_item.get("channel_name", "unknown")
                        },
                        engagement_metrics={
                            "views": content_item.get("view_count", 0),
                            "likes": content_item.get("like_count", 0),
                            "shares": content_item.get("share_count", 0)
                        }
                    )
            
            return best_match
            
        except Exception as e:
            logger.error(f"Content item analysis failed: {e}")
            return None
    
    async def _compare_fingerprints(
        self,
        fingerprint: ContentFingerprint,
        content_item: Dict[str, Any]
    ) -> Tuple[float, Dict[str, Any]]:
        """Compare fingerprint with content item"""
        content_type = fingerprint.content_type
        
        if content_type == "audio":
            return await self.audio_matcher.analyze_audio_similarity(fingerprint, content_item)
        elif content_type == "video":
            return await self.video_matcher.analyze_video_similarity(fingerprint, content_item)
        elif content_type == "image":
            return await self.image_matcher.analyze_image_similarity(fingerprint, content_item)
        elif content_type == "text":
            return await self.text_matcher.analyze_text_similarity(fingerprint, content_item)
        else:
            # Generic comparison for mixed or unknown content
            return await self._generic_comparison(fingerprint, content_item)
    
    async def _generic_comparison(
        self,
        fingerprint: ContentFingerprint,
        content_item: Dict[str, Any]
    ) -> Tuple[float, Dict[str, Any]]:
        """Generic content comparison for mixed media"""
        similarity_scores = []
        analysis_details = {}
        
        # Title/metadata comparison
        if fingerprint.fingerprint_data.get("title") and content_item.get("title"):
            title_similarity = self._compare_titles(
                fingerprint.fingerprint_data["title"],
                content_item["title"]
            )
            similarity_scores.append(title_similarity)
            analysis_details["title_similarity"] = title_similarity
        
        # Keyword comparison
        if fingerprint.keywords and content_item.get("keywords"):
            keyword_similarity = self._compare_keyword_lists(
                fingerprint.keywords,
                content_item["keywords"]
            )
            similarity_scores.append(keyword_similarity)
            analysis_details["keyword_similarity"] = keyword_similarity
        
        # Overall similarity
        if similarity_scores:
            overall_similarity = max(similarity_scores)
        else:
            overall_similarity = 0.0
        
        return overall_similarity, analysis_details
    
    def _compare_titles(self, title1: str, title2: str) -> float:
        """Compare titles for similarity"""
        # Simple title comparison using word overlap
        words1 = set(title1.lower().split())
        words2 = set(title2.lower().split())
        
        if not words1 or not words2:
            return 0.0
        
        intersection = len(words1.intersection(words2))
        union = len(words1.union(words2))
        
        return intersection / union if union > 0 else 0.0
    
    def _compare_keyword_lists(self, keywords1: List[str], keywords2: List[str]) -> float:
        """Compare keyword lists"""
        set1 = set(k.lower() for k in keywords1)
        set2 = set(k.lower() for k in keywords2)
        
        intersection = len(set1.intersection(set2))
        union = len(set1.union(set2))
        
        return intersection / union if union > 0 else 0.0
    
    def _determine_infringement_type(
        self, 
        similarity_score: float, 
        analysis_details: Dict[str, Any]
    ) -> InfringementType:
        """Determine the type of infringement based on similarity analysis"""
        if similarity_score >= 0.98:
            return InfringementType.EXACT_COPY
        elif similarity_score >= 0.90:
            return InfringementType.PARTIAL_COPY
        elif similarity_score >= 0.85:
            return InfringementType.DERIVATIVE_WORK
        else:
            return InfringementType.STYLE_IMITATION
    
    def _determine_risk_level(
        self, 
        similarity_score: float, 
        content_item: Dict[str, Any], 
        platform: str
    ) -> RiskLevel:
        """Determine risk level of infringement"""
        view_count = content_item.get("view_count", 0)
        engagement = content_item.get("like_count", 0) + content_item.get("share_count", 0)
        
        # Base risk on similarity score
        if similarity_score >= 0.95:
            base_risk = RiskLevel.HIGH
        elif similarity_score >= 0.90:
            base_risk = RiskLevel.MEDIUM
        else:
            base_risk = RiskLevel.LOW
        
        # Escalate based on engagement
        if view_count > 100000 or engagement > 10000:
            if base_risk == RiskLevel.HIGH:
                return RiskLevel.CRITICAL
            elif base_risk == RiskLevel.MEDIUM:
                return RiskLevel.HIGH
            else:
                return RiskLevel.MEDIUM
        
        return base_risk
    
    def _estimate_revenue_loss(
        self, 
        content_item: Dict[str, Any], 
        platform: str, 
        similarity_score: float
    ) -> float:
        """Estimate potential revenue loss from infringement"""
        view_count = content_item.get("view_count", 0)
        
        # Platform-specific revenue estimation
        revenue_per_view = {
            "youtube": 0.001,
            "tiktok": 0.0005,
            "instagram": 0.0003,
            "facebook": 0.0004
        }
        
        base_rate = revenue_per_view.get(platform, 0.0005)
        
        # Adjust based on similarity (higher similarity = higher loss)
        adjusted_rate = base_rate * similarity_score
        
        return view_count * adjusted_rate
    
    def _assess_threats(self, infringements: List[InfringementMatch]) -> Dict[str, Any]:
        """Assess overall threat level from detected infringements"""
        if not infringements:
            return {
                "overall_threat_level": "none",
                "risk_distribution": {},
                "platform_analysis": {},
                "recommended_actions": []
            }
        
        # Analyze risk distribution
        risk_counts = {}
        platform_counts = {}
        total_revenue_at_risk = 0.0
        
        for infringement in infringements:
            # Risk level counts
            risk_level = infringement.risk_level.value
            risk_counts[risk_level] = risk_counts.get(risk_level, 0) + 1
            
            # Platform counts
            platform = infringement.platform
            platform_counts[platform] = platform_counts.get(platform, 0) + 1
            
            # Total revenue
            total_revenue_at_risk += infringement.estimated_revenue_loss
        
        # Determine overall threat level
        if risk_counts.get("critical", 0) > 0:
            overall_threat = "critical"
        elif risk_counts.get("high", 0) > 2:
            overall_threat = "high"
        elif risk_counts.get("high", 0) > 0 or risk_counts.get("medium", 0) > 3:
            overall_threat = "medium"
        else:
            overall_threat = "low"
        
        return {
            "overall_threat_level": overall_threat,
            "total_infringements": len(infringements),
            "risk_distribution": risk_counts,
            "platform_analysis": platform_counts,
            "total_revenue_at_risk": total_revenue_at_risk,
            "average_similarity_score": sum(inf.similarity_score for inf in infringements) / len(infringements),
            "recommended_actions": self._get_threat_actions(overall_threat, risk_counts)
        }
    
    def _get_threat_actions(self, threat_level: str, risk_counts: Dict[str, int]) -> List[str]:
        """Get recommended actions based on threat level"""
        actions = []
        
        if threat_level == "critical":
            actions.extend([
                "Immediate legal action required",
                "Issue emergency takedown notices",
                "Contact platform abuse teams directly",
                "Consider copyright enforcement services"
            ])
        elif threat_level == "high":
            actions.extend([
                "Issue DMCA takedown notices",
                "Monitor closely for new infringements",
                "Consider automated protection services",
                "Document all infringements for legal purposes"
            ])
        elif threat_level == "medium":
            actions.extend([
                "Send copyright notices to infringers",
                "Increase monitoring frequency",
                "Review content protection measures"
            ])
        else:
            actions.extend([
                "Continue regular monitoring",
                "Consider improved content watermarking"
            ])
        
        return actions
    
    def _generate_recommendations(
        self, 
        infringements: List[InfringementMatch],
        threat_assessment: Dict[str, Any]
    ) -> List[str]:
        """Generate actionable recommendations based on analysis"""
        recommendations = []
        
        if not infringements:
            recommendations.append("Continue monitoring - no infringements detected")
            return recommendations
        
        # Platform-specific recommendations
        platform_counts = threat_assessment.get("platform_analysis", {})
        for platform, count in platform_counts.items():
            if count >= 2:
                recommendations.append(f"Focus enforcement efforts on {platform} - {count} infringements detected")
        
        # Revenue-based recommendations
        total_revenue_at_risk = threat_assessment.get("total_revenue_at_risk", 0)
        if total_revenue_at_risk > 1000:
            recommendations.append("High revenue at risk - prioritize immediate action")
        
        # Risk-based recommendations
        risk_distribution = threat_assessment.get("risk_distribution", {})
        if risk_distribution.get("critical", 0) > 0:
            recommendations.append("Critical infringements detected - engage legal counsel")
        if risk_distribution.get("high", 0) > 1:
            recommendations.append("Multiple high-risk infringements - escalate protection measures")
        
        # General recommendations
        recommendations.extend([
            "Document all infringements for potential legal action",
            "Consider implementing stronger content watermarking",
            "Review and update content protection strategies"
        ])
        
        return recommendations[:10]  # Limit to top 10 recommendations
    
    async def health_check(self) -> Dict[str, Any]:
        """Perform health check on detection engine"""
        return {
            "engine": "healthy" if self.initialized else "unhealthy",
            "matchers": {
                "audio": "ready",
                "video": "ready", 
                "image": "ready",
                "text": "ready"
            },
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    
    async def shutdown(self) -> None:
        """Gracefully shutdown detection engine"""
        logger.info("Shutting down Infringement Detection Engine")
        self.initialized = False
        logger.info("Infringement Detection Engine shutdown complete")


# Export main components
__all__ = [
    "InfringementDetectionEngine",
    "ContentFingerprint",
    "InfringementMatch", 
    "InfringementAnalysis",
    "InfringementType",
    "RiskLevel",
    "AudioFingerprintMatcher",
    "VideoFingerprintMatcher",
    "ImageFingerprintMatcher",
    "TextFingerprintMatcher"
]
