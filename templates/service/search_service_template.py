"""
🔍 SEARCH SERVICE TEMPLATE - BACKEND SENIOR EXPERT IMPLEMENTATION
================================================================

Enterprise-grade search service template with:
- Elasticsearch/OpenSearch integration
- Full-text search with relevance scoring
- Faceted search and filtering
- Auto-completion and suggestions
- Search analytics and monitoring
- Multi-language support
- Personalized search results

Author: Backend Senior Expert
Version: 1.0.0
"""

from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass
from abc import ABC, abstractmethod
from enum import Enum
import asyncio
import logging
from datetime import datetime
import json
import re
from elasticsearch import AsyncElasticsearch
from elasticsearch.exceptions import ConnectionError, NotFoundError
import redis.asyncio as redis
from pydantic import BaseModel, Field


class SearchType(Enum):
    """Search type enumeration"""
    CONTENT = "content"
    CREATOR = "creator"
    HASHTAG = "hashtag"
    COLLABORATION = "collaboration"
    UNIVERSAL = "universal"


class SearchEngine(Enum):
    """Search engine types"""
    ELASTICSEARCH = "elasticsearch"
    OPENSEARCH = "opensearch"
    SOLR = "solr"
    WHOOSH = "whoosh"


@dataclass
class SearchConfig:
    """Search service configuration"""
    engine: SearchEngine = SearchEngine.ELASTICSEARCH
    host: str = "localhost"
    port: int = 9200
    username: Optional[str] = None
    password: Optional[str] = None
    ssl: bool = False
    ca_certs: Optional[str] = None
    timeout: int = 30
    max_retries: int = 3
    
    # Index settings
    number_of_shards: int = 3
    number_of_replicas: int = 1
    refresh_interval: str = "1s"
    
    # Search settings
    default_size: int = 20
    max_size: int = 1000
    highlight_fragment_size: int = 150
    highlight_number_of_fragments: int = 3
    
    # Cache settings
    cache_enabled: bool = True
    cache_ttl: int = 300  # 5 minutes
    cache_prefix: str = "search_cache"


class SearchQuery(BaseModel):
    """Search query model"""
    query: str = Field(..., min_length=1, max_length=500)
    search_type: SearchType = SearchType.UNIVERSAL
    filters: Dict[str, Any] = Field(default_factory=dict)
    facets: List[str] = Field(default_factory=list)
    sort: Optional[List[Dict[str, str]]] = None
    size: int = Field(default=20, ge=1, le=1000)
    from_: int = Field(default=0, ge=0, alias="from")
    highlight: bool = True
    suggest: bool = True
    explain: bool = False
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    ip_address: Optional[str] = None


class SearchResult(BaseModel):
    """Search result model"""
    id: str
    score: float
    source: Dict[str, Any]
    highlight: Dict[str, List[str]] = Field(default_factory=dict)
    explanation: Optional[Dict[str, Any]] = None
    index: str
    type: str


class SearchResponse(BaseModel):
    """Search response model"""
    total: int
    max_score: float
    took: int
    timed_out: bool
    results: List[SearchResult]
    aggregations: Dict[str, Any] = Field(default_factory=dict)
    suggestions: List[str] = Field(default_factory=list)
    query_id: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class SearchAnalytics(BaseModel):
    """Search analytics model"""
    query: str
    search_type: SearchType
    total_results: int
    took_ms: int
    user_id: Optional[str]
    session_id: Optional[str]
    ip_address: Optional[str]
    clicked_results: List[str] = Field(default_factory=list)
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class AbstractSearchEngine(ABC):
    """Abstract search engine interface"""
    
    @abstractmethod
    async def index_document(self, index: str, doc_id: str, document: Dict[str, Any]) -> bool:
        """Index a document"""
        pass
    
    @abstractmethod
    async def search(self, query: SearchQuery) -> SearchResponse:
        """Perform search"""
        pass
    
    @abstractmethod
    async def suggest(self, query: str, field: str = "title") -> List[str]:
        """Get search suggestions"""
        pass
    
    @abstractmethod
    async def delete_document(self, index: str, doc_id: str) -> bool:
        """Delete a document"""
        pass
    
    @abstractmethod
    async def bulk_index(self, operations: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Bulk index operations"""
        pass


class ElasticsearchEngine(AbstractSearchEngine):
    """Elasticsearch implementation"""
    
    def __init__(self, config -> None: SearchConfig) -> None:
        self.config = config
        self.client = None
        self.logger = logging.getLogger(__name__)
    
    async def connect(self) -> None:
        """Connect to Elasticsearch"""
        try:
            self.client = AsyncElasticsearch(
                [f"{self.config.host}:{self.config.port}"],
                http_auth=(self.config.username, self.config.password) if self.config.username else None,
                use_ssl=self.config.ssl,
                ca_certs=self.config.ca_certs,
                timeout=self.config.timeout,
                max_retries=self.config.max_retries,
                retry_on_timeout=True
            )
            await self.client.ping()
            self.logger.info("Connected to Elasticsearch")
        except Exception as e:
            self.logger.error(f"Failed to connect to Elasticsearch: {e}")
            raise
    
    async def disconnect(self) -> None:
        """Disconnect from Elasticsearch"""
        if self.client:
            await self.client.close()
    
    async def create_index(self, index -> None: str, mapping -> None: Dict[str, Any]) -> None:
        """Create index with mapping"""
        try:
            body = {
                "settings": {
                    "number_of_shards": self.config.number_of_shards,
                    "number_of_replicas": self.config.number_of_replicas,
                    "refresh_interval": self.config.refresh_interval,
                    "analysis": {
                        "analyzer": {
                            "custom_text_analyzer": {
                                "type": "custom",
                                "tokenizer": "standard",
                                "filter": [
                                    "lowercase",
                                    "asciifolding",
                                    "stop",
                                    "stemmer"
                                ]
                            },
                            "autocomplete_analyzer": {
                                "type": "custom",
                                "tokenizer": "standard",
                                "filter": [
                                    "lowercase",
                                    "asciifolding",
                                    "autocomplete_filter"
                                ]
                            }
                        },
                        "filter": {
                            "autocomplete_filter": {
                                "type": "edge_ngram",
                                "min_gram": 2,
                                "max_gram": 20
                            }
                        }
                    }
                },
                "mappings": mapping
            }
            
            await self.client.indices.create(index=index, body=body)
            self.logger.info(f"Created index: {index}")
        except Exception as e:
            if "already_exists" not in str(e):
                self.logger.error(f"Failed to create index {index}: {e}")
                raise
    
    async def index_document(self, index: str, doc_id: str, document: Dict[str, Any]) -> bool:
        """Index a document"""
        try:
            response = await self.client.index(
                index=index,
                id=doc_id,
                body=document
            )
            return response["result"] in ["created", "updated"]
        except Exception as e:
            self.logger.error(f"Failed to index document {doc_id}: {e}")
            return False
    
    async def search(self, query: SearchQuery) -> SearchResponse:
        """Perform search"""
        try:
            # Build search body
            search_body = self._build_search_body(query)
            
            # Execute search
            response = await self.client.search(
                index=self._get_indices(query.search_type),
                body=search_body
            )
            
            # Parse response
            return self._parse_search_response(response, query)
        
        except Exception as e:
            self.logger.error(f"Search failed: {e}")
            raise
    
    def _build_search_body(self, query: SearchQuery) -> Dict[str, Any]:
        """Build Elasticsearch search body"""
        body = {
            "size": query.size,
            "from": query.from_,
            "track_total_hits": True,
            "query": self._build_query(query),
            "_source": True
        }
        
        # Add sorting
        if query.sort:
            body["sort"] = query.sort
        else:
            body["sort"] = [{"_score": {"order": "desc"}}]
        
        # Add highlighting
        if query.highlight:
            body["highlight"] = {
                "fields": {
                    "title": {
                        "fragment_size": self.config.highlight_fragment_size,
                        "number_of_fragments": self.config.highlight_number_of_fragments
                    },
                    "content": {
                        "fragment_size": self.config.highlight_fragment_size,
                        "number_of_fragments": self.config.highlight_number_of_fragments
                    },
                    "description": {
                        "fragment_size": self.config.highlight_fragment_size,
                        "number_of_fragments": self.config.highlight_number_of_fragments
                    }
                },
                "pre_tags": ["<em>"],
                "post_tags": ["</em>"]
            }
        
        # Add aggregations/facets
        if query.facets:
            body["aggregations"] = self._build_aggregations(query.facets)
        
        # Add suggestions
        if query.suggest:
            body["suggest"] = {
                "text": query.query,
                "term_suggest": {
                    "term": {
                        "field": "title",
                        "size": 5
                    }
                },
                "phrase_suggest": {
                    "phrase": {
                        "field": "title",
                        "size": 5,
                        "gram_size": 3,
                        "direct_generator": [{
                            "field": "title",
                            "suggest_mode": "always"
                        }]
                    }
                }
            }
        
        # Add explanation
        if query.explain:
            body["explain"] = True
        
        return body
    
    def _build_query(self, query: SearchQuery) -> Dict[str, Any]:
        """Build Elasticsearch query"""
        # Start with multi-match query
        must_queries = []
        
        if query.query.strip():
            must_queries.append({
                "multi_match": {
                    "query": query.query,
                    "fields": [
                        "title^3",
                        "description^2",
                        "content",
                        "tags^2",
                        "category^1.5"
                    ],
                    "type": "best_fields",
                    "operator": "or",
                    "fuzziness": "AUTO",
                    "prefix_length": 2
                }
            })
        else:
            must_queries.append({"match_all": {}})
        
        # Add filters
        filter_queries = []
        for field, value in query.filters.items():
            if isinstance(value, list):
                filter_queries.append({"terms": {field: value}})
            elif isinstance(value, dict):
                if "range" in value:
                    filter_queries.append({"range": {field: value["range"]}})
                else:
                    filter_queries.append({"term": {field: value}})
            else:
                filter_queries.append({"term": {field: value}})
        
        # Build bool query
        bool_query = {
            "bool": {
                "must": must_queries,
                "filter": filter_queries
            }
        }
        
        # Add personalization if user_id provided
        if query.user_id:
            bool_query["bool"]["should"] = [
                {
                    "function_score": {
                        "query": {"match_all": {}},
                        "functions": [
                            {
                                "filter": {"term": {"creator_id": query.user_id}},
                                "weight": 1.5
                            },
                            {
                                "filter": {"term": {"followers": query.user_id}},
                                "weight": 1.2
                            }
                        ],
                        "score_mode": "multiply"
                    }
                }
            ]
        
        return bool_query
    
    def _build_aggregations(self, facets: List[str]) -> Dict[str, Any]:
        """Build aggregations for facets"""
        aggregations = {}
        
        for facet in facets:
            if facet in ["category", "type", "status", "language"]:
                aggregations[f"{facet}_facet"] = {
                    "terms": {
                        "field": facet,
                        "size": 20
                    }
                }
            elif facet == "date_range":
                aggregations["date_range_facet"] = {
                    "date_range": {
                        "field": "created_at",
                        "ranges": [
                            {"key": "last_hour", "from": "now-1h"},
                            {"key": "last_day", "from": "now-1d"},
                            {"key": "last_week", "from": "now-7d"},
                            {"key": "last_month", "from": "now-30d"}
                        ]
                    }
                }
            elif facet == "price_range":
                aggregations["price_range_facet"] = {
                    "range": {
                        "field": "price",
                        "ranges": [
                            {"key": "free", "to": 0.01},
                            {"key": "low", "from": 0.01, "to": 10},
                            {"key": "medium", "from": 10, "to": 50},
                            {"key": "high", "from": 50}
                        ]
                    }
                }
        
        return aggregations
    
    def _get_indices(self, search_type: SearchType) -> List[str]:
        """Get indices based on search type"""
        index_mapping = {
            SearchType.CONTENT: ["content", "posts", "videos", "images"],
            SearchType.CREATOR: ["creators", "users"],
            SearchType.HASHTAG: ["hashtags", "tags"],
            SearchType.COLLABORATION: ["collaborations", "projects"],
            SearchType.UNIVERSAL: ["*"]
        }
        return index_mapping.get(search_type, ["*"])
    
    def _parse_search_response(self, response: Dict[str, Any], query: SearchQuery) -> SearchResponse:
        """Parse Elasticsearch response"""
        hits = response["hits"]
        results = []
        
        for hit in hits["hits"]:
            result = SearchResult(
                id=hit["_id"],
                score=hit["_score"],
                source=hit["_source"],
                highlight=hit.get("highlight", {}),
                explanation=hit.get("_explanation"),
                index=hit["_index"],
                type=hit.get("_type", "document")
            )
            results.append(result)
        
        # Parse aggregations
        aggregations = {}
        if "aggregations" in response:
            for agg_name, agg_data in response["aggregations"].items():
                if "buckets" in agg_data:
                    aggregations[agg_name] = [
                        {"key": bucket["key"], "count": bucket["doc_count"]}
                        for bucket in agg_data["buckets"]
                    ]
        
        # Parse suggestions
        suggestions = []
        if "suggest" in response:
            for suggest_name, suggest_data in response["suggest"].items():
                for suggestion in suggest_data:
                    for option in suggestion.get("options", []):
                        suggestions.append(option["text"])
        
        return SearchResponse(
            total=hits["total"]["value"],
            max_score=hits["max_score"] or 0.0,
            took=response["took"],
            timed_out=response["timed_out"],
            results=results,
            aggregations=aggregations,
            suggestions=list(set(suggestions)),  # Remove duplicates
            query_id=f"query_{datetime.utcnow().timestamp()}"
        )
    
    async def suggest(self, query: str, field: str = "title") -> List[str]:
        """Get search suggestions"""
        try:
            response = await self.client.search(
                index="*",
                body={
                    "suggest": {
                        "autocomplete": {
                            "prefix": query,
                            "completion": {
                                "field": f"{field}.suggest",
                                "size": 10
                            }
                        }
                    }
                }
            )
            
            suggestions = []
            for suggestion in response["suggest"]["autocomplete"]:
                for option in suggestion["options"]:
                    suggestions.append(option["text"])
            
            return suggestions
        except Exception as e:
            self.logger.error(f"Failed to get suggestions: {e}")
            return []
    
    async def delete_document(self, index: str, doc_id: str) -> bool:
        """Delete a document"""
        try:
            response = await self.client.delete(
                index=index,
                id=doc_id
            )
            return response["result"] == "deleted"
        except NotFoundError:
            return False
        except Exception as e:
            self.logger.error(f"Failed to delete document {doc_id}: {e}")
            return False
    
    async def bulk_index(self, operations: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Bulk index operations"""
        try:
            body = []
            for op in operations:
                action = {"index": {"_index": op["index"], "_id": op["id"]}}
                body.append(action)
                body.append(op["document"])
            
            response = await self.client.bulk(body=body)
            return {
                "took": response["took"],
                "errors": response["errors"],
                "items": len(response["items"])
            }
        except Exception as e:
            self.logger.error(f"Bulk index failed: {e}")
            raise


class SearchService:
    """Enterprise search service"""
    
    def __init__(self, config -> None: SearchConfig) -> None:
        self.config = config
        self.engine = self._create_engine()
        self.cache = None
        self.analytics_buffer = []
        self.logger = logging.getLogger(__name__)
    
    def _create_engine(self) -> AbstractSearchEngine:
        """Create search engine instance"""
        if self.config.engine == SearchEngine.ELASTICSEARCH:
            return ElasticsearchEngine(self.config)
        else:
            raise ValueError(f"Unsupported search engine: {self.config.engine}")
    
    async def initialize(self) -> None:
        """Initialize search service"""
        await self.engine.connect()
        
        if self.config.cache_enabled:
            self.cache = redis.Redis(
                host="localhost",
                port=6379,
                decode_responses=True
            )
        
        # Create default indices
        await self._create_default_indices()
        
        self.logger.info("Search service initialized")
    
    async def shutdown(self) -> None:
        """Shutdown search service"""
        await self.engine.disconnect()
        if self.cache:
            await self.cache.close()
    
    async def _create_default_indices(self) -> None:
        """Create default search indices"""
        indices = {
            "content": {
                "properties": {
                    "title": {
                        "type": "text",
                        "analyzer": "custom_text_analyzer",
                        "fields": {
                            "suggest": {
                                "type": "completion"
                            }
                        }
                    },
                    "description": {
                        "type": "text",
                        "analyzer": "custom_text_analyzer"
                    },
                    "content": {
                        "type": "text",
                        "analyzer": "custom_text_analyzer"
                    },
                    "category": {
                        "type": "keyword"
                    },
                    "tags": {
                        "type": "keyword"
                    },
                    "creator_id": {
                        "type": "keyword"
                    },
                    "created_at": {
                        "type": "date"
                    },
                    "updated_at": {
                        "type": "date"
                    },
                    "status": {
                        "type": "keyword"
                    },
                    "language": {
                        "type": "keyword"
                    },
                    "price": {
                        "type": "float"
                    },
                    "rating": {
                        "type": "float"
                    },
                    "view_count": {
                        "type": "long"
                    },
                    "like_count": {
                        "type": "long"
                    }
                }
            },
            "creators": {
                "properties": {
                    "username": {
                        "type": "text",
                        "analyzer": "custom_text_analyzer",
                        "fields": {
                            "suggest": {
                                "type": "completion"
                            }
                        }
                    },
                    "display_name": {
                        "type": "text",
                        "analyzer": "custom_text_analyzer"
                    },
                    "bio": {
                        "type": "text",
                        "analyzer": "custom_text_analyzer"
                    },
                    "category": {
                        "type": "keyword"
                    },
                    "verified": {
                        "type": "boolean"
                    },
                    "follower_count": {
                        "type": "long"
                    },
                    "content_count": {
                        "type": "long"
                    },
                    "rating": {
                        "type": "float"
                    },
                    "location": {
                        "type": "geo_point"
                    },
                    "created_at": {
                        "type": "date"
                    }
                }
            }
        }
        
        for index, mapping in indices.items():
            await self.engine.create_index(index, mapping)
    
    async def search(self, query: SearchQuery) -> SearchResponse:
        """Perform search with caching and analytics"""
        start_time = datetime.utcnow()
        
        # Check cache first
        cache_key = None
        if self.config.cache_enabled and self.cache:
            cache_key = self._generate_cache_key(query)
            cached_result = await self.cache.get(cache_key)
            if cached_result:
                try:
                    return SearchResponse.parse_raw(cached_result)
                except Exception:
                    pass  # Ignore cache parsing errors
        
        # Perform search
        response = await self.engine.search(query)
        
        # Cache result
        if cache_key and self.cache:
            await self.cache.setex(
                cache_key,
                self.config.cache_ttl,
                response.json()
            )
        
        # Record analytics
        duration = (datetime.utcnow() - start_time).total_seconds() * 1000
        analytics = SearchAnalytics(
            query=query.query,
            search_type=query.search_type,
            total_results=response.total,
            took_ms=int(duration),
            user_id=query.user_id,
            session_id=query.session_id,
            ip_address=query.ip_address
        )
        self.analytics_buffer.append(analytics)
        
        # Flush analytics buffer if needed
        if len(self.analytics_buffer) >= 100:
            await self._flush_analytics()
        
        return response
    
    def _generate_cache_key(self, query: SearchQuery) -> str:
        """Generate cache key for query"""
        key_data = {
            "query": query.query,
            "type": query.search_type.value,
            "filters": query.filters,
            "sort": query.sort,
            "size": query.size,
            "from": query.from_
        }
        key_hash = hash(json.dumps(key_data, sort_keys=True))
        return f"{self.config.cache_prefix}:{key_hash}"
    
    async def _flush_analytics(self) -> None:
        """Flush analytics buffer"""
        try:
            # In a real implementation, this would send to analytics service
            self.logger.info(f"Flushing {len(self.analytics_buffer)} analytics records")
            self.analytics_buffer.clear()
        except Exception as e:
            self.logger.error(f"Failed to flush analytics: {e}")
    
    async def index_content(self, content_id: str, content: Dict[str, Any]) -> bool:
        """Index content document"""
        return await self.engine.index_document("content", content_id, content)
    
    async def index_creator(self, creator_id: str, creator: Dict[str, Any]) -> bool:
        """Index creator document"""
        return await self.engine.index_document("creators", creator_id, creator)
    
    async def delete_content(self, content_id: str) -> bool:
        """Delete content document"""
        return await self.engine.delete_document("content", content_id)
    
    async def delete_creator(self, creator_id: str) -> bool:
        """Delete creator document"""
        return await self.engine.delete_document("creators", creator_id)
    
    async def bulk_index_content(self, contents: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Bulk index content documents"""
        operations = [
            {
                "index": "content",
                "id": content["id"],
                "document": content
            }
            for content in contents
        ]
        return await self.engine.bulk_index(operations)
    
    async def get_suggestions(self, query: str, field: str = "title") -> List[str]:
        """Get search suggestions"""
        return await self.engine.suggest(query, field)
    
    async def get_analytics(self, start_date: datetime, end_date: datetime) -> List[SearchAnalytics]:
        """Get search analytics for date range"""
        # In a real implementation, this would query analytics storage
        return [
            analytics for analytics in self.analytics_buffer
            if start_date <= analytics.timestamp <= end_date
        ]


# Usage example
async def main() -> None:
    """Example usage of SearchService"""
    
    # Configure search service
    config = SearchConfig(
        engine=SearchEngine.ELASTICSEARCH,
        host="localhost",
        port=9200,
        cache_enabled=True
    )
    
    # Initialize service
    search_service = SearchService(config)
    await search_service.initialize()
    
    try:
        # Index some content
        content_data = {
            "id": "content_1",
            "title": "Amazing AI-Generated Art Tutorial",
            "description": "Learn how to create stunning AI art",
            "content": "This tutorial covers the basics of AI art generation...",
            "category": "tutorial",
            "tags": ["ai", "art", "tutorial"],
            "creator_id": "creator_123",
            "created_at": datetime.utcnow().isoformat(),
            "status": "published",
            "language": "en",
            "price": 0.0,
            "rating": 4.8,
            "view_count": 1000,
            "like_count": 150
        }
        
        await search_service.index_content("content_1", content_data)
        
        # Perform search
        query = SearchQuery(
            query="AI art tutorial",
            search_type=SearchType.CONTENT,
            filters={"category": "tutorial"},
            facets=["category", "language"],
            size=10
        )
        
        response = await search_service.search(query)
        
        print(f"Found {response.total} results")
        for result in response.results:
            print(f"- {result.source.get('title')} (Score: {result.score})")
        
        # Get suggestions
        suggestions = await search_service.get_suggestions("AI ar")
        print(f"Suggestions: {suggestions}")
        
    finally:
        await search_service.shutdown()


if __name__ == "__main__":
    asyncio.run(main())