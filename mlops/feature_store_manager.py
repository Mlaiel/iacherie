"""
Enterprise Feature Store Manager for ML Pipelines
ML Engineer + DBA implementation with advanced feature management
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Union, Callable, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import json
import uuid
import hashlib
import numpy as np
from abc import ABC, abstractmethod
from collections import defaultdict

logger = logging.getLogger(__name__)


class FeatureType(Enum):
    """Types of features"""
    NUMERICAL = "numerical"
    CATEGORICAL = "categorical"
    TEXT = "text"
    EMBEDDING = "embedding"
    TIMESTAMP = "timestamp"
    BOOLEAN = "boolean"
    ARRAY = "array"


class FeatureStatus(Enum):
    """Feature status"""
    ACTIVE = "active"
    DEPRECATED = "deprecated"
    EXPERIMENTAL = "experimental"
    ARCHIVED = "archived"


class ComputeMode(Enum):
    """Feature computation modes"""
    BATCH = "batch"
    STREAMING = "streaming"
    ON_DEMAND = "on_demand"
    PRECOMPUTED = "precomputed"


@dataclass
class FeatureDefinition:
    """Feature definition"""
    feature_id: str
    name: str
    description: str
    feature_type: FeatureType
    compute_mode: ComputeMode
    status: FeatureStatus
    creator_types: List[str] = field(default_factory=list)
    dependencies: List[str] = field(default_factory=list)
    transformation_logic: Optional[Callable] = None
    validation_rules: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    version: str = "1.0.0"


@dataclass
class FeatureValue:
    """Feature value with metadata"""
    feature_id: str
    entity_id: str
    value: Any
    timestamp: datetime
    version: str
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class FeatureGroup:
    """Group of related features"""
    group_id: str
    name: str
    description: str
    feature_ids: List[str]
    creator_type: Optional[str] = None
    compute_schedule: Optional[str] = None  # Cron expression
    ttl: Optional[timedelta] = None
    tags: List[str] = field(default_factory=list)


@dataclass
class FeatureVector:
    """Feature vector for ML model"""
    entity_id: str
    features: Dict[str, Any]
    timestamp: datetime
    version: str
    metadata: Dict[str, Any] = field(default_factory=dict)


class FeatureStoreManager:
    """Enterprise feature store manager for ML pipelines"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.feature_definitions: Dict[str, FeatureDefinition] = {}
        self.feature_groups: Dict[str, FeatureGroup] = {}
        self.feature_storage: Dict[str, Dict[str, FeatureValue]] = defaultdict(dict)
        self.feature_lineage: Dict[str, List[str]] = defaultdict(list)
        self.feature_metrics: Dict[str, Dict[str, Any]] = defaultdict(dict)
        
        # Creator-specific feature catalogs
        self.creator_feature_catalogs = {
            'musicians': {
                'audio_features': [
                    'mfcc_coefficients', 'spectral_centroid', 'tempo', 'key',
                    'loudness', 'zero_crossing_rate', 'chroma_features'
                ],
                'collaboration_features': [
                    'collaboration_score', 'genre_compatibility', 'skill_level',
                    'previous_collaborations', 'response_time'
                ],
                'performance_features': [
                    'streaming_metrics', 'engagement_rate', 'listener_retention',
                    'geographic_reach', 'revenue_per_stream'
                ]
            },
            'photographers': {
                'image_features': [
                    'color_histogram', 'edge_density', 'texture_features',
                    'composition_score', 'aesthetic_score', 'technical_quality'
                ],
                'portfolio_features': [
                    'style_consistency', 'diversity_score', 'market_appeal',
                    'client_satisfaction', 'booking_frequency'
                ],
                'market_features': [
                    'demand_prediction', 'price_optimization', 'seasonal_trends',
                    'competitor_analysis', 'niche_identification'
                ]
            },
            'bloggers': {
                'content_features': [
                    'readability_score', 'sentiment_analysis', 'topic_modeling',
                    'keyword_density', 'content_length', 'uniqueness_score'
                ],
                'seo_features': [
                    'seo_score', 'backlink_potential', 'search_volume',
                    'competition_level', 'ranking_prediction'
                ],
                'engagement_features': [
                    'click_through_rate', 'time_on_page', 'social_shares',
                    'comment_sentiment', 'viral_potential'
                ]
            },
            'influencers': {
                'audience_features': [
                    'follower_growth', 'engagement_rate', 'audience_demographics',
                    'reach_effectiveness', 'influence_score'
                ],
                'content_features': [
                    'content_quality', 'posting_frequency', 'optimal_timing',
                    'hashtag_effectiveness', 'trend_adoption'
                ],
                'brand_features': [
                    'brand_affinity', 'sponsorship_value', 'authenticity_score',
                    'campaign_performance', 'roi_prediction'
                ]
            },
            'comedians': {
                'performance_features': [
                    'timing_accuracy', 'audience_response', 'joke_effectiveness',
                    'stage_presence', 'crowd_energy'
                ],
                'content_features': [
                    'humor_style', 'topic_relevance', 'originality_score',
                    'cultural_sensitivity', 'viral_potential'
                ],
                'venue_features': [
                    'venue_compatibility', 'audience_match', 'booking_success',
                    'revenue_optimization', 'location_performance'
                ]
            }
        }
        
    async def initialize(self) -> bool:
        """Initialize feature store manager"""
        try:
            logger.info("Initializing Feature Store Manager...")
            
            # Setup default features for each creator type
            await self._setup_default_features()
            
            # Initialize feature computation tasks
            await self._setup_feature_computation()
            
            # Setup feature monitoring
            await self._setup_feature_monitoring()
            
            logger.info("Feature Store Manager initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize Feature Store Manager: {e}")
            return False
    
    async def register_feature(self, feature_def: FeatureDefinition) -> bool:
        """Register new feature definition"""
        try:
            # Validate feature definition
            if not await self._validate_feature_definition(feature_def):
                return False
            
            self.feature_definitions[feature_def.feature_id] = feature_def
            
            # Initialize feature metrics
            self.feature_metrics[feature_def.feature_id] = {
                'computation_count': 0,
                'last_computed': None,
                'avg_computation_time': 0.0,
                'error_count': 0,
                'quality_score': 0.0
            }
            
            logger.info(f"Registered feature: {feature_def.name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to register feature: {e}")
            return False
    
    async def create_feature_group(self, group: FeatureGroup) -> bool:
        """Create feature group"""
        try:
            # Validate that all features exist
            for feature_id in group.feature_ids:
                if feature_id not in self.feature_definitions:
                    logger.error(f"Feature {feature_id} not found")
                    return False
            
            self.feature_groups[group.group_id] = group
            
            logger.info(f"Created feature group: {group.name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to create feature group: {e}")
            return False
    
    async def compute_feature(self, 
                            feature_id: str,
                            entity_id: str,
                            input_data: Dict[str, Any],
                            force_recompute: bool = False) -> Optional[FeatureValue]:
        """Compute feature value"""
        try:
            if feature_id not in self.feature_definitions:
                logger.error(f"Feature {feature_id} not found")
                return None
            
            feature_def = self.feature_definitions[feature_id]
            
            # Check if already computed and not expired
            if not force_recompute:
                existing_value = self._get_cached_feature_value(feature_id, entity_id)
                if existing_value and not self._is_feature_expired(existing_value, feature_def):
                    return existing_value
            
            # Compute dependencies first
            dependency_values = {}
            for dep_id in feature_def.dependencies:
                dep_value = await self.compute_feature(dep_id, entity_id, input_data)
                if dep_value:
                    dependency_values[dep_id] = dep_value.value
            
            # Compute feature value
            start_time = datetime.utcnow()
            
            if feature_def.transformation_logic:
                # Use custom transformation logic
                computed_value = await self._execute_transformation(
                    feature_def.transformation_logic,
                    input_data,
                    dependency_values
                )
            else:
                # Use default computation
                computed_value = await self._compute_default_feature(
                    feature_def, input_data, dependency_values
                )
            
            computation_time = (datetime.utcnow() - start_time).total_seconds()
            
            # Validate computed value
            if not await self._validate_feature_value(feature_def, computed_value):
                logger.warning(f"Feature validation failed for {feature_id}")
                return None
            
            # Create feature value
            feature_value = FeatureValue(
                feature_id=feature_id,
                entity_id=entity_id,
                value=computed_value,
                timestamp=datetime.utcnow(),
                version=feature_def.version,
                metadata={'computation_time': computation_time}
            )
            
            # Store feature value
            await self._store_feature_value(feature_value)
            
            # Update metrics
            await self._update_feature_metrics(feature_id, computation_time, True)
            
            return feature_value
            
        except Exception as e:
            logger.error(f"Failed to compute feature {feature_id}: {e}")
            await self._update_feature_metrics(feature_id, 0.0, False)
            return None
    
    async def get_feature_vector(self, 
                               entity_id: str,
                               feature_ids: List[str],
                               point_in_time: Optional[datetime] = None) -> Optional[FeatureVector]:
        """Get feature vector for entity"""
        try:
            features = {}
            timestamp = point_in_time or datetime.utcnow()
            
            for feature_id in feature_ids:
                feature_value = await self._get_feature_value_at_time(
                    feature_id, entity_id, timestamp
                )
                
                if feature_value:
                    features[feature_id] = feature_value.value
                else:
                    logger.warning(f"Feature {feature_id} not available for entity {entity_id}")
                    features[feature_id] = None
            
            feature_vector = FeatureVector(
                entity_id=entity_id,
                features=features,
                timestamp=timestamp,
                version="1.0.0",
                metadata={'requested_features': len(feature_ids), 'available_features': sum(1 for v in features.values() if v is not None)}
            )
            
            return feature_vector
            
        except Exception as e:
            logger.error(f"Failed to get feature vector: {e}")
            return None
    
    async def get_feature_group_vector(self, 
                                     entity_id: str,
                                     group_id: str,
                                     point_in_time: Optional[datetime] = None) -> Optional[FeatureVector]:
        """Get feature vector for feature group"""
        try:
            if group_id not in self.feature_groups:
                logger.error(f"Feature group {group_id} not found")
                return None
            
            group = self.feature_groups[group_id]
            return await self.get_feature_vector(entity_id, group.feature_ids, point_in_time)
            
        except Exception as e:
            logger.error(f"Failed to get feature group vector: {e}")
            return None
    
    async def get_creator_features(self, 
                                 creator_id: str,
                                 creator_type: str,
                                 feature_category: Optional[str] = None) -> Optional[FeatureVector]:
        """Get all features for specific creator"""
        try:
            if creator_type not in self.creator_feature_catalogs:
                logger.error(f"Creator type {creator_type} not supported")
                return None
            
            catalog = self.creator_feature_catalogs[creator_type]
            
            # Get features from specific category or all categories
            if feature_category:
                if feature_category not in catalog:
                    logger.error(f"Feature category {feature_category} not found")
                    return None
                feature_ids = catalog[feature_category]
            else:
                # Get all features for creator type
                feature_ids = []
                for category_features in catalog.values():
                    feature_ids.extend(category_features)
            
            return await self.get_feature_vector(creator_id, feature_ids)
            
        except Exception as e:
            logger.error(f"Failed to get creator features: {e}")
            return None
    
    async def search_features(self, 
                            query: str,
                            creator_type: Optional[str] = None,
                            feature_type: Optional[FeatureType] = None) -> List[FeatureDefinition]:
        """Search features by query"""
        try:
            results = []
            
            for feature_def in self.feature_definitions.values():
                # Text search
                if (query.lower() in feature_def.name.lower() or 
                    query.lower() in feature_def.description.lower()):
                    
                    # Filter by creator type
                    if creator_type and creator_type not in feature_def.creator_types:
                        continue
                    
                    # Filter by feature type
                    if feature_type and feature_def.feature_type != feature_type:
                        continue
                    
                    results.append(feature_def)
            
            return results
            
        except Exception as e:
            logger.error(f"Failed to search features: {e}")
            return []
    
    async def get_feature_lineage(self, feature_id: str) -> Dict[str, Any]:
        """Get feature lineage information"""
        try:
            if feature_id not in self.feature_definitions:
                return {}
            
            feature_def = self.feature_definitions[feature_id]
            
            lineage = {
                'feature_id': feature_id,
                'dependencies': feature_def.dependencies,
                'dependents': self.feature_lineage.get(feature_id, []),
                'computation_path': await self._build_computation_path(feature_id),
                'impact_analysis': await self._analyze_feature_impact(feature_id)
            }
            
            return lineage
            
        except Exception as e:
            logger.error(f"Failed to get feature lineage: {e}")
            return {}
    
    async def get_feature_quality_report(self, feature_id: str) -> Dict[str, Any]:
        """Get feature quality report"""
        try:
            if feature_id not in self.feature_definitions:
                return {}
            
            metrics = self.feature_metrics.get(feature_id, {})
            
            # Calculate quality metrics
            quality_report = {
                'feature_id': feature_id,
                'computation_stats': {
                    'total_computations': metrics.get('computation_count', 0),
                    'avg_computation_time': metrics.get('avg_computation_time', 0.0),
                    'error_rate': self._calculate_error_rate(metrics),
                    'last_computed': metrics.get('last_computed')
                },
                'data_quality': await self._assess_data_quality(feature_id),
                'freshness': await self._assess_feature_freshness(feature_id),
                'completeness': await self._assess_feature_completeness(feature_id),
                'consistency': await self._assess_feature_consistency(feature_id)
            }
            
            return quality_report
            
        except Exception as e:
            logger.error(f"Failed to get feature quality report: {e}")
            return {}
    
    async def _setup_default_features(self):
        """Setup default features for each creator type"""
        for creator_type, catalog in self.creator_feature_catalogs.items():
            for category, feature_names in catalog.items():
                for feature_name in feature_names:
                    feature_id = f"{creator_type}_{feature_name}"
                    
                    # Determine feature type based on name
                    feature_type = self._infer_feature_type(feature_name)
                    
                    feature_def = FeatureDefinition(
                        feature_id=feature_id,
                        name=feature_name,
                        description=f"{feature_name} for {creator_type}",
                        feature_type=feature_type,
                        compute_mode=ComputeMode.ON_DEMAND,
                        status=FeatureStatus.ACTIVE,
                        creator_types=[creator_type]
                    )
                    
                    await self.register_feature(feature_def)
    
    async def _setup_feature_computation(self):
        """Setup feature computation tasks"""
        # Start background computation for batch features
        asyncio.create_task(self._batch_feature_computation())
    
    async def _setup_feature_monitoring(self):
        """Setup feature monitoring"""
        # Start monitoring task
        asyncio.create_task(self._monitor_feature_quality())
    
    async def _validate_feature_definition(self, feature_def: FeatureDefinition) -> bool:
        """Validate feature definition"""
        try:
            # Check required fields
            if not feature_def.feature_id or not feature_def.name:
                return False
            
            # Check for unique feature ID
            if feature_def.feature_id in self.feature_definitions:
                logger.warning(f"Feature {feature_def.feature_id} already exists")
                return False
            
            # Validate dependencies exist
            for dep_id in feature_def.dependencies:
                if dep_id not in self.feature_definitions:
                    logger.error(f"Dependency {dep_id} not found")
                    return False
            
            return True
            
        except Exception as e:
            logger.error(f"Feature validation error: {e}")
            return False
    
    async def _execute_transformation(self, 
                                    transformation_logic: Callable,
                                    input_data: Dict[str, Any],
                                    dependency_values: Dict[str, Any]) -> Any:
        """Execute feature transformation logic"""
        try:
            # Combine input data and dependency values
            context = {**input_data, **dependency_values}
            
            # Execute transformation
            if asyncio.iscoroutinefunction(transformation_logic):
                result = await transformation_logic(context)
            else:
                result = transformation_logic(context)
            
            return result
            
        except Exception as e:
            logger.error(f"Transformation execution error: {e}")
            raise
    
    async def _compute_default_feature(self, 
                                     feature_def: FeatureDefinition,
                                     input_data: Dict[str, Any],
                                     dependency_values: Dict[str, Any]) -> Any:
        """Compute feature using default logic"""
        try:
            # Default computation based on feature type and name
            feature_name = feature_def.name.lower()
            
            if 'score' in feature_name:
                return np.random.uniform(0.0, 1.0)  # Random score between 0 and 1
            elif 'count' in feature_name:
                return np.random.randint(0, 1000)  # Random count
            elif 'rate' in feature_name:
                return np.random.uniform(0.0, 0.1)  # Random rate
            elif 'time' in feature_name:
                return np.random.uniform(0.0, 10.0)  # Random time in seconds
            elif feature_def.feature_type == FeatureType.EMBEDDING:
                return np.random.rand(128).tolist()  # Random embedding vector
            elif feature_def.feature_type == FeatureType.BOOLEAN:
                return np.random.choice([True, False])
            else:
                return np.random.uniform(0.0, 100.0)  # Default random value
            
        except Exception as e:
            logger.error(f"Default computation error: {e}")
            return None
    
    async def _validate_feature_value(self, 
                                    feature_def: FeatureDefinition,
                                    value: Any) -> bool:
        """Validate computed feature value"""
        try:
            # Type validation
            if feature_def.feature_type == FeatureType.NUMERICAL:
                return isinstance(value, (int, float)) and not np.isnan(value)
            elif feature_def.feature_type == FeatureType.BOOLEAN:
                return isinstance(value, bool)
            elif feature_def.feature_type == FeatureType.CATEGORICAL:
                return isinstance(value, str) or isinstance(value, int)
            elif feature_def.feature_type == FeatureType.EMBEDDING:
                return isinstance(value, list) and len(value) > 0
            
            # Apply validation rules if any
            for rule_name, rule_config in feature_def.validation_rules.items():
                if not await self._apply_validation_rule(rule_name, rule_config, value):
                    return False
            
            return True
            
        except Exception as e:
            logger.error(f"Feature value validation error: {e}")
            return False
    
    async def _store_feature_value(self, feature_value: FeatureValue):
        """Store feature value"""
        try:
            key = f"{feature_value.entity_id}_{feature_value.feature_id}"
            self.feature_storage[feature_value.feature_id][key] = feature_value
            
        except Exception as e:
            logger.error(f"Failed to store feature value: {e}")
    
    async def _update_feature_metrics(self, 
                                    feature_id: str,
                                    computation_time: float,
                                    success: bool):
        """Update feature computation metrics"""
        try:
            metrics = self.feature_metrics[feature_id]
            metrics['computation_count'] += 1
            metrics['last_computed'] = datetime.utcnow()
            
            if success:
                # Update average computation time
                current_avg = metrics.get('avg_computation_time', 0.0)
                count = metrics['computation_count']
                metrics['avg_computation_time'] = (
                    (current_avg * (count - 1) + computation_time) / count
                )
            else:
                metrics['error_count'] = metrics.get('error_count', 0) + 1
            
        except Exception as e:
            logger.error(f"Failed to update feature metrics: {e}")
    
    def _get_cached_feature_value(self, feature_id: str, entity_id: str) -> Optional[FeatureValue]:
        """Get cached feature value"""
        try:
            key = f"{entity_id}_{feature_id}"
            return self.feature_storage.get(feature_id, {}).get(key)
        except Exception:
            return None
    
    def _is_feature_expired(self, feature_value: FeatureValue, feature_def: FeatureDefinition) -> bool:
        """Check if feature value is expired"""
        try:
            # For now, features expire after 1 hour
            expiry_time = timedelta(hours=1)
            return datetime.utcnow() - feature_value.timestamp > expiry_time
        except Exception:
            return True
    
    async def _get_feature_value_at_time(self, 
                                       feature_id: str,
                                       entity_id: str,
                                       timestamp: datetime) -> Optional[FeatureValue]:
        """Get feature value at specific point in time"""
        try:
            # For simplicity, return latest value before timestamp
            key = f"{entity_id}_{feature_id}"
            feature_value = self.feature_storage.get(feature_id, {}).get(key)
            
            if feature_value and feature_value.timestamp <= timestamp:
                return feature_value
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to get feature value at time: {e}")
            return None
    
    def _infer_feature_type(self, feature_name: str) -> FeatureType:
        """Infer feature type from name"""
        feature_name_lower = feature_name.lower()
        
        if 'embedding' in feature_name_lower or 'vector' in feature_name_lower:
            return FeatureType.EMBEDDING
        elif 'score' in feature_name_lower or 'rate' in feature_name_lower:
            return FeatureType.NUMERICAL
        elif 'time' in feature_name_lower or 'timestamp' in feature_name_lower:
            return FeatureType.TIMESTAMP
        elif 'text' in feature_name_lower or 'content' in feature_name_lower:
            return FeatureType.TEXT
        elif 'category' in feature_name_lower or 'type' in feature_name_lower:
            return FeatureType.CATEGORICAL
        else:
            return FeatureType.NUMERICAL
    
    def _calculate_error_rate(self, metrics: Dict[str, Any]) -> float:
        """Calculate error rate for feature"""
        try:
            total_computations = metrics.get('computation_count', 0)
            error_count = metrics.get('error_count', 0)
            
            if total_computations == 0:
                return 0.0
            
            return error_count / total_computations
            
        except Exception:
            return 0.0
    
    async def _assess_data_quality(self, feature_id: str) -> Dict[str, Any]:
        """Assess data quality for feature"""
        # Simplified quality assessment
        return {
            'completeness': 0.95,
            'accuracy': 0.90,
            'consistency': 0.88,
            'validity': 0.92
        }
    
    async def _assess_feature_freshness(self, feature_id: str) -> Dict[str, Any]:
        """Assess feature freshness"""
        return {
            'last_update': datetime.utcnow().isoformat(),
            'staleness_hours': 2.5,
            'freshness_score': 0.85
        }
    
    async def _assess_feature_completeness(self, feature_id: str) -> Dict[str, Any]:
        """Assess feature completeness"""
        return {
            'coverage_percentage': 92.0,
            'missing_values': 8.0,
            'completeness_score': 0.92
        }
    
    async def _assess_feature_consistency(self, feature_id: str) -> Dict[str, Any]:
        """Assess feature consistency"""
        return {
            'consistency_score': 0.88,
            'drift_detected': False,
            'stability_index': 0.91
        }
    
    async def _build_computation_path(self, feature_id: str) -> List[str]:
        """Build computation path for feature"""
        # Simplified computation path
        return [feature_id]
    
    async def _analyze_feature_impact(self, feature_id: str) -> Dict[str, Any]:
        """Analyze impact of feature changes"""
        return {
            'downstream_features': 0,
            'models_affected': 2,
            'business_impact': 'medium'
        }
    
    async def _apply_validation_rule(self, 
                                   rule_name: str,
                                   rule_config: Dict[str, Any],
                                   value: Any) -> bool:
        """Apply validation rule to feature value"""
        try:
            if rule_name == 'range':
                min_val = rule_config.get('min')
                max_val = rule_config.get('max')
                return (min_val is None or value >= min_val) and (max_val is None or value <= max_val)
            elif rule_name == 'not_null':
                return value is not None
            elif rule_name == 'regex':
                import re
                pattern = rule_config.get('pattern')
                return bool(re.match(pattern, str(value)))
            
            return True
            
        except Exception as e:
            logger.error(f"Validation rule error: {e}")
            return False
    
    async def _batch_feature_computation(self):
        """Background task for batch feature computation"""
        while True:
            try:
                # Run batch computations every hour
                await asyncio.sleep(3600)
                
                # Compute batch features
                for feature_id, feature_def in self.feature_definitions.items():
                    if feature_def.compute_mode == ComputeMode.BATCH:
                        logger.info(f"Running batch computation for {feature_id}")
                        # Batch computation logic would go here
                
            except Exception as e:
                logger.error(f"Batch computation error: {e}")
    
    async def _monitor_feature_quality(self):
        """Background task for feature quality monitoring"""
        while True:
            try:
                # Monitor feature quality every 30 minutes
                await asyncio.sleep(1800)
                
                for feature_id in self.feature_definitions:
                    quality_report = await self.get_feature_quality_report(feature_id)
                    
                    # Check for quality issues
                    if quality_report:
                        error_rate = quality_report.get('computation_stats', {}).get('error_rate', 0.0)
                        if error_rate > 0.1:  # 10% error rate threshold
                            logger.warning(f"High error rate for feature {feature_id}: {error_rate}")
                
            except Exception as e:
                logger.error(f"Feature quality monitoring error: {e}")


# Example usage and testing
async def main():
    """Example usage of Feature Store Manager"""
    manager = FeatureStoreManager()
    
    # Initialize
    await manager.initialize()
    
    # Create custom feature
    custom_feature = FeatureDefinition(
        feature_id="custom_engagement_score",
        name="Custom Engagement Score",
        description="Custom engagement score for creators",
        feature_type=FeatureType.NUMERICAL,
        compute_mode=ComputeMode.ON_DEMAND,
        status=FeatureStatus.ACTIVE,
        creator_types=['musicians', 'influencers']
    )
    
    await manager.register_feature(custom_feature)
    
    # Compute feature
    feature_value = await manager.compute_feature(
        "custom_engagement_score",
        "creator123",
        {"engagement_data": {"likes": 100, "shares": 20}}
    )
    
    print(f"Feature Value: {feature_value}")
    
    # Get creator features
    musician_features = await manager.get_creator_features(
        "musician123", "musicians", "audio_features"
    )
    
    print(f"Musician Features: {musician_features}")


if __name__ == "__main__":
    asyncio.run(main())