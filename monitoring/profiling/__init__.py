"""⚡ Profiling Enterprise Module
===============================

Advanced performance profiling system for the Creator Economy platform.
Provides comprehensive monitoring and optimization across all system components.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️ INTELLECTUAL PROPERTY WARNING:
=====================================
This code is proprietary to Fahed Mlaiel <mlaiel@live.de>
- Commercial use FORBIDDEN without written authorization
- Reverse engineering STRICTLY PROHIBITED
- Distribution FORBIDDEN without explicit license
- Violation = Automatic legal prosecution

🏢 ENTERPRISE USAGE:
- Enterprise license available on request
- Technical support included with license
- Maintenance and updates assured
- Technical team training provided
"""

# AI/ML Profiling Components
from .ai_model_profiler import (
    AIModelProfiler,
    ModelType,
    InferenceMode,
    GPUMetrics,
    ModelInferenceMetrics,
    ModelBottleneck,
    InferenceProfiler,
    create_ai_model_profiler
)

from .content_processing_profiler import (
    ContentProcessingProfiler,
    ContentType,
    ProcessingOperation,
    ProcessingQuality,
    ContentMetadata,
    ProcessingMetrics,
    ProcessingBottleneck,
    ProcessingProfiler,
    create_content_processing_profiler
)

from .nlp_processing_profiler import (
    NLPProcessingProfiler,
    NLPOperation,
    TextComplexity,
    AnalysisQuality,
    TextMetadata,
    SEOMetrics,
    NLPProcessingMetrics,
    NLPBottleneck,
    NLPProfiler,
    create_nlp_processing_profiler
)

from .recommendation_engine_profiler import (
    RecommendationEngineProfiler,
    RecommendationAlgorithm,
    RecommendationType,
    QualityMetric,
    UserProfile,
    RecommendationRequest,
    RecommendationResult,
    RecommendationMetrics,
    RecommendationBottleneck,
    RecommendationProfiler,
    create_recommendation_engine_profiler
)

# Database & Storage Profiling Components
from .database_query_profiler import (
    DatabaseQueryProfiler,
    QueryType,
    DatabaseEngine,
    QueryComplexity,
    QueryMetadata,
    QueryExecutionMetrics,
    QueryBottleneck,
    QueryProfiler,
    create_database_query_profiler
)

from .cache_profiler import (
    CacheProfiler,
    CacheType,
    CacheOperation,
    EvictionPolicy,
    CacheKeyMetadata,
    CacheMetrics,
    CacheInstanceStats,
    CacheBottleneck,
    CacheOperationProfiler,
    create_cache_profiler
)

# Performance profiler (existing) - temporarily disabled due to syntax error
# try:
#     from .performance_profiler import *
# except ImportError:
#     pass  # Original profiler may not be available

# Version information
__version__ = "1.0.0"
__author__ = "Fahed Mlaiel <mlaiel@live.de>"

# Module exports
__all__ = [
    # AI/ML Profiling
    "AIModelProfiler",
    "ModelType", 
    "InferenceMode",
    "GPUMetrics",
    "ModelInferenceMetrics",
    "ModelBottleneck",
    "InferenceProfiler",
    "create_ai_model_profiler",
    
    # Content Processing
    "ContentProcessingProfiler",
    "ContentType",
    "ProcessingOperation", 
    "ProcessingQuality",
    "ContentMetadata",
    "ProcessingMetrics",
    "ProcessingBottleneck",
    "ProcessingProfiler",
    "create_content_processing_profiler",
    
    # NLP Processing
    "NLPProcessingProfiler",
    "NLPOperation",
    "TextComplexity",
    "AnalysisQuality", 
    "TextMetadata",
    "SEOMetrics",
    "NLPProcessingMetrics",
    "NLPBottleneck",
    "NLPProfiler",
    "create_nlp_processing_profiler",
    
    # Recommendation Engine
    "RecommendationEngineProfiler",
    "RecommendationAlgorithm",
    "RecommendationType",
    "QualityMetric",
    "UserProfile",
    "RecommendationRequest", 
    "RecommendationResult",
    "RecommendationMetrics",
    "RecommendationBottleneck",
    "RecommendationProfiler",
    "create_recommendation_engine_profiler",
    
    # Database & Storage
    "DatabaseQueryProfiler",
    "QueryType",
    "DatabaseEngine",
    "QueryComplexity",
    "QueryMetadata",
    "QueryExecutionMetrics", 
    "QueryBottleneck",
    "QueryProfiler",
    "create_database_query_profiler",
    
    # Cache
    "CacheProfiler",
    "CacheType",
    "CacheOperation",
    "EvictionPolicy",
    "CacheKeyMetadata",
    "CacheMetrics",
    "CacheInstanceStats",
    "CacheBottleneck", 
    "CacheOperationProfiler",
    "create_cache_profiler"
]

# Factory functions for creating profiler instances
def create_enterprise_profiling_suite(
    enable_ai_profiling: bool = True,
    enable_content_profiling: bool = True,
    enable_nlp_profiling: bool = True,
    enable_recommendation_profiling: bool = True,
    enable_database_profiling: bool = True,
    enable_cache_profiling: bool = True,
    start_monitoring: bool = True
) -> dict:
    """
    Create a complete enterprise profiling suite
    
    Args:
        enable_ai_profiling: Enable AI model profiling
        enable_content_profiling: Enable content processing profiling
        enable_nlp_profiling: Enable NLP processing profiling
        enable_recommendation_profiling: Enable recommendation engine profiling
        enable_database_profiling: Enable database query profiling
        enable_cache_profiling: Enable cache profiling
        start_monitoring: Start background monitoring for all profilers
    
    Returns:
        Dictionary containing all configured profilers
    """
    profilers = {}
    
    if enable_ai_profiling:
        profilers['ai_model'] = create_ai_model_profiler(
            start_monitoring=start_monitoring
        )
    
    if enable_content_profiling:
        profilers['content_processing'] = create_content_processing_profiler(
            start_monitoring=start_monitoring
        )
    
    if enable_nlp_profiling:
        profilers['nlp_processing'] = create_nlp_processing_profiler(
            start_monitoring=start_monitoring
        )
    
    if enable_recommendation_profiling:
        profilers['recommendation_engine'] = create_recommendation_engine_profiler(
            start_monitoring=start_monitoring
        )
    
    if enable_database_profiling:
        profilers['database_query'] = create_database_query_profiler(
            start_monitoring=start_monitoring
        )
    
    if enable_cache_profiling:
        profilers['cache'] = create_cache_profiler(
            start_monitoring=start_monitoring
        )
    
    return profilers


def stop_all_profilers(profilers: dict):
    """
    Stop monitoring for all profilers
    
    Args:
        profilers: Dictionary of profiler instances
    """
    for name, profiler in profilers.items():
        try:
            if hasattr(profiler, 'stop_monitoring'):
                profiler.stop_monitoring()
                print(f"Stopped monitoring for {name} profiler")
        except Exception as e:
            print(f"Error stopping {name} profiler: {e}")


# Enterprise profiling configuration
ENTERPRISE_PROFILING_CONFIG = {
    'sampling_intervals': {
        'ai_model': 0.1,        # 100ms for AI operations
        'content_processing': 0.5,   # 500ms for content operations
        'nlp_processing': 0.1,       # 100ms for NLP operations  
        'recommendation': 1.0,       # 1s for recommendation operations
        'database_query': 1.0,       # 1s for database monitoring
        'cache': 5.0                 # 5s for cache monitoring
    },
    'thresholds': {
        'slow_query_threshold': 1.0,     # 1 second
        'cache_hit_rate_threshold': 80.0, # 80%
        'ai_inference_threshold': 0.5,    # 500ms
        'content_processing_threshold': 30.0  # 30 seconds
    },
    'max_history_sizes': {
        'ai_model': 10000,
        'content_processing': 5000,
        'nlp_processing': 10000,
        'recommendation': 50000,
        'database_query': 50000,
        'cache': 100000
    }
}