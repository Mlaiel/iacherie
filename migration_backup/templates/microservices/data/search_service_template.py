"""
⚠️ AVERTISSEMENT LÉGAL OBLIGATOIRE:
==========================================
© 2025 Fahed Mlaiel <mlaiel@live.de>
TOUS DROITS RÉSERVÉS

🚨 PROTECTION INTELLECTUELLE:
- Code propriétaire de Fahed Mlaiel
- Utilisation commerciale INTERDITE sans autorisation écrite
- Reverse engineering STRICTEMENT INTERDIT
- Distribution INTERDITE sans licence explicite
- Violation = Poursuites judiciaires automatiques

Search Service Template for Ainflue Creator Economy Platform
Enterprise search service with Elasticsearch, advanced analytics and AI-powered recommendations
"""

import asyncio
import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field
from enum import Enum
import hashlib

from fastapi import FastAPI, HTTPException, Query, BackgroundTasks
from pydantic import BaseModel, validator
from elasticsearch import AsyncElasticsearch
import redis.asyncio as redis
import logging
from prometheus_client import Counter, Histogram, Gauge


class SearchProvider(str, Enum):
    ELASTICSEARCH = "elasticsearch"
    OPENSEARCH = "opensearch"
    SOLR = "solr"
    MEILISEARCH = "meilisearch"


class IndexType(str, Enum):
    CREATORS = "creators"
    CONTENT = "content"
    COLLABORATIONS = "collaborations"
    ANALYTICS = "analytics"
    USERS = "users"
    TAGS = "tags"
    CATEGORIES = "categories"


class SearchType(str, Enum):
    SIMPLE = "simple"
    ADVANCED = "advanced"
    FUZZY = "fuzzy"
    SEMANTIC = "semantic"
    AGGREGATION = "aggregation"
    AUTOCOMPLETE = "autocomplete"
    SIMILARITY = "similarity"


class SortOrder(str, Enum):
    ASC = "asc"
    DESC = "desc"


@dataclass
class SearchConfig:
    """Configuration du service de recherche"""
    # Elasticsearch configuration
    elasticsearch_hosts: List[str] = field(default_factory=lambda: ["http://localhost:9200"])
    elasticsearch_username: Optional[str] = None
    elasticsearch_password: Optional[str] = None
    elasticsearch_api_key: Optional[str] = None
    
    # Index settings
    default_shards: int = 1
    default_replicas: int = 1
    refresh_interval: str = "1s"
    max_result_window: int = 10000
    
    # Search optimization
    enable_caching: bool = True
    cache_ttl_seconds: int = 300
    enable_query_optimization: bool = True
    enable_autocomplete: bool = True
    
    # Analytics and monitoring
    enable_search_analytics: bool = True
    enable_performance_monitoring: bool = True
    slow_query_threshold_ms: int = 1000
    
    # AI/ML features
    enable_semantic_search: bool = True
    enable_personalization: bool = True
    enable_recommendations: bool = True
    
    # Security
    enable_query_validation: bool = True
    max_query_complexity: int = 100
    rate_limit_per_minute: int = 1000


class SearchQuery(BaseModel):
    """Requête de recherche"""
    query: str
    index_type: IndexType = IndexType.CONTENT
    search_type: SearchType = SearchType.SIMPLE
    
    # Filtering
    filters: Dict[str, Any] = {}
    date_range: Optional[Dict[str, str]] = None
    
    # Pagination
    page: int = 1
    size: int = 20
    
    # Sorting
    sort_by: Optional[str] = None
    sort_order: SortOrder = SortOrder.DESC
    
    # Advanced options
    highlight: bool = True
    include_aggregations: bool = False
    include_suggestions: bool = False
    fuzzy_threshold: float = 0.8
    
    # Personalization
    user_id: Optional[str] = None
    user_preferences: Dict[str, Any] = {}


class SearchResult(BaseModel):
    """Résultat de recherche"""
    query: str
    total_hits: int
    execution_time_ms: float
    page: int
    size: int
    
    # Results
    hits: List[Dict[str, Any]] = []
    
    # Enhancements
    highlights: Dict[str, List[str]] = {}
    aggregations: Dict[str, Any] = {}
    suggestions: List[str] = []
    
    # Analytics
    search_id: str
    timestamp: datetime


class IndexDocument(BaseModel):
    """Document à indexer"""
    id: str
    index_type: IndexType
    data: Dict[str, Any]
    tags: List[str] = []
    metadata: Dict[str, Any] = {}


class SearchAnalytics(BaseModel):
    """Analytics de recherche"""
    total_searches: int = 0
    successful_searches: int = 0
    failed_searches: int = 0
    average_response_time_ms: float = 0.0
    top_queries: List[Dict[str, Any]] = []
    top_indices: List[Dict[str, Any]] = []
    search_trends: Dict[str, Any] = {}


class SearchServiceTemplate:
    """
    Template de service de recherche enterprise pour Ainflue
    
    Fonctionnalités:
    - Multi-provider search (Elasticsearch, OpenSearch, etc.)
    - Advanced search capabilities (fuzzy, semantic, aggregations)
    - Real-time indexing avec optimizations
    - Search analytics et monitoring
    - AI-powered recommendations
    - Autocomplete intelligent
    - Personalization et user preferences
    - Performance optimization
    - Security et rate limiting
    """
    
    def __init__(self, config: SearchConfig = None):
        self.config = config or SearchConfig()
        self.app = FastAPI(
            title="Ainflue Search Service",
            description="Enterprise search service with AI-powered capabilities",
            version="1.0.0"
        )
        
        # Search client
        self.es_client: Optional[AsyncElasticsearch] = None
        
        # Redis pour cache
        self.redis = redis.Redis(host='localhost', port=6379, db=9, decode_responses=True)
        
        # Analytics storage
        self.search_analytics = SearchAnalytics()
        self.query_cache: Dict[str, Any] = {}
        
        # Index mappings
        self.index_mappings = self._get_index_mappings()
        
        # Métriques Prometheus
        self.search_requests = Counter('search_requests_total', ['index_type', 'search_type', 'status'])
        self.search_duration = Histogram('search_duration_seconds', ['index_type', 'search_type'])
        self.indexing_operations = Counter('search_indexing_operations_total', ['index_type', 'operation'])
        self.index_size = Gauge('search_index_size_documents', ['index_type'])
        self.cache_hit_ratio = Gauge('search_cache_hit_ratio')
        
        # Setup
        asyncio.create_task(self._initialize_elasticsearch())
        self._setup_routes()
        self._start_background_tasks()
        
        # Logger
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)

    async def _initialize_elasticsearch(self):
        """Initialisation d'Elasticsearch"""
        try:
            # Configuration client
            client_config = {
                "hosts": self.config.elasticsearch_hosts,
                "verify_certs": False,
                "request_timeout": 30
            }
            
            if self.config.elasticsearch_username and self.config.elasticsearch_password:
                client_config["basic_auth"] = (
                    self.config.elasticsearch_username,
                    self.config.elasticsearch_password
                )
            elif self.config.elasticsearch_api_key:
                client_config["api_key"] = self.config.elasticsearch_api_key
            
            self.es_client = AsyncElasticsearch(**client_config)
            
            # Test connection
            await self.es_client.ping()
            
            # Créer indices si nécessaire
            await self._ensure_indices_exist()
            
            self.logger.info("Elasticsearch client initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize Elasticsearch: {str(e)}")
            raise

    def _get_index_mappings(self) -> Dict[str, Dict]:
        """Mappings des indices Elasticsearch"""
        return {
            IndexType.CREATORS.value: {
                "properties": {
                    "id": {"type": "keyword"},
                    "name": {"type": "text", "analyzer": "standard"},
                    "username": {"type": "keyword"},
                    "bio": {"type": "text"},
                    "avatar_url": {"type": "keyword"},
                    "follower_count": {"type": "integer"},
                    "content_count": {"type": "integer"},
                    "verification_status": {"type": "keyword"},
                    "category": {"type": "keyword"},
                    "tags": {"type": "keyword"},
                    "location": {"type": "geo_point"},
                    "created_at": {"type": "date"},
                    "updated_at": {"type": "date"},
                    "engagement_score": {"type": "float"},
                    "search_vector": {"type": "dense_vector", "dims": 384}  # Pour semantic search
                }
            },
            IndexType.CONTENT.value: {
                "properties": {
                    "id": {"type": "keyword"},
                    "title": {"type": "text", "analyzer": "standard"},
                    "description": {"type": "text"},
                    "content_type": {"type": "keyword"},
                    "creator_id": {"type": "keyword"},
                    "creator_name": {"type": "text"},
                    "duration": {"type": "integer"},
                    "file_size": {"type": "long"},
                    "thumbnail_url": {"type": "keyword"},
                    "view_count": {"type": "integer"},
                    "like_count": {"type": "integer"},
                    "comment_count": {"type": "integer"},
                    "share_count": {"type": "integer"},
                    "category": {"type": "keyword"},
                    "tags": {"type": "keyword"},
                    "language": {"type": "keyword"},
                    "published_at": {"type": "date"},
                    "updated_at": {"type": "date"},
                    "quality_score": {"type": "float"},
                    "engagement_rate": {"type": "float"},
                    "monetization_enabled": {"type": "boolean"},
                    "content_vector": {"type": "dense_vector", "dims": 384}
                }
            },
            IndexType.COLLABORATIONS.value: {
                "properties": {
                    "id": {"type": "keyword"},
                    "title": {"type": "text"},
                    "description": {"type": "text"},
                    "creator_ids": {"type": "keyword"},
                    "status": {"type": "keyword"},
                    "collaboration_type": {"type": "keyword"},
                    "deadline": {"type": "date"},
                    "budget": {"type": "float"},
                    "requirements": {"type": "text"},
                    "skills_required": {"type": "keyword"},
                    "created_at": {"type": "date"},
                    "updated_at": {"type": "date"}
                }
            }
        }

    async def _ensure_indices_exist(self):
        """S'assurer que tous les indices existent"""
        for index_type, mapping in self.index_mappings.items():
            index_name = f"ainflue_{index_type}"
            
            try:
                exists = await self.es_client.indices.exists(index=index_name)
                
                if not exists:
                    index_settings = {
                        "settings": {
                            "number_of_shards": self.config.default_shards,
                            "number_of_replicas": self.config.default_replicas,
                            "refresh_interval": self.config.refresh_interval,
                            "max_result_window": self.config.max_result_window,
                            "analysis": {
                                "analyzer": {
                                    "autocomplete": {
                                        "tokenizer": "autocomplete",
                                        "filter": ["lowercase"]
                                    }
                                },
                                "tokenizer": {
                                    "autocomplete": {
                                        "type": "edge_ngram",
                                        "min_gram": 2,
                                        "max_gram": 10,
                                        "token_chars": ["letter", "digit"]
                                    }
                                }
                            }
                        },
                        "mappings": mapping
                    }
                    
                    await self.es_client.indices.create(
                        index=index_name,
                        body=index_settings
                    )
                    
                    self.logger.info(f"Created index: {index_name}")
                
            except Exception as e:
                self.logger.error(f"Failed to create index {index_name}: {str(e)}")

    def _start_background_tasks(self):
        """Démarre les tâches en arrière-plan"""
        # Analytics collection
        if self.config.enable_search_analytics:
            asyncio.create_task(self._analytics_collection_loop())
        
        # Index optimization
        asyncio.create_task(self._index_optimization_loop())

    def _setup_routes(self):
        """Configuration des routes du service"""
        
        @self.app.post("/search", response_model=SearchResult)
        async def search_documents(query: SearchQuery):
            """Rechercher dans les documents"""
            search_id = f"search_{int(time.time())}_{hashlib.md5(query.query.encode()).hexdigest()[:8]}"
            
            with self.search_duration.labels(
                index_type=query.index_type.value,
                search_type=query.search_type.value
            ).time():
                
                start_time = time.time()
                
                try:
                    # Validation de sécurité
                    if self.config.enable_query_validation:
                        await self._validate_search_query(query)
                    
                    # Vérifier cache
                    cached_result = None
                    if self.config.enable_caching:
                        cached_result = await self._get_cached_result(query)
                        if cached_result:
                            execution_time = (time.time() - start_time) * 1000
                            cached_result.execution_time_ms = execution_time
                            cached_result.search_id = search_id
                            return cached_result
                    
                    # Construire requête Elasticsearch
                    es_query = await self._build_elasticsearch_query(query)
                    
                    # Exécuter recherche
                    index_name = f"ainflue_{query.index_type.value}"
                    response = await self.es_client.search(
                        index=index_name,
                        body=es_query,
                        request_timeout=30
                    )
                    
                    execution_time = (time.time() - start_time) * 1000
                    
                    # Traiter résultats
                    result = await self._process_search_response(
                        response, query, execution_time, search_id
                    )
                    
                    # Cache le résultat
                    if self.config.enable_caching and not cached_result:
                        await self._cache_search_result(query, result)
                    
                    # Analytics
                    await self._track_search_analytics(query, result, execution_time)
                    
                    # Métriques
                    self.search_requests.labels(
                        index_type=query.index_type.value,
                        search_type=query.search_type.value,
                        status="success"
                    ).inc()
                    
                    # Log slow queries
                    if execution_time > self.config.slow_query_threshold_ms:
                        self.logger.warning(f"Slow search query: {execution_time:.2f}ms - {query.query}")
                    
                    return result
                    
                except Exception as e:
                    execution_time = (time.time() - start_time) * 1000
                    
                    self.search_requests.labels(
                        index_type=query.index_type.value,
                        search_type=query.search_type.value,
                        status="error"
                    ).inc()
                    
                    self.logger.error(f"Search error: {str(e)} - Query: {query.query}")
                    raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")

        @self.app.post("/index/document")
        async def index_document(document: IndexDocument, background_tasks: BackgroundTasks):
            """Indexer un document"""
            try:
                index_name = f"ainflue_{document.index_type.value}"
                
                # Préparer document pour indexation
                doc_body = {
                    **document.data,
                    "tags": document.tags,
                    "metadata": document.metadata,
                    "indexed_at": datetime.utcnow().isoformat()
                }
                
                # Indexer dans Elasticsearch
                await self.es_client.index(
                    index=index_name,
                    id=document.id,
                    body=doc_body,
                    refresh="wait_for"
                )
                
                # Mise à jour des métriques
                self.indexing_operations.labels(
                    index_type=document.index_type.value,
                    operation="index"
                ).inc()
                
                # Tasks en arrière-plan
                if self.config.enable_semantic_search:
                    background_tasks.add_task(self._generate_search_vector, document)
                
                return {
                    "success": True,
                    "document_id": document.id,
                    "index": index_name
                }
                
            except Exception as e:
                self.indexing_operations.labels(
                    index_type=document.index_type.value,
                    operation="error"
                ).inc()
                self.logger.error(f"Indexing error: {str(e)}")
                raise HTTPException(status_code=500, detail=f"Indexing failed: {str(e)}")

        @self.app.delete("/index/document/{index_type}/{document_id}")
        async def delete_document(index_type: IndexType, document_id: str):
            """Supprimer un document de l'index"""
            try:
                index_name = f"ainflue_{index_type.value}"
                
                response = await self.es_client.delete(
                    index=index_name,
                    id=document_id,
                    refresh="wait_for"
                )
                
                self.indexing_operations.labels(
                    index_type=index_type.value,
                    operation="delete"
                ).inc()
                
                return {
                    "success": True,
                    "document_id": document_id,
                    "result": response["result"]
                }
                
            except Exception as e:
                self.logger.error(f"Document deletion error: {str(e)}")
                raise HTTPException(status_code=500, detail=f"Deletion failed: {str(e)}")

        @self.app.get("/autocomplete/{index_type}")
        async def autocomplete_suggestions(
            index_type: IndexType,
            query: str = Query(..., min_length=2),
            limit: int = Query(10, le=50)
        ):
            """Suggestions d'autocomplétion"""
            if not self.config.enable_autocomplete:
                raise HTTPException(status_code=501, detail="Autocomplete not enabled")
            
            try:
                suggestions = await self._get_autocomplete_suggestions(index_type, query, limit)
                return {"suggestions": suggestions}
                
            except Exception as e:
                self.logger.error(f"Autocomplete error: {str(e)}")
                raise HTTPException(status_code=500, detail=f"Autocomplete failed: {str(e)}")

        @self.app.get("/recommendations/{user_id}")
        async def get_recommendations(
            user_id: str,
            index_type: IndexType = IndexType.CONTENT,
            limit: int = Query(20, le=100)
        ):
            """Recommandations personnalisées"""
            if not self.config.enable_recommendations:
                raise HTTPException(status_code=501, detail="Recommendations not enabled")
            
            try:
                recommendations = await self._get_personalized_recommendations(
                    user_id, index_type, limit
                )
                return {"recommendations": recommendations}
                
            except Exception as e:
                self.logger.error(f"Recommendations error: {str(e)}")
                raise HTTPException(status_code=500, detail=f"Recommendations failed: {str(e)}")

        @self.app.get("/analytics")
        async def get_search_analytics(days_back: int = Query(7, le=30)):
            """Analytics de recherche"""
            try:
                analytics = await self._generate_search_analytics(days_back)
                return analytics
                
            except Exception as e:
                self.logger.error(f"Analytics error: {str(e)}")
                raise HTTPException(status_code=500, detail=f"Analytics failed: {str(e)}")

        @self.app.post("/index/reindex/{index_type}")
        async def reindex_data(index_type: IndexType, background_tasks: BackgroundTasks):
            """Réindexer toutes les données d'un type"""
            try:
                background_tasks.add_task(self._reindex_background, index_type)
                
                return {
                    "success": True,
                    "message": f"Reindexing started for {index_type.value}",
                    "index_type": index_type.value
                }
                
            except Exception as e:
                self.logger.error(f"Reindex error: {str(e)}")
                raise HTTPException(status_code=500, detail=f"Reindex failed: {str(e)}")

        @self.app.get("/health")
        async def get_search_health():
            """Health check du service de recherche"""
            try:
                # Test Elasticsearch connection
                es_health = await self.es_client.cluster.health()
                
                # Test Redis connection
                redis_ping = await self.redis.ping()
                
                # Collect index stats
                index_stats = {}
                for index_type in IndexType:
                    index_name = f"ainflue_{index_type.value}"
                    try:
                        stats = await self.es_client.indices.stats(index=index_name)
                        index_stats[index_type.value] = {
                            "document_count": stats["indices"][index_name]["total"]["docs"]["count"],
                            "size_mb": stats["indices"][index_name]["total"]["store"]["size_in_bytes"] / 1024 / 1024
                        }
                    except:
                        index_stats[index_type.value] = {"status": "not_found"}
                
                return {
                    "status": "healthy",
                    "timestamp": datetime.utcnow().isoformat(),
                    "elasticsearch": {
                        "status": es_health["status"],
                        "cluster_name": es_health["cluster_name"],
                        "active_shards": es_health["active_shards"]
                    },
                    "redis": "connected" if redis_ping else "disconnected",
                    "indices": index_stats,
                    "analytics": {
                        "total_searches": self.search_analytics.total_searches,
                        "success_rate": (self.search_analytics.successful_searches / 
                                       max(self.search_analytics.total_searches, 1) * 100),
                        "avg_response_time": self.search_analytics.average_response_time_ms
                    }
                }
                
            except Exception as e:
                return {
                    "status": "unhealthy",
                    "error": str(e),
                    "timestamp": datetime.utcnow().isoformat()
                }

    async def _build_elasticsearch_query(self, query: SearchQuery) -> Dict[str, Any]:
        """Construire requête Elasticsearch"""
        es_query = {
            "from": (query.page - 1) * query.size,
            "size": query.size,
            "track_total_hits": True
        }
        
        # Query construction
        if query.search_type == SearchType.SIMPLE:
            es_query["query"] = {
                "multi_match": {
                    "query": query.query,
                    "fields": ["title^2", "description", "name^2", "bio"],
                    "type": "best_fields",
                    "fuzziness": "AUTO" if query.search_type == SearchType.FUZZY else None
                }
            }
        
        elif query.search_type == SearchType.ADVANCED:
            bool_query = {"bool": {"must": []}}
            
            # Multi-field search
            bool_query["bool"]["must"].append({
                "multi_match": {
                    "query": query.query,
                    "fields": ["title^3", "description^2", "name^3", "bio", "tags^2"],
                    "type": "cross_fields",
                    "operator": "and"
                }
            })
            
            es_query["query"] = bool_query
        
        elif query.search_type == SearchType.SEMANTIC and self.config.enable_semantic_search:
            # Semantic search using vector similarity
            # Note: Requires embeddings to be generated
            vector_query = await self._get_query_vector(query.query)
            if vector_query:
                es_query["query"] = {
                    "script_score": {
                        "query": {"match_all": {}},
                        "script": {
                            "source": "cosineSimilarity(params.query_vector, 'search_vector') + 1.0",
                            "params": {"query_vector": vector_query}
                        }
                    }
                }
        
        # Filters
        if query.filters or query.date_range:
            if "query" not in es_query:
                es_query["query"] = {"bool": {"must": []}}
            elif "bool" not in es_query["query"]:
                es_query["query"] = {"bool": {"must": [es_query["query"]]}}
            
            es_query["query"]["bool"]["filter"] = []
            
            # Apply filters
            for field, value in query.filters.items():
                if isinstance(value, list):
                    es_query["query"]["bool"]["filter"].append({
                        "terms": {field: value}
                    })
                else:
                    es_query["query"]["bool"]["filter"].append({
                        "term": {field: value}
                    })
            
            # Date range filter
            if query.date_range:
                date_filter = {"range": {}}
                for field, range_config in query.date_range.items():
                    if isinstance(range_config, dict):
                        date_filter["range"][field] = range_config
                    else:
                        # Assume it's a simple date value
                        date_filter["range"][field] = {"gte": range_config}
                
                es_query["query"]["bool"]["filter"].append(date_filter)
        
        # Sorting
        if query.sort_by:
            es_query["sort"] = [{
                query.sort_by: {"order": query.sort_order.value}
            }]
        else:
            # Default scoring sort
            es_query["sort"] = ["_score"]
        
        # Highlighting
        if query.highlight:
            es_query["highlight"] = {
                "fields": {
                    "title": {},
                    "description": {},
                    "name": {},
                    "bio": {}
                },
                "pre_tags": ["<mark>"],
                "post_tags": ["</mark>"]
            }
        
        # Aggregations
        if query.include_aggregations:
            es_query["aggs"] = {
                "categories": {"terms": {"field": "category", "size": 10}},
                "tags": {"terms": {"field": "tags", "size": 20}},
                "date_histogram": {
                    "date_histogram": {
                        "field": "created_at",
                        "calendar_interval": "1M"
                    }
                }
            }
        
        return es_query

    async def _process_search_response(
        self, response: Dict, query: SearchQuery, execution_time: float, search_id: str
    ) -> SearchResult:
        """Traiter la réponse Elasticsearch"""
        
        hits = []
        highlights = {}
        
        for hit in response["hits"]["hits"]:
            hit_data = hit["_source"]
            hit_data["_id"] = hit["_id"]
            hit_data["_score"] = hit["_score"]
            hits.append(hit_data)
            
            # Process highlights
            if "highlight" in hit:
                highlights[hit["_id"]] = hit["highlight"]
        
        # Process aggregations
        aggregations = {}
        if "aggregations" in response:
            for agg_name, agg_data in response["aggregations"].items():
                if "buckets" in agg_data:
                    aggregations[agg_name] = agg_data["buckets"]
                else:
                    aggregations[agg_name] = agg_data
        
        # Generate suggestions
        suggestions = []
        if query.include_suggestions:
            suggestions = await self._generate_query_suggestions(query.query, query.index_type)
        
        return SearchResult(
            query=query.query,
            total_hits=response["hits"]["total"]["value"],
            execution_time_ms=execution_time,
            page=query.page,
            size=query.size,
            hits=hits,
            highlights=highlights,
            aggregations=aggregations,
            suggestions=suggestions,
            search_id=search_id,
            timestamp=datetime.utcnow()
        )

    async def _get_autocomplete_suggestions(
        self, index_type: IndexType, query: str, limit: int
    ) -> List[str]:
        """Générer suggestions d'autocomplétion"""
        try:
            index_name = f"ainflue_{index_type.value}"
            
            es_query = {
                "size": 0,
                "suggest": {
                    "autocomplete": {
                        "prefix": query,
                        "completion": {
                            "field": "suggest",
                            "size": limit
                        }
                    }
                }
            }
            
            response = await self.es_client.search(index=index_name, body=es_query)
            
            suggestions = []
            if "suggest" in response and "autocomplete" in response["suggest"]:
                for suggestion in response["suggest"]["autocomplete"][0]["options"]:
                    suggestions.append(suggestion["text"])
            
            return suggestions
            
        except Exception as e:
            self.logger.error(f"Autocomplete error: {str(e)}")
            return []

    def get_app(self) -> FastAPI:
        """Retourne instance FastAPI"""
        return self.app


def create_search_service(config: SearchConfig = None) -> FastAPI:
    """
    Factory pour créer service de recherche
    
    Args:
        config: Configuration personnalisée
        
    Returns:
        FastAPI: Instance du service configuré
    """
    search_service = SearchServiceTemplate(config)
    return search_service.get_app()


if __name__ == "__main__":
    import uvicorn
    
    config = SearchConfig(
        elasticsearch_hosts=["http://localhost:9200"],
        enable_semantic_search=True,
        enable_search_analytics=True,
        enable_autocomplete=True
    )
    
    app = create_search_service(config)
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )