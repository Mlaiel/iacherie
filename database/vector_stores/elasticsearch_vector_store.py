"""Elasticsearch Vector Store Implementation

This module provides Elasticsearch-based vector storage with hybrid search capabilities.
Combines vector similarity search with full-text search and filtering.

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
from elasticsearch import AsyncElasticsearch, exceptions as es_exceptions
from elasticsearch.helpers import async_bulk, async_scan
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
class HybridSearchResult:
    """
Hybrid search result combining vector and text search"""
    content_id: str
    fingerprint_id: int
    vector_score: float
    text_score: float
    combined_score: float
    content_type: str
    metadata: Dict[str, Any]
    highlights: Dict[str, List[str]]


@dataclass
class ElasticsearchStats:
    """
Elasticsearch cluster and index statistics"""
    cluster_health: str
    total_documents: int
    index_size_bytes: int
    search_latency_ms: float
    indexing_rate: float
    memory_usage_mb: float


class ElasticsearchVectorStore:
    """
    Elasticsearch-based vector store with hybrid search capabilities.
    
    Features:
    - Dense vector search using kNN
    - Full-text search and filtering
    - Hybrid scoring combining vector and text relevance
    - Real-time indexing and search
    - Distributed storage and search
    - Advanced analytics and aggregations
    """
    
    def __init__(
        self,
        hosts: List[str] = None,
        index_prefix: str = "content_vectors",
        vector_dimension: int = 512,
        shard_count: int = 1,
        replica_count: int = 0
    ):
        """
        Initialize Elasticsearch vector store
        
        Args:
            hosts: Elasticsearch cluster hosts
            index_prefix: Prefix for index names
            vector_dimension: Vector dimension
            shard_count: Number of shards per index
            replica_count: Number of replicas per index
        """
        self.hosts = hosts or [settings.ELASTICSEARCH_URL or "http://localhost:9200"]
        self.index_prefix = index_prefix
        self.vector_dimension = vector_dimension
        self.shard_count = shard_count
        self.replica_count = replica_count
        
        # Initialize Elasticsearch client
        self.client = AsyncElasticsearch(
            hosts=self.hosts,
            timeout=30,
            max_retries=3,
            retry_on_timeout=True
        )
        
        # Index mappings for different content types
        self.index_mappings = {
            "audio": self._get_audio_mapping(),
            "video": self._get_video_mapping(),
            "image": self._get_image_mapping(),
            "text": self._get_text_mapping()
        }
        
        # Search statistics
        self.search_stats = {
            "total_searches": 0,
            "avg_response_time": 0.0,
            "vector_searches": 0,
            "text_searches": 0,
            "hybrid_searches": 0
        }
        
        logger.info(
            f"Initialized Elasticsearch vector store - Hosts: {self.hosts}, "
            f"Dimension: {vector_dimension}, Index Prefix: {index_prefix}"
        )
    
    async def initialize(self) -> None:
        """Initialize Elasticsearch cluster and indices"""
        try:
            # Check cluster health
            health = await self.client.cluster.health()
            logger.info(f"Elasticsearch cluster health: {health['status']}")
            
            # Create indices for each content type
            for content_type in ["audio", "video", "image", "text"]:
                await self._create_index(content_type)
            
            logger.info("Elasticsearch vector store initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize Elasticsearch: {str(e)}")
            raise VectorStoreError(f"Elasticsearch initialization failed: {str(e)}")
    
    @measure_execution_time
    async def index_document(
        self,
        content_type: str,
        content_id: str,
        vector: np.ndarray,
        metadata: Dict[str, Any],
        text_content: str = None,
        fingerprint_id: int = None
    ) -> str:
        """
        Index a document with vector and metadata
        
        Args:
            content_type: Content type (audio, video, image, text)
            content_id: Unique content identifier
            vector: Dense vector embedding
            metadata: Document metadata
            text_content: Text content for full-text search
            fingerprint_id: Associated fingerprint ID
            
        Returns:
            Document ID in Elasticsearch
        """
        try:
            index_name = f"{self.index_prefix}_{content_type}"
            
            # Validate vector dimension
            if len(vector) != self.vector_dimension:
                raise VectorStoreError(
                    f"Vector dimension mismatch: expected {self.vector_dimension}, "
                    f"got {len(vector)}"
                )
            
            # Prepare document
            doc = {
                "content_id": content_id,
                "fingerprint_id": fingerprint_id,
                "content_type": content_type,
                "vector": vector.tolist(),
                "metadata": metadata,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "text_content": text_content or "",
                **metadata  # Flatten metadata for easier searching
            }
            
            # Index document
            response = await self.client.index(
                index=index_name,
                id=content_id,
                document=doc,
                refresh=True  # For immediate search availability
            )
            
            logger.info(
                f"Indexed document {content_id} in {index_name}: {response['result']}"
            )
            
            return response['_id']
            
        except Exception as e:
            logger.error(
                f"Failed to index document {content_id} in {content_type}: {str(e)}"
            )
            raise VectorStoreError(f"Document indexing failed: {str(e)}")
    
    @measure_execution_time
    async def vector_search(
        self,
        content_type: str,
        query_vector: np.ndarray,
        k: int = 10,
        similarity_threshold: float = 0.8,
        filters: Dict[str, Any] = None
    ) -> List[HybridSearchResult]:
        """
        Perform vector similarity search
        
        Args:
            content_type: Content type to search
            query_vector: Query vector
            k: Number of results
            similarity_threshold: Minimum similarity score
            filters: Additional filters
            
        Returns:
            List of search results
        """
        try:
            self.search_stats["vector_searches"] += 1
            start_time = datetime.now()
            
            index_name = f"{self.index_prefix}_{content_type}"
            
            # Validate vector
            if len(query_vector) != self.vector_dimension:
                raise SearchError(
                    f"Query vector dimension mismatch: expected {self.vector_dimension}, "
                    f"got {len(query_vector)}"
                )
            
            # Build search query
            search_query = {
                "size": k,
                "query": {
                    "bool": {
                        "must": [
                            {
                                "knn": {
                                    "field": "vector",
                                    "query_vector": query_vector.tolist(),
                                    "k": k * 2,  # Get more candidates
                                    "num_candidates": k * 10
                                }
                            }
                        ]
                    }
                },
                "_source": {
                    "excludes": ["vector"]  # Don't return vectors in response
                }
            }
            
            # Add filters if provided
            if filters:
                filter_clauses = []
                for field, value in filters.items():
                    if isinstance(value, list):
                        filter_clauses.append({"terms": {field: value}})
                    else:
                        filter_clauses.append({"term": {field: value}})
                
                if filter_clauses:
                    search_query["query"]["bool"]["filter"] = filter_clauses
            
            # Execute search
            response = await self.client.search(
                index=index_name,
                body=search_query
            )
            
            # Process results
            results = []
            for hit in response["hits"]["hits"]:
                score = hit["_score"]
                similarity_score = self._score_to_similarity(score)
                
                if similarity_score < similarity_threshold:
                    continue
                
                source = hit["_source"]
                
                result = HybridSearchResult(
                    content_id=source["content_id"],
                    fingerprint_id=source.get("fingerprint_id", 0),
                    vector_score=similarity_score,
                    text_score=0.0,  # No text search in pure vector search
                    combined_score=similarity_score,
                    content_type=content_type,
                    metadata=source.get("metadata", {}),
                    highlights={}
                )
                results.append(result)
            
            # Update stats
            response_time = (datetime.now() - start_time).total_seconds()
            self._update_search_stats(response_time)
            
            logger.info(
                f"Vector search completed: {len(results)} results in {response_time:.3f}s"
            )
            
            return results
            
        except Exception as e:
            logger.error(f"Vector search failed: {str(e)}")
            raise SearchError(f"Vector search failed: {str(e)}")
    
    @measure_execution_time
    async def text_search(
        self,
        content_type: str,
        query_text: str,
        k: int = 10,
        filters: Dict[str, Any] = None
    ) -> List[HybridSearchResult]:
        """
        Perform full-text search
        
        Args:
            content_type: Content type to search
            query_text: Text query
            k: Number of results
            filters: Additional filters
            
        Returns:
            List of search results
        """
        try:
            self.search_stats["text_searches"] += 1
            start_time = datetime.now()
            
            index_name = f"{self.index_prefix}_{content_type}"
            
            # Build search query
            search_query = {
                "size": k,
                "query": {
                    "bool": {
                        "should": [
                            {
                                "multi_match": {
                                    "query": query_text,
                                    "fields": [
                                        "text_content^3",
                                        "metadata.title^2",
                                        "metadata.description^1.5",
                                        "metadata.tags^1.2",
                                        "metadata.*"
                                    ],
                                    "type": "best_fields",
                                    "fuzziness": "AUTO"
                                }
                            }
                        ]
                    }
                },
                "highlight": {
                    "fields": {
                        "text_content": {},
                        "metadata.title": {},
                        "metadata.description": {}
                    }
                },
                "_source": {
                    "excludes": ["vector"]
                }
            }
            
            # Add filters
            if filters:
                filter_clauses = []
                for field, value in filters.items():
                    if isinstance(value, list):
                        filter_clauses.append({"terms": {field: value}})
                    else:
                        filter_clauses.append({"term": {field: value}})
                
                if filter_clauses:
                    search_query["query"]["bool"]["filter"] = filter_clauses
            
            # Execute search
            response = await self.client.search(
                index=index_name,
                body=search_query
            )
            
            # Process results
            results = []
            for hit in response["hits"]["hits"]:
                source = hit["_source"]
                text_score = hit["_score"] / 10.0  # Normalize to 0-1 range
                
                result = HybridSearchResult(
                    content_id=source["content_id"],
                    fingerprint_id=source.get("fingerprint_id", 0),
                    vector_score=0.0,  # No vector search in pure text search
                    text_score=text_score,
                    combined_score=text_score,
                    content_type=content_type,
                    metadata=source.get("metadata", {}),
                    highlights=hit.get("highlight", {})
                )
                results.append(result)
            
            # Update stats
            response_time = (datetime.now() - start_time).total_seconds()
            self._update_search_stats(response_time)
            
            logger.info(
                f"Text search completed: {len(results)} results in {response_time:.3f}s"
            )
            
            return results
            
        except Exception as e:
            logger.error(f"Text search failed: {str(e)}")
            raise SearchError(f"Text search failed: {str(e)}")
    
    @measure_execution_time
    async def hybrid_search(
        self,
        content_type: str,
        query_vector: np.ndarray = None,
        query_text: str = None,
        k: int = 10,
        vector_weight: float = 0.7,
        text_weight: float = 0.3,
        filters: Dict[str, Any] = None
    ) -> List[HybridSearchResult]:
        """
        Perform hybrid search combining vector and text search
        
        Args:
            content_type: Content type to search
            query_vector: Query vector (optional)
            query_text: Text query (optional)
            k: Number of results
            vector_weight: Weight for vector search score
            text_weight: Weight for text search score
            filters: Additional filters
            
        Returns:
            List of hybrid search results
        """
        try:
            self.search_stats["hybrid_searches"] += 1
            start_time = datetime.now()
            
            if not query_vector and not query_text:
                raise SearchError("Either query_vector or query_text must be provided")
            
            index_name = f"{self.index_prefix}_{content_type}"
            
            # Build hybrid query
            must_clauses = []
            should_clauses = []
            
            # Add vector search
            if query_vector is not None:
                should_clauses.append({
                    "script_score": {
                        "query": {"match_all": {}},
                        "script": {
                            "source": f"""
                                cosineSimilarity(params.query_vector, 'vector') * {vector_weight}
                            """,
                            "params": {
                                "query_vector": query_vector.tolist()
                            }
                        }
                    }
                })
            
            # Add text search
            if query_text:
                should_clauses.append({
                    "script_score": {
                        "query": {
                            "multi_match": {
                                "query": query_text,
                                "fields": [
                                    "text_content^3",
                                    "metadata.title^2",
                                    "metadata.description^1.5",
                                    "metadata.tags^1.2"
                                ]
                            }
                        },
                        "script": {
                            "source": f"_score * {text_weight}"
                        }
                    }
                })
            
            search_query = {
                "size": k,
                "query": {
                    "bool": {
                        "should": should_clauses,
                        "minimum_should_match": 1
                    }
                },
                "highlight": {
                    "fields": {
                        "text_content": {},
                        "metadata.title": {},
                        "metadata.description": {}
                    }
                },
                "_source": {
                    "excludes": ["vector"]
                }
            }
            
            # Add filters
            if filters:
                filter_clauses = []
                for field, value in filters.items():
                    if isinstance(value, list):
                        filter_clauses.append({"terms": {field: value}})
                    else:
                        filter_clauses.append({"term": {field: value}})
                
                if filter_clauses:
                    search_query["query"]["bool"]["filter"] = filter_clauses
            
            # Execute search
            response = await self.client.search(
                index=index_name,
                body=search_query
            )
            
            # Process results
            results = []
            for hit in response["hits"]["hits"]:
                source = hit["_source"]
                combined_score = hit["_score"]
                
                # Calculate individual scores (approximate)
                vector_score = combined_score * vector_weight if query_vector is not None else 0.0
                text_score = combined_score * text_weight if query_text else 0.0
                
                result = HybridSearchResult(
                    content_id=source["content_id"],
                    fingerprint_id=source.get("fingerprint_id", 0),
                    vector_score=vector_score,
                    text_score=text_score,
                    combined_score=combined_score,
                    content_type=content_type,
                    metadata=source.get("metadata", {}),
                    highlights=hit.get("highlight", {})
                )
                results.append(result)
            
            # Update stats
            response_time = (datetime.now() - start_time).total_seconds()
            self._update_search_stats(response_time)
            
            logger.info(
                f"Hybrid search completed: {len(results)} results in {response_time:.3f}s"
            )
            
            return results
            
        except Exception as e:
            logger.error(f"Hybrid search failed: {str(e)}")
            raise SearchError(f"Hybrid search failed: {str(e)}")
    
    async def delete_document(self, content_type: str, content_id: str) -> bool:
        """
        Delete a document from the index
        
        Args:
            content_type: Content type
            content_id: Content ID to delete
            
        Returns:
            True if deleted successfully
        """
        try:
            index_name = f"{self.index_prefix}_{content_type}"
            
            response = await self.client.delete(
                index=index_name,
                id=content_id,
                refresh=True
            )
            
            logger.info(f"Deleted document {content_id} from {index_name}")
            return response["result"] == "deleted"
            
        except es_exceptions.NotFoundError:
            logger.warning(f"Document {content_id} not found in {content_type}")
            return False
        except Exception as e:
            logger.error(f"Failed to delete document {content_id}: {str(e)}")
            raise VectorStoreError(f"Document deletion failed: {str(e)}")
    
    async def bulk_index(
        self,
        content_type: str,
        documents: List[Dict[str, Any]]
    ) -> Dict[str, int]:
        """
        Bulk index multiple documents
        
        Args:
            content_type: Content type
            documents: List of documents to index
            
        Returns:
            Statistics about the bulk operation
        """
        try:
            index_name = f"{self.index_prefix}_{content_type}"
            
            # Prepare bulk actions
            actions = []
            for doc in documents:
                action = {
                    "_index": index_name,
                    "_id": doc["content_id"],
                    "_source": doc
                }
                actions.append(action)
            
            # Execute bulk operation
            success_count, failed_items = await async_bulk(
                self.client,
                actions,
                refresh=True
            )
            
            stats = {
                "total": len(documents),
                "successful": success_count,
                "failed": len(failed_items)
            }
            
            logger.info(
                f"Bulk indexed {success_count}/{len(documents)} documents "
                f"in {index_name}"
            )
            
            return stats
            
        except Exception as e:
            logger.error(f"Bulk indexing failed: {str(e)}")
            raise VectorStoreError(f"Bulk indexing failed: {str(e)}")
    
    async def get_cluster_stats(self) -> ElasticsearchStats:
        """Get Elasticsearch cluster statistics"""
        try:
            # Get cluster health
            health = await self.client.cluster.health()
            
            # Get cluster stats
            stats = await self.client.cluster.stats()
            
            # Calculate metrics
            total_docs = stats["indices"]["count"]
            index_size_bytes = stats["indices"]["store"]["size_in_bytes"]
            memory_usage_mb = stats["nodes"]["jvm"]["mem"]["heap_used_in_bytes"] / (1024 * 1024)
            
            # Get search latency (approximate)
            search_stats = stats["indices"]["search"]
            search_latency_ms = (
                search_stats["query_time_in_millis"] / max(search_stats["query_total"], 1)
            )
            
            # Get indexing rate
            indexing_stats = stats["indices"]["indexing"]
            indexing_rate = indexing_stats["index_total"] / max(
                indexing_stats["index_time_in_millis"] / 1000, 1
            )
            
            return ElasticsearchStats(
                cluster_health=health["status"],
                total_documents=total_docs,
                index_size_bytes=index_size_bytes,
                search_latency_ms=search_latency_ms,
                indexing_rate=indexing_rate,
                memory_usage_mb=memory_usage_mb
            )
            
        except Exception as e:
            logger.error(f"Failed to get cluster stats: {str(e)}")
            raise VectorStoreError(f"Cluster stats retrieval failed: {str(e)}")
    
    async def _create_index(self, content_type: str) -> None:
        """Create index for content type"""
        try:
            index_name = f"{self.index_prefix}_{content_type}"
            
            if await self.client.indices.exists(index=index_name):
                logger.info(f"Index {index_name} already exists")
                return
            
            # Get mapping for content type
            mapping = self.index_mappings.get(content_type, self._get_default_mapping())
            
            # Create index
            await self.client.indices.create(
                index=index_name,
                body={
                    "settings": {
                        "number_of_shards": self.shard_count,
                        "number_of_replicas": self.replica_count,
                        "index.knn": True,  # Enable kNN search
                        "analysis": {
                            "analyzer": {
                                "content_analyzer": {
                                    "type": "custom",
                                    "tokenizer": "standard",
                                    "filter": [
                                        "lowercase",
                                        "stop",
                                        "stemmer"
                                    ]
                                }
                            }
                        }
                    },
                    "mappings": mapping
                }
            )
            
            logger.info(f"Created index {index_name}")
            
        except Exception as e:
            logger.error(f"Failed to create index {index_name}: {str(e)}")
            raise VectorStoreError(f"Index creation failed: {str(e)}")
    
    def _get_default_mapping(self) -> Dict[str, Any]:
        """Get default mapping for content"""
        return {
            "properties": {
                "content_id": {"type": "keyword"},
                "fingerprint_id": {"type": "long"},
                "content_type": {"type": "keyword"},
                "vector": {
                    "type": "dense_vector",
                    "dims": self.vector_dimension,
                    "index": True,
                    "similarity": "cosine"
                },
                "text_content": {
                    "type": "text",
                    "analyzer": "content_analyzer"
                },
                "metadata": {
                    "type": "object",
                    "dynamic": True
                },
                "timestamp": {"type": "date"}
            }
        }
    
    def _get_audio_mapping(self) -> Dict[str, Any]:
        """Get mapping for audio content"""
        mapping = self._get_default_mapping()
        mapping["properties"]["metadata"]["properties"] = {
            "title": {"type": "text", "analyzer": "content_analyzer"},
            "artist": {"type": "keyword"},
            "album": {"type": "text"},
            "genre": {"type": "keyword"},
            "duration": {"type": "float"},
            "sample_rate": {"type": "integer"},
            "bitrate": {"type": "integer"},
            "bpm": {"type": "float"},
            "key": {"type": "keyword"},
            "mood": {"type": "keyword"},
            "energy": {"type": "float"},
            "valence": {"type": "float"}
        }
        return mapping
    
    def _get_video_mapping(self) -> Dict[str, Any]:
        """Get mapping for video content"""
        mapping = self._get_default_mapping()
        mapping["properties"]["metadata"]["properties"] = {
            "title": {"type": "text", "analyzer": "content_analyzer"},
            "description": {"type": "text", "analyzer": "content_analyzer"},
            "duration": {"type": "float"},
            "resolution": {"type": "keyword"},
            "fps": {"type": "float"},
            "bitrate": {"type": "integer"},
            "codec": {"type": "keyword"},
            "tags": {"type": "keyword"},
            "category": {"type": "keyword"},
            "language": {"type": "keyword"}
        }
        return mapping
    
    def _get_image_mapping(self) -> Dict[str, Any]:
        """Get mapping for image content"""
        mapping = self._get_default_mapping()
        mapping["properties"]["metadata"]["properties"] = {
            "title": {"type": "text", "analyzer": "content_analyzer"},
            "description": {"type": "text", "analyzer": "content_analyzer"},
            "width": {"type": "integer"},
            "height": {"type": "integer"},
            "format": {"type": "keyword"},
            "color_space": {"type": "keyword"},
            "tags": {"type": "keyword"},
            "location": {"type": "geo_point"},
            "camera_model": {"type": "keyword"},
            "dominant_colors": {"type": "keyword"}
        }
        return mapping
    
    def _get_text_mapping(self) -> Dict[str, Any]:
        """Get mapping for text content"""
        mapping = self._get_default_mapping()
        mapping["properties"]["metadata"]["properties"] = {
            "title": {"type": "text", "analyzer": "content_analyzer"},
            "author": {"type": "keyword"},
            "language": {"type": "keyword"},
            "word_count": {"type": "integer"},
            "tags": {"type": "keyword"},
            "category": {"type": "keyword"},
            "sentiment": {"type": "float"},
            "reading_time": {"type": "float"}
        }
        return mapping
    
    def _score_to_similarity(self, score: float) -> float:
        """Convert Elasticsearch score to similarity score (0-1)"""
        # This is a simple conversion, can be adjusted based on requirements
        return min(1.0, score / 10.0)
    
    def _update_search_stats(self, response_time: float) -> None:
        """
Update search performance statistics"""
        total_searches = self.search_stats["total_searches"]
        current_avg = self.search_stats["avg_response_time"]
        
        # Calculate new average
        new_avg = ((current_avg * (total_searches - 1)) + response_time) / total_searches
        self.search_stats["avg_response_time"] = new_avg
    
    async def close(self) -> None:
        """Close Elasticsearch client"""
        try:
            await self.client.close()
            logger.info("Elasticsearch client closed successfully")
        except Exception as e:
            logger.error(f"Error closing Elasticsearch client: {str(e)}")
