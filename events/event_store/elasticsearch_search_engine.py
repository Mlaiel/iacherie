"""🚀 Elasticsearch Search Engine - IA Influencer Agent Platform
===============================================================
Module: events/event_store/elasticsearch_search_engine.py
Author: Fahed Mlaiel (mlaiel@live.de)
===============================================================

⚠️ PROPRIÉTÉ INTELLECTUELLE EXCLUSIVE - FAHED MLAIEL ⚠️
(c) 2025 Fahed Mlaiel. Tous droits réservés.
Contact: mlaiel@live.de

🎯 ELASTICSEARCH SEARCH ENGINE
High-performance Elasticsearch integration for full-text search,
analytics aggregations, and real-time monitoring of Ainflue events.

Key Features:
- Full-text search across event content and metadata
- Real-time analytics and aggregations
- Business intelligence dashboards
- Anomaly detection and alerting
- Performance monitoring and visualization
- Advanced search with filters and facets
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, AsyncIterator
from decimal import Decimal
import json

try:
    from elasticsearch import AsyncElasticsearch
    from elasticsearch.exceptions import ElasticsearchException, NotFoundError
    ELASTICSEARCH_AVAILABLE = True
except ImportError:
    ELASTICSEARCH_AVAILABLE = False
    # Create placeholder classes
    class AsyncElasticsearch: pass
    class ElasticsearchException(Exception): pass
    class NotFoundError(Exception): pass

from ..core.base_event import BaseEvent
from .enterprise_store_interface import (
    IEventStoreBackend, EventQuery, StreamConfig, StoreResult, StorageBackendType
)

logger = logging.getLogger(__name__)

if not ELASTICSEARCH_AVAILABLE:
    logger.warning("Elasticsearch not available - install with: pip install elasticsearch")


class ElasticsearchSearchEngine(IEventStoreBackend):
    """
    Elasticsearch search engine for Ainflue platform
    
    Optimized for:
    - Full-text search across content and metadata
    - Real-time analytics and business intelligence
    - Performance monitoring and alerting
    - Content discovery and recommendations
    - SEO analytics and optimization
    - Anomaly detection and trend analysis
    """
    
    def __init__(self, connection_config: Dict[str, Any]):
        if not ELASTICSEARCH_AVAILABLE:
            raise ImportError("Elasticsearch not available. Install with: pip install elasticsearch")
        
        self.config = connection_config
        self.client: Optional[AsyncElasticsearch] = None
        self._is_initialized = False
        self._indices = {}
        self._metrics = {
            'events_indexed': 0,
            'total_latency': 0.0,
            'latency_samples': 0,
            'errors': 0,
            'searches_executed': 0,
            'aggregations_executed': 0
        }
        
        # Index names for different event types
        self.index_names = {
            'content_events': 'ainflue-content-events',
            'user_events': 'ainflue-user-events',
            'revenue_events': 'ainflue-revenue-events',
            'performance_events': 'ainflue-performance-events',
            'search_events': 'ainflue-search-events',
            'analytics_events': 'ainflue-analytics-events'
        }
    
    async def initialize(self):
        """Initialize Elasticsearch connection and indices"""
        try:
            # Create Elasticsearch client
            hosts = self.config.get('hosts', ['localhost:9200'])
            
            client_config = {
                'hosts': hosts,
                'timeout': self.config.get('timeout', 30),
                'retry_on_timeout': True,
                'max_retries': self.config.get('max_retries', 3)
            }
            
            # Add authentication if configured
            if self.config.get('username') and self.config.get('password'):
                client_config['http_auth'] = (
                    self.config['username'], 
                    self.config['password']
                )
            
            # Add SSL/TLS if configured
            if self.config.get('use_ssl', False):
                client_config['use_ssl'] = True
                client_config['verify_certs'] = self.config.get('verify_certs', True)
                if self.config.get('ca_certs'):
                    client_config['ca_certs'] = self.config['ca_certs']
            
            self.client = AsyncElasticsearch(**client_config)
            
            # Test connection
            cluster_info = await self.client.info()
            logger.info(f"Connected to Elasticsearch cluster: {cluster_info['cluster_name']}")
            
            # Initialize indices with optimized mappings
            await self._initialize_indices()
            
            # Setup index templates
            await self._setup_index_templates()
            
            # Create index aliases
            await self._setup_index_aliases()
            
            self._is_initialized = True
            logger.info("Elasticsearch Search Engine initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize Elasticsearch search engine: {e}")
            raise
    
    async def _initialize_indices(self):
        """Initialize indices with optimized mappings for Ainflue events"""
        
        # Content events index
        await self._create_index_if_not_exists(
            self.index_names['content_events'],
            self._get_content_events_mapping()
        )
        
        # User events index
        await self._create_index_if_not_exists(
            self.index_names['user_events'],
            self._get_user_events_mapping()
        )
        
        # Revenue events index
        await self._create_index_if_not_exists(
            self.index_names['revenue_events'],
            self._get_revenue_events_mapping()
        )
        
        # Performance events index
        await self._create_index_if_not_exists(
            self.index_names['performance_events'],
            self._get_performance_events_mapping()
        )
        
        # Search events index
        await self._create_index_if_not_exists(
            self.index_names['search_events'],
            self._get_search_events_mapping()
        )
        
        # Analytics events index
        await self._create_index_if_not_exists(
            self.index_names['analytics_events'],
            self._get_analytics_events_mapping()
        )
    
    async def _create_index_if_not_exists(self, index_name: str, mapping: Dict[str, Any]):
        """Create index if it doesn't exist"""
        try:
            exists = await self.client.indices.exists(index=index_name)
            if not exists:
                await self.client.indices.create(
                    index=index_name,
                    body=mapping
                )
                logger.info(f"Created index: {index_name}")
            else:
                logger.info(f"Index already exists: {index_name}")
                
        except Exception as e:
            logger.error(f"Failed to create index {index_name}: {e}")
            raise
    
    def _get_content_events_mapping(self) -> Dict[str, Any]:
        """Get optimized mapping for content events"""
        return {
            "settings": {
                "number_of_shards": self.config.get('shards', 3),
                "number_of_replicas": self.config.get('replicas', 1),
                "analysis": {
                    "analyzer": {
                        "content_analyzer": {
                            "tokenizer": "standard",
                            "filter": ["lowercase", "stop", "snowball"]
                        }
                    }
                }
            },
            "mappings": {
                "properties": {
                    "event_id": {"type": "keyword"},
                    "event_type": {"type": "keyword"},
                    "occurred_at": {"type": "date"},
                    "created_at": {"type": "date"},
                    
                    # Content-specific fields
                    "creator_id": {"type": "keyword"},
                    "content_id": {"type": "keyword"},
                    "content_type": {"type": "keyword"},
                    "title": {
                        "type": "text",
                        "analyzer": "content_analyzer",
                        "fields": {
                            "keyword": {"type": "keyword"}
                        }
                    },
                    "description": {
                        "type": "text",
                        "analyzer": "content_analyzer"
                    },
                    "tags": {"type": "keyword"},
                    "category": {"type": "keyword"},
                    
                    # Content metrics
                    "file_size": {"type": "long"},
                    "duration": {"type": "float"},
                    "views": {"type": "long"},
                    "likes": {"type": "long"},
                    "shares": {"type": "long"},
                    "comments": {"type": "long"},
                    "engagement_score": {"type": "float"},
                    
                    # AI processing fields
                    "ai_model": {"type": "keyword"},
                    "processing_type": {"type": "keyword"},
                    "confidence_score": {"type": "float"},
                    "ai_results": {"type": "object"},
                    
                    # SEO fields
                    "seo_score": {"type": "float"},
                    "keywords": {"type": "keyword"},
                    "meta_description": {"type": "text"},
                    
                    # Event metadata
                    "source": {"type": "keyword"},
                    "priority": {"type": "keyword"},
                    "status": {"type": "keyword"},
                    "correlation_id": {"type": "keyword"},
                    "metadata": {"type": "object"}
                }
            }
        }
    
    def _get_user_events_mapping(self) -> Dict[str, Any]:
        """Get optimized mapping for user events"""
        return {
            "settings": {
                "number_of_shards": self.config.get('shards', 3),
                "number_of_replicas": self.config.get('replicas', 1)
            },
            "mappings": {
                "properties": {
                    "event_id": {"type": "keyword"},
                    "event_type": {"type": "keyword"},
                    "occurred_at": {"type": "date"},
                    
                    # User-specific fields
                    "user_id": {"type": "keyword"},
                    "creator_id": {"type": "keyword"},
                    "username": {"type": "keyword"},
                    "creator_type": {"type": "keyword"},
                    "email": {"type": "keyword"},
                    
                    # User interaction fields
                    "session_id": {"type": "keyword"},
                    "platform": {"type": "keyword"},
                    "device_type": {"type": "keyword"},
                    "location": {"type": "geo_point"},
                    "ip_address": {"type": "ip"},
                    
                    # Collaboration fields
                    "collaboration_id": {"type": "keyword"},
                    "collaboration_type": {"type": "keyword"},
                    "participants": {"type": "keyword"},
                    
                    # Activity metrics
                    "activity_score": {"type": "float"},
                    "interaction_count": {"type": "long"},
                    
                    # Event metadata
                    "source": {"type": "keyword"},
                    "priority": {"type": "keyword"},
                    "metadata": {"type": "object"}
                }
            }
        }
    
    def _get_revenue_events_mapping(self) -> Dict[str, Any]:
        """Get optimized mapping for revenue events"""
        return {
            "settings": {
                "number_of_shards": self.config.get('shards', 3),
                "number_of_replicas": self.config.get('replicas', 1)
            },
            "mappings": {
                "properties": {
                    "event_id": {"type": "keyword"},
                    "event_type": {"type": "keyword"},
                    "occurred_at": {"type": "date"},
                    
                    # Revenue fields
                    "creator_id": {"type": "keyword"},
                    "content_id": {"type": "keyword"},
                    "revenue_amount": {"type": "double"},
                    "currency": {"type": "keyword"},
                    "revenue_source": {"type": "keyword"},
                    "payment_method": {"type": "keyword"},
                    "transaction_id": {"type": "keyword"},
                    
                    # Monetization fields
                    "licensing_type": {"type": "keyword"},
                    "royalty_rate": {"type": "float"},
                    "payout_status": {"type": "keyword"},
                    
                    # Business metrics
                    "conversion_rate": {"type": "float"},
                    "lifetime_value": {"type": "double"},
                    
                    # Event metadata
                    "source": {"type": "keyword"},
                    "priority": {"type": "keyword"},
                    "metadata": {"type": "object"}
                }
            }
        }
    
    def _get_performance_events_mapping(self) -> Dict[str, Any]:
        """Get optimized mapping for performance events"""
        return {
            "settings": {
                "number_of_shards": self.config.get('shards', 2),
                "number_of_replicas": self.config.get('replicas', 1)
            },
            "mappings": {
                "properties": {
                    "event_id": {"type": "keyword"},
                    "event_type": {"type": "keyword"},
                    "occurred_at": {"type": "date"},
                    
                    # Performance metrics
                    "component": {"type": "keyword"},
                    "operation": {"type": "keyword"},
                    "duration_ms": {"type": "long"},
                    "latency_ms": {"type": "long"},
                    "throughput": {"type": "float"},
                    "error_rate": {"type": "float"},
                    "cpu_usage": {"type": "float"},
                    "memory_usage": {"type": "float"},
                    "disk_usage": {"type": "float"},
                    
                    # System health
                    "status": {"type": "keyword"},
                    "severity": {"type": "keyword"},
                    "alert_level": {"type": "keyword"},
                    
                    # Event metadata
                    "source": {"type": "keyword"},
                    "metadata": {"type": "object"}
                }
            }
        }
    
    def _get_search_events_mapping(self) -> Dict[str, Any]:
        """Get optimized mapping for search events"""
        return {
            "settings": {
                "number_of_shards": self.config.get('shards', 2),
                "number_of_replicas": self.config.get('replicas', 1)
            },
            "mappings": {
                "properties": {
                    "event_id": {"type": "keyword"},
                    "event_type": {"type": "keyword"},
                    "occurred_at": {"type": "date"},
                    
                    # Search fields
                    "query_text": {
                        "type": "text",
                        "analyzer": "standard"
                    },
                    "user_id": {"type": "keyword"},
                    "search_filters": {"type": "object"},
                    "results_count": {"type": "long"},
                    "click_through_rate": {"type": "float"},
                    
                    # SEO and discovery
                    "keywords": {"type": "keyword"},
                    "search_intent": {"type": "keyword"},
                    "ranking_position": {"type": "integer"},
                    
                    # Event metadata
                    "source": {"type": "keyword"},
                    "metadata": {"type": "object"}
                }
            }
        }
    
    def _get_analytics_events_mapping(self) -> Dict[str, Any]:
        """Get optimized mapping for analytics events"""
        return {
            "settings": {
                "number_of_shards": self.config.get('shards', 3),
                "number_of_replicas": self.config.get('replicas', 1)
            },
            "mappings": {
                "properties": {
                    "event_id": {"type": "keyword"},
                    "event_type": {"type": "keyword"},
                    "occurred_at": {"type": "date"},
                    
                    # Analytics dimensions
                    "creator_id": {"type": "keyword"},
                    "content_id": {"type": "keyword"},
                    "user_id": {"type": "keyword"},
                    "platform": {"type": "keyword"},
                    "campaign_id": {"type": "keyword"},
                    
                    # Metrics
                    "metric_name": {"type": "keyword"},
                    "metric_value": {"type": "double"},
                    "metric_unit": {"type": "keyword"},
                    
                    # Aggregated data
                    "daily_metrics": {"type": "object"},
                    "weekly_metrics": {"type": "object"},
                    "monthly_metrics": {"type": "object"},
                    
                    # Event metadata
                    "source": {"type": "keyword"},
                    "metadata": {"type": "object"}
                }
            }
        }
    
    async def _setup_index_templates(self):
        """Setup index templates for automatic index creation"""
        
        # Template for time-based indices
        template_body = {
            "index_patterns": ["ainflue-*"],
            "settings": {
                "number_of_shards": self.config.get('shards', 3),
                "number_of_replicas": self.config.get('replicas', 1),
                "refresh_interval": "5s"
            }
        }
        
        try:
            await self.client.indices.put_template(
                name="ainflue-template",
                body=template_body
            )
            logger.info("Created index template")
        except Exception as e:
            logger.warning(f"Failed to create index template: {e}")
    
    async def _setup_index_aliases(self):
        """Setup index aliases for easier querying"""
        
        aliases = {
            "ainflue-all-events": list(self.index_names.values()),
            "ainflue-business-events": [
                self.index_names['content_events'],
                self.index_names['user_events'],
                self.index_names['revenue_events']
            ],
            "ainflue-monitoring": [
                self.index_names['performance_events'],
                self.index_names['analytics_events']
            ]
        }
        
        for alias_name, indices in aliases.items():
            try:
                await self.client.indices.put_alias(
                    index=indices,
                    name=alias_name
                )
                logger.info(f"Created alias: {alias_name}")
            except Exception as e:
                logger.warning(f"Failed to create alias {alias_name}: {e}")
    
    async def store_event(self, event: BaseEvent) -> StoreResult:
        """Store event in appropriate Elasticsearch index"""
        start_time = datetime.utcnow()
        
        try:
            # Determine target index
            index_name = self._get_index_for_event(event)
            
            # Prepare document
            document = self._prepare_search_document(event)
            
            # Index document
            result = await self.client.index(
                index=index_name,
                id=event.event_id,
                body=document,
                refresh='wait_for'  # Ensure document is searchable immediately
            )
            
            # Update metrics
            latency = (datetime.utcnow() - start_time).total_seconds() * 1000
            self._metrics['events_indexed'] += 1
            self._metrics['total_latency'] += latency
            self._metrics['latency_samples'] += 1
            
            return StoreResult(
                success=True,
                event_id=event.event_id,
                backends_used=[StorageBackendType.ELASTICSEARCH],
                latency_ms=latency,
                metadata={
                    'index': index_name,
                    'elasticsearch_id': result['_id'],
                    'result': result['result']
                }
            )
            
        except Exception as e:
            self._metrics['errors'] += 1
            logger.error(f"Failed to index event {event.event_id}: {e}")
            return StoreResult(
                success=False,
                event_id=event.event_id,
                backends_used=[],
                latency_ms=(datetime.utcnow() - start_time).total_seconds() * 1000,
                errors=[str(e)]
            )
    
    def _get_index_for_event(self, event: BaseEvent) -> str:
        """Determine appropriate index for event type"""
        
        event_type = event.event_type.lower()
        
        # Content events
        if 'content' in event_type or 'media' in event_type or 'seo' in event_type:
            return self.index_names['content_events']
        
        # User events
        elif 'user' in event_type or 'creator' in event_type or 'collaboration' in event_type:
            return self.index_names['user_events']
        
        # Revenue events
        elif 'revenue' in event_type or 'payment' in event_type or 'monetization' in event_type:
            return self.index_names['revenue_events']
        
        # Performance events
        elif 'performance' in event_type or 'system' in event_type or 'health' in event_type:
            return self.index_names['performance_events']
        
        # Search events
        elif 'search' in event_type or 'query' in event_type:
            return self.index_names['search_events']
        
        # Analytics events
        elif 'analytics' in event_type or 'metrics' in event_type:
            return self.index_names['analytics_events']
        
        # Default to content events
        else:
            return self.index_names['content_events']
    
    def _prepare_search_document(self, event: BaseEvent) -> Dict[str, Any]:
        """Prepare optimized document for Elasticsearch indexing"""
        
        document = {
            'event_id': event.event_id,
            'event_type': event.event_type,
            'occurred_at': event.timestamp.isoformat(),
            'created_at': datetime.utcnow().isoformat(),
            'source': getattr(event, 'source', None),
            'priority': str(getattr(event, 'priority', None)) if getattr(event, 'priority', None) else None,
            'status': str(getattr(event, 'status', None)) if getattr(event, 'status', None) else None,
            'correlation_id': getattr(event, 'correlation_id', None),
            'metadata': getattr(event, 'metadata', {})
        }
        
        # Extract and flatten event data for better searchability
        if event.data:
            data = event.data
            
            # Extract common business fields
            business_fields = {
                'creator_id': data.get('creator_id'),
                'content_id': data.get('content_id'),
                'content_type': data.get('content_type'),
                'user_id': data.get('user_id'),
                'collaboration_id': data.get('collaboration_id')
            }
            
            # Remove None values
            business_fields = {k: v for k, v in business_fields.items() if v is not None}
            document.update(business_fields)
            
            # Extract content-specific fields
            if 'content' in event.event_type:
                content_fields = {
                    'title': data.get('title'),
                    'description': data.get('description'),
                    'tags': data.get('tags', []),
                    'category': data.get('category'),
                    'file_size': data.get('file_size'),
                    'duration': data.get('duration'),
                    'views': data.get('views', 0),
                    'likes': data.get('likes', 0),
                    'shares': data.get('shares', 0),
                    'comments': data.get('comments', 0),
                    'engagement_score': data.get('engagement_score'),
                    'ai_model': data.get('ai_model'),
                    'processing_type': data.get('processing_type'),
                    'confidence_score': data.get('confidence_score'),
                    'seo_score': data.get('seo_score'),
                    'keywords': data.get('keywords', [])
                }
                
                content_fields = {k: v for k, v in content_fields.items() if v is not None}
                document.update(content_fields)
            
            # Extract revenue-specific fields
            if 'revenue' in event.event_type or 'payment' in event.event_type:
                revenue_fields = {
                    'revenue_amount': float(data.get('revenue_amount', 0)) if data.get('revenue_amount') else 0,
                    'currency': data.get('currency'),
                    'revenue_source': data.get('source'),
                    'payment_method': data.get('payment_method'),
                    'transaction_id': data.get('transaction_id')
                }
                
                revenue_fields = {k: v for k, v in revenue_fields.items() if v is not None}
                document.update(revenue_fields)
            
            # Extract performance-specific fields
            if 'performance' in event.event_type or 'system' in event.event_type:
                performance_fields = {
                    'component': data.get('component'),
                    'operation': data.get('operation'),
                    'duration_ms': data.get('duration_ms') or data.get('processing_time'),
                    'latency_ms': data.get('latency_ms'),
                    'throughput': data.get('throughput'),
                    'error_rate': data.get('error_rate'),
                    'cpu_usage': data.get('cpu_usage'),
                    'memory_usage': data.get('memory_usage'),
                    'severity': data.get('severity')
                }
                
                performance_fields = {k: v for k, v in performance_fields.items() if v is not None}
                document.update(performance_fields)
            
            # Store original event data for completeness
            document['event_data'] = data
        
        return document
    
    async def store_events_batch(self, events: List[BaseEvent]) -> List[StoreResult]:
        """Store multiple events using bulk indexing"""
        start_time = datetime.utcnow()
        results = []
        
        if not events:
            return results
        
        try:
            # Prepare bulk operations
            bulk_operations = []
            for event in events:
                index_name = self._get_index_for_event(event)
                document = self._prepare_search_document(event)
                
                # Index operation
                bulk_operations.append({
                    'index': {
                        '_index': index_name,
                        '_id': event.event_id
                    }
                })
                bulk_operations.append(document)
            
            # Execute bulk operation
            response = await self.client.bulk(
                body=bulk_operations,
                refresh='wait_for'
            )
            
            # Process results
            latency = (datetime.utcnow() - start_time).total_seconds() * 1000
            
            for i, item in enumerate(response['items']):
                event = events[i]
                index_result = item['index']
                
                if index_result.get('status', 200) < 300:
                    # Success
                    results.append(StoreResult(
                        success=True,
                        event_id=event.event_id,
                        backends_used=[StorageBackendType.ELASTICSEARCH],
                        latency_ms=latency / len(events),
                        metadata={
                            'index': index_result['_index'],
                            'elasticsearch_id': index_result['_id']
                        }
                    ))
                    self._metrics['events_indexed'] += 1
                else:
                    # Error
                    error_msg = index_result.get('error', {}).get('reason', 'Unknown error')
                    results.append(StoreResult(
                        success=False,
                        event_id=event.event_id,
                        backends_used=[],
                        latency_ms=0,
                        errors=[error_msg]
                    ))
                    self._metrics['errors'] += 1
            
            self._metrics['total_latency'] += latency
            self._metrics['latency_samples'] += 1
            
        except Exception as e:
            self._metrics['errors'] += 1
            logger.error(f"Bulk indexing failed: {e}")
            
            # Create error results for all events
            for event in events:
                results.append(StoreResult(
                    success=False,
                    event_id=event.event_id,
                    backends_used=[],
                    latency_ms=0,
                    errors=[str(e)]
                ))
        
        return results
    
    async def retrieve_events(self, query: EventQuery) -> List[BaseEvent]:
        """Retrieve events using Elasticsearch search"""
        
        try:
            # Build Elasticsearch query
            search_body = self._build_search_query(query)
            
            # Determine indices to search
            indices = self._get_indices_for_query(query)
            
            # Execute search
            response = await self.client.search(
                index=indices,
                body=search_body
            )
            
            # Convert hits to events
            events = []
            for hit in response['hits']['hits']:
                event = self._hit_to_event(hit)
                events.append(event)
            
            self._metrics['searches_executed'] += 1
            return events
            
        except Exception as e:
            self._metrics['errors'] += 1
            logger.error(f"Search failed: {e}")
            raise
    
    def _build_search_query(self, query: EventQuery) -> Dict[str, Any]:
        """Build Elasticsearch search query from EventQuery"""
        
        search_body = {
            'query': {
                'bool': {
                    'must': [],
                    'filter': []
                }
            },
            'sort': [
                {query.order_by: {'order': query.order_direction.lower()}}
            ],
            'size': query.limit,
            'from': query.offset
        }
        
        # Add filters
        if query.aggregate_id:
            search_body['query']['bool']['filter'].append({
                'term': {'aggregate_id': query.aggregate_id}
            })
        
        if query.event_types:
            search_body['query']['bool']['filter'].append({
                'terms': {'event_type': query.event_types}
            })
        
        if query.creator_id:
            search_body['query']['bool']['filter'].append({
                'term': {'creator_id': query.creator_id}
            })
        
        if query.content_type:
            search_body['query']['bool']['filter'].append({
                'term': {'content_type': query.content_type}
            })
        
        # Time range filter
        if query.start_time or query.end_time:
            time_range = {}
            if query.start_time:
                time_range['gte'] = query.start_time.isoformat()
            if query.end_time:
                time_range['lte'] = query.end_time.isoformat()
            
            search_body['query']['bool']['filter'].append({
                'range': {'occurred_at': time_range}
            })
        
        # If no filters, match all
        if not search_body['query']['bool']['filter'] and not search_body['query']['bool']['must']:
            search_body['query'] = {'match_all': {}}
        
        return search_body
    
    def _get_indices_for_query(self, query: EventQuery) -> List[str]:
        """Determine which indices to search based on query"""
        
        if query.event_types:
            indices = set()
            for event_type in query.event_types:
                if 'content' in event_type:
                    indices.add(self.index_names['content_events'])
                elif 'user' in event_type or 'creator' in event_type:
                    indices.add(self.index_names['user_events'])
                elif 'revenue' in event_type or 'payment' in event_type:
                    indices.add(self.index_names['revenue_events'])
                elif 'performance' in event_type:
                    indices.add(self.index_names['performance_events'])
                elif 'search' in event_type:
                    indices.add(self.index_names['search_events'])
                elif 'analytics' in event_type:
                    indices.add(self.index_names['analytics_events'])
                else:
                    indices.add(self.index_names['content_events'])
            
            return list(indices)
        
        # Search all indices
        return list(self.index_names.values())
    
    def _hit_to_event(self, hit: Dict[str, Any]) -> BaseEvent:
        """Convert Elasticsearch hit to BaseEvent"""
        
        source = hit['_source']
        
        event = BaseEvent(
            event_type=source['event_type'],
            data=source.get('event_data', {}),
            event_id=source['event_id'],
            timestamp=datetime.fromisoformat(source['occurred_at'].replace('Z', '+00:00')),
            metadata=source.get('metadata', {}),
            source=source.get('source')
        )
        
        return event
    
    async def stream_events(self, config: StreamConfig) -> AsyncIterator[BaseEvent]:
        """Stream events using scroll API for large result sets"""
        
        try:
            # Initial search with scroll
            search_body = {
                'query': config.filter_criteria or {'match_all': {}},
                'sort': [{'occurred_at': {'order': 'asc'}}],
                'size': config.batch_size
            }
            
            response = await self.client.search(
                index=list(self.index_names.values()),
                body=search_body,
                scroll='5m'  # Keep scroll context for 5 minutes
            )
            
            while response['hits']['hits']:
                # Yield events from current batch
                for hit in response['hits']['hits']:
                    event = self._hit_to_event(hit)
                    yield event
                
                # Get next batch
                scroll_id = response['_scroll_id']
                response = await self.client.scroll(
                    scroll_id=scroll_id,
                    scroll='5m'
                )
            
            # Clear scroll context
            if '_scroll_id' in response:
                await self.client.clear_scroll(scroll_id=response['_scroll_id'])
                
        except Exception as e:
            logger.error(f"Event streaming failed: {e}")
            raise
    
    async def search_content(self, search_text: str, 
                           filters: Dict[str, Any] = None,
                           limit: int = 20) -> List[Dict[str, Any]]:
        """Search content events with full-text search"""
        
        search_body = {
            'query': {
                'bool': {
                    'must': [
                        {
                            'multi_match': {
                                'query': search_text,
                                'fields': ['title^3', 'description^2', 'tags', 'keywords'],
                                'type': 'best_fields',
                                'fuzziness': 'AUTO'
                            }
                        }
                    ],
                    'filter': []
                }
            },
            'highlight': {
                'fields': {
                    'title': {},
                    'description': {}
                }
            },
            'size': limit
        }
        
        # Add filters
        if filters:
            for field, value in filters.items():
                search_body['query']['bool']['filter'].append({
                    'term': {field: value}
                })
        
        try:
            response = await self.client.search(
                index=self.index_names['content_events'],
                body=search_body
            )
            
            results = []
            for hit in response['hits']['hits']:
                result = {
                    'event_id': hit['_source']['event_id'],
                    'title': hit['_source'].get('title'),
                    'description': hit['_source'].get('description'),
                    'score': hit['_score'],
                    'highlights': hit.get('highlight', {})
                }
                results.append(result)
            
            self._metrics['searches_executed'] += 1
            return results
            
        except Exception as e:
            self._metrics['errors'] += 1
            logger.error(f"Content search failed: {e}")
            raise
    
    async def get_analytics_aggregation(self, aggregation_query: Dict[str, Any],
                                      index_type: str = 'analytics_events') -> Dict[str, Any]:
        """Execute analytics aggregation query"""
        
        try:
            index_name = self.index_names.get(index_type, self.index_names['analytics_events'])
            
            response = await self.client.search(
                index=index_name,
                body=aggregation_query
            )
            
            self._metrics['aggregations_executed'] += 1
            return response['aggregations']
            
        except Exception as e:
            self._metrics['errors'] += 1
            logger.error(f"Analytics aggregation failed: {e}")
            raise
    
    async def health_check(self) -> bool:
        """Check Elasticsearch cluster health"""
        try:
            if not self.client:
                return False
            
            health = await self.client.cluster.health()
            return health['status'] in ['green', 'yellow']
            
        except Exception as e:
            logger.error(f"Elasticsearch health check failed: {e}")
            return False
    
    async def get_metrics(self) -> Dict[str, Any]:
        """Get search engine performance metrics"""
        
        # Calculate derived metrics
        avg_latency = 0.0
        if self._metrics['latency_samples'] > 0:
            avg_latency = self._metrics['total_latency'] / self._metrics['latency_samples']
        
        # Get cluster stats
        cluster_stats = {}
        try:
            stats = await self.client.cluster.stats()
            cluster_stats = {
                'nodes_count': stats['nodes']['count']['total'],
                'indices_count': stats['indices']['count'],
                'docs_count': stats['indices']['docs']['count'],
                'store_size_bytes': stats['indices']['store']['size_in_bytes']
            }
        except Exception as e:
            logger.warning(f"Could not get cluster stats: {e}")
        
        return {
            'events_indexed': self._metrics['events_indexed'],
            'total_latency': self._metrics['total_latency'],
            'latency_samples': self._metrics['latency_samples'],
            'average_latency_ms': avg_latency,
            'errors': self._metrics['errors'],
            'searches_executed': self._metrics['searches_executed'],
            'aggregations_executed': self._metrics['aggregations_executed'],
            'error_rate': self._metrics['errors'] / max(self._metrics['events_indexed'], 1),
            'cluster_stats': cluster_stats
        }
    
    async def close(self):
        """Close Elasticsearch connection"""
        if self.client:
            await self.client.close()
            self._is_initialized = False
            logger.info("Elasticsearch Search Engine closed")


# Export public APIs
__all__ = [
    'ElasticsearchSearchEngine'
]