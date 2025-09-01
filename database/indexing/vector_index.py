"""Vector Index Manager for IA-Influencer-Agent Platform

Ultra-advanced vector indexing system for high-performance similarity search
across multi-modal content embeddings with enterprise-grade optimization.

🚀 Enterprise Team Project Specialties:
✅ Lead Dev + Architecte Développeur IA
✅ Développeur Backend Senior (Python/FastAPI/Django)  
✅ Ingénieur Machine Learning (TensorFlow/PyTorch/Hugging Face)
✅ DBA & Data Engineer (PostgreSQL/Redis/MongoDB)
✅ Spécialiste Sécurité Backend
✅ Architecte Microservices
✅ Développeur Audio
✅ DevOps Engineer
✅ IA Prompt Engineer

Created by: Fahed Mlaiel (mlaiel@live.de)
(c) 2025 Fahed Mlaiel. All rights reserved.

⚠️ STRICT COPYRIGHT WARNING ⚠️
This software is proprietary and confidential. 
Unauthorized use, modification, or distribution by any individual or entity 
without explicit written permission from Fahed Mlaiel (mlaiel@live.de) is strictly prohibited.
Violators will be prosecuted to the full extent of the law.
"""

import asyncio
import logging
import numpy as np
import json
from typing import Dict, List, Optional, Any, Tuple, Union
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor
import pickle
from pathlib import Path

# Vector database imports
try:
    from pgvector.asyncpg import register_vector
    import asyncpg
    PGVECTOR_AVAILABLE = True
except ImportError:
    PGVECTOR_AVAILABLE = False
    logger.warning("pgvector not available, falling back to FAISS only")

from ..connections.postgresql_manager import PostgreSQLManager
from ..connections.redis_manager import RedisManager
from ..monitoring.performance_tracker import PerformanceTracker
from ..security.vector_security import VectorSecurityManager

logger = logging.getLogger(__name__)

class VectorIndexType:
    """Vector index types for different similarity algorithms"""

    COSINE = "cosine"
    EUCLIDEAN = "euclidean"
    DOT_PRODUCT = "dot_product"
    MANHATTAN = "manhattan"
    HAMMING = "hamming"

class VectorStorageBackend:
    """Vector storage backend options"""

    POSTGRESQL = "postgresql"
    REDIS = "redis"
    MEMORY = "memory"
    HYBRID = "hybrid"

class VectorIndexManager:
    """
    Enterprise-grade vector index manager for IA-Influencer platform
    
    Provides high-performance vector similarity search with multiple backends:
    - PostgreSQL with pgvector extension
    - Redis with vector similarity
    - In-memory for ultra-fast operations
    - Hybrid approach for optimal performance
    
    Supports multi-modal content embeddings:
    - Audio spectral and semantic embeddings
    - Video visual and temporal embeddings
    - Image feature and semantic embeddings
    - Text semantic and syntactic embeddings
    - Cross-modal composite embeddings
    """
    
    def __init__(self):
        """
Initialize vector index manager"""
        self.db_manager = PostgreSQLManager()
        self.redis_manager = RedisManager()
        self.performance_tracker = PerformanceTracker()
        self.security_manager = VectorSecurityManager()
        self.thread_executor = ThreadPoolExecutor(max_workers=6)
        
        # Vector indexes by backend
        self.postgresql_indexes = {}
        self.redis_indexes = {}
        self.memory_indexes = {}
        
        # Index metadata and configuration
        self.index_metadata = {}
        self.vector_mappings = {}  # Vector ID to content ID mapping
        
        # Performance settings
        self.batch_size = 500
        self.cache_size = 10000
        self.similarity_threshold = 0.8
        self.use_approximate_search = True
        
        # Storage paths for persistence
        self.storage_path = Path("/data/vector_indexes")
        self.storage_path.mkdir(parents=True, exist_ok=True)
        
        logger.info("VectorIndexManager initialized")
    
    async def initialize(self) -> bool:
        """Initialize vector index manager"""
        try:
            # Initialize database connections
            if not await self.db_manager.initialize():
                raise Exception("Failed to initialize PostgreSQL manager")
                
            if not await self.redis_manager.initialize():
                raise Exception("Failed to initialize Redis manager")
            
            # Initialize tracking and security
            await self.performance_tracker.initialize()
            await self.security_manager.initialize()
            
            # Setup PostgreSQL vector support
            if PGVECTOR_AVAILABLE:
                await self._setup_postgresql_vector_support()
            
            # Load existing indexes
            await self._load_existing_indexes()
            
            # Setup optimization scheduling
            await self._setup_optimization_schedule()
            
            logger.info("VectorIndexManager initialization completed")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize VectorIndexManager: {str(e)}")
            return False
    
    async def _setup_postgresql_vector_support(self):
        """Setup PostgreSQL with pgvector extension"""
        try:
            conn = await self.db_manager.get_connection()
            
            # Enable pgvector extension
            await conn.execute("CREATE EXTENSION IF NOT EXISTS vector;")
            
            # Register vector type for asyncpg
            await register_vector(conn)
            
            # Create vector index metadata table
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS vector_index_metadata (
                    index_id SERIAL PRIMARY KEY,
                    index_name VARCHAR(255) UNIQUE NOT NULL,
                    table_name VARCHAR(255) NOT NULL,
                    column_name VARCHAR(255) NOT NULL,
                    dimension INTEGER NOT NULL,
                    index_type VARCHAR(50) NOT NULL,
                    distance_function VARCHAR(50) NOT NULL,
                    storage_backend VARCHAR(50) NOT NULL,
                    config JSONB DEFAULT '{}',
                    performance_stats JSONB DEFAULT '{}',
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
                );
            """)
            
            # Create vector content table template
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS vector_content_template (
                    vector_id SERIAL PRIMARY KEY,
                    content_id VARCHAR(255) NOT NULL,
                    user_id VARCHAR(255) NOT NULL,
                    content_type VARCHAR(50) NOT NULL,
                    embedding_type VARCHAR(50) NOT NULL,
                    vector_data vector,
                    metadata JSONB DEFAULT '{}',
                    quality_score FLOAT DEFAULT 0.0,
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
                );
            """)
            
            logger.info("PostgreSQL vector support setup completed")
            
        except Exception as e:
            logger.error(f"Failed to setup PostgreSQL vector support: {str(e)}")
            raise
        finally:
            await self.db_manager.return_connection(conn)
    
    async def create_index(self, index_name: str, config: Dict[str, Any]) -> bool:
        """Create a new vector index with specified configuration"""
        try:
            dimension = config.get('dimension', 512)
            index_type = config.get('index_type', VectorIndexType.COSINE)
            storage_backend = config.get('storage_backend', VectorStorageBackend.HYBRID)
            
            # Validate security permissions
            if not await self.security_manager.validate_index_creation(index_name, config):
                raise Exception("Index creation not authorized")
            
            start_time = datetime.now()
            
            # Create index based on storage backend
            if storage_backend == VectorStorageBackend.POSTGRESQL:
                success = await self._create_postgresql_index(index_name, dimension, index_type, config)
            elif storage_backend == VectorStorageBackend.REDIS:
                success = await self._create_redis_index(index_name, dimension, index_type, config)
            elif storage_backend == VectorStorageBackend.MEMORY:
                success = await self._create_memory_index(index_name, dimension, index_type, config)
            elif storage_backend == VectorStorageBackend.HYBRID:
                success = await self._create_hybrid_index(index_name, dimension, index_type, config)
            else:
                raise ValueError(f"Unsupported storage backend: {storage_backend}")
            
            if not success:
                return False
            
            creation_time = (datetime.now() - start_time).total_seconds()
            
            # Store index metadata
            self.index_metadata[index_name] = {
                'dimension': dimension,
                'index_type': index_type,
                'storage_backend': storage_backend,
                'config': config,
                'created_at': datetime.now(),
                'total_vectors': 0,
                'last_updated': datetime.now(),
                'performance_stats': {
                    'creation_time': creation_time,
                    'average_search_time': 0,
                    'cache_hit_rate': 0
                }
            }
            
            self.vector_mappings[index_name] = {}
            
            # Save metadata
            await self._save_index_metadata(index_name)
            
            # Log performance
            await self.performance_tracker.log_index_operation(
                index_name, 'create', creation_time, config
            )
            
            logger.info(f"Vector index {index_name} created successfully in {creation_time:.2f}s")
            return True
            
        except Exception as e:
            logger.error(f"Failed to create vector index {index_name}: {str(e)}")
            return False
    
    async def _create_postgresql_index(self, index_name: str, dimension: int, 
                                     index_type: str, config: Dict[str, Any]) -> bool:
        """Create PostgreSQL-based vector index"""
        try:
            if not PGVECTOR_AVAILABLE:
                raise Exception("pgvector not available")
            
            conn = await self.db_manager.get_connection()
            
            # Create table for this index
            table_name = f"vector_index_{index_name}"
            
            await conn.execute(f"""
                CREATE TABLE {table_name} (
                    vector_id SERIAL PRIMARY KEY,
                    content_id VARCHAR(255) NOT NULL,
                    user_id VARCHAR(255) NOT NULL,
                    content_type VARCHAR(50) NOT NULL,
                    embedding_type VARCHAR(50) NOT NULL,
                    vector_data vector({dimension}),
                    metadata JSONB DEFAULT '{{}}',
                    quality_score FLOAT DEFAULT 0.0,
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
                );
            """)
            
            # Create appropriate vector index
            distance_func = self._get_postgresql_distance_function(index_type)
            
            await conn.execute(f"""
                CREATE INDEX {index_name}_vector_idx ON {table_name} 
                USING ivfflat (vector_data {distance_func}) 
                WITH (lists = {config.get('lists', 100)});
            """)
            
            # Create additional indexes for filtering
            await conn.execute(f"""
                CREATE INDEX {index_name}_content_idx ON {table_name} (content_id);
                CREATE INDEX {index_name}_user_idx ON {table_name} (user_id);
                CREATE INDEX {index_name}_type_idx ON {table_name} (content_type, embedding_type);
                CREATE INDEX {index_name}_quality_idx ON {table_name} (quality_score DESC);
                CREATE INDEX {index_name}_created_idx ON {table_name} (created_at DESC);
            """)
            
            self.postgresql_indexes[index_name] = {
                'table_name': table_name,
                'dimension': dimension,
                'index_type': index_type,
                'distance_function': distance_func
            }
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to create PostgreSQL vector index: {str(e)}")
            return False
        finally:
            await self.db_manager.return_connection(conn)
    
    def _get_postgresql_distance_function(self, index_type: str) -> str:
        """Get PostgreSQL distance function for index type"""
        if index_type == VectorIndexType.COSINE:
            return "vector_cosine_ops"
        elif index_type == VectorIndexType.EUCLIDEAN:
            return "vector_l2_ops"
        elif index_type == VectorIndexType.DOT_PRODUCT:
            return "vector_ip_ops"
        else:
            return "vector_l2_ops"  # Default to L2
    
    async def _create_redis_index(self, index_name: str, dimension: int,
                                index_type: str, config: Dict[str, Any]) -> bool:
        """Create Redis-based vector index"""
        try:
            redis_conn = await self.redis_manager.get_connection()
            
            # Redis vector index configuration
            index_config = {
                'dimension': dimension,
                'distance_metric': self._get_redis_distance_metric(index_type),
                'vector_type': 'FLOAT32'
            }
            
            # Store index configuration in Redis
            config_key = f"vector_index_config:{index_name}"
            await redis_conn.hset(config_key, mapping=index_config)
            
            self.redis_indexes[index_name] = {
                'dimension': dimension,
                'index_type': index_type,
                'config': index_config
            }
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to create Redis vector index: {str(e)}")
            return False
    
    def _get_redis_distance_metric(self, index_type: str) -> str:
        """Get Redis distance metric for index type"""
        if index_type == VectorIndexType.COSINE:
            return "COSINE"
        elif index_type == VectorIndexType.EUCLIDEAN:
            return "L2"
        elif index_type == VectorIndexType.DOT_PRODUCT:
            return "IP"
        else:
            return "L2"  # Default to L2
    
    async def _create_memory_index(self, index_name: str, dimension: int,
                                 index_type: str, config: Dict[str, Any]) -> bool:
        """Create in-memory vector index"""
        try:
            self.memory_indexes[index_name] = {
                'vectors': np.empty((0, dimension), dtype=np.float32),
                'content_ids': [],
                'dimension': dimension,
                'index_type': index_type,
                'total_vectors': 0
            }
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to create memory vector index: {str(e)}")
            return False
    
    async def _create_hybrid_index(self, index_name: str, dimension: int,
                                 index_type: str, config: Dict[str, Any]) -> bool:
        """Create hybrid vector index (PostgreSQL + Redis + Memory)"""
        try:
            # Create all three backends
            pg_success = await self._create_postgresql_index(index_name, dimension, index_type, config)
            redis_success = await self._create_redis_index(index_name, dimension, index_type, config)
            mem_success = await self._create_memory_index(index_name, dimension, index_type, config)
            
            return pg_success and redis_success and mem_success
            
        except Exception as e:
            logger.error(f"Failed to create hybrid vector index: {str(e)}")
            return False
    
    async def add_vectors(self, index_name: str, vectors: np.ndarray,
                         content_ids: List[str], metadata: Optional[List[Dict]] = None) -> bool:
        """Add vectors to the index"""
        try:
            if index_name not in self.index_metadata:
                raise ValueError(f"Index {index_name} not found")
            
            if len(vectors) != len(content_ids):
                raise ValueError("Number of vectors must match number of content IDs")
            
            index_meta = self.index_metadata[index_name]
            storage_backend = index_meta['storage_backend']
            
            start_time = datetime.now()
            
            # Add vectors based on storage backend
            if storage_backend == VectorStorageBackend.POSTGRESQL:
                success = await self._add_vectors_postgresql(index_name, vectors, content_ids, metadata)
            elif storage_backend == VectorStorageBackend.REDIS:
                success = await self._add_vectors_redis(index_name, vectors, content_ids, metadata)
            elif storage_backend == VectorStorageBackend.MEMORY:
                success = await self._add_vectors_memory(index_name, vectors, content_ids, metadata)
            elif storage_backend == VectorStorageBackend.HYBRID:
                success = await self._add_vectors_hybrid(index_name, vectors, content_ids, metadata)
            else:
                raise ValueError(f"Unsupported storage backend: {storage_backend}")
            
            if not success:
                return False
            
            add_time = (datetime.now() - start_time).total_seconds()
            
            # Update metadata
            index_meta['total_vectors'] += len(vectors)
            index_meta['last_updated'] = datetime.now()
            
            # Update mappings
            for i, content_id in enumerate(content_ids):
                self.vector_mappings[index_name][content_id] = {
                    'vector_id': index_meta['total_vectors'] - len(vectors) + i,
                    'added_at': datetime.now()
                }
            
            # Save metadata
            await self._save_index_metadata(index_name)
            
            # Log performance
            await self.performance_tracker.log_index_operation(
                index_name, 'add_vectors', add_time,
                {'vector_count': len(vectors), 'total_vectors': index_meta['total_vectors']}
            )
            
            logger.info(f"Added {len(vectors)} vectors to index {index_name} in {add_time:.2f}s")
            return True
            
        except Exception as e:
            logger.error(f"Failed to add vectors to index {index_name}: {str(e)}")
            return False
    
    async def _add_vectors_postgresql(self, index_name: str, vectors: np.ndarray,
                                    content_ids: List[str], metadata: Optional[List[Dict]]) -> bool:
        """Add vectors to PostgreSQL backend"""
        try:
            if index_name not in self.postgresql_indexes:
                raise ValueError(f"PostgreSQL index {index_name} not found")
            
            table_name = self.postgresql_indexes[index_name]['table_name']
            conn = await self.db_manager.get_connection()
            
            # Prepare batch insert
            insert_data = []
            for i, (content_id, vector) in enumerate(zip(content_ids, vectors)):
                vector_meta = metadata[i] if metadata else {}
                insert_data.append((
                    content_id,
                    vector_meta.get('user_id', ''),
                    vector_meta.get('content_type', ''),
                    vector_meta.get('embedding_type', ''),
                    vector.tolist(),  # Convert to list for pgvector
                    json.dumps(vector_meta),
                    vector_meta.get('quality_score', 0.0)
                ))
            
            # Batch insert
            await conn.executemany(f"""
                INSERT INTO {table_name} 
                (content_id, user_id, content_type, embedding_type, vector_data, metadata, quality_score)
                VALUES ($1, $2, $3, $4, $5, $6, $7)
            """, insert_data)
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to add vectors to PostgreSQL: {str(e)}")
            return False
        finally:
            await self.db_manager.return_connection(conn)
    
    async def _add_vectors_redis(self, index_name: str, vectors: np.ndarray,
                               content_ids: List[str], metadata: Optional[List[Dict]]) -> bool:
        """Add vectors to Redis backend"""
        try:
            redis_conn = await self.redis_manager.get_connection()
            
            # Store vectors in Redis
            pipe = redis_conn.pipeline()
            for i, (content_id, vector) in enumerate(zip(content_ids, vectors)):
                vector_key = f"vector:{index_name}:{content_id}"
                vector_meta = metadata[i] if metadata else {}
                
                # Store vector and metadata
                pipe.hset(vector_key, mapping={
                    'vector': vector.tobytes(),
                    'metadata': json.dumps(vector_meta),
                    'created_at': datetime.now().isoformat()
                })
                
                # Add to index set
                pipe.sadd(f"vector_index_members:{index_name}", content_id)
            
            await pipe.execute()
            return True
            
        except Exception as e:
            logger.error(f"Failed to add vectors to Redis: {str(e)}")
            return False
    
    async def _add_vectors_memory(self, index_name: str, vectors: np.ndarray,
                                content_ids: List[str], metadata: Optional[List[Dict]]) -> bool:
        """Add vectors to memory backend"""
        try:
            mem_index = self.memory_indexes[index_name]
            
            # Append vectors
            if mem_index['total_vectors'] == 0:
                mem_index['vectors'] = vectors.astype(np.float32)
            else:
                mem_index['vectors'] = np.vstack([mem_index['vectors'], vectors.astype(np.float32)])
            
            # Append content IDs
            mem_index['content_ids'].extend(content_ids)
            mem_index['total_vectors'] += len(vectors)
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to add vectors to memory: {str(e)}")
            return False
    
    async def _add_vectors_hybrid(self, index_name: str, vectors: np.ndarray,
                                content_ids: List[str], metadata: Optional[List[Dict]]) -> bool:
        """Add vectors to all hybrid backends"""
        try:
            # Add to all backends
            pg_success = await self._add_vectors_postgresql(index_name, vectors, content_ids, metadata)
            redis_success = await self._add_vectors_redis(index_name, vectors, content_ids, metadata)
            mem_success = await self._add_vectors_memory(index_name, vectors, content_ids, metadata)
            
            return pg_success and redis_success and mem_success
            
        except Exception as e:
            logger.error(f"Failed to add vectors to hybrid index: {str(e)}")
            return False
    
    async def search_similar(self, index_name: str, query_vector: np.ndarray,
                           k: int = 10, similarity_threshold: Optional[float] = None,
                           filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Search for similar vectors"""
        try:
            if index_name not in self.index_metadata:
                raise ValueError(f"Index {index_name} not found")
            
            index_meta = self.index_metadata[index_name]
            storage_backend = index_meta['storage_backend']
            threshold = similarity_threshold or self.similarity_threshold
            
            start_time = datetime.now()
            
            # Search based on storage backend
            if storage_backend == VectorStorageBackend.POSTGRESQL:
                results = await self._search_postgresql(index_name, query_vector, k, threshold, filters)
            elif storage_backend == VectorStorageBackend.REDIS:
                results = await self._search_redis(index_name, query_vector, k, threshold, filters)
            elif storage_backend == VectorStorageBackend.MEMORY:
                results = await self._search_memory(index_name, query_vector, k, threshold, filters)
            elif storage_backend == VectorStorageBackend.HYBRID:
                results = await self._search_hybrid(index_name, query_vector, k, threshold, filters)
            else:
                raise ValueError(f"Unsupported storage backend: {storage_backend}")
            
            search_time = (datetime.now() - start_time).total_seconds()
            
            # Update performance stats
            index_meta['performance_stats']['average_search_time'] = (
                index_meta['performance_stats']['average_search_time'] * 0.9 + search_time * 0.1
            )
            
            # Log performance
            await self.performance_tracker.log_index_operation(
                index_name, 'search', search_time,
                {'k': k, 'results_count': len(results), 'threshold': threshold}
            )
            
            logger.debug(f"Vector search in {index_name} completed in {search_time:.3f}s, found {len(results)} results")
            return results
            
        except Exception as e:
            logger.error(f"Failed to search in vector index {index_name}: {str(e)}")
            return []
    
    async def _search_postgresql(self, index_name: str, query_vector: np.ndarray,
                               k: int, threshold: float, filters: Optional[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Search vectors in PostgreSQL backend"""
        try:
            if index_name not in self.postgresql_indexes:
                raise ValueError(f"PostgreSQL index {index_name} not found")
            
            table_name = self.postgresql_indexes[index_name]['table_name']
            distance_func = self.postgresql_indexes[index_name]['distance_function']
            
            conn = await self.db_manager.get_connection()
            
            # Build WHERE clause from filters
            where_clause = ""
            params = [query_vector.tolist(), k]
            param_count = 2
            
            if filters:
                conditions = []
                for key, value in filters.items():
                    param_count += 1
                    conditions.append(f"{key} = ${param_count}")
                    params.append(value)
                
                if conditions:
                    where_clause = "WHERE " + " AND ".join(conditions)
            
            # Execute similarity search
            if distance_func == "vector_cosine_ops":
                distance_op = "<=>"
            elif distance_func == "vector_ip_ops":
                distance_op = "<#>"
            else:
                distance_op = "<->"
            
            query = f"""
                SELECT content_id, user_id, content_type, embedding_type, metadata,
                       quality_score, vector_data {distance_op} $1 as distance,
                       created_at
                FROM {table_name}
                {where_clause}
                ORDER BY vector_data {distance_op} $1
                LIMIT $2
            """
            
            rows = await conn.fetch(query, *params)
            
            # Convert to result format
            results = []
            for row in rows:
                # Convert distance to similarity
                similarity = self._distance_to_similarity(row['distance'], distance_func)
                
                if similarity >= threshold:
                    results.append({
                        'content_id': row['content_id'],
                        'user_id': row['user_id'],
                        'content_type': row['content_type'],
                        'embedding_type': row['embedding_type'],
                        'similarity_score': float(similarity),
                        'distance': float(row['distance']),
                        'quality_score': float(row['quality_score']),
                        'metadata': row['metadata'],
                        'created_at': row['created_at'].isoformat()
                    })
            
            return results
            
        except Exception as e:
            logger.error(f"Failed to search PostgreSQL vectors: {str(e)}")
            return []
        finally:
            await self.db_manager.return_connection(conn)
    
    def _distance_to_similarity(self, distance: float, distance_func: str) -> float:
        """Convert distance to similarity score"""
        if distance_func == "vector_cosine_ops":
            return 1.0 - distance  # Cosine distance to similarity
        elif distance_func == "vector_ip_ops":
            return distance  # Inner product is already similarity
        else:
            return 1.0 / (1.0 + distance)  # L2 distance to similarity
    
    async def _search_memory(self, index_name: str, query_vector: np.ndarray,
                           k: int, threshold: float, filters: Optional[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Search vectors in memory backend"""
        try:
            mem_index = self.memory_indexes[index_name]
            
            if mem_index['total_vectors'] == 0:
                return []
            
            vectors = mem_index['vectors']
            content_ids = mem_index['content_ids']
            index_type = mem_index['index_type']
            
            # Calculate similarities
            if index_type == VectorIndexType.COSINE:
                # Normalize vectors for cosine similarity
                query_norm = query_vector / np.linalg.norm(query_vector)
                vectors_norm = vectors / np.linalg.norm(vectors, axis=1, keepdims=True)
                similarities = np.dot(vectors_norm, query_norm)
            elif index_type == VectorIndexType.DOT_PRODUCT:
                similarities = np.dot(vectors, query_vector)
            else:  # Euclidean
                distances = np.linalg.norm(vectors - query_vector, axis=1)
                similarities = 1.0 / (1.0 + distances)
            
            # Get top k results above threshold
            valid_indices = np.where(similarities >= threshold)[0]
            top_indices = valid_indices[np.argsort(similarities[valid_indices])[::-1]][:k]
            
            results = []
            for idx in top_indices:
                results.append({
                    'content_id': content_ids[idx],
                    'similarity_score': float(similarities[idx]),
                    'vector_index': int(idx)
                })
            
            return results
            
        except Exception as e:
            logger.error(f"Failed to search memory vectors: {str(e)}")
            return []
    
    async def _search_hybrid(self, index_name: str, query_vector: np.ndarray,
                           k: int, threshold: float, filters: Optional[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Search vectors using hybrid approach"""
        try:
            # First try memory for fast search
            mem_results = await self._search_memory(index_name, query_vector, k, threshold, filters)
            
            if len(mem_results) >= k:
                return mem_results
            
            # Fall back to PostgreSQL for comprehensive search
            pg_results = await self._search_postgresql(index_name, query_vector, k, threshold, filters)
            
            # Merge and deduplicate results
            seen_content_ids = set()
            combined_results = []
            
            for result in mem_results + pg_results:
                content_id = result['content_id']
                if content_id not in seen_content_ids:
                    seen_content_ids.add(content_id)
                    combined_results.append(result)
            
            # Sort by similarity and return top k
            combined_results.sort(key=lambda x: x['similarity_score'], reverse=True)
            return combined_results[:k]
            
        except Exception as e:
            logger.error(f"Failed to search hybrid vectors: {str(e)}")
            return []
    
    async def _save_index_metadata(self, index_name: str):
        """Save index metadata to disk"""
        try:
            metadata_path = self.storage_path / f"{index_name}_metadata.json"
            
            metadata = self.index_metadata[index_name].copy()
            # Convert datetime to string for JSON serialization
            metadata['created_at'] = metadata['created_at'].isoformat()
            metadata['last_updated'] = metadata['last_updated'].isoformat()
            
            with open(metadata_path, 'w') as f:
                json.dump(metadata, f, indent=2)
            
            logger.debug(f"Vector index metadata saved for {index_name}")
            
        except Exception as e:
            logger.error(f"Failed to save vector index metadata: {str(e)}")
    
    async def _load_existing_indexes(self):
        """Load existing vector indexes"""
        try:
            # Load from metadata files
            for metadata_file in self.storage_path.glob("*_metadata.json"):
                index_name = metadata_file.stem.replace("_metadata", "")
                try:
                    with open(metadata_file, 'r') as f:
                        metadata = json.load(f)
                        
                    # Convert string back to datetime
                    metadata['created_at'] = datetime.fromisoformat(metadata['created_at'])
                    metadata['last_updated'] = datetime.fromisoformat(metadata['last_updated'])
                    
                    self.index_metadata[index_name] = metadata
                    
                except Exception as e:
                    logger.error(f"Failed to load metadata for index {index_name}: {str(e)}")
            
            # Load PostgreSQL indexes
            if PGVECTOR_AVAILABLE:
                await self._load_postgresql_indexes()
            
            logger.info(f"Loaded {len(self.index_metadata)} vector indexes")
            
        except Exception as e:
            logger.error(f"Failed to load existing vector indexes: {str(e)}")
    
    async def _load_postgresql_indexes(self):
        """Load PostgreSQL vector indexes"""
        try:
            conn = await self.db_manager.get_connection()
            
            rows = await conn.fetch("""
                SELECT index_name, table_name, dimension, index_type, distance_function
                FROM vector_index_metadata
                WHERE storage_backend = 'postgresql' OR storage_backend = 'hybrid'
            """)
            
            for row in rows:
                self.postgresql_indexes[row['index_name']] = {
                    'table_name': row['table_name'],
                    'dimension': row['dimension'],
                    'index_type': row['index_type'],
                    'distance_function': row['distance_function']
                }
            
        except Exception as e:
            logger.debug(f"Could not load PostgreSQL indexes: {str(e)}")
        finally:
            await self.db_manager.return_connection(conn)
    
    async def _setup_optimization_schedule(self):
        """Setup automatic index optimization schedule"""
        # This would typically run as a background task
        pass
    
    async def get_index_stats(self, index_name: Optional[str] = None) -> Dict[str, Any]:
        """
Get comprehensive statistics for vector indexes"""
        if index_name:
            if index_name not in self.index_metadata:
                return {'error': f'Index {index_name} not found'}
            
            metadata = self.index_metadata[index_name]
            return {
                'index_name': index_name,
                'dimension': metadata['dimension'],
                'index_type': metadata['index_type'],
                'storage_backend': metadata['storage_backend'],
                'total_vectors': metadata['total_vectors'],
                'created_at': metadata['created_at'].isoformat(),
                'last_updated': metadata['last_updated'].isoformat(),
                'performance_stats': metadata['performance_stats'],
                'memory_usage': metadata['total_vectors'] * metadata['dimension'] * 4  # Approximate bytes
            }
        else:
            # Return stats for all indexes
            stats = {
                'total_indexes': len(self.index_metadata),
                'total_vectors': sum(meta['total_vectors'] for meta in self.index_metadata.values()),
                'storage_backends': {},
                'indexes': {}
            }
            
            # Count by storage backend
            for meta in self.index_metadata.values():
                backend = meta['storage_backend']
                stats['storage_backends'][backend] = stats['storage_backends'].get(backend, 0) + 1
            
            # Individual index stats
            for name in self.index_metadata:
                stats['indexes'][name] = await self.get_index_stats(name)
            
            return stats
    
    async def cleanup(self):
        """
Cleanup resources and save indexes"""
        try:
            # Save all index metadata
            save_tasks = [self._save_index_metadata(name) for name in self.index_metadata]
            await asyncio.gather(*save_tasks, return_exceptions=True)
            
            # Cleanup thread executor
            self.thread_executor.shutdown(wait=True)
            
            # Cleanup managers
            if self.performance_tracker:
                await self.performance_tracker.cleanup()
            if self.security_manager:
                await self.security_manager.cleanup()
            if self.redis_manager:
                await self.redis_manager.cleanup()
            if self.db_manager:
                await self.db_manager.cleanup()
            
            logger.info("VectorIndexManager cleanup completed")
            
        except Exception as e:
            logger.error(f"Error during VectorIndexManager cleanup: {str(e)}")
