"""Pinecone Vector Store Implementation

This module provides Pinecone-based vector storage for cloud-native vector search.
Optimized for high-scale similarity search with managed infrastructure.

Author: Fahed Mlaiel <mlaiel@live.de>
Project: IA Influencer Agent + Content Protection Platform
Copyright: All rights reserved. Unauthorized use, modification, or distribution prohibited.

WARNING: This code is proprietary to Fahed Mlaiel. Any unauthorized copying, modification, 
or distribution without explicit written permission is strictly prohibited and will result 
in legal action under German and international copyright law.
"""

import os
import json
import logging
import asyncio
from typing import Dict, List, Optional, Tuple, Any, Union
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
import numpy as np
import pinecone
from pinecone import Pinecone, ServerlessSpec, PodSpec
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from backend.core.config import get_settings
from backend.core.database import get_db_session
from backend.models.content_fingerprints import ContentFingerprint
from backend.utils.exceptions import VectorStoreError, SearchError
from backend.utils.performance import measure_execution_time

logger = logging.getLogger(__name__)
settings = get_settings()


@dataclass
class PineconeSearchResult:
    """
Pinecone search result with metadata"""
    content_id: str
    fingerprint_id: int
    similarity_score: float
    content_type: str
    metadata: Dict[str, Any]
    namespace: str


@dataclass
class PineconeIndexStats:
    """
Pinecone index statistics"""
    total_vectors: int
    dimension: int
    index_fullness: float
    namespaces: Dict[str, int]
    total_requests: int
    avg_latency_ms: float


class PineconeVectorStore:
    """
    Pinecone-based vector store for cloud-native vector search.
    
    Features:
    - Managed vector database with auto-scaling
    - High-performance similarity search
    - Namespace-based organization
    - Real-time updates and queries
    - Built-in metadata filtering
    - Global deployment options
    """
    
    def __init__(
        self,
        api_key: str = None,
        environment: str = None,
        index_name: str = "content-vectors",
        dimension: int = 512,
        metric: str = "cosine",
        cloud: str = "aws",
        region: str = "us-east-1"
    ):
        """
        Initialize Pinecone vector store
        
        Args:
            api_key: Pinecone API key
            environment: Pinecone environment
            index_name: Name of the Pinecone index
            dimension: Vector dimension
            metric: Distance metric (cosine, euclidean, dotproduct)
            cloud: Cloud provider (aws, gcp, azure)
            region: Cloud region
        """
        self.api_key = api_key or settings.PINECONE_API_KEY
        self.environment = environment or settings.PINECONE_ENVIRONMENT
        self.index_name = index_name
        self.dimension = dimension
        self.metric = metric
        self.cloud = cloud
        self.region = region
        
        if not self.api_key:
            raise VectorStoreError("Pinecone API key is required")
        
        # Initialize Pinecone client
        self.pc = Pinecone(api_key=self.api_key)
        self.index = None
        
        # Namespace mappings for different content types
        self.namespaces = {
            "audio": "audio-content",
            "video": "video-content", 
            "image": "image-content",
            "text": "text-content"
        }
        
        # Performance metrics
        self.search_stats = {
            "total_searches": 0,
            "avg_response_time": 0.0,
            "cache_hits": 0,
            "cache_misses": 0,
            "errors": 0
        }
        
        logger.info(
            f"Initialized Pinecone vector store - Index: {index_name}, "
            f"Dimension: {dimension}, Metric: {metric}"
        )
    
    async def initialize(self) -> None:
        """Initialize Pinecone index"""
        try:
            # Check if index exists
            existing_indexes = self.pc.list_indexes()
            index_names = [idx.name for idx in existing_indexes.indexes]
            
            if self.index_name not in index_names:
                # Create index
                await self._create_index()
            
            # Connect to index
            self.index = self.pc.Index(self.index_name)
            
            # Verify index configuration
            stats = self.index.describe_index_stats()
            logger.info(
                f"Connected to Pinecone index '{self.index_name}' - "
                f"Dimension: {stats.dimension}, Total vectors: {stats.total_vector_count}"
            )
            
        except Exception as e:
            logger.error(f"Failed to initialize Pinecone index: {str(e)}")
            raise VectorStoreError(f"Pinecone initialization failed: {str(e)}")
    
    @measure_execution_time
    async def upsert_vectors(
        self,
        content_type: str,
        vectors: List[Tuple[str, np.ndarray, Dict[str, Any]]]
    ) -> Dict[str, int]:
        """
        Upsert vectors to Pinecone index
        
        Args:
            content_type: Content type
            vectors: List of (id, vector, metadata) tuples
            
        Returns:
            Upsert statistics
        """
        try:
            if not self.index:
                await self.initialize()
            
            namespace = self.namespaces.get(content_type, content_type)
            
            # Prepare vectors for upsert
            vectors_to_upsert = []
            for content_id, vector, metadata in vectors:
                # Validate vector dimension
                if len(vector) != self.dimension:
                    raise VectorStoreError(
                        f"Vector dimension mismatch: expected {self.dimension}, "
                        f"got {len(vector)}"
                    )
                
                # Prepare metadata
                full_metadata = {
                    "content_id": content_id,
                    "content_type": content_type,
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    **metadata
                }
                
                # Convert numpy array to list
                vector_list = vector.tolist() if isinstance(vector, np.ndarray) else vector
                
                vectors_to_upsert.append((content_id, vector_list, full_metadata))
            
            # Batch upsert (Pinecone recommends batches of 100-1000)
            batch_size = 100
            upserted_count = 0
            
            for i in range(0, len(vectors_to_upsert), batch_size):
                batch = vectors_to_upsert[i:i + batch_size]
                
                response = self.index.upsert(
                    vectors=batch,
                    namespace=namespace
                )
                
                upserted_count += response.upserted_count
                
                logger.debug(
                    f"Upserted batch {i//batch_size + 1}: "
                    f"{response.upserted_count} vectors"
                )
            
            logger.info(
                f"Successfully upserted {upserted_count} vectors "
                f"to {content_type} namespace"
            )
            
            return {
                "total": len(vectors),
                "upserted": upserted_count,
                "namespace": namespace
            }
            
        except Exception as e:
            logger.error(f"Failed to upsert vectors for {content_type}: {str(e)}")
            raise VectorStoreError(f"Vector upsert failed: {str(e)}")
    
    @measure_execution_time
    async def search_similar(
        self,
        content_type: str,
        query_vector: np.ndarray,
        k: int = 10,
        similarity_threshold: float = 0.8,
        metadata_filter: Dict[str, Any] = None,
        include_metadata: bool = True
    ) -> List[PineconeSearchResult]:
        """
        Search for similar vectors in Pinecone
        
        Args:
            content_type: Content type to search
            query_vector: Query vector
            k: Number of results
            similarity_threshold: Minimum similarity score
            metadata_filter: Metadata-based filtering
            include_metadata: Include metadata in results
            
        Returns:
            List of search results
        """
        try:
            self.search_stats["total_searches"] += 1
            start_time = datetime.now()
            
            if not self.index:
                await self.initialize()
            
            namespace = self.namespaces.get(content_type, content_type)
            
            # Validate query vector
            if len(query_vector) != self.dimension:
                raise SearchError(
                    f"Query vector dimension mismatch: expected {self.dimension}, "
                    f"got {len(query_vector)}"
                )
            
            # Convert to list
            query_vector_list = query_vector.tolist() if isinstance(query_vector, np.ndarray) else query_vector
            
            # Prepare search parameters
            search_params = {
                "vector": query_vector_list,
                "top_k": k,
                "namespace": namespace,
                "include_metadata": include_metadata
            }
            
            # Add metadata filter if provided
            if metadata_filter:
                search_params["filter"] = metadata_filter
            
            # Perform search
            response = self.index.query(**search_params)
            
            # Process results
            results = []
            for match in response.matches:
                similarity_score = match.score
                
                # Apply similarity threshold
                if similarity_score < similarity_threshold:
                    continue
                
                # Extract metadata
                metadata = match.metadata if include_metadata else {}
                content_id = metadata.get("content_id", match.id)
                
                # Get fingerprint info
                fingerprint_info = await self._get_fingerprint_info(content_id)
                
                result = PineconeSearchResult(
                    content_id=content_id,
                    fingerprint_id=fingerprint_info.get("id", 0),
                    similarity_score=similarity_score,
                    content_type=content_type,
                    metadata=metadata,
                    namespace=namespace
                )
                results.append(result)
            
            # Update performance stats
            response_time = (datetime.now() - start_time).total_seconds()
            self._update_search_stats(response_time)
            
            logger.info(
                f"Pinecone search completed for {content_type}: "
                f"{len(results)} results in {response_time:.3f}s"
            )
            
            return results
            
        except Exception as e:
            self.search_stats["errors"] += 1
            logger.error(f"Pinecone search failed for {content_type}: {str(e)}")
            raise SearchError(f"Pinecone search failed: {str(e)}")
    
    async def delete_vectors(
        self,
        content_type: str,
        content_ids: List[str]
    ) -> Dict[str, int]:
        """
        Delete vectors from Pinecone index
        
        Args:
            content_type: Content type
            content_ids: List of content IDs to delete
            
        Returns:
            Deletion statistics
        """
        try:
            if not self.index:
                await self.initialize()
            
            namespace = self.namespaces.get(content_type, content_type)
            
            # Delete vectors in batches
            batch_size = 1000  # Pinecone deletion batch limit
            deleted_count = 0
            
            for i in range(0, len(content_ids), batch_size):
                batch = content_ids[i:i + batch_size]
                
                response = self.index.delete(
                    ids=batch,
                    namespace=namespace
                )
                
                deleted_count += len(batch)
                
                logger.debug(
                    f"Deleted batch {i//batch_size + 1}: {len(batch)} vectors"
                )
            
            logger.info(
                f"Successfully deleted {deleted_count} vectors "
                f"from {content_type} namespace"
            )
            
            return {
                "total": len(content_ids),
                "deleted": deleted_count,
                "namespace": namespace
            }
            
        except Exception as e:
            logger.error(f"Failed to delete vectors for {content_type}: {str(e)}")
            raise VectorStoreError(f"Vector deletion failed: {str(e)}")
    
    async def get_vector(
        self,
        content_type: str,
        content_id: str,
        include_metadata: bool = True
    ) -> Optional[Dict[str, Any]]:
        """
        Fetch a specific vector by ID
        
        Args:
            content_type: Content type
            content_id: Content ID
            include_metadata: Include metadata in response
            
        Returns:
            Vector data or None if not found
        """
        try:
            if not self.index:
                await self.initialize()
            
            namespace = self.namespaces.get(content_type, content_type)
            
            response = self.index.fetch(
                ids=[content_id],
                namespace=namespace
            )
            
            if content_id in response.vectors:
                vector_data = response.vectors[content_id]
                
                result = {
                    "id": content_id,
                    "values": vector_data.values,
                    "namespace": namespace
                }
                
                if include_metadata and vector_data.metadata:
                    result["metadata"] = vector_data.metadata
                
                return result
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to fetch vector {content_id}: {str(e)}")
            raise VectorStoreError(f"Vector fetch failed: {str(e)}")
    
    async def get_index_stats(self) -> Optional[PineconeIndexStats]:
        """Get Pinecone index statistics"""
        try:
            if not self.index:
                await self.initialize()
            
            stats = self.index.describe_index_stats()
            
            # Get namespace statistics
            namespaces = {}
            if stats.namespaces:
                for ns_name, ns_stats in stats.namespaces.items():
                    namespaces[ns_name] = ns_stats.vector_count
            
            return PineconeIndexStats(
                total_vectors=stats.total_vector_count,
                dimension=stats.dimension,
                index_fullness=stats.index_fullness,
                namespaces=namespaces,
                total_requests=self.search_stats["total_searches"],
                avg_latency_ms=self.search_stats["avg_response_time"] * 1000
            )
            
        except Exception as e:
            logger.error(f"Failed to get Pinecone index stats: {str(e)}")
            return None
    
    async def update_metadata(
        self,
        content_type: str,
        content_id: str,
        metadata: Dict[str, Any]
    ) -> bool:
        """
        Update metadata for a vector
        
        Args:
            content_type: Content type
            content_id: Content ID
            metadata: New metadata
            
        Returns:
            True if updated successfully
        """
        try:
            if not self.index:
                await self.initialize()
            
            namespace = self.namespaces.get(content_type, content_type)
            
            # Prepare updated metadata
            full_metadata = {
                "content_id": content_id,
                "content_type": content_type,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                **metadata
            }
            
            # Update metadata (requires vector value, so we fetch first)
            existing_vector = await self.get_vector(content_type, content_id)
            if not existing_vector:
                logger.warning(f"Vector {content_id} not found for metadata update")
                return False
            
            # Upsert with new metadata
            response = self.index.upsert(
                vectors=[(content_id, existing_vector["values"], full_metadata)],
                namespace=namespace
            )
            
            logger.info(f"Updated metadata for vector {content_id}")
            return response.upserted_count > 0
            
        except Exception as e:
            logger.error(f"Failed to update metadata for {content_id}: {str(e)}")
            raise VectorStoreError(f"Metadata update failed: {str(e)}")
    
    async def clear_namespace(self, content_type: str) -> bool:
        """
        Clear all vectors in a namespace
        
        Args:
            content_type: Content type (namespace to clear)
            
        Returns:
            True if cleared successfully
        """
        try:
            if not self.index:
                await self.initialize()
            
            namespace = self.namespaces.get(content_type, content_type)
            
            # Delete all vectors in namespace
            response = self.index.delete(
                delete_all=True,
                namespace=namespace
            )
            
            logger.info(f"Cleared all vectors from {namespace} namespace")
            return True
            
        except Exception as e:
            logger.error(f"Failed to clear namespace {content_type}: {str(e)}")
            raise VectorStoreError(f"Namespace clear failed: {str(e)}")
    
    async def _create_index(self) -> None:
        """Create Pinecone index"""
        try:
            # Determine index spec based on environment
            if self.environment.startswith("gcp-starter"):
                spec = ServerlessSpec(cloud=self.cloud, region=self.region)
            else:
                spec = PodSpec(environment=self.environment)
            
            self.pc.create_index(
                name=self.index_name,
                dimension=self.dimension,
                metric=self.metric,
                spec=spec
            )
            
            logger.info(
                f"Created Pinecone index '{self.index_name}' - "
                f"Dimension: {self.dimension}, Metric: {self.metric}"
            )
            
            # Wait for index to be ready
            import time
            while not self.pc.describe_index(self.index_name).status['ready']:
                time.sleep(1)
            
        except Exception as e:
            logger.error(f"Failed to create Pinecone index: {str(e)}")
            raise VectorStoreError(f"Index creation failed: {str(e)}")
    
    async def _get_fingerprint_info(self, content_id: str) -> Dict[str, Any]:
        """Get fingerprint information from database"""
        try:
            async with get_db_session() as session:
                stmt = select(ContentFingerprint).where(
                    ContentFingerprint.content_id == content_id
                )
                result = await session.execute(stmt)
                fingerprint = result.scalar_one_or_none()
                
                if fingerprint:
                    return {
                        "id": fingerprint.id,
                        "user_id": fingerprint.user_id,
                        "content_type": fingerprint.content_type,
                        "created_at": fingerprint.created_at
                    }
                
                return {"id": 0}
                
        except Exception as e:
            logger.error(f"Failed to get fingerprint info for {content_id}: {str(e)}")
            return {"id": 0}
    
    def _update_search_stats(self, response_time: float) -> None:
        """Update search performance statistics"""
        total_searches = self.search_stats["total_searches"]
        current_avg = self.search_stats["avg_response_time"]
        
        # Calculate new average
        new_avg = ((current_avg * (total_searches - 1)) + response_time) / total_searches
        self.search_stats["avg_response_time"] = new_avg
    
    async def close(self) -> None:
        """Close Pinecone connection"""
        try:
            # Pinecone client doesn't require explicit closing
            self.index = None
            logger.info("Pinecone vector store closed successfully")
        except Exception as e:
            logger.error(f"Error closing Pinecone vector store: {str(e)}")
