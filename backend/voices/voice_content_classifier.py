"""Voice Content Classification System

AI-powered voice content classification system for automatic categorization,
content type detection, and intelligent voice content organization.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Union, Tuple
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime
import json

try:
    import numpy as np
except ImportError:
    np = None

try:
    from creator_voice_intelligence import CreatorType, VoiceContentType
    from voice_metadata_generator import ContentCategory, VoiceFeature
except ImportError:
    from .creator_voice_intelligence import CreatorType, VoiceContentType
    from .voice_metadata_generator import ContentCategory, VoiceFeature

logger = logging.getLogger(__name__)


class ClassificationMethod(Enum):
    """Voice content classification methods"""
    ACOUSTIC_ANALYSIS = "acoustic_analysis"
    SEMANTIC_ANALYSIS = "semantic_analysis"
    PATTERN_RECOGNITION = "pattern_recognition"
    MACHINE_LEARNING = "machine_learning"
    HYBRID_ANALYSIS = "hybrid_analysis"


class ContentGenre(Enum):
    """Detailed content genres"""
    MUSIC_VOCAL = "music_vocal"
    MUSIC_INSTRUMENTAL = "music_instrumental"
    PODCAST_INTERVIEW = "podcast_interview"
    PODCAST_SOLO = "podcast_solo"
    AUDIOBOOK_FICTION = "audiobook_fiction"
    AUDIOBOOK_NONFICTION = "audiobook_nonfiction"
    NEWS_BROADCAST = "news_broadcast"
    COMMERCIAL_AD = "commercial_ad"
    VOICEOVER_DOCUMENTARY = "voiceover_documentary"
    VOICEOVER_ANIMATION = "voiceover_animation"
    EDUCATIONAL_LECTURE = "educational_lecture"
    EDUCATIONAL_TUTORIAL = "educational_tutorial"
    ENTERTAINMENT_COMEDY = "entertainment_comedy"
    ENTERTAINMENT_DRAMA = "entertainment_drama"
    BUSINESS_PRESENTATION = "business_presentation"
    PERSONAL_VLOG = "personal_vlog"


class AudioQuality(Enum):
    """Audio quality classifications"""
    STUDIO_QUALITY = "studio_quality"
    PROFESSIONAL = "professional"
    GOOD = "good"
    ACCEPTABLE = "acceptable"
    POOR = "poor"
    NOISE_HEAVY = "noise_heavy"


class SpeechPattern(Enum):
    """Speech pattern classifications"""
    CONVERSATIONAL = "conversational"
    FORMAL_PRESENTATION = "formal_presentation"
    NARRATIVE = "narrative"
    INSTRUCTIONAL = "instructional"
    EMOTIONAL_EXPRESSIVE = "emotional_expressive"
    MONOTONE = "monotone"
    RHYTHMIC = "rhythmic"
    SPONTANEOUS = "spontaneous"


@dataclass
class ClassificationConfidence:
    """Classification confidence scores"""
    primary_category: float = 0.0
    genre_classification: float = 0.0
    quality_assessment: float = 0.0
    creator_type: float = 0.0
    speech_pattern: float = 0.0
    overall_confidence: float = 0.0


@dataclass
class VoiceContentClassification:
    """Voice content classification result"""
    content_id: str
    primary_category: ContentCategory
    genre: ContentGenre
    creator_type: CreatorType
    voice_content_type: VoiceContentType
    audio_quality: AudioQuality
    speech_pattern: SpeechPattern
    
    # Detailed classification data
    acoustic_features: Dict[str, Any] = field(default_factory=dict)
    semantic_features: Dict[str, Any] = field(default_factory=dict)
    content_characteristics: Dict[str, Any] = field(default_factory=dict)
    
    # Confidence scores
    confidence: ClassificationConfidence = field(default_factory=ClassificationConfidence)
    
    # Alternative classifications
    alternative_categories: List[Tuple[ContentCategory, float]] = field(default_factory=list)
    alternative_genres: List[Tuple[ContentGenre, float]] = field(default_factory=list)
    
    # Metadata
    classification_method: ClassificationMethod = ClassificationMethod.HYBRID_ANALYSIS
    processing_time: float = 0.0
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class ClassificationResult:
    """Classification operation result"""
    success: bool
    classification: Optional[VoiceContentClassification] = None
    error_message: Optional[str] = None
    warnings: List[str] = field(default_factory=list)
    processing_metrics: Dict[str, Any] = field(default_factory=dict)


class VoiceContentClassifier:
    """Voice content classification engine"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize voice content classifier"""
        self.config = config or {}
        self.logger = logging.getLogger(__name__)
        
        # Initialize classification models
        self._init_classification_models()
        
        # Classification thresholds
        self.confidence_thresholds = {
            "minimum_confidence": 0.6,
            "high_confidence": 0.8,
            "uncertainty_threshold": 0.5
        }
        
        self.logger.info("Voice content classifier initialized")
    
    def _init_classification_models(self):
        """Initialize classification models and features"""
        # Feature extractors for different classification methods
        self.feature_extractors = {
            ClassificationMethod.ACOUSTIC_ANALYSIS: self._extract_acoustic_features,
            ClassificationMethod.SEMANTIC_ANALYSIS: self._extract_semantic_features,
            ClassificationMethod.PATTERN_RECOGNITION: self._extract_pattern_features,
            ClassificationMethod.MACHINE_LEARNING: self._extract_ml_features
        }
        
        # Classification rules and patterns
        self.classification_rules = self._load_classification_rules()
    
    def _load_classification_rules(self) -> Dict[str, Any]:
        """Load classification rules and patterns"""
        return {
            "duration_rules": {
                "short_form": {"max": 60, "categories": [ContentCategory.COMMERCIAL]},
                "medium_form": {"min": 60, "max": 1800, "categories": [ContentCategory.NARRATION, ContentCategory.EDUCATIONAL]},
                "long_form": {"min": 1800, "categories": [ContentCategory.PODCAST, ContentCategory.AUDIOBOOK]}
            },
            "frequency_patterns": {
                "music": {"fundamental_freq_range": (80, 1100), "harmonic_content": "high"},
                "speech": {"fundamental_freq_range": (85, 255), "harmonic_content": "medium"},
                "commercial": {"dynamic_range": "high", "compression": "heavy"}
            },
            "content_keywords": {
                ContentGenre.PODCAST_INTERVIEW: ["interview", "discussion", "conversation", "guest"],
                ContentGenre.EDUCATIONAL_LECTURE: ["lesson", "tutorial", "learn", "education"],
                ContentGenre.NEWS_BROADCAST: ["news", "breaking", "report", "update"],
                ContentGenre.COMMERCIAL_AD: ["buy", "sale", "offer", "product", "service"]
            }
        }
    
    async def classify_content(
        self,
        voice_content: bytes,
        content_id: str,
        method: ClassificationMethod = ClassificationMethod.HYBRID_ANALYSIS,
        metadata: Optional[Dict[str, Any]] = None
    ) -> ClassificationResult:
        """Classify voice content using specified method"""
        start_time = datetime.now()
        
        try:
            # Extract features based on classification method
            if method == ClassificationMethod.HYBRID_ANALYSIS:
                features = await self._extract_hybrid_features(voice_content, metadata)
            else:
                extractor = self.feature_extractors.get(method)
                if not extractor:
                    raise ValueError(f"Unknown classification method: {method}")
                features = await extractor(voice_content, metadata)
            
            # Perform classification
            classification = await self._perform_classification(
                content_id, features, method, metadata
            )
            
            # Calculate processing time
            processing_time = (datetime.now() - start_time).total_seconds()
            classification.processing_time = processing_time
            
            # Validate classification quality
            warnings = self._validate_classification(classification)
            
            return ClassificationResult(
                success=True,
                classification=classification,
                warnings=warnings,
                processing_metrics={
                    "processing_time": processing_time,
                    "feature_count": len(features),
                    "confidence_level": classification.confidence.overall_confidence
                }
            )
            
        except Exception as e:
            self.logger.error(f"Content classification failed: {str(e)}")
            processing_time = (datetime.now() - start_time).total_seconds()
            
            return ClassificationResult(
                success=False,
                error_message=str(e),
                processing_metrics={"processing_time": processing_time}
            )
    
    async def _extract_hybrid_features(
        self,
        voice_content: bytes,
        metadata: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Extract features using hybrid analysis approach"""
        features = {}
        
        # Extract acoustic features
        acoustic_features = await self._extract_acoustic_features(voice_content, metadata)
        features.update({"acoustic": acoustic_features})
        
        # Extract semantic features
        semantic_features = await self._extract_semantic_features(voice_content, metadata)
        features.update({"semantic": semantic_features})
        
        # Extract pattern features
        pattern_features = await self._extract_pattern_features(voice_content, metadata)
        features.update({"pattern": pattern_features})
        
        # Extract ML features
        ml_features = await self._extract_ml_features(voice_content, metadata)
        features.update({"ml": ml_features})
        
        return features
    
    async def _extract_acoustic_features(
        self,
        voice_content: bytes,
        metadata: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Extract acoustic audio features"""
        try:
            # Simulate acoustic feature extraction
            # In real implementation, use librosa, scipy, or similar
            duration = len(voice_content) / (44100 * 2)  # Simplified duration calculation
            
            features = {
                "duration": duration,
                "sample_rate": 44100,
                "spectral_features": {
                    "spectral_centroid": 2500.0,
                    "spectral_rolloff": 8000.0,
                    "zero_crossing_rate": 0.1,
                    "spectral_contrast": [0.5, 0.7, 0.8, 0.6, 0.4, 0.3, 0.2]
                },
                "temporal_features": {
                    "tempo": 120.0 if duration > 60 else 0.0,  # Music vs speech indicator
                    "rhythmic_pattern": "speech" if duration > 120 else "music",
                    "pause_detection": duration / 60  # Simplified pause ratio
                },
                "frequency_features": {
                    "fundamental_frequency": 150.0,  # Hz
                    "formant_frequencies": [800, 1200, 2400],  # Hz
                    "harmonic_ratio": 0.7,
                    "noise_ratio": 0.1
                },
                "dynamic_features": {
                    "dynamic_range": 45.0,  # dB
                    "rms_energy": 0.3,
                    "peak_level": -3.0,  # dBFS
                    "loudness_range": 15.0  # LU
                }
            }
            
            return features
            
        except Exception as e:
            self.logger.error(f"Acoustic feature extraction failed: {str(e)}")
            return {}
    
    async def _extract_semantic_features(
        self,
        voice_content: bytes,
        metadata: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Extract semantic content features"""
        try:
            # Simulate semantic analysis
            # In real implementation, use speech-to-text and NLP
            
            # Simulated transcript analysis
            features = {
                "transcript_available": True,
                "language": "en-US",
                "word_count": 250,
                "vocabulary_complexity": "intermediate",
                "topic_categories": ["technology", "business"],
                "content_keywords": ["artificial", "intelligence", "voice", "processing"],
                "named_entities": ["OpenAI", "Google", "Microsoft"],
                "sentiment_analysis": {
                    "overall_sentiment": "neutral",
                    "confidence": 0.8,
                    "emotional_tone": "professional"
                },
                "discourse_markers": {
                    "questions": 5,
                    "statements": 45,
                    "exclamations": 2
                },
                "content_structure": {
                    "has_introduction": True,
                    "has_conclusion": True,
                    "section_count": 3,
                    "logical_flow": "good"
                }
            }
            
            return features
            
        except Exception as e:
            self.logger.error(f"Semantic feature extraction failed: {str(e)}")
            return {}
    
    async def _extract_pattern_features(
        self,
        voice_content: bytes,
        metadata: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Extract pattern recognition features"""
        try:
            duration = len(voice_content) / (44100 * 2)
            
            features = {
                "duration_pattern": "long" if duration > 1800 else "medium" if duration > 300 else "short",
                "speech_patterns": {
                    "speaking_rate": "normal",
                    "pause_patterns": "natural",
                    "intonation_variety": "high",
                    "emphasis_patterns": "moderate"
                },
                "content_patterns": {
                    "repetition_level": "low",
                    "structure_type": "conversational",
                    "interaction_indicators": "monologue",
                    "professional_indicators": "high"
                },
                "audio_patterns": {
                    "background_noise": "minimal",
                    "echo_reverb": "none",
                    "compression_artifacts": "none",
                    "editing_indicators": "present"
                },
                "genre_indicators": {
                    "music_elements": False,
                    "commercial_elements": False,
                    "educational_elements": True,
                    "entertainment_elements": False
                }
            }
            
            return features
            
        except Exception as e:
            self.logger.error(f"Pattern feature extraction failed: {str(e)}")
            return {}
    
    async def _extract_ml_features(
        self,
        voice_content: bytes,
        metadata: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Extract machine learning model features"""
        try:
            # Simulate ML model predictions
            features = {
                "content_type_prediction": {
                    "podcast": 0.75,
                    "audiobook": 0.15,
                    "music": 0.05,
                    "commercial": 0.05
                },
                "quality_prediction": {
                    "studio_quality": 0.6,
                    "professional": 0.3,
                    "good": 0.1
                },
                "creator_type_prediction": {
                    "podcaster": 0.8,
                    "narrator": 0.15,
                    "musician": 0.05
                },
                "audience_prediction": {
                    "adults_25_45": 0.7,
                    "professionals": 0.8,
                    "tech_enthusiasts": 0.9
                },
                "engagement_prediction": {
                    "high_engagement": 0.65,
                    "viral_potential": 0.3,
                    "retention_rate": 0.75
                }
            }
            
            return features
            
        except Exception as e:
            self.logger.error(f"ML feature extraction failed: {str(e)}")
            return {}
    
    async def _perform_classification(
        self,
        content_id: str,
        features: Dict[str, Any],
        method: ClassificationMethod,
        metadata: Optional[Dict[str, Any]]
    ) -> VoiceContentClassification:
        """Perform content classification based on extracted features"""
        
        # Initialize classification result
        classification = VoiceContentClassification(
            content_id=content_id,
            primary_category=ContentCategory.PODCAST,  # Default
            genre=ContentGenre.PODCAST_SOLO,  # Default
            creator_type=CreatorType.PODCASTER,  # Default
            voice_content_type=VoiceContentType.PODCAST,  # Default
            audio_quality=AudioQuality.PROFESSIONAL,  # Default
            speech_pattern=SpeechPattern.CONVERSATIONAL,  # Default
            classification_method=method
        )
        
        # Classify primary category
        primary_category, category_confidence = self._classify_primary_category(features)
        classification.primary_category = primary_category
        classification.confidence.primary_category = category_confidence
        
        # Classify genre
        genre, genre_confidence = self._classify_genre(features, primary_category)
        classification.genre = genre
        classification.confidence.genre_classification = genre_confidence
        
        # Classify creator type
        creator_type, creator_confidence = self._classify_creator_type(features, primary_category)
        classification.creator_type = creator_type
        classification.confidence.creator_type = creator_confidence
        
        # Map to voice content type
        classification.voice_content_type = self._map_to_voice_content_type(genre, creator_type)
        
        # Assess audio quality
        quality, quality_confidence = self._assess_audio_quality(features)
        classification.audio_quality = quality
        classification.confidence.quality_assessment = quality_confidence
        
        # Identify speech pattern
        pattern, pattern_confidence = self._identify_speech_pattern(features)
        classification.speech_pattern = pattern
        classification.confidence.speech_pattern = pattern_confidence
        
        # Calculate overall confidence
        classification.confidence.overall_confidence = self._calculate_overall_confidence(
            classification.confidence
        )
        
        # Store detailed features
        classification.acoustic_features = features.get("acoustic", {})
        classification.semantic_features = features.get("semantic", {})
        classification.content_characteristics = self._extract_content_characteristics(features)
        
        # Generate alternatives
        classification.alternative_categories = self._generate_alternative_categories(features)
        classification.alternative_genres = self._generate_alternative_genres(features, primary_category)
        
        return classification
    
    def _classify_primary_category(self, features: Dict[str, Any]) -> Tuple[ContentCategory, float]:
        """Classify primary content category"""
        try:
            # Check ML predictions if available
            if "ml" in features and "content_type_prediction" in features["ml"]:
                predictions = features["ml"]["content_type_prediction"]
                max_pred = max(predictions.items(), key=lambda x: x[1])
                
                category_map = {
                    "podcast": ContentCategory.PODCAST,
                    "audiobook": ContentCategory.NARRATION,
                    "music": ContentCategory.MUSIC,
                    "commercial": ContentCategory.COMMERCIAL,
                    "news": ContentCategory.NEWS,
                    "educational": ContentCategory.EDUCATIONAL
                }
                
                category = category_map.get(max_pred[0], ContentCategory.PODCAST)
                confidence = max_pred[1]
                
                return category, confidence
            
            # Fallback to rule-based classification
            duration = features.get("acoustic", {}).get("duration", 0)
            
            if duration < 60:
                return ContentCategory.COMMERCIAL, 0.8
            elif duration > 1800:
                return ContentCategory.PODCAST, 0.7
            else:
                return ContentCategory.NARRATION, 0.6
                
        except Exception as e:
            self.logger.error(f"Primary category classification failed: {str(e)}")
            return ContentCategory.PODCAST, 0.5
    
    def _classify_genre(
        self,
        features: Dict[str, Any],
        primary_category: ContentCategory
    ) -> Tuple[ContentGenre, float]:
        """Classify content genre based on category"""
        try:
            if primary_category == ContentCategory.PODCAST:
                # Check for interview indicators
                semantic = features.get("semantic", {})
                if "questions" in str(semantic) or "interview" in str(semantic):
                    return ContentGenre.PODCAST_INTERVIEW, 0.8
                else:
                    return ContentGenre.PODCAST_SOLO, 0.7
            
            elif primary_category == ContentCategory.MUSIC:
                # Check for vocal content
                acoustic = features.get("acoustic", {})
                if acoustic.get("frequency_features", {}).get("harmonic_ratio", 0) > 0.8:
                    return ContentGenre.MUSIC_VOCAL, 0.75
                else:
                    return ContentGenre.MUSIC_INSTRUMENTAL, 0.75
            
            elif primary_category == ContentCategory.NARRATION:
                # Classify based on content characteristics
                semantic = features.get("semantic", {})
                if "story" in str(semantic) or "fiction" in str(semantic):
                    return ContentGenre.AUDIOBOOK_FICTION, 0.7
                else:
                    return ContentGenre.AUDIOBOOK_NONFICTION, 0.7
            
            elif primary_category == ContentCategory.COMMERCIAL:
                return ContentGenre.COMMERCIAL_AD, 0.8
            
            elif primary_category == ContentCategory.EDUCATIONAL:
                return ContentGenre.EDUCATIONAL_LECTURE, 0.7
            
            else:
                return ContentGenre.PODCAST_SOLO, 0.5  # Default
                
        except Exception as e:
            self.logger.error(f"Genre classification failed: {str(e)}")
            return ContentGenre.PODCAST_SOLO, 0.5
    
    def _classify_creator_type(
        self,
        features: Dict[str, Any],
        primary_category: ContentCategory
    ) -> Tuple[CreatorType, float]:
        """Classify creator type"""
        try:
            # Check ML predictions
            if "ml" in features and "creator_type_prediction" in features["ml"]:
                predictions = features["ml"]["creator_type_prediction"]
                max_pred = max(predictions.items(), key=lambda x: x[1])
                
                creator_map = {
                    "podcaster": CreatorType.PODCASTER,
                    "narrator": CreatorType.NARRATOR,
                    "musician": CreatorType.MUSICIAN,
                    "voice_actor": CreatorType.VOICE_ACTOR
                }
                
                creator_type = creator_map.get(max_pred[0], CreatorType.PODCASTER)
                confidence = max_pred[1]
                
                return creator_type, confidence
            
            # Fallback to category-based mapping
            category_to_creator = {
                ContentCategory.PODCAST: CreatorType.PODCASTER,
                ContentCategory.MUSIC: CreatorType.MUSICIAN,
                ContentCategory.NARRATION: CreatorType.NARRATOR,
                ContentCategory.COMMERCIAL: CreatorType.VOICE_ACTOR,
                ContentCategory.EDUCATIONAL: CreatorType.NARRATOR
            }
            
            creator_type = category_to_creator.get(primary_category, CreatorType.PODCASTER)
            return creator_type, 0.7
            
        except Exception as e:
            self.logger.error(f"Creator type classification failed: {str(e)}")
            return CreatorType.PODCASTER, 0.5
    
    def _map_to_voice_content_type(
        self,
        genre: ContentGenre,
        creator_type: CreatorType
    ) -> VoiceContentType:
        """Map genre and creator type to voice content type"""
        genre_to_voice_type = {
            ContentGenre.PODCAST_INTERVIEW: VoiceContentType.PODCAST,
            ContentGenre.PODCAST_SOLO: VoiceContentType.PODCAST,
            ContentGenre.MUSIC_VOCAL: VoiceContentType.SINGING,
            ContentGenre.AUDIOBOOK_FICTION: VoiceContentType.NARRATION,
            ContentGenre.AUDIOBOOK_NONFICTION: VoiceContentType.NARRATION,
            ContentGenre.COMMERCIAL_AD: VoiceContentType.VOICE_OVER,
            ContentGenre.EDUCATIONAL_LECTURE: VoiceContentType.SPEAKING
        }
        
        return genre_to_voice_type.get(genre, VoiceContentType.SPEAKING)
    
    def _assess_audio_quality(self, features: Dict[str, Any]) -> Tuple[AudioQuality, float]:
        """Assess audio quality"""
        try:
            acoustic = features.get("acoustic", {})
            dynamic_features = acoustic.get("dynamic_features", {})
            
            # Check ML quality prediction
            if "ml" in features and "quality_prediction" in features["ml"]:
                predictions = features["ml"]["quality_prediction"]
                max_pred = max(predictions.items(), key=lambda x: x[1])
                
                quality_map = {
                    "studio_quality": AudioQuality.STUDIO_QUALITY,
                    "professional": AudioQuality.PROFESSIONAL,
                    "good": AudioQuality.GOOD,
                    "acceptable": AudioQuality.ACCEPTABLE,
                    "poor": AudioQuality.POOR
                }
                
                quality = quality_map.get(max_pred[0], AudioQuality.GOOD)
                confidence = max_pred[1]
                
                return quality, confidence
            
            # Rule-based quality assessment
            dynamic_range = dynamic_features.get("dynamic_range", 0)
            noise_ratio = acoustic.get("frequency_features", {}).get("noise_ratio", 1.0)
            
            if dynamic_range > 40 and noise_ratio < 0.1:
                return AudioQuality.STUDIO_QUALITY, 0.8
            elif dynamic_range > 30 and noise_ratio < 0.2:
                return AudioQuality.PROFESSIONAL, 0.7
            elif dynamic_range > 20 and noise_ratio < 0.3:
                return AudioQuality.GOOD, 0.6
            else:
                return AudioQuality.ACCEPTABLE, 0.5
                
        except Exception as e:
            self.logger.error(f"Audio quality assessment failed: {str(e)}")
            return AudioQuality.GOOD, 0.5
    
    def _identify_speech_pattern(self, features: Dict[str, Any]) -> Tuple[SpeechPattern, float]:
        """Identify speech pattern"""
        try:
            pattern_features = features.get("pattern", {})
            speech_patterns = pattern_features.get("speech_patterns", {})
            
            # Analyze speech characteristics
            intonation = speech_patterns.get("intonation_variety", "medium")
            structure = pattern_features.get("content_patterns", {}).get("structure_type", "conversational")
            
            if structure == "conversational":
                return SpeechPattern.CONVERSATIONAL, 0.8
            elif "presentation" in structure:
                return SpeechPattern.FORMAL_PRESENTATION, 0.8
            elif "narrative" in structure:
                return SpeechPattern.NARRATIVE, 0.8
            elif "instructional" in structure:
                return SpeechPattern.INSTRUCTIONAL, 0.8
            else:
                return SpeechPattern.CONVERSATIONAL, 0.6
                
        except Exception as e:
            self.logger.error(f"Speech pattern identification failed: {str(e)}")
            return SpeechPattern.CONVERSATIONAL, 0.5
    
    def _calculate_overall_confidence(self, confidence: ClassificationConfidence) -> float:
        """Calculate overall classification confidence"""
        try:
            confidences = [
                confidence.primary_category,
                confidence.genre_classification,
                confidence.quality_assessment,
                confidence.creator_type,
                confidence.speech_pattern
            ]
            
            # Remove zero confidence scores
            valid_confidences = [c for c in confidences if c > 0]
            
            if not valid_confidences:
                return 0.0
            
            # Calculate weighted average (primary category has higher weight)
            weights = [0.3, 0.25, 0.15, 0.2, 0.1][:len(valid_confidences)]
            weighted_sum = sum(c * w for c, w in zip(valid_confidences, weights))
            weight_sum = sum(weights)
            
            return weighted_sum / weight_sum
            
        except Exception as e:
            self.logger.error(f"Overall confidence calculation failed: {str(e)}")
            return 0.5
    
    def _extract_content_characteristics(self, features: Dict[str, Any]) -> Dict[str, Any]:
        """Extract content characteristics summary"""
        characteristics = {}
        
        # Duration characteristics
        acoustic = features.get("acoustic", {})
        duration = acoustic.get("duration", 0)
        characteristics["duration_category"] = (
            "short" if duration < 300 else
            "medium" if duration < 1800 else
            "long"
        )
        
        # Content complexity
        semantic = features.get("semantic", {})
        characteristics["complexity"] = semantic.get("vocabulary_complexity", "unknown")
        
        # Production quality indicators
        pattern = features.get("pattern", {})
        characteristics["production_quality"] = pattern.get("audio_patterns", {})
        
        return characteristics
    
    def _generate_alternative_categories(
        self,
        features: Dict[str, Any]
    ) -> List[Tuple[ContentCategory, float]]:
        """Generate alternative category classifications"""
        alternatives = []
        
        # If ML predictions available, use them
        if "ml" in features and "content_type_prediction" in features["ml"]:
            predictions = features["ml"]["content_type_prediction"]
            
            category_map = {
                "podcast": ContentCategory.PODCAST,
                "audiobook": ContentCategory.NARRATION,
                "music": ContentCategory.MUSIC,
                "commercial": ContentCategory.COMMERCIAL,
                "news": ContentCategory.NEWS,
                "educational": ContentCategory.EDUCATIONAL
            }
            
            # Sort by confidence and take top alternatives
            sorted_predictions = sorted(predictions.items(), key=lambda x: x[1], reverse=True)
            
            for pred_type, confidence in sorted_predictions[1:4]:  # Skip top prediction
                if pred_type in category_map and confidence > 0.1:
                    alternatives.append((category_map[pred_type], confidence))
        
        return alternatives
    
    def _generate_alternative_genres(
        self,
        features: Dict[str, Any],
        primary_category: ContentCategory
    ) -> List[Tuple[ContentGenre, float]]:
        """Generate alternative genre classifications"""
        alternatives = []
        
        # Generate genre alternatives based on category
        if primary_category == ContentCategory.PODCAST:
            alternatives = [
                (ContentGenre.PODCAST_INTERVIEW, 0.4),
                (ContentGenre.PODCAST_SOLO, 0.3)
            ]
        elif primary_category == ContentCategory.EDUCATIONAL:
            alternatives = [
                (ContentGenre.EDUCATIONAL_TUTORIAL, 0.5),
                (ContentGenre.EDUCATIONAL_LECTURE, 0.4)
            ]
        
        return alternatives
    
    def _validate_classification(self, classification: VoiceContentClassification) -> List[str]:
        """Validate classification results and return warnings"""
        warnings = []
        
        # Check confidence levels
        if classification.confidence.overall_confidence < self.confidence_thresholds["minimum_confidence"]:
            warnings.append("Low overall classification confidence")
        
        # Check for inconsistencies
        if (classification.primary_category == ContentCategory.MUSIC and 
            classification.creator_type != CreatorType.MUSICIAN):
            warnings.append("Potential inconsistency between category and creator type")
        
        # Check duration vs category consistency
        duration = classification.acoustic_features.get("duration", 0)
        if (classification.primary_category == ContentCategory.COMMERCIAL and duration > 120):
            warnings.append("Long duration for commercial content")
        
        return warnings
    
    async def batch_classify(
        self,
        content_list: List[Tuple[bytes, str]],  # (content, content_id)
        method: ClassificationMethod = ClassificationMethod.HYBRID_ANALYSIS
    ) -> List[ClassificationResult]:
        """Classify multiple voice contents in batch"""
        results = []
        
        for voice_content, content_id in content_list:
            try:
                result = await self.classify_content(voice_content, content_id, method)
                results.append(result)
            except Exception as e:
                self.logger.error(f"Batch classification failed for {content_id}: {str(e)}")
                results.append(ClassificationResult(
                    success=False,
                    error_message=str(e)
                ))
        
        return results
    
    def get_classification_summary(self, classification: VoiceContentClassification) -> Dict[str, Any]:
        """Get summary of classification results"""
        return {
            "content_id": classification.content_id,
            "primary_category": classification.primary_category.value,
            "genre": classification.genre.value,
            "creator_type": classification.creator_type.value,
            "voice_content_type": classification.voice_content_type.value,
            "audio_quality": classification.audio_quality.value,
            "speech_pattern": classification.speech_pattern.value,
            "overall_confidence": classification.confidence.overall_confidence,
            "processing_time": classification.processing_time,
            "alternatives_count": len(classification.alternative_categories),
            "method_used": classification.classification_method.value
        }


# Export classes and enums
__all__ = [
    'VoiceContentClassifier',
    'ClassificationMethod',
    'ContentGenre',
    'AudioQuality',
    'SpeechPattern',
    'VoiceContentClassification',
    'ClassificationConfidence',
    'ClassificationResult'
]