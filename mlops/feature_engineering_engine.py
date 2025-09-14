"""
Feature Engineering Engine module
Enterprise implementation for Ainflue platform
"""

#!/usr/bin/env python3
"""
🏗️ MLOps Feature Engineering Engine - Automated ML Feature Pipeline

Engine d'engineering de features automatisé avec ML AutoFE pour créateurs.
Transformation intelligente de données multi-format avec optimisation business logic Ainflue.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
Role: ML Engineer + Data Engineer + Backend Senior
"""

import asyncio
import json
import hashlib
import time
import re
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, List, Optional, Any, Union, Callable, Tuple
import logging
from pathlib import Path
import pickle
import base64

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class FeatureType(Enum):
    """Types de features"""
    NUMERICAL = "numerical"
    CATEGORICAL = "categorical"
    TEXT = "text"
    AUDIO = "audio"
    IMAGE = "image"
    TEMPORAL = "temporal"
    INTERACTION = "interaction"
    DERIVED = "derived"


class TransformationType(Enum):
    """Types de transformations"""
    NORMALIZATION = "normalization"
    STANDARDIZATION = "standardization"
    ENCODING = "encoding"
    BINNING = "binning"
    POLYNOMIAL = "polynomial"
    LOG_TRANSFORM = "log_transform"
    TEXT_VECTORIZATION = "text_vectorization"
    AUDIO_FEATURES = "audio_features"
    IMAGE_FEATURES = "image_features"
    AGGREGATION = "aggregation"
    ROLLING_STATS = "rolling_stats"


class CreatorType(Enum):
    """Types de créateurs Ainflue"""
    MUSICIAN = "musician"
    BLOGGER = "blogger"
    PHOTOGRAPHER = "photographer"
    INFLUENCER = "influencer"
    COMEDIAN = "comedian"


@dataclass
class FeatureSchema:
    """Schéma d'une feature"""
    name: str
    feature_type: FeatureType
    data_type: str  # int, float, str, list, etc.
    description: str
    source_columns: List[str] = field(default_factory=list)
    transformation: Optional[TransformationType] = None
    parameters: Dict[str, Any] = field(default_factory=dict)
    creator_specific: Optional[CreatorType] = None
    business_importance: float = 1.0  # 0-1 score
    computation_cost: float = 1.0     # 0-1 score (lower is better)


@dataclass
class FeatureTransformation:
    """Transformation de feature avec métadonnées"""
    name: str
    transformation_type: TransformationType
    input_features: List[str]
    output_features: List[str]
    parameters: Dict[str, Any] = field(default_factory=dict)
    code: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.now)
    created_by: str = "system"
    version: str = "1.0.0"


@dataclass
class FeatureSet:
    """Ensemble de features pour un use case"""
    name: str
    features: List[FeatureSchema]
    creator_type: Optional[CreatorType] = None
    use_case: str = "general"
    version: str = "1.0.0"
    created_at: datetime = field(default_factory=datetime.now)
    performance_metrics: Dict[str, float] = field(default_factory=dict)


class AutoFeatureSelector:
    """Sélecteur automatique de features basé sur l'importance"""
    
    def __init__(self) -> None:
        # Importance scores for different creator types and use cases
        self.feature_importance_weights = {
            CreatorType.MUSICIAN: {
                "audio_features": 0.9,
                "engagement_rate": 0.8,
                "genre_tags": 0.7,
                "tempo": 0.8,
                "mood_score": 0.7,
                "collaboration_history": 0.6
            },
            CreatorType.BLOGGER: {
                "text_features": 0.9,
                "readability_score": 0.8,
                "keyword_density": 0.7,
                "sentiment_score": 0.8,
                "word_count": 0.6,
                "topic_relevance": 0.8
            },
            CreatorType.PHOTOGRAPHER: {
                "image_features": 0.9,
                "color_palette": 0.8,
                "composition_score": 0.7,
                "aesthetic_rating": 0.8,
                "technical_quality": 0.7,
                "style_consistency": 0.6
            },
            CreatorType.INFLUENCER: {
                "engagement_metrics": 0.9,
                "follower_growth": 0.8,
                "cross_platform_presence": 0.7,
                "brand_affinity": 0.8,
                "audience_demographics": 0.7
            },
            CreatorType.COMEDIAN: {
                "humor_features": 0.9,
                "timing_analysis": 0.8,
                "audience_reaction": 0.8,
                "joke_structure": 0.7,
                "delivery_style": 0.6
            }
        }
    
    def select_features_for_creator(self, available_features: List[FeatureSchema],
                                  creator_type: CreatorType, use_case: str = "general",
                                  max_features: int = 50) -> List[FeatureSchema]:
        """Sélectionne automatiquement les meilleures features pour un créateur"""
        
        # Calculate scores for each feature
        feature_scores = []
        weights = self.feature_importance_weights.get(creator_type, {})
        
        for feature in available_features:
            score = self._calculate_feature_score(feature, creator_type, weights, use_case)
            feature_scores.append((feature, score))
        
        # Sort by score and select top features
        feature_scores.sort(key=lambda x: x[1], reverse=True)
        selected_features = [f[0] for f in feature_scores[:max_features]]
        
        logger.info(f"✅ Selected {len(selected_features)} features for {creator_type.value} ({use_case})")
        return selected_features
    
    def _calculate_feature_score(self, feature: FeatureSchema, creator_type: CreatorType,
                                weights: Dict[str, float], use_case: str) -> float:
        """Calculate feature importance score"""
        score = feature.business_importance
        
        # Creator-specific boost
        if feature.creator_specific == creator_type:
            score *= 1.5
        
        # Weight-based scoring
        feature_category = self._get_feature_category(feature.name)
        if feature_category in weights:
            score *= weights[feature_category]
        
        # Penalize high computation cost
        score *= (2.0 - feature.computation_cost)
        
        # Use case specific adjustments
        if use_case == "monetization" and "revenue" in feature.name.lower():
            score *= 1.3
        elif use_case == "engagement" and "engagement" in feature.name.lower():
            score *= 1.3
        elif use_case == "quality" and "quality" in feature.name.lower():
            score *= 1.3
        
        return max(0, score)
    
    def _get_feature_category(self, feature_name: str) -> str:
        """Extract feature category from name"""
        name_lower = feature_name.lower()
        
        if any(word in name_lower for word in ["audio", "tempo", "genre", "music"]):
            return "audio_features"
        elif any(word in name_lower for word in ["text", "word", "sentiment", "topic"]):
            return "text_features"
        elif any(word in name_lower for word in ["image", "color", "visual", "composition"]):
            return "image_features"
        elif any(word in name_lower for word in ["engagement", "like", "comment", "share"]):
            return "engagement_metrics"
        elif any(word in name_lower for word in ["humor", "joke", "comedy", "funny"]):
            return "humor_features"
        else:
            return "general"


class FeatureTransformationEngine:
    """Engine de transformation de features"""
    
    def __init__(self) -> None:
        self.transformations = {}
        self.transformation_cache = {}
        
        # Initialize common transformations
        self._init_common_transformations()
    
    def _init_common_transformations(self) -> None:
        """Initialize common feature transformations"""
        
        # Text transformations for bloggers
        self.register_transformation(FeatureTransformation(
            name="text_length_features",
            transformation_type=TransformationType.AGGREGATION,
            input_features=["content_text"],
            output_features=["word_count", "char_count", "sentence_count", "paragraph_count"],
            parameters={"include_stopwords": False},
            code="""
def transform(text) -> None:
    words = len(text.split())
    chars = len(text)
    sentences = len([s for s in text.split('.') if s.strip()])
    paragraphs = len([p for p in text.split('\\n\\n') if p.strip()])
    return {
        'word_count': words,
        'char_count': chars, 
        'sentence_count': sentences,
        'paragraph_count': paragraphs
    }
"""
        ))
        
        # Audio transformations for musicians
        self.register_transformation(FeatureTransformation(
            name="audio_basic_features",
            transformation_type=TransformationType.AUDIO_FEATURES,
            input_features=["audio_file_path"],
            output_features=["duration", "sample_rate", "tempo_bpm", "key_signature"],
            parameters={"normalize": True},
            code="""
def transform(audio_path) -> None:
    # Simulated audio analysis
    import random
    return {
        'duration': random.uniform(120, 300),  # seconds
        'sample_rate': 44100,
        'tempo_bpm': random.uniform(60, 180),
        'key_signature': random.choice(['C', 'D', 'E', 'F', 'G', 'A', 'B'])
    }
"""
        ))
        
        # Image transformations for photographers
        self.register_transformation(FeatureTransformation(
            name="image_composition_features",
            transformation_type=TransformationType.IMAGE_FEATURES,
            input_features=["image_file_path"],
            output_features=["aspect_ratio", "dominant_colors", "brightness", "contrast"],
            parameters={"color_analysis": True},
            code="""
def transform(image_path) -> None:
    # Simulated image analysis
    import random
    return {
        'aspect_ratio': random.choice([1.0, 1.33, 1.77, 0.75]),
        'dominant_colors': random.randint(3, 8),
        'brightness': random.uniform(0.2, 0.8),
        'contrast': random.uniform(0.3, 0.9)
    }
"""
        ))
        
        # Engagement transformations for all creators
        self.register_transformation(FeatureTransformation(
            name="engagement_rate_features",
            transformation_type=TransformationType.AGGREGATION,
            input_features=["likes", "comments", "shares", "views"],
            output_features=["engagement_rate", "interaction_ratio", "viral_score"],
            parameters={"time_window": "24h"},
            code="""
def transform(likes, comments, shares, views) -> None:
    if views == 0:
        return {'engagement_rate': 0, 'interaction_ratio': 0, 'viral_score': 0}
    
    engagement_rate = (likes + comments + shares) / views
    interaction_ratio = comments / max(likes, 1)
    viral_score = shares / max(views / 1000, 1)
    
    return {
        'engagement_rate': min(engagement_rate, 1.0),
        'interaction_ratio': min(interaction_ratio, 1.0), 
        'viral_score': min(viral_score, 1.0)
    }
"""
        ))
    
    def register_transformation(self, transformation -> None: FeatureTransformation) -> None:
        """Register a new transformation"""
        self.transformations[transformation.name] = transformation
        logger.info(f"✅ Registered transformation: {transformation.name}")
    
    def apply_transformation(self, transformation_name: str, 
                           input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Apply a transformation to input data"""
        
        if transformation_name not in self.transformations:
            raise ValueError(f"Transformation {transformation_name} not found")
        
        transformation = self.transformations[transformation_name]
        
        # Check cache first
        cache_key = self._get_cache_key(transformation_name, input_data)
        if cache_key in self.transformation_cache:
            return self.transformation_cache[cache_key]
        
        try:
            # Extract required input features
            inputs = {}
            for feature in transformation.input_features:
                if feature not in input_data:
                    raise ValueError(f"Required input feature {feature} not found")
                inputs[feature] = input_data[feature]
            
            # Apply transformation (simplified - in production would use exec safely)
            result = self._execute_transformation(transformation, inputs)
            
            # Cache result
            self.transformation_cache[cache_key] = result
            
            logger.debug(f"✅ Applied transformation {transformation_name}")
            return result
            
        except Exception as e:
            logger.error(f"❌ Failed to apply transformation {transformation_name}: {e}")
            return {}
    
    def _execute_transformation(self, transformation: FeatureTransformation,
                              inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Execute transformation logic"""
        
        # Simplified execution - in production would use sandboxed execution
        if transformation.name == "text_length_features":
            text = inputs["content_text"]
            words = len(str(text).split())
            chars = len(str(text))
            sentences = len([s for s in str(text).split('.') if s.strip()])
            paragraphs = len([p for p in str(text).split('\n\n') if p.strip()])
            return {
                'word_count': words,
                'char_count': chars,
                'sentence_count': sentences,
                'paragraph_count': paragraphs
            }
        
        elif transformation.name == "audio_basic_features":
            # Simulated audio analysis
            import random
            return {
                'duration': random.uniform(120, 300),
                'sample_rate': 44100,
                'tempo_bpm': random.uniform(60, 180),
                'key_signature': random.choice(['C', 'D', 'E', 'F', 'G', 'A', 'B'])
            }
        
        elif transformation.name == "image_composition_features":
            # Simulated image analysis  
            import random
            return {
                'aspect_ratio': random.choice([1.0, 1.33, 1.77, 0.75]),
                'dominant_colors': random.randint(3, 8),
                'brightness': random.uniform(0.2, 0.8),
                'contrast': random.uniform(0.3, 0.9)
            }
        
        elif transformation.name == "engagement_rate_features":
            likes = inputs.get("likes", 0)
            comments = inputs.get("comments", 0)
            shares = inputs.get("shares", 0)
            views = inputs.get("views", 1)
            
            if views == 0:
                return {'engagement_rate': 0, 'interaction_ratio': 0, 'viral_score': 0}
            
            engagement_rate = (likes + comments + shares) / views
            interaction_ratio = comments / max(likes, 1)
            viral_score = shares / max(views / 1000, 1)
            
            return {
                'engagement_rate': min(engagement_rate, 1.0),
                'interaction_ratio': min(interaction_ratio, 1.0),
                'viral_score': min(viral_score, 1.0)
            }
        
        return {}
    
    def _get_cache_key(self, transformation_name: str, input_data: Dict[str, Any]) -> str:
        """Generate cache key for transformation result"""
        data_str = json.dumps(input_data, sort_keys=True, default=str)
        return hashlib.md5(f"{transformation_name}:{data_str}".encode()).hexdigest()
    
    def get_available_transformations(self) -> List[str]:
        """Get list of available transformations"""
        return list(self.transformations.keys())


class FeatureEngineeringEngine:
    """
    🏗️ Engine d'engineering de features enterprise pour MLOps
    
    Fonctionnalités:
    - Automated feature generation avec ML AutoFE
    - Creator-specific feature engineering (musiciens, blogueurs, etc.)
    - Real-time feature computation pipeline
    - Feature store integration
    - Data quality validation
    - Feature importance scoring
    - Transformation versioning et lineage
    - Business logic integration Ainflue
    """
    
    def __init__(self, config -> None: Optional[Dict[str, Any]] = None) -> None:
        self.config = config or {}
        self.feature_selector = AutoFeatureSelector()
        self.transformation_engine = FeatureTransformationEngine()
        
        # Feature catalog
        self.feature_catalog: Dict[str, FeatureSchema] = {}
        self.feature_sets: Dict[str, FeatureSet] = {}
        
        # Processing pipeline
        self.processing_pipeline: List[str] = []
        
        # Initialize creator-specific features
        self._init_creator_features()
        
        logger.info("🏗️ Feature Engineering Engine initialized for enterprise ML")
    
    def _init_creator_features(self) -> None:
        """Initialize creator-specific feature schemas"""
        
        # Musician features
        musician_features = [
            FeatureSchema(
                name="tempo_bpm",
                feature_type=FeatureType.NUMERICAL,
                data_type="float",
                description="Tempo of the music in beats per minute",
                source_columns=["audio_file"],
                transformation=TransformationType.AUDIO_FEATURES,
                creator_specific=CreatorType.MUSICIAN,
                business_importance=0.9,
                computation_cost=0.7
            ),
            FeatureSchema(
                name="genre_embedding",
                feature_type=FeatureType.CATEGORICAL,
                data_type="list",
                description="Multi-hot encoding of music genres",
                source_columns=["genre_tags"],
                transformation=TransformationType.ENCODING,
                creator_specific=CreatorType.MUSICIAN,
                business_importance=0.8,
                computation_cost=0.3
            ),
            FeatureSchema(
                name="collaboration_score",
                feature_type=FeatureType.NUMERICAL,
                data_type="float",
                description="Score based on collaboration history and compatibility",
                source_columns=["collaborations", "musical_style"],
                transformation=TransformationType.AGGREGATION,
                creator_specific=CreatorType.MUSICIAN,
                business_importance=0.7,
                computation_cost=0.5
            )
        ]
        
        # Blogger features
        blogger_features = [
            FeatureSchema(
                name="readability_score",
                feature_type=FeatureType.NUMERICAL,
                data_type="float",
                description="Flesch-Kincaid readability score",
                source_columns=["content_text"],
                transformation=TransformationType.TEXT_VECTORIZATION,
                creator_specific=CreatorType.BLOGGER,
                business_importance=0.8,
                computation_cost=0.4
            ),
            FeatureSchema(
                name="keyword_density",
                feature_type=FeatureType.NUMERICAL,
                data_type="dict",
                description="Density of important keywords in content",
                source_columns=["content_text", "target_keywords"],
                transformation=TransformationType.TEXT_VECTORIZATION,
                creator_specific=CreatorType.BLOGGER,
                business_importance=0.7,
                computation_cost=0.6
            ),
            FeatureSchema(
                name="sentiment_score",
                feature_type=FeatureType.NUMERICAL,
                data_type="float",
                description="Overall sentiment score of the content",
                source_columns=["content_text"],
                transformation=TransformationType.TEXT_VECTORIZATION,
                creator_specific=CreatorType.BLOGGER,
                business_importance=0.8,
                computation_cost=0.5
            )
        ]
        
        # Photographer features
        photographer_features = [
            FeatureSchema(
                name="aesthetic_score",
                feature_type=FeatureType.NUMERICAL,
                data_type="float",
                description="AI-computed aesthetic quality score",
                source_columns=["image_file"],
                transformation=TransformationType.IMAGE_FEATURES,
                creator_specific=CreatorType.PHOTOGRAPHER,
                business_importance=0.9,
                computation_cost=0.8
            ),
            FeatureSchema(
                name="color_harmony",
                feature_type=FeatureType.NUMERICAL,
                data_type="float",
                description="Color harmony and palette analysis",
                source_columns=["image_file"],
                transformation=TransformationType.IMAGE_FEATURES,
                creator_specific=CreatorType.PHOTOGRAPHER,
                business_importance=0.7,
                computation_cost=0.7
            )
        ]
        
        # Register all features
        all_features = musician_features + blogger_features + photographer_features
        for feature in all_features:
            self.feature_catalog[feature.name] = feature
        
        logger.info(f"✅ Initialized {len(all_features)} creator-specific features")
    
    async def generate_features_for_creator(self, creator_type: CreatorType,
                                          input_data: Dict[str, Any],
                                          use_case: str = "general") -> Dict[str, Any]:
        """Generate features for a specific creator type"""
        
        # Select relevant features
        available_features = list(self.feature_catalog.values())
        selected_features = self.feature_selector.select_features_for_creator(
            available_features, creator_type, use_case
        )
        
        # Generate features
        generated_features = {}
        
        for feature_schema in selected_features:
            try:
                feature_value = await self._generate_single_feature(feature_schema, input_data)
                if feature_value is not None:
                    generated_features[feature_schema.name] = feature_value
                    
            except Exception as e:
                logger.warning(f"⚠️ Failed to generate feature {feature_schema.name}: {e}")
        
        logger.info(f"✅ Generated {len(generated_features)} features for {creator_type.value}")
        return generated_features
    
    async def _generate_single_feature(self, feature_schema: FeatureSchema,
                                     input_data: Dict[str, Any]) -> Any:
        """Generate a single feature based on its schema"""
        
        # Check if required source columns are available
        missing_columns = [col for col in feature_schema.source_columns if col not in input_data]
        if missing_columns:
            logger.debug(f"Missing columns for {feature_schema.name}: {missing_columns}")
            return None
        
        # Apply transformation if specified
        if feature_schema.transformation:
            transformation_name = self._get_transformation_name(feature_schema)
            
            if transformation_name in self.transformation_engine.transformations:
                result = self.transformation_engine.apply_transformation(
                    transformation_name, input_data
                )
                return result.get(feature_schema.name)
        
        # Direct feature extraction for simple cases
        if len(feature_schema.source_columns) == 1:
            source_col = feature_schema.source_columns[0]
            return input_data.get(source_col)
        
        return None
    
    def _get_transformation_name(self, feature_schema: FeatureSchema) -> str:
        """Get transformation name for feature schema"""
        if feature_schema.transformation == TransformationType.TEXT_VECTORIZATION:
            return "text_length_features"
        elif feature_schema.transformation == TransformationType.AUDIO_FEATURES:
            return "audio_basic_features"
        elif feature_schema.transformation == TransformationType.IMAGE_FEATURES:
            return "image_composition_features"
        elif feature_schema.transformation == TransformationType.AGGREGATION:
            if "engagement" in feature_schema.name:
                return "engagement_rate_features"
        
        return feature_schema.name
    
    async def create_feature_set(self, name: str, creator_type: CreatorType,
                               use_case: str, feature_names: List[str]) -> FeatureSet:
        """Create a new feature set"""
        
        features = []
        for feature_name in feature_names:
            if feature_name in self.feature_catalog:
                features.append(self.feature_catalog[feature_name])
            else:
                logger.warning(f"⚠️ Feature {feature_name} not found in catalog")
        
        feature_set = FeatureSet(
            name=name,
            features=features,
            creator_type=creator_type,
            use_case=use_case
        )
        
        self.feature_sets[name] = feature_set
        logger.info(f"✅ Created feature set {name} with {len(features)} features")
        
        return feature_set
    
    async def compute_feature_importance(self, feature_set_name: str,
                                       target_metric: str) -> Dict[str, float]:
        """Compute feature importance scores"""
        
        if feature_set_name not in self.feature_sets:
            return {}
        
        feature_set = self.feature_sets[feature_set_name]
        importance_scores = {}
        
        # Simplified importance calculation based on business importance
        for feature in feature_set.features:
            base_score = feature.business_importance
            
            # Adjust based on target metric
            if target_metric == "engagement" and "engagement" in feature.name:
                base_score *= 1.3
            elif target_metric == "revenue" and "monetization" in feature.name:
                base_score *= 1.3
            elif target_metric == "quality" and "quality" in feature.name:
                base_score *= 1.3
            
            # Penalize high computation cost
            adjusted_score = base_score * (2.0 - feature.computation_cost)
            importance_scores[feature.name] = max(0, adjusted_score)
        
        return importance_scores
    
    async def validate_feature_quality(self, features: Dict[str, Any]) -> Dict[str, Any]:
        """Validate feature quality and detect issues"""
        
        quality_report = {
            "total_features": len(features),
            "valid_features": 0,
            "missing_features": 0,
            "invalid_features": [],
            "quality_score": 0.0,
            "issues": []
        }
        
        for feature_name, feature_value in features.items():
            try:
                if feature_value is None:
                    quality_report["missing_features"] += 1
                    quality_report["issues"].append(f"Missing value for {feature_name}")
                elif self._is_valid_feature_value(feature_name, feature_value):
                    quality_report["valid_features"] += 1
                else:
                    quality_report["invalid_features"].append(feature_name)
                    quality_report["issues"].append(f"Invalid value for {feature_name}")
                    
            except Exception as e:
                quality_report["invalid_features"].append(feature_name)
                quality_report["issues"].append(f"Error validating {feature_name}: {e}")
        
        # Calculate quality score
        if quality_report["total_features"] > 0:
            quality_report["quality_score"] = quality_report["valid_features"] / quality_report["total_features"]
        
        return quality_report
    
    def _is_valid_feature_value(self, feature_name: str, feature_value: Any) -> bool:
        """Validate individual feature value"""
        
        if feature_name not in self.feature_catalog:
            return True  # Unknown features are considered valid
        
        feature_schema = self.feature_catalog[feature_name]
        
        # Type validation
        if feature_schema.data_type == "float":
            try:
                float(feature_value)
                return not (isinstance(feature_value, float) and 
                          (feature_value != feature_value))  # NaN check
            except (ValueError, TypeError):
                return False
        
        elif feature_schema.data_type == "int":
            try:
                int(feature_value)
                return True
            except (ValueError, TypeError):
                return False
        
        elif feature_schema.data_type == "str":
            return isinstance(feature_value, str) and len(feature_value) > 0
        
        elif feature_schema.data_type == "list":
            return isinstance(feature_value, list)
        
        elif feature_schema.data_type == "dict":
            return isinstance(feature_value, dict)
        
        return True
    
    def get_feature_lineage(self, feature_name: str) -> Dict[str, Any]:
        """Get feature lineage and transformation history"""
        
        if feature_name not in self.feature_catalog:
            return {}
        
        feature_schema = self.feature_catalog[feature_name]
        
        lineage = {
            "feature_name": feature_name,
            "feature_type": feature_schema.feature_type.value,
            "source_columns": feature_schema.source_columns,
            "transformation": feature_schema.transformation.value if feature_schema.transformation else None,
            "creator_specific": feature_schema.creator_specific.value if feature_schema.creator_specific else None,
            "business_importance": feature_schema.business_importance,
            "computation_cost": feature_schema.computation_cost,
            "dependencies": []
        }
        
        # Add transformation details if available
        transformation_name = self._get_transformation_name(feature_schema)
        if transformation_name in self.transformation_engine.transformations:
            transformation = self.transformation_engine.transformations[transformation_name]
            lineage["transformation_details"] = {
                "name": transformation.name,
                "version": transformation.version,
                "created_by": transformation.created_by,
                "created_at": transformation.created_at.isoformat(),
                "input_features": transformation.input_features,
                "output_features": transformation.output_features
            }
        
        return lineage
    
    def export_feature_catalog(self) -> Dict[str, Any]:
        """Export complete feature catalog"""
        
        catalog_export = {
            "total_features": len(self.feature_catalog),
            "creator_types": list(set(f.creator_specific.value for f in self.feature_catalog.values() if f.creator_specific)),
            "feature_types": list(set(f.feature_type.value for f in self.feature_catalog.values())),
            "transformations": len(self.transformation_engine.transformations),
            "features": {}
        }
        
        for feature_name, feature_schema in self.feature_catalog.items():
            catalog_export["features"][feature_name] = {
                "type": feature_schema.feature_type.value,
                "data_type": feature_schema.data_type,
                "description": feature_schema.description,
                "creator_specific": feature_schema.creator_specific.value if feature_schema.creator_specific else None,
                "business_importance": feature_schema.business_importance,
                "computation_cost": feature_schema.computation_cost
            }
        
        return catalog_export
    
    def get_engine_statistics(self) -> Dict[str, Any]:
        """Get feature engineering engine statistics"""
        
        creator_feature_counts = {}
        for creator_type in CreatorType:
            count = len([f for f in self.feature_catalog.values() if f.creator_specific == creator_type])
            creator_feature_counts[creator_type.value] = count
        
        return {
            "total_features": len(self.feature_catalog),
            "feature_sets": len(self.feature_sets),
            "transformations": len(self.transformation_engine.transformations),
            "creator_feature_counts": creator_feature_counts,
            "cache_size": len(self.transformation_engine.transformation_cache),
            "avg_computation_cost": sum(f.computation_cost for f in self.feature_catalog.values()) / len(self.feature_catalog) if self.feature_catalog else 0,
            "avg_business_importance": sum(f.business_importance for f in self.feature_catalog.values()) / len(self.feature_catalog) if self.feature_catalog else 0
        }


# Demo function
async def demo_feature_engineering_engine() -> None:
    """Démonstration du feature engineering engine"""
    print("🏗️ MLOps Feature Engineering Engine Demo")
    
    # Initialize engine
    engine = FeatureEngineeringEngine()
    
    # Sample input data for a musician
    musician_data = {
        "audio_file": "/path/to/song.mp3",
        "genre_tags": ["rock", "alternative", "indie"],
        "collaborations": ["artist1", "artist2"],
        "musical_style": "indie-rock",
        "likes": 1500,
        "comments": 200,
        "shares": 50,
        "views": 10000
    }
    
    # Generate features for musician
    print("🎵 Generating features for musician...")
    musician_features = await engine.generate_features_for_creator(
        CreatorType.MUSICIAN, musician_data, "engagement"
    )
    print(f"✅ Generated {len(musician_features)} musician features:")
    for name, value in list(musician_features.items())[:5]:
        print(f"  - {name}: {value}")
    
    # Sample input data for a blogger
    blogger_data = {
        "content_text": "This is a comprehensive guide to machine learning for content creators. It covers various aspects of AI technology and how creators can leverage it for better engagement with their audience.",
        "target_keywords": ["machine learning", "AI", "content creation"],
        "likes": 800,
        "comments": 150,
        "shares": 75,
        "views": 5000
    }
    
    # Generate features for blogger
    print("\n📝 Generating features for blogger...")
    blogger_features = await engine.generate_features_for_creator(
        CreatorType.BLOGGER, blogger_data, "quality"
    )
    print(f"✅ Generated {len(blogger_features)} blogger features:")
    for name, value in list(blogger_features.items())[:5]:
        print(f"  - {name}: {value}")
    
    # Create feature set
    print("\n📊 Creating feature set...")
    feature_set = await engine.create_feature_set(
        "musician_engagement_features",
        CreatorType.MUSICIAN,
        "engagement",
        list(musician_features.keys())[:10]
    )
    print(f"✅ Created feature set with {len(feature_set.features)} features")
    
    # Compute feature importance
    print("\n🎯 Computing feature importance...")
    importance = await engine.compute_feature_importance("musician_engagement_features", "engagement")
    print("📈 Top 5 most important features:")
    sorted_importance = sorted(importance.items(), key=lambda x: x[1], reverse=True)
    for name, score in sorted_importance[:5]:
        print(f"  - {name}: {score:.3f}")
    
    # Validate feature quality
    print("\n🔍 Validating feature quality...")
    quality_report = await engine.validate_feature_quality(musician_features)
    print(f"📊 Quality Report:")
    print(f"  - Total features: {quality_report['total_features']}")
    print(f"  - Valid features: {quality_report['valid_features']}")
    print(f"  - Quality score: {quality_report['quality_score']:.2f}")
    
    # Get feature lineage
    print("\n🔄 Feature lineage example...")
    if musician_features:
        feature_name = list(musician_features.keys())[0]
        lineage = engine.get_feature_lineage(feature_name)
        if lineage:
            print(f"📋 Lineage for {feature_name}:")
            print(f"  - Type: {lineage.get('feature_type')}")
            print(f"  - Sources: {lineage.get('source_columns')}")
            print(f"  - Business importance: {lineage.get('business_importance')}")
    
    # Engine statistics
    print("\n📊 Engine Statistics:")
    stats = engine.get_engine_statistics()
    print(f"  - Total features: {stats['total_features']}")
    print(f"  - Feature sets: {stats['feature_sets']}")
    print(f"  - Transformations: {stats['transformations']}")
    print(f"  - Creator feature counts: {stats['creator_feature_counts']}")
    print(f"  - Average business importance: {stats['avg_business_importance']:.3f}")


if __name__ == "__main__":
    asyncio.run(demo_feature_engineering_engine())