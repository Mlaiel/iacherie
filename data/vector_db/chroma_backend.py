"""ChromaDB Backend Implementation for Vector Database Management
============================================================

Persistent vector database backend using ChromaDB for long-term storage,
metadata management, and hybrid search capabilities.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: © 2025 Fahed Mlaiel - All Rights Reserved

ATTENTION: Ce code est protégé par les droits d'auteur.
Toute reproduction, distribution ou modification non autorisée est strictement interdite.
"""import asyncio
import logging
import numpy as np
import json
import uuid
from typing import Dict, List, Optional, Tuple, Any, Union
from datetime import datetime, timedelta
from pathlib import Path
import threading
from concurrent.futures import ThreadPoolExecutor

# ChromaDB imports
import chromadb
from chromadb.config import Settings
from chromadb.utils import embedding_functions
from chromadb.api.types import QueryResult, GetResult
import chromadb.errors

# Local imports
from . import VectorBackend, VectorSearchResult, VectorIndex

logger = logging.getLogger(__name__)


class ChromaCollectionManager:
    """    Advanced ChromaDB collection manager with optimized operations.
    
    Features:
    - Persistent storage
    - Metadata filtering
    - Batch operations
    - Index optimization
    """    
    def __init__(self, client, collection_name: str, dimension: int, 
                 metric: str = "cosine"):
        self.client = client
        self.collection_name = collection_name
        self.dimension = dimension
        self.metric = metric
        self.collection = None
        self.lock = threading.RLock()
        
        # Collection metadata
        self.metadata = {
            'dimension': dimension,
            'metric': metric,
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat()
        }
        
        self._create_or_get_collection()
    
    def _create_or_get_collection(self):
        """Create or get existing collection."""        try:
            with self.lock:
                # Try to get existing collection
                try:
                    self.collection = self.client.get_collection(
                        name=self.collection_name
                    )
                    logger.info(f"Retrieved existing ChromaDB collection: {self.collection_name}")
                    
                except chromadb.errors.InvalidCollectionException:
                    # Create new collection
                    self.collection = self.client.create_collection(
                        name=self.collection_name,
                        metadata=self.metadata
                    )
                    logger.info(f"Created new ChromaDB collection: {self.collection_name}")
                
        except Exception as e:
            logger.error(f"Failed to create/get collection {self.collection_name}: {str(e)}")
            raise
    
    def add_vectors(self, vectors: np.ndarray, ids: List[str],
                   metadata: List[Dict[str, Any]]) -> bool:
        """Add vectors to the collection."""        try:
            with self.lock:
                # Convert numpy arrays to lists
                embeddings = vectors.tolist()
                
                # Ensure metadata is serializable
                processed_metadata = []
                for meta in metadata:
                    processed_meta = {}
                    for key, value in meta.items():
                        if isinstance(value, (str, int, float, bool)):
                            processed_meta[key] = value
                        else:
                            processed_meta[key] = json.dumps(value)
                    processed_metadata.append(processed_meta)
                
                # Add to collection
                self.collection.add(
                    embeddings=embeddings,
                    ids=ids,
                    metadatas=processed_metadata
                )
                
                # Update collection metadata
                self.metadata['updated_at'] = datetime.now().isoformat()
                self.collection.modify(metadata=self.metadata)
                
                logger.info(f"Added {len(ids)} vectors to collection {self.collection_name}")
                return True
                
        except Exception as e:
            logger.error(f"Failed to add vectors to collection {self.collection_name}: {str(e)}")
            return False
    
    def search(self, query_vector: np.ndarray, k: int = 10,
              threshold: float = 0.8, where: Dict[str, Any] = None) -> List[VectorSearchResult]:
        """Search for similar vectors in the collection."""        try:
            with self.lock:
                # Convert to list
                query_embedding = query_vector.tolist()
                
                # Perform query
                results = self.collection.query(
                    query_embeddings=[query_embedding],
                    n_results=k,
                    where=where
                )
                
                search_results = []
                if results['ids'] and len(results['ids']) > 0:
                    for i, (content_id, distance, metadata) in enumerate(zip(
                        results['ids'][0],
                        results['distances'][0],
                        results['metadatas'][0] or [{}] * len(results['ids'][0])
                    )):
                        # Convert distance to similarity based on metric
                        if self.metric == "cosine":
                            # ChromaDB returns 1 - cosine_similarity as distance
                            similarity = 1.0 - distance
                        else:
                            # For euclidean, convert distance to similarity
                            similarity = 1.0 / (1.0 + distance)
                        
                        if similarity >= threshold:
                            # Deserialize complex metadata values
                            processed_metadata = {}
                            for key, value in metadata.items():
                                if isinstance(value, str) and value.startswith('{'):
                                    try:
                                        processed_metadata[key] = json.loads(value)
                                    except json.JSONDecodeError:
                                        processed_metadata[key] = value
                                else:
                                    processed_metadata[key] = value
                            
                            result = VectorSearchResult(
                                content_id=content_id,
                                similarity_score=similarity,
                                metadata=processed_metadata,
                                distance=distance
                            )
                            search_results.append(result)
                
                return search_results
                
        except Exception as e:
            logger.error(f"Failed to search collection {self.collection_name}: {str(e)}")
            return []
    
    def get_vectors(self, ids: List[str]) -> List[Dict[str, Any]]:
        """Get specific vectors by IDs."""        try:
            with self.lock:
                results = self.collection.get(
                    ids=ids,
                    include=['embeddings', 'metadatas']
                )
                
                vectors = []
                for i, content_id in enumerate(results['ids']):
                    vector_data = {
                        'id': content_id,
                        'embedding': np.array(results['embeddings'][i]) if results['embeddings'] else None,
                        'metadata': results['metadatas'][i] if results['metadatas'] else {}
                    }
                    vectors.append(vector_data)
                
                return vectors
                
        except Exception as e:
            logger.error(f"Failed to get vectors from collection {self.collection_name}: {str(e)}")
            return []
    
    def update_vectors(self, ids: List[str], vectors: np.ndarray = None,
                      metadata: List[Dict[str, Any]] = None) -> bool:
        """Update existing vectors."""        try:
            with self.lock:
                update_data = {'ids': ids}
                
                if vectors is not None:
                    update_data['embeddings'] = vectors.tolist()
                
                if metadata is not None:
                    # Process metadata
                    processed_metadata = []
                    for meta in metadata:
                        processed_meta = {}
                        for key, value in meta.items():
                            if isinstance(value, (str, int, float, bool)):
                                processed_meta[key] = value
                            else:
                                processed_meta[key] = json.dumps(value)
                        processed_metadata.append(processed_meta)
                    update_data['metadatas'] = processed_metadata
                
                self.collection.update(**update_data)
                
                # Update collection metadata
                self.metadata['updated_at'] = datetime.now().isoformat()
                self.collection.modify(metadata=self.metadata)
                
                logger.info(f"Updated {len(ids)} vectors in collection {self.collection_name}")
                return True
                
        except Exception as e:
            logger.error(f"Failed to update vectors in collection {self.collection_name}: {str(e)}")
            return False
    
    def delete_vectors(self, ids: List[str]) -> bool:
        """Delete vectors from the collection."""        try:
            with self.lock:
                self.collection.delete(ids=ids)
                
                # Update collection metadata
                self.metadata['updated_at'] = datetime.now().isoformat()
                self.collection.modify(metadata=self.metadata)
                
                logger.info(f"Deleted {len(ids)} vectors from collection {self.collection_name}")
                return True
                
        except Exception as e:
            logger.error(f"Failed to delete vectors from collection {self.collection_name}: {str(e)}")
            return False
    
    def get_stats(self) -> Dict[str, Any]:
        """Get collection statistics."""        try:
            with self.lock:
                count = self.collection.count()
                
                stats = {
                    'name': self.collection_name,
                    'dimension': self.dimension,
                    'metric': self.metric,
                    'vector_count': count,
                    'metadata': self.metadata
                }
                
                return stats
                
        except Exception as e:
            logger.error(f"Failed to get stats for collection {self.collection_name}: {str(e)}")
            return {}
    
    def clear_collection(self) -> bool:
        """Clear all vectors from the collection."""        try:
            with self.lock:
                # Get all IDs
                all_data = self.collection.get()
                if all_data['ids']:
                    self.collection.delete(ids=all_data['ids'])
                
                logger.info(f"Cleared all vectors from collection {self.collection_name}")
                return True
                
        except Exception as e:
            logger.error(f"Failed to clear collection {self.collection_name}: {str(e)}")
            return False


class ChromaBackend(VectorBackend):
    """    Enhanced ChromaDB backend with persistent storage and advanced features.
    
    Features:
    - Persistent storage with SQLite/DuckDB
    - Metadata filtering and search
    - Collection management
    - Batch operations
    - Backup and restore
    """    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.persist_directory = config.get('persist_directory', './data/chroma')
        self.collection_managers: Dict[str, ChromaCollectionManager] = {}
        self.executor = ThreadPoolExecutor(max_workers=4)
        
        # Create persist directory
        Path(self.persist_directory).mkdir(parents=True, exist_ok=True)
        
        # Initialize ChromaDB client with persistence
        self.client_settings = Settings(
            chroma_db_impl="duckdb+parquet",
            persist_directory=self.persist_directory,
            anonymized_telemetry=False
        )
        
        self.client = chromadb.Client(self.client_settings)
        
        logger.info(f"ChromaDB backend initialized with persist directory: {self.persist_directory}")
    
    async def create_index(self, name: str, dimension: int, metric: str = "cosine") -> bool:
        """Create a new ChromaDB collection."""        try:
            if name in self.collection_managers:
                logger.warning(f"Collection '{name}' already exists")
                return True
            
            # Create collection manager
            loop = asyncio.get_event_loop()
            manager = await loop.run_in_executor(
                self.executor, 
                ChromaCollectionManager,
                self.client, name, dimension, metric
            )
            
            self.collection_managers[name] = manager
            
            logger.info(f"Created ChromaDB collection '{name}' with dimension {dimension}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to create ChromaDB collection '{name}': {str(e)}")
            return False
    
    async def add_vectors(self, index_name: str, vectors: np.ndarray,
                         ids: List[str], metadata: List[Dict]) -> bool:
        """Add vectors to ChromaDB collection."""        try:
            if index_name not in self.collection_managers:
                raise ValueError(f"Collection '{index_name}' not found")
            
            manager = self.collection_managers[index_name]
            
            success = await asyncio.get_event_loop().run_in_executor(
                self.executor, manager.add_vectors, vectors, ids, metadata
            )
            
            return success
            
        except Exception as e:
            logger.error(f"Failed to add vectors to collection '{index_name}': {str(e)}")
            return False
    
    async def search(self, index_name: str, query_vector: np.ndarray,
                    k: int = 10, threshold: float = 0.8,
                    where: Dict[str, Any] = None) -> List[VectorSearchResult]:
        """Search for similar vectors in ChromaDB collection."""        try:
            if index_name not in self.collection_managers:
                raise ValueError(f"Collection '{index_name}' not found")
            
            manager = self.collection_managers[index_name]
            
            results = await asyncio.get_event_loop().run_in_executor(
                self.executor, manager.search, query_vector, k, threshold, where
            )
            
            return results
            
        except Exception as e:
            logger.error(f"Failed to search collection '{index_name}': {str(e)}")
            return []
    
    async def delete_vectors(self, index_name: str, ids: List[str]) -> bool:
        """Delete vectors from ChromaDB collection."""        try:
            if index_name not in self.collection_managers:
                raise ValueError(f"Collection '{index_name}' not found")
            
            manager = self.collection_managers[index_name]
            
            success = await asyncio.get_event_loop().run_in_executor(
                self.executor, manager.delete_vectors, ids
            )
            
            return success
            
        except Exception as e:
            logger.error(f"Failed to delete vectors from collection '{index_name}': {str(e)}")
            return False
    
    async def update_vectors(self, index_name: str, ids: List[str],
                           vectors: np.ndarray = None,
                           metadata: List[Dict[str, Any]] = None) -> bool:
        """Update existing vectors in ChromaDB collection."""        try:
            if index_name not in self.collection_managers:
                raise ValueError(f"Collection '{index_name}' not found")
            
            manager = self.collection_managers[index_name]
            
            success = await asyncio.get_event_loop().run_in_executor(
                self.executor, manager.update_vectors, ids, vectors, metadata
            )
            
            return success
            
        except Exception as e:
            logger.error(f"Failed to update vectors in collection '{index_name}': {str(e)}")
            return False
    
    async def get_vectors(self, index_name: str, ids: List[str]) -> List[Dict[str, Any]]:
        """Get specific vectors by IDs."""        try:
            if index_name not in self.collection_managers:
                raise ValueError(f"Collection '{index_name}' not found")
            
            manager = self.collection_managers[index_name]
            
            vectors = await asyncio.get_event_loop().run_in_executor(
                self.executor, manager.get_vectors, ids
            )
            
            return vectors
            
        except Exception as e:
            logger.error(f"Failed to get vectors from collection '{index_name}': {str(e)}")
            return []
    
    async def search_with_metadata(self, index_name: str, query_vector: np.ndarray,
                                 metadata_filter: Dict[str, Any],
                                 k: int = 10, threshold: float = 0.8) -> List[VectorSearchResult]:
        """Search with metadata filtering."""        try:
            return await self.search(
                index_name, query_vector, k, threshold, where=metadata_filter
            )
            
        except Exception as e:
            logger.error(f"Failed to search with metadata filter: {str(e)}")
            return []
    
    async def list_collections(self) -> List[str]:
        """List all available collections."""        try:
            collections = await asyncio.get_event_loop().run_in_executor(
                self.executor, self.client.list_collections
            )
            
            return [col.name for col in collections]
            
        except Exception as e:
            logger.error(f"Failed to list collections: {str(e)}")
            return []
    
    async def delete_collection(self, index_name: str) -> bool:
        """Delete an entire collection."""        try:
            if index_name in self.collection_managers:
                del self.collection_managers[index_name]
            
            await asyncio.get_event_loop().run_in_executor(
                self.executor, self.client.delete_collection, index_name
            )
            
            logger.info(f"Deleted ChromaDB collection '{index_name}'")
            return True
            
        except Exception as e:
            logger.error(f"Failed to delete collection '{index_name}': {str(e)}")
            return False
    
    def get_collection_stats(self, index_name: str) -> Dict[str, Any]:
        """Get statistics for a specific collection."""        try:
            if index_name not in self.collection_managers:
                return {}
            
            manager = self.collection_managers[index_name]
            return manager.get_stats()
            
        except Exception as e:
            logger.error(f"Failed to get stats for collection '{index_name}': {str(e)}")
            return {}
    
    def get_system_stats(self) -> Dict[str, Any]:
        """Get system-wide statistics."""        try:
            stats = {
                'backend': 'chromadb',
                'total_collections': len(self.collection_managers),
                'persist_directory': self.persist_directory,
                'collections': {name: manager.get_stats() 
                              for name, manager in self.collection_managers.items()}
            }
            
            return stats
            
        except Exception as e:
            logger.error(f"Failed to get system stats: {str(e)}")
            return {}
    
    async def persist_data(self) -> bool:
        """Explicitly persist data to disk."""        try:
            await asyncio.get_event_loop().run_in_executor(
                self.executor, self.client.persist
            )
            
            logger.info("ChromaDB data persisted to disk")
            return True
            
        except Exception as e:
            logger.error(f"Failed to persist data: {str(e)}")
            return False
    
    async def backup_collection(self, index_name: str, backup_path: str) -> bool:
        """Create a backup of a collection."""        try:
            if index_name not in self.collection_managers:
                raise ValueError(f"Collection '{index_name}' not found")
            
            # For ChromaDB, backup involves copying the persist directory
            # This is a simplified implementation
            import shutil
            
            source_path = self.persist_directory
            backup_full_path = Path(backup_path) / f"chroma_backup_{index_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            await asyncio.get_event_loop().run_in_executor(
                self.executor, shutil.copytree, source_path, backup_full_path
            )
            
            logger.info(f"Created backup of collection '{index_name}' at {backup_full_path}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to backup collection '{index_name}': {str(e)}")
            return False
    
    async def restore_collection(self, backup_path: str) -> bool:
        """Restore a collection from backup."""        try:
            # This would restore from a backup directory
            # Implementation depends on specific backup format
            logger.info(f"Restore functionality not fully implemented for path: {backup_path}")
            return False
            
        except Exception as e:
            logger.error(f"Failed to restore from backup: {str(e)}")
            return False
    
    def __del__(self):
        """Cleanup when backend is destroyed."""        try:
            if hasattr(self, 'client'):
                self.client.persist()
        except:
            pass


# Export the backend
__all__ = ['ChromaBackend', 'ChromaCollectionManager']
