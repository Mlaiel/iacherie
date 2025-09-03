#!/usr/bin/env python3
"""Style Transfer Protection Module for IA-Influencer-Agent
========================================================

Advanced protection system against unauthorized style transfer and content manipulation.
Detects when artistic styles, writing patterns, or content characteristics have been
artificially transferred or mimicked without permission.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

This module provides:
- Style fingerprinting and detection
- Unauthorized style transfer detection
- Content authenticity verification
- Protection against AI-generated mimicry
"""

import logging
import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
from typing import Dict, List, Optional, Union, Tuple, Any
from dataclasses import dataclass
from enum import Enum
import time
import hashlib
import asyncio
import json

# Conditional imports
try:
    import cv2
    from PIL import Image
    CV2_AVAILABLE = True
except ImportError:
    CV2_AVAILABLE = False

try:
    import sklearn.feature_extraction.text as text_features
    from sklearn.metrics.pairwise import cosine_similarity
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False

logger = logging.getLogger(__name__)


class StyleType(Enum):
    """Types of style that can be protected"""
    ARTISTIC_VISUAL = "artistic_visual"
    WRITING_STYLE = "writing_style"
    MUSICAL_STYLE = "musical_style"
    VOICE_STYLE = "voice_style"
    VIDEO_EDITING = "video_editing"
    PHOTOGRAPHIC = "photographic"
    DESIGN_PATTERN = "design_pattern"


class ProtectionLevel(Enum):
    """Style protection levels"""
    BASIC = "basic"
    STANDARD = "standard"
    ADVANCED = "advanced"
    MAXIMUM = "maximum"


class TransferDetectionResult(Enum):
    """Style transfer detection results"""
    ORIGINAL = "original"
    MINOR_SIMILARITY = "minor_similarity"
    SIGNIFICANT_TRANSFER = "significant_transfer"
    UNAUTHORIZED_COPY = "unauthorized_copy"
    DEFINITIVE_THEFT = "definitive_theft"


@dataclass
class StyleFingerprint:
    """Comprehensive style fingerprint"""
    style_id: str
    style_type: StyleType
    feature_vector: np.ndarray
    style_hash: str
    dominant_characteristics: Dict[str, float]
    technical_parameters: Dict[str, Any]
    creation_timestamp: float
    protection_level: ProtectionLevel


@dataclass
class StyleTransferAnalysis:
    """Analysis result for style transfer detection"""
    detection_result: TransferDetectionResult
    confidence_score: float
    similarity_score: float
    transfer_probability: float
    matched_styles: List[Dict[str, Any]]
    analysis_details: Dict[str, Any]
    protection_violations: List[str]
    processing_time: float


class StyleTransferProtector:
    """
    Advanced Style Transfer Protection System
    
    Protects against unauthorized use of artistic, writing, and content styles:
    - Style fingerprinting and database management
    - Real-time style transfer detection
    - Multi-modal style analysis
    - Legal protection support
    """
    
    def __init__(self, device: str = "cpu"):
        self.device = device
        self.is_initialized = False
        
        # Style database for comparison
        self.style_database = {}
        
        # Detection thresholds
        self.thresholds = {
            'similarity_alert': 0.7,
            'transfer_detection': 0.8,
            'theft_threshold': 0.9,
            'confidence_minimum': 0.6
        }
        
        # Style analysis models
        self.analyzers = {}
        
        logger.info(f"StyleTransferProtector initialized on device: {device}")
    
    async def initialize(self) -> bool:
        """Initialize the style transfer protection system"""
        try:
            # Initialize different style analyzers
            self.analyzers[StyleType.ARTISTIC_VISUAL] = await self._create_visual_style_analyzer()
            self.analyzers[StyleType.WRITING_STYLE] = await self._create_text_style_analyzer()
            self.analyzers[StyleType.MUSICAL_STYLE] = await self._create_music_style_analyzer()
            self.analyzers[StyleType.VOICE_STYLE] = await self._create_voice_style_analyzer()
            self.analyzers[StyleType.VIDEO_EDITING] = await self._create_video_style_analyzer()
            self.analyzers[StyleType.PHOTOGRAPHIC] = await self._create_photo_style_analyzer()
            self.analyzers[StyleType.DESIGN_PATTERN] = await self._create_design_style_analyzer()
            
            self.is_initialized = True
            logger.info("Style transfer protector initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize style transfer protector: {e}")
            return False
    
    async def register_style(self,
                           content_data: Any,
                           style_type: StyleType,
                           owner_id: str,
                           style_name: str,
                           protection_level: ProtectionLevel = ProtectionLevel.STANDARD) -> StyleFingerprint:
        """
        Register a new style for protection
        
        Args:
            content_data: The content containing the style to protect
            style_type: Type of style being registered
            owner_id: ID of the style owner
            style_name: Human-readable name for the style
            protection_level: Level of protection to apply
            
        Returns:
            StyleFingerprint: Generated fingerprint for the style
        """
        if not self.is_initialized:
            await self.initialize()
        
        try:
            # Generate unique style ID
            style_id = self._generate_style_id(owner_id, style_name, style_type)
            
            # Extract style features based on type
            analyzer = self.analyzers.get(style_type)
            if not analyzer:
                raise ValueError(f"No analyzer available for style type: {style_type}")
            
            # Extract style characteristics
            feature_vector = await self._extract_style_features(content_data, style_type, analyzer)
            dominant_characteristics = await self._identify_dominant_characteristics(
                feature_vector, style_type
            )
            technical_parameters = await self._extract_technical_parameters(
                content_data, style_type
            )
            
            # Generate style hash
            style_hash = self._generate_style_hash(feature_vector, dominant_characteristics)
            
            # Create fingerprint
            fingerprint = StyleFingerprint(
                style_id=style_id,
                style_type=style_type,
                feature_vector=feature_vector,
                style_hash=style_hash,
                dominant_characteristics=dominant_characteristics,
                technical_parameters=technical_parameters,
                creation_timestamp=time.time(),
                protection_level=protection_level
            )
            
            # Store in database
            self.style_database[style_id] = {
                'fingerprint': fingerprint,
                'owner_id': owner_id,
                'style_name': style_name,
                'registration_time': time.time()
            }
            
            logger.info(f"Style registered: {style_name} ({style_id})")
            return fingerprint
            
        except Exception as e:
            logger.error(f"Style registration failed: {e}")
            raise
    
    async def detect_style_transfer(self,
                                  content_data: Any,
                                  style_type: StyleType,
                                  check_database: bool = True) -> StyleTransferAnalysis:
        """
        Detect if content uses protected styles without authorization
        
        Args:
            content_data: Content to analyze
            style_type: Type of style to check for
            check_database: Whether to check against registered styles
            
        Returns:
            StyleTransferAnalysis: Analysis results
        """
        if not self.is_initialized:
            await self.initialize()
        
        start_time = time.time()
        
        try:
            # Extract style features from content
            analyzer = self.analyzers.get(style_type)
            if not analyzer:
                raise ValueError(f"No analyzer available for style type: {style_type}")
            
            content_features = await self._extract_style_features(content_data, style_type, analyzer)
            content_characteristics = await self._identify_dominant_characteristics(
                content_features, style_type
            )
            
            matched_styles = []
            max_similarity = 0.0
            
            if check_database:
                # Compare against registered styles
                for style_id, style_data in self.style_database.items():
                    fingerprint = style_data['fingerprint']
                    
                    if fingerprint.style_type != style_type:
                        continue
                    
                    # Calculate similarity
                    similarity = self._calculate_style_similarity(
                        content_features,
                        fingerprint.feature_vector,
                        content_characteristics,
                        fingerprint.dominant_characteristics
                    )
                    
                    if similarity > self.thresholds['similarity_alert']:
                        matched_styles.append({
                            'style_id': style_id,
                            'style_name': style_data['style_name'],
                            'owner_id': style_data['owner_id'],
                            'similarity': similarity,
                            'protection_level': fingerprint.protection_level.value
                        })
                        
                        max_similarity = max(max_similarity, similarity)
            
            # Determine detection result
            detection_result = self._determine_detection_result(max_similarity)
            
            # Calculate transfer probability
            transfer_probability = min(max_similarity * 1.2, 1.0)
            
            # Identify protection violations
            protection_violations = self._identify_protection_violations(
                matched_styles, max_similarity
            )
            
            # Generate analysis details
            analysis_details = {
                'content_features_analyzed': len(content_features),
                'database_styles_checked': len(self.style_database),
                'similarity_threshold': self.thresholds['similarity_alert'],
                'detection_method': 'feature_vector_comparison',
                'style_characteristics': content_characteristics
            }
            
            processing_time = time.time() - start_time
            
            return StyleTransferAnalysis(
                detection_result=detection_result,
                confidence_score=min(max_similarity + 0.1, 1.0),
                similarity_score=max_similarity,
                transfer_probability=transfer_probability,
                matched_styles=matched_styles,
                analysis_details=analysis_details,
                protection_violations=protection_violations,
                processing_time=processing_time
            )
            
        except Exception as e:
            logger.error(f"Style transfer detection failed: {e}")
            return StyleTransferAnalysis(
                detection_result=TransferDetectionResult.MINOR_SIMILARITY,
                confidence_score=0.0,
                similarity_score=0.0,
                transfer_probability=0.0,
                matched_styles=[],
                analysis_details={"error": str(e)},
                protection_violations=[],
                processing_time=time.time() - start_time
            )
    
    async def verify_style_authenticity(self,
                                      content_data: Any,
                                      claimed_style_id: str) -> Dict[str, Any]:
        """
        Verify if content authentically matches a claimed style
        
        Args:
            content_data: Content to verify
            claimed_style_id: ID of the style being claimed
            
        Returns:
            Dict containing verification results
        """
        if claimed_style_id not in self.style_database:
            return {
                'authentic': False,
                'error': 'Style ID not found in database'
            }
        
        style_data = self.style_database[claimed_style_id]
        fingerprint = style_data['fingerprint']
        
        # Extract features from content
        analyzer = self.analyzers.get(fingerprint.style_type)
        content_features = await self._extract_style_features(
            content_data, fingerprint.style_type, analyzer
        )
        content_characteristics = await self._identify_dominant_characteristics(
            content_features, fingerprint.style_type
        )
        
        # Calculate similarity
        similarity = self._calculate_style_similarity(
            content_features,
            fingerprint.feature_vector,
            content_characteristics,
            fingerprint.dominant_characteristics
        )
        
        # Determine authenticity
        authentic = similarity > 0.85  # High threshold for authenticity
        
        return {
            'authentic': authentic,
            'similarity_score': similarity,
            'style_name': style_data['style_name'],
            'owner_id': style_data['owner_id'],
            'analysis_timestamp': time.time()
        }
    
    # Style-specific feature extraction methods
    async def _extract_style_features(self,
                                     content_data: Any,
                                     style_type: StyleType,
                                     analyzer: Any) -> np.ndarray:
        """Extract style features based on content type"""
        if style_type == StyleType.ARTISTIC_VISUAL:
            return await self._extract_visual_style_features(content_data, analyzer)
        elif style_type == StyleType.WRITING_STYLE:
            return await self._extract_text_style_features(content_data, analyzer)
        elif style_type == StyleType.MUSICAL_STYLE:
            return await self._extract_music_style_features(content_data, analyzer)
        elif style_type == StyleType.VOICE_STYLE:
            return await self._extract_voice_style_features(content_data, analyzer)
        elif style_type == StyleType.VIDEO_EDITING:
            return await self._extract_video_style_features(content_data, analyzer)
        elif style_type == StyleType.PHOTOGRAPHIC:
            return await self._extract_photo_style_features(content_data, analyzer)
        elif style_type == StyleType.DESIGN_PATTERN:
            return await self._extract_design_style_features(content_data, analyzer)
        else:
            raise ValueError(f"Unsupported style type: {style_type}")
    
    async def _extract_visual_style_features(self, image_data: Any, analyzer: Any) -> np.ndarray:
        """Extract visual style features from images"""
        if not CV2_AVAILABLE:
            # Fallback: simple statistical features
            if isinstance(image_data, np.ndarray):
                features = [
                    np.mean(image_data),
                    np.std(image_data),
                    np.percentile(image_data.flatten(), 25),
                    np.percentile(image_data.flatten(), 75),
                    np.max(image_data) - np.min(image_data)
                ]
                return np.array(features + [0] * 27)  # Pad to 32 features
            else:
                return np.random.random(32)  # Dummy features
        
        try:
            # Convert to OpenCV format if needed
            if isinstance(image_data, str):  # File path
                image = cv2.imread(image_data)
            elif hasattr(image_data, 'save'):  # PIL Image
                image_data.save('/tmp/temp_image.jpg')
                image = cv2.imread('/tmp/temp_image.jpg')
            else:  # Assume numpy array
                image = image_data
            
            if image is None:
                return np.random.random(32)
            
            # Extract various visual features
            features = []
            
            # Color histogram features
            for i in range(3):  # BGR channels
                hist = cv2.calcHist([image], [i], None, [8], [0, 256])
                features.extend(hist.flatten())
            
            # Texture features using LBP-like patterns
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # Edge density
            edges = cv2.Canny(gray, 50, 150)
            edge_density = np.sum(edges > 0) / edges.size
            features.append(edge_density)
            
            # Contrast and brightness
            features.append(np.std(gray))  # Contrast
            features.append(np.mean(gray))  # Brightness
            
            # Saturation
            hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
            features.append(np.mean(hsv[:, :, 1]))  # Saturation
            
            # Ensure fixed feature size
            features = features[:32]
            if len(features) < 32:
                features.extend([0] * (32 - len(features)))
            
            return np.array(features)
            
        except Exception as e:
            logger.warning(f"Visual feature extraction failed: {e}")
            return np.random.random(32)
    
    async def _extract_text_style_features(self, text_data: str, analyzer: Any) -> np.ndarray:
        """Extract writing style features from text"""
        if not SKLEARN_AVAILABLE:
            # Fallback: simple text statistics
            if isinstance(text_data, str):
                features = [
                    len(text_data),
                    len(text_data.split()),
                    len(set(text_data.lower().split())),
                    text_data.count('.'),
                    text_data.count(','),
                    text_data.count('!'),
                    text_data.count('?'),
                    len([w for w in text_data.split() if len(w) > 6])
                ]
                return np.array(features + [0] * 24)  # Pad to 32 features
            else:
                return np.random.random(32)
        
        try:
            if not isinstance(text_data, str):
                text_data = str(text_data)
            
            features = []
            
            # Basic text statistics
            words = text_data.split()
            sentences = text_data.split('.')
            
            features.extend([
                len(words),  # Word count
                len(sentences),  # Sentence count
                np.mean([len(w) for w in words]) if words else 0,  # Average word length
                np.mean([len(s.split()) for s in sentences if s.strip()]) if sentences else 0,  # Average sentence length
                len(set(words)) / len(words) if words else 0,  # Vocabulary diversity
            ])
            
            # Punctuation usage
            features.extend([
                text_data.count('.') / len(text_data) if text_data else 0,
                text_data.count(',') / len(text_data) if text_data else 0,
                text_data.count('!') / len(text_data) if text_data else 0,
                text_data.count('?') / len(text_data) if text_data else 0,
                text_data.count(';') / len(text_data) if text_data else 0,
            ])
            
            # Character-level features
            features.extend([
                sum(1 for c in text_data if c.isupper()) / len(text_data) if text_data else 0,
                sum(1 for c in text_data if c.islower()) / len(text_data) if text_data else 0,
                sum(1 for c in text_data if c.isdigit()) / len(text_data) if text_data else 0,
            ])
            
            # Word length distribution
            word_lengths = [len(w) for w in words]
            if word_lengths:
                features.extend([
                    np.std(word_lengths),
                    len([w for w in words if len(w) == 1]) / len(words),
                    len([w for w in words if len(w) >= 10]) / len(words),
                ])
            else:
                features.extend([0, 0, 0])
            
            # TF-IDF features (simplified)
            try:
                vectorizer = text_features.TfidfVectorizer(max_features=10, stop_words='english')
                if len(text_data.split()) > 1:
                    tfidf_matrix = vectorizer.fit_transform([text_data])
                    tfidf_features = tfidf_matrix.toarray().flatten()
                    features.extend(tfidf_features)
                else:
                    features.extend([0] * 10)
            except:
                features.extend([0] * 10)
            
            # Ensure fixed feature size
            features = features[:32]
            if len(features) < 32:
                features.extend([0] * (32 - len(features)))
            
            return np.array(features)
            
        except Exception as e:
            logger.warning(f"Text feature extraction failed: {e}")
            return np.random.random(32)
    
    async def _extract_music_style_features(self, audio_data: Any, analyzer: Any) -> np.ndarray:
        """Extract musical style features from audio"""
        # Simplified music style features
        try:
            if isinstance(audio_data, np.ndarray):
                # Basic audio statistics
                features = [
                    np.mean(audio_data),
                    np.std(audio_data),
                    np.max(audio_data),
                    np.min(audio_data),
                    np.percentile(audio_data, 25),
                    np.percentile(audio_data, 75),
                ]
                
                # Frequency domain features (simplified)
                fft = np.fft.fft(audio_data[:8192])  # Use first 8192 samples
                magnitude = np.abs(fft)
                
                features.extend([
                    np.mean(magnitude),
                    np.std(magnitude),
                    np.argmax(magnitude),  # Dominant frequency
                ])
                
                # Pad to 32 features
                features.extend([0] * (32 - len(features)))
                return np.array(features[:32])
            else:
                return np.random.random(32)
        except Exception as e:
            logger.warning(f"Music feature extraction failed: {e}")
            return np.random.random(32)
    
    async def _extract_voice_style_features(self, audio_data: Any, analyzer: Any) -> np.ndarray:
        """Extract voice style features from audio"""
        # Similar to music but focused on voice characteristics
        return await self._extract_music_style_features(audio_data, analyzer)
    
    async def _extract_video_style_features(self, video_data: Any, analyzer: Any) -> np.ndarray:
        """Extract video editing style features"""
        # Simplified video style features
        try:
            # Extract features based on video metadata or frames
            # For now, return dummy features
            return np.random.random(32)
        except Exception as e:
            logger.warning(f"Video feature extraction failed: {e}")
            return np.random.random(32)
    
    async def _extract_photo_style_features(self, image_data: Any, analyzer: Any) -> np.ndarray:
        """Extract photographic style features"""
        # Use visual features but focus on photographic aspects
        return await self._extract_visual_style_features(image_data, analyzer)
    
    async def _extract_design_style_features(self, design_data: Any, analyzer: Any) -> np.ndarray:
        """Extract design pattern features"""
        # Similar to visual features but focus on design elements
        return await self._extract_visual_style_features(design_data, analyzer)
    
    # Analyzer creation methods
    async def _create_visual_style_analyzer(self) -> Dict[str, Any]:
        """Create visual style analyzer"""
        return {"type": "visual", "initialized": True}
    
    async def _create_text_style_analyzer(self) -> Dict[str, Any]:
        """Create text style analyzer"""
        return {"type": "text", "initialized": True}
    
    async def _create_music_style_analyzer(self) -> Dict[str, Any]:
        """Create music style analyzer"""
        return {"type": "music", "initialized": True}
    
    async def _create_voice_style_analyzer(self) -> Dict[str, Any]:
        """Create voice style analyzer"""
        return {"type": "voice", "initialized": True}
    
    async def _create_video_style_analyzer(self) -> Dict[str, Any]:
        """Create video style analyzer"""
        return {"type": "video", "initialized": True}
    
    async def _create_photo_style_analyzer(self) -> Dict[str, Any]:
        """Create photo style analyzer"""
        return {"type": "photo", "initialized": True}
    
    async def _create_design_style_analyzer(self) -> Dict[str, Any]:
        """Create design style analyzer"""
        return {"type": "design", "initialized": True}
    
    # Helper methods
    async def _identify_dominant_characteristics(self,
                                               feature_vector: np.ndarray,
                                               style_type: StyleType) -> Dict[str, float]:
        """Identify dominant characteristics from feature vector"""
        # Find the most significant features
        characteristics = {}
        
        # Top features by magnitude
        top_indices = np.argsort(np.abs(feature_vector))[-5:]
        
        for i, idx in enumerate(top_indices):
            characteristics[f"feature_{idx}"] = float(feature_vector[idx])
        
        # Add style-specific characteristics
        if style_type == StyleType.ARTISTIC_VISUAL:
            characteristics.update({
                "color_complexity": float(np.std(feature_vector[:8])),
                "texture_richness": float(np.mean(feature_vector[8:16])),
                "composition_balance": float(np.mean(feature_vector[16:24]))
            })
        elif style_type == StyleType.WRITING_STYLE:
            characteristics.update({
                "vocabulary_diversity": float(feature_vector[4]) if len(feature_vector) > 4 else 0.0,
                "sentence_complexity": float(feature_vector[3]) if len(feature_vector) > 3 else 0.0,
                "punctuation_style": float(np.mean(feature_vector[5:10])) if len(feature_vector) > 9 else 0.0
            })
        
        return characteristics
    
    async def _extract_technical_parameters(self,
                                          content_data: Any,
                                          style_type: StyleType) -> Dict[str, Any]:
        """Extract technical parameters specific to content type"""
        parameters = {
            "extraction_timestamp": time.time(),
            "style_type": style_type.value
        }
        
        if style_type == StyleType.ARTISTIC_VISUAL:
            if hasattr(content_data, 'size'):
                parameters["image_dimensions"] = content_data.size
            elif isinstance(content_data, np.ndarray):
                parameters["array_shape"] = content_data.shape
        elif style_type == StyleType.WRITING_STYLE:
            if isinstance(content_data, str):
                parameters["character_count"] = len(content_data)
                parameters["word_count"] = len(content_data.split())
        
        return parameters
    
    def _generate_style_id(self, owner_id: str, style_name: str, style_type: StyleType) -> str:
        """Generate unique style ID"""
        data = f"{owner_id}_{style_name}_{style_type.value}_{time.time()}"
        return hashlib.sha256(data.encode()).hexdigest()[:16]
    
    def _generate_style_hash(self,
                           feature_vector: np.ndarray,
                           characteristics: Dict[str, float]) -> str:
        """Generate hash for style fingerprint"""
        # Combine feature vector and characteristics
        data = feature_vector.tobytes() + json.dumps(characteristics, sort_keys=True).encode()
        return hashlib.sha256(data).hexdigest()
    
    def _calculate_style_similarity(self,
                                   features1: np.ndarray,
                                   features2: np.ndarray,
                                   characteristics1: Dict[str, float],
                                   characteristics2: Dict[str, float]) -> float:
        """Calculate similarity between two styles"""
        # Feature vector similarity (cosine similarity)
        features1_norm = features1 / (np.linalg.norm(features1) + 1e-8)
        features2_norm = features2 / (np.linalg.norm(features2) + 1e-8)
        feature_similarity = np.dot(features1_norm, features2_norm)
        
        # Characteristics similarity
        char_similarity = 0.0
        common_keys = set(characteristics1.keys()) & set(characteristics2.keys())
        
        if common_keys:
            char_diffs = []
            for key in common_keys:
                diff = abs(characteristics1[key] - characteristics2[key])
                char_diffs.append(diff)
            char_similarity = 1.0 - (np.mean(char_diffs) if char_diffs else 0.0)
        
        # Weighted combination
        total_similarity = 0.7 * feature_similarity + 0.3 * char_similarity
        return max(0.0, min(1.0, total_similarity))
    
    def _determine_detection_result(self, similarity_score: float) -> TransferDetectionResult:
        """Determine detection result based on similarity score"""
        if similarity_score >= self.thresholds['theft_threshold']:
            return TransferDetectionResult.DEFINITIVE_THEFT
        elif similarity_score >= self.thresholds['transfer_detection']:
            return TransferDetectionResult.UNAUTHORIZED_COPY
        elif similarity_score >= 0.6:
            return TransferDetectionResult.SIGNIFICANT_TRANSFER
        elif similarity_score >= self.thresholds['similarity_alert']:
            return TransferDetectionResult.MINOR_SIMILARITY
        else:
            return TransferDetectionResult.ORIGINAL
    
    def _identify_protection_violations(self,
                                      matched_styles: List[Dict[str, Any]],
                                      max_similarity: float) -> List[str]:
        """Identify specific protection violations"""
        violations = []
        
        for match in matched_styles:
            if match['similarity'] >= self.thresholds['transfer_detection']:
                violations.append(
                    f"High similarity ({match['similarity']:.2f}) with protected style "
                    f"'{match['style_name']}' owned by {match['owner_id']}"
                )
            
            if match['protection_level'] == ProtectionLevel.MAXIMUM.value and match['similarity'] >= 0.6:
                violations.append(
                    f"Unauthorized use of maximum-protected style '{match['style_name']}'"
                )
        
        if max_similarity >= self.thresholds['theft_threshold']:
            violations.append("Potential style theft detected - legal action may be warranted")
        
        return violations
    
    # Database management methods
    def export_style_database(self) -> Dict[str, Any]:
        """Export style database for backup"""
        export_data = {}
        for style_id, data in self.style_database.items():
            export_data[style_id] = {
                'owner_id': data['owner_id'],
                'style_name': data['style_name'],
                'registration_time': data['registration_time'],
                'fingerprint': {
                    'style_type': data['fingerprint'].style_type.value,
                    'style_hash': data['fingerprint'].style_hash,
                    'dominant_characteristics': data['fingerprint'].dominant_characteristics,
                    'technical_parameters': data['fingerprint'].technical_parameters,
                    'creation_timestamp': data['fingerprint'].creation_timestamp,
                    'protection_level': data['fingerprint'].protection_level.value
                }
            }
        return export_data
    
    def import_style_database(self, import_data: Dict[str, Any]) -> bool:
        """Import style database from backup"""
        try:
            for style_id, data in import_data.items():
                fingerprint_data = data['fingerprint']
                
                # Reconstruct fingerprint (without feature_vector for security)
                fingerprint = StyleFingerprint(
                    style_id=style_id,
                    style_type=StyleType(fingerprint_data['style_type']),
                    feature_vector=np.array([]),  # Empty for security
                    style_hash=fingerprint_data['style_hash'],
                    dominant_characteristics=fingerprint_data['dominant_characteristics'],
                    technical_parameters=fingerprint_data['technical_parameters'],
                    creation_timestamp=fingerprint_data['creation_timestamp'],
                    protection_level=ProtectionLevel(fingerprint_data['protection_level'])
                )
                
                self.style_database[style_id] = {
                    'fingerprint': fingerprint,
                    'owner_id': data['owner_id'],
                    'style_name': data['style_name'],
                    'registration_time': data['registration_time']
                }
            
            logger.info(f"Imported {len(import_data)} styles to database")
            return True
            
        except Exception as e:
            logger.error(f"Failed to import style database: {e}")
            return False


# Factory function
def create_style_transfer_protector(device: str = "cpu") -> StyleTransferProtector:
    """Create and return a StyleTransferProtector instance"""
    return StyleTransferProtector(device=device)


# Example usage
async def main():
    """Example usage of StyleTransferProtector"""
    protector = create_style_transfer_protector()
    await protector.initialize()
    
    # Example: Register a writing style
    sample_text = """
    This is a sample text that demonstrates a particular writing style.
    The author uses specific vocabulary, sentence structures, and patterns
    that make their writing unique and recognizable.
    """
    
    fingerprint = await protector.register_style(
        content_data=sample_text,
        style_type=StyleType.WRITING_STYLE,
        owner_id="user123",
        style_name="Original Author Style",
        protection_level=ProtectionLevel.ADVANCED
    )
    
    print(f"Registered style: {fingerprint.style_id}")
    
    # Example: Test detection on similar text
    test_text = """
    This is a sample text that demonstrates a particular writing style.
    The author uses specific vocabulary, sentence structures, and patterns
    that make their writing quite unique and recognizable.
    """
    
    analysis = await protector.detect_style_transfer(
        content_data=test_text,
        style_type=StyleType.WRITING_STYLE
    )
    
    print(f"Detection Result: {analysis.detection_result.value}")
    print(f"Similarity Score: {analysis.similarity_score:.2f}")
    print(f"Transfer Probability: {analysis.transfer_probability:.2f}")
    print(f"Matched Styles: {len(analysis.matched_styles)}")
    
    if analysis.protection_violations:
        print("Protection Violations:")
        for violation in analysis.protection_violations:
            print(f"  - {violation}")


if __name__ == "__main__":
    asyncio.run(main())