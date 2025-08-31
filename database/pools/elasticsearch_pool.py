"""
Elasticsearch Connection Pool - IA Influencer Agent + Content Protection Platform

Enterprise Elasticsearch connection pool for search indexing, content discovery,
logging, and real-time analytics for the content protection platform.

Features:
- Full-text search across content metadata
- Real-time content indexing and search
- Log aggregation and monitoring
- Multi-language content analysis
- Geospatial search for location-based content
- Analytics data aggregation
- Auto-scaling cluster management
- Search performance optimization

Search Capabilities:
- Content fingerprint similarity search
- User behavior pattern analysis
- Revenue trend analytics
- Protection alert correlation
- Cross-platform content matching
- Real-time content monitoring

Author: Fahed Mlaiel <mlaiel@live.de>
Project: IA Influencer Agent + Content Protection Platform
Team: Lead Dev IA + Backend Senior + ML Engineer + DBA + Security + Microservices + Audio + DevOps

WARNING: This code is proprietary and confidential. Any unauthorized use, modification,
or distribution is strictly prohibited and may result in legal action.
Contact: mlaiel@live.de for licensing inquiries.

Copyright (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass
from datetime import datetime, timedelta
import json

try:
    from elasticsearch import AsyncElasticsearch
    from elasticsearch.exceptions import ConnectionError, RequestError, TransportError
    from elasticsearch.helpers import async_bulk, async_scan
except ImportError as e:
    logging.warning(f"Elasticsearch dependency missing: {e}")

from .manager import IConnectionPool, PoolConfig, DatabaseConnectionInfo, ConnectionState

logger = logging.getLogger(__name__)

# =============== ELASTICSEARCH SPECIFIC CONFIGURATION ===============

@dataclass
class ElasticsearchPoolConfig(PoolConfig):
    """Extended Elasticsearch pool configuration"""
    # Elasticsearch specific settings
    use_ssl: bool = True
    verify_certs: bool = True
    ca_certs: Optional[str] = None
    client_cert: Optional[str] = None
    client_key: Optional[str] = None
    
    # Connection optimization
    max_retries: int = 3
    retry_on_timeout: bool = True
    retry_on_status: List[int] = None
    sniff_on_start: bool = True
    sniff_on_connection_fail: bool = True
    sniffer_timeout: int = 60
    
    # Index management
    index_prefix: str = "ia_influencer"
    number_of_shards: int = 3
    number_of_replicas: int = 1
    refresh_interval: str = "1s"
    
    # Search optimization
    max_result_window: int = 10000
    default_search_timeout: str = "30s"
    enable_source_compression: bool = True
    
    # Bulk operations
    bulk_chunk_size: int = 1000
    bulk_max_chunk_bytes: int = 100 * 1024 * 1024  # 100MB
    bulk_queue_size: int = 4
    
    # Analytics settings
    enable_analytics: bool = True
    analytics_retention_days: int = 365

# =============== INDEX MAPPINGS ===============

INDEX_MAPPINGS = {
    "content_fingerprints": {
        "mappings": {
            "properties": {
                "user_id": {"type": "keyword"},
                "content_type": {"type": "keyword"},
                "fingerprint_hash": {"type": "keyword"},
                "original_filename": {
                    "type": "text",
                    "analyzer": "standard",
                    "fields": {
                        "keyword": {"type": "keyword", "ignore_above": 256}
                    }
                },
                "vector_embedding": {"type": "dense_vector", "dims": 512},
                "metadata": {
                    "type": "object",
                    "properties": {
                        "duration": {"type": "float"},
                        "file_size": {"type": "long"},
                        "resolution": {"type": "keyword"},
                        "bitrate": {"type": "integer"},
                        "format": {"type": "keyword"},
                        "tags": {"type": "keyword"}
                    }
                },
                "created_at": {"type": "date"},
                "updated_at": {"type": "date"},
                "location": {"type": "geo_point"},
                "content_text": {
                    "type": "text",
                    "analyzer": "standard",
                    "fields": {
                        "english": {"type": "text", "analyzer": "english"},
                        "french": {"type": "text", "analyzer": "french"},
                        "german": {"type": "text", "analyzer": "german"}
                    }
                }
            }
        },
        "settings": {
            "number_of_shards": 3,
            "number_of_replicas": 1,
            "refresh_interval": "1s",
            "max_result_window": 10000,
            "analysis": {
                "analyzer": {
                    "content_analyzer": {
                        "tokenizer": "standard",
                        "filter": ["lowercase", "stop", "stemmer"]
                    }
                }
            }
        }
    },
    
    "protection_alerts": {
        "mappings": {
            "properties": {
                "fingerprint_id": {"type": "keyword"},
                "detected_url": {
                    "type": "text",
                    "analyzer": "keyword",
                    "fields": {
                        "domain": {"type": "keyword"}
                    }
                },
                "platform": {"type": "keyword"},
                "similarity_score": {"type": "float"},
                "status": {"type": "keyword"},
                "evidence_screenshot": {"type": "keyword"},
                "detection_method": {"type": "keyword"},
                "confidence_level": {"type": "float"},
                "created_at": {"type": "date"},
                "resolved_at": {"type": "date"},
                "location": {"type": "geo_point"},
                "user_agent": {"type": "text", "analyzer": "keyword"},
                "ip_address": {"type": "ip"},
                "false_positive": {"type": "boolean"}
            }
        },
        "settings": {
            "number_of_shards": 2,
            "number_of_replicas": 1,
            "refresh_interval": "5s"
        }
    },
    
    "analytics_events": {
        "mappings": {
            "properties": {
                "user_id": {"type": "keyword"},
                "content_id": {"type": "keyword"},
                "event_type": {"type": "keyword"},
                "platform": {"type": "keyword"},
                "metrics": {
                    "type": "object",
                    "properties": {
                        "views": {"type": "long"},
                        "likes": {"type": "long"},
                        "shares": {"type": "long"},
                        "comments": {"type": "long"},
                        "revenue": {"type": "float"},
                        "engagement_rate": {"type": "float"}
                    }
                },
                "timestamp": {"type": "date"},
                "session_id": {"type": "keyword"},
                "location": {"type": "geo_point"},
                "device_info": {
                    "type": "object",
                    "properties": {
                        "type": {"type": "keyword"},
                        "os": {"type": "keyword"},
                        "browser": {"type": "keyword"}
                    }
                }
            }
        },
        "settings": {
            "number_of_shards": 5,
            "number_of_replicas": 1,
            "refresh_interval": "30s",
            "index.lifecycle.name": "analytics_policy",
            "index.lifecycle.rollover_alias": "analytics_events"
        }
    },
    
    "search_logs": {
        "mappings": {
            "properties": {
                "timestamp": {"type": "date"},
                "level": {"type": "keyword"},
                "logger": {"type": "keyword"},
                "message": {
                    "type": "text",
                    "analyzer": "standard"
                },
                "user_id": {"type": "keyword"},
                "request_id": {"type": "keyword"},
                "module": {"type": "keyword"},
                "function": {"type": "keyword"},
                "line_number": {"type": "integer"},
                "exception": {
                    "type": "object",
                    "properties": {
                        "type": {"type": "keyword"},
                        "message": {"type": "text"},
                        "traceback": {"type": "text"}
                    }
                },
                "performance_metrics": {
                    "type": "object",
                    "properties": {
                        "execution_time": {"type": "float"},
                        "memory_usage": {"type": "long"},
                        "cpu_usage": {"type": "float"}
                    }
                }
            }
        },
        "settings": {
            "number_of_shards": 2,
            "number_of_replicas": 0,
            "refresh_interval": "10s"
        }
    }
}

# =============== ELASTICSEARCH CONNECTION POOL ===============

class ElasticsearchConnectionPool(IConnectionPool):
    """Elasticsearch connection pool with enterprise features"""
    
    def __init__(self, config: ElasticsearchPoolConfig, connection_info: DatabaseConnectionInfo):
        self.config = config
        self.connection_info = connection_info
        self.client: Optional[AsyncElasticsearch] = None
        self.state = ConnectionState.IDLE
        
        # Statistics
        self.stats = {
            "created_at": datetime.utcnow(),
            "total_operations": 0,
            "total_searches": 0,
            "total_indexing": 0,
            "failed_operations": 0,
            "avg_search_time": 0.0,
            "avg_index_time": 0.0,
            "cluster_health": "unknown",
            "index_count": 0,
            "document_count": 0,
            "last_health_check": None
        }
        
        # Health monitoring
        self._health_check_task: Optional[asyncio.Task] = None
        self._bulk_queue: asyncio.Queue = asyncio.Queue(maxsize=self.config.bulk_queue_size)
        self._bulk_processor_task: Optional[asyncio.Task] = None
    
    async def initialize(self) -> bool:
        """Initialize Elasticsearch connection"""



        try:
            # Build client configuration
            client_config = {
                'hosts': [f"{self.connection_info.host}:{self.connection_info.port}"],
                'timeout': self.config.connection_timeout,
                'max_retries': self.config.max_retries,
                'retry_on_timeout': self.config.retry_on_timeout,
            }
            
            # SSL configuration
            if self.config.use_ssl:
                client_config.update({
                    'use_ssl': True,
                    'verify_certs': self.config.verify_certs,
                })
                
                if self.config.ca_certs:
                    client_config['ca_certs'] = self.config.ca_certs
                if self.config.client_cert:
                    client_config['client_cert'] = self.config.client_cert
                if self.config.client_key:
                    client_config['client_key'] = self.config.client_key
            
            # Authentication
            if self.connection_info.username and self.connection_info.password:
                client_config['http_auth'] = (
                    self.connection_info.username,
                    self.connection_info.password
                )
            
            # Sniffing configuration
            if self.config.sniff_on_start:
                client_config.update({
                    'sniff_on_start': True,
                    'sniff_on_connection_fail': self.config.sniff_on_connection_fail,
                    'sniffer_timeout': self.config.sniffer_timeout
                })
            
            # Create client
            self.client = AsyncElasticsearch(**client_config)
            
            # Test connection and get cluster info
            cluster_info = await self.client.info()
            logger.info(f" Connected to Elasticsearch cluster: {cluster_info['cluster_name']}")
            
            # Initialize indices
            await self._initialize_indices()
            
            # Set up index lifecycle policies
            await self._setup_lifecycle_policies()
            
            self.state = ConnectionState.ACTIVE
            
            # Start health monitoring
            if self.config.enable_monitoring:
                self._health_check_task = asyncio.create_task(self._health_monitor())
            
            # Start bulk processor
            self._bulk_processor_task = asyncio.create_task(self._bulk_processor())
            
            logger.info(" Elasticsearch pool initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f" Elasticsearch pool initialization failed: {e}")
            self.state = ConnectionState.FAILED
            return False
    
    async def _initialize_indices(self) -> None:
        """Initialize all required indices"""
        for index_name, index_config in INDEX_MAPPINGS.items():
            try:
                full_index_name = f"{self.config.index_prefix}_{index_name}"
                
                # Check if index exists
                if not await self.client.indices.exists(index=full_index_name):
                    # Create index with mapping and settings
                    await self.client.indices.create(
                        index=full_index_name,
                        body=index_config
                    )
                    logger.info(f" Created index: {full_index_name}")
                else:
                    # Update mapping if needed
                    await self.client.indices.put_mapping(
                        index=full_index_name,
                        body=index_config["mappings"]
                    )
                    logger.info(f" Updated mapping for index: {full_index_name}")
                
            except Exception as e:
                logger.error(f"Failed to initialize index {index_name}: {e}")
    
    async def _setup_lifecycle_policies(self) -> None:
        """Setup index lifecycle management policies"""
        if not self.config.enable_analytics:
            return
        
        # Analytics data retention policy
        analytics_policy = {
            "policy": {
                "phases": {
                    "hot": {
                        "actions": {
                            "rollover": {
                                "max_size": "10GB",
                                "max_age": "7d"
                            }
                        }
                    },
                    "warm": {
                        "min_age": "7d",
                        "actions": {
                            "allocate": {
                                "number_of_replicas": 0
                            }
                        }
                    },
                    "cold": {
                        "min_age": "30d",
                        "actions": {
                            "allocate": {
                                "number_of_replicas": 0
                            }
                        }
                    },
                    "delete": {
                        "min_age": f"{self.config.analytics_retention_days}d"
                    }
                }
            }
        }
        
        try:
            await self.client.ilm.put_lifecycle(
                name="analytics_policy",
                body=analytics_policy
            )
            logger.info(" Analytics lifecycle policy created")
        except Exception as e:
            logger.error(f"Failed to create lifecycle policy: {e}")
    
    async def acquire(self, timeout: Optional[float] = None) -> AsyncElasticsearch:
        """Acquire Elasticsearch client"""
        if not self.client:
            raise Exception("Elasticsearch pool not initialized")
        
        self.stats["total_operations"] += 1
        return self.client
    
    async def release(self, connection: AsyncElasticsearch) -> None:
        """Release Elasticsearch client (no-op)"""
        pass
    
    async def search_content(self, query: Dict[str, Any], index_name: str = "content_fingerprints", 
                           size: int = 100) -> Dict[str, Any]:
        """Search content with optimized performance"""
        start_time = asyncio.get_event_loop().time()
        
        try:
            client = await self.acquire()
            full_index_name = f"{self.config.index_prefix}_{index_name}"
            
            # Add default parameters
            search_params = {
                "index": full_index_name,
                "body": query,
                "size": min(size, self.config.max_result_window),
                "timeout": self.config.default_search_timeout
            }
            
            result = await client.search(**search_params)
            
            # Update statistics
            search_time = asyncio.get_event_loop().time() - start_time
            self.stats["total_searches"] += 1
            self.stats["avg_search_time"] = (
                (self.stats["avg_search_time"] * (self.stats["total_searches"] - 1) + search_time) /
                self.stats["total_searches"]
            )
            
            return result
            
        except Exception as e:
            self.stats["failed_operations"] += 1
            logger.error(f"Search failed: {e}")
            raise
    
    async def index_document(self, document: Dict[str, Any], index_name: str, 
                           doc_id: Optional[str] = None, refresh: str = "false") -> Dict[str, Any]:
        """Index single document"""
        start_time = asyncio.get_event_loop().time()
        
        try:
            client = await self.acquire()
            full_index_name = f"{self.config.index_prefix}_{index_name}"
            
            index_params = {
                "index": full_index_name,
                "body": document,
                "refresh": refresh
            }
            
            if doc_id:
                index_params["id"] = doc_id
            
            result = await client.index(**index_params)
            
            # Update statistics
            index_time = asyncio.get_event_loop().time() - start_time
            self.stats["total_indexing"] += 1
            self.stats["avg_index_time"] = (
                (self.stats["avg_index_time"] * (self.stats["total_indexing"] - 1) + index_time) /
                self.stats["total_indexing"]
            )
            
            return result
            
        except Exception as e:
            self.stats["failed_operations"] += 1
            logger.error(f"Indexing failed: {e}")
            raise
    
    async def bulk_index_documents(self, documents: List[Dict[str, Any]], 
                                 index_name: str, refresh: str = "false") -> Dict[str, Any]:
        """Bulk index documents with optimized performance"""



        try:
            client = await self.acquire()
            full_index_name = f"{self.config.index_prefix}_{index_name}"
            
            # Prepare bulk actions
            actions = []
            for doc in documents:
                action = {
                    "_index": full_index_name,
                    "_source": doc
                }
                if "_id" in doc:
                    action["_id"] = doc.pop("_id")
                actions.append(action)
            
            # Execute bulk operation
            result = await async_bulk(
                client,
                actions,
                chunk_size=self.config.bulk_chunk_size,
                max_chunk_bytes=self.config.bulk_max_chunk_bytes,
                refresh=refresh
            )
            
            self.stats["total_indexing"] += len(documents)
            return {"success": True, "indexed": len(documents), "errors": result[1]}
            
        except Exception as e:
            self.stats["failed_operations"] += 1
            logger.error(f"Bulk indexing failed: {e}")
            raise
    
    async def queue_bulk_document(self, document: Dict[str, Any], index_name: str) -> None:
        """Queue document for bulk processing"""



        try:
            await self._bulk_queue.put({
                "document": document,
                "index_name": index_name,
                "timestamp": datetime.utcnow()
            }, timeout=1.0)
        except asyncio.TimeoutError:
            logger.warning("Bulk queue is full, dropping document")
    
    async def _bulk_processor(self) -> None:
        """Background bulk processor"""
        batch = []
        last_flush = datetime.utcnow()
        
        while self.state == ConnectionState.ACTIVE:
            try:
                # Wait for documents or timeout
                try:
                    item = await asyncio.wait_for(self._bulk_queue.get(), timeout=5.0)
                    batch.append(item)
                except asyncio.TimeoutError:
                    pass
                
                # Check if we should flush the batch
                should_flush = (
                    len(batch) >= self.config.bulk_chunk_size or
                    (batch and (datetime.utcnow() - last_flush).seconds >= 30)
                )
                
                if should_flush and batch:
                    # Group by index
                    index_groups = {}
                    for item in batch:
                        index_name = item["index_name"]
                        if index_name not in index_groups:
                            index_groups[index_name] = []
                        index_groups[index_name].append(item["document"])
                    
                    # Bulk index each group
                    for index_name, documents in index_groups.items():
                        try:
                            await self.bulk_index_documents(documents, index_name)
                        except Exception as e:
                            logger.error(f"Bulk processing failed for {index_name}: {e}")
                    
                    batch.clear()
                    last_flush = datetime.utcnow()
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Bulk processor error: {e}")
                await asyncio.sleep(1)
        
        # Flush remaining documents
        if batch:
            logger.info(f"Flushing {len(batch)} remaining documents")
            # Process remaining batch similar to above
    
    async def search_similar_content(self, vector_embedding: List[float], 
                                   content_type: str, threshold: float = 0.8) -> List[Dict]:
        """Search for similar content using vector similarity"""
        query = {
            "query": {
                "bool": {
                    "must": [
                        {"term": {"content_type": content_type}},
                        {
                            "script_score": {
                                "query": {"match_all": {}},
                                "script": {
                                    "source": "cosineSimilarity(params.query_vector, 'vector_embedding') + 1.0",
                                    "params": {"query_vector": vector_embedding}
                                },
                                "min_score": threshold
                            }
                        }
                    ]
                }
            },
            "sort": [
                {"_score": {"order": "desc"}}
            ]
        }
        
        result = await self.search_content(query, "content_fingerprints", size=100)
        return result.get("hits", {}).get("hits", [])
    
    async def aggregate_analytics(self, aggregation_query: Dict[str, Any], 
                                index_name: str = "analytics_events") -> Dict[str, Any]:
        """Execute analytics aggregation query"""



        try:
            client = await self.acquire()
            full_index_name = f"{self.config.index_prefix}_{index_name}"
            
            result = await client.search(
                index=full_index_name,
                body=aggregation_query,
                size=0  # Only return aggregation results
            )
            
            return result.get("aggregations", {})
            
        except Exception as e:
            logger.error(f"Aggregation failed: {e}")
            raise
    
    async def get_protection_alerts(self, user_id: str, status: Optional[str] = None, 
                                  limit: int = 100) -> List[Dict]:
        """Get protection alerts for user"""
        query = {
            "query": {
                "bool": {
                    "must": [
                        {"term": {"user_id": user_id}}
                    ]
                }
            },
            "sort": [
                {"created_at": {"order": "desc"}}
            ]
        }
        
        if status:
            query["query"]["bool"]["must"].append({"term": {"status": status}})
        
        result = await self.search_content(query, "protection_alerts", size=limit)
        return [hit["_source"] for hit in result.get("hits", {}).get("hits", [])]
    
    async def log_event(self, log_data: Dict[str, Any]) -> None:
        """Log event to Elasticsearch"""
        log_data["timestamp"] = datetime.utcnow().isoformat()
        await self.queue_bulk_document(log_data, "search_logs")
    
    async def health_check(self) -> bool:
        """Check Elasticsearch cluster health"""



        try:
            client = await self.acquire()
            
            # Cluster health
            health = await client.cluster.health()
            self.stats["cluster_health"] = health["status"]
            
            # Cluster stats
            stats = await client.cluster.stats()
            self.stats["index_count"] = stats["indices"]["count"]
            self.stats["document_count"] = stats["indices"]["docs"]["count"]
            
            self.stats["last_health_check"] = datetime.utcnow()
            
            return health["status"] in ["green", "yellow"]
            
        except Exception as e:
            logger.error(f"Elasticsearch health check failed: {e}")
            return False
    
    async def _health_monitor(self) -> None:
        """Background health monitoring"""
        while self.state == ConnectionState.ACTIVE:
            try:
                is_healthy = await self.health_check()
                if not is_healthy:
                    logger.warning("Elasticsearch cluster health check failed")
                
                await asyncio.sleep(self.config.health_check_interval)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Elasticsearch health monitor error: {e}")
                await asyncio.sleep(5)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get Elasticsearch pool statistics"""
        pool_stats = {
            "client_info": str(self.client) if self.client else None,
            "state": self.state.value,
            "bulk_queue_size": self._bulk_queue.qsize(),
            "config": {
                "index_prefix": self.config.index_prefix,
                "max_result_window": self.config.max_result_window,
                "bulk_chunk_size": self.config.bulk_chunk_size
            }
        }
        pool_stats.update(self.stats)
        return pool_stats
    
    async def close(self) -> None:
        """Close Elasticsearch pool"""



        try:
            self.state = ConnectionState.CLOSED
            
            # Cancel bulk processor
            if self._bulk_processor_task:
                self._bulk_processor_task.cancel()
                try:
                    await self._bulk_processor_task
                except asyncio.CancelledError:
                    pass
            
            # Cancel health monitoring
            if self._health_check_task:
                self._health_check_task.cancel()
                try:
                    await self._health_check_task
                except asyncio.CancelledError:
                    pass
            
            # Close client
            if self.client:
                await self.client.close()
            
            logger.info(" Elasticsearch pool closed")
            
        except Exception as e:
            logger.error(f"Error closing Elasticsearch pool: {e}")

# =============== EXPORTS ===============

__all__ = [
    "ElasticsearchConnectionPool",
    "ElasticsearchPoolConfig",
    "INDEX_MAPPINGS"
]
