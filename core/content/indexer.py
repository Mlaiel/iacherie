"""Content Indexer - AI-Powered Content Indexing and Search Engine
===============================================================

The ContentIndexer creates and maintains searchable indexes of content
using advanced AI techniques for semantic search and content discovery.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: © 2025 Fahed Mlaiel. All rights reserved.
"""import asyncio
import logging
from typing import Dict, List, Optional, Any, Union
from datetime import datetime
import uuid

import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import faiss
from sqlalchemy.ext.asyncio import AsyncSession

from ..search.vector_store import VectorStore
from ..search.elasticsearch_client import ElasticsearchClient


class ContentIndexer:
    """    AI-Powered Content Indexing and Search Engine
    
    Provides advanced content indexing capabilities including:
    - Semantic vector indexing for similarity search
    - Full-text search indexing
    - Multi-modal content indexing
    - Real-time index updates
    - Content recommendation indexing
    """    
    def __init__(self, db_session: AsyncSession):
        self.db = db_session
        self.logger = logging.getLogger(__name__)
        
        # Initialize search components
        self.vector_store = VectorStore()
        self.elasticsearch = ElasticsearchClient()
        self.sentence_model = SentenceTransformer('all-MiniLM-L6-v2')
        
        # Index configuration
        self.index_config = {
            "vector_dimension": 384,  # SentenceTransformer dimension
            "similarity_threshold": 0.7,
            "max_results": 100
        }

    async def index_content(self, content_id: str) -> Dict[str, Any]:
        """        Index content for search and discovery
        
        Args:
            content_id: Content identifier
            
        Returns:
            Indexing result
        """        try:
            self.logger.info(f"Indexing content {content_id}")
            
            # Get content data
            content = await self._get_content(content_id)
            if not content:
                return {
                    "success": False,
                    "error": "Content not found",
                    "content_id": content_id
                }
            
            # Extract searchable text
            searchable_text = await self._extract_searchable_text(content)
            
            # Generate embeddings
            embeddings = await self._generate_embeddings(searchable_text)
            
            # Index in vector store
            vector_result = await self.vector_store.add_vector(
                content_id, embeddings, metadata=content.metadata
            )
            
            # Index in Elasticsearch
            es_result = await self.elasticsearch.index_document(
                index="content",
                doc_id=content_id,
                document={
                    "content_id": content_id,
                    "title": content.title,
                    "description": content.metadata.get("description", ""),
                    "content_type": content.content_type,
                    "tags": content.metadata.get("tags", []),
                    "searchable_text": searchable_text,
                    "indexed_at": datetime.utcnow().isoformat(),
                    "user_id": content.user_id
                }
            )
            
            return {
                "success": True,
                "content_id": content_id,
                "vector_indexed": vector_result.get("success", False),
                "text_indexed": es_result.get("success", False),
                "embeddings_generated": len(embeddings) > 0,
                "indexed_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            error_msg = f"Content indexing failed: {str(e)}"
            self.logger.error(error_msg)
            return {
                "success": False,
                "error": error_msg,
                "content_id": content_id
            }

    async def search_content(
        self,
        query: str,
        content_types: List[str] = None,
        user_id: int = None,
        limit: int = 50
    ) -> Dict[str, Any]:
        """        Search content using hybrid approach
        
        Args:
            query: Search query
            content_types: Filter by content types
            user_id: Filter by user ID
            limit: Maximum results
            
        Returns:
            Search results with relevance scores
        """        try:
            # Generate query embedding
            query_embedding = await self._generate_embeddings(query)
            
            # Vector similarity search
            vector_results = await self.vector_store.search_similar(
                query_embedding, limit=limit * 2
            )
            
            # Text search
            text_results = await self.elasticsearch.search(
                index="content",
                query={
                    "bool": {
                        "must": [
                            {
                                "multi_match": {
                                    "query": query,
                                    "fields": ["title^3", "description^2", "searchable_text", "tags^2"]
                                }
                            }
                        ],
                        "filter": self._build_search_filters(content_types, user_id)
                    }
                },
                size=limit * 2
            )
            
            # Combine and rank results
            combined_results = await self._combine_search_results(
                vector_results, text_results, limit
            )
            
            return {
                "success": True,
                "query": query,
                "results": combined_results,
                "total_found": len(combined_results),
                "search_time": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Search failed: {str(e)}",
                "query": query,
                "results": []
            }

    async def find_similar_content(
        self,
        content_id: str,
        limit: int = 10
    ) -> Dict[str, Any]:
        """        Find content similar to given content
        
        Args:
            content_id: Reference content ID
            limit: Maximum similar content to return
            
        Returns:
            Similar content results
        """        try:
            # Get content vector
            content_vector = await self.vector_store.get_vector(content_id)
            if not content_vector:
                return {
                    "success": False,
                    "error": "Content vector not found",
                    "content_id": content_id
                }
            
            # Find similar vectors
            similar_results = await self.vector_store.search_similar(
                content_vector, limit=limit + 1  # +1 to exclude self
            )
            
            # Filter out the original content
            filtered_results = [
                result for result in similar_results
                if result.get("content_id") != content_id
            ][:limit]
            
            return {
                "success": True,
                "content_id": content_id,
                "similar_content": filtered_results,
                "total_found": len(filtered_results)
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Similar content search failed: {str(e)}",
                "content_id": content_id
            }

    async def get_content_recommendations(
        self,
        user_id: int,
        content_types: List[str] = None,
        limit: int = 20
    ) -> Dict[str, Any]:
        """        Get personalized content recommendations
        
        Args:
            user_id: User identifier
            content_types: Filter by content types
            limit: Maximum recommendations
            
        Returns:
            Personalized content recommendations
        """        try:
            # Get user's interaction history
            user_history = await self._get_user_interaction_history(user_id)
            
            # Build user profile vector
            user_profile = await self._build_user_profile_vector(user_history)
            
            # Find content similar to user profile
            recommendations = await self.vector_store.search_similar(
                user_profile, limit=limit * 2
            )
            
            # Filter and rank recommendations
            filtered_recommendations = await self._filter_recommendations(
                recommendations, user_id, content_types, limit
            )
            
            return {
                "success": True,
                "user_id": user_id,
                "recommendations": filtered_recommendations,
                "total_recommendations": len(filtered_recommendations),
                "recommendation_source": "ai_personalized"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Recommendations failed: {str(e)}",
                "user_id": user_id,
                "recommendations": []
            }

    async def update_content_index(self, content_id: str) -> Dict[str, Any]:
        """        Update existing content index
        
        Args:
            content_id: Content identifier
            
        Returns:
            Update result
        """        try:
            # Remove existing index
            await self.remove_content_index(content_id)
            
            # Re-index content
            result = await self.index_content(content_id)
            
            if result["success"]:
                result["operation"] = "updated"
            
            return result
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Index update failed: {str(e)}",
                "content_id": content_id
            }

    async def remove_content_index(self, content_id: str) -> Dict[str, Any]:
        """        Remove content from all indexes
        
        Args:
            content_id: Content identifier
            
        Returns:
            Removal result
        """        try:
            # Remove from vector store
            vector_result = await self.vector_store.remove_vector(content_id)
            
            # Remove from Elasticsearch
            es_result = await self.elasticsearch.delete_document(
                index="content", doc_id=content_id
            )
            
            return {
                "success": True,
                "content_id": content_id,
                "vector_removed": vector_result.get("success", False),
                "text_removed": es_result.get("success", False),
                "removed_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Index removal failed: {str(e)}",
                "content_id": content_id
            }

    async def get_trending_content(
        self,
        time_period: str = "week",
        content_types: List[str] = None,
        limit: int = 50
    ) -> Dict[str, Any]:
        """        Get trending content based on engagement metrics
        
        Args:
            time_period: Time period for trending calculation
            content_types: Filter by content types
            limit: Maximum results
            
        Returns:
            Trending content results
        """        try:
            # Calculate time range
            time_filter = self._get_time_filter(time_period)
            
            # Search for trending content
            trending_query = {
                "bool": {
                    "must": [
                        {"range": {"indexed_at": time_filter}}
                    ],
                    "filter": self._build_search_filters(content_types, None)
                }
            }
            
            # Get content with high engagement
            results = await self.elasticsearch.search(
                index="content",
                query=trending_query,
                sort=[
                    {"engagement_score": {"order": "desc"}},
                    {"views_count": {"order": "desc"}}
                ],
                size=limit
            )
            
            return {
                "success": True,
                "trending_content": results.get("hits", []),
                "time_period": time_period,
                "total_found": len(results.get("hits", [])),
                "retrieved_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Trending content retrieval failed: {str(e)}",
                "trending_content": []
            }

    async def build_content_clusters(
        self,
        content_type: str = None,
        num_clusters: int = 10
    ) -> Dict[str, Any]:
        """        Build content clusters for discovery and organization
        
        Args:
            content_type: Filter by content type
            num_clusters: Number of clusters to create
            
        Returns:
            Content clustering results
        """        try:
            # Get all content vectors
            vectors_data = await self.vector_store.get_all_vectors(
                content_type_filter=content_type
            )
            
            if len(vectors_data) < num_clusters:
                return {
                    "success": False,
                    "error": "Insufficient content for clustering",
                    "content_count": len(vectors_data)
                }
            
            # Extract vectors and IDs
            vectors = np.array([item["vector"] for item in vectors_data])
            content_ids = [item["content_id"] for item in vectors_data]
            
            # Perform clustering
            from sklearn.cluster import KMeans
            kmeans = KMeans(n_clusters=num_clusters, random_state=42)
            cluster_labels = kmeans.fit_predict(vectors)
            
            # Organize results by cluster
            clusters = {}
            for i, (content_id, cluster_label) in enumerate(zip(content_ids, cluster_labels)):
                cluster_id = f"cluster_{cluster_label}"
                if cluster_id not in clusters:
                    clusters[cluster_id] = {
                        "cluster_id": cluster_id,
                        "content_ids": [],
                        "cluster_center": kmeans.cluster_centers_[cluster_label].tolist(),
                        "size": 0
                    }
                
                clusters[cluster_id]["content_ids"].append(content_id)
                clusters[cluster_id]["size"] += 1
            
            return {
                "success": True,
                "clusters": list(clusters.values()),
                "num_clusters": len(clusters),
                "total_content": len(vectors_data),
                "content_type": content_type,
                "clustered_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Content clustering failed: {str(e)}",
                "clusters": []
            }

    # Helper methods

    async def _get_content(self, content_id: str):
        """Get content from database"""        # Mock implementation - replace with actual database query
        class MockContent:
            def __init__(self):
                self.id = content_id
                self.title = "Sample Content"
                self.content_type = "text"
                self.user_id = 1
                self.metadata = {
                    "description": "Sample description",
                    "tags": ["sample", "content"]
                }
        
        return MockContent()

    async def _extract_searchable_text(self, content) -> str:
        """Extract searchable text from content"""        searchable_parts = []
        
        # Add title
        if content.title:
            searchable_parts.append(content.title)
        
        # Add description
        if content.metadata.get("description"):
            searchable_parts.append(content.metadata["description"])
        
        # Add tags
        if content.metadata.get("tags"):
            searchable_parts.extend(content.metadata["tags"])
        
        # For text content, could add full text content
        # For audio/video, could add transcription
        # For images, could add OCR text or caption
        
        return " ".join(searchable_parts)

    async def _generate_embeddings(self, text: str) -> np.ndarray:
        """Generate vector embeddings for text"""        try:
            embeddings = self.sentence_model.encode([text])
            return embeddings[0]
        except Exception as e:
            self.logger.error(f"Embedding generation failed: {str(e)}")
            return np.zeros(self.index_config["vector_dimension"])

    def _build_search_filters(
        self,
        content_types: List[str] = None,
        user_id: int = None
    ) -> List[Dict]:
        """Build Elasticsearch filters"""        filters = []
        
        if content_types:
            filters.append({
                "terms": {"content_type": content_types}
            })
        
        if user_id:
            filters.append({
                "term": {"user_id": user_id}
            })
        
        return filters

    async def _combine_search_results(
        self,
        vector_results: List[Dict],
        text_results: Dict,
        limit: int
    ) -> List[Dict]:
        """Combine and rank vector and text search results"""        combined_scores = {}
        
        # Process vector results
        for result in vector_results:
            content_id = result.get("content_id")
            if content_id:
                combined_scores[content_id] = {
                    "content_id": content_id,
                    "vector_score": result.get("similarity", 0.0),
                    "text_score": 0.0,
                    "metadata": result.get("metadata", {})
                }
        
        # Process text results
        for hit in text_results.get("hits", []):
            content_id = hit.get("_source", {}).get("content_id")
            if content_id:
                if content_id not in combined_scores:
                    combined_scores[content_id] = {
                        "content_id": content_id,
                        "vector_score": 0.0,
                        "text_score": 0.0,
                        "metadata": {}
                    }
                
                combined_scores[content_id]["text_score"] = hit.get("_score", 0.0)
                combined_scores[content_id]["metadata"].update(hit.get("_source", {}))
        
        # Calculate combined scores and sort
        for result in combined_scores.values():
            # Weighted combination: 60% vector, 40% text
            result["combined_score"] = (
                result["vector_score"] * 0.6 + 
                result["text_score"] * 0.4
            )
        
        # Sort by combined score and return top results
        sorted_results = sorted(
            combined_scores.values(),
            key=lambda x: x["combined_score"],
            reverse=True
        )
        
        return sorted_results[:limit]

    async def _get_user_interaction_history(self, user_id: int) -> List[Dict]:
        """Get user's content interaction history"""        # Mock implementation - replace with actual data
        return []

    async def _build_user_profile_vector(self, interaction_history: List[Dict]) -> np.ndarray:
        """Build user profile vector from interaction history"""        if not interaction_history:
            # Return zero vector for new users
            return np.zeros(self.index_config["vector_dimension"])
        
        # In real implementation, this would aggregate vectors from user's
        # liked/viewed content weighted by interaction type
        return np.random.random(self.index_config["vector_dimension"])

    async def _filter_recommendations(
        self,
        recommendations: List[Dict],
        user_id: int,
        content_types: List[str],
        limit: int
    ) -> List[Dict]:
        """Filter and rank recommendations"""        filtered = []
        
        for rec in recommendations:
            # Filter by content type if specified
            if content_types:
                content_type = rec.get("metadata", {}).get("content_type")
                if content_type not in content_types:
                    continue
            
            # Filter out user's own content
            content_user_id = rec.get("metadata", {}).get("user_id")
            if content_user_id == user_id:
                continue
            
            filtered.append(rec)
            
            if len(filtered) >= limit:
                break
        
        return filtered

    def _get_time_filter(self, time_period: str) -> Dict[str, str]:
        """Get time filter for trending calculation"""        now = datetime.utcnow()
        
        if time_period == "day":
            start_time = now - timedelta(days=1)
        elif time_period == "week":
            start_time = now - timedelta(weeks=1)
        elif time_period == "month":
            start_time = now - timedelta(days=30)
        else:
            start_time = now - timedelta(weeks=1)  # Default to week
        
        return {
            "gte": start_time.isoformat(),
            "lte": now.isoformat()
        }
