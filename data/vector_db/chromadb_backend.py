"""
ChromaDB Backend - Modern Vector Database Integration
====================================================

Enterprise-grade ChromaDB backend implementation with native embedding
functions, advanced metadata filtering, and distributed deployment support.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: © 2025 Fahed Mlaiel. All rights reserved.

⚠️ CRITICAL COPYRIGHT WARNING ⚠️
This code is the intellectual property of Fahed Mlaiel and is protected by 
international copyright law. Any unauthorized use, reproduction, distribution 
or modification is strictly prohibited and will result in legal action.

For licensing inquiries: mlaiel@live.de
"""

import asyncio
import logging
import numpy as np
import json
import uuid
from typing import Any, Dict, List, Optional, Tuple, Union
from datetime import datetime
from pathlib import Path
import aiofiles

# ChromaDB imports with fallback handling
try:
    import chromadb
    from chromadb.config import Settings
    from chromadb.utils import embedding_functions
    CHROMADB_AVAILABLE = True
except ImportError:
    CHROMADB_AVAILABLE = False
    chromadb = None

from .vector_storage import BaseVectorBackend, VectorMetadata, SearchResult

logger = logging.getLogger(__name__)


class ChromaDBEmbeddingFunction:
    """Custom embedding function wrapper for ChromaDB."""
    
    def __init__(self, external_embedding_func -> None: Optional[callable] = None) -> None:
        """
        Initialize embedding function.
        
        Args:
            external_embedding_func: External embedding function to use
        """
        self.external_func = external_embedding_func
    
    def __call__(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for texts.
        
        Args:
            texts: List of text strings
        
        Returns:
            List of embedding vectors
        """
        if self.external_func:
            return [self.external_func(text).tolist() for text in texts]
        else:
            # Default: return zero vectors (should be replaced with actual embeddings)
            return [[0.0] * 768 for _ in texts]


class ChromaDBCollectionManager:
    """Manages ChromaDB collections and their configurations."""
    
    def __init__(self, client -> None: Any, collection_name -> None: str = "ainflue_vectors") -> None:
        """
        Initialize collection manager.
        
        Args:
            client: ChromaDB client instance
            collection_name: Name of the collection
        """
        self.client = client
        self.collection_name = collection_name
        self.collection: Optional[Any] = None
        
    async def initialize_collection(
        self,
        embedding_function: Optional[Any] = None,
        metadata_config: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Initialize or get existing collection.
        
        Args:
            embedding_function: Embedding function to use
            metadata_config: Metadata configuration
        
        Returns:
            True if successful
        """
        try:
            # Set default embedding function if none provided
            if embedding_function is None:
                embedding_function = embedding_functions.DefaultEmbeddingFunction()
            
            # Try to get existing collection first
            try:
                self.collection = self.client.get_collection(
                    name=self.collection_name,
                    embedding_function=embedding_function
                )
                logger.info(f"Retrieved existing ChromaDB collection: {self.collection_name}")
            except Exception:
                # Create new collection if it doesn't exist
                self.collection = self.client.create_collection(
                    name=self.collection_name,
                    embedding_function=embedding_function,
                    metadata=metadata_config or {}
                )
                logger.info(f"Created new ChromaDB collection: {self.collection_name}")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize ChromaDB collection: {e}")
            return False
    
    async def delete_collection(self) -> bool:
        """Delete the collection."""
        try:
            if self.collection:
                self.client.delete_collection(name=self.collection_name)
                self.collection = None
                logger.info(f"Deleted ChromaDB collection: {self.collection_name}")
                return True
            return False
            
        except Exception as e:
            logger.error(f"Failed to delete collection: {e}")
            return False
    
    def get_collection_info(self) -> Dict[str, Any]:
        """Get collection information."""
        if not self.collection:
            return {}
        
        try:
            count = self.collection.count()
            return {
                'name': self.collection_name,
                'count': count,
                'metadata': getattr(self.collection, 'metadata', {})
            }
        except Exception as e:
            logger.error(f"Failed to get collection info: {e}")
            return {}


class ChromaDBBackend(BaseVectorBackend):
    """
    Enterprise ChromaDB backend implementation.
    
    Features:
    - Native embedding functions support
    - Advanced metadata filtering
    - Collections management
    - Persistence configuration
    - Distributed deployment support
    - Custom embedding functions
    - Real-time updates optimization
    - Batch operations
    - Query optimization
    """
    
    def __init__(self, config -> None: Any, security_manager -> None: Optional[Any] = None) -> None:
        """Initialize ChromaDB backend."""
        super().__init__(config, security_manager)
        
        # Configuration
        self.host = config.get('backend.host', 'localhost')
        self.port = config.get('backend.port', 8000)
        self.persist_directory = config.get('backend.persist_directory', 'data/chromadb')
        self.collection_name = config.get('backend.collection_name', 'ainflue_vectors')
        self.distance_metric = config.get('backend.distance_metric', 'cosine')
        self.batch_size = config.get('backend.batch_size', 1000)
        self.enable_persistence = config.get('backend.enable_persistence', True)
        
        # Core components
        self.client: Optional[Any] = None
        self.collection_manager: Optional[ChromaDBCollectionManager] = None
        self.embedding_function: Optional[Any] = None
        
        # Statistics
        self.stats = {
            'total_searches': 0,
            'total_adds': 0,
            'total_updates': 0,
            'total_deletes': 0,
            'total_vectors': 0,
            'collection_count': 0
        }
        
        logger.info(f"ChromaDBBackend initialized with collection: {self.collection_name}")
    
    async def initialize(self) -> bool:
        """Initialize the ChromaDB backend."""
        try:
            if not CHROMADB_AVAILABLE:
                raise RuntimeError("ChromaDB not available. Install with: pip install chromadb")
            
            # Configure ChromaDB settings
            settings = {}
            
            if self.enable_persistence:
                # Persistent mode
                persist_path = Path(self.persist_directory)
                persist_path.mkdir(parents=True, exist_ok=True)
                
                settings = Settings(
                    chroma_db_impl="duckdb+parquet",
                    persist_directory=str(persist_path),
                    anonymized_telemetry=False
                )
                
                self.client = chromadb.Client(settings)
                logger.info(f"ChromaDB client initialized in persistent mode: {persist_path}")
                
            else:
                # In-memory mode
                settings = Settings(
                    chroma_db_impl="duckdb",
                    anonymized_telemetry=False
                )
                
                self.client = chromadb.Client(settings)
                logger.info("ChromaDB client initialized in memory mode")
            
            # Initialize collection manager
            self.collection_manager = ChromaDBCollectionManager(
                client=self.client,
                collection_name=self.collection_name
            )
            
            # Set up embedding function
            self.embedding_function = self._create_embedding_function()
            
            # Initialize collection
            success = await self.collection_manager.initialize_collection(
                embedding_function=self.embedding_function,
                metadata_config={
                    'distance_metric': self.distance_metric,
                    'created_at': datetime.utcnow().isoformat()
                }
            )
            
            if not success:
                return False
            
            # Update statistics
            await self._update_statistics()
            
            self.initialized = True
            logger.info("ChromaDB backend initialization completed")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize ChromaDB backend: {e}")
            return False
    
    def _create_embedding_function(self) -> Any:
        """Create appropriate embedding function."""
        try:
            # Try to use sentence transformers if available
            try:
                return embedding_functions.SentenceTransformerEmbeddingFunction(
                    model_name="all-MiniLM-L6-v2"
                )
            except Exception:
                # Fallback to default embedding function
                return embedding_functions.DefaultEmbeddingFunction()
                
        except Exception as e:
            logger.warning(f"Failed to create embedding function: {e}")
            return None
    
    async def add_vector(
        self,
        vector_id: str,
        vector: np.ndarray,
        metadata: Optional[VectorMetadata] = None
    ) -> bool:
        """Add a vector to ChromaDB."""
        try:
            if not self.initialized or not self.collection_manager or not self.collection_manager.collection:
                return False
            
            # Prepare metadata
            chroma_metadata = {}
            if metadata:
                chroma_metadata = {
                    'content_type': metadata.content_type,
                    'content_hash': metadata.content_hash,
                    'created_at': metadata.created_at.isoformat(),
                    'version': metadata.version
                }
                
                if metadata.custom_metadata:
                    # Flatten custom metadata with prefix
                    for key, value in metadata.custom_metadata.items():
                        chroma_metadata[f'custom_{key}'] = str(value)
                
                if metadata.encryption_key_id:
                    chroma_metadata['encryption_key_id'] = metadata.encryption_key_id
                
                if metadata.compression_type:
                    chroma_metadata['compression_type'] = metadata.compression_type
            
            # Convert vector to list
            if vector.ndim > 1:
                vector = vector.flatten()
            vector_list = vector.tolist()
            
            # Add to collection
            self.collection_manager.collection.add(
                ids=[vector_id],
                embeddings=[vector_list],
                metadatas=[chroma_metadata],
                documents=[f"vector_{vector_id}"]  # ChromaDB requires documents
            )
            
            self.stats['total_adds'] += 1
            self.stats['total_vectors'] += 1
            
            logger.debug(f"Added vector to ChromaDB: {vector_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to add vector {vector_id} to ChromaDB: {e}")
            return False
    
    async def add_vectors_batch(
        self,
        vectors: List[Tuple[str, np.ndarray, Optional[VectorMetadata]]]
    ) -> List[bool]:
        """Add multiple vectors in a batch."""
        try:
            if not self.initialized or not self.collection_manager or not self.collection_manager.collection:
                return [False] * len(vectors)
            
            # Prepare batch data
            ids = []
            embeddings = []
            metadatas = []
            documents = []
            
            for vector_id, vector, metadata in vectors:
                try:
                    # Prepare metadata
                    chroma_metadata = {}
                    if metadata:
                        chroma_metadata = {
                            'content_type': metadata.content_type,
                            'content_hash': metadata.content_hash,
                            'created_at': metadata.created_at.isoformat(),
                            'version': metadata.version
                        }
                        
                        if metadata.custom_metadata:
                            for key, value in metadata.custom_metadata.items():
                                chroma_metadata[f'custom_{key}'] = str(value)
                    
                    # Convert vector
                    if vector.ndim > 1:
                        vector = vector.flatten()
                    
                    ids.append(vector_id)
                    embeddings.append(vector.tolist())
                    metadatas.append(chroma_metadata)
                    documents.append(f"vector_{vector_id}")
                    
                except Exception as e:
                    logger.error(f"Failed to prepare vector {vector_id}: {e}")
                    continue
            
            if not ids:
                return [False] * len(vectors)
            
            # Add batch to collection
            self.collection_manager.collection.add(
                ids=ids,
                embeddings=embeddings,
                metadatas=metadatas,
                documents=documents
            )
            
            # Update statistics
            successful_adds = len(ids)
            self.stats['total_adds'] += successful_adds
            self.stats['total_vectors'] += successful_adds
            
            # Return results (all successful for batch operation)
            results = [True if vector_ids[i] in ids else False 
                      for i, (vector_ids, _, _) in enumerate([(vid, v, m) for vid, v, m in vectors])]
            
            logger.info(f"Added {successful_adds} vectors to ChromaDB in batch")
            return results
            
        except Exception as e:
            logger.error(f"Failed to add vectors batch to ChromaDB: {e}")
            return [False] * len(vectors)
    
    async def search_similar(
        self,
        query_vector: np.ndarray,
        top_k: int = 10,
        threshold: float = 0.0,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[SearchResult]:
        """Search for similar vectors."""
        try:
            if not self.initialized or not self.collection_manager or not self.collection_manager.collection:
                return []
            
            # Prepare query vector
            if query_vector.ndim > 1:
                query_vector = query_vector.flatten()
            query_list = query_vector.tolist()
            
            # Prepare metadata filters for ChromaDB
            where_clause = {}
            if filters:
                for key, value in filters.items():
                    if key == 'content_type':
                        where_clause['content_type'] = value
                    elif key == 'created_after':
                        # ChromaDB uses different filter syntax
                        where_clause['created_at'] = {"$gt": value}
                    elif key == 'created_before':
                        where_clause['created_at'] = {"$lt": value}
                    elif key.startswith('custom.'):
                        custom_key = f"custom_{key[7:]}"
                        where_clause[custom_key] = str(value)
            
            # Perform search
            search_params = {
                'query_embeddings': [query_list],
                'n_results': top_k
            }
            
            if where_clause:
                search_params['where'] = where_clause
            
            results = self.collection_manager.collection.query(**search_params)
            
            # Process results
            search_results = []
            
            if results and 'ids' in results and results['ids']:
                ids = results['ids'][0]
                distances = results.get('distances', [[]])[0]
                metadatas = results.get('metadatas', [[]])[0]
                
                for i, (vector_id, distance) in enumerate(zip(ids, distances)):
                    # Convert distance to similarity score
                    if self.distance_metric == 'cosine':
                        # ChromaDB returns cosine distance (0 = identical, 2 = opposite)
                        similarity_score = 1.0 - (distance / 2.0)
                    elif self.distance_metric == 'euclidean':
                        # Convert euclidean distance to similarity
                        similarity_score = 1.0 / (1.0 + distance)
                    else:
                        # Default scoring
                        similarity_score = 1.0 - distance
                    
                    # Apply threshold
                    if similarity_score < threshold:
                        continue
                    
                    # Create metadata object
                    metadata = None
                    if i < len(metadatas) and metadatas[i]:
                        chroma_meta = metadatas[i]
                        
                        # Extract custom metadata
                        custom_metadata = {}
                        for key, value in chroma_meta.items():
                            if key.startswith('custom_'):
                                custom_metadata[key[7:]] = value
                        
                        metadata = VectorMetadata(
                            id=vector_id,
                            content_type=chroma_meta.get('content_type', 'unknown'),
                            content_hash=chroma_meta.get('content_hash', ''),
                            created_at=datetime.fromisoformat(chroma_meta.get('created_at', datetime.utcnow().isoformat())),
                            custom_metadata=custom_metadata if custom_metadata else None,
                            encryption_key_id=chroma_meta.get('encryption_key_id'),
                            compression_type=chroma_meta.get('compression_type'),
                            version=int(chroma_meta.get('version', 1))
                        )
                    
                    search_results.append(SearchResult(
                        id=vector_id,
                        score=similarity_score,
                        metadata=metadata
                    ))
            
            self.stats['total_searches'] += 1
            
            logger.debug(f"ChromaDB search found {len(search_results)} results")
            return search_results
            
        except Exception as e:
            logger.error(f"Failed to search similar vectors in ChromaDB: {e}")
            return []
    
    async def get_vector(self, vector_id: str) -> Optional[Tuple[np.ndarray, VectorMetadata]]:
        """Get a specific vector by ID."""
        try:
            if not self.initialized or not self.collection_manager or not self.collection_manager.collection:
                return None
            
            # Get vector from collection
            results = self.collection_manager.collection.get(
                ids=[vector_id],
                include=['embeddings', 'metadatas']
            )
            
            if not results or not results.get('ids') or vector_id not in results['ids']:
                return None
            
            # Extract vector and metadata
            idx = results['ids'].index(vector_id)
            
            # Get embedding
            if 'embeddings' in results and results['embeddings'] and idx < len(results['embeddings']):
                vector = np.array(results['embeddings'][idx], dtype=np.float32)
            else:
                return None
            
            # Get metadata
            metadata = None
            if 'metadatas' in results and results['metadatas'] and idx < len(results['metadatas']):
                chroma_meta = results['metadatas'][idx]
                
                if chroma_meta:
                    # Extract custom metadata
                    custom_metadata = {}
                    for key, value in chroma_meta.items():
                        if key.startswith('custom_'):
                            custom_metadata[key[7:]] = value
                    
                    metadata = VectorMetadata(
                        id=vector_id,
                        content_type=chroma_meta.get('content_type', 'unknown'),
                        content_hash=chroma_meta.get('content_hash', ''),
                        created_at=datetime.fromisoformat(chroma_meta.get('created_at', datetime.utcnow().isoformat())),
                        custom_metadata=custom_metadata if custom_metadata else None,
                        encryption_key_id=chroma_meta.get('encryption_key_id'),
                        compression_type=chroma_meta.get('compression_type'),
                        version=int(chroma_meta.get('version', 1))
                    )
            
            if metadata is None:
                # Create minimal metadata
                metadata = VectorMetadata(
                    id=vector_id,
                    content_type="unknown",
                    content_hash="",
                    created_at=datetime.utcnow()
                )
            
            return vector, metadata
            
        except Exception as e:
            logger.error(f"Failed to get vector {vector_id} from ChromaDB: {e}")
            return None
    
    async def delete_vector(self, vector_id: str) -> bool:
        """Delete a vector by ID."""
        try:
            if not self.initialized or not self.collection_manager or not self.collection_manager.collection:
                return False
            
            # Delete from collection
            self.collection_manager.collection.delete(ids=[vector_id])
            
            self.stats['total_deletes'] += 1
            self.stats['total_vectors'] = max(0, self.stats['total_vectors'] - 1)
            
            logger.debug(f"Deleted vector from ChromaDB: {vector_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to delete vector {vector_id} from ChromaDB: {e}")
            return False
    
    async def update_vector(
        self,
        vector_id: str,
        vector: Optional[np.ndarray] = None,
        metadata: Optional[VectorMetadata] = None
    ) -> bool:
        """Update a vector."""
        try:
            if not self.initialized or not self.collection_manager or not self.collection_manager.collection:
                return False
            
            # ChromaDB doesn't have direct update, so we delete and re-add
            # First check if vector exists
            existing = await self.get_vector(vector_id)
            if not existing:
                return False
            
            existing_vector, existing_metadata = existing
            
            # Use new vector or keep existing
            update_vector = vector if vector is not None else existing_vector
            
            # Merge metadata
            if metadata:
                metadata.updated_at = datetime.utcnow()
                update_metadata = metadata
            else:
                update_metadata = existing_metadata
                update_metadata.updated_at = datetime.utcnow()
            
            # Delete existing
            delete_success = await self.delete_vector(vector_id)
            if not delete_success:
                return False
            
            # Add updated version
            add_success = await self.add_vector(vector_id, update_vector, update_metadata)
            
            if add_success:
                self.stats['total_updates'] += 1
            
            return add_success
            
        except Exception as e:
            logger.error(f"Failed to update vector {vector_id} in ChromaDB: {e}")
            return False
    
    async def _update_statistics(self) -> None:
        """Update internal statistics."""
        try:
            if self.collection_manager and self.collection_manager.collection:
                count = self.collection_manager.collection.count()
                self.stats['total_vectors'] = count
                self.stats['collection_count'] = count
        except Exception as e:
            logger.error(f"Failed to update statistics: {e}")
    
    async def get_statistics(self) -> Dict[str, Any]:
        """Get backend statistics."""
        await self._update_statistics()
        
        stats = self.stats.copy()
        stats.update({
            'backend_type': 'chromadb',
            'collection_name': self.collection_name,
            'distance_metric': self.distance_metric,
            'persist_directory': self.persist_directory,
            'enable_persistence': self.enable_persistence
        })
        
        # Add collection info
        if self.collection_manager:
            collection_info = self.collection_manager.get_collection_info()
            stats.update(collection_info)
        
        return stats
    
    async def health_check(self) -> bool:
        """Perform health check."""
        try:
            if not self.initialized or not self.collection_manager or not self.collection_manager.collection:
                return False
            
            # Test basic operations
            try:
                # Try to get collection count
                count = self.collection_manager.collection.count()
                
                # Test search with dummy vector if collection has data
                if count > 0:
                    dummy_vector = np.random.random(768).astype(np.float32)
                    results = self.collection_manager.collection.query(
                        query_embeddings=[dummy_vector.tolist()],
                        n_results=1
                    )
                    if results is None:
                        return False
                
                return True
                
            except Exception as e:
                logger.error(f"ChromaDB health check operation failed: {e}")
                return False
            
        except Exception as e:
            logger.error(f"ChromaDB health check failed: {e}")
            return False
    
    async def reset_collection(self) -> bool:
        """Reset (delete and recreate) the collection."""
        try:
            if not self.initialized or not self.collection_manager:
                return False
            
            # Delete existing collection
            await self.collection_manager.delete_collection()
            
            # Recreate collection
            success = await self.collection_manager.initialize_collection(
                embedding_function=self.embedding_function
            )
            
            if success:
                # Reset statistics
                self.stats['total_vectors'] = 0
                self.stats['collection_count'] = 0
                logger.info("ChromaDB collection reset successfully")
            
            return success
            
        except Exception as e:
            logger.error(f"Failed to reset ChromaDB collection: {e}")
            return False
    
    async def shutdown(self) -> None:
        """Shutdown the ChromaDB backend."""
        logger.info("Shutting down ChromaDB backend...")
        
        try:
            # ChromaDB client doesn't require explicit shutdown
            # but we can clear references
            self.collection_manager = None
            self.client = None
            self.embedding_function = None
            
            self.initialized = False
            logger.info("ChromaDB backend shutdown completed")
            
        except Exception as e:
            logger.error(f"Error during ChromaDB shutdown: {e}")


# Export main class
__all__ = [
    'ChromaDBBackend',
    'ChromaDBCollectionManager',
    'ChromaDBEmbeddingFunction'
]