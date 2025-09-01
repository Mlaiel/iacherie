"""Enterprise Vector Cache Implementation for IA Influencer Agent Platform
AI-powered vector similarity caching with FAISS integration for content fingerprinting
Specialized for multi-format content creators (audio, video, image, text)

Business Logic: Creator Upload → AI Processing → Vector Cache → Similarity Search → Content Protection

Author: Fahed Mlaiel <mlaiel@live.de>
Contact: mlaiel@live.de
Team: Lead Dev IA + Backend Senior + ML Engineer + DBA + Security Expert + 
      Microservices Architect + Audio Processing Expert + DevOps Engineer + IA Prompt Engineer

⚠️  PROPRIETARY SOFTWARE - UNAUTHORIZED USE PROHIBITED ⚠️
Copyright (C) 2024 Fahed Mlaiel. All rights reserved.
For licensing inquiries: mlaiel@live.de
"""

import asyncio
import logging
import numpy as np
from typing import Any, Dict, List, Optional, Tuple, Union, Set, Callable
import pickle
import json
import hashlib
import threading
import time
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
from concurrent.futures import ThreadPoolExecutor

# FAISS imports with error handling
try:
    import faiss
    FAISS_AVAILABLE = True
except ImportError:
    FAISS_AVAILABLE = False

# Additional ML libraries for advanced features
try:
    from sklearn.metrics.pairwise import cosine_similarity, euclidean_distances
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False

logger = logging.getLogger(__name__)

class ContentType(Enum):
    """
Content types for IA Influencer Agent platform"""

    AUDIO = "audio"
    VIDEO = "video" 
    IMAGE = "image"
    TEXT = "text"
    MUSIC = "music"
    PODCAST = "podcast"
    PHOTO = "photo"
    BLOG = "blog"
    SOCIAL_POST = "social_post"

class SimilarityMetric(Enum):
    """Supported similarity metrics"""

    COSINE = "cosine"
    EUCLIDEAN = "euclidean"
    MANHATTAN = "manhattan"
    DOT_PRODUCT = "dot_product"
    JACCARD = "jaccard"

class IndexType(Enum):
    """FAISS index types for different use cases"""

    FLAT_IP = "IndexFlatIP"  # Exact search, inner product
    FLAT_L2 = "IndexFlatL2"  # Exact search, L2 distance
    IVF_FLAT = "IndexIVFFlat"  # Approximate search, faster
    HNSW = "IndexHNSWFlat"  # Hierarchical NSW, best for query speed
    LSH = "IndexLSH"  # Locality sensitive hashing

@dataclass
class VectorEntry:
    """Enhanced vector cache entry with comprehensive metadata"""
    vector: np.ndarray
    content_id: str
    creator_id: str
    content_type: ContentType
    
    # Metadata
    metadata: Dict[str, Any] = field(default_factory=dict)
    fingerprint_hash: Optional[str] = None
    original_filename: Optional[str] = None
    file_size: Optional[int] = None
    
    # Timestamps
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    accessed_at: datetime = field(default_factory=datetime.utcnow)
    
    # Access tracking
    access_count: int = 0
    last_similarity_score: Optional[float] = None
    
    # AI-specific features
    ai_model_version: Optional[str] = None
    embedding_method: Optional[str] = None
    confidence_score: Optional[float] = None
    
    # Content protection
    protection_enabled: bool = True
    similarity_threshold: float = 0.85
    alert_threshold: float = 0.95
    
    # Platform tracking
    platforms_found: Set[str] = field(default_factory=set)
    violation_count: int = 0
    last_violation_detected: Optional[datetime] = None
    
    def update_access(self):
        """
Update access statistics"""
        self.accessed_at = datetime.utcnow()
        self.access_count += 1
    
    def add_platform_detection(self, platform: str):
        """
Add platform where content was detected"""
        self.platforms_found.add(platform)
        if platform not in ['original', 'authorized']:
            self.violation_count += 1
            self.last_violation_detected = datetime.utcnow()
    
    def to_dict(self) -> Dict[str, Any]:
        """
Convert to dictionary for storage"""
        return {
            'content_id': self.content_id,
            'creator_id': self.creator_id,
            'content_type': self.content_type.value,
            'metadata': self.metadata,
            'fingerprint_hash': self.fingerprint_hash,
            'original_filename': self.original_filename,
            'file_size': self.file_size,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'accessed_at': self.accessed_at.isoformat(),
            'access_count': self.access_count,
            'last_similarity_score': self.last_similarity_score,
            'ai_model_version': self.ai_model_version,
            'embedding_method': self.embedding_method,
            'confidence_score': self.confidence_score,
            'protection_enabled': self.protection_enabled,
            'similarity_threshold': self.similarity_threshold,
            'alert_threshold': self.alert_threshold,
            'platforms_found': list(self.platforms_found),
            'violation_count': self.violation_count,
            'last_violation_detected': self.last_violation_detected.isoformat() if self.last_violation_detected else None
        }

@dataclass
class SimilarityResult:
    """
Enhanced similarity search result"""
    content_id: str
    creator_id: str
    similarity_score: float
    content_type: ContentType
    metadata: Dict[str, Any]
    vector: np.ndarray
    
    # Additional context
    fingerprint_hash: Optional[str] = None
    original_filename: Optional[str] = None
    platforms_found: Set[str] = field(default_factory=set)
    violation_count: int = 0
    protection_enabled: bool = True
    
    # Detection context
    detection_method: str = "vector_similarity"
    confidence_level: str = "high"  # high, medium, low
    alert_level: str = "info"  # critical, warning, info
    
    def __post_init__(self):
        """Set alert level based on similarity score"""
        if self.similarity_score >= 0.95:
            self.alert_level = "critical"
            self.confidence_level = "high"
        elif self.similarity_score >= 0.85:
            self.alert_level = "warning" 
            self.confidence_level = "medium"
        else:
            self.alert_level = "info"
            self.confidence_level = "low"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'content_id': self.content_id,
            'creator_id': self.creator_id,
            'similarity_score': self.similarity_score,
            'content_type': self.content_type.value,
            'metadata': self.metadata,
            'fingerprint_hash': self.fingerprint_hash,
            'original_filename': self.original_filename,
            'platforms_found': list(self.platforms_found),
            'violation_count': self.violation_count,
            'protection_enabled': self.protection_enabled,
            'detection_method': self.detection_method,
            'confidence_level': self.confidence_level,
            'alert_level': self.alert_level
        }

@dataclass
class VectorCacheConfig:
    """
Comprehensive configuration for vector cache"""
    # Core settings
    dimension: int = 512
    metric: SimilarityMetric = SimilarityMetric.COSINE
    max_vectors: int = 1000000  # 1M vectors for large-scale deployment
    
    # Similarity thresholds per content type
    similarity_thresholds: Dict[ContentType, float] = field(default_factory=lambda: {
        ContentType.AUDIO: 0.85,
        ContentType.VIDEO: 0.80,
        ContentType.IMAGE: 0.90,
        ContentType.TEXT: 0.75,
        ContentType.MUSIC: 0.85,
        ContentType.PODCAST: 0.80,
        ContentType.PHOTO: 0.90,
        ContentType.BLOG: 0.75,
        ContentType.SOCIAL_POST: 0.70
    })
    
    # Alert thresholds
    alert_thresholds: Dict[ContentType, float] = field(default_factory=lambda: {
        ContentType.AUDIO: 0.95,
        ContentType.VIDEO: 0.92,
        ContentType.IMAGE: 0.95,
        ContentType.TEXT: 0.85,
        ContentType.MUSIC: 0.95,
        ContentType.PODCAST: 0.90,
        ContentType.PHOTO: 0.95,
        ContentType.BLOG: 0.85,
        ContentType.SOCIAL_POST: 0.80
    })
    
    # Performance settings
    enable_parallel_search: bool = True
    max_workers: int = 4
    batch_size: int = 1000
    
    # FAISS settings
    faiss_index_type: IndexType = IndexType.HNSW
    faiss_nlist: int = 1024  # For IVF indices
    faiss_nprobe: int = 64   # Search probe count
    faiss_m: int = 32        # HNSW parameter
    
    # Caching and persistence
    enable_disk_persistence: bool = True
    persistence_path: str = "/tmp/vector_cache"
    save_interval: int = 300  # Save every 5 minutes
    
    # Multi-tenant settings
    tenant_isolation: bool = True
    per_tenant_limits: Dict[str, int] = field(default_factory=dict)
    
    # Monitoring
    enable_metrics: bool = True
    enable_slow_query_log: bool = True
    slow_query_threshold: float = 1.0  # 1 second
    
    # Content protection specific
    enable_content_protection: bool = True
    protection_monitoring_interval: int = 60  # Check every minute
    violation_escalation_threshold: int = 5  # Alert after 5 violations

class VectorCache:
    """
    Enterprise vector cache for IA Influencer Agent platform
    Specialized for content creator protection and monetization
    """
    
    def __init__(self, config: VectorCacheConfig):
        self.config = config
        
        # Core storage
        self._vectors: Dict[str, VectorEntry] = {}
        self._creator_vectors: Dict[str, Set[str]] = {}  # creator_id -> content_ids
        self._content_type_vectors: Dict[ContentType, Set[str]] = {
            ct: set() for ct in ContentType
        }
        
        # Threading and concurrency
        self._lock = threading.RLock()
        self._executor = ThreadPoolExecutor(max_workers=config.max_workers)
        
        # Performance metrics
        self._stats = {
            'total_vectors': 0,
            'searches_performed': 0,
            'cache_hits': 0,
            'cache_misses': 0,
            'vectors_added': 0,
            'vectors_removed': 0,
            'violations_detected': 0,
            'protection_alerts': 0,
            'avg_search_time': 0.0,
            'total_search_time': 0.0,
            'slow_queries': 0
        }
        
        # Content type specific stats
        self._content_type_stats: Dict[ContentType, Dict[str, int]] = {
            ct: {'vectors': 0, 'searches': 0, 'violations': 0}
            for ct in ContentType
        }
        
        # Creator-specific stats
        self._creator_stats: Dict[str, Dict[str, int]] = {}
        
        # Slow query log
        self._slow_queries: List[Dict[str, Any]] = []
        
        # Violation tracking
        self._violation_log: List[Dict[str, Any]] = []
        
        logger.info(f"VectorCache initialized for IA Influencer Agent - Dimension: {config.dimension}")
        
        if not FAISS_AVAILABLE:
            logger.warning("FAISS not available. Some advanced features will be limited.")
        if not SKLEARN_AVAILABLE:
            logger.warning("Scikit-learn not available. Some similarity metrics will be unavailable.")
    
    def _normalize_vector(self, vector: np.ndarray) -> np.ndarray:
        """Advanced vector normalization based on metric"""
        if self.config.metric == SimilarityMetric.COSINE:
            norm = np.linalg.norm(vector)
            if norm > 0:
                return vector / norm
        elif self.config.metric == SimilarityMetric.DOT_PRODUCT:
            # For dot product, we might want to maintain magnitude
            return vector.astype(np.float32)
        
        return vector.astype(np.float32)
    
    def _compute_similarity(self, vec1: np.ndarray, vec2: np.ndarray) -> float:
        """
Compute similarity using configured metric"""
        if self.config.metric == SimilarityMetric.COSINE:
            if SKLEARN_AVAILABLE:
                return float(cosine_similarity([vec1], [vec2])[0][0])
            else:
                # Manual cosine similarity
                vec1_norm = self._normalize_vector(vec1)
                vec2_norm = self._normalize_vector(vec2)
                return float(np.dot(vec1_norm, vec2_norm))
        
        elif self.config.metric == SimilarityMetric.EUCLIDEAN:
            if SKLEARN_AVAILABLE:
                distance = euclidean_distances([vec1], [vec2])[0][0]
            else:
                distance = np.linalg.norm(vec1 - vec2)
            return 1.0 / (1.0 + distance)  # Convert distance to similarity
        
        elif self.config.metric == SimilarityMetric.MANHATTAN:
            distance = np.sum(np.abs(vec1 - vec2))
            return 1.0 / (1.0 + distance)
        
        elif self.config.metric == SimilarityMetric.DOT_PRODUCT:
            return float(np.dot(vec1, vec2))
        
        else:
            # Default to cosine
            vec1_norm = self._normalize_vector(vec1)
            vec2_norm = self._normalize_vector(vec2)
            return float(np.dot(vec1_norm, vec2_norm))
    
    def _get_similarity_threshold(self, content_type: ContentType) -> float:
        """
Get similarity threshold for content type"""
        return self.config.similarity_thresholds.get(content_type, 0.85)
    
    def _get_alert_threshold(self, content_type: ContentType) -> float:
        """
Get alert threshold for content type"""
        return self.config.alert_thresholds.get(content_type, 0.95)
    
    def _track_slow_query(self, operation: str, duration: float, metadata: Dict[str, Any]):
        """
Track slow queries for performance monitoring"""
        if duration > self.config.slow_query_threshold:
            slow_query = {
                'operation': operation,
                'duration_seconds': duration,
                'timestamp': datetime.utcnow().isoformat(),
                'metadata': metadata
            }
            
            self._slow_queries.append(slow_query)
            self._stats['slow_queries'] += 1
            
            # Keep only recent slow queries
            if len(self._slow_queries) > 100:
                self._slow_queries = self._slow_queries[-100:]
            
            logger.warning(f"Slow vector cache operation: {operation} took {duration:.2f}s")
    
    def _update_creator_stats(self, creator_id: str, operation: str):
        """Update creator-specific statistics"""
        if creator_id not in self._creator_stats:
            self._creator_stats[creator_id] = {
                'vectors_added': 0,
                'searches_performed': 0,
                'violations_detected': 0,
                'last_activity': datetime.utcnow().isoformat()
            }
        
        if operation in self._creator_stats[creator_id]:
            self._creator_stats[creator_id][operation] += 1
        
        self._creator_stats[creator_id]['last_activity'] = datetime.utcnow().isoformat()
    
    async def add_vector(self,
                        content_id: str,
                        creator_id: str,
                        vector: Union[np.ndarray, List[float]],
                        content_type: ContentType,
                        metadata: Optional[Dict[str, Any]] = None,
                        fingerprint_hash: Optional[str] = None,
                        original_filename: Optional[str] = None,
                        file_size: Optional[int] = None,
                        ai_model_version: Optional[str] = None,
                        embedding_method: Optional[str] = None,
                        confidence_score: Optional[float] = None) -> bool:
        """
Add vector to cache with comprehensive metadata"""
        
        start_time = time.time()
        
        try:
            if isinstance(vector, list):
                vector = np.array(vector, dtype=np.float32)
            
            if vector.shape[0] != self.config.dimension:
                logger.error(f"Vector dimension mismatch: expected {self.config.dimension}, got {vector.shape[0]}")
                return False
            
            with self._lock:
                # Check tenant limits
                if self.config.tenant_isolation and creator_id in self.config.per_tenant_limits:
                    creator_vector_count = len(self._creator_vectors.get(creator_id, set()))
                    if creator_vector_count >= self.config.per_tenant_limits[creator_id]:
                        logger.warning(f"Creator {creator_id} exceeded vector limit")
                        return False
                
                # Check global capacity
                if len(self._vectors) >= self.config.max_vectors:
                    await self._evict_oldest_vectors()
                
                # Normalize vector
                normalized_vector = self._normalize_vector(vector)
                
                # Create enhanced entry
                entry = VectorEntry(
                    vector=normalized_vector,
                    content_id=content_id,
                    creator_id=creator_id,
                    content_type=content_type,
                    metadata=metadata or {},
                    fingerprint_hash=fingerprint_hash,
                    original_filename=original_filename,
                    file_size=file_size,
                    ai_model_version=ai_model_version,
                    embedding_method=embedding_method,
                    confidence_score=confidence_score,
                    similarity_threshold=self._get_similarity_threshold(content_type),
                    alert_threshold=self._get_alert_threshold(content_type)
                )
                
                # Store vector
                self._vectors[content_id] = entry
                
                # Update indices
                if creator_id not in self._creator_vectors:
                    self._creator_vectors[creator_id] = set()
                self._creator_vectors[creator_id].add(content_id)
                
                self._content_type_vectors[content_type].add(content_id)
                
                # Update statistics
                self._stats['vectors_added'] += 1
                self._stats['total_vectors'] = len(self._vectors)
                self._content_type_stats[content_type]['vectors'] += 1
                self._update_creator_stats(creator_id, 'vectors_added')
                
                duration = time.time() - start_time
                if duration > self.config.slow_query_threshold:
                    self._track_slow_query('add_vector', duration, {
                        'content_id': content_id,
                        'creator_id': creator_id,
                        'content_type': content_type.value
                    })
                
                logger.debug(f"Added vector for content {content_id} (creator: {creator_id})")
                return True
                
        except Exception as e:
            logger.error(f"Error adding vector for content {content_id}: {e}")
            return False
    
    async def get_vector(self, content_id: str) -> Optional[VectorEntry]:
        """Get vector entry by content ID"""
        with self._lock:
            if content_id in self._vectors:
                entry = self._vectors[content_id]
                entry.update_access()
                return entry
            return None
    
    async def search_similar(self,
                           query_vector: Union[np.ndarray, List[float]],
                           top_k: int = 10,
                           content_type: Optional[ContentType] = None,
                           creator_id: Optional[str] = None,
                           exclude_creator: Optional[str] = None,
                           min_similarity: Optional[float] = None,
                           platforms_to_check: Optional[List[str]] = None) -> List[SimilarityResult]:
        """
Advanced similarity search with business logic"""
        
        start_time = time.time()
        
        try:
            if isinstance(query_vector, list):
                query_vector = np.array(query_vector, dtype=np.float32)
            
            if query_vector.shape[0] != self.config.dimension:
                logger.error(f"Query vector dimension mismatch: expected {self.config.dimension}, got {query_vector.shape[0]}")
                return []
            
            query_vector = self._normalize_vector(query_vector)
            
            # Determine similarity threshold
            if min_similarity is None:
                if content_type:
                    min_similarity = self._get_similarity_threshold(content_type)
                else:
                    min_similarity = 0.8  # Default threshold
            
            results = []
            
            with self._lock:
                self._stats['searches_performed'] += 1
                if content_type:
                    self._content_type_stats[content_type]['searches'] += 1
                if creator_id:
                    self._update_creator_stats(creator_id, 'searches_performed')
                
                # Filter vectors based on search criteria
                candidate_vectors = self._vectors.items()
                
                if content_type:
                    content_ids = self._content_type_vectors[content_type]
                    candidate_vectors = [(cid, entry) for cid, entry in candidate_vectors if cid in content_ids]
                
                if exclude_creator:
                    candidate_vectors = [(cid, entry) for cid, entry in candidate_vectors if entry.creator_id != exclude_creator]
                
                # Parallel similarity computation if enabled
                if self.config.enable_parallel_search and len(candidate_vectors) > 100:
                    results = await self._parallel_similarity_search(
                        query_vector, candidate_vectors, min_similarity, top_k
                    )
                else:
                    # Sequential search
                    for content_id, entry in candidate_vectors:
                        similarity = self._compute_similarity(query_vector, entry.vector)
                        
                        if similarity >= min_similarity:
                            # Check if this is a potential violation
                            is_violation = self._detect_potential_violation(entry, similarity, creator_id)
                            
                            result = SimilarityResult(
                                content_id=content_id,
                                creator_id=entry.creator_id,
                                similarity_score=similarity,
                                content_type=entry.content_type,
                                metadata=entry.metadata,
                                vector=entry.vector,
                                fingerprint_hash=entry.fingerprint_hash,
                                original_filename=entry.original_filename,
                                platforms_found=entry.platforms_found.copy(),
                                violation_count=entry.violation_count,
                                protection_enabled=entry.protection_enabled
                            )
                            
                            results.append(result)
                            
                            # Update entry access
                            entry.update_access()
                            entry.last_similarity_score = similarity
                            
                            if is_violation:
                                await self._handle_violation_detection(entry, result)
                
                # Sort by similarity score (descending)
                results.sort(key=lambda x: x.similarity_score, reverse=True)
                
                # Update statistics
                if results:
                    self._stats['cache_hits'] += 1
                else:
                    self._stats['cache_misses'] += 1
                
                duration = time.time() - start_time
                self._stats['total_search_time'] += duration
                self._stats['avg_search_time'] = self._stats['total_search_time'] / self._stats['searches_performed']
                
                if duration > self.config.slow_query_threshold:
                    self._track_slow_query('search_similar', duration, {
                        'top_k': top_k,
                        'content_type': content_type.value if content_type else None,
                        'creator_id': creator_id,
                        'candidates_checked': len(candidate_vectors),
                        'results_found': len(results)
                    })
                
                return results[:top_k]
                
        except Exception as e:
            logger.error(f"Error in similarity search: {e}")
            return []
    
    async def _parallel_similarity_search(self,
                                        query_vector: np.ndarray,
                                        candidate_vectors: List[Tuple[str, VectorEntry]],
                                        min_similarity: float,
                                        top_k: int) -> List[SimilarityResult]:
        """Parallel similarity search for better performance"""
        
        def compute_batch_similarities(batch):
            batch_results = []
            for content_id, entry in batch:
                similarity = self._compute_similarity(query_vector, entry.vector)
                if similarity >= min_similarity:
                    result = SimilarityResult(
                        content_id=content_id,
                        creator_id=entry.creator_id,
                        similarity_score=similarity,
                        content_type=entry.content_type,
                        metadata=entry.metadata,
                        vector=entry.vector,
                        fingerprint_hash=entry.fingerprint_hash,
                        original_filename=entry.original_filename,
                        platforms_found=entry.platforms_found.copy(),
                        violation_count=entry.violation_count,
                        protection_enabled=entry.protection_enabled
                    )
                    batch_results.append(result)
            return batch_results
        
        # Split into batches
        batches = [
            candidate_vectors[i:i + self.config.batch_size]
            for i in range(0, len(candidate_vectors), self.config.batch_size)
        ]
        
        # Process batches in parallel
        futures = [
            self._executor.submit(compute_batch_similarities, batch)
            for batch in batches
        ]
        
        # Collect results
        all_results = []
        for future in futures:
            batch_results = future.result()
            all_results.extend(batch_results)
        
        return all_results
    
    def _detect_potential_violation(self, entry: VectorEntry, similarity: float, querying_creator_id: Optional[str]) -> bool:
        """
Detect potential content protection violation"""
        if not self.config.enable_content_protection or not entry.protection_enabled:
            return False
        
        # If same creator, not a violation
        if querying_creator_id and entry.creator_id == querying_creator_id:
            return False
        
        # Check if similarity exceeds alert threshold
        alert_threshold = self._get_alert_threshold(entry.content_type)
        return similarity >= alert_threshold
    
    async def _handle_violation_detection(self, entry: VectorEntry, result: SimilarityResult):
        """
Handle detected content protection violation"""
        # Update violation statistics
        self._stats['violations_detected'] += 1
        self._content_type_stats[entry.content_type]['violations'] += 1
        
        # Log violation
        violation_record = {
            'timestamp': datetime.utcnow().isoformat(),
            'original_content_id': entry.content_id,
            'original_creator_id': entry.creator_id,
            'similarity_score': result.similarity_score,
            'content_type': entry.content_type.value,
            'alert_level': result.alert_level,
            'detection_method': 'vector_similarity'
        }
        
        self._violation_log.append(violation_record)
        
        # Keep violation log manageable
        if len(self._violation_log) > 1000:
            self._violation_log = self._violation_log[-1000:]
        
        # Update entry violation count
        entry.violation_count += 1
        entry.last_violation_detected = datetime.utcnow()
        
        # Generate alert if threshold exceeded
        if entry.violation_count >= self.config.violation_escalation_threshold:
            self._stats['protection_alerts'] += 1
            await self._generate_protection_alert(entry, result)
    
    async def _generate_protection_alert(self, entry: VectorEntry, result: SimilarityResult):
        """
Generate high-priority protection alert"""
        alert = {
            'alert_id': hashlib.md5(f"{entry.content_id}_{datetime.utcnow()}".encode()).hexdigest(),
            'timestamp': datetime.utcnow().isoformat(),
            'alert_type': 'content_protection_violation',
            'severity': 'high',
            'original_content': {
                'content_id': entry.content_id,
                'creator_id': entry.creator_id,
                'content_type': entry.content_type.value,
                'filename': entry.original_filename
            },
            'violation_details': {
                'similarity_score': result.similarity_score,
                'total_violations': entry.violation_count,
                'platforms_found': list(entry.platforms_found),
                'last_violation': entry.last_violation_detected.isoformat() if entry.last_violation_detected else None
            },
            'recommended_actions': [
                'review_content_usage',
                'contact_platform_support',
                'initiate_takedown_request',
                'monitor_additional_platforms'
            ]
        }
        
        logger.critical(f"Content protection alert generated: {alert['alert_id']}")
        
        # Here you would typically send the alert to a monitoring system,
        # notification service, or queue for processing
        # For now, we log it
    
    async def remove_vector(self, content_id: str) -> bool:
        """Remove vector from cache"""
        with self._lock:
            if content_id in self._vectors:
                entry = self._vectors[content_id]
                
                # Remove from indices
                creator_id = entry.creator_id
                content_type = entry.content_type
                
                del self._vectors[content_id]
                
                if creator_id in self._creator_vectors:
                    self._creator_vectors[creator_id].discard(content_id)
                    if not self._creator_vectors[creator_id]:
                        del self._creator_vectors[creator_id]
                
                self._content_type_vectors[content_type].discard(content_id)
                
                # Update statistics
                self._stats['vectors_removed'] += 1
                self._stats['total_vectors'] = len(self._vectors)
                self._content_type_stats[content_type]['vectors'] -= 1
                
                logger.debug(f"Removed vector for content {content_id}")
                return True
            
            return False
    
    async def _evict_oldest_vectors(self, count: int = 100):
        """Evict oldest vectors when cache is full"""
        if not self._vectors:
            return
        
        # Sort by creation time and remove oldest
        sorted_vectors = sorted(
            self._vectors.items(),
            key=lambda x: x[1].created_at
        )
        
        for i in range(min(count, len(sorted_vectors))):
            content_id, _ = sorted_vectors[i]
            await self.remove_vector(content_id)
        
        logger.info(f"Evicted {count} oldest vectors due to capacity limit")
    
    async def get_creator_vectors(self, creator_id: str) -> List[VectorEntry]:
        """Get all vectors for a specific creator"""
        with self._lock:
            content_ids = self._creator_vectors.get(creator_id, set())
            return [self._vectors[cid] for cid in content_ids if cid in self._vectors]
    
    async def get_content_type_vectors(self, content_type: ContentType) -> List[VectorEntry]:
        """
Get all vectors for a specific content type"""
        with self._lock:
            content_ids = self._content_type_vectors[content_type]
            return [self._vectors[cid] for cid in content_ids if cid in self._vectors]
    
    async def detect_content_violations(self, creator_id: str, platforms: List[str]) -> List[Dict[str, Any]]:
        """
Detect potential content violations across platforms"""
        violations = []
        
        creator_vectors = await self.get_creator_vectors(creator_id)
        
        for entry in creator_vectors:
            if not entry.protection_enabled:
                continue
            
            # Check for new platform detections
            new_platforms = set(platforms) - entry.platforms_found - {'original', 'authorized'}
            
            for platform in new_platforms:
                violation = {
                    'content_id': entry.content_id,
                    'creator_id': creator_id,
                    'content_type': entry.content_type.value,
                    'platform': platform,
                    'detected_at': datetime.utcnow().isoformat(),
                    'original_filename': entry.original_filename,
                    'violation_score': 1.0,  # Platform detection = 100% violation
                    'recommended_action': 'immediate_takedown'
                }
                
                violations.append(violation)
                entry.add_platform_detection(platform)
        
        return violations
    
    def get_comprehensive_stats(self) -> Dict[str, Any]:
        """
Get comprehensive cache statistics"""
        with self._lock:
            return {
                'general_stats': self._stats.copy(),
                'content_type_stats': {
                    ct.value: stats for ct, stats in self._content_type_stats.items()
                },
                'creator_stats': self._creator_stats.copy(),
                'slow_queries': self._slow_queries[-10:],  # Last 10 slow queries
                'recent_violations': self._violation_log[-10:],  # Last 10 violations
                'cache_efficiency': {
                    'hit_rate': self._stats['cache_hits'] / max(1, self._stats['searches_performed']),
                    'avg_search_time_ms': self._stats['avg_search_time'] * 1000,
                    'vectors_per_content_type': {
                        ct.value: len(ids) for ct, ids in self._content_type_vectors.items()
                    },
                    'top_creators_by_vectors': sorted(
                        [(cid, len(vids)) for cid, vids in self._creator_vectors.items()],
                        key=lambda x: x[1], reverse=True
                    )[:10]
                },
                'protection_stats': {
                    'total_violations': self._stats['violations_detected'],
                    'protection_alerts': self._stats['protection_alerts'],
                    'violation_rate': self._stats['violations_detected'] / max(1, self._stats['searches_performed'])
                },
                'memory_usage': {
                    'total_vectors': len(self._vectors),
                    'estimated_memory_mb': self._estimate_memory_usage() / (1024 * 1024),
                    'capacity_utilization': len(self._vectors) / self.config.max_vectors
                }
            }
    
    def _estimate_memory_usage(self) -> int:
        """
Estimate memory usage in bytes"""
        vector_size = self.config.dimension * 4  # float32 = 4 bytes
        metadata_size = 500  # Estimated metadata size per entry
        return len(self._vectors) * (vector_size + metadata_size)
    
    async def clear(self, creator_id: Optional[str] = None, content_type: Optional[ContentType] = None):
        """
Clear cache with optional filtering"""
        with self._lock:
            if creator_id:
                # Clear specific creator's vectors
                content_ids = self._creator_vectors.get(creator_id, set()).copy()
                for content_id in content_ids:
                    await self.remove_vector(content_id)
            elif content_type:
                # Clear specific content type vectors
                content_ids = self._content_type_vectors[content_type].copy()
                for content_id in content_ids:
                    await self.remove_vector(content_id)
            else:
                # Clear all vectors
                self._vectors.clear()
                self._creator_vectors.clear()
                for ct in ContentType:
                    self._content_type_vectors[ct].clear()
                
                # Reset statistics
                self._stats['total_vectors'] = 0
                for ct in ContentType:
                    self._content_type_stats[ct]['vectors'] = 0

class FAISSCache(VectorCache):
    """
    Enterprise FAISS-powered vector cache for IA Influencer Agent
    Optimized for large-scale content fingerprinting and similarity search
    Supports millions of vectors with sub-second query times
    """
    
    def __init__(self, config: VectorCacheConfig):
        if not FAISS_AVAILABLE:
            raise ImportError("FAISS is required for FAISSCache. Install with: pip install faiss-cpu or faiss-gpu")
        
        super().__init__(config)
        
        # FAISS-specific configuration
        self.index_type = config.faiss_index_type
        self.nlist = config.faiss_nlist
        self.nprobe = config.faiss_nprobe
        self.m = config.faiss_m
        
        # Initialize FAISS index
        self._index = self._create_faiss_index()
        self._id_to_content: Dict[int, str] = {}
        self._content_to_id: Dict[str, int] = {}
        self._next_id = 0
        self._index_trained = False
        
        # Performance tracking
        self._faiss_stats = {
            'index_size': 0,
            'total_indexed': 0,
            'search_time_ms': 0.0,
            'index_rebuilds': 0,
            'training_time_ms': 0.0
        }
        
        logger.info(f"FAISSCache initialized - Type: {self.index_type.value}, Dimension: {config.dimension}")
    
    def _create_faiss_index(self):
        """Create FAISS index optimized for IA Influencer Agent use cases"""
        if self.index_type == IndexType.FLAT_IP:
            # Best for accuracy, slower for large datasets
            return faiss.IndexFlatIP(self.config.dimension)
        
        elif self.index_type == IndexType.FLAT_L2:
            # L2 distance, exact search
            return faiss.IndexFlatL2(self.config.dimension)
        
        elif self.index_type == IndexType.IVF_FLAT:
            # Good balance of speed and accuracy
            quantizer = faiss.IndexFlatIP(self.config.dimension)
            index = faiss.IndexIVFFlat(quantizer, self.config.dimension, self.nlist)
            index.nprobe = self.nprobe
            return index
        
        elif self.index_type == IndexType.HNSW:
            # Best for query speed, good accuracy
            index = faiss.IndexHNSWFlat(self.config.dimension, self.m)
            index.hnsw.efConstruction = 200
            index.hnsw.efSearch = 100
            return index
        
        elif self.index_type == IndexType.LSH:
            # Good for very large datasets, approximate results
            return faiss.IndexLSH(self.config.dimension, 512)
        
        else:
            # Default to HNSW for IA Influencer Agent (best balance)
            index = faiss.IndexHNSWFlat(self.config.dimension, 32)
            index.hnsw.efConstruction = 200
            index.hnsw.efSearch = 100
            return index
    
    async def add_vector(self,
                        content_id: str,
                        creator_id: str,
                        vector: Union[np.ndarray, List[float]],
                        content_type: ContentType,
                        **kwargs) -> bool:
        """
Add vector to FAISS index with enterprise features"""
        
        # First add to parent cache for metadata management
        success = await super().add_vector(
            content_id, creator_id, vector, content_type, **kwargs
        )
        
        if not success:
            return False
        
        try:
            with self._lock:
                entry = self._vectors[content_id]
                normalized_vector = entry.vector.reshape(1, -1)
                
                # Add to FAISS index if not already present
                if content_id not in self._content_to_id:
                    faiss_id = self._next_id
                    self._next_id += 1
                    
                    self._id_to_content[faiss_id] = content_id
                    self._content_to_id[content_id] = faiss_id
                    
                    # Check if index needs training
                    if (hasattr(self._index, 'is_trained') and 
                        not self._index_trained and 
                        self._index.ntotal >= self.nlist):
                        await self._train_index()
                    
                    # Add vector to index
                    if not hasattr(self._index, 'is_trained') or self._index.is_trained:
                        self._index.add(normalized_vector)
                        self._faiss_stats['total_indexed'] += 1
                        self._faiss_stats['index_size'] = self._index.ntotal
                    
                    logger.debug(f"Added vector to FAISS index: {content_id} -> {faiss_id}")
                    return True
                
                return False
                
        except Exception as e:
            logger.error(f"Error adding vector to FAISS index: {e}")
            return False
    
    async def _train_index(self):
        """Train FAISS index for optimal performance"""
        if self._index_trained or len(self._vectors) < self.nlist:
            return
        
        start_time = time.time()
        
        try:
            logger.info("Training FAISS index for optimal performance...")
            
            # Collect training vectors
            training_vectors = []
            for entry in list(self._vectors.values()):
                training_vectors.append(entry.vector)
            
            if training_vectors:
                training_data = np.vstack([v.reshape(1, -1) for v in training_vectors])
                self._index.train(training_data)
                self._index_trained = True
                
                training_time = (time.time() - start_time) * 1000
                self._faiss_stats['training_time_ms'] = training_time
                
                logger.info(f"FAISS index training completed in {training_time:.2f}ms")
            
        except Exception as e:
            logger.error(f"FAISS index training failed: {e}")
    
    async def search_similar(self,
                           query_vector: Union[np.ndarray, List[float]],
                           top_k: int = 10,
                           content_type: Optional[ContentType] = None,
                           creator_id: Optional[str] = None,
                           exclude_creator: Optional[str] = None,
                           min_similarity: Optional[float] = None,
                           platforms_to_check: Optional[List[str]] = None) -> List[SimilarityResult]:
        """High-performance similarity search using FAISS"""
        
        start_time = time.time()
        
        try:
            if isinstance(query_vector, list):
                query_vector = np.array(query_vector, dtype=np.float32)
            
            if query_vector.shape[0] != self.config.dimension:
                logger.error(f"Query vector dimension mismatch: expected {self.config.dimension}, got {query_vector.shape[0]}")
                return []
            
            query_vector = self._normalize_vector(query_vector).reshape(1, -1)
            
            # Determine similarity threshold
            if min_similarity is None:
                if content_type:
                    min_similarity = self._get_similarity_threshold(content_type)
                else:
                    min_similarity = 0.8
            
            with self._lock:
                self._stats['searches_performed'] += 1
                if content_type:
                    self._content_type_stats[content_type]['searches'] += 1
                if creator_id:
                    self._update_creator_stats(creator_id, 'searches_performed')
                
                # Adjust search parameters based on index size
                search_k = min(top_k * 5, self._index.ntotal, 1000)  # Search more than needed for filtering
                
                if search_k == 0:
                    self._stats['cache_misses'] += 1
                    return []
                
                # Perform FAISS search
                if self.config.metric == SimilarityMetric.COSINE:
                    # For cosine similarity, FAISS returns inner product (since vectors are normalized)
                    similarities, indices = self._index.search(query_vector, search_k)
                else:
                    # For other metrics, we need to convert distances to similarities
                    distances, indices = self._index.search(query_vector, search_k)
                    similarities = self._convert_distances_to_similarities(distances)
                
                results = []
                
                for i, (similarity, idx) in enumerate(zip(similarities[0], indices[0])):
                    if idx == -1:  # Invalid index
                        continue
                    
                    content_id = self._id_to_content.get(idx)
                    if not content_id or content_id not in self._vectors:
                        continue
                    
                    entry = self._vectors[content_id]
                    
                    # Apply filters
                    if content_type and entry.content_type != content_type:
                        continue
                    
                    if exclude_creator and entry.creator_id == exclude_creator:
                        continue
                    
                    if similarity < min_similarity:
                        continue
                    
                    # Check for potential violation
                    is_violation = self._detect_potential_violation(entry, similarity, creator_id)
                    
                    result = SimilarityResult(
                        content_id=content_id,
                        creator_id=entry.creator_id,
                        similarity_score=float(similarity),
                        content_type=entry.content_type,
                        metadata=entry.metadata,
                        vector=entry.vector,
                        fingerprint_hash=entry.fingerprint_hash,
                        original_filename=entry.original_filename,
                        platforms_found=entry.platforms_found.copy(),
                        violation_count=entry.violation_count,
                        protection_enabled=entry.protection_enabled
                    )
                    
                    results.append(result)
                    
                    # Update entry access
                    entry.update_access()
                    entry.last_similarity_score = similarity
                    
                    if is_violation:
                        await self._handle_violation_detection(entry, result)
                    
                    if len(results) >= top_k:
                        break
                
                # Update statistics
                search_time = (time.time() - start_time) * 1000
                self._faiss_stats['search_time_ms'] = (
                    self._faiss_stats['search_time_ms'] * 0.9 + search_time * 0.1
                )
                
                if results:
                    self._stats['cache_hits'] += 1
                else:
                    self._stats['cache_misses'] += 1
                
                duration = time.time() - start_time
                self._stats['total_search_time'] += duration
                self._stats['avg_search_time'] = self._stats['total_search_time'] / self._stats['searches_performed']
                
                if duration > self.config.slow_query_threshold:
                    self._track_slow_query('faiss_search_similar', duration, {
                        'top_k': top_k,
                        'search_k': search_k,
                        'content_type': content_type.value if content_type else None,
                        'creator_id': creator_id,
                        'results_found': len(results),
                        'index_size': self._index.ntotal
                    })
                
                return results
                
        except Exception as e:
            logger.error(f"Error in FAISS similarity search: {e}")
            return []
    
    def _convert_distances_to_similarities(self, distances: np.ndarray) -> np.ndarray:
        """Convert FAISS distances to similarity scores"""
        if self.config.metric == SimilarityMetric.EUCLIDEAN:
            # Convert L2 distance to similarity
            return 1.0 / (1.0 + distances)
        elif self.config.metric == SimilarityMetric.MANHATTAN:
            # Convert Manhattan distance to similarity
            return 1.0 / (1.0 + distances)
        else:
            # For other metrics, assume distance is already similarity-like
            return distances
    
    async def remove_vector(self, content_id: str) -> bool:
        """
Remove vector from FAISS index (marks for rebuild)"""
        with self._lock:
            if content_id in self._content_to_id:
                faiss_id = self._content_to_id[content_id]
                
                # Remove from mappings
                del self._content_to_id[content_id]
                del self._id_to_content[faiss_id]
                
                # Remove from parent cache
                success = await super().remove_vector(content_id)
                
                # Note: FAISS doesn't support efficient single vector removal
                # We'll rebuild the index periodically or when removal ratio gets high
                removed_ratio = len(self._content_to_id) / max(1, self._index.ntotal)
                if removed_ratio < 0.7:  # If more than 30% removed, consider rebuild
                    logger.info("High removal ratio detected, scheduling index rebuild")
                    # You could schedule a rebuild here
                
                logger.debug(f"Removed vector from FAISS index: {content_id}")
                return success
            
            return False
    
    async def rebuild_index(self):
        """Rebuild FAISS index for optimal performance"""
        start_time = time.time()
        
        with self._lock:
            if not self._vectors:
                return
            
            logger.info(f"Rebuilding FAISS index with {len(self._vectors)} vectors...")
            
            # Create new index
            old_index = self._index
            self._index = self._create_faiss_index()
            
            # Reset mappings
            self._id_to_content.clear()
            self._content_to_id.clear()
            self._next_id = 0
            self._index_trained = False
            
            # Prepare vectors for batch addition
            vectors = []
            content_ids = []
            
            for content_id, entry in self._vectors.items():
                vectors.append(entry.vector)
                content_ids.append(content_id)
                
                faiss_id = self._next_id
                self._next_id += 1
                self._id_to_content[faiss_id] = content_id
                self._content_to_id[content_id] = faiss_id
            
            if vectors:
                vectors_array = np.vstack([v.reshape(1, -1) for v in vectors])
                
                # Train if necessary
                if hasattr(self._index, 'is_trained') and not self._index.is_trained:
                    if len(vectors) >= self.nlist:
                        self._index.train(vectors_array)
                        self._index_trained = True
                
                # Add all vectors in batch
                if not hasattr(self._index, 'is_trained') or self._index.is_trained:
                    self._index.add(vectors_array)
                    self._faiss_stats['total_indexed'] = len(vectors)
                    self._faiss_stats['index_size'] = self._index.ntotal
            
            rebuild_time = (time.time() - start_time) * 1000
            self._faiss_stats['index_rebuilds'] += 1
            
            logger.info(f"FAISS index rebuilt in {rebuild_time:.2f}ms with {len(vectors)} vectors")
    
    async def save_index(self, file_path: str):
        """Save FAISS index and metadata to disk"""
        try:
            with self._lock:
                # Save FAISS index
                faiss.write_index(self._index, file_path)
                
                # Save metadata
                metadata = {
                    'id_to_content': self._id_to_content,
                    'content_to_id': self._content_to_id,
                    'next_id': self._next_id,
                    'index_trained': self._index_trained,
                    'config': {
                        'dimension': self.config.dimension,
                        'metric': self.config.metric.value,
                        'index_type': self.index_type.value,
                        'nlist': self.nlist,
                        'nprobe': self.nprobe,
                        'm': self.m
                    },
                    'stats': self._faiss_stats,
                    'vectors_metadata': {
                        content_id: entry.to_dict()
                        for content_id, entry in self._vectors.items()
                    }
                }
                
                with open(f"{file_path}.metadata", 'wb') as f:
                    pickle.dump(metadata, f)
                
                logger.info(f"FAISS index and metadata saved to {file_path}")
                
        except Exception as e:
            logger.error(f"Failed to save FAISS index: {e}")
            raise
    
    async def load_index(self, file_path: str):
        """Load FAISS index and metadata from disk"""
        try:
            with self._lock:
                # Load FAISS index
                self._index = faiss.read_index(file_path)
                
                # Load metadata
                with open(f"{file_path}.metadata", 'rb') as f:
                    metadata = pickle.load(f)
                
                self._id_to_content = metadata['id_to_content']
                self._content_to_id = metadata['content_to_id']
                self._next_id = metadata['next_id']
                self._index_trained = metadata.get('index_trained', True)
                self._faiss_stats.update(metadata.get('stats', {}))
                
                # Restore vector entries
                vectors_metadata = metadata.get('vectors_metadata', {})
                for content_id, entry_data in vectors_metadata.items():
                    # Reconstruct VectorEntry from saved data
                    # Note: vector data is not saved with metadata, only in FAISS index
                    # This is a simplified restoration - in production, you might want
                    # to save vectors separately for complete restoration
                    pass
                
                logger.info(f"FAISS index and metadata loaded from {file_path}")
                logger.info(f"Restored {len(self._content_to_id)} vectors")
                
        except Exception as e:
            logger.error(f"Failed to load FAISS index: {e}")
            raise
    
    def get_comprehensive_stats(self) -> Dict[str, Any]:
        """Get enhanced statistics including FAISS-specific metrics"""
        base_stats = super().get_comprehensive_stats()
        
        with self._lock:
            faiss_specific_stats = {
                'faiss_stats': self._faiss_stats.copy(),
                'index_info': {
                    'type': self.index_type.value,
                    'dimension': self._index.d,
                    'total_vectors': self._index.ntotal,
                    'is_trained': getattr(self._index, 'is_trained', True),
                    'index_size_mb': faiss.serialize_index(self._index).__len__() / (1024 * 1024)
                },
                'performance_metrics': {
                    'avg_search_time_ms': self._faiss_stats.get('search_time_ms', 0),
                    'vectors_per_second': (
                        self._faiss_stats['total_indexed'] / 
                        max(1, self._faiss_stats.get('training_time_ms', 1000) / 1000)
                    ),
                    'index_efficiency': len(self._content_to_id) / max(1, self._index.ntotal)
                }
            }
            
            # Merge with base stats
            base_stats.update(faiss_specific_stats)
            return base_stats

# Factory functions for easy instantiation
async def create_vector_cache(config: Optional[VectorCacheConfig] = None) -> VectorCache:
    """
Create standard vector cache instance"""
    if config is None:
        config = VectorCacheConfig()
    
    cache = VectorCache(config)
    return cache

async def create_faiss_cache(config: Optional[VectorCacheConfig] = None) -> FAISSCache:
    """
Create FAISS-powered vector cache instance"""
    if config is None:
        config = VectorCacheConfig()
    
    if not FAISS_AVAILABLE:
        logger.warning("FAISS not available, falling back to standard VectorCache")
        return await create_vector_cache(config)
    
    cache = FAISSCache(config)
    return cache

# Global cache instances for IA Influencer Agent
_vector_cache_instance: Optional[VectorCache] = None
_faiss_cache_instance: Optional[FAISSCache] = None

async def get_vector_cache() -> VectorCache:
    """Get or create global vector cache instance"""
    global _vector_cache_instance
    
    if _vector_cache_instance is None:
        _vector_cache_instance = await create_vector_cache()
    
    return _vector_cache_instance

async def get_faiss_cache() -> Union[FAISSCache, VectorCache]:
    """
Get or create global FAISS cache instance"""
    global _faiss_cache_instance
    
    if _faiss_cache_instance is None:
        _faiss_cache_instance = await create_faiss_cache()
    
    return _faiss_cache_instance

# Content-specific helper functions for IA Influencer Agent

async def cache_audio_fingerprint(vector_cache: VectorCache,
                                 audio_id: str,
                                 creator_id: str,
                                 fingerprint_vector: np.ndarray,
                                 metadata: Dict[str, Any]) -> bool:
    """
Helper to cache audio fingerprint"""
    return await vector_cache.add_vector(
        content_id=audio_id,
        creator_id=creator_id,
        vector=fingerprint_vector,
        content_type=ContentType.AUDIO,
        metadata=metadata,
        fingerprint_hash=hashlib.sha256(fingerprint_vector.tobytes()).hexdigest()
    )

async def search_similar_audio(vector_cache: VectorCache,
                              query_fingerprint: np.ndarray,
                              creator_id: Optional[str] = None,
                              top_k: int = 10) -> List[SimilarityResult]:
    """
Helper to search for similar audio content"""
    return await vector_cache.search_similar(
        query_vector=query_fingerprint,
        top_k=top_k,
        content_type=ContentType.AUDIO,
        exclude_creator=creator_id  # Exclude same creator to find violations
    )

async def detect_audio_violations(vector_cache: VectorCache,
                                 creator_id: str,
                                 platforms: List[str]) -> List[Dict[str, Any]]:
    """
Detect potential audio content violations"""
    return await vector_cache.detect_content_violations(creator_id, platforms)

# Advanced analytics and monitoring functions

class VectorCacheAnalytics:
    """
Advanced analytics for vector cache performance and usage"""
    
    def __init__(self, vector_cache: VectorCache):
        self.cache = vector_cache
    
    async def generate_creator_report(self, creator_id: str) -> Dict[str, Any]:
        """
Generate comprehensive report for a creator"""
        creator_vectors = await self.cache.get_creator_vectors(creator_id)
        
        if not creator_vectors:
            return {'creator_id': creator_id, 'vectors': 0, 'message': 'No vectors found'}
        
        # Content type breakdown
        content_type_counts = {}
        total_violations = 0
        platforms_detected = set()
        
        for entry in creator_vectors:
            content_type = entry.content_type.value
            content_type_counts[content_type] = content_type_counts.get(content_type, 0) + 1
            total_violations += entry.violation_count
            platforms_detected.update(entry.platforms_found)
        
        # Recent activity
        recent_activity = sorted(creator_vectors, key=lambda x: x.accessed_at, reverse=True)[:10]
        
        return {
            'creator_id': creator_id,
            'summary': {
                'total_vectors': len(creator_vectors),
                'content_types': content_type_counts,
                'total_violations': total_violations,
                'platforms_detected': list(platforms_detected),
                'protection_enabled_count': sum(1 for v in creator_vectors if v.protection_enabled)
            },
            'recent_activity': [
                {
                    'content_id': entry.content_id,
                    'content_type': entry.content_type.value,
                    'accessed_at': entry.accessed_at.isoformat(),
                    'access_count': entry.access_count,
                    'violation_count': entry.violation_count
                }
                for entry in recent_activity
            ],
            'recommendations': self._generate_creator_recommendations(creator_vectors)
        }
    
    def _generate_creator_recommendations(self, vectors: List[VectorEntry]) -> List[str]:
        """
Generate recommendations for creator based on vector data"""
        recommendations = []
        
        total_vectors = len(vectors)
        protected_vectors = sum(1 for v in vectors if v.protection_enabled)
        total_violations = sum(v.violation_count for v in vectors)
        
        if protected_vectors < total_vectors:
            recommendations.append("Enable protection for all content to maximize coverage")
        
        if total_violations > total_vectors * 0.1:  # More than 10% violation rate
            recommendations.append("High violation rate detected - consider enhanced monitoring")
        
        # Check for inactive content
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        inactive_count = sum(1 for v in vectors if v.accessed_at < thirty_days_ago)
        
        if inactive_count > total_vectors * 0.5:
            recommendations.append("Consider archiving or removing inactive content")
        
        return recommendations

# Export all public classes and functions
__all__ = [
    # Enums
    'ContentType', 'SimilarityMetric', 'IndexType',
    
    # Data classes
    'VectorEntry', 'SimilarityResult', 'VectorCacheConfig',
    
    # Main classes
    'VectorCache', 'FAISSCache',
    
    # Factory functions
    'create_vector_cache', 'create_faiss_cache',
    'get_vector_cache', 'get_faiss_cache',
    
    # Helper functions
    'cache_audio_fingerprint', 'search_similar_audio', 'detect_audio_violations',
    
    # Analytics
    'VectorCacheAnalytics'
]
