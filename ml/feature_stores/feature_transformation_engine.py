"""🔧 Feature Transformation Engine - Enterprise ML Infrastructure
================================================================
Module: ml/feature_stores/feature_transformation_engine.py
Author: Fahed Mlaiel (mlaiel@live.de)
================================================================

⚠️  PROPRIÉTÉ INTELLECTUELLE EXCLUSIVE - FAHED MLAIEL ⚠️
(c) 2025 Fahed Mlaiel. Tous droits réservés.
Contact: mlaiel@live.de

🎯 FEATURE TRANSFORMATION ENGINE
Advanced feature transformations including scaling, encoding, and binning
- Multi-modal feature transformations
- Creator-specific transformation pipelines
- Real-time and batch transformation
- Performance optimization and caching
"""

import asyncio
import logging
import time
import uuid
import pickle
import json
from typing import Dict, List, Optional, Any, Union, Tuple, Callable
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
import numpy as np
import pandas as pd
from sklearn.preprocessing import (
    StandardScaler, MinMaxScaler, RobustScaler, 
    LabelEncoder, OneHotEncoder, OrdinalEncoder,
    PowerTransformer, QuantileTransformer
)
from sklearn.feature_selection import SelectKBest, f_classif
import threading
from concurrent.futures import ThreadPoolExecutor

logger = logging.getLogger(__name__)


class TransformationType(Enum):
    """Types of feature transformations"""
    SCALING = "scaling"
    ENCODING = "encoding"
    BINNING = "binning"
    NORMALIZATION = "normalization"
    DIMENSIONALITY_REDUCTION = "dimensionality_reduction"
    FEATURE_SELECTION = "feature_selection"
    CREATOR_SPECIFIC = "creator_specific"
    TEMPORAL = "temporal"
    TEXT_PROCESSING = "text_processing"
    AUDIO_PROCESSING = "audio_processing"


class CreatorType(Enum):
    """Creator types for specialized transformations"""
    MUSICIAN = "musician"
    BLOGGER = "blogger"
    PHOTOGRAPHER = "photographer"
    INFLUENCER = "influencer"
    COMEDIAN = "comedian"
    GENERIC = "generic"


class ProcessingMode(Enum):
    """Processing modes"""
    REAL_TIME = "real_time"
    BATCH = "batch"
    STREAMING = "streaming"


@dataclass
class TransformationStep:
    """Single transformation step"""
    step_id: str
    transformation_type: TransformationType
    transformer: Any
    parameters: Dict[str, Any] = field(default_factory=dict)
    input_columns: List[str] = field(default_factory=list)
    output_columns: List[str] = field(default_factory=list)
    creator_specific: bool = False
    enabled: bool = True


@dataclass
class TransformationPipeline:
    """Feature transformation pipeline"""
    pipeline_id: str
    name: str
    creator_type: CreatorType
    steps: List[TransformationStep] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    version: str = "1.0.0"
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class TransformationResult:
    """Transformation result"""
    original_features: Dict[str, Any]
    transformed_features: Dict[str, Any]
    transformation_time: float
    pipeline_id: str
    applied_steps: List[str]
    metadata: Dict[str, Any] = field(default_factory=dict)


class FeatureTransformationEngine:
    """Enterprise Feature Transformation Engine"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        
        # Pipeline storage
        self.pipelines: Dict[str, TransformationPipeline] = {}
        self.fitted_transformers: Dict[str, Dict[str, Any]] = {}
        
        # Configuration
        self.cache_enabled = self.config.get('cache_enabled', True)
        self.cache_ttl = self.config.get('cache_ttl', 3600)
        self.max_workers = self.config.get('max_workers', 4)
        self.enable_parallel_processing = self.config.get('enable_parallel_processing', True)
        
        # Performance tracking
        self.transformation_metrics = {
            'total_transformations': 0,
            'successful_transformations': 0,
            'failed_transformations': 0,
            'average_processing_time': 0.0,
            'cache_hits': 0,
            'cache_misses': 0
        }
        
        # Caching
        self.transformation_cache: Dict[str, Tuple[Any, datetime]] = {}
        
        # Thread pool for parallel processing
        self.executor = ThreadPoolExecutor(max_workers=self.max_workers)
        
        logger.info("🔧 Feature Transformation Engine initialized")
    
    async def create_pipeline(
        self,
        name: str,
        creator_type: CreatorType,
        steps: List[Dict[str, Any]],
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """Create a new transformation pipeline"""
        try:
            pipeline_id = str(uuid.uuid4())
            
            # Create transformation steps
            transformation_steps = []
            for i, step_config in enumerate(steps):
                step = await self._create_transformation_step(
                    f"{pipeline_id}_step_{i}",
                    step_config
                )
                transformation_steps.append(step)
            
            # Create pipeline
            pipeline = TransformationPipeline(
                pipeline_id=pipeline_id,
                name=name,
                creator_type=creator_type,
                steps=transformation_steps,
                metadata=metadata or {}
            )
            
            self.pipelines[pipeline_id] = pipeline
            
            logger.info(f"✅ Created transformation pipeline: {name} ({pipeline_id})")
            return pipeline_id
            
        except Exception as e:
            logger.error(f"❌ Error creating pipeline: {e}")
            raise
    
    async def fit_pipeline(
        self,
        pipeline_id: str,
        training_data: pd.DataFrame
    ) -> bool:
        """Fit transformation pipeline on training data"""
        try:
            if pipeline_id not in self.pipelines:
                raise ValueError(f"Pipeline {pipeline_id} not found")
            
            pipeline = self.pipelines[pipeline_id]
            fitted_transformers = {}
            
            # Process data through each step
            current_data = training_data.copy()
            
            for step in pipeline.steps:
                if not step.enabled:
                    continue
                
                # Fit transformer on current data
                transformer = step.transformer
                
                if step.input_columns:
                    # Use specific columns
                    input_data = current_data[step.input_columns]
                else:
                    # Use all columns
                    input_data = current_data
                
                # Fit the transformer
                if hasattr(transformer, 'fit'):
                    transformer.fit(input_data)
                
                # Transform the data for next step
                if hasattr(transformer, 'transform'):
                    transformed_data = transformer.transform(input_data)
                    
                    # Update current data
                    if step.output_columns:
                        for i, col in enumerate(step.output_columns):
                            if hasattr(transformed_data, 'shape') and len(transformed_data.shape) > 1:
                                current_data[col] = transformed_data[:, i] if i < transformed_data.shape[1] else transformed_data[:, 0]
                            else:
                                current_data[col] = transformed_data
                    else:
                        # Replace input columns
                        if isinstance(transformed_data, np.ndarray):
                            for i, col in enumerate(step.input_columns or current_data.columns):
                                if i < transformed_data.shape[1] if len(transformed_data.shape) > 1 else 1:
                                    current_data[col] = transformed_data[:, i] if len(transformed_data.shape) > 1 else transformed_data
                
                # Store fitted transformer
                fitted_transformers[step.step_id] = {
                    'transformer': transformer,
                    'input_columns': step.input_columns,
                    'output_columns': step.output_columns
                }
            
            # Store fitted transformers
            self.fitted_transformers[pipeline_id] = fitted_transformers
            
            logger.info(f"✅ Fitted pipeline: {pipeline_id}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error fitting pipeline {pipeline_id}: {e}")
            return False
    
    async def transform_features(
        self,
        pipeline_id: str,
        features: Union[Dict[str, Any], pd.DataFrame],
        processing_mode: ProcessingMode = ProcessingMode.REAL_TIME
    ) -> TransformationResult:
        """Transform features using fitted pipeline"""
        try:
            start_time = time.time()
            
            if pipeline_id not in self.pipelines:
                raise ValueError(f"Pipeline {pipeline_id} not found")
            
            if pipeline_id not in self.fitted_transformers:
                raise ValueError(f"Pipeline {pipeline_id} not fitted")
            
            # Check cache
            cache_key = None
            if self.cache_enabled and processing_mode == ProcessingMode.REAL_TIME:
                cache_key = self._generate_cache_key(pipeline_id, features)
                cached_result = self._get_cached_result(cache_key)
                if cached_result:
                    self.transformation_metrics['cache_hits'] += 1
                    return cached_result
                self.transformation_metrics['cache_misses'] += 1
            
            # Convert to DataFrame if needed
            if isinstance(features, dict):
                original_features = features.copy()
                df = pd.DataFrame([features])
            else:
                original_features = features.to_dict('records')[0] if len(features) > 0 else {}
                df = features.copy()
            
            pipeline = self.pipelines[pipeline_id]
            fitted_transformers = self.fitted_transformers[pipeline_id]
            applied_steps = []
            
            # Apply transformations
            current_data = df.copy()
            
            for step in pipeline.steps:
                if not step.enabled or step.step_id not in fitted_transformers:
                    continue
                
                fitted_transformer_info = fitted_transformers[step.step_id]
                transformer = fitted_transformer_info['transformer']
                input_columns = fitted_transformer_info['input_columns']
                output_columns = fitted_transformer_info['output_columns']
                
                # Apply transformation
                if input_columns:
                    input_data = current_data[input_columns]
                else:
                    input_data = current_data
                
                if hasattr(transformer, 'transform'):
                    transformed_data = transformer.transform(input_data)
                    
                    # Update current data
                    if output_columns:
                        for i, col in enumerate(output_columns):
                            if hasattr(transformed_data, 'shape') and len(transformed_data.shape) > 1:
                                current_data[col] = transformed_data[:, i] if i < transformed_data.shape[1] else transformed_data[:, 0]
                            else:
                                current_data[col] = transformed_data
                    else:
                        # Replace input columns
                        if isinstance(transformed_data, np.ndarray):
                            for i, col in enumerate(input_columns or current_data.columns):
                                if len(transformed_data.shape) > 1:
                                    if i < transformed_data.shape[1]:
                                        current_data[col] = transformed_data[:, i]
                                else:
                                    current_data[col] = transformed_data
                
                applied_steps.append(step.step_id)
            
            # Create result
            transformed_features = current_data.iloc[0].to_dict() if len(current_data) > 0 else {}
            processing_time = time.time() - start_time
            
            result = TransformationResult(
                original_features=original_features,
                transformed_features=transformed_features,
                transformation_time=processing_time,
                pipeline_id=pipeline_id,
                applied_steps=applied_steps,
                metadata={
                    'processing_mode': processing_mode.value,
                    'creator_type': pipeline.creator_type.value,
                    'pipeline_version': pipeline.version
                }
            )
            
            # Cache result
            if cache_key and self.cache_enabled:
                self._cache_result(cache_key, result)
            
            # Update metrics
            await self._update_metrics(processing_time, True)
            
            return result
            
        except Exception as e:
            logger.error(f"❌ Error transforming features: {e}")
            await self._update_metrics(0, False)
            raise
    
    async def transform_batch(
        self,
        pipeline_id: str,
        features_batch: List[Dict[str, Any]]
    ) -> List[TransformationResult]:
        """Transform batch of features"""
        try:
            if not self.enable_parallel_processing:
                # Sequential processing
                results = []
                for features in features_batch:
                    result = await self.transform_features(
                        pipeline_id, features, ProcessingMode.BATCH
                    )
                    results.append(result)
                return results
            
            # Parallel processing
            loop = asyncio.get_event_loop()
            tasks = []
            
            for features in features_batch:
                task = loop.run_in_executor(
                    self.executor,
                    self._transform_sync,
                    pipeline_id,
                    features
                )
                tasks.append(task)
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Filter out exceptions
            valid_results = [
                result for result in results
                if isinstance(result, TransformationResult)
            ]
            
            return valid_results
            
        except Exception as e:
            logger.error(f"❌ Error in batch transformation: {e}")
            raise
    
    async def create_creator_specific_pipeline(
        self,
        creator_type: CreatorType,
        name: Optional[str] = None
    ) -> str:
        """Create creator-specific transformation pipeline"""
        try:
            pipeline_name = name or f"{creator_type.value}_pipeline"
            
            # Define creator-specific transformations
            steps = await self._get_creator_specific_steps(creator_type)
            
            return await self.create_pipeline(
                pipeline_name,
                creator_type,
                steps,
                {'auto_generated': True, 'creator_optimized': True}
            )
            
        except Exception as e:
            logger.error(f"❌ Error creating creator-specific pipeline: {e}")
            raise
    
    async def optimize_pipeline(
        self,
        pipeline_id: str,
        validation_data: pd.DataFrame,
        target_column: str
    ) -> bool:
        """Optimize pipeline performance"""
        try:
            if pipeline_id not in self.pipelines:
                raise ValueError(f"Pipeline {pipeline_id} not found")
            
            pipeline = self.pipelines[pipeline_id]
            
            # Feature selection optimization
            await self._optimize_feature_selection(pipeline, validation_data, target_column)
            
            # Parameter optimization
            await self._optimize_parameters(pipeline, validation_data)
            
            # Re-fit with optimized pipeline
            await self.fit_pipeline(pipeline_id, validation_data)
            
            pipeline.updated_at = datetime.utcnow()
            
            logger.info(f"✅ Optimized pipeline: {pipeline_id}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error optimizing pipeline: {e}")
            return False
    
    async def _create_transformation_step(
        self,
        step_id: str,
        step_config: Dict[str, Any]
    ) -> TransformationStep:
        """Create a transformation step"""
        try:
            transformation_type = TransformationType(step_config['type'])
            
            # Create appropriate transformer
            if transformation_type == TransformationType.SCALING:
                method = step_config.get('method', 'standard')
                if method == 'standard':
                    transformer = StandardScaler()
                elif method == 'minmax':
                    transformer = MinMaxScaler()
                elif method == 'robust':
                    transformer = RobustScaler()
                else:
                    transformer = StandardScaler()
            
            elif transformation_type == TransformationType.ENCODING:
                method = step_config.get('method', 'onehot')
                if method == 'onehot':
                    transformer = OneHotEncoder(sparse_output=False, handle_unknown='ignore')
                elif method == 'label':
                    transformer = LabelEncoder()
                elif method == 'ordinal':
                    transformer = OrdinalEncoder()
                else:
                    transformer = OneHotEncoder(sparse_output=False, handle_unknown='ignore')
            
            elif transformation_type == TransformationType.NORMALIZATION:
                method = step_config.get('method', 'quantile')
                if method == 'power':
                    transformer = PowerTransformer()
                elif method == 'quantile':
                    transformer = QuantileTransformer()
                else:
                    transformer = QuantileTransformer()
            
            elif transformation_type == TransformationType.FEATURE_SELECTION:
                k = step_config.get('k', 10)
                transformer = SelectKBest(score_func=f_classif, k=k)
            
            else:
                # Custom transformer
                transformer = step_config.get('transformer')
                if not transformer:
                    raise ValueError(f"No transformer specified for type {transformation_type}")
            
            return TransformationStep(
                step_id=step_id,
                transformation_type=transformation_type,
                transformer=transformer,
                parameters=step_config.get('parameters', {}),
                input_columns=step_config.get('input_columns', []),
                output_columns=step_config.get('output_columns', []),
                creator_specific=step_config.get('creator_specific', False),
                enabled=step_config.get('enabled', True)
            )
            
        except Exception as e:
            logger.error(f"❌ Error creating transformation step: {e}")
            raise
    
    async def _get_creator_specific_steps(self, creator_type: CreatorType) -> List[Dict[str, Any]]:
        """Get creator-specific transformation steps"""
        try:
            base_steps = [
                {
                    'type': 'scaling',
                    'method': 'standard',
                    'input_columns': []  # Will be filled automatically
                }
            ]
            
            if creator_type == CreatorType.MUSICIAN:
                base_steps.extend([
                    {
                        'type': 'audio_processing',
                        'method': 'spectral_features',
                        'parameters': {'n_fft': 2048, 'hop_length': 512}
                    },
                    {
                        'type': 'temporal',
                        'method': 'rhythm_analysis',
                        'parameters': {'tempo_range': [60, 200]}
                    }
                ])
            
            elif creator_type == CreatorType.BLOGGER:
                base_steps.extend([
                    {
                        'type': 'text_processing',
                        'method': 'tfidf',
                        'parameters': {'max_features': 5000}
                    },
                    {
                        'type': 'text_processing',
                        'method': 'sentiment_analysis',
                        'parameters': {}
                    }
                ])
            
            elif creator_type == CreatorType.PHOTOGRAPHER:
                base_steps.extend([
                    {
                        'type': 'creator_specific',
                        'method': 'image_features',
                        'parameters': {'extract_color': True, 'extract_texture': True}
                    },
                    {
                        'type': 'creator_specific',
                        'method': 'composition_analysis',
                        'parameters': {'rule_of_thirds': True}
                    }
                ])
            
            elif creator_type == CreatorType.INFLUENCER:
                base_steps.extend([
                    {
                        'type': 'creator_specific',
                        'method': 'engagement_features',
                        'parameters': {'include_viral_metrics': True}
                    },
                    {
                        'type': 'temporal',
                        'method': 'trend_analysis',
                        'parameters': {'window_size': 30}
                    }
                ])
            
            return base_steps
            
        except Exception as e:
            logger.error(f"❌ Error getting creator-specific steps: {e}")
            return []
    
    def _transform_sync(
        self,
        pipeline_id: str,
        features: Dict[str, Any]
    ) -> TransformationResult:
        """Synchronous transformation for thread pool"""
        try:
            # This would normally call the async version, but for thread pool we need sync
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            try:
                result = loop.run_until_complete(
                    self.transform_features(pipeline_id, features, ProcessingMode.BATCH)
                )
                return result
            finally:
                loop.close()
                
        except Exception as e:
            logger.error(f"❌ Error in sync transformation: {e}")
            raise
    
    def _generate_cache_key(self, pipeline_id: str, features: Any) -> str:
        """Generate cache key for transformation"""
        try:
            # Create a deterministic hash of pipeline and features
            features_str = json.dumps(features, sort_keys=True, default=str)
            combined = f"{pipeline_id}:{features_str}"
            return str(hash(combined))
        except:
            return f"{pipeline_id}:{time.time()}"
    
    def _get_cached_result(self, cache_key: str) -> Optional[TransformationResult]:
        """Get cached transformation result"""
        try:
            if cache_key in self.transformation_cache:
                result, timestamp = self.transformation_cache[cache_key]
                
                # Check if cache is still valid
                if (datetime.utcnow() - timestamp).seconds < self.cache_ttl:
                    return result
                else:
                    # Remove expired cache
                    del self.transformation_cache[cache_key]
            
            return None
            
        except Exception as e:
            logger.error(f"❌ Error getting cached result: {e}")
            return None
    
    def _cache_result(self, cache_key: str, result: TransformationResult):
        """Cache transformation result"""
        try:
            self.transformation_cache[cache_key] = (result, datetime.utcnow())
            
            # Cleanup old cache entries
            if len(self.transformation_cache) > 1000:
                # Remove oldest 20% of entries
                sorted_entries = sorted(
                    self.transformation_cache.items(),
                    key=lambda x: x[1][1]
                )
                
                for key, _ in sorted_entries[:200]:
                    del self.transformation_cache[key]
                    
        except Exception as e:
            logger.error(f"❌ Error caching result: {e}")
    
    async def _optimize_feature_selection(
        self,
        pipeline: TransformationPipeline,
        validation_data: pd.DataFrame,
        target_column: str
    ):
        """Optimize feature selection steps"""
        try:
            # Find feature selection steps
            for step in pipeline.steps:
                if step.transformation_type == TransformationType.FEATURE_SELECTION:
                    # Optimize number of features
                    best_k = await self._find_optimal_k(
                        validation_data, target_column, step
                    )
                    
                    # Update transformer
                    if hasattr(step.transformer, 'k'):
                        step.transformer.k = best_k
                        
        except Exception as e:
            logger.error(f"❌ Error optimizing feature selection: {e}")
    
    async def _find_optimal_k(
        self,
        data: pd.DataFrame,
        target_column: str,
        step: TransformationStep
    ) -> int:
        """Find optimal number of features for selection"""
        try:
            # Simple optimization - test different k values
            X = data.drop(columns=[target_column])
            y = data[target_column]
            
            best_k = 10
            best_score = 0
            
            for k in [5, 10, 15, 20, 25]:
                if k >= X.shape[1]:
                    break
                
                selector = SelectKBest(score_func=f_classif, k=k)
                X_selected = selector.fit_transform(X, y)
                
                # Use simple scoring (mean of feature scores)
                scores = selector.scores_
                mean_score = np.mean(scores[~np.isnan(scores)])
                
                if mean_score > best_score:
                    best_score = mean_score
                    best_k = k
            
            return best_k
            
        except Exception as e:
            logger.error(f"❌ Error finding optimal k: {e}")
            return 10  # Default
    
    async def _optimize_parameters(
        self,
        pipeline: TransformationPipeline,
        validation_data: pd.DataFrame
    ):
        """Optimize transformation parameters"""
        try:
            # For now, just log optimization attempt
            # In practice, this would use techniques like grid search
            logger.info(f"Parameter optimization for pipeline {pipeline.pipeline_id}")
            
        except Exception as e:
            logger.error(f"❌ Error optimizing parameters: {e}")
    
    async def _update_metrics(self, processing_time: float, success: bool):
        """Update transformation metrics"""
        try:
            self.transformation_metrics['total_transformations'] += 1
            
            if success:
                self.transformation_metrics['successful_transformations'] += 1
                
                # Update average processing time
                total = self.transformation_metrics['successful_transformations']
                current_avg = self.transformation_metrics['average_processing_time']
                new_avg = (current_avg * (total - 1) + processing_time) / total
                self.transformation_metrics['average_processing_time'] = new_avg
            else:
                self.transformation_metrics['failed_transformations'] += 1
                
        except Exception as e:
            logger.error(f"❌ Error updating metrics: {e}")
    
    async def get_pipeline_info(self, pipeline_id: str) -> Optional[Dict[str, Any]]:
        """Get pipeline information"""
        try:
            if pipeline_id not in self.pipelines:
                return None
            
            pipeline = self.pipelines[pipeline_id]
            
            return {
                'pipeline_id': pipeline.pipeline_id,
                'name': pipeline.name,
                'creator_type': pipeline.creator_type.value,
                'num_steps': len(pipeline.steps),
                'version': pipeline.version,
                'created_at': pipeline.created_at.isoformat(),
                'updated_at': pipeline.updated_at.isoformat(),
                'fitted': pipeline_id in self.fitted_transformers,
                'steps': [
                    {
                        'step_id': step.step_id,
                        'type': step.transformation_type.value,
                        'input_columns': step.input_columns,
                        'output_columns': step.output_columns,
                        'enabled': step.enabled
                    }
                    for step in pipeline.steps
                ]
            }
            
        except Exception as e:
            logger.error(f"❌ Error getting pipeline info: {e}")
            return None
    
    async def get_metrics(self) -> Dict[str, Any]:
        """Get transformation metrics"""
        return {
            **self.transformation_metrics,
            'active_pipelines': len(self.pipelines),
            'fitted_pipelines': len(self.fitted_transformers),
            'cache_size': len(self.transformation_cache)
        }


# Global instance
transformation_engine = FeatureTransformationEngine()


async def main():
    """Test the Feature Transformation Engine"""
    engine = FeatureTransformationEngine()
    
    print("🔧 Testing Feature Transformation Engine...")
    
    # Create sample data
    sample_data = pd.DataFrame({
        'numeric_feature_1': [1, 2, 3, 4, 5],
        'numeric_feature_2': [10, 20, 30, 40, 50],
        'categorical_feature': ['A', 'B', 'A', 'C', 'B'],
        'target': [0, 1, 0, 1, 1]
    })
    
    # Create pipeline
    steps = [
        {
            'type': 'scaling',
            'method': 'standard',
            'input_columns': ['numeric_feature_1', 'numeric_feature_2']
        },
        {
            'type': 'encoding',
            'method': 'onehot',
            'input_columns': ['categorical_feature']
        }
    ]
    
    pipeline_id = await engine.create_pipeline(
        "test_pipeline",
        CreatorType.GENERIC,
        steps
    )
    print(f"Created pipeline: {pipeline_id}")
    
    # Fit pipeline
    success = await engine.fit_pipeline(pipeline_id, sample_data)
    print(f"Pipeline fitted: {success}")
    
    # Transform features
    test_features = {
        'numeric_feature_1': 3,
        'numeric_feature_2': 25,
        'categorical_feature': 'A'
    }
    
    result = await engine.transform_features(pipeline_id, test_features)
    print(f"Transformation result: {result.transformed_features}")
    print(f"Processing time: {result.transformation_time:.4f}s")
    
    # Get metrics
    metrics = await engine.get_metrics()
    print(f"Metrics: {metrics}")


if __name__ == "__main__":
    asyncio.run(main())