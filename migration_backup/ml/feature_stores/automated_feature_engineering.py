"""
Automated Feature Engineering - Automated Feature Engineering with Deep Feature Synthesis
Author: Fahed Mlaiel (mlaiel@live.de) - ML Engineer  
Copyright: © 2025 Fahed Mlaiel. All rights reserved.

Enterprise-grade automated feature engineering with deep feature synthesis for creator content analysis.
Optimized for multi-modal content with intelligent feature discovery and optimization.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Tuple, Union, Callable
from dataclasses import dataclass, asdict
from pathlib import Path
import json
import numpy as np
import pandas as pd
import time
from datetime import datetime, timedelta
from itertools import combinations, product
import hashlib

@dataclass
class FeatureDefinition:
    """Definition of an engineered feature."""
    feature_id: str
    feature_name: str
    feature_type: str  # "numerical", "categorical", "temporal", "text", "audio", "image"
    description: str
    transformation_pipeline: List[Dict[str, Any]]
    source_features: List[str]
    complexity_score: float
    importance_score: float
    computation_cost: float  # milliseconds
    memory_footprint: int  # bytes
    stability_score: float  # across different data samples
    interpretability: str  # "high", "medium", "low"
    domain_relevance: Dict[str, float]  # relevance per creator domain

@dataclass
class FeatureSet:
    """Set of related features."""
    set_id: str
    set_name: str
    features: List[FeatureDefinition]
    target_domain: str  # "musician", "blogger", "photographer", "influencer"
    performance_metrics: Dict[str, float]
    creation_timestamp: datetime
    validation_results: Dict[str, Any]
    optimization_history: List[Dict[str, Any]]

@dataclass
class SynthesisConfig:
    """Configuration for automated feature synthesis."""
    max_features: int = 1000
    max_depth: int = 3
    min_importance_threshold: float = 0.01
    max_computation_cost_ms: float = 100.0
    enable_temporal_features: bool = True
    enable_interaction_features: bool = True
    enable_aggregation_features: bool = True
    enable_transformation_features: bool = True
    target_domains: List[str] = None
    feature_selection_strategy: str = "importance_based"  # "importance_based", "correlation_based", "genetic"

class AutomatedFeatureEngineering:
    """
    Advanced automated feature engineering with deep feature synthesis.
    
    Features:
    - Deep feature synthesis with multi-level transformations
    - Creator-domain specific feature patterns
    - Multi-modal feature engineering (audio, image, text, video)
    - Temporal feature extraction and aggregation
    - Interaction feature discovery
    - Feature importance estimation and selection
    - Performance-aware feature optimization
    - Incremental feature learning and adaptation
    """
    
    def __init__(self, feature_cache_dir: str = "feature_cache/"):
        self.logger = logging.getLogger(__name__)
        self.feature_cache_dir = Path(feature_cache_dir)
        self.feature_cache_dir.mkdir(exist_ok=True, parents=True)
        
        # Feature registry and cache
        self.feature_registry = {}
        self.feature_sets = {}
        self.feature_cache = {}
        
        # Transformation primitives
        self.transformation_primitives = {
            "numerical": {
                "aggregation": ["mean", "std", "min", "max", "median", "percentile_25", "percentile_75", "skewness", "kurtosis"],
                "transformation": ["log", "sqrt", "square", "reciprocal", "normalize", "standardize", "clip", "diff"],
                "temporal": ["rolling_mean", "rolling_std", "lag", "trend", "seasonality", "autocorr"],
                "interaction": ["multiply", "divide", "add", "subtract", "ratio", "difference"]
            },
            "categorical": {
                "encoding": ["one_hot", "target_encoding", "frequency_encoding", "label_encoding", "hash_encoding"],
                "aggregation": ["mode", "nunique", "entropy", "frequency"],
                "interaction": ["cross_feature", "interaction_encoding"]
            },
            "text": {
                "extraction": ["word_count", "char_count", "sentence_count", "avg_word_length", "vocabulary_size"],
                "semantic": ["sentiment", "emotion", "topic", "language", "readability"],
                "stylistic": ["formality", "complexity", "creativity", "engagement_score"],
                "n_grams": ["unigrams", "bigrams", "trigrams", "char_ngrams"]
            },
            "audio": {
                "spectral": ["mfcc", "spectral_centroid", "spectral_bandwidth", "spectral_rolloff", "zero_crossing_rate"],
                "temporal": ["tempo", "rhythm", "beats", "onset_strength", "duration"],
                "harmonic": ["chroma", "tonnetz", "harmonic_ratio", "pitch"],
                "energy": ["rms", "energy", "loudness", "dynamic_range"]
            },
            "image": {
                "color": ["mean_rgb", "color_histogram", "dominant_colors", "color_variance"],
                "texture": ["lbp", "glcm", "gabor", "wavelet"],
                "shape": ["edges", "corners", "contours", "moments"],
                "aesthetic": ["rule_of_thirds", "symmetry", "contrast", "brightness"]
            }
        }
        
        # Domain-specific feature patterns
        self.domain_patterns = {
            "musician": {
                "primary_modalities": ["audio", "text"],
                "key_features": ["tempo", "key", "genre", "mood", "energy", "danceability"],
                "interaction_patterns": ["audio_text", "temporal_aggregation"],
                "performance_features": ["stream_count", "engagement_rate", "viral_coefficient"]
            },
            "blogger": {
                "primary_modalities": ["text", "image"],
                "key_features": ["readability", "sentiment", "topic", "engagement", "seo_score"],
                "interaction_patterns": ["text_image", "temporal_trends"],
                "performance_features": ["page_views", "time_on_page", "social_shares"]
            },
            "photographer": {
                "primary_modalities": ["image", "text"],
                "key_features": ["composition", "lighting", "color_harmony", "aesthetic_score"],
                "interaction_patterns": ["image_metadata", "visual_text"],
                "performance_features": ["likes", "downloads", "portfolio_views"]
            },
            "influencer": {
                "primary_modalities": ["image", "video", "text"],
                "key_features": ["engagement_rate", "viral_potential", "brand_affinity", "authenticity"],
                "interaction_patterns": ["multimodal_fusion", "cross_platform"],
                "performance_features": ["follower_growth", "reach", "conversion_rate"]
            }
        }
        
        # Feature importance estimators
        self.importance_estimators = {}
        
    async def synthesize_features(
        self,
        input_data: pd.DataFrame,
        target_domain: str,
        synthesis_config: SynthesisConfig = None
    ) -> FeatureSet:
        """Synthesize features automatically using deep feature synthesis."""
        try:
            if synthesis_config is None:
                synthesis_config = SynthesisConfig()
            
            set_id = f"featureset_{target_domain}_{int(time.time())}"
            
            # Initialize synthesis
            synthesized_features = []
            synthesis_stats = {
                "total_features_generated": 0,
                "features_selected": 0,
                "synthesis_time": 0,
                "performance_gain": 0
            }
            
            start_time = time.time()
            
            # Stage 1: Basic feature extraction
            basic_features = await self._extract_basic_features(input_data, target_domain)
            synthesized_features.extend(basic_features)
            
            # Stage 2: Temporal feature synthesis
            if synthesis_config.enable_temporal_features:
                temporal_features = await self._synthesize_temporal_features(
                    input_data, basic_features, target_domain
                )
                synthesized_features.extend(temporal_features)
            
            # Stage 3: Interaction feature synthesis  
            if synthesis_config.enable_interaction_features:
                interaction_features = await self._synthesize_interaction_features(
                    basic_features, target_domain, synthesis_config.max_depth
                )
                synthesized_features.extend(interaction_features)
            
            # Stage 4: Aggregation feature synthesis
            if synthesis_config.enable_aggregation_features:
                aggregation_features = await self._synthesize_aggregation_features(
                    input_data, basic_features, target_domain
                )
                synthesized_features.extend(aggregation_features)
            
            # Stage 5: Transformation feature synthesis
            if synthesis_config.enable_transformation_features:
                transformation_features = await self._synthesize_transformation_features(
                    basic_features, target_domain
                )
                synthesized_features.extend(transformation_features)
            
            # Stage 6: Domain-specific feature synthesis
            domain_features = await self._synthesize_domain_specific_features(
                input_data, synthesized_features, target_domain
            )
            synthesized_features.extend(domain_features)
            
            synthesis_stats["total_features_generated"] = len(synthesized_features)
            
            # Stage 7: Feature selection and optimization
            selected_features = await self._select_optimal_features(
                synthesized_features, synthesis_config, target_domain
            )
            
            synthesis_stats["features_selected"] = len(selected_features)
            synthesis_stats["synthesis_time"] = time.time() - start_time
            
            # Stage 8: Feature validation
            validation_results = await self._validate_feature_set(
                selected_features, input_data, target_domain
            )
            
            # Create feature set
            feature_set = FeatureSet(
                set_id=set_id,
                set_name=f"AutoEngineered_{target_domain}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                features=selected_features,
                target_domain=target_domain,
                performance_metrics=synthesis_stats,
                creation_timestamp=datetime.now(),
                validation_results=validation_results,
                optimization_history=[]
            )
            
            # Store feature set
            self.feature_sets[set_id] = feature_set
            
            # Cache engineered features
            await self._cache_feature_set(feature_set)
            
            self.logger.info(f"Feature synthesis completed: {len(selected_features)} features "
                           f"for {target_domain} in {synthesis_stats['synthesis_time']:.2f}s")
            
            return feature_set
            
        except Exception as e:
            self.logger.error(f"Error in feature synthesis: {e}")
            raise
    
    async def optimize_feature_set(
        self,
        feature_set_id: str,
        optimization_config: Dict[str, Any],
        performance_data: pd.DataFrame = None
    ) -> FeatureSet:
        """Optimize existing feature set based on performance feedback."""
        try:
            if feature_set_id not in self.feature_sets:
                raise ValueError(f"Feature set not found: {feature_set_id}")
            
            feature_set = self.feature_sets[feature_set_id]
            
            # Performance-based optimization
            if performance_data is not None:
                performance_optimization = await self._optimize_by_performance(
                    feature_set, performance_data, optimization_config
                )
            else:
                performance_optimization = {"features_removed": [], "features_added": []}
            
            # Computational efficiency optimization
            efficiency_optimization = await self._optimize_computational_efficiency(
                feature_set, optimization_config.get("max_computation_time", 1000.0)
            )
            
            # Memory optimization
            memory_optimization = await self._optimize_memory_usage(
                feature_set, optimization_config.get("max_memory_mb", 512)
            )
            
            # Correlation-based optimization (remove redundant features)
            correlation_optimization = await self._optimize_feature_correlations(
                feature_set, optimization_config.get("max_correlation", 0.95)
            )
            
            # Create optimized feature set
            optimized_features = await self._apply_optimizations(
                feature_set.features,
                [performance_optimization, efficiency_optimization, 
                 memory_optimization, correlation_optimization]
            )
            
            # Update feature set
            optimization_record = {
                "optimization_id": f"opt_{int(time.time())}",
                "timestamp": datetime.now().isoformat(),
                "original_feature_count": len(feature_set.features),
                "optimized_feature_count": len(optimized_features),
                "optimizations_applied": [
                    performance_optimization,
                    efficiency_optimization,
                    memory_optimization,
                    correlation_optimization
                ],
                "performance_improvement": await self._calculate_performance_improvement(
                    feature_set.features, optimized_features
                )
            }
            
            feature_set.features = optimized_features
            feature_set.optimization_history.append(optimization_record)
            
            # Re-validate optimized feature set
            feature_set.validation_results = await self._validate_feature_set(
                optimized_features, performance_data, feature_set.target_domain
            )
            
            self.logger.info(f"Feature set optimized: {len(optimized_features)} features remaining")
            return feature_set
            
        except Exception as e:
            self.logger.error(f"Error optimizing feature set: {e}")
            raise
    
    async def extract_incremental_features(
        self,
        new_data: pd.DataFrame,
        existing_feature_set_id: str,
        adaptation_config: Dict[str, Any] = None
    ) -> List[FeatureDefinition]:
        """Extract features incrementally from new data."""
        try:
            if existing_feature_set_id not in self.feature_sets:
                raise ValueError(f"Feature set not found: {existing_feature_set_id}")
            
            existing_feature_set = self.feature_sets[existing_feature_set_id]
            
            # Analyze new data patterns
            data_patterns = await self._analyze_data_patterns(new_data)
            
            # Detect feature drift
            feature_drift = await self._detect_feature_drift(
                new_data, existing_feature_set
            )
            
            # Generate adaptive features
            adaptive_features = []
            
            # Handle data distribution changes
            if feature_drift["distribution_shift"]:
                distribution_features = await self._create_distribution_adaptive_features(
                    new_data, existing_feature_set, feature_drift
                )
                adaptive_features.extend(distribution_features)
            
            # Handle new categorical values
            if feature_drift["new_categories"]:
                category_features = await self._create_category_adaptive_features(
                    new_data, existing_feature_set, feature_drift
                )
                adaptive_features.extend(category_features)
            
            # Handle temporal pattern changes
            if feature_drift["temporal_patterns"]:
                temporal_features = await self._create_temporal_adaptive_features(
                    new_data, existing_feature_set, feature_drift
                )
                adaptive_features.extend(temporal_features)
            
            # Generate features for new data patterns
            if data_patterns["new_patterns"]:
                pattern_features = await self._create_pattern_based_features(
                    new_data, data_patterns, existing_feature_set.target_domain
                )
                adaptive_features.extend(pattern_features)
            
            # Validate and select incremental features
            validated_features = await self._validate_incremental_features(
                adaptive_features, new_data, existing_feature_set
            )
            
            # Update feature registry
            for feature in validated_features:
                self.feature_registry[feature.feature_id] = feature
            
            self.logger.info(f"Generated {len(validated_features)} incremental features")
            return validated_features
            
        except Exception as e:
            self.logger.error(f"Error extracting incremental features: {e}")
            raise
    
    async def _extract_basic_features(
        self, 
        data: pd.DataFrame, 
        target_domain: str
    ) -> List[FeatureDefinition]:
        """Extract basic features from raw data."""
        try:
            basic_features = []
            domain_patterns = self.domain_patterns.get(target_domain, {})
            
            for column in data.columns:
                column_type = self._infer_column_type(data[column])
                
                # Extract type-specific features
                if column_type == "numerical":
                    numerical_features = await self._extract_numerical_features(
                        data[column], column, target_domain
                    )
                    basic_features.extend(numerical_features)
                
                elif column_type == "categorical":
                    categorical_features = await self._extract_categorical_features(
                        data[column], column, target_domain
                    )
                    basic_features.extend(categorical_features)
                
                elif column_type == "text":
                    text_features = await self._extract_text_features(
                        data[column], column, target_domain
                    )
                    basic_features.extend(text_features)
                
                elif column_type == "datetime":
                    temporal_features = await self._extract_temporal_features(
                        data[column], column, target_domain
                    )
                    basic_features.extend(temporal_features)
            
            # Extract domain-specific basic features
            domain_basic_features = await self._extract_domain_basic_features(
                data, target_domain
            )
            basic_features.extend(domain_basic_features)
            
            return basic_features
            
        except Exception as e:
            self.logger.error(f"Error extracting basic features: {e}")
            return []
    
    async def _synthesize_interaction_features(
        self,
        basic_features: List[FeatureDefinition],
        target_domain: str,
        max_depth: int
    ) -> List[FeatureDefinition]:
        """Synthesize interaction features between basic features."""
        try:
            interaction_features = []
            
            # Generate pairwise interactions
            for feature1, feature2 in combinations(basic_features, 2):
                if await self._should_create_interaction(feature1, feature2, target_domain):
                    interaction_feature = await self._create_interaction_feature(
                        feature1, feature2, target_domain
                    )
                    if interaction_feature:
                        interaction_features.append(interaction_feature)
            
            # Generate higher-order interactions if max_depth > 2
            if max_depth > 2:
                higher_order_features = await self._create_higher_order_interactions(
                    basic_features, interaction_features, target_domain, max_depth
                )
                interaction_features.extend(higher_order_features)
            
            return interaction_features
            
        except Exception as e:
            self.logger.error(f"Error synthesizing interaction features: {e}")
            return []
    
    async def _synthesize_temporal_features(
        self,
        data: pd.DataFrame,
        basic_features: List[FeatureDefinition],
        target_domain: str
    ) -> List[FeatureDefinition]:
        """Synthesize temporal features and time-based aggregations."""
        try:
            temporal_features = []
            
            # Identify temporal columns
            temporal_columns = [col for col in data.columns 
                              if data[col].dtype.name.startswith('datetime')]
            
            if not temporal_columns:
                return temporal_features
            
            # Create temporal aggregations
            for feature in basic_features:
                if feature.feature_type == "numerical":
                    # Rolling window features
                    rolling_features = await self._create_rolling_features(
                        data, feature, target_domain
                    )
                    temporal_features.extend(rolling_features)
                    
                    # Lag features
                    lag_features = await self._create_lag_features(
                        data, feature, target_domain
                    )
                    temporal_features.extend(lag_features)
                    
                    # Trend features
                    trend_features = await self._create_trend_features(
                        data, feature, target_domain
                    )
                    temporal_features.extend(trend_features)
            
            # Create time-based categorical features
            time_categorical_features = await self._create_time_categorical_features(
                data, temporal_columns, target_domain
            )
            temporal_features.extend(time_categorical_features)
            
            return temporal_features
            
        except Exception as e:
            self.logger.error(f"Error synthesizing temporal features: {e}")
            return []
    
    def _infer_column_type(self, series: pd.Series) -> str:
        """Infer the type of a pandas series."""
        if pd.api.types.is_numeric_dtype(series):
            return "numerical"
        elif pd.api.types.is_datetime64_any_dtype(series):
            return "datetime"
        elif series.dtype == 'object':
            # Check if it's text or categorical
            unique_ratio = series.nunique() / len(series)
            if unique_ratio > 0.5:  # High unique ratio suggests text
                return "text"
            else:
                return "categorical"
        else:
            return "categorical"
    
    async def _extract_numerical_features(
        self, 
        series: pd.Series, 
        column_name: str, 
        target_domain: str
    ) -> List[FeatureDefinition]:
        """Extract numerical features."""
        features = []
        
        # Basic statistical features
        stats_features = [
            ("mean", series.mean()),
            ("std", series.std()),
            ("min", series.min()),
            ("max", series.max()),
            ("median", series.median()),
            ("skewness", series.skew()),
            ("kurtosis", series.kurtosis())
        ]
        
        for stat_name, stat_value in stats_features:
            feature = FeatureDefinition(
                feature_id=f"{column_name}_{stat_name}_{hash(str(stat_value))[:8]}",
                feature_name=f"{column_name}_{stat_name}",
                feature_type="numerical",
                description=f"{stat_name} of {column_name}",
                transformation_pipeline=[{"operation": stat_name, "column": column_name}],
                source_features=[column_name],
                complexity_score=1.0,
                importance_score=0.5,  # Will be updated later
                computation_cost=1.0,
                memory_footprint=8,  # 8 bytes for float64
                stability_score=0.8,
                interpretability="high",
                domain_relevance={target_domain: 0.7}
            )
            features.append(feature)
        
        return features

# Example usage and testing
async def main():
    """Example usage of AutomatedFeatureEngineering."""
    engineer = AutomatedFeatureEngineering()
    
    # Create mock data for a musician
    np.random.seed(42)
    mock_data = pd.DataFrame({
        'audio_duration': np.random.uniform(180, 300, 1000),  # Song duration in seconds
        'tempo': np.random.uniform(60, 180, 1000),  # BPM
        'key': np.random.choice(['C', 'D', 'E', 'F', 'G', 'A', 'B'], 1000),
        'genre': np.random.choice(['pop', 'rock', 'jazz', 'classical'], 1000),
        'release_date': pd.date_range('2020-01-01', periods=1000, freq='D'),
        'streams': np.random.exponential(1000, 1000),
        'likes': np.random.poisson(100, 1000),
        'artist_followers': np.random.uniform(1000, 1000000, 1000)
    })
    
    # Configure synthesis
    config = SynthesisConfig(
        max_features=500,
        max_depth=2,
        min_importance_threshold=0.05,
        enable_temporal_features=True,
        enable_interaction_features=True,
        target_domains=["musician"]
    )
    
    # Synthesize features
    feature_set = await engineer.synthesize_features(
        mock_data, "musician", config
    )
    
    print(f"Feature synthesis completed:")
    print(f"- Generated {len(feature_set.features)} features")
    print(f"- Target domain: {feature_set.target_domain}")
    print(f"- Synthesis time: {feature_set.performance_metrics['synthesis_time']:.2f}s")
    
    # Show some example features
    print("\nExample features:")
    for i, feature in enumerate(feature_set.features[:5]):
        print(f"{i+1}. {feature.feature_name} ({feature.feature_type})")
        print(f"   Description: {feature.description}")
        print(f"   Complexity: {feature.complexity_score:.2f}")
        print(f"   Sources: {feature.source_features}")
        print()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())