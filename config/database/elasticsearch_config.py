"""Elasticsearch Configuration Module for IA-Influencer Agent Platform
===================================================================

Professional Elasticsearch configuration for search, analytics, content indexing,
and real-time monitoring in multi-tenant content protection platform.

Author: Fahed Mlaiel <mlaiel@live.de>
Project: IA-Influencer Agent + Content Protection Platform
Team: Lead Dev IA + Backend Senior + ML Engineer + DBA + Security + Microservices + Audio + DevOps

Copyright Notice:
This code is the intellectual property of Fahed Mlaiel. 
Any unauthorized use, reproduction, or distribution of this code 
without explicit written permission from the author is strictly prohibited.

Contact: mlaiel@live.de for licensing inquiries.
"""
import os
import json
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field
from enum import Enum
from elasticsearch import Elasticsearch, AsyncElasticsearch
from elasticsearch.connection import create_ssl_context
from elasticsearch.exceptions import ConnectionError, RequestError, NotFoundError
import ssl
import logging
from urllib.parse import urlparse

logger = logging.getLogger(__name__)


class ElasticsearchEnvironment(Enum):
    """Elasticsearch environment configurations"""
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"
    TESTING = "testing"


class ElasticsearchClusterType(Enum):
    """Elasticsearch cluster deployment types"""
    SINGLE_NODE = "single_node"
    CLUSTER = "cluster"
    CLOUD = "cloud"


class ElasticsearchWorkloadType(Enum):
    """Elasticsearch workload optimization types"""
    SEARCH = "search"
    ANALYTICS = "analytics"
    LOGGING = "logging"
    MONITORING = "monitoring"
    CONTENT_INDEXING = "content_indexing"


@dataclass
class ElasticsearchCredentials:
    """Elasticsearch authentication credentials"""
    hosts: List[str] = field(default_factory=lambda: ["localhost:9200"])
    username: Optional[str] = None
    password: Optional[str] = None
    api_key: Optional[str] = None
    cloud_id: Optional[str] = None
    use_ssl: bool = False
    verify_certs: bool = True
    ca_certs: Optional[str] = None
    client_cert: Optional[str] = None
    client_key: Optional[str] = None


@dataclass
class ElasticsearchConnectionConfig:
    """Elasticsearch connection configuration"""
    timeout: int = 30
    max_retries: int = 3
    retry_on_timeout: bool = True
    retry_on_status: List[int] = field(default_factory=lambda: [502, 503, 504])
    max_connections: int = 25
    maxsize: int = 25
    block: bool = False
    headers: Dict[str, str] = field(default_factory=dict)


@dataclass
class ElasticsearchIndexConfig:
    """Elasticsearch index configuration templates"""
    content_protection: Dict[str, Any] = field(default_factory=lambda: {
        "settings": {
            "number_of_shards": 3,
            "number_of_replicas": 1,
            "refresh_interval": "5s",
            "analysis": {
                "analyzer": {
                    "content_analyzer": {
                        "type": "custom",
                        "tokenizer": "standard",
                        "filter": ["lowercase", "stop", "snowball"]
                    }
                }
            }
        },
        "mappings": {
            "properties": {
                "content_id": {"type": "keyword"},
                "creator_id": {"type": "keyword"},
                "content_type": {"type": "keyword"},
                "title": {"type": "text", "analyzer": "content_analyzer"},
                "description": {"type": "text", "analyzer": "content_analyzer"},
                "fingerprint": {"type": "binary"},
                "similarity_score": {"type": "float"},
                "platform": {"type": "keyword"},
                "detected_at": {"type": "date"},
                "status": {"type": "keyword"},
                "metadata": {"type": "object", "dynamic": True}
            }
        }
    })
    
    analytics_events: Dict[str, Any] = field(default_factory=lambda: {
        "settings": {
            "number_of_shards": 5,
            "number_of_replicas": 1,
            "refresh_interval": "1s",
            "index.mapping.total_fields.limit": 2000
        },
        "mappings": {
            "properties": {
                "event_id": {"type": "keyword"},
                "event_type": {"type": "keyword"},
                "user_id": {"type": "keyword"},
                "session_id": {"type": "keyword"},
                "timestamp": {"type": "date"},
                "platform": {"type": "keyword"},
                "event_data": {"type": "object", "dynamic": True},
                "user_agent": {"type": "text"},
                "ip_address": {"type": "ip"},
                "location": {"type": "geo_point"}
            }
        }
    })
    
    content_search: Dict[str, Any] = field(default_factory=lambda: {
        "settings": {
            "number_of_shards": 2,
            "number_of_replicas": 1,
            "refresh_interval": "30s",
            "analysis": {
                "analyzer": {
                    "search_analyzer": {
                        "type": "custom",
                        "tokenizer": "standard",
                        "filter": ["lowercase", "stop", "snowball", "synonym"]
                    }
                },
                "filter": {
                    "synonym": {
                        "type": "synonym",
                        "synonyms": ["music,song,track", "video,clip,movie"]
                    }
                }
            }
        },
        "mappings": {
            "properties": {
                "content_id": {"type": "keyword"},
                "title": {"type": "text", "analyzer": "search_analyzer"},
                "description": {"type": "text", "analyzer": "search_analyzer"},
                "tags": {"type": "keyword"},
                "category": {"type": "keyword"},
                "creator": {"type": "text"},
                "upload_date": {"type": "date"},
                "duration": {"type": "integer"},
                "file_size": {"type": "long"},
                "format": {"type": "keyword"},
                "quality": {"type": "keyword"},
                "language": {"type": "keyword"}
            }
        }
    })


@dataclass
class ElasticsearchPerformanceConfig:
    """Elasticsearch performance optimization settings"""
    bulk_size: int = 1000
    bulk_timeout: str = "60s"
    scroll_size: int = 5000
    scroll_timeout: str = "10m"
    search_timeout: str = "30s"
    refresh_policy: str = "wait_for"
    request_timeout: int = 60
    sniff_on_start: bool = True
    sniff_on_connection_fail: bool = True
    sniff_timeout: int = 10
    max_concurrent_searches: int = 5


class ElasticsearchConfig:
    """
    Professional Elasticsearch configuration manager for IA-Influencer Agent Platform
    
    Handles search indexing, analytics, content discovery, and monitoring
    across multi-tenant content protection platform.
    """
    def __init__(self, 
                 environment: ElasticsearchEnvironment = ElasticsearchEnvironment.DEVELOPMENT,
                 workload_type: ElasticsearchWorkloadType = ElasticsearchWorkloadType.SEARCH,
                 cluster_type: ElasticsearchClusterType = ElasticsearchClusterType.SINGLE_NODE):
        self.environment = environment
        self.workload_type = workload_type
        self.cluster_type = cluster_type
        self.credentials = self._load_credentials()
        self.connection_config = self._get_connection_config()
        self.index_config = ElasticsearchIndexConfig()
        self.performance_config = self._get_performance_config()
        self._clients: Dict[str, Elasticsearch] = {}
        self._async_clients: Dict[str, AsyncElasticsearch] = {}
        self._setup_logging()

    def _setup_logging(self) -> None:
        """Setup Elasticsearch-specific logging"""
        self.logger = logging.getLogger(f"elasticsearch.{self.environment.value}.{self.workload_type.value}")
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
            self.logger.setLevel(logging.INFO)

    def _load_credentials(self) -> ElasticsearchCredentials:
        """Load Elasticsearch credentials from environment"""
        env_prefix = f"ELASTICSEARCH_{self.environment.value.upper()}"
        
        # Parse hosts
        hosts_str = os.getenv(f"{env_prefix}_HOSTS", "localhost:9200")
        hosts = [host.strip() for host in hosts_str.split(",")]
        
        return ElasticsearchCredentials(
            hosts=hosts,
            username=os.getenv(f"{env_prefix}_USERNAME"),
            password=os.getenv(f"{env_prefix}_PASSWORD"),
            api_key=os.getenv(f"{env_prefix}_API_KEY"),
            cloud_id=os.getenv(f"{env_prefix}_CLOUD_ID"),
            use_ssl=os.getenv(f"{env_prefix}_USE_SSL", "false").lower() == "true",
            verify_certs=os.getenv(f"{env_prefix}_VERIFY_CERTS", "true").lower() == "true",
            ca_certs=os.getenv(f"{env_prefix}_CA_CERTS"),
            client_cert=os.getenv(f"{env_prefix}_CLIENT_CERT"),
            client_key=os.getenv(f"{env_prefix}_CLIENT_KEY")
        )

    def _get_connection_config(self) -> ElasticsearchConnectionConfig:
        """Get connection configuration based on environment and workload"""
        base_configs = {
            ElasticsearchEnvironment.DEVELOPMENT: ElasticsearchConnectionConfig(
                timeout=15, max_connections=10
            ),
            ElasticsearchEnvironment.STAGING: ElasticsearchConnectionConfig(
                timeout=30, max_connections=20
            ),
            ElasticsearchEnvironment.PRODUCTION: ElasticsearchConnectionConfig(
                timeout=60, max_connections=50, max_retries=5
            ),
            ElasticsearchEnvironment.TESTING: ElasticsearchConnectionConfig(
                timeout=10, max_connections=5
            )
        }
        
        config = base_configs.get(self.environment, ElasticsearchConnectionConfig())
        
        # Adjust based on workload
        if self.workload_type == ElasticsearchWorkloadType.ANALYTICS:
            config.timeout = config.timeout * 2
            config.max_connections = config.max_connections * 2
        elif self.workload_type == ElasticsearchWorkloadType.LOGGING:
            config.max_connections = config.max_connections * 3
        
        return config

    def _get_performance_config(self) -> ElasticsearchPerformanceConfig:
        """Get performance configuration based on workload type"""
        workload_configs = {
            ElasticsearchWorkloadType.SEARCH: ElasticsearchPerformanceConfig(
                bulk_size=500,
                search_timeout="10s",
                refresh_policy="false"
            ),
            ElasticsearchWorkloadType.ANALYTICS: ElasticsearchPerformanceConfig(
                bulk_size=2000,
                scroll_size=10000,
                search_timeout="60s",
                max_concurrent_searches=10
            ),
            ElasticsearchWorkloadType.LOGGING: ElasticsearchPerformanceConfig(
                bulk_size=5000,
                refresh_policy="false",
                request_timeout=120
            ),
            ElasticsearchWorkloadType.MONITORING: ElasticsearchPerformanceConfig(
                bulk_size=1000,
                refresh_policy="wait_for",
                search_timeout="5s"
            ),
            ElasticsearchWorkloadType.CONTENT_INDEXING: ElasticsearchPerformanceConfig(
                bulk_size=1500,
                refresh_policy="false",
                request_timeout=90
            )
        }
        
        return workload_configs.get(self.workload_type, ElasticsearchPerformanceConfig())

    def _create_ssl_context(self) -> Optional[ssl.SSLContext]:
        """Create SSL context if SSL is enabled"""
        if not self.credentials.use_ssl:
            return None
        
        try:
            context = create_ssl_context()
            
            if not self.credentials.verify_certs:
                context.check_hostname = False
                context.verify_mode = ssl.CERT_NONE
            
            if self.credentials.ca_certs:
                context.load_verify_locations(self.credentials.ca_certs)
            
            if self.credentials.client_cert and self.credentials.client_key:
                context.load_cert_chain(self.credentials.client_cert, self.credentials.client_key)
            
            return context
            
        except Exception as e:
            self.logger.error(f"Failed to create SSL context: {str(e)}")
            raise

    def create_client(self, client_name: str = "default") -> Elasticsearch:
        """
        Create Elasticsearch client
        
        Args:
            client_name: Unique client identifier
            
        Returns:
            Configured Elasticsearch client
        """
        if client_name in self._clients:
            return self._clients[client_name]
        
        try:
            client_kwargs = {
                "hosts": self.credentials.hosts,
                "timeout": self.connection_config.timeout,
                "max_retries": self.connection_config.max_retries,
                "retry_on_timeout": self.connection_config.retry_on_timeout,
                "retry_on_status": self.connection_config.retry_on_status,
                "maxsize": self.connection_config.maxsize,
                "block": self.connection_config.block,
                "headers": self.connection_config.headers,
                "sniff_on_start": self.performance_config.sniff_on_start,
                "sniff_on_connection_fail": self.performance_config.sniff_on_connection_fail,
                "sniff_timeout": self.performance_config.sniff_timeout,
                "request_timeout": self.performance_config.request_timeout
            }
            
            # Add authentication
            if self.credentials.cloud_id:
                client_kwargs["cloud_id"] = self.credentials.cloud_id
            
            if self.credentials.api_key:
                client_kwargs["api_key"] = self.credentials.api_key
            elif self.credentials.username and self.credentials.password:
                client_kwargs["basic_auth"] = (self.credentials.username, self.credentials.password)
            
            # Add SSL configuration
            if self.credentials.use_ssl:
                client_kwargs["use_ssl"] = True
                client_kwargs["verify_certs"] = self.credentials.verify_certs
                client_kwargs["ssl_context"] = self._create_ssl_context()
            
            client = Elasticsearch(**client_kwargs)
            
            # Test connection
            if not client.ping():
                raise ConnectionError("Failed to connect to Elasticsearch cluster")
            
            self._clients[client_name] = client
            self.logger.info(f"Elasticsearch client created: {client_name}")
            
            return client
            
        except Exception as e:
            self.logger.error(f"Failed to create Elasticsearch client: {str(e)}")
            raise

    def create_async_client(self, client_name: str = "async_default") -> AsyncElasticsearch:
        """
        Create async Elasticsearch client
        
        Args:
            client_name: Unique client identifier
            
        Returns:
            Configured async Elasticsearch client
        """
        if client_name in self._async_clients:
            return self._async_clients[client_name]
        
        try:
            client_kwargs = {
                "hosts": self.credentials.hosts,
                "timeout": self.connection_config.timeout,
                "max_retries": self.connection_config.max_retries,
                "retry_on_timeout": self.connection_config.retry_on_timeout,
                "retry_on_status": self.connection_config.retry_on_status,
                "maxsize": self.connection_config.maxsize,
                "headers": self.connection_config.headers,
                "sniff_on_start": self.performance_config.sniff_on_start,
                "sniff_on_connection_fail": self.performance_config.sniff_on_connection_fail,
                "request_timeout": self.performance_config.request_timeout
            }
            
            # Add authentication
            if self.credentials.cloud_id:
                client_kwargs["cloud_id"] = self.credentials.cloud_id
            
            if self.credentials.api_key:
                client_kwargs["api_key"] = self.credentials.api_key
            elif self.credentials.username and self.credentials.password:
                client_kwargs["basic_auth"] = (self.credentials.username, self.credentials.password)
            
            # Add SSL configuration
            if self.credentials.use_ssl:
                client_kwargs["use_ssl"] = True
                client_kwargs["verify_certs"] = self.credentials.verify_certs
                client_kwargs["ssl_context"] = self._create_ssl_context()
            
            client = AsyncElasticsearch(**client_kwargs)
            self._async_clients[client_name] = client
            
            self.logger.info(f"Elasticsearch async client created: {client_name}")
            return client
            
        except Exception as e:
            self.logger.error(f"Failed to create async Elasticsearch client: {str(e)}")
            raise

    def get_content_protection_client(self) -> Elasticsearch:
        """Get Elasticsearch client for content protection operations"""
        return self.create_client("content_protection")

    def get_analytics_client(self) -> Elasticsearch:
        """Get Elasticsearch client optimized for analytics"""
        analytics_config = ElasticsearchConfig(
            self.environment, 
            ElasticsearchWorkloadType.ANALYTICS, 
            self.cluster_type
        )
        return analytics_config.create_client("analytics")

    def get_search_client(self) -> Elasticsearch:
        """Get Elasticsearch client for search operations"""
        return self.create_client("search")

    def get_monitoring_client(self) -> Elasticsearch:
        """Get Elasticsearch client for monitoring and logging"""
        monitoring_config = ElasticsearchConfig(
            self.environment, 
            ElasticsearchWorkloadType.MONITORING, 
            self.cluster_type
        )
        return monitoring_config.create_client("monitoring")

    def create_index(self, client: Elasticsearch, index_name: str, index_type: str) -> bool:
        """
        Create index with predefined configuration
        
        Args:
            client: Elasticsearch client
            index_name: Name of the index to create
            index_type: Type of index (content_protection, analytics_events, content_search)
            
        Returns:
            True if index created successfully
        """
        try:
            # Get index configuration
            index_configs = {
                "content_protection": self.index_config.content_protection,
                "analytics_events": self.index_config.analytics_events,
                "content_search": self.index_config.content_search
            }
            
            if index_type not in index_configs:
                raise ValueError(f"Unknown index type: {index_type}")
            
            config = index_configs[index_type].copy()
            
            # Adjust settings based on environment
            if self.environment == ElasticsearchEnvironment.PRODUCTION:
                config["settings"]["number_of_replicas"] = 2
                config["settings"]["refresh_interval"] = "30s"
            elif self.environment == ElasticsearchEnvironment.DEVELOPMENT:
                config["settings"]["number_of_shards"] = 1
                config["settings"]["number_of_replicas"] = 0
            
            # Create index
            if not client.indices.exists(index=index_name):
                client.indices.create(index=index_name, body=config)
                self.logger.info(f"Created Elasticsearch index: {index_name} ({index_type})")
            else:
                self.logger.info(f"Index already exists: {index_name}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to create index {index_name}: {str(e)}")
            raise

    def create_index_template(self, client: Elasticsearch, template_name: str, 
                            pattern: str, index_type: str) -> bool:
        """
        Create index template for automatic index creation
        
        Args:
            client: Elasticsearch client
            template_name: Name of the template
            pattern: Index pattern (e.g., "content-*")
            index_type: Type of index configuration to use
            
        Returns:
            True if template created successfully
        """
        try:
            index_configs = {
                "content_protection": self.index_config.content_protection,
                "analytics_events": self.index_config.analytics_events,
                "content_search": self.index_config.content_search
            }
            
            if index_type not in index_configs:
                raise ValueError(f"Unknown index type: {index_type}")
            
            config = index_configs[index_type].copy()
            
            template_body = {
                "index_patterns": [pattern],
                "template": {
                    "settings": config["settings"],
                    "mappings": config["mappings"]
                },
                "priority": 1,
                "version": 1,
                "_meta": {
                    "description": f"Template for {index_type} indexes",
                    "created_by": "IA-Influencer-Agent",
                    "environment": self.environment.value
                }
            }
            
            client.indices.put_index_template(name=template_name, body=template_body)
            self.logger.info(f"Created Elasticsearch template: {template_name} for pattern {pattern}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to create index template {template_name}: {str(e)}")
            raise

    def bulk_index_documents(self, client: Elasticsearch, index_name: str, 
                           documents: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Bulk index documents
        
        Args:
            client: Elasticsearch client
            index_name: Target index name
            documents: List of documents to index
            
        Returns:
            Bulk operation results
        """
        try:
            actions = []
            for doc in documents:
                action = {
                    "_index": index_name,
                    "_source": doc
                }
                
                # Use document ID if provided
                if "_id" in doc:
                    action["_id"] = doc.pop("_id")
                
                actions.append({"index": action})
            
            # Perform bulk operation
            response = client.bulk(
                body=actions,
                timeout=self.performance_config.bulk_timeout,
                refresh=self.performance_config.refresh_policy
            )
            
            # Check for errors
            errors = []
            if response.get("errors", False):
                for item in response["items"]:
                    if "index" in item and "error" in item["index"]:
                        errors.append(item["index"]["error"])
            
            result = {
                "total": len(documents),
                "successful": len(documents) - len(errors),
                "errors": errors,
                "took": response.get("took", 0)
            }
            
            self.logger.info(f"Bulk indexed {result['successful']}/{result['total']} documents to {index_name}")
            
            if errors:
                self.logger.warning(f"Bulk indexing had {len(errors)} errors")
            
            return result
            
        except Exception as e:
            self.logger.error(f"Failed to bulk index documents: {str(e)}")
            raise

    def search_documents(self, client: Elasticsearch, index_name: str, 
                        query: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        """
        Search documents in index
        
        Args:
            client: Elasticsearch client
            index_name: Index to search
            query: Elasticsearch query DSL
            **kwargs: Additional search parameters
            
        Returns:
            Search results
        """
        try:
            search_params = {
                "index": index_name,
                "body": {"query": query},
                "timeout": self.performance_config.search_timeout,
                **kwargs
            }
            
            response = client.search(**search_params)
            
            self.logger.debug(f"Search completed: {response['hits']['total']['value']} results")
            
            return response
            
        except Exception as e:
            self.logger.error(f"Search failed on {index_name}: {str(e)}")
            raise

    def health_check(self) -> Dict[str, Any]:
        """
        Perform comprehensive health check on Elasticsearch
        
        Returns:
            Health check results dictionary
        """
        health_status = {
            "status": "healthy",
            "environment": self.environment.value,
            "workload_type": self.workload_type.value,
            "cluster_type": self.cluster_type.value,
            "clients": {},
            "cluster_health": {},
            "timestamp": None
        }
        
        import datetime
        health_status["timestamp"] = datetime.datetime.utcnow().isoformat()
        
        try:
            # Test main client
            main_client = self.create_client()
            
            # Get cluster health
            cluster_health = main_client.cluster.health()
            health_status["cluster_health"] = {
                "status": cluster_health["status"],
                "cluster_name": cluster_health["cluster_name"],
                "number_of_nodes": cluster_health["number_of_nodes"],
                "number_of_data_nodes": cluster_health["number_of_data_nodes"],
                "active_primary_shards": cluster_health["active_primary_shards"],
                "active_shards": cluster_health["active_shards"],
                "relocating_shards": cluster_health["relocating_shards"],
                "initializing_shards": cluster_health["initializing_shards"],
                "unassigned_shards": cluster_health["unassigned_shards"],
                "delayed_unassigned_shards": cluster_health["delayed_unassigned_shards"],
                "number_of_pending_tasks": cluster_health["number_of_pending_tasks"],
                "number_of_in_flight_fetch": cluster_health["number_of_in_flight_fetch"],
                "task_max_waiting_in_queue_millis": cluster_health["task_max_waiting_in_queue_millis"],
                "active_shards_percent_as_number": cluster_health["active_shards_percent_as_number"]
            }
            
            # Get cluster stats
            cluster_stats = main_client.cluster.stats()
            health_status["cluster_stats"] = {
                "indices_count": cluster_stats["indices"]["count"],
                "docs_count": cluster_stats["indices"]["docs"]["count"],
                "store_size_bytes": cluster_stats["indices"]["store"]["size_in_bytes"],
                "nodes_count": cluster_stats["nodes"]["count"]["total"],
                "jvm_heap_used_percent": cluster_stats["nodes"]["jvm"]["mem"]["heap_used_percent"],
                "jvm_heap_max_bytes": cluster_stats["nodes"]["jvm"]["mem"]["heap_max_in_bytes"]
            }
            
            health_status["clients"]["main"] = {
                "status": "healthy",
                "cluster_status": cluster_health["status"]
            }
            
            # Overall status based on cluster health
            if cluster_health["status"] in ["yellow", "red"]:
                health_status["status"] = "degraded" if cluster_health["status"] == "yellow" else "unhealthy"
            
        except (ConnectionError, RequestError) as e:
            health_status["status"] = "unhealthy"
            health_status["clients"]["main"] = {
                "status": "unhealthy",
                "error": str(e)
            }
            self.logger.error(f"Elasticsearch health check failed: {str(e)}")
        except Exception as e:
            health_status["status"] = "unhealthy"
            health_status["error"] = str(e)
            self.logger.error(f"Elasticsearch health check error: {str(e)}")
        
        return health_status

    def close_all_connections(self) -> None:
        """Close all Elasticsearch connections and cleanup resources"""
        # Close sync clients
        for client_name, client in self._clients.items():
            try:
                client.transport.close()
                self.logger.info(f"Closed Elasticsearch client: {client_name}")
            except Exception as e:
                self.logger.error(f"Error closing client {client_name}: {str(e)}")
        
        # Close async clients
        for client_name, client in self._async_clients.items():
            try:
                client.close()
                self.logger.info(f"Closed Elasticsearch async client: {client_name}")
            except Exception as e:
                self.logger.error(f"Error closing async client {client_name}: {str(e)}")
        
        self._clients.clear()
        self._async_clients.clear()

    def __del__(self):
        """Cleanup on object destruction"""
        self.close_all_connections()
