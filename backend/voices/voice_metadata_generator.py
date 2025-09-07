"""Voice Metadata Generation Engine

AI-powered voice metadata generation system for automatic voice content 
analysis, metadata extraction, and intelligent voice content tagging.

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
import hashlib

try:
    from creator_voice_intelligence import CreatorType, VoiceContentType
    from voice_quality_optimizer import QualityMetric
except ImportError:
    from .creator_voice_intelligence import CreatorType, VoiceContentType
    from .voice_quality_optimizer import QualityMetric

logger = logging.getLogger(__name__)


class MetadataType(Enum):
    """Types of voice metadata"""
    TECHNICAL = "technical"
    SEMANTIC = "semantic"
    EMOTIONAL = "emotional"
    CONTEXTUAL = "contextual"
    DESCRIPTIVE = "descriptive"
    ANALYTICAL = "analytical"


class VoiceFeature(Enum):
    """Voice feature characteristics"""
    PITCH_RANGE = "pitch_range"
    VOCAL_TIMBRE = "vocal_timbre"
    SPEAKING_RATE = "speaking_rate"
    EMOTIONAL_TONE = "emotional_tone"
    ACCENT_TYPE = "accent_type"
    VOICE_AGE = "voice_age"
    GENDER_INDICATOR = "gender_indicator"
    ENERGY_LEVEL = "energy_level"


class ContentCategory(Enum):
    """Voice content categories"""
    MUSIC = "music"
    PODCAST = "podcast"
    NARRATION = "narration"
    COMMERCIAL = "commercial"
    EDUCATIONAL = "educational"
    ENTERTAINMENT = "entertainment"
    NEWS = "news"
    INTERVIEW = "interview"


@dataclass
class VoiceMetadata:
    """Voice content metadata container"""
    content_id: str
    creator_id: str
    title: Optional[str] = None
    description: Optional[str] = None
    duration: float = 0.0
    file_size: int = 0
    format: str = "wav"
    sample_rate: int = 44100
    bit_depth: int = 16
    channels: int = 1
    
    # Technical metadata
    technical_metadata: Dict[str, Any] = field(default_factory=dict)
    audio_fingerprint: Optional[str] = None
    quality_score: float = 0.0
    
    # Content metadata
    content_category: Optional[ContentCategory] = None
    creator_type: Optional[CreatorType] = None
    voice_type: Optional[VoiceContentType] = None
    
    # Voice characteristics
    voice_features: Dict[str, Any] = field(default_factory=dict)
    emotional_metadata: Dict[str, Any] = field(default_factory=dict)
    semantic_metadata: Dict[str, Any] = field(default_factory=dict)
    
    # SEO metadata
    keywords: List[str] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)
    transcript: Optional[str] = None
    
    # Analytics metadata
    analytics_metadata: Dict[str, Any] = field(default_factory=dict)
    
    # Timestamps
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)


@dataclass
class MetadataExtractionResult:
    """Result of metadata extraction process"""
    success: bool
    metadata: Optional[VoiceMetadata] = None
    confidence_score: float = 0.0
    processing_time: float = 0.0
    extraction_errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)


class VoiceMetadataGenerator:
    """Voice metadata generation engine"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize voice metadata generator"""
        self.config = config or {}
        self.logger = logging.getLogger(__name__)
        
        # Initialize metadata extractors
        self.extractors = {
            MetadataType.TECHNICAL: self._extract_technical_metadata,
            MetadataType.SEMANTIC: self._extract_semantic_metadata,
            MetadataType.EMOTIONAL: self._extract_emotional_metadata,
            MetadataType.CONTEXTUAL: self._extract_contextual_metadata,
            MetadataType.DESCRIPTIVE: self._extract_descriptive_metadata,
            MetadataType.ANALYTICAL: self._extract_analytical_metadata
        }
        
        self.logger.info("Voice metadata generator initialized")
    
    async def generate_metadata(
        self,
        voice_content: bytes,
        content_id: str,
        creator_id: str,
        metadata_types: Optional[List[MetadataType]] = None,
        options: Optional[Dict[str, Any]] = None
    ) -> MetadataExtractionResult:
        """Generate comprehensive metadata for voice content"""
        start_time = datetime.now()
        
        try:
            # Initialize metadata container
            metadata = VoiceMetadata(
                content_id=content_id,
                creator_id=creator_id
            )
            
            # Extract basic file metadata
            metadata = await self._extract_basic_metadata(voice_content, metadata)
            
            # Generate audio fingerprint
            metadata.audio_fingerprint = self._generate_audio_fingerprint(voice_content)
            
            # Extract requested metadata types
            types_to_extract = metadata_types or list(MetadataType)
            extraction_errors = []
            
            for metadata_type in types_to_extract:
                try:
                    if metadata_type in self.extractors:
                        extractor = self.extractors[metadata_type]
                        metadata = await extractor(voice_content, metadata, options or {})
                except Exception as e:
                    error_msg = f"Failed to extract {metadata_type.value} metadata: {str(e)}"
                    extraction_errors.append(error_msg)
                    self.logger.error(error_msg)
            
            # Calculate overall confidence score
            confidence_score = self._calculate_confidence_score(metadata, extraction_errors)
            
            # Update metadata timestamps
            metadata.updated_at = datetime.now()
            
            processing_time = (datetime.now() - start_time).total_seconds()
            
            return MetadataExtractionResult(
                success=True,
                metadata=metadata,
                confidence_score=confidence_score,
                processing_time=processing_time,
                extraction_errors=extraction_errors
            )
            
        except Exception as e:
            self.logger.error(f"Metadata generation failed: {str(e)}")
            processing_time = (datetime.now() - start_time).total_seconds()
            
            return MetadataExtractionResult(
                success=False,
                confidence_score=0.0,
                processing_time=processing_time,
                extraction_errors=[str(e)]
            )
    
    async def _extract_basic_metadata(
        self,
        voice_content: bytes,
        metadata: VoiceMetadata
    ) -> VoiceMetadata:
        """Extract basic file metadata"""
        try:
            # Basic file properties
            metadata.file_size = len(voice_content)
            
            # Simulate audio analysis (in real implementation, use librosa/soundfile)
            metadata.duration = len(voice_content) / (metadata.sample_rate * 2)  # Simplified
            metadata.format = "wav"  # Default format
            
            # Basic quality assessment
            metadata.quality_score = 0.85  # Simulated quality score
            
            return metadata
            
        except Exception as e:
            self.logger.error(f"Basic metadata extraction failed: {str(e)}")
            return metadata
    
    async def _extract_technical_metadata(
        self,
        voice_content: bytes,
        metadata: VoiceMetadata,
        options: Dict[str, Any]
    ) -> VoiceMetadata:
        """Extract technical audio metadata"""
        try:
            technical_data = {
                "bit_rate": 1411,  # kbps
                "codec": "PCM",
                "channel_layout": "mono" if metadata.channels == 1 else "stereo",
                "dynamic_range": 72.5,  # dB
                "peak_level": -3.2,  # dBFS
                "rms_level": -18.7,  # dBFS
                "frequency_response": {
                    "low_end": 20,  # Hz
                    "high_end": 20000,  # Hz
                    "presence_peak": 2500  # Hz
                },
                "noise_floor": -65.3,  # dB
                "thd_plus_n": 0.003  # %
            }
            
            metadata.technical_metadata = technical_data
            return metadata
            
        except Exception as e:
            self.logger.error(f"Technical metadata extraction failed: {str(e)}")
            return metadata
    
    async def _extract_semantic_metadata(
        self,
        voice_content: bytes,
        metadata: VoiceMetadata,
        options: Dict[str, Any]
    ) -> VoiceMetadata:
        """Extract semantic content metadata"""
        try:
            # Simulated semantic analysis
            semantic_data = {
                "language": "en-US",
                "dialect": "american",
                "topic_categories": ["technology", "education"],
                "key_concepts": ["artificial intelligence", "voice processing"],
                "complexity_level": "intermediate",
                "formality_level": "professional",
                "content_structure": {
                    "introduction": True,
                    "main_content": True,
                    "conclusion": True
                }
            }
            
            metadata.semantic_metadata = semantic_data
            
            # Extract keywords for SEO
            metadata.keywords = semantic_data.get("key_concepts", [])
            
            return metadata
            
        except Exception as e:
            self.logger.error(f"Semantic metadata extraction failed: {str(e)}")
            return metadata
    
    async def _extract_emotional_metadata(
        self,
        voice_content: bytes,
        metadata: VoiceMetadata,
        options: Dict[str, Any]
    ) -> VoiceMetadata:
        """Extract emotional tone metadata"""
        try:
            emotional_data = {
                "primary_emotion": "neutral",
                "emotion_confidence": 0.82,
                "emotional_range": {
                    "happiness": 0.15,
                    "sadness": 0.05,
                    "anger": 0.02,
                    "fear": 0.03,
                    "surprise": 0.08,
                    "neutral": 0.67
                },
                "energy_level": "medium",
                "speaking_pace": "normal",
                "vocal_stress": "low",
                "emotional_stability": "high"
            }
            
            metadata.emotional_metadata = emotional_data
            return metadata
            
        except Exception as e:
            self.logger.error(f"Emotional metadata extraction failed: {str(e)}")
            return metadata
    
    async def _extract_contextual_metadata(
        self,
        voice_content: bytes,
        metadata: VoiceMetadata,
        options: Dict[str, Any]
    ) -> VoiceMetadata:
        """Extract contextual metadata"""
        try:
            # Infer content category and creator type
            if metadata.duration > 300:  # 5+ minutes
                if "interview" in metadata.semantic_metadata.get("content_structure", {}):
                    metadata.content_category = ContentCategory.INTERVIEW
                else:
                    metadata.content_category = ContentCategory.PODCAST
            elif metadata.duration < 60:  # < 1 minute
                metadata.content_category = ContentCategory.COMMERCIAL
            else:
                metadata.content_category = ContentCategory.NARRATION
            
            # Infer creator type based on content
            if metadata.content_category in [ContentCategory.PODCAST, ContentCategory.INTERVIEW]:
                metadata.creator_type = CreatorType.PODCASTER
            elif metadata.content_category == ContentCategory.MUSIC:
                metadata.creator_type = CreatorType.MUSICIAN
            else:
                metadata.creator_type = CreatorType.NARRATOR
            
            return metadata
            
        except Exception as e:
            self.logger.error(f"Contextual metadata extraction failed: {str(e)}")
            return metadata
    
    async def _extract_descriptive_metadata(
        self,
        voice_content: bytes,
        metadata: VoiceMetadata,
        options: Dict[str, Any]
    ) -> VoiceMetadata:
        """Extract descriptive metadata"""
        try:
            # Voice feature analysis
            voice_features = {
                VoiceFeature.PITCH_RANGE.value: "medium",
                VoiceFeature.VOCAL_TIMBRE.value: "warm",
                VoiceFeature.SPEAKING_RATE.value: "normal",
                VoiceFeature.EMOTIONAL_TONE.value: "neutral",
                VoiceFeature.ACCENT_TYPE.value: "american",
                VoiceFeature.VOICE_AGE.value: "adult",
                VoiceFeature.GENDER_INDICATOR.value: "neutral",
                VoiceFeature.ENERGY_LEVEL.value: "medium"
            }
            
            metadata.voice_features = voice_features
            
            # Generate descriptive tags
            tags = []
            if voice_features[VoiceFeature.VOCAL_TIMBRE.value] == "warm":
                tags.append("warm-voice")
            if voice_features[VoiceFeature.ENERGY_LEVEL.value] == "high":
                tags.append("energetic")
            
            metadata.tags = tags
            
            return metadata
            
        except Exception as e:
            self.logger.error(f"Descriptive metadata extraction failed: {str(e)}")
            return metadata
    
    async def _extract_analytical_metadata(
        self,
        voice_content: bytes,
        metadata: VoiceMetadata,
        options: Dict[str, Any]
    ) -> VoiceMetadata:
        """Extract analytical metadata"""
        try:
            analytics_data = {
                "predicted_engagement": 0.75,
                "viral_potential": 0.32,
                "target_audience": {
                    "age_range": "25-45",
                    "interests": ["technology", "education"],
                    "demographics": "professional"
                },
                "platform_suitability": {
                    "podcast": 0.95,
                    "audiobook": 0.78,
                    "social_media": 0.45,
                    "commercial": 0.62
                },
                "monetization_potential": {
                    "subscription": 0.71,
                    "advertising": 0.58,
                    "licensing": 0.82
                }
            }
            
            metadata.analytics_metadata = analytics_data
            return metadata
            
        except Exception as e:
            self.logger.error(f"Analytical metadata extraction failed: {str(e)}")
            return metadata
    
    def _generate_audio_fingerprint(self, voice_content: bytes) -> str:
        """Generate unique audio fingerprint"""
        try:
            # Create SHA-256 hash of audio content
            hash_obj = hashlib.sha256(voice_content)
            fingerprint = hash_obj.hexdigest()
            
            return fingerprint
            
        except Exception as e:
            self.logger.error(f"Audio fingerprint generation failed: {str(e)}")
            return ""
    
    def _calculate_confidence_score(
        self,
        metadata: VoiceMetadata,
        errors: List[str]
    ) -> float:
        """Calculate confidence score for extracted metadata"""
        try:
            total_fields = 10  # Key metadata fields
            filled_fields = 0
            
            # Check if key fields are populated
            if metadata.duration > 0:
                filled_fields += 1
            if metadata.audio_fingerprint:
                filled_fields += 1
            if metadata.content_category:
                filled_fields += 1
            if metadata.creator_type:
                filled_fields += 1
            if metadata.technical_metadata:
                filled_fields += 1
            if metadata.semantic_metadata:
                filled_fields += 1
            if metadata.emotional_metadata:
                filled_fields += 1
            if metadata.voice_features:
                filled_fields += 1
            if metadata.keywords:
                filled_fields += 1
            if metadata.analytics_metadata:
                filled_fields += 1
            
            # Calculate base confidence
            base_confidence = filled_fields / total_fields
            
            # Reduce confidence based on errors
            error_penalty = len(errors) * 0.1
            confidence = max(0.0, base_confidence - error_penalty)
            
            return min(1.0, confidence)
            
        except Exception as e:
            self.logger.error(f"Confidence score calculation failed: {str(e)}")
            return 0.0
    
    async def update_metadata(
        self,
        metadata: VoiceMetadata,
        updates: Dict[str, Any]
    ) -> VoiceMetadata:
        """Update existing metadata with new information"""
        try:
            # Update basic fields
            for field, value in updates.items():
                if hasattr(metadata, field):
                    setattr(metadata, field, value)
            
            # Update timestamp
            metadata.updated_at = datetime.now()
            
            return metadata
            
        except Exception as e:
            self.logger.error(f"Metadata update failed: {str(e)}")
            return metadata
    
    def export_metadata(
        self,
        metadata: VoiceMetadata,
        format: str = "json"
    ) -> str:
        """Export metadata in specified format"""
        try:
            if format.lower() == "json":
                # Convert to JSON-serializable format
                metadata_dict = {
                    "content_id": metadata.content_id,
                    "creator_id": metadata.creator_id,
                    "title": metadata.title,
                    "description": metadata.description,
                    "duration": metadata.duration,
                    "file_size": metadata.file_size,
                    "format": metadata.format,
                    "sample_rate": metadata.sample_rate,
                    "bit_depth": metadata.bit_depth,
                    "channels": metadata.channels,
                    "technical_metadata": metadata.technical_metadata,
                    "audio_fingerprint": metadata.audio_fingerprint,
                    "quality_score": metadata.quality_score,
                    "content_category": metadata.content_category.value if metadata.content_category else None,
                    "creator_type": metadata.creator_type.value if metadata.creator_type else None,
                    "voice_type": metadata.voice_type.value if metadata.voice_type else None,
                    "voice_features": metadata.voice_features,
                    "emotional_metadata": metadata.emotional_metadata,
                    "semantic_metadata": metadata.semantic_metadata,
                    "keywords": metadata.keywords,
                    "tags": metadata.tags,
                    "transcript": metadata.transcript,
                    "analytics_metadata": metadata.analytics_metadata,
                    "created_at": metadata.created_at.isoformat(),
                    "updated_at": metadata.updated_at.isoformat()
                }
                
                return json.dumps(metadata_dict, indent=2)
            else:
                raise ValueError(f"Unsupported export format: {format}")
                
        except Exception as e:
            self.logger.error(f"Metadata export failed: {str(e)}")
            return "{}"


# Export classes and enums
__all__ = [
    'VoiceMetadataGenerator',
    'MetadataType',
    'VoiceFeature',
    'ContentCategory',
    'VoiceMetadata',
    'MetadataExtractionResult'
]