"""⚡ ML Inference Module - IA Influencer Agent Platform Enterprise
================================================================
Module: backend/ml/inference/__init__.py
Author: Fahed Mlaiel (mlaiel@live.de)
================================================================

⚠️  PROPRIÉTÉ INTELLECTUELLE EXCLUSIVE - FAHED MLAIEL ⚠️
(c) 2025 Fahed Mlaiel. Tous droits réservés.
Contact: mlaiel@live.de

🎯 MODULE D'INFÉRENCE ML
Systèmes avancés d'inférence temps réel
- Real-time inference engine <100ms
- Batch processing pour large-scale
- Streaming inference pour contenus live
- High-performance serving avec auto-scaling
- Audio inference spécialisé musiciens
"""

from .real_time_inference_engine import (
    RealTimeInferenceEngine,
    PredictionRequest,
    PredictionResponse,
    InferenceStatus,
    ModelInstance,
    InferenceMetrics,
    ModelState
)

from .batch_inference_processor import (
    BatchInferenceProcessor,
    BatchJob,
    BatchResult,
    BatchStatus,
    BatchMetrics,
    ProcessingMode
)

from .streaming_inference_engine import (
    StreamingInferenceEngine,
    StreamConfig,
    StreamSample,
    StreamPrediction,
    StreamStatus,
    StreamMetrics
)

# Temporarily disabled due to torch dependency
# from .high_performance_serving import (
#     HighPerformanceServingEngine,
#     InferenceRequest as HPInferenceRequest,
#     InferenceResponse as HPInferenceResponse,
#     ModelInstance as HPModelInstance,
#     PerformanceMonitor,
#     ModelCache
# )

from .audio_inference_engine import (
    AudioInferenceEngine,
    AudioFeatures,
    AudioAnalysisResult,
    AudioFormat,
    AudioQuality,
    MusicGenre,
    AudioMood,
    InstrumentType,
    StreamingAudioBuffer
)

# NEW - Performance Monitoring & Resource Tracking
from .inference_performance_monitor import (
    InferencePerformanceMonitor,
    InferenceMetrics,
    PerformanceAlert
)

from .resource_usage_tracker import (
    ResourceUsageTracker,
    ResourceSnapshot,
    CostMetrics
)

__all__ = [
    # Real-Time Inference (Existing)
    'RealTimeInferenceEngine',
    'PredictionRequest',
    'PredictionResponse',
    'InferenceStatus',
    'ModelInstance',
    'InferenceMetrics',
    'ModelState',
    
    # Batch Inference (Existing)
    'BatchInferenceProcessor',
    'BatchJob',
    'BatchResult',
    'BatchStatus',
    'BatchMetrics',
    'ProcessingMode',
    
    # Streaming Inference (Existing)
    'StreamingInferenceEngine',
    'StreamConfig',
    'StreamSample',
    'StreamPrediction',
    'StreamStatus',
    'StreamMetrics',
    
    # High Performance Serving (Existing - temporarily disabled)
    # 'HighPerformanceServingEngine',
    # 'HPInferenceRequest',
    # 'HPInferenceResponse',
    # 'HPModelInstance',
    # 'PerformanceMonitor',
    # 'ModelCache',
    
    # Audio Inference (NEW - PHASE 4)
    'AudioInferenceEngine',
    'AudioFeatures',
    'AudioAnalysisResult',
    'AudioFormat',
    'AudioQuality',
    'MusicGenre',
    'AudioMood',
    'InstrumentType',
    'StreamingAudioBuffer',
    
    # Performance Monitoring & Resource Tracking (NEW - PHASE 23)
    'InferencePerformanceMonitor',
    'InferenceMetrics',
    'PerformanceAlert',
    'ResourceUsageTracker',
    'ResourceSnapshot',
    'CostMetrics'
]

# Version du module
__version__ = "1.0.0"

# Metadata
__author__ = "Fahed Mlaiel"
__email__ = "mlaiel@live.de"
__copyright__ = "(c) 2025 Fahed Mlaiel. Tous droits réservés."
