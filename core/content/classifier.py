"""Content Classifier - AI-Powered Content Classification Engine
=============================================================

The ContentClassifier automatically categorizes and tags content using
advanced machine learning models for improved organization and discovery.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Union, Tuple
from datetime import datetime
from dataclasses import dataclass
import uuid

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import Pipeline
import joblib
from sqlalchemy.ext.asyncio import AsyncSession

from ..ml.models.content_classifier_model import ContentClassifierModel
from ..ml.models.genre_classifier import GenreClassifier
from ..ml.models.mood_classifier import MoodClassifier
from ..ml.models.quality_classifier import QualityClassifier


@dataclass
class ClassificationResult:
    """
Content classification result container"""
    content_id: str
    primary_category: str
    subcategories: List[str]
    tags: List[str]
    confidence_scores: Dict[str, float]
    metadata_enhanced: Dict[str, Any]
    classification_time: float = 0.0


@dataclass
class ClassificationConfig:
    """
Content classification configuration"""
    enable_auto_tagging: bool = True
    enable_genre_detection: bool = True
    enable_mood_analysis: bool = True
    enable_quality_assessment: bool = True
    confidence_threshold: float = 0.7
    max_tags: int = 10
    max_categories: int = 5


class ContentClassifier:
    """
    AI-Powered Content Classification Engine
    
    Provides intelligent content classification including:
    - Automatic categorization into predefined taxonomies
    - Genre and style detection for media content
    - Mood and sentiment classification
    - Quality level assessment
    - Automated tagging and metadata enhancement
    - Content difficulty and audience targeting
    """
    
    def __init__(self, db_session: AsyncSession, config: ClassificationConfig = None):
        self.db = db_session
        self.config = config or ClassificationConfig()
        self.logger = logging.getLogger(__name__)
        
        # Initialize ML models
        self.content_classifier = ContentClassifierModel()
        self.genre_classifier = GenreClassifier()
        self.mood_classifier = MoodClassifier()
        self.quality_classifier = QualityClassifier()
        
        # Classification taxonomies
        self.taxonomies = self._load_classification_taxonomies()
        
        # Model performance cache
        self.classification_cache = {}

    async def classify_content(
        self,
        content_id: str,
        content_data: Dict[str, Any] = None,
        custom_config: ClassificationConfig = None
    ) -> Dict[str, Any]:
        """
        Classify content using AI models
        
        Args:
            content_id: Content identifier
            content_data: Optional content data to avoid database lookup
            custom_config: Custom classification configuration
            
        Returns:
            Classification result with categories, tags, and metadata
        """
        classification_start = datetime.utcnow()
        config = custom_config or self.config
        
        try:
            self.logger.info(f"Classifying content {content_id}")
            
            # Get content data
            if not content_data:
                content_data = await self._get_content_data(content_id)
                if not content_data:
                    return {
                        "success": False,
                        "error": "Content not found",
                        "content_id": content_id
                    }
            
            # Route to appropriate classifier based on content type
            content_type = content_data.get("content_type", "unknown")
            
            if content_type == "audio":
                result = await self._classify_audio(content_id, content_data, config)
            elif content_type == "video":
                result = await self._classify_video(content_id, content_data, config)
            elif content_type == "image":
                result = await self._classify_image(content_id, content_data, config)
            elif content_type == "text":
                result = await self._classify_text(content_id, content_data, config)
            else:
                result = await self._classify_generic(content_id, content_data, config)
            
            # Calculate classification time
            classification_time = (datetime.utcnow() - classification_start).total_seconds()
            result.classification_time = classification_time
            
            # Save classification result
            await self._save_classification_result(content_id, result)
            
            # Cache result
            self.classification_cache[content_id] = result
            
            self.logger.info(f"Content classification completed for {content_id} in {classification_time:.2f}s")
            
            return {
                "success": True,
                "content_id": content_id,
                "classification": self._serialize_classification_result(result),
                "classification_time": classification_time
            }
            
        except Exception as e:
            classification_time = (datetime.utcnow() - classification_start).total_seconds()
            error_msg = f"Content classification failed: {str(e)}"
            self.logger.error(error_msg)
            
            return {
                "success": False,
                "error": error_msg,
                "content_id": content_id,
                "classification_time": classification_time
            }

    async def _classify_audio(
        self,
        content_id: str,
        content_data: Dict[str, Any],
        config: ClassificationConfig
    ) -> ClassificationResult:
        """
        Classify audio content
        
        Args:
            content_id: Content identifier
            content_data: Content metadata and information
            config: Classification configuration
            
        Returns:
            Audio classification result
        """
        try:
            primary_category = "audio"
            subcategories = []
            tags = []
            confidence_scores = {}
            metadata_enhanced = content_data.get("metadata", {}).copy()
            
            # Genre classification
            if config.enable_genre_detection:
                genre_result = await self.genre_classifier.classify_audio_genre(
                    content_data.get("file_path", "")
                )
                
                if genre_result.get("confidence", 0) >= config.confidence_threshold:
                    subcategories.append(genre_result["genre"])
                    confidence_scores["genre"] = genre_result["confidence"]
                    metadata_enhanced["genre"] = genre_result["genre"]
                    
                    # Add genre-related tags
                    tags.extend(genre_result.get("related_tags", []))
            
            # Mood classification
            if config.enable_mood_analysis:
                mood_result = await self.mood_classifier.classify_audio_mood(
                    content_data.get("file_path", "")
                )
                
                if mood_result.get("confidence", 0) >= config.confidence_threshold:
                    subcategories.append(f"mood_{mood_result['mood']}")
                    confidence_scores["mood"] = mood_result["confidence"]
                    metadata_enhanced["mood"] = mood_result["mood"]
                    
                    # Add mood-related tags
                    tags.extend(mood_result.get("related_tags", []))
            
            # Quality assessment
            if config.enable_quality_assessment:
                quality_result = await self.quality_classifier.assess_audio_quality(
                    content_data.get("file_path", "")
                )
                
                quality_level = quality_result.get("quality_level", "standard")
                subcategories.append(f"quality_{quality_level}")
                confidence_scores["quality"] = quality_result.get("confidence", 0.0)
                metadata_enhanced["quality_level"] = quality_level
                metadata_enhanced["quality_metrics"] = quality_result.get("metrics", {})
            
            # Instrument detection
            instruments = await self._detect_audio_instruments(content_data.get("file_path", ""))
            if instruments:
                tags.extend([f"instrument_{inst}" for inst in instruments])
                metadata_enhanced["instruments"] = instruments
            
            # Tempo and energy classification
            audio_features = await self._extract_audio_features(content_data.get("file_path", ""))
            if audio_features:
                tempo_category = self._categorize_tempo(audio_features.get("tempo", 0))
                energy_category = self._categorize_energy(audio_features.get("energy", 0))
                
                subcategories.extend([f"tempo_{tempo_category}", f"energy_{energy_category}"])
                tags.extend([tempo_category, energy_category])
                metadata_enhanced.update(audio_features)
            
            # Auto-tagging from metadata
            if config.enable_auto_tagging:
                auto_tags = await self._generate_auto_tags(content_data, "audio")
                tags.extend(auto_tags)
            
            # Remove duplicates and limit tags
            tags = list(set(tags))[:config.max_tags]
            subcategories = list(set(subcategories))[:config.max_categories]
            
            return ClassificationResult(
                content_id=content_id,
                primary_category=primary_category,
                subcategories=subcategories,
                tags=tags,
                confidence_scores=confidence_scores,
                metadata_enhanced=metadata_enhanced
            )
            
        except Exception as e:
            raise Exception(f"Audio classification failed: {str(e)}")

    async def _classify_video(
        self,
        content_id: str,
        content_data: Dict[str, Any],
        config: ClassificationConfig
    ) -> ClassificationResult:
        """
        Classify video content
        
        Args:
            content_id: Content identifier
            content_data: Content metadata and information
            config: Classification configuration
            
        Returns:
            Video classification result
        """
        try:
            primary_category = "video"
            subcategories = []
            tags = []
            confidence_scores = {}
            metadata_enhanced = content_data.get("metadata", {}).copy()
            
            # Content type classification (tutorial, entertainment, etc.)
            content_type_result = await self.content_classifier.classify_video_type(
                content_data.get("file_path", "")
            )
            
            if content_type_result.get("confidence", 0) >= config.confidence_threshold:
                subcategories.append(content_type_result["type"])
                confidence_scores["content_type"] = content_type_result["confidence"]
                metadata_enhanced["video_type"] = content_type_result["type"]
            
            # Visual style classification
            style_result = await self._classify_video_style(content_data.get("file_path", ""))
            if style_result:
                subcategories.append(f"style_{style_result['style']}")
                confidence_scores["style"] = style_result.get("confidence", 0.0)
                metadata_enhanced["visual_style"] = style_result["style"]
            
            # Object and scene detection
            objects_detected = await self._detect_video_objects(content_data.get("file_path", ""))
            if objects_detected:
                tags.extend([f"object_{obj}" for obj in objects_detected[:5]])  # Limit to top 5
                metadata_enhanced["objects_detected"] = objects_detected
            
            # Quality assessment
            if config.enable_quality_assessment:
                quality_result = await self.quality_classifier.assess_video_quality(
                    content_data.get("file_path", "")
                )
                
                quality_level = quality_result.get("quality_level", "standard")
                subcategories.append(f"quality_{quality_level}")
                confidence_scores["quality"] = quality_result.get("confidence", 0.0)
                metadata_enhanced["quality_level"] = quality_level
            
            # Duration-based classification
            duration = metadata_enhanced.get("duration", 0)
            duration_category = self._categorize_video_duration(duration)
            subcategories.append(f"duration_{duration_category}")
            tags.append(duration_category)
            
            # Resolution-based classification
            resolution = metadata_enhanced.get("resolution", "")
            if resolution:
                resolution_category = self._categorize_video_resolution(resolution)
                subcategories.append(f"resolution_{resolution_category}")
                tags.append(resolution_category)
            
            # Auto-tagging
            if config.enable_auto_tagging:
                auto_tags = await self._generate_auto_tags(content_data, "video")
                tags.extend(auto_tags)
            
            # Remove duplicates and limit
            tags = list(set(tags))[:config.max_tags]
            subcategories = list(set(subcategories))[:config.max_categories]
            
            return ClassificationResult(
                content_id=content_id,
                primary_category=primary_category,
                subcategories=subcategories,
                tags=tags,
                confidence_scores=confidence_scores,
                metadata_enhanced=metadata_enhanced
            )
            
        except Exception as e:
            raise Exception(f"Video classification failed: {str(e)}")

    async def _classify_image(
        self,
        content_id: str,
        content_data: Dict[str, Any],
        config: ClassificationConfig
    ) -> ClassificationResult:
        """
        Classify image content
        
        Args:
            content_id: Content identifier
            content_data: Content metadata and information
            config: Classification configuration
            
        Returns:
            Image classification result
        """
        try:
            primary_category = "image"
            subcategories = []
            tags = []
            confidence_scores = {}
            metadata_enhanced = content_data.get("metadata", {}).copy()
            
            # Image category classification (photo, artwork, diagram, etc.)
            category_result = await self.content_classifier.classify_image_category(
                content_data.get("file_path", "")
            )
            
            if category_result.get("confidence", 0) >= config.confidence_threshold:
                subcategories.append(category_result["category"])
                confidence_scores["category"] = category_result["confidence"]
                metadata_enhanced["image_category"] = category_result["category"]
            
            # Style classification (realistic, artistic, abstract, etc.)
            style_result = await self._classify_image_style(content_data.get("file_path", ""))
            if style_result:
                subcategories.append(f"style_{style_result['style']}")
                confidence_scores["style"] = style_result.get("confidence", 0.0)
                metadata_enhanced["artistic_style"] = style_result["style"]
            
            # Object detection and tagging
            objects_detected = await self._detect_image_objects(content_data.get("file_path", ""))
            if objects_detected:
                tags.extend([obj["name"] for obj in objects_detected[:8]])  # Top 8 objects
                metadata_enhanced["objects_detected"] = objects_detected
            
            # Color analysis
            color_analysis = await self._analyze_image_colors(content_data.get("file_path", ""))
            if color_analysis:
                dominant_colors = color_analysis.get("dominant_colors", [])
                tags.extend([f"color_{color}" for color in dominant_colors[:3]])
                metadata_enhanced["color_analysis"] = color_analysis
            
            # Quality assessment
            if config.enable_quality_assessment:
                quality_result = await self.quality_classifier.assess_image_quality(
                    content_data.get("file_path", "")
                )
                
                quality_level = quality_result.get("quality_level", "standard")
                subcategories.append(f"quality_{quality_level}")
                confidence_scores["quality"] = quality_result.get("confidence", 0.0)
                metadata_enhanced["quality_level"] = quality_level
            
            # Resolution and format classification
            dimensions = metadata_enhanced.get("dimensions", {})
            if dimensions:
                resolution_category = self._categorize_image_resolution(
                    dimensions.get("width", 0), dimensions.get("height", 0)
                )
                subcategories.append(f"resolution_{resolution_category}")
                tags.append(resolution_category)
            
            # Face detection
            faces_detected = await self._detect_faces_in_image(content_data.get("file_path", ""))
            if faces_detected > 0:
                subcategories.append("contains_faces")
                tags.append("portrait" if faces_detected == 1 else "group_photo")
                metadata_enhanced["faces_count"] = faces_detected
            
            # Text detection (OCR)
            text_detected = await self._detect_text_in_image(content_data.get("file_path", ""))
            if text_detected:
                subcategories.append("contains_text")
                tags.append("text_overlay")
                metadata_enhanced["text_detected"] = text_detected
            
            # Auto-tagging
            if config.enable_auto_tagging:
                auto_tags = await self._generate_auto_tags(content_data, "image")
                tags.extend(auto_tags)
            
            # Remove duplicates and limit
            tags = list(set(tags))[:config.max_tags]
            subcategories = list(set(subcategories))[:config.max_categories]
            
            return ClassificationResult(
                content_id=content_id,
                primary_category=primary_category,
                subcategories=subcategories,
                tags=tags,
                confidence_scores=confidence_scores,
                metadata_enhanced=metadata_enhanced
            )
            
        except Exception as e:
            raise Exception(f"Image classification failed: {str(e)}")

    async def _classify_text(
        self,
        content_id: str,
        content_data: Dict[str, Any],
        config: ClassificationConfig
    ) -> ClassificationResult:
        """
        Classify text content
        
        Args:
            content_id: Content identifier
            content_data: Content metadata and information
            config: Classification configuration
            
        Returns:
            Text classification result
        """
        try:
            primary_category = "text"
            subcategories = []
            tags = []
            confidence_scores = {}
            metadata_enhanced = content_data.get("metadata", {}).copy()
            
            # Read text content
            text_content = await self._read_text_file(content_data.get("file_path", ""))
            
            # Document type classification
            doc_type_result = await self.content_classifier.classify_document_type(text_content)
            if doc_type_result.get("confidence", 0) >= config.confidence_threshold:
                subcategories.append(doc_type_result["type"])
                confidence_scores["document_type"] = doc_type_result["confidence"]
                metadata_enhanced["document_type"] = doc_type_result["type"]
            
            # Topic classification
            topic_result = await self._classify_text_topic(text_content)
            if topic_result:
                subcategories.append(f"topic_{topic_result['topic']}")
                confidence_scores["topic"] = topic_result.get("confidence", 0.0)
                metadata_enhanced["primary_topic"] = topic_result["topic"]
                
                # Add topic-related tags
                tags.extend(topic_result.get("related_keywords", []))
            
            # Language detection
            language_result = await self._detect_text_language(text_content)
            if language_result:
                subcategories.append(f"lang_{language_result['language']}")
                confidence_scores["language"] = language_result.get("confidence", 0.0)
                metadata_enhanced["language"] = language_result["language"]
            
            # Reading level assessment
            reading_level = await self._assess_reading_level(text_content)
            if reading_level:
                subcategories.append(f"level_{reading_level['level']}")
                metadata_enhanced["reading_level"] = reading_level["level"]
                metadata_enhanced["reading_metrics"] = reading_level.get("metrics", {})
            
            # Mood and sentiment classification
            if config.enable_mood_analysis:
                sentiment_result = await self.mood_classifier.classify_text_sentiment(text_content)
                if sentiment_result:
                    subcategories.append(f"sentiment_{sentiment_result['sentiment']}")
                    confidence_scores["sentiment"] = sentiment_result.get("confidence", 0.0)
                    metadata_enhanced["sentiment"] = sentiment_result["sentiment"]
                    metadata_enhanced["sentiment_scores"] = sentiment_result.get("scores", {})
            
            # Content length categorization
            word_count = len(text_content.split())
            length_category = self._categorize_text_length(word_count)
            subcategories.append(f"length_{length_category}")
            tags.append(length_category)
            
            # Extract key phrases and entities
            key_phrases = await self._extract_key_phrases(text_content)
            if key_phrases:
                tags.extend(key_phrases[:5])  # Top 5 key phrases
                metadata_enhanced["key_phrases"] = key_phrases
            
            # Named entity recognition
            entities = await self._extract_named_entities(text_content)
            if entities:
                entity_tags = [f"entity_{ent['type'].lower()}" for ent in entities[:3]]
                tags.extend(entity_tags)
                metadata_enhanced["named_entities"] = entities
            
            # Auto-tagging
            if config.enable_auto_tagging:
                auto_tags = await self._generate_auto_tags(content_data, "text")
                tags.extend(auto_tags)
            
            # Remove duplicates and limit
            tags = list(set(tags))[:config.max_tags]
            subcategories = list(set(subcategories))[:config.max_categories]
            
            return ClassificationResult(
                content_id=content_id,
                primary_category=primary_category,
                subcategories=subcategories,
                tags=tags,
                confidence_scores=confidence_scores,
                metadata_enhanced=metadata_enhanced
            )
            
        except Exception as e:
            raise Exception(f"Text classification failed: {str(e)}")

    async def _classify_generic(
        self,
        content_id: str,
        content_data: Dict[str, Any],
        config: ClassificationConfig
    ) -> ClassificationResult:
        """
        Generic classification for unknown content types
        
        Args:
            content_id: Content identifier
            content_data: Content metadata and information
            config: Classification configuration
            
        Returns:
            Generic classification result
        """
        try:
            content_type = content_data.get("content_type", "unknown")
            primary_category = content_type
            subcategories = []
            tags = []
            confidence_scores = {}
            metadata_enhanced = content_data.get("metadata", {}).copy()
            
            # Basic file type classification
            file_extension = content_data.get("file_path", "").split(".")[-1].lower()
            if file_extension:
                subcategories.append(f"format_{file_extension}")
                tags.append(file_extension)
            
            # Size-based classification
            file_size = metadata_enhanced.get("file_size", 0)
            size_category = self._categorize_file_size(file_size)
            subcategories.append(f"size_{size_category}")
            tags.append(size_category)
            
            # Auto-tagging from metadata
            if config.enable_auto_tagging:
                auto_tags = await self._generate_auto_tags(content_data, content_type)
                tags.extend(auto_tags)
            
            # Remove duplicates and limit
            tags = list(set(tags))[:config.max_tags]
            subcategories = list(set(subcategories))[:config.max_categories]
            
            return ClassificationResult(
                content_id=content_id,
                primary_category=primary_category,
                subcategories=subcategories,
                tags=tags,
                confidence_scores=confidence_scores,
                metadata_enhanced=metadata_enhanced
            )
            
        except Exception as e:
            raise Exception(f"Generic classification failed: {str(e)}")

    # Helper methods

    def _load_classification_taxonomies(self) -> Dict[str, Any]:
        """Load classification taxonomies and categories"""
        return {
            "audio": {
                "genres": ["rock", "pop", "jazz", "classical", "electronic", "hip-hop", "country", "blues"],
                "moods": ["happy", "sad", "energetic", "calm", "aggressive", "romantic", "mysterious"],
                "instruments": ["guitar", "piano", "drums", "violin", "saxophone", "bass", "vocals"]
            },
            "video": {
                "types": ["tutorial", "entertainment", "documentary", "music_video", "presentation", "vlog"],
                "styles": ["cinematic", "amateur", "professional", "artistic", "commercial"],
                "durations": ["short", "medium", "long", "feature_length"]
            },
            "image": {
                "categories": ["photo", "artwork", "diagram", "screenshot", "design", "meme"],
                "styles": ["realistic", "artistic", "abstract", "minimalist", "vintage", "modern"],
                "subjects": ["people", "nature", "architecture", "food", "technology", "animals"]
            },
            "text": {
                "types": ["article", "story", "poem", "technical", "academic", "legal", "creative"],
                "topics": ["technology", "science", "business", "health", "entertainment", "sports", "politics"],
                "levels": ["beginner", "intermediate", "advanced", "expert"]
            }
        }

    async def _get_content_data(self, content_id: str) -> Optional[Dict[str, Any]]:
        """Get content data from database"""
        # Mock implementation - replace with actual database query
        return {
            "id": content_id,
            "content_type": "text",
            "file_path": "/path/to/content",
            "metadata": {}
        }

    async def _save_classification_result(self, content_id: str, result: ClassificationResult) -> None:
        """Save classification result to database"""
        try:
            # This would save to the actual database
            pass
        except Exception as e:
            self.logger.error(f"Failed to save classification result: {str(e)}")

    def _serialize_classification_result(self, result: ClassificationResult) -> Dict[str, Any]:
        """Convert classification result to serializable format"""
        return {
            "content_id": result.content_id,
            "primary_category": result.primary_category,
            "subcategories": result.subcategories,
            "tags": result.tags,
            "confidence_scores": result.confidence_scores,
            "metadata_enhanced": result.metadata_enhanced,
            "classification_time": result.classification_time
        }

    # Placeholder methods for AI model calls
    async def _detect_audio_instruments(self, file_path: str) -> List[str]:
        """Detect instruments in audio content"""
        # Placeholder - implement with actual audio analysis
        return ["guitar", "drums"]

    async def _extract_audio_features(self, file_path: str) -> Dict[str, Any]:
        """Extract audio features like tempo, energy, etc."""
        # Placeholder - implement with librosa or similar
        return {"tempo": 120, "energy": 0.8}

    def _categorize_tempo(self, tempo: float) -> str:
        """Categorize tempo into descriptive labels"""
        if tempo < 60:
            return "very_slow"
        elif tempo < 90:
            return "slow"
        elif tempo < 120:
            return "moderate"
        elif tempo < 150:
            return "fast"
        else:
            return "very_fast"

    def _categorize_energy(self, energy: float) -> str:
        """Categorize energy level"""
        if energy < 0.3:
            return "low_energy"
        elif energy < 0.7:
            return "medium_energy"
        else:
            return "high_energy"

    async def _generate_auto_tags(self, content_data: Dict[str, Any], content_type: str) -> List[str]:
        """Generate automatic tags from content metadata"""
        tags = []
        
        # Add tags from existing metadata
        metadata = content_data.get("metadata", {})
        
        if "tags" in metadata:
            tags.extend(metadata["tags"])
        
        if "keywords" in metadata:
            tags.extend(metadata["keywords"])
        
        # Add content type as tag
        tags.append(content_type)
        
        # Add creation date tags
        created_at = content_data.get("created_at")
        if created_at:
            # Add year, month tags
            year = created_at.year if hasattr(created_at, 'year') else None
            if year:
                tags.append(f"year_{year}")
        
        return tags

    # Additional helper methods would be implemented for:
    # - Various classification and detection functions
    # - File analysis and feature extraction
    # - Category and tag generation
    # - Model inference and result processing
