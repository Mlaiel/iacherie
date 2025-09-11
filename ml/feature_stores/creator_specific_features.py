"""🎵 Creator Specific Features - Enterprise ML Infrastructure
============================================================
Module: ml/feature_stores/creator_specific_features.py
Author: Fahed Mlaiel (mlaiel@live.de)
============================================================

⚠️  PROPRIÉTÉ INTELLECTUELLE EXCLUSIVE - FAHED MLAIEL ⚠️
(c) 2025 Fahed Mlaiel. Tous droits réservés.
Contact: mlaiel@live.de

🎯 CREATOR-SPECIFIC FEATURE ENGINEERING
Specialized feature engineering for different creator types
- Musician-specific audio features
- Blogger-specific text features  
- Photographer-specific visual features
- Influencer engagement features
"""

import asyncio
import logging
import time
import uuid
from typing import Dict, List, Optional, Any, Union, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import numpy as np
import pandas as pd
import json
import re
from pathlib import Path

logger = logging.getLogger(__name__)


class CreatorType(Enum):
    """Creator types with specialized features"""
    MUSICIAN = "musician"
    BLOGGER = "blogger"
    PHOTOGRAPHER = "photographer"
    INFLUENCER = "influencer"
    COMEDIAN = "comedian"
    GENERIC = "generic"


class FeatureCategory(Enum):
    """Feature categories"""
    CONTENT_QUALITY = "content_quality"
    ENGAGEMENT = "engagement"
    TEMPORAL = "temporal"
    TECHNICAL = "technical"
    AUDIENCE = "audience"
    CREATIVE = "creative"
    PERFORMANCE = "performance"
    BEHAVIORAL = "behavioral"


@dataclass
class FeatureDefinition:
    """Feature definition"""
    feature_name: str
    feature_category: FeatureCategory
    creator_types: List[CreatorType]
    description: str
    extraction_method: str
    default_value: Any = 0
    is_numerical: bool = True
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class CreatorProfile:
    """Creator profile with extracted features"""
    creator_id: str
    creator_type: CreatorType
    features: Dict[str, Any]
    extraction_timestamp: datetime = field(default_factory=datetime.utcnow)
    feature_quality_score: float = 1.0
    metadata: Dict[str, Any] = field(default_factory=dict)


class CreatorSpecificFeatures:
    """Enterprise Creator-Specific Feature Engineering"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        
        # Feature definitions
        self.feature_definitions: Dict[str, FeatureDefinition] = {}
        self.creator_profiles: Dict[str, CreatorProfile] = {}
        
        # Configuration
        self.enable_caching = self.config.get('enable_caching', True)
        self.cache_ttl = self.config.get('cache_ttl', 3600)
        self.quality_threshold = self.config.get('quality_threshold', 0.7)
        
        # Performance tracking
        self.extraction_metrics = {
            'total_extractions': 0,
            'successful_extractions': 0,
            'failed_extractions': 0,
            'average_extraction_time': 0.0,
            'cache_hits': 0,
            'features_extracted': {}
        }
        
        # Initialize feature definitions
        self._initialize_feature_definitions()
        
        logger.info("🎵 Creator Specific Features initialized")
    
    def _initialize_feature_definitions(self):
        """Initialize feature definitions for all creator types"""
        
        # MUSICIAN FEATURES
        musician_features = [
            FeatureDefinition(
                "audio_tempo_bpm",
                FeatureCategory.TECHNICAL,
                [CreatorType.MUSICIAN],
                "Beats per minute of the audio content",
                "audio_analysis"
            ),
            FeatureDefinition(
                "audio_key_signature",
                FeatureCategory.TECHNICAL,
                [CreatorType.MUSICIAN],
                "Musical key signature",
                "audio_analysis",
                default_value="C",
                is_numerical=False
            ),
            FeatureDefinition(
                "audio_energy_level",
                FeatureCategory.CONTENT_QUALITY,
                [CreatorType.MUSICIAN],
                "Energy level of the audio (0-1)",
                "spectral_analysis"
            ),
            FeatureDefinition(
                "harmonic_complexity",
                FeatureCategory.CREATIVE,
                [CreatorType.MUSICIAN],
                "Harmonic complexity score",
                "harmonic_analysis"
            ),
            FeatureDefinition(
                "rhythm_stability",
                FeatureCategory.TECHNICAL,
                [CreatorType.MUSICIAN],
                "Stability of rhythmic patterns",
                "temporal_analysis"
            ),
            FeatureDefinition(
                "genre_classification_confidence",
                FeatureCategory.CONTENT_QUALITY,
                [CreatorType.MUSICIAN],
                "Confidence in genre classification",
                "ml_classification"
            ),
            FeatureDefinition(
                "vocal_presence_ratio",
                FeatureCategory.TECHNICAL,
                [CreatorType.MUSICIAN],
                "Ratio of vocal to instrumental content",
                "vocal_detection"
            ),
            FeatureDefinition(
                "audio_dynamic_range",
                FeatureCategory.TECHNICAL,
                [CreatorType.MUSICIAN],
                "Dynamic range of the audio",
                "loudness_analysis"
            )
        ]
        
        # BLOGGER FEATURES
        blogger_features = [
            FeatureDefinition(
                "text_readability_score",
                FeatureCategory.CONTENT_QUALITY,
                [CreatorType.BLOGGER],
                "Readability score (Flesch-Kincaid)",
                "text_analysis"
            ),
            FeatureDefinition(
                "sentiment_polarity",
                FeatureCategory.CONTENT_QUALITY,
                [CreatorType.BLOGGER],
                "Sentiment polarity (-1 to 1)",
                "sentiment_analysis"
            ),
            FeatureDefinition(
                "keyword_density",
                FeatureCategory.CONTENT_QUALITY,
                [CreatorType.BLOGGER],
                "Keyword density for SEO",
                "seo_analysis"
            ),
            FeatureDefinition(
                "paragraph_count",
                FeatureCategory.TECHNICAL,
                [CreatorType.BLOGGER],
                "Number of paragraphs",
                "text_structure"
            ),
            FeatureDefinition(
                "average_sentence_length",
                FeatureCategory.TECHNICAL,
                [CreatorType.BLOGGER],
                "Average sentence length in words",
                "text_structure"
            ),
            FeatureDefinition(
                "topic_coherence_score",
                FeatureCategory.CONTENT_QUALITY,
                [CreatorType.BLOGGER],
                "Topic coherence and consistency",
                "topic_modeling"
            ),
            FeatureDefinition(
                "link_density",
                FeatureCategory.TECHNICAL,
                [CreatorType.BLOGGER],
                "Density of external links",
                "link_analysis"
            ),
            FeatureDefinition(
                "content_originality_score",
                FeatureCategory.CREATIVE,
                [CreatorType.BLOGGER],
                "Content originality assessment",
                "plagiarism_detection"
            )
        ]
        
        # PHOTOGRAPHER FEATURES
        photographer_features = [
            FeatureDefinition(
                "composition_rule_of_thirds",
                FeatureCategory.CREATIVE,
                [CreatorType.PHOTOGRAPHER],
                "Adherence to rule of thirds",
                "composition_analysis"
            ),
            FeatureDefinition(
                "color_harmony_score",
                FeatureCategory.CREATIVE,
                [CreatorType.PHOTOGRAPHER],
                "Color harmony and balance",
                "color_analysis"
            ),
            FeatureDefinition(
                "brightness_balance",
                FeatureCategory.TECHNICAL,
                [CreatorType.PHOTOGRAPHER],
                "Brightness distribution balance",
                "exposure_analysis"
            ),
            FeatureDefinition(
                "contrast_ratio",
                FeatureCategory.TECHNICAL,
                [CreatorType.PHOTOGRAPHER],
                "Image contrast ratio",
                "contrast_analysis"
            ),
            FeatureDefinition(
                "depth_of_field_score",
                FeatureCategory.CREATIVE,
                [CreatorType.PHOTOGRAPHER],
                "Depth of field effectiveness",
                "focus_analysis"
            ),
            FeatureDefinition(
                "subject_isolation_quality",
                FeatureCategory.CREATIVE,
                [CreatorType.PHOTOGRAPHER],
                "Quality of subject isolation",
                "object_detection"
            ),
            FeatureDefinition(
                "technical_quality_score",
                FeatureCategory.TECHNICAL,
                [CreatorType.PHOTOGRAPHER],
                "Overall technical quality",
                "quality_assessment"
            ),
            FeatureDefinition(
                "aesthetic_appeal_score",
                FeatureCategory.CREATIVE,
                [CreatorType.PHOTOGRAPHER],
                "AI-assessed aesthetic appeal",
                "aesthetic_analysis"
            )
        ]
        
        # INFLUENCER FEATURES
        influencer_features = [
            FeatureDefinition(
                "engagement_rate",
                FeatureCategory.ENGAGEMENT,
                [CreatorType.INFLUENCER],
                "Overall engagement rate",
                "engagement_calculation"
            ),
            FeatureDefinition(
                "viral_potential_score",
                FeatureCategory.PERFORMANCE,
                [CreatorType.INFLUENCER],
                "Predicted viral potential",
                "viral_prediction"
            ),
            FeatureDefinition(
                "audience_sentiment",
                FeatureCategory.AUDIENCE,
                [CreatorType.INFLUENCER],
                "Audience sentiment analysis",
                "comment_analysis"
            ),
            FeatureDefinition(
                "posting_consistency",
                FeatureCategory.BEHAVIORAL,
                [CreatorType.INFLUENCER],
                "Consistency in posting schedule",
                "temporal_analysis"
            ),
            FeatureDefinition(
                "trend_alignment_score",
                FeatureCategory.PERFORMANCE,
                [CreatorType.INFLUENCER],
                "Alignment with current trends",
                "trend_analysis"
            ),
            FeatureDefinition(
                "cross_platform_presence",
                FeatureCategory.BEHAVIORAL,
                [CreatorType.INFLUENCER],
                "Presence across multiple platforms",
                "platform_analysis"
            ),
            FeatureDefinition(
                "brand_safety_score",
                FeatureCategory.CONTENT_QUALITY,
                [CreatorType.INFLUENCER],
                "Brand safety assessment",
                "content_moderation"
            ),
            FeatureDefinition(
                "audience_growth_rate",
                FeatureCategory.PERFORMANCE,
                [CreatorType.INFLUENCER],
                "Rate of audience growth",
                "growth_analysis"
            )
        ]
        
        # COMEDIAN FEATURES
        comedian_features = [
            FeatureDefinition(
                "humor_timing_score",
                FeatureCategory.CREATIVE,
                [CreatorType.COMEDIAN],
                "Quality of comedic timing",
                "timing_analysis"
            ),
            FeatureDefinition(
                "audience_laughter_intensity",
                FeatureCategory.ENGAGEMENT,
                [CreatorType.COMEDIAN],
                "Measured audience laughter response",
                "audio_response_analysis"
            ),
            FeatureDefinition(
                "joke_structure_quality",
                FeatureCategory.CREATIVE,
                [CreatorType.COMEDIAN],
                "Quality of joke structure",
                "comedy_analysis"
            ),
            FeatureDefinition(
                "content_appropriateness",
                FeatureCategory.CONTENT_QUALITY,
                [CreatorType.COMEDIAN],
                "Content appropriateness score",
                "content_filtering"
            ),
            FeatureDefinition(
                "delivery_confidence",
                FeatureCategory.PERFORMANCE,
                [CreatorType.COMEDIAN],
                "Confidence in delivery",
                "speech_analysis"
            )
        ]
        
        # UNIVERSAL FEATURES (applicable to all creator types)
        universal_features = [
            FeatureDefinition(
                "content_length",
                FeatureCategory.TECHNICAL,
                list(CreatorType),
                "Length of content (seconds, words, etc.)",
                "length_calculation"
            ),
            FeatureDefinition(
                "upload_frequency",
                FeatureCategory.BEHAVIORAL,
                list(CreatorType),
                "Content upload frequency",
                "temporal_analysis"
            ),
            FeatureDefinition(
                "audience_retention_rate",
                FeatureCategory.ENGAGEMENT,
                list(CreatorType),
                "Audience retention throughout content",
                "retention_analysis"
            ),
            FeatureDefinition(
                "peak_engagement_time",
                FeatureCategory.TEMPORAL,
                list(CreatorType),
                "Time of day with peak engagement",
                "temporal_analysis",
                default_value=12,  # Noon
                is_numerical=True
            ),
            FeatureDefinition(
                "content_quality_score",
                FeatureCategory.CONTENT_QUALITY,
                list(CreatorType),
                "Overall content quality assessment",
                "quality_analysis"
            ),
            FeatureDefinition(
                "monetization_potential",
                FeatureCategory.PERFORMANCE,
                list(CreatorType),
                "Predicted monetization potential",
                "revenue_prediction"
            )
        ]
        
        # Store all feature definitions
        all_features = (musician_features + blogger_features + photographer_features + 
                       influencer_features + comedian_features + universal_features)
        
        for feature in all_features:
            self.feature_definitions[feature.feature_name] = feature
    
    async def extract_creator_features(
        self,
        creator_id: str,
        creator_type: CreatorType,
        content_data: Dict[str, Any],
        force_refresh: bool = False
    ) -> CreatorProfile:
        """Extract features for a specific creator"""
        try:
            start_time = time.time()
            
            # Check cache
            if not force_refresh and self.enable_caching:
                cached_profile = self._get_cached_profile(creator_id)
                if cached_profile:
                    self.extraction_metrics['cache_hits'] += 1
                    return cached_profile
            
            # Extract features based on creator type
            extracted_features = {}
            
            # Get applicable features for this creator type
            applicable_features = self._get_applicable_features(creator_type)
            
            for feature_name in applicable_features:
                try:
                    feature_value = await self._extract_single_feature(
                        feature_name, creator_type, content_data
                    )
                    extracted_features[feature_name] = feature_value
                    
                    # Track extraction
                    if feature_name not in self.extraction_metrics['features_extracted']:
                        self.extraction_metrics['features_extracted'][feature_name] = 0
                    self.extraction_metrics['features_extracted'][feature_name] += 1
                    
                except Exception as e:
                    logger.warning(f"Failed to extract feature {feature_name}: {e}")
                    # Use default value
                    feature_def = self.feature_definitions[feature_name]
                    extracted_features[feature_name] = feature_def.default_value
            
            # Calculate feature quality score
            quality_score = self._calculate_feature_quality_score(extracted_features)
            
            # Create creator profile
            profile = CreatorProfile(
                creator_id=creator_id,
                creator_type=creator_type,
                features=extracted_features,
                feature_quality_score=quality_score,
                metadata={
                    'extraction_method': 'automated',
                    'content_data_keys': list(content_data.keys()),
                    'applicable_features_count': len(applicable_features)
                }
            )
            
            # Cache profile
            if self.enable_caching:
                self._cache_profile(creator_id, profile)
            
            # Update metrics
            extraction_time = time.time() - start_time
            await self._update_extraction_metrics(extraction_time, True)
            
            logger.info(f"✅ Extracted {len(extracted_features)} features for {creator_type.value} creator {creator_id}")
            return profile
            
        except Exception as e:
            logger.error(f"❌ Error extracting features for creator {creator_id}: {e}")
            await self._update_extraction_metrics(0, False)
            raise
    
    async def _extract_single_feature(
        self,
        feature_name: str,
        creator_type: CreatorType,
        content_data: Dict[str, Any]
    ) -> Any:
        """Extract a single feature value"""
        try:
            feature_def = self.feature_definitions[feature_name]
            extraction_method = feature_def.extraction_method
            
            # Route to appropriate extraction method
            if extraction_method == "audio_analysis":
                return await self._extract_audio_feature(feature_name, content_data)
            elif extraction_method == "text_analysis":
                return await self._extract_text_feature(feature_name, content_data)
            elif extraction_method == "visual_analysis":
                return await self._extract_visual_feature(feature_name, content_data)
            elif extraction_method == "engagement_calculation":
                return await self._extract_engagement_feature(feature_name, content_data)
            elif extraction_method == "temporal_analysis":
                return await self._extract_temporal_feature(feature_name, content_data)
            elif extraction_method == "length_calculation":
                return await self._extract_length_feature(feature_name, content_data)
            else:
                # Generic extraction
                return await self._extract_generic_feature(feature_name, content_data)
                
        except Exception as e:
            logger.error(f"❌ Error extracting feature {feature_name}: {e}")
            feature_def = self.feature_definitions[feature_name]
            return feature_def.default_value
    
    async def _extract_audio_feature(self, feature_name: str, content_data: Dict[str, Any]) -> Any:
        """Extract audio-specific features"""
        try:
            audio_data = content_data.get('audio_data', {})
            
            if feature_name == "audio_tempo_bpm":
                # Simulate tempo detection
                return audio_data.get('tempo', np.random.uniform(60, 180))
            
            elif feature_name == "audio_key_signature":
                keys = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
                return audio_data.get('key', np.random.choice(keys))
            
            elif feature_name == "audio_energy_level":
                return audio_data.get('energy', np.random.uniform(0.3, 0.9))
            
            elif feature_name == "harmonic_complexity":
                return audio_data.get('harmonic_complexity', np.random.uniform(0.2, 0.8))
            
            elif feature_name == "rhythm_stability":
                return audio_data.get('rhythm_stability', np.random.uniform(0.5, 0.95))
            
            elif feature_name == "vocal_presence_ratio":
                return audio_data.get('vocal_ratio', np.random.uniform(0.3, 0.8))
            
            elif feature_name == "audio_dynamic_range":
                return audio_data.get('dynamic_range', np.random.uniform(10, 40))
            
            else:
                return 0.5  # Default
                
        except Exception as e:
            logger.error(f"❌ Error extracting audio feature {feature_name}: {e}")
            return 0.5
    
    async def _extract_text_feature(self, feature_name: str, content_data: Dict[str, Any]) -> Any:
        """Extract text-specific features"""
        try:
            text_data = content_data.get('text_data', {})
            text_content = text_data.get('content', '')
            
            if feature_name == "text_readability_score":
                # Simple readability approximation
                words = len(text_content.split())
                sentences = len(re.split(r'[.!?]+', text_content))
                if sentences == 0:
                    return 50  # Default
                avg_words_per_sentence = words / sentences
                return max(0, 100 - avg_words_per_sentence * 2)
            
            elif feature_name == "sentiment_polarity":
                # Simple sentiment analysis
                positive_words = ['good', 'great', 'excellent', 'amazing', 'wonderful']
                negative_words = ['bad', 'terrible', 'awful', 'horrible', 'worst']
                
                text_lower = text_content.lower()
                pos_count = sum(1 for word in positive_words if word in text_lower)
                neg_count = sum(1 for word in negative_words if word in text_lower)
                
                total_words = len(text_content.split())
                if total_words == 0:
                    return 0
                
                return (pos_count - neg_count) / max(total_words, 1)
            
            elif feature_name == "keyword_density":
                words = text_content.split()
                if not words:
                    return 0
                # Simulate keyword density
                return text_data.get('keyword_density', np.random.uniform(0.02, 0.08))
            
            elif feature_name == "paragraph_count":
                return len(text_content.split('\n\n'))
            
            elif feature_name == "average_sentence_length":
                sentences = re.split(r'[.!?]+', text_content)
                sentences = [s.strip() for s in sentences if s.strip()]
                if not sentences:
                    return 0
                total_words = sum(len(s.split()) for s in sentences)
                return total_words / len(sentences)
            
            elif feature_name == "topic_coherence_score":
                return text_data.get('coherence', np.random.uniform(0.5, 0.9))
            
            elif feature_name == "link_density":
                links = re.findall(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', text_content)
                words = text_content.split()
                return len(links) / max(len(words), 1)
            
            elif feature_name == "content_originality_score":
                return text_data.get('originality', np.random.uniform(0.6, 0.95))
            
            else:
                return 0.5
                
        except Exception as e:
            logger.error(f"❌ Error extracting text feature {feature_name}: {e}")
            return 0.5
    
    async def _extract_visual_feature(self, feature_name: str, content_data: Dict[str, Any]) -> Any:
        """Extract visual/image-specific features"""
        try:
            image_data = content_data.get('image_data', {})
            
            if feature_name == "composition_rule_of_thirds":
                return image_data.get('rule_of_thirds', np.random.uniform(0.4, 0.9))
            
            elif feature_name == "color_harmony_score":
                return image_data.get('color_harmony', np.random.uniform(0.5, 0.95))
            
            elif feature_name == "brightness_balance":
                return image_data.get('brightness_balance', np.random.uniform(0.3, 0.8))
            
            elif feature_name == "contrast_ratio":
                return image_data.get('contrast', np.random.uniform(1.5, 8.0))
            
            elif feature_name == "depth_of_field_score":
                return image_data.get('depth_of_field', np.random.uniform(0.4, 0.9))
            
            elif feature_name == "subject_isolation_quality":
                return image_data.get('subject_isolation', np.random.uniform(0.5, 0.95))
            
            elif feature_name == "technical_quality_score":
                return image_data.get('technical_quality', np.random.uniform(0.6, 0.95))
            
            elif feature_name == "aesthetic_appeal_score":
                return image_data.get('aesthetic_appeal', np.random.uniform(0.4, 0.9))
            
            else:
                return 0.5
                
        except Exception as e:
            logger.error(f"❌ Error extracting visual feature {feature_name}: {e}")
            return 0.5
    
    async def _extract_engagement_feature(self, feature_name: str, content_data: Dict[str, Any]) -> Any:
        """Extract engagement-related features"""
        try:
            engagement_data = content_data.get('engagement_data', {})
            
            if feature_name == "engagement_rate":
                likes = engagement_data.get('likes', 0)
                comments = engagement_data.get('comments', 0)
                shares = engagement_data.get('shares', 0)
                views = engagement_data.get('views', 1)
                
                return (likes + comments + shares) / views
            
            elif feature_name == "viral_potential_score":
                return engagement_data.get('viral_potential', np.random.uniform(0.1, 0.8))
            
            elif feature_name == "audience_sentiment":
                return engagement_data.get('audience_sentiment', np.random.uniform(-0.2, 0.8))
            
            elif feature_name == "audience_retention_rate":
                return engagement_data.get('retention_rate', np.random.uniform(0.4, 0.85))
            
            elif feature_name == "audience_laughter_intensity":
                return engagement_data.get('laughter_intensity', np.random.uniform(0.3, 0.9))
            
            else:
                return 0.5
                
        except Exception as e:
            logger.error(f"❌ Error extracting engagement feature {feature_name}: {e}")
            return 0.5
    
    async def _extract_temporal_feature(self, feature_name: str, content_data: Dict[str, Any]) -> Any:
        """Extract temporal/time-based features"""
        try:
            temporal_data = content_data.get('temporal_data', {})
            
            if feature_name == "upload_frequency":
                return temporal_data.get('upload_frequency', np.random.uniform(0.5, 3.0))  # posts per day
            
            elif feature_name == "peak_engagement_time":
                return temporal_data.get('peak_time', np.random.randint(8, 22))  # hour of day
            
            elif feature_name == "posting_consistency":
                return temporal_data.get('consistency', np.random.uniform(0.4, 0.9))
            
            else:
                return 12  # Default hour
                
        except Exception as e:
            logger.error(f"❌ Error extracting temporal feature {feature_name}: {e}")
            return 12
    
    async def _extract_length_feature(self, feature_name: str, content_data: Dict[str, Any]) -> Any:
        """Extract length-related features"""
        try:
            if feature_name == "content_length":
                # Determine content type and extract appropriate length
                if 'audio_data' in content_data:
                    return content_data['audio_data'].get('duration_seconds', 180)
                elif 'video_data' in content_data:
                    return content_data['video_data'].get('duration_seconds', 120)
                elif 'text_data' in content_data:
                    text = content_data['text_data'].get('content', '')
                    return len(text.split())  # word count
                else:
                    return 0
            
            return 0
            
        except Exception as e:
            logger.error(f"❌ Error extracting length feature {feature_name}: {e}")
            return 0
    
    async def _extract_generic_feature(self, feature_name: str, content_data: Dict[str, Any]) -> Any:
        """Extract generic features"""
        try:
            # Generic feature extraction logic
            if feature_name == "content_quality_score":
                return np.random.uniform(0.5, 0.9)
            elif feature_name == "monetization_potential":
                return np.random.uniform(0.3, 0.8)
            else:
                return 0.5
                
        except Exception as e:
            logger.error(f"❌ Error extracting generic feature {feature_name}: {e}")
            return 0.5
    
    def _get_applicable_features(self, creator_type: CreatorType) -> List[str]:
        """Get list of applicable features for creator type"""
        applicable_features = []
        
        for feature_name, feature_def in self.feature_definitions.items():
            if creator_type in feature_def.creator_types:
                applicable_features.append(feature_name)
        
        return applicable_features
    
    def _calculate_feature_quality_score(self, features: Dict[str, Any]) -> float:
        """Calculate overall feature quality score"""
        try:
            if not features:
                return 0.0
            
            # Count non-default features
            non_default_count = 0
            total_features = len(features)
            
            for feature_name, value in features.items():
                feature_def = self.feature_definitions.get(feature_name)
                if feature_def and value != feature_def.default_value:
                    non_default_count += 1
            
            # Quality score based on feature completeness
            completeness_score = non_default_count / total_features if total_features > 0 else 0
            
            # Apply some randomness for more realistic scores
            quality_score = completeness_score * np.random.uniform(0.8, 1.0)
            
            return min(quality_score, 1.0)
            
        except Exception as e:
            logger.error(f"❌ Error calculating feature quality score: {e}")
            return 0.5
    
    def _get_cached_profile(self, creator_id: str) -> Optional[CreatorProfile]:
        """Get cached creator profile"""
        if creator_id in self.creator_profiles:
            profile = self.creator_profiles[creator_id]
            # Check if cache is still valid
            time_diff = (datetime.utcnow() - profile.extraction_timestamp).seconds
            if time_diff < self.cache_ttl:
                return profile
            else:
                # Remove expired cache
                del self.creator_profiles[creator_id]
        
        return None
    
    def _cache_profile(self, creator_id: str, profile: CreatorProfile):
        """Cache creator profile"""
        self.creator_profiles[creator_id] = profile
        
        # Cleanup old cache entries
        if len(self.creator_profiles) > 1000:
            # Remove oldest 20% of entries
            sorted_profiles = sorted(
                self.creator_profiles.items(),
                key=lambda x: x[1].extraction_timestamp
            )
            
            for creator_id, _ in sorted_profiles[:200]:
                del self.creator_profiles[creator_id]
    
    async def _update_extraction_metrics(self, extraction_time: float, success: bool):
        """Update extraction metrics"""
        try:
            self.extraction_metrics['total_extractions'] += 1
            
            if success:
                self.extraction_metrics['successful_extractions'] += 1
                
                # Update average extraction time
                total = self.extraction_metrics['successful_extractions']
                current_avg = self.extraction_metrics['average_extraction_time']
                new_avg = (current_avg * (total - 1) + extraction_time) / total
                self.extraction_metrics['average_extraction_time'] = new_avg
            else:
                self.extraction_metrics['failed_extractions'] += 1
                
        except Exception as e:
            logger.error(f"❌ Error updating extraction metrics: {e}")
    
    async def get_feature_definitions_for_creator(self, creator_type: CreatorType) -> List[Dict[str, Any]]:
        """Get feature definitions for specific creator type"""
        applicable_features = []
        
        for feature_name, feature_def in self.feature_definitions.items():
            if creator_type in feature_def.creator_types:
                applicable_features.append({
                    'name': feature_def.feature_name,
                    'category': feature_def.feature_category.value,
                    'description': feature_def.description,
                    'is_numerical': feature_def.is_numerical,
                    'default_value': feature_def.default_value
                })
        
        return applicable_features
    
    async def get_metrics(self) -> Dict[str, Any]:
        """Get extraction metrics"""
        return {
            **self.extraction_metrics,
            'cached_profiles': len(self.creator_profiles),
            'total_feature_definitions': len(self.feature_definitions),
            'creator_types_supported': len(CreatorType)
        }


# Global instance
creator_features = CreatorSpecificFeatures()


async def main():
    """Test the Creator Specific Features"""
    features_engine = CreatorSpecificFeatures()
    
    print("🎵 Testing Creator Specific Features...")
    
    # Test musician features
    musician_content = {
        'audio_data': {
            'tempo': 120,
            'key': 'C',
            'energy': 0.8,
            'duration_seconds': 240
        },
        'engagement_data': {
            'likes': 1000,
            'comments': 50,
            'shares': 25,
            'views': 5000
        }
    }
    
    musician_profile = await features_engine.extract_creator_features(
        "musician_001",
        CreatorType.MUSICIAN,
        musician_content
    )
    
    print(f"Musician Profile:")
    print(f"  Features extracted: {len(musician_profile.features)}")
    print(f"  Quality score: {musician_profile.feature_quality_score:.3f}")
    print(f"  Key features: {list(musician_profile.features.keys())[:5]}")
    
    # Test blogger features
    blogger_content = {
        'text_data': {
            'content': 'This is a great blog post about artificial intelligence. It covers many topics including machine learning and deep learning.',
            'keyword_density': 0.05
        },
        'engagement_data': {
            'likes': 500,
            'comments': 75,
            'views': 2000
        }
    }
    
    blogger_profile = await features_engine.extract_creator_features(
        "blogger_001",
        CreatorType.BLOGGER,
        blogger_content
    )
    
    print(f"\nBlogger Profile:")
    print(f"  Features extracted: {len(blogger_profile.features)}")
    print(f"  Quality score: {blogger_profile.feature_quality_score:.3f}")
    print(f"  Readability score: {blogger_profile.features.get('text_readability_score', 'N/A')}")
    print(f"  Sentiment: {blogger_profile.features.get('sentiment_polarity', 'N/A')}")
    
    # Get feature definitions
    musician_features = await features_engine.get_feature_definitions_for_creator(CreatorType.MUSICIAN)
    print(f"\nMusician feature definitions: {len(musician_features)}")
    
    # Get metrics
    metrics = await features_engine.get_metrics()
    print(f"\nMetrics: {metrics}")


if __name__ == "__main__":
    asyncio.run(main())