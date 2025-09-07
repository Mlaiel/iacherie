"""Multimodal Intelligence - Cross-Modal Content Intelligence System

Advanced AI system for understanding and processing content across multiple modalities
(text, audio, video, images) with intelligent cross-modal analysis and insights.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel - All Rights Reserved

LEGAL WARNING: This code is the exclusive property of Fahed Mlaiel.
Unauthorized use, reproduction, or distribution is strictly prohibited.
"""

import asyncio
import json
import logging
import numpy as np
from datetime import datetime, timezone
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Any, Tuple, Union
import uuid
from pathlib import Path

# AI/ML dependencies with graceful fallbacks
try:
    import torch
    import torch.nn as nn
    HAS_TORCH = True
except ImportError:
    HAS_TORCH = False
    logging.warning("PyTorch not available - using simplified AI processing")

try:
    from transformers import pipeline, AutoModel, AutoTokenizer
    HAS_TRANSFORMERS = True
except ImportError:
    HAS_TRANSFORMERS = False
    logging.warning("Transformers not available - using basic text processing")

try:
    import clip
    HAS_CLIP = True
except ImportError:
    HAS_CLIP = False
    logging.warning("CLIP not available - using basic image-text alignment")

try:
    import librosa
    HAS_LIBROSA = True
except ImportError:
    HAS_LIBROSA = False
    logging.warning("Librosa not available - audio analysis limited")

try:
    import cv2
    HAS_OPENCV = True
except ImportError:
    HAS_OPENCV = False
    logging.warning("OpenCV not available - video analysis limited")

try:
    from PIL import Image
    HAS_PIL = True
except ImportError:
    HAS_PIL = False
    logging.warning("PIL not available - image processing limited")

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ModalityType(Enum):
    """Content modality types"""
    TEXT = "text"
    AUDIO = "audio"
    VIDEO = "video"
    IMAGE = "image"
    DOCUMENT = "document"


class AnalysisType(Enum):
    """Types of cross-modal analysis"""
    SEMANTIC_ALIGNMENT = "semantic_alignment"
    CONTENT_COHERENCE = "content_coherence"
    EMOTION_ANALYSIS = "emotion_analysis"
    STYLE_TRANSFER = "style_transfer"
    CONTENT_MATCHING = "content_matching"
    ACCESSIBILITY_ANALYSIS = "accessibility_analysis"
    QUALITY_ASSESSMENT = "quality_assessment"
    ENGAGEMENT_PREDICTION = "engagement_prediction"


class IntelligenceLevel(Enum):
    """Intelligence processing levels"""
    BASIC = "basic"
    ADVANCED = "advanced"
    EXPERT = "expert"
    CREATIVE = "creative"


@dataclass
class ModalityFeatures:
    """Features extracted from a specific modality"""
    modality: ModalityType
    features: Dict[str, Any]
    embeddings: Optional[np.ndarray] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    confidence: float = 0.0
    extraction_time: float = 0.0
    model_used: Optional[str] = None


@dataclass
class CrossModalAlignment:
    """Cross-modal alignment analysis"""
    source_modality: ModalityType
    target_modality: ModalityType
    alignment_score: float
    semantic_similarity: float
    emotional_coherence: float
    style_consistency: float
    
    # Detailed analysis
    matching_concepts: List[str] = field(default_factory=list)
    conflicting_elements: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    
    # Quality metrics
    clarity_score: float = 0.0
    engagement_score: float = 0.0
    accessibility_score: float = 0.0


@dataclass
class IntelligenceInsight:
    """AI-generated insight about content"""
    id: str
    type: str
    title: str
    description: str
    confidence: float
    
    # Context
    affected_modalities: List[ModalityType]
    related_concepts: List[str] = field(default_factory=list)
    
    # Actionable recommendations
    recommendations: List[Dict[str, Any]] = field(default_factory=list)
    
    # Supporting evidence
    evidence: Dict[str, Any] = field(default_factory=dict)
    
    # Metadata
    generated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    model_version: str = "1.0"


@dataclass
class MultimodalContent:
    """Container for multimodal content analysis"""
    id: str
    content_id: str
    title: str
    
    # Modality data
    modalities: Dict[ModalityType, ModalityFeatures] = field(default_factory=dict)
    
    # Cross-modal analysis
    alignments: List[CrossModalAlignment] = field(default_factory=list)
    
    # AI insights
    insights: List[IntelligenceInsight] = field(default_factory=list)
    
    # Overall assessment
    coherence_score: float = 0.0
    quality_score: float = 0.0
    engagement_prediction: float = 0.0
    accessibility_score: float = 0.0
    
    # Processing metadata
    processed_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    processing_time: float = 0.0
    intelligence_level: IntelligenceLevel = IntelligenceLevel.BASIC


class MultimodalIntelligence:
    """Advanced multimodal intelligence system"""
    
    def __init__(self, intelligence_level: IntelligenceLevel = IntelligenceLevel.ADVANCED):
        """Initialize multimodal intelligence system
        
        Args:
            intelligence_level: Level of intelligence processing
        """
        self.intelligence_level = intelligence_level
        self.models = {}
        self.feature_extractors = {}
        self.analysis_cache = {}
        
        # Initialize models based on availability
        self._initialize_models()
        
        logger.info(f"MultimodalIntelligence initialized with {intelligence_level.value} level")
    
    def _initialize_models(self):
        """Initialize AI models based on available dependencies"""
        try:
            # CLIP model for image-text understanding
            if HAS_CLIP:
                import clip
                self.models['clip_model'], self.models['clip_preprocess'] = clip.load("ViT-B/32")
                logger.info("CLIP model loaded successfully")
            
            # Text analysis models
            if HAS_TRANSFORMERS:
                self.models['text_classifier'] = pipeline("text-classification", 
                    model="cardiffnlp/twitter-roberta-base-emotion")
                self.models['text_embedder'] = pipeline("feature-extraction", 
                    model="sentence-transformers/all-MiniLM-L6-v2")
                logger.info("Text analysis models loaded")
            
            # Audio analysis setup
            if HAS_LIBROSA:
                self.feature_extractors['audio'] = self._create_audio_extractor()
                logger.info("Audio feature extractor ready")
            
            # Video analysis setup
            if HAS_OPENCV:
                self.feature_extractors['video'] = self._create_video_extractor()
                logger.info("Video feature extractor ready")
                
        except Exception as e:
            logger.warning(f"Error initializing models: {e}")
    
    async def analyze_multimodal_content(self, content_data: Dict[str, Any]) -> MultimodalContent:
        """Analyze multimodal content for intelligence insights
        
        Args:
            content_data: Dictionary containing content files and metadata
            
        Returns:
            Multimodal analysis results
        """
        try:
            start_time = datetime.now(timezone.utc)
            content_id = content_data.get("id", str(uuid.uuid4()))
            
            analysis = MultimodalContent(
                id=str(uuid.uuid4()),
                content_id=content_id,
                title=content_data.get("title", "Untitled Content"),
                intelligence_level=self.intelligence_level
            )
            
            # Extract features from each modality
            for modality_type, file_path in content_data.get("files", {}).items():
                try:
                    modality = ModalityType(modality_type)
                    features = await self._extract_modality_features(modality, file_path)
                    if features:
                        analysis.modalities[modality] = features
                except ValueError:
                    logger.warning(f"Unknown modality type: {modality_type}")
                except Exception as e:
                    logger.error(f"Error extracting features for {modality_type}: {e}")
            
            # Perform cross-modal analysis
            if len(analysis.modalities) > 1:
                analysis.alignments = await self._analyze_cross_modal_alignment(analysis.modalities)
            
            # Generate AI insights
            analysis.insights = await self._generate_intelligence_insights(analysis)
            
            # Calculate overall scores
            await self._calculate_overall_scores(analysis)
            
            # Record processing time
            end_time = datetime.now(timezone.utc)
            analysis.processing_time = (end_time - start_time).total_seconds()
            
            logger.info(f"Completed multimodal analysis for {content_id}")
            return analysis
            
        except Exception as e:
            logger.error(f"Error in multimodal analysis: {e}")
            raise
    
    async def _extract_modality_features(self, modality: ModalityType, file_path: str) -> Optional[ModalityFeatures]:
        """Extract features from specific modality
        
        Args:
            modality: Type of modality
            file_path: Path to content file
            
        Returns:
            Extracted features or None
        """
        try:
            start_time = datetime.now()
            
            if modality == ModalityType.TEXT:
                features = await self._extract_text_features(file_path)
            elif modality == ModalityType.IMAGE:
                features = await self._extract_image_features(file_path)
            elif modality == ModalityType.AUDIO:
                features = await self._extract_audio_features(file_path)
            elif modality == ModalityType.VIDEO:
                features = await self._extract_video_features(file_path)
            else:
                logger.warning(f"Unsupported modality: {modality}")
                return None
            
            # Calculate extraction time
            extraction_time = (datetime.now() - start_time).total_seconds()
            features.extraction_time = extraction_time
            
            return features
            
        except Exception as e:
            logger.error(f"Error extracting {modality.value} features: {e}")
            return None
    
    async def _extract_text_features(self, file_path: str) -> ModalityFeatures:
        """Extract text features and embeddings"""
        try:
            # Read text content
            text_content = Path(file_path).read_text(encoding='utf-8')
            
            features = {
                "content": text_content,
                "length": len(text_content),
                "word_count": len(text_content.split()),
                "language": "auto-detected",  # Simplified
                "readability_score": self._calculate_readability(text_content)
            }
            
            embeddings = None
            model_used = "basic"
            confidence = 0.8
            
            # Advanced text analysis if models available
            if HAS_TRANSFORMERS and self.models.get('text_classifier'):
                try:
                    # Emotion analysis
                    emotion_result = self.models['text_classifier'](text_content[:512])  # Limit length
                    features["emotions"] = emotion_result
                    
                    # Text embeddings
                    embedding_result = self.models['text_embedder'](text_content[:512])
                    if embedding_result:
                        embeddings = np.array(embedding_result[0])
                        
                    confidence = 0.95
                    model_used = "transformers"
                    
                except Exception as e:
                    logger.warning(f"Advanced text analysis failed: {e}")
            
            # Additional text analysis
            features.update({
                "sentiment_score": self._analyze_sentiment(text_content),
                "key_concepts": self._extract_key_concepts(text_content),
                "readability_level": self._get_readability_level(features["readability_score"])
            })
            
            return ModalityFeatures(
                modality=ModalityType.TEXT,
                features=features,
                embeddings=embeddings,
                confidence=confidence,
                model_used=model_used
            )
            
        except Exception as e:
            logger.error(f"Error in text feature extraction: {e}")
            raise
    
    async def _extract_image_features(self, file_path: str) -> ModalityFeatures:
        """Extract image features and embeddings"""
        try:
            features = {
                "file_path": file_path,
                "format": Path(file_path).suffix.lower()
            }
            
            embeddings = None
            model_used = "basic"
            confidence = 0.7
            
            if HAS_PIL:
                # Basic image analysis
                with Image.open(file_path) as img:
                    features.update({
                        "dimensions": img.size,
                        "mode": img.mode,
                        "has_transparency": img.mode in ('RGBA', 'LA') or 'transparency' in img.info
                    })
                    
                    # Basic color analysis
                    colors = img.getcolors(maxcolors=256)
                    if colors:
                        features["dominant_colors"] = len(colors)
                        features["color_complexity"] = min(len(colors) / 256, 1.0)
            
            # Advanced image analysis with CLIP
            if HAS_CLIP and self.models.get('clip_model'):
                try:
                    with Image.open(file_path) as img:
                        image_input = self.models['clip_preprocess'](img).unsqueeze(0)
                        
                        with torch.no_grad():
                            image_features = self.models['clip_model'].encode_image(image_input)
                            embeddings = image_features.numpy()
                        
                        confidence = 0.95
                        model_used = "clip"
                        
                        # Analyze image content with predefined concepts
                        concepts = ["person", "animal", "nature", "building", "vehicle", "food", "technology"]
                        text_inputs = torch.cat([clip.tokenize(f"a photo of {concept}") for concept in concepts])
                        
                        with torch.no_grad():
                            text_features = self.models['clip_model'].encode_text(text_inputs)
                            similarities = torch.cosine_similarity(image_features, text_features)
                            
                        features["detected_concepts"] = [
                            {"concept": concepts[i], "confidence": float(similarities[i])}
                            for i in range(len(concepts))
                            if similarities[i] > 0.2
                        ]
                        
                except Exception as e:
                    logger.warning(f"CLIP analysis failed: {e}")
            
            # Additional image analysis
            features.update({
                "estimated_complexity": self._estimate_image_complexity(features),
                "accessibility_alt_text": self._generate_alt_text(features),
                "quality_score": self._assess_image_quality(features)
            })
            
            return ModalityFeatures(
                modality=ModalityType.IMAGE,
                features=features,
                embeddings=embeddings,
                confidence=confidence,
                model_used=model_used
            )
            
        except Exception as e:
            logger.error(f"Error in image feature extraction: {e}")
            raise
    
    async def _extract_audio_features(self, file_path: str) -> ModalityFeatures:
        """Extract audio features and embeddings"""
        try:
            features = {
                "file_path": file_path,
                "format": Path(file_path).suffix.lower()
            }
            
            embeddings = None
            model_used = "basic"
            confidence = 0.7
            
            if HAS_LIBROSA:
                try:
                    # Load audio file
                    y, sr = librosa.load(file_path, duration=30)  # Limit to 30 seconds for analysis
                    
                    # Basic audio features
                    features.update({
                        "duration": len(y) / sr,
                        "sample_rate": sr,
                        "channels": 1,  # Librosa loads as mono by default
                        "rms_energy": float(np.sqrt(np.mean(y**2))),
                        "zero_crossing_rate": float(np.mean(librosa.feature.zero_crossing_rate(y))),
                        "spectral_centroid": float(np.mean(librosa.feature.spectral_centroid(y=y, sr=sr)))
                    })
                    
                    # Advanced audio features
                    mfccs = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=13)
                    chroma = librosa.feature.chroma(y=y, sr=sr)
                    spectral_contrast = librosa.feature.spectral_contrast(y=y, sr=sr)
                    
                    # Create embeddings from features
                    feature_vector = np.concatenate([
                        np.mean(mfccs, axis=1),
                        np.mean(chroma, axis=1),
                        np.mean(spectral_contrast, axis=1)
                    ])
                    embeddings = feature_vector
                    
                    features.update({
                        "mfcc_features": np.mean(mfccs, axis=1).tolist(),
                        "chroma_features": np.mean(chroma, axis=1).tolist(),
                        "spectral_contrast": np.mean(spectral_contrast, axis=1).tolist(),
                        "tempo": float(librosa.beat.tempo(y=y, sr=sr)[0])
                    })
                    
                    confidence = 0.9
                    model_used = "librosa"
                    
                except Exception as e:
                    logger.warning(f"Librosa analysis failed: {e}")
            
            # Additional audio analysis
            features.update({
                "estimated_speech": self._detect_speech_content(features),
                "music_probability": self._detect_music_content(features),
                "quality_score": self._assess_audio_quality(features)
            })
            
            return ModalityFeatures(
                modality=ModalityType.AUDIO,
                features=features,
                embeddings=embeddings,
                confidence=confidence,
                model_used=model_used
            )
            
        except Exception as e:
            logger.error(f"Error in audio feature extraction: {e}")
            raise
    
    async def _extract_video_features(self, file_path: str) -> ModalityFeatures:
        """Extract video features and embeddings"""
        try:
            features = {
                "file_path": file_path,
                "format": Path(file_path).suffix.lower()
            }
            
            embeddings = None
            model_used = "basic"
            confidence = 0.7
            
            if HAS_OPENCV:
                try:
                    cap = cv2.VideoCapture(file_path)
                    
                    # Basic video properties
                    fps = cap.get(cv2.CAP_PROP_FPS)
                    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
                    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
                    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
                    
                    features.update({
                        "duration": frame_count / fps if fps > 0 else 0,
                        "fps": fps,
                        "frame_count": frame_count,
                        "resolution": (width, height),
                        "aspect_ratio": width / height if height > 0 else 0
                    })
                    
                    # Sample frames for analysis
                    frame_features = []
                    sample_interval = max(1, frame_count // 10)  # Sample 10 frames
                    
                    for i in range(0, frame_count, sample_interval):
                        cap.set(cv2.CAP_PROP_POS_FRAMES, i)
                        ret, frame = cap.read()
                        if ret:
                            # Basic frame analysis
                            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                            brightness = np.mean(gray)
                            contrast = np.std(gray)
                            
                            frame_features.append({
                                "brightness": float(brightness),
                                "contrast": float(contrast),
                                "frame_number": i
                            })
                    
                    cap.release()
                    
                    features.update({
                        "avg_brightness": np.mean([f["brightness"] for f in frame_features]),
                        "avg_contrast": np.mean([f["contrast"] for f in frame_features]),
                        "frame_analysis": frame_features[:5]  # Keep first 5 for reference
                    })
                    
                    confidence = 0.85
                    model_used = "opencv"
                    
                except Exception as e:
                    logger.warning(f"OpenCV video analysis failed: {e}")
            
            # Additional video analysis
            features.update({
                "estimated_motion": self._estimate_motion_content(features),
                "quality_score": self._assess_video_quality(features),
                "accessibility_features": self._analyze_video_accessibility(features)
            })
            
            return ModalityFeatures(
                modality=ModalityType.VIDEO,
                features=features,
                embeddings=embeddings,
                confidence=confidence,
                model_used=model_used
            )
            
        except Exception as e:
            logger.error(f"Error in video feature extraction: {e}")
            raise
    
    async def _analyze_cross_modal_alignment(self, modalities: Dict[ModalityType, ModalityFeatures]) -> List[CrossModalAlignment]:
        """Analyze alignment between different modalities"""
        alignments = []
        
        try:
            modality_list = list(modalities.keys())
            
            # Analyze all pairs of modalities
            for i, source in enumerate(modality_list):
                for target in modality_list[i+1:]:
                    alignment = await self._calculate_modality_alignment(
                        modalities[source], modalities[target]
                    )
                    if alignment:
                        alignments.append(alignment)
            
            return alignments
            
        except Exception as e:
            logger.error(f"Error in cross-modal alignment analysis: {e}")
            return []
    
    async def _calculate_modality_alignment(self, source: ModalityFeatures, target: ModalityFeatures) -> Optional[CrossModalAlignment]:
        """Calculate alignment between two modalities"""
        try:
            alignment = CrossModalAlignment(
                source_modality=source.modality,
                target_modality=target.modality,
                alignment_score=0.0,
                semantic_similarity=0.0,
                emotional_coherence=0.0,
                style_consistency=0.0
            )
            
            # Semantic similarity using embeddings
            if source.embeddings is not None and target.embeddings is not None:
                # Normalize embeddings for cosine similarity
                source_norm = source.embeddings / np.linalg.norm(source.embeddings)
                target_norm = target.embeddings / np.linalg.norm(target.embeddings)
                alignment.semantic_similarity = float(np.dot(source_norm, target_norm))
            
            # Modality-specific alignment analysis
            if source.modality == ModalityType.TEXT and target.modality == ModalityType.IMAGE:
                alignment = await self._analyze_text_image_alignment(source, target, alignment)
            elif source.modality == ModalityType.AUDIO and target.modality == ModalityType.VIDEO:
                alignment = await self._analyze_audio_video_alignment(source, target, alignment)
            elif source.modality == ModalityType.TEXT and target.modality == ModalityType.AUDIO:
                alignment = await self._analyze_text_audio_alignment(source, target, alignment)
            
            # Calculate overall alignment score
            alignment.alignment_score = (
                alignment.semantic_similarity * 0.4 +
                alignment.emotional_coherence * 0.3 +
                alignment.style_consistency * 0.3
            )
            
            return alignment
            
        except Exception as e:
            logger.error(f"Error calculating modality alignment: {e}")
            return None
    
    async def _analyze_text_image_alignment(self, text_features: ModalityFeatures, 
                                          image_features: ModalityFeatures, 
                                          alignment: CrossModalAlignment) -> CrossModalAlignment:
        """Analyze text-image alignment"""
        try:
            # Check for concept overlap
            text_content = text_features.features.get("content", "").lower()
            image_concepts = image_features.features.get("detected_concepts", [])
            
            matching_concepts = []
            for concept_data in image_concepts:
                concept = concept_data.get("concept", "")
                if concept in text_content:
                    matching_concepts.append(concept)
                    alignment.semantic_similarity += concept_data.get("confidence", 0) * 0.1
            
            alignment.matching_concepts = matching_concepts
            
            # Emotional coherence analysis
            text_emotions = text_features.features.get("emotions", [])
            if text_emotions:
                # Simplified emotion mapping to image characteristics
                dominant_emotion = max(text_emotions, key=lambda x: x.get("score", 0))
                emotion_label = dominant_emotion.get("label", "").lower()
                
                # Map emotions to expected image characteristics
                if "joy" in emotion_label or "positive" in emotion_label:
                    expected_brightness = image_features.features.get("avg_brightness", 128)
                    if expected_brightness > 120:  # Bright images align with positive emotions
                        alignment.emotional_coherence += 0.3
                elif "sadness" in emotion_label or "negative" in emotion_label:
                    expected_brightness = image_features.features.get("avg_brightness", 128)
                    if expected_brightness < 100:  # Darker images align with negative emotions
                        alignment.emotional_coherence += 0.3
            
            # Style consistency (simplified)
            text_readability = text_features.features.get("readability_score", 0)
            image_complexity = image_features.features.get("estimated_complexity", 0.5)
            
            # Simple rule: formal text should align with clear, simple images
            if text_readability > 0.7 and image_complexity < 0.5:
                alignment.style_consistency += 0.4
            elif text_readability < 0.5 and image_complexity > 0.7:
                alignment.style_consistency += 0.3
            
            return alignment
            
        except Exception as e:
            logger.error(f"Error in text-image alignment analysis: {e}")
            return alignment
    
    async def _analyze_audio_video_alignment(self, audio_features: ModalityFeatures,
                                           video_features: ModalityFeatures,
                                           alignment: CrossModalAlignment) -> CrossModalAlignment:
        """Analyze audio-video alignment"""
        try:
            # Duration matching
            audio_duration = audio_features.features.get("duration", 0)
            video_duration = video_features.features.get("duration", 0)
            
            if audio_duration > 0 and video_duration > 0:
                duration_ratio = min(audio_duration, video_duration) / max(audio_duration, video_duration)
                alignment.semantic_similarity = duration_ratio
            
            # Tempo and motion correlation
            audio_tempo = audio_features.features.get("tempo", 120)
            video_motion = video_features.features.get("estimated_motion", 0.5)
            
            # Higher tempo should correlate with higher motion
            tempo_normalized = min(audio_tempo / 200, 1.0)  # Normalize tempo to 0-1
            if abs(tempo_normalized - video_motion) < 0.3:
                alignment.style_consistency += 0.4
            
            # Energy matching
            audio_energy = audio_features.features.get("rms_energy", 0)
            video_contrast = video_features.features.get("avg_contrast", 0)
            
            # Normalize and compare energy levels
            if audio_energy > 0 and video_contrast > 0:
                energy_correlation = 1 - abs((audio_energy * 100) - video_contrast) / 100
                alignment.emotional_coherence = max(0, energy_correlation)
            
            return alignment
            
        except Exception as e:
            logger.error(f"Error in audio-video alignment analysis: {e}")
            return alignment
    
    async def _analyze_text_audio_alignment(self, text_features: ModalityFeatures,
                                          audio_features: ModalityFeatures,
                                          alignment: CrossModalAlignment) -> CrossModalAlignment:
        """Analyze text-audio alignment"""
        try:
            # Speech content detection
            has_speech = audio_features.features.get("estimated_speech", False)
            text_content = text_features.features.get("content", "")
            
            if has_speech and len(text_content) > 0:
                alignment.semantic_similarity += 0.5  # Assume speech aligns with text
            
            # Mood alignment
            text_emotions = text_features.features.get("emotions", [])
            audio_tempo = audio_features.features.get("tempo", 120)
            audio_energy = audio_features.features.get("rms_energy", 0)
            
            if text_emotions:
                dominant_emotion = max(text_emotions, key=lambda x: x.get("score", 0))
                emotion_label = dominant_emotion.get("label", "").lower()
                
                # Map emotions to audio characteristics
                if "joy" in emotion_label or "excitement" in emotion_label:
                    if audio_tempo > 140 and audio_energy > 0.1:
                        alignment.emotional_coherence += 0.4
                elif "sadness" in emotion_label or "calm" in emotion_label:
                    if audio_tempo < 100 and audio_energy < 0.05:
                        alignment.emotional_coherence += 0.4
            
            # Formality alignment
            text_readability = text_features.features.get("readability_score", 0)
            music_probability = audio_features.features.get("music_probability", 0.5)
            
            # Formal text might align better with instrumental music
            if text_readability > 0.8 and music_probability > 0.7:
                alignment.style_consistency += 0.3
            
            return alignment
            
        except Exception as e:
            logger.error(f"Error in text-audio alignment analysis: {e}")
            return alignment
    
    async def _generate_intelligence_insights(self, analysis: MultimodalContent) -> List[IntelligenceInsight]:
        """Generate AI-powered insights about the content"""
        insights = []
        
        try:
            # Content coherence insights
            if analysis.alignments:
                avg_alignment = np.mean([a.alignment_score for a in analysis.alignments])
                if avg_alignment < 0.3:
                    insights.append(IntelligenceInsight(
                        id=str(uuid.uuid4()),
                        type="coherence_warning",
                        title="Low Cross-Modal Coherence",
                        description="The different content modalities don't align well semantically or stylistically.",
                        confidence=0.8,
                        affected_modalities=list(analysis.modalities.keys()),
                        recommendations=[
                            {
                                "type": "content_adjustment",
                                "description": "Consider adjusting content to improve alignment between modalities",
                                "priority": "high"
                            }
                        ]
                    ))
            
            # Accessibility insights
            accessibility_issues = []
            for modality, features in analysis.modalities.items():
                if modality == ModalityType.IMAGE and not features.features.get("accessibility_alt_text"):
                    accessibility_issues.append("Missing alt text for images")
                elif modality == ModalityType.VIDEO and not features.features.get("accessibility_features", {}).get("captions"):
                    accessibility_issues.append("Video lacks captions")
            
            if accessibility_issues:
                insights.append(IntelligenceInsight(
                    id=str(uuid.uuid4()),
                    type="accessibility_improvement",
                    title="Accessibility Enhancements Needed",
                    description=f"Found {len(accessibility_issues)} accessibility issues",
                    confidence=0.9,
                    affected_modalities=list(analysis.modalities.keys()),
                    recommendations=[
                        {
                            "type": "accessibility_fix",
                            "description": issue,
                            "priority": "medium"
                        }
                        for issue in accessibility_issues
                    ]
                ))
            
            # Quality insights
            low_quality_modalities = []
            for modality, features in analysis.modalities.items():
                quality_score = features.features.get("quality_score", 0.7)
                if quality_score < 0.5:
                    low_quality_modalities.append(modality.value)
            
            if low_quality_modalities:
                insights.append(IntelligenceInsight(
                    id=str(uuid.uuid4()),
                    type="quality_improvement",
                    title="Quality Enhancement Opportunities",
                    description=f"Some modalities have below-average quality: {', '.join(low_quality_modalities)}",
                    confidence=0.85,
                    affected_modalities=[ModalityType(m) for m in low_quality_modalities],
                    recommendations=[
                        {
                            "type": "quality_enhancement",
                            "description": f"Improve quality of {modality} content",
                            "priority": "medium"
                        }
                        for modality in low_quality_modalities
                    ]
                ))
            
            # Engagement prediction insights
            engagement_factors = self._analyze_engagement_factors(analysis)
            if engagement_factors:
                insights.append(IntelligenceInsight(
                    id=str(uuid.uuid4()),
                    type="engagement_optimization",
                    title="Engagement Optimization Suggestions",
                    description="AI-identified opportunities to improve content engagement",
                    confidence=0.75,
                    affected_modalities=list(analysis.modalities.keys()),
                    recommendations=engagement_factors
                ))
            
            return insights
            
        except Exception as e:
            logger.error(f"Error generating intelligence insights: {e}")
            return []
    
    def _analyze_engagement_factors(self, analysis: MultimodalContent) -> List[Dict[str, Any]]:
        """Analyze factors that could improve engagement"""
        recommendations = []
        
        try:
            # Analyze text engagement
            if ModalityType.TEXT in analysis.modalities:
                text_features = analysis.modalities[ModalityType.TEXT].features
                word_count = text_features.get("word_count", 0)
                
                if word_count > 1000:
                    recommendations.append({
                        "type": "text_optimization",
                        "description": "Consider breaking long text into shorter, more digestible sections",
                        "priority": "low"
                    })
                elif word_count < 100:
                    recommendations.append({
                        "type": "text_expansion",
                        "description": "Text content might benefit from more detail or context",
                        "priority": "low"
                    })
            
            # Analyze visual engagement
            if ModalityType.IMAGE in analysis.modalities:
                image_features = analysis.modalities[ModalityType.IMAGE].features
                color_complexity = image_features.get("color_complexity", 0.5)
                
                if color_complexity < 0.2:
                    recommendations.append({
                        "type": "visual_enhancement",
                        "description": "Consider adding more visual variety or color to improve engagement",
                        "priority": "low"
                    })
            
            # Analyze audio engagement
            if ModalityType.AUDIO in analysis.modalities:
                audio_features = analysis.modalities[ModalityType.AUDIO].features
                energy = audio_features.get("rms_energy", 0)
                
                if energy < 0.01:
                    recommendations.append({
                        "type": "audio_enhancement",
                        "description": "Audio content might benefit from increased energy or volume",
                        "priority": "low"
                    })
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Error analyzing engagement factors: {e}")
            return []
    
    async def _calculate_overall_scores(self, analysis: MultimodalContent):
        """Calculate overall assessment scores"""
        try:
            # Coherence score from alignments
            if analysis.alignments:
                analysis.coherence_score = np.mean([a.alignment_score for a in analysis.alignments])
            else:
                analysis.coherence_score = 0.8  # Single modality gets default high coherence
            
            # Quality score from individual modalities
            quality_scores = [
                features.features.get("quality_score", 0.7)
                for features in analysis.modalities.values()
            ]
            analysis.quality_score = np.mean(quality_scores) if quality_scores else 0.5
            
            # Engagement prediction based on various factors
            engagement_factors = []
            
            # Text engagement factors
            if ModalityType.TEXT in analysis.modalities:
                text_features = analysis.modalities[ModalityType.TEXT].features
                readability = text_features.get("readability_score", 0.5)
                engagement_factors.append(readability * 0.3)
            
            # Visual engagement factors
            if ModalityType.IMAGE in analysis.modalities:
                image_features = analysis.modalities[ModalityType.IMAGE].features
                color_complexity = image_features.get("color_complexity", 0.5)
                engagement_factors.append(color_complexity * 0.2)
            
            # Audio engagement factors
            if ModalityType.AUDIO in analysis.modalities:
                audio_features = analysis.modalities[ModalityType.AUDIO].features
                tempo = audio_features.get("tempo", 120)
                tempo_factor = min(tempo / 140, 1.0) * 0.2  # Normalize tempo
                engagement_factors.append(tempo_factor)
            
            analysis.engagement_prediction = sum(engagement_factors) + 0.5  # Base engagement
            analysis.engagement_prediction = min(analysis.engagement_prediction, 1.0)
            
            # Accessibility score
            accessibility_factors = []
            for modality, features in analysis.modalities.items():
                if modality == ModalityType.TEXT:
                    readability = features.features.get("readability_score", 0.5)
                    accessibility_factors.append(readability)
                elif modality == ModalityType.IMAGE:
                    has_alt_text = bool(features.features.get("accessibility_alt_text"))
                    accessibility_factors.append(0.8 if has_alt_text else 0.3)
                elif modality == ModalityType.VIDEO:
                    video_accessibility = features.features.get("accessibility_features", {})
                    score = 0.5
                    if video_accessibility.get("captions"):
                        score += 0.3
                    if video_accessibility.get("audio_description"):
                        score += 0.2
                    accessibility_factors.append(score)
                else:
                    accessibility_factors.append(0.6)  # Default for other modalities
            
            analysis.accessibility_score = np.mean(accessibility_factors) if accessibility_factors else 0.5
            
        except Exception as e:
            logger.error(f"Error calculating overall scores: {e}")
    
    # Helper methods for feature extraction
    def _calculate_readability(self, text: str) -> float:
        """Calculate text readability score (simplified)"""
        try:
            words = text.split()
            sentences = text.split('.')
            
            if len(sentences) == 0 or len(words) == 0:
                return 0.5
            
            avg_words_per_sentence = len(words) / len(sentences)
            
            # Simplified readability based on sentence length
            if avg_words_per_sentence < 15:
                return 0.9
            elif avg_words_per_sentence < 25:
                return 0.7
            else:
                return 0.4
                
        except Exception:
            return 0.5
    
    def _analyze_sentiment(self, text: str) -> float:
        """Analyze text sentiment (simplified)"""
        try:
            positive_words = ["good", "great", "excellent", "amazing", "wonderful", "fantastic"]
            negative_words = ["bad", "terrible", "awful", "horrible", "disappointing"]
            
            text_lower = text.lower()
            positive_count = sum(1 for word in positive_words if word in text_lower)
            negative_count = sum(1 for word in negative_words if word in text_lower)
            
            if positive_count + negative_count == 0:
                return 0.5  # Neutral
            
            return positive_count / (positive_count + negative_count)
            
        except Exception:
            return 0.5
    
    def _extract_key_concepts(self, text: str) -> List[str]:
        """Extract key concepts from text (simplified)"""
        try:
            # Simple keyword extraction based on frequency
            words = text.lower().split()
            word_freq = {}
            
            # Filter out common words
            stop_words = {"the", "and", "or", "but", "in", "on", "at", "to", "for", "of", "with", "by"}
            
            for word in words:
                clean_word = word.strip(".,!?;:")
                if len(clean_word) > 3 and clean_word not in stop_words:
                    word_freq[clean_word] = word_freq.get(clean_word, 0) + 1
            
            # Return top 5 most frequent words
            sorted_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
            return [word for word, freq in sorted_words[:5]]
            
        except Exception:
            return []
    
    def _get_readability_level(self, score: float) -> str:
        """Convert readability score to level"""
        if score > 0.8:
            return "Easy"
        elif score > 0.6:
            return "Medium"
        else:
            return "Difficult"
    
    def _estimate_image_complexity(self, features: Dict[str, Any]) -> float:
        """Estimate image complexity"""
        try:
            color_complexity = features.get("color_complexity", 0.5)
            has_concepts = len(features.get("detected_concepts", [])) > 0
            
            complexity = color_complexity
            if has_concepts:
                complexity += 0.2
            
            return min(complexity, 1.0)
            
        except Exception:
            return 0.5
    
    def _generate_alt_text(self, features: Dict[str, Any]) -> str:
        """Generate alt text for image"""
        try:
            concepts = features.get("detected_concepts", [])
            if concepts:
                primary_concept = max(concepts, key=lambda x: x.get("confidence", 0))
                return f"Image containing {primary_concept.get('concept', 'content')}"
            
            return "Image content"
            
        except Exception:
            return "Image"
    
    def _assess_image_quality(self, features: Dict[str, Any]) -> float:
        """Assess image quality"""
        try:
            dimensions = features.get("dimensions", (0, 0))
            
            # Basic quality assessment based on resolution
            total_pixels = dimensions[0] * dimensions[1]
            
            if total_pixels > 1920 * 1080:  # HD+
                return 0.9
            elif total_pixels > 1280 * 720:  # HD
                return 0.8
            elif total_pixels > 640 * 480:   # SD
                return 0.6
            else:
                return 0.4
                
        except Exception:
            return 0.5
    
    def _detect_speech_content(self, features: Dict[str, Any]) -> bool:
        """Detect if audio contains speech (simplified)"""
        try:
            # Simplified speech detection based on spectral features
            spectral_centroid = features.get("spectral_centroid", 0)
            zero_crossing_rate = features.get("zero_crossing_rate", 0)
            
            # Speech typically has specific spectral characteristics
            if 1000 < spectral_centroid < 4000 and 0.1 < zero_crossing_rate < 0.3:
                return True
            
            return False
            
        except Exception:
            return False
    
    def _detect_music_content(self, features: Dict[str, Any]) -> float:
        """Detect probability of music content"""
        try:
            tempo = features.get("tempo", 0)
            rms_energy = features.get("rms_energy", 0)
            
            # Music typically has consistent tempo and energy
            if 60 < tempo < 200 and rms_energy > 0.01:
                return 0.8
            
            return 0.3
            
        except Exception:
            return 0.5
    
    def _assess_audio_quality(self, features: Dict[str, Any]) -> float:
        """Assess audio quality"""
        try:
            sample_rate = features.get("sample_rate", 22050)
            
            if sample_rate >= 44100:
                return 0.9
            elif sample_rate >= 22050:
                return 0.7
            else:
                return 0.5
                
        except Exception:
            return 0.5
    
    def _estimate_motion_content(self, features: Dict[str, Any]) -> float:
        """Estimate motion in video content"""
        try:
            frame_analysis = features.get("frame_analysis", [])
            
            if len(frame_analysis) < 2:
                return 0.5
            
            # Calculate brightness variation as proxy for motion
            brightness_values = [frame["brightness"] for frame in frame_analysis]
            brightness_std = np.std(brightness_values)
            
            # Normalize to 0-1 range
            motion_estimate = min(brightness_std / 50, 1.0)
            return motion_estimate
            
        except Exception:
            return 0.5
    
    def _assess_video_quality(self, features: Dict[str, Any]) -> float:
        """Assess video quality"""
        try:
            resolution = features.get("resolution", (0, 0))
            fps = features.get("fps", 0)
            
            total_pixels = resolution[0] * resolution[1]
            
            quality = 0.0
            
            # Resolution score
            if total_pixels > 1920 * 1080:
                quality += 0.5
            elif total_pixels > 1280 * 720:
                quality += 0.4
            elif total_pixels > 640 * 480:
                quality += 0.3
            else:
                quality += 0.2
            
            # FPS score
            if fps >= 60:
                quality += 0.3
            elif fps >= 30:
                quality += 0.25
            elif fps >= 24:
                quality += 0.2
            else:
                quality += 0.1
            
            # Contrast/clarity score
            avg_contrast = features.get("avg_contrast", 0)
            if avg_contrast > 50:
                quality += 0.2
            elif avg_contrast > 30:
                quality += 0.15
            else:
                quality += 0.1
            
            return min(quality, 1.0)
            
        except Exception:
            return 0.5
    
    def _analyze_video_accessibility(self, features: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze video accessibility features"""
        return {
            "captions": False,  # Would need actual caption detection
            "audio_description": False,  # Would need audio analysis
            "contrast_ratio": "unknown",  # Would need detailed frame analysis
            "motion_sensitivity": "low" if features.get("estimated_motion", 0.5) < 0.3 else "medium"
        }
    
    def _create_audio_extractor(self):
        """Create audio feature extractor"""
        return lambda x: "audio_extractor_ready"
    
    def _create_video_extractor(self):
        """Create video feature extractor"""
        return lambda x: "video_extractor_ready"


# Convenience functions for easy usage
async def analyze_multimodal_content(content_files: Dict[str, str], title: str = "Untitled",
                                   intelligence_level: str = "advanced") -> Dict[str, Any]:
    """Analyze multimodal content for intelligence insights
    
    Args:
        content_files: Dictionary mapping modality types to file paths
        title: Content title
        intelligence_level: Level of intelligence processing
        
    Returns:
        Analysis results
    """
    intelligence = MultimodalIntelligence(IntelligenceLevel(intelligence_level))
    
    content_data = {
        "id": str(uuid.uuid4()),
        "title": title,
        "files": content_files
    }
    
    analysis = await intelligence.analyze_multimodal_content(content_data)
    
    # Convert to serializable format
    return {
        "id": analysis.id,
        "content_id": analysis.content_id,
        "title": analysis.title,
        "coherence_score": analysis.coherence_score,
        "quality_score": analysis.quality_score,
        "engagement_prediction": analysis.engagement_prediction,
        "accessibility_score": analysis.accessibility_score,
        "processing_time": analysis.processing_time,
        "insights": [
            {
                "type": insight.type,
                "title": insight.title,
                "description": insight.description,
                "confidence": insight.confidence,
                "recommendations": insight.recommendations
            }
            for insight in analysis.insights
        ],
        "alignments": [
            {
                "source": alignment.source_modality.value,
                "target": alignment.target_modality.value,
                "alignment_score": alignment.alignment_score,
                "semantic_similarity": alignment.semantic_similarity,
                "recommendations": alignment.recommendations
            }
            for alignment in analysis.alignments
        ]
    }


if __name__ == "__main__":
    # Example usage
    async def main():
        # Create multimodal intelligence system
        intelligence = MultimodalIntelligence(IntelligenceLevel.ADVANCED)
        
        # Example content analysis
        content_data = {
            "id": "example_content_123",
            "title": "Marketing Campaign Content",
            "files": {
                "text": "/path/to/marketing_copy.txt",
                "image": "/path/to/hero_image.jpg",
                "audio": "/path/to/background_music.mp3"
            }
        }
        
        # Note: This would require actual files to run
        print("Multimodal Intelligence system initialized")
        print("Ready to analyze content across text, image, audio, and video modalities")
        print("Features: Cross-modal alignment, semantic coherence, quality assessment, engagement prediction")
    
    asyncio.run(main())