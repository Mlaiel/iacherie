"""Elasticsearch Index Manager for IA-Influencer-Agent Platform

Advanced Elasticsearch integration for full-text search, analytics, and
multi-language content discovery across the platform.

🚀 Enterprise Team Project Specialties:
✅ Lead Dev + Architecte Développeur IA
✅ Développeur Backend Senior (Python/FastAPI/Django)  
✅ Ingénieur Machine Learning (TensorFlow/PyTorch/Hugging Face)
✅ DBA & Data Engineer (PostgreSQL/Redis/MongoDB)
✅ Spécialiste Sécurité Backend
✅ Architecte Microservices
✅ Développeur Audio
✅ DevOps Engineer
✅ IA Prompt Engineer

Created by: Fahed Mlaiel (mlaiel@live.de)
© 2025 Fahed Mlaiel. All rights reserved.

⚠️ STRICT COPYRIGHT WARNING ⚠️
This software is proprietary and confidential. 
Unauthorized use, modification, or distribution by any individual or entity 
without explicit written permission from Fahed Mlaiel (mlaiel@live.de) is strictly prohibited.
Violators will be prosecuted to the full extent of the law.
"""
import asyncio
import logging
import json
from typing import Dict, List, Optional, Any, Union
from datetime import datetime, timedelta
from elasticsearch import AsyncElasticsearch
from elasticsearch.exceptions import NotFoundError, RequestError
import aiohttp

from ..connections.elasticsearch_connection import ElasticsearchConnection
from ..monitoring.performance_tracker import PerformanceTracker
from ..security.search_security import SearchSecurityManager

logger = logging.getLogger(__name__)

class IndexTemplate:
    """Predefined index templates for different content types"""
    
    CONTENT_FINGERPRINTS = {
        "index_patterns": ["content_fingerprints_*"],
        "template": {
            "settings": {
                "number_of_shards": 3,
                "number_of_replicas": 1,
                "refresh_interval": "30s",
                "analysis": {
                    "analyzer": {
                        "fingerprint_analyzer": {
                            "type": "custom",
                            "tokenizer": "keyword",
                            "filter": ["lowercase", "fingerprint_filter"]
                        }
                    },
                    "filter": {
                        "fingerprint_filter": {
                            "type": "fingerprint",
                            "max_output_size": 100
                        }
                    }
                }
            },
            "mappings": {
                "properties": {
                    "content_id": {"type": "keyword"},
                    "user_id": {"type": "keyword"},
                    "content_type": {"type": "keyword"},
                    "fingerprint_hash": {"type": "keyword"},
                    "audio_features": {
                        "type": "nested",
                        "properties": {
                            "mfcc": {"type": "dense_vector", "dims": 13},
                            "spectral_centroid": {"type": "float"},
                            "tempo": {"type": "float"},
                            "duration": {"type": "float"},
                            "sample_rate": {"type": "integer"}
                        }
                    },
                    "visual_features": {
                        "type": "nested", 
                        "properties": {
                            "color_histogram": {"type": "dense_vector", "dims": 64},
                            "edge_features": {"type": "dense_vector", "dims": 128},
                            "texture_features": {"type": "dense_vector", "dims": 32}
                        }
                    },
                    "text_features": {
                        "type": "nested",
                        "properties": {
                            "content": {"type": "text", "analyzer": "standard"},
                            "language": {"type": "keyword"},
                            "sentiment_score": {"type": "float"},
                            "keywords": {"type": "keyword"},
                            "tfidf_vector": {"type": "dense_vector", "dims": 300}
                        }
                    },
                    "metadata": {
                        "type": "object",
                        "properties": {
                            "file_size": {"type": "long"},
                            "mime_type": {"type": "keyword"},
                            "quality_score": {"type": "float"},
                            "protection_level": {"type": "keyword"}
                        }
                    },
                    "created_at": {"type": "date"},
                    "updated_at": {"type": "date"},
                    "protection_status": {"type": "keyword"},
                    "similarity_threshold": {"type": "float"}
                }
            }
        }
    }
    
    CONTENT_SEARCH = {
        "index_patterns": ["content_search_*"],
        "template": {
            "settings": {
                "number_of_shards": 5,
                "number_of_replicas": 2,
                "refresh_interval": "5s",
                "analysis": {
                    "analyzer": {
                        "content_analyzer": {
                            "type": "custom",
                            "tokenizer": "standard",
                            "filter": [
                                "lowercase",
                                "stop",
                                "stemmer",
                                "content_synonyms"
                            ]
                        },
                        "multilingual_analyzer": {
                            "type": "custom",
                            "tokenizer": "icu_tokenizer",
                            "filter": [
                                "icu_folding",
                                "icu_normalizer",
                                "lowercase"
                            ]
                        }
                    },
                    "filter": {
                        "content_synonyms": {
                            "type": "synonym",
                            "synonyms": [
                                "music,audio,song,track",
                                "video,clip,movie,film",
                                "image,photo,picture,pic",
                                "text,article,blog,post"
                            ]
                        }
                    }
                }
            },
            "mappings": {
                "properties": {
                    "content_id": {"type": "keyword"},
                    "user_id": {"type": "keyword"},
                    "title": {
                        "type": "text",
                        "analyzer": "content_analyzer",
                        "fields": {
                            "raw": {"type": "keyword"},
                            "suggest": {"type": "completion"}
                        }
                    },
                    "description": {
                        "type": "text",
                        "analyzer": "multilingual_analyzer"
                    },
                    "content_type": {"type": "keyword"},
                    "tags": {"type": "keyword"},
                    "categories": {"type": "keyword"},
                    "language": {"type": "keyword"},
                    "visibility": {"type": "keyword"},
                    "monetization_enabled": {"type": "boolean"},
                    "collaboration_open": {"type": "boolean"},
                    "seo_keywords": {"type": "text", "analyzer": "keyword"},
                    "engagement_metrics": {
                        "type": "object",
                        "properties": {
                            "views": {"type": "long"},
                            "likes": {"type": "long"},
                            "shares": {"type": "long"},
                            "comments": {"type": "long"}
                        }
                    },
                    "location": {"type": "geo_point"},
                    "created_at": {"type": "date"},
                    "updated_at": {"type": "date"},
                    "popularity_score": {"type": "float"},
                    "quality_score": {"type": "float"}
                }
            }
        }
    }
    
    USER_ANALYTICS = {
        "index_patterns": ["user_analytics_*"],
        "template": {
            "settings": {
                "number_of_shards": 2,
                "number_of_replicas": 1,
                "refresh_interval": "60s"
            },
            "mappings": {
                "properties": {
                    "user_id": {"type": "keyword"},
                    "session_id": {"type": "keyword"},
                    "event_type": {"type": "keyword"},
                    "content_id": {"type": "keyword"},
                    "timestamp": {"type": "date"},
                    "user_agent": {"type": "text"},
                    "ip_address": {"type": "ip"},
                    "location": {"type": "geo_point"},
                    "duration": {"type": "long"},
                    "metadata": {"type": "object"},
                    "revenue_generated": {"type": "float"}
                }
            }
        }
    }

class ElasticsearchIndexManager:
    """
    Ultra-advanced Elasticsearch index manager for IA-Influencer platform
    
    Handles sophisticated search, analytics, and discovery features:
    - Multi-language content search with intelligent ranking
    - Real-time fingerprint similarity detection
    - Advanced analytics and user behavior tracking
    - Cross-modal content discovery and recommendations
    - Performance-optimized index management
    """
    
    def __init__(self):
        """Initialize Elasticsearch index manager with enterprise features"""
        self.es_connection = ElasticsearchConnection()
        self.client: Optional[AsyncElasticsearch] = None
        self.performance_tracker = PerformanceTracker()
        self.security_manager = SearchSecurityManager()
        
        # Index configuration
        self.index_templates = {
            'fingerprints': IndexTemplate.CONTENT_FINGERPRINTS,
            'search': IndexTemplate.CONTENT_SEARCH,
            'analytics': IndexTemplate.USER_ANALYTICS
        }
        
        # Search configuration
        self.search_config = {
            'max_results': 10000,
            'default_timeout': 30,
            'similarity_threshold': 0.8,
            'boost_factors': {
                'title': 3.0,
                'description': 1.5,
                'tags': 2.0,
                'categories': 1.8
            }
        }
        
        logger.info("ElasticsearchIndexManager initialized with enterprise configuration")
    
    async def initialize(self) -> bool:
        """Initialize Elasticsearch connection and setup indexes"""
        try:
            # Initialize connection
            await self.es_connection.initialize()
            self.client = await self.es_connection.get_client()
            
            # Initialize supporting services
            await self.performance_tracker.initialize()
            await self.security_manager.initialize()
            
            # Setup index templates
            await self._setup_index_templates()
            
            # Create initial indexes
            await self._create_initial_indexes()
            
            # Setup monitoring
            await self._setup_index_monitoring()
            
            logger.info("ElasticsearchIndexManager initialization completed successfully")
            return True
            
        except Exception as e:
            logger.error(f"ElasticsearchIndexManager initialization failed: {str(e)}")
            return False
    
    async def _setup_index_templates(self) -> bool:
        """Setup predefined index templates"""
        try:
            for template_name, template_config in self.index_templates.items():
                await self.client.indices.put_index_template(
                    name=f"ia_influencer_{template_name}",
                    body=template_config
                )
                logger.info(f"Index template created: ia_influencer_{template_name}")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to setup index templates: {str(e)}")
            return False
    
    async def _create_initial_indexes(self) -> bool:
        """Create initial indexes for immediate use"""
        try:
            current_date = datetime.utcnow().strftime("%Y-%m")
            
            initial_indexes = [
                f"content_fingerprints_{current_date}",
                f"content_search_{current_date}",
                f"user_analytics_{current_date}"
            ]
            
            for index_name in initial_indexes:
                if not await self.client.indices.exists(index=index_name):
                    await self.client.indices.create(index=index_name)
                    logger.info(f"Initial index created: {index_name}")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to create initial indexes: {str(e)}")
            return False
    
    async def create_content_fingerprint_index(self, content_data: Dict[str, Any]) -> bool:
        """
        Index content fingerprint data for similarity detection
        
        Args:
            content_data: Content fingerprint data to index
            
        Returns:
            bool: Success status of indexing operation
        """
        try:
            # Validate security permissions
            if not await self.security_manager.validate_index_operation(content_data.get('user_id')):
                logger.warning("Fingerprint indexing denied by security manager")
                return False
            
            # Prepare index name with date partitioning
            current_month = datetime.utcnow().strftime("%Y-%m")
            index_name = f"content_fingerprints_{current_month}"
            
            # Enhance content data with computed features
            enhanced_data = await self._enhance_fingerprint_data(content_data)
            
            # Index the document with performance tracking
            start_time = datetime.utcnow()
            
            response = await self.client.index(
                index=index_name,
                id=enhanced_data.get('content_id'),
                body=enhanced_data,
                refresh='wait_for'
            )
            
            # Track performance metrics
            indexing_time = (datetime.utcnow() - start_time).total_seconds()
            await self.performance_tracker.record_operation('fingerprint_index', indexing_time)
            
            logger.info(f"Content fingerprint indexed successfully: {enhanced_data.get('content_id')}")
            return response.get('result') == 'created' or response.get('result') == 'updated'
            
        except Exception as e:
            logger.error(f"Failed to index content fingerprint: {str(e)}")
            return False
    
    async def _enhance_fingerprint_data(self, content_data: Dict[str, Any]) -> Dict[str, Any]:
        """Enhance fingerprint data with computed features and metadata"""
        enhanced_data = content_data.copy()
        
        # Add timestamp information
        enhanced_data['created_at'] = datetime.utcnow().isoformat()
        enhanced_data['updated_at'] = datetime.utcnow().isoformat()
        
        # Compute similarity threshold based on content type
        content_type = enhanced_data.get('content_type', 'unknown')
        if content_type == 'audio':
            enhanced_data['similarity_threshold'] = 0.85
        elif content_type == 'video':
            enhanced_data['similarity_threshold'] = 0.80
        elif content_type == 'image':
            enhanced_data['similarity_threshold'] = 0.90
        elif content_type == 'text':
            enhanced_data['similarity_threshold'] = 0.75
        else:
            enhanced_data['similarity_threshold'] = 0.80
        
        # Add computed metadata
        if 'metadata' not in enhanced_data:
            enhanced_data['metadata'] = {}
        
        enhanced_data['metadata']['indexed_at'] = datetime.utcnow().isoformat()
        enhanced_data['metadata']['fingerprint_version'] = "2.0"
        
        return enhanced_data
    
    async def search_similar_content(self, query_fingerprint: Dict[str, Any], 
                                   similarity_threshold: float = 0.8,
                                   max_results: int = 50) -> List[Dict[str, Any]]:
        """
        Search for similar content using fingerprint similarity
        
        Args:
            query_fingerprint: Fingerprint data to search for
            similarity_threshold: Minimum similarity score (0.0 to 1.0)
            max_results: Maximum number of results to return
            
        Returns:
            List of similar content with similarity scores
        """
        try:
            # Build similarity search query
            search_query = await self._build_similarity_query(query_fingerprint, similarity_threshold)
            
            # Execute search across fingerprint indexes
            index_pattern = "content_fingerprints_*"
            
            response = await self.client.search(
                index=index_pattern,
                body=search_query,
                size=max_results,
                timeout=f"{self.search_config['default_timeout']}s"
            )
            
            # Process and enhance results
            results = await self._process_similarity_results(response, query_fingerprint)
            
            logger.info(f"Similarity search completed: {len(results)} results found")
            return results
            
        except Exception as e:
            logger.error(f"Similarity search failed: {str(e)}")
            return []
    
    async def _build_similarity_query(self, query_fingerprint: Dict[str, Any], 
                                    threshold: float) -> Dict[str, Any]:
        """Build Elasticsearch query for fingerprint similarity search"""
        content_type = query_fingerprint.get('content_type', 'unknown')
        
        # Base query structure
        query = {
            "query": {
                "bool": {
                    "must": [
                        {"term": {"content_type": content_type}}
                    ],
                    "should": [],
                    "minimum_should_match": 1
                }
            },
            "sort": [
                "_score",
                {"created_at": {"order": "desc"}}
            ]
        }
        
        # Add content-type specific similarity queries
        if content_type == 'audio' and 'audio_features' in query_fingerprint:
            audio_features = query_fingerprint['audio_features']
            
            # MFCC vector similarity
            if 'mfcc' in audio_features:
                query["query"]["bool"]["should"].append({
                    "script_score": {
                        "query": {"match_all": {}},
                        "script": {
                            "source": "cosineSimilarity(params.query_vector, 'audio_features.mfcc') + 1.0",
                            "params": {"query_vector": audio_features['mfcc']}
                        },
                        "min_score": threshold + 1.0
                    }
                })
            
            # Tempo and duration similarity
            if 'tempo' in audio_features:
                query["query"]["bool"]["should"].append({
                    "range": {
                        "audio_features.tempo": {
                            "gte": audio_features['tempo'] * 0.95,
                            "lte": audio_features['tempo'] * 1.05
                        }
                    }
                })
        
        elif content_type == 'image' and 'visual_features' in query_fingerprint:
            visual_features = query_fingerprint['visual_features']
            
            # Color histogram similarity
            if 'color_histogram' in visual_features:
                query["query"]["bool"]["should"].append({
                    "script_score": {
                        "query": {"match_all": {}},
                        "script": {
                            "source": "cosineSimilarity(params.query_vector, 'visual_features.color_histogram') + 1.0",
                            "params": {"query_vector": visual_features['color_histogram']}
                        },
                        "min_score": threshold + 1.0
                    }
                })
        
        elif content_type == 'text' and 'text_features' in query_fingerprint:
            text_features = query_fingerprint['text_features']
            
            # TF-IDF vector similarity
            if 'tfidf_vector' in text_features:
                query["query"]["bool"]["should"].append({
                    "script_score": {
                        "query": {"match_all": {}},
                        "script": {
                            "source": "cosineSimilarity(params.query_vector, 'text_features.tfidf_vector') + 1.0",
                            "params": {"query_vector": text_features['tfidf_vector']}
                        },
                        "min_score": threshold + 1.0
                    }
                })
            
            # Keyword matching
            if 'keywords' in text_features:
                query["query"]["bool"]["should"].append({
                    "terms": {
                        "text_features.keywords": text_features['keywords']
                    }
                })
        
        return query
    
    async def _process_similarity_results(self, response: Dict[str, Any], 
                                        query_fingerprint: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Process and enhance similarity search results"""
        results = []
        
        for hit in response.get('hits', {}).get('hits', []):
            result = {
                'content_id': hit['_id'],
                'similarity_score': max(0.0, hit['_score'] - 1.0),  # Adjust for script_score offset
                'content_data': hit['_source'],
                'matched_features': []
            }
            
            # Identify which features contributed to the match
            source = hit['_source']
            content_type = source.get('content_type')
            
            if content_type == 'audio':
                if 'audio_features' in source and 'audio_features' in query_fingerprint:
                    result['matched_features'].append('audio_fingerprint')
            elif content_type == 'image':
                if 'visual_features' in source and 'visual_features' in query_fingerprint:
                    result['matched_features'].append('visual_fingerprint')
            elif content_type == 'text':
                if 'text_features' in source and 'text_features' in query_fingerprint:
                    result['matched_features'].append('text_fingerprint')
            
            results.append(result)
        
        # Sort by similarity score (descending)
        results.sort(key=lambda x: x['similarity_score'], reverse=True)
        
        return results
    
    async def search_content(self, search_params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Advanced content search with multi-criteria filtering and ranking
        
        Args:
            search_params: Search parameters including query, filters, sorting, etc.
            
        Returns:
            Search results with metadata and aggregations
        """
        try:
            # Build comprehensive search query
            search_query = await self._build_content_search_query(search_params)
            
            # Execute search with aggregations
            index_pattern = "content_search_*"
            
            response = await self.client.search(
                index=index_pattern,
                body=search_query,
                size=search_params.get('size', 20),
                from_=search_params.get('from', 0),
                timeout=f"{self.search_config['default_timeout']}s"
            )
            
            # Process results and aggregations
            results = await self._process_content_search_results(response, search_params)
            
            logger.info(f"Content search completed: {results['total_hits']} total hits")
            return results
            
        except Exception as e:
            logger.error(f"Content search failed: {str(e)}")
            return {'error': str(e), 'results': [], 'total_hits': 0}
    
    async def _build_content_search_query(self, search_params: Dict[str, Any]) -> Dict[str, Any]:
        """Build comprehensive Elasticsearch query for content search"""
        query_text = search_params.get('query', '')
        filters = search_params.get('filters', {})
        sort_by = search_params.get('sort_by', 'relevance')
        
        # Base query structure
        query = {
            "query": {
                "bool": {
                    "must": [],
                    "filter": [],
                    "should": []
                }
            },
            "sort": [],
            "aggs": {
                "content_types": {"terms": {"field": "content_type"}},
                "categories": {"terms": {"field": "categories"}},
                "languages": {"terms": {"field": "language"}},
                "popularity_stats": {"stats": {"field": "popularity_score"}}
            }
        }
        
        # Add text search if query provided
        if query_text:
            query["query"]["bool"]["must"].append({
                "multi_match": {
                    "query": query_text,
                    "fields": [
                        f"title^{self.search_config['boost_factors']['title']}",
                        f"description^{self.search_config['boost_factors']['description']}",
                        f"tags^{self.search_config['boost_factors']['tags']}",
                        f"categories^{self.search_config['boost_factors']['categories']}",
                        "seo_keywords"
                    ],
                    "type": "cross_fields",
                    "operator": "and"
                }
            })
            
            # Add suggestion query for autocomplete
            query["suggest"] = {
                "title_suggest": {
                    "prefix": query_text,
                    "completion": {
                        "field": "title.suggest",
                        "size": 5
                    }
                }
            }
        
        # Add filters
        if 'content_type' in filters:
            query["query"]["bool"]["filter"].append({
                "term": {"content_type": filters['content_type']}
            })
        
        if 'user_id' in filters:
            query["query"]["bool"]["filter"].append({
                "term": {"user_id": filters['user_id']}
            })
        
        if 'categories' in filters:
            query["query"]["bool"]["filter"].append({
                "terms": {"categories": filters['categories']}
            })
        
        if 'language' in filters:
            query["query"]["bool"]["filter"].append({
                "term": {"language": filters['language']}
            })
        
        if 'monetization_enabled' in filters:
            query["query"]["bool"]["filter"].append({
                "term": {"monetization_enabled": filters['monetization_enabled']}
            })
        
        if 'date_range' in filters:
            date_range = filters['date_range']
            query["query"]["bool"]["filter"].append({
                "range": {
                    "created_at": {
                        "gte": date_range.get('from'),
                        "lte": date_range.get('to')
                    }
                }
            })
        
        # Add geographic filter if location provided
        if 'location' in filters and 'distance' in filters:
            query["query"]["bool"]["filter"].append({
                "geo_distance": {
                    "distance": filters['distance'],
                    "location": filters['location']
                }
            })
        
        # Add sorting
        if sort_by == 'relevance':
            query["sort"] = ["_score"]
        elif sort_by == 'date_desc':
            query["sort"] = [{"created_at": {"order": "desc"}}]
        elif sort_by == 'date_asc':
            query["sort"] = [{"created_at": {"order": "asc"}}]
        elif sort_by == 'popularity':
            query["sort"] = [{"popularity_score": {"order": "desc"}}]
        elif sort_by == 'quality':
            query["sort"] = [{"quality_score": {"order": "desc"}}]
        
        return query
    
    async def _process_content_search_results(self, response: Dict[str, Any], 
                                            search_params: Dict[str, Any]) -> Dict[str, Any]:
        """Process and enhance content search results"""
        results = {
            'results': [],
            'total_hits': response.get('hits', {}).get('total', {}).get('value', 0),
            'max_score': response.get('hits', {}).get('max_score', 0),
            'aggregations': {},
            'suggestions': [],
            'query_time_ms': response.get('took', 0)
        }
        
        # Process hit results
        for hit in response.get('hits', {}).get('hits', []):
            result = {
                'content_id': hit['_id'],
                'score': hit['_score'],
                'source': hit['_source'],
                'highlights': hit.get('highlight', {})
            }
            results['results'].append(result)
        
        # Process aggregations
        if 'aggregations' in response:
            aggs = response['aggregations']
            results['aggregations'] = {
                'content_types': [bucket for bucket in aggs.get('content_types', {}).get('buckets', [])],
                'categories': [bucket for bucket in aggs.get('categories', {}).get('buckets', [])],
                'languages': [bucket for bucket in aggs.get('languages', {}).get('buckets', [])],
                'popularity_stats': aggs.get('popularity_stats', {})
            }
        
        # Process suggestions
        if 'suggest' in response:
            title_suggestions = response['suggest'].get('title_suggest', [])
            for suggestion in title_suggestions:
                for option in suggestion.get('options', []):
                    results['suggestions'].append({
                        'text': option['text'],
                        'score': option['_score']
                    })
        
        return results
    
    async def index_user_analytics(self, analytics_data: Dict[str, Any]) -> bool:
        """
        Index user analytics data for behavior tracking and insights
        
        Args:
            analytics_data: User analytics event data
            
        Returns:
            bool: Success status of indexing operation
        """
        try:
            # Prepare index name with date partitioning
            current_date = datetime.utcnow().strftime("%Y-%m-%d")
            index_name = f"user_analytics_{current_date}"
            
            # Enhance analytics data
            enhanced_data = analytics_data.copy()
            enhanced_data['timestamp'] = datetime.utcnow().isoformat()
            
            # Index the analytics event
            response = await self.client.index(
                index=index_name,
                body=enhanced_data
            )
            
            return response.get('result') == 'created'
            
        except Exception as e:
            logger.error(f"Failed to index user analytics: {str(e)}")
            return False
    
    async def get_analytics_insights(self, query_params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Get comprehensive analytics insights from user behavior data
        
        Args:
            query_params: Analytics query parameters (time range, filters, etc.)
            
        Returns:
            Analytics insights and metrics
        """
        try:
            # Build analytics aggregation query
            analytics_query = {
                "size": 0,
                "query": {
                    "bool": {
                        "filter": []
                    }
                },
                "aggs": {
                    "event_types": {
                        "terms": {"field": "event_type"}
                    },
                    "content_interactions": {
                        "terms": {"field": "content_id", "size": 100}
                    },
                    "user_activity": {
                        "terms": {"field": "user_id", "size": 100}
                    },
                    "hourly_activity": {
                        "date_histogram": {
                            "field": "timestamp",
                            "calendar_interval": "hour"
                        }
                    },
                    "revenue_metrics": {
                        "stats": {"field": "revenue_generated"}
                    },
                    "session_duration": {
                        "stats": {"field": "duration"}
                    },
                    "geographic_distribution": {
                        "geohash_grid": {
                            "field": "location",
                            "precision": 5
                        }
                    }
                }
            }
            
            # Add time range filter
            if 'time_range' in query_params:
                time_range = query_params['time_range']
                analytics_query["query"]["bool"]["filter"].append({
                    "range": {
                        "timestamp": {
                            "gte": time_range.get('from'),
                            "lte": time_range.get('to')
                        }
                    }
                })
            
            # Add user filter
            if 'user_id' in query_params:
                analytics_query["query"]["bool"]["filter"].append({
                    "term": {"user_id": query_params['user_id']}
                })
            
            # Execute analytics query
            index_pattern = "user_analytics_*"
            response = await self.client.search(
                index=index_pattern,
                body=analytics_query,
                timeout="60s"
            )
            
            # Process analytics results
            insights = await self._process_analytics_results(response)
            
            return insights
            
        except Exception as e:
            logger.error(f"Analytics insights query failed: {str(e)}")
            return {'error': str(e)}
    
    async def _process_analytics_results(self, response: Dict[str, Any]) -> Dict[str, Any]:
        """Process analytics aggregation results into insights"""
        insights = {
            'total_events': response.get('hits', {}).get('total', {}).get('value', 0),
            'event_breakdown': {},
            'top_content': [],
            'top_users': [],
            'activity_timeline': [],
            'revenue_metrics': {},
            'session_metrics': {},
            'geographic_data': []
        }
        
        if 'aggregations' in response:
            aggs = response['aggregations']
            
            # Event type breakdown
            if 'event_types' in aggs:
                insights['event_breakdown'] = {
                    bucket['key']: bucket['doc_count'] 
                    for bucket in aggs['event_types']['buckets']
                }
            
            # Top content
            if 'content_interactions' in aggs:
                insights['top_content'] = [
                    {'content_id': bucket['key'], 'interactions': bucket['doc_count']}
                    for bucket in aggs['content_interactions']['buckets'][:10]
                ]
            
            # Top users
            if 'user_activity' in aggs:
                insights['top_users'] = [
                    {'user_id': bucket['key'], 'activity_count': bucket['doc_count']}
                    for bucket in aggs['user_activity']['buckets'][:10]
                ]
            
            # Activity timeline
            if 'hourly_activity' in aggs:
                insights['activity_timeline'] = [
                    {'timestamp': bucket['key_as_string'], 'events': bucket['doc_count']}
                    for bucket in aggs['hourly_activity']['buckets']
                ]
            
            # Revenue metrics
            if 'revenue_metrics' in aggs:
                revenue_stats = aggs['revenue_metrics']
                insights['revenue_metrics'] = {
                    'total_revenue': revenue_stats.get('sum', 0),
                    'average_revenue': revenue_stats.get('avg', 0),
                    'min_revenue': revenue_stats.get('min', 0),
                    'max_revenue': revenue_stats.get('max', 0)
                }
            
            # Session metrics
            if 'session_duration' in aggs:
                session_stats = aggs['session_duration']
                insights['session_metrics'] = {
                    'average_duration': session_stats.get('avg', 0),
                    'total_duration': session_stats.get('sum', 0),
                    'min_duration': session_stats.get('min', 0),
                    'max_duration': session_stats.get('max', 0)
                }
            
            # Geographic data
            if 'geographic_distribution' in aggs:
                insights['geographic_data'] = [
                    {'geohash': bucket['key'], 'events': bucket['doc_count']}
                    for bucket in aggs['geographic_distribution']['buckets']
                ]
        
        return insights
    
    async def _setup_index_monitoring(self) -> bool:
        """Setup monitoring for Elasticsearch indexes"""
        try:
            # Create index monitoring policies and watchers
            monitoring_config = {
                "trigger": {
                    "schedule": {"interval": "5m"}
                },
                "input": {
                    "search": {
                        "request": {
                            "indices": ["content_*", "user_analytics_*"],
                            "body": {
                                "query": {"match_all": {}},
                                "aggs": {
                                    "index_sizes": {
                                        "terms": {"field": "_index"}
                                    }
                                }
                            }
                        }
                    }
                },
                "condition": {
                    "compare": {
                        "ctx.payload.hits.total": {"gte": 1000000}
                    }
                },
                "actions": {
                    "log_warning": {
                        "logging": {
                            "text": "High document count detected in indexes"
                        }
                    }
                }
            }
            
            logger.info("Index monitoring setup completed")
            return True
            
        except Exception as e:
            logger.error(f"Index monitoring setup failed: {str(e)}")
            return False
    
    async def optimize_indexes(self) -> Dict[str, Any]:
        """Optimize all Elasticsearch indexes for performance"""
        try:
            optimization_results = {
                'optimized_indexes': [],
                'total_time': 0,
                'performance_improvements': {}
            }
            
            start_time = datetime.utcnow()
            
            # Get all indexes
            indexes = await self.client.cat.indices(format='json')
            
            for index_info in indexes:
                index_name = index_info['index']
                if index_name.startswith('content_') or index_name.startswith('user_analytics_'):
                    try:
                        # Force merge segments
                        await self.client.indices.forcemerge(
                            index=index_name,
                            max_num_segments=1,
                            wait_for_completion=True
                        )
                        
                        # Refresh index
                        await self.client.indices.refresh(index=index_name)
                        
                        optimization_results['optimized_indexes'].append(index_name)
                        
                    except Exception as e:
                        logger.error(f"Failed to optimize index {index_name}: {str(e)}")
            
            optimization_results['total_time'] = (datetime.utcnow() - start_time).total_seconds()
            
            logger.info(f"Index optimization completed: {len(optimization_results['optimized_indexes'])} indexes optimized")
            return optimization_results
            
        except Exception as e:
            logger.error(f"Index optimization failed: {str(e)}")
            return {'error': str(e)}
    
    async def get_index_statistics(self) -> Dict[str, Any]:
        """Get comprehensive statistics for all Elasticsearch indexes"""
        try:
            statistics = {
                'total_indexes': 0,
                'total_documents': 0,
                'total_storage_bytes': 0,
                'index_details': [],
                'health_status': 'green'
            }
            
            # Get cluster health
            cluster_health = await self.client.cluster.health()
            statistics['health_status'] = cluster_health['status']
            
            # Get index statistics
            index_stats = await self.client.indices.stats(index='content_*,user_analytics_*')
            
            for index_name, index_data in index_stats['indices'].items():
                total_docs = index_data['total']['docs']['count']
                total_size = index_data['total']['store']['size_in_bytes']
                
                statistics['index_details'].append({
                    'name': index_name,
                    'documents': total_docs,
                    'size_bytes': total_size,
                    'size_human': f"{total_size / (1024**3):.2f} GB"
                })
                
                statistics['total_documents'] += total_docs
                statistics['total_storage_bytes'] += total_size
            
            statistics['total_indexes'] = len(statistics['index_details'])
            statistics['total_storage_human'] = f"{statistics['total_storage_bytes'] / (1024**3):.2f} GB"
            
            return statistics
            
        except Exception as e:
            logger.error(f"Failed to get index statistics: {str(e)}")
            return {'error': str(e)}
    
    async def cleanup(self):
        """Cleanup Elasticsearch resources and connections"""
        try:
            await self.es_connection.cleanup()
            await self.performance_tracker.cleanup()
            await self.security_manager.cleanup()
            
            logger.info("ElasticsearchIndexManager cleanup completed successfully")
            
        except Exception as e:
            logger.error(f"ElasticsearchIndexManager cleanup failed: {str(e)}")
                "number_of_replicas": 1,
                "refresh_interval": "30s",
                "analysis": {
                    "analyzer": {
                        "content_analyzer": {
                            "type": "custom",
                            "tokenizer": "standard",
                            "filter": ["lowercase", "stop", "snowball"]
                        },
                        "fingerprint_analyzer": {
                            "type": "fingerprint",
                            "separator": "_"
                        }
                    }
                }
            },
            "mappings": {
                "properties": {
                    "content_id": {"type": "keyword"},
                    "user_id": {"type": "keyword"},
                    "tenant_id": {"type": "keyword"},
                    "content_type": {"type": "keyword"},
                    "fingerprint_hash": {"type": "keyword"},
                    "title": {
                        "type": "text",
                        "analyzer": "content_analyzer",
                        "fields": {
                            "keyword": {"type": "keyword", "ignore_above": 256}
                        }
                    },
                    "description": {
                        "type": "text",
                        "analyzer": "content_analyzer"
                    },
                    "tags": {"type": "keyword"},
                    "metadata": {"type": "object"},
                    "quality_score": {"type": "float"},
                    "similarity_features": {"type": "dense_vector", "dims": 512},
                    "created_at": {"type": "date"},
                    "updated_at": {"type": "date"}
                }
            }
        }
    }
    
    PROTECTION_ALERTS = {
        "index_patterns": ["protection_alerts_*"],
        "template": {
            "settings": {
                "number_of_shards": 2,
                "number_of_replicas": 1,
                "refresh_interval": "5s"
            },
            "mappings": {
                "properties": {
                    "alert_id": {"type": "keyword"},
                    "fingerprint_id": {"type": "keyword"},
                    "detected_url": {"type": "keyword"},
                    "platform": {"type": "keyword"},
                    "similarity_score": {"type": "float"},
                    "status": {"type": "keyword"},
                    "evidence_data": {"type": "object"},
                    "location": {"type": "geo_point"},
                    "detected_at": {"type": "date"},
                    "resolved_at": {"type": "date"}
                }
            }
        }
    }
    
    ANALYTICS_DATA = {
        "index_patterns": ["analytics_*"],
        "template": {
            "settings": {
                "number_of_shards": 5,
                "number_of_replicas": 1,
                "refresh_interval": "10s"
            },
            "mappings": {
                "properties": {
                    "event_id": {"type": "keyword"},
                    "user_id": {"type": "keyword"},
                    "content_id": {"type": "keyword"},
                    "event_type": {"type": "keyword"},
                    "platform": {"type": "keyword"},
                    "metrics": {
                        "properties": {
                            "views": {"type": "long"},
                            "likes": {"type": "long"},
                            "shares": {"type": "long"},
                            "engagement_rate": {"type": "float"},
                            "revenue": {"type": "float"}
                        }
                    },
                    "dimensions": {"type": "object"},
                    "timestamp": {"type": "date"}
                }
            }
        }
    }
    
    SEARCH_LOGS = {
        "index_patterns": ["search_logs_*"],
        "template": {
            "settings": {
                "number_of_shards": 1,
                "number_of_replicas": 0,
                "refresh_interval": "60s"
            },
            "mappings": {
                "properties": {
                    "query_id": {"type": "keyword"},
                    "user_id": {"type": "keyword"},
                    "query_text": {
                        "type": "text",
                        "analyzer": "content_analyzer"
                    },
                    "search_type": {"type": "keyword"},
                    "results_count": {"type": "integer"},
                    "response_time": {"type": "float"},
                    "clicked_results": {"type": "keyword"},
                    "timestamp": {"type": "date"}
                }
            }
        }
    }

class ElasticsearchIndexManager:
    """
    Advanced Elasticsearch index manager for IA-Influencer platform
    
    Provides comprehensive search and analytics capabilities for:
    - Content fingerprint search
    - Protection alert monitoring
    - User behavior analytics
    - Multi-language content discovery
    - Real-time data aggregation
    """
    
    def __init__(self):
        """Initialize Elasticsearch index manager"""
        self.es_connection = ElasticsearchConnection()
        self.performance_tracker = PerformanceTracker()
        self.security_manager = SearchSecurityManager()
        self.client: Optional[AsyncElasticsearch] = None
        
        # Index management
        self.active_indexes = set()
        self.index_aliases = {}
        self.template_registry = {
            'content_fingerprints': IndexTemplate.CONTENT_FINGERPRINTS,
            'protection_alerts': IndexTemplate.PROTECTION_ALERTS,
            'analytics_data': IndexTemplate.ANALYTICS_DATA,
            'search_logs': IndexTemplate.SEARCH_LOGS
        }
        
        # Performance settings
        self.bulk_size = 1000
        self.refresh_interval = "30s"
        self.max_result_window = 10000
        self.default_timeout = 30
        
        logger.info("ElasticsearchIndexManager initialized")
    
    async def initialize(self) -> bool:
        """Initialize Elasticsearch index manager"""
        try:
            # Initialize Elasticsearch connection
            if not await self.es_connection.initialize():
                raise Exception("Failed to initialize Elasticsearch connection")
            
            self.client = self.es_connection.get_client()
            
            # Initialize performance tracking
            await self.performance_tracker.initialize()
            
            # Initialize security manager
            await self.security_manager.initialize()
            
            # Setup index templates
            await self._setup_index_templates()
            
            # Load existing indexes
            await self._load_existing_indexes()
            
            # Setup monitoring
            await self._setup_index_monitoring()
            
            logger.info("ElasticsearchIndexManager initialization completed")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize ElasticsearchIndexManager: {str(e)}")
            return False
    
    async def _setup_index_templates(self):
        """Setup Elasticsearch index templates"""
        try:
            for template_name, template_config in self.template_registry.items():
                try:
                    await self.client.indices.put_index_template(
                        name=template_name,
                        body=template_config,
                        timeout=f"{self.default_timeout}s"
                    )
                    logger.info(f"Index template {template_name} created/updated")
                    
                except RequestError as e:
                    if "already exists" not in str(e):
                        logger.error(f"Failed to create template {template_name}: {str(e)}")
                        
        except Exception as e:
            logger.error(f"Failed to setup index templates: {str(e)}")
            raise
    
    async def create_index(self, index_name: str, config: Dict[str, Any]) -> bool:
        """Create a new Elasticsearch index with specified configuration"""
        try:
            # Validate security permissions
            if not await self.security_manager.validate_index_creation(index_name):
                raise Exception("Index creation not authorized")
            
            # Build index configuration
            index_config = await self._build_index_config(config)
            
            start_time = datetime.now()
            
            # Create index
            response = await self.client.indices.create(
                index=index_name,
                body=index_config,
                timeout=f"{self.default_timeout}s"
            )
            
            creation_time = (datetime.now() - start_time).total_seconds()
            
            if response.get('acknowledged'):
                self.active_indexes.add(index_name)
                
                # Setup alias if specified
                alias_name = config.get('alias')
                if alias_name:
                    await self._create_alias(index_name, alias_name)
                
                # Log performance metrics
                await self.performance_tracker.log_index_operation(
                    index_name, 'create', creation_time, config
                )
                
                logger.info(f"Elasticsearch index {index_name} created successfully in {creation_time:.2f}s")
                return True
            else:
                logger.error(f"Failed to create index {index_name}: {response}")
                return False
                
        except Exception as e:
            logger.error(f"Failed to create Elasticsearch index {index_name}: {str(e)}")
            return False
    
    async def _build_index_config(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Build optimized index configuration"""
        # Default settings
        index_config = {
            "settings": {
                "number_of_shards": config.get('shards', 1),
                "number_of_replicas": config.get('replicas', 1),
                "refresh_interval": config.get('refresh_interval', self.refresh_interval),
                "max_result_window": config.get('max_result_window', self.max_result_window),
                "analysis": {
                    "analyzer": {
                        "default": {
                            "type": "standard",
                            "stopwords": "_english_"
                        },
                        "multilingual": {
                            "type": "custom",
                            "tokenizer": "standard",
                            "filter": ["lowercase", "stop", "snowball"]
                        }
                    }
                }
            }
        }
        
        # Add mappings if provided
        if 'mappings' in config:
            index_config['mappings'] = config['mappings']
        
        # Add custom analyzers
        if 'analyzers' in config:
            index_config['settings']['analysis']['analyzer'].update(config['analyzers'])
        
        return index_config
    
    async def _create_alias(self, index_name: str, alias_name: str):
        """Create index alias for easier management"""
        try:
            await self.client.indices.put_alias(
                index=index_name,
                name=alias_name
            )
            
            self.index_aliases[alias_name] = index_name
            logger.info(f"Alias {alias_name} created for index {index_name}")
            
        except Exception as e:
            logger.error(f"Failed to create alias {alias_name}: {str(e)}")
    
    async def index_document(self, index_name: str, document: Dict[str, Any],
                           doc_id: Optional[str] = None) -> bool:
        """Index a single document"""
        try:
            start_time = datetime.now()
            
            response = await self.client.index(
                index=index_name,
                body=document,
                id=doc_id,
                timeout=f"{self.default_timeout}s"
            )
            
            index_time = (datetime.now() - start_time).total_seconds()
            
            # Log performance
            await self.performance_tracker.log_index_operation(
                index_name, 'index_document', index_time, {'doc_size': len(str(document))}
            )
            
            return response.get('result') in ['created', 'updated']
            
        except Exception as e:
            logger.error(f"Failed to index document in {index_name}: {str(e)}")
            return False
    
    async def bulk_index_documents(self, index_name: str, documents: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Bulk index multiple documents for better performance"""
        try:
            if not documents:
                return {'indexed': 0, 'errors': []}
            
            # Prepare bulk request
            bulk_body = []
            for doc in documents:
                bulk_body.append({"index": {"_index": index_name}})
                bulk_body.append(doc)
            
            start_time = datetime.now()
            
            # Process in batches
            total_indexed = 0
            errors = []
            
            for i in range(0, len(bulk_body), self.bulk_size * 2):  # *2 because each doc has 2 lines
                batch = bulk_body[i:i + self.bulk_size * 2]
                
                try:
                    response = await self.client.bulk(
                        body=batch,
                        timeout=f"{self.default_timeout}s"
                    )
                    
                    # Process response
                    for item in response['items']:
                        if 'index' in item:
                            if item['index']['status'] in [200, 201]:
                                total_indexed += 1
                            else:
                                errors.append(item['index'])
                        
                except Exception as e:
                    errors.append(str(e))
            
            bulk_time = (datetime.now() - start_time).total_seconds()
            
            # Log performance
            await self.performance_tracker.log_index_operation(
                index_name, 'bulk_index', bulk_time, 
                {'document_count': len(documents), 'indexed_count': total_indexed, 'error_count': len(errors)}
            )
            
            logger.info(f"Bulk indexed {total_indexed}/{len(documents)} documents in {index_name}")
            
            return {
                'indexed': total_indexed,
                'total': len(documents),
                'errors': errors,
                'time_taken': bulk_time
            }
            
        except Exception as e:
            logger.error(f"Failed to bulk index documents in {index_name}: {str(e)}")
            return {'indexed': 0, 'errors': [str(e)]}
    
    async def search(self, index_name: str, query: Dict[str, Any], 
                    size: int = 10, from_: int = 0) -> Dict[str, Any]:
        """Perform advanced search with analytics"""
        try:
            start_time = datetime.now()
            
            # Build search request
            search_body = {
                "query": query,
                "size": size,
                "from": from_,
                "track_total_hits": True
            }
            
            # Add highlighting if requested
            if 'highlight' in query:
                search_body['highlight'] = {
                    "fields": {
                        "*": {}
                    }
                }
            
            # Execute search
            response = await self.client.search(
                index=index_name,
                body=search_body,
                timeout=f"{self.default_timeout}s"
            )
            
            search_time = (datetime.now() - start_time).total_seconds()
            
            # Process results
            results = {
                'total_hits': response['hits']['total']['value'],
                'hits': response['hits']['hits'],
                'search_time': search_time,
                'aggregations': response.get('aggregations', {}),
                'suggest': response.get('suggest', {})
            }
            
            # Log search analytics
            await self._log_search_analytics(index_name, query, results, search_time)
            
            # Log performance
            await self.performance_tracker.log_index_operation(
                index_name, 'search', search_time,
                {'results_count': results['total_hits'], 'query_complexity': len(str(query))}
            )
            
            return results
            
        except Exception as e:
            logger.error(f"Failed to search in index {index_name}: {str(e)}")
            return {'total_hits': 0, 'hits': [], 'error': str(e)}
    
    async def multi_search(self, searches: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Perform multiple searches in a single request"""
        try:
            # Build multi-search request
            msearch_body = []
            for search in searches:
                msearch_body.append({"index": search['index']})
                msearch_body.append(search['body'])
            
            start_time = datetime.now()
            
            response = await self.client.msearch(
                body=msearch_body,
                timeout=f"{self.default_timeout}s"
            )
            
            search_time = (datetime.now() - start_time).total_seconds()
            
            # Process responses
            results = []
            for i, resp in enumerate(response['responses']):
                if 'error' in resp:
                    results.append({'error': resp['error']})
                else:
                    results.append({
                        'total_hits': resp['hits']['total']['value'],
                        'hits': resp['hits']['hits'],
                        'aggregations': resp.get('aggregations', {})
                    })
            
            # Log performance
            await self.performance_tracker.log_index_operation(
                'multi_search', 'multi_search', search_time,
                {'search_count': len(searches)}
            )
            
            return results
            
        except Exception as e:
            logger.error(f"Failed to execute multi-search: {str(e)}")
            return [{'error': str(e)} for _ in searches]
    
    async def aggregate_data(self, index_name: str, aggregations: Dict[str, Any]) -> Dict[str, Any]:
        """Perform advanced data aggregations"""
        try:
            start_time = datetime.now()
            
            search_body = {
                "size": 0,  # We only want aggregations
                "aggs": aggregations
            }
            
            response = await self.client.search(
                index=index_name,
                body=search_body,
                timeout=f"{self.default_timeout}s"
            )
            
            agg_time = (datetime.now() - start_time).total_seconds()
            
            # Log performance
            await self.performance_tracker.log_index_operation(
                index_name, 'aggregation', agg_time,
                {'aggregation_count': len(aggregations)}
            )
            
            return response.get('aggregations', {})
            
        except Exception as e:
            logger.error(f"Failed to aggregate data in {index_name}: {str(e)}")
            return {'error': str(e)}
    
    async def _log_search_analytics(self, index_name: str, query: Dict[str, Any], 
                                   results: Dict[str, Any], search_time: float):
        """Log search analytics for performance monitoring"""
        try:
            analytics_doc = {
                'index_name': index_name,
                'query_type': self._determine_query_type(query),
                'results_count': results['total_hits'],
                'search_time': search_time,
                'timestamp': datetime.now()
            }
            
            # Log to search analytics index (fire and forget)
            asyncio.create_task(
                self.index_document('search_logs', analytics_doc)
            )
            
        except Exception as e:
            logger.debug(f"Failed to log search analytics: {str(e)}")
    
    def _determine_query_type(self, query: Dict[str, Any]) -> str:
        """Determine the type of search query for analytics"""
        if 'match_all' in query:
            return 'match_all'
        elif 'bool' in query:
            return 'bool'
        elif 'match' in query:
            return 'match'
        elif 'term' in query:
            return 'term'
        elif 'range' in query:
            return 'range'
        elif 'wildcard' in query:
            return 'wildcard'
        else:
            return 'complex'
    
    async def optimize_index(self, index_name: str) -> bool:
        """Optimize index for better performance"""
        try:
            start_time = datetime.now()
            
            # Force merge segments
            response = await self.client.indices.forcemerge(
                index=index_name,
                max_num_segments=1,
                wait_for_completion=True,
                timeout=f"{self.default_timeout * 5}s"
            )
            
            optimization_time = (datetime.now() - start_time).total_seconds()
            
            # Log performance
            await self.performance_tracker.log_index_operation(
                index_name, 'optimize', optimization_time
            )
            
            logger.info(f"Index {index_name} optimized in {optimization_time:.2f}s")
            return True
            
        except Exception as e:
            logger.error(f"Failed to optimize index {index_name}: {str(e)}")
            return False
    
    async def get_index_stats(self, index_name: Optional[str] = None) -> Dict[str, Any]:
        """Get comprehensive index statistics"""
        try:
            if index_name:
                response = await self.client.indices.stats(index=index_name)
                
                index_stats = response['indices'].get(index_name, {})
                return {
                    'index_name': index_name,
                    'document_count': index_stats.get('total', {}).get('docs', {}).get('count', 0),
                    'store_size': index_stats.get('total', {}).get('store', {}).get('size_in_bytes', 0),
                    'search_stats': index_stats.get('total', {}).get('search', {}),
                    'indexing_stats': index_stats.get('total', {}).get('indexing', {})
                }
            else:
                response = await self.client.indices.stats()
                
                stats = {
                    'total_indexes': len(response['indices']),
                    'total_documents': 0,
                    'total_size': 0,
                    'indexes': {}
                }
                
                for idx_name, idx_stats in response['indices'].items():
                    doc_count = idx_stats.get('total', {}).get('docs', {}).get('count', 0)
                    size = idx_stats.get('total', {}).get('store', {}).get('size_in_bytes', 0)
                    
                    stats['total_documents'] += doc_count
                    stats['total_size'] += size
                    stats['indexes'][idx_name] = {
                        'document_count': doc_count,
                        'store_size': size
                    }
                
                return stats
                
        except Exception as e:
            logger.error(f"Failed to get index stats: {str(e)}")
            return {'error': str(e)}
    
    async def _load_existing_indexes(self):
        """Load information about existing indexes"""
        try:
            response = await self.client.indices.get_alias(index="*")
            
            for index_name in response.keys():
                if not index_name.startswith('.'):  # Skip system indexes
                    self.active_indexes.add(index_name)
            
            logger.info(f"Loaded {len(self.active_indexes)} existing Elasticsearch indexes")
            
        except Exception as e:
            logger.error(f"Failed to load existing indexes: {str(e)}")
    
    async def _setup_index_monitoring(self):
        """Setup monitoring for index health and performance"""
        # This would typically setup periodic health checks
        pass
    
    async def cleanup(self):
        """Cleanup resources and connections"""
        try:
            if self.performance_tracker:
                await self.performance_tracker.cleanup()
            if self.security_manager:
                await self.security_manager.cleanup()
            if self.es_connection:
                await self.es_connection.cleanup()
            
            logger.info("ElasticsearchIndexManager cleanup completed")
            
        except Exception as e:
            logger.error(f"Error during ElasticsearchIndexManager cleanup: {str(e)}")
