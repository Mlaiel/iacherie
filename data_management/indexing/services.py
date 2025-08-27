"""
IA Influencer Agent - Advanced Indexing Services
===============================================

Business logic layer for indexing operations with high-level services
for content indexing, search, vectors, and real-time processing.

Author: Fahed Mlaiel <mlaiel@live.de>
Project: IA Influencer Agent - Content Protection Platform

⚠️  INTELLECTUAL PROPERTY WARNING ⚠️
This code is the exclusive property of Fahed Mlaiel.
Any unauthorized use, copying, distribution, or reproduction
without explicit written permission is strictly prohibited.
Contact: mlaiel@live.de
"""

import asyncio
import logging
from typing import Dict, List, Optional, Union, Any, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
import uuid
import json
from pathlib import Path

from .engines import (
    VectorSearchEngine, ContentIndexEngine, 
    FingerprintIndexEngine, MetadataIndexEngine, IndexingConfig
)
from .processors import (
    MultiFormatProcessor, AudioIndexProcessor,
    VideoIndexProcessor, ImageIndexProcessor, TextIndexProcessor,
    ProcessingConfig
)
from .repositories import (
    IndexRepository, VectorRepository, FingerprintRepository, SearchRepository,
    IndexRecord, VectorRecord, FingerprintRecord, SearchQuery
)
from .strategies import (
    ContentIndexingStrategy, VectorEmbeddingStrategy,
    SimilaritySearchStrategy, RankingStrategy
)

logger = logging.getLogger(__name__)


@dataclass
class IndexingRequest:
    """Request structure for content indexing"""
    content_id: Optional[str] = None
    creator_id: str = ""
    file_path: Optional[str] = None
    content_data: Optional[Dict] = None
    content_type: Optional[str] = None
    title: str = ""
    description: str = ""
    tags: List[str] = None
    metadata: Dict[str, Any] = None
    protection_level: str = "standard"
    licensing_info: Optional[Dict] = None
    process_embeddings: bool = True
    generate_fingerprints: bool = True
    enable_realtime: bool = False


@dataclass
class IndexingResult:
    """Result structure for indexing operations"""
    content_id: str
    success: bool
    indexed_at: datetime
    processing_time_ms: int
    features_extracted: List[str]
    embeddings_generated: List[str]
    fingerprints_created: List[str]
    errors: List[str]
    warnings: List[str]
    metadata: Dict[str, Any]


@dataclass
class SearchRequest:
    """Request structure for search operations"""
    query_text: Optional[str] = None
    query_vector: Optional[List[float]] = None
    content_types: Optional[List[str]] = None
    creator_ids: Optional[List[str]] = None
    tags: Optional[List[str]] = None
    filters: Optional[Dict[str, Any]] = None
    similarity_threshold: float = 0.8
    limit: int = 50
    offset: int = 0
    sort_by: str = "relevance"
    include_vectors: bool = False
    include_fingerprints: bool = False
    enable_fuzzy: bool = True


@dataclass
class SearchResult:
    """Result structure for search operations"""
    results: List[Dict[str, Any]]
    total_count: int
    query_time_ms: int
    aggregations: Dict[str, Any]
    suggestions: List[str]
    similar_queries: List[str]


class IndexingService:
    """High-level service for content indexing operations"""
    
    def __init__(self, 
                 indexing_config: IndexingConfig,
                 processing_config: ProcessingConfig,
                 index_repo: IndexRepository,
                 vector_repo: VectorRepository,
                 fingerprint_repo: FingerprintRepository):
        
        self.config = indexing_config
        self.processing_config = processing_config
        self.index_repo = index_repo
        self.vector_repo = vector_repo
        self.fingerprint_repo = fingerprint_repo
        
        # Initialize engines
        self.content_engine = ContentIndexEngine(indexing_config)
        self.vector_engine = VectorSearchEngine(indexing_config)
        self.fingerprint_engine = FingerprintIndexEngine(indexing_config)
        self.metadata_engine = MetadataIndexEngine(indexing_config)
        
        # Initialize processor
        self.processor = MultiFormatProcessor(processing_config)
        
        # Initialize strategies
        self.indexing_strategy = ContentIndexingStrategy()
        self.embedding_strategy = VectorEmbeddingStrategy()
        
        self.logger = logging.getLogger(self.__class__.__name__)
        self._initialized = False
    
    async def initialize(self) -> None:
        """Initialize all components"""
        try:
            # Initialize engines
            await asyncio.gather(
                self.content_engine.initialize(),
                self.vector_engine.initialize(),
                self.fingerprint_engine.initialize(),
                self.metadata_engine.initialize()
            )
            
            # Initialize processor
            await self.processor.initialize()
            
            self._initialized = True
            self.logger.info("IndexingService initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize IndexingService: {e}")
            raise
    
    async def index_content(self, request: IndexingRequest) -> IndexingResult:
        """Index content with comprehensive feature extraction"""
        try:
            if not self._initialized:
                await self.initialize()
            
            start_time = datetime.now()
            
            # Generate content ID if not provided
            content_id = request.content_id or str(uuid.uuid4())
            
            result = IndexingResult(
                content_id=content_id,
                success=False,
                indexed_at=datetime.now(timezone.utc),
                processing_time_ms=0,
                features_extracted=[],
                embeddings_generated=[],
                fingerprints_created=[],
                errors=[],
                warnings=[],
                metadata={}
            )
            
            try:
                # Process content if file path provided
                processed_data = {}
                if request.file_path:
                    if not Path(request.file_path).exists():
                        raise FileNotFoundError(f"File not found: {request.file_path}")
                    
                    processed_data = await self.processor.process(
                        request.file_path, 
                        request.metadata or {}
                    )
                    result.features_extracted.append(processed_data.get("content_type", "unknown"))
                
                # Combine with provided content data
                if request.content_data:
                    processed_data.update(request.content_data)
                
                # Create index record
                index_record = IndexRecord(
                    content_id=content_id,
                    creator_id=request.creator_id,
                    content_type=request.content_type or processed_data.get("content_type", "unknown"),
                    title=request.title or processed_data.get("title", ""),
                    description=request.description or processed_data.get("description", ""),
                    tags=request.tags or [],
                    metadata={
                        **(request.metadata or {}),
                        **processed_data,
                        "file_path": request.file_path,
                        "processing_info": {
                            "indexed_at": datetime.now(timezone.utc).isoformat(),
                            "indexing_version": "2.0.0"
                        }
                    },
                    created_at=datetime.now(timezone.utc),
                    updated_at=datetime.now(timezone.utc),
                    indexed_at=datetime.now(timezone.utc),
                    protection_level=request.protection_level,
                    licensing_info=request.licensing_info
                )
                
                # Store in repository
                await self.index_repo.create(index_record)
                
                # Index in content engine
                await self.content_engine.index_content(content_id, {
                    "title": index_record.title,
                    "description": index_record.description,
                    "content_type": index_record.content_type,
                    "creator_id": index_record.creator_id,
                    "tags": index_record.tags,
                    "metadata": index_record.metadata,
                    "protection_level": index_record.protection_level
                })
                
                # Index in metadata engine
                await self.metadata_engine.index_content(content_id, index_record.metadata)
                
                # Generate embeddings if requested
                if request.process_embeddings:
                    embeddings_result = await self._generate_embeddings(
                        content_id, processed_data, index_record
                    )
                    result.embeddings_generated.extend(embeddings_result)
                
                # Generate fingerprints if requested
                if request.generate_fingerprints:
                    fingerprints_result = await self._generate_fingerprints(
                        content_id, processed_data, request.file_path
                    )
                    result.fingerprints_created.extend(fingerprints_result)
                
                # Apply indexing strategy optimizations
                await self.indexing_strategy.optimize_index(content_id, index_record)
                
                result.success = True
                result.metadata = processed_data
                
                self.logger.info(f"Successfully indexed content: {content_id}")
                
            except Exception as e:
                result.errors.append(str(e))
                self.logger.error(f"Failed to index content {content_id}: {e}")
            
            # Calculate processing time
            end_time = datetime.now()
            result.processing_time_ms = int((end_time - start_time).total_seconds() * 1000)
            
            return result
            
        except Exception as e:
            self.logger.error(f"Critical error in index_content: {e}")
            raise
    
    async def _generate_embeddings(self, content_id: str, processed_data: Dict, 
                                 index_record: IndexRecord) -> List[str]:
        """Generate embeddings for content"""
        try:
            embeddings_generated = []
            
            # Text embeddings
            searchable_text = processed_data.get("searchable_text", "")
            if not searchable_text:
                searchable_text = f"{index_record.title} {index_record.description} {' '.join(index_record.tags)}"
            
            if searchable_text.strip():
                text_embedding_result = await self.vector_engine.index_content(content_id, {
                    "text": searchable_text,
                    "metadata": {
                        "embedding_type": "text",
                        "content_type": index_record.content_type,
                        "creator_id": index_record.creator_id
                    }
                })
                
                if text_embedding_result.get("status") == "indexed":
                    # Store in repository
                    vector_record = VectorRecord(
                        vector_id=str(uuid.uuid4()),
                        content_id=content_id,
                        embedding=text_embedding_result.get("embedding", []),
                        embedding_type="text",
                        dimension=text_embedding_result.get("embedding_dimension", 768),
                        model_version="sentence-transformers/all-MiniLM-L6-v2",
                        similarity_threshold=0.8,
                        created_at=datetime.now(timezone.utc),
                        metadata={
                            "source_text": searchable_text[:500],  # First 500 chars
                            "content_type": index_record.content_type
                        }
                    )
                    
                    await self.vector_repo.create(vector_record)
                    embeddings_generated.append("text")
            
            # Content-specific embeddings
            content_type = processed_data.get("content_type", "")
            
            if content_type == "audio" and "audio_features" in processed_data:
                # Audio feature embeddings (simplified)
                audio_features = processed_data["audio_features"]
                audio_vector = await self._create_audio_embedding(audio_features)
                
                if audio_vector:
                    vector_record = VectorRecord(
                        vector_id=str(uuid.uuid4()),
                        content_id=content_id,
                        embedding=audio_vector,
                        embedding_type="audio_features",
                        dimension=len(audio_vector),
                        model_version="custom_audio_v1",
                        similarity_threshold=0.85,
                        created_at=datetime.now(timezone.utc),
                        metadata={"audio_features": audio_features}
                    )
                    
                    await self.vector_repo.create(vector_record)
                    embeddings_generated.append("audio_features")
            
            return embeddings_generated
            
        except Exception as e:
            self.logger.error(f"Failed to generate embeddings for {content_id}: {e}")
            return []
    
    async def _create_audio_embedding(self, audio_features: Dict) -> Optional[List[float]]:
        """Create embedding from audio features"""
        try:
            # Extract key audio features and create a simple embedding
            features = []
            
            # Add MFCC features
            for i in range(13):
                features.append(audio_features.get(f"mfcc_{i}_mean", 0.0))
                features.append(audio_features.get(f"mfcc_{i}_std", 0.0))
            
            # Add other features
            features.extend([
                audio_features.get("tempo", 0.0) / 200.0,  # Normalize
                audio_features.get("spectral_centroid_mean", 0.0) / 5000.0,
                audio_features.get("spectral_rolloff_mean", 0.0) / 10000.0,
                audio_features.get("zero_crossing_rate", 0.0),
                audio_features.get("rms_energy", 0.0)
            ])
            
            # Pad to fixed dimension
            target_dim = 32
            while len(features) < target_dim:
                features.append(0.0)
            
            return features[:target_dim]
            
        except Exception as e:
            self.logger.error(f"Failed to create audio embedding: {e}")
            return None
    
    async def _generate_fingerprints(self, content_id: str, processed_data: Dict, 
                                   file_path: Optional[str]) -> List[str]:
        """Generate fingerprints for content"""
        try:
            fingerprints_created = []
            
            if not file_path:
                return fingerprints_created
            
            # Generate fingerprints using engine
            fingerprint_result = await self.fingerprint_engine.index_content(content_id, {
                "content_type": processed_data.get("content_type", "unknown"),
                "file_path": file_path,
                "metadata": processed_data
            })
            
            if fingerprint_result.get("status") == "fingerprinted":
                fingerprints_created.append(fingerprint_result.get("content_type", "unknown"))
                
                # Store in repository (fingerprint data is already stored in engine)
                # We could retrieve and store in our repository if needed
            
            return fingerprints_created
            
        except Exception as e:
            self.logger.error(f"Failed to generate fingerprints for {content_id}: {e}")
            return []
    
    async def update_index(self, content_id: str, updates: Dict[str, Any]) -> bool:
        """Update existing index"""
        try:
            # Update in repository
            repo_updated = await self.index_repo.update(content_id, updates)
            
            if repo_updated:
                # Update in engines
                await self.content_engine.index_content(content_id, updates)
                await self.metadata_engine.index_content(content_id, updates)
                
                self.logger.info(f"Updated index for content: {content_id}")
                return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"Failed to update index for {content_id}: {e}")
            return False
    
    async def delete_index(self, content_id: str) -> bool:
        """Delete content from all indexes"""
        try:
            # Delete from all engines
            engine_results = await asyncio.gather(
                self.content_engine.delete_index(content_id),
                self.vector_engine.delete_index(content_id),
                self.fingerprint_engine.delete_index(content_id),
                self.metadata_engine.delete_index(content_id),
                return_exceptions=True
            )
            
            # Delete from repositories
            repo_results = await asyncio.gather(
                self.index_repo.delete(content_id),
                self._delete_vectors_by_content(content_id),
                self._delete_fingerprints_by_content(content_id),
                return_exceptions=True
            )
            
            success = any(engine_results) and any(repo_results)
            
            if success:
                self.logger.info(f"Deleted index for content: {content_id}")
            
            return success
            
        except Exception as e:
            self.logger.error(f"Failed to delete index for {content_id}: {e}")
            return False
    
    async def _delete_vectors_by_content(self, content_id: str) -> bool:
        """Delete all vectors for a content ID"""
        try:
            vectors = await self.vector_repo.get_by_content_id(content_id)
            
            for vector in vectors:
                await self.vector_repo.delete(vector.vector_id)
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to delete vectors for {content_id}: {e}")
            return False
    
    async def _delete_fingerprints_by_content(self, content_id: str) -> bool:
        """Delete all fingerprints for a content ID"""
        try:
            fingerprints = await self.fingerprint_repo.get_by_content_id(content_id)
            
            for fingerprint in fingerprints:
                await self.fingerprint_repo.delete(fingerprint.fingerprint_id)
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to delete fingerprints for {content_id}: {e}")
            return False
    
    async def get_indexing_stats(self, creator_id: Optional[str] = None) -> Dict[str, Any]:
        """Get indexing statistics"""
        try:
            stats = {
                "total_indexed": 0,
                "by_content_type": {},
                "by_creator": {},
                "recent_activity": [],
                "processing_stats": {
                    "avg_processing_time_ms": 0,
                    "total_processed": 0
                }
            }
            
            # Get content counts (simplified - would need more sophisticated aggregation)
            if creator_id:
                content_records = await self.index_repo.get_by_creator(creator_id, 1000)
            else:
                # Would need a method to get all content with pagination
                content_records = []
            
            stats["total_indexed"] = len(content_records)
            
            # Group by content type
            for record in content_records:
                content_type = record.content_type
                stats["by_content_type"][content_type] = stats["by_content_type"].get(content_type, 0) + 1
                
                creator = record.creator_id
                stats["by_creator"][creator] = stats["by_creator"].get(creator, 0) + 1
            
            # Recent activity (last 10 items)
            recent_records = sorted(content_records, key=lambda x: x.indexed_at, reverse=True)[:10]
            stats["recent_activity"] = [
                {
                    "content_id": record.content_id,
                    "title": record.title,
                    "content_type": record.content_type,
                    "indexed_at": record.indexed_at.isoformat()
                }
                for record in recent_records
            ]
            
            return stats
            
        except Exception as e:
            self.logger.error(f"Failed to get indexing stats: {e}")
            return {}


class SearchService:
    """High-level service for search operations"""
    
    def __init__(self,
                 indexing_config: IndexingConfig,
                 search_repo: SearchRepository,
                 index_repo: IndexRepository,
                 vector_repo: VectorRepository,
                 fingerprint_repo: FingerprintRepository):
        
        self.config = indexing_config
        self.search_repo = search_repo
        self.index_repo = index_repo
        self.vector_repo = vector_repo
        self.fingerprint_repo = fingerprint_repo
        
        # Initialize engines
        self.content_engine = ContentIndexEngine(indexing_config)
        self.vector_engine = VectorSearchEngine(indexing_config)
        
        # Initialize strategies
        self.search_strategy = SimilaritySearchStrategy()
        self.ranking_strategy = RankingStrategy()
        
        self.logger = logging.getLogger(self.__class__.__name__)
        self._initialized = False
    
    async def initialize(self) -> None:
        """Initialize search components"""
        try:
            await asyncio.gather(
                self.content_engine.initialize(),
                self.vector_engine.initialize()
            )
            
            self._initialized = True
            self.logger.info("SearchService initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize SearchService: {e}")
            raise
    
    async def search(self, request: SearchRequest) -> SearchResult:
        """Perform comprehensive search"""
        try:
            if not self._initialized:
                await self.initialize()
            
            start_time = datetime.now()
            
            # Convert to internal query format
            search_query = SearchQuery(
                query_text=request.query_text,
                vector_query=request.query_vector,
                content_types=request.content_types,
                creator_ids=request.creator_ids,
                tags=request.tags,
                filters=request.filters,
                similarity_threshold=request.similarity_threshold,
                limit=request.limit,
                offset=request.offset,
                sort_by=request.sort_by
            )
            
            # Perform unified search
            search_results = await self.search_repo.unified_search(search_query)
            
            # Combine and rank results
            combined_results = []
            
            # Add text search results
            for result in search_results.get("text_results", []):
                result["search_type"] = "text"
                result["relevance_score"] = 1.0  # Default score
                combined_results.append(result)
            
            # Add vector search results
            for result in search_results.get("vector_results", []):
                result["search_type"] = "vector"
                combined_results.append(result)
            
            # Apply ranking strategy
            ranked_results = await self.ranking_strategy.rank_results(
                combined_results, request
            )
            
            # Generate aggregations
            aggregations = await self._generate_aggregations(ranked_results)
            
            # Generate suggestions
            suggestions = await self._generate_suggestions(request.query_text)
            
            # Calculate query time
            end_time = datetime.now()
            query_time_ms = int((end_time - start_time).total_seconds() * 1000)
            
            result = SearchResult(
                results=ranked_results,
                total_count=len(ranked_results),
                query_time_ms=query_time_ms,
                aggregations=aggregations,
                suggestions=suggestions,
                similar_queries=[]
            )
            
            self.logger.info(f"Search completed: {len(ranked_results)} results in {query_time_ms}ms")
            
            return result
            
        except Exception as e:
            self.logger.error(f"Failed to perform search: {e}")
            return SearchResult(
                results=[],
                total_count=0,
                query_time_ms=0,
                aggregations={},
                suggestions=[],
                similar_queries=[]
            )
    
    async def _generate_aggregations(self, results: List[Dict]) -> Dict[str, Any]:
        """Generate aggregations from search results"""
        try:
            aggregations = {
                "content_types": {},
                "creators": {},
                "tags": {},
                "protection_levels": {}
            }
            
            for result in results:
                # Content types
                content_type = result.get("content_type", "unknown")
                aggregations["content_types"][content_type] = aggregations["content_types"].get(content_type, 0) + 1
                
                # Creators
                creator_id = result.get("creator_id", "unknown")
                aggregations["creators"][creator_id] = aggregations["creators"].get(creator_id, 0) + 1
                
                # Tags
                for tag in result.get("tags", []):
                    aggregations["tags"][tag] = aggregations["tags"].get(tag, 0) + 1
                
                # Protection levels
                protection_level = result.get("protection_level", "standard")
                aggregations["protection_levels"][protection_level] = aggregations["protection_levels"].get(protection_level, 0) + 1
            
            return aggregations
            
        except Exception as e:
            self.logger.error(f"Failed to generate aggregations: {e}")
            return {}
    
    async def _generate_suggestions(self, query_text: Optional[str]) -> List[str]:
        """Generate search suggestions"""
        try:
            if not query_text:
                return []
            
            suggestions = []
            
            # Simple word-based suggestions (could be enhanced with ML)
            words = query_text.lower().split()
            
            # Add related terms (this would be enhanced with a proper thesaurus/ML model)
            related_terms = {
                "music": ["audio", "song", "track", "melody"],
                "video": ["clip", "movie", "footage", "recording"],
                "image": ["photo", "picture", "graphic", "visual"],
                "text": ["document", "article", "content", "writing"]
            }
            
            for word in words:
                if word in related_terms:
                    for related in related_terms[word]:
                        suggestion = query_text.replace(word, related)
                        if suggestion != query_text:
                            suggestions.append(suggestion)
            
            return suggestions[:5]  # Limit to 5 suggestions
            
        except Exception as e:
            self.logger.error(f"Failed to generate suggestions: {e}")
            return []
    
    async def find_similar_content(self, content_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Find content similar to the given content"""
        try:
            return await self.search_repo.find_duplicate_content(content_id)
            
        except Exception as e:
            self.logger.error(f"Failed to find similar content for {content_id}: {e}")
            return []
    
    async def get_recommendations(self, content_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Get content recommendations"""
        try:
            return await self.search_repo.get_content_recommendations(content_id, limit)
            
        except Exception as e:
            self.logger.error(f"Failed to get recommendations for {content_id}: {e}")
            return []


class VectorService:
    """Specialized service for vector operations"""
    
    def __init__(self, 
                 indexing_config: IndexingConfig,
                 vector_repo: VectorRepository,
                 vector_engine: VectorSearchEngine):
        
        self.config = indexing_config
        self.vector_repo = vector_repo
        self.vector_engine = vector_engine
        self.embedding_strategy = VectorEmbeddingStrategy()
        
        self.logger = logging.getLogger(self.__class__.__name__)
    
    async def create_embedding(self, content_id: str, text: str, 
                             embedding_type: str = "text") -> Optional[str]:
        """Create text embedding for content"""
        try:
            # Generate embedding using engine
            result = await self.vector_engine.index_content(content_id, {
                "text": text,
                "metadata": {"embedding_type": embedding_type}
            })
            
            if result.get("status") == "indexed":
                # Store in repository
                vector_record = VectorRecord(
                    vector_id=str(uuid.uuid4()),
                    content_id=content_id,
                    embedding=result.get("embedding", []),
                    embedding_type=embedding_type,
                    dimension=result.get("embedding_dimension", 768),
                    model_version="sentence-transformers/all-MiniLM-L6-v2",
                    similarity_threshold=0.8,
                    created_at=datetime.now(timezone.utc),
                    metadata={"source_text": text[:500]}
                )
                
                vector_id = await self.vector_repo.create(vector_record)
                return vector_id
            
            return None
            
        except Exception as e:
            self.logger.error(f"Failed to create embedding for {content_id}: {e}")
            return None
    
    async def similarity_search_by_text(self, query_text: str, 
                                      top_k: int = 10) -> List[Dict[str, Any]]:
        """Perform similarity search using text query"""
        try:
            # Generate query embedding
            query_result = await self.vector_engine._generate_embedding(query_text)
            
            if query_result is None:
                return []
            
            # Perform similarity search
            similar_vectors = await self.vector_repo.similarity_search(
                query_result.tolist(), top_k
            )
            
            results = []
            for vector_id, similarity in similar_vectors:
                vector_record = await self.vector_repo.get_by_id(vector_id)
                if vector_record:
                    result = asdict(vector_record)
                    result["similarity_score"] = similarity
                    results.append(result)
            
            return results
            
        except Exception as e:
            self.logger.error(f"Failed to perform similarity search: {e}")
            return []
    
    async def get_content_vectors(self, content_id: str) -> List[VectorRecord]:
        """Get all vectors for a content ID"""
        try:
            return await self.vector_repo.get_by_content_id(content_id)
            
        except Exception as e:
            self.logger.error(f"Failed to get vectors for {content_id}: {e}")
            return []


class RealtimeIndexService:
    """Service for real-time indexing and updates"""
    
    def __init__(self, indexing_service: IndexingService):
        self.indexing_service = indexing_service
        self.pending_operations = asyncio.Queue()
        self.worker_tasks = []
        self.logger = logging.getLogger(self.__class__.__name__)
        self._running = False
    
    async def start(self, num_workers: int = 3) -> None:
        """Start real-time processing workers"""
        try:
            self._running = True
            
            # Start worker tasks
            for i in range(num_workers):
                task = asyncio.create_task(self._process_worker(f"worker-{i}"))
                self.worker_tasks.append(task)
            
            self.logger.info(f"Started {num_workers} real-time indexing workers")
            
        except Exception as e:
            self.logger.error(f"Failed to start real-time service: {e}")
            raise
    
    async def stop(self) -> None:
        """Stop real-time processing"""
        try:
            self._running = False
            
            # Cancel all worker tasks
            for task in self.worker_tasks:
                task.cancel()
            
            # Wait for tasks to complete
            await asyncio.gather(*self.worker_tasks, return_exceptions=True)
            
            self.worker_tasks.clear()
            
            self.logger.info("Stopped real-time indexing service")
            
        except Exception as e:
            self.logger.error(f"Failed to stop real-time service: {e}")
    
    async def queue_indexing(self, request: IndexingRequest) -> None:
        """Queue content for real-time indexing"""
        try:
            await self.pending_operations.put(("index", request))
            self.logger.debug(f"Queued indexing for content: {request.content_id}")
            
        except Exception as e:
            self.logger.error(f"Failed to queue indexing: {e}")
    
    async def queue_update(self, content_id: str, updates: Dict[str, Any]) -> None:
        """Queue content update"""
        try:
            await self.pending_operations.put(("update", (content_id, updates)))
            self.logger.debug(f"Queued update for content: {content_id}")
            
        except Exception as e:
            self.logger.error(f"Failed to queue update: {e}")
    
    async def queue_deletion(self, content_id: str) -> None:
        """Queue content deletion"""
        try:
            await self.pending_operations.put(("delete", content_id))
            self.logger.debug(f"Queued deletion for content: {content_id}")
            
        except Exception as e:
            self.logger.error(f"Failed to queue deletion: {e}")
    
    async def _process_worker(self, worker_id: str) -> None:
        """Process queued operations"""
        self.logger.info(f"Started real-time worker: {worker_id}")
        
        while self._running:
            try:
                # Get operation from queue with timeout
                operation_type, operation_data = await asyncio.wait_for(
                    self.pending_operations.get(),
                    timeout=1.0
                )
                
                start_time = datetime.now()
                
                try:
                    if operation_type == "index":
                        result = await self.indexing_service.index_content(operation_data)
                        if result.success:
                            self.logger.debug(
                                f"{worker_id}: Indexed {result.content_id} "
                                f"in {result.processing_time_ms}ms"
                            )
                        else:
                            self.logger.warning(
                                f"{worker_id}: Failed to index {result.content_id}: "
                                f"{result.errors}"
                            )
                    
                    elif operation_type == "update":
                        content_id, updates = operation_data
                        success = await self.indexing_service.update_index(content_id, updates)
                        if success:
                            self.logger.debug(f"{worker_id}: Updated {content_id}")
                        else:
                            self.logger.warning(f"{worker_id}: Failed to update {content_id}")
                    
                    elif operation_type == "delete":
                        content_id = operation_data
                        success = await self.indexing_service.delete_index(content_id)
                        if success:
                            self.logger.debug(f"{worker_id}: Deleted {content_id}")
                        else:
                            self.logger.warning(f"{worker_id}: Failed to delete {content_id}")
                
                except Exception as e:
                    self.logger.error(f"{worker_id}: Operation failed: {e}")
                
                finally:
                    # Mark task as done
                    self.pending_operations.task_done()
                
            except asyncio.TimeoutError:
                # No operations in queue, continue
                continue
            except asyncio.CancelledError:
                # Worker cancelled
                break
            except Exception as e:
                self.logger.error(f"{worker_id}: Unexpected error: {e}")
        
        self.logger.info(f"Stopped real-time worker: {worker_id}")
    
    async def get_queue_status(self) -> Dict[str, Any]:
        """Get queue status information"""
        return {
            "pending_operations": self.pending_operations.qsize(),
            "active_workers": len([t for t in self.worker_tasks if not t.done()]),
            "total_workers": len(self.worker_tasks),
            "is_running": self._running
        }
