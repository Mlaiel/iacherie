"""Vector Stores Module - IA Influencer Agent

This module provides comprehensive vector database operations for AI fingerprinting, 
similarity search, real-time streaming, and content protection across multiple vector stores.

Supports FAISS, Pinecone, and Elasticsearch with advanced features:
- Real-time vector streaming for live content protection
- Advanced similarity search with multiple metrics
- Vector quality assessment and optimization
- Multi-modal embedding generation
- Clustering and anomaly detection
- Performance optimization and monitoring

Author: Fahed Mlaiel <mlaiel@live.de>
Project: IA Influencer Agent + Content Protection Platform
Copyright: All rights reserved. Unauthorized use, modification, or distribution prohibited.

WARNING: This code is proprietary to Fahed Mlaiel. Any unauthorized copying, modification, 
or distribution without explicit written permission is strictly prohibited and will result 
in legal action under German and international copyright law.
"""# Core vector store implementations
from .faiss_vector_store import FAISSVectorStore
from .elasticsearch_vector_store import ElasticsearchVectorStore
from .pinecone_vector_store import PineconeVectorStore

# Management and orchestration
from .vector_store_manager import VectorStoreManager, VectorStoreType, SearchStrategy
from .vector_indexing import VectorIndexManager

# Embedding and similarity
from .embedding_generator import EmbeddingGenerator
from .similarity_search import SimilaritySearchEngine, SimilarityMetric

# Clustering and analysis
from .vector_clustering import VectorClusteringEngine

# Advanced features
from .realtime_streaming import RealTimeVectorStreaming, StreamingMode, StreamingPriority
from .optimization_engine import VectorDatabaseOptimizer, OptimizationStrategy
from .quality_assessment import VectorQualityAssessment, QualityMetric

# Data classes and types
from .vector_store_manager import UnifiedSearchResult, VectorStoreHealth, SearchPerformanceMetrics
from .realtime_streaming import StreamingConfig, StreamChunk, LiveAlert
from .optimization_engine import OptimizationConfig, PerformanceMetrics, OptimizationResult
from .quality_assessment import QualityAssessmentConfig, QualityReport, DimensionalityAnalysis

__all__ = [
    # Core implementations
    "FAISSVectorStore",
    "ElasticsearchVectorStore", 
    "PineconeVectorStore",
    
    # Management
    "VectorStoreManager",
    "VectorIndexManager",
    "VectorStoreType",
    "SearchStrategy",
    
    # Embedding and search
    "EmbeddingGenerator",
    "SimilaritySearchEngine",
    "SimilarityMetric",
    
    # Clustering
    "VectorClusteringEngine",
    
    # Advanced features
    "RealTimeVectorStreaming",
    "VectorDatabaseOptimizer",
    "VectorQualityAssessment",
    
    # Enums
    "StreamingMode",
    "StreamingPriority",
    "OptimizationStrategy",
    "QualityMetric",
    
    # Data classes
    "UnifiedSearchResult",
    "VectorStoreHealth",
    "SearchPerformanceMetrics",
    "StreamingConfig",
    "StreamChunk",
    "LiveAlert",
    "OptimizationConfig",
    "PerformanceMetrics",
    "OptimizationResult",
    "QualityAssessmentConfig",
    "QualityReport",
    "DimensionalityAnalysis"
]

__version__ = "3.0.0"
__author__ = "Fahed Mlaiel"
__email__ = "mlaiel@live.de"
__description__ = "Enterprise-grade vector database system for IA Influencer Agent content protection"
