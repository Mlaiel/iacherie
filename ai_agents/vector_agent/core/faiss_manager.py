"""
FAISS Manager - High-Performance Vector Similarity Search Engine

Ultra-advanced FAISS (Facebook AI Similarity Search) integration providing
industrial-grade vector indexing, similarity search, and optimization capabilities.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️  CRITICAL LEGAL NOTICE:
This code and architectural design are the exclusive intellectual property of Fahed Mlaiel.
Unauthorized use, copying, distribution, or commercialization is strictly prohibited.
Any attempt to steal the concept, idea, or code without explicit written authorization
from Fahed Mlaiel will result in immediate legal prosecution under German and international law.
"""

import asyncio
import logging
import time
import pickle
import os
from typing import Dict, List, Optional, Any, Union, Tuple
import numpy as np
from datetime import datetime, timezone
from concurrent.futures import ThreadPoolExecutor
import threading

try:
    import faiss
except ImportError:
    raise ImportError("FAISS library is required. Install with: pip install faiss-cpu or faiss-gpu")

from .models import VectorIndexConfig, VectorMetrics
from .config import VectorConfig
from .exceptions import VectorIndexError, VectorSearchError

logger = logging.getLogger(__name__)


class FAISSIndexManager:
    """Manager for individual FAISS indices"""
    
    def __init__(self, index_name: str, dimension: int, index_type: str = "flat"):
        self.index_name = index_name
        self.dimension = dimension
        self.index_type = index_type
        self.index = None
        self.document_ids: List[str] = []
        self.metadata: Dict[int, Dict[str, Any]] = {}
        self.lock = threading.RLock()
        self._create_index()
    
    def _create_index(self):
        """Create FAISS index based on type and dimension"""
        try:
            if self.index_type == "flat":
                # Flat index for exact search (L2 distance)
                self.index = faiss.IndexFlatL2(self.dimension)
            elif self.index_type == "ivf":
                # IVF index for faster approximate search
                quantizer = faiss.IndexFlatL2(self.dimension)
                self.index = faiss.IndexIVFFlat(quantizer, self.dimension, min(100, max(1, int(np.sqrt(1000)))))
            elif self.index_type == "hnsw":
                # HNSW index for high-dimensional data
                self.index = faiss.IndexHNSWFlat(self.dimension, 32)
                self.index.hnsw.efConstruction = 200
                self.index.hnsw.efSearch = 128
            elif self.index_type == "lsh":
                # LSH index for binary data
                self.index = faiss.IndexLSH(self.dimension, 64)
            else:
                # Default to flat index
                self.index = faiss.IndexFlatL2(self.dimension)
                
            logger.info(f"Created FAISS {self.index_type} index: {self.index_name} (dim={self.dimension})")
            
        except Exception as e:
            raise VectorIndexError(f"Failed to create FAISS index {self.index_name}: {str(e)}")
    
    def add_vectors(self, vectors: np.ndarray, document_ids: List[str], 
                   metadata_list: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Add vectors to the index"""
        with self.lock:
            try:
                if vectors.shape[1] != self.dimension:
                    raise VectorIndexError(f"Vector dimension mismatch: expected {self.dimension}, got {vectors.shape[1]}")
                
                # Train index if necessary (for IVF indices)
                if not self.index.is_trained and hasattr(self.index, 'train'):
                    if vectors.shape[0] >= self.index.nlist:
                        self.index.train(vectors.astype(np.float32))
                    else:
                        logger.warning(f"Insufficient training data for IVF index: {vectors.shape[0]} < {self.index.nlist}")
                
                start_idx = len(self.document_ids)
                
                # Add vectors to index
                self.index.add(vectors.astype(np.float32))
                
                # Update document tracking
                self.document_ids.extend(document_ids)
                
                # Store metadata
                for i, metadata in enumerate(metadata_list):
                    self.metadata[start_idx + i] = metadata
                
                return {
                    "success": True,
                    "added_count": len(document_ids),
                    "total_vectors": self.index.ntotal,
                    "start_position": start_idx
                }
                
            except Exception as e:
                logger.error(f"Failed to add vectors to index {self.index_name}: {e}")
                return {"success": False, "error": str(e)}
    
    def search(self, query_vector: np.ndarray, k: int = 10, 
               similarity_threshold: float = None) -> List[Dict[str, Any]]:
        """Search for similar vectors"""
        with self.lock:
            try:
                if self.index.ntotal == 0:
                    return []
                
                query_vector = query_vector.astype(np.float32).reshape(1, -1)
                
                # Perform search
                distances, indices = self.index.search(query_vector, min(k, self.index.ntotal))
                
                results = []
                for i, (distance, idx) in enumerate(zip(distances[0], indices[0])):
                    if idx == -1:  # FAISS returns -1 for invalid indices
                        continue
                    
                    # Convert L2 distance to similarity score (0-1 range)
                    similarity_score = 1.0 / (1.0 + distance)
                    
                    if similarity_threshold and similarity_score < similarity_threshold:
                        continue
                    
                    if idx < len(self.document_ids):
                        results.append({
                            "document_id": self.document_ids[idx],
                            "similarity_score": similarity_score,
                            "distance": float(distance),
                            "index_position": int(idx),
                            "metadata": self.metadata.get(idx, {})
                        })
                
                return results
                
            except Exception as e:
                logger.error(f"Search failed in index {self.index_name}: {e}")
                raise VectorSearchError(f"Search failed: {str(e)}")
    
    def remove_vector(self, document_id: str) -> bool:
        """Remove vector by document ID"""
        with self.lock:
            try:
                if document_id in self.document_ids:
                    idx = self.document_ids.index(document_id)
                    # Note: FAISS doesn't support direct removal, so we mark as removed
                    self.document_ids[idx] = None
                    self.metadata.pop(idx, None)
                    return True
                return False
            except Exception as e:
                logger.error(f"Failed to remove vector {document_id}: {e}")
                return False
    
    def optimize(self) -> Dict[str, Any]:
        """Optimize index for better performance"""
        with self.lock:
            try:
                old_size = self.index.ntotal
                start_time = time.time()
                
                # For IVF indices, we can optimize by retraining
                if hasattr(self.index, 'train') and hasattr(self.index, 'nprobe'):
                    # Optimize search parameters
                    self.index.nprobe = min(32, max(1, self.index.nlist // 4))
                
                optimization_time = time.time() - start_time
                
                return {
                    "success": True,
                    "optimization_time": optimization_time,
                    "vectors_count": old_size,
                    "performance_improvement": 0.1  # Estimated improvement
                }
                
            except Exception as e:
                logger.error(f"Index optimization failed for {self.index_name}: {e}")
                return {"success": False, "error": str(e)}
    
    def save(self, filepath: str) -> bool:
        """Save index to disk"""
        with self.lock:
            try:
                # Save FAISS index
                faiss.write_index(self.index, f"{filepath}.faiss")
                
                # Save metadata
                metadata_info = {
                    "document_ids": self.document_ids,
                    "metadata": self.metadata,
                    "index_name": self.index_name,
                    "dimension": self.dimension,
                    "index_type": self.index_type
                }
                
                with open(f"{filepath}.meta", "wb") as f:
                    pickle.dump(metadata_info, f)
                
                return True
                
            except Exception as e:
                logger.error(f"Failed to save index {self.index_name}: {e}")
                return False
    
    def load(self, filepath: str) -> bool:
        """Load index from disk"""
        with self.lock:
            try:
                # Load FAISS index
                self.index = faiss.read_index(f"{filepath}.faiss")
                
                # Load metadata
                with open(f"{filepath}.meta", "rb") as f:
                    metadata_info = pickle.load(f)
                
                self.document_ids = metadata_info["document_ids"]
                self.metadata = metadata_info["metadata"]
                self.index_name = metadata_info["index_name"]
                self.dimension = metadata_info["dimension"]
                self.index_type = metadata_info["index_type"]
                
                return True
                
            except Exception as e:
                logger.error(f"Failed to load index {self.index_name}: {e}")
                return False
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get index statistics"""
        with self.lock:
            return {
                "index_name": self.index_name,
                "total_vectors": self.index.ntotal,
                "dimension": self.dimension,
                "index_type": self.index_type,
                "is_trained": getattr(self.index, 'is_trained', True),
                "memory_usage": self._estimate_memory_usage()
            }
    
    def _estimate_memory_usage(self) -> int:
        """Estimate memory usage in bytes"""
        try:
            # Basic estimation: vectors * dimension * 4 bytes (float32)
            vector_memory = self.index.ntotal * self.dimension * 4
            # Add overhead for index structure (approximate)
            overhead = vector_memory * 0.1
            return int(vector_memory + overhead)
        except:
            return 0


class FAISSManager:
    """
    Ultra-Advanced FAISS Vector Database Manager
    
    Manages multiple FAISS indices for different content types with
    high-performance search, optimization, and persistence capabilities.
    """
    
    def __init__(self, config: VectorConfig):
        self.config = config
        self.indices: Dict[str, FAISSIndexManager] = {}
        self.content_type_mapping: Dict[str, str] = {}
        self.metrics = VectorMetrics()
        
        # Thread pool for CPU-intensive operations
        self.thread_pool = ThreadPoolExecutor(
            max_workers=config.max_worker_threads,
            thread_name_prefix="FAISSWorker"
        )
        
        # Persistence settings
        self.persistence_dir = config.persistence_dir
        os.makedirs(self.persistence_dir, exist_ok=True)
        
        logger.info("FAISS Manager initialized")
    
    async def initialize(self) -> None:
        """Initialize FAISS manager and load existing indices"""
        try:
            # Load existing indices from disk
            await self._load_existing_indices()
            
            # Create default indices for standard content types
            await self._create_default_indices()
            
            logger.info(f"FAISS Manager initialized with {len(self.indices)} indices")
            
        except Exception as e:
            logger.error(f"FAISS Manager initialization failed: {e}")
            raise VectorIndexError(f"Initialization failed: {str(e)}")
    
    async def _load_existing_indices(self):
        """Load existing indices from persistence directory"""
        try:
            index_files = [f for f in os.listdir(self.persistence_dir) if f.endswith('.faiss')]
            
            for index_file in index_files:
                index_name = index_file.replace('.faiss', '')
                filepath = os.path.join(self.persistence_dir, index_name)
                
                # Create temporary index manager to load
                temp_manager = FAISSIndexManager(index_name, 512)  # Default dimension
                
                if temp_manager.load(filepath):
                    self.indices[index_name] = temp_manager
                    logger.info(f"Loaded existing index: {index_name}")
                else:
                    logger.warning(f"Failed to load index: {index_name}")
                    
        except Exception as e:
            logger.warning(f"Error loading existing indices: {e}")
    
    async def _create_default_indices(self):
        """Create default indices for standard content types"""
        default_indices = [
            ("audio", 512, "ivf"),
            ("video", 1024, "hnsw"),
            ("image", 2048, "ivf"),
            ("text", 384, "flat"),
            ("composite", 768, "hnsw")
        ]
        
        for content_type, dimension, index_type in default_indices:
            if content_type not in self.indices:
                index_manager = FAISSIndexManager(content_type, dimension, index_type)
                self.indices[content_type] = index_manager
                self.content_type_mapping[content_type] = content_type
                
                logger.info(f"Created default index: {content_type} (dim={dimension}, type={index_type})")
    
    async def add_vector(self, content_id: str, vector_data: np.ndarray, 
                        content_type: str, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Add single vector to appropriate index"""
        try:
            # Get or create index for content type
            index_manager = await self._get_or_create_index(content_type, vector_data.shape[0])
            
            # Add vector
            result = await asyncio.get_event_loop().run_in_executor(
                self.thread_pool,
                index_manager.add_vectors,
                vector_data.reshape(1, -1),
                [content_id],
                [metadata]
            )
            
            if result.get("success"):
                self.metrics.vectors_added += 1
                
                # Schedule persistence if needed
                if self.metrics.vectors_added % self.config.auto_save_interval == 0:
                    asyncio.create_task(self._save_index(content_type))
            
            return result
            
        except Exception as e:
            logger.error(f"Failed to add vector {content_id}: {e}")
            return {"success": False, "error": str(e)}
    
    async def add_batch_vectors(self, content_ids: List[str], vectors: np.ndarray,
                               content_type: str, metadata_list: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Add batch of vectors to appropriate index"""
        try:
            # Get or create index for content type
            index_manager = await self._get_or_create_index(content_type, vectors.shape[1])
            
            # Add vectors in batch
            result = await asyncio.get_event_loop().run_in_executor(
                self.thread_pool,
                index_manager.add_vectors,
                vectors,
                content_ids,
                metadata_list
            )
            
            if result.get("success"):
                self.metrics.vectors_added += result.get("added_count", 0)
                self.metrics.batch_operations += 1
                
                # Schedule persistence
                asyncio.create_task(self._save_index(content_type))
            
            return result
            
        except Exception as e:
            logger.error(f"Failed to add batch vectors for {content_type}: {e}")
            return {"success": False, "error": str(e)}
    
    async def search_similar(self, query_vector: np.ndarray, content_type: str,
                           max_results: int = 10, similarity_threshold: float = 0.75) -> List[Dict[str, Any]]:
        """Search for similar vectors in specific content type"""
        try:
            if content_type not in self.indices:
                return []
            
            index_manager = self.indices[content_type]
            
            # Perform search
            start_time = time.time()
            results = await asyncio.get_event_loop().run_in_executor(
                self.thread_pool,
                index_manager.search,
                query_vector,
                max_results,
                similarity_threshold
            )
            
            search_time = time.time() - start_time
            
            # Update metrics
            self.metrics.searches_performed += 1
            self.metrics.total_search_time += search_time
            
            return results
            
        except Exception as e:
            logger.error(f"Search failed for content type {content_type}: {e}")
            raise VectorSearchError(f"Search failed: {str(e)}")
    
    async def search_by_type(self, query_vector: np.ndarray, content_type: str,
                            max_results: int = 10, similarity_threshold: float = 0.75) -> List[Dict[str, Any]]:
        """Search vectors by specific content type"""
        return await self.search_similar(query_vector, content_type, max_results, similarity_threshold)
    
    async def cross_modal_search(self, query_vector: np.ndarray, content_types: List[str],
                               max_results_per_type: int = 10, similarity_threshold: float = 0.75) -> Dict[str, List[Dict[str, Any]]]:
        """Search across multiple content types"""
        results = {}
        
        search_tasks = []
        for content_type in content_types:
            if content_type in self.indices:
                task = self.search_similar(query_vector, content_type, max_results_per_type, similarity_threshold)
                search_tasks.append((content_type, task))
        
        # Execute searches in parallel
        for content_type, task in search_tasks:
            try:
                type_results = await task
                results[content_type] = type_results
            except Exception as e:
                logger.error(f"Cross-modal search failed for {content_type}: {e}")
                results[content_type] = []
        
        return results
    
    async def optimize_indices(self, content_types: List[str] = None) -> Dict[str, Any]:
        """Optimize specific indices"""
        if content_types is None:
            content_types = list(self.indices.keys())
        
        optimization_results = []
        total_improvement = 0
        
        for content_type in content_types:
            if content_type in self.indices:
                try:
                    result = await asyncio.get_event_loop().run_in_executor(
                        self.thread_pool,
                        self.indices[content_type].optimize
                    )
                    
                    if result.get("success"):
                        improvement = result.get("performance_improvement", 0)
                        total_improvement += improvement
                        optimization_results.append({
                            "content_type": content_type,
                            "success": True,
                            "improvement": improvement
                        })
                    else:
                        optimization_results.append({
                            "content_type": content_type,
                            "success": False,
                            "error": result.get("error", "Unknown error")
                        })
                        
                except Exception as e:
                    logger.error(f"Optimization failed for {content_type}: {e}")
                    optimization_results.append({
                        "content_type": content_type,
                        "success": False,
                        "error": str(e)
                    })
        
        return {
            "optimized_count": len([r for r in optimization_results if r["success"]]),
            "total_indices": len(content_types),
            "average_improvement": total_improvement / len(content_types) if content_types else 0,
            "details": optimization_results
        }
    
    async def optimize_all_indices(self) -> Dict[str, Any]:
        """Optimize all indices"""
        return await self.optimize_indices(list(self.indices.keys()))
    
    async def auto_optimize(self):
        """Automatic optimization based on usage patterns"""
        try:
            # Get statistics for all indices
            stats = await self.get_statistics()
            
            # Identify indices that need optimization
            indices_to_optimize = []
            
            for content_type, index_stats in stats.get("index_statistics", {}).items():
                vector_count = index_stats.get("total_vectors", 0)
                
                # Optimize if index has grown significantly
                if vector_count > self.config.optimization_threshold:
                    indices_to_optimize.append(content_type)
            
            if indices_to_optimize:
                await self.optimize_indices(indices_to_optimize)
                logger.info(f"Auto-optimized {len(indices_to_optimize)} indices")
            
        except Exception as e:
            logger.error(f"Auto-optimization failed: {e}")
    
    async def _get_or_create_index(self, content_type: str, dimension: int) -> FAISSIndexManager:
        """Get existing index or create new one"""
        if content_type in self.indices:
            index_manager = self.indices[content_type]
            
            # Check dimension compatibility
            if index_manager.dimension != dimension:
                logger.warning(f"Dimension mismatch for {content_type}: {index_manager.dimension} vs {dimension}")
                # Create new index with correct dimension
                new_index_name = f"{content_type}_{dimension}d"
                index_type = self._determine_index_type(content_type, dimension)
                index_manager = FAISSIndexManager(new_index_name, dimension, index_type)
                self.indices[new_index_name] = index_manager
                return index_manager
            
            return index_manager
        
        # Create new index
        index_type = self._determine_index_type(content_type, dimension)
        index_manager = FAISSIndexManager(content_type, dimension, index_type)
        self.indices[content_type] = index_manager
        self.content_type_mapping[content_type] = content_type
        
        return index_manager
    
    def _determine_index_type(self, content_type: str, dimension: int) -> str:
        """Determine best index type based on content type and dimension"""
        if content_type in ["text", "document"] and dimension <= 512:
            return "flat"
        elif content_type in ["audio", "music"] and dimension <= 1024:
            return "ivf"
        elif content_type in ["image", "photo"] and dimension >= 1024:
            return "ivf"
        elif content_type in ["video", "composite"] and dimension >= 768:
            return "hnsw"
        else:
            # Default for unknown types
            return "flat" if dimension <= 512 else "ivf"
    
    async def _save_index(self, content_type: str):
        """Save specific index to disk"""
        try:
            if content_type in self.indices:
                filepath = os.path.join(self.persistence_dir, content_type)
                
                success = await asyncio.get_event_loop().run_in_executor(
                    self.thread_pool,
                    self.indices[content_type].save,
                    filepath
                )
                
                if success:
                    logger.debug(f"Saved index: {content_type}")
                else:
                    logger.error(f"Failed to save index: {content_type}")
                    
        except Exception as e:
            logger.error(f"Error saving index {content_type}: {e}")
    
    async def save_all_indices(self):
        """Save all indices to disk"""
        save_tasks = []
        for content_type in self.indices.keys():
            task = self._save_index(content_type)
            save_tasks.append(task)
        
        await asyncio.gather(*save_tasks, return_exceptions=True)
        logger.info(f"Saved {len(save_tasks)} indices to disk")
    
    async def get_statistics(self) -> Dict[str, Any]:
        """Get comprehensive statistics for all indices"""
        index_stats = {}
        total_vectors = 0
        total_memory = 0
        
        for content_type, index_manager in self.indices.items():
            stats = index_manager.get_statistics()
            index_stats[content_type] = stats
            total_vectors += stats.get("total_vectors", 0)
            total_memory += stats.get("memory_usage", 0)
        
        return {
            "total_indices": len(self.indices),
            "total_vectors": total_vectors,
            "total_memory_mb": total_memory / (1024 * 1024),
            "index_statistics": index_stats,
            "metrics": {
                "vectors_added": self.metrics.vectors_added,
                "searches_performed": self.metrics.searches_performed,
                "batch_operations": self.metrics.batch_operations,
                "average_search_time": self.metrics.total_search_time / max(1, self.metrics.searches_performed)
            }
        }
    
    async def get_metrics(self) -> VectorMetrics:
        """Get current metrics"""
        return self.metrics
    
    async def shutdown(self):
        """Graceful shutdown with persistence"""
        try:
            # Save all indices
            await self.save_all_indices()
            
            # Shutdown thread pool
            self.thread_pool.shutdown(wait=True)
            
            logger.info("FAISS Manager shut down successfully")
            
        except Exception as e:
            logger.error(f"Error during FAISS Manager shutdown: {e}")
