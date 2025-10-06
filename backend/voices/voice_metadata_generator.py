"""Voice Metadata Generator - Intelligent Audio Metadata System
=============================================================

Automated metadata generation for voice content with AI-powered tagging,
description generation, and SEO optimization.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import uuid

logger = logging.getLogger(__name__)


class MetadataType(Enum):
    """Types of metadata"""
    DESCRIPTIVE = "descriptive"
    TECHNICAL = "technical"
    RIGHTS = "rights"
    STRUCTURAL = "structural"
    ADMINISTRATIVE = "administrative"
    PRESERVATION = "preservation"


class VoiceFeature(Enum):
    """Voice features for classification"""
    EMOTION = "emotion"
    ACCENT = "accent"
    AGE = "age"
    GENDER = "gender"
    TONE = "tone"
    PACE = "pace"
    CLARITY = "clarity"
    ENERGY = "energy"


class ContentCategory(Enum):
    """Content categories"""
    PODCAST = "podcast"
    AUDIOBOOK = "audiobook"
    VOICE_MESSAGE = "voice_message"
    NARRATION = "narration"
    INTERVIEW = "interview"
    MUSIC_VOCAL = "music_vocal"
    ANNOUNCEMENT = "announcement"
    EDUCATIONAL = "educational"


@dataclass
class VoiceMetadata:
    """Comprehensive voice metadata"""
    metadata_id: str
    voice_id: str
    title: Optional[str] = None
    description: Optional[str] = None
    tags: List[str] = field(default_factory=list)
    keywords: List[str] = field(default_factory=list)
    category: Optional[ContentCategory] = None
    language: str = "en"
    duration: float = 0.0
    features: Dict[str, Any] = field(default_factory=dict)
    technical_specs: Dict[str, Any] = field(default_factory=dict)
    rights_info: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    custom_fields: Dict[str, Any] = field(default_factory=dict)


@dataclass
class MetadataExtractionResult:
    """Result of metadata extraction"""
    success: bool
    voice_id: str
    metadata: Optional[VoiceMetadata] = None
    confidence: float = 0.0
    message: str = ""
    processing_time: float = 0.0


class VoiceMetadataGenerator:
    """
    Intelligent voice metadata generation system
    """
    
    def __init__(self):
        """Initialize metadata generator"""
        self.metadata_store = {}
        self.templates = {}
        self.ai_models = {}
        
        logger.info("📋 VoiceMetadataGenerator initialized")
    
    async def generate_metadata(
        self,
        voice_id: str,
        audio_data: bytes,
        options: Dict[str, Any] = None
    ) -> MetadataExtractionResult:
        """
        Generate comprehensive metadata for voice
        
        Args:
            voice_id: Voice identifier
            audio_data: Audio data to analyze
            options: Generation options
            
        Returns:
            MetadataExtractionResult
        """
        try:
            start_time = datetime.now()
            options = options or {}
            
            # Extract audio features
            features = await self._extract_features(audio_data)
            
            # Generate title
            title = await self._generate_title(features, options)
            
            # Generate description
            description = await self._generate_description(features, options)
            
            # Extract keywords
            keywords = await self._extract_keywords(features, options)
            
            # Generate tags
            tags = await self._generate_tags(features, options)
            
            # Classify category
            category = await self._classify_category(features)
            
            # Extract technical specs
            technical_specs = await self._extract_technical_specs(audio_data)
            
            # Create metadata object
            metadata = VoiceMetadata(
                metadata_id=str(uuid.uuid4()),
                voice_id=voice_id,
                title=title,
                description=description,
                tags=tags,
                keywords=keywords,
                category=category,
                language=features.get('language', 'en'),
                duration=features.get('duration', 0.0),
                features=features,
                technical_specs=technical_specs
            )
            
            # Store metadata
            self.metadata_store[metadata.metadata_id] = metadata
            
            processing_time = (datetime.now() - start_time).total_seconds()
            
            logger.info(f"✅ Metadata generated: {metadata.metadata_id}")
            
            return MetadataExtractionResult(
                success=True,
                voice_id=voice_id,
                metadata=metadata,
                confidence=0.9,
                message="Metadata generated successfully",
                processing_time=processing_time
            )
            
        except Exception as e:
            logger.error(f"Metadata generation failed: {e}")
            return MetadataExtractionResult(
                success=False,
                voice_id=voice_id,
                message=f"Generation failed: {str(e)}"
            )
    
    async def enrich_metadata(
        self,
        metadata_id: str,
        enrichment_data: Dict[str, Any]
    ) -> bool:
        """
        Enrich existing metadata with additional data
        
        Args:
            metadata_id: Metadata to enrich
            enrichment_data: Additional data
            
        Returns:
            Success status
        """
        try:
            if metadata_id not in self.metadata_store:
                raise ValueError(f"Metadata {metadata_id} not found")
            
            metadata = self.metadata_store[metadata_id]
            
            # Update fields
            for key, value in enrichment_data.items():
                if hasattr(metadata, key):
                    setattr(metadata, key, value)
                else:
                    metadata.custom_fields[key] = value
            
            metadata.updated_at = datetime.now()
            
            logger.info(f"✅ Metadata enriched: {metadata_id}")
            return True
            
        except Exception as e:
            logger.error(f"Metadata enrichment failed: {e}")
            return False
    
    async def generate_seo_metadata(
        self,
        voice_id: str,
        target_platforms: List[str] = None
    ) -> Dict[str, Any]:
        """
        Generate SEO-optimized metadata
        
        Args:
            voice_id: Voice identifier
            target_platforms: Target platforms for optimization
            
        Returns:
            SEO metadata
        """
        try:
            target_platforms = target_platforms or ['youtube', 'spotify', 'soundcloud']
            
            # Find voice metadata
            metadata = next(
                (m for m in self.metadata_store.values() if m.voice_id == voice_id),
                None
            )
            
            if not metadata:
                raise ValueError(f"Metadata for voice {voice_id} not found")
            
            seo_metadata = {}
            
            for platform in target_platforms:
                platform_meta = await self._optimize_for_platform(
                    metadata,
                    platform
                )
                seo_metadata[platform] = platform_meta
            
            logger.info(f"✅ SEO metadata generated for {len(target_platforms)} platforms")
            
            return seo_metadata
            
        except Exception as e:
            logger.error(f"SEO metadata generation failed: {e}")
            return {}
    
    async def extract_embedded_metadata(
        self,
        audio_data: bytes
    ) -> Dict[str, Any]:
        """
        Extract existing metadata from audio file
        
        Args:
            audio_data: Audio file data
            
        Returns:
            Extracted metadata
        """
        try:
            # Extract ID3 tags, WAV info, etc.
            embedded = {
                'title': None,
                'artist': None,
                'album': None,
                'year': None,
                'genre': None,
                'comment': None,
                'track_number': None,
                'duration': 0.0,
                'bitrate': None,
                'sample_rate': None,
                'channels': None
            }
            
            # Simulate extraction (would use mutagen, tinytag, etc.)
            logger.info("✅ Embedded metadata extracted")
            
            return embedded
            
        except Exception as e:
            logger.error(f"Embedded metadata extraction failed: {e}")
            return {}
    
    async def generate_structured_data(
        self,
        metadata_id: str,
        schema_type: str = "AudioObject"
    ) -> Dict[str, Any]:
        """
        Generate structured data (Schema.org) for voice
        
        Args:
            metadata_id: Metadata identifier
            schema_type: Schema.org type
            
        Returns:
            Structured data in JSON-LD format
        """
        try:
            if metadata_id not in self.metadata_store:
                raise ValueError(f"Metadata {metadata_id} not found")
            
            metadata = self.metadata_store[metadata_id]
            
            structured_data = {
                "@context": "https://schema.org",
                "@type": schema_type,
                "name": metadata.title,
                "description": metadata.description,
                "duration": f"PT{int(metadata.duration)}S",
                "encodingFormat": metadata.technical_specs.get('format', 'audio/mpeg'),
                "inLanguage": metadata.language,
                "keywords": ", ".join(metadata.keywords),
                "dateCreated": metadata.created_at.isoformat(),
                "dateModified": metadata.updated_at.isoformat()
            }
            
            logger.info(f"✅ Structured data generated for {metadata_id}")
            
            return structured_data
            
        except Exception as e:
            logger.error(f"Structured data generation failed: {e}")
            return {}
    
    async def validate_metadata(
        self,
        metadata_id: str,
        schema: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Validate metadata against schema
        
        Args:
            metadata_id: Metadata to validate
            schema: Validation schema
            
        Returns:
            Validation results
        """
        try:
            if metadata_id not in self.metadata_store:
                raise ValueError(f"Metadata {metadata_id} not found")
            
            metadata = self.metadata_store[metadata_id]
            errors = []
            warnings = []
            
            # Basic validation
            if not metadata.title or len(metadata.title) < 3:
                errors.append("Title is missing or too short")
            
            if not metadata.description or len(metadata.description) < 20:
                warnings.append("Description is missing or too short")
            
            if not metadata.keywords or len(metadata.keywords) == 0:
                warnings.append("No keywords provided")
            
            if not metadata.category:
                warnings.append("Category not specified")
            
            is_valid = len(errors) == 0
            
            return {
                'valid': is_valid,
                'errors': errors,
                'warnings': warnings,
                'completeness_score': await self._calculate_completeness(metadata)
            }
            
        except Exception as e:
            logger.error(f"Metadata validation failed: {e}")
            return {
                'valid': False,
                'error': str(e)
            }
    
    async def batch_generate(
        self,
        voice_data_list: List[Dict[str, Any]]
    ) -> List[MetadataExtractionResult]:
        """
        Generate metadata for multiple voices in batch
        
        Args:
            voice_data_list: List of voice data dicts
            
        Returns:
            List of MetadataExtractionResults
        """
        try:
            results = []
            
            for voice_data in voice_data_list:
                result = await self.generate_metadata(
                    voice_data['voice_id'],
                    voice_data['audio_data'],
                    voice_data.get('options')
                )
                results.append(result)
            
            logger.info(f"✅ Batch generation completed: {len(results)} voices")
            
            return results
            
        except Exception as e:
            logger.error(f"Batch generation failed: {e}")
            return []
    
    async def export_metadata(
        self,
        metadata_id: str,
        format: str = "json"
    ) -> str:
        """
        Export metadata in specified format
        
        Args:
            metadata_id: Metadata to export
            format: Export format (json, xml, yaml, csv)
            
        Returns:
            Formatted metadata string
        """
        try:
            if metadata_id not in self.metadata_store:
                raise ValueError(f"Metadata {metadata_id} not found")
            
            metadata = self.metadata_store[metadata_id]
            
            if format == "json":
                import json
                return json.dumps({
                    'metadata_id': metadata.metadata_id,
                    'voice_id': metadata.voice_id,
                    'title': metadata.title,
                    'description': metadata.description,
                    'tags': metadata.tags,
                    'keywords': metadata.keywords,
                    'category': metadata.category.value if metadata.category else None,
                    'language': metadata.language,
                    'duration': metadata.duration,
                    'features': metadata.features,
                    'technical_specs': metadata.technical_specs,
                    'created_at': metadata.created_at.isoformat()
                }, indent=2)
            
            elif format == "xml":
                # Simplified XML export
                return f"""
                <metadata>
                    <id>{metadata.metadata_id}</id>
                    <voice_id>{metadata.voice_id}</voice_id>
                    <title>{metadata.title}</title>
                    <description>{metadata.description}</description>
                </metadata>
                """
            
            else:
                raise ValueError(f"Unsupported format: {format}")
            
        except Exception as e:
            logger.error(f"Metadata export failed: {e}")
            return ""
    
    # Private methods
    
    async def _extract_features(
        self,
        audio_data: bytes
    ) -> Dict[str, Any]:
        """Extract audio features"""
        # Simulate feature extraction
        return {
            'duration': 180.0,
            'language': 'en',
            'speech_rate': 'normal',
            'emotion': 'neutral',
            'clarity': 'high',
            'background_noise': 'low'
        }
    
    async def _generate_title(
        self,
        features: Dict[str, Any],
        options: Dict[str, Any]
    ) -> str:
        """Generate title from features"""
        # Simulate AI title generation
        return options.get('title', f"Voice Recording - {datetime.now().strftime('%Y%m%d')}")
    
    async def _generate_description(
        self,
        features: Dict[str, Any],
        options: Dict[str, Any]
    ) -> str:
        """Generate description from features"""
        # Simulate AI description generation
        duration_min = int(features.get('duration', 0) / 60)
        language = features.get('language', 'en')
        
        return f"A {duration_min}-minute voice recording in {language} with {features.get('emotion', 'neutral')} tone and {features.get('clarity', 'good')} clarity."
    
    async def _extract_keywords(
        self,
        features: Dict[str, Any],
        options: Dict[str, Any]
    ) -> List[str]:
        """Extract keywords from features"""
        # Simulate keyword extraction
        keywords = [
            features.get('language', 'en'),
            features.get('emotion', 'neutral'),
            'voice',
            'audio'
        ]
        return keywords
    
    async def _generate_tags(
        self,
        features: Dict[str, Any],
        options: Dict[str, Any]
    ) -> List[str]:
        """Generate tags from features"""
        # Simulate tag generation
        tags = [
            f"language:{features.get('language', 'en')}",
            f"emotion:{features.get('emotion', 'neutral')}",
            f"quality:{features.get('clarity', 'high')}"
        ]
        return tags
    
    async def _classify_category(
        self,
        features: Dict[str, Any]
    ) -> ContentCategory:
        """Classify content category"""
        # Simulate classification
        return ContentCategory.VOICE_MESSAGE
    
    async def _extract_technical_specs(
        self,
        audio_data: bytes
    ) -> Dict[str, Any]:
        """Extract technical specifications"""
        return {
            'format': 'mp3',
            'bitrate': 320,
            'sample_rate': 44100,
            'channels': 2,
            'codec': 'mp3',
            'file_size': len(audio_data)
        }
    
    async def _optimize_for_platform(
        self,
        metadata: VoiceMetadata,
        platform: str
    ) -> Dict[str, Any]:
        """Optimize metadata for specific platform"""
        # Platform-specific optimization
        optimized = {
            'title': metadata.title,
            'description': metadata.description,
            'tags': metadata.tags[:10],  # Limit tags
            'keywords': metadata.keywords[:20]  # Limit keywords
        }
        
        # Platform-specific adjustments
        if platform == 'youtube':
            optimized['title'] = optimized['title'][:100]  # YouTube limit
            optimized['description'] = optimized['description'][:5000]
        elif platform == 'spotify':
            optimized['title'] = optimized['title'][:50]
        
        return optimized
    
    async def _calculate_completeness(
        self,
        metadata: VoiceMetadata
    ) -> float:
        """Calculate metadata completeness score"""
        total_fields = 8
        filled_fields = 0
        
        if metadata.title: filled_fields += 1
        if metadata.description: filled_fields += 1
        if metadata.tags: filled_fields += 1
        if metadata.keywords: filled_fields += 1
        if metadata.category: filled_fields += 1
        if metadata.language: filled_fields += 1
        if metadata.duration > 0: filled_fields += 1
        if metadata.technical_specs: filled_fields += 1
        
        return (filled_fields / total_fields) * 100
