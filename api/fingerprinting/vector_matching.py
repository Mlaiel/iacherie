"""
Advanced Vector Matching System for Content Protection
=====================================================
High-performance FAISS-based similarity search and matching engine.

Author: Fahed Mlaiel (mlaiel@live.de)  
Team: IA-Influencer-Agent Expert Development Team

Features:
- Real-time vector similarity search using FAISS
- Multi-index support for different content types
- Advanced clustering and indexing strategies
- Scalable architecture for millions of fingerprints
- Real-time matching with <100ms response time
"""

import numpy as np
import faiss
import pickle
import asyncio
from typing import Dict, List, Optional, Tuple, Any
from pathlib import Path
from dataclasses import dataclass
import logging
from concurrent.futures import ThreadPoolExecutor
import threading
from datetime import datetime
import json

logger = logging.getLogger(__name__)


@dataclass
class VectorMatchConfig:
    """Configuration for vector matching operations."""
    index_type: str = "flat"  # flat, ivf, hnsw, pq
    vector_dimension: int = 512
    similarity_threshold: float = 0.85
    max_results: int = 100
    ivf_clusters: int = 1000
    hnsw_m: int = 16
    hnsw_ef_construction: int = 200
    hnsw_ef_search: int = 50
    pq_subvectors: int = 64


@dataclass 
class MatchResult:
    """Result of a similarity match operation."""
    content_id: int
    similarity_score: float
    content_type: str
    fingerprint_hash: str
    metadata: Dict[str, Any]
    match_timestamp: datetime
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'content_id': self.content_id,
            'similarity_score': self.similarity_score,
            'content_type': self.content_type,
            'fingerprint_hash': self.fingerprint_hash,
            'metadata': self.metadata,
            'match_timestamp': self.match_timestamp.isoformat()
        }


class IndexManager:
    """Manages FAISS indices for different content types."""
    
    def __init__(self, config: VectorMatchConfig):
        self.config = config
        self.indices: Dict[str, faiss.Index] = {}
        self.content_mappings: Dict[str, Dict[int, Dict]] = {}
        self.index_locks: Dict[str, threading.Lock] = {}
        self.logger = logging.getLogger(__name__)
        
        # Thread pool for async operations
        self.executor = ThreadPoolExecutor(max_workers=4)
    
    def create_index(self, content_type: str) -> faiss.Index:
        """Create optimized FAISS index for specific content type."""
        try:
            if self.config.index_type == "flat":
                # Flat index for exact search (best quality)
                index = faiss.IndexFlatIP(self.config.vector_dimension)
                
            elif self.config.index_type == "ivf":
                # IVF index for faster search with clustering
                quantizer = faiss.IndexFlatIP(self.config.vector_dimension)
                index = faiss.IndexIVFFlat(
                    quantizer, 
                    self.config.vector_dimension, 
                    self.config.ivf_clusters
                )
                
            elif self.config.index_type == "hnsw":
                # HNSW index for very fast approximate search
                index = faiss.IndexHNSWFlat(
                    self.config.vector_dimension, 
                    self.config.hnsw_m
                )
                index.hnsw.efConstruction = self.config.hnsw_ef_construction
                index.hnsw.efSearch = self.config.hnsw_ef_search
                
            elif self.config.index_type == "pq":
                # Product Quantization for memory efficiency
                index = faiss.IndexPQ(
                    self.config.vector_dimension,
                    self.config.pq_subvectors,
                    8  # 8 bits per subvector
                )
                
            else:
                raise ValueError(f"Unsupported index type: {self.config.index_type}")
            
            # Initialize content mapping and lock for this content type
            self.content_mappings[content_type] = {}
            self.index_locks[content_type] = threading.Lock()
            
            self.logger.info(
                f"Created {self.config.index_type} index for {content_type} "
                f"with {self.config.vector_dimension}D vectors"
            )
            
            return index
            
        except Exception as e:
            self.logger.error(f"Index creation failed for {content_type}: {str(e)}")
            raise
    
    def get_or_create_index(self, content_type: str) -> faiss.Index:
        """Get existing index or create new one for content type."""
        if content_type not in self.indices:
            self.indices[content_type] = self.create_index(content_type)
        
        return self.indices[content_type]
    
    async def add_vector(
        self, 
        content_type: str,
        content_id: int, 
        vector: np.ndarray, 
        metadata: Dict[str, Any]
    ) -> None:
        """Add vector to appropriate index with thread safety."""
        try:
            index = self.get_or_create_index(content_type)
            
            # Normalize vector for cosine similarity
            vector_normalized = vector / np.linalg.norm(vector)
            vector_array = vector_normalized.reshape(1, -1).astype('float32')
            
            # Thread-safe addition to index
            with self.index_locks[content_type]:
                faiss_id = index.ntotal
                index.add(vector_array)
                
                # Store content mapping
                self.content_mappings[content_type][faiss_id] = {
                    'content_id': content_id,
                    'metadata': metadata,
                    'added_at': datetime.now().isoformat()
                }
            
            self.logger.debug(
                f"Added vector for content {content_id} to {content_type} index"
            )
            
        except Exception as e:
            self.logger.error(f"Failed to add vector: {str(e)}")
            raise
    
    async def search_similar(
        self, 
        content_type: str,
        query_vector: np.ndarray,
        top_k: Optional[int] = None
    ) -> List[MatchResult]:
        """Search for similar vectors in the index."""
        try:
            index = self.get_or_create_index(content_type)
            top_k = top_k or min(self.config.max_results, index.ntotal)
            
            if index.ntotal == 0:
                return []
            
            # Normalize query vector
            query_normalized = query_vector / np.linalg.norm(query_vector)
            query_array = query_normalized.reshape(1, -1).astype('float32')
            
            # Perform similarity search
            with self.index_locks[content_type]:
                scores, indices = index.search(query_array, top_k)
            
            # Convert results to MatchResult objects
            matches = []
            content_mapping = self.content_mappings[content_type]
            
            for score, idx in zip(scores[0], indices[0]):
                if idx != -1 and score >= self.config.similarity_threshold:
                    if idx in content_mapping:
                        mapping_data = content_mapping[idx]
                        
                        match = MatchResult(
                            content_id=mapping_data['content_id'],
                            similarity_score=float(score),
                            content_type=content_type,
                            fingerprint_hash=mapping_data.get('metadata', {}).get('fingerprint_hash', ''),
                            metadata=mapping_data.get('metadata', {}),
                            match_timestamp=datetime.now()
                        )
                        matches.append(match)
            
            self.logger.info(
                f"Found {len(matches)} similar matches for {content_type} "
                f"with threshold {self.config.similarity_threshold}"
            )
            
            return matches
            
        except Exception as e:
            self.logger.error(f"Similarity search failed: {str(e)}")
            return []
    
    async def save_index(self, content_type: str, file_path: str) -> None:
        """Save FAISS index to disk."""
        try:
            if content_type in self.indices:
                index = self.indices[content_type]
                content_mapping = self.content_mappings[content_type]
                
                # Save FAISS index
                faiss.write_index(index, file_path)
                
                # Save content mapping separately
                mapping_path = file_path.replace('.faiss', '_mapping.pkl')
                with open(mapping_path, 'wb') as f:
                    pickle.dump(content_mapping, f)
                
                self.logger.info(f"Saved {content_type} index to {file_path}")
            
        except Exception as e:
            self.logger.error(f"Failed to save index: {str(e)}")
            raise
    
    async def load_index(self, content_type: str, file_path: str) -> None:
        """Load FAISS index from disk."""
        try:
            if Path(file_path).exists():
                # Load FAISS index
                index = faiss.read_index(file_path)
                self.indices[content_type] = index
                self.index_locks[content_type] = threading.Lock()
                
                # Load content mapping
                mapping_path = file_path.replace('.faiss', '_mapping.pkl')
                if Path(mapping_path).exists():
                    with open(mapping_path, 'rb') as f:
                        self.content_mappings[content_type] = pickle.load(f)
                else:
                    self.content_mappings[content_type] = {}
                
                self.logger.info(f"Loaded {content_type} index from {file_path}")
            
        except Exception as e:
            self.logger.error(f"Failed to load index: {str(e)}")
            raise
    
    def get_index_stats(self, content_type: str) -> Dict[str, Any]:
        """Get statistics for a specific index."""
        try:
            if content_type in self.indices:
                index = self.indices[content_type]
                mapping = self.content_mappings[content_type]
                
                return {
                    'content_type': content_type,
                    'index_type': self.config.index_type,
                    'total_vectors': index.ntotal,
                    'vector_dimension': self.config.vector_dimension,
                    'mapping_entries': len(mapping),
                    'similarity_threshold': self.config.similarity_threshold
                }
            else:
                return {'content_type': content_type, 'status': 'not_initialized'}
                
        except Exception as e:
            self.logger.error(f"Failed to get index stats: {str(e)}")
            return {'error': str(e)}


class AdvancedVectorMatcher:
    """Advanced vector matching system with multiple optimization strategies."""
    
    def __init__(self, config: Optional[VectorMatchConfig] = None):
        self.config = config or VectorMatchConfig()
        self.index_manager = IndexManager(self.config)
        self.logger = logging.getLogger(__name__)
        
        # Performance tracking
        self.match_stats = {
            'total_searches': 0,
            'total_matches_found': 0,
            'average_search_time': 0.0,
            'cache_hits': 0
        }
        
        # Simple cache for recent queries
        self.query_cache = {}
        self.cache_max_size = 1000
    
    async def add_content_fingerprint(
        self, 
        content_id: int,
        content_type: str,
        vector: np.ndarray,
        fingerprint_hash: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """Add content fingerprint to the matching system."""
        try:
            full_metadata = {
                'fingerprint_hash': fingerprint_hash,
                'content_type': content_type,
                **(metadata or {})
            }
            
            await self.index_manager.add_vector(
                content_type, content_id, vector, full_metadata
            )
            
            self.logger.info(
                f"Added fingerprint for content {content_id} ({content_type})"
            )
            
        except Exception as e:
            self.logger.error(f"Failed to add content fingerprint: {str(e)}")
            raise
    
    async def find_matches(
        self, 
        query_vector: np.ndarray,
        content_type: str,
        top_k: Optional[int] = None,
        use_cache: bool = True
    ) -> List[MatchResult]:
        """Find matching content using vector similarity."""
        import time
        start_time = time.time()
        
        try:
            # Generate cache key
            cache_key = None
            if use_cache:
                cache_key = self._generate_cache_key(query_vector, content_type)
                if cache_key in self.query_cache:
                    self.match_stats['cache_hits'] += 1
                    return self.query_cache[cache_key]
            
            # Perform similarity search
            matches = await self.index_manager.search_similar(
                content_type, query_vector, top_k
            )
            
            # Update cache
            if use_cache and cache_key:
                self._update_cache(cache_key, matches)
            
            # Update statistics
            search_time = time.time() - start_time
            self._update_stats(len(matches), search_time)
            
            self.logger.info(
                f"Found {len(matches)} matches in {search_time:.3f}s"
            )
            
            return matches
            
        except Exception as e:
            self.logger.error(f"Match search failed: {str(e)}")
            return []
    
    async def batch_find_matches(
        self,
        query_vectors: List[np.ndarray],
        content_types: List[str],
        top_k: Optional[int] = None
    ) -> List[List[MatchResult]]:
        """Find matches for multiple queries efficiently."""
        try:
            # Process queries concurrently
            tasks = []
            for vector, content_type in zip(query_vectors, content_types):
                task = self.find_matches(vector, content_type, top_k)
                tasks.append(task)
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Filter out exceptions and return valid results
            valid_results = []
            for result in results:
                if isinstance(result, Exception):
                    self.logger.error(f"Batch query failed: {result}")
                    valid_results.append([])
                else:
                    valid_results.append(result)
            
            return valid_results
            
        except Exception as e:
            self.logger.error(f"Batch matching failed: {str(e)}")
            return [[] for _ in query_vectors]
    
    def _generate_cache_key(self, vector: np.ndarray, content_type: str) -> str:
        """Generate cache key for query vector."""
        # Use hash of vector and content type for cache key
        vector_hash = hash(vector.tobytes())
        return f"{content_type}:{vector_hash}"
    
    def _update_cache(self, key: str, matches: List[MatchResult]) -> None:
        """Update query cache with results."""
        # Simple LRU-style cache management
        if len(self.query_cache) >= self.cache_max_size:
            # Remove oldest entry
            oldest_key = next(iter(self.query_cache))
            del self.query_cache[oldest_key]
        
        self.query_cache[key] = matches
    
    def _update_stats(self, matches_found: int, search_time: float) -> None:
        """Update performance statistics."""
        self.match_stats['total_searches'] += 1
        self.match_stats['total_matches_found'] += matches_found
        
        # Update rolling average search time
        current_avg = self.match_stats['average_search_time']
        total_searches = self.match_stats['total_searches']
        
        new_avg = ((current_avg * (total_searches - 1)) + search_time) / total_searches
        self.match_stats['average_search_time'] = new_avg
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """Get performance statistics for the matching system."""
        return {
            **self.match_stats,
            'cache_size': len(self.query_cache),
            'cache_hit_rate': (
                self.match_stats['cache_hits'] / 
                max(1, self.match_stats['total_searches'])
            ) * 100
        }
    
    def get_all_index_stats(self) -> Dict[str, Any]:
        """Get statistics for all indices."""
        stats = {}
        for content_type in self.index_manager.indices.keys():
            stats[content_type] = self.index_manager.get_index_stats(content_type)
        
        return stats
    
    async def save_all_indices(self, base_path: str) -> None:
        """Save all indices to disk."""
        try:
            base_dir = Path(base_path)
            base_dir.mkdir(parents=True, exist_ok=True)
            
            for content_type in self.index_manager.indices.keys():
                file_path = str(base_dir / f"{content_type}_index.faiss")
                await self.index_manager.save_index(content_type, file_path)
            
            self.logger.info(f"Saved all indices to {base_path}")
            
        except Exception as e:
            self.logger.error(f"Failed to save indices: {str(e)}")
            raise
    
    async def load_all_indices(self, base_path: str) -> None:
        """Load all indices from disk."""
        try:
            base_dir = Path(base_path)
            
            for index_file in base_dir.glob("*_index.faiss"):
                content_type = index_file.stem.replace('_index', '')
                await self.index_manager.load_index(content_type, str(index_file))
            
            self.logger.info(f"Loaded indices from {base_path}")
            
        except Exception as e:
            self.logger.error(f"Failed to load indices: {str(e)}")
            raise


# Export classes for use in other modules
__all__ = [
    'VectorMatchConfig',
    'MatchResult',
    'IndexManager', 
    'AdvancedVectorMatcher'
]
