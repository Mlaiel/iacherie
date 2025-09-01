"""Vector Agent Data Models - Advanced Type Definitions & Schema

Ultra-comprehensive data models providing type safety, validation, and
serialization for all vector operations and data structures.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️  CRITICAL LEGAL NOTICE:
This code and architectural design are the exclusive intellectual property of Fahed Mlaiel.
Unauthorized use, copying, distribution, or commercialization is strictly prohibited.
Any attempt to steal the concept, idea, or code without explicit written authorization
from Fahed Mlaiel will result in immediate legal prosecution under German and international law.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Union, Tuple
from datetime import datetime, timezone
from enum import Enum
import numpy as np
import json


class ContentType(Enum):
    """
Supported content types for vector processing"""

    AUDIO = "audio"
    VIDEO = "video"
    IMAGE = "image"
    TEXT = "text"
    MUSIC = "music"
    PHOTO = "photo"
    DOCUMENT = "document"
    COMPOSITE = "composite"
    GENERIC = "generic"


class MatchType(Enum):
    """Types of similarity matches"""

    EXACT = "exact"
    NEAR_DUPLICATE = "near_duplicate"
    SIMILAR = "similar"
    RELATED = "related"
    DIFFERENT = "different"


class IndexType(Enum):
    """FAISS index types"""

    FLAT = "flat"
    IVF = "ivf"
    HNSW = "hnsw"
    LSH = "lsh"
    PQ = "pq"
    IVFPQ = "ivfpq"


class ProcessingStatus(Enum):
    """Vector processing status"""

    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CACHED = "cached"


@dataclass
class VectorDocument:
    """Complete vector document with metadata"""
    document_id: str
    content_type: str
    vector_data: np.ndarray
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: Optional[datetime] = None
    
    def __post_init__(self):
        """
Post-initialization validation and processing"""
        if self.updated_at is None:
            self.updated_at = self.created_at
        
        # Validate vector data
        if self.vector_data is not None and len(self.vector_data.shape) > 2:
            raise ValueError("Vector data must be 1D or 2D array")
        
        # Ensure vector data is float32 for FAISS compatibility
        if self.vector_data is not None:
            self.vector_data = self.vector_data.astype(np.float32)
    
    @property
    def vector_dimension(self) -> int:
        """Get vector dimension"""
        return self.vector_data.shape[-1] if self.vector_data is not None else 0
    
    @property
    def vector_count(self) -> int:
        """
Get number of vectors (for batch operations)"""
        if self.vector_data is None:
            return 0
        return 1 if len(self.vector_data.shape) == 1 else self.vector_data.shape[0]
    
    def to_dict(self) -> Dict[str, Any]:
        """
Convert to dictionary (excluding numpy array)"""
        return {
            "document_id": self.document_id,
            "content_type": self.content_type,
            "vector_dimension": self.vector_dimension,
            "vector_count": self.vector_count,
            "metadata": self.metadata,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }
    
    def serialize_vector(self) -> List[float]:
        """Serialize vector data for JSON"""
        if self.vector_data is None:
            return []
        return self.vector_data.flatten().tolist()


@dataclass
class VectorSearchRequest:
    """
Comprehensive vector search request"""
    query_id: str
    query_vector: Union[np.ndarray, List[float]]
    content_type: str
    max_results: int = 10
    similarity_threshold: float = 0.75
    search_parameters: Dict[str, Any] = field(default_factory=dict)
    filters: Dict[str, Any] = field(default_factory=dict)
    include_metadata: bool = True
    include_detailed_scores: bool = False
    
    def __post_init__(self):
        """
Post-initialization processing"""
        # Convert list to numpy array if needed
        if isinstance(self.query_vector, list):
            self.query_vector = np.array(self.query_vector, dtype=np.float32)
        elif isinstance(self.query_vector, np.ndarray):
            self.query_vector = self.query_vector.astype(np.float32)
        
        # Validate parameters
        if self.max_results <= 0:
            raise ValueError("max_results must be positive")
        
        if not (0.0 <= self.similarity_threshold <= 1.0):
            raise ValueError("similarity_threshold must be between 0 and 1")
    
    @property
    def vector_dimension(self) -> int:
        """Get query vector dimension"""
        return len(self.query_vector) if self.query_vector is not None else 0
    
    def to_dict(self) -> Dict[str, Any]:
        """
Convert to dictionary"""
        return {
            "query_id": self.query_id,
            "content_type": self.content_type,
            "vector_dimension": self.vector_dimension,
            "max_results": self.max_results,
            "similarity_threshold": self.similarity_threshold,
            "search_parameters": self.search_parameters,
            "filters": self.filters,
            "include_metadata": self.include_metadata,
            "include_detailed_scores": self.include_detailed_scores
        }


@dataclass
class VectorSearchResult:
    """Individual search result with detailed information"""
    document_id: str
    similarity_score: float
    confidence: float
    match_type: str
    detailed_scores: Optional[Dict[str, float]] = None
    metadata: Optional[Dict[str, Any]] = None
    rank: int = 0
    processing_time: float = 0.0
    
    def __post_init__(self):
        """
Post-initialization validation"""
        if not (0.0 <= self.similarity_score <= 1.0):
            raise ValueError("similarity_score must be between 0 and 1")
        
        if not (0.0 <= self.confidence <= 1.0):
            raise ValueError("confidence must be between 0 and 1")
    
    @property
    def match_quality(self) -> str:
        """Get qualitative match assessment"""
        if self.similarity_score >= 0.95:
            return "excellent"
        elif self.similarity_score >= 0.85:
            return "very_good"
        elif self.similarity_score >= 0.75:
            return "good"
        elif self.similarity_score >= 0.60:
            return "fair"
        else:
            return "poor"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "document_id": self.document_id,
            "similarity_score": self.similarity_score,
            "confidence": self.confidence,
            "match_type": self.match_type,
            "match_quality": self.match_quality,
            "detailed_scores": self.detailed_scores or {},
            "metadata": self.metadata or {},
            "rank": self.rank,
            "processing_time": self.processing_time
        }


@dataclass
class SimilarityMatch:
    """Similarity match result with comprehensive details"""
    document_id: str
    similarity_score: float
    content_type: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    match_segments: List[Dict[str, Any]] = field(default_factory=list)
    confidence: float = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        """
Convert to dictionary"""
        return {
            "document_id": self.document_id,
            "similarity_score": self.similarity_score,
            "content_type": self.content_type,
            "metadata": self.metadata,
            "match_segments": self.match_segments,
            "confidence": self.confidence
        }


@dataclass
class VectorIndexConfig:
    """Configuration for vector index creation"""
    index_name: str
    index_type: IndexType
    dimension: int
    content_type: str
    parameters: Dict[str, Any] = field(default_factory=dict)
    optimization_settings: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """
Convert to dictionary"""
        return {
            "index_name": self.index_name,
            "index_type": self.index_type.value,
            "dimension": self.dimension,
            "content_type": self.content_type,
            "parameters": self.parameters,
            "optimization_settings": self.optimization_settings
        }


@dataclass
class IndexingResult:
    """Result of vector indexing operation"""
    success: bool
    document_id: str
    index_position: int = -1
    storage_path: Optional[str] = None
    error: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    processing_time: float = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        """
Convert to dictionary"""
        return {
            "success": self.success,
            "document_id": self.document_id,
            "index_position": self.index_position,
            "storage_path": self.storage_path,
            "error": self.error,
            "metadata": self.metadata,
            "processing_time": self.processing_time
        }


@dataclass
class BatchProcessingResult:
    """Result of batch vector processing operation"""
    batch_id: str
    total_processed: int
    successful: int
    failed: int
    processing_time: float
    results: List[IndexingResult] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
    
    @property
    def success_rate(self) -> float:
        """
Calculate success rate"""
        return self.successful / self.total_processed if self.total_processed > 0 else 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        """
Convert to dictionary"""
        return {
            "batch_id": self.batch_id,
            "total_processed": self.total_processed,
            "successful": self.successful,
            "failed": self.failed,
            "success_rate": self.success_rate,
            "processing_time": self.processing_time,
            "results": [r.to_dict() for r in self.results],
            "errors": self.errors
        }


@dataclass
class VectorMetrics:
    """Comprehensive metrics for vector operations"""
    # Storage metrics
    vectors_stored: int = 0
    vectors_deleted: int = 0
    total_storage_size_mb: float = 0.0
    
    # Search metrics
    searches_performed: int = 0
    similarity_searches: int = 0
    total_search_time: float = 0.0
    average_search_time: float = 0.0
    
    # Processing metrics
    documents_indexed: int = 0
    documents_retrieved: int = 0
    documents_deleted: int = 0
    total_processing_time: float = 0.0
    
    # Performance metrics
    cache_hit_rate: float = 0.0
    cache_size: int = 0
    optimization_count: int = 0
    
    # Error tracking
    processing_errors: int = 0
    search_errors: int = 0
    storage_errors: int = 0
    
    # Additional metrics
    vectors_added: int = 0
    batch_operations: int = 0
    cross_modal_searches: int = 0
    
    def update_search_metrics(self, search_time: float):
        """
Update search performance metrics"""
        self.searches_performed += 1
        self.total_search_time += search_time
        self.average_search_time = self.total_search_time / self.searches_performed
    
    def update_from_components(self, *component_metrics):
        """
Update metrics from multiple components"""
        for metrics in component_metrics:
            if hasattr(metrics, 'searches_performed'):
                self.searches_performed += metrics.searches_performed
            if hasattr(metrics, 'total_search_time'):
                self.total_search_time += metrics.total_search_time
            if hasattr(metrics, 'vectors_added'):
                self.vectors_added += metrics.vectors_added
    
    def to_dict(self) -> Dict[str, Any]:
        """
Convert to dictionary"""
        return {
            "storage_metrics": {
                "vectors_stored": self.vectors_stored,
                "vectors_deleted": self.vectors_deleted,
                "total_storage_size_mb": self.total_storage_size_mb
            },
            "search_metrics": {
                "searches_performed": self.searches_performed,
                "similarity_searches": self.similarity_searches,
                "total_search_time": self.total_search_time,
                "average_search_time": self.average_search_time
            },
            "processing_metrics": {
                "documents_indexed": self.documents_indexed,
                "documents_retrieved": self.documents_retrieved,
                "documents_deleted": self.documents_deleted,
                "total_processing_time": self.total_processing_time
            },
            "performance_metrics": {
                "cache_hit_rate": self.cache_hit_rate,
                "cache_size": self.cache_size,
                "optimization_count": self.optimization_count
            },
            "error_metrics": {
                "processing_errors": self.processing_errors,
                "search_errors": self.search_errors,
                "storage_errors": self.storage_errors
            }
        }


@dataclass
class VectorProcessingTask:
    """Task definition for vector processing operations"""
    task_id: str
    task_type: str  # store, search, optimize, delete, etc.
    priority: int
    content_id: Optional[str] = None
    content_type: Optional[str] = None
    parameters: Dict[str, Any] = field(default_factory=dict)
    status: ProcessingStatus = ProcessingStatus.PENDING
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None
    result: Optional[Dict[str, Any]] = None
    
    @property
    def processing_time(self) -> float:
        """
Get processing time in seconds"""
        if self.started_at and self.completed_at:
            return (self.completed_at - self.started_at).total_seconds()
        return 0.0
    
    @property
    def age_seconds(self) -> float:
        """
Get task age in seconds"""
        return (datetime.now(timezone.utc) - self.created_at).total_seconds()
    
    def to_dict(self) -> Dict[str, Any]:
        """
Convert to dictionary"""
        return {
            "task_id": self.task_id,
            "task_type": self.task_type,
            "priority": self.priority,
            "content_id": self.content_id,
            "content_type": self.content_type,
            "parameters": self.parameters,
            "status": self.status.value,
            "created_at": self.created_at.isoformat(),
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "processing_time": self.processing_time,
            "age_seconds": self.age_seconds,
            "error_message": self.error_message,
            "result": self.result
        }


@dataclass
class CrossModalSearchRequest:
    """Cross-modal similarity search request"""
    query_id: str
    query_vector: Union[np.ndarray, List[float]]
    content_types: List[str]
    max_results_per_type: int = 10
    overall_max_results: int = 50
    similarity_threshold: float = 0.75
    cross_modal_boost: float = 1.0
    include_score_breakdown: bool = True
    
    def __post_init__(self):
        """
Post-initialization processing"""
        if isinstance(self.query_vector, list):
            self.query_vector = np.array(self.query_vector, dtype=np.float32)
        elif isinstance(self.query_vector, np.ndarray):
            self.query_vector = self.query_vector.astype(np.float32)
    
    def to_dict(self) -> Dict[str, Any]:
        """
Convert to dictionary"""
        return {
            "query_id": self.query_id,
            "content_types": self.content_types,
            "max_results_per_type": self.max_results_per_type,
            "overall_max_results": self.overall_max_results,
            "similarity_threshold": self.similarity_threshold,
            "cross_modal_boost": self.cross_modal_boost,
            "include_score_breakdown": self.include_score_breakdown,
            "vector_dimension": len(self.query_vector) if self.query_vector is not None else 0
        }


@dataclass
class VectorStatistics:
    """Comprehensive statistics for vector system"""
    total_documents: int = 0
    total_vectors: int = 0
    storage_size_bytes: int = 0
    index_count: int = 0
    average_vector_dimension: float = 0.0
    
    # Content type distribution
    content_type_distribution: Dict[str, int] = field(default_factory=dict)
    
    # Performance metrics
    search_performance: Dict[str, float] = field(default_factory=dict)
    indexing_performance: Dict[str, float] = field(default_factory=dict)
    
    # System health
    system_health: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """
Convert to dictionary"""
        return {
            "total_documents": self.total_documents,
            "total_vectors": self.total_vectors,
            "storage_size_mb": self.storage_size_bytes / (1024 * 1024),
            "index_count": self.index_count,
            "average_vector_dimension": self.average_vector_dimension,
            "content_type_distribution": self.content_type_distribution,
            "search_performance": self.search_performance,
            "indexing_performance": self.indexing_performance,
            "system_health": self.system_health
        }
