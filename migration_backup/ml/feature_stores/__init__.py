"""🏗️ ML Feature Stores Module - IA Influencer Agent Platform Enterprise
========================================================================
Module: backend/ml/feature_stores/__init__.py
Author: Fahed Mlaiel (mlaiel@live.de)
========================================================================

⚠️  PROPRIÉTÉ INTELLECTUELLE EXCLUSIVE - FAHED MLAIEL ⚠️
(c) 2025 Fahed Mlaiel. Tous droits réservés.
Contact: mlaiel@live.de

🎯 MODULE FEATURE STORES ML
Systèmes avancés de gestion des features
- Feature store enterprise avec lineage tracking
- Feature discovery engine automatique
- Pipeline orchestration pour feature engineering
- Streaming feature processor temps réel
"""

from .feature_store import (
    FeatureStore,
    FeatureType,
    FeatureStatus,
    FeatureSchema,
    FeatureValue,
    FeatureGroup,
    SQLiteFeatureStore,
    FeatureTransformation,
    FeatureValidator,
    FeatureLineage
)

from .feature_pipeline_orchestrator import (
    FeaturePipelineOrchestrator,
    PipelineConfig,
    PipelineRun,
    PipelineStatus,
    TransformationStep,
    FeatureDefinition,
    FeatureLineage,
    TransformationType,
    ExecutionMode
)

from .feature_discovery_engine import (
    FeatureDiscoveryEngine,
    DiscoveryConfig,
    FeatureCandidate,
    FeatureImportance,
    DiscoveryResult,
    AutoFeatureGeneration,
    CreatorSpecificFeatures
)

from .streaming_feature_processor import (
    StreamingFeatureProcessor,
    StreamingFeatureConfig,
    FeatureWindow,
    StreamingDataPoint,
    ProcessedFeature,
    StreamSource,
    FeatureType,
    AggregationType,
    WindowType
)

# NEW PHASE 15 MODULES - Advanced Feature Engineering
from .temporal_feature_generator import (
    TemporalFeatureGenerator,
    TemporalFeature,
    TimeSeriesData,
    TemporalPattern,
    TemporalFeatureType,
    GeneratorConfig,
    CreatorType as FeatureCreatorType,
    create_temporal_feature_generator
)

__all__ = [
    # Feature Store (Existing)
    'FeatureStore',
    'FeatureType',
    'FeatureStatus',
    'FeatureSchema',
    'FeatureValue',
    'FeatureGroup',
    'SQLiteFeatureStore',
    'FeatureTransformation',
    'FeatureValidator',
    'FeatureLineage',
    
    # Pipeline Orchestrator (Existing)
    'FeaturePipelineOrchestrator',
    'PipelineConfig',
    'PipelineRun',
    'PipelineStatus',
    'TransformationStep',
    'FeatureDefinition',
    'FeatureLineage',
    'TransformationType',
    'ExecutionMode',
    
    # Discovery Engine (Existing)
    'FeatureDiscoveryEngine',
    'DiscoveryConfig',
    'FeatureCandidate',
    'FeatureImportance',
    'DiscoveryResult',
    'AutoFeatureGeneration',
    'CreatorSpecificFeatures',
    
    # Streaming Processor (NEW - PHASE 4)
    'StreamingFeatureProcessor',
    'StreamingFeatureConfig',
    'FeatureWindow',
    'StreamingDataPoint',
    'ProcessedFeature',
    'StreamSource',
    'FeatureType',
    'AggregationType',
    'WindowType',
    
    # NEW PHASE 15 - Advanced Feature Engineering
    'TemporalFeatureGenerator',
    'TemporalFeature',
    'TimeSeriesData',
    'TemporalPattern',
    'TemporalFeatureType',
    'GeneratorConfig',
    'FeatureCreatorType',
    'create_temporal_feature_generator'
]

# Version du module
__version__ = "1.0.0"

# Metadata
__author__ = "Fahed Mlaiel"
__email__ = "mlaiel@live.de"
__copyright__ = "(c) 2025 Fahed Mlaiel. Tous droits réservés."
