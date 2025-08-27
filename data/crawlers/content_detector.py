"""
Content Detector Implementation
==============================

Advanced content detection system for identifying copyrighted material across platforms.
Implements sophisticated fingerprinting and similarity matching algorithms.

Team Expertise: Lead Dev IA + Backend Senior + ML Engineer + DBA + Security + 
Microservices + Audio + DevOps + IA Prompt Engineer

Author: Fahed Mlaiel (mlaiel@live.de)
Email: mlaiel@live.de
Copyright: © 2025 Fahed Mlaiel - All Rights Reserved

⚠️  CRITICAL WARNING ⚠️
This code is PROPRIETARY and CONFIDENTIAL intellectual property.
Any unauthorized use, reproduction, distribution, or reverse engineering 
is STRICTLY PROHIBITED and will result in immediate legal action.

Unauthorized copying or theft of this concept, code, or methodology 
will be prosecuted to the FULL EXTENT OF THE LAW under German and 
International Copyright Laws.

For licensing inquiries, contact: mlaiel@live.de
"""

import asyncio
import hashlib
import cv2
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple, Union
from dataclasses import dataclass, field
from enum import Enum
import json
import io
from PIL import Image, ImageHash
import librosa
import tensorflow as tf
from transformers import CLIPProcessor, CLIPModel
import torch

from ..fingerprinting.audio_fingerprint import AudioFingerprinter
from ..fingerprinting.video_fingerprint import VideoFingerprinter
from ..fingerprinting.image_fingerprint import ImageFingerprinter
from ..fingerprinting.text_fingerprint import TextFingerprinter
from ..fingerprinting.vector_matcher import VectorMatcher


class DetectionType(Enum):
    """Types of content detection"""
    EXACT_MATCH = "exact_match"
    NEAR_DUPLICATE = "near_duplicate"
    DERIVATIVE_WORK = "derivative_work"
    SIMILAR_CONTENT = "similar_content"
    REMIX_COVER = "remix_cover"
    SAMPLE_USAGE = "sample_usage"
    FALSE_POSITIVE = "false_positive"


class ContentType(Enum):
    """Types of content that can be detected"""
    AUDIO = "audio"
    VIDEO = "video"
    IMAGE = "image"
    TEXT = "text"
    MIXED_MEDIA = "mixed_media"


@dataclass
class DetectionResult:
    """Result of content detection analysis"""
    detection_id: str
    content_type: ContentType
    detection_type: DetectionType
    similarity_score: float
    confidence_score: float
    original_content_id: str
    detected_content_url: str
    platform: str
    evidence: Dict[str, Any]
    metadata: Dict[str, Any]
    timestamp: datetime = field(default_factory=datetime.utcnow)
    processing_time_ms: float = 0.0
    fingerprint_matches: List[Dict[str, Any]] = field(default_factory=list)
    ai_analysis: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ContentFingerprint:
    """Comprehensive content fingerprint"""
    content_id: str
    content_type: ContentType
    audio_fingerprint: Optional[Dict[str, Any]] = None
    video_fingerprint: Optional[Dict[str, Any]] = None
    image_fingerprint: Optional[Dict[str, Any]] = None
    text_fingerprint: Optional[Dict[str, Any]] = None
    vector_embedding: Optional[List[float]] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)


class ContentDetector:
    """
    Advanced content detection system for identifying copyrighted material.
    
    Features:
    - Multi-modal content fingerprinting
    - AI-powered similarity detection
    - Cross-platform content matching
    - Real-time detection capabilities
    - Advanced false positive filtering
    - Evidence collection and documentation
    """
    
    def __init__(self, vector_matcher: VectorMatcher):
        """
        Initialize content detector.
        
        Args:
            vector_matcher: Vector matching service for similarity detection
        """
        self.vector_matcher = vector_matcher
        self.logger = logging.getLogger(__name__)
        
        # Fingerprinting engines
        self.audio_fingerprinter = AudioFingerprinter()
        self.video_fingerprinter = VideoFingerprinter()
        self.image_fingerprinter = ImageFingerprinter()
        self.text_fingerprinter = TextFingerprinter()
        
        # AI models for advanced detection
        self.clip_model = None
        self.clip_processor = None
        
        # Detection thresholds
        self.similarity_thresholds = {
            DetectionType.EXACT_MATCH: 0.95,
            DetectionType.NEAR_DUPLICATE: 0.85,
            DetectionType.DERIVATIVE_WORK: 0.75,
            DetectionType.SIMILAR_CONTENT: 0.65,
            DetectionType.REMIX_COVER: 0.60,
            DetectionType.SAMPLE_USAGE: 0.55
        }
        
        # Performance metrics
        self.detection_stats = {
            'total_detections': 0,
            'true_positives': 0,
            'false_positives': 0,
            'processing_times': []
        }
        
        # Initialize AI models
        asyncio.create_task(self._initialize_ai_models())
    
    async def _initialize_ai_models(self):
        """Initialize AI models for content detection"""
        try:
            # Initialize CLIP model for cross-modal similarity
            self.clip_model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32")
            self.clip_processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")
            
            self.logger.info("AI models initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize AI models: {str(e)}")
    
    async def create_content_fingerprint(self, content_data: bytes, 
                                       content_type: ContentType,
                                       metadata: Dict[str, Any] = None) -> ContentFingerprint:
        """
        Create comprehensive fingerprint for content.
        
        Args:
            content_data: Raw content data
            content_type: Type of content
            metadata: Optional metadata about the content
            
        Returns:
            ContentFingerprint object
        """
        try:
            start_time = datetime.utcnow()
            
            content_id = hashlib.sha256(content_data).hexdigest()
            fingerprint = ContentFingerprint(
                content_id=content_id,
                content_type=content_type,
                metadata=metadata or {}
            )
            
            # Generate type-specific fingerprints
            if content_type == ContentType.AUDIO:
                fingerprint.audio_fingerprint = await self._generate_audio_fingerprint(content_data)
                
            elif content_type == ContentType.VIDEO:
                fingerprint.video_fingerprint = await self._generate_video_fingerprint(content_data)
                # Extract audio from video for audio fingerprinting
                audio_data = await self._extract_audio_from_video(content_data)
                if audio_data:
                    fingerprint.audio_fingerprint = await self._generate_audio_fingerprint(audio_data)
                
            elif content_type == ContentType.IMAGE:
                fingerprint.image_fingerprint = await self._generate_image_fingerprint(content_data)
                
            elif content_type == ContentType.TEXT:
                text_content = content_data.decode('utf-8', errors='ignore')
                fingerprint.text_fingerprint = await self._generate_text_fingerprint(text_content)
            
            # Generate unified vector embedding using CLIP
            if self.clip_model:
                fingerprint.vector_embedding = await self._generate_clip_embedding(content_data, content_type)
            
            processing_time = (datetime.utcnow() - start_time).total_seconds() * 1000
            self.logger.info(f"Created fingerprint for {content_type.value} content in {processing_time:.2f}ms")
            
            return fingerprint
            
        except Exception as e:
            self.logger.error(f"Error creating content fingerprint: {str(e)}")
            raise
    
    async def detect_content_matches(self, target_content: bytes,
                                   content_type: ContentType,
                                   reference_fingerprints: List[ContentFingerprint],
                                   platform: str = "unknown") -> List[DetectionResult]:
        """
        Detect matches between target content and reference fingerprints.
        
        Args:
            target_content: Content to analyze
            content_type: Type of target content
            reference_fingerprints: List of reference fingerprints to compare against
            platform: Platform where content was found
            
        Returns:
            List of detection results
        """
        try:
            start_time = datetime.utcnow()
            
            # Create fingerprint for target content
            target_fingerprint = await self.create_content_fingerprint(target_content, content_type)
            
            detection_results = []
            
            # Compare against each reference fingerprint
            for ref_fingerprint in reference_fingerprints:
                try:
                    result = await self._compare_fingerprints(
                        target_fingerprint, ref_fingerprint, platform
                    )
                    
                    if result and result.similarity_score >= self.similarity_thresholds[DetectionType.SAMPLE_USAGE]:
                        detection_results.append(result)
                        
                except Exception as e:
                    self.logger.warning(f"Error comparing fingerprints: {str(e)}")
                    continue
            
            # Sort by similarity score
            detection_results.sort(key=lambda x: x.similarity_score, reverse=True)
            
            # Update statistics
            processing_time = (datetime.utcnow() - start_time).total_seconds() * 1000
            self.detection_stats['total_detections'] += 1
            self.detection_stats['processing_times'].append(processing_time)
            
            self.logger.info(f"Detected {len(detection_results)} potential matches in {processing_time:.2f}ms")
            
            return detection_results
            
        except Exception as e:
            self.logger.error(f"Error detecting content matches: {str(e)}")
            return []
    
    async def analyze_detection_accuracy(self, detections: List[DetectionResult],
                                       ground_truth: List[Dict[str, Any]]) -> Dict[str, float]:
        """
        Analyze detection accuracy against ground truth data.
        
        Args:
            detections: List of detection results
            ground_truth: List of ground truth annotations
            
        Returns:
            Accuracy metrics
        """
        try:
            true_positives = 0
            false_positives = 0
            false_negatives = 0
            
            # Create sets for comparison
            detected_matches = {(d.original_content_id, d.detected_content_url) for d in detections}
            true_matches = {(gt['original_id'], gt['detected_url']) for gt in ground_truth}
            
            # Calculate metrics
            true_positives = len(detected_matches.intersection(true_matches))
            false_positives = len(detected_matches - true_matches)
            false_negatives = len(true_matches - detected_matches)
            
            # Calculate precision, recall, F1
            precision = true_positives / (true_positives + false_positives) if (true_positives + false_positives) > 0 else 0
            recall = true_positives / (true_positives + false_negatives) if (true_positives + false_negatives) > 0 else 0
            f1_score = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
            
            accuracy_metrics = {
                'precision': precision,
                'recall': recall,
                'f1_score': f1_score,
                'true_positives': true_positives,
                'false_positives': false_positives,
                'false_negatives': false_negatives,
                'total_detections': len(detections),
                'total_ground_truth': len(ground_truth)
            }
            
            # Update global statistics
            self.detection_stats['true_positives'] += true_positives
            self.detection_stats['false_positives'] += false_positives
            
            return accuracy_metrics
            
        except Exception as e:
            self.logger.error(f"Error analyzing detection accuracy: {str(e)}")
            return {}
    
    async def filter_false_positives(self, detections: List[DetectionResult],
                                   confidence_threshold: float = 0.8) -> List[DetectionResult]:
        """
        Filter out likely false positives using ML techniques.
        
        Args:
            detections: List of detection results
            confidence_threshold: Minimum confidence score
            
        Returns:
            Filtered detection results
        """
        try:
            filtered_detections = []
            
            for detection in detections:
                # Apply multiple filtering criteria
                if await self._is_likely_true_positive(detection, confidence_threshold):
                    filtered_detections.append(detection)
                else:
                    detection.detection_type = DetectionType.FALSE_POSITIVE
            
            self.logger.info(f"Filtered {len(detections) - len(filtered_detections)} false positives")
            
            return filtered_detections
            
        except Exception as e:
            self.logger.error(f"Error filtering false positives: {str(e)}")
            return detections
    
    async def batch_detection(self, content_batch: List[Tuple[bytes, ContentType]],
                            reference_fingerprints: List[ContentFingerprint],
                            platform: str = "unknown") -> List[List[DetectionResult]]:
        """
        Perform batch content detection for multiple items.
        
        Args:
            content_batch: List of (content_data, content_type) tuples
            reference_fingerprints: Reference fingerprints to compare against
            platform: Platform where content was found
            
        Returns:
            List of detection results for each content item
        """
        try:
            batch_results = []
            
            # Process content items concurrently
            tasks = []
            for content_data, content_type in content_batch:
                task = asyncio.create_task(
                    self.detect_content_matches(content_data, content_type, reference_fingerprints, platform)
                )
                tasks.append(task)
            
            # Wait for all detections to complete
            batch_results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Filter out exceptions
            valid_results = []
            for result in batch_results:
                if isinstance(result, list):
                    valid_results.append(result)
                else:
                    self.logger.error(f"Batch detection error: {str(result)}")
                    valid_results.append([])
            
            self.logger.info(f"Completed batch detection for {len(content_batch)} items")
            
            return valid_results
            
        except Exception as e:
            self.logger.error(f"Error in batch detection: {str(e)}")
            return []
    
    # Private helper methods
    
    async def _generate_audio_fingerprint(self, audio_data: bytes) -> Dict[str, Any]:
        """Generate audio fingerprint"""
        try:
            return await self.audio_fingerprinter.generate_fingerprint(audio_data)
        except Exception as e:
            self.logger.error(f"Error generating audio fingerprint: {str(e)}")
            return {}
    
    async def _generate_video_fingerprint(self, video_data: bytes) -> Dict[str, Any]:
        """Generate video fingerprint"""
        try:
            return await self.video_fingerprinter.generate_fingerprint(video_data)
        except Exception as e:
            self.logger.error(f"Error generating video fingerprint: {str(e)}")
            return {}
    
    async def _generate_image_fingerprint(self, image_data: bytes) -> Dict[str, Any]:
        """Generate image fingerprint"""
        try:
            return await self.image_fingerprinter.generate_fingerprint(image_data)
        except Exception as e:
            self.logger.error(f"Error generating image fingerprint: {str(e)}")
            return {}
    
    async def _generate_text_fingerprint(self, text_content: str) -> Dict[str, Any]:
        """Generate text fingerprint"""
        try:
            return await self.text_fingerprinter.generate_fingerprint(text_content)
        except Exception as e:
            self.logger.error(f"Error generating text fingerprint: {str(e)}")
            return {}
    
    async def _generate_clip_embedding(self, content_data: bytes, 
                                     content_type: ContentType) -> Optional[List[float]]:
        """Generate CLIP embedding for cross-modal similarity"""
        try:
            if not self.clip_model or not self.clip_processor:
                return None
            
            if content_type == ContentType.IMAGE:
                # Process image
                image = Image.open(io.BytesIO(content_data))
                inputs = self.clip_processor(images=image, return_tensors="pt")
                
                with torch.no_grad():
                    image_features = self.clip_model.get_image_features(**inputs)
                    embedding = image_features.squeeze().numpy().tolist()
                
                return embedding
                
            elif content_type == ContentType.TEXT:
                # Process text
                text = content_data.decode('utf-8', errors='ignore')
                inputs = self.clip_processor(text=text, return_tensors="pt", padding=True, truncation=True)
                
                with torch.no_grad():
                    text_features = self.clip_model.get_text_features(**inputs)
                    embedding = text_features.squeeze().numpy().tolist()
                
                return embedding
            
            return None
            
        except Exception as e:
            self.logger.error(f"Error generating CLIP embedding: {str(e)}")
            return None
    
    async def _extract_audio_from_video(self, video_data: bytes) -> Optional[bytes]:
        """Extract audio track from video data"""
        try:
            # This would use ffmpeg or similar to extract audio
            # Placeholder implementation
            return None
            
        except Exception as e:
            self.logger.error(f"Error extracting audio from video: {str(e)}")
            return None
    
    async def _compare_fingerprints(self, target: ContentFingerprint,
                                  reference: ContentFingerprint,
                                  platform: str) -> Optional[DetectionResult]:
        """Compare two fingerprints and generate detection result"""
        try:
            detection_id = f"det_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{target.content_id[:8]}"
            
            # Calculate similarity scores for each modality
            similarity_scores = {}
            fingerprint_matches = []
            
            # Audio similarity
            if target.audio_fingerprint and reference.audio_fingerprint:
                audio_sim = await self._calculate_audio_similarity(
                    target.audio_fingerprint, reference.audio_fingerprint
                )
                similarity_scores['audio'] = audio_sim
                if audio_sim > 0.5:
                    fingerprint_matches.append({
                        'type': 'audio',
                        'similarity': audio_sim,
                        'evidence': 'Audio fingerprint match'
                    })
            
            # Video similarity
            if target.video_fingerprint and reference.video_fingerprint:
                video_sim = await self._calculate_video_similarity(
                    target.video_fingerprint, reference.video_fingerprint
                )
                similarity_scores['video'] = video_sim
                if video_sim > 0.5:
                    fingerprint_matches.append({
                        'type': 'video',
                        'similarity': video_sim,
                        'evidence': 'Video fingerprint match'
                    })
            
            # Image similarity
            if target.image_fingerprint and reference.image_fingerprint:
                image_sim = await self._calculate_image_similarity(
                    target.image_fingerprint, reference.image_fingerprint
                )
                similarity_scores['image'] = image_sim
                if image_sim > 0.5:
                    fingerprint_matches.append({
                        'type': 'image',
                        'similarity': image_sim,
                        'evidence': 'Image fingerprint match'
                    })
            
            # Text similarity
            if target.text_fingerprint and reference.text_fingerprint:
                text_sim = await self._calculate_text_similarity(
                    target.text_fingerprint, reference.text_fingerprint
                )
                similarity_scores['text'] = text_sim
                if text_sim > 0.5:
                    fingerprint_matches.append({
                        'type': 'text',
                        'similarity': text_sim,
                        'evidence': 'Text fingerprint match'
                    })
            
            # Vector embedding similarity (CLIP)
            if target.vector_embedding and reference.vector_embedding:
                vector_sim = await self.vector_matcher.calculate_similarity(
                    target.vector_embedding, reference.vector_embedding
                )
                similarity_scores['vector'] = vector_sim
                if vector_sim > 0.5:
                    fingerprint_matches.append({
                        'type': 'vector',
                        'similarity': vector_sim,
                        'evidence': 'Cross-modal vector similarity'
                    })
            
            # Calculate overall similarity score
            if not similarity_scores:
                return None
            
            # Weighted average based on available modalities
            overall_similarity = await self._calculate_weighted_similarity(similarity_scores)
            
            # Determine detection type
            detection_type = self._determine_detection_type(overall_similarity)
            
            # Calculate confidence score
            confidence_score = await self._calculate_confidence_score(
                similarity_scores, fingerprint_matches
            )
            
            # Create detection result
            result = DetectionResult(
                detection_id=detection_id,
                content_type=target.content_type,
                detection_type=detection_type,
                similarity_score=overall_similarity,
                confidence_score=confidence_score,
                original_content_id=reference.content_id,
                detected_content_url=f"platform://{platform}/{target.content_id}",
                platform=platform,
                evidence={
                    'similarity_scores': similarity_scores,
                    'fingerprint_comparison': 'Detailed fingerprint analysis performed'
                },
                metadata={
                    'target_metadata': target.metadata,
                    'reference_metadata': reference.metadata
                },
                fingerprint_matches=fingerprint_matches
            )
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error comparing fingerprints: {str(e)}")
            return None
    
    async def _calculate_audio_similarity(self, target: Dict[str, Any],
                                        reference: Dict[str, Any]) -> float:
        """Calculate audio similarity score"""
        try:
            # Use audio fingerprinting engine
            return await self.audio_fingerprinter.calculate_similarity(target, reference)
        except Exception as e:
            self.logger.error(f"Error calculating audio similarity: {str(e)}")
            return 0.0
    
    async def _calculate_video_similarity(self, target: Dict[str, Any],
                                        reference: Dict[str, Any]) -> float:
        """Calculate video similarity score"""
        try:
            # Use video fingerprinting engine
            return await self.video_fingerprinter.calculate_similarity(target, reference)
        except Exception as e:
            self.logger.error(f"Error calculating video similarity: {str(e)}")
            return 0.0
    
    async def _calculate_image_similarity(self, target: Dict[str, Any],
                                        reference: Dict[str, Any]) -> float:
        """Calculate image similarity score"""
        try:
            # Use image fingerprinting engine
            return await self.image_fingerprinter.calculate_similarity(target, reference)
        except Exception as e:
            self.logger.error(f"Error calculating image similarity: {str(e)}")
            return 0.0
    
    async def _calculate_text_similarity(self, target: Dict[str, Any],
                                       reference: Dict[str, Any]) -> float:
        """Calculate text similarity score"""
        try:
            # Use text fingerprinting engine
            return await self.text_fingerprinter.calculate_similarity(target, reference)
        except Exception as e:
            self.logger.error(f"Error calculating text similarity: {str(e)}")
            return 0.0
    
    async def _calculate_weighted_similarity(self, similarity_scores: Dict[str, float]) -> float:
        """Calculate weighted overall similarity score"""
        try:
            # Weights for different modalities
            weights = {
                'audio': 0.35,
                'video': 0.30,
                'image': 0.20,
                'text': 0.10,
                'vector': 0.05
            }
            
            weighted_sum = 0.0
            total_weight = 0.0
            
            for modality, score in similarity_scores.items():
                weight = weights.get(modality, 0.1)
                weighted_sum += score * weight
                total_weight += weight
            
            return weighted_sum / total_weight if total_weight > 0 else 0.0
            
        except Exception as e:
            self.logger.error(f"Error calculating weighted similarity: {str(e)}")
            return 0.0
    
    def _determine_detection_type(self, similarity_score: float) -> DetectionType:
        """Determine detection type based on similarity score"""
        for detection_type, threshold in self.similarity_thresholds.items():
            if similarity_score >= threshold:
                return detection_type
        
        return DetectionType.FALSE_POSITIVE
    
    async def _calculate_confidence_score(self, similarity_scores: Dict[str, float],
                                        fingerprint_matches: List[Dict[str, Any]]) -> float:
        """Calculate confidence score for detection"""
        try:
            # Base confidence on number of matching modalities
            modality_count = len([s for s in similarity_scores.values() if s > 0.5])
            base_confidence = min(modality_count / 3.0, 1.0)  # Up to 3 modalities
            
            # Boost confidence based on high similarity scores
            high_similarity_boost = sum(1 for s in similarity_scores.values() if s > 0.8) * 0.1
            
            # Boost confidence based on number of fingerprint matches
            match_boost = min(len(fingerprint_matches) * 0.05, 0.2)
            
            confidence = min(base_confidence + high_similarity_boost + match_boost, 1.0)
            
            return confidence
            
        except Exception as e:
            self.logger.error(f"Error calculating confidence score: {str(e)}")
            return 0.5
    
    async def _is_likely_true_positive(self, detection: DetectionResult,
                                     confidence_threshold: float) -> bool:
        """Determine if detection is likely a true positive"""
        try:
            # Multiple criteria for false positive filtering
            criteria_passed = 0
            
            # Confidence score check
            if detection.confidence_score >= confidence_threshold:
                criteria_passed += 1
            
            # Multiple fingerprint matches
            if len(detection.fingerprint_matches) >= 2:
                criteria_passed += 1
            
            # High similarity in primary modality
            if detection.content_type == ContentType.AUDIO and 'audio' in detection.evidence.get('similarity_scores', {}):
                if detection.evidence['similarity_scores']['audio'] > 0.8:
                    criteria_passed += 1
            
            # Metadata consistency check
            if await self._check_metadata_consistency(detection):
                criteria_passed += 1
            
            # Require at least 2 out of 4 criteria
            return criteria_passed >= 2
            
        except Exception as e:
            self.logger.error(f"Error checking true positive likelihood: {str(e)}")
            return True  # Default to keeping detection
    
    async def _check_metadata_consistency(self, detection: DetectionResult) -> bool:
        """Check if metadata is consistent between target and reference"""
        try:
            target_meta = detection.metadata.get('target_metadata', {})
            reference_meta = detection.metadata.get('reference_metadata', {})
            
            # Check common metadata fields
            consistent_fields = 0
            total_fields = 0
            
            common_fields = ['title', 'artist', 'duration', 'genre']
            
            for field in common_fields:
                if field in target_meta and field in reference_meta:
                    total_fields += 1
                    if target_meta[field] == reference_meta[field]:
                        consistent_fields += 1
            
            if total_fields == 0:
                return True  # No metadata to compare
            
            return (consistent_fields / total_fields) >= 0.5
            
        except Exception as e:
            self.logger.error(f"Error checking metadata consistency: {str(e)}")
            return True
    
    def get_detection_statistics(self) -> Dict[str, Any]:
        """Get current detection statistics"""
        try:
            stats = self.detection_stats.copy()
            
            if stats['processing_times']:
                stats['average_processing_time_ms'] = sum(stats['processing_times']) / len(stats['processing_times'])
                stats['max_processing_time_ms'] = max(stats['processing_times'])
                stats['min_processing_time_ms'] = min(stats['processing_times'])
            
            if stats['total_detections'] > 0:
                stats['accuracy'] = (stats['true_positives'] / 
                                   (stats['true_positives'] + stats['false_positives'])) * 100
            
            return stats
            
        except Exception as e:
            self.logger.error(f"Error getting detection statistics: {str(e)}")
            return {}
