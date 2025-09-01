"""Multimedia Index - Enterprise Content Indexing System

Advanced indexing system for multimedia content discovery and search.
Provides comprehensive indexing, search, and retrieval capabilities.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️  CRITICAL LEGAL NOTICE:
This code and concept are the exclusive intellectual property of Fahed Mlaiel.
Any unauthorized use, copying, distribution, or commercialization without explicit written permission is strictly prohibited.
Contact: mlaiel@live.de for licensing inquiries.
"""

import asyncio
import logging
import json
import hashlib
from typing import Dict, List, Any, Optional, Union, Tuple
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from enum import Enum
import numpy as np
from pathlib import Path

# Search and indexing
try:
    import elasticsearch
    from elasticsearch import Elasticsearch
    ELASTICSEARCH_AVAILABLE = True
except ImportError:
    ELASTICSEARCH_AVAILABLE = False

try:
    import faiss
    FAISS_AVAILABLE = True
except ImportError:
    FAISS_AVAILABLE = False

try:
    from whoosh import index
    from whoosh.fields import Schema, TEXT, KEYWORD, DATETIME, NUMERIC, ID
    from whoosh.qparser import QueryParser, MultifieldParser
    from whoosh.query import Every
    WHOOSH_AVAILABLE = True
except ImportError:
    WHOOSH_AVAILABLE = False

from .analyzer import MultimediaAnalyzer
from .metadata import MultimediaMetadata

logger = logging.getLogger(__name__)


class IndexType(Enum):
    """
Index types"""

    TEXT = "text"
    VECTOR = "vector"
    METADATA = "metadata"
    CONTENT = "content"
    SEMANTIC = "semantic"
    FEATURE = "feature"


class SearchMode(Enum):
    """Search modes"""

    EXACT = "exact"
    FUZZY = "fuzzy"
    SEMANTIC = "semantic"
    HYBRID = "hybrid"
    SIMILARITY = "similarity"


@dataclass
class IndexedContent:
    """Indexed content entry"""
    content_id: str
    file_path: str
    content_type: str
    title: Optional[str] = None
    description: Optional[str] = None
    tags: List[str] = field(default_factory=list)
    keywords: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    technical_metadata: Dict[str, Any] = field(default_factory=dict)
    feature_vectors: Dict[str, List[float]] = field(default_factory=dict)
    content_hash: Optional[str] = None
    file_size: int = 0
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    indexed_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    user_id: Optional[str] = None
    status: str = "active"


@dataclass
class SearchQuery:
    """Search query specification"""
    query_id: str = field(default_factory=lambda: f"q_{datetime.now().timestamp()}")
    query_text: Optional[str] = None
    filters: Dict[str, Any] = field(default_factory=dict)
    content_types: List[str] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)
    date_range: Optional[Tuple[datetime, datetime]] = None
    similarity_threshold: float = 0.7
    feature_vector: Optional[List[float]] = None
    search_mode: SearchMode = SearchMode.HYBRID
    max_results: int = 50
    offset: int = 0
    sort_by: str = "relevance"
    sort_order: str = "desc"
    include_similar: bool = False
    user_id: Optional[str] = None


@dataclass
class SearchResult:
    """Search result entry"""
    content_id: str
    score: float
    content: IndexedContent
    highlights: Dict[str, List[str]] = field(default_factory=dict)
    similarity_scores: Dict[str, float] = field(default_factory=dict)
    explanation: Optional[str] = None


@dataclass
class SearchResponse:
    """
Search response"""
    query_id: str
    total_results: int
    results: List[SearchResult]
    facets: Dict[str, Dict[str, int]] = field(default_factory=dict)
    suggestions: List[str] = field(default_factory=list)
    processing_time: float = 0.0
    search_mode: SearchMode = SearchMode.HYBRID


class MultimediaIndex:
    """
Enterprise multimedia content index"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.analyzer = MultimediaAnalyzer(config.get("analyzer", {}))
        self.metadata_extractor = MultimediaMetadata(config.get("metadata", {}))
        
        # Index storage
        self.indexed_content: Dict[str, IndexedContent] = {}
        
        # Search engines
        self.elasticsearch_client = None
        self.whoosh_index = None
        self.vector_index = None
        
        # Configuration
        self.index_directory = Path(config.get("index_directory", "./multimedia_index"))
        self.elasticsearch_url = config.get("elasticsearch_url")
        self.vector_dimension = config.get("vector_dimension", 512)
        self.enable_vector_search = config.get("enable_vector_search", True)
        self.enable_text_search = config.get("enable_text_search", True)
        self.batch_size = config.get("batch_size", 100)
        
        # Statistics
        self.index_stats = {
            "total_indexed": 0,
            "index_size": 0,
            "last_update": None,
            "content_types": {},
            "search_queries": 0,
            "average_search_time": 0.0
        }
        
    async def initialize(self):
        """Initialize index system"""
        try:
            await self.analyzer.initialize()
            await self.metadata_extractor.initialize()
            
            # Initialize search engines
            await self._initialize_search_engines()
            
            # Create index directory
            self.index_directory.mkdir(parents=True, exist_ok=True)
            
            # Load existing index
            await self._load_existing_index()
            
            logger.info("Multimedia index initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize index: {e}")
            raise
            
    async def index_content(
        self, 
        file_path: str, 
        user_id: Optional[str] = None,
        metadata: Dict[str, Any] = None
    ) -> str:
        """Index multimedia content"""
        try:
            # Generate content ID
            content_id = self._generate_content_id(file_path)
            
            # Check if already indexed
            if content_id in self.indexed_content:
                logger.info(f"Content already indexed: {content_id}")
                return content_id
                
            # Analyze content
            analysis_result = await self.analyzer.analyze_file(file_path)
            
            # Extract metadata
            extracted_metadata = await self.metadata_extractor.extract_metadata(file_path)
            
            # Create indexed content entry
            indexed_content = IndexedContent(
                content_id=content_id,
                file_path=file_path,
                content_type=analysis_result.format_info.get("format", "unknown"),
                title=metadata.get("title") if metadata else None,
                description=analysis_result.description,
                tags=analysis_result.tags,
                keywords=analysis_result.keywords if hasattr(analysis_result, 'keywords') else [],
                metadata=metadata or {},
                technical_metadata=analysis_result.technical_metrics,
                feature_vectors=analysis_result.feature_vectors,
                content_hash=self._calculate_content_hash(file_path),
                file_size=Path(file_path).stat().st_size,
                user_id=user_id
            )
            
            # Store in memory index
            self.indexed_content[content_id] = indexed_content
            
            # Index in search engines
            await self._index_in_search_engines(indexed_content)
            
            # Update statistics
            self._update_index_stats(indexed_content)
            
            logger.info(f"Content indexed successfully: {content_id}")
            return content_id
            
        except Exception as e:
            logger.error(f"Failed to index content {file_path}: {e}")
            raise
            
    async def batch_index(
        self, 
        file_paths: List[str], 
        user_id: Optional[str] = None,
        metadata_list: Optional[List[Dict[str, Any]]] = None
    ) -> List[str]:
        """Index multiple files in batch"""
        try:
            # Create semaphore for parallel processing
            semaphore = asyncio.Semaphore(self.batch_size)
            
            async def index_with_semaphore(i, file_path):
                async with semaphore:
                    metadata = metadata_list[i] if metadata_list and i < len(metadata_list) else None
                    return await self.index_content(file_path, user_id, metadata)
                    
            # Process files in parallel
            tasks = [index_with_semaphore(i, path) for i, path in enumerate(file_paths)]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Filter successful results
            content_ids = []
            for result in results:
                if isinstance(result, str):
                    content_ids.append(result)
                else:
                    logger.error(f"Batch indexing error: {result}")
                    
            return content_ids
            
        except Exception as e:
            logger.error(f"Batch indexing failed: {e}")
            return []
            
    async def search(self, query: SearchQuery) -> SearchResponse:
        """Search indexed content"""
        start_time = datetime.now()
        
        try:
            # Initialize response
            response = SearchResponse(
                query_id=query.query_id,
                total_results=0,
                results=[],
                search_mode=query.search_mode
            )
            
            # Perform search based on mode
            if query.search_mode == SearchMode.EXACT:
                results = await self._exact_search(query)
            elif query.search_mode == SearchMode.FUZZY:
                results = await self._fuzzy_search(query)
            elif query.search_mode == SearchMode.SEMANTIC:
                results = await self._semantic_search(query)
            elif query.search_mode == SearchMode.SIMILARITY:
                results = await self._similarity_search(query)
            else:  # HYBRID
                results = await self._hybrid_search(query)
                
            # Apply filtering and sorting
            filtered_results = self._apply_filters(results, query)
            sorted_results = self._sort_results(filtered_results, query)
            
            # Paginate results
            paginated_results = sorted_results[query.offset:query.offset + query.max_results]
            
            # Generate facets
            facets = self._generate_facets(filtered_results)
            
            # Build response
            response.total_results = len(filtered_results)
            response.results = paginated_results
            response.facets = facets
            response.processing_time = (datetime.now() - start_time).total_seconds()
            
            # Update statistics
            self._update_search_stats(response.processing_time)
            
            return response
            
        except Exception as e:
            logger.error(f"Search failed: {e}")
            return SearchResponse(
                query_id=query.query_id,
                total_results=0,
                results=[],
                processing_time=(datetime.now() - start_time).total_seconds()
            )
            
    async def find_similar(
        self, 
        content_id: str, 
        max_results: int = 10,
        similarity_threshold: float = 0.7
    ) -> List[SearchResult]:
        """Find similar content"""
        try:
            content = self.indexed_content.get(content_id)
            if not content:
                return []
                
            # Use feature vectors for similarity
            if not content.feature_vectors:
                return []
                
            similar_results = []
            
            for other_id, other_content in self.indexed_content.items():
                if other_id == content_id:
                    continue
                    
                # Calculate similarity
                similarity_score = self._calculate_content_similarity(content, other_content)
                
                if similarity_score >= similarity_threshold:
                    result = SearchResult(
                        content_id=other_id,
                        score=similarity_score,
                        content=other_content,
                        similarity_scores={"overall": similarity_score}
                    )
                    similar_results.append(result)
                    
            # Sort by similarity score
            similar_results.sort(key=lambda x: x.score, reverse=True)
            
            return similar_results[:max_results]
            
        except Exception as e:
            logger.error(f"Similar content search failed: {e}")
            return []
            
    async def get_content(self, content_id: str) -> Optional[IndexedContent]:
        """Get indexed content by ID"""
        return self.indexed_content.get(content_id)
        
    async def update_content(
        self, 
        content_id: str, 
        updates: Dict[str, Any]
    ) -> bool:
        """
Update indexed content"""
        try:
            content = self.indexed_content.get(content_id)
            if not content:
                return False
                
            # Update fields
            for field, value in updates.items():
                if hasattr(content, field):
                    setattr(content, field, value)
                    
            content.updated_at = datetime.now(timezone.utc)
            
            # Re-index in search engines
            await self._index_in_search_engines(content)
            
            logger.info(f"Content updated: {content_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to update content {content_id}: {e}")
            return False
            
    async def remove_content(self, content_id: str) -> bool:
        """Remove content from index"""
        try:
            if content_id not in self.indexed_content:
                return False
                
            # Remove from memory index
            content = self.indexed_content.pop(content_id)
            
            # Remove from search engines
            await self._remove_from_search_engines(content_id)
            
            # Update statistics
            self.index_stats["total_indexed"] -= 1
            content_type = content.content_type
            if content_type in self.index_stats["content_types"]:
                self.index_stats["content_types"][content_type] -= 1
                
            logger.info(f"Content removed from index: {content_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to remove content {content_id}: {e}")
            return False
            
    async def get_index_stats(self) -> Dict[str, Any]:
        """Get index statistics"""
        return {
            **self.index_stats,
            "index_size_mb": sum(content.file_size for content in self.indexed_content.values()) / (1024 * 1024),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
    async def health_check(self) -> Dict[str, Any]:
        """Index health check"""
        try:
            # Check search engines
            search_engines_status = {}
            
            if self.elasticsearch_client:
                try:
                    search_engines_status["elasticsearch"] = "healthy" if self.elasticsearch_client.ping() else "unhealthy"
                except Exception:
                    search_engines_status["elasticsearch"] = "unhealthy"
                    
            if self.whoosh_index:
                search_engines_status["whoosh"] = "healthy"
                
            if self.vector_index:
                search_engines_status["faiss"] = "healthy"
                
            # Check analyzer health
            analyzer_health = await self.analyzer.health_check()
            
            status = "healthy"
            if analyzer_health.get("status") != "healthy":
                status = "degraded"
                
            return {
                "status": status,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "search_engines": search_engines_status,
                "analyzer_health": analyzer_health,
                "index_stats": await self.get_index_stats()
            }
            
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
            
    # Private methods
    
    async def _initialize_search_engines(self):
        """Initialize search engines"""
        # Elasticsearch
        if self.elasticsearch_url and ELASTICSEARCH_AVAILABLE:
            try:
                self.elasticsearch_client = Elasticsearch([self.elasticsearch_url])
                logger.info("Elasticsearch client initialized")
            except Exception as e:
                logger.warning(f"Failed to initialize Elasticsearch: {e}")
                
        # Whoosh
        if WHOOSH_AVAILABLE and self.enable_text_search:
            try:
                whoosh_dir = self.index_directory / "whoosh"
                whoosh_dir.mkdir(exist_ok=True)
                
                schema = Schema(
                    content_id=ID(stored=True, unique=True),
                    title=TEXT(stored=True),
                    description=TEXT(stored=True),
                    tags=KEYWORD(stored=True, commas=True),
                    keywords=KEYWORD(stored=True, commas=True),
                    content_type=KEYWORD(stored=True),
                    user_id=KEYWORD(stored=True),
                    created_at=DATETIME(stored=True),
                    file_size=NUMERIC(stored=True)
                )
                
                if index.exists_in(str(whoosh_dir)):
                    self.whoosh_index = index.open_dir(str(whoosh_dir))
                else:
                    self.whoosh_index = index.create_in(str(whoosh_dir), schema)
                    
                logger.info("Whoosh index initialized")
            except Exception as e:
                logger.warning(f"Failed to initialize Whoosh: {e}")
                
        # FAISS vector index
        if FAISS_AVAILABLE and self.enable_vector_search:
            try:
                self.vector_index = faiss.IndexFlatIP(self.vector_dimension)
                logger.info("FAISS vector index initialized")
            except Exception as e:
                logger.warning(f"Failed to initialize FAISS: {e}")
                
    async def _index_in_search_engines(self, content: IndexedContent):
        """Index content in all search engines"""
        # Elasticsearch
        if self.elasticsearch_client:
            try:
                doc = asdict(content)
                doc["created_at"] = content.created_at.isoformat()
                doc["updated_at"] = content.updated_at.isoformat()
                doc["indexed_at"] = content.indexed_at.isoformat()
                
                self.elasticsearch_client.index(
                    index="multimedia_content",
                    id=content.content_id,
                    body=doc
                )
            except Exception as e:
                logger.error(f"Elasticsearch indexing failed: {e}")
                
        # Whoosh
        if self.whoosh_index:
            try:
                writer = self.whoosh_index.writer()
                writer.add_document(
                    content_id=content.content_id,
                    title=content.title or "",
                    description=content.description or "",
                    tags=",".join(content.tags),
                    keywords=",".join(content.keywords),
                    content_type=content.content_type,
                    user_id=content.user_id or "",
                    created_at=content.created_at,
                    file_size=content.file_size
                )
                writer.commit()
            except Exception as e:
                logger.error(f"Whoosh indexing failed: {e}")
                
        # FAISS vector index
        if self.vector_index and content.feature_vectors:
            try:
                # Use first available feature vector
                for vector_name, vector_data in content.feature_vectors.items():
                    if len(vector_data) == self.vector_dimension:
                        vector = np.array([vector_data], dtype=np.float32)
                        self.vector_index.add(vector)
                        break
            except Exception as e:
                logger.error(f"FAISS indexing failed: {e}")
                
    async def _remove_from_search_engines(self, content_id: str):
        """Remove content from search engines"""
        # Elasticsearch
        if self.elasticsearch_client:
            try:
                self.elasticsearch_client.delete(
                    index="multimedia_content",
                    id=content_id,
                    ignore=[404]
                )
            except Exception as e:
                logger.error(f"Elasticsearch removal failed: {e}")
                
        # Whoosh
        if self.whoosh_index:
            try:
                writer = self.whoosh_index.writer()
                writer.delete_by_term("content_id", content_id)
                writer.commit()
            except Exception as e:
                logger.error(f"Whoosh removal failed: {e}")
                
    async def _exact_search(self, query: SearchQuery) -> List[SearchResult]:
        """Perform exact text search"""
        results = []
        
        if not query.query_text:
            return results
            
        query_text = query.query_text.lower()
        
        for content_id, content in self.indexed_content.items():
            score = 0.0
            highlights = {}
            
            # Search in title
            if content.title and query_text in content.title.lower():
                score += 2.0
                highlights["title"] = [content.title]
                
            # Search in description
            if content.description and query_text in content.description.lower():
                score += 1.5
                highlights["description"] = [content.description[:200]]
                
            # Search in tags
            for tag in content.tags:
                if query_text in tag.lower():
                    score += 1.0
                    highlights.setdefault("tags", []).append(tag)
                    
            if score > 0:
                result = SearchResult(
                    content_id=content_id,
                    score=score,
                    content=content,
                    highlights=highlights
                )
                results.append(result)
                
        return results
        
    async def _fuzzy_search(self, query: SearchQuery) -> List[SearchResult]:
        """Perform fuzzy text search"""
        # This is a simplified implementation
        # In production, you would use proper fuzzy matching algorithms
        results = await self._exact_search(query)
        
        # Add partial matches with lower scores
        if query.query_text:
            words = query.query_text.lower().split()
            
            for content_id, content in self.indexed_content.items():
                if any(result.content_id == content_id for result in results):
                    continue
                    
                score = 0.0
                highlights = {}
                
                # Check for partial word matches
                text_fields = [
                    content.title or "",
                    content.description or "",
                    " ".join(content.tags),
                    " ".join(content.keywords)
                ]
                
                for field_name, field_text in zip(["title", "description", "tags", "keywords"], text_fields):
                    for word in words:
                        if len(word) > 2 and word in field_text.lower():
                            score += 0.5
                            highlights.setdefault(field_name, []).append(field_text[:100])
                            
                if score > 0:
                    result = SearchResult(
                        content_id=content_id,
                        score=score,
                        content=content,
                        highlights=highlights
                    )
                    results.append(result)
                    
        return results
        
    async def _semantic_search(self, query: SearchQuery) -> List[SearchResult]:
        """Perform semantic search"""
        results = []
        
        if not query.feature_vector:
            # If no feature vector provided, fall back to text search
            return await self._fuzzy_search(query)
            
        query_vector = np.array(query.feature_vector, dtype=np.float32)
        
        for content_id, content in self.indexed_content.items():
            if not content.feature_vectors:
                continue
                
            max_similarity = 0.0
            
            # Calculate similarity with each feature vector
            for vector_name, vector_data in content.feature_vectors.items():
                if len(vector_data) == len(query.feature_vector):
                    content_vector = np.array(vector_data, dtype=np.float32)
                    
                    # Cosine similarity
                    similarity = np.dot(query_vector, content_vector) / (
                        np.linalg.norm(query_vector) * np.linalg.norm(content_vector)
                    )
                    
                    max_similarity = max(max_similarity, similarity)
                    
            if max_similarity >= query.similarity_threshold:
                result = SearchResult(
                    content_id=content_id,
                    score=float(max_similarity),
                    content=content,
                    similarity_scores={"semantic": float(max_similarity)}
                )
                results.append(result)
                
        return results
        
    async def _similarity_search(self, query: SearchQuery) -> List[SearchResult]:
        """Perform similarity search using FAISS"""
        if not self.vector_index or not query.feature_vector:
            return []
            
        try:
            query_vector = np.array([query.feature_vector], dtype=np.float32)
            
            # Search similar vectors
            scores, indices = self.vector_index.search(query_vector, query.max_results)
            
            results = []
            content_list = list(self.indexed_content.values())
            
            for i, (score, idx) in enumerate(zip(scores[0], indices[0])):
                if idx < len(content_list) and score >= query.similarity_threshold:
                    content = content_list[idx]
                    result = SearchResult(
                        content_id=content.content_id,
                        score=float(score),
                        content=content,
                        similarity_scores={"vector": float(score)}
                    )
                    results.append(result)
                    
            return results
            
        except Exception as e:
            logger.error(f"FAISS similarity search failed: {e}")
            return []
            
    async def _hybrid_search(self, query: SearchQuery) -> List[SearchResult]:
        """Perform hybrid search combining multiple methods"""
        # Combine text and semantic search results
        text_results = await self._fuzzy_search(query)
        semantic_results = await self._semantic_search(query) if query.feature_vector else []
        
        # Merge results by content_id
        combined_results = {}
        
        # Add text search results
        for result in text_results:
            combined_results[result.content_id] = result
            
        # Add or merge semantic search results
        for result in semantic_results:
            if result.content_id in combined_results:
                # Combine scores
                existing = combined_results[result.content_id]
                existing.score = (existing.score + result.score) / 2
                existing.similarity_scores.update(result.similarity_scores)
            else:
                combined_results[result.content_id] = result
                
        return list(combined_results.values())
        
    def _apply_filters(self, results: List[SearchResult], query: SearchQuery) -> List[SearchResult]:
        """
Apply filters to search results"""
        filtered_results = results
        
        # Content type filter
        if query.content_types:
            filtered_results = [
                r for r in filtered_results 
                if r.content.content_type in query.content_types
            ]
            
        # Tags filter
        if query.tags:
            filtered_results = [
                r for r in filtered_results 
                if any(tag in r.content.tags for tag in query.tags)
            ]
            
        # Date range filter
        if query.date_range:
            start_date, end_date = query.date_range
            filtered_results = [
                r for r in filtered_results 
                if start_date <= r.content.created_at <= end_date
            ]
            
        # User filter
        if query.user_id:
            filtered_results = [
                r for r in filtered_results 
                if r.content.user_id == query.user_id
            ]
            
        # Additional filters
        for filter_key, filter_value in query.filters.items():
            if filter_key == "file_size_min":
                filtered_results = [
                    r for r in filtered_results 
                    if r.content.file_size >= filter_value
                ]
            elif filter_key == "file_size_max":
                filtered_results = [
                    r for r in filtered_results 
                    if r.content.file_size <= filter_value
                ]
                
        return filtered_results
        
    def _sort_results(self, results: List[SearchResult], query: SearchQuery) -> List[SearchResult]:
        """Sort search results"""
        if query.sort_by == "relevance":
            return sorted(results, key=lambda x: x.score, reverse=(query.sort_order == "desc"))
        elif query.sort_by == "date":
            return sorted(results, key=lambda x: x.content.created_at, reverse=(query.sort_order == "desc"))
        elif query.sort_by == "size":
            return sorted(results, key=lambda x: x.content.file_size, reverse=(query.sort_order == "desc"))
        elif query.sort_by == "title":
            return sorted(results, key=lambda x: x.content.title or "", reverse=(query.sort_order == "desc"))
        else:
            return results
            
    def _generate_facets(self, results: List[SearchResult]) -> Dict[str, Dict[str, int]]:
        """Generate facets for search results"""
        facets = {
            "content_types": {},
            "tags": {},
            "users": {}
        }
        
        for result in results:
            content = result.content
            
            # Content type facet
            content_type = content.content_type
            facets["content_types"][content_type] = facets["content_types"].get(content_type, 0) + 1
            
            # Tags facet
            for tag in content.tags:
                facets["tags"][tag] = facets["tags"].get(tag, 0) + 1
                
            # User facet
            if content.user_id:
                facets["users"][content.user_id] = facets["users"].get(content.user_id, 0) + 1
                
        return facets
        
    def _calculate_content_similarity(self, content1: IndexedContent, content2: IndexedContent) -> float:
        """Calculate similarity between two content items"""
        similarities = []
        
        # Feature vector similarity
        for vector_name in content1.feature_vectors:
            if vector_name in content2.feature_vectors:
                vec1 = np.array(content1.feature_vectors[vector_name])
                vec2 = np.array(content2.feature_vectors[vector_name])
                
                if len(vec1) == len(vec2):
                    # Cosine similarity
                    sim = np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2))
                    similarities.append(float(sim))
                    
        # Tag similarity
        tags1 = set(content1.tags)
        tags2 = set(content2.tags)
        if tags1 or tags2:
            tag_sim = len(tags1.intersection(tags2)) / len(tags1.union(tags2))
            similarities.append(tag_sim)
            
        # Content type match
        if content1.content_type == content2.content_type:
            similarities.append(1.0)
        else:
            similarities.append(0.0)
            
        return np.mean(similarities) if similarities else 0.0
        
    def _generate_content_id(self, file_path: str) -> str:
        """
Generate unique content ID"""
        # Use file path and modification time for uniqueness
        file_stat = Path(file_path).stat()
        content_string = f"{file_path}_{file_stat.st_mtime}_{file_stat.st_size}"
        return hashlib.md5(content_string.encode()).hexdigest()
        
    def _calculate_content_hash(self, file_path: str) -> str:
        """Calculate content hash"""
        hash_obj = hashlib.sha256()
        
        try:
            with open(file_path, 'rb') as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_obj.update(chunk)
            return hash_obj.hexdigest()
        except Exception as e:
            logger.error(f"Failed to calculate content hash: {e}")
            return ""
            
    def _update_index_stats(self, content: IndexedContent):
        """Update index statistics"""
        self.index_stats["total_indexed"] += 1
        self.index_stats["last_update"] = datetime.now(timezone.utc).isoformat()
        
        content_type = content.content_type
        if content_type not in self.index_stats["content_types"]:
            self.index_stats["content_types"][content_type] = 0
        self.index_stats["content_types"][content_type] += 1
        
    def _update_search_stats(self, processing_time: float):
        """Update search statistics"""
        self.index_stats["search_queries"] += 1
        
        # Update average search time
        total_queries = self.index_stats["search_queries"]
        current_avg = self.index_stats["average_search_time"]
        new_avg = ((current_avg * (total_queries - 1)) + processing_time) / total_queries
        self.index_stats["average_search_time"] = new_avg
        
    async def _load_existing_index(self):
        """Load existing index from storage"""
        # This would typically load from persistent storage
        # For now, this is a placeholder
        pass
