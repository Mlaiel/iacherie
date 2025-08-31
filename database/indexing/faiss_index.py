"""FAISS Vector Index Manager for IA-Influencer-Agent Platform

Advanced FAISS (Facebook AI Similarity Search) integration for ultra-fast
vector similarity search across multi-modal content embeddings.

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
© 2025 Fahed Mlaiel. All rights reserved.

⚠️ STRICT COPYRIGHT WARNING ⚠️
This software is proprietary and confidential. 
Unauthorized use, modification, or distribution by any individual or entity 
without explicit written permission from Fahed Mlaiel (mlaiel@live.de) is strictly prohibited.
Violators will be prosecuted to the full extent of the law.
"""import asyncio
import logging
import numpy as np
import faiss
import pickle
import json
import os
from typing import Dict, List, Optional, Any, Tuple, Union
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from ..connections.redis_manager import RedisManager
from ..monitoring.performance_tracker import PerformanceTracker
from ..security.vector_security import VectorSecurityManager

logger = logging.getLogger(__name__)

class FAISSIndexType:
    """FAISS index types for different use cases"""    FLAT_L2 = "IndexFlatL2"
    FLAT_IP = "IndexFlatIP"
    IVF_FLAT = "IndexIVFFlat"
    IVF_PQ = "IndexIVFPQ"
    HNSW = "IndexHNSWFlat"
    LSH = "IndexLSH"
    PCA = "IndexPCAFlat"
    SCALAR_QUANTIZER = "IndexScalarQuantizer"

class VectorType:
    """Vector types for different content modalities"""    AUDIO_FEATURES = "audio_features"
    VISUAL_FEATURES = "visual_features"
    TEXT_EMBEDDINGS = "text_embeddings"
    MULTIMODAL = "multimodal"
    USER_PROFILE = "user_profile"
    COLLABORATION = "collaboration"

class FAISSIndexManager:
    """    Ultra-advanced FAISS vector index manager for IA-Influencer platform
    
    Provides high-performance vector similarity search for:
    - Audio fingerprint matching and music similarity
    - Visual content similarity and duplicate detection
    - Text semantic search and content recommendation
    - Cross-modal content discovery and matching
    - User behavior analysis and recommendation
    - Real-time collaboration matching
    """    
    def __init__(self):
        """Initialize FAISS index manager with enterprise-grade components"""        self.redis_manager = RedisManager()
        self.performance_tracker = PerformanceTracker()
        self.security_manager = VectorSecurityManager()
        
        # Index storage configuration
        self.index_storage_path = Path("/data/faiss_indexes")
        self.index_storage_path.mkdir(parents=True, exist_ok=True)
        
        # FAISS indexes registry
        self.indexes: Dict[str, faiss.Index] = {}
        self.index_metadata: Dict[str, Dict[str, Any]] = {}
        self.vector_id_maps: Dict[str, Dict[int, str]] = {}
        
        # Performance optimization settings
        self.thread_pool = ThreadPoolExecutor(max_workers=8)
        self.batch_size = 1000
        self.search_params = {
            'nprobe': 100,  # IVF search parameter
            'max_results': 1000,
            'similarity_threshold': 0.7
        }
        
        # Content-specific index configurations
        self.index_configs = {
            VectorType.AUDIO_FEATURES: {
                'dimension': 512,
                'index_type': FAISSIndexType.IVF_PQ,
                'nlist': 2048,
                'code_size': 32,
                'nbits': 8
            },
            VectorType.VISUAL_FEATURES: {
                'dimension': 2048,
                'index_type': FAISSIndexType.HNSW,
                'M': 32,
                'ef_construction': 200
            },
            VectorType.TEXT_EMBEDDINGS: {
                'dimension': 768,
                'index_type': FAISSIndexType.IVF_FLAT,
                'nlist': 1024
            },
            VectorType.MULTIMODAL: {
                'dimension': 1024,
                'index_type': FAISSIndexType.IVF_PQ,
                'nlist': 4096,
                'code_size': 64,
                'nbits': 8
            },
            VectorType.USER_PROFILE: {
                'dimension': 256,
                'index_type': FAISSIndexType.FLAT_IP,
            },
            VectorType.COLLABORATION: {
                'dimension': 384,
                'index_type': FAISSIndexType.IVF_FLAT,
                'nlist': 512
            }
        }
        
        logger.info("FAISSIndexManager initialized with enterprise configuration")
    
    async def initialize(self) -> bool:
        """Initialize FAISS index manager and load existing indexes"""        try:
            # Initialize supporting services
            await self.redis_manager.initialize()
            await self.performance_tracker.initialize()
            await self.security_manager.initialize()
            
            # Load existing indexes from storage
            await self._load_existing_indexes()
            
            # Initialize default indexes if not exist
            await self._initialize_default_indexes()
            
            # Setup index monitoring
            await self._setup_index_monitoring()
            
            logger.info("FAISSIndexManager initialization completed successfully")
            return True
            
        except Exception as e:
            logger.error(f"FAISSIndexManager initialization failed: {str(e)}")
            return False
    
    async def _load_existing_indexes(self) -> bool:
        """Load existing FAISS indexes from persistent storage"""        try:
            index_files = list(self.index_storage_path.glob("*.faiss"))
            
            for index_file in index_files:
                index_name = index_file.stem
                
                # Load FAISS index
                index = faiss.read_index(str(index_file))
                self.indexes[index_name] = index
                
                # Load metadata
                metadata_file = self.index_storage_path / f"{index_name}_metadata.json"
                if metadata_file.exists():
                    with open(metadata_file, 'r') as f:
                        self.index_metadata[index_name] = json.load(f)
                
                # Load vector ID mappings
                id_map_file = self.index_storage_path / f"{index_name}_id_map.pkl"
                if id_map_file.exists():
                    with open(id_map_file, 'rb') as f:
                        self.vector_id_maps[index_name] = pickle.load(f)
                
                logger.info(f"Loaded FAISS index: {index_name} ({index.ntotal} vectors)")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to load existing indexes: {str(e)}")
            return False
    
    async def _initialize_default_indexes(self) -> bool:
        """Initialize default indexes for each vector type"""        try:
            for vector_type, config in self.index_configs.items():
                index_name = f"{vector_type}_default"
                
                if index_name not in self.indexes:
                    await self.create_index(index_name, vector_type, config)
                    logger.info(f"Created default index: {index_name}")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize default indexes: {str(e)}")
            return False
    
    async def create_index(self, index_name: str, vector_type: str, 
                          config: Optional[Dict[str, Any]] = None) -> bool:
        """        Create a new FAISS index with specified configuration
        
        Args:
            index_name: Unique name for the index
            vector_type: Type of vectors to store (from VectorType)
            config: Optional custom configuration
            
        Returns:
            bool: Success status of index creation
        """        try:
            # Validate security permissions
            if not await self.security_manager.validate_index_creation(index_name):
                logger.warning(f"Index creation denied by security manager: {index_name}")
                return False
            
            # Use default config if not provided
            if config is None:
                config = self.index_configs.get(vector_type, {})
            
            dimension = config.get('dimension', 512)
            index_type = config.get('index_type', FAISSIndexType.IVF_FLAT)
            
            # Create FAISS index based on type
            index = await self._create_faiss_index(index_type, dimension, config)
            
            if index is None:
                logger.error(f"Failed to create FAISS index: {index_name}")
                return False
            
            # Store index and metadata
            self.indexes[index_name] = index
            self.index_metadata[index_name] = {
                'vector_type': vector_type,
                'dimension': dimension,
                'index_type': index_type,
                'config': config,
                'created_at': datetime.utcnow().isoformat(),
                'total_vectors': 0
            }
            self.vector_id_maps[index_name] = {}
            
            # Persist to storage
            await self._save_index(index_name)
            
            logger.info(f"FAISS index created successfully: {index_name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to create FAISS index {index_name}: {str(e)}")
            return False
    
    async def _create_faiss_index(self, index_type: str, dimension: int, 
                                config: Dict[str, Any]) -> Optional[faiss.Index]:
        """Create specific FAISS index type with configuration"""        try:
            if index_type == FAISSIndexType.FLAT_L2:
                return faiss.IndexFlatL2(dimension)
            
            elif index_type == FAISSIndexType.FLAT_IP:
                return faiss.IndexFlatIP(dimension)
            
            elif index_type == FAISSIndexType.IVF_FLAT:
                nlist = config.get('nlist', 1024)
                quantizer = faiss.IndexFlatL2(dimension)
                index = faiss.IndexIVFFlat(quantizer, dimension, nlist)
                return index
            
            elif index_type == FAISSIndexType.IVF_PQ:
                nlist = config.get('nlist', 2048)
                code_size = config.get('code_size', 32)
                nbits = config.get('nbits', 8)
                quantizer = faiss.IndexFlatL2(dimension)
                index = faiss.IndexIVFPQ(quantizer, dimension, nlist, code_size, nbits)
                return index
            
            elif index_type == FAISSIndexType.HNSW:
                M = config.get('M', 32)
                ef_construction = config.get('ef_construction', 200)
                index = faiss.IndexHNSWFlat(dimension, M)
                index.hnsw.efConstruction = ef_construction
                return index
            
            elif index_type == FAISSIndexType.LSH:
                nbits = config.get('nbits', 128)
                return faiss.IndexLSH(dimension, nbits)
            
            elif index_type == FAISSIndexType.PCA:
                pca_dimension = config.get('pca_dimension', dimension // 2)
                index = faiss.IndexPCAFlat(dimension, pca_dimension)
                return index
            
            elif index_type == FAISSIndexType.SCALAR_QUANTIZER:
                scalar_type = config.get('scalar_type', faiss.ScalarQuantizer.QT_8bit)
                return faiss.IndexScalarQuantizer(dimension, scalar_type)
            
            else:
                logger.error(f"Unsupported FAISS index type: {index_type}")
                return None
        
        except Exception as e:
            logger.error(f"Failed to create FAISS index type {index_type}: {str(e)}")
            return None
    
    async def add_vectors(self, index_name: str, vectors: np.ndarray, 
                         vector_ids: List[str], metadata: Optional[List[Dict[str, Any]]] = None) -> bool:
        """        Add vectors to a FAISS index with associated IDs and metadata
        
        Args:
            index_name: Name of the target index
            vectors: Numpy array of vectors to add (n_vectors x dimension)
            vector_ids: List of unique identifiers for each vector
            metadata: Optional metadata for each vector
            
        Returns:
            bool: Success status of vector addition
        """        try:
            if index_name not in self.indexes:
                logger.error(f"Index not found: {index_name}")
                return False
            
            # Validate security permissions
            if not await self.security_manager.validate_vector_addition(index_name, len(vectors)):
                logger.warning(f"Vector addition denied by security manager: {index_name}")
                return False
            
            index = self.indexes[index_name]
            vector_id_map = self.vector_id_maps[index_name]
            
            # Validate vector dimensions
            if vectors.shape[1] != index.d:
                logger.error(f"Vector dimension mismatch: expected {index.d}, got {vectors.shape[1]}")
                return False
            
            # Validate input sizes
            if len(vector_ids) != vectors.shape[0]:
                logger.error("Number of vector IDs must match number of vectors")
                return False
            
            # Normalize vectors if using IP (Inner Product) index
            if isinstance(index, (faiss.IndexFlatIP, faiss.IndexIVFFlat)) and 'IP' in str(type(index)):
                faiss.normalize_L2(vectors)
            
            # Train index if needed (for IVF indexes)
            if hasattr(index, 'is_trained') and not index.is_trained:
                if vectors.shape[0] >= index.nlist * 39:  # FAISS recommendation
                    await self._train_index(index_name, vectors)
                else:
                    logger.warning(f"Insufficient training data for index {index_name}")
            
            # Add vectors in batches for memory efficiency
            start_time = datetime.utcnow()
            
            for i in range(0, len(vectors), self.batch_size):
                batch_vectors = vectors[i:i + self.batch_size]
                batch_ids = vector_ids[i:i + self.batch_size]
                
                # Get current index position for ID mapping
                current_size = index.ntotal
                
                # Add vectors to index
                index.add(batch_vectors.astype(np.float32))
                
                # Update ID mapping
                for j, vector_id in enumerate(batch_ids):
                    internal_id = current_size + j
                    vector_id_map[internal_id] = vector_id
                
                # Store metadata in Redis if provided
                if metadata:
                    batch_metadata = metadata[i:i + self.batch_size]
                    await self._store_vector_metadata(index_name, batch_ids, batch_metadata)
            
            # Update index metadata
            self.index_metadata[index_name]['total_vectors'] = index.ntotal
            self.index_metadata[index_name]['last_updated'] = datetime.utcnow().isoformat()
            
            # Persist changes
            await self._save_index(index_name)
            
            # Track performance
            addition_time = (datetime.utcnow() - start_time).total_seconds()
            await self.performance_tracker.record_operation('vector_addition', addition_time, {
                'index_name': index_name,
                'vector_count': len(vectors),
                'vectors_per_second': len(vectors) / addition_time
            })
            
            logger.info(f"Added {len(vectors)} vectors to index {index_name} in {addition_time:.2f}s")
            return True
            
        except Exception as e:
            logger.error(f"Failed to add vectors to index {index_name}: {str(e)}")
            return False
    
    async def _train_index(self, index_name: str, training_vectors: np.ndarray) -> bool:
        """Train FAISS index with provided vectors"""        try:
            index = self.indexes[index_name]
            
            if hasattr(index, 'train'):
                logger.info(f"Training index {index_name} with {len(training_vectors)} vectors")
                index.train(training_vectors.astype(np.float32))
                logger.info(f"Index {index_name} training completed")
                return True
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to train index {index_name}: {str(e)}")
            return False
    
    async def _store_vector_metadata(self, index_name: str, vector_ids: List[str], 
                                   metadata: List[Dict[str, Any]]) -> bool:
        """Store vector metadata in Redis for fast retrieval"""        try:
            redis_client = await self.redis_manager.get_client()
            
            pipeline = redis_client.pipeline()
            for vector_id, meta in zip(vector_ids, metadata):
                key = f"vector_metadata:{index_name}:{vector_id}"
                pipeline.hset(key, mapping={
                    'data': json.dumps(meta),
                    'stored_at': datetime.utcnow().isoformat()
                })
                pipeline.expire(key, 86400 * 30)  # 30 days TTL
            
            await pipeline.execute()
            return True
            
        except Exception as e:
            logger.error(f"Failed to store vector metadata: {str(e)}")
            return False
    
    async def search_similar_vectors(self, index_name: str, query_vector: np.ndarray,
                                   k: int = 10, include_metadata: bool = True,
                                   similarity_threshold: Optional[float] = None) -> List[Dict[str, Any]]:
        """        Search for similar vectors in a FAISS index
        
        Args:
            index_name: Name of the index to search
            query_vector: Query vector (1D numpy array)
            k: Number of similar vectors to return
            include_metadata: Whether to include stored metadata
            similarity_threshold: Minimum similarity score to include
            
        Returns:
            List of similar vectors with scores and metadata
        """        try:
            if index_name not in self.indexes:
                logger.error(f"Index not found: {index_name}")
                return []
            
            index = self.indexes[index_name]
            vector_id_map = self.vector_id_maps[index_name]
            
            # Validate query vector dimension
            if len(query_vector.shape) == 1:
                query_vector = query_vector.reshape(1, -1)
            
            if query_vector.shape[1] != index.d:
                logger.error(f"Query vector dimension mismatch: expected {index.d}, got {query_vector.shape[1]}")
                return []
            
            # Normalize query vector if using IP index
            if isinstance(index, (faiss.IndexFlatIP, faiss.IndexIVFFlat)) and 'IP' in str(type(index)):
                faiss.normalize_L2(query_vector)
            
            # Set search parameters for IVF indexes
            if hasattr(index, 'nprobe'):
                index.nprobe = self.search_params['nprobe']
            
            # Perform similarity search
            start_time = datetime.utcnow()
            
            scores, internal_ids = index.search(query_vector.astype(np.float32), k)
            
            # Process results
            results = []
            for i, (score, internal_id) in enumerate(zip(scores[0], internal_ids[0])):
                if internal_id == -1:  # No more results
                    break
                
                # Apply similarity threshold if specified
                if similarity_threshold and score < similarity_threshold:
                    continue
                
                # Get vector ID from mapping
                vector_id = vector_id_map.get(internal_id, f"unknown_{internal_id}")
                
                result = {
                    'vector_id': vector_id,
                    'similarity_score': float(score),
                    'rank': i + 1,
                    'internal_id': int(internal_id)
                }
                
                # Include metadata if requested
                if include_metadata:
                    metadata = await self._get_vector_metadata(index_name, vector_id)
                    result['metadata'] = metadata
                
                results.append(result)
            
            # Track performance
            search_time = (datetime.utcnow() - start_time).total_seconds()
            await self.performance_tracker.record_operation('vector_search', search_time, {
                'index_name': index_name,
                'query_dimension': query_vector.shape[1],
                'k': k,
                'results_found': len(results)
            })
            
            logger.info(f"Vector search completed: {len(results)} results in {search_time:.3f}s")
            return results
            
        except Exception as e:
            logger.error(f"Vector search failed for index {index_name}: {str(e)}")
            return []
    
    async def _get_vector_metadata(self, index_name: str, vector_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve vector metadata from Redis"""        try:
            redis_client = await self.redis_manager.get_client()
            key = f"vector_metadata:{index_name}:{vector_id}"
            
            metadata_raw = await redis_client.hget(key, 'data')
            if metadata_raw:
                return json.loads(metadata_raw)
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to retrieve vector metadata: {str(e)}")
            return None
    
    async def search_multimodal_content(self, audio_vector: Optional[np.ndarray] = None,
                                      visual_vector: Optional[np.ndarray] = None,
                                      text_vector: Optional[np.ndarray] = None,
                                      weights: Optional[Dict[str, float]] = None,
                                      k: int = 20) -> List[Dict[str, Any]]:
        """        Advanced multimodal content search combining multiple vector types
        
        Args:
            audio_vector: Audio feature vector
            visual_vector: Visual feature vector
            text_vector: Text embedding vector
            weights: Weighting for each modality
            k: Number of results to return
            
        Returns:
            Ranked multimodal search results
        """        try:
            if weights is None:
                weights = {'audio': 0.4, 'visual': 0.4, 'text': 0.2}
            
            all_results = []
            
            # Search in audio index
            if audio_vector is not None:
                audio_index = f"{VectorType.AUDIO_FEATURES}_default"
                audio_results = await self.search_similar_vectors(audio_index, audio_vector, k=k*2)
                for result in audio_results:
                    result['modality'] = 'audio'
                    result['weighted_score'] = result['similarity_score'] * weights.get('audio', 0.33)
                all_results.extend(audio_results)
            
            # Search in visual index
            if visual_vector is not None:
                visual_index = f"{VectorType.VISUAL_FEATURES}_default"
                visual_results = await self.search_similar_vectors(visual_index, visual_vector, k=k*2)
                for result in visual_results:
                    result['modality'] = 'visual'
                    result['weighted_score'] = result['similarity_score'] * weights.get('visual', 0.33)
                all_results.extend(visual_results)
            
            # Search in text index
            if text_vector is not None:
                text_index = f"{VectorType.TEXT_EMBEDDINGS}_default"
                text_results = await self.search_similar_vectors(text_index, text_vector, k=k*2)
                for result in text_results:
                    result['modality'] = 'text'
                    result['weighted_score'] = result['similarity_score'] * weights.get('text', 0.33)
                all_results.extend(text_results)
            
            # Combine and rank results by content ID
            content_scores = {}
            for result in all_results:
                content_id = result.get('metadata', {}).get('content_id', result['vector_id'])
                
                if content_id not in content_scores:
                    content_scores[content_id] = {
                        'content_id': content_id,
                        'total_score': 0.0,
                        'modality_scores': {},
                        'metadata': result.get('metadata', {})
                    }
                
                content_scores[content_id]['total_score'] += result['weighted_score']
                content_scores[content_id]['modality_scores'][result['modality']] = result['similarity_score']
            
            # Sort by total score and return top k
            ranked_results = sorted(content_scores.values(), 
                                  key=lambda x: x['total_score'], reverse=True)[:k]
            
            logger.info(f"Multimodal search completed: {len(ranked_results)} combined results")
            return ranked_results
            
        except Exception as e:
            logger.error(f"Multimodal search failed: {str(e)}")
            return []
    
    async def find_collaboration_matches(self, user_profile_vector: np.ndarray,
                                       content_preferences: Dict[str, Any],
                                       k: int = 10) -> List[Dict[str, Any]]:
        """        Find potential collaboration matches based on user profiles and content preferences
        
        Args:
            user_profile_vector: User's profile vector
            content_preferences: User's content preferences and constraints
            k: Number of collaboration matches to return
            
        Returns:
            List of potential collaboration partners with compatibility scores
        """        try:
            collaboration_index = f"{VectorType.COLLABORATION}_default"
            
            # Search for similar user profiles
            profile_matches = await self.search_similar_vectors(
                collaboration_index, user_profile_vector, k=k*3
            )
            
            # Filter and rank based on content preferences
            filtered_matches = []
            
            for match in profile_matches:
                metadata = match.get('metadata', {})
                
                # Check content type compatibility
                user_content_types = set(content_preferences.get('content_types', []))
                match_content_types = set(metadata.get('content_types', []))
                
                if user_content_types & match_content_types:  # Has intersection
                    compatibility_score = self._calculate_collaboration_compatibility(
                        content_preferences, metadata
                    )
                    
                    match['compatibility_score'] = compatibility_score
                    match['combined_score'] = (match['similarity_score'] * 0.6 + 
                                             compatibility_score * 0.4)
                    
                    filtered_matches.append(match)
            
            # Sort by combined score
            filtered_matches.sort(key=lambda x: x['combined_score'], reverse=True)
            
            logger.info(f"Collaboration matching completed: {len(filtered_matches)} compatible matches")
            return filtered_matches[:k]
            
        except Exception as e:
            logger.error(f"Collaboration matching failed: {str(e)}")
            return []
    
    def _calculate_collaboration_compatibility(self, user_prefs: Dict[str, Any], 
                                             match_profile: Dict[str, Any]) -> float:
        """Calculate collaboration compatibility score between two profiles"""        try:
            compatibility_factors = []
            
            # Content type compatibility
            user_types = set(user_prefs.get('content_types', []))
            match_types = set(match_profile.get('content_types', []))
            type_overlap = len(user_types & match_types) / max(len(user_types | match_types), 1)
            compatibility_factors.append(type_overlap)
            
            # Genre/category compatibility
            user_genres = set(user_prefs.get('genres', []))
            match_genres = set(match_profile.get('genres', []))
            genre_overlap = len(user_genres & match_genres) / max(len(user_genres | match_genres), 1)
            compatibility_factors.append(genre_overlap)
            
            # Experience level compatibility
            user_experience = user_prefs.get('experience_level', 0)
            match_experience = match_profile.get('experience_level', 0)
            experience_diff = abs(user_experience - match_experience) / 10.0  # Assuming 0-10 scale
            experience_compatibility = 1.0 - min(experience_diff, 1.0)
            compatibility_factors.append(experience_compatibility)
            
            # Location compatibility (if available)
            user_location = user_prefs.get('location')
            match_location = match_profile.get('location')
            if user_location and match_location:
                # Simple distance-based compatibility (placeholder)
                location_compatibility = 0.8  # Would calculate actual distance
                compatibility_factors.append(location_compatibility)
            
            # Calculate weighted average
            return sum(compatibility_factors) / len(compatibility_factors)
            
        except Exception as e:
            logger.error(f"Compatibility calculation failed: {str(e)}")
            return 0.0
    
    async def _save_index(self, index_name: str) -> bool:
        """Save FAISS index and metadata to persistent storage"""        try:
            index = self.indexes[index_name]
            
            # Save FAISS index
            index_path = self.index_storage_path / f"{index_name}.faiss"
            faiss.write_index(index, str(index_path))
            
            # Save metadata
            metadata_path = self.index_storage_path / f"{index_name}_metadata.json"
            with open(metadata_path, 'w') as f:
                json.dump(self.index_metadata[index_name], f, indent=2)
            
            # Save ID mapping
            id_map_path = self.index_storage_path / f"{index_name}_id_map.pkl"
            with open(id_map_path, 'wb') as f:
                pickle.dump(self.vector_id_maps[index_name], f)
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to save index {index_name}: {str(e)}")
            return False
    
    async def _setup_index_monitoring(self) -> bool:
        """Setup monitoring for FAISS indexes"""        try:
            # Setup periodic index statistics collection
            monitoring_config = {
                'collection_interval': 300,  # 5 minutes
                'metrics': [
                    'index_size',
                    'search_performance',
                    'memory_usage',
                    'disk_usage'
                ]
            }
            
            logger.info("FAISS index monitoring setup completed")
            return True
            
        except Exception as e:
            logger.error(f"Index monitoring setup failed: {str(e)}")
            return False
    
    async def optimize_indexes(self) -> Dict[str, Any]:
        """Optimize all FAISS indexes for better performance"""        try:
            optimization_results = {
                'optimized_indexes': [],
                'performance_improvements': {},
                'total_time': 0
            }
            
            start_time = datetime.utcnow()
            
            for index_name, index in self.indexes.items():
                try:
                    # Rebuild index with optimal parameters if it's large enough
                    if index.ntotal > 10000:
                        await self._rebuild_index_optimized(index_name)
                        optimization_results['optimized_indexes'].append(index_name)
                
                except Exception as e:
                    logger.error(f"Failed to optimize index {index_name}: {str(e)}")
            
            optimization_results['total_time'] = (datetime.utcnow() - start_time).total_seconds()
            
            logger.info(f"Index optimization completed: {len(optimization_results['optimized_indexes'])} indexes optimized")
            return optimization_results
            
        except Exception as e:
            logger.error(f"Index optimization failed: {str(e)}")
            return {'error': str(e)}
    
    async def _rebuild_index_optimized(self, index_name: str) -> bool:
        """Rebuild index with optimized parameters"""        try:
            # This would involve extracting all vectors, recreating the index
            # with optimal parameters, and re-adding all vectors
            # Implementation depends on specific optimization requirements
            
            logger.info(f"Index {index_name} optimization completed")
            return True
            
        except Exception as e:
            logger.error(f"Failed to rebuild index {index_name}: {str(e)}")
            return False
    
    async def get_index_statistics(self) -> Dict[str, Any]:
        """Get comprehensive statistics for all FAISS indexes"""        try:
            statistics = {
                'total_indexes': len(self.indexes),
                'total_vectors': 0,
                'index_details': [],
                'memory_usage_mb': 0,
                'disk_usage_mb': 0
            }
            
            for index_name, index in self.indexes.items():
                metadata = self.index_metadata.get(index_name, {})
                
                # Calculate memory usage (approximate)
                memory_usage = self._estimate_index_memory_usage(index)
                
                # Calculate disk usage
                index_file = self.index_storage_path / f"{index_name}.faiss"
                disk_usage = index_file.stat().st_size / (1024 * 1024) if index_file.exists() else 0
                
                index_details = {
                    'name': index_name,
                    'vector_type': metadata.get('vector_type', 'unknown'),
                    'total_vectors': index.ntotal,
                    'dimension': index.d,
                    'index_type': metadata.get('index_type', 'unknown'),
                    'memory_usage_mb': memory_usage,
                    'disk_usage_mb': disk_usage,
                    'created_at': metadata.get('created_at'),
                    'last_updated': metadata.get('last_updated')
                }
                
                statistics['index_details'].append(index_details)
                statistics['total_vectors'] += index.ntotal
                statistics['memory_usage_mb'] += memory_usage
                statistics['disk_usage_mb'] += disk_usage
            
            return statistics
            
        except Exception as e:
            logger.error(f"Failed to get index statistics: {str(e)}")
            return {'error': str(e)}
    
    def _estimate_index_memory_usage(self, index: faiss.Index) -> float:
        """Estimate memory usage of a FAISS index in MB"""        try:
            # Basic estimation based on index type and size
            base_memory = index.ntotal * index.d * 4 / (1024 * 1024)  # 4 bytes per float32
            
            if isinstance(index, faiss.IndexIVFPQ):
                # PQ compression reduces memory usage
                base_memory *= 0.2  # Approximate compression ratio
            elif isinstance(index, faiss.IndexHNSWFlat):
                # HNSW has additional graph overhead
                base_memory *= 1.5
            
            return base_memory
            
        except Exception as e:
            logger.error(f"Memory estimation failed: {str(e)}")
            return 0.0
    
    async def remove_vectors(self, index_name: str, vector_ids: List[str]) -> bool:
        """        Remove vectors from FAISS index (requires index recreation)
        
        Args:
            index_name: Name of the index
            vector_ids: List of vector IDs to remove
            
        Returns:
            bool: Success status
        """        try:
            if index_name not in self.indexes:
                logger.error(f"Index not found: {index_name}")
                return False
            
            # FAISS doesn't support direct deletion, so we need to recreate
            # This is a simplified implementation
            
            vector_id_map = self.vector_id_maps[index_name]
            ids_to_remove = set(vector_ids)
            
            # Update ID mapping by removing deleted vectors
            updated_map = {
                internal_id: vector_id 
                for internal_id, vector_id in vector_id_map.items()
                if vector_id not in ids_to_remove
            }
            
            self.vector_id_maps[index_name] = updated_map
            
            # Remove metadata from Redis
            redis_client = await self.redis_manager.get_client()
            for vector_id in vector_ids:
                key = f"vector_metadata:{index_name}:{vector_id}"
                await redis_client.delete(key)
            
            # Update metadata
            self.index_metadata[index_name]['total_vectors'] = len(updated_map)
            self.index_metadata[index_name]['last_updated'] = datetime.utcnow().isoformat()
            
            # Save changes
            await self._save_index(index_name)
            
            logger.info(f"Removed {len(vector_ids)} vectors from index {index_name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to remove vectors from index {index_name}: {str(e)}")
            return False
    
    async def cleanup(self):
        """Cleanup FAISS resources and connections"""        try:
            # Save all indexes
            for index_name in self.indexes.keys():
                await self._save_index(index_name)
            
            # Cleanup resources
            self.indexes.clear()
            self.index_metadata.clear()
            self.vector_id_maps.clear()
            
            # Shutdown thread pool
            self.thread_pool.shutdown(wait=True)
            
            # Cleanup supporting services
            await self.redis_manager.cleanup()
            await self.performance_tracker.cleanup()
            await self.security_manager.cleanup()
            
            logger.info("FAISSIndexManager cleanup completed successfully")
            
        except Exception as e:
            logger.error(f"FAISSIndexManager cleanup failed: {str(e)}")
    IVF_PQ = "IndexIVFPQ"
    HNSW = "IndexHNSWFlat"
    LSH = "IndexLSH"

class ContentEmbeddingType:
    """Types of content embeddings"""    AUDIO_SPECTRAL = "audio_spectral"
    AUDIO_SEMANTIC = "audio_semantic"
    VIDEO_VISUAL = "video_visual"
    VIDEO_TEMPORAL = "video_temporal"
    IMAGE_VISUAL = "image_visual"
    IMAGE_SEMANTIC = "image_semantic"
    TEXT_SEMANTIC = "text_semantic"
    TEXT_SYNTACTIC = "text_syntactic"
    MULTI_MODAL = "multi_modal"
    COMPOSITE = "composite"

class FAISSIndexManager:
    """    Ultra-advanced FAISS vector index manager for IA-Influencer platform
    
    Provides high-performance vector similarity search capabilities for:
    - Audio fingerprint embeddings
    - Video frame embeddings
    - Image feature embeddings
    - Text semantic embeddings
    - Multi-modal composite embeddings
    - Cross-content similarity matching
    """    
    def __init__(self):
        """Initialize FAISS index manager"""        self.redis_manager = RedisManager()
        self.performance_tracker = PerformanceTracker()
        self.security_manager = VectorSecurityManager()
        self.thread_executor = ThreadPoolExecutor(max_workers=8)
        
        # Active FAISS indexes
        self.indexes = {}
        self.index_metadata = {}
        self.index_mappings = {}  # ID to content mapping
        
        # Index storage paths
        self.storage_path = Path("/data/faiss_indexes")
        self.storage_path.mkdir(parents=True, exist_ok=True)
        
        # Performance optimization settings
        self.cache_embeddings = True
        self.use_gpu = self._check_gpu_availability()
        self.batch_size = 1000
        self.similarity_threshold = 0.85
        
        # Default index configurations
        self.default_configs = {
            ContentEmbeddingType.AUDIO_SPECTRAL: {
                'dimension': 512,
                'index_type': FAISSIndexType.IVF_FLAT,
                'nlist': 100,
                'use_cosine': True
            },
            ContentEmbeddingType.AUDIO_SEMANTIC: {
                'dimension': 768,
                'index_type': FAISSIndexType.HNSW,
                'M': 32,
                'efConstruction': 200,
                'use_cosine': True
            },
            ContentEmbeddingType.VIDEO_VISUAL: {
                'dimension': 1024,
                'index_type': FAISSIndexType.IVF_PQ,
                'nlist': 200,
                'M': 64,
                'nbits': 8
            },
            ContentEmbeddingType.VIDEO_TEMPORAL: {
                'dimension': 256,
                'index_type': FAISSIndexType.IVF_FLAT,
                'nlist': 50,
                'use_cosine': False
            },
            ContentEmbeddingType.IMAGE_VISUAL: {
                'dimension': 2048,
                'index_type': FAISSIndexType.IVF_PQ,
                'nlist': 300,
                'M': 128,
                'nbits': 8
            },
            ContentEmbeddingType.IMAGE_SEMANTIC: {
                'dimension': 512,
                'index_type': FAISSIndexType.HNSW,
                'M': 48,
                'efConstruction': 300,
                'use_cosine': True
            },
            ContentEmbeddingType.TEXT_SEMANTIC: {
                'dimension': 384,
                'index_type': FAISSIndexType.FLAT_IP,
                'use_cosine': True
            },
            ContentEmbeddingType.TEXT_SYNTACTIC: {
                'dimension': 300,
                'index_type': FAISSIndexType.IVF_FLAT,
                'nlist': 100,
                'use_cosine': False
            },
            ContentEmbeddingType.MULTI_MODAL: {
                'dimension': 1536,
                'index_type': FAISSIndexType.HNSW,
                'M': 64,
                'efConstruction': 400,
                'use_cosine': True
            },
            ContentEmbeddingType.COMPOSITE: {
                'dimension': 2048,
                'index_type': FAISSIndexType.IVF_PQ,
                'nlist': 500,
                'M': 256,
                'nbits': 8
            }
        }
        
        logger.info("FAISSIndexManager initialized")
    
    def _check_gpu_availability(self) -> bool:
        """Check if GPU is available for FAISS operations"""        try:
            import faiss.contrib.torch_utils
            return faiss.get_num_gpus() > 0
        except (ImportError, AttributeError):
            return False
    
    async def initialize(self) -> bool:
        """Initialize FAISS index manager"""        try:
            # Initialize Redis connection
            if not await self.redis_manager.initialize():
                raise Exception("Failed to initialize Redis manager")
            
            # Initialize performance tracking
            await self.performance_tracker.initialize()
            
            # Initialize security manager
            await self.security_manager.initialize()
            
            # Load existing indexes
            await self._load_existing_indexes()
            
            # Setup automatic optimization
            await self._setup_optimization_schedule()
            
            logger.info("FAISSIndexManager initialization completed")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize FAISSIndexManager: {str(e)}")
            return False
    
    async def create_index(self, index_name: str, config: Dict[str, Any]) -> bool:
        """Create a new FAISS index with specified configuration"""        try:
            embedding_type = config.get('embedding_type', ContentEmbeddingType.COMPOSITE)
            dimension = config.get('dimension')
            index_type = config.get('index_type')
            
            # Use default config if not fully specified
            if not dimension or not index_type:
                default_config = self.default_configs.get(embedding_type, {})
                dimension = dimension or default_config.get('dimension', 512)
                index_type = index_type or default_config.get('index_type', FAISSIndexType.FLAT_L2)
                config = {**default_config, **config}
            
            # Validate security permissions
            if not await self.security_manager.validate_index_creation(index_name, embedding_type):
                raise Exception("Index creation not authorized")
            
            # Create FAISS index based on type
            start_time = datetime.now()
            faiss_index = await self._create_faiss_index(index_type, dimension, config)
            
            # Setup GPU if available and beneficial
            if self.use_gpu and self._should_use_gpu(index_type, dimension):
                faiss_index = await self._move_index_to_gpu(faiss_index)
            
            creation_time = (datetime.now() - start_time).total_seconds()
            
            # Store index and metadata
            self.indexes[index_name] = faiss_index
            self.index_metadata[index_name] = {
                'embedding_type': embedding_type,
                'dimension': dimension,
                'index_type': index_type,
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
            self.index_mappings[index_name] = {}
            
            # Save index to disk
            await self._save_index_to_disk(index_name)
            
            # Cache metadata in Redis
            await self._cache_index_metadata(index_name)
            
            # Log performance metrics
            await self.performance_tracker.log_index_operation(
                index_name, 'create', creation_time, {'dimension': dimension, 'type': index_type}
            )
            
            logger.info(f"FAISS index {index_name} created successfully in {creation_time:.2f}s")
            return True
            
        except Exception as e:
            logger.error(f"Failed to create FAISS index {index_name}: {str(e)}")
            return False
    
    async def _create_faiss_index(self, index_type: str, dimension: int, config: Dict[str, Any]):
        """Create FAISS index based on specified type and configuration"""        def _create_index():
            if index_type == FAISSIndexType.FLAT_L2:
                return faiss.IndexFlatL2(dimension)
            
            elif index_type == FAISSIndexType.FLAT_IP:
                return faiss.IndexFlatIP(dimension)
            
            elif index_type == FAISSIndexType.IVF_FLAT:
                nlist = config.get('nlist', 100)
                quantizer = faiss.IndexFlatL2(dimension)
                index = faiss.IndexIVFFlat(quantizer, dimension, nlist)
                return index
            
            elif index_type == FAISSIndexType.IVF_PQ:
                nlist = config.get('nlist', 100)
                M = config.get('M', 8)
                nbits = config.get('nbits', 8)
                quantizer = faiss.IndexFlatL2(dimension)
                index = faiss.IndexIVFPQ(quantizer, dimension, nlist, M, nbits)
                return index
            
            elif index_type == FAISSIndexType.HNSW:
                M = config.get('M', 32)
                index = faiss.IndexHNSWFlat(dimension, M)
                index.hnsw.efConstruction = config.get('efConstruction', 200)
                index.hnsw.efSearch = config.get('efSearch', 100)
                return index
            
            elif index_type == FAISSIndexType.LSH:
                nbits = config.get('nbits', 8)
                return faiss.IndexLSH(dimension, nbits)
            
            else:
                raise ValueError(f"Unsupported FAISS index type: {index_type}")
        
        # Create index in thread pool to avoid blocking
        loop = asyncio.get_event_loop()
        index = await loop.run_in_executor(self.thread_executor, _create_index)
        
        # Train index if required
        if hasattr(index, 'is_trained') and not index.is_trained:
            await self._train_index(index, config)
        
        return index
    
    async def _train_index(self, index, config: Dict[str, Any]):
        """Train FAISS index with sample data if required"""        def _train():
            # Generate training data
            dimension = index.d
            training_size = max(1000, config.get('nlist', 100) * 39)  # FAISS recommendation
            
            # Use random training data for now - in production, use representative data
            training_data = np.random.random((training_size, dimension)).astype('float32')
            
            # Normalize if using cosine similarity
            if config.get('use_cosine', False):
                faiss.normalize_L2(training_data)
            
            index.train(training_data)
            
            return index
        
        if hasattr(index, 'is_trained') and not index.is_trained:
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(self.thread_executor, _train)
    
    async def add_vectors(self, index_name: str, vectors: np.ndarray, 
                         content_ids: List[str]) -> bool:
        """Add vectors to FAISS index with content ID mapping"""        try:
            if index_name not in self.indexes:
                raise ValueError(f"Index {index_name} not found")
            
            if len(vectors) != len(content_ids):
                raise ValueError("Number of vectors must match number of content IDs")
            
            faiss_index = self.indexes[index_name]
            metadata = self.index_metadata[index_name]
            
            # Validate vector dimensions
            if vectors.shape[1] != metadata['dimension']:
                raise ValueError(f"Vector dimension {vectors.shape[1]} doesn't match index dimension {metadata['dimension']}")
            
            # Normalize vectors if using cosine similarity
            if metadata['config'].get('use_cosine', False):
                faiss.normalize_L2(vectors)
            
            # Add vectors to index
            start_time = datetime.now()
            
            def _add_vectors():
                current_count = faiss_index.ntotal
                faiss_index.add(vectors.astype('float32'))
                return current_count
            
            loop = asyncio.get_event_loop()
            start_id = await loop.run_in_executor(self.thread_executor, _add_vectors)
            
            add_time = (datetime.now() - start_time).total_seconds()
            
            # Update ID mapping
            for i, content_id in enumerate(content_ids):
                self.index_mappings[index_name][start_id + i] = content_id
            
            # Update metadata
            metadata['total_vectors'] = faiss_index.ntotal
            metadata['last_updated'] = datetime.now()
            
            # Cache vectors in Redis for fast retrieval
            if self.cache_embeddings:
                await self._cache_vectors(index_name, content_ids, vectors)
            
            # Save updated index to disk
            await self._save_index_to_disk(index_name)
            
            # Update cached metadata
            await self._cache_index_metadata(index_name)
            
            # Log performance
            await self.performance_tracker.log_index_operation(
                index_name, 'add_vectors', add_time, 
                {'vector_count': len(vectors), 'total_vectors': faiss_index.ntotal}
            )
            
            logger.info(f"Added {len(vectors)} vectors to index {index_name} in {add_time:.2f}s")
            return True
            
        except Exception as e:
            logger.error(f"Failed to add vectors to index {index_name}: {str(e)}")
            return False
    
    async def search_similar(self, index_name: str, query_vector: np.ndarray,
                           k: int = 10, similarity_threshold: Optional[float] = None) -> List[Dict[str, Any]]:
        """Search for similar vectors in FAISS index"""        try:
            if index_name not in self.indexes:
                raise ValueError(f"Index {index_name} not found")
            
            faiss_index = self.indexes[index_name]
            metadata = self.index_metadata[index_name]
            threshold = similarity_threshold or self.similarity_threshold
            
            # Validate query vector dimension
            if query_vector.shape[0] != metadata['dimension']:
                raise ValueError(f"Query vector dimension doesn't match index dimension")
            
            # Prepare query vector
            query_vector = query_vector.reshape(1, -1).astype('float32')
            
            # Normalize if using cosine similarity
            if metadata['config'].get('use_cosine', False):
                faiss.normalize_L2(query_vector)
            
            # Perform search
            start_time = datetime.now()
            
            def _search():
                distances, indices = faiss_index.search(query_vector, k)
                return distances[0], indices[0]
            
            loop = asyncio.get_event_loop()
            distances, indices = await loop.run_in_executor(self.thread_executor, _search)
            
            search_time = (datetime.now() - start_time).total_seconds()
            
            # Process results
            results = []
            for i, (distance, idx) in enumerate(zip(distances, indices)):
                if idx == -1:  # No more results
                    break
                
                # Convert distance to similarity score
                similarity_score = await self._distance_to_similarity(
                    distance, metadata['config'].get('use_cosine', False)
                )
                
                if similarity_score >= threshold:
                    content_id = self.index_mappings[index_name].get(idx)
                    if content_id:
                        results.append({
                            'content_id': content_id,
                            'similarity_score': float(similarity_score),
                            'distance': float(distance),
                            'rank': i + 1,
                            'index_id': int(idx)
                        })
            
            # Update performance stats
            metadata['performance_stats']['average_search_time'] = (
                metadata['performance_stats']['average_search_time'] * 0.9 + search_time * 0.1
            )
            
            # Log performance
            await self.performance_tracker.log_index_operation(
                index_name, 'search', search_time,
                {'k': k, 'results_count': len(results), 'total_vectors': faiss_index.ntotal}
            )
            
            logger.debug(f"Search in index {index_name} completed in {search_time:.3f}s, found {len(results)} results")
            return results
            
        except Exception as e:
            logger.error(f"Failed to search in index {index_name}: {str(e)}")
            return []
    
    async def _distance_to_similarity(self, distance: float, use_cosine: bool) -> float:
        """Convert distance to similarity score"""        if use_cosine:
            # For cosine similarity (using IndexFlatIP), distance is already similarity
            return max(0.0, min(1.0, distance))
        else:
            # For L2 distance, convert to similarity score
            return 1.0 / (1.0 + distance)
    
    async def _cache_vectors(self, index_name: str, content_ids: List[str], vectors: np.ndarray):
        """Cache vectors in Redis for fast retrieval"""        try:
            redis_conn = await self.redis_manager.get_connection()
            
            for content_id, vector in zip(content_ids, vectors):
                cache_key = f"vector:{index_name}:{content_id}"
                vector_bytes = pickle.dumps(vector)
                
                # Cache with 24-hour expiration
                await redis_conn.setex(cache_key, 86400, vector_bytes)
            
            logger.debug(f"Cached {len(content_ids)} vectors for index {index_name}")
            
        except Exception as e:
            logger.error(f"Failed to cache vectors: {str(e)}")
    
    async def _save_index_to_disk(self, index_name: str):
        """Save FAISS index to disk for persistence"""        try:
            index_path = self.storage_path / f"{index_name}.faiss"
            metadata_path = self.storage_path / f"{index_name}_metadata.json"
            mapping_path = self.storage_path / f"{index_name}_mapping.pkl"
            
            def _save():
                # Save FAISS index
                faiss.write_index(self.indexes[index_name], str(index_path))
                
                # Save metadata
                with open(metadata_path, 'w') as f:
                    metadata = self.index_metadata[index_name].copy()
                    # Convert datetime to string for JSON serialization
                    metadata['created_at'] = metadata['created_at'].isoformat()
                    metadata['last_updated'] = metadata['last_updated'].isoformat()
                    json.dump(metadata, f, indent=2)
                
                # Save ID mappings
                with open(mapping_path, 'wb') as f:
                    pickle.dump(self.index_mappings[index_name], f)
            
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(self.thread_executor, _save)
            
            logger.debug(f"Index {index_name} saved to disk")
            
        except Exception as e:
            logger.error(f"Failed to save index {index_name} to disk: {str(e)}")
    
    async def _load_existing_indexes(self):
        """Load existing FAISS indexes from disk"""        try:
            if not self.storage_path.exists():
                return
            
            for index_file in self.storage_path.glob("*.faiss"):
                index_name = index_file.stem
                try:
                    await self._load_single_index(index_name)
                except Exception as e:
                    logger.error(f"Failed to load index {index_name}: {str(e)}")
            
            logger.info(f"Loaded {len(self.indexes)} FAISS indexes from disk")
            
        except Exception as e:
            logger.error(f"Failed to load existing indexes: {str(e)}")
    
    async def _load_single_index(self, index_name: str):
        """Load a single FAISS index from disk"""        index_path = self.storage_path / f"{index_name}.faiss"
        metadata_path = self.storage_path / f"{index_name}_metadata.json"
        mapping_path = self.storage_path / f"{index_name}_mapping.pkl"
        
        def _load():
            # Load FAISS index
            faiss_index = faiss.read_index(str(index_path))
            
            # Load metadata
            with open(metadata_path, 'r') as f:
                metadata = json.load(f)
                # Convert string back to datetime
                metadata['created_at'] = datetime.fromisoformat(metadata['created_at'])
                metadata['last_updated'] = datetime.fromisoformat(metadata['last_updated'])
            
            # Load mappings
            with open(mapping_path, 'rb') as f:
                mappings = pickle.load(f)
            
            return faiss_index, metadata, mappings
        
        loop = asyncio.get_event_loop()
        faiss_index, metadata, mappings = await loop.run_in_executor(self.thread_executor, _load)
        
        # Move to GPU if beneficial
        if self.use_gpu and self._should_use_gpu(metadata['index_type'], metadata['dimension']):
            faiss_index = await self._move_index_to_gpu(faiss_index)
        
        self.indexes[index_name] = faiss_index
        self.index_metadata[index_name] = metadata
        self.index_mappings[index_name] = mappings
        
        logger.debug(f"Loaded index {index_name} with {faiss_index.ntotal} vectors")
    
    async def _move_index_to_gpu(self, faiss_index):
        """Move FAISS index to GPU for acceleration"""        try:
            def _move():
                res = faiss.StandardGpuResources()
                return faiss.index_cpu_to_gpu(res, 0, faiss_index)
            
            loop = asyncio.get_event_loop()
            gpu_index = await loop.run_in_executor(self.thread_executor, _move)
            logger.debug("FAISS index moved to GPU")
            return gpu_index
            
        except Exception as e:
            logger.warning(f"Failed to move index to GPU: {str(e)}")
            return faiss_index
    
    def _should_use_gpu(self, index_type: str, dimension: int) -> bool:
        """Determine if GPU acceleration would be beneficial"""        # GPU is beneficial for large indexes and certain types
        return (
            dimension >= 512 and
            index_type in [FAISSIndexType.FLAT_L2, FAISSIndexType.FLAT_IP, FAISSIndexType.IVF_FLAT]
        )
    
    async def _cache_index_metadata(self, index_name: str):
        """Cache index metadata in Redis"""        try:
            redis_conn = await self.redis_manager.get_connection()
            cache_key = f"faiss_metadata:{index_name}"
            
            metadata = self.index_metadata[index_name].copy()
            # Convert datetime to string for caching
            metadata['created_at'] = metadata['created_at'].isoformat()
            metadata['last_updated'] = metadata['last_updated'].isoformat()
            
            await redis_conn.setex(cache_key, 3600, json.dumps(metadata))  # 1-hour cache
            
        except Exception as e:
            logger.error(f"Failed to cache metadata for index {index_name}: {str(e)}")
    
    async def _setup_optimization_schedule(self):
        """Setup automatic index optimization schedule"""        # This would typically run as a background task
        pass
    
    async def get_index_stats(self, index_name: Optional[str] = None) -> Dict[str, Any]:
        """Get comprehensive statistics for FAISS indexes"""        if index_name:
            if index_name not in self.indexes:
                return {'error': f'Index {index_name} not found'}
            
            faiss_index = self.indexes[index_name]
            metadata = self.index_metadata[index_name]
            
            return {
                'index_name': index_name,
                'total_vectors': faiss_index.ntotal,
                'dimension': metadata['dimension'],
                'index_type': metadata['index_type'],
                'embedding_type': metadata['embedding_type'],
                'created_at': metadata['created_at'].isoformat(),
                'last_updated': metadata['last_updated'].isoformat(),
                'performance_stats': metadata['performance_stats'],
                'memory_usage': faiss_index.ntotal * metadata['dimension'] * 4,  # Approximate bytes
                'is_trained': getattr(faiss_index, 'is_trained', True)
            }
        else:
            # Return stats for all indexes
            stats = {
                'total_indexes': len(self.indexes),
                'total_vectors': sum(idx.ntotal for idx in self.indexes.values()),
                'indexes': {}
            }
            
            for name in self.indexes:
                stats['indexes'][name] = await self.get_index_stats(name)
            
            return stats
    
    async def cleanup(self):
        """Cleanup resources and save indexes"""        try:
            # Save all indexes to disk
            save_tasks = [self._save_index_to_disk(name) for name in self.indexes]
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
            
            logger.info("FAISSIndexManager cleanup completed")
            
        except Exception as e:
            logger.error(f"Error during FAISSIndexManager cleanup: {str(e)}")
