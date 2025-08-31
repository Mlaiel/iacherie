"""Elasticsearch Connection Handler - IA Influencer Agent Platform

Manages Elasticsearch connections for search, indexing, and analytics:
- Content search and discovery indexing
- Log aggregation and monitoring
- Real-time analytics and reporting
- Creator and content recommendation indexing
- Platform integration event logging
- Revenue and performance analytics

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.
"""
import asyncio
import logging
from typing import Dict, Any, Optional, List, Union
from dataclasses import dataclass
from datetime import datetime, timedelta

from elasticsearch import AsyncElasticsearch
from elasticsearch.exceptions import ConnectionError, NotFoundError, RequestError


@dataclass
class ElasticsearchConfig:
    """Elasticsearch connection configuration"""    hosts: List[str]
    username: Optional[str] = None
    password: Optional[str] = None
    api_key: Optional[str] = None
    cloud_id: Optional[str] = None
    use_ssl: bool = True
    verify_certs: bool = True
    ca_certs: Optional[str] = None
    client_cert: Optional[str] = None
    client_key: Optional[str] = None
    timeout: int = 30
    max_retries: int = 3
    retry_on_timeout: bool = True
    sniff_on_start: bool = False
    sniff_on_connection_fail: bool = False
    sniffer_timeout: int = 0.1
    # Index settings
    default_index_prefix: str = "ia_influencer"
    tenant_index_prefix: str = "tenant"
    number_of_shards: int = 1
    number_of_replicas: int = 0


class ElasticsearchConnectionHandler:
    """    Elasticsearch connection handler for IA Influencer platform.
    
    Manages Elasticsearch for:
    - Content search and discovery
    - Application logs and monitoring
    - Real-time analytics and metrics
    - User behavior tracking
    - Performance monitoring
    - Revenue analytics and reporting
    """    
    def __init__(self, config: Dict[str, Any]):
        self.config = ElasticsearchConfig(**config)
        self.logger = logging.getLogger(__name__)
        
        self.client: Optional[AsyncElasticsearch] = None
        
        # Connection metrics
        self.connection_count = 0
        self.operation_count = 0
        self.error_count = 0
        self.last_health_check = None
        
        # Index mappings
        self.index_mappings = self._get_index_mappings()
    
    async def initialize(self) -> None:
        """Initialize Elasticsearch connection"""        try:
            self.logger.info("Initializing Elasticsearch connection...")
            
            # Create client
            client_config = self._build_client_config()
            self.client = AsyncElasticsearch(**client_config)
            
            # Test connection
            await self._test_connection()
            
            # Create default indexes
            await self._create_default_indexes()
            
            # Verify connection
            await self.health_check()
            
            self.logger.info("Elasticsearch connection initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize Elasticsearch connection: {e}")
            raise
    
    def _build_client_config(self) -> Dict[str, Any]:
        """Build Elasticsearch client configuration"""        config = {
            "hosts": self.config.hosts,
            "timeout": self.config.timeout,
            "max_retries": self.config.max_retries,
            "retry_on_timeout": self.config.retry_on_timeout,
            "sniff_on_start": self.config.sniff_on_start,
            "sniff_on_connection_fail": self.config.sniff_on_connection_fail,
            "sniffer_timeout": self.config.sniffer_timeout
        }
        
        # Authentication
        if self.config.cloud_id:
            config["cloud_id"] = self.config.cloud_id
        
        if self.config.api_key:
            config["api_key"] = self.config.api_key
        elif self.config.username and self.config.password:
            config["basic_auth"] = (self.config.username, self.config.password)
        
        # SSL settings
        if self.config.use_ssl:
            config["use_ssl"] = True
            config["verify_certs"] = self.config.verify_certs
            
            if self.config.ca_certs:
                config["ca_certs"] = self.config.ca_certs
            
            if self.config.client_cert and self.config.client_key:
                config["client_cert"] = self.config.client_cert
                config["client_key"] = self.config.client_key
        
        return config
    
    async def _test_connection(self) -> None:
        """Test Elasticsearch connection"""        if not self.client:
            raise RuntimeError("Elasticsearch client not initialized")
        
        try:
            info = await self.client.info()
            self.logger.info(f"Connected to Elasticsearch {info['version']['number']}")
        except Exception as e:
            self.logger.error(f"Elasticsearch connection test failed: {e}")
            raise
    
    def _get_index_mappings(self) -> Dict[str, Dict[str, Any]]:
        """Get index mappings for different content types"""        return {
            "content_fingerprints": {
                "mappings": {
                    "properties": {
                        "user_id": {"type": "keyword"},
                        "content_id": {"type": "keyword"},
                        "content_type": {"type": "keyword"},
                        "title": {"type": "text", "analyzer": "standard"},
                        "description": {"type": "text", "analyzer": "standard"},
                        "tags": {"type": "keyword"},
                        "platform": {"type": "keyword"},
                        "fingerprint_hash": {"type": "keyword"},
                        "similarity_vector": {"type": "dense_vector", "dims": 512},
                        "metadata": {"type": "object"},
                        "created_at": {"type": "date"},
                        "updated_at": {"type": "date"}
                    }
                },
                "settings": {
                    "number_of_shards": self.config.number_of_shards,
                    "number_of_replicas": self.config.number_of_replicas,
                    "analysis": {
                        "analyzer": {
                            "content_analyzer": {
                                "tokenizer": "standard",
                                "filter": ["lowercase", "stop", "snowball"]
                            }
                        }
                    }
                }
            },
            "user_analytics": {
                "mappings": {
                    "properties": {
                        "user_id": {"type": "keyword"},
                        "session_id": {"type": "keyword"},
                        "event_type": {"type": "keyword"},
                        "event_data": {"type": "object"},
                        "platform": {"type": "keyword"},
                        "ip_address": {"type": "ip"},
                        "user_agent": {"type": "text"},
                        "timestamp": {"type": "date"}
                    }
                },
                "settings": {
                    "number_of_shards": self.config.number_of_shards,
                    "number_of_replicas": self.config.number_of_replicas
                }
            },
            "application_logs": {
                "mappings": {
                    "properties": {
                        "level": {"type": "keyword"},
                        "logger": {"type": "keyword"},
                        "message": {"type": "text"},
                        "module": {"type": "keyword"},
                        "function": {"type": "keyword"},
                        "user_id": {"type": "keyword"},
                        "request_id": {"type": "keyword"},
                        "exception": {"type": "text"},
                        "extra_data": {"type": "object"},
                        "timestamp": {"type": "date"}
                    }
                },
                "settings": {
                    "number_of_shards": self.config.number_of_shards,
                    "number_of_replicas": self.config.number_of_replicas
                }
            },
            "revenue_analytics": {
                "mappings": {
                    "properties": {
                        "user_id": {"type": "keyword"},
                        "content_id": {"type": "keyword"},
                        "platform": {"type": "keyword"},
                        "revenue_type": {"type": "keyword"},
                        "amount": {"type": "double"},
                        "currency": {"type": "keyword"},
                        "period_start": {"type": "date"},
                        "period_end": {"type": "date"},
                        "metrics": {"type": "object"},
                        "created_at": {"type": "date"}
                    }
                },
                "settings": {
                    "number_of_shards": self.config.number_of_shards,
                    "number_of_replicas": self.config.number_of_replicas
                }
            },
            "collaboration_recommendations": {
                "mappings": {
                    "properties": {
                        "creator_id": {"type": "keyword"},
                        "potential_collaborator_id": {"type": "keyword"},
                        "match_score": {"type": "double"},
                        "match_factors": {"type": "object"},
                        "content_similarity": {"type": "double"},
                        "audience_overlap": {"type": "double"},
                        "engagement_compatibility": {"type": "double"},
                        "generated_at": {"type": "date"}
                    }
                },
                "settings": {
                    "number_of_shards": self.config.number_of_shards,
                    "number_of_replicas": self.config.number_of_replicas
                }
            }
        }
    
    async def _create_default_indexes(self) -> None:
        """Create default indexes with mappings"""        for index_suffix, mapping in self.index_mappings.items():
            index_name = f"{self.config.default_index_prefix}_{index_suffix}"
            
            try:
                if not await self.client.indices.exists(index=index_name):
                    await self.client.indices.create(
                        index=index_name,
                        body=mapping
                    )
                    self.logger.info(f"Created index: {index_name}")
                else:
                    self.logger.info(f"Index already exists: {index_name}")
                    
            except Exception as e:
                self.logger.error(f"Failed to create index {index_name}: {e}")
                # Don't raise here, continue with other indexes
    
    async def get_connection(self) -> AsyncElasticsearch:
        """Get Elasticsearch connection"""        if not self.client:
            raise RuntimeError("Elasticsearch client not initialized")
        
        self.connection_count += 1
        return self.client
    
    def _get_tenant_index_name(self, base_index: str, tenant_id: str) -> str:
        """Get tenant-specific index name"""        return f"{self.config.tenant_index_prefix}_{tenant_id}_{base_index}"
    
    async def get_tenant_index(self, index_suffix: str, tenant_id: str) -> str:
        """Get or create tenant-specific index"""        index_name = self._get_tenant_index_name(index_suffix, tenant_id)
        
        # Create index if it doesn't exist
        if not await self.client.indices.exists(index=index_name):
            if index_suffix in self.index_mappings:
                mapping = self.index_mappings[index_suffix]
                await self.client.indices.create(
                    index=index_name,
                    body=mapping
                )
                self.logger.info(f"Created tenant index: {index_name}")
        
        return index_name
    
    # Document operations
    async def index_document(self, 
                           index: str, 
                           document: Dict[str, Any],
                           doc_id: Optional[str] = None,
                           tenant_id: Optional[str] = None) -> str:
        """Index a document"""        try:
            client = await self.get_connection()
            
            if tenant_id:
                index = await self.get_tenant_index(index, tenant_id)
            else:
                index = f"{self.config.default_index_prefix}_{index}"
            
            # Add timestamp if not present
            if 'created_at' not in document:
                document['created_at'] = datetime.utcnow().isoformat()
            
            result = await client.index(
                index=index,
                id=doc_id,
                body=document
            )
            
            self.operation_count += 1
            return result['_id']
            
        except Exception as e:
            self.error_count += 1
            self.logger.error(f"Elasticsearch index failed: {e}")
            raise
    
    async def get_document(self, 
                          index: str, 
                          doc_id: str,
                          tenant_id: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Get document by ID"""        try:
            client = await self.get_connection()
            
            if tenant_id:
                index = await self.get_tenant_index(index, tenant_id)
            else:
                index = f"{self.config.default_index_prefix}_{index}"
            
            result = await client.get(
                index=index,
                id=doc_id
            )
            
            self.operation_count += 1
            return result['_source']
            
        except NotFoundError:
            return None
        except Exception as e:
            self.error_count += 1
            self.logger.error(f"Elasticsearch get failed: {e}")
            raise
    
    async def update_document(self, 
                            index: str, 
                            doc_id: str,
                            update_data: Dict[str, Any],
                            tenant_id: Optional[str] = None) -> bool:
        """Update document"""        try:
            client = await self.get_connection()
            
            if tenant_id:
                index = await self.get_tenant_index(index, tenant_id)
            else:
                index = f"{self.config.default_index_prefix}_{index}"
            
            # Add updated timestamp
            update_data['updated_at'] = datetime.utcnow().isoformat()
            
            await client.update(
                index=index,
                id=doc_id,
                body={"doc": update_data}
            )
            
            self.operation_count += 1
            return True
            
        except Exception as e:
            self.error_count += 1
            self.logger.error(f"Elasticsearch update failed: {e}")
            raise
    
    async def delete_document(self, 
                            index: str, 
                            doc_id: str,
                            tenant_id: Optional[str] = None) -> bool:
        """Delete document"""        try:
            client = await self.get_connection()
            
            if tenant_id:
                index = await self.get_tenant_index(index, tenant_id)
            else:
                index = f"{self.config.default_index_prefix}_{index}"
            
            await client.delete(
                index=index,
                id=doc_id
            )
            
            self.operation_count += 1
            return True
            
        except NotFoundError:
            return False
        except Exception as e:
            self.error_count += 1
            self.logger.error(f"Elasticsearch delete failed: {e}")
            raise
    
    async def search(self, 
                    index: str, 
                    query: Dict[str, Any],
                    size: int = 10,
                    from_: int = 0,
                    sort: Optional[List[Dict]] = None,
                    tenant_id: Optional[str] = None) -> Dict[str, Any]:
        """Search documents"""        try:
            client = await self.get_connection()
            
            if tenant_id:
                index = await self.get_tenant_index(index, tenant_id)
            else:
                index = f"{self.config.default_index_prefix}_{index}"
            
            search_body = {
                "query": query,
                "size": size,
                "from": from_
            }
            
            if sort:
                search_body["sort"] = sort
            
            result = await client.search(
                index=index,
                body=search_body
            )
            
            self.operation_count += 1
            return result
            
        except Exception as e:
            self.error_count += 1
            self.logger.error(f"Elasticsearch search failed: {e}")
            raise
    
    async def bulk_index(self, 
                        operations: List[Dict[str, Any]],
                        tenant_id: Optional[str] = None) -> Dict[str, Any]:
        """Bulk index operations"""        try:
            client = await self.get_connection()
            
            # Process operations for tenant isolation
            if tenant_id:
                for op in operations:
                    if 'index' in op and '_index' in op['index']:
                        base_index = op['index']['_index'].replace(f"{self.config.default_index_prefix}_", "")
                        op['index']['_index'] = await self.get_tenant_index(base_index, tenant_id)
            
            result = await client.bulk(body=operations)
            self.operation_count += 1
            
            return result
            
        except Exception as e:
            self.error_count += 1
            self.logger.error(f"Elasticsearch bulk index failed: {e}")
            raise
    
    async def aggregate(self, 
                       index: str, 
                       aggregations: Dict[str, Any],
                       query: Optional[Dict[str, Any]] = None,
                       tenant_id: Optional[str] = None) -> Dict[str, Any]:
        """Execute aggregation query"""        try:
            client = await self.get_connection()
            
            if tenant_id:
                index = await self.get_tenant_index(index, tenant_id)
            else:
                index = f"{self.config.default_index_prefix}_{index}"
            
            search_body = {
                "aggs": aggregations,
                "size": 0
            }
            
            if query:
                search_body["query"] = query
            
            result = await client.search(
                index=index,
                body=search_body
            )
            
            self.operation_count += 1
            return result
            
        except Exception as e:
            self.error_count += 1
            self.logger.error(f"Elasticsearch aggregation failed: {e}")
            raise
    
    async def health_check(self) -> Dict[str, Any]:
        """Check Elasticsearch connection health"""        try:
            start_time = datetime.utcnow()
            
            client = await self.get_connection()
            
            # Test basic connectivity
            health = await client.cluster.health()
            
            # Get cluster stats
            stats = await client.cluster.stats()
            
            # Get node info
            nodes = await client.nodes.info()
            
            response_time = (datetime.utcnow() - start_time).total_seconds()
            self.last_health_check = datetime.utcnow()
            
            return {
                "status": "healthy" if health["status"] in ["green", "yellow"] else "unhealthy",
                "response_time": response_time,
                "cluster": {
                    "name": health["cluster_name"],
                    "status": health["status"],
                    "number_of_nodes": health["number_of_nodes"],
                    "number_of_data_nodes": health["number_of_data_nodes"],
                    "active_primary_shards": health["active_primary_shards"],
                    "active_shards": health["active_shards"],
                    "relocating_shards": health["relocating_shards"],
                    "initializing_shards": health["initializing_shards"],
                    "unassigned_shards": health["unassigned_shards"]
                },
                "indices": {
                    "count": stats["indices"]["count"],
                    "docs_count": stats["indices"]["docs"]["count"],
                    "store_size": stats["indices"]["store"]["size_in_bytes"]
                },
                "nodes": len(nodes["nodes"]),
                "metrics": {
                    "connection_count": self.connection_count,
                    "operation_count": self.operation_count,
                    "error_count": self.error_count
                },
                "last_check": self.last_health_check.isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Elasticsearch health check failed: {e}")
            return {
                "status": "unhealthy",
                "error": str(e),
                "last_check": datetime.utcnow().isoformat()
            }
    
    async def get_metrics(self) -> Dict[str, Any]:
        """Get detailed Elasticsearch metrics"""        try:
            client = await self.get_connection()
            
            # Cluster stats
            cluster_stats = await client.cluster.stats()
            
            # Node stats
            node_stats = await client.nodes.stats()
            
            # Index stats
            index_stats = await client.indices.stats()
            
            return {
                "cluster": cluster_stats,
                "nodes": node_stats,
                "indices": index_stats,
                "client_metrics": {
                    "connection_count": self.connection_count,
                    "operation_count": self.operation_count,
                    "error_count": self.error_count
                }
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get Elasticsearch metrics: {e}")
            return {"error": str(e)}
    
    async def shutdown(self) -> None:
        """Shutdown Elasticsearch connections"""        self.logger.info("Shutting down Elasticsearch connections...")
        
        if self.client:
            await self.client.close()
            self.logger.info("Closed Elasticsearch client")
        
        self.client = None
        
        self.logger.info("Elasticsearch connections shutdown completed")
