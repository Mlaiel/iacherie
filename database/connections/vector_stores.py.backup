"""Vector Store Connection Handler - IA Influencer Agent Platform

Manages vector database connections for content similarity and AI operations:
- Content fingerprint similarity search
- AI embedding storage and retrieval
- Collaborative filtering and recommendations
- Content matching and discovery
- User behavior pattern analysis
- Cross-platform content correlation

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.
"""
import asyncio
import logging
import numpy as np
from typing import Dict, Any, Optional, List, Tuple, Union
from dataclasses import dataclass
from datetime import datetime
import pickle
import json

import faiss
from pinecone import Pinecone, PodSpec
import hnswlib


@dataclass
class VectorStoreConfig:
    """Vector store connection configuration"""
    provider: str = "faiss"  # faiss, pinecone, hnswlib
    dimension: int = 512
    # FAISS specific
    faiss_index_type: str = "IndexFlatL2"  # IndexFlatL2, IndexIVFFlat, IndexHNSWFlat
    faiss_storage_path: str = "/tmp/faiss_indexes"
    # Pinecone specific
    pinecone_api_key: Optional[str] = None
    pinecone_environment: str = "us-west1-gcp"
    pinecone_index_name: str = "ia-influencer-content"
    pinecone_pod_type: str = "p1.x1"
    # HNSWLIB specific
    hnswlib_max_elements: int = 1000000
    hnswlib_ef_construction: int = 200
    hnswlib_m: int = 16
    hnswlib_storage_path: str = "/tmp/hnswlib_indexes"
    # General settings
    metric: str = "cosine"  # cosine, euclidean, manhattan
    batch_size: int = 1000
    tenant_isolation: bool = True


class VectorStoreConnectionHandler:
    """
    Vector store connection handler for IA Influencer platform.
    
    Manages vector databases for:
    - Content fingerprint similarity matching
    - AI-generated embedding storage
    - Collaborative recommendation systems
    - Content discovery and matching
    - User preference learning
    - Cross-platform content correlation
    """
    
    def __init__(self, config: Dict[str, Any]):
        self.config = VectorStoreConfig(**config)
        self.logger = logging.getLogger(__name__)
        
        # Vector store clients
        self.faiss_indexes: Dict[str, faiss.Index] = {}
        self.pinecone_client: Optional[Pinecone] = None
        self.hnswlib_indexes: Dict[str, hnswlib.Index] = {}
        
        # Tenant isolation
        self.tenant_indexes: Dict[str, Dict[str, Any]] = {}
        
        # Connection metrics
        self.connection_count = 0
        self.operation_count = 0
        self.error_count = 0
        self.last_health_check = None
        
        # Index metadata
        self.index_metadata: Dict[str, Dict[str, Any]] = {}
    
    async def initialize(self) -> None:
        """Initialize vector store connections"""
        try:
            self.logger.info(f"Initializing {self.config.provider} vector store...")
            
            if self.config.provider == "faiss":
                await self._initialize_faiss()
            elif self.config.provider == "pinecone":
                await self._initialize_pinecone()
            elif self.config.provider == "hnswlib":
                await self._initialize_hnswlib()
            else:
                raise ValueError(f"Unsupported vector store provider: {self.config.provider}")
            
            # Create default indexes
            await self._create_default_indexes()
            
            # Verify connection
            await self.health_check()
            
            self.logger.info(f"{self.config.provider} vector store initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize vector store: {e}")
            raise
    
    async def _initialize_faiss(self) -> None:
        """Initialize FAISS vector store"""
        import os
        os.makedirs(self.config.faiss_storage_path, exist_ok=True)
        self.logger.info("FAISS vector store initialized")
    
    async def _initialize_pinecone(self) -> None:
        """Initialize Pinecone vector store"""
        if not self.config.pinecone_api_key:
            raise ValueError("Pinecone API key required")
        
        self.pinecone_client = Pinecone(api_key=self.config.pinecone_api_key)
        self.logger.info("Pinecone vector store initialized")
    
    async def _initialize_hnswlib(self) -> None:
        """Initialize HNSWLIB vector store"""
        import os
        os.makedirs(self.config.hnswlib_storage_path, exist_ok=True)
        self.logger.info("HNSWLIB vector store initialized")
    
    async def _create_default_indexes(self) -> None:
        """Create default indexes for different content types"""
        default_indexes = [
            "content_fingerprints",
            "user_embeddings", 
            "content_embeddings",
            "collaboration_vectors",
            "recommendation_vectors"
        ]
        
        for index_name in default_indexes:
            await self.create_index(index_name, self.config.dimension)
    
    async def create_index(self, 
                         index_name: str, 
                         dimension: int,
                         tenant_id: Optional[str] = None) -> bool:
        """Create a new vector index"""
        try:
            full_index_name = self._get_full_index_name(index_name, tenant_id)
            
            if self.config.provider == "faiss":
                await self._create_faiss_index(full_index_name, dimension)
            elif self.config.provider == "pinecone":
                await self._create_pinecone_index(full_index_name, dimension)
            elif self.config.provider == "hnswlib":
                await self._create_hnswlib_index(full_index_name, dimension)
            
            # Store metadata
            self.index_metadata[full_index_name] = {
                "dimension": dimension,
                "created_at": datetime.utcnow().isoformat(),
                "count": 0,
                "tenant_id": tenant_id
            }
            
            self.logger.info(f"Created vector index: {full_index_name}")
            return True
            
        except Exception as e:
            self.error_count += 1
            self.logger.error(f"Failed to create index {index_name}: {e}")
            raise
    
    def _get_full_index_name(self, index_name: str, tenant_id: Optional[str] = None) -> str:
        """Get full index name with tenant prefix if applicable"""
        if tenant_id and self.config.tenant_isolation:
            return f"tenant_{tenant_id}_{index_name}"
        return index_name
    
    async def _create_faiss_index(self, index_name: str, dimension: int) -> None:
        """Create FAISS index"""
        if self.config.faiss_index_type == "IndexFlatL2":
            index = faiss.IndexFlatL2(dimension)
        elif self.config.faiss_index_type == "IndexIVFFlat":
            quantizer = faiss.IndexFlatL2(dimension)
            index = faiss.IndexIVFFlat(quantizer, dimension, 100)
        elif self.config.faiss_index_type == "IndexHNSWFlat":
            index = faiss.IndexHNSWFlat(dimension, 32)
        else:
            raise ValueError(f"Unsupported FAISS index type: {self.config.faiss_index_type}")
        
        self.faiss_indexes[index_name] = index
    
    async def _create_pinecone_index(self, index_name: str, dimension: int) -> None:
        """Create Pinecone index"""
        if not self.pinecone_client:
            raise RuntimeError("Pinecone client not initialized")
        
        # Check if index exists
        existing_indexes = self.pinecone_client.list_indexes()
        if index_name not in [idx['name'] for idx in existing_indexes]:
            self.pinecone_client.create_index(
                name=index_name,
                dimension=dimension,
                metric=self.config.metric,
                spec=PodSpec(
                    environment=self.config.pinecone_environment,
                    pod_type=self.config.pinecone_pod_type
                )
            )
    
    async def _create_hnswlib_index(self, index_name: str, dimension: int) -> None:
        """Create HNSWLIB index"""
        space = 'cosine' if self.config.metric == 'cosine' else 'l2'
        
        index = hnswlib.Index(space=space, dim=dimension)
        index.init_index(
            max_elements=self.config.hnswlib_max_elements,
            ef_construction=self.config.hnswlib_ef_construction,
            M=self.config.hnswlib_m
        )
        
        self.hnswlib_indexes[index_name] = index
    
    async def add_vectors(self, 
                         index_name: str, 
                         vectors: np.ndarray,
                         ids: Optional[List[str]] = None,
                         metadata: Optional[List[Dict[str, Any]]] = None,
                         tenant_id: Optional[str] = None) -> bool:
        """Add vectors to index"""
        try:
            full_index_name = self._get_full_index_name(index_name, tenant_id)
            
            if full_index_name not in self._get_available_indexes():
                await self.create_index(index_name, vectors.shape[1], tenant_id)
                full_index_name = self._get_full_index_name(index_name, tenant_id)
            
            if self.config.provider == "faiss":
                await self._add_vectors_faiss(full_index_name, vectors, ids)
            elif self.config.provider == "pinecone":
                await self._add_vectors_pinecone(full_index_name, vectors, ids, metadata)
            elif self.config.provider == "hnswlib":
                await self._add_vectors_hnswlib(full_index_name, vectors, ids)
            
            # Update metadata
            if full_index_name in self.index_metadata:
                self.index_metadata[full_index_name]["count"] += len(vectors)
            
            self.operation_count += 1
            return True
            
        except Exception as e:
            self.error_count += 1
            self.logger.error(f"Failed to add vectors to {index_name}: {e}")
            raise
    
    def _get_available_indexes(self) -> List[str]:
        """Get list of available indexes"""
        indexes = []
        if self.config.provider == "faiss":
            indexes.extend(self.faiss_indexes.keys())
        elif self.config.provider == "pinecone":
            if self.pinecone_client:
                indexes.extend([idx['name'] for idx in self.pinecone_client.list_indexes()])
        elif self.config.provider == "hnswlib":
            indexes.extend(self.hnswlib_indexes.keys())
        return indexes
    
    async def _add_vectors_faiss(self, 
                               index_name: str, 
                               vectors: np.ndarray, 
                               ids: Optional[List[str]]) -> None:
        """Add vectors to FAISS index"""
        if index_name not in self.faiss_indexes:
            raise ValueError(f"FAISS index {index_name} not found")
        
        index = self.faiss_indexes[index_name]
        
        # Train index if necessary
        if not index.is_trained:
            index.train(vectors.astype(np.float32))
        
        index.add(vectors.astype(np.float32))
        
        # Save index to disk
        await self._save_faiss_index(index_name, index)
    
    async def _add_vectors_pinecone(self, 
                                  index_name: str, 
                                  vectors: np.ndarray,
                                  ids: Optional[List[str]],
                                  metadata: Optional[List[Dict[str, Any]]]) -> None:
        """Add vectors to Pinecone index"""
        if not self.pinecone_client:
            raise RuntimeError("Pinecone client not initialized")
        
        index = self.pinecone_client.Index(index_name)
        
        # Prepare vectors for upsert
        vector_data = []
        for i, vector in enumerate(vectors):
            vector_id = ids[i] if ids else f"vec_{i}"
            vector_metadata = metadata[i] if metadata else {}
            vector_data.append({
                "id": vector_id,
                "values": vector.tolist(),
                "metadata": vector_metadata
            })
        
        # Batch upsert
        for i in range(0, len(vector_data), self.config.batch_size):
            batch = vector_data[i:i + self.config.batch_size]
            index.upsert(vectors=batch)
    
    async def _add_vectors_hnswlib(self, 
                                 index_name: str, 
                                 vectors: np.ndarray,
                                 ids: Optional[List[str]]) -> None:
        """Add vectors to HNSWLIB index"""
        if index_name not in self.hnswlib_indexes:
            raise ValueError(f"HNSWLIB index {index_name} not found")
        
        index = self.hnswlib_indexes[index_name]
        
        # Generate numeric IDs if string IDs provided
        if ids:
            numeric_ids = [hash(id_str) % (2**31) for id_str in ids]
        else:
            numeric_ids = list(range(index.get_current_count(), 
                                   index.get_current_count() + len(vectors)))
        
        index.add_items(vectors.astype(np.float32), numeric_ids)
        
        # Save index to disk
        await self._save_hnswlib_index(index_name, index)
    
    async def search_vectors(self, 
                           index_name: str, 
                           query_vector: np.ndarray,
                           k: int = 10,
                           tenant_id: Optional[str] = None) -> List[Tuple[str, float]]:
        """Search for similar vectors"""
        try:
            full_index_name = self._get_full_index_name(index_name, tenant_id)
            
            if self.config.provider == "faiss":
                results = await self._search_faiss(full_index_name, query_vector, k)
            elif self.config.provider == "pinecone":
                results = await self._search_pinecone(full_index_name, query_vector, k)
            elif self.config.provider == "hnswlib":
                results = await self._search_hnswlib(full_index_name, query_vector, k)
            else:
                raise ValueError(f"Unsupported provider: {self.config.provider}")
            
            self.operation_count += 1
            return results
            
        except Exception as e:
            self.error_count += 1
            self.logger.error(f"Vector search failed for {index_name}: {e}")
            raise
    
    async def _search_faiss(self, 
                          index_name: str, 
                          query_vector: np.ndarray, 
                          k: int) -> List[Tuple[str, float]]:
        """Search FAISS index"""
        if index_name not in self.faiss_indexes:
            raise ValueError(f"FAISS index {index_name} not found")
        
        index = self.faiss_indexes[index_name]
        
        # Ensure query vector is 2D
        if query_vector.ndim == 1:
            query_vector = query_vector.reshape(1, -1)
        
        distances, indices = index.search(query_vector.astype(np.float32), k)
        
        results = []
        for i, (distance, idx) in enumerate(zip(distances[0], indices[0])):
            if idx != -1:  # Valid result
                results.append((str(idx), float(distance)))
        
        return results
    
    async def _search_pinecone(self, 
                             index_name: str, 
                             query_vector: np.ndarray, 
                             k: int) -> List[Tuple[str, float]]:
        """Search Pinecone index"""
        if not self.pinecone_client:
            raise RuntimeError("Pinecone client not initialized")
        
        index = self.pinecone_client.Index(index_name)
        
        response = index.query(
            vector=query_vector.tolist(),
            top_k=k,
            include_metadata=True
        )
        
        results = []
        for match in response['matches']:
            results.append((match['id'], match['score']))
        
        return results
    
    async def _search_hnswlib(self, 
                            index_name: str, 
                            query_vector: np.ndarray, 
                            k: int) -> List[Tuple[str, float]]:
        """Search HNSWLIB index"""
        if index_name not in self.hnswlib_indexes:
            raise ValueError(f"HNSWLIB index {index_name} not found")
        
        index = self.hnswlib_indexes[index_name]
        
        labels, distances = index.knn_query(query_vector.astype(np.float32), k=k)
        
        results = []
        for label, distance in zip(labels[0], distances[0]):
            results.append((str(label), float(distance)))
        
        return results
    
    async def _save_faiss_index(self, index_name: str, index: faiss.Index) -> None:
        """Save FAISS index to disk"""
        import os
        file_path = os.path.join(self.config.faiss_storage_path, f"{index_name}.index")
        faiss.write_index(index, file_path)
    
    async def _save_hnswlib_index(self, index_name: str, index: hnswlib.Index) -> None:
        """Save HNSWLIB index to disk"""
        import os
        file_path = os.path.join(self.config.hnswlib_storage_path, f"{index_name}.bin")
        index.save_index(file_path)
    
    async def delete_vectors(self, 
                           index_name: str, 
                           vector_ids: List[str],
                           tenant_id: Optional[str] = None) -> bool:
        """Delete vectors from index"""
        try:
            full_index_name = self._get_full_index_name(index_name, tenant_id)
            
            if self.config.provider == "pinecone":
                await self._delete_vectors_pinecone(full_index_name, vector_ids)
            else:
                # FAISS and HNSWLIB don't support deletion, need recreation
                self.logger.warning(f"Vector deletion not supported for {self.config.provider}")
                return False
            
            self.operation_count += 1
            return True
            
        except Exception as e:
            self.error_count += 1
            self.logger.error(f"Failed to delete vectors from {index_name}: {e}")
            raise
    
    async def _delete_vectors_pinecone(self, index_name: str, vector_ids: List[str]) -> None:
        """Delete vectors from Pinecone index"""
        if not self.pinecone_client:
            raise RuntimeError("Pinecone client not initialized")
        
        index = self.pinecone_client.Index(index_name)
        index.delete(ids=vector_ids)
    
    async def get_connection(self) -> Dict[str, Any]:
        """Get vector store connection info"""
        self.connection_count += 1
        
        return {
            "provider": self.config.provider,
            "indexes": self._get_available_indexes(),
            "metadata": self.index_metadata
        }
    
    async def health_check(self) -> Dict[str, Any]:
        """Check vector store health"""
        try:
            start_time = datetime.utcnow()
            
            # Test basic operations based on provider
            test_vector = np.random.random((1, self.config.dimension)).astype(np.float32)
            
            if self.config.provider == "faiss" and self.faiss_indexes:
                # Test FAISS
                index_name = list(self.faiss_indexes.keys())[0]
                index = self.faiss_indexes[index_name]
                if index.ntotal > 0:
                    distances, indices = index.search(test_vector, 1)
            
            elif self.config.provider == "pinecone" and self.pinecone_client:
                # Test Pinecone
                indexes = self.pinecone_client.list_indexes()
                if indexes:
                    index = self.pinecone_client.Index(indexes[0]['name'])
                    index.query(vector=test_vector[0].tolist(), top_k=1)
            
            elif self.config.provider == "hnswlib" and self.hnswlib_indexes:
                # Test HNSWLIB
                index_name = list(self.hnswlib_indexes.keys())[0]
                index = self.hnswlib_indexes[index_name]
                if index.get_current_count() > 0:
                    labels, distances = index.knn_query(test_vector, k=1)
            
            response_time = (datetime.utcnow() - start_time).total_seconds()
            self.last_health_check = datetime.utcnow()
            
            return {
                "status": "healthy",
                "response_time": response_time,
                "provider": self.config.provider,
                "indexes": len(self._get_available_indexes()),
                "total_vectors": sum(meta.get("count", 0) for meta in self.index_metadata.values()),
                "metrics": {
                    "connection_count": self.connection_count,
                    "operation_count": self.operation_count,
                    "error_count": self.error_count
                },
                "last_check": self.last_health_check.isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Vector store health check failed: {e}")
            return {
                "status": "unhealthy",
                "error": str(e),
                "last_check": datetime.utcnow().isoformat()
            }
    
    async def get_metrics(self) -> Dict[str, Any]:
        """Get detailed vector store metrics"""
        try:
            metrics = {
                "provider": self.config.provider,
                "configuration": {
                    "dimension": self.config.dimension,
                    "metric": self.config.metric,
                    "batch_size": self.config.batch_size
                },
                "indexes": self.index_metadata,
                "performance": {
                    "connection_count": self.connection_count,
                    "operation_count": self.operation_count,
                    "error_count": self.error_count
                }
            }
            
            if self.config.provider == "faiss":
                metrics["faiss_indexes"] = len(self.faiss_indexes)
            elif self.config.provider == "pinecone" and self.pinecone_client:
                metrics["pinecone_indexes"] = len(self.pinecone_client.list_indexes())
            elif self.config.provider == "hnswlib":
                metrics["hnswlib_indexes"] = len(self.hnswlib_indexes)
            
            return metrics
            
        except Exception as e:
            self.logger.error(f"Failed to get vector store metrics: {e}")
            return {"error": str(e)}
    
    async def shutdown(self) -> None:
        """Shutdown vector store connections"""
        self.logger.info("Shutting down vector store connections...")
        
        # Save FAISS indexes
        for index_name, index in self.faiss_indexes.items():
            try:
                await self._save_faiss_index(index_name, index)
            except Exception as e:
                self.logger.error(f"Failed to save FAISS index {index_name}: {e}")
        
        # Save HNSWLIB indexes
        for index_name, index in self.hnswlib_indexes.items():
            try:
                await self._save_hnswlib_index(index_name, index)
            except Exception as e:
                self.logger.error(f"Failed to save HNSWLIB index {index_name}: {e}")
        
        # Clear indexes
        self.faiss_indexes.clear()
        self.hnswlib_indexes.clear()
        self.pinecone_client = None
        
        self.logger.info("Vector store connections shutdown completed")
